"""Offline daily crypto CODR-1 engine (Crypto Oversold-Dip Reversion in Uptrend v1).

Implements EXACTLY the frozen rules pre-registered in
reports/crypto_d4_first_strategy_spec/ (committed 5552356).

OFFLINE / INERT: pure-Python standard library only (csv, datetime, statistics).
It never fetches, downloads, streams, or connects anywhere. It runs no
optimization and no parameter search. Every constant below is a fixed input
frozen by the Crypto-D4 spec; changing any of them requires a NEW spec id and a
fresh validation ladder, never an edit here. The core engine writes no files.

Hypothesis (Crypto-D4): inside an established uptrend, an outsized one-day drop
in a crypto spot market is an overreaction that tends to revert over the next
few days. The edge, if real, must come from MANY small repeated dip-reversion
trades whose winners are capped by a fixed holding horizon -- not from a few
large trend captures. That capped-winner property is the structural antidote to
the top-3-winner dependence that parked every prior branch.

Frozen rules (Crypto-D4, CODR-1 v1):
  Market      : spot only. LONG only. No shorting, no leverage, no perpetuals,
                no funding leg.
  Universe    : BTC / ETH / SOL daily candles, USD-tether quoted, UTC 00:00
                boundary. Primary symbol = BTC. The identical spec runs on all
                three with no per-symbol tuning.
  Trend filter: close_t > SMA200_t  (200-day simple moving average of close).
  Shock       : ret_t = close_t / close_{t-1} - 1 <= -0.07  (a -7% or worse day).
  Entry       : when BOTH the trend filter and the shock fire on day t, enter
                LONG at the NEXT bar's OPEN (open_{t+1}). Signal uses only data
                through close_t; the fill is the next open -> no lookahead.
  Position    : one open position per symbol; NO pyramiding (new signals are
                ignored while a position is open).
  Exit        : (a) PROTECTIVE STOP -- if a daily close is <= entry_fill * 0.90
                (-10% from entry on a close basis), exit at that close;
                (b) otherwise TIME STOP -- exit at the CLOSE of the 5th held bar
                (the entry bar counts as bar 1, so exit index = entry_index + 4);
                (c) the protective stop takes precedence when both could trigger
                on the same bar (it is checked first).
                NO profit target in v1.
  Accounting  : fixed notional, no leverage, no intra-test compounding; per-trade
                return_pct = exit_price / entry_price - 1 (GROSS). Friction is
                NOT applied in this engine -- it is a separate later validation
                layer (Crypto-D14 / friction module), mirroring how the futures
                factory separates friction from the raw engine. r_like_return is
                return_pct expressed in units of the -10% stop risk
                (return_pct / 0.10).

RESOLVED INTERPRETATIONS (the conservative reading):
  * SMA200 warmup: SMA200_t is None for t < 199, so no entry can fire until at
    least 200 bars of history exist (the trend filter is False while warming).
  * ret_0 is None (no prior close); the first bar can never be a shock day.
  * "Consecutive sessions" -> adjacency in the time-sorted bar list. Calendar
    gap detection is the data-QA layer's job (the snapshot is already QA-clean,
    0 missing calendar days); the engine treats adjacent sorted bars as
    consecutive and never fabricates bars.
  * The protective stop is evaluated from the entry bar's own close onward (the
    dip can keep falling on the entry day).
  * data_end: if the dataset ends before the 5-bar horizon completes and no stop
    fired, the open trade is marked-to-market at the last available close with
    exit_reason "data_end". This is a boundary artifact, never a normal exit, and
    is reported explicitly rather than hidden.
  * After a trade exits at bar X, the next eligible signal day is t >= X (no
    overlap, since the prior trade is flat at close[X]).

Lookahead safety: SMA200 and ret read only data through close_t; the entry fill
is open_{t+1}; exits read only the held bars' own closes. Nothing reads a future
bar relative to its own decision point.
"""

from __future__ import annotations

import csv
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen Crypto-D4 constants (NOT tunable).
SMA_PERIOD = 200            # trend-filter lookback (200-day SMA of close)
SHOCK_TRIGGER = -0.07       # entry shock: one-day close-to-close return threshold
STOP_LEVEL = -0.10          # protective stop: close return from entry fill
TIME_STOP_BARS = 5          # fixed holding horizon (entry bar counts as bar 1)
DIRECTION = "long_spot"     # v1 direction invariant (no shorts, no perps)

ACCOUNTING_NOTE = (
    "long-only spot; enter at open_{t+1} after close_t>SMA200 and ret_t<=-7%; "
    "one position per symbol; no pyramiding; protective close-stop at -10% "
    "(precedence) else time stop at close of the 5th held bar; no profit target; "
    "per-trade return_pct is GROSS (friction applied in a later validation "
    "layer); r_like_return = return_pct / 0.10; no leverage; no compounding"
)

EXIT_REASONS = ("protective_stop", "time_stop", "data_end")


