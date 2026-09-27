import pytest
from app.services.pattern_discovery_planner import (
    MAX_CORRELATION_PAIRS,
    MAX_GROUP_COMPARISONS,
    PatternDiscoveryPlanner,
)


def test_planner_generates_valid_candidates_and_enforces_caps():
    planner = PatternDiscoveryPlanner()

    # Build synthetic column profiles
    col_profiles = [
        {"column_name": "sales", "data_type": "float64", "distinct_count": 80, "null_count": 0},
        {"column_name": "profit", "data_type": "float64", "distinct_count": 80, "null_count": 0},
        {"column_name": "discount", "data_type": "float64", "distinct_count": 50, "null_count": 0},
        {"column_name": "region", "data_type": "object", "distinct_count": 4, "null_count": 0},
        {"column_name": "category", "data_type": "object", "distinct_count": 5, "null_count": 0},
        {"column_name": "order_date", "data_type": "datetime64[ns]", "distinct_count": 90, "null_count": 0},
        {"column_name": "customer_id", "data_type": "object", "distinct_count": 100, "null_count": 0},  # Identifier
        {"column_name": "constant_col", "data_type": "int64", "distinct_count": 1, "null_count": 0},  # Unsuitable
    ]


    tasks = planner.generate_candidate_tasks(col_profiles, total_rows=100)
    assert len(tasks) > 0

    # Ensure identifier and constant column are excluded
    for task in tasks:
        assert "customer_id" not in task.columns
        assert "constant_col" not in task.columns

    pattern_types = set(t.pattern_type for t in tasks)
    assert "CORRELATION" in pattern_types
    assert "GROUP_DIFFERENCE" in pattern_types
    assert "CATEGORICAL_ASSOCIATION" in pattern_types
    assert "TIME_TREND" in pattern_types
    assert "DISTRIBUTION" in pattern_types


def test_planner_deduplications_and_caps():
    planner = PatternDiscoveryPlanner()
    # Create 40 numeric columns
    col_profiles = [
        {"column_name": f"num_{i}", "data_type": "float64", "distinct_count": 100, "null_count": 0}
        for i in range(40)
    ]

    tasks = planner.generate_candidate_tasks(col_profiles, total_rows=100)
    corr_tasks = [t for t in tasks if t.pattern_type == "CORRELATION"]

    # Verify correlation candidates do not exceed MAX_CORRELATION_PAIRS (100)
    assert len(corr_tasks) <= MAX_CORRELATION_PAIRS

    # Verify no duplicate dedup_keys exist
    keys = set()
    for t in tasks:
        assert t.dedup_key not in keys
        keys.add(t.dedup_key)
