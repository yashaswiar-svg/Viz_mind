import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.preprocessing_job import PreprocessingJob
from app.db.models.preprocessing_transformation import PreprocessingTransformation


class PreprocessingRepository:
    """Repository handling database operations for PreprocessingJob and PreprocessingTransformation entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job: PreprocessingJob) -> PreprocessingJob:
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job

    async def update_job(self, job: PreprocessingJob) -> PreprocessingJob:
        await self.session.flush()
        await self.session.refresh(job)
        return job

    async def get_job_by_id(self, job_id: uuid.UUID) -> Optional[PreprocessingJob]:
        result = await self.session.execute(
            select(PreprocessingJob)
            .options(selectinload(PreprocessingJob.transformations))
            .where(PreprocessingJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_job_for_dataset(self, dataset_id: uuid.UUID) -> Optional[PreprocessingJob]:
        result = await self.session.execute(
            select(PreprocessingJob)
            .options(selectinload(PreprocessingJob.transformations))
            .where(PreprocessingJob.dataset_id == dataset_id)
            .order_by(PreprocessingJob.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_transformations(
        self, transformations: List[PreprocessingTransformation]
    ) -> List[PreprocessingTransformation]:
        self.session.add_all(transformations)
        await self.session.flush()
        return transformations

    async def get_transformations_for_job(self, job_id: uuid.UUID) -> List[PreprocessingTransformation]:
        result = await self.session.execute(
            select(PreprocessingTransformation)
            .where(PreprocessingTransformation.job_id == job_id)
            .order_by(PreprocessingTransformation.step_order.asc())
        )
        return list(result.scalars().all())
