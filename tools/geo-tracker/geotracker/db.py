"""SQLite-Zugriff und Migrationen.

Migrationen sind nummerierte .sql-Dateien in `migrations/`. Sie laufen genau
einmal, in Dateinamen-Reihenfolge, und werden in `schema_migrations`
protokolliert — damit das Schema migrierbar bleibt und nicht per Hand
nachgezogen werden muss.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import PACKAGE_DIR

MIGRATIONS_DIR = PACKAGE_DIR / "migrations"


def utcnow() -> str:
    """ISO-8601-Zeitstempel in UTC, sekundengenau."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    """run_date-Achse: Kalendertag in UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL: der Scheduler schreibt, während das Dashboard liest.
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Wendet alle noch nicht angewandten Migrationen an. Gibt deren Namen zurück."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    applied = {row["version"] for row in conn.execute("SELECT version FROM schema_migrations")}

    newly_applied: list[str] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        # executescript() committet implizit — jede Migration ist ihre eigene
        # Transaktion, eine fehlgeschlagene blockiert die folgenden.
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (path.name, utcnow()),
        )
        conn.commit()
        newly_applied.append(path.name)

    return newly_applied


def open_db(db_path: Path) -> sqlite3.Connection:
    """Verbindung öffnen und Schema auf den aktuellen Stand bringen."""
    conn = connect(db_path)
    migrate(conn)
    return conn
