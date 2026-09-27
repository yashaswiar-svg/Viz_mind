from typing import Any, Dict, List


class QuestionSuggester:
    """Generates deterministic suggested question pills based on dataset metadata."""

    def suggest_questions(self, profile_columns: List[Dict[str, Any]]) -> List[str]:
        suggestions: List[str] = [
            "Give me a dataset overview and column summary.",
            "Are there any unusual anomalies in this dataset?",
            "What key AI insights did VizMind discover?",
        ]

        numeric_cols = [
            c.get("column_name") for c in profile_columns
            if any(t in str(c.get("data_type", "")).lower() for t in ["int", "float", "number", "decimal", "numeric"])
        ]
        categorical_cols = [
            c.get("column_name") for c in profile_columns
            if c.get("column_name") not in numeric_cols and not any(t in str(c.get("data_type", "")).lower() for t in ["date", "time"])
        ]

        if numeric_cols:
            suggestions.append(f"What is the average {numeric_cols[0]}?")
            if len(numeric_cols) > 1:
                suggestions.append(f"What is the correlation between {numeric_cols[0]} and {numeric_cols[1]}?")

        if categorical_cols and numeric_cols:
            suggestions.append(f"Which {categorical_cols[0]} has the highest {numeric_cols[0]}?")

        return suggestions[:6]
