"""gap_search — search Gumroad for the OPERATIONS wubu3d lacks, not for the word "roblox".

The first census learned what the Roblox tool market sells. This pass asks the complementary
question: who sells particles, retopology, cloth, groom, navmesh, LOD, occlusion — the rows of
`docs/WUBU3D_GAPS.md` that we marked `none`. One query per missing capability, then a seller hop for
any maker that shows up more than once (that is where the catalogues are).

Every row keeps `via` = the capability it was found under, so the gap table cites itself.
"""

import html
import json
import os
import random
import re
import time
import urllib.parse
import urllib.request

BOX = "/opt/data/work/wubu3d"
CENSUS = os.path.join(BOX, "specs/gumroad_tools.json")
OUT = os.path.join(BOX, "specs/gumroad_hops.json")
UAS = ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36",
       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15"]

# the gaps, as search terms
GAP_QUERIES = [
    "particle system", "vfx particles", "cloth simulation", "ragdoll physics",
    "retopology tool", "hair groom", "fur shader", "navmesh pathfinding",
    "lod generator", "occlusion culling", "gpu instancing", "decal projection",
    "texture atlas", "normal map baker", "subsurface scattering shader",
    "translucent shader", "procedural scatter", "foliage shader", "squash stretch rig",
    "motion matching", "retarget animation", "vertex color painter", "uv packing tool",
    "soft body simulation", "water simulation", "god rays volumetric light",
    "toon outline shader", "rim light shader", "matcap shader", "cubemap reflection",
]


def fetch(url, tries=2, timeout=25):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": random.choice(UAS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                "Accept-Language": "en-US,en;q=0.9"})
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception:
            if t == tries - 1:
                return ""
            time.sleep(6.0)
    return ""


def products_at(page):
    text = html.unescape(page)
    i = text.find('"products":')
    if i < 0:
        return []
    j = text.find("[", i)
    depth, k = 0, j
    while k < len(text) and j >= 0:
        if text[k] == "[":
            depth += 1
        elif text[k] == "]":
            depth -= 1
            if depth == 0:
                break
        k += 1
    try:
        items = json.loads(text[j:k + 1])
    except Exception:
        return []
    out = []
    for d in items:
        if "permalink" not in d or "name" not in d:
            continue
        seller = d.get("seller") or {}
        m = re.match(r"https://([a-z0-9-]+)\.gumroad\.com", seller.get("profile_url") or "")
        sub = m.group(1) if m else ""
        out.append(dict(
            name=d.get("name", "").strip(), seller=seller.get("name", "") or sub,
            url=("https://%s.gumroad.com/l/%s" % (sub, d["permalink"])) if sub
            else "https://gumroad.com/l/%s" % d["permalink"],
            price=d.get("formatted_price") or "", sub=sub))
    return out


def main():
    census = json.load(open(CENSUS))
    known = {p["url"] for p in census["all"]}
    hops = []
    if os.path.exists(OUT):
        try:
            hops = json.load(open(OUT)).get("hops", [])
        except Exception:
            hops = []
    seen = {h["url"] for h in hops}

    sellers = {}
    for q in GAP_QUERIES:
        page = fetch("https://gumroad.com/discover?query=" + urllib.parse.quote(q))
        got = products_at(page)
        new = 0
        for g in got:
            if g["url"] in known or g["url"] in seen:
                continue
            g["query"] = "gap:%s" % q
            hops.append(g)
            seen.add(g["url"])
            new += 1
            sellers[g["sub"]] = sellers.get(g["sub"], 0) + 1
        print("%-30s %3d found, %2d new" % (q, len(got), new))
        time.sleep(3.0)

    # seller hop on makers that appeared more than once under these capability searches
    rich = [s for s, n in sorted(sellers.items(), key=lambda kv: -kv[1]) if s and n >= 2][:12]
    print("\nseller hops: %s" % ", ".join(rich))
    for sub in rich:
        page = fetch("https://%s.gumroad.com/" % sub)
        if not page:
            continue
        text = html.unescape(page)
        got = 0
        for m in re.finditer(r"/l/([a-z0-9]+)", text):
            u = "https://%s.gumroad.com/l/%s" % (sub, m.group(1))
            if u in known or u in seen:
                continue
            hops.append(dict(name=m.group(1), seller=sub, url=u, price="", query="lilypad:%s" % sub, sub=sub))
            seen.add(u)
            got += 1
        print("  %-20s %2d new" % (sub, got))
        time.sleep(3.0)

    json.dump(dict(queries=GAP_QUERIES, sellers=rich, hops=hops,
                   generated=time.strftime("%Y-%m-%d")), open(OUT, "w"), indent=1)
    print("\ntotal hop rows: %d -> %s" % (len(hops), OUT))


if __name__ == "__main__":
    main()
