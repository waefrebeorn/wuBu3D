// wubumesh — C11 mesh core: welding, crease-angle normals, QEM decimation.
//
// Python scripts load and author meshes; this does the per-face, per-edge work that runs over
// thousands of them.
//
// SLERM note — algorithms cited, code ours:
//   quadric error metrics   Garland & Heckbert, "Surface Simplification Using Quadric Error
//                           Metrics", SIGGRAPH 1997. Each vertex carries the summed quadric of its
//                           incident planes; collapsing an edge costs v^T (Qa+Qb) v, so the
//                           cheapest collapse disturbs the surface least.
//   crease normals          Blender's shade-smooth-by-angle: an edge whose faces differ by more
//                           than the crease angle keeps a hard split, so one position can carry
//                           two normals.
//   welding                 meshoptimizer builds on the same hash-and-merge step; a quad soup has
//                           four vertices per corner and no adjacency at all without it.
//
// Adjacency is built ONCE (counting sort into CSR) and maintained through a per-vertex ring of
// faces. The first version of this file scanned every face per candidate edge, which is O(F*E) —
// minutes on a 5k-triangle mesh. Rings make each collapse O(degree).
//
// Build: cc -O2 -std=c11 -shared -fPIC -o libwubumesh.so wubumesh.c -lm

#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define DEAD 0xFFFFFFFFu

// ---------------------------------------------------------------- welding

// Merge vertices rounding to the same cell. remap[n] out, unique positions to out_pos. Returns the
// number of unique vertices, or -1 on allocation failure.
int wb_weld(const float *pos, int n, float cell, uint32_t *remap, float *out_pos) {
    if (cell <= 0.0f) cell = 1e-5f;
    int cap = 1;
    while (cap < n * 2 + 8) cap <<= 1;
    uint32_t *table = (uint32_t *)malloc((size_t)cap * sizeof(uint32_t));
    if (!table) return -1;
    for (int i = 0; i < cap; i++) table[i] = DEAD;
    int uniq = 0;
    for (int i = 0; i < n; i++) {
        int64_t qx = (int64_t)llroundf(pos[i * 3 + 0] / cell);
        int64_t qy = (int64_t)llroundf(pos[i * 3 + 1] / cell);
        int64_t qz = (int64_t)llroundf(pos[i * 3 + 2] / cell);
        uint64_t h = (uint64_t)(qx * 73856093LL) ^ (uint64_t)(qy * 19349663LL) ^
                     (uint64_t)(qz * 83492791LL);
        uint32_t slot = (uint32_t)(h & (uint64_t)(cap - 1));
        for (;;) {
            uint32_t j = table[slot];
            if (j == DEAD) {
                table[slot] = (uint32_t)uniq;
                if (out_pos) {
                    out_pos[uniq * 3 + 0] = pos[i * 3 + 0];
                    out_pos[uniq * 3 + 1] = pos[i * 3 + 1];
                    out_pos[uniq * 3 + 2] = pos[i * 3 + 2];
                }
                remap[i] = (uint32_t)uniq;
                uniq++;
                break;
            }
            const float *p = out_pos ? out_pos + (size_t)j * 3 : pos + (size_t)j * 3;
            if ((int64_t)llroundf(p[0] / cell) == qx &&
                (int64_t)llroundf(p[1] / cell) == qy &&
                (int64_t)llroundf(p[2] / cell) == qz) {
                remap[i] = j;
                break;
            }
            slot = (slot + 1) & (uint32_t)(cap - 1);
        }
    }
    free(table);
    return uniq;
}

// ---------------------------------------------------------------- adjacency

