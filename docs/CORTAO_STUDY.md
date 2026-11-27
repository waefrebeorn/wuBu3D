# What we took from CORTAO

Read 2026-11-26. `theagentd/CORTAO` (MIT, Daniel Isheden / Fenris Creations, 371★) is Circular
Occluder Ray-Traced Ambient Occlusion: a physically based screen-space AO that replaces the
horizon-based family (GTAO). It was built for `EVE Frontier`, where players reshape the world,
so nothing can be baked.

**No code was copied.** What follows is what we learned, what we built, and what we measured.

## Why it matters here

Our raster composite already ran a screen-space AO, but it was a crude one: twelve fixed taps
in pixel space, comparing depths, with no normals and no world-space radius. That is not AO, it
is a depth-difference blur — it never darkens contact points, and it changes with resolution.

CORTAO's insight is that you do not need a horizon: sample the depth buffer, keep the samples
inside the occlusion radius, turn each into a **circular occluder**, and trace rays against that
proxy geometry instead of against the full scene. Their lookup table makes up to 32 rays cheap
enough for a GPU frame.

## What shipped

`"ao": "ssao"` in a spec switches the composite from the fixed taps to a screen-space raytraced
AO: rays in a normal-oriented hemisphere, projected back into the depth buffer and compared,
radius in metres (`ao_radius`, default 0.35, `ao_rays`, default 10). It is **opt-in**, not the
default, because of the cost below.

The raster now also publishes the camera it used (`cam_####.bin`: eye, right/up/forward basis,
focal length) next to the depth and normal buffers. Any screen-space effect needs it, and depth
alone cannot unproject to world space.

Measured on this box, 144 frames at 320×180 (SSAA 2):

| composite pass | time | per frame |
|---|---|---|
| fixed taps (default) | 5.7 s | 40 ms |
| screen-space raytraced (`"ao": "ssao"`) | 59.9 s | 416 ms |

A single `still --at N` costs 1.9 s → 3.0 s with the new AO, which is the right way to use it:
look-dev and hero frames, not the whole film.

## Three things the port taught us

**1. Normals are geometric, not view-oriented.** The raster computes normals from triangle
winding. Any AO built on them must flip by `dot(N, view)` first, or the ground — whose winding
faces down — occludes everything: the first AO map came out solid black on the ground and white
on the sky. That single line is the difference between "AO is broken" and "AO works".

**2. A solid-angle port of CORTAO's occluder model is not CORTAO.** Summing the solid angles of
eight circular occluders (their geometry, without their lookup table) produced faint
self-occlusion on vertical faces and almost no contact darkening on the ground: with 8–24
samples spread over a metre, most rays miss the thin geometry between them. Their table and mip
sampling exist precisely to make that affordable; strip them and the model degrades into a worse
GTAO. The screen-space ray march kept the shape and gave real contact darkening.

**3. It needs the filter pass.** CORTAO is a multi-pass technique: prepass, main pass, filter.
Without their spatial/temporal filter our raytraced AO is grainy at 10 rays, and grain is worse
than no AO. That filter is the next piece of work, and it is the reason this ships opt-in.

## What we did not take

* The occluder lookup tables and their generators — they assume GPU texture sampling; on the CPU
  the ray march is simpler and, at our resolution, faster to write.
* Bent normals — worth having for rim light direction, but only after the filter exists.
* Their Carbon Engine depth-range specialisation (16-bit packed depth for vast space scenes).
  Our depth is already linear in metres.


## The filter pass, finally built

CORTAO runs prepass → trace → filter. We had prepass → trace and stopped, and the missing
stage is why SSAO shipped opt-in: 10 rays looked grainy and 4 looked like noise. `_ao_filter`
is a bilateral pass over the AO buffer, weighted by depth difference in metres and by the dot
product of neighbouring normals, over two rings of eight taps. Silhouettes keep their edge
because a jump in depth or facing kills the weight; flat walls smooth out.

Measured on `specs/assets_ssao.json` at 320×180 (a still, wall clock, same machine load):

| rays | filter | still time |
|---|---|---|
| 10 | no  | 3.30 s |
| 4  | no  | 2.46 s |
| 4  | yes | 2.56 s |
| 2  | yes | 2.29 s |

So the filter buys back the ray count: 2 rays + filter is 31% faster than 10 rays alone and
reads cleaner than 4 unfiltered. The default stays 10 rays for hero frames; the preview path
can now afford `"ao": "ssao", "ao_rays": 2` at all.

## The rule this leaves behind

Every screen-space effect needs three things from the rasteriser: linear depth, world normals
that face the viewer, and the camera. We now publish all three per frame; the next effect (wet
ground, lantern occlusion, reflections) starts from the same three files.
