import pytest
import pandas as pd
import numpy as np
from app.services.prediction_models import LinearRegression, evaluate_regression
from app.services.prediction_planner import PredictionPlanner


def test_prediction_execution_determinism():
    """Verify that running prediction twice on unchanged data yields identical metrics and predictions."""
    np.random.seed(42)
    x_data = np.random.randn(100, 2)
    y_data = 2.5 * x_data[:, 0] - 1.2 * x_data[:, 1] + np.random.randn(100) * 0.1

    df = pd.DataFrame({"x1": x_data[:, 0], "x2": x_data[:, 1], "target": y_data})
    planner = PredictionPlanner()

    # Execution 1
    train1, val1, test1 = planner.split_data(df, target_column="target", problem_type="REGRESSION")
    model1 = LinearRegression().fit(train1[["x1", "x2"]], train1["target"])
    preds1 = model1.predict(test1[["x1", "x2"]])
    metrics1 = evaluate_regression(test1["target"].values, preds1)

    # Execution 2
    train2, val2, test2 = planner.split_data(df, target_column="target", problem_type="REGRESSION")
    model2 = LinearRegression().fit(train2[["x1", "x2"]], train2["target"])
    preds2 = model2.predict(test2[["x1", "x2"]])
    metrics2 = evaluate_regression(test2["target"].values, preds2)

    assert metrics1 == metrics2
    assert np.allclose(preds1, preds2)