// CSR: vertices -> incident faces. Caller frees *start and *list.
static int build_adjacency(const uint32_t *tri, int faces, int nverts, int **start, int **list) {
    int *cnt = (int *)calloc((size_t)nverts + 1, sizeof(int));
    if (!cnt) return 1;
    for (int f = 0; f < faces; f++)
        for (int k = 0; k < 3; k++) {
            uint32_t v = tri[f * 3 + k];
            if (v < (uint32_t)nverts) cnt[v + 1]++;
        }
    for (int i = 1; i <= nverts; i++) cnt[i] += cnt[i - 1];
    int *lst = (int *)malloc((size_t)cnt[nverts] * sizeof(int) + sizeof(int));
    if (!lst) { free(cnt); return 1; }
    int *fill = (int *)calloc((size_t)nverts, sizeof(int));
    if (!fill) { free(cnt); free(lst); return 1; }
    for (int f = 0; f < faces; f++)
        for (int k = 0; k < 3; k++) {
            uint32_t v = tri[f * 3 + k];
            if (v < (uint32_t)nverts) lst[cnt[v] + fill[v]++] = f;
        }
    free(fill);
    *start = cnt;
    *list = lst;
    return 0;
}

// ---------------------------------------------------------------- normals

void wb_face_normals(const float *pos, const uint32_t *tri, int faces, float *fn) {
    for (int f = 0; f < faces; f++) {
        const float *a = pos + (size_t)tri[f * 3 + 0] * 3;
        const float *b = pos + (size_t)tri[f * 3 + 1] * 3;
        const float *c = pos + (size_t)tri[f * 3 + 2] * 3;
        float e1[3] = {b[0] - a[0], b[1] - a[1], b[2] - a[2]};
        float e2[3] = {c[0] - a[0], c[1] - a[1], c[2] - a[2]};
        // left unnormalised: |a x b| is twice the area, which is the weighting a smooth normal
        // wants anyway
        fn[f * 3 + 0] = e1[1] * e2[2] - e1[2] * e2[1];
        fn[f * 3 + 1] = e1[2] * e2[0] - e1[0] * e2[2];
        fn[f * 3 + 2] = e1[0] * e2[1] - e1[1] * e2[0];
    }
}

// One normal per face corner (faces*3*3 out), splitting at creases above `cos_threshold`.
void wb_corner_normals(const float *pos, const uint32_t *tri, int faces, int nverts,
                       float cos_threshold, float *out) {
    int *start = NULL, *list = NULL;
    if (build_adjacency(tri, faces, nverts, &start, &list)) return;
    float *fn = (float *)malloc((size_t)faces * 3 * sizeof(float));
    if (!fn) { free(start); free(list); return; }
    wb_face_normals(pos, tri, faces, fn);

    for (int f = 0; f < faces; f++) {
        const float *nf = fn + f * 3;
        float lf = sqrtf(nf[0] * nf[0] + nf[1] * nf[1] + nf[2] * nf[2]);
        float uf[3] = {0.0f, 0.0f, 0.0f};
        if (lf > 1e-12f) { uf[0] = nf[0] / lf; uf[1] = nf[1] / lf; uf[2] = nf[2] / lf; }
        for (int k = 0; k < 3; k++) {
            uint32_t v = tri[f * 3 + k];
            float acc[3] = {0.0f, 0.0f, 0.0f};
            if (v < (uint32_t)nverts) {
                for (int a = start[v]; a < start[v + 1]; a++) {
                    const float *ng = fn + (size_t)list[a] * 3;
                    float lg = sqrtf(ng[0] * ng[0] + ng[1] * ng[1] + ng[2] * ng[2]);
                    if (lg < 1e-12f) continue;
                    float d = (ng[0] * uf[0] + ng[1] * uf[1] + ng[2] * uf[2]) / lg;
                    if (d < cos_threshold) continue;   // a crease: do not blend across it
                    acc[0] += ng[0]; acc[1] += ng[1]; acc[2] += ng[2];
                }
            }
            float L = sqrtf(acc[0] * acc[0] + acc[1] * acc[1] + acc[2] * acc[2]);
            float *o = out + ((size_t)f * 3 + k) * 3;
            if (L > 1e-12f) { o[0] = acc[0] / L; o[1] = acc[1] / L; o[2] = acc[2] / L; }
            else { o[0] = uf[0]; o[1] = uf[1]; o[2] = uf[2]; }
        }
    }
    free(fn); free(start); free(list);
}

