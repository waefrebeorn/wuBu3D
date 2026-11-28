# The gaps that got filled, with the numbers

Three C modules, each closing a row of `ENGINE_GAPS.md`. Every claim below is a print from
`demo_fx.py`; the contact sheet is three panels of the same shot with one system added at a time.

## `shadow.c` — cast shadows

Every engine has cascaded shadow maps. We had a grey ellipse under the feet, which fakes contact
but does not occlude light: a wall could not shade a floor.

The pass is cheap because the rasteriser already exists — render depth from the light, then ask the
map a question per pixel. `wubu_shadow_floor` does the whole frame in one loop: intersect the ground
plane, transform the hit into light space, 2x2 PCF tap. As one C call it is a fraction of a second;
as a per-pixel Python call it was two minutes.

    shadow: 6.5% of floor pixels occluded, mean floor factor 0.94

Two bugs on the way, both instructive:

- **An empty map reads as fully lit.** The light's 60-degree cone at five units did not contain the
  set, so every triangle projected outside the map and every pixel tested "not occluded". A shadow
  system that fails open looks identical to no shadow system.
- **The view matrix had the forward axis negated.** `z = f.(eye - p)` is negative for points in
  front of the light, so every vertex was rejected before rasterisation. The map was empty from the
  first frame; nothing warned, because empty is a legal state.

## `particles.c` — the largest census gap

51 Gumroad products sell VFX systems and every engine ships one. Ours is two loops:

    wubu_psys_step   gravity, drag, wind, turbulent jitter, lifetime, in place
    wubu_splat       additive soft discs with a depth test

    particles: 675 alive, 675 splatted, 93772 blended pixels

The split is deliberate: integration is cheap arithmetic that Python could do, and splatting is
memory traffic that it cannot. 20k sprites at 120 px each is 2.4M blended pixels per frame.

## `fx.c` — colour management

Blender 5 ships ACES 1.3/2.0 views and a wide-gamut pipeline. We were writing sRGB bytes straight
out of the rasteriser, so every value above white was clamped flat. The stack is now

    bytes -> linear (sRGB EOTF) -> bloom -> god rays -> ACES tonemap -> sRGB encode

    post: clipped pixels 0.366% -> 0.000% (ACES shoulder), mean luma 62.2 -> 74.6

The point is not that the frame got brighter; it is that the 0.366 % of pixels that were hard white
now carry a gradient, because the shoulder is a curve instead of a clamp.

## Round two: cloth, navmesh, fur shells, retargeting

    cloth:    384 particles, 728 constraints, mean stretch 4.483% of rest, 120 steps at 1/60
    navmesh:  116 -> 48 points after string-pull, path 131.5 vs straight 116.0 (ratio 1.13),
              2367 of 7560 free cells expanded
    fur:      49 head faces -> 49 / 196 / 392 faces at 1, 4 and 8 shells
    retarget: 5 joints mapped, round trip 5.55e-17 body units; ignoring the foreign bind costs 0.0427

**`cloth.c`** — verlet with distance constraints, 6 iterations, damping 0.994, wind jitter. Stretch is
the metric because it is the one thing a position-based solver can get visibly wrong: a cape at 40 %
stretch is a net. 4.5 % holds its shape through a fall and a floor collision.

**`navmesh.c`** — A\* on a cost field (not a bitmap: 0 blocked, 255 free, in between = expensive
ground), 8-connected with corner-cut rejection, inflated by an agent radius, then string-pulled.
**The smoother was wrong first**: it kept the waypoint that *failed* the line test, which invented
shortcuts through walls, and the tell was a path shorter than the straight line — 89.4 against 116.0,
a physical impossibility. Keeping the farthest *reachable* point instead gives 1.13, which is what a
route through a gap should cost.

**fur shells** — offset copies of the head along the face normal, tapered. The first attempt offset
each vertex by the sign of its own coordinate, which just inflates the box; the panels looked
identical at 4 and 8 shells. With normals and a 10 % taper the rim steps. Honest limit: without
alpha-tested strand cards a shell stack reads as layered hair volume, not fur. That needs a stipple
pass, not more shells.

**`retarget.py`** — the name map is the easy half. The other half is the bind: a rotation is relative
to a rest pose, so a rig bound 7/-11/4 degrees off ours imports bent by exactly that. Two bugs came
out of testing it:

- **Euler order.** `r15` composes `MX @ MY @ MZ`; the retarget module composed `Rz @ Ry @ Rx`. Every
  angle it handed back was a different rotation than the one it decomposed — 0.074 body units.
- **Both directions conjugated the same way.** `to_foreign` and `retarget_pose` applied identical
  transforms, so they compounded the bind instead of cancelling it. The round trip has to be
  conjugation by `M` in one direction and `M^T` in the other.

## `shade.c` — normal mapping

14 products sell it and every engine has had it for twenty years; until now a surface could be only
as detailed as its triangles. The change is a tangent basis per triangle from the uv gradient, then a
tangent-space normal sampled through the same uv as the albedo:

    flat        detail energy 2.425, distinct 101
    normal map  detail energy 3.211, distinct 129   (1.3x on 50 triangles)

The picture is the argument: 28 rivets and 5 panel lines appear on a 5x5 quad wall. Two notes worth
keeping —

- **A frontal key makes normal maps invisible.** The perturbed normal only shows up through N.L, so
  the lights have to graze the surface. Half the "it does nothing" reports in the world are this.
- **Gradient percentiles are the wrong instrument.** p90 stayed at 1.0/255 while the rivets were
  plainly visible, because smooth-shaded bumps have small per-pixel gradients. Detail energy
  (|image - blur|) and distinct-value count measure the thing being added.

## Ledger

| gap | status | number |
|---|---|---|
| colour management | filled | clipped 0.366% -> 0.000%, ACES shoulder |
| particles | filled | 675 alive, 93,772 blended px |
| cast shadows | filled | 6.5% of floor occluded, factor 0.94 |
| motion blur | filled | 3 subframes accumulated |
| cloth | filled | 4.483% mean stretch, 384 particles |
| navmesh | filled | path 1.13x straight through a gap |
| normal mapping | filled | detail 2.425 -> 3.211, 101 -> 129 values |
| retargeting | filled | round trip 5.55e-17, bind ignored costs 0.0427 |
| fur | partial | shells give volume, not strands |
| navmesh bake | open | solver works on a grid; mesh -> grid is the remaining work |
| SSS / translucency | filled | wrapped terminator + tinted transmission: mean +5.1, max +27.7 levels, 30.1% of head pixels |
| EXR / ProRes | open | needs a data pass to put in the EXR |
| LOD | open | no mesh budget in the renderer |

## What is still missing, and what it would take

| gap | why it is still open |
|---|---|
| strand fur | shells give volume, not strands; needs alpha-tested cards and a stipple pass |
| normal mapping | needs a tangent basis per face in `shade.c`; the sampler exists |
| SSS / translucency | a wrapped-lambert term and a thickness pass; no material system to hang it on |
| EXR / ProRes | ffmpeg can do both; the missing piece is a data pass (depth, normal) to put in the EXR |
| LOD | decimation and a per-shot LOD bias; the renderer has no mesh budget |
| navmesh bake | the solver works on a grid; turning a mesh into that grid is the remaining work |
