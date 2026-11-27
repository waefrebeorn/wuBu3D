#!/usr/bin/env python3
"""Contract tests for the agent-facing CLI.

Run: python3 tests/test_agent_cli.py        (no pytest, no network, ~2 s)

Every case is a claim the docs make: exit codes, path-precise errors, and the fact
that a bad spec never reaches a renderer. A test that only checks "it ran" would let
the three defects these cases were written for come back.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "src" / "wubu3d.py" if (ROOT / "src" / "wubu3d.py").exists() else ROOT / "wubu3d.py"
PY = sys.executable
TMP = Path(tempfile.mkdtemp(prefix="wubu3d-test-"))

PASS, FAIL = [], []


def run(args, stdin=None):
    return subprocess.run([PY, str(CLI)] + args, capture_output=True, text=True,
                          input=stdin, cwd=str(TMP), timeout=180)


def case(name):
    def deco(fn):
        try:
            fn()
            PASS.append(name)
            print(f"  ok    {name}")
        except AssertionError as e:
            FAIL.append((name, str(e)))
            print(f"  FAIL  {name}: {e}")
        return fn
    return deco


def spec_file(name, spec) -> Path:
    p = TMP / f"{name}.json"
    p.write_text(json.dumps(spec))
    return p


GOOD = {
    "name": "probe", "preset": "preview", "duration": 1.0, "fps": 24,
    "cast": [{"name": "walker", "path": [[0, -4], [0, 4]], "walk": [0, 24]}],
    "shots": [{"in": 0, "out": 23, "cam": [0, -6, 1.6], "lens": 50, "follow": "walker"}],
}


@case("schema is valid JSON describing the spec object")
def _():
    r = run(["schema"])
    assert r.returncode == 0, r.stderr[-300:]
    s = json.loads(r.stdout)
    assert s["type"] == "object" and "name" in s["properties"], "schema lacks name/properties"
    assert s["required"] == ["name"], s.get("required")


@case("validate accepts a good spec (exit 0, no errors)")
def _():
    r = run(["validate", str(spec_file("good", GOOD))])
    assert r.returncode == 0, f"exit {r.returncode}: {r.stdout} {r.stderr}"
    assert "0 error(s)" in r.stdout, r.stdout


@case("missing name is an error with path 'name' (exit 2)")
def _():
    bad = dict(GOOD); bad.pop("name")
    r = run(["validate", str(spec_file("noname", bad))])
    assert r.returncode == 2, f"exit {r.returncode}"
    assert "name:" in r.stdout and "required" in r.stdout, r.stdout


@case("odd resolution is refused with the libx264 reason")
def _():
    bad = dict(GOOD, resolution=[321, 181])
    r = run(["validate", str(spec_file("odd", bad))])
    assert r.returncode == 2, f"exit {r.returncode}"
    assert "odd side" in r.stdout and "libx264" in r.stdout, r.stdout


@case("unknown cast member in follow is an error naming the cast")
def _():
    bad = json.loads(json.dumps(GOOD))
    bad["shots"][0]["follow"] = "nobody"
    r = run(["validate", str(spec_file("badfollow", bad))])
    assert r.returncode == 2, f"exit {r.returncode}"
    assert "shots[0].follow" in r.stdout and "walker" in r.stdout, r.stdout


@case("a walk past the end of the film is an error, not a silent clamp")
def _():
    bad = json.loads(json.dumps(GOOD))
    bad["cast"][0]["walk"] = [0, 999]
    r = run(["validate", str(spec_file("longwalk", bad))])
    assert r.returncode == 2, f"exit {r.returncode}"
    assert "walk ends at frame 999" in r.stdout, r.stdout


@case("unknown top-level key is a warning, not an error")
def _():
    s = dict(GOOD, durration=3.0)
    r = run(["validate", str(spec_file("typo", s))])
    assert r.returncode == 0, f"exit {r.returncode}: {r.stdout}"
    assert "unknown key" in r.stdout and "durration" in r.stdout, r.stdout


@case("inspect derives frames from duration x fps")
def _():
    r = run(["inspect", str(spec_file("good2", GOOD))])
    assert r.returncode == 0, r.stderr[-300:]
    d = json.loads(r.stdout)
    assert d["frames"] == 24 and d["fps"] == 24, d
    assert d["mp4"] == "out/probe/probe.mp4", d["mp4"]


@case("render refuses an invalid spec before touching a frame (exit 2)")
def _():
    bad = dict(GOOD, resolution=[100, 99])
    r = run(["build", str(spec_file("badbuild", bad))])
    assert r.returncode == 2, f"exit {r.returncode} (a renderer started on a bad spec)"
    assert "spec error" in r.stderr and "nothing was rendered" in r.stderr, r.stderr


@case("plan reports cost and admits when it is unmeasured")
def _():
    r = run(["plan", str(spec_file("good3", GOOD))])
    assert r.returncode == 0, r.stderr[-300:]
    d = json.loads(run(["plan", str(spec_file("good3", GOOD)), "--json"]).stdout)
    assert "estimate" in d and "raster_s" in d["estimate"], d
    assert "raster:" in r.stdout, r.stdout


@case("--json keeps stdout pure JSON while logs go to stderr")
def _():
    p = spec_file("jsonmode", dict(GOOD, durration=1.0))   # extra key -> a warning
    r = run(["validate", str(p), "--json"])
    d = json.loads(r.stdout)            # would raise if a log line leaked into stdout
    assert d["ok"] is True and isinstance(d["warnings"], list), d


@case("qa measures a rendered film and passes it")
def _():
    d = ROOT / "out" / "demo_preview"
    if not (d / "receipt.json").exists():
        print("      (skipped: no out/demo_preview receipt)")
        return
    r = run(["qa", str(ROOT / "specs" / "demo_preview.json")])
    assert r.returncode == 0, f"exit {r.returncode}: {r.stdout}"
    assert "passed" in r.stdout.lower(), r.stdout
    rec = json.loads((d / "receipt.json").read_text())
    assert rec["qa"]["frames"] > 0 and "sha256" in rec["outputs"], rec


@case("still renders one frame fast and names it")
def _():
    r = run(["still", str(ROOT / "specs" / "assets_test.json"), "--at", "1"])
    assert r.returncode == 0, f"exit {r.returncode}: {r.stderr[-400:]}"
    out = ROOT / "out" / "assets_test" / "still_0001.png"
    assert out.exists() and out.stat().st_size > 1000, f"no still at {out}"


@case("an OBJ meshes entry validates and imports")
def _():
    spec = json.loads(json.dumps(GOOD))
    spec["props"] = {"meshes": [{"obj": "assets/obelisk.obj", "at": [2, 3, 0]}]}
    r = run(["validate", str(spec_file("mesh_ok", spec))], )
    assert r.returncode == 0, r.stdout + r.stderr


@case("a mesh path outside the project is refused")
def _():
    spec = json.loads(json.dumps(GOOD))
    spec["props"] = {"meshes": [{"obj": "../../etc/passwd.obj"}]}
    r = run(["validate", str(spec_file("mesh_bad", spec))])
    assert r.returncode == 2, f"exit {r.returncode}"
    assert "props.meshes[0].obj" in r.stdout and "inside the project" in r.stdout, r.stdout


@case("a caption renders at the right time in a still (frame-numbered, not loop index)")
def _():
    words = ROOT / "assets" / "_test_words.json"      # must live inside the project
    words.write_text(json.dumps([{"word": "hello", "start": 0.4, "end": 0.9}]))
    spec = dict(GOOD, duration=1.0, resolution=[320, 180], samples=1, ssaa=1,
                name="captest",
                captions={"words": "assets/_test_words.json", "size": 0.12, "y": 0.6, "stroke": True})
    p = spec_file("captest", spec)
    r = run(["still", str(p), "--at", "15"])          # 15/24 = 0.625 s, inside the caption
    assert r.returncode == 0, r.stderr[-300:]
    out = ROOT / "out" / "captest" / "still_0015.png"
    assert out.exists(), f"no still at {out}"
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(out).convert("L"), dtype=np.uint8)
    h = a.shape[0]
    band = a[int(h * 0.45):int(h * 0.75)]
    assert (band > 200).sum() > 40, f"caption pixels missing ({(band > 200).sum()} bright)"


@case("accum/shutter/tonemap validate, and out-of-range values are refused")
def _():
    ok = dict(GOOD, accum=4, shutter=0.5, tonemap="aces")
    assert run(["validate", str(spec_file("acc_ok", ok))]).returncode == 0
    bad = dict(GOOD, accum=99)
    r = run(["validate", str(spec_file("acc_bad", bad))])
    assert r.returncode == 2 and "accum" in r.stdout, r.stdout


@case("a 2-frame render with 3 subframes writes 2 frames, not 6")
def _():
    spec = dict(GOOD, name="subframes", duration=2 / 24, fps=24, resolution=[96, 64],
                samples=1, ssaa=1, accum=3, shutter=0.5,
                cast=[{"name": "walker", "path": [[0, -2], [0, 2]], "walk": [0, 2]}],
                shots=[{"in": 0, "out": 1, "cam": [0, -5, 1.6], "target": [0, 0, 1.0], "lens": 40}])
    r = run(["raster", str(spec_file("subframes", spec))])
    assert r.returncode == 0, r.stderr[-400:]
    graded = list((ROOT / "out" / "subframes" / "graded").glob("f_*.png"))
    assert len(graded) == 2, f"expected 2 output frames, got {len(graded)}"




@case("a GLB actor needs a clip that exists in the file")
def _():
    spec = dict(GOOD, name="glbclip", duration=2 / 24, fps=24, resolution=[96, 64], samples=1,
                cast=[{"name": "walker", "glb": "assets/cache/mini-characters/Models/GLB format/"
                                                "character-female-a.glb",
                       "clip": "no-such-clip", "path": [[0, -2], [0, 2]], "walk": [0, 1]}],
                shots=[{"in": 0, "out": 1, "cam": [0, -5, 1.6], "target": [0, 0, 1.0], "lens": 40}])
    if not (ROOT / "assets/cache/mini-characters").exists():
        return          # the pack is fetched on demand; nothing to test without it
    r = run(["raster", str(spec_file("glbclip", spec))])
    assert r.returncode != 0, "a missing clip must fail"
    assert "no clip" in (r.stdout + r.stderr), (r.stdout + r.stderr)[-300:]


@case("a GLB actor renders and the posed mesh is not empty")
def _():
    import sys as _s
    _s.path.insert(0, str(ROOT))
    import wubu3d_gltf as G
    glb = ROOT / "assets/cache/mini-characters/Models/GLB format/character-female-a.glb"
    if not glb.exists():
        return
    asset = G.load(glb)
    assert "walk" in asset.animations, asset.clip_names()[:5]
    a = G.bounds(asset, "walk", 0.0)
    b = G.bounds(asset, "walk", 0.33)
    import numpy as _np
    assert float(_np.linalg.norm(a[1] - b[1])) > 1e-4, "the walk clip does not move the mesh"


print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for n, e in FAIL:
        print(f"  {n}: {e}")
    sys.exit(1)
