import pytest
from app.services.insight_evidence_service import InsightVersionMismatchError


def test_insight_version_mismatch_exception():
    err = InsightVersionMismatchError("Checksum mismatch detected for processed dataset.")
    assert "Checksum mismatch" in str(err)
