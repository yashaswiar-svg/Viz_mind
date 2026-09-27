import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DataQualityIssue(BaseModel):
    code: str
    severity: str = Field(..., description="info, warning, or critical")
    column: Optional[str] = None
    message: str
    value: Optional[float] = None


class DatasetProfileOverview(BaseModel):
    rows: int
    columns: int
    duplicate_rows: int
    duplicate_row_percentage: float
    missing_cells: int
    missing_cell_percentage: float
    memory_bytes: int
    sheet_name: Optional[str] = None


class DatasetQualityResponse(BaseModel):
    score: float
    level: str
    issues: List[DataQualityIssue]


class DatasetColumnProfileResponse(BaseModel):
    id: uuid.UUID
    column_name: str
    column_index: int
    inferred_type: str
    pandas_dtype: str
    null_count: int
    null_percentage: float
    non_null_count: int
    unique_count: int
    unique_percentage: float
    is_constant: bool

    # Numerical
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_value: Optional[float] = None
    q1_value: Optional[float] = None
    q3_value: Optional[float] = None

    # Categorical / Text
    top_values: Optional[List[dict]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None

    # Datetime
    min_datetime: Optional[str] = None
    max_datetime: Optional[str] = None

    # Boolean
    true_count: Optional[int] = None
    false_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetProfileResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    profiled_at: datetime
    created_at: datetime
    updated_at: datetime
    overview: DatasetProfileOverview
    quality: DatasetQualityResponse
    columns: List[DatasetColumnProfileResponse]

    model_config = ConfigDict(from_attributes=True)
