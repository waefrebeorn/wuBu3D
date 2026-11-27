"""Heat weights and dual quaternion skinning: the two claims, measured.

  HEAT  weights diffuse over the mesh surface, so a vertex is influenced by bones it is connected
        to, not merely by bones that are near it in space.
  DQS   blending rigid transforms as dual quaternions does not shrink the surface. LBS on a 50/50
        twist pulls a point at radius r in to r*cos(45deg) = 0.707r; DQS keeps r.

Run: python3 tests/test_heat_dqs.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wubu3d_dqs as dqs  # noqa: E402
import wubu3d_heat as heat  # noqa: E402
import wubu3d_skin as skin  # noqa: E402

S, E, W = (0.0, 0.0, 0.0), (0.0, -0.62, 0.0), (0.0, -1.06, 0.0)
BONES = dict(upper=(S, E), fore=(E, W))
RINGS, SIDES, RAD = 14, 8, 0.085


def tube():
    """Tube as quads: each quad contributes four vertices in face order (what heat_weights wants)."""
    def ring(i):
        t = i / (RINGS - 1.0)
        if t <= 0.5:
            c = tuple(S[k] + (E[k] - S[k]) * t * 2 for k in range(3))
        else:
            c = tuple(E[k] + (W[k] - E[k]) * (t - 0.5) * 2 for k in range(3))
        return [(c[0] + RAD * math.cos(2 * math.pi * j / SIDES), c[1],
                 c[2] + RAD * math.sin(2 * math.pi * j / SIDES)) for j in range(SIDES)]

    rings = [ring(i) for i in range(RINGS)]
    faces, pts = [], []
    for i in range(RINGS - 1):
        for j in range(SIDES):
            a = rings[i][j]
            b = rings[i][(j + 1) % SIDES]
            c = rings[i + 1][(j + 1) % SIDES]
            d = rings[i + 1][j]
            faces.append([a, b, c, d])
            pts.extend([a, b, c, d])
    return pts, faces, rings


def pose(theta_deg, axis="x"):
    th = math.radians(theta_deg)
    c, s = math.cos(th), math.sin(th)
    if axis == "x":
        R = [[1, 0, 0], [0, c, -s], [0, s, c]]
    else:                       # twist about the bone's own axis (y)
        R = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    wrist = tuple(E[k] + sum(R[k][j] * (W[j] - E[j]) for j in range(3)) for k in range(3))
    mats = {"upper": skin.bone_matrix(S, E, S, E), "fore": skin.bone_matrix(E, W, E, wrist)}
    return mats


def main():
    pts, faces, rings = tube()

    names, Wh, nw, ne = heat.heat_weights(pts, faces, BONES, per_face=4, iterations=60)
    sums = [abs(sum(r) - 1.0) for r in Wh]
    inf = max(sum(1 for v in r if v > 0.01) for r in Wh)
    print("heat: %d raw verts -> %d welded, %d edges, weight-sum error %.1e, max influences %d"
          % (len(pts), nw, ne, max(sums), inf))

    # heat weights must be smooth: no vertex should jump straight from all-upper to all-fore
    hard = sum(1 for r in Wh if min(r) < 0.02 and max(r) > 0.98)
    print("heat: vertices locked 100/0 between the two bones: %d of %d (smoother is better)"
          % (hard, len(Wh)))

    # bend, then compare stretch
    mats = pose(90)
    names2, Wd = skin.paint([(p[0], p[1], p[2]) for p in pts], BONES, radius=0.25)
    def stretch(out):
        """Quad q = i*SIDES+j owns vertices 4q..4q+3; compare its first corner with the same
        corner of the quad one ring up."""
        worst = 1.0
        for i in range(RINGS - 2):
            for j in range(SIDES):
                a = 4 * (i * SIDES + j)
                b = 4 * ((i + 1) * SIDES + j)
                rest = math.dist(pts[a], pts[b])
                worst = max(worst, math.dist(out[a], out[b]) / max(1e-6, rest))
        return worst
    lb_h = stretch(skin.deform(pts, names, Wh, mats))
    lb_d = stretch(skin.deform(pts, names2, Wd, mats))
    print("bend 90: worst edge stretch  heat %.2fx   distance %.2fx" % (lb_h, lb_d))

    # ---- DQS vs LBS on a pure twist at the joint
    twist = pose(90, axis="y")
    mid = rings[RINGS // 2]
    probe = mid[0]
    Wt = [[0.5, 0.5]] * 1
    nms = ["upper", "fore"]
    lbs = skin.deform([probe], nms, Wt, twist)[0]
    dq = dqs.deform([probe], nms, Wt, twist)[0]

    def radius(p):      # distance from the bone axis (the y axis through x=z=0)
        return math.hypot(p[0], p[2])
    r0 = radius(probe)
    print("twist 90, point at radius %.4f:" % r0)
    print("   LBS -> radius %.4f  (%.0f%% of rest, the candy-wrapper pinch)"
          % (radius(lbs), 100 * radius(lbs) / r0))
    print("   DQS -> radius %.4f  (%.0f%% of rest)" % (radius(dq), 100 * radius(dq) / r0))

    ok = True
    if abs(radius(dq) - r0) > r0 * 0.06:
        print("FAIL: DQS did not preserve radius")
        ok = False
    if radius(lbs) > r0 * 0.9:
        print("FAIL: LBS was expected to pinch and did not")
        ok = False
    print("ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
