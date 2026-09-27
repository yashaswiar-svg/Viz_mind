import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.db.models.dataset import Dataset
from app.schemas.patterns import (
    PatternDiscoveryRunResponse,
    PatternResultResponse,
    PatternSummaryResponse,
)
from app.services.pattern_discovery_service import PatternDiscoveryService

router = APIRouter(prefix="/datasets", tags=["Pattern Discovery"])


@router.post(
    "/{dataset_id}/patterns",
    response_model=PatternSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger pattern discovery intelligence engine for dataset",
)
async def run_pattern_discovery(
    dataset_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> PatternSummaryResponse:
    service = PatternDiscoveryService(session)
    run, patterns = await service.run_pattern_discovery(dataset.id)
    
    significant_count = sum(1 for p in patterns if p.significant)
    strong_count = sum(1 for p in patterns if p.strength.upper() == "STRONG")

    return PatternSummaryResponse(
        run=run,
        patterns=patterns,
        total_patterns=len(patterns),
        significant_patterns=significant_count,
        strong_patterns=strong_count,
    )


@router.get(
    "/{dataset_id}/patterns",
    response_model=PatternSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve latest pattern discovery results for dataset",
)
async def get_patterns(
    dataset_id: uuid.UUID,
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    strength: Optional[str] = Query(None, description="Filter by strength (WEAK, MODERATE, STRONG)"),
    significant: Optional[bool] = Query(None, description="Filter by statistical significance"),
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> PatternSummaryResponse:
    service = PatternDiscoveryService(session)
    run, patterns = await service.get_latest_patterns_for_dataset(
        dataset_id=dataset.id,
        pattern_type=pattern_type,
        strength=strength,
        significant=significant,
    )

    if not run:
        empty_run = {
            "id": uuid.uuid4(),
            "dataset_id": dataset.id,
            "processed_dataset_id": dataset.id,
            "profile_id": None,
            "processed_checksum": None,
            "status": "NOT_STARTED",
            "started_at": None,
            "completed_at": None,
            "pattern_count": 0,
            "error_message": None,
            "created_at": None,
            "updated_at": None,
        }
        return PatternSummaryResponse(
            run=PatternDiscoveryRunResponse(**empty_run),
            patterns=[],
            total_patterns=0,
            significant_patterns=0,
            strong_patterns=0,
        )

    significant_count = sum(1 for p in patterns if p.significant)
    strong_count = sum(1 for p in patterns if p.strength.upper() == "STRONG")

    return PatternSummaryResponse(
        run=run,
        patterns=patterns,
        total_patterns=len(patterns),
        significant_patterns=significant_count,
        strong_patterns=strong_count,
    )


@router.get(
    "/{dataset_id}/patterns/{pattern_id}",
    response_model=PatternResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve individual pattern discovery result by ID",
)
async def get_pattern(
    dataset_id: uuid.UUID,
    pattern_id: uuid.UUID,
    dataset: Dataset = Depends(verify_dataset_ownership),
    session: AsyncSession = Depends(get_db),
) -> PatternResultResponse:
    service = PatternDiscoveryService(session)
    pattern = await service.get_pattern_by_id(dataset.id, pattern_id)
    return pattern
