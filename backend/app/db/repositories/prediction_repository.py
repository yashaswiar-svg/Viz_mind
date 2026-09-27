import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.prediction_run import PredictionRun
from app.db.models.prediction_result import PredictionResult


class PredictionRepository:
    """Repository handling database operations for PredictionRun and PredictionResult entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: PredictionRun) -> PredictionRun:
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def update_run(self, run: PredictionRun) -> PredictionRun:
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: uuid.UUID) -> Optional[PredictionRun]:
        result = await self.session.execute(
            select(PredictionRun)
            .options(selectinload(PredictionRun.results))
            .where(PredictionRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_completed_run_for_dataset(
        self, dataset_id: uuid.UUID
    ) -> Optional[PredictionRun]:
        result = await self.session.execute(
            select(PredictionRun)
            .options(selectinload(PredictionRun.results))
            .where(
                PredictionRun.dataset_id == dataset_id,
                PredictionRun.status == "COMPLETED",
            )
            .order_by(PredictionRun.completed_at.desc(), PredictionRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_prediction_results(
        self, results: List[PredictionResult]
    ) -> List[PredictionResult]:
        self.session.add_all(results)
        await self.session.flush()
        return results

    async def get_results_paginated(
        self,
        run_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PredictionResult], int]:
        count_stmt = select(func.count(PredictionResult.id)).where(PredictionResult.run_id == run_id)
        total_res = await self.session.execute(count_stmt)
        total_count = total_res.scalar_one() or 0

        stmt = (
            select(PredictionResult)
            .where(PredictionResult.run_id == run_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total_count

    async def delete_runs_for_dataset(self, dataset_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(PredictionRun).where(PredictionRun.dataset_id == dataset_id)
        )
        await self.session.flush()
