import numpy as np
import pandas as pd
from app.services.preprocessing_transformers import PreprocessingTransformers


def test_transformer_remove_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 10, 20]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.remove_duplicates(df)
    assert len(df_clean) == 2
    assert rows_aff == 1


def test_transformer_drop_empty_columns():
    df = pd.DataFrame({"a": [1, 2], "empty": [None, None]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.drop_empty_columns(df)
    assert "empty" not in df_clean.columns
    assert "a" in df_clean.columns


def test_transformer_drop_constant_columns():
    df = pd.DataFrame({"a": [1, 2], "const": ["X", "X"]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.drop_constant_columns(df)
    assert "const" not in df_clean.columns
    assert "a" in df_clean.columns


def test_transformer_impute_missing_numeric():
    df = pd.DataFrame({"age": [20.0, np.nan, 40.0]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.impute_missing_numeric(df, "age")
    assert df_clean["age"].isna().sum() == 0
    assert df_clean["age"].iloc[1] == 30.0  # median of 20 and 40 is 30


def test_transformer_impute_missing_categorical():
    df = pd.DataFrame({"city": ["Paris", None, "Tokyo"]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.impute_missing_categorical(df, "city", fill_value="Unknown")
    assert df_clean["city"].iloc[1] == "Unknown"
    assert df_clean["city"].isna().sum() == 0


def test_transformer_normalize_text_whitespace():
    df = pd.DataFrame({"name": ["  Alice ", "Bob\t", "Charlie"]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.normalize_text_whitespace(df, "name")
    assert list(df_clean["name"]) == ["Alice", "Bob", "Charlie"]
    assert vals_aff == 2


def test_transformer_one_hot_encode():
    df = pd.DataFrame({"color": ["red", "blue", "red"]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.one_hot_encode_categorical(df, "color", max_categories=5)
    assert "color" not in df_clean.columns
    assert "color_red" in df_clean.columns
    assert "color_blue" in df_clean.columns


def test_transformer_scale_numeric():
    df = pd.DataFrame({"val": [10.0, 20.0, 30.0]})
    df_clean, rows_aff, vals_aff, desc, meta = PreprocessingTransformers.scale_numeric_standard(df, "val")
    assert np.isclose(df_clean["val"].mean(), 0.0)
    assert np.isclose(df_clean["val"].std(ddof=0), 1.0)
