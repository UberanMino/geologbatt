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
