"""bench — where the frame time actually goes, before optimising anything.

Rule: measure the split between C work and Python-per-triangle overhead. The renderer calls
`shade_tri` once per triangle from a Python loop, so a 10k-triangle frame makes 10k ctypes calls;
if that is the bottleneck, no amount of C tuning helps and the fix is a batch entry point.
"""

import ctypes
import time

import numpy as np

import cast_blocky as CB
import render_shaded as RS

_P = ctypes.c_void_p
_lib = RS._lib


def scene(nt):
    """A grid of boxes: n boxes, 12 quads each, 288 triangles per 24 boxes."""
    f = []
    side = int(np.sqrt(nt))
    for i in range(side):
        for j in range(side):
            f += [(q, c, o) for q, c, o in
                  CB.box(-1.4 + 2.8 * i / side, 0.2, -1.4 + 2.8 * j / side, 0.06, 0.6, 0.06,
                         (120, 100, 80))]
    return f


def bench(n):
    f = scene(n)
    tris = sum(1 for _ in f) * 2
    t0 = time.perf_counter()
    im = RS.aa(f, (0.0, 0.9, 3.2), (0.0, 0.5, 0.0), 480, 640, ss=1, fov=46, flat=[],
                   bg=(40, 40, 40), lights=[(0.8, 1.4, 1.6, 2.0)], ambient=0.4, gain=0.5, rim=0.1)
    dt = time.perf_counter() - t0
    print("%5d boxes %6d tris: %6.2f ms total, %5.1f us per triangle, %.1f us per triangle+overhead"
          % (n, tris, dt * 1e3, dt * 1e6 / tris, dt * 1e6 / tris))
    return dt, tris


def bench_c_only():
    """Time the same triangle count with the Python loop removed: hand the same vertex block to
    shade_tri in a tight loop so the difference is pure ctypes overhead."""
    n = 2000
    vv = np.zeros((3, 11), np.float32)
    vv[0] = [0, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0]
    vv[1] = [10, 0, 2, 0.2, 0, 0, 0, 0, 1, 1, 0]
    vv[2] = [0, 10, 2, 0, 0.2, 0, 0, 0, 1, 0, 1]
    rgb = np.zeros((640, 480, 3), np.uint8)
    zb = np.full((640, 480), np.inf, np.float32)
    L = np.array([[0.8, 1.4, 1.6, 2.0]], np.float32)
    c = np.array([120, 100, 80], np.float32)
    eye = np.array([0, 0.9, 3.2], np.float32)
    t0 = time.perf_counter()
    for _ in range(n):
        _lib.shade_tri(_P(rgb.ctypes.data), _P(zb.ctypes.data), 480, 640, _P(vv.ctypes.data),
                       _P(c.ctypes.data), _P(L.ctypes.data), 1, 0.4, 0.5, 0.1, _P(eye.ctypes.data))
    dt = time.perf_counter() - t0
    print("bare ctypes call: %5.1f us per shade_tri (200x200 px triangle)" % (dt * 1e6 / n))


if __name__ == "__main__":
    for n in (25, 100, 400):
        bench(n)
    bench_c_only()
