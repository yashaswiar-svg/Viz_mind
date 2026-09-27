import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    target_column: Optional[str] = Field(
        default=None,
        description="Optional target column for prediction. If omitted, eligible target discovery will be used.",
    )
    problem_type: Optional[str] = Field(
        default=None,
        description="Optional problem type (REGRESSION, CLASSIFICATION, FORECASTING)",
    )


class PredictionResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    observation_reference: str
    actual_value: Optional[str] = None
    predicted_value: Optional[str] = None
    prediction_error: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    split: str
    created_at: datetime
    updated_at: datetime


class PaginatedPredictionResultsResponse(BaseModel):
    items: List[PredictionResultResponse]
    total: int
    offset: int
    limit: int


class PredictionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    processed_dataset_id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    processed_checksum: Optional[str] = None
    problem_type: str
    target_column: str
    model_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    training_rows: int
    validation_rows: int
    test_rows: int
    feature_columns: List[str]
    metrics: Dict[str, Any]
    baseline_metrics: Dict[str, Any]
    model_parameters: Dict[str, Any]
    random_state: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    results: List[PredictionResultResponse] = []

