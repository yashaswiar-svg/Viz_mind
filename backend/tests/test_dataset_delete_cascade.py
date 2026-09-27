import io
import uuid
import pytest
from sqlalchemy import select
from app.db.models.dataset import Dataset
from app.db.models.dataset_profile import DatasetProfile
from app.db.models.preprocessing_job import PreprocessingJob
from app.db.models.preprocessing_transformation import PreprocessingTransformation
from app.db.repositories.dataset_repository import DatasetRepository
from app.services.profiling_service import ProfilingService
from app.services.preprocessing_service import PreprocessingService


@pytest.mark.asyncio
async def test_dataset_delete_cascade_purges_all_derived_records(db_session, storage_service):
    # 1. Create dataset
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
        name="Cascade Source",
        original_filename="cascade.csv",
        file_type="csv",
        file_size=file_size,
        storage_path=logical_path,
        checksum=checksum,
        status="ready",
    )
    db_session.add(dataset)
    await db_session.commit()

    # Profile & Preprocess
    profiling_service = ProfilingService(db_session)
    profiling_service.storage_service = storage_service
    await profiling_service.profile_dataset(ds_id)

    prep_service = PreprocessingService(db_session)
    prep_service.storage_service = storage_service
    job, processed_ds, transformations = await prep_service.run_preprocessing(ds_id)

    # Delete source dataset
    repo = DatasetRepository(db_session)
    deleted = await repo.delete(ds_id)
    storage_service.delete_file(ds_id)
    if processed_ds:
        storage_service.delete_file(processed_ds.id)
    await db_session.commit()
    db_session.expire_all()

    assert deleted is True

    # Verify all records purged from DB
    res_source = await db_session.execute(select(Dataset).where(Dataset.id == ds_id))
    assert res_source.scalar_one_or_none() is None

    res_proc = await db_session.execute(select(Dataset).where(Dataset.id == processed_ds.id))
    assert res_proc.scalar_one_or_none() is None

    res_prof = await db_session.execute(select(DatasetProfile).where(DatasetProfile.dataset_id == ds_id))
    assert res_prof.scalar_one_or_none() is None

    res_job = await db_session.execute(select(PreprocessingJob).where(PreprocessingJob.id == job.id))
    assert res_job.scalar_one_or_none() is None

    res_trans = await db_session.execute(select(PreprocessingTransformation).where(PreprocessingTransformation.job_id == job.id))
    assert len(list(res_trans.scalars().all())) == 0
