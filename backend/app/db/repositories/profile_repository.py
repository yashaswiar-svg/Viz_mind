import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.dataset_column_profile import DatasetColumnProfile


class ProfileRepository:
    """Repository handling database operations for DatasetProfile and DatasetColumnProfile."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_dataset_id(self, dataset_id: uuid.UUID) -> Optional[DatasetProfile]:
        result = await self.session.execute(
            select(DatasetProfile)
            .where(DatasetProfile.dataset_id == dataset_id)
            .options(selectinload(DatasetProfile.columns))
        )
        return result.scalar_one_or_none()

    get_profile_by_dataset_id = get_by_dataset_id

    async def save_profile(
        self,
        profile: DatasetProfile,
        columns: list[DatasetColumnProfile],
    ) -> DatasetProfile:
        """Atomically replaces any existing profile for the dataset and saves new column profiles."""
        existing = await self.get_by_dataset_id(profile.dataset_id)
        if existing:
            await self.session.delete(existing)
            await self.session.flush()

        self.session.add(profile)
        await self.session.flush()

        for col in columns:
            col.profile_id = profile.id
            self.session.add(col)

        await self.session.flush()
        await self.session.refresh(profile)

        # Re-query with columns loaded
        return await self.get_by_dataset_id(profile.dataset_id)
