import pytest
import pandas as pd
import numpy as np
from app.services.chart_spec_builder import ChartSpecBuilder, SCATTER_MAX_POINTS


def test_build_chart_data_histogram():
    builder = ChartSpecBuilder()
    df = pd.DataFrame({"sales": np.random.normal(100, 15, 200)})

    spec = builder.build_chart_spec(chart_type="histogram", x_column="sales")
    res = builder.build_chart_data(df, spec)

    assert "data" in res
    assert len(res["data"]) == 20
    assert "bin_start" in res["data"][0]
    assert "bin_end" in res["data"][0]
    assert "count" in res["data"][0]


def test_build_chart_data_bar():
    builder = ChartSpecBuilder()
    df = pd.DataFrame({
        "region": ["North", "South", "East", "West", "North"],
        "sales": [100, 200, 150, 300, 250],
    })

    spec = builder.build_chart_spec(chart_type="bar", x_column="region", y_column="sales", aggregation="sum")
    res = builder.build_chart_data(df, spec)

    assert len(res["data"]) == 4
    categories = [d["category"] for d in res["data"]]
    assert "North" in categories
    north_val = next(d["value"] for d in res["data"] if d["category"] == "North")
    assert north_val == 350.0


def test_build_chart_data_scatter_sampling():
    builder = ChartSpecBuilder()
    # Generate 6000 points (exceeding SCATTER_MAX_POINTS)
    df = pd.DataFrame({
        "height": np.random.normal(170, 10, 6000),
        "weight": np.random.normal(70, 5, 6000),
    })

    spec = builder.build_chart_spec(chart_type="scatter", x_column="height", y_column="weight")
    res = builder.build_chart_data(df, spec)

    assert len(res["data"]) == SCATTER_MAX_POINTS
    assert res["metadata"]["sampled"] is True
    assert res["metadata"]["sample_size"] == SCATTER_MAX_POINTS


def test_build_chart_data_boxplot():
    builder = ChartSpecBuilder()
    df = pd.DataFrame({"age": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 500]})  # 500 is an outlier

    spec = builder.build_chart_spec(chart_type="boxplot", x_column="age")
    res = builder.build_chart_data(df, spec)

    assert len(res["data"]) == 1
    bp = res["data"][0]
    assert "min" in bp
    assert "q1" in bp
    assert "median" in bp
    assert "q3" in bp
    assert "max" in bp
    assert "outliers" in bp
    assert 500 in bp["outliers"]
