"""Seed-Daten einlesen und idempotent in die DB schreiben.

Idempotent heißt: `geotracker seed` darf beliebig oft laufen. Vorhandene Zeilen
werden aktualisiert, nie gelöscht — insbesondere werden Brands/Domains, die der
Auswertungs-Layer per offener Entdeckung angelegt hat, nicht angefasst.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

from .classify import Classifier
from .config import PACKAGE_DIR
from .db import utcnow
from .urls import normalize_domain

SEEDS_DIR = PACKAGE_DIR / "seeds"


def _read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_classifier(conn: sqlite3.Connection, seeds_dir: Path | None = None) -> Classifier:
    """Classifier inkl. der Regex-Muster aus domains.yaml."""
    data = _read_yaml((seeds_dir or SEEDS_DIR) / "domains.yaml")
    return Classifier.from_db(conn, extra_patterns=data.get("earned_media_patterns") or [])


def seed_brands(conn: sqlite3.Connection, seeds_dir: Path | None = None) -> dict[str, int]:
    data = _read_yaml((seeds_dir or SEEDS_DIR) / "brands.yaml")
    now = utcnow()
    inserted = updated = domains = 0

    entries: list[tuple[dict[str, Any], bool]] = [
        (entry, True) for entry in (data.get("brands") or [])
    ] + [(entry, False) for entry in (data.get("partners") or [])]

    for entry, is_competitor in entries:
        name = entry["name"]
        aliases = json.dumps(entry.get("aliases") or [], ensure_ascii=False)
        is_own = int(bool(entry.get("is_own_brand")))

        row = conn.execute("SELECT id FROM brands WHERE name = ?", (name,)).fetchone()
        if row is None:
            cursor = conn.execute(
                """
                INSERT INTO brands (name, aliases, is_known, is_own_brand, is_competitor,
                                    first_seen_at, notes)
                VALUES (?, ?, 1, ?, ?, ?, ?)
                """,
                (name, aliases, is_own, int(is_competitor), now, entry.get("notes")),
            )
            brand_id = int(cursor.lastrowid)
            inserted += 1
        else:
            brand_id = int(row["id"])
            # is_known/first_seen_at bleiben: eine von Ebene 2 entdeckte Marke,
            # die wir später seeden, wird dadurch zur bekannten Marke — aber
            # ihr erstes Auftreten bleibt erhalten.
            conn.execute(
                """
                UPDATE brands
                   SET aliases = ?, is_known = 1, is_own_brand = ?, is_competitor = ?
                 WHERE id = ?
                """,
                (aliases, is_own, int(is_competitor), brand_id),
            )
            updated += 1

        for raw_domain in entry.get("domains") or []:
            host = normalize_domain(raw_domain)
            if not host:
                continue
            conn.execute(
                """
                INSERT INTO brand_domains (brand_id, domain) VALUES (?, ?)
                ON CONFLICT (domain) DO UPDATE SET brand_id = excluded.brand_id
                """,
                (brand_id, host),
            )
            domains += 1

    conn.commit()
    return {"brands_inserted": inserted, "brands_updated": updated, "brand_domains": domains}


def seed_domains(conn: sqlite3.Connection, seeds_dir: Path | None = None) -> dict[str, int]:
    """owned- und earned_media-Domains ins Register schreiben.

    Wettbewerber-Domains kommen aus brand_domains und müssen hier nicht doppelt
    gepflegt werden — sie werden beim ersten Zitat automatisch registriert.
    """
    data = _read_yaml((seeds_dir or SEEDS_DIR) / "domains.yaml")
    now = utcnow()
    counts = {"owned": 0, "earned_media": 0}

    for source_type, key in (("owned", "owned"), ("earned_media", "earned_media")):
        for raw_domain in data.get(key) or []:
            host = normalize_domain(raw_domain)
            if not host:
                continue
            brand_row = conn.execute(
                "SELECT brand_id FROM brand_domains WHERE domain = ?", (host,)
            ).fetchone()
            brand_id = brand_row["brand_id"] if brand_row else None
            conn.execute(
                """
                INSERT INTO domains (domain, source_type, is_known, classified_by, brand_id,
                                     first_seen_at)
                VALUES (?, ?, 1, 'seed', ?, ?)
                ON CONFLICT (domain) DO UPDATE
                    SET source_type   = excluded.source_type,
                        is_known      = 1,
                        classified_by = 'seed',
                        brand_id      = excluded.brand_id
                    WHERE domains.classified_by != 'manual'
                """,
                (host, source_type, brand_id, now),
            )
            counts[source_type] += 1

    conn.commit()
    return {f"domains_{k}": v for k, v in counts.items()}


def seed_prompts(conn: sqlite3.Connection, seeds_dir: Path | None = None) -> dict[str, int]:
    data = _read_yaml((seeds_dir or SEEDS_DIR) / "prompts.yaml")
    defaults = data.get("defaults") or {}
    now = utcnow()
    inserted = updated = 0

    for entry in data.get("prompts") or []:
        text = entry["text"].strip()
        category = entry.get("category") or defaults.get("category") or "Ohne Kategorie"
        country = (entry.get("country") or defaults.get("country") or "DE").upper()
        language = (entry.get("language") or defaults.get("language") or "de").lower()
        engines = json.dumps(
            entry.get("engines") or defaults.get("engines") or ["chatgpt"], ensure_ascii=False
        )
        active = int(bool(entry.get("active", defaults.get("active", True))))

        row = conn.execute(
            "SELECT id FROM prompts WHERE text = ? AND country = ? AND language = ?",
            (text, country, language),
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO prompts (text, category, country, language, engines, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (text, category, country, language, engines, active, now),
            )
            inserted += 1
        else:
            # `active` wird bewusst NICHT überschrieben: wenn jemand einen
            # Prompt im Betrieb deaktiviert, darf ein Re-Seed ihn nicht
            # wiederbeleben.
            conn.execute(
                "UPDATE prompts SET category = ?, engines = ? WHERE id = ?",
                (category, engines, row["id"]),
            )
            updated += 1

    conn.commit()
    return {"prompts_inserted": inserted, "prompts_updated": updated}


def seed_all(conn: sqlite3.Connection, seeds_dir: Path | None = None) -> dict[str, int]:
    result: dict[str, int] = {}
    result.update(seed_brands(conn, seeds_dir))
    result.update(seed_domains(conn, seeds_dir))
    result.update(seed_prompts(conn, seeds_dir))
    return result
