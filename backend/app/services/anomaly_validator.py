import pandas as pd
from typing import List
from app.db.models.dataset_column_profile import DatasetColumnProfile


def get_eligible_anomaly_columns(
    df: pd.DataFrame,
    column_profiles: List[DatasetColumnProfile],
) -> List[str]:
    """Identify numeric columns eligible for anomaly detection.

    Excludes:
      - Obvious identifiers (IDs, customer_id, transaction_id, etc.)
      - Constant columns
      - All-null columns
      - Non-numeric columns
      - Free text or extreme high cardinality columns
    """
    profile_map = {col.column_name: col for col in column_profiles}
    eligible = []

    for col in df.columns:
        # 1. Must be numeric in DataFrame
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        prof = profile_map.get(col)
        if prof:
            is_id = getattr(prof, "is_identifier", False)
            is_const = getattr(prof, "is_constant", False)
            sem_type = getattr(prof, "semantic_type", getattr(prof, "inferred_type", ""))

            if is_id or is_const or sem_type in ["IDENTIFIER", "FREE_TEXT"]:
                continue


        # 5. Check actual data characteristics
        valid_series = df[col].dropna()
        if len(valid_series) < 10:
            continue

        if valid_series.nunique() <= 1:
            continue

        # Exclude exact sequential row indices if present
        lower_col = col.lower()
        if lower_col in ["id", "index", "row_id", "unnamed: 0"]:
            continue

        eligible.append(col)

    return eligible
