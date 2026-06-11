"""Tests for the SPARTA NY FVG+CHOCH Dry-Run Replay Results Review contract."""

from __future__ import annotations

import ast

import sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract as rv


def test_live_runner_behavior_accepted_for_real_candle_staging():
    review = rv.build_dry_run_replay_results_review()
    assert review["verdict"] == rv.VERDICT_ACCEPTED
    assert review["blockers"] == []
    assert all(review["checklist_results"][n] is True
               for n in rv.REVIEW_CHECKLIST)
    assert len(rv.REVIEW_CHECKLIST) == 11
    assert review["next_required_action"] == (
        "HUMAN_APPROVED_REAL_CANDLE_STAGING_PLAN")
    assert rv.validate_dry_run_replay_results_review(review)["valid"] is True


def test_acceptance_stages_and_promotes_nothing():
    review = rv.build_dry_run_replay_results_review()
    assert review["acceptance_stages_nothing"] is True
    assert review["acceptance_is_not_a_promotion"] is True
    assert review["real_candle_staging_requires_its_own_human_approval"] is True
    assert review["modifies_mission_flow"] is False


def test_missing_runner_observation_blocks():
    review = rv.certify_dry_run_results(None)
    assert review["verdict"] == rv.VERDICT_BLOCKED
    assert "observation_missing_runner_unavailable" in review["blockers"]


def test_missing_cost_accounting_rejects():
    obs = rv.observe_runner_behavior()
    obs["win_net_r"] = obs["win_gross_r"]  # costs no longer reduce wins
    review = rv.certify_dry_run_results(obs)
    assert review["verdict"] == rv.VERDICT_REJECTED
    assert ("check_failed:costs_worsen_losses_and_reduce_wins"
            in review["blockers"])
    obs2 = rv.observe_runner_behavior()
    obs2["net_fields_numeric"] = False
    review2 = rv.certify_dry_run_results(obs2)
    assert "check_failed:net_after_costs_mandatory" in review2["blockers"]


def test_missing_outcome_coverage_rejects():
    obs = rv.observe_runner_behavior()
    del obs["outcomes"]["breakeven"]
    review = rv.certify_dry_run_results(obs)
    assert review["verdict"] == rv.VERDICT_REJECTED
    assert "check_failed:all_five_outcomes_supported" in review["blockers"]


def test_forbidden_capability_or_label_leak_rejects():
    obs = rv.observe_runner_behavior()
    obs["forbidden_status"] = "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW"
    review = rv.certify_dry_run_results(obs)
    assert review["verdict"] == rv.VERDICT_REJECTED
    assert ("check_failed:fixture_only_no_fetch_no_network_no_credentials"
            "_no_execution" in review["blockers"])
    obs2 = rv.observe_runner_behavior()
    obs2["rejected_label_status"] = "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW"
    review2 = rv.certify_dry_run_results(obs2)
    assert "check_failed:rejected_label_cannot_replay" in review2["blockers"]


def test_conservatism_checks_enforced():
    obs = rv.observe_runner_behavior()
    obs["same_candle_exit"] = "target_4r_hit"
    review = rv.certify_dry_run_results(obs)
    assert ("check_failed:same_candle_entry_stop_conservative"
            in review["blockers"])
    obs2 = rv.observe_runner_behavior()
    obs2["ambiguous_exit"] = "target_4r_hit"
    review2 = rv.certify_dry_run_results(obs2)
    assert "check_failed:stop_checked_before_target" in review2["blockers"]


def test_no_promotion_or_gate_unlock_possible():
    review = rv.build_dry_run_replay_results_review()
    for key in ("executes", "fetches_data", "uses_network", "calls_api",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "contains_order_logic",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate"):
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    tampered = rv.build_dry_run_replay_results_review()
    tampered["promotes_gate"] = True
    assert rv.validate_dry_run_replay_results_review(tampered)["valid"] is False
    tampered2 = rv.build_dry_run_replay_results_review()
    tampered2["live_gate_locked"] = False
    assert rv.validate_dry_run_replay_results_review(tampered2)["valid"] is False


def test_upstream_stack_and_pm_lane_untouched():
    from sparta_commander.ny_session_fvg_choch_replay_spec import (
        build_ny_fvg_choch_replay_spec)
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_ny_fvg_choch_replay_spec()["verdict"] == (
        "NY_FVG_CHOCH_REPLAY_SPEC_READY")
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_review_is_deterministic_and_validator_strict():
    assert (rv.build_dry_run_replay_results_review()
            == rv.build_dry_run_replay_results_review())
    review = rv.build_dry_run_replay_results_review()
    review["checklist_results"]["net_after_costs_mandatory"] = False
    assert rv.validate_dry_run_replay_results_review(review)["valid"] is False
    review2 = rv.build_dry_run_replay_results_review()
    review2["checklist"] = review2["checklist"][:3]
    assert rv.validate_dry_run_replay_results_review(review2)["valid"] is False


def test_label_action_and_imports_clean():
    assert rv.get_dry_run_replay_results_review_label() == rv.RV_LABEL
    assert "READ-ONLY" in rv.RV_LABEL and rv.RV_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rv.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(rv.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
