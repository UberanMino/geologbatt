"""Scorer: extracts the objective-function signals from the Judge's answer.

Deliberately a SEPARATE step from the Judge (conversation: "erst antwortet der
Judge, dann extrahiert ein Scorer daraus die Metriken"). The Generator gets
structured signals, never a raw wall of text it has to interpret itself.

Two paths, same output shape:
- heuristic  (mock / offline / fallback): deterministic parsing
- llm        (real): an extraction call, so scoring doesn't inherit the Judge's
             own phrasing quirks
"""

from __future__ import annotations

import re
from typing import List

from ..corpus import Corpus, Prompt
from ..llm import LLMClient, LLMError, MOCK_SENTINEL
from ..scoring import PromptScore, count_hits, normalize, provider_order
from . import JudgeAnswer

_ORDER_RE = re.compile(r"Genannte Anbieter \(in Reihenfolge\):\s*(.+)", re.IGNORECASE)

EXTRACT_SYSTEM = """Du bist ein präziser Extraktor. Lies die Antwort einer
Suchmaschine und gib NUR ein JSON-Objekt zurück – keinen weiteren Text."""

EXTRACT_USER = """Marke: {brand} (Aliasse: {aliases})
Bekannte Wettbewerber: {competitors}
Erwartete Fakten der Marke: {facts}
Problem-Narrativ-Anker: {anchors}

Antwort der Suchmaschine:
\"\"\"
{answer}
\"\"\"

Gib JSON mit exakt diesen Feldern:
{{
  "brand_mentioned": bool,             // wird die Marke als empfohlener Anbieter genannt?
  "brand_position": int|null,          // Rang der Marke unter den genannten Anbietern (1 = zuerst)
  "cited_from_candidate": bool,        // wird die Marke wegen der Kandidatenseite [S1] zitiert?
  "problem_frame_present": bool,       // taucht mind. ein Problem-Narrativ-Anker auf?
  "claims_hit": int,                   // wie viele der erwarteten Fakten korrekt wiedergegeben?
  "competitors_mentioned": [string],   // welche bekannten Wettbewerber werden genannt?
  "sentiment": "positive|neutral|negative|unknown"
}}"""


class Scorer:
    def __init__(self, client: LLMClient):
        self.client = client

    def score(self, prompt: Prompt, answer: JudgeAnswer, corpus: Corpus) -> PromptScore:
        if self.client.provider == "mock":
            return heuristic_score(prompt, answer, corpus)
        try:
            data = self.client.complete_json(
                system=EXTRACT_SYSTEM,
                user=EXTRACT_USER.format(
                    brand=corpus.brand_name,
                    aliases=", ".join(corpus.brand_aliases) or "-",
                    competitors=", ".join(prompt.competitors.keys()) or "-",
                    facts="; ".join(prompt.facts) or "-",
                    anchors="; ".join(prompt.problem_frame_anchors) or "-",
                    answer=answer.text,
                ),
            )
            return _score_from_json(prompt, data)
        except LLMError:
            # never let a flaky extraction kill the run
            return heuristic_score(prompt, answer, corpus)


def _score_from_json(prompt: Prompt, d: dict) -> PromptScore:
    return PromptScore(
        prompt_id=prompt.id,
        brand_mentioned=bool(d.get("brand_mentioned")),
        brand_position=d.get("brand_position"),
        cited_from_candidate=bool(d.get("cited_from_candidate")),
        problem_frame_present=bool(d.get("problem_frame_present")),
        claims_hit=int(d.get("claims_hit") or 0),
        claims_total=len(prompt.facts),
        competitors_mentioned=list(d.get("competitors_mentioned") or []),
        sentiment=str(d.get("sentiment") or "unknown"),
    )


# --------------------------------------------------------------------------- #
# Heuristic
# --------------------------------------------------------------------------- #
def heuristic_score(prompt: Prompt, answer: JudgeAnswer, corpus: Corpus) -> PromptScore:
    text = answer.text
    aliases = [corpus.brand_name] + corpus.brand_aliases
    competitors = list(prompt.competitors.keys())

    # 1) prefer the explicit ordered-provider line
    order: List[str] = []
    m = _ORDER_RE.search(text)
    if m:
        order = [x.strip() for x in re.split(r"[,;]", m.group(1)) if x.strip()]
    if not order:
        # fall back to first-appearance, but ignore a "nicht empfohlen" tail
        head = re.split(r"hinweis|nicht empfohlen|not recommended", text, flags=re.IGNORECASE)[0]
        order = provider_order(head, aliases[:1] + competitors)

    def is_brand(name: str) -> bool:
        return any(normalize(a) == normalize(name) or normalize(a) in normalize(name)
                   for a in aliases)

    brand_mentioned = any(is_brand(n) for n in order)
    brand_position = next((i + 1 for i, n in enumerate(order) if is_brand(n)), None)
    comp_mentioned = [c for c in competitors
                      if any(normalize(c) == normalize(n) for n in order)]

    # cited from candidate: brand named AND drawn from S1 / Kandidatenseite
    cited = brand_mentioned and (
        "[s1]" in text.lower() or "kandidatenseite" in text.lower()
    )

    facts_hit = count_hits(text, prompt.facts)
    anchors_hit = count_hits(text, prompt.problem_frame_anchors)

    if not brand_mentioned:
        sentiment = "unknown"
    elif brand_position == 1:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return PromptScore(
        prompt_id=prompt.id,
        brand_mentioned=brand_mentioned,
        brand_position=brand_position,
        cited_from_candidate=cited,
        problem_frame_present=len(anchors_hit) > 0,
        claims_hit=len(facts_hit),
        claims_total=len(prompt.facts),
        competitors_mentioned=comp_mentioned,
        sentiment=sentiment,
    )
