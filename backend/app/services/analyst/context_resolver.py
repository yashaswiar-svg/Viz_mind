from typing import Any, Dict, List, Optional
from app.services.analyst.query_plan import FilterCondition, OperationType, QueryPlan


class ContextResolver:
    """Resolves follow-up conversation context strictly using previous validated QueryPlans."""

    def resolve_follow_up(
        self,
        current_question: str,
        previous_query_plan_dict: Optional[Dict[str, Any]],
        new_columns: List[str],
        new_filters: List[FilterCondition],
    ) -> Optional[QueryPlan]:
        """
        Merges new follow-up parameters into previous validated QueryPlan.
        """
        if not previous_query_plan_dict:
            return None

        try:
            prev_plan = QueryPlan.model_validate(previous_query_plan_dict)
        except Exception:
            return None

        # Build modified query plan preserving operation and targets
        merged_filters = list(prev_plan.filters)
        if new_filters:
            # Replace filter on same column if exists, otherwise append
            new_cols = {f.column for f in new_filters}
            merged_filters = [f for f in merged_filters if f.column not in new_cols] + new_filters

        merged_targets = list(prev_plan.target_columns)
        if new_columns:
            merged_targets = list(set(merged_targets + new_columns))

        return QueryPlan(
            operation=prev_plan.operation,
            intent=prev_plan.intent,
            target_columns=merged_targets,
            dimension_columns=prev_plan.dimension_columns,
            aggregations=prev_plan.aggregations,
            filters=merged_filters,
            sort=prev_plan.sort,
            limit=prev_plan.limit,
            time_column=prev_plan.time_column,
            group_values=prev_plan.group_values,
            insight_type_filter=prev_plan.insight_type_filter,
        )
