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

## The core is C11; Python only drives it

Per-vertex work is the one place the language matters. `src/wubuskin.c` implements the bone
transform, linear blend skinning, dual quaternion skinning and bone-heat weights; `wubu3d_c11.py`
binds it with ctypes and rebuilds the shared object when the C source changes.

Measured on 200,000 vertices, two bones, one blend each:

| | time |
| --- | --- |
| C11 (`wb_lbs`) | **1.5 ms** |
| Python (`wubu3d_skin.deform`) | ~2400 ms |

**1595×**. The C results match the Python reference to 1.2e-07 (LBS), 3.6e-07 (DQS) and 1.1e-08
(bone matrices), so the fast path is the same maths, not an approximation of it.

## Dual quaternions, and why they replace LBS

Linear blend skinning averages the bone MATRICES. The average of two rotations is not a rotation,
so a vertex weighted 50/50 between them is pulled inside the surface. On a twist — a bone rolling
about its own axis — the limb collapses into a candy-wrapper pinch.

Dual quaternions carry rotation and translation as one unit that blends correctly: weighted sum,
renormalise, apply. Measured with a 50/50 blend against a 90° roll, point at radius 0.085:

| | radius | |
| --- | --- | --- |
| rest | 0.0850 | |
| LBS | 0.0601 | **71% — pinched** |
| DQS | 0.0850 | **100% — preserved** |

Note that `bone_matrix` derives its rotation from the bone's rest and posed DIRECTIONS, so it
cannot express a roll at all: the parentheses above needed matrices built by hand. Roll has to come
from the rig, not from the segment pair.

## Bone heat weights (Baran & Popović 2007)

Distance-based weights are a proximity proxy: a bone buried inside the torso and a bone lying on the
surface are treated the same if they are equally far. Heat weights diffuse over the MESH instead —
each bone seeds the vertices that clearly belong to it (less than 60% as far as any other bone), and
the weights relax along mesh edges until they settle.

```
heat: 416 raw verts -> 112 welded, 216 edges, weight-sum error 0.0e+00, max influences 2
bend 90: worst edge stretch  heat 1.69x   distance 1.64x
```

Seeding by radius alone (every vertex within a band) fixed every vertex and left the diffusion
nothing to solve, which silently produced hard 100/0 weights. The dominance rule is what leaves a
free region between the bones.

Sources in the tree: Baran & Popović, *Automatic Rigging and Animation of 3D Characters* (SIGGRAPH
2007); Kavan, Collins, O'Sullivan & Zara, *Dual Quaternions for Rigid Transformation Blending*
(TCD-CS-2006-46).
