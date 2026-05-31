"""Offline daily crypto Crash-Candle Reversion engine (Crypto-CCR1 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/crypto_d9_crash_candle_reversion_strategy_spec/ (committed 6e0c85b).

OFFLINE / INERT: pure-Python standard library only (csv, datetime, statistics).
It never fetches, downloads, streams, or connects anywhere. It runs no
optimization and no parameter search. Every constant below is a fixed input
frozen by the Crypto-D9 spec; changing any of them requires a NEW spec id and a
fresh validation ladder, never an edit here. The core engine writes no files.

Hypothesis (Crypto-D9): a large one-day spot crypto selloff may create
short-horizon mean reversion via forced liquidation / panic selling / liquidity
recovery. Crypto-D8 proved this family has enough raw BTC event count (81 events
at -5% across 2020-2023 IS, regime-diverse) but does NOT prove an edge. This
engine only realises the frozen rules so a later, separately-authorized IS
baseline can measure whether an edge exists.

Frozen rules (Crypto-D9, CCR1 v1):
  Market      : spot only. LONG only. No shorting, no leverage, no perpetuals,
                no funding leg.
  Universe    : BTC / ETH / SOL daily candles, USD-tether quoted, UTC 00:00
                boundary. Primary symbol = BTC. The identical spec runs on all
                three with no per-symbol tuning.
  No filter   : v1 deliberately has NO trend filter (no SMA200) and NO
                confirmation filter. Crypto-D8 proved a trend filter starves BTC
                below the event-count floor (CODR-1's close>SMA200 collapsed BTC
                to 9 events); a confirmation filter risks the same. The raw
                crash candle is the entire signal.
  Crash       : ret_1d_t = close_t / close_{t-1} - 1 <= -0.05  (a -5% or worse
                one-day close-to-close drop).
  Entry       : when the crash fires on day t, enter LONG at the NEXT bar's OPEN
                (open_{t+1}). Signal uses only data through close_t; the fill is
                the next open -> no lookahead.
  Position    : one open position per symbol; NO pyramiding (new signals are
                ignored while a position is open).
  Exit        : FIXED HORIZON only -- exit at the CLOSE of the 3rd held bar. The
                entry bar counts as bar 1, so the exit index = entry_index + 2
                (if entry is open_{t+1}, exit is close_{t+3}). NO protective
                stop. NO profit target. NO intraday assumptions.
  Accounting  : fixed notional, no leverage, no intra-test compounding; per-trade
                return_pct = exit_price / entry_price - 1 (GROSS). Friction is
                NOT applied in this engine -- it is a separate later validation /
                report layer (0.30% base, 0.45% stress), mirroring how the
                futures factory separates friction from the raw engine.

RESOLVED INTERPRETATIONS (the conservative reading):
  * ret_1d_0 is None (no prior close); the first bar can never be a crash day.
  * "Adjacent" -> adjacency in the time-sorted bar list. Calendar gap detection
    is the data-QA layer's job (the snapshot is already QA-clean); the engine
    treats adjacent sorted bars as consecutive and never fabricates bars.
  * data_end: if the dataset ends before the 3-bar horizon completes, the open
    trade is marked-to-market at the last available close with exit_reason
    "data_end". This is a boundary artifact, never a normal exit, and is
    reported explicitly rather than hidden. The frozen IS slice ends at the
    2023-12-31 close, so a late-IS entry exits data_end there -- no later bar is
    ever read.
  * After a trade exits at bar X, the next eligible signal day is t >= X (no
    overlap, since the prior trade is flat at close[X]).

Lookahead safety: ret_1d reads only data through close_t; the entry fill is
open_{t+1}; the exit reads only the held bars' own closes. Nothing reads a
future bar relative to its own decision point.
"""

from __future__ import annotations

import csv
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen Crypto-D9 constants (NOT tunable).
CRASH_TRIGGER = -0.05       # entry crash: one-day close-to-close return threshold
HOLD_BARS = 3               # fixed holding horizon (entry bar counts as bar 1)
DIRECTION = "long_spot"     # v1 direction invariant (no shorts, no perps)

ACCOUNTING_NOTE = (
    "long-only spot; enter at open_{t+1} after ret_1d_t<=-5%; no trend filter; "
    "no confirmation filter; one position per symbol; no pyramiding; fixed exit "
    "at the close of the 3rd held bar (no stop, no profit target); per-trade "
    "return_pct is GROSS (friction applied in a later validation layer); no "
    "leverage; no compounding"
)

EXIT_REASONS = ("time_exit", "data_end")


def daily_return_pct(bars: List[Dict[str, Any]]) -> List[Optional[float]]:
    """Close-to-close daily return; ret[k] = close[k]/close[k-1]-1, ret[0]=None."""
    n = len(bars)
    out: List[Optional[float]] = [None] * n
    for k in range(1, n):
        prev_c = bars[k - 1]["close"]
        if isinstance(prev_c, (int, float)) and prev_c > 0:
            out[k] = bars[k]["close"] / prev_c - 1.0
    return out


def is_crash_candle(ret_t: Optional[float]) -> bool:
    """Crash trigger: True iff the one-day return is <= -5% (CRASH_TRIGGER)."""
    return ret_t is not None and ret_t <= CRASH_TRIGGER


def _date_of(bar: Dict[str, Any]) -> Optional[str]:
    ts = bar.get("timestamp")
    return str(ts.date()) if isinstance(ts, datetime) else None


