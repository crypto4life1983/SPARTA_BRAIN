"""Offline daily Donchian System-1 (no-pyramid) baseline for the NQ-only slice.

OFFLINE / CSV-ONLY: reads daily OHLCV bars from a local CSV only. It never
fetches, downloads, streams, or connects anywhere. Python standard library only
(csv, datetime). It runs no optimization and no parameter search; parameters are
fixed inputs.

Strategy (per strategies/donchian_nq_daily/strategy_spec.md):
  - entry_channel = 55, exit_channel = 20 (daily bars)
  - LONG  when a bar's high breaks the prior `entry_channel`-day high
  - SHORT when a bar's low  breaks the prior `entry_channel`-day low
  - exit LONG  when a bar's low  breaks the prior `exit_channel`-day low
  - exit SHORT when a bar's high breaks the prior `exit_channel`-day high
  - hard stop = stop_n_multiple * N, N = Wilder ATR(atr_period) as of the prior bar
  - no pyramiding: at most one open unit at a time (max_units_per_market = 1)

ACCOUNTING — READ THIS: results are expressed in R-multiples where 1R = the
initial 2N stop distance (requirement 6: "R = pnl divided by initial stop
distance"). This is a SIMPLIFIED 2N-stop R baseline. It does NOT model dollar
sizing, point value, contract multiplier, roll, or commissions/slippage, and it
is therefore **NOT a reproduction of the S10-D2 result** (which used full
ATR/dollar sizing on a 4-market portfolio). Do not compare its numbers to the
old report's dollar figures.

Lookahead safety: all channel levels and N use PRIOR bars only (never the
current bar). Position management starts on the bar AFTER entry; the entry bar
does not also exit (conservative simplification). Within a single bar, the hard
stop is checked BEFORE the channel exit (conservative worst-case ordering).
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Dict, List, Optional

ACCOUNTING_NOTE = (
    "simplified_2N_stop_R_baseline; no dollar sizing / point value / cost / roll; "
    "NOT an S10-D2 reproduction"
)


def load_daily_bars(
    csv_path: str, timestamp_column: str = "ts_event"
) -> List[Dict[str, Any]]:
    """Load daily OHLC bars from a local CSV. Offline read only, sorted by time."""
    bars: List[Dict[str, Any]] = []
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header_map = {h.lower(): h for h in (reader.fieldnames or [])}
        ts_key = header_map.get(timestamp_column.lower(), timestamp_column)
        for row in reader:
            ts_raw = row.get(ts_key)
            if ts_raw is None:
                continue
            bars.append(
                {
                    "timestamp": datetime.fromisoformat(ts_raw.strip()),
                    "open": float(row[header_map["open"]]),
                    "high": float(row[header_map["high"]]),
                    "low": float(row[header_map["low"]]),
                    "close": float(row[header_map["close"]]),
                }
            )
    bars.sort(key=lambda b: b["timestamp"])
    return bars


def _highest_high(bars: List[Dict[str, Any]], end: int, window: int) -> Optional[float]:
    """Max high over bars[end-window:end] (PRIOR bars only). None if not enough."""
    if window <= 0 or end - window < 0:
        return None
    return max(b["high"] for b in bars[end - window:end])


def _lowest_low(bars: List[Dict[str, Any]], end: int, window: int) -> Optional[float]:
    """Min low over bars[end-window:end] (PRIOR bars only). None if not enough."""
    if window <= 0 or end - window < 0:
        return None
    return min(b["low"] for b in bars[end - window:end])


def wilder_atr(bars: List[Dict[str, Any]], period: int) -> List[Optional[float]]:
    """Wilder ATR aligned to bars; atr[k] is the ATR through bar k (None until warm)."""
    n = len(bars)
    atr: List[Optional[float]] = [None] * n
    if period <= 0 or n < period + 1:
        return atr
    trs: List[Optional[float]] = [None] * n
    for k in range(1, n):
        h = bars[k]["high"]
        lo = bars[k]["low"]
        pc = bars[k - 1]["close"]
        trs[k] = max(h - lo, abs(h - pc), abs(lo - pc))
    seed = sum(trs[1:period + 1]) / period  # type: ignore[arg-type]
    atr[period] = seed
    prev = seed
    for k in range(period + 1, n):
        cur = (prev * (period - 1) + trs[k]) / period  # type: ignore[operator]
        prev = cur
        atr[k] = cur
    return atr


def simulate(
    bars: List[Dict[str, Any]],
    entry_channel: int = 55,
    exit_channel: int = 20,
    atr_period: int = 20,
    stop_n_multiple: float = 2.0,
) -> List[Dict[str, Any]]:
    """Deterministic daily Donchian System-1 no-pyramid simulation.

    Returns a list of closed-trade dicts. Pure function: no I/O, no randomness.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    atr = wilder_atr(bars, atr_period)
    pos: Optional[Dict[str, Any]] = None
    min_index = max(int(entry_channel), int(atr_period) + 1)

    for i in range(n):
        bar = bars[i]

        if pos is None:
            if i < min_index:
                continue
            entry_high = _highest_high(bars, i, entry_channel)
            entry_low = _lowest_low(bars, i, entry_channel)
            n_val = atr[i - 1]
            if entry_high is None or entry_low is None or n_val is None or n_val <= 0:
                continue
            risk = stop_n_multiple * n_val
            if bar["high"] > entry_high:
                entry_price = entry_high
                pos = {
                    "direction": "long",
                    "entry_index": i,
                    "entry_date": str(bar["timestamp"].date()),
                    "entry_price": entry_price,
                    "stop_price": entry_price - risk,
                    "n_at_entry": n_val,
                    "risk": risk,
                }
            elif bar["low"] < entry_low:
                entry_price = entry_low
                pos = {
                    "direction": "short",
                    "entry_index": i,
                    "entry_date": str(bar["timestamp"].date()),
                    "entry_price": entry_price,
                    "stop_price": entry_price + risk,
                    "n_at_entry": n_val,
                    "risk": risk,
                }
            # Manage from the NEXT bar; the entry bar does not also exit.
            continue

        # Managing an open position on this bar.
        direction = pos["direction"]
        entry = pos["entry_price"]
        stop = pos["stop_price"]
        risk = pos["risk"]
        exit_price: Optional[float] = None
        reason: Optional[str] = None

        if direction == "long":
            if bar["low"] <= stop:
                exit_price, reason = stop, "stop"
            else:
                exit_low = _lowest_low(bars, i, exit_channel)
                if exit_low is not None and bar["low"] < exit_low:
                    exit_price, reason = exit_low, "channel"
        else:  # short
            if bar["high"] >= stop:
                exit_price, reason = stop, "stop"
            else:
                exit_high = _highest_high(bars, i, exit_channel)
                if exit_high is not None and bar["high"] > exit_high:
                    exit_price, reason = exit_high, "channel"

        if exit_price is not None:
            pnl = (exit_price - entry) if direction == "long" else (entry - exit_price)
            trades.append(
                {
                    **pos,
                    "exit_index": i,
                    "exit_date": str(bar["timestamp"].date()),
                    "exit_price": exit_price,
                    "exit_reason": reason,
                    "r_multiple": pnl / risk if risk else 0.0,
                }
            )
            pos = None

    # Force-close any still-open position at the last bar's close.
    if pos is not None and n > 0:
        last = bars[-1]
        direction = pos["direction"]
        entry = pos["entry_price"]
        risk = pos["risk"]
        exit_price = last["close"]
        pnl = (exit_price - entry) if direction == "long" else (entry - exit_price)
        trades.append(
            {
                **pos,
                "exit_index": n - 1,
                "exit_date": str(last["timestamp"].date()),
                "exit_price": exit_price,
                "exit_reason": "end_of_data",
                "r_multiple": pnl / risk if risk else 0.0,
            }
        )

    return trades


def run_backtest(
    csv_path: str,
    params: Optional[Dict[str, Any]] = None,
    timestamp_column: str = "ts_event",
) -> Dict[str, Any]:
    """Run the daily Donchian baseline over a local CSV. Returns inert data.

    `params` keys: entry_channel, exit_channel, atr_period, stop_n_multiple.
    Output: {'r_multiples': [...], 'trades': [...], 'accounting': <note>}.
    The r_multiples list is directly consumable by engine.metrics.summarize().
    """
    params = params or {}
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate(
        bars,
        entry_channel=int(params.get("entry_channel", 55)),
        exit_channel=int(params.get("exit_channel", 20)),
        atr_period=int(params.get("atr_period", 20)),
        stop_n_multiple=float(params.get("stop_n_multiple", 2.0)),
    )
    return {
        "r_multiples": [t["r_multiple"] for t in trades],
        "trades": trades,
        "bars_loaded": len(bars),
        "accounting": ACCOUNTING_NOTE,
    }
