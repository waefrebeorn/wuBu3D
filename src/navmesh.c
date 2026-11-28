/* navmesh.c — A* on a grid, inflated by an agent radius, with a path smoother.

22 Gumroad products sell navmesh and pathfinding. For video it is not about gameplay: it is how a
character walks a route that respects obstacles without the animator plotting every waypoint, and how
a crowd can be scattered and still move.

The grid is a cost field, not a bitmap: 0 = blocked, 255 = free, in between = expensive (sand, stairs).
A* runs 8-connected with a diagonal cost and a Manhattan/octile heuristic, then the path is smoothed by
string-pulling so the actor walks in straight lines instead of stair-steps.

    gcc -O2 -march=native -shared -fPIC -o libnavmesh.so navmesh.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { float f; int idx; } _HN;

static void hpush(_HN *h, int *n, float f, int idx)
{
    int i = (*n)++;
    h[i].f = f; h[i].idx = idx;
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h[p].f <= h[i].f) break;
        _HN t = h[p]; h[p] = h[i]; h[i] = t;
        i = p;
    }
}

static int hpop(_HN *h, int *n, int *idx)
{
    if (*n <= 0) return 0;
    *idx = h[0].idx;
    h[0] = h[--(*n)];
    int i = 0;
    for (;;) {
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < *n && h[l].f < h[m].f) m = l;
        if (r < *n && h[r].f < h[m].f) m = r;
        if (m == i) break;
        _HN t = h[m]; h[m] = h[i]; h[i] = t;
        i = m;
    }
    return 1;
}

/* Inflate blocked cells by `radius` cells (a disc), so the path keeps a body's width of clearance. */
void wubu_nav_inflate(uint8_t *grid, int w, int h, int radius)
{
    if (radius <= 0) return;
    uint8_t *src = malloc((size_t)w * h);
    if (!src) return;
    memcpy(src, grid, (size_t)w * h);
    int r2 = radius * radius;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (src[y * w + x] != 0) continue;
            for (int dy = -radius; dy <= radius; ++dy) {
                for (int dx = -radius; dx <= radius; ++dx) {
                    if (dx * dx + dy * dy > r2) continue;
                    int nx = x + dx, ny = y + dy;
                    if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
                    grid[ny * w + nx] = 0;
                }
            }
        }
    }
    free(src);
}

/* Returns the number of nodes on the path (0 = unreachable). Path is written into out as x,y pairs. */
int wubu_nav_path(const uint8_t *grid, int w, int h, int sx, int sy, int tx, int ty,
                  float *out, int max_pts, int *expanded)
{
    if (sx < 0 || sy < 0 || tx < 0 || ty < 0 || sx >= w || sy >= h || tx >= w || ty >= h) return 0;
    if (grid[ty * w + tx] == 0) return 0;

    int n = w * h;
    float *g = malloc((size_t)n * sizeof(float));
    int *from = malloc((size_t)n * sizeof(int));
    uint8_t *closed = calloc((size_t)n, 1);
    _HN *heap = malloc((size_t)n * 8 * sizeof(_HN));
    if (!g || !from || !closed || !heap) { free(g); free(from); free(closed); free(heap); return 0; }
    for (int i = 0; i < n; ++i) { g[i] = 1e30f; from[i] = -1; }

    int hn = 0, expanded_n = 0;
    int start = sy * w + sx, goal = ty * w + tx;
    g[start] = 0.0f;
    hpush(heap, &hn, 0.0f, start);

    static const int DX[8] = {1, -1, 0, 0, 1, 1, -1, -1};
    static const int DY[8] = {0, 0, 1, -1, 1, -1, 1, -1};
    static const float DC[8] = {1, 1, 1, 1, 1.4142f, 1.4142f, 1.4142f, 1.4142f};

    while (hn > 0) {
        int cur;
        if (!hpop(heap, &hn, &cur)) break;
        if (closed[cur]) continue;
        closed[cur] = 1;
        expanded_n++;
        if (cur == goal) break;
        int cx = cur % w, cy = cur / w;
        for (int k = 0; k < 8; ++k) {
            int nx = cx + DX[k], ny = cy + DY[k];
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
            int ni = ny * w + nx;
            if (grid[ni] == 0 || closed[ni]) continue;
            if (k >= 4 && (grid[cy * w + nx] == 0 || grid[ny * w + cx] == 0)) continue;  /* no corner cut */
            float step = DC[k] * (1.0f + (255 - grid[ni]) / 255.0f * 2.0f);   /* soft ground costs */
            float ng = g[cur] + step;
            if (ng < g[ni]) {
                g[ni] = ng;
                from[ni] = cur;
                int hx = abs(nx - tx), hy = abs(ny - ty);
                float hc = (float)(hx + hy) + (1.4142f - 2.0f) * (float)(hx < hy ? hx : hy);
                hpush(heap, &hn, ng + hc, ni);
            }
        }
    }

    int count = 0;
    if (from[goal] >= 0 || goal == start) {
        int cur = goal, stack[4096], sn = 0;
        while (cur >= 0 && sn < 4096) { stack[sn++] = cur; cur = from[cur]; }
        for (int i = sn - 1; i >= 0 && count < max_pts; --i) {
            out[count * 2] = (float)(stack[i] % w) + 0.5f;
            out[count * 2 + 1] = (float)(stack[i] / w) + 0.5f;
            count++;
        }
    }
    if (expanded) *expanded = expanded_n;
    free(g); free(from); free(closed); free(heap);
    return count;
}

/* String-pull: drop every waypoint that a straight line can replace. Returns the new count. */
static int _line_clear(const uint8_t *grid, int w, int h, float x0, float y0, float x1, float y1,
                      float radius)
{
    float len = sqrtf((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0));
    int steps = (int)(len * 2.0f) + 1;
    for (int s = 0; s <= steps; ++s) {
        float t = (float)s / (float)steps;
        float x = x0 + (x1 - x0) * t, y = y0 + (y1 - y0) * t;
        for (int oy = -1; oy <= 1; ++oy) {
            for (int ox = -1; ox <= 1; ++ox) {
                int ix = (int)(x + ox * radius), iy = (int)(y + oy * radius);
                if (ix < 0 || iy < 0 || ix >= w || iy >= h || grid[iy * w + ix] == 0) return 0;
            }
        }
    }
    return 1;
}

int wubu_nav_smooth(const uint8_t *grid, int w, int h, float *pts, int n, float radius)
{
    if (n < 3) return n;
    int out = 1, anchor = 0;
    while (anchor < n - 1) {
        int best = anchor + 1;
        for (int j = n - 1; j > anchor; --j) {
            if (_line_clear(grid, w, h, pts[anchor * 2], pts[anchor * 2 + 1],
                            pts[j * 2], pts[j * 2 + 1], radius)) {
                best = j;
                break;
            }
        }
        if (out != best) {
            pts[out * 2] = pts[best * 2];
            pts[out * 2 + 1] = pts[best * 2 + 1];
        }
        out++;
        anchor = best;
    }
    return out;
}
