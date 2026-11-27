# Materials: why everything used to look like clay

Three separate bugs produced the same complaint — a scene painted in one colour, lit like
plasticine. Each was in a different layer, and fixing one alone changed nothing visible.

## 1. The OBJ loader threw materials away

`load_obj` read `v` and `f` and skipped `usemtl` and `mtllib` on purpose ("the raster path
shades flat per vertex"). Kenney's dungeon kit is built the other way round: a handful of
materials (`grey`, `grey-light`, `default`) carry the entire look, and a placement colour is
just a tint. Dropping them meant a room of white plaster.

The loader now reads `usemtl`, resolves the companion `.mtl` (`Kd`, `map_Kd`), keeps `vt`, and
returns three corner colours per face — sampled from the atlas when the material has one,
otherwise the material's flat colour. A catch-all white material (`default`, `Material`,
`None`) is treated as *no material*, so the placement colour shows through instead of white.

## 2. glTF atlases were never sampled

A GLB primitive has `TEXCOORD_0` and a `baseColorTexture`; we read neither, so every character
came out in its `baseColorFactor` — usually white. The reader now decodes the atlas image out
of the buffer (PIL), keeps the UVs per primitive, and bilinear-samples per vertex in the pose.
glTF UVs are top-left origin: flipping v (the OBJ convention) puts a character's shoes on its
head.

Per-vertex, not per-pixel, because the wire format carries colour per vertex and the meshes are
already dense enough (≈1.1 k verts per Kenney character). A per-pixel texture fetch would need
UVs in the vertex record and a sampler in the rasteriser — a real feature, deliberately not
this one.

## 3. Lighting added light instead of scaling reflectance

In `wuburaster.c` the ambient term was `albedo·s + (26, 14, 7)·ndf` — an additive warm
constant — and the lamp did the same again per pixel (`+ attr·255·(0.55, 0.34, 0.16)`). Adding
a fixed colour on top of albedo destroys saturation: a blue wall, a green orc and a white floor
all converge on the same beige. Both terms now multiply:

```c
vc[i].sh[k] = albedo * (s + 0.10f*ndf);      /* ambient scales reflectance */
base[k]   *= (1.0f + attr*2.0f);             /* the lamp scales it too   */
```

The key light also falls off with distance from the lamp (`1/(1+d²·0.0022)`); without it every
surface in a 12 m room received identical light, so a room had no gradient and therefore no
depth, however correct its albedo.

## 4. The grade was desaturating on purpose

`night` defaulted to 0.75, and the Purkinje block pulls 22 % of the colour toward grey at full
strength — 16 % by default. Bloom added 0.30 of a blurred bright pass, the composite added a
warm rim at 0.12, and exposure defaulted to 1.55. Together that is a wash. Now:

| knob | before | after |
|---|---|---|
| `night` | 0.75 | 0.30 |
| `saturation` | (none) | 1.12 |
| `bloom` | 0.30 | 0.18 |
| `exposure` default | 1.55 | 1.05 |
| composite rim (additive) | 0.12 | 0.035, and it scales |

## Checking it instead of eyeballing it

Saturation is measurable: median HSV saturation over the graded frame. The character probe
(`specs/glb_probe.json`) went **0.39 → 0.49** while mean luma stayed ~0.28, which is the
signature of adding colour rather than adding brightness.

```
python3 - <<'EOF'
import numpy as np; from PIL import Image
a = np.asarray(Image.open('out/glb_probe/graded/f_0006.png').convert('RGB'), np.float32)/255
mx, mn = a.max(2), a.min(2)
print('mean', a.mean().round(3), 'sat', np.median(np.where(mx>0.01,(mx-mn)/np.maximum(mx,1e-6),0)).round(3))
EOF
```
