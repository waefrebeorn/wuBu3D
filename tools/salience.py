#!/usr/bin/env python3
"""Measure whether the frame's subject actually wins the eye.

The composition rules say the eye goes to, in order: size > contrast > colour > position,
and one element must be primary. That is checkable. This prints a number for each term so
a shot can be judged by evidence instead of by how it felt at 2 a.m.

usage: salience.py frame.png [--depth dep.bin] [--json]

Subject mask: nearest 12% of pixels by depth (the layer the camera is pointed at). With no
depth pass, falls back to the central third of the frame.
"""
import json, sys
import numpy as np
from PIL import Image


def load_depth(path):
    """returns (depth, subject_bbox) — the rasteriser tags character pixels and
    reports their screen box in the header, so the mask is measured, not guessed"""
    raw = open(path, "rb").read()
    w, h = np.frombuffer(raw[:8], dtype="<u4")
    hdr = 8
    bbox = None
    if len(raw) >= 8 + 16 + w * h * 4:
        b = np.frombuffer(raw[8:24], dtype="<i4")
        if len(b) == 4 and b[0] >= 0 and b[2] > b[0]:
            bbox = (int(b[0]), int(b[1]), int(b[2]), int(b[3]))   # half-res pixels
        hdr = 24
    return np.frombuffer(raw[hdr:hdr + w * h * 4], dtype="<f4").reshape(h, w), bbox


def luma(rgb):
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])


def laplacian(a):
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    from numpy.lib.stride_tricks import sliding_window_view
    if a.shape[0] < 3 or a.shape[1] < 3:
        return np.zeros_like(a)
    win = sliding_window_view(a, (3, 3))
    return np.einsum("ijkl,kl->ij", win, k)


def report(path, depth_path=None, at=None, radius=0.16):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    h, w = rgb.shape[:2]
    L = luma(rgb)

    bbox = None
    if depth_path:
        _, bbox = load_depth(depth_path)

    if at is None and bbox is not None:
        # the header's w2 tells us whether the box is in pass resolution or full
        w2 = int(np.frombuffer(open(depth_path, "rb").read(4), dtype="<u4")[0])
        scale = 1 if w2 == w else 2
        x0, y0, x1, y1 = [v * scale for v in bbox]
        subj = np.zeros((h, w), bool)
        subj[max(0, y0):min(h, y1 + 2), max(0, x0):min(w, x1 + 2)] = True
    elif at is not None:
        # subject is where we put it, not merely "the nearest thing" — a foreground prop
        # is nearer than the character and would otherwise capture the mask
        cx0, cy0 = at
        yy, xx = np.mgrid[0:h, 0:w]
        subj = ((xx / w - cx0) ** 2 + (yy / h - cy0) ** 2) ** 0.5 < radius
        if depth_path:
            d = load_depth(depth_path)
            if d.shape != (h, w):
                d = np.asarray(Image.fromarray(d).resize((w, h), Image.NEAREST))
    elif depth_path:
        d = load_depth(depth_path)
        if d.shape != (h, w):
            d = np.asarray(Image.fromarray(d).resize((w, h), Image.NEAREST))
        valid = d < 1e29
        near = np.percentile(d[valid], 12)
        subj = valid & (d <= near)
    else:
        subj = np.zeros((h, w), bool)
        subj[h // 3:2 * h // 3, w // 3:2 * w // 3] = True

    if subj.sum() < 200:
        return {"error": "subject mask too small", "subject_px": int(subj.sum())}

    bg = ~subj
    ms, mb = float(L[subj].mean()), float(L[bg].mean())
    # contrast the eye sees: value separation, local detail, colour separation
    value_sep = abs(ms - mb)
    hp = np.abs(laplacian(L))
    hp = np.pad(hp, ((1, 1), (1, 1)), mode="edge")   # sliding window shaves one pixel
    detail_s = float(hp[subj].mean())
    detail_b = float(hp[bg].mean())
    detail_ratio = detail_s / max(detail_b, 1e-6)
    mu_s = rgb[subj].mean(axis=0)
    mu_b = rgb[bg].mean(axis=0)
    colour_sep = float(np.linalg.norm(mu_s - mu_b))

    # thirds compliance: where is the subject's centroid, as a distance from a power point
    ys, xs = np.nonzero(subj)
    cx, cy = xs.mean() / w, ys.mean() / h
    pts = [(1 / 3, 1 / 3), (2 / 3, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 2 / 3)]
    thirds_dist = min(((cx - px) ** 2 + (cy - py) ** 2) ** 0.5 for px, py in pts)
    centre_dist = ((cx - 0.5) ** 2 + (cy - 0.5) ** 2) ** 0.5
    on_third = thirds_dist < 0.12

    # One number, weighted the way the hierarchy ranks them. Each term is normalised
    # against a stated "strong" reference, not against 1.0: in a night frame a 0.25
    # luminance gap is a strong value separation, 2x the local detail is a strong
    # focus cue, and a 0.35 RGB distance is a strong colour separation.
    score = (min(value_sep / 0.25, 1.0) * 55 +
             min(detail_ratio / 2.0, 1.0) * 25 +
             min(colour_sep / 0.35, 1.0) * 20)
    return {
        "file": path,
        "size": [w, h],
        "subject_px_pct": round(100 * subj.sum() / (h * w), 1),
        "subject_mean_lum": round(ms, 3),
        "bg_mean_lum": round(mb, 3),
        "value_separation": round(value_sep, 3),
        "detail_ratio": round(detail_ratio, 2),
        "colour_separation": round(colour_sep, 3),
        "subject_centroid": [round(cx, 3), round(cy, 3)],
        "on_thirds": bool(on_third),
        "centre_offset": round(centre_dist, 3),
        "salience": round(score, 1),
        "verdict": (
            "subject wins, framed on a third" if score >= 45 and value_sep >= 0.08 and on_third
            else "subject wins, centred (fine only if symmetry is deliberate)"
            if score >= 45 and value_sep >= 0.08
            else "subject is not the focal point"),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    path = args[0]
    depth = None
    if "--depth" in args:
        depth = args[args.index("--depth") + 1]
    at = None
    if "--at" in args:
        at = tuple(float(v) for v in args[args.index("--at") + 1].split(","))
    rad = 0.16
    if "--radius" in args:
        rad = float(args[args.index("--radius") + 1])
    r = report(path, depth, at, rad)
    print(json.dumps(r, indent=1) if "--json" in args else
          "\n".join(f"{k:22s} {v}" for k, v in r.items()))
