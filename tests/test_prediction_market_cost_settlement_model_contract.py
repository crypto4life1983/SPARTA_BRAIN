"""Tests for the SPARTA PM Factory V1 Cost & Settlement Model contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_cost_settlement_model_contract as cm
import sparta_commander.prediction_market_data_contract as pd


def _inputs(**overrides):
    inputs = {
        "gross_edge_bps": 120.0, "spread_cost_bps": 30.0, "fee_bps": 20.0,
        "gas_cost_bps": 5.0, "settlement_cost_bps": 10.0,
        "liquidity_penalty_bps": 10.0, "resolution_risk_bps": 15.0,
        "market_status": "open", "data_age_days": 1,
    }
    inputs.update(overrides)
    return inputs


def test_model_ready_on_real_chain():
    m = cm.build_pm_cost_settlement_model()
    assert m["verdict"] == cm.VERDICT_PM_MODEL_READY
    assert m["blockers"] == []
    assert m["data_contract_verdict"] == pd.VERDICT_PM_DATA_READY
    assert m["roadmap_seq"] == 3
    assert m["next_required_action"] == "HUMAN_APPROVED_PM_ALERT_REPORT_SCHEMA"


def test_yes_no_sum_gross_edge():
    g = cm.gross_edge_from_yes_no_sum(0.55, 0.40)
    assert g["computable"] is True
    assert abs(g["gross_edge_bps"] - 500.0) < 1e-9
    assert g["deviation_label"] == "sum_below_one_deviation"
    g2 = cm.gross_edge_from_yes_no_sum(0.60, 0.45)
    assert g2["deviation_label"] == "sum_above_one_deviation"
    bad = cm.gross_edge_from_yes_no_sum(1.4, -0.1)
    assert bad["computable"] is False


def test_net_edge_charges_every_cost_and_passes_when_it_survives():
    r = cm.estimate_pm_net_edge_bps(_inputs())
    assert r["computable"] is True
    # 120 - 30 - 20 - 5 - 10 - 10 - 15 = 30
    assert abs(r["net_edge_bps"] - 30.0) < 1e-9
    assert cm.classify_pm_net_edge(r["net_edge_bps"]) == "PASS"


def test_positive_gross_edge_killed_by_costs_fails():
    r = cm.estimate_pm_net_edge_bps(_inputs(gross_edge_bps=50.0))
    assert r["computable"] is True
    assert r["net_edge_bps"] < 0
    assert cm.classify_pm_net_edge(r["net_edge_bps"]) == "FAIL"


def test_classification_thresholds_and_doubt_is_fail():
    assert cm.classify_pm_net_edge(25.0) == "PASS"
    assert cm.classify_pm_net_edge(10.0) == "WATCH"
    assert cm.classify_pm_net_edge(0.0) == "WATCH"
    assert cm.classify_pm_net_edge(-0.1) == "FAIL"
    assert cm.classify_pm_net_edge(None) == "FAIL"
    assert cm.classify_pm_net_edge(float("nan")) == "FAIL"
    assert cm.classify_pm_net_edge(True) == "FAIL"


def test_non_open_or_stale_markets_refused():
    for status in ("closed", "resolved", "paused"):
        r = cm.estimate_pm_net_edge_bps(_inputs(market_status=status))
        assert r["computable"] is False, status
        assert any("market_not_open_refused" in e for e in r["errors"])
    r2 = cm.estimate_pm_net_edge_bps(_inputs(market_status="trading"))
    assert any("market_status_unknown" in e for e in r2["errors"])
    r3 = cm.estimate_pm_net_edge_bps(_inputs(data_age_days=30))
    assert any("stale_data_refused" in e for e in r3["errors"])
    r4 = cm.estimate_pm_net_edge_bps(_inputs(data_age_days=None))
    assert any("data_age_days_missing" in e for e in r4["errors"])


def test_missing_negative_or_zero_liquidity_costs_refused():
    bad = _inputs()
    del bad["settlement_cost_bps"]
    r = cm.estimate_pm_net_edge_bps(bad)
    assert r["computable"] is False
    assert "missing_or_non_numeric:settlement_cost_bps" in r["errors"]
    r2 = cm.estimate_pm_net_edge_bps(_inputs(fee_bps=-1.0))
    assert "negative_cost:fee_bps" in r2["errors"]
    r3 = cm.estimate_pm_net_edge_bps(_inputs(liquidity_penalty_bps=0.0))
    assert any("zero_liquidity_penalty_refused" in e for e in r3["errors"])


def test_forbidden_private_inputs_refused():
    for bad_key in ("wallet_address", "account_balance", "order_id",
                    "api_key", "session_id"):
        r = cm.estimate_pm_net_edge_bps(_inputs(**{bad_key: 1.0}))
        assert r["computable"] is False, bad_key
        assert any("forbidden_input" in e for e in r["errors"])


def test_gating_blocks_on_bad_upstream():
    assert cm.record_pm_cost_settlement_model(None)["verdict"] == (
        cm.VERDICT_PM_MODEL_BLOCKED)
    dc = pd.build_prediction_market_data_contract()
    dc["uses_wallet"] = True
    m = cm.record_pm_cost_settlement_model(dc)
    assert "data_contract_invalid" in m["blockers"]
    blocked = pd.record_prediction_market_data_contract(None)
    m2 = cm.record_pm_cost_settlement_model(blocked)
    assert "data_contract_not_ready" in m2["blockers"]


def test_inert_and_gates_locked_on_all_paths():
    for m in (cm.build_pm_cost_settlement_model(),
              cm.record_pm_cost_settlement_model(None)):
        assert m["classification_is_research_readiness_not_a_trade_signal"] is True
        assert m["costs_never_default_to_zero"] is True
        assert m["gas_is_a_cost_assumption_only"] is True
        for key in ("executes", "writes_files", "runs_scanner", "fetches_data",
                    "calls_api", "uses_network", "uses_credentials",
                    "uses_wallet", "contains_order_logic", "starts_scheduler",
                    "promotes_gate", "unlocks_downstream_gate"):
            assert m[key] is False, key
        assert m["paper_trading_gate_locked"] is True
        assert m["micro_live_gate_locked"] is True
        assert m["live_gate_locked"] is True


def test_validate_passes_and_catches_tampering():
    ok = cm.build_pm_cost_settlement_model()
    assert cm.validate_pm_cost_settlement_model(ok)["valid"] is True
    assert cm.validate_pm_cost_settlement_model(
        cm.record_pm_cost_settlement_model(None))["valid"] is True
    m1 = cm.build_pm_cost_settlement_model()
    m1["min_net_edge_pass_bps"] = 1.0
    v1 = cm.validate_pm_cost_settlement_model(m1)
    assert v1["valid"] is False and "thresholds_loosened" in v1["errors"]
    m2 = cm.build_pm_cost_settlement_model()
    m2["conservative_assumptions"] = m2["conservative_assumptions"][:2]
    assert cm.validate_pm_cost_settlement_model(m2)["valid"] is False
    m3 = cm.build_pm_cost_settlement_model()
    m3["costs_never_default_to_zero"] = False
    assert cm.validate_pm_cost_settlement_model(m3)["valid"] is False
    m4 = cm.build_pm_cost_settlement_model()
    m4["live_gate_locked"] = False
    assert cm.validate_pm_cost_settlement_model(m4)["valid"] is False


def test_build_and_estimate_deterministic():
    assert cm.build_pm_cost_settlement_model() == cm.build_pm_cost_settlement_model()
    assert cm.estimate_pm_net_edge_bps(_inputs()) == cm.estimate_pm_net_edge_bps(_inputs())


def test_label_action_and_imports_clean():
    assert cm.get_pm_cost_settlement_model_label() == cm.PM_MODEL_LABEL
    assert "READ-ONLY" in cm.PM_MODEL_LABEL and cm.PM_MODEL_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in cm.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(cm.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
