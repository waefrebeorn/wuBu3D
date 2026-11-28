/* exr.c — write a frame as OpenEXR, because a video pipeline that only emits 8-bit PNG has already
 * thrown away everything the tonemap did.

Gap inventory said "EXR / ProRes — the missing piece is a data pass to put in the EXR". The pass is
the easy half; the container is this file. Uncompressed scanline EXR, HALF channels, which every
compositor reads (Nuke, Fusion, Blender, ffmpeg, OpenImageIO).

Layout, in the order it goes on disk:
    magic (0x76 0x2F 0x31 0x01) + version (2)
    header: attributes, each name\0 type\0 int32 size, payload; ends with a single \0
    offset table: int64 per scanline, absolute file offsets
    scanlines: int32 y, int32 size, then the channel planes for that scanline

Channel order in the file must be alphabetical (B, G, R) — EXR sort order is by name, and a file with
R,G,B is legal but readers that assume sorted chlist get confused.

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
static void _put_i64(_buf *b, int64_t v) { _put(b, &v, 8); }

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

int wubu_exr(const char *path, const float *rgb, int w, int h)
{
    if (!path || !rgb || w < 1 || h < 1) return -1;
    _buf hd = {0, 0, 0};

    _put_str(&hd, "channels");
    _put_str(&hd, "chlist");
    int32_t chsize_pos = (int32_t)hd.n;
    _put_i32(&hd, 0);
    size_t ch_start = hd.n;
    const char *names[3] = {"B", "G", "R"};       /* alphabetical, as EXR requires */
    int order[3] = {2, 1, 0};
    for (int c = 0; c < 3; ++c) {
        _put_str(&hd, names[c]);
        _put_i32(&hd, 1);                          /* pixelType = HALF */
        /* pLinear is ONE byte plus THREE reserved bytes, not an int32. With 4 extra bytes here the
           chlist is 15 bytes too long, ffprobe parses it as EXR with width 0, and ffmpeg reports
           "Not yet implemented" — which is about the malformed header, not about half floats. */
        _put(&hd, "\0\0\0\0", 4);
        _put_i32(&hd, 1);                          /* xSampling */
        _put_i32(&hd, 1);                          /* ySampling */
    }
    _put(&hd, "\0", 1);                            /* end of chlist */
    int32_t chsize = (int32_t)(hd.n - ch_start);
    memcpy(hd.p + chsize_pos, &chsize, 4);

    _put_str(&hd, "compression"); _put_str(&hd, "compression"); _put_i32(&hd, 1);
    _put(&hd, "\0", 1);                            /* NO_COMPRESSION */

    _put_str(&hd, "dataWindow"); _put_str(&hd, "box2i"); _put_i32(&hd, 16);
    int32_t z = 0, x0 = 0, y0 = 0, xm = w - 1, ym = h - 1;
    _put(&hd, &z, 4); _put(&hd, &z, 4); _put(&hd, &xm, 4); _put(&hd, &ym, 4);

    _put_str(&hd, "displayWindow"); _put_str(&hd, "box2i"); _put_i32(&hd, 16);
    _put(&hd, &z, 4); _put(&hd, &z, 4); _put(&hd, &xm, 4); _put(&hd, &ym, 4);

    _put_str(&hd, "lineOrder"); _put_str(&hd, "lineOrder"); _put_i32(&hd, 1);
    _put(&hd, "\0", 1);                            /* INCREASING_Y */

    _put_str(&hd, "pixelAspectRatio"); _put_str(&hd, "float"); _put_i32(&hd, 4);
    float par = 1.0f; _put(&hd, &par, 4);

    _put_str(&hd, "screenWindowCenter"); _put_str(&hd, "v2f"); _put_i32(&hd, 8);
    float swc[2] = {0.0f, 0.0f}; _put(&hd, swc, 8);

    _put_str(&hd, "screenWindowWidth"); _put_str(&hd, "float"); _put_i32(&hd, 4);
    float sww = 1.0f; _put(&hd, &sww, 4);

    _put(&hd, "\0", 1);                            /* end of header */

    size_t header_end = 8 + hd.n;                  /* magic + version come first */
    size_t line_bytes = 4 + 4 + (size_t)w * 3 * 2;  /* y, size, planes */
    size_t off_table = header_end;
    size_t first = off_table + (size_t)h * 8;

    FILE *f = fopen(path, "wb");
    if (!f) { free(hd.p); return -2; }
    uint8_t magic[8] = {0x76, 0x2F, 0x31, 0x01, 0x02, 0x00, 0x00, 0x00};
    fwrite(magic, 1, 8, f);
    fwrite(hd.p, 1, hd.n, f);

    for (int y = 0; y < h; ++y) {
        int64_t off = (int64_t)(first + (size_t)y * line_bytes);
        fwrite(&off, 8, 1, f);
    }

    uint8_t *row = malloc((size_t)w * 3 * 2);
    for (int y = 0; y < h; ++y) {
        int32_t yy = y, sz = w * 3 * 2;
        fwrite(&yy, 4, 1, f);
        fwrite(&sz, 4, 1, f);
        for (int c = 0; c < 3; ++c) {
            int src = order[c];
            for (int x = 0; x < w; ++x) {
                uint16_t hv = _half(rgb[((size_t)y * w + x) * 3 + src]);
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
