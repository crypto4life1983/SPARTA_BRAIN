"""Tests for the Factory-D6 sequence-risk / Monte Carlo integration layer.

Covers R-multiple normalization (floats / trade dicts / rejection), the path
metrics (equity curve, max drawdown, longest losing streak, worst window),
top-winner dependence, the seeded order-shuffle and bootstrap distributions, the
conservative verdict mapping, the run battery + standard-schema report builder +
write_report integration, an offline-source token scan, and a no-real-data scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_sequence_risk as Q
from engine import validation_reports as VR


# 1 -- normalize accepts bare floats (order preserved).
def test_normalize_accepts_floats():
    assert Q.normalize_r_multiples([1.0, -2.0, 3.5]) == [1.0, -2.0, 3.5]


# 2 -- normalize accepts trade dicts via 'r_multiple' or 'r'.
def test_normalize_accepts_trade_dicts():
    trades = [{"r_multiple": 1.5}, {"r": -1.0}, {"r_multiple": 2}]
    assert Q.normalize_r_multiples(trades) == [1.5, -1.0, 2.0]


# 3 -- normalize rejects invalid values (bool, str, key-less dict).
def test_normalize_rejects_invalid():
    with pytest.raises(ValueError):
        Q.normalize_r_multiples([True])
    with pytest.raises(ValueError):
        Q.normalize_r_multiples(["1.0"])
    with pytest.raises(ValueError):
        Q.normalize_r_multiples([{"pnl": 1.0}])


# 4 -- equity_curve produces the cumulative R path.
def test_equity_curve_works():
    assert Q.equity_curve([1.0, 2.0, -1.0]) == [1.0, 3.0, 2.0]


# 5 -- max_drawdown on a known example.
def test_max_drawdown_known_example():
    assert Q.max_drawdown([1.0, -2.0, 1.0]) == 2.0


# 6 -- longest_losing_streak on a known example.
def test_longest_losing_streak_known_example():
    assert Q.longest_losing_streak([1.0, -1.0, -1.0, 1.0, -1.0]) == 2


# 7 -- worst_window_sum on a known example.
def test_worst_window_sum_known_example():
    assert Q.worst_window_sum([1.0, -2.0, -3.0, 4.0], 2) == -5.0


# 8 -- top_winner_dependence flags top-3 fragility (net flips without top 3).
def test_top_winner_dependence_identifies_fragility():
    rs = [10.0, 10.0, 10.0, -5.0, -5.0, -5.0, -5.0, -5.0]
    tw = Q.top_winner_dependence(rs)
    assert tw["net_r"] == pytest.approx(5.0)
    assert tw["net_r_ex_top3"] == pytest.approx(-25.0)
    assert tw["passes"] is False
    assert tw["best_trade_share"] > 0.5


# 9 -- trade_order_shuffle is deterministic under a fixed seed.
def test_trade_order_shuffle_deterministic():
    rs = [3.0, -1.0, -1.0, 2.0, -2.0, 4.0, -1.0]
    a = Q.trade_order_shuffle(rs, n_iter=200, seed=11)
    b = Q.trade_order_shuffle(rs, n_iter=200, seed=11)
    assert a == b


# 10 -- bootstrap_resample is deterministic under a fixed seed.
def test_bootstrap_resample_deterministic():
    rs = [3.0, -1.0, -1.0, 2.0, -2.0, 4.0, -1.0]
    a = Q.bootstrap_resample(rs, n_iter=200, seed=11)
    b = Q.bootstrap_resample(rs, n_iter=200, seed=11)
    assert a == b


# 11 -- bootstrap prob(total<=0) is high for a fragile one-winner distribution.
def test_bootstrap_prob_le0_high_for_bad_distribution():
    rs = [10.0] + [-1.0] * 9  # net +1, but the +1 lives in a single trade
    boot = Q.bootstrap_resample(rs, n_iter=3000, seed=0)
    assert boot["prob_total_le_0"] > 0.20


# 12 -- verdict ACCEPTABLE for a healthy, robust distribution.
def test_verdict_acceptable_for_healthy():
    summary = {
        "n_trades": 20,
        "net_positive": True,
        "bootstrap": {"prob_total_le_0": 0.02},
        "top_winner": {"net_r": 30.0, "net_r_ex_top3": 18.0, "best_trade_share": 0.20},
        "shuffle": {"drawdown_tail_extreme": False},
    }
    assert Q.derive_sequence_risk_verdict(summary) == Q.SEQUENCE_RISK_ACCEPTABLE


# 13 -- verdict FRAGILE for a top-winner-dependent distribution.
def test_verdict_fragile_for_top_winner_dependent():
    summary = {
        "n_trades": 10,
        "net_positive": True,
        "bootstrap": {"prob_total_le_0": 0.05},
        "top_winner": {"net_r": 5.0, "net_r_ex_top3": -20.0, "best_trade_share": 2.0},
        "shuffle": {"drawdown_tail_extreme": False},
    }
    assert Q.derive_sequence_risk_verdict(summary) == Q.SEQUENCE_RISK_FRAGILE


# 14 -- verdict INCONCLUSIVE for a mixed / middling case.
def test_verdict_inconclusive_for_mixed():
    summary = {
        "n_trades": 15,
        "net_positive": True,
        "bootstrap": {"prob_total_le_0": 0.15},
        "top_winner": {"net_r": 20.0, "net_r_ex_top3": 8.0, "best_trade_share": 0.40},
        "shuffle": {"drawdown_tail_extreme": False},
    }
    assert Q.derive_sequence_risk_verdict(summary) == Q.SEQUENCE_RISK_INCONCLUSIVE


# 15 -- run_sequence_risk returns the expected top-level keys.
def test_run_sequence_risk_returns_expected_keys():
    rs = [2.0, -1.0, -1.0, 3.0, -1.0, 2.0, -1.0, 1.0]
    out = Q.run_sequence_risk(rs, n_iter=200, seed=0)
    assert set(out.keys()) == {
        "n_trades", "total_r", "net_positive", "top_winner",
        "drawdown", "shuffle", "bootstrap", "verdict",
    }
    assert out["n_trades"] == 8
    assert out["verdict"] in (
        Q.SEQUENCE_RISK_ACCEPTABLE, Q.SEQUENCE_RISK_INCONCLUSIVE,
        Q.SEQUENCE_RISK_FRAGILE,
    )


# 16 -- build_sequence_risk_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    rs = [2.0, -1.0, -1.0, 3.0, -1.0, 2.0, -1.0, 1.0]
    summary = Q.run_sequence_risk(rs, n_iter=200, seed=0)
    rep = Q.build_sequence_risk_report(
        branch_id="S99",
        title="Synthetic Sequence Risk",
        summary=summary,
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_trades.json"],
        data_window={"years": [2020]},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "sequence_risk"
    assert rep["next_allowed_step"] == "regime_breakdown"
    assert rep["verdict"] in (
        Q.SEQUENCE_RISK_ACCEPTABLE, Q.SEQUENCE_RISK_INCONCLUSIVE,
        Q.SEQUENCE_RISK_FRAGILE,
    )
    assert "no_cherry_picked_ordering" in rep["forbidden_actions"]
    assert rep["frozen_parameters"]["n_iter"] == 200


# 17 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    rs = [1.0, -1.0, 2.0, -1.0]
    summary = Q.run_sequence_risk(rs, n_iter=100, seed=0)
    rep = Q.build_sequence_risk_report(
        branch_id="S99",
        title="Synthetic Sequence Risk",
        summary=summary,
        verdict=Q.SEQUENCE_RISK_INCONCLUSIVE,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"]["n_trades"] == 4
    assert loaded["verdict"] == Q.SEQUENCE_RISK_INCONCLUSIVE


# 18 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_sequence_risk.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__", "git",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 19 -- empty R list is handled safely (NO crash, INCONCLUSIVE).
def test_empty_r_list_handled_safely():
    out = Q.run_sequence_risk([], n_iter=100, seed=0)
    assert out["n_trades"] == 0
    assert out["total_r"] == 0.0
    assert out["bootstrap"]["prob_total_le_0"] is None
    assert out["verdict"] == Q.SEQUENCE_RISK_INCONCLUSIVE


# 20 -- module reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_sequence_risk.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"
