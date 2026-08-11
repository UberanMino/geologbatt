"""Load the prompt set, the content targets and the source documents.

Everything the agents need at runtime lives on disk so it is auditable and
swappable:

  prompts/prompts.yaml        brand, weights, content targets, the prompt set
  corpus/competitors/*.md     one card per competitor (frontmatter + body)
  corpus/logbatt/*.md         seed content for each target (frontmatter + body)

The source documents handed to the Judge are: all competitor cards (byte
identical across iterations) + the current candidate (the only thing that
changes). That is what makes each iteration a clean A/B — see README, "Kontext-
Swap, kein Eingriff ins Wissensnetz".
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml


# --------------------------------------------------------------------------- #
# Data models
# --------------------------------------------------------------------------- #
@dataclass
class SourceDoc:
    id: str                       # S1, S2 ... (S1 is always the candidate)
    title: str
    domain: str
    kind: str                     # candidate | competitor | reference
    content: str
    signals: List[str] = field(default_factory=list)  # keywords this doc "owns"
    base_strength: float = 0.0    # mock-only: tracked share for competitors


@dataclass
class Prompt:
    id: str
    target: str                   # which content target this optimises
    cluster: str
    text: str
    intent: str = "commercial"
    split: str = "train"          # train | val  (val = held-out, never fed back)
    mode: str = "swap"            # swap (brand already retrieved) | inject
    baseline_mention_pct: Optional[float] = None
    facts: List[str] = field(default_factory=list)
    problem_frame_anchors: List[str] = field(default_factory=list)
    competitors: Dict[str, float] = field(default_factory=dict)  # name -> tracked %


@dataclass
class Target:
    id: str
    title: str
    cluster: str
    seed_path: str
    brand_voice: str = ""
    facts: List[str] = field(default_factory=list)
    problem_frame_anchors: List[str] = field(default_factory=list)


@dataclass
class Corpus:
    brand_name: str
    brand_aliases: List[str]
    brand_domain: str
    partners: List[str]           # never counted as competitors
    weights: dict
    targets: Dict[str, Target]
    prompts: List[Prompt]
    competitors: Dict[str, SourceDoc]  # name -> card
    root: str

    # -- convenience -------------------------------------------------------- #
    def prompts_for(self, target: str, split: Optional[str] = None) -> List[Prompt]:
        out = [p for p in self.prompts if p.target == target]
        if split:
            out = [p for p in out if p.split == split]
        return out

    def target_ids(self) -> List[str]:
        return list(self.targets.keys())

    def seed_content(self, target_id: str) -> str:
        t = self.targets[target_id]
        path = os.path.join(self.root, t.seed_path)
        _, body = _read_frontmatter(path)
        return body.strip()

    def competitor_cards(self, names: List[str]) -> List[SourceDoc]:
        cards = []
        for n in names:
            card = self.competitors.get(n)
            if card:
                cards.append(card)
        return cards


# --------------------------------------------------------------------------- #
# Frontmatter parsing (``---`` YAML block + markdown body)
# --------------------------------------------------------------------------- #
def _read_frontmatter(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2]
    return {}, raw


# --------------------------------------------------------------------------- #
# Loader
# --------------------------------------------------------------------------- #
def load_corpus(root: str, prompts_file: str = "prompts/prompts.yaml") -> Corpus:
    root = os.path.abspath(root)
    with open(os.path.join(root, prompts_file), "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    brand = spec.get("brand", {})
    targets = {
        tid: Target(
            id=tid,
            title=t.get("title", tid),
            cluster=t.get("cluster", ""),
            seed_path=t["seed"],
            brand_voice=t.get("brand_voice", ""),
            facts=list(t.get("facts", [])),
            problem_frame_anchors=list(t.get("problem_frame_anchors", [])),
        )
        for tid, t in spec.get("targets", {}).items()
    }

    prompts = []
    for p in spec.get("prompts", []):
        tgt = targets.get(p["target"])
        prompts.append(
            Prompt(
                id=p["id"],
                target=p["target"],
                cluster=p.get("cluster", tgt.cluster if tgt else ""),
                text=p["text"],
                intent=p.get("intent", "commercial"),
                split=p.get("split", "train"),
                mode=p.get("mode", "swap"),
                baseline_mention_pct=p.get("baseline_mention_pct"),
                # a prompt inherits its target's facts/anchors unless overridden
                facts=list(p.get("facts", tgt.facts if tgt else [])),
                problem_frame_anchors=list(
                    p.get("problem_frame_anchors", tgt.problem_frame_anchors if tgt else [])
                ),
                competitors=_parse_competitors(p.get("competitors", {})),
            )
        )

    competitors = _load_competitor_cards(os.path.join(root, "corpus", "competitors"))

    return Corpus(
        brand_name=brand.get("name", "LogBATT"),
        brand_aliases=list(brand.get("aliases", [])),
        brand_domain=brand.get("domain", ""),
        partners=list(spec.get("partners", [])),
        weights=spec.get("weights", {}),
        targets=targets,
        prompts=prompts,
        competitors=competitors,
        root=root,
    )


def _parse_competitors(raw) -> Dict[str, float]:
    """Accept either a list of names or a dict name->percent."""
    if isinstance(raw, dict):
        return {str(k): float(v) for k, v in raw.items()}
    if isinstance(raw, list):
        return {str(x): 0.0 for x in raw}
    return {}


def _load_competitor_cards(folder: str) -> Dict[str, SourceDoc]:
    cards: Dict[str, SourceDoc] = {}
    if not os.path.isdir(folder):
        return cards
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".md") or fname.lower() in ("readme.md", "_index.md"):
            continue
        meta, body = _read_frontmatter(os.path.join(folder, fname))
        name = meta.get("name") or os.path.splitext(fname)[0]
        cards[name] = SourceDoc(
            id="",  # assigned per prompt when the doc set is built
            title=name,
            domain=meta.get("domain", ""),
            kind="competitor",
            content=body.strip(),
            signals=list(meta.get("signals", [])),
            base_strength=float(meta.get("base_strength", 0.0)),
        )
    return cards
