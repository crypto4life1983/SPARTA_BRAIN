"""Tests for the continue / park / kill decision logic. Offline, no I/O."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import decision  # noqa: E402


def _metrics(trade_count=50, profit_factor=1.5, win_rate=0.5, max_dd=10.0):
    return {
        "trade_count": float(trade_count),
        "profit_factor": profit_factor,
        "win_rate": win_rate,
        "max_drawdown_pct": max_dd,
    }


def test_too_few_trades_is_kill():
    out = decision.decide(_metrics(trade_count=5))
    assert out["decision"] == decision.KILL


def test_strong_variant_continues():
    out = decision.decide(_metrics(profit_factor=1.5, win_rate=0.5, max_dd=10.0))
    assert out["decision"] == decision.CONTINUE


def test_mediocre_variant_parks():
    # PF above park bar (1.0) but below continue bar (1.30)
    out = decision.decide(_metrics(profit_factor=1.10, win_rate=0.5, max_dd=10.0))
    assert out["decision"] == decision.PARK


def test_weak_variant_is_killed():
    out = decision.decide(_metrics(profit_factor=0.8))
    assert out["decision"] == decision.KILL


def test_high_drawdown_blocks_continue():
    # PF and win rate fine, but drawdown too high -> not continue.
    out = decision.decide(_metrics(profit_factor=1.5, win_rate=0.5, max_dd=40.0))
    assert out["decision"] in (decision.PARK, decision.KILL)
    assert out["decision"] == decision.PARK  # PF still above park bar


def test_custom_thresholds():
    thresholds = {
        "min_trades": 10,
        "continue": {"min_profit_factor": 2.0, "min_win_rate": 0.6, "max_drawdown_pct": 15.0},
        "park": {"min_profit_factor": 1.2},
    }
    out = decision.decide(_metrics(trade_count=12, profit_factor=1.5, win_rate=0.5), thresholds)
    assert out["decision"] == decision.PARK


def test_reasons_present():
    out = decision.decide(_metrics())
    assert isinstance(out["reasons"], list) and out["reasons"]
