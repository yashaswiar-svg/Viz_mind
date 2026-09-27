import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.schemas.profile import DatasetProfileResponse
from app.services.profiling_service import ProfilingService

router = APIRouter(prefix="/datasets/{dataset_id}/profile", tags=["Profiling"])


@router.post(
    "",
    response_model=DatasetProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Profile dataset",
    description="Triggers read-only dataset profiling, type inference, statistical extraction, and Data Quality Score calculation.",
)
async def profile_dataset(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
) -> DatasetProfileResponse:
    service = ProfilingService(db)
    return await service.profile_dataset(dataset.id)


@router.get(
    "",
    response_model=DatasetProfileResponse,
    summary="Get dataset profile",
    description="Retrieves the latest stored profile and quality assessment for a dataset.",
)
async def get_dataset_profile(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
) -> DatasetProfileResponse:
    service = ProfilingService(db)
    return await service.get_profile(dataset.id)
