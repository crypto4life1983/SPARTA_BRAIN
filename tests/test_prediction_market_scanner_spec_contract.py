"""Tests for the SPARTA Prediction Market Factory V1 Scanner Spec contract."""

from __future__ import annotations

import ast

import sparta_commander.prediction_market_factory_v1_research_readiness_contract as pr
import sparta_commander.prediction_market_scanner_spec_contract as ps


def test_spec_ready_on_real_chain_and_scanner_not_built():
    s = ps.build_prediction_market_scanner_spec()
    assert s["verdict"] == ps.VERDICT_PM_SPEC_READY
    assert s["blockers"] == []
    assert s["readiness_verdict"] == pr.VERDICT_PM_READINESS_READY
    assert s["lane"] == "prediction_market_factory_v1"
    assert s["roadmap_seq"] == 1
    assert s["scanner_built_by_this_contract"] is False
    assert s["reports_root"] == "reports/prediction_market_factory_v1/"
    assert s["next_required_action"] == (
        "HUMAN_APPROVED_PREDICTION_MARKET_DATA_CONTRACT")


def test_families_inputs_and_forbidden_inputs():
    s = ps.build_prediction_market_scanner_spec()
    assert tuple(s["accepted_families"]) == pr.CANDIDATE_FAMILIES
    for t in ("market_id", "event_id", "outcome_yes_price", "outcome_no_price",
              "yes_bid", "yes_ask", "no_bid", "no_ask", "liquidity_depth",
              "resolution_date", "market_status", "provenance_label",
              "fee_gas_settlement_cost_assumptions"):
        assert t in s["allowed_input_data_types"], t
    for f in ("wallet_address", "private_key", "seed_phrase", "account_balance",
              "positions", "orders", "fills", "deposits_withdrawals",
              "login_session_cookie_api_key"):
        assert f in s["forbidden_inputs"], f


def test_output_rules_complete():
    joined = " ".join(ps.OUTPUT_RULES)
    assert "pass_watch_fail_research_alerts_only" in joined
    assert "no_trading_instruction_ever" in joined
    assert "no_guaranteed_or_winning_claim_ever" in joined
    assert "no_wallet_or_account_action_ever" in joined
    assert "resolution_risk_caveat" in joined
    assert "research_only_disclaimer" in joined
    assert "one_approved_run_writes_one_report" in joined
    assert "refused_or_blocked_runs_write_nothing" in joined
    assert "per_run_human_approval_no_scheduler" in joined


def test_gating_blocks_on_missing_invalid_or_tampered_readiness():
    assert ps.record_prediction_market_scanner_spec(None)["verdict"] == (
        ps.VERDICT_PM_SPEC_BLOCKED)
    bad = pr.build_prediction_market_factory_v1_readiness()
    bad["execution_capability_exists"] = True
    s = ps.record_prediction_market_scanner_spec(bad)
    assert s["verdict"] == ps.VERDICT_PM_SPEC_BLOCKED
    assert "readiness_invalid" in s["blockers"]


def test_inert_and_gates_locked_on_all_paths():
    for s in (ps.build_prediction_market_scanner_spec(),
              ps.record_prediction_market_scanner_spec(None)):
        for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                    "fetches_data", "calls_api", "uses_network",
                    "uses_credentials", "uses_wallet", "connects_broker",
                    "connects_exchange", "uses_real_money",
                    "contains_order_logic", "starts_scheduler",
                    "sends_notifications", "promotes_gate",
                    "unlocks_downstream_gate"):
            assert s[key] is False, key
        assert s["paper_trading_gate_locked"] is True
        assert s["micro_live_gate_locked"] is True
        assert s["live_gate_locked"] is True
        assert s["modifies_arbitrage_factory_v1_lane"] is False
        assert s["modifies_crypto_d1_lane"] is False


def test_validate_passes_and_catches_tampering():
    ok = ps.build_prediction_market_scanner_spec()
    assert ps.validate_prediction_market_scanner_spec(ok)["valid"] is True
    assert ps.validate_prediction_market_scanner_spec(
        ps.record_prediction_market_scanner_spec(None))["valid"] is True
    s1 = ps.build_prediction_market_scanner_spec()
    s1["scanner_built_by_this_contract"] = True
    v1 = ps.validate_prediction_market_scanner_spec(s1)
    assert v1["valid"] is False and "scanner_claimed_built" in v1["errors"]
    s2 = ps.build_prediction_market_scanner_spec()
    s2["forbidden_inputs"].remove("private_key")
    assert ps.validate_prediction_market_scanner_spec(s2)["valid"] is False
    s3 = ps.build_prediction_market_scanner_spec()
    s3["output_rules"] = s3["output_rules"][:3]
    assert ps.validate_prediction_market_scanner_spec(s3)["valid"] is False
    s4 = ps.build_prediction_market_scanner_spec()
    s4["reports_root"] = "C:/anywhere/"
    assert ps.validate_prediction_market_scanner_spec(s4)["valid"] is False
    s5 = ps.build_prediction_market_scanner_spec()
    s5["live_gate_locked"] = False
    assert ps.validate_prediction_market_scanner_spec(s5)["valid"] is False


def test_build_is_deterministic():
    assert (ps.build_prediction_market_scanner_spec()
            == ps.build_prediction_market_scanner_spec())


def test_label_action_and_imports_clean():
    assert ps.get_prediction_market_scanner_spec_label() == ps.PM_SPEC_LABEL
    assert "READ-ONLY" in ps.PM_SPEC_LABEL and ps.PM_SPEC_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in ps.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(ps.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
