import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_profile_api_flow(async_client: AsyncClient):
    # 1. Upload Dataset
    csv_content = b"age,income,category\n25,50000,A\n30,60000,B\n35,70000,A\n25,50000,A\n"
    files = {"file": ("people.csv", csv_content, "text/csv")}
    upload_res = await async_client.post("/api/v1/datasets", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["id"]

    # 2. GET Profile before profiling -> 404
    get_before = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert get_before.status_code == 404
    assert get_before.json()["error"]["code"] == "PROFILE_NOT_FOUND"

    # 3. POST Profile execution -> 200
    post_res = await async_client.post(f"/api/v1/datasets/{dataset_id}/profile")
    assert post_res.status_code == 200
    p_data = post_res.json()
    assert p_data["dataset_id"] == dataset_id
    assert p_data["overview"]["rows"] == 4
    assert p_data["overview"]["columns"] == 3
    assert p_data["quality"]["score"] > 0
    assert len(p_data["columns"]) == 3

    # 4. GET Profile -> 200
    get_after = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert get_after.status_code == 200
    assert get_after.json()["id"] == p_data["id"]

    # 5. Reprofile -> replace profile
    repost_res = await async_client.post(f"/api/v1/datasets/{dataset_id}/profile")
    assert repost_res.status_code == 200

    # 6. Delete dataset -> CASCADE removes profile
    del_res = await async_client.delete(f"/api/v1/datasets/{dataset_id}")
    assert del_res.status_code == 204

    # Verify profile is also deleted
    get_del = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert get_del.status_code == 404
