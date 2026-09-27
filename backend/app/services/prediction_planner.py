import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import settings
from app.core.exceptions import (
    TargetColumnInvalidException,
)

from app.db.models.dataset_column_profile import DatasetColumnProfile


class PredictionPlanner:
    """Plans problem type, feature selection, data leakage prevention, and split allocation."""

    def infer_problem_type(
        self,
        series: pd.Series,
        date_column: Optional[str] = None,
    ) -> str:
        if date_column and pd.api.types.is_numeric_dtype(series):
            return "FORECASTING"
        elif pd.api.types.is_numeric_dtype(series):
            # Check cardinality: if unique values <= 10 and integer-like, could be classification, but default numeric is REGRESSION
            if series.nunique() <= 5 and series.dropna().isin([0, 1]).all():
                return "CLASSIFICATION"
            return "REGRESSION"
        else:
            return "CLASSIFICATION"

    def select_features(
        self,
        df: pd.DataFrame,
        column_profiles: List[DatasetColumnProfile],
        target_column: str,
        date_column: Optional[str] = None,
    ) -> Tuple[List[str], List[str]]:
        """Select eligible numeric and categorical feature columns, protecting against data leakage.

        Excludes:
          - Target column itself
          - Obvious identifiers (ID, row_id, etc.)
          - Post-outcome fields / future timestamps
          - High-cardinality free-text or constant columns
        """
        profile_map = {col.column_name: col for col in column_profiles}

        numeric_features = []
        categorical_features = []

        leakage_keywords = ["status", "outcome", "result", "future", "post_", "payment_status"]

        for col in df.columns:
            if col == target_column or col == date_column:
                continue

            lower_col = col.lower()

            # Skip obvious identifiers
            if lower_col in ["id", "index", "row_id", "unnamed: 0"]:
                continue

            # Check profile guidance
            prof = profile_map.get(col)
            if prof:
                is_id = getattr(prof, "is_identifier", False)
                is_const = getattr(prof, "is_constant", False)
                sem_type = getattr(prof, "semantic_type", getattr(prof, "inferred_type", ""))

                if is_id or is_const or sem_type in ["IDENTIFIER", "FREE_TEXT"]:
                    continue


            # Skip obvious post-outcome fields
            if any(kw in lower_col for kw in leakage_keywords if kw not in target_column.lower()):
                continue

            # Classify feature type
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_features.append(col)
            elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col]):
                if df[col].nunique() <= settings.MAX_CATEGORICAL_CARDINALITY:
                    categorical_features.append(col)

        # Cap total features
        all_features = numeric_features + categorical_features
        if len(all_features) > settings.MAX_FEATURES:
            numeric_features = numeric_features[: settings.MAX_FEATURES]
            categorical_features = categorical_features[: max(0, settings.MAX_FEATURES - len(numeric_features))]

        return numeric_features, categorical_features

    def split_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        problem_type: str,
        date_column: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into Train (60%), Validation (20%), and Test (20%).

        Preserves chronological ordering for forecasting; uses random split for regression/classification.
        """
        clean_df = df.dropna(subset=[target_column]).copy()

        if problem_type == "FORECASTING" and date_column and date_column in clean_df.columns:
            sorted_df = clean_df.sort_values(by=date_column).reset_index(drop=True)
            n = len(sorted_df)
            n_train = int(n * (1.0 - settings.TEST_SIZE - settings.VALIDATION_SIZE))
            n_val = int(n * settings.VALIDATION_SIZE)

            train_df = sorted_df.iloc[:n_train]
            val_df = sorted_df.iloc[n_train : n_train + n_val]
            test_df = sorted_df.iloc[n_train + n_val :]
            return train_df, val_df, test_df
        else:
            shuffled_df = clean_df.sample(frac=1.0, random_state=settings.RANDOM_STATE).reset_index(drop=True)
            n = len(shuffled_df)
            n_train = int(n * (1.0 - settings.TEST_SIZE - settings.VALIDATION_SIZE))
            n_val = int(n * settings.VALIDATION_SIZE)

            train_df = shuffled_df.iloc[:n_train]
            val_df = shuffled_df.iloc[n_train : n_train + n_val]
            test_df = shuffled_df.iloc[n_train + n_val :]
            return train_df, val_df, test_df
