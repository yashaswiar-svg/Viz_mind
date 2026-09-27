import pytest
from app.services.visualization_planner import (
    VisualizationPlanner,
    ROLE_NUMERIC_MEASURE,
    ROLE_CATEGORICAL_DIMENSION,
    ROLE_DATETIME_DIMENSION,
    ROLE_IDENTIFIER,
    ROLE_UNSUITABLE,
    MAX_HISTOGRAMS,
    MAX_BAR_CHARTS,
    MAX_LINE_CHARTS,
    MAX_SCATTER_PLOTS,
    MAX_BOXPLOTS,
)


def test_classify_column_roles():
    planner = VisualizationPlanner()
    total_rows = 100

    # Numeric measure
    num_role = planner.classify_column_role(
        {"column_name": "sales", "data_type": "float64", "distinct_count": 85, "null_count": 0},
        total_rows,
    )
    assert num_role.role == ROLE_NUMERIC_MEASURE

    # Categorical dimension
    cat_role = planner.classify_column_role(
        {"column_name": "category", "data_type": "object", "distinct_count": 5, "null_count": 0},
        total_rows,
    )
    assert cat_role.role == ROLE_CATEGORICAL_DIMENSION

    # Datetime dimension
    dt_role = planner.classify_column_role(
        {"column_name": "order_date", "data_type": "datetime64[ns]", "distinct_count": 90, "null_count": 0},
        total_rows,
    )
    assert dt_role.role == ROLE_DATETIME_DIMENSION

    # Identifier
    id_role = planner.classify_column_role(
        {"column_name": "user_id", "data_type": "int64", "distinct_count": 100, "null_count": 0},
        total_rows,
    )
    assert id_role.role == ROLE_IDENTIFIER

    # Unsuitable (100% null)
    unsuitable_role = planner.classify_column_role(
        {"column_name": "empty_col", "data_type": "float64", "distinct_count": 0, "null_count": 100},
        total_rows,
    )
    assert unsuitable_role.role == ROLE_UNSUITABLE


def test_plan_candidates_limits_and_deduplication():
    planner = VisualizationPlanner()
    total_rows = 100

    column_profiles = [
        {"column_name": "sales", "data_type": "float64", "distinct_count": 80, "null_count": 0},
        {"column_name": "profit", "data_type": "float64", "distinct_count": 75, "null_count": 0},
        {"column_name": "quantity", "data_type": "int64", "distinct_count": 30, "null_count": 0},
        {"column_name": "discount", "data_type": "float64", "distinct_count": 25, "null_count": 0},
        {"column_name": "region", "data_type": "object", "distinct_count": 4, "null_count": 0},
        {"column_name": "category", "data_type": "object", "distinct_count": 3, "null_count": 0},
        {"column_name": "order_date", "data_type": "datetime64[ns]", "distinct_count": 90, "null_count": 0},
    ]

    candidates = planner.plan_candidates(column_profiles, total_rows)
    assert len(candidates) > 0

    # Count by chart type
    counts = {}
    for c in candidates:
        counts[c.chart_type] = counts.get(c.chart_type, 0) + 1

    assert counts.get("histogram", 0) <= MAX_HISTOGRAMS
    assert counts.get("bar", 0) <= MAX_BAR_CHARTS
    assert counts.get("line", 0) <= MAX_LINE_CHARTS
    assert counts.get("scatter", 0) <= MAX_SCATTER_PLOTS
    assert counts.get("boxplot", 0) <= MAX_BOXPLOTS
