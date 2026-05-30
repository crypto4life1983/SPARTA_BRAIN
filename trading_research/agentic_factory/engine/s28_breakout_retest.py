"""Offline daily Breakout-Retest-with-Volatility-Expansion engine (S28 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/s28_d2_breakout_retest_vol_expansion_strategy_spec/ (committed 5204fe1).
LONG-ONLY v1.

OFFLINE / INERT: pure-Python standard library only (csv, datetime). It never
fetches, downloads, streams, or connects anywhere. It writes no files. It runs
no optimization and no parameter search; every constant below is a fixed input
frozen by the S28-D2 spec.

Hypothesis: a raw breakout alone is noisy, but a breakout that EXPANDS
volatility/participation and then RETESTS-and-HOLDS the prior resistance level
(prior resistance becomes support) may mark genuine acceptance above resistance.
The edge must come from the discrete retest-hold event AFTER expansion -- not
from raw breakout chasing -- which is why the entry is a datable event built to
be significance-testable against BOTH random-in-regime and raw-breakout entries.

Frozen rules (S28-D2):
  Indicators  : EMA50, EMA200, ATR20 (Wilder), SMA20(volume), per-bar TrueRange.
  Trend filter: close[i] > EMA200[i] AND EMA50[i] > EMA200[i]
                AND EMA200[i] - EMA200[i-20] >= 0  (non-negative 20-bar slope).
                Checked on the BREAKOUT bar (the background context for the setup).
  Resistance  : highest HIGH over the prior 55 bars, EXCLUDING the current bar.
  Breakout    : close[i] > resistance
                AND TrueRange[i] >= 1.25 * ATR20[i]   (range expansion)
                AND volume[i]    >= 1.20 * SMA20(volume)[i]  (participation).
  Retest win. : up to 10 bars AFTER the breakout bar (b+1 .. b+10).
  Retest/hold : on candidate bar j -- low[j] <= resistance + 0.25 * ATR20_at_breakout
                AND close[j] >= resistance (closes back above the reclaimed level).
                The FIRST in-window bar satisfying both = the retest-hold signal bar.
  Expiry      : if close[j] < resistance on any in-window bar BEFORE a retest-hold,
                the setup FAILS (acceptance lost); if no bar retests within 10 bars,
                the setup EXPIRES.
  Bad-regime  : NO TRADE if  abs(close[s]-EMA200[s]) <= 1.0*ATR20[s]
                AND (EMA50[s]-EMA50[s-20]) <= 0.   Evaluated on the SIGNAL bar s.
  Entry       : fill at the OPEN of bar s+1 (the bar after the retest-hold). No
                same-bar lookahead.
  Stop        : entry - 2.0 * ATR20[s].  1R = 2.0 * ATR20[s] = that stop distance.
  Target      : entry + 2.0R (= entry + 2 * 1R = entry + 4.0 * ATR20[s]).
  Time stop   : exit at the CLOSE of the 20th bar held if neither stop nor target.
  Precedence  : (1) hard stop -1R intrabar, (2) +2.0R target intrabar,
                (3) time stop on the 20th held bar's close, (4) end-of-data close.
  Accounting  : R-only. No compounding, no pyramiding, one position at a time,
                one active setup at a time.

RESOLVED INTERPRETATIONS (the more conservative reading, mirroring S26/S27):
  * "Trend / background filter" -- section 4 does not name a bar; the breakout
    must occur in a rising trend, so the 3-part trend filter is checked on the
    BREAKOUT bar. The bad-regime no-trade gate (section 8) is separately
    evaluated on the retest-hold SIGNAL bar exactly as the spec states.
  * ATR for the retest threshold is ATR20 captured AT THE BREAKOUT bar
    (atr_at_breakout); ATR for the stop / 1R is ATR20 at the SIGNAL bar -- two
    distinct values, exactly as the spec text distinguishes them.
  * "Management begins the bar AFTER the fill" -> the fill bar (s+1) only opens
    the position; exits are evaluated from bar s+2 onward. The fill bar never
    also exits, so it counts as the 1st bar held but is not itself an exit bar.
  * Same-bar stop+target -> the stop is checked BEFORE the target (conservative
    worst-case), so a bar touching both records -1R.
  * Bars held are counted 1-based from the fill bar; the time stop fires on the
    20th held bar (= entry_index + 19).
  * One active setup at a time: each breakout's 10-bar retest window is fully
    resolved (entry / suppression / expiry) before any later breakout is sought,
    and no new setup is opened while a position is live.

Lookahead safety: every indicator value at bar i uses bars up to and including
bar i's close only; the EMA slopes read bar i-20 (a PRIOR bar); the retest scan
reads forward bars but the fill is the signal bar's NEXT open. Nothing reads a
future bar relative to its own decision point.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen S28-D2 constants (NOT tunable; changing any of these requires a NEW
# branch with a fresh pre-registered OOS, never an edit here).
EMA_MID = 50
EMA_SLOW = 200
ATR_PERIOD = 20
VOL_SMA_PERIOD = 20            # SMA20(volume)
SLOPE_LOOKBACK = 20           # EMA200[i]-EMA200[i-20] >= 0 ; EMA50[i]-EMA50[i-20] <= 0
RESISTANCE_LOOKBACK = 55      # highest high over the prior 55 bars (excl. current)
TR_ATR_MULT = 1.25            # breakout TrueRange >= 1.25 * ATR20
VOL_MULT = 1.20              # breakout volume >= 1.20 * SMA20(volume)
RETEST_WINDOW = 10            # up to 10 bars after the breakout bar
RETEST_ATR_MULT = 0.25       # low <= resistance + 0.25 * ATR20_at_breakout
BAD_REGIME_ATR_MULT = 1.0    # abs(close-EMA200) <= 1.0 * ATR20 (near-mean)
STOP_ATR_MULT = 2.0          # stop distance = 2.0 * ATR20 at signal ; 1R = this
TARGET_R_MULTIPLE = 2.0      # take-profit at +2.0R
TIME_STOP_BARS = 20           # exit at close of the 20th bar held

ACCOUNTING_NOTE = (
    "R-only; 1R = initial 2.0*ATR20(signal) stop distance; no dollar sizing / "
    "point value / cost / roll; long-only v1; +2.0R target; 20-bar time stop; "
    "one position and one active setup at a time"
)


def load_daily_bars(
    csv_path: str, timestamp_column: str = "ts_event"
) -> List[Dict[str, Any]]:
    """Load daily OHLCV bars from a local CSV. Offline read only, sorted by time.

    Requires a real volume column (the S28 breakout requires volume expansion);
    the loader reads the 'volume' header. No network, no fetch.
    """
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
                    "volume": float(row[header_map["volume"]]),
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


def true_range(bars: List[Dict[str, Any]]) -> List[Optional[float]]:
    """Per-bar true range; tr[k] is None for k==0 (no prior close)."""
    n = len(bars)
    out: List[Optional[float]] = [None] * n
    for k in range(1, n):
        h = bars[k]["high"]
        lo = bars[k]["low"]
        pc = bars[k - 1]["close"]
        out[k] = max(h - lo, abs(h - pc), abs(lo - pc))
    return out


def sma_volume(bars: List[Dict[str, Any]], period: int) -> List[Optional[float]]:
    """Simple 20-bar average of volume; sma[k] uses bars[k-period+1 .. k] (k inclusive)."""
    n = len(bars)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    for k in range(period - 1, n):
        out[k] = sum(bars[j]["volume"] for j in range(k - period + 1, k + 1)) / period
    return out


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays, aligned to bars. Pure, no I/O."""
    closes = [b["close"] for b in bars]
    return {
        "ema50": ema(closes, EMA_MID),
        "ema200": ema(closes, EMA_SLOW),
        "atr": wilder_atr(bars, ATR_PERIOD),
        "vol_sma": sma_volume(bars, VOL_SMA_PERIOD),
        "tr": true_range(bars),
    }


