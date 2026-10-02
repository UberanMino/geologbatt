import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo_agent.scoring import PromptScore, Weights, aggregate, provider_order, count_hits


def test_composite_full_vs_empty():
    w = Weights()
    best = PromptScore("p", brand_mentioned=True, brand_position=1,
                       cited_from_candidate=True, problem_frame_present=True,
                       claims_hit=4, claims_total=4)
    worst = PromptScore("p", brand_mentioned=False)
    assert best.composite(w) > 0.99
    assert worst.composite(w) == 0.0


def test_position_decay():
    w = Weights()
    p1 = PromptScore("p", brand_mentioned=True, brand_position=1)
    p3 = PromptScore("p", brand_mentioned=True, brand_position=3)
    assert p1.composite(w) > p3.composite(w)


def test_provider_order_by_first_appearance():
    text = "Empfohlen: 1. LogBATT ... 2. DENIOS ... 3. Zarges"
    order = provider_order(text, ["LogBATT", "Zarges", "DENIOS"])
    assert order == ["LogBATT", "DENIOS", "Zarges"]


def test_count_hits_accent_insensitive():
    hits = count_hits("Quarantane und Havariefall", ["Quarantäne", "Recycling"])
    assert "Quarantäne" in hits and "Recycling" not in hits


def test_aggregate_mention_rate():
    scores = [
        PromptScore("a", brand_mentioned=True, brand_position=1),
        PromptScore("b", brand_mentioned=False),
    ]
    agg = aggregate(scores)
    assert agg.n == 2
    assert agg.mention_rate == 0.5
    assert agg.avg_position == 1.0
