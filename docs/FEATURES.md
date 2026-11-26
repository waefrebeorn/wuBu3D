# WuBu3D spec reference

A film is one JSON file. `wubu3d.py` compiles it to a Blender scene and, separately, to a
binary stream this repo's own rasteriser eats. Both paths read the same numbers, so a preview
and a delivery frame come from one source.

```bash
python3 wubu3d.py build  specs/x.json     # spec -> scene.py  (+ spec.json, resolved)
python3 wubu3d.py render specs/x.json     # Cycles CPU frames
python3 wubu3d.py raster specs/x.json     # C11 rasteriser: colour + depth + normal passes
python3 wubu3d.py finish specs/x.json     # denoise (if any) -> grade -> score -> mux
python3 wubu3d.py demo --preset cinematic --raster
```

Agent-facing commands (machine-readable, exit codes, see `AGENT_API.md`):

```bash
python3 wubu3d.py schema                 # the spec as JSON Schema
python3 wubu3d.py validate specs/x.json  # path-precise errors, exit 2 when illegal
python3 wubu3d.py inspect  specs/x.json  # resolved numbers, no render
python3 wubu3d.py plan     specs/x.json  # frames + cost on both paths (calibrated)
python3 wubu3d.py qa       specs/x.json  # luma, motion, dead frames from the render
python3 wubu3d.py still    specs/x.json --at 70   # one frame through the raster path, ~1 s
```

## Vertical and captions

`"preset": "vertical"` renders 720×1280 — the grade skips the 2.39:1 bars for portrait frames,
because cropping a vertical frame to cinema ratio throws away the picture the format exists for.

Captions take either a list of `{text, in, out}` (seconds) or a pointer to a whisper-style words
file, which is what the transcription tools already emit:

```json
"captions": {"words": "assets/words_probe.json", "size": 0.045, "y": 0.7, "stroke": true}
```

Words files are `[{"word": "hello", "start": 0.2, "end": 0.6}]`. One word at a time, centered,
with a black outline (`stroke_width = size/16`). The path must stay inside the project.

`"ambient"` (0..1.5, default 0.24) is the flat light floor: what a surface keeps when nothing
lights it. It rides in the frame struct's spare float, so it costs the rasteriser nothing.

**Frame timing is the frame number, not the loop index.** Titles, captions and fades are timed
from the frame's own number, so a range render (`"range": [120, 180]`) or `still --at 150` shows
the captions that belong at 6.25 s — not the ones from the top of the film.

## Meshes

Real geometry comes in as OBJ. An agent that can model (or finds an asset) does not have to
rebuild it out of primitives:

```json
"props": {
  "meshes": [
    {"obj": "assets/obelisk.obj", "at": [-1.6, 3.0, 0], "scale": 1.0, "yaw": 0.4,
     "color": [0.30, 0.29, 0.32]}
  ]
}
```

Read by `src/wubu3d.py` (raster path) and by the generated Blender scene (Cycles path), from
the same file. The reader takes `v` and `f` (triangles, quads, n-gons, negative indices) and
ignores the rest; materials are the placement's `color`, because both renderers shade per
vertex. Vertices are unshared per face, so an imported mesh keeps its hard edges instead of
turning into a smooth blob. Paths must stay inside the project — absolute paths and `..` are
refused by the validator.

Every render also writes `out/<name>/receipt.json` (timings, triangle count, QA, mp4 sha256)
and appends one line to `out/_history.jsonl`, which is what `plan` calibrates from.

## Top level

| key | meaning | default |
|---|---|---|
| `name` | output directory under `out/` | required |
| `preset` | `preview` / `cartoon` / `cinematic` — fills resolution, samples, denoise | `cartoon` |
| `duration` | seconds — **this is what sets frame count** (`frames = round(duration × fps)`) | 6.0 |
| `fps` | frames per second | 24 |
| `resolution` | `[w, h]`, must be even for H.264 | from preset |
| `samples` | Cycles samples (Blender path only) | from preset |
| `seed` | prop placement seed | 7 |
| `fog` | exponential fog distance, metres | 140 |
| `ssaa` | raster supersample factor (2 = 4× pixels, Lanczos resolve) | 2 |
| `raster_gain` | brightness multiplier for flat vertex colour in the raster path | 1.15 |

## Scene

```json
"ground": [0.026, 0.028, 0.034],
"sky": {"horizon": [0.055, 0.062, 0.085], "zenith": [0.010, 0.012, 0.020]},
"props": {"towers": 40, "tower_radius": [28, 120], "rocks": 12}
```

## Cast

