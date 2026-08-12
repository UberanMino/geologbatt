"""Ebene 1 — Rohdaten-Ingestion (Source of Truth).

Der einzige Schreibpfad für runs + citations. Regeln, die hier nicht verletzt
werden dürfen:

  1. Der volle Antworttext und JEDE einzelne Quelle werden roh gespeichert.
  2. Es gibt keinerlei Abhängigkeit vom Auswertungs-Layer. Kein Import aus
     Ebene 2, kein Anthropic-Aufruf, nichts. Fällt Ebene 2 aus oder ist sie
     abgeschaltet, ist Ebene 1 trotzdem vollständig.
  3. Nichts wird überschrieben: jeder Lauf legt einen NEUEN run an.
  4. Auch Fehlläufe werden gespeichert (status = error/deferred) — inklusive
     dem, was vom Payload da war. "Nicht gespeichert" wäre ein Datenverlust,
     den wir später nicht mehr rekonstruieren können.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .classify import Classifier, register_domain
from .config import Config
from .db import today, utcnow
from .searchapi.client import SearchApiClient, SearchApiError, SearchApiResult
from .searchapi.parsers import EngineNotImplemented, build_params, parse_response


@dataclass
class RunTarget:
    """Ein geplanter Lauf: Prompt x Engine x Land."""

    prompt_id: int
    text: str
    category: str
    country: str
    language: str
    engine: str


@dataclass
class IngestOutcome:
    target: RunTarget
    run_id: int | None
    status: str
    citations_cited: int = 0
    citations_retrieved: int = 0
    message: str | None = None


def plan_targets(
    conn: sqlite3.Connection,
    *,
    engine: str,
    prompt_ids: Iterable[int] | None = None,
    category: str | None = None,
    country: str | None = None,
    limit: int | None = None,
    skip_existing_today: bool = True,
    run_date: str | None = None,
) -> list[RunTarget]:
    """Welche Läufe stehen an? Filter sind UND-verknüpft."""
    run_date = run_date or today()
    sql = ["SELECT id, text, category, country, language, engines FROM prompts WHERE active = 1"]
    params: list[Any] = []

    if prompt_ids:
        ids = list(prompt_ids)
        sql.append(f"AND id IN ({','.join('?' * len(ids))})")
        params.extend(ids)
    if category:
        sql.append("AND category = ?")
        params.append(category)
    if country:
        sql.append("AND country = ?")
        params.append(country.upper())

    sql.append("ORDER BY id")

    targets: list[RunTarget] = []
    for row in conn.execute(" ".join(sql), params):
        engines = json.loads(row["engines"])
        if engine not in engines:
            continue

        if skip_existing_today:
            # Deduplizierung "ein erfolgreicher Lauf pro Prompt/Engine/Tag".
            # Fehlgeschlagene Läufe zählen NICHT als erledigt, damit ein
            # Nachlauf sie erneut versucht.
            existing = conn.execute(
                """
                SELECT 1 FROM runs
                 WHERE prompt_id = ? AND engine = ? AND run_date = ?
                   AND status IN ('success', 'partial')
                 LIMIT 1
                """,
                (row["id"], engine, run_date),
            ).fetchone()
            if existing:
                continue

        targets.append(
            RunTarget(
                prompt_id=row["id"],
                text=row["text"],
                category=row["category"],
                country=row["country"],
                language=row["language"],
                engine=engine,
            )
        )
        if limit is not None and len(targets) >= limit:
            break

    return targets


def _insert_run(conn: sqlite3.Connection, target: RunTarget, run_date: str, **fields: Any) -> int:
    columns = [
        "prompt_id", "engine", "country", "language", "run_date", "status",
        "raw_response", "raw_payload", "provider_search_id", "provider_model",
        "web_search_performed", "request_url", "http_status", "attempts",
        "latency_ms", "error", "requested_at", "completed_at",
    ]
    values: dict[str, Any] = {
        "prompt_id": target.prompt_id,
        "engine": target.engine,
        "country": target.country,
        "language": target.language,
        "run_date": run_date,
        "attempts": 1,
    }
    values.update(fields)

    placeholders = ", ".join("?" * len(columns))
    cursor = conn.execute(
        f"INSERT INTO runs ({', '.join(columns)}) VALUES ({placeholders})",
        [values.get(column) for column in columns],
    )
    return int(cursor.lastrowid)


def _store_citations(
    conn: sqlite3.Connection,
    classifier: Classifier,
    run_id: int,
    citations: list[Any],
    now: str,
) -> tuple[int, int]:
    cited = retrieved = 0
    for citation in citations:
        source_type, is_known = register_domain(conn, classifier, citation.cited_domain, now)
        conn.execute(
            """
            INSERT INTO citations (
                run_id, cited_url, cited_domain, title, snippet, citation_rank,
                source_type, is_known, origin, provider_source, provider_index,
                ref_id, published_date, raw_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                citation.cited_url,
                citation.cited_domain,
                citation.title,
                citation.snippet,
                citation.citation_rank,
                source_type,
                int(is_known),
                citation.origin,
                citation.provider_source,
                citation.provider_index,
                citation.ref_id,
                citation.published_date,
                json.dumps(citation.raw, ensure_ascii=False),
                now,
            ),
        )
        if citation.origin == "cited":
            cited += 1
        else:
            retrieved += 1
    return cited, retrieved


