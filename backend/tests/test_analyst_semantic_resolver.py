from app.services.analyst.semantic_resolver import SemanticResolver


def test_semantic_resolver_exact_and_case_insensitive():
    profile_columns = [
        {"column_name": "Revenue", "data_type": "float"},
        {"column_name": "Region_Name", "data_type": "string"},
    ]
    resolver = SemanticResolver(profile_columns)

    # Exact
    res = resolver.resolve_column("Revenue")
    assert res.resolved_column == "Revenue"
    assert res.confidence == 1.0

    # Normalized / Case-insensitive
    res_lower = resolver.resolve_column("revenue")
    assert res_lower.resolved_column == "Revenue"

    res_spaces = resolver.resolve_column("region name")
    assert res_spaces.resolved_column == "Region_Name"


def test_semantic_resolver_ambiguity_clarification():
    profile_columns = [
        {"column_name": "Order_Date", "data_type": "datetime"},
        {"column_name": "Ship_Date", "data_type": "datetime"},
    ]
    resolver = SemanticResolver(profile_columns)

    res = resolver.resolve_column("date")
    assert res.is_ambiguous is True
    assert set(res.candidate_columns) == {"Order_Date", "Ship_Date"}
