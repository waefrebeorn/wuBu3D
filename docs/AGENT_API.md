# Agent API

WuBu3D is built to be driven by a process, not a person. This is the contract: what an
agent may call, what it gets back, what the exit codes mean, and what it can trust.

Everything is one JSON file in, one JSON object out. Human logs never share a stream with
machine output when `--json` is set.

```
schema   → the spec's schema, as JSON Schema
validate → is this spec legal? path-precise errors, exit 2 if not
inspect  → resolved numbers (frames, resolution, shots) without rendering
plan     → frames, shots, and cost on both render paths (calibrated on measured receipts)
raster   → the C11 path: a finished film in seconds, no Blender
still    → one frame through the C11 path (~1 s): the viewport grab an agent looks at
render   → Cycles frames (delivery path)
finish   → denoise → grade → score → mux
make     → render + finish
qa       → measure a rendered film: lit? moving? dead frames?
demo     → write a demo spec and deliver it
```

## The loop an agent should run

```bash
python3 src/wubu3d.py schema                                  # learn the fields once
python3 src/wubu3d.py validate my_film.json                   # exit 2 + paths if illegal
python3 src/wubu3d.py plan     my_film.json --json             # frames, shots, cost
python3 src/wubu3d.py still    my_film.json --at 70             # one frame, ~1 s: look at it
python3 src/wubu3d.py raster   my_film.json                    # seconds: check framing
#   look at out/<name>/<name>.mp4 (or a frame), fix the spec, repeat
python3 src/wubu3d.py make     my_film.json                    # Cycles, the delivery render
python3 src/wubu3d.py qa       my_film.json --json             # numbers, not adjectives
```

Never go from `validate` straight to `make`. The raster frame is 300–6,000× cheaper and
shows every framing, walk and camera error; a Cycles pass spent on a wrong shot costs an hour
and teaches nothing.

## Exit codes

| code | meaning | what an agent does next |
|---|---|---|
| 0 | the command's work finished (validate: the spec is legal) | read the JSON |
| 1 | runtime failure — missing binary, ffmpeg error, no blender | fix the environment, not the spec |
| 2 | the spec is invalid, or `validate` found errors | read `errors[].path` and repair the spec |

A renderer never starts on an invalid spec: `build`, `raster`, `render`, `finish` and `make`
all validate first and exit 2 with the same messages `validate` prints.

## `--json`

One JSON object on stdout; every `[wubu3d]` log line moves to stderr. `validate --json`:

```json
{
 "ok": false,
 "spec": "specs/film.json",
 "errors":   [{"level": "error",   "path": "shots[0].follow", "message": "no cast member named 'nobody' (cast: keeper)"}],
 "warnings": [{"level": "warning", "path": "durration",       "message": "unknown key 'durration' — no effect; ..."}]
}
```

`plan --json` adds `estimate` and `calibration`:

```json
"estimate": {"frames": 144, "pixels_per_frame": 1228800, "raster_s": 19.4,
             "cycles_s": 496.0, "basis": "calibrated on 3 previous raster run(s)"},
"calibration": {"ms_per_px_frame": 0.00011, "n": 3, "cycles_s_per_frame": 3.45, "cycles_px": 153600}
```

When there is no receipt to calibrate from, `raster_s` is `null` and `basis` says
`unmeasured`. That is deliberate: an estimate invented from a formula is a number the
project cannot defend. One raster run is enough to calibrate the box.

## The receipt

Every delivered film writes `out/<name>/receipt.json`. It is the claim, in a file:

```json
{
 "tool": "wubu3d", "version": "1.1", "name": "keepsake", "path": "raster",
 "created": "2026-11-26T17:04:11+00:00",
 "spec_sha256": "…", "resolution": [854, 480], "ssaa": 2,
 "frames": 144, "fps": 24, "duration_s": 6.0,
 "timings_s": {"raster": 5.5, "composite": 6.1, "grade": 5.9, "score": 0.4, "mux": 0.7, "total": 19.2},
 "scene": {"frames_rasterised": 144, "tris_per_frame": 2534, "glass_and_culled": "0 glass, 0 occlusion-culled"},
 "qa": {"frames": 144, "mean_luma": 32.7, "body_mean_luma": 37.4, "min_luma": 0.0, "max_luma": 38.7,
        "black_frames": 2, "motion_mean": 1.63, "motion_max": 5.16, "static_frames": 0, "passed": true},
 "outputs": {"mp4": "keepsake.mp4", "bytes": 511424, "sha256": "…", "score_wav": "score.wav", "score_bytes": 1152044}
}
```

`qa` is measured on 96×54 thumbnails, so it costs about a second on a 144-frame film:

* `body_mean_luma` — mean luma with the first and last tenth excluded (fades live there).
  Below ~6 the film is a black rectangle and `passed` is false.
* `motion_max` / `motion_mean` — mean absolute difference between consecutive thumbnails.
  A film that never exceeds 0.05 is a still with sound; `passed` is false.
* `static_frames` — count of adjacent pairs below 0.02. A long run of these is a hold that
  was meant to be a move.
* `black_frames` — luma < 1.0. Two or three at the head and tail are fades, not failures.

`sha256` is of the delivered MP4, so a receipt identifies the exact file it describes.

## Validation rules worth knowing

The validator is deliberately opinionated — every rule below exists because the
alternative cost a real render:

* `frames` is **derived** (`round(duration × fps)`); setting it is a warning, never an effect.
* odd resolution sides are an error, with the libx264 reason attached.
* a `walk` that ends past the last frame is an error — the walk is cut mid-stride.
* `follow` must name a cast member that exists (the error lists the cast).
* a shot with `follow` still needs a camera: `cam`, `cam_offset` or `move`.
* unknown top-level keys are warnings that name the key and list the known ones — typo
  protection without breaking forward-compatible specs.
* shot ranges accept both `[in, out]` inclusive and `[in, out+1]`; only real overlaps
  (more than one shared frame) and real gaps are flagged.

## Testing

`python3 tests/test_agent_cli.py` runs the contract: 12 cases, no network, about two
seconds. It asserts exit codes, that each message names the offending path, and that an
invalid spec never reaches a renderer. Run it before pushing a change to the contract.
