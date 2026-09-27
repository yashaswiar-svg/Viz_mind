import uuid
import pandas as pd
import pytest
from app.services.profiling_service import ProfilingService


def test_infer_column_types():
    df = pd.DataFrame({
        "num": [1, 2, 3, 4, 5],
        "cat": ["A", "B", "A", "B", "A"],
        "bool_val": [True, False, True, False, True],
        "str_bool": ["yes", "no", "yes", "no", "yes"],
        "text_val": [f"long text string {i}" for i in range(5)],
    })

    assert ProfilingService.infer_column_type(df["num"]) == "numeric"
    assert ProfilingService.infer_column_type(df["cat"]) == "categorical"
    assert ProfilingService.infer_column_type(df["bool_val"]) == "boolean"
    assert ProfilingService.infer_column_type(df["str_bool"]) == "boolean"


def test_profile_numeric_column_with_nan_and_inf():
    service = ProfilingService(None)
    series = pd.Series([10.0, 20.0, float("nan"), float("inf"), 30.0])

    profile = service.profile_column(series, "val", 0)

    assert profile["inferred_type"] == "numeric"
    assert profile["null_count"] == 1
    assert profile["min_value"] == 10.0
    assert profile["max_value"] == 30.0
    assert profile["mean_value"] == 20.0
