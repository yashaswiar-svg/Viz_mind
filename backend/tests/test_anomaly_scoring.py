import pytest
from app.services.anomaly_scoring import calculate_anomaly_score_and_severity


def test_calculate_anomaly_score_and_severity_single_method():
    raw = [
        {
            "observation_reference": "row_5",
            "row_index": 5,
            "column_name": "price",
            "value": 1000.0,
            "method": "ROBUST_ZSCORE",
            "statistics": {"abs_robust_zscore": 8.5},
            "expected_range": {"lower_bound": 0.0, "upper_bound": 100.0},
        }
    ]

    res = calculate_anomaly_score_and_severity(raw)
    assert len(res) == 1
    item = res[0]
    assert item["severity"] == "HIGH"
    assert item["anomaly_score"] >= 70.0
    assert item["methods_detected"] == ["ROBUST_ZSCORE"]


def test_calculate_anomaly_score_and_severity_deduplication():
    raw = [
        {
            "observation_reference": "row_5",
            "row_index": 5,
            "column_name": "price",
            "value": 1000.0,
            "method": "ROBUST_ZSCORE",
            "statistics": {"abs_robust_zscore": 4.5},
            "expected_range": {"lower_bound": 0.0, "upper_bound": 100.0},
        },
        {
            "observation_reference": "row_5",
            "row_index": 5,
            "column_name": "price",
            "value": 1000.0,
            "method": "IQR",
            "statistics": {"normalized_distance": 2.0},
            "expected_range": {"lower_bound": 0.0, "upper_bound": 100.0},
        },
    ]

    res = calculate_anomaly_score_and_severity(raw)
    assert len(res) == 1
    item = res[0]
    assert "ROBUST_ZSCORE" in item["methods_detected"]
    assert "IQR" in item["methods_detected"]