```json
{"name": "keeper", "color": [0.075, 0.070, 0.082], "skin": [0.46, 0.35, 0.28],
 "path": [[0, -6], [0, 22]], "walk": [0, 143], "stride": 0.85,
 "hood": true, "coat": true,
 "gait": {"swing": 0.52, "arm_swing": 0.36, "knee_lift": 0.55, "bob": 0.022,
          "lean": 0.04, "elbow_bend": 0.22, "carry": "R", "carry_angle": -0.30}}
```

* `path` — two XY points; the character is yawed along that heading, so it walks forward.
* `walk` — frame window for one traversal; stride sets the step length, hence cadence.
* `gait` — the same knobs feed the raster rig and the Blender armature.
* The rig is 21 joints, 1.78 m, ground at z = 0 (`wubu3d_rig.py`).

## Shots

```json
{"in": 0, "out": 60, "follow": "keeper", "lens": 50,
 "cam": [-4, -6, 1.6], "target": [0, 0, 1.1]}
```

| key | meaning |
|---|---|
| `cam` / `target` | static position and look-at, or `[[start], [end]]` for a linear move |
| `follow` | name of a cast member; the target tracks them at +1.1 m |
| `cam_offset` | with `follow`: camera = subject + offset, so distance stays constant |
| `move` | named camera move, see below |
| `lens` | focal length, mm (thin-lens 24 mm sensor; the raster converts to identical FOV) |

### Camera moves

```json
"move": {"type": "push",  "from": 8.0, "to": 4.6, "angle": -0.5, "height": 1.5}
"move": {"type": "orbit", "from": -0.9, "to": 0.6, "radius": 5.0, "height": 1.62}
"move": {"type": "crane", "radius": 4.5, "angle": -0.6, "z": [1.0, 3.2]}
```

`angle` and `from`/`to` are radians around the subject, 0 = straight in front (−Y).

## Titles

```json
"titles": [{"text": "WuBu3D", "in": 0.2, "out": 2.4, "size": 0.115, "y": 0.40,
            "pos": "center", "color": [0.93, 0.90, 0.84]}]
```

`size` and `y` are fractions of frame height. Drawn after the letterbox, with a hard shadow,
in Anton (`FONT_PATH`). `in`/`out` are seconds.

## Post

```json
"fade": {"in": 0.7, "out": 0.9},
"dof":  {"focus": 5.2, "range": 7.0, "amount": 0.8}
```

> **Raster path:** the ground is a 48×48 grid over ±200 m (a single quad clipped to
> screen coordinates in the millions and lost every pixel to float precision), and a 512²
> shadow map is built per frame from the opaque triangles, compared per pixel with 2×2 PCF
> (0.38 ms/frame of the ~7 ms). `wuburaster --no-shadow` renders without it. Notes and
> measurements: `SH4DER_PVR_STUDY.md`.

`"ao": "ssao"` switches the composite's ambient occlusion from twelve fixed taps to a
screen-space raytraced pass with a world-space radius (`ao_radius`, metres, default 0.35;
`ao_rays`, default 10). It costs ~0.42 s/frame at 320×180 versus 0.04 s for the taps, so it is
opt-in: use it for `still` look-dev and hero frames. Notes and measurements:
`CORTAO_STUDY.md`.

* `fade` — multiplies the frame by a ramp at each end of the film.
* `dof` — defocus from the depth pass: `k = (|z − focus| / range)^{1.4} × amount`, applied as a
  half-res blur mix. Raster path only (Cycles has its own camera DOF).

Grade is fixed (sky composite, median de-firefly, soften, bloom, S-curve, highlight rolloff,
vignette, 2.39:1 bars). Nothing to configure, on purpose.

## Validation

`validate` is the contract, and every renderer runs it before touching a frame. Errors name
the field (`shots[0].follow`, `cast[0].walk`); unknown top-level keys are warnings, not
errors. The rules exist because each one cost a render: `frames` is derived (setting it does
nothing), odd resolution sides break libx264, a `walk` past the last frame is cut mid-stride,
`follow` must name a real cast member, and a shot with `follow` still needs `cam`,
`cam_offset` or `move`.

## Gotchas that cost real runs

1. `frames` is **derived** from `duration × fps`. Setting `frames` directly does nothing.
2. Odd heights kill libx264 (`height not divisible by 2`); `mux` guards, but specs should not
   ask for 405.
3. `cam_offset` and `move` only apply when `follow` names an existing cast member.
4. The rasteriser ignores `samples` — it has no sampling.
5. A move radius under ~4 m puts the camera inside the coat; 5 m is the useful minimum for a
   full-body frame at 50 mm.
6. Blender 5.x: `Scene.node_tree` is gone (`compositing_node_group`), and Glare parameters are
   input sockets — which is why grading lives in NumPy, not the compositor.