// ---------------------------------------------------------------- QEM

typedef struct { double q[10]; } quadric;

static void quad_from_plane(quadric *o, double a, double b, double c, double d) {
    o->q[0] = a * a; o->q[1] = a * b; o->q[2] = a * c; o->q[3] = a * d;
    o->q[4] = b * b; o->q[5] = b * c; o->q[6] = b * d;
    o->q[7] = c * c; o->q[8] = c * d;
    o->q[9] = d * d;
}
static void quad_add(quadric *dst, const quadric *src) {
    for (int i = 0; i < 10; i++) dst->q[i] += src->q[i];
}
static double quad_err(const quadric *Q, double x, double y, double z) {
    const double *q = Q->q;
    double e = q[0] * x * x + 2 * q[1] * x * y + 2 * q[2] * x * z + 2 * q[3] * x
             + q[4] * y * y + 2 * q[5] * y * z + 2 * q[6] * y
             + q[7] * z * z + 2 * q[8] * z + q[9];
    return e < 0.0 ? 0.0 : e;
}
static void quad_best(const quadric *Q, const double *pa, const double *pb, double *out, double *err) {
    double best = 1e300;
    double c[3][3] = {{pa[0], pa[1], pa[2]}, {pb[0], pb[1], pb[2]},
                      {(pa[0] + pb[0]) * 0.5, (pa[1] + pb[1]) * 0.5, (pa[2] + pb[2]) * 0.5}};
    for (int i = 0; i < 3; i++) {
        double e = quad_err(Q, c[i][0], c[i][1], c[i][2]);
        if (e < best) { best = e; out[0] = c[i][0]; out[1] = c[i][1]; out[2] = c[i][2]; }
    }
    *err = best;
}

typedef struct { double err; int a, b; } edge_t;
static int cmp_edge(const void *A, const void *B) {
    double a = ((const edge_t *)A)->err, b = ((const edge_t *)B)->err;
    return (a < b) ? -1 : (a > b) ? 1 : 0;
}

