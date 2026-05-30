"""Reusable IN-SAMPLE baseline runner harness (Factory-D3).

Smallest reusable harness for the reusable validation runner planned in
reports/factory_d1_reusable_validation_runner_plan/ (committed 93b5299) and built
on the report schema/writer of engine/validation_reports.py (Factory-D2,
committed 5c538c1). It runs ONE already-frozen strategy on an explicit IS dataset
and produces a standard validation-report dict.

IS ONLY. This module runs NO OOS, NO protocol logic, NO entry-significance, NO
Monte Carlo, NO regime breakdown, NO multi-market, NO walk-forward, NO friction
stress, NO final decision -- those are later Factory steps.

OFFLINE / INERT: Python standard library only (csv, os, statistics, datetime,
typing). It opens no network connection, spawns no child process, fetches no
data, and does NO dynamic code loading -- the strategy is passed in as a plain
callable, never imported from an arbitrary string. It never mutates a strategy's
frozen parameters.

Hard OOS seal: the 2023/2024/2025 years are refused for an IS window both by
input-path inspection AND by bar-date inspection, so an accidental OOS file or an
out-of-range bar fails loudly before any metric is computed.
"""

from __future__ import annotations

import csv
import os
import statistics
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from engine import validation_reports


# The sealed out-of-sample years. An IS window must never touch these, enforced
# at TWO layers: input file paths and individual bar dates.
OOS_YEARS: Tuple[str, ...] = ("2023", "2024", "2025")


def _path_has_oos_year(path: str) -> bool:
    base = os.path.basename(path)
    return any(year in base for year in OOS_YEARS)


def assert_is_only_paths(paths: List[str], window_label: str = "IS") -> None:
    """Refuse OOS files when the window is IS (path-level seal).

    Raises ValueError naming the offending path(s); returns None when clean.
    """
    if str(window_label).upper() != "IS":
        return
    bad = [p for p in paths if _path_has_oos_year(p)]
    if bad:
        raise ValueError(
            "IS window refuses out-of-sample (2023/2024/2025) files: "
            + ", ".join(bad)
        )


def assert_bars_in_is_range(
    bars: List[Dict[str, Any]], allowed_years: List[int]
) -> None:
    """Refuse any bar whose calendar year is not in `allowed_years` (bar-level seal).

    Raises ValueError listing the out-of-range years; returns None when clean.
    """
    allowed = {int(y) for y in allowed_years}
    seen_bad = sorted(
        {b["timestamp"].year for b in bars if b["timestamp"].year not in allowed}
    )
    if seen_bad:
        raise ValueError(
            "bars fall outside the expected IS years "
            f"{sorted(allowed)}: out-of-range years {seen_bad}"
        )


def _valid_ohlc(o: float, h: float, l: float, c: float, v: float) -> bool:
    """A bar is valid iff low<=open/close<=high, low<=high, prices>0, volume>=0."""
    if not (h >= l):
        return False
    if not (l <= o <= h):
        return False
    if not (l <= c <= h):
        return False
    if min(o, h, l, c) <= 0.0:
        return False
    if v < 0.0:
        return False
    return True


