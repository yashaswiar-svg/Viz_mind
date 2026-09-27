from typing import Any, Dict, List, Optional
from app.services.analyst.query_plan import (
    AnalystIntent,
    FilterCondition,
    OperationType,
    QueryPlan,
    SortCondition,
)
from app.services.analyst.semantic_resolver import SemanticResolver


class QueryPlanner:
    """Transforms intent, semantic column mapping, and dataset profile into a structured QueryPlan."""

    INTENT_TO_OPERATION = {
        AnalystIntent.DATASET_OVERVIEW: OperationType.DESCRIBE,
        AnalystIntent.DESCRIPTIVE_STATISTIC: OperationType.AGGREGATE,
        AnalystIntent.GROUP_COMPARISON: OperationType.GROUP_AGGREGATE,
        AnalystIntent.TOP_BOTTOM: OperationType.TOP_N,
        AnalystIntent.FILTERED_ANALYSIS: OperationType.FILTER,
        AnalystIntent.TREND: OperationType.TREND,
        AnalystIntent.RELATIONSHIP: OperationType.CORRELATION,
        AnalystIntent.ANOMALY: OperationType.ANOMALY_LOOKUP,
        AnalystIntent.PREDICTION: OperationType.PREDICTION_LOOKUP,
        AnalystIntent.PATTERN: OperationType.PATTERN_LOOKUP,
        AnalystIntent.INSIGHT: OperationType.INSIGHT_LOOKUP,
        AnalystIntent.VISUALIZATION: OperationType.VISUALIZATION_REQUEST,
    }

    def build_plan(
        self,
        intent: AnalystIntent,
        question: str,
        profile_columns: List[Dict[str, Any]],
        previous_plan: Optional[QueryPlan] = None,
    ) -> QueryPlan:
        resolver = SemanticResolver(profile_columns)
        matched_cols, _, ambiguous_list = resolver.extract_columns_from_text(question)

        # 1. Ambiguity Clarification Check
        if ambiguous_list:
            options = ambiguous_list[0]
            return QueryPlan(
                operation=OperationType.DESCRIBE,
                intent=AnalystIntent.CLARIFICATION,
                requires_clarification=True,
                clarification_message=f"I found multiple columns matching your query: {', '.join(options)}. Which one did you mean?",
                clarification_options=options,
            )

        # Handle follow-up intent
        if intent == AnalystIntent.FOLLOW_UP and previous_plan:
            new_filters: List[FilterCondition] = []
            # Check if user mentioned a value or column
            if matched_cols:
                return QueryPlan(
                    operation=previous_plan.operation,
                    intent=previous_plan.intent,
                    target_columns=matched_cols or previous_plan.target_columns,
                    dimension_columns=previous_plan.dimension_columns,
                    aggregations=previous_plan.aggregations,
                    filters=previous_plan.filters,
                    sort=previous_plan.sort,
                    limit=previous_plan.limit,
                )

        # Categorize columns into numeric targets and categorical dimensions based on profile
        numeric_cols = []
        categorical_cols = []
        date_cols = []

        for col_name in matched_cols:
            for pcol in profile_columns:
                pname = pcol.get("column_name") if isinstance(pcol, dict) else str(pcol)
                if pname == col_name:
                    dtype = str(pcol.get("data_type", "")).lower() if isinstance(pcol, dict) else ""
                    if any(t in dtype for t in ["int", "float", "number", "decimal", "numeric"]):
                        numeric_cols.append(col_name)
                    elif any(t in dtype for t in ["date", "time"]):
                        date_cols.append(col_name)
                    else:
                        categorical_cols.append(col_name)

        op_type = self.INTENT_TO_OPERATION.get(intent, OperationType.DESCRIBE)

        # Build aggregations map for numeric columns
        aggregations: Dict[str, str] = {}
        q_lower = question.lower()

        agg_func = "mean"
        if "sum" in q_lower or "total" in q_lower:
            agg_func = "sum"
        elif "max" in q_lower or "highest" in q_lower or "best" in q_lower:
            agg_func = "max"
        elif "min" in q_lower or "lowest" in q_lower or "worst" in q_lower:
            agg_func = "min"
        elif "count" in q_lower:
            agg_func = "count"

        for ncol in numeric_cols:
            aggregations[ncol] = agg_func

        sort_cond = None
        if intent == AnalystIntent.TOP_BOTTOM:
            if "bottom" in q_lower or "lowest" in q_lower or "worst" in q_lower:
                sort_dir = "asc"
            else:
                sort_dir = "desc"
            sort_col = numeric_cols[0] if numeric_cols else (matched_cols[0] if matched_cols else "")
            if sort_col:
                sort_cond = SortCondition(column=sort_col, direction=sort_dir)

        # Determine time column for trends
        time_col = date_cols[0] if date_cols else None

        return QueryPlan(
            operation=op_type,
            intent=intent,
            target_columns=numeric_cols or matched_cols,
            dimension_columns=categorical_cols,
            aggregations=aggregations,
            sort=sort_cond,
            time_column=time_col,
            limit=10 if op_type == OperationType.TOP_N else 100,
        )
