"""Deterministic, offline heuristics shared by the mock agents.

These make the mock understand the *content*: the candidate's strength on a
prompt is how many of that prompt's facts and problem-frame anchors it actually
contains. So when the Generator adds what the Synthesizer asked for, the mock
Judge really does start naming the brand and ranking it higher. The loop
converges because the content improved, not because a counter ticked.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from ..corpus import Prompt
from ..scoring import normalize


def candidate_signals(prompt: Prompt, candidate_content: str) -> Tuple[List[str], List[str]]:
    """Return (facts_present, anchors_present) found in the candidate content."""
    norm = normalize(candidate_content)
    facts = [f for f in prompt.facts if normalize(f) in norm]
    anchors = [a for a in prompt.problem_frame_anchors if normalize(a) in norm]
    return facts, anchors


def candidate_strength(prompt: Prompt, candidate_content: str, brand_aliases: List[str]) -> float:
    """0..100 proxy for how compelling the candidate is for this prompt."""
    facts, anchors = candidate_signals(prompt, candidate_content)
    total = max(1, len(prompt.facts) + len(prompt.problem_frame_anchors))
    coverage = (len(facts) + len(anchors)) / total
    norm = normalize(candidate_content)
    brand_hits = sum(norm.count(normalize(a)) for a in brand_aliases)
    brand_bonus = min(0.15, 0.03 * brand_hits)  # naming yourself helps, with a cap
    return round(100 * min(1.0, coverage + brand_bonus), 1)


def ranked_providers(prompt: Prompt, brand_name: str,
                     logbatt_strength: float, top_k_competitors: int = 3
                     ) -> List[Tuple[str, float]]:
    """Rank brand + top competitors by strength (desc)."""
    ranked: List[Tuple[str, float]] = [(brand_name, logbatt_strength)]
    comps = sorted(prompt.competitors.items(), key=lambda t: -t[1])[:top_k_competitors]
    ranked.extend(comps)
    ranked.sort(key=lambda t: -t[1])
    return ranked
