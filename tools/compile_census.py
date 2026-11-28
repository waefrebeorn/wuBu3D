"""compile_census — build docs/SLERM_BATTLEFIELD.md from the Gumroad tool census.

Scope: all of Gumroad's tool market, code first. Asset packs are excluded by rule — a model cannot be
slermed, an operation can. Every row keeps its own source URL so a reader can check the claim where it
was made; descriptions come from the page's own metadata and are cached so the document never
paraphrases something the listing does not say.
"""

import html
import json
import os
import re
import sys
import time
import urllib.request

BOX = "/opt/data/work/wubu3d"
SRC = os.path.join(BOX, "specs/gumroad_tools.json")
CACHE = "/opt/data/cache/scratch/gumroad_desc_all.json"
OUT = os.path.join(BOX, "docs/SLERM_BATTLEFIELD.md")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

CATS = [
    ("Shaders & rendering", ("shader", "render", "glsl", "hlsl", "raytrac", "post process",
                             "toon", "lighting", "skybox", "water", "material", "texture bake")),
    ("Rigging, skinning & animation", ("rig", "skinning", "weight", "skeleton", "joint", "ik",
                                       "anim", "motion capture", "mocap", "keyframe", "walk")),
    ("Modeling, mesh & procedural", ("mesh", "retopo", "uv", "topolog", "procedural", "geometry node",
                                    "modifier", "boolean", "subdivision", "sculpt")),
    ("VFX & simulation", ("vfx", "particle", "niagara", "simulation", "fluid", "cloth", "destruction",
                          "water sim", "explosion")),
    ("Engine tooling: Unity / Godot / Unreal", ("unity", "godot", "unreal", "ue5", "ue4", "editor tool")),
    ("Roblox tools", ("roblox", "r15", "r6", "blocky", "studio")),
    ("Gameplay systems", ("system", "combat", "inventory", "movement", "camera", "save", "data",
                          "quest", "npc", "ai ", "procedural gen")),
    ("Audio", ("audio", "vst", "sound", "music", "synth", "dsp")),
    ("Pipeline, export & automation", ("pipeline", "export", "import", "automation", "batch",
                                       "converter", "baker", "optimis", "optimiz")),
    ("UI & interface", ("ui", "interface", "gui", "hud", "menu", "widget")),
]

EPIGRAPH = (
    "> \u201cto slerm is to raise the floor standards, do not feel bad you are on here, "
    "understand that time marches forward, do not become a boomer\u201d"
)

BUILT = [
    ("per-pixel lighting: lambert, point lights, fresnel rim, ground AO, 2x SSAA",
     "src/shade.c", "gradient p90 0.11 -> 0.51, distinct colours 58 -> 194"),
    ("adaptive auto-skinning: distance binding, Laplacian weight smoothing, top-k",
     "src/rig.c", "crease 0.00442 -> 0.00240 over 32 passes"),
    ("two-bone IK with pole vector, FABRIK for n-bone chains",
     "src/rig.c", "end->target 0.000000, segment lengths constant to 6 dp"),
    ("auto-rig: height bands, medial axis, inboard/outboard limb split",
     "src/rig.c", "mean joint error 0.031 body units, max 0.073"),
    ("grip, attach, surface placement, grid snap",
     "src/grab.c", "placement 0.00000, rigidity 0.000000, drift 0.0438"),
    ("blocky R15 rig on a measured band table with an invariant audit",
     "r15.py", "7/7 invariants pass"),
    ("planted IK walk: world-fixed stance, root cancellation, contact-phase bob",
     "animate_r15.py", "slip 0.41 -> 0.075, duty 0.19 -> 0.62, penetration 28 -> 3.7 mm"),
    ("Roblox asset import: .mesh v1 soup, .mesh v4 binary, rbxm binary",
     "rbxmesh.py, rbxm.py", "506-triangle UGC item parsed end to end"),
    ("specular (Blinn-Phong half-vector, per-pixel) + depth of field from the z-buffer",
     "src/shade.c, render_shaded.py", "highlights 0 -> 3180 px over 200; bg variance 57 -> 42"),
    ("per-pixel texture sampling with perspective-correct UVs",
     "src/shade.c wubu_tex", "unique colours 85 -> 279, local detail 0.82 -> 4.30 on a checkerboard"),
    ("procedural placement: Bridson Poisson-disk, exclusion circles, per-instance scale/rotation",
     "src/scatter.c", "min pair 0.1600 against a 0.160 radius (uniform random: 0.0023); 0 in clearings"),
]


