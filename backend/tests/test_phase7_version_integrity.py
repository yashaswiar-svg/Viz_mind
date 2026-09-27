import pytest
from app.services.dataset_loader import DatasetLoader
from app.core.exceptions import AnomalyVersionMismatchException, PredictionVersionMismatchException


def test_checksum_verification():
    loader = DatasetLoader()
    # Test checksum calculation consistency
    import tempfile
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
        tmp.write("col1,col2\n10,20\n30,40\n")
        tmp_path = tmp.name

    hash1 = loader.calculate_checksum(tmp_path)
    hash2 = loader.calculate_checksum(tmp_path)

    assert hash1 == hash2
    assert len(hash1) == 64