// Decimate to at most target_faces. pos is updated in place (vertices move when collapsed).
// Returns the resulting face count through *faces_out; -1 on allocation failure.
int wb_qem_simplify(float *pos, const uint32_t *tri_in, int faces_in, uint32_t *tri_out,
                    int *faces_out, int target_faces, int nverts) {
    *faces_out = 0;
    uint32_t *tri = (uint32_t *)malloc((size_t)faces_in * 3 * sizeof(uint32_t));
    quadric *Q = (quadric *)calloc((size_t)nverts, sizeof(quadric));
    unsigned char *alive = (unsigned char *)malloc((size_t)nverts);
    if (!tri || !Q || !alive) { free(tri); free(Q); free(alive); return -1; }
    memcpy(tri, tri_in, (size_t)faces_in * 3 * sizeof(uint32_t));
    memset(alive, 1, (size_t)nverts);

    // area-weighted plane quadrics
    for (int f = 0; f < faces_in; f++) {
        const float *a = pos + (size_t)tri[f * 3 + 0] * 3;
        const float *b = pos + (size_t)tri[f * 3 + 1] * 3;
        const float *c = pos + (size_t)tri[f * 3 + 2] * 3;
        double e1[3] = {b[0] - a[0], b[1] - a[1], b[2] - a[2]};
        double e2[3] = {c[0] - a[0], c[1] - a[1], c[2] - a[2]};
        double nx = e1[1] * e2[2] - e1[2] * e2[1];
        double ny = e1[2] * e2[0] - e1[0] * e2[2];
        double nz = e1[0] * e2[1] - e1[1] * e2[0];
        double L = sqrt(nx * nx + ny * ny + nz * nz);
        if (L < 1e-12) continue;
        nx /= L; ny /= L; nz /= L;
        double d = -(nx * a[0] + ny * a[1] + nz * a[2]);
        quadric fq;
        quad_from_plane(&fq, nx, ny, nz, d);
        for (int i = 0; i < 10; i++) fq.q[i] *= L;     // weight by 2*area
        for (int k = 0; k < 3; k++) quad_add(&Q[tri[f * 3 + k]], &fq);
    }

    // candidate edges
    size_t maxe = (size_t)faces_in * 3;
    edge_t *edges = (edge_t *)malloc(maxe * sizeof(edge_t));
    if (!edges) { free(tri); free(Q); free(alive); return -1; }
    size_t ne = 0;
    for (int f = 0; f < faces_in; f++)
        for (int k = 0; k < 3; k++) {
            uint32_t a = tri[f * 3 + k], b = tri[f * 3 + (k + 1) % 3];
            if (a == b) continue;
            if (a > b) { uint32_t t = a; a = b; b = t; }
            quadric qq = Q[a];
            quad_add(&qq, &Q[b]);
            double pa[3] = {pos[(size_t)a * 3], pos[(size_t)a * 3 + 1], pos[(size_t)a * 3 + 2]};
            double pb[3] = {pos[(size_t)b * 3], pos[(size_t)b * 3 + 1], pos[(size_t)b * 3 + 2]};
            double o[3], err;
            quad_best(&qq, pa, pb, o, &err);
            edges[ne].err = err; edges[ne].a = (int)a; edges[ne].b = (int)b;
            ne++;
        }
    qsort(edges, ne, sizeof(edge_t), cmp_edge);

    int live = faces_in;
    // per-vertex face lists. The face RING linked each face only under its first vertex, so most
    // vertices had an empty ring and every collapse was skipped as "shared == 0" — the first
    // version decimated 5120 triangles to 3804 and stopped.
    int **vfaces = (int **)calloc((size_t)nverts, sizeof(int *));
    int *vcount = (int *)calloc((size_t)nverts, sizeof(int));
    int *vcap = (int *)calloc((size_t)nverts, sizeof(int));
    if (!vfaces || !vcount || !vcap) {
        free(tri); free(Q); free(alive); free(edges); free(vfaces); free(vcount); free(vcap);
        return -1;
    }
    for (int f = 0; f < faces_in; f++)
        for (int k2 = 0; k2 < 3; k2++) {
            int v = (int)tri[f * 3 + k2];
            if (vcount[v] == vcap[v]) {
                int nc = vcap[v] ? vcap[v] * 2 : 8;
                int *nb = (int *)realloc(vfaces[v], (size_t)nc * sizeof(int));
                if (!nb) { live = -1; break; }
                vfaces[v] = nb; vcap[v] = nc;
            }
            vfaces[v][vcount[v]++] = f;
        }
    if (live < 0) {
        for (int v = 0; v < nverts; v++) free(vfaces[v]);
        free(tri); free(Q); free(alive); free(edges); free(vfaces); free(vcount); free(vcap);
        return -1;
    }

    for (size_t e = 0; e < ne && live > target_faces; e++) {
        int a = edges[e].a, b = edges[e].b;
        if (!alive[a] || !alive[b]) continue;

        int shared = 0;
        for (int i2 = 0; i2 < vcount[b]; i2++) {
            int f = vfaces[b][i2];
            if (tri[f * 3] == DEAD) continue;
            if (tri[f * 3] == (uint32_t)a || tri[f * 3 + 1] == (uint32_t)a || tri[f * 3 + 2] == (uint32_t)a)
                shared++;
        }
        if (shared < 1 || shared > 2) continue;

        quadric qq = Q[a];
        quad_add(&qq, &Q[b]);
        double pa[3] = {pos[(size_t)a * 3], pos[(size_t)a * 3 + 1], pos[(size_t)a * 3 + 2]};
        double pb[3] = {pos[(size_t)b * 3], pos[(size_t)b * 3 + 1], pos[(size_t)b * 3 + 2]};
        double np[3], err;
        quad_best(&qq, pa, pb, np, &err);

        int flip = 0;
        for (int i2 = 0; i2 < vcount[b] && !flip; i2++) {
            int f = vfaces[b][i2];
            if (tri[f * 3] == DEAD) continue;
            uint32_t i0 = tri[f * 3], i1 = tri[f * 3 + 1], i2v = tri[f * 3 + 2];
            float o[3][3];
            uint32_t ids[3] = {i0, i1, i2v};
            for (int c = 0; c < 3; c++) {
                o[c][0] = pos[(size_t)ids[c] * 3];
                o[c][1] = pos[(size_t)ids[c] * 3 + 1];
                o[c][2] = pos[(size_t)ids[c] * 3 + 2];
            }
            float e1[3] = {o[1][0] - o[0][0], o[1][1] - o[0][1], o[1][2] - o[0][2]};
            float e2[3] = {o[2][0] - o[0][0], o[2][1] - o[0][1], o[2][2] - o[0][2]};
            float on[3] = {e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2],
                           e1[0] * e2[1] - e1[1] * e2[0]};
            float q[3][3];
            for (int c = 0; c < 3; c++) {
                if (ids[c] == (uint32_t)b) { q[c][0] = (float)np[0]; q[c][1] = (float)np[1]; q[c][2] = (float)np[2]; }
                else { q[c][0] = o[c][0]; q[c][1] = o[c][1]; q[c][2] = o[c][2]; }
            }
            float f1[3] = {q[1][0] - q[0][0], q[1][1] - q[0][1], q[1][2] - q[0][2]};
            float f2[3] = {q[2][0] - q[0][0], q[2][1] - q[0][1], q[2][2] - q[0][2]};
            float nn[3] = {f1[1] * f2[2] - f1[2] * f2[1], f1[2] * f2[0] - f1[0] * f2[2],
                           f1[0] * f2[1] - f1[1] * f2[0]};
            if (nn[0] * on[0] + nn[1] * on[1] + nn[2] * on[2] < 0.0f) flip = 1;
        }
        if (flip) continue;

        pos[(size_t)a * 3] = (float)np[0];
        pos[(size_t)a * 3 + 1] = (float)np[1];
        pos[(size_t)a * 3 + 2] = (float)np[2];
        Q[a] = qq;
        alive[b] = 0;

        for (int i2 = 0; i2 < vcount[b]; i2++) {
            int f = vfaces[b][i2];
            if (tri[f * 3] == DEAD) continue;
            for (int k2 = 0; k2 < 3; k2++)
                if (tri[f * 3 + k2] == (uint32_t)b) tri[f * 3 + k2] = (uint32_t)a;
            uint32_t j0 = tri[f * 3], j1 = tri[f * 3 + 1], j2 = tri[f * 3 + 2];
            if (j0 == j1 || j1 == j2 || j0 == j2) {
                tri[f * 3] = DEAD; tri[f * 3 + 1] = DEAD; tri[f * 3 + 2] = DEAD;
                live--;
            } else {
                if (vcount[a] == vcap[a]) {
                    int nc = vcap[a] ? vcap[a] * 2 : 8;
                    int *nb2 = (int *)realloc(vfaces[a], (size_t)nc * sizeof(int));
                    if (nb2) { vfaces[a] = nb2; vcap[a] = nc; }
                }
                if (vcount[a] < vcap[a]) vfaces[a][vcount[a]++] = f;
            }
        }
        vcount[b] = 0;
    }

    for (int v = 0; v < nverts; v++) free(vfaces[v]);
    free(vfaces); free(vcount); free(vcap);
    free(edges);

    int k = 0;
    for (int f = 0; f < faces_in; f++) {
        if (tri[f * 3] == DEAD) continue;
        tri_out[k * 3 + 0] = tri[f * 3 + 0];
        tri_out[k * 3 + 1] = tri[f * 3 + 1];
        tri_out[k * 3 + 2] = tri[f * 3 + 2];
        k++;
    }
    *faces_out = k;
    free(tri); free(Q); free(alive);
    return 0;
}