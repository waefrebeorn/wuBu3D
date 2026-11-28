/* particles.c — the largest gap in the census (51 products sell VFX), in C11.

Two halves, because they have different shapes:

  wubu_psys_step   integration in place: gravity, drag, wind, turbulent jitter, lifetime. One loop,
                   no allocation, so a 20k-particle field costs a few hundred microseconds.
  wubu_splat       additive soft discs with a depth test. This is where a particle system actually
                   spends its time: 20k sprites x ~120 px each is 2.4M blended pixels, which Python
                   cannot do at video resolution.

State layout is flat and documented so the caller can drive it from numpy:
    [x, y, z, vx, vy, vz, age, life, size]   9 floats per particle
    [r, g, b, a]                             4 floats of colour per particle (separate arrays)

    gcc -O2 -march=native -shared -fPIC -o libparticles.so particles.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#define PSTRIDE 9

void wubu_psys_step(float *p, int n, float dt,
                    float gx, float gy, float gz,
                    float drag, float windx, float windz,
                    float turb, int seed)
{
    unsigned s = (unsigned)(seed ? seed : 7);
    for (int i = 0; i < n; ++i) {
        float *q = p + i * PSTRIDE;
        if (q[7] > 0.0f && q[6] >= q[7]) continue;          /* dead */

        s = s * 1664525u + 1013904223u;
        float r1 = (float)((s >> 8) & 0xFFFF) / 65535.0f - 0.5f;
        s = s * 1664525u + 1013904223u;
        float r2 = (float)((s >> 8) & 0xFFFF) / 65535.0f - 0.5f;
        s = s * 1664525u + 1013904223u;
        float r3 = (float)((s >> 8) & 0xFFFF) / 65535.0f - 0.5f;

        q[3] += (gx + windx + r1 * turb) * dt;
        q[4] += (gy + r2 * turb) * dt;
        q[5] += (gz + windz + r3 * turb) * dt;
        float k = 1.0f - drag * dt;
        if (k < 0.0f) k = 0.0f;
        q[3] *= k; q[4] *= k; q[5] *= k;
        q[0] += q[3] * dt;
        q[1] += q[4] * dt;
        q[2] += q[5] * dt;
        q[6] += dt;
    }
}

int wubu_psys_alive(const float *p, int n)
{
    int a = 0;
    for (int i = 0; i < n; ++i) {
        const float *q = p + i * PSTRIDE;
        if (q[7] <= 0.0f || q[6] < q[7]) a++;
    }
    return a;
}

/* sprites: s = [sx, sy, depth, radius, r, g, b] per particle, already projected by the caller.
 * Additive, depth-tested, with a smooth falloff so a puff has a soft edge instead of a hard disc. */
int wubu_splat(uint8_t *rgb, float *zb, int w, int h, const float *s, int n)
{
    int drawn = 0;
    for (int i = 0; i < n; ++i) {
        const float *q = s + i * 7;
        float cx = q[0], cy = q[1], z = q[2], rad = q[3];
        if (rad <= 0.25f || z <= 0.0f) continue;
        int x0 = (int)(cx - rad), x1 = (int)(cx + rad) + 1;
        int y0 = (int)(cy - rad), y1 = (int)(cy + rad) + 1;
        if (x1 < 0 || y1 < 0 || x0 >= w || y0 >= h) continue;
        if (x0 < 0) x0 = 0;
        if (y0 < 0) y0 = 0;
        if (x1 > w - 1) x1 = w - 1;
        if (y1 > h - 1) y1 = h - 1;
        float inv = 1.0f / rad;
        for (int y = y0; y <= y1; ++y) {
            float dy = (y + 0.5f - cy) * inv;
            for (int x = x0; x <= x1; ++x) {
                float dx = (x + 0.5f - cx) * inv;
                float d2 = dx * dx + dy * dy;
                if (d2 > 1.0f) continue;
                int idx = y * w + x;
                if (z > zb[idx] + 0.02f) continue;          /* behind solid geometry */
                float a = 1.0f - d2;
                a = a * a;                                   /* soft edge */
                int o = idx * 3;
                float r = rgb[o] + q[4] * a * 255.0f;
                float g = rgb[o + 1] + q[5] * a * 255.0f;
                float b = rgb[o + 2] + q[6] * a * 255.0f;
                rgb[o] = (uint8_t)(r > 255.0f ? 255.0f : r);
                rgb[o + 1] = (uint8_t)(g > 255.0f ? 255.0f : g);
                rgb[o + 2] = (uint8_t)(b > 255.0f ? 255.0f : b);
                drawn++;
            }
        }
    }
    return drawn;
}
