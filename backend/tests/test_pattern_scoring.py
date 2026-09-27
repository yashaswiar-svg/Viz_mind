import pytest
from app.services.pattern_scoring import PatternScoringEngine


def test_scoring_engine_deduplication_and_ranking():
    engine = PatternScoringEngine()

    raw_items = [
        {
            "pattern_type": "CORRELATION",
            "columns": ["sales", "profit"],
            "statistics": {"absolute_correlation": 0.85, "correlation": 0.85},
            "adjusted_p_value": 0.0001,
            "sample_size": 500,
            "effect_size": 0.85,
            "strength": "STRONG",
            "significant": True,
            "method": "pearson",
        },
        # Duplicate pair (order reversed) with slightly lower effect size
        {
            "pattern_type": "CORRELATION",
            "columns": ["profit", "sales"],
            "statistics": {"absolute_correlation": 0.80, "correlation": 0.80},
            "adjusted_p_value": 0.001,
            "sample_size": 500,
            "effect_size": 0.80,
            "strength": "STRONG",
            "significant": True,
            "method": "pearson",
        },
        {
            "pattern_type": "GROUP_DIFFERENCE",
            "columns": ["region", "revenue"],
            "statistics": {"effect_size_type": "eta_squared", "effect_size": 0.20},
            "adjusted_p_value": 0.005,
            "sample_size": 300,
            "effect_size": 0.20,
            "strength": "STRONG",
            "significant": True,
            "method": "One-way ANOVA",
        },
    ]

    ranked = engine.score_and_rank_patterns(raw_items)

    # Verify deduplication reduced 2 correlation items to 1
    assert len(ranked) == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2

    # Scores must be bounded between 0 and 100
    for r in ranked:
        assert 0.0 <= r["score"] <= 100.0
        assert "title" in r
        assert "description" in r

    # Top ranked should be the higher scoring correlation item
    assert ranked[0]["pattern_type"] == "CORRELATION"
    assert set(ranked[0]["columns"]) == {"sales", "profit"}
