import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.schemas.anomaly import (
    AnomalyDetectionRunResponse,
    AnomalyRequest,
    AnomalyResultResponse,
)
from app.services.anomaly_detection_service import AnomalyDetectionService

router = APIRouter(prefix="/datasets/{dataset_id}/anomalies", tags=["Anomalies"])


@router.post(
    "",
    response_model=AnomalyDetectionRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run anomaly detection analysis",
)
async def run_anomaly_detection(
    dataset_id: uuid.UUID,
    request_body: Optional[AnomalyRequest] = None,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = AnomalyDetectionService(session)
    method = request_body.method if request_body else None
    return await service.run_anomaly_detection(dataset_id=dataset_id, method=method)


@router.get(
    "",
    response_model=AnomalyDetectionRunResponse,
    summary="Get latest anomaly detection run for a dataset",
)
async def get_latest_anomaly_run(
    dataset_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = AnomalyDetectionService(session)
    return await service.get_latest_run(dataset_id=dataset_id)


@router.get(
    "/{anomaly_id}",
    response_model=AnomalyResultResponse,
    summary="Get specific anomaly result details",
)
async def get_anomaly_details(
    dataset_id: uuid.UUID,
    anomaly_id: uuid.UUID,
    dataset=Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
):
    service = AnomalyDetectionService(session)
    return await service.get_anomaly_by_id(anomaly_id=anomaly_id)

