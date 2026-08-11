"""Command-line entry point.

    python run.py run --target havarie --iterations 4
    python run.py list
    python run.py show-prompt hav-01
"""

from __future__ import annotations

import argparse
import os
import sys

from .config import load_config
from .corpus import load_corpus
from .loop import Optimizer
from .report import print_console, save_run
from .scoring import Weights

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # geo-agent/


def _load(args):
    # optional .env (no hard dependency)
    env = os.path.join(HERE, ".env")
    if os.path.exists(env):
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv(env)
        except ImportError:
            _manual_dotenv(env)
    cfg = load_config(os.path.join(HERE, "config.yaml"), profile=args.profile)
    corpus = load_corpus(HERE)
    return cfg, corpus


def _manual_dotenv(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def cmd_run(args):
    cfg, corpus = _load(args)
    if args.iterations:
        cfg.loop.max_iterations = args.iterations
    if args.target not in corpus.targets:
        print(f"unknown target '{args.target}'. Available: {', '.join(corpus.target_ids())}")
        return 2

    opt = Optimizer(corpus, cfg)
    print(f"\nOptimising target '{args.target}' "
          f"({len(corpus.prompts_for(args.target,'train'))} train / "
          f"{len(corpus.prompts_for(args.target,'val'))} val prompts) "
          f"— profile={cfg.profile}, up to {cfg.loop.max_iterations} iterations…")

    def tick(rec):
        print(f"  · iter {rec.iteration}: train={rec.train.mean_composite:.3f} "
              f"val={rec.val.mean_composite:.3f} mention={rec.train.mention_rate*100:.0f}%")

    result = opt.optimize(args.target, on_iteration=tick)
    print_console(result)

    if not args.no_save:
        base = save_run(result, Weights.from_dict(corpus.weights),
                        os.path.join(HERE, "runs"))
        print(f"  Saved: {os.path.relpath(base, HERE)}.(json|md|final.md)\n")
    return 0


def cmd_list(args):
    _, corpus = _load(args)
    print("\nContent targets:")
    for tid, t in corpus.targets.items():
        n_tr = len(corpus.prompts_for(tid, "train"))
        n_va = len(corpus.prompts_for(tid, "val"))
        print(f"  {tid:14} {t.title}  [{n_tr} train / {n_va} val]  cluster='{t.cluster}'")
    print(f"\nCompetitor cards: {', '.join(corpus.competitors.keys())}\n")
    return 0


def cmd_show_prompt(args):
    _, corpus = _load(args)
    p = next((x for x in corpus.prompts if x.id == args.prompt_id), None)
    if not p:
        print(f"no prompt '{args.prompt_id}'")
        return 2
    print(f"\n[{p.id}] target={p.target} split={p.split} mode={p.mode} intent={p.intent}")
    print(f"  text: {p.text}")
    print(f"  baseline mention: {p.baseline_mention_pct}%")
    print(f"  facts: {p.facts}")
    print(f"  anchors: {p.problem_frame_anchors}")
    print(f"  competitors: {p.competitors}\n")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="geo-agent",
                                description="Recursive GEO content-optimization loop")
    p.add_argument("--profile", default=None,
                   help="mock (offline, default) | live (real providers via config/.env)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the optimization loop on a target")
    r.add_argument("--target", required=True)
    r.add_argument("--iterations", type=int, default=None)
    r.add_argument("--no-save", action="store_true")
    r.set_defaults(func=cmd_run)

    l = sub.add_parser("list", help="list targets and competitor cards")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("show-prompt", help="inspect one prompt")
    s.add_argument("prompt_id")
    s.set_defaults(func=cmd_show_prompt)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
