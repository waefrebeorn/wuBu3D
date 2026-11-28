"""demo_fur — strand fur with alpha-tested cards, and what the shells could not do.

Shell fur gave volume and a stepped rim. Real fur needs strands: a card with a hair-clump texture and
holes, replicated around the head with a random tilt, rendered with the alpha test on. This is the
look every cartoon and every engine's groom tool produces, and it is 40 lines of geometry plus one
discard in the shader.
"""

import ctypes

import numpy as np
from PIL import Image

import render_shaded as RS
import r15

_P = ctypes.c_void_p
_lib = ctypes.CDLL("/opt/data/work/wubu3d/libshade.so")
_lib.wubu_alpha_cut.argtypes = [ctypes.c_float]


def clump_texture(size=256, strands=26, seed=5):
    """One hair card: vertical strands tapering to a point, with alpha holes between them."""
    rng = np.random.default_rng(seed)
    tex = np.zeros((size, size, 4), np.uint8)
    tex[..., 0:3] = (34, 44, 80)
    xx = np.arange(size, dtype=np.float32)[None, :]
    yy = np.arange(size, dtype=np.float32)[:, None] / size
    for s in range(strands):
        base = rng.uniform(0.03, 0.97) * size
        lean = rng.uniform(-0.16, 0.16) * size
        width = rng.uniform(1.6, 3.4)
        tip = rng.uniform(0.55, 1.0)
        cx = base + lean * yy
        taper = width * (1.0 - yy / tip).clip(0.0, 1.0)
        m = (np.abs(xx - cx) < taper) & (yy < tip)
        shade = 0.75 + 0.5 * yy
        for c in range(3):
            tex[..., c] = np.where(m, np.clip(tex[..., c] * shade, 0, 255).astype(np.uint8),
                                   tex[..., c])
        tex[..., 3] = np.where(m | (np.abs(xx - cx) < taper + 1.0), 255, tex[..., 3])
    return tex


def cards(n=64, radius=0.145, seed=1):
    """Cards standing off the scalp, tilted outward, each a quad with uv 0..1."""
    rng = np.random.default_rng(seed)
    faces = []
    for i in range(n):
        a = rng.uniform(0, 2 * np.pi)
        t = rng.uniform(0.25, 0.95)              # height on the head
        r = radius * (1.0 - 0.35 * t)
        cx = np.cos(a) * r
        cz = np.sin(a) * r * 0.85
        cy = 0.78 + 0.16 * t
        hgt = rng.uniform(0.10, 0.20)
        wid = hgt * 0.55
        # the card faces outward and leans out
        nx, nz = np.cos(a), np.sin(a)
        px, pz = -nz, nx
        q = [(cx - px * wid / 2, cy, cz - pz * wid / 2),
             (cx + px * wid / 2, cy, cz + pz * wid / 2),
             (cx + px * wid / 2 + nx * 0.02, cy + hgt, cz + pz * wid / 2 + nz * 0.02),
             (cx - px * wid / 2 + nx * 0.02, cy + hgt, cz - pz * wid / 2 + nz * 0.02)]
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        faces.append((q, (34, 44, 80), {"n": (nx, 0.15, nz), "uv": uv}))
    return faces


def main():
    head, _ = r15.build({"Head": (0, -6, 0)}, H=1.0, hair=(30, 40, 74))
    scalp = [(q, c, o) for q, c, o in head
             if min(v[1] for v in q) > 0.62 and max(abs(v[0]) for v in q) < 0.24]
    tex = clump_texture()
    eye, tgt = (0.0, 0.80, 1.85), (0.0, 0.78, 0.0)
    kw = dict(ss=2, fov=32, flat=[], bg=(236, 232, 226),
              lights=[(0.7, 1.5, 1.9, 2.0), (-1.1, 0.9, 0.6, 1.2)],
              ambient=0.45, gain=0.5, rim=0.18, tex=tex)

    bare = RS.aa(scalp, eye, tgt, 300, 340, **kw).convert("RGB")
    shells = None
    for n in (150, 400):
        # second pass, alpha test on: the card texture has holes and the head must not sample it
        with_fur = RS.aa(scalp, eye, tgt, 300, 340, alpha_faces=cards(n), alpha_tex=tex,
                         alpha_cut=0.5, **kw).convert("RGB")
        a = np.asarray(bare.convert("L"), np.float32)
        b = np.asarray(with_fur.convert("L"), np.float32)
        cover = float(((np.abs(b - 236) > 12) & (np.abs(a - 236) <= 12)).mean())
        print("fur: %3d cards -> %5.1f%% of the frame newly covered by strands" % (n, 100 * cover))
        shells = with_fur

    sh = Image.new("RGB", (900, 340), (236, 232, 226))
    sh.paste(bare, (0, 0))
    sh.paste(shells, (300, 0))
    sh.save("/opt/data/cache/scratch/fur_strands.png")
    print("wrote fur_strands.png")


if __name__ == "__main__":
    main()
