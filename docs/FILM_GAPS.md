# The third axis: comparing against compositing pipelines, not engines

Two gap lists existed. The census counted what Gumroad sellers sell; `ENGINE_GAPS.md` compared against
game engines. Both are the wrong comparison for half of what wubu3d does, because a cartoon for video
is finished in a **comp**, not in a renderer. This is the list that comparison produces.

## Deep is the dividing line

Nuke's own description: a deep image "contains multiple samples per pixel at varying depths and each
sample contains per-pixel information such as color, opacity, and camera-relative depth"
([Foundry](https://learn.foundry.com/nuke/content/comp_environment/deep/deep_compositing.html)).
That is what lets a compositor put fog in front of a character and behind it without a re-render.

We have a single z-buffer per pixel. **Status: not started.** Deep is a different data structure
(per-pixel sample lists), not a channel.

Two channels of it, though, are cheap and I did them. `wubu_exr_z` writes beauty plus **Z**, and
`wubu_exr_passes` writes **beauty + Z + normals** as `B, G, NX, NY, NZ, R, Z`. The shader already had
the normal in hand, so the G-buffer is one store per pixel.

Verified by walking the file's own chlist and decoding planes, not by asking ffprobe (which reads the
beauty and ignores the rest): channels `['B', 'G', 'NX', 'NY', 'NZ', 'R', 'Z']`, a row through the
subject carrying **2 distinct normal directions** (front and side faces), depth **1.93–2.09**, and a
whole-box test giving exactly **6** distinct normals — a cube has six faces, so that is an exact
check rather than a smoke test.

## What a comp pipeline has that we do not

| capability | reference | wubu3d |
|---|---|---|
| deep images | Nuke, per-sample RGBA+depth | none — single z-buffer |
| multi-channel passes | beauty, Z, normal, motion, AO, crypto | **Z + NX/NY/NZ done** (`wubu_gbuf`, `wubu_exr_passes`); motion, AO, crypto missing |
| node graph | Fusion: "a node based workflow with hundreds of 2D and 3D tools" ([BMD](https://www.blackmagicdesign.com/products/davinciresolve/fusion)) | shot list in Python; no graph |
| grade nodes | lift/gamma/gain, curves, LUTs, power windows | LAB statistics match + ACES; **no LUT** |
| 2.5D cards | camera-projected cards with per-card depth | `plate.py` is 2D only |
| retime / time warp | optical-flow retiming | none |
| tracking / stabilisation | point and planar tracking | none |
| rotoscoping | spline roto with motion blur | none — we generate, we do not isolate |
| text / motion graphics | AE's whole reason for existing ([Adobe](https://helpx.adobe.com/after-effects/desktop/what-s-new/whats-new.html)) | word captions only |
| denoise | temporal + spatial | `wubudenoise.c` |
| grain / vignette / chromatic aberration | the last ten minutes of every comp | **added**: `wubu_lens` — 52 % corner darkening at vignette 0.55, grain amplitude 0.02 |
| bokeh shape | aperture-shaped defocus | 3-tap gaussian DOF only |
| EDL / OTIO interchange | editorial round-trip | none |

## The three that matter for what we actually make

1. **Normal and motion passes.** A comp with beauty + Z can defocus and fog. With normals it can
   relight; with motion vectors it can retime and add directional blur. Both are outputs I already
   compute internally and throw away.
2. **A LUT stage.** Every look in the references was graded by someone with a LUT. We have a
   statistics match and a tonemap curve, which is not the same tool.
3. **2.5D card comps.** `plate.py` composites a render onto a flat plate. The brainrot references use
   *projected* plates with parallax — cards on a camera, each with its own depth. That is a small
   extension of the compositor and a large change in how the shot reads.

## What this axis says about priorities

The census says particles (51 products). The engine comparison says colour management and shadows.
The comp comparison says **passes** — because a renderer that only emits a picture forces the artist
to re-render for every change, and that is the defining limitation of a video pipeline that cannot be
graded.
