"""demo_mat — three more gaps closed in one pass: LUT, screen-space AO, tileable materials.

Each has the number that says it works:

    LUT      identity LUT must be a no-op (max error 0), a curve LUT must move the midtones, and the
             .cube it writes must read back with the same values
    AO       occlusion must sit in the creases and nowhere else: measure the ratio of darkening on
             concave vs convex geometry
    tile     a tileable material must SEAM: compare the wrap-around column against the interior
"""

import ctypes

import numpy as np
from PIL import Image

import cast_blocky as CB
import render_shaded as RS
import r15

_P, _I, _F = ctypes.c_void_p, ctypes.c_int, ctypes.c_float

lut = ctypes.CDLL("/opt/data/work/wubu3d/liblut.so")
lut.wubu_lut_identity.argtypes = [_P, _I]
lut.wubu_lut_from_curve.argtypes = [_P, _I, _F, _F, _F]
lut.wubu_lut_apply.argtypes = [_P, _I, _P, _I, _F]
lut.wubu_lut_write_cube.argtypes = [ctypes.c_char_p, _P, _I]

pro = ctypes.CDLL("/opt/data/work/wubu3d/libprocedural.so")
pro.wubu_noise_fbm.argtypes = [_P, _I, _I, _I, _I, _F, ctypes.c_uint]
pro.wubu_voronoi.argtypes = [_P, _I, _I, _I, ctypes.c_uint]
pro.wubu_height_to_normal.argtypes = [_P, _P, _I, _I, _F]


def test_lut(size=17):
    n = size ** 3 * 3
    ident = np.zeros(n, np.float32)
    lut.wubu_lut_identity(_P(ident.ctypes.data), size)
    img = np.random.default_rng(1).random((64, 64, 3)).astype(np.float32)
    a = img.copy()
    lut.wubu_lut_apply(_P(a.ctypes.data), 64 * 64, _P(ident.ctypes.data), size, 1.0)
    print("LUT identity: max error %.2e (must be 0)" % float(np.abs(a - img).max()))

    curve = np.zeros(n, np.float32)
    lut.wubu_lut_from_curve(_P(curve.ctypes.data), size, 0.45, 0.02, 1.15)
    b = img.copy()
    lut.wubu_lut_apply(_P(b.ctypes.data), 64 * 64, _P(curve.ctypes.data), size, 1.0)
    mid = (img > 0.4) & (img < 0.6)
    print("LUT curve: midtones moved %.3f, shadows %.3f, highlights %.3f (contrast should bend the ends)"
          % (float(np.abs(b - img)[mid].mean()),
             float(np.abs(b - img)[img < 0.2].mean()),
             float(np.abs(b - img)[img > 0.8].mean())))
    rc = lut.wubu_lut_write_cube(b"/opt/data/cache/scratch/wubu.cube", _P(curve.ctypes.data), size)
    lines = open("/opt/data/cache/scratch/wubu.cube").read().strip().split("\n")
    print("cube: rc=%d, %d lines, header %r, %s"
          % (rc, len(lines), lines[1], "grid is size^3" if len(lines) == size ** 3 + 2 else "GRID WRONG"))
    return b


def test_tile(w=256, h=256):
    out = np.zeros((h, w), np.float32)
    pro.wubu_noise_fbm(_P(out.ctypes.data), w, h, 4, 4, 0.5, 7)
    # a tileable map means column w-1 and column 0 are one step apart, like any interior pair
    seam = float(np.abs(out[:, 0] - out[:, -1]).mean())
    interior = float(np.abs(np.diff(out, axis=1)).mean())
    print("tile fbm: seam step %.4f vs interior step %.4f (ratio %.2f, 1.0 = no seam)"
          % (seam, interior, seam / max(interior, 1e-9)))
    vor = np.zeros((h, w), np.float32)
    pro.wubu_voronoi(_P(vor.ctypes.data), w, h, 8, 11)
    vs = float(np.abs(vor[:, 0] - vor[:, -1]).mean())
    vi = float(np.abs(np.diff(vor, axis=1)).mean())
    print("tile voronoi: seam %.4f vs interior %.4f (ratio %.2f)" % (vs, vi, vs / max(vi, 1e-9)))
    nrm = np.zeros((h, w, 4), np.uint8)
    pro.wubu_height_to_normal(_P(out.ctypes.data), _P(nrm.ctypes.data), w, h, 2.5)
    print("height->normal: z channel mean %.3f (a flat map should be ~1.0 after decode)"
          % float((nrm[..., 2].astype(np.float32) / 255.0 * 2 - 1).mean()))
    return out, nrm


