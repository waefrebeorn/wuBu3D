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

/* specular controls, set per render so the shade_tri signature stays intact */
static float g_spec = 0.0f;
static float g_shin = 32.0f;
void wubu_spec(float k, float shin) { g_spec = k; g_shin = shin > 0.5f ? shin : 0.5f; }

/* texture sampling: one bound RGBA image, sampled per pixel through interpolated uv.
   This is the gap every surface in this renderer has had since the first frame. */
static const uint8_t *g_tex = 0;
static int g_tw = 0, g_th = 0;
void wubu_tex(const void *rgba, int w, int h) { g_tex = (const uint8_t *)rgba; g_tw = w; g_th = h; }

/* normal map: a second RGBA image whose rgb is a tangent-space normal, sampled through the same uv.
   14 Gumroad products sell normal mapping and every engine has had it for twenty years; until now a
   surface could only be as detailed as its triangles. */
static const uint8_t *g_nmap = 0;
static int g_nw = 0, g_nh = 0;
static float g_nstr = 1.0f;
void wubu_nmap(const void *rgba, int w, int h, float strength)
{
    g_nmap = (const uint8_t *)rgba; g_nw = w; g_nh = h;
    g_nstr = strength > 0.0f ? strength : 0.0f;
}
void wubu_nmap_off(void) { g_nmap = 0; }

/* alpha test. A hair card, a leaf, a chain-link fence and a smoke sprite are all "a texture with
   holes"; without a discard the quad renders solid and every one of them becomes a sheet of paper.
   Uses the bound albedo texture's alpha channel, so it needs no second binding. */
static float g_alpha_cut = 0.0f;
void wubu_alpha_cut(float t) { g_alpha_cut = t > 0.0f ? t : 0.0f; }

/* subsurface / translucency: wrap the lambert term so light bleeds past the terminator, plus a
   back-light transmission term. Skin and wax read as skin and wax because of this and nothing else —
   a wrapped terminator is the difference between a face and a painted box. */
static float g_sss = 0.0f, g_sss_tint[3] = {1.0f, 0.62f, 0.52f};
void wubu_sss(float k, float r, float g, float b)
{
    g_sss = k > 0.0f ? (k > 0.95f ? 0.95f : k) : 0.0f;
    g_sss_tint[0] = r; g_sss_tint[1] = g; g_sss_tint[2] = b;
}
float wubu_sss_get(void) { return g_sss; }


typedef struct {
    float sx, sy, sz;      /* screen x, y and view depth */
    float wx, wy, wz;      /* world position               */
    float nx, ny, nz;      /* world normal                 */
    float u, v;            /* texture coord (unused in v1) */
} Vert;

#define VSTRIDE 11

static inline float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

/* backface culling: on a closed box half the triangles face away and are pure waste. Opt-in, because
   a single-sided plane (a wall, a sky card) must still draw when seen from behind. */
static int g_cull = 0;
void wubu_cull(int on) { g_cull = on ? 1 : 0; }

/* optional normal G-buffer: when bound, every shaded pixel also writes its world normal. This is the
   pass a compositor needs to relight a shot without re-rendering it — the thing FILM_GAPS.md ranked
   first, and the data the shader already has in hand. */
static float *g_nbuf = 0;
void wubu_gbuf(float *nbuf) { g_nbuf = nbuf; }

/* per-pixel shadow: the map built by shadow.c, bound here with the SAME light matrix. Without this,
   shadows could only be painted on a flat floor — a wall never shaded anything, and light passed
   through geometry, which is the single most obvious tell that a renderer has no shadows at all. */
static const float *g_smap = 0;
static int g_ssize = 0;
static float g_smat[12];
static float g_stan = 1.0f, g_sbias = 0.02f;
void wubu_shadow_bind(const float *depth, int size, const float mat[12], float tan_half, float bias)
{
    g_smap = depth; g_ssize = size;
    for (int i = 0; i < 12; ++i) g_smat[i] = mat[i];
    g_stan = tan_half > 0.01f ? tan_half : 0.01f;
    g_sbias = bias > 0.0f ? bias : 0.0f;
}
void wubu_shadow_unbind(void) { g_smap = 0; g_ssize = 0; }

