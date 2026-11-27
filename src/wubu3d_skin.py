"""wubu3d_skin — linear blend skinning with painted weights.

The rig in wubu3d_rig builds geometry directly in posed space, which means a limb is a rigid tube
that pivots: at 90 degrees the surface tears at the joint, and the tear grows with the bend.

Skinned deformation separates REST geometry from the pose:

    rest mesh  --bones-->  weights  --pose-->  deformed mesh

Every vertex carries weights over the bones (max 4, summing to 1, as GPUs require). A vertex near
a joint is shared by both bones, so the surface bends THROUGH the joint instead of breaking at it.

Measured on a two-bone arm bent 90 degrees: worst edge stretch 3.05x rigid, 1.35x skinned.

No numpy: this module matches the rest of the box tree (pure python, lists and math).
"""

import math

MAX_INFLUENCES = 4


def seg_dist(p, a, b):
    """Distance from point p to segment a-b.

    Weights come from distance to the BONE SEGMENT, not to the joint. A vertex halfway along a
    forearm is far from both joints and would take a single influence, so nothing would blend.
    """
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    L2 = dx * dx + dy * dy + dz * dz
    if L2 < 1e-12:
        return math.dist(p, a)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy + (p[2] - az) * dz) / L2
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return math.dist(p, (ax + dx * t, ay + dy * t, az + dz * t))


def falloff(dist, radius):
    """Smoothstep: 1 at the bone, 0 at `radius`, and C1-continuous between. A linear ramp leaves a
    visible crease where its derivative jumps."""
    t = 1.0 - dist / radius if radius > 1e-9 else 0.0
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return t * t * (3.0 - 2.0 * t)


def normalise(W, max_inf=MAX_INFLUENCES):
    """Keep the strongest `max_inf` influences and make every row sum to 1."""
    out = []
    for row in W:
        pairs = sorted(enumerate(row), key=lambda kv: -kv[1])[:max_inf]
        s = sum(v for _i, v in pairs)
        col = [0.0] * len(row)
        if s > 1e-9:
            for i, v in pairs:
                col[i] = v / s
        out.append(col)
    return out


def paint(points, bones, radius):
    """Automatic weights: bones is {name: (head, tail)}; points is [(x,y,z)].

    Returns (names, W) where W[i][k] is the weight of bone k on vertex i.
    """
    names = list(bones)
    W = []
    for p in points:
        row = [falloff(seg_dist(p, bones[n][0], bones[n][1]), radius) + 1e-6 for n in names]
        if max(row) < 1e-3:                      # no bone reaches: take the nearest
            d = [seg_dist(p, bones[n][0], bones[n][1]) for n in names]
            row = [1.0 if i == d.index(min(d)) else 0.0 for i in range(len(names))]
        W.append(row)
    return names, normalise(W)


def _norm(v):
    L = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
    return (v[0] / L, v[1] / L, v[2] / L)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def bone_matrix(rest_head, rest_tail, pose_head, pose_tail):
    """4x4 (list of rows) taking the rest bone to its posed position: rotate, then translate."""
    a = _norm((rest_tail[0] - rest_head[0], rest_tail[1] - rest_head[1],
               rest_tail[2] - rest_head[2]))
    b = _norm((pose_tail[0] - pose_head[0], pose_tail[1] - pose_head[1],
               pose_tail[2] - pose_head[2]))
    v = _cross(a, b)
    c = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    if math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) < 1e-9:
        R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] if c > 0 else [[-1, 0, 0], [0, -1, 0], [0, 0, -1]]
    else:
        vx = [[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]
        k = 1.0 / (1.0 + c)
        R = [[(1 if i == j else 0) + vx[i][j] + sum(vx[i][m] * vx[m][j] for m in range(3)) * k
              for j in range(3)] for i in range(3)]
    t = tuple(pose_head[i] - sum(R[i][j] * rest_head[j] for j in range(3)) for i in range(3))
    return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]], [0.0, 0.0, 0.0, 1.0]]


def deform(points, names, W, mats):
    """Linear blend skinning: p' = sum_k w_k * M_k * p."""
    out = []
    for p, row in zip(points, W):
        acc = [0.0, 0.0, 0.0]
        for k, w in enumerate(row):
            if w <= 1e-6:
                continue
            M = mats.get(names[k])
            if M is None:
                continue
            for i in range(3):
                acc[i] += w * (M[i][0] * p[0] + M[i][1] * p[1] + M[i][2] * p[2] + M[i][3])
        out.append(tuple(acc))
    return out


def apply_to_render(verts, bones, mats, radius):
    """Skin a wubu3d render buffer: verts are (x, y, z, colour) tuples; returns the same format."""
    pts = [(v[0], v[1], v[2]) for v in verts]
    names, W = paint(pts, bones, radius)
    moved = deform(pts, names, W, mats)
    return [(m[0], m[1], m[2], v[3]) for m, v in zip(moved, verts)], W


def _self_test():
    # a two-bone arm as a tube of rings
    S, E, Wr = (0.0, 0.0, 0.0), (0.0, -0.62, 0.0), (0.0, -1.06, 0.0)
    pts = []
    for i in range(14):
        t = i / 13.0
        c = (S[0] + (E[0] - S[0]) * t * 2, S[1] + (E[1] - S[1]) * t * 2, 0.0) if t <= 0.5 else \
            (E[0] + (Wr[0] - E[0]) * (t - 0.5) * 2, E[1] + (Wr[1] - E[1]) * (t - 0.5) * 2, 0.0)
        for j in range(8):
            a = 2 * math.pi * j / 8
            pts.append((c[0] + 0.085 * math.cos(a), c[1], c[2] + 0.085 * math.sin(a)))
    bones = dict(upper=(S, E), fore=(E, Wr))
    # a TRUE 90-degree bend: the rest forearm points -y, the posed one points -z.
    # (The first version of this test flipped it 180 degrees — linear blend skinning collapses
    # through an exact flip, so skinning looked WORSE than rigid until the pose was fixed.)
    waist = (E[0], E[1], E[2] - (Wr[1] - E[1]))
    mats = dict(upper=bone_matrix(S, E, S, E), fore=bone_matrix(E, Wr, E, waist))

    def worst_stretch(d):
        worst = 1.0
        for i in range(13):
            a0, a1 = d[i * 8:(i + 1) * 8], d[(i + 1) * 8:(i + 2) * 8]
            rest = math.dist(pts[i * 8], pts[(i + 1) * 8])
            worst = max(worst, max(math.dist(x, y) for x, y in zip(a0, a1)) / max(1e-6, rest))
        return worst

    print("vertices %d  (%d rings x 8)" % (len(pts), 14))
    print("bend 90 deg — the blend RADIUS is the weight-painting control:")
    for r in (0.10, 0.18, 0.30, 0.45, 0.60):
        names, W = paint(pts, bones, r)
        sums = max(abs(sum(row) - 1.0) for row in W)
        blend = sum(1 for row in W if sum(1 for v in row if v > 0.05) == 2)
        idx = [row.index(max(row)) for row in W]
        hard = [[1.0 if idx[i] == k else 0.0 for k in range(2)] for i in range(len(W))]
        print("  radius %.2f  blended %2d  weights sum err %.1e  skinned %.2fx  rigid %.2fx"
              % (r, blend, sums, worst_stretch(deform(pts, names, W, mats)),
                 worst_stretch(deform(pts, names, hard, mats))))


if __name__ == "__main__":
    _self_test()
