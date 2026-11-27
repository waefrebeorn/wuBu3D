// wuburig — C11 rigging core: swing-twist decomposition, twist distribution, FK/IK blending.
//
// The candy-wrapper is not a weight problem. Linear blend skinning averages bone MATRICES, and the
// average of two rotations 180 degrees apart collapses to near-zero scale — every weight value
// still averages two opposed rotations, so no painting fixes it. Dual quaternions fix the visible
// collapse (wubu3d_dqs) but they do not survive export: glTF, Unity and Unreal all skin with LBS.
//
// The rig-side fix is to never let a joint twist 180 degrees. Spread the twist across the chain, so
// each bone carries a share small enough that matrix averaging barely distorts:
//
//     hand twists 180 -> wrist 60 + forearm 60 + upper arm 60
//
// Short doc: Jessy Leite, "Fix Candy-Wrap Twist Deformation" (2026) — three stacked fixes:
// preserve volume (DQS), twist bones, corrective smoothing. This module is the second one.
//
// SLERM note — swing-twist decomposition: Chad Vernon, "Swing Twist Decomposition" and the standard
// formulation q = swing * twist, where twist is the rotation about a chosen axis and swing is the
// shortest arc that gets there. Code ours.
//
// Build: cc -O3 -std=c11 -shared -fPIC -o libwuburig.so wuburig.c -lm

#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct { double x, y, z, w; } quat;

quat wb_q_from_axis_angle(const double *axis, double angle) {
    double L = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]);
    if (L < 1e-12) { quat q = {0, 0, 0, 1}; return q; }
    double s = sin(angle * 0.5) / L;
    quat q = {axis[0] * s, axis[1] * s, axis[2] * s, cos(angle * 0.5)};
    return q;
}

static quat q_mul(quat a, quat b) {
    quat r;
    r.x = a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y;
    r.y = a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x;
    r.z = a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w;
    r.w = a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z;
    return r;
}
static quat q_conj(quat q) { quat r = {-q.x, -q.y, -q.z, q.w}; return r; }
static double q_len(quat q) { return sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w); }
static quat q_norm(quat q) {
    double L = q_len(q);
    if (L < 1e-12) { quat i = {0, 0, 0, 1}; return i; }
    quat r = {q.x / L, q.y / L, q.z / L, q.w / L};
    return r;
}

// q = swing * twist about `axis` (axis need not be normalised; it is the bone's own direction)
void wb_swing_twist(const double *q_in, const double *axis, double *swing_out, double *twist_deg_out) {
    quat q = q_norm((quat){q_in[0], q_in[1], q_in[2], q_in[3]});
    double L = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]);
    double a[3] = {axis[0] / (L > 1e-12 ? L : 1.0), axis[1] / (L > 1e-12 ? L : 1.0),
                   axis[2] / (L > 1e-12 ? L : 1.0)};
    // projection of the vector part onto the axis gives the twist quaternion directly
    double d = q.x * a[0] + q.y * a[1] + q.z * a[2];
    quat twist = {a[0] * d, a[1] * d, a[2] * d, q.w};
    double tl = q_len(twist);
    if (tl < 1e-9) {
        // no twist component: the whole thing is swing
        twist = (quat){0, 0, 0, 1};
    } else {
        twist = q_norm(twist);
    }
    quat swing = q_mul(q, q_conj(twist));       // q = swing * twist  =>  swing = q * twist^-1
    if (swing_out) {
        swing_out[0] = swing.x; swing_out[1] = swing.y;
        swing_out[2] = swing.z; swing_out[3] = swing.w;
    }
    if (twist_deg_out) {
        double ang = 2.0 * atan2(sqrt(twist.x * twist.x + twist.y * twist.y + twist.z * twist.z),
                                 twist.w);
        if (ang > M_PI) ang -= 2.0 * M_PI;
        *twist_deg_out = ang * 180.0 / M_PI;
    }
}

// Distribute a total twist (degrees) across `n` bones of a chain lying along `axis`.
// out_angles[i] is the share applied at bone i, so the sum equals the total.
void wb_twist_distribute(int n, double total_deg, double *out_angles, int mode) {
    if (n <= 0) return;
    for (int i = 0; i < n; i++) {
        double share;
        if (mode == 1) {
            // even split: the classic twist-bone setup
            share = total_deg / (double)n;
        } else {
            // ramped: root carries less, the joint nearest the twist carries most, which keeps the
            // seam that would pinch under matrix averaging furthest from the parent
            double wsum = 0.0;
            for (int k = 0; k < n; k++) wsum += (double)(k + 1);
            share = total_deg * (double)(i + 1) / wsum;
        }
        out_angles[i] = share;
    }
}

// Compose a chain: given per-bone rotation quaternions relative to the parent, produce world
// quaternions. rotations is n*4, out is n*4.
void wb_chain_world(int n, const double *rotations, double *out) {
    quat acc = {0, 0, 0, 1};
    for (int i = 0; i < n; i++) {
        quat r = {rotations[i * 4], rotations[i * 4 + 1], rotations[i * 4 + 2], rotations[i * 4 + 3]};
        acc = q_mul(acc, q_norm(r));
        out[i * 4 + 0] = acc.x; out[i * 4 + 1] = acc.y;
        out[i * 4 + 2] = acc.z; out[i * 4 + 3] = acc.w;
    }
}

// Rotate a point by a quaternion.
void wb_qrot(const double *q_in, const double *p, double *out) {
    quat q = q_norm((quat){q_in[0], q_in[1], q_in[2], q_in[3]});
    quat v = {p[0], p[1], p[2], 0.0};
    quat r = q_mul(q_mul(q, v), q_conj(q));
    out[0] = r.x; out[1] = r.y; out[2] = r.z;
}

// FK/IK blend: a weight of 0 is pure FK, 1 is pure IK, and the result is a straight blend of the
// two pose positions. Enough for a switch that eases between the two, which is how engines expose
// it; a proper solution would slerp the rotations instead of the endpoints.
void wb_fkik_blend(const double *fk, const double *ik, int n, double w, double *out) {
    for (int i = 0; i < n * 3; i++) out[i] = fk[i] * (1.0 - w) + ik[i] * w;
}

// Radius preservation estimate for a two-bone LBS blend at angle `twist_deg`, used by the tests to
// show what distribution buys: LBS averages the matrices, so a point at radius r lands at
// r*cos(twist/2).
double wb_lbs_radius_ratio(double twist_deg) {
    double half = (twist_deg * 0.5) * M_PI / 180.0;
    return fabs(cos(half));
}
