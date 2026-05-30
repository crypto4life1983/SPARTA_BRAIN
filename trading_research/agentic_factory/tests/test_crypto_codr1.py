"""Tests for the CODR-1 crypto engine (Crypto Oversold-Dip Reversion in Uptrend v1).

Covers the frozen Crypto-D4 rules: SMA200 warmup gating, the close>SMA200 trend
filter, the ret<=-7% shock trigger, the close_t/close_{t-1}-1 return definition,
the next-bar-open entry fill, one-position-per-symbol / no-pyramiding, the -10%
protective close-stop, the 5th-bar time stop, stop-over-time-stop precedence, the
absence of any profit target, the long-only-spot invariant (no short/perp/funding
fields), safe handling of empty/short data, a deterministic hand-checked scenario,
the anti-top3 gate pass/fail, multi-symbol summary, and an offline-safety scan of
the engine source.

Synthetic-data only. No real BTC/ETH/SOL data is read here; load_daily_bars and
run_backtest are never called.
"""

import os
from datetime import datetime, timedelta

import pytest

from engine import crypto_codr1 as C

BASE = datetime(2020, 1, 1)


def _bar(k, c, o=None, h=None, l=None, v=1000.0):
    o = c if o is None else o
    h = max(o, c) + 2.0 if h is None else h
    l = min(o, c) - 2.0 if l is None else l
    return {
        "timestamp": BASE + timedelta(days=k),
        "open": o, "high": h, "low": l, "close": c, "volume": v,
    }


def _scenario(post_dip_closes, entry_open=None, dip_factor=0.92):
    """Build a warmed-up uptrend with a single -8% dip, then custom post-dip closes.

    Layout (indices):
      0..199   flat at 100.0           (warms SMA200; close==SMA so not uptrend)
      200..249 ramp 101..150 (+1/bar)  (lifts close well above the trailing SMA)
      250      dip: close = 150*dip_factor (=138.0 at 0.92) -> ret=-8% <= -7%,
               and 138 > SMA200(~107) so the trend filter still passes -> SIGNAL
      251..    entry bar is 251 (fill at open_251); closes given by post_dip_closes
    The only signal is at t=250, so the only entry fills at open_251.
    """
    bars = [_bar(i, 100.0) for i in range(200)]
    for i in range(200, 250):
        bars.append(_bar(i, 100.0 + (i - 199)))   # 101..150
    dip_close = round(150.0 * dip_factor, 6)
    bars.append(_bar(250, dip_close))
    eo = dip_close if entry_open is None else entry_open
    for offset, c in enumerate(post_dip_closes):
        idx = 251 + offset
        o = eo if offset == 0 else c
        bars.append(_bar(idx, c, o=o))
    return bars


# 1 — SMA200 warmup blocks early entries (fewer than 200 bars -> no trend, no trade).
def test_sma_warmup_blocks_early_entries():
    bars = [_bar(i, 100.0) for i in range(50)]
    bars.append(_bar(50, 100.0 * 0.90))   # a -10% dip but SMA200 not warm
    assert C.find_entries(bars) == []
    assert C.simulate_codr1(bars, "BTC") == []


# 2 — Uptrend requires close_t > SMA200_t (strict).
def test_uptrend_requires_close_above_sma():
    assert C.is_uptrend(101.0, 100.0) is True
    assert C.is_uptrend(100.0, 100.0) is False   # strict, not >=
    assert C.is_uptrend(99.0, 100.0) is False
    assert C.is_uptrend(101.0, None) is False     # SMA not warm


# 3 — Oversold dip requires ret_t <= -7%.
def test_oversold_dip_threshold():
    assert C.is_oversold_dip(-0.07) is True       # boundary is inclusive
    assert C.is_oversold_dip(-0.0699) is False
    assert C.is_oversold_dip(-0.08) is True
    assert C.is_oversold_dip(0.0) is False
    assert C.is_oversold_dip(None) is False


# 4 — ret_t uses close_t / close_{t-1} - 1, and ret[0] is None.
def test_daily_return_definition():
    bars = [_bar(0, 100.0), _bar(1, 110.0), _bar(2, 99.0)]
    ret = C.daily_return_pct(bars)
    assert ret[0] is None
    assert ret[1] == pytest.approx(110.0 / 100.0 - 1.0)
    assert ret[2] == pytest.approx(99.0 / 110.0 - 1.0)


# 5 — Entry fills at the next bar's open (open_{t+1}), signal one bar earlier.
def test_entry_fills_next_bar_open():
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 148.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["signal_index"] == 250
    assert tr["entry_index"] == 251
    assert tr["entry_price"] == 138.0
    assert tr["entry_price"] == bars[251]["open"]


