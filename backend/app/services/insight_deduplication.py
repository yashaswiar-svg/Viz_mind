import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class InsightDeduplicationEngine:
    """Deduplicates insight candidates or outputs using semantic fingerprint keys."""

    def deduplicate_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates a list of insight output objects.
        Returns deduplicated insights ordered by importance_score descending.
        """
        seen_fingerprints: Set[str] = set()
        unique_insights: List[Dict[str, Any]] = []

        # Sort by importance score descending if available
        sorted_insights = sorted(
            insights,
            key=lambda x: x.get("importance_score", 0.0),
            reverse=True,
        )

        for ins in sorted_insights:
            fp = self.create_fingerprint(
                insight_type=ins.get("insight_type", ""),
                columns=ins.get("columns", []),
                evidence_ids=[e.get("evidence_id") for e in ins.get("evidence_items", []) if isinstance(e, dict)],
            )
            if fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                unique_insights.append(ins)
            else:
                logger.debug(f"Filtered out duplicate insight with fingerprint: {fp}")

        return unique_insights

    @staticmethod
    def create_fingerprint(insight_type: str, columns: List[str], evidence_ids: List[str]) -> str:
        sorted_cols = "_".join(sorted(str(c).lower() for c in columns))
        sorted_eids = "_".join(sorted(str(e) for e in evidence_ids if e))
        return f"{insight_type}:{sorted_cols}:{sorted_eids}"
