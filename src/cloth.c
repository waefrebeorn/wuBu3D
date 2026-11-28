/* cloth.c — verlet cloth with distance and bend constraints, and pinning.

Closes the "cloth / soft body" row: Houdini ships Vellum, every engine has Chaos or a cloth module,
and a character in a cape with no simulation looks like cardboard.

Verlet is the right choice for video: position-based, unconditionally stable at a fixed step, and
damping is a multiply rather than an integration of friction. Constraint order matters — distance
first, then bend — because bend constraints that run first get violated by the stretch solve.

    gcc -O2 -march=native -shared -fPIC -o libcloth.so cloth.c -lm

State: x,y,z,px,py,pz,inv_mass   (7 floats per particle; inv_mass 0 = pinned)
*/

#include <math.h>
#include <stdint.h>
#include <string.h>

#define CST 7

void wubu_cloth_step(float *p, int n,
                     const int *ca, const int *cb, const float *rest, int ncon,
                     float dt, float gx, float gy, float gz,
                     float damping, int iters, float wind, int seed)
{
    unsigned s = (unsigned)(seed ? seed : 13);
    for (int i = 0; i < n; ++i) {
        float *q = p + i * CST;
        if (q[6] <= 0.0f) {                 /* pinned */
            q[3] = q[0]; q[4] = q[1]; q[5] = q[2];
            continue;
        }
        s = s * 1664525u + 1013904223u;
        float r = (float)((s >> 8) & 0xFFFF) / 65535.0f - 0.5f;
        float ax = gx + wind * r;
        float vx = (q[0] - q[3]) * damping;
        float vy = (q[1] - q[4]) * damping;
        float vz = (q[2] - q[5]) * damping;
        q[3] = q[0]; q[4] = q[1]; q[5] = q[2];
        q[0] += vx + ax * dt * dt;
        q[1] += vy + gy * dt * dt;
        q[2] += vz + gz * dt * dt;
    }

    for (int it = 0; it < iters; ++it) {
        for (int k = 0; k < ncon; ++k) {
            float *a = p + ca[k] * CST;
            float *b = p + cb[k] * CST;
            float w = a[6] + b[6];
            if (w <= 0.0f) continue;
            float dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
            float d = sqrtf(dx * dx + dy * dy + dz * dz);
            if (d < 1e-6f) continue;
            float diff = (d - rest[k]) / d / w;
            float ka = a[6] * diff, kb = b[6] * diff;
            a[0] += dx * ka; a[1] += dy * ka; a[2] += dz * ka;
            b[0] -= dx * kb; b[1] -= dy * kb; b[2] -= dz * kb;
        }
    }
}

/* Stretch error is the honest metric for a cloth solver: mean ||p-q|| - rest| over all constraints,
 * as a fraction of rest length. A solver that goes 900% stretch is a net, not a cape. */
float wubu_cloth_stretch(const float *p, const int *ca, const int *cb, const float *rest, int ncon)
{
    float acc = 0.0f;
    for (int k = 0; k < ncon; ++k) {
        const float *a = p + ca[k] * CST;
        const float *b = p + cb[k] * CST;
        float d = sqrtf((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) +
                        (b[2] - a[2]) * (b[2] - a[2]));
        acc += fabsf(d - rest[k]) / (rest[k] > 1e-5f ? rest[k] : 1e-5f);
    }
    return ncon ? acc / (float)ncon : 0.0f;
}

/* Ground collision: push any particle below y=0 back to it and kill the downward velocity. */
int wubu_cloth_floor(float *p, int n, float y, float friction)
{
    int hits = 0;
    for (int i = 0; i < n; ++i) {
        float *q = p + i * CST;
        if (q[6] <= 0.0f || q[1] >= y) continue;
        q[1] = y;
        q[4] = q[1];
        q[3] = q[0] + (q[3] - q[0]) * friction;
        q[5] = q[2] + (q[5] - q[2]) * friction;
        hits++;
    }
    return hits;
}
