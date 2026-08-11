"""The recursive optimization loop.

One content target (a page for a cluster) is optimised against the cluster's
TRAIN prompts and validated on its held-out VAL prompts every iteration. The
val split is scored but never fed to the Synthesizer, so a growing train/val gap
tells you the loop is overfitting the Judge instead of genuinely improving —
exactly the Goodhart guardrail from the conversation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .agents import Evaluation, Feedback
from .agents.generator import Generator
from .agents.judge import Judge, build_doc_set
from .agents.scorer import Scorer
from .agents.synthesizer import Synthesizer
from .config import Config
from .corpus import Corpus, Prompt
from .scoring import Aggregate, PromptScore, Weights, aggregate


@dataclass
class IterationRecord:
    iteration: int
    draft: str
    train: Aggregate
    val: Aggregate
    train_scores: List[PromptScore]
    val_scores: List[PromptScore]
    evals_train: List[Evaluation]
    feedback: Feedback


@dataclass
class RunResult:
    target_id: str
    profile: str
    grounding: str
    models: dict
    iterations: List[IterationRecord] = field(default_factory=list)
    best_iteration: int = 0
    stop_reason: str = ""

    @property
    def final_draft(self) -> str:
        return self.iterations[self.best_iteration].draft if self.iterations else ""


class Optimizer:
    def __init__(self, corpus: Corpus, config: Config):
        config.assert_distinct_families()
        self.corpus = corpus
        self.config = config
        self.weights = Weights.from_dict(corpus.weights)
        self.generator = Generator(config.client("generator"))
        self.judge = Judge(config.client("judge"), grounding=config.grounding)
        self.scorer = Scorer(config.client("scorer"))
        self.synthesizer = Synthesizer(config.client("synthesizer"))

    # -- one prompt through Judge + Scorer ---------------------------------- #
    def evaluate(self, prompt: Prompt, draft: str) -> Evaluation:
        docs = build_doc_set(prompt, draft, self.corpus)
        answer = self.judge.answer(prompt, docs, self.corpus)
        score = self.scorer.score(prompt, answer, self.corpus)
        return Evaluation(prompt=prompt, answer=answer, score=score)

    # -- the loop ----------------------------------------------------------- #
    def optimize(self, target_id: str, on_iteration=None) -> RunResult:
        target = self.corpus.targets[target_id]
        train = self.corpus.prompts_for(target_id, "train")
        val = self.corpus.prompts_for(target_id, "val")
        if not train:
            raise ValueError(f"target '{target_id}' has no train prompts")

        result = RunResult(
            target_id=target_id, profile=self.config.profile,
            grounding=self.config.grounding, models=dict(self.config.models),
        )

        draft = self.corpus.seed_content(target_id)
        feedback: Optional[Feedback] = None
        best_score = -1.0
        no_improve = 0

        for it in range(self.config.loop.max_iterations):
            if it > 0:
                draft = self.generator.generate(target, draft, feedback, self.corpus)

            evals_train = [self.evaluate(p, draft) for p in train]
            val_scores = [self.evaluate(p, draft).score for p in val]
            train_scores = [e.score for e in evals_train]

            train_agg = aggregate(train_scores, self.weights)
            val_agg = aggregate(val_scores, self.weights)

            feedback = self.synthesizer.synthesize(target, draft, evals_train, self.corpus)

            rec = IterationRecord(
                iteration=it, draft=draft, train=train_agg, val=val_agg,
                train_scores=train_scores, val_scores=val_scores,
                evals_train=evals_train, feedback=feedback,
            )
            result.iterations.append(rec)
            if on_iteration:
                on_iteration(rec)

            # track best + plateau
            score = train_agg.mean_composite
            if score > best_score + self.config.loop.min_delta:
                best_score = score
                result.best_iteration = it
                no_improve = 0
            else:
                no_improve += 1

            # stopping criteria
            if feedback.converged:
                result.stop_reason = "synthesizer_converged"
                break
            if score >= self.config.loop.target_score:
                result.stop_reason = "target_reached"
                result.best_iteration = it
                break
            if no_improve >= self.config.loop.patience:
                result.stop_reason = "plateau"
                break
        else:
            result.stop_reason = "max_iterations"

        # best iteration = highest train mean composite
        result.best_iteration = max(
            range(len(result.iterations)),
            key=lambda i: result.iterations[i].train.mean_composite,
        )
        return result
