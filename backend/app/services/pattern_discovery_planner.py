import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from app.services.visualization_planner import (
    ROLE_BOOLEAN_DIMENSION,
    ROLE_CATEGORICAL_DIMENSION,
    ROLE_DATETIME_DIMENSION,
    ROLE_IDENTIFIER,
    ROLE_NUMERIC_MEASURE,
    ROLE_UNSUITABLE,
    VisualizationPlanner,
)

logger = logging.getLogger(__name__)

# Centralized Configuration Limits
MAX_CORRELATION_COLUMNS = 30
MAX_CORRELATION_PAIRS = 100
MAX_GROUP_COMPARISONS = 50
MAX_CATEGORICAL_ASSOCIATIONS = 50
MAX_TIME_TRENDS = 10
MAX_DISTRIBUTION_PATTERNS = 10
MAX_TOTAL_PATTERNS = 30

MIN_CORRELATION_N = 10
MIN_GROUP_SIZE = 10
MIN_TIME_POINTS = 8

P_VALUE_THRESHOLD = 0.05
FDR_ALPHA = 0.05

ABS_CORRELATION_MIN = 0.30
MIN_TREND_R2 = 0.30
MAX_CATEGORICAL_GROUPS = 20


@dataclass
class PatternCandidateTask:
    pattern_type: str
    columns: List[str]
    group_column: Optional[str] = None
    measure_column: Optional[str] = None
    datetime_column: Optional[str] = None
    method: str = ""
    reason: str = ""

    @property
    def dedup_key(self) -> Tuple[str, Tuple[str, ...]]:
        # Sort columns to enforce canonical pair identification
        sorted_cols = tuple(sorted(self.columns))
        return (self.pattern_type, sorted_cols)


