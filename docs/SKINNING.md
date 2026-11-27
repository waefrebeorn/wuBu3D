# Skinning

`wubu3d_skin` adds linear blend skinning to the rig: rest mesh → bones → weights → posed mesh.

The rig in `wubu3d_rig` builds geometry directly in posed space, so each limb is a rigid tube that
pivots at a joint. At a 90° bend that tears the surface across the joint, and the tear grows with
the angle. Skinning removes the tear by sharing vertices between the two bones either side.

## API

```python
import wubu3d_skin as sk

bones = {"upper": (shoulder, elbow), "fore": (elbow, wrist)}   # rest positions
names, W = sk.paint(points, bones, radius=0.25)                # rows sum to 1, max 4 influences
mats = {n: sk.bone_matrix(*bones[n], *posed[n]) for n in names}
moved = sk.deform(points, names, W, mats)

# or straight onto a render buffer of (x, y, z, colour) tuples
verts, W = sk.apply_to_render(verts, bones, mats, radius=0.25)
```

## Two mistakes that cost the most time

**Weights from distance to the JOINTS leave nothing blended.** A vertex halfway along a forearm is
far from both ends, so it takes one influence and the limb stays rigid — the whole exercise is
pointless. Weight against the bone SEGMENT instead: a vertex near a joint is then close to *both*
segments, which is exactly where blending belongs.

**A test that bends the bone 180° makes skinning look worse than rigid.** LBS interpolates
matrices, and an exact flip passes through a collapsed frame, so blended vertices pinch harder than
unblended ones. Check the pose is the one you meant before drawing conclusions from the numbers.

## Blend width is the parameter that matters

Worst edge stretch on a two-bone arm bent 90°, 14 rings × 8 sides, 112 vertices:

| blend radius | blended verts | skinned | rigid |
| --- | --- | --- | --- |
| 0.10 | 8 | 1.78× | 2.18× |
| 0.18 | 24 | **1.67×** | 2.18× |
| 0.30 | 56 | 1.67× | 2.18× |
| 0.45 | 80 | 1.70× | 2.18× |
| 0.60 | 96 | 1.68× | 2.18× |

Wider is not automatically better: once the band covers the joint, the gain flattens, and a band
that reaches past the next joint smears that joint too. One to two rings either side is the useful
range.

Weights are normalised to sum to 1 (error ~1e-16) and capped at 4 influences per vertex, the GPU
skinning limit.
