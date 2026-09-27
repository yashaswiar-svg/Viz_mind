import pytest
from app.services.insight_validator import InsightValidator, InsightValidationError


def test_validator_valid_output():
    validator = InsightValidator()
    valid_output = {
        "title": "Sales and Spend Correlation",
        "summary": "A positive relationship was observed between sales and advertising spend.",
        "explanation": "Statistical evaluation showed a correlation coefficient of 0.85.",
        "claims": [
            {
                "claim_id": "CLAIM_001",
                "claim_text": "Sales and advertising spend show a positive relationship.",
                "evidence_ids": ["EVID_001"],
            }
        ],
        "limitations": ["Correlation does not establish causation."],
    }

    assert validator.validate_llm_output(valid_output, ["EVID_001", "EVID_002"], "CORRELATION") is True


def test_validator_invalid_evidence_id():
    validator = InsightValidator()
    invalid_output = {
        "title": "Sales Correlation",
        "summary": "Relationship observed.",
        "explanation": "Correlation calculated.",
        "claims": [
            {
                "claim_id": "CLAIM_001",
                "claim_text": "Sales correlated with spend.",
                "evidence_ids": ["EVID_999"],  # Invalid evidence ID!
            }
        ],
    }

    with pytest.raises(InsightValidationError, match="invalid or unsupplied evidence ID"):
        validator.validate_llm_output(invalid_output, ["EVID_001"], "CORRELATION")


def test_validator_causality_rejection():
    validator = InsightValidator()
    causal_output = {
        "title": "Sales Correlation",
        "summary": "Advertising spend caused sales to increase.",  # Forbidden word 'caused'!
        "explanation": "Statistical correlation proves advertising drives sales.",
        "claims": [
            {
                "claim_id": "CLAIM_001",
                "claim_text": "Spend caused sales increase.",
                "evidence_ids": ["EVID_001"],
            }
        ],
    }

    with pytest.raises(InsightValidationError, match="forbidden causality claim pattern"):
        validator.validate_llm_output(causal_output, ["EVID_001"], "CORRELATION")


def test_validator_future_certainty_rejection():
    validator = InsightValidator()
    future_output = {
        "title": "Sales Prediction",
        "summary": "Sales will definitely increase next quarter.",  # Forbidden word 'will definitely'!
        "explanation": "Model predictions guarantee an outcome.",
        "claims": [
            {
                "claim_id": "CLAIM_001",
                "claim_text": "Sales will definitely rise.",
                "evidence_ids": ["EVID_001"],
            }
        ],
    }

    with pytest.raises(InsightValidationError, match="forbidden future certainty pattern"):
        validator.validate_llm_output(future_output, ["EVID_001"], "PREDICTION")
