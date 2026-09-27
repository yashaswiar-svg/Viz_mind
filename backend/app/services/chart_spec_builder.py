import math
import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SCATTER_MAX_POINTS = 5000
SCATTER_RANDOM_SEED = 42
DEFAULT_HISTOGRAM_BINS = 20
MAX_CATEGORIES = 20


def sanitize_value(val: Any) -> Any:
    """Converts Pandas/NumPy primitives, NaN, Inf, and timestamps to JSON-safe Python values."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(val).isoformat()
    return str(val)


class ChartSpecBuilder:
    """Constructs chart specifications and generates safe, aggregated chart-ready payloads."""

    def build_chart_spec(
        self,
        chart_type: str,
        x_column: str,
        y_column: Optional[str] = None,
        aggregation: Optional[str] = None,
        time_granularity: Optional[str] = None,
        title: str = "",
        description: str = "",
    ) -> Dict[str, Any]:
        spec = {
            "chart_type": chart_type,
            "x_column": x_column,
            "y_column": y_column,
            "aggregation": aggregation,
            "time_granularity": time_granularity,
            "title": title,
            "description": description,
            "x_label": x_column,
            "y_label": f"{aggregation.upper()}({y_column})" if (aggregation and y_column) else (y_column or "Count"),
            "sampled": False,
            "sample_size": None,
        }
        if chart_type == "histogram":
            spec["bins"] = DEFAULT_HISTOGRAM_BINS
        return spec

    def build_chart_data(
        self,
        df: pd.DataFrame,
        chart_spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        chart_type = chart_spec.get("chart_type")
        x_col = chart_spec.get("x_column")
        y_col = chart_spec.get("y_column")
        agg = chart_spec.get("aggregation") or "mean"
        time_granularity = chart_spec.get("time_granularity") or "daily"

        result_data: List[Dict[str, Any]] = []
        metadata: Dict[str, Any] = {
            "chart_type": chart_type,
            "x_column": x_col,
            "y_column": y_col,
            "aggregation": agg,
            "row_count": len(df),
            "sampled": False,
            "sample_size": len(df),
        }

        if x_col not in df.columns:
            return {"data": [], "metadata": metadata, "error": f"Column '{x_col}' not found in dataset."}

        # --- 1. HISTOGRAM ---
        if chart_type == "histogram":
            series = pd.to_numeric(df[x_col], errors="coerce").dropna()
            if len(series) == 0:
                return {"data": [], "metadata": metadata}

            num_bins = min(max(5, int(chart_spec.get("bins", DEFAULT_HISTOGRAM_BINS))), 50)
            counts, bin_edges = np.histogram(series, bins=num_bins)

            for i in range(len(counts)):
                start = sanitize_value(bin_edges[i])
                end = sanitize_value(bin_edges[i + 1])
                result_data.append(
                    {
                        "bin_start": start,
                        "bin_end": end,
                        "label": f"{start} - {end}",
                        "count": int(counts[i]),
                    }
                )

        # --- 2. BAR CHART ---
        elif chart_type == "bar":
            if not y_col or y_col not in df.columns:
                return {"data": [], "metadata": metadata}

            clean_df = df[[x_col, y_col]].dropna()
            clean_df[y_col] = pd.to_numeric(clean_df[y_col], errors="coerce")
            clean_df = clean_df.dropna()

            grouped = clean_df.groupby(x_col)[y_col].agg(agg).reset_index()
            grouped = grouped.sort_values(by=y_col, ascending=False).head(MAX_CATEGORIES)

            for _, row in grouped.iterrows():
                result_data.append(
                    {
                        "category": sanitize_value(row[x_col]),
                        "value": sanitize_value(row[y_col]),
                    }
                )

        # --- 3. COUNT BAR CHART ---
        elif chart_type == "count_bar":
            clean_series = df[x_col].dropna()
            counts = clean_series.value_counts().head(MAX_CATEGORIES)

            for cat, count in counts.items():
                result_data.append(
                    {
                        "category": sanitize_value(cat),
                        "count": int(count),
                    }
                )

        # --- 4. LINE CHART (TIME-SERIES) ---
        elif chart_type == "line":
            if not y_col or y_col not in df.columns:
                return {"data": [], "metadata": metadata}

            temp_df = df[[x_col, y_col]].copy()
            temp_df[x_col] = pd.to_datetime(temp_df[x_col], errors="coerce")
            temp_df[y_col] = pd.to_numeric(temp_df[y_col], errors="coerce")
            temp_df = temp_df.dropna()

            if len(temp_df) == 0:
                return {"data": [], "metadata": metadata}

            if time_granularity == "weekly":
                temp_df["dt_group"] = temp_df[x_col].dt.to_period("W").dt.to_timestamp()
            elif time_granularity == "monthly":
                temp_df["dt_group"] = temp_df[x_col].dt.to_period("M").dt.to_timestamp()
            else:
                temp_df["dt_group"] = temp_df[x_col].dt.floor("D")

            grouped = temp_df.groupby("dt_group")[y_col].agg(agg).reset_index()
            grouped = grouped.sort_values(by="dt_group")

            for _, row in grouped.iterrows():
                result_data.append(
                    {
                        "date": pd.Timestamp(row["dt_group"]).strftime("%Y-%m-%d"),
                        "value": sanitize_value(row[y_col]),
                    }
                )

        # --- 5. SCATTER PLOT ---
        elif chart_type == "scatter":
            if not y_col or y_col not in df.columns:
                return {"data": [], "metadata": metadata}

            clean_df = df[[x_col, y_col]].dropna()
            clean_df[x_col] = pd.to_numeric(clean_df[x_col], errors="coerce")
            clean_df[y_col] = pd.to_numeric(clean_df[y_col], errors="coerce")
            clean_df = clean_df.dropna()

            if len(clean_df) > SCATTER_MAX_POINTS:
                clean_df = clean_df.sample(n=SCATTER_MAX_POINTS, random_state=SCATTER_RANDOM_SEED)
                metadata["sampled"] = True
                metadata["sample_size"] = SCATTER_MAX_POINTS

            for _, row in clean_df.iterrows():
                result_data.append(
                    {
                        "x": sanitize_value(row[x_col]),
                        "y": sanitize_value(row[y_col]),
                    }
                )

        # --- 6. BOX PLOT ---
        elif chart_type == "boxplot":
            series = pd.to_numeric(df[x_col], errors="coerce").dropna()
            if len(series) == 0:
                return {"data": [], "metadata": metadata}

            q1 = float(series.quantile(0.25))
            median = float(series.median())
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            non_outliers = series[(series >= lower_bound) & (series <= upper_bound)]
            min_val = float(non_outliers.min()) if len(non_outliers) > 0 else float(series.min())
            max_val = float(non_outliers.max()) if len(non_outliers) > 0 else float(series.max())

            outliers = series[(series < lower_bound) | (series > upper_bound)].head(50).tolist()
            outliers_sanitized = [sanitize_value(o) for o in outliers]

            result_data.append(
                {
                    "min": sanitize_value(min_val),
                    "q1": sanitize_value(q1),
                    "median": sanitize_value(median),
                    "q3": sanitize_value(q3),
                    "max": sanitize_value(max_val),
                    "outliers": outliers_sanitized,
                }
            )

        return {
            "data": result_data,
            "metadata": metadata,
        }
