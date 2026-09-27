import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.insight_run import InsightRun
from app.db.models.insight import Insight
from app.db.models.insight_evidence import InsightEvidence

logger = logging.getLogger(__name__)


class InsightRepository:
    """Database repository for Phase 8 Insight runs, insights, and evidence entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(self, run: InsightRun) -> InsightRun:
        self.db.add(run)
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def update_run(self, run: InsightRun) -> InsightRun:
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def get_run(self, run_id: UUID) -> Optional[InsightRun]:
        stmt = select(InsightRun).where(InsightRun.id == run_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_run_for_dataset(self, dataset_id: UUID) -> Optional[InsightRun]:
        stmt = (
            select(InsightRun)
            .where(InsightRun.dataset_id == dataset_id)
            .order_by(InsightRun.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def save_insights_and_evidence(
        self,
        run_id: UUID,
        dataset_id: UUID,
        processed_dataset_id: UUID,
        insights_data: List[Dict[str, Any]],
    ) -> List[Insight]:
        created_insights: List[Insight] = []

        for item_data in insights_data:
            insight = Insight(
                run_id=run_id,
                dataset_id=dataset_id,
                processed_dataset_id=processed_dataset_id,
                insight_type=item_data["insight_type"],
                title=item_data["title"],
                summary=item_data["summary"],
                explanation=item_data["explanation"],
                importance_score=item_data["importance_score"],
                importance_level=item_data["importance_level"],
                evidence_strength=item_data["evidence_strength"],
                columns=item_data.get("columns", []),
                statistics=item_data.get("statistics", {}),
                limitations=item_data.get("limitations", []),
                generation_mode=item_data.get("generation_mode", "LLM"),
                validation_status=item_data.get("validation_status", "VALIDATED"),
            )
            self.db.add(insight)
            await self.db.flush()
            await self.db.refresh(insight)

            # Add linked evidence items
            for evid in item_data.get("evidence_items", []):
                if isinstance(evid, dict):
                    ev_model = InsightEvidence(
                        insight_id=insight.id,
                        evidence_id=evid.get("evidence_id", ""),
                        source_phase=evid.get("source_phase", ""),
                        source_type=evid.get("source_type", ""),
                        source_id=str(evid.get("source_id", "")) if evid.get("source_id") else None,
                        metrics=evid.get("metrics", {}),
                        description=evid.get("description", ""),
                    )
                    self.db.add(ev_model)

            created_insights.append(insight)

        await self.db.flush()
        return created_insights

    async def get_insights_for_dataset(self, dataset_id: UUID) -> List[Insight]:
        stmt = (
            select(Insight)
            .where(Insight.dataset_id == dataset_id)
            .options(selectinload(Insight.evidence_items))
            .order_by(Insight.importance_score.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_insight_by_id(self, insight_id: UUID) -> Optional[Insight]:
        stmt = (
            select(Insight)
            .where(Insight.id == insight_id)
            .options(selectinload(Insight.evidence_items))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
