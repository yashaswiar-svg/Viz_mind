import pytest
from app.services.insight_evidence import EvidenceItem
from app.services.insight_candidate_generator import InsightCandidateGenerator
from app.services.insight_scoring import InsightScoringEngine
from app.services.insight_fallback import InsightFallbackEngine


def test_insight_mock_determinism():
    evid = EvidenceItem(
        evidence_id="EVID_001",
        source_phase="PHASE6_PATTERN",
        source_type="CORRELATION",
        columns=["sales", "budget"],
        metrics={"correlation": 0.85},
        description="Correlation between sales and budget.",
    )

    gen = InsightCandidateGenerator()
    cands1 = gen.generate_candidates([evid])
    cands2 = gen.generate_candidates([evid])

    assert len(cands1) == len(cands2)
    assert cands1[0].candidate_id == cands2[0].candidate_id
    assert cands1[0].insight_type == cands2[0].insight_type

    scoring = InsightScoringEngine()
    score1, level1, str1 = scoring.compute_candidate_score("CORRELATION", [evid])
    score2, level2, str2 = scoring.compute_candidate_score("CORRELATION", [evid])

    assert score1 == score2
    assert level1 == level2
    assert str1 == str2

    fallback = InsightFallbackEngine()
    res1 = fallback.generate_fallback_insight(cands1[0])
    res2 = fallback.generate_fallback_insight(cands2[0])

    assert res1["title"] == res2["title"]
    assert res1["summary"] == res2["summary"]
    assert res1["explanation"] == res2["explanation"]
