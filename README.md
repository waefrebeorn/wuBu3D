# ~ WuBu ~

One human, four cores, no GPU. Films, and the pipeline that makes them.

**854×480 · 144 frames · 47.5 s raster · 4 cores · no GPU**

That is the whole claim, and every part of it is checkable from this repository.

## The films

| film | length | what it is |
|---|---|---|
| **THE LAMP** | 47 s | a lamplighter gives away his only light. Narrated, captioned, scored. `THE_LAMP.mp4` |
| **THE LIGHTKEEPER** | 90 s | 8 shots, 2,160 frames, Cycles CPU at 400×225 / 4 spp, denoised with a C11 filter written here |
| **FIRST LIGHT** | 40 s | 960 frames, 5 shots |

## What is in here

| file | what it does | measured |
|---|---|---|
| `wuburaster.c` | fixed-function C11 rasteriser: colour, depth and normal passes, near-plane clipping, weighted blended OIT, software occlusion culling | 0.57 ms/frame at 320×180 |
| `wubu3d_rig.py` | 21-joint skeleton, walk cycle, pose overrides | 1.78 m, 7.2 heads |
| `wubu2d.py` | flat cartoon puppets drawn in code, joint-driven | 9 poses × 7 expressions |
| `wubudenoise.c` | edge-aware à-trous denoiser, RGB→YCbCr, temporal reuse | 34.53 → 35.96 dB PSNR, 56 ms/frame |
| `wubu3d.py` | spec → film: geometry, camera, grade, score, mux | 110 s end to end at 480p |
| `wubu3d_spec.py` | the spec contract: schema, validation, resolve, cost estimate | 12 contract tests pass |

Sources live in `src/`. Around them:

| path | what it is |
|---|---|
| `tools/silhouette.py` | measures a silhouette PNG: heads tall, shoulder-widths, hip width, knee height, leg gap |
| `tools/salience.py` · `tools/cull_bench.py` | composition sampling and occlusion-culling benchmark |
| `tools/build_body.py` · `tools/character_sheet.py` | body builder and contact-sheet generator used by the rig |
| `specs/` | ten worked specs — preview, cartoon, cinematic, heavy, OIT, camera moves, plates |
| `docs/` | measured notes: OIT, occlusion culling, the 10-step pipeline, SLERM provenance, security audit |

## Run it

```bash
mkdir -p bin
gcc -O2 -o bin/wuburaster src/wuburaster.c -lm      # the C11 preview renderer
gcc -O2 -o bin/wubudenoise src/wubudenoise.c -lm

python3 src/wubu3d.py build  specs/demo_preview.json   # emit scene.py — inspect before spending CPU
python3 src/wubu3d.py raster specs/demo_preview.json   # 144 frames, 20 s, no Blender
python3 src/wubu3d.py make   specs/demo_cinematic.json # Blender 5.x → denoise → grade → score → mp4
```

Outputs land in `out/<name>/`: `scene.py`, `frames/`, `denoised/`, `graded/`, `score.wav`, `<name>.mp4`.
Blender 5.x is required for the Cycles path; the raster path runs on `gcc` and `libm`.

Nothing here is a secret, a fork, or a wrapper. The renderer, the denoiser, the rig and the
grade are all written from scratch against this project's own formats.

## Driven by an agent, not a mouse

The interface is a JSON file and a CLI with exit codes, because a process has to be able to
tell a bad spec from a broken box. `schema` describes the file, `validate` names the exact
field that is wrong, `plan` prices both render paths from measured receipts, and every
delivery writes `out/<name>/receipt.json` — resolution, frames, per-stage seconds, triangle
count, QA numbers and the MP4's sha256.

```bash
python3 src/wubu3d.py schema                       # the spec, as JSON Schema
python3 src/wubu3d.py validate specs/demo_preview.json   # exit 2 + field paths if illegal
python3 src/wubu3d.py plan     specs/demo_preview.json   # frames, shots, cost on both paths
python3 src/wubu3d.py raster   specs/demo_preview.json   # a whole film in ~20 s, no Blender
python3 src/wubu3d.py make     specs/probe_cycles.json   # Cycles delivery + receipt
python3 src/wubu3d.py qa       specs/demo_preview.json   # lit? moving? dead frames?
python3 tests/test_agent_cli.py                    # the contract, 12 cases, ~2 s
```

Full contract, exit codes and receipt schema: [`docs/AGENT_API.md`](docs/AGENT_API.md).

## The ecosystem

~ WuBu ~ is more than this repository: **100+ public repos, 113 stars, 6,807 dataset downloads,
6 models, zero venture dollars.** Agents in C11, a 744B MoE on a 25 GB machine, a video codec,
an OS, a memory system, and the media corpus the films are cut from.

Full map: [`ECOSYSTEM.md`](ECOSYSTEM.md)

## The doctrine

> **The work is the receipt.**

1. **Measure it.** If you cannot put a number on it, you do not know if it is good.
2. **Ship it.** A finished thing at 480p beats a perfect thing at never.
3. **Show the cost.** Say what it took — seconds, cores, watts, attempts.

> **A number is a promise you can keep.**
> **Permission is a rounding error.**
> **Cheap is not small. Cheap is honest about its budget.**

Full text: [`DOCTRINE.md`](DOCTRINE.md)

## The test

Ask anyone what their last piece cost: **resolution, frames, seconds, hardware.**
Four numbers means a pipeline. Adjectives mean a prompt.

Run it on this repository first. If the numbers do not hold up, say so — corrections are the
point, not a threat.

## Contact

James Taylor · Piqua, Ohio · open to remote research and technical work, and to building an
animation and ML lab in Ohio.

* GitHub: [github.com/waefrebeorn](https://github.com/waefrebeorn)
* Hugging Face: [huggingface.co/WaefreBeorn](https://huggingface.co/WaefreBeorn)
* YouTube: [youtube.com/@wubustreams](https://youtube.com/@wubustreams)

MIT licensed. Attribution appreciated, not required.
