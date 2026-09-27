import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def _approx_erfc(x: float) -> float:
    """Approximation of complementary error function erfc(x)."""
    if x < 0:
        return 2.0 - _approx_erfc(-x)
    # Abramowitz and Stegun formula 7.1.26
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * math.exp(-x * x))
    return 1.0 - y


def _normal_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal distribution."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _t_pvalue(t_stat: float, df: float) -> float:
    """Approximates 2-tailed p-value for Student's t distribution."""
    abs_t = abs(t_stat)
    if df <= 0:
        return 1.0
    # For df >= 30, normal distribution approximation is accurate to 3+ decimal places
    if df >= 30:
        return max(0.0, min(1.0, 2.0 * (1.0 - _normal_cdf(abs_t))))
    
    # For smaller df, transformation using t^2 / (df + t^2)
    x = df / (df + abs_t * abs_t)
    # Simple polynomial approximation for small df
    z = abs_t / math.sqrt(df)
    prob = 2.0 * (1.0 - _normal_cdf(z * (1.0 - 1.0 / (4.0 * df))))
    return max(0.0, min(1.0, prob))


def _f_pvalue(f_stat: float, df1: float, df2: float) -> float:
    """Approximates p-value for F distribution."""
    if f_stat <= 0 or df1 <= 0 or df2 <= 0:
        return 1.0
    # Normal approximation for F distribution: z = (F^(1/3) * (1 - 2/(9*df2)) - (1 - 2/(9*df1))) / sqrt(2/(9*df1) + F^(2/3) * 2/(9*df2))
    try:
        f_cbrt = math.pow(f_stat, 1.0 / 3.0)
        num = f_cbrt * (1.0 - 2.0 / (9.0 * df2)) - (1.0 - 2.0 / (9.0 * df1))
        den = math.sqrt(2.0 / (9.0 * df1) + (f_cbrt * f_cbrt) * 2.0 / (9.0 * df2))
        z = num / den
        return max(0.0, min(1.0, 1.0 - _normal_cdf(z)))
    except Exception:
        return 0.05 if f_stat > 3.0 else 0.5


def _chi2_pvalue(chi2: float, df: int) -> float:
    """Approximates p-value for Chi-square distribution using Wilson-Hilferty transformation."""
    if chi2 <= 0 or df <= 0:
        return 1.0
    try:
        # Wilson-Hilferty transformation: z = ((chi2 / df)^(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df))
        term = math.pow(chi2 / float(df), 1.0 / 3.0)
        mean_term = 1.0 - (2.0 / (9.0 * float(df)))
        var_term = math.sqrt(2.0 / (9.0 * float(df)))
        z = (term - mean_term) / var_term
        return max(0.0, min(1.0, 1.0 - _normal_cdf(z)))
    except Exception:
        return 0.05 if chi2 > df else 0.5


def apply_fdr_correction(raw_p_values: List[float]) -> List[float]:
    """Applies Benjamini-Hochberg False Discovery Rate (FDR) correction to a list of raw p-values."""
    m = len(raw_p_values)
    if m == 0:
        return []
    if m == 1:
        return [min(1.0, max(0.0, raw_p_values[0]))]

    indexed_pvals = sorted(enumerate(raw_p_values), key=lambda x: x[1])
    adjusted = [0.0] * m

    cum_min = 1.0
    for rank_idx in range(m - 1, -1, -1):
        orig_idx, pval = indexed_pvals[rank_idx]
        rank = rank_idx + 1  # 1-based rank
        adj_p = (pval * m) / rank
        cum_min = min(cum_min, adj_p)
        adjusted[orig_idx] = min(1.0, max(0.0, cum_min))

    return adjusted


def compute_correlation(
    series1: pd.Series, series2: pd.Series, method: str = "pearson", min_n: int = 10
) -> Optional[Dict[str, Any]]:
    """Computes Pearson correlation between two numeric series with statistical validity checks."""
    df_clean = pd.DataFrame({"x": series1, "y": series2}).dropna()
    n = len(df_clean)
    if n < min_n:
        return None

    x = df_clean["x"].astype(float).values
    y = df_clean["y"].astype(float).values

    std_x, std_y = np.std(x, ddof=1), np.std(y, ddof=1)
    if std_x == 0 or std_y == 0:
        return None

    try:
        if method == "spearman":
            rank_x = pd.Series(x).rank().values
            rank_y = pd.Series(y).rank().values
            r = float(np.corrcoef(rank_x, rank_y)[0, 1])
        else:
            r = float(np.corrcoef(x, y)[0, 1])

        if math.isnan(r) or math.isinf(r):
            return None

        # Clamp r to [-1.0, 1.0]
        r = max(-1.0, min(1.0, r))
        abs_r = abs(r)

        # p-value calculation via t-statistic
        if abs_r >= 1.0:
            p_val = 0.0
        else:
            t_stat = r * math.sqrt(n - 2) / math.sqrt(1.0 - r * r)
            p_val = _t_pvalue(t_stat, float(n - 2))

        if abs_r >= 0.70:
            strength = "STRONG"
        elif abs_r >= 0.50:
            strength = "STRONG"
        elif abs_r >= 0.30:
            strength = "MODERATE"
        else:
            strength = "WEAK"

        direction = "POSITIVE" if r > 0 else ("NEGATIVE" if r < 0 else "NONE")

        return {
            "correlation": round(r, 4),
            "absolute_correlation": round(abs_r, 4),
            "raw_p_value": float(p_val),
            "sample_size": n,
            "strength": strength,
            "direction": direction,
            "method": method,
        }
    except Exception:
        return None


