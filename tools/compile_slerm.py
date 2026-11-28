"""compile_slerm — turn the scraped Gumroad listings into a citable battlefield document.

Input:  specs/gumroad_roblox_listings.json  (from tools/gumroad_scrape.py)
Output: docs/SLERM_BATTLEFIELD.md           (every row carries its own source URL)

Descriptions are fetched once per product and cached next to the listing file, so re-running the
compiler is cheap and the document never claims a product does something its page does not say.
"""

import html
import json
import os
import re
import sys
import time
import urllib.request

BOX = "/opt/data/work/wubu3d"
LISTINGS = os.path.join(BOX, "specs/gumroad_roblox_listings.json")
CACHE = "/opt/data/cache/scratch/gumroad_desc.json"
OUT = os.path.join(BOX, "docs/SLERM_BATTLEFIELD.md")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

CATS = [
    ("Rigging & skinning", ("rig", "skinning", "weight", "skeleton", "joint", "motor6d", "pose")),
    ("Animation", ("anim", "walk", "run", "idle", "motion", "keyframe", "mocap")),
    ("Gameplay systems", ("system", "combat", "inventory", "gun", "weapon", "tycoon", "obby",
                          "movement", "camera", "data")),
    ("Art, textures & props", ("texture", "map", "environment", "tree", "forest", "model", "prop",
                               "asset", "chain", "pet")),
    ("UI & interface", ("ui", "interface", "gui", "hud", "menu")),
    ("Education & templates", ("learn", "academy", "course", "template", "guide", "tutorial",
                              "resources", "pack")),
]


def fetch_desc(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        page = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
    except Exception as e:
        return "_(page unavailable: %s)_" % type(e).__name__
    m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]{10,400})"', page, re.I)
    if not m:
        m = re.search(r'<meta[^>]+property="og:description"[^>]+content="([^"]{10,400})"', page, re.I)
    if not m:
        return "_no description in page metadata_"
    d = html.unescape(m.group(1))
    d = re.sub(r"\s+", " ", d).strip()
    return d.replace("|", "\\|")


def category(name, desc):
    hay = (name + " " + desc).lower()
    for label, keys in CATS:
        if any(k in hay for k in keys):
            return label
    return "Uncategorised"


EPIGRAPH = (
    "> \u201cto slerm is to raise the floor standards, do not feel bad you are on here, "
    "understand that time marches forward, do not become a boomer\u201d"
)


def main():
    if not os.path.exists(LISTINGS):
        print("missing", LISTINGS)
        return 1
    data = json.load(open(LISTINGS))
    prods = data["products"]

    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE))
    todo = [p for p in prods if p["url"] not in cache]
    print("descriptions: %d cached, %d to fetch" % (len(cache), len(todo)))
    for i, p in enumerate(todo):
        cache[p["url"]] = fetch_desc(p["url"])
        if i % 10 == 0:
            print("  %d/%d" % (i, len(todo)))
        time.sleep(0.25)
    json.dump(cache, open(CACHE, "w"), indent=1)

    for p in prods:
        p["desc"] = cache.get(p["url"], "")
        p["cat"] = category(p["name"], p["desc"])

    by_cat = {}
    for p in prods:
        by_cat.setdefault(p["cat"], []).append(p)

    L = []
    A = L.append
    A("# The SLERM battlefield\n")
    A(EPIGRAPH + "\n")
    A("Every listing below was scraped from Gumroad's public search, %d queries, %d products, "
      "%d kept as Roblox-related.\n" % (len(data.get("queries", [])), len(data.get("all", prods)),
                                        len(prods)))
    A("The point is not to buy anything. The point is that a paid tool's *description* is a "
      "specification: it names the operation, the input and the promise. That is enough to "
      "reimplement the operation in C11 and measure whether it holds.\n")
    A("Nothing here is copied, decompiled or redistributed. Names, prices and links are cited so a "
      "reader can check the claim at its source.\n")

    A("\n## What is already on the floor\n")
    A("| capability | file | measured |\n|---|---|---|")
    A("| per-pixel lighting (lambert + point lights + rim + ground AO) | `src/shade.c` | "
      "gradient p90 0.11 -> 0.51 with 2x SSAA |")
    A("| adaptive auto-skinning (distance + Laplacian smoothing + top-k) | `src/rig.c` | "
      "crease 0.00442 -> 0.00240 over 32 passes |")
    A("| two-bone IK with pole, FABRIK for longer chains | `src/rig.c` | end->target 0.000000, "
      "lengths constant |")
    A("| auto-rig (band analysis, side split) | `src/rig.c` | mean joint error 0.031 body units |")
    A("| grip / attach / surface placement | `src/grab.c` | placement 0.00000, rigidity 0.000000 |")
    A("| blocky R15 rig with measured band table | `r15.py` | 7/7 invariants pass |")
    A("| planted IK walk (duty, slip) | `animate_r15.py` | slip 0.41 -> 0.075, penetration 28 -> 3.7 mm |")
    A("| Roblox asset import (.mesh v1 soup, v4 binary, rbxm) | `rbxmesh.py`, `rbxm.py` | "
      "506-tri UGC item parsed |")

    cite = 0
    for label, _ in CATS + [("Uncategorised", ())]:
        items = by_cat.get(label) or []
        if not items:
            continue
        A("\n## %s (%d)\n" % (label, len(items)))
        A("| # | product | seller | price | what the listing claims | source |")
        A("|---|---|---|---|---|---|")
        for p in sorted(items, key=lambda x: x["name"].lower()):
            cite += 1
            A("| %d | %s | %s | %s | %s | [%s](%s) |" % (
                cite, p["name"].replace("|", "\\|")[:60], p["seller"][:22] or "-",
                (p["price"] or "free"), (p["desc"] or "")[:190], p["url"].split("/")[-1], p["url"]))
    A("\n---\n")
    A("Scraped %s. Regenerate with `tools/gumroad_scrape.py` then `tools/compile_slerm.py`." %
      time.strftime("%Y-%m-%d"))
    open(OUT, "w").write("\n".join(L) + "\n")
    print("wrote %s (%d bytes, %d citations)" % (OUT, os.path.getsize(OUT), cite))
    return 0


if __name__ == "__main__":
    sys.exit(main())
