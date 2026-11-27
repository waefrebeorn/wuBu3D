"""The C11 core against the Python implementations: same answers, and the speed that justifies it.

Checks
  1. wb_bone_matrix matches wubu3d_skin.bone_matrix
  2. wb_lbs matches wubu3d_skin.deform
  3. wb_dqs matches wubu3d_dqs.deform
  4. dual quaternions preserve the radius where linear blend skinning pinches (the candy wrapper)
  5. timing: 200k vertices, Python vs C

Run: python3 tests/test_c11_skin.py
"""

import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wubu3d_c11 as wc  # noqa: E402
import wubu3d_dqs as dqs  # noqa: E402
import wubu3d_skin as skin  # noqa: E402

S, E, W = (0.0, 0.0, 0.0), (0.0, -0.62, 0.0), (0.0, -1.06, 0.0)


def rot_y(deg, t=(0.0, 0.0, 0.0)):
    th = math.radians(deg)
    c, s = math.cos(th), math.sin(th)
    M = np.eye(4, dtype=np.float32)
    M[0, 0] = c; M[0, 2] = s
    M[2, 0] = -s; M[2, 2] = c
    M[0, 3] = t[0]; M[1, 3] = t[1]; M[2, 3] = t[2]
    return M


def main():
    wc.load()
    ok = True

    # 1. bone matrix
    pa = np.array(S, np.float32)
    pb = np.array(E, np.float32)
    qa = np.array(S, np.float32)
    qb = np.array([0.10, -0.60, 0.14], np.float32)
    C = wc.bone_matrix(pa, pb, qa, qb)
    Py = skin.bone_matrix(np.array(S, np.float32), np.array(E, np.float32),
                          np.array(S, np.float32), qb)
    d = float(np.abs(C - Py).max())
    print("1 bone matrix: max |C - Python| = %.2e" % d)
    ok &= d < 1e-5

    # 2. LBS
    rng = np.random.default_rng(7)
    n = 2000
    pts = rng.normal(size=(n, 3)).astype(np.float32) * 0.4
    misc = np.stack([
        np.array([S, E, E, W], np.float32),
        np.array([[0.05, -0.60, 0.10], [0.10, -0.58, 0.16],
                  [0.10, -0.58, 0.16], [-0.05, -1.02, 0.22]], np.float32)], 0)
    # two bones: upper (rest S->E) and forearm bent
    mats = np.stack([
        skin.bone_matrix(np.array(S, np.float32), np.array(E, np.float32),
                         np.array(S, np.float32), np.array(E, np.float32)),
        skin.bone_matrix(np.array(E, np.float32), np.array(W, np.float32),
                         np.array(E, np.float32), np.array([0.12, -1.00, 0.20], np.float32))], 0)
    Wt = rng.random((n, 2)).astype(np.float32)
    Wt /= Wt.sum(1, keepdims=True)
    c_out = wc.lbs(pts, Wt, mats)
    py_out = np.array(skin.deform([tuple(p) for p in pts], ["a", "b"], Wt, {"a": mats[0], "b": mats[1]}),
                      np.float32)
    d = float(np.abs(c_out - py_out).max())
    print("2 LBS: max |C - Python| = %.2e" % d)
    ok &= d < 5e-5

    # 3. DQS
    c_out = wc.dqs(pts, Wt, mats)
    py_out = np.array(dqs.deform([tuple(p) for p in pts], ["a", "b"], Wt, {"a": mats[0], "b": mats[1]}),
                      np.float32)
    d = float(np.abs(c_out - py_out).max())
    print("3 DQS: max |C - Python| = %.2e" % d)
    ok &= d < 5e-5

    # 4. the candy wrapper: blend identity with a 90 degree ROLL about the bone axis
    #    (a twist about its own axis is exactly what averaging matrices cannot represent)
    m1 = rot_y(0.0)
    m2 = rot_y(90.0)
    mm = np.stack([m1, m2], 0)
    probe = np.array([[0.085, 0.0, 0.0]], np.float32)
    w50 = np.array([[0.5, 0.5]], np.float32)
    lb = wc.lbs(probe, w50, mm)[0]
    dq = wc.dqs(probe, w50, mm)[0]
    r0 = math.hypot(float(probe[0, 0]), float(probe[0, 2]))
    rl = math.hypot(float(lb[0]), float(lb[2]))
    rd = math.hypot(float(dq[0]), float(dq[2]))
    print("4 twist 50/50: rest r=%.4f  LBS r=%.4f (%.0f%%)  DQS r=%.4f (%.0f%%)"
          % (r0, rl, 100 * rl / r0, rd, 100 * rd / r0))
    ok &= abs(rd - r0) < r0 * 0.05
    ok &= rl < r0 * 0.85

    # 5. timing on a real-sized load
    N = 200_000
    big = rng.normal(size=(N, 3)).astype(np.float32) * 0.5
    bigW = rng.random((N, 2)).astype(np.float32)
    bigW /= bigW.sum(1, keepdims=True)
    t0 = time.perf_counter()
    wc.lbs(big, bigW, mats)
    t_c = time.perf_counter() - t0
    t0 = time.perf_counter()
    skin.deform([tuple(p) for p in big[:20000]], ["a", "b"], bigW[:20000],
                {"a": mats[0], "b": mats[1]})
    t_py20k = time.perf_counter() - t0
    t_py = t_py20k * (N / 20000.0)
    print("5 %d vertices LBS: C %.1f ms   Python %.0f ms (extrapolated)   %.0fx"
          % (N, t_c * 1000, t_py * 1000, t_py / max(t_c, 1e-9)))
    ok &= t_c < t_py

    print("ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
