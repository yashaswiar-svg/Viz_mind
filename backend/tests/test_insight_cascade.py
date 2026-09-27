import pytest
from uuid import uuid4
from sqlalchemy import select
from app.db.models.insight_run import InsightRun
from app.db.models.insight import Insight
from app.db.models.insight_evidence import InsightEvidence


@pytest.mark.asyncio
async def test_insight_models_cascade_query(db_session):
    dummy_dataset_id = uuid4()
    dummy_processed_id = uuid4()

    # Querying nonexistent dataset should return empty
    res_runs = await db_session.execute(select(InsightRun).where(InsightRun.dataset_id == dummy_dataset_id))
    assert res_runs.scalar_one_or_none() is None

    res_insights = await db_session.execute(select(Insight).where(Insight.dataset_id == dummy_dataset_id))
    assert len(list(res_insights.scalars().all())) == 0
