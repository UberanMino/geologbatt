"""REST-API des Dashboards (FastAPI).

Die gesamte Filter-/Visualisierungslogik liegt im Frontend; hier gibt es nur
JSON. Secrets bleiben serverseitig — kein Endpunkt gibt einen Provider-Key
zurück, und das Frontend braucht keinen.

Start:  python3 -m geotracker serve  (oder: uvicorn geotracker.api.app:app)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..config import load_config
from ..db import open_db
from . import queries
from .queries import Filters

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="GEO-Visibility-Tracker",
    description="Dashboard-API für das LogBATT-GEO-Monitoring.",
    version="0.3.0",
)

_config = load_config()


def get_conn() -> sqlite3.Connection:
    """Pro Request eine Verbindung — SQLite-Verbindungen sind nicht threadsicher."""
    conn = open_db(_config.db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_filters(
    since: str | None = None,
    until: str | None = None,
    engine: list[str] = Query(default=[]),
    country: list[str] = Query(default=[]),
    language: list[str] = Query(default=[]),
    category: list[str] = Query(default=[]),
    prompt_id: list[int] = Query(default=[]),
    source: list[str] = Query(default=[]),
    domain: list[str] = Query(default=[]),
    url: str | None = None,
    brand_id: list[int] = Query(default=[]),
) -> Filters:
    """Ein Filter-Objekt für alle Endpunkte — Facetten UND-verknüpft."""
    return Filters(
        since=since, until=until, engines=engine, countries=country, languages=language,
        categories=category, prompt_ids=prompt_id, sources=source, domains=domain,
        url=url, brand_ids=brand_id,
    )


# ---------------------------------------------------------------------------
@app.get("/api/meta")
def meta(conn: sqlite3.Connection = Depends(get_conn)) -> dict[str, Any]:
    """Optionen für die Filterleiste."""
    return queries.filter_options(conn)


@app.get("/api/overview")
def overview(
    filters: Filters = Depends(get_filters), conn: sqlite3.Connection = Depends(get_conn)
) -> dict[str, Any]:
    """KPIs der gefilterten Menge inkl. Delta zum gleich langen Vorzeitraum."""
    return queries.overview(conn, filters)


@app.get("/api/timeseries")
def timeseries(
    filters: Filters = Depends(get_filters), conn: sqlite3.Connection = Depends(get_conn)
) -> list[dict[str, Any]]:
    return queries.timeseries(conn, filters)


@app.get("/api/breakdown/{dimension}")
def breakdown(
    dimension: str,
    filters: Filters = Depends(get_filters),
    conn: sqlite3.Connection = Depends(get_conn),
) -> list[dict[str, Any]]:
    """dimension: category | country | engine | language | source"""
    try:
        return queries.breakdown(conn, filters, dimension)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/domains")
def domains(
    filters: Filters = Depends(get_filters),
    limit: int = 50,
    source_type: str | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
) -> list[dict[str, Any]]:
    return queries.domain_ranking(conn, filters, limit=limit, source_type=source_type)


@app.get("/api/urls")
def urls(
    filters: Filters = Depends(get_filters),
    limit: int = 50,
    conn: sqlite3.Connection = Depends(get_conn),
) -> list[dict[str, Any]]:
    return queries.url_ranking(conn, filters, limit=limit)


@app.get("/api/gaps")
def gaps(
    filters: Filters = Depends(get_filters), conn: sqlite3.Connection = Depends(get_conn)
) -> list[dict[str, Any]]:
    """Eigen-Domain-Gap: Prompts mit Relevanz, aber ohne eigene zitierte Domain."""
    return queries.owned_domain_gaps(conn, filters)


@app.get("/api/brands")
def brands(
    filters: Filters = Depends(get_filters),
    limit: int = 50,
    conn: sqlite3.Connection = Depends(get_conn),
) -> list[dict[str, Any]]:
    return queries.brand_leaderboard(conn, filters, limit=limit)


@app.get("/api/prompts")
def prompts(
    filters: Filters = Depends(get_filters), conn: sqlite3.Connection = Depends(get_conn)
) -> list[dict[str, Any]]:
    return queries.prompt_table(conn, filters)


# Der Pfadparameter heißt bewusst `pid` und nicht `prompt_id`: `prompt_id` ist
# bereits ein Query-Filter in get_filters, und FastAPI kann denselben Namen
# nicht gleichzeitig als Pfad- und Query-Parameter binden.
@app.get("/api/prompts/{pid}")
def prompt_detail(
    pid: int,
    filters: Filters = Depends(get_filters),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Volle Antwort-Historie inkl. Datum, Marken und zitierten Quellen."""
    result = queries.prompt_history(conn, filters, pid)
    if result["prompt"] is None:
        raise HTTPException(status_code=404, detail="Prompt nicht gefunden")
    return result


@app.get("/api/discoveries")
def discoveries(
    filters: Filters = Depends(get_filters),
    days: int = 14,
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    return queries.discoveries(conn, filters, days=days)


@app.get("/api/health")
def health(conn: sqlite3.Connection = Depends(get_conn)) -> dict[str, Any]:
    runs = conn.execute("SELECT COUNT(*) c FROM runs").fetchone()["c"]
    return {"status": "ok", "db": str(_config.db_path), "runs": runs}


# --- Frontend --------------------------------------------------------------
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
