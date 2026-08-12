"""Systemprompt, JSON-Schema und User-Message für den Auswertungs-Layer.

Der Systemprompt ist KONSTANT (Marke, Wettbewerber, Regeln, Schema) und steht
vor der variablen Rohantwort — genau die Reihenfolge, die Prompt Caching
braucht: `tools` -> `system` -> `messages`. Alles Volatile (Prompt-Text,
Antworttext) liegt hinter dem Cache-Breakpoint.

Zwei Dinge, die den Cache still zerstören würden und deshalb hier bewusst
geregelt sind:

  1. Die Brand-Liste enthält NUR bekannte Brands (is_known = 1), sortiert nach
     Name. Von Ebene 2 neu entdeckte Brands kommen NICHT in den Systemprompt —
     sonst würde jede Entdeckung den Prefix ändern und den Cache für alle
     folgenden Läufe entwerten. Neue Brands werden im Code abgeglichen, nicht
     im Prompt.
  2. Kein Datum, keine Run-ID, keine Zählerstände im Systemprompt.

ACHTUNG — Mindestlänge fürs Caching: Claude Haiku 4.5 cached erst ab 4096
Tokens Prefix. Darunter passiert schlicht nichts (kein Fehler, nur
cache_creation_input_tokens = 0). Siehe README, Abschnitt "Kosten".
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

# Version des Auswertungs-Layers. Ändert sich, sobald Systemprompt, Schema oder
# Ableitungslogik angefasst werden — landet in evaluations.evaluator_version,
# damit im Dashboard sichtbar bleibt, mit welcher Logik ein Wert entstand.
EVALUATOR_VERSION = "e2-2026-08-12.1"

OWN_BRAND = "LogBATT"


# ---------------------------------------------------------------------------
# JSON-Schema (Structured Outputs)
# ---------------------------------------------------------------------------
# Bewusst schmal gehalten: das Modell liefert NUR, was Sprachverständnis
# braucht. Alles Ableitbare (mention_rank, logbatt_position, share_of_voice)
# rechnen wir deterministisch aus dem Ergebnis — ein Modell, das Anteile
# ausrechnet, ist eine unnötige Fehlerquelle. Siehe apply.py.
RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "brands_in_order": {
            "type": "array",
            "description": (
                "ALLE genannten Anbieter/Marken, in der Reihenfolge ihres ersten "
                "Auftretens im Antworttext."
            ),
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Kanonischer Markenname aus der Liste, sonst der Name wie im Text.",
                    },
                    "mention_text": {
                        "type": "string",
                        "description": "Die Schreibweise, wie sie im Antworttext steht.",
                    },
                },
                "required": ["name", "mention_text"],
                "additionalProperties": False,
            },
        },
        "logbatt_mentioned": {
            "type": "boolean",
            "description": "Wird LogBATT im Antworttext genannt?",
        },
        "sentiment": {
            "type": "string",
            "enum": ["positive", "neutral", "negative"],
            "description": (
                "Sentiment gegenüber LogBATT. Wenn LogBATT nicht genannt wird: 'neutral' "
                "(der Wert wird dann verworfen)."
            ),
        },
        "problem_narrative_anchored": {
            "type": "boolean",
            "description": (
                "Wird LogBATT im Kontext eines Gefahren-/Havarieszenarios genannt "
                "(Thermal Runaway, Brand, defekte/kritisch defekte Batterie, Havariefall, "
                "Löschwasser, Unfall) — oder nur als generischer Anbieter?"
            ),
        },
        "problem_narrative_evidence": {
            "type": "string",
            "description": (
                "Wörtliches Zitat aus dem Antworttext, das die Einordnung belegt. "
                "Leerer String, wenn kein Beleg."
            ),
        },
    },
    "required": [
        "brands_in_order",
        "logbatt_mentioned",
        "sentiment",
        "problem_narrative_anchored",
        "problem_narrative_evidence",
    ],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Systemprompt
# ---------------------------------------------------------------------------
_INSTRUCTIONS = """\
Du wertest Antworten von KI-Suchoberflächen (ChatGPT, Perplexity, Gemini, \
Google AI Overview) für ein GEO-Monitoring der LogBATT GmbH aus.

LogBATT ist Anbieter einer Gesamtlösung für Lithium-Ionen-Batterielogistik: \
Transport, Lagerung, Verpackung, Entsorgung und Recycling, dazu eigene \
zertifizierte Transport-, Lager- und Quarantänebehälter (Marke SafetyBATTbox). \
Sitz Plochingen, seit 2023 Teil der Lagermax Group.

Du bekommst den Prompt, der gestellt wurde, und den vollständigen Antworttext. \
Deine Aufgabe ist reine Textanalyse. Du recherchierst nicht, du ergänzt kein \
Wissen und du korrigierst die Antwort nicht — du beschreibst nur, was im Text \
steht.

## Aufgabe 1 — Marken in Reihenfolge

