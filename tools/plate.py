"""plate — put a code-rendered character inside a photographic plate.

The brainrot reference ("Creative DIY Brainrot") is not a rendering achievement: the characters are
simple, and every shot's weight comes from a photographic plate — a temple garden at dusk, a fleshy
cave, a floor of petals. The skill file says it plainly: paint the world, do not simulate it. A plate
reads as a place; a hand-built set of the same shot reads as a diagram.

So this module does the four things compositing actually needs, in order:

    matte()       cut the render out of its key colour, with a one-pixel erosion so no fringe shows
    shadow()      darken the plate under the character, soft and offset along the plate's light
    match()       pull the character's LAB statistics toward the plate's local region
    composite()   the three above, plus a depth-of-field blur of the plate itself

Nothing here generates a plate. Plates come from an image model or a camera; this puts work into one.
"""

import numpy as np
from PIL import Image, ImageFilter

import grade as G


def matte(render, key=(255, 0, 255), tol=38, erode=True):
    """render: PIL RGB on a solid key colour. Returns (rgb, alpha uint8)."""
    a = np.asarray(render.convert("RGB"), np.float32)
    d = np.abs(a - np.array(key, np.float32)).sum(2)
    alpha = np.clip((d - tol) / 60.0, 0.0, 1.0)
    if erode:
        # a sharp key leaves a one-pixel halo of blended edge colour; eroding one pixel removes it
        m = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))
        alpha = np.asarray(m, np.float32) / 255.0
    return render.convert("RGB"), (alpha * 255).astype(np.uint8)


def shadow(plate, anchor, radius, strength=0.55, squash=0.42, offset=(0, 0)):
    """Multiply the plate toward black under the character, in an ellipse."""
    p = np.asarray(plate, np.float32).copy()
    h, w = p.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = anchor[0] + offset[0], anchor[1] + offset[1]
    r = np.hypot((xx - cx) / max(1, radius), (yy - cy) / max(1, radius * squash))
    m = np.clip(1.0 - r, 0.0, 1.0) ** 1.4
    k = 1.0 - strength * m
    p *= k[..., None]
    return Image.fromarray(np.clip(p, 0, 255).astype(np.uint8))


def local_stats(plate, anchor, radius):
    w, h = plate.size
    cx, cy = anchor
    box = (max(0, int(cx - radius)), max(0, int(cy - radius * 1.6)),
           min(w, int(cx + radius)), min(h, int(cy + radius * 1.6)))
    region = plate.crop(box)
    return G.stats(region)


def match(char_rgb, plate, anchor, radius, strength=0.75):
    """Colour-match the character to the plate AROUND its feet, not to the whole frame: a global
    match turns a character lit by lanterns into the average of a dark sky."""
    tgt = local_stats(plate, anchor, radius)
    return G.match(char_rgb, tgt, strength=strength)


