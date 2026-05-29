"""Offline NQ ORB backtester.

OFFLINE / CSV-ONLY: reads bars from a local CSV file only. It never fetches,
downloads, streams, or connects anywhere. Uses the Python standard library
only (csv, datetime) so no package install is required.

Input CSV columns (case-insensitive): timestamp, open, high, low, close.
Output: a list of trade R-multiples (and a small per-trade detail list) that
the metrics layer can summarize.
"""

from __future__ import annotations

import csv
from datetime import datetime, time as dtime
from typing import List, Dict, Any, Optional


def _parse_time(hhmm: str) -> dtime:
    parts = hhmm.split(":")
    return dtime(int(parts[0]), int(parts[1]))


def load_bars(csv_path: str, timestamp_column: str = "timestamp") -> List[Dict[str, Any]]:
    """Load OHLC bars from a local CSV file. Offline read only."""
    bars: List[Dict[str, Any]] = []
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        # Build a case-insensitive header map.
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


def _group_by_day(bars: List[Dict[str, Any]]) -> Dict[Any, List[Dict[str, Any]]]:
    days: Dict[Any, List[Dict[str, Any]]] = {}
    for b in bars:
        days.setdefault(b["timestamp"].date(), []).append(b)
    return days


def _simulate_day(
    day_bars: List[Dict[str, Any]],
    or_minutes: int,
    session_start: dtime,
    session_end: dtime,
    target_r_multiple: float,
) -> Optional[float]:
    """Simulate one day of NQ ORB. Returns the trade R-multiple, or None.

    Long on break above OR high, short on break below OR low (first break wins).
    Stop at the opposite side of the opening range. Target at target_r_multiple.
    Fallback exit at session close.
    """
    session = [
        b for b in day_bars
        if session_start <= b["timestamp"].time() <= session_end
    ]
    if not session:
        return None

    or_end_minute = (session_start.hour * 60 + session_start.minute) + or_minutes
    or_bars = [
        b for b in session
        if (b["timestamp"].hour * 60 + b["timestamp"].minute) < or_end_minute
    ]
    if not or_bars:
        return None

    or_high = max(b["high"] for b in or_bars)
    or_low = min(b["low"] for b in or_bars)
    if or_high <= or_low:
        return None

    post = [
        b for b in session
        if (b["timestamp"].hour * 60 + b["timestamp"].minute) >= or_end_minute
    ]
    if not post:
        return None

    direction = None
    entry = None
    stop = None
    target = None

    for b in post:
        if direction is None:
            if b["high"] > or_high:
                direction = "long"
                entry = or_high
                stop = or_low
                risk = entry - stop
                target = entry + target_r_multiple * risk
            elif b["low"] < or_low:
                direction = "short"
                entry = or_low
                stop = or_high
                risk = stop - entry
                target = entry - target_r_multiple * risk
            else:
                continue
            # Check the same bar for an immediate stop/target hit.
        if direction == "long":
            if b["low"] <= stop:
                return -1.0
            if b["high"] >= target:
                return target_r_multiple
        elif direction == "short":
            if b["high"] >= stop:
                return -1.0
            if b["low"] <= target:
                return target_r_multiple

    # Fallback: exit at last session close, expressed in R.
    if direction is None or entry is None:
        return None
    last_close = post[-1]["close"]
    risk = abs(entry - stop)
    if risk == 0:
        return None
    if direction == "long":
        return (last_close - entry) / risk
    return (entry - last_close) / risk


def run_backtest(
    csv_path: str,
    params: Dict[str, Any],
    timestamp_column: str = "timestamp",
) -> Dict[str, Any]:
    """Run the NQ ORB backtest over a local CSV.

    `params` keys: opening_range_minutes, target_r_multiple, session_start,
    session_end. Returns {'r_multiples': [...], 'trades': [...]} (inert data).
    """
    bars = load_bars(csv_path, timestamp_column=timestamp_column)
    or_minutes = int(params.get("opening_range_minutes", 15))
    target_r = float(params.get("target_r_multiple", 2.0))
    session_start = _parse_time(params.get("session_start", "09:30"))
    session_end = _parse_time(params.get("session_end", "16:00"))

    r_multiples: List[float] = []
    trades: List[Dict[str, Any]] = []
    for day, day_bars in sorted(_group_by_day(bars).items()):
        r = _simulate_day(day_bars, or_minutes, session_start, session_end, target_r)
        if r is not None:
            r_multiples.append(r)
            trades.append({"date": str(day), "r_multiple": r})

    return {"r_multiples": r_multiples, "trades": trades}
