"""bokeh — aperture-shaped defocus, the difference between "out of focus" and "shot on a lens".

A gaussian blur has no shape: every highlight becomes a soft blob. A real lens turns a highlight into
an aperture — hexagonal at 6 blades, round wide open, cat's-eye at the edge of the frame. The test is
the shape of a point highlight, and it is measurable: circularity of the bright region.
"""

import numpy as np
from PIL import Image


def aperture_kernel(radius=9, blades=6, rotation=0.0, cats_eye=0.0, ss=3):
    """A disc masked by a polygon: blades=0 gives a circle, cats_eye squashes the near edge."""
    # supersample the mask: a hard polygon edge gives a staircase bokeh, which reads as a bad lens.
    # sample at pixel centres of an (n*ss)^2 grid so the downsample reshape is exact.
    r = int(radius)
    n = 2 * r + 1
    c = (np.arange(n * ss, dtype=np.float32) - (n * ss - 1) / 2.0) / ss
    xx, yy = np.meshgrid(c, c)
    d = np.hypot(xx, yy)
    ang = np.arctan2(yy, xx)
    k = (d <= radius).astype(np.float32)
    if blades >= 3:
        # a polygon inscribed in the disc: r(theta) = R * cos(pi/n) / cos((theta mod 2pi/n) - pi/n)
        seg = 2.0 * np.pi / blades
        a = np.mod(ang - np.radians(rotation), seg) - seg / 2.0
        poly = radius * np.cos(np.pi / blades) / np.cos(a)
        k *= (d <= poly).astype(np.float32)
    if cats_eye > 0.0:
        k *= np.clip(1.0 - cats_eye * (xx + radius) / (2.0 * radius), 0.0, 1.0)
    if ss > 1:
        k = k.reshape(n, ss, n, ss).mean(axis=(1, 3))
    k /= max(k.sum(), 1.0)
    return k


def defocus(im, zb, focus=2.0, aperture=1.0, blades=6, max_radius=10):
    """Per-pixel circle of confusion from depth, applied as an aperture-shaped splat."""
    a = np.asarray(im.convert("RGB"), np.float32)
    z = np.asarray(zb, np.float32)
    z = np.where(np.isfinite(z), z, focus)
    coc = np.clip(np.abs(z - focus) / max(1e-3, focus) * aperture, 0.0, 1.0)
    out = a.copy()
    for radius in range(1, max_radius + 1):
        k = aperture_kernel(radius, blades)
        pad = radius
        ap = np.pad(a, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
        acc = np.zeros_like(a)
        r = int(radius)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                w = k[dy + r, dx + r]
                if w <= 0:
                    continue
                acc += ap[pad + dy:pad + dy + a.shape[0], pad + dx:pad + dx + a.shape[1]] * w
        band = (coc > (radius - 1) / max_radius) & (coc <= radius / max_radius)
        out[band] = acc[band]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def fill_ratio(mask):
    """Area over the area of the circumscribed circle: 1.0 for a disc, 0.83 for a hexagon, 0.64 for a
    square. Perimeter-based circularity on a 19-pixel blob is dominated by staircase noise and ranked
    a circle below a hexagon, which is the metric telling you it is the wrong metric."""
    ys, xs = np.nonzero(mask)
    if len(xs) < 8:
        return 0.0
    cy, cx = ys.mean(), xs.mean()
    rmax = float(np.hypot(ys - cy, xs - cx).max())
    return float(len(xs)) / max(1e-9, np.pi * rmax * rmax)


def highlight_shape(radius=9, blades=6, size=41):
    """Render a single point light through the kernel and measure the shape that comes out."""
    img = np.zeros((size, size), np.float32)
    c = size // 2
    img[c, c] = 255.0
    k = aperture_kernel(radius, blades)
    r = int(radius)
    out = np.zeros_like(img)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            yy, xx = c + dy, c + dx
            if 0 <= yy < size and 0 <= xx < size:
                out[yy, xx] = img[c, c] * k[dy + r, dx + r] * (k.size)
    return out, fill_ratio(out > (out.max() * 0.4))
