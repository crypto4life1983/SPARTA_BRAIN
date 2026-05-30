"""Tests for the S27 Mean-Reversion-After-Overextension-Inside-Bull-Trend engine.

Covers the frozen S27-D2 rules: indicator warmup safety, the 3-part bull-trend
filter (incl. the EMA200 slope gate), the 3-part overextension trigger, Option-B
reversal confirmation / expiry, next-bar(i+2) entry, the 1.5*ATR stop (-1R), the
+1.5R target, conservative same-bar stop>target precedence, the 10-bar time stop,
long-only behaviour, the anti-Donchian top-3 gate, and an offline-safety scan of
the engine source.

Synthetic-data only. No real NQ/ES data is read here.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import s27_mean_reversion_bull as S

BASE = datetime(2020, 1, 1)


def _bar(k, o, h, l, c):
    return {"timestamp": BASE + timedelta(days=k), "open": o, "high": h, "low": l, "close": c}


def _warmup(n=230, start=100.0, slope=0.5):
    """n bars of a gentle uptrend -> warm bullish EMA stack, positive EMA200 slope."""
    out = []
    for i in range(n):
        c = start + slope * i
        out.append(_bar(i, c, c + 0.3, c - 0.3, c))
    return out


def _dip_base(up=True):
    """Warmup + an 8-bar monotonic decline + (optionally) one reversal up-bar.

    With up=True the trough bar (237) is a confirmed setup; the fill would be the
    OPEN of the next appended bar (239). With up=False the decline has no reversal,
    so no setup is ever confirmed.
    """
    bars = _warmup()
    prev = bars[-1]["close"]  # 214.5 at index 229
    k = 230
    for _ in range(8):
        c = prev - 3.5
        bars.append(_bar(k, prev, prev + 0.3, c - 0.3, c))  # open=prev (gap-down bar)
        prev = c
        k += 1
    # bars[230..237]; trough close at index 237.
    if up:
        # reversal up-bar at 238: close above the trough -> confirms setup at 237.
        bars.append(_bar(238, prev + 0.5, prev + 4.0, prev - 0.5, prev + 3.5))
    else:
        # decline continues (no reversal) -> nothing gets confirmed.
        for _ in range(4):
            c = prev - 3.5
            bars.append(_bar(k, prev, prev + 0.3, c - 0.3, c))
            prev = c
            k += 1
    return bars


def _scenario(tail):
    """_dip_base(up=True) + the fill bar (239) + the supplied managed tail bars."""
    bars = _dip_base(up=True)
    bars.extend(tail)
    return bars


# Fill bar 239 (neutral, near the reversal close ~190) then variant tails.
_FILL = _bar(239, 190.0, 190.5, 189.5, 190.0)


def _stop_tail():
    return [_FILL, _bar(240, 189.0, 189.2, 150.0, 151.0)]  # low pierces the -1R stop


def _target_tail():
    return [_FILL, _bar(240, 191.0, 215.0, 190.5, 210.0)]  # high reaches the +1.5R target


def _samebar_tail():
    return [_FILL, _bar(240, 190.0, 216.0, 150.0, 200.0)]  # low<=stop AND high>=target


def _time_tail():
    # 9 flat managed bars (240..248) never touching stop or target -> time stop at 248.
    return [_FILL] + [_bar(240 + j, 190.0, 191.0, 189.0, 190.0) for j in range(9)]


def _setup_fixture():
    """21-bar fixture + ind dict where candidate bar i=20 PASSES every S27 gate.

    Tests toggle one field to isolate each gate. EMA200 slope reads index 0.
    """
    n = 21
    bars = [_bar(i, 110.0, 110.5, 109.5, 110.0) for i in range(n)]
    bars[20] = _bar(20, 101.0, 101.5, 99.5, 100.0)  # overextended low close 100
    none = [None] * n
    ind = {
        "ema20": list(none), "ema50": list(none),
        "ema200": list(none), "rsi": list(none), "atr": list(none),
    }
    ind["ema20"][20] = 103.0     # close 100 <= 103 - 1*2 = 101 -> True
    ind["atr"][20] = 2.0
    ind["rsi"][20] = 30.0        # <= 35
    ind["ema50"][20] = 96.0
    ind["ema200"][20] = 90.0     # close 100 > 90 ; ema50 96 > 90
    ind["ema200"][0] = 88.0      # slope = 90 - 88 = +2 >= 0
    return bars, ind


# 1 — warmup safety: indicators None until warm; pure uptrend yields no setups.
def test_warmup_no_early_setups():
    short = _warmup()[:10]
    ind = S.compute_indicators(short)
    assert all(v is None for v in ind["ema200"])
    assert all(v is None for v in ind["atr"])
    assert all(v is None for v in ind["rsi"])
    # A pure uptrend (no overextension) confirms no entries and no trades.
    assert S.find_entries(_warmup()) == []
    assert S.simulate_s27(_warmup()) == []


# 2 — bull-trend filter requires all three conditions.
def test_bull_trend_requires_all_three():
    bars, ind = _setup_fixture()
    assert S.is_bull_trend(bars, 20, ind) is True
    ind["ema200"][20] = 101.0   # close 100 not > EMA200
    assert S.is_bull_trend(bars, 20, ind) is False
    bars, ind = _setup_fixture()
    ind["ema50"][20] = 89.0     # EMA50 < EMA200
    assert S.is_bull_trend(bars, 20, ind) is False


# 3 — a falling (negative-slope) EMA200 blocks even with a bullish stack.
def test_falling_ema200_slope_blocks():
    bars, ind = _setup_fixture()
    assert S.is_bull_trend(bars, 20, ind) is True
    ind["ema200"][0] = 95.0     # slope = 90 - 95 = -5 < 0 -> blocked
    assert S.is_bull_trend(bars, 20, ind) is False
    assert S.is_overextended_setup(bars, 20, ind) is False


# 4 — overextension trigger requires all three conditions.
def test_overextension_requires_all_three():
    bars, ind = _setup_fixture()
    assert S.is_overextended_setup(bars, 20, ind) is True
    # (a) not 1 ATR below EMA20.
    ind["ema20"][20] = 101.0    # 100 <= 101 - 2 = 99 -> False
    assert S.is_overextended_setup(bars, 20, ind) is False
    # (b) RSI not oversold.
    bars, ind = _setup_fixture()
    ind["rsi"][20] = 40.0       # > 35
    assert S.is_overextended_setup(bars, 20, ind) is False
    # (c) close not the lowest of the last 5.
    bars, ind = _setup_fixture()
    bars[18] = _bar(18, 99.0, 99.5, 98.5, 99.0)  # an earlier lower close
    assert S.is_overextended_setup(bars, 20, ind) is False


# 5 — setup expires if the next bar does NOT close higher (no Option-B reversal).
def test_setup_expires_without_reversal():
    # Monotonic decline, no up-bar -> nothing confirmed -> no entries / no trades.
    bars = _dip_base(up=False)
    assert S.find_entries(bars) == []
    assert S.simulate_s27(bars) == []
    # Direct unit check of the confirmation predicate.
    two = [_bar(0, 10, 10, 9, 9.0), _bar(1, 9, 9, 8, 8.0)]   # close falls
    assert S.is_reversal_confirmed(two, 0) is False
    two_up = [_bar(0, 10, 10, 9, 9.0), _bar(1, 9, 11, 9, 10.0)]  # close rises
    assert S.is_reversal_confirmed(two_up, 0) is True


# 6 — a confirmed reversal enters at the OPEN of bar i+2 (not the setup close or i+1).
def test_entry_is_open_of_i_plus_two():
    bars = _scenario(_target_tail())
    trades = S.simulate_s27(bars)
    assert len(trades) == 1
    t = trades[0]
    assert t["entry_index"] == t["signal_index"] + 2
    assert t["confirm_index"] == t["signal_index"] + 1
    assert t["entry_price"] == bars[t["entry_index"]]["open"]


# 7 — stop is exactly 1.5*ATR below entry and produces -1R.
def test_stop_is_one_and_half_atr_minus_one_r():
    bars = _scenario(_stop_tail())
    trades = S.simulate_s27(bars)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "stop"
    assert t["stop_price"] == pytest.approx(t["entry_price"] - 1.5 * t["n_at_entry"])
    assert t["risk"] == pytest.approx(1.5 * t["n_at_entry"])
    assert t["r_multiple"] == pytest.approx(-1.0)


# 8 — target is exactly +1.5R (= entry + 2.25*ATR) and produces +1.5R.
def test_target_is_plus_one_and_half_r():
    bars = _scenario(_target_tail())
    trades = S.simulate_s27(bars)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "target"
    assert t["target_price"] == pytest.approx(t["entry_price"] + 2.25 * t["n_at_entry"])
    assert t["r_multiple"] == pytest.approx(1.5)


# 9 — same-bar stop+target -> conservative stop precedence (-1R).
def test_same_bar_stop_beats_target():
    bars = _scenario(_samebar_tail())
    trades = S.simulate_s27(bars)
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop"
    assert trades[0]["r_multiple"] == pytest.approx(-1.0)


# 10 — time stop fires at the CLOSE of the 10th bar held (entry_index + 9).
def test_time_stop_on_tenth_bar():
    bars = _scenario(_time_tail())
    trades = S.simulate_s27(bars)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "time_stop"
    assert t["exit_index"] == t["entry_index"] + 9
    assert t["exit_price"] == bars[t["exit_index"]]["close"]


# 11 — long-only: every trade is long, and a market with no bull trend yields none.
def test_long_only_and_no_trades_without_bull_trend():
    for tail in (_stop_tail(), _target_tail(), _time_tail()):
        for t in S.simulate_s27(_scenario(tail)):
            assert t["direction"] == "long"
    # Pure downtrend: never passes the bull-trend filter -> no trades.
    down = [_bar(i, 200 - 0.5 * i, 200 - 0.5 * i + 0.3, 200 - 0.5 * i - 0.3, 200 - 0.5 * i)
            for i in range(230)]
    assert S.simulate_s27(down) == []


# 12 — anti-Donchian top-3 gate: passes only if IS net stays positive ex top 3.
def test_anti_donchian_top3_gate():
    # Net positive but carried by 3 fat winners -> removing them flips negative (FAIL).
    fragile = [{"r_multiple": r} for r in [10.0, 9.0, 8.0, -1, -1, -1, -1, -1, -1, -1]]
    g = S.anti_donchian_top3_gate(fragile)
    assert g["net_r"] == pytest.approx(20.0)
    assert g["net_r_ex_top3"] == pytest.approx(-7.0)
    assert g["passes"] is False
    # Broad-based winners -> still positive after removing top 3 (PASS).
    robust = [{"r_multiple": r} for r in [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, -1, -1, -1, -1]]
    g2 = S.anti_donchian_top3_gate(robust)
    assert g2["net_r"] == pytest.approx(5.0)
    assert g2["net_r_ex_top3"] == pytest.approx(0.5)
    assert g2["passes"] is True


# 13 — one position at a time; the engine opens exactly one trade in the scenario.
def test_one_position_at_a_time():
    trades = S.simulate_s27(_scenario(_time_tail()))
    assert len(trades) == 1
    # empty / short data is safe.
    assert S.simulate_s27([]) == []
    assert S.simulate_s27(_warmup()[:5]) == []


# 14 — offline safety: engine source has no network/broker/secret tokens.
def test_engine_source_is_offline_inert():
    engine_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "s27_mean_reversion_bull.py",
    )
    with open(engine_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "socket",
        "ccxt", "binance", "bybit", "ib_insync", "alpaca", "api_key",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"
