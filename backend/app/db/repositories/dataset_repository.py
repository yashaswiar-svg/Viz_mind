import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.dataset import Dataset
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.preprocessing_job import PreprocessingJob


class DatasetRepository:
    """Repository handling database operations for Dataset entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, dataset: Dataset) -> Dataset:
        self.session.add(dataset)
        await self.session.flush()
        await self.session.refresh(dataset)
        return dataset

    async def get_by_id(self, dataset_id: uuid.UUID) -> Optional[Dataset]:
        result = await self.session.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def count(self, user_id: Optional[uuid.UUID] = None) -> int:
        stmt = select(func.count()).select_from(Dataset)
        if user_id:
            stmt = stmt.where(Dataset.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def list_paginated(self, page: int = 1, page_size: int = 20, user_id: Optional[uuid.UUID] = None) -> Tuple[List[Dataset], int]:
        offset = (page - 1) * page_size
        total = await self.count(user_id=user_id)
        stmt = select(Dataset).offset(offset).limit(page_size).order_by(Dataset.created_at.desc())
        if user_id:
            stmt = stmt.where(Dataset.user_id == user_id)
        result = await self.session.execute(stmt)
        datasets = list(result.scalars().all())
        return datasets, total

    async def list_all(self, limit: int = 100, offset: int = 0, user_id: Optional[uuid.UUID] = None) -> List[Dataset]:
        stmt = select(Dataset).offset(offset).limit(limit).order_by(Dataset.created_at.desc())
        if user_id:
            stmt = stmt.where(Dataset.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, dataset_id: uuid.UUID) -> bool:
        dataset = await self.get_by_id(dataset_id)
        if dataset:
            # Delete derived datasets first
            derived_res = await self.session.execute(
                select(Dataset).where(Dataset.parent_dataset_id == dataset_id)
            )
            for derived in derived_res.scalars().all():
                await self.delete(derived.id)

            # Delete associated profile
            profile_res = await self.session.execute(
                select(DatasetProfile).where(DatasetProfile.dataset_id == dataset_id)
            )
            for prof in profile_res.scalars().all():
                await self.session.delete(prof)

            # Delete associated jobs
            job_res = await self.session.execute(
                select(PreprocessingJob).where(PreprocessingJob.dataset_id == dataset_id)
            )
            for job in job_res.scalars().all():
                await self.session.delete(job)

            await self.session.delete(dataset)
            await self.session.flush()
            return True
        return False
