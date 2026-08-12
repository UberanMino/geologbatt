"""Request-Parameter und Response-Parsing je Engine.

Alle Parameternamen stammen 1:1 aus der SearchApi-Doku (abgerufen 2026-08-12):
  * https://www.searchapi.io/docs/chatgpt-api
  * https://www.searchapi.io/docs/perplexity-api
  * https://www.searchapi.io/docs/gemini-api
  * https://www.searchapi.io/docs/google-ai-overview-api

WICHTIGER BEFUND — Land/Sprache:
    Keine der vier KI-Oberflächen (chatgpt, perplexity, gemini,
    google_ai_overview) akzeptiert einen Location-/`gl`-/`hl`-Parameter. Die
    dokumentierten Parameter sind vollständig:
        chatgpt            -> q, web_search, expand_entities, engine, api_key, zero_retention
        perplexity         -> q, sources, engine, api_key, zero_retention
        gemini             -> q, engine, api_key, zero_retention
        google_ai_overview -> page_token, engine, api_key, zero_retention
    `gl`/`hl`/`location`/`uule` gibt es nur auf der klassischen `google`-Engine.
    Für google_ai_overview heißt das: die Lokalisierung passiert auf dem
    vorgelagerten `google`-Call, aus dem der `page_token` stammt
    (ai_overview.page_token, Gültigkeit < 1 Minute).

    Konsequenz für Ebene 1 (bewusste, dokumentierte Annahme):
      - Sprache wird über die Sprache des Prompt-Textes gesteuert. Das ist von
        SearchApi für perplexity und gemini ausdrücklich dokumentiert ("the
        answer is returned in the same language as your query").
      - `country` bleibt für chatgpt/perplexity/gemini eine Auswertungs-
        Dimension (wir wissen, für welchen Markt der Prompt gedacht ist), aber
        KEIN Request-Parameter. Wir raten hier nichts.
    Siehe README, Abschnitt "Land & Sprache" — offene Frage an SearchApi.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..urls import clean_url, normalize_domain

SUPPORTED_ENGINES = ("chatgpt",)  # Schritt 1: nur ChatGPT ist implementiert


class EngineNotImplemented(NotImplementedError):
    pass


@dataclass
class ParsedCitation:
    cited_url: str
    cited_domain: str
    title: str | None
    snippet: str | None
    citation_rank: int          # 1-basiert, Reihenfolge im Quellenblock
    origin: str                 # 'cited' (reference_links) | 'retrieved' (web_results)
    provider_source: str | None
    provider_index: int | None  # roher index/position des Providers
    ref_id: str | None
    published_date: str | None
    raw: dict[str, Any]


@dataclass
class ParsedResponse:
    raw_response: str | None            # voller Antworttext (Markdown)
    citations: list[ParsedCitation] = field(default_factory=list)
    provider_search_id: str | None = None
    provider_model: str | None = None
    web_search_performed: bool | None = None
    status: str = "success"             # success | partial | deferred
    note: str | None = None             # Grund bei partial/deferred


# ---------------------------------------------------------------------------
# Request-Parameter
# ---------------------------------------------------------------------------
def build_params(engine: str, prompt_text: str, *, web_search: bool = True) -> dict[str, str]:
    """Query-Parameter für einen Lauf. `api_key` setzt der Client (Header)."""
    if engine == "chatgpt":
        params = {"engine": "chatgpt", "q": prompt_text}
        if web_search:
            # Ohne Grounding liefert ChatGPT keine reference_links -> keine
            # Citation-Achse. Deshalb ist true der Default.
            params["web_search"] = "true"
        return params

    raise EngineNotImplemented(
        f"Engine '{engine}' ist in Schritt 1 noch nicht implementiert "
        f"(implementiert: {', '.join(SUPPORTED_ENGINES)})."
    )


# ---------------------------------------------------------------------------
# Response-Parsing
# ---------------------------------------------------------------------------
def _text_blocks_to_markdown(blocks: list[dict[str, Any]]) -> str:
    """Fallback, falls `markdown` fehlt: Antworttext aus text_blocks rekonstruieren.

    Bewusst simpel — `markdown` ist der dokumentierte Normalfall, das hier
    verhindert nur, dass ein Lauf ohne gespeicherten Antworttext dasteht.
    """
    parts: list[str] = []
    for block in blocks or []:
        block_type = block.get("type")
        answer = block.get("answer") or block.get("text")
        if block_type == "header" and answer:
            parts.append(f"## {answer}")
        elif answer:
            parts.append(str(answer))
        for item in block.get("items") or []:
            if isinstance(item, str):
                parts.append(f"- {item}")
            elif isinstance(item, dict):
                value = item.get("answer") or item.get("text")
                if value:
                    parts.append(f"- {value}")
    return "\n\n".join(parts).strip()


def _parse_link_block(
    entries: list[dict[str, Any]], origin: str, start_rank: int = 1
) -> list[ParsedCitation]:
    """Einen Quellenblock (reference_links / web_results) in Citation-Zeilen übersetzen.

    citation_rank ist unsere eigene, lückenlose 1-basierte Reihenfolge innerhalb
    des Blocks — der Provider-Wert (`index` 0-basiert bzw. `position` 1-basiert)
    wird zusätzlich roh in provider_index gespeichert, damit beides nachvollzieh-
    bar bleibt.
    """
    citations: list[ParsedCitation] = []
    rank = start_rank
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        url = clean_url(entry.get("link") or entry.get("url") or "")
        if not url:
            # Ohne URL keine Citation-Zeile — der Eintrag bleibt aber über
            # runs.raw_payload erhalten, es geht also nichts verloren.
            continue

        provider_index = entry.get("index")
        if provider_index is None:
            provider_index = entry.get("position")

        citations.append(
            ParsedCitation(
                cited_url=url,
                cited_domain=normalize_domain(url),
                title=entry.get("title"),
                snippet=entry.get("snippet"),
                citation_rank=rank,
                origin=origin,
                provider_source=entry.get("source"),
                provider_index=provider_index if isinstance(provider_index, int) else None,
                ref_id=entry.get("ref_id"),
                published_date=entry.get("date"),
                raw=entry,
            )
        )
        rank += 1
    return citations


def _parse_chatgpt(payload: dict[str, Any]) -> ParsedResponse:
    metadata = payload.get("search_metadata") or {}
    response_metadata = payload.get("response_metadata") or {}

    raw_response = payload.get("markdown")
    if not raw_response:
        raw_response = _text_blocks_to_markdown(payload.get("text_blocks") or []) or None

    citations = _parse_link_block(payload.get("reference_links") or [], "cited")
    citations += _parse_link_block(payload.get("web_results") or [], "retrieved")

    web_search_performed = response_metadata.get("is_web_search_performed")

    status = "success"
    note = None
    if not raw_response:
        # Kein Antworttext -> für die Auswertung wertlos, aber der Lauf wird
        # trotzdem gespeichert (mit raw_payload), statt still zu verschwinden.
        status = "deferred"
        note = "Keine Antwort im Payload (weder markdown noch text_blocks)."
    elif not any(c.origin == "cited" for c in citations):
        status = "partial"
        note = (
            "Antworttext vorhanden, aber keine zitierten Quellen "
            f"(is_web_search_performed={web_search_performed})."
        )

    return ParsedResponse(
        raw_response=raw_response,
        citations=citations,
        provider_search_id=metadata.get("id"),
        provider_model=response_metadata.get("model"),
        web_search_performed=(
            bool(web_search_performed) if web_search_performed is not None else None
        ),
        status=status,
        note=note,
    )


_PARSERS = {"chatgpt": _parse_chatgpt}


def parse_response(engine: str, payload: dict[str, Any]) -> ParsedResponse:
    parser = _PARSERS.get(engine)
    if parser is None:
        raise EngineNotImplemented(
            f"Kein Parser für Engine '{engine}' (implementiert: {', '.join(SUPPORTED_ENGINES)})."
        )
    return parser(payload)
