from typing import Any, Dict, List
import pandas as pd


class PreprocessingPlannerConfig:
    """Centralized configuration defaults for Phase 4 preprocessing planner."""

    EMPTY_COLUMN_THRESHOLD: float = 100.0
    HIGH_MISSINGNESS_THRESHOLD: float = 80.0
    MAX_ONE_HOT_CATEGORIES: int = 20
    NUMERIC_IMPUTATION_STRATEGY: str = "median"
    CATEGORICAL_IMPUTATION_STRATEGY: str = "Unknown"
    TEXT_IMPUTATION_STRATEGY: str = "Unknown"
    ENABLE_SCALING: bool = False


class PreprocessingPlanner:
    """Planner that analyzes DataFrame structure and Phase 3 profile to build a deterministic PreprocessingPlan."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_one_hot = self.config.get("MAX_ONE_HOT_CATEGORIES", PreprocessingPlannerConfig.MAX_ONE_HOT_CATEGORIES)
        self.enable_scaling = self.config.get("ENABLE_SCALING", PreprocessingPlannerConfig.ENABLE_SCALING)

    @staticmethod
    def is_identifier_column(col_name: str) -> bool:
        lower = col_name.lower()
        return lower in ("id", "uuid", "guid") or lower.endswith("_id") or lower.endswith("id") or lower in ("email", "ssn", "phone", "mobile")

    def build_plan(self, df: pd.DataFrame, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = []
        step_order = 1

        # Step 1: Duplicate Rows Removal
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            steps.append({
                "step_order": step_order,
                "transformation_type": "REMOVE_DUPLICATES",
                "column_name": None,
                "parameters": {"duplicates_detected": dup_count},
                "reason": f"Detected {dup_count} exact duplicate rows.",
            })
            step_order += 1

        # Inspect column profiles from Phase 3 profile data
        cols_meta = {col["column_name"]: col for col in profile_data.get("columns", [])}

        empty_cols = []
        constant_cols = []

        for col in df.columns:
            meta = cols_meta.get(col, {})
            null_pct = meta.get("null_percentage", (df[col].isna().sum() / len(df) * 100) if len(df) > 0 else 0)
            is_const = meta.get("is_constant", (df[col].dropna().nunique() <= 1 if len(df[col].dropna()) > 0 else False))

            if null_pct >= 100.0:
                empty_cols.append(col)
            elif is_const:
                constant_cols.append(col)

        # Step 2: Empty Columns Removal
        if empty_cols:
            steps.append({
                "step_order": step_order,
                "transformation_type": "DROP_EMPTY_COLUMN",
                "column_name": None,
                "parameters": {"columns": empty_cols},
                "reason": f"Columns {empty_cols} contain 100% missing values.",
            })
            step_order += 1

        # Step 3: Constant Columns Removal
        if constant_cols:
            steps.append({
                "step_order": step_order,
                "transformation_type": "DROP_CONSTANT_COLUMN",
                "column_name": None,
                "parameters": {"columns": constant_cols},
                "reason": f"Columns {constant_cols} contain single constant value.",
            })
            step_order += 1

        # Remaining columns
        active_cols = [c for c in df.columns if c not in empty_cols and c not in constant_cols]

        for col in active_cols:
            meta = cols_meta.get(col, {})
            inferred_type = meta.get("inferred_type", "text")
            null_count = int(df[col].isna().sum())

            # Text Normalization
            if inferred_type in ("text", "categorical"):
                steps.append({
                    "step_order": step_order,
                    "transformation_type": "NORMALIZE_TEXT",
                    "column_name": col,
                    "parameters": {},
                    "reason": f"Strip leading/trailing whitespace from string column '{col}'.",
                })
                step_order += 1

            # Missing value imputation
            if null_count > 0:
                if inferred_type == "numeric":
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "IMPUTE_MISSING_NUMERIC",
                        "column_name": col,
                        "parameters": {"strategy": "median"},
                        "reason": f"Impute {null_count} missing numeric values in '{col}' using median.",
                    })
                    step_order += 1

                elif inferred_type == "categorical":
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "IMPUTE_MISSING_CATEGORICAL",
                        "column_name": col,
                        "parameters": {"strategy": "constant", "fill_value": "Unknown"},
                        "reason": f"Impute {null_count} missing categorical values in '{col}' with 'Unknown'.",
                    })
                    step_order += 1

                elif inferred_type == "text":
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "IMPUTE_MISSING_TEXT",
                        "column_name": col,
                        "parameters": {"strategy": "constant", "fill_value": "Unknown"},
                        "reason": f"Impute {null_count} missing text values in '{col}' with 'Unknown'.",
                    })
                    step_order += 1

            # Categorical encoding
            if inferred_type == "categorical":
                unique_cnt = meta.get("unique_count", df[col].dropna().nunique())
                if self.is_identifier_column(col):
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "HIGH_CARDINALITY_SKIPPED",
                        "column_name": col,
                        "parameters": {"reason": "Identifier column preserved without encoding."},
                        "reason": f"Identifier column '{col}' skipped from one-hot encoding.",
                    })
                    step_order += 1
                elif unique_cnt <= self.max_one_hot and unique_cnt > 1:
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "ONE_HOT_ENCODING",
                        "column_name": col,
                        "parameters": {"max_categories": self.max_one_hot, "cardinality": unique_cnt},
                        "reason": f"One-hot encode low-cardinality categorical column '{col}' ({unique_cnt} categories).",
                    })
                    step_order += 1
                elif unique_cnt > self.max_one_hot:
                    steps.append({
                        "step_order": step_order,
                        "transformation_type": "HIGH_CARDINALITY_SKIPPED",
                        "column_name": col,
                        "parameters": {"max_categories": self.max_one_hot, "cardinality": unique_cnt},
                        "reason": f"High cardinality column '{col}' ({unique_cnt} > max {self.max_one_hot}) preserved without encoding.",
                    })
                    step_order += 1

            # Optional Numeric Scaling
            if inferred_type == "numeric" and self.enable_scaling and not self.is_identifier_column(col):
                steps.append({
                    "step_order": step_order,
                    "transformation_type": "SCALE_NUMERIC",
                    "column_name": col,
                    "parameters": {"strategy": "standard"},
                    "reason": f"Standardize numeric column '{col}'.",
                })
                step_order += 1

        return steps
