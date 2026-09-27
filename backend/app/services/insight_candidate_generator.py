import logging
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.insight_evidence import EvidenceItem

logger = logging.getLogger(__name__)


class InsightCandidate(BaseModel):
    """Candidate insight structure generated deterministically from evidence before LLM processing."""

    candidate_id: str
    insight_type: str
    title_template: str
    target_columns: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    candidate_metrics: Dict[str, Any] = Field(default_factory=dict)


class InsightCandidateGenerator:
    """Generates candidate insights deterministically using evidence combination rules."""

    def generate_candidates(self, evidence_items: List[EvidenceItem]) -> List[InsightCandidate]:
        """
        Processes evidence items and generates candidate insights.
        Returns a bounded list of InsightCandidate instances (max MAX_INSIGHT_CANDIDATES = 30).
        """
        candidates: List[InsightCandidate] = []
        c_counter = 1

        def next_cand_id() -> str:
            nonlocal c_counter
            cid = f"CAND_{c_counter:03d}"
            c_counter += 1
            return cid

        # Map evidence items by ID and phase/type
        evid_by_phase: Dict[str, List[EvidenceItem]] = {}
        for item in evidence_items:
            evid_by_phase.setdefault(item.source_phase, []).append(item)

        # 1. DATA_QUALITY Candidates
        for item in evid_by_phase.get("PHASE3_PROFILE", []):
            if item.source_type == "DATA_QUALITY":
                candidates.append(
                    InsightCandidate(
                        candidate_id=next_cand_id(),
                        insight_type="DATA_QUALITY",
                        title_template=f"Data Quality Analysis for {', '.join(item.columns) if item.columns else 'Dataset'}",
                        target_columns=item.columns,
                        evidence_ids=[item.evidence_id],
                        evidence_items=[item],
                        candidate_metrics=item.metrics,
                    )
                )

        # 2. Phase 6 Pattern Candidates (CORRELATION, GROUP_DIFFERENCE, CATEGORICAL_ASSOCIATION, TREND, DISTRIBUTION)
        pattern_items = evid_by_phase.get("PHASE6_PATTERN", [])
        for item in pattern_items:
            ptype = item.source_type
            valid_types = {
                "CORRELATION": "CORRELATION",
                "GROUP_DIFFERENCE": "GROUP_DIFFERENCE",
                "CATEGORICAL_ASSOCIATION": "CATEGORICAL_ASSOCIATION",
                "TREND": "TREND",
                "DISTRIBUTION": "DISTRIBUTION",
            }
            itype = valid_types.get(ptype, "CORRELATION")
            candidates.append(
                InsightCandidate(
                    candidate_id=next_cand_id(),
                    insight_type=itype,
                    title_template=f"{itype.replace('_', ' ').title()} Pattern in {', '.join(item.columns)}",
                    target_columns=item.columns,
                    evidence_ids=[item.evidence_id],
                    evidence_items=[item],
                    candidate_metrics=item.metrics,
                )
            )

        # 3. Phase 7 Anomaly Candidates
        anomaly_items = evid_by_phase.get("PHASE7_ANOMALY", [])
        # Summary anomaly candidate
        summary_anom = [i for i in anomaly_items if i.source_type == "ANOMALY_SUMMARY"]
        if summary_anom:
            s_item = summary_anom[0]
            candidates.append(
                InsightCandidate(
                    candidate_id=next_cand_id(),
                    insight_type="ANOMALY",
                    title_template="Overall Dataset Outlier Overview",
                    target_columns=[],
                    evidence_ids=[s_item.evidence_id],
                    evidence_items=[s_item],
                    candidate_metrics=s_item.metrics,
                )
            )
        # Detailed anomaly candidates
        for item in anomaly_items:
            if item.source_type == "ANOMALY":
                candidates.append(
                    InsightCandidate(
                        candidate_id=next_cand_id(),
                        insight_type="ANOMALY",
                        title_template=f"Statistical Outliers Detected in {', '.join(item.columns)}",
                        target_columns=item.columns,
                        evidence_ids=[item.evidence_id],
                        evidence_items=[item],
                        candidate_metrics=item.metrics,
                    )
                )

        # 4. Phase 7 Prediction Candidates
        pred_items = evid_by_phase.get("PHASE7_PREDICTION", [])
        for item in pred_items:
            ptype = item.metrics.get("problem_type", "REGRESSION")
            itype = "FORECAST" if ptype == "FORECASTING" else "PREDICTION"
            target_col = item.metrics.get("target_column", "")
            candidates.append(
                InsightCandidate(
                    candidate_id=next_cand_id(),
                    insight_type=itype,
                    title_template=f"{itype.title()} Model Evaluation for '{target_col}'",
                    target_columns=[target_col] if target_col else item.columns,
                    evidence_ids=[item.evidence_id],
                    evidence_items=[item],
                    candidate_metrics=item.metrics,
                )
            )

        # 5. Phase 5 Visualization Candidates
        viz_items = evid_by_phase.get("PHASE5_VISUALIZATION", [])
        for item in viz_items[:3]:
            candidates.append(
                InsightCandidate(
                    candidate_id=next_cand_id(),
                    insight_type="VISUALIZATION",
                    title_template=f"Key Chart Recommendation for {', '.join(item.columns)}",
                    target_columns=item.columns,
                    evidence_ids=[item.evidence_id],
                    evidence_items=[item],
                    candidate_metrics=item.metrics,
                )
            )

        # 6. CROSS_MODULE Candidates (e.g., Trend + Prediction for same target column)
        trend_items = [i for i in pattern_items if i.source_type == "TREND"]
        for t_item in trend_items:
            for p_item in pred_items:
                t_col = t_item.columns[0] if t_item.columns else ""
                p_target = p_item.metrics.get("target_column", "")
                if t_col and t_col == p_target:
                    candidates.append(
                        InsightCandidate(
                            candidate_id=next_cand_id(),
                            insight_type="CROSS_MODULE",
                            title_template=f"Historical Trend and Prediction Synthesis for '{t_col}'",
                            target_columns=[t_col],
                            evidence_ids=[t_item.evidence_id, p_item.evidence_id],
                            evidence_items=[t_item, p_item],
                            candidate_metrics={
                                "trend": t_item.metrics,
                                "prediction": p_item.metrics,
                            },
                        )
                    )

        # Truncate candidates to MAX_INSIGHT_CANDIDATES
        final_cands = candidates[: settings.MAX_INSIGHT_CANDIDATES]
        logger.info(f"Generated {len(final_cands)} insight candidates from {len(evidence_items)} evidence items.")
        return final_cands
