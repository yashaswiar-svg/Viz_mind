import pytest
import numpy as np
import pandas as pd
from app.services.prediction_models import (
    LinearRegression,
    LogisticRegression,
    MajorityClassClassifier,
    MeanRegressor,
    NaiveForecast,
    evaluate_classification,
    evaluate_regression,
)


def test_mean_regressor():
    X = pd.DataFrame({"feat": [1, 2, 3, 4, 5]})
    y = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])

    model = MeanRegressor().fit(X, y)
    preds = model.predict(X)
    assert np.allclose(preds, 30.0)


def test_majority_class_classifier():
    X = pd.DataFrame({"feat": [1, 2, 3, 4, 5]})
    y = pd.Series(["A", "A", "A", "B", "C"])

    model = MajorityClassClassifier().fit(X, y)
    preds = model.predict(X)
    assert np.all(preds == "A")


def test_naive_forecast():
    y = pd.Series([10.0, 20.0, 30.0, 45.0])
    model = NaiveForecast().fit(y)
    preds = model.predict(3)
    assert np.allclose(preds, 45.0)


def test_evaluate_regression():
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([10.0, 20.0, 30.0])

    metrics = evaluate_regression(y_true, y_pred)
    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["r2"] == 1.0


def test_evaluate_classification():
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 1])

    metrics = evaluate_classification(y_true, y_pred)
    assert metrics["accuracy"] == 1.0
    assert metrics["f1"] == 1.0
