"""Tests for the SPARTA NY-Session FVG+CHOCH Strategy Spec contract."""

from __future__ import annotations

import ast

import sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec as ca
import sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract as op
import sparta_commander.ny_session_fvg_choch_strategy_spec_contract as fs


def _conditions(**overrides):
    conditions = {"htf_fvg_present": True,
                  "liquidity_or_sr_context_present": True,
                  "choch_1m_present": True, "fvg_1m_present": True,
                  "fib_alignment_present": True,
                  "htf_fvg_closed_through": False, "ambiguous": False}
    conditions.update(overrides)
    return conditions


def test_spec_ready_with_identity():
    s = fs.build_ny_fvg_choch_strategy_spec()
    assert s["verdict"] == fs.VERDICT_FS_READY
    assert s["blockers"] == []
    assert s["candidate_id"] == "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert s["candidate_family"] == "intraday_fvg_choch"
    assert s["research_only"] is True
    assert s["live_trading_authorized"] is False
    assert s["paper_trading_authorized"] is False
    assert s["human_review_required"] is True
    assert s["next_required_action"] == "HUMAN_APPROVED_FVG_CHOCH_DETECTOR_SPEC"
    assert fs.validate_ny_fvg_choch_strategy_spec(s)["valid"] is True


def test_session_windows_are_research_parameters_only():
    s = fs.build_ny_fvg_choch_strategy_spec()
    assert s["default_session_window"] == "09:30-12:00 America/New_York"
    assert tuple(s["allowed_test_windows"]) == (
        "09:30-10:30", "09:30-11:30", "09:30-12:00", "09:30-13:00")
    assert s["session_windows_are_research_parameters_only"] is True


def test_rules_are_deterministic_and_explicit():
    r = fs.DETERMINISTIC_RULES
    assert "candle1.high < candle3.low" in r["htf_15m_bullish_fvg"]
    assert "candle1.low > candle3.high" in r["htf_15m_bearish_fvg"]
    assert "(gap_upper + gap_lower) / 2" in r["fvg_midpoint"]
    assert "CLOSES fully through" in r["htf_invalidation"]
    assert "20 bars" in r["liquidity_inflection_approx"]
    assert "3-bar fractal" in r["trigger_1m_bullish_choch"]
    assert "61.8%" in r["fib_alignment"] and "+/- 5%" in r["fib_alignment"]
    assert "1:4 risk/reward" in r["target_rule"]
    assert "never live sizing" in r["stop_rule"]
    assert "never an execution instruction" in r["breakeven_rule"]
    assert fs.FIB_LEVEL == 0.618 and fs.FIB_TOLERANCE == 0.05
    assert fs.RISK_REWARD_TARGET == 4.0
    # deterministic: same inputs, same outputs
    assert fs.evaluate_setup_completeness(_conditions()) == (
        fs.evaluate_setup_completeness(_conditions()))


def test_complete_setup_accepted_but_authorizes_nothing():
    r = fs.evaluate_setup_completeness(_conditions())
    assert r["verdict"] == fs.VERDICT_SETUP_COMPLETE
    assert r["rejection_reasons"] == []
    assert r["completeness_authorizes_nothing"] is True


def test_missing_components_reject():
    cases = {"htf_fvg_present": "missing_15m_fvg_context",
             "liquidity_or_sr_context_present":
                 "missing_liquidity_or_sr_approximation",
             "choch_1m_present": "missing_1m_choch",
             "fvg_1m_present": "missing_1m_fvg",
             "fib_alignment_present": "missing_fib_alignment"}
    for cond, reason in cases.items():
        r = fs.evaluate_setup_completeness(_conditions(**{cond: False}))
        assert r["verdict"] == fs.VERDICT_SETUP_REJECTED, cond
        assert reason in r["rejection_reasons"]


def test_invalidation_ambiguity_and_authorization_claims_reject():
    r = fs.evaluate_setup_completeness(_conditions(htf_fvg_closed_through=True))
    assert "htf_fvg_closed_through_invalidation" in r["rejection_reasons"]
    r2 = fs.evaluate_setup_completeness(_conditions(ambiguous=True))
    assert "ambiguous_or_low_quality_setup" in r2["rejection_reasons"]
    r3 = fs.evaluate_setup_completeness(
        _conditions(live_authorization_claimed=True))
    assert "any_live_or_paper_authorization_claim" in r3["rejection_reasons"]
    r4 = fs.evaluate_setup_completeness(
        _conditions(paper_authorization_claimed=True))
    assert "any_live_or_paper_authorization_claim" in r4["rejection_reasons"]
    assert fs.evaluate_setup_completeness(None)["verdict"] == (
        fs.VERDICT_SETUP_REJECTED)


def test_instance_conforms_to_mutable_candidate_asset_spec():
    instance = fs.build_candidate_asset_instance()
    check = ca.validate_candidate_asset(instance)
    assert check["verdict"] == "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH", check
    assert instance["fields"]["candidate_id"] == fs.CANDIDATE_ID
    assert instance["fields"]["status"] == "draft"
    assert instance["locked_instructions_may_edit"] is False
    assert instance["locked_scorer_may_edit"] is False


def test_forbidden_list_and_capabilities():
    s = fs.build_ny_fvg_choch_strategy_spec()
    joined = " ".join(s["forbidden"])
    for must in ("order_placement", "broker_or_exchange_api_calls",
                 "credential_access", "wallet_account_login_fields",
                 "live_config_modification", "paper_micro_live_promotion",
                 "changing_locked_scorer", "changing_locked_instructions",
                 "hidden_rejected_experiments", "network_calls",
                 "data_fetching", "backtest_or_replay_execution_here"):
        assert must in joined, must
    for key in ("executes", "contains_order_logic", "connects_broker",
                "connects_exchange", "uses_credentials", "uses_wallet",
                "uses_network", "calls_api", "fetches_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate"):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True


def test_foundation_and_pm_lane_untouched():
    assert op.build_optimizer_contract()["verdict"] == (
        op.VERDICT_OPT_CONTRACT_READY)
    assert ca.build_mutable_candidate_asset_spec()["verdict"] == (
        ca.VERDICT_CA_SPEC_READY)
    s = fs.build_ny_fvg_choch_strategy_spec()
    assert s["modifies_locked_scorer"] is False
    assert s["modifies_locked_instructions"] is False
    assert s["modifies_mission_flow"] is False
    assert s["modifies_pm_lane"] is False
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_validate_catches_tampering():
    s1 = fs.build_ny_fvg_choch_strategy_spec()
    s1["risk_reward_target"] = 1.0
    assert fs.validate_ny_fvg_choch_strategy_spec(s1)["valid"] is False
    s2 = fs.build_ny_fvg_choch_strategy_spec()
    s2["forbidden"] = s2["forbidden"][:3]
    assert fs.validate_ny_fvg_choch_strategy_spec(s2)["valid"] is False
    s3 = fs.build_ny_fvg_choch_strategy_spec()
    s3["live_trading_authorized"] = True
    assert fs.validate_ny_fvg_choch_strategy_spec(s3)["valid"] is False
    s4 = fs.build_ny_fvg_choch_strategy_spec()
    s4["live_gate_locked"] = False
    assert fs.validate_ny_fvg_choch_strategy_spec(s4)["valid"] is False


def test_label_action_and_imports_clean():
    assert fs.get_ny_fvg_choch_strategy_spec_label() == fs.FS_LABEL
    assert "READ-ONLY" in fs.FS_LABEL and fs.FS_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fs.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(fs.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
