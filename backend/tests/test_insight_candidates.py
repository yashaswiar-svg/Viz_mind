import pytest
from app.services.insight_evidence import EvidenceItem
from app.services.insight_candidate_generator import InsightCandidateGenerator


def test_candidate_generation_from_evidence():
    evid1 = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE3_PROFILE",
        source_type="DATA_QUALITY",
        columns=[],
        metrics={"overall_quality_score": 92.5},
        description="High data quality.",
    )
    evid2 = EvidenceItem(
        evidence_id="EVID_002",
        source_phase="PHASE6_PATTERN",
        source_type="CORRELATION",
        columns=["sales", "budget"],
        metrics={"correlation": 0.78},
        description="Correlation between sales and budget.",
    )
    evid3 = EvidenceItem(
        evidence_id="EVID_003",
        source_phase="PHASE7_ANOMALY",
        source_type="ANOMALY",
        columns=["revenue"],
        metrics={"anomaly_score": 88.0, "severity": "HIGH"},
        description="High severity anomaly in revenue.",
    )
    evid4 = EvidenceItem(
        evidence_id="EVID_004",
        source_phase="PHASE6_PATTERN",
        source_type="TREND",
        columns=["sales"],
        metrics={"trend": "increasing"},
        description="Increasing sales trend.",
    )
    evid5 = EvidenceItem(
        evidence_id="EVID_005",
        source_phase="PHASE7_PREDICTION",
        source_type="PREDICTION",
        columns=["sales"],
        metrics={"target_column": "sales", "problem_type": "REGRESSION"},
        description="Prediction model for sales.",
    )

    gen = InsightCandidateGenerator()
    candidates = gen.generate_candidates([evid1, evid2, evid3, evid4, evid5])

    assert len(candidates) >= 4
    types = [c.insight_type for c in candidates]
    assert "DATA_QUALITY" in types
    assert "CORRELATION" in types
    assert "ANOMALY" in types
    assert "PREDICTION" in types
    assert "CROSS_MODULE" in types  # Trend + Prediction cross module candidate!


def test_candidate_limits():
    gen = InsightCandidateGenerator()
    evids = [
        EvidenceItem(
            evidence_id=f"EVID_{i:03d}",
            source_phase="PHASE6_PATTERN",
            source_type="CORRELATION",
            columns=[f"col_{i}", "target"],
            metrics={"correlation": 0.5},
            description=f"Correlation {i}",
        )
        for i in range(50)
    ]
    candidates = gen.generate_candidates(evids)
    assert len(candidates) <= 30
