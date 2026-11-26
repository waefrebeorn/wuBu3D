"""wubu3d_char — one character, built as a single mesh.

The previous cast was seven primitives parented to an empty: it read as shapes glued
together because it *was* shapes glued together. This builds one body from lofted
rings along a skeleton — torso, neck, head, arms, legs, feet — with consistent
tapering, so the silhouette is a figure rather than a stack.

Units are metres, ground at z = 0, total height 1.78 (7.2 heads, adult).
Blender and the rasteriser both read the same vertex/triangle lists, so the preview and
the delivery are the same character.
"""

import math

HEIGHT = 1.78

# ── body plan ────────────────────────────────────────────────────────────────
# (z, half-width x, half-depth y) for the torso loft
TORSO = [
    (0.94, 0.150, 0.098),   # hips
    (1.06, 0.152, 0.100),
    (1.18, 0.163, 0.104),
    (1.30, 0.180, 0.110),
    (1.40, 0.196, 0.114),   # shoulders
]
NECK = [(1.40, 0.058, 0.052), (1.50, 0.052, 0.048), (1.545, 0.050, 0.047)]
HEAD = [
    (1.545, 0.058, 0.056),   # jaw
    (1.578, 0.082, 0.086),   # cheek
    (1.618, 0.096, 0.100),   # brow
    (1.660, 0.094, 0.098),
    (1.700, 0.078, 0.084),
    (1.734, 0.044, 0.048),   # crown
]
ARM = {"shoulder": (0.196, 0.0, 1.392), "elbow": (0.222, 0.010, 1.115),
       "wrist": (0.232, 0.030, 0.875)}
LEG = {"hip": (0.098, 0.0, 0.905), "knee": (0.104, 0.012, 0.500),
       "ankle": (0.104, 0.0, 0.078)}

C_COAT = (0.30, 0.31, 0.37)
C_SKIN = (0.56, 0.43, 0.35)
C_BOOT = (0.11, 0.11, 0.13)
C_HOOD = (0.24, 0.25, 0.31)
C_EYE = (0.95, 0.80, 0.55)


def _ring(z, rx, ry, segs, cx=0.0, cy=0.0, colour=C_COAT):
    pts = []
    for k in range(segs):
        a = 2.0 * math.pi * k / segs
        pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry, z))
    return pts


def _ring_axis(center, axis, radius, segs, colour=C_COAT, squash=1.0):
    """a circle perpendicular to `axis` — used for limbs"""
    ax = _norm(axis)
    up = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = _norm(_cross(ax, up))
    v = _cross(ax, u)
    pts = []
    for k in range(segs):
        a = 2.0 * math.pi * k / segs
        pts.append((center[0] + (u[0] * math.cos(a) + v[0] * math.sin(a)) * radius,
                    center[1] + (u[1] * math.cos(a) + v[1] * math.sin(a)) * radius * squash,
                    center[2] + (u[2] * math.cos(a) + v[2] * math.sin(a)) * radius))
    return pts


def _norm(a):
    l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1e-9
    return (a[0] / l, a[1] / l, a[2] / l)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _axis(a, b):
    return _norm((b[0] - a[0], b[1] - a[1], b[2] - a[2]))


class Builder:
    def __init__(self):
        self.v = []
        self.t = []
        self.groups = []          # (name, first_vert, last_vert) for skinning

    def add_loft(self, rings, colour, cap_start=False, cap_end=False, group=None):
        """stitch a list of equal-length rings into a tube"""
        start = len(self.v)
        n = len(rings[0])
        for rp in rings:
            for p in rp:
                self.v.append((p[0], p[1], p[2], colour))
        for i in range(len(rings) - 1):
            a0 = start + i * n
            a1 = a0 + n
            for k in range(n):
                k2 = (k + 1) % n
                self.t.append((a0 + k, a0 + k2, a1 + k2))
                self.t.append((a0 + k, a1 + k2, a1 + k))
        if cap_start:
            self._cap(start, rings[0], colour, flip=True)
        if cap_end:
            self._cap(start + (len(rings) - 1) * n, rings[-1], colour, flip=False)
        if group:
            self.groups.append((group, start, len(self.v) - 1))
        return start

    def _cap(self, base, ring, colour, flip):
        n = len(ring)
        cx = sum(p[0] for p in ring) / n
        cy = sum(p[1] for p in ring) / n
        cz = sum(p[2] for p in ring) / n
        c = len(self.v)
        self.v.append((cx, cy, cz, colour))
        for k in range(n):
            k2 = (k + 1) % n
            if flip:
                self.t.append((base + k2, base + k, c))
            else:
                self.t.append((base + k, base + k2, c))

    def add_box(self, center, size, colour, group=None, y_offset=0.0):
        start = len(self.v)
        hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
        for (x, y, z) in ((-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                          (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)):
            self.v.append((center[0] + x, center[1] + y + y_offset, center[2] + z, colour))
        for f in ((0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1),
                  (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)):
            self.t.append((start + f[0], start + f[1], start + f[2]))
        if group:
            self.groups.append((group, start, len(self.v) - 1))

    def add_limb(self, joints, radii, segs, colour, prefix):
        """loft a limb along a chain of joints, one ring per joint plus mid rings"""
        rings, marks = [], []
        for i in range(len(joints) - 1):
            a, b = joints[i], joints[i + 1]
            n_seg = 3
            for s in range(n_seg):
                t = s / n_seg
                c = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                     a[2] + (b[2] - a[2]) * t)
                r = radii[i] + (radii[i + 1] - radii[i]) * t
                rings.append(_ring_axis(c, _axis(a, b), r, segs, colour))
        a, b = joints[-2], joints[-1]
        rings.append(_ring_axis(b, _axis(a, b), radii[-1], segs, colour))
        self.add_loft(rings, colour, cap_start=True, cap_end=True, group=prefix)


