# Mesh and IK

Two more C11 cores, both driven from Python.

## wubumesh.c

| function | what it does |
| --- | --- |
| `wb_weld` | merge coincident vertices (hash grid). A quad soup arrives with four vertices per corner and no adjacency at all. |
| `wb_face_normals` | area-weighted; the cross product is left unnormalised because |axb| is twice the area, which is the weighting a smooth normal wants. |
| `wb_corner_normals` | one normal per face corner, splitting at a crease angle — Blender's shade-smooth-by-angle. |
| `wb_qem_simplify` | Garland & Heckbert quadric error decimation by edge collapse. |

Measured on an icosphere (radius 1):

```
weld     3840 soup vertices -> 642 unique (642 in the source mesh)
crease   cube corners align to their own face, max dot 1.000
         sphere corner normals follow the surface, mean dot 1.0000
QEM      5120 -> 1010 triangles in 3 ms
         surface error mean 0.0079, max 0.0188  (0.8% of the radius)
```

Two bugs worth keeping in the record. The first version scanned every face per candidate edge —
O(F·E), minutes on 5k triangles. The second built a face RING linking each face only under its
first vertex, so most vertices had an empty ring, every collapse read as `shared == 0`, and the
decimation stalled at 3804 triangles from 5120 while reporting success. Per-vertex face lists fixed
it; a flip test rejects any collapse that would turn a face inside out.

## wubuik.c

| function | what it does |
| --- | --- |
| `wb_ik_two_bone` | closed-form law of cosines. No iteration — the triangle is determined by the root, the target and the two lengths. |
| `wb_ik_fabrik` | Aristidou & Lasenby, *FABRIK* (Graphical Models 2011): forward and backward reaching passes over a chain. |

```
two-bone  end error 0.00e+00, |root-joint| 0.6200 (want 0.6200), |joint-end| 0.4400 (want 0.4400)
FABRIK    8 joints, converged in 29 iterations, end error 9.05e-04, bone lengths constant
```

A target outside the reachable ring is clamped onto it and the chain straightens, rather than the
solve failing: an IK call that returns a pose is more useful than one that returns an error.

## Why C11

The Python reference implementations stay in the tree as the thing the C is tested against. The C
is not an approximation of them — skinning matches to 1.2e-07 — it is the same maths at
engine speed, which is what 1,000 characters needs.
