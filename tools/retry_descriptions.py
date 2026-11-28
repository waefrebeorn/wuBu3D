"""retry_descriptions — refetch only the Gumroad pages that failed, slowly.

The first pass fired 438 requests in a couple of minutes and Gumroad answered with HTTPError (429/403)
for 371 of them. The fix is not a clever header, it is patience: spaced requests, a couple of tries,
and a checkpoint so a long run can be resumed.
"""

import json
import random
import re
import time
import urllib.request

CACHE = "/opt/data/cache/scratch/gumroad_desc_all.json"
UAS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36 Edg/120",
]


def grab(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": random.choice(UAS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            })
            page = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
            m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]{5,400})"', page, re.I) or \
                re.search(r'<meta[^>]+property="og:description"[^>]+content="([^"]{5,400})"', page, re.I)
            if m:
                return re.sub(r"\s+", " ", m.group(1)).strip().replace("|", "\\|")
            return "_no description in metadata_"
        except Exception as e:
            if attempt == 2:
                return "_page unavailable (%s)_" % type(e).__name__
            time.sleep(4.0 + attempt * 4.0)
    return "_page unavailable_"


def main():
    cache = json.load(open(CACHE))
    todo = [k for k, v in cache.items() if "unavailable" in v]
    print("retrying %d" % len(todo))
    for i, url in enumerate(todo):
        cache[url] = grab(url)
        if i % 20 == 0:
            json.dump(cache, open(CACHE, "w"))
            print("  %d/%d  ok so far %d" % (i, len(todo),
                                             sum(1 for k in todo[:i] if "unavailable" not in cache[k])))
        time.sleep(2.0 + random.random() * 1.5)
    json.dump(cache, open(CACHE, "w"))
    good = sum(1 for v in cache.values() if "unavailable" not in v)
    print("done: %d/%d have a description" % (good, len(cache)))


if __name__ == "__main__":
    main()
