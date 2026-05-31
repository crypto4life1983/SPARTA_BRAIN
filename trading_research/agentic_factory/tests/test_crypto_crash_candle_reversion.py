"""Tests for the CCR1 crypto engine (Crypto Daily Crash-Candle Reversion v1).

Covers the frozen Crypto-D9 rules: the close_t/close_{t-1}-1 return definition,
the ret_1d<=-5% crash trigger (boundary inclusive), the next-bar-open entry fill,
one-position-per-symbol / no-pyramiding, the fixed exit at the close of the 3rd
held bar (entry bar counts as bar 1), the ABSENCE of any protective stop or
profit target, the data_end boundary exit, the long-only-spot invariant (no
short/perp/funding fields), safe handling of empty/short data, a deterministic
hand-checked scenario, the anti-top3 gate pass/fail, multi-symbol summary, and an
offline-safety scan of the engine source.

Synthetic-data only. No real BTC/ETH/SOL data is read here; load_daily_bars and
run_backtest are never called.
"""

from datetime import datetime, timedelta

import pytest

from engine import crypto_crash_candle_reversion as C

BASE = datetime(2020, 1, 1)


def _bar(k, c, o=None, h=None, l=None, v=1000.0):
    o = c if o is None else o
    h = max(o, c) + 2.0 if h is None else h
    l = min(o, c) - 2.0 if l is None else l
    return {
        "timestamp": BASE + timedelta(days=k),
        "open": o, "high": h, "low": l, "close": c, "volume": v,
    }


def _scenario(post_crash_closes, entry_open=None, pre_close=100.0, crash_factor=0.92):
    """Build a single -8% crash candle, then custom post-crash closes.

    Layout (indices):
      0   pre_close (=100.0)
      1   crash: close = pre_close*crash_factor (=92.0 at 0.92) -> ret_1=-8% <= -5%
          -> the ONLY signal is at t=1
      2.. entry bar is 2 (fill at open_2); closes given by post_crash_closes
    """
    bars = [_bar(0, pre_close)]
    crash_close = round(pre_close * crash_factor, 6)
    bars.append(_bar(1, crash_close))
    eo = crash_close if entry_open is None else entry_open
    for offset, c in enumerate(post_crash_closes):
        idx = 2 + offset
        o = eo if offset == 0 else c
        bars.append(_bar(idx, c, o=o))
    return bars


# 1 — ret_1d uses close_t / close_{t-1} - 1, and ret[0] is None.
def test_daily_return_definition():
    bars = [_bar(0, 100.0), _bar(1, 110.0), _bar(2, 99.0)]
    ret = C.daily_return_pct(bars)
    assert ret[0] is None
    assert ret[1] == pytest.approx(110.0 / 100.0 - 1.0)
    assert ret[2] == pytest.approx(99.0 / 110.0 - 1.0)


# 2 — Crash signal fires when ret_1d <= -5% (boundary inclusive).
def test_crash_signal_fires():
    assert C.is_crash_candle(-0.05) is True       # boundary is inclusive
    assert C.is_crash_candle(-0.08) is True
    assert C.is_crash_candle(-0.50) is True


# 3 — Crash signal does NOT fire when ret_1d > -5%.
def test_crash_signal_does_not_fire():
    assert C.is_crash_candle(-0.0499) is False
    assert C.is_crash_candle(0.0) is False
    assert C.is_crash_candle(0.10) is False
    assert C.is_crash_candle(None) is False