def ingest_target(
    conn: sqlite3.Connection,
    config: Config,
    classifier: Classifier,
    target: RunTarget,
    *,
    fetch: Callable[[dict[str, str]], SearchApiResult] | None = None,
    run_date: str | None = None,
) -> IngestOutcome:
    """Einen einzelnen Lauf ausführen und vollständig persistieren.

    `fetch` ist injizierbar, damit derselbe Codepfad mit einem gespeicherten
    Payload (Fixture) getestet werden kann — ohne zweiten Ingest-Pfad, der
    auseinanderlaufen könnte.
    """
    run_date = run_date or today()
    requested_at = utcnow()

    if fetch is None:
        client = SearchApiClient(
            api_key=config.searchapi_key,
            base_url=config.searchapi_base_url,
            timeout=config.request_timeout,
            max_retries=config.max_retries,
            retry_backoff=config.retry_backoff,
        )
        fetch = client.search

    try:
        params = build_params(
            target.engine, target.text, web_search=config.chatgpt_web_search
        )
    except EngineNotImplemented as exc:
        return IngestOutcome(target=target, run_id=None, status="skipped", message=str(exc))

    try:
        result = fetch(params)
    except SearchApiError as exc:
        # Teil-Ergebnis retten: der Fehler-Body ist oft eine JSON-Fehlermeldung
        # von SearchApi und gehört zur Wahrheit dazu.
        run_id = _insert_run(
            conn, target, run_date,
            status="error",
            raw_payload=exc.body,
            http_status=exc.status,
            error=str(exc),
            requested_at=requested_at,
            completed_at=utcnow(),
        )
        conn.commit()
        return IngestOutcome(target=target, run_id=run_id, status="error", message=str(exc))

    parsed = parse_response(target.engine, result.payload)
    now = utcnow()

    run_id = _insert_run(
        conn, target, run_date,
        status=parsed.status,
        raw_response=parsed.raw_response,
        raw_payload=json.dumps(result.payload, ensure_ascii=False),
        provider_search_id=parsed.provider_search_id,
        provider_model=parsed.provider_model,
        web_search_performed=(
            None if parsed.web_search_performed is None else int(parsed.web_search_performed)
        ),
        request_url=result.request_url,
        http_status=result.http_status,
        attempts=result.attempts,
        latency_ms=result.latency_ms,
        error=parsed.note,
        requested_at=requested_at,
        completed_at=now,
    )

    cited, retrieved = _store_citations(conn, classifier, run_id, parsed.citations, now)
    conn.commit()

    return IngestOutcome(
        target=target,
        run_id=run_id,
        status=parsed.status,
        citations_cited=cited,
        citations_retrieved=retrieved,
        message=parsed.note,
    )


def ingest(
    conn: sqlite3.Connection,
    config: Config,
    classifier: Classifier,
    targets: list[RunTarget],
    *,
    fetch: Callable[[dict[str, str]], SearchApiResult] | None = None,
    on_progress: Callable[[IngestOutcome], None] | None = None,
    run_date: str | None = None,
) -> list[IngestOutcome]:
    """Läufe sequenziell und gedrosselt abarbeiten.

    Sequenziell ist Absicht: die Engines sind Scraping-Ziele, paralleles Feuern
    provoziert Rate-Limits und verfälscht die Zeitreihe.
    """
    outcomes: list[IngestOutcome] = []
    for index, target in enumerate(targets):
        if index and config.throttle_seconds > 0:
            time.sleep(config.throttle_seconds)
        outcome = ingest_target(
            conn, config, classifier, target, fetch=fetch, run_date=run_date
        )
        outcomes.append(outcome)
        if on_progress:
            on_progress(outcome)
    return outcomes
