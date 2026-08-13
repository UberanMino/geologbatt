"""Domain- und URL-Typen — die zweite Klassifikationsachse.

`source_type` (owned/competitor/earned_media/other) beantwortet "wem gehört
das?" und ist die Handlungsachse. `domain_type` beantwortet "was für eine Art
Quelle ist das?" — dieselbe Trennung, die Peec fährt. Beide sind unabhängig
und werden getrennt gespeichert:

    logbatt.de        source_type=owned       domain_type=you
    denios.de         source_type=competitor  domain_type=competitor
    reddit.com        source_type=earned_media domain_type=ugc
    umweltbundesamt.de source_type=earned_media domain_type=institutional

Beides ist regelbasiert und jederzeit neu berechenbar (`geotracker retype`) —
ohne erneutes Scrapen und ohne Modellaufruf.
"""

from __future__ import annotations

import re
import sqlite3
from urllib.parse import urlsplit

from .urls import domain_matches, normalize_domain

DOMAIN_TYPES = (
    "you", "competitor", "corporate", "institutional",
    "ugc", "editorial", "reference", "marketplace", "other",
)

URL_TYPES = (
    "homepage", "product_page", "category_page", "article",
    "how_to", "listicle", "profile", "other", "unknown",
)

# Reihenfolge = Priorität. Erste passende Regel gewinnt.
_DOMAIN_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("ugc", (
        "reddit.com", "quora.com", "youtube.com", "facebook.com", "instagram.com",
        "linkedin.com", "x.com", "twitter.com", "tiktok.com", "gutefrage.net",
        "motor-talk.de", "stackexchange.com", "stackoverflow.com", "pinterest.com",
    )),
    ("reference", ("wikipedia.org", "wikimedia.org", "wikidata.org", "dict.cc")),
    ("institutional", (
        "umweltbundesamt.de", "bam.de", "dguv.de", "bgetem.de", "vde.com", "vci.de",
        "bmuv.de", "bund.de", "europa.eu", "gov.uk", "bfs.de", "baua.de", "bgrci.de",
        "din.de", "unece.org", "destatis.de", "bundesanzeiger.de",
    )),
    ("marketplace", (
        "wlw.de", "europages.de", "europages.com", "kompass.com", "industrystock.de",
        "exportpages.de", "gelbeseiten.de", "dastelefonbuch.de", "bundes-telefonbuch.de",
        "trustpilot.com", "provenexpert.com", "amazon.de", "ebay.de", "alibaba.com",
        "kaiserkraft.de", "mercateo.com", "conrad.de",
    )),
]

_INSTITUTIONAL_PATTERNS = (
    re.compile(r"(^|\.)ihk[-.]"),
    re.compile(r"(^|\.)(bund|bmwk|bmuv)\.de$"),
    re.compile(r"\.gov(\.[a-z]{2})?$"),
    re.compile(r"\.gv\.at$"),
    re.compile(r"(^|\.)(tuv|tuev|dekra)"),
)

_EDITORIAL_PATTERNS = (
    re.compile(r"(magazin|magazine|zeitung|news|presse|blog|journal|report)"),
)

_URL_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("how_to", ("/guide", "/anleitung", "/how-to", "/howto", "/ratgeber", "/wissen",
                "/lexikon", "/glossar", "/faq", "/tipps", "/schulung")),
    ("listicle", ("/beste", "/best-", "/top-", "/vergleich", "/test", "/ranking")),
    ("article", ("/blog", "/news", "/magazin", "/artikel", "/aktuelles", "/presse",
                 "/stories", "/insights")),
    ("profile", ("/ueber-uns", "/about", "/unternehmen", "/company", "/profil",
                 "/kontakt", "/impressum", "/team")),
    ("category_page", ("/kategorie", "/category", "/collections", "/sortiment",
                       "/produkte", "/products", "/shop")),
    ("product_page", ("/produkt", "/product", "/artikel-", "/p/", "/item/")),
]


def classify_domain_type(
    host: str, *, source_type: str, is_brand_domain: bool = False
) -> str:
    """Art der Quelle. `source_type` hat Vorrang, wo er eindeutig ist."""
    host = normalize_domain(host)
    if not host:
        return "other"

    # Besitz schlägt Art: die eigene Domain ist "you", eine Wettbewerber-Domain
    # ist "competitor" — auch wenn sie technisch ein Corporate-Auftritt ist.
    if source_type == "owned":
        return "you"
    if source_type == "competitor" or is_brand_domain:
        return "competitor"

    for domain_type, domains in _DOMAIN_RULES:
        if any(domain_matches(host, d) for d in domains):
            return domain_type

    if any(p.search(host) for p in _INSTITUTIONAL_PATTERNS):
        return "institutional"
    if any(p.search(host) for p in _EDITORIAL_PATTERNS):
        return "editorial"

    # Konservativer Default: ein Firmenauftritt ist die häufigste Quelle.
    return "corporate"


def classify_url_type(url: str, *, url_known: bool = True) -> str:
    """Art der Seite aus dem Pfad. Ohne echte URL ehrlich 'unknown'."""
    if not url_known or not url:
        return "unknown"

    path = (urlsplit(url).path or "/").lower().rstrip("/")
    if not path:
        return "homepage"

    for url_type, needles in _URL_RULES:
        if any(needle in path for needle in needles):
            return url_type

    # Tiefe Pfade mit sprechendem Slug sind meist Produkt-/Detailseiten.
    segments = [s for s in path.split("/") if s]
    if len(segments) >= 2:
        return "product_page"
    return "other"


def retype(conn: sqlite3.Connection) -> dict[str, int]:
    """domain_type und url_type für den gesamten Bestand neu berechnen."""
    brand_domains = {
        row["domain"] for row in conn.execute("SELECT domain FROM brand_domains")
    }

    domains_changed = 0
    for row in conn.execute("SELECT id, domain, source_type, domain_type FROM domains").fetchall():
        is_brand = any(domain_matches(row["domain"], d) for d in brand_domains)
        new_type = classify_domain_type(
            row["domain"], source_type=row["source_type"], is_brand_domain=is_brand
        )
        if new_type != row["domain_type"]:
            conn.execute(
                "UPDATE domains SET domain_type = ? WHERE id = ?", (new_type, row["id"])
            )
            domains_changed += 1

    urls_changed = 0
    for row in conn.execute(
        "SELECT id, cited_url, url_known, url_type FROM citations"
    ).fetchall():
        new_type = classify_url_type(row["cited_url"], url_known=bool(row["url_known"]))
        if new_type != row["url_type"]:
            conn.execute(
                "UPDATE citations SET url_type = ? WHERE id = ?", (new_type, row["id"])
            )
            urls_changed += 1

    conn.commit()
    return {"domain_types_changed": domains_changed, "url_types_changed": urls_changed}
