# Gap matrix — 25 facets

A sweep across every facet of making a short cartoon, checked against what the box actually has.
"Have" means working code with a measured number behind it.

| # | facet | state |
| --- | --- | --- |
| 1 | camera language / shot sizes | **closed** — WS/MS/MCU/CU/ECU distances from subject height |
| 2 | staging, rule of thirds | **closed** — `craft.thirds()` + caption safe areas |
| 3 | character silhouette | partial — critic scores fill/solidity/appeal |
| 4 | squash & stretch, timing charts | open |
| 5 | lip sync visemes | **closed** — 6 shapes, 12 changes/sec |
| 6 | sound stings | open (tones only, no sting library) |
| 7 | comedy music cue / hit punctuation | open |
| 8 | edit rhythm, cut rate | partial — timing.py generates the shot table |
| 9 | hook in first seconds | open — no explicit hook beat |
| 10 | thumbnail / CTR | open |
| 11 | caption typography, safe area | **closed** — hard captions with reveal timing |
| 12 | colour script per beat | open — palettes locked per character, not per scene |
| 13 | stylised lighting | partial — 5-step ramp |
| 14 | cheap AO (screen space) | **failed** — see below |
| 15 | soft shadows | open |
| 16 | cloth | open |
| 17 | hair cards | open |
| 18 | particles (dust/smoke) | partial — 2D in sets.py |
| 19 | crowd | partial — 2D instancing |
| 20 | LOD | **closed** — QEM, 6724 -> 1678 tris in 4 ms |
| 21 | texture atlas | n/a — flat colour shading |
| 22 | auto UV unwrap | n/a |
| 23 | normal baking | n/a |
| 24 | vertical export codec | **closed** — 1080x1920 h264 |
| 25 | audio ducking / mix | open |

## Two failures worth recording

**Screen-space AO does not fire on flat-shaded box rooms.** SSAO looks for a *depth jump* between
neighbouring pixels. A wall meeting a floor at 90 degrees is depth CONTINUOUS — the gradient changes,
the value does not jump — so a neighbour-difference test finds nothing: measured mean brightness
1.000, i.e. no darkening at all.

**Ray-baked AO self-occluded.** Casting hemisphere rays from each face centroid returned full
occlusion on every face (mean 1.00). The rays were travelling into the geometry rather than away from
it: hemisphere orientation from face winding is not reliable on box meshes where faces are generated
per side. A correct bake needs the surface normal to be resolved against the owning volume first.

Neither is in the pipeline. Both are cheap to finish and both are cosmetic next to the open gaps
below.

## What the sweep says to build next

Ordered by what a finished short needs and what we have least of:

1. **Sound**: stings (whoosh, pop, thud), a ducking mix under the voice, hit punctuation on the cuts
2. **Squash & stretch** on contact frames — the single biggest "this moves like animation" lever
3. **Hook beat** in the shot planner, and a thumbnail frame chosen by contrast rather than by time
4. **Colour script** per beat, so the palette shifts with the story instead of staying per character