def find_entries(
    bars: List[Dict[str, Any]],
    returns: Optional[List[Optional[float]]] = None,
) -> List[int]:
    """Raw signal indices t where a crash fires AND a next bar exists to fill.

    This is the position-agnostic candidate list (it does NOT apply the
    one-position / no-pyramiding rule -- that is simulate_crash_reversion's job).
    """
    if returns is None:
        returns = daily_return_pct(bars)
    n = len(bars)
    signals: List[int] = []
    for t in range(n):
        if t + 1 >= n:
            break  # need open_{t+1} to fill the entry
        if is_crash_candle(returns[t]):
            signals.append(t)
    return signals


def simulate_crash_reversion(
    bars: List[Dict[str, Any]], symbol: str = "UNKNOWN"
) -> List[Dict[str, Any]]:
    """Deterministic CCR1 simulation over one symbol's sorted daily bars.

    Enforces one-position-per-symbol and no pyramiding. Returns a list of trade
    dicts. Pure, no I/O, no randomness.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n < 2:
        return trades
    ret = daily_return_pct(bars)

    t = 0
    while t < n:
        if t + 1 >= n:
            break  # no next bar to fill -> no further entries possible
        if not is_crash_candle(ret[t]):
            t += 1
            continue

        entry_index = t + 1
        entry_price = bars[entry_index]["open"]
        target_exit = entry_index + HOLD_BARS - 1   # close of the 3rd held bar

        if target_exit <= n - 1:
            exit_index, exit_reason = target_exit, "time_exit"
        else:                                        # data ended before horizon
            exit_index, exit_reason = n - 1, "data_end"

        exit_price = bars[exit_index]["close"]
        return_pct = exit_price / entry_price - 1.0
        trades.append({
            "symbol": symbol,
            "direction": DIRECTION,
            "signal_index": t,
            "signal_date": _date_of(bars[t]),
            "entry_index": entry_index,
            "entry_date": _date_of(bars[entry_index]),
            "exit_index": exit_index,
            "exit_date": _date_of(bars[exit_index]),
            "entry_price": entry_price,
            "exit_price": exit_price,
            "return_pct": return_pct,
            "exit_reason": exit_reason,
            "hold_bars": exit_index - entry_index + 1,
        })
        t = exit_index  # no pyramiding: next eligible signal day is the exit bar
    return trades


def summarize(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Inert distribution summary over a list of CCR1 trades (gross returns)."""
    rets = [tr["return_pct"] for tr in trades]
    n = len(rets)
    per_symbol: Dict[str, int] = {}
    exit_breakdown: Dict[str, int] = {}
    for tr in trades:
        per_symbol[tr["symbol"]] = per_symbol.get(tr["symbol"], 0) + 1
        exit_breakdown[tr["exit_reason"]] = exit_breakdown.get(tr["exit_reason"], 0) + 1
    if n == 0:
        return {
            "trade_count": 0,
            "total_return_pct": 0.0,
            "average_return_pct": 0.0,
            "median_return_pct": 0.0,
            "win_rate": 0.0,
            "profit_factor": None,
            "average_hold_bars": 0.0,
            "per_symbol": per_symbol,
            "exit_reason_counts": exit_breakdown,
        }
    gross_win = sum(r for r in rets if r > 0)
    gross_loss = -sum(r for r in rets if r < 0)
    return {
        "trade_count": n,
        "total_return_pct": sum(rets),
        "average_return_pct": sum(rets) / n,
        "median_return_pct": statistics.median(rets),
        "win_rate": sum(1 for r in rets if r > 0) / n,
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else None,
        "average_hold_bars": sum(tr["hold_bars"] for tr in trades) / n,
        "per_symbol": per_symbol,
        "exit_reason_counts": exit_breakdown,
    }


def anti_top3_gate(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Frozen hard gate: net gross return must stay POSITIVE ex the top 3 winners.

    The direct guard against the universal parked-branch failure (a thin net
    propped up by a handful of fat-tail winners). Pure accounting; no I/O.
    """
    rets = sorted((tr["return_pct"] for tr in trades), reverse=True)
    n = len(rets)
    net = sum(rets)
    net_ex_top3 = sum(rets[3:])
    return {
        "trade_count": n,
        "net_return_pct": net,
        "top3_return_pct": sum(rets[:3]),
        "net_ex_top3_return_pct": net_ex_top3,
        "passes_ex_top3": net_ex_top3 > 0.0,
    }


def load_daily_bars(
    csv_path: str, timestamp_column: str = "timestamp"
) -> List[Dict[str, Any]]:
    """Load daily OHLCV bars from a local spot daily CSV. Offline read only.

    Expects the frozen-snapshot schema timestamp,open,high,low,close,volume.
    Sorted by time. No network, no fetch. NOT used by the synthetic test suite.
    """
    bars: List[Dict[str, Any]] = []
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header_map = {h.lower(): h for h in (reader.fieldnames or [])}
        ts_key = header_map.get(timestamp_column.lower(), timestamp_column)
        vol_key = header_map.get("volume")
        for row in reader:
            ts_raw = row.get(ts_key)
            if ts_raw is None:
                continue
            bars.append({
                "timestamp": datetime.fromisoformat(ts_raw.strip()),
                "open": float(row[header_map["open"]]),
                "high": float(row[header_map["high"]]),
                "low": float(row[header_map["low"]]),
                "close": float(row[header_map["close"]]),
                "volume": float(row[vol_key]) if vol_key else 0.0,
            })
    bars.sort(key=lambda b: b["timestamp"])
    return bars


def run_backtest(
    csv_path: str, symbol: str = "UNKNOWN", timestamp_column: str = "timestamp"
) -> Dict[str, Any]:
    """Run CCR1 over a local CSV and return inert data. NOT used in tests."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate_crash_reversion(bars, symbol=symbol)
    return {
        "bars_loaded": len(bars),
        "trades": trades,
        "summary": summarize(trades),
        "anti_top3_gate": anti_top3_gate(trades),
        "accounting": ACCOUNTING_NOTE,
    }
