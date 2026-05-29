"""Kill-switch checks (plan 3dd8b3c sec 6-7). Returns a status + reasons; never auto-resumes."""

from .manifest import MANIFEST

T = MANIFEST["gate_thresholds"]


def check_killswitch(metrics):
    """metrics keys (all optional, conservative defaults): current_drawdown, annualized_cost_drag, data_integrity_ok,
    mean_shortfall_bps, trailing_expectancy, mechanic_drift, manual_stop. Returns {status, reasons, halt}."""
    reasons = []
    dd = float(metrics.get("current_drawdown", 0.0) or 0.0)
    cost_drag = float(metrics.get("annualized_cost_drag", 0.0) or 0.0)
    data_ok = bool(metrics.get("data_integrity_ok", True))
    shortfall = float(metrics.get("mean_shortfall_bps", 0.0) or 0.0)
    trailing_exp = metrics.get("trailing_expectancy", None)
    mechanic_drift = bool(metrics.get("mechanic_drift", False))
    manual_stop = bool(metrics.get("manual_stop", False))

    halt = False
    if manual_stop:
        reasons.append("MANUAL_STOP"); halt = True
    if not data_ok:
        reasons.append("DATA_INTEGRITY_FAILURE_NO_TRADE"); halt = True
    if mechanic_drift:
        reasons.append("MECHANIC_DRIFT_FROM_LOCKED_S21"); halt = True
    if dd >= T["drawdown_kill"]:
        reasons.append("DRAWDOWN_KILL_GE_%d_PCT" % int(T["drawdown_kill"] * 100)); halt = True
    if cost_drag > T["annualized_cost_drag_max"]:
        reasons.append("COST_DRAG_BREACH_GT_5PCT_PER_YEAR"); halt = True
    if shortfall > T["implementation_shortfall_max_bps"]:
        reasons.append("IMPLEMENTATION_SHORTFALL_BLOWOUT"); halt = True
    if trailing_exp is not None and float(trailing_exp) < 0:
        reasons.append("EDGE_DIVERGENCE_TRAILING_EXPECTANCY_NEGATIVE")  # review-level (not auto-halt unless persistent)

    if halt:
        status = "TRIGGERED"
    elif dd >= T["drawdown_review"] or ("EDGE_DIVERGENCE_TRAILING_EXPECTANCY_NEGATIVE" in reasons):
        status = "REVIEW"
    elif dd >= T["drawdown_warn"]:
        status = "WARN"
    else:
        status = "GREEN"
    return {"status": status, "halt": halt, "reasons": reasons}
