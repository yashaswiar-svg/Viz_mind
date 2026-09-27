import pytest
from app.services.insight_evidence import EvidenceItem
from app.services.insight_candidate_generator import InsightCandidate
from app.services.insight_fallback import InsightFallbackEngine


def test_fallback_all_insight_types():
    engine = InsightFallbackEngine()

    types = [
        "DATA_QUALITY",
        "CORRELATION",
        "GROUP_DIFFERENCE",
        "CATEGORICAL_ASSOCIATION",
        "TREND",
        "DISTRIBUTION",
        "ANOMALY",
        "PREDICTION",
        "FORECAST",
        "VISUALIZATION",
        "CROSS_MODULE",
    ]

    for itype in types:
        cand = InsightCandidate(
            candidate_id="CAND_001",
            insight_type=itype,
            title_template=f"Test {itype} Template",
            target_columns=["sales"],
            evidence_ids=["EVID_001"],
            evidence_items=[
                EvidenceItem(
                    evidence_id="EVID_001",
                    source_phase="PHASE6_PATTERN",
                    source_type=itype,
                    columns=["sales"],
                    metrics={"score": 80.0},
                    description=f"Fallback evidence description for {itype}.",
                )
            ],
        )

        res = engine.generate_fallback_insight(cand)

        assert isinstance(res, dict)
        assert "title" in res
        assert "summary" in res
        assert "explanation" in res
        assert "claims" in res
        assert len(res["claims"]) > 0
        assert "EVID_001" in res["claims"][0]["evidence_ids"]
        assert len(res["limitations"]) > 0
