import io
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatasetNotFoundException, FileValidationException
from app.db.repositories.dataset_repository import DatasetRepository
from app.services.storage_service import StorageService


class DatasetLoader:
    """Service safely loading stored dataset files into Pandas DataFrames."""

    def __init__(self, session: Optional[AsyncSession] = None, storage_service: Optional[StorageService] = None):
        self.session = session
        self.repository = DatasetRepository(session) if session else None
        self.storage_service = storage_service or StorageService()

    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        import hashlib
        path = Path(file_path).resolve()
        if not path.exists():
            return ""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def load_dataframe(file_path: str, file_type: str = "csv") -> pd.DataFrame:
        path = Path(file_path).resolve()
        if file_type in ["xlsx", "xls"]:
            return pd.read_excel(path)
        return pd.read_csv(path)


    async def load_dataset(self, dataset_id: uuid.UUID) -> Tuple[pd.DataFrame, Optional[str]]:
        dataset = await self.repository.get_by_id(dataset_id)
        if not dataset:
            raise DatasetNotFoundException(f"Dataset with ID {dataset_id} not found.")

        # Resolve internal physical path safely
        dataset_dir = self.storage_service.get_dataset_dir(dataset_id)
        if not dataset_dir.exists():
            raise FileValidationException(
                f"Source storage directory for dataset {dataset_id} does not exist.",
                code="STORAGE_ERROR",
            )

        # Locate physical file in dataset dir
        file_paths = list(dataset_dir.glob(f"dataset_*.{dataset.file_type}"))
        if not file_paths:
            raise FileValidationException(
                f"Physical dataset file missing for dataset {dataset_id}.",
                code="STORAGE_ERROR",
            )

        physical_file = file_paths[0]
        sheet_name: Optional[str] = None

        try:
            if dataset.file_type == "csv":
                # Load CSV cleanly
                df = pd.read_csv(physical_file)
            elif dataset.file_type in ["xlsx", "xls"]:
                # Inspect sheet names
                excel_file = pd.ExcelFile(physical_file)
                if not excel_file.sheet_names:
                    raise FileValidationException("Excel workbook contains no sheets.", code="INVALID_FILE")

                # Find first non-empty sheet
                selected_sheet = excel_file.sheet_names[0]
                for sheet in excel_file.sheet_names:
                    temp_df = pd.read_excel(excel_file, sheet_name=sheet, nrows=5)
                    if not temp_df.empty:
                        selected_sheet = sheet
                        break

                df = pd.read_excel(excel_file, sheet_name=selected_sheet)
                sheet_name = selected_sheet
            else:
                raise FileValidationException(
                    f"Unsupported file format '{dataset.file_type}' for dataset loader.",
                    code="UNSUPPORTED_FILE_TYPE",
                )

            return df, sheet_name

        except FileValidationException:
            raise
        except Exception as exc:
            raise FileValidationException(
                f"Failed to load dataset file: {str(exc)}",
                code="INVALID_FILE",
            )
