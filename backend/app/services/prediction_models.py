import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple, Union
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.core.config import settings


class MeanRegressor:
    """Baseline regressor predicting the mean of the target on training data."""

    def __init__(self):
        self.mean_val: float = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        clean_y = pd.to_numeric(y, errors="coerce").dropna()
        self.mean_val = float(clean_y.mean()) if len(clean_y) > 0 else 0.0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.mean_val)


class MajorityClassClassifier:
    """Baseline classifier predicting the most frequent class in training data."""

    def __init__(self):
        self.majority_class: Any = None
        self.classes_: np.ndarray = np.array([])

    def fit(self, X: pd.DataFrame, y: pd.Series):
        clean_y = y.dropna()
        self.classes_ = np.unique(clean_y)
        if len(clean_y) > 0:
            self.majority_class = clean_y.mode()[0]
        else:
            self.majority_class = 0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.majority_class)


class NaiveForecast:
    """Naive baseline forecast predicting the last observed value in training data."""

    def __init__(self):
        self.last_value: float = 0.0

    def fit(self, y: pd.Series):
        clean_y = pd.to_numeric(y, errors="coerce").dropna()
        if len(clean_y) > 0:
            self.last_value = float(clean_y.iloc[-1])
        else:
            self.last_value = 0.0
        return self

    def predict(self, n_steps: int) -> np.ndarray:
        return np.full(n_steps, self.last_value)


def build_preprocessing_pipeline(
    numeric_features: List[str],
    categorical_features: List[str],
) -> ColumnTransformer:
    """Construct a scikit-learn ColumnTransformer for model inputs.

    Strictly fitted ONLY on the training split to avoid data leakage.
    """
    transformers = []

    if numeric_features:
        num_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        transformers.append(("num", num_pipeline, numeric_features))

    if categorical_features:
        cat_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )
        transformers.append(("cat", cat_pipeline, categorical_features))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def evaluate_regression(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, Any]:
    """Calculate MAE, RMSE, R^2, and MAPE (when valid)."""
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    metrics = {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
    }

    # Calculate MAPE only if no zero or near-zero values in y_true
    if np.all(np.abs(y_true) > 1e-5):
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0)
        metrics["mape"] = round(mape, 2)
    else:
        metrics["mape"] = None

    return metrics


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Calculate Accuracy, Precision, Recall, F1, Balanced Accuracy, ROC-AUC."""
    unique_classes = np.unique(y_true)
    is_binary = len(unique_classes) == 2
    avg_mode = "binary" if is_binary else "weighted"

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average=avg_mode, zero_division=0))
    rec = float(recall_score(y_true, y_pred, average=avg_mode, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average=avg_mode, zero_division=0))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "roc_auc": None,
    }

    if is_binary and y_prob is not None:
        try:
            auc = float(roc_auc_score(y_true, y_prob[:, 1]))
            metrics["roc_auc"] = round(auc, 4)
        except Exception:
            metrics["roc_auc"] = None

    return metrics
