"""Skinning invariants. Run directly: python3 tests/test_skin.py"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wubu3d_skin as sk  # noqa: E402

S, E, W = (0.0, 0.0, 0.0), (0.0, -0.62, 0.0), (0.0, -1.06, 0.0)
BONES = dict(upper=(S, E), fore=(E, W))


def tube(rings=14, sides=8, r=0.085):
    pts = []
    for i in range(rings):
        t = i / (rings - 1.0)
        if t <= 0.5:
            c = tuple(S[k] + (E[k] - S[k]) * t * 2 for k in range(3))
        else:
            c = tuple(E[k] + (W[k] - E[k]) * (t - 0.5) * 2 for k in range(3))
        for j in range(sides):
            a = 2 * math.pi * j / sides
            pts.append((c[0] + r * math.cos(a), c[1], c[2] + r * math.sin(a)))
    return pts


def stretch(pts, out, sides=8, rings=14):
    worst = 1.0
    for i in range(rings - 1):
        a0, a1 = out[i * sides:(i + 1) * sides], out[(i + 1) * sides:(i + 2) * sides]
        rest = math.dist(pts[i * sides], pts[(i + 1) * sides])
        worst = max(worst, max(math.dist(x, y) for x, y in zip(a0, a1)) / max(1e-6, rest))
    return worst


def main():
    pts = tube()
    names, Wt = sk.paint(pts, BONES, 0.25)

    # 1. weights are normalised and capped
    err = max(abs(sum(r) - 1.0) for r in Wt)
    inf = max(sum(1 for v in r if v > 0.0) for r in Wt)
    assert err < 1e-9, "weights must sum to 1, worst error %.2e" % err
    assert inf <= sk.MAX_INFLUENCES, "at most %d influences, saw %d" % (sk.MAX_INFLUENCES, inf)

    # 2. the joint actually blends
    blended = sum(1 for r in Wt if sum(1 for v in r if v > 0.05) == 2)
    assert blended >= 8, "expected a blend band at the elbow, got %d vertices" % blended

    # 3. a 90-degree bend is tolerated better by skinning than by rigid assignment
    waist = (E[0], E[1], E[2] - (W[1] - E[1]))
    mats = dict(upper=sk.bone_matrix(S, E, S, E), fore=sk.bone_matrix(E, W, E, waist))
    idx = [r.index(max(r)) for r in Wt]
    hard = [[1.0 if idx[i] == k else 0.0 for k in range(2)] for i in range(len(Wt))]
    s_skin = stretch(pts, sk.deform(pts, names, Wt, mats))
    s_rig = stretch(pts, sk.deform(pts, names, hard, mats))
    assert s_skin < s_rig, "skinning must beat rigid: %.2f vs %.2f" % (s_skin, s_rig)

    # 4. an unbent pose is an identity
    ident = {n: sk.bone_matrix(*BONES[n], *BONES[n]) for n in names}
    moved = sk.deform(pts, names, Wt, ident)
    drift = max(math.dist(a, b) for a, b in zip(pts, moved))
    assert drift < 1e-6, "rest pose must not move vertices, drift %.2e" % drift

    print("ok  weights err %.1e  influences %d  blended %d  "
          "stretch skinned %.2fx vs rigid %.2fx  rest drift %.1e"
          % (err, inf, blended, s_skin, s_rig, drift))


if __name__ == "__main__":
    main()
