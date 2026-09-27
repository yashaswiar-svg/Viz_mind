import logging
from typing import Set

logger = logging.getLogger(__name__)

ALLOWED_AGGREGATIONS: Set[str] = {"sum", "mean", "median", "count", "min", "max"}
ALLOWED_CHART_TYPES: Set[str] = {"histogram", "bar", "count_bar", "line", "scatter", "boxplot"}


class VisualizationValidationError(Exception):
    """Exception raised when dataset version validation or aggregation validation fails."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class VisualizationValidator:
    """Validates dataset checksum/version integrity and chart aggregation requests."""

    def validate_aggregation(self, aggregation: str) -> str:
        if not aggregation:
            return "mean"
        agg_clean = aggregation.lower().strip()
        if agg_clean not in ALLOWED_AGGREGATIONS:
            raise VisualizationValidationError(
                code="INVALID_AGGREGATION_FUNCTION",
                message=f"Aggregation '{aggregation}' is not allowed. Allowed aggregations: {sorted(list(ALLOWED_AGGREGATIONS))}",
            )
        return agg_clean

    def validate_chart_type(self, chart_type: str) -> str:
        ct_clean = chart_type.lower().strip()
        if ct_clean not in ALLOWED_CHART_TYPES:
            raise VisualizationValidationError(
                code="INVALID_CHART_TYPE",
                message=f"Chart type '{chart_type}' is not supported. Allowed: {sorted(list(ALLOWED_CHART_TYPES))}",
            )
        return ct_clean

    def validate_dataset_version(
        self,
        source_dataset_id: str,
        processed_dataset_id: str,
        expected_checksum: str,
        actual_checksum: str,
    ) -> None:
        if expected_checksum and actual_checksum and expected_checksum != actual_checksum:
            raise VisualizationValidationError(
                code="VISUALIZATION_DATASET_VERSION_MISMATCH",
                message=(
                    f"Processed dataset checksum mismatch for dataset '{source_dataset_id}'. "
                    f"Expected {expected_checksum}, found {actual_checksum}."
                ),
            )
