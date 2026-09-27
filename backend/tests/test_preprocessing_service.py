import io
import uuid
import pytest
from app.db.models.dataset import Dataset
from app.services.profiling_service import ProfilingService
from app.services.preprocessing_service import PreprocessingService
from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_run_preprocessing_flow(db_session, storage_service):
    # 1. Upload dummy dataset
    ds_id = uuid.uuid4()
    csv_bytes = b"name,age,city\n Alice ,25.0,NY\nBob,,London\n Alice ,25.0,NY\n"

    class DummyFile:
        def __init__(self, content: bytes):
            self.content = content
            self.stream = io.BytesIO(content)

        async def read(self, size=-1):
            return self.stream.read(size)

        async def seek(self, pos):
            self.stream.seek(pos)

    dummy_file = DummyFile(csv_bytes)
    logical_path, checksum, file_size = await storage_service.save_upload(dummy_file, ds_id, "csv")

    dataset = Dataset(
        id=ds_id,
        name="Test Ingestion",
        original_filename="test.csv",
        file_type="csv",
        file_size=file_size,
        storage_path=logical_path,
        checksum=checksum,
        status="ready",
    )
    db_session.add(dataset)
    await db_session.commit()

    # 2. Run Phase 3 Profile
    profiling_service = ProfilingService(db_session)
    profiling_service.storage_service = storage_service
    await profiling_service.profile_dataset(ds_id)

    # 3. Run Phase 4 Preprocessing
    prep_service = PreprocessingService(db_session)
    prep_service.storage_service = storage_service
    job, processed_dataset, transformations = await prep_service.run_preprocessing(ds_id)

    assert job.status == "COMPLETED"
    assert job.rows_before == 3
    assert job.rows_after == 2  # 1 duplicate row removed
    assert processed_dataset.dataset_kind == "PROCESSED"
    assert processed_dataset.parent_dataset_id == ds_id
    assert len(transformations) > 0

    # 4. Verify source checksum before and after remain strictly equal
    assert job.source_checksum_before == job.source_checksum_after
