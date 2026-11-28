"""demo_bokeh — aperture defocus against the gaussian the renderer already had.

The scene puts small bright emitters at two depths behind and in front of the focus plane. Gaussian
DOF turns each into a soft blob with no shape; an aperture kernel turns each into the shape of the
iris. The number is the fill ratio of the brightest region (0.99 disc, 0.83 hexagon).
"""

import numpy as np
from PIL import Image

import bokeh
import cast_blocky as CB
import render_shaded as RS


def scene():
    f = []
    f += [(q, c, o) for q, c, o in CB.box(0, -0.4, -1.2, 5.0, 0.1, 4.0, (40, 38, 44))]
    for k in range(5):
        x = -1.0 + 0.5 * k
        z = -0.6 - 0.35 * k
        f += [(q, c, o) for q, c, o in CB.box(x, 0.14, z, 0.11, 0.11, 0.11, (255, 248, 226))]
    return f


def fill_of(im, zb, focus, cam):
    """Per-emitter fill ratio, medians over the five emitters.

    A single mask over the whole frame mixes five blobs and scores near zero for both methods; the
    shape question is per highlight, so each emitter gets its own window.
    """
    a = np.asarray(im.convert("L"), np.float32)
    h, w = a.shape
    vals = []
    for k in range(5):
        x = -1.0 + 0.5 * k
        z = -0.6 - 0.35 * k
        pr, zz = cam.project(np.array([[x, 0.14, z]], np.float32))
        cx, cy = int(pr[0][0]), int(pr[0][1])
        r = 14
        if not (r <= cx < w - r and r <= cy < h - r):
            continue
        win = a[cy - r:cy + r + 1, cx - r:cx + r + 1]
        m = win > (win.max() * 0.35)
        if m.sum() < 6:
            continue
        vals.append(bokeh.fill_ratio(m))
    return (float(np.median(vals)) if vals else 0.0), len(vals)


def main():
    f = scene()
    # the emitters are the subject: with a dim key the whole frame sits in the dark and the bokeh
    # shape cannot be seen at all, which is what the first render proved
    im = RS.aa(f, (0.0, 0.55, 1.9), (0.0, 0.0, -0.9), 360, 260, ss=2, fov=52, flat=[],
               bg=(16, 15, 18), lights=[(0.4, 1.5, 1.2, 14.0)], ambient=0.34, gain=0.55, rim=0.0,
               spec=1.2, gloss=80.0)
    zb = np.array(RS._LAST_ZB, np.float32)

    gauss = RS.dof(im, focus=1.9, aperture=1.4, far=9.0).convert("RGB")
    hexa = bokeh.defocus(im, zb, focus=1.9, aperture=1.6, blades=6, max_radius=9).convert("RGB")

    cam = RS.B.Cam((0.0, 0.55, 1.9), (0.0, 0.0, -0.9), fov=52, w=360, h=260)
    fg, ng = fill_of(gauss, zb, 1.9, cam)
    fh, nh = fill_of(hexa, zb, 1.9, cam)
    Ag = np.asarray(gauss, np.float32)
    Ah = np.asarray(hexa, np.float32)
    print("gaussian DOF: median per-emitter fill %.3f over %d emitters" % (fg, ng))
    print("aperture DOF: median per-emitter fill %.3f over %d emitters (hexagon theory 0.83)"
          % (fh, nh))
    print("images differ by %.1f levels mean — same defocus, different shape" % float(np.abs(Ag - Ah).mean()))

    sheet = Image.new("RGB", (360 * 3, 260), (16, 15, 18))
    sheet.paste(im.convert("RGB"), (0, 0))
    sheet.paste(gauss, (360, 0))
    sheet.paste(hexa, (720, 0))
    sheet.save("/opt/data/cache/scratch/bokeh_sheet.png")
    print("wrote bokeh_sheet.png (sharp | gaussian | aperture)")


if __name__ == "__main__":
    main()
