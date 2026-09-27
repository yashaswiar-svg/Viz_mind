from typing import List, Tuple
from app.schemas.profile import DataQualityIssue


class DataQualityService:
    """Service providing deterministic Data Quality Score calculation and rule-based issue identification."""

    @staticmethod
    def evaluate_quality(
        row_count: int,
        column_count: int,
        duplicate_rows: int,
        missing_cells: int,
        column_profiles: list,
    ) -> Tuple[float, str, List[DataQualityIssue]]:
        issues: List[DataQualityIssue] = []

        total_cells = max(row_count * column_count, 1)
        missing_cell_percentage = (missing_cells / total_cells) * 100.0
        duplicate_row_percentage = (duplicate_rows / max(row_count, 1)) * 100.0 if row_count > 0 else 0.0

        constant_count = 0
        empty_count = 0
        high_cardinality_count = 0
        invalid_value_count = 0

        for col in column_profiles:
            c_name = col["column_name"]
            null_pct = col["null_percentage"]
            unique_pct = col["unique_percentage"]
            is_const = col["is_constant"]
            non_null = col["non_null_count"]

            # Issue: Empty Column
            if non_null == 0:
                empty_count += 1
                issues.append(
                    DataQualityIssue(
                        code="EMPTY_COLUMN",
                        severity="critical",
                        column=c_name,
                        message=f"Column '{c_name}' is entirely empty (100% missing).",
                        value=100.0,
                    )
                )
            # Issue: High Missingness
            elif null_pct >= 30.0:
                severity = "critical" if null_pct >= 70.0 else "warning"
                issues.append(
                    DataQualityIssue(
                        code="HIGH_MISSINGNESS",
                        severity=severity,
                        column=c_name,
                        message=f"Column '{c_name}' has a high percentage of missing values ({null_pct:.1f}%).",
                        value=round(null_pct, 1),
                    )
                )

            # Issue: Constant Column
            if is_const and non_null > 0:
                constant_count += 1
                issues.append(
                    DataQualityIssue(
                        code="CONSTANT_COLUMN",
                        severity="warning",
                        column=c_name,
                        message=f"Column '{c_name}' contains only 1 distinct non-null value.",
                    )
                )

            # Issue: High Cardinality
            if unique_pct >= 95.0 and non_null > 10 and not c_name.lower().endswith("id"):
                high_cardinality_count += 1
                issues.append(
                    DataQualityIssue(
                        code="HIGH_CARDINALITY",
                        severity="info",
                        column=c_name,
                        message=f"Column '{c_name}' has high cardinality ({unique_pct:.1f}% unique values).",
                        value=round(unique_pct, 1),
                    )
                )

        # Issue: Duplicate Rows
        if duplicate_row_percentage >= 5.0:
            severity = "warning" if duplicate_row_percentage < 20.0 else "critical"
            issues.append(
                DataQualityIssue(
                    code="DUPLICATE_ROWS",
                    severity=severity,
                    column=None,
                    message=f"Dataset contains {duplicate_rows} duplicate rows ({duplicate_row_percentage:.1f}%).",
                    value=round(duplicate_row_percentage, 1),
                )
            )

        # Calculate Score Weights (0-100)
        # 1. Missingness Weight (30%)
        missing_score = 30.0 * max(0.0, (1.0 - (missing_cell_percentage / 100.0)))

        # 2. Duplicate Weight (20%)
        duplicate_score = 20.0 * max(0.0, (1.0 - (duplicate_row_percentage / 100.0)))

        # 3. Invalid/Empty Columns Weight (20%)
        col_count_safe = max(column_count, 1)
        empty_col_penalty = (empty_count / col_count_safe) * 20.0
        invalid_score = max(0.0, 20.0 - empty_col_penalty)

        # 4. Constant Columns Weight (10%)
        const_col_penalty = (constant_count / col_count_safe) * 10.0
        constant_score = max(0.0, 10.0 - const_col_penalty)

        # 5. High Cardinality Weight (10%) - Conservative penalty
        cardinality_penalty = (high_cardinality_count / col_count_safe) * 5.0
        cardinality_score = max(5.0, 10.0 - cardinality_penalty)

        # 6. Type Consistency Weight (10%)
        type_score = 10.0

        total_score = round(min(100.0, max(0.0, missing_score + duplicate_score + invalid_score + constant_score + cardinality_score + type_score)), 1)

        # Assign Quality Level
        if total_score >= 90.0:
            level = "Excellent"
        elif total_score >= 75.0:
            level = "Good"
        elif total_score >= 50.0:
            level = "Fair"
        else:
            level = "Poor"

        return total_score, level, issues