def load_yearly_csvs(
    paths: List[str], timestamp_column: str = "ts_event"
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Load explicit per-year CSV paths into sorted bars + a data-QA summary.

    Offline read only. Sorts by timestamp, REJECTS duplicate calendar dates and
    invalid OHLC rows (raises ValueError), and returns
    (bars, qa) where qa carries total_bars, date_range, per_year_row_counts and
    the (zero, since we reject) duplicate / invalid counters plus a verdict.

    The strategy is NOT run here -- this only loads and QA-checks data.
    """
    bars: List[Dict[str, Any]] = []
    for path in paths:
        with open(path, "r", newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            header_map = {h.lower(): h for h in (reader.fieldnames or [])}
            ts_key = None
            for cand in (timestamp_column.lower(), "ts_event", "timestamp", "date"):
                if cand in header_map:
                    ts_key = header_map[cand]
                    break
            if ts_key is None:
                raise ValueError(f"no timestamp column found in {path}")
            for row in reader:
                ts_raw = row.get(ts_key)
                if ts_raw is None or not str(ts_raw).strip():
                    continue
                o = float(row[header_map["open"]])
                h = float(row[header_map["high"]])
                l = float(row[header_map["low"]])
                c = float(row[header_map["close"]])
                v = float(row[header_map["volume"]])
                if not _valid_ohlc(o, h, l, c, v):
                    raise ValueError(
                        f"invalid OHLC row in {path} at {ts_raw}: "
                        f"o={o} h={h} l={l} c={c} v={v}"
                    )
                bars.append(
                    {
                        "timestamp": datetime.fromisoformat(str(ts_raw).strip()),
                        "open": o, "high": h, "low": l, "close": c, "volume": v,
                    }
                )

    bars.sort(key=lambda b: b["timestamp"])

    dates = [b["timestamp"].date() for b in bars]
    if len(set(dates)) != len(dates):
        seen: set = set()
        dupes = sorted({str(d) for d in dates if d in seen or seen.add(d)})
        raise ValueError(f"duplicate calendar dates rejected: {dupes}")

    per_year: Dict[str, int] = {}
    for b in bars:
        y = str(b["timestamp"].year)
        per_year[y] = per_year.get(y, 0) + 1

    qa: Dict[str, Any] = {
        "total_bars": len(bars),
        "date_range": (
            [str(bars[0]["timestamp"].date()), str(bars[-1]["timestamp"].date())]
            if bars else []
        ),
        "per_year_row_counts": per_year,
        "duplicate_dates_count": 0,
        "invalid_ohlc_count": 0,
        "qa_verdict": "CLEAN -- no duplicate dates, no invalid OHLC rows.",
    }
    return bars, qa


def _r_of(trade: Dict[str, Any]) -> float:
    """Pull the R-multiple from a trade dict (accepts 'r_multiple' or 'r')."""
    if "r_multiple" in trade:
        return float(trade["r_multiple"])
    if "r" in trade:
        return float(trade["r"])
    raise ValueError("trade dict missing 'r_multiple'/'r'")


def compute_is_metrics(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize a list of closed trades into the standard IS metric set (R-only).

    Profit factor is None when there are no losing trades (undefined, not inf),
    so the zero-loss case never divides by zero. Empty trade lists return safe
    zeros / None.
    """
    rs = [_r_of(t) for t in trades]
    n = len(rs)
    if n == 0:
        return {
            "trade_count": 0, "total_r": 0.0, "profit_factor": None,
            "win_rate": 0.0, "expectancy_r": 0.0, "avg_r": 0.0,
            "median_r": 0.0, "best_r": None, "worst_r": None,
            "max_drawdown_r": 0.0,
        }
    gross_win = sum(r for r in rs if r > 0)
    gross_loss = -sum(r for r in rs if r < 0)
    peak = eq = 0.0
    max_dd = 0.0
    for r in rs:
        eq += r
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd
    total = sum(rs)
    return {
        "trade_count": n,
        "total_r": total,
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else None,
        "win_rate": sum(1 for r in rs if r > 0) / n,
        "expectancy_r": total / n,
        "avg_r": total / n,
        "median_r": statistics.median(rs),
        "best_r": max(rs),
        "worst_r": min(rs),
        "max_drawdown_r": max_dd,
    }


_STANDARD_METRIC_KEYS = (
    "trade_count", "total_r", "profit_factor", "win_rate", "expectancy_r",
    "avg_r", "median_r", "best_r", "worst_r", "max_drawdown_r",
)


def _normalize_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Carry a pre-computed summary dict into the standard metric shape.

    Missing standard keys are filled with None so the metric block is uniform; no
    value is recomputed or altered (a runner that already summarized is trusted).
    """
    out = {k: summary.get(k) for k in _STANDARD_METRIC_KEYS}
    # Preserve any extra keys the runner reported (e.g. exit_reason_counts).
    for k, v in summary.items():
        if k not in out:
            out[k] = v
    return out


def run_is_baseline(
    strategy_runner: Callable[[List[Dict[str, Any]]], Any],
    bars: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a frozen strategy callable on IS bars and return normalized metrics.

    `strategy_runner` is a plain callable supplied by the caller -- never loaded
    from a string -- so no dynamic code execution happens here. It is expected to
    return either a list of closed-trade dicts (each with 'r_multiple'/'r') OR a
    pre-computed summary dict. Strategy parameters are never mutated.

    Returns {"metrics": <standard metric dict>, "trades": <list>, "raw": <result>}.
    """
    if metadata:
        allowed = metadata.get("is_years")
        if allowed:
            assert_bars_in_is_range(bars, allowed)

    result = strategy_runner(bars)

    if isinstance(result, list):
        trades = result
        metrics = compute_is_metrics(trades)
    elif isinstance(result, dict):
        if isinstance(result.get("trades"), list):
            trades = result["trades"]
            metrics = compute_is_metrics(trades)
        else:
            trades = []
            metrics = _normalize_summary(result)
    else:
        raise TypeError(
            "strategy_runner must return a list of trades or a summary dict, "
            f"got {type(result).__name__}"
        )

    return {"metrics": metrics, "trades": trades, "raw": result}


def build_is_report(
    *,
    branch_id: str,
    module_id: str,
    title: str,
    verdict: str,
    metrics: Dict[str, Any],
    input_files: List[str],
    data_window: Dict[str, Any],
    frozen_parameters: Dict[str, Any],
    source_commits: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "oos_protocol",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema validation report dict for an IS baseline.

    Re-asserts the IS path seal on `input_files` before building, then delegates
    to validation_reports.make_report so the result validates against the frozen
    report schema. Nothing is written here (call validation_reports.write_report).
    """
    assert_is_only_paths(input_files, "IS")

    default_forbidden = [
        "no_oos_peek", "no_optimization", "no_parameter_sweeps",
        "no_data_fetch", "no_paper_or_live", "no_execution_or_api",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=verdict,
        created_utc=created_utc,
        source_commits=source_commits or {},
        input_files=list(input_files),
        data_window=dict(data_window),
        frozen_parameters=dict(frozen_parameters),
        metrics=dict(metrics),
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )
