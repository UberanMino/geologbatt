"""Judge: answers the prompt like a grounded generative search engine.

It sees a document set = the candidate (always S1) + the competitor cards. In
``sources_only`` grounding it must answer from those documents alone, which is
what makes the answer maximally sensitive to the one thing that changes between
iterations (the candidate). ``blended`` additionally allows parametric
knowledge and is only a secondary realism check — see README.
"""

from __future__ import annotations

from typing import List

from ..corpus import Corpus, Prompt, SourceDoc
from ..llm import LLMClient, MOCK_SENTINEL
from ._mock import candidate_signals, candidate_strength, ranked_providers
from . import JudgeAnswer

SYSTEM_SOURCES_ONLY = """Du bist eine generative Suchmaschine (wie Perplexity).
Beantworte die Nutzerfrage AUSSCHLIESSLICH gestützt auf die beigefügten Quellen.
Nutze KEIN externes/eigenes Wissen. Wenn die Quellen einen Anbieter nicht
stützen, nenne ihn nicht.

- Empfiehl konkrete Anbieter und begründe knapp, gestützt auf die Quellen.
- Zitiere inline mit [S1], [S2], … welche Quelle welche Aussage trägt.
- Schließe mit einer Zeile:
  "Genannte Anbieter (in Reihenfolge): A, B, C"
"""

SYSTEM_BLENDED = """Du bist eine generative Suchmaschine. Beantworte die
Nutzerfrage gestützt auf die beigefügten Quellen UND dein internes Wissen.
Zitiere Quellen inline mit [S1], [S2] … wo du dich auf sie stützt.
Schließe mit einer Zeile:
"Genannte Anbieter (in Reihenfolge): A, B, C"
"""

USER = """# Nutzerfrage
{prompt}

# Quellen
{sources}

Beantworte die Frage wie eine generative Suchmaschine."""


def build_doc_set(prompt: Prompt, candidate_content: str, corpus: Corpus) -> List[SourceDoc]:
    """S1 = candidate, then one card per named competitor (byte-identical)."""
    candidate = SourceDoc(
        id="S1",
        title=f"Kandidatenseite ({corpus.brand_domain})",
        domain=corpus.brand_domain,
        kind="candidate",
        content=candidate_content,
    )
    docs = [candidate]
    cards = corpus.competitor_cards(list(prompt.competitors.keys()))
    for i, card in enumerate(cards, start=2):
        docs.append(
            SourceDoc(id=f"S{i}", title=card.title, domain=card.domain,
                      kind="competitor", content=card.content,
                      signals=card.signals, base_strength=card.base_strength)
        )
    return docs


class Judge:
    def __init__(self, client: LLMClient, grounding: str = "sources_only"):
        self.client = client
        self.grounding = grounding

    def answer(self, prompt: Prompt, docs: List[SourceDoc], corpus: Corpus) -> JudgeAnswer:
        if self.client.provider == "mock":
            return _mock_answer(prompt, docs, corpus)

        sys = SYSTEM_SOURCES_ONLY if self.grounding == "sources_only" else SYSTEM_BLENDED
        sources = "\n\n".join(
            f"[{d.id}] {d.title} — {d.domain}\n{d.content}" for d in docs
        )
        resp = self.client.complete(
            system=sys, user=USER.format(prompt=prompt.text, sources=sources)
        )
        text = resp.text.strip()
        if text == MOCK_SENTINEL:
            return _mock_answer(prompt, docs, corpus)
        return JudgeAnswer(prompt_id=prompt.id, text=text)


# --------------------------------------------------------------------------- #
# Mock
# --------------------------------------------------------------------------- #
def _mock_answer(prompt: Prompt, docs: List[SourceDoc], corpus: Corpus) -> JudgeAnswer:
    candidate = docs[0]
    aliases = [corpus.brand_name] + corpus.brand_aliases
    strength = candidate_strength(prompt, candidate.content, aliases)
    threshold = 20.0 if prompt.mode == "swap" else 40.0

    ranked = ranked_providers(prompt, corpus.brand_name, strength)
    # decide inclusion: brand only if above threshold; competitors if tracked > 0
    listed = []
    for name, sc in ranked:
        if name == corpus.brand_name:
            if strength >= threshold:
                listed.append((name, sc))
        elif sc > 0:
            listed.append((name, sc))

    facts, anchors = candidate_signals(prompt, candidate.content)
    lines = [f"Für die Anfrage „{prompt.text}“ kommen folgende Anbieter infrage:", ""]
    order_names = []
    for rank, (name, _sc) in enumerate(listed, 1):
        order_names.append(name)
        if name == corpus.brand_name:
            basis = ", ".join((facts + anchors)[:3]) or "spezialisierte Lösung"
            lines.append(
                f"{rank}. **{corpus.brand_name}** — deckt laut Kandidatenseite ab: "
                f"{basis}. (Quelle: Kandidatenseite [S1])"
            )
        else:
            dom = next((d.domain for d in docs if d.title == name), "")
            sid = next((d.id for d in docs if d.title == name), "")
            cite = f" [{sid}]" if sid else ""
            lines.append(f"{rank}. **{name}** — etablierter Anbieter{(' (' + dom + ')') if dom else ''}.{cite}")
    if corpus.brand_name not in order_names:
        lines.append(
            f"\n(Hinweis: {corpus.brand_name} wird auf Basis der vorliegenden Quellen "
            f"für diese Frage nicht empfohlen.)"
        )
    lines.append("")
    lines.append("Genannte Anbieter (in Reihenfolge): " + ", ".join(order_names))
    return JudgeAnswer(prompt_id=prompt.id, text="\n".join(lines))
