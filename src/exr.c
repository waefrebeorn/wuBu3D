/* exr.c — OpenEXR output with the passes that make it compositing data instead of a picture.

The gap list said "EXR / ProRes — the missing piece is a data pass to put in the EXR"; FILM_GAPS.md
ranked normal and depth passes above almost every feature, because a renderer that emits only a
picture forces a re-render for every grade change. This writes:

    wubu_exr         B, G, R
    wubu_exr_z       B, G, R, Z
    wubu_exr_passes  B, G, NX, NY, NZ, R, Z

Uncompressed scanline, HALF channels, which every compositor reads. Channels must be written in
alphabetical order — a chlist out of order is legal but readers that assume sorted get confused, and
the same mistake with the wrong entry size produces a file ffprobe calls EXR with width 0.

    gcc -O2 -march=native -shared -fPIC -o libexr.so exr.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { uint8_t *p; size_t n, cap; } _buf;

static void _put(_buf *b, const void *src, size_t n)
{
    if (b->n + n > b->cap) {
        while (b->cap < b->n + n) b->cap = b->cap ? b->cap * 2 : 1024;
        b->p = realloc(b->p, b->cap);
    }
    memcpy(b->p + b->n, src, n);
    b->n += n;
}
static void _put_str(_buf *b, const char *s) { _put(b, s, strlen(s) + 1); }
static void _put_i32(_buf *b, int32_t v) { _put(b, &v, 4); }

/* float -> IEEE half, round to nearest even */
static uint16_t _half(float f)
{
    uint32_t x;
    memcpy(&x, &f, 4);
    uint32_t sign = (x >> 16) & 0x8000u;
    int32_t exp = (int32_t)((x >> 23) & 0xFF) - 127 + 15;
    uint32_t mant = x & 0x7FFFFFu;
    if (((x >> 23) & 0xFF) == 0xFF) return (uint16_t)(sign | 0x7C00u | (mant ? 0x200u : 0));
    if (exp <= 0) {
        if (exp < -10) return (uint16_t)sign;
        mant |= 0x800000u;
        uint32_t shift = (uint32_t)(14 - exp);
        uint32_t m = mant >> shift;
        uint32_t rem = mant & ((1u << shift) - 1);
        uint32_t halfway = 1u << (shift - 1);
        if (rem > halfway || (rem == halfway && (m & 1u))) m++;
        return (uint16_t)(sign | m);
    }
    if (exp >= 31) return (uint16_t)(sign | 0x7C00u);
    return (uint16_t)(sign | ((uint32_t)exp << 10) | (mant >> 13));
}

/* one output channel: where its value comes from, one sample per pixel */
typedef struct { const char *name; const float *base; int off; int stride; } _ch;

static int _write(const char *path, const _ch *ch, int nch, int w, int h)
{
    if (!path || !ch || nch < 1 || w < 1 || h < 1) return -1;
    _buf hd = {0, 0, 0};

    _put_str(&hd, "channels");
    _put_str(&hd, "chlist");
    int32_t chsize_pos = (int32_t)hd.n;
    _put_i32(&hd, 0);
    size_t ch_start = hd.n;
    for (int c = 0; c < nch; ++c) {
        _put_str(&hd, ch[c].name);
        _put_i32(&hd, 1);                          /* pixelType = HALF */
        /* pLinear is ONE byte then THREE reserved bytes, not an int32. Four extra bytes here makes
           the chlist too long and ffprobe reports EXR with width 0. */
        _put(&hd, "\0\0\0\0", 4);
        _put_i32(&hd, 1);
        _put_i32(&hd, 1);
    }
    _put(&hd, "\0", 1);
    int32_t chsize = (int32_t)(hd.n - ch_start);
    memcpy(hd.p + chsize_pos, &chsize, 4);

    _put_str(&hd, "compression"); _put_str(&hd, "compression"); _put_i32(&hd, 1);
    _put(&hd, "\0", 1);                            /* NO_COMPRESSION */

    int32_t zero = 0, xm = w - 1, ym = h - 1;
    _put_str(&hd, "dataWindow"); _put_str(&hd, "box2i"); _put_i32(&hd, 16);
    _put(&hd, &zero, 4); _put(&hd, &zero, 4); _put(&hd, &xm, 4); _put(&hd, &ym, 4);
    _put_str(&hd, "displayWindow"); _put_str(&hd, "box2i"); _put_i32(&hd, 16);
    _put(&hd, &zero, 4); _put(&hd, &zero, 4); _put(&hd, &xm, 4); _put(&hd, &ym, 4);
    _put_str(&hd, "lineOrder"); _put_str(&hd, "lineOrder"); _put_i32(&hd, 1);
    _put(&hd, "\0", 1);
    _put_str(&hd, "pixelAspectRatio"); _put_str(&hd, "float"); _put_i32(&hd, 4);
    float par = 1.0f; _put(&hd, &par, 4);
    _put_str(&hd, "screenWindowCenter"); _put_str(&hd, "v2f"); _put_i32(&hd, 8);
    float swc[2] = {0.0f, 0.0f}; _put(&hd, swc, 8);
    _put_str(&hd, "screenWindowWidth"); _put_str(&hd, "float"); _put_i32(&hd, 4);
    float sww = 1.0f; _put(&hd, &sww, 4);
    _put(&hd, "\0", 1);

    size_t header_end = 8 + hd.n;
    size_t line_bytes = 4 + 4 + (size_t)w * nch * 2;
    size_t first = header_end + (size_t)h * 8;

    FILE *f = fopen(path, "wb");
    if (!f) { free(hd.p); return -2; }
    uint8_t magic[8] = {0x76, 0x2F, 0x31, 0x01, 0x02, 0x00, 0x00, 0x00};
    fwrite(magic, 1, 8, f);
    fwrite(hd.p, 1, hd.n, f);
    for (int y = 0; y < h; ++y) {
        int64_t off = (int64_t)(first + (size_t)y * line_bytes);
        fwrite(&off, 8, 1, f);
    }

    uint8_t *row = malloc((size_t)w * nch * 2);
    if (!row) { fclose(f); free(hd.p); return -3; }
    for (int y = 0; y < h; ++y) {
        int32_t yy = y, sz = w * nch * 2;
        fwrite(&yy, 4, 1, f);
        fwrite(&sz, 4, 1, f);
        for (int c = 0; c < nch; ++c) {
            const float *base = ch[c].base;
            int off = ch[c].off, stride = ch[c].stride;
            for (int x = 0; x < w; ++x) {
                uint16_t hv = _half(base[((size_t)y * w + x) * stride + off]);
                row[((size_t)c * w + x) * 2 + 0] = (uint8_t)(hv & 0xFF);
                row[((size_t)c * w + x) * 2 + 1] = (uint8_t)(hv >> 8);
            }
        }
        fwrite(row, 1, (size_t)sz, f);
    }
    free(row);
    fclose(f);
    free(hd.p);
    return 0;
}

