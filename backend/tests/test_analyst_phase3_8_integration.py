import pytest
from app.services.analyst.query_executor import QueryExecutor
from app.services.analyst.query_plan import AnalystIntent, OperationType, QueryPlan


@pytest.mark.asyncio
async def test_phase9_reuses_phase3_8_analytical_records(db_session):
    executor = QueryExecutor(db_session)

    # Test Anomaly lookup plan
    plan_anomaly = QueryPlan(
        operation=OperationType.ANOMALY_LOOKUP,
        intent=AnalystIntent.ANOMALY,
    )
    res_anomaly = await executor.execute(plan_anomaly)
    assert res_anomaly.execution_path == "PERSISTED_RECORD"

    # Test Prediction lookup plan
    plan_pred = QueryPlan(
        operation=OperationType.PREDICTION_LOOKUP,
        intent=AnalystIntent.PREDICTION,
    )
    res_pred = await executor.execute(plan_pred)
    assert res_pred.execution_path == "PERSISTED_RECORD"

    # Test Insight lookup plan
    plan_insight = QueryPlan(
        operation=OperationType.INSIGHT_LOOKUP,
        intent=AnalystIntent.INSIGHT,
    )
    res_insight = await executor.execute(plan_insight)
    assert res_insight.execution_path == "PERSISTED_RECORD"
