// wuburaster v5 — C11 rasteriser: opaque pass, near-plane clipping, weighted blended OIT.
//
// SLERM note: pipeline shape from CubeCoders/Jet (fixed-function, zero deps, framebuffer
// out) and Whisk3D (retro-first); the transparent solution is McGuire & Bavoil's weighted
// blended order-independent transparency, as demonstrated in Lele Feng's OIT_Lab. The code
// is ours, against our own WB3D stream; nothing was copied.
//
// Why OIT: alpha blending is only correct back-to-front, so engines sort whole objects by
// centre. Four panes sharing a centre, or crossing each other, sort wrong, and inside one
// mesh the triangles draw in index order. Weighted blended OIT removes the sort entirely —
// addition and multiplication commute.
//
//   accum  (RGBA float, starts 0, additive):  += (colour * a * w,  a * w)
//   reveal (R float, starts 1, multiply):     *= (1 - a)
//   resolve:  avg = accum.rgb / max(accum.a, 1e-4)
//             out = avg * (1 - reveal) + background * reveal
//
//   weight w = a * clamp(10 / (1e-5 + (z/5)^2 + (z/200)^6), 0.01, 3000)
//
// Vertex (20 B): f32 x,y,z  u8 r,g,b,a  u8 tag, pad,pad,pad     (a = 255 means opaque)
// Frame: 16 floats — cam xyz, target xyz, fov, fog, lantern xyz, intensity, sun rgb, pad
//
// Usage: wuburaster <prefix> [--no-oit]     (--no-oit reproduces the sorted-free failure)
//
// Build: cc -O3 -march=native -std=c11 -o wuburaster wuburaster.c -lm

#define _POSIX_C_SOURCE 199309L
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define NEAR_Z 0.06f

typedef struct { float x, y, z; uint8_t r, g, b, a; uint8_t tag, p1, p2, p3; } Vert;
typedef struct { uint32_t a, b, c; } Tri;
typedef struct {
    float cx, cy, cz, tx, ty, tz, fov, fog;
    float lx, ly, lz, li;
    float sc_r, sc_g, sc_b, ambient;
    /* Movie Render Queue's temporal sample count, cheap version: each subframe is the
       same scene at a subpixel offset (anti-aliasing) and a subframe time (motion blur).
       Two floats buy both, because the caller averages the subframes. */
    float jitter_x, jitter_y, pad1, pad2;
} Frame;

typedef struct { float vx, vy, vz; float sh[3]; float kd[3]; float n[3]; float a; uint8_t tag; } CVert;

