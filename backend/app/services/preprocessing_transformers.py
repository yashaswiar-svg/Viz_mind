from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class PreprocessingTransformers:
    """Pure, deterministic DataFrame transformation functions for Phase 4 preprocessing."""

    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        initial_rows = len(df)
        df_clean = df.drop_duplicates()
        rows_removed = initial_rows - len(df_clean)
        desc = f"Removed {rows_removed} exact duplicate rows." if rows_removed > 0 else "No duplicate rows detected."
        return df_clean, rows_removed, rows_removed, desc, {"duplicate_rows_removed": rows_removed}

    @staticmethod
    def drop_empty_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if not empty_cols:
            return df, 0, 0, "No completely empty columns detected.", {"dropped_columns": []}

        df_clean = df.drop(columns=empty_cols)
        desc = f"Dropped {len(empty_cols)} completely empty column(s): {', '.join(empty_cols)}."
        return df_clean, 0, len(empty_cols), desc, {"dropped_columns": empty_cols}

    @staticmethod
    def drop_constant_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        constant_cols = []
        for col in df.columns:
            non_nulls = df[col].dropna()
            if len(non_nulls) > 0 and non_nulls.nunique() == 1:
                constant_cols.append(col)

        if not constant_cols:
            return df, 0, 0, "No constant columns detected.", {"dropped_columns": []}

        df_clean = df.drop(columns=constant_cols)
        desc = f"Dropped {len(constant_cols)} constant column(s): {', '.join(constant_cols)}."
        return df_clean, 0, len(constant_cols), desc, {"dropped_columns": constant_cols}

    @staticmethod
    def impute_missing_numeric(
        df: pd.DataFrame, column: str, strategy: str = "median"
    ) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        null_count = int(df[column].isna().sum())
        if null_count == 0:
            return df, 0, 0, f"No missing values in numeric column '{column}'.", {"column": column, "imputed_count": 0}

        non_null = df[column].dropna()
        if len(non_null) == 0:
            return df, 0, 0, f"Numeric column '{column}' is entirely null, skipped imputation.", {"column": column, "imputed_count": 0}

        fill_val = float(non_null.median())
        df[column] = df[column].fillna(fill_val)
        desc = f"Imputed {null_count} missing value(s) in column '{column}' using median ({fill_val})."
        return df, 0, null_count, desc, {"column": column, "strategy": strategy, "fill_value": fill_val, "imputed_count": null_count}

    @staticmethod
    def impute_missing_categorical(
        df: pd.DataFrame, column: str, fill_value: str = "Unknown"
    ) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        null_count = int(df[column].isna().sum())
        if null_count == 0:
            return df, 0, 0, f"No missing values in categorical column '{column}'.", {"column": column, "imputed_count": 0}

        df[column] = df[column].fillna(fill_value)
        desc = f"Imputed {null_count} missing value(s) in categorical column '{column}' with '{fill_value}'."
        return df, 0, null_count, desc, {"column": column, "fill_value": fill_value, "imputed_count": null_count}

    @staticmethod
    def impute_missing_text(
        df: pd.DataFrame, column: str, fill_value: str = "Unknown"
    ) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        null_count = int(df[column].isna().sum())
        if null_count == 0:
            return df, 0, 0, f"No missing values in text column '{column}'.", {"column": column, "imputed_count": 0}

        df[column] = df[column].fillna(fill_value)
        desc = f"Imputed {null_count} missing value(s) in text column '{column}' with '{fill_value}'."
        return df, 0, null_count, desc, {"column": column, "fill_value": fill_value, "imputed_count": null_count}

    @staticmethod
    def normalize_text_whitespace(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        if column not in df.columns:
            return df, 0, 0, f"Column '{column}' not found.", {}

        def _clean_str(val):
            if isinstance(val, str):
                return val.strip()
            return val

        original_series = df[column].copy()
        df[column] = df[column].apply(_clean_str)
        diff_count = int((original_series != df[column]).sum())
        desc = f"Normalized leading/trailing whitespace for {diff_count} string value(s) in column '{column}'."
        return df, 0, diff_count, desc, {"column": column, "normalized_count": diff_count}

    @staticmethod
    def one_hot_encode_categorical(
        df: pd.DataFrame, column: str, max_categories: int = 20
    ) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        unique_vals = df[column].dropna().unique()
        n_unique = len(unique_vals)

        if n_unique > max_categories or n_unique <= 1:
            desc = f"Skipped one-hot encoding for column '{column}' (cardinality {n_unique} > max {max_categories})."
            return df, 0, 0, desc, {"column": column, "action": "SKIPPED", "cardinality": n_unique}

        dummies = pd.get_dummies(df[column], prefix=column, dtype=int)
        df = df.drop(columns=[column])
        df = pd.concat([df, dummies], axis=1)
        gen_cols = list(dummies.columns)

        desc = f"One-hot encoded column '{column}' into {len(gen_cols)} binary indicator columns."
        return df, 0, len(df), desc, {"column": column, "generated_columns": gen_cols, "cardinality": n_unique}

    @staticmethod
    def scale_numeric_standard(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int, int, str, Dict[str, Any]]:
        df = df.copy()
        non_nulls = df[column].dropna()
        if len(non_nulls) == 0:
            return df, 0, 0, f"Numeric column '{column}' has no valid values for scaling.", {}

        mean_val = float(non_nulls.mean())
        std_val = float(non_nulls.std(ddof=0))
        if std_val == 0:
            return df, 0, 0, f"Numeric column '{column}' has zero variance, skipped scaling.", {}

        df[column] = (df[column] - mean_val) / std_val
        desc = f"Standardized numeric column '{column}' (mean={mean_val:.2f}, std={std_val:.2f})."
        return df, 0, len(df), desc, {"column": column, "mean": mean_val, "std": std_val}
