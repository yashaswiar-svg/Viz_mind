import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_dataset_ownership
from app.db.database import get_db
from app.schemas.insight import (
    InsightGenerationRequest,
    InsightListResponse,
    InsightResponse,
    InsightRunResponse,
)
from app.services.insight_service import (
    InsightService,
    PreprocessingRequiredError,
    InsightVersionMismatchError,
)
from app.db.repositories.insight_repository import InsightRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets/{dataset_id}/insights", tags=["AI Insights"])


@router.post("", response_model=InsightListResponse, status_code=status.HTTP_200_OK)
async def generate_insights(
    dataset_id: UUID,
    req: Optional[InsightGenerationRequest] = None,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers Phase 8 AI Insight Engine execution for specified dataset.
    """
    service = InsightService(db)
    try:
        run, insights = await service.generate_insights(dataset_id)
        repo = InsightRepository(db)
        all_insights = await repo.get_insights_for_dataset(dataset_id)
        return InsightListResponse(
            dataset_id=dataset_id,
            latest_run=InsightRunResponse.model_validate(run),
            total_insights=len(all_insights),
            insights=[InsightResponse.model_validate(i) for i in all_insights],
            fallback_active=run.fallback_used,
        )
    except PreprocessingRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "PREPROCESSING_REQUIRED", "message": str(e)},
        )
    except InsightVersionMismatchError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INSIGHT_DATASET_VERSION_MISMATCH", "message": str(e)},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DATASET_NOT_FOUND", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Error generating insights for dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INSIGHT_GENERATION_FAILED", "message": str(e)},
        )


@router.get("", response_model=InsightListResponse, status_code=status.HTTP_200_OK)
async def list_insights(
    dataset_id: UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves persisted insights for dataset.
    """
    repo = InsightRepository(db)
    run = await repo.get_latest_run_for_dataset(dataset_id)
    all_insights = await repo.get_insights_for_dataset(dataset_id)

    return InsightListResponse(
        dataset_id=dataset_id,
        latest_run=InsightRunResponse.model_validate(run) if run else None,
        total_insights=len(all_insights),
        insights=[InsightResponse.model_validate(i) for i in all_insights],
        fallback_active=run.fallback_used if run else False,
    )


@router.get("/runs/{run_id}", response_model=InsightRunResponse, status_code=status.HTTP_200_OK)
async def get_insight_run(
    dataset_id: UUID,
    run_id: UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves status of a specific InsightRun.
    """
    repo = InsightRepository(db)
    run = await repo.get_run(run_id)
    if not run or run.dataset_id != dataset_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INSIGHT_RUN_NOT_FOUND", "message": f"Run {run_id} not found for dataset {dataset_id}."},
        )
    return InsightRunResponse.model_validate(run)


@router.get("/{insight_id}", response_model=InsightResponse, status_code=status.HTTP_200_OK)
async def get_insight_detail(
    dataset_id: UUID,
    insight_id: UUID,
    dataset=Depends(verify_dataset_ownership),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves detailed insight record including grounded evidence.
    """
    repo = InsightRepository(db)
    insight = await repo.get_insight_by_id(insight_id)
    if not insight or insight.dataset_id != dataset_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INSIGHT_NOT_FOUND", "message": f"Insight {insight_id} not found for dataset {dataset_id}."},
        )
    return InsightResponse.model_validate(insight)

