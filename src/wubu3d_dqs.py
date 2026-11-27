"""wubu3d_dqs — dual quaternion skinning, after Kavan, Collins, O'Sullivan & Zara (2006/2007).

Linear blend skinning averages the bone MATRICES. Rotations are not linear, so the average of two
rotations is not a rotation: at a 90 degree bend a vertex weighted 50/50 shrinks toward the origin,
and on a twist the limb collapses into a candy-wrapper pinch.

Dual quaternions represent a rigid transform as a pair of quaternions that blend correctly: the
blend of two dual quaternions is renormalised back to a rigid transform, so no shrinkage is
introduced by the blend itself.

    qr  rotation quaternion
    qd  dual part = 0.5 * (0, t) * qr, where t is the translation
    transform(p) = R(p) + t, with t recovered as 2 * (qd * conj(qr)).vec

Blending (DLB, dual quaternion linear blending): normalise weights, sum, then divide both parts by
|qr_sum|. Antipodal pairs must be flipped to the same hemisphere first, or the blend takes the long
way round and the limb explodes through itself.

Reference: Kavan, L., Collins, S., O'Sullivan, C., Zara, J., "Dual Quaternions for Rigid
Transformation Blending", Trinity College Dublin TCD-CS-2006-46 / I3D 2007.

Pure python.
"""

import math


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def qconj(q):
    return (-q[0], -q[1], -q[2], q[3])


def qnorm(q):
    return math.sqrt(sum(v * v for v in q)) or 1e-12


def qscale(q, s):
    return (q[0] * s, q[1] * s, q[2] * s, q[3] * s)


def matrix_to_quat(M):
    """Rotation quaternion from the 3x3 part of a 4x4 (Shepperd's method, branch on the big term)."""
    m00, m01, m02 = M[0][0], M[0][1], M[0][2]
    m10, m11, m12 = M[1][0], M[1][1], M[1][2]
    m20, m21, m22 = M[2][0], M[2][1], M[2][2]
    tr = m00 + m11 + m22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = ((m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s, 0.25 * s)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        q = (0.25 * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s)
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        q = ((m01 + m10) / s, 0.25 * s, (m12 + m21) / s, (m02 - m20) / s)
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2
        q = ((m02 + m20) / s, (m12 + m21) / s, 0.25 * s, (m10 - m01) / s)
    n = qnorm(q)
    return qscale(q, 1.0 / n)


def matrix_to_dq(M):
    """Rigid transform (4x4) as a unit dual quaternion (qr, qd)."""
    qr = matrix_to_quat(M)
    t = (M[0][3], M[1][3], M[2][3])
    qd = qscale(qmul((t[0], t[1], t[2], 0.0), qr), 0.5)
    return qr, qd


def blend(dqs, weights):
    """DLB: weighted sum, antipodal flip, renormalise."""
    ref = None
    accr = (0.0, 0.0, 0.0, 0.0)
    accd = (0.0, 0.0, 0.0, 0.0)
    for (qr, qd), w in zip(dqs, weights):
        if w <= 1e-9:
            continue
        if ref is None:
            ref = qr
        # shortest path: a quaternion and its negation are the same rotation, but blending them
        # without choosing a hemisphere interpolates the long way and the surface turns inside out
        dot = sum(qr[i] * ref[i] for i in range(4))
        s = -1.0 if dot < 0 else 1.0
        accr = tuple(accr[i] + s * w * qr[i] for i in range(4))
        accd = tuple(accd[i] + s * w * qd[i] for i in range(4))
    n = qnorm(accr) or 1e-12
    return qscale(accr, 1.0 / n), qscale(accd, 1.0 / n)


def transform_point(dq, p):
    """Apply a dual quaternion to a point: p' = R(p) + t."""
    qr, qd = dq
    # rotate with the rotation quaternion
    v = qmul(qmul(qr, (p[0], p[1], p[2], 0.0)), qconj(qr))
    # translation: t = 2 * (qd * conj(qr)), vector part
    t = qmul(qd, qconj(qr))
    return (v[0] + 2 * t[0], v[1] + 2 * t[1], v[2] + 2 * t[2])


def deform(points, names, W, mats):
    """Dual quaternion skinning: p' = blend_i(w_i * dq_i)(p)."""
    dqs = {n: matrix_to_dq(mats[n]) for n in names if n in mats}
    out = []
    for p, row in zip(points, W):
        pairs = [(dqs[names[i]], w) for i, w in enumerate(row) if w > 1e-6 and names[i] in dqs]
        if not pairs:
            out.append(tuple(p))
            continue
        dq = blend([a for a, _w in pairs], [w for _a, w in pairs])
        out.append(transform_point(dq, (p[0], p[1], p[2])))
    return out
