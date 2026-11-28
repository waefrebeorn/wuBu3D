/* scatter.c — procedural placement, the biggest gap in the census (53 products sell it).

Bridson's Poisson-disk sampling: points are at least `radius` apart, so instances look placed rather
than random-clumped, and the cost is O(n) with a grid that only checks 5x5 neighbouring cells.

On top of the sampling, two placement controls every scatter tool sells:
  * exclusion circles — keep a clearing, a path, a doorway (a scatter that fills everything is a
    texture, not a place)
  * per-instance scale and rotation from the same seed, so the field reads as variation

    gcc -O2 -march=native -shared -fPIC -o libscatter.so scatter.c -lm
*/

#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct { unsigned s; } rng_t;

static float frand(rng_t *r)
{
    r->s = r->s * 1664525u + 1013904223u;
    return (float)((r->s >> 8) & 0xFFFFFF) / 16777216.0f;
}

int wubu_poisson(float *out_xy, int max_n, float radius,
                 float x0, float y0, float x1, float y1,
                 unsigned seed, int k_tries,
                 const float *excl, int n_excl,
                 float *out_scale, float *out_rot)
{
    if (!out_xy || max_n < 1 || radius <= 0.0f) return 0;
    float w = x1 - x0, h = y1 - y0;
    if (w <= 0.0f || h <= 0.0f) return 0;
    if (k_tries < 1) k_tries = 30;

    float cell = radius / sqrtf(2.0f);
    int gw = (int)ceilf(w / cell) + 1, gh = (int)ceilf(h / cell) + 1;
    if ((long)gw * gh > 25000000L) return 0;
    int *grid = malloc((size_t)gw * gh * sizeof(int));
    int *active = malloc((size_t)max_n * sizeof(int));
    if (!grid || !active) { free(grid); free(active); return 0; }
    for (int i = 0; i < gw * gh; ++i) grid[i] = -1;

    rng_t rng; rng.s = seed ? seed : 12345u;
    int n = 0, na = 0;

    /* seed point: rejection-sample a valid spot rather than dropping one that lands in a clearing */
    for (int t = 0; t < 4000 && n == 0; ++t) {
        float px = x0 + frand(&rng) * w, py = y0 + frand(&rng) * h;
        int bad = 0;
        for (int e = 0; e < n_excl; ++e) {
            float dx = px - excl[e * 3], dy = py - excl[e * 3 + 1];
            if (dx * dx + dy * dy < excl[e * 3 + 2] * excl[e * 3 + 2]) { bad = 1; break; }
        }
        if (bad) continue;
        out_xy[n * 2] = px; out_xy[n * 2 + 1] = py;
        if (out_scale) out_scale[n] = 0.75f + 0.5f * frand(&rng);
        if (out_rot) out_rot[n] = frand(&rng) * 6.2831853f;
        int gx = (int)((px - x0) / cell), gy = (int)((py - y0) / cell);
        if (gx >= 0 && gx < gw && gy >= 0 && gy < gh) grid[gy * gw + gx] = n;
        active[na++] = n;
        n++;
    }

    while (na > 0 && n < max_n) {
        int ai = (int)(frand(&rng) * na);
        if (ai >= na) ai = na - 1;
        int pi = active[ai];
        float px = out_xy[pi * 2], py = out_xy[pi * 2 + 1];
        int placed = 0;
        for (int k = 0; k < k_tries && !placed && n < max_n; ++k) {
            float ang = frand(&rng) * 6.2831853f;
            float rad = radius * (1.0f + frand(&rng));
            float nx = px + cosf(ang) * rad, ny = py + sinf(ang) * rad;
            if (nx < x0 || nx > x1 || ny < y0 || ny > y1) continue;

            int bad = 0;
            for (int e = 0; e < n_excl && !bad; ++e) {
                float dx = nx - excl[e * 3], dy = ny - excl[e * 3 + 1];
                if (dx * dx + dy * dy < excl[e * 3 + 2] * excl[e * 3 + 2]) bad = 1;
            }
            if (bad) continue;

            int gx = (int)((nx - x0) / cell), gy = (int)((ny - y0) / cell);
            for (int yy = gy - 2; yy <= gy + 2 && !bad; ++yy) {
                if (yy < 0 || yy >= gh) continue;
                for (int xx = gx - 2; xx <= gx + 2 && !bad; ++xx) {
                    if (xx < 0 || xx >= gw) continue;
                    int q = grid[yy * gw + xx];
                    if (q < 0) continue;
                    float dx = nx - out_xy[q * 2], dy = ny - out_xy[q * 2 + 1];
                    if (dx * dx + dy * dy < radius * radius) bad = 1;
                }
            }
            if (bad) continue;

            out_xy[n * 2] = nx; out_xy[n * 2 + 1] = ny;
            if (out_scale) out_scale[n] = 0.75f + 0.5f * frand(&rng);
            if (out_rot) out_rot[n] = frand(&rng) * 6.2831853f;
            if (gx >= 0 && gx < gw && gy >= 0 && gy < gh) grid[gy * gw + gx] = n;
            active[na++] = n;
            n++;
            placed = 1;
        }
        if (!placed) {                       /* retire this active point */
            active[ai] = active[na - 1];
            na--;
        }
    }

    free(grid);
    free(active);
    return n;
}

/* The test is the closest pair: it must be >= radius, and it is the number a uniform random field
 * fails badly (measured 0.0023 against a 0.16 radius). Nearest-neighbour CV is a shape descriptor,
 * not a test: ~0.09 at saturation for Poisson (near the hexagonal limit), ~0.53 for uniform random. */
void wubu_scatter_stats(const float *xy, int n, float *min_dist, float *nn_cv)
{
    if (!xy || n < 2) { if (min_dist) *min_dist = 0.0f; if (nn_cv) *nn_cv = 0.0f; return; }
    float gmin = 1e30f;
    float *nn = malloc((size_t)n * sizeof(float));
    for (int i = 0; i < n; ++i) nn[i] = 1e30f;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) {
            float dx = xy[i * 2] - xy[j * 2], dy = xy[i * 2 + 1] - xy[j * 2 + 1];
            float d = sqrtf(dx * dx + dy * dy);
            if (d < gmin) gmin = d;
            if (d < nn[i]) nn[i] = d;
            if (d < nn[j]) nn[j] = d;
        }
    float mean = 0.0f;
    for (int i = 0; i < n; ++i) mean += nn[i];
    mean /= (float)n;
    float var = 0.0f;
    for (int i = 0; i < n; ++i) var += (nn[i] - mean) * (nn[i] - mean);
    var /= (float)n;
    if (min_dist) *min_dist = gmin;
    if (nn_cv) *nn_cv = mean > 1e-6f ? sqrtf(var) / mean : 0.0f;
    free(nn);
}
