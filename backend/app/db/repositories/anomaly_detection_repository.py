import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.anomaly_detection_run import AnomalyDetectionRun
from app.db.models.anomaly_result import AnomalyResult


class AnomalyDetectionRepository:
    """Repository handling database operations for AnomalyDetectionRun and AnomalyResult entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: AnomalyDetectionRun) -> AnomalyDetectionRun:
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def update_run(self, run: AnomalyDetectionRun) -> AnomalyDetectionRun:
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: uuid.UUID) -> Optional[AnomalyDetectionRun]:
        result = await self.session.execute(
            select(AnomalyDetectionRun)
            .options(selectinload(AnomalyDetectionRun.results))
            .where(AnomalyDetectionRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_completed_run_for_dataset(
        self, dataset_id: uuid.UUID
    ) -> Optional[AnomalyDetectionRun]:
        result = await self.session.execute(
            select(AnomalyDetectionRun)
            .options(selectinload(AnomalyDetectionRun.results))
            .where(
                AnomalyDetectionRun.dataset_id == dataset_id,
                AnomalyDetectionRun.status == "COMPLETED",
            )
            .order_by(AnomalyDetectionRun.completed_at.desc(), AnomalyDetectionRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_anomaly_results(
        self, results: List[AnomalyResult]
    ) -> List[AnomalyResult]:
        self.session.add_all(results)
        await self.session.flush()
        return results

    async def get_anomaly_by_id(self, anomaly_id: uuid.UUID) -> Optional[AnomalyResult]:
        result = await self.session.execute(
            select(AnomalyResult).where(AnomalyResult.id == anomaly_id)
        )
        return result.scalar_one_or_none()

    async def delete_runs_for_dataset(self, dataset_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(AnomalyDetectionRun).where(AnomalyDetectionRun.dataset_id == dataset_id)
        )
        await self.session.flush()
