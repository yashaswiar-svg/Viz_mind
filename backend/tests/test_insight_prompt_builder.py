import pytest
from app.services.insight_evidence import EvidenceItem
from app.services.insight_candidate_generator import InsightCandidate
from app.services.insight_prompt_builder import InsightPromptBuilder


def test_prompt_builder_structure():
    builder = InsightPromptBuilder()
    sys_inst = builder.build_system_instruction()

    assert "GROUNDING ONLY" in sys_inst
    assert "NO STATISTICAL CALCULATIONS" in sys_inst
    assert "NO RAW DATA" in sys_inst
    assert "NO CAUSALITY CLAIMS" in sys_inst
    assert "NO FUTURE CERTAINTY" in sys_inst
    assert "MANDATORY EVIDENCE CITATIONS" in sys_inst

    cand = InsightCandidate(
        candidate_id="CAND_001",
        insight_type="CORRELATION",
        title_template="Correlation Analysis for sales, spend",
        target_columns=["sales", "spend"],
        evidence_ids=["EVID_001"],
        evidence_items=[
            EvidenceItem(
                evidence_id="EVID_001",
                source_phase="PHASE6_PATTERN",
                source_type="CORRELATION",
                columns=["sales", "spend"],
                metrics={"correlation": 0.85},
                description="Strong correlation between sales and spend.",
            )
        ],
    )

    prompt, schema = builder.build_user_prompt(cand)
    assert "CAND_001" in prompt
    assert "EVID_001" in prompt
    assert "sales" in prompt
    assert "spend" in prompt
    assert "title" in schema
    assert "claims" in schema
