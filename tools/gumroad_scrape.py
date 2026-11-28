"""gumroad_scrape — pull Roblox-tool listings off Gumroad search and keep the receipts.

Every row keeps its source URL, so the compiled document is citable rather than "things I remember".
Gumroad's discover page is React with an HTML-escaped JSON blob containing a `products` array; there is
no public search API, so the parse is: unescape, find `"products":`, bracket-match, json.loads.

    python3 gumroad_scrape.py --out /opt/data/cache/scratch/gumroad.json
"""

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
QUERIES = [
    "roblox plugin", "roblox rig", "roblox animation", "roblox studio",
    "roblox vfx", "roblox ui", "roblox game system", "roblox builder",
    "roblox script", "roblox model", "r15 rig", "roblox avatar",
]


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def _blob(text):
    """Extract the biggest JSON object that contains a products array."""
    for key in ('"products":'):
        i = text.find(key)
        if i < 0:
            continue
        start = text.rfind("{", 0, i)
        depth, j = 0, start
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    return text[start:j + 1]
            j += 1
    return None


def products_from(page, query):
    text = html.unescape(page)
    out = []
    blob = _blob(text)
    items = []
    if blob:
        try:
            items = json.loads(blob).get("products") or []
        except Exception:
            items = []
    if not items:
        # fall back to bracket-matching the array itself
        i = text.find('"products":')
        if i >= 0:
            j = text.find("[", i)
            depth, k = 0, j
            while k < len(text):
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
                items = []
    for d in items:
        if "permalink" not in d or "name" not in d:
            continue
        seller = (d.get("seller") or {})
        sub = ""
        pu = seller.get("profile_url") or ""
        m = re.match(r"https://([a-z0-9-]+)\.gumroad\.com", pu)
        if m:
            sub = m.group(1)
        url = "https://%s.gumroad.com/l/%s" % (sub, d["permalink"]) if sub else \
              "https://gumroad.com/l/%s" % d["permalink"]
        out.append(dict(
            name=d.get("name", "").strip(),
            seller=seller.get("name", "").strip(),
            url=url,
            price=d.get("formatted_price") or (
                "%.2f" % (d.get("price_cents", 0) / 100.0) if d.get("price_cents") else ""),
            currency=d.get("currency_code", ""),
            query=query,
            ratings=d.get("ratings_count"),
            sales=d.get("sales_count"),
        ))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/opt/data/cache/scratch/gumroad.json")
    ap.add_argument("--queries", default="")
    a = ap.parse_args()
    queries = [q.strip() for q in a.queries.split("|") if q.strip()] or QUERIES

    rows, seen = [], set()
    for q in queries:
        url = "https://gumroad.com/discover?query=" + urllib.parse.quote(q)
        try:
            page = fetch(url)
        except Exception as e:
            print("FAIL %-22s %s" % (q, e))
            continue
        got = products_from(page, q)
        new = 0
        for r in got:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            rows.append(r)
            new += 1
        print("%-22s %3d products, %3d new" % (q, len(got), new))
        time.sleep(1.0)

    # Roblox-relevance filter: the search is fuzzy and returns 3D-general assets too
    kw = ("roblox", "r15", "r6", "blocky", "avatar", "studio", "obby", "luau")
    keep = []
    for r in rows:
        hay = (r["name"] + " " + r["url"]).lower()
        if any(k in hay for k in kw):
            keep.append(r)
    print("\nkept %d of %d (rob-test on name/url)" % (len(keep), len(rows)))
    with open(a.out, "w") as fh:
        json.dump(dict(queries=queries, products=keep, all=rows), fh, indent=1)
    print("wrote", a.out)
    for r in keep[:40]:
        print("  %-52s %-18s %8s  %s" % (r["name"][:52], r["seller"][:18], r["price"], r["url"]))


if __name__ == "__main__":
    main()
