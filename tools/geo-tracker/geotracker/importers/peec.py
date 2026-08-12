"""Import der bestehenden Peec-Chat-Exporte als Ebene-1-Läufe.

Warum: der eigene Tracker startet bei null. Im Repo liegen aber echte,
tagesgenaue Peec-Exporte (Volltext-Antworten + zitierte Domains über
4 Engines). Die hier zu importieren gibt dem Dashboard ab Tag 1 eine echte
Historie — und macht unsere Zahlen direkt gegen Peec prüfbar.

Ehrlichkeit über die Datenqualität, an drei Stellen im Schema markiert:

  * `runs.source = 'peec_import'` — jederzeit herausfilterbar, damit niemand
    Peec-Historie und eigene Scrapes unbemerkt vermischt.
  * `citations.url_known = 0` — Peec exportiert nur Domains, keine Pfade. Es
    werden KEINE URLs erfunden; die URL-Ansicht blendet diese Zeilen aus.
  * `evaluations.evaluator_version = 'peec-import'` — die Markennennungen und
    Positionen stammen aus Peecs eigener Auswertung, nicht von unserem
    Haiku-Layer. Ein `evaluate --re-run` überschreibt sie später sauber mit
    einer eigenen Auswertung (neue Zeile, alte bleibt stehen).
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ..classify import Classifier, register_domain
from ..db import utcnow
from ..urls import normalize_domain

# Peec-Modellnamen -> unsere Engine-Keys.
ENGINE_MAP = {
    "chatgpt-ui": "chatgpt",
    "perplexity-ui": "perplexity",
    "gemini-ui": "gemini",
    "google-ai-overview": "google_ai_overview",
}

_ENGINE_HEADING = re.compile(r"^###\s+.*\(`([a-z0-9-]+)`\)\s*$", re.MULTILINE)
_DETAILS = re.compile(r"<details><summary>(.*?)</summary>(.*?)</details>", re.DOTALL)
_SUMMARY = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s*[–-]\s*(?P<body>.*)$", re.DOTALL
)
_POSITION = re.compile(r"Position\s+(\d+)")
_MENTIONS = re.compile(r"Erwähnt:\s*(?P<list>.*)$", re.DOTALL)
_SOURCES = re.compile(r"^\*\*Quellen/Zitate:\*\*\s*(?P<list>.+)$", re.MULTILINE)
_TITLE = re.compile(r'^#\s+.*?„(?P<prompt>.+?)"', re.MULTILINE)


@dataclass
class ImportStats:
    prompts: int = 0
    runs: int = 0
    citations: int = 0
    evaluations: int = 0
    mentions: int = 0
    skipped: int = 0

    def merge(self, other: "ImportStats") -> None:
        for field in ("prompts", "runs", "citations", "evaluations", "mentions", "skipped"):
            setattr(self, field, getattr(self, field) + getattr(other, field))


def _prompt_text(markdown: str, path: Path) -> str:
    match = _TITLE.search(markdown)
    if match:
        return match.group("prompt").strip()
    # Fallback: Dateiname entslugen, damit ein Export ohne Titelzeile nicht
    # den ganzen Import blockiert.
    return path.stem.replace("-", " ").strip()


def _split_engines(markdown: str) -> list[tuple[str, str]]:
    """(peec_model, abschnitt) je Engine-Überschrift."""
    matches = list(_ENGINE_HEADING.finditer(markdown))
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((match.group(1), markdown[match.end() : end]))
    return sections


def _ensure_prompt(conn: sqlite3.Connection, text: str, category: str) -> tuple[int, bool]:
    row = conn.execute(
        "SELECT id FROM prompts WHERE text = ? AND country = 'DE' AND language = 'de'", (text,)
    ).fetchone()
    if row:
        return int(row["id"]), False
    cursor = conn.execute(
        """
        INSERT INTO prompts (text, category, country, language, engines, active, created_at)
        VALUES (?, ?, 'DE', 'de', ?, 1, ?)
        """,
        (text, category, json.dumps(list(ENGINE_MAP.values())), utcnow()),
    )
    return int(cursor.lastrowid), True


def _brand_id(conn: sqlite3.Connection, name: str, lookup: dict[str, int]) -> int:
    """Marke auflösen; unbekannte anlegen (offene Entdeckung, wie in Ebene 2)."""
    from ..evaluate.apply import normalize_brand  # lokal: Ebene 1 bleibt importfrei

    key = normalize_brand(name)
    if key in lookup:
        return lookup[key]
    cursor = conn.execute(
        """
        INSERT INTO brands (name, aliases, is_known, is_own_brand, is_competitor,
                            first_seen_at, notes)
        VALUES (?, '[]', 0, 0, 1, ?, 'Aus Peec-Import entdeckt.')
        """,
        (name.strip(), utcnow()),
    )
    brand_id = int(cursor.lastrowid)
    lookup[key] = brand_id
    return brand_id


def _brand_lookup(conn: sqlite3.Connection) -> dict[str, int]:
    from ..evaluate.apply import normalize_brand

    lookup: dict[str, int] = {}
    for row in conn.execute("SELECT id, name, aliases FROM brands"):
        for candidate in [row["name"], *json.loads(row["aliases"])]:
            key = normalize_brand(candidate)
            if key:
                lookup.setdefault(key, row["id"])
    return lookup


def import_file(
    conn: sqlite3.Connection,
    classifier: Classifier,
    path: Path,
    *,
    category: str = "Peec-Import",
) -> ImportStats:
    stats = ImportStats()
    markdown = path.read_text(encoding="utf-8")
    text = _prompt_text(markdown, path)

    prompt_id, created = _ensure_prompt(conn, text, category)
    stats.prompts += int(created)

    lookup = _brand_lookup(conn)
    own_brand = conn.execute(
        "SELECT id FROM brands WHERE is_own_brand = 1 ORDER BY id LIMIT 1"
    ).fetchone()
    own_brand_id = int(own_brand["id"]) if own_brand else None
    now = utcnow()

    for peec_model, section in _split_engines(markdown):
        engine = ENGINE_MAP.get(peec_model)
        if engine is None:
            continue

        for summary_raw, body in _DETAILS.findall(section):
            summary = _SUMMARY.match(summary_raw.strip())
            if not summary:
                stats.skipped += 1
                continue

            run_date = summary.group("date")
            headline = summary.group("body")

            # Doppelimport verhindern: derselbe Prompt/Engine/Tag aus derselben
            # Quelle wird nicht zweimal angelegt.
            if conn.execute(
                """
                SELECT 1 FROM runs
                 WHERE prompt_id = ? AND engine = ? AND run_date = ? AND source = 'peec_import'
                """,
                (prompt_id, engine, run_date),
            ).fetchone():
                stats.skipped += 1
                continue

            no_answer = "keine Antwort" in headline
            source_match = _SOURCES.search(body)
            answer = _SOURCES.sub("", body).strip()

            status = "deferred" if no_answer or not answer else "success"
            cursor = conn.execute(
                """
                INSERT INTO runs (prompt_id, engine, country, language, run_date, status,
                                  raw_response, source, requested_at, completed_at, attempts)
                VALUES (?, ?, 'DE', 'de', ?, ?, ?, 'peec_import', ?, ?, 1)
                """,
                (prompt_id, engine, run_date, status, answer or None, now, now),
            )
            run_id = int(cursor.lastrowid)
            stats.runs += 1

            # --- Citations: nur Domains, ehrlich markiert -------------------
            if source_match:
                domains = [d.strip() for d in source_match.group("list").split(",")]
                rank = 0
                seen: set[str] = set()
                for raw_domain in domains:
                    host = normalize_domain(raw_domain)
                    # Platzhalter aus dem Export („–", „keine") sind keine
                    # Domains. Ohne Punkt ist es keine Host-Angabe.
                    if not host or "." not in host or host in seen:
                        continue
                    seen.add(host)
                    rank += 1
                    source_type, is_known = register_domain(conn, classifier, host, now)
                    conn.execute(
                        """
                        INSERT INTO citations (
                            run_id, cited_url, cited_domain, title, snippet, citation_rank,
                            source_type, is_known, origin, provider_source, provider_index,
                            ref_id, published_date, raw_json, created_at, url_known
                        ) VALUES (?, '', ?, NULL, NULL, ?, ?, ?, 'cited', 'peec', ?, NULL, NULL, ?, ?, 0)
                        """,
                        (
                            run_id, host, rank, source_type, int(is_known), rank,
                            json.dumps({"peec_domain": raw_domain.strip()}, ensure_ascii=False),
                            now,
                        ),
                    )
                    stats.citations += 1

            # --- Peecs eigene Auswertung übernehmen ------------------------
            if no_answer:
                continue

            mention_match = _MENTIONS.search(headline)
            names: list[str] = []
            if mention_match:
                raw_list = mention_match.group("list").strip()
                if raw_list and raw_list != "–":
                    names = [n.strip() for n in raw_list.split(",") if n.strip()]

            position_match = _POSITION.search(headline)
            mentioned = "✅" in headline
            position = int(position_match.group(1)) if position_match else None
            share = (1.0 / len(names)) if (mentioned and names) else 0.0

            evaluation = conn.execute(
                """
                INSERT INTO evaluations (
                    run_id, logbatt_mentioned, logbatt_position, sentiment,
                    problem_narrative_anchored, share_of_voice, raw_classifier_output,
                    evaluator_version, model, is_current, created_at
                ) VALUES (?, ?, ?, NULL, NULL, ?, ?, 'peec-import', NULL, 1, ?)
                """,
                (
                    run_id, int(mentioned), position, share,
                    json.dumps({"peec_summary": summary_raw.strip()}, ensure_ascii=False),
                    now,
                ),
            )
            evaluation_id = int(evaluation.lastrowid)
            stats.evaluations += 1

            used: set[int] = set()
            rank = 0
            for name in names:
                brand_id = _brand_id(conn, name, lookup)
                if brand_id in used:
                    continue
                used.add(brand_id)
                rank += 1
                conn.execute(
                    """
                    INSERT INTO brand_mentions (run_id, evaluation_id, brand_id, mention_rank, mention_text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (run_id, evaluation_id, brand_id, rank, name),
                )
                stats.mentions += 1

            # Peec liefert die Position separat; wenn sie von der Reihenfolge
            # abweicht, gewinnt Peecs Angabe — sie ist hier die Quelle.
            if own_brand_id is not None and position is None and mentioned:
                derived = conn.execute(
                    "SELECT mention_rank FROM brand_mentions WHERE evaluation_id = ? AND brand_id = ?",
                    (evaluation_id, own_brand_id),
                ).fetchone()
                if derived:
                    conn.execute(
                        "UPDATE evaluations SET logbatt_position = ? WHERE id = ?",
                        (derived["mention_rank"], evaluation_id),
                    )

    conn.commit()
    return stats


def import_directory(
    conn: sqlite3.Connection, classifier: Classifier, directory: Path, *, category: str
) -> ImportStats:
    total = ImportStats()
    for path in sorted(directory.glob("*.md")):
        total.merge(import_file(conn, classifier, path, category=category))
    return total
