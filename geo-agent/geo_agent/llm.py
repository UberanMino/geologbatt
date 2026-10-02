"""Provider-abstracted LLM client.

A model is addressed by a string ``"<provider>:<model>"``:

    anthropic:claude-opus-5
    openai:gpt-4.1
    google:gemini-2.5-pro
    mock:heuristic          # deterministic, offline, no key required

The whole system runs end-to-end on ``mock:`` so you can see the loop turn
without any API key. Swap in real providers via config.yaml / .env once you
have keys.

Design note (self-bias): the Generator and the Judge MUST come from different
model families, otherwise the loop optimises into a shared blind spot
(LLMRefine / self-bias, arXiv:2412.16829). ``assert_distinct_families`` in
config.py enforces this.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResponse:
    text: str
    model: str
    raw: Optional[object] = None


def family_of(model_spec: str) -> str:
    """Return the provider family, e.g. 'anthropic' from 'anthropic:claude-...'."""
    return model_spec.split(":", 1)[0].strip().lower()


def _split(model_spec: str):
    if ":" not in model_spec:
        raise LLMError(
            f"model spec '{model_spec}' must be '<provider>:<model>' "
            "(e.g. anthropic:claude-opus-5, mock:heuristic)"
        )
    provider, model = model_spec.split(":", 1)
    return provider.strip().lower(), model.strip()


class LLMClient:
    """Thin wrapper. One instance per role (generator/judge/scorer/synthesizer)."""

    def __init__(self, model_spec: str, temperature: float = 0.4, max_tokens: int = 4000):
        self.model_spec = model_spec
        self.provider, self.model = _split(model_spec)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._impl = None  # lazy

    # -- public ------------------------------------------------------------- #
    def complete(self, system: str, user: str, *, temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> LLMResponse:
        temp = self.temperature if temperature is None else temperature
        mt = self.max_tokens if max_tokens is None else max_tokens
        if self.provider == "mock":
            return LLMResponse(text=_mock_complete(self.model, system, user),
                               model=self.model_spec)
        if self.provider == "anthropic":
            return self._anthropic(system, user, temp, mt)
        if self.provider == "openai":
            return self._openai(system, user, temp, mt)
        if self.provider == "google":
            return self._google(system, user, temp, mt)
        raise LLMError(f"unknown provider '{self.provider}' in '{self.model_spec}'")

    def complete_json(self, system: str, user: str, **kw) -> dict:
        """Complete and parse the first JSON object out of the reply."""
        resp = self.complete(system, user, **kw)
        return _extract_json(resp.text)

    # -- providers (lazy imports so SDKs are optional) ---------------------- #
    def _anthropic(self, system, user, temp, mt) -> LLMResponse:
        try:
            import anthropic  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install anthropic (or use mock:)") from e
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise LLMError("ANTHROPIC_API_KEY not set (or use mock:)")
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=self.model, system=system, max_tokens=mt, temperature=temp,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return LLMResponse(text=text, model=self.model_spec, raw=msg)

    def _openai(self, system, user, temp, mt) -> LLMResponse:
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install openai (or use mock:)") from e
        if not os.getenv("OPENAI_API_KEY"):
            raise LLMError("OPENAI_API_KEY not set (or use mock:)")
        client = OpenAI()
        resp = client.chat.completions.create(
            model=self.model, temperature=temp, max_tokens=mt,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
        )
        return LLMResponse(text=resp.choices[0].message.content or "",
                           model=self.model_spec, raw=resp)

    def _google(self, system, user, temp, mt) -> LLMResponse:
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise LLMError("pip install google-genai (or use mock:)") from e
        if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            raise LLMError("GEMINI_API_KEY / GOOGLE_API_KEY not set (or use mock:)")
        client = genai.Client()
        resp = client.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system, temperature=temp,
                max_output_tokens=mt,
            ),
        )
        return LLMResponse(text=resp.text or "", model=self.model_spec, raw=resp)


# --------------------------------------------------------------------------- #
# JSON extraction
# --------------------------------------------------------------------------- #
def _extract_json(text: str) -> dict:
    text = text.strip()
    # fenced ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        # first {...} span
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"could not parse JSON from model reply: {e}\n---\n{text[:500]}")


# --------------------------------------------------------------------------- #
# Mock provider
# --------------------------------------------------------------------------- #
# The mock does NOT call any network. It returns a sentinel that the agents
# recognise and replace with their own deterministic heuristic (see each
# agent's ``_mock_*`` method). Keeping the heuristics inside the agents means
# the mock understands the actual content, so the loop genuinely converges as
# the Generator adds the signals the Synthesizer asked for — it is a real
# demonstration of the mechanism, not a canned animation.
MOCK_SENTINEL = "__GEO_MOCK__"


def _mock_complete(model: str, system: str, user: str) -> str:
    return MOCK_SENTINEL


def is_mock(client: LLMClient) -> bool:
    return client.provider == "mock"
