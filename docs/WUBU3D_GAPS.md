# wubu3d gaps, counted from the market

Generated from the census: 438 products from search plus 0 more found by seller and keyword hops (see `tools/lilypad.py`), scraped 2026-11-28.

Each row counts how many products advertise the operation, what we have, and three examples with links. A row we have marked `done` also names the file and the measured number.

| operation | products selling it | wubu3d | evidence | examples |
|---|---|---|---|---|
| skin & subsurface scattering | 0 | none | our characters are opaque lambert+specular | -- |
| translucency / transmission | 0 | none | no transmission path at all | -- |
| texture sampling | 18 | done | src/shade.c wubu_tex, perspective-correct UV, nearest sample: detail 0.82 -> 4.30 | [Texture - (Plugin)](https://mrquaxkers.gumroad.com/l/aebhqo), [Worm Host Animation](https://n5studios.gumroad.com/l/racij), [Roblox Blocky Finger Rig (Blender ](https://paribes.gumroad.com/l/fpbjgc) |
| normal mapping | 0 | none | no tangent space in the mesh path | -- |
| cast shadows | 0 | none | a contact ellipse stands in for a real shadow | -- |
| ambient occlusion | 1 | partial | ground-contact darkening only, not occlusion between parts | [Blender Batch AO Baker Addon](https://vdskinworks.gumroad.com/l/embsc) |
| bloom / glare | 1 | none | a threshold blur exists but is unused | [Spark AR - Heart Bloom / Shader](https://enuriru.gumroad.com/l/njlAb) |
| depth of field | 0 | done | render_shaded.dof, z-buffer CoC | -- |
| motion blur | 1 | none | no velocity pass | [Motion Blur Shaders – Advanced Sha](https://raulfx.gumroad.com/l/ebtxq) |
| volumetrics / fog | 1 | partial | depth fog in render_blocky only | [Volumetric Environment Shaders](https://naitoookami.gumroad.com/l/QceXI) |
| hair / fur grooming | 11 | none | hair is four boxes | [40% OFF🧨IN DESCRIPTION / Dergal VR](https://neochroma.gumroad.com/l/yxtvch), [Marik / Male / PC + Quest + Opti /](https://heartmarksman.gumroad.com/l/zuvneh), [Warren's Fast Fur Shader](https://warrenwolfy.gumroad.com/l/atntv) |
| cloth simulation | 3 | none | no simulation of any kind | [Roblox Multipurpose Cloth Rig (4.5](https://paribes.gumroad.com/l/hwthor), [Garment Tool](https://bartoszstyperek.gumroad.com/l/MAnWP), [Garment Tool 2.1 for MetaHuman — U](https://6062949617079.gumroad.com/l/sqbht) |
| soft body / jiggle | 0 | none | the walk bobs a whole body, no secondary motion | -- |
| ragdoll / physics | 5 | none | no solver | [Roblox Multipurpose Cloth Rig (4.5](https://paribes.gumroad.com/l/hwthor), [Roblox FPS System](https://jeynkinsrbxlstudios.gumroad.com/l/gfmdgs), [Unreal Self Balance 1.2 Project - ](https://codefloat.gumroad.com/l/ytjyu) |
| retargeting | 0 | none | poses only apply to our own joint names | -- |
| auto weighting | 0 | done | src/rig.c, Laplacian smoothing | -- |
| auto rig | 0 | done | src/rig.c wubu_autorig, 0.031 mean error | -- |
| IK solvers | 0 | done | src/rig.c, end->target 0.000000 | -- |
| retopology / remesh | 4 | none | no mesh editing at all | [MHFRT - Auto Facial Rig & Auto Ret](https://souhailninia.gumroad.com/l/pzqmlw), [PatchGAP - Plasticity Retopology t](https://bezgod.gumroad.com/l/ildlkt), [EzyTopo - Retopology tool for Maya](https://justinkirkwood.gumroad.com/l/otyqu) |
| UV unwrap / atlas | 2 | none | meshes arrive with UVs, we never make them | [Atlas Cutter](https://darktreetools.gumroad.com/l/fpros), [Bake Multiple Materials into One T](https://aisal.gumroad.com/l/gfeaqu) |
| LOD generation | 0 | none | one resolution, always | -- |
| occlusion culling | 1 | none | depth test only | [Sword Combat & NPC System [ROBLOX]](https://piercedevelop.gumroad.com/l/swhwn) |
| instancing / batching | 0 | none | every face is pushed individually | -- |
| procedural placement | 28 | none | props are placed by hand in the shot list | [Weight Scatter - (Plugin)](https://mrquaxkers.gumroad.com/l/vhxkmj), [Ultimate Blender Procedural Materi](https://ryankingart.gumroad.com/l/gdkltz), [Procedural Pipes & Roads (Godot 4)](https://mpecheux.gumroad.com/l/bmobcx) |
| tileable material authoring | 4 | none | no material system | [⚽ Roblox Football/Soccer Rigs (Kit](https://paribes.gumroad.com/l/ovwtcn), [Roblox Starter Rigs 1.0 MODDED](https://paribes.gumroad.com/l/xbrdsa), [Substance Node Pack / Dete Trim To](https://dete.gumroad.com/l/hjmavo) |
| decal projection | 3 | partial | world-space flat decals for footprints | [[Addon]DECALmachine](https://machin3.gumroad.com/l/fjXBHu), [MatricX bake: Blender Material & D](https://eidosedge.gumroad.com/l/gjpmlv), [Magic Decal](https://nebulaanimations.gumroad.com/l/bmouh) |
| node graph / shader authoring | 0 | none | shaders are hand-written C | -- |
| particle / VFX | 37 | none | no particles | [FUGA - Imagined by Starkim1999 [VF](https://starkim1999.gumroad.com/l/gwsrd), [Standing Fire [Medium Scale] VFX A](https://benharkervfx.gumroad.com/l/bnizsn), [WebGL Magnetic Field: Interactive ](https://creativeapes.gumroad.com/l/dqgfpw) |
| navmesh / pathfinding | 8 | none | no agents | [WEPPY Roblox Plugin Pro](https://weppy.gumroad.com/l/faccjs), [SmartMonster AI - Dynamic Enemy Pa](https://scriptrblx.gumroad.com/l/zwotiv), [NodeArchitect - AI Agent and MCP S](https://bishopvfx.gumroad.com/l/thptkt) |
| motion capture cleanup | 0 | none | no mocap path | -- |

**22 operations missing, 3 partial, 5 done.**

Ordered by how many products sell it, the top five missing are:

- **particle / VFX** — 37 products
- **procedural placement** — 28 products
- **hair / fur grooming** — 11 products
- **navmesh / pathfinding** — 8 products
- **ragdoll / physics** — 5 products
