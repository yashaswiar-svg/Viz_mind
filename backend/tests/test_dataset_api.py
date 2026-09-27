import io
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_csv_success(async_client: AsyncClient):
    csv_content = b"header1,header2\nvalue1,value2\n"
    files = {"file": ("test_data.csv", csv_content, "text/csv")}
    data = {"name": "Test Sales Dataset"}

    response = await async_client.post("/api/v1/datasets", files=files, data=data)
    assert response.status_code == 201
    res = response.json()
    assert res["name"] == "Test Sales Dataset"
    assert res["original_filename"] == "test_data.csv"
    assert res["file_type"] == "csv"
    assert res["file_size"] == len(csv_content)
    assert res["status"] == "ready"
    assert "checksum" in res
    assert res["checksum"] is not None


@pytest.mark.asyncio
async def test_upload_unsupported_file(async_client: AsyncClient):
    pdf_content = b"%PDF-1.4 dummy content"
    files = {"file": ("report.pdf", pdf_content, "application/pdf")}

    response = await async_client.post("/api/v1/datasets", files=files)
    assert response.status_code == 400
    res = response.json()
    assert res["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_empty_file(async_client: AsyncClient):
    files = {"file": ("empty.csv", b"", "text/csv")}

    response = await async_client.post("/api/v1/datasets", files=files)
    assert response.status_code == 400
    res = response.json()
    assert res["error"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_upload_path_traversal_attempt(async_client: AsyncClient):
    csv_content = b"a,b\n1,2\n"
    files = {"file": ("../../malicious.csv", csv_content, "text/csv")}

    response = await async_client.post("/api/v1/datasets", files=files)
    assert response.status_code == 400
    res = response.json()
    assert res["error"]["code"] == "INVALID_FILENAME"


@pytest.mark.asyncio
async def test_dataset_crud_flow(async_client: AsyncClient):
    # 1. Upload
    csv_content = b"x,y,z\n10,20,30\n"
    files = {"file": ("metrics.csv", csv_content, "text/csv")}
    upload_res = await async_client.post("/api/v1/datasets", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["id"]

    # 2. Get by ID
    get_res = await async_client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == dataset_id
    assert get_res.json()["name"] == "metrics"

    # 3. List
    list_res = await async_client.get("/api/v1/datasets?page=1&page_size=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert list_data["page"] == 1
    assert any(item["id"] == dataset_id for item in list_data["items"])

    # 4. Delete
    del_res = await async_client.delete(f"/api/v1/datasets/{dataset_id}")
    assert del_res.status_code == 204

    # 5. Verify 404 after delete
    get_after_del = await async_client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_after_del.status_code == 404
    assert get_after_del.json()["error"]["code"] == "DATASET_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_nonexistent_dataset(async_client: AsyncClient):
    random_uuid = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/datasets/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DATASET_NOT_FOUND"
