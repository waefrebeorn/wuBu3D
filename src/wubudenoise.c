// wubudenoise — à-trous edge-aware denoiser for rendered frames.
#define _POSIX_C_SOURCE 199309L
// C11, libc only, streams P6 PPM on stdin -> P6 PPM on stdout.
//
// Why it exists: OIDN inside Blender costs ~9 s/frame at 480p on this CPU.
// An à-trous bilateral filter over YCbCr costs tens of milliseconds a frame
// and removes render noise without smearing edges, if the edge-stop is tuned.
//
// Build:  cc -O3 -march=native -std=c11 -o wubudenoise wubudenoise.c -lm
// Use:    ffmpeg -i frames/%04d.png -f image2pipe -pix_fmt rgb24 -vcodec ppm - \
//          | ./wubudenoise --sigma 10 --scales 3 --temporal 1
//          | ffmpeg -f image2pipe -pix_fmt rgb24 -vcodec ppm -i - ...
//
// Flags:
//   --sigma N     edge-stop strength on luma (default 10; 4-20 sensible)
//   --scales N    à-trous iterations (default 3; radius doubles each time)
//   --chroma X    multiplier on sigma for chroma planes (default 1.8)
//   --keep X      blend back toward the source, 0..1 (default 0.15)
//   --temporal    blend 50 % with the previous frame where pixels are static
//   --stats       print per-frame timing to stderr

#include <ctype.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const float K5[5] = {1.0f / 16, 4.0f / 16, 6.0f / 16, 4.0f / 16, 1.0f / 16};

typedef struct { int w, h; uint8_t *rgb; } Frame;
typedef struct { int w, h; float *p; } Plane;

static int read_token(FILE *f, char *buf, size_t n) {
    int c, i = 0;
    // skip whitespace and comments
    for (;;) {
        c = fgetc(f);
        if (c == '#') { while (c != '\n' && c != EOF) c = fgetc(f); }
        else if (!isspace(c)) break;
        if (c == EOF) return 0;
    }
    while (c != EOF && !isspace(c)) {
        if ((size_t)i + 1 < n) buf[i++] = (char)c;
        c = fgetc(f);
    }
    buf[i] = 0;
    return i > 0;
}

static int read_ppm(FILE *f, Frame *fr) {
    char tok[64];
    if (!read_token(f, tok, sizeof tok) || strcmp(tok, "P6")) return 0;
    if (!read_token(f, tok, sizeof tok)) return 0;
    fr->w = atoi(tok);
    if (!read_token(f, tok, sizeof tok)) return 0;
    fr->h = atoi(tok);
    if (!read_token(f, tok, sizeof tok)) return 0;
    if (atoi(tok) > 255) return 0;                 // 8-bit only
    size_t n = (size_t)fr->w * fr->h * 3;
    fr->rgb = malloc(n);
    if (!fr->rgb) return 0;
    return fread(fr->rgb, 1, n, f) == n;
}

static void write_ppm(FILE *f, const Frame *fr) {
    fprintf(f, "P6\n%d %d\n255\n", fr->w, fr->h);
    fwrite(fr->rgb, 1, (size_t)fr->w * fr->h * 3, f);
}

static Plane plane_new(int w, int h) { Plane p = {w, h, calloc((size_t)w * h, sizeof(float))}; return p; }

static void rgb_to_ycc(const Frame *fr, Plane *Y, Plane *Cb, Plane *Cr) {
    const int n = fr->w * fr->h;
    for (int i = 0; i < n; i++) {
        const float r = fr->rgb[i * 3 + 0] / 255.0f;
        const float g = fr->rgb[i * 3 + 1] / 255.0f;
        const float b = fr->rgb[i * 3 + 2] / 255.0f;
        Y->p[i]  = 0.2126f * r + 0.7152f * g + 0.0722f * b;
        Cb->p[i] = (b - Y->p[i]) / 1.8556f;
        Cr->p[i] = (r - Y->p[i]) / 1.5748f;
    }
}

static void ycc_to_rgb(const Plane *Y, const Plane *Cb, const Plane *Cr, Frame *fr) {
    const int n = fr->w * fr->h;
    for (int i = 0; i < n; i++) {
        const float y = Y->p[i];
        float r = y + 1.5748f * Cr->p[i];
        float b = y + 1.8556f * Cb->p[i];
        float g = (y - 0.2126f * r - 0.0722f * b) / 0.7152f;
        r = fminf(fmaxf(r, 0.0f), 1.0f);
        g = fminf(fmaxf(g, 0.0f), 1.0f);
        b = fminf(fmaxf(b, 0.0f), 1.0f);
        fr->rgb[i * 3 + 0] = (uint8_t)(r * 255.0f + 0.5f);
        fr->rgb[i * 3 + 1] = (uint8_t)(g * 255.0f + 0.5f);
        fr->rgb[i * 3 + 2] = (uint8_t)(b * 255.0f + 0.5f);
    }
}

// Separable à-trous step: 5-tap B3 spline horizontally, then vertically.
// Separable costs 10 taps/pixel instead of 25 and reads sequentially, which is
// what makes this fast enough to sit in a pipe on four cores.
static void atrous_h(const Plane *src, Plane *dst, const float *stop, int step) {
    const int w = src->w, h = src->h;
    for (int y = 0; y < h; y++) {
        const float *row = src->p + (size_t)y * w;
        float *out = dst->p + (size_t)y * w;
        for (int x = 0; x < w; x++) {
            const float c = row[x];
            float sum = 0.0f, wsum = 0.0f;
            for (int k = -2; k <= 2; k++) {
                int sx = x + k * step;
                if (sx < 0) sx = 0; else if (sx >= w) sx = w - 1;
                const int idx = (int)(fabsf(row[sx] - c) * 255.0f);
                const float wgt = K5[k + 2] * stop[idx < 255 ? idx : 255];
                sum += wgt * row[sx];
                wsum += wgt;
            }
            out[x] = sum / (wsum + 1e-8f);
        }
    }
}

