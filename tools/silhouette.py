#!/usr/bin/env python3
"""Measure a character's silhouette the way a modeller checks proportions.

Takes a flat silhhouette render (white on black) and reports the numbers the 10-step
pipeline gates on: heads tall, shoulder width in head-widths, hip width, knee height,
leg gap. Heuristic, but fixed and published — so a change either moves the number or it
does not.

usage: silhouette.py mask.png [--height 1.76]
"""
import json, sys
import numpy as np
from PIL import Image


def measure(path, real_height=1.76):
    im = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
    mask = im > 40
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0:
        return {"error": "empty mask"}
    top, bot = rows[0], rows[-1]
    h_px = bot - top + 1
    width = mask.sum(axis=1).astype(float)

    def at(frac):
        """row width at a fraction of height from the top"""
        r = int(top + frac * (h_px - 1))
        return float(width[r])

    # head: widest row in the top 22%; neck: narrowest in 22-34%
    head_zone = width[top:top + int(0.22 * h_px)]
    head_w = float(head_zone.max())
    neck_zone = width[top + int(0.20 * h_px):top + int(0.34 * h_px)]
    neck_w = float(neck_zone.min()) if len(neck_zone) else 0.0
    shoulders = float(width[top + int(0.22 * h_px):top + int(0.36 * h_px)].max())
    hips = at(0.52)
    knee = at(0.72)
    ankle = at(0.95)

    head_h_px = head_w * 1.15                     # head reads slightly taller than wide
    heads_tall = h_px / max(head_h_px, 1.0)

    # leg gap: horizontal runs of mask at 82% height (below the coat)
    r = int(top + 0.82 * h_px)
    row = mask[r]
    runs, inrun = [], False
    for v in row:
        if v and not inrun:
            start = True
            inrun = True
            n = 1
        elif v and inrun:
            n += 1
        elif not v and inrun:
            runs.append(n)
            inrun = False
    if inrun:
        runs.append(n)
    legs_separate = len(runs) >= 2

    return {
        "file": path,
        "height_px": int(h_px),
        "width_px": int(cols[-1] - cols[0] + 1),
        "aspect": round((cols[-1] - cols[0] + 1) / h_px, 3),
        "heads_tall": round(heads_tall, 2),
        "head_width_px": int(head_w),
        "neck_width_px": int(neck_w),
        "shoulder_width_px": int(shoulders),
        "shoulders_in_head_widths": round(shoulders / max(head_w, 1), 2),
        "hips_in_head_widths": round(hips / max(head_w, 1), 2),
        "knee_width_px": int(knee),
        "leg_gap_at_82pct": legs_separate,
        "real_height_m": real_height,
        "targets": {"heads_tall": "7.0-7.5", "shoulders_in_head_widths": "2.0-2.4",
                    "hips_in_head_widths": "1.4-1.8", "leg_gap_at_82pct": True},
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    print(json.dumps(measure(args[0]), indent=1))
