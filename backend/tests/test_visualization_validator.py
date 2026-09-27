import pytest
from app.services.visualization_validator import VisualizationValidator, VisualizationValidationError


def test_validate_aggregation_allowed():
    validator = VisualizationValidator()
    assert validator.validate_aggregation("sum") == "sum"
    assert validator.validate_aggregation("MEAN") == "mean"
    assert validator.validate_aggregation("median") == "median"


def test_validate_aggregation_invalid():
    validator = VisualizationValidator()
    with pytest.raises(VisualizationValidationError) as exc:
        validator.validate_aggregation("eval(import os)")
    assert exc.value.code == "INVALID_AGGREGATION_FUNCTION"


def test_validate_dataset_version_mismatch():
    validator = VisualizationValidator()
    with pytest.raises(VisualizationValidationError) as exc:
        validator.validate_dataset_version(
            source_dataset_id="source-123",
            processed_dataset_id="proc-456",
            expected_checksum="sha256-abc",
            actual_checksum="sha256-xyz",
        )
    assert exc.value.code == "VISUALIZATION_DATASET_VERSION_MISMATCH"
