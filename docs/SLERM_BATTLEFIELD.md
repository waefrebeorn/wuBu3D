# The SLERM battlefield

> “to slerm is to raise the floor standards, do not feel bad you are on here, understand that time marches forward, do not become a boomer”

A census of Gumroad's **tool** market — plugins, addons, shaders, editor tools, systems. Not its asset packs: a model cannot be slermed, an operation can.

Scope: 53 queries, 1012 listings scraped, **438 tools kept**, 23 dropped as asset packs. Scraped 2026-11-28.

A paid tool's description is a specification: it names the operation, the input and the promise. That is enough to reimplement the operation in C11 and measure whether it holds. Nothing here is copied or redistributed — names, prices, claims and links are citation only.


## What already stands on this floor

| capability | file | measured |
|---|---|---|
| per-pixel lighting: lambert, point lights, fresnel rim, ground AO, 2x SSAA | `src/shade.c` | gradient p90 0.11 -> 0.51, distinct colours 58 -> 194 |
| adaptive auto-skinning: distance binding, Laplacian weight smoothing, top-k | `src/rig.c` | crease 0.00442 -> 0.00240 over 32 passes |
| two-bone IK with pole vector, FABRIK for n-bone chains | `src/rig.c` | end->target 0.000000, segment lengths constant to 6 dp |
| auto-rig: height bands, medial axis, inboard/outboard limb split | `src/rig.c` | mean joint error 0.031 body units, max 0.073 |
| grip, attach, surface placement, grid snap | `src/grab.c` | placement 0.00000, rigidity 0.000000, drift 0.0438 |
| blocky R15 rig on a measured band table with an invariant audit | `r15.py` | 7/7 invariants pass |
| planted IK walk: world-fixed stance, root cancellation, contact-phase bob | `animate_r15.py` | slip 0.41 -> 0.075, duty 0.19 -> 0.62, penetration 28 -> 3.7 mm |
| Roblox asset import: .mesh v1 soup, .mesh v4 binary, rbxm binary | `rbxmesh.py, rbxm.py` | 506-triangle UGC item parsed end to end |
| specular (Blinn-Phong half-vector, per-pixel) + depth of field from the z-buffer | `src/shade.c, render_shaded.py` | highlights 0 -> 3180 px over 200; bg variance 57 -> 42 |

Not implemented yet, and said plainly: **texture sampling** (surfaces are flat-coloured), **cast shadows** (a contact ellipse stands in), **bevels**, **retargeting**, **squash/stretch**, and **translucency** — the glossy subsurface look of a TrendStory-style vinyl character is a transmission model we do not have, even though the specular highlight and the depth of field around it now exist.


