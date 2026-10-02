"""Ebene 2 — Modellausgabe auf gespeicherte Rohdaten anwenden.

Arbeitsteilung, bewusst gezogen:

  Das Modell liefert nur, wofür man Sprachverständnis braucht — welche Marken
  im Text vorkommen und in welcher Reihenfolge, das Sentiment, die
  Narrativ-Verankerung.

  Alles Ableitbare rechnen wir hier deterministisch: mention_rank,
  logbatt_position und share_of_voice folgen zwingend aus der Markenliste.
  Ein Modell rechnen zu lassen, was Arithmetik ist, wäre eine vermeidbare
  Fehlerquelle — und die Werte sollen bei gleichem Rohtext reproduzierbar sein.
  Die rohe Modellantwort wird trotzdem vollständig gespeichert
  (evaluations.raw_classifier_output), inklusive der Felder, die wir überschreiben.

Wiederholbarkeit: jeder Auswertungslauf legt eine NEUE evaluations-Zeile an und
setzt is_current der vorherigen auf 0. Nichts wird gelöscht.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any

from ..db import utcnow
from .prompt import EVALUATOR_VERSION, OWN_BRAND

# Rechtsformen und Zusätze, die beim Abgleich ignoriert werden. "Zarges GmbH",
# "ZARGES" und "Zarges Aluminium" sollen dieselbe Marke treffen.
_LEGAL_SUFFIXES = (
    "gmbh & co. kg", "gmbh & co kg", "gmbh und co kg", "ag & co kg",
    "gmbh", "mbh", "ag", "se", "kg", "ohg", "e.k.", "ek", "b.v.", "bv",
    "n.v.", "nv", "ltd", "ltd.", "limited", "inc", "inc.", "llc", "plc",
    "s.a.", "sa", "srl", "s.r.l.", "oy", "ab", "as", "a/s", "sp. z o.o.",
)

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE = re.compile(r"\s+")


def normalize_brand(name: str) -> str:
    """Vergleichsform eines Markennamens.

    Kleinschreibung, Umlaut-Normalisierung, Rechtsform und Satzzeichen weg,
    Leerzeichen weg. "Bauer Südlohn GmbH" und "bauer-suedlohn" treffen sich.
    """
    value = (name or "").strip().lower()
    if not value:
        return ""

    for umlaut, replacement in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        value = value.replace(umlaut, replacement)

    value = _PUNCT.sub(" ", value)
    value = _SPACE.sub(" ", value).strip()

    # Rechtsform am Ende abschneiden (längster Treffer zuerst).
    for suffix in sorted(_LEGAL_SUFFIXES, key=len, reverse=True):
        normalized_suffix = _PUNCT.sub(" ", suffix)
        normalized_suffix = _SPACE.sub(" ", normalized_suffix).strip()
        if normalized_suffix and value.endswith(" " + normalized_suffix):
            value = value[: -len(normalized_suffix) - 1].strip()
            break

    return value.replace(" ", "")


@dataclass
class AppliedEvaluation:
    run_id: int
    evaluation_id: int
    logbatt_mentioned: bool
    logbatt_position: int | None
    sentiment: str | None
    problem_narrative_anchored: bool
    share_of_voice: float
    mentions: int
    new_brands: list[str]
    warnings: list[str]


class BrandResolver:
    """Markenabgleich inkl. offener Entdeckung.

    Wird einmal je Auswertungslauf gebaut und dabei fortgeschrieben: eine neu
    entdeckte Marke ist ab dem nächsten Lauf sofort bekannt.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._lookup: dict[str, int] = {}
        self._reload()

    def _reload(self) -> None:
        self._lookup.clear()
        for row in self._conn.execute("SELECT id, name, aliases FROM brands"):
            for candidate in [row["name"], *json.loads(row["aliases"])]:
                key = normalize_brand(candidate)
                if key:
                    self._lookup.setdefault(key, row["id"])

    def resolve(self, name: str) -> tuple[int, bool]:
        """(brand_id, is_new). Unbekannte Marken werden angelegt, nicht verworfen."""
        key = normalize_brand(name)
        if not key:
            raise ValueError("Leerer Markenname")

        existing = self._lookup.get(key)
        if existing is not None:
            return existing, False

        # Offene Entdeckung: is_known = 0 markiert "vom Auswertungs-Layer
        # gefunden, noch nicht von Menschen eingeordnet". is_competitor bleibt
        # auf dem Default 1 — die Einordnung als Partner ist eine bewusste
        # Entscheidung, die niemand automatisch treffen sollte.
        cursor = self._conn.execute(
            """
            INSERT INTO brands (name, aliases, is_known, is_own_brand, is_competitor,
                                first_seen_at, notes)
            VALUES (?, '[]', 0, 0, 1, ?, ?)
            """,
            (name.strip(), utcnow(), f"Automatisch entdeckt von {EVALUATOR_VERSION}."),
        )
        brand_id = int(cursor.lastrowid)
        self._lookup[key] = brand_id
        return brand_id, True

    def own_brand_id(self) -> int | None:
        row = self._conn.execute(
            "SELECT id FROM brands WHERE is_own_brand = 1 ORDER BY id LIMIT 1"
        ).fetchone()
        return int(row["id"]) if row else None


