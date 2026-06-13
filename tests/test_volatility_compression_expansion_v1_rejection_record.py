"""Tests for the formal Candidate #7 rejection record
(seventh ledger entry, VOLATILITY_COMPRESSION_EXPANSION_V1).

Covers: REJECTED_KEPT_ON_RECORD status; EDIT_SPENT_AND_STILL_ZERO
_ACCEPTED_REAL_CANDLE_SETUPS_AFTER_RELAXED_CONTRACTION reason;
frozen original detection (122/0/0/0); frozen edited detection
(122/0/0/0 again); frozen single-edit (CONTRACTION_FRACTION 0.6 ->
0.7, token spent, anti-cluster proposal-locked); auto-rejection
triggers (near-zero accepted fired; no inviolable changes; no
second edit); permanence flags; prior six-record ledger unchanged;
ledger now seven records; future-family blacklist addition;
tamper-failure on any frozen-fact change; no profit/paper/live
wording; no trading-adjacent capability; AST/purity green.
Commander safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.volatility_compression_expansion_v1_edited_real_candle_labels_review_contract as c7el
import sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract as c7l
import sparta_commander.volatility_compression_expansion_v1_rejection_record as rj7
import sparta_commander.volatility_compression_expansion_v1_single_edit_relaxed_contraction_decision_contract as c7e

REPO_ROOT = "C:/SPARTA_BRAIN"


def _record():
    return rj7.build_c7_rejection_record(REPO_ROOT, tracked_paths=[])


# (1) status = REJECTED_KEPT_ON_RECORD --------------------------------------

def test_1_rejection_status_is_rejected_kept_on_record():
    assert rj7.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["verdict"] == rj7.VERDICT_RJ7_RECORDED
    assert record["blockers"] == []
    assert rj7.validate_c7_rejection_record(record)["valid"] is True


# (2) reason = EDIT_SPENT_AND_STILL_ZERO_ACCEPTED... -----------------------

def test_2_rejection_reason_is_edit_spent_and_still_zero_accepted():
    assert rj7.REJECTION_REASON == (
        "EDIT_SPENT_AND_STILL_ZERO_ACCEPTED_REAL_CANDLE_SETUPS_AFTER"
        "_RELAXED_CONTRACTION")
    record = _record()
    assert record["rejection_reason"] == rj7.REJECTION_REASON
    assert rj7.VERDICT_RJ7_RECORDED == (
        "C7_REJECTED_KEPT_ON_RECORD_EDIT_SPENT_AND_STILL_ZERO"
        "_ACCEPTED_REAL_CANDLE_SETUPS")


# (3) frozen original detection evidence -----------------------------------

def test_3_original_detection_122_attempts_zero_accepted():
    record = _record()
    orig = record["expected_original_detection"]
    assert orig["total_attempts"] == 122
    assert orig["accepted_pre_anti_cluster"] == 0
    assert orig["accepted_post_anti_cluster"] == 0
    assert orig["rejected_by_scanner"] == 122
    assert orig["dropped_by_anti_cluster"] == 0
    assert orig["status_breakdown"] == {
        "rejected_contraction_window": 122}
    assert orig["floor_pass_counts"] == {"2r": 0, "3r": 0, "4r": 0}
    assert orig["bars_4h_scanned"] == 240
    assert orig["all_rejected_on_contraction_window"] is True
    assert orig["zero_accepted_setups"] is True
    assert orig["no_replay_run"] is True
    assert orig["no_pnl_computed"] is True
    assert orig["no_trading_authorized"] is True


# (4) frozen single-edit evidence ------------------------------------------

def test_4_single_edit_contraction_fraction_0_6_to_0_7_spent():
    record = _record()
    ed = record["expected_edit"]
    assert ed["edit_parameter_name"] == "CONTRACTION_FRACTION"
    assert ed["edit_parameter_old_value"] == 0.6
    assert ed["edit_parameter_new_value"] == 0.7
    assert ed["edit_token_used"] == 1
    assert ed["edits_remaining_after_this"] == 0
    assert ed["this_was_the_only_allowed_c7_edit"] is True
    assert ed["no_further_c7_edits_allowed"] is True
    assert ed["no_other_numeric_changed"] is True
    assert ed[
        "anti_cluster_gap_remained_proposal_level_locked_not_edit_token"
    ] is True
    assert ed["is_single_controlled_relaxation"] is True
    assert ed["is_a_rescue_bundle"] is False
    # pinned via the pushed single-edit decision module
    assert c7e.EDIT_TOKEN_USED == 1
    assert c7e.EDITS_REMAINING_AFTER_THIS == 0


# (5) frozen edited detection evidence ------------------------------------

def test_5_edited_detection_122_attempts_zero_accepted_again():
    record = _record()
    ed = record["expected_edited_detection"]
    assert ed["total_attempts"] == 122
    assert ed["accepted_pre_anti_cluster"] == 0
    assert ed["accepted_post_anti_cluster"] == 0
    assert ed["rejected_by_scanner"] == 122
    assert ed["dropped_by_anti_cluster"] == 0
    assert ed["status_breakdown"] == {
        "rejected_contraction_window": 122}
    assert ed["floor_pass_counts"] == {"2r": 0, "3r": 0, "4r": 0}
    assert ed["bars_4h_scanned"] == 240
    assert ed[
        "rejection_reason_referenced_strict_below_0_7_x_rolling_avg"
    ] is True
    assert ed["all_rejected_on_contraction_window"] is True
    assert ed["zero_accepted_setups"] is True
    assert ed["original_artifacts_unchanged"] is True
    assert ed["no_replay_run"] is True
    assert ed["no_pnl_computed"] is True
    assert ed["no_trading_authorized"] is True
    assert ed["post_edit_auto_rejection_trigger_fired"] == (
        "near_zero_accepted_count_after_edited_detection")
    # pinned to the pushed C7 edited labels review module
    assert ed["edited_labels_sha256"] == (
        c7el.EXPECTED_EDITED_LABELS_SHA256)
    assert ed["edited_summary_sha256"] == (
        c7el.EXPECTED_EDITED_SUMMARY_SHA256)
    assert ed["post_edit_auto_rejection_trigger_fired"] == (
        c7el.EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED)


# (6) auto-rejection triggers satisfied ------------------------------------

def test_6_auto_rejection_triggers_all_satisfied():
    record = _record()
    triggers = record["auto_rejection_triggers_satisfied"]
    assert triggers[
        "near_zero_accepted_count_after_edited_detection"] is True
    assert triggers[
        "filter_or_edit_spent_and_still_negative_or_zero_accepted"
    ] is True
    # NOT fired (clean lane)
    assert triggers[
        "any_attempt_to_change_more_than_contraction_fraction"] is (
        False)
    assert triggers[
        "any_attempt_to_spend_a_second_edit_on_this_family"] is False
    assert triggers[
        "any_attempt_to_change_an_inviolable_upstream_rule"] is False
    assert triggers[
        "any_artifact_hash_or_gate_mismatch_in_edited_pipeline"] is (
        False)
    # mirror the pushed-loop AUTO_REJECTION_RULES
    for needed in ("filter_or_edit_spent_and_still_negative",):
        # at least one of the pushed loop rules must be referenced
        assert needed in " ".join(ap.AUTO_REJECTION_RULES), needed


# (7) frozen staged source SHAs match the pushed labels review ------------

def test_7_staged_source_shas_match_labels_review():
    record = _record()
    assert record["expected_staged_source_shas"] == (
        c7l.EXPECTED_STAGED_SHAS)
    # both BTCUSD files pinned with 64-char hex shas
    for sha in record["expected_staged_source_shas"].values():
        assert len(sha) == 64
        int(sha, 16)


# (8) prior six-record ledger unchanged + C7 added at position 7 ---------

def test_8_prior_six_records_unchanged_c7_added_at_position_7():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C5)
    from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C6)
    for status in (C1, C2, C3, C4, C5, C6):
        assert status == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["prior_six_records_unchanged"] is True
    assert record["ledger_position"] == 7
    assert record["ledger_now_contains_seven_records"] is True
    # enumerate all seven rejection record modules
    ledger_modules = (
        "sparta_commander.ny_session_fvg_choch_v3_result_and_candidate"
        "_rejection_record_contract",
        "sparta_commander.crypto_intraday_breakout_pullback_structure_v2"
        "_result_and_rejection_record_contract",
        "sparta_commander.btc_sol_long_trend_continuation_v1_result_and"
        "_rejection_record_contract",
        "sparta_commander.sol_btc_long_1h_swing_structure_rejection"
        "_record_contract",
        "sparta_commander.eth_sol_relative_strength_rejection_record"
        "_contract",
        "sparta_commander.multi_symbol_relative_strength_rotation_filter"
        "_rejection_record_contract",
        "sparta_commander.volatility_compression_expansion_v1_rejection"
        "_record",
    )
    statuses = []
    for module_path in ledger_modules:
        mod = __import__(module_path, fromlist=["REJECTION_STATUS"])
        statuses.append(mod.REJECTION_STATUS)
    assert len(statuses) == 7
    assert all(s == "REJECTED_KEPT_ON_RECORD" for s in statuses)


# (9) future family blacklist addition for the recommendation logic ------

def test_9_future_family_blacklist_addition():
    record = _record()
    assert record["future_family_blacklist_addition"] == (
        "volatility_compression_expansion")
    assert "must_not_be_reproposed_as_is" in record[
        "future_family_blacklist_reason"]
    assert tuple(record["prior_ledger_families"]) == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter")


# (10) full pushed C7 evidence chain certifies live ---------------------

def test_10_full_pushed_chain_certifies_live():
    record = _record()
    assert record["verdict"] == rj7.VERDICT_RJ7_RECORDED
    expected_chain = (
        "volatility_compression_expansion_v1_family_proposal_contract",
        "volatility_compression_expansion_v1_spec_review_contract",
        "volatility_compression_expansion_v1_detector_spec_dry_run"
        "_contract",
        "volatility_compression_expansion_v1_detector_dry_run_review"
        "_contract",
        "volatility_compression_expansion_v1_real_candle_labels_review"
        "_contract",
        "volatility_compression_expansion_v1_single_edit_relaxed"
        "_contraction_decision_contract",
        "volatility_compression_expansion_v1_edited_real_candle_labels"
        "_review_contract",
        "strategy_factory_overnight_research_autopilot_v2_contract",
        "strategy_factory_candidate_recommendation_v1_contract",
        "strategy_factory_autopilot_research_loop_v1_contract")
    assert tuple(record["pushed_evidence_chain"]) == expected_chain


# (11) rejection record fails on any frozen-fact change -----------------

def test_11_rejection_record_fails_on_any_frozen_fact_change():
    for field, value in (
            ("rejection_status", "APPROVED"),
            ("rejection_reason", "PROFITABLE"),
            ("edit_classification", "tampered"),
            ("edited_detection_classification", "tampered"),
            ("ledger_position", 6),
            ("prior_ledger_families", []),
            ("expected_original_detection", {}),
            ("expected_edit", {}),
            ("expected_edited_detection", {}),
            ("expected_staged_source_shas", {}),
            ("auto_rejection_triggers_satisfied", {}),
            ("rejection_facts", []),
            ("evidence_notes", []),
            ("seeds_for_future_families_only", []),
            ("seeds_are_never_rescue_paths", False),
            ("future_family_blacklist_addition", "tampered"),
            ("future_family_blacklist_reason", "tampered"),
            ("pushed_evidence_chain", []),
            ("edit_allowance_spent", False),
            ("candidate_7_may_continue_as_is", True),
            ("candidate_7_may_receive_another_edit", True),
            ("further_detections_authorized", True),
            ("further_replays_authorized", True),
            ("further_relabels_authorized", True),
            ("ledger_now_contains_seven_records", False),
            ("prior_six_records_unchanged", False),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("claims_profitability", True),
            ("live_gate_locked", False),
            ("verdict", "C7_APPROVED_FOR_TRADING")):
        tampered = _record()
        tampered[field] = value
        assert rj7.validate_c7_rejection_record(
            tampered)["valid"] is False, field


# (12) no profitability / paper / live / winner wording ---------------

def test_12_no_profitability_paper_live_or_winner_wording():
    record = _record()
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_micro_live"] is False
    assert record["authorizes_live_trading"] is False
    assert record["claims_profitability"] is False
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    facts = record["rejection_facts"]
    for fact in ("no paper approval", "no live approval",
                 "no profitability claim permitted",
                 "no winner wording permitted"):
        assert fact in facts, fact
    label = rj7.RJ7_LABEL
    assert "READ-ONLY" in label
    assert "REJECTED KEPT ON RECORD" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "ZERO ACCEPTED REAL-CANDLE SETUPS" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase


# (13) no trading-adjacent capability ----------------------------------

def test_13_no_trading_adjacent_capability():
    record = _record()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "computes_pnl_now", "applies_another_edit",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key


# (14) AST / purity ----------------------------------------------------

def test_14_ast_purity_and_no_writers_or_runners():
    assert rj7.get_c7_rejection_record_label() == rj7.RJ7_LABEL
    assert rj7.RJ7_MODE == "RESEARCH_ONLY"
    assert rj7.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj7.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj7.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
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


def test_determinism():
    assert _record() == _record()
