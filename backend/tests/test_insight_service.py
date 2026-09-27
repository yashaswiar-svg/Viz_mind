import pytest
from uuid import uuid4
from app.services.insight_service import InsightService, PreprocessingRequiredError


@pytest.mark.asyncio
async def test_insight_service_unpreprocessed_error(db_session):
    service = InsightService(db_session)
    dummy_id = uuid4()

    with pytest.raises((ValueError, PreprocessingRequiredError)):
        await service.generate_insights(dummy_id)
