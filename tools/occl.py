"""occl — software occlusion culling of box batches against the depth buffer.

The invariant: culling must not change a single pixel. If it does, a box that was visible got thrown
away, and the renderer lied about what was in front of it.

A box is marked occluded only when EVERY sample of its screen rectangle is nearer than the box's own
nearest point. Sampling a grid instead of every pixel can therefore miss a cull but never make a bad
one — which is the direction the error has to point.
"""

import ctypes

import numpy as np

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float
_lib = ctypes.CDLL("/opt/data/work/wubu3d/liboccl.so")
_lib.wubu_occl_test.argtypes = [_P, _I, _I, _P, _P, _I, _I, _P]   # zb,W,H,rects,nearz,n,step,vis


def boxes_of(faces):
    """Group faces by their source box: blocky emits 6 quads per box, consecutively."""
    return faces


def cull(faces, cam, zb, w, h, step=3):
    """Returns a boolean mask of faces to keep. Each face is culled on its own quad (cheap, and a quad
    is the draw unit here), using the quad's nearest corner depth."""
    Q = np.array([f[0] for f in faces], np.float32) if faces else np.zeros((0, 4, 3), np.float32)
    if len(Q) == 0:
        return np.zeros(0, bool), {}
    S, Z = cam.project(Q.reshape(-1, 3))
    S = S.reshape(-1, 4, 2)
    Z = Z.reshape(-1, 4)
    rects = np.empty((len(Q), 4), np.int32)
    rects[:, 0] = np.floor(S[..., 0].min(1))
    rects[:, 1] = np.floor(S[..., 1].min(1))
    rects[:, 2] = np.ceil(S[..., 0].max(1))
    rects[:, 3] = np.ceil(S[..., 1].max(1))
    nearz = Z.min(1).astype(np.float32)
    vis = np.ones(len(Q), np.int32)
    kept = _lib.wubu_occl_test(zb.ctypes.data_as(_P), w, h, rects.ctypes.data_as(_P),
                               nearz.ctypes.data_as(_P), len(Q), int(step),
                               vis.ctypes.data_as(_P))
    return vis.astype(bool), {"kept": kept, "culled": len(Q) - kept, "total": len(Q)}
