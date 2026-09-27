import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.schemas.prediction import (
    PaginatedPredictionResultsResponse,
    PredictionRequest,
    PredictionRunResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/datasets/{dataset_id}/predictions", tags=["Predictions"])


@router.post(
    "",
    response_model=PredictionRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run prediction and forecasting analysis",
)
async def run_prediction_analysis(
    dataset_id: uuid.UUID,
    request_body: Optional[PredictionRequest] = None,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = PredictionService(session)
    target_column = request_body.target_column if request_body else None
    problem_type = request_body.problem_type if request_body else None

    return await service.run_prediction(
        dataset_id=dataset_id,
        target_column=target_column,
        problem_type=problem_type,
    )


@router.get(
    "",
    response_model=PredictionRunResponse,
    summary="Get latest prediction run for a dataset",
)
async def get_latest_prediction_run(
    dataset_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = PredictionService(session)
    return await service.get_latest_run(dataset_id=dataset_id)


@router.get(
    "/{run_id}",
    response_model=PredictionRunResponse,
    summary="Get specific prediction run details",
)
async def get_prediction_run(
    dataset_id: uuid.UUID,
    run_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = PredictionService(session)
    return await service.get_run_by_id(run_id=run_id)


@router.get(
    "/{run_id}/results",
    response_model=PaginatedPredictionResultsResponse,
    summary="Get paginated prediction results for a run",
)
async def get_prediction_results_paginated(
    dataset_id: uuid.UUID,
    run_id: uuid.UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = PredictionService(session)
    items, total = await service.get_prediction_results(run_id=run_id, offset=offset, limit=limit)
    return PaginatedPredictionResultsResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )

