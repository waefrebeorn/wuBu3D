"""demo_instancing — 756 scattered boxes: object layer vs instanced arrays, timed and compared."""

import time

import numpy as np

import blocky as B
import cast_blocky as CB
import instancing as INS
import render_shaded as RS


def poisson(n_max, radius, x0, y0, x1, y1, seed=7, k=30):
    rng = np.random.default_rng(seed)
    cell = radius / np.sqrt(2)
    gw, gh = int((x1 - x0) / cell) + 1, int((y1 - y0) / cell) + 1
    grid = -np.ones((gh, gw), np.int64)
    pts = [np.array([(x0 + x1) / 2, (y0 + y1) / 2])]
    active = [0]
    while active and len(pts) < n_max:
        i = active[rng.integers(len(active))]
        ok = False
        for _ in range(k):
            ang = rng.uniform(0, 2 * np.pi)
            r = rng.uniform(radius, 2 * radius)
            p = pts[i] + np.array([np.cos(ang), np.sin(ang)]) * r
            if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
                continue
            gi, gj = int((p[0] - x0) / cell), int((p[1] - y0) / cell)
            free = True
            for di in (-2, -1, 0, 1, 2):
                for dj in (-2, -1, 0, 1, 2):
                    ni, nj = gi + di, gj + dj
                    if 0 <= ni < gw and 0 <= nj < gh and grid[nj, ni] >= 0:
                        if np.linalg.norm(pts[grid[nj, ni]] - p) < radius:
                            free = False
                            break
                if not free:
                    break
            if free:
                grid[gj, gi] = len(pts)
                pts.append(p)
                active.append(len(pts) - 1)
                ok = True
                break
        if not ok:
            active.remove(i)
    return np.array(pts)


def main():
    pts = poisson(900, 0.16, -3.2, -2.6, 3.2, 2.6)
    n = len(pts)
    rng = np.random.default_rng(4)
    scl = rng.uniform(0.5, 1.3, n)
    rot = rng.uniform(0, 2 * np.pi, n)
    print("scatter: %d instances, %d quads" % (n, n * 6))

    cam = RS.B.Cam((0.0, 3.0, 4.4), (0.0, 0.0, 0.0), fov=52, w=480, h=640)
    kw = dict(bg=(96, 78, 54), lights=[(3.0, 6.0, 2.0, 3.0)], ambient=0.38, gain=0.5, rim=0.05)

    t0 = time.perf_counter()
    faces = [(q, c, o) for q, c, o in B.box(0, -0.04, 0, 7.0, 0.08, 6.0, (96, 78, 54))]
    for k in range(n):
        x, y = float(pts[k][0]), float(pts[k][1])
        h = 0.35 * scl[k]
        faces += [(q, c, o) for q, c, o in
                  B.box(x, h / 2, y, 0.05 * scl[k], h, 0.05 * scl[k], (128, 106, 78),
                        rot=(0, rot[k], 0))]
    t_build_obj = time.perf_counter() - t0
    t0 = time.perf_counter()
    a = RS.aa(faces, cam.eye, (0, 0, 0), 480, 640, ss=1, fov=52, flat=[], **kw)
    t_obj = time.perf_counter() - t0

    t0 = time.perf_counter()
    centres = np.column_stack([pts[:, 0], 0.35 * scl / 2, pts[:, 1]])
    half = np.column_stack([0.05 * scl, 0.35 * scl / 2, 0.05 * scl])
    Q, cols, nrm = INS.boxes(centres, half, (128, 106, 78), rot)
    floorQ, floorC, floorN = INS.boxes([[0, -0.04, 0]], [3.5, 0.04, 3.0], (96, 78, 54))
    Q = np.concatenate([floorQ, Q]); cols = np.concatenate([floorC, cols])
    nrm = np.concatenate([floorN, nrm])
    t_build_arr = time.perf_counter() - t0

    t0 = time.perf_counter()
    rgb = np.zeros((640, 480, 3), np.uint8); rgb[:, :] = kw["bg"]
    zb = np.full((640, 480), np.inf, np.float32)
    RS._draw_arrays(rgb, zb, cam, 480, 640, Q, cols, nrm=nrm, lights=kw["lights"],
                    ambient=kw["ambient"], gain=kw["gain"], rim=kw["rim"])
    t_arr = time.perf_counter() - t0

    A = np.asarray(a, np.float32); IMG = rgb.astype(np.float32)
    print("build: object %.1f ms, arrays %.1f ms (%.0fx)" % (t_build_obj * 1e3, t_build_arr * 1e3,
                                                            t_build_obj / max(t_build_arr, 1e-9)))
    print("draw : object %.1f ms, arrays %.1f ms (%.2fx)" % (t_obj * 1e3, t_arr * 1e3,
                                                             t_obj / max(t_arr, 1e-9)))
    print("frame diff mean %.2f, px>10 %d" % (np.abs(A - IMG).mean(),
                                              int((np.abs(A - IMG).max(2) > 10).sum())))


if __name__ == "__main__":
    main()
