"""gumroad_census — census Gumroad's tool market (code, plugins, shaders), not its asset packs.

The rule this file encodes: **a model cannot be slermed, an operation can.** A rig file or a texture
pack is a product; a shader, an addon, an editor tool or a system is a specification you can
reimplement and measure. So the query pass is wide across engines and formats, and the filter keeps
tools while dropping asset packs.

Gumroad's discover page is client-rendered: product data sits in an HTML-escaped JSON blob under
`"products":`. Parse the array, never the markup — a `[^{}]*` regex over product objects returns zero
rows because every product nests its seller and price.

    python3 gumroad_census.py --market all --out specs/gumroad_tools.json
"""

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

QUERIES_ROBLOX = [
    "roblox plugin", "roblox rig", "roblox animation", "roblox studio tool",
    "roblox vfx", "roblox ui kit", "roblox npc", "roblox combat",
    "roblox inventory", "roblox gun", "roblox texture", "roblox r15",
    "roblox script", "roblox system", "roblox builder", "roblox obby",
]

QUERIES_ALL = QUERIES_ROBLOX + [
    "shader", "unity shader", "blender shader", "godot shader", "glsl shader",
    "shader graph", "compute shader", "vfx graph", "post processing",
    "toon shader", "water shader", "skybox shader", "raytracer",
    "blender addon", "blender python", "geometry nodes", "blender tool",
    "unity editor tool", "unity plugin", "godot plugin", "godot addon",
    "unreal engine plugin", "ue5 tool", "niagara vfx", "houdini hda",
    "procedural tool", "retopology", "uv tool", "mesh tool", "rigging tool",
    "auto rig", "animation tool", "node editor", "pixel art tool",
    "audio plugin", "vst plugin", "motion graphics tool",
]

KEEP = ("plugin", "addon", "shader", "tool", "system", "script", "editor",
        "extension", "framework", "generator", "simulation", "automation",
        " rig", "ik ", "ik/", "anim", "pipeline", "library", "sdk", "api",
        "vfx", "engine", "procedural", "baker")
DROP = ("3d model", "model pack", "models pack", "asset pack", "assets pack",
        "texture pack", "textures pack", "environment pack", "map pack",
        "sound pack", "music pack", "sfx pack", "font pack", "icon pack",
        "pose pack", "poses pack", "mocap pack", "sample pack", "preset pack",
        "brush pack", "stl ", "fbx pack", "obj pack")


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def _array_at(text, key):
    i = text.find(key)
    if i < 0:
        return None
    j = text.find("[", i)
    depth, k = 0, j
    while k < len(text) and j >= 0:
        if text[k] == "[":
            depth += 1
        elif text[k] == "]":
            depth -= 1
            if depth == 0:
                return text[j:k + 1]
        k += 1
    return None


def products_from(page, query):
    text = html.unescape(page)
    items = []
    arr = _array_at(text, '"products":')
    if arr:
        try:
            items = json.loads(arr)
        except Exception:
            items = []
    out = []
    for d in items:
        if "permalink" not in d or "name" not in d:
            continue
        seller = d.get("seller") or {}
        m = re.match(r"https://([a-z0-9-]+)\.gumroad\.com", seller.get("profile_url") or "")
        url = ("https://%s.gumroad.com/l/%s" % (m.group(1), d["permalink"])) if m else \
              ("https://gumroad.com/l/%s" % d["permalink"])
        out.append(dict(
            name=d.get("name", "").strip(), seller=seller.get("name", "").strip(), url=url,
            price=d.get("formatted_price") or (
                "%.2f" % (d.get("price_cents", 0) / 100.0) if d.get("price_cents") else ""),
            currency=d.get("currency_code", ""), query=query,
            ratings=d.get("ratings_count"), sales=d.get("sales_count")))
    return out


def classify(name, url, market):
    hay = (name + " " + url).lower()
    if any(k in hay for k in DROP):
        return "asset"
    if market == "roblox" and not any(k in hay for k in ("roblox", "r15", "r6", "blocky", "studio")):
        return "off-topic"
    if any(k in hay for k in KEEP):
        return "tool"
    return "unclear"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", default="all", choices=["all", "roblox"])
    ap.add_argument("--out", default="specs/gumroad_tools.json")
    ap.add_argument("--queries", default="")
    a = ap.parse_args()
    queries = [q.strip() for q in a.queries.split("|") if q.strip()] or \
              (QUERIES_ALL if a.market == "all" else QUERIES_ROBLOX)

    rows, seen = [], set()
    for q in queries:
        url = "https://gumroad.com/discover?query=" + urllib.parse.quote(q)
        try:
            page = fetch(url)
        except Exception as e:
            print("FAIL %-24s %s" % (q, e))
            continue
        got = products_from(page, q)
        new = 0
        for r in got:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            rows.append(r)
            new += 1
        print("%-24s %3d products, %3d new" % (q, len(got), new))
        time.sleep(0.6)

    for r in rows:
        r["kind"] = classify(r["name"], r["url"], a.market)
    tools = [r for r in rows if r["kind"] == "tool"]
    assets = sum(1 for r in rows if r["kind"] == "asset")
    print("\nraw %d | tools %d | assets dropped %d | unclear %d"
          % (len(rows), len(tools), assets, len(rows) - len(tools) - assets))
    json.dump(dict(market=a.market, queries=queries, tools=tools, all=rows),
              open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
