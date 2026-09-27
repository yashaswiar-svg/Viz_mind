import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Column Visualization Roles
ROLE_NUMERIC_MEASURE = "NUMERIC_MEASURE"
ROLE_CATEGORICAL_DIMENSION = "CATEGORICAL_DIMENSION"
ROLE_DATETIME_DIMENSION = "DATETIME_DIMENSION"
ROLE_BOOLEAN_DIMENSION = "BOOLEAN_DIMENSION"
ROLE_IDENTIFIER = "IDENTIFIER"
ROLE_UNSUITABLE = "UNSUITABLE"

# Per Chart-Type Limits
MAX_HISTOGRAMS = 3
MAX_BAR_CHARTS = 4
MAX_LINE_CHARTS = 3
MAX_SCATTER_PLOTS = 3
MAX_BOXPLOTS = 2
MAX_COUNT_CHARTS = 2
MAX_TOTAL_RECOMMENDATIONS = 12


@dataclass
class ColumnRoleInfo:
    column_name: str
    data_type: str
    role: str
    distinct_count: int
    null_percentage: float
    is_numeric: bool
    is_categorical: bool
    is_datetime: bool


@dataclass
class ChartCandidate:
    chart_type: str
    x_column: str
    y_column: Optional[str] = None
    aggregation: Optional[str] = None
    grouping: Optional[str] = None
    time_granularity: Optional[str] = None
    title: str = ""
    description: str = ""
    base_score: float = 0.0
    reason: str = ""

    @property
    def dedup_key(self) -> Tuple[str, str, Optional[str], Optional[str], Optional[str], Optional[str]]:
        return (
            self.chart_type,
            self.x_column,
            self.y_column,
            self.aggregation,
            self.grouping,
            self.time_granularity,
        )


