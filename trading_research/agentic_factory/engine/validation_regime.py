"""Reusable regime-breakdown integration (Factory-D7 / ladder module G).

Classifies already-produced bars into volatility regimes, tags already-produced
trades by the regime they were entered in, and summarizes per-regime
concentration -- then maps that to one conservative regime-risk verdict. This
encodes the S26 lesson: an edge that lives almost entirely inside a single
volatility regime (or whose net collapses once the dominant regime is removed) is
a concentration risk, not a robust edge.

It computes NO strategy trades and fetches NO data. Bars and trades are supplied
by the caller; this layer only classifies, tags, and summarizes them.

OFFLINE / INERT: Python standard library only (typing) plus the report writer. It
opens no network connection, spawns no child process, fetches no data, runs no
shell or version-control call, reads no real market data, and does NO dynamic code
loading. It mutates nothing and writes nothing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from engine import validation_reports


# Regime-risk dispositions.
REGIME_RISK_ACCEPTABLE = "REGIME_RISK_ACCEPTABLE"
REGIME_RISK_INCONCLUSIVE = "REGIME_RISK_INCONCLUSIVE"
REGIME_RISK_CONCENTRATED = "REGIME_RISK_CONCENTRATED"
REGIME_RISK_FAIL = "REGIME_RISK_FAIL"


def _r_of(trade: Dict[str, Any]) -> float:
    """Pull the R-multiple from a trade dict (accepts 'r_multiple' or 'r')."""
    if "r_multiple" in trade:
        return float(trade["r_multiple"])
    if "r" in trade:
        return float(trade["r"])
    raise ValueError("trade dict missing 'r_multiple'/'r'")


def _percentile(sorted_vals: List[float], pct: float) -> Optional[float]:
    """Nearest-rank percentile of an already-sorted list (None when empty)."""
    if not sorted_vals:
        return None
    n = len(sorted_vals)
    k = int(round((pct / 100.0) * (n - 1)))
    k = max(0, min(n - 1, k))
    return sorted_vals[k]


def compute_is_tertiles(values: Sequence[float]) -> Dict[str, Optional[float]]:
    """Two cut points (lower 1/3, upper 2/3) of a value distribution.

    Deterministic nearest-rank percentiles. Returns {"lower", "upper"} (both None
    when there are no values), used to bucket values into low/mid/high regimes.
    """
    vals = sorted(float(v) for v in values)
    return {
        "lower": _percentile(vals, 100.0 / 3.0),
        "upper": _percentile(vals, 200.0 / 3.0),
    }


def apply_regime_thresholds(
    values: Sequence[float], thresholds: Dict[str, Optional[float]]
) -> List[str]:
    """Label each value low/mid/high by the lower/upper cut points.

    value <= lower -> "low"; value > upper -> "high"; otherwise "mid". When the
    thresholds are undefined (empty training set) every value is "unknown".
    """
    lower = thresholds.get("lower")
    upper = thresholds.get("upper")
    labels: List[str] = []
    for v in values:
        if lower is None or upper is None:
            labels.append("unknown")
        elif float(v) <= lower:
            labels.append("low")
        elif float(v) > upper:
            labels.append("high")
        else:
            labels.append("mid")
    return labels


def classify_volatility_regimes(
    bars: Sequence[Dict[str, Any]],
    atr_key: str = "atr20",
    close_key: str = "close",
    thresholds: Optional[Dict[str, Optional[float]]] = None,
) -> List[str]:
    """Per-bar low/mid/high volatility label from a normalized-ATR proxy.

    The proxy is atr/close. Bars missing the ATR or with a non-positive close are
    labelled "unknown". When `thresholds` is None they are derived from the
    in-sample tertiles of the present proxies. Returns a label per bar, aligned by
    index so the result can drive tag_trades_by_entry_regime.
    """
    proxies: List[Optional[float]] = []
    for b in bars:
        a = b.get(atr_key)
        c = b.get(close_key)
        if a is None or c in (None, 0, 0.0):
            proxies.append(None)
        else:
            proxies.append(float(a) / float(c))
    present = [p for p in proxies if p is not None]
    th = thresholds if thresholds is not None else compute_is_tertiles(present)
    labels: List[str] = []
    for p in proxies:
        if p is None:
            labels.append("unknown")
        else:
            labels.append(apply_regime_thresholds([p], th)[0])
    return labels


def tag_trades_by_entry_regime(
    trades: Sequence[Dict[str, Any]], regime_by_index: Sequence[str]
) -> List[Dict[str, Any]]:
    """Copy each trade and attach the regime of its entry bar.

    A trade carries its entry bar position in "entry_index" (or "entry_idx"). When
    the index is missing or out of range the regime is "unknown". The input trades
    are never mutated (shallow copies are returned).
    """
    out: List[Dict[str, Any]] = []
    n = len(regime_by_index)
    for t in trades:
        idx = t.get("entry_index", t.get("entry_idx"))
        tt = dict(t)
        if isinstance(idx, bool) or not isinstance(idx, int) or idx < 0 or idx >= n:
            tt["regime"] = "unknown"
        else:
            tt["regime"] = regime_by_index[idx]
        out.append(tt)
    return out


def summarize_by_regime(
    trades: Sequence[Dict[str, Any]], regime_key: str = "regime"
) -> Dict[str, Any]:
    """Per-regime trade counts / total R plus dominant-regime concentration.

    Reports the dominant regime (most trades), its share of trades and of net R,
    and `net_without_dominant` (net R with the dominant regime removed) -- the
    severe-concentration probe used by derive_regime_verdict.
    """
    by: Dict[str, Dict[str, Any]] = {}
    total = 0.0
    for t in trades:
        r = _r_of(t)
        lab = t.get(regime_key, "unknown")
        d = by.setdefault(lab, {"trade_count": 0, "total_r": 0.0})
        d["trade_count"] += 1
        d["total_r"] += r
        total += r

    n = len(list(trades))
    dominant: Optional[str] = None
    dom_count = 0
    for lab, d in by.items():
        if d["trade_count"] > dom_count:
            dom_count = d["trade_count"]
            dominant = lab

    dom_r = by[dominant]["total_r"] if dominant is not None else 0.0
    return {
        "trade_count": n,
        "total_r": total,
        "regime_count": len(by),
        "by_regime": by,
        "dominant_regime": dominant,
        "dominant_count_share": (dom_count / n) if n else 0.0,
        "dominant_r_share": (dom_r / total) if total > 0 else None,
        "net_without_dominant": total - dom_r,
    }


def derive_regime_verdict(summary: Dict[str, Any]) -> str:
    """Map a regime summary to one conservative concentration verdict.

    FAIL          -- net positive but collapses to <= 0 without the dominant
                     regime AND that regime holds >= 80% of trades (the edge lives
                     in one regime).
    CONCENTRATED  -- dominant regime holds >= 70% of trades, OR net positive but
                     <= 0 without the dominant regime (survives less severely).
    ACCEPTABLE    -- dominant share < 60%, net positive, and net stays > 0 without
                     the dominant regime.
    INCONCLUSIVE  -- otherwise, incl. no trades or a single regime present.
    """
    n = summary.get("trade_count", 0)
    regimes = summary.get("regime_count", 0)
    total = summary.get("total_r", 0.0)
    dom_share = summary.get("dominant_count_share", 0.0)
    net_wo = summary.get("net_without_dominant", 0.0)
    net_positive = total > 0

    if n == 0 or regimes <= 1:
        return REGIME_RISK_INCONCLUSIVE
    if net_positive and net_wo <= 0.0 and dom_share >= 0.80:
        return REGIME_RISK_FAIL
    if dom_share >= 0.70 or (net_positive and net_wo <= 0.0):
        return REGIME_RISK_CONCENTRATED
    if dom_share < 0.60 and net_positive and net_wo > 0.0:
        return REGIME_RISK_ACCEPTABLE
    return REGIME_RISK_INCONCLUSIVE


def build_regime_report(
    *,
    branch_id: str,
    title: str,
    summary: Dict[str, Any],
    verdict: Optional[str] = None,
    module_id: str = "regime_breakdown",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "multimarket",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema regime-breakdown report from a summary.

    The verdict defaults to derive_regime_verdict(summary); the caller may
    override. Writes nothing.
    """
    v = verdict or derive_regime_verdict(summary)
    default_forbidden = [
        "no_optimization", "no_parameter_sweeps", "no_data_fetch",
        "no_paper_or_live", "no_execution_or_api", "no_regime_cherry_picking",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=v,
        created_utc=created_utc,
        source_commits=dict(source_commits or {}),
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=dict(frozen_parameters or {}),
        metrics=dict(summary),
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )
