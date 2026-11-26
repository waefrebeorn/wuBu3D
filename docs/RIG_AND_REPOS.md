# Rig, repos and what was actually learned

Written after the "cone figure" failure. The raster character read as a traffic cone
because it was three primitives, not because the shading was wrong.

## What is on disk now

| source | how it got here | size | used for |
|---|---|---|---|
| `CubeCoders/Jet` | clone | 17 MB | fixed-function pipeline shape, framebuffer-only output, zero deps |
| `Dante-Leoncini/Whisk3D-Editor` | clone | — | retro-first constraint, undo rules, serial-based resource purge |
| `blender/blender` | `--depth 1 --filter=blob:none` + sparse checkout of `editors/armature` and `editors/mesh` | 6.4 MB | real skinning and armature code to read |
| `creator-generalist` | clone | — | 2D/3D/game skill layout for agents |
| `rea-toon` | clone | — | short-drama breakdown docs |
| `blender-ps1-shader` | clone | — | PS1 vertex-snap / affine texture look |
| `pixelfx`, `lemo-opuscar`, `WUBUMV`, `PS1-ify` | clone | — | pixel-art and film pipelines |

Blender is blobless: the commit tree is local, file bodies are fetched on demand with
`git show HEAD:path`. That keeps a 1.5 GB repository at 6.4 MB of working tree.

## Lessons taken, and where each one landed

**Blender `armature_skinning.cc`** — Blender has exactly two weighting modes: envelope
(`distfactor_to_bone`, radius falloff per bone) and heat equilibrium (solved in
`meshlaplacian`). Bones flagged `BONE_NO_DEFORM` are excluded from both. Lesson applied:
our rig keeps a `PARENT` table and a `JWT`-style joint list so a weighting pass can be added
later without touching the pose code; nothing is weighted yet, parts are rigid, which is
correct for a fixed-function rasteriser and wrong for a deforming skin.

**character-forge `references/rig-and-animation-lab.md`** — 31 bones, zone-gated Gaussian
weights, pole-target IK (left π, right 0), contact poses at 0/0.5 and pass poses at 0.25/0.75,
three-quarter camera at ~42°, and: *verify motion with pixel diffs, because identical-looking
sheets can still differ*. The walk cycle here uses the contact/pass key structure and the
opposite-arm swing; the camera rule is why the demo shots sit off-axis rather than front-on.

**character-forge `references/world-scale-and-adults.md`** — one unit = one metre, ground at
z = 0, adults 1.50–2.00 m, 4–7 heads. Enforced in `wubu3d_rig.HEIGHT = 1.78` and measured
after every build (the rig reports z range 0.000 … 1.810, x ±0.330).

**Jet** — fixed-function pipeline, no scene graph, no shader abstraction. Confirms the raster
path should stay a straight transform → clip → raster → fog loop.

**Whisk3D** — retro-first: if it does not run on dead hardware, it is not the target. The
rasteriser still writes plain PPM and flat binaries, no PNG, no zlib.

## The rig

`wubu3d_rig.py` (~360 lines, stdlib only):

* **21 joints** — pelvis, spine, chest, neck, head, head_top, clavicle/shoulder/elbow/wrist
  per side, hip/knee/ankle/toe per side. Rest pose in metres, `.L` on +X as the skill requires.
* **Forward kinematics** — `pose(phase, cfg)` returns world-space joints for a walk phase.
  Rotation about X for swing, about Y for lean. Hip swing, knee lift, arm swing, elbow bend,
  pelvis bob at twice the step rate, head counter-bob.
* **Mesh primitives** — tapered `capsule` with rounded end caps, `sphere` (lat/long, scalable),
  `tube` (lofted rings with optional caps), `box`.
* **Body** — lofted 12-sided torso from pelvis to shoulders with elliptical cross-sections,
  neck capsule, egg-shaped head forward of the spine, arms as two capsules plus a hand sphere,
  legs as two capsules plus a boot box, a coat lofted from waist to hem, and a hood built as a
  cowl with a **1.95 rad opening at the front** so the face reads instead of a cone.
* **Facing** — the exporter rotates the whole character by the path heading
  (`atan2(dx, dy)`), because a rig that always faces +Y walks backwards in half the shots.

Measured: 1 373 verts / 2 002 tris per frame, 21 joints, height 1.81 m.

## Result

The figure now reads as a hooded walking person: hood with a dark face opening, shoulders,
arms with visible hands, coat to mid-shin, boots below the hem, legs alternating.

Still wrong, in order of how much it costs the frame:

1. **No skinning.** Parts are rigid; a bent elbow shows a seam instead of a smooth joint.
   Fix: add the envelope weighting pass Blender uses, or a 2-bone smoothstep blend per joint.
2. **No face.** A dark hole where the face is. At 480p a single bright eye line would be enough
   to sell it; that is a 12-triangle insert, not a modelling project.
3. **The raster camera is a pinhole with no depth of field**, so the figure sits flat against the
   towers. A cheap 3-tap defocus on the half-res depth pass would fix the separation.
4. **The coat has no folds.** Lofted rings are smooth; adding two sinusoidal bands to the hem
   radius would give it cloth.

## Numbers

| stage | 854×480, 144 frames, ~2 000 tris |
|---|---|
| raster, 3 passes | 47.9 s — 332 ms/frame (figure fills a third of frame) |
| composite | 7.3 s |
| grade + score + mux | ~11 s |
| **spec → MP4** | **~66 s** |

The per-frame cost tripled when the camera moved in, because fill rate is now dominated by the
character rather than the ground. That is the correct scaling: at 320×180 the same scene runs at
~75 ms/frame.
