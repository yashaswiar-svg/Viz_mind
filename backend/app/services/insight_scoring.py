import math
from typing import Any, Dict, List, Tuple
from app.services.insight_evidence import EvidenceItem


class InsightScoringEngine:
    """Computes transparent, bounded 0-100 importance scores and evidence strength ratings."""

    def compute_candidate_score(
        self, insight_type: str, evidence_items: List[EvidenceItem]
    ) -> Tuple[float, str, str]:
        """
        Returns (importance_score 0-100, importance_level 'HIGH'/'MEDIUM'/'LOW', evidence_strength 'STRONG'/'MODERATE'/'WEAK').
        """
        if not evidence_items:
            return 30.0, "LOW", "WEAK"

        score = 50.0

        if insight_type == "CORRELATION":
            score = self._score_correlation(evidence_items)
        elif insight_type in ("GROUP_DIFFERENCE", "CATEGORICAL_ASSOCIATION", "TREND", "DISTRIBUTION"):
            score = self._score_pattern(evidence_items)
        elif insight_type == "ANOMALY":
            score = self._score_anomaly(evidence_items)
        elif insight_type in ("PREDICTION", "FORECAST"):
            score = self._score_prediction(evidence_items)
        elif insight_type == "DATA_QUALITY":
            score = self._score_data_quality(evidence_items)
        elif insight_type == "VISUALIZATION":
            score = self._score_visualization(evidence_items)
        elif insight_type == "CROSS_MODULE":
            score = self._score_cross_module(evidence_items)
        else:
            score = 50.0

        # Bound score between 0 and 100
        score = max(0.0, min(100.0, round(score, 1)))

        # Derive Importance Level
        if score >= 70.0:
            importance_level = "HIGH"
        elif score >= 40.0:
            importance_level = "MEDIUM"
        else:
            importance_level = "LOW"

        # Derive Evidence Strength
        strength = self._derive_evidence_strength(score, insight_type, evidence_items)

        return score, importance_level, strength

    def _score_correlation(self, items: List[EvidenceItem]) -> float:
        scores = []
        for item in items:
            stats = item.metrics.get("statistics", {})
            r = abs(stats.get("correlation", item.metrics.get("correlation", 0.5)))
            p_val = stats.get("p_value", item.metrics.get("p_value", 0.05))

            # Base score = |r| * 100
            s = r * 100.0
            if p_val > 0.05:
                s *= 0.5  # penalty for non-significant correlation
            scores.append(s)
        return max(scores) if scores else 50.0

    def _score_pattern(self, items: List[EvidenceItem]) -> float:
        scores = []
        for item in items:
            s = item.metrics.get("score", item.strength_metadata.get("score", 50.0))
            scores.append(float(s))
        return max(scores) if scores else 50.0

    def _score_anomaly(self, items: List[EvidenceItem]) -> float:
        scores = []
        for item in items:
            if item.source_type == "ANOMALY_SUMMARY":
                pct = item.metrics.get("anomaly_percentage", 0.0)
                # higher percentage or unusual count -> higher score
                s = min(100.0, pct * 10.0 + 40.0)
            else:
                s = item.metrics.get("anomaly_score", 50.0)
                sev = item.metrics.get("severity", "MEDIUM")
                if sev == "HIGH":
                    s = max(s, 80.0)
                elif sev == "MEDIUM":
                    s = max(s, 50.0)
            scores.append(float(s))
        return max(scores) if scores else 50.0

    def _score_prediction(self, items: List[EvidenceItem]) -> float:
        scores = []
        for item in items:
            metrics = item.metrics.get("metrics", {})
            baseline = item.metrics.get("baseline_metrics", {})
            ptype = item.metrics.get("problem_type", "REGRESSION")

            if ptype == "REGRESSION":
                r2 = metrics.get("r2", 0.0)
                base_r2 = baseline.get("r2", 0.0)
                imp = r2 - base_r2
                s = max(0.0, r2) * 80.0 + max(0.0, imp) * 20.0
            elif ptype == "CLASSIFICATION":
                acc = metrics.get("accuracy", 0.5)
                f1 = metrics.get("f1", acc)
                s = f1 * 100.0
            else:  # FORECASTING
                mae = metrics.get("mae", 1.0)
                base_mae = baseline.get("mae", 1.0)
                if base_mae > 0:
                    rel_imp = max(0.0, (base_mae - mae) / base_mae)
                    s = min(100.0, rel_imp * 100.0 + 40.0)
                else:
                    s = 50.0
            scores.append(s)
        return max(scores) if scores else 50.0

    def _score_data_quality(self, items: List[EvidenceItem]) -> float:
        scores = []
        for item in items:
            if "overall_quality_score" in item.metrics:
                q_score = item.metrics["overall_quality_score"]
                # Impact is high if quality is poor (< 70) or exceptionally high (> 95)
                if q_score < 70:
                    s = 100.0 - q_score
                else:
                    s = q_score * 0.5
            else:
                missing_pct = item.metrics.get("missing_percentage", 0.0)
                s = min(100.0, missing_pct * 2.0 + 30.0)
            scores.append(float(s))
        return max(scores) if scores else 50.0

    def _score_visualization(self, items: List[EvidenceItem]) -> float:
        scores = [item.metrics.get("relevance_score", 50.0) for item in items]
        return max(scores) if scores else 50.0

    def _score_cross_module(self, items: List[EvidenceItem]) -> float:
        sub_scores = []
        for item in items:
            if item.source_phase == "PHASE6_PATTERN":
                sub_scores.append(self._score_pattern([item]))
            elif item.source_phase == "PHASE7_PREDICTION":
                sub_scores.append(self._score_prediction([item]))
            elif item.source_phase == "PHASE7_ANOMALY":
                sub_scores.append(self._score_anomaly([item]))
            else:
                sub_scores.append(50.0)
        base = sum(sub_scores) / max(1, len(sub_scores))
        return min(100.0, base + 15.0)  # Cross-module synthesis bonus

    def _derive_evidence_strength(
        self, score: float, insight_type: str, items: List[EvidenceItem]
    ) -> str:
        if score >= 75.0:
            return "STRONG"
        elif score >= 45.0:
            return "MODERATE"
        else:
            return "WEAK"
