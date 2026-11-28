"""bake — mesh to navmesh grid, the half of pathfinding that `navmesh.c` did not do.

`navmesh.c` solves A* on a cost field; the open row was "mesh -> grid". The bake is a rasterisation:
walkable faces (normal up) write free cells and a height, steep faces write blocked cells. Two rules
that matter and are easy to get wrong:

- **Slope is per face, not per vertex.** A quad whose normal is up is floor even if its corners differ
  in height; a quad with a sideways normal is wall even if it is only 3 cm tall.
- **Blocked beats free.** Paint free first, then blocked, or a wall crossing a floor cell is erased by
  the floor and the agent walks through it.
"""

import numpy as np


def bake_navmesh(faces, res=96, size=6.0, step_up=0.35):
    """Returns (grid uint8 0=blocked 255=free, height float32, x0, z0, cell)."""
    grid = np.zeros((res, res), np.uint8)
    height = np.full((res, res), -1e9, np.float32)
    cell = size / res
    x0 = -size / 2
    z0 = -size / 2

    # A vertical wall has ZERO footprint from above: its side faces project to a line, so a bake that
    # paints "wall faces" blocked marks nothing and every room comes out 100% free. The right rule is
    # occupancy: a cell is walkable if the LOWEST surface there is within a step of the floor and
    # nothing sits above it.
    low = np.full((res, res), 1e9, np.float32)
    high = np.full((res, res), -1e9, np.float32)

    def _raster(quads, fn):
        for a in quads:
            tris = ((a[0], a[1], a[2]), (a[0], a[2], a[3]))
            for t in tris:
                lo = np.minimum(np.minimum(t[0], t[1]), t[2])
                hi = np.maximum(np.maximum(t[0], t[1]), t[2])
                i0 = max(0, int((lo[0] - x0) / cell))
                i1 = min(res - 1, int((hi[0] - x0) / cell) + 1)
                j0 = max(0, int((lo[2] - z0) / cell))
                j1 = min(res - 1, int((hi[2] - z0) / cell) + 1)
                if i1 < i0 or j1 < j0:
                    continue
                p0, p1, p2 = t
                den = ((p1[2] - p2[2]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[2] - p2[2]))
                if abs(den) < 1e-12:
                    continue
                for j in range(j0, j1 + 1):
                    cz = z0 + (j + 0.5) * cell
                    for i in range(i0, i1 + 1):
                        cx = x0 + (i + 0.5) * cell
                        w0 = ((p1[2] - p2[2]) * (cx - p2[0]) + (p2[0] - p1[0]) * (cz - p2[2])) / den
                        w1 = ((p2[2] - p0[2]) * (cx - p2[0]) + (p0[0] - p2[0]) * (cz - p2[2])) / den
                        w2 = 1.0 - w0 - w1
                        if w0 < -1e-6 or w1 < -1e-6 or w2 < -1e-6:
                            continue
                        fn(i, j, w0 * p0[1] + w1 * p1[1] + w2 * p2[1])

    def _occ(i, j, y):
        if y < low[j, i]:
            low[j, i] = y
        if y > high[j, i]:
            high[j, i] = y

    _raster([np.array(q, np.float64) for q, c, o in faces], _occ)

    seen = low < 1e8
    floor_h = float(np.median(low[seen])) if seen.any() else 0.0
    walkable = seen & (low <= floor_h + step_up) & (high <= floor_h + step_up)
    grid = np.where(walkable, np.uint8(255), np.uint8(0))
    height = np.where(walkable, low, np.float32(-1e9))
    return grid, height, x0, z0, cell


def path_length(pts):
    p = np.asarray(pts, np.float64).reshape(-1, 2)
    if len(p) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())
