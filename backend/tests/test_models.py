import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.dataset import Dataset
from app.db.repositories.dataset_repository import DatasetRepository


@pytest.mark.asyncio
async def test_dataset_repository_crud(db_session: AsyncSession):
    repo = DatasetRepository(db_session)

    # 1. Create
    dataset = Dataset(
        name="Sales 2026",
        original_filename="sales_data.csv",
        file_type="csv",
        file_size=102450,
        storage_path="/storage/sales_data.csv",
        status="pending",
    )
    created = await repo.create(dataset)
    assert isinstance(created.id, uuid.UUID)
    assert created.name == "Sales 2026"
    assert created.status == "pending"

    # 2. Get by ID
    retrieved = await repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id

    # 3. List
    all_datasets = await repo.list_all()
    assert len(all_datasets) >= 1

    # 4. Delete
    deleted = await repo.delete(created.id)
    assert deleted is True
    assert await repo.get_by_id(created.id) is None