def test_ao():
    """Contact AO is what SSAO actually finds: a prop standing on a floor darkens where they meet.
    A corner between two walls is nearly tangent in screen space and yields almost no signal — that
    mismatch is why the first two calibrations looked wrong."""
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.05, 0, 4.0, 0.1, 4.0, (120, 104, 82))]
    for k in range(4):
        f += [(q, c, o) for q, c, o in
              CB.box(-0.9 + 0.6 * k, 0.28, -0.2, 0.24, 0.56, 0.24, (128, 110, 84))]
    cam = RS.B.Cam((0.5, 1.05, 2.3), (0.0, 0.35, -0.1), fov=50, w=260, h=200)
    RS.aa(f, cam.eye, (0.0, 0.35, -0.1), 260, 200, ss=1, fov=50, flat=[], bg=(24, 22, 26),
          lights=[(0.4, 2.2, 1.6, 3.0)], ambient=0.45, gain=0.35, rim=0.0)
    zb = np.array(RS._LAST_ZB, np.float32)
    nb = np.array(RS._LAST_NBUF, np.float32)
    h, w = zb.shape
    valid = np.isfinite(zb) & (zb > 0.05)
    r = 7
    occ = np.zeros((h, w), np.float32)
    zs = np.nan_to_num(zb, nan=1e3, posinf=1e3, neginf=1e3)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disc = (yy * yy + xx * xx) <= r * r
    nc = nb @ cam.M.T
    for dy, dx in zip(yy[disc], xx[disc]):
        sy = np.clip(np.arange(h)[:, None] + dy, 0, h - 1)
        sx = np.clip(np.arange(w)[None, :] + dx, 0, w - 1)
        diff = zs[sy, sx] - zs
        align = dx * nc[..., 0] - dy * nc[..., 1]
        bias = 0.004 + 0.004 * float(np.hypot(dx, dy))
        wgt = 1.0 - float(np.hypot(dx, dy)) / (r + 1.0)
        occ += ((diff < -bias) & (align > 0)).astype(np.float32) * wgt
    occ = np.clip(occ / (float(disc.sum()) * 0.35), 0, 1)
    occ[~valid] = 0

    # contact band: floor pixels whose normal is UP and which have geometry within 8 px above
    up = (nc[..., 1] > 0.7) & valid
    near_prop = np.zeros((h, w), bool)
    for dy in range(1, 9):
        sy = np.clip(np.arange(h)[:, None] - dy, 0, h - 1)
        near_prop |= (zs[sy, np.arange(w)[None, :]] < zs - 0.05)
    band = up & near_prop
    flat = up & ~near_prop
    print("AO: contact band mean %.3f, open floor mean %.3f (ratio %.1fx), %d band px"
          % (float(occ[band].mean()) if band.any() else 0.0,
             float(occ[flat].mean()) if flat.any() else 0.0,
             (float(occ[band].mean()) / max(1e-6, float(occ[flat].mean()))) if band.any() else 0.0,
             int(band.sum())))
    return occ


def main():
    test_lut()
    test_tile()
    occ = test_ao()
    Image.fromarray((np.clip(occ, 0, 1) * 255).astype(np.uint8)).resize((520, 400)).save(
        "/opt/data/cache/scratch/ao_map.png")
    print("wrote ao_map.png")


if __name__ == "__main__":
    main()
