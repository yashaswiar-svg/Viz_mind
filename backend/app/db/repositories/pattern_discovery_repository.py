import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.pattern_discovery_run import PatternDiscoveryRun
from app.db.models.pattern_result import PatternResult


class PatternDiscoveryRepository:
    """Repository handling database operations for PatternDiscoveryRun and PatternResult entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, run: PatternDiscoveryRun) -> PatternDiscoveryRun:
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def update_run(self, run: PatternDiscoveryRun) -> PatternDiscoveryRun:
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_run_by_id(self, run_id: uuid.UUID) -> Optional[PatternDiscoveryRun]:
        result = await self.session.execute(
            select(PatternDiscoveryRun)
            .options(selectinload(PatternDiscoveryRun.results))
            .where(PatternDiscoveryRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_completed_run_for_dataset(self, dataset_id: uuid.UUID) -> Optional[PatternDiscoveryRun]:
        result = await self.session.execute(
            select(PatternDiscoveryRun)
            .options(selectinload(PatternDiscoveryRun.results))
            .where(
                PatternDiscoveryRun.dataset_id == dataset_id,
                PatternDiscoveryRun.status == "COMPLETED"
            )
            .order_by(PatternDiscoveryRun.completed_at.desc(), PatternDiscoveryRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_pattern_results(
        self, results: List[PatternResult]
    ) -> List[PatternResult]:
        self.session.add_all(results)
        await self.session.flush()
        return results

    async def get_patterns_for_run(self, run_id: uuid.UUID) -> List[PatternResult]:
        result = await self.session.execute(
            select(PatternResult)
            .where(PatternResult.run_id == run_id)
            .order_by(PatternResult.rank.asc())
        )
        return list(result.scalars().all())

    async def get_pattern_by_id(self, pattern_id: uuid.UUID) -> Optional[PatternResult]:
        result = await self.session.execute(
            select(PatternResult).where(PatternResult.id == pattern_id)
        )
        return result.scalar_one_or_none()

    async def delete_runs_for_dataset(self, dataset_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(PatternDiscoveryRun).where(PatternDiscoveryRun.dataset_id == dataset_id)
        )
        await self.session.flush()
