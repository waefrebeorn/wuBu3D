/* shade.c — per-pixel shaded triangle rasteriser.

Why this exists: every frame produced so far fills each quad with ONE colour. A slab of skin has no
falloff, no contact darkening, no rim — so the figure reads as vector clipart no matter how many
colours the palette has. Lighting has to be evaluated per pixel, and per the project rule that work
belongs in C, not in a Python loop.

Pipeline per horizontal span of a triangle:
    perspective-correct 1/z interpolation -> world position and normal
    N point lights with inverse-square falloff -> lambert term
    fresnel rim against the eye -> edge light
    z-test -> colour

Build:  gcc -O2 -march=native -shared -fPIC -o libshade.so shade.c
*/

#include <math.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    float sx, sy, sz;      /* screen x, y and view depth */
    float wx, wy, wz;      /* world position               */
    float nx, ny, nz;      /* world normal                 */
    float u, v;            /* texture coord (unused in v1) */
} Vert;

#define VSTRIDE 11

static inline float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

/* one triangle: 3 verts, base colour, and the light set */
int shade_tri(uint8_t *rgb, float *zb, int W, int H,
              const float *v, const float *base,
              const float *lights, int nlights,
              float ambient, float gain, float rimk,
              const float *eye)
{
    const Vert *a = (const Vert *)(v + 0 * VSTRIDE);
    const Vert *b = (const Vert *)(v + 1 * VSTRIDE);
    const Vert *c = (const Vert *)(v + 2 * VSTRIDE);

    float minx = fminf(a->sx, fminf(b->sx, c->sx));
    float maxx = fmaxf(a->sx, fmaxf(b->sx, c->sx));
    float miny = fminf(a->sy, fminf(b->sy, c->sy));
    float maxy = fmaxf(a->sy, fmaxf(b->sy, c->sy));
    int x0 = (int)floorf(minx), x1 = (int)ceilf(maxx);
    int y0 = (int)floorf(miny), y1 = (int)ceilf(maxy);
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > W - 1) x1 = W - 1;
    if (y1 > H - 1) y1 = H - 1;
    if (x0 > x1 || y0 > y1) return 0;

    float area = (b->sx - a->sx) * (c->sy - a->sy) - (c->sx - a->sx) * (b->sy - a->sy);
    if (fabsf(area) < 1e-9f) return 0;
    float inv_area = 1.0f / area;

    /* reciprocal depth for perspective-correct interpolation */
    float iza = 1.0f / fmaxf(a->sz, 1e-4f);
    float izb = 1.0f / fmaxf(b->sz, 1e-4f);
    float izc = 1.0f / fmaxf(c->sz, 1e-4f);

    int drawn = 0;
    for (int py = y0; py <= y1; ++py) {
        float cy = (float)py + 0.5f;
        for (int px = x0; px <= x1; ++px) {
            float cx = (float)px + 0.5f;
            float w0 = ((b->sx - cx) * (c->sy - cy) - (c->sx - cx) * (b->sy - cy)) * inv_area;
            float w1 = ((c->sx - cx) * (a->sy - cy) - (a->sx - cx) * (c->sy - cy)) * inv_area;
            float w2 = 1.0f - w0 - w1;
            if (w0 < -0.0005f || w1 < -0.0005f || w2 < -0.0005f) continue;

            float iz = w0 * iza + w1 * izb + w2 * izc;
            if (iz <= 1e-9f) continue;
            float z = 1.0f / iz;
            if (z >= zb[py * W + px]) continue;

            float pw = w0 * iza, qw = w1 * izb, rw = w2 * izc;
            float sumw = pw + qw + rw;
            pw /= sumw; qw /= sumw; rw /= sumw;

            float wx_ = pw * a->wx + qw * b->wx + rw * c->wx;
            float wy_ = pw * a->wy + qw * b->wy + rw * c->wy;
            float wz_ = pw * a->wz + qw * b->wz + rw * c->wz;
            float nx = pw * a->nx + qw * b->nx + rw * c->nx;
            float ny = pw * a->ny + qw * b->ny + rw * c->ny;
            float nz = pw * a->nz + qw * b->nz + rw * c->nz;
            float nl = sqrtf(nx * nx + ny * ny + nz * nz);
            if (nl > 1e-6f) { nx /= nl; ny /= nl; nz /= nl; }

            float s = ambient;
            for (int i = 0; i < nlights; ++i) {
                const float *L = lights + i * 4;
                float dx = L[0] - wx_, dy = L[1] - wy_, dz = L[2] - wz_;
                float d2 = dx * dx + dy * dy + dz * dz;
                float d = sqrtf(d2) + 1e-5f;
                float nd = (nx * dx + ny * dy + nz * dz) / d;
                if (nd > 0.0f) {
                    float fall = 1.0f / (1.0f + (0.55f / (L[3] * L[3])) * d2);
                    s += gain * nd * fall;
                }
            }

            /* contact darkening: a surface is darker the closer it is to the ground it sits on,
               which is the cheapest stand-in for ambient occlusion and the thing that makes parts
               look assembled instead of stacked */
            s *= 0.78f + 0.22f * clampf(wy_ / 0.55f, 0.0f, 1.0f);

            float rim = 0.0f;
            if (rimk > 0.0f) {
                float ex = eye[0] - wx_, ey = eye[1] - wy_, ez = eye[2] - wz_;
                float el = sqrtf(ex * ex + ey * ey + ez * ez) + 1e-5f;
                float f = 1.0f - fabsf((nx * ex + ny * ey + nz * ez) / el);
                f = f * f * f;
                rim = rimk * f;
            }

            float r = base[0] * s + 255.0f * rim;
            float g = base[1] * s + 255.0f * rim;
            float bl = base[2] * s + 255.0f * rim;
            int o = (py * W + px) * 3;
            rgb[o + 0] = (uint8_t)clampf(r, 0.0f, 255.0f);
            rgb[o + 1] = (uint8_t)clampf(g, 0.0f, 255.0f);
            rgb[o + 2] = (uint8_t)clampf(bl, 0.0f, 255.0f);
            zb[py * W + px] = z;
            drawn++;
        }
    }
    return drawn;
}

/* flat fill, for the sky bands and ground which are already correct as flat colour */
int fill_quad(uint8_t *rgb, float *zb, int W, int H, const float *v, const float *col)
{
    return shade_tri(rgb, zb, W, H, v, col, 0, 0, 1.0f, 0.0f, 0.0f, (const float[3]){0, 0, 0});
}
