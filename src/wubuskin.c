// wubuskin — C11 character animation core for wuBu3D.
//
// Python is the scripting layer: it loads meshes, builds casts, writes files. Everything that runs
// per-vertex per-frame lives here, because it is the only part where the language choice matters:
// a 1000-character cast at 60 fps is ~10^8 vertex-blends per second, and CPython spends longer
// unpacking arguments than doing the arithmetic.
//
// SLERM note: the algorithms are public and cited, the code is ours.
//   bone transform            rigid transform between two segments (axis-angle form)
//   linear blend skinning     Magnenat-Thalmann et al. 1988 — the baseline every engine still ships
//   dual quaternion skinning  Kavan, Collins, O'Sullivan & Zara, "Dual Quaternions for Rigid
//                             Transformation Blending", TCD-CS-2006-46 / I3D 2007
//   bone heat weights         Baran & Popović, "Automatic Rigging and Animation of 3D Characters",
//                             SIGGRAPH 2007 — weights diffuse over the mesh, not through space
//
// Build:  cc -O2 -std=c11 -shared -fPIC -o libwubuskin.so wubuskin.c -lm
// Test:   python3 tests/test_c11_skin.py
//
// All arrays are float32, row-major, and caller-allocated. Nothing here allocates except wb_heat,
// which takes a caller-supplied scratch buffer for the same reason.

#include <math.h>
#include <stddef.h>
#include <string.h>

#define WB_MAX_INFLUENCES 4

// ---------------------------------------------------------------- vectors

static inline void v3_sub(const float *a, const float *b, float *o) {
    o[0] = a[0] - b[0]; o[1] = a[1] - b[1]; o[2] = a[2] - b[2];
}
static inline float v3_dot(const float *a, const float *b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
static inline void v3_cross(const float *a, const float *b, float *o) {
    float x = a[1] * b[2] - a[2] * b[1];
    float y = a[2] * b[0] - a[0] * b[2];
    float z = a[0] * b[1] - a[1] * b[0];
    o[0] = x; o[1] = y; o[2] = z;
}
static inline float v3_len(const float *a) { return sqrtf(v3_dot(a, a)); }
static inline int v3_norm(float *a) {
    float L = v3_len(a);
    if (L < 1e-12f) return 0;
    a[0] /= L; a[1] /= L; a[2] /= L;
    return 1;
}
static inline float v3_dist(const float *a, const float *b) {
    float d[3]; v3_sub(a, b, d); return v3_len(d);
}

// Distance from p to the segment a-b, and the nearest point on it.
static inline float seg_dist(const float *p, const float *a, const float *b, float *near) {
    float ab[3], ap[3];
    v3_sub(b, a, ab);
    v3_sub(p, a, ap);
    float L2 = v3_dot(ab, ab);
    float t = (L2 < 1e-12f) ? 0.0f : v3_dot(ap, ab) / L2;
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;
    if (near) { near[0] = a[0] + ab[0] * t; near[1] = a[1] + ab[1] * t; near[2] = a[2] + ab[2] * t; }
    float d[3];
    d[0] = p[0] - (a[0] + ab[0] * t);
    d[1] = p[1] - (a[1] + ab[1] * t);
    d[2] = p[2] - (a[2] + ab[2] * t);
    return v3_len(d);
}

// ---------------------------------------------------------------- matrices (row-major 4x4)

static inline void m4_identity(float *m) {
    memset(m, 0, 16 * sizeof(float));
    m[0] = m[5] = m[10] = m[15] = 1.0f;
}

// out = a * b  (a applies first)
void wb_mat4_mul(const float *a, const float *b, float *out) {
    float t[16];
    for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++) {
            float s = 0.0f;
            for (int k = 0; k < 4; k++) s += a[r * 4 + k] * b[k * 4 + c];
            t[r * 4 + c] = s;
        }
    memcpy(out, t, sizeof(t));
}

static inline void m4_point(const float *m, const float *p, float *o) {
    o[0] = m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3];
    o[1] = m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7];
    o[2] = m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11];
}

