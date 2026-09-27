from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Structured analytical evidence item produced by Phase 3-7 engines."""

    evidence_id: str = Field(..., description="Unique evidence ID (e.g. EVID_001)")
    source_phase: str = Field(
        ...,
        description="Source phase (PHASE3_PROFILE, PHASE5_VISUALIZATION, PHASE6_PATTERN, PHASE7_ANOMALY, PHASE7_PREDICTION)",
    )
    source_type: str = Field(..., description="Evidence sub-type (e.g. CORRELATION, ANOMALY, PREDICTION, etc.)")
    source_id: Optional[str] = Field(None, description="Reference ID from source model if available")
    columns: List[str] = Field(default_factory=list, description="Target column names associated with this evidence")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Raw pre-computed statistical metrics")
    description: str = Field(..., description="Human-readable factual summary of evidence")
    strength_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Normalized metadata used for ranking evidence"
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
