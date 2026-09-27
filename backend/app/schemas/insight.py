from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class InsightGenerationRequest(BaseModel):
    """Request payload for triggering Phase 8 insight generation."""

    provider: Optional[str] = Field(None, description="Optional provider override ('mock', 'gemini', 'openai')")


class InsightEvidenceResponse(BaseModel):
    """Response model for individual grounded evidence items."""

    id: UUID
    insight_id: UUID
    evidence_id: str
    source_phase: str
    source_type: str
    source_id: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightResponse(BaseModel):
    """Response model for individual insights."""

    id: UUID
    run_id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    insight_type: str
    title: str
    summary: str
    explanation: str
    importance_score: float
    importance_level: str
    evidence_strength: str
    columns: List[str] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    generation_mode: str
    validation_status: str
    created_at: datetime
    updated_at: datetime
    evidence_items: List[InsightEvidenceResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InsightRunResponse(BaseModel):
    """Response model for InsightRun status overview."""

    id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    profile_id: Optional[UUID] = None
    processed_checksum: Optional[str] = None
    status: str
    provider: str
    model: Optional[str] = None
    fallback_used: bool
    evidence_count: int
    candidate_count: int
    insight_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightListResponse(BaseModel):
    """Response model for listing dataset insights."""

    dataset_id: UUID
    latest_run: Optional[InsightRunResponse] = None
    total_insights: int
    insights: List[InsightResponse] = Field(default_factory=list)
    fallback_active: bool = False
    disclaimer: str = (
        "The analytical values shown here come from VizMind's statistical and machine-learning engines. "
        "AI is used to explain those computed results and does not independently calculate the underlying statistics."
    )

    model_config = ConfigDict(from_attributes=True)
