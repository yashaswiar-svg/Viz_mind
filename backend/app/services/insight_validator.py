import re
import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class InsightValidationError(Exception):
    """Raised when LLM generated insight fails strict output validation rules."""
    pass


class InsightValidator:
    """Validates structured LLM outputs against schema, evidence grounding, anti-causality, and anti-future certainty rules."""

    FORBIDDEN_CAUSALITY_PATTERNS = [
        r"\bcaused\b",
        r"\bcauses\b",
        r"\bled to\b",
        r"\bleads to\b",
        r"\bbecause of\b",
        r"\bdrives\b",
        r"\bdriving\b",
    ]

    FORBIDDEN_FUTURE_CERTAINTY_PATTERNS = [
        r"\bwill definitely\b",
        r"\bguaranteed\b",
        r"\bcertainly will\b",
        r"\b100% certain\b",
        r"\bproven fact\b",
    ]

    def validate_llm_output(
        self,
        output: Dict[str, Any],
        candidate_evidence_ids: List[str],
        insight_type: str,
    ) -> bool:
        """
        Validates LLM output dictionary. Raises InsightValidationError if invalid.
        Returns True if valid.
        """
        # Stage 1: JSON Schema structure check
        if not isinstance(output, dict):
            raise InsightValidationError("LLM output is not a dictionary.")

        for required_field in ("title", "summary", "explanation", "claims"):
            if required_field not in output or not output[required_field]:
                raise InsightValidationError(f"Missing or empty required field '{required_field}'.")

        if not isinstance(output["claims"], list) or len(output["claims"]) == 0:
            raise InsightValidationError("Field 'claims' must be a non-empty list.")

        # Stage 2 & 3: Evidence ID citation & claim grounding
        valid_evid_set: Set[str] = set(candidate_evidence_ids)
        for idx, claim in enumerate(output["claims"]):
            if not isinstance(claim, dict):
                raise InsightValidationError(f"Claim at index {idx} is not a dictionary.")
            if "claim_text" not in claim or not claim["claim_text"]:
                raise InsightValidationError(f"Claim at index {idx} missing 'claim_text'.")
            eids = claim.get("evidence_ids", [])
            if not isinstance(eids, list) or len(eids) == 0:
                raise InsightValidationError(f"Claim at index {idx} ('{claim.get('claim_text')}') does not reference any evidence IDs.")
            for eid in eids:
                if eid not in valid_evid_set:
                    raise InsightValidationError(
                        f"Claim references invalid or unsupplied evidence ID '{eid}' (valid IDs: {sorted(list(valid_evid_set))})."
                    )

        # Combined text for prose pattern checks
        full_prose = f"{output.get('title', '')} {output.get('summary', '')} {output.get('explanation', '')}"

        # Stage 4: Anti-causality check (for non-causal types e.g. CORRELATION)
        if insight_type in ("CORRELATION", "CATEGORICAL_ASSOCIATION", "DISTRIBUTION", "TREND"):
            for pattern in self.FORBIDDEN_CAUSALITY_PATTERNS:
                if re.search(pattern, full_prose, re.IGNORECASE):
                    raise InsightValidationError(
                        f"Prose contains forbidden causality claim pattern '{pattern}' for insight type '{insight_type}'."
                    )

        # Stage 5: Anti-future certainty check
        for pattern in self.FORBIDDEN_FUTURE_CERTAINTY_PATTERNS:
            if re.search(pattern, full_prose, re.IGNORECASE):
                raise InsightValidationError(
                    f"Prose contains forbidden future certainty pattern '{pattern}'."
                )

        logger.debug(f"Insight output validated successfully for type '{insight_type}'.")
        return True
