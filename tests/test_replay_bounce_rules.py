"""Tests for tools/replay_bounce_rules.py (observation-only replay of support-bounce entries)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

rb = pytest.importorskip("tools.replay_bounce_rules")


def _frame(n: int = 80, base: float = 100.0) -> pd.DataFrame:
    """Flat-ish synthetic daily bars with a known 20-day low of `base - 5` and a known ATR scale."""
    idx = pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC")
    close = np.full(n, base)
    open_ = np.full(n, base)
    high = close + 1.0
    low = close - 1.0
    low[n - 10] = base - 5.0          # the prior 20-day low that don_lo will carry
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                         "volume": np.full(n, 1000.0)}, index=idx)


def _ind(df: pd.DataFrame) -> pd.DataFrame:
    return rb.compute_indicators(df)


def test_don_rule_fires_on_touch_and_hold_but_not_on_close_through():
    df = _frame()
    n = len(df)
    # last bar dips to the prior low, closes up above it -> DON bounce
    df.loc[df.index[-1], ["open", "low", "close", "high"]] = [100.0, 95.0, 101.0, 101.5]
    d = _ind(df)
    m, lvl = rb.rule_mask(d, "DON")
    assert bool(m.iloc[-1]) is True
    assert lvl.iloc[-1] == pytest.approx(95.0)
    # same bar closing BELOW the prior low is D's short, not a bounce
    df2 = _frame()
    df2.loc[df2.index[-1], ["open", "low", "close", "high"]] = [100.0, 93.0, 94.0, 100.5]
    m2, _ = rb.rule_mask(_ind(df2), "DON")
    assert bool(m2.iloc[-1]) is False
    # a red bar (close < open) at the low is not a rejection either
    df3 = _frame()
    df3.loc[df3.index[-1], ["open", "low", "close", "high"]] = [100.0, 95.0, 96.0, 100.5]
    m3, _ = rb.rule_mask(_ind(df3), "DON")
    assert bool(m3.iloc[-1]) is False
    assert n == 80


def test_ema50_rule_needs_uptrend_structure():
    df = _frame()
    d = _ind(df)
    # flat series: ema50 == ema200 == close, so ema50 > ema200 is False -> no EMA50 signal anywhere
    m, _ = rb.rule_mask(d, "EMA50")
    assert not bool(m.any())
    # rising series: ema50 > ema200; last bar dips to ema50 and closes up -> fires
    idx = df.index
    close = np.linspace(80, 100, len(df))
    up = pd.DataFrame({"open": close - 0.2, "high": close + 0.5, "low": close - 0.5, "close": close,
                       "volume": 1000.0}, index=idx)
    dd = _ind(up)
    e50 = float(dd["ema50"].iloc[-1])
    up.loc[idx[-1], ["open", "low", "close", "high"]] = [e50 + 0.1, e50 - 0.05, e50 + 0.3, e50 + 0.6]
    dd = _ind(up)
    m2, lvl = rb.rule_mask(dd, "EMA50")
    assert bool(m2.iloc[-1]) is True
    assert lvl.iloc[-1] == pytest.approx(float(dd["ema50"].iloc[-1]))


def test_exit_builders_and_structural_cap():
    sd = rb.d_exit_sig(100.0, 2.0, "long")
    assert sd["sl"] == 96.0 and sd["tp1"] == pytest.approx(112.0)
    ss = rb.s_exit_sig(100.0, 2.0, 97.0, "long")       # stop 0.5*ATR below the level
    assert ss["sl"] == pytest.approx(96.0) and ss["tp1"] == pytest.approx(112.0)
    assert rb.s_exit_sig(100.0, 2.0, 80.0, "long") is None   # stop distance > 4 ATR -> skipped
    sh = rb.s_exit_sig(100.0, 2.0, 103.0, "short")
    assert sh["sl"] == pytest.approx(104.0) and sh["tp1"] == pytest.approx(88.0)
    assert rb.direction_of("DON_HI_T") == "short" and rb.direction_of("EMA50") == "long"


def test_dedup_one_open_trade_per_symbol_and_rule():
    sigs = [
        {"sym": "A", "rule": "DON", "date": "2025-01-01", "d_exit": {"R": 1.0, "exit_date": "2025-01-10"}},
        {"sym": "A", "rule": "DON", "date": "2025-01-05", "d_exit": {"R": -1.0, "exit_date": "2025-01-20"}},  # overlaps
        {"sym": "A", "rule": "DON", "date": "2025-01-11", "d_exit": {"R": 0.5, "exit_date": "2025-01-15"}},
        {"sym": "A", "rule": "EMA50", "date": "2025-01-05", "d_exit": {"R": 0.2, "exit_date": "2025-01-08"}},
        {"sym": "B", "rule": "DON", "date": "2025-01-05", "d_exit": None},                                   # still open
    ]
    out = rb.dedup(sigs, "d_exit")
    assert [(s["sym"], s["rule"], s["date"]) for s in out] == [
        ("A", "DON", "2025-01-01"), ("A", "EMA50", "2025-01-05"), ("A", "DON", "2025-01-11")]


def _synthetic(rule_R: float, bench_R: float):
    bench = [{"sym": "A", "rule": "ANY_DAY", "date": f"2025-0{1 + i % 9}-1{i % 9}", "direction": "long",
              "d_exit": {"R": bench_R, "exit_date": "2025-12-31"}} for i in range(40)]
    sigs = []
    for i in range(30):
        for rule in rb.RULES:
            sigs.append({"sym": f"S{i}", "rule": rule, "date": f"2025-0{1 + i % 9}-1{i % 9}", "direction": rb.direction_of(rule),
                         "entry": 1.0, "atr": 0.1, "level": 0.9, "regime": "RANGE", "allowed": True, "reason": "",
                         "d_exit": {"R": rule_R, "outcome": "WIN", "exit_date": "2025-12-31"},
                         "s_exit": {"R": 0.1, "outcome": "WIN", "exit_date": "2025-12-31"}})
    return sigs, bench


def test_report_render_is_clean_and_headline_bar_is_strict():
    # dates span two half-years with >= 10 trades each, so stability is defined
    sigs, bench = _synthetic(0.3, -0.1)
    res = rb.build(sigs, bench, "2025-12-31")
    assert res["headline"]["cell"] == "DON_T d_exit gated"
    assert res["headline"]["stable"] is True and res["headline"]["p"] == 1.0 and res["headline"]["finding"] is True
    md = rb.render(res)
    assert rb.check_words(md) == []
    assert "any-day" in md and "DON_T" in md and "Passes the pre-stated bar" in md
    # a rule that only matches the benchmark is not a finding, whatever its own p(mean>0)
    sigs2, bench2 = _synthetic(0.3, 0.5)
    res2 = rb.build(sigs2, bench2, "2025-12-31")
    assert res2["rules"]["DON_T"]["d_exit_gated"]["p_pos"] == 1.0
    assert res2["headline"]["finding"] is False
    assert "Does not pass" in rb.render(res2)


def test_trade_loop_page_lists_the_bounce_report():
    from tools import trade_loop_page
    keys = {k for k, _, _ in trade_loop_page.SECTIONS}
    assert "replay_bounce" in keys
