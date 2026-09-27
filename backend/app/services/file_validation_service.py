import io
import os
from pathlib import Path
from typing import Tuple
from fastapi import status
from app.core.config import settings
from app.core.exceptions import FileValidationException

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


class FileValidationService:
    """Service handling file extension, size limit, path traversal, and basic structural validation."""

    @staticmethod
    def validate_filename_safety(original_filename: str) -> str:
        if not original_filename or not original_filename.strip():
            raise FileValidationException("Filename is required.", code="INVALID_FILENAME")

        # Check for explicit path traversal signatures
        if ".." in original_filename or "/" in original_filename or "\\" in original_filename:
            raise FileValidationException(
                "Filename contains invalid path characters.",
                code="INVALID_FILENAME",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        sanitized = os.path.basename(original_filename.strip())
        return sanitized

    @staticmethod
    def validate_extension(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise FileValidationException(
                "Unsupported file type. Only CSV (.csv) and Excel (.xlsx, .xls) files are supported.",
                code="UNSUPPORTED_FILE_TYPE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # Normalize file_type string: csv, xlsx, xls
        return ext.lstrip(".")

    @staticmethod
    def validate_size(file_size: int) -> None:
        if file_size == 0:
            raise FileValidationException(
                "The uploaded file is empty (0 bytes).",
                code="EMPTY_FILE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if file_size > settings.max_upload_size_bytes:
            raise FileValidationException(
                f"The uploaded file exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
                code="FILE_TOO_LARGE",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def validate_path_safety(base_dir: Path, target_path: Path) -> None:
        resolved_base = base_dir.resolve()
        resolved_target = target_path.resolve()

        try:
            resolved_target.relative_to(resolved_base)
        except ValueError:
            raise FileValidationException(
                "Security violation: path traversal detected.",
                code="INVALID_FILENAME",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def validate_structure(file_content: bytes, file_type: str) -> None:
        """Performs basic structural/readability validation without dataset profiling."""
        if file_type == "csv":
            try:
                # Try decoding sample as text
                text_sample = file_content[:4096].decode("utf-8", errors="replace")
                if "\0" in text_sample:
                    raise FileValidationException(
                        "CSV file appears to be a binary file.",
                        code="INVALID_FILE",
                    )
            except Exception as e:
                raise FileValidationException(f"Invalid CSV file encoding: {str(e)}", code="INVALID_FILE")

        elif file_type == "xlsx":
            try:
                import openpyxl

                wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
                wb.close()
            except Exception as e:
                raise FileValidationException(
                    f"Corrupted or invalid Excel (.xlsx) workbook: {str(e)}",
                    code="INVALID_FILE",
                )

        elif file_type == "xls":
            try:
                import xlrd

                wb = xlrd.open_workbook(file_contents=file_content)
            except Exception as e:
                raise FileValidationException(
                    f"Corrupted or invalid Excel (.xls) workbook: {str(e)}",
                    code="INVALID_FILE",
                )
