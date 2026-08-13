"""Export des Dashboards als EINE eigenständige HTML-Datei.

Zweck: das Dashboard ansehen und filtern, ohne Python, ohne Server, ohne
Installation — Datei doppelklicken genügt. Die Daten werden als JSON in die
Seite eingebettet, die gesamte Filter- und Kennzahlenlogik läuft im Browser.

Wichtig und bewusst: das ist ein **Schnappschuss**. Er zeigt den Datenstand
zum Zeitpunkt des Exports und kann selbst nichts abrufen. Neue Daten holt
weiterhin nur `geotracker ingest` / `schedule`; danach exportiert man neu.

    python3 -m geotracker export-html dashboard.html
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "api" / "static" / "standalone.html"
PLACEHOLDER = "/*__GEO_DATA__*/null"


def build_payload(conn: sqlite3.Connection) -> dict:
    """Alles, was das Dashboard braucht — kompakt, aber vollständig.

    Kurze Schlüssel, weil jeder Lauf den kompletten Antworttext mitbringt und
    die Datei sonst unnötig aufgeht.
    """
    prompts = [
        {
            "id": row["id"], "text": row["text"], "cat": row["category"],
            "country": row["country"], "lang": row["language"],
            "branding": row["branding"], "intent": row["intent"],
            "tags": json.loads(row["tags"] or "[]"),
        }
        for row in conn.execute("SELECT * FROM prompts ORDER BY id")
    ]

    brands = [
        {
            "id": row["id"], "name": row["name"], "own": row["is_own_brand"],
            "comp": row["is_competitor"], "known": row["is_known"],
            "seen": row["first_seen_at"],
        }
        for row in conn.execute("SELECT * FROM brands ORDER BY id")
    ]

    domains = {
        row["domain"]: {"type": row["source_type"], "dtype": row["domain_type"],
                        "known": row["is_known"], "seen": row["first_seen_at"]}
        for row in conn.execute("SELECT * FROM domains")
    }

    # Nur beantwortete Läufe: 'deferred'/'error' sind Ebene-1-Wahrheit, würden
    # aber jede Rate verwässern — sie heißen "keine Antwort", nicht
    # "LogBATT kam nicht vor". Die Zahl der ausgelassenen Läufe steht in meta.
    runs = []
    for row in conn.execute(
        """
        SELECT r.id, r.prompt_id, r.engine, r.run_date, r.source, r.status,
               r.raw_response, r.provider_model,
               e.logbatt_mentioned, e.logbatt_position, e.sentiment,
               e.problem_narrative_anchored, e.evaluator_version
          FROM runs r
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         WHERE r.status IN ('success', 'partial')
         ORDER BY r.run_date, r.id
        """
    ):
        citations = [
            [
                c["cited_domain"], c["cited_url"], c["source_type"],
                c["url_known"], c["citation_rank"], c["title"], c["is_known"],
                c["url_type"],
            ]
            for c in conn.execute(
                """
                SELECT cited_domain, cited_url, source_type, url_known,
                       citation_rank, title, is_known, url_type
                  FROM citations WHERE run_id = ? AND origin = 'cited'
                 ORDER BY citation_rank
                """,
                (row["id"],),
            )
        ]
        mentions = [
            [m["brand_id"], m["mention_rank"]]
            for m in conn.execute(
                """
                SELECT m.brand_id, m.mention_rank FROM brand_mentions m
                  JOIN evaluations e ON e.id = m.evaluation_id AND e.is_current = 1
                 WHERE m.run_id = ? ORDER BY m.mention_rank
                """,
                (row["id"],),
            )
        ]
        runs.append({
            "id": row["id"], "p": row["prompt_id"], "e": row["engine"],
            "d": row["run_date"], "s": row["source"],
            "m": row["logbatt_mentioned"], "pos": row["logbatt_position"],
            "sen": row["sentiment"], "pn": row["problem_narrative_anchored"],
            "ev": row["evaluator_version"],
            "t": row["raw_response"] or "",
            "c": citations, "b": mentions,
        })

    skipped = conn.execute(
        "SELECT COUNT(*) c FROM runs WHERE status NOT IN ('success', 'partial')"
    ).fetchone()["c"]

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "prompts": prompts,
        "brands": brands,
        "domains": domains,
        "runs": runs,
        "meta": {
            "skipped_runs": skipped,
            "sources": sorted({r["s"] for r in runs}),
            "engines": sorted({r["e"] for r in runs}),
        },
    }


def _to_fragment(html: str) -> str:
    """Die Rahmen-Tags entfernen (doctype/html/head/body).

    Für Umgebungen, die den Seitenrahmen selbst mitbringen und nur den Inhalt
    einbetten — dort würde ein zweites <html> die Seite zerlegen.
    """
    start = html.index("<title>")
    end = html.rindex("</body>")
    inner = html[start:end]
    return inner.replace("</head>\n<body>\n", "", 1).strip() + "\n"


def render_dashboard(conn: sqlite3.Connection, payload: dict | None = None) -> str:
    """Die Vorlage mit eingebettetem Payload — Basis für Export UND Server."""
    payload = build_payload(conn) if payload is None else payload
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError(f"Platzhalter {PLACEHOLDER} fehlt in {TEMPLATE}")

    # `</script>` im Antworttext würde die Seite zerreißen — die einzige
    # Stelle, an der die eingebetteten Daten das umgebende HTML treffen können.
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    return template.replace(PLACEHOLDER, data)


def export_html(conn: sqlite3.Connection, destination: Path, *, fragment: bool = False) -> dict:
    payload = build_payload(conn)
    html = render_dashboard(conn, payload)
    destination.write_text(_to_fragment(html) if fragment else html, encoding="utf-8")
    return {
        "file": str(destination),
        "size_kb": round(destination.stat().st_size / 1024),
        "runs": len(payload["runs"]),
        "citations": sum(len(r["c"]) for r in payload["runs"]),
        "prompts": len(payload["prompts"]),
    }
