import math
import numpy as np
import pandas as pd
import pytest

from app.services.pattern_statistics import (
    apply_fdr_correction,
    compute_categorical_association,
    compute_correlation,
    compute_distribution_statistics,
    compute_group_difference,
    compute_time_trend,
)


def test_compute_correlation_strong_positive():
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    y = pd.Series([2.1, 4.0, 6.2, 7.9, 10.1, 12.0, 14.1, 16.0, 18.2, 20.0])

    res = compute_correlation(x, y, method="pearson", min_n=10)
    assert res is not None
    assert res["correlation"] > 0.95
    assert res["strength"] == "STRONG"
    assert res["direction"] == "POSITIVE"
    assert res["sample_size"] == 10
    assert res["raw_p_value"] < 0.001


def test_compute_correlation_strong_negative():
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    y = pd.Series([100.0, 90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0, 10.0])

    res = compute_correlation(x, y, method="pearson", min_n=10)
    assert res is not None
    assert res["correlation"] < -0.95
    assert res["strength"] == "STRONG"
    assert res["direction"] == "NEGATIVE"


def test_compute_correlation_zero_variance_or_insufficient():
    x = pd.Series([5.0] * 10)
    y = pd.Series(range(10))
    assert compute_correlation(x, y) is None

    # Insufficient sample size
    x_small = pd.Series([1.0, 2.0, 3.0])
    y_small = pd.Series([2.0, 4.0, 6.0])
    assert compute_correlation(x_small, y_small, min_n=10) is None


def test_compute_group_difference_two_groups():
    groups = pd.Series(["A"] * 15 + ["B"] * 15)
    measures = pd.Series([10.0 + np.random.normal(0, 1) for _ in range(15)] + [25.0 + np.random.normal(0, 1) for _ in range(15)])

    res = compute_group_difference(groups, measures, min_group_size=10)
    assert res is not None
    assert res["method"] == "Welch's t-test"
    assert res["groups"] == 2
    assert res["effect_size_type"] == "cohens_d"
    assert res["effect_size"] > 0.8
    assert res["strength"] == "STRONG"
    assert res["raw_p_value"] < 0.01


def test_compute_group_difference_anova():
    groups = pd.Series(["North"] * 12 + ["South"] * 12 + ["East"] * 12)
    measures = pd.Series(
        [10.0 + np.random.normal(0, 1) for _ in range(12)]
        + [20.0 + np.random.normal(0, 1) for _ in range(12)]
        + [30.0 + np.random.normal(0, 1) for _ in range(12)]
    )

    res = compute_group_difference(groups, measures, min_group_size=10)
    assert res is not None
    assert res["method"] == "One-way ANOVA"
    assert res["groups"] == 3
    assert res["effect_size_type"] == "eta_squared"
    assert res["effect_size"] > 0.14
    assert res["strength"] == "STRONG"


def test_compute_categorical_association():
    c1 = pd.Series(["Male"] * 30 + ["Female"] * 30)
    c2 = pd.Series(["Tech"] * 25 + ["Other"] * 5 + ["Tech"] * 5 + ["Other"] * 25)

    res = compute_categorical_association(c1, c2, min_n=20)
    assert res is not None
    assert res["method"] == "chi_square"
    assert res["cramers_v"] > 0.30
    assert res["strength"] == "STRONG"
    assert res["raw_p_value"] < 0.05


def test_compute_time_trend():
    dates = pd.date_range(start="2026-01-01", periods=12, freq="D")
    dt_series = pd.Series(dates)
    measures = pd.Series([100.0, 110.0, 125.0, 140.0, 155.0, 170.0, 180.0, 195.0, 210.0, 225.0, 240.0, 255.0])

    res = compute_time_trend(dt_series, measures, min_time_points=8)
    assert res is not None
    assert res["direction"] == "INCREASING"
    assert res["r_squared"] > 0.90
    assert res["strength"] == "STRONG"
    assert res["slope"] > 0


def test_compute_distribution_statistics():
    data = pd.Series([10, 12, 14, 15, 16, 18, 20, 22, 24, 100])
    res = compute_distribution_statistics(data)

    assert res is not None
    assert res["sample_size"] == 10
    assert res["median"] == 17.0
    assert res["shape"] == "RIGHT_SKEWED"
    assert res["iqr"] > 0


def test_apply_fdr_correction():
    raw_pvals = [0.001, 0.01, 0.03, 0.04, 0.20, 0.50]
    adj_pvals = apply_fdr_correction(raw_pvals)

    assert len(adj_pvals) == len(raw_pvals)
    # FDR adjusted p-values must be >= raw p-values and <= 1.0
    for r, a in zip(raw_pvals, adj_pvals):
        assert a >= r
        assert a <= 1.0

    # Test monotonicity
    for i in range(len(adj_pvals) - 1):
        assert adj_pvals[i] <= adj_pvals[i + 1]
