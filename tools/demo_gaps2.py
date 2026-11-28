"""demo_gaps2 — cloth, navmesh, and fur shells, each with the number that says it works.

    cloth     verlet cape on a 24x16 grid, pinned along the top edge, solved 120 steps; the metric is
              mean stretch as a fraction of rest length (a net that goes 900% is not a cape)
    navmesh   A* on a 96x96 cost field with a wall, inflated by an agent radius; the metric is path
              length against the straight line, and nodes expanded against the free-cell count
    fur       3 shells over the head with per-shell alpha, which is how a blocky character gets a
              hairline without a strand system
"""

import ctypes

import numpy as np
from PIL import Image

import cast_blocky as CB
import render_shaded as RS
import r15

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float

cl = ctypes.CDLL("/opt/data/work/wubu3d/libcloth.so")
cl.wubu_cloth_step.argtypes = [_P, _I, _P, _P, _P, _I, _F, _F, _F, _F, _F, _I, _F, _I]
cl.wubu_cloth_stretch.argtypes = [_P, _P, _P, _P, _I]
cl.wubu_cloth_stretch.restype = ctypes.c_float
cl.wubu_cloth_floor.argtypes = [_P, _I, _F, _F]
cl.wubu_cloth_floor.restype = _I

nv = ctypes.CDLL("/opt/data/work/wubu3d/libnavmesh.so")
nv.wubu_nav_inflate.argtypes = [_P, _I, _I, _I]
nv.wubu_nav_path.argtypes = [_P, _I, _I, _I, _I, _I, _I, _P, _I, _P]
nv.wubu_nav_smooth.argtypes = [_P, _I, _I, _P, _I, _F]


def cloth_demo():
    GW, GH = 24, 16
    n = GW * GH
    p = np.zeros((n, 7), np.float32)
    for j in range(GH):
        for i in range(GW):
            k = j * GW + i
            p[k, 0] = -0.6 + 1.2 * i / (GW - 1)
            p[k, 1] = 1.55 - 0.02 * j
            p[k, 2] = 0.55 + 0.60 * j / (GH - 1)
            p[k, 3:6] = p[k, 0:3]
            p[k, 6] = 0.0 if j == 0 else 1.0        # pinned top edge
    ca, cb, rest = [], [], []
    for j in range(GH):
        for i in range(GW):
            k = j * GW + i
            for di, dj in ((1, 0), (0, 1)):
                ni, nj = i + di, j + dj
                if ni >= GW or nj >= GH:
                    continue
                m = nj * GW + ni
                ca.append(k); cb.append(m)
                rest.append(float(np.linalg.norm(p[k, 0:3] - p[m, 0:3])))
    ca = np.asarray(ca, np.int32); cb = np.asarray(cb, np.int32); rest = np.asarray(rest, np.float32)
    print("cloth: %d particles, %d constraints" % (n, len(ca)))

    hits = 0
    for s in range(120):
        cl.wubu_cloth_step(p.ctypes.data_as(_P), n, ca.ctypes.data_as(_P), cb.ctypes.data_as(_P),
                           rest.ctypes.data_as(_P), len(ca), 1.0 / 60.0, 0.0, -9.8, 0.0,
                           0.994, 6, 0.35, 5)
        hits += int(cl.wubu_cloth_floor(p.ctypes.data_as(_P), n, 0.02, 0.55))

    st = float(cl.wubu_cloth_stretch(p.ctypes.data_as(_P), ca.ctypes.data_as(_P),
                                     cb.ctypes.data_as(_P), rest.ctypes.data_as(_P), len(ca)))
    low = float(p[:, 1].min())
    print("cloth: mean stretch %.3f%% of rest, lowest y %.3f, %d floor contacts"
          % (100 * st, low, hits))
    return p, GW, GH


def nav_demo():
    W = H = 96
    g = np.full((H, W), 255, np.uint8)
    g[:, 40:48] = 0                      # a wall with one gap
    g[70:78, 40:48] = 255                # the gap
    g[10:30, 60:80] = 0                  # a block
    nv.wubu_nav_inflate(g.ctypes.data_as(_P), W, H, 2)
    pts = np.zeros(4096 * 2, np.float32)
    exp = ctypes.c_int(0)
    n = nv.wubu_nav_path(g.ctypes.data_as(_P), W, H, 6, 6, 88, 88,
                         pts.ctypes.data_as(_P), 4096, ctypes.byref(exp))
    raw = n
    n = nv.wubu_nav_smooth(g.ctypes.data_as(_P), W, H, pts.ctypes.data_as(_P), n, 1.0)
    P = pts[: n * 2].reshape(-1, 2)
    L = float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum()) if n > 1 else 0.0
    straight = float(np.hypot(88 - 6, 88 - 6))
    free = int((g > 0).sum())
    print("navmesh: %d -> %d points, path %.1f vs straight %.1f (ratio %.2f), %d/%d cells expanded"
          % (raw, n, L, straight, L / straight, exp.value, free))
    return g, P


def fur_demo():
    """Shell fur: offset copies of the head box, shrinking and lightening, with a per-shell alpha.
    It is the cheapest way to a hairline and it composites with the same pipeline."""
    f, _ = r15.build({"Head": (0, -6, 0)}, H=1.0, hair=(30, 40, 74))
    head = [(q, c, o) for q, c, o in f if min(v[1] for v in q) > 0.62 and max(abs(v[0]) for v in q) < 0.24]
    print("fur: head region has %d faces" % len(head))
    panels = []
    for shells in (1, 4, 8):
        g = []
        for s in range(shells):
            k = s / max(1, shells - 1) if shells > 1 else 0.0
            off = 0.030 * k          # hair stands off the scalp by up to 3 cm at this scale
            taper = 1.0 - 0.10 * k   # and the tips pull in, or the head just inflates
            shade = 1.0 + 0.55 * k
            for q, c, o in head:
                cen = np.array(q, np.float64).mean(0)
                e1 = np.array(q[1]) - np.array(q[0])
                e2 = np.array(q[3]) - np.array(q[0])
                nvec = np.cross(e1, e2)
                ln = np.linalg.norm(nvec)
                nvec = nvec / ln if ln > 1e-9 else np.array([0.0, 1.0, 0.0])
                qq = []
                for v in q:
                    p = cen + (np.array(v, np.float64) - cen) * taper + nvec * off
                    qq.append(tuple(float(x) for x in p))
                cc = tuple(min(255, int(x * shade)) for x in c)
                g.append((qq, cc, o))
        cam_eye = (0.0, 0.62, 1.95)
        cam_tgt = (0.0, 0.55, 0.0)
        im = RS.aa(g, cam_eye, cam_tgt, 240, 300, ss=2, fov=34, flat=[], bg=(236, 232, 226),
                   lights=[(0.6, 1.6, 2.2, 2.0)], ambient=0.5, gain=0.45, rim=0.25)
        panels.append(im.convert("RGB"))
        print("fur: %d shells, %d faces" % (shells, len(head) * shells))
    sh = Image.new("RGB", (240 * 3, 300), (236, 232, 226))
    for i, im in enumerate(panels):
        sh.paste(im, (i * 240, 0))
    sh.save("/opt/data/cache/scratch/fur_shells.png")


if __name__ == "__main__":
    cloth_demo()
    nav_demo()
    fur_demo()
