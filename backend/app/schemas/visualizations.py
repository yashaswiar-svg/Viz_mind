from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class VisualizationRecommendationResponse(BaseModel):
    id: UUID
    run_id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    profile_id: Optional[UUID] = None
    rank: int
    chart_type: str
    title: str
    description: Optional[str] = None
    x_column: str
    y_column: Optional[str] = None
    aggregation: Optional[str] = None
    score: float
    reason: str
    chart_spec: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VisualizationRunResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    profile_id: Optional[UUID] = None
    processed_checksum: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    recommendation_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VisualizationReportResponse(BaseModel):
    run: VisualizationRunResponse
    recommendations: List[VisualizationRecommendationResponse]

    model_config = ConfigDict(from_attributes=True)


class VisualizationDataResponse(BaseModel):
    visualization_id: str
    title: str
    rank: int
    score: float
    reason: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
