import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AnomalyRequest(BaseModel):
    method: Optional[str] = Field(
        default=None,
        description="Optional detection method filter (IQR, ROBUST_ZSCORE, TIME_SERIES_RESIDUAL, or UNIVARIATE_COMBINED)",
    )


class AnomalyResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    dataset_id: uuid.UUID
    processed_dataset_id: uuid.UUID
    observation_reference: str
    column_name: str
    value: Optional[float] = None
    expected_range: Optional[Dict[str, Any]] = None
    anomaly_score: float
    severity: str
    methods_detected: List[str]
    evidence: Dict[str, Any]
    statistics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AnomalyDetectionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    processed_dataset_id: uuid.UUID
    profile_id: Optional[uuid.UUID] = None
    processed_checksum: Optional[str] = None
    method: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_observations: int
    anomaly_count: int
    anomaly_percentage: float
    results_truncated: bool
    method_summary: Dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    results: List[AnomalyResultResponse] = []

