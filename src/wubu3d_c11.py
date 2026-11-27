"""wubu3d_c11 — ctypes driver for libwubuskin.so.

Python is the scripting layer. This binds the C11 core so the per-vertex work happens in C: bone
matrices, linear blend skinning, dual quaternion skinning, and bone-heat weights.

    import wubu3d_c11 as wc
    wc.load()                       # builds libwubuskin.so if needed
    mats = wc.bone_matrix(ra, rb, pa, pb)
    out = wc.lbs(points, W, mats)
    names, W, n = wc.heat(verts, edges, heads, tails, bones)
"""

import ctypes
import os
import subprocess
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wubuskin.c")
_LIB = None


def build(force=False):
    """Compile the shared object next to the source."""
    so = os.path.join(_HERE, "libwubuskin.so")
    if force or not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(SRC):
        tmp = so + ".tmp"
        cmd = ["cc", "-O2", "-std=c11", "-shared", "-fPIC", "-o", tmp, SRC, "-lm"]
        subprocess.run(cmd, check=True)
        os.replace(tmp, so)
    return so


def load():
    global _LIB
    so = build()
    lib = ctypes.CDLL(so)
    f32 = ctypes.POINTER(ctypes.c_float)
    i32 = ctypes.POINTER(ctypes.c_int)

    lib.wb_bone_matrix.argtypes = [f32, f32, f32, f32, f32]
    lib.wb_bone_matrix.restype = None
    lib.wb_lbs.argtypes = [f32, f32, ctypes.c_int, ctypes.c_int, f32, f32]
    lib.wb_lbs.restype = None
    lib.wb_dqs.argtypes = [f32, f32, ctypes.c_int, ctypes.c_int, f32, f32]
    lib.wb_dqs.restype = None
    lib.wb_heat.argtypes = [f32, ctypes.c_int, i32, ctypes.c_int, f32, f32, ctypes.c_int,
                            ctypes.c_int, ctypes.c_float, f32, f32, i32]
    lib.wb_heat.restype = ctypes.c_int
    lib.wb_heat_scratch_floats.argtypes = [ctypes.c_int]
    lib.wb_heat_scratch_floats.restype = ctypes.c_int
    lib.wb_mat4_mul.argtypes = [f32, f32, f32]
    lib.wb_mat4_mul.restype = None
    _LIB = lib
    return lib


def _p(a):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_float))


def _pi(a):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_int))


def _f32(x):
    return np.ascontiguousarray(x, dtype=np.float32)


def bone_matrix(ra, rb, pa, pb):
    lib = _LIB or load()
    out = np.zeros(16, np.float32)
    lib.wb_bone_matrix(_p(_f32(ra)), _p(_f32(rb)), _p(_f32(pa)), _p(_f32(pb)), _p(out))
    return out.reshape(4, 4)


def mul(a, b):
    lib = _LIB or load()
    out = np.zeros(16, np.float32)
    lib.wb_mat4_mul(_p(_f32(np.asarray(a, np.float32).reshape(-1))),
                    _p(_f32(np.asarray(b, np.float32).reshape(-1))), _p(out))
    return out.reshape(4, 4)


def lbs(points, W, mats):
    """points (n,3), W (n,bones), mats (bones,4,4) -> (n,3)"""
    lib = _LIB or load()
    P = _f32(points)
    Wt = _f32(W)
    M = _f32(np.asarray(mats, np.float32).reshape(-1))
    n, bones = Wt.shape
    out = np.zeros((n, 3), np.float32)
    lib.wb_lbs(_p(P), _p(Wt), n, bones, _p(M), _p(out))
    return out


def dqs(points, W, mats):
    lib = _LIB or load()
    P = _f32(points)
    Wt = _f32(W)
    M = _f32(np.asarray(mats, np.float32).reshape(-1))
    n, bones = Wt.shape
    out = np.zeros((n, 3), np.float32)
    lib.wb_dqs(_p(P), _p(Wt), n, bones, _p(M), _p(out))
    return out


def heat(verts, edges, heads, tails, iterations=60, rel=0.35):
    """Bone-heat weights. verts (n,3) welded positions, edges (m,2) welded indices,
    heads/tails (bones,3). Returns (n,bones) float32."""
    lib = _LIB or load()
    V = _f32(verts)
    E = np.ascontiguousarray(edges, dtype=np.int32)
    H = _f32(heads)
    T = _f32(tails)
    n = V.shape[0]
    bones = H.shape[0]
    out = np.zeros((n, bones), np.float32)
    scratch = np.zeros(lib.wb_heat_scratch_floats(n), np.float32)
    owner = np.zeros(n, np.int32)
    rc = lib.wb_heat(_p(V), n, _pi(E), E.shape[0], _p(H), _p(T), bones,
                     iterations, float(rel), _p(out), _p(scratch), _pi(owner))
    if rc:
        raise RuntimeError("wb_heat failed rc=%d" % rc)
    return out
