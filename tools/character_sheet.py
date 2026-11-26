"""Character sheet: one figure, flat light, no fog, so the model can be judged.

Renders the raw colour pass from the C11 rasteriser — no grade, no bloom, no film
treatment. If the silhouette does not read here, it will not read on screen either.
"""
import json, pathlib, subprocess, sys
sys.path.insert(0, "/opt/data/work/wubu3d")
import wubu3d as W

spec = {
    "name": "sheet", "preset": "cartoon", "duration": 1 / 24, "fps": 24,
    "resolution": [600, 800], "ssaa": 1, "samples": 1, "seed": 7,
    "fog": 100000.0,
    "ground": [0.42, 0.42, 0.44],
    "sky": {"horizon": [0.55, 0.57, 0.60], "zenith": [0.62, 0.65, 0.70]},
    "props": {"towers": 0, "tower_radius": [60, 80], "rocks": 0, "glass": [], "fg": []},
    "cast": [{
        "name": "figure", "color": [0.16, 0.15, 0.16], "skin": [0.72, 0.58, 0.48],
        "path": [[0, 0], [0, 0.001]], "walk": [0, 1], "stride": 1.0,
        "hood": True, "coat": True,
        "lantern": {"intensity": 0.0},
        "perf": [{"f": 0, "walk": 0.0}],
    }],
    "shots": [{"in": 0, "out": 1, "cam": [2.4, 3.6, 1.35], "target": [0, 0, 1.02], "lens": 50}],
}
spec = W.load_spec_from_dict(spec) if hasattr(W, "load_spec_from_dict") else spec
spec.setdefault("frames", 1)
pathlib.Path("/opt/data/work/wubu3d/specs/sheet.json").write_text(json.dumps(spec, indent=1))

data = W.build_raster_scene(spec, 1)
out = pathlib.Path("/opt/data/work/wubu3d/out/sheet")
out.mkdir(parents=True, exist_ok=True)
r = subprocess.run([str(W.RASTER_BIN), str(out) + "/"], input=data, capture_output=True)
print(r.stderr.decode().strip()[-200:])
print("wrote", out / "col_0000.ppm")
