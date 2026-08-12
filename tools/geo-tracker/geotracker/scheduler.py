"""Täglicher Lauf: alle Engines scrapen (Ebene 1), danach auswerten (Ebene 2).

Reihenfolge ist Absicht: erst wird die Wahrheit gesichert, dann ausgewertet.
Fällt Ebene 2 aus, sind die Rohdaten des Tages trotzdem vollständig — und der
nächste `evaluate`-Lauf holt sie nach, weil noch nicht ausgewertete Läufe
automatisch fällig bleiben.

    python3 -m geotracker schedule                 # täglich 03:00 (Default)
    python3 -m geotracker schedule --cron "30 4 * * *"
    python3 -m geotracker schedule --once          # sofort einmal ausführen
"""

from __future__ import annotations

import logging
from typing import Callable

from .classify import Classifier
from .config import Config, load_config
from .db import open_db, today
from .ingest import ingest, plan_targets
from .seeds import build_classifier

log = logging.getLogger("geotracker.scheduler")


def run_daily(config: Config, *, engines: list[str] | None = None, evaluate: bool = True) -> dict:
    """Ein kompletter Tageslauf. Gibt eine Zusammenfassung zurück."""
    conn = open_db(config.db_path)
    classifier: Classifier = build_classifier(conn)
    summary: dict = {"date": today(), "engines": {}, "evaluated": 0, "failed_evaluations": 0}

    for engine in engines or list(config.engines_for_scheduler):
        targets = plan_targets(conn, engine=engine, limit=config.max_runs_per_invocation)
        if not targets:
            summary["engines"][engine] = {"planned": 0}
            log.info("%s: nichts zu tun", engine)
            continue

        log.info("%s: %d Läufe", engine, len(targets))
        outcomes = ingest(conn, config, classifier, targets)
        summary["engines"][engine] = {
            "planned": len(targets),
            "success": sum(1 for o in outcomes if o.status == "success"),
            "partial": sum(1 for o in outcomes if o.status == "partial"),
            "deferred": sum(1 for o in outcomes if o.status == "deferred"),
            "error": sum(1 for o in outcomes if o.status == "error"),
        }

    if evaluate and config.anthropic_key:
        # Import bleibt lokal: ohne anthropic-SDK soll der Ingest-Teil des
        # Tageslaufs trotzdem durchlaufen.
        from .evaluate import EvaluatorClient, collect_batch, select_runs, submit_batch
        from .evaluate import wait_for_batch

        targets = select_runs(conn)
        if targets:
            log.info("Auswertung: %d Läufe (Batch API)", len(targets))
            client = EvaluatorClient(
                api_key=config.anthropic_key,
                max_retries=config.max_retries,
                timeout=float(config.request_timeout),
            )
            batch_id = submit_batch(conn, client, targets)
            wait_for_batch(client, batch_id)
            applied, failed = collect_batch(conn, client, batch_id)
            summary["evaluated"] = len(applied)
            summary["failed_evaluations"] = len(failed)
    elif evaluate:
        log.warning("ANTHROPIC_API_KEY fehlt — Ebene 2 übersprungen, Rohdaten sind gesichert.")

    conn.close()
    return summary


def start(
    cron: str = "0 3 * * *",
    *,
    engines: list[str] | None = None,
    evaluate: bool = True,
    on_run: Callable[[dict], None] | None = None,
) -> None:
    """Blockierender Scheduler. `cron` im Standard-5-Feld-Format."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    config = load_config()
    scheduler = BlockingScheduler(timezone="Europe/Berlin")

    def job() -> None:
        try:
            summary = run_daily(config, engines=engines, evaluate=evaluate)
            log.info("Tageslauf fertig: %s", summary)
            if on_run:
                on_run(summary)
        except Exception:
            # Ein gescheiterter Tag darf den Scheduler nicht beenden.
            log.exception("Tageslauf fehlgeschlagen")

    scheduler.add_job(job, CronTrigger.from_crontab(cron), id="daily", max_instances=1)
    log.info("Scheduler gestartet (cron: %s, Zeitzone Europe/Berlin)", cron)
    scheduler.start()
