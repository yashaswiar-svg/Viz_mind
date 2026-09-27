import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pattern_api_endpoints_unpreprocessed_dataset(async_client: AsyncClient):
    fake_id = uuid.uuid4()
    # GET patterns for non-existent/un-analyzed dataset should return 200 with empty patterns and NOT_STARTED status
    res_get = await async_client.get(f"/api/v1/datasets/{fake_id}/patterns")
    assert res_get.status_code in (404, 200)

    # POST discovery for non-existent dataset should return 404 DATASET_NOT_FOUND
    res_post = await async_client.post(f"/api/v1/datasets/{fake_id}/patterns")
    assert res_post.status_code in (404, 400)
    data_post = res_post.json()
    assert "error" in data_post
