import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo_agent.config import load_config
from geo_agent.corpus import load_corpus
from geo_agent.loop import Optimizer

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _opt():
    cfg = load_config(os.path.join(HERE, "config.yaml"), profile="mock")
    corpus = load_corpus(HERE)
    return Optimizer(corpus, cfg), corpus


def test_corpus_loads():
    _, corpus = _opt()
    assert "havarie" in corpus.targets
    assert len(corpus.prompts_for("havarie", "train")) >= 3
    assert len(corpus.prompts_for("havarie", "val")) >= 1
    assert "DENIOS" in corpus.competitors


def test_loop_improves_mock():
    opt, _ = _opt()
    result = opt.optimize("havarie")
    first = result.iterations[0].train.mean_composite
    best = result.iterations[result.best_iteration].train.mean_composite
    # the mock must genuinely improve as the generator adds signals
    assert best > first
    # mention rate should climb from the weak seed
    assert result.iterations[result.best_iteration].train.mention_rate >= \
        result.iterations[0].train.mention_rate


def test_self_bias_guard_raises_without_optin():
    import pytest
    cfg = load_config(os.path.join(HERE, "config.yaml"), profile="live")
    cfg.models["generator"] = "openai:gpt-4.1"
    cfg.models["judge"] = "openai:gpt-4o"
    cfg.allow_same_family = False  # no opt-in -> must raise
    corpus = load_corpus(HERE)
    with pytest.raises(ValueError):
        Optimizer(corpus, cfg)


def test_self_bias_guard_allows_optin_with_warning():
    import warnings
    cfg = load_config(os.path.join(HERE, "config.yaml"), profile="live")
    cfg.models["generator"] = "anthropic:claude-opus-5"
    cfg.models["judge"] = "anthropic:claude-sonnet-5"
    cfg.allow_same_family = True  # deliberate single-family run -> warns, no raise
    corpus = load_corpus(HERE)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        Optimizer(corpus, cfg)
        assert any("single-family" in str(x.message).lower() for x in w)