class VisualizationPlanner:
    """Classifies column roles and plans valid visualization chart candidates."""

    def classify_column_role(self, col_profile: Dict[str, Any], total_rows: int) -> ColumnRoleInfo:
        col_name = col_profile.get("column_name", "")
        data_type = str(col_profile.get("data_type", "")).lower()
        distinct_count = col_profile.get("distinct_count", 0)
        null_count = col_profile.get("null_count", 0)
        null_pct = (null_count / total_rows * 100.0) if total_rows > 0 else 0.0

        # Unsuitable: 100% null or 1 unique value
        if null_pct >= 100.0 or distinct_count <= 1:
            return ColumnRoleInfo(col_name, data_type, ROLE_UNSUITABLE, distinct_count, null_pct, False, False, False)

        # Identifier: unique per row or ID column name hint
        is_id_name = any(col_name.lower().endswith(suffix) for suffix in ["_id", "id", "uuid", "guid", "pk", "index"])
        if (distinct_count == total_rows and total_rows > 10) or (is_id_name and distinct_count > total_rows * 0.9):
            return ColumnRoleInfo(col_name, data_type, ROLE_IDENTIFIER, distinct_count, null_pct, False, False, False)

        # Datetime
        is_datetime = "date" in data_type or "time" in data_type or "timestamp" in data_type
        if is_datetime:
            return ColumnRoleInfo(col_name, data_type, ROLE_DATETIME_DIMENSION, distinct_count, null_pct, False, False, True)

        # Boolean
        is_bool = "bool" in data_type or distinct_count == 2
        if is_bool and not ("int" in data_type or "float" in data_type):
            return ColumnRoleInfo(col_name, data_type, ROLE_BOOLEAN_DIMENSION, distinct_count, null_pct, False, True, False)

        # Numeric vs Categorical
        is_numeric_type = any(t in data_type for t in ["int", "float", "double", "decimal", "numeric", "real"])
        
        if is_numeric_type:
            # Low cardinality integers can act as categorical dimension
            if distinct_count <= 15 and "int" in data_type:
                return ColumnRoleInfo(col_name, data_type, ROLE_CATEGORICAL_DIMENSION, distinct_count, null_pct, True, True, False)
            return ColumnRoleInfo(col_name, data_type, ROLE_NUMERIC_MEASURE, distinct_count, null_pct, True, False, False)

        # String/Categorical
        return ColumnRoleInfo(col_name, data_type, ROLE_CATEGORICAL_DIMENSION, distinct_count, null_pct, False, True, False)

    def plan_candidates(
        self,
        column_profiles: List[Dict[str, Any]],
        total_rows: int,
    ) -> List[ChartCandidate]:
        """Classify columns and generate deduplicated candidate charts subject to per-type limits."""
        column_roles: List[ColumnRoleInfo] = [
            self.classify_column_role(cp, total_rows) for cp in column_profiles
        ]

        numerics = [c for c in column_roles if c.role == ROLE_NUMERIC_MEASURE]
        categoricals = [c for c in column_roles if c.role in (ROLE_CATEGORICAL_DIMENSION, ROLE_BOOLEAN_DIMENSION) and c.distinct_count <= 25]
        datetimes = [c for c in column_roles if c.role == ROLE_DATETIME_DIMENSION]

        raw_candidates: List[ChartCandidate] = []

        # 1. Histograms (Distribution of numeric measures)
        for num_col in numerics[:6]:
            raw_candidates.append(
                ChartCandidate(
                    chart_type="histogram",
                    x_column=num_col.column_name,
                    title=f"Distribution of {num_col.column_name}",
                    description=f"Frequency distribution across bins for numeric column {num_col.column_name}.",
                    reason=f"Shows the underlying frequency distribution and spread for {num_col.column_name}.",
                    base_score=75.0,
                )
            )

        # 2. Box Plots (Spread & quartiles of numeric measures)
        for num_col in numerics[:4]:
            raw_candidates.append(
                ChartCandidate(
                    chart_type="boxplot",
                    x_column=num_col.column_name,
                    title=f"Box Plot of {num_col.column_name}",
                    description=f"Five-number summary (min, Q1, median, Q3, max) for {num_col.column_name}.",
                    reason=f"Identifies spread, median, quartiles, and potential outliers for {num_col.column_name}.",
                    base_score=70.0,
                )
            )

        # 3. Bar Charts (Categorical dimension vs Numeric measure)
        for cat_col in categoricals[:5]:
            for num_col in numerics[:4]:
                agg = "sum" if any(kw in num_col.column_name.lower() for kw in ["total", "amount", "sales", "revenue", "price", "count", "cost"]) else "mean"
                raw_candidates.append(
                    ChartCandidate(
                        chart_type="bar",
                        x_column=cat_col.column_name,
                        y_column=num_col.column_name,
                        aggregation=agg,
                        title=f"{agg.upper()} of {num_col.column_name} by {cat_col.column_name}",
                        description=f"Aggregated {agg} of {num_col.column_name} grouped by category {cat_col.column_name}.",
                        reason=f"Compares aggregated {agg} values of {num_col.column_name} across {cat_col.column_name} categories.",
                        base_score=85.0,
                    )
                )

        # 4. Count Bar Charts (Frequency of categorical categories)
        for cat_col in categoricals[:4]:
            raw_candidates.append(
                ChartCandidate(
                    chart_type="count_bar",
                    x_column=cat_col.column_name,
                    aggregation="count",
                    title=f"Count of Records by {cat_col.column_name}",
                    description=f"Record frequency count for each category in {cat_col.column_name}.",
                    reason=f"Displays categorical frequency and class distribution for {cat_col.column_name}.",
                    base_score=78.0,
                )
            )

        # 5. Line Charts (Time-series / Datetime trend vs Numeric measure)
        for dt_col in datetimes[:2]:
            for num_col in numerics[:4]:
                agg = "sum" if any(kw in num_col.column_name.lower() for kw in ["total", "amount", "sales", "revenue", "cost"]) else "mean"
                granularity = "daily" if total_rows <= 90 else ("weekly" if total_rows <= 365 else "monthly")
                raw_candidates.append(
                    ChartCandidate(
                        chart_type="line",
                        x_column=dt_col.column_name,
                        y_column=num_col.column_name,
                        aggregation=agg,
                        time_granularity=granularity,
                        title=f"{agg.upper()} of {num_col.column_name} over {dt_col.column_name}",
                        description=f"Time-series trend showing aggregated {agg} of {num_col.column_name} over time.",
                        reason=f"Tracks historical temporal progression of {num_col.column_name} over {dt_col.column_name}.",
                        base_score=90.0,
                    )
                )

        # 6. Scatter Plots (Relationship between two numeric measures)
        for i, col1 in enumerate(numerics[:4]):
            for col2 in numerics[i + 1 : 5]:
                raw_candidates.append(
                    ChartCandidate(
                        chart_type="scatter",
                        x_column=col1.column_name,
                        y_column=col2.column_name,
                        title=f"{col2.column_name} vs {col1.column_name}",
                        description=f"Bivariate scatter plot comparing {col1.column_name} against {col2.column_name}.",
                        reason=f"Visualizes potential correlation and joint distribution between {col1.column_name} and {col2.column_name}.",
                        base_score=80.0,
                    )
                )

        # Candidate Deduplication
        seen_keys: Set[Tuple[str, str, Optional[str], Optional[str], Optional[str], Optional[str]]] = set()
        deduped: List[ChartCandidate] = []
        for candidate in raw_candidates:
            if candidate.dedup_key not in seen_keys:
                seen_keys.add(candidate.dedup_key)
                deduped.append(candidate)

        # Enforce Per-Chart Type Limits
        counts: Dict[str, int] = {
            "histogram": 0,
            "bar": 0,
            "count_bar": 0,
            "line": 0,
            "scatter": 0,
            "boxplot": 0,
        }
        type_limits: Dict[str, int] = {
            "histogram": MAX_HISTOGRAMS,
            "bar": MAX_BAR_CHARTS,
            "count_bar": MAX_COUNT_CHARTS,
            "line": MAX_LINE_CHARTS,
            "scatter": MAX_SCATTER_PLOTS,
            "boxplot": MAX_BOXPLOTS,
        }

        limited_candidates: List[ChartCandidate] = []
        for c in deduped:
            c_type = c.chart_type
            if counts.get(c_type, 0) < type_limits.get(c_type, 99):
                counts[c_type] = counts.get(c_type, 0) + 1
                limited_candidates.append(c)

        return limited_candidates
