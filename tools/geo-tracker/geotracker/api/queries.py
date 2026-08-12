"""Abfrage-Schicht des Dashboards.

Ein einziger Filter-Baustein, den ALLE Kennzahlen benutzen. Das ist die
zentrale Zusage aus dem Auftrag: Share of Voice, Visibility und
Domain-Rankings kommen immer aus der aktuell gefilterten Menge, nie aus der
Gesamtmenge. Es gibt hier bewusst keine zweite, "schnellere" Query, die den
Filter umgeht — genau so entstehen sonst Zahlen, die im Dashboard nicht
zusammenpassen.

Filter-Semantik:
  * Zwischen verschiedenen Facetten UND  (Land=DE UND Kategorie=Recycling)
  * Innerhalb einer Facette ODER         (Engine=chatgpt ODER perplexity)
Das ist das übliche Facetten-Verhalten und macht Mehrfachauswahl brauchbar.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

# Ein Lauf zählt für Kennzahlen nur, wenn eine verwertbare Antwort da ist.
# 'deferred'/'error' bleiben in der DB (Ebene-1-Wahrheit), aber sie würden
# Visibility-Raten verwässern — sie sind kein "LogBATT kam nicht vor",
# sondern "es gab keine Antwort".
ANSWERED = "('success', 'partial')"


@dataclass
class Filters:
    since: str | None = None
    until: str | None = None
    engines: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    prompt_ids: list[int] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    url: str | None = None
    brand_ids: list[int] = field(default_factory=list)

    def where(self) -> tuple[str, list[Any]]:
        """WHERE-Fragment über `runs r JOIN prompts p`."""
        clauses = [f"r.status IN {ANSWERED}"]
        params: list[Any] = []

        def facet(column: str, values: list[Any]) -> None:
            if values:
                clauses.append(f"{column} IN ({','.join('?' * len(values))})")
                params.extend(values)

        if self.since:
            clauses.append("r.run_date >= ?")
            params.append(self.since)
        if self.until:
            clauses.append("r.run_date <= ?")
            params.append(self.until)

        facet("r.engine", self.engines)
        facet("r.country", [c.upper() for c in self.countries])
        facet("p.language", [lang.lower() for lang in self.languages])
        facet("p.category", self.categories)
        facet("r.prompt_id", self.prompt_ids)
        facet("r.source", self.sources)

        # "nur Läufe, die Domain X zitieren" — als EXISTS, damit ein Lauf nicht
        # vervielfacht wird, wenn er dieselbe Domain mehrfach zitiert.
        if self.domains:
            placeholders = ",".join("?" * len(self.domains))
            clauses.append(
                f"""EXISTS (SELECT 1 FROM citations c WHERE c.run_id = r.id
                             AND c.origin = 'cited' AND c.cited_domain IN ({placeholders}))"""
            )
            params.extend(self.domains)

        if self.url:
            clauses.append(
                """EXISTS (SELECT 1 FROM citations c WHERE c.run_id = r.id
                            AND c.origin = 'cited' AND c.url_known = 1 AND c.cited_url = ?)"""
            )
            params.append(self.url)

        if self.brand_ids:
            placeholders = ",".join("?" * len(self.brand_ids))
            clauses.append(
                f"""EXISTS (SELECT 1 FROM brand_mentions m
                             JOIN evaluations e ON e.id = m.evaluation_id AND e.is_current = 1
                            WHERE m.run_id = r.id AND m.brand_id IN ({placeholders}))"""
            )
            params.extend(self.brand_ids)

        return " AND ".join(clauses), params

    def run_ids_sql(self) -> tuple[str, list[Any]]:
        where, params = self.where()
        return (
            f"SELECT r.id FROM runs r JOIN prompts p ON p.id = r.prompt_id WHERE {where}",
            params,
        )

    def previous_period(self) -> "Filters | None":
        """Gleich langer Zeitraum davor — Grundlage aller Deltas."""
        if not self.since or not self.until:
            return None
        start = date.fromisoformat(self.since)
        end = date.fromisoformat(self.until)
        length = (end - start).days + 1
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=length - 1)
        clone = Filters(**{**self.__dict__})
        clone.since = previous_start.isoformat()
        clone.until = previous_end.isoformat()
        return clone


def _rows(conn: sqlite3.Connection, sql: str, params: list[Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in conn.execute(sql, params)]


# ---------------------------------------------------------------------------
# Kennzahlen
# ---------------------------------------------------------------------------
def kpis(conn: sqlite3.Connection, filters: Filters) -> dict[str, Any]:
    runs_sql, params = filters.run_ids_sql()

    base = conn.execute(
        f"""
        SELECT COUNT(*) AS runs,
               SUM(CASE WHEN e.logbatt_mentioned = 1 THEN 1 ELSE 0 END) AS mentioned,
               AVG(CASE WHEN e.logbatt_mentioned = 1 THEN e.logbatt_position END) AS avg_position,
               COUNT(e.id) AS evaluated,
               SUM(CASE WHEN e.problem_narrative_anchored = 1 THEN 1 ELSE 0 END) AS anchored,
               SUM(CASE WHEN e.sentiment = 'positive' THEN 1 ELSE 0 END) AS positive,
               SUM(CASE WHEN e.sentiment = 'neutral'  THEN 1 ELSE 0 END) AS neutral,
               SUM(CASE WHEN e.sentiment = 'negative' THEN 1 ELSE 0 END) AS negative
          FROM ({runs_sql}) f
          LEFT JOIN evaluations e ON e.run_id = f.id AND e.is_current = 1
        """,
        params,
    ).fetchone()

    # Share of Voice über die gefilterte Menge: LogBATT-Nennungen geteilt durch
    # ALLE Marken-Nennungen. Nicht der Mittelwert der Einzel-SoVs — der würde
    # Läufe mit wenigen Marken überbewerten.
    voice = conn.execute(
        f"""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN b.is_own_brand = 1 THEN 1 ELSE 0 END) AS own
          FROM ({runs_sql}) f
          JOIN evaluations e ON e.run_id = f.id AND e.is_current = 1
          JOIN brand_mentions m ON m.evaluation_id = e.id
          JOIN brands b ON b.id = m.brand_id
        """,
        params,
    ).fetchone()

    citations = conn.execute(
        f"""
        SELECT COUNT(*) AS total,
               COUNT(DISTINCT c.cited_domain) AS domains,
               SUM(CASE WHEN c.source_type = 'owned' THEN 1 ELSE 0 END) AS owned,
               SUM(CASE WHEN c.source_type = 'competitor' THEN 1 ELSE 0 END) AS competitor,
               SUM(CASE WHEN c.source_type = 'earned_media' THEN 1 ELSE 0 END) AS earned
          FROM ({runs_sql}) f
          JOIN citations c ON c.run_id = f.id AND c.origin = 'cited'
        """,
        params,
    ).fetchone()

    runs = base["runs"] or 0
    evaluated = base["evaluated"] or 0
    total_voice = voice["total"] or 0

    return {
        "runs": runs,
        "evaluated": evaluated,
        # Nenner ist die Zahl der AUSGEWERTETEN Läufe, nicht aller Läufe:
        # ein noch nicht bewerteter Lauf ist kein "nicht genannt".
        "visibility": (base["mentioned"] or 0) / evaluated if evaluated else None,
        "avg_position": base["avg_position"],
        "share_of_voice": (voice["own"] or 0) / total_voice if total_voice else None,
        "problem_narrative_rate": (base["anchored"] or 0) / evaluated if evaluated else None,
        "sentiment": {
            "positive": base["positive"] or 0,
            "neutral": base["neutral"] or 0,
            "negative": base["negative"] or 0,
        },
        "citations": {
            "total": citations["total"] or 0,
            "domains": citations["domains"] or 0,
            "owned": citations["owned"] or 0,
            "competitor": citations["competitor"] or 0,
            "earned_media": citations["earned"] or 0,
        },
    }


def overview(conn: sqlite3.Connection, filters: Filters) -> dict[str, Any]:
    current = kpis(conn, filters)
    previous_filters = filters.previous_period()
    previous = kpis(conn, previous_filters) if previous_filters else None

    def delta(key: str) -> float | None:
        if not previous:
            return None
        now, before = current.get(key), previous.get(key)
        if now is None or before is None:
            return None
        return now - before

    return {
        "current": current,
        "previous": previous,
        "deltas": {
            key: delta(key)
            for key in ("visibility", "share_of_voice", "avg_position", "problem_narrative_rate")
        },
        "previous_period": (
            {"since": previous_filters.since, "until": previous_filters.until}
            if previous_filters
            else None
        ),
    }


def timeseries(conn: sqlite3.Connection, filters: Filters) -> list[dict[str, Any]]:
    runs_sql, params = filters.run_ids_sql()
    return _rows(
        conn,
        f"""
        SELECT r.run_date AS day,
               COUNT(*) AS runs,
               AVG(CASE WHEN e.id IS NULL THEN NULL
                        WHEN e.logbatt_mentioned = 1 THEN 1.0 ELSE 0.0 END) AS visibility,
               AVG(CASE WHEN e.logbatt_mentioned = 1 THEN e.logbatt_position END) AS avg_position,
               (SELECT COUNT(*) FROM brand_mentions m2
                  JOIN evaluations e2 ON e2.id = m2.evaluation_id AND e2.is_current = 1
                  JOIN brands b2 ON b2.id = m2.brand_id
                  JOIN runs r2 ON r2.id = m2.run_id
                 WHERE r2.run_date = r.run_date AND m2.run_id IN (SELECT id FROM ({runs_sql}) x)
                   AND b2.is_own_brand = 1) AS own_mentions,
               (SELECT COUNT(*) FROM brand_mentions m3
                  JOIN evaluations e3 ON e3.id = m3.evaluation_id AND e3.is_current = 1
                  JOIN runs r3 ON r3.id = m3.run_id
                 WHERE r3.run_date = r.run_date AND m3.run_id IN (SELECT id FROM ({runs_sql}) y)
                ) AS all_mentions
          FROM ({runs_sql}) f
          JOIN runs r ON r.id = f.id
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         GROUP BY r.run_date
         ORDER BY r.run_date
        """,
        params * 3,
    )


def breakdown(conn: sqlite3.Connection, filters: Filters, dimension: str) -> list[dict[str, Any]]:
    """Kennzahlen je Kategorie / Land / Engine / Quelle."""
    columns = {
        "category": "p.category",
        "country": "r.country",
        "engine": "r.engine",
        "language": "p.language",
        "source": "r.source",
    }
    column = columns.get(dimension)
    if column is None:
        raise ValueError(f"Unbekannte Dimension: {dimension}")

    runs_sql, params = filters.run_ids_sql()
    return _rows(
        conn,
        f"""
        SELECT {column} AS label,
               COUNT(*) AS runs,
               AVG(CASE WHEN e.id IS NULL THEN NULL
                        WHEN e.logbatt_mentioned = 1 THEN 1.0 ELSE 0.0 END) AS visibility,
               AVG(CASE WHEN e.logbatt_mentioned = 1 THEN e.logbatt_position END) AS avg_position,
               SUM(CASE WHEN e.problem_narrative_anchored = 1 THEN 1 ELSE 0 END) AS anchored
          FROM ({runs_sql}) f
          JOIN runs r ON r.id = f.id
          JOIN prompts p ON p.id = r.prompt_id
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         GROUP BY {column}
         ORDER BY runs DESC
        """,
        params,
    )


# ---------------------------------------------------------------------------
# Citation-Achse
# ---------------------------------------------------------------------------
def domain_ranking(
    conn: sqlite3.Connection, filters: Filters, *, limit: int = 50, source_type: str | None = None
) -> list[dict[str, Any]]:
    runs_sql, params = filters.run_ids_sql()
    extra = ""
    if source_type:
        extra = "AND c.source_type = ?"
        params = params + [source_type]

    return _rows(
        conn,
        f"""
        SELECT c.cited_domain AS domain,
               c.source_type,
               MAX(d.is_known) AS is_known,
               COUNT(*) AS citations,
               COUNT(DISTINCT c.run_id) AS runs,
               COUNT(DISTINCT r.prompt_id) AS prompts,
               AVG(c.citation_rank) AS avg_rank,
               MIN(d.first_seen_at) AS first_seen_at
          FROM ({runs_sql}) f
          JOIN citations c ON c.run_id = f.id AND c.origin = 'cited' {extra}
          JOIN runs r ON r.id = f.id
          LEFT JOIN domains d ON d.domain = c.cited_domain
         GROUP BY c.cited_domain, c.source_type
         ORDER BY citations DESC, domain
         LIMIT ?
        """,
        params + [limit],
    )


def url_ranking(
    conn: sqlite3.Connection, filters: Filters, *, limit: int = 50
) -> list[dict[str, Any]]:
    """Nur echte URLs. Peec-Importe liefern nur Domains (url_known = 0)."""
    runs_sql, params = filters.run_ids_sql()
    return _rows(
        conn,
        f"""
        SELECT c.cited_url AS url, c.cited_domain AS domain, c.source_type,
               MAX(c.title) AS title,
               COUNT(*) AS citations,
               COUNT(DISTINCT r.prompt_id) AS prompts,
               AVG(c.citation_rank) AS avg_rank
          FROM ({runs_sql}) f
          JOIN citations c ON c.run_id = f.id AND c.origin = 'cited' AND c.url_known = 1
          JOIN runs r ON r.id = f.id
         GROUP BY c.cited_url
         ORDER BY citations DESC
         LIMIT ?
        """,
        params + [limit],
    )


def owned_domain_gaps(conn: sqlite3.Connection, filters: Filters) -> list[dict[str, Any]]:
    """Gap-View: hohe Relevanz, aber eigene Domain fehlt.

    Je Prompt: wie oft lief er, wie oft wurde eine eigene Domain zitiert, und
    wie oft eine Wettbewerber-Domain. Prompts ganz oben (viele Läufe, null
    eigene Zitate, viele Wettbewerber-Zitate) sind die Arbeitsliste.
    """
    runs_sql, params = filters.run_ids_sql()
    return _rows(
        conn,
        f"""
        SELECT r.prompt_id, p.text AS prompt, p.category, p.country,
               COUNT(DISTINCT r.id) AS runs,
               COUNT(DISTINCT CASE WHEN c.source_type = 'owned' THEN r.id END) AS runs_with_owned,
               COUNT(DISTINCT CASE WHEN c.source_type = 'competitor' THEN r.id END) AS runs_with_competitor,
               SUM(CASE WHEN c.source_type = 'owned' THEN 1 ELSE 0 END) AS owned_citations,
               AVG(CASE WHEN e.id IS NULL THEN NULL
                        WHEN e.logbatt_mentioned = 1 THEN 1.0 ELSE 0.0 END) AS visibility
          FROM ({runs_sql}) f
          JOIN runs r ON r.id = f.id
          JOIN prompts p ON p.id = r.prompt_id
          LEFT JOIN citations c ON c.run_id = r.id AND c.origin = 'cited'
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         GROUP BY r.prompt_id
         ORDER BY runs_with_owned ASC, runs DESC
        """,
        params,
    )


# ---------------------------------------------------------------------------
# Marken
# ---------------------------------------------------------------------------
def brand_leaderboard(
    conn: sqlite3.Connection, filters: Filters, *, limit: int = 50
) -> list[dict[str, Any]]:
    runs_sql, params = filters.run_ids_sql()
    total = conn.execute(
        f"""
        SELECT COUNT(*) AS c FROM ({runs_sql}) f
          JOIN evaluations e ON e.run_id = f.id AND e.is_current = 1
          JOIN brand_mentions m ON m.evaluation_id = e.id
        """,
        params,
    ).fetchone()["c"] or 0

    evaluated_runs = conn.execute(
        f"""
        SELECT COUNT(*) AS c FROM ({runs_sql}) f
          JOIN evaluations e ON e.run_id = f.id AND e.is_current = 1
        """,
        params,
    ).fetchone()["c"] or 0

    rows = _rows(
        conn,
        f"""
        SELECT b.id AS brand_id, b.name, b.is_own_brand, b.is_competitor, b.is_known,
               b.first_seen_at,
               COUNT(*) AS mentions,
               COUNT(DISTINCT m.run_id) AS runs,
               AVG(m.mention_rank) AS avg_position
          FROM ({runs_sql}) f
          JOIN evaluations e ON e.run_id = f.id AND e.is_current = 1
          JOIN brand_mentions m ON m.evaluation_id = e.id
          JOIN brands b ON b.id = m.brand_id
         GROUP BY b.id
         ORDER BY mentions DESC
         LIMIT ?
        """,
        params + [limit],
    )
    for row in rows:
        row["share_of_voice"] = row["mentions"] / total if total else None
        row["visibility"] = row["runs"] / evaluated_runs if evaluated_runs else None
    return rows


def prompt_table(conn: sqlite3.Connection, filters: Filters) -> list[dict[str, Any]]:
    runs_sql, params = filters.run_ids_sql()
    return _rows(
        conn,
        f"""
        SELECT r.prompt_id, p.text AS prompt, p.category, p.country, p.language,
               COUNT(*) AS runs,
               AVG(CASE WHEN e.id IS NULL THEN NULL
                        WHEN e.logbatt_mentioned = 1 THEN 1.0 ELSE 0.0 END) AS visibility,
               AVG(CASE WHEN e.logbatt_mentioned = 1 THEN e.logbatt_position END) AS avg_position,
               SUM(CASE WHEN e.problem_narrative_anchored = 1 THEN 1 ELSE 0 END) AS anchored,
               MAX(r.run_date) AS last_run
          FROM ({runs_sql}) f
          JOIN runs r ON r.id = f.id
          JOIN prompts p ON p.id = r.prompt_id
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         GROUP BY r.prompt_id
         ORDER BY visibility IS NULL, visibility DESC, runs DESC
        """,
        params,
    )


def prompt_history(
    conn: sqlite3.Connection, filters: Filters, prompt_id: int, *, limit: int = 60
) -> dict[str, Any]:
    """Volle Antwort-Historie eines Prompts inkl. Datum, Marken und Quellen."""
    scoped = Filters(**{**filters.__dict__})
    scoped.prompt_ids = [prompt_id]
    runs_sql, params = scoped.run_ids_sql()

    prompt = conn.execute(
        "SELECT id, text, category, country, language FROM prompts WHERE id = ?", (prompt_id,)
    ).fetchone()

    runs = _rows(
        conn,
        f"""
        SELECT r.id, r.run_date, r.engine, r.source, r.status, r.provider_model,
               r.raw_response,
               e.logbatt_mentioned, e.logbatt_position, e.sentiment,
               e.problem_narrative_anchored, e.share_of_voice, e.evaluator_version
          FROM ({runs_sql}) f
          JOIN runs r ON r.id = f.id
          LEFT JOIN evaluations e ON e.run_id = r.id AND e.is_current = 1
         ORDER BY r.run_date DESC, r.engine
         LIMIT ?
        """,
        params + [limit],
    )

    for run in runs:
        run["citations"] = _rows(
            conn,
            """
            SELECT citation_rank, cited_domain, cited_url, url_known, source_type, is_known, title
              FROM citations WHERE run_id = ? AND origin = 'cited' ORDER BY citation_rank
            """,
            [run["id"]],
        )
        run["brands"] = _rows(
            conn,
            """
            SELECT m.mention_rank, b.name, b.is_own_brand
              FROM brand_mentions m JOIN brands b ON b.id = m.brand_id
              JOIN evaluations e ON e.id = m.evaluation_id AND e.is_current = 1
             WHERE m.run_id = ? ORDER BY m.mention_rank
            """,
            [run["id"]],
        )

    return {"prompt": dict(prompt) if prompt else None, "runs": runs}


def discoveries(conn: sqlite3.Connection, filters: Filters, *, days: int = 14) -> dict[str, Any]:
    """„Neu entdeckt" — Marken und Domains, die zuletzt erstmals auftauchten."""
    runs_sql, params = filters.run_ids_sql()
    cutoff = (
        date.fromisoformat(filters.until) if filters.until else date.today()
    ) - timedelta(days=days)

    new_domains = _rows(
        conn,
        f"""
        SELECT c.cited_domain AS domain, c.source_type, MIN(r.run_date) AS first_run_date,
               COUNT(*) AS citations
          FROM ({runs_sql}) f
          JOIN citations c ON c.run_id = f.id AND c.origin = 'cited'
          JOIN runs r ON r.id = f.id
          JOIN domains d ON d.domain = c.cited_domain
         WHERE d.is_known = 0
         GROUP BY c.cited_domain
         ORDER BY first_run_date DESC, citations DESC
         LIMIT 50
        """,
        params,
    )

    new_brands = _rows(
        conn,
        """
        SELECT id AS brand_id, name, first_seen_at, notes
          FROM brands WHERE is_known = 0
         ORDER BY first_seen_at DESC LIMIT 50
        """,
        [],
    )

    return {"cutoff": cutoff.isoformat(), "domains": new_domains, "brands": new_brands}


