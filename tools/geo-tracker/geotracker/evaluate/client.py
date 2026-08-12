"""Anthropic-Anbindung des Auswertungs-Layers (Claude Haiku 4.5).

Zwei Betriebsarten, gleiche Request-Bausteine:

  * `evaluate_sync`  — ein Lauf sofort. Für Ad-hoc-Prüfungen und kleine Mengen.
  * `submit_batch` / `collect_batch` — Message Batches API, 50 % günstiger.
    Der tägliche Auswertungslauf braucht keine Echtzeit, also ist Batch der
    Default.

Prompt Caching ist in beiden Pfaden aktiv: der Systemprompt trägt den
Cache-Breakpoint, der variable Teil steht dahinter. `usage`-Zähler werden
zurückgegeben, damit sich am Cache-Verhalten nicht raten lässt.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Iterable

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from .prompt import RESPONSE_SCHEMA

# Claude Haiku 4.5: schnell und günstig ($1/$5 je Mio. Token) und für
# Extraktion/Klassifikation ausreichend — die Aufgabe ist Textverständnis, kein
# tiefes Reasoning. Structured Outputs werden unterstützt.
MODEL = "claude-haiku-4-5"

# Die Ausgabe ist ein kleines, schemagebundenes JSON-Objekt (eine Handvoll
# Marken + drei Felder). 4096 ist reichlich; höher zu gehen kostet nichts,
# verschleiert aber, dass hier bewusst kein langer Output entsteht.
MAX_TOKENS = 4096


class EvaluationError(RuntimeError):
    pass


@dataclass
class EvaluationResult:
    run_id: int
    parsed: dict[str, Any] | None
    raw_output: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.parsed is not None


def build_params(system_prompt: str, user_message: str) -> dict[str, Any]:
    """Request-Bausteine, identisch für Sync- und Batch-Pfad.

    Reihenfolge ist entscheidend: der konstante Systemprompt trägt den
    Cache-Breakpoint, alles Variable steht in `messages` dahinter.
    """
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [{"role": "user", "content": user_message}],
        # Structured Outputs: erzwingt gültiges JSON nach unserem Schema, statt
        # per Prompt um JSON zu bitten und hinterher zu reparieren.
        "output_config": {"format": {"type": "json_schema", "schema": RESPONSE_SCHEMA}},
    }


def _usage_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {}
    return {
        "input_tokens": getattr(usage, "input_tokens", 0) or 0,
        "output_tokens": getattr(usage, "output_tokens", 0) or 0,
        "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0) or 0,
    }


def _extract_json(message: Any) -> tuple[dict[str, Any] | None, str, str | None]:
    """(parsed, raw_text, error) aus einer Message ziehen."""
    if getattr(message, "stop_reason", None) == "refusal":
        return None, "", "Modell hat die Auswertung abgelehnt (stop_reason=refusal)."

    text = next(
        (block.text for block in message.content if getattr(block, "type", None) == "text"),
        "",
    )
    if getattr(message, "stop_reason", None) == "max_tokens":
        return None, text, "Antwort bei max_tokens abgeschnitten — JSON unvollständig."
    if not text:
        return None, "", "Keine Textausgabe im Modell-Response."

    try:
        return json.loads(text), text, None
    except json.JSONDecodeError as exc:
        # Sollte mit Structured Outputs nicht vorkommen; wenn doch, wird der
        # Rohtext trotzdem gespeichert, damit nachvollziehbar bleibt, was kam.
        return None, text, f"Antwort war kein gültiges JSON: {exc}"


class EvaluatorClient:
    def __init__(self, api_key: str, max_retries: int = 3, timeout: float = 120.0):
        if not api_key:
            raise EvaluationError(
                "Kein ANTHROPIC_API_KEY gesetzt — der Auswertungs-Layer braucht einen "
                "serverseitigen Key (.env, siehe .env.example). Ebene 1 läuft ohne."
            )
        # Das SDK wiederholt 429/5xx/Verbindungsfehler selbst mit Backoff.
        self._client = anthropic.Anthropic(
            api_key=api_key, max_retries=max_retries, timeout=timeout
        )

    # -- Sync ---------------------------------------------------------------
    def evaluate_sync(self, run_id: int, system_prompt: str, user_message: str) -> EvaluationResult:
        params = build_params(system_prompt, user_message)
        try:
            message = self._client.messages.create(**params)
        except anthropic.APIStatusError as exc:
            return EvaluationResult(
                run_id=run_id, parsed=None, raw_output="", model=MODEL,
                error=f"HTTP {exc.status_code}: {exc.message}",
            )
        except anthropic.APIConnectionError as exc:
            return EvaluationResult(
                run_id=run_id, parsed=None, raw_output="", model=MODEL,
                error=f"Verbindungsfehler: {exc}",
            )

        parsed, raw, error = _extract_json(message)
        return EvaluationResult(
            run_id=run_id,
            parsed=parsed,
            raw_output=raw,
            model=getattr(message, "model", MODEL),
            usage=_usage_dict(getattr(message, "usage", None)),
            error=error,
        )

    # -- Batch --------------------------------------------------------------
    def submit_batch(self, items: Iterable[tuple[int, str, str]]) -> str:
        """items = (run_id, system_prompt, user_message). Gibt die Batch-ID zurück."""
        requests = [
            Request(
                custom_id=f"run-{run_id}",
                params=MessageCreateParamsNonStreaming(
                    **build_params(system_prompt, user_message)
                ),
            )
            for run_id, system_prompt, user_message in items
        ]
        if not requests:
            raise EvaluationError("Leerer Batch.")
        return self._client.messages.batches.create(requests=requests).id

    def batch_status(self, batch_id: str) -> str:
        return self._client.messages.batches.retrieve(batch_id).processing_status

    def collect_batch(self, batch_id: str) -> list[EvaluationResult]:
        """Ergebnisse eines beendeten Batches einsammeln.

        Die Reihenfolge der Ergebnisse ist NICHT die der Anfragen — deshalb wird
        strikt über custom_id zugeordnet, nie über die Position.
        """
        results: list[EvaluationResult] = []
        for entry in self._client.messages.batches.results(batch_id):
            run_id = int(entry.custom_id.removeprefix("run-"))
            outcome = entry.result

            if outcome.type != "succeeded":
                detail = getattr(getattr(outcome, "error", None), "type", outcome.type)
                results.append(
                    EvaluationResult(
                        run_id=run_id, parsed=None, raw_output="", model=MODEL,
                        error=f"Batch-Ergebnis '{outcome.type}': {detail}",
                    )
                )
                continue

            parsed, raw, error = _extract_json(outcome.message)
            results.append(
                EvaluationResult(
                    run_id=run_id,
                    parsed=parsed,
                    raw_output=raw,
                    model=getattr(outcome.message, "model", MODEL),
                    usage=_usage_dict(getattr(outcome.message, "usage", None)),
                    error=error,
                )
            )
        return results
