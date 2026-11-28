"""demo_nmap — normal mapping on a surface that has almost no triangles.

A 5x5 quad wall is 50 triangles. With a normal map it should carry rivets and panel lines that the
geometry cannot express; the test is whether the shading gradient appears where there is no edge.
"""

import ctypes

import numpy as np
from PIL import Image, ImageFilter

import render_shaded as RS

_P = ctypes.c_void_p
_lib = ctypes.CDLL("/opt/data/work/wubu3d/libshade.so")
_lib.wubu_nmap.argtypes = [_P, ctypes.c_int, ctypes.c_int, ctypes.c_float]
_lib.wubu_nmap_off.argtypes = []


def wall(n=5, w=1.0, h=1.0):
    faces = []
    for j in range(n):
        for i in range(n):
            x0, x1 = -w / 2 + w * i / n, -w / 2 + w * (i + 1) / n
            y0, y1 = h * j / n, h * (j + 1) / n
            q = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)]
            uv = [(i / n, j / n), ((i + 1) / n, j / n), ((i + 1) / n, (j + 1) / n), (i / n, (j + 1) / n)]
            faces.append((q, (168, 150, 122), {"n": (0, 0, 1), "uv": uv}))
    return faces


def normal_map(size=512, rivets=7, rings=4):
    """Rivets on a grid plus horizontal panel lines, in tangent space (+z out of the surface)."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    nx = np.zeros_like(xx)
    ny = np.zeros_like(yy)
    for r in range(rings):
        for c in range(rivets):
            cx = (c + 0.5) / rivets
            cy = (r + 0.5) / rings
            dx, dy = xx - cx, yy - cy
            d = np.sqrt(dx * dx + dy * dy)
            k = np.clip(1.0 - d / 0.045, 0.0, 1.0) ** 0.6
            nx -= dx / (d + 1e-5) * k * 1.6
            ny -= dy / (d + 1e-5) * k * 1.6
    for r in range(rings + 1):
        cy = r / rings
        band = np.clip(1.0 - np.abs(yy - cy) / 0.012, 0.0, 1.0)
        ny += np.sign(cy - yy) * band * 0.9
    nz = np.ones_like(nx)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    rgba = np.zeros((size, size, 4), np.uint8)
    rgba[..., 0] = ((nx * 0.5 + 0.5) * 255).astype(np.uint8)
    rgba[..., 1] = ((ny * 0.5 + 0.5) * 255).astype(np.uint8)
    rgba[..., 2] = ((nz * 0.5 + 0.5) * 255).astype(np.uint8)
    rgba[..., 3] = 255
    return rgba


def measure(im, tag):
    """High-frequency energy: |image - blur(image)|. A gradient percentile is the wrong instrument for
    smooth-shaded bumps — most rivet pixels have a tiny gradient and the number stays at zero — while
    detail energy is exactly "how much structure is there that geometry did not put there"."""
    a = np.asarray(im.convert("L"), np.float32)
    lo = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(3)), np.float32)
    hf = float(np.abs(a - lo).mean())
    print("%-10s detail energy %.3f, luminance std %.2f, distinct %d"
          % (tag, hf, a.std(), len(np.unique(a.astype(np.uint8)))))
    return hf


def main():
    f = wall()
    eye, tgt = (0.0, 0.55, 2.2), (0.0, 0.5, 0.0)
    lit = dict(ss=2, fov=34, flat=[], bg=(232, 228, 220),
               lights=[(-1.7, 1.35, 0.55, 2.0), (1.5, 0.7, 0.45, 1.6)],
               ambient=0.34, gain=0.55, rim=0.08)
    _lib.wubu_nmap_off()
    flat_im = RS.aa(f, eye, tgt, 420, 520, **lit).convert("RGB")
    nm = normal_map()
    _lib.wubu_nmap(nm.ctypes.data_as(_P), nm.shape[1], nm.shape[0], 1.0)
    nmap_im = RS.aa(f, eye, tgt, 420, 520, **lit).convert("RGB")
    _lib.wubu_nmap_off()

    a = measure(flat_im, "flat")
    b = measure(nmap_im, "normal")
    print("normal map raised detail energy %.3f -> %.3f (%.1fx) on 50 triangles"
          % (a, b, b / max(a, 1e-6)))
    sheet = Image.new("RGB", (840, 520), (232, 228, 220))
    sheet.paste(flat_im, (0, 0))
    sheet.paste(nmap_im, (420, 0))
    sheet.save("/opt/data/cache/scratch/nmap_sheet.png")
    print("wrote nmap_sheet.png")


if __name__ == "__main__":
    main()
