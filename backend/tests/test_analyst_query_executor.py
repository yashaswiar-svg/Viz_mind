import numpy as np
import pandas as pd
import pytest
from app.services.analyst.query_executor import QueryExecutor
from app.services.analyst.query_plan import AnalystIntent, OperationType, QueryPlan


@pytest.mark.asyncio
async def test_query_executor_dataframe_path(db_session):
    executor = QueryExecutor(db_session)

    df = pd.DataFrame({
        "region": ["North", "North", "South", "South", "West"],
        "sales": [100.0, 200.0, 150.0, 50.0, np.nan],
    })

    plan = QueryPlan(
        operation=OperationType.GROUP_AGGREGATE,
        intent=AnalystIntent.GROUP_COMPARISON,
        target_columns=["sales"],
        dimension_columns=["region"],
        aggregations={"sales": "mean"},
    )

    result = await executor.execute(plan, df=df)
    assert result.success is True
    assert result.execution_path == "DATAFRAME"
    assert len(result.data) > 0
    # Ensure NaN was sanitized to None
    for row in result.data:
        assert not isinstance(row.get("sales"), float) or not np.isnan(row.get("sales"))


@pytest.mark.asyncio
async def test_query_executor_byte_limit_truncation(db_session):
    executor = QueryExecutor(db_session)

    # Large dataset generating > 1MB result
    df = pd.DataFrame({
        "id": range(15000),
        "long_text": ["A" * 100 for _ in range(15000)],
    })

    plan = QueryPlan(
        operation=OperationType.FILTER,
        intent=AnalystIntent.FILTERED_ANALYSIS,
        limit=15000,
    )

    result = await executor.execute(plan, df=df)
    assert result.result_bytes <= 1048576
    assert result.truncated is True