// The rigid transform taking the rest segment to the posed segment.
// Rotation is the axis-angle form: axis = a x b, angle from a . b. Translation then makes the
// rest head land on the posed head. One bone, no hierarchy — the caller composes the chain.
void wb_bone_matrix(const float *ra, const float *rb, const float *pa, const float *pb,
                    float *out) {
    float a[3], b[3], axis[3];
    v3_sub(rb, ra, a);
    v3_sub(pb, pa, b);
    if (!v3_norm(a) || !v3_norm(b)) { m4_identity(out); return; }
    v3_cross(a, b, axis);
    float c = v3_dot(a, b);
    float s = v3_len(axis);
    float R[9];
    if (s < 1e-9f) {
        if (c > 0.0f) { R[0] = 1; R[1] = 0; R[2] = 0; R[3] = 0; R[4] = 1; R[5] = 0; R[6] = 0; R[7] = 0; R[8] = 1; }
        else { R[0] = -1; R[1] = 0; R[2] = 0; R[3] = 0; R[4] = -1; R[5] = 0; R[6] = 0; R[7] = 0; R[8] = -1; }
    } else {
        v3_norm(axis);
        float th = atan2f(s, c);
        float ct = cosf(th), st = sinf(th), vt = 1.0f - ct;
        float x = axis[0], y = axis[1], z = axis[2];
        R[0] = ct + x * x * vt;      R[1] = x * y * vt - z * st;  R[2] = x * z * vt + y * st;
        R[3] = y * x * vt + z * st;  R[4] = ct + y * y * vt;      R[5] = y * z * vt - x * st;
        R[6] = z * x * vt - y * st;  R[7] = z * y * vt + x * st;  R[8] = ct + z * z * vt;
    }
    m4_identity(out);
    out[0] = R[0]; out[1] = R[1]; out[2] = R[2];
    out[4] = R[3]; out[5] = R[4]; out[6] = R[5];
    out[8] = R[6]; out[9] = R[7]; out[10] = R[8];
    out[3] = pa[0] - (R[0] * ra[0] + R[1] * ra[1] + R[2] * ra[2]);
    out[7] = pa[1] - (R[3] * ra[0] + R[4] * ra[1] + R[5] * ra[2]);
    out[11] = pa[2] - (R[6] * ra[0] + R[7] * ra[1] + R[8] * ra[2]);
}

// ---------------------------------------------------------------- linear blend skinning

// pos: n*3, W: n*bones (rows already normalised), mats: bones*16, out: n*3
void wb_lbs(const float *pos, const float *W, int n, int bones, const float *mats, float *out) {
    for (int i = 0; i < n; i++) {
        const float *p = pos + i * 3;
        const float *w = W + (size_t)i * bones;
        float acc[3] = {0.0f, 0.0f, 0.0f};
        for (int k = 0; k < bones; k++) {
            float wk = w[k];
            if (wk <= 1e-7f) continue;
            const float *m = mats + k * 16;
            acc[0] += wk * (m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3]);
            acc[1] += wk * (m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7]);
            acc[2] += wk * (m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11]);
        }
        out[i * 3 + 0] = acc[0];
        out[i * 3 + 1] = acc[1];
        out[i * 3 + 2] = acc[2];
    }
}

// ---------------------------------------------------------------- dual quaternions

typedef struct { float r[4]; float d[4]; } wb_dq;   // r = rotation, d = dual part

static inline void q_mul(const float *a, const float *b, float *o) {
    float x = a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1];
    float y = a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0];
    float z = a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3];
    float w = a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2];
    o[0] = x; o[1] = y; o[2] = z; o[3] = w;
}
static inline void q_conj(const float *q, float *o) { o[0] = -q[0]; o[1] = -q[1]; o[2] = -q[2]; o[3] = q[3]; }

