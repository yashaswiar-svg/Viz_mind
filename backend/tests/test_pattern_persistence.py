import uuid
import pytest
from sqlalchemy import select
from app.db.models.dataset import Dataset
from app.db.models.pattern_discovery_run import PatternDiscoveryRun
from app.db.models.pattern_result import PatternResult
from app.db.repositories.pattern_discovery_repository import PatternDiscoveryRepository


@pytest.mark.asyncio
async def test_pattern_repository_crud(db_session):
    repo = PatternDiscoveryRepository(db_session)

    # Setup dummy source and processed datasets
    ds_id = uuid.uuid4()
    proc_id = uuid.uuid4()

    source_ds = Dataset(
        id=ds_id,
        name="Source DS",
        original_filename="source.csv",
        file_type="csv",
        file_size=100,
        storage_path="datasets/source.csv",
        checksum="chk_source",
        status="ready",
    )
    proc_ds = Dataset(
        id=proc_id,
        name="Proc DS",
        original_filename="proc.csv",
        file_type="csv",
        file_size=100,
        storage_path="datasets/proc.csv",
        checksum="chk_proc",
        status="ready",
        dataset_kind="PROCESSED",
        parent_dataset_id=ds_id,
    )
    db_session.add_all([source_ds, proc_ds])
    await db_session.commit()

    # Create PatternDiscoveryRun
    run = PatternDiscoveryRun(
        dataset_id=ds_id,
        processed_dataset_id=proc_id,
        processed_checksum="chk_proc",
        status="RUNNING",
    )
    run = await repo.create_run(run)
    assert run.id is not None

    # Save PatternResult records
    pat1 = PatternResult(
        run_id=run.id,
        dataset_id=ds_id,
        processed_dataset_id=proc_id,
        pattern_type="CORRELATION",
        rank=1,
        score=88.5,
        title="Sales vs Profit Correlation",
        description="Strong correlation test",
        columns=["sales", "profit"],
        statistics={"correlation": 0.82},
        significant=True,
        strength="STRONG",
        sample_size=100,
        raw_p_value=0.001,
        adjusted_p_value=0.002,
        effect_size=0.82,
        method="pearson",
    )
    await repo.save_pattern_results([pat1])

    # Complete run
    run.status = "COMPLETED"
    run.pattern_count = 1
    await repo.update_run(run)
    await db_session.commit()

    # Retrieve latest completed run
    latest_run = await repo.get_latest_completed_run_for_dataset(ds_id)
    assert latest_run is not None
    assert latest_run.id == run.id

    patterns = await repo.get_patterns_for_run(run.id)
    assert len(patterns) == 1
    assert patterns[0].title == "Sales vs Profit Correlation"
    assert patterns[0].rank == 1

    # Verify single pattern retrieval
    fetched_pat = await repo.get_pattern_by_id(pat1.id)
    assert fetched_pat is not None
    assert fetched_pat.id == pat1.id
