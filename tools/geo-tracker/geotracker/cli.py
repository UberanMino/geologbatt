"""Kommandozeile des GEO-Visibility-Trackers.

    python -m geotracker init-db
    python -m geotracker seed
    python -m geotracker ingest --engine chatgpt --limit 1
    python -m geotracker show-run <id>

Bewusst argparse statt Click/Typer: keine zusätzliche Dependency für Ebene 1.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .classify import reclassify_all
from .config import IMPLEMENTED_ENGINES, load_config
from .db import open_db, today
from .ingest import IngestOutcome, ingest, plan_targets
from .searchapi.client import SearchApiResult
from .seeds import build_classifier, seed_all


def _print(*args: object) -> None:
    print(*args, flush=True)


# ---------------------------------------------------------------------------
# Befehle
# ---------------------------------------------------------------------------
def cmd_init_db(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    tables = [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    _print(f"DB: {config.db_path}")
    _print(f"Tabellen ({len(tables)}): {', '.join(tables)}")
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    result = seed_all(conn)
    for key, value in result.items():
        _print(f"  {key:24} {value}")
    return 0


def cmd_prompts(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    rows = conn.execute(
        """
        SELECT p.id, p.text, p.category, p.country, p.language, p.active,
               (SELECT COUNT(*) FROM runs r WHERE r.prompt_id = p.id) AS runs
          FROM prompts p
         ORDER BY p.category, p.id
        """
    ).fetchall()
    for row in rows:
        flag = " " if row["active"] else "x"
        _print(
            f"[{flag}] #{row['id']:<4} {row['country']}/{row['language']}  "
            f"{row['runs']:>3} Läufe  {row['category'][:28]:<28} {row['text']}"
        )
    _print(f"\n{len(rows)} Prompts.")
    return 0


def _fixture_fetch(path: Path):
    """Gespeicherten Payload abspielen statt zu scrapen.

    Zweck: den Ingest-Pfad end-to-end prüfen, ohne API-Key und ohne Kosten —
    und ohne einen zweiten Codepfad zu bauen, der vom echten abweichen könnte.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))

    def fetch(params: dict[str, str]) -> SearchApiResult:
        return SearchApiResult(
            payload=payload,
            raw_body=json.dumps(payload, ensure_ascii=False),
            http_status=200,
            attempts=1,
            latency_ms=0,
            request_url=f"fixture://{path.name}",
        )

    return fetch


