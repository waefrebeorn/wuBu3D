# wubu3d vs the engines: what a *video* renderer owes a frame

The comparison that matters is not "can it run a game". wubu3d makes **cartoons and VFX for video** —
finished frames, offline, few of them, and every frame has to survive being paused on. So the axes are
the ones that show up in a still: colour management, antialiasing, motion blur, DOF, light transport,
particles, simulation, and the plumbing that gets pixels out of the machine intact.

Engine features below are cited to the vendor's own documentation. Our column is measured, in this
repository, with the command that produced the number where one exists.

## Where a video renderer earns its keep

| capability | who ships it | what they say it does | wubu3d |
|---|---|---|---|
| wide-gamut / HDR colour | Blender 5.0 | "overhauled colour management pipeline that natively supports wide-gamut and HDR colour spaces", ACES 1.3 and 2.0 views ([source](https://www.blender.org/download/releases/5-0/)) | **none.** sRGB bytes throughout, grade is a LAB statistics match, no tonemap and no OCIO |
| motion blur | UE Movie Render Pipeline, Unity HDRP | subframe accumulation / velocity-based blur ([UE docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-cinematics-in-unreal-engine), [Unity pipeline comparison](https://docs.unity3d.com/6/Documentation/Manual/render-pipelines-feature-comparison.html)) | **none.** no velocity pass; a fast pan strobes |
| depth of field | UE, Unity HDRP, Cycles | physical camera DOF with aperture/focus distance | **done.** `render_shaded.dof` from the z-buffer, three-tap CoC; bg variance 57 -> 42 |
| specular / material response | all | PBR or Blinn-Phong with roughness | **partial.** Blinn-Phong with a gloss exponent, measured 0 -> 3180 highlight px; no roughness map, no metalness |
| textures | all | sampled albedo/PBR from UVs | **done.** `wubu_tex`, perspective-correct UVs: detail 0.82 -> 4.30 |
| shadows | all | shadow maps with cascades, or ray-traced | **none.** a contact ellipse stands in; nothing occludes light |
| ambient occlusion | UE/Unity/Houdini | SSAO or baked AO | **partial.** ground-contact darkening only |
| volumetrics | UE, Cycles, Houdini 21 ("sparse GPU Pyro FX solver", reaction-diffusion, [source](https://www.sidefx.com/products/whats-new-in-h21/)) | participating media, god rays, fire and smoke | **partial.** depth fog only; no participating media |
| particles / VFX | UE Niagara, Unity VFX Graph, Houdini | GPU particle systems with curves, collisions, sprites | **none.** 47 Gumroad products sell this; it is our largest gap |
| cloth / soft body | Houdini Vellum, Blender, UE Chaos | position-based dynamics | **none** |
| hair / groom | all films pipelines | strand or card hair | **none.** hair is four boxes |
| retargeting | Houdini KineFX, UE | map a captured performance onto another skeleton ([Houdini 21 "Autorig Builder", motion mixer](https://www.sidefx.com/products/whats-new-in-h21/)) | **none.** poses only apply to our own joint names |
| autorig | Houdini 21, Blender addons | fit a skeleton to a mesh | **done.** `src/rig.c` band analysis, mean joint error 0.031 body units |
| skinning | all | heat/voxel weights, DQS | **done.** distance weights + Laplacian smoothing, crease 0.00442 -> 0.00240 |
| scattering | UE/Unity foliage tools, Houdini | Poisson or mask-driven instancing | **done.** `src/scatter.c`, min pair == radius, exclusions honoured |
| sequencer / timeline | UE Sequencer, Unity Timeline, Houdini Solaris Shot Builder | shots, cuts, camera rigs in one timeline | **partial.** a shot list in Python with absolute times, no editor |
| render farm / resume | Movie Render Queue, Deadline | queue, chunk, resume | **none.** one process, no resume |
| output formats | all | EXR (multichannel), ProRes, and the rest | **partial.** PNG frames + h264 via ffmpeg; no EXR, no ProRes, no data passes (depth/normal/motion) |
| compositing inside the tool | Nuke, Fusion, AE | layers, mattes, grade, god rays | **partial.** `plate.py`: matte, contact shadow, plate-key relight, composite, measured edge break 0.010 |

## Ranked by what a paused frame shows

1. **Colour management.** Blender 5 ships ACES in the box; we clip sRGB. Every graded frame is a
   compromise until there is a scene-linear pipeline with a tonemap. This is the largest honest gap
   and it is invisible until compared side by side.
2. **Particles.** 47 products sell them on Gumroad, every engine has a system, and a "VFX for video"
   tool with none is a cartoon renderer only.
3. **Shadows.** No shadow maps means light passes through walls. A contact ellipse fakes grounding,
   not occlusion.
4. **Motion blur.** A cartoon at 24 fps with fast cuts reads fine without it; a camera pan does not.
5. **Cloth / soft body / hair** — the three that make a character look alive rather than rigid.

## What we do have, that an engine would need a plugin for

- Per-pixel lighting in ~13 KB of C11 with no GPU, no shader compiler and no engine runtime: the whole
  renderer is `cc -O2` and a 9 MB binary.
- Rigging and skinning that measure themselves (`wubu_autorig` returns joints, `audit()` asserts the
  invariants), so a regression is a number, not a look.
- A shot pipeline that emits a verified mp4 and a manifest of gates in the same run.

## Not a gap, on purpose

Realtime performance, gameplay netcode, physics stability at 60 Hz, editor UX. We render minutes of
footage on a 4-core box without a GPU; an engine spends its complexity on frames it must deliver in
16 ms. Judging wubu3d by that is judging a camera by its autofocus speed.