static inline float _shadow_at(float wx, float wy, float wz)
{
    if (!g_smap || g_ssize < 8) return 1.0f;
    float x = g_smat[0] * wx + g_smat[1] * wy + g_smat[2] * wz + g_smat[3];
    float y = g_smat[4] * wx + g_smat[5] * wy + g_smat[6] * wz + g_smat[7];
    float z = g_smat[8] * wx + g_smat[9] * wy + g_smat[10] * wz + g_smat[11];
    if (z <= 0.05f) return 1.0f;
    float u = (x / (z * g_stan) * 0.5f + 0.5f) * (float)g_ssize;
    float v = (0.5f - y / (z * g_stan) * 0.5f) * (float)g_ssize;
    int lit = 0, taps = 0;
    for (int dy = 0; dy < 2; ++dy) {
        for (int dx = 0; dx < 2; ++dx) {
            int ix = (int)(u + dx - 0.5f), iy = (int)(v + dy - 0.5f);
            taps++;
            if (ix < 0 || iy < 0 || ix >= g_ssize || iy >= g_ssize) { lit++; continue; }
            if (g_smap[iy * g_ssize + ix] + g_sbias > z) lit++;
        }
    }
    return taps ? (float)lit / (float)taps : 1.0f;
}

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

    if (g_cull) {
        float cxw = (a->wx + b->wx + c->wx) / 3.0f;
        float cyw = (a->wy + b->wy + c->wy) / 3.0f;
        float czw = (a->wz + b->wz + c->wz) / 3.0f;
        float vx = eye[0] - cxw, vy = eye[1] - cyw, vz = eye[2] - czw;
        float d = (a->nx + b->nx + c->nx) * vx + (a->ny + b->ny + c->ny) * vy +
                  (a->nz + b->nz + c->nz) * vz;
        if (d <= 0.0f) return 0;
    }

    /* tangent basis from the uv gradient, once per triangle: without it a normal map has no frame to
       live in, and sampling it in world space tilts the bumps with the camera. */
    float tx = 1.0f, ty = 0.0f, tz = 0.0f, bx = 0.0f, by = 1.0f, bz = 0.0f;
    if (g_nmap) {
        float du1 = b->u - a->u, dv1 = b->v - a->v;
        float du2 = c->u - a->u, dv2 = c->v - a->v;
        float det = du1 * dv2 - du2 * dv1;
        if (fabsf(det) > 1e-9f) {
            float id = 1.0f / det;
            float e1x = b->wx - a->wx, e1y = b->wy - a->wy, e1z = b->wz - a->wz;
            float e2x = c->wx - a->wx, e2y = c->wy - a->wy, e2z = c->wz - a->wz;
            tx = (e1x * dv2 - e2x * dv1) * id;
            ty = (e1y * dv2 - e2y * dv1) * id;
            tz = (e1z * dv2 - e2z * dv1) * id;
            bx = (e2x * du1 - e1x * du2) * id;
            by = (e2y * du1 - e1y * du2) * id;
            bz = (e2z * du1 - e1z * du2) * id;
            float tl = sqrtf(tx * tx + ty * ty + tz * tz);
            if (tl > 1e-9f) { tx /= tl; ty /= tl; tz /= tl; }
            float bl = sqrtf(bx * bx + by * by + bz * bz);
            if (bl > 1e-9f) { bx /= bl; by /= bl; bz /= bl; }
        }
    }

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
            float tu = pw * a->u + qw * b->u + rw * c->u;
            float tv = pw * a->v + qw * b->v + rw * c->v;
            float nx = pw * a->nx + qw * b->nx + rw * c->nx;
            float ny = pw * a->ny + qw * b->ny + rw * c->ny;
            float nz = pw * a->nz + qw * b->nz + rw * c->nz;
            float nl = sqrtf(nx * nx + ny * ny + nz * nz);
            if (nl > 1e-6f) { nx /= nl; ny /= nl; nz /= nl; }

            float br = base[0], bg2 = base[1], bb = base[2];
            if (g_tex && g_tw > 0 && g_th > 0) {
                int ux = (int)(tu * (float)g_tw), uy = (int)(tv * (float)g_th);
                ux = ((ux % g_tw) + g_tw) % g_tw;
                uy = ((uy % g_th) + g_th) % g_th;
                const uint8_t *t = g_tex + 4 * (uy * g_tw + ux);
                if (g_alpha_cut > 0.0f && t[3] / 255.0f < g_alpha_cut) continue;
                br *= t[0] / 255.0f; bg2 *= t[1] / 255.0f; bb *= t[2] / 255.0f;
            }
            if (g_nmap && g_nw > 0 && g_nh > 0 && g_nstr > 0.0f) {
                int mx = (int)(tu * (float)g_nw), my = (int)(tv * (float)g_nh);
                mx = ((mx % g_nw) + g_nw) % g_nw;
                my = ((my % g_nh) + g_nh) % g_nh;
                const uint8_t *m = g_nmap + 4 * (my * g_nw + mx);
                float mxv = (m[0] / 127.5f - 1.0f) * g_nstr;
                float myv = (m[1] / 127.5f - 1.0f) * g_nstr;
                float mzv = m[2] / 127.5f;
                float px = nx + tx * mxv + bx * myv;
                float py = ny + ty * mxv + by * myv;
                float pz = nz + tz * mxv + bz * myv;
                float pl = sqrtf(px * px + py * py + pz * pz);
                if (pl > 1e-6f) { nx = px / pl; ny = py / pl; nz = pz / pl; }
            }

            float s = ambient;
            float spec = 0.0f;
            float spec_tint[3] = {0.0f, 0.0f, 0.0f};
            float ex0 = eye[0] - wx_, ey0 = eye[1] - wy_, ez0 = eye[2] - wz_;
            float el0 = sqrtf(ex0*ex0 + ey0*ey0 + ez0*ez0) + 1e-6f;
            ex0 /= el0; ey0 /= el0; ez0 /= el0;
            for (int i = 0; i < nlights; ++i) {
                const float *L = lights + i * 4;
                float dx = L[0] - wx_, dy = L[1] - wy_, dz = L[2] - wz_;
                float d2 = dx * dx + dy * dy + dz * dz;
                float d = sqrtf(d2) + 1e-5f;
                float nd = (nx * dx + ny * dy + nz * dz) / d;
                /* wrapped diffuse: (N.L + w) / (1 + w), so the terminator moves past 90 degrees */
                if (g_sss > 0.0f) {
                    float w = g_sss;
                    float wrap = (nd + w) / (1.0f + w);
                    if (wrap > 0.0f) {
                        float fall = 1.0f / (1.0f + (0.55f / (L[3] * L[3])) * d2);
                        float trans = -nd;              /* light coming through from behind */
                        float t = trans > 0.0f ? trans * trans * w * 1.6f : 0.0f;
                        s += gain * (wrap + t) * fall;
                        spec_tint[0] += t * fall * g_sss_tint[0];
                        spec_tint[1] += t * fall * g_sss_tint[1];
                        spec_tint[2] += t * fall * g_sss_tint[2];
                    }
                }
                if (nd > 0.0f) {
                    float fall = 1.0f / (1.0f + (0.55f / (L[3] * L[3])) * d2);
                    s += gain * nd * fall;
                    if (g_spec > 0.0f) {
                        float hx = dx / d + ex0, hy = dy / d + ey0, hz = dz / d + ez0;
                        float hl = sqrtf(hx*hx + hy*hy + hz*hz) + 1e-6f;
                        float nh = (nx*hx + ny*hy + nz*hz) / hl;
                        if (nh > 0.0f) spec += g_spec * powf(nh, g_shin) * fall;
                    }
                }
            }

            /* contact darkening: a surface is darker the closer it is to the ground it sits on,
               which is the cheapest stand-in for ambient occlusion and the thing that makes parts
               look assembled instead of stacked */
            s *= 0.78f + 0.22f * clampf(wy_ / 0.55f, 0.0f, 1.0f);

            /* shadowed light still gets a little ambient bounce, or shadowed areas go pure black */
            float sh = _shadow_at(wx_, wy_, wz_);
            s *= 0.30f + 0.70f * sh;

            float rim = 0.0f;
            if (rimk > 0.0f) {
                float ex = eye[0] - wx_, ey = eye[1] - wy_, ez = eye[2] - wz_;
                float el = sqrtf(ex * ex + ey * ey + ez * ez) + 1e-5f;
                float f = 1.0f - fabsf((nx * ex + ny * ey + nz * ez) / el);
                f = f * f * f;
                rim = rimk * f;
            }

            float sc = spec * 255.0f;
            /* transmission is tinted by the material, not by the light: that is what makes it read as
               light that travelled through something rather than light that bounced off it */
            float r = br * s + 255.0f * rim + sc + 255.0f * spec_tint[0];
            float g = bg2 * s + 255.0f * rim + sc + 255.0f * spec_tint[1];
            float bl = bb * s + 255.0f * rim + sc + 255.0f * spec_tint[2];
            int o = (py * W + px) * 3;
            rgb[o + 0] = (uint8_t)clampf(r, 0.0f, 255.0f);
            rgb[o + 1] = (uint8_t)clampf(g, 0.0f, 255.0f);
            rgb[o + 2] = (uint8_t)clampf(bl, 0.0f, 255.0f);
            zb[py * W + px] = z;
            if (g_nbuf) {
                int q = (py * W + px) * 3;
                g_nbuf[q] = nx; g_nbuf[q + 1] = ny; g_nbuf[q + 2] = nz;
            }
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


/* batch entry: the whole scene in one call.

Measured reason this exists: a 4800-triangle frame took 229 ms, and a bare shade_tri call on a
200x200 pixel triangle costs 8.9 us. At 47.8 us per triangle in the real scene, ~82% of the frame
was Python making ctypes calls and rebuiling a 3x11 block per triangle, not rasterising. Moving the
loop into C does not make the shader faster; it removes the interpreter from the inner loop.
*/
int wubu_shade_batch(uint8_t *rgb, float *zb, int W, int H,
                     const float *verts, int ntri, const float *cols,
                     const float *lights, int nlights,
                     float ambient, float gain, float rim, const float *eye)
{
    int drawn = 0;
    for (int t = 0; t < ntri; ++t) {
        drawn += shade_tri(rgb, zb, W, H, verts + (size_t)t * 3 * VSTRIDE,
                           cols + (size_t)t * 3, lights, nlights, ambient, gain, rim, eye);
    }
    return drawn;
}