# 4 — Entry fills at the next bar's open (open_{t+1}), signal one bar earlier.
def test_entry_fills_next_bar_open():
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    trades = C.simulate_crash_reversion(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["signal_index"] == 1
    assert tr["entry_index"] == 2
    assert tr["entry_price"] == 90.0
    assert tr["entry_price"] == bars[2]["open"]


# 5 — Exit is the close of the 3rd bar after entry.
def test_exit_is_close_of_third_bar():
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    tr = C.simulate_crash_reversion(bars, "BTC")[0]
    assert tr["exit_index"] == 4              # entry_index 2 + (3 - 1)
    assert tr["exit_price"] == 97.0
    assert tr["exit_reason"] == "time_exit"


# 6 — Entry bar counts as bar 1 (so a completed hold is exactly 3 bars).
def test_entry_bar_counts_as_bar_one():
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    tr = C.simulate_crash_reversion(bars, "BTC")[0]
    assert tr["hold_bars"] == 3
    assert tr["exit_index"] == tr["entry_index"] + C.HOLD_BARS - 1


# 7 — One position per symbol (a single entry yields a single trade).
def test_one_position_per_symbol():
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    trades = C.simulate_crash_reversion(bars, "BTC")
    assert len(trades) == 1


# 8 — No pyramiding: a fresh crash while in position is ignored.
def test_no_pyramiding_signals_in_position_ignored():
    # close_2=95, close_3=85.5 -> ret_3 = 85.5/95 - 1 = -10% (a fresh crash) while
    # the t=1 trade is open; find_entries lists BOTH crash candles, but the engine
    # must take only the first and ignore the in-position one.
    bars = _scenario([95.0, 85.5, 90.0], entry_open=90.0)
    assert C.find_entries(bars) == [1, 3]     # both are raw candidates
    trades = C.simulate_crash_reversion(bars, "BTC")
    assert len(trades) == 1                   # but only one trade is taken
    assert trades[0]["exit_reason"] == "time_exit"
    assert trades[0]["exit_index"] == 4


# 9 — No protective stop exists: no stop constant, no stop field/exit reason.
def test_no_stop():
    assert not any("STOP" in name.upper() for name in dir(C))
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    tr = C.simulate_crash_reversion(bars, "BTC")[0]
    assert not any("stop" in key.lower() for key in tr)
    assert "stop" not in tr["exit_reason"]


# 10 — No profit target exists: no target constant, exit reasons are fixed.
def test_no_profit_target():
    assert not any("TARGET" in name.upper() for name in dir(C))
    assert set(C.EXIT_REASONS) == {"time_exit", "data_end"}
    bars = _scenario([200.0, 220.0, 240.0], entry_open=90.0)   # a huge gain
    tr = C.simulate_crash_reversion(bars, "BTC")[0]
    assert tr["exit_reason"] == "time_exit"                    # still exits on bar 3
    assert not any("target" in key.lower() for key in tr)
    assert tr["return_pct"] == pytest.approx(240.0 / 90.0 - 1.0)


# 11 — Long-only spot: direction invariant, and no short/perp/funding fields.
def test_long_only_spot_no_short_perp_funding():
    assert C.DIRECTION == "long_spot"
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    tr = C.simulate_crash_reversion(bars, "BTC")[0]
    assert tr["direction"] == "long_spot"
    for key in tr:
        kl = key.lower()
        assert "short" not in kl
        assert "perp" not in kl
        assert "funding" not in kl
        assert "leverage" not in kl


# 12 — data_end exit when the data ends before the 3-bar horizon completes.
def test_data_end_exit():
    # crash at t=1, entry at index 2, the 3rd held bar would be index 4 but the
    # data ends at index 3 -> exit data_end at the last close (96.0), hold 2 bars.
    bars = _scenario([95.0, 96.0], entry_open=90.0)
    trades = C.simulate_crash_reversion(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["exit_reason"] == "data_end"
    assert tr["exit_index"] == 3
    assert tr["exit_price"] == 96.0
    assert tr["hold_bars"] == 2


# 13 — Empty / short / flat data is handled safely.
def test_empty_and_short_data_safe():
    assert C.simulate_crash_reversion([], "BTC") == []
    assert C.simulate_crash_reversion([_bar(0, 100.0)], "BTC") == []
    assert C.find_entries([]) == []
    flat = [_bar(i, 100.0) for i in range(10)]    # no crash candle anywhere
    assert C.simulate_crash_reversion(flat, "BTC") == []


# 14 — Deterministic hand-checked scenario: exactly one time-exit trade.
def test_deterministic_scenario():
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    trades = C.simulate_crash_reversion(bars, "BTC")
    assert len(trades) == 1
    tr = trades[0]
    assert tr["entry_index"] == 2 and tr["entry_price"] == 90.0
    assert tr["exit_index"] == 4 and tr["exit_price"] == 97.0
    assert tr["exit_reason"] == "time_exit"
    assert tr["hold_bars"] == 3
    assert tr["return_pct"] == pytest.approx(97.0 / 90.0 - 1.0)
    summ = C.summarize(trades)
    assert summ["trade_count"] == 1
    assert summ["total_return_pct"] == pytest.approx(97.0 / 90.0 - 1.0)


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
    closes = [95.0, 96.0, 97.0]
    all_trades = []
    for sym in ("BTC", "ETH", "SOL"):
        all_trades += C.simulate_crash_reversion(_scenario(closes, entry_open=90.0), sym)
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
    bars = _scenario([95.0, 96.0, 97.0], entry_open=90.0)
    assert C.simulate_crash_reversion(bars, "BTC")  # works without any file/network
