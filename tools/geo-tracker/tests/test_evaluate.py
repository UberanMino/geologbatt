"""Tests für Ebene 2 (Auswertungs-Layer).

Kein Test hier ruft die Anthropic-API auf — geprüft wird, was wir selbst
verantworten: Markenabgleich, offene Entdeckung, die deterministisch
abgeleiteten Kennzahlen, Wiederholbarkeit und die Cache-Stabilität des
Systemprompts.

    python tools/geo-tracker/tests/test_evaluate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotracker.db import open_db  # noqa: E402
from geotracker.evaluate.apply import BrandResolver, apply_evaluation, normalize_brand  # noqa: E402
from geotracker.evaluate.prompt import (  # noqa: E402
    RESPONSE_SCHEMA,
    build_system_prompt,
    build_user_message,
)
from geotracker.evaluate.runner import select_runs  # noqa: E402
from geotracker.ingest import RunTarget, ingest_target  # noqa: E402
from geotracker.seeds import build_classifier, seed_all  # noqa: E402
from test_ingest import FIXTURE, _config, _fixture_fetch  # noqa: E402


def _db_with_run(tmp_path: Path):
    """Ebene-1-DB mit genau einem gespeicherten Lauf (Fixture)."""
    config = _config(tmp_path)
    conn = open_db(config.db_path)
    seed_all(conn)
    row = conn.execute("SELECT * FROM prompts ORDER BY id LIMIT 1").fetchone()
    target = RunTarget(
        prompt_id=row["id"], text=row["text"], category=row["category"],
        country=row["country"], language=row["language"], engine="chatgpt",
    )
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    outcome = ingest_target(
        conn, config, build_classifier(conn), target, fetch=_fixture_fetch(payload)
    )
    return conn, outcome.run_id


# Modellausgabe, wie sie zum Fixture-Antworttext passt (LogBATT zuerst,
# PROTECTO, LionCare, dann zwei Marken, die in keinem Seed stehen).
MODEL_OUTPUT = {
    "brands_in_order": [
        {"name": "LogBATT", "mention_text": "LogBATT GmbH"},
        {"name": "PROTECTO", "mention_text": "PROTECTO GmbH"},
        {"name": "LionCare", "mention_text": "LionCare"},
        {"name": "Schuon Batterielogistik", "mention_text": "Schuon Batterielogistik"},
        {"name": "Lacont", "mention_text": "Batterielagerung.de (Lacont)"},
    ],
    "logbatt_mentioned": True,
    "sentiment": "positive",
    "problem_narrative_anchored": False,
    "problem_narrative_evidence": "",
}


# ---------------------------------------------------------------------------
def test_normalize_brand():
    # Rechtsform, Groß-/Kleinschreibung und Satzzeichen dürfen nicht trennen.
    assert normalize_brand("Zarges GmbH") == normalize_brand("ZARGES")
    assert normalize_brand("Bauer Südlohn GmbH") == normalize_brand("bauer-suedlohn")
    assert normalize_brand("Paul Müller") == normalize_brand("Paul Mueller")
    assert normalize_brand("Ellermann GmbH & Co. KG") == normalize_brand("Ellermann")
    # Verschiedene Marken bleiben verschieden.
    assert normalize_brand("DENIOS") != normalize_brand("DellCon")
    assert normalize_brand("") == ""


def test_response_schema_is_strict():
    # Structured Outputs verlangen additionalProperties=false und required.
    assert RESPONSE_SCHEMA["additionalProperties"] is False
    assert set(RESPONSE_SCHEMA["required"]) == set(RESPONSE_SCHEMA["properties"])
    item = RESPONSE_SCHEMA["properties"]["brands_in_order"]["items"]
    assert item["additionalProperties"] is False
    assert set(item["required"]) == set(item["properties"])


def test_derived_metrics_are_computed_not_trusted(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    outcome = apply_evaluation(
        conn, BrandResolver(conn), run_id, MODEL_OUTPUT, json.dumps(MODEL_OUTPUT), "claude-haiku-4-5"
    )

    assert outcome.logbatt_mentioned is True
    assert outcome.logbatt_position == 1          # aus der Reihenfolge abgeleitet
    assert outcome.mentions == 5
    assert outcome.share_of_voice == 1 / 5        # 1 von 5 Marken, nicht vom Modell
    assert outcome.sentiment == "positive"
    assert outcome.problem_narrative_anchored is False

    ranks = conn.execute(
        """
        SELECT m.mention_rank, b.name FROM brand_mentions m
        JOIN brands b ON b.id = m.brand_id
        WHERE m.evaluation_id = ? ORDER BY m.mention_rank
        """,
        (outcome.evaluation_id,),
    ).fetchall()
    assert [r["mention_rank"] for r in ranks] == [1, 2, 3, 4, 5]
    assert ranks[0]["name"] == "LogBATT"

    # Die rohe Modellausgabe bleibt vollständig erhalten.
    stored = conn.execute(
        "SELECT raw_classifier_output FROM evaluations WHERE id = ?", (outcome.evaluation_id,)
    ).fetchone()["raw_classifier_output"]
    assert json.loads(stored) == MODEL_OUTPUT


def test_open_brand_discovery(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    outcome = apply_evaluation(
        conn, BrandResolver(conn), run_id, MODEL_OUTPUT, "{}", "claude-haiku-4-5"
    )

    # Nicht gelistete Marken werden angelegt, nicht verworfen.
    assert sorted(outcome.new_brands) == ["Lacont", "Schuon Batterielogistik"]
    for name in outcome.new_brands:
        row = conn.execute("SELECT is_known FROM brands WHERE name = ?", (name,)).fetchone()
        assert row is not None and row["is_known"] == 0

    # Bekannte Marken erzeugen keine Dubletten.
    assert conn.execute(
        "SELECT COUNT(*) c FROM brands WHERE name = 'LogBATT'"
    ).fetchone()["c"] == 1


def test_alias_matching_does_not_create_duplicates(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    parsed = dict(MODEL_OUTPUT)
    # Aliasschreibweisen bekannter Marken.
    parsed["brands_in_order"] = [
        {"name": "Log BATT", "mention_text": "Log BATT"},
        {"name": "Denios AG", "mention_text": "Denios AG"},
        {"name": "ZARGES GmbH", "mention_text": "ZARGES GmbH"},
    ]
    before = conn.execute("SELECT COUNT(*) c FROM brands").fetchone()["c"]
    outcome = apply_evaluation(conn, BrandResolver(conn), run_id, parsed, "{}", "m")

    assert outcome.new_brands == []
    assert conn.execute("SELECT COUNT(*) c FROM brands").fetchone()["c"] == before
    assert outcome.logbatt_position == 1


def test_duplicate_brand_keeps_first_position(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    parsed = dict(MODEL_OUTPUT)
    parsed["brands_in_order"] = [
        {"name": "DENIOS", "mention_text": "DENIOS"},
        {"name": "LogBATT", "mention_text": "LogBATT"},
        {"name": "DENIOS GmbH", "mention_text": "DENIOS GmbH"},  # dieselbe Marke nochmal
    ]
    outcome = apply_evaluation(conn, BrandResolver(conn), run_id, parsed, "{}", "m")

    assert outcome.mentions == 2
    assert outcome.logbatt_position == 2
    assert outcome.share_of_voice == 0.5


def test_no_mention_clears_sentiment_and_anchoring(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    parsed = {
        "brands_in_order": [{"name": "DENIOS", "mention_text": "DENIOS"}],
        # Das Modell behauptet Nennung und Verankerung — die Markenliste sagt nein.
        "logbatt_mentioned": True,
        "sentiment": "positive",
        "problem_narrative_anchored": True,
        "problem_narrative_evidence": "",
    }
    outcome = apply_evaluation(conn, BrandResolver(conn), run_id, parsed, "{}", "m")

    assert outcome.logbatt_mentioned is False
    assert outcome.logbatt_position is None
    assert outcome.sentiment is None
    assert outcome.problem_narrative_anchored is False
    assert outcome.share_of_voice == 0.0
    assert outcome.warnings, "Widerspruch Modell vs. Ableitung muss gemeldet werden"


def test_re_run_supersedes_without_deleting(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    first = apply_evaluation(conn, BrandResolver(conn), run_id, MODEL_OUTPUT, "{}", "m")

    changed = dict(MODEL_OUTPUT)
    changed["sentiment"] = "neutral"
    second = apply_evaluation(conn, BrandResolver(conn), run_id, changed, "{}", "m")

    rows = conn.execute(
        "SELECT id, is_current, sentiment FROM evaluations WHERE run_id = ? ORDER BY id", (run_id,)
    ).fetchall()
    assert len(rows) == 2, "alte Auswertung darf nicht überschrieben werden"
    assert rows[0]["id"] == first.evaluation_id and rows[0]["is_current"] == 0
    assert rows[1]["id"] == second.evaluation_id and rows[1]["is_current"] == 1
    assert rows[1]["sentiment"] == "neutral"

    # brand_mentions hängen an der jeweiligen Auswertung, nicht am Lauf.
    assert conn.execute(
        "SELECT COUNT(DISTINCT evaluation_id) c FROM brand_mentions WHERE run_id = ?", (run_id,)
    ).fetchone()["c"] == 2


def test_select_runs_skips_evaluated_and_re_run_includes(tmp_path):
    conn, run_id = _db_with_run(tmp_path)
    assert [t.run_id for t in select_runs(conn)] == [run_id]

    apply_evaluation(conn, BrandResolver(conn), run_id, MODEL_OUTPUT, "{}", "m")
    assert select_runs(conn) == []
    assert [t.run_id for t in select_runs(conn, re_run=True)] == [run_id]


def test_system_prompt_is_cache_stable_after_discovery(tmp_path):
    """Der Cache-Prefix darf sich durch offene Entdeckung NICHT ändern.

    Neu entdeckte Marken (is_known = 0) gehören nicht in den Systemprompt —
    sonst würde jede Entdeckung den Prompt-Cache aller folgenden Läufe entwerten.
    """
    conn, run_id = _db_with_run(tmp_path)
    before = build_system_prompt(conn)

    outcome = apply_evaluation(conn, BrandResolver(conn), run_id, MODEL_OUTPUT, "{}", "m")
    assert outcome.new_brands, "Test braucht mindestens eine neue Marke"

    assert build_system_prompt(conn) == before
    # Deterministisch: gleicher Input, gleiche Bytes.
    assert build_system_prompt(conn) == build_system_prompt(conn)
    # Nichts Volatiles im Prefix.
    assert "2026-" not in before and "run #" not in before


def test_user_message_carries_volatile_part():
    message = build_user_message("Prompt?", "Antworttext")
    assert "Prompt?" in message and "Antworttext" in message


def test_ebene_1_does_not_import_ebene_2():
    """Architektur-Zusage: Ebene 1 kennt Ebene 2 nicht — auch nicht beim Import."""
    root = Path(__file__).resolve().parents[1] / "geotracker"
    for name in ("ingest.py", "classify.py", "seeds.py", "db.py", "config.py", "urls.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "evaluate" not in source, f"{name} referenziert den Auswertungs-Layer"
    # Auch die CLI importiert Ebene 2 nur innerhalb der Befehle (lazy), damit
    # `ingest` ohne installiertes anthropic-SDK läuft.
    cli = (root / "cli.py").read_text(encoding="utf-8")
    assert "\nfrom .evaluate import" not in cli


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile
    import traceback

    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(Path(tmp)) if fn.__code__.co_argcount else fn()
                print(f"  ok   {name}")
            except Exception:
                failed += 1
                print(f"  FAIL {name}")
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} Tests bestanden.")
    sys.exit(1 if failed else 0)
