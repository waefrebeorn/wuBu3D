/* rig.c — auto-skinning and IK, in C11.

SLERM of the tools the Roblox rigging market actually sells, by technique rather than by copying
code:

  Adaptive Auto Skinning ($35, Blender)      "auto weight tool... simple and predictable... resolution"
      -> per-vertex inverse-distance binding to bone SEGMENTS, then Laplacian weight smoothing over
         the mesh adjacency graph. The smoothing is the whole trick: raw distance weights are lumpy
         and crease at every joint, and a few smoothing passes is what makes a bind look hand-made.

  Rigs Suite / Blocky R15 / Fluid Rig        FK/IK rigs with a pole control
      -> analytic two-bone IK (law of cosines, pole-vector plane) and FABRIK for longer chains.

  Game Rig Tools                             "game-ready rigs in seconds"
      -> rigid mode: one influence per vertex, chosen by nearest segment, with a blend band.

Build:
    gcc -O2 -march=native -shared -fPIC -o librig.so rig.c -lm
*/

#include <math.h>
#include <stdlib.h>
#include <string.h>

/* squared distance from p to segment ab, plus the parametric position of the closest point */
static float seg_dist2(const float *p, const float *a, const float *b, float *t_out)
{
    float abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
    float apx = p[0] - a[0], apy = p[1] - a[1], apz = p[2] - a[2];
    float den = abx * abx + aby * aby + abz * abz;
    float t = den > 1e-12f ? (apx * abx + apy * aby + apz * abz) / den : 0.0f;
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;
    float dx = apx - abx * t, dy = apy - aby * t, dz = apz - abz * t;
    if (t_out) *t_out = t;
    return dx * dx + dy * dy + dz * dz;
}

/* Build a vertex adjacency list from triangles: neighbour ids for the weight smoothing pass. */
static int build_adjacency(const int *tris, int ntris, int nverts,
                           int **adj_out, int **off_out)
{
    int nedge = ntris * 3;
    int *deg = calloc((size_t)nverts + 1, sizeof(int));
    if (!deg) return -1;
    for (int i = 0; i < ntris; ++i)
        for (int k = 0; k < 3; ++k) deg[tris[i * 3 + k]] += 2;

    int *off = malloc(((size_t)nverts + 1) * sizeof(int));
    if (!off) { free(deg); return -1; }
    off[0] = 0;
    for (int v = 0; v < nverts; ++v) off[v + 1] = off[v] + deg[v];

    int *adj = malloc((size_t)off[nverts] * sizeof(int));
    int *fill = calloc((size_t)nverts, sizeof(int));
    if (!adj || !fill) { free(deg); free(off); free(adj); free(fill); return -1; }

    for (int i = 0; i < ntris; ++i) {
        int a = tris[i * 3], b = tris[i * 3 + 1], c = tris[i * 3 + 2];
        int tri[3] = {a, b, c};
        for (int k = 0; k < 3; ++k) {
            int v = tri[k], u1 = tri[(k + 1) % 3], u2 = tri[(k + 2) % 3];
            adj[off[v] + fill[v]++] = u1;
            adj[off[v] + fill[v]++] = u2;
        }
    }
    free(deg);
    free(fill);
    *adj_out = adj;
    *off_out = off;
    (void)nedge;
    return 0;
}

/* wubu_skin: bind a mesh to a bone set.
 *   verts       n*3
 *   tris        ntris*3
 *   bones       nbones*6  (p0.xyz, p1.xyz)
 *   weights_out n*nbones  row-major, sums to 1 per vertex
 * Returns 0 on success.
 */
int wubu_skin(const float *verts, int n, const int *tris, int ntris,
              const float *bones, int nbones,
              int max_inf, float power, float eps,
              int smooth_iters, float smooth_lambda,
              float *weights_out)
{
    if (n <= 0 || nbones <= 0 || !verts || !bones || !weights_out) return -1;
    if (max_inf < 1) max_inf = 1;
    if (max_inf > nbones) max_inf = nbones;

    /* pass 1: inverse-distance weights */
    for (int v = 0; v < n; ++v) {
        const float *p = verts + v * 3;
        float *w = weights_out + (size_t)v * nbones;
        float sum = 0.0f;
        for (int b = 0; b < nbones; ++b) {
            float d2 = seg_dist2(p, bones + b * 6, bones + b * 6 + 3, NULL);
            float ww = 1.0f / (powf(d2, power * 0.5f) + eps);
            w[b] = ww;
            sum += ww;
        }
        if (sum <= 0.0f) {
            for (int b = 0; b < nbones; ++b) w[b] = (b == 0) ? 1.0f : 0.0f;
        } else {
            for (int b = 0; b < nbones; ++b) w[b] /= sum;
        }
    }

    /* pass 2 (top-k) is a separate call so a caller can smooth first and prune after, which is the
       order that keeps the smoothed field from being cut into hard bands. */
    (void)max_inf;
    return 0;
}

