import pytest
from pydantic import ValidationError
from app.services.analyst.query_plan import (
    AnalystIntent,
    FilterCondition,
    OperationType,
    QueryPlan,
    QueryResult,
    SortCondition,
)


def test_query_plan_extra_forbid():
    plan = QueryPlan(
        operation=OperationType.AGGREGATE,
        intent=AnalystIntent.DESCRIPTIVE_STATISTIC,
        target_columns=["sales"],
    )
    assert plan.operation == OperationType.AGGREGATE
    assert plan.target_columns == ["sales"]

    # Test extra="forbid" raises ValidationError when arbitrary field passed
    with pytest.raises(ValidationError):
        QueryPlan.model_validate({
            "operation": "AGGREGATE",
            "intent": "DESCRIPTIVE_STATISTIC",
            "arbitrary_field": "unauthorized",
        })


def test_filter_condition_extra_forbid():
    fc = FilterCondition(column="region", operator="=", value="North")
    assert fc.column == "region"

    with pytest.raises(ValidationError):
        FilterCondition.model_validate({
            "column": "region",
            "operator": "=",
            "value": "North",
            "malicious_code": "eval('1+1')",
        })


def test_query_result_sanitization():
    res = QueryResult(
        operation=OperationType.DESCRIBE,
        success=True,
        summary_text="Completed",
        data=[{"sales": 100.5}],
        metrics={"mean": 100.5},
        column_names=["sales"],
        row_count=1,
    )
    assert res.success is True
    assert res.execution_path == "DATAFRAME"
