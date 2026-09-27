import hashlib
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.dataset_repository import DatasetRepository
from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_source_checksum_integrity_after_profiling(
    async_client: AsyncClient,
    db_session: AsyncSession,
    storage_service: StorageService,
):
    # Upload CSV file
    csv_content = b"user_id,amount,signup_date\n101,150.5,2026-01-01\n102,200.0,2026-01-02\n"
    initial_checksum = hashlib.sha256(csv_content).hexdigest()

    files = {"file": ("transactions.csv", csv_content, "text/csv")}
    upload_res = await async_client.post("/api/v1/datasets", files=files)
    assert upload_res.status_code == 201
    dataset_id = uuid.UUID(upload_res.json()["id"])
    assert upload_res.json()["checksum"] == initial_checksum

    # Trigger profiling
    profile_res = await async_client.post(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200

    # Verify dataset checksum in DB remains unchanged
    repo = DatasetRepository(db_session)
    dataset_after = await repo.get_by_id(dataset_id)
    assert dataset_after.checksum == initial_checksum

    # Verify physical file on disk remains unchanged
    dataset_dir = storage_service.get_dataset_dir(dataset_id)
    file_path = list(dataset_dir.glob("dataset_*.csv"))[0]
    with open(file_path, "rb") as f:
        disk_content = f.read()

    assert disk_content == csv_content
    assert hashlib.sha256(disk_content).hexdigest() == initial_checksum


@pytest.mark.asyncio
async def test_source_checksum_integrity_after_preprocessing(
    async_client: AsyncClient,
    db_session: AsyncSession,
    storage_service: StorageService,
):
    # Upload CSV file
    csv_content = b"user_id,amount,signup_date\n101,150.5,2026-01-01\n101,150.5,2026-01-01\n102,,2026-01-02\n"
    initial_checksum = hashlib.sha256(csv_content).hexdigest()

    files = {"file": ("transactions.csv", csv_content, "text/csv")}
    upload_res = await async_client.post("/api/v1/datasets", files=files)
    assert upload_res.status_code == 201
    dataset_id = uuid.UUID(upload_res.json()["id"])

    # Profile dataset
    profile_res = await async_client.post(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200

    # Trigger preprocessing
    prep_res = await async_client.post(f"/api/v1/datasets/{dataset_id}/preprocess")
    assert prep_res.status_code == 200
    prep_data = prep_res.json()

    # Verify job reported source checksum matches initial
    assert prep_data["job"]["source_checksum_before"] == initial_checksum
    assert prep_data["job"]["source_checksum_after"] == initial_checksum

    # Verify physical source file on disk remains completely unchanged
    dataset_dir = storage_service.get_dataset_dir(dataset_id)
    file_path = list(dataset_dir.glob("dataset_*.csv"))[0]
    with open(file_path, "rb") as f:
        disk_content = f.read()

    assert disk_content == csv_content
    assert hashlib.sha256(disk_content).hexdigest() == initial_checksum