def composite(plate, char_rgb, alpha, anchor, shadow_radius=None, shadow_strength=0.5,
              match_strength=0.75, plate_blur=0.0):
    """anchor: (x, y) of the character's feet in plate pixels."""
    out = plate.convert("RGB")
    if plate_blur > 0:
        out = out.filter(ImageFilter.GaussianBlur(plate_blur))
    r = shadow_radius or max(8, int(alpha.shape[1] * 0.22))
    out = shadow(out, anchor, r, strength=shadow_strength)

    # Match on the CHARACTER ONLY. The render still carries its key-colour background, and that is
    # 66 % of the frame: LAB statistics over the whole buffer drag every pixel toward the key, which
    # is why the first composites came back as a flat magenta figure with clean edges.
    cr = char_rgb
    if match_strength > 0:
        a3 = np.asarray(alpha, np.float32)[..., None] / 255.0
        ca = np.asarray(char_rgb.convert("RGB"), np.float32)
        only = ca * a3 + (1.0 - a3) * ca[a3[..., 0] > 0.5].mean(0)   # neutral fill, character stats
        cr = match(Image.fromarray(np.clip(only, 0, 255).astype(np.uint8)), out, anchor, r,
                   strength=match_strength)
        cr = Image.fromarray((np.asarray(cr.convert("RGB"), np.float32) * a3 +
                              ca * (1 - a3)).astype(np.uint8))

    W, H = out.size
    cw, ch = cr.size
    x0 = int(anchor[0] - cw / 2)
    y0 = int(anchor[1] - ch)
    base = np.asarray(out, np.float32).copy()
    ch_arr = np.asarray(cr, np.float32)
    al = np.asarray(alpha, np.float32)[..., None] / 255.0

    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(W, x0 + cw), min(H, y0 + ch)
    if xs1 <= xs0 or ys1 <= ys0:
        return out
    cx0, cy0 = xs0 - x0, ys0 - y0
    cx1, cy1 = cx0 + (xs1 - xs0), cy0 + (ys1 - ys0)
    region = base[ys0:ys1, xs0:xs1]
    a = al[cy0:cy1, cx0:cx1]
    base[ys0:ys1, xs0:xs1] = region * (1 - a) + ch_arr[cy0:cy1, cx0:cx1] * a
    # return the alpha in PLATE space: callers measuring the composite need it at the same size,
    # not at the character's size, or every index check fails on shape
    placed = np.zeros((H, W), np.uint8)
    placed[ys0:ys1, xs0:xs1] = (al[cy0:cy1, cx0:cx1, 0] * 255).astype(np.uint8)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)), placed


def edge_quality(comp, alpha, anchor):
    """Fraction of the character's silhouette that sits on a different luminance band than the plate
    just outside it. A bad comp leaves a bright rim; a good one is < 0.05."""
    a = np.asarray(alpha, np.float32) / 255.0
    if a.max() <= 0:
        return 1.0
    ys, xs = np.nonzero(a > 0.6)
    if len(xs) < 50:
        return 1.0
    edge = np.zeros_like(a, bool)
    edge[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    inner = (a > 0.9)
    outer = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(9)), np.float32) / 255.0 > 0.1
    ring = outer & ~inner & edge
    if ring.sum() < 20:
        return 0.0
    c = np.asarray(comp.convert("L"), np.float32)
    ci = c[inner].mean() if inner.sum() else 0.0
    cr = c[ring].mean()
    return float(abs(ci - cr) / 255.0)


def key_light(plate, top=0.03):
    """The plate's own key: mean colour of its brightest 3% of pixels, plus where they are.

    Matching a character to the LOCAL plate makes it dark and correct-looking and dead. The reference
    does the opposite — the character keeps its colour and takes the environment's light. So read the
    light out of the plate and use it as a tint on the character before compositing.
    """
    a = np.asarray(plate.convert("RGB"), np.float32)
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    thr = np.percentile(L, 100.0 * (1.0 - top))
    m = L >= thr
    tint = a[m].mean(0) if m.sum() else np.array([255, 235, 200], np.float32)
    ys, xs = np.nonzero(m)
    cx = float(xs.mean() / a.shape[1]) if len(xs) else 0.5
    cy = float(ys.mean() / a.shape[0]) if len(ys) else 0.2
    return tuple(int(min(255, v)) for v in tint), (cx, cy)


def separate(char_rgb, lift=1.45, tint=None):
    """Raise the subject above the value it was matched to.

    Matching a character to the plate *around its feet* makes it the same value as its surroundings —
    which is photographic and invisible. A subject sits a third of a stop to a full stop above its
    local background; this is that lift, in L only so the hue survives.
    """
    lab = G.rgb2lab(np.asarray(char_rgb.convert("RGB"), np.float32))
    lab[..., 0] = np.clip(lab[..., 0] * lift, 0, 100)
    out = Image.fromarray(G.lab2rgb(lab))
    if tint is not None:
        out = relight(out, tint, 0.22)
    return out


def relight(char_rgb, tint, amount=0.45):
    """Tint toward a light colour without touching value structure."""
    """Warm the character toward the plate's key colour without changing its value structure."""
    a = np.asarray(char_rgb.convert("RGB"), np.float32)
    t = np.array(tint, np.float32)
    tn = t / (t.max() + 1e-6) * 255.0
    out = a * (1.0 - amount) + (a * (tn / 200.0)) * amount
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
