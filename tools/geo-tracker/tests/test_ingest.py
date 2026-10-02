"""Tests für Ebene 1.

Der zentrale Test ist `test_evaluation_layer_is_not_required`: er hält die
Architektur-Zusage fest, dass Rohspeicherung ohne Auswertungs-Layer und ohne
Anthropic-Key vollständig funktioniert.

    python -m pytest tools/geo-tracker/tests -q
    # oder ohne pytest:
    python tools/geo-tracker/tests/test_ingest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotracker.config import Config  # noqa: E402
from geotracker.db import open_db  # noqa: E402
from geotracker.ingest import RunTarget, ingest_target, plan_targets  # noqa: E402
from geotracker.searchapi.client import SearchApiError, SearchApiResult  # noqa: E402
from geotracker.searchapi.parsers import build_params, parse_response  # noqa: E402
from geotracker.seeds import build_classifier, seed_all  # noqa: E402
from geotracker.urls import domain_matches, normalize_domain  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "chatgpt_lagercontainer_2026-07-27.json"


def _config(tmp_path: Path, *, searchapi_key: str = "", anthropic_key: str = "") -> Config:
    return Config(
        db_path=tmp_path / "test.sqlite3",
        searchapi_key=searchapi_key,
        searchapi_base_url="https://www.searchapi.io/api/v1/search",
        anthropic_key=anthropic_key,
        request_timeout=10,
        max_retries=0,
        retry_backoff=0.0,
        throttle_seconds=0.0,
        max_runs_per_invocation=10,
        chatgpt_web_search=True,
        engines_for_scheduler=("chatgpt",),
    )


def _setup(tmp_path: Path):
    config = _config(tmp_path)
    conn = open_db(config.db_path)
    seed_all(conn)
    return config, conn, build_classifier(conn)


def _fixture_fetch(payload: dict):
    def fetch(params):
        return SearchApiResult(
            payload=payload,
            raw_body=json.dumps(payload),
            http_status=200,
            attempts=1,
            latency_ms=1234,
            request_url="fixture://chatgpt",
        )

    return fetch


def _target(conn) -> RunTarget:
    row = conn.execute("SELECT * FROM prompts ORDER BY id LIMIT 1").fetchone()
    return RunTarget(
        prompt_id=row["id"],
        text=row["text"],
        category=row["category"],
        country=row["country"],
        language=row["language"],
        engine="chatgpt",
    )


# ---------------------------------------------------------------------------
def test_normalize_domain():
    assert normalize_domain("https://WWW.LogBATT.de/lager/?utm_source=x") == "logbatt.de"
    assert normalize_domain("logbatt.de") == "logbatt.de"
    assert normalize_domain("https://shop.denios.de/a/1") == "shop.denios.de"
    assert normalize_domain("") == ""
    assert domain_matches("shop.denios.de", "denios.de")
    # Kein Teilstring-Match: "notdenios.de" darf nicht auf "denios.de" matchen.
    assert not domain_matches("notdenios.de", "denios.de")


def test_build_params_chatgpt():
    # Exakt die dokumentierten Parameternamen — nichts geraten.
    assert build_params("chatgpt", "Testprompt") == {
        "engine": "chatgpt",
        "q": "Testprompt",
        "web_search": "true",
    }
    assert "web_search" not in build_params("chatgpt", "Testprompt", web_search=False)


def test_parse_chatgpt_fixture():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    parsed = parse_response("chatgpt", payload)

    assert parsed.status == "success"
    assert parsed.raw_response and len(parsed.raw_response) > 500
    assert parsed.provider_model == "gpt-5-5"
    assert parsed.web_search_performed is True

    cited = [c for c in parsed.citations if c.origin == "cited"]
    assert len(cited) == 10
    # citation_rank ist lückenlos 1-basiert, in Reihenfolge des Quellenblocks.
    assert [c.citation_rank for c in cited] == list(range(1, 11))
    assert cited[0].cited_domain == "lithiumionenlagerung.de"
    assert cited[1].cited_domain == "logbatt.com"


def test_ingest_stores_raw_response_and_every_citation(tmp_path):
    config, conn, classifier = _setup(tmp_path)
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    outcome = ingest_target(
        conn, config, classifier, _target(conn), fetch=_fixture_fetch(payload)
    )

    assert outcome.status == "success"
    assert outcome.citations_cited == 10

    run = conn.execute("SELECT * FROM runs WHERE id = ?", (outcome.run_id,)).fetchone()
    # Ebene 1: voller Antworttext UND kompletter Provider-Payload.
    assert run["raw_response"] == payload["markdown"]
    assert json.loads(run["raw_payload"])["response_metadata"]["model"] == "gpt-5-5"
    # Kein Secret in der gespeicherten URL.
    assert "api_key" not in (run["request_url"] or "")

    rows = conn.execute(
        "SELECT * FROM citations WHERE run_id = ? AND origin = 'cited' ORDER BY citation_rank",
        (outcome.run_id,),
    ).fetchall()
    assert len(rows) == 10
    # Jede Quelle ist eine eigene Zeile mit roher URL + rohem JSON.
    for row in rows:
        assert row["cited_url"].startswith("https://")
        assert json.loads(row["raw_json"])["ref_id"].startswith("turn0search")

    by_domain = {row["cited_domain"]: row for row in rows}
    assert by_domain["logbatt.de"]["source_type"] == "owned"
    assert by_domain["protecto.de"]["source_type"] == "competitor"
    assert by_domain["wlw.de"]["source_type"] == "earned_media"
    # Offene Entdeckung: unbekannte Domain wird gespeichert, nicht verworfen.
    assert by_domain["relionbat.com"]["source_type"] == "other"
    assert by_domain["relionbat.com"]["is_known"] == 0
    assert conn.execute(
        "SELECT 1 FROM domains WHERE domain = 'relionbat.com'"
    ).fetchone() is not None


def test_evaluation_layer_is_not_required(tmp_path):
    """Ebene 1 läuft ohne ANTHROPIC_API_KEY und ohne jede Auswertung."""
    config = _config(tmp_path, anthropic_key="")
    conn = open_db(config.db_path)
    seed_all(conn)
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    outcome = ingest_target(
        conn, config, build_classifier(conn), _target(conn), fetch=_fixture_fetch(payload)
    )

    assert outcome.status == "success"
    assert conn.execute("SELECT COUNT(*) c FROM citations").fetchone()["c"] == 10
    # Ebene 2 ist leer — und das ist völlig in Ordnung.
    assert conn.execute("SELECT COUNT(*) c FROM evaluations").fetchone()["c"] == 0
    assert conn.execute("SELECT COUNT(*) c FROM brand_mentions").fetchone()["c"] == 0


def test_failed_run_is_still_stored(tmp_path):
    """Auch ein Fehlschlag wird protokolliert — inklusive Fehler-Body."""
    config, conn, classifier = _setup(tmp_path)

    def failing_fetch(params):
        raise SearchApiError("HTTP 429 von SearchApi", status=429, body='{"error":"rate limited"}')

    outcome = ingest_target(conn, config, classifier, _target(conn), fetch=failing_fetch)

    assert outcome.status == "error"
    run = conn.execute("SELECT * FROM runs WHERE id = ?", (outcome.run_id,)).fetchone()
    assert run["status"] == "error"
    assert run["http_status"] == 429
    assert "rate limited" in run["raw_payload"]


def test_partial_when_no_sources(tmp_path):
    """Antwort ohne Quellen -> status = partial, Rohantwort trotzdem gespeichert."""
    config, conn, classifier = _setup(tmp_path)
    payload = {
        "search_metadata": {"id": "search_x", "status": "Success"},
        "markdown": "Eine Antwort ganz ohne Websuche.",
        "response_metadata": {"model": "gpt-5-5", "is_web_search_performed": False},
    }

    outcome = ingest_target(conn, config, classifier, _target(conn), fetch=_fixture_fetch(payload))

    assert outcome.status == "partial"
    run = conn.execute("SELECT * FROM runs WHERE id = ?", (outcome.run_id,)).fetchone()
    assert run["raw_response"] == "Eine Antwort ganz ohne Websuche."
    assert run["web_search_performed"] == 0


def test_plan_targets_skips_completed_and_retries_failed(tmp_path):
    config, conn, classifier = _setup(tmp_path)
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    target = _target(conn)

    before = len(plan_targets(conn, engine="chatgpt"))
    ingest_target(conn, config, classifier, target, fetch=_fixture_fetch(payload))
    after = len(plan_targets(conn, engine="chatgpt"))
    assert after == before - 1

    # --force ignoriert den Tages-Check und legt einen NEUEN run an.
    assert len(plan_targets(conn, engine="chatgpt", skip_existing_today=False)) == before
    ingest_target(conn, config, classifier, target, fetch=_fixture_fetch(payload))
    assert conn.execute(
        "SELECT COUNT(*) c FROM runs WHERE prompt_id = ?", (target.prompt_id,)
    ).fetchone()["c"] == 2


def test_seed_is_idempotent(tmp_path):
    config, conn, _ = _setup(tmp_path)
    counts = lambda: tuple(  # noqa: E731
        conn.execute(f"SELECT COUNT(*) c FROM {t}").fetchone()["c"]
        for t in ("prompts", "brands", "brand_domains", "domains")
    )
    first = counts()
    seed_all(conn)
    assert counts() == first


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile
    import traceback

    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_")]
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