def apply_evaluation(
    conn: sqlite3.Connection,
    resolver: BrandResolver,
    run_id: int,
    parsed: dict[str, Any],
    raw_output: str,
    model: str,
) -> AppliedEvaluation:
    warnings: list[str] = []
    new_brands: list[str] = []
    own_brand_id = resolver.own_brand_id()

    # --- Marken auflösen, Reihenfolge erhalten, Dubletten zusammenführen ----
    ordered: list[tuple[int, str]] = []  # (brand_id, mention_text)
    seen: set[int] = set()
    for entry in parsed.get("brands_in_order") or []:
        name = (entry or {}).get("name", "").strip()
        if not name:
            continue
        brand_id, is_new = resolver.resolve(name)
        if is_new:
            new_brands.append(name)
        if brand_id in seen:
            # Das Modell hat dieselbe Marke zweimal gelistet (oder zwei
            # Schreibweisen derselben Marke). Erste Nennung gewinnt — die
            # Position ist die Kennzahl, nicht die Häufigkeit.
            continue
        seen.add(brand_id)
        ordered.append((brand_id, (entry.get("mention_text") or name).strip()))

    # --- Abgeleitete Kennzahlen (deterministisch) --------------------------
    position = next(
        (rank for rank, (brand_id, _) in enumerate(ordered, start=1) if brand_id == own_brand_id),
        None,
    )
    mentioned = position is not None

    if bool(parsed.get("logbatt_mentioned")) != mentioned:
        # Kein Fehler, aber ein Signal: entweder hat das Modell LogBATT im
        # Fließtext gesehen, ohne es zu listen, oder umgekehrt.
        warnings.append(
            f"Modell meldet logbatt_mentioned={parsed.get('logbatt_mentioned')}, "
            f"aus der Markenliste abgeleitet: {mentioned}. Abgeleiteter Wert gilt."
        )

    # share_of_voice = LogBATT-Anteil an allen Marken-Nennungen dieses Laufs.
    # Jede Marke zählt einmal (erste Nennung), also 1/N bzw. 0. Über eine
    # gefilterte Menge aggregiert das Dashboard sum(LogBATT)/sum(alle).
    share_of_voice = (1.0 / len(ordered)) if (mentioned and ordered) else 0.0

    sentiment = parsed.get("sentiment") if mentioned else None
    if sentiment not in ("positive", "neutral", "negative"):
        sentiment = None

    # Ohne Nennung gibt es nichts zu verankern.
    anchored = bool(parsed.get("problem_narrative_anchored")) and mentioned

    # --- Schreiben (neue Zeile, alte bleibt erhalten) ----------------------
    conn.execute("UPDATE evaluations SET is_current = 0 WHERE run_id = ?", (run_id,))
    cursor = conn.execute(
        """
        INSERT INTO evaluations (
            run_id, logbatt_mentioned, logbatt_position, sentiment,
            problem_narrative_anchored, share_of_voice, raw_classifier_output,
            evaluator_version, model, is_current, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (
            run_id,
            int(mentioned),
            position,
            sentiment,
            int(anchored),
            share_of_voice,
            raw_output,
            EVALUATOR_VERSION,
            model,
            utcnow(),
        ),
    )
    evaluation_id = int(cursor.lastrowid)

    for rank, (brand_id, mention_text) in enumerate(ordered, start=1):
        conn.execute(
            """
            INSERT INTO brand_mentions (run_id, evaluation_id, brand_id, mention_rank, mention_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, evaluation_id, brand_id, rank, mention_text),
        )

    conn.commit()

    return AppliedEvaluation(
        run_id=run_id,
        evaluation_id=evaluation_id,
        logbatt_mentioned=mentioned,
        logbatt_position=position,
        sentiment=sentiment,
        problem_narrative_anchored=anchored,
        share_of_voice=share_of_voice,
        mentions=len(ordered),
        new_brands=new_brands,
        warnings=warnings,
    )
