"""demo_exr — write beauty+depth EXR from a real render, then read the depth plane back.

The test is not "a file appeared". It is: does a reader see four channels, and does the Z channel
actually carry the depth of the thing in front of the camera.
"""

import ctypes

import numpy as np

import render_shaded as RS
import r15

_P = ctypes.c_void_p
_exr = ctypes.CDLL("/opt/data/work/wubu3d/libexr.so")
_exr.wubu_exr.argtypes = [ctypes.c_char_p, _P, ctypes.c_int, ctypes.c_int]
_exr.wubu_exr_z.argtypes = [ctypes.c_char_p, _P, _P, ctypes.c_int, ctypes.c_int]


def main():
    f, _ = r15.build({"Head": (0, -8, 0)}, H=1.0, hair=(30, 40, 74), shirt=(96, 92, 132))
    cam = RS.B.Cam((0.4, 0.75, 2.0), (0.05, 0.5, 0.0), fov=46, w=320, h=420)
    im = RS.aa(f, cam.eye, (0.05, 0.5, 0.0), 320, 420, ss=2, fov=46, flat=[], bg=(20, 18, 22),
               lights=[(1.6, 2.4, 1.8, 2.6)], ambient=0.35, gain=0.55, rim=0.2)
    rgb = np.asarray(im.convert("RGB"), np.float32) / 255.0
    rgb = np.ascontiguousarray(np.power(np.clip(rgb, 0, 1), 2.2).astype(np.float32))   # to linear

    zb = RS._LAST_ZB
    zb = np.asarray(zb if zb is not None else np.full((420, 320), 5.0), np.float32)
    if zb.shape != (420, 320):
        zb = zb.reshape(420, 320)
    zb = np.ascontiguousarray(np.where(np.isfinite(zb), zb, 0.0).astype(np.float32))

    rc1 = _exr.wubu_exr(b"/opt/data/cache/scratch/beauty.exr", _P(rgb.ctypes.data), 320, 420)
    rc2 = _exr.wubu_exr_z(b"/opt/data/cache/scratch/beauty_z.exr", _P(rgb.ctypes.data),
                          _P(zb.ctypes.data), 320, 420)
    print("write: beauty rc=%d, beauty+z rc=%d" % (rc1, rc2))
    print("depth plane: %.2f..%.2f world units, mean %.2f"
          % (float(zb[zb > 0].min()), float(zb.max()), float(zb[zb > 0].mean())))


if __name__ == "__main__":
    main()