static inline void vsub(const float *a,const float *b,float *o){o[0]=a[0]-b[0];o[1]=a[1]-b[1];o[2]=a[2]-b[2];}
static inline void vcross(const float *a,const float *b,float *o){o[0]=a[1]*b[2]-a[2]*b[1];o[1]=a[2]*b[0]-a[0]*b[2];o[2]=a[0]*b[1]-a[1]*b[0];}
static inline float vdot(const float *a,const float *b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
static inline float vlen(const float *a){return sqrtf(vdot(a,a));}
static inline void vnorm(float *a){float l=vlen(a);if(l>1e-8f){a[0]/=l;a[1]/=l;a[2]/=l;}}

typedef struct {
    float eye[3], right[3], up[3], fwd[3];
    float focal, cx, cy;
    uint32_t w, h;
    float *depth; float *nrmbuf; uint8_t *fb;
    float *acc;   /* 4 floats: rgb premultiplied by weight, weight */
    float *rev;   /* 1 float: revealage */
    int no_oit;
    int no_cull;          /* --no-cull: draw everything, for an A/B measurement */
    int cw, ch;           /* coarse buffer size */
    float *coarse;        /* nearest z per coarse pixel */
    float *region_max;    /* farthest nearest-z per 32x32 screen region */
    uint32_t nrx, nry;
    uint32_t culled;
    int32_t sb_minx, sb_miny, sb_maxx, sb_maxy;
    Frame fr;
} Ctx;

static int clip_near(const CVert in[3], CVert out[4]) {
    int n = 0;
    for (int i = 0; i < 3; i++) {
        const CVert *a = &in[i], *b = &in[(i + 1) % 3];
        float da = a->vz - NEAR_Z, db = b->vz - NEAR_Z;
        if (da >= 0.0f) out[n++] = *a;
        if ((da >= 0.0f) != (db >= 0.0f)) {
            float t = da / (da - db);
            CVert c;
            c.vx = a->vx + (b->vx - a->vx) * t;
            c.vy = a->vy + (b->vy - a->vy) * t;
            c.vz = NEAR_Z;
            for (int k = 0; k < 3; k++) {
                c.sh[k] = a->sh[k] + (b->sh[k] - a->sh[k]) * t;
                c.kd[k] = a->kd[k] + (b->kd[k] - a->kd[k]) * t;
                c.n[k]  = a->n[k]  + (b->n[k]  - a->n[k])  * t;
            }
            c.a = a->a + (b->a - a->a) * t;
            c.tag = a->tag | b->tag;
            out[n++] = c;
        }
    }
    return n;
}

/* Software occlusion culling, the cheap kind: rasterise everything once at 1/8
   resolution to learn the nearest surface per coarse pixel, summarise each 32x32
   screen region by the FARTHEST of those nearest values, then in the expensive pass
   skip any triangle whose nearest vertex is behind that number. Sound because a
   triangle behind every occluder in its region cannot be seen. */
static void build_coarse(Ctx *c, const Vert *verts, const Tri *tris, uint32_t nt, const float *vn) {
    const uint32_t cw = c->cw, ch = c->ch;
    for (size_t i = 0; i < (size_t)cw*ch; i++) c->coarse[i] = 1e30f;
    const float fx = (float)cw / (float)c->w, fy = (float)ch / (float)c->h;

    for (uint32_t t = 0; t < nt; t++) {
        const Vert *V[3] = { &verts[tris[t].a], &verts[tris[t].b], &verts[tris[t].c] };
        if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) continue;   /* glass never occludes */
        float sx[3], sy[3], iz[3]; int behind = 0;
        for (int k = 0; k < 3; k++) {
            float d[3], pw[3] = { V[k]->x, V[k]->y, V[k]->z };
            vsub(pw, c->eye, d);
            float vz = vdot(d, c->fwd);
            if (vz < NEAR_Z) { behind = 1; break; }
            float vx = vdot(d, c->right), vy = vdot(d, c->up);
            sx[k] = (c->cx + c->focal * vx / vz) * fx;
            sy[k] = (c->cy - c->focal * vy / vz) * fy;
            iz[k] = 1.0f / vz;
        }
        if (behind) continue;
        int x0 = (int)floorf(fminf(sx[0], fminf(sx[1], sx[2])));
        int x1 = (int)ceilf (fmaxf(sx[0], fmaxf(sx[1], sx[2])));
        int y0 = (int)floorf(fminf(sy[0], fminf(sy[1], sy[2])));
        int y1 = (int)ceilf (fmaxf(sy[0], fmaxf(sy[1], sy[2])));
        if (x1 < 0 || y1 < 0 || x0 >= (int)cw || y0 >= (int)ch) continue;
        if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0;
        if (x1 >= (int)cw) x1 = (int)cw-1; if (y1 >= (int)ch) y1 = (int)ch-1;
        float area = (sx[1]-sx[0])*(sy[2]-sy[0]) - (sx[2]-sx[0])*(sy[1]-sy[0]);
        if (fabsf(area) < 1e-6f) continue;
        float ia = 1.0f/area;
        for (int y = y0; y <= y1; y++)
            for (int x = x0; x <= x1; x++) {
                float px = x + 0.5f, py = y + 0.5f;
                float w0 = ((sx[1]-px)*(sy[2]-py) - (sx[2]-px)*(sy[1]-py)) * ia;
                float w1 = ((sx[2]-px)*(sy[0]-py) - (sx[0]-px)*(sy[2]-py)) * ia;
                float w2 = 1.0f - w0 - w1;
                if (w0 < 0 || w1 < 0 || w2 < 0) continue;
                float z = 1.0f / (w0*iz[0] + w1*iz[1] + w2*iz[2]);
                float *cell = &c->coarse[(size_t)y*cw + x];
                if (z < *cell) *cell = z;
            }
    }

    for (uint32_t ry = 0; ry < c->nry; ry++)
        for (uint32_t rx = 0; rx < c->nrx; rx++) {
            float mx = 0.0f; int any = 0;
            uint32_t y0 = ry*32, y1 = y0+32, x0 = rx*32, x1 = x0+32;
            if (y1 > ch) y1 = ch; if (x1 > cw) x1 = cw;
            for (uint32_t y = y0; y < y1; y++)
                for (uint32_t x = x0; x < x1; x++) {
                    float z = c->coarse[(size_t)y*cw + x];
                    if (z > 1e29f) continue;
                    if (!any || z > mx) { mx = z; any = 1; }
                }
            c->region_max[(size_t)ry*c->nrx + rx] = any ? mx : -1.0f;
        }
}

static float oit_weight(float a, float z) {
    float d = z / 5.0f, d2 = d * d;
    float f = d / 200.0f, f6 = f * f * f; f6 = f6 * f6;
    float w = 10.0f / (1e-5f + d2 + f6);
    if (w < 0.01f) w = 0.01f;
    if (w > 3000.0f) w = 3000.0f;
    return a * w;
}


/* ── shadow map ────────────────────────────────────────────────────────────────
   The one thing a fixed-function rasteriser normally cannot do. SH4DER-PVR's psm
   route B does it as a depth map plus a per-receiver compare; the same shape works
   here per pixel with 2x2 PCF. The map is built from the opaque triangles already
   in the frame's stream, so the wire format does not change and the light is the
   same fixed key direction the vertex shader uses.                              */
#define SM 512
static float sm_depth[SM*SM];
static float sm_r[3], sm_u[3], sm_f[3], sm_c[3], sm_scale;
static int sm_ok = 0;

static int is_ground_tri(const Vert *A, const Vert *B, const Vert *C) {
    return A->z < 0.2f && B->z < 0.2f && C->z < 0.2f;
}

