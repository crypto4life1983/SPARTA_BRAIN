"""Offline daily Failed-Breakout / False-Break Reversal engine (S29 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/s29_d2_failed_breakout_reversal_strategy_spec/ (committed c96850f).
LONG-ONLY false DOWNSIDE break v1 (symmetric false-upside shorts are DEFERRED to
a future, separately-authorized branch and are NOT implemented here).

OFFLINE / INERT: pure-Python standard library only (csv, datetime). It never
fetches, downloads, streams, or connects anywhere. It writes no files. It runs
no optimization and no parameter search; every constant below is a fixed input
frozen by the S29-D2 spec.

Hypothesis: a daily bar that violates a prior daily extreme INTRABAR but FAILS to
close beyond the prior range (a false break) traps breakout traders, who are then
forced to cover -- mechanically reverting price over the next several bars. The
edge must come from the FAILURE EVENT, not from broad trend drift, which is why
the entry is a datable event built to be significance-testable against BOTH
random-in-regime entries and raw prior-extreme touches.

Frozen rules (S29-D2):
  Indicators  : EMA50, EMA200, ATR20 (Wilder).
  False-break : prior 20-day low EXCLUDING the current bar (20-bar rolling low
                shifted one bar).  Long trigger on bar i:
                  low[i] < prior_20_low[i]  AND  close[i] > prior_20_low[i].
                A bar piercing the prior low intrabar but closing back above it.
  Regime guard: Option B (most permissive). BLOCK a long entry if
                  close[i] < EMA200[i]  AND  EMA50[i] < EMA200[i]
                (a confirmed both-bearish downtrend); otherwise eligible.
                Evaluated on the SIGNAL bar.
  Entry       : fill at the OPEN of bar s+1 (the bar after the false-break signal
                bar). No same-bar lookahead.
  Stop        : LEVEL-based (thesis-invalidation).
                  stop_price = signal_bar_low - 0.25 * ATR20_at_signal_bar.
                  1R = entry_open - stop_price  (NOT a fixed ATR multiple).
  Target      : entry_open + 1.5 * R  (+1.5R).
  Time stop   : exit at the CLOSE of the 10th bar held if neither stop nor target.
  Precedence  : (1) hard stop -1R intrabar, (2) +1.5R target intrabar,
                (3) time stop on the 10th held bar's close, (4) end-of-data close.
  Accounting  : R-only. No compounding, no pyramiding, one position at a time.

RESOLVED INTERPRETATIONS (the more conservative reading, mirroring S26/S27/S28):
  * The regime guard reads bar i indicators only; an entry can only fire once
    EMA200 (and therefore EMA50) and ATR20 are warm, so the guard is always
    meaningfully evaluable at any real entry.
  * "Management begins the bar AFTER the fill" -> the fill bar (s+1) only opens
    the position; exits are evaluated from bar s+2 onward. The fill bar never
    also exits, so it counts as the 1st bar held but is not itself an exit bar.
  * Same-bar stop+target -> the stop is checked BEFORE the target (conservative
    worst-case), so a bar touching both records -1R.
  * Bars held are counted 1-based from the fill bar; the time stop fires on the
    10th held bar (= entry_index + 9).
  * If a gap-up open places the fill at or below the level stop (risk <= 0) the
    setup is skipped as un-fillable, never recorded as a degenerate trade.
  * One position at a time: a false-break signal is ignored while a position is
    live; the next signal is sought only after the open position closes.

Lookahead safety: every indicator value at bar i uses bars up to and including
bar i's close only; prior_low reads PRIOR bars [i-20 : i] (excludes bar i); the
fill is the signal bar's NEXT open. Nothing reads a future bar relative to its
own decision point.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen S29-D2 constants (NOT tunable; changing any of these requires a NEW
# branch with a fresh pre-registered OOS, never an edit here).
EMA_FAST = 50
EMA_SLOW = 200
ATR_PERIOD = 20
LOOKBACK_N = 20             # prior 20-day low, excluding the current bar
STOP_ATR_BUFFER = 0.25     # stop = signal_low - 0.25 * ATR20(signal)
TARGET_R_MULTIPLE = 1.5    # take-profit at +1.5R
TIME_STOP_BARS = 10         # exit at close of the 10th bar held

ACCOUNTING_NOTE = (
    "R-only; 1R = entry_open - (signal_low - 0.25*ATR20(signal)) level stop; no "
    "dollar sizing / point value / cost / roll; long-only false-downside-break "
    "v1; +1.5R target; 10-bar time stop; one position at a time"
)


def load_daily_bars(
    csv_path: str, timestamp_column: str = "ts_event"
) -> List[Dict[str, Any]]:
    """Load daily OHLC(V) bars from a local CSV. Offline read only, sorted by time.

    Volume is read if present but the S29 false-break rule does not require it.
    No network, no fetch. NOT used by the synthetic test suite.
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
            bars.append(
                {
                    "timestamp": datetime.fromisoformat(ts_raw.strip()),
                    "open": float(row[header_map["open"]]),
                    "high": float(row[header_map["high"]]),
                    "low": float(row[header_map["low"]]),
                    "close": float(row[header_map["close"]]),
                    "volume": float(row[vol_key]) if vol_key else 0.0,
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


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays, aligned to bars. Pure, no I/O."""
    closes = [b["close"] for b in bars]
    return {
        "ema50": ema(closes, EMA_FAST),
        "ema200": ema(closes, EMA_SLOW),
        "atr": wilder_atr(bars, ATR_PERIOD),
    }


def prior_low(
    bars: List[Dict[str, Any]], i: int, lookback: int = LOOKBACK_N
) -> Optional[float]:
    """Lowest LOW over the prior `lookback` bars [i-lookback : i], EXCLUDING bar i."""
    if lookback <= 0 or i < lookback:
        return None
    return min(bars[j]["low"] for j in range(i - lookback, i))


def is_false_downside_break(
    bars: List[Dict[str, Any]], i: int, lookback: int = LOOKBACK_N
) -> bool:
    """True if bar i pierces the prior `lookback`-low intrabar but closes back above it."""
    pl = prior_low(bars, i, lookback)
    if pl is None:
        return False
    low = bars[i]["low"]
    close = bars[i]["close"]
    return low < pl and close > pl


def is_regime_blocked(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i is a CONFIRMED downtrend (close<EMA200 AND EMA50<EMA200) -> block.

    Option B guard: the MOST PERMISSIVE filter -- it blocks only the both-bearish
    falling-knife regime. While EMA200/EMA50 are still warming (None) the regime
    cannot be confirmed bearish, so the bar is NOT blocked here; a real entry is
    separately gated on warm indicators in simulate_s29.
    """
    ema200 = ind["ema200"][i]
    ema50 = ind["ema50"][i]
    if ema200 is None or ema50 is None:
        return False
    close = bars[i]["close"]
    return close < ema200 and ema50 < ema200


def find_entries(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Diagnostic listing of false-break -> entry candidates.

    Ignores one-position overlap (it does not simulate management); it DOES apply
    the false-break trigger, the regime guard, and the warm-indicator / fill-bar
    availability checks, so the listed 'entry' candidates are the bars that would
    actually fill.
    """
    ind = compute_indicators(bars)
    atr = ind["atr"]
    ema200 = ind["ema200"]
    ema50 = ind["ema50"]
    n = len(bars)
    out: List[Dict[str, Any]] = []
    for i in range(n):
        if not is_false_downside_break(bars, i):
            continue
        if atr[i] is None or atr[i] <= 0.0 or ema200[i] is None or ema50[i] is None:
            out.append({
                "signal_index": i, "entry_index": None,
                "setup_status": "not_warm",
            })
            continue
        if is_regime_blocked(bars, i, ind):
            out.append({
                "signal_index": i, "entry_index": None,
                "setup_status": "suppressed_bad_regime",
            })
            continue
        if i + 1 >= n:
            out.append({
                "signal_index": i, "entry_index": None,
                "setup_status": "no_entry_bar",
            })
            continue
        entry_price = bars[i + 1]["open"]
        stop_price = bars[i]["low"] - STOP_ATR_BUFFER * atr[i]  # type: ignore[operator]
        if entry_price - stop_price <= 0.0:
            out.append({
                "signal_index": i, "entry_index": None,
                "setup_status": "unfillable_nonpositive_risk",
            })
            continue
        out.append({
            "signal_index": i, "entry_index": i + 1,
            "setup_status": "entry",
        })
    return out


def simulate_s29(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic long-only S29 simulation. Returns a list of closed trades.

    Pure function: no I/O, no randomness. One position at a time, no pyramiding,
    no compounding.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n == 0:
        return trades
    ind = compute_indicators(bars)
    atr = ind["atr"]
    ema200 = ind["ema200"]
    ema50 = ind["ema50"]

    i = 0
    while i < n:
        # 1) Seek a false-downside-break signal bar.
        if not is_false_downside_break(bars, i):
            i += 1
            continue
        # 2) Require warm indicators (regime guard + ATR stop must be evaluable).
        if atr[i] is None or atr[i] <= 0.0 or ema200[i] is None or ema50[i] is None:
            i += 1
            continue
        # 3) Regime NO-TRADE gate on the signal bar (block confirmed downtrend).
        if is_regime_blocked(bars, i, ind):
            i += 1
            continue

        signal_index = i
        signal_low = bars[i]["low"]
        pl = prior_low(bars, i, LOOKBACK_N)
        atr_at_signal = atr[i]

        # 4) Entry at the OPEN of the bar after the signal bar.
        entry_index = signal_index + 1
        if entry_index >= n:
            break  # no bar to fill on
        entry_price = bars[entry_index]["open"]
        stop_price = signal_low - STOP_ATR_BUFFER * atr_at_signal  # type: ignore[operator]
        risk = entry_price - stop_price  # 1R = entry_open - level stop
        if risk <= 0.0:
            # Un-fillable gap (open at/below the level stop) -> skip, seek next.
            i = signal_index + 1
            continue
        target_price = entry_price + TARGET_R_MULTIPLE * risk
        pos = {
            "direction": "long",
            "signal_index": signal_index,
            "signal_date": str(bars[signal_index]["timestamp"].date()),
            "prior_low": pl,
            "signal_low": signal_low,
            "entry_index": entry_index,
            "entry_date": str(bars[entry_index]["timestamp"].date()),
            "entry_price": entry_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "atr_at_signal": atr_at_signal,
            "risk": risk,
            "setup_status": "entered",
        }

        # 5) Manage from the bar AFTER the fill bar (entry_index + 1).
        k = entry_index + 1
        closed = False
        while k < n:
            bar = bars[k]
            bars_held = k - entry_index + 1  # fill bar = 1st held bar
            exit_price: Optional[float] = None
            reason: Optional[str] = None
            # Precedence: stop (worst-case) -> target -> time stop on the 10th held bar.
            if bar["low"] <= stop_price:
                exit_price, reason = stop_price, "stop"
            elif bar["high"] >= target_price:
                exit_price, reason = target_price, "target"
            elif bars_held >= TIME_STOP_BARS:
                exit_price, reason = bar["close"], "time_stop"
            if exit_price is not None:
                pnl = exit_price - entry_price
                trades.append({
                    **pos,
                    "exit_index": k,
                    "exit_date": str(bar["timestamp"].date()),
                    "exit_price": exit_price,
                    "exit_reason": reason,
                    "r_multiple": pnl / risk if risk else 0.0,
                })
                closed = True
                i = k + 1  # new signals only after this position closes
                break
            k += 1

        if not closed:
            # Force-close any still-open position at the last bar's close.
            last = bars[-1]
            pnl = last["close"] - entry_price
            trades.append({
                **pos,
                "exit_index": n - 1,
                "exit_date": str(last["timestamp"].date()),
                "exit_price": last["close"],
                "exit_reason": "end_of_data",
                "r_multiple": pnl / risk if risk else 0.0,
            })
            i = n

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
    """Frozen S29 hard gate: IS net must stay POSITIVE after removing the top 3 winners.

    The explicit guard against the Donchian failure mode (S24/S25), where a few
    fat-tail winners carried the whole record. Pure accounting; no I/O.
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
    """Run the S29 long-only strategy over a local CSV. Returns inert data."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate_s29(bars)
    return {
        "r_multiples": [t["r_multiple"] for t in trades],
        "trades": trades,
        "bars_loaded": len(bars),
        "summary": summarize(trades),
        "top3_gate": anti_donchian_top3_gate(trades),
        "accounting": ACCOUNTING_NOTE,
    }
