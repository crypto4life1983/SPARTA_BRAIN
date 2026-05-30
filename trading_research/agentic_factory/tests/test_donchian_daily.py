"""Tests for the offline daily Donchian System-1 baseline. Pure, no I/O.

All scenarios use tiny channel/ATR windows (entry=3, exit=2, atr=2) so the
hand-computed expectations are easy to verify. Bars are synthetic dicts built
by `_bars`; no CSV, no network, no real data are touched.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import donchian_daily as dd  # noqa: E402


def _bars(ohlc):
    """Build bar dicts from a list of (open, high, low, close) tuples."""
    base = datetime(2013, 1, 1)
    out = []
    for i, (o, h, l, c) in enumerate(ohlc):
        out.append(
            {
                "timestamp": base + timedelta(days=i),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
            }
        )
    return out


# Three flat warm-up bars: prior-3 high = 101, prior-3 low = 99, ATR(2) = 2.
_FLAT3 = [(100, 101, 99, 100), (100, 101, 99, 100), (100, 101, 99, 100)]

_PARAMS = dict(entry_channel=3, exit_channel=2, atr_period=2, stop_n_multiple=2.0)


# --- no-lookahead channel calculation --------------------------------------

def test_highest_high_excludes_current_bar():
    bars = _bars([(0, 10, 0, 0), (0, 20, 0, 0), (0, 30, 0, 0), (0, 999, 0, 0)])
    # window of 3 ending at index 3 looks at bars[0:3] only -> never sees 999.
    assert dd._highest_high(bars, 3, 3) == 30.0


def test_lowest_low_excludes_current_bar():
    bars = _bars([(0, 0, 50, 0), (0, 0, 40, 0), (0, 0, 30, 0), (0, 0, -999, 0)])
    assert dd._lowest_low(bars, 3, 3) == 30.0


def test_channel_helpers_return_none_when_insufficient_history():
    bars = _bars([(0, 1, 1, 0), (0, 1, 1, 0)])
    assert dd._highest_high(bars, 2, 3) is None  # end-window < 0
    assert dd._lowest_low(bars, 2, 3) is None
    assert dd._highest_high(bars, 1, 0) is None  # non-positive window


# --- long breakout entry ----------------------------------------------------

def test_long_breakout_entry():
    # bar3 high 102 > prior-3 high 101 -> long at 101, stop 101 - 2N = 97.
    bars = _bars(_FLAT3 + [(101, 102, 101, 102)])
    trades = dd.simulate(bars, **_PARAMS)
    assert len(trades) == 1
    t = trades[0]
    assert t["direction"] == "long"
    assert t["entry_price"] == 101.0
    assert t["n_at_entry"] == 2.0
    assert t["risk"] == 4.0
    assert t["stop_price"] == 97.0
    assert t["exit_reason"] == "end_of_data"  # force-closed at last close


# --- short breakout entry ---------------------------------------------------

def test_short_breakout_entry():
    # bar3 low 98 < prior-3 low 99 -> short at 99, stop 99 + 2N = 103.
    bars = _bars(_FLAT3 + [(99, 99, 98, 98)])
    trades = dd.simulate(bars, **_PARAMS)
    assert len(trades) == 1
    t = trades[0]
    assert t["direction"] == "short"
    assert t["entry_price"] == 99.0
    assert t["risk"] == 4.0
    assert t["stop_price"] == 103.0


# --- exit on opposite 20-day (here: 2-day) channel --------------------------

def test_long_exits_on_opposite_channel():
    # Enter long at 101 (stop 97). bar4 low 98: not stopped (98 > 97), but
    # 98 < prior-2 low (min of bars[2].low 99, bars[3].low 101 = 99) -> channel.
    bars = _bars(_FLAT3 + [(101, 102, 101, 102), (100, 100, 98, 98)])
    trades = dd.simulate(bars, **_PARAMS)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "channel"
    assert t["exit_price"] == 99.0
    assert t["r_multiple"] == (99.0 - 101.0) / 4.0  # -0.5R


def test_long_hard_stop_takes_priority_over_channel():
    # bar4 crashes: low 90 <= stop 97 -> stop exit at 97 = exactly -1R.
    bars = _bars(_FLAT3 + [(101, 102, 101, 102), (100, 100, 90, 92)])
    trades = dd.simulate(bars, **_PARAMS)
    assert len(trades) == 1
    t = trades[0]
    assert t["exit_reason"] == "stop"
    assert t["exit_price"] == 97.0
    assert t["r_multiple"] == -1.0


# --- no pyramiding / one position max ---------------------------------------

def test_no_pyramiding_single_position():
    # Continuous uptrend: every bar after entry is a fresh high that would be a
    # breakout if flat, but a position is already open -> exactly one trade.
    uptrend = [
        (101, 102, 101, 102),
        (102, 103, 102, 103),
        (103, 104, 103, 104),
        (104, 105, 104, 105),
    ]
    bars = _bars(_FLAT3 + uptrend)
    trades = dd.simulate(bars, **_PARAMS)
    assert len(trades) == 1
    assert trades[0]["direction"] == "long"
    assert trades[0]["exit_reason"] == "end_of_data"


# --- empty / too-short data produces no trades ------------------------------

def test_empty_data_no_trades():
    assert dd.simulate([], **_PARAMS) == []


def test_too_short_data_no_trades():
    # Fewer bars than min_index (= max(entry_channel, atr_period+1) = 3).
    bars = _bars([(100, 101, 99, 100), (100, 101, 99, 100)])
    assert dd.simulate(bars, **_PARAMS) == []


# --- deterministic output ---------------------------------------------------

def test_deterministic_output():
    bars = _bars(_FLAT3 + [(101, 102, 101, 102), (100, 100, 98, 98)])
    first = dd.simulate(bars, **_PARAMS)
    second = dd.simulate(bars, **_PARAMS)
    assert first == second


# --- accounting honesty -----------------------------------------------------

def test_accounting_note_is_not_a_reproduction_claim():
    note = dd.ACCOUNTING_NOTE.lower()
    assert "not an s10-d2 reproduction" in note
    assert "simplified" in note
