"""Tests for the SPARTA Prediction Market Factory V1 Research Readiness contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_factory_v1_research_readiness_contract as pm


def test_readiness_ready_and_separate_lane():
    s = pm.build_prediction_market_factory_v1_readiness()
    assert s["verdict"] == pm.VERDICT_PM_READINESS_READY
    assert s["lane"] == "prediction_market_factory_v1"
    assert s["separate_from_arbitrage_factory_v1"] is True
    assert s["modifies_arbitrage_factory_v1_lane"] is False
    assert s["modifies_crypto_d1_lane"] is False
    assert s["next_required_action"] == (
        "HUMAN_APPROVED_PREDICTION_MARKET_SCANNER_SPEC")


def test_six_families_and_roadmap():
    s = pm.build_prediction_market_factory_v1_readiness()
    assert len(s["candidate_families"]) == 6
    assert s["candidate_families"][0] == "PM_F1_yes_no_pricing_inefficiency"
    assert s["candidate_families"][-1] == "PM_F6_pass_watch_fail_report_framework"
    assert [b["block"] for b in s["future_blocks_roadmap"]] == [
        "prediction_market_scanner_spec_contract",
        "prediction_market_data_contract",
        "prediction_market_cost_and_settlement_model_contract",
        "prediction_market_alert_report_schema_contract",
        "prediction_market_lane_review_contract",
        "prediction_market_mission_flow_registration",
    ]


def test_required_data_and_forbidden_data():
    s = pm.build_prediction_market_factory_v1_readiness()
    for needed in ("market_id", "event_id", "outcome_yes_price",
                   "outcome_no_price", "bid_ask_per_outcome", "liquidity_depth",
                   "resolution_date", "market_status",
                   "source_provenance_label",
                   "fee_gas_settlement_cost_assumptions"):
        assert needed in s["required_future_data_types"], needed
    for banned in ("wallet_address", "private_key", "seed_phrase",
                   "account_balance", "positions", "orders", "fills",
                   "deposits_withdrawals", "login_session_cookie_api_key"):
        assert banned in s["forbidden_data"], banned


def test_no_trade_rules_and_constitution():
    s = pm.build_prediction_market_factory_v1_readiness()
    joined = " ".join(s["no_trade_rules"])
    assert "execution_is_absent_by_construction" in joined
    assert "no_wallet_key_login_account" in joined
    assert "per_run_human_approval" in joined
    assert "top_level_architecture_authorization" in joined
    assert s["alerts_and_reports_only"] is True
    assert s["execution_capability_exists"] is False


def test_inert_capabilities_and_gates():
    s = pm.build_prediction_market_factory_v1_readiness()
    for key in ("executes", "writes_files", "runs_scanner", "fetches_data",
                "calls_api", "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate"):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True


def test_validate_passes_and_catches_tampering():
    s = pm.build_prediction_market_factory_v1_readiness()
    assert pm.validate_prediction_market_factory_v1_readiness(s)["valid"] is True
    s2 = pm.build_prediction_market_factory_v1_readiness()
    s2["forbidden_data"].remove("private_key")
    assert pm.validate_prediction_market_factory_v1_readiness(s2)["valid"] is False
    s3 = pm.build_prediction_market_factory_v1_readiness()
    s3["execution_capability_exists"] = True
    v3 = pm.validate_prediction_market_factory_v1_readiness(s3)
    assert v3["valid"] is False
    assert "constitution_flag_wrong:execution_capability_exists" in v3["errors"]
    s4 = pm.build_prediction_market_factory_v1_readiness()
    s4["uses_wallet"] = True
    assert pm.validate_prediction_market_factory_v1_readiness(s4)["valid"] is False


def test_build_is_deterministic():
    assert (pm.build_prediction_market_factory_v1_readiness()
            == pm.build_prediction_market_factory_v1_readiness())


def test_label_action_and_imports_clean():
    assert pm.get_prediction_market_factory_v1_readiness_label() == pm.PM_LABEL
    assert "READ-ONLY" in pm.PM_LABEL and pm.PM_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in pm.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(pm.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
