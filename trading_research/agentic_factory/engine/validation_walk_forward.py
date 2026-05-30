"""Reusable walk-forward / rolling-window stability integration (Factory-D7).

Ladder module I (walk_forward): break an already-produced trade record into
year-by-year and rolling 3yr / 5yr windows and surface shared weak windows. This
encodes the S26 lesson: a record that lives entirely in one stretch of years (the
post-2016 trend) is fragile even when the headline net is positive.

It computes NO strategy trades and fetches NO data. Trades are supplied by the
caller, each carrying its entry year; this layer only filters, groups, and
summarizes them.

OFFLINE / INERT: Python standard library only (typing) plus the report writer. It
opens no network connection, spawns no child process, fetches no data, runs no
shell or version-control call, reads no real market data, and does NO dynamic code
loading. It mutates nothing and writes nothing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from engine import validation_reports


# Walk-forward dispositions.
WALK_FORWARD_STABLE = "WALK_FORWARD_STABLE"
WALK_FORWARD_INCONCLUSIVE = "WALK_FORWARD_INCONCLUSIVE"
WALK_FORWARD_FRAGILE = "WALK_FORWARD_FRAGILE"
WALK_FORWARD_FAIL = "WALK_FORWARD_FAIL"


def _r_of(trade: Dict[str, Any]) -> float:
    """Pull the R-multiple from a trade dict (accepts 'r_multiple' or 'r')."""
    if "r_multiple" in trade:
        return float(trade["r_multiple"])
    if "r" in trade:
        return float(trade["r"])
    raise ValueError("trade dict missing 'r_multiple'/'r'")


def _trade_year(trade: Dict[str, Any]) -> int:
    """Read a trade's entry year ('year'/'entry_year', or a timestamp .year)."""
    if "year" in trade:
        return int(trade["year"])
    if "entry_year" in trade:
        return int(trade["entry_year"])
    ts = trade.get("timestamp", trade.get("entry_time"))
    if ts is not None and hasattr(ts, "year"):
        return int(ts.year)
    raise ValueError("trade dict missing 'year'/'entry_year'/timestamp")


def filter_trades_by_year_range(
    trades: Sequence[Dict[str, Any]], start_year: int, end_year: int
) -> List[Dict[str, Any]]:
    """Return trades whose entry year is within [start_year, end_year]."""
    return [t for t in trades if start_year <= _trade_year(t) <= end_year]


def summarize_year_by_year(trades: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Per-year trade counts / total R plus positive / negative year tallies."""
    by: Dict[int, Dict[str, Any]] = {}
    total = 0.0
    for t in trades:
        y = _trade_year(t)
        r = _r_of(t)
        d = by.setdefault(y, {"trade_count": 0, "total_r": 0.0})
        d["trade_count"] += 1
        d["total_r"] += r
        total += r
    years = sorted(by)
    return {
        "by_year": {str(y): by[y] for y in years},
        "years": years,
        "year_count": len(years),
        "positive_years": sum(1 for y in years if by[y]["total_r"] > 0),
        "negative_years": sum(1 for y in years if by[y]["total_r"] < 0),
        "total_r": total,
    }


def rolling_windows(
    start_year: int, end_year: int, window_size: int
) -> List[Tuple[int, int]]:
    """Inclusive rolling windows of `window_size` years, stepping by one year.

    e.g. (2013, 2022, 3) -> [(2013,2015), (2014,2016), ..., (2020,2022)].
    Returns [] for a non-positive window or an inverted range.
    """
    if window_size <= 0 or end_year < start_year:
        return []
    out: List[Tuple[int, int]] = []
    s = start_year
    while s + window_size - 1 <= end_year:
        out.append((s, s + window_size - 1))
        s += 1
    return out


def summarize_rolling_windows(
    trades: Sequence[Dict[str, Any]],
    start_year: int,
    end_year: int,
    window_size: int,
) -> Dict[str, Any]:
    """Total R / trade count per rolling window + the positive-window share.

    Each window aggregates the per-year totals it spans. `positive_window_share`
    is computed over windows that actually contain trades (empty windows are not
    counted for or against). `negative_windows` lists the losing windows so a
    shared weak stretch is visible.
    """
    wins = rolling_windows(start_year, end_year, window_size)
    yby = summarize_year_by_year(trades)["by_year"]
    net_total = sum(d["total_r"] for d in yby.values())

    windows: List[Dict[str, Any]] = []
    for (a, b) in wins:
        tot = 0.0
        cnt = 0
        for y in range(a, b + 1):
            d = yby.get(str(y))
            if d:
                tot += d["total_r"]
                cnt += d["trade_count"]
        windows.append(
            {"start": a, "end": b, "trade_count": cnt,
             "total_r": tot, "net_positive": tot > 0}
        )

    with_trades = [w for w in windows if w["trade_count"] > 0]
    pos = sum(1 for w in with_trades if w["total_r"] > 0)
    share = (pos / len(with_trades)) if with_trades else None
    return {
        "window_size": window_size,
        "window_count": len(windows),
        "windows": windows,
        "windows_with_trades": len(with_trades),
        "positive_window_share": share,
        "negative_windows": [
            {"start": w["start"], "end": w["end"], "total_r": w["total_r"]}
            for w in with_trades if w["total_r"] <= 0
        ],
        "net_total_r": net_total,
    }


def derive_walk_forward_verdict(summary: Dict[str, Any]) -> str:
    """Map a rolling-window summary to one conservative stability verdict.

    FAIL         -- half or more of the populated windows are non-positive.
    STABLE       -- at least 80% of populated windows are positive.
    FRAGILE      -- in between (a meaningful minority of windows lose).
    INCONCLUSIVE -- fewer than two populated windows / no measurable share.
    """
    with_trades = summary.get("windows_with_trades", 0)
    share = summary.get("positive_window_share")
    if with_trades < 2 or share is None:
        return WALK_FORWARD_INCONCLUSIVE
    if share <= 0.50:
        return WALK_FORWARD_FAIL
    if share >= 0.80:
        return WALK_FORWARD_STABLE
    return WALK_FORWARD_FRAGILE


def build_walk_forward_report(
    *,
    branch_id: str,
    title: str,
    summary: Dict[str, Any],
    verdict: Optional[str] = None,
    module_id: str = "walk_forward",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "friction_stress",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema walk-forward report from a summary.

    The verdict defaults to derive_walk_forward_verdict(summary); the caller may
    override. The window size is frozen into frozen_parameters. Writes nothing.
    """
    v = verdict or derive_walk_forward_verdict(summary)
    frozen = dict(frozen_parameters or {})
    frozen.setdefault("window_size", summary.get("window_size"))

    default_forbidden = [
        "no_optimization", "no_parameter_sweeps", "no_data_fetch",
        "no_paper_or_live", "no_execution_or_api", "no_window_cherry_picking",
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
        frozen_parameters=frozen,
        metrics=dict(summary),
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )
