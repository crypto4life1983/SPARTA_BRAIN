"""Tests for the SPARTA Crypto-D1 Auto Research Strategy Optimizer contract."""

from __future__ import annotations

import ast

import sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract as op


def _metrics(**overrides):
    metrics = {
        "net_edge_after_costs_bps": 35.0, "independent_trade_count": 120,
        "max_drawdown": -0.20, "single_symbol_profit_share": 0.45,
        "single_day_profit_share": 0.10,
        "correlation_to_existing_evidence": 0.30,
        "cluster_profit_share": 0.30, "oos_validated": True,
        "oos_degradation_pct": 20.0,
    }
    metrics.update(overrides)
    return metrics


def test_contract_ready_and_research_only():
    c = op.build_optimizer_contract()
    assert c["verdict"] == op.VERDICT_OPT_CONTRACT_READY
    assert c["mode"] == "RESEARCH_ONLY"
    assert c["optimizer_execution_not_built_yet"] is True
    assert c["next_required_action"] == (
        "HUMAN_APPROVED_MUTABLE_CANDIDATE_ASSET_SPEC")
    assert op.validate_optimizer_contract(c)["valid"] is True


def test_three_file_architecture_present():
    c = op.build_optimizer_contract()
    assert c["instructions_locked"] is True
    assert c["scorer_locked"] is True
    assert c["only_candidate_asset_is_mutable"] is True
    assert c["mutable_candidate_asset_spec"]["editable_by_optimizer"] is True
    assert c["mutable_candidate_asset_spec"][
        "edits_are_research_proposals_awaiting_human_review"] is True
    assert c["mutable_candidate_asset_spec"][
        "edits_never_touch_live_trading_config"] is True


def test_locked_instructions_are_immutable():
    c = op.build_optimizer_contract()
    c["locked_human_instructions"][0] = "optimizer_may_do_what_it_wants"
    v = op.validate_optimizer_contract(c)
    assert v["valid"] is False
    assert "locked_instructions_modified" in v["errors"]
    joined = " ".join(op.LOCKED_HUMAN_INSTRUCTIONS)
    assert "do_not_promote_resume_policy_yet_remains_preserved" in joined
    assert "frozen_block_190_fresh_evidence_bars_remain_untouched" in joined


def test_locked_scorer_is_immutable():
    c = op.build_optimizer_contract()
    c["locked_scoring_rules"] = c["locked_scoring_rules"][:3]
    v = op.validate_optimizer_contract(c)
    assert v["valid"] is False and "locked_scorer_modified" in v["errors"]
    c2 = op.build_optimizer_contract()
    c2["min_independent_trades"] = 1
    assert "trade_count_threshold_tampered" in op.validate_optimizer_contract(
        c2)["errors"]
    c3 = op.build_optimizer_contract()
    c3["max_oos_degradation_pct"] = 99.0
    assert "overfit_bound_tampered" in op.validate_optimizer_contract(c3)["errors"]


def test_live_trading_and_credentials_impossible():
    c = op.build_optimizer_contract()
    joined = " ".join(c["forbidden_forever"])
    assert "placing_orders" in joined
    assert "broker_or_exchange_credential_access" in joined
    assert "broker_or_exchange_api_calls" in joined
    assert "modifying_live_trading_config" in joined
    assert "auto_promoting_a_candidate_to_paper_or_live" in joined
    assert "auto_pushing_commits" in joined
    assert "hiding_rejected_experiments" in joined
    assert "network_calls_of_any_kind" in joined
    assert "bypassing_human_approval" in joined
    assert "unlocking_paper_micro_live_or_live_gates" in joined
    for key in ("executes", "contains_order_logic", "connects_broker",
                "connects_exchange", "uses_credentials", "uses_wallet",
                "uses_network", "calls_api", "uses_real_money",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate"):
        assert c[key] is False, key
    c2 = op.build_optimizer_contract()
    c2["forbidden_forever"] = c2["forbidden_forever"][:3]
    assert "forbidden_forever_weakened" in op.validate_optimizer_contract(
        c2)["errors"]


def test_good_candidate_accepted_but_promotes_nothing():
    r = op.evaluate_candidate_score(_metrics())
    assert r["verdict"] == op.VERDICT_SCORE_ACCEPTED
    assert r["rejection_reasons"] == []
    assert r["acceptance_promotes_nothing"] is True
    assert r["human_approval_required_before_promotion_review"] is True


def test_negative_net_edge_cannot_pass():
    r = op.evaluate_candidate_score(_metrics(net_edge_after_costs_bps=-5.0))
    assert r["verdict"] == op.VERDICT_SCORE_REJECTED
    assert "net_edge_after_costs_not_positive" in r["rejection_reasons"]
    r2 = op.evaluate_candidate_score(_metrics(net_edge_after_costs_bps=0.0))
    assert r2["verdict"] == op.VERDICT_SCORE_REJECTED


def test_low_trade_count_cannot_pass():
    r = op.evaluate_candidate_score(_metrics(independent_trade_count=10))
    assert r["verdict"] == op.VERDICT_SCORE_REJECTED
    assert "independent_trade_count_below_minimum" in r["rejection_reasons"]


def test_drawdown_and_concentration_gates():
    r = op.evaluate_candidate_score(_metrics(max_drawdown=-0.50))
    assert "max_drawdown_beyond_bound" in r["rejection_reasons"]
    r2 = op.evaluate_candidate_score(_metrics(single_symbol_profit_share=0.90))
    assert "symbol_concentration_too_high" in r2["rejection_reasons"]
    r3 = op.evaluate_candidate_score(_metrics(single_day_profit_share=0.40))
    assert "single_day_concentration_too_high" in r3["rejection_reasons"]


def test_correlated_and_cluster_only_candidates_penalized():
    r = op.evaluate_candidate_score(
        _metrics(correlation_to_existing_evidence=0.90))
    assert "correlation_penalty_applied" in r["penalties"]
    r2 = op.evaluate_candidate_score(_metrics(cluster_profit_share=0.80))
    assert r2["verdict"] == op.VERDICT_SCORE_REJECTED
    assert "cluster_only_profit_penalty_applied" in r2["penalties"]
    assert "profit_concentrated_in_one_cluster" in r2["rejection_reasons"]


def test_overfit_and_missing_oos_rejected():
    r = op.evaluate_candidate_score(_metrics(oos_degradation_pct=80.0))
    assert r["verdict"] == op.VERDICT_SCORE_REJECTED
    assert "overfit_rejected_oos_degradation_too_large" in r["rejection_reasons"]
    r2 = op.evaluate_candidate_score(_metrics(oos_validated=False))
    assert "out_of_sample_validation_missing" in r2["rejection_reasons"]
    r3 = op.evaluate_candidate_score(None)
    assert r3["verdict"] == op.VERDICT_SCORE_REJECTED
    incomplete = _metrics(); del incomplete["max_drawdown"]
    r4 = op.evaluate_candidate_score(incomplete)
    assert "missing_metric:max_drawdown" in r4["rejection_reasons"]


def test_gates_locked_and_lanes_untouched():
    c = op.build_optimizer_contract()
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True
    assert c["live_gate_locked"] is True
    assert c["modifies_mission_flow"] is False
    assert c["modifies_pm_lane"] is False
    assert c["modifies_crypto_d1_sealed_chain"] is False
    c2 = op.build_optimizer_contract()
    c2["live_gate_locked"] = False
    assert op.validate_optimizer_contract(c2)["valid"] is False
    # PM lane recognition still intact and untouched by this module
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Prediction Market Factory V1" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert op.get_crypto_d1_auto_research_optimizer_label() == op.OPT_LABEL
    assert "READ-ONLY" in op.OPT_LABEL and op.OPT_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in op.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(op.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
