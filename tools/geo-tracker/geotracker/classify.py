"""source_type-Klassifikation der zitierten Domains (Ebene 1, regelbasiert).

Wichtig: das hier ist KEINE KI-Auswertung. Die Zuordnung ist deterministisch
und regelbasiert, damit Ebene 1 vollständig ohne Ebene 2 funktioniert. Der
Auswertungs-Layer (Haiku) darf die Einordnung später verfeinern — er ist aber
nie Voraussetzung dafür, dass eine Citation gespeichert wird.

Prioritätsreihenfolge (erste Regel gewinnt):
    owned         -> eigene Domains (logbatt.de/.com)
    competitor    -> Domain gehört einer Brand aus brands.yaml
    earned_media  -> Foren/Vergleichs-/Referenzseiten aus domains.yaml
    other         -> alles Übrige (= "neu entdeckt", bis jemand einsortiert)
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field

from .urls import domain_matches, normalize_domain

SOURCE_TYPES = ("owned", "competitor", "earned_media", "other")


@dataclass
class Classifier:
    """Regelsatz, einmal aus der DB geladen und dann in-memory angewandt."""

    owned: list[str] = field(default_factory=list)
    # domain -> brand_id
    brand_domains: dict[str, int] = field(default_factory=dict)
    earned_media: list[str] = field(default_factory=list)
    earned_media_patterns: list[re.Pattern[str]] = field(default_factory=list)

    @classmethod
    def from_db(cls, conn: sqlite3.Connection, extra_patterns: list[str] | None = None) -> "Classifier":
        owned = [
            row["domain"]
            for row in conn.execute(
                """
                SELECT bd.domain FROM brand_domains bd
                JOIN brands b ON b.id = bd.brand_id
                WHERE b.is_own_brand = 1
                """
            )
        ]
        brand_domains = {
            row["domain"]: row["brand_id"]
            for row in conn.execute("SELECT domain, brand_id FROM brand_domains")
        }
        earned = [
            row["domain"]
            for row in conn.execute(
                "SELECT domain FROM domains WHERE source_type = 'earned_media' AND classified_by = 'seed'"
            )
        ]
        patterns = [re.compile(p, re.IGNORECASE) for p in (extra_patterns or [])]
        return cls(
            owned=owned,
            brand_domains=brand_domains,
            earned_media=earned,
            earned_media_patterns=patterns,
        )

    def classify(self, host: str) -> tuple[str, int | None]:
        """(source_type, brand_id) für einen normalisierten Host."""
        host = normalize_domain(host)
        if not host:
            return "other", None

        for owned in self.owned:
            if domain_matches(host, owned):
                brand_id = self._brand_for(host)
                return "owned", brand_id

        brand_id = self._brand_for(host)
        if brand_id is not None:
            return "competitor", brand_id

        for domain in self.earned_media:
            if domain_matches(host, domain):
                return "earned_media", None

        for pattern in self.earned_media_patterns:
            if pattern.search(host):
                return "earned_media", None

        return "other", None

    def _brand_for(self, host: str) -> int | None:
        """Längster passender Domain-Match gewinnt (spezifischer schlägt allgemein)."""
        best: tuple[int, int] | None = None  # (länge, brand_id)
        for domain, brand_id in self.brand_domains.items():
            if domain_matches(host, domain) and (best is None or len(domain) > best[0]):
                best = (len(domain), brand_id)
        return best[1] if best else None


def register_domain(
    conn: sqlite3.Connection,
    classifier: Classifier,
    host: str,
    seen_at: str,
) -> tuple[str, bool]:
    """Domain im Register anlegen/auffrischen. Gibt (source_type, is_known) zurück.

    Das ist die "offene Entdeckung" für Domains: jede zitierte Domain bekommt
    eine Zeile, auch eine wildfremde. Bereits manuell eingeordnete Domains
    (classified_by = 'manual') werden NICHT überschrieben.
    """
    host = normalize_domain(host)
    if not host:
        return "other", False

    row = conn.execute(
        "SELECT source_type, is_known, classified_by FROM domains WHERE domain = ?", (host,)
    ).fetchone()

    if row is not None:
        conn.execute("UPDATE domains SET last_seen_at = ? WHERE domain = ?", (seen_at, host))
        return row["source_type"], bool(row["is_known"])

    source_type, brand_id = classifier.classify(host)
    # is_known = "wir wussten vorher, was das ist" — also alles außer 'other'.
    is_known = source_type != "other"
    conn.execute(
        """
        INSERT INTO domains (domain, source_type, is_known, classified_by, brand_id,
                             first_seen_at, last_seen_at)
        VALUES (?, ?, ?, 'auto', ?, ?, ?)
        """,
        (host, source_type, int(is_known), brand_id, seen_at, seen_at),
    )
    return source_type, is_known


def reclassify_all(conn: sqlite3.Connection, classifier: Classifier) -> dict[str, int]:
    """Alle Domains + Citations neu klassifizieren, ohne erneut zu scrapen.

    Nötig, sobald sich brands.yaml/domains.yaml ändern. Manuelle Einordnungen
    (classified_by = 'manual') bleiben unangetastet.
    """
    changed_domains = 0
    for row in conn.execute(
        "SELECT id, domain, source_type, is_known FROM domains WHERE classified_by != 'manual'"
    ).fetchall():
        source_type, brand_id = classifier.classify(row["domain"])
        is_known = source_type != "other"
        if source_type != row["source_type"] or int(is_known) != row["is_known"]:
            conn.execute(
                "UPDATE domains SET source_type = ?, is_known = ?, brand_id = ? WHERE id = ?",
                (source_type, int(is_known), brand_id, row["id"]),
            )
            changed_domains += 1

    # Denormalisierte Kopie in citations nachziehen.
    cursor = conn.execute(
        """
        UPDATE citations
           SET source_type = (SELECT d.source_type FROM domains d WHERE d.domain = citations.cited_domain),
               is_known    = (SELECT d.is_known    FROM domains d WHERE d.domain = citations.cited_domain)
         WHERE EXISTS (SELECT 1 FROM domains d WHERE d.domain = citations.cited_domain)
        """
    )
    conn.commit()
    return {"domains_changed": changed_domains, "citations_touched": cursor.rowcount}
