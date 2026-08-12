"""Ebene 2 — Orchestrierung: welche Läufe, Sync oder Batch, dann anwenden.

Der Layer liest ausschließlich gespeicherte Ebene-1-Rohdaten. Er scrapt nie.
Deshalb lässt er sich beliebig oft auf denselben Läufen neu ausführen —
genau das ist der Sinn von `--re-run`, wenn sich Systemprompt oder
Ableitungslogik geändert haben.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .apply import AppliedEvaluation, BrandResolver, apply_evaluation
from .client import EvaluationResult, EvaluatorClient
from .prompt import EVALUATOR_VERSION, build_system_prompt, build_user_message


@dataclass
class EvalTarget:
    run_id: int
    prompt_text: str
    raw_response: str


def select_runs(
    conn: sqlite3.Connection,
    *,
    since: str | None = None,
    until: str | None = None,
    engine: str | None = None,
    category: str | None = None,
    country: str | None = None,
    prompt_ids: Iterable[int] | None = None,
    run_ids: Iterable[int] | None = None,
    limit: int | None = None,
    re_run: bool = False,
) -> list[EvalTarget]:
    """Auswertbare Läufe auswählen. Filter sind UND-verknüpft."""
    sql = [
        """
        SELECT r.id, r.raw_response, p.text AS prompt_text
          FROM runs r
          JOIN prompts p ON p.id = r.prompt_id
         WHERE r.raw_response IS NOT NULL
           AND r.raw_response != ''
           AND r.status IN ('success', 'partial')
        """
    ]
    params: list[Any] = []

    if since:
        sql.append("AND r.run_date >= ?")
        params.append(since)
    if until:
        sql.append("AND r.run_date <= ?")
        params.append(until)
    if engine:
        sql.append("AND r.engine = ?")
        params.append(engine)
    if country:
        sql.append("AND r.country = ?")
        params.append(country.upper())
    if category:
        sql.append("AND p.category = ?")
        params.append(category)
    if prompt_ids:
        ids = list(prompt_ids)
        sql.append(f"AND r.prompt_id IN ({','.join('?' * len(ids))})")
        params.extend(ids)
    if run_ids:
        ids = list(run_ids)
        sql.append(f"AND r.id IN ({','.join('?' * len(ids))})")
        params.extend(ids)

    if not re_run:
        # Schon mit DIESER Version ausgewertet -> überspringen. Eine neue
        # evaluator_version macht alle Läufe automatisch wieder fällig, ohne
        # dass jemand etwas zurücksetzen muss.
        sql.append(
            """
            AND NOT EXISTS (
                SELECT 1 FROM evaluations e
                 WHERE e.run_id = r.id
                   AND e.is_current = 1
                   AND e.evaluator_version = ?
            )
            """
        )
        params.append(EVALUATOR_VERSION)

    sql.append("ORDER BY r.id")
    if limit is not None:
        sql.append("LIMIT ?")
        params.append(limit)

    return [
        EvalTarget(
            run_id=row["id"], prompt_text=row["prompt_text"], raw_response=row["raw_response"]
        )
        for row in conn.execute(" ".join(sql), params)
    ]


def _apply_results(
    conn: sqlite3.Connection,
    resolver: BrandResolver,
    results: Iterable[EvaluationResult],
    on_result: Callable[[EvaluationResult, AppliedEvaluation | None], None] | None,
) -> tuple[list[AppliedEvaluation], list[EvaluationResult]]:
    applied: list[AppliedEvaluation] = []
    failed: list[EvaluationResult] = []

    for result in results:
        if not result.ok:
            failed.append(result)
            if on_result:
                on_result(result, None)
            continue
        outcome = apply_evaluation(
            conn, resolver, result.run_id, result.parsed or {}, result.raw_output, result.model
        )
        applied.append(outcome)
        if on_result:
            on_result(result, outcome)

    return applied, failed


def evaluate_sync(
    conn: sqlite3.Connection,
    client: EvaluatorClient,
    targets: list[EvalTarget],
    *,
    on_result: Callable[[EvaluationResult, AppliedEvaluation | None], None] | None = None,
) -> tuple[list[AppliedEvaluation], list[EvaluationResult]]:
    system_prompt = build_system_prompt(conn)
    resolver = BrandResolver(conn)

    def results() -> Iterable[EvaluationResult]:
        for target in targets:
            yield client.evaluate_sync(
                target.run_id,
                system_prompt,
                build_user_message(target.prompt_text, target.raw_response),
            )

    return _apply_results(conn, resolver, results(), on_result)


def submit_batch(
    conn: sqlite3.Connection, client: EvaluatorClient, targets: list[EvalTarget]
) -> str:
    system_prompt = build_system_prompt(conn)
    return client.submit_batch(
        (
            target.run_id,
            system_prompt,
            build_user_message(target.prompt_text, target.raw_response),
        )
        for target in targets
    )


def wait_for_batch(
    client: EvaluatorClient,
    batch_id: str,
    *,
    poll_seconds: int = 30,
    timeout_seconds: int = 24 * 3600,
    on_poll: Callable[[str], None] | None = None,
) -> str:
    """Bis `ended` pollen. Batches laufen meist unter einer Stunde, garantiert < 24 h."""
    deadline = time.monotonic() + timeout_seconds
    while True:
        status = client.batch_status(batch_id)
        if on_poll:
            on_poll(status)
        if status == "ended":
            return status
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Batch {batch_id} nach {timeout_seconds}s nicht beendet.")
        time.sleep(poll_seconds)


def collect_batch(
    conn: sqlite3.Connection,
    client: EvaluatorClient,
    batch_id: str,
    *,
    on_result: Callable[[EvaluationResult, AppliedEvaluation | None], None] | None = None,
) -> tuple[list[AppliedEvaluation], list[EvaluationResult]]:
    resolver = BrandResolver(conn)
    return _apply_results(conn, resolver, client.collect_batch(batch_id), on_result)