# 6 / 7 — One position per symbol; an in-window qualifying dip does NOT pyramid.
def test_one_position_no_pyramiding():
    # close_252=140, close_253=140*0.92=128.8 -> ret_253=-8% (a fresh dip) while a
    # position is open; it must be ignored (no second/overlapping trade). 128.8/138
    # = -6.7% so it does not trip the -10% stop either; time stop ends the one trade.
    bars = _scenario([139.0, 140.0, 128.8, 135.0, 137.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "time_stop"


# 8 — Protective stop exits when a daily close is <= -10% from entry.
def test_protective_stop_exit():
    # A gradual decline: cumulative-from-entry hits -10% only on bar 254
    # (123/138 = -10.9%), and no intermediate close-to-close move is <= -7%, so no
    # fresh dip signal is created during the hold -> exactly one stop-exit trade.
    bars = _scenario([134.0, 130.0, 126.0, 123.0, 160.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["exit_reason"] == "protective_stop"
    assert tr["exit_index"] == 254              # first close to breach -10% from entry
    assert tr["exit_price"] == 123.0
    assert tr["hold_bars"] == 4                 # bars 251..254 inclusive
    assert tr["return_pct"] == pytest.approx(123.0 / 138.0 - 1.0)


# 9 — Time stop exits at the close of the 5th held bar (entry bar counts as bar 1).
def test_time_stop_exit():
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 148.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    tr = trades[0]
    assert tr["exit_reason"] == "time_stop"
    assert tr["exit_index"] == 255              # 251 + (5 - 1)
    assert tr["hold_bars"] == 5
    assert tr["exit_price"] == 148.0


# 10 — Stop takes precedence over time stop when both occur on the same (5th) bar.
def test_stop_precedence_over_time_stop():
    # closes stay above the stop until bar 255 (the time-stop bar), where
    # 124/138 - 1 = -10.1% <= -10% -> protective stop must win, not time stop.
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 124.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    tr = trades[0]
    assert tr["exit_index"] == 255
    assert tr["exit_reason"] == "protective_stop"


# 11 — No profit target exists: a large gain still exits only via the time stop.
def test_no_profit_target():
    bars = _scenario([150.0, 170.0, 190.0, 210.0, 230.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    tr = trades[0]
    assert tr["exit_reason"] == "time_stop"
    assert tr["return_pct"] == pytest.approx(230.0 / 138.0 - 1.0)
    # engine exposes no profit-target constant of any kind
    assert not any("TARGET" in name.upper() for name in dir(C))
    assert set(C.EXIT_REASONS) == {"protective_stop", "time_stop", "data_end"}


# 12 — Long-only spot: direction invariant, and no short/perp/funding fields.
def test_long_only_spot_no_short_perp_funding():
    assert C.DIRECTION == "long_spot"
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 148.0], entry_open=138.0)
    tr = C.simulate_codr1(bars, "BTC")[0]
    assert tr["direction"] == "long_spot"
    for key in tr:
        kl = key.lower()
        assert "short" not in kl
        assert "perp" not in kl
        assert "funding" not in kl
        assert "leverage" not in kl


# 13 — Empty / short data is handled safely.
def test_empty_and_short_data_safe():
    assert C.simulate_codr1([], "BTC") == []
    assert C.simulate_codr1([_bar(0, 100.0)], "BTC") == []
    assert C.find_entries([]) == []
    flat = [_bar(i, 100.0) for i in range(10)]
    assert C.simulate_codr1(flat, "BTC") == []


# 14 — Deterministic hand-checked scenario: exactly one time-stop trade.
def test_deterministic_scenario():
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 148.0], entry_open=138.0)
    trades = C.simulate_codr1(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["entry_index"] == 251 and tr["entry_price"] == 138.0
    assert tr["exit_index"] == 255 and tr["exit_price"] == 148.0
    assert tr["exit_reason"] == "time_stop"
    assert tr["hold_bars"] == 5
    assert tr["return_pct"] == pytest.approx(148.0 / 138.0 - 1.0)
    assert tr["r_like_return"] == pytest.approx((148.0 / 138.0 - 1.0) / 0.10)
    summ = C.summarize(trades)
    assert summ["trade_count"] == 1
    assert summ["total_return_pct"] == pytest.approx(148.0 / 138.0 - 1.0)


# 15 — Anti-top3 gate passes on a broad edge, fails when net is propped by winners.
def test_anti_top3_gate_pass_and_fail():
    broad = [{"return_pct": r} for r in (0.05, 0.04, 0.03, 0.02, 0.01)]
    g_pass = C.anti_top3_gate(broad)
    assert g_pass["passes_ex_top3"] is True
    assert g_pass["net_ex_top3_return_pct"] == pytest.approx(0.03)

    propped = [{"return_pct": r} for r in (1.0, 0.05, -0.10, -0.10, -0.10, -0.10)]
    g_fail = C.anti_top3_gate(propped)
    assert g_fail["passes_ex_top3"] is False
    assert g_fail["net_ex_top3_return_pct"] < 0.0


# 16 — Multi-symbol summary handles BTC / ETH / SOL together.
def test_multi_symbol_summary():
    closes = [140.0, 142.0, 144.0, 146.0, 148.0]
    all_trades = []
    for sym in ("BTC", "ETH", "SOL"):
        all_trades += C.simulate_codr1(_scenario(closes, entry_open=138.0), sym)
    summ = C.summarize(all_trades)
    assert summ["trade_count"] == 3
    assert set(summ["per_symbol"].keys()) == {"BTC", "ETH", "SOL"}
    assert all(v == 1 for v in summ["per_symbol"].values())


# 17 — Offline-safety scan: the engine source contains no forbidden tokens.
def test_engine_source_offline_safe():
    forbidden = [
        "requests", "urllib", "httpx", "aiohttp", "websockets", "ccxt",
        "bybit", "binance", "databento", "ib_insync", "alpaca",
        "local_secrets", ".env", "api_key", "secret",
    ]
    with open(C.__file__, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in engine source: {hits}"


# 18 — No real CSV/data is used: the offline loaders exist but are never called.
def test_no_real_data_used():
    assert callable(C.load_daily_bars)
    assert callable(C.run_backtest)
    # the whole suite drives the engine from synthetic in-memory bars only
    bars = _scenario([140.0, 142.0, 144.0, 146.0, 148.0], entry_open=138.0)
    assert C.simulate_codr1(bars, "BTC")  # works without any file/network access
