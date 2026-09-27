from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TransformationSummaryResponse(BaseModel):
    step_order: int
    transformation_type: str
    column_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    rows_affected: int
    values_affected: int
    description: str

    model_config = ConfigDict(from_attributes=True)


class ProcessedDatasetResponse(BaseModel):
    id: UUID
    parent_dataset_id: Optional[UUID] = None
    dataset_kind: str = "PROCESSED"
    name: str
    original_filename: str
    file_type: str
    file_size: int
    checksum: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreprocessingJobResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    source_profile_id: Optional[UUID] = None
    output_dataset_id: Optional[UUID] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    missing_cells_before: int
    missing_cells_after: int
    duplicate_rows_before: int
    duplicate_rows_after: int
    source_checksum_before: Optional[str] = None
    source_checksum_after: Optional[str] = None
    processed_checksum: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreprocessingReportResponse(BaseModel):
    job: PreprocessingJobResponse
    processed_dataset: Optional[ProcessedDatasetResponse] = None
    transformations: List[TransformationSummaryResponse]

    model_config = ConfigDict(from_attributes=True)
