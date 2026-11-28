"""shadow (shader) — the map bound into the rasteriser, so walls shade floors and props shade walls.

Before this the shadow pass could only darken a flat ground plane: `wubu_shadow_floor` intersects y=0
and nothing else, so light passed straight through every vertical surface. The test is a wall between
a light and a second wall: the far wall must darken, and it must not darken anywhere else.
"""

import ctypes

import numpy as np
from PIL import Image

import blocky as B
import cast_blocky as CB
import render_shaded as RS

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float
sh = ctypes.CDLL("/opt/data/work/wubu3d/libshadow.so")
sh.wubu_shadowmap.argtypes = [_P, _I, _P, _P, _I, _F, _P]
sh.wubu_shadow_lookat.argtypes = [_P, _P, _P]
lib = RS._lib
lib.wubu_shadow_bind.argtypes = [_P, _I, _P, _F, _F]
lib.wubu_shadow_unbind.argtypes = []

LIGHT = np.array([3.2, 4.4, 2.0], np.float32)
TARGET = np.array([0.0, 0.4, 0.0], np.float32)
FOV = 62.0


def build_map(faces, size=512):
    tri = []
    for q, c, o in faces:
        for idx in ((0, 1, 2), (0, 2, 3)):
            for i in idx:
                tri.extend(q[i])
    tri = np.asarray(tri, np.float32)
    dep = np.full(size * size, 1e30, np.float32)
    sh.wubu_shadowmap(tri.ctypes.data_as(_P), len(tri) // 9, LIGHT.ctypes.data_as(_P),
                      TARGET.ctypes.data_as(_P), size, FOV, dep.ctypes.data_as(_P))
    mat = np.zeros(12, np.float32)
    sh.wubu_shadow_lookat(LIGHT.ctypes.data_as(_P), TARGET.ctypes.data_as(_P),
                          mat.ctypes.data_as(_P))
    return dep, mat, size


def scene():
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, 0, 4.0, 0.1, 4.0, (120, 104, 82))]
    f += [(q, c, o) for q, c, o in CB.box(-0.4, 0.75, -0.5, 0.12, 1.5, 1.6, (120, 104, 82))]
    f += [(q, c, o) for q, c, o in CB.box(0.9, 0.5, -0.9, 1.4, 1.0, 0.12, (110, 96, 76))]
    return f


def main():
    f = scene()
    dep, mat, size = build_map(f)
    tan_half = float(np.tan(np.radians(FOV) / 2))
    cam_eye, cam_tgt = (-0.9, 1.35, 2.3), (0.1, 0.45, -0.6)
    # the light is 5.6 units away and falloff is inverse-square-ish: 3.0 puts the whole scene under
    # the floor of visibility, which hides the very thing the test is about
    kw = dict(ss=2, fov=50, flat=[], bg=(30, 28, 34), lights=[tuple(LIGHT) + (11.0,)],
              ambient=0.30, gain=0.55, rim=0.0)

    lib.wubu_shadow_unbind()
    a = RS.aa(f, cam_eye, cam_tgt, 420, 320, **kw).convert("RGB")

    lib.wubu_shadow_bind(_P(dep.ctypes.data), size, _P(mat.ctypes.data), tan_half, 0.02)
    b = RS.aa(f, cam_eye, cam_tgt, 420, 320, **kw).convert("RGB")
    lib.wubu_shadow_unbind()

    A = np.asarray(a, np.float32)
    Bm = np.asarray(b, np.float32)
    d = (A - Bm).mean(2)
    dark = d > 12
    print("shader shadows: %.1f%% of the frame darkened, mean %.1f levels, max %.0f"
          % (100 * dark.mean(), float(d[dark].mean()) if dark.any() else 0.0, float(d.max())))

    sheet = Image.new("RGB", (840, 320), (24, 22, 26))
    sheet.paste(a, (0, 0)); sheet.paste(b, (420, 0))
    sheet.save("/opt/data/cache/scratch/shadow_shader.png")
    print("wrote shadow_shader.png")


if __name__ == "__main__":
    main()
