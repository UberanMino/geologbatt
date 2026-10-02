#!/usr/bin/env python3
"""Compare a page file in this repo with the live page on the website.

Purpose: before changing a page, make sure the repo file still matches what
is live (headings, carousel, product titles, images, internal links). If the
page was changed in the WordPress editor in the meantime, the diff shows it,
and the current editor code has to be fetched first. Nothing is rebuilt from
the front end.

Usage:
    python3 tools/live-diff.py optimized/en/transport-crates.html
    python3 tools/live-diff.py optimized/en/transport-crates.html https://www.logbatt.com/transport-crates/

Without a URL, the URL is derived from the path (see DOMAINS). Exit code 0 =
no differences, 1 = differences found, 2 = error.
Stdlib only, no extra packages needed.
"""
import html
import os
import re
import ssl
import sys
import urllib.request
from html.parser import HTMLParser

DOMAINS = {
    "de": "https://www.logbatt.de", "en": "https://www.logbatt.com", "nl": "https://www.logbatt.nl",
    "dk": "https://www.logbatt.dk", "no": "https://www.logbatt.no", "it": "https://www.logbatt.it",
    "es": "https://www.logbatt.es", "fr": "https://www.logbatt.fr", "fi": "https://www.logbatt.fi",
    "se": "https://www.logbatt.se", "sv": "https://www.logbatt.se", "pt": "https://www.logbatt.pt",
    "pl": "https://www.logbatt.pl", "cz": "https://www.logbatt.cz", "hu": "https://www.logbatt.hu",
}


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headings, self.links, self.images = [], set(), set()
        self._h, self._buf = None, []
        self._skip = 0  # inside <header>/<footer>/<nav>/<script>/<style> (theme parts, not content)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("header", "footer", "nav", "script", "style", "noscript"):
            self._skip += 1
        if self._skip:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self._h, self._buf = tag, []
        elif tag == "a" and a.get("href"):
            self.links.add(a["href"].split("?")[0])
        elif tag == "img" and a.get("src"):
            self.images.add(os.path.basename(a["src"].split("?")[0]))

    def handle_endtag(self, tag):
        if tag in ("header", "footer", "nav", "script", "style", "noscript") and self._skip:
            self._skip -= 1
            return
        if self._skip:
            return
        if tag == self._h:
            txt = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if txt:
                self.headings.append(f"{tag}: {txt}")
            self._h = None

    def handle_data(self, data):
        if self._h and not self._skip:
            self._buf.append(data)


def norm(s):
    s = html.unescape(s).replace("’", "'").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def content_part(page):
    """Live page: only the post content (entry-content up to the footer), without menu/header."""
    i = page.find('class="entry-content')
    if i < 0:
        i = page.find("<main")
    start = page.rfind("<", 0, i) if i > 0 else 0
    j = page.find("<footer", start)
    return page[start: j if j > 0 else len(page)]


def features(src, live):
    p = Extract()
    p.feed(content_part(src) if live else src)
    if live:
        carousels = src.count("wp-block-rh-block-splide")
        slides = re.findall(r'splide__slide.*?<strong>([^<]+)</strong>', content_part(src), re.S)
    else:
        carousels = src.count("<!-- wp:rh/block-splide")
        slides = re.findall(r'"splide__slide".*?<strong>([^<]+)</strong>', src, re.S)
    imgs = {re.sub(r"(-\d+x\d+)?\.(png|jpe?g|webp)(\.webp)?$", "", i) for i in p.images}
    return {
        "headings": [norm(h) for h in p.headings],
        "carousels": carousels,
        "slides": sorted(set(norm(s) for s in slides)),
        "images": imgs,
        "links": {l for l in p.links if l.startswith("http") and "logbatt" in l and "wp-content" not in l},
    }


def fetch(url):
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not cafile and os.path.exists("/root/.ccr/ca-bundle.crt"):
        cafile = "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (live-diff)", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")


def derive_url(path):
    parts = os.path.normpath(path).split(os.sep)
    if "optimized" not in parts and "website" not in parts:
        raise SystemExit("Cannot derive URL from path – please pass the URL as the 2nd argument.")
    k = parts.index("optimized") if "optimized" in parts else parts.index("website")
    lang, rest = parts[k + 1], parts[k + 2:]
    slug = "/".join(rest)[:-5]  # strip .html
    return f"{DOMAINS[lang]}/{slug}/"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else derive_url(path)
    repo = features(open(path, encoding="utf-8").read(), live=False)
    try:
        live_raw = fetch(url)
        live = features(live_raw, live=True)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR loading {url}: {e}")
        return 2

    print(f"Repo: {path}\nLive: {url}\n")
    diffs = 0
    if repo["carousels"] != live["carousels"]:
        diffs += 1
        print(f"!! Product carousels: repo {repo['carousels']} vs. live {live['carousels']}")
    only_live = [h for h in live["headings"] if h not in repo["headings"]]
    only_repo = [h for h in repo["headings"] if h not in live["headings"]]
    for label, items in (("Headings only LIVE (missing in repo)", only_live),
                         ("Headings only in REPO (not live)", only_repo),
                         ("Carousel titles only LIVE", sorted(set(live["slides"]) - set(repo["slides"]))),
                         ("Carousel titles only in REPO", sorted(set(repo["slides"]) - set(live["slides"]))),
                         ("Images only LIVE", sorted(live["images"] - repo["images"])),
                         ("Images only in REPO", sorted(i for i in repo["images"] - live["images"]
                                                        if i not in live_raw)),
                         ("Links only LIVE", sorted(live["links"] - repo["links"])),
                         ("Links only in REPO", sorted(repo["links"] - live["links"]))):
        if items:
            diffs += 1
            print(f"!! {label}:")
            for i in items[:25]:
                print(f"     {i}")
    if not diffs:
        print("OK – repo file and live page match (headings, carousel, images, links).")
        return 0
    print("\n=> Differences found. If the live page is newer: fetch the current editor code first "
          "(WordPress code editor) and store it in the repo, then make the change there.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
