import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.schemas.visualizations import (
    VisualizationDataResponse,
    VisualizationRecommendationResponse,
    VisualizationReportResponse,
)
from app.services.visualization_service import VisualizationService

router = APIRouter(prefix="/datasets", tags=["Visualizations"])


@router.post(
    "/{dataset_id}/visualizations",
    response_model=VisualizationReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger smart visualization recommendation generation for dataset",
)
async def generate_visualizations(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> VisualizationReportResponse:
    service = VisualizationService(session)
    run, recommendations = await service.generate_visualizations(dataset.id)
    return VisualizationReportResponse(
        run=run,
        recommendations=recommendations,
    )


@router.get(
    "/{dataset_id}/visualizations",
    response_model=List[VisualizationRecommendationResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve top recommended visualizations for dataset",
)
async def get_visualizations(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> List[VisualizationRecommendationResponse]:
    service = VisualizationService(session)
    recommendations = await service.get_visualizations_for_dataset(dataset.id)
    return recommendations


@router.get(
    "/{dataset_id}/visualizations/{visualization_id}/data",
    response_model=VisualizationDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve pre-aggregated chart-ready data payload for visualization",
)
async def get_visualization_data(
    dataset_id: uuid.UUID,
    visualization_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> VisualizationDataResponse:
    service = VisualizationService(session)
    chart_data = await service.get_visualization_data(dataset.id, visualization_id)
    return VisualizationDataResponse(**chart_data)
