"""Tests for the Factory-D7 friction / slippage-stress integration layer.

Covers per-trade cost application, break-even cost, the cost-ladder scenarios, the
conservative robustness verdict map (robust / sensitive / fragile / fail), the
standard-schema report builder + write_report integration, an offline-source token
scan, empty-input safety, and a no-real-data scan.

Synthetic data only. No real NQ/ES CSVs are read; no strategy is backtested.
"""

import json
import os

import pytest

from engine import validation_friction as FR
from engine import validation_reports as VR


# 1 -- applying a flat per-trade cost subtracts it from each R.
def test_apply_r_cost():
    assert FR.apply_r_cost([1.0, -1.0, 0.5], 0.1) == pytest.approx([0.9, -1.1, 0.4])


# 2 -- break-even cost per trade is the mean R per trade.
def test_break_even_cost():
    assert FR.break_even_cost_per_trade([2.0, -1.0, -1.0, 2.0]) == pytest.approx(0.5)
    assert FR.break_even_cost_per_trade([]) is None


# 3 -- friction scenarios total R correctly at each cost level.
def test_friction_scenario_metrics():
    rs = [1.0, 1.0, 1.0, -1.0]  # baseline net = +2 over 4 trades
    s = FR.friction_scenarios(rs, costs=(0.05, 0.20))
    assert s["trade_count"] == 4
    assert s["baseline_total_r"] == pytest.approx(2.0)
    assert s["scenarios"]["0.05"]["total_r"] == pytest.approx(2.0 - 4 * 0.05)
    assert s["scenarios"]["0.2"]["total_r"] == pytest.approx(2.0 - 4 * 0.20)
    assert s["break_even_cost_per_trade"] == pytest.approx(0.5)


# 4 -- verdict ROBUST when the edge survives the highest tested cost.
def test_verdict_robust():
    s = FR.friction_scenarios([1.0] * 10)  # break-even 1.0 >= 0.20
    assert FR.derive_friction_verdict(s) == FR.FRICTION_ROBUST


# 5 -- verdict SENSITIVE for a thin edge that dies in the mid range.
def test_verdict_sensitive():
    s = FR.friction_scenarios([0.06] * 10)  # break-even 0.06 in (0.02, 0.20)
    assert FR.derive_friction_verdict(s) == FR.FRICTION_SENSITIVE


# 6 -- verdict FRAGILE when the edge dies at the gentlest cost.
def test_verdict_fragile():
    s = FR.friction_scenarios([0.01] * 10)  # break-even 0.01 <= 0.02
    assert FR.derive_friction_verdict(s) == FR.FRICTION_FRAGILE


# 7 -- verdict FAIL when the raw record is already net-negative.
def test_verdict_fail():
    s = FR.friction_scenarios([-0.5, -0.5, 0.2, 0.1])  # net negative
    assert FR.derive_friction_verdict(s) == FR.FRICTION_FAIL


# 8 -- build_friction_report returns a valid D2-schema report.
def test_build_report_valid_schema():
    s = FR.friction_scenarios([1.0, 1.0, -0.5, 0.5])
    rep = FR.build_friction_report(
        branch_id="S99",
        title="Synthetic Friction Stress",
        summary=s,
        source_commits={"engine": "deadbeef"},
        input_files=["data/synthetic_trades.json"],
        data_window={"years": [2020]},
        created_utc="2026-05-30T00:00:00+00:00",
    )
    assert VR.validate_report(rep) == []
    assert rep["module_id"] == "friction_stress"
    assert rep["next_allowed_step"] == "readiness_gate"
    assert rep["frozen_parameters"]["costs_tested"] == list(FR.DEFAULT_COSTS)
    assert "no_cost_cherry_picking" in rep["forbidden_actions"]


# 9 -- write_report integration produces report.json + report.md.
def test_write_report_integration(tmp_path):
    s = FR.friction_scenarios([1.0, -1.0, 2.0, -1.0])
    rep = FR.build_friction_report(
        branch_id="S99",
        title="Synthetic Friction Stress",
        summary=s,
        created_utc="2026-05-30T00:00:00+00:00",
    )
    dest = str(tmp_path / "rep")
    paths = VR.write_report(rep, dest)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    with open(paths["report_json"], "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"]["trade_count"] == 4


# 10 -- module source is offline/inert (no network/broker/dynamic-exec/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_friction.py",
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


# 11 -- empty inputs are handled safely (no crash, FAIL with no edge to stress).
def test_empty_inputs_handled_safely():
    assert FR.apply_r_cost([], 0.1) == []
    s = FR.friction_scenarios([])
    assert s["trade_count"] == 0
    assert s["break_even_cost_per_trade"] is None
    assert FR.derive_friction_verdict(s) == FR.FRICTION_FAIL


# 12 -- module reads no real market data (no CSV/data-loading references).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_friction.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"
