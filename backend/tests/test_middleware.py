import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_generated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    req_id = response.headers["X-Request-ID"]
    # Verify it is a valid UUID
    parsed_uuid = uuid.UUID(req_id)
    assert str(parsed_uuid) == req_id


@pytest.mark.asyncio
async def test_request_id_passed_through(async_client: AsyncClient):
    custom_id = "test-custom-request-id-12345"
    response = await async_client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id
