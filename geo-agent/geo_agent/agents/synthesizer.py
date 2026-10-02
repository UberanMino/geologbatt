"""Synthesizer: the third agent.

Combines the Generator's draft with how the Judge answered each *training*
prompt (never the held-out validation prompts) and produces concrete,
actionable directives for the next Generator turn. Specific feedback beats a
long list (Self-Refine, Madaan et al. 2023), so we keep directives few and
pointed, and we set ``converged`` when there is nothing left worth changing.
"""

from __future__ import annotations

from typing import List

from ..corpus import Corpus, Target
from ..llm import LLMClient, LLMError, MOCK_SENTINEL
from ..scoring import normalize
from . import Evaluation, Feedback

SYSTEM = """Du bist ein GEO-Optimierungsstratege. Du bekommst (a) den aktuellen
Seitenentwurf und (b) wie eine geerdete Suchmaschine auf die Zielprompts
geantwortet hat, inklusive Metriken. Erzeuge ein knappes, präzises Feedback für
den Generator.

Regeln:
- Spezifisch schlägt viel: max. 4 Direktiven, jede konkret und umsetzbar.
- Nenne wörtlich (in Anführungszeichen "…"), welche Fakten/Anker fehlen.
- Respektiere die Nebenbedingungen: Markenstimme, menschliche Lesbarkeit,
  Faktentreue (nur freigegebene Fakten).
- Setze "converged": true, wenn die Marke bei allen Prompts an Position 1 genannt
  wird, das Problem-Narrativ präsent ist und die Kernfakten korrekt ankommen.

Gib NUR JSON zurück:
{"diagnosis": "...", "directives": ["...", "..."], "converged": false}"""

USER = """# Aktueller Entwurf
{draft}

# Ergebnisse je Trainings-Prompt
{results}

Erzeuge das Feedback-JSON."""


class Synthesizer:
    def __init__(self, client: LLMClient):
        self.client = client

    def synthesize(self, target: Target, draft: str, evals: List[Evaluation],
                   corpus: Corpus) -> Feedback:
        if self.client.provider == "mock":
            return _mock_synthesize(target, draft, evals, corpus)

        results = "\n\n".join(_render_eval(e, corpus) for e in evals)
        try:
            data = self.client.complete_json(
                system=SYSTEM,
                user=USER.format(draft=draft, results=results),
            )
            return Feedback(
                diagnosis=str(data.get("diagnosis", "")),
                directives=list(data.get("directives", [])),
                converged=bool(data.get("converged", False)),
            )
        except LLMError:
            return _mock_synthesize(target, draft, evals, corpus)


def _render_eval(e: Evaluation, corpus: Corpus) -> str:
    s = e.score
    return (
        f"Prompt [{e.prompt.id}] ({e.prompt.mode}): {e.prompt.text}\n"
        f"  Marke genannt: {s.brand_mentioned} | Position: {s.brand_position} | "
        f"aus Kandidat zitiert: {s.cited_from_candidate} | "
        f"Problem-Frame: {s.problem_frame_present} | "
        f"Fakten: {s.claims_hit}/{s.claims_total} | "
        f"Wettbewerber genannt: {', '.join(s.competitors_mentioned) or '-'}\n"
        f"  Antwortauszug: {e.answer.text[:300]}"
    )


# --------------------------------------------------------------------------- #
# Mock
# --------------------------------------------------------------------------- #
def _mock_synthesize(target: Target, draft: str, evals: List[Evaluation],
                     corpus: Corpus, max_directives: int = 4) -> Feedback:
    low = normalize(draft)
    brand_named = normalize(corpus.brand_name) in low

    # collect signals that are missing from the draft, prioritised by prompts
    # where the brand is not (yet) mentioned
    missing_ordered: List[str] = []
    seen = set()

    def add(sig: str):
        key = normalize(sig)
        if key and key not in seen and key not in low:
            seen.add(key)
            missing_ordered.append(sig)

    for e in sorted(evals, key=lambda x: (x.score.brand_mentioned, x.score.brand_position or 99)):
        for a in e.prompt.problem_frame_anchors:
            add(a)
        for f in e.prompt.facts:
            add(f)

    all_mentioned = all(e.score.brand_mentioned for e in evals)
    all_pos1 = all((e.score.brand_position == 1) for e in evals)
    all_frame = all(e.score.problem_frame_present for e in evals)
    converged = bool(evals) and all_mentioned and all_pos1 and all_frame and not missing_ordered

    directives: List[str] = []
    if not brand_named:
        directives.append(
            f'Nenne die Marke "{corpus.brand_name}" explizit und mehrfach im Fließtext.'
        )
    take = missing_ordered[:max_directives - len(directives)]
    if take:
        quoted = ", ".join(f'"{t}"' for t in take)
        directives.append(f"Verankere die fehlenden Signale wörtlich: {quoted}.")

    n_missing = sum(1 for e in evals if not e.score.brand_mentioned)
    diagnosis = (
        f"Marke in {len(evals) - n_missing}/{len(evals)} Trainings-Prompts genannt. "
        + ("Konvergiert – keine sinnvollen Änderungen mehr offen."
           if converged else
           f"{len(missing_ordered)} verankerbare Signale fehlen noch im Entwurf.")
    )
    return Feedback(diagnosis=diagnosis, directives=directives, converged=converged)