Extrahiere ALLE genannten Anbieter/Marken in der Reihenfolge ihres ERSTEN \
Auftretens im Antworttext. Reihenfolge heißt Textreihenfolge (von oben nach \
unten, in Tabellen zeilenweise) — nicht die Reihenfolge in einem Quellen- oder \
Linkblock.

Regeln:
- Jede Marke genau EINMAL, an der Position ihrer ersten Nennung.
- Gleiche eine erkannte Marke gegen die Liste bekannter Marken unten ab und \
  gib dann den dortigen kanonischen Namen zurück (Spalte "Name"), egal welche \
  Schreibweise im Text steht.
- Marken, die NICHT in der Liste stehen, gibst du trotzdem zurück — mit dem \
  Namen, wie er im Text steht. Neue Anbieter sollen gefunden werden.
- Zähle nur Anbieter/Hersteller/Dienstleister als Marke. Keine Behörden, \
  Normen, Verbände, Zertifikate, Gesetze, Produktkategorien oder Portale \
  (z. B. nicht: ADR, DIBt, TÜV, IHK, DGUV, "Wer liefert was").
- Produktnamen sind keine eigenen Marken: "SafetyBATTbox" ist LogBATT, \
  "RED BOXX" ist Ellermann.
- `mention_text` ist die Schreibweise, die tatsächlich im Text steht.

## Aufgabe 2 — Sentiment gegenüber LogBATT

- positive: LogBATT wird empfohlen, hervorgehoben, als führend/spezialisiert \
  beschrieben oder an erster Stelle als passende Lösung genannt.
- neutral: LogBATT steht als einer von mehreren Anbietern in einer Liste, ohne \
  wertende Aussage.
- negative: Einschränkungen, Kritik, Abraten, oder LogBATT wird als weniger \
  geeignet als ein anderer Anbieter dargestellt.

Wird LogBATT nicht genannt, gib "neutral" zurück.

## Aufgabe 3 — Problem-Narrativ-Verankerung

`problem_narrative_anchored` = true, wenn LogBATT im Kontext eines Gefahren- \
oder Havarieszenarios genannt wird: Thermal Runaway, Brand/Brandfall, \
Löschwasser/Wasserbad, Unfall, defekte oder kritisch defekte Batterien, \
Havariefall, Quarantäne, Rückruf.

`problem_narrative_anchored` = false, wenn LogBATT nur als generischer Anbieter \
in einer Auflistung steht (Verkauf, Vermietung, Logistik, Lagerung ohne \
Gefahrenbezug) — oder wenn LogBATT gar nicht genannt wird.

Entscheidend ist der Kontext DER LOGBATT-NENNUNG, nicht das Thema des Prompts. \
Ein Prompt über Havariefälle, dessen Antwort LogBATT nur in einer neutralen \
Anbieterliste führt, ist NICHT verankert.

`problem_narrative_evidence`: das wörtliche Textstück, auf das du die \
Entscheidung stützt. Wenn LogBATT nicht genannt wird oder es keinen Beleg gibt: \
leerer String.

## Ausgabe

Antworte ausschließlich mit dem geforderten JSON-Objekt. Kein Fließtext, keine \
Erklärung, keine Code-Fences.
"""


def _known_brand_table(conn: sqlite3.Connection) -> str:
    """Markdown-Tabelle der bekannten Marken — deterministisch sortiert.

    Nur is_known = 1. Die von Ebene 2 entdeckten Marken bleiben draußen, damit
    der Systemprompt stabil bleibt (siehe Modul-Docstring).
    """
    rows = conn.execute(
        """
        SELECT name, aliases, is_own_brand, is_competitor
          FROM brands
         WHERE is_known = 1
         ORDER BY name COLLATE NOCASE
        """
    ).fetchall()

    lines = ["| Name | Auch geschrieben als | Rolle |", "| --- | --- | --- |"]
    for row in rows:
        aliases = ", ".join(sorted(json.loads(row["aliases"]))) or "–"
        if row["is_own_brand"]:
            role = "eigene Marke"
        elif row["is_competitor"]:
            role = "Wettbewerber"
        else:
            role = "Partner, kein Wettbewerber"
        lines.append(f"| {row['name']} | {aliases} | {role} |")
    return "\n".join(lines)


def build_system_prompt(conn: sqlite3.Connection) -> str:
    """Der konstante, cachebare Systemprompt."""
    return (
        _INSTRUCTIONS
        + "\n## Bekannte Marken\n\n"
        + _known_brand_table(conn)
        + "\n"
    )


def build_user_message(prompt_text: str, raw_response: str) -> str:
    """Der variable Teil — steht hinter dem Cache-Breakpoint."""
    return (
        f"<gestellter_prompt>\n{prompt_text}\n</gestellter_prompt>\n\n"
        f"<antworttext>\n{raw_response}\n</antworttext>"
    )
