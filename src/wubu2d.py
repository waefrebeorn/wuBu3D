"""wubu2d — flat cartoon characters drawn in code, on transparent canvas.

The format that actually works: 2D cutout characters in front of 3D sets. They are cheap
to draw, they can act (a pose is a handful of numbers), they never lose their face between
shots, and a black outline reads at any size.

Everything is drawn at 4x and downsampled, so the outline is clean instead of jagged.
"""
import math
from PIL import Image, ImageDraw

SS = 4                      # supersample
OUTLINE = (17, 17, 19, 255)
PAPER = (247, 243, 234, 255)
INK = (24, 24, 28, 255)

EXPRESSIONS = {
    #            eye_open, brow_lift, mouth_w, mouth_h, mouth_curve
    "neutral":  (1.00, 0.00, 0.030, 0.010, 0.00),
    "grin":     (0.92, 0.05, 0.062, 0.040, -0.02),
    "shock":    (1.18, 0.10, 0.034, 0.046, 0.00),
    "squint":   (0.34, -0.03, 0.040, 0.012, 0.01),
    "smile":    (0.96, 0.02, 0.050, 0.026, -0.012),
    "angry":    (0.86, -0.06, 0.044, 0.020, 0.012),
    "sad":      (0.80, -0.05, 0.026, 0.008, 0.014),
}

POSES = {
    #          arm_l, arm_r, leg_l, leg_r, lean, head_tilt
    "stand":   (0.20, -0.20, 0.06, -0.06, 0.00, 0.00),
    "walk_a":  (0.55, -0.55, 0.30, -0.30, 0.02, 0.02),
    "walk_b":  (-0.55, 0.55, -0.30, 0.30, 0.02, -0.02),
    "point":   (0.10, -1.15, 0.10, -0.10, 0.03, 0.06),
    "shrug":   (0.95, -0.95, 0.05, -0.05, -0.02, 0.03),
    "hold":    (0.75, -0.75, 0.05, -0.05, 0.04, 0.00),
}


def _limb(d, p0, ang, length, w, colour):
    """a limb as a thick round-capped line with an outline"""
    p1 = (p0[0] + math.sin(ang) * length, p0[1] + math.cos(ang) * length)
    d.line([p0, p1], fill=OUTLINE, width=w + 8 * SS // 2, joint="curve")
    d.line([p0, p1], fill=colour, width=w, joint="curve")
    return p1


def _capsule(d, p0, p1, w, colour):
    ow = int(w * 0.34)
    d.line([p0, p1], fill=OUTLINE, width=int(w + 2 * ow), joint="curve")
    d.line([p0, p1], fill=colour, width=int(w), joint="curve")
    for p in (p0, p1):
        d.ellipse([p[0] - w / 2 - ow, p[1] - w / 2 - ow,
                   p[0] + w / 2 + ow, p[1] + w / 2 + ow], fill=OUTLINE)
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=colour)


