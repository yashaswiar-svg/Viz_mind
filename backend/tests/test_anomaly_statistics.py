import pytest
import pandas as pd
import numpy as np
from app.services.anomaly_statistics import (
    detect_iqr_anomalies,
    detect_robust_zscore_anomalies,
    detect_time_series_rolling_anomalies,
)


def test_detect_iqr_anomalies_obvious_outlier():
    # Normal data around 10, outlier at 500
    data = [10.0] * 20 + [500.0]
    series = pd.Series(data)
    res = detect_iqr_anomalies(series)

    assert len(res) >= 1
    outlier = res[0]
    assert outlier["value"] == 500.0
    assert outlier["method"] == "IQR"
    assert "lower_bound" in outlier["expected_range"]


def test_detect_iqr_anomalies_constant_series():
    series = pd.Series([5.0] * 30)
    res = detect_iqr_anomalies(series)
    assert len(res) == 0


def test_detect_robust_zscore_anomalies_obvious_outlier():
    # Median ~ 10, MAD ~ 0, outlier at 100
    data = [10.0, 10.1, 9.9, 10.2, 9.8, 10.0, 10.1, 9.9, 10.0, 10.2, 10.1, 9.9, 100.0]
    series = pd.Series(data)
    res = detect_robust_zscore_anomalies(series, threshold=3.5)

    assert len(res) >= 1
    assert any(item["value"] == 100.0 for item in res)


def test_detect_robust_zscore_zero_mad():
    series = pd.Series([10.0] * 20)
    res = detect_robust_zscore_anomalies(series)
    assert len(res) == 0


def test_detect_time_series_rolling_anomalies():
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    vals = [10.0] * 19 + [100.0]
    df = pd.DataFrame({"date": dates, "val": vals})

    res = detect_time_series_rolling_anomalies(df, date_col="date", num_col="val", threshold=3.0)
    assert len(res) >= 1
    assert res[0]["value"] == 100.0

