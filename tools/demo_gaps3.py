"""demo_gaps3 — two more gaps: occlusion culling, and an arm that can reach.

Cull: a wall with sixty boxes behind it. Culling must remove most of them and change ZERO pixels.
IK:   a five-joint arm reaching twenty random targets — tip error in mm, bone drift in mm.
"""

import time

import numpy as np
from PIL import Image

import blocky as B
import cast_blocky as CB
import ik
import occl
import render_shaded as RS


def wall_scene():
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, 0, 8.0, 0.1, 9.0, (86, 78, 68))]
    f += [(q, c, o) for q, c, o in CB.box(0, 1.2, -2.6, 5.0, 2.4, 0.14, (104, 96, 86))]   # occluder
    rng = np.random.default_rng(5)
    for i in range(60):
        x = float(rng.uniform(-3.4, 3.4))
        y = float(rng.uniform(0.15, 1.9))
        z = float(rng.uniform(-5.6, -3.4))
        s = float(rng.uniform(0.16, 0.30))
        f += [(q, c, o) for q, c, o in CB.box(x, y, z, s, s, s, (150, 130, 96))]
    return f


def test_cull():
    w, h = 420, 300
    f = wall_scene()
    cam_eye, cam_tgt = (0.0, 1.5, 3.2), (0.0, 1.0, -3.0)
    kw = dict(ss=1, fov=52, flat=[], bg=(22, 21, 26), lights=[(1.5, 3.5, 2.0, 9.0)],
              ambient=0.34, gain=0.5, rim=0.0)

    t0 = time.time()
    full = RS.aa(f, cam_eye, cam_tgt, w, h, **kw).convert("RGB")
    t_full = time.time() - t0
    zb = np.array(RS._LAST_ZB, np.float32)
    cam = RS.B.Cam(cam_eye, cam_tgt, fov=52, w=w, h=h)

    # depth of everything in front of the boxes: cull against the frame we already drew minus the boxes
    keep, st = occl.cull(f, cam, zb, w, h, step=3)
    kept_faces = [face for face, k in zip(f, keep) if k]
    t0 = time.time()
    part = RS.aa(kept_faces, cam_eye, cam_tgt, w, h, **kw).convert("RGB")
    t_part = time.time() - t0

    A = np.asarray(full, np.int16)
    Bm = np.asarray(part, np.int16)
    d = np.abs(A - Bm).max(2)
    print("cull: kept %d/%d (%d culled, %.0f%%), %.0f -> %.0f ms"
          % (st["kept"], st["total"], st["culled"], 100 * st["culled"] / max(1, st["total"]),
             t_full * 1000, t_part * 1000))
    print("      pixels changed: %d (max %.0f levels) — must be 0" % (int((d > 0).sum()), float(d.max())))
    sheet = Image.new("RGB", (w * 2, h), (22, 21, 26))
    sheet.paste(full, (0, 0))
    sheet.paste(part, (w, 0))
    sheet.save("/opt/data/cache/scratch/cull_sheet.png")
    return float(d.max())


def test_ik():
    rng = np.random.default_rng(3)
    chain0 = np.array([[0, 0, 0], [0.0, -0.28, 0.0], [0.0, -0.54, 0.0],
                       [0.0, -0.78, 0.0], [0.0, -1.0, 0.0]], np.float64)
    errs, drifts = [], []
    for _ in range(20):
        t = np.array([rng.uniform(-0.7, 0.7), rng.uniform(-0.5, 0.35), rng.uniform(-0.5, 0.5)])
        P, e, unreachable = ik.fabrik(chain0, t)
        r = ik.report(chain0, P, t)
        errs.append(r["tip_error_mm"])
        drifts.append(r["bone_drift_mm"])
    print("ik: 20 targets, tip error median %.3f mm, worst %.2f mm; bone drift worst %.2e mm"
          % (float(np.median(errs)), float(max(errs)), float(max(drifts))))

    # and one straight-up unreachable target, which must not explode
    t = np.array([2.0, 0.0, 0.0])
    P, e, un = ik.fabrik(chain0, t)
    print("ik: unreachable target flagged=%s, tip sits %.2f mm short of it" % (un, e * 1000))


def main():
    worst = test_cull()
    test_ik()
    print("culling changed at most %.0f levels of the frame" % worst)


if __name__ == "__main__":
    main()
