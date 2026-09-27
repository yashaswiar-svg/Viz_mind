import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.visualization_run import VisualizationRun
from app.db.models.visualization_recommendation import VisualizationRecommendation


class VisualizationRepository:
    """Repository handling database operations for VisualizationRun and VisualizationRecommendation entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: VisualizationRun) -> VisualizationRun:
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def update_run(self, run: VisualizationRun) -> VisualizationRun:
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: uuid.UUID) -> Optional[VisualizationRun]:
        result = await self.session.execute(
            select(VisualizationRun)
            .options(selectinload(VisualizationRun.recommendations))
            .where(VisualizationRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_run_for_dataset(self, dataset_id: uuid.UUID) -> Optional[VisualizationRun]:
        result = await self.session.execute(
            select(VisualizationRun)
            .options(selectinload(VisualizationRun.recommendations))
            .where(VisualizationRun.dataset_id == dataset_id)
            .order_by(VisualizationRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_recommendations(
        self, recommendations: List[VisualizationRecommendation]
    ) -> List[VisualizationRecommendation]:
        self.session.add_all(recommendations)
        await self.session.flush()
        return recommendations

    async def get_recommendations_for_dataset(self, dataset_id: uuid.UUID) -> List[VisualizationRecommendation]:
        latest_run = await self.get_latest_run_for_dataset(dataset_id)
        if not latest_run:
            return []
        result = await self.session.execute(
            select(VisualizationRecommendation)
            .where(VisualizationRecommendation.run_id == latest_run.id)
            .order_by(VisualizationRecommendation.rank.asc())
        )
        return list(result.scalars().all())

    async def get_recommendation_by_id(
        self, recommendation_id: uuid.UUID
    ) -> Optional[VisualizationRecommendation]:
        result = await self.session.execute(
            select(VisualizationRecommendation)
            .where(VisualizationRecommendation.id == recommendation_id)
        )
        return result.scalar_one_or_none()

    async def delete_recommendations_for_dataset(self, dataset_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(VisualizationRun).where(VisualizationRun.dataset_id == dataset_id)
        )
        await self.session.flush()