def draw(pose="stand", expression="neutral", body_colour=(74, 96, 148, 255),
         trouser=(52, 58, 74, 255), size=(512, 768), frame_seed=0):
    """A puppet, not a drawing: every part is built between two joints, so a limb can
    never detach from the body. Joint heights are fractions of the canvas height."""
    W, H = size[0] * SS, size[1] * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if isinstance(pose, dict):
        arm_l, arm_r, leg_l, leg_r, lean, tilt = (pose.get("arm_l", 0.0), pose.get("arm_r", 0.0),
                                                  pose.get("leg_l", 0.0), pose.get("leg_r", 0.0),
                                                  pose.get("lean", 0.0), pose.get("tilt", 0.0))
    else:
        arm_l, arm_r, leg_l, leg_r, lean, tilt = POSES[pose]
    eye_open, brow, mouth_w, mouth_h, curve = EXPRESSIONS[expression]

    # ── skeleton, in canvas units
    cx = W * 0.5 + lean * W * 0.25
    hip_y = H * 0.520
    neck_y = H * 0.300
    head_r = H * 0.098
    head_c = (cx, neck_y - head_r * 0.78 + tilt * H * 0.010)
    sh_y = neck_y + H * 0.020
    sh_x = H * 0.118
    hip_x = H * 0.055

    leg_len = H * 0.205
    arm_len = H * 0.135
    leg_w = H * 0.030
    arm_w = H * 0.026

    def joint(base, ang, length):
        return (base[0] + math.sin(ang) * length, base[1] + math.cos(ang) * length)

    # ── back limbs first
    for sign, ang, col in ((1, leg_l, trouser), (-1, leg_r, trouser)):
        hip = (cx + sign * hip_x, hip_y)
        knee = joint(hip, ang * sign, leg_len)
        foot = joint(knee, ang * sign * 0.35, leg_len)
        _capsule(d, hip, knee, leg_w, col)
        _capsule(d, knee, foot, leg_w * 0.92, col)
        d.rounded_rectangle([foot[0] - H * 0.030, foot[1] - H * 0.012,
                             foot[0] + H * 0.052, foot[1] + H * 0.024],
                            radius=int(H * 0.012), fill=OUTLINE)
        d.rounded_rectangle([foot[0] - H * 0.023, foot[1] - H * 0.006,
                             foot[0] + H * 0.045, foot[1] + H * 0.018],
                            radius=int(H * 0.009), fill=(32, 34, 40, 255))

    # ── torso: a polygon anchored on the hip line and the shoulder line
    lw, rw = H * 0.072, H * 0.062     # half width at shoulder / waist
    torso = []
    steps = 18
    for i in range(steps + 1):        # right side, shoulder -> hip
        t = i / steps
        y = sh_y + (hip_y - sh_y) * t
        x = cx + (rw + (lw - rw) * (1 - t)) * (1.0 - 0.10 * math.sin(math.pi * t))
        torso.append((x, y))
    for i in range(steps + 1):        # left side, hip -> shoulder
        t = 1 - i / steps
        y = sh_y + (hip_y - sh_y) * t
        x = cx - (rw + (lw - rw) * (1 - t)) * (1.0 - 0.10 * math.sin(math.pi * t))
        torso.append((x, y))
    d.polygon(torso, fill=OUTLINE)
    inner = [(cx + (x - cx) * 0.90, sh_y + (y - sh_y) * 0.97) for (x, y) in torso]
    d.polygon(inner, fill=body_colour)

    # ── front arm
    for sign, ang in ((1, arm_l), (-1, arm_r)):
        sh = (cx + sign * sh_x * 0.86, sh_y + H * 0.012)
        elbow = joint(sh, ang * sign, arm_len)
        hand = joint(elbow, ang * sign * 1.15, arm_len * 0.95)
        _capsule(d, sh, elbow, arm_w, body_colour)
        _capsule(d, elbow, hand, arm_w * 0.90, body_colour)
        d.ellipse([hand[0] - H * 0.022, hand[1] - H * 0.022,
                   hand[0] + H * 0.022, hand[1] + H * 0.022], fill=OUTLINE)
        d.ellipse([hand[0] - H * 0.016, hand[1] - H * 0.016,
                   hand[0] + H * 0.016, hand[1] + H * 0.016], fill=PAPER)

    # ── neck and head
    _capsule(d, (cx, neck_y + H * 0.012), (cx, neck_y - head_r * 0.55), H * 0.030, PAPER)
    d.ellipse([head_c[0] - head_r - H * 0.008, head_c[1] - head_r - H * 0.008,
               head_c[0] + head_r + H * 0.008, head_c[1] + head_r + H * 0.008], fill=OUTLINE)
    d.ellipse([head_c[0] - head_r, head_c[1] - head_r,
               head_c[0] + head_r, head_c[1] + head_r], fill=PAPER)

    eye_dx = head_r * 0.40
    eye_y = head_c[1] + head_r * 0.04
    er = head_r * 0.16 * eye_open
    for sign in (-1, 1):
        ex = head_c[0] + sign * eye_dx
        if eye_open < 0.40:
            d.line([ex - er * 1.8, eye_y, ex + er * 1.8, eye_y], fill=INK, width=5 * SS)
        else:
            d.ellipse([ex - er * 0.70, eye_y - er, ex + er * 0.70, eye_y + er], fill=INK)
        by = eye_y - head_r * (0.42 + brow * 3.0)
        d.line([ex - head_r * 0.20, by + brow * head_r * 0.8,
                ex + head_r * 0.20, by - brow * head_r * 0.8], fill=INK, width=4 * SS)

    my = head_c[1] + head_r * 0.48
    mw = head_r * mouth_w * 8.0
    mh = max(2 * SS, head_r * mouth_h * 7.0)
    d.ellipse([head_c[0] - mw, my - mh, head_c[0] + mw, my + mh], fill=INK)

    return img.resize(size, Image.LANCZOS)


if __name__ == "__main__":
    import os
    out = "/opt/data/work/wubu3d/out/char2d"
    os.makedirs(out, exist_ok=True)
    for pose in ("stand", "walk_a", "point", "shrug"):
        for expr in ("neutral", "grin"):
            im = draw(pose, expr)
            im.save(f"{out}/{pose}_{expr}.png")
    print("wrote", os.listdir(out))