## Shaders & rendering (71)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 1 | "Frosted Glass" Gradient Shader | 1HP | 15.00 | _page unavailable (HTTPError)_ | [exzjvy](https://1hp.gumroad.com/l/exzjvy) |
| 2 | "Shaders Plus" - Real-Time Caustics, Thin Film, Dispersion f | SMOUSE | free | _page unavailable (HTTPError)_ | [bljae](https://smouse.gumroad.com/l/bljae) |
| 3 | (ENG) TUTORIAL NPR Painterly Arnold Shader Pack: Arcane & An | Mani Salguero | 27.50 | _page unavailable (HTTPError)_ | [obmxk](https://manisalguero.gumroad.com/l/obmxk) |
| 4 | 150+ ChatGPT prompts to make you a top 1% shader wizard 🪄 | OccaSoftware | free | _page unavailable (HTTPError)_ | [ihlcap](https://occasoftware.gumroad.com/l/ihlcap) |
| 5 | [Tutorial] UE5 Advanced Ocean Shader Creation - With Gerstne | Abderrezak Bouhedda | 20.00 | _page unavailable (HTTPError)_ | [nmwaa](https://artofab.gumroad.com/l/nmwaa) |
| 6 | Advanced Outline Shader for Unreal Engine 5 | Evans Bohl | 14.99 | _page unavailable (HTTPError)_ | [uiqov](https://evansbohl.gumroad.com/l/uiqov) |
| 7 | Bake Multiple Materials into One Texture Atlas - AtlasForge  | Aisal | free | _page unavailable (HTTPError)_ | [gfeaqu](https://aisal.gumroad.com/l/gfeaqu) |
| 8 | Batch Render Creator - Local Render Queue for Blender | Wanderson M. Pimenta | free | _page unavailable (HTTPError)_ | [kAloE](https://blender-addons.gumroad.com/l/kAloE) |
| 9 | C4D plugin for Seedance, Meshy, Kling and any Al possible. C | Dani Zaitcev | 5.00 | Nano Pro 3.5 The only AI plugin you actually need for Cinema 4D. Think of Nano Pro as your Cinema 4D render window, but with AI image, video, and 3D... | [cbfnyr](https://manicporcupine.gumroad.com/l/cbfnyr) |
| 10 | Cartoon Afro Girl 2 - Toon Rigged Child Character Maya Versi | Harun BOL (A.K.A.) Cha | 97.00 | Cartoon Afro Girl - Toon Rigged Child - Maya Version High Quality Low Poly Rigged Cute African American Little Girl Model... | [ezrkd](https://harunbol.gumroad.com/l/ezrkd) |
| 11 | Cinematic Product Studio Blender Add On - 79 Animation,  52  | Gigi Gorlova | 15.00 | _page unavailable (HTTPError)_ | [hewskz](https://gigirenders.gumroad.com/l/hewskz) |
| 12 | COD Auto-Shader Blender Add-On + More | killshotttttt | 15.00 | _page unavailable (HTTPError)_ | [hbdsgo](https://killshotttttt.gumroad.com/l/hbdsgo) |
| 13 | DXSky: Skybox Shader for VRChat & Unity | DX | 11.00 | _page unavailable (HTTPError)_ | [xtghoq](https://dx30.gumroad.com/l/xtghoq) |
| 14 | Fake Diamonds shader for Cycles and Eevee | Lance Phan | 5.85 | This product is a collection of 4 diamond shader node groups to let you quickly and easily make a lot of diamonds. These node groups are very easy to use... | [wfoff](https://lancephan.gumroad.com/l/wfoff) |
| 15 | Feather/Fur Shader | normalizedcrow | free | _page unavailable (HTTPError)_ | [bvako](https://normalizedcrow.gumroad.com/l/bvako) |
| 16 | GLSL Eyeball + MediaPipe Timemachine / Two-in-One TouchDesig | Irina.ae | 5.00 | _page unavailable (HTTPError)_ | [ucsggn](https://irinaught.gumroad.com/l/ucsggn) |
| 17 | Godot Pixelated Shader + RGB shift + Pixel Size + Curved scr | Yaroslav Samoilov | 5.99 | _page unavailable (HTTPError)_ | [xqaoh](https://yaosam0.gumroad.com/l/xqaoh) |
| 18 | Godot Shader Pack: 150+ shaders for Godot 4 | Filip Rachůnek | 14.99 | _page unavailable (HTTPError)_ | [krudjf](https://filiprachunek.gumroad.com/l/krudjf) |
| 19 | Holofoil Shader | 1HP | 15.00 | _page unavailable (HTTPError)_ | [fogdg](https://1hp.gumroad.com/l/fogdg) |
| 20 | Hologram Shaders Pro for Unity | Daniel Ilett | 19.99 | _page unavailable (HTTPError)_ | [oqgmq](https://danielilett.gumroad.com/l/oqgmq) |
| 21 | MANI NPR for Blender — Stylized Shader & Lookdev Toolkit (An | Mani Salguero | 39.99 | _page unavailable (HTTPError)_ | [wdcig](https://manisalguero.gumroad.com/l/wdcig) |
| 22 | MatricX bake: Blender Material & Decal Baking Addon | EidosEdge | 79.00 | _page unavailable (HTTPError)_ | [gjpmlv](https://eidosedge.gumroad.com/l/gjpmlv) |
| 23 | More shaders in Godot 4: Add stunning visual effects to your | Filip Rachůnek | 9.90 | _page unavailable (HTTPError)_ | [mrtmj](https://filiprachunek.gumroad.com/l/mrtmj) |
| 24 | Motion Blur Shaders – Advanced Shader Setups for Unreal Engi | raulfx | 14.99 | _page unavailable (HTTPError)_ | [ebtxq](https://raulfx.gumroad.com/l/ebtxq) |
| 25 | Multi-Mat Baker - Bake Multiple Materials into One PBR Textu | Junaid Alam | 15.00 | _page unavailable (HTTPError)_ | [btyxer](https://blenderustad.gumroad.com/l/btyxer) |
| 26 | Next-Gen Shader Helper Plugin | Hanmen | 5.99 | _page unavailable (HTTPError)_ | [lnfdr](https://hanmen.gumroad.com/l/lnfdr) |
| 27 | Next-Gen Shaders V5.10 for Honey Select 2 (FLASH SALE) | Hanmen | 10.99 | _page unavailable (HTTPError)_ | [cdxely](https://hanmen.gumroad.com/l/cdxely) |
| 28 | OMNIKIT — Geometry Nodes, VFX & Materials for Blender | Blender addons | free | _page unavailable (HTTPError)_ | [lauvm](https://maroc777772.gumroad.com/l/lauvm) |
| 29 | Photoshop Character Designer Toolkit Brushes | Francisco Beltrán | 20.00 | This pack includes all my brush sets (Pencils, Inkers, Screentones, Storyboard) plus the Cartoon, Sketch, Gouache, Oils, Pastels and Aquarelles / Watercolors... | [xAMz](https://frankstore.gumroad.com/l/xAMz) |
| 30 | Physically Based Cel Shader | Jumpeter | 50.00 | _page unavailable (HTTPError)_ | [zobtn](https://jumpeter.gumroad.com/l/zobtn) |
| 31 | Quest Basic Water Shader(VRChat) | noriben | 9.00 | _page unavailable (HTTPError)_ | [exzzss](https://noriben3.gumroad.com/l/exzzss) |
| 32 | Quick Water Drops V3 (Blender 5.0+ Addon) | Faebe | 5.00 | _page unavailable (HTTPError)_ | [yifmr](https://faebe.gumroad.com/l/yifmr) |
| 33 | RainDrop Shader (VRChat) | noriben | 9.00 | _page unavailable (HTTPError)_ | [quhsao](https://noriben3.gumroad.com/l/quhsao) |
| 34 | Realistic Rainbow Shader (VRChat) | noriben | 7.00 | _page unavailable (HTTPError)_ | [qbuorz](https://noriben3.gumroad.com/l/qbuorz) |
| 35 | Realistic Unity Clay Shader | taletronic | 2.00 | _page unavailable (HTTPError)_ | [TVgZk](https://taletronic.gumroad.com/l/TVgZk) |
| 36 | REDSHIFT SHADER SUITE v.5 + REDSHIFT LIGHT SUITE v.5 + TT MO | jonpol | 139.00 | _page unavailable (HTTPError)_ | [milqk](https://trucateam.gumroad.com/l/milqk) |
| 37 | Retro Shaders Pro for Unity URP | Daniel Ilett | 23.99 | _page unavailable (HTTPError)_ | [fnrbi](https://danielilett.gumroad.com/l/fnrbi) |
| 38 | SafeSpace (VRChat Shader & Particle Filter) | KleineLuka 🌺 | 5.00 | _page unavailable (HTTPError)_ | [qgniq](https://kleineluka.gumroad.com/l/qgniq) |
| 39 | Sanctus Library - Procedural Materials and Assets Library fo | Sanctus | free | _page unavailable (HTTPError)_ | [fogcj](https://sanctus.gumroad.com/l/fogcj) |
| 40 | Screen Freeze Shader (Godot 4) | Mina Pêcheux | 6.00 | _page unavailable (HTTPError)_ | [femznt](https://mpecheux.gumroad.com/l/femznt) |
| 41 | Shader Toolbox: Graphs and Nodes for Unity URP | Daniel Ilett | 24.99 | _page unavailable (HTTPError)_ | [tjlzf](https://danielilett.gumroad.com/l/tjlzf) |
| 42 | Shey Hair Shader | Shey | 10.00 | _page unavailable (HTTPError)_ | [kvuuz](https://shrenders.gumroad.com/l/kvuuz) |
| 43 | Simple Skybox Shader | TechSane | 3.00 | _page unavailable (HTTPError)_ | [ybnjla](https://techsane.gumroad.com/l/ybnjla) |
| 44 | Skybox - (Plugin) | MrQuaxkers | 9.99 | 450+ Skybox library / browser for roblox studio. | [pjedcf](https://mrquaxkers.gumroad.com/l/pjedcf) |
| 45 | SkyCraft: Skybox Shader for VRChat & Unity | DX | 8.00 | _page unavailable (HTTPError)_ | [cdegf](https://dx30.gumroad.com/l/cdegf) |
| 46 | SkyMove: Skybox Shader for VRChat & Unity & Blender | DX | 8.00 | _page unavailable (HTTPError)_ | [adrpwl](https://dx30.gumroad.com/l/adrpwl) |
| 47 | Snakeskin Tunnel / 2-in-1 TouchDesigner Gyroid Shader | Irina.ae | 10.00 | A real-time raymarched gyroid shader that never ends. Two .toe files included — one driven by MediaPipe hand tracking with three switchable colorways, one by... | [ngmfist](https://irinaught.gumroad.com/l/ngmfist) |
| 48 | Soft Outline Shader (VRChat) | Zekk | 13.59 | _page unavailable (HTTPError)_ | [exmcjh](https://zekk.gumroad.com/l/exmcjh) |
| 49 | Spark AR - Heart Bloom / Shader | Spark AR Shaders by De | 50.00 | _page unavailable (HTTPError)_ | [njlAb](https://enuriru.gumroad.com/l/njlAb) |
| 50 | Stylized Medieval Inn Shader Pack for Blender 5 Cycles | 3D Tudor | 4.50 | _page unavailable (HTTPError)_ | [atisqm](https://3dtudor.gumroad.com/l/atisqm) |
| 51 | Stylized Water Shaders And Generator | Casey Sheep | 12.00 | _page unavailable (HTTPError)_ | [jclot](https://caseysheep.gumroad.com/l/jclot) |
| 52 | TG Shaders: Updated Shaders for Assetto Corsa | Allies Motor House | 8.00 | _page unavailable (HTTPError)_ | [mlpnj](https://threatjpn.gumroad.com/l/mlpnj) |
| 53 | Tiny Hair Shader | tinynocky | free | _page unavailable (HTTPError)_ | [yhyuou](https://tinynocky.gumroad.com/l/yhyuou) |
| 54 | Udin Blender Shaders | UDIN | free | _page unavailable (HTTPError)_ | [fzvbo](https://udinbv.gumroad.com/l/fzvbo) |
| 55 | UE 5 Katana Toolkit : 30+ professional tools, materials, and | I am Wanderboy. | 24.90 | _page unavailable (HTTPError)_ | [azfnlg](https://xaviwanderboy.gumroad.com/l/azfnlg) |
| 56 | UE5 Procedural Regular Polygon Shader | HeyYo | 3.00 | _page unavailable (HTTPError)_ | [nmusq](https://heyyohanashima.gumroad.com/l/nmusq) |
| 57 | Ultimate Blender Procedural Material Pack | Ryan King Art | 55.30 | _page unavailable (HTTPError)_ | [gdkltz](https://ryankingart.gumroad.com/l/gdkltz) |
| 58 | Ultimate Metallic Silk: Interactive Molten Shader for Framer | Creative Apes | 10.00 | _page unavailable (HTTPError)_ | [pndod](https://creativeapes.gumroad.com/l/pndod) |
| 59 | Ultimate ShaderFuse Guide for DaVinci Resolve | Akascape | 20.00 | _page unavailable (HTTPError)_ | [ohaswb](https://akascape.gumroad.com/l/ohaswb) |
| 60 | Unity VFX Graph：Collision Edge Line(SDF) | Eric VFX Studio | 4.00 | Created using VFX Graph and SDF, particles can create irregular lines along their edges when in contact with SDF. Version：6000.0.3f1 Render Mode：HDRP... | [xybwbh](https://raywang4.gumroad.com/l/xybwbh) |
| 61 | Unity VFX Graph：Lightning Trail | Eric VFX Studio | 10.00 | Drag lightning effect created using Unity VFX Graph, You can follow the target point and modify the length, color, jitter level, etc. 2022.3.45f1 Render... | [vvhpas](https://raywang4.gumroad.com/l/vvhpas) |
| 62 | Unity VFX Graph：Sci-fi Line | Eric VFX Studio | 3.00 | Sci-fi linework created using Unity VFX Graph. You can modify the line changes, size, color, direction, etc. by yourself. 2021.3.28f1(up) Render Mode：HDRP... | [eibuq](https://raywang4.gumroad.com/l/eibuq) |
| 63 | Unity VFX Graph：Waterfall(HDRP) | Eric VFX Studio | 7.50 | _page unavailable (HTTPError)_ | [slzhfx](https://raywang4.gumroad.com/l/slzhfx) |
| 64 | Volumetric Environment Shaders | Naito Ookami | 12.50 | Fog Volume/Fog Volume Lite The first shader is an extremely customizable fog shader with several variants for performance optimization. Shader variants are... | [QceXI](https://naitoookami.gumroad.com/l/QceXI) |
| 65 | VRChat Hypno Eyes Shader / 🌌 Somna Presets | Value 🌿 | 15.00 | _page unavailable (HTTPError)_ | [cwqvu](https://valuef.gumroad.com/l/cwqvu) |
| 66 | Warren's Fast Fur Shader | Warren | free | _page unavailable (HTTPError)_ | [atntv](https://warrenwolfy.gumroad.com/l/atntv) |
| 67 | Water Shader Blender Add-on + Assets & Terrains | Chuck_CG | free | _page unavailable (HTTPError)_ | [sxbcnw](https://chuckcg.gumroad.com/l/sxbcnw) |
| 68 | YMA Toon Shader [RS + C4D] [DEPRECATED - C4D 2023 - XPresso  | You And Me Academy | 49.00 | ATTENTION DEPRECATED: YMA Toon Shader uses XPresso only and was custom built in 2023 before toon existed in Redshift. For 2026 modern Redshift Toon Materials... | [icujek](https://youmeacademy.gumroad.com/l/icujek) |
| 69 | 🌌 Domain Warp Noise Generator (GPU Compute Shader) | CyberLuna | free | _page unavailable (HTTPError)_ | [acjge](https://cyberluna.gumroad.com/l/acjge) |
| 70 | 💦 VRChat Goo Shader 2.0 / 🌌 Somna Presets | Value 🌿 | 17.50 | _page unavailable (HTTPError)_ | [pzfmx](https://valuef.gumroad.com/l/pzfmx) |
| 71 | 📜 Worley Noise Generator (GPU Compute Shader) | CyberLuna | free | _page unavailable (HTTPError)_ | [tnlsug](https://cyberluna.gumroad.com/l/tnlsug) |

## Rigging, skinning & animation (103)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 72 | 2D FX Animation Bundle – High-Impact Visual Effects for Anim | DucVu FX | 35.00 | ⚡ Subscribe for official store updates. I'm engineering something big behind the scenes. Stay tuned. 📢 Update 2026: FX List & Future Updates View the Update... | [yrryu](https://ducvu.gumroad.com/l/yrryu) |
| 73 | 2D Rigging Toolbox 4.0 | Motion Gears | 22.50 | _page unavailable (HTTPError)_ | [iqabgx](https://motiongears.gumroad.com/l/iqabgx) |
| 74 | 2D/3D Storyboarding MASTERCLASS - Creating Animatics in BLEN | Spitfire Storyboards | 250.00 | Are you looking to learn how to create 2D 3D storyboards and animatics using Blender and its awesome Grease Pencil tool? Then this is THE COURSE for you... | [tciowl](https://spitfirestoryboards.gumroad.com/l/tciowl) |
| 75 | AniMate Forge - all AniMate Add-ons Bundle | not that NDA | 89.00 | _page unavailable (HTTPError)_ | [lgvbxw](https://nda.gumroad.com/l/lgvbxw) |
| 76 | AniMate Pro - Core | not that NDA | 50.00 | _page unavailable (HTTPError)_ | [kxqdom](https://nda.gumroad.com/l/kxqdom) |
| 77 | Animated 3D Curve Graph in AE / Project File | Noble Kreative | 30.00 | _page unavailable (HTTPError)_ | [hQcfQ](https://noblekreative.gumroad.com/l/hQcfQ) |
| 78 | Animated RPG Health Bar | gfxcomet | 11.40 | _page unavailable (HTTPError)_ | [mohtug](https://gfxcomet.gumroad.com/l/mohtug) |
| 79 | Animated Toggle | gfxcomet | free | _page unavailable (HTTPError)_ | [txoms](https://gfxcomet.gumroad.com/l/txoms) |
| 80 | Animation Snapper Pro - Blender Addon | Melowilo Animation | 24.99 | _page unavailable (HTTPError)_ | [rwyvce](https://melowilo.gumroad.com/l/rwyvce) |
| 81 | Animator Toolkit | TohruTheDragon | 20.00 | _page unavailable (HTTPError)_ | [oizdm](https://tohruthedragon.gumroad.com/l/oizdm) |
| 82 | Anime Codes | gfxcomet | 1.80 | _page unavailable (HTTPError)_ | [skjcnx](https://gfxcomet.gumroad.com/l/skjcnx) |
| 83 | Anime Egg Shop | gfxcomet | free | _page unavailable (HTTPError)_ | [hkqiur](https://gfxcomet.gumroad.com/l/hkqiur) |
| 84 | Anime Hair HM Toolkit — Shadows & Highlights for Blender | Weytant_V | 15.20 | _page unavailable (HTTPError)_ | [gywiag](https://weytant.gumroad.com/l/gywiag) |
| 85 | Anime Health 3 | gfxcomet | 1.80 | _page unavailable (HTTPError)_ | [batgd](https://gfxcomet.gumroad.com/l/batgd) |
| 86 | Anime Inventory 2 | gfxcomet | 4.80 | _page unavailable (HTTPError)_ | [hmmdv](https://gfxcomet.gumroad.com/l/hmmdv) |
| 87 | Anime Quests | gfxcomet | 3.00 | _page unavailable (HTTPError)_ | [stqzza](https://gfxcomet.gumroad.com/l/stqzza) |
| 88 | Anime Rewards UI for Roblox Studio (RBXM) | Kaisen | free | _page unavailable (HTTPError)_ | [qogihq](https://claritykaisen.gumroad.com/l/qogihq) |
| 89 | Anime Settings | gfxcomet | 3.00 | _page unavailable (HTTPError)_ | [ydgqz](https://gfxcomet.gumroad.com/l/ydgqz) |
| 90 | Anime Simulator 2 UI Kit | gfxcomet | 11.40 | _page unavailable (HTTPError)_ | [hchgy](https://gfxcomet.gumroad.com/l/hchgy) |
| 91 | Anime Simulator Kit V2 | gfxcomet | 11.97 | _page unavailable (HTTPError)_ | [jibid](https://gfxcomet.gumroad.com/l/jibid) |
| 92 | Anime Stylized VFX - Unity | Vefects - Realtime VFX | 29.99 | _page unavailable (HTTPError)_ | [tfegu](https://vefects.gumroad.com/l/tfegu) |
| 93 | Anime Units | gfxcomet | 6.00 | _page unavailable (HTTPError)_ | [hwxbz](https://gfxcomet.gumroad.com/l/hwxbz) |
| 94 | AnimToTexture (VAT) One-Click Tool by tiedtke. | tiedtke. | 9.99 | _page unavailable (HTTPError)_ | [agfrjg](https://tiedtke.gumroad.com/l/agfrjg) |
| 95 | Arrow Shot VFX | HeyYo | 7.00 | A blazing arrow streaks across the field and strikes the enemy, bursting into a ring of light and scattering sparks. Made in Unreal Engine. I provide the... | [phxbo](https://heyyohanashima.gumroad.com/l/phxbo) |
| 96 | Audiomation for Unity animation | Pancake992 | 7.00 | _page unavailable (HTTPError)_ | [nxkih](https://pancake992.gumroad.com/l/nxkih) |
| 97 | basic scripts for the OverRig animation method | Pavel Barnev | 70.00 | _page unavailable (HTTPError)_ | [cIdFbR](https://pavelbarnev.gumroad.com/l/cIdFbR) |
| 98 | Blender Massive 250-Piece Modular Mega - Kitbash Immersive C | 3D Tudor | 18.00 | _page unavailable (HTTPError)_ | [bmbhc](https://3dtudor.gumroad.com/l/bmbhc) |
| 99 | Book Rigger | Tik Works | 15.00 | _page unavailable (HTTPError)_ | [vjcph](https://tikworks.gumroad.com/l/vjcph) |
| 100 | Bookasaur Rig | ComixProd. | free | _page unavailable (HTTPError)_ | [YMeCo](https://comixproductions.gumroad.com/l/YMeCo) |
| 101 | CGDive: The Vault - Rigging and Animation Tutorials [SUBSCRI | Todor - cgdive.com | 6.00 | _page unavailable (HTTPError)_ | [ruyce](https://toshicg.gumroad.com/l/ruyce) |
| 102 | Cubic Face (Roblox Face Rig) | ComixProd. | free | Cubic Face is a simple face rig I created. It was made in a video. No credit needed, however do not redistribute or claim ownership. If you want to share... | [crzat](https://comixproductions.gumroad.com/l/crzat) |
| 103 | DEM V3.1 — Procedural Animation System for Cinema 4D + Blend | Giuliano Dasky | 59.00 | NEW RELEASE — DEM V3.1 A NEW WAY TO ANIMATE IN CINEMA 4D A complete procedural animation system — build advanced motion with editable layers in a dedicated... | [kumrw](https://daskydesign.gumroad.com/l/kumrw) |
| 104 | EPIK RIG - Quick Rig + Animation Tools for Games (UE) | ShinGidora | 29.99 | _page unavailable (HTTPError)_ | [njrwka](https://shingidora.gumroad.com/l/njrwka) |
| 105 | Fluid Rig | ComixProd. | free | Latest Version: E2 This rig is designed for Blender, and it will not work in Roblox Studio. Fluid Rig is one of the best ROBLOX package rigs you can find for... | [iinfw](https://comixproductions.gumroad.com/l/iinfw) |
| 106 | Free Low Poly 3D Character - Juliet from Lollipop Chainsaw ( | Crashsune | free | _page unavailable (HTTPError)_ | [inljko](https://crashsune.gumroad.com/l/inljko) |
| 107 | Game Rig Tools (Blender Addon) - game-ready rigs in seconds | Todor - cgdive.com | free | _page unavailable (HTTPError)_ | [OmHCS](https://toshicg.gumroad.com/l/OmHCS) |
| 108 | Ghost Frames — Onion Skinning Plugin for Unreal Engine 5.8 | Aymen Selmi | 14.99 | _page unavailable (HTTPError)_ | [gyubxu](https://kazuyasama.gumroad.com/l/gyubxu) |
| 109 | Glock R6 Roblox Rig for Moon Animator | Nisky | free | Roblox R6 Rig with a Welded and fully animatable Glock 17 designed to be used with Moon Animator. | [yaavw](https://nisky.gumroad.com/l/yaavw) |
| 110 | Gridflow — Procedural Animated Grids | Rajat Subhra | 35.00 | _page unavailable (HTTPError)_ | [wpgzfh](https://rajatsubhra.gumroad.com/l/wpgzfh) |
| 111 | Happy Birthday Grimace! (Animation File + Animation Timelaps | Paribes | 10.00 | _page unavailable (HTTPError)_ | [nbbxnn](https://paribes.gumroad.com/l/nbbxnn) |
| 112 | Hazem Rig | ComixProd. | 3.00 | This is the rig I made when making the "How To Make A Roblox Rig" tutorial series. If you want to explore what I made and find out more about how the rig... | [ppwik](https://comixproductions.gumroad.com/l/ppwik) |
| 113 | Houdini Animation Sequencer | bereg | 25.00 | _page unavailable (HTTPError)_ | [wyaanb](https://bereg.gumroad.com/l/wyaanb) |
| 114 | How To Design an Anime Inventory UI (Tutorial) | gfxcomet | 6.00 | _page unavailable (HTTPError)_ | [tceqo](https://gfxcomet.gumroad.com/l/tceqo) |
| 115 | How to Design An Anime Units UI in Roblox Studio | gfxcomet | 6.00 | _page unavailable (HTTPError)_ | [vjvcdvq](https://gfxcomet.gumroad.com/l/vjvcdvq) |
| 116 | HP Art Toolset: Facial Character Rigging for Maya | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [mqrebc](https://hparttoolset.gumroad.com/l/mqrebc) |
| 117 | HP Art Toolset: Fast Character Rigging for Maya | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [bmstj](https://hparttoolset.gumroad.com/l/bmstj) |
| 118 | i5K Rig | ComixProd. | free | _page unavailable (HTTPError)_ | [obfij](https://comixproductions.gumroad.com/l/obfij) |
| 119 | IK Grab | normalizedcrow | 12.00 | _page unavailable (HTTPError)_ | [karln](https://normalizedcrow.gumroad.com/l/karln) |
| 120 | Industrial Sci-Fi and Modular Oil Rig | Sierra Division | 179.00 | _page unavailable (HTTPError)_ | [ikobf](https://sierradivision.gumroad.com/l/ikobf) |
| 121 | KTR - E.V.A. Suit from Dead Space RIG for Jerry | KTR | 22.00 | _page unavailable (HTTPError)_ | [hiwpa](https://kotyor.gumroad.com/l/hiwpa) |
| 122 | Launch Control  //  Auto Car Rig | Daniel Vesterbaek | 59.00 | _page unavailable (HTTPError)_ | [orzsz](https://danielvesterbaek.gumroad.com/l/orzsz) |
| 123 | Let’s learn ANIMATED CHARACTER  CREATION IN 3D | Ram@Crossmind | 34.30 | _page unavailable (HTTPError)_ | [gjpami](https://crossmindstudio.gumroad.com/l/gjpami) |
| 124 | Magma Rig (Blender 3.4+) | Paribes | free | This rig is a rig from a character in Roblox called "The Magma Fiend" including features like: - Brightness control - Magma Fiend's color - Fancy Feet on... | [embpw](https://paribes.gumroad.com/l/embpw) |
| 125 | Marik / Male / PC + Quest + Opti / VRCFT & VRCFury | Heartmarksman | 35.00 | _page unavailable (HTTPError)_ | [zuvneh](https://heartmarksman.gumroad.com/l/zuvneh) |
| 126 | Mechanical Rigging in Blender - A Beginner Course 🦾 | Niko | 19.90 | _page unavailable (HTTPError)_ | [zecxxb](https://demnikoart.gumroad.com/l/zecxxb) |
| 127 | MHFRT - Auto Facial Rig & Auto Retopology | Souhail Ninia | 24.99 | _page unavailable (HTTPError)_ | [pzqmlw](https://souhailninia.gumroad.com/l/pzqmlw) |
| 128 | Mixamo Rig 5 | Knit Motion | 5.00 | _page unavailable (HTTPError)_ | [fjidu](https://knitmotion.gumroad.com/l/fjidu) |
| 129 | Moon Animator 2 Plugin | kai | free | This was originally a paid plugin but its free to get here:) Best Roblox Studio animating plugin out there | [bbsmm](https://realestkai.gumroad.com/l/bbsmm) |
| 130 | Muscle Anatomy  - Ecorche Rigged Set | Alex Lashko | 99.00 | _page unavailable (HTTPError)_ | [fffeg](https://alexlashko.gumroad.com/l/fffeg) |
| 131 | Painterly + Animately Bundle DEAL! | Doughy Animation Studi | 34.50 | _page unavailable (HTTPError)_ | [qrdvwb](https://doughyanimation.gumroad.com/l/qrdvwb) |
| 132 | Physics animation (Plugin for Figma) | DAVV | 39.00 | _page unavailable (HTTPError)_ | [pfabo](https://davvstore.gumroad.com/l/pfabo) |
| 133 | PinRig / After Effects Plugin | What? Studio | free | _page unavailable (HTTPError)_ | [rvcux](https://whatstudio.gumroad.com/l/rvcux) |
| 134 | Profine's Roblox Toy Rig EDIT (Blender 4.0+) | Paribes | free | Profine made a Roblox toy rig a while back, I made a simple edit which has bone shapes and allat (this was mainly for me to have a better animating experience). | [udkwsf](https://paribes.gumroad.com/l/udkwsf) |
| 135 | Quick Start To Blender Animation: Professional Techniques An | VFX Grace | 198.00 | _page unavailable (HTTPError)_ | [kavusr](https://vfxgrace.gumroad.com/l/kavusr) |
| 136 | R15 Roblox ANIMATION Rig (Blender -> Roblox Studio) | Paribes | free | A rig for Blender 3D to export to Roblox Studio! Settings HeadTarget HeadTarget Parent Torso IK Arm/Leg Settings IK/FK Switch Bone Layers (IK/FK) Fancy... | [zmyfl](https://paribes.gumroad.com/l/zmyfl) |
| 137 | R15 Roblox Starter Rigs (TEMPORARY) | Paribes | free | while waiting for the next starter rigs update, use these rigs if you need r15 here's the description of starter rigs: Introducing Roblox Starter Rigs, which... | [jjhtt](https://paribes.gumroad.com/l/jjhtt) |
| 138 | Rich Rig (Blender 3.4+) | Paribes | free | _page unavailable (HTTPError)_ | [xsgzm](https://paribes.gumroad.com/l/xsgzm) |
| 139 | Roblox Blocky Finger Rig (Blender 4.0+) | Paribes | free | fingies NOTE: FACE RIG IS NOT INCLUDED, THAT IS AEPBR EXCLUSIVE | [fpbjgc](https://paribes.gumroad.com/l/fpbjgc) |
| 140 | Roblox Blocky Rig / C4D R20+ | Chastling | 1.50 | Available on Gumroad | [ahkbz](https://chastling.gumroad.com/l/ahkbz) |
| 141 | Roblox Fat Rig (4.0+) | Paribes | free | _no description in metadata_ | [jiojiw](https://paribes.gumroad.com/l/jiojiw) |
| 142 | Roblox Football Rig V1 (Blender 4.2+) | Paribes | 10.00 | NOTE: redistributing or reselling the rigs, even if modified or at a price, is PROHIBITED. Muscle System The rig contains a special muscle system that is... | [ifhke](https://paribes.gumroad.com/l/ifhke) |
| 143 | Roblox Multipurpose Cloth Rig (4.5+) | Paribes | free | Features: Classic Cloth Modification - This modification is a top-tier cloth simulation rig that bakes the shirt, providing realistic cloth physics... | [hwthor](https://paribes.gumroad.com/l/hwthor) |
| 144 | Roblox Rig Vault (Blender 4.0+) | Paribes | free | Introducing Roblox Rig Vault! Roblox Rig Vault (RRV) is a unique Blender rig pack and addon made by Roblox rigging innovators ChillingParibes and Comix... | [htzgj](https://paribes.gumroad.com/l/htzgj) |
| 145 | Roblox Rigs Suite | ComixProd. | free | Thanks to @BricksBree, @ChillingParibes, @MrSonicTeam, @MXFlamez, @Koth for beta testing this! I would really appreciate it if you donated, it's taken me... | [xpqyw](https://comixproductions.gumroad.com/l/xpqyw) |
| 146 | Roblox Starter Rigs (Blender 3.4+) | Softy | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [ytmdjz](https://softgb.gumroad.com/l/ytmdjz) |
| 147 | Roblox Starter Rigs (Blender 3.4+) | Paribes | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [pblgq](https://paribes.gumroad.com/l/pblgq) |
| 148 | Roblox Starter Rigs 1.0 MODDED | Paribes | free | Starter rigs by SoftGB & ChillingParibes Modified rigs by imbob02 (seamless boy rigs) R15 rig by BaconofVibes Compiled by Malakai_GFX If you need rigs... | [xbrdsa](https://paribes.gumroad.com/l/xbrdsa) |
| 149 | Roblox Woman Blocky Legs Rig (Blender 4.0+) | Paribes | free | If you need rigs, contact me on Discord (chillingparibes)! https://discord.com/invite/Mc5PdfZnBd NOTE: redistributing or reselling the rigs, even if modified... | [oqjvxf](https://paribes.gumroad.com/l/oqjvxf) |
| 150 | Scene Auditor Pro — Analyze, Clean & Optimize Blender Scenes | Chowdhury Tarul Ahsan | 15.00 | _page unavailable (HTTPError)_ | [yvydx](https://tarulahsanbd.gumroad.com/l/yvydx) |
| 151 | Seraph Wings — Animated Six-Wing VRChat Accessory / PCVR | KuroLabs | 15.00 | _page unavailable (HTTPError)_ | [fetsbo](https://rajcu.gumroad.com/l/fetsbo) |
| 152 | SimpleAnime - Fast Anime / Retro Texturing | Nhance School | 19.00 | SimpleAnime - Easy Anime / Retro texturing Create stunning texturing results on your 3D Models + speed up workflow with SimpleAnime filter🎨 SimpleAnime was... | [dptffu](https://nhanceschool.gumroad.com/l/dptffu) |
| 153 | Spider-Man Roblox Rig (4.4+) | Paribes | free | credits to @imbob02 , @BallzyGFX and @xmavster on Twitter for making this Starter Rigs mod! | [ogunp](https://paribes.gumroad.com/l/ogunp) |
| 154 | Stadium Spectators: High Performance Stadium Crowds for Unre | RT ArtFast | 150.00 | _page unavailable (HTTPError)_ | [oannzl](https://tartfast.gumroad.com/l/oannzl) |
| 155 | Stylized Character Modeling for Animation | Stephen Anderson | 100.00 | Stylized Character Modeling for Animation is all about character design and application in production modeling for the animation pipeline. This self-paced... | [hqtmF](https://smaartist.gumroad.com/l/hqtmF) |
| 156 | SuperRoblox (Roblox Rig) | ComixProd. | free | _page unavailable (HTTPError)_ | [jFnRyz](https://comixproductions.gumroad.com/l/jFnRyz) |
| 157 | Talia + Adam - Maya Rig Bundle | Red Crow Studio | 68.00 | _page unavailable (HTTPError)_ | [xfplhw](https://manuelaf.gumroad.com/l/xfplhw) |
| 158 | Texter - Text Animation Tool for Blender | Graffinity | free | _page unavailable (HTTPError)_ | [tquro](https://graffinity3d.gumroad.com/l/tquro) |
| 159 | The Ultimate Guide to Blender 3D Rigging and Animation | 3D Tudor | 11.25 | _page unavailable (HTTPError)_ | [irfmu](https://3dtudor.gumroad.com/l/irfmu) |
| 160 | Throw Food For Animals Template | ROKITS | 9.99 | Throw Food for Animals \| Roblox Template Train your strength, throw food farther, and collect animals to build your income! What’s Included 🐾 40 collectible... | [pyycl](https://rokits.gumroad.com/l/pyycl) |
| 161 | UI Animator Pro / After Effects Plugin | What? Studio | free | _page unavailable (HTTPError)_ | [xariqf](https://whatstudio.gumroad.com/l/xariqf) |
| 162 | Ultimate 2D FX Explosions for Animators & Devs | DucVu FX | 20.00 | _page unavailable (HTTPError)_ | [rfhalq](https://ducvu.gumroad.com/l/rfhalq) |
| 163 | Ultimate 2D FX Fire Animation Pack for Creators & Devs | DucVu FX | 20.00 | _page unavailable (HTTPError)_ | [menshz](https://ducvu.gumroad.com/l/menshz) |
| 164 | Ultimate Roblox Rig | MattRBX | 5.00 | IF YOU DIDN'T RECIEVE THE PRODUCT OR HAVE SIMILAR ISSUES JOIN THE DISCORD SERVER BELOW !! Support Server: https://discord.gg/DvK73fgEka Ultimate Rig Premium... | [lnldn](https://mattrbx.gumroad.com/l/lnldn) |
| 165 | Ultimate Weapon Sweep VFX !! [Houdini 19-20 / Niagara UE Cou | Tristan Gybels | 30.00 | This course tackles one of the most common problems but yet unheard of solutions for creating incredibly precise weapon sweep VFX. Unlike similar tutorials... | [qbfhe](https://tristangybels.gumroad.com/l/qbfhe) |
| 166 | Unreal Engine 5 Massive 250-Piece Modular Mega - Kitbash Imm | 3D Tudor | 18.00 | _page unavailable (HTTPError)_ | [rapdi](https://3dtudor.gumroad.com/l/rapdi) |
| 167 | Weight Scatter - (Plugin) | MrQuaxkers | 4.99 | Weight based object scattering in roblox studio. | [vhxkmj](https://mrquaxkers.gumroad.com/l/vhxkmj) |
| 168 | Worm Host Animation | Satch Nomad | 20.00 | This is a custom animation that can be easily transfered over to the custom character model of your choice. the "Worm Host", is a 3D combat/ability splash... | [racij](https://n5studios.gumroad.com/l/racij) |
| 169 | Zazar - Rigged 3D Lizard for Blender | Rakenval | 60.00 | _page unavailable (HTTPError)_ | [ynfspb](https://rakenval.gumroad.com/l/ynfspb) |
| 170 | ⚽ Roblox Football/Soccer Rigs (Kit, Shoes, Trophies, ...) | Paribes | free | credit: @ChillingParibes - the rig @SoftGB - HD Faces @imbob02 - modified seamless boy rig vansire - football stuff on the rig and the boot textures... | [ovwtcn](https://paribes.gumroad.com/l/ovwtcn) |
| 171 | 🎮 Legendary Sky Champion Rig (Roblox: The Games) | Paribes | free | "Defeat" will be forever erased from your vocabulary. A brand new rig for the package Roblox released For Blender 4.2+ (probably works for minimum 4.0+) | [yowflf](https://paribes.gumroad.com/l/yowflf) |
| 172 | 🏃 Roblox Animation Starter Pack | Paribes | free | _page unavailable (HTTPError)_ | [knclku](https://paribes.gumroad.com/l/knclku) |
| 173 | 🤖 AEPBR Roblox Rig (BETA) | Paribes | free | 🤖 STILL IN BETA!! Features it has so far: ☑️ Customisable face rig Customisable Eye Color Hideable Parts Face controls Mouth Sync Control Blink Control Teeth... | [wvyryw](https://paribes.gumroad.com/l/wvyryw) |
| 174 | 🧟 Roblox Zombie Rig (Blender 4.0+) | Paribes | free | zombie PS: The best works of Softy and STAR's contest will end up on this page as well! EDIT: Winning GFX has been added, made by @vanziervh If you need... | [quhwki](https://paribes.gumroad.com/l/quhwki) |

## Modeling, mesh & procedural (30)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 175 | [Addon]MESHmachine | machin3 | 44.99 | _page unavailable (HTTPError)_ | [Gwgt](https://machin3.gumroad.com/l/Gwgt) |
| 176 | CGE Sculpting Tool for Maya | CGElementary | 78.40 | _page unavailable (HTTPError)_ | [lkvikqt](https://cgelementary.gumroad.com/l/lkvikqt) |
| 177 | Cloud Creator / Blender Geometry Nodes Tool | Adrien Latran | free | _page unavailable (HTTPError)_ | [qcppwq](https://adrienltn.gumroad.com/l/qcppwq) |
| 178 | Cobweb Generator Pro | Jose Leon Molfino | free | Houdini Cobweb Generator Pro - It generates cobwebs procedurally from a collider geometry, from your own straight lines, or both. This is a full rewrite of... | [zbrsd](https://cmolfino.gumroad.com/l/zbrsd) |
| 179 | Extra Nodes for Geometry Nodes | 3dsinghvfx | free | _page unavailable (HTTPError)_ | [aaxrtj](https://3dsinghvfx.gumroad.com/l/aaxrtj) |
| 180 | EzyTopo - Retopology tool for Maya | Justin Kirkwood | 16.99 | _page unavailable (HTTPError)_ | [otyqu](https://justinkirkwood.gumroad.com/l/otyqu) |
| 181 | Hiddenfy 6 — Hard-Surface Armor, IMM system, Tactical Cloth  | Daniel Arcos Escobar | 10.50 | _page unavailable (HTTPError)_ | [ebbxj](https://darksurfacetv.gumroad.com/l/ebbxj) |
| 182 | Houdini Tutorial Procedural Pillar Generation | Radu Cius | 45.00 | _page unavailable (HTTPError)_ | [btbwd](https://rart.gumroad.com/l/btbwd) |
| 183 | MEDUSA NODES - Procedural Hair System for Blender (Beta) | Irakli Kupunia | 15.00 | _page unavailable (HTTPError)_ | [XEzSy](https://ikakupa.gumroad.com/l/XEzSy) |
| 184 | PatchGAP - Plasticity Retopology tool for Blender | Andrei Bezgodov | 35.00 | _page unavailable (HTTPError)_ | [ildlkt](https://bezgod.gumroad.com/l/ildlkt) |
| 185 | Procedural City Generator for Houdini / by MrShark (UPDATED  | Mr.Shark | 15.00 | _page unavailable (HTTPError)_ | [bpdiq](https://mrshark.gumroad.com/l/bpdiq) |
| 186 | Procedural Damage + Imperfections (Blender Geometry-Nodes) | Alex Martinelli | free | _page unavailable (HTTPError)_ | [tkbjk](https://sagado.gumroad.com/l/tkbjk) |
| 187 | Procedural Grid (Blender 3+, 4+) | Mina Pêcheux | 3.00 | _page unavailable (HTTPError)_ | [okeizj](https://mpecheux.gumroad.com/l/okeizj) |
| 188 | Procedural Pipes & Roads (Godot 4) | Mina Pêcheux | 7.00 | _page unavailable (HTTPError)_ | [bmobcx](https://mpecheux.gumroad.com/l/bmobcx) |
| 189 | Procedural Planet (Blender 4+) | Mina Pêcheux | 9.00 | _page unavailable (HTTPError)_ | [gfhysx](https://mpecheux.gumroad.com/l/gfhysx) |
| 190 | Procedural Sky System - Blender Addon | Other Realms | 15.00 | _page unavailable (HTTPError)_ | [sogyzv](https://otrealms.gumroad.com/l/sogyzv) |
| 191 | Procedural Thunder | HeyYo | 7.00 | _page unavailable (HTTPError)_ | [mycyh](https://heyyohanashima.gumroad.com/l/mycyh) |
| 192 | Procedural Urban Building Generator for Houdini (HDA) | Radu Cius | 39.00 | _page unavailable (HTTPError)_ | [civgek](https://rart.gumroad.com/l/civgek) |
| 193 | Project Damage / Procedural Destruction Toolkit [Blender Add | Lazy3D Blender | free | _page unavailable (HTTPError)_ | [wwwauu](https://lazy3d.gumroad.com/l/wwwauu) |
| 194 | Quadremsh Tools for Blender — Fast Quad Remeshing & Retopolo | SyncTools Pro — Cross- | free | _page unavailable (HTTPError)_ | [svwvny](https://synctools.gumroad.com/l/svwvny) |
| 195 | Spall: Procedural Damage for Blender | Alberto Cordero | 29.00 | _page unavailable (HTTPError)_ | [ttqrme](https://albertocgart.gumroad.com/l/ttqrme) |
| 196 | SpiralForge – Procedural Galaxy Builder for Blender | Petr Chekushkin | free | _page unavailable (HTTPError)_ | [qlafqt](https://astrodemiurge.gumroad.com/l/qlafqt) |
| 197 | Stacking Stones — Procedural Rock Walls & Ruins in Houdini ( | Hugo Beyer | 29.00 | _page unavailable (HTTPError)_ | [jsepsh](https://hugobeyer.gumroad.com/l/jsepsh) |
| 198 | The Big Nodebook: A Geometry Nodes Guide | MTR Animation | 19.99 | _page unavailable (HTTPError)_ | [hzsqw](https://mtranimationgumroad.gumroad.com/l/hzsqw) |
| 199 | Tutorial series - Procedural Cliffs with SideFX houdini | adrienlambert | 10.00 | _page unavailable (HTTPError)_ | [pYaGH](https://adrienlambert.gumroad.com/l/pYaGH) |
| 200 | Unity VFX Graph：Mesh Particle Fragments | Eric VFX Studio | 8.99 | _page unavailable (HTTPError)_ | [udgno](https://raywang4.gumroad.com/l/udgno) |
| 201 | Unity VFX Graph：Particle Character (Skinned Mesh) | Eric VFX Studio | 9.99 | _page unavailable (HTTPError)_ | [cwkeg](https://raywang4.gumroad.com/l/cwkeg) |
| 202 | Unreal Engine Procedural Damage Toolset | Hoj Dee | 19.99 | _page unavailable (HTTPError)_ | [vsykco](https://hojdee.gumroad.com/l/vsykco) |
| 203 | Unreal Engine Procedural Snow Toolset | Hoj Dee | 19.99 | _page unavailable (HTTPError)_ | [jixnf](https://hojdee.gumroad.com/l/jixnf) |
| 204 | UV Unfoldr – A Modern UV Editor for 3ds Max | Sargis Ter-Grigoryan | 39.00 | _page unavailable (HTTPError)_ | [nnwzju](https://sargisstg.gumroad.com/l/nnwzju) |

## VFX & simulation (36)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 205 | 200 FX Alpha VFX Asset Library | Comp Academy | 150.00 | _page unavailable (HTTPError)_ | [bgnny](https://compacademy.gumroad.com/l/bgnny) |
| 206 | Background Birds - Drag-and-Drop Niagara Bird System for Unr | Josh Toonen | 25.00 | _page unavailable (HTTPError)_ | [yyrmy](https://unrealforvfx.gumroad.com/l/yyrmy) |
| 207 | Blood VFX - Unreal Engine | Vefects - Realtime VFX | 57.99 | _page unavailable (HTTPError)_ | [qmvvfa](https://vefects.gumroad.com/l/qmvvfa) |
| 208 | Chain Simulation in Niagara - Create Mario's Chain Chomp | HeyYo | 7.00 | This is a Chain Simulation Niagara asset. I created Mario's Chain Chomp as an example to show how the chain simulation works. Both ends of the chain are... | [noiblu](https://heyyohanashima.gumroad.com/l/noiblu) |
| 209 | Fire Slash VFX | HeyYo | 15.00 | I made Fire Slash VFX as my personal work. I provide the whole UE data of this VFX so that you can explore, study, modify, and utilize the data for any... | [uajdj](https://heyyohanashima.gumroad.com/l/uajdj) |
| 210 | Flux Particle Studio / Blender | R Animation Studios | 29.00 | _page unavailable (HTTPError)_ | [wtgjlc](https://ranimationstudios.gumroad.com/l/wtgjlc) |
| 211 | FUGA - Imagined by Starkim1999 [VFX/VRChat] | Starkim1999 | 25.00 | _page unavailable (HTTPError)_ | [gwsrd](https://starkim1999.gumroad.com/l/gwsrd) |
| 212 | Fumaris — GPU Smoke & Fire Simulation for Blender | Venous_FX | 39.00 | Smoke and fire you can direct while it simulates Watch the simulation run in the Blender viewport, lit by your scene, and change it while it plays. When the... | [sszyf](https://venousfx.gumroad.com/l/sszyf) |
| 213 | GPU Fluid Simulation / No Kinect Required | Irina.ae | 5.00 | _page unavailable (HTTPError)_ | [jelqf](https://irinaught.gumroad.com/l/jelqf) |
| 214 | Magic Spell VFX System | Digital Dungeon Assets | 124.99 | _page unavailable (HTTPError)_ | [ozbpme](https://dungeonforge.gumroad.com/l/ozbpme) |
| 215 | MPMStudio Solver - Particle simulation plugin for C4D & BLEN | RiverExtend | 35.00 | _page unavailable (HTTPError)_ | [kwttbt](https://riverextend.gumroad.com/l/kwttbt) |
| 216 | Next Gen Destruction Toolkit for Unreal Engine 5 | Kristian Kebbe | 44.99 | _page unavailable (HTTPError)_ | [fjpon](https://lucendev.gumroad.com/l/fjpon) |
| 217 | PCOPs - GPU Enabled Particle Simulation Tools in Houdini | Inside The Mind | 35.00 | _page unavailable (HTTPError)_ | [kpysmy](https://insidethemindspace.gumroad.com/l/kpysmy) |
| 218 | Pro Particles - Advanced Blender Particle System Add-on v5 | Cg-Flow | 51.35 | _page unavailable (HTTPError)_ | [qzaiz](https://cgflow.gumroad.com/l/qzaiz) |
| 219 | Standing Fire [Medium Scale] VFX Asset Bundle [x10] | Ben Harker | VFX | 15.00 | _page unavailable (HTTPError)_ | [bnizsn](https://benharkervfx.gumroad.com/l/bnizsn) |
| 220 | Unity VFX Graph - Level Up Effect | Gabriel Aguiar Prod | 5.00 | _page unavailable (HTTPError)_ | [alchf](https://gabrielaguiarprod1.gumroad.com/l/alchf) |
| 221 | Unity VFX Graph - Muzzle Effects Vol. 1 | Gabriel Aguiar Prod | 10.00 | _page unavailable (HTTPError)_ | [lkcfx](https://gabrielaguiarprod1.gumroad.com/l/lkcfx) |
| 222 | Unity VFX Graph - Stylized Laser Beams Vol. 1 | Gabriel Aguiar Prod | 10.00 | _page unavailable (HTTPError)_ | [jrdekb](https://gabrielaguiarprod1.gumroad.com/l/jrdekb) |
| 223 | Unity VFX Graph - Weapon Effects Vol. 1 | Gabriel Aguiar Prod | 10.00 | _page unavailable (HTTPError)_ | [mmckxd](https://gabrielaguiarprod1.gumroad.com/l/mmckxd) |
| 224 | Unity VFX Graph：Attractor Force and Particle Trail effect | Eric VFX Studio | 8.00 | _page unavailable (HTTPError)_ | [kbffp](https://raywang4.gumroad.com/l/kbffp) |
| 225 | Unity VFX Graph：Disturbed Image Particles | Eric VFX Studio | 9.99 | Particle picture effects created using Unity VFX Graph, You can add pictures yourself, modify particle size, color, jitter amplitude, etc. Detailed... | [wzdfe](https://raywang4.gumroad.com/l/wzdfe) |
| 226 | Unity VFX Graph：Galaxy and Meteor | Eric VFX Studio | 7.99 | _page unavailable (HTTPError)_ | [hubvqv](https://raywang4.gumroad.com/l/hubvqv) |
| 227 | Unity VFX Graph：Image Fireworks | Eric VFX Studio | 8.99 | _page unavailable (HTTPError)_ | [ejzku](https://raywang4.gumroad.com/l/ejzku) |
| 228 | Unity VFX Graph：Particle shaping application(SDF) | Eric VFX Studio | 9.00 | _page unavailable (HTTPError)_ | [jhrat](https://raywang4.gumroad.com/l/jhrat) |
| 229 | Unity VFX Graph：Particles Attraction | Eric VFX Studio | 8.00 | Made using Unity VFX Graph so that particles can follow the target point. You can modify the particle size, color, fluttering direction, etc. by yourself... | [qiqwkbw](https://raywang4.gumroad.com/l/qiqwkbw) |
| 230 | Unity VFX Graph：Post-it(Particles aggregate into models) | Eric VFX Studio | 7.99 | _page unavailable (HTTPError)_ | [fjnqc](https://raywang4.gumroad.com/l/fjnqc) |
| 231 | Unity VFX Graph：SDF Model Particle Deformation | Eric VFX Studio | 7.99 | _page unavailable (HTTPError)_ | [mcstjd](https://raywang4.gumroad.com/l/mcstjd) |
| 232 | Unity VFX Graph：Use SDF to make model particle effects | Eric VFX Studio | 9.99 | Made using Unity VFX Graph, with the model special effects generated by the SDF function, you can change the model to create different effects. Detailed... | [kehpsj](https://raywang4.gumroad.com/l/kehpsj) |
| 233 | Unreal 5 Advanced Niagara | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [wkvru](https://tharlevfx.gumroad.com/l/wkvru) |
| 234 | Unreal 5 Intro to Niagara | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [yvgfg](https://tharlevfx.gumroad.com/l/yvgfg) |
| 235 | Unreal 5 Niagara Bundle | tharlevfx | 125.00 | _page unavailable (HTTPError)_ | [czhuq](https://tharlevfx.gumroad.com/l/czhuq) |
| 236 | Unreal 5 Niagara Sim Stages | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [ufmqh](https://tharlevfx.gumroad.com/l/ufmqh) |
| 237 | Unreal Engine 4.22 Niagara Dissolution Effect | ArtHiteca | 15.00 | _page unavailable (HTTPError)_ | [AzoNY](https://arthiteca.gumroad.com/l/AzoNY) |
| 238 | Unreal Engine 4.22 Niagara Test Examples #1 | ArtHiteca | 20.00 | _page unavailable (HTTPError)_ | [SvcVn](https://arthiteca.gumroad.com/l/SvcVn) |
| 239 | VFXGen — Stylized VFX Texture Editor | ChunHu | 29.99 | _page unavailable (HTTPError)_ | [frhhpp](https://chunhuvfx.gumroad.com/l/frhhpp) |
| 240 | WebGL Magnetic Field: Interactive Particle Engine for Framer | Creative Apes | 8.00 | _page unavailable (HTTPError)_ | [dqgfpw](https://creativeapes.gumroad.com/l/dqgfpw) |

## Engine tooling: Unity / Godot / Unreal (37)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 241 | 1900s Office (Unreal Engine) | Leartes Studios | 69.99 | _page unavailable (HTTPError)_ | [zjvzpa](https://leartesstudios.gumroad.com/l/zjvzpa) |
| 242 | 2D Modern Pack - SPUM Premium AddOn (Unity Addition) | SOONSOON | 19.99 | _page unavailable (HTTPError)_ | [sbdqj](https://soonsoon.gumroad.com/l/sbdqj) |
| 243 | Asset Downgrader for Unreal Engine 5 | Ciprian Stanciu | 34.99 | _page unavailable (HTTPError)_ | [igbejz](https://relativegames.gumroad.com/l/igbejz) |
| 244 | AWS GameLift Client Plugin by eelDev for Unreal Engine | eelDev | 45.00 | _page unavailable (HTTPError)_ | [fbozz](https://eeldev.gumroad.com/l/fbozz) |
| 245 | Blender Godot 4 Pipeline Add-on | Michael Burt | 5.00 | _page unavailable (HTTPError)_ | [alpunq](https://michaeljared.gumroad.com/l/alpunq) |
| 246 | Blender Godot Suffixes (Addon) by Suzuka Ka | Suzuka Ka | 2.00 | _page unavailable (HTTPError)_ | [yvzxt](https://orb91.gumroad.com/l/yvzxt) |
| 247 | Blender To Game Engine (Unity, Unreal & Godot) Bundle | karan@b3dhub | 42.50 | _page unavailable (HTTPError)_ | [najqn](https://b3dhub.gumroad.com/l/najqn) |
| 248 | Blender to Unreal Engine 5: Build a Stylized Greek Island En | 3D Tudor | 11.25 | _page unavailable (HTTPError)_ | [vmbyjm](https://3dtudor.gumroad.com/l/vmbyjm) |
| 249 | Blender to Unreal Engine 5: Playable Stylized Turret | 3D Tudor | 11.25 | _page unavailable (HTTPError)_ | [whfxr](https://3dtudor.gumroad.com/l/whfxr) |
| 250 | Cloud Forge Complete 1.4.3 Unreal Engine 5.3 - 5.6 - VDB Clo | Arghanion's Puzzlebox | 24.99 | _page unavailable (HTTPError)_ | [fkjic](https://arghanion.gumroad.com/l/fkjic) |
| 251 | Cloud Forge Vol 2 - Unreal Engine 5.3 - 5.6 - VDB Clouds | Arghanion's Puzzlebox | 10.99 | _page unavailable (HTTPError)_ | [fxwqc](https://arghanion.gumroad.com/l/fxwqc) |
| 252 | Cloud Forge Volume 3 - Unreal Engine 5.3 - 5.6 - VDB Clouds | Arghanion's Puzzlebox | 12.99 | _page unavailable (HTTPError)_ | [plicg](https://arghanion.gumroad.com/l/plicg) |
| 253 | Collision Splitter for Maya -> Unreal Engine | Honey3D | free | _page unavailable (HTTPError)_ | [atvjq](https://raditsys.gumroad.com/l/atvjq) |
| 254 | Complete Masterclass for Creating Cinematic Games in Unreal  | CGDealers | 39.90 | _page unavailable (HTTPError)_ | [nluov](https://cgdealers.gumroad.com/l/nluov) |
| 255 | Creating a metro train interior in Unreal Engine 5 | FastTrack Tutorials | 29.99 | _page unavailable (HTTPError)_ | [coMXC](https://fasttracktutorials.gumroad.com/l/coMXC) |
| 256 | EOSCore (Epic Online Services) Plugin for Unreal Engine | eelDev | 65.00 | _page unavailable (HTTPError)_ | [aoGtA](https://eeldev.gumroad.com/l/aoGtA) |
| 257 | Ezreal Slashes Vol.1 - Unreal Engine | Gabriel Aguiar Prod | 12.00 | _page unavailable (HTTPError)_ | [yizfn](https://gabrielaguiarprod1.gumroad.com/l/yizfn) |
| 258 | Flipbook Tool - Looping flipbook textures for Unreal Engine | henlo | free | _page unavailable (HTTPError)_ | [SQnwg](https://henlo.gumroad.com/l/SQnwg) |
| 259 | French Quarter Street Environment (Unreal Engine) | Leartes Studios | 69.99 | _page unavailable (HTTPError)_ | [homxva](https://leartesstudios.gumroad.com/l/homxva) |
| 260 | Godot 4 AutoSave Plugin — Periodic & On-Event Save System (G | OccaSoftware | free | _page unavailable (HTTPError)_ | [ogxgd](https://occasoftware.gumroad.com/l/ogxgd) |
| 261 | How to make a movie in Unreal Engine 5 Beginners Edition (Up | JSFILMZ | 19.99 | _page unavailable (HTTPError)_ | [mdwrk](https://jsfilmz.gumroad.com/l/mdwrk) |
| 262 | NameFrame 1.0 for Unreal Engine 5.8 | NameFrame | 149.00 | _page unavailable (HTTPError)_ | [vuaozu](https://nameframe.gumroad.com/l/vuaozu) |
| 263 | RevoltGPT Plugin for Unreal Engine 5 | RevoltGPT | 79.99 | _page unavailable (HTTPError)_ | [jbgunp](https://revoltgpt.gumroad.com/l/jbgunp) |
| 264 | Sentari AI Assistant - Copilot & MCP for Unreal Engine 5 | Sentari Digital | 99.00 | BUILD INSIDE UNREAL BY DESCRIBING WHAT YOU WANT Sentari AI Assistant installs into the Unreal Editor as a panel you talk to. Describe what you need in plain... | [wlwvbl](https://sentaridigital.gumroad.com/l/wlwvbl) |
| 265 | Star Collapse Space Scene for Unreal Engine 5.1 - 5.6 | Arghanion's Puzzlebox | 15.00 | _page unavailable (HTTPError)_ | [ormou](https://arghanion.gumroad.com/l/ormou) |
| 266 | Unreal 5 Tech Art Bundle | tharlevfx | 225.00 | _page unavailable (HTTPError)_ | [yilqk](https://tharlevfx.gumroad.com/l/yilqk) |
| 267 | Unreal Engine - Shrubland 4x4km Landscape Environment ( Arid | Freshcan 3D | 44.00 | _page unavailable (HTTPError)_ | [owybs](https://freshcan.gumroad.com/l/owybs) |
| 268 | Unreal Engine 5 - Ultimate Courses & Plugins Bundle | CGDealers | 49.99 | _page unavailable (HTTPError)_ | [fyiyw](https://cgdealers.gumroad.com/l/fyiyw) |
| 269 | Unreal Engine Cosmic Forge Bundle 30% OFF - Standard License | Arghanion's Puzzlebox | 32.32 | _page unavailable (HTTPError)_ | [eskpl](https://arghanion.gumroad.com/l/eskpl) |
| 270 | Unreal Engine Film School (Course) | Virtual Production Ins | 199.00 | _page unavailable (HTTPError)_ | [mszovu](https://vpinsider.gumroad.com/l/mszovu) |
| 271 | Unreal Engine Jumpstart (Tutorial) | Fabio Montorzi | 34.00 | _page unavailable (HTTPError)_ | [cqgrq](https://fabiomontorzi.gumroad.com/l/cqgrq) |
| 272 | Unreal Engine Space Bundle - Standard Licence - 40% Savings! | Arghanion's Puzzlebox | 22.79 | Elevate Your Unreal Engine Projects with Our Exclusive 3D Asset Bundle! Transform your Unreal Engine creations with this exclusive bundle featuring four... | [qvjbb](https://arghanion.gumroad.com/l/qvjbb) |
| 273 | Unreal Engine to 3ds Max Biped Tool | Mark Blosser | 15.00 | _page unavailable (HTTPError)_ | [iaxic](https://markblosser.gumroad.com/l/iaxic) |
| 274 | Unreal Exporter - Blender Addon | Kostia Perry | free | _page unavailable (HTTPError)_ | [perhw](https://tarmunds.gumroad.com/l/perhw) |
| 275 | Unreal Self Balance 1.2 Project - UE5.6 Self Balancing Ragdo | CodeFloat | 49.99 | _page unavailable (HTTPError)_ | [ytjyu](https://codefloat.gumroad.com/l/ytjyu) |
| 276 | Utu Plugin - Unity to Unreal Project Converter | Alex Quevillon | 30.00 | _page unavailable (HTTPError)_ | [eamdpu](https://alexquevillon.gumroad.com/l/eamdpu) |
| 277 | xGen2UE Script - Export Alembic Hair from Maya xGen to Unrea | RealTime Hair | 15.00 | _page unavailable (HTTPError)_ | [clqdlu](https://realtimehair.gumroad.com/l/clqdlu) |

## Roblox tools (21)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 278 | [ NEW ] Roblox The Armory OP Script Hub / Crate ESP, Human E | Rixtreat | 0.99 | _page unavailable (HTTPError)_ | [dpdhro](https://rixtreat.gumroad.com/l/dpdhro) |
| 279 | [Roblox Studio]Advanced  (Suspicious)  NPC System | TheTomato | free | _page unavailable (HTTPError)_ | [hfmpt](https://thetomato.gumroad.com/l/hfmpt) |
| 280 | [v1.3] Hash Studios Alcohol Drinks [UdonSharp] [SDK3] | Hash Studios LLC | 49.99 | _page unavailable (HTTPError)_ | [dcggw](https://hashstudiosllc.gumroad.com/l/dcggw) |
| 281 | [‼️ON SALE‼️] Advanced Roblox NPC System | _mosES() | 0.99 | _page unavailable (HTTPError)_ | [ggtge](https://mose5.gumroad.com/l/ggtge) |
| 282 | Advanced Zombie Horde System | Nox | 5.00 | Tired of zombies that stop at the first wall? Elevate your Roblox survival or horror game with our Advanced Horde AI. Inspired by World War Z, this system... | [pdemm](https://noxwen.gumroad.com/l/pdemm) |
| 283 | Car Customization System (Paint, Wheels & More) / Roblox Stu | Nytrix Prime | 6.99 | _page unavailable (HTTPError)_ | [wlqsva](https://nytrixprime4.gumroad.com/l/wlqsva) |
| 284 | Foliage Presets Plugin – Studio License (UE 5.7 and 5.8, up  | levelarttools | 999.00 | STUDIO LICENSE This listing is a Studio License covering up to 15 named users within one company – intended for teams that cannot purchase individual seats... | [pmrma](https://levelarttools.gumroad.com/l/pmrma) |
| 285 | Hair Card Studio (Hair Card Creator Addon for Blender) | PixelicaCG | 11.99 | _page unavailable (HTTPError)_ | [bktxo](https://pixelicacg.gumroad.com/l/bktxo) |
| 286 | R6 ROBLOX REALISTIC MOVEMENT/CAMERA SYSTEM | JUNIS | 9.99 | _page unavailable (HTTPError)_ | [aorzrj](https://clownjunis.gumroad.com/l/aorzrj) |
| 287 | Roblox Advanced Player Data System (Attributes + DataStore) | AB price | 50.00 | _page unavailable (HTTPError)_ | [lprem](https://abprice.gumroad.com/l/lprem) |
| 288 | Roblox Boid System | Tekleed | 15.00 | _page unavailable (HTTPError)_ | [vxmjq](https://tekleed.gumroad.com/l/vxmjq) |
| 289 | Roblox FPS System | Jeynkins | 12.00 | _page unavailable (HTTPError)_ | [gfmdgs](https://jeynkinsrbxlstudios.gumroad.com/l/gfmdgs) |
| 290 | Roblox Jojo Bizarre Incremental Script / Auto Combat, Auto S | Rixtreat | 0.99 | _page unavailable (HTTPError)_ | [nprkf](https://rixtreat.gumroad.com/l/nprkf) |
| 291 | Roblox Ocean System | Tekleed | 200.00 | _page unavailable (HTTPError)_ | [qgvvc](https://tekleed.gumroad.com/l/qgvvc) |
| 292 | Roblox Sorcerer Incremental Script Hub / OP Auto Farm, Auto  | Rixtreat | 0.99 | _page unavailable (HTTPError)_ | [mtujfu](https://rixtreat.gumroad.com/l/mtujfu) |
| 293 | Roblox Studio: Movement system (8 directions) | LionDev | 12.00 | _page unavailable (HTTPError)_ | [cddbt](https://liondev.gumroad.com/l/cddbt) |
| 294 | SmartMonster AI - Dynamic Enemy Pathfinding for Roblox | Harry | 15.00 | _page unavailable (HTTPError)_ | [zwotiv](https://scriptrblx.gumroad.com/l/zwotiv) |
| 295 | Studio Color - (Plugin) | MrQuaxkers | 6.99 | Full coloring toolkit for roblox studio. | [wbfovn](https://mrquaxkers.gumroad.com/l/wbfovn) |
| 296 | Sword Combat & NPC System [ROBLOX] | Pierce | 5.00 | _page unavailable (HTTPError)_ | [swhwn](https://piercedevelop.gumroad.com/l/swhwn) |
| 297 | Texture - (Plugin) | MrQuaxkers | 14.99 | 3000+ CC0 Textures for roblox studio. | [aebhqo](https://mrquaxkers.gumroad.com/l/aebhqo) |
| 298 | WEPPY Roblox Plugin Pro | Weppy | 9.99 | 🚀 WEPPY Roblox AI Toolkit Pro — AI-Powered Roblox Studio Workflow Ship production Roblox workflows faster with AI coding agents connected directly to Roblox... | [faccjs](https://weppy.gumroad.com/l/faccjs) |

## Gameplay systems (16)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 299 | 2D Avatar : Avatar System for VRChat | DX | 15.00 | _page unavailable (HTTPError)_ | [otqkek](https://dx30.gumroad.com/l/otqkek) |
| 300 | Avatar Flying System & Effects [VRChat] | Pointless Creations | 5.00 | _page unavailable (HTTPError)_ | [ytgqe](https://pointlesscreations.gumroad.com/l/ytgqe) |
| 301 | Avatar Protection System for VRChat | Dextro | 20.00 | _page unavailable (HTTPError)_ | [gxayd](https://dextrovr.gumroad.com/l/gxayd) |
| 302 | CAMSUITE — All-in-One Camera Toolkit for Houdini | HYUNJOON KANG | 19.00 | _page unavailable (HTTPError)_ | [nzgkr](https://hyunjoonkang.gumroad.com/l/nzgkr) |
| 303 | Cryomancy and Earthshaping (VRCHAT + Quest) | Liindy | 15.00 | _page unavailable (HTTPError)_ | [gqvvuq](https://liindy.gumroad.com/l/gqvvuq) |
| 304 | Hair Card Pack + Pro Hair System | PixelicaCG | 8.99 | _page unavailable (HTTPError)_ | [wlwfe](https://pixelicacg.gumroad.com/l/wlwfe) |
| 305 | hood release system | chedsapp | 4.00 | _page unavailable (HTTPError)_ | [pdnoc](https://chedsapp.gumroad.com/l/pdnoc) |
| 306 | NodeArchitect - AI Agent and MCP Server for Houdini. | Jbishop - NodeArchitec | 24.99 | _page unavailable (HTTPError)_ | [thptkt](https://bishopvfx.gumroad.com/l/thptkt) |
| 307 | Real Sweat System for VRChat | Cooki | 6.49 | _page unavailable (HTTPError)_ | [vosmpv](https://cookipiece.gumroad.com/l/vosmpv) |
| 308 | Real Wet System for VRChat | Cooki | 14.99 | _page unavailable (HTTPError)_ | [ucwktv](https://cookipiece.gumroad.com/l/ucwktv) |
| 309 | Reality Field Virtual Production System 2024 | LOLED | free | _page unavailable (HTTPError)_ | [zkxko](https://loledvirtual.gumroad.com/l/zkxko) |
| 310 | Replicated Hitbox System | Aurora Devs | 54.99 | _page unavailable (HTTPError)_ | [xdcif](https://auroradevs.gumroad.com/l/xdcif) |
| 311 | Style-Locked AI Motion Graphics from Any Script (Claude Skil | FRMWRKD | 10.00 | _page unavailable (HTTPError)_ | [vluidk](https://frmwrkd.gumroad.com/l/vluidk) |
| 312 | TekDetek Pro // Live AI Detection // ASCII // VJ Browser Too | TekDetek | 20.00 | _page unavailable (HTTPError)_ | [xkljia](https://tekdetek.gumroad.com/l/xkljia) |
| 313 | Vibe Coder Kit — AI Development Framework for Production-Rea | Shahid Malik | 79.89 | _page unavailable (HTTPError)_ | [wvshw](https://nuovanceai.gumroad.com/l/wvshw) |
| 314 | VRCLens: VRChat Camera Extension for Desktop and VR | Hirabiki | 10.00 | _page unavailable (HTTPError)_ | [rpnel](https://hirabiki.gumroad.com/l/rpnel) |

## Audio (16)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 315 | 3dSynth - Generative G-code Engine for Creative 3D Printing | Kubuz | 39.00 | _page unavailable (HTTPError)_ | [vkyvdy](https://kubuz.gumroad.com/l/vkyvdy) |
| 316 | ALL IN ONE SOUND LIBRARY BUNDLE | Free To Use Sounds | 25.00 | _page unavailable (HTTPError)_ | [waasf](https://ftus.gumroad.com/l/waasf) |
| 317 | DEGAUSS - VST Plugin | SynthSkool | 99.00 | _page unavailable (HTTPError)_ | [exmdlr](https://synthskool.gumroad.com/l/exmdlr) |
| 318 | FIELD KIT Playback Engine / Standalone + VST3 + AU | Field Tone Audio | 26.25 | _page unavailable (HTTPError)_ | [yurac](https://fieldtoneaudio.gumroad.com/l/yurac) |
| 319 | GuyEngine V2 - VST | Ultima DSP | 14.00 | _page unavailable (HTTPError)_ | [aaube](https://ultimadsp.gumroad.com/l/aaube) |
| 320 | Kick & Bass Auto Mix: VST3 & AU Plugin | Wagner Who | 37.00 | _page unavailable (HTTPError)_ | [reveh](https://wagnerwho.gumroad.com/l/reveh) |
| 321 | Liminal Space 2: Haunted Digital Reverb Synthesizer - CLAP,  | Wavetables.lol | 10.00 | _page unavailable (HTTPError)_ | [zobuuw](https://kcrosley.gumroad.com/l/zobuuw) |
| 322 | MODEL 200 REVERBERATOR PLUGIN (VST3 - AU - AAX - MAC - WINDO | PastToFutureReverbs | 99.00 | _page unavailable (HTTPError)_ | [ctwdx](https://pasttofuturereverbs.gumroad.com/l/ctwdx) |
| 323 | PTF 144 FOUR TRACK CASSETTE MIXER PLUGIN (VST3 - AU - AAX -  | PastToFutureReverbs | 69.00 | PTF-144 – Four-Track Cassette Mixer & Recorder Four Channels. Four Tracks. Pure Analog Cassette Magic. Bring the unmistakable sound and workflow of a... | [dwqdph](https://pasttofuturereverbs.gumroad.com/l/dwqdph) |
| 324 | PTF 16 DIGITAL REVERB PLUGIN (VST3 - AU - AAX - MAC - WINDOW | PastToFutureReverbs | 99.00 | PTF 16 – Legendary Digital Reverb THE SOUND OF THE '80s. THE MAGIC OF EARLY DIGITAL REVERB. Before plugins, before endless processing power, there was a... | [wkcax](https://pasttofuturereverbs.gumroad.com/l/wkcax) |
| 325 | PTF 350 TUBE TAPE RECORDER PLUGIN (VST3 - AU - AAX - MAC OS  | PastToFutureReverbs | 79.00 | The PTF-350 by Past To Future Plugins is a detailed plugin recreation (available as VST3 and Audio Unit for macOS, and VST3 for Windows) of a classic... | [gkdxxy](https://pasttofuturereverbs.gumroad.com/l/gkdxxy) |
| 326 | PTF 3630 COMPRESSOR PLUGIN (VST3 - AU - AAX - MAC OS - WINDO | PastToFutureReverbs | 49.00 | _page unavailable (HTTPError)_ | [ajaipb](https://pasttofuturereverbs.gumroad.com/l/ajaipb) |
| 327 | PTF DMX-15 STEREO DIGITAL DELAY & PITCH SHIFTER PLUGIN (VST3 | PastToFutureReverbs | 89.00 | _page unavailable (HTTPError)_ | [kvizb](https://pasttofuturereverbs.gumroad.com/l/kvizb) |
| 328 | PTF S950 SAMPLER PLUGIN (VST3 - AU - AAX - MAC - WINDOWS) | PastToFutureReverbs | 89.00 | _page unavailable (HTTPError)_ | [blrcpl](https://pasttofuturereverbs.gumroad.com/l/blrcpl) |
| 329 | Twenty Engine 1.1: an 8-voice polysynth inspired by the Korg | Peter Kohlmetz Møller | free | _page unavailable (HTTPError)_ | [ygmrks](https://7233849350308.gumroad.com/l/ygmrks) |
| 330 | U273 VINTAGE GERMAN COMPRESSOR LIMITER PLUGIN (VST3 - AU - A | PastToFutureReverbs | 79.00 | _page unavailable (HTTPError)_ | [ouitxw](https://pasttofuturereverbs.gumroad.com/l/ouitxw) |

## Pipeline, export & automation (4)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 331 | Blender Batch AO Baker Addon | VD Skinworks | 24.99 | ## 🇬🇧 English ### Batch AO Baker – Unwrap, bake & denoise ambient occlusion for all your objects in one click Stop baking AO object by object. Batch AO Baker... | [embsc](https://vdskinworks.gumroad.com/l/embsc) |
| 332 | Clip Exporter / Essential Premiere Pro Plugin | Piotr Toczynski | 25.00 | _page unavailable (HTTPError)_ | [otjkzv](https://cuttothepoint.gumroad.com/l/otjkzv) |
| 333 | MetaHuman Converter tool | Pavel Barnev | 300.00 | _page unavailable (HTTPError)_ | [tgxgnp](https://pavelbarnev.gumroad.com/l/tgxgnp) |
| 334 | Mystery Pixel Image Generator By Marina Art Design (WINDOWS  | Marina Art Design | 80.00 | ⭐ Mystery Pixel Image Generator Turn any black‑and‑white image into a clean, printable Mystery Pixel Image in minutes. This desktop tool lets you import or... | [qczcw](https://marinaartdesign.gumroad.com/l/qczcw) |

## UI & interface (3)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 335 | Pie Menu Editor Fork 2.4.0 | Pluglug | 29.99 | _page unavailable (HTTPError)_ | [ghqdwox](https://pluglug.gumroad.com/l/ghqdwox) |
| 336 | Quick Launcher | Live Workflow Tools | 14.00 | _page unavailable (HTTPError)_ | [grqraj](https://liveworkflowtools.gumroad.com/l/grqraj) |
| 337 | QuickMat Bake Pro – Ultimate Texture Baking Tool for Blender | Studio156 | 15.00 | _page unavailable (HTTPError)_ | [vdfltt](https://studio156.gumroad.com/l/vdfltt) |

## Uncategorised (101)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 338 | 100+ CLAUDE REMOTION STYLES VAULT - Fully Automatic Editor | CHRONIXEL SHOP | free | _page unavailable (HTTPError)_ | [gexbt](https://chronixel.gumroad.com/l/gexbt) |
| 339 | 40% OFF🧨IN DESCRIPTION / Antigen VRChat Furry Avatar | gum.neochroma.xyz | 35.00 | _page unavailable (HTTPError)_ | [hhtkv](https://neochroma.gumroad.com/l/hhtkv) |
| 340 | 40% OFF🧨IN DESCRIPTION / Dergal VRChat Furry Model | gum.neochroma.xyz | 35.00 | _page unavailable (HTTPError)_ | [yxtvch](https://neochroma.gumroad.com/l/yxtvch) |
| 341 | [Addon]DECALmachine | machin3 | 54.99 | _page unavailable (HTTPError)_ | [fjXBHu](https://machin3.gumroad.com/l/fjXBHu) |
| 342 | [Addon]MACHIN3tools | machin3 | 2.00 | _page unavailable (HTTPError)_ | [IjsAf](https://machin3.gumroad.com/l/IjsAf) |
| 343 | [VRChat/SDK3] GD's VRChat Avatar Making Masterclass | YerGodDamnRight (GD, Y | 80.00 | _page unavailable (HTTPError)_ | [xmzhz](https://yergoddamnright.gumroad.com/l/xmzhz) |
| 344 | A3D TexSync - Substance Painter Plugin | A3D Labs | 15.00 | _page unavailable (HTTPError)_ | [fcxrss](https://a3dtools.gumroad.com/l/fcxrss) |
| 345 | Ability Toolbar | gfxcomet | 1.80 | _page unavailable (HTTPError)_ | [wjxwf](https://gfxcomet.gumroad.com/l/wjxwf) |
| 346 | Advanced Car Spawner Script | Kaisen | free | _page unavailable (HTTPError)_ | [exfxu](https://claritykaisen.gumroad.com/l/exfxu) |
| 347 | Afterimages Installation Script (VRChat) | Zekk | free | _page unavailable (HTTPError)_ | [bghnkq](https://zekk.gumroad.com/l/bghnkq) |
| 348 | Anymo | Anymotool | 240.00 | _page unavailable (HTTPError)_ | [kptqn](https://anymotool.gumroad.com/l/kptqn) |
| 349 | Asad FX (After Effects, Premier Pro Plugin) | Asad Ali | 49.99 | _page unavailable (HTTPError)_ | [ozigow](https://editmaster12.gumroad.com/l/ozigow) |
| 350 | Atlas Cutter | Sebastien Rousseau | 25.00 | _page unavailable (HTTPError)_ | [fpros](https://darktreetools.gumroad.com/l/fpros) |
| 351 | Avatar Accessory Tools | Shatter | 2.99 | _page unavailable (HTTPError)_ | [rwani](https://shatteredfur.gumroad.com/l/rwani) |
| 352 | BDFM tool - pixelated SVG | DesignFamilyMarket | free | _page unavailable (HTTPError)_ | [byown](https://designfamilymarket.gumroad.com/l/byown) |
| 353 | Behemox Hair Generator for Blender | Behemox Studio | 19.50 | _page unavailable (HTTPError)_ | [ucnep](https://behemox.gumroad.com/l/ucnep) |
| 354 | Blender vertex color I Octopus | maso_tools | 14.99 | _page unavailable (HTTPError)_ | [omprho](https://masotools.gumroad.com/l/omprho) |
| 355 | Blueish Asset-A Free Node Library | blueish | 10.00 | _page unavailable (HTTPError)_ | [jkglzv](https://blueish0930.gumroad.com/l/jkglzv) |
| 356 | BLUUR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [pwobgm](https://antlii.gumroad.com/l/pwobgm) |
| 357 | CAD Sketcher [ Blender Addon ] | Keep Making | free | _page unavailable (HTTPError)_ | [rfoow](https://keepmaking.gumroad.com/l/rfoow) |
| 358 | CC4D Tools & CC4D Link | Benjamin Broschinski | 40.00 | _page unavailable (HTTPError)_ | [tovtvi](https://blkmsk.gumroad.com/l/tovtvi) |
| 359 | Cinematic Compositor Addon | ALANWAYNE | 8.98 | _page unavailable (HTTPError)_ | [memaa](https://alanwayne.gumroad.com/l/memaa) |
| 360 | Cloooner - Ae Cloner Tool That’s Actually Simple! | Phan Đức Trọng | 15.00 | _page unavailable (HTTPError)_ | [gojuoe](https://motionbytrong.gumroad.com/l/gojuoe) |
| 361 | DanTools | Daniel TechArt | 29.00 | HOUDINI HDAs. Houdini version 21+ New updated DanTools version: 1.1 Added high-resolution LiDAR in Europe, from 0.5 centimeters to 10 meters per pixels... | [noreow](https://danieltechart.gumroad.com/l/noreow) |
| 362 | Deep Paint -Blender GP Modeling & Painting tool Set | Gaku | 40.00 | _page unavailable (HTTPError)_ | [ffodac](https://gakutada.gumroad.com/l/ffodac) |
| 363 | Delta Quad (blender addon) | Kushiro | 10.00 | _page unavailable (HTTPError)_ | [hoivtl](https://kushiro.gumroad.com/l/hoivtl) |
| 364 | DITHR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [bdfpne](https://antlii.gumroad.com/l/bdfpne) |
| 365 | Draw Model Tool | Joey Carlino | 7.00 | _page unavailable (HTTPError)_ | [npepei](https://joeycarlino.gumroad.com/l/npepei) |
| 366 | Droplet Generator 3 for Blender | ibotpl | 19.00 | _page unavailable (HTTPError)_ | [alvgr](https://ibotpl.gumroad.com/l/alvgr) |
| 367 | Easy Chain — Blender Addon for FiveM Jewelry Conversion | DistrictXStudios | 10.00 | _page unavailable (HTTPError)_ | [xnvxa](https://districtxstudios.gumroad.com/l/xnvxa) |
| 368 | Easy Custom Normals - Stylized Shading Workflows in Blender | Fondant | 10.00 | _page unavailable (HTTPError)_ | [oatmwu](https://fondanttools.gumroad.com/l/oatmwu) |
| 369 | Easy Terrain Generator | kollapse3d | 4.99 | _page unavailable (HTTPError)_ | [qcmfh](https://kollapse3d.gumroad.com/l/qcmfh) |
| 370 | Easy Treez V2.0 for Maya | UnPLUG Tools | 110.00 | _page unavailable (HTTPError)_ | [lFVRg](https://unplugtools.gumroad.com/l/lFVRg) |
| 371 | EDGY - Worn Edges Plugin for Cinema 4D & Blender | Cornelius Dämmrich | 15.00 | _page unavailable (HTTPError)_ | [fyhsz](https://corneliusdammrich.gumroad.com/l/fyhsz) |
| 372 | Foliage Tint Master — One Click Tools | Alexandre Besson | 24.00 | _page unavailable (HTTPError)_ | [ylbgs](https://alexandrebesson.gumroad.com/l/ylbgs) |
| 373 | Galeria Tool License Key | Adhemas Batista | 50.00 | _page unavailable (HTTPError)_ | [gdddk](https://adhemas.gumroad.com/l/gdddk) |
| 374 | Garment Tool | bartoszstyperek | 40.00 | _page unavailable (HTTPError)_ | [MAnWP](https://bartoszstyperek.gumroad.com/l/MAnWP) |
| 375 | Garment Tool 2.1 for MetaHuman — UE 5.8 / Fit, Layer & Refit | Unreal Engine Cinemati | 10.00 | _page unavailable (HTTPError)_ | [sqbht](https://6062949617079.gumroad.com/l/sqbht) |
| 376 | Graphics Plugin Full v3.0.1 | Hanmen | 8.00 | _page unavailable (HTTPError)_ | [jdycp](https://hanmen.gumroad.com/l/jdycp) |
| 377 | Grid Method Tool - Rounded Pixel to Vector SVG | DesignFamilyMarket | 5.00 | _page unavailable (HTTPError)_ | [xruudv](https://designfamilymarket.gumroad.com/l/xruudv) |
| 378 | Grid Modeler (blender addon) | Kushiro | 20.00 | _page unavailable (HTTPError)_ | [VthLyO](https://kushiro.gumroad.com/l/VthLyO) |
| 379 | GRM Groom Toolkit (Houdini FX) | Gerardo Castellanos | 100.00 | _page unavailable (HTTPError)_ | [vbvrwb](https://gerardocastellanos.gumroad.com/l/vbvrwb) |
| 380 | GRM Groom Toolkit (Houdini INDIE) | Gerardo Castellanos | 30.00 | _page unavailable (HTTPError)_ | [swsmwj](https://gerardocastellanos.gumroad.com/l/swsmwj) |
| 381 | GroomBear - grooming toolkit for Houdini | kwac | 59.00 | _page unavailable (HTTPError)_ | [yndnV](https://kwac.gumroad.com/l/yndnV) |
| 382 | Hair Tool for Blender | bartoszstyperek | 52.00 | _page unavailable (HTTPError)_ | [Dbhj](https://bartoszstyperek.gumroad.com/l/Dbhj) |
| 383 | Hairshop v2.98 - Hair card texture generator | KM Lee | 22.60 | _page unavailable (HTTPError)_ | [wyhba](https://kyoungmin.gumroad.com/l/wyhba) |
| 384 | Houdini 19.5 FX Encanto Cracking Concrete | Pol Villà | 10.00 | _page unavailable (HTTPError)_ | [daztv](https://polvfx.gumroad.com/l/daztv) |
| 385 | Houdini Solaris - USD & Environment Workflow (Subscription) | adrienlambert | 4.00 | _page unavailable (HTTPError)_ | [ztwuaj](https://adrienlambert.gumroad.com/l/ztwuaj) |
| 386 | HP Art Toolset: Surface Wrap for Maya and Blender | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [bwkfxb](https://hparttoolset.gumroad.com/l/bwkfxb) |
| 387 | Item Tooltip | gfxcomet | 1.80 | _page unavailable (HTTPError)_ | [ihsii](https://gfxcomet.gumroad.com/l/ihsii) |
| 388 | Jeano's Gun Framework | Jeano | 1.00 | _page unavailable (HTTPError)_ | [xvpxc](https://scofieldstudios.gumroad.com/l/xvpxc) |
| 389 | Kiosk Library - Asset Manager for 3D Artist | Fabian Strube | free | _page unavailable (HTTPError)_ | [xcsxpt](https://fabianstrube.gumroad.com/l/xcsxpt) |
| 390 | Leons Modeling Toolkit 2.0 | _3Leon | 10.00 | _page unavailable (HTTPError)_ | [vwija](https://3leon.gumroad.com/l/vwija) |
| 391 | Liminal Editor | Pawel | 12.50 | _page unavailable (HTTPError)_ | [spkbhy](https://venetian5gmailcom.gumroad.com/l/spkbhy) |
| 392 | LIVEWIRED MPC Plugin Bundle – 13 Free Plugins for MPC | Livewired Sound Series | free | _page unavailable (HTTPError)_ | [urmntl](https://livewired808.gumroad.com/l/urmntl) |
| 393 | Love2D Dev Tools Pro | abyo software | 12.00 | _page unavailable (HTTPError)_ | [aolecz](https://y1uda.gumroad.com/l/aolecz) |
| 394 | Lua Scripting Full Course | Rodel Catampongan | 10.00 | _page unavailable (HTTPError)_ | [kibiI](https://venuslock.gumroad.com/l/kibiI) |
| 395 | Magic Decal | Nebula Animations | 15.00 | _page unavailable (HTTPError)_ | [bmouh](https://nebulaanimations.gumroad.com/l/bmouh) |
| 396 | Malbers Biped Ragdoll | Malbers Animations | 24.99 | _page unavailable (HTTPError)_ | [awukjv](https://malberanimations.gumroad.com/l/awukjv) |
| 397 | Mallet: Blender addon | Twist | 15.00 | _page unavailable (HTTPError)_ | [qxigq](https://dertwist.gumroad.com/l/qxigq) |
| 398 | MEGA ADDON For Blender | CGStore | 15.00 | _page unavailable (HTTPError)_ | [ehqjh](https://cgcool.gumroad.com/l/ehqjh) |
| 399 | Merge Master - Blender addon | miccoli3d | 60.00 | _page unavailable (HTTPError)_ | [zkckw](https://miccoli3d.gumroad.com/l/zkckw) |
| 400 | MotionKit AE – All-in-One Ae ToolKit | Off.motionsfly | 10.00 | _page unavailable (HTTPError)_ | [bedrnd](https://officialmotionsfly.gumroad.com/l/bedrnd) |
| 401 | Noesis Intelligent Harmony Generator & Assistant | Dystopian Waves | 10.79 | _page unavailable (HTTPError)_ | [nvfzqi](https://dystopianwaves.gumroad.com/l/nvfzqi) |
| 402 | NTD Engine - Full Version | OwnLife Audio | 39.00 | _page unavailable (HTTPError)_ | [zlbwog](https://ownlifeaudio.gumroad.com/l/zlbwog) |
| 403 | Old (Kinda broken) - Boom-Box (VRChat-SDK3) | Doloro | 3.50 | _page unavailable (HTTPError)_ | [txufu](https://doloro.gumroad.com/l/txufu) |
| 404 | Omni-Matrix Holograph: Premium 3D WebGL Engine for Framer | Creative Apes | 6.00 | _page unavailable (HTTPError)_ | [umfgop](https://creativeapes.gumroad.com/l/umfgop) |
| 405 | Outliyr Framework | outliyr | 199.99 | _page unavailable (HTTPError)_ | [etpeiq](https://outlier2.gumroad.com/l/etpeiq) |
| 406 | Oven Bake / Blender Baking Addon | Boreo | 16.00 | _page unavailable (HTTPError)_ | [undhn](https://boreo.gumroad.com/l/undhn) |
| 407 | Painterly V.3 Blender (5.1+)  Add-on | Doughy Animation Studi | 19.50 | _page unavailable (HTTPError)_ | [wvwta](https://doughyanimation.gumroad.com/l/wvwta) |
| 408 | Palette Grid - Smart Palette Texture Workflow Blender Addon | Saved Pixel | 25.00 | _page unavailable (HTTPError)_ | [uqjpux](https://savedpixel.gumroad.com/l/uqjpux) |
| 409 | Partice Editor PRO for Honey Select 2 | Hanmen | 9.00 | _page unavailable (HTTPError)_ | [iopwv](https://hanmen.gumroad.com/l/iopwv) |
| 410 | Plugin Bundle Vol. 1 | Rex Roberts | 60.00 | _page unavailable (HTTPError)_ | [hxnqce](https://rexaffects.gumroad.com/l/hxnqce) |
| 411 | Poly Modeling Toolbox - Everything You Need And More | Noggi | 39.00 | _page unavailable (HTTPError)_ | [mipncz](https://noggi3d.gumroad.com/l/mipncz) |
| 412 | Polytool 2 | Markcreator | free | _page unavailable (HTTPError)_ | [hsseod](https://markcreator.gumroad.com/l/hsseod) |
| 413 | RESOLUME Plugin FX^ASCII.GLYPH_TMBK | VJ Tembak | 18.00 | _page unavailable (HTTPError)_ | [kkfmbii](https://vjtembak.gumroad.com/l/kkfmbii) |
| 414 | Retro Diffusion Extension for Aseprite | Cody Claus | 20.00 | _page unavailable (HTTPError)_ | [yqecpq](https://astropulse.gumroad.com/l/yqecpq) |
| 415 | RH Character Tools for Cinema 4D & Mixamo | rhymage | 48.00 | _page unavailable (HTTPError)_ | [bbLu](https://rhymage.gumroad.com/l/bbLu) |
| 416 | Ripplor Plugin for Cinema 4D | Spenser Clark | 25.00 | _page unavailable (HTTPError)_ | [wvohg](https://sdimaging.gumroad.com/l/wvohg) |
| 417 | SAMPL Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [vfetba](https://antlii.gumroad.com/l/vfetba) |
| 418 | ShapeKeyGen V3.50 Blender Addon | Wee learn from Mobile | 15.00 | _page unavailable (HTTPError)_ | [yrfsq](https://pymarket.gumroad.com/l/yrfsq) |
| 419 | SHAPES - Shape Key Editor for Blender | brave rabbit | 20.00 | _page unavailable (HTTPError)_ | [dfuju](https://braverabbit.gumroad.com/l/dfuju) |
| 420 | SHAPES 5.13 - Blend Shape Editor for Maya 2023-2027 | brave rabbit | 20.00 | _page unavailable (HTTPError)_ | [sovts](https://braverabbit.gumroad.com/l/sovts) |
| 421 | Simple Tree Tools 3.0 for Houdini | nirfse3D | free | _page unavailable (HTTPError)_ | [hsgdax](https://nwestfelt.gumroad.com/l/hsgdax) |
| 422 | Smart Layer v0.91.1 (Python Script for Maya) | Slava Baravik | 52.00 | _page unavailable (HTTPError)_ | [apvbbq](https://borovikmotion.gumroad.com/l/apvbbq) |
| 423 | Stereo Bundle: Rotation + Deviation - Quadrature stereo proc | RawtonForge | 32.00 | _page unavailable (HTTPError)_ | [osgyf](https://rawton.gumroad.com/l/osgyf) |
| 424 | Stylized Cloud Generator | Rei | 9.50 | _page unavailable (HTTPError)_ | [qcgrt](https://reipart.gumroad.com/l/qcgrt) |
| 425 | Stylized Sky World Generator | Rei | 18.00 | _page unavailable (HTTPError)_ | [vaznyj](https://reipart.gumroad.com/l/vaznyj) |
| 426 | Stylized Tree Asset Generator | Rei | 12.50 | _page unavailable (HTTPError)_ | [kluofh](https://reipart.gumroad.com/l/kluofh) |
| 427 | Substance Node Pack / Dete Trim Toolkit | Dete Art Resources | 2.50 | _page unavailable (HTTPError)_ | [hjmavo](https://dete.gumroad.com/l/hjmavo) |
| 428 | SuperLCD - Davinci Resolve Plugin | Akascape | 5.60 | _page unavailable (HTTPError)_ | [qiahk](https://akascape.gumroad.com/l/qiahk) |
| 429 | TEXTR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [lsucj](https://antlii.gumroad.com/l/lsucj) |
| 430 | TFMSTYLE Addon Collection for Blender | TFMSTYLE | 8.99 | _page unavailable (HTTPError)_ | [faifq](https://tfmstyle.gumroad.com/l/faifq) |
| 431 | The Nature Generator | Andreas Dürr | 85.00 | _page unavailable (HTTPError)_ | [gzyaj](https://cinematiccookie.gumroad.com/l/gzyaj) |
| 432 | TrackToolsV2.1 - BETA | MeshHouse | free | _page unavailable (HTTPError)_ | [acmxzm](https://meshhouse.gumroad.com/l/acmxzm) |
| 433 | Tradigitalist Toolbag - All Access | Alan Wyatt | 12.00 | _page unavailable (HTTPError)_ | [enxsr](https://tradigital.gumroad.com/l/enxsr) |
| 434 | Tree Library Botaniq Trees+Plants | polygoniq | 2.00 | _page unavailable (HTTPError)_ | [MOZJY](https://polygoniq.gumroad.com/l/MOZJY) |
| 435 | TunaMetaPack - MetaHuman Convert / Custom Tools | Tuna | 150.00 | _page unavailable (HTTPError)_ | [wsbap](https://tunarig.gumroad.com/l/wsbap) |
| 436 | Viral Styles Launchpad | The AI Tool Finds | 19.00 | _page unavailable (HTTPError)_ | [wbsqwp](https://theaitoolfinds.gumroad.com/l/wbsqwp) |
| 437 | Vooolume - Relief Brush Tool | Krftoools | 15.00 | _page unavailable (HTTPError)_ | [yrgeg](https://krftoools.gumroad.com/l/yrgeg) |
| 438 | WireTools / Node Connection Tools for Cinema 4D & Redshift | Maksym Vysokolov | 19.50 | _page unavailable (HTTPError)_ | [ozgreb](https://thodos998.gumroad.com/l/ozgreb) |

---

Regenerate: `python3 tools/gumroad_census.py --market all` then `python3 tools/compile_census.py`. Query list and scrape date are in `specs/gumroad_tools.json`.
