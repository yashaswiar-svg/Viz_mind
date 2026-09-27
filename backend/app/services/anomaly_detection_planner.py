import pandas as pd
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.db.models.dataset_column_profile import DatasetColumnProfile
from app.services.anomaly_validator import get_eligible_anomaly_columns


class AnomalyDetectionPlanner:
    """Plans anomaly detection analysis tasks across eligible columns."""

    def plan_analysis(
        self,
        df: pd.DataFrame,
        column_profiles: List[DatasetColumnProfile],
        requested_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        eligible_cols = get_eligible_anomaly_columns(df, column_profiles)
        eligible_cols = eligible_cols[: settings.MAX_ANOMALY_COLUMNS]

        date_col = None
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_col = col
                break
            # Check profile for TEMPORAL
            for prof in column_profiles:
                if prof.column_name == col and prof.semantic_type in ["DATETIME", "DATE", "TEMPORAL"]:
                    try:
                        df[col] = pd.to_datetime(df[col])
                        date_col = col
                        break
                    except Exception:
                        pass
            if date_col:
                break

        tasks = []
        for col in eligible_cols:
            if requested_method in [None, "IQR", "UNIVARIATE_COMBINED"]:
                tasks.append({"column": col, "method": "IQR"})
            if requested_method in [None, "ROBUST_ZSCORE", "UNIVARIATE_COMBINED"]:
                tasks.append({"column": col, "method": "ROBUST_ZSCORE"})
            if date_col and requested_method in [None, "TIME_SERIES_RESIDUAL", "UNIVARIATE_COMBINED"]:
                tasks.append({"column": col, "method": "TIME_SERIES_RESIDUAL", "date_column": date_col})

        return {
            "eligible_columns": eligible_cols,
            "date_column": date_col,
            "tasks": tasks,
        }
