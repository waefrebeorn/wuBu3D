"""wubu3d_ik — ctypes driver for libwubuik.so (analytic two-bone, FABRIK chains)."""

import ctypes
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wubuik.c")
_LIB = None
F = ctypes.POINTER(ctypes.c_float)


def build(force=False):
    so = os.path.join(_HERE, "libwubuik.so")
    if force or not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(SRC):
        tmp = so + ".tmp"
        subprocess.run(["cc", "-O3", "-std=c11", "-shared", "-fPIC", "-o", tmp, SRC, "-lm"],
                       check=True)
        os.replace(tmp, so)
    return so


def load():
    global _LIB
    lib = ctypes.CDLL(build())
    lib.wb_ik_two_bone.argtypes = [F, F, ctypes.c_float, ctypes.c_float, F, F, F]
    lib.wb_ik_two_bone.restype = ctypes.c_int
    lib.wb_ik_fabrik.argtypes = [F, ctypes.c_int, F, ctypes.c_int, ctypes.c_float]
    lib.wb_ik_fabrik.restype = ctypes.c_int
    _LIB = lib
    return lib


def _f(a):
    return np.ascontiguousarray(a, dtype=np.float32)


def _p(a):
    return a.ctypes.data_as(F)


def two_bone(root, target, l1, l2, pole=(0.0, 1.0, 0.0)):
    """Returns (joint, end) — the closed-form elbow position and the reached end."""
    lib = _LIB or load()
    r = _f(np.asarray(root, np.float32))
    t = _f(np.asarray(target, np.float32))
    p = _f(np.asarray(pole, np.float32))
    j = np.zeros(3, np.float32)
    e = np.zeros(3, np.float32)
    ok = lib.wb_ik_two_bone(_p(r), _p(t), float(l1), float(l2), _p(p), _p(j), _p(e))
    return ok, j, e


def fabrik(joints, target, max_iter=32, tol=1e-3):
    """joints: (n,3) chain. Returns (joints solved, iterations used)."""
    lib = _LIB or load()
    P = _f(np.asarray(joints, np.float32)).copy()
    T = _f(np.asarray(target, np.float32))
    it = lib.wb_ik_fabrik(_p(P), P.shape[0], _p(T), int(max_iter), float(tol))
    return P, it
