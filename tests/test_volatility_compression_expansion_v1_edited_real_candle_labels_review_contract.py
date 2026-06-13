"""Tests for the Candidate #7 edited real-candle labels review
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Verifies: chain gates live; both edited artifact shas; original
pushed-review artifact shas remain byte-identical; staged BTCUSD shas
unchanged; aggregation rule identical to original; 122 total
attempts; 0 accepted; 122 rejected on `rejected_contraction_window`;
0 anti-cluster drops; zero floor pass; event_index range [118, 239];
first/last sorted setup IDs identical to original; rejection reasons
in every label reference `strict_below_0.7_x_rolling_avg`; summary
self-claims (including edit-token-spent flags); the post-edit
auto-rejection trigger `near_zero_accepted_count_after_edited_detection`
is recorded as fired; review flags downstream locks; AST/purity green;
commander safety suite alongside (12 tests)."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.volatility_compression_expansion_v1_edited_real_candle_labels_review_contract as c7el

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "edited_labels_exists": True, "edited_summary_exists": True,
        "edited_labels_sha256": c7el.EXPECTED_EDITED_LABELS_SHA256,
        "edited_summary_sha256": c7el.EXPECTED_EDITED_SUMMARY_SHA256,
        "edited_labels_line_count": c7el.EXPECTED_TOTAL_ATTEMPTS,
        "status_breakdown": dict(c7el.EXPECTED_STATUS_BREAKDOWN),
        "all_symbols_btcusd": True,
        "all_timeframes_4h": True,
        "all_direction_long": True,
        "all_rejection_reasons_reference_0_7": True,
        "min_event_index_seen": c7el.EXPECTED_MIN_EVENT_INDEX,
        "max_event_index_seen": c7el.EXPECTED_MAX_EVENT_INDEX,
        "first_three_sorted_setup_ids":
            c7el.EXPECTED_FIRST_THREE_SORTED_SETUP_IDS,
        "last_three_sorted_setup_ids":
            c7el.EXPECTED_LAST_THREE_SORTED_SETUP_IDS,
        "summary_candidate_id":
            "VOLATILITY_COMPRESSION_EXPANSION_V1",
        "summary_edit_applied": "relaxed_contraction_fraction_only",
        "summary_edit_parameter_name": "CONTRACTION_FRACTION",
        "summary_edit_parameter_old_value": 0.6,
        "summary_edit_parameter_new_value": 0.7,
        "summary_symbol": "BTCUSD",
        "summary_timeframe": "4h",
        "summary_direction": "long_only",
        "summary_sample_tag": "2026-05-02_2026-06-10",
        "summary_edit_token_used": 1,
        "summary_edits_remaining_after_this": 0,
        "summary_this_is_the_only_allowed_c7_edit": True,
        "summary_no_other_numeric_changed_besides_contraction"
        "_fraction": True,
        "summary_anti_cluster_does_not_consume_edit_token": True,
        "summary_replay_executed_now": False,
        "summary_pnl_computed": False,
        "summary_labels_authorize_nothing": True,
        "summary_statuses_closed_set_ok": True,
        "summary_original_labels_sha256_verified":
            c7el.EXPECTED_ORIGINAL_LABELS_SHA256,
        "summary_original_summary_sha256_verified":
            c7el.EXPECTED_ORIGINAL_SUMMARY_SHA256,
        "summary_git_head": c7el.HEAD_AT_EDITED_DETECTION,
        "summary_total_attempts": 122,
        "summary_accepted_before_anti_cluster": 0,
        "summary_accepted_after_anti_cluster": 0,
        "summary_rejected_by_scanner": 122,
        "summary_dropped_by_anti_cluster": 0,
        "summary_status_breakdown":
            {"rejected_contraction_window": 122},
        "summary_floor_pass_pre": {"2r": 0, "3r": 0, "4r": 0},
        "summary_floor_pass_post": {"2r": 0, "3r": 0, "4r": 0},
        "summary_bars_15m": 3840,
        "summary_bars_4h": 240,
        "original_labels_sha256_now":
            c7el.EXPECTED_ORIGINAL_LABELS_SHA256,
        "original_summary_sha256_now":
            c7el.EXPECTED_ORIGINAL_SUMMARY_SHA256,
        "original_artifacts_unchanged": True,
        "staged_shas_now": dict(c7el.EXPECTED_STAGED_SHAS_FROZEN),
        "staged_shas_match": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c7el.certify_c7_edited_labels_review(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_edited_and_original_artifact_shas_frozen():
    assert c7el.EXPECTED_EDITED_LABELS_SHA256 == (
        "cc258348c9962c11a3bc60180f589ebc6353ceb16a44734ae9a541aa91b569"
        "5e")
    assert c7el.EXPECTED_EDITED_SUMMARY_SHA256 == (
        "60a5a04feb448c9e3cfd03b136be3f837bf4b623cc3667691ef4d95b05782"
        "34c")
    assert c7el.EXPECTED_ORIGINAL_LABELS_SHA256 == (
        "dc242578436b00bd22b5352153e5b5226d3dce4449bf67db6ab9229d61f988"
        "61")
    assert c7el.EXPECTED_ORIGINAL_SUMMARY_SHA256 == (
        "b9d9d781d7557ad58d7bae3e796cf8d9cea582b7fd71f8e7ca8672c35ffec"
        "32e")
    # edited sha tampers reject
    bad = _good_observation()
    bad["edited_labels_sha256"] = "00" * 32
    assert "edited_labels_sha_mismatch" in (
        c7el.certify_c7_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["edited_summary_sha256"] = "00" * 32
    assert "edited_summary_sha_mismatch" in (
        c7el.certify_c7_edited_labels_review(bad2)["failures"])
    # original sha drift rejects
    bad3 = _good_observation()
    bad3["original_artifacts_unchanged"] = False
    assert "original_pushed_review_artifacts_changed" in (
        c7el.certify_c7_edited_labels_review(bad3)["failures"])


def test_staged_btcusd_shas_and_aggregation_rule_unchanged():
    assert set(c7el.EXPECTED_STAGED_SHAS_FROZEN) == {
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv",
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"}
    rule = c7el.EXPECTED_AGGREGATION_RULE
    assert rule["method"] == "aggregate_4h_from_15m"
    assert rule["buckets_aligned_to_hours"] == (0, 4, 8, 12, 16, 20)
    assert rule["complete_bucket_rule"] == (
        "exactly_16_15m_bars_per_bucket")
    assert rule["incomplete_buckets_dropped"] is True
    assert rule["bars_15m_input"] == 3840
    assert rule["bars_4h_output"] == 240
    bad = _good_observation()
    bad["staged_shas_match"] = False
    assert "staged_data_shas_changed" in (
        c7el.certify_c7_edited_labels_review(bad)["failures"])


def test_frozen_counts_are_zero_accepted_and_zero_drops():
    assert c7el.EXPECTED_TOTAL_ATTEMPTS == 122
    assert c7el.EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER == 0
    assert c7el.EXPECTED_ACCEPTED_POST_ANTI_CLUSTER == 0
    assert c7el.EXPECTED_REJECTED_BY_SCANNER == 122
    assert c7el.EXPECTED_DROPPED_BY_ANTI_CLUSTER == 0
    assert sum(c7el.EXPECTED_STATUS_BREAKDOWN.values()) == 122
    assert c7el.EXPECTED_STATUS_BREAKDOWN == {
        "rejected_contraction_window": 122}
    for field, value in (
            ("edited_labels_line_count", 121),
            ("summary_total_attempts", 121),
            ("summary_accepted_before_anti_cluster", 1),
            ("summary_accepted_after_anti_cluster", 1),
            ("summary_rejected_by_scanner", 100),
            ("summary_dropped_by_anti_cluster", 5),
            ("status_breakdown",
             {"accepted_for_replay_review": 122})):
        bad = _good_observation()
        bad[field] = value
        assert c7el.certify_c7_edited_labels_review(
            bad)["certified"] is False, field


def test_rejection_reason_must_reference_0_7():
    assert c7el.EXPECTED_REJECTION_REASON_FRAGMENT == (
        "strict_below_0.7_x_rolling_avg")
    bad = _good_observation()
    bad["all_rejection_reasons_reference_0_7"] = False
    assert "rejection_reasons_must_reference_strict_below_0_7" in (
        c7el.certify_c7_edited_labels_review(bad)["failures"])


def test_floor_pass_is_zero_at_every_variant():
    assert c7el.EXPECTED_FLOOR_PASS_COUNTS == {
        "2r": 0, "3r": 0, "4r": 0}
    for key, value in (
            ("summary_floor_pass_pre", {"2r": 1, "3r": 0, "4r": 0}),
            ("summary_floor_pass_post", {"2r": 0, "3r": 5, "4r": 0})):
        bad = _good_observation()
        bad[key] = value
        assert c7el.certify_c7_edited_labels_review(
            bad)["certified"] is False, key


def test_event_index_range_and_first_last_setup_ids_identical_to_original():
    assert c7el.EXPECTED_MIN_EVENT_INDEX == 118
    assert c7el.EXPECTED_MAX_EVENT_INDEX == 239
    assert (c7el.EXPECTED_MAX_EVENT_INDEX
            - c7el.EXPECTED_MIN_EVENT_INDEX + 1) == 122
    assert c7el.EXPECTED_FIRST_THREE_SORTED_SETUP_IDS == (
        "BTCUSD_2026-05-21T16:00:00Z",
        "BTCUSD_2026-05-21T20:00:00Z",
        "BTCUSD_2026-05-22T00:00:00Z")
    assert c7el.EXPECTED_LAST_THREE_SORTED_SETUP_IDS == (
        "BTCUSD_2026-06-10T12:00:00Z",
        "BTCUSD_2026-06-10T16:00:00Z",
        "BTCUSD_2026-06-10T20:00:00Z")


def test_summary_self_claims_lock_edit_token_spent():
    claims = c7el.EXPECTED_SUMMARY_SELF_CLAIMS
    assert claims["edit_applied"] == "relaxed_contraction_fraction_only"
    assert claims["edit_parameter_name"] == "CONTRACTION_FRACTION"
    assert claims["edit_parameter_old_value"] == 0.6
    assert claims["edit_parameter_new_value"] == 0.7
    assert claims["edit_token_used"] == 1
    assert claims["edits_remaining_after_this"] == 0
    assert claims["this_is_the_only_allowed_c7_edit"] is True
    assert claims[
        "no_other_numeric_changed_besides_contraction_fraction"
    ] is True
    assert claims["anti_cluster_does_not_consume_edit_token"] is True
    assert claims["replay_executed_now"] is False
    assert claims["pnl_computed"] is False
    # mutating any claim rejects
    bad = _good_observation()
    bad["summary_edit_token_used"] = 2
    assert "summary_claim_mismatch:edit_token_used" in (
        c7el.certify_c7_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["summary_edits_remaining_after_this"] = 1
    assert "summary_claim_mismatch:edits_remaining_after_this" in (
        c7el.certify_c7_edited_labels_review(bad2)["failures"])
    bad3 = _good_observation()
    bad3["summary_edit_parameter_new_value"] = 0.8
    assert "summary_claim_mismatch:edit_parameter_new_value" in (
        c7el.certify_c7_edited_labels_review(bad3)["failures"])
    bad4 = _good_observation()
    bad4["summary_no_other_numeric_changed_besides_contraction"
         "_fraction"] = False
    assert ("summary_claim_mismatch:"
            "no_other_numeric_changed_besides_contraction_fraction"
            ) in (
        c7el.certify_c7_edited_labels_review(bad4)["failures"])
    bad5 = _good_observation()
    bad5["summary_replay_executed_now"] = True
    assert "summary_claim_mismatch:replay_executed_now" in (
        c7el.certify_c7_edited_labels_review(bad5)["failures"])


def test_post_edit_auto_rejection_trigger_recorded_as_fired():
    record = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["expected_post_edit_auto_rejection_trigger_fired"] \
        == "near_zero_accepted_count_after_edited_detection"
    status = record["expected_auto_rejection_trigger_status"]
    assert status["near_zero_accepted_count_after_edited_detection"] \
        is True
    # the other triggers did NOT fire (no second edit, no inviolable
    # change, no artifact mismatch)
    assert status[
        "any_attempt_to_change_more_than_contraction_fraction"] is (
        False)
    assert status[
        "any_attempt_to_spend_a_second_edit_on_this_family"] is False
    assert status["any_attempt_to_change_an_inviolable_upstream_rule"] \
        is False
    assert status[
        "any_artifact_hash_or_gate_mismatch_in_edited_pipeline"] is (
        False)
    # tampering the trigger status rejects
    tampered = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    tampered["expected_auto_rejection_trigger_status"] = dict(
        tampered["expected_auto_rejection_trigger_status"],
        near_zero_accepted_count_after_edited_detection=False)
    assert c7el.validate_c7_edited_labels_review(
        tampered)["valid"] is False
    tampered2 = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    tampered2["expected_post_edit_auto_rejection_trigger_fired"] = (
        "any_attempt_to_spend_a_second_edit_on_this_family")
    assert c7el.validate_c7_edited_labels_review(
        tampered2)["valid"] is False


def test_review_flags_downstream_locks_and_no_capability():
    record = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["is_edited_labels_review_only"] is True
    assert record["second_edit_possible"] is False
    assert record["edit_token_applied_by_this_gate"] is False
    assert record["rejection_decision_made_by_this_gate"] is False
    assert record["replay_authorized_by_this_gate"] is False
    assert record["relabel_authorized_by_this_gate"] is False
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording",
                 "no_replay_authorized_by_this_gate",
                 "no_relabel_authorized_by_this_gate",
                 "no_second_edit_possible",
                 "no_rejection_record_created_by_this_gate",
                 "anti_cluster_gap_remains_proposal_level_locked",
                 "edit_token_already_spent_no_refund"):
        assert lock in locks, lock
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "computes_pnl_now",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_second_edit_now",
                "claims_profitability"):
        assert record[key] is False, key
        tampered = c7el.build_c7_edited_labels_review(
            REPO_ROOT, tracked_paths=[])
        tampered[key] = True
        assert c7el.validate_c7_edited_labels_review(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT)
            / c7el.EDITED_LABELS_PATH).is_file():
        pytest.skip("candidate #7 edited labels not present")
    record = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c7el.VERDICT_C7EL_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c7el.validate_c7_edited_labels_review(
        record)["valid"] is True
    # determinism
    assert c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[]) == record
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_runner_and_artifacts_must_stay_untracked():
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c7el.EDITED_RUNNER_PATH]
    assert "edited_runner_and_artifacts_must_stay_untracked" in (
        c7el.certify_c7_edited_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["artifacts_tracked_in_git"] = [c7el.EDITED_LABELS_PATH]
    assert "edited_runner_and_artifacts_must_stay_untracked" in (
        c7el.certify_c7_edited_labels_review(bad2)["failures"])


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.volatility_compression_expansion_v1_edited_real_candle_labels_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            rec = mod.build_c7_edited_labels_review(
                REPO_ROOT, tracked_paths=[])
            assert rec["verdict"] == c7el.VERDICT_C7EL_BLOCKED, key
            assert "six_record_ledger_broken" in rec["blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])["verdict"] == (
            c7el.VERDICT_C7EL_FROZEN)


def test_label_next_action_and_module_purity():
    record = c7el.build_c7_edited_labels_review(
        REPO_ROOT, tracked_paths=[])
    assert record["next_required_action"] == (
        "BUILD_C7_REJECTION_RECORD_AS_SEVENTH_LEDGER_ENTRY")
    assert c7el.VERDICT_C7EL_FROZEN == (
        "CANDIDATE_7_EDITED_REAL_CANDLE_LABELS_REVIEW_FROZEN")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7el.NEXT_REQUIRED_ACTION.upper(), banned
    assert c7el.get_candidate_7_edited_labels_review_label() == (
        c7el.C7EL_LABEL)
    assert "READ-ONLY" in c7el.C7EL_LABEL
    assert "RESEARCH ONLY" in c7el.C7EL_LABEL
    assert "ZERO ACCEPTED SETUPS AFTER EDIT" in c7el.C7EL_LABEL
    assert "POST-EDIT AUTO-REJECTION TRIGGER FIRED" in c7el.C7EL_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c7el.C7EL_LABEL
    src = open(c7el.__file__, encoding="utf-8").read()
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
                   "os", "io", "shutil", "databento", "ssl", "ftplib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
