import pytest
import pandas as pd
from app.services.prediction_planner import PredictionPlanner
from app.db.models.dataset_column_profile import DatasetColumnProfile


def test_prediction_planner_split_data_temporal():
    planner = PredictionPlanner()
    dates = pd.date_range("2026-01-01", periods=100, freq="D")
    vals = range(100)
    df = pd.DataFrame({"date": dates, "val": vals})

    train, val, test = planner.split_data(df, target_column="val", problem_type="FORECASTING", date_column="date")

    assert len(train) == 60
    assert len(val) == 20
    assert len(test) == 20

    # Ensure chronological order
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()


def test_prediction_planner_feature_selection_leakage():
    planner = PredictionPlanner()
    df = pd.DataFrame({
        "id": range(100),
        "feature_1": range(100),
        "post_outcome_status": range(100),
        "target": range(100),
    })

    class MockProf:
        def __init__(self, column_name, is_identifier=False, is_constant=False, semantic_type="NUMERIC"):
            self.column_name = column_name
            self.is_identifier = is_identifier
            self.is_constant = is_constant
            self.semantic_type = semantic_type
            self.inferred_type = semantic_type

    profiles = [
        MockProf(column_name="id", is_identifier=True, semantic_type="IDENTIFIER"),
        MockProf(column_name="feature_1", is_identifier=False, semantic_type="NUMERIC"),
        MockProf(column_name="post_outcome_status", is_identifier=False, semantic_type="NUMERIC"),
        MockProf(column_name="target", is_identifier=False, semantic_type="NUMERIC"),
    ]


    num_feats, cat_feats = planner.select_features(df, profiles, target_column="target")

    assert "id" not in num_feats
    assert "target" not in num_feats
    assert "post_outcome_status" not in num_feats
    assert "feature_1" in num_feats
