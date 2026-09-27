import pandas as pd
from app.services.preprocessing_planner import PreprocessingPlanner


def test_planner_detects_duplicates():
    df = pd.DataFrame({"age": [25, 25, 30], "city": ["A", "A", "B"]})
    profile_data = {"columns": []}
    planner = PreprocessingPlanner()
    plan = planner.build_plan(df, profile_data)

    types = [step["transformation_type"] for step in plan]
    assert "REMOVE_DUPLICATES" in types


def test_planner_detects_empty_and_constant_columns():
    df = pd.DataFrame({
        "empty_col": [None, None, None],
        "const_col": ["Male", "Male", "Male"],
        "normal_col": [1, 2, 3],
    })
    profile_data = {
        "columns": [
            {"column_name": "empty_col", "null_percentage": 100.0, "is_constant": True, "inferred_type": "text"},
            {"column_name": "const_col", "null_percentage": 0.0, "is_constant": True, "inferred_type": "categorical"},
            {"column_name": "normal_col", "null_percentage": 0.0, "is_constant": False, "inferred_type": "numeric"},
        ]
    }
    planner = PreprocessingPlanner()
    plan = planner.build_plan(df, profile_data)

    types = [step["transformation_type"] for step in plan]
    assert "DROP_EMPTY_COLUMN" in types
    assert "DROP_CONSTANT_COLUMN" in types


def test_planner_imputation_and_encoding_rules():
    df = pd.DataFrame({
        "user_id": ["u1", "u2", "u3"],
        "score": [10.0, None, 30.0],
        "category": ["catA", None, "catB"],
    })
    profile_data = {
        "columns": [
            {"column_name": "user_id", "inferred_type": "categorical", "null_percentage": 0.0, "unique_count": 3, "is_constant": False},
            {"column_name": "score", "inferred_type": "numeric", "null_percentage": 33.3, "unique_count": 2, "is_constant": False},
            {"column_name": "category", "inferred_type": "categorical", "null_percentage": 33.3, "unique_count": 2, "is_constant": False},
        ]
    }
    planner = PreprocessingPlanner(config={"MAX_ONE_HOT_CATEGORIES": 10})
    plan = planner.build_plan(df, profile_data)

    types = [step["transformation_type"] for step in plan]
    assert "IMPUTE_MISSING_NUMERIC" in types
    assert "IMPUTE_MISSING_CATEGORICAL" in types
    assert "ONE_HOT_ENCODING" in types
    # Identifier user_id should skip one hot encoding
    id_steps = [s for s in plan if s.get("column_name") == "user_id" and s["transformation_type"] == "HIGH_CARDINALITY_SKIPPED"]
    assert len(id_steps) == 1
