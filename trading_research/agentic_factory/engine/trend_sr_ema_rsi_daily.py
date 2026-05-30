"""Offline daily Trend + Support/Resistance + EMA/RSI strategy engine (S26 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/s26_d1_trend_sr_ema_rsi_strategy_spec/ (committed af643ae). LONG-ONLY v1.

OFFLINE / INERT: pure-Python standard library only (csv, datetime). It never
fetches, downloads, streams, or connects anywhere. It writes no files. It runs
no optimization and no parameter search; every constant below is a fixed input
frozen by the S26-D1 spec.

Hypothesis (the OPPOSITE of the parked Donchian breakout entry): in an
established daily uptrend, buy a controlled pullback toward recent support that
shows momentum stabilizing, with risk fixed at 2N and reward capped at +2R.

Frozen rules (S26-D1):
  Indicators : EMA20, EMA50, EMA200, RSI(14) Wilder, ATR(20) Wilder.
               support_ref[i] = lowest low over bars[i-20:i] (EXCLUDES bar i).
  Trend      : close[i] > EMA200[i] AND EMA50[i] > EMA200[i].
  Pullback   : low[i] <= support_ref[i] + 1.5 * ATR20[i].
  RSI band   : 40 <= RSI14[i] <= 55.
  Confirm    : RSI14[i] > RSI14[i-1]  OR  close[i] > EMA20[i].
  Entry      : fill at the OPEN of the NEXT bar (i+1). No same-bar lookahead.
  Stop       : entry - 2.0 * ATR20[i].  1R = 2N = that initial stop distance.
  Target     : entry + 2R (= entry + 2 * 2N).
  Backstop   : if still open at a bar CLOSE and close < EMA50, exit at that close.
  Precedence : (1) hard stop -1R intrabar, (2) +2R target intrabar,
               (3) EMA50 trend-break on close, (4) end-of-data close.
  Accounting : R-only. No compounding, no pyramiding, one position at a time.

RESOLVED INTERPRETATION (recorded per the S26-D1 instruction to take the more
conservative reading where the spec is silent):
  * "Management begins the bar AFTER entry" -> the fill bar (i+1) only opens the
    position; exits are evaluated from bar i+2 onward. The fill bar never also
    exits. This mirrors the frozen Donchian convention and avoids crediting
    intrabar precision on the fill bar.
  * Same-bar stop+target -> the stop is checked BEFORE the target (conservative
    worst-case), so a bar touching both records -1R.

Lookahead safety: every indicator value at bar i uses bars up to and including
bar i's close only (known at that close); the support window excludes bar i; the
fill is the next bar's open. Nothing reads a future bar.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen S26-D1 constants (NOT tunable; changing any of these requires a new
# branch with a fresh pre-registered OOS, never an edit here).
EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200
RSI_PERIOD = 14
ATR_PERIOD = 20
SUPPORT_WINDOW = 20
SUPPORT_ATR_MULT = 1.5
RSI_BAND_LOW = 40.0
RSI_BAND_HIGH = 55.0
STOP_N_MULTIPLE = 2.0          # stop distance = 2N ; 1R = this distance
TARGET_R_MULTIPLE = 2.0        # take-profit at +2R

ACCOUNTING_NOTE = (
    "R-only; 1R = initial 2N stop distance; no dollar sizing / point value / "
    "cost / roll; long-only v1; capped +2R target"
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


def ema(values: List[float], period: int) -> List[Optional[float]]:
    """EMA aligned to values; ema[k] is None until warm (k < period-1).

    Seeded with the simple average of the first `period` values at index
    period-1, then standard EMA recursion (multiplier 2/(period+1)).
    """
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    mult = 2.0 / (period + 1.0)
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    prev = seed
    for k in range(period, n):
        cur = values[k] * mult + prev * (1.0 - mult)
        out[k] = cur
        prev = cur
    return out


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


def wilder_rsi(bars: List[Dict[str, Any]], period: int) -> List[Optional[float]]:
    """Wilder RSI(period) on close; rsi[k] is None until warm (k < period)."""
    n = len(bars)
    rsi: List[Optional[float]] = [None] * n
    if period <= 0 or n < period + 1:
        return rsi
    gains: List[float] = [0.0] * n
    losses: List[float] = [0.0] * n
    for k in range(1, n):
        delta = bars[k]["close"] - bars[k - 1]["close"]
        gains[k] = delta if delta > 0 else 0.0
        losses[k] = -delta if delta < 0 else 0.0
    avg_gain = sum(gains[1:period + 1]) / period
    avg_loss = sum(losses[1:period + 1]) / period

    def _rsi(ag: float, al: float) -> float:
        if al == 0.0:
            return 100.0
        rs = ag / al
        return 100.0 - (100.0 / (1.0 + rs))

    rsi[period] = _rsi(avg_gain, avg_loss)
    for k in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[k]) / period
        avg_loss = (avg_loss * (period - 1) + losses[k]) / period
        rsi[k] = _rsi(avg_gain, avg_loss)
    return rsi


def rolling_low(bars: List[Dict[str, Any]], end: int, window: int) -> Optional[float]:
    """Min low over bars[end-window:end] (PRIOR bars only, EXCLUDES bar `end`)."""
    if window <= 0 or end - window < 0:
        return None
    return min(b["low"] for b in bars[end - window:end])


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays, aligned to bars. Pure, no I/O."""
    closes = [b["close"] for b in bars]
    n = len(bars)
    support = [rolling_low(bars, i, SUPPORT_WINDOW) for i in range(n)]
    return {
        "ema20": ema(closes, EMA_FAST),
        "ema50": ema(closes, EMA_MID),
        "ema200": ema(closes, EMA_SLOW),
        "rsi": wilder_rsi(bars, RSI_PERIOD),
        "atr": wilder_atr(bars, ATR_PERIOD),
        "support": support,
    }


