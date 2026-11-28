# The SLERM battlefield

> “to slerm is to raise the floor standards, do not feel bad you are on here, understand that time marches forward, do not become a boomer”

Every listing below was scraped from Gumroad's public search, 16 queries, 168 products, 68 kept as Roblox-related.

The point is not to buy anything. The point is that a paid tool's *description* is a specification: it names the operation, the input and the promise. That is enough to reimplement the operation in C11 and measure whether it holds.

Nothing here is copied, decompiled or redistributed. Names, prices and links are cited so a reader can check the claim at its source.


## What is already on the floor

| capability | file | measured |
|---|---|---|
| per-pixel lighting (lambert + point lights + rim + ground AO) | `src/shade.c` | gradient p90 0.11 -> 0.51 with 2x SSAA |
| adaptive auto-skinning (distance + Laplacian smoothing + top-k) | `src/rig.c` | crease 0.00442 -> 0.00240 over 32 passes |
| two-bone IK with pole, FABRIK for longer chains | `src/rig.c` | end->target 0.000000, lengths constant |
| auto-rig (band analysis, side split) | `src/rig.c` | mean joint error 0.031 body units |
| grip / attach / surface placement | `src/grab.c` | placement 0.00000, rigidity 0.000000 |
| blocky R15 rig with measured band table | `r15.py` | 7/7 invariants pass |
| planted IK walk (duty, slip) | `animate_r15.py` | slip 0.41 -> 0.075, penetration 28 -> 3.7 mm |
| Roblox asset import (.mesh v1 soup, v4 binary, rbxm) | `rbxmesh.py`, `rbxm.py` | 506-tri UGC item parsed |

