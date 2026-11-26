#!/usr/bin/env python3
"""WuBu3D spec contract — resolve, validate, describe, estimate.

This module is the machine-facing half of the pipeline: an agent writes a spec,
asks this module whether it is legal, and gets path-precise errors back instead
of a traceback three stages into a render. Stdlib only, no Blender.

Used by `wubu3d.py` (`validate`, `inspect`, `plan`, `schema`, and every render,
which refuses an invalid spec before it touches a frame).
"""
from __future__ import annotations

import copy
import math

PRESETS = {
    "preview":   {"resolution": [320, 180], "samples": 4, "denoise": False, "grade": True},
    "cartoon":   {"resolution": [640, 360], "samples": 6, "denoise": True,  "grade": True},
    "cinematic": {"resolution": [854, 480], "samples": 8, "denoise": True,  "grade": True},
    "vertical":  {"resolution": [720, 1280], "samples": 8, "denoise": True,  "grade": True},
}

KNOWN_TOP = [
    "name", "preset", "duration", "fps", "resolution", "samples", "denoise", "seed",
    "fog", "ssaa", "raster_gain", "range", "ground", "sky", "lights", "props", "cast",
    "shots", "titles", "fade", "dof", "sound", "exposure", "frames",
    "ao", "ao_radius", "ao_rays", "ambient", "captions", "accum", "shutter", "tonemap", "upscale",
]


def issue(level: str, path: str, message: str) -> dict:
    return {"level": level, "path": path, "message": message}


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _v3(v) -> bool:
    return isinstance(v, (list, tuple)) and len(v) == 3 and all(_is_num(x) for x in v)


def _v2(v) -> bool:
    return isinstance(v, (list, tuple)) and len(v) == 2 and all(_is_num(x) for x in v)


def _rgb_ok(v) -> bool:
    return _v3(v) and all(0.0 <= x <= 1.0 for x in v)


