# Rasteriser performance: what measured, what didn't

Every number here is `ms/frame` printed by `wuburaster` from `clock_gettime` around the frame
loop, 144 frames at 320×180 with SSAA 2, 7,140 triangles. Wall clock on this box swings 3× with
other load, so the internal per-frame number is the only figure worth trusting; wall-clock minima
are quoted only where the effect is bigger than the noise.

## Kept

**Edge-function stepping (Pineda, and Jet's span walker).** The fill loop evaluated two edge
functions per pixel — six products, four subtractions — then divided. Both are linear in x and y,
so each row starts at a corner value and advances by one add per pixel: three adds instead of
ten arithmetic ops. **20.2 → 17.3 ms/frame (~14%)**, output identical to within 0.02% of pixels
(silhouette edges, where a one-ulp difference flips a depth test — measured against the previous
binary on three specs, max 257 px of 921,600).

The literature agrees on the shape of this: Owens' Stanford thesis measured a scanline rasteriser
at 83–93% of the time of a barycentric one for large triangles, while barycentric wins for
triangles of 2–3 pixels. Our scenes are dominated by a few thousand mid-to-large triangles, so
row stepping is the right side of that trade.

**Shadow lookups only where there is sun.** A fragment whose interpolated key term is ~0 was still
doing four depth taps. Multiplying by zero costs less than sampling: skip below 0.35 of summed key
contribution. Small, free, no visual change (those fragments are ambient-only by definition).

## Tried and reverted

**Fog LUT instead of `expf`.** A 1024-entry table with a lerp was **29% slower** than glibc's
`expf` (5.49 s → 7.07 s, min of 7 interleaved runs). The SH4ZAM rule ("no libm in a hot loop") is
right on an SH-4 with no FPU, and wrong here.

**Opaque front-to-back depth buckets (Jet's `DepthBuckets`).** A counting sort over 64 buckets per
frame, near shells first so the z-test rejects far ones before they shade. It costs two extra
passes over 7,000 triangles per frame, and our software occlusion culling already removes most of
what it would save: **19.4 → 24.2 ms/frame**, 25% slower. Kept behind `--sort` for scenes where
overdraw is the dominant cost (a deep city of overlapping towers), off by default.

**Vertex reuse (kept, but not for the reason expected).** One transform per vertex instead of one
per face: byte-identical output, ~6% of the frame. It is the right code, but it proves the point
below.

## The shape of the cost

The raster is **fill-bound**: 2,534 triangles and 7,140 triangles cost about the same per frame at
the same pixel coverage, and vertex-level optimisations buy single-digit percentages. So the next
real win is not in the vertex stage or the ordering; it is in the inner loop — fewer operations per
covered pixel, or fewer covered pixels. That means span filling with per-span constant shading
(Jet's `fillRGB565Span` with `TiledSpan`), or dropping SSAA in favour of a cheap post-resolve.
