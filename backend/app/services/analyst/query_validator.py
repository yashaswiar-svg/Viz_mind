from typing import List, Optional, Set
from app.core.config import settings
from app.services.analyst.query_plan import OperationType, QueryPlan


class QueryValidationError(Exception):
    pass


class QueryValidator:
    """Validates structural query plan safety, parameters, and bound limits."""

    ALLOWED_OPERATIONS: Set[OperationType] = {
        OperationType.DESCRIBE,
        OperationType.COUNT,
        OperationType.AGGREGATE,
        OperationType.GROUP_AGGREGATE,
        OperationType.FILTER,
        OperationType.SORT,
        OperationType.TOP_N,
        OperationType.BOTTOM_N,
        OperationType.COMPARE_GROUPS,
        OperationType.TREND,
        OperationType.CORRELATION,
        OperationType.DISTRIBUTION,
        OperationType.ANOMALY_LOOKUP,
        OperationType.PREDICTION_LOOKUP,
        OperationType.PATTERN_LOOKUP,
        OperationType.INSIGHT_LOOKUP,
        OperationType.VISUALIZATION_REQUEST,
    }

    ALLOWED_AGGREGATIONS: Set[str] = {"sum", "mean", "median", "min", "max", "count"}
    ALLOWED_OPERATORS: Set[str] = {"=", "!=", ">", ">=", "<", "<=", "IN", "NOT_IN", "CONTAINS"}

    def validate_plan(self, plan: QueryPlan, valid_columns: Optional[List[str]] = None) -> None:
        if plan.requires_clarification:
            return

        if plan.operation not in self.ALLOWED_OPERATIONS:
            raise QueryValidationError(f"Operation '{plan.operation}' is not allowed.")

        # Check limit bounds
        if plan.limit and plan.limit > settings.MAX_QUERY_ROWS:
            plan.limit = settings.MAX_QUERY_ROWS

        # Check column count bounds
        total_cols = len(plan.target_columns) + len(plan.dimension_columns)
        if total_cols > settings.MAX_QUERY_COLUMNS:
            raise QueryValidationError(f"Query targets {total_cols} columns, exceeding limit of {settings.MAX_QUERY_COLUMNS}.")

        # Check valid column names if provided
        if valid_columns:
            valid_set = set(valid_columns)
            for c in plan.target_columns + plan.dimension_columns:
                if c not in valid_set:
                    raise QueryValidationError(f"Column '{c}' does not exist in dataset.")

        # Validate aggregations
        for col, func in plan.aggregations.items():
            if func.lower() not in self.ALLOWED_AGGREGATIONS:
                raise QueryValidationError(f"Aggregation function '{func}' is not permitted.")

        # Validate filters
        if len(plan.filters) > settings.MAX_FILTER_VALUES:
            raise QueryValidationError(f"Filter count exceeds maximum allowed limit of {settings.MAX_FILTER_VALUES}.")

        for f in plan.filters:
            if f.operator.upper() not in self.ALLOWED_OPERATORS:
                raise QueryValidationError(f"Filter operator '{f.operator}' is not permitted.")

        # Validate group values count
        if len(plan.group_values) > settings.MAX_GROUP_VALUES:
            raise QueryValidationError(f"Group values count exceeds limit of {settings.MAX_GROUP_VALUES}.")
