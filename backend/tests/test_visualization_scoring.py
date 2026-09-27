import pytest
from app.services.visualization_planner import ChartCandidate, MAX_TOTAL_RECOMMENDATIONS
from app.services.visualization_scoring import VisualizationScoringEngine


def test_score_and_rank_candidates():
    scoring = VisualizationScoringEngine()
    total_rows = 100

    column_profiles = [
        {"column_name": "sales", "distinct_count": 80, "null_count": 0},
        {"column_name": "region", "distinct_count": 4, "null_count": 0},
        {"column_name": "order_date", "distinct_count": 90, "null_count": 0},
    ]

    candidates = [
        ChartCandidate(chart_type="line", x_column="order_date", y_column="sales", aggregation="sum", base_score=90.0),
        ChartCandidate(chart_type="bar", x_column="region", y_column="sales", aggregation="sum", base_score=85.0),
        ChartCandidate(chart_type="histogram", x_column="sales", base_score=75.0),
    ]

    ranked = scoring.score_and_rank_candidates(candidates, column_profiles, total_rows)

    assert len(ranked) == 3
    # Check score ordering (descending)
    assert ranked[0].base_score >= ranked[1].base_score >= ranked[2].base_score
    assert ranked[0].chart_type == "line"


def test_global_hard_cap_limit():
    scoring = VisualizationScoringEngine()
    total_rows = 100

    column_profiles = [{"column_name": f"col_{i}", "distinct_count": 50, "null_count": 0} for i in range(20)]

    # Generate 20 candidates
    candidates = [
        ChartCandidate(chart_type="histogram", x_column=f"col_{i}", base_score=70.0 + i)
        for i in range(20)
    ]

    ranked = scoring.score_and_rank_candidates(candidates, column_profiles, total_rows)
    assert len(ranked) == MAX_TOTAL_RECOMMENDATIONS
    assert len(ranked) == 12
