import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DatasetBase(BaseModel):
    name: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=50)
    file_size: int = Field(..., ge=0)
    storage_path: Optional[str] = None
    checksum: Optional[str] = None


class DatasetCreate(DatasetBase):
    pass


class DatasetResponse(DatasetBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDatasetResponse(BaseModel):
    items: List[DatasetResponse]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
