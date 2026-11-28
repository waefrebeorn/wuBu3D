"""demo_bake — the whole pathfinding stack: bake a room to a grid, inflate, A*, smooth, walk it.

The scene is a floor with two walls forming a gap and a box obstacle, which is the case where a
straight line is illegal and a bad bake turns a corridor into a wall.
"""

import ctypes

import numpy as np

import bake
import cast_blocky as CB
import navmesh_shim as NV


def room():
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, 0, 6.0, 0.1, 6.0, (108, 92, 70))]      # floor
    f += [(q, c, o) for q, c, o in CB.box(-1.2, 0.6, 0.6, 0.3, 1.2, 3.0, (86, 74, 58))]    # wall A
    f += [(q, c, o) for q, c, o in CB.box(1.2, 0.6, -0.9, 0.3, 1.2, 3.0, (86, 74, 58))]    # wall B
    f += [(q, c, o) for q, c, o in CB.box(0.2, 0.2, 1.6, 0.8, 0.4, 0.8, (120, 96, 64))]    # crate
    return f


def main():
    f = room()
    grid, height, x0, z0, cell = bake.bake_navmesh(f, res=96, size=6.0)
    print("bake: %d/%d cells free (%.1f%%), floor height range %.2f..%.2f"
          % (int((grid > 0).sum()), grid.size, 100.0 * (grid > 0).mean(),
             float(height[grid > 0].min()) if (grid > 0).any() else 0.0,
             float(height[grid > 0].max()) if (grid > 0).any() else 0.0))

    g = grid.copy()
    NV.inflate(g, 96, 96, 2)
    pts = np.zeros(4096 * 2, np.float32)
    n = NV.path(g, 96, 96, 8, 8, 88, 88, pts, 4096)
    raw = n
    n = NV.smooth(g, 96, 96, pts, n, 1.0)
    P = pts[: n * 2].reshape(-1, 2)
    L = bake.path_length(P)
    straight = float(np.hypot(88 - 8, 88 - 8)) * cell
    print("path: %d -> %d points, %.2f world units vs straight %.2f (ratio %.2f)"
          % (raw, n, L * cell, straight, L * cell / straight))

    # does the direct line actually hit a wall? sample the SEGMENT, not one row through the middle:
    # the first version scanned a single row and called a diagonal that threads the gap "blocked"
    p0, p1 = P[0], P[-1]
    steps = 400
    hit = 0
    for s in range(steps + 1):
        t = s / steps
        cx = int(round(p0[0] + (p1[0] - p0[0]) * t))
        cy = int(round(p0[1] + (p1[1] - p0[1]) * t))
        if 0 <= cx < 96 and 0 <= cy < 96 and grid[cy, cx] == 0:
            hit += 1
    print("direct line: %d/%d samples inside a wall (%s)"
          % (hit, steps + 1, "clear, the diagonal threads the gap" if hit == 0 else "blocked"))

    # a goal that IS behind a wall: the path must be longer than the straight line, and that ratio is
    # the only honest evidence that the detour is real
    pts2 = np.zeros(4096 * 2, np.float32)
    n2 = NV.path(g, 96, 96, 8, 88, 88, 12, pts2, 4096)
    n2 = NV.smooth(g, 96, 96, pts2, n2, 1.0)
    P2 = pts2[: n2 * 2].reshape(-1, 2)
    L2 = bake.path_length(P2)
    st2 = float(np.hypot(88 - 8, 12 - 88)) * cell
    print("blocked goal: %.2f units vs straight %.2f (detour %.2fx)"
          % (L2 * cell, st2, (L2 * cell) / st2))


if __name__ == "__main__":
    main()
