# OBJ, and the ripped-model ecosystem

The Models Resource (vg-resource) is where game models and stages live, and OBJ + MTL is one of its
two preferred formats (DAE is the other). The wiki is explicit about the practical failure modes:

- OBJ carries **no rigging** — a submission with a rig has to bake it into meshes
- materials live in a sidecar **.mtl**; OBJ without MTL is rejected by the site
- the most common import failure is a **absolute texture path** in the MTL, which resolves only on
  the machine that exported it

`src/wubuobj.c` parses what real files contain, not the tutorial subset:

| feature | handled |
| --- | --- |
| `v` / `vn` / `vt` | yes |
| `f a b c d` polygons | fan-triangulated |
| `f a`, `a/b`, `a//c`, `a/b/c` | all four index forms |
| negative indices (`f -1 -2 -3`) | resolved relative to vertices seen so far |
| `usemtl` | counted, so materials can be split downstream |

Verified on a hand-built cube: 8 vertices, 5 triangles from 3 polygons (two quads and one triangle),
negative indices resolving to the right corners, 2 material statements counted.

## Legal, plainly

Models on that site are extracted from commercial games by fans. They are fine as study reference —
proportions, palettes, how a stage is built — but they are not ours to redistribute, so nothing from
it goes into this repo. The loader exists so a model can be examined locally; what gets committed
stays code and generated meshes.