def sma(values: List[float], period: int = SMA_PERIOD) -> List[Optional[float]]:
    """Simple moving average aligned to values; out[k] uses values[k-period+1..k].

    out[k] is None until the window is warm (k < period-1). Pure, no I/O.
    """
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period <= 0:
        return out
    running = 0.0
    for k in range(n):
        running += values[k]
        if k >= period:
            running -= values[k - period]
        if k >= period - 1:
            out[k] = running / period
    return out


def daily_return_pct(bars: List[Dict[str, Any]]) -> List[Optional[float]]:
    """Close-to-close daily return; ret[k] = close[k]/close[k-1]-1, ret[0]=None."""
    n = len(bars)
    out: List[Optional[float]] = [None] * n
    for k in range(1, n):
        prev_c = bars[k - 1]["close"]
        if isinstance(prev_c, (int, float)) and prev_c > 0:
            out[k] = bars[k]["close"] / prev_c - 1.0
    return out


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays aligned to bars. Pure, no I/O."""
    closes = [b["close"] for b in bars]
    return {"sma200": sma(closes, SMA_PERIOD), "ret": daily_return_pct(bars)}


def is_uptrend(close_t: Optional[float], sma_t: Optional[float]) -> bool:
    """Trend filter: True iff SMA200 is warm and close_t strictly exceeds it."""
    return (
        isinstance(close_t, (int, float))
        and sma_t is not None
        and close_t > sma_t
    )


def is_oversold_dip(ret_t: Optional[float]) -> bool:
    """Shock trigger: True iff the one-day return is <= -7% (SHOCK_TRIGGER)."""
    return ret_t is not None and ret_t <= SHOCK_TRIGGER


def find_entries(
    bars: List[Dict[str, Any]],
    indicators: Optional[Dict[str, List[Optional[float]]]] = None,
) -> List[int]:
    """Raw signal indices t where BOTH filters fire AND a next bar exists to fill.

    This is the position-agnostic candidate list (it does NOT apply the
    one-position / no-pyramiding rule -- that is simulate_codr1's job).
    """
    if indicators is None:
        indicators = compute_indicators(bars)
    sma200 = indicators["sma200"]
    ret = indicators["ret"]
    n = len(bars)
    signals: List[int] = []
    for t in range(n):
        if t + 1 >= n:
            break  # need open_{t+1} to fill the entry
        if is_uptrend(bars[t]["close"], sma200[t]) and is_oversold_dip(ret[t]):
            signals.append(t)
    return signals


def _date_of(bar: Dict[str, Any]) -> Optional[str]:
    ts = bar.get("timestamp")
    return str(ts.date()) if isinstance(ts, datetime) else None


def simulate_codr1(
    bars: List[Dict[str, Any]], symbol: str = "UNKNOWN"
) -> List[Dict[str, Any]]:
    """Deterministic CODR-1 simulation over one symbol's sorted daily bars.

    Enforces one-position-per-symbol and no pyramiding. Returns a list of trade
    dicts. Pure, no I/O, no randomness.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n < 2:
        return trades
    ind = compute_indicators(bars)
    sma200 = ind["sma200"]
    ret = ind["ret"]

    t = 0
    while t < n:
        if t + 1 >= n:
            break  # no next bar to fill -> no further entries possible
        if not (is_uptrend(bars[t]["close"], sma200[t]) and is_oversold_dip(ret[t])):
            t += 1
            continue

        entry_index = t + 1
        entry_price = bars[entry_index]["open"]
        last_index = min(entry_index + TIME_STOP_BARS - 1, n - 1)

        exit_index: Optional[int] = None
        exit_reason: Optional[str] = None
        j = entry_index
        while j <= last_index:
            close_ret_from_entry = bars[j]["close"] / entry_price - 1.0
            if close_ret_from_entry <= STOP_LEVEL:           # (a) stop, checked first
                exit_index, exit_reason = j, "protective_stop"
                break
            if j == entry_index + TIME_STOP_BARS - 1:        # (b) time stop on bar 5
                exit_index, exit_reason = j, "time_stop"
                break
            j += 1
        if exit_index is None:                               # (c) data ended early
            exit_index, exit_reason = last_index, "data_end"

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
            "r_like_return": return_pct / abs(STOP_LEVEL),
            "exit_reason": exit_reason,
            "hold_bars": exit_index - entry_index + 1,
        })
        t = exit_index  # no pyramiding: next eligible signal day is the exit bar
    return trades


def summarize(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Inert distribution summary over a list of CODR-1 trades (gross returns)."""
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
    """Run CODR-1 over a local CSV and return inert data. NOT used in tests."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate_codr1(bars, symbol=symbol)
    return {
        "bars_loaded": len(bars),
        "trades": trades,
        "summary": summarize(trades),
        "anti_top3_gate": anti_top3_gate(trades),
        "accounting": ACCOUNTING_NOTE,
    }
