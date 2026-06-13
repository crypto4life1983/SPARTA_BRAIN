"""Tests for the Candidate #6 dry-run review / evidence-freeze contract.

Proves: the review FREEZES by recomputing the pushed dry run live and
matching every frozen fact; each frozen fact holds; tampering with any
frozen block invalidates; chain gates block on break; synthetic-only
boundary permanent; zero trading-adjacent capability; AST purity.
Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.multi_symbol_relative_strength_rotation_filter_detector_spec_contract as c6d
import sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract as c6r


def test_review_frozen_with_zero_mismatches():
    record = c6r.build_c6_dry_run_review()
    assert record["verdict"] == c6r.VERDICT_C6R_FROZEN
    assert record["blockers"] == []
    assert record["mismatches"] == []
    assert c6r.validate_c6_dry_run_review(record)["valid"] is True
    assert record["candidate_id"] == (
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1")
    # 10. deterministic across repeated builds
    assert c6r.build_c6_dry_run_review() == record


def test_frozen_fixture_counts_facts_1_6_7_8_9():
    assert c6r.EXPECTED_FIXTURE_COUNTS == {
        "sol_rank1_breakout": {"attempts": 1, "accepted": 1},
        "rank_tie_fails": {"attempts": 1, "accepted": 0},
        "rank1_but_negative_rs": {"attempts": 3, "accepted": 0},
        "no_fresh_closing_high": {"attempts": 0, "accepted": 0},
        "event_on_last_bar": {"attempts": 1, "accepted": 0}}
    facts = c6r.EXPECTED_REJECTION_FACTS
    assert facts["tie_status"] == "rejected_not_strict_rank_1"
    assert facts["negative_rs_status"] == "rejected_rs_not_positive"
    assert facts["negative_rs_all_strict_rank_1"] is True
    assert facts["negative_rs_all_rs_not_positive"] is True
    assert facts["last_bar_status"] == "rejected_no_evaluation_bar"
    assert facts["last_bar_reason"] == "no_next_bar_for_evaluation"


def test_frozen_accepted_setup_facts_2_3_4_5():
    exp = c6r.EXPECTED_ACCEPTED_SETUP
    assert exp["entry_price"] == 106.5                      # fact 2
    assert exp["stop_distance"] == 1.5                      # fact 3
    assert exp["structure_stop_distance"] == 1.5            # fact 4
    assert exp["structure_stop_distance"] > 1.5 * exp["atr14"]
    assert exp["stop_source"] == "structure_wider_than_1_5x_atr"
    assert exp["geometry_floor_pass_by_variant"] == {       # fact 5
        "2r": True, "3r": True, "4r": True}
    assert exp["target_distance_bps_2r"] >= 81
    assert exp["replay_start_time"] > exp["event_time"]


def test_chain_gates_live_fact_11():
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract as c6p
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract as c6s
    import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c6p.build_candidate_6_family_proposal()["verdict"] == (
        "CANDIDATE_6_FAMILY_PROPOSAL_READY")
    assert c6s.build_candidate_6_spec_review()["verdict"] == (
        "CANDIDATE_6_SPEC_REVIEW_READY")
    assert c6d.build_c6_detector_spec_contract()["verdict"] == (
        "CANDIDATE_6_DETECTOR_SPEC_READY")
    assert cr.build_candidate_recommendation()["verdict"] == (
        "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_READY")
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
        REJECTION_STATUS as C5)
    assert C1 == C2 == C3 == C4 == C5 == "REJECTED_KEPT_ON_RECORD"
    # the review record itself reaches FROZEN only because the chain
    # held; a chain break flips the build to BLOCKED by construction
    record = c6r.build_c6_dry_run_review()
    assert record["verdict"] != c6r.VERDICT_C6R_BLOCKED


def test_tampering_each_frozen_block_invalidates():
    for field, value in (
            ("expected_detector_verdict", "SOMETHING"),
            ("expected_dry_run_verdict", "SOMETHING"),
            ("expected_fixture_counts", {}),                # counts
            ("expected_accepted_setup", {"entry_price": 1.0}),  # entry
            ("expected_rejection_facts", {}),               # tie/neg/last
            ("frozen_scope_facts", []),
            ("claim_locks", []),
            ("real_detection_authorized_by_this_gate", True),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("runs_real_detection_now", True),
            ("creates_data_artifacts_now", True),
            ("live_gate_locked", False),
            ("candidate_id", "CANDIDATE_5_REVIVED"),
            ("verdict", "CANDIDATE_6_APPROVED_FOR_TRADING")):
        tampered = c6r.build_c6_dry_run_review()
        tampered[field] = value
        assert c6r.validate_c6_dry_run_review(
            tampered)["valid"] is False, field
    # specific fact tampers: entry, stop distance, floor map
    for key, value in (("entry_price", 100.0),
                       ("stop_distance", 0.5),
                       ("geometry_floor_pass_by_variant",
                        {"2r": False, "3r": True, "4r": True})):
        tampered = c6r.build_c6_dry_run_review()
        tampered["expected_accepted_setup"] = dict(
            c6r.EXPECTED_ACCEPTED_SETUP, **{key: value})
        assert c6r.validate_c6_dry_run_review(
            tampered)["valid"] is False, key
    # rejection-logic tampers: tie reason, negative-RS, last-bar
    for key, value in (("tie_status", "rejected_something_else"),
                       ("negative_rs_status", "accepted"),
                       ("last_bar_status", "accepted")):
        tampered = c6r.build_c6_dry_run_review()
        tampered["expected_rejection_facts"] = dict(
            c6r.EXPECTED_REJECTION_FACTS, **{key: value})
        assert c6r.validate_c6_dry_run_review(
            tampered)["valid"] is False, key
    frozen_with_mismatch = c6r.build_c6_dry_run_review()
    frozen_with_mismatch["mismatches"] = ["fake"]
    assert c6r.validate_c6_dry_run_review(
        frozen_with_mismatch)["valid"] is False


def test_synthetic_only_boundary_permanent():
    dry = c6d.run_c6_detector_dry_run()
    assert dry["uses_synthetic_fixtures_only"] is True
    assert dry["reads_real_candles"] is False
    assert dry["reads_staged_data"] is False
    assert dry["reads_any_files"] is False
    record = c6r.build_c6_dry_run_review()
    facts = record["frozen_scope_facts"]
    assert "synthetic in-memory fixtures only" in facts
    assert any("no real candle has been touched" in fact
               for fact in facts)
    assert any("no staged data read" in fact for fact in facts)
    assert any("no labels, no replay, no artifacts" in fact
               for fact in facts)
    assert record["real_detection_authorized_by_this_gate"] is False


def test_no_trading_adjacent_capability():
    record = c6r.build_c6_dry_run_review()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording"):
        assert lock in locks, lock


def test_next_gate_and_module_purity():
    record = c6r.build_c6_dry_run_review()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_6_REAL_CANDLE_DETECTION")
    assert c6r.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_6_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6r.NEXT_REQUIRED_ACTION.upper(), banned
    assert c6r.get_c6_dry_run_review_label() == c6r.C6R_LABEL
    assert "READ-ONLY" in c6r.C6R_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c6r.C6R_LABEL
    assert c6r.C6R_MODE == "RESEARCH_ONLY"
    assert c6r.VERDICT_C6R_FROZEN == "CANDIDATE_6_DRY_RUN_REVIEW_FROZEN"
    src = open(c6r.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
