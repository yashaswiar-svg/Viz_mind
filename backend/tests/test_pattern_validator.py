import pytest
from app.core.exceptions import PatternVersionMismatchException
from app.services.pattern_validator import PatternValidator


def test_validator_matching_checksum():
    validator = PatternValidator()
    # No exception raised for matching checksum
    validator.validate_dataset_version("ds1", "proc1", "checksumA", "checksumA")


def test_validator_mismatching_checksum():
    validator = PatternValidator()
    with pytest.raises(PatternVersionMismatchException):
        validator.validate_dataset_version("ds1", "proc1", "expected_checksum", "differing_checksum")


def test_validator_pattern_result_sanity():
    validator = PatternValidator()
    valid_res = {
        "pattern_type": "CORRELATION",
        "raw_p_value": 0.01,
        "adjusted_p_value": 0.02,
        "statistics": {"correlation": 0.75},
    }
    assert validator.validate_pattern_result(valid_res) is True

    invalid_res = {
        "pattern_type": "INVALID_TYPE",
        "raw_p_value": float("nan"),
        "statistics": {},
    }
    assert validator.validate_pattern_result(invalid_res) is False