def is_long_signal(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i is a frozen long ENTRY SIGNAL (fill would be at bar i+1 open)."""
    if i < 1:
        return False
    ema20 = ind["ema20"][i]
    ema50 = ind["ema50"][i]
    ema200 = ind["ema200"][i]
    rsi_i = ind["rsi"][i]
    rsi_prev = ind["rsi"][i - 1]
    atr_i = ind["atr"][i]
    support_i = ind["support"][i]
    # All indicators must be fully warm; ATR must be positive for a valid risk.
    if (
        ema20 is None or ema50 is None or ema200 is None
        or rsi_i is None or rsi_prev is None
        or atr_i is None or atr_i <= 0.0 or support_i is None
    ):
        return False
    bar = bars[i]
    # C1 Trend (bullish stack).
    if not (bar["close"] > ema200 and ema50 > ema200):
        return False
    # C2 Pullback toward recent support.
    if not (bar["low"] <= support_i + SUPPORT_ATR_MULT * atr_i):
        return False
    # C3 RSI pullback band.
    if not (RSI_BAND_LOW <= rsi_i <= RSI_BAND_HIGH):
        return False
    # C4 Confirmation: RSI turning up OR close reclaiming EMA20.
    if not (rsi_i > rsi_prev or bar["close"] > ema20):
        return False
    return True


def long_signal_indices(bars: List[Dict[str, Any]]) -> List[int]:
    """All bar indices that satisfy the frozen long entry signal (diagnostic)."""
    ind = compute_indicators(bars)
    return [i for i in range(len(bars)) if is_long_signal(bars, i, ind)]


def simulate(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic long-only S26 simulation. Returns a list of closed trades.

    Pure function: no I/O, no randomness. One position at a time, no pyramiding.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n == 0:
        return trades
    ind = compute_indicators(bars)
    ema50 = ind["ema50"]
    atr = ind["atr"]

    pos: Optional[Dict[str, Any]] = None
    i = 0
    while i < n:
        if pos is None:
            # Look for a signal at bar i; fill at the next bar's open.
            if i + 1 < n and is_long_signal(bars, i, ind):
                fill_index = i + 1
                entry_price = bars[fill_index]["open"]
                risk = STOP_N_MULTIPLE * atr[i]  # 1R = 2N at the signal bar
                pos = {
                    "direction": "long",
                    "signal_index": i,
                    "entry_index": fill_index,
                    "entry_date": str(bars[fill_index]["timestamp"].date()),
                    "entry_price": entry_price,
                    "stop_price": entry_price - risk,
                    "target_price": entry_price + TARGET_R_MULTIPLE * risk,
                    "n_at_entry": atr[i],
                    "risk": risk,
                }
                # Management begins the bar AFTER the fill bar (i+2).
                i = fill_index + 1
                continue
            i += 1
            continue

        # Managing an open long position at bar i (i >= entry_index + 1).
        bar = bars[i]
        entry = pos["entry_price"]
        stop = pos["stop_price"]
        target = pos["target_price"]
        risk = pos["risk"]
        e50 = ema50[i]
        exit_price: Optional[float] = None
        reason: Optional[str] = None

        # Precedence: stop (worst-case) -> target -> EMA50 trend-break on close.
        if bar["low"] <= stop:
            exit_price, reason = stop, "stop"
        elif bar["high"] >= target:
            exit_price, reason = target, "target"
        elif e50 is not None and bar["close"] < e50:
            exit_price, reason = bar["close"], "ema50_trend_break"

        if exit_price is not None:
            pnl = exit_price - entry
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
        i += 1

    # Force-close any still-open position at the last bar's close.
    if pos is not None:
        last = bars[-1]
        entry = pos["entry_price"]
        risk = pos["risk"]
        exit_price = last["close"]
        pnl = exit_price - entry
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


def summarize(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Inert summary metrics from a list of closed trades (R-only)."""
    rs = [t["r_multiple"] for t in trades]
    n = len(rs)
    if n == 0:
        return {
            "trade_count": 0, "total_r": 0.0, "profit_factor": None,
            "win_rate": 0.0, "expectancy_r": 0.0, "max_drawdown_r": 0.0,
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
    return {
        "trade_count": n,
        "total_r": sum(rs),
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else None,
        "win_rate": sum(1 for r in rs if r > 0) / n,
        "expectancy_r": sum(rs) / n,
        "max_drawdown_r": max_dd,
    }


def run_backtest(
    csv_path: str, timestamp_column: str = "ts_event"
) -> Dict[str, Any]:
    """Run the S26 long-only strategy over a local CSV. Returns inert data."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate(bars)
    return {
        "r_multiples": [t["r_multiple"] for t in trades],
        "trades": trades,
        "bars_loaded": len(bars),
        "summary": summarize(trades),
        "accounting": ACCOUNTING_NOTE,
    }
