# What we took from SH4DER-PVR

Read 2026-11-26. Local checkout kept at `/opt/data/work/refs/SH4DER-PVR` (the wiki is the useful
part: `wiki/shadows/thesis.md`, `wiki/effects/psm.md`, `wiki/methods/sh4zam-rule.md`).
`JiltedValkyrie/SH4DER-PVR` (MIT) is a bespoke graphics library for the Sega
Dreamcast: a fixed-function PowerVR2 driven by a 200 MHz SH-4 with 16 MB of RAM. It is the
closest published thing to our problem — a fixed-function rasteriser, hand-written maths, no
GPU driver to hide behind — so it is worth reading for the shape of the pipeline even though
none of its code runs here.

**No code was copied.** What follows is the architecture, reimplemented in C11 against this
project's own `WB3D` stream.

## The three ideas that changed our renderer

### 1. A shadow map is a depth map plus one compare (their `psm`, route B)

Their shadow layer offers two routes: the PVR draws a render target, or **the CPU rasterises
casters as 16-bit depth into RAM and compares per receiver** with 2×2 PCF. Route B is the one
that fits us, because we already own a CPU rasteriser.

What we built (`wuburaster.c`, `build_shadowmap` / `shadow_vis`):

* one 512² float depth map per frame, built from the opaque triangles **already in the frame
  stream** — the wire format did not change, which is what made this cheap to adopt;
* an orthographic light basis along the fixed key direction the vertex shader already uses,
  fitted to the bounds of everything above z = 0.2 m (the ground is the receiver, not a caster);
* per-pixel 2×2 PCF with a 0.16 m world-space bias.

Measured on this box (4 cores, no GPU), 144 frames at 320×180 with SSAA 2:

| | ms/frame |
|---|---|
| raster path before shadows | 6.31 |
| raster path with shadows | 6.96 |
| of which: building the map (`clock_gettime`, internal) | 0.38 |
| per-pixel lookups (difference) | ~0.27 |

**Two bugs the port exposed, both of which were already in our renderer:**

* our depth ordering was inverted for a fixed-function light: depth along "toward the light"
  *grows* toward the light, so the map must keep the **maximum**, not the minimum. With the
  min, the character shadowed itself completely and cast nothing;
* the ground plane was **never drawn at all** in the raster path. It was one quad with two
  vertices behind the camera; after near-plane clipping its screen coordinates were in the
  millions and float barycentrics lost the precision, so every pixel was rejected. A 48×48
  grid over ±200 m fixed it. Every raster preview before this had figures standing on the
  background gradient — see `docs/FEATURES.md`.

### 2. Bake what does not move; treat movers as proxies (their shadow thesis)

`wiki/shadows/thesis.md` argues for one byte of sun visibility per static vertex, baked once,
with moving things handled as spheres, capsules and boxes checked only on nearby receivers.
Their measured proxy pass for 8 people and 4 hens was 312 µs — under their 2 ms slice.

We are not there yet: our static geometry is small enough that one map per frame is cheaper
than the bake bookkeeping. But the rule is recorded here because it is the right shape the
moment scenes get bigger than one film: **static bakes, movers proxy, and never re-cast the sun
every frame for geometry that has not moved.**

### 3. Depth readback is the depth test (their "depth fade")

Their discovery: on a fixed-function GPU the bump-map unit can read a depth texture back, so a
glow or headlight can fade where it meets a wall instead of slicing through it. The transferable
part is the pattern, not the mechanism — **a depth pass is not only for hidden-surface removal;
it is the input to every effect that needs to know what is in front.**

We already run a depth pass for the raster composite (AO, rim, haze). The next effect that
should use it is the lantern: it currently ignores occlusion and bleeds through the coat.

## Two optimisations we tried and measured, one of which lost

**Vertex reuse (kept).** A closed mesh shares each vertex between ~6 triangles; the old
inner loop transformed and shaded every vertex once per face. One pass per vertex per frame
(Jet calls it position reuse) is byte-identical output and ~6% off the frame at 2,534 tris —
and it is simply less work to read.

**Edge stepping (kept).** Edge functions are linear in x and y, so the per-pixel fill now
steps two accumulators instead of recomputing both barycentrics from scratch: ~7–9% off the
frame at 2,534 tris (19.4 → 18.4 ms/frame), output identical except for ~50 silhouette pixels
where float drift flips a depth test.

**Depth buckets (rejected for now).** Jet sorts opaque draws front to back so the z-test rejects
far geometry before it shades. Implemented as a counting sort over 64 buckets, it measured
*slower* (19.4 → 24.2 ms/frame on the same scene): our occlusion culling already removes the
hidden triangles, so the sort is pure overhead. It stays behind `--sort` for scenes with heavy
overdraw, off by default.

**A fog LUT (rejected).** SH4ZAM's "no libm in a hot loop" suggested replacing the per-fragment
`expf(-z/fog)` with a 1024-entry table plus a lerp. Measured on this box, min of 7 interleaved
runs: **5.49 s with `expf`, 7.07 s with the table** — 29% slower. glibc's `expf` is fast, the
table added a dependent load and a branch, and the result was reverted. The rule is right on an
SH-4 with no FPU; on x86 it is not automatically right, which is exactly why the ledger marks
things MEASURED instead of DERIVED.

**What the numbers say about where the time goes.** The raster is **fill-bound, not
vertex-bound**: 2,534 triangles or 7,140 triangles, the per-frame cost tracks covered pixels
far more than vertex count. So the next real win is Jet's span filling (walk each scanline once,
step the attributes incrementally, instead of recomputing three edge functions and two divides
per pixel), not more vertex maths.

## Math and speed rules worth stealing (their SH4ZAM rule)

* **One transform per vertex, none per pixel.** Our fragment loop already interpolates
  reciprocals; nothing in the inner loop divides except by an interpolated `izp`.
* **No libm in a hot loop.** `expf` is still called per fragment for fog. That is the largest
  remaining per-pixel cost and the next optimisation: a 256-entry fog LUT indexed by depth,
  the same trick their `PSM` texel lookup uses.
* **Measure per stage, not per run.** Their ledgers separate SH-4 ms from PVR ms so a
  regression lands on one stage. Our receipt does the same (`timings_s` per stage, plus
  `scene.tris_per_frame`).

## What we deliberately did not take

* **The PVR render-target route (route A)** and the DMA readback stub — no equivalent here,
  and the stub is one frame late on purpose.
* **Perspective shadow maps** (their `psm.h` post-projective fit). Uniform orthographic is
  enough at 854×480 with our depth ranges; PSM helps when the near ground needs texels, and
  that is a change to make when a shot demands it, with a before/after pair.
* **Their `blade`, `bolt`, `ocean` effect catalogue** — those are Dreamcast-specific draws
  (additive untextured tubes, PVR punch-through). The *effect* language is useful to read; the
  implementations are not portable to a float framebuffer.
* **SH4ZAM itself.** It is Falco Girgis's MIT library of SH-4 assembly (`fipr`, `ftrv`,
  `fsrra`, `fsca`). There is no SH-4 here. What transfers is the discipline: fewer divides,
  vectors before scalars, one transform per vertex.

## Where their numbers are honest and ours are not yet

Their ledger marks every line MEASURED, DERIVED, ESTIMATE or OPEN, and marks predictions that
their own benches overturned. Our receipt does the same for run times and triangle counts but
not yet for image quality; `qa` is a liveness gate (lit, moving, no dead frames), not a quality
score. That is the next gap: a quality number that can be quoted next to a frame.
