"""demo_sss — skin with a wrapped terminator and back-light transmission.

A head lit from behind should glow at the thin edges: ears, the shadow side of the nose. Without it a
face is a painted box, which is exactly what the reference short's characters avoid by keeping the
face flat and graphic — but any character with a nose needs it.
"""

import ctypes

import numpy as np
from PIL import Image

import render_shaded as RS
import r15

_P = ctypes.c_void_p
_lib = ctypes.CDLL("/opt/data/work/wubu3d/libshade.so")
_lib.wubu_sss.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]


def render(sss):
    f, _ = r15.build({"Head": (0, -12, 0)}, H=1.0, hair=(30, 40, 74))
    head = [(q, c, o) for q, c, o in f
            if min(v[1] for v in q) > 0.62 and max(abs(v[0]) for v in q) < 0.24]
    if sss:
        _lib.wubu_sss(0.55, 1.0, 0.55, 0.45)
    else:
        _lib.wubu_sss(0.0, 1.0, 1.0, 1.0)
    im = RS.aa(head, (0.55, 0.72, 1.60), (0.0, 0.72, 0.0), 300, 340, ss=2, fov=32,
               flat=[], bg=(238, 234, 228),
               lights=[(1.15, 1.30, -1.60, 2.2)],     # behind and to the side
               ambient=0.22, gain=0.62, rim=0.05)
    _lib.wubu_sss(0.0, 1.0, 1.0, 1.0)
    return im.convert("RGB")


def main():
    a = render(False)
    b = render(True)
    A = np.asarray(a, np.float32)
    B = np.asarray(b, np.float32)
    mask = (np.abs(A - np.array([238, 234, 228])).sum(2) > 18)     # head pixels only
    d = (B - A).mean(2)[mask]
    print("sss: %d head px, mean shift %+.1f levels, max %+.1f, %.1f%% of head lifted >5 levels"
          % (mask.sum(), d.mean(), d.max(), 100.0 * (d > 5).mean()))
    sheet = Image.new("RGB", (600, 340), (238, 234, 228))
    sheet.paste(a, (0, 0))
    sheet.paste(b, (300, 0))
    sheet.save("/opt/data/cache/scratch/sss_sheet.png")
    print("wrote sss_sheet.png")


if __name__ == "__main__":
    main()
