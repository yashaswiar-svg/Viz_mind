import logging
from typing import Any, Dict, List
from app.services.insight_candidate_generator import InsightCandidate

logger = logging.getLogger(__name__)


class InsightFallbackEngine:
    """Generates deterministic, template-driven explanations from evidence metrics when LLM is unavailable or invalid."""

    def generate_fallback_insight(self, candidate: InsightCandidate) -> Dict[str, Any]:
        """
        Generates fallback output structured according to the standard insight output schema.
        """
        itype = candidate.insight_type
        evids = candidate.evidence_ids
        cols = candidate.target_columns
        col_str = ", ".join(cols) if cols else "the dataset"
        items = candidate.evidence_items

        title = candidate.title_template
        summary = ""
        explanation = ""
        claims: List[Dict[str, Any]] = []
        limitations: List[str] = []

        if itype == "DATA_QUALITY":
            summary = f"Data quality analysis for {col_str} identified key profile characteristics and metrics."
            explanation = (
                f"The Phase 3 Data Profiling engine evaluated the structure and cleanliness of {col_str}. "
                f"The analysis recorded the following evidence summary: {items[0].description if items else 'Quality bounds verified.'}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Data quality metrics for {col_str} were established by statistical profiling.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Profile quality metrics reflect structural integrity and null counts, not domain accuracy.")

        elif itype == "CORRELATION":
            r_val = items[0].metrics.get("statistics", {}).get("correlation", items[0].metrics.get("correlation", "N/A")) if items else "N/A"
            summary = f"A statistical relationship was detected between {col_str} (correlation value: {r_val})."
            explanation = (
                f"Phase 6 Pattern Discovery evaluated the bivariate relationship between {col_str}. "
                f"The computed correlation metric is {r_val}. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"A statistically evaluated correlation exists between {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Correlation does not establish causation.")

        elif itype in ("GROUP_DIFFERENCE", "CATEGORICAL_ASSOCIATION"):
            summary = f"A statistical group relationship was identified across {col_str}."
            explanation = (
                f"Phase 6 Pattern Discovery evaluated categorical associations/differences across {col_str}. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Statistical testing identified significant pattern differences across {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Group differences describe historical sample distributions and do not prove underlying mechanisms.")

        elif itype == "TREND":
            summary = f"A historical trend pattern was identified for {col_str}."
            explanation = (
                f"Phase 6 Pattern Discovery evaluated temporal and sequential variations in {col_str}. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Historical sequential data displays a measurable trend pattern in {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Historical trends reflect past observed patterns and are not guarantees of future outcomes.")

        elif itype == "DISTRIBUTION":
            summary = f"Statistical distribution characteristics were profiled for {col_str}."
            explanation = (
                f"Phase 6 Pattern Discovery profiled distribution moments and spread for {col_str}. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Distribution metrics characterize the variance and shape of {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Distribution profiles summarize historical observations.")

        elif itype == "ANOMALY":
            summary = f"Statistical outliers were detected in {col_str} using bounded IQR / Robust Z-score algorithms."
            explanation = (
                f"Phase 7 Anomaly Detection engine evaluated observations against statistical dispersion bounds. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Outlier detection identified statistically unusual values in {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Anomalies represent statistical unusualness and do not necessarily indicate data errors or business fraud.")

        elif itype in ("PREDICTION", "FORECAST"):
            summary = f"Evaluation metrics were computed for a predictive model targeting '{col_str}' against naive baselines."
            explanation = (
                f"Phase 7 Prediction engine evaluated machine learning pipelines on a held-out test split for target '{col_str}'. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"The predictive model for target '{col_str}' was quantitatively evaluated on held-out test data.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Prediction models provide statistical estimates based on historical features and are not guaranteed outcomes.")

        elif itype == "VISUALIZATION":
            summary = f"A recommended visualization chart type was identified for {col_str}."
            explanation = (
                f"Phase 5 Visualization Intelligence identified appropriate chart types for presenting {col_str}. "
                f"{items[0].description if items else ''}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Chart recommendations highlight optimal graphical representations for {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Visualizations provide graphical summary views of analytical metrics.")

        else:  # CROSS_MODULE
            summary = f"Cross-module synthesis connected historical patterns and predictive evaluations for {col_str}."
            explanation = (
                f"Combining analytical outputs across Phase 6 Pattern Discovery and Phase 7 Prediction engine: "
                f"{' '.join([item.description for item in items])}"
            )
            claims.append(
                {
                    "claim_id": "CLAIM_001",
                    "claim_text": f"Integrated analytical evidence connects pattern discoveries with model evaluations for {col_str}.",
                    "evidence_ids": evids,
                }
            )
            limitations.append("Cross-module synthesis combines distinct analytical evaluations; correlation does not imply causation.")

        return {
            "title": title,
            "summary": summary,
            "explanation": explanation,
            "claims": claims,
            "limitations": limitations,
        }