def compute_group_difference(
    group_series: pd.Series,
    measure_series: pd.Series,
    min_group_size: int = 10,
    max_groups: int = 20,
) -> Optional[Dict[str, Any]]:
    """Computes statistical group difference (Welch's t-test or One-way ANOVA)."""
    df_clean = pd.DataFrame({"g": group_series, "m": measure_series}).dropna()
    if df_clean.empty:
        return None

    df_clean["m"] = df_clean["m"].astype(float)
    groups_data = {}
    for g_val, sub_df in df_clean.groupby("g"):
        if len(sub_df) >= min_group_size:
            groups_data[str(g_val)] = sub_df["m"].values

    num_valid_groups = len(groups_data)
    if num_valid_groups < 2 or num_valid_groups > max_groups:
        return None

    group_keys = list(groups_data.keys())
    group_values = [groups_data[k] for k in group_keys]
    total_n = sum(len(arr) for arr in group_values)

    try:
        if num_valid_groups == 2:
            arr1, arr2 = group_values[0], group_values[1]
            n1, n2 = len(arr1), len(arr2)
            mean1, mean2 = np.mean(arr1), np.mean(arr2)
            var1, var2 = np.var(arr1, ddof=1), np.var(arr2, ddof=1)

            if var1 == 0 and var2 == 0:
                return None

            se = math.sqrt(var1 / n1 + var2 / n2)
            if se == 0:
                return None

            t_stat = (mean1 - mean2) / se
            # Welch-Satterthwaite degrees of freedom
            df_num = (var1 / n1 + var2 / n2) ** 2
            df_den = ((var1 / n1) ** 2) / max(1, n1 - 1) + ((var2 / n2) ** 2) / max(1, n2 - 1)
            df_welch = df_num / df_den if df_den > 0 else float(total_n - 2)

            p_val = _t_pvalue(t_stat, df_welch)

            # Calculate Cohen's d
            s_pooled = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / max(1, n1 + n2 - 2))
            cohens_d = (mean1 - mean2) / s_pooled if s_pooled > 0 else 0.0
            abs_d = abs(cohens_d)

            if abs_d >= 0.8:
                strength = "STRONG"
            elif abs_d >= 0.5:
                strength = "MODERATE"
            else:
                strength = "WEAK"

            return {
                "statistic": round(t_stat, 4),
                "raw_p_value": float(p_val),
                "effect_size": round(abs_d, 4),
                "effect_size_type": "cohens_d",
                "groups": num_valid_groups,
                "group_names": group_keys,
                "group_sizes": {k: len(v) for k, v in groups_data.items()},
                "sample_size": total_n,
                "strength": strength,
                "method": "Welch's t-test",
            }
        else:
            # One-way ANOVA
            k = num_valid_groups
            overall_mean = np.mean(np.concatenate(group_values))
            ss_between = sum(len(arr) * ((np.mean(arr) - overall_mean) ** 2) for arr in group_values)
            ss_within = sum(np.sum((arr - np.mean(arr)) ** 2) for arr in group_values)
            ss_total = ss_between + ss_within

            df1 = k - 1
            df2 = total_n - k

            ms_between = ss_between / df1 if df1 > 0 else 0.0
            ms_within = ss_within / df2 if df2 > 0 else 0.0

            if ms_within == 0:
                return None

            f_stat = ms_between / ms_within
            p_val = _f_pvalue(f_stat, float(df1), float(df2))
            eta_squared = (ss_between / ss_total) if ss_total > 0 else 0.0

            if eta_squared >= 0.14:
                strength = "STRONG"
            elif eta_squared >= 0.06:
                strength = "MODERATE"
            else:
                strength = "WEAK"

            return {
                "statistic": round(f_stat, 4),
                "raw_p_value": float(p_val),
                "effect_size": round(float(eta_squared), 4),
                "effect_size_type": "eta_squared",
                "groups": num_valid_groups,
                "group_names": group_keys,
                "group_sizes": {k: len(v) for k, v in groups_data.items()},
                "sample_size": total_n,
                "strength": strength,
                "method": "One-way ANOVA",
            }
    except Exception:
        return None