static void build_shadowmap(const Vert *verts, const Tri *tris, uint32_t nt, const float *sun) {
    sm_ok = 0;
    if (nt == 0) return;
    float up[3] = {0,0,1};
    if (fabsf(sun[2]) > 0.95f) { up[0]=1; up[1]=0; up[2]=0; }
    vcross(up, sun, sm_r); vnorm(sm_r);
    vcross(sun, sm_r, sm_u); vnorm(sm_u);
    for (int k=0;k<3;k++) sm_f[k] = sun[k];

    float mn[3] = {1e30f,1e30f,1e30f}, mx[3] = {-1e30f,-1e30f,-1e30f};
    int any = 0;
    for (uint32_t i = 0; i < nt; i++) {
        const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
        if (is_ground_tri(V[0], V[1], V[2])) continue;
        any = 1;
        for (int k = 0; k < 3; k++) {
            const float p[3] = { V[k]->x, V[k]->y, V[k]->z };
            for (int a = 0; a < 3; a++) { if (p[a]<mn[a]) mn[a]=p[a]; if (p[a]>mx[a]) mx[a]=p[a]; }
        }
    }
    if (!any) return;
    for (int k=0;k<3;k++) sm_c[k] = 0.5f*(mn[k]+mx[k]);
    float dx = mx[0]-mn[0], dy = mx[1]-mn[1], dz = mx[2]-mn[2];
    float radius = 0.5f*sqrtf(dx*dx + dy*dy + dz*dz);
    if (radius < 8.0f) radius = 8.0f;
    if (radius > 90.0f) radius = 90.0f;
    sm_scale = (float)SM / (2.0f * radius);

    for (size_t i = 0; i < (size_t)SM*SM; i++) sm_depth[i] = -1e30f;   /* d grows toward the light */

    for (uint32_t i = 0; i < nt; i++) {
        const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
        if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) continue;   /* glass casts nothing */
        if (is_ground_tri(V[0], V[1], V[2])) continue;                    /* the receiver */
        float qx[3], qy[3], qd[3];
        for (int k = 0; k < 3; k++) {
            const float p[3] = { V[k]->x, V[k]->y, V[k]->z };
            float rel[3]; vsub(p, sm_c, rel);
            qx[k] = SM*0.5f + vdot(rel, sm_r) * sm_scale;
            qy[k] = SM*0.5f - vdot(rel, sm_u) * sm_scale;
            qd[k] = vdot(rel, sm_f);
        }
        float area = (qx[1]-qx[0])*(qy[2]-qy[0]) - (qx[2]-qx[0])*(qy[1]-qy[0]);
        if (fabsf(area) < 1e-4f) continue;
        if (area < 0.0f) {            /* a caster wound either way still casts */
            float tf;
            tf = qx[1]; qx[1] = qx[2]; qx[2] = tf;
            tf = qy[1]; qy[1] = qy[2]; qy[2] = tf;
            tf = qd[1]; qd[1] = qd[2]; qd[2] = tf;
            area = -area;
        }
        float ia = 1.0f/area;
        int x0 = (int)floorf(fminf(qx[0], fminf(qx[1], qx[2])));
        int x1 = (int)ceilf (fmaxf(qx[0], fmaxf(qx[1], qx[2])));
        int y0 = (int)floorf(fminf(qy[0], fminf(qy[1], qy[2])));
        int y1 = (int)ceilf (fmaxf(qy[0], fmaxf(qy[1], qy[2])));
        if (x0 < 0) x0 = 0; if (y0 < 0) y0 = 0;
        if (x1 > SM-1) x1 = SM-1; if (y1 > SM-1) y1 = SM-1;
        for (int y = y0; y <= y1; y++) {
            for (int x = x0; x <= x1; x++) {
                float px = x + 0.5f, py = y + 0.5f;
                float w0 = ((qx[1]-px)*(qy[2]-py) - (qx[2]-px)*(qy[1]-py)) * ia;
                float w1 = ((qx[2]-px)*(qy[0]-py) - (qx[0]-px)*(qy[2]-py)) * ia;
                float w2 = 1.0f - w0 - w1;
                if (w0 < 0 || w1 < 0 || w2 < 0) continue;
                float z = w0*qd[0] + w1*qd[1] + w2*qd[2];
                size_t idx = (size_t)y*SM + x;
                if (z > sm_depth[idx]) sm_depth[idx] = z;    /* keep the closest to the light */
            }
        }
    }
    sm_ok = 1;
}

/* 0 = fully shadowed, 1 = fully lit; 2x2 PCF, slope-independent world bias */
static long dbg_frag = 0, dbg_hit = 0, dbg_shadowed = 0;
static float shadow_vis(const float *p) {
    dbg_frag++;
    if (!sm_ok) return 1.0f;
    float rel[3]; vsub(p, sm_c, rel);
    float u = SM*0.5f + vdot(rel, sm_r) * sm_scale;
    float v = SM*0.5f - vdot(rel, sm_u) * sm_scale;
    float d = vdot(rel, sm_f);
    int x0 = (int)u, y0 = (int)v;
    if (x0 < 1 || y0 < 1 || x0 >= SM-2 || y0 >= SM-2) return 1.0f;
    dbg_hit++;
    int lit = 0;
    for (int dy = 0; dy < 2; dy++)
        for (int dx = 0; dx < 2; dx++) {
            float s = sm_depth[(size_t)(y0+dy)*SM + (x0+dx)];
            if (s < -1e29f || d + 0.16f >= s) lit++;
        }
    if (lit < 4) dbg_shadowed++;
    return lit * 0.25f;
}

