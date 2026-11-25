"""wubu3d_rig — a small humanoid rig and mesh builder, shared by both renderers.

Why this exists: the first raster figure was three cones and read as a traffic
cone. The fix is a proper skeleton with jointed limbs, a lofted torso, a head
that sits above the shoulders and boots below the coat hem — the same joints the
Blender rig drives, so preview and delivery agree on silhouette.

Conventions (from the character-forge standards):
  * one unit = one metre, ground at z = 0
  * adult proportions, 7.2 heads, total height 1.78 m
  * every limb is a tapered capsule with a cap at each joint, never two shapes
    meeting at a seam
  * .L on +X, .R on -X

No external dependencies. Angles in radians, rotations about X (swing) and Y
(lean) only — a walk cycle does not need a full matrix stack.
"""

import math

HEIGHT = 1.78

# rest-pose joints, metres. z is up, +y is forward.
JOINTS = {
    "pelvis":     (0.000, 0.000, 0.945),
    "spine":      (0.000, 0.010, 1.100),
    "chest":      (0.000, 0.000, 1.300),
    "neck":       (0.000, 0.000, 1.455),
    "head":       (0.000, 0.010, 1.560),
    "head_top":   (0.000, 0.015, 1.780),
    "clav.L":     (0.055, 0.000, 1.395),
    "shoulder.L": (0.215, 0.000, 1.395),
    "elbow.L":    (0.238, -0.005, 1.115),
    "wrist.L":    (0.245, 0.010, 0.870),
    "clav.R":     (-0.055, 0.000, 1.395),
    "shoulder.R": (-0.215, 0.000, 1.395),
    "elbow.R":    (-0.238, -0.005, 1.115),
    "wrist.R":    (-0.245, 0.010, 0.870),
    "hip.L":      (0.095, 0.000, 0.905),
    "knee.L":     (0.100, 0.010, 0.500),
    "ankle.L":    (0.100, 0.000, 0.085),
    "toe.L":      (0.100, 0.115, 0.035),
    "hip.R":      (-0.095, 0.000, 0.905),
    "knee.R":     (-0.100, 0.010, 0.500),
    "ankle.R":    (-0.100, 0.000, 0.085),
    "toe.R":      (-0.100, 0.115, 0.035),
}

PARENT = {
    "spine": "pelvis", "chest": "spine", "neck": "chest", "head": "neck",
    "clav.L": "chest", "shoulder.L": "clav.L", "elbow.L": "shoulder.L", "wrist.L": "elbow.L",
    "clav.R": "chest", "shoulder.R": "clav.R", "elbow.R": "shoulder.R", "wrist.R": "elbow.R",
    "hip.L": "pelvis", "knee.L": "hip.L", "ankle.L": "knee.L", "toe.L": "ankle.L",
    "hip.R": "pelvis", "knee.R": "hip.R", "ankle.R": "knee.R", "toe.R": "ankle.R",
}


def _rot_x(v, ang):
    """rotate a point about the origin around X (forward swing)"""
    y, z = v[1], v[2]
    c, s = math.cos(ang), math.sin(ang)
    return (v[0], y * c - z * s, y * s + z * c)


