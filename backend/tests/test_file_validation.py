from pathlib import Path
import pytest
from app.core.exceptions import FileValidationException
from app.services.file_validation_service import FileValidationService


def test_validate_filename_safety_valid():
    filename = FileValidationService.validate_filename_safety("sales_data_2026.csv")
    assert filename == "sales_data_2026.csv"


def test_validate_filename_safety_path_traversal():
    with pytest.raises(FileValidationException) as exc_info:
        FileValidationService.validate_filename_safety("../../etc/passwd.csv")
    assert exc_info.value.code == "INVALID_FILENAME"

    with pytest.raises(FileValidationException) as exc_info:
        FileValidationService.validate_filename_safety("..\\..\\windows\\system32.csv")
    assert exc_info.value.code == "INVALID_FILENAME"


def test_validate_extension_allowed():
    assert FileValidationService.validate_extension("data.csv") == "csv"
    assert FileValidationService.validate_extension("report.xlsx") == "xlsx"
    assert FileValidationService.validate_extension("legacy.xls") == "xls"


def test_validate_extension_unsupported():
    for invalid in ["data.pdf", "script.exe", "file.json", "archive.zip", "page.html"]:
        with pytest.raises(FileValidationException) as exc_info:
            FileValidationService.validate_extension(invalid)
        assert exc_info.value.code == "UNSUPPORTED_FILE_TYPE"


def test_validate_size_empty_file():
    with pytest.raises(FileValidationException) as exc_info:
        FileValidationService.validate_size(0)
    assert exc_info.value.code == "EMPTY_FILE"


def test_validate_size_oversized():
    fifty_one_mb = 51 * 1024 * 1024
    with pytest.raises(FileValidationException) as exc_info:
        FileValidationService.validate_size(fifty_one_mb)
    assert exc_info.value.code == "FILE_TOO_LARGE"


def test_validate_path_safety():
    base = Path("/app/storage/datasets").resolve()
    safe_child = (base / "uuid-123" / "dataset_123.csv").resolve()

    # Should pass without exception
    FileValidationService.validate_path_safety(base, safe_child)

    # Path traversal outside base
    unsafe_target = Path("/app/storage/../etc/passwd").resolve()
    with pytest.raises(FileValidationException) as exc_info:
        FileValidationService.validate_path_safety(base, unsafe_target)
    assert exc_info.value.code == "INVALID_FILENAME"