def cmd_ingest(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    classifier = build_classifier(conn)

    if args.engine not in IMPLEMENTED_ENGINES:
        _print(
            f"Engine '{args.engine}' ist noch nicht implementiert. "
            f"Verfügbar: {', '.join(IMPLEMENTED_ENGINES)}."
        )
        return 2

    limit = args.limit if args.limit is not None else config.max_runs_per_invocation
    targets = plan_targets(
        conn,
        engine=args.engine,
        prompt_ids=args.prompt_id,
        category=args.category,
        country=args.country,
        limit=limit,
        skip_existing_today=not args.force,
        run_date=args.run_date,
    )

    if not targets:
        _print("Nichts zu tun (alle passenden Prompts sind heute bereits gelaufen).")
        return 0

    _print(f"{len(targets)} Lauf/Läufe geplant (Engine: {args.engine}, Datum: {args.run_date or today()})")

    if args.dry_run:
        for target in targets:
            _print(f"  #{target.prompt_id} [{target.country}] {target.text}")
        return 0

    fetch = _fixture_fetch(Path(args.fixture)) if args.fixture else None
    if fetch is None and not config.has_searchapi_key:
        _print(
            "FEHLER: SEARCHAPI_API_KEY fehlt. Key in tools/geo-tracker/.env eintragen "
            "(Vorlage: .env.example) oder mit --fixture einen gespeicherten Payload abspielen."
        )
        return 2

    def on_progress(outcome: IngestOutcome) -> None:
        marker = {"success": "ok", "partial": "~ ", "deferred": "..", "error": "!!"}.get(
            outcome.status, "??"
        )
        _print(
            f"  [{marker}] run #{outcome.run_id} prompt #{outcome.target.prompt_id} "
            f"{outcome.citations_cited} zitiert / {outcome.citations_retrieved} abgerufen"
            + (f"  — {outcome.message}" if outcome.message else "")
        )

    outcomes = ingest(
        conn, config, classifier, targets, fetch=fetch, on_progress=on_progress,
        run_date=args.run_date,
    )

    failed = sum(1 for o in outcomes if o.status in ("error", "deferred"))
    _print(f"\nFertig: {len(outcomes)} Läufe, davon {failed} ohne verwertbare Antwort.")
    return 0


def cmd_runs(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    rows = conn.execute(
        """
        SELECT r.id, r.run_date, r.engine, r.country, r.status, r.provider_model,
               length(r.raw_response) AS chars,
               (SELECT COUNT(*) FROM citations c WHERE c.run_id = r.id AND c.origin = 'cited') AS cited,
               (SELECT COUNT(*) FROM citations c WHERE c.run_id = r.id AND c.origin = 'retrieved') AS retrieved,
               p.text
          FROM runs r JOIN prompts p ON p.id = r.prompt_id
         ORDER BY r.id DESC
         LIMIT ?
        """,
        (args.limit,),
    ).fetchall()
    for row in rows:
        _print(
            f"#{row['id']:<4} {row['run_date']} {row['engine']:<10} {row['country']} "
            f"{row['status']:<8} {row['chars'] or 0:>6} Zeichen  "
            f"{row['cited']:>2} zit./{row['retrieved']:>2} abg.  {row['text'][:60]}"
        )
    return 0


def cmd_show_run(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    run = conn.execute(
        """
        SELECT r.*, p.text AS prompt_text, p.category
          FROM runs r JOIN prompts p ON p.id = r.prompt_id
         WHERE r.id = ?
        """,
        (args.run_id,),
    ).fetchone()
    if run is None:
        _print(f"Kein run mit id {args.run_id}.")
        return 1

    _print("=" * 78)
    _print(f"RUN #{run['id']}  ({run['status']})")
    _print("=" * 78)
    for label, value in [
        ("Prompt", f"#{run['prompt_id']} {run['prompt_text']}"),
        ("Kategorie", run["category"]),
        ("Engine", run["engine"]),
        ("Land/Sprache", f"{run['country']} / {run['language']}"),
        ("Datum", run["run_date"]),
        ("Modell", run["provider_model"]),
        ("Websuche", run["web_search_performed"]),
        ("SearchApi-ID", run["provider_search_id"]),
        ("HTTP", f"{run['http_status']} · {run['attempts']} Versuch(e) · {run['latency_ms']} ms"),
        ("Hinweis", run["error"]),
    ]:
        if value not in (None, ""):
            _print(f"{label:>14}: {value}")

    raw = run["raw_response"] or ""
    _print(f"\n--- ROHANTWORT ({len(raw)} Zeichen) " + "-" * 40)
    _print(raw if args.full else raw[:2000] + ("\n[... gekürzt, --full für alles]" if len(raw) > 2000 else ""))

    for origin, heading in (("cited", "ZITIERTE QUELLEN"), ("retrieved", "ABGERUFEN, NICHT ZITIERT")):
        rows = conn.execute(
            """
            SELECT citation_rank, cited_domain, source_type, is_known, cited_url, title
              FROM citations WHERE run_id = ? AND origin = ?
             ORDER BY citation_rank
            """,
            (run["id"], origin),
        ).fetchall()
        if not rows:
            continue
        _print(f"\n--- {heading} ({len(rows)}) " + "-" * 40)
        for row in rows:
            known = "" if row["is_known"] else "  [NEU]"
            _print(
                f"{row['citation_rank']:>3}. {row['cited_domain']:<32} "
                f"{row['source_type']:<13}{known}"
            )
            _print(f"     {row['cited_url']}")
            if row["title"]:
                _print(f"     {row['title'][:100]}")
    return 0


def cmd_domains(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    rows = conn.execute(
        """
        SELECT d.domain, d.source_type, d.is_known, d.first_seen_at,
               COUNT(c.id) AS citations
          FROM domains d
          LEFT JOIN citations c ON c.cited_domain = d.domain AND c.origin = 'cited'
         GROUP BY d.id
        HAVING citations > 0 OR ? = 1
         ORDER BY citations DESC, d.domain
         LIMIT ?
        """,
        (1 if args.all else 0, args.limit),
    ).fetchall()
    for row in rows:
        known = " " if row["is_known"] else "N"
        _print(
            f"{row['citations']:>4}x  [{known}] {row['source_type']:<13} {row['domain']}"
        )
    return 0


# ---------------------------------------------------------------------------
# Ebene 2 — Auswertungs-Layer
# ---------------------------------------------------------------------------
# Die Imports stehen bewusst INNERHALB der Befehle: `geotracker ingest` soll
# laufen, auch wenn das anthropic-SDK gar nicht installiert ist. Ebene 1 darf
# keine Abhängigkeit auf Ebene 2 haben — auch keine beim Import.
def _evaluator(config):
    from .evaluate import EvaluationError, EvaluatorClient

    try:
        return EvaluatorClient(
            api_key=config.anthropic_key,
            max_retries=config.max_retries,
            timeout=float(config.request_timeout),
        )
    except EvaluationError as exc:
        _print(f"FEHLER: {exc}")
        return None


def _report(result, outcome) -> None:
    if outcome is None:
        _print(f"  [!!] run #{result.run_id}: {result.error}")
        return
    position = outcome.logbatt_position or "-"
    _print(
        f"  [ok] run #{result.run_id}: {outcome.mentions} Marken, "
        f"LogBATT {'Pos. ' + str(position) if outcome.logbatt_mentioned else 'nicht genannt'}, "
        f"SoV {outcome.share_of_voice:.0%}, {outcome.sentiment or 'kein Sentiment'}"
        + (", Problem-Narrativ" if outcome.problem_narrative_anchored else "")
    )
    for name in outcome.new_brands:
        _print(f"       + neue Marke entdeckt: {name}")
    for warning in outcome.warnings:
        _print(f"       ~ {warning}")
    if result.usage:
        cache_read = result.usage.get("cache_read_input_tokens", 0)
        cache_write = result.usage.get("cache_creation_input_tokens", 0)
        if cache_read or cache_write:
            _print(f"       cache: {cache_read} gelesen / {cache_write} geschrieben")


def cmd_evaluate(args: argparse.Namespace) -> int:
    from .evaluate import EVALUATOR_VERSION, collect_batch, evaluate_sync, select_runs
    from .evaluate import submit_batch as submit
    from .evaluate import wait_for_batch

    config = load_config()
    conn = open_db(config.db_path)

    targets = select_runs(
        conn,
        since=args.since,
        until=args.until,
        engine=args.engine,
        category=args.category,
        country=args.country,
        prompt_ids=args.prompt_id,
        run_ids=args.run_id,
        limit=args.limit,
        re_run=args.re_run,
    )

    if not targets:
        _print(
            f"Keine auswertbaren Läufe (Version {EVALUATOR_VERSION}). "
            "Mit --re-run auch bereits ausgewertete Läufe erneut auswerten."
        )
        return 0

    _print(f"{len(targets)} Lauf/Läufe zur Auswertung (Version {EVALUATOR_VERSION})")
    if args.dry_run:
        from .evaluate import build_system_prompt

        system_prompt = build_system_prompt(conn)
        for target in targets:
            _print(f"  run #{target.run_id}  {len(target.raw_response)} Zeichen Rohantwort")
        # Sichtbar machen, ob der Systemprompt überhaupt cachebar ist:
        # Claude Haiku 4.5 cached erst ab 4096 Tokens Prefix (siehe README).
        _print(
            f"\nSystemprompt (Cache-Prefix): {len(system_prompt)} Zeichen "
            f"(~{round(len(system_prompt) / 3.3)} Tokens geschätzt, Caching ab 4096)"
        )
        return 0

    client = _evaluator(config)
    if client is None:
        return 2

    if args.sync:
        applied, failed = evaluate_sync(conn, client, targets, on_result=_report)
    else:
        batch_id = submit(conn, client, targets)
        _print(f"Batch angelegt: {batch_id} (50 % günstiger als Einzelabrufe)")
        if args.no_wait:
            _print(f"Später einsammeln mit: geotracker evaluate-collect {batch_id}")
            return 0
        wait_for_batch(
            client, batch_id,
            poll_seconds=args.poll_seconds,
            on_poll=lambda status: _print(f"  Batch-Status: {status}"),
        )
        applied, failed = collect_batch(conn, client, batch_id, on_result=_report)

    _print(f"\nFertig: {len(applied)} ausgewertet, {len(failed)} fehlgeschlagen.")
    return 0


def cmd_evaluate_collect(args: argparse.Namespace) -> int:
    from .evaluate import collect_batch

    config = load_config()
    conn = open_db(config.db_path)
    client = _evaluator(config)
    if client is None:
        return 2

    status = client.batch_status(args.batch_id)
    if status != "ended":
        _print(f"Batch {args.batch_id} ist noch '{status}' — später erneut versuchen.")
        return 1

    applied, failed = collect_batch(conn, client, args.batch_id, on_result=_report)
    _print(f"\nFertig: {len(applied)} ausgewertet, {len(failed)} fehlgeschlagen.")
    return 0


def cmd_evaluations(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)

    if args.run_id:
        row = conn.execute(
            """
            SELECT e.*, p.text AS prompt_text, r.engine, r.run_date
              FROM evaluations e
              JOIN runs r ON r.id = e.run_id
              JOIN prompts p ON p.id = r.prompt_id
             WHERE e.run_id = ? AND e.is_current = 1
            """,
            (args.run_id,),
        ).fetchone()
        if row is None:
            _print(f"Keine aktuelle Auswertung für run {args.run_id}.")
            return 1

        _print("=" * 78)
        _print(f"AUSWERTUNG zu run #{row['run_id']}  ({row['engine']}, {row['run_date']})")
        _print("=" * 78)
        _print(f"        Prompt: {row['prompt_text']}")
        _print(f"       LogBATT: {'genannt' if row['logbatt_mentioned'] else 'NICHT genannt'}"
               + (f", Position {row['logbatt_position']}" if row["logbatt_position"] else ""))
        _print(f"     Sentiment: {row['sentiment'] or '–'}")
        _print(f"Problem-Narrativ: {'ja' if row['problem_narrative_anchored'] else 'nein'}")
        _print(f"Share of Voice: {row['share_of_voice']:.0%}")
        _print(f"        Modell: {row['model']}  ·  Version {row['evaluator_version']}")

        mentions = conn.execute(
            """
            SELECT m.mention_rank, m.mention_text, b.name, b.is_known, b.is_own_brand, b.is_competitor
              FROM brand_mentions m JOIN brands b ON b.id = m.brand_id
             WHERE m.evaluation_id = ?
             ORDER BY m.mention_rank
            """,
            (row["id"],),
        ).fetchall()
        _print(f"\n--- MARKEN-NENNUNGEN ({len(mentions)}, Reihenfolge im Antworttext) ---")
        for mention in mentions:
            flags = []
            if mention["is_own_brand"]:
                flags.append("eigene Marke")
            elif not mention["is_competitor"]:
                flags.append("Partner")
            if not mention["is_known"]:
                flags.append("NEU")
            suffix = f"  [{', '.join(flags)}]" if flags else ""
            _print(f"{mention['mention_rank']:>3}. {mention['name']:<28} „{mention['mention_text']}\"{suffix}")

        if args.raw:
            _print("\n--- ROHE MODELLAUSGABE ---")
            _print(row["raw_classifier_output"])
        return 0

    rows = conn.execute(
        """
        SELECT e.run_id, e.logbatt_mentioned, e.logbatt_position, e.sentiment,
               e.problem_narrative_anchored, e.share_of_voice, e.evaluator_version,
               r.engine, r.run_date, p.text
          FROM evaluations e
          JOIN runs r ON r.id = e.run_id
          JOIN prompts p ON p.id = r.prompt_id
         WHERE e.is_current = 1
         ORDER BY e.run_id DESC
         LIMIT ?
        """,
        (args.limit,),
    ).fetchall()
    for row in rows:
        marker = f"#{row['logbatt_position']}" if row["logbatt_mentioned"] else "–"
        _print(
            f"run #{row['run_id']:<4} {row['run_date']} {row['engine']:<10} "
            f"LogBATT {marker:<3} SoV {row['share_of_voice']:>4.0%} "
            f"{(row['sentiment'] or '-'):<9}"
            f"{'PN' if row['problem_narrative_anchored'] else '  '}  {row['text'][:48]}"
        )
    _print(f"\n{len(rows)} Auswertungen.")
    return 0


# ---------------------------------------------------------------------------
# Schritt 3 — Import, Dashboard, Scheduler
# ---------------------------------------------------------------------------
def cmd_import_peec(args: argparse.Namespace) -> int:
    from .importers.peec import import_directory

    config = load_config()
    conn = open_db(config.db_path)
    directory = Path(args.directory)
    if not directory.is_dir():
        _print(f"Kein Verzeichnis: {directory}")
        return 2

    stats = import_directory(conn, build_classifier(conn), directory, category=args.category)
    for label, value in vars(stats).items():
        _print(f"  {label:14} {value}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    _print(f"Dashboard: http://{args.host}:{args.port}/")
    _print(f"API-Doku:  http://{args.host}:{args.port}/docs")
    uvicorn.run(
        "geotracker.api.app:app", host=args.host, port=args.port, reload=args.reload,
        log_level="info",
    )
    return 0


def cmd_schedule(args: argparse.Namespace) -> int:
    import logging

    from . import scheduler

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()

    if args.once:
        summary = scheduler.run_daily(config, evaluate=not args.no_evaluate)
        _print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    scheduler.start(args.cron, evaluate=not args.no_evaluate)
    return 0


def cmd_reclassify(args: argparse.Namespace) -> int:
    config = load_config()
    conn = open_db(config.db_path)
    seed_all(conn)  # Seeds zuerst aktualisieren, dann neu klassifizieren
    result = reclassify_all(conn, build_classifier(conn))
    _print(f"Domains geändert: {result['domains_changed']}, Citations aktualisiert: {result['citations_touched']}")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geotracker", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Schema anlegen/migrieren").set_defaults(func=cmd_init_db)
    sub.add_parser("seed", help="Brands, Domains und Prompts seeden (idempotent)").set_defaults(func=cmd_seed)
    sub.add_parser("prompts", help="Prompts auflisten").set_defaults(func=cmd_prompts)

    p_ingest = sub.add_parser("ingest", help="Ebene 1: scrapen und roh speichern")
    p_ingest.add_argument("--engine", default="chatgpt")
    p_ingest.add_argument("--prompt-id", type=int, action="append", help="mehrfach möglich")
    p_ingest.add_argument("--category")
    p_ingest.add_argument("--country")
    p_ingest.add_argument("--limit", type=int, help="max. Läufe (Default: GEOTRACKER_MAX_RUNS)")
    p_ingest.add_argument("--run-date", help="YYYY-MM-DD, Default: heute (UTC)")
    p_ingest.add_argument("--force", action="store_true", help="auch laufen, wenn heute schon erfolgreich")
    p_ingest.add_argument("--dry-run", action="store_true")
    p_ingest.add_argument("--fixture", help="gespeicherten Payload abspielen statt zu scrapen")
    p_ingest.set_defaults(func=cmd_ingest)

    p_runs = sub.add_parser("runs", help="Läufe auflisten")
    p_runs.add_argument("--limit", type=int, default=30)
    p_runs.set_defaults(func=cmd_runs)

    p_show = sub.add_parser("show-run", help="Einen Lauf inkl. Citations anzeigen")
    p_show.add_argument("run_id", type=int)
    p_show.add_argument("--full", action="store_true", help="Rohantwort ungekürzt")
    p_show.set_defaults(func=cmd_show_run)

    p_domains = sub.add_parser("domains", help="Domain-Ranking (zitierte Quellen)")
    p_domains.add_argument("--limit", type=int, default=40)
    p_domains.add_argument("--all", action="store_true", help="auch nie zitierte Seed-Domains")
    p_domains.set_defaults(func=cmd_domains)

    sub.add_parser(
        "reclassify-domains",
        help="source_type aller Domains/Citations neu berechnen (ohne erneutes Scrapen)",
    ).set_defaults(func=cmd_reclassify)

    # --- Ebene 2 ----------------------------------------------------------
    p_eval = sub.add_parser(
        "evaluate",
        help="Ebene 2: gespeicherte Rohantworten auswerten (wiederholbar, ohne Scrapen)",
    )
    p_eval.add_argument("--since", help="run_date >= YYYY-MM-DD")
    p_eval.add_argument("--until", help="run_date <= YYYY-MM-DD")
    p_eval.add_argument("--engine")
    p_eval.add_argument("--category")
    p_eval.add_argument("--country")
    p_eval.add_argument("--prompt-id", type=int, action="append", help="mehrfach möglich")
    p_eval.add_argument("--run-id", type=int, action="append", help="mehrfach möglich")
    p_eval.add_argument("--limit", type=int)
    p_eval.add_argument(
        "--re-run",
        action="store_true",
        help="auch bereits ausgewertete Läufe erneut auswerten (neue evaluations-Zeile)",
    )
    p_eval.add_argument(
        "--sync",
        action="store_true",
        help="einzeln und sofort statt über die Batch API (teurer, aber ohne Wartezeit)",
    )
    p_eval.add_argument("--no-wait", action="store_true", help="Batch nur anlegen, nicht abwarten")
    p_eval.add_argument("--poll-seconds", type=int, default=30)
    p_eval.add_argument("--dry-run", action="store_true")
    p_eval.set_defaults(func=cmd_evaluate)

    p_collect = sub.add_parser(
        "evaluate-collect", help="Ergebnisse eines zuvor angelegten Batches einsammeln"
    )
    p_collect.add_argument("batch_id")
    p_collect.set_defaults(func=cmd_evaluate_collect)

    p_evals = sub.add_parser("evaluations", help="Auswertungen anzeigen")
    p_evals.add_argument("--run-id", type=int, help="Detailansicht eines Laufs")
    p_evals.add_argument("--limit", type=int, default=30)
    p_evals.add_argument("--raw", action="store_true", help="rohe Modellausgabe mit anzeigen")
    p_evals.set_defaults(func=cmd_evaluations)

    # --- Schritt 3 --------------------------------------------------------
    p_import = sub.add_parser(
        "import-peec", help="bestehende Peec-Chat-Exporte als historische Läufe importieren"
    )
    p_import.add_argument("directory", help="Ordner mit den *.md-Chat-Exporten")
    p_import.add_argument("--category", default="Peec-Import",
                          help="Kategorie für Prompts, die noch nicht existieren")
    p_import.set_defaults(func=cmd_import_peec)

    p_serve = sub.add_parser("serve", help="Dashboard + REST-API starten")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")
    p_serve.set_defaults(func=cmd_serve)

    p_sched = sub.add_parser("schedule", help="täglichen Lauf starten (Ebene 1 + Ebene 2)")
    p_sched.add_argument("--cron", default="0 3 * * *", help="5-Feld-Cron, Default 03:00")
    p_sched.add_argument("--once", action="store_true", help="einmal sofort statt Dauerbetrieb")
    p_sched.add_argument("--no-evaluate", action="store_true", help="nur Ebene 1")
    p_sched.set_defaults(func=cmd_schedule)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except sqlite3.Error as exc:
        _print(f"DB-Fehler: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
