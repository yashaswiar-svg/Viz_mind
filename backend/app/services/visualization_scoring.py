import logging
from typing import Any, Dict, List
from app.services.visualization_planner import ChartCandidate, MAX_TOTAL_RECOMMENDATIONS

logger = logging.getLogger(__name__)


class VisualizationScoringEngine:
    """Evaluates 0-100 relevance score for chart candidates and ranks top recommendations."""

    def score_candidate(
        self,
        candidate: ChartCandidate,
        column_profiles_map: Dict[str, Dict[str, Any]],
        total_rows: int,
    ) -> float:
        score = candidate.base_score

        x_prof = column_profiles_map.get(candidate.x_column, {})
        y_prof = column_profiles_map.get(candidate.y_column, {}) if candidate.y_column else {}

        # 1. Missingness Penalty
        x_null_pct = (x_prof.get("null_count", 0) / total_rows * 100.0) if total_rows > 0 else 0.0
        y_null_pct = (y_prof.get("null_count", 0) / total_rows * 100.0) if y_prof and total_rows > 0 else 0.0
        score -= (x_null_pct * 0.3 + y_null_pct * 0.3)

        # 2. High Cardinality Penalty for Categorical Charts
        if candidate.chart_type in ("bar", "count_bar"):
            distinct_count = x_prof.get("distinct_count", 0)
            if distinct_count > 15:
                score -= (distinct_count - 15) * 1.5
            elif distinct_count <= 2:
                # Binary columns are slightly less interesting for big bar charts
                score -= 5.0

        # 3. Temporal Line Chart Boost
        if candidate.chart_type == "line":
            score += 10.0

        # 4. Semantic Aggregation Affinity Boost
        if candidate.y_column and candidate.aggregation:
            y_name = candidate.y_column.lower()
            if any(kw in y_name for kw in ["sales", "revenue", "amount", "total", "cost", "price", "profit"]):
                if candidate.aggregation == "sum":
                    score += 5.0
            elif candidate.aggregation == "mean":
                score += 3.0

        # 5. Scatter plot cardinality boost
        if candidate.chart_type == "scatter":
            x_distinct = x_prof.get("distinct_count", 0)
            y_distinct = y_prof.get("distinct_count", 0)
            if x_distinct > 20 and y_distinct > 20:
                score += 5.0

        # Clamp between 0.0 and 100.0
        clamped_score = max(0.0, min(100.0, round(score, 1)))
        candidate.base_score = clamped_score
        return clamped_score

    def score_and_rank_candidates(
        self,
        candidates: List[ChartCandidate],
        column_profiles: List[Dict[str, Any]],
        total_rows: int,
    ) -> List[ChartCandidate]:
        column_profiles_map = {cp.get("column_name", ""): cp for cp in column_profiles}

        for c in candidates:
            self.score_candidate(c, column_profiles_map, total_rows)

        # Sort descending by score
        sorted_candidates = sorted(candidates, key=lambda c: c.base_score, reverse=True)

        # Global hard cap limit of 12 recommendations
        final_candidates = sorted_candidates[:MAX_TOTAL_RECOMMENDATIONS]

        return final_candidates
