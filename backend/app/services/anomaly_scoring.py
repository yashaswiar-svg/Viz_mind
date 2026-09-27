from typing import Any, Dict, List
from app.core.config import settings


def calculate_anomaly_score_and_severity(
    raw_anomalies: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Deduplicate raw candidate anomalies per (observation_reference, column_name),

    combine evidence, calculate a deterministic 0-100 anomaly score, and assign severity.

    Score interpretation:
      Higher score = more statistically unusual under the selected detection methods.
      (Does NOT imply business risk, fraud, or error).

    Severity Mapping:
      score < 40  -> LOW
      40 <= score < 70 -> MEDIUM
      score >= 70 -> HIGH
    """
    grouped: Dict[str, Dict[str, Any]] = {}

    for item in raw_anomalies:
        key = f"{item['observation_reference']}::{item['column_name']}"
        method = item["method"]

        if key not in grouped:
            grouped[key] = {
                "observation_reference": item["observation_reference"],
                "row_index": item.get("row_index", 0),
                "column_name": item["column_name"],
                "value": item["value"],
                "expected_range": item["expected_range"],
                "methods_detected": [method],
                "evidence": {method: item["statistics"]},
                "statistics": item["statistics"],
            }
        else:
            if method not in grouped[key]["methods_detected"]:
                grouped[key]["methods_detected"].append(method)
            grouped[key]["evidence"][method] = item["statistics"]

    merged_results = []
    for entry in grouped.values():
        score_components = []

        # 1. Robust Z-score component
        if "ROBUST_ZSCORE" in entry["evidence"]:
            z_val = entry["evidence"]["ROBUST_ZSCORE"].get("abs_robust_zscore", 3.5)
            # z=3.5 -> score ~ 35, z=7.0 -> score ~ 85, z>=10 -> score 100
            z_score_comp = min(100.0, (z_val / 10.0) * 100.0)
            score_components.append(z_score_comp)

        # 2. IQR component
        if "IQR" in entry["evidence"]:
            norm_dist = entry["evidence"]["IQR"].get("normalized_distance", 0.0)
            # norm_dist=0 -> score ~ 30, norm_dist=3 -> score ~ 90
            iqr_score_comp = min(100.0, 30.0 + (norm_dist / 3.0) * 70.0)
            score_components.append(iqr_score_comp)

        # 3. Time series component
        if "TIME_SERIES_RESIDUAL" in entry["evidence"]:
            ts_z = entry["evidence"]["TIME_SERIES_RESIDUAL"].get("robust_zscore", 3.5)
            ts_score_comp = min(100.0, (ts_z / 10.0) * 100.0)
            score_components.append(ts_score_comp)

        base_score = max(score_components) if score_components else 35.0

        # Multi-method boost (if detected by multiple methods, increase confidence)
        if len(entry["methods_detected"]) > 1:
            base_score = min(100.0, base_score + 10.0)

        final_score = round(float(base_score), 2)

        if final_score < 40.0:
            severity = "LOW"
        elif final_score < 70.0:
            severity = "MEDIUM"
        else:
            severity = "HIGH"

        entry["anomaly_score"] = final_score
        entry["severity"] = severity

        merged_results.append(entry)

    # Sort descending by anomaly_score
    merged_results.sort(key=lambda x: x["anomaly_score"], reverse=True)
    return merged_results
