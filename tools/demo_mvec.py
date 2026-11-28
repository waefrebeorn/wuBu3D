"""demo_mvec — motion vectors from depth alone, checked against the pixels themselves.

A vector that is merely non-zero is worthless. This renders the same scene from two camera positions,
measures the real image displacement with block matching on the frames, and compares that against the
depth-derived vectors. The frames are the ground truth; the depth buffer is only a claim about them.
"""

import ctypes
import struct

import numpy as np

import blocky as B
import cast_blocky as CB
import mvec
import render_shaded as RS

_P = ctypes.c_void_p
_exr = ctypes.CDLL("/opt/data/work/wubu3d/libexr.so")


def scene():
    f = []
    for i in range(6):
        for j in range(4):
            f += [(q, c, o) for q, c, o in
                  CB.box(-1.2 + 0.5 * i, 0.25, -1.0 + 0.5 * j, 0.12, 0.5, 0.12, (130, 108, 80))]
    return f


def render(cam, w, h, f=scene()):
    # look where the camera looks: forcing the same target for both frames cancels most of the pan
    # (a rotation that exactly compensates a translation), and block matching then measures ~1 px
    tgt = tuple((cam.eye + cam.M[2]).astype(np.float64))
    im = RS.aa(f, cam.eye, tgt, w, h, ss=1, fov=50, flat=[], bg=(28, 26, 30),
               lights=[(1.5, 2.5, 1.8, 2.6)], ambient=0.35, gain=0.5, rim=0.1)
    return np.asarray(im.convert("L"), np.float32), np.array(RS._LAST_ZB, np.float32)


def block_match(a, b, pts, half=4, search=12):
    """Best integer displacement for each patch centre, by SAD over a (2h+1)^2 window."""
    H, W = a.shape
    out = []
    for (x, y) in pts:
        x0, y0 = int(x), int(y)
        if x0 - half < search or y0 - half < search or x0 + half + search >= W or y0 + half + search >= H:
            continue
        patch = a[y0 - half:y0 + half + 1, x0 - half:x0 + half + 1]
        best, bd = 1e18, (0, 0)
        for dy in range(-search, search + 1):
            for dx in range(-search, search + 1):
                cand = b[y0 + dy - half:y0 + dy + half + 1, x0 + dx - half:x0 + dx + half + 1]
                if cand.shape != patch.shape:
                    continue
                d = float(np.abs(cand - patch).mean())
                if d < best:
                    best, bd = d, (dx, dy)
        out.append((x0, y0, bd[0], bd[1], best))
    return out


def main():
    w, h = 320, 240
    cam_now = B.Cam((0.0, 0.9, 2.4), (0.0, 0.4, 0.0), fov=50, w=w, h=h)
    img_a, zb = render(cam_now, w, h)

    dpan = 0.06
    cam_prev = B.Cam((dpan, 0.9, 2.4), (dpan, 0.4, 0.0), fov=50, w=w, h=h)
    img_b, _ = render(cam_prev, w, h)

    mv, valid = mvec.motion_vectors(zb, cam_now, cam_prev)
    st = mvec.stats(mv, valid)
    print("depth-derived: %.0f%% pixels valid, mean %.2f px, p99 %.2f px"
          % (100 * st["frac_valid"], st["mean_px"], st["p99_px"]))

    # sample patch centres where geometry exists
    ys, xs = np.nonzero(valid)
    rng = np.random.default_rng(2)
    pick = rng.choice(len(xs), size=min(40, len(xs)), replace=False)
    pts = [(xs[i], ys[i]) for i in pick]
    matches = block_match(img_a, img_b, pts)

    err = []
    for (x, y, dx, dy, sad) in matches:
        if sad > 6.0:                    # flat or occluded patch: no reliable flow
            continue
        px = int(min(w - 1, x)); py = int(min(h - 1, y))
        err.append((dx - mv[py, px, 0], dy - mv[py, px, 1]))
    if err:
        e = np.array(err, np.float32)
        print("block matching on %d patches: mean error vx %+.2f px, vy %+.2f px"
              % (len(e), e[:, 0].mean(), e[:, 1].mean()))
        print("median |error| %.2f px (a 12 px search cannot resolve better than about 1 px)"
              % float(np.median(np.abs(e))))
    else:
        print("block matching found no reliable patches")

    exr_path = b"/opt/data/cache/scratch/comp_mv.exr"
    _exr.wubu_exr_comp.argtypes = [ctypes.c_char_p, _P, _P, _P, _P, ctypes.c_int, ctypes.c_int]
    rgb = np.ascontiguousarray(np.repeat(img_a[..., None], 3, -1) / 255.0)
    nrm = np.ascontiguousarray(np.nan_to_num(RS._LAST_NBUF).astype(np.float32))
    rc = _exr.wubu_exr_comp(exr_path, _P(rgb.ctypes.data), _P(zb.ctypes.data), _P(nrm.ctypes.data),
                            _P(np.ascontiguousarray(mv).ctypes.data), w, h)

    d = open(exr_path, "rb").read()
    p, names = 8, []
    while d[p] != 0:
        e = d.index(0, p); nm = d[p:e].decode(); p = e + 1
        e = d.index(0, p); p = e + 1
        size = struct.unpack_from("<i", d, p)[0]; p += 4
        if nm == "channels":
            q, pay = 0, d[p:p + size]
            while pay[q] != 0:
                ee = pay.index(0, q); names.append(pay[q:ee].decode()); q = ee + 1 + 16
        p += size
    print("exr rc=%d channels=%s" % (rc, names))
    first = struct.unpack_from("<q", d, p + 1)[0]
    ry = 150
    off = first + ry * (struct.unpack_from("<ii", d, first)[1] + 8)
    _, sz = struct.unpack_from("<ii", d, off)
    row = d[off + 8:off + 8 + sz]
    n = len(names)
    ww = sz // (n * 2)
    plane = {names[i]: np.frombuffer(row[i * ww * 2:(i + 1) * ww * 2], dtype="<f2").astype(np.float32)
             for i in range(n)}
    print("row %d: VX %.2f..%.2f, VY %.2f..%.2f, Z %.2f..%.2f"
          % (ry, plane["VX"].min(), plane["VX"].max(), plane["VY"].min(), plane["VY"].max(),
             plane["Z"].min(), plane["Z"].max()))


if __name__ == "__main__":
    main()
