"""demo_ragdoll — drop the skeleton, measure whether bones stay bones, render three states."""

import numpy as np
from PIL import Image

import ragdoll as RD
import render_shaded as RS


def box_from_segment(pa, pb, w, colour):
    """A box spanning pa->pb with square section w, built from an orthonormal basis (not euler)."""
    d = np.asarray(pb, np.float64) - np.asarray(pa, np.float64)
    L = float(np.linalg.norm(d))
    if L < 1e-9:
        return None
    d = d / L
    up = np.array([0.0, 1.0, 0.0])
    if abs(float(np.dot(d, up))) > 0.95:
        up = np.array([0.0, 0.0, 1.0])
    s = np.cross(d, up); s /= np.linalg.norm(s)
    u = np.cross(s, d)
    c = (np.asarray(pa, np.float64) + np.asarray(pb, np.float64)) / 2
    hx, hy, hz = w / 2, L / 2, w / 2
    corners = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corners.append(c + s * hx * sx + d * hy * sy + u * hz * sz)
    idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    nrm = [(-s, ), (s, ), (-u, ), (u, ), (-d, ), (d, )]
    faces = []
    for k, q in enumerate(idx):
        quad = [tuple(corners[i]) for i in q]
        n = nrm[k][0]
        faces.append((quad, colour, {"n": tuple(float(x) for x in n)}))
    return faces


def draw(p, ca, cb, w=420, h=560):
    faces = []
    for a, b in zip(ca, cb):
        f = box_from_segment(p[a, 0:3], p[b, 0:3], 0.05, (150, 128, 96))
        if f:
            faces += f
    faces += [(q, c, o) for q, c, o in
              [( [( -3, 0, -3), (3, 0, -3), (3, 0, 3), (-3, 0, 3)], (86, 76, 62), {"n": (0, 1, 0)})]]
    # frame the body, not the origin: by the third state it has drifted and left the shot
    c = p[:, 0:3].mean(0)
    # margin: the radius reaches the joints, not the tops of the limbs, and the head was being cropped
    rad = 1.45 * float(max(0.22, np.linalg.norm(p[:, 0:3] - c, axis=1).max()))
    tgt = (float(c[0]), float(max(0.12, c[1])), float(c[2]))
    eye = (tgt[0] + 0.9 * rad, tgt[1] + 0.75 * rad, tgt[2] + 1.6 * rad)
    return RS.aa(faces, eye, tgt, w, h, ss=2, fov=44, flat=[],
                 bg=(30, 28, 32), lights=[(2.2, 3.4, 2.6, 3.0)], ambient=0.34, gain=0.55, rim=0.15)


def main():
    p, ca, cb, rest, hits, worst = RD.simulate()
    err = RD.bone_error(p, ca, cb, rest)
    low = float(p[:, 1].min())
    print("ragdoll: %d joints, %d constraints, %d floor contacts" % (len(p), len(ca), hits))
    print("bone fidelity: worst during the fall %.1f%%, at rest %.1f%% (bones must stay bones)"
          % (100 * worst, 100 * err))
    print("rest: lowest joint y %.3f m, head y %.3f m (a body on the floor, not a net)"
          % (low, float(p[RD.IDX["head"], 1])))

    # three states: start, mid-fall, at rest
    p0, ca, cb, rest = RD.build()
    p0[:, 1] += 0.55
    ims = [draw(p0, ca, cb)]
    pm, _, _, _, _, _ = RD.simulate(steps=40)
    ims.append(draw(pm, ca, cb))
    ims.append(draw(p, ca, cb))
    sheet = Image.new("RGB", (420 * 3, 560), (30, 28, 32))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB"), (i * 420, 0))
    sheet.save("/opt/data/cache/scratch/ragdoll_sheet.png")
    print("wrote ragdoll_sheet.png")


if __name__ == "__main__":
    main()
