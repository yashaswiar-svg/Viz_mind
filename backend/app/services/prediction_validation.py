import pandas as pd
from typing import List, Optional
from app.core.config import settings
from app.core.exceptions import (
    InsufficientClassSamplesException,
    InsufficientDataException,
    TargetColumnInvalidException,
    TargetColumnRequiredException,
)
from app.db.models.dataset_column_profile import DatasetColumnProfile


def validate_prediction_eligibility(
    df: pd.DataFrame,
    column_profiles: List[DatasetColumnProfile],
    target_column: str,
    problem_type: Optional[str] = None,
):
    """Validate that the requested dataset and target column meet eligibility constraints."""
    if not target_column or target_column not in df.columns:
        raise TargetColumnRequiredException(f"Target column '{target_column}' does not exist in dataset.")

    profile_map = {col.column_name: col for col in column_profiles}
    target_prof = profile_map.get(target_column)

    if target_prof:
        is_id = getattr(target_prof, "is_identifier", False)
        is_const = getattr(target_prof, "is_constant", False)
        sem_type = getattr(target_prof, "semantic_type", getattr(target_prof, "inferred_type", ""))

        if is_id:
            raise TargetColumnInvalidException(f"Column '{target_column}' is an identifier and cannot be a prediction target.")
        if is_const:
            raise TargetColumnInvalidException(f"Column '{target_column}' is constant and cannot be a prediction target.")
        if sem_type in ["IDENTIFIER", "FREE_TEXT"]:
            raise TargetColumnInvalidException(f"Column '{target_column}' semantic type '{sem_type}' is ineligible.")


    valid_target = df[target_column].dropna()
    if len(valid_target) < settings.MIN_PREDICTION_ROWS:
        raise InsufficientDataException(
            f"Dataset has {len(valid_target)} valid target rows; minimum required is {settings.MIN_PREDICTION_ROWS}."
        )

    if problem_type == "CLASSIFICATION":
        class_counts = valid_target.value_counts()
        if len(class_counts) < 2:
            raise TargetColumnInvalidException("Classification target must have at least 2 classes.")

        min_class_samples = class_counts.min()
        if min_class_samples < 2:
            raise InsufficientClassSamplesException(
                f"Classification class '{class_counts.idxmin()}' has only {min_class_samples} sample(s); minimum 2 required."
            )
