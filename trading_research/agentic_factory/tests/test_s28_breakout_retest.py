"""Tests for the S28 Breakout-Retest-with-Volatility-Expansion engine.

Covers the frozen S28-D2 rules: indicator warmup safety, prior-resistance
exclusion of the current bar, the 3-part breakout gate (close>resistance, range
expansion, volume expansion), the 3-part trend filter (incl. the EMA200 slope
gate), the bad-regime NO-TRADE gate, the 10-bar retest window with the
0.25*ATR-at-breakout threshold and the close>=resistance hold, expiry/failure,
next-bar entry, the 2.0*ATR stop (-1R), the +2.0R target, conservative same-bar
stop>target precedence, the 20-bar time stop, one-position/one-setup behaviour,
a deterministic two-trade scenario, and an offline-safety scan of the source.

Synthetic-data only. No real NQ/ES data is read here.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import s28_breakout_retest as S

BASE = datetime(2020, 1, 1)


def _bar(k, o, h, l, c, v=1000.0):
    return {
        "timestamp": BASE + timedelta(days=k),
        "open": o, "high": h, "low": l, "close": c, "volume": v,
    }


def _warmup(n=230, start=100.0, slope=0.5, vol=1000.0):
    """n bars of a gentle uptrend -> warm bullish EMA stack, +EMA200 slope.

    Constant volume and small ranges, so NO bar shows range/volume expansion:
    a pure uptrend produces zero breakout bars and zero trades.
    """
    out = []
    for i in range(n):
        c = start + slope * i
        out.append(_bar(i, c, c + 0.3, c - 0.3, c, vol))
    return out


def _breakout_base():
    """Warmup + a real expansion breakout (230), a retest-hold (231), a fill bar (232).

    Bar 230 closes above the prior-55 high with a wide range and a volume spike;
    bar 231 dips to retest the reclaimed level and closes back above it (signal);
    bar 232 is the fill bar (entry = its open). Tails are appended after 232.
    """
    bars = _warmup()                                            # 0..229
    bars.append(_bar(230, 216.0, 222.0, 216.0, 220.0, 5000.0))  # breakout (expansion)
    bars.append(_bar(231, 219.0, 219.5, 214.0, 216.0, 1000.0))  # retest-hold signal
    bars.append(_bar(232, 216.0, 216.5, 215.5, 216.0, 1000.0))  # fill bar (opens only)
    return bars


def _scenario(tail):
    bars = _breakout_base()
    bars.extend(tail)
    return bars


def _stop_tail():
    return [_bar(233, 216.0, 217.0, 210.0, 212.0, 1000.0)]       # low pierces -1R stop


def _target_tail():
    return [_bar(233, 216.0, 230.0, 216.0, 225.0, 1000.0)]       # high reaches +2R target


def _samebar_tail():
    return [_bar(233, 216.0, 230.0, 210.0, 220.0, 1000.0)]       # low<=stop AND high>=target


def _time_tail():
    # 19 neutral managed bars (233..251) never touching stop/target -> time stop at 251.
    return [_bar(233 + j, 216.0, 216.5, 215.5, 216.0, 1000.0) for j in range(19)]


def _two_trade():
    """First trade stops out (233), market climbs, a second breakout (245) targets.

    Demonstrates one-position / one-active-setup: the second setup is only taken
    after the first position has closed; trades never overlap in time.
    """
    bars = _breakout_base()
    bars.extend(_stop_tail())                                    # trade 1 stops at 233
    prev = 212.0
    for k in range(234, 245):                                    # recovery climb stays < 222
        prev += 0.8
        bars.append(_bar(k, prev, prev + 0.3, prev - 0.3, prev, 1000.0))
    bars.append(_bar(245, 224.0, 230.0, 224.0, 226.0, 5000.0))  # 2nd breakout (expansion)
    bars.append(_bar(246, 226.0, 226.5, 221.0, 226.0, 1000.0))  # 2nd retest-hold signal
    bars.append(_bar(247, 226.0, 226.5, 225.5, 226.0, 1000.0))  # 2nd fill bar
    bars.append(_bar(248, 226.0, 245.0, 226.0, 240.0, 1000.0))  # 2nd trade targets
    return bars


def _trend_fixture():
    """21-bar fixture + ind dict where bar 20 PASSES the trend filter; toggle to break it."""
    n = 21
    bars = [_bar(i, 110.0, 110.5, 109.5, 110.0) for i in range(n)]
    bars[20] = _bar(20, 100.0, 100.5, 99.5, 100.0)
    none = [None] * n
    ind = {"ema50": list(none), "ema200": list(none), "atr": list(none),
           "vol_sma": list(none), "tr": list(none)}
    ind["ema50"][20] = 96.0
    ind["ema200"][20] = 90.0     # close 100 > 90 ; ema50 96 > 90
    ind["ema200"][0] = 88.0      # slope = 90 - 88 = +2 >= 0
    return bars, ind


def _breakout_gate_fixture():
    """57-bar fixture + ind where bar 56 PASSES the breakout gate; toggle to break it."""
    n = 57
    bars = [_bar(i, 109.5, 110.0, 109.0, 109.5, 1000.0) for i in range(56)]
    bars.append(_bar(56, 118.0, 121.0, 118.0, 120.0, 2000.0))
    none = [None] * n
    ind = {"ema50": list(none), "ema200": list(none), "atr": list(none),
           "vol_sma": list(none), "tr": list(none)}
    ind["atr"][56] = 2.0
    ind["tr"][56] = 3.0          # 3.0 >= 1.25*2 = 2.5 -> True
    ind["vol_sma"][56] = 1000.0  # 2000 >= 1.2*1000 = 1200 -> True
    return bars, ind


def _regime_fixture():
    """21-bar fixture + ind where bar 20 IS the bad regime; toggle to leave it."""
    n = 21
    bars = [_bar(i, 100.0, 100.5, 99.5, 101.0) for i in range(n)]
    none = [None] * n
    ind = {"ema50": list(none), "ema200": list(none), "atr": list(none),
           "vol_sma": list(none), "tr": list(none)}
    ind["ema200"][20] = 100.0    # abs(101-100)=1 <= 1.0*2 = 2 -> near mean
    ind["atr"][20] = 2.0
    ind["ema50"][20] = 50.0
    ind["ema50"][0] = 50.0       # EMA50 slope = 0 <= 0 -> flat/down
    return bars, ind


# 1 — warmup safety: indicators None until warm; a pure uptrend yields no trades.
def test_warmup_no_early_signals():
    short = _warmup()[:10]
    ind = S.compute_indicators(short)
    assert all(v is None for v in ind["ema200"])
    assert all(v is None for v in ind["atr"])
    # No range/volume expansion anywhere -> zero breakouts, zero trades.
    assert S.find_setups_or_entries(_warmup()) == []
    assert S.simulate_s28(_warmup()) == []


# 2 — prior resistance is the highest high over the prior 55 bars, EXCLUDING bar i.
def test_prior_resistance_excludes_current_bar():
    bars = [_bar(i, 100.0, 110.0, 99.0, 100.0) for i in range(56)]
    bars[55] = _bar(55, 100.0, 999.0, 99.0, 100.0)  # current bar has a huge high
    res = S.prior_resistance(bars, 55, S.RESISTANCE_LOOKBACK)
    assert res == 110.0                              # excludes bar 55's 999 high
    assert S.prior_resistance(bars, 10, S.RESISTANCE_LOOKBACK) is None  # not warm


# 3 — breakout requires close > prior 55-bar high.
def test_breakout_requires_close_above_resistance():
    bars, ind = _breakout_gate_fixture()
    assert S.is_breakout_bar(bars, 56, ind) is True
    bars[10] = _bar(10, 109.5, 125.0, 109.0, 109.5, 1000.0)  # raise resistance above close
    assert S.prior_resistance(bars, 56, S.RESISTANCE_LOOKBACK) == 125.0
    assert S.is_breakout_bar(bars, 56, ind) is False


# 4 — breakout requires TrueRange >= 1.25 * ATR20.
def test_breakout_requires_range_expansion():
    bars, ind = _breakout_gate_fixture()
    assert S.is_breakout_bar(bars, 56, ind) is True
    ind["tr"][56] = 2.0          # 2.0 >= 1.25*2 = 2.5 -> False
    assert S.is_breakout_bar(bars, 56, ind) is False


# 5 — breakout requires volume >= 1.20 * SMA20(volume).
def test_breakout_requires_volume_expansion():
    bars, ind = _breakout_gate_fixture()
    assert S.is_breakout_bar(bars, 56, ind) is True
    bars[56]["volume"] = 1100.0  # 1100 >= 1.2*1000 = 1200 -> False
    assert S.is_breakout_bar(bars, 56, ind) is False


# 6 — trend filter blocks when close <= EMA200.
def test_trend_blocks_when_close_below_ema200():
    bars, ind = _trend_fixture()
    assert S.is_trend_ok(bars, 20, ind) is True
    ind["ema200"][20] = 101.0    # close 100 not > 101
    assert S.is_trend_ok(bars, 20, ind) is False


# 7 — trend filter blocks when EMA50 <= EMA200.
def test_trend_blocks_when_ema50_below_ema200():
    bars, ind = _trend_fixture()
    ind["ema50"][20] = 89.0      # 89 not > 90
    assert S.is_trend_ok(bars, 20, ind) is False


# 8 — trend filter blocks when EMA200 slope < 0.
def test_trend_blocks_when_ema200_slope_negative():
    bars, ind = _trend_fixture()
    ind["ema200"][0] = 95.0      # slope = 90 - 95 = -5 < 0
    assert S.is_trend_ok(bars, 20, ind) is False


# 9 — bad-regime gate fires only when near-mean AND non-rising EMA50.
def test_bad_regime_gate():
    bars, ind = _regime_fixture()
    assert S.is_bad_regime(bars, 20, ind) is True
    bars, ind = _regime_fixture()
    ind["ema200"][20] = 90.0     # abs(101-90)=11 > 2 -> not near mean
    assert S.is_bad_regime(bars, 20, ind) is False
    bars, ind = _regime_fixture()
    ind["ema50"][0] = 40.0       # EMA50 slope = 50-40 = +10 > 0 -> rising
    assert S.is_bad_regime(bars, 20, ind) is False


# 10 — the retest must occur within 10 bars after the breakout.
def test_retest_must_be_within_ten_bars():
    # No touch inside the window, a touch only at bar 11 -> expired.
    bars = [_bar(0, 100, 100, 100, 100)]
    bars += [_bar(k, 102, 102, 101.5, 102) for k in range(1, 11)]  # bars 1..10, no touch
    bars.append(_bar(11, 102, 102, 100.5, 102))                    # touch is too late
    r = S._resolve_retest(bars, 0, 100.0, 4.0)                     # threshold = 101.0
    assert r["status"] == "expired"
    # A touch on bar 10 (the last in-window bar) DOES signal.
    bars2 = [_bar(0, 100, 100, 100, 100)]
    bars2 += [_bar(k, 102, 102, 101.5, 102) for k in range(1, 10)]
    bars2.append(_bar(10, 102, 102, 100.5, 102))                   # in-window touch
    r2 = S._resolve_retest(bars2, 0, 100.0, 4.0)
    assert r2["status"] == "signal" and r2["signal_index"] == 10


# 11 — retest requires low <= resistance + 0.25 * ATR-at-breakout.
def test_retest_requires_low_within_threshold():
    res, atr_b = 100.0, 4.0                         # threshold = 100 + 0.25*4 = 101.0
    touch = [_bar(0, 100, 100, 100, 100), _bar(1, 101, 101, 101.0, 102)]   # low == 101.0
    assert S._resolve_retest(touch, 0, res, atr_b)["status"] == "signal"
    no_touch = [_bar(0, 100, 100, 100, 100), _bar(1, 102, 102, 101.01, 102)]  # low > 101.0
    assert S._resolve_retest(no_touch, 0, res, atr_b)["status"] == "expired"


# 12 — retest requires close >= resistance (a low-touch that closes below is NOT a signal).
def test_retest_requires_close_hold():
    res, atr_b = 100.0, 4.0
    bars = [_bar(0, 100, 100, 100, 100), _bar(1, 100, 100, 99.0, 99.5)]  # low touches, close < res
    r = S._resolve_retest(bars, 0, res, atr_b)
    assert r["status"] == "failed" and r["signal_index"] is None


# 13 — setup fails if a bar closes back below resistance before any retest-hold.
def test_setup_fails_on_close_below_resistance():
    res, atr_b = 100.0, 4.0
    bars = [_bar(0, 100, 100, 100, 100), _bar(1, 99, 99, 98, 99.0)]      # close 99 < 100
    assert S._resolve_retest(bars, 0, res, atr_b)["status"] == "failed"


# 14 — entry is the OPEN of the bar AFTER the retest-hold signal bar.
def test_entry_is_open_of_bar_after_signal():
    trades = S.simulate_s28(_scenario(_target_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["breakout_index"] == 230
    assert t["signal_index"] == 231 and t["retest_index"] == 231
    assert t["entry_index"] == t["signal_index"] + 1 == 232
    assert t["entry_price"] == _scenario(_target_tail())[232]["open"]


# 15 — one active setup at a time: the single-breakout scenario opens exactly one trade.
def test_one_active_setup_at_a_time():
    trades = S.simulate_s28(_scenario(_target_tail()))
    assert len(trades) == 1
    entries = [e for e in S.find_setups_or_entries(_scenario(_target_tail()))
               if e["setup_status"] == "entry"]
    assert len(entries) == 1 and entries[0]["entry_index"] == 232


# 16 — one position at a time / no pyramiding: two sequential trades never overlap.
def test_one_position_no_overlap():
    trades = S.simulate_s28(_two_trade())
    assert len(trades) == 2
    assert all(t["direction"] == "long" for t in trades)
    assert trades[0]["exit_reason"] == "stop"
    assert trades[1]["exit_reason"] == "target"
    assert trades[1]["entry_index"] > trades[0]["exit_index"]  # opened only after close


# 17 — stop is exactly 2.0*ATR(signal) below entry and produces -1R.
def test_stop_is_two_atr_minus_one_r():
    trades = S.simulate_s28(_scenario(_stop_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "stop"
    assert t["stop_price"] == pytest.approx(t["entry_price"] - 2.0 * t["atr_at_signal"])
    assert t["risk"] == pytest.approx(2.0 * t["atr_at_signal"])
    assert t["r_multiple"] == pytest.approx(-1.0)


# 18 — target is exactly +2.0R (= entry + 4.0*ATR(signal)) and produces +2.0R.
def test_target_is_plus_two_r():
    trades = S.simulate_s28(_scenario(_target_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "target"
    assert t["target_price"] == pytest.approx(t["entry_price"] + 4.0 * t["atr_at_signal"])
    assert t["r_multiple"] == pytest.approx(2.0)


# 19 — same-bar stop+target -> conservative stop precedence (-1R).
def test_same_bar_stop_beats_target():
    trades = S.simulate_s28(_scenario(_samebar_tail()))
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop"
    assert trades[0]["r_multiple"] == pytest.approx(-1.0)


# 20 — time stop fires at the CLOSE of the 20th bar held (entry_index + 19).
def test_time_stop_on_twentieth_bar():
    trades = S.simulate_s28(_scenario(_time_tail()))
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "time_stop"
    assert t["exit_index"] == t["entry_index"] + 19
    assert t["exit_price"] == _scenario(_time_tail())[t["exit_index"]]["close"]


# 21 — empty / short data returns safely.
def test_empty_and_short_data_safe():
    assert S.simulate_s28([]) == []
    assert S.find_setups_or_entries([]) == []
    assert S.simulate_s28(_warmup()[:5]) == []
    assert S.summarize([])["trade_count"] == 0


# 22 — deterministic scenario gives the expected trade count and R.
def test_deterministic_scenario_count_and_r():
    target = S.simulate_s28(_scenario(_target_tail()))
    assert len(target) == 1 and target[0]["r_multiple"] == pytest.approx(2.0)
    stop = S.simulate_s28(_scenario(_stop_tail()))
    assert len(stop) == 1 and stop[0]["r_multiple"] == pytest.approx(-1.0)
    summ = S.summarize(target)
    assert summ["trade_count"] == 1 and summ["total_r"] == pytest.approx(2.0)
    # Anti-Donchian top-3 gate accounting is exposed and correct.
    fragile = [{"r_multiple": r} for r in [10.0, 9.0, 8.0, -1, -1, -1, -1]]
    g = S.anti_donchian_top3_gate(fragile)
    assert g["net_r"] == pytest.approx(23.0) and g["net_r_ex_top3"] == pytest.approx(-4.0)
    assert g["passes"] is False


# 23 — offline safety: engine source has no network/broker/secret tokens.
def test_engine_source_is_offline_inert():
    engine_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "s28_breakout_retest.py",
    )
    with open(engine_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "socket",
        "ccxt", "binance", "bybit", "ib_insync", "alpaca", "api_key",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"
