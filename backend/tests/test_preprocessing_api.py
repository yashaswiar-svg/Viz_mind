import io
import uuid
import pytest
from app.db.models.dataset import Dataset
from app.services.profiling_service import ProfilingService
from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_preprocess_api_endpoints(async_client, db_session, storage_service):
    # 1. Create dataset without profile
    ds_id = uuid.uuid4()
    csv_bytes = b"id,val\n1,100\n2,200\n"

    class DummyFile:
        def __init__(self, content: bytes):
            self.stream = io.BytesIO(content)

        async def read(self, size=-1):
            return self.stream.read(size)

        async def seek(self, pos):
            self.stream.seek(pos)

    dummy_file = DummyFile(csv_bytes)
    logical_path, checksum, file_size = await storage_service.save_upload(dummy_file, ds_id, "csv")

    from app.api.deps import SYSTEM_USER_ID
    dataset = Dataset(
        id=ds_id,
        user_id=SYSTEM_USER_ID,
        name="API Dataset",
        original_filename="api.csv",
        file_type="csv",
        file_size=file_size,
        storage_path=logical_path,
        checksum=checksum,
        status="ready",
    )
    db_session.add(dataset)
    await db_session.commit()

    # Attempt POST preprocess before profiling -> expect 400 PROFILE_REQUIRED
    res_unprofiled = await async_client.post(f"/api/v1/datasets/{ds_id}/preprocess")
    assert res_unprofiled.status_code == 400
    assert res_unprofiled.json()["error"]["code"] == "PROFILE_REQUIRED"

    # Now profile dataset
    profiling_service = ProfilingService(db_session)
    profiling_service.storage_service = storage_service
    await profiling_service.profile_dataset(ds_id)

    # POST preprocess -> expect 200 OK
    res_prep = await async_client.post(f"/api/v1/datasets/{ds_id}/preprocess")
    assert res_prep.status_code == 200
    data = res_prep.json()
    assert data["job"]["status"] == "COMPLETED"
    assert data["processed_dataset"]["dataset_kind"] == "PROCESSED"

    # GET preprocessing report -> expect 200 OK
    res_get = await async_client.get(f"/api/v1/datasets/{ds_id}/preprocessing")
    assert res_get.status_code == 200
    assert res_get.json()["job"]["id"] == data["job"]["id"]
