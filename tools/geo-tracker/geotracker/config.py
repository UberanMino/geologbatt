"""Konfiguration — ausschließlich serverseitig.

Secrets kommen aus der Umgebung bzw. aus `.env` (nicht im Repo, siehe
`.env.example`). Es gibt bewusst KEINEN Codepfad, der einen Key an das
Frontend durchreicht: das Dashboard spricht später nur mit unserer REST-API.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent

# Alle vier Oberflächen, die das Tool abdeckt.
ENGINES = ("chatgpt", "perplexity", "gemini", "google_ai_overview")
IMPLEMENTED_ENGINES = ENGINES  # alle vier Oberflächen implementiert


def _load_dotenv(path: Path) -> None:
    """Minimaler .env-Loader (KEY=VALUE, '#'-Kommentare, optionale Quotes).

    Bewusst ohne python-dotenv-Zwang, damit `geotracker` auch ohne installierte
    Dependencies startet; bestehende Umgebungsvariablen gewinnen immer.
    """
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


# Schlüssel, die das Dashboard-Einstellungsfenster setzen darf. Bewusst eine
# feste Whitelist: das Settings-Fenster kann NUR diese beiden Secrets schreiben,
# keine beliebigen Umgebungsvariablen.
EDITABLE_SECRETS: dict[str, str] = {
    "searchapi": "SEARCHAPI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def env_path() -> Path:
    """Pfad der `.env` (respektiert GEOTRACKER_ENV_FILE für Tests)."""
    override = os.environ.get("GEOTRACKER_ENV_FILE", "").strip()
    return Path(override).expanduser() if override else PROJECT_DIR / ".env"


def mask_secret(value: str) -> str:
    """Nur ein Wiedererkennungs-Hinweis, nie der ganze Schlüssel.

    "gesetzt · ····ab12" reicht dem Nutzer zum Abgleich; die vollständige
    Zeichenkette verlässt den Server bewusst nie.
    """
    v = (value or "").strip()
    if not v:
        return ""
    return "····" + v[-4:] if len(v) >= 4 else "····"


def write_env_values(updates: dict[str, str], env_file: Path | None = None) -> None:
    """`KEY=VALUE` in der `.env` aktualisieren (anlegen/ersetzen), Rest erhalten.

    Kommentare, Reihenfolge und andere Einträge bleiben unangetastet; ein bereits
    vorhandener Schlüssel wird an Ort und Stelle ersetzt, ein neuer angehängt.
    """
    path = env_file or env_path()
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    remaining = dict(updates)
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in remaining:
                out.append(f"{key}={remaining.pop(key)}")
                continue
        out.append(line)
    for key, value in remaining.items():
        out.append(f"{key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    try:
        return float(raw) if raw else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    db_path: Path
    searchapi_key: str
    searchapi_base_url: str
    anthropic_key: str

    # Robustheit / Drosselung
    request_timeout: int          # Sekunden pro HTTP-Request
    max_retries: int              # zusätzliche Versuche nach dem ersten
    retry_backoff: float          # Sekunden, exponentiell verdoppelt
    throttle_seconds: float       # Pause zwischen zwei Läufen (sequenziell!)
    max_runs_per_invocation: int  # Kostenbremse: hartes Limit je Ingest-Aufruf

    # ChatGPT-Engine
    chatgpt_web_search: bool

    # Engines, die der Scheduler täglich abarbeitet
    engines_for_scheduler: tuple[str, ...]

    @property
    def has_searchapi_key(self) -> bool:
        return bool(self.searchapi_key)


def load_config(env_file: Path | None = None) -> Config:
    _load_dotenv(env_file or env_path())

    db_path = Path(
        os.environ.get("GEOTRACKER_DB_PATH", str(PROJECT_DIR / "data" / "geotracker.sqlite3"))
    ).expanduser()

    return Config(
        db_path=db_path,
        searchapi_key=os.environ.get("SEARCHAPI_API_KEY", "").strip(),
        searchapi_base_url=os.environ.get(
            "SEARCHAPI_BASE_URL", "https://www.searchapi.io/api/v1/search"
        ).strip(),
        anthropic_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        request_timeout=_env_int("GEOTRACKER_REQUEST_TIMEOUT", 120),
        max_retries=_env_int("GEOTRACKER_MAX_RETRIES", 3),
        retry_backoff=_env_float("GEOTRACKER_RETRY_BACKOFF", 2.0),
        throttle_seconds=_env_float("GEOTRACKER_THROTTLE_SECONDS", 2.0),
        max_runs_per_invocation=_env_int("GEOTRACKER_MAX_RUNS", 200),
        # ChatGPT sucht auch von sich aus im Web; explizit true zu setzen macht
        # das Grounding deterministisch — und ohne Grounding gäbe es keine
        # reference_links, also keine Citation-Achse.
        chatgpt_web_search=os.environ.get("GEOTRACKER_CHATGPT_WEB_SEARCH", "true").lower()
        not in ("0", "false", "no"),
        engines_for_scheduler=tuple(
            e.strip()
            for e in os.environ.get("GEOTRACKER_SCHEDULER_ENGINES", ",".join(ENGINES)).split(",")
            if e.strip() in ENGINES
        )
        or ENGINES,
    )
