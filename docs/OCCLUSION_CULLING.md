# Occlusion culling in wuburaster

Came from an asset-store promo for Unity's *Perfect Culling* — a precomputed occlusion system that
bakes visibility per camera cell. The product is not the lesson; the lesson is that most of a frame
is geometry nobody can see. This is the runtime, no-bake version, written in C11 against our own
stream.

## What it does

Two extra passes, both cheap:

1. **Coarse pass.** Every opaque triangle is rasterised once at 1/8 resolution into a buffer holding
   the *nearest* z per coarse pixel. Glass is skipped — it must never occlude.
2. **Region summary.** The coarse buffer is summarised into 32×32-coarse-pixel regions (256×256
   screen pixels), each storing the **farthest of those nearest values**. That number is the depth
   below which everything in the region is definitely behind something.

Then, in the expensive pass, for every triangle whose three vertices are in front of the near plane:

* project to screen, take its bounding box, map to a region range;
* take the **maximum** region value over that range;
* if the triangle's **nearest** vertex is farther than that maximum, the triangle is behind every
  occluder in every region it touches → skip it before clipping, shading and scan conversion.

The test is sound rather than heuristic: a triangle can only be hidden if something closer covers
its whole footprint, and the region maximum is the most conservative depth that satisfies that.

## Measured

854×480, 48 frames (24 for OIT), same binary, `--no-cull` for the control:

| scene | tris/frame | culled | cull | no cull | delta |
|---|---|---|---|---|---|
| walker + towers | 2 602 | 2 242 (86%) | 19.4 ms | 20.3 ms | **−4%** |
| four glass panes (OIT) | 2 118 | 288 (14%) | 26.2 ms | 25.7 ms | +2% |
| 400 towers + rocks | 7 702 | 6 652 (86%) | 31.9 ms | 47.9 ms | **−33%** |

Output is pixel-identical with and without culling (mean |diff| 0.000, max 0) on both scenes, which
is the check that the conservative bound is actually conservative.

## What the numbers say

The coarse pass costs roughly what rasterising four thousand tiny triangles costs. Below that, it is
a small loss; at 7.7k triangles it pays back a third of the frame. So the pass is **gated**: it only
runs when the frame has more than 4 000 triangles, which is why the small scenes above report zero
culls instead of a slower frame.

**The real limitation:** this is *triangle*-level culling. The industry version culls whole objects
before their vertices are ever transformed, because transforming vertices is usually the expensive
part. Ours still transforms every triangle to work out its depth, then saves only the rasterisation —
fine here because our rasterisation is the expensive half, wrong for a scene with millions of
vertices. Object-level culling needs object IDs in the stream and bounding volumes; that is the next
step, not this one.

## Flags

* `--no-cull` — draw everything, for the A/B.
* Culling is otherwise automatic above 4 000 triangles per frame.

## Files

* `wuburaster.c` — `build_coarse()`, the region grid, and the test in the draw loop.
* `tools/cull_bench.py` — the three-scene benchmark behind the table.
