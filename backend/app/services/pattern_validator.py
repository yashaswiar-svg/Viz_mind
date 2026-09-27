import logging
import math
from typing import Any, Dict
from app.core.exceptions import PatternVersionMismatchException, PatternDiscoveryException

logger = logging.getLogger(__name__)

ALLOWED_PATTERN_TYPES = {"CORRELATION", "GROUP_DIFFERENCE", "CATEGORICAL_ASSOCIATION", "TIME_TREND", "DISTRIBUTION"}


class PatternValidator:
    """Validates dataset checksum integrity and statistical pattern result sanity."""

    def validate_dataset_version(
        self,
        source_dataset_id: str,
        processed_dataset_id: str,
        expected_checksum: str,
        actual_checksum: str,
    ) -> None:
        if expected_checksum and actual_checksum and expected_checksum != actual_checksum:
            raise PatternVersionMismatchException(
                f"Processed dataset checksum mismatch for dataset '{source_dataset_id}'. "
                f"Expected {expected_checksum}, found {actual_checksum}."
            )

    def validate_pattern_result(self, result: Dict[str, Any]) -> bool:
        pattern_type = result.get("pattern_type")
        if pattern_type not in ALLOWED_PATTERN_TYPES:
            return False

        stats = result.get("statistics", {})
        if not isinstance(stats, dict):
            return False

        # Validate finite numeric values
        for k, v in stats.items():
            if isinstance(v, float):
                if math.isnan(v) or math.isinf(v):
                    return False

        raw_p = result.get("raw_p_value")
        if raw_p is not None:
            if math.isnan(raw_p) or math.isinf(raw_p) or raw_p < 0.0 or raw_p > 1.0:
                return False

        adj_p = result.get("adjusted_p_value")
        if adj_p is not None:
            if math.isnan(adj_p) or math.isinf(adj_p) or adj_p < 0.0 or adj_p > 1.0:
                return False

        return True
