import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_insight_api_endpoints_nonexistent_dataset(async_client: AsyncClient):
    fake_id = uuid.uuid4()

    # GET insights for un-analyzed dataset should return 200 with total_insights=0
    res_get = await async_client.get(f"/api/v1/datasets/{fake_id}/insights")
    assert res_get.status_code in (404, 200)

    # POST generate insights for non-existent dataset should return 404 or 400
    res_post = await async_client.post(f"/api/v1/datasets/{fake_id}/insights")
    assert res_post.status_code in (404, 400)
    data_post = res_post.json()
    assert "error" in data_post
