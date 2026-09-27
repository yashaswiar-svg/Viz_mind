import uuid
import pytest
from app.db.models.preprocessing_job import PreprocessingJob
from app.db.models.preprocessing_transformation import PreprocessingTransformation
from app.db.repositories.preprocessing_repository import PreprocessingRepository


@pytest.mark.asyncio
async def test_preprocessing_repository_crud(db_session):
    repo = PreprocessingRepository(db_session)
    dataset_id = uuid.uuid4()

    # Create job
    job = PreprocessingJob(
        dataset_id=dataset_id,
        status="PENDING",
        rows_before=100,
        rows_after=90,
        columns_before=5,
        columns_after=6,
    )
    job = await repo.create_job(job)
    assert job.id is not None

    # Save transformations
    trans = PreprocessingTransformation(
        job_id=job.id,
        step_order=1,
        transformation_type="REMOVE_DUPLICATES",
        column_name=None,
        parameters={"duplicates_removed": 10},
        rows_affected=10,
        values_affected=10,
        description="Removed 10 exact duplicate rows.",
    )
    await repo.save_transformations([trans])
    await db_session.commit()

    # Get latest job
    latest = await repo.get_latest_job_for_dataset(dataset_id)
    assert latest is not None
    assert latest.id == job.id
    assert len(latest.transformations) == 1
    assert latest.transformations[0].transformation_type == "REMOVE_DUPLICATES"