static void atrous_v(const Plane *src, Plane *dst, const float *stop, int step) {
    const int w = src->w, h = src->h;
    for (int y = 0; y < h; y++) {
        float *out = dst->p + (size_t)y * w;
        for (int x = 0; x < w; x++) {
            const float c = src->p[(size_t)y * w + x];
            float sum = 0.0f, wsum = 0.0f;
            for (int k = -2; k <= 2; k++) {
                int sy = y + k * step;
                if (sy < 0) sy = 0; else if (sy >= h) sy = h - 1;
                const float q = src->p[(size_t)sy * w + x];
                const int idx = (int)(fabsf(q - c) * 255.0f);
                const float wgt = K5[k + 2] * stop[idx < 255 ? idx : 255];
                sum += wgt * q;
                wsum += wgt;
            }
            out[x] = sum / (wsum + 1e-8f);
        }
    }
}

static void build_stop(float *stop, float sigma) {
    const float s2 = 2.0f * sigma * sigma;
    for (int i = 0; i < 256; i++) stop[i] = expf(-(float)(i * i) / s2);
}

static void denoise_plane(Plane *plane, float sigma, int scales, float keep) {
    float stop[256];
    build_stop(stop, sigma);
    Plane a = plane_new(plane->w, plane->h);
    Plane b = plane_new(plane->w, plane->h);
    memcpy(a.p, plane->p, (size_t)plane->w * plane->h * sizeof(float));
    for (int s = 0; s < scales; s++) {
        atrous_h(&a, &b, stop, 1 << s);
        atrous_v(&b, &a, stop, 1 << s);
    }
    const int n = plane->w * plane->h;
    for (int i = 0; i < n; i++) plane->p[i] = keep * plane->p[i] + (1.0f - keep) * a.p[i];
    free(a.p); free(b.p);
}

static void temporal_blend(Plane *cur, const Plane *prev, float thr) {
    const int n = cur->w * cur->h;
    for (int i = 0; i < n; i++) {
        const float d = fabsf(cur->p[i] - prev->p[i]);
        if (d < thr) cur->p[i] = 0.5f * cur->p[i] + 0.5f * prev->p[i];
    }
}

int main(int argc, char **argv) {
    float sigma = 10.0f, chroma_mult = 1.8f, keep = 0.15f, temporal_thr = 6.0f / 255.0f;
    int scales = 3, temporal = 0, stats = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--sigma") && i + 1 < argc) sigma = (float)atof(argv[++i]);
        else if (!strcmp(argv[i], "--scales") && i + 1 < argc) scales = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--chroma") && i + 1 < argc) chroma_mult = (float)atof(argv[++i]);
        else if (!strcmp(argv[i], "--keep") && i + 1 < argc) keep = (float)atof(argv[++i]);
        else if (!strcmp(argv[i], "--temporal")) temporal = 1;
        else if (!strcmp(argv[i], "--stats")) stats = 1;
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 2; }
    }

    Frame fr = {0};
    Plane Y = {0}, Cb = {0}, Cr = {0};
    Plane Yprev = {0}, Cbprev = {0}, Crprev = {0};
    int have_prev = 0, frame_no = 0;
    double total_ms = 0.0;

    while (read_ppm(stdin, &fr)) {
        if (!Y.p) {
            Y = plane_new(fr.w, fr.h); Cb = plane_new(fr.w, fr.h); Cr = plane_new(fr.w, fr.h);
            Yprev = plane_new(fr.w, fr.h); Cbprev = plane_new(fr.w, fr.h); Crprev = plane_new(fr.w, fr.h);
        }
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);

        rgb_to_ycc(&fr, &Y, &Cb, &Cr);
        if (temporal && have_prev) {
            temporal_blend(&Y, &Yprev, temporal_thr);
            temporal_blend(&Cb, &Cbprev, temporal_thr);
            temporal_blend(&Cr, &Crprev, temporal_thr);
        }
        denoise_plane(&Y, sigma, scales, keep);
        denoise_plane(&Cb, sigma * chroma_mult, scales > 1 ? scales - 1 : 1, keep);
        denoise_plane(&Cr, sigma * chroma_mult, scales > 1 ? scales - 1 : 1, keep);
        ycc_to_rgb(&Y, &Cb, &Cr, &fr);

        if (temporal) {
            memcpy(Yprev.p, Y.p, (size_t)fr.w * fr.h * sizeof(float));
            memcpy(Cbprev.p, Cb.p, (size_t)fr.w * fr.h * sizeof(float));
            memcpy(Crprev.p, Cr.p, (size_t)fr.w * fr.h * sizeof(float));
            have_prev = 1;
        }

        clock_gettime(CLOCK_MONOTONIC, &t1);
        double ms = (t1.tv_sec - t0.tv_sec) * 1e3 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
        total_ms += ms;
        frame_no++;
        if (stats) fprintf(stderr, "frame %d  %.1f ms  (%.1f Mpix/s)\n", frame_no, ms,
                           (fr.w * (double)fr.h) / (ms * 1000.0));
        write_ppm(stdout, &fr);
        free(fr.rgb); fr.rgb = NULL;
    }

    if (stats && frame_no) {
        const double mpx = ((double)fr.w * fr.h) / 1e6;
        fprintf(stderr, "total %d frames, mean %.1f ms/frame, %.1f Mpix/s\n",
                frame_no, total_ms / frame_no, mpx / (total_ms / frame_no / 1000.0));
    }
    return frame_no ? 0 : 1;
}
