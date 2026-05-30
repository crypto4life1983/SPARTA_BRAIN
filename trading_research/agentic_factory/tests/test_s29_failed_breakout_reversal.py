"""Tests for the S29 Failed-Breakout / False-Break Reversal engine.

Covers the frozen S29-D2 rules: indicator warmup safety, prior-20-low exclusion
of the current bar, the two-part false-downside-break trigger (low pierces the
prior low intrabar AND close returns above it), the Option-B regime guard (block
only a confirmed both-bearish downtrend), next-bar-open entry, the LEVEL-based
stop (signal_low - 0.25*ATR20) and 1R = entry - stop, the +1.5R target,
conservative same-bar stop>target precedence, the 10-bar time stop, one-position
behaviour, a deterministic two-trade scenario, the anti-Donchian top-3 gate, the
long-only invariant, and an offline-safety scan of the engine source.

Synthetic-data only. No real NQ/ES data is read here; load_daily_bars is never
called.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import s29_failed_breakout_reversal as S

BASE = datetime(2020, 1, 1)


def _bar(k, o, h, l, c, v=1000.0):
    return {
        "timestamp": BASE + timedelta(days=k),
        "open": o, "high": h, "low": l, "close": c, "volume": v,
    }


def _warmup(n=230, start=100.0, slope=0.5):
    """n bars of a gentle monotonic uptrend -> warm bullish EMA stack.

    Lows ascend with price, so no bar ever pierces the prior-20-low: a pure
    uptrend produces zero false breaks and zero trades.
    """
    out = []
    for i in range(n):
        c = start + slope * i
        out.append(_bar(i, c, c + 0.3, c - 0.3, c))
    return out


def _falsebreak_base():
    """Warmup (0..229) + a false-downside-break signal (230) + a fill bar (231).

    Bar 230 dips its LOW below the prior-20-low (min low over 210..229 = 204.7)
    but closes back well above it -> a false break; bar 231 is the fill bar whose
    OPEN (215.0) is the entry. Tails are appended after 231.
    """
    bars = _warmup()                                          # 0..229
    bars.append(_bar(230, 215.0, 215.5, 203.0, 215.0))        # false-break signal
    bars.append(_bar(231, 215.0, 215.5, 214.5, 215.0))        # fill bar (opens only)
    return bars


def _scenario(tail):
    bars = _falsebreak_base()
    bars.extend(tail)
    return bars


def _stop_tail():
    # low pierces the level stop (~202.5); high stays below the target.
    return [_bar(232, 215.0, 216.0, 195.0, 205.0)]


def _target_tail():
    # high reaches the +1.5R target (~233.7); low stays above the stop.
    return [_bar(232, 215.0, 240.0, 214.0, 230.0)]


def _samebar_tail():
    # low<=stop AND high>=target in one bar -> conservative stop-first.
    return [_bar(232, 215.0, 240.0, 195.0, 220.0)]


def _time_tail():
    # 9 neutral managed bars (232..240) touching neither stop nor target ->
    # time stop on the 10th held bar (entry_index 231 + 9 = 240).
    return [_bar(232 + j, 215.0, 216.0, 214.0, 215.0) for j in range(9)]


def _two_trade():
    """First trade stops out (232), price plateaus, a second false break targets.

    Demonstrates one position at a time: the second setup is taken only after the
    first position closes; the trades never overlap in time.
    """
    bars = _falsebreak_base()                                 # 0..231
    bars.append(_bar(232, 215.0, 216.0, 200.0, 205.0))        # trade 1 stops out
    for k in range(233, 253):                                 # plateau 233..252 (no breaks)
        bars.append(_bar(k, 218.0, 218.4, 217.6, 218.0))
    bars.append(_bar(253, 218.0, 218.4, 215.0, 218.0))        # 2nd false-break signal
    bars.append(_bar(254, 218.0, 218.4, 217.6, 218.0))        # 2nd fill bar (entry 218)
    bars.append(_bar(255, 218.0, 230.0, 217.0, 226.0))        # 2nd trade targets (+1.5R)
    return bars


def _regime_fixture():
    """21-bar fixture + ind where bar 20 IS a confirmed downtrend; toggle to unblock."""
    n = 21
    bars = [_bar(i, 100.0, 100.5, 99.5, 100.0) for i in range(n)]
    none = [None] * n
    ind = {"ema50": list(none), "ema200": list(none), "atr": list(none)}
    ind["ema200"][20] = 110.0    # close 100 < 110 -> below the slow line
    ind["ema50"][20] = 105.0     # ema50 105 < ema200 110 -> confirmed downtrend
    return bars, ind


# 1 — warmup safety: indicators None until warm; a pure uptrend yields no trades.
def test_warmup_no_early_signals():
    short = _warmup()[:10]
    ind = S.compute_indicators(short)
    assert all(v is None for v in ind["ema200"])
    assert all(v is None for v in ind["atr"])
    assert S.find_entries(_warmup()) == []
    assert S.simulate_s29(_warmup()) == []


# 2 — prior low is the lowest low over the prior 20 bars, EXCLUDING bar i.
def test_prior_low_excludes_current_bar():
    bars = [_bar(i, 100.0, 101.0, 99.0, 100.0) for i in range(21)]
    bars[20] = _bar(20, 100.0, 101.0, 1.0, 100.0)   # current bar has a tiny low
    assert S.prior_low(bars, 20, S.LOOKBACK_N) == 99.0    # excludes bar 20's 1.0
    assert S.prior_low(bars, 10, S.LOOKBACK_N) is None    # not warm (i < lookback)


# 3 — false break requires the low to pierce BELOW the prior-20-low.
def test_false_break_requires_low_below_prior_low():
    bars = [_bar(i, 100.0, 101.0, 99.0, 100.0) for i in range(21)]   # prior-20-low = 99.0
    bars[20] = _bar(20, 100.0, 101.0, 98.0, 100.0)   # low 98 < 99 AND close 100 > 99
    assert S.is_false_downside_break(bars, 20) is True
    bars[20] = _bar(20, 100.0, 101.0, 99.5, 100.0)   # low 99.5 not < 99
    assert S.is_false_downside_break(bars, 20) is False


# 4 — false break requires the CLOSE to return above the prior-20-low.
def test_false_break_requires_close_above_prior_low():
    bars = [_bar(i, 100.0, 101.0, 99.0, 100.0) for i in range(21)]   # prior-20-low = 99.0
    bars[20] = _bar(20, 100.0, 101.0, 98.0, 98.5)    # pierced but closed BELOW -> real break
    assert S.is_false_downside_break(bars, 20) is False
    bars[20] = _bar(20, 100.0, 101.0, 98.0, 99.5)    # pierced and closed back above
    assert S.is_false_downside_break(bars, 20) is True
    bars[20] = _bar(20, 100.0, 101.0, 98.0, 99.0)    # close == prior low (not strictly above)
    assert S.is_false_downside_break(bars, 20) is False


# 5 — regime guard blocks a confirmed both-bearish downtrend.
def test_regime_blocks_confirmed_downtrend():
    bars, ind = _regime_fixture()
    assert S.is_regime_blocked(bars, 20, ind) is True


# 6 — regime guard does NOT block when close is at/above EMA200.
def test_regime_not_blocked_when_close_above_ema200():
    bars, ind = _regime_fixture()
    ind["ema200"][20] = 95.0     # close 100 >= 95 -> not a confirmed downtrend
    assert S.is_regime_blocked(bars, 20, ind) is False


# 7 — regime guard does NOT block when EMA50 is at/above EMA200.
def test_regime_not_blocked_when_ema50_above_ema200():
    bars, ind = _regime_fixture()
    ind["ema50"][20] = 115.0     # ema50 115 >= ema200 110 -> not a confirmed downtrend
    assert S.is_regime_blocked(bars, 20, ind) is False


# 8 — entry is the OPEN of the bar AFTER the false-break signal bar.
def test_entry_is_open_of_bar_after_signal():
    sc = _scenario(_target_tail())
    trades = S.simulate_s29(sc)
    assert len(trades) == 1
    t = trades[0]
    assert t["signal_index"] == 230
    assert t["entry_index"] == t["signal_index"] + 1 == 231
    assert t["entry_price"] == sc[231]["open"]
    assert t["signal_low"] == sc[230]["low"] == 203.0


# 9 — stop is LEVEL-based (signal_low - 0.25*ATR20) and produces -1R.
def test_stop_is_level_based_minus_one_r():
    trades = S.simulate_s29(_scenario(_stop_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "stop"
    assert t["stop_price"] == pytest.approx(
        t["signal_low"] - 0.25 * t["atr_at_signal"]
    )
    assert t["r_multiple"] == pytest.approx(-1.0)


# 10 — 1R is exactly entry_open minus the level stop.
def test_one_r_equals_entry_minus_stop():
    t = S.simulate_s29(_scenario(_target_tail()))[0]
    assert t["risk"] == pytest.approx(t["entry_price"] - t["stop_price"])
    assert t["risk"] > 0.0


# 11 — target is exactly +1.5R and produces +1.5R.
def test_target_is_plus_one_point_five_r():
    trades = S.simulate_s29(_scenario(_target_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "target"
    assert t["target_price"] == pytest.approx(t["entry_price"] + 1.5 * t["risk"])
    assert t["r_multiple"] == pytest.approx(1.5)


# 12 — same-bar stop+target -> conservative stop precedence (-1R).
def test_same_bar_stop_beats_target():
    trades = S.simulate_s29(_scenario(_samebar_tail()))
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop"
    assert trades[0]["r_multiple"] == pytest.approx(-1.0)


# 13 — time stop fires at the CLOSE of the 10th bar held (entry_index + 9).
def test_time_stop_on_tenth_bar():
    sc = _scenario(_time_tail())
    trades = S.simulate_s29(sc)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "time_stop"
    assert t["exit_index"] == t["entry_index"] + 9
    assert t["exit_price"] == sc[t["exit_index"]]["close"]


# 14 — one position at a time / no pyramiding: two sequential trades never overlap.
def test_one_position_no_overlap():
    trades = S.simulate_s29(_two_trade())
    assert len(trades) == 2
    assert all(t["direction"] == "long" for t in trades)
    assert trades[0]["exit_reason"] == "stop"
    assert trades[1]["exit_reason"] == "target"
    assert trades[1]["entry_index"] > trades[0]["exit_index"]  # opened only after close


# 15 — empty / short data returns safely.
def test_empty_and_short_data_safe():
    assert S.simulate_s29([]) == []
    assert S.find_entries([]) == []
    assert S.simulate_s29(_warmup()[:5]) == []
    assert S.summarize([])["trade_count"] == 0


# 16 — deterministic scenarios give the expected trade count and R.
def test_deterministic_scenario_count_and_r():
    target = S.simulate_s29(_scenario(_target_tail()))
    assert len(target) == 1 and target[0]["r_multiple"] == pytest.approx(1.5)
    stop = S.simulate_s29(_scenario(_stop_tail()))
    assert len(stop) == 1 and stop[0]["r_multiple"] == pytest.approx(-1.0)
    summ = S.summarize(target)
    assert summ["trade_count"] == 1 and summ["total_r"] == pytest.approx(1.5)


# 17 — anti-Donchian top-3 gate accounting is exposed and correct.
def test_anti_donchian_gate_pass_and_fail():
    fragile = [{"r_multiple": r} for r in [10.0, 9.0, 8.0, -1, -1, -1, -1]]
    g = S.anti_donchian_top3_gate(fragile)
    assert g["net_r"] == pytest.approx(23.0)
    assert g["net_r_ex_top3"] == pytest.approx(-4.0)
    assert g["passes"] is False
    robust = [{"r_multiple": r} for r in [3.0, 2.0, 1.5, 1.0, 1.0, 1.0, -1.0]]
    g2 = S.anti_donchian_top3_gate(robust)
    assert g2["net_r_ex_top3"] == pytest.approx(2.0)
    assert g2["passes"] is True


# 18 — long-only invariant: the engine never emits a short trade or short fields.
def test_long_only_no_short_fields():
    for sc in (_scenario(_target_tail()), _scenario(_stop_tail()), _two_trade()):
        for t in S.simulate_s29(sc):
            assert t["direction"] == "long"
            assert "short" not in t["direction"]


# 19 — find_entries lists exactly one fillable entry for the single-break scenario.
def test_find_entries_reports_single_entry():
    entries = [e for e in S.find_entries(_scenario(_target_tail()))
               if e["setup_status"] == "entry"]
    assert len(entries) == 1
    assert entries[0]["signal_index"] == 230
    assert entries[0]["entry_index"] == 231


# 20 — offline safety: engine source has no network/broker/secret tokens.
def test_engine_source_is_offline_inert():
    engine_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "s29_failed_breakout_reversal.py",
    )
    with open(engine_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "socket",
        "ccxt", "binance", "bybit", "ib_insync", "alpaca", "api_key",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"
