import pytest
from app.services.insight_evidence import EvidenceItem


def test_evidence_item_contract():
    item = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE6_PATTERN",
        source_type="CORRELATION",
        source_id="123",
        columns=["sales", "spend"],
        metrics={"correlation": 0.85, "p_value": 0.001},
        description="Strong positive correlation between sales and spend.",
        strength_metadata={"score": 85.0},
    )

    assert item.evidence_id == "EVID_001"
    assert item.source_phase == "PHASE6_PATTERN"
    assert item.columns == ["sales", "spend"]
    assert item.metrics["correlation"] == 0.85

    d = item.to_dict()
    assert isinstance(d, dict)
    assert d["evidence_id"] == "EVID_001"
    assert d["source_type"] == "CORRELATION"