/* Select top-k influences per vertex without destroying the row layout. */
int wubu_skin_topk(float *weights, int n, int nbones, int k)
{
    if (!weights || n <= 0 || nbones <= 0) return -1;
    if (k < 1) k = 1;
    if (k > nbones) k = nbones;
    int *use = malloc((size_t)nbones * sizeof(int));
    int *mask = malloc((size_t)nbones * sizeof(int));
    if (!use || !mask) { free(use); free(mask); return -1; }

    for (int v = 0; v < n; ++v) {
        float *w = weights + (size_t)v * nbones;
        for (int b = 0; b < nbones; ++b) mask[b] = 0;
        for (int s = 0; s < k; ++s) {
            int best = -1;
            float bw = -1.0f;
            for (int b = 0; b < nbones; ++b)
                if (!mask[b] && w[b] > bw) { bw = w[b]; best = b; }
            if (best < 0) break;
            mask[best] = 1;
            use[s] = best;
        }
        float sum = 0.0f;
        for (int b = 0; b < nbones; ++b)
            if (!mask[b]) w[b] = 0.0f;
            else sum += w[b];
        if (sum > 0.0f)
            for (int b = 0; b < nbones; ++b) w[b] /= sum;
    }
    free(use);
    free(mask);
    return 0;
}

/* Laplacian smoothing of the weight field. This is the step that turns lumpy distance weights into
 * something that deforms without creasing, and it is the reason a bind takes a couple of seconds
 * instead of being instant. */
int wubu_smooth_weights(float *weights, int n, int nbones,
                        const int *tris, int ntris, int iters, float lambda)
{
    int *adj = NULL, *off = NULL;
    if (build_adjacency(tris, ntris, n, &adj, &off) != 0) return -1;
    float *tmp = malloc((size_t)n * (size_t)nbones * sizeof(float));
    if (!tmp) { free(adj); free(off); return -1; }

    for (int it = 0; it < iters; ++it) {
        memcpy(tmp, weights, (size_t)n * (size_t)nbones * sizeof(float));
        for (int v = 0; v < n; ++v) {
            int s = off[v], e = off[v + 1];
            if (e <= s) continue;
            float inv = 1.0f / (float)(e - s);
            for (int b = 0; b < nbones; ++b) {
                float acc = 0.0f;
                for (int i = s; i < e; ++i) acc += tmp[(size_t)adj[i] * nbones + b];
                acc *= inv;
                weights[(size_t)v * nbones + b] =
                        (1.0f - lambda) * tmp[(size_t)v * nbones + b] + lambda * acc;
            }
            float sum = 0.0f;
            for (int b = 0; b < nbones; ++b) sum += weights[(size_t)v * nbones + b];
            if (sum > 1e-8f)
                for (int b = 0; b < nbones; ++b) weights[(size_t)v * nbones + b] /= sum;
        }
    }
    free(tmp);
    free(adj);
    free(off);
    return 0;
}

/* Analytic two-bone IK. Bones are root->joint (len1) and joint->end (len2); the end is placed on
 * the target, the joint swings in the plane defined by the target and the pole vector. Returning a
 * pole direction as an explicit input is what the FK/IK rigs in this market expose as a control. */
int wubu_ik2(const float root[3], const float target[3], float len1, float len2,
             const float pole[3], float joint_out[3], float end_out[3])
{
    float dx = target[0] - root[0], dy = target[1] - root[1], dz = target[2] - root[2];
    float d = sqrtf(dx * dx + dy * dy + dz * dz);
    if (d < 1e-6f) return -1;
    float maxr = len1 + len2 - 1e-5f;
    float minr = fabsf(len1 - len2) + 1e-5f;
    float dd = d;
    if (dd > maxr) dd = maxr;
    if (dd < minr) dd = minr;

    float ux = dx / d, uy = dy / d, uz = dz / d;
    end_out[0] = root[0] + ux * dd;
    end_out[1] = root[1] + uy * dd;
    end_out[2] = root[2] + uz * dd;

    /* law of cosines: distance along the axis from the root to the joint's projection */
    float a = (len1 * len1 - len2 * len2 + dd * dd) / (2.0f * dd);
    float h2 = len1 * len1 - a * a;
    float h = h2 > 0.0f ? sqrtf(h2) : 0.0f;

    /* an axis perpendicular to the chain, bent toward the pole */
    float px = pole[0] - root[0], py = pole[1] - root[1], pz = pole[2] - root[2];
    float dot = px * ux + py * uy + pz * uz;
    px -= ux * dot; py -= uy * dot; pz -= uz * dot;
    float pl = sqrtf(px * px + py * py + pz * pz);
    if (pl < 1e-6f) {                      /* degenerate pole: pick any perpendicular */
        px = -uz; py = 0.0f; pz = ux;
        pl = sqrtf(px * px + py * py + pz * pz);
        if (pl < 1e-6f) { px = 1.0f; py = 0.0f; pz = 0.0f; pl = 1.0f; }
    }
    px /= pl; py /= pl; pz /= pl;

    joint_out[0] = root[0] + ux * a + px * h;
    joint_out[1] = root[1] + uy * a + py * h;
    joint_out[2] = root[2] + uz * a + pz * h;
    return 0;
}

