/* procedural.c — tileable materials, the 18-product census row.

A material that tiles is a material you can repeat across a wall without a seam. Every one of those
products is selling noise: value fbm, voronoi cells, and a way to make it periodic instead of just
small. The periodicity is the whole trick — naive fbm sampled in [0,1] has a seam every tile because
the lattice does not wrap.

    wubu_noise_fbm      value noise on a wrapped lattice (period P), 4 octaves
    wubu_voronoi        cellular, also wrapped
    wubu_height_to_normal   finite differences -> tangent-space normal map

    gcc -O2 -march=native -shared -fPIC -o libprocedural.so procedural.c -lm
*/

#include <math.h>
#include <stdint.h>
#include <stdlib.h>

static inline uint32_t _h(uint32_t x, uint32_t y, uint32_t seed)
{
    uint32_t n = x * 374761393u + y * 668265263u + seed * 2246822519u;
    n = (n ^ (n >> 13)) * 1274126177u;
    return n ^ (n >> 16);
}

static inline float _rand01(uint32_t v) { return (float)(v & 0xFFFFFF) / 16777215.0f; }

/* lattice value noise with WRAP: coordinates are taken mod period, so the tile meets itself */
static float _value(float x, float y, int period, uint32_t seed)
{
    int x0 = (int)floorf(x), y0 = (int)floorf(y);
    float fx = x - x0, fy = y - y0;
    fx = fx * fx * (3.0f - 2.0f * fx);          /* smoothstep: linear interpolation reads as a grid */
    fy = fy * fy * (3.0f - 2.0f * fy);
    int xa = ((x0 % period) + period) % period, xb = (xa + 1) % period;
    int ya = ((y0 % period) + period) % period, yb = (ya + 1) % period;
    float a = _rand01(_h(xa, ya, seed)), b = _rand01(_h(xb, ya, seed));
    float c = _rand01(_h(xa, yb, seed)), d = _rand01(_h(xb, yb, seed));
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy;
}

int wubu_noise_fbm(float *out, int w, int h, int period, int octaves, float gain, uint32_t seed)
{
    if (!out || w < 1 || h < 1 || period < 1) return -1;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float sum = 0.0f, amp = 1.0f, norm = 0.0f;
            int p = period;
            for (int o = 0; o < octaves; ++o) {
                float u = (float)x / (float)w * (float)p;
                float v = (float)y / (float)h * (float)p;
                sum += amp * _value(u, v, p, seed + (uint32_t)o * 7919u);
                norm += amp;
                amp *= gain;
                p *= 2;                          /* doubling keeps every octave periodic in the tile */
            }
            out[y * w + x] = sum / (norm > 0.0f ? norm : 1.0f);
        }
    }
    return 0;
}

int wubu_voronoi(float *out, int w, int h, int cells, uint32_t seed)
{
    if (!out || w < 1 || h < 1 || cells < 1) return -1;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            float px = (float)x / (float)w * cells, py = (float)y / (float)h * cells;
            int cx = (int)floorf(px), cy = (int)floorf(py);
            float best = 1e9f, second = 1e9f;
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    int gx = ((cx + dx) % cells + cells) % cells;
                    int gy = ((cy + dy) % cells + cells) % cells;
                    uint32_t hv = _h(gx, gy, seed);
                    float ox = cx + dx + _rand01(hv);
                    float oy = cy + dy + _rand01(hv >> 8);
                    float d = sqrtf((px - ox) * (px - ox) + (py - oy) * (py - oy));
                    if (d < best) { second = best; best = d; }
                    else if (d < second) second = d;
                }
            }
            out[y * w + x] = (second - best);    /* cell edge distance: mortar lines */
        }
    }
    return 0;
}

/* height -> tangent-space normal, written as unsigned rgb so it feeds wubu_nmap directly */
int wubu_height_to_normal(const float *hmap, uint8_t *out, int w, int h, float strength)
{
    if (!hmap || !out || w < 2 || h < 2) return -1;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int xl = (x - 1 + w) % w, xr = (x + 1) % w;
            int yu = (y - 1 + h) % h, yd = (y + 1) % h;
            float dx = (hmap[y * w + xr] - hmap[y * w + xl]) * strength;
            float dy = (hmap[yd * w + x] - hmap[yu * w + x]) * strength;
            float nx = -dx, ny = -dy, nz = 1.0f;
            float l = sqrtf(nx * nx + ny * ny + nz * nz);
            int o = (y * w + x) * 4;
            out[o + 0] = (uint8_t)((nx / l * 0.5f + 0.5f) * 255.0f);
            out[o + 1] = (uint8_t)((ny / l * 0.5f + 0.5f) * 255.0f);
            out[o + 2] = (uint8_t)((nz / l * 0.5f + 0.5f) * 255.0f);
            out[o + 3] = 255;
        }
    }
    return 0;
}
