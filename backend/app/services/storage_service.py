import hashlib
import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple
from app.core.config import settings
from app.core.exceptions import StorageException
from app.core.logging import logger
from app.services.file_validation_service import FileValidationService


class StorageService:
    """Service handling safe chunked file storage, SHA-256 calculation, and physical deletion."""

    def __init__(self, base_storage_path: str = None):
        self.base_path = Path(base_storage_path or settings.STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_dataset_dir(self, dataset_id: uuid.UUID) -> Path:
        dataset_dir = (self.base_path / str(dataset_id)).resolve()
        FileValidationService.validate_path_safety(self.base_path, dataset_dir)
        return dataset_dir

    async def save_upload(
        self,
        file_obj,
        dataset_id: uuid.UUID,
        file_type: str,
    ) -> Tuple[str, str, int]:
        """Streams uploaded file to disk inside dataset_dir, computes SHA-256, and returns (logical_path, checksum, file_size)."""
        dataset_dir = self.get_dataset_dir(dataset_id)
        dataset_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = f"dataset_{uuid.uuid4().hex}.{file_type}"
        file_path = (dataset_dir / safe_filename).resolve()
        FileValidationService.validate_path_safety(self.base_path, file_path)

        sha256_hash = hashlib.sha256()
        bytes_written = 0

        try:
            # Reset stream position if possible
            if hasattr(file_obj, "seek"):
                await file_obj.seek(0)

            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file_obj.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    buffer.write(chunk)
                    sha256_hash.update(chunk)
                    bytes_written += len(chunk)

            checksum = sha256_hash.hexdigest()
            # Construct logical relative path: datasets/<uuid>/dataset_<hex>.<ext>
            logical_path = f"datasets/{dataset_id}/{safe_filename}"
            logger.info(f"Successfully stored file for dataset {dataset_id} ({bytes_written} bytes) at {logical_path}")
            return logical_path, checksum, bytes_written

        except Exception as exc:
            logger.error(f"Failed to write file for dataset {dataset_id}: {exc}")
            self.cleanup_dataset_storage(dataset_id)
            raise StorageException(f"Failed to store file on disk: {str(exc)}")

    def save_processed_dataframe(
        self,
        df,
        processed_dataset_id: uuid.UUID,
        file_type: str = "csv",
    ) -> Tuple[str, str, int]:
        """Saves a processed DataFrame to disk under a separate processed directory, returning (logical_path, checksum, file_size)."""
        processed_dir = (self.base_path.parent / "processed" / str(processed_dataset_id)).resolve()
        # Fallback if base_path is root storage dir
        if not processed_dir.parent.exists():
            processed_dir = (self.base_path / "processed" / str(processed_dataset_id)).resolve()

        processed_dir.mkdir(parents=True, exist_ok=True)
        safe_filename = f"processed_{uuid.uuid4().hex}.{file_type}"
        file_path = (processed_dir / safe_filename).resolve()

        try:
            if file_type in ("xlsx", "xls"):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)

            sha256_hash = hashlib.sha256()
            file_size = os.path.getsize(file_path)

            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    sha256_hash.update(chunk)

            checksum = sha256_hash.hexdigest()
            logical_path = f"processed/{processed_dataset_id}/{safe_filename}"
            logger.info(f"Saved processed dataset {processed_dataset_id} ({file_size} bytes) at {logical_path}")
            return logical_path, checksum, file_size

        except Exception as exc:
            logger.error(f"Failed to save processed dataset {processed_dataset_id}: {exc}")
            if processed_dir.exists():
                shutil.rmtree(processed_dir, ignore_errors=True)
            raise StorageException(f"Failed to save processed dataset on disk: {str(exc)}")

    def cleanup_dataset_storage(self, dataset_id: uuid.UUID) -> None:
        """Removes the entire storage directory for a dataset (checking both dataset_dir and processed_dir)."""
        try:
            dataset_dir = self.get_dataset_dir(dataset_id)
            if dataset_dir.exists():
                shutil.rmtree(dataset_dir)
                logger.info(f"Cleaned up storage directory for dataset {dataset_id}")

            processed_dir1 = (self.base_path.parent / "processed" / str(dataset_id)).resolve()
            if processed_dir1.exists():
                shutil.rmtree(processed_dir1)
                logger.info(f"Cleaned up processed storage directory for dataset {dataset_id}")

            processed_dir2 = (self.base_path / "processed" / str(dataset_id)).resolve()
            if processed_dir2.exists():
                shutil.rmtree(processed_dir2)
        except Exception as exc:
            logger.warning(f"Failed to clean up storage for dataset {dataset_id}: {exc}")

    def delete_file(self, dataset_id: uuid.UUID) -> None:
        """Deletes dataset directory and all contained files."""
        self.cleanup_dataset_storage(dataset_id)

