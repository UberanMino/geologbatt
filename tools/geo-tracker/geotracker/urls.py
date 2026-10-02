"""URL- und Domain-Normalisierung.

Die Domain ist die Analyse-Achse Nr. 1 der Citation-Auswertung — sie muss
deshalb stabil sein. `cited_url` bleibt roh, `cited_domain` wird normalisiert:

    https://WWW.LogBATT.de/lager/?utm_source=x  ->  logbatt.de
    https://shop.denios.de/artikel/123          ->  shop.denios.de

Subdomains werden NICHT zusammengefasst — "shop.denios.de wird zitiert, die
Hauptdomain nicht" ist eine Information, die wir nicht wegwerfen wollen. Für
die Zuordnung zu Marken/Regeln matchen wir per Suffix (siehe `domain_matches`).
"""

from __future__ import annotations

from urllib.parse import urlsplit


def normalize_domain(value: str) -> str:
    """Host aus einer URL (oder einer nackten Domain) in Normalform bringen."""
    if not value:
        return ""

    candidate = value.strip()
    if "//" not in candidate:
        # Nackte Domain oder "example.com/pfad": urlsplit braucht ein Schema,
        # sonst landet alles im Pfad.
        candidate = "//" + candidate

    host = urlsplit(candidate).hostname or ""
    host = host.strip().strip(".").lower()

    # IDN: einheitlich als Unicode ablegen, damit "xn--..." und "münchen.de"
    # im Ranking nicht als zwei Domains erscheinen.
    if host.startswith("xn--") or ".xn--" in host:
        try:
            host = host.encode("ascii").decode("idna")
        except (UnicodeError, UnicodeDecodeError):
            pass

    if host.startswith("www."):
        host = host[4:]

    return host


def domain_matches(host: str, pattern_domain: str) -> bool:
    """True, wenn `host` die Domain selbst oder eine Subdomain davon ist."""
    host = normalize_domain(host)
    pattern_domain = normalize_domain(pattern_domain)
    if not host or not pattern_domain:
        return False
    return host == pattern_domain or host.endswith("." + pattern_domain)


def clean_url(url: str) -> str:
    """URL für die Speicherung säubern — nur Whitespace, sonst nichts.

    Bewusst KEINE Parameter-Entfernung: `cited_url` ist Ebene-1-Rohdatum. Wenn
    eine Engine eine URL mit Tracking-Parametern zitiert, ist genau das die
    Wahrheit. Aufräumen passiert (falls überhaupt) im Auswertungs-Layer.
    """
    return (url or "").strip()
