# What we took from the two repos — and what we didn't

Read 2026-11-25. Both are C++17, both MIT. **No code was copied**; the value was the architecture, and the implementation below is C11 written against WuBu3D's own scene format.

## CubeCoders/Jet — a fixed-function 3D rasteriser for ESP32

**What it is:** a tiny, dependency-free, fixed-function software rasteriser (567★, 7.9 MB, C++17). Camera, lights, materials, span blending, depth buckets, environment mapping, lens flare, OBJ loader.

**What we took:** the shape of the pipeline, not the source.
- A rasteriser is enough for a preview: transform → project → triangle fill with a z-buffer → shade → write a frame. No ray tracing, no sampling, no denoiser.
- Fixed-function means "no shader graph, no textures required" — a flat shade plus fog reads as a scene at preview scale.
- The output is just a framebuffer; writing PPM per frame keeps the whole path free of image libraries.

**What we didn't take:** their C++ class design (Camera/Light/Material/Object hierarchies), span blending, environment mapping, lens flare. None of that buys a preview.

**Result in our code:** `wuburaster.c` — ~250 lines of C11, no dependencies, `WB3D` binary scene stream in, PPM frames out. 698 triangles, **0.57 ms/frame at 320×180**.

## Dante-Leoncini/Whisk3D-Editor — a Blender clone aimed at a 2007 Nokia

**What it is:** a 100% free Blender-alike (317★, 467 MB, C++17) targeting an ARM11 at 332 MHz with 64 MB RAM: modelling, armatures, painting, ray tracing on Vulkan/CPU, Lua scripting, game export.

**What we took:** the constraint, and the documentation habit.
- *"El hardware no debería morir por el software"* — the retro-first rule. Every design choice is measured against running on hardware nobody else supports. That is the same discipline our CPU-only, no-GPU pipeline needs.
- Low-poly as a target, not a compromise: flat shading, few triangles, no textures. A 698-triangle scene is not a downgrade from a path trace for a *preview*; it's the correct abstraction.
- Their `docs/decisiones.md` is a rulebook, not a diary: each decision is one paragraph, with the mechanical rules a future contributor must follow. Our `references/short-film-pipeline.md` now follows that pattern.

**What we didn't take:** the editor. A scene editor with undo stacks, gizmos and mesh editing is a different product. WuBu3D's interface is the spec file; adding a GUI is a separate build.

**One idea borrowed conceptually:** their undo rule about index-based destinations — *"if a list has index targets, every operation that shifts its indices must snapshot the list or announce the shift"* — is the same failure mode we hit twice in this session (stale `SRC` constant, stale frame directory). The general form: **an action that recomputes state must announce it or take a snapshot.** Noted for when WuBu3D grows incremental rebuilds.

## The resulting split

| path | renderer | cost/frame @320×180 | use |
|---|---|---|---|
| `render` | Blender Cycles CPU | 3.45 s | delivery |
| `raster` | our C11 rasteriser | **0.57 ms** | blocking, timing, camera checks, cartoon look-dev |

Same spec, same grade, same score, same mux. Only the geometry-producing renderer changes, so a preview is not a different film — it is the same film with the shading simplified.
