// wubuik — C11 inverse kinematics: analytic two-bone and FABRIK chains.
//
// Python drives it (poses, targets, animation curves); the solve is here.
//
// SLERM note — algorithms cited, code ours:
//   two-bone analytic   law of cosines. Given the root, the target and the two bone lengths the
//                       triangle is determined, so the joint sits at a closed-form angle. This is
//                       what Godot's SkeletonModification2DTwoBoneIK and Unity's two-bone IK
//                       constraints do; no iteration is needed or wanted.
//   FABRIK              Aristidou & Lasenby, "FABRIK: A fast, iterative solver for the Inverse
//                       Kinematics problem", Graphical Models 2011 — forward and backward
//                       reaching passes over the chain, converging in a handful of iterations.
//
// Build: cc -O2 -std=c11 -shared -fPIC -o libwubuik.so wubuik.c -lm

#include <math.h>
#include <string.h>

static void vsub(const float *a, const float *b, float *o) {
    o[0] = a[0] - b[0]; o[1] = a[1] - b[1]; o[2] = a[2] - b[2];
}
static float vlen(const float *a) { return sqrtf(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]); }
static float vdot(const float *a, const float *b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
static int vnorm(float *a) {
    float L = vlen(a);
    if (L < 1e-12f) return 0;
    a[0] /= L; a[1] /= L; a[2] /= L;
    return 1;
}

static int two_bone(const float *root, const float *target, float l1, float l2,
                    const float *pole, float *joint, float *end) {
    float axis[3];
    vsub(target, root, axis);
    float d = vlen(axis);
    if (d < 1e-6f) return 0;
    float dir[3] = {axis[0] / d, axis[1] / d, axis[2] / d};

    // a target outside the reachable ring is clamped onto it: the chain points at it and
    // straightens, rather than the solve failing
    float lo = fabsf(l1 - l2) + 1e-4f, hi = l1 + l2 - 1e-4f;
    float dd = d;
    if (dd < lo) dd = lo;
    if (dd > hi) dd = hi;

    // cosine rule at the root
    float ca = (l1 * l1 + dd * dd - l2 * l2) / (2.0f * l1 * dd);
    if (ca > 1.0f) ca = 1.0f;
    if (ca < -1.0f) ca = -1.0f;
    float a = acosf(ca);

    // bend plane: the pole vector projected off the root->target axis
    float p[3] = {pole[0] - root[0], pole[1] - root[1], pole[2] - root[2]};
    float along = vdot(p, dir);
    p[0] -= dir[0] * along; p[1] -= dir[1] * along; p[2] -= dir[2] * along;
    if (!vnorm(p)) {                       // degenerate pole: pick any stable perpendicular
        float t[3] = {0.0f, 1.0f, 0.0f};
        if (fabsf(vdot(t, dir)) > 0.9f) { t[0] = 1.0f; t[1] = 0.0f; }
        p[0] = t[0] - dir[0] * vdot(t, dir);
        p[1] = t[1] - dir[1] * vdot(t, dir);
        p[2] = t[2] - dir[2] * vdot(t, dir);
        vnorm(p);
    }

    float sa = sinf(a), cb = cosf(a);
    joint[0] = root[0] + l1 * (cb * dir[0] + sa * p[0]);
    joint[1] = root[1] + l1 * (cb * dir[1] + sa * p[1]);
    joint[2] = root[2] + l1 * (cb * dir[2] + sa * p[2]);
    end[0] = root[0] + dd * dir[0];
    end[1] = root[1] + dd * dir[1];
    end[2] = root[2] + dd * dir[2];
    return 1;
}

// joints: n*3, modified in place. Returns iterations used (or -1 if unreachable and stretched).
int wb_ik_two_bone(const float *root, const float *target, float l1, float l2,
                   const float *pole, float *joint_out, float *end_out) {
    return two_bone(root, target, l1, l2, pole, joint_out, end_out) ? 1 : 0;
}

// FABRIK over a chain of n joint positions. Returns the number of iterations used.
int wb_ik_fabrik(float *p, int n, const float *target, int max_iter, float tol) {
    if (n < 2) return 0;
    float L[64];
    int nb = n - 1 > 64 ? 64 : n - 1;
    float total = 0.0f;
    for (int i = 0; i < nb; i++) {
        float d[3];
        vsub(p + (i + 1) * 3, p + i * 3, d);
        L[i] = vlen(d);
        total += L[i];
    }
    float root[3] = {p[0], p[1], p[2]};
    float to_t[3];
    vsub(target, root, to_t);
    float dist = vlen(to_t);
    if (dist > total) {
        // out of reach: lay the chain along the direction and stop
        float dir[3] = {to_t[0], to_t[1], to_t[2]};
        if (!vnorm(dir)) return 0;
        for (int i = 1; i < n; i++) {
            p[i * 3 + 0] = p[(i - 1) * 3 + 0] + dir[0] * L[i - 1];
            p[i * 3 + 1] = p[(i - 1) * 3 + 1] + dir[1] * L[i - 1];
            p[i * 3 + 2] = p[(i - 1) * 3 + 2] + dir[2] * L[i - 1];
        }
        return max_iter;
    }

    int it = 0;
    for (; it < max_iter; it++) {
        float err[3];
        vsub(p + (n - 1) * 3, target, err);
        if (vlen(err) <= tol) break;

        // backward: pin the end effector to the target and walk toward the root
        p[(n - 1) * 3 + 0] = target[0];
        p[(n - 1) * 3 + 1] = target[1];
        p[(n - 1) * 3 + 2] = target[2];
        for (int i = n - 2; i >= 0; i--) {
            float d[3];
            vsub(p + i * 3, p + (i + 1) * 3, d);
            if (!vnorm(d)) continue;
            p[i * 3 + 0] = p[(i + 1) * 3 + 0] + d[0] * L[i];
            p[i * 3 + 1] = p[(i + 1) * 3 + 1] + d[1] * L[i];
            p[i * 3 + 2] = p[(i + 1) * 3 + 2] + d[2] * L[i];
        }
        // forward: put the root back and restore every bone length outward
        p[0] = root[0]; p[1] = root[1]; p[2] = root[2];
        for (int i = 0; i < n - 1; i++) {
            float d[3];
            vsub(p + (i + 1) * 3, p + i * 3, d);
            if (!vnorm(d)) continue;
            p[(i + 1) * 3 + 0] = p[i * 3 + 0] + d[0] * L[i];
            p[(i + 1) * 3 + 1] = p[i * 3 + 1] + d[1] * L[i];
            p[(i + 1) * 3 + 2] = p[i * 3 + 2] + d[2] * L[i];
        }
    }
    return it;
}
