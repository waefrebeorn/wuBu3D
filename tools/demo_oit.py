"""demo_oit — three crossing panes, drawn forward and reversed, which must agree exactly.

Also compares against sorted alpha blending on the same panes: sorted blending is correct only when
the panes do not cross, and crossing panes are the entire reason this exists.
"""

import numpy as np
from PIL import Image

import blocky as B
import oit as O


def panes():
    """Three panes at different depths, two of them crossing in screen space."""
    return [
        (O.pane((0.00, 0.00, -0.10), (0.0, 0.0, 1.0), (0, 1, 0), 0.62, 0.44), (0.95, 0.25, 0.20, 0.55)),
        (O.pane((0.18, 0.05, -0.55), (0.5, 0.1, 1.0), (0, 1, 0), 0.55, 0.50), (0.20, 0.75, 0.95, 0.55)),
        (O.pane((-0.20, -0.10, -1.05), (-0.4, 0.0, 1.0), (0, 1, 0), 0.60, 0.40), (0.95, 0.85, 0.30, 0.50)),
    ]


def main():
    w, h = 360, 260
    cam = B.Cam((0.0, 0.0, 1.6), (0.0, 0.0, 0.0), fov=48, w=w, h=h)
    P = panes()

    a = O.OIT(w, h)
    for q, c in P:
        a.add(q, c)
    fwd = a.render(cam, scale=2.0)

    b = O.OIT(w, h)
    for q, c in reversed(P):
        b.add(q, c)
    rev = b.render(cam, scale=2.0)

    d = np.abs(fwd.astype(np.int16) - rev.astype(np.int16))
    print("order independence: max channel diff %d, mean %.4f (%d px differ)"
          % (d.max(), d.mean(), int((d.max(2) > 0).sum())))

    # same panes through the sorted alpha path in the renderer
    import render_shaded as RS
    faces = []
    for q, c in P:
        faces.append((q, (c[0] * 255, c[1] * 255, c[2] * 255), {"alpha": c[3]}))
    sorted_im = RS.aa(faces, cam.eye, (0.0, 0.0, 0.0), w, h, ss=1, fov=48, flat=[],
                      bg=(16, 15, 18), lights=[(0.6, 1.2, 1.6, 2.0)], ambient=0.55, gain=0.4)
    S = np.asarray(sorted_im.convert("RGB"), np.int16)
    ds = np.abs(S - fwd.astype(np.int16))
    print("vs sorted alpha: mean %.1f levels, %.1f%% of pixels differ by >8"
          % (ds.mean(), 100 * float((ds.max(2) > 8).mean())))

    sheet = Image.new("RGB", (w * 3, h), (16, 15, 18))
    sheet.paste(Image.fromarray(fwd), (0, 0))
    sheet.paste(Image.fromarray(rev), (w, 0))
    sheet.paste(sorted_im.convert("RGB"), (w * 2, 0))
    sheet.save("/opt/data/cache/scratch/oit_sheet.png")
    print("wrote oit_sheet.png (oit forward | oit reversed | sorted alpha)")


if __name__ == "__main__":
    main()
