import os
import uuid
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatasetNotFoundException, VizMindException
from app.core.logging import logger
from app.db.models.dataset import Dataset
from app.db.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset import DatasetResponse, PaginatedDatasetResponse
from app.services.file_validation_service import FileValidationService
from app.services.storage_service import StorageService


class DatasetService:
    """Service orchestrating dataset upload ingestion, validation, storage, metadata persistence, and deletion."""

    def __init__(self, session: AsyncSession, storage_service: Optional[StorageService] = None):
        self.session = session
        self.repository = DatasetRepository(session)
        self.storage_service = storage_service or StorageService()

    async def upload_dataset(self, file: UploadFile, custom_name: Optional[str] = None, user_id: Optional[uuid.UUID] = None) -> DatasetResponse:
        original_filename = file.filename or "dataset.csv"

        # 1. Validate filename safety & extension
        sanitized_filename = FileValidationService.validate_filename_safety(original_filename)
        file_type = FileValidationService.validate_extension(sanitized_filename)

        # Read content into memory or read size
        content = await file.read()
        file_size = len(content)

        # 2. Validate size & structural validity
        FileValidationService.validate_size(file_size)
        FileValidationService.validate_structure(content, file_type)

        # 3. Generate dataset UUID & determine dataset name
        dataset_id = uuid.uuid4()
        if custom_name and custom_name.strip():
            dataset_name = custom_name.strip()
        else:
            dataset_name = os.path.splitext(sanitized_filename)[0]

        # 4. Stream save to disk & calculate checksum
        class BytesAsyncStream:
            def __init__(self, data: bytes):
                self.data = data
                self.offset = 0

            async def seek(self, pos: int):
                self.offset = pos

            async def read(self, chunk_size: int):
                if self.offset >= len(self.data):
                    return b""
                chunk = self.data[self.offset : self.offset + chunk_size]
                self.offset += len(chunk)
                return chunk

        stream_obj = BytesAsyncStream(content)
        storage_path, checksum, bytes_written = await self.storage_service.save_upload(
            stream_obj, dataset_id, file_type
        )

        # Default fallback system user if missing
        assigned_user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000000")

        # 5. Persist Dataset metadata to PostgreSQL
        dataset = Dataset(
            id=dataset_id,
            user_id=assigned_user_id,
            name=dataset_name,
            original_filename=sanitized_filename,
            file_type=file_type,
            file_size=bytes_written,
            storage_path=storage_path,
            checksum=checksum,
            status="ready",
        )

        try:
            created = await self.repository.create(dataset)
            logger.info(f"Dataset {dataset_id} metadata persisted to database for user {assigned_user_id}.")
            return DatasetResponse.model_validate(created)
        except Exception as exc:
            logger.error(f"Database error saving dataset metadata for {dataset_id}: {exc}")
            self.storage_service.cleanup_dataset_storage(dataset_id)
            raise VizMindException(
                message=f"Failed to persist dataset metadata: {str(exc)}",
                code="DATABASE_ERROR",
            )

    async def get_dataset(self, dataset_id: uuid.UUID) -> DatasetResponse:
        dataset = await self.repository.get_by_id(dataset_id)
        if not dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")
        return DatasetResponse.model_validate(dataset)

    async def list_datasets(self, page: int = 1, page_size: int = 20, user_id: Optional[uuid.UUID] = None) -> PaginatedDatasetResponse:
        items, total = await self.repository.list_paginated(page=page, page_size=page_size, user_id=user_id)
        return PaginatedDatasetResponse(
            items=[DatasetResponse.model_validate(d) for d in items],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def delete_dataset(self, dataset_id: uuid.UUID) -> bool:
        dataset = await self.repository.get_by_id(dataset_id)
        if not dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        # 1. Delete physical storage
        self.storage_service.delete_file(dataset_id)

        # 2. Delete database record
        deleted = await self.repository.delete(dataset_id)
        logger.info(f"Successfully deleted dataset {dataset_id}")
        return deleted
