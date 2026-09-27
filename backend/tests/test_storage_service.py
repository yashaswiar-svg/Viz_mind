import uuid
import pytest
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
async def test_save_upload_and_delete(storage_service: StorageService):
    dataset_id = uuid.uuid4()
    content = b"col1,col2\nval1,val2\n"

    dummy_file = DummyAsyncFile(content)
    logical_path, checksum, bytes_written = await storage_service.save_upload(
        dummy_file, dataset_id, "csv"
    )

    assert logical_path.startswith(f"datasets/{dataset_id}/dataset_")
    assert logical_path.endswith(".csv")
    assert bytes_written == len(content)
    assert len(checksum) == 64  # SHA-256 hex length

    # Verify physical file exists on disk
    dataset_dir = storage_service.get_dataset_dir(dataset_id)
    assert dataset_dir.exists()
    assert len(list(dataset_dir.glob("*.csv"))) == 1

    # Delete storage
    storage_service.delete_file(dataset_id)
    assert not dataset_dir.exists()
