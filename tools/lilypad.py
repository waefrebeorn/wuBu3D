"""lilypad — hop the Gumroad tool graph two ways, and keep the provenance of every hop.

Straight search only finds what you already know to ask for. Two other moves find the rest:

  **lilypad** (seller hop): a maker who sells one rigging tool usually sells four. Read the seller's
  profile page and take every product on it. This is how a census of 438 becomes a census of the
  market's actual working catalogues.

  **kevin bacon** (keyword hop): every description names operations — "retopology", "subsurface",
  "cloth sim", "LOD", "gpu instancing". Search those words. A product you never searched for is one
  hop from a product you did, and the hop is the interesting part.

Every new row records `via` — the seller or the keyword that led there — so a reader can walk the
chain back instead of taking the row on faith.

    python3 tools/lilypad.py --sellers 40 --keywords 25
"""

import argparse
import html
import json
import os
import random
import re
import time
import urllib.parse
import urllib.request

BOX = "/opt/data/work/wubu3d"
SEED = os.path.join(BOX, "specs/gumroad_tools.json")
OUT = os.path.join(BOX, "specs/gumroad_hops.json")
UAS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
]

# words that name an OPERATION. A tool that advertises one is a specification for that operation.
CAPS = [
    "retopolog", "subsurface", "sss", "cloth sim", "hair card", "groom", "procedural",
    "tileable", "normal map", "decal", "lod", "batching", "gpu instancing", "occlusion",
    "raytrac", "path trac", "denois", "bloom", "motion blur", "depth of field", "chromatic",
    "volumetric", "fog", "ssao", "shadow map", "cascade", "parallax", "displacement",
    "vertex paint", "weight paint", "auto weight", "auto rig", "ik solver", "retarget",
    "motion matching", "blend tree", "state machine", "navmesh", "pathfind", "lod group",
    "bake", "atlas", "uv unwrap", "boolean", "sculpt", "subdiv", "bevel", "extrude",
    "squash", "stretch", "jiggle", "physics", "ragdoll", "constraint", "spline",
    "instance", "chunk", "streaming", "culling", "batching", "atlas", "shader graph",
    "compute shader", "geometry shader", "tessellation", "deferred", "forward+",
]


def fetch(url, tries=2, timeout=25):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": random.choice(UAS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9"})
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception:
            if t == tries - 1:
                return ""
            time.sleep(5.0)
    return ""


def seller_products(sub):
    """Every product on a seller's profile page."""
    page = fetch("https://%s.gumroad.com/" % sub)
    if not page:
        return []
    text = html.unescape(page)
    out, seen = [], set()
    for m in re.finditer(r'/l/([a-z0-9]+)', text):
        perm = m.group(1)
        if perm in seen:
            continue
        seen.add(perm)
        # the nearest product name in the markup, if the card carries one
        seg = text[max(0, m.start() - 600):m.start()]
        nm = re.findall(r'aria-label="([^"]{4,90})"', seg) or \
             re.findall(r'alt="([^"]{4,90})"', seg) or \
             re.findall(r'>([A-Z][^<>]{6,70})<', seg)
        name = html.unescape(nm[-1]).strip() if nm else ""
        out.append(dict(name=name or perm, seller=sub, url="https://%s.gumroad.com/l/%s" % (sub, perm),
                        price="", query="lilypad:%s" % sub))
    return out


def keyword_products(kw):
    page = fetch("https://gumroad.com/discover?query=" + urllib.parse.quote(kw))
    if not page:
        return []
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
        url = ("https://%s.gumroad.com/l/%s" % (sub, d["permalink"])) if sub else \
              ("https://gumroad.com/l/%s" % d["permalink"])
        out.append(dict(name=d.get("name", "").strip(), seller=seller.get("name", "") or sub, url=url,
                        price=d.get("formatted_price") or "", query="bacon:%s" % kw))
    return out


def keywords_from(desc_cache, urls, limit):
    """Pick the capability words the market actually advertises, most common first."""
    counts = {}
    for u in urls:
        d = (desc_cache.get(u) or "").lower()
        for c in CAPS:
            if c in d:
                counts[c] = counts.get(c, 0) + 1
    picks = sorted(counts.items(), key=lambda kv: -kv[1])[:limit]
    return picks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sellers", type=int, default=30)
    ap.add_argument("--keywords", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=2.2)
    a = ap.parse_args()

    seed = json.load(open(SEED))
    known = {p["url"] for p in seed["all"]}
    desc = {}
    cache_path = "/opt/data/cache/scratch/gumroad_desc_all.json"
    if os.path.exists(cache_path):
        desc = json.load(open(cache_path))

    hops = []

    # ---- lilypad: sellers with the most tools first, that is where the catalogues are
    subs = {}
    for p in seed["tools"]:
        m = re.match(r"https://([a-z0-9-]+)\.gumroad\.com", p["url"])
        if m:
            subs.setdefault(m.group(1), 0)
            subs[m.group(1)] += 1
    sellers = [s for s, _ in sorted(subs.items(), key=lambda kv: -kv[1])][:a.sellers]
    print("lilypad: %d sellers" % len(sellers))
    for i, sub in enumerate(sellers):
        got = seller_products(sub)
        new = [g for g in got if g["url"] not in known]
        for g in new:
            known.add(g["url"])
            hops.append(g)
        print("  %-22s %2d on profile, %2d new" % (sub, len(got), len(new)))
        time.sleep(a.sleep)

    # ---- kevin bacon: search the operations the descriptions actually name
    picks = keywords_from(desc, [p["url"] for p in seed["tools"]], a.keywords)
    print("\nbacon: %d keyword hops -> %s" % (len(picks), [k for k, _ in picks[:8]]))
    for kw, n in picks:
        got = keyword_products(kw)
        new = [g for g in got if g["url"] not in known]
        for g in new:
            known.add(g["url"])
            hops.append(g)
        print("  %-18s (seen in %2d descriptions) -> %2d new" % (kw, n, len(new)))
        time.sleep(a.sleep)

    json.dump(dict(sellers=sellers, keywords=[k for k, _ in picks], hops=hops,
                   generated=time.strftime("%Y-%m-%d")), open(OUT, "w"), indent=1)
    print("\n%d new products via hops -> %s" % (len(hops), OUT))


if __name__ == "__main__":
    main()
