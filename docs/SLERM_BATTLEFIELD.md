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
| per-pixel texture sampling with perspective-correct UVs | `src/shade.c wubu_tex` | unique colours 85 -> 279, local detail 0.82 -> 4.30 on a checkerboard |
| procedural placement: Bridson Poisson-disk, exclusion circles, per-instance scale/rotation | `src/scatter.c` | min pair 0.1600 against a 0.160 radius (uniform random: 0.0023); 0 in clearings |

Not implemented yet, and said plainly: **texture sampling** (surfaces are flat-coloured), **cast shadows** (a contact ellipse stands in), **bevels**, **retargeting**, **squash/stretch**, and **translucency** — the glossy subsurface look of a TrendStory-style vinyl character is a transmission model we do not have, even though the specular highlight and the depth of field around it now exist.


## Shaders & rendering (82)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 1 | "Frosted Glass" Gradient Shader | 1HP | 15.00 | ✨ Dynamic Gradient Shader — Smooth, Frosted, Alive This shader turns a simple gradient into a living, breathing visual effect. It blends colors with a soft... | [exzjvy](https://1hp.gumroad.com/l/exzjvy) |
| 2 | "Shaders Plus" - Real-Time Caustics, Thin Film, Dispersion f | SMOUSE | free | _page unavailable (HTTPError)_ | [bljae](https://smouse.gumroad.com/l/bljae) |
| 3 | (ENG) TUTORIAL NPR Painterly Arnold Shader Pack: Arcane & An | Mani Salguero | 27.50 | This painterly shader for Maya and Arnold is the result of years of experimentation and refinement. It is ready to use on any prop or character, even without... | [obmxk](https://manisalguero.gumroad.com/l/obmxk) |
| 4 | 150+ ChatGPT prompts to make you a top 1% shader wizard 🪄 | OccaSoftware | free | 150 ChatGPT prompts to make you a top 1% shader wizard 🧙‍♂️ This collection of ChatGPT prompts will help you make the most of ChatGPT to supercharge your... | [ihlcap](https://occasoftware.gumroad.com/l/ihlcap) |
| 5 | [Tutorial] UE5 Advanced Ocean Shader Creation - With Gerstne | Abderrezak Bouhedda | 20.00 | ** Please read the whole product description ** This 3-hour tutorial teaches you how to create a realistic ocean shader inside Unreal Engine, using... | [nmwaa](https://artofab.gumroad.com/l/nmwaa) |
| 6 | Advanced Outline Shader for Unreal Engine 5 | Evans Bohl | 14.99 | This post process material shader allows you to get the cleanest outlines possible in Unreal Engine! Even if it&#39;s an advanced Outline Shader, you&#39;ll be able... | [uiqov](https://evansbohl.gumroad.com/l/uiqov) |
| 7 | Bake Multiple Materials into One Texture Atlas - AtlasForge  | Aisal | free | _page unavailable (HTTPError)_ | [gfeaqu](https://aisal.gumroad.com/l/gfeaqu) |
| 8 | Batch Render Creator - Local Render Queue for Blender | Wanderson M. Pimenta | free | WHAT IS BATCH RENDER CREATOR? The Batch Render Creator is a render queue for Blender that works like a local render farm, allowing you to send multiple... | [kAloE](https://blender-addons.gumroad.com/l/kAloE) |
| 9 | Blueish Asset-A Free Node Library | blueish | 10.00 | 534 Blender node assets, free for everyone This is my whole node library: Geometry Nodes, shaders, material functions, compositor effects, a particle system... | [jkglzv](https://blueish0930.gumroad.com/l/jkglzv) |
| 10 | C4D plugin for Seedance, Meshy, Kling and any Al possible. C | Dani Zaitcev | 5.00 | Nano Pro 3.5 The only AI plugin you actually need for Cinema 4D. Think of Nano Pro as your Cinema 4D render window, but with AI image, video, and 3D... | [cbfnyr](https://manicporcupine.gumroad.com/l/cbfnyr) |
| 11 | Cartoon Afro Girl 2 - Toon Rigged Child Character Maya Versi | Harun BOL (A.K.A.) Cha | 97.00 | Cartoon Afro Girl - Toon Rigged Child - Maya Version High Quality Low Poly Rigged Cute African American Little Girl Model... | [ezrkd](https://harunbol.gumroad.com/l/ezrkd) |
| 12 | Cinematic Product Studio Blender Add On - 79 Animation,  52  | Gigi Gorlova | 15.00 | _page unavailable (HTTPError)_ | [hewskz](https://gigirenders.gumroad.com/l/hewskz) |
| 13 | COD Auto-Shader Blender Add-On + More | killshotttttt | 15.00 | _page unavailable (HTTPError)_ | [hbdsgo](https://killshotttttt.gumroad.com/l/hbdsgo) |
| 14 | DXSky: Skybox Shader for VRChat & Unity | DX | 11.00 | SkyMove + SkyCraft Get yours now. these two incredible animated Skybox Shader packages, both featuring easy installation and customization. Contains 5... | [xtghoq](https://dx30.gumroad.com/l/xtghoq) |
| 15 | Fake Diamonds shader for Cycles and Eevee | Lance Phan | 5.85 | This product is a collection of 4 diamond shader node groups to let you quickly and easily make a lot of diamonds. These node groups are very easy to use... | [wfoff](https://lancephan.gumroad.com/l/wfoff) |
| 16 | Feather/Fur Shader | normalizedcrow | free | _page unavailable (HTTPError)_ | [bvako](https://normalizedcrow.gumroad.com/l/bvako) |
| 17 | GLSL Eyeball + MediaPipe Timemachine / Two-in-One TouchDesig | Irina.ae | 5.00 | Two functions for the price of one. Learn GLSL from the shader. Play with time-displacement from the effect. Mode 1 — GLSL Eyeball A fully annotated GLSL... | [ucsggn](https://irinaught.gumroad.com/l/ucsggn) |
| 18 | Godot Pixelated Shader + RGB shift + Pixel Size + Curved scr | Yaroslav Samoilov | 5.99 | Godot 2d/3d Shader with Curvature and RGB shift. | [xqaoh](https://yaosam0.gumroad.com/l/xqaoh) |
| 19 | Godot Shader Pack: 150+ shaders for Godot 4 | Filip Rachůnek | 14.99 | ⚠️ Get all Godot products at a discounted price! Godot Master Creator Bundle Would you like to add great-looking visual effects to your game made in the... | [krudjf](https://filiprachunek.gumroad.com/l/krudjf) |
| 20 | GPU Fluid Simulation / No Kinect Required | Irina.ae | 5.00 | A real-time GPU fluid simulation for TouchDesigner. Not a blur trick — a proper Navier-Stokes solver running 16 GLSL passes per frame: advection, vorticity... | [jelqf](https://irinaught.gumroad.com/l/jelqf) |
| 21 | Holofoil Shader | 1HP | 15.00 | Holofoil Shader This is a fully customizable holographic shader made in Unity Shader Graph (Unity 6.0) and works smoothly in both URP and HDRP. It’s inspired... | [fogdg](https://1hp.gumroad.com/l/fogdg) |
| 22 | Hologram Shaders Pro for Unity | Daniel Ilett | 19.99 | This pack adds a range of hologram shaders to Unity. From basic holograms with Fresnel highlights to advanced holograms with two kinds of glitch effect... | [oqgmq](https://danielilett.gumroad.com/l/oqgmq) |
| 23 | MANI NPR for Blender — Stylized Shader & Lookdev Toolkit (An | Mani Salguero | 39.99 | ONE TOOLKIT. ENDLESS STYLIZED LOOKS. Create anime, toon, comic, manga, and painterly looks with the freedom to mix different techniques and make them your... | [wdcig](https://manisalguero.gumroad.com/l/wdcig) |
| 24 | MatricX bake: Blender Material & Decal Baking Addon | EidosEdge | 79.00 | _page unavailable (HTTPError)_ | [gjpmlv](https://eidosedge.gumroad.com/l/gjpmlv) |
| 25 | More shaders in Godot 4: Add stunning visual effects to your | Filip Rachůnek | 9.90 | ⚠️ Get all Godot products at a discounted price! Godot Master Creator Bundle Once more, learn how to enhance your game&#39;s graphics with impressive visual... | [mrtmj](https://filiprachunek.gumroad.com/l/mrtmj) |
| 26 | Motion Blur Shaders – Advanced Shader Setups for Unreal Engi | raulfx | 14.99 | This pack contains a versatile collection of custom motion blur setups designed for Unreal Engine, each tailored for different use cases, performance... | [ebtxq](https://raulfx.gumroad.com/l/ebtxq) |
| 27 | Multi-Mat Baker - Bake Multiple Materials into One PBR Textu | Junaid Alam | 15.00 | Multi-Mat Baker- One Click. One Material. Game Ready. Downloaded a character with 30 materials? Bought an asset pack where every piece has its own shader... | [btyxer](https://blenderustad.gumroad.com/l/btyxer) |
| 28 | Next-Gen Shader Helper Plugin | Hanmen | 5.99 | Changing the shaders manually for each character card and for each accessory and clothing takes a lot of time. Here comes this plugin. A Customizable shader... | [lnfdr](https://hanmen.gumroad.com/l/lnfdr) |
| 29 | Next-Gen Shaders V5.10 for Honey Select 2 (FLASH SALE) | Hanmen | 10.99 | FEATURES ULTIMATE PERFORMANCE Up to 100-500%. New optimized SSS algorithm. Based on improved HSSSS. Better Integration with other Post Processing Effects... | [cdxely](https://hanmen.gumroad.com/l/cdxely) |
| 30 | Omni-Matrix Holograph: Premium 3D WebGL Engine for Framer | Creative Apes | 6.00 | Turn your media into a living digital projection. The Omni-Matrix Holograph is a high-fidelity WebGL shader designed for designers who want to push the... | [umfgop](https://creativeapes.gumroad.com/l/umfgop) |
| 31 | OMNIKIT — Geometry Nodes, VFX & Materials for Blender | Blender addons | free | Build, shape and animate with OMNIKIT. Editable Geometry Nodes, VFX and materials for your next Blender project. OMNIKIT brings reusable procedural tools... | [lauvm](https://maroc777772.gumroad.com/l/lauvm) |
| 32 | Photoshop Character Designer Toolkit Brushes | Francisco Beltrán | 20.00 | This pack includes all my brush sets (Pencils, Inkers, Screentones, Storyboard) plus the Cartoon, Sketch, Gouache, Oils, Pastels and Aquarelles / Watercolors... | [xAMz](https://frankstore.gumroad.com/l/xAMz) |
| 33 | Physically Based Cel Shader | Jumpeter | 50.00 | This is a Sample Project for the Physically Based Cel Shader Post Process I build in this video tutorial: https://youtu.be/eBS3BOI5KnM Reach out to my... | [zobtn](https://jumpeter.gumroad.com/l/zobtn) |
| 34 | Procedural Grid (Blender 3+, 4+) | Mina Pêcheux | 3.00 | Looking for an easy-to-use level design tool? This procedural grid Blender shader will make it easy to create whiteboxes and prototype base versions of your... | [okeizj](https://mpecheux.gumroad.com/l/okeizj) |
| 35 | Procedural Planet (Blender 4+) | Mina Pêcheux | 9.00 | Need to make some neat 3D procedural planet for your next project? This node-based shader will give you an infinity of variations just by tweaking a few... | [gfhysx](https://mpecheux.gumroad.com/l/gfhysx) |
| 36 | Procedural Sky System - Blender Addon | Other Realms | 15.00 | Discord: https://discord.gg/9HPkQf9ebu Formerly a world material now a Blender add-on. A fully procedural sky system containing a World node-graph and sun... | [sogyzv](https://otrealms.gumroad.com/l/sogyzv) |
| 37 | Quest Basic Water Shader(VRChat) | noriben | 9.00 | Overview This is an asset for VRChat worlds. This is a world asset for a water shader created for Quest, balancing good appearance, lightweight performance... | [exzzss](https://noriben3.gumroad.com/l/exzzss) |
| 38 | Quick Water Drops V3 (Blender 5.0+ Addon) | Faebe | 5.00 | HOW TO USE IT -&gt; https://youtu.be/MiIAdbYE4uw Version 3 is now also Available for Blender 5.2! Have Fun Creating :) 💧 What&#39;s New in Version 3? Version 3 is a... | [yifmr](https://faebe.gumroad.com/l/yifmr) |
| 39 | RainDrop Shader (VRChat) | noriben | 9.00 | Major Update — v3.0.0 (July 26, 2026) Added refraction, frosted-glass effects, and background blur. Added support for VRC Light Volumes. Redesigned the... | [quhsao](https://noriben3.gumroad.com/l/quhsao) |
| 40 | Realistic Rainbow Shader (VRChat) | noriben | 7.00 | Overview This is an asset for VRChat worlds. This is a realistic-looking rainbow shader that can be used in Unity, VRChat, and similar platforms. I created... | [qbuorz](https://noriben3.gumroad.com/l/qbuorz) |
| 41 | Realistic Unity Clay Shader | taletronic | 2.00 | With this shader for Unity you can create stop-motion effects in your models. It&#39;s built using Shader Graph and it&#39;s compatible with Unity 2019.2, 2019.3 and... | [TVgZk](https://taletronic.gumroad.com/l/TVgZk) |
| 42 | REDSHIFT SHADER SUITE v.5 + REDSHIFT LIGHT SUITE v.5 + TT MO | jonpol | 139.00 | _page unavailable (HTTPError)_ | [milqk](https://trucateam.gumroad.com/l/milqk) |
| 43 | Retro Shaders Pro for Unity URP | Daniel Ilett | 23.99 | Instantly transform your game into a retro classic with this collection of PSX-style, N64-style, and CRT screen shaders and bring an old-school look to your... | [fnrbi](https://danielilett.gumroad.com/l/fnrbi) |
| 44 | Ripplor Plugin for Cinema 4D | Spenser Clark | 25.00 | Ripplor Real water interaction in Cinema 4D - without caching a fluid sim. (SEE VIDEO) Drop the deformer on any mesh and it becomes water. Objects push it... | [wvohg](https://sdimaging.gumroad.com/l/wvohg) |
| 45 | SafeSpace (VRChat Shader & Particle Filter) | KleineLuka 🌺 | 5.00 | VR can be overstimulating (or straight up annoying) - even without all the clutter of user&#39;s avatars and worlds&#39; effects. But.. safety limits are too strict... | [qgniq](https://kleineluka.gumroad.com/l/qgniq) |
| 46 | Sanctus Library - Procedural Materials and Assets Library fo | Sanctus | free | _page unavailable (HTTPError)_ | [fogcj](https://sanctus.gumroad.com/l/fogcj) |
| 47 | Screen Freeze Shader (Godot 4) | Mina Pêcheux | 6.00 | Fancy a little &quot;screen freeze&quot; shader for your next Godot game? With this simple GLSL shader, you&#39;ll be able to easily setup and configure an icy... | [femznt](https://mpecheux.gumroad.com/l/femznt) |
| 48 | Shader Toolbox: Graphs and Nodes for Unity URP | Daniel Ilett | 24.99 | Shader Toolbox for Unity URP adds production-ready shader effects including dithered transparency, Voronoi-based lava, and iridescent bubbles, complete with... | [tjlzf](https://danielilett.gumroad.com/l/tjlzf) |
| 49 | Shey Hair Shader | Shey | 10.00 | _page unavailable (HTTPError)_ | [kvuuz](https://shrenders.gumroad.com/l/kvuuz) |
| 50 | Simple Skybox Shader | TechSane | 3.00 | A Simple skybox shader with a few example presets to get you going! 25/09/26 - Added Sun options. Added moon option (Image). Includes a button in the shader... | [ybnjla](https://techsane.gumroad.com/l/ybnjla) |
| 51 | Skybox - (Plugin) | MrQuaxkers | 9.99 | 450+ Skybox library / browser for roblox studio. | [pjedcf](https://mrquaxkers.gumroad.com/l/pjedcf) |
| 52 | SkyCraft: Skybox Shader for VRChat & Unity | DX | 8.00 | Minecraft Sky in VRChat? Introducing SkyCraft, your personalized Minecraft-like Skybox Shader for VRChat World &amp; Unity! - 3 Beautiful Skyboxes Presets -... | [cdegf](https://dx30.gumroad.com/l/cdegf) |
| 53 | SkyMove: Skybox Shader for VRChat & Unity & Blender | DX | 8.00 | Bring your skyboxes to life in VRChat &amp; Unity &amp; Blender Transform your map&#39;s skybox using this easy-to-use and customizable Shader that adds life and... | [adrpwl](https://dx30.gumroad.com/l/adrpwl) |
| 54 | Snakeskin Tunnel / 2-in-1 TouchDesigner Gyroid Shader | Irina.ae | 10.00 | A real-time raymarched gyroid shader that never ends. Two .toe files included — one driven by MediaPipe hand tracking with three switchable colorways, one by... | [ngmfist](https://irinaught.gumroad.com/l/ngmfist) |
| 55 | Soft Outline Shader (VRChat) | Zekk | 13.59 | A shader designed to be used in VRChat! As its core is a shader, it is PC only! Please read the full product page before purchase &lt;3 If you enjoy this... | [exmcjh](https://zekk.gumroad.com/l/exmcjh) |
| 56 | Spark AR - Heart Bloom / Shader | Spark AR Shaders by De | 50.00 | Описание на русском — ниже. 🇺🇸 A unique effect that transforms lights into hearts. Try the demo: test link Adjustable size and light detection Compatible... | [njlAb](https://enuriru.gumroad.com/l/njlAb) |
| 57 | Stylized Medieval Inn Shader Pack for Blender 5 Cycles | 3D Tudor | 4.50 | _page unavailable (HTTPError)_ | [atisqm](https://3dtudor.gumroad.com/l/atisqm) |
| 58 | Stylized Water Shaders And Generator | Casey Sheep | 12.00 | CODE: SW25 Use code SW25 for a limited-time 25% OFF! Blender Add-onStylized Environment Tools Stylized Water Expressive, animated stylized water — no complex... | [jclot](https://caseysheep.gumroad.com/l/jclot) |
| 59 | TG Shaders: Updated Shaders for Assetto Corsa | Allies Motor House | 8.00 | Experimental Shaders Use with Caution! Linear Colour Space IS NOT SUPPORTED &amp; NEVER WILL BE!! USE Gamma Colour Space!!! Make every car look real. TG Shaders... | [mlpnj](https://threatjpn.gumroad.com/l/mlpnj) |
| 60 | Tiny Hair Shader | tinynocky | free | What is Tiny Hair Shader? Tiny Hair Shader is a fully procedural hair shader that works in both EEVEE and Cycles (Blender) Read before you purchase the... | [yhyuou](https://tinynocky.gumroad.com/l/yhyuou) |
| 61 | Udin Blender Shaders | UDIN | free | _page unavailable (HTTPError)_ | [fzvbo](https://udinbv.gumroad.com/l/fzvbo) |
| 62 | UE 5 Katana Toolkit : 30+ professional tools, materials, and | I am Wanderboy. | 24.90 | _page unavailable (HTTPError)_ | [azfnlg](https://xaviwanderboy.gumroad.com/l/azfnlg) |
| 63 | UE5 Procedural Regular Polygon Shader | HeyYo | 3.00 | UE5 material that draws regular polygons procedurally. The logic is basically implemented by HLSL, so you can easily reproduce it in other platforms or... | [nmusq](https://heyyohanashima.gumroad.com/l/nmusq) |
| 64 | Ultimate Blender Procedural Material Pack | Ryan King Art | 55.30 | Ultimate Blender Procedural Material Pack, pre-setup in Blender’s asset browser, with custom thumbnails, sorted catalogs, and customizable node groups. In my... | [gdkltz](https://ryankingart.gumroad.com/l/gdkltz) |
| 65 | Ultimate Metallic Silk: Interactive Molten Shader for Framer | Creative Apes | 10.00 | Digital luxury, in motion. The Ultimate Metallic Silk is a high-fidelity WebGL shader designed for designers who want to move beyond static backgrounds. It... | [pndod](https://creativeapes.gumroad.com/l/pndod) |
| 66 | Ultimate ShaderFuse Guide for DaVinci Resolve | Akascape | 20.00 | Learn to build Shader Fuses, convert Shadertoy shaders, add custom controls, and create your own Fusion effects, all in one course. Shader Fuses bring the... | [ohaswb](https://akascape.gumroad.com/l/ohaswb) |
| 67 | Unity VFX Graph - Level Up Effect | Gabriel Aguiar Prod | 5.00 | 12 Level Up Effects for Skinned Mesh Renderer done entirely with Visual Effect Graph. This package includes: -12 Level Up Effects (2 customizable VFX Graph)... | [alchf](https://gabrielaguiarprod1.gumroad.com/l/alchf) |
| 68 | Unity VFX Graph：Collision Edge Line(SDF) | Eric VFX Studio | 4.00 | Created using VFX Graph and SDF, particles can create irregular lines along their edges when in contact with SDF. Version：6000.0.3f1 Render Mode：HDRP... | [xybwbh](https://raywang4.gumroad.com/l/xybwbh) |
| 69 | Unity VFX Graph：Galaxy and Meteor | Eric VFX Studio | 7.99 | Galaxy and Meteor built using Unity VFX Graph, You can modify Galaxy&#39;s particle changes and Meteor&#39;s direction yourself. 2021.3.2f1 Render Mode：URP &amp; HDRP... | [hubvqv](https://raywang4.gumroad.com/l/hubvqv) |
| 70 | Unity VFX Graph：Lightning Trail | Eric VFX Studio | 10.00 | Drag lightning effect created using Unity VFX Graph, You can follow the target point and modify the length, color, jitter level, etc. 2022.3.45f1 Render... | [vvhpas](https://raywang4.gumroad.com/l/vvhpas) |
| 71 | Unity VFX Graph：Mesh Particle Fragments | Eric VFX Studio | 8.99 | Model particle effects created using Unity VFX Graph, You can modify the particle size, color, fluttering direction, etc. by yourself. 2023.1.0b12(up) Render... | [udgno](https://raywang4.gumroad.com/l/udgno) |
| 72 | Unity VFX Graph：Particle Character (Skinned Mesh) | Eric VFX Studio | 9.99 | Particle character effects created using Unity VFX Graph, You can modify particle size, color, flutter, etc. 2021.2.17f1 (up) Render Mode：HDRP Requires Unity... | [cwkeg](https://raywang4.gumroad.com/l/cwkeg) |
| 73 | Unity VFX Graph：Sci-fi Line | Eric VFX Studio | 3.00 | Sci-fi linework created using Unity VFX Graph. You can modify the line changes, size, color, direction, etc. by yourself. 2021.3.28f1(up) Render Mode：HDRP... | [eibuq](https://raywang4.gumroad.com/l/eibuq) |
| 74 | Unity VFX Graph：Waterfall(HDRP) | Eric VFX Studio | 7.50 | A waterfall made with the Unity VFX Graph. You can modify the number of particles, color, smoke, add collision zones, etc., and petal effects are also... | [slzhfx](https://raywang4.gumroad.com/l/slzhfx) |
| 75 | Volumetric Environment Shaders | Naito Ookami | 12.50 | Fog Volume/Fog Volume Lite The first shader is an extremely customizable fog shader with several variants for performance optimization. Shader variants are... | [QceXI](https://naitoookami.gumroad.com/l/QceXI) |
| 76 | VRChat Hypno Eyes Shader / 🌌 Somna Presets | Value 🌿 | 15.00 | Available for -20% HERE (Card and PayPal supported!) 🥴 The Hypno Shader for VRChat Avatars. 🎯 Focus DLC \| 💻 Screenspace DLC \| 📦 Material Preset Pack 🌍 Public... | [cwqvu](https://valuef.gumroad.com/l/cwqvu) |
| 77 | Warren's Fast Fur Shader | Warren | free | NOTE: IF (WHEN) YOU ENCOUNTER ANY BUGS, PLEASE LET ME KNOW ON THE DISCORD SERVER! Free &quot;Lite&quot; version available. Heavily-optimized for speed. Automatically... | [atntv](https://warrenwolfy.gumroad.com/l/atntv) |
| 78 | Water Shader Blender Add-on + Assets & Terrains | Chuck_CG | free | There are 2 versions Free &amp; Paid, please make sure to select the correct version. See what&#39;s new in the new 3.0 update: https://youtu.be/-FXA3nDJykg Create... | [sxbcnw](https://chuckcg.gumroad.com/l/sxbcnw) |
| 79 | YMA Toon Shader [RS + C4D] [DEPRECATED - C4D 2023 - XPresso  | You And Me Academy | 49.00 | ATTENTION DEPRECATED: YMA Toon Shader uses XPresso only and was custom built in 2023 before toon existed in Redshift. For 2026 modern Redshift Toon Materials... | [icujek](https://youmeacademy.gumroad.com/l/icujek) |
| 80 | 🌌 Domain Warp Noise Generator (GPU Compute Shader) | CyberLuna | free | Create flowing, organic domain-warped noise textures instantly using a GPU compute shader. The CyberLuna Domain Warp Noise Generator is a Unity Editor tool... | [acjge](https://cyberluna.gumroad.com/l/acjge) |
| 81 | 💦 VRChat Goo Shader 2.0 / 🌌 Somna Presets | Value 🌿 | 17.50 | Available for -20% HERE (Card and PayPal supported!) 💦 The droopy &amp; reactive VRChat goo &amp; slime shader 💦 💧 Owned 1.0 previously? Get your 100% or 50%... | [pzfmx](https://valuef.gumroad.com/l/pzfmx) |
| 82 | 📜 Worley Noise Generator (GPU Compute Shader) | CyberLuna | free | Generate high-quality tileable Worley noise textures instantly using a GPU compute shader. The CyberLuna Worley Noise Generator is a Unity Editor tool that... | [tnlsug](https://cyberluna.gumroad.com/l/tnlsug) |

## Rigging, skinning & animation (108)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 83 | 2D FX Animation Bundle – High-Impact Visual Effects for Anim | DucVu FX | 35.00 | ⚡ Subscribe for official store updates. I'm engineering something big behind the scenes. Stay tuned. 📢 Update 2026: FX List & Future Updates View the Update... | [yrryu](https://ducvu.gumroad.com/l/yrryu) |
| 84 | 2D Rigging Toolbox 4.0 | Motion Gears | 22.50 | _page unavailable (HTTPError)_ | [iqabgx](https://motiongears.gumroad.com/l/iqabgx) |
| 85 | 2D/3D Storyboarding MASTERCLASS - Creating Animatics in BLEN | Spitfire Storyboards | 250.00 | Are you looking to learn how to create 2D 3D storyboards and animatics using Blender and its awesome Grease Pencil tool? Then this is THE COURSE for you... | [tciowl](https://spitfirestoryboards.gumroad.com/l/tciowl) |
| 86 | AniMate Forge - all AniMate Add-ons Bundle | not that NDA | 89.00 | _page unavailable (HTTPError)_ | [lgvbxw](https://nda.gumroad.com/l/lgvbxw) |
| 87 | AniMate Pro - Core | not that NDA | 50.00 | _page unavailable (HTTPError)_ | [kxqdom](https://nda.gumroad.com/l/kxqdom) |
| 88 | Animated 3D Curve Graph in AE / Project File | Noble Kreative | 30.00 | Create an Animated 3D Curve Graph in Adobe After Effect using Stardust \| Stardust Tutorial series for VFX &amp; Motion Graphics \| ■ Easy to customize using... | [hQcfQ](https://noblekreative.gumroad.com/l/hQcfQ) |
| 89 | Animated RPG Health Bar | gfxcomet | 11.40 | A fully animated and customizable stylized Health Bar UI component for your Roblox game project! What&#39;s included? A health and stamina bar which you can... | [mohtug](https://gfxcomet.gumroad.com/l/mohtug) |
| 90 | Animated Toggle | gfxcomet | free | Enjoy this Animated Toggle UI for your own game project! Instructions: Make sure the script is placed in &quot;StarterPlayerScripts&quot; Add the tag &quot;ToggleComponen | [txoms](https://gfxcomet.gumroad.com/l/txoms) |
| 91 | Animation Snapper Pro - Blender Addon | Melowilo Animation | 24.99 | _page unavailable (HTTPError)_ | [rwyvce](https://melowilo.gumroad.com/l/rwyvce) |
| 92 | Animator Toolkit | TohruTheDragon | 20.00 | _page unavailable (HTTPError)_ | [oizdm](https://tohruthedragon.gumroad.com/l/oizdm) |
| 93 | Anime Codes | gfxcomet | 1.80 | A simple yet aesthetic Anime Codes UI inspired by the popular Roblox game &quot;Anime Last Stand&quot; What&#39;s Included? A textbox/field to enter your codes in A clean | [skjcnx](https://gfxcomet.gumroad.com/l/skjcnx) |
| 94 | Anime Egg Shop | gfxcomet | free | The perfect egg shop ui for your anime game project. What&#39;s Included? 6 item displays with rarity color coding Currency display with gem icon (from Currency... | [hkqiur](https://gfxcomet.gumroad.com/l/hkqiur) |
| 95 | Anime Hair HM Toolkit — Shadows & Highlights for Blender | Weytant_V | 15.20 | _page unavailable (HTTPError)_ | [gywiag](https://weytant.gumroad.com/l/gywiag) |
| 96 | Anime Health 3 | gfxcomet | 1.80 | A stylized anime health interface component for your next game project What&#39;s included? A stylistic design Avatar Frame (you can add an image or icon) The... | [batgd](https://gfxcomet.gumroad.com/l/batgd) |
| 97 | Anime Inventory 2 | gfxcomet | 4.80 | Meet the new Anime Inventory 2 This is a robust and stylized inventory interface which consists of: Unlocked and Locked item variants Stroke + Glow to... | [hmmdv](https://gfxcomet.gumroad.com/l/hmmdv) |
| 98 | Anime Quests | gfxcomet | 3.00 | A robust and aesthetic Anime Quests UI inspired by the popular Roblox game Anime Last Stand. What&#39;s Included? Gradients used to visually separate elements... | [stqzza](https://gfxcomet.gumroad.com/l/stqzza) |
| 99 | Anime Rewards UI for Roblox Studio (RBXM) | Kaisen | free | Elevate your Roblox game with the Anime Rewards UI a beautifully designed, anime-inspired user interface for reward systems! This script provides a visually... | [qogihq](https://claritykaisen.gumroad.com/l/qogihq) |
| 100 | Anime Settings | gfxcomet | 3.00 | A beautifully crafted Anime Settings interface inspired by the popular title Anime Last Stand What&#39;s Included Responsive List Sections: each section allows... | [ydgqz](https://gfxcomet.gumroad.com/l/ydgqz) |
| 101 | Anime Simulator 2 UI Kit | gfxcomet | 11.40 | Presenting the sequel to the Anime Simulator UI Kit! Looking to start your new anime game but don&#39;t know where to find good design? The Anime Simulator UI... | [hchgy](https://gfxcomet.gumroad.com/l/hchgy) |
| 102 | Anime Simulator Kit V2 | gfxcomet | 11.97 | Introducing the Anime Simulator UI Kit V2! The sequel to our Anime Simulator UI Kit, this one is fresh, new and improved, with the highest design quality... | [jibid](https://gfxcomet.gumroad.com/l/jibid) |
| 103 | Anime Stylized VFX - Unity | Vefects - Realtime VFX | 29.99 | _page unavailable (HTTPError)_ | [tfegu](https://vefects.gumroad.com/l/tfegu) |
| 104 | Anime Units | gfxcomet | 6.00 | A robust and aesthetic Anime Units ui inspired by the popular Roblox game &quot;Anime Last Stand&quot; This is a robust and comprehensive Anime Units interface that is... | [hwxbz](https://gfxcomet.gumroad.com/l/hwxbz) |
| 105 | AnimToTexture (VAT) One-Click Tool by tiedtke. | tiedtke. | 9.99 | _page unavailable (HTTPError)_ | [agfrjg](https://tiedtke.gumroad.com/l/agfrjg) |
| 106 | Arrow Shot VFX | HeyYo | 7.00 | A blazing arrow streaks across the field and strikes the enemy, bursting into a ring of light and scattering sparks. Made in Unreal Engine. I provide the... | [phxbo](https://heyyohanashima.gumroad.com/l/phxbo) |
| 107 | Audiomation for Unity animation | Pancake992 | 7.00 | _page unavailable (HTTPError)_ | [nxkih](https://pancake992.gumroad.com/l/nxkih) |
| 108 | basic scripts for the OverRig animation method | Pavel Barnev | 70.00 | _page unavailable (HTTPError)_ | [cIdFbR](https://pavelbarnev.gumroad.com/l/cIdFbR) |
| 109 | Blender Massive 250-Piece Modular Mega - Kitbash Immersive C | 3D Tudor | 18.00 | _page unavailable (HTTPError)_ | [bmbhc](https://3dtudor.gumroad.com/l/bmbhc) |
| 110 | Book Rigger | Tik Works | 15.00 | _page unavailable (HTTPError)_ | [vjcph](https://tikworks.gumroad.com/l/vjcph) |
| 111 | Bookasaur Rig | ComixProd. | free | This is my first rig made on timelapse! The rig is featuring Bookasaur, make sure to check him out since he&#39;s cool. Also I wanna say the rig is not fit for... | [YMeCo](https://comixproductions.gumroad.com/l/YMeCo) |
| 112 | CGDive: The Vault - Rigging and Animation Tutorials [SUBSCRI | Todor - cgdive.com | 6.00 | _page unavailable (HTTPError)_ | [ruyce](https://toshicg.gumroad.com/l/ruyce) |
| 113 | Cryomancy and Earthshaping (VRCHAT + Quest) | Liindy | 15.00 | Please rate this item if you buy it, this will vastly help me out by getting seen more, and will help fund more cool items like this one! ⭐⭐⭐⭐⭐ Alternate... | [gqvvuq](https://liindy.gumroad.com/l/gqvvuq) |
| 114 | Cubic Face (Roblox Face Rig) | ComixProd. | free | Cubic Face is a simple face rig I created. It was made in a video. No credit needed, however do not redistribute or claim ownership. If you want to share... | [crzat](https://comixproductions.gumroad.com/l/crzat) |
| 115 | DEM V3.1 — Procedural Animation System for Cinema 4D + Blend | Giuliano Dasky | 59.00 | NEW RELEASE — DEM V3.1 A NEW WAY TO ANIMATE IN CINEMA 4D A complete procedural animation system — build advanced motion with editable layers in a dedicated... | [kumrw](https://daskydesign.gumroad.com/l/kumrw) |
| 116 | EPIK RIG - Quick Rig + Animation Tools for Games (UE) | ShinGidora | 29.99 | _page unavailable (HTTPError)_ | [njrwka](https://shingidora.gumroad.com/l/njrwka) |
| 117 | Fluid Rig | ComixProd. | free | Latest Version: E2 This rig is designed for Blender, and it will not work in Roblox Studio. Fluid Rig is one of the best ROBLOX package rigs you can find for... | [iinfw](https://comixproductions.gumroad.com/l/iinfw) |
| 118 | Free Low Poly 3D Character - Juliet from Lollipop Chainsaw ( | Crashsune | free | What You’ll Get A fully rigged low-poly Juliet inspired by Lollipop Chainsaw ✨ Included in the download: Juliet (fully rigged) Her chainsaw Nick All assets... | [inljko](https://crashsune.gumroad.com/l/inljko) |
| 119 | FUGA - Imagined by Starkim1999 [VFX/VRChat] | Starkim1999 | 25.00 | This is an animation inspired by Sukuna&#39;s Fuga (Fire Arrow) from Jujutsu Kaisen. I took heavy inspiration from how Roblox games portray this effect, as well... | [gwsrd](https://starkim1999.gumroad.com/l/gwsrd) |
| 120 | Game Rig Tools (Blender Addon) - game-ready rigs in seconds | Todor - cgdive.com | free | _page unavailable (HTTPError)_ | [OmHCS](https://toshicg.gumroad.com/l/OmHCS) |
| 121 | Ghost Frames — Onion Skinning Plugin for Unreal Engine 5.8 | Aymen Selmi | 14.99 | _page unavailable (HTTPError)_ | [gyubxu](https://kazuyasama.gumroad.com/l/gyubxu) |
| 122 | Glock R6 Roblox Rig for Moon Animator | Nisky | free | Roblox R6 Rig with a Welded and fully animatable Glock 17 designed to be used with Moon Animator. | [yaavw](https://nisky.gumroad.com/l/yaavw) |
| 123 | Gridflow — Procedural Animated Grids | Rajat Subhra | 35.00 | _page unavailable (HTTPError)_ | [wpgzfh](https://rajatsubhra.gumroad.com/l/wpgzfh) |
| 124 | Happy Birthday Grimace! (Animation File + Animation Timelaps | Paribes | 10.00 | This file includes my animation file AND a timelapse which is not edited and not sped up of me animating this! (tipping is always appreciated! :)) PS: I... | [nbbxnn](https://paribes.gumroad.com/l/nbbxnn) |
| 125 | Hazem Rig | ComixProd. | 3.00 | This is the rig I made when making the "How To Make A Roblox Rig" tutorial series. If you want to explore what I made and find out more about how the rig... | [ppwik](https://comixproductions.gumroad.com/l/ppwik) |
| 126 | Houdini Animation Sequencer | bereg | 25.00 | _page unavailable (HTTPError)_ | [wyaanb](https://bereg.gumroad.com/l/wyaanb) |
| 127 | How To Design an Anime Inventory UI (Tutorial) | gfxcomet | 6.00 | This is a 41 minute comprehensive lesson where I walk you through step-by-step, the design and import of an Anime Inventory interface. You will learn how to... | [tceqo](https://gfxcomet.gumroad.com/l/tceqo) |
| 128 | How to Design An Anime Units UI in Roblox Studio | gfxcomet | 6.00 | This 53 minute tutorial follows the first part where we designed this Units frame from the game Anime Last Stand inside of Photoshop, which you can watch for... | [vjvcdvq](https://gfxcomet.gumroad.com/l/vjvcdvq) |
| 129 | HP Art Toolset: Facial Character Rigging for Maya | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [mqrebc](https://hparttoolset.gumroad.com/l/mqrebc) |
| 130 | HP Art Toolset: Fast Character Rigging for Maya | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [bmstj](https://hparttoolset.gumroad.com/l/bmstj) |
| 131 | i5K Rig | ComixProd. | free | A random GFX rig for i5K. What&#39;s cool is that this rig has better bends than all of my other rigs, so yeah 🤷‍♂️ No credit needed just don&#39;t claim ownership | [obfij](https://comixproductions.gumroad.com/l/obfij) |
| 132 | IK Grab | normalizedcrow | 12.00 | An avatar interaction system for VRChat Features Let other players grab your arms, legs, and head using VRChat&#39;s built-in IK for natural joint bending Pose... | [karln](https://normalizedcrow.gumroad.com/l/karln) |
| 133 | Industrial Sci-Fi and Modular Oil Rig | Sierra Division | 179.00 | _page unavailable (HTTPError)_ | [ikobf](https://sierradivision.gumroad.com/l/ikobf) |
| 134 | KTR - E.V.A. Suit from Dead Space RIG for Jerry | KTR | 22.00 | _page unavailable (HTTPError)_ | [hiwpa](https://kotyor.gumroad.com/l/hiwpa) |
| 135 | Launch Control  //  Auto Car Rig | Daniel Vesterbaek | 59.00 | _page unavailable (HTTPError)_ | [orzsz](https://danielvesterbaek.gumroad.com/l/orzsz) |
| 136 | Let’s learn ANIMATED CHARACTER  CREATION IN 3D | Ram@Crossmind | 34.30 | _page unavailable (HTTPError)_ | [gjpami](https://crossmindstudio.gumroad.com/l/gjpami) |
| 137 | Magma Rig (Blender 3.4+) | Paribes | free | This rig is a rig from a character in Roblox called "The Magma Fiend" including features like: - Brightness control - Magma Fiend's color - Fancy Feet on... | [embpw](https://paribes.gumroad.com/l/embpw) |
| 138 | Marik / Male / PC + Quest + Opti / VRCFT & VRCFury | Heartmarksman | 35.00 | Marik comes which MANY features not listed here, go to my discord linked below to see the full list of Toggles! 😏❤️ We also offer FREE Uploads if you can&#39;t... | [zuvneh](https://heartmarksman.gumroad.com/l/zuvneh) |
| 139 | Mechanical Rigging in Blender - A Beginner Course 🦾 | Niko | 19.90 | _page unavailable (HTTPError)_ | [zecxxb](https://demnikoart.gumroad.com/l/zecxxb) |
| 140 | MHFRT - Auto Facial Rig & Auto Retopology | Souhail Ninia | 24.99 | _page unavailable (HTTPError)_ | [pzqmlw](https://souhailninia.gumroad.com/l/pzqmlw) |
| 141 | Mixamo Rig 5 | Knit Motion | 5.00 | _page unavailable (HTTPError)_ | [fjidu](https://knitmotion.gumroad.com/l/fjidu) |
| 142 | Moon Animator 2 Plugin | kai | free | This was originally a paid plugin but its free to get here:) Best Roblox Studio animating plugin out there | [bbsmm](https://realestkai.gumroad.com/l/bbsmm) |
| 143 | Muscle Anatomy  - Ecorche Rigged Set | Alex Lashko | 99.00 | _page unavailable (HTTPError)_ | [fffeg](https://alexlashko.gumroad.com/l/fffeg) |
| 144 | Painterly + Animately Bundle DEAL! | Doughy Animation Studi | 34.50 | _page unavailable (HTTPError)_ | [qrdvwb](https://doughyanimation.gumroad.com/l/qrdvwb) |
| 145 | Physics animation (Plugin for Figma) | DAVV | 39.00 | _page unavailable (HTTPError)_ | [pfabo](https://davvstore.gumroad.com/l/pfabo) |
| 146 | PinRig / After Effects Plugin | What? Studio | free | _page unavailable (HTTPError)_ | [rvcux](https://whatstudio.gumroad.com/l/rvcux) |
| 147 | Profine's Roblox Toy Rig EDIT (Blender 4.0+) | Paribes | free | Profine made a Roblox toy rig a while back, I made a simple edit which has bone shapes and allat (this was mainly for me to have a better animating experience). | [udkwsf](https://paribes.gumroad.com/l/udkwsf) |
| 148 | Quick Start To Blender Animation: Professional Techniques An | VFX Grace | 198.00 | What Will You Learn? In the animation section, we will learn how to create walking and howling animations for a creature character in Blender. We will start... | [kavusr](https://vfxgrace.gumroad.com/l/kavusr) |
| 149 | R15 Roblox ANIMATION Rig (Blender -> Roblox Studio) | Paribes | free | A rig for Blender 3D to export to Roblox Studio! Settings HeadTarget HeadTarget Parent Torso IK Arm/Leg Settings IK/FK Switch Bone Layers (IK/FK) Fancy... | [zmyfl](https://paribes.gumroad.com/l/zmyfl) |
| 150 | R15 Roblox Starter Rigs (TEMPORARY) | Paribes | free | while waiting for the next starter rigs update, use these rigs if you need r15 here's the description of starter rigs: Introducing Roblox Starter Rigs, which... | [jjhtt](https://paribes.gumroad.com/l/jjhtt) |
| 151 | Rich Rig (Blender 3.4+) | Paribes | free | roblox rig for the Rich package. Blender version: 3.4+ SECOND THUMBNAIL BY CLIPON If you need rigs, contact me on Discord (chillingparibes)... | [xsgzm](https://paribes.gumroad.com/l/xsgzm) |
| 152 | Roblox Blocky Finger Rig (Blender 4.0+) | Paribes | free | fingies NOTE: FACE RIG IS NOT INCLUDED, THAT IS AEPBR EXCLUSIVE | [fpbjgc](https://paribes.gumroad.com/l/fpbjgc) |
| 153 | Roblox Blocky Rig / C4D R20+ | Chastling | 1.50 | Available on Gumroad | [ahkbz](https://chastling.gumroad.com/l/ahkbz) |
| 154 | Roblox Fat Rig (4.0+) | Paribes | free | _no description in metadata_ | [jiojiw](https://paribes.gumroad.com/l/jiojiw) |
| 155 | Roblox Football Rig V1 (Blender 4.2+) | Paribes | 10.00 | NOTE: redistributing or reselling the rigs, even if modified or at a price, is PROHIBITED. Muscle System The rig contains a special muscle system that is... | [ifhke](https://paribes.gumroad.com/l/ifhke) |
| 156 | Roblox Multipurpose Cloth Rig (4.5+) | Paribes | free | Features: Classic Cloth Modification - This modification is a top-tier cloth simulation rig that bakes the shirt, providing realistic cloth physics... | [hwthor](https://paribes.gumroad.com/l/hwthor) |
| 157 | Roblox Ocean System | Tekleed | 200.00 | Roblox FFT Ocean System Real ocean simulation for Roblox. This uses the FFT wave technique behind AAA oceans like Sea of Thieves, running natively on... | [qgvvc](https://tekleed.gumroad.com/l/qgvvc) |
| 158 | Roblox Rig Vault (Blender 4.0+) | Paribes | free | Introducing Roblox Rig Vault! Roblox Rig Vault (RRV) is a unique Blender rig pack and addon made by Roblox rigging innovators ChillingParibes and Comix... | [htzgj](https://paribes.gumroad.com/l/htzgj) |
| 159 | Roblox Rigs Suite | ComixProd. | free | Thanks to @BricksBree, @ChillingParibes, @MrSonicTeam, @MXFlamez, @Koth for beta testing this! I would really appreciate it if you donated, it's taken me... | [xpqyw](https://comixproductions.gumroad.com/l/xpqyw) |
| 160 | Roblox Starter Rigs (Blender 3.4+) | Softy | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [ytmdjz](https://softgb.gumroad.com/l/ytmdjz) |
| 161 | Roblox Starter Rigs (Blender 3.4+) | Paribes | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [pblgq](https://paribes.gumroad.com/l/pblgq) |
| 162 | Roblox Starter Rigs 1.0 MODDED | Paribes | free | Starter rigs by SoftGB & ChillingParibes Modified rigs by imbob02 (seamless boy rigs) R15 rig by BaconofVibes Compiled by Malakai_GFX If you need rigs... | [xbrdsa](https://paribes.gumroad.com/l/xbrdsa) |
| 163 | Roblox Studio: Movement system (8 directions) | LionDev | 12.00 | This package for Roblox Studio includes a movement system that detects the direction in which the character is moving and plays the appropriate animations... | [cddbt](https://liondev.gumroad.com/l/cddbt) |
| 164 | Roblox Woman Blocky Legs Rig (Blender 4.0+) | Paribes | free | If you need rigs, contact me on Discord (chillingparibes)! https://discord.com/invite/Mc5PdfZnBd NOTE: redistributing or reselling the rigs, even if modified... | [oqjvxf](https://paribes.gumroad.com/l/oqjvxf) |
| 165 | Scene Auditor Pro — Analyze, Clean & Optimize Blender Scenes | Chowdhury Tarul Ahsan | 15.00 | Saves hours of manual troubleshooting by instantly mapping, validating, and safely purging hidden asset bloat in Blender 5.0 - 5.2 Scene Auditor Pro... | [yvydx](https://tarulahsanbd.gumroad.com/l/yvydx) |
| 166 | Seraph Wings — Animated Six-Wing VRChat Accessory / PCVR | KuroLabs | 15.00 | _page unavailable (HTTPError)_ | [fetsbo](https://rajcu.gumroad.com/l/fetsbo) |
| 167 | SimpleAnime - Fast Anime / Retro Texturing | Nhance School | 19.00 | SimpleAnime - Easy Anime / Retro texturing Create stunning texturing results on your 3D Models + speed up workflow with SimpleAnime filter🎨 SimpleAnime was... | [dptffu](https://nhanceschool.gumroad.com/l/dptffu) |
| 168 | Spider-Man Roblox Rig (4.4+) | Paribes | free | credits to @imbob02 , @BallzyGFX and @xmavster on Twitter for making this Starter Rigs mod! | [ogunp](https://paribes.gumroad.com/l/ogunp) |
| 169 | Stadium Spectators: High Performance Stadium Crowds for Unre | RT ArtFast | 150.00 | _page unavailable (HTTPError)_ | [oannzl](https://tartfast.gumroad.com/l/oannzl) |
| 170 | Stylized Character Modeling for Animation | Stephen Anderson | 100.00 | Stylized Character Modeling for Animation is all about character design and application in production modeling for the animation pipeline. This self-paced... | [hqtmF](https://smaartist.gumroad.com/l/hqtmF) |
| 171 | SuperRoblox (Roblox Rig) | ComixProd. | free | Superhero rig with a load of settings. | [jFnRyz](https://comixproductions.gumroad.com/l/jFnRyz) |
| 172 | Talia + Adam - Maya Rig Bundle | Red Crow Studio | 68.00 | _page unavailable (HTTPError)_ | [xfplhw](https://manuelaf.gumroad.com/l/xfplhw) |
| 173 | Texter - Text Animation Tool for Blender | Graffinity | free | _page unavailable (HTTPError)_ | [tquro](https://graffinity3d.gumroad.com/l/tquro) |
| 174 | The Nature Generator | Andreas Dürr | 85.00 | YOUR ENTIRE ENVIRONMENT LIBRARY — GENERATED IN BLENDER SEE FOR YOURSELF IN THIS VIDEO, I’LL WALK YOU THROUGH ALL THE FEATURES OF THE NATURE GENERATOR 100%... | [gzyaj](https://cinematiccookie.gumroad.com/l/gzyaj) |
| 175 | The Ultimate Guide to Blender 3D Rigging and Animation | 3D Tudor | 11.25 | _page unavailable (HTTPError)_ | [irfmu](https://3dtudor.gumroad.com/l/irfmu) |
| 176 | Throw Food For Animals Template | ROKITS | 9.99 | Throw Food for Animals \| Roblox Template Train your strength, throw food farther, and collect animals to build your income! What’s Included 🐾 40 collectible... | [pyycl](https://rokits.gumroad.com/l/pyycl) |
| 177 | UI Animator Pro / After Effects Plugin | What? Studio | free | _page unavailable (HTTPError)_ | [xariqf](https://whatstudio.gumroad.com/l/xariqf) |
| 178 | Ultimate 2D FX Explosions for Animators & Devs | DucVu FX | 20.00 | _page unavailable (HTTPError)_ | [rfhalq](https://ducvu.gumroad.com/l/rfhalq) |
| 179 | Ultimate 2D FX Fire Animation Pack for Creators & Devs | DucVu FX | 20.00 | _page unavailable (HTTPError)_ | [menshz](https://ducvu.gumroad.com/l/menshz) |
| 180 | Ultimate Roblox Rig | MattRBX | 5.00 | IF YOU DIDN'T RECIEVE THE PRODUCT OR HAVE SIMILAR ISSUES JOIN THE DISCORD SERVER BELOW !! Support Server: https://discord.gg/DvK73fgEka Ultimate Rig Premium... | [lnldn](https://mattrbx.gumroad.com/l/lnldn) |
| 181 | Ultimate Weapon Sweep VFX !! [Houdini 19-20 / Niagara UE Cou | Tristan Gybels | 30.00 | This course tackles one of the most common problems but yet unheard of solutions for creating incredibly precise weapon sweep VFX. Unlike similar tutorials... | [qbfhe](https://tristangybels.gumroad.com/l/qbfhe) |
| 182 | Unreal Engine 5 Massive 250-Piece Modular Mega - Kitbash Imm | 3D Tudor | 18.00 | _page unavailable (HTTPError)_ | [rapdi](https://3dtudor.gumroad.com/l/rapdi) |
| 183 | Weight Scatter - (Plugin) | MrQuaxkers | 4.99 | Weight based object scattering in roblox studio. | [vhxkmj](https://mrquaxkers.gumroad.com/l/vhxkmj) |
| 184 | Worm Host Animation | Satch Nomad | 20.00 | This is a custom animation that can be easily transfered over to the custom character model of your choice. the "Worm Host", is a 3D combat/ability splash... | [racij](https://n5studios.gumroad.com/l/racij) |
| 185 | Zazar - Rigged 3D Lizard for Blender | Rakenval | 60.00 | Meet Zazar, a fully rigged, expressive 3D Lizard ready to leap into your Blender projects ! From subtle blinks to dramatic screams, this rig will let you... | [ynfspb](https://rakenval.gumroad.com/l/ynfspb) |
| 186 | ⚽ Roblox Football/Soccer Rigs (Kit, Shoes, Trophies, ...) | Paribes | free | credit: @ChillingParibes - the rig @SoftGB - HD Faces @imbob02 - modified seamless boy rig vansire - football stuff on the rig and the boot textures... | [ovwtcn](https://paribes.gumroad.com/l/ovwtcn) |
| 187 | 🎮 Legendary Sky Champion Rig (Roblox: The Games) | Paribes | free | "Defeat" will be forever erased from your vocabulary. A brand new rig for the package Roblox released For Blender 4.2+ (probably works for minimum 4.0+) | [yowflf](https://paribes.gumroad.com/l/yowflf) |
| 188 | 🏃 Roblox Animation Starter Pack | Paribes | free | A bunch of assets you could possibly need to start as an animator! | [knclku](https://paribes.gumroad.com/l/knclku) |
| 189 | 🤖 AEPBR Roblox Rig (BETA) | Paribes | free | 🤖 STILL IN BETA!! Features it has so far: ☑️ Customisable face rig Customisable Eye Color Hideable Parts Face controls Mouth Sync Control Blink Control Teeth... | [wvyryw](https://paribes.gumroad.com/l/wvyryw) |
| 190 | 🧟 Roblox Zombie Rig (Blender 4.0+) | Paribes | free | zombie PS: The best works of Softy and STAR's contest will end up on this page as well! EDIT: Winning GFX has been added, made by @vanziervh If you need... | [quhwki](https://paribes.gumroad.com/l/quhwki) |

## Modeling, mesh & procedural (31)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 191 | [Addon]MESHmachine | machin3 | 44.99 | _page unavailable (HTTPError)_ | [Gwgt](https://machin3.gumroad.com/l/Gwgt) |
| 192 | Avatar Protection System for VRChat | Dextro | 20.00 | SCRAMBLED MESH WILL NEVER BE VISIBLE, VIDEO IS SIMPLIFIED FOR DEMONSTRATION This asset is also available on Jinxxy for 10% off: Avatar Protection System on... | [gxayd](https://dextrovr.gumroad.com/l/gxayd) |
| 193 | CGE Sculpting Tool for Maya | CGElementary | 78.40 | Please note this is a perpetual license, not a subscription; you pay once and can use it forever. Stop round-tripping to other Apps. A complete... | [lkvikqt](https://cgelementary.gumroad.com/l/lkvikqt) |
| 194 | Cloud Creator / Blender Geometry Nodes Tool | Adrien Latran | free | _page unavailable (HTTPError)_ | [qcppwq](https://adrienltn.gumroad.com/l/qcppwq) |
| 195 | Cobweb Generator Pro | Jose Leon Molfino | free | Houdini Cobweb Generator Pro - It generates cobwebs procedurally from a collider geometry, from your own straight lines, or both. This is a full rewrite of... | [zbrsd](https://cmolfino.gumroad.com/l/zbrsd) |
| 196 | Easy Terrain Generator | kollapse3d | 4.99 | Also available on Superhive Create easily any kind of terrain in no time with this geometry nodes terrain generator. Just play with all the sliders in the... | [qcmfh](https://kollapse3d.gumroad.com/l/qcmfh) |
| 197 | EDGY - Worn Edges Plugin for Cinema 4D & Blender | Cornelius Dämmrich | 15.00 | Edgy is a plugin for Cinema 4D and Blender. It cuts damage into the edges and surfaces of a closed mesh. Edgy modifies the mesh itself. It does not use a... | [fyhsz](https://corneliusdammrich.gumroad.com/l/fyhsz) |
| 198 | Extra Nodes for Geometry Nodes | 3dsinghvfx | free | _page unavailable (HTTPError)_ | [aaxrtj](https://3dsinghvfx.gumroad.com/l/aaxrtj) |
| 199 | EzyTopo - Retopology tool for Maya | Justin Kirkwood | 16.99 | _page unavailable (HTTPError)_ | [otyqu](https://justinkirkwood.gumroad.com/l/otyqu) |
| 200 | Hiddenfy 6 — Hard-Surface Armor, IMM system, Tactical Cloth  | Daniel Arcos Escobar | 10.50 | _page unavailable (HTTPError)_ | [ebbxj](https://darksurfacetv.gumroad.com/l/ebbxj) |
| 201 | hood release system | chedsapp | 4.00 | visuals shown are placeholders, meant to be replaced by your own meshes. | [pdnoc](https://chedsapp.gumroad.com/l/pdnoc) |
| 202 | Houdini Tutorial Procedural Pillar Generation | Radu Cius | 45.00 | _page unavailable (HTTPError)_ | [btbwd](https://rart.gumroad.com/l/btbwd) |
| 203 | MEDUSA NODES - Procedural Hair System for Blender (Beta) | Irakli Kupunia | 15.00 | IMPORTANT: Development is currently on hold. Keep in mind that this addon is not production-ready yet and has lots of issues! You will most certainly... | [XEzSy](https://ikakupa.gumroad.com/l/XEzSy) |
| 204 | PatchGAP - Plasticity Retopology tool for Blender | Andrei Bezgodov | 35.00 | _page unavailable (HTTPError)_ | [ildlkt](https://bezgod.gumroad.com/l/ildlkt) |
| 205 | Procedural City Generator for Houdini / by MrShark (UPDATED  | Mr.Shark | 15.00 | _page unavailable (HTTPError)_ | [bpdiq](https://mrshark.gumroad.com/l/bpdiq) |
| 206 | Procedural Damage + Imperfections (Blender Geometry-Nodes) | Alex Martinelli | free | A Blender file with Geometry-Nodes (GN) modifier to procedurally add damage and imperfections to any mesh. Requires Blender &gt;=5.0. Have questions or want to... | [tkbjk](https://sagado.gumroad.com/l/tkbjk) |
| 207 | Procedural Pipes & Roads (Godot 4) | Mina Pêcheux | 7.00 | Want to create some instant pipes or roads in your Godot 3D scenes using just a simple Path3D node? This addon is for you! With the Procedural Pipes &amp; Roads... | [bmobcx](https://mpecheux.gumroad.com/l/bmobcx) |
| 208 | Procedural Thunder | HeyYo | 7.00 | _page unavailable (HTTPError)_ | [mycyh](https://heyyohanashima.gumroad.com/l/mycyh) |
| 209 | Procedural Urban Building Generator for Houdini (HDA) | Radu Cius | 39.00 | _page unavailable (HTTPError)_ | [civgek](https://rart.gumroad.com/l/civgek) |
| 210 | Project Damage / Procedural Destruction Toolkit [Blender Add | Lazy3D Blender | free | _page unavailable (HTTPError)_ | [wwwauu](https://lazy3d.gumroad.com/l/wwwauu) |
| 211 | Quadremsh Tools for Blender — Fast Quad Remeshing & Retopolo | SyncTools Pro — Cross- | free | _page unavailable (HTTPError)_ | [svwvny](https://synctools.gumroad.com/l/svwvny) |
| 212 | Spall: Procedural Damage for Blender | Alberto Cordero | 29.00 | _page unavailable (HTTPError)_ | [ttqrme](https://albertocgart.gumroad.com/l/ttqrme) |
| 213 | SpiralForge – Procedural Galaxy Builder for Blender | Petr Chekushkin | free | Build an entire galaxy in one click - then make it truly yours. SpiralForge is a fully procedural galaxy generator for Blender, built entirely with Geometry... | [qlafqt](https://astrodemiurge.gumroad.com/l/qlafqt) |
| 214 | Stacking Stones — Procedural Rock Walls & Ruins in Houdini ( | Hugo Beyer | 29.00 | _page unavailable (HTTPError)_ | [jsepsh](https://hugobeyer.gumroad.com/l/jsepsh) |
| 215 | Stylized Sky World Generator | Rei | 18.00 | 360° procedural Stylized Sky World in one click Making a stylized sky for 3D scenes usually takes heavy node tweaking and volumetrics, or painting a full... | [vaznyj](https://reipart.gumroad.com/l/vaznyj) |
| 216 | TFMSTYLE Addon Collection for Blender | TFMSTYLE | 8.99 | The TFMSTYLE Addon Collection is a unified ecosystem of creative tools for Blender. Built from the ground up to streamline procedural design, visualization... | [faifq](https://tfmstyle.gumroad.com/l/faifq) |
| 217 | The Big Nodebook: A Geometry Nodes Guide | MTR Animation | 19.99 | _page unavailable (HTTPError)_ | [hzsqw](https://mtranimationgumroad.gumroad.com/l/hzsqw) |
| 218 | Tutorial series - Procedural Cliffs with SideFX houdini | adrienlambert | 10.00 | !! project files / Tools : Houdini 18 Indie only !! This new tutorial series should be particularly exciting if you are looking to generate procedural cliffs... | [pYaGH](https://adrienlambert.gumroad.com/l/pYaGH) |
| 219 | Unreal Engine Procedural Damage Toolset | Hoj Dee | 19.99 | _page unavailable (HTTPError)_ | [vsykco](https://hojdee.gumroad.com/l/vsykco) |
| 220 | Unreal Engine Procedural Snow Toolset | Hoj Dee | 19.99 | _page unavailable (HTTPError)_ | [jixnf](https://hojdee.gumroad.com/l/jixnf) |
| 221 | UV Unfoldr – A Modern UV Editor for 3ds Max | Sargis Ter-Grigoryan | 39.00 | _page unavailable (HTTPError)_ | [nnwzju](https://sargisstg.gumroad.com/l/nnwzju) |

## VFX & simulation (33)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 222 | 200 FX Alpha VFX Asset Library | Comp Academy | 150.00 | _page unavailable (HTTPError)_ | [bgnny](https://compacademy.gumroad.com/l/bgnny) |
| 223 | Background Birds - Drag-and-Drop Niagara Bird System for Unr | Josh Toonen | 25.00 | _page unavailable (HTTPError)_ | [yyrmy](https://unrealforvfx.gumroad.com/l/yyrmy) |
| 224 | Blood VFX - Unreal Engine | Vefects - Realtime VFX | 57.99 | _page unavailable (HTTPError)_ | [qmvvfa](https://vefects.gumroad.com/l/qmvvfa) |
| 225 | Chain Simulation in Niagara - Create Mario's Chain Chomp | HeyYo | 7.00 | This is a Chain Simulation Niagara asset. I created Mario's Chain Chomp as an example to show how the chain simulation works. Both ends of the chain are... | [noiblu](https://heyyohanashima.gumroad.com/l/noiblu) |
| 226 | Droplet Generator 3 for Blender | ibotpl | 19.00 | Bugfix Release Version 3.0.4 Fixed simulation not working in certain situations Bugfix Release Version 3.0.3 Fixed crash when baking the simulation Bugfix... | [alvgr](https://ibotpl.gumroad.com/l/alvgr) |
| 227 | Fire Slash VFX | HeyYo | 15.00 | I made Fire Slash VFX as my personal work. I provide the whole UE data of this VFX so that you can explore, study, modify, and utilize the data for any... | [uajdj](https://heyyohanashima.gumroad.com/l/uajdj) |
| 228 | Flux Particle Studio / Blender | R Animation Studios | 29.00 | Flux — Particle Simulator + Blender Addon Design particle systems in your browser. Send them to Blender in one click. Flux is a real-time, browser-based... | [wtgjlc](https://ranimationstudios.gumroad.com/l/wtgjlc) |
| 229 | Fumaris — GPU Smoke & Fire Simulation for Blender | Venous_FX | 39.00 | Smoke and fire you can direct while it simulates Watch the simulation run in the Blender viewport, lit by your scene, and change it while it plays. When the... | [sszyf](https://venousfx.gumroad.com/l/sszyf) |
| 230 | Magic Spell VFX System | Digital Dungeon Assets | 124.99 | _page unavailable (HTTPError)_ | [ozbpme](https://dungeonforge.gumroad.com/l/ozbpme) |
| 231 | MPMStudio Solver - Particle simulation plugin for C4D & BLEN | RiverExtend | 35.00 | _page unavailable (HTTPError)_ | [kwttbt](https://riverextend.gumroad.com/l/kwttbt) |
| 232 | Next Gen Destruction Toolkit for Unreal Engine 5 | Kristian Kebbe | 44.99 | _page unavailable (HTTPError)_ | [fjpon](https://lucendev.gumroad.com/l/fjpon) |
| 233 | PCOPs - GPU Enabled Particle Simulation Tools in Houdini | Inside The Mind | 35.00 | _page unavailable (HTTPError)_ | [kpysmy](https://insidethemindspace.gumroad.com/l/kpysmy) |
| 234 | Pro Particles - Advanced Blender Particle System Add-on v5 | Cg-Flow | 51.35 | _page unavailable (HTTPError)_ | [qzaiz](https://cgflow.gumroad.com/l/qzaiz) |
| 235 | Standing Fire [Medium Scale] VFX Asset Bundle [x10] | Ben Harker | VFX | 15.00 | This bundle includes fully loopable VFX elements, built for maximum flexibility across film, game, and real-time projects! What’s inside: ✅ EXR image... | [bnizsn](https://benharkervfx.gumroad.com/l/bnizsn) |
| 236 | Unity VFX Graph - Muzzle Effects Vol. 1 | Gabriel Aguiar Prod | 10.00 | Here&#39;s the whole project created for the Muzzle Flash video tutorial. 10 Muzzle Effects done entirely with Visual Effect Graph. This package includes: -10... | [lkcfx](https://gabrielaguiarprod1.gumroad.com/l/lkcfx) |
| 237 | Unity VFX Graph - Stylized Laser Beams Vol. 1 | Gabriel Aguiar Prod | 10.00 | Here&#39;s the whole project created for the Stylized Beam video. 14 Stylized Laser Beams done entirely with Visual Effect Graph. This package includes: -14... | [jrdekb](https://gabrielaguiarprod1.gumroad.com/l/jrdekb) |
| 238 | Unity VFX Graph - Weapon Effects Vol. 1 | Gabriel Aguiar Prod | 10.00 | 19 Weapon Effects done entirely with Visual Effect Graph. Here&#39;s the whole project created for the Weapon Effect video tutorial. This project includes: -19... | [mmckxd](https://gabrielaguiarprod1.gumroad.com/l/mmckxd) |
| 239 | Unity VFX Graph：Attractor Force and Particle Trail effect | Eric VFX Studio | 8.00 | Created using Unity VFX Graph, the trailing line effects can follow the target point and can be modified in length or jitter degree, etc. Detailed... | [kbffp](https://raywang4.gumroad.com/l/kbffp) |
| 240 | Unity VFX Graph：Disturbed Image Particles | Eric VFX Studio | 9.99 | Particle picture effects created using Unity VFX Graph, You can add pictures yourself, modify particle size, color, jitter amplitude, etc. Detailed... | [wzdfe](https://raywang4.gumroad.com/l/wzdfe) |
| 241 | Unity VFX Graph：Image Fireworks | Eric VFX Studio | 8.99 | Unity VFX Graph - Image Fireworks Unity Version：2020.3.37f1(HDRP) Use Unity VFX Graph to create special effects pattern fireworks. You can import images to... | [ejzku](https://raywang4.gumroad.com/l/ejzku) |
| 242 | Unity VFX Graph：Particle shaping application(SDF) | Eric VFX Studio | 9.00 | Particle shaping effects made with VFX Graph. There are three application examples. You can change the SDF file and the number, color and attractiveness of... | [jhrat](https://raywang4.gumroad.com/l/jhrat) |
| 243 | Unity VFX Graph：Particles Attraction | Eric VFX Studio | 8.00 | Made using Unity VFX Graph so that particles can follow the target point. You can modify the particle size, color, fluttering direction, etc. by yourself... | [qiqwkbw](https://raywang4.gumroad.com/l/qiqwkbw) |
| 244 | Unity VFX Graph：Post-it(Particles aggregate into models) | Eric VFX Studio | 7.99 | Post-it effect created using Unity VFX Graph, You can use your own model to create different SDF files and give them the same sticky note effects. You can... | [fjnqc](https://raywang4.gumroad.com/l/fjnqc) |
| 245 | Unity VFX Graph：SDF Model Particle Deformation | Eric VFX Studio | 7.99 | Model particle aggregation effect created using Unity VFX Graph and produced through SDF You can add new SDF files and modify the model particle size, color... | [mcstjd](https://raywang4.gumroad.com/l/mcstjd) |
| 246 | Unity VFX Graph：Use SDF to make model particle effects | Eric VFX Studio | 9.99 | Made using Unity VFX Graph, with the model special effects generated by the SDF function, you can change the model to create different effects. Detailed... | [kehpsj](https://raywang4.gumroad.com/l/kehpsj) |
| 247 | Unreal 5 Advanced Niagara | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [wkvru](https://tharlevfx.gumroad.com/l/wkvru) |
| 248 | Unreal 5 Intro to Niagara | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [yvgfg](https://tharlevfx.gumroad.com/l/yvgfg) |
| 249 | Unreal 5 Niagara Bundle | tharlevfx | 125.00 | _page unavailable (HTTPError)_ | [czhuq](https://tharlevfx.gumroad.com/l/czhuq) |
| 250 | Unreal 5 Niagara Sim Stages | tharlevfx | 50.00 | _page unavailable (HTTPError)_ | [ufmqh](https://tharlevfx.gumroad.com/l/ufmqh) |
| 251 | Unreal Engine 4.22 Niagara Dissolution Effect | ArtHiteca | 15.00 | _page unavailable (HTTPError)_ | [AzoNY](https://arthiteca.gumroad.com/l/AzoNY) |
| 252 | Unreal Engine 4.22 Niagara Test Examples #1 | ArtHiteca | 20.00 | _page unavailable (HTTPError)_ | [SvcVn](https://arthiteca.gumroad.com/l/SvcVn) |
| 253 | VFXGen — Stylized VFX Texture Editor | ChunHu | 29.99 | _page unavailable (HTTPError)_ | [frhhpp](https://chunhuvfx.gumroad.com/l/frhhpp) |
| 254 | WebGL Magnetic Field: Interactive Particle Engine for Framer | Creative Apes | 8.00 | Add physical tension to your digital canvas. The WebGL Magnetic Field is a production-ready Three.js engine built for designers who need more than just a... | [dqgfpw](https://creativeapes.gumroad.com/l/dqgfpw) |

## Engine tooling: Unity / Godot / Unreal (38)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 255 | 1900s Office (Unreal Engine) | Leartes Studios | 69.99 | _page unavailable (HTTPError)_ | [zjvzpa](https://leartesstudios.gumroad.com/l/zjvzpa) |
| 256 | 2D Modern Pack - SPUM Premium AddOn (Unity Addition) | SOONSOON | 19.99 | _page unavailable (HTTPError)_ | [sbdqj](https://soonsoon.gumroad.com/l/sbdqj) |
| 257 | [v1.3] Hash Studios Alcohol Drinks [UdonSharp] [SDK3] | Hash Studios LLC | 49.99 | Description Introducing Hash Studios Alcohol Drinks—the ultimate Unity Udon prefab for immersive, interactive VRChat drinking experiences! Create, mix, and... | [dcggw](https://hashstudiosllc.gumroad.com/l/dcggw) |
| 258 | Asset Downgrader for Unreal Engine 5 | Ciprian Stanciu | 34.99 | _page unavailable (HTTPError)_ | [igbejz](https://relativegames.gumroad.com/l/igbejz) |
| 259 | AWS GameLift Client Plugin by eelDev for Unreal Engine | eelDev | 45.00 | _page unavailable (HTTPError)_ | [fbozz](https://eeldev.gumroad.com/l/fbozz) |
| 260 | Blender Godot 4 Pipeline Add-on | Michael Burt | 5.00 | _page unavailable (HTTPError)_ | [alpunq](https://michaeljared.gumroad.com/l/alpunq) |
| 261 | Blender Godot Suffixes (Addon) by Suzuka Ka | Suzuka Ka | 2.00 | _page unavailable (HTTPError)_ | [yvzxt](https://orb91.gumroad.com/l/yvzxt) |
| 262 | Blender To Game Engine (Unity, Unreal & Godot) Bundle | karan@b3dhub | 42.50 | _page unavailable (HTTPError)_ | [najqn](https://b3dhub.gumroad.com/l/najqn) |
| 263 | Blender to Unreal Engine 5: Build a Stylized Greek Island En | 3D Tudor | 11.25 | Greek-island-inspired village with white plaster buildings Overview Your Assets Are Not the Problem. The Missing System Is. You can model a door. You can... | [vmbyjm](https://3dtudor.gumroad.com/l/vmbyjm) |
| 264 | Blender to Unreal Engine 5: Playable Stylized Turret | 3D Tudor | 11.25 | Getting a clean model into Unreal Engine is usually the point where a tidy Blender project starts confessing everything it has been hiding. The upper body... | [whfxr](https://3dtudor.gumroad.com/l/whfxr) |
| 265 | Cloud Forge Complete 1.4.3 Unreal Engine 5.3 - 5.6 - VDB Clo | Arghanion's Puzzlebox | 24.99 | _page unavailable (HTTPError)_ | [fkjic](https://arghanion.gumroad.com/l/fkjic) |
| 266 | Cloud Forge Vol 2 - Unreal Engine 5.3 - 5.6 - VDB Clouds | Arghanion's Puzzlebox | 10.99 | _page unavailable (HTTPError)_ | [fxwqc](https://arghanion.gumroad.com/l/fxwqc) |
| 267 | Cloud Forge Volume 3 - Unreal Engine 5.3 - 5.6 - VDB Clouds | Arghanion's Puzzlebox | 12.99 | 💢 VIDEO: TUTORIAL 💢 CINEMATIC: TRAILER 💢 CLOUD SPAWNER: TRAILER Unreal Engine Versions Supported: 5.3 / 5.4 / 5.5 VDB Cloud Kit - Volume 03 Here you will... | [plicg](https://arghanion.gumroad.com/l/plicg) |
| 268 | Collision Splitter for Maya -> Unreal Engine | Honey3D | free | _page unavailable (HTTPError)_ | [atvjq](https://raditsys.gumroad.com/l/atvjq) |
| 269 | Complete Masterclass for Creating Cinematic Games in Unreal  | CGDealers | 39.90 | _page unavailable (HTTPError)_ | [nluov](https://cgdealers.gumroad.com/l/nluov) |
| 270 | Creating a metro train interior in Unreal Engine 5 | FastTrack Tutorials | 29.99 | _page unavailable (HTTPError)_ | [coMXC](https://fasttracktutorials.gumroad.com/l/coMXC) |
| 271 | EOSCore (Epic Online Services) Plugin for Unreal Engine | eelDev | 65.00 | _page unavailable (HTTPError)_ | [aoGtA](https://eeldev.gumroad.com/l/aoGtA) |
| 272 | Ezreal Slashes Vol.1 - Unreal Engine | Gabriel Aguiar Prod | 12.00 | _page unavailable (HTTPError)_ | [yizfn](https://gabrielaguiarprod1.gumroad.com/l/yizfn) |
| 273 | Flipbook Tool - Looping flipbook textures for Unreal Engine | henlo | free | _page unavailable (HTTPError)_ | [SQnwg](https://henlo.gumroad.com/l/SQnwg) |
| 274 | French Quarter Street Environment (Unreal Engine) | Leartes Studios | 69.99 | _page unavailable (HTTPError)_ | [homxva](https://leartesstudios.gumroad.com/l/homxva) |
| 275 | Godot 4 AutoSave Plugin — Periodic & On-Event Save System (G | OccaSoftware | free | _page unavailable (HTTPError)_ | [ogxgd](https://occasoftware.gumroad.com/l/ogxgd) |
| 276 | How to make a movie in Unreal Engine 5 Beginners Edition (Up | JSFILMZ | 19.99 | _page unavailable (HTTPError)_ | [mdwrk](https://jsfilmz.gumroad.com/l/mdwrk) |
| 277 | NameFrame 1.0 for Unreal Engine 5.8 | NameFrame | 149.00 | _page unavailable (HTTPError)_ | [vuaozu](https://nameframe.gumroad.com/l/vuaozu) |
| 278 | RevoltGPT Plugin for Unreal Engine 5 | RevoltGPT | 79.99 | _page unavailable (HTTPError)_ | [jbgunp](https://revoltgpt.gumroad.com/l/jbgunp) |
| 279 | Sentari AI Assistant - Copilot & MCP for Unreal Engine 5 | Sentari Digital | 99.00 | BUILD INSIDE UNREAL BY DESCRIBING WHAT YOU WANT Sentari AI Assistant installs into the Unreal Editor as a panel you talk to. Describe what you need in plain... | [wlwvbl](https://sentaridigital.gumroad.com/l/wlwvbl) |
| 280 | Star Collapse Space Scene for Unreal Engine 5.1 - 5.6 | Arghanion's Puzzlebox | 15.00 | _page unavailable (HTTPError)_ | [ormou](https://arghanion.gumroad.com/l/ormou) |
| 281 | Unreal 5 Tech Art Bundle | tharlevfx | 225.00 | _page unavailable (HTTPError)_ | [yilqk](https://tharlevfx.gumroad.com/l/yilqk) |
| 282 | Unreal Engine - Shrubland 4x4km Landscape Environment ( Arid | Freshcan 3D | 44.00 | _page unavailable (HTTPError)_ | [owybs](https://freshcan.gumroad.com/l/owybs) |
| 283 | Unreal Engine 5 - Ultimate Courses & Plugins Bundle | CGDealers | 49.99 | _page unavailable (HTTPError)_ | [fyiyw](https://cgdealers.gumroad.com/l/fyiyw) |
| 284 | Unreal Engine Cosmic Forge Bundle 30% OFF - Standard License | Arghanion's Puzzlebox | 32.32 | 1. Cloud Forge Complete Unreal Engine 5.3 - 5.4 - VDB Clouds Tutorials &amp; Cinematics: 💢 Update 1.4 VIDEO: TUTORIAL_03 💢 How to Use in your Scene VIDEO... | [eskpl](https://arghanion.gumroad.com/l/eskpl) |
| 285 | Unreal Engine Film School (Course) | Virtual Production Ins | 199.00 | _page unavailable (HTTPError)_ | [mszovu](https://vpinsider.gumroad.com/l/mszovu) |
| 286 | Unreal Engine Jumpstart (Tutorial) | Fabio Montorzi | 34.00 | _page unavailable (HTTPError)_ | [cqgrq](https://fabiomontorzi.gumroad.com/l/cqgrq) |
| 287 | Unreal Engine Space Bundle - Standard Licence - 40% Savings! | Arghanion's Puzzlebox | 22.79 | Elevate Your Unreal Engine Projects with Our Exclusive 3D Asset Bundle! Transform your Unreal Engine creations with this exclusive bundle featuring four... | [qvjbb](https://arghanion.gumroad.com/l/qvjbb) |
| 288 | Unreal Engine to 3ds Max Biped Tool | Mark Blosser | 15.00 | _page unavailable (HTTPError)_ | [iaxic](https://markblosser.gumroad.com/l/iaxic) |
| 289 | Unreal Exporter - Blender Addon | Kostia Perry | free | _page unavailable (HTTPError)_ | [perhw](https://tarmunds.gumroad.com/l/perhw) |
| 290 | Unreal Self Balance 1.2 Project - UE5.6 Self Balancing Ragdo | CodeFloat | 49.99 | _page unavailable (HTTPError)_ | [ytjyu](https://codefloat.gumroad.com/l/ytjyu) |
| 291 | Utu Plugin - Unity to Unreal Project Converter | Alex Quevillon | 30.00 | This plugin gives you the possibility to import a big chunk of the art work you did in Unity into Unreal. Compatible Unity Versions (Windows, Mac &amp; Linux) -... | [eamdpu](https://alexquevillon.gumroad.com/l/eamdpu) |
| 292 | xGen2UE Script - Export Alembic Hair from Maya xGen to Unrea | RealTime Hair | 15.00 | _page unavailable (HTTPError)_ | [clqdlu](https://realtimehair.gumroad.com/l/clqdlu) |

## Roblox tools (19)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 293 | [ NEW ] Roblox The Armory OP Script Hub / Crate ESP, Human E | Rixtreat | 0.99 | 🔥 THE ARMORY – ULTIMATE OP SCRIPT 🔥 ⚡ FEATURES 👁 Crate ESP – Instantly locate valuable loot across the map 🧍 Human ESP – Track every player with precision... | [dpdhro](https://rixtreat.gumroad.com/l/dpdhro) |
| 294 | [Roblox Studio]Advanced  (Suspicious)  NPC System | TheTomato | free | [Roblox Studio]Advanced (Suspicious) NPC System Contains: NPC Dummy. Instructions. NPC functions: Finds the closest player and follows (until the player... | [hfmpt](https://thetomato.gumroad.com/l/hfmpt) |
| 295 | [‼️ON SALE‼️] Advanced Roblox NPC System | _mosES() | 0.99 | [‼️ON SALE‼️] Advanced Roblox NPC System - Add interactive NPCs to your game for free! No Refunds as this is a Digital Download file. | [ggtge](https://mose5.gumroad.com/l/ggtge) |
| 296 | Advanced Car Spawner Script | Kaisen | free | Advanced Car Spawner Script for Roblox This script lets you easily spawn and control cars in your Roblox game. With customizable options for car models... | [exfxu](https://claritykaisen.gumroad.com/l/exfxu) |
| 297 | Advanced Zombie Horde System | Nox | 5.00 | Tired of zombies that stop at the first wall? Elevate your Roblox survival or horror game with our Advanced Horde AI. Inspired by World War Z, this system... | [pdemm](https://noxwen.gumroad.com/l/pdemm) |
| 298 | Car Customization System (Paint, Wheels & More) / Roblox Stu | Nytrix Prime | 6.99 | Create fully customizable cars in your Roblox game with this powerful and beginner-friendly system! This system lets players change the look of their... | [wlqsva](https://nytrixprime4.gumroad.com/l/wlqsva) |
| 299 | Foliage Presets Plugin – Studio License (UE 5.7 and 5.8, up  | levelarttools | 999.00 | STUDIO LICENSE This listing is a Studio License covering up to 15 named users within one company – intended for teams that cannot purchase individual seats... | [pmrma](https://levelarttools.gumroad.com/l/pmrma) |
| 300 | Hair Card Studio (Hair Card Creator Addon for Blender) | PixelicaCG | 11.99 | _page unavailable (HTTPError)_ | [bktxo](https://pixelicacg.gumroad.com/l/bktxo) |
| 301 | R6 ROBLOX REALISTIC MOVEMENT/CAMERA SYSTEM | JUNIS | 9.99 | A high-quality, professional First Person Movement System for ROBLOX R6, designed to deliver a smooth and immersive gameplay experience!! 🎮 Key Features... | [aorzrj](https://clownjunis.gumroad.com/l/aorzrj) |
| 302 | Roblox Advanced Player Data System (Attributes + DataStore) | AB price | 50.00 | A clean, scalable, and production-ready Player Data System for Roblox games. Built with DataStoreService, Attributes, Leaderstats, and RemoteFunctions, this... | [lprem](https://abprice.gumroad.com/l/lprem) |
| 303 | Roblox Boid System | Tekleed | 15.00 | Roblox BOID System Bring natural flocking behavior to your Roblox game. Schools of fish, flocks of birds, swarms of bats, or anything else that moves as a... | [vxmjq](https://tekleed.gumroad.com/l/vxmjq) |
| 304 | Roblox FPS System | Jeynkins | 12.00 | Includes: Fire, Sliding, Physics, Guns, Blocking, Melees, Explosives, Glass Breaking Level up your Roblox game with this easy-to-use system: Fire that... | [gfmdgs](https://jeynkinsrbxlstudios.gumroad.com/l/gfmdgs) |
| 305 | Roblox Jojo Bizarre Incremental Script / Auto Combat, Auto S | Rixtreat | 0.99 | 🩸 JoJo’s Bizarre Incremental – PRIVATE OP SCRIPT 🩸 ⚠️ LIMITED • UNDETECTED • NOT PUBLIC ⚠️ This is NOT one of those leaked, overused scripts floating around... | [nprkf](https://rixtreat.gumroad.com/l/nprkf) |
| 306 | Roblox Sorcerer Incremental Script Hub / OP Auto Farm, Auto  | Rixtreat | 0.99 | ⚠️ Early Access Script (Experimental) This is an early release version of my Roblox script. The project is currently in active development, meaning features... | [mtujfu](https://rixtreat.gumroad.com/l/mtujfu) |
| 307 | SmartMonster AI - Dynamic Enemy Pathfinding for Roblox | Harry | 15.00 | 🧠 SmartMonster AI – Plug-and-Play Monster System for Roblox A fully-featured Monster AI system designed for Roblox developers who want smarter, dynamic... | [zwotiv](https://scriptrblx.gumroad.com/l/zwotiv) |
| 308 | Studio Color - (Plugin) | MrQuaxkers | 6.99 | Full coloring toolkit for roblox studio. | [wbfovn](https://mrquaxkers.gumroad.com/l/wbfovn) |
| 309 | Sword Combat & NPC System [ROBLOX] | Pierce | 5.00 | Level up your game with this fully-featured Sword Combat System, perfect for action, RPG, or PvP experiences on Roblox! ⚔️ Core Features: Dynamic Sword... | [swhwn](https://piercedevelop.gumroad.com/l/swhwn) |
| 310 | Texture - (Plugin) | MrQuaxkers | 14.99 | 3000+ CC0 Textures for roblox studio. | [aebhqo](https://mrquaxkers.gumroad.com/l/aebhqo) |
| 311 | WEPPY Roblox Plugin Pro | Weppy | 9.99 | 🚀 WEPPY Roblox AI Toolkit Pro — AI-Powered Roblox Studio Workflow Ship production Roblox workflows faster with AI coding agents connected directly to Roblox... | [faccjs](https://weppy.gumroad.com/l/faccjs) |

## Gameplay systems (14)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 312 | 2D Avatar : Avatar System for VRChat | DX | 15.00 | _page unavailable (HTTPError)_ | [otqkek](https://dx30.gumroad.com/l/otqkek) |
| 313 | Avatar Flying System & Effects [VRChat] | Pointless Creations | 5.00 | ⭐️⭐️⭐️⭐️⭐️ Leave a rating on this product! Helps my product get recommended more! Want to test it out before you buy it? You can try out my Public Asset Test... | [ytgqe](https://pointlesscreations.gumroad.com/l/ytgqe) |
| 314 | CAMSUITE — All-in-One Camera Toolkit for Houdini | HYUNJOON KANG | 19.00 | _page unavailable (HTTPError)_ | [nzgkr](https://hyunjoonkang.gumroad.com/l/nzgkr) |
| 315 | Hair Card Pack + Pro Hair System | PixelicaCG | 8.99 | _page unavailable (HTTPError)_ | [wlwfe](https://pixelicacg.gumroad.com/l/wlwfe) |
| 316 | Jeano's Gun Framework | Jeano | 1.00 | A clean gun system built for speed and ease. This system makes it effortless to drop powerful weapons into any experience. Testing Place... | [xvpxc](https://scofieldstudios.gumroad.com/l/xvpxc) |
| 317 | NodeArchitect - AI Agent and MCP Server for Houdini. | Jbishop - NodeArchitec | 24.99 | NodeArchitect: AI Agent + MCP Server for Houdini A complete Houdini plugin that brings AI directly into your workflow. Built-in web UI, AI agent, 156 curated... | [thptkt](https://bishopvfx.gumroad.com/l/thptkt) |
| 318 | Real Sweat System for VRChat | Cooki | 6.49 | ━━━━━━━━━━━━━━━━━━━━ Official Documentation https://cookipiece.github.io/RealSweatSystem-Docs/ Installation Video https://youtu.be/KyYyZLNPSnc Real Wet... | [vosmpv](https://cookipiece.gumroad.com/l/vosmpv) |
| 319 | Real Wet System for VRChat | Cooki | 14.99 | _page unavailable (HTTPError)_ | [ucwktv](https://cookipiece.gumroad.com/l/ucwktv) |
| 320 | Reality Field Virtual Production System 2024 | LOLED | free | _page unavailable (HTTPError)_ | [zkxko](https://loledvirtual.gumroad.com/l/zkxko) |
| 321 | Replicated Hitbox System | Aurora Devs | 54.99 | _page unavailable (HTTPError)_ | [xdcif](https://auroradevs.gumroad.com/l/xdcif) |
| 322 | Style-Locked AI Motion Graphics from Any Script (Claude Skil | FRMWRKD | 10.00 | _page unavailable (HTTPError)_ | [vluidk](https://frmwrkd.gumroad.com/l/vluidk) |
| 323 | TekDetek Pro // Live AI Detection // ASCII // VJ Browser Too | TekDetek | 20.00 | TekDetek 0.7 Pro — Live AI Detection / ASCII / VJ Tool for Browser (License Key) TekDetek is a real-time video tool. Plug in a camera or drop a clip, wire up... | [xkljia](https://tekdetek.gumroad.com/l/xkljia) |
| 324 | Vibe Coder Kit — AI Development Framework for Production-Rea | Shahid Malik | 79.89 | _page unavailable (HTTPError)_ | [wvshw](https://nuovanceai.gumroad.com/l/wvshw) |
| 325 | VRCLens: VRChat Camera Extension for Desktop and VR | Hirabiki | 10.00 | VRCLens is a set of photographic extensions to the stock VRChat camera to be added on your avatar. It also supports desktop/2D mode, meaning you can take... | [rpnel](https://hirabiki.gumroad.com/l/rpnel) |

## Audio (17)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 326 | 3dSynth - Generative G-code Engine for Creative 3D Printing | Kubuz | 39.00 | _page unavailable (HTTPError)_ | [vkyvdy](https://kubuz.gumroad.com/l/vkyvdy) |
| 327 | ALL IN ONE SOUND LIBRARY BUNDLE | Free To Use Sounds | 25.00 | _page unavailable (HTTPError)_ | [waasf](https://ftus.gumroad.com/l/waasf) |
| 328 | DEGAUSS - VST Plugin | SynthSkool | 99.00 | _page unavailable (HTTPError)_ | [exmdlr](https://synthskool.gumroad.com/l/exmdlr) |
| 329 | FIELD KIT Playback Engine / Standalone + VST3 + AU | Field Tone Audio | 26.25 | _page unavailable (HTTPError)_ | [yurac](https://fieldtoneaudio.gumroad.com/l/yurac) |
| 330 | GuyEngine V2 - VST | Ultima DSP | 14.00 | _page unavailable (HTTPError)_ | [aaube](https://ultimadsp.gumroad.com/l/aaube) |
| 331 | Kick & Bass Auto Mix: VST3 & AU Plugin | Wagner Who | 37.00 | _page unavailable (HTTPError)_ | [reveh](https://wagnerwho.gumroad.com/l/reveh) |
| 332 | Liminal Space 2: Haunted Digital Reverb Synthesizer - CLAP,  | Wavetables.lol | 10.00 | _page unavailable (HTTPError)_ | [zobuuw](https://kcrosley.gumroad.com/l/zobuuw) |
| 333 | MODEL 200 REVERBERATOR PLUGIN (VST3 - AU - AAX - MAC - WINDO | PastToFutureReverbs | 99.00 | _page unavailable (HTTPError)_ | [ctwdx](https://pasttofuturereverbs.gumroad.com/l/ctwdx) |
| 334 | Old (Kinda broken) - Boom-Box (VRChat-SDK3) | Doloro | 3.50 | Annoy your friends!, Vibe to Music while staring into a mirror!, Do what ever you want with this VRChat boombox prefab https://discord.gg/eBMMr5csQM It comes... | [txufu](https://doloro.gumroad.com/l/txufu) |
| 335 | PTF 144 FOUR TRACK CASSETTE MIXER PLUGIN (VST3 - AU - AAX -  | PastToFutureReverbs | 69.00 | PTF-144 – Four-Track Cassette Mixer & Recorder Four Channels. Four Tracks. Pure Analog Cassette Magic. Bring the unmistakable sound and workflow of a... | [dwqdph](https://pasttofuturereverbs.gumroad.com/l/dwqdph) |
| 336 | PTF 16 DIGITAL REVERB PLUGIN (VST3 - AU - AAX - MAC - WINDOW | PastToFutureReverbs | 99.00 | PTF 16 – Legendary Digital Reverb THE SOUND OF THE '80s. THE MAGIC OF EARLY DIGITAL REVERB. Before plugins, before endless processing power, there was a... | [wkcax](https://pasttofuturereverbs.gumroad.com/l/wkcax) |
| 337 | PTF 350 TUBE TAPE RECORDER PLUGIN (VST3 - AU - AAX - MAC OS  | PastToFutureReverbs | 79.00 | The PTF-350 by Past To Future Plugins is a detailed plugin recreation (available as VST3 and Audio Unit for macOS, and VST3 for Windows) of a classic... | [gkdxxy](https://pasttofuturereverbs.gumroad.com/l/gkdxxy) |
| 338 | PTF 3630 COMPRESSOR PLUGIN (VST3 - AU - AAX - MAC OS - WINDO | PastToFutureReverbs | 49.00 | _page unavailable (HTTPError)_ | [ajaipb](https://pasttofuturereverbs.gumroad.com/l/ajaipb) |
| 339 | PTF DMX-15 STEREO DIGITAL DELAY & PITCH SHIFTER PLUGIN (VST3 | PastToFutureReverbs | 89.00 | _page unavailable (HTTPError)_ | [kvizb](https://pasttofuturereverbs.gumroad.com/l/kvizb) |
| 340 | PTF S950 SAMPLER PLUGIN (VST3 - AU - AAX - MAC - WINDOWS) | PastToFutureReverbs | 89.00 | _page unavailable (HTTPError)_ | [blrcpl](https://pasttofuturereverbs.gumroad.com/l/blrcpl) |
| 341 | Twenty Engine 1.1: an 8-voice polysynth inspired by the Korg | Peter Kohlmetz Møller | free | _page unavailable (HTTPError)_ | [ygmrks](https://7233849350308.gumroad.com/l/ygmrks) |
| 342 | U273 VINTAGE GERMAN COMPRESSOR LIMITER PLUGIN (VST3 - AU - A | PastToFutureReverbs | 79.00 | _page unavailable (HTTPError)_ | [ouitxw](https://pasttofuturereverbs.gumroad.com/l/ouitxw) |

## Pipeline, export & automation (5)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 343 | Blender Batch AO Baker Addon | VD Skinworks | 24.99 | ## 🇬🇧 English ### Batch AO Baker – Unwrap, bake & denoise ambient occlusion for all your objects in one click Stop baking AO object by object. Batch AO Baker... | [embsc](https://vdskinworks.gumroad.com/l/embsc) |
| 344 | Clip Exporter / Essential Premiere Pro Plugin | Piotr Toczynski | 25.00 | _page unavailable (HTTPError)_ | [otjkzv](https://cuttothepoint.gumroad.com/l/otjkzv) |
| 345 | MetaHuman Converter tool | Pavel Barnev | 300.00 | _page unavailable (HTTPError)_ | [tgxgnp](https://pavelbarnev.gumroad.com/l/tgxgnp) |
| 346 | Mystery Pixel Image Generator By Marina Art Design (WINDOWS  | Marina Art Design | 80.00 | ⭐ Mystery Pixel Image Generator Turn any black‑and‑white image into a clean, printable Mystery Pixel Image in minutes. This desktop tool lets you import or... | [qczcw](https://marinaartdesign.gumroad.com/l/qczcw) |
| 347 | Tree Library Botaniq Trees+Plants | polygoniq | 2.00 | About botaniq is a library of optimized &amp; realistic 3D vegetation. It features a variety of Trees, Palms, Succulents, Shrubs, Plants, and Pots for... | [MOZJY](https://polygoniq.gumroad.com/l/MOZJY) |

## UI & interface (7)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 348 | Item Tooltip | gfxcomet | 1.80 | A beautiful Tooltip UI to display your weapons and in-game items What&#39;s included: Tooltip design with gradient header Organized and clean list of stats... | [ihsii](https://gfxcomet.gumroad.com/l/ihsii) |
| 349 | Love2D Dev Tools Pro | abyo software | 12.00 | Love2D Dev Tools Pro Unlock the full power of Love2D Dev Tools — the VS Code extension purpose-built for Love2D (LÖVE) game development. The free version... | [aolecz](https://y1uda.gumroad.com/l/aolecz) |
| 350 | Lua Scripting Full Course | Rodel Catampongan | 10.00 | 🚀 Stop Searching for Scripts. Start Building Your Own. Tired of searching for working scripts only to find out they’ve been patched the very next day? You... | [kibiI](https://venuslock.gumroad.com/l/kibiI) |
| 351 | Pie Menu Editor Fork 2.4.0 | Pluglug | 29.99 | _page unavailable (HTTPError)_ | [ghqdwox](https://pluglug.gumroad.com/l/ghqdwox) |
| 352 | Quick Launcher | Live Workflow Tools | 14.00 | _page unavailable (HTTPError)_ | [grqraj](https://liveworkflowtools.gumroad.com/l/grqraj) |
| 353 | QuickMat Bake Pro – Ultimate Texture Baking Tool for Blender | Studio156 | 15.00 | _page unavailable (HTTPError)_ | [vdfltt](https://studio156.gumroad.com/l/vdfltt) |
| 354 | Stylized Tree Asset Generator | Rei | 12.50 | Easy-to-use and highly customizable Stylized Tree Asset Generator Making good-looking stylized trees in Blender can quickly embark you in a rabbit-hole of... | [kluofh](https://reipart.gumroad.com/l/kluofh) |

## Uncategorised (84)

| # | product | maker | price | the listing's own claim | source |
|---|---|---|---|---|---|
| 355 | 100+ CLAUDE REMOTION STYLES VAULT - Fully Automatic Editor | CHRONIXEL SHOP | free | _page unavailable (HTTPError)_ | [gexbt](https://chronixel.gumroad.com/l/gexbt) |
| 356 | 40% OFF🧨IN DESCRIPTION / Antigen VRChat Furry Avatar | gum.neochroma.xyz | 35.00 | Also available on Jinxxy: https://jinxxy.com/Neochroma/antigen 🙏Special thanks to those who leave a tip and/or pay full price for my products. I do notice... | [hhtkv](https://neochroma.gumroad.com/l/hhtkv) |
| 357 | 40% OFF🧨IN DESCRIPTION / Dergal VRChat Furry Model | gum.neochroma.xyz | 35.00 | 🙏Special thanks to those who tip and/or pay full price for my products🙏 I do notice and am very grateful for your generosity &lt;3 I&#39;m running a sale! 25% off 1... | [yxtvch](https://neochroma.gumroad.com/l/yxtvch) |
| 358 | [Addon]DECALmachine | machin3 | 54.99 | _page unavailable (HTTPError)_ | [fjXBHu](https://machin3.gumroad.com/l/fjXBHu) |
| 359 | [Addon]MACHIN3tools | machin3 | 2.00 | _page unavailable (HTTPError)_ | [IjsAf](https://machin3.gumroad.com/l/IjsAf) |
| 360 | [VRChat/SDK3] GD's VRChat Avatar Making Masterclass | YerGodDamnRight (GD, Y | 80.00 | _page unavailable (HTTPError)_ | [xmzhz](https://yergoddamnright.gumroad.com/l/xmzhz) |
| 361 | A3D TexSync - Substance Painter Plugin | A3D Labs | 15.00 | _page unavailable (HTTPError)_ | [fcxrss](https://a3dtools.gumroad.com/l/fcxrss) |
| 362 | Ability Toolbar | gfxcomet | 1.80 | A simple, aesthetic ability toolbar based off Valorant Need a practical and visually appealing ability toolbar for your game project? This is perfect for any... | [wjxwf](https://gfxcomet.gumroad.com/l/wjxwf) |
| 363 | Afterimages Installation Script (VRChat) | Zekk | free | _page unavailable (HTTPError)_ | [bghnkq](https://zekk.gumroad.com/l/bghnkq) |
| 364 | Anymo | Anymotool | 240.00 | _page unavailable (HTTPError)_ | [kptqn](https://anymotool.gumroad.com/l/kptqn) |
| 365 | Asad FX (After Effects, Premier Pro Plugin) | Asad Ali | 49.99 | _page unavailable (HTTPError)_ | [ozigow](https://editmaster12.gumroad.com/l/ozigow) |
| 366 | Atlas Cutter | Sebastien Rousseau | 25.00 | The Definitive Tool for Creating 3D Models from Texture Atlases. Never waste another minute cutting atlas textures by hand. Atlas Cutter is a pro-grade HDA... | [fpros](https://darktreetools.gumroad.com/l/fpros) |
| 367 | Avatar Accessory Tools | Shatter | 2.99 | _page unavailable (HTTPError)_ | [rwani](https://shatteredfur.gumroad.com/l/rwani) |
| 368 | BDFM tool - pixelated SVG | DesignFamilyMarket | free | _page unavailable (HTTPError)_ | [byown](https://designfamilymarket.gumroad.com/l/byown) |
| 369 | Behemox Hair Generator for Blender | Behemox Studio | 19.50 | _page unavailable (HTTPError)_ | [ucnep](https://behemox.gumroad.com/l/ucnep) |
| 370 | Blender vertex color I Octopus | maso_tools | 14.99 | 🐙 Octopus Vertex Color Professional Vertex Color Tools for Blender Paint, bake, randomize, debug, and manage vertex color workflows directly inside Blender... | [omprho](https://masotools.gumroad.com/l/omprho) |
| 371 | BLUUR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [pwobgm](https://antlii.gumroad.com/l/pwobgm) |
| 372 | CAD Sketcher [ Blender Addon ] | Keep Making | free | _page unavailable (HTTPError)_ | [rfoow](https://keepmaking.gumroad.com/l/rfoow) |
| 373 | CC4D Tools & CC4D Link | Benjamin Broschinski | 40.00 | CC4D Tools Version: 1.1.0 The CC4D Tools are collection of tools and scripts to simplify and enhance the process of working with Characters coming from... | [tovtvi](https://blkmsk.gumroad.com/l/tovtvi) |
| 374 | Cinematic Compositor Addon | ALANWAYNE | 8.98 | _page unavailable (HTTPError)_ | [memaa](https://alanwayne.gumroad.com/l/memaa) |
| 375 | Cloooner - Ae Cloner Tool That’s Actually Simple! | Phan Đức Trọng | 15.00 | _page unavailable (HTTPError)_ | [gojuoe](https://motionbytrong.gumroad.com/l/gojuoe) |
| 376 | DanTools | Daniel TechArt | 29.00 | HOUDINI HDAs. Houdini version 21+ New updated DanTools version: 1.1 Added high-resolution LiDAR in Europe, from 0.5 centimeters to 10 meters per pixels... | [noreow](https://danieltechart.gumroad.com/l/noreow) |
| 377 | Deep Paint -Blender GP Modeling & Painting tool Set | Gaku | 40.00 | Deep Paint v3.1.6 Your 2D style. Now in 3D. Last update Nov/03/2026 (Support for Blender 5.2) _____ Deep Paint is a user-friendly Blender add-on that enables... | [ffodac](https://gakutada.gumroad.com/l/ffodac) |
| 378 | Delta Quad (blender addon) | Kushiro | 10.00 | _page unavailable (HTTPError)_ | [hoivtl](https://kushiro.gumroad.com/l/hoivtl) |
| 379 | DITHR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [bdfpne](https://antlii.gumroad.com/l/bdfpne) |
| 380 | Draw Model Tool | Joey Carlino | 7.00 | _page unavailable (HTTPError)_ | [npepei](https://joeycarlino.gumroad.com/l/npepei) |
| 381 | Easy Chain — Blender Addon for FiveM Jewelry Conversion | DistrictXStudios | 10.00 | _page unavailable (HTTPError)_ | [xnvxa](https://districtxstudios.gumroad.com/l/xnvxa) |
| 382 | Easy Custom Normals - Stylized Shading Workflows in Blender | Fondant | 10.00 | _page unavailable (HTTPError)_ | [oatmwu](https://fondanttools.gumroad.com/l/oatmwu) |
| 383 | Easy Treez V2.0 for Maya | UnPLUG Tools | 110.00 | _page unavailable (HTTPError)_ | [lFVRg](https://unplugtools.gumroad.com/l/lFVRg) |
| 384 | Foliage Tint Master — One Click Tools | Alexandre Besson | 24.00 | _page unavailable (HTTPError)_ | [ylbgs](https://alexandrebesson.gumroad.com/l/ylbgs) |
| 385 | Galeria Tool License Key | Adhemas Batista | 50.00 | _page unavailable (HTTPError)_ | [gdddk](https://adhemas.gumroad.com/l/gdddk) |
| 386 | Garment Tool | bartoszstyperek | 40.00 | _page unavailable (HTTPError)_ | [MAnWP](https://bartoszstyperek.gumroad.com/l/MAnWP) |
| 387 | Garment Tool 2.1 for MetaHuman — UE 5.8 / Fit, Layer & Refit | Unreal Engine Cinemati | 10.00 | _page unavailable (HTTPError)_ | [sqbht](https://6062949617079.gumroad.com/l/sqbht) |
| 388 | Graphics Plugin Full v3.0.1 | Hanmen | 8.00 | CONTENT Contains the latest full version of the Graphics Plugin for Honey Select 2 + AI*Shoujo. This product is subscription-based. You will receive monthly... | [jdycp](https://hanmen.gumroad.com/l/jdycp) |
| 389 | Grid Method Tool - Rounded Pixel to Vector SVG | DesignFamilyMarket | 5.00 | _page unavailable (HTTPError)_ | [xruudv](https://designfamilymarket.gumroad.com/l/xruudv) |
| 390 | Grid Modeler (blender addon) | Kushiro | 20.00 | _page unavailable (HTTPError)_ | [VthLyO](https://kushiro.gumroad.com/l/VthLyO) |
| 391 | GRM Groom Toolkit (Houdini FX) | Gerardo Castellanos | 100.00 | _page unavailable (HTTPError)_ | [vbvrwb](https://gerardocastellanos.gumroad.com/l/vbvrwb) |
| 392 | GRM Groom Toolkit (Houdini INDIE) | Gerardo Castellanos | 30.00 | _page unavailable (HTTPError)_ | [swsmwj](https://gerardocastellanos.gumroad.com/l/swsmwj) |
| 393 | GroomBear - grooming toolkit for Houdini | kwac | 59.00 | _page unavailable (HTTPError)_ | [yndnV](https://kwac.gumroad.com/l/yndnV) |
| 394 | Hair Tool for Blender | bartoszstyperek | 52.00 | Hair Tool is Blender add-on that will help you: generate and model hair-card based hair, bake textures (with support for channel packing), do manual or... | [Dbhj](https://bartoszstyperek.gumroad.com/l/Dbhj) |
| 395 | Hairshop v2.98 - Hair card texture generator | KM Lee | 22.60 | _page unavailable (HTTPError)_ | [wyhba](https://kyoungmin.gumroad.com/l/wyhba) |
| 396 | Houdini 19.5 FX Encanto Cracking Concrete | Pol Villà | 10.00 | _page unavailable (HTTPError)_ | [daztv](https://polvfx.gumroad.com/l/daztv) |
| 397 | Houdini Solaris - USD & Environment Workflow (Subscription) | adrienlambert | 4.00 | Access to my Houdini USD tutorial series (previously on youtube) &amp; More tutorials series DOES NOT INCLUDE PROJECT FILES // VIDEO READ ONLY (No offline /... | [ztwuaj](https://adrienlambert.gumroad.com/l/ztwuaj) |
| 398 | HP Art Toolset: Surface Wrap for Maya and Blender | HP Art Toolset by Hai  | free | _page unavailable (HTTPError)_ | [bwkfxb](https://hparttoolset.gumroad.com/l/bwkfxb) |
| 399 | Kiosk Library - Asset Manager for 3D Artist | Fabian Strube | free | _page unavailable (HTTPError)_ | [xcsxpt](https://fabianstrube.gumroad.com/l/xcsxpt) |
| 400 | Leons Modeling Toolkit 2.0 | _3Leon | 10.00 | _page unavailable (HTTPError)_ | [vwija](https://3leon.gumroad.com/l/vwija) |
| 401 | Liminal Editor | Pawel | 12.50 | _page unavailable (HTTPError)_ | [spkbhy](https://venetian5gmailcom.gumroad.com/l/spkbhy) |
| 402 | LIVEWIRED MPC Plugin Bundle – 13 Free Plugins for MPC | Livewired Sound Series | free | _page unavailable (HTTPError)_ | [urmntl](https://livewired808.gumroad.com/l/urmntl) |
| 403 | Magic Decal | Nebula Animations | 15.00 | _page unavailable (HTTPError)_ | [bmouh](https://nebulaanimations.gumroad.com/l/bmouh) |
| 404 | Malbers Biped Ragdoll | Malbers Animations | 24.99 | _page unavailable (HTTPError)_ | [awukjv](https://malberanimations.gumroad.com/l/awukjv) |
| 405 | Mallet: Blender addon | Twist | 15.00 | _page unavailable (HTTPError)_ | [qxigq](https://dertwist.gumroad.com/l/qxigq) |
| 406 | MEGA ADDON For Blender | CGStore | 15.00 | _page unavailable (HTTPError)_ | [ehqjh](https://cgcool.gumroad.com/l/ehqjh) |
| 407 | Merge Master - Blender addon | miccoli3d | 60.00 | _page unavailable (HTTPError)_ | [zkckw](https://miccoli3d.gumroad.com/l/zkckw) |
| 408 | MotionKit AE – All-in-One Ae ToolKit | Off.motionsfly | 10.00 | MotionKit AE MotionKit AE is an all-in-one, modular control panel for After Effects, designed to automate repetitive tasks, speed up your workflow, and bring... | [bedrnd](https://officialmotionsfly.gumroad.com/l/bedrnd) |
| 409 | Noesis Intelligent Harmony Generator & Assistant | Dystopian Waves | 10.79 | _page unavailable (HTTPError)_ | [nvfzqi](https://dystopianwaves.gumroad.com/l/nvfzqi) |
| 410 | NTD Engine - Full Version | OwnLife Audio | 39.00 | _page unavailable (HTTPError)_ | [zlbwog](https://ownlifeaudio.gumroad.com/l/zlbwog) |
| 411 | Outliyr Framework | outliyr | 199.99 | _page unavailable (HTTPError)_ | [etpeiq](https://outlier2.gumroad.com/l/etpeiq) |
| 412 | Oven Bake / Blender Baking Addon | Boreo | 16.00 | _page unavailable (HTTPError)_ | [undhn](https://boreo.gumroad.com/l/undhn) |
| 413 | Painterly V.3 Blender (5.1+)  Add-on | Doughy Animation Studi | 19.50 | _page unavailable (HTTPError)_ | [wvwta](https://doughyanimation.gumroad.com/l/wvwta) |
| 414 | Palette Grid - Smart Palette Texture Workflow Blender Addon | Saved Pixel | 25.00 | _page unavailable (HTTPError)_ | [uqjpux](https://savedpixel.gumroad.com/l/uqjpux) |
| 415 | Partice Editor PRO for Honey Select 2 | Hanmen | 9.00 | _page unavailable (HTTPError)_ | [iopwv](https://hanmen.gumroad.com/l/iopwv) |
| 416 | Plugin Bundle Vol. 1 | Rex Roberts | 60.00 | _page unavailable (HTTPError)_ | [hxnqce](https://rexaffects.gumroad.com/l/hxnqce) |
| 417 | Poly Modeling Toolbox - Everything You Need And More | Noggi | 39.00 | _page unavailable (HTTPError)_ | [mipncz](https://noggi3d.gumroad.com/l/mipncz) |
| 418 | Polytool 2 | Markcreator | free | _page unavailable (HTTPError)_ | [hsseod](https://markcreator.gumroad.com/l/hsseod) |
| 419 | RESOLUME Plugin FX^ASCII.GLYPH_TMBK | VJ Tembak | 18.00 | FX^ASCII.GLYPH_TMBK The Ultimate Real-Time Geometric &amp; ASCII Generative FX Plugin for Resolume Arena / Avenue Transform raw video inputs into dynamic... | [kkfmbii](https://vjtembak.gumroad.com/l/kkfmbii) |
| 420 | Retro Diffusion Extension for Aseprite | Cody Claus | 20.00 | This product is in the process of being phased out for Retro Diffusion&#39;s own native pixel art editor! The editor is in early stages, but will hopefully be... | [yqecpq](https://astropulse.gumroad.com/l/yqecpq) |
| 421 | RH Character Tools for Cinema 4D & Mixamo | rhymage | 48.00 | _page unavailable (HTTPError)_ | [bbLu](https://rhymage.gumroad.com/l/bbLu) |
| 422 | SAMPL Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [vfetba](https://antlii.gumroad.com/l/vfetba) |
| 423 | ShapeKeyGen V3.50 Blender Addon | Wee learn from Mobile | 15.00 | _page unavailable (HTTPError)_ | [yrfsq](https://pymarket.gumroad.com/l/yrfsq) |
| 424 | SHAPES - Shape Key Editor for Blender | brave rabbit | 20.00 | _page unavailable (HTTPError)_ | [dfuju](https://braverabbit.gumroad.com/l/dfuju) |
| 425 | SHAPES 5.13 - Blend Shape Editor for Maya 2023-2027 | brave rabbit | 20.00 | _page unavailable (HTTPError)_ | [sovts](https://braverabbit.gumroad.com/l/sovts) |
| 426 | Simple Tree Tools 3.0 for Houdini | nirfse3D | free | _page unavailable (HTTPError)_ | [hsgdax](https://nwestfelt.gumroad.com/l/hsgdax) |
| 427 | Smart Layer v0.91.1 (Python Script for Maya) | Slava Baravik | 52.00 | _page unavailable (HTTPError)_ | [apvbbq](https://borovikmotion.gumroad.com/l/apvbbq) |
| 428 | Stereo Bundle: Rotation + Deviation - Quadrature stereo proc | RawtonForge | 32.00 | Two devices, one idea: stereo that comes from the signal itself. Most stereo tools fake width. They delay one channel, invert a phase, or spread a reverb... | [osgyf](https://rawton.gumroad.com/l/osgyf) |
| 429 | Stylized Cloud Generator | Rei | 9.50 | _page unavailable (HTTPError)_ | [qcgrt](https://reipart.gumroad.com/l/qcgrt) |
| 430 | Substance Node Pack / Dete Trim Toolkit | Dete Art Resources | 2.50 | About the Trim Tool Trim textures, or trim sheets, are commonly used in the video game industry. Until now, there hasn&#39;t been a unified workflow for creating... | [hjmavo](https://dete.gumroad.com/l/hjmavo) |
| 431 | SuperLCD - Davinci Resolve Plugin | Akascape | 5.60 | _page unavailable (HTTPError)_ | [qiahk](https://akascape.gumroad.com/l/qiahk) |
| 432 | TEXTR Tool License Key | Antlii | 9.00 | _page unavailable (HTTPError)_ | [lsucj](https://antlii.gumroad.com/l/lsucj) |
| 433 | TrackToolsV2.1 - BETA | MeshHouse | free | _page unavailable (HTTPError)_ | [acmxzm](https://meshhouse.gumroad.com/l/acmxzm) |
| 434 | Tradigitalist Toolbag - All Access | Alan Wyatt | 12.00 | _page unavailable (HTTPError)_ | [enxsr](https://tradigital.gumroad.com/l/enxsr) |
| 435 | TunaMetaPack - MetaHuman Convert / Custom Tools | Tuna | 150.00 | _page unavailable (HTTPError)_ | [wsbap](https://tunarig.gumroad.com/l/wsbap) |
| 436 | Viral Styles Launchpad | The AI Tool Finds | 19.00 | _page unavailable (HTTPError)_ | [wbsqwp](https://theaitoolfinds.gumroad.com/l/wbsqwp) |
| 437 | Vooolume - Relief Brush Tool | Krftoools | 15.00 | _page unavailable (HTTPError)_ | [yrgeg](https://krftoools.gumroad.com/l/yrgeg) |
| 438 | WireTools / Node Connection Tools for Cinema 4D & Redshift | Maksym Vysokolov | 19.50 | _page unavailable (HTTPError)_ | [ozgreb](https://thodos998.gumroad.com/l/ozgreb) |

## Reached by hopping (1054 products)

Straight search only finds what you already thought to ask for. These came from searching the *operation* instead of the domain, and from reading a maker's whole catalogue. Each group is one hop; the URL is the product the hop landed on.

| hop | products | examples |
|---|---|---|
| seller:atouchofthegods | 39 | [avoidlycocoon](https://atouchofthegods.gumroad.com/l/avoidlycocoon), [infinityaura](https://atouchofthegods.gumroad.com/l/infinityaura), [befreeofjudgement](https://atouchofthegods.gumroad.com/l/befreeofjudgement) |
| occlusion culling | 34 | [Blender 3.3-5.3 Higgsas Geometry Nodes](https://higgsas.gumroad.com/l/wrusot), [Suite Nile — Egyptian Luxury Penthouse](https://davysh.gumroad.com/l/kaasv), [CLUB NEON Deluxe](https://mina1.gumroad.com/l/crtcx) |
| explainer video | 34 | [The 3D Reel Playbook](https://sothatshow.gumroad.com/l/bogmif), [Fábrica de Porqués](https://rubenito08.gumroad.com/l/ijdpp), [Custom Explainer Video (Script + Desig](https://designlabstudio.gumroad.com/l/fxxng) |
| lut color grading | 34 | [Mindthecolor v3](https://carlodiamanti.gumroad.com/l/icedku), [MindTheColor PowerSet](https://carlodiamanti.gumroad.com/l/cbqnm), [The Everyday LUT](https://toldbynick.gumroad.com/l/cvhce) |
| matte painting | 33 | [Original Blade Runner Textures](https://ankaris.gumroad.com/l/EpePN), [ZTexturator](https://ceco.gumroad.com/l/gxgnd), [✦ My Photoshop Brushpack +500 brushes ](https://xbrianfloresx.gumroad.com/l/jhwdi) |
| squash stretch rig | 32 | [Rigging in Maya / Quick Start Part Two](https://riggingpro.gumroad.com/l/isiri), [Yamal - Cartoony rig for Maya](https://loganrigs.gumroad.com/l/zqorl), [SHAPE Course - Face Rig Module](https://armenpamokdjian.gumroad.com/l/stnfm) |
| ink lines | 31 | [The Forgotten Frontier Journal](https://silasmercer.gumroad.com/l/rcdkm), [Practice Book "Sketching Winter with P](https://daribodrawing.gumroad.com/l/wmykhc), [ATOMOON  brush](https://atomoon.gumroad.com/l/vrdzg) |
| seller:3dtudor | 30 | [blender](https://3dtudor.gumroad.com/l/blender), [blender4ultimateguide](https://3dtudor.gumroad.com/l/blender4ultimateguide), [blender4](https://3dtudor.gumroad.com/l/blender4) |
| toon outline shader | 29 | ["Peppermint" Customisable Head for VTu](https://nelaire.gumroad.com/l/tndczy), [Toon Shaders v1.6](https://hanmen.gumroad.com/l/ilywp), [Kris Dreemurr Model (Blender Rig + VRC](https://denmarkus.gumroad.com/l/apkzwi) |
| subsurface scattering shader | 28 | [Novabeast Muscle Textures - Normal map](https://mmmos.gumroad.com/l/lcvpk), [Nardoragon Muscle Textures - Normal ma](https://mmmos.gumroad.com/l/owmff), [PBR Color Reference List & Color Calib](https://gbaran.gumroad.com/l/rjthlk) |
| hair groom | 27 | [Ageless Style](https://davidrennerfashion.gumroad.com/l/fdjqzc), [WEDDING OUTFIT PACK / FOXIPAWS CELESTE](https://meowmelon.gumroad.com/l/bfveha), [StrandKit / The Hair, Fur & Dynamics L](https://ninodefoq.gumroad.com/l/ifpqd) |
| matcap shader | 27 | [FemRex (Female Rexouium) (PC/Quest)](https://justper.gumroad.com/l/hhuodv), [Ace of Spades from Destiny 2 [VRChat]](https://pointlesscreations.gumroad.com/l/qtqhe), [NovaMaid - Novabeast Maid dress [ VRCH](https://fukaoni.gumroad.com/l/tbili) |
| cel shader | 27 | [Star Wars: Clone Wars 2003 Clone Troop](https://zerochurros.gumroad.com/l/hpxus), [Noggi's 3D Anime Starter Kit](https://noggi3d.gumroad.com/l/ofqblj), [[Blender] Breath of the Wild and Tears](https://thejudsub.gumroad.com/l/fojcg) |
| foliage shader | 26 | [Painterly Tree & Flora Creator: ShapeS](https://tradigital.gumroad.com/l/mefur), [Light Wrangler: Best Blender Lighting ](https://leonidaltman.gumroad.com/l/ffstxw), [- White Ascent - (Quest & PC) (NIGHT)](https://imbeemo.gumroad.com/l/befze) |
| soft body simulation | 26 | [Bliss](https://atouchofthegods.gumroad.com/l/xcftnj), [Aqua Therapy](https://atouchofthegods.gumroad.com/l/ilbyf), [Fascia Regeneration and Rejuvenation](https://atouchofthegods.gumroad.com/l/yjjesc) |
| texture atlas | 25 | [Atlas VRFX - Studio Light [VRChat]](https://atlasvrfx.gumroad.com/l/zsqux), [Novabeast / Nova Tech Wear- MMXXV](https://dasteel.gumroad.com/l/qbwbex), [Horse Anatomy Kit Commercial License. ](https://farzinizadyar.gumroad.com/l/jqann) |
| translucent shader | 25 | [Pencil and Markers Brush Pack // PROCR](https://ayeoops.gumroad.com/l/bdwys), [Introduction to Interior Visualization](https://mographplus.gumroad.com/l/ogzap), [Pencil and Markers Brush Pack BUNDLE P](https://ayeoops.gumroad.com/l/edlbgm) |
| vfx particles | 23 | [HydroFX 1.5.5](https://stormvfx.gumroad.com/l/bxcdab), [Wraith](https://meechu.gumroad.com/l/qgfsh), [Ultimate VFX Pack — The Complete Video](https://enchantedmediauk.gumroad.com/l/nvbjwi) |
| fur shader | 23 | [SkylarFox II Twink Fox Base II VRChat ](https://skylarfoxvr.gumroad.com/l/xakevn), [Procreate MEGAPACK XXL: 2000+ Premium ](https://georgvw.gumroad.com/l/ghzuF), [Mantled Beast V2.1.2](https://luxaeterna.gumroad.com/l/fiowh) |
| cloth simulation | 20 | [Tenpix Cloth](https://alirezaakhbari.gumroad.com/l/lmiiu), [Garment Studio (Beta) - Draft, Sew and](https://georgezaky108.gumroad.com/l/jpadzx), [A3D Procedural Generation Toolkit for ](https://ashlee3dee.gumroad.com/l/izqnta) |
| lod generator | 20 | [TACTYC Gaussian Splat v2.0 — Gaussian ](https://tactyc.gumroad.com/l/dgmnyj), [G-Ready - Game Ready Modeling Tools](https://faridmammadov.gumroad.com/l/uzwvxd), [Roadscape 4.13 (Blender Procedural Roa](https://bampt.gumroad.com/l/udncg) |
| decal projection | 20 | [The Ultimate Introduction to Octane Fo](https://mographplus.gumroad.com/l/pbxmho), [PBR Painter 3 for Blender](https://bytebrushstudio.gumroad.com/l/WQfMY), [Decalify - Turn Any Mesh Into a Decal ](https://hodgson3d.gumroad.com/l/cbfnrv) |
| motion matching | 20 | [SickMotionz ToolBox Pro For Premiere P](https://motionzzy.gumroad.com/l/iabesh), [Make Movement Feel Real - 3 Hours of A](https://quantumstage.gumroad.com/l/uqomm), [Music Visualizer by VisualizerWave - a](https://unformaudio.gumroad.com/l/wslqc) |
| 2d rig | 20 | [** BLACK FRIDAY DISCOUNT!** The One We](https://joelmayer.gumroad.com/l/zrlpbt), [LIZ&ROB](https://animworkshop.gumroad.com/l/apxrdw), [Soap Dragons (VRChat Dragon Avatar Bas](https://ironicsoap.gumroad.com/l/syvap) |
| depth pass | 20 | [The SHTF Home Defense Manual](https://rhettcallahan.gumroad.com/l/fedece), [PaintBridge Krita](https://madcanvas.gumroad.com/l/syhbrs), [The Dark Knight](https://atouchofthegods.gumroad.com/l/zspzjz) |
| gpu instancing | 19 | [BeamLight Control System(VRChat)](https://noriben3.gumroad.com/l/qpidx), [Blob Fusion](https://bartoszstyperek.gumroad.com/l/nqcbb), [LaserLight Shader (VRChat)](https://noriben3.gumroad.com/l/xtkksq) |
| retarget animation | 19 | [CascadeBridge – Blender to Cascadeur f](https://ibr4him2.gumroad.com/l/rafwrh), [Full motion capture cleanup course for](https://pavelbarnev.gumroad.com/l/jXWDVB), [RealMotion Pro Blender Addon For Anima](https://pymarket.gumroad.com/l/tvxre) |
| vertex color painter | 19 | [40% OFF🧨IN DESCRIPTION / Moriarty Hybr](https://neochroma.gumroad.com/l/fbhbyf), [B_PAINTBRUSH  - PAINTING LAYERS:  BLEN](https://nano3dart.gumroad.com/l/okatr), [[P.0.E] - Orion Jumpsuit](https://darksideralex.gumroad.com/l/tesvb) |
| motion graphics | 19 | [SYNAPS8 – Blob Tacking plugin (After E](https://idsley.gumroad.com/l/zhbsbh), [C4D Gaussian Splat Studio](https://alphapixel3d.gumroad.com/l/ywjene), [All Four Prompt Kits](https://attunedjosh.gumroad.com/l/ekxbl) |
| water simulation | 18 | [Complete ESG Career Builder Pack](https://esgcareerbuilder.gumroad.com/l/qfwwub), [Divinius Supremium Injection - (Potent](https://submorphic.gumroad.com/l/haskbb), [Water Shots Bundle](https://dancortes.gumroad.com/l/vfdgt) |
| spine animation | 18 | [All-in-one - 2D Fx Tutorial Bundle](https://ducvu.gumroad.com/l/rmypsx), [Universal AFK Beast Animations Pack [V](https://himasters.gumroad.com/l/orqmqh), [Cycler](https://dkolpakov.gumroad.com/l/fhehk) |
| retopology tool | 17 | [MSD PointCloudSnap Pro Indie 3 seats](https://ytsejam.gumroad.com/l/vuvcic), [Character & Creature Art Mentorship & ](https://korln.gumroad.com/l/qeaer), [Drones & Photogrammetry](https://maxdepth.gumroad.com/l/tSiOQ) |
| compositing | 16 | [Camera Realism Course — why technicall](https://aitorecheveste.gumroad.com/l/jowcy), [StoryboardSim](https://sekiun.gumroad.com/l/dubvdy), [Environment creation in Houdini Part1 ](https://mizukiyamada8.gumroad.com/l/bamwqe) |
| particle system | 15 | [Layla / Female / PC + Quest / VRCFT & ](https://heartmarksman.gumroad.com/l/apdyl), [Rizzo / Female/Femboy / PC + Quest / V](https://heartmarksman.gumroad.com/l/vdweqy), [Gwen / Female / PC + Quest / VRCFT & V](https://heartmarksman.gumroad.com/l/himsno) |
| procedural scatter | 15 | [MatterAE](https://ablebaker.gumroad.com/l/scqmn), [OTOMO - Pipe Generator Plugin for Cine](https://corneliusdammrich.gumroad.com/l/clnvwi), [Anime Garden // Painterly Asset Librar](https://omarfaruqtawsif.gumroad.com/l/lbajds) |
| god rays volumetric light | 15 | [BlendFog - Depth Fade Fog Shader](https://jesperbylov.gumroad.com/l/ayhrrl), [Goo Asset Pack - Spring 2025](https://dillongoo.gumroad.com/l/gwsfft), [Blender 4 UE5 & Aseprite: Game Designe](https://3dtudor.gumroad.com/l/fighom) |
| ragdoll physics | 14 | [Dave (VRC Avatar)](https://ramiwatanuki.gumroad.com/l/zykcs), [David (VRC Avatar)](https://ramiwatanuki.gumroad.com/l/ucmxe), [VRChat Ragdoll System](https://littlewhinging.gumroad.com/l/ybibai) |
| normal map baker | 14 | [SoMuchMaterials](https://somuchmonsters.gumroad.com/l/Xyttv), [MeshSplatter - Substance Designer](https://1086785678474.gumroad.com/l/txfbki), [N-Gone Pro 2.0](https://takerefuge3d.gumroad.com/l/xwdkp) |
| stylized render | 14 | [DemiRaito Brushes: Momentum Collection](https://demiraito.gumroad.com/l/xsewmf), [Complete Concept Art Course](https://trentk.gumroad.com/l/xkgntc), [Rairei Avatar [VRChat]](https://rocrocot.gumroad.com/l/iibypq) |
| rim light shader | 13 | [🧊 Fast Voxel Shader for VRChat 🆕](https://valuef.gumroad.com/l/edklge), [Eye Glint Poiyomi Shader](https://foxipso.gumroad.com/l/wuzwx), [arcane style shader addon  v1.0 and v2](https://agrimart.gumroad.com/l/nodfz) |
| seller:daoudyai | 11 | [xuymr](https://daoudyai.gumroad.com/l/xuymr), [itajdw](https://daoudyai.gumroad.com/l/itajdw), [xbbghk](https://daoudyai.gumroad.com/l/xbbghk) |
| seller:noriben3 | 10 | [transparentscreen](https://noriben3.gumroad.com/l/transparentscreen), [blackkite](https://noriben3.gumroad.com/l/blackkite), [mirrorballlight](https://noriben3.gumroad.com/l/mirrorballlight) |
| toon shading | 9 | [Cover girl outfit (Multi-Model)  (Nova](https://vanadstudio.gumroad.com/l/vyapnt), [normalMagic for Blender](https://spaghetmenot.gumroad.com/l/oemsm), [YMA Toon Studio for Redshift [C4D or H](https://youmeacademy.gumroad.com/l/jbamei) |
| seller:fotoref | 9 | [hnfekax](https://fotoref.gumroad.com/l/hnfekax), [sfske](https://fotoref.gumroad.com/l/sfske), [murgc](https://fotoref.gumroad.com/l/murgc) |
| cubemap reflection | 8 | [[VRC] Glass/Refraction Shader](https://jayievr.gumroad.com/l/eznby), [PANDA GIRL 3.0 / VF+[OPTIMIZED]+[FT]+[](https://vframeassets.gumroad.com/l/lzwgh), [Dynamic Fake Liquid in a Bottle - UE M](https://morepawa.gumroad.com/l/xsfua) |
| seller:promptblueprint | 8 | [bdnkdb](https://promptblueprint.gumroad.com/l/bdnkdb), [fdwchc](https://promptblueprint.gumroad.com/l/fdwchc), [ozshe](https://promptblueprint.gumroad.com/l/ozshe) |
| seller:2dcharacter | 8 | [osgby](https://2dcharacter.gumroad.com/l/osgby), [haoui](https://2dcharacter.gumroad.com/l/haoui), [hczltq](https://2dcharacter.gumroad.com/l/hczltq) |
| uv packing tool | 7 | [HairCard Forge — Advanced Hair Card Te](https://1136505014009.gumroad.com/l/hebrpd), [Rizom Bridge for Maya](https://optagon.gumroad.com/l/gqKcz), [Assetify / The Ultimate Bake & Export ](https://ninodefoq.gumroad.com/l/zjcemn) |
| seller:ragdollphysics | 7 | [firstfive](https://ragdollphysics.gumroad.com/l/firstfive), [ice](https://ragdollphysics.gumroad.com/l/ice), [bucket](https://ragdollphysics.gumroad.com/l/bucket) |
| seller:fasttracktutorials | 7 | [chkqqw](https://fasttracktutorials.gumroad.com/l/chkqqw), [myxny](https://fasttracktutorials.gumroad.com/l/myxny), [exzsi](https://fasttracktutorials.gumroad.com/l/exzsi) |
| seller:trevital | 7 | [f](https://trevital.gumroad.com/l/f), [v](https://trevital.gumroad.com/l/v), [i](https://trevital.gumroad.com/l/i) |
| seller:aitorecheveste | 7 | [tpc01](https://aitorecheveste.gumroad.com/l/tpc01), [pct01](https://aitorecheveste.gumroad.com/l/pct01), [sgmbk](https://aitorecheveste.gumroad.com/l/sgmbk) |
| seller:heartmarksman | 6 | [lhijmg](https://heartmarksman.gumroad.com/l/lhijmg), [rdutl](https://heartmarksman.gumroad.com/l/rdutl), [mdlxr](https://heartmarksman.gumroad.com/l/mdlxr) |
| seller:monochromecbn | 6 | [keiuh](https://monochromecbn.gumroad.com/l/keiuh), [vimxvc](https://monochromecbn.gumroad.com/l/vimxvc), [soktun](https://monochromecbn.gumroad.com/l/soktun) |
| seller:vfxgrace | 5 | [gsobka](https://vfxgrace.gumroad.com/l/gsobka), [wnrly](https://vfxgrace.gumroad.com/l/wnrly), [vftct](https://vfxgrace.gumroad.com/l/vftct) |
| seller:maroc777772 | 4 | [zfzpfi](https://maroc777772.gumroad.com/l/zfzpfi), [xpzhk](https://maroc777772.gumroad.com/l/xpzhk), [rrzsdn](https://maroc777772.gumroad.com/l/rrzsdn) |
| seller:mographplus | 4 | [awmbwxc](https://mographplus.gumroad.com/l/awmbwxc), [hbcvw](https://mographplus.gumroad.com/l/hbcvw), [kbfems](https://mographplus.gumroad.com/l/kbfems) |
| seller:cawrigs | 4 | [standard](https://cawrigs.gumroad.com/l/standard), [nxoaz](https://cawrigs.gumroad.com/l/nxoaz), [ldkomm](https://cawrigs.gumroad.com/l/ldkomm) |
| navmesh pathfinding | 3 | [VRChat Pet Follower System](https://unrealakira.gumroad.com/l/esorl), [Agents](https://globglob.gumroad.com/l/pjcnm), [Shooter Example Project – Lyra Demo fo](https://neostarstudios.gumroad.com/l/xntfbz) |
| seller:carlodiamanti | 3 | [yrrpr](https://carlodiamanti.gumroad.com/l/yrrpr), [mtc](https://carlodiamanti.gumroad.com/l/mtc), [zivfg](https://carlodiamanti.gumroad.com/l/zivfg) |
| seller:mina1 | 2 | [clubneon](https://mina1.gumroad.com/l/clubneon), [cpztr](https://mina1.gumroad.com/l/cpztr) |
| seller:dustywhite | 1 | [tarot](https://dustywhite.gumroad.com/l/tarot) |

---

Regenerate: `python3 tools/gumroad_census.py --market all` then `python3 tools/compile_census.py`. Query list and scrape date are in `specs/gumroad_tools.json`.
