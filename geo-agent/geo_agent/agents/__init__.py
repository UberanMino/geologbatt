"""The three (+1) agents of the loop.

    Generator   -> writes / rewrites the candidate content
    Judge       -> answers the prompt like a grounded search engine
    Scorer      -> extracts the objective-function signals from the answer
    Synthesizer -> turns Generator draft + Judge answers into content directives

Generator and Judge are deliberately different model families (self-bias). The
Scorer and Synthesizer default to the Judge family so the Generator never grades
or coaches itself.
"""

from dataclasses import dataclass, field
from typing import List

from ..corpus import Prompt
from ..scoring import PromptScore


@dataclass
class JudgeAnswer:
    prompt_id: str
    text: str


@dataclass
class Evaluation:
    """One prompt run through Judge + Scorer against the current draft."""

    prompt: Prompt
    answer: JudgeAnswer
    score: PromptScore


@dataclass
class Feedback:
    """Structured coaching for the next Generator turn."""

    diagnosis: str
    directives: List[str] = field(default_factory=list)
    converged: bool = False

    def as_text(self) -> str:
        lines = [self.diagnosis.strip(), ""]
        for i, d in enumerate(self.directives, 1):
            lines.append(f"{i}. {d}")
        return "\n".join(lines).strip()
