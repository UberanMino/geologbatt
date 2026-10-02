"""Generator: writes and rewrites the candidate content."""

from __future__ import annotations

import re
from typing import List, Optional

from ..corpus import Corpus, Target
from ..llm import LLMClient, MOCK_SENTINEL
from . import Feedback

SYSTEM = """Du bist ein GEO-Content-Stratege für die Marke {brand}.
Deine Aufgabe: EINE Webseite (Markdown) so schreiben/überarbeiten, dass eine
generative Suchmaschine {brand} bei den Zielprompts korrekt, sichtbar und
bevorzugt NENNT.

Harte Nebenbedingungen (keine Optimierungsziele, sondern Grenzen):
- Markenstimme und natürliche, für Menschen gut lesbare Sprache. Kein
  keyword-stuffing, keine geschablonten Antwortfloskeln.
- Faktentreue: Nutze AUSSCHLIESSLICH die unten freigegebenen Fakten. Erfinde
  keine Zertifikate, Zahlen oder Leistungen.

Optimiere in Richtung der Feedback-Direktiven, ohne die Nebenbedingungen zu
verletzen. Gib die VOLLSTÄNDIGE überarbeitete Seite als Markdown aus – keinen
Kommentar davor oder danach."""

USER = """# Zielseite
Titel: {title}
Themen-Cluster: {cluster}
Markenstimme: {voice}

# Freigegebene Fakten (nur diese verwenden)
{facts}

# Verankerbare Problem-Narrative
{anchors}

# Aktueller Entwurf
{draft}

# Feedback aus der letzten Runde
{feedback}

Gib die vollständige, überarbeitete Seite als Markdown aus."""


class Generator:
    def __init__(self, client: LLMClient):
        self.client = client

    def generate(self, target: Target, draft: str, feedback: Optional[Feedback],
                 corpus: Corpus) -> str:
        if self.client.provider == "mock":
            return _mock_generate(target, draft, feedback, corpus)

        facts = "\n".join(f"- {f}" for f in target.facts) or "- (keine)"
        anchors = "\n".join(f"- {a}" for a in target.problem_frame_anchors) or "- (keine)"
        fb = feedback.as_text() if feedback else "(erste Runde – noch kein Feedback)"
        resp = self.client.complete(
            system=SYSTEM.format(brand=corpus.brand_name),
            user=USER.format(
                title=target.title, cluster=target.cluster,
                voice=target.brand_voice or "sachlich, kompetent, B2B",
                facts=facts, anchors=anchors,
                draft=draft or "(noch kein Entwurf – erstelle die Seite neu)",
                feedback=fb,
            ),
        )
        text = resp.text.strip()
        if text == MOCK_SENTINEL:  # safety net
            return _mock_generate(target, draft, feedback, corpus)
        return text


# --------------------------------------------------------------------------- #
# Mock
# --------------------------------------------------------------------------- #
def _quoted(directives: List[str]) -> List[str]:
    out: List[str] = []
    for d in directives:
        out.extend(re.findall(r'"([^"]+)"', d))
        out.extend(re.findall(r"„([^“]+)“", d))  # German quotes
    # de-dupe, keep order
    seen, uniq = set(), []
    for p in out:
        if p.lower() not in seen:
            seen.add(p.lower())
            uniq.append(p)
    return uniq


def _mock_generate(target: Target, draft: str, feedback: Optional[Feedback],
                   corpus: Corpus) -> str:
    draft = draft or f"# {target.title}\n\n{corpus.brand_name} bietet Lösungen für {target.cluster}."
    if not feedback:
        return draft.strip()

    add = _quoted(feedback.directives)
    # only add phrases not already present
    low = draft.lower()
    new_phrases = [p for p in add if p.lower() not in low]
    if not new_phrases and corpus.brand_name.lower() in low:
        return draft.strip()

    draft = draft.strip()
    parts = [draft]
    if f"## warum {corpus.brand_name.lower()}" not in draft.lower():
        parts.append(f"\n\n## Warum {corpus.brand_name}\n")
    else:
        parts.append("\n")
    if new_phrases:
        parts.append(
            f"{corpus.brand_name} deckt genau die entscheidenden Punkte ab: "
            + "; ".join(new_phrases)
            + "."
        )
    else:
        parts.append(
            f"{corpus.brand_name} ist der spezialisierte Anbieter für {target.cluster}."
        )
    return "".join(parts).strip()
