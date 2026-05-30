"""Offline daily Mean-Reversion-After-Overextension-Inside-Bull-Trend engine (S27 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/s27_d2_mean_reversion_bull_trend_strategy_spec/ (committed 4a678ce). LONG-ONLY v1.

OFFLINE / INERT: pure-Python standard library only (csv, datetime). It never
fetches, downloads, streams, or connects anywhere. It writes no files. It runs
no optimization and no parameter search; every constant below is a fixed input
frozen by the S27-D2 spec.

Hypothesis: in a confirmed bull trend, a sharp short-term OVEREXTENSION to the
downside that then shows a one-bar reversal tends to mean-revert. The edge must
come from the DISCRETE overextension-then-reversal event, not from broad trend
drift -- which is why the entry is a two-step event built to be significance-
testable against random bull-trend entries.

Frozen rules (S27-D2):
  Indicators  : EMA20, EMA50, EMA200, RSI(14) Wilder, ATR(20) Wilder.
  Bull filter : close[i] > EMA200[i] AND EMA50[i] > EMA200[i]
                AND EMA200[i] - EMA200[i-20] >= 0  (non-negative 20-bar slope).
  Overextend  : close[i] <= EMA20[i] - 1.0 * ATR20[i]
                AND RSI14[i] <= 35
                AND close[i] is the LOWEST close of the last 5 bars (i inclusive).
  Reversal    : Option B -- require close[i+1] > close[i]. If satisfied the setup
                is confirmed on bar i+1; if close[i+1] <= close[i] it EXPIRES.
  Entry       : fill at the OPEN of bar i+2 (the bar after confirmation). No
                same-bar lookahead.
  Stop        : entry - 1.5 * ATR20[i].  1R = 1.5 * ATR20[i] = that stop distance.
  Target      : entry + 1.5R (= entry + 1.5 * 1R = entry + 2.25 * ATR20[i]).
  Time stop   : exit at the CLOSE of the 10th bar held if neither stop nor target.
  Precedence  : (1) hard stop -1R intrabar, (2) +1.5R target intrabar,
                (3) time stop on the 10th held bar's close, (4) end-of-data close.
  Accounting  : R-only. No compounding, no pyramiding, one position at a time.

RESOLVED INTERPRETATION (the more conservative reading, mirroring S26):
  * "Management begins the bar AFTER the fill" -> the fill bar (i+2) only opens
    the position; exits are evaluated from bar i+3 onward. The fill bar never
    also exits, so it counts as the 1st bar held but is not itself an exit bar.
  * Same-bar stop+target -> the stop is checked BEFORE the target (conservative
    worst-case), so a bar touching both records -1R.
  * Bars held are counted 1-based from the fill bar; the time stop fires on the
    10th held bar (= entry_index + 9).

Lookahead safety: every indicator value at bar i uses bars up to and including
bar i's close only; the EMA200 slope reads bar i-20 (a PRIOR bar); confirmation
reads bar i+1's close but the fill is bar i+2's open. Nothing reads a future bar
relative to its own decision point.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen S27-D2 constants (NOT tunable; changing any of these requires a new
# branch with a fresh pre-registered OOS, never an edit here).
EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200
RSI_PERIOD = 14
ATR_PERIOD = 20
SLOPE_LOOKBACK = 20            # EMA200[i] - EMA200[i-20] >= 0
OVEREXT_ATR_MULT = 1.0         # close <= EMA20 - 1.0 * ATR20
RSI_MAX = 35.0                 # RSI14 <= 35
LOWEST_CLOSE_WINDOW = 5        # close is lowest close of last 5 bars (i inclusive)
STOP_ATR_MULT = 1.5            # stop distance = 1.5 * ATR20 ; 1R = this distance
TARGET_R_MULTIPLE = 1.5        # take-profit at +1.5R
TIME_STOP_BARS = 10            # exit at close of the 10th bar held

ACCOUNTING_NOTE = (
    "R-only; 1R = initial 1.5*ATR20 stop distance; no dollar sizing / point "
    "value / cost / roll; long-only v1; capped +1.5R target; 10-bar time stop"
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


def is_lowest_close(bars: List[Dict[str, Any]], i: int, window: int) -> bool:
    """True if close[i] is the lowest close over bars[i-window+1 : i+1] (i inclusive)."""
    if window <= 0 or i - window + 1 < 0:
        return False
    ci = bars[i]["close"]
    return all(ci <= bars[j]["close"] for j in range(i - window + 1, i + 1))


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays, aligned to bars. Pure, no I/O."""
    closes = [b["close"] for b in bars]
    return {
        "ema20": ema(closes, EMA_FAST),
        "ema50": ema(closes, EMA_MID),
        "ema200": ema(closes, EMA_SLOW),
        "rsi": wilder_rsi(bars, RSI_PERIOD),
        "atr": wilder_atr(bars, ATR_PERIOD),
    }