def _rot_y(v, ang):
    """rotate about Y (lean sideways)"""
    x, z = v[0], v[2]
    c, s = math.cos(ang), math.sin(ang)
    return (x * c + z * s, v[1], -x * s + z * c)


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def pose(phase, cfg=None, perf=None):
    """World-space joints for a walk cycle phase in [0, 1).

    Contact poses at 0 and 0.5, pass poses at 0.25 and 0.75 — the standard
    four-key cycle. Amplitude comes from cfg so a shot can scale the gait.
    """
    cfg = cfg or {}
    perf = perf or {}
    # performance overrides: a walk cycle is a loop, acting is a choice. `walk` scales
    # the loop to zero when the character is supposed to be still; the rest are
    # absolute poses an animator would key.
    walk = float(perf.get("walk", 1.0))
    swing = cfg.get("swing", 0.52) * walk
    arm = cfg.get("arm_swing", 0.36) * walk
    knee_lift = cfg.get("knee_lift", 0.55) * walk
    bob_amp = cfg.get("bob", 0.022) * walk
    crouch = float(perf.get("crouch", 0.0))
    pitch = float(perf.get("pitch", 0.0))       # torso lean forward, radians
    head_yaw = float(perf.get("head", 0.0))

    out = {}
    # pelvis rises twice per cycle
    bob = -bob_amp * math.cos(4 * math.pi * phase)
    lean = cfg.get("lean", 0.04)
    pelvis = _add(JOINTS["pelvis"], (0, -0.02 * walk, bob - crouch))
    out["pelvis"] = pelvis

    # spine / chest / neck / head: small counter-rotation and bob
    spine = _add(pelvis, _sub(JOINTS["spine"], JOINTS["pelvis"]))
    chest = _add(spine, _sub(JOINTS["chest"], JOINTS["spine"]))
    neck = _add(chest, _sub(JOINTS["neck"], JOINTS["chest"]))
    head = _add(neck, _sub(JOINTS["head"], JOINTS["neck"]))
    if pitch:
        spine = _rot_x(_sub(spine, pelvis), -pitch)
        spine = _add(pelvis, spine)
        chest = _add(spine, _rot_x(_sub(chest, pelvis), -pitch))
        neck = _add(chest, _rot_x(_sub(neck, chest), -pitch * 0.4))
        head = _add(neck, _rot_x(_sub(head, neck), -pitch * 0.2))
    if head_yaw:
        hx = _sub(head, neck)
        c, s_ = math.cos(head_yaw), math.sin(head_yaw)
        hx = (hx[0] * c - hx[1] * s_, hx[0] * s_ + hx[1] * c, hx[2])
        head = _add(neck, hx)
    head = _add(head, (0, 0, -bob * 0.5))
    out["spine"], out["chest"], out["neck"], out["head"] = spine, chest, neck, head
    out["head_top"] = _add(head, _sub(JOINTS["head_top"], JOINTS["head"]))

    for side, sign in (("L", 1.0), ("R", -1.0)):
        hip = _add(pelvis, _sub(JOINTS[f"hip.{side}"], JOINTS["pelvis"]))
        out[f"hip.{side}"] = hip
        # legs alternate, half a cycle apart
        ph = phase if side == "L" else (phase + 0.5) % 1.0
        thigh_ang = swing * math.cos(2 * math.pi * ph)
        knee_ang = knee_lift * max(0.0, math.sin(2 * math.pi * ph + math.pi * 0.5)) ** 2

        knee_rest = _sub(JOINTS[f"knee.{side}"], JOINTS[f"hip.{side}"])
        ankle_rest = _sub(JOINTS[f"ankle.{side}"], JOINTS[f"knee.{side}"])
        toe_rest = _sub(JOINTS[f"toe.{side}"], JOINTS[f"ankle.{side}"])

        knee = _add(hip, _rot_x(knee_rest, -thigh_ang))
        ankle = _add(knee, _rot_x(ankle_rest, -thigh_ang + knee_ang))
        toe = _add(ankle, _rot_x(toe_rest, -thigh_ang + knee_ang * 0.4))
        out[f"knee.{side}"], out[f"ankle.{side}"], out[f"toe.{side}"] = knee, ankle, toe

        clav = _add(chest, _sub(JOINTS[f"clav.{side}"], JOINTS["chest"]))
        sh = _add(chest, _sub(JOINTS[f"shoulder.{side}"], JOINTS["chest"]))
        out[f"clav.{side}"], out[f"shoulder.{side}"] = clav, sh
        # arms swing opposite the same-side leg
        a_ang = -arm * math.cos(2 * math.pi * ph)
        abs_key = "arm_r" if side == "R" else "arm_l"
        if abs_key in perf:
            a_ang = float(perf[abs_key])
        if cfg.get("carry") == side:      # a hand holding a lantern stays low
            a_ang = cfg.get("carry_angle", -0.30)
        el_rest = _sub(JOINTS[f"elbow.{side}"], JOINTS[f"shoulder.{side}"])
        wr_rest = _sub(JOINTS[f"wrist.{side}"], JOINTS[f"elbow.{side}"])
        elbow = _add(sh, _rot_x(el_rest, -a_ang))
        bend = cfg.get("elbow_bend", 0.22)
        wrist = _add(elbow, _rot_x(wr_rest, -a_ang - bend))
        out[f"elbow.{side}"], out[f"wrist.{side}"] = elbow, wrist
    return out