class PatternDiscoveryPlanner:
    """Generates candidate pattern analysis tasks based on profile metadata and column eligibility."""

    def __init__(self):
        self.viz_planner = VisualizationPlanner()

    def generate_candidate_tasks(
        self, column_profiles: List[Dict[str, Any]], total_rows: int
    ) -> List[PatternCandidateTask]:
        roles = {}
        for col_p in column_profiles:
            col_name = col_p.get("column_name")
            if not col_name:
                continue
            role_info = self.viz_planner.classify_column_role(col_p, total_rows)
            roles[col_name] = role_info

        numeric_cols = [
            c for c, r in roles.items()
            if r.role == ROLE_NUMERIC_MEASURE or (r.is_numeric and r.role != ROLE_IDENTIFIER and r.role != ROLE_UNSUITABLE)
        ]
        categorical_cols = [
            c for c, r in roles.items()
            if r.role in (ROLE_CATEGORICAL_DIMENSION, ROLE_BOOLEAN_DIMENSION) or (r.is_categorical and r.role != ROLE_IDENTIFIER and r.role != ROLE_UNSUITABLE)
        ]
        datetime_cols = [
            c for c, r in roles.items()
            if r.role == ROLE_DATETIME_DIMENSION or (r.is_datetime and r.role != ROLE_IDENTIFIER and r.role != ROLE_UNSUITABLE)
        ]

        candidates: List[PatternCandidateTask] = []
        seen_keys: Set[Tuple[str, Tuple[str, ...]]] = set()

        # 1. Correlation Candidates (Numeric Pair)
        num_corr_cols = numeric_cols[:MAX_CORRELATION_COLUMNS]
        corr_pair_count = 0
        for i in range(len(num_corr_cols)):
            if corr_pair_count >= MAX_CORRELATION_PAIRS:
                break
            for j in range(i + 1, len(num_corr_cols)):
                if corr_pair_count >= MAX_CORRELATION_PAIRS:
                    break
                col1, col2 = num_corr_cols[i], num_corr_cols[j]
                task = PatternCandidateTask(
                    pattern_type="CORRELATION",
                    columns=[col1, col2],
                    method="pearson",
                    reason=f"Candidate numeric correlation pair between '{col1}' and '{col2}'.",
                )
                if task.dedup_key not in seen_keys:
                    seen_keys.add(task.dedup_key)
                    candidates.append(task)
                    corr_pair_count += 1

        # 2. Group Difference Candidates (Categorical + Numeric)
        group_diff_count = 0
        for cat_col in categorical_cols:
            if group_diff_count >= MAX_GROUP_COMPARISONS:
                break
            cat_role = roles[cat_col]
            if cat_role.distinct_count < 2 or cat_role.distinct_count > MAX_CATEGORICAL_GROUPS:
                continue

            for num_col in numeric_cols:
                if group_diff_count >= MAX_GROUP_COMPARISONS:
                    break
                if cat_col == num_col:
                    continue

                method = "Welch's t-test" if cat_role.distinct_count == 2 else "One-way ANOVA"
                task = PatternCandidateTask(
                    pattern_type="GROUP_DIFFERENCE",
                    columns=[cat_col, num_col],
                    group_column=cat_col,
                    measure_column=num_col,
                    method=method,
                    reason=f"Group comparison candidate for '{num_col}' across categories of '{cat_col}'.",
                )
                if task.dedup_key not in seen_keys:
                    seen_keys.add(task.dedup_key)
                    candidates.append(task)
                    group_diff_count += 1

        # 3. Categorical Association Candidates (Categorical + Categorical)
        cat_assoc_count = 0
        for i in range(len(categorical_cols)):
            if cat_assoc_count >= MAX_CATEGORICAL_ASSOCIATIONS:
                break
            for j in range(i + 1, len(categorical_cols)):
                if cat_assoc_count >= MAX_CATEGORICAL_ASSOCIATIONS:
                    break
                c1, c2 = categorical_cols[i], categorical_cols[j]
                r1, r2 = roles[c1], roles[c2]
                if r1.distinct_count < 2 or r1.distinct_count > MAX_CATEGORICAL_GROUPS:
                    continue
                if r2.distinct_count < 2 or r2.distinct_count > MAX_CATEGORICAL_GROUPS:
                    continue

                task = PatternCandidateTask(
                    pattern_type="CATEGORICAL_ASSOCIATION",
                    columns=[c1, c2],
                    method="chi_square",
                    reason=f"Categorical association candidate test between '{c1}' and '{c2}'.",
                )
                if task.dedup_key not in seen_keys:
                    seen_keys.add(task.dedup_key)
                    candidates.append(task)
                    cat_assoc_count += 1

        # 4. Time Trend Candidates (Datetime + Numeric)
        trend_count = 0
        for dt_col in datetime_cols:
            if trend_count >= MAX_TIME_TRENDS:
                break
            for num_col in numeric_cols:
                if trend_count >= MAX_TIME_TRENDS:
                    break
                task = PatternCandidateTask(
                    pattern_type="TIME_TREND",
                    columns=[dt_col, num_col],
                    datetime_column=dt_col,
                    measure_column=num_col,
                    method="linear_regression",
                    reason=f"Historical linear trend candidate for '{num_col}' over time '{dt_col}'.",
                )
                if task.dedup_key not in seen_keys:
                    seen_keys.add(task.dedup_key)
                    candidates.append(task)
                    trend_count += 1

        # 5. Distribution Candidates (Numeric)
        dist_count = 0
        for num_col in numeric_cols:
            if dist_count >= MAX_DISTRIBUTION_PATTERNS:
                break
            task = PatternCandidateTask(
                pattern_type="DISTRIBUTION",
                columns=[num_col],
                measure_column=num_col,
                method="descriptive_summary",
                reason=f"Descriptive distribution analysis candidate for '{num_col}'.",
            )
            if task.dedup_key not in seen_keys:
                seen_keys.add(task.dedup_key)
                candidates.append(task)
                dist_count += 1

        logger.info(f"Generated {len(candidates)} candidate pattern discovery tasks.")
        return candidates
