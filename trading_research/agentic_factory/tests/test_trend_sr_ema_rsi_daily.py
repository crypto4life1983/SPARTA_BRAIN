"""Tests for the S26 Trend + S/R + EMA/RSI long-only daily engine.

Covers the frozen S26-D1 rules: indicator warmup safety, lookahead-safe support
window, the four entry-condition gates (trend / pullback / RSI band /
confirmation), next-bar entry, one-position-at-a-time, the -1R stop, the +2R
target, conservative same-bar stop>target precedence, the EMA50 trend-break
exit, empty/short data, a deterministic multi-trade scenario, and an offline
safety scan of the engine source.

Synthetic-data only. No real NQ data is read here.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import trend_sr_ema_rsi_daily as S

BASE = datetime(2020, 1, 1)


def _bar(k, o, h, l, c):
    return {"timestamp": BASE + timedelta(days=k), "open": o, "high": h, "low": l, "close": c}


def _warmup():
    """200 bars of a gentle (slope 0.3) uptrend -> bullish EMA stack, no pullback."""
    return [
        _bar(i, 100.0 + 0.3 * i, 100.0 + 0.3 * i + 0.3, 100.0 + 0.3 * i - 0.3, 100.0 + 0.3 * i)
        for i in range(200)
    ]


def _pullback_then_signal(bars):
    """Append a 4-bar pullback (200-203) and one long-signal bar (204)."""
    for j, c in enumerate([158.0, 156.5, 155.0, 153.5]):
        i = 200 + j
        bars.append(_bar(i, c + 0.5, c + 0.6, c - 0.5, c))
    bars.append(_bar(204, 153.5, 155.6, 150.5, 155.0))  # signal bar; fill at 205 open
    return bars


def _target_scenario():
    b = _pullback_then_signal(_warmup())
    for j, c in enumerate([156.0, 159.0, 162.0, 165.0, 168.0]):
        i = 205 + j
        b.append(_bar(i, c - 1.0, c + 0.5, c - 1.5, c))  # rally -> hits +2R
    return b


def _stop_scenario():
    b = _pullback_then_signal(_warmup())
    b.append(_bar(205, 155.0, 155.5, 154.0, 154.5))   # fill bar (not managed)
    b.append(_bar(206, 154.0, 154.2, 151.0, 151.5))   # low pierces -1R stop
    b.append(_bar(207, 150.0, 150.3, 149.7, 150.0))
    return b


def _samebar_scenario():
    b = _pullback_then_signal(_warmup())
    b.append(_bar(205, 155.0, 155.5, 154.5, 155.0))   # fill bar
    b.append(_bar(206, 155.0, 160.0, 150.0, 156.0))   # low<=stop AND high>=target
    return b


def _ema50_scenario():
    b = _pullback_then_signal(_warmup())
    b.append(_bar(205, 155.0, 155.5, 154.5, 155.0))   # fill bar
    b.append(_bar(206, 154.0, 154.2, 153.0, 153.0))   # drifts, no stop/target
    b.append(_bar(207, 153.0, 153.2, 152.95, 152.97))  # close < EMA50 -> exit
    return b


def _blocks(nblocks):
    """nblocks repeating pullback->signal->gentle-recovery cycles; each yields
    exactly one +2R target trade."""
    bars = []
    k = 0
    price = 100.0
    for _ in range(200):
        bars.append(_bar(k, price, price + 0.3, price - 0.3, price))
        price += 0.3
        k += 1
    for _ in range(nblocks):
        top = price
        for d in [1.5, 3.0, 4.5, 6.0]:
            c = top - d
            bars.append(_bar(k, c + 0.4, c + 0.5, c - 0.4, c))
            k += 1
        sc = top - 5.0
        bars.append(_bar(k, sc, sc + 0.5, top - 8.0, sc + 1.0))  # signal
        k += 1
        price = sc + 1.0
        for _ in range(20):
            price += 0.3
            bars.append(_bar(k, price - 0.2, price + 0.4, price - 0.4, price))
            k += 1
    return bars


def _gate_setup():
    """A 3-bar fixture + indicator dict where candidate bar i=2 PASSES all gates.
    Tests toggle one field to isolate each gate."""
    bars = [
        _bar(0, 100, 101, 99, 100),
        _bar(1, 100, 101, 99, 100),
        _bar(2, 100, 101, 87, 100),  # low 87 reaches the support zone
    ]
    ind = {
        "ema20": [None, 99.0, 99.0],
        "ema50": [None, 95.0, 95.0],
        "ema200": [None, 90.0, 90.0],
        "rsi": [None, 45.0, 50.0],   # band 40-55, turning up
        "atr": [None, 2.0, 2.0],
        "support": [None, 85.0, 85.0],  # thr = 85 + 1.5*2 = 88 ; low 87 <= 88
    }
    return bars, ind


# 1 — warmup safety: indicators None until warm; no early signals.
def test_warmup_no_early_signals():
    short = _warmup()[:10]
    ind = S.compute_indicators(short)
    assert all(v is None for v in ind["ema200"])
    assert all(v is None for v in ind["atr"])
    assert all(v is None for v in ind["rsi"])
    assert S.long_signal_indices(short) == []
    # A full pure-uptrend warmup (no pullback) must produce no signals.
    assert S.long_signal_indices(_warmup()) == []


# 2 — support window excludes the current bar (no lookahead).
def test_support_window_excludes_current_bar():
    bars = [
        _bar(0, 10, 10, 10, 10),
        _bar(1, 11, 11, 11, 11),
        _bar(2, 12, 12, 12, 12),
        _bar(3, 5, 5, 5, 5),  # current bar has the lowest low
    ]
    # prior 3 bars (0,1,2) only -> min low = 10, NOT the current bar's 5.
    assert S.rolling_low(bars, end=3, window=3) == 10.0
    assert S.rolling_low(bars, end=2, window=2) == 10.0


# 3 — trend filter blocks when stack is not bullish.
def test_trend_filter_blocks():
    bars, ind = _gate_setup()
    assert S.is_long_signal(bars, 2, ind) is True
    ind["ema200"][2] = 101.0  # close 100 not > EMA200
    assert S.is_long_signal(bars, 2, ind) is False
    bars, ind = _gate_setup()
    ind["ema50"][2] = 89.0  # EMA50 < EMA200
    assert S.is_long_signal(bars, 2, ind) is False


# 4 — pullback/retest gate: only fires near the rolling-low support within 1.5 ATR.
def test_pullback_support_gate():
    bars, ind = _gate_setup()
    assert S.is_long_signal(bars, 2, ind) is True
    ind["support"][2] = 80.0  # thr = 80 + 3 = 83 ; low 87 > 83 -> blocked
    assert S.is_long_signal(bars, 2, ind) is False


# 5 — confirmation: RSI band AND (RSI turning up OR close reclaims EMA20).
def test_confirmation_gate():
    bars, ind = _gate_setup()
    assert S.is_long_signal(bars, 2, ind) is True
    # RSI out of band -> blocked.
    ind["rsi"][2] = 60.0
    assert S.is_long_signal(bars, 2, ind) is False
    # In band but neither turning up nor reclaiming EMA20 -> blocked.
    bars, ind = _gate_setup()
    ind["rsi"][1] = 55.0   # rsi[2]=50 < rsi[1]=55 -> not turning up
    ind["ema20"][2] = 101.0  # close 100 < EMA20 101 -> no reclaim
    assert S.is_long_signal(bars, 2, ind) is False


# 6 — entry fills on the NEXT bar, not the signal bar.
def test_entry_is_next_bar():
    trades = S.simulate(_target_scenario())
    assert len(trades) == 1
    t = trades[0]
    assert t["entry_index"] == t["signal_index"] + 1
    # entry price is the fill bar's OPEN.
    bars = _target_scenario()
    assert t["entry_price"] == bars[t["entry_index"]]["open"]


# 7 — one position at a time; no pyramiding (in-position signals never double-open).
def test_one_position_at_a_time():
    trades = S.simulate(_blocks(3))
    assert len(trades) == 3
    for a, b in zip(trades, trades[1:]):
        assert b["entry_index"] > a["exit_index"]  # no overlap


# 8 — stop produces exactly -1R.
def test_stop_is_minus_one_r():
    trades = S.simulate(_stop_scenario())
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop"
    assert trades[0]["r_multiple"] == pytest.approx(-1.0)


# 9 — target produces exactly +2R.
def test_target_is_plus_two_r():
    trades = S.simulate(_target_scenario())
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "target"
    assert trades[0]["r_multiple"] == pytest.approx(2.0)


# 10 — same-bar stop+target -> conservative stop precedence (-1R).
def test_same_bar_stop_beats_target():
    trades = S.simulate(_samebar_scenario())
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop"
    assert trades[0]["r_multiple"] == pytest.approx(-1.0)


# 11 — EMA50 trend-break close exit fires when neither stop nor target hit.
def test_ema50_trend_break_exit():
    trades = S.simulate(_ema50_scenario())
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "ema50_trend_break"
    assert trades[0]["r_multiple"] < 0  # exited below entry, above the -1R stop
    assert trades[0]["r_multiple"] > -1.0


# 12 — empty / short data returns no trades safely.
def test_empty_and_short_data():
    assert S.simulate([]) == []
    assert S.simulate(_warmup()[:5]) == []
    s = S.summarize([])
    assert s["trade_count"] == 0 and s["total_r"] == 0.0


# 13 — deterministic synthetic scenario: expected trade count and total R.
def test_deterministic_scenario_count_and_r():
    trades = S.simulate(_blocks(3))
    assert len(trades) == 3
    assert all(t["exit_reason"] == "target" for t in trades)
    assert sum(t["r_multiple"] for t in trades) == pytest.approx(6.0)
    summ = S.summarize(trades)
    assert summ["trade_count"] == 3
    assert summ["win_rate"] == pytest.approx(1.0)
    assert summ["total_r"] == pytest.approx(6.0)


# 14 — offline safety: engine source has no network/broker/secret tokens.
def test_engine_source_is_offline_inert():
    engine_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "trend_sr_ema_rsi_daily.py",
    )
    with open(engine_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "socket",
        "ccxt", "binance", "bybit", "ib_insync", "alpaca", "api_key",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"
