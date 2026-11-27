"""wubu3d_rigc — ctypes driver for libwuburig.so (swing-twist, twist distribution, FK/IK blend).

Not to be confused with wubu3d_rig.py, which is the older pure-Python rig that builds geometry.
This is the C11 maths: decomposition, distribution, blending.
"""

import ctypes
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wuburig.c")
_LIB = None
D = ctypes.POINTER(ctypes.c_double)


def build(force=False):
    so = os.path.join(_HERE, "libwuburig.so")
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
    lib.wb_swing_twist.argtypes = [D, D, D, D]
    lib.wb_twist_distribute.argtypes = [ctypes.c_int, ctypes.c_double, D, ctypes.c_int]
    lib.wb_chain_world.argtypes = [ctypes.c_int, D, D]
    lib.wb_qrot.argtypes = [D, D, D]
    lib.wb_fkik_blend.argtypes = [D, D, ctypes.c_int, ctypes.c_double, D]
    lib.wb_lbs_radius_ratio.argtypes = [ctypes.c_double]
    lib.wb_lbs_radius_ratio.restype = ctypes.c_double
    _LIB = lib
    return lib


def _d(a):
    return np.ascontiguousarray(a, dtype=np.float64)


def _p(a):
    return a.ctypes.data_as(D)


def swing_twist(q, axis):
    """Returns (swing quaternion, twist angle in degrees about `axis`)."""
    lib = _get_lib()
    Q = _d(np.asarray(q, np.float64).reshape(4))
    A = _d(np.asarray(axis, np.float64).reshape(3))
    swing = np.zeros(4, np.float64)
    tw = ctypes.c_double(0.0)
    lib.wb_swing_twist(_p(Q), _p(A), _p(swing), ctypes.byref(tw))
    return swing, tw.value


def twist_distribute(n, total_deg, mode=0):
    lib = _get_lib()
    out = np.zeros(n, np.float64)
    lib.wb_twist_distribute(n, float(total_deg), _p(out), int(mode))
    return out


def chain_world(rotations):
    lib = _get_lib()
    R = _d(np.asarray(rotations, np.float64).reshape(-1, 4))
    out = np.zeros_like(R)
    lib.wb_chain_world(R.shape[0], _p(R), _p(out))
    return out


def qrot(q, p):
    lib = _get_lib()
    Q = _d(np.asarray(q, np.float64))
    P = _d(np.asarray(p, np.float64))
    out = np.zeros(3, np.float64)
    lib.wb_qrot(_p(Q), _p(P), _p(out))
    return out


def fkik_blend(fk, ik, w):
    lib = _get_lib()
    A = _d(np.asarray(fk, np.float64).reshape(-1))
    B = _d(np.asarray(ik, np.float64).reshape(-1))
    out = np.zeros_like(A)
    lib.wb_fkik_blend(_p(A), _p(B), A.size // 3, float(w), _p(out))
    return out.reshape(-1, 3)


def lbs_radius_ratio(twist_deg):
    return _get_lib().wb_lbs_radius_ratio(float(twist_deg))
