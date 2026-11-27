"""wubu3d_mesh — ctypes driver for libwubumesh.so (weld, crease normals, QEM decimation).

    import wubu3d_mesh as wm
    remap, uniq = wm.weld(pos, cell=1e-4)
    n = wm.corner_normals(pos, tri, cos_threshold=0.5)
    tri2, faces = wm.simplify(pos, tri, target=500)
"""

import ctypes
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wubumesh.c")
_LIB = None
F = ctypes.POINTER(ctypes.c_float)
U = ctypes.POINTER(ctypes.c_uint32)


def build(force=False):
    so = os.path.join(_HERE, "libwubumesh.so")
    if force or not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(SRC):
        tmp = so + ".tmp"
        subprocess.run(["cc", "-O2", "-std=c11", "-shared", "-fPIC", "-o", tmp, SRC, "-lm"],
                       check=True)
        os.replace(tmp, so)
    return so


def load():
    global _LIB
    lib = ctypes.CDLL(build())
    lib.wb_weld.argtypes = [F, ctypes.c_int, ctypes.c_float, U, F]
    lib.wb_weld.restype = ctypes.c_int
    lib.wb_face_normals.argtypes = [F, U, ctypes.c_int, F]
    lib.wb_corner_normals.argtypes = [F, U, ctypes.c_int, ctypes.c_int, ctypes.c_float, F]
    lib.wb_qem_simplify.argtypes = [F, U, ctypes.c_int, U, ctypes.POINTER(ctypes.c_int),
                                    ctypes.c_int, ctypes.c_int]
    lib.wb_qem_simplify.restype = ctypes.c_int
    _LIB = lib
    return lib


def _f(a):
    return np.ascontiguousarray(a, dtype=np.float32)


def _u(a):
    return np.ascontiguousarray(a, dtype=np.uint32)


def _p32(a):
    return a.ctypes.data_as(F)


def weld(pos, cell=1e-4):
    lib = _LIB or load()
    P = _f(pos)
    n = P.shape[0]
    remap = np.zeros(n, np.uint32)
    out = np.zeros((n, 3), np.float32)
    uniq = lib.wb_weld(_p32(P), n, float(cell), remap.ctypes.data_as(U),
                       out.ctypes.data_as(F))
    return remap, out[:uniq]


def face_normals(pos, tri):
    lib = _LIB or load()
    P = _f(pos)
    T = _u(tri)
    out = np.zeros((T.shape[0], 3), np.float32)
    lib.wb_face_normals(_p32(P), T.ctypes.data_as(U), T.shape[0], _p32(out))
    return out


def corner_normals(pos, tri, cos_threshold=0.5):
    lib = _LIB or load()
    P = _f(pos)
    T = _u(tri)
    out = np.zeros((T.shape[0], 3, 3), np.float32)
    lib.wb_corner_normals(_p32(P), T.ctypes.data_as(U), T.shape[0], P.shape[0],
                          float(cos_threshold), _p32(out))
    return out


def simplify(pos, tri, target=500):
    """Returns (new_pos, new_tri). pos is copied — the C call moves collapsed vertices."""
    lib = _LIB or load()
    P = _f(pos).copy()
    T = _u(tri)
    out = np.zeros_like(T)
    nf = ctypes.c_int(0)
    rc = lib.wb_qem_simplify(_p32(P), T.ctypes.data_as(U), T.shape[0],
                             out.ctypes.data_as(U), ctypes.byref(nf), int(target), P.shape[0])
    if rc:
        raise RuntimeError("wb_qem_simplify rc=%d" % rc)
    return P, out[:nf.value]
