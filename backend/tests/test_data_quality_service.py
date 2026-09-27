import pytest
from app.services.data_quality_service import DataQualityService


def test_quality_score_perfect_dataset():
    cols = [
        {"column_name": "id", "null_percentage": 0.0, "unique_percentage": 100.0, "is_constant": False, "non_null_count": 100},
        {"column_name": "category", "null_percentage": 0.0, "unique_percentage": 10.0, "is_constant": False, "non_null_count": 100},
    ]

    score, level, issues = DataQualityService.evaluate_quality(
        row_count=100,
        column_count=2,
        duplicate_rows=0,
        missing_cells=0,
        column_profiles=cols,
    )

    assert score >= 95.0
    assert level == "Excellent"
    assert len([i for i in issues if i.severity == "critical"]) == 0


def test_quality_score_poor_dataset():
    cols = [
        {"column_name": "empty_col", "null_percentage": 100.0, "unique_percentage": 0.0, "is_constant": False, "non_null_count": 0},
        {"column_name": "const_col", "null_percentage": 0.0, "unique_percentage": 1.0, "is_constant": True, "non_null_count": 100},
    ]

    score, level, issues = DataQualityService.evaluate_quality(
        row_count=100,
        column_count=2,
        duplicate_rows=50,  # 50% duplicates
        missing_cells=100,  # 50% missing cells
        column_profiles=cols,
    )

    assert score < 75.0
    assert level in ["Fair", "Poor"]
    assert any(i.code == "EMPTY_COLUMN" for i in issues)
    assert any(i.code == "CONSTANT_COLUMN" for i in issues)
    assert any(i.code == "DUPLICATE_ROWS" for i in issues)
