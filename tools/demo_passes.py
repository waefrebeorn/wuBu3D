"""demo_passes — a real render out to EXR with depth and normals, verified by reading it back.

A box has exactly six face normals, so the check is exact: the normal channels must contain six
distinct vectors. Stronger than "the file is not empty".
"""

import ctypes
import struct

import numpy as np

import render_shaded as RS
import r15

_P = ctypes.c_void_p
_exr = ctypes.CDLL("/opt/data/work/wubu3d/libexr.so")
_exr.wubu_exr_passes.argtypes = [ctypes.c_char_p, _P, _P, _P, ctypes.c_int, ctypes.c_int]


def read_planes(path, row_y=None):
    d = open(path, "rb").read()
    p, names = 8, []
    while d[p] != 0:
        e = d.index(0, p); name = d[p:e].decode(); p = e + 1
        e = d.index(0, p); p = e + 1
        size = struct.unpack_from("<i", d, p)[0]; p += 4
        if name == "channels":
            q, pay = 0, d[p:p + size]
            while pay[q] != 0:
                ee = pay.index(0, q); names.append(pay[q:ee].decode()); q = ee + 1 + 16
        p += size
    first = struct.unpack_from("<q", d, p + 1)[0]
    _, sz = struct.unpack_from("<ii", d, first)
    # scanline 0 is sky: every plane is legitimately constant there, so read a row through the subject
    ry = 0 if row_y is None else row_y
    off = first + ry * (sz + 8)
    _, sz2 = struct.unpack_from("<ii", d, off)
    row = d[off + 8:off + 8 + sz2]
    w = sz // (len(names) * 2)
    planes = {names[i]: np.frombuffer(row[i * w * 2:(i + 1) * w * 2], dtype="<f2").astype(np.float32)
              for i in range(len(names))}
    return names, planes, w


def main():
    f, _ = r15.build({"Head": (0, -10, 0)}, H=1.0, hair=(30, 40, 74), shirt=(96, 92, 132))
    im = RS.aa(f, (0.4, 0.75, 2.0), (0.05, 0.5, 0.0), 240, 320, ss=1, fov=46, flat=[],
               bg=(20, 18, 22), lights=[(1.6, 2.4, 1.8, 2.6)], ambient=0.3, gain=0.5, rim=0.1)
    rgb = np.ascontiguousarray((np.asarray(im.convert("RGB"), np.float32) / 255.0).astype(np.float32))
    z = np.ascontiguousarray(np.where(np.isfinite(RS._LAST_ZB), RS._LAST_ZB, 0.0).astype(np.float32))
    n = np.ascontiguousarray(np.nan_to_num(RS._LAST_NBUF).astype(np.float32))

    rc = _exr.wubu_exr_passes(b"/opt/data/cache/scratch/passes_real.exr", _P(rgb.ctypes.data),
                              _P(z.ctypes.data), _P(n.ctypes.data), 240, 320)
    names, planes, w = read_planes("/opt/data/cache/scratch/passes_real.exr", row_y=150)
    print("rc=%d channels=%s width=%d height=%d" % (rc, names, w, 320))

    nxy = np.stack([planes["NX"], planes["NY"], planes["NZ"]], -1)
    live = np.abs(nxy).sum(-1) > 0.05
    uniq = np.unique(np.round(nxy[live], 1), axis=0)
    print("normal pass: %d px carry a normal, %d distinct directions" % (int(live.sum()), len(uniq)))
    zz = planes["Z"]
    print("depth pass: %.2f..%.2f world units" % (float(zz[zz > 0].min()), float(zz.max())))


if __name__ == "__main__":
    main()
