from typing import Any, Dict


def calculate_baseline_improvement(
    model_metrics: Dict[str, Any],
    baseline_metrics: Dict[str, Any],
    problem_type: str,
) -> Dict[str, Any]:
    """Calculate transparent performance improvement of trained model vs baseline.

    Does NOT generate a fake AI score; provides metric delta and percentage change.
    """
    improvement = {}

    if problem_type in ["REGRESSION", "FORECASTING"]:
        b_mae = baseline_metrics.get("mae")
        m_mae = model_metrics.get("mae")

        if b_mae is not None and m_mae is not None and b_mae > 0:
            mae_diff = b_mae - m_mae
            mae_pct = (mae_diff / b_mae) * 100.0
            improvement["mae_reduction_pct"] = round(mae_pct, 2)
            improvement["is_better"] = bool(m_mae < b_mae)
        else:
            improvement["mae_reduction_pct"] = 0.0
            improvement["is_better"] = False

    elif problem_type == "CLASSIFICATION":
        b_acc = baseline_metrics.get("accuracy", 0.0)
        m_acc = model_metrics.get("accuracy", 0.0)

        if b_acc is not None and m_acc is not None:
            acc_diff = m_acc - b_acc
            acc_pct = (acc_diff / b_acc * 100.0) if b_acc > 0 else 0.0
            improvement["accuracy_gain_pct"] = round(acc_pct, 2)
            improvement["is_better"] = bool(m_acc > b_acc)
        else:
            improvement["accuracy_gain_pct"] = 0.0
            improvement["is_better"] = False

    return improvement