def fetch_desc(url):
    try:
        page = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                      timeout=20).read().decode("utf-8", "replace")
    except Exception as e:
        return "_page unavailable (%s)_" % type(e).__name__
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]{5,400})"', page, re.I) or \
        re.search(r'<meta[^>]+property="og:description"[^>]+content="([^"]{5,400})"', page, re.I)
    if not m:
        return "_no description in metadata_"
    d = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
    return d.replace("|", "\\|")


def cat_of(name, desc):
    hay = (name + " " + desc).lower()
    for label, keys in CATS:
        if any(k in hay for k in keys):
            return label
    return "Uncategorised"


def main():
    if not os.path.exists(SRC):
        print("missing", SRC)
        return 1
    data = json.load(open(SRC))
    prods = data["tools"]
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [p for p in prods if p["url"] not in cache]
    print("descriptions: %d cached, %d to fetch" % (len(cache), len(todo)))
    for i, p in enumerate(todo):
        cache[p["url"]] = fetch_desc(p["url"])
        if i % 25 == 0:
            print("  %d/%d" % (i, len(todo)))
        time.sleep(0.15)
        if i % 40 == 39:
            json.dump(cache, open(CACHE, "w"))
    json.dump(cache, open(CACHE, "w"), indent=1)

    for p in prods:
        p["desc"] = cache.get(p["url"], "")
        p["cat"] = cat_of(p["name"], p["desc"])

    groups = {}
    for p in prods:
        groups.setdefault(p["cat"], []).append(p)

    L, A = [], None
    A = L.append
    A("# The SLERM battlefield\n")
    A(EPIGRAPH + "\n")
    A("A census of Gumroad's **tool** market — plugins, addons, shaders, editor tools, systems. Not its"
      " asset packs: a model cannot be slermed, an operation can.\n")
    A("Scope: %d queries, %d listings scraped, **%d tools kept**, %d dropped as asset packs. "
      "Scraped %s.\n" % (len(data.get("queries", [])), len(data.get("all", prods)), len(prods),
                          sum(1 for r in data.get("all", []) if r.get("kind") == "asset"),
                          time.strftime("%Y-%m-%d")))
    A("A paid tool's description is a specification: it names the operation, the input and the promise."
      " That is enough to reimplement the operation in C11 and measure whether it holds. Nothing here"
      " is copied or redistributed — names, prices, claims and links are citation only.\n")

    A("\n## What already stands on this floor\n")
    A("| capability | file | measured |\n|---|---|---|")
    for cap, f, m in BUILT:
        A("| %s | `%s` | %s |" % (cap, f, m))
    A("\nNot implemented yet, and said plainly: **texture sampling** (surfaces are flat-coloured), "
      "**cast shadows** (a contact ellipse stands in), **bevels**, **retargeting**, "
      "**squash/stretch**, and **translucency** — the glossy subsurface look of a TrendStory-style "
      "vinyl character is a transmission model we do not have, even though the specular highlight and "
      "the depth of field around it now exist.\n")

    n = 0
    order = [c for c, _ in CATS] + ["Uncategorised"]
    for label in order:
        items = groups.get(label) or []
        if not items:
            continue
        A("\n## %s (%d)\n" % (label, len(items)))
        A("| # | product | maker | price | the listing's own claim | source |")
        A("|---|---|---|---|---|---|")
        for p in sorted(items, key=lambda x: x["name"].lower()):
            n += 1
            A("| %d | %s | %s | %s | %s | [%s](%s) |" % (
                n, p["name"].replace("|", "/")[:60], p["seller"][:22] or "-",
                p["price"] or "free", (p["desc"] or "")[:170], p["url"].split("/")[-1], p["url"]))

    # ---- what the hops reached
    hops_path = os.path.join(BOX, "specs/gumroad_hops.json")
    if os.path.exists(hops_path):
        hops = json.load(open(hops_path)).get("hops", [])
        by = {}
        for h in hops:
            key = (h.get("query") or "hop").replace("gap:", "").replace("lilypad:", "seller:")
            by.setdefault(key, []).append(h)
        A("\n## Reached by hopping (%d products)\n" % len(hops))
        A("Straight search only finds what you already thought to ask for. These came from searching "
          "the *operation* instead of the domain, and from reading a maker's whole catalogue. Each "
          "group is one hop; the URL is the product the hop landed on.\n")
        A("| hop | products | examples |")
        A("|---|---|---|")
        for k in sorted(by, key=lambda x: -len(by[x])):
            ex = by[k][:3]
            exs = ", ".join("[%s](%s)" % ((e.get("name") or "")[:38].replace("|", "/"), e["url"]) for e in ex)
            A("| %s | %d | %s |" % (k, len(by[k]), exs))
    A("\n---\n")
    A("Regenerate: `python3 tools/gumroad_census.py --market all` then "
      "`python3 tools/compile_census.py`. Query list and scrape date are in "
      "`specs/gumroad_tools.json`.")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("wrote %s (%d bytes, %d rows)" % (OUT, os.path.getsize(OUT), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
