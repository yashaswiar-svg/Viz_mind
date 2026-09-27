import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.schemas.preprocessing import PreprocessingReportResponse
from app.services.preprocessing_service import PreprocessingService

router = APIRouter(prefix="/datasets", tags=["Preprocessing"])


@router.post(
    "/{dataset_id}/preprocess",
    response_model=PreprocessingReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger automated preprocessing pipeline for dataset",
)
async def run_preprocessing(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> PreprocessingReportResponse:
    service = PreprocessingService(session)
    job, processed_dataset, transformations = await service.run_preprocessing(dataset.id)
    return PreprocessingReportResponse(
        job=job,
        processed_dataset=processed_dataset,
        transformations=transformations,
    )


@router.get(
    "/{dataset_id}/preprocessing",
    response_model=PreprocessingReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve latest preprocessing report for dataset",
)
async def get_preprocessing_report(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> PreprocessingReportResponse:

    service = PreprocessingService(session)
    job, processed_dataset, transformations = await service.get_latest_preprocessing_report(dataset.id)
    return PreprocessingReportResponse(
        job=job,
        processed_dataset=processed_dataset,
        transformations=transformations,
    )
