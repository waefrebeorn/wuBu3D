"""oit — order-independent transparency, driven from Python against the same camera the rasteriser uses.

The invariant that makes this worth having is not "it looks glassy": it is that drawing the same panes
in the reverse order produces the *identical* image. Sorted alpha blending fails that by construction;
weighted-blended OIT passes it exactly.
"""

import ctypes

import numpy as np

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float
_lib = ctypes.CDLL("/opt/data/work/wubu3d/liboit.so")
_lib.wubu_oit_clear.argtypes = [_P, _P, _I]
_lib.wubu_oit_batch.argtypes = [_P, _P, _I, _I, _P, _I, _P, _F]
_lib.wubu_oit_resolve.argtypes = [_P, _P, _P, _I, _P]


def _ptr(a):
    return a.ctypes.data_as(_P)


def _tris(quads):
    # a single pane arrives as (4,3): reshape to (n,4,3) or the corner indices index the wrong axis
    q = np.asarray(quads, np.float32).reshape(-1, 4, 3)
    return np.stack([q[:, [0, 1, 2]], q[:, [0, 2, 3]]], 1).reshape(-1, 3, 3)


class OIT:
    def __init__(self, w, h, bg=(16, 15, 18)):
        self.w, self.h = w, h
        self.bg = np.array(bg, np.float32) / 255.0
        n = w * h
        self.acc = np.zeros(n * 4, np.float32)
        self.rev = np.ones(n, np.float32)
        self.items = []          # (world quads, rgba) — nothing is projected until render

    def add(self, quads, rgba):
        q = np.asarray(quads, np.float32).reshape(-1, 4, 3)
        c = np.asarray(rgba, np.float32).reshape(-1, 4)
        self.items.append((q, c))

    def render(self, cam, scale=2.0):
        _lib.wubu_oit_clear(_ptr(self.acc), _ptr(self.rev), self.w * self.h)
        for quads, rgba in self.items:
            tri = _tris(quads)
            Q = tri.reshape(-1, 3)
            S, Z = cam.project(Q)
            V = np.zeros((len(Q), 11), np.float32)
            V[:, 0], V[:, 1], V[:, 2] = S[:, 0], S[:, 1], Z
            V[:, 3:6] = Q
            tri_c = np.repeat(rgba, 3, axis=0).astype(np.float32)
            _lib.wubu_oit_batch(_ptr(self.acc), _ptr(self.rev), self.w, self.h,
                                _ptr(np.ascontiguousarray(V, np.float32)), len(tri),
                                _ptr(tri_c), float(scale))
        out = np.zeros((self.h, self.w, 3), np.uint8)
        _lib.wubu_oit_resolve(_ptr(out), _ptr(self.acc), _ptr(self.rev),
                              self.w * self.h, _ptr(self.bg))
        return out


def pane(centre, normal, up, half_w, half_h):
    c = np.asarray(centre, np.float32)
    n = np.asarray(normal, np.float32); n = n / max(1e-9, np.linalg.norm(n))
    u = np.asarray(up, np.float32); u = u - n * float(u @ n)
    u = u / max(1e-9, np.linalg.norm(u))
    r = np.cross(u, n); r = r / max(1e-9, np.linalg.norm(r))
    return np.array([c - r * half_w - u * half_h, c + r * half_w - u * half_h,
                     c + r * half_w + u * half_h, c - r * half_w + u * half_h], np.float32)
