from typing import Any, Dict, List
from app.services.analyst.query_plan import QueryResult


class EvidenceBuilder:
    """Formats QueryResult objects into evidence payloads with source references."""

    def build_evidence(self, query_result: QueryResult) -> Dict[str, Any]:
        source_ref = {
            "source_type": query_result.source_type,
            "execution_path": query_result.execution_path,
            "operation": query_result.operation.value if hasattr(query_result.operation, "value") else str(query_result.operation),
            "row_count": query_result.row_count,
            "metrics": query_result.metrics,
        }

        evidence_items: List[Dict[str, Any]] = []
        for idx, row in enumerate(query_result.data[:20]):
            evidence_items.append({
                "id": f"EV-{idx+1}",
                "content": row,
                "source": query_result.source_type,
            })

        return {
            "summary_text": query_result.summary_text,
            "source_references": [source_ref],
            "evidence_items": evidence_items,
            "metrics": query_result.metrics,
            "data_sample": query_result.data[:10],
            "truncated": query_result.truncated,
        }
