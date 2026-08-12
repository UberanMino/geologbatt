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

SUPPORTED_ENGINES = ("chatgpt", "perplexity", "gemini", "google_ai_overview")


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
def build_params(
    engine: str,
    prompt_text: str,
    *,
    web_search: bool = True,
    country: str | None = None,
    language: str | None = None,
    page_token: str | None = None,
) -> dict[str, str]:
    """Query-Parameter für einen Lauf. `api_key` setzt der Client (Header).

    `country`/`language` werden NUR dort gesetzt, wo SearchApi sie dokumentiert
    — also beim vorgelagerten `google`-Call für die AI Overview. Für die drei
    übrigen Engines gibt es keinen solchen Parameter (siehe Modul-Docstring);
    dort werden sie bewusst ignoriert statt geraten.
    """
    if engine == "chatgpt":
        params = {"engine": "chatgpt", "q": prompt_text}
        if web_search:
            # Ohne Grounding liefert ChatGPT keine reference_links -> keine
            # Citation-Achse. Deshalb ist true der Default.
            params["web_search"] = "true"
        return params

    if engine == "perplexity":
        # `sources` ist der einzige zusätzliche dokumentierte Parameter.
        # 'web' ist ohnehin der Default; explizit gesetzt bleibt es stabil,
        # falls SearchApi den Default später ändert.
        return {"engine": "perplexity", "q": prompt_text, "sources": "web"}

    if engine == "gemini":
        # Gemini kennt ausschließlich `q`.
        return {"engine": "gemini", "q": prompt_text}

    if engine == "google_ai_overview":
        # Zweischritt: der page_token stammt aus einem vorgelagerten
        # `google`-Call (siehe build_google_params) und ist unter 1 Minute
        # gültig — beide Requests müssen unmittelbar hintereinander laufen.
        if not page_token:
            raise EngineNotImplemented(
                "google_ai_overview braucht einen page_token aus dem "
                "vorgelagerten google-Call (ai_overview.page_token)."
            )
        return {"engine": "google_ai_overview", "page_token": page_token}

    raise EngineNotImplemented(
        f"Unbekannte Engine '{engine}' (implementiert: {', '.join(SUPPORTED_ENGINES)})."
    )


def build_google_params(
    prompt_text: str, *, country: str | None = None, language: str | None = None
) -> dict[str, str]:
    """Parameter des vorgelagerten `google`-Calls für die AI Overview.

    Das ist die EINZIGE Stelle, an der Land und Sprache echt steuerbar sind:
    `gl` (Land) und `hl` (Oberflächensprache) sind auf der klassischen
    google-Engine dokumentiert. Aus der Antwort brauchen wir
    `ai_overview.page_token`.
    """
    params = {"engine": "google", "q": prompt_text}
    if country:
        params["gl"] = country.lower()
    if language:
        params["hl"] = language.lower()
    return params


def extract_page_token(payload: dict[str, Any]) -> str | None:
    """`ai_overview.page_token` aus der google-Antwort ziehen.

    Fehlt er, hat Google für diese Suche schlicht keine AI Overview
    ausgespielt — das ist ein normaler Zustand, kein Fehler, und wird als
    `deferred` protokolliert.
    """
    overview = payload.get("ai_overview")
    if isinstance(overview, dict):
        token = overview.get("page_token")
        if isinstance(token, str) and token:
            return token
    return None


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


def _parse_reference_links_engine(payload: dict[str, Any]) -> ParsedResponse:
    """Perplexity, Gemini und Google AI Overview.

    Alle drei liefern dieselbe Form: `markdown` + `text_blocks` als Antwort und
    `reference_links` als Quellenblock. Anders als ChatGPT haben sie kein
    `web_results` — es gibt also nur `origin = 'cited'`.
    """
    metadata = payload.get("search_metadata") or {}
    response_metadata = payload.get("response_metadata") or {}

    raw_response = payload.get("markdown")
    if not raw_response:
        raw_response = _text_blocks_to_markdown(payload.get("text_blocks") or []) or None

    citations = _parse_link_block(payload.get("reference_links") or [], "cited")

    status = "success"
    note = None
    if not raw_response:
        # Bei google_ai_overview der Normalfall, wenn Google keine Overview
        # ausspielt — protokollieren, nicht verlieren.
        status = "deferred"
        note = "Keine Antwort im Payload (weder markdown noch text_blocks)."
    elif not citations:
        status = "partial"
        note = "Antworttext vorhanden, aber keine zitierten Quellen."

    return ParsedResponse(
        raw_response=raw_response,
        citations=citations,
        provider_search_id=metadata.get("id"),
        provider_model=response_metadata.get("model"),
        # Diese Engines grounden immer im Web; ein Flag wie bei ChatGPT gibt es
        # nicht, deshalb bleibt das Feld bewusst leer statt geraten.
        web_search_performed=None,
        status=status,
        note=note,
    )


_PARSERS = {
    "chatgpt": _parse_chatgpt,
    "perplexity": _parse_reference_links_engine,
    "gemini": _parse_reference_links_engine,
    "google_ai_overview": _parse_reference_links_engine,
}


def parse_response(engine: str, payload: dict[str, Any]) -> ParsedResponse:
    parser = _PARSERS.get(engine)
    if parser is None:
        raise EngineNotImplemented(
            f"Kein Parser für Engine '{engine}' (implementiert: {', '.join(SUPPORTED_ENGINES)})."
        )
    return parser(payload)