# ── mesh primitives ──────────────────────────────────────────────────────────


def _ring(center, axis, radius, segs, squash=1.0):
    """a circle of points perpendicular to `axis`"""
    ax = _norm(axis)
    up = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = _norm(_cross(ax, up))
    v = _cross(ax, u)
    pts = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        pts.append(_add(center, (
            (u[0] * math.cos(a) + v[0] * math.sin(a)) * radius,
            (u[1] * math.cos(a) + v[1] * math.sin(a)) * radius * squash,
            (u[2] * math.cos(a) + v[2] * math.sin(a)) * radius,
        )))
    return pts


def _norm(a):
    l = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1e-9
    return (a[0] / l, a[1] / l, a[2] / l)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def capsule(verts, tris, p0, p1, r0, r1, color, segs=8, cap=True):
    """tapered limb with rounded caps — the shape that keeps joints from pinching"""
    axis = _sub(p1, p0)
    base = len(verts)
    rings = [(p0, r0), (p1, r1)]
    for pt, r in rings:
        for q in _ring(pt, axis, r, segs):
            verts.append((q[0], q[1], q[2], color))
    for k in range(segs):
        k2 = (k + 1) % segs
        tris.append((base + k, base + k2, base + segs + k2))
        tris.append((base + k, base + segs + k2, base + segs + k))
    if cap:
        # hemispherical caps: two extra rings squeezed toward each end
        for (pt, r, sgn) in ((p0, r0, -1.0), (p1, r1, 1.0)):
            d = _norm(axis)
            for t, rr in ((0.55, 0.80), (0.85, 0.45)):
                c = _add(pt, (d[0] * r * sgn * t, d[1] * r * sgn * t, d[2] * r * sgn * t))
                b2 = len(verts)
                for q in _ring(c, d, r * rr, segs):
                    verts.append((q[0], q[1], q[2], color))
                prev = base if sgn < 0 else base + segs
                if sgn > 0:
                    prev = base + segs
                for k in range(segs):
                    k2 = (k + 1) % segs
                    if sgn < 0:
                        tris.append((prev + k2, prev + k, b2 + k))
                        tris.append((prev + k2, b2 + k, b2 + k2))
                    else:
                        tris.append((prev + k, prev + k2, b2 + k2))
                        tris.append((prev + k, b2 + k2, b2 + k))
                prev = b2
                base_cap = b2


def sphere(verts, tris, center, radius, color, segs=10, rings=6, scale=(1, 1, 1)):
    base = len(verts)
    verts.append((center[0], center[1], center[2] + radius * scale[2], color))
    for i in range(1, rings):
        phi = math.pi * i / rings
        z = math.cos(phi) * radius * scale[2]
        r = math.sin(phi) * radius
        for k in range(segs):
            a = 2 * math.pi * k / segs
            verts.append((center[0] + math.cos(a) * r * scale[0],
                          center[1] + math.sin(a) * r * scale[1],
                          center[2] + z, color))
    verts.append((center[0], center[1], center[2] - radius * scale[2], color))
    bottom = len(verts) - 1
    for k in range(segs):
        k2 = (k + 1) % segs
        tris.append((base, base + 1 + k2, base + 1 + k))
    for i in range(rings - 2):
        a0 = base + 1 + i * segs
        a1 = a0 + segs
        for k in range(segs):
            k2 = (k + 1) % segs
            tris.append((a0 + k, a0 + k2, a1 + k2))
            tris.append((a0 + k, a1 + k2, a1 + k))
    a0 = base + 1 + (rings - 2) * segs
    for k in range(segs):
        k2 = (k + 1) % segs
        tris.append((a0 + k, a0 + k2, bottom))