static void raster_tri(Ctx *c, const CVert *A, const CVert *B, const CVert *C, int transparent) {
    const CVert *p3[3] = { A, B, C };
    int32_t sx[3], sy[3]; float iz[3];
    for (int k = 0; k < 3; k++) {
        sx[k] = (int32_t)lrintf(c->cx + c->fr.jitter_x + c->focal * p3[k]->vx / p3[k]->vz);
        sy[k] = (int32_t)lrintf(c->cy + c->fr.jitter_y - c->focal * p3[k]->vy / p3[k]->vz);
        iz[k] = 1.0f / p3[k]->vz;
    }
    int32_t minx = sx[0], maxx = sx[0], miny = sy[0], maxy = sy[0];
    for (int k = 1; k < 3; k++) {
        if (sx[k] < minx) minx = sx[k];
        if (sx[k] > maxx) maxx = sx[k];
        if (sy[k] < miny) miny = sy[k];
        if (sy[k] > maxy) maxy = sy[k];
    }
    if (maxx < 0 || maxy < 0 || minx >= (int32_t)c->w || miny >= (int32_t)c->h) return;
    if (minx < 0) minx = 0;
    if (miny < 0) miny = 0;
    if (maxx >= (int32_t)c->w) maxx = (int32_t)c->w - 1;
    if (maxy >= (int32_t)c->h) maxy = (int32_t)c->h - 1;

    float area = (float)((sx[1]-sx[0])*(sy[2]-sy[0]) - (sx[2]-sx[0])*(sy[1]-sy[0]));
    if (fabsf(area) < 1e-6f) return;
    if (area < 0.0f) {
        /* double-sided: an imported OBJ can be wound either way, and a face wound the
           other way used to vanish instead of drawing. Swapping two corners keeps the
           positive-barycentric fill and flips nothing else. */
        const CVert *tp = p3[1]; p3[1] = p3[2]; p3[2] = tp;
        int32_t ti = sx[1]; sx[1] = sx[2]; sx[2] = ti;
        ti = sy[1]; sy[1] = sy[2]; sy[2] = ti;
        float tf = iz[1]; iz[1] = iz[2]; iz[2] = tf;
        area = -area;
    }
    const float ia = 1.0f / area;

    /* Edge functions are linear in x and y, so step them: one add per pixel and one per
       row, instead of two products and four subtractions per pixel. Pineda's method, and
       the same trick Jet's span walker uses. The weights are advanced at the TOP of the
       body so every `continue` below stays correct. */
    const float e0x = (sy[1] - sy[2]) * ia, e0y = (sx[2] - sx[1]) * ia;
    const float e1x = (sy[2] - sy[0]) * ia, e1y = (sx[0] - sx[2]) * ia;
    const float px0 = minx + 0.5f, py0 = miny + 0.5f;
    float row0 = ((sx[1]-px0)*(sy[2]-py0) - (sx[2]-px0)*(sy[1]-py0)) * ia;
    float row1 = ((sx[2]-px0)*(sy[0]-py0) - (sx[0]-px0)*(sy[2]-py0)) * ia;

    for (int32_t y = miny; y <= maxy; y++) {
        float rw0 = row0, rw1 = row1;
        for (int32_t x = minx; x <= maxx; x++) {
            const float w0 = rw0, w1 = rw1;
            rw0 += e0x; rw1 += e1x;
            const float w2 = 1.0f - w0 - w1;
            if (w0 < 0 || w1 < 0 || w2 < 0) continue;
            const float px = x + 0.5f, py = y + 0.5f;
            const float izp = w0*iz[0] + w1*iz[1] + w2*iz[2];
            const float z = 1.0f / izp;
            const size_t idx = (size_t)y * c->w + x;

            /* glass is tested against the opaque depth; it never writes it */
            if (z >= c->depth[idx]) continue;

            const float b0 = w0*iz[0]/izp, b1 = w1*iz[1]/izp, b2 = w2*iz[2]/izp;
            float nn[3];
            for (int k = 0; k < 3; k++)
                nn[k] = b0*p3[0]->n[k] + b1*p3[1]->n[k] + b2*p3[2]->n[k];
            vnorm(nn);

            const Frame *fr = &c->fr;
            float fogh = 1.0f - expf(-z / (fr->fog > 0 ? fr->fog : 120.0f));
            if (fogh > 1.0f) fogh = 1.0f;

            float base[3], keyt[3];
            for (int k = 0; k < 3; k++) {
                base[k] = b0*p3[0]->sh[k] + b1*p3[1]->sh[k] + b2*p3[2]->sh[k];
                keyt[k] = b0*p3[0]->kd[k] + b1*p3[1]->kd[k] + b2*p3[2]->kd[k];
            }

            if (!transparent) {
                c->depth[idx] = z;
                if (A->tag || B->tag || C->tag) {
                    if (x < c->sb_minx) c->sb_minx = x;
                    if (y < c->sb_miny) c->sb_miny = y;
                    if (x > c->sb_maxx) c->sb_maxx = x;
                    if (y > c->sb_maxy) c->sb_maxy = y;
                }
                c->nrmbuf[idx*3] = nn[0]; c->nrmbuf[idx*3+1] = nn[1]; c->nrmbuf[idx*3+2] = nn[2];

                float wxp = c->eye[0] + c->right[0]*(px-c->cx)*z/c->focal + c->up[0]*(c->cy-py)*z/c->focal + c->fwd[0]*z;
                float wyp = c->eye[1] + c->right[1]*(px-c->cx)*z/c->focal + c->up[1]*(c->cy-py)*z/c->focal + c->fwd[1]*z;
                float wzp = c->eye[2] + c->right[2]*(px-c->cx)*z/c->focal + c->up[2]*(c->cy-py)*z/c->focal + c->fwd[2]*z;
                const float wp[3] = { wxp, wyp, wzp };
                const float ksum = keyt[0] + keyt[1] + keyt[2];
                const float vis = ksum > 0.35f ? shadow_vis(wp) : 1.0f;   /* no sun here: skip 4 taps */
                for (int k = 0; k < 3; k++) base[k] += vis*keyt[k];
                float dlx = fr->lx-wxp, dly = fr->ly-wyp, dlz = fr->lz-wzp;
                float dl = sqrtf(dlx*dlx + dly*dly + dlz*dlz) + 1e-4f;
                float att = fr->li / (1.0f + dl*dl*2.2f);
                float ndl = (nn[0]*dlx + nn[1]*dly + nn[2]*dlz) / dl;
                if (ndl < 0.0f) ndl = 0.0f;
                float attr = att * ndl;
                if (attr > 0.55f) attr = 0.55f;
                /* the lamp also scales the surface, for the same reason: adding a fixed
                   warm value on top of albedo is a wash, not a light */
                float kk = 1.0f + attr*2.0f;
                base[0] *= kk*1.04f;
                base[1] *= kk*1.00f;
                base[2] *= kk*0.94f;
                float haze_l = att * 0.55f;
                uint8_t *out = c->fb + 3*idx;
                for (int k = 0; k < 3; k++) {
                    float sk = (k==0?11.f:k==1?14.f:21.f) +
                               (k==0?haze_l*70.f:k==1?haze_l*42.f:haze_l*18.f);
                    out[k] = (uint8_t)fminf(255.0f, base[k]*(1-fogh) + sk*fogh);
                }
                continue;
            }

            /* transparent fragment */
            float a = b0*p3[0]->a + b1*p3[1]->a + b2*p3[2]->a;
            if (a <= 0.001f) continue;
            for (int k = 0; k < 3; k++)
                base[k] = (base[k] + keyt[k])*(1-fogh) + (k==0?11.f:k==1?14.f:21.f)*fogh;

            if (c->no_oit) {
                /* the failure mode: draw in index order with plain alpha blending */
                uint8_t *out = c->fb + 3*idx;
                for (int k = 0; k < 3; k++)
                    out[k] = (uint8_t)fminf(255.0f, base[k]*a + out[k]*(1-a));
                continue;
            }
            float wgt = oit_weight(a, z);
            c->acc[idx*4+0] += base[0] * a * wgt;
            c->acc[idx*4+1] += base[1] * a * wgt;
            c->acc[idx*4+2] += base[2] * a * wgt;
            c->acc[idx*4+3] += a * wgt;
            c->rev[idx] *= (1.0f - a);
        }
        row0 += e0y; row1 += e1y;
    }
}