def build(hood=True, jacket=True):
    b = Builder()
    SEG = 12

    # torso
    torso_rings = [_ring(z, rx, ry, SEG) for (z, rx, ry) in TORSO]
    b.add_loft(torso_rings, C_COAT, cap_start=True, group="spine")

    # neck + head
    neck_rings = [_ring(z, rx, ry, SEG, colour=C_SKIN) for (z, rx, ry) in NECK]
    b.add_loft(neck_rings, C_SKIN, group="head")
    head_rings = [_ring(z, rx, ry, SEG, colour=C_SKIN) for (z, rx, ry) in HEAD]
    b.add_loft(head_rings, C_SKIN, cap_end=True, group="head")

    # face hardware: eyes set into the brow, and a nose so the profile is not a slab
    for sx in (-0.034, 0.034):
        b.add_box((sx, 0.098, 1.640), (0.026, 0.012, 0.013), C_EYE, group="head")
    b.add_box((0.0, 0.104, 1.612), (0.024, 0.026, 0.034), C_SKIN, group="head")

    # arms: upper and lower as separate lofts, so the elbow is a joint, not a bend
    for side, sgn in (("L", 1.0), ("R", -1.0)):
        sh = (sgn * ARM["shoulder"][0], ARM["shoulder"][1], ARM["shoulder"][2])
        el = (sgn * ARM["elbow"][0], ARM["elbow"][1], ARM["elbow"][2])
        wr = (sgn * ARM["wrist"][0], ARM["wrist"][1], ARM["wrist"][2])
        b.add_limb([sh, el], [0.062, 0.050], 8, C_COAT, f"arm.{side}")
        b.add_limb([el, wr], [0.050, 0.040], 8, C_COAT, f"fore.{side}")
        b.add_box((wr[0], wr[1] + 0.012, wr[2] - 0.048), (0.055, 0.070, 0.100),
                  C_SKIN, group=f"fore.{side}")

    # legs with boots, feet forward
    for side, sgn in (("L", 1.0), ("R", -1.0)):
        hp = (sgn * LEG["hip"][0], LEG["hip"][1], LEG["hip"][2])
        kn = (sgn * LEG["knee"][0], LEG["knee"][1], LEG["knee"][2])
        an = (sgn * LEG["ankle"][0], LEG["ankle"][1], LEG["ankle"][2])
        b.add_limb([hp, (kn[0], kn[1], kn[2] + 0.045)], [0.094, 0.064], 8, C_COAT, f"leg.{side}")
        knee_c = (kn[0], kn[1] + 0.012, kn[2])
        b.add_loft([_ring_axis((knee_c[0], knee_c[1], knee_c[2] + 0.055), (0, 0, -1), 0.066, 8, C_COAT),
                    _ring_axis(knee_c, (0, 0, -1), 0.078, 8, C_COAT),
                    _ring_axis((knee_c[0], knee_c[1], knee_c[2] - 0.050), (0, 0, -1), 0.070, 8, C_COAT)],
                   C_COAT, group=f"leg.{side}")
        b.add_limb([(kn[0], kn[1], kn[2] - 0.045), an], [0.070, 0.052], 8, C_COAT, f"shin.{side}")
        b.add_box((an[0], an[1] + 0.060, 0.045), (0.112, 0.265, 0.090),
                  C_BOOT, group=f"foot.{side}")

    # short jacket: covers the torso, stops at the hip so the legs stay visible
    if jacket:
        jr = []
        for (z, rx, ry) in ((1.395, 0.208, 0.126), (1.28, 0.194, 0.122),
                            (1.16, 0.176, 0.116), (1.04, 0.166, 0.112),
                            (0.985, 0.170, 0.114)):
            jr.append(_ring(z, rx, ry, SEG, colour=C_COAT))
        b.add_loft(jr, C_COAT, cap_start=False, cap_end=False, group="spine")

    # hood: a cowl behind the head with the face left open
    if hood:
        a0, a1 = math.pi * 0.5 + 1.45, math.pi * 0.5 + 2 * math.pi - 1.45
        rings = []
        for t, r, z in ((0.0, 0.118, 1.455), (0.38, 0.126, 1.545), (0.72, 0.112, 1.650),
                        (1.0, 0.058, 1.760)):
            pts = []
            for k in range(14):
                a = a0 + (a1 - a0) * k / 13
                pts.append((math.cos(a) * r, math.sin(a) * r * 1.08 + 0.055, z))
            rings.append(pts)
        b.add_loft(rings, C_HOOD, group="head")
    return b.v, b.t, b.groups


if __name__ == "__main__":
    v, t, g = build()
    zs = [p[2] for p in v]
    xs = [p[0] for p in v]
    print(f"verts {len(v)}  tris {len(t)}  height {max(zs):.3f}  width {max(xs)-min(xs):.3f}")
    print("groups:", [n for n, _, _ in g])
