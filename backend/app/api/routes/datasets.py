import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, verify_dataset_ownership
from app.core.exceptions import FileValidationException
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.db.models.user import User
from app.schemas.dataset import DatasetResponse, PaginatedDatasetResponse
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post(
    "",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload dataset file",
    description="Upload a CSV (.csv) or Excel (.xlsx, .xls) dataset file up to 50 MB.",
)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DatasetResponse:
    if not file:
        raise FileValidationException("File payload is required.", code="FILE_REQUIRED")

    service = DatasetService(db)
    return await service.upload_dataset(file=file, custom_name=name, user_id=current_user.id)


@router.get(
    "",
    response_model=PaginatedDatasetResponse,
    summary="List datasets",
    description="Retrieve paginated list of uploaded datasets metadata owned by user.",
)
async def list_datasets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedDatasetResponse:
    service = DatasetService(db)
    return await service.list_datasets(page=page, page_size=page_size, user_id=current_user.id)


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
    summary="Get dataset metadata",
    description="Retrieve dataset metadata by UUID.",
)
async def get_dataset(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
) -> DatasetResponse:
    return DatasetResponse.model_validate(dataset)


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete dataset",
    description="Delete dataset metadata record and remove associated physical file storage.",
)
async def delete_dataset(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(db)
    await service.delete_dataset(dataset.id)
    return None
