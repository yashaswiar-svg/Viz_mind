import logging
import math
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

MAX_TOTAL_PATTERNS = 30


class PatternScoringEngine:
    """Calculates deterministic relevance scores (0-100), template descriptions, deduplicates, and ranks pattern discovery results."""

    def calculate_score(self, item: Dict[str, Any]) -> float:
        pattern_type = item.get("pattern_type", "")
        stats = item.get("statistics", {})
        adj_p = item.get("adjusted_p_value")
        n = item.get("sample_size", 0)
        effect_size = item.get("effect_size")

        # 1. Effect strength component (0-40 points)
        effect_score = 0.0
        if pattern_type == "CORRELATION":
            abs_r = stats.get("absolute_correlation", 0.0)
            effect_score = abs_r * 40.0
        elif pattern_type == "GROUP_DIFFERENCE":
            eff_type = stats.get("effect_size_type")
            eff_val = effect_size or 0.0
            if eff_type == "cohens_d":
                effect_score = min(40.0, (eff_val / 1.5) * 40.0)
            else:  # eta_squared
                effect_score = min(40.0, (eff_val / 0.25) * 40.0)
        elif pattern_type == "CATEGORICAL_ASSOCIATION":
            cv = effect_size or 0.0
            effect_score = min(40.0, (cv / 0.50) * 40.0)
        elif pattern_type == "TIME_TREND":
            r2 = effect_size or 0.0
            effect_score = r2 * 40.0
        elif pattern_type == "DISTRIBUTION":
            effect_score = 20.0

        # 2. Statistical significance component (0-30 points)
        sig_score = 5.0
        if adj_p is not None:
            if adj_p < 0.001:
                sig_score = 30.0
            elif adj_p < 0.01:
                sig_score = 25.0
            elif adj_p < 0.05:
                sig_score = 20.0
            else:
                sig_score = 5.0

        # 3. Sample size reliability component (0-20 points)
        sample_score = 0.0
        if n > 0:
            sample_score = min(20.0, math.log10(n) * 6.66)

        # 4. Method reliability component (0-10 points)
        method_score = 10.0
        if pattern_type == "CATEGORICAL_ASSOCIATION":
            method_score = 8.0
        elif pattern_type == "DISTRIBUTION":
            method_score = 5.0

        total_score = min(100.0, effect_score + sig_score + sample_score + method_score)
        return round(total_score, 2)

    def generate_title_and_description(self, item: Dict[str, Any]) -> Tuple[str, str]:
        pattern_type = item.get("pattern_type", "")
        cols = item.get("columns", [])
        stats = item.get("statistics", {})
        strength = item.get("strength", "WEAK")
        method = item.get("method", "")
        adj_p = item.get("adjusted_p_value")
        p_str = f"p-adjusted = {adj_p:.4f}" if adj_p is not None else "p-adjusted N/A"

        if pattern_type == "CORRELATION":
            col1, col2 = cols[0], cols[1] if len(cols) > 1 else ""
            r_val = stats.get("correlation", 0.0)
            direction = stats.get("direction", "NONE").lower()
            title = f"{strength.title()} {direction.title()} Correlation between {col1} and {col2}"
            desc = (
                f"Statistical correlation (r = {r_val}, {p_str}, n = {item.get('sample_size')}) "
                f"indicates a {strength.lower()} {direction} linear relationship between '{col1}' and '{col2}'. "
                "Note: Correlation does not imply causation."
            )
        elif pattern_type == "GROUP_DIFFERENCE":
            cat_col, num_col = (cols[0], cols[1]) if len(cols) > 1 else (cols[0], "")
            eff_type = stats.get("effect_size_type", "effect")
            eff_val = stats.get("effect_size", 0.0)
            num_groups = stats.get("groups", 2)
            title = f"Group Difference in {num_col} across {cat_col}"
            desc = (
                f"Numeric measure '{num_col}' differs across {num_groups} categories of '{cat_col}' using {method} "
                f"({eff_type} = {eff_val}, {p_str}, n = {item.get('sample_size')}). "
                "Statistical significance does not imply practical importance."
            )
        elif pattern_type == "CATEGORICAL_ASSOCIATION":
            c1, c2 = (cols[0], cols[1]) if len(cols) > 1 else (cols[0], "")
            cv = stats.get("cramers_v", 0.0)
            title = f"Categorical Association between {c1} and {c2}"
            desc = (
                f"Chi-square test reveals a {strength.lower()} categorical association between '{c1}' and '{c2}' "
                f"(Cramer's V = {cv}, {p_str}, n = {item.get('sample_size')})."
            )
        elif pattern_type == "TIME_TREND":
            dt_col, num_col = (cols[0], cols[1]) if len(cols) > 1 else (cols[0], "")
            direction = stats.get("direction", "STABLE").lower()
            r2 = stats.get("r_squared", 0.0)
            title = f"{direction.title()} Historical Trend in {num_col} over {dt_col}"
            desc = (
                f"Historical linear regression shows a {direction} trend for '{num_col}' over '{dt_col}' "
                f"(R^2 = {r2}, {p_str}, n = {item.get('sample_size')}). "
                "Note: Historical trends describe observed data and are not forecasts."
            )
        elif pattern_type == "DISTRIBUTION":
            col = cols[0] if cols else ""
            shape = stats.get("shape", "SYMMETRIC").replace("_", " ").title()
            mean_val = stats.get("mean")
            med_val = stats.get("median")
            title = f"{shape} Distribution Summary for {col}"
            desc = (
                f"Descriptive distribution summary for '{col}' (mean = {mean_val}, median = {med_val}, "
                f"std = {stats.get('std')}, n = {item.get('sample_size')})."
            )
        else:
            title = f"Pattern Discovery: {pattern_type}"
            desc = f"Pattern detected in columns {cols}."

        return title, desc

    def score_and_rank_patterns(
        self, unranked_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not unranked_items:
            return []

        # 1. Deduplicate by (pattern_type, canonical_sorted_columns)
        deduped_map: Dict[Tuple[str, Tuple[str, ...]], Dict[str, Any]] = {}
        for item in unranked_items:
            ptype = item.get("pattern_type", "")
            cols = sorted(item.get("columns", []))
            key = (ptype, tuple(cols))

            item["score"] = self.calculate_score(item)
            title, desc = self.generate_title_and_description(item)
            item["title"] = title
            item["description"] = desc

            # Keep higher scoring if duplicate exists
            if key not in deduped_map or item["score"] > deduped_map[key]["score"]:
                deduped_map[key] = item

        deduped_items = list(deduped_map.values())

        # 2. 5-Tier Deterministic Ranking
        # Key: (1) score DESC, (2) adjusted_p_value ASC, (3) effect_size DESC, (4) sample_size DESC, (5) canonical_pattern_id ASC
        def ranking_key(x: Dict[str, Any]):
            score = x.get("score", 0.0)
            adj_p = x.get("adjusted_p_value")
            adj_p_val = adj_p if adj_p is not None else 1.0
            eff_size = x.get("effect_size")
            eff_size_val = eff_size if eff_size is not None else 0.0
            n = x.get("sample_size", 0)
            canonical_cols = "_".join(sorted(x.get("columns", [])))
            canon_id = f"{x.get('pattern_type')}_{canonical_cols}"

            return (-score, adj_p_val, -eff_size_val, -n, canon_id)

        ranked_items = sorted(deduped_items, key=ranking_key)

        # 3. Limit to MAX_TOTAL_PATTERNS (30) and assign 1-based ranks
        final_patterns = ranked_items[:MAX_TOTAL_PATTERNS]
        for idx, item in enumerate(final_patterns, start=1):
            item["rank"] = idx

        return final_patterns