// Rotation quaternion from the 3x3 part of a 4x4, Shepperd's method.
static void m4_to_quat(const float *m, float *q) {
    float m00 = m[0], m01 = m[1], m02 = m[2];
    float m10 = m[4], m11 = m[5], m12 = m[6];
    float m20 = m[8], m21 = m[9], m22 = m[10];
    float tr = m00 + m11 + m22;
    if (tr > 0.0f) {
        float s = sqrtf(tr + 1.0f) * 2.0f;
        q[0] = (m21 - m12) / s; q[1] = (m02 - m20) / s; q[2] = (m10 - m01) / s; q[3] = 0.25f * s;
    } else if (m00 > m11 && m00 > m22) {
        float s = sqrtf(1.0f + m00 - m11 - m22) * 2.0f;
        q[0] = 0.25f * s; q[1] = (m01 + m10) / s; q[2] = (m02 + m20) / s; q[3] = (m21 - m12) / s;
    } else if (m11 > m22) {
        float s = sqrtf(1.0f + m11 - m00 - m22) * 2.0f;
        q[0] = (m01 + m10) / s; q[1] = 0.25f * s; q[2] = (m12 + m21) / s; q[3] = (m02 - m20) / s;
    } else {
        float s = sqrtf(1.0f + m22 - m00 - m11) * 2.0f;
        q[0] = (m02 + m20) / s; q[1] = (m12 + m21) / s; q[2] = 0.25f * s; q[3] = (m10 - m01) / s;
    }
    float L = sqrtf(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
    if (L > 1e-12f) { q[0] /= L; q[1] /= L; q[2] /= L; q[3] /= L; }
}

static void m4_to_dq(const float *m, wb_dq *dq) {
    m4_to_quat(m, dq->r);
    float t[4] = {m[3], m[7], m[11], 0.0f};
    q_mul(t, dq->r, dq->d);
    for (int i = 0; i < 4; i++) dq->d[i] *= 0.5f;
}

static void dq_transform(const wb_dq *dq, const float *p, float *o) {
    float q[4] = {dq->r[0], dq->r[1], dq->r[2], dq->r[3]};
    float cq[4]; q_conj(q, cq);
    float v[4] = {p[0], p[1], p[2], 0.0f};
    float t1[4], rot[4];
    q_mul(q, v, t1);
    q_mul(t1, cq, rot);
    float tq[4];
    q_mul(dq->d, cq, tq);
    o[0] = rot[0] + 2.0f * tq[0];
    o[1] = rot[1] + 2.0f * tq[1];
    o[2] = rot[2] + 2.0f * tq[2];
}

// DLB: weighted sum with antipodal correction, then renormalise both parts by |real|.
static void dq_blend(const wb_dq *dqs, const float *w, int k, wb_dq *out) {
    float ar[4] = {0, 0, 0, 0}, ad[4] = {0, 0, 0, 0};
    const float *ref = NULL;
    for (int i = 0; i < k; i++) {
        if (w[i] <= 1e-7f) continue;
        if (!ref) ref = dqs[i].r;
        // a quaternion and its negation are the same rotation; blending without choosing a
        // hemisphere takes the long way round and turns the surface inside out
        float dot = 0.0f;
        for (int j = 0; j < 4; j++) dot += dqs[i].r[j] * ref[j];
        float s = (dot < 0.0f) ? -1.0f : 1.0f;
        for (int j = 0; j < 4; j++) {
            ar[j] += s * w[i] * dqs[i].r[j];
            ad[j] += s * w[i] * dqs[i].d[j];
        }
    }
    float L = sqrtf(ar[0] * ar[0] + ar[1] * ar[1] + ar[2] * ar[2] + ar[3] * ar[3]);
    if (L < 1e-12f) L = 1.0f;
    for (int j = 0; j < 4; j++) { out->r[j] = ar[j] / L; out->d[j] = ad[j] / L; }
}

void wb_dqs(const float *pos, const float *W, int n, int bones, const float *mats, float *out) {
    wb_dq dqs[64];
    int nb = bones > 64 ? 64 : bones;
    for (int k = 0; k < nb; k++) m4_to_dq(mats + k * 16, &dqs[k]);
    for (int i = 0; i < n; i++) {
        const float *w = W + (size_t)i * bones;
        wb_dq b;
        dq_blend(dqs, w, nb, &b);
        dq_transform(&b, pos + i * 3, out + i * 3);
    }
}

// ---------------------------------------------------------------- heat weights

// Baran & Popović: weights diffuse along mesh edges with Dirichlet seeds, so influence follows the
// surface. A vertex is seeded for the bone that clearly owns it (less than 60% as far as any
// other); everything else is solved. Seeding by radius alone fixed every vertex and left the
// diffusion nothing to do.
//
// scratch: 3*n floats (two weight buffers + the fixed mask as 0/1 stored separately)
// Returns 0 on success.
static inline int fixed_kind(int i, const int *owner, const float *d1, const float *d2,
                              int b, float diag, float rel) {
    float dn = d1[i] <= diag * rel && d1[i] <= 0.6f * (d2[i] > 1e-6f ? d2[i] : 1e-6f);
    if (!dn) return 0;
    return owner[i] == b ? 1 : 2;
}

int wb_heat(const float *verts, int n, const int *edges, int m,
            const float *heads, const float *tails, int bones,
            int iterations, float rel, float *out, float *scratch, int *owner) {
    if (n <= 0 || bones <= 0 || bones > 64) return 1;
    float *cur = scratch;              // n
    float *nxt = scratch + n;          // n
    float *d1 = scratch + 2 * n;       // n
    float *d2 = scratch + 3 * n;       // n

    float lo[3] = {1e30f, 1e30f, 1e30f}, hi[3] = {-1e30f, -1e30f, -1e30f};
    for (int i = 0; i < n; i++)
        for (int k = 0; k < 3; k++) {
            float v = verts[i * 3 + k];
            if (v < lo[k]) lo[k] = v;
            if (v > hi[k]) hi[k] = v;
        }
    float diag = v3_dist(lo, hi);
    if (diag < 1e-9f) diag = 1.0f;

    for (int i = 0; i < n; i++) {
        const float *p = verts + i * 3;
        float best = 1e30f, second = 1e30f;
        int bi = 0;
        for (int k = 0; k < bones; k++) {
            float d = seg_dist(p, heads + k * 3, tails + k * 3, NULL);
            if (d < best) { second = best; best = d; bi = k; }
            else if (d < second) second = d;
        }
        owner[i] = bi; d1[i] = best; d2[i] = second;
    }

    // seed kind per vertex per bone, recomputed in place: 1 = held at one, 2 = held at zero,
    // 0 = free. Storing it cost an extra buffer and the predicate is three comparisons.
    for (int b = 0; b < bones; b++) {
        for (int i = 0; i < n; i++) {
            float dn = d1[i] <= diag * rel && d1[i] <= 0.6f * (d2[i] > 1e-6f ? d2[i] : 1e-6f);
            cur[i] = !dn ? 0.5f : (owner[i] == b ? 1.0f : 0.0f);
        }
        for (int it = 0; it < iterations; it++) {
            memcpy(nxt, cur, (size_t)n * sizeof(float));
            for (int e = 0; e < m; e++) {
                int a = edges[e * 2], c = edges[e * 2 + 1];
                if (fixed_kind(a, owner, d1, d2, b, diag, rel) == 0)
                    cur[a] = 0.5f * (cur[a] + nxt[c]);
                if (fixed_kind(c, owner, d1, d2, b, diag, rel) == 0)
                    cur[c] = 0.5f * (cur[c] + nxt[a]);
            }
        }
        for (int i = 0; i < n; i++) out[(size_t)i * bones + b] = cur[i];
    }

    for (int i = 0; i < n; i++) {
        float *row = out + (size_t)i * bones;
        float s = 0.0f;
        for (int k = 0; k < bones; k++) { if (row[k] < 0.0f) row[k] = 0.0f; s += row[k]; }
        if (s < 1e-9f) { for (int k = 0; k < bones; k++) row[k] = 0.0f; row[owner[i]] = 1.0f; continue; }
        for (int k = 0; k < bones; k++) row[k] /= s;
        if (bones > WB_MAX_INFLUENCES) {
            for (int drop = 0; drop < bones - WB_MAX_INFLUENCES; drop++) {
                int mi = -1; float mv = 1e30f;
                for (int k = 0; k < bones; k++) if (row[k] > 0.0f && row[k] < mv) { mv = row[k]; mi = k; }
                if (mi >= 0) row[mi] = 0.0f;
            }
            s = 0.0f;
            for (int k = 0; k < bones; k++) s += row[k];
            if (s > 1e-9f) for (int k = 0; k < bones; k++) row[k] /= s;
        }
    }
    return 0;
}

// scratch buffer (floats) and owner buffer (ints) the caller must supply to wb_heat
int wb_heat_scratch_floats(int n) { return 4 * n; }
