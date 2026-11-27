"""wubu3d_obj — ctypes driver for libwubuobj.so (Wavefront OBJ).

The Models Resource ships game models as OBJ + MTL. This loads the geometry; the material sidecar is
parsed in Python because it is a handful of lines and only runs once per model.

    pos, tri, nrm, nverts, ntris = wubu3d_obj.load("stage.obj")
"""

import ctypes
import os
import subprocess

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "wubuobj.c")
_LIB = None


def build(force=False):
    so = os.path.join(_HERE, "libwubuobj.so")
    if force or not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(SRC):
        tmp = so + ".tmp"
        subprocess.run(["cc", "-O3", "-std=c11", "-shared", "-fPIC", "-o", tmp, SRC, "-lm"],
                       check=True)
        os.replace(tmp, so)
    return so


def _get_lib():
    global _LIB
    lib = ctypes.CDLL(build())
    lib.wb_obj_parse.argtypes = [ctypes.c_char_p, ctypes.c_size_t,
                                 ctypes.POINTER(ctypes.c_float),
                                 ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_int32),
                                 ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    lib.wb_obj_parse.restype = ctypes.c_int
    lib.wb_obj_material_count.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.wb_obj_material_count.restype = ctypes.c_int
    _LIB = lib
    return lib


def load_text(text, want_normals=False):
    """Parse OBJ text. Returns (pos (n,3) f32, tri (m,3) u32, vnorm (m,3) i32 or None)."""
    lib = _LIB or _get_lib()
    buf = text.encode("utf-8") if isinstance(text, str) else text
    nv = ctypes.c_int(0)
    nt = ctypes.c_int(0)
    lib.wb_obj_parse(buf, len(buf), None, None, None, 0, ctypes.byref(nv), ctypes.byref(nt))
    pos = np.zeros((max(1, nv.value), 3), np.float32)
    tri = np.zeros((max(1, nt.value), 3), np.uint32)
    vn = np.zeros((max(1, nt.value), 3), np.int32) if want_normals else None
    got = lib.wb_obj_parse(buf, len(buf),
                           pos.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                           tri.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                           vn.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)) if want_normals else None,
                           1 if want_normals else 0,
                           ctypes.byref(nv), ctypes.byref(nt))
    return pos[:nv.value], tri[:got], (vn[:got] if want_normals else None)


def load(path, want_normals=False):
    with open(path, "rb") as f:
        text = f.read()
    lib = _LIB or _get_lib()
    mats = lib.wb_obj_material_count(text, len(text))
    pos, tri, vn = load_text(text, want_normals=want_normals)
    return pos, tri, vn, mats


def parse_mtl(path):
    """Material colours from an MTL sidecar: {name: (r,g,b)}. Texture paths are ignored —
    the Models Resource wiki's most common complaint is absolute paths that only resolve on the
    machine that exported them, so a missing .png must not break the load."""
    out = {}
    name = None
    with open(path, "r", errors="ignore") as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            if p[0] == "newmtl" and len(p) > 1:
                name = p[1]
                out[name] = (0.8, 0.8, 0.8)
            elif p[0] in ("Kd", "Ka") and name and len(p) >= 4:
                try:
                    out[name] = tuple(min(1.0, max(0.0, float(v))) for v in p[1:4])
                except ValueError:
                    pass
    return out