/* FABRIK for chains longer than two bones. pts is n*3 with pts[0] fixed (the root). */
int wubu_fabrik(float *pts, int n, const float target[3], int iters, float tol)
{
    if (!pts || n < 2) return -1;
    float *len = malloc((size_t)(n - 1) * sizeof(float));
    if (!len) return -1;
    float total = 0.0f;
    for (int i = 0; i < n - 1; ++i) {
        float dx = pts[(i + 1) * 3] - pts[i * 3];
        float dy = pts[(i + 1) * 3 + 1] - pts[i * 3 + 1];
        float dz = pts[(i + 1) * 3 + 2] - pts[i * 3 + 2];
        len[i] = sqrtf(dx * dx + dy * dy + dz * dz);
        total += len[i];
    }
    float rootx = pts[0], rooty = pts[1], rootz = pts[2];
    float dx = target[0] - rootx, dy = target[1] - rooty, dz = target[2] - rootz;
    float dist = sqrtf(dx * dx + dy * dy + dz * dz);

    if (dist > total) {                      /* unreachable: point the chain at it, straight */
        for (int i = 1; i < n; ++i) {
            float t = (i > 0) ? 1.0f : 0.0f;
            (void)t;
            pts[i * 3] = pts[(i - 1) * 3] + dx / dist * len[i - 1];
            pts[i * 3 + 1] = pts[(i - 1) * 3 + 1] + dy / dist * len[i - 1];
            pts[i * 3 + 2] = pts[(i - 1) * 3 + 2] + dz / dist * len[i - 1];
        }
        free(len);
        return 0;
    }

    for (int it = 0; it < iters; ++it) {
        /* backward: pin the end at the target */
        pts[(n - 1) * 3] = target[0];
        pts[(n - 1) * 3 + 1] = target[1];
        pts[(n - 1) * 3 + 2] = target[2];
        for (int i = n - 2; i >= 0; --i) {
            float vx = pts[i * 3] - pts[(i + 1) * 3];
            float vy = pts[i * 3 + 1] - pts[(i + 1) * 3 + 1];
            float vz = pts[i * 3 + 2] - pts[(i + 1) * 3 + 2];
            float l = sqrtf(vx * vx + vy * vy + vz * vz);
            if (l < 1e-6f) continue;
            float r = len[i] / l;
            pts[i * 3] = pts[(i + 1) * 3] + vx * r;
            pts[i * 3 + 1] = pts[(i + 1) * 3 + 1] + vy * r;
            pts[i * 3 + 2] = pts[(i + 1) * 3 + 2] + vz * r;
        }
        /* forward: pin the root again */
        pts[0] = rootx; pts[1] = rooty; pts[2] = rootz;
        for (int i = 0; i < n - 1; ++i) {
            float vx = pts[(i + 1) * 3] - pts[i * 3];
            float vy = pts[(i + 1) * 3 + 1] - pts[i * 3 + 1];
            float vz = pts[(i + 1) * 3 + 2] - pts[i * 3 + 2];
            float l = sqrtf(vx * vx + vy * vy + vz * vz);
            if (l < 1e-6f) continue;
            float r = len[i] / l;
            pts[(i + 1) * 3] = pts[i * 3] + vx * r;
            pts[(i + 1) * 3 + 1] = pts[i * 3 + 1] + vy * r;
            pts[(i + 1) * 3 + 2] = pts[i * 3 + 2] + vz * r;
        }
        float ex = pts[(n - 1) * 3] - target[0];
        float ey = pts[(n - 1) * 3 + 1] - target[1];
        float ez = pts[(n - 1) * 3 + 2] - target[2];
        if (sqrtf(ex * ex + ey * ey + ez * ez) < tol) break;
    }
    free(len);
    return 0;
}

