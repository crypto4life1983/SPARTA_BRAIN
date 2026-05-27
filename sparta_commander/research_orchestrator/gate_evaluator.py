"""Extract K9 / DR / performance metrics from sealed JSON reports.

Used to evaluate whether a P6 IS / P6.5 / P10 OOS result has cleared the
sample-size + cost-stress gates. Read-only.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any


K9_STATUS_PASS = "PASS"
K9_STATUS_FAIL = "FAIL"
K9_STATUS_UNKNOWN = "UNKNOWN"
K9_STATUS_NOT_EVALUATED = "NOT_EVALUATED"


def _safe_get(d: dict[str, Any], *keys: str) -> Any:
    """Walk a nested dict; return None on miss."""
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def extract_gates(report_path: str | pathlib.Path) -> dict[str, Any]:
    """Pull K9 / DR / performance metrics from one sealed JSON.

    Returns {} on parse failure. Otherwise:
        {
          "verdict": "READY_FOR_LONGER_BACKTEST"|"INSUFFICIENT_SAMPLE"|"REJECT_FAST"|...,
          "closed_trades": int | None,
          "k9_threshold": int | None,
          "k9_status": "PASS"|"FAIL"|"UNKNOWN"|"NOT_EVALUATED",
          "k9_margin_ratio": float | None,
          "net_pnl_usd": float | None,
          "max_drawdown_pct": float | None,
          "sharpe_annualized": float | None,
          "annual_turnover": float | None,
          "s1_cost_drag": float | None,
          "is_window_start": str | None,
          "is_window_end": str | None,
          "oos_window_start": str | None,
          "oos_window_end": str | None,
          "dr_gates_fired": {"DR2": bool|None, "DR3": bool|None, ...},
          "phase_verdict_raw": <whatever the report calls "verdict">,
        }
    """
    p = pathlib.Path(report_path)
    if not p.exists():
        return {}
    try:
        body = json.loads(p.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if not isinstance(body, dict):
        return {}

    perf = body.get("performance_summary") if isinstance(body.get("performance_summary"), dict) else {}
    config = body.get("config_used") if isinstance(body.get("config_used"), dict) else {}
    scan = body.get("scan_diagnostics") if isinstance(body.get("scan_diagnostics"), dict) else {}
    k_eval = body.get("k_gates_p6_is_evaluation") if isinstance(body.get("k_gates_p6_is_evaluation"), dict) else {}
    a_eval = body.get("a_gates_p6_is_evaluation") if isinstance(body.get("a_gates_p6_is_evaluation"), dict) else {}

    # K9 extraction. Multiple locations to handle across phases.
    closed_trades = (
        perf.get("closed_trades_count")
        or _safe_get(body, "trade_diagnostics", "closed_trades_count")
        or _safe_get(body, "p6_is_verdict_anchor", "closed_trades_count_observed")
        or _safe_get(body, "p6_result_attestation", "closed_trades_count")
    )
    k9_threshold = (
        config.get("verdict_min_closed_trades")
        or _safe_get(body, "p6_is_verdict_anchor", "k9_threshold")
        or _safe_get(body, "k9_and_sample_size_rules", "k9_threshold")
        or 100  # chain-wide default
    )
    if isinstance(closed_trades, int) and isinstance(k9_threshold, int) and k9_threshold > 0:
        k9_status = K9_STATUS_PASS if closed_trades >= k9_threshold else K9_STATUS_FAIL
        k9_margin = round(closed_trades / k9_threshold, 4)
    else:
        k9_status = K9_STATUS_NOT_EVALUATED
        k9_margin = None

    verdict = body.get("verdict") or body.get("lifecycle_decision") or _safe_get(body, "p6_is_verdict_anchor", "verdict")

    # DR-gate fired status: peek at common shapes
    dr_fired: dict[str, Any] = {}
    for dr in ("DR1", "DR2", "DR3", "DR4", "DR5", "DR6", "DR7", "DR8", "DR9", "DR10", "DR11", "K12"):
        for source in (k_eval, body.get("dr_gate_evaluation"), body):
            if not isinstance(source, dict):
                continue
            for k, v in source.items():
                if dr.lower() in k.lower() and isinstance(v, bool):
                    dr_fired[dr] = v
                    break
            if dr in dr_fired:
                break

    return {
        "verdict": verdict,
        "phase_verdict_raw": body.get("verdict"),
        "closed_trades": closed_trades if isinstance(closed_trades, int) else None,
        "k9_threshold": k9_threshold if isinstance(k9_threshold, int) else None,
        "k9_status": k9_status,
        "k9_margin_ratio": k9_margin,
        "net_pnl_usd": perf.get("net_pnl_usd"),
        "max_drawdown_pct": perf.get("max_drawdown_pct"),
        "sharpe_annualized": perf.get("sharpe_annualized"),
        "sharpe_proxy_per_trade": perf.get("sharpe_proxy_per_trade"),
        "expectancy_per_trade_usd": perf.get("expectancy_per_trade_usd"),
        "annual_turnover": perf.get("annual_turnover"),
        "s1_cost_drag": perf.get("s1_cost_drag_fraction"),
        "s2_cost_drag_estimate": perf.get("s2_cost_drag_fraction_estimate_for_dr10_monitor"),
        "trades_per_year_observed": perf.get("trades_per_year_observed"),
        "is_window_start": (
            scan.get("is_window_start_engine_truth")
            or _safe_get(body, "config_used", "is_window_start")
            or _safe_get(body, "is_oos_split_plan", "in_sample_window_start")
        ),
        "is_window_end": (
            scan.get("is_window_end_engine_truth")
            or _safe_get(body, "config_used", "is_window_end")
            or _safe_get(body, "is_oos_split_plan", "in_sample_window_end")
        ),
        "oos_window_start": (
            _safe_get(body, "is_oos_split_plan", "out_of_sample_window_start")
            or _safe_get(body, "config_used", "oos_window_start")
        ),
        "oos_window_end": (
            _safe_get(body, "is_oos_split_plan", "out_of_sample_window_end")
            or _safe_get(body, "config_used", "oos_window_end")
        ),
        "csv_sha_verified_at_load": scan.get("csv_sha_verified_at_load"),
        "a_gates_evaluation": a_eval if a_eval else None,
        "k_gates_evaluation": k_eval if k_eval else None,
        "dr_gates_fired": dr_fired,
    }
