"""C11 rig maths: does twist distribution actually save the candy wrapper?

  1. swing-twist decomposes a rotation into a shortest-arc swing and a twist about the bone axis,
     and the two recompose to the original
  2. distribution splits a total twist across a chain, summing back to the total
  3. the prize: LBS collapses at 180 degrees (radius 0.00) but barely dents at the 60 degrees a
     three-bone distribution leaves at any one joint (radius 0.87)
  4. FK/IK blend hits both endpoints exactly

Run: PYTHONPATH=/opt/data/shitpost-box/pylibs python3 tests/test_c11_rig.py
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wubu3d_rigc as wr  # noqa: E402


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw,
                     aw * bw - ax * bx - ay * by - az * bz])


def axis_angle(axis, deg):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    s = math.sin(math.radians(deg) / 2)
    return np.array([a[0] * s, a[1] * s, a[2] * s, math.cos(math.radians(deg) / 2)])


def main():
    ok = True

    # 1. pure twist about the axis
    q = axis_angle([1, 0, 0], 60)
    swing, tw = wr.swing_twist(q, [1, 0, 0])
    print("1 pure twist: recovered %.2f deg (want 60.00), swing w %.6f (want 1.0)" % (tw, swing[3]))
    ok &= abs(tw - 60) < 1e-6 and abs(swing[3] - 1) < 1e-9

    # mixed: swing then twist, and recompose
    qs = axis_angle([0, 1, 0], 50)
    qt = axis_angle([1, 0, 0], 45)
    q = qmul(qs, qt)
    swing, tw = wr.swing_twist(q, [1, 0, 0])
    recomp = qmul(swing, axis_angle([1, 0, 0], tw))
    err = float(np.abs(recomp - q).max())
    print("  mixed: twist %.2f deg (want 45.00), recompose error %.1e" % (tw, err))
    ok &= abs(tw - 45) < 1e-6 and err < 1e-9

    # 2. distribution
    even = wr.twist_distribute(3, 180, mode=1)
    ramp = wr.twist_distribute(3, 180, mode=0)
    print("2 distribute 180 over 3 bones: even %s (sum %.1f), ramped %s (sum %.1f)"
          % (np.round(even, 1), even.sum(), np.round(ramp, 1), ramp.sum()))
    ok &= abs(even.sum() - 180) < 1e-9 and abs(ramp.sum() - 180) < 1e-9
    ok &= abs(even[0] - 60) < 1e-9

    # 3. the prize
    r180 = wr.lbs_radius_ratio(180)
    r60 = wr.lbs_radius_ratio(60)
    r90 = wr.lbs_radius_ratio(90)
    print("3 LBS radius at a joint: 180 deg %.3f (collapse)   90 deg %.3f   60 deg %.3f"
          % (r180, r90, r60))
    print("  a wrist twisting 180 with no twist bones keeps %.0f%% of its radius; spread over three"
          " bones the worst joint keeps %.0f%%" % (100 * r180, 100 * r60))
    ok &= r180 < 0.02 and r60 > 0.85

    # 4. chain composition + fk/ik blend
    rots = [axis_angle([0, 0, 1], 30), axis_angle([0, 0, 1], 30), axis_angle([0, 0, 1], 30)]
    world = wr.chain_world(rots)
    total = 2 * math.degrees(math.acos(min(1.0, abs(world[-1][3]))))
    print("4 three 30 deg bones in the same plane compose to %.1f deg" % total)
    ok &= abs(total - 90) < 1e-6

    fk = np.array([[0, 0, 0], [0, -1, 0], [0, -2, 0]], float)
    ik = np.array([[0, 0, 0], [0.4, -0.9, 0], [0.8, -1.6, 0]], float)
    b0 = wr.fkik_blend(fk, ik, 0.0)
    b1 = wr.fkik_blend(fk, ik, 1.0)
    b5 = wr.fkik_blend(fk, ik, 0.5)
    print("  fk/ik blend: w=0 error %.1e, w=1 error %.1e, w=0.5 midpoint error %.1e"
          % (np.abs(b0 - fk).max(), np.abs(b1 - ik).max(), np.abs(b5 - (fk + ik) / 2).max()))
    ok &= np.abs(b0 - fk).max() < 1e-12 and np.abs(b1 - ik).max() < 1e-12

    print("ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