def tube(verts, tris, rings_pts, color, close_top=True, close_bottom=True):
    """loft a list of equal-length point rings into a tube"""
    base = len(verts)
    n = len(rings_pts[0])
    for rp in rings_pts:
        for q in rp:
            verts.append((q[0], q[1], q[2], color))
    for i in range(len(rings_pts) - 1):
        a0 = base + i * n
        a1 = a0 + n
        for k in range(n):
            k2 = (k + 1) % n
            tris.append((a0 + k, a0 + k2, a1 + k2))
            tris.append((a0 + k, a1 + k2, a1 + k))
    if close_bottom:
        c = len(verts)
        pts = rings_pts[0]
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        cz = sum(p[2] for p in pts) / n
        verts.append((cx, cy, cz, color))
        for k in range(n):
            tris.append((base + (k + 1) % n, base + k, c))
    if close_top:
        c = len(verts)
        pts = rings_pts[-1]
        cx = sum(p[0] for p in pts) / n
        cy = sum(p[1] for p in pts) / n
        cz = sum(p[2] for p in pts) / n
        verts.append((cx, cy, cz, color))
        off = base + (len(rings_pts) - 1) * n
        for k in range(n):
            tris.append((off + k, off + (k + 1) % n, c))


def build(color=(0.10, 0.10, 0.12), skin=(0.55, 0.42, 0.34), phase=0.0, cfg=None,
          hood=True, coat=True, perf=None):
    """Return (verts, tris) for one posed character. Colors are 0..1 floats."""
    verts, tris = [], []
    j = pose(phase, cfg, perf)
    cc = tuple(int(min(1.0, max(0.0, v)) * 255) for v in color)
    sc = tuple(int(min(1.0, max(0.0, v)) * 255) for v in skin)

    # torso: pelvis -> chest -> shoulders, elliptical cross-sections
    rings = []
    for z0, z1, rx, ry in ((0.86, 1.02, 0.135, 0.105), (1.02, 1.20, 0.150, 0.110),
                           (1.20, 1.34, 0.172, 0.118), (1.34, 1.44, 0.165, 0.112)):
        zz = z0 + (z1 - z0) * 0.5
        pts = []
        for k in range(12):
            a = 2 * math.pi * k / 12
            pts.append((j["pelvis"][0] + math.cos(a) * rx,
                        j["pelvis"][1] + math.sin(a) * ry, zz))
        rings.append(pts)
    tube(verts, tris, rings, cc)

    # neck
    capsule(verts, tris, (j["neck"][0], j["neck"][1], 1.40),
            (j["neck"][0], j["neck"][1], 1.52), 0.048, 0.045, sc, 8, cap=False)

    # head, slightly egg-shaped, forward of the spine
    sphere(verts, tris, (j["head"][0], j["head"][1] + 0.010, 1.620), 0.104,
           tuple(int(c * 0.55) for c in cc), segs=14, rings=10, scale=(1.0, 1.06, 1.14))

    # face: a darker plane recessed under the hood, with two bright slits. Without the
    # recessed plane the hood opening reads as a bright hole, not a face in shadow.

    eye = (255, 196, 128)
    for sx in (-0.030, 0.030):
        _box(verts, tris, (j["head"][0] + sx, j["head"][1] + 0.098, 1.634),
             (0.036, 0.010, 0.013), eye)

    if hood:
        # a cowl with the front left open, so the face reads instead of a cone
        hc = tuple(int(min(1.0, v * 1.15) * 255) for v in color)
        # a cowl that sits behind and around the head. The apex leans back so it reads as
        # cloth over a skull, not a cone growing out of the shoulders.
        gap = 1.30
        a0, a1 = math.pi / 2 + gap / 2, math.pi / 2 + 2 * math.pi - gap / 2
        rings = []
        for t, r, dz, dy in ((0.0, 0.165, 0.00, -0.020), (0.35, 0.170, 0.10, -0.030),
                             (0.65, 0.152, 0.20, -0.045), (0.85, 0.110, 0.28, -0.060),
                             (1.0, 0.050, 0.33, -0.075)):
            z = j["neck"][2] + dz
            pts = []
            for k in range(16):
                a = a0 + (a1 - a0) * k / 15
                pts.append((math.cos(a) * r, math.sin(a) * r * 1.02 + dy, z))
            rings.append(pts)
        tube(verts, tris, rings, hc, close_top=False, close_bottom=False)

    # joint caps: a sphere at every hinge stops capsules from seaming
    for name, r in (("elbow.L", 0.048), ("elbow.R", 0.048),
                    ("hip.L", 0.082), ("hip.R", 0.082),
                    ("knee.L", 0.052), ("knee.R", 0.052)):
        pt = j[name]
        sphere(verts, tris, pt, r, cc, segs=8, rings=5)

    # arms
    for side in ("L", "R"):
        sh, el, wr = j[f"shoulder.{side}"], j[f"elbow.{side}"], j[f"wrist.{side}"]
        capsule(verts, tris, sh, el, 0.058, 0.048, cc, 10)
        capsule(verts, tris, el, wr, 0.046, 0.038, cc, 10)
        sphere(verts, tris, wr, 0.034, cc, segs=8, rings=5)

    # legs
    for side in ("L", "R"):
        hp, kn, an = j[f"hip.{side}"], j[f"knee.{side}"], j[f"ankle.{side}"]
        capsule(verts, tris, hp, kn, 0.082, 0.062, cc, 8)
        capsule(verts, tris, kn, an, 0.060, 0.045, cc, 8)
        # boot: a box from ankle forward
        bx = an[0]
        _box(verts, tris, (bx, an[1] + 0.050, 0.038), (0.092, 0.215, 0.076),
             (28, 26, 30))

    if coat:
        rings = []
        for z, r in ((1.38, 0.172), (1.20, 0.180), (1.00, 0.196), (0.82, 0.210), (0.62, 0.222)):
            pts = []
            for k in range(14):
                a = 2 * math.pi * k / 14
                fold = 1.0 + 0.030 * math.sin(7 * a) * (1.0 - (z - 0.30) / 0.75)
                pts.append((math.cos(a) * r * fold, math.sin(a) * r * 0.86 * fold, z))
            rings.append(pts)
        for rp in rings:
            shifted = [(p[0] + j["pelvis"][0], p[1] + j["pelvis"][1], p[2]) for p in rp]
            rp[:] = shifted
        tube(verts, tris, rings, cc, close_top=False, close_bottom=False)
    return verts, tris


def _box(verts, tris, center, size, color):
    base = len(verts)
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    for (x, y, z) in ((-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                      (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)):
        verts.append((center[0] + x, center[1] + y, center[2] + z, color))
    for f in ((0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1),
              (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)):
        tris.append((base + f[0], base + f[1], base + f[2]))


def gait_phase(c, frame):
    """shared by the mesh exporter and the lantern position, so they never drift"""
    f0, f1 = int(c.get("walk", [0, 1])[0]), int(c.get("walk", [0, 1])[1])
    path = c["path"]
    length = math.dist(path[0], path[1])
    stride = c.get("stride", 0.85)
    window = max(1, f1 - f0)
    ph = ((frame - f0) / window) * max(1.0, length / stride)
    return ph - math.floor(ph)


def lantern(c, frame, yaw, origin):
    """world position of the lantern in the character's right hand"""
    j = pose(gait_phase(c, frame), c.get("gait") or {})
    x, y, z = j["wrist.R"]
    z -= 0.07
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (x * cy - y * sy + origin[0], x * sy + y * cy + origin[1], z)
