"""Objective function for the loop.

The whole point of the conversation was: *"was ankam" ist zu vage, um darauf zu
optimieren* — so we decompose "what arrived" into a handful of measurable
signals and combine them into one composite score the Synthesizer can push on.

This module is pure and deterministic. The Scorer agent may fill a
``PromptScore`` either via an LLM extraction call or via the heuristic parser
here; the maths that turns a ``PromptScore`` into a number lives in one place so
both the real and the mock paths agree.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


# --------------------------------------------------------------------------- #
# Text helpers (shared by the mock Judge and the heuristic Scorer)
# --------------------------------------------------------------------------- #
def normalize(text: str) -> str:
    """Lowercase + strip accents so 'Quarantäne' matches 'quarantane'."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def contains(haystack: str, needle: str) -> bool:
    return normalize(needle) in normalize(haystack)


def count_hits(text: str, needles: List[str]) -> List[str]:
    """Return the subset of ``needles`` that appear in ``text``."""
    norm = normalize(text)
    return [n for n in needles if normalize(n) in norm]


def provider_order(answer: str, brands: List[str]) -> List[str]:
    """Order the brands by first appearance in the answer.

    A crude proxy for the "position" an engine assigns to each provider, which
    is exactly what Peec's ``position`` column measures.
    """
    norm = normalize(answer)
    found = []
    for b in brands:
        idx = norm.find(normalize(b))
        if idx >= 0:
            found.append((idx, b))
    found.sort(key=lambda t: t[0])
    return [b for _, b in found]


# --------------------------------------------------------------------------- #
# Weights
# --------------------------------------------------------------------------- #
@dataclass
class Weights:
    """How much each signal contributes to the composite (should sum to ~1)."""

    mention: float = 0.35
    position: float = 0.20
    cited_from_candidate: float = 0.20
    problem_frame: float = 0.10
    claims: float = 0.15

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> "Weights":
        if not d:
            return cls()
        known = {k: v for k, v in d.items() if k in cls().__dict__}
        return cls(**known)


def _position_score(position: Optional[int]) -> float:
    """1.0 at rank 1, decaying; 0 if unranked. Mirrors 'niedriger = besser'."""
    if not position or position < 1:
        return 0.0
    return max(0.0, 1.0 - (position - 1) * 0.2)


# --------------------------------------------------------------------------- #
# Per-prompt score
# --------------------------------------------------------------------------- #
@dataclass
class PromptScore:
    prompt_id: str
    brand_mentioned: bool = False
    brand_position: Optional[int] = None
    cited_from_candidate: bool = False
    problem_frame_present: bool = False
    claims_hit: int = 0
    claims_total: int = 0
    competitors_mentioned: List[str] = field(default_factory=list)
    sentiment: str = "unknown"  # positive | neutral | negative | unknown
    notes: str = ""

    def composite(self, w: Optional[Weights] = None) -> float:
        w = w or Weights()
        claims_ratio = (self.claims_hit / self.claims_total) if self.claims_total else 0.0
        score = (
            w.mention * (1.0 if self.brand_mentioned else 0.0)
            + w.position * _position_score(self.brand_position)
            + w.cited_from_candidate * (1.0 if self.cited_from_candidate else 0.0)
            + w.problem_frame * (1.0 if self.problem_frame_present else 0.0)
            + w.claims * claims_ratio
        )
        return round(score, 4)

    def as_dict(self, w: Optional[Weights] = None) -> dict:
        d = asdict(self)
        d["composite"] = self.composite(w)
        return d


# --------------------------------------------------------------------------- #
# Aggregation across a prompt set (a cluster, or its train / val split)
# --------------------------------------------------------------------------- #
@dataclass
class Aggregate:
    n: int
    mean_composite: float
    mention_rate: float
    avg_position: Optional[float]
    cited_from_candidate_rate: float
    problem_frame_rate: float
    mean_claims_ratio: float
    competitor_counter: Dict[str, int]

    def as_dict(self) -> dict:
        return asdict(self)


def aggregate(scores: List[PromptScore], w: Optional[Weights] = None) -> Aggregate:
    w = w or Weights()
    n = len(scores)
    if n == 0:
        return Aggregate(0, 0.0, 0.0, None, 0.0, 0.0, 0.0, {})

    mentioned = [s for s in scores if s.brand_mentioned]
    positions = [s.brand_position for s in mentioned if s.brand_position]
    comp: Dict[str, int] = {}
    for s in scores:
        for c in s.competitors_mentioned:
            comp[c] = comp.get(c, 0) + 1

    return Aggregate(
        n=n,
        mean_composite=round(sum(s.composite(w) for s in scores) / n, 4),
        mention_rate=round(len(mentioned) / n, 4),
        avg_position=round(sum(positions) / len(positions), 2) if positions else None,
        cited_from_candidate_rate=round(
            sum(1 for s in scores if s.cited_from_candidate) / n, 4
        ),
        problem_frame_rate=round(
            sum(1 for s in scores if s.problem_frame_present) / n, 4
        ),
        mean_claims_ratio=round(
            sum((s.claims_hit / s.claims_total) if s.claims_total else 0.0 for s in scores)
            / n,
            4,
        ),
        competitor_counter=dict(sorted(comp.items(), key=lambda t: -t[1])),
    )
