# glTF / GLB: rigged characters as actors

Before this, a character in wuBu3D was a chain of primitives posed by our own 21-joint rig. It
moved, but it was our mannequin wearing a colour. A GLB from an asset kit is a **rigged actor
with its own skeleton, its own skin weights and its own clips** — Kenney's Mini Characters ship
32 animations each (`idle`, `walk`, `sprint`, `jump`, `attack-kick-left`, `die`, …), all CC0.

## Using one

```json
"cast": [{
  "name": "walker",
  "glb": "assets/cache/mini-characters/Models/GLB format/character-female-a.glb",
  "clip": "walk",
  "clip_speed": 1.0,
  "scale": 2.2,
  "path": [[-5.2, -3.0, 0], [3.2, 1.6, 0]],
  "walk": [0, 47]
}]
```

`walk` is still the frame window the actor travels across; `clip` is the performance that plays
underneath it. Time is `(frame - walk[0]) / fps × clip_speed`, wrapped by the clip's own
length, so a 0.667 s walk cycle loops three times across a 2 s shot instead of running once and
freezing.

## Two paths, one asset, different fidelity

| | raster (`raster`) | Cycles (`render`/`make`) |
|---|---|---|
| geometry | our reader, CPU linear-blend skinning | Blender's own glTF importer |
| skeleton | joints resolved by walking the node tree | imported armature |
| clip | sampled per frame in Python | the imported action |
| colour | material `baseColorFactor` (flat) | full PBR + the kit's texture atlas |
| speed | 48 skinned frames of a room in 27 s @ 640×360 | one 480² frame in ~1.3 s |

Cycles is the fidelity path and it costs nothing to get: Blender already understands glTF, so
the importer hands us materials, normal maps and the full clip. The raster path reimplements
enough of the format to keep the fast preview honest — and it is the path that has to stay
dependency-free, which is why the reader is written against the spec instead of wrapping a
library.

## What the reader does

* GLB container and `.gltf` + external buffers/data URIs.
* Accessors with byte strides (interleaved and packed).
* Node hierarchy: `matrix` or TRS, resolved to world matrices.
* Skins: joints, inverse bind matrices (column-major, transposed on read), four influences.
  `jointMatrix = inverse(global(meshNode)) · global(joint) · inverseBind` — dropping the
  mesh-node term is the classic bug and it shows up as a giant head and a shrunken body.
* Animation channels: translation/rotation/scale, LINEAR / STEP / CUBICSPLINE, quaternions
  slerped along the shortest arc.
* Y-up → Z-up conversion on output, feet grounded at z = 0.

## What it does not do

* **Texture sampling in the raster path.** The Cycles path shows the kit's atlas; the raster
  path paints `baseColorFactor`. A textured raster needs UV interpolation plus a PNG decoder
  and a bilinear sampler, and that is a deliberate non-goal for the preview renderer.
* **Draco / meshopt compression.** Kenney, Quaternius and Poly Haven's glTF are uncompressed.
* **Morph targets, sparse accessors.**
* **Clip looping in the Cycles path.** The imported action plays once from the shot's start; if
  the shot is longer than the clip, it holds the last pose. The raster path loops correctly,
  which is why the preview is the place to check timing.
