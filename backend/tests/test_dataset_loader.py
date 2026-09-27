import uuid
import pytest
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DatasetNotFoundException, FileValidationException
from app.db.models.dataset import Dataset
from app.services.dataset_loader import DatasetLoader
from app.services.storage_service import StorageService


class DummyAsyncFile:
    def __init__(self, content: bytes):
        self.content = content
        self.offset = 0

    async def seek(self, pos: int):
        self.offset = pos

    async def read(self, size: int):
        if self.offset >= len(self.content):
            return b""
        chunk = self.content[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


@pytest.mark.asyncio
async def test_loader_csv_success(db_session: AsyncSession, storage_service: StorageService):
    dataset_id = uuid.uuid4()
    content = b"col_a,col_b\n10,hello\n20,world\n"

    dummy_file = DummyAsyncFile(content)
    path, checksum, size = await storage_service.save_upload(dummy_file, dataset_id, "csv")

    dataset = Dataset(
        id=dataset_id,
        name="Loader Test",
        original_filename="loader_test.csv",
        file_type="csv",
        file_size=size,
        storage_path=path,
        checksum=checksum,
        status="ready",
    )
    db_session.add(dataset)
    await db_session.flush()

    loader = DatasetLoader(db_session, storage_service=storage_service)
    df, sheet_name = await loader.load_dataset(dataset_id)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["col_a", "col_b"]
    assert sheet_name is None


@pytest.mark.asyncio
async def test_loader_nonexistent_dataset(db_session: AsyncSession):
    loader = DatasetLoader(db_session)
    with pytest.raises(DatasetNotFoundException):
        await loader.load_dataset(uuid.uuid4())
