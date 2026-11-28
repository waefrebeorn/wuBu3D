/* fx.c — the post stack: linear light in, a finished frame out.

Every entry here closes a gap from docs/ENGINE_GAPS.md, where the engines have had these for years and
we were writing sRGB bytes straight to a PNG:

  wubu_tonemap   ACES-fitted curve (Narkowicz fit) with exposure and highlight rolloff.
                 Blender 5 ships ACES 1.3/2.0 views; we clipped at 255.
  wubu_bloom     threshold + separable box blur + add, the glare every renderer has
  wubu_rays      radial god-rays from a light position, the volumetric stand-in that costs nothing
  wubu_mblur     accumulate subframes, which is how a camera pan stops strobing

Frames arrive as float RGB in scene-referred 0..N; the stack ends with 0..255 bytes.

    gcc -O2 -march=native -shared -fPIC -o libfx.so fx.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Narkowicz's ACES filmic fit: cheap, and its shoulder is what keeps a highlight from clipping flat */
static inline float aces(float x)
{
    const float a = 2.51f, b = 0.03f, c = 2.43f, d = 0.59f, e = 0.14f;
    float v = (x * (a * x + b)) / (x * (c * x + d) + e);
    return v < 0.0f ? 0.0f : (v > 1.0f ? 1.0f : v);
}

void wubu_tonemap(float *rgb, int n, float exposure, int mode)
{
    for (int i = 0; i < n * 3; ++i) {
        float x = rgb[i] * exposure;
        if (mode == 0) {                       /* linear clamp: what we had */
            x = x < 0 ? 0 : (x > 1 ? 1 : x);
        } else if (mode == 1) {                /* ACES */
            x = aces(x);
        } else {                               /* reinhard */
            x = x / (1.0f + x);
        }
        rgb[i] = x;
    }
}

/* one separable box pass, radius r, on a float image; repeated 3x it is a Gaussian to within nothing
 * anyone can see at these radii */
static void box_blur(float *img, int w, int h, int r)
{
    if (r < 1) return;
    float *tmp = malloc((size_t)w * h * 3 * sizeof(float));
    if (!tmp) return;
    memcpy(tmp, img, (size_t)w * h * 3 * sizeof(float));
    int win = 2 * r + 1;
    for (int y = 0; y < h; ++y) {
        for (int c = 0; c < 3; ++c) {
            float acc = 0.0f;
            for (int i = -r; i <= r; ++i) {
                int x = i < 0 ? 0 : (i >= w ? w - 1 : i);
                acc += tmp[(y * w + x) * 3 + c];
            }
            for (int x = 0; x < w; ++x) {
                img[(y * w + x) * 3 + c] = acc / (float)win;
                int add = x + r + 1, sub = x - r;
                if (add >= w) add = w - 1;
                if (sub < 0) sub = 0;
                acc += tmp[(y * w + add) * 3 + c] - tmp[(y * w + sub) * 3 + c];
            }
        }
    }
    memcpy(tmp, img, (size_t)w * h * 3 * sizeof(float));
    for (int x = 0; x < w; ++x) {
        for (int c = 0; c < 3; ++c) {
            float acc = 0.0f;
            for (int i = -r; i <= r; ++i) {
                int y = i < 0 ? 0 : (i >= h ? h - 1 : i);
                acc += tmp[(y * w + x) * 3 + c];
            }
            for (int y = 0; y < h; ++y) {
                img[(y * w + x) * 3 + c] = acc / (float)win;
                int add = y + r + 1, sub = y - r;
                if (add >= h) add = h - 1;
                if (sub < 0) sub = 0;
                acc += tmp[((add * w) + x) * 3 + c] - tmp[((sub * w) + x) * 3 + c];
            }
        }
    }
    free(tmp);
}

void wubu_bloom(float *rgb, int w, int h, float threshold, float strength, int radius)
{
    if (strength <= 0.0f) return;
    int n = w * h * 3;
    float *hot = malloc((size_t)n * sizeof(float));
    if (!hot) return;
    for (int i = 0; i < n; ++i) {
        float v = rgb[i] - threshold;
        hot[i] = v > 0.0f ? v : 0.0f;
    }
    box_blur(hot, w, h, radius);
    box_blur(hot, w, h, radius);
    for (int i = 0; i < n; ++i) rgb[i] += hot[i] * strength;
    free(hot);
}

/* god rays: sample toward the light, accumulate, add. Cheap, and it is the difference between a
 * lantern and a bright dot. */
