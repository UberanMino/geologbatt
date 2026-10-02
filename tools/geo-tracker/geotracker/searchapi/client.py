"""HTTP-Client für die SearchApi (https://www.searchapi.io/api/v1/search).

Alle Engines laufen über denselben GET-Endpoint; unterschiedlich sind nur die
Parameter (siehe `parsers.build_params`). Der Client kennt bewusst KEINE
Engine-Semantik — er transportiert, protokolliert und wiederholt.

Robustheit:
  * Timeout pro Request
  * Retries mit exponentiellem Backoff bei Netzwerkfehlern, 429 und 5xx
  * 4xx (außer 429) werden NICHT wiederholt — das sind unsere Fehler
  * Der rohe Response-Body wird immer mitgeliefert, auch im Fehlerfall, damit
    Ebene 1 auch dann etwas speichern kann
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

USER_AGENT = "geologbatt-geotracker/0.1 (+internal GEO monitoring)"

# Statuscodes, bei denen ein erneuter Versuch sinnvoll ist.
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class SearchApiError(RuntimeError):
    """Fehler, der auch nach allen Retries bestehen blieb."""

    def __init__(self, message: str, *, status: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status = status
        self.body = body


@dataclass
class SearchApiResult:
    payload: dict[str, Any]      # geparstes JSON
    raw_body: str                # Response-Body roh
    http_status: int
    attempts: int
    latency_ms: int
    request_url: str             # OHNE api_key — landet in der DB


class SearchApiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.searchapi.io/api/v1/search",
        timeout: int = 120,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

    def _url(self, params: dict[str, str], *, with_key: bool) -> str:
        query = dict(params)
        if with_key:
            query["api_key"] = self.api_key
        return f"{self.base_url}?{urllib.parse.urlencode(query)}"

    def search(self, params: dict[str, str]) -> SearchApiResult:
        """Einen Request ausführen (inkl. Retries). Wirft SearchApiError bei Endgültigkeit."""
        if not self.api_key:
            raise SearchApiError(
                "Kein SEARCHAPI_API_KEY gesetzt — Ebene-1-Ingestion braucht einen "
                "serverseitigen Key (.env, siehe .env.example)."
            )

        # Der Key steht im Authorization-Header, nicht in der URL: so kann die
        # angefragte URL bedenkenlos in der DB und im Log landen.
        safe_url = self._url(params, with_key=False)
        request = urllib.request.Request(
            safe_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )

        started = time.monotonic()
        last_error: SearchApiError | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read().decode("utf-8", errors="replace")
                    status = response.status
                payload = json.loads(body)
                return SearchApiResult(
                    payload=payload,
                    raw_body=body,
                    http_status=status,
                    attempts=attempt,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    request_url=safe_url,
                )

            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
                last_error = SearchApiError(
                    f"HTTP {exc.code} von SearchApi: {body[:500]}", status=exc.code, body=body
                )
                if exc.code not in RETRYABLE_STATUS:
                    break

            except urllib.error.URLError as exc:
                last_error = SearchApiError(f"Netzwerkfehler: {exc.reason}")

            except json.JSONDecodeError as exc:
                # Kein gültiges JSON -> nicht wiederholen, das wird beim zweiten
                # Versuch auch nicht besser.
                last_error = SearchApiError(f"Antwort war kein gültiges JSON: {exc}")
                break

            except TimeoutError:
                last_error = SearchApiError(f"Timeout nach {self.timeout}s")

            if attempt <= self.max_retries:
                time.sleep(self.retry_backoff * (2 ** (attempt - 1)))

        assert last_error is not None
        last_error.args = (f"{last_error.args[0]} (nach {self.max_retries + 1} Versuchen)",)
        raise last_error
