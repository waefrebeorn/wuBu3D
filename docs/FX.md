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

## What is still missing, and what it would take

| gap | why it is still open |
|---|---|
| hair / fur | shells or cards need per-strand geometry; 31 products sell groom tools |
| cloth / soft body | a verlet solver with distance and bend constraints — a weekend, not a paragraph |
| normal mapping | needs a tangent basis per face in `shade.c`; the sampler exists |
| retargeting | the joint names are ours only; a rest-pose offset table would close it |
| EXR / ProRes | ffmpeg can do both; the missing piece is a data pass (depth, normal) to put in the EXR |
| navmesh | A\* on a grid is easy; the mesh bake is the work |
