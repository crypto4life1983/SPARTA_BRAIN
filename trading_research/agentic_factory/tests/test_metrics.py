"""Tests for the pure metric functions. Offline, no I/O."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import metrics  # noqa: E402


def test_empty_inputs():
    assert metrics.trade_count([]) == 0
    assert metrics.win_rate([]) == 0.0
    assert metrics.profit_factor([]) == 0.0
    assert metrics.expectancy([]) == 0.0
    assert metrics.max_drawdown_r([]) == 0.0
    assert metrics.max_drawdown_pct([]) == 0.0
    assert metrics.sharpe_like([]) == 0.0


def test_win_rate():
    assert metrics.win_rate([1.0, -1.0, 2.0, -1.0]) == 0.5
    assert metrics.win_rate([1.0, 2.0]) == 1.0
    assert metrics.win_rate([-1.0, -1.0]) == 0.0


def test_profit_factor():
    # gross profit 3, gross loss 2 -> 1.5
    assert metrics.profit_factor([2.0, 1.0, -1.0, -1.0]) == 1.5
    # profits but no losses -> inf
    assert metrics.profit_factor([1.0, 2.0]) == math.inf
    # no profits -> 0.0
    assert metrics.profit_factor([-1.0, -2.0]) == 0.0


def test_expectancy():
    assert metrics.expectancy([2.0, -1.0, 2.0, -1.0]) == 0.5


def test_equity_curve():
    assert metrics.equity_curve([1.0, -1.0, 2.0]) == [1.0, 0.0, 2.0]


def test_max_drawdown_r():
    # peak 3 then down to 1 -> dd of 2 R
    r = [2.0, 1.0, -1.0, -1.0, 3.0]
    assert metrics.max_drawdown_r(r) == 2.0
    # monotonically rising -> 0
    assert metrics.max_drawdown_r([1.0, 1.0, 1.0]) == 0.0


def test_max_drawdown_pct():
    # peak 3, trough 1 -> (3-1)/3*100 = 66.66..%
    r = [3.0, -2.0]
    assert abs(metrics.max_drawdown_pct(r) - (2.0 / 3.0 * 100.0)) < 1e-9


def test_sharpe_like_zero_variance():
    assert metrics.sharpe_like([1.0, 1.0, 1.0]) == 0.0
    assert metrics.sharpe_like([1.0]) == 0.0


def test_summarize_keys():
    out = metrics.summarize([1.0, -1.0, 2.0])
    for key in [
        "trade_count",
        "win_rate",
        "profit_factor",
        "expectancy_r",
        "max_drawdown_r",
        "max_drawdown_pct",
        "sharpe_like",
    ]:
        assert key in out
