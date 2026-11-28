/* oit.c — weighted blended order-independent transparency (McGuire & Bavoil).

Alpha blending is correct only back-to-front. Every engine that sorts transparent objects gets it
wrong the moment two panes cross, share a centre, or live in one mesh — the artefact is a pane pasted
on top of another, or colours that pop as the camera moves.

Two order-independent targets instead:

    accum (RGBA)  += colour * a * w,  a * w
    reveal (R)    *= 1 - a

Resolve once per frame:

    avg = accum.rgb / max(accum.a, 1e-4)
    out = avg * (1 - reveal) + background * reveal

The weight biases near, opaque fragments so a front pane still reads stronger:

    w = clamp(0.03 / (1e-5 + pow(z / scale, 4)), 1e-2, 3e3)

`scale` is a scene unit, not a constant: 200 is metres for a game world and 2 is metres for a room,
and picking the wrong one flattens every layer into the same weight.
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    float sx, sy, sz;
    float wx, wy, wz;
    float nx, ny, nz;
    float u, v;
} Vert;

#define VSTRIDE 11

void wubu_oit_clear(float *acc, float *rev, int n)
{
    for (int i = 0; i < n; ++i) {
        acc[i * 4 + 0] = acc[i * 4 + 1] = acc[i * 4 + 2] = acc[i * 4 + 3] = 0.0f;
    }
    for (int i = 0; i < n; ++i) rev[i] = 1.0f;
}

static inline float _wgt(float z, float scale)
{
    float t = z / (scale > 0.01f ? scale : 0.01f);
    float w = 0.03f / (1e-5f + t * t * t * t);
    return w < 1e-2f ? 1e-2f : (w > 3e3f ? 3e3f : w);
}

int wubu_oit_batch(float *acc, float *rev, int W, int H, const float *verts, int ntri,
                   const float *rgba, float scale)
{
    if (!acc || !rev || !verts || !rgba || W < 1 || H < 1) return -1;
    int touched = 0;
    for (int t = 0; t < ntri; ++t) {
        const Vert *a = (const Vert *)(verts + (size_t)t * 3 * VSTRIDE);
        const Vert *b = a + 1, *c = a + 2;
        const float *col = rgba + (size_t)t * 4;
        float al = col[3];
        if (al <= 0.0f) continue;
        if (al > 1.0f) al = 1.0f;

        float area = (b->sx - a->sx) * (c->sy - a->sy) - (c->sx - a->sx) * (b->sy - a->sy);
        if (fabsf(area) < 1e-9f) continue;
        float inv = 1.0f / area;

        int x0 = (int)floorf(fminf(a->sx, fminf(b->sx, c->sx)));
        int x1 = (int)ceilf(fmaxf(a->sx, fmaxf(b->sx, c->sx)));
        int y0 = (int)floorf(fminf(a->sy, fminf(b->sy, c->sy)));
        int y1 = (int)ceilf(fmaxf(a->sy, fmaxf(b->sy, c->sy)));
        if (x0 < 0) x0 = 0;
        if (y0 < 0) y0 = 0;
        if (x1 > W - 1) x1 = W - 1;
        if (y1 > H - 1) y1 = H - 1;

        for (int y = y0; y <= y1; ++y) {
            for (int x = x0; x <= x1; ++x) {
                float px = (float)x + 0.5f, py = (float)y + 0.5f;
                float w0 = ((b->sx - px) * (c->sy - py) - (c->sx - px) * (b->sy - py)) * inv;
                float w1 = ((c->sx - px) * (a->sy - py) - (a->sx - px) * (c->sy - py)) * inv;
                float w2 = 1.0f - w0 - w1;
                if (w0 < 0.0f || w1 < 0.0f || w2 < 0.0f) continue;
                float z = w0 * a->sz + w1 * b->sz + w2 * c->sz;
                if (z <= 0.02f) continue;
                int i = y * W + x;
                float wg = _wgt(z, scale) * al;
                float *ac = acc + (size_t)i * 4;
                ac[0] += col[0] * wg;
                ac[1] += col[1] * wg;
                ac[2] += col[2] * wg;
                ac[3] += wg;
                rev[i] *= (1.0f - al);
                touched++;
            }
        }
    }
    return touched;
}

int wubu_oit_resolve(uint8_t *out, const float *acc, const float *rev, int n, const float bg[3])
{
    if (!out || !acc || !rev) return -1;
    for (int i = 0; i < n; ++i) {
        const float *ac = acc + (size_t)i * 4;
        float A = ac[3];
        float r = rev[i];
        if (r < 0.0f) r = 0.0f;
        if (r > 1.0f) r = 1.0f;
        float c[3];
        if (A > 1e-4f) {
            c[0] = ac[0] / A; c[1] = ac[1] / A; c[2] = ac[2] / A;
            for (int k = 0; k < 3; ++k) c[k] = c[k] * (1.0f - r) + bg[k] * r;
        } else {
            c[0] = bg[0]; c[1] = bg[1]; c[2] = bg[2];
        }
        for (int k = 0; k < 3; ++k) {
            float v = c[k] * 255.0f;
            out[i * 3 + k] = (uint8_t)(v < 0.0f ? 0.0f : (v > 255.0f ? 255.0f : v));
        }
    }
    return 0;
}