def filter_options(conn: sqlite3.Connection) -> dict[str, Any]:
    """Alles, was die Filterleiste anbieten kann."""

    def column(sql: str) -> list[Any]:
        return [row[0] for row in conn.execute(sql)]

    span = conn.execute(
        f"SELECT MIN(run_date) AS a, MAX(run_date) AS b FROM runs WHERE status IN {ANSWERED}"
    ).fetchone()

    return {
        "date_range": {"min": span["a"], "max": span["b"]},
        "engines": column("SELECT DISTINCT engine FROM runs ORDER BY engine"),
        "countries": column("SELECT DISTINCT country FROM runs ORDER BY country"),
        "languages": column("SELECT DISTINCT language FROM prompts ORDER BY language"),
        "categories": column("SELECT DISTINCT category FROM prompts ORDER BY category"),
        "sources": column("SELECT DISTINCT source FROM runs ORDER BY source"),
        "prompts": _rows(
            conn,
            """
            SELECT p.id, p.text, p.category FROM prompts p
             WHERE EXISTS (SELECT 1 FROM runs r WHERE r.prompt_id = p.id)
             ORDER BY p.category, p.text
            """,
            [],
        ),
        "brands": _rows(
            conn,
            """
            SELECT b.id, b.name, b.is_own_brand, b.is_known FROM brands b
             WHERE EXISTS (SELECT 1 FROM brand_mentions m WHERE m.brand_id = b.id)
             ORDER BY b.is_own_brand DESC, b.name
            """,
            [],
        ),
        "domains": _rows(
            conn,
            """
            SELECT c.cited_domain AS domain, COUNT(*) AS citations
              FROM citations c WHERE c.origin = 'cited'
             GROUP BY c.cited_domain ORDER BY citations DESC LIMIT 200
            """,
            [],
        ),
    }
