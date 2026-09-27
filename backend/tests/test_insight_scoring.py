import pytest
from app.services.insight_evidence import EvidenceItem
from app.services.insight_scoring import InsightScoringEngine


def test_insight_scoring_correlation():
    engine = InsightScoringEngine()

    strong_evid = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE6_PATTERN",
        source_type="CORRELATION",
        columns=["sales", "spend"],
        metrics={"correlation": 0.88, "p_value": 0.001},
        description="Strong correlation",
    )

    score, imp_level, ev_strength = engine.compute_candidate_score("CORRELATION", [strong_evid])

    assert 80.0 <= score <= 100.0
    assert imp_level == "HIGH"
    assert ev_strength == "STRONG"


def test_insight_scoring_anomaly():
    engine = InsightScoringEngine()

    high_anom = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE7_ANOMALY",
        source_type="ANOMALY",
        columns=["revenue"],
        metrics={"anomaly_score": 92.0, "severity": "HIGH"},
        description="High anomaly",
    )

    score, imp_level, ev_strength = engine.compute_candidate_score("ANOMALY", [high_anom])

    assert score >= 80.0
    assert imp_level == "HIGH"
    assert ev_strength == "STRONG"


def test_insight_scoring_bounds():
    engine = InsightScoringEngine()
    weak_evid = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE6_PATTERN",
        source_type="CORRELATION",
        columns=["a", "b"],
        metrics={"correlation": 0.1, "p_value": 0.2},
        description="Weak correlation",
    )

    score, imp_level, ev_strength = engine.compute_candidate_score("CORRELATION", [weak_evid])

    assert 0.0 <= score <= 100.0
    assert imp_level == "LOW"
    assert ev_strength == "WEAK"