void wubu_rays(float *rgb, int w, int h, float lx, float ly, float threshold, float strength,
               int samples, float decay)
{
    if (strength <= 0.0f || samples < 2) return;
    int n = w * h * 3;
    float *hot = malloc((size_t)n * sizeof(float));
    if (!hot) return;
    for (int i = 0; i < n; ++i) {
        float v = rgb[i] - threshold;
        hot[i] = v > 0.0f ? v : 0.0f;
    }
    float *out = calloc((size_t)n, sizeof(float));
    if (!out) { free(hot); return; }
    int cx = (int)(lx * (w - 1)), cy = (int)(ly * (h - 1));
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float dx = (float)(cx - x) / (float)w, dy = (float)(cy - y) / (float)h;
            float ex = (float)x, ey = (float)y, acc = 0.0f, k = 1.0f;
            for (int s = 0; s < samples; ++s) {
                int sx = (int)ex, sy = (int)ey;
                if (sx >= 0 && sx < w && sy >= 0 && sy < h) {
                    acc += hot[(sy * w + sx) * 3] * k;
                    acc += hot[(sy * w + sx) * 3 + 1] * k;
                    acc += hot[(sy * w + sx) * 3 + 2] * k;
                }
                ex += dx; ey += dy;
                k *= decay;
            }
            acc /= (float)samples * 3.0f;
            for (int c = 0; c < 3; ++c) out[(y * w + x) * 3 + c] = acc * strength;
        }
    }
    for (int i = 0; i < n; ++i) rgb[i] += out[i];
    free(hot);
    free(out);
}

/* motion blur by accumulation: the caller renders N subframes with the camera moved along its path
 * and hands each here. This is how offline renderers do it, and it is the only honest way without a
 * velocity buffer. */
void wubu_mblur_acc(float *acc, const float *frame, int n, int index, int total)
{
    float wgt = 1.0f / (float)total;
    if (index == 0) {
        for (int i = 0; i < n; ++i) acc[i] = frame[i] * wgt;
    } else {
        for (int i = 0; i < n; ++i) acc[i] += frame[i] * wgt;
    }
}

/* bytes out, with the sRGB transfer applied at the very end of the chain */
void wubu_to_bytes(const float *rgb, uint8_t *out, int n)
{
    for (int i = 0; i < n; ++i) {
        float v = rgb[i];
        v = v < 0.0f ? 0.0f : (v > 1.0f ? 1.0f : v);
        v = v <= 0.0031308f ? 12.92f * v : 1.055f * powf(v, 1.0f / 2.4f) - 0.055f;
        out[i] = (uint8_t)(v * 255.0f + 0.5f);
    }
}

/* linearise an existing 8-bit image, for frames that came from the rasteriser */
void wubu_to_linear(const uint8_t *in, float *out, int n, float gain)
{
    for (int i = 0; i < n; ++i) {
        float v = in[i] / 255.0f;
        v = v <= 0.04045f ? v / 12.92f : powf((v + 0.055f) / 1.055f, 2.4f);
        out[i] = v * gain;
    }
}


/* lens pass: vignette, chromatic aberration, grain. The three things every comp adds in the last ten
 * minutes and every renderer forgets — a frame with no vignette reads as a diagram, and grain is what
 * keeps a gradient from banding after 8-bit encode. */
void wubu_lens(float *rgb, int w, int h, float vignette, float ca, float grain, int seed)
{
    int n = w * h;
    float cx = (float)w * 0.5f, cy = (float)h * 0.5f;
    float norm = 1.0f / sqrtf(cx * cx + cy * cy);
    float *src = malloc((size_t)n * 3 * sizeof(float));
    if (!src) return;
    memcpy(src, rgb, (size_t)n * 3 * sizeof(float));

    unsigned s = (unsigned)(seed ? seed : 99);
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float dx = ((float)x + 0.5f - cx), dy = ((float)y + 0.5f - cy);
            float r = sqrtf(dx * dx + dy * dy) * norm;          /* 0 centre, 1 corner */

            /* chromatic aberration: red and blue sample slightly outward, green stays put. At 1-2
               pixels on a 1080 frame it is invisible on purpose and impossible to fake in post */
            float k = ca * r * r * 12.0f;
            int sxr = (int)(x + dx * k), syr = (int)(y + dy * k);
            int sxb = (int)(x - dx * k), syb = (int)(y - dy * k);
            if (sxr < 0 || sxr >= w || syr < 0 || syr >= h) { sxr = x; syr = y; }
            if (sxb < 0 || sxb >= w || syb < 0 || syb >= h) { sxb = x; syb = y; }
            int o = (y * w + x) * 3;
            float R = src[(syr * w + sxr) * 3 + 0];
            float G = src[o + 1];
            float B = src[(syb * w + sxb) * 3 + 2];

            float v = 1.0f - vignette * r * r;
            if (v < 0.0f) v = 0.0f;

            s = s * 1664525u + 1013904223u;
            float g = (((float)((s >> 8) & 0xFFFF) / 65535.0f) - 0.5f) * grain;

            rgb[o + 0] = R * v + g;
            rgb[o + 1] = G * v + g;
            rgb[o + 2] = B * v + g;
        }
    }
    free(src);
}