# ───────────────────────────────────────────────────────────────── resolution
def deep_merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def default_shots(spec):
    n = spec["frames"]
    return [
        {"in": 0, "out": n // 2, "cam": [-14, -22, 3.0], "target": [0, 6, 2.5], "lens": 35},
        {"in": n // 2, "out": n, "cam": [-8, -10, 2.2], "target": [0, 8, 3.0], "lens": 45},
    ]


def resolve(raw: dict, defaults: dict, presets: dict | None = None) -> dict:
    """Fill defaults and derive the numbers the renderers read (frames, shots)."""
    presets = presets or PRESETS
    spec = deep_merge(defaults, raw)
    preset = presets.get(spec.get("preset"), presets["cartoon"])
    for k in ("resolution", "samples", "denoise"):
        if spec.get(k) is None:
            spec[k] = preset[k]
    try:
        spec["frames"] = int(round(float(spec["duration"]) * float(spec["fps"])))
    except (TypeError, ValueError):
        spec["frames"] = 0
    if not spec.get("shots"):
        spec["shots"] = default_shots(spec) if spec["frames"] > 1 else []
    return spec


# ───────────────────────────────────────────────────────────────── validation
def validate(raw: dict) -> tuple[list, list]:
    """Return (errors, warnings). Every item is {level, path, message}."""
    errors, warnings = [], []

    def err(p, m):
        errors.append(issue("error", p, m))

    def warn(p, m):
        warnings.append(issue("warning", p, m))

    if not isinstance(raw, dict):
        err("$", f"spec must be a JSON object, got {type(raw).__name__}")
        return errors, warnings

    for k in sorted(set(raw) - set(KNOWN_TOP)):
        warn(k, f"unknown key {k!r} — no effect; known keys: {', '.join(KNOWN_TOP)}")

    # name — it is an output directory, so it must be one
    name = raw.get("name")
    if name is None:
        err("name", "required: the output directory under out/")
    elif not isinstance(name, str) or not name.strip():
        err("name", "must be a non-empty string")
    elif any(c in name for c in "/\\") or ".." in name or name != name.strip():
        err("name", "must be a plain directory name: no slashes, no '..', no surrounding spaces")

    if "frames" in raw:
        warn("frames", "frames is derived from duration x fps — setting it does nothing "
                       "(change duration or fps)")

    preset = raw.get("preset", "cartoon")
    if not isinstance(preset, str):
        err("preset", "must be a string")
    elif preset not in PRESETS:
        warn("preset", f"unknown preset {preset!r}; the renderers fall back to 'cartoon' "
                       f"(known: {', '.join(PRESETS)})")

    fps = raw.get("fps", 24)
    if not _is_int(fps) or not (1 <= fps <= 120):
        err("fps", "must be an integer 1..120")

    duration = raw.get("duration", 6.0)
    frames = 0
    if not _is_num(duration) or not (0 < duration <= 900):
        err("duration", "must be a number of seconds in (0, 900]")
    elif _is_int(fps) and 1 <= fps <= 120:
        frames = int(round(float(duration) * fps))
        if frames < 1:
            err("duration", f"{duration}s at {fps} fps rounds to 0 frames")
        elif frames == 1:
            warn("duration", "one frame — that is a still, not a film (raise duration or fps)")
        elif frames > 20000:
            warn("duration", f"{frames} frames — roughly "
                             f"{frames * 0.008 / 60:.0f} min on the raster path, hours on Cycles")

    res = raw.get("resolution")
    if res is not None:
        if not (isinstance(res, (list, tuple)) and len(res) == 2 and all(_is_int(x) for x in res)):
            err("resolution", "must be [width, height] integers")
        else:
            w, h = res
            if not (16 <= w <= 4320 and 16 <= h <= 4320):
                err("resolution", "each side must be 16..4320")
            elif w % 2 or h % 2:
                err("resolution", f"{w}x{h} has an odd side — libx264 refuses it; use even sides")
            elif w > h and w / h > 3.5:
                warn("resolution", f"aspect {w / h:.2f}:1 is wider than the 2.39:1 bars the grade draws")

    if raw.get("ssaa") is not None and (not _is_int(raw["ssaa"]) or not (1 <= raw["ssaa"] <= 4)):
        err("ssaa", "must be an integer 1..4 (2 = 4x pixels)")
    if raw.get("samples") is not None and (not _is_int(raw["samples"]) or not (1 <= raw["samples"] <= 4096)):
        err("samples", "must be an integer 1..4096")
    if raw.get("raster_gain") is not None and not (0.1 <= _num(raw["raster_gain"]) <= 4.0):
        err("raster_gain", "must be 0.1..4.0")
    if raw.get("fog") is not None and not (_num(raw["fog"]) > 0):
        err("fog", "must be a positive distance in metres")
    if raw.get("seed") is not None and not _is_int(raw["seed"]):
        err("seed", "must be an integer")
    caps = raw.get("captions")
    if caps is not None:
        if isinstance(caps, dict):
            wpath = caps.get("words")
            if not isinstance(wpath, str):
                err("captions", "a captions object needs 'words': a path to a words json")
            elif wpath.startswith("/") or ".." in wpath or not wpath.endswith(".json"):
                err("captions.words", "must be a .json path inside the project")
            if "size" in caps and not (0 < _num(caps["size"]) <= 0.5):
                err("captions.size", "must be 0..0.5 of frame height")
            if "y" in caps and not (0 <= _num(caps["y"]) <= 1):
                err("captions.y", "must be 0..1 of frame height")
        elif isinstance(caps, list):
            for i, c in enumerate(caps):
                if not isinstance(c, dict) or not isinstance(c.get("text"), str):
                    err(f"captions[{i}]", "needs a string 'text'")
                    continue
                if not _is_num(c.get("in")) or not _is_num(c.get("out")):
                    err(f"captions[{i}]", "needs numeric 'in' and 'out' in seconds")
                elif c["out"] <= c["in"]:
                    err(f"captions[{i}].out", "must be greater than in")
        else:
            err("captions", "must be a list of {text, in, out} or {words: path}")
    if raw.get("tonemap") is not None and raw["tonemap"] not in ("srgb", "aces"):
        err("tonemap", "must be 'srgb' (tone curve on encoded values) or 'aces' (linear)")
    if raw.get("accum") is not None and (not _is_int(raw["accum"]) or not (1 <= raw["accum"] <= 16)):
        err("accum", "must be an integer 1..16 subframes per output frame")
    if raw.get("shutter") is not None and not (0.0 <= _num(raw["shutter"]) <= 1.0):
        err("shutter", "must be 0..1 of a frame time (0.5 is a 180-degree shutter)")
    if raw.get("ambient") is not None and not (0.0 <= _num(raw["ambient"]) <= 1.5):
        err("ambient", "must be 0..1.5 — the flat light floor every surface keeps in shadow")
    if raw.get("ao") is not None and raw["ao"] not in ("taps", "ssao"):
        err("ao", "must be 'taps' (default, cheap) or 'ssao' (raytraced, ~0.4 s/frame)")
    if raw.get("ao_radius") is not None and not (0.02 <= _num(raw["ao_radius"]) <= 8.0):
        err("ao_radius", "must be 0.02..8.0 metres")
    if raw.get("ao_rays") is not None and (not _is_int(raw["ao_rays"]) or not (1 <= raw["ao_rays"] <= 32)):
        err("ao_rays", "must be an integer 1..32")
    if raw.get("exposure") is not None and not (0.1 <= _num(raw["exposure"]) <= 5.0):
        err("exposure", "must be 0.1..5.0")

    sky = raw.get("sky")
    if sky is not None:
        if not isinstance(sky, dict):
            err("sky", "must be an object {horizon, zenith}")
        else:
            for k in ("horizon", "zenith"):
                if k in sky and not _rgb_ok(sky[k]):
                    err(f"sky.{k}", "must be 3 numbers 0..1 (linear RGB)")

    if raw.get("ground") is not None and not _rgb_ok(raw["ground"]):
        err("ground", "must be 3 numbers 0..1 (linear RGB)")

    lights = raw.get("lights")
    if lights is not None:
        if not isinstance(lights, dict):
            err("lights", "must be an object {key, rim}")
        else:
            for lk, lv in lights.items():
                p = f"lights.{lk}"
                if not isinstance(lv, dict):
                    err(p, "must be an object {energy, size, color, loc}")
                    continue
                if "energy" in lv and not (_num(lv["energy"]) > 0):
                    err(f"{p}.energy", "must be a positive wattage")
                if "size" in lv and not (_num(lv["size"]) > 0):
                    err(f"{p}.size", "must be a positive size in metres")
                if "color" in lv and not _rgb_ok(lv["color"]):
                    err(f"{p}.color", "must be 3 numbers 0..1")
                if "loc" in lv and not _v3(lv["loc"]):
                    err(f"{p}.loc", "must be 3 numbers [x, y, z]")

    props = raw.get("props")
    if props is not None:
        if not isinstance(props, dict):
            err("props", "must be an object")
        else:
            for k in ("towers", "rocks"):
                if k in props and (not _is_int(props[k]) or not (0 <= props[k] <= 2000)):
                    err(f"props.{k}", "must be an integer 0..2000")
            tr = props.get("tower_radius")
            if tr is not None:
                if not _v2(tr) or not (0 < tr[0] <= tr[1]):
                    err("props.tower_radius", "must be [lo, hi] metres with 0 < lo <= hi")
            for i, g in enumerate(props.get("glass") or []):
                p = f"props.glass[{i}]"
                if not isinstance(g, dict) or "at" not in g:
                    err(p, "must be an object with 'at': [x, y, z]")
                    continue
                if not _v3(g["at"]):
                    err(f"{p}.at", "must be 3 numbers")
                if "size" in g and not _v2(g["size"]):
                    err(f"{p}.size", "must be [width, height] metres")
                if "alpha" in g and not (0 < _num(g["alpha"]) <= 1):
                    err(f"{p}.alpha", "must be 0 < alpha <= 1")
            for i, m_ in enumerate(props.get("meshes") or []):
                p = f"props.meshes[{i}]"
                if not isinstance(m_, dict):
                    err(p, "must be an object {obj, at, scale, yaw, color}")
                    continue
                obj = m_.get("obj")
                if not isinstance(obj, str) or not obj.lower().endswith(".obj"):
                    err(f"{p}.obj", "must be a path to a .obj file, relative to the project")
                elif obj.startswith("/") or ".." in obj:
                    err(f"{p}.obj", "must stay inside the project: no absolute paths, no '..'")
                if "at" in m_ and not _v3(m_["at"]):
                    err(f"{p}.at", "must be [x, y, z] in metres")
                if "scale" in m_ and not (_num(m_["scale"]) > 0):
                    err(f"{p}.scale", "must be a positive multiplier")
                if "yaw" in m_ and not _is_num(m_["yaw"]):
                    err(f"{p}.yaw", "must be radians about Z")
                if "color" in m_ and not _rgb_ok(m_["color"]):
                    err(f"{p}.color", "must be 3 numbers 0..1")

            for i, fg in enumerate(props.get("fg") or []):
                p = f"props.fg[{i}]"
                if not isinstance(fg, dict) or not (_v2(fg.get("at")) or _v3(fg.get("at"))):
                    err(p, "must be an object with 'at': [x, y] (z = half the height) or [x, y, z]")
                elif "size" in fg and not _v3(fg["size"]):
                    err(f"{p}.size", "must be 3 numbers [x, y, z]")

    cast = raw.get("cast", [])
    names = set()
    if not isinstance(cast, list):
        err("cast", "must be a list")
        cast = []
    for i, c in enumerate(cast):
        p = f"cast[{i}]"
        if not isinstance(c, dict):
            err(p, "must be an object")
            continue
        cn = c.get("name")
        if not isinstance(cn, str) or not cn.strip():
            err(f"{p}.name", "required: a non-empty name (shots and follow refer to it)")
        elif cn in names:
            err(f"{p}.name", f"duplicate cast name {cn!r}")
        else:
            names.add(cn)
        if "color" in c and not _rgb_ok(c["color"]):
            err(f"{p}.color", "must be 3 numbers 0..1")
        if "skin" in c and not _rgb_ok(c["skin"]):
            err(f"{p}.skin", "must be 3 numbers 0..1")
        path = c.get("path")
        if path is not None:
            if not (isinstance(path, list) and len(path) == 2
                    and all(isinstance(pt, (list, tuple)) and len(pt) in (2, 3)
                            and all(_is_num(x) for x in pt) for pt in path)):
                err(f"{p}.path", "must be two points, each [x, y] or [x, y, z] — the walk is a straight line")
            elif list(path[0][:2]) == list(path[1][:2]):
                warn(f"{p}.path", "start and end are the same point; the walk goes nowhere")
        walk = c.get("walk")
        if walk is not None:
            if not (isinstance(walk, list) and len(walk) == 2 and all(_is_int(x) for x in walk)):
                err(f"{p}.walk", "must be [first_frame, last_frame] integers")
            else:
                f0, f1 = walk
                if not (0 <= f0 < f1):
                    err(f"{p}.walk", f"[{f0}, {f1}] is not an increasing frame window")
                elif frames and f1 > frames:
                    err(f"{p}.walk", f"walk ends at frame {f1} but the film is {frames} frames")
        if "stride" in c and not (_num(c["stride"]) >= 0.05):
            err(f"{p}.stride", "must be >= 0.05 m or the feet slide")
        gait = c.get("gait")
        if gait is not None:
            if not isinstance(gait, dict):
                err(f"{p}.gait", "must be an object")
            else:
                for k in ("swing", "arm_swing", "knee_lift", "bob", "lean", "elbow_bend", "carry_angle"):
                    if k in gait and not _is_num(gait[k]):
                        err(f"{p}.gait.{k}", "must be a number")
                if "carry" in gait and gait["carry"] not in (None, "L", "R"):
                    err(f"{p}.gait.carry", "must be 'L', 'R' or null")

    shots = raw.get("shots")
    if shots is not None:
        if not isinstance(shots, list):
            err("shots", "must be a list")
            shots = []
        prev_out = None
        for i, s in enumerate(shots):
            p = f"shots[{i}]"
            if not isinstance(s, dict):
                err(p, "must be an object")
                continue
            si, so = s.get("in"), s.get("out")
            if not _is_int(si) or not _is_int(so):
                err(p, "needs integer 'in' and 'out' frames")
            else:
                if si < 0:
                    err(f"{p}.in", "must be >= 0")
                if so <= si:
                    err(f"{p}.out", f"must be greater than in ({si})")
                if frames and so > frames:
                    err(f"{p}.out", f"shot ends at {so} but the film is {frames} frames")
                # both authoring styles are legal: [in, out] inclusive, and [in, out+1]
                if prev_out is not None and si < prev_out:
                    warn(p, f"starts at {si} but the previous shot runs to {prev_out} — "
                            f"{prev_out - si + 1} shared frame(s), the earlier shot wins")
                elif prev_out is not None and si > prev_out + 1:
                    warn(p, f"gap of {si - prev_out - 1} frame(s) before this shot; "
                            f"the previous shot holds")
                prev_out = so
            if "lens" in s and not (8 <= _num(s["lens"]) <= 400):
                err(f"{p}.lens", "must be 8..400 mm")
            for k in ("cam", "target"):
                v = s.get(k)
                if v is not None and not (_v3(v) or (isinstance(v, list) and len(v) == 2 and all(_v3(x) for x in v))):
                    err(f"{p}.{k}", "must be [x, y, z] or [[x,y,z], [x,y,z]] for a move")
            if "cam_offset" in s and not _v3(s["cam_offset"]):
                err(f"{p}.cam_offset", "must be [x, y, z]")
            if "follow" in s:
                if s["follow"] not in names:
                    err(f"{p}.follow", f"no cast member named {s['follow']!r} "
                                       f"(cast: {', '.join(sorted(names)) or 'none'})")
                if "cam" not in s and "cam_offset" not in s and "move" not in s:
                    err(f"{p}.follow", "tracks the subject but the shot has no camera: "
                                       "give cam, cam_offset, or move")
            mv = s.get("move")
            if mv is not None:
                if not isinstance(mv, dict) or mv.get("type") not in ("push", "orbit", "crane"):
                    err(f"{p}.move", "must be {type: push|orbit|crane, ...}")
                elif "follow" not in s:
                    warn(f"{p}.move", "camera moves are authored around a subject; set 'follow'")

    titles = raw.get("titles")
    if titles is not None:
        if not isinstance(titles, list):
            err("titles", "must be a list")
        else:
            for i, t in enumerate(titles):
                p = f"titles[{i}]"
                if not isinstance(t, dict) or not isinstance(t.get("text"), str):
                    err(p, "must be an object with a string 'text'")
                    continue
                ti, to = t.get("in", 0), t.get("out")
                if not _is_num(ti) or not _is_num(to) or to <= ti:
                    err(p, "needs numeric 'in' < 'out' in seconds")
                elif _is_num(raw.get("duration", 6.0)) and to > float(raw["duration"]) + 1e-6:
                    warn(f"{p}.out", f"title ends at {to}s but the film is {raw['duration']}s long")
                if "size" in t and not (0 < _num(t["size"]) <= 0.5):
                    err(f"{p}.size", "must be 0..0.5 of frame height")
                if "y" in t and not (0 <= _num(t["y"]) <= 1):
                    err(f"{p}.y", "must be 0..1 of frame height")
                if "pos" in t and t["pos"] not in ("left", "center", "right"):
                    err(f"{p}.pos", "must be left, center or right")

    fade = raw.get("fade")
    if fade is not None:
        if not isinstance(fade, dict):
            err("fade", "must be an object {in, out} in seconds")
        else:
            for k in ("in", "out"):
                if k in fade and not (_num(fade[k]) >= 0):
                    err(f"fade.{k}", "must be >= 0 seconds")

    dof = raw.get("dof")
    if dof is not None:
        if not isinstance(dof, dict):
            err("dof", "must be an object {focus, range, amount}")
        else:
            if "focus" in dof and not (_num(dof["focus"]) > 0):
                err("dof.focus", "must be a positive distance in metres")
            if "range" in dof and not (_num(dof["range"]) > 0):
                err("dof.range", "must be positive")
            if "amount" in dof and not (0 <= _num(dof["amount"]) <= 4):
                err("dof.amount", "must be 0..4")

    snd = raw.get("sound")
    if snd is not None:
        if not isinstance(snd, dict):
            err("sound", "must be an object {motif, cue, wind}")
        else:
            motif = snd.get("motif")
            if motif is not None and not (isinstance(motif, list) and motif
                                          and all(_is_num(m) and 55 <= m <= 2000 for m in motif)):
                err("sound.motif", "must be a list of frequencies 55..2000 Hz")
            if "cue" in snd and not (0 <= _num(snd["cue"]) <= 5):
                err("sound.cue", "must be 0..5 (fraction of the film)")
            if "wind" in snd and not (0 <= _num(snd["wind"]) <= 1):
                err("sound.wind", "must be 0..1")

    rng = raw.get("range")
    if rng is not None:
        if not (isinstance(rng, list) and len(rng) == 2 and all(_is_int(x) for x in rng)):
            err("range", "must be [first_frame, last_frame] integers for a partial render")
        elif not (0 <= rng[0] < rng[1]):
            err("range", "must be [a, b] with a < b")

    return errors, warnings


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


# ────────────────────────────────────────────────────────────────── describing
def describe(spec: dict) -> dict:
    """Everything an agent needs to know before spending a frame."""
    w, h = spec["resolution"]
    ssaa = int(spec.get("ssaa", 2))
    return {
        "name": spec["name"],
        "frames": spec["frames"],
        "fps": spec["fps"],
        "duration_s": round(spec["frames"] / spec["fps"], 3),
        "preset": spec.get("preset"),
        "resolution": [w, h],
        "ssaa": ssaa,
        "raster_pixels": [w * ssaa, h * ssaa],
        "samples": spec.get("samples"),
        "denoise": spec.get("denoise"),
        "cast": [{"name": c.get("name"), "path": c.get("path"), "walk": c.get("walk")}
                 for c in spec.get("cast", [])],
        "shots": [{"in": s.get("in"), "out": s.get("out"), "lens": s.get("lens"),
                   "follow": s.get("follow"), "move": (s.get("move") or {}).get("type")}
                  for s in spec.get("shots", [])],
        "has_titles": bool(spec.get("titles")),
        "has_dof": bool(spec.get("dof")),
        "out_dir": f"out/{spec['name']}",
        "mp4": f"out/{spec['name']}/{spec['name']}.mp4",
    }


def estimate(spec: dict, calibration: dict | None = None) -> dict:
    """Predict both paths. Numbers come from measured receipts when we have them.

    `calibration` is {'ms_per_px_frame': float, 'n': int} recorded by past raster runs.
    Without it the raster estimate is None — a guess is not a measurement.
    """
    w, h = spec["resolution"]
    ssaa = int(spec.get("ssaa", 2))
    frames = max(1, int(spec["frames"]))
    px = w * h * ssaa * ssaa
    out = {"frames": frames, "pixels_per_frame": px, "raster_s": None, "cycles_s": None,
           "basis": "unmeasured"}
    if calibration and calibration.get("ms_per_px_frame"):
        out["raster_s"] = round(px * frames * calibration["ms_per_px_frame"] / 1000.0, 1)
        out["basis"] = f"calibrated on {calibration.get('n', '?')} previous raster run(s)"
    if calibration and calibration.get("cycles_s_per_frame") and calibration.get("cycles_px"):
        scale = (w * h) / calibration["cycles_px"]
        out["cycles_s"] = round(frames * calibration["cycles_s_per_frame"] * max(0.35, scale), 1)
    return out


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/waefrebeorn/wuBu3D/schema/film.spec.json",
    "title": "WuBu3D film spec",
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "pattern": "^[^/\\\\.]+$",
                 "description": "output directory under out/"},
        "preset": {"enum": list(PRESETS), "default": "cartoon",
                   "description": "fills resolution, samples, denoise"},
        "duration": {"type": "number", "minimum": 0.01, "maximum": 900, "default": 6.0,
                     "description": "seconds; frames = round(duration * fps)"},
        "fps": {"type": "integer", "minimum": 1, "maximum": 120, "default": 24},
        "resolution": {"type": "array", "items": {"type": "integer", "minimum": 16, "maximum": 4320},
                       "minItems": 2, "maxItems": 2,
                       "description": "must be even; default from preset"},
        "samples": {"type": "integer", "minimum": 1, "maximum": 4096,
                    "description": "Cycles samples; the raster path ignores it"},
        "denoise": {"type": "boolean"},
        "seed": {"type": "integer", "default": 7},
        "fog": {"type": "number", "exclusiveMinimum": 0, "default": 140},
        "ssaa": {"type": "integer", "minimum": 1, "maximum": 4, "default": 2},
        "raster_gain": {"type": "number", "minimum": 0.1, "maximum": 4.0, "default": 1.15},
        "range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2,
                  "description": "partial render [first, last]; a range clears old frames first"},
        "ground": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
        "sky": {
            "type": "object",
            "properties": {
                "horizon": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "zenith": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "additionalProperties": False,
        },
        "lights": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "energy": {"type": "number", "exclusiveMinimum": 0},
                    "size": {"type": "number", "exclusiveMinimum": 0},
                    "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    "loc": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                },
            },
        },
        "props": {
            "type": "object",
            "properties": {
                "towers": {"type": "integer", "minimum": 0, "maximum": 2000},
                "rocks": {"type": "integer", "minimum": 0, "maximum": 2000},
                "tower_radius": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "meshes": {"type": "array", "items": {
                    "type": "object",
                    "required": ["obj"],
                    "properties": {
                        "obj": {"type": "string", "pattern": "\\.obj$",
                                "description": "OBJ path relative to the project root"},
                        "at": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                        "scale": {"type": "number", "exclusiveMinimum": 0},
                        "yaw": {"type": "number", "description": "radians about Z"},
                        "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    },
                }},
                "glass": {"type": "array", "items": {
                    "type": "object",
                    "required": ["at"],
                    "properties": {
                        "at": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                        "size": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                        "alpha": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
                        "yaw": {"type": "number"}, "pitch": {"type": "number"},
                        "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    },
                }},
                "fg": {"type": "array", "items": {
                    "type": "object", "required": ["at"],
                    "properties": {
                        "at": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3},
                        "size": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                        "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    },
                }},
            },
        },
        "cast": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    "skin": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                    "path": {"type": "array",
                             "items": {"type": "array", "items": {"type": "number"},
                                       "minItems": 2, "maxItems": 3},
                             "minItems": 2, "maxItems": 2,
                             "description": "start and end [x, y] (z optional); the figure yaws along the heading"},
                    "walk": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                    "stride": {"type": "number", "minimum": 0.05},
                    "hood": {"type": "boolean"}, "coat": {"type": "boolean"},
                    "gait": {"type": "object"},
                },
            },
        },
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["in", "out"],
                "properties": {
                    "in": {"type": "integer", "minimum": 0},
                    "out": {"type": "integer", "minimum": 1},
                    "cam": {}, "target": {}, "cam_offset": {},
                    "follow": {"type": "string", "description": "cast member the camera tracks"},
                    "lens": {"type": "number", "minimum": 8, "maximum": 400},
                    "move": {"type": "object",
                             "properties": {"type": {"enum": ["push", "orbit", "crane"]}},
                             "required": ["type"]},
                },
            },
        },
        "titles": {"type": "array", "items": {
            "type": "object",
            "required": ["text", "in", "out"],
            "properties": {
                "text": {"type": "string"},
                "in": {"type": "number", "minimum": 0},
                "out": {"type": "number", "minimum": 0},
                "size": {"type": "number", "minimum": 0, "maximum": 0.5},
                "y": {"type": "number", "minimum": 0, "maximum": 1},
                "pos": {"enum": ["left", "center", "right"]},
                "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
        }},
        "fade": {"type": "object", "properties": {"in": {"type": "number", "minimum": 0},
                                                  "out": {"type": "number", "minimum": 0}}},
        "dof": {"type": "object", "properties": {"focus": {"type": "number", "exclusiveMinimum": 0},
                                                 "range": {"type": "number", "exclusiveMinimum": 0},
                                                 "amount": {"type": "number", "minimum": 0, "maximum": 4}}},
        "sound": {"type": "object", "properties": {
            "motif": {"type": "array", "items": {"type": "number", "minimum": 55, "maximum": 2000}},
            "cue": {"type": "number", "minimum": 0, "maximum": 5},
            "wind": {"type": "number", "minimum": 0, "maximum": 1}}},
        "exposure": {"type": "number", "minimum": 0.1, "maximum": 5.0},
        "tonemap": {"enum": ["srgb", "aces"], "default": "srgb",
                    "description": "aces applies the tone curve in linear light, like a film pipeline"},
        "accum": {"type": "integer", "minimum": 1, "maximum": 16, "default": 1,
                  "description": "temporal samples per output frame: jittered AA and shutter blur"},
        "shutter": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.0,
                    "description": "shutter interval as a fraction of a frame (0.5 = 180 degrees)"},
        "ambient": {"type": "number", "minimum": 0.0, "maximum": 1.5, "default": 0.24,
                    "description": "flat light floor; keeps shadowed surfaces readable"},
        "captions": {
            "type": "object",
            "properties": {
                "words": {"type": "string", "description": "json list of {word, start, end}"},
                "size": {"type": "number", "exclusiveMinimum": 0, "maximum": 0.5},
                "y": {"type": "number", "minimum": 0, "maximum": 1},
                "stroke": {"type": "boolean"},
            },
        },
        "ao": {"enum": ["taps", "ssao"], "default": "taps",
               "description": "ambient occlusion pass: fixed taps (cheap) or raytraced"},
        "ao_radius": {"type": "number", "minimum": 0.02, "maximum": 8.0, "default": 0.35},
        "ao_rays": {"type": "integer", "minimum": 1, "maximum": 32, "default": 10},
    },
    "additionalProperties": True,
}


def schema() -> dict:
    return copy.deepcopy(SCHEMA)