static void _rgb_ch(_ch *dst, const float *rgb)
{
    dst[0] = (_ch){"B", rgb, 2, 3};
    dst[1] = (_ch){"G", rgb, 1, 3};
    dst[2] = (_ch){"R", rgb, 0, 3};
}

int wubu_exr(const char *path, const float *rgb, int w, int h)
{
    _ch c[3];
    _rgb_ch(c, rgb);
    return _write(path, c, 3, w, h);
}

/* beauty + depth: a comp can defocus, fog or grade by this plane without a re-render */
int wubu_exr_z(const char *path, const float *rgb, const float *z, int w, int h)
{
    if (!z) return wubu_exr(path, rgb, w, h);
    _ch c[4];
    _rgb_ch(c, rgb);
    c[3] = (_ch){"Z", z, 0, 1};
    return _write(path, c, 4, w, h);
}

/* beauty + depth + normals, in alphabetical channel order: B, G, NX, NY, NZ, R, Z.
   The normal pass is what lets a compositor relight the shot instead of re-rendering it. */
int wubu_exr_passes(const char *path, const float *rgb, const float *z, const float *nrm,
                    int w, int h)
{
    if (!nrm) return wubu_exr_z(path, rgb, z, w, h);
    _ch c[7];
    c[0] = (_ch){"B", rgb, 2, 3};
    c[1] = (_ch){"G", rgb, 1, 3};
    c[2] = (_ch){"NX", nrm, 0, 3};
    c[3] = (_ch){"NY", nrm, 1, 3};
    c[4] = (_ch){"NZ", nrm, 2, 3};
    c[5] = (_ch){"R", rgb, 0, 3};
    if (z) c[6] = (_ch){"Z", z, 0, 1};
    return _write(path, c, z ? 7 : 6, w, h);
}


/* the full comp set: beauty + depth + normals + motion, alphabetical B,G,NX,NY,NZ,R,VX,VY,Z.
   Motion vectors are what let a comp do directional blur and retime without a re-render. */
int wubu_exr_comp(const char *path, const float *rgb, const float *z, const float *nrm,
                  const float *mv, int w, int h)
{
    if (!mv) return wubu_exr_passes(path, rgb, z, nrm, w, h);
    /* build the list conditionally: a missing pass must be OMITTED, not filled with another pass's
       data, or a comp reads depth out of NX and cannot tell */
    _ch c[9];
    int n = 0;
    c[n++] = (_ch){"B", rgb, 2, 3};
    c[n++] = (_ch){"G", rgb, 1, 3};
    if (nrm) {
        c[n++] = (_ch){"NX", nrm, 0, 3};
        c[n++] = (_ch){"NY", nrm, 1, 3};
        c[n++] = (_ch){"NZ", nrm, 2, 3};
    }
    c[n++] = (_ch){"R", rgb, 0, 3};
    c[n++] = (_ch){"VX", mv, 0, 2};
    c[n++] = (_ch){"VY", mv, 1, 2};
    if (z) c[n++] = (_ch){"Z", z, 0, 1};
    return _write(path, c, n, w, h);
}