def prior_resistance(
    bars: List[Dict[str, Any]], i: int, lookback: int = RESISTANCE_LOOKBACK
) -> Optional[float]:
    """Highest HIGH over the prior `lookback` bars [i-lookback : i], EXCLUDING bar i."""
    if lookback <= 0 or i < lookback:
        return None
    return max(bars[j]["high"] for j in range(i - lookback, i))


def is_trend_ok(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i satisfies the frozen 3-part trend/background filter."""
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


def is_breakout_bar(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i is a frozen BREAKOUT bar (close>resistance + range + volume)."""
    res = prior_resistance(bars, i, RESISTANCE_LOOKBACK)
    if res is None:
        return False
    atr_i = ind["atr"][i]
    tr_i = ind["tr"][i]
    vsma = ind["vol_sma"][i]
    if atr_i is None or atr_i <= 0.0 or tr_i is None or vsma is None:
        return False
    close = bars[i]["close"]
    vol = bars[i]["volume"]
    if not (close > res):
        return False
    if not (tr_i >= TR_ATR_MULT * atr_i):       # range expansion
        return False
    if not (vol >= VOL_MULT * vsma):            # volume / participation expansion
        return False
    return True


def is_bad_regime(
    bars: List[Dict[str, Any]], i: int, ind: Dict[str, List[Optional[float]]]
) -> bool:
    """True if bar i is the near-mean / non-rising chop regime (NO-TRADE gate)."""
    if i < SLOPE_LOOKBACK:
        return False
    ema200 = ind["ema200"][i]
    atr_i = ind["atr"][i]
    ema50 = ind["ema50"][i]
    ema50_prev = ind["ema50"][i - SLOPE_LOOKBACK]
    if ema200 is None or atr_i is None or ema50 is None or ema50_prev is None:
        return False
    close = bars[i]["close"]
    near_mean = abs(close - ema200) <= BAD_REGIME_ATR_MULT * atr_i
    flat_or_down = (ema50 - ema50_prev) <= 0.0
    return near_mean and flat_or_down


def _resolve_retest(
    bars: List[Dict[str, Any]],
    breakout_index: int,
    resistance: float,
    atr_at_breakout: float,
) -> Dict[str, Any]:
    """Scan the 10-bar retest window after a breakout. Returns the outcome.

    status in {"signal", "failed", "expired"}; signal_index set iff status=="signal".
    'failed'  = an in-window bar closed back below resistance before any retest-hold.
    'expired' = the window ended with no retest touch (and no failure close).
    """
    n = len(bars)
    threshold = resistance + RETEST_ATR_MULT * atr_at_breakout
    window_end = breakout_index + RETEST_WINDOW
    j = breakout_index + 1
    while j <= window_end and j < n:
        cj = bars[j]["close"]
        if cj < resistance:                     # acceptance lost before a retest-hold
            return {"status": "failed", "signal_index": None, "retest_index": j}
        if bars[j]["low"] <= threshold:         # close>=resistance (implied) AND retest touch
            return {"status": "signal", "signal_index": j, "retest_index": j}
        j += 1
    return {"status": "expired", "signal_index": None, "retest_index": None}


def find_setups_or_entries(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Diagnostic listing of breakout->retest->entry candidates.

    Ignores one-position overlap (it does not simulate management); it DOES apply
    the trend filter, the retest resolution, and the bad-regime suppression so the
    listed 'entry' candidates are the bars that would actually fill.
    """
    ind = compute_indicators(bars)
    atr = ind["atr"]
    n = len(bars)
    out: List[Dict[str, Any]] = []
    for i in range(n):
        if not is_trend_ok(bars, i, ind) or not is_breakout_bar(bars, i, ind):
            continue
        res = prior_resistance(bars, i, RESISTANCE_LOOKBACK)
        atr_b = atr[i]
        r = _resolve_retest(bars, i, res, atr_b)  # type: ignore[arg-type]
        if r["status"] != "signal":
            out.append({
                "breakout_index": i, "signal_index": None,
                "entry_index": None, "setup_status": r["status"],
            })
            continue
        s = r["signal_index"]
        if is_bad_regime(bars, s, ind):
            out.append({
                "breakout_index": i, "signal_index": s,
                "entry_index": None, "setup_status": "suppressed_bad_regime",
            })
            continue
        if s + 1 >= n:
            out.append({
                "breakout_index": i, "signal_index": s,
                "entry_index": None, "setup_status": "no_entry_bar",
            })
            continue
        out.append({
            "breakout_index": i, "signal_index": s,
            "entry_index": s + 1, "setup_status": "entry",
        })
    return out


def simulate_s28(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic long-only S28 simulation. Returns a list of closed trades.

    Pure function: no I/O, no randomness. One position at a time, one active
    setup at a time, no pyramiding, no compounding.
    """
    n = len(bars)
    trades: List[Dict[str, Any]] = []
    if n == 0:
        return trades
    ind = compute_indicators(bars)
    atr = ind["atr"]

    i = 0
    while i < n:
        # 1) Seek a trend-confirmed breakout bar.
        if not is_trend_ok(bars, i, ind) or not is_breakout_bar(bars, i, ind):
            i += 1
            continue

        breakout_index = i
        resistance = prior_resistance(bars, i, RESISTANCE_LOOKBACK)
        atr_at_breakout = atr[i]
        r = _resolve_retest(bars, i, resistance, atr_at_breakout)  # type: ignore[arg-type]

        if r["status"] != "signal":
            # failed or expired -> resume scanning after the breakout bar.
            i = breakout_index + 1
            continue

        s = r["signal_index"]
        # 2) Bad-regime NO-TRADE gate on the signal bar.
        if is_bad_regime(bars, s, ind):
            i = s + 1
            continue

        # 3) Entry at the OPEN of the bar after the retest-hold signal bar.
        entry_index = s + 1
        if entry_index >= n:
            break  # no bar to fill on
        entry_price = bars[entry_index]["open"]
        atr_at_signal = atr[s]
        risk = STOP_ATR_MULT * atr_at_signal  # 1R = 2.0*ATR20 at the signal bar
        stop_price = entry_price - risk
        target_price = entry_price + TARGET_R_MULTIPLE * risk
        pos = {
            "direction": "long",
            "breakout_index": breakout_index,
            "breakout_date": str(bars[breakout_index]["timestamp"].date()),
            "retest_index": s,
            "retest_date": str(bars[s]["timestamp"].date()),
            "signal_index": s,
            "entry_index": entry_index,
            "entry_date": str(bars[entry_index]["timestamp"].date()),
            "resistance": resistance,
            "entry_price": entry_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "atr_at_breakout": atr_at_breakout,
            "atr_at_signal": atr_at_signal,
            "n_at_entry": atr_at_signal,
            "risk": risk,
            "setup_status": "entered",
        }

        # 4) Manage from the bar AFTER the fill bar (entry_index + 1).
        k = entry_index + 1
        closed = False
        while k < n:
            bar = bars[k]
            bars_held = k - entry_index + 1  # fill bar = 1st held bar
            exit_price: Optional[float] = None
            reason: Optional[str] = None
            # Precedence: stop (worst-case) -> target -> time stop on the 20th held bar.
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
                i = k + 1  # new setups only after this position closes
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
    """Frozen S28 hard gate: IS net must stay POSITIVE after removing the top 3 winners.

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
    """Run the S28 long-only strategy over a local CSV. Returns inert data."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    trades = simulate_s28(bars)
    return {
        "r_multiples": [t["r_multiple"] for t in trades],
        "trades": trades,
        "bars_loaded": len(bars),
        "summary": summarize(trades),
        "top3_gate": anti_donchian_top3_gate(trades),
        "accounting": ACCOUNTING_NOTE,
    }
