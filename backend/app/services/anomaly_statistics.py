import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from app.core.config import settings


def detect_iqr_anomalies(
    series: pd.Series,
    iqr_multiplier: float = 1.5,
) -> List[Dict[str, Any]]:
    """Detect anomalies in a numerical series using the Interquartile Range (IQR) method.

    Formula:
      Q1 = 25th percentile
      Q3 = 75th percentile
      IQR = Q3 - Q1
      lower_bound = Q1 - 1.5 * IQR
      upper_bound = Q3 + 1.5 * IQR
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_series) < settings.MIN_ANOMALY_OBSERVATIONS:
        return []

    q1 = float(clean_series.quantile(0.25))
    q3 = float(clean_series.quantile(0.75))
    iqr = q3 - q1

    if iqr == 0:
        std_val = float(clean_series.std())
        if std_val > 0:
            iqr = std_val
        else:
            return []

    lower_bound = q1 - iqr_multiplier * iqr
    upper_bound = q3 + iqr_multiplier * iqr


    results = []
    for idx, val in series.items():
        if pd.isna(val) or not np.isfinite(val):
            continue

        val_float = float(val)
        if val_float < lower_bound or val_float > upper_bound:
            distance = max(lower_bound - val_float, val_float - upper_bound)
            normalized_distance = distance / iqr if iqr > 0 else 0.0

            results.append(
                {
                    "observation_reference": f"row_{idx}",
                    "row_index": int(idx),
                    "value": val_float,
                    "method": "IQR",
                    "statistics": {
                        "q1": q1,
                        "q3": q3,
                        "iqr": iqr,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "normalized_distance": normalized_distance,
                    },
                    "expected_range": {
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                    },
                }
            )

    return results


def detect_robust_zscore_anomalies(
    series: pd.Series,
    threshold: float = settings.ROBUST_Z_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Detect anomalies in a numerical series using Robust Z-Score (Median & MAD).

    Formula:
      median = median(x)
      MAD = median(|x - median(x)|)
      robust_z = 0.6745 * (x - median) / MAD
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_series) < settings.MIN_ANOMALY_OBSERVATIONS:
        return []

    med = float(clean_series.median())
    mad = float((clean_series - med).abs().median())

    if mad == 0:
        return []

    results = []
    for idx, val in series.items():
        if pd.isna(val) or not np.isfinite(val):
            continue

        val_float = float(val)
        robust_z = 0.6745 * (val_float - med) / mad
        abs_z = abs(robust_z)

        if abs_z >= threshold:
            expected_lower = med - (threshold * mad / 0.6745)
            expected_upper = med + (threshold * mad / 0.6745)

            results.append(
                {
                    "observation_reference": f"row_{idx}",
                    "row_index": int(idx),
                    "value": val_float,
                    "method": "ROBUST_ZSCORE",
                    "statistics": {
                        "median": med,
                        "mad": mad,
                        "robust_zscore": float(robust_z),
                        "abs_robust_zscore": float(abs_z),
                    },
                    "expected_range": {
                        "lower_bound": float(expected_lower),
                        "upper_bound": float(expected_upper),
                    },
                }
            )

    return results


def detect_time_series_rolling_anomalies(
    df: pd.DataFrame,
    date_col: str,
    num_col: str,
    window: int = 7,
    threshold: float = settings.ROBUST_Z_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Detect anomalies in a chronological numerical series using rolling median baseline residuals."""
    if date_col not in df.columns or num_col not in df.columns:
        return []

    sorted_df = df.sort_values(by=date_col).copy()
    num_series = pd.to_numeric(sorted_df[num_col], errors="coerce")

    if num_series.dropna().count() < settings.MIN_ANOMALY_OBSERVATIONS:
        return []

    rolling_med = num_series.rolling(window=window, min_periods=1, center=True).median()
    residuals = (num_series - rolling_med).abs()
    mad = float(residuals.median())

    if mad == 0:
        std_res = float(residuals.std())
        if std_res > 0:
            mad = std_res
        else:
            return []


    results = []
    for idx, val in num_series.items():
        if pd.isna(val) or not np.isfinite(val):
            continue

        val_float = float(val)
        med_val = float(rolling_med.loc[idx])
        res_val = abs(val_float - med_val)
        robust_z = 0.6745 * res_val / mad

        if robust_z >= threshold:
            results.append(
                {
                    "observation_reference": f"row_{idx}",
                    "row_index": int(idx),
                    "value": val_float,
                    "method": "TIME_SERIES_RESIDUAL",
                    "statistics": {
                        "rolling_median": med_val,
                        "residual": res_val,
                        "mad": mad,
                        "robust_zscore": float(robust_z),
                    },
                    "expected_range": {
                        "lower_bound": float(med_val - threshold * mad / 0.6745),
                        "upper_bound": float(med_val + threshold * mad / 0.6745),
                    },
                }
            )

    return results
