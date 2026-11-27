# Rasterising in C11

`src/wubuzbuf.c` is the renderer's hot loop: a z-buffered triangle raster plus depth-tested
cylindrical decals. `wubu3d_z.py` binds it; `raster.py` stays as the reference it is diffed against.

Two loops that matter, and one that does not:

- the **triangle** loop computes barycentrics and the reciprocal-depth test per pixel of its
  bounding box
- the **decals** loop unprojects every covered pixel and samples the texture by angle around the
  body axis, alpha-tested
- clearing is not the bottleneck: splitting `wb_clear` into two loops and building at `-O3` moved a
  1080p frame from 46.2 ms to 44.6 ms, i.e. noise. The pixels are, on average, written once and
  tested several times.

## Correctness first

The C path must be the same render, not a similar one. Measured against `raster.py` on a real
character (peanut, 1,264 triangles, 440x560):

```
painted pixels      py 126754   C 126754   overlap 126754
colour agreement    on overlap 100.00%
depth difference    max 2.38e-07
```

One trap worth recording: the two buffers use different "empty" sentinels (`np.inf` vs `1e30f`), so
`np.isfinite(zbuf)` is true for the whole C buffer and a comparison test written that way reports a
46% mismatch that does not exist. Compare with `zbuf < 1e29`.

## Speed

| | 1080x1920, 1116 triangles |
| --- | --- |
| Python (numpy per triangle) | 271 ms |
| C11 | **44.6 ms** |

**6x**, which for the 912-frame film is 247 s down to 40.6 s of raster time.