## Rigging & skinning (24)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 1 | Cubic Face (Roblox Face Rig) | ComixProd. | free | Cubic Face is a simple face rig I created. It was made in a video. No credit needed, however do not redistribute or claim ownership. If you want to share... | [crzat](https://comixproductions.gumroad.com/l/crzat) |
| 2 | Glock R6 Roblox Rig for Moon Animator | Nisky | free | Roblox R6 Rig with a Welded and fully animatable Glock 17 designed to be used with Moon Animator. | [yaavw](https://nisky.gumroad.com/l/yaavw) |
| 3 | Nisky's Ultimate R6IK Pose Pack for Blender | Nisky | 5.00 | Speed up your blender animation workflow with 60 different poses. Including all the necessary poses for walk cycles, run cycles, M1 cycles and much more... | [vhibt](https://nisky.gumroad.com/l/vhibt) |
| 4 | Profine's Roblox Toy Rig EDIT (Blender 4.0+) | Paribes | free | Profine made a Roblox toy rig a while back, I made a simple edit which has bone shapes and allat (this was mainly for me to have a better animating experience). | [udkwsf](https://paribes.gumroad.com/l/udkwsf) |
| 5 | R15 Roblox ANIMATION Rig (Blender -> Roblox Studio) | Paribes | free | A rig for Blender 3D to export to Roblox Studio! Settings HeadTarget HeadTarget Parent Torso IK Arm/Leg Settings IK/FK Switch Bone Layers (IK/FK) Fancy... | [zmyfl](https://paribes.gumroad.com/l/zmyfl) |
| 6 | R15 Roblox Starter Rigs (TEMPORARY) | Paribes | free | while waiting for the next starter rigs update, use these rigs if you need r15 here's the description of starter rigs: Introducing Roblox Starter Rigs, which... | [jjhtt](https://paribes.gumroad.com/l/jjhtt) |
| 7 | Roblox Blocky Finger Rig (Blender 4.0+) | Paribes | free | fingies NOTE: FACE RIG IS NOT INCLUDED, THAT IS AEPBR EXCLUSIVE | [fpbjgc](https://paribes.gumroad.com/l/fpbjgc) |
| 8 | Roblox Blocky Rig \| C4D R20+ | Chastling | 1.50 | Available on Gumroad | [ahkbz](https://chastling.gumroad.com/l/ahkbz) |
| 9 | Roblox Fat Rig (4.0+) | Paribes | free | _no description in page metadata_ | [jiojiw](https://paribes.gumroad.com/l/jiojiw) |
| 10 | Roblox Football Rig V1 (Blender 4.2+) | Paribes | 10.00 | NOTE: redistributing or reselling the rigs, even if modified or at a price, is PROHIBITED. Muscle System The rig contains a special muscle system that is... | [ifhke](https://paribes.gumroad.com/l/ifhke) |
| 11 | Roblox Multipurpose Cloth Rig (4.5+) | Paribes | free | Features: Classic Cloth Modification - This modification is a top-tier cloth simulation rig that bakes the shirt, providing realistic cloth physics... | [hwthor](https://paribes.gumroad.com/l/hwthor) |
| 12 | Roblox Rig Vault (Blender 4.0+) | Paribes | free | Introducing Roblox Rig Vault! Roblox Rig Vault (RRV) is a unique Blender rig pack and addon made by Roblox rigging innovators ChillingParibes and Comix... | [htzgj](https://paribes.gumroad.com/l/htzgj) |
| 13 | Roblox Rigs Suite | ComixProd. | free | Thanks to @BricksBree, @ChillingParibes, @MrSonicTeam, @MXFlamez, @Koth for beta testing this! I would really appreciate it if you donated, it's taken me... | [xpqyw](https://comixproductions.gumroad.com/l/xpqyw) |
| 14 | Roblox Starter Rigs (Blender 3.4+) | Softy | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [ytmdjz](https://softgb.gumroad.com/l/ytmdjz) |
| 15 | Roblox Starter Rigs (Blender 3.4+) | Paribes | free | Introducing Roblox Starter Rigs, which will match all your needs when making gfx, whether you are a beginner at gfx or experienced. It includes the... | [pblgq](https://paribes.gumroad.com/l/pblgq) |
| 16 | Roblox Starter Rigs 1.0 MODDED | Paribes | free | Starter rigs by SoftGB & ChillingParibes Modified rigs by imbob02 (seamless boy rigs) R15 rig by BaconofVibes Compiled by Malakai_GFX If you need rigs... | [xbrdsa](https://paribes.gumroad.com/l/xbrdsa) |
| 17 | Roblox Woman Blocky Legs Rig (Blender 4.0+) | Paribes | free | If you need rigs, contact me on Discord (chillingparibes)! https://discord.com/invite/Mc5PdfZnBd NOTE: redistributing or reselling the rigs, even if modified... | [oqjvxf](https://paribes.gumroad.com/l/oqjvxf) |
| 18 | Spider-Man Roblox Rig (4.4+) | Paribes | free | credits to @imbob02 , @BallzyGFX and @xmavster on Twitter for making this Starter Rigs mod! | [ogunp](https://paribes.gumroad.com/l/ogunp) |
| 19 | SuperRoblox (Roblox Rig) | ComixProd. | free | Superhero rig with a load of settings. | [jFnRyz](https://comixproductions.gumroad.com/l/jFnRyz) |
| 20 | Ultimate Roblox Rig | MattRBX | 5.00 | IF YOU DIDN'T RECIEVE THE PRODUCT OR HAVE SIMILAR ISSUES JOIN THE DISCORD SERVER BELOW !! Support Server: https://discord.gg/DvK73fgEka Ultimate Rig Premium... | [lnldn](https://mattrbx.gumroad.com/l/lnldn) |
| 21 | ⚽ Roblox Football/Soccer Rigs (Kit, Shoes, Trophies, ...) | Paribes | free | credit: @ChillingParibes - the rig @SoftGB - HD Faces @imbob02 - modified seamless boy rig vansire - football stuff on the rig and the boot textures... | [ovwtcn](https://paribes.gumroad.com/l/ovwtcn) |
| 22 | 🎮 Legendary Sky Champion Rig (Roblox: The Games) | Paribes | free | "Defeat" will be forever erased from your vocabulary. A brand new rig for the package Roblox released For Blender 4.2+ (probably works for minimum 4.0+) | [yowflf](https://paribes.gumroad.com/l/yowflf) |
| 23 | 🤖 AEPBR Roblox Rig (BETA) | Paribes | free | 🤖 STILL IN BETA!! Features it has so far: ☑️ Customisable face rig Customisable Eye Color Hideable Parts Face controls Mouth Sync Control Blink Control Teeth... | [wvyryw](https://paribes.gumroad.com/l/wvyryw) |
| 24 | 🧟 Roblox Zombie Rig (Blender 4.0+) | Paribes | free | zombie PS: The best works of Softy and STAR's contest will end up on this page as well! EDIT: Winning GFX has been added, made by @vanziervh If you need... | [quhwki](https://paribes.gumroad.com/l/quhwki) |

## Animation (4)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 25 | How to Design An Anime Units UI in Roblox Studio | gfxcomet | 6.00 | _(page unavailable: HTTPError)_ | [vjvcdvq](https://gfxcomet.gumroad.com/l/vjvcdvq) |
| 26 | Roblox Studio: Movement system (8 directions) | LionDev | 12.00 | This package for Roblox Studio includes a movement system that detects the direction in which the character is moving and plays the appropriate animations... | [cddbt](https://liondev.gumroad.com/l/cddbt) |
| 27 | Worm Host Animation | Satch Nomad | 20.00 | This is a custom animation that can be easily transfered over to the custom character model of your choice. the "Worm Host", is a 3D combat/ability splash... | [racij](https://n5studios.gumroad.com/l/racij) |
| 28 | 🏃 Roblox Animation Starter Pack | Paribes | free | A bunch of assets you could possibly need to start as an animator! | [knclku](https://paribes.gumroad.com/l/knclku) |

## Gameplay systems (12)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 29 | [Roblox Studio]Advanced  (Suspicious)  NPC System | TheTomato | free | _(page unavailable: HTTPError)_ | [hfmpt](https://thetomato.gumroad.com/l/hfmpt) |
| 30 | [‼️ON SALE‼️] Advanced Roblox NPC System | _mosES() | 0.99 | _(page unavailable: HTTPError)_ | [ggtge](https://mose5.gumroad.com/l/ggtge) |
| 31 | Jeano's Gun Framework | Jeano | 1.00 | _(page unavailable: HTTPError)_ | [xvpxc](https://scofieldstudios.gumroad.com/l/xvpxc) |
| 32 | R6 ROBLOX REALISTIC MOVEMENT/CAMERA SYSTEM | JUNIS | 9.99 | A high-quality, professional First Person Movement System for ROBLOX R6, designed to deliver a smooth and immersive gameplay experience!! 🎮 Key Features... | [aorzrj](https://clownjunis.gumroad.com/l/aorzrj) |
| 33 | Roblox Advanced Player Data System (Attributes + DataStore) | AB price | 50.00 | _(page unavailable: HTTPError)_ | [lprem](https://abprice.gumroad.com/l/lprem) |
| 34 | Roblox Boid System | Tekleed | 15.00 | _(page unavailable: HTTPError)_ | [vxmjq](https://tekleed.gumroad.com/l/vxmjq) |
| 35 | Roblox FPS System | Jeynkins | 12.00 | _(page unavailable: HTTPError)_ | [gfmdgs](https://jeynkinsrbxlstudios.gumroad.com/l/gfmdgs) |
| 36 | Roblox Halloween Obby Game | Megalodons Studios | 7.19 | _(page unavailable: HTTPError)_ | [lzmkp](https://megalodonsstudios1.gumroad.com/l/lzmkp) |
| 37 | Roblox Jojo Bizarre Incremental Script \| Auto Combat, Auto  | Rixtreat | 0.99 | _(page unavailable: HTTPError)_ | [nprkf](https://rixtreat.gumroad.com/l/nprkf) |
| 38 | Roblox Obby Game | Megalodons Studios | 4.49 | _(page unavailable: HTTPError)_ | [hsaqy](https://megalodonsstudios1.gumroad.com/l/hsaqy) |
| 39 | Roblox Ocean System | Tekleed | 200.00 | _(page unavailable: HTTPError)_ | [qgvvc](https://tekleed.gumroad.com/l/qgvvc) |
| 40 | Sword Combat & NPC System [ROBLOX] | Pierce | 5.00 | _(page unavailable: HTTPError)_ | [swhwn](https://piercedevelop.gumroad.com/l/swhwn) |

## Art, textures & props (9)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 41 | 25 Brainroit Pets for Fortnite UEFN/Roblox 🧠 | Eve3D_UEFN | free | 25 Brainroit Pets for Fortnite UEFN/Roblox 🧠 🔥 One-Time Purchase Investment! ⚡ ROI in a Week!!! ✅ In-Island Transactions License 📨DM for direct inquiry 💲 For... | [hvrti](https://eve3duefn.gumroad.com/l/hvrti) |
| 42 | 40 Brainroit Pets V2 for Fortnite UEFN/Roblox 🧠 | Eve3D_UEFN | 55.30 | _(page unavailable: HTTPError)_ | [umfhc](https://eve3duefn.gumroad.com/l/umfhc) |
| 43 | Currency & Collectables Asset Pack #1 - UEFN / UE5 / ROBLOX | EAY Visuals | 20.00 | _(page unavailable: HTTPError)_ | [vimbo](https://eayvisuals.gumroad.com/l/vimbo) |
| 44 | DAV's Roblox Studio Prison Map | DAV | 60.00 | _(page unavailable: HTTPError)_ | [zoccgh](https://mystique427.gumroad.com/l/zoccgh) |
| 45 | Essential 20 Pets for Fortnite UEFN/Roblox 🐇🐱 | Eve3D_UEFN | 42.00 | _(page unavailable: HTTPError)_ | [nvnec](https://eve3duefn.gumroad.com/l/nvnec) |
| 46 | Minimap For Roblox Studio | Nytrix Prime | 7.99 | _(page unavailable: HTTPError)_ | [zpipkh](https://nytrixprime4.gumroad.com/l/zpipkh) |
| 47 | Pepper's Roblox Face Assets: Ver 1.0 | mors | 1.00 | _(page unavailable: HTTPError)_ | [yAZuE](https://rblxmors.gumroad.com/l/yAZuE) |
| 48 | Roblox Stylized Environment \| Oak Forest \| Small 3D Asset  | Jeeno | 15.99 | _(page unavailable: HTTPError)_ | [qjgzmi](https://jeenodev.gumroad.com/l/qjgzmi) |
| 49 | Roblox Stylized Oak Forest \| Full 3D Asset Pack | Jeeno | 24.99 | _(page unavailable: HTTPError)_ | [fqzaua](https://jeenodev.gumroad.com/l/fqzaua) |

## UI & interface (3)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 50 | How To Design a Shop UI in Roblox Studio (Tutorial) | gfxcomet | 6.00 | _(page unavailable: HTTPError)_ | [uhfiea](https://gfxcomet.gumroad.com/l/uhfiea) |
| 51 | INFINITE WORLDS:   How Gaming, Virtual Reality, AI Worldbuil | Fahri Karakaş | 4.99 | _(page unavailable: HTTPError)_ | [cvxvng](https://karakasfahri.gumroad.com/l/cvxvng) |
| 52 | Roblox Makeup Thumbnail Mannequin Template | Instance Enterprises | 10.00 | _(page unavailable: HTTPError)_ | [idggih](https://instanceenterprises.gumroad.com/l/idggih) |

## Education & templates (3)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 53 | Design Academy - Learn Roblox Design | gfxcomet | 23.40 | _(page unavailable: HTTPError)_ | [fiqpf](https://gfxcomet.gumroad.com/l/fiqpf) |
| 54 | Roblox Outlast Pack \| Updated! | Jeynkins | 24.00 | _(page unavailable: HTTPError)_ | [ifkvke](https://jeynkinsrbxlstudios.gumroad.com/l/ifkvke) |
| 55 | Roblox Rant Editing Resources | Hexa Visual | 5.00 | Grab the best ROBLOX RANT resources NOW! You looking for roblox rant pack? yeah thats why you are here - there is tons of resources that is going to help you... | [awhdb](https://hexavisual.gumroad.com/l/awhdb) |

## Uncategorised (13)

| # | product | seller | price | what the listing claims | source |
|---|---|---|---|---|---|
| 56 | Cartoony Roblox Shader (Blender 3D) | Paribes | free | _(page unavailable: HTTPError)_ | [vouyo](https://paribes.gumroad.com/l/vouyo) |
| 57 | Escape A Tsunami (Cars Edition) \| Roblox Studio | Nytrix Prime | 9.99 | Escape A Tsunami (Cars Edition) \| Roblox Studio Escape A Tsunami (Cars Edition) is a complete, fully playable Roblox game where players must upgrade their... | [dqsxd](https://nytrixprime4.gumroad.com/l/dqsxd) |
| 58 | FIXED Kylie De'Amore \| Procreate Roblox Pattern+Stamps Brus | kylie deamore | 4.99 | _(page unavailable: HTTPError)_ | [jvzmq](https://kyliedeamore.gumroad.com/l/jvzmq) |
| 59 | GP5 Soviet Gas Mask [VRChat \| Roblox] | Mori Unofficial | 5.00 | _(page unavailable: HTTPError)_ | [rpphn](https://moriunofficial.gumroad.com/l/rpphn) |
| 60 | Kylie De'Amore \| Procreate Art/Roblox Designing Brushes | kylie deamore | 4.99 | _(page unavailable: HTTPError)_ | [mudxs](https://kyliedeamore.gumroad.com/l/mudxs) |
| 61 | Roblox First Person Shooter Game | Megalodons Studios | 4.49 | _(page unavailable: HTTPError)_ | [sstsz](https://megalodonsstudios1.gumroad.com/l/sstsz) |
| 62 | Roblox FPS Deathmatch Game | Megalodons Studios | 4.49 | _(page unavailable: HTTPError)_ | [xjkdc](https://megalodonsstudios1.gumroad.com/l/xjkdc) |
| 63 | Roblox Material Fixer+ Backface Culling Node (Blender) | Paribes | free | _(page unavailable: HTTPError)_ | [tztba](https://paribes.gumroad.com/l/tztba) |
| 64 | Roblox Murder Mystery Game | Megalodons Studios | 4.49 | _(page unavailable: HTTPError)_ | [fdwkuk](https://megalodonsstudios1.gumroad.com/l/fdwkuk) |
| 65 | Roblox Stud Material | rKaype | 15.00 | _(page unavailable: HTTPError)_ | [yhhjs](https://rkaype.gumroad.com/l/yhhjs) |
| 66 | Roblox Zombie Wave Game | Megalodons Studios | 4.49 | _(page unavailable: HTTPError)_ | [thlaa](https://megalodonsstudios1.gumroad.com/l/thlaa) |
| 67 | Studio Color - (Plugin) | MrQuaxkers | 6.99 | Full coloring toolkit for roblox studio. | [wbfovn](https://mrquaxkers.gumroad.com/l/wbfovn) |
| 68 | WEPPY Roblox Plugin Pro | Weppy | 9.99 | 🚀 WEPPY Roblox AI Toolkit Pro — AI-Powered Roblox Studio Workflow Ship production Roblox workflows faster with AI coding agents connected directly to Roblox... | [faccjs](https://weppy.gumroad.com/l/faccjs) |

---

Scraped 2026-11-28. Regenerate with `tools/gumroad_scrape.py` then `tools/compile_slerm.py`.
