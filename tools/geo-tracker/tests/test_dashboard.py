"""Tests für Schritt 3: weitere Engines, Peec-Import, Filter und API.

Der wichtigste Test ist `test_filters_apply_to_every_metric`: er hält die
zentrale Zusage fest, dass Kennzahlen IMMER aus der gefilterten Menge kommen
und nie aus der Gesamtmenge.

    python tools/geo-tracker/tests/test_dashboard.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotracker.api import queries  # noqa: E402
from geotracker.api.queries import Filters  # noqa: E402
from geotracker.db import open_db  # noqa: E402
from geotracker.importers.peec import import_directory  # noqa: E402
from geotracker.searchapi.parsers import (  # noqa: E402
    EngineNotImplemented,
    build_google_params,
    build_params,
    extract_page_token,
    parse_response,
)
from geotracker.seeds import build_classifier, seed_all  # noqa: E402
from test_ingest import _config  # noqa: E402

PEEC_DIR = Path(__file__).resolve().parents[3] / "data/peec/2026-07-27_2026-08-03/chats"


def _db(tmp_path: Path):
    config = _config(tmp_path)
    conn = open_db(config.db_path)
    seed_all(conn)
    import_directory(conn, build_classifier(conn), PEEC_DIR, category="Peec-Import")
    return conn


# ---------------------------------------------------------------------------
# Engines 2–4
# ---------------------------------------------------------------------------
def test_engine_params_match_documented_names():
    # Nur dokumentierte Parameter — nichts geraten. Keine Engine bekommt gl/hl.
    assert build_params("perplexity", "Frage") == {
        "engine": "perplexity", "q": "Frage", "sources": "web",
    }
    assert build_params("gemini", "Frage") == {"engine": "gemini", "q": "Frage"}
    assert build_params("google_ai_overview", "Frage", page_token="tok") == {
        "engine": "google_ai_overview", "page_token": "tok",
    }
    for engine in ("chatgpt", "perplexity", "gemini"):
        params = build_params(engine, "Frage")
        assert "gl" not in params and "hl" not in params and "location" not in params


def test_google_step_carries_country_and_language():
    # Der vorgelagerte google-Call ist die EINZIGE Stelle mit echtem gl/hl.
    assert build_google_params("Frage", country="DE", language="de") == {
        "engine": "google", "q": "Frage", "gl": "de", "hl": "de",
    }


def test_ai_overview_requires_page_token():
    try:
        build_params("google_ai_overview", "Frage")
    except EngineNotImplemented as exc:
        assert "page_token" in str(exc)
    else:
        raise AssertionError("ohne page_token muss ein Fehler kommen")


def test_extract_page_token():
    assert extract_page_token({"ai_overview": {"page_token": "abc"}}) == "abc"
    # Keine Overview ausgespielt ist ein Normalfall, kein Fehler.
    assert extract_page_token({"organic_results": []}) is None


def test_reference_link_engines_parse_identically():
    payload = {
        "search_metadata": {"id": "search_1"},
        "markdown": "Antwort mit Quellen.",
        "reference_links": [
            {"index": 0, "title": "A", "link": "https://denios.de/x", "source": "denios.de"},
            {"index": 1, "title": "B", "link": "https://logbatt.de/y", "source": "logbatt.de"},
        ],
        "response_metadata": {"model": "sonar"},
    }
    for engine in ("perplexity", "gemini", "google_ai_overview"):
        parsed = parse_response(engine, payload)
        assert parsed.status == "success"
        assert [c.cited_domain for c in parsed.citations] == ["denios.de", "logbatt.de"]
        assert all(c.origin == "cited" for c in parsed.citations)


def test_ai_overview_without_answer_is_deferred():
    parsed = parse_response("google_ai_overview", {"search_metadata": {"id": "x"}})
    assert parsed.status == "deferred"


# ---------------------------------------------------------------------------
# Peec-Import
# ---------------------------------------------------------------------------
def test_peec_import_marks_provenance_honestly(tmp_path):
    conn = _db(tmp_path)

    runs = conn.execute("SELECT COUNT(*) c FROM runs WHERE source = 'peec_import'").fetchone()["c"]
    assert runs == 160, runs
    assert conn.execute(
        "SELECT COUNT(*) c FROM runs WHERE source = 'searchapi'"
    ).fetchone()["c"] == 0

    # Peec liefert nur Domains — es werden KEINE URLs erfunden.
    assert conn.execute("SELECT COUNT(*) c FROM citations WHERE url_known = 1").fetchone()["c"] == 0
    assert conn.execute("SELECT COUNT(*) c FROM citations WHERE cited_url != ''").fetchone()["c"] == 0

    # Und die Auswertung ist als fremde gekennzeichnet.
    versions = {
        row["evaluator_version"]
        for row in conn.execute("SELECT DISTINCT evaluator_version FROM evaluations")
    }
    assert versions == {"peec-import"}


def test_peec_import_is_idempotent(tmp_path):
    conn = _db(tmp_path)
    before = conn.execute("SELECT COUNT(*) c FROM runs").fetchone()["c"]
    import_directory(conn, build_classifier(conn), PEEC_DIR, category="Peec-Import")
    assert conn.execute("SELECT COUNT(*) c FROM runs").fetchone()["c"] == before


def test_placeholder_is_not_imported_as_domain(tmp_path):
    conn = _db(tmp_path)
    # „–" im Quellenfeld ist keine Domain.
    bad = conn.execute(
        "SELECT COUNT(*) c FROM citations WHERE cited_domain NOT LIKE '%.%'"
    ).fetchone()["c"]
    assert bad == 0


# ---------------------------------------------------------------------------
# Filter — die zentrale Zusage
# ---------------------------------------------------------------------------
def test_filters_apply_to_every_metric(tmp_path):
    conn = _db(tmp_path)
    everything = Filters()
    one_engine = Filters(engines=["chatgpt"])

    total = queries.kpis(conn, everything)
    subset = queries.kpis(conn, one_engine)

    assert subset["runs"] < total["runs"]
    assert subset["citations"]["total"] < total["citations"]["total"]

    # Jede Kennzahl-Query respektiert denselben Filter — keine rechnet auf der
    # Gesamtmenge weiter.
    assert len(queries.timeseries(conn, one_engine)) <= len(queries.timeseries(conn, everything))
    assert {r["label"] for r in queries.breakdown(conn, one_engine, "engine")} == {"chatgpt"}
    assert sum(r["citations"] for r in queries.domain_ranking(conn, one_engine, limit=999)) \
        == subset["citations"]["total"]
    assert sum(r["mentions"] for r in queries.brand_leaderboard(conn, one_engine, limit=999)) \
        <= sum(r["mentions"] for r in queries.brand_leaderboard(conn, everything, limit=999))


def test_facets_are_and_combined(tmp_path):
    conn = _db(tmp_path)
    engine_only = queries.kpis(conn, Filters(engines=["chatgpt"]))["runs"]
    combined = queries.kpis(
        conn, Filters(engines=["chatgpt"], since="2026-07-26", until="2026-07-28")
    )["runs"]
    assert combined < engine_only


def test_domain_filter_selects_only_runs_citing_it(tmp_path):
    conn = _db(tmp_path)
    filters = Filters(domains=["logbatt.de"])
    runs_sql, params = filters.run_ids_sql()
    run_ids = [row["id"] for row in conn.execute(runs_sql, params)]
    assert run_ids

    for run_id in run_ids:
        assert conn.execute(
            "SELECT 1 FROM citations WHERE run_id = ? AND cited_domain = 'logbatt.de'", (run_id,)
        ).fetchone(), f"run {run_id} zitiert logbatt.de nicht"


def test_brand_filter_selects_only_runs_mentioning_it(tmp_path):
    conn = _db(tmp_path)
    brand = conn.execute("SELECT id FROM brands WHERE name = 'RETRON'").fetchone()["id"]
    runs_sql, params = Filters(brand_ids=[brand]).run_ids_sql()
    run_ids = [row["id"] for row in conn.execute(runs_sql, params)]
    assert run_ids

    for run_id in run_ids:
        assert conn.execute(
            "SELECT 1 FROM brand_mentions WHERE run_id = ? AND brand_id = ?", (run_id, brand)
        ).fetchone()


def test_share_of_voice_is_computed_over_filtered_set(tmp_path):
    conn = _db(tmp_path)
    filters = Filters(engines=["gemini"])
    kpi = queries.kpis(conn, filters)
    board = queries.brand_leaderboard(conn, filters, limit=999)

    own = next(r for r in board if r["is_own_brand"])
    # Der SoV der eigenen Marke im Leaderboard muss zur KPI-Kachel passen.
    assert abs(own["share_of_voice"] - kpi["share_of_voice"]) < 1e-9
    # Und alle Anteile zusammen ergeben 100 %.
    assert abs(sum(r["share_of_voice"] for r in board) - 1.0) < 1e-9


def test_previous_period_is_equal_length():
    previous = Filters(since="2026-08-01", until="2026-08-07").previous_period()
    assert previous.since == "2026-07-25" and previous.until == "2026-07-31"
    assert Filters().previous_period() is None


def test_gap_view_finds_prompts_without_own_domain(tmp_path):
    conn = _db(tmp_path)
    rows = queries.owned_domain_gaps(conn, Filters())
    assert rows
    # Sortierung: die schlechteste Abdeckung zuerst — das ist die Arbeitsliste.
    assert rows[0]["runs_with_owned"] <= rows[-1]["runs_with_owned"]
    for row in rows:
        assert row["runs_with_owned"] <= row["runs"]


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
def test_api_endpoints_respond(tmp_path, monkeypatch=None):
    from fastapi.testclient import TestClient

    import geotracker.api.app as app_module

    conn = _db(tmp_path)
    conn.close()
    app_module._config = _config(tmp_path)

    client = TestClient(app_module.app)
    window = "since=2026-07-26&until=2026-08-02"
    for path in [
        "/api/health", "/api/meta", f"/api/overview?{window}", f"/api/timeseries?{window}",
        f"/api/domains?{window}", f"/api/urls?{window}", f"/api/brands?{window}",
        f"/api/prompts?{window}", f"/api/gaps?{window}", f"/api/discoveries?{window}",
        f"/api/breakdown/category?{window}", "/",
    ]:
        assert client.get(path).status_code == 200, path

    assert client.get("/api/breakdown/quatsch").status_code == 400
    assert client.get("/api/prompts/999999").status_code == 404

    # Kein Endpunkt gibt jemals einen Key zurück.
    body = client.get("/api/health").text + client.get("/api/meta").text
    assert "api_key" not in body.lower() and "sk-" not in body


def test_api_filters_are_forwarded(tmp_path):
    from fastapi.testclient import TestClient

    import geotracker.api.app as app_module

    conn = _db(tmp_path)
    conn.close()
    app_module._config = _config(tmp_path)
    client = TestClient(app_module.app)

    everything = client.get("/api/overview").json()["current"]["runs"]
    filtered = client.get("/api/overview?engine=chatgpt&engine=gemini").json()["current"]["runs"]
    assert 0 < filtered < everything


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