/* Linear-blend skinning of one vertex: sum_b w_b * (M_b * p). mats is nbones*12 (3x4 row-major). */
void wubu_skin_point(const float p[3], const float *weights, const float *mats3x4, int nbones,
                     float out[3])
{
    float x = 0.0f, y = 0.0f, z = 0.0f;
    for (int b = 0; b < nbones; ++b) {
        float w = weights[b];
        if (w <= 1e-6f) continue;
        const float *m = mats3x4 + b * 12;
        float rx = m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3];
        float ry = m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7];
        float rz = m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11];
        x += w * rx; y += w * ry; z += w * rz;
    }
    out[0] = x; out[1] = y; out[2] = z;
}

/* wubu_autorig — fit an R15-shaped skeleton to an arbitrary humanoid mesh.
 *
 * The market name for this is "auto rig" (AFK AI, Avatar Auto Setup, Game Rig Tools). The technique
 * is band analysis: slice the mesh by height, take each slice's centroid for the medial axis, and put
 * the joints at the band centres the R15 proportions imply. Side limbs split by the sign of x about
 * that medial axis. No learning, no templates beyond the proportion table.
 *
 * out_joints: 15 * 3 floats, out_parent: 15 ints, order = ORDER below.
 */
int wubu_autorig(const float *verts, int n, float out_joints[45], int out_parent[15])
{
    static const char *names[15] = {"LowerTorso","UpperTorso","Head",
        "LUpperArm","LLowerArm","LHand","RUpperArm","RLowerArm","RHand",
        "LUpperLeg","LLowerLeg","LFoot","RUpperLeg","RLowerLeg","RFoot"};
    static const int parents[15] = {-1,0,1, 1,3,4, 1,6,7, 0,9,10, 0,12,13};
    /* band centres as a fraction of total height, from the R15 proportion table */
    static const float bf[15] = {0.495f,0.655f,0.870f,
        0.650f,0.500f,0.355f, 0.650f,0.500f,0.355f,
        0.325f,0.145f,0.030f, 0.325f,0.145f,0.030f};
    (void)names;
    if (!verts || n < 8) return -1;

    float lo[3] = {1e30f,1e30f,1e30f}, hi[3] = {-1e30f,-1e30f,-1e30f};
    for (int i = 0; i < n; ++i)
        for (int k = 0; k < 3; ++k) {
            float v = verts[i*3+k];
            if (v < lo[k]) lo[k] = v;
            if (v > hi[k]) hi[k] = v;
        }
    float h = hi[1] - lo[1];
    if (h < 1e-4f) return -2;
    float midx = (lo[0] + hi[0]) * 0.5f;

    /* medial axis + side offsets per band, accumulated from the vertices that fall in each band */
    for (int j = 0; j < 15; ++j) {
        float cy = lo[1] + bf[j] * h;
        float bw = h * 0.045f;                      /* half-thickness of the slice */
        float sx = 0.0f, sz = 0.0f;
        float sxl = 0.0f, sxr = 0.0f;
        int cnt = 0, cnl = 0, cnr = 0;
        for (int i = 0; i < n; ++i) {
            float y = verts[i*3+1];
            if (y < cy - bw || y > cy + bw) continue;
            float x = verts[i*3] - midx, z = verts[i*3+2];
            sx += x; sz += z; cnt++;
            /* sides are split by the SIGN of x, not by the mean of |x|: averaging both sides gives
               zero for a symmetric body, which put both arm joints on the spine */
            /* arms are the outboard cluster, legs the inboard one. Without this split, the hip
               band averages in the hands (which hang to hip height) and pushes both hip joints
               out to the width of the arms. */
            int leg_band = (j >= 9);
            float lim = 0.175f * h;
            int in_zone = leg_band ? (fabsf(x) < lim) : (fabsf(x) > lim);
            if (!in_zone) continue;
            if (x < -0.05f * h) { sxl += x; cnl++; }
            else if (x > 0.05f * h) { sxr += x; cnr++; }
        }
        float px = 0.0f, pz = 0.0f;
        if (cnt) { px = sx / cnt; pz = sz / cnt; }
        float sidex_l = cnl ? sxl / cnl : 0.0f;
        float sidex_r = cnr ? sxr / cnr : 0.0f;

        /* limbs sit out at the mean |x| of their slice; the spine sits on the medial axis */
        int left = (j >= 3 && j <= 5) || (j >= 9 && j <= 11);
        int right = (j >= 6 && j <= 8) || (j >= 12);
        int is_limb = left || right;
        float x = is_limb ? (left ? sidex_l : sidex_r) : px;
        out_joints[j*3+0] = midx + x;
        out_joints[j*3+1] = cy;
        out_joints[j*3+2] = pz;
        out_parent[j] = parents[j];
    }
    return 0;
}
