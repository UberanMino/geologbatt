"""Runtime configuration: which model plays which role, loop parameters, and
the self-bias guard.
"""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from typing import Dict, Optional

import yaml

from .llm import LLMClient, family_of

ROLES = ("generator", "judge", "scorer", "synthesizer")


@dataclass
class LoopParams:
    max_iterations: int = 5
    patience: int = 2          # stop after this many non-improving iterations
    target_score: float = 0.9  # stop early once train mean composite >= this
    min_delta: float = 0.01    # improvement smaller than this counts as a plateau
    top_k_competitors: int = 3


@dataclass
class Config:
    models: Dict[str, str]
    grounding: str
    temperature: Dict[str, float]
    loop: LoopParams
    profile: str
    allow_same_family: bool = False  # opt-in for single-provider setups

    # -- factories ---------------------------------------------------------- #
    def client(self, role: str) -> LLMClient:
        return LLMClient(self.models[role], temperature=self.temperature.get(role, 0.3))

    def assert_distinct_families(self):
        gen, judge = family_of(self.models["generator"]), family_of(self.models["judge"])
        if gen == "mock" or judge == "mock":
            return
        if gen == judge:
            if not self.allow_same_family:
                raise ValueError(
                    f"Generator and Judge share the model family '{gen}'. This "
                    "re-introduces self-bias (arXiv:2412.16829). Use different "
                    "families (generator=anthropic:…, judge=openai:…), or set "
                    "allow_same_family: true in config.yaml if you deliberately "
                    "want a single-provider run."
                )
            # single-family opt-in: still warn, and warn harder if identical model
            if self.models["generator"] == self.models["judge"]:
                warnings.warn(
                    f"Generator and Judge use the SAME model ({self.models['judge']}). "
                    "Self-bias is at its worst here — prefer different models per "
                    "role within the family (e.g. generator=opus, judge=sonnet)."
                )
            else:
                warnings.warn(
                    f"Single-family run ({gen}): Generator and Judge share a family. "
                    "Different models per role partly mitigates self-bias, but treat "
                    "results as a proxy until you can add a second provider."
                )


DEFAULTS = {
    "profile": "mock",
    "models": {
        "generator": "anthropic:claude-opus-5",
        "judge": "openai:gpt-4.1",
        "scorer": "openai:gpt-4o-mini",
        "synthesizer": "openai:gpt-4.1",
    },
    "grounding": "sources_only",
    "temperature": {"generator": 0.5, "judge": 0.2, "scorer": 0.0, "synthesizer": 0.3},
    "loop": {"max_iterations": 5, "patience": 2, "target_score": 0.9,
             "min_delta": 0.01, "top_k_competitors": 3},
}


def load_config(path: Optional[str] = None, profile: Optional[str] = None) -> Config:
    data = dict(DEFAULTS)
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
        _deep_update(data, user)

    prof = profile or os.getenv("GEO_PROFILE") or data.get("profile", "mock")

    models = dict(data["models"])
    # per-role env override, e.g. GEO_MODEL_JUDGE=google:gemini-2.5-pro
    for role in ROLES:
        env = os.getenv(f"GEO_MODEL_{role.upper()}")
        if env:
            models[role] = env

    if prof == "mock":
        models = {role: "mock:heuristic" for role in ROLES}

    loop = data["loop"]
    cfg = Config(
        models=models,
        grounding=data.get("grounding", "sources_only"),
        temperature=data.get("temperature", {}),
        loop=LoopParams(
            max_iterations=int(loop.get("max_iterations", 5)),
            patience=int(loop.get("patience", 2)),
            target_score=float(loop.get("target_score", 0.9)),
            min_delta=float(loop.get("min_delta", 0.01)),
            top_k_competitors=int(loop.get("top_k_competitors", 3)),
        ),
        profile=prof,
        allow_same_family=bool(data.get("allow_same_family", False)),
    )
    return cfg


def _deep_update(base: dict, extra: dict):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
