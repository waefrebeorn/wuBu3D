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

* `fade` — multiplies the frame by a ramp at each end of the film.
* `dof` — defocus from the depth pass: `k = (|z − focus| / range)^{1.4} × amount`, applied as a
  half-res blur mix. Raster path only (Cycles has its own camera DOF).

Grade is fixed (sky composite, median de-firefly, soften, bloom, S-curve, highlight rolloff,
vignette, 2.39:1 bars). Nothing to configure, on purpose.

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