int main(int argc, char **argv) {
    const char *prefix = argc > 1 ? argv[1] : "frame_";
    int no_oit = 0;
    int no_cull = 0;
    int no_shadow = 0;
    int no_sort = 1;      /* --sort opts into depth-bucket ordering; measured inconclusive under load */
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--no-oit")) no_oit = 1;
        if (!strcmp(argv[i], "--no-cull")) no_cull = 1;
        if (!strcmp(argv[i], "--no-shadow")) no_shadow = 1;
        if (!strcmp(argv[i], "--sort")) no_sort = 0;
        if (!strcmp(argv[i], "--sort")) no_sort = 0;
    }

    char magic[4]; uint32_t nf, w, h;
    if (fread(magic,1,4,stdin)!=4 || memcmp(magic,"WB3D",4)) { fprintf(stderr,"wuburaster: bad magic\n"); return 1; }
    if (fread(&nf,4,1,stdin)!=1 || fread(&w,4,1,stdin)!=1 || fread(&h,4,1,stdin)!=1) {
        fprintf(stderr,"wuburaster: short header\n"); return 1;
    }

    Ctx ctx; memset(&ctx, 0, sizeof ctx);
    ctx.w = w; ctx.h = h; ctx.no_oit = no_oit; ctx.no_cull = no_cull;
    ctx.cw = (int)(w/8 ? w/8 : 1); ctx.ch = (int)(h/8 ? h/8 : 1);
    ctx.nrx = (ctx.cw + 31) / 32; ctx.nry = (ctx.ch + 31) / 32;
    ctx.coarse = malloc(sizeof(float)*(size_t)ctx.cw*ctx.ch);
    ctx.region_max = malloc(sizeof(float)*(size_t)ctx.nrx*ctx.nry);
    ctx.depth = malloc(sizeof(float)*(size_t)w*h);
    ctx.nrmbuf = malloc(sizeof(float)*3*(size_t)w*h);
    ctx.fb = malloc(3*(size_t)w*h);
    ctx.acc = malloc(sizeof(float)*4*(size_t)w*h);
    ctx.rev = malloc(sizeof(float)*(size_t)w*h);
    if (!ctx.depth || !ctx.nrmbuf || !ctx.fb || !ctx.acc || !ctx.rev ||
        !ctx.coarse || !ctx.region_max) return 1;

    float g_amb = 0.15f;      /* frame-supplied ambient: an interior needs a lower floor */
    float lkey[3]  = {-0.45f,-0.52f, 0.72f}; vnorm(lkey);
    float lfill[3] = { 0.62f, 0.30f, 0.18f}; vnorm(lfill);

    uint32_t total_tris = 0, glass_tris = 0;
    long shadow_ns = 0;
    struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);

    for (uint32_t f = 0; f < nf; f++) {
        uint32_t nv, nt;
        if (fread(&nv,4,1,stdin)!=1 || fread(&nt,4,1,stdin)!=1) {
            fprintf(stderr,"wuburaster: eof at frame %u\n",f); return 1;
        }
        Vert *verts = malloc(sizeof(Vert)*nv);
        Tri  *tris  = malloc(sizeof(Tri)*nt);
        float *vn   = calloc((size_t)nv*3, sizeof(float));
        if (!verts||!tris||!vn) return 1;
        if (fread(verts,sizeof(Vert),nv,stdin)!=nv) { fprintf(stderr,"wuburaster: short verts\n"); return 1; }
        if (fread(tris,sizeof(Tri),nt,stdin)!=nt) { fprintf(stderr,"wuburaster: short tris\n"); return 1; }
        Frame fr; if (fread(&fr,sizeof(Frame),1,stdin)!=1) { fprintf(stderr,"wuburaster: short frame\n"); return 1; }
        total_tris += nt;
        /* the coarse pass costs about as much as rasterising 4k tiny triangles, so it is
           only worth running once the frame is big enough to pay it back */
        ctx.no_cull = no_cull || (nt <= 4000);

        for (uint32_t i=0;i<nt;i++){
            const Vert *A=&verts[tris[i].a],*B=&verts[tris[i].b],*C=&verts[tris[i].c];
            float p0[3]={A->x,A->y,A->z},p1[3]={B->x,B->y,B->z},p2[3]={C->x,C->y,C->z};
            float e1[3],e2[3],n[3]; vsub(p1,p0,e1); vsub(p2,p0,e2); vcross(e1,e2,n);
            for (int k=0;k<3;k++){ vn[tris[i].a*3+k]+=n[k]; vn[tris[i].b*3+k]+=n[k]; vn[tris[i].c*3+k]+=n[k]; }
        }
        for (uint32_t i=0;i<nv;i++){ float n[3]={vn[i*3],vn[i*3+1],vn[i*3+2]}; vnorm(n);
            vn[i*3]=n[0]; vn[i*3+1]=n[1]; vn[i*3+2]=n[2]; }

        ctx.sb_minx = 1 << 30; ctx.sb_miny = 1 << 30; ctx.sb_maxx = -1; ctx.sb_maxy = -1;
        ctx.fr = fr;
        g_amb = (fr.ambient > 0.0f) ? fr.ambient : 0.24f;
        ctx.eye[0]=fr.cx; ctx.eye[1]=fr.cy; ctx.eye[2]=fr.cz;
        float tg[3] = {fr.tx,fr.ty,fr.tz};
        vsub(tg, ctx.eye, ctx.fwd); vnorm(ctx.fwd);
        float up0[3] = {0,0,1}; if (fabsf(ctx.fwd[2]) > 0.98f) { up0[0]=1; up0[1]=0; up0[2]=0; }
        vcross(ctx.fwd, up0, ctx.right); vnorm(ctx.right);
        vcross(ctx.right, ctx.fwd, ctx.up);
        ctx.focal = (float)h*0.5f/tanf(fr.fov*0.5f*(float)M_PI/180.0f);
        ctx.cx = w*0.5f; ctx.cy = h*0.5f;

        for (uint32_t y=0;y<h;y++){
            float t=(float)y/(float)(h-1);
            uint8_t r=(uint8_t)(12+16*(1-t)), g=(uint8_t)(16+20*(1-t)), b=(uint8_t)(26+24*(1-t));
            for (uint32_t x=0;x<w;x++){
                size_t i=(size_t)y*w+x;
                uint8_t *p=ctx.fb+3*i; p[0]=r;p[1]=g;p[2]=b;
                ctx.depth[i]=1e30f;
                ctx.nrmbuf[i*3]=0; ctx.nrmbuf[i*3+1]=0; ctx.nrmbuf[i*3+2]=1;
                ctx.acc[i*4]=0; ctx.acc[i*4+1]=0; ctx.acc[i*4+2]=0; ctx.acc[i*4+3]=0;
                ctx.rev[i]=1.0f;
            }
        }

        if (!ctx.no_cull) build_coarse(&ctx, verts, tris, nt, vn);

        if (!no_shadow) {
            struct timespec s0, s1; clock_gettime(CLOCK_MONOTONIC,&s0);
            build_shadowmap(verts, tris, nt, lkey);
            clock_gettime(CLOCK_MONOTONIC,&s1);
            shadow_ns += (s1.tv_sec-s0.tv_sec)*1000000000L + (s1.tv_nsec-s0.tv_nsec);
        }

        /* One transform and one shade per VERTEX per frame, not per face. A closed mesh
           shares every vertex between ~6 triangles, so the old loop repeated the same
           dot products six times: 2,534 tris meant 7,602 transforms where 1,660 would do.
           Jet calls this position reuse; here it is simply not doing the work twice. */
        CVert *vc = malloc(sizeof(CVert) * nv);
        if (!vc) return 1;
        for (uint32_t i = 0; i < nv; i++) {
            float d[3], pw[3] = { verts[i].x, verts[i].y, verts[i].z };
            vsub(pw, ctx.eye, d);
            vc[i].vx = vdot(d, ctx.right);
            vc[i].vy = vdot(d, ctx.up);
            vc[i].vz = vdot(d, ctx.fwd);
            float nl[3] = { vn[i*3], vn[i*3+1], vn[i*3+2] };
            vnorm(nl);
            float ndl = fabsf(vdot(nl, lkey));
            float ndf = fmaxf(vdot(nl, lfill), 0.0f);
            float s = g_amb + 0.16f*ndf;        /* ambient and fill: never shadowed */
            /* The key falls off with distance from the lamp. Without it every surface in a
               12 m room received the same light, which is why a dungeon read as a flat white
               sheet: no gradient means no depth cue, whatever the albedo says. */
            float kdx = verts[i].x - fr.lx, kdy = verts[i].y - fr.ly, kdz = verts[i].z - fr.lz;
            float kd2 = kdx*kdx + kdy*kdy + kdz*kdz;
            float kfall = 1.0f / (1.0f + kd2*0.0022f);
            float key = 0.95f*ndl*kfall;        /* the sun: shadowed per pixel */
            /* Ambient MULTIPLIES albedo. It used to add a warm constant (+26/+14/+7 per
               fill-light) which is what made every material converge on the same beige:
               a blue wall, a green orc and a white floor all drifted toward clay. A
               lighting term that adds light instead of scaling reflectance destroys
               saturation, and no amount of texture fixes it downstream. */
            vc[i].sh[0] = verts[i].r * (s + 0.10f*ndf);
            vc[i].sh[1] = verts[i].g * (s + 0.10f*ndf);
            vc[i].sh[2] = verts[i].b * (s + 0.10f*ndf);
            vc[i].kd[0] = verts[i].r*key;
            vc[i].kd[1] = verts[i].g*key;
            vc[i].kd[2] = verts[i].b*key;
            vc[i].n[0] = nl[0]; vc[i].n[1] = nl[1]; vc[i].n[2] = nl[2];
            vc[i].a = verts[i].a / 255.0f;
            vc[i].tag = verts[i].tag;
        }

        /* Opaque front-to-back. Shading is the expensive part, so paint the near shells of
           the scene first and let the z-test reject the far ones before they shade. A
           counting sort over 64 depth buckets (Jet calls them depth buckets) costs two
           passes over the list and no comparisons. Glass keeps submission order: weighted
           blended OIT is order independent, which is the whole point of it. */
        uint32_t *opaque_order = malloc(sizeof(uint32_t) * (nt ? nt : 1));
        uint32_t *glass_order  = malloc(sizeof(uint32_t) * (nt ? nt : 1));
        uint32_t n_opaque = 0, n_glass = 0;
        if (no_sort) {
            for (uint32_t i = 0; i < nt; i++) {
                const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
                if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) glass_order[n_glass++] = i;
                else opaque_order[n_opaque++] = i;
            }
        } else if (opaque_order && glass_order) {
            float zmin = 1e30f, zmax = -1e30f;
            for (uint32_t i = 0; i < nt; i++) {
                const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
                if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) { n_glass++; continue; }
                float z = fminf(vc[tris[i].a].vz, fminf(vc[tris[i].b].vz, vc[tris[i].c].vz));
                if (z < zmin) zmin = z;
                if (z > zmax) zmax = z;
            }
            enum { NB = 64 };
            uint32_t counts[NB]; memset(counts, 0, sizeof counts);
            uint32_t n_o = nt - n_glass;
            float span = (zmax > zmin) ? (zmax - zmin) : 1.0f;
            for (uint32_t i = 0; i < nt; i++) {
                const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
                if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) { glass_order[n_glass++] = i; continue; }
                float z = fminf(vc[tris[i].a].vz, fminf(vc[tris[i].b].vz, vc[tris[i].c].vz));
                int b = (int)((z - zmin) / span * (NB - 1));
                if (b < 0) b = 0; if (b >= NB) b = NB - 1;
                counts[b]++;
            }
            uint32_t start[NB], sum = 0;
            for (int b = 0; b < NB; b++) { start[b] = sum; sum += counts[b]; }
            n_opaque = n_o;
            for (uint32_t i = 0; i < nt; i++) {
                const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
                if (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250) continue;
                float z = fminf(vc[tris[i].a].vz, fminf(vc[tris[i].b].vz, vc[tris[i].c].vz));
                int b = (int)((z - zmin) / span * (NB - 1));
                if (b < 0) b = 0; if (b >= NB) b = NB - 1;
                opaque_order[start[b]++] = i;
            }
        } else {
            n_opaque = n_glass = 0;   /* malloc failed: nothing draws, which is loud */
        }

        /* two passes over the same list: opaque, near to far, then glass. */
        for (int pass = 0; pass < 2; pass++) {
            int transparent = pass;
            const uint32_t n_this = transparent ? n_glass : n_opaque;
            const uint32_t *order = transparent ? glass_order : opaque_order;
            for (uint32_t oi = 0; oi < n_this; oi++) {
                const uint32_t i = order[oi];
                const Vert *V[3] = { &verts[tris[i].a], &verts[tris[i].b], &verts[tris[i].c] };
                int is_glass = (V[0]->a < 250 || V[1]->a < 250 || V[2]->a < 250);
                if (is_glass != transparent) continue;
                if (is_glass) glass_tris++;

                const CVert in[3] = { vc[tris[i].a], vc[tris[i].b], vc[tris[i].c] };
                if (in[0].vz < NEAR_Z && in[1].vz < NEAR_Z && in[2].vz < NEAR_Z) continue;

                if (!ctx.no_cull && !transparent &&
                    in[0].vz >= NEAR_Z && in[1].vz >= NEAR_Z && in[2].vz >= NEAR_Z) {
                    float near_z = fminf(in[0].vz, fminf(in[1].vz, in[2].vz));
                    float bx0 = 1e9f, bx1 = -1e9f, by0 = 1e9f, by1 = -1e9f;
                    for (int k = 0; k < 3; k++) {
                        float sxk = ctx.cx + fr.jitter_x + ctx.focal * in[k].vx / in[k].vz;
                        float syk = ctx.cy + fr.jitter_y - ctx.focal * in[k].vy / in[k].vz;
                        if (sxk < bx0) bx0 = sxk; if (sxk > bx1) bx1 = sxk;
                        if (syk < by0) by0 = syk; if (syk > by1) by1 = syk;
                    }
                    int rx0 = (int)(bx0 * ctx.cw / (float)w) / 32, rx1 = (int)(bx1 * ctx.cw / (float)w) / 32;
                    int ry0 = (int)(by0 * ctx.ch / (float)h) / 32, ry1 = (int)(by1 * ctx.ch / (float)h) / 32;
                    if (rx0 < 0) rx0 = 0; if (ry0 < 0) ry0 = 0;
                    if (rx1 >= (int)ctx.nrx) rx1 = (int)ctx.nrx - 1;
                    if (ry1 >= (int)ctx.nry) ry1 = (int)ctx.nry - 1;
                    float hidden_below = -1.0f;
                    for (int ry = ry0; ry <= ry1; ry++)
                        for (int rx = rx0; rx <= rx1; rx++) {
                            float m = ctx.region_max[(size_t)ry*ctx.nrx + rx];
                            if (m < 0.0f) { hidden_below = -1.0f; ry = ry1 + 1; break; }
                            if (m > hidden_below) hidden_below = m;
                        }
                    if (hidden_below > 0.0f && near_z > hidden_below * 1.02f) { ctx.culled++; continue; }
                }

                CVert poly[4];
                int np = clip_near(in, poly);
                if (np < 3) continue;
                for (int k = 1; k + 1 < np; k++)
                    raster_tri(&ctx, &poly[0], &poly[k], &poly[k+1], transparent);
            }
        }

        if (!no_oit) {
            for (size_t i = 0; i < (size_t)w*h; i++) {
                float rv = ctx.rev[i];
                if (rv >= 0.999f) continue;
                float aw = ctx.acc[i*4+3];
                if (aw <= 1e-6f) continue;
                uint8_t *out = ctx.fb + 3*i;
                for (int k = 0; k < 3; k++) {
                    float avg = ctx.acc[i*4+k] / aw;
                    out[k] = (uint8_t)fminf(255.0f, avg * (1.0f - rv) + out[k] * rv);
                }
            }
        }

        char path[1024];
        snprintf(path,sizeof path,"%scol_%04u.ppm",prefix,f);
        FILE *o=fopen(path,"wb"); if(!o){fprintf(stderr,"wuburaster: write fail\n");return 1;}
        fprintf(o,"P6\n%u %u\n255\n",w,h); fwrite(ctx.fb,3,(size_t)w*h,o); fclose(o);

        uint32_t w2 = w/2 ? w/2 : 1, h2 = h/2 ? h/2 : 1;
        float *dep2 = malloc(sizeof(float)*(size_t)w2*h2);
        float *nrm2 = malloc(sizeof(float)*3*(size_t)w2*h2);
        if (!dep2||!nrm2) return 1;
        for (uint32_t y=0;y<h2;y++)
            for (uint32_t x=0;x<w2;x++){
                size_t si=(size_t)(y*2)*w + (x*2), di=(size_t)y*w2 + x;
                dep2[di]=ctx.depth[si];
                nrm2[di*3]=ctx.nrmbuf[si*3];
                nrm2[di*3+1]=ctx.nrmbuf[si*3+1];
                nrm2[di*3+2]=ctx.nrmbuf[si*3+2];
            }

        snprintf(path,sizeof path,"%sdep_%04u.bin",prefix,f);
        o=fopen(path,"wb"); if(!o) return 1;
        int32_t bx0 = ctx.sb_maxx >= 0 ? ctx.sb_minx/2 : -1;
        int32_t by0 = ctx.sb_maxy >= 0 ? ctx.sb_miny/2 : -1;
        int32_t bx1 = ctx.sb_maxx >= 0 ? ctx.sb_maxx/2 : -1;
        int32_t by1 = ctx.sb_maxy >= 0 ? ctx.sb_maxy/2 : -1;
        fwrite(&w2,4,1,o); fwrite(&h2,4,1,o);
        fwrite(&bx0,4,1,o); fwrite(&by0,4,1,o); fwrite(&bx1,4,1,o); fwrite(&by1,4,1,o);
        fwrite(dep2,4,(size_t)w2*h2,o); fclose(o);

        snprintf(path,sizeof path,"%snrm_%04u.bin",prefix,f);
        o=fopen(path,"wb"); if(!o) return 1;
        fwrite(&w2,4,1,o); fwrite(&h2,4,1,o); fwrite(nrm2,4,3*(size_t)w2*h2,o); fclose(o);

        /* Publish the camera with the frame. Depth alone lets a post pass fake occlusion;
           depth plus the eye basis lets it unproject to world space and do the real thing,
           which is what any screen-space effect needs (AO now, reflections later). */
        snprintf(path,sizeof path,"%scam_%04u.bin",prefix,f);
        o=fopen(path,"wb"); if(!o) return 1;
        float camdata[16] = { ctx.eye[0], ctx.eye[1], ctx.eye[2],
                              ctx.right[0], ctx.right[1], ctx.right[2],
                              ctx.up[0], ctx.up[1], ctx.up[2],
                              ctx.fwd[0], ctx.fwd[1], ctx.fwd[2],
                              ctx.focal, (float)w2, (float)h2, 0.0f };
        fwrite(&w2,4,1,o); fwrite(&h2,4,1,o); fwrite(camdata,4,16,o); fclose(o);
        free(dep2); free(nrm2);

        free(vc); free(opaque_order); free(glass_order); free(verts); free(tris); free(vn);
    }

    clock_gettime(CLOCK_MONOTONIC,&t1);
    double ms=(t1.tv_sec-t0.tv_sec)*1e3+(t1.tv_nsec-t0.tv_nsec)/1e6;
    fprintf(stderr,"wuburaster: %u frames, %.0f tris/frame (%u glass, %u occlusion-culled), "
                   "%.1f ms total, %.2f ms/frame, shadow %.2f ms/frame%s%s%s\n",
            nf, (double)total_tris/(nf?nf:1), glass_tris, ctx.culled,
            ms, ms/(nf?nf:1), (double)shadow_ns/1e6/(nf?nf:1),
            no_oit ? " [no-oit]" : "", no_cull ? " [no-cull]" : "",
            no_shadow ? " [no-shadow]" : "");
    if (getenv("WUBU_DEBUG_SHADOW"))
        fprintf(stderr, "debug: frag %ld, in-map %ld, shadowed %ld\n", dbg_frag, dbg_hit, dbg_shadowed);
    return 0;
}
