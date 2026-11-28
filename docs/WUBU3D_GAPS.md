# wubu3d gaps, counted from the market

Generated from the census: 438 products from search plus 717 more found by seller and keyword hops (see `tools/lilypad.py`), scraped 2026-11-28.

Each row counts how many products advertise the operation, what we have, and three examples with links. A row we have marked `done` also names the file and the measured number.

| operation | products selling it | wubu3d | evidence | examples |
|---|---|---|---|---|
| skin & subsurface scattering | 3 | none | our characters are opaque lambert+specular | [Next-Gen Shaders V5.10 for Honey S](https://hanmen.gumroad.com/l/cdxely), [Aura SSS Collection for C4D and Re](https://effectatron.gumroad.com/l/lztbid), [Single Map PBR Skin Shader for Ble](https://victoriadyer.gumroad.com/l/ZRnyU) |
| translucency / transmission | 2 | none | no transmission path at all | [Glass Shader & Props for Honey Sel](https://hanmen.gumroad.com/l/avfvbe), [[VRC] Glass/Refraction Shader](https://jayievr.gumroad.com/l/eznby) |
| texture sampling | 64 | done | src/shade.c wubu_tex, perspective-correct UV, nearest sample: detail 0.82 -> 4.30 | [Texture - (Plugin)](https://mrquaxkers.gumroad.com/l/aebhqo), [Worm Host Animation](https://n5studios.gumroad.com/l/racij), [Roblox Blocky Finger Rig (Blender ](https://paribes.gumroad.com/l/fpbjgc) |
| normal mapping | 14 | none | no tangent space in the mesh path | [Novabeast Muscle Textures - Normal](https://mmmos.gumroad.com/l/lcvpk), [Nardoragon Muscle Textures - Norma](https://mmmos.gumroad.com/l/owmff), [Druffle Muscle Textures - Normal m](https://mmmos.gumroad.com/l/aksin) |
| cast shadows | 1 | none | a contact ellipse stands in for a real shadow | [CascadeBridge – Blender to Cascade](https://ibr4him2.gumroad.com/l/rafwrh) |
| ambient occlusion | 15 | partial | ground-contact darkening only, not occlusion between parts | [Blender Batch AO Baker Addon](https://vdskinworks.gumroad.com/l/embsc), [Novabeast Muscle Textures - Normal](https://mmmos.gumroad.com/l/lcvpk), [Nardoragon Muscle Textures - Norma](https://mmmos.gumroad.com/l/owmff) |
| bloom / glare | 2 | none | a threshold blur exists but is unused | [Spark AR - Heart Bloom / Shader](https://enuriru.gumroad.com/l/njlAb), [▌BLOOM - FEMBOY B_SIDE ▌[DEPRECATE](https://arkhype.gumroad.com/l/ftyhxv) |
| depth of field | 0 | done | render_shaded.dof, z-buffer CoC | -- |
| motion blur | 1 | none | no velocity pass | [Motion Blur Shaders – Advanced Sha](https://raulfx.gumroad.com/l/ebtxq) |
| volumetrics / fog | 9 | partial | depth fog in render_blocky only | [Stylized Sky World Generator](https://reipart.gumroad.com/l/vaznyj), [Volumetric Environment Shaders](https://naitoookami.gumroad.com/l/QceXI), [Physical Starlight and Atmosphere](https://physicaladdons.gumroad.com/l/AYuK) |
| hair / fur grooming | 31 | none | hair is four boxes | [40% OFF🧨IN DESCRIPTION / Dergal VR](https://neochroma.gumroad.com/l/yxtvch), [Marik / Male / PC + Quest + Opti /](https://heartmarksman.gumroad.com/l/zuvneh), [Warren's Fast Fur Shader](https://warrenwolfy.gumroad.com/l/atntv) |
| cloth simulation | 5 | none | no simulation of any kind | [Roblox Multipurpose Cloth Rig (4.5](https://paribes.gumroad.com/l/hwthor), [Garment Tool](https://bartoszstyperek.gumroad.com/l/MAnWP), [Garment Tool 2.1 for MetaHuman — U](https://6062949617079.gumroad.com/l/sqbht) |
| soft body / jiggle | 6 | none | the walk bobs a whole body, no secondary motion | [JiggleGen](https://pathnode.gumroad.com/l/odzcn), [Squash - Stretch Maker for Maya](https://khaledhussein.gumroad.com/l/AuyUu), [Blender Physics Masterclass: Rigid](https://mk3dgraphics.gumroad.com/l/xypeey) |
| ragdoll / physics | 12 | none | no solver | [Roblox Multipurpose Cloth Rig (4.5](https://paribes.gumroad.com/l/hwthor), [Roblox FPS System](https://jeynkinsrbxlstudios.gumroad.com/l/gfmdgs), [Unreal Self Balance 1.2 Project - ](https://codefloat.gumroad.com/l/ytjyu) |
| retargeting | 5 | none | poses only apply to our own joint names | [Maya Retarget Pro](https://animpro.gumroad.com/l/xoyiaf), [Universal Spatial Retargeter for A](https://chmillout.gumroad.com/l/yogpph), [HP Art Toolset: Animation Retarget](https://hparttoolset.gumroad.com/l/mkyzly) |
| auto weighting | 0 | done | src/rig.c, Laplacian smoothing | -- |
| auto rig | 1 | done | src/rig.c wubu_autorig, 0.031 mean error | [Maya Pyhon quadruped autorig tutor](https://blaabjerg.gumroad.com/l/lNZUz) |
| IK solvers | 0 | done | src/rig.c, end->target 0.000000 | -- |
| retopology / remesh | 6 | none | no mesh editing at all | [MHFRT - Auto Facial Rig & Auto Ret](https://souhailninia.gumroad.com/l/pzqmlw), [PatchGAP - Plasticity Retopology t](https://bezgod.gumroad.com/l/ildlkt), [EzyTopo - Retopology tool for Maya](https://justinkirkwood.gumroad.com/l/otyqu) |
| UV unwrap / atlas | 8 | none | meshes arrive with UVs, we never make them | [Atlas Cutter](https://darktreetools.gumroad.com/l/fpros), [Bake Multiple Materials into One T](https://aisal.gumroad.com/l/gfeaqu), [Atlas VRFX - Studio Light [VRChat]](https://atlasvrfx.gumroad.com/l/zsqux) |
| LOD generation | 3 | none | one resolution, always | [SimplyFive-PRO (LOD Generator for ](https://zloy-pingvin.gumroad.com/l/fdlhr), [SimplyFive-Light (LOD Generator fo](https://zloy-pingvin.gumroad.com/l/tkmyvg), [Resolution LOD Generator (Blender ](https://cdmcrash.gumroad.com/l/yxznv) |
| occlusion culling | 1 | none | depth test only | [Sword Combat & NPC System [ROBLOX]](https://piercedevelop.gumroad.com/l/swhwn) |
| instancing / batching | 0 | none | every face is pushed individually | -- |
| procedural placement | 54 | done | src/scatter.c Bridson Poisson-disk: min pair == radius, exclusions honoured | [Weight Scatter - (Plugin)](https://mrquaxkers.gumroad.com/l/vhxkmj), [Stylized Sky World Generator](https://reipart.gumroad.com/l/vaznyj), [Ultimate Blender Procedural Materi](https://ryankingart.gumroad.com/l/gdkltz) |
| tileable material authoring | 15 | none | no material system | [⚽ Roblox Football/Soccer Rigs (Kit](https://paribes.gumroad.com/l/ovwtcn), [Roblox Starter Rigs 1.0 MODDED](https://paribes.gumroad.com/l/xbrdsa), [Substance Node Pack / Dete Trim To](https://dete.gumroad.com/l/hjmavo) |
| decal projection | 15 | partial | world-space flat decals for footprints | [Omni-Matrix Holograph: Premium 3D ](https://creativeapes.gumroad.com/l/umfgop), [[Addon]DECALmachine](https://machin3.gumroad.com/l/fjXBHu), [MatricX bake: Blender Material & D](https://eidosedge.gumroad.com/l/gjpmlv) |
| node graph / shader authoring | 1 | none | shaders are hand-written C | [Holofoil Shader](https://1hp.gumroad.com/l/fogdg) |
| particle / VFX | 47 | none | no particles | [FUGA - Imagined by Starkim1999 [VF](https://starkim1999.gumroad.com/l/gwsrd), [Standing Fire [Medium Scale] VFX A](https://benharkervfx.gumroad.com/l/bnizsn), [WebGL Magnetic Field: Interactive ](https://creativeapes.gumroad.com/l/dqgfpw) |
| navmesh / pathfinding | 13 | none | no agents | [WEPPY Roblox Plugin Pro](https://weppy.gumroad.com/l/faccjs), [SmartMonster AI - Dynamic Enemy Pa](https://scriptrblx.gumroad.com/l/zwotiv), [NodeArchitect - AI Agent and MCP S](https://bishopvfx.gumroad.com/l/thptkt) |
| motion capture cleanup | 4 | none | no mocap path | [Make Movement Feel Real - 3 Hours ](https://quantumstage.gumroad.com/l/uqomm), [Full motion capture cleanup course](https://pavelbarnev.gumroad.com/l/jXWDVB), [Mocap Blender](https://emblematic3.gumroad.com/l/ujhub) |

**21 operations missing, 3 partial, 6 done.**

Ordered by how many products sell it, the top five missing are:

- **particle / VFX** — 47 products
- **hair / fur grooming** — 31 products
- **tileable material authoring** — 15 products
- **normal mapping** — 14 products
- **navmesh / pathfinding** — 13 products
