import pytest
from app.services.insight_deduplication import InsightDeduplicationEngine


def test_deduplication_engine():
    engine = InsightDeduplicationEngine()

    insights = [
        {
            "insight_type": "CORRELATION",
            "columns": ["sales", "budget"],
            "importance_score": 85.0,
            "evidence_items": [{"evidence_id": "EVID_001"}],
        },
        {
            "insight_type": "CORRELATION",
            "columns": ["budget", "sales"],  # Same columns reversed
            "importance_score": 80.0,
            "evidence_items": [{"evidence_id": "EVID_001"}],
        },
        {
            "insight_type": "ANOMALY",
            "columns": ["revenue"],
            "importance_score": 90.0,
            "evidence_items": [{"evidence_id": "EVID_002"}],
        },
    ]

    deduped = engine.deduplicate_insights(insights)

    assert len(deduped) == 2
    types = [i["insight_type"] for i in deduped]
    assert "CORRELATION" in types
    assert "ANOMALY" in types
    # Higher score duplicate retained
    corr_insight = [i for i in deduped if i["insight_type"] == "CORRELATION"][0]
    assert corr_insight["importance_score"] == 85.0
