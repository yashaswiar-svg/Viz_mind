import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.repositories.anomaly_detection_repository import AnomalyDetectionRepository
from app.db.repositories.insight_repository import InsightRepository
from app.db.repositories.pattern_discovery_repository import PatternDiscoveryRepository
from app.db.repositories.prediction_repository import PredictionRepository
from app.db.repositories.visualization_repository import VisualizationRepository
from app.services.analyst.query_plan import OperationType, QueryPlan, QueryResult


class QueryExecutor:
    """
    Deterministic execution engine for QueryPlans.
    Executes Path A (DataFrame calculations) or Path B (Phase 3-8 persisted records).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def _sanitize_value(self, val: Any) -> Any:
        if pd.isna(val) or val is None:
            return None
        if isinstance(val, (float, np.floating)):
            if np.isinf(val) or np.isnan(val):
                return None
            return float(val)
        if isinstance(val, (int, np.integer)):
            return int(val)
        if isinstance(val, (np.ndarray, list)):
            return [self._sanitize_value(x) for x in val]
        if isinstance(val, dict):
            return {str(k): self._sanitize_value(v) for k, v in val.items()}
        return str(val) if not isinstance(val, (bool, str)) else val

    def _sanitize_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{k: self._sanitize_value(v) for k, v in row.items()} for row in data]

    def _enforce_byte_limit(self, result: QueryResult) -> QueryResult:
        data_json = json.dumps(result.data, default=str)
        result.result_bytes = len(data_json.encode("utf-8"))
        if result.result_bytes > settings.MAX_QUERY_RESULT_BYTES:
            # Truncate rows until byte limit is respected
            truncated_data = list(result.data)
            while truncated_data and len(json.dumps(truncated_data, default=str).encode("utf-8")) > settings.MAX_QUERY_RESULT_BYTES:
                truncated_data.pop()
            result.data = truncated_data
            result.truncated = True
            result.row_count = len(result.data)
            result.result_bytes = len(json.dumps(result.data, default=str).encode("utf-8"))
        return result

    async def execute(
        self,
        plan: QueryPlan,
        df: Optional[pd.DataFrame] = None,
        dataset_id: Optional[Any] = None,
        profile_data: Optional[Dict[str, Any]] = None,
    ) -> QueryResult:

        if plan.requires_clarification:
            return QueryResult(
                operation=plan.operation,
                success=True,
                summary_text=plan.clarification_message or "Clarification required.",
                data=[],
                execution_path="CLARIFICATION",
                source_type="SYSTEM",
            )

        # Path B: Persisted Analytical Record Lookups (Phase 3-8)
        if plan.operation in {
            OperationType.ANOMALY_LOOKUP,
            OperationType.PREDICTION_LOOKUP,
            OperationType.PATTERN_LOOKUP,
            OperationType.INSIGHT_LOOKUP,
            OperationType.VISUALIZATION_REQUEST,
            OperationType.CORRELATION,
        }:
            return await self._execute_path_b_persisted(plan, dataset_id, profile_data, df)

        # Path A: DataFrame Operations
        if df is None or df.empty:
            return QueryResult(
                operation=plan.operation,
                success=False,
                summary_text="No processed dataset DataFrame available for calculation.",
                execution_path="DATAFRAME",
                source_type="PHASE_4_DATASET",
                error_message="Dataset is empty or unavailable.",
            )

        return self._execute_path_a_dataframe(plan, df)

    def _execute_path_a_dataframe(self, plan: QueryPlan, df: pd.DataFrame) -> QueryResult:
        df_work = df.copy()

        # Apply filters
        for f in plan.filters:
            col = f.column
            if col in df_work.columns:
                op = f.operator.upper()
                val = f.value
                if op == "=":
                    df_work = df_work[df_work[col] == val]
                elif op == "!=":
                    df_work = df_work[df_work[col] != val]
                elif op == ">":
                    df_work = df_work[df_work[col] > val]
                elif op == ">=":
                    df_work = df_work[df_work[col] >= val]
                elif op == "<":
                    df_work = df_work[df_work[col] < val]
                elif op == "<=":
                    df_work = df_work[df_work[col] <= val]
                elif op == "IN" and isinstance(val, list):
                    df_work = df_work[df_work[col].isin(val)]
                elif op == "NOT_IN" and isinstance(val, list):
                    df_work = df_work[~df_work[col].isin(val)]
                elif op == "CONTAINS" and isinstance(val, str):
                    df_work = df_work[df_work[col].astype(str).str.contains(val, case=False, na=False)]

        op_type = plan.operation

        if op_type == OperationType.COUNT:
            total_count = len(df_work)
            res = QueryResult(
                operation=op_type,
                success=True,
                summary_text=f"Total record count is {total_count}.",
                data=[{"count": total_count}],
                metrics={"total_count": total_count},
                column_names=["count"],
                row_count=1,
                execution_path="DATAFRAME",
                source_type="PHASE_4_DATASET",
            )
            return self._enforce_byte_limit(res)

        if op_type in {OperationType.AGGREGATE, OperationType.DESCRIBE}:
            metrics: Dict[str, Any] = {}
            row_dict: Dict[str, Any] = {}
            target_cols = plan.target_columns or [c for c in df_work.columns if pd.api.types.is_numeric_dtype(df_work[c])]

            for col in target_cols[:settings.MAX_QUERY_COLUMNS]:
                if col in df_work.columns:
                    s = df_work[col].dropna()
                    if s.empty:
                        continue
                    func = plan.aggregations.get(col, "mean").lower()
                    if func == "mean":
                        val = float(s.mean())
                    elif func == "sum":
                        val = float(s.sum())
                    elif func == "min":
                        val = float(s.min())
                    elif func == "max":
                        val = float(s.max())
                    elif func == "median":
                        val = float(s.median())
                    elif func == "count":
                        val = int(s.count())
                    else:
                        val = float(s.mean())

                    metrics[f"{col}_{func}"] = val
                    row_dict[col] = val

            res_data = [self._sanitize_value(row_dict)] if row_dict else []
            summary = f"Aggregated {len(row_dict)} metrics on dataset."
            res = QueryResult(
                operation=op_type,
                success=True,
                summary_text=summary,
                data=self._sanitize_data(res_data),
                metrics=self._sanitize_value(metrics),
                column_names=list(row_dict.keys()),
                row_count=len(res_data),
                execution_path="DATAFRAME",
                source_type="PHASE_4_DATASET",
            )
            return self._enforce_byte_limit(res)

        if op_type in {OperationType.GROUP_AGGREGATE, OperationType.COMPARE_GROUPS, OperationType.TOP_N, OperationType.BOTTOM_N}:
            dim_cols = plan.dimension_columns or [c for c in df_work.columns if not pd.api.types.is_numeric_dtype(df_work[c])]
            if not dim_cols:
                dim_col = df_work.columns[0]
            else:
                dim_col = dim_cols[0]

            target_cols = plan.target_columns or [c for c in df_work.columns if pd.api.types.is_numeric_dtype(df_work[c])]
            num_col = target_cols[0] if target_cols else None

            if num_col and num_col in df_work.columns:
                agg_func = plan.aggregations.get(num_col, "mean")
                grouped = df_work.groupby(dim_col)[num_col].agg(agg_func).reset_index()
            else:
                grouped = df_work.groupby(dim_col).size().reset_index(name="count")
                num_col = "count"

            # Apply sorting
            if plan.sort:
                ascending = (plan.sort.direction.lower() == "asc")
                grouped = grouped.sort_values(by=plan.sort.column if plan.sort.column in grouped.columns else num_col, ascending=ascending)
            elif op_type in {OperationType.TOP_N, OperationType.GROUP_AGGREGATE}:
                grouped = grouped.sort_values(by=num_col, ascending=False)
            elif op_type == OperationType.BOTTOM_N:
                grouped = grouped.sort_values(by=num_col, ascending=True)

            limit = plan.limit or settings.MAX_QUERY_ROWS
            grouped = grouped.head(limit)

            data_list = grouped.to_dict(orient="records")
            sanitized_data = self._sanitize_data(data_list)
            top_val = sanitized_data[0] if sanitized_data else {}
            summary = f"Group breakdown by {dim_col} returned {len(sanitized_data)} groups."
            if top_val:
                summary += f" Top category is '{top_val.get(dim_col)}' with {num_col} = {top_val.get(num_col)}."

            res = QueryResult(
                operation=op_type,
                success=True,
                summary_text=summary,
                data=sanitized_data,
                metrics={"group_count": len(sanitized_data)},
                column_names=list(grouped.columns),
                row_count=len(sanitized_data),
                execution_path="DATAFRAME",
                source_type="PHASE_4_DATASET",
            )
            return self._enforce_byte_limit(res)

        # Default fallback for FILTER or other DataFrame operations
        limit = plan.limit or settings.MAX_QUERY_ROWS
        res_df = df_work.head(limit)
        data_list = res_df.to_dict(orient="records")
        sanitized_data = self._sanitize_data(data_list)
        res = QueryResult(
            operation=op_type,
            success=True,
            summary_text=f"Retrieved {len(sanitized_data)} rows matching criteria.",
            data=sanitized_data,
            metrics={"row_count": len(sanitized_data)},
            column_names=list(res_df.columns),
            row_count=len(sanitized_data),
            execution_path="DATAFRAME",
            source_type="PHASE_4_DATASET",
        )
        return self._enforce_byte_limit(res)

    async def _execute_path_b_persisted(
        self,
        plan: QueryPlan,
        dataset_id: Optional[Any],
        profile_data: Optional[Dict[str, Any]],
        df: Optional[pd.DataFrame],
    ) -> QueryResult:

        op_type = plan.operation

        # CORRELATION
        if op_type == OperationType.CORRELATION:
            if dataset_id:
                pat_repo = PatternDiscoveryRepository(self.db)
                latest_run = await pat_repo.get_latest_run_for_dataset(dataset_id)
                if latest_run:
                    patterns = await pat_repo.get_results_by_run_id(latest_run.id)
                    corr_patterns = [p for p in patterns if p.pattern_type == "CORRELATION"]
                    if corr_patterns:
                        data = [
                            {
                                "feature_1": p.columns[0] if len(p.columns) > 0 else "",
                                "feature_2": p.columns[1] if len(p.columns) > 1 else "",
                                "correlation": p.metrics.get("correlation"),
                                "strength": p.strength,
                            }
                            for p in corr_patterns
                        ]
                        res = QueryResult(
                            operation=op_type,
                            success=True,
                            summary_text=f"Retrieved {len(data)} correlation results from Phase 6 discovery.",
                            data=self._sanitize_data(data),
                            metrics={"correlation_count": len(data)},
                            column_names=["feature_1", "feature_2", "correlation", "strength"],
                            row_count=len(data),
                            execution_path="PERSISTED_RECORD",
                            source_type="PHASE_6_PATTERNS",
                        )
                        return self._enforce_byte_limit(res)

            # DataFrame fallback correlation if no persisted run
            if df is not None:
                num_df = df.select_dtypes(include=[np.number])
                if not num_df.empty:
                    corr_matrix = num_df.corr().abs()
                    pairs = []
                    cols = list(num_df.columns)
                    for i in range(len(cols)):
                        for j in range(i + 1, len(cols)):
                            val = float(num_df[cols[i]].corr(num_df[cols[j]]))
                            pairs.append({"feature_1": cols[i], "feature_2": cols[j], "correlation": val})
                    pairs.sort(key=lambda x: abs(x["correlation"] or 0), reverse=True)
                    res = QueryResult(
                        operation=op_type,
                        success=True,
                        summary_text=f"Calculated {len(pairs)} correlation pairs.",
                        data=self._sanitize_data(pairs[:10]),
                        metrics={"pair_count": len(pairs)},
                        column_names=["feature_1", "feature_2", "correlation"],
                        row_count=min(len(pairs), 10),
                        execution_path="DATAFRAME",
                        source_type="PHASE_4_DATASET",
                    )
                    return self._enforce_byte_limit(res)

        # ANOMALY_LOOKUP
        if op_type == OperationType.ANOMALY_LOOKUP and dataset_id:
            anom_repo = AnomalyDetectionRepository(self.db)
            latest_run = await anom_repo.get_latest_run_for_dataset(dataset_id)
            if latest_run:
                anomalies = await anom_repo.get_results_by_run_id(latest_run.id)
                data = [
                    {
                        "column_name": a.column_name,
                        "row_index": a.row_index,
                        "value": a.anomaly_value,
                        "score": a.anomaly_score,
                        "method": a.method_used,
                    }
                    for a in anomalies[:20]
                ]
                res = QueryResult(
                    operation=op_type,
                    success=True,
                    summary_text=f"Found {latest_run.total_anomalies_detected} anomalies across {latest_run.anomalous_columns_count} columns in Phase 7.",
                    data=self._sanitize_data(data),
                    metrics={"total_anomalies": latest_run.total_anomalies_detected},
                    column_names=["column_name", "row_index", "value", "score", "method"],
                    row_count=len(data),
                    execution_path="PERSISTED_RECORD",
                    source_type="PHASE_7_ANOMALIES",
                )
                return self._enforce_byte_limit(res)

        # PREDICTION_LOOKUP
        if op_type == OperationType.PREDICTION_LOOKUP and dataset_id:
            pred_repo = PredictionRepository(self.db)
            latest_run = await pred_repo.get_latest_run_for_dataset(dataset_id)
            if latest_run:
                results = await pred_repo.get_results_by_run_id(latest_run.id)
                data = [
                    {
                        "task_type": r.task_type,
                        "target_column": r.target_column,
                        "model_name": r.model_name,
                        "metrics": r.metrics,
                    }
                    for r in results
                ]
                res = QueryResult(
                    operation=op_type,
                    success=True,
                    summary_text=f"Phase 7 predictive modeling trained {latest_run.models_trained_count} models with target '{latest_run.target_column}'.",
                    data=self._sanitize_data(data),
                    metrics={"task_type": latest_run.task_type, "target_column": latest_run.target_column},
                    column_names=["task_type", "target_column", "model_name", "metrics"],
                    row_count=len(data),
                    execution_path="PERSISTED_RECORD",
                    source_type="PHASE_7_PREDICTIONS",
                )
                return self._enforce_byte_limit(res)

        # INSIGHT_LOOKUP
        if op_type == OperationType.INSIGHT_LOOKUP and dataset_id:
            ins_repo = InsightRepository(self.db)
            latest_run = await ins_repo.get_latest_run_for_dataset(dataset_id)
            if latest_run:
                insights = await ins_repo.get_insights_by_run_id(latest_run.id)
                data = [
                    {
                        "title": i.title,
                        "type": i.insight_type,
                        "summary": i.summary,
                        "score": i.importance_score,
                    }
                    for i in insights
                ]
                res = QueryResult(
                    operation=op_type,
                    success=True,
                    summary_text=f"Retrieved {len(data)} AI insights discovered in Phase 8.",
                    data=self._sanitize_data(data),
                    metrics={"insight_count": len(data)},
                    column_names=["title", "type", "summary", "score"],
                    row_count=len(data),
                    execution_path="PERSISTED_RECORD",
                    source_type="PHASE_8_INSIGHTS",
                )
                return self._enforce_byte_limit(res)

        # VISUALIZATION_REQUEST
        if op_type == OperationType.VISUALIZATION_REQUEST and dataset_id:
            viz_repo = VisualizationRepository(self.db)
            latest_run = await viz_repo.get_latest_run_for_dataset(dataset_id)
            if latest_run:
                recs = await viz_repo.get_recommendations_by_run_id(latest_run.id)
                data = [
                    {
                        "chart_type": r.chart_type,
                        "title": r.title,
                        "x_column": r.x_column,
                        "y_column": r.y_column,
                        "score": r.score,
                    }
                    for r in recs[:5]
                ]
                res = QueryResult(
                    operation=op_type,
                    success=True,
                    summary_text=f"Phase 5 generated {len(recs)} visualization recommendations.",
                    data=self._sanitize_data(data),
                    metrics={"rec_count": len(recs)},
                    column_names=["chart_type", "title", "x_column", "y_column", "score"],
                    row_count=len(data),
                    execution_path="PERSISTED_RECORD",
                    source_type="PHASE_5_VISUALIZATIONS",
                )
                return self._enforce_byte_limit(res)

        # Fallback if persisted record missing
        res = QueryResult(
            operation=op_type,
            success=False,
            summary_text="No analytical results currently exist for this query type. Please run Phase 5-8 analysis first.",
            execution_path="PERSISTED_RECORD",
            source_type="SYSTEM",
            error_message="Persisted run not found.",
        )
        return self._enforce_byte_limit(res)
