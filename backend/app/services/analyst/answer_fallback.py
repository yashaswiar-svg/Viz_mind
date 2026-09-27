from typing import Any, Dict
from app.services.analyst.query_plan import OperationType, QueryResult


class AnswerFallback:
    """Generates deterministic, structured natural-language answers directly from QueryResult."""

    def generate_fallback(self, question: str, query_result: QueryResult) -> Dict[str, Any]:
        if not query_result.success:
            return {
                "answer": f"I was unable to complete your query: {query_result.summary_text}",
                "key_points": [query_result.error_message or "Execution failed"],
                "evidence_ids": [],
                "limitations": ["Query execution failed or returned no data."],
            }

        op = query_result.operation
        summary = query_result.summary_text
        key_points = []

        if query_result.metrics:
            for k, v in query_result.metrics.items():
                key_points.append(f"{k.replace('_', ' ').title()}: {v}")

        if not key_points and query_result.data:
            first_row = query_result.data[0]
            for k, v in list(first_row.items())[:3]:
                key_points.append(f"{k}: {v}")

        limitations = []
        if query_result.truncated:
            limitations.append("Query result exceeded 1 MB byte limit and was truncated.")

        answer_text = f"Based on computed dataset analysis: {summary}"

        return {
            "answer": answer_text,
            "key_points": key_points,
            "evidence_ids": ["EV-1"],
            "limitations": limitations,
            "generation_mode": "DETERMINISTIC_FALLBACK",
        }
