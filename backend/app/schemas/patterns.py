from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PatternResultResponse(BaseModel):
    id: UUID
    run_id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    pattern_type: str
    rank: int
    score: float
    title: str
    description: Optional[str] = None
    columns: List[str]
    statistics: Dict[str, Any]
    significant: bool
    strength: str
    sample_size: int
    raw_p_value: Optional[float] = None
    adjusted_p_value: Optional[float] = None
    effect_size: Optional[float] = None
    method: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatternDiscoveryRunResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    processed_dataset_id: UUID
    profile_id: Optional[UUID] = None
    processed_checksum: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pattern_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatternSummaryResponse(BaseModel):
    run: PatternDiscoveryRunResponse
    patterns: List[PatternResultResponse]
    total_patterns: int
    significant_patterns: int
    strong_patterns: int

    model_config = ConfigDict(from_attributes=True)
