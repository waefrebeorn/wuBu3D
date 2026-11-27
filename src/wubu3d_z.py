"""wubu3d_z — ctypes driver for libwubuzbuf.so (z-buffered raster + cylindrical decals).

Same contract as raster.py, so the two can be diffed and the C path swapped in wherever the Python
one is used today.

    import wubu3d_z as wz
    rgb = np.zeros((h, w, 3), np.uint8); zb = np.full((h, w), np.inf, np.float32)
    wz.clear(rgb, zb, (24, 26, 34))
    wz.draw(rgb, zb, pts, depth, cols)       # pts (n,3,2), depth (n,3), cols (n,3) uint8
    wz.decal_cyl(rgb, zb, tex_rgba, cam, centre, half_h, theta_max)
"""

import ctypes
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wubuzbuf.c")
_LIB = None


def build(force=False):
    so = os.path.join(_HERE, "libwubuzbuf.so")
    if force or not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(SRC):
        tmp = so + ".tmp"
        subprocess.run(["cc", "-O3", "-std=c11", "-shared", "-fPIC", "-o", tmp, SRC, "-lm"],
                       check=True)
        os.replace(tmp, so)
    return so


def _get_lib():
    global _LIB
    if _LIB is not None:
        return _LIB
    lib = ctypes.CDLL(build())
    U8 = ctypes.POINTER(ctypes.c_uint8)
    F = ctypes.POINTER(ctypes.c_float)
    lib.wb_clear.argtypes = [U8, F, ctypes.c_int, ctypes.c_int,
                             ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    lib.wb_draw_tris.argtypes = [U8, F, ctypes.c_int, ctypes.c_int, F, F, U8, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int)]
    lib.wb_decal_cyl.argtypes = [U8, F, ctypes.c_int, ctypes.c_int, U8, ctypes.c_int, ctypes.c_int,
                                 F, ctypes.c_float, ctypes.c_float, F, F, ctypes.c_float,
                                 ctypes.c_float, ctypes.c_float]
    lib.wb_decal_cyl.restype = ctypes.c_int
    _LIB = lib
    return lib


def _u8(a):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))


def _f(a):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_float))


def clear(rgb, zb, bg):
    """rgb/zb must be C-contiguous and owned by the caller: the C side writes in place, and
    np.ascontiguousarray would silently hand it a copy that is thrown away."""
    lib = _get_lib()
    h, w = zb.shape
    if not rgb.flags["C_CONTIGUOUS"] or not zb.flags["C_CONTIGUOUS"]:
        raise ValueError("rgb and zb must be C-contiguous")
    lib.wb_clear(_u8(rgb), _f(zb), w, h, int(bg[0]), int(bg[1]), int(bg[2]))


def draw(rgb, zb, pts, depth, cols):
    lib = _get_lib()
    h, w = zb.shape
    P = np.ascontiguousarray(pts, np.float32).reshape(-1, 6)
    D = np.ascontiguousarray(depth, np.float32).reshape(-1, 3)
    C = np.ascontiguousarray(cols, np.uint8).reshape(-1, 3)
    n = P.shape[0]
    lib.wb_draw_tris(_u8(rgb), _f(zb), w, h, _f(P), _f(D), _u8(C), n, None)


def decal_cyl(rgb, zb, tex, cam, centre, half_h, theta_max):
    lib = _get_lib()
    h, w = zb.shape
    T = np.ascontiguousarray(tex, np.uint8)
    th, tw = T.shape[:2]
    M = np.ascontiguousarray(np.asarray(cam.M, np.float32).reshape(9), np.float32)
    eye = np.ascontiguousarray(np.asarray(cam.eye, np.float32).reshape(3), np.float32)
    c = np.ascontiguousarray(np.asarray(centre, np.float32).reshape(3), np.float32)
    return lib.wb_decal_cyl(_u8(rgb), _f(zb), w, h, _u8(T), tw, th, _f(c),
                            float(half_h), float(theta_max), _f(M), _f(eye),
                            float(cam.f), float(cam.cx), float(cam.cy))