def is_bull_trend(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i satisfies the frozen 3-part bull-trend filter."""
    if i < SLOPE_LOOKBACK:
        return False
    ema50 = ind["ema50"][i]
    ema200 = ind["ema200"][i]
    ema200_prev = ind["ema200"][i - SLOPE_LOOKBACK]
    if ema50 is None or ema200 is None or ema200_prev is None:
        return False
    close = bars[i]["close"]
    if not (close > ema200):
        return False
    if not (ema50 > ema200):
        return False
    if not (ema200 - ema200_prev >= 0.0):  # non-negative EMA200 slope
        return False
    return True


def is_overextended_setup(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i is a frozen overextension SETUP (still needs i+1 reversal).

    Requires the bull-trend filter AND all three overextension conditions.
    """
    if not is_bull_trend(bars, i, ind):
        return False
    ema20 = ind["ema20"][i]
    atr_i = ind["atr"][i]
    rsi_i = ind["rsi"][i]
    if ema20 is None or atr_i is None or atr_i <= 0.0 or rsi_i is None:
        return False
    close = bars[i]["close"]
    # O1 close at least 1.0 ATR20 below EMA20.
    if not (close <= ema20 - OVEREXT_ATR_MULT * atr_i):
        return False
    # O2 oversold RSI.
    if not (rsi_i <= RSI_MAX):
        return False
    # O3 fresh local extreme: lowest close of the last 5 bars (i inclusive).
    if not is_lowest_close(bars, i, LOWEST_CLOSE_WINDOW):
        return False
    return True


def is_reversal_confirmed(bars: List[Dict[str, Any]], i: int) -> bool:
    """Option B confirmation: the bar AFTER the setup closes higher (close[i+1] > close[i])."""
    if i + 1 >= len(bars):
        return False
    return bars[i + 1]["close"] > bars[i]["close"]


def find_entries(bars: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    """All confirmed entry candidates (diagnostic; ignores one-position overlap).

    Each entry: setup on bar i, reversal confirmed on i+1, fill on i+2 open.
    """
    ind = compute_indicators(bars)
    n = len(bars)
    out: List[Dict[str, int]] = []
    for i in range(n):
        if i + 2 >= n:
            break
        if is_overextended_setup(bars, i, ind) and is_reversal_confirmed(bars, i):
            out.append({"signal_index": i, "confirm_index": i + 1, "entry_index": i + 2})
    return out


def simulate_s27(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic long-only S27 simulation. Returns a list of closed trades.

    Pure function: no I/O, no randomness. One position at a time, no pyramiding.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n == 0:
        return trades
    ind = compute_indicators(bars)
    atr = ind["atr"]

    pos: Optional[Dict[str, Any]] = None
    i = 0
    while i < n:
        if pos is None:
            # Setup on bar i, reversal confirmation on i+1, fill on i+2 open.
            if (
                i + 2 < n
                and is_overextended_setup(bars, i, ind)
                and is_reversal_confirmed(bars, i)
            ):
                fill_index = i + 2
                entry_price = bars[fill_index]["open"]
                risk = STOP_ATR_MULT * atr[i]  # 1R = 1.5*ATR20 at the signal bar
                pos = {
                    "direction": "long",
                    "signal_index": i,
                    "confirm_index": i + 1,
                    "entry_index": fill_index,
                    "entry_date": str(bars[fill_index]["timestamp"].date()),
                    "entry_price": entry_price,
                    "stop_price": entry_price - risk,
                    "target_price": entry_price + TARGET_R_MULTIPLE * risk,
                    "n_at_entry": atr[i],
                    "risk": risk,
                }
                # Management begins the bar AFTER the fill bar (i+3).
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
        bars_held = i - pos["entry_index"] + 1  # fill bar = 1st held bar
        exit_price: Optional[float] = None
        reason: Optional[str] = None

        # Precedence: stop (worst-case) -> target -> time stop on the 10th held bar.
        if bar["low"] <= stop:
            exit_price, reason = stop, "stop"
        elif bar["high"] >= target:
            exit_price, reason = target, "target"
        elif bars_held >= TIME_STOP_BARS:
            exit_price, reason = bar["close"], "time_stop"

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


def anti_donchian_top3_gate(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Frozen S27 hard gate: IS net must stay POSITIVE after removing the top 3 winners.

    This is the explicit guard against the Donchian failure mode (S24/S25), where
    a few fat-tail winners carried the whole record. Pure accounting; no I/O.
    """
    rs = sorted((t["r_multiple"] for t in trades), reverse=True)
    net_r = sum(rs)
    net_r_ex_top3 = sum(rs[3:])  # drop the 3 largest r-multiples
    return {
        "trade_count": len(rs),
        "net_r": net_r,
        "top3_r": sum(rs[:3]),
        "net_r_ex_top3": net_r_ex_top3,
        "passes": net_r_ex_top3 > 0.0,
    }


def run_backtest(
    csv_path: str, timestamp_column: str = "ts_event"
) -> Dict[str, Any]:
    """Run the S27 long-only strategy over a local CSV. Returns inert data."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate_s27(bars)
    return {
        "r_multiples": [t["r_multiple"] for t in trades],
        "trades": trades,
        "bars_loaded": len(bars),
        "summary": summarize(trades),
        "top3_gate": anti_donchian_top3_gate(trades),
        "accounting": ACCOUNTING_NOTE,
    }