def compute_categorical_association(
    cat1_series: pd.Series, cat2_series: pd.Series, min_n: int = 20
) -> Optional[Dict[str, Any]]:
    """Computes Chi-square test of independence and Cramér's V for two categorical columns."""
    df_clean = pd.DataFrame({"c1": cat1_series, "c2": cat2_series}).dropna()
    n = len(df_clean)
    if n < min_n:
        return None

    contingency_table = pd.crosstab(df_clean["c1"], df_clean["c2"])
    r_count, c_count = contingency_table.shape
    if r_count < 2 or c_count < 2:
        return None

    try:
        observed = contingency_table.values.astype(float)
        row_sums = observed.sum(axis=1)
        col_sums = observed.sum(axis=0)
        total_obs = float(n)

        expected = np.outer(row_sums, col_sums) / total_obs
        if np.any(expected == 0):
            return None

        chi2 = float(np.sum(((observed - expected) ** 2) / expected))
        dof = (r_count - 1) * (c_count - 1)

        p_val = _chi2_pvalue(chi2, dof)

        min_dim = min(r_count - 1, c_count - 1)
        if min_dim == 0 or total_obs == 0:
            return None

        cramers_v = math.sqrt(chi2 / (total_obs * min_dim))
        cramers_v = float(cramers_v)

        if cramers_v >= 0.30:
            strength = "STRONG"
        elif cramers_v >= 0.15:
            strength = "MODERATE"
        else:
            strength = "WEAK"

        return {
            "chi_square": round(chi2, 4),
            "raw_p_value": float(p_val),
            "degrees_of_freedom": int(dof),
            "cramers_v": round(cramers_v, 4),
            "effect_size": round(cramers_v, 4),
            "effect_size_type": "cramers_v",
            "sample_size": n,
            "strength": strength,
            "method": "chi_square",
        }
    except Exception:
        return None


def compute_time_trend(
    dt_series: pd.Series, measure_series: pd.Series, min_time_points: int = 8
) -> Optional[Dict[str, Any]]:
    """Computes historical linear trend over time."""
    df_clean = pd.DataFrame({"dt": dt_series, "m": measure_series}).dropna()
    if df_clean.empty:
        return None

    df_clean["dt"] = pd.to_datetime(df_clean["dt"], errors="coerce")
    df_clean["m"] = df_clean["m"].astype(float)
    df_clean = df_clean.dropna().sort_values("dt")

    n = len(df_clean)
    if n < min_time_points:
        return None

    x = np.arange(n, dtype=float)
    y = df_clean["m"].values

    std_y = np.std(y, ddof=1)
    if std_y == 0:
        return None

    try:
        r = float(np.corrcoef(x, y)[0, 1])
        r_squared = float(r ** 2)

        mean_x, mean_y = np.mean(x), np.mean(y)
        var_x = np.var(x, ddof=1)
        cov_xy = np.cov(x, y)[0, 1]

        slope = float(cov_xy / var_x) if var_x > 0 else 0.0
        intercept = float(mean_y - slope * mean_x)

        # p-value for slope test
        abs_r = abs(r)
        if abs_r >= 1.0:
            p_val = 0.0
        else:
            t_stat = r * math.sqrt(n - 2) / math.sqrt(1.0 - r * r)
            p_val = _t_pvalue(t_stat, float(n - 2))

        if slope > 0 and r_squared >= 0.30:
            direction = "INCREASING"
        elif slope < 0 and r_squared >= 0.30:
            direction = "DECREASING"
        else:
            direction = "STABLE"

        if r_squared >= 0.70:
            strength = "STRONG"
        elif r_squared >= 0.30:
            strength = "MODERATE"
        else:
            strength = "WEAK"

        return {
            "slope": round(slope, 6),
            "intercept": round(intercept, 4),
            "r_squared": round(r_squared, 4),
            "raw_p_value": float(p_val),
            "sample_size": n,
            "direction": direction,
            "strength": strength,
            "effect_size": round(r_squared, 4),
            "effect_size_type": "r_squared",
            "method": "linear_regression",
        }
    except Exception:
        return None


def compute_distribution_statistics(series: pd.Series) -> Optional[Dict[str, Any]]:
    """Computes descriptive distribution statistics for a numeric column."""
    clean_s = series.dropna().astype(float)
    n = len(clean_s)
    if n < 5:
        return None

    try:
        mean_val = float(clean_s.mean())
        std_val = float(clean_s.std())
        min_val = float(clean_s.min())
        max_val = float(clean_s.max())
        q1_val = float(clean_s.quantile(0.25))
        median_val = float(clean_s.median())
        q3_val = float(clean_s.quantile(0.75))
        iqr_val = q3_val - q1_val
        skew_val = float(clean_s.skew()) if n >= 3 else 0.0

        if math.isnan(skew_val):
            skew_val = 0.0

        if skew_val > 1.0:
            shape_desc = "RIGHT_SKEWED"
        elif skew_val < -1.0:
            shape_desc = "LEFT_SKEWED"
        else:
            shape_desc = "SYMMETRIC"

        return {
            "mean": round(mean_val, 4),
            "median": round(median_val, 4),
            "std": round(std_val, 4),
            "min": round(min_val, 4),
            "max": round(max_val, 4),
            "q1": round(q1_val, 4),
            "q3": round(q3_val, 4),
            "iqr": round(iqr_val, 4),
            "skewness": round(skew_val, 4),
            "shape": shape_desc,
            "sample_size": n,
            "strength": "MODERATE",
            "method": "descriptive_summary",
        }
    except Exception:
        return None
