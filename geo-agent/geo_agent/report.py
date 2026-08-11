"""Rendering: console summary, machine-readable JSON, and a markdown report."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

from .loop import RunResult
from .scoring import Weights


def _fmt_pos(p: Optional[float]) -> str:
    return f"{p:.2f}" if p is not None else "—"


# --------------------------------------------------------------------------- #
# Console
# --------------------------------------------------------------------------- #
def print_console(result: RunResult) -> None:
    print()
    print(f"  Target:    {result.target_id}")
    print(f"  Profile:   {result.profile}   Grounding: {result.grounding}")
    print(f"  Models:    gen={result.models['generator']}  judge={result.models['judge']}")
    print(f"             scorer={result.models['scorer']}  synth={result.models['synthesizer']}")
    print()
    header = (f"  {'iter':>4}  {'train':>6}  {'val':>6}  {'mention':>8}  "
              f"{'avg_pos':>7}  {'cited':>6}  {'frame':>6}")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for rec in result.iterations:
        t, v = rec.train, rec.val
        star = "*" if rec.iteration == result.best_iteration else " "
        print(f" {star}{rec.iteration:>4}  {t.mean_composite:>6.3f}  "
              f"{v.mean_composite:>6.3f}  {t.mention_rate*100:>7.0f}%  "
              f"{_fmt_pos(t.avg_position):>7}  {t.cited_from_candidate_rate*100:>5.0f}%  "
              f"{t.problem_frame_rate*100:>5.0f}%")
    print()
    print(f"  Stop reason: {result.stop_reason}")
    print(f"  Best iteration: {result.best_iteration} "
          f"(train {result.iterations[result.best_iteration].train.mean_composite:.3f})")
    # overfitting hint
    best = result.iterations[result.best_iteration]
    gap = best.train.mean_composite - best.val.mean_composite
    if gap > 0.15:
        print(f"  ⚠ train/val gap {gap:.2f} — possible overfit to the Judge; "
              f"widen the Judge panel or check the synthetic↔real correlation.")
    print()


# --------------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------------- #
def to_dict(result: RunResult, weights: Weights) -> dict:
    return {
        "target": result.target_id,
        "profile": result.profile,
        "grounding": result.grounding,
        "models": result.models,
        "stop_reason": result.stop_reason,
        "best_iteration": result.best_iteration,
        "iterations": [
            {
                "iteration": r.iteration,
                "train": r.train.as_dict(),
                "val": r.val.as_dict(),
                "train_scores": [s.as_dict(weights) for s in r.train_scores],
                "val_scores": [s.as_dict(weights) for s in r.val_scores],
                "feedback": {
                    "diagnosis": r.feedback.diagnosis,
                    "directives": r.feedback.directives,
                    "converged": r.feedback.converged,
                },
                "draft_chars": len(r.draft),
            }
            for r in result.iterations
        ],
        "final_draft": result.final_draft,
    }


def save_run(result: RunResult, weights: Weights, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = os.path.join(out_dir, f"{result.target_id}-{stamp}")

    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(to_dict(result, weights), f, ensure_ascii=False, indent=2)

    with open(base + ".md", "w", encoding="utf-8") as f:
        f.write(_markdown(result, weights))

    with open(base + ".final.md", "w", encoding="utf-8") as f:
        f.write(result.final_draft)

    return base


def _markdown(result: RunResult, weights: Weights) -> str:
    lines = [
        f"# GEO-Optimierungslauf – {result.target_id}",
        "",
        f"- Profil: `{result.profile}` · Grounding: `{result.grounding}`",
        f"- Modelle: Generator `{result.models['generator']}`, "
        f"Judge `{result.models['judge']}`, Scorer `{result.models['scorer']}`, "
        f"Synthesizer `{result.models['synthesizer']}`",
        f"- Abbruchgrund: **{result.stop_reason}** · beste Iteration: "
        f"**{result.best_iteration}**",
        "",
        "## Verlauf",
        "",
        "| Iter | Train | Val | Mention | Ø Pos | aus Kandidat zitiert | Problem-Frame |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in result.iterations:
        t, v = r.train, r.val
        lines.append(
            f"| {r.iteration} | {t.mean_composite:.3f} | {v.mean_composite:.3f} | "
            f"{t.mention_rate*100:.0f}% | {_fmt_pos(t.avg_position)} | "
            f"{t.cited_from_candidate_rate*100:.0f}% | {t.problem_frame_rate*100:.0f}% |"
        )
    lines += ["", "## Feedback je Iteration", ""]
    for r in result.iterations:
        lines.append(f"### Iteration {r.iteration}")
        lines.append(f"*{r.feedback.diagnosis}*")
        lines.append("")
        for d in r.feedback.directives:
            lines.append(f"- {d}")
        lines.append("")
    lines += ["## Finaler Entwurf (beste Iteration)", "", "```markdown",
              result.final_draft, "```", ""]
    return "\n".join(lines)
