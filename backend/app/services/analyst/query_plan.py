from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    DESCRIBE = "DESCRIBE"
    COUNT = "COUNT"
    AGGREGATE = "AGGREGATE"
    GROUP_AGGREGATE = "GROUP_AGGREGATE"
    FILTER = "FILTER"
    SORT = "SORT"
    TOP_N = "TOP_N"
    BOTTOM_N = "BOTTOM_N"
    COMPARE_GROUPS = "COMPARE_GROUPS"
    TREND = "TREND"
    CORRELATION = "CORRELATION"
    DISTRIBUTION = "DISTRIBUTION"
    ANOMALY_LOOKUP = "ANOMALY_LOOKUP"
    PREDICTION_LOOKUP = "PREDICTION_LOOKUP"
    PATTERN_LOOKUP = "PATTERN_LOOKUP"
    INSIGHT_LOOKUP = "INSIGHT_LOOKUP"
    VISUALIZATION_REQUEST = "VISUALIZATION_REQUEST"


class AnalystIntent(str, Enum):
    DATASET_OVERVIEW = "DATASET_OVERVIEW"
    DESCRIPTIVE_STATISTIC = "DESCRIPTIVE_STATISTIC"
    GROUP_COMPARISON = "GROUP_COMPARISON"
    TOP_BOTTOM = "TOP_BOTTOM"
    FILTERED_ANALYSIS = "FILTERED_ANALYSIS"
    TREND = "TREND"
    RELATIONSHIP = "RELATIONSHIP"
    ANOMALY = "ANOMALY"
    PREDICTION = "PREDICTION"
    PATTERN = "PATTERN"
    INSIGHT = "INSIGHT"
    VISUALIZATION = "VISUALIZATION"
    FOLLOW_UP = "FOLLOW_UP"
    CLARIFICATION = "CLARIFICATION"
    UNSUPPORTED = "UNSUPPORTED"


class FilterCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str
    operator: str = Field(..., description="One of =, !=, >, >=, <, <=, IN, NOT_IN, CONTAINS")
    value: Any


class SortCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str
    direction: str = Field("asc", description="asc or desc")


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: OperationType
    intent: AnalystIntent
    target_columns: List[str] = Field(default_factory=list)
    dimension_columns: List[str] = Field(default_factory=list)
    aggregations: Dict[str, str] = Field(default_factory=dict, description="e.g. {'sales': 'mean'}")
    filters: List[FilterCondition] = Field(default_factory=list)
    sort: Optional[SortCondition] = None
    limit: Optional[int] = Field(default=100)
    time_column: Optional[str] = None
    group_values: List[Any] = Field(default_factory=list)
    insight_type_filter: Optional[str] = None
    requires_clarification: bool = False
    clarification_message: Optional[str] = None
    clarification_options: List[str] = Field(default_factory=list)


class QueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: OperationType
    success: bool
    summary_text: str
    data: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    column_names: List[str] = Field(default_factory=list)
    row_count: int = 0
    execution_path: str = Field("DATAFRAME", description="DATAFRAME or PERSISTED_RECORD")
    source_type: str = Field("PHASE_4_DATASET", description="Origin of analytical evidence")
    error_message: Optional[str] = None
    truncated: bool = False
    result_bytes: int = 0
