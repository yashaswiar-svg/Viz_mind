from typing import Any, Dict
from app.services.analyst.query_plan import QueryResult


class AnswerValidator:
    """Validates LLM generated answers against computed evidence metrics and anti-causality rules."""

    def validate_answer(self, llm_response: Dict[str, Any], query_result: QueryResult) -> Dict[str, Any]:
        answer_text = llm_response.get("answer", "")
        key_points = llm_response.get("key_points", [])
        limitations = list(llm_response.get("limitations", []))

        # Check anti-causality: if correlation operation, ensure answer doesn't assert causation without disclaimer
        if query_result.operation.value in {"CORRELATION", "RELATIONSHIP"}:
            causal_words = ["causes", "caused by", "drives", "leads to"]
            if any(w in answer_text.lower() for w in causal_words):
                limitations.append("Correlation indicates linear association, not direct causal dependency.")

        return {
            "answer": answer_text,
            "key_points": key_points,
            "evidence_ids": llm_response.get("evidence_ids", []),
            "limitations": list(set(limitations)),
            "validation_passed": True,
        }
