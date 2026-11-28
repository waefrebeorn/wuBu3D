"""navmesh_shim — ctypes wrapper for libnavmesh.so (inflate, A*, string-pull)."""

import ctypes

import numpy as np

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float

lib = ctypes.CDLL("/opt/data/work/wubu3d/libnavmesh.so")
lib.wubu_nav_inflate.argtypes = [_P, _I, _I, _I]
lib.wubu_nav_path.argtypes = [_P, _I, _I, _I, _I, _I, _I, _P, _I, _P]
lib.wubu_nav_path.restype = _I
lib.wubu_nav_smooth.argtypes = [_P, _I, _I, _P, _I, _F]
lib.wubu_nav_smooth.restype = _I


def inflate(grid, w, h, radius):
    lib.wubu_nav_inflate(grid.ctypes.data_as(_P), w, h, radius)


def path(grid, w, h, sx, sy, tx, ty, out, max_pts):
    exp = ctypes.c_int(0)
    n = lib.wubu_nav_path(grid.ctypes.data_as(_P), w, h, sx, sy, tx, ty,
                          out.ctypes.data_as(_P), max_pts, ctypes.byref(exp))
    return n


def smooth(grid, w, h, pts, n, radius):
    return lib.wubu_nav_smooth(grid.ctypes.data_as(_P), w, h, pts.ctypes.data_as(_P), n,
                               float(radius))


def reachable(grid, w, h, sx, sy):
    """Flood fill count, for checking that a bake actually connects the room."""
    seen = np.zeros((h, w), np.uint8)
    if grid[sy, sx] == 0:
        return 0
    stack = [(sx, sy)]
    seen[sy, sx] = 1
    n = 0
    while stack:
        x, y = stack.pop()
        n += 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny, nx] and grid[ny, nx] > 0:
                seen[ny, nx] = 1
                stack.append((nx, ny))
    return n
