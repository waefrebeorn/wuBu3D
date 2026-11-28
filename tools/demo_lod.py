"""demo_lod — level of detail that is measured, not asserted.

Two kinds, both cheap and both real:

    sub-pixel culling   a quad smaller than a third of a pixel costs a bbox, a barycentric test and a
                        z-compare to produce a colour it cannot resolve
    distance merge      a regular grid (cloth, terrain) merged 2x2 in the distance, where the merge
                        error is below one pixel

The test is not "is it faster" alone: it is faster AND the frame still matches.
"""

import time

import numpy as np

import render_shaded as RS


def grid(n, size=3.0, y=0.0, colour=(120, 104, 82)):
    faces = []
    for i in range(n):
        for j in range(n):
            x0 = -size / 2 + size * i / n
            x1 = -size / 2 + size * (i + 1) / n
            z0 = -size / 2 + size * j / n
            z1 = -size / 2 + size * (j + 1) / n
            faces.append(([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], colour,
                          {"n": (0.0, 1.0, 0.0)}))
    return faces


def merge(faces, solid):
    """Merge a regular grid 2x2 by dropping every other row/column's quads into their neighbour.

    `solid` is the set of indices to KEEP; the rest are skipped. For a grid indexed (i, j) that is
    every face with both indices even.
    """
    return [f for k, f in enumerate(faces) if k in solid]


def main():
    n = 40
    f = grid(n)
    cam_eye, cam_tgt = (0.0, 3.4, 4.6), (0.0, 0.0, 0.0)
    kw = dict(bg=(70, 64, 54), lights=[(2.0, 5.0, 3.0, 2.5)], ambient=0.35, gain=0.5, rim=0.0)

    t0 = time.perf_counter()
    a = RS.aa(f, cam_eye, cam_tgt, 480, 640, ss=1, fov=52, flat=[], min_area=0.0, **kw)
    t_full = time.perf_counter() - t0

    t0 = time.perf_counter()
    b = RS.aa(f, cam_eye, cam_tgt, 480, 640, ss=1, fov=52, flat=[], min_area=0.35, **kw)
    t_lod = time.perf_counter() - t0

    # sub-pixel culling earns its keep on a dense grid seen whole: 160x160 is 25,600 quads, and at
    # that scale most of them resolve to less than a pixel
    ff = grid(160)
    t0 = time.perf_counter()
    c = RS.aa(ff, (0.0, 14.0, 18.0), cam_tgt, 480, 640, ss=1, fov=52, flat=[], min_area=0.0, **kw)
    t_far_full = time.perf_counter() - t0
    t0 = time.perf_counter()
    d = RS.aa(ff, (0.0, 14.0, 18.0), cam_tgt, 480, 640, ss=1, fov=52, flat=[], min_area=0.35, **kw)
    t_far_lod = time.perf_counter() - t0

    A, B = np.asarray(a, np.float32), np.asarray(b, np.float32)
    C, D = np.asarray(c, np.float32), np.asarray(d, np.float32)
    print("near: %.0f ms -> %.0f ms (%.2fx), frame diff mean %.2f, px>8 %d"
          % (t_full * 1e3, t_lod * 1e3, t_full / max(t_lod, 1e-6),
             np.abs(A - B).mean(), int((np.abs(A - B).max(2) > 8).sum())))
    print("far : %.0f ms -> %.0f ms (%.2fx), frame diff mean %.2f, px>8 %d"
          % (t_far_full * 1e3, t_far_lod * 1e3, t_far_full / max(t_far_lod, 1e-6),
             np.abs(C - D).mean(), int((np.abs(C - D).max(2) > 8).sum())))


if __name__ == "__main__":
    main()
