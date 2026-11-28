# Making it fast: where the time actually went

Measured before changing anything, which is the only way this works. `bench.py`:

    25 boxes    300 tris:  20.8 ms    69.4 us per triangle
    100 boxes  1200 tris:  66.0 ms    55.0 us per triangle
    400 boxes  4800 tris: 229.3 ms    47.8 us per triangle
    bare shade_tri call:    8.9 us per triangle (200x200 px)

Eight point nine microseconds is the rasteriser doing real work. At 47.8 us per triangle in a scene,
**82 % of the frame was never in C at all** — it was Python projecting each quad, allocating a 3x11
float block, and making two ctypes calls per triangle.

## The fix: one call, one numpy pass

`wubu_shade_batch` takes a pre-packed vertex array and loops in C. Python builds that array with
vectorised numpy (one gather, one concatenate) instead of per-triangle allocation.

    4800 triangles    229.3 ms -> 75.9 ms   3.24x
    + backface cull                 56.8 ms   4.32x
    420x700 ss2 frame                82 ms

Backface culling is opt-in (`wubu_cull`), because a single-sided card must still draw when seen from
behind. On a closed box half the triangles face away and are pure waste.

## The three bugs the batch pass exposed

**1. A placeholder normal was lighting every character.** `r15.build` stores `(0,0,1)` on faces it
never measured, and the old path used it verbatim — so the whole cast has been lit by one global
normal since the first frame. That is why characters read flat next to the props, which do carry real
normals. The batch derives the normal from the quad and orients it toward the eye, and only trusts a
stored normal that is not the placeholder.

**2. Triangle layout is `[all tri-A][all tri-B]`.** Per-quad data must be `np.concatenate`, not
`np.repeat`. `repeat` gives `[n0,n0,n1,n1,...]`, pairing every triangle with its neighbour's normal
and colour — which renders the character as a patchwork of inconsistent triangles. The tell was a
diagonal seam across the chest.

**3. Vertex proliferation is not free.** The first version indexed each face's `q` and `c` separately
per triangle; building the block in one pass per attribute cut the Python half of the frame to a
rounding error.

## Parity

The batch path is not a different renderer. On the character test:

    diff mean 0.13 levels, 0 pixels over 10

The remaining 0.13 is antialiasing ties on shared edges.

## What is still slow

- **Per-pixel shading with N point lights.** The inner loop does a sqrt and a pow per light; a
  lookup-table or half-vector precompute would cut it, but it is already ~9 us per large triangle.
- **Supersampling.** 2x SSAA is 4x the pixels by definition. `ss=1` with a good tonemap is the
  cheaper trade once bloom and rays are in.
- **Scatter and cloth** are Python-order loops over instances; both would benefit from the same
  treatment as the renderer, a batch call with the loop in C.
