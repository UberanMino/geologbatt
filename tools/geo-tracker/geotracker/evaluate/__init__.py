"""Ebene 2 — Auswertungs-Layer (Claude Haiku 4.5).

Liest ausschließlich gespeicherte Ebene-1-Rohdaten und ist jederzeit auf
denselben Läufen wiederholbar. Ebene 1 importiert nichts hieraus.
"""

from .apply import BrandResolver, apply_evaluation, normalize_brand  # noqa: F401
from .client import EvaluationError, EvaluationResult, EvaluatorClient  # noqa: F401
from .prompt import EVALUATOR_VERSION, build_system_prompt, build_user_message  # noqa: F401
from .runner import (  # noqa: F401
    EvalTarget,
    collect_batch,
    evaluate_sync,
    select_runs,
    submit_batch,
    wait_for_batch,
)
