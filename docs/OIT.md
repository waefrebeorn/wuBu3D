# Weighted blended OIT in wuburaster

Slermed from the technique described by McGuire & Bavoil, as demonstrated in Lele Feng's
`candycat1992/OIT_Lab` (Unity/URP). The code here is ours — C11, no dependencies, against the
WB3D stream — but the method is theirs and this note is the attribution.

## The problem it solves

Alpha blending is only correct back-to-front. Engines sort transparent objects by centre, which
works for separate things in a row and fails when objects cross, share a centre, or live inside
one mesh (triangles draw in index order). The visible symptom is a pane pasted on top, or colours
that pop when the camera moves.

## The method

Stop sorting. Two auxiliary targets, both order-independent:

| target | clear | blend | per fragment |
|---|---|---|---|
| accumulation (RGBA float) | 0 | add | `+= (colour · a · w, a · w)` |
| revealage (R float) | 1 | multiply | `*= (1 - a)` |

Resolve once per frame:

```
avg = accum.rgb / max(accum.a, 1e-4)
out = avg · (1 - revealage) + background · revealage
```

The weight biases nearer, more opaque fragments so a front pane still reads stronger:

```
w = a · clamp(10 / (1e-5 + (z/5)² + (z/200)⁶), 0.01, 3000)
```

Addition and multiplication commute, so there is nothing to sort. Glass is depth-tested against
the opaque pass but never writes depth.

## What is implemented here

In `wuburaster.c`:

* **Vertex format grew to 20 bytes** — `f32 x,y,z` + `u8 r,g,b,a` + `u8 tag, pad×3`. `a = 255`
  means opaque; anything lower goes through the transparency path.
* **Two passes over one triangle list** — opaque first (writes colour, depth, normals, subject
  box), then glass (tests depth, accumulates). Order inside a pass is irrelevant.
* **`--no-oit` flag** reproduces the failure mode: glass drawn in index order with plain alpha
  blending, for side-by-side evidence.
* Weight, accumulation, revealage and the resolve pass are as above. Fog is applied per glass
  fragment before accumulation so distance still reads.

In `wubu3d.py`:

* `props.glass` in the spec — panes with `at`, `size`, `yaw`, `pitch`, `color`, `alpha`, built as
  quads. The demo puts four of them on one centre, which is exactly the case per-object sorting
  cannot resolve.
* Vertex packing is now `<3f4B4B`, and the character tag rides in the byte after alpha.

## Measured

`specs/demo_oit.json` — 4 panes at 38% alpha sharing one centre, 2 118 tris/frame of which 192 are
glass, 24 frames at 854×480:

| mode | per frame |
|---|---|
| weighted blended OIT | **22.5 ms** |
| index order + alpha blend (`--no-oit`) | 34.5 ms |

The OIT path is not slower here: it writes one accumulated value per fragment instead of reading
and writing the framebuffer per overlapping pane.

Visual check (`chk_oit.png`): the same geometry produces two different composites. Under OIT the
overlap keeps distinct red/green/blue tints from all four panes; under index order the last-drawn
pane dominates and the overlap goes muddy yellow.

## Trade-offs, stated honestly

1. **It is an approximation.** Layers inside one pixel are averaged, not ordered, so a very strong
   front layer reads weaker than true back-to-front blending would give.
2. **The weights are tuned to a depth range.** Outside roughly 5–200 m the bias stops being
   meaningful; nearer or farther layers can dominate the wrong way.
3. **Cost:** two extra float targets (5 floats/pixel here — at 854×480 that is 8.2 MB) and one
   full-screen resolve.
4. **Exact answers need depth peeling or per-pixel lists**, with a layer limit or extra memory.

## When to reach for it

Glass, foliage cards, particles, holograms — anywhere many overlapping transparent surfaces make
per-object sorting fail. Not needed for a single transparent quad in front of a wall.
