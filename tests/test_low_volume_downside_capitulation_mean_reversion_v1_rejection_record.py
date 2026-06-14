"""Tests for the Candidate #9 formal rejection record (9th
rejected-family ledger entry).

Verifies: chain-gate on the eight-record ledger + the full pushed C9
chain through edited labels review + V4 + V3 + V2 + Recommendation
V1 + Autopilot V1; REJECTION_STATUS = REJECTED_KEPT_ON_RECORD;
FUTURE_FAMILY_BLACKLIST_ADDITION = low_volume_downside_capitulation
_mean_reversion; ledger position = 9; edit allowance SPENT (token
consumed on DOWNSIDE_Z_SCORE_THRESHOLD -2.0 -> -1.5); original
detection evidence (3840 bars, 8/1/1/7/0) frozen; edited detection
evidence (3840 bars, 27/5/5/22/0) frozen; status breakdowns frozen;
SHA pins (original + edited labels/summary, staged source CSVs)
frozen; post-edit auto-rejection trigger fired; all downstream
capability flags False; AST/purity green."""

from __future__ import annotations

import ast
import copy
import subprocess

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_edited_real_candle_labels_review_contract as c9el
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract as c9l
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record as rj9
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_single_edit_relaxed_z_score_decision_contract as c9e
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract as c9s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


_TRACKED = _tracked_paths()
_R = rj9.build_c9_rejection_record(".", _TRACKED)


# ---- chain gate + recorded verdict ----------------------------------------

def test_rejection_recorded_and_chain_gates_all_certify():
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert c9s.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)
    assert c9d.build_candidate_9_detector_spec_contract()[
        "verdict"] == c9d.VERDICT_C9D_READY
    assert c9r.build_candidate_9_dry_run_review()["verdict"] == (
        c9r.VERDICT_C9R_FROZEN)
    assert c9l.build_c9_labels_review(
        ".", _TRACKED)["verdict"] == c9l.VERDICT_C9L_FROZEN
    assert c9e.build_c9_single_edit_relaxed_z_score(
        ".", _TRACKED)["verdict"] == c9e.VERDICT_C9E_APPROVED
    assert c9el.build_c9_edited_labels_review(
        ".", _TRACKED)["verdict"] == c9el.VERDICT_C9EL_FROZEN
    assert bl4.build_rejected_family_blacklist_v4()["verdict"] == (
        bl4.VERDICT_BL4_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    assert _R["verdict"] == rj9.VERDICT_RJ9_RECORDED
    assert _R["blockers"] == []
    assert rj9.validate_c9_rejection_record(_R)["valid"] is True


def test_rejection_status_and_classification_constants():
    assert rj9.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert "EDIT_SPENT" in rj9.REJECTION_REASON
    assert "RELAXED_DOWNSIDE_Z_SCORE_THRESHOLD" in rj9.REJECTION_REASON
    assert "SAMPLE_SIZE_STILL_BELOW_THRESHOLD" in rj9.REJECTION_REASON
    assert "EDIT_V1" in rj9.EDIT_CLASSIFICATION
    assert "FAILED_REJECT_NEXT" in rj9.EDIT_CLASSIFICATION
    assert "BOTH_BELOW_SAMPLE_SIZE_THRESHOLD_20" in (
        rj9.EDITED_DETECTION_CLASSIFICATION)
    assert rj9.FUTURE_FAMILY_BLACKLIST_ADDITION == (
        "low_volume_downside_capitulation_mean_reversion")
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert _R["ledger_position"] == 9


def test_ledger_position_and_prior_families():
    assert _R["ledger_position"] == 9
    assert _R["ledger_now_contains_nine_records"] is True
    assert _R["prior_eight_records_unchanged"] is True
    assert tuple(_R["prior_ledger_families"]) == (
        "ny_session_fvg_choch_v3",
        "crypto_intraday_breakout_pullback_structure_v2",
        "btc_sol_long_trend_continuation_v1",
        "sol_btc_long_1h_swing_structure",
        "eth_sol_relative_strength_pullback_continuation_v1",
        "multi_symbol_relative_strength_rotation_filter",
        "volatility_compression_expansion",
        "liquidity_sweep_mean_reversion")


def test_edit_token_was_spent_on_relaxed_z_score_threshold():
    edit = _R["expected_edit"]
    assert edit["edit_parameter_name"] == "DOWNSIDE_Z_SCORE_THRESHOLD"
    assert edit["edit_parameter_old_value"] == -2.0
    assert edit["edit_parameter_new_value"] == -1.5
    assert edit["edit_token_used"] == 1
    assert edit["edits_remaining_after_this"] == 0
    assert edit["this_was_the_only_allowed_c9_edit"] is True
    assert edit["no_further_c9_edits_allowed"] is True
    assert edit["no_other_numeric_changed"] is True
    assert edit[
        "anti_cluster_gap_remained_proposal_level_locked_not_edit"
        "_token"] is True
    assert edit[
        "sample_size_threshold_remained_proposal_level_locked_not"
        "_edit_token"] is True
    assert edit[
        "explicit_edge_argument_field_remained_proposal_level_locked"
        "_not_edit_token"] is True
    assert edit["is_single_controlled_relaxation"] is True
    assert edit["is_a_rescue_bundle"] is False
    assert _R["edit_allowance_spent"] is True
    assert _R["applies_another_edit"] is False


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_c9_rejection_record(".", _TRACKED)
            assert record["verdict"] == rj9.VERDICT_RJ9_BLOCKED, key
            assert "eight_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_c9_rejection_record(
        ".", _TRACKED)["verdict"] == rj9.VERDICT_RJ9_RECORDED


# ---- frozen original detection evidence -----------------------------------

def test_original_detection_evidence_frozen():
    det = _R["expected_original_detection"]
    assert det["head_at_detection"] == (
        "ba02fdea73bc344cd8e9fcd1e28a32c60932b63b")
    assert det["total_attempts"] == 8
    assert det["accepted_pre_anti_cluster"] == 1
    assert det["accepted_post_anti_cluster"] == 1
    assert det["rejected_by_scanner"] == 7
    assert det["dropped_by_anti_cluster"] == 0
    assert det["status_breakdown"] == {
        "accepted_for_replay_review": 1,
        "rejected_geometry_floor": 7}
    assert det["sample_size_threshold_min_required"] == 20
    assert det["sample_size_satisfied"] is False
    assert det["sample_size_structural_failure"] is True
    assert det["no_replay_run"] is True
    assert det["no_pnl_computed"] is True
    assert det["no_trading_authorized"] is True


# ---- frozen edited detection evidence -------------------------------------

def test_edited_detection_evidence_frozen():
    det = _R["expected_edited_detection"]
    assert det["head_at_edited_detection"] == (
        "ae65340d9999d7bc91ca11db608531e0e60f7d5c")
    assert det["total_attempts"] == 27
    assert det["accepted_pre_anti_cluster"] == 5
    assert det["accepted_post_anti_cluster"] == 5
    assert det["rejected_by_scanner"] == 22
    assert det["dropped_by_anti_cluster"] == 0
    assert det["status_breakdown"] == {
        "accepted_for_replay_review": 5,
        "rejected_geometry_floor": 12,
        "rejected_entry_bar_close_at_or_below_trigger_bar_low": 10}
    assert det["sample_size_threshold_min_required"] == 20
    assert det["sample_size_satisfied_after_edit"] is False
    assert det[
        "sample_size_still_below_threshold_after_edited_detection"
    ] is True
    assert det[
        "attempts_increased_from_8_to_27_a_3_4x_increase_matching"
        "_lower_tail_expansion"] is True
    assert det["accepted_increased_from_1_to_5"] is True
    assert det[
        "new_failure_mode_observed_entry_bar_close_at_or_below_trigger"
        "_bar_low_10_setups"] is True
    assert det["original_artifacts_unchanged"] is True
    assert det["post_edit_auto_rejection_trigger_fired"] is True
    assert det["post_edit_auto_rejection_trigger_name"] == (
        "sample_size_still_below_threshold_after_edited_detection")


def test_artifact_sha_pins_pulled_forward():
    det_orig = _R["expected_original_detection"]
    assert det_orig["labels_sha256"] == (
        "8a9bb08d9e03f7c49961830c53c182a61b619013c48ed862e2be5d"
        "4b7dd40fbf")
    assert det_orig["summary_sha256"] == (
        "8ff429165b8cfbfaa9ed1c8cde3674cf901cd373ca1404d414b0d0"
        "1e8cc90d4e")
    det_ed = _R["expected_edited_detection"]
    assert det_ed["edited_labels_sha256"] == (
        "6e4f89821547cb89bb94b58a3c6dfcaac486af278aba6cf47171f7"
        "2e359d3474")
    assert det_ed["edited_summary_sha256"] == (
        "f689920b512587386538d83045ef3208ae8db7577abd6b0e79197f"
        "5cfafc53dc")


def test_staged_source_data_sha_pins_frozen():
    pins = _R["expected_staged_source_shas"]
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv"
    ] == ("4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0a"
          "fd1298ee9f14")
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"
    ] == ("4bb50873df5194de65315bf44f1823d17922e445745401eb01aa"
          "1670aed4956d")


def test_auto_rejection_triggers_satisfied():
    triggers = _R["auto_rejection_triggers_satisfied"]
    assert triggers[
        "sample_size_still_below_threshold_after_edited_detection"
    ] is True
    assert triggers[
        "edit_token_was_spent_on_single_allowed_parameter_only"
    ] is True
    assert triggers[
        "any_attempt_to_change_more_than_downside_z_score_threshold"
    ] is False
    assert triggers[
        "any_attempt_to_spend_a_second_edit_on_this_family"] is False
    assert triggers[
        "any_attempt_to_modify_anti_cluster_gap_via_this_edit"] is (
        False)
    assert triggers[
        "any_attempt_to_modify_sample_size_threshold_via_this_edit"
    ] is False
    assert triggers[
        "any_attempt_to_modify_explicit_edge_argument_field_via_this"
        "_edit"] is False
    assert triggers[
        "any_artifact_hash_or_gate_mismatch_in_edited_pipeline"] is (
        False)


# ---- rejection narrative + seeds ------------------------------------------

def test_rejection_facts_and_evidence_notes():
    facts = " || ".join(_R["rejection_facts"])
    assert "candidate #9 is rejected" in facts
    assert "ninth ledger entry" in facts
    assert "DOWNSIDE_Z_SCORE_THRESHOLD from -2.0 to -1.5" in facts
    assert "STILL FAILED post-edit: 5 < 20" in facts
    assert "no profitability claim permitted" in facts
    assert "no winner wording permitted" in facts
    notes = " || ".join(_R["evidence_notes"])
    assert ("low-volume-downside-capitulation-mean-reversion "
            "hypothesis is unsupported") in notes
    assert ("volume condition (the structural microstructure "
            "edge) is the binding constraint") in notes
    assert "anti-cluster gap stayed proposal-level locked at 8 bars" \
        in notes
    assert ("sample-size adequacy threshold stayed proposal-level "
            "locked at 20") in notes
    assert ("explicit-edge-argument field stayed proposal/spec-level "
            "locked") in notes


def test_seeds_for_future_families_only_never_rescue():
    assert _R["seeds_are_never_rescue_paths"] is True
    seeds = " || ".join(_R["seeds_for_future_families_only"])
    assert "do_not_reuse_c9_as_is" in seeds
    assert "any_future_candidate_must_be_a_new_clean_hypothesis" \
        in seeds
    assert ("joint_price_and_volume_thresholds_can_be_structurally"
            "_too_sparse") in seeds
    assert "future_families_must_pre_justify_sample_size_adequacy" \
        in seeds
    assert "fee_aware_geometry_with_an_81_bps_floor_remains" \
        "_inviolable" in seeds


def test_future_family_blacklist_export_and_pushed_chain():
    assert _R["future_family_blacklist_addition"] == (
        "low_volume_downside_capitulation_mean_reversion")
    assert "candidate_9_rejected" in _R[
        "future_family_blacklist_reason"]
    assert ("edit_spent_on_relaxed_z_score_threshold_and_sample_size"
            "_still_below_threshold") in _R[
        "future_family_blacklist_reason"]
    chain = _R["pushed_evidence_chain"]
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_family_proposal_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_spec_review_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_detector_spec_dry_run_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_dry_run_review_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_real_candle_labels_review_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_single_edit_relaxed_z_score_decision_contract") in chain
    assert ("low_volume_downside_capitulation_mean_reversion_v1"
            "_edited_real_candle_labels_review_contract") in chain
    assert "strategy_factory_rejected_family_blacklist_v4_contract" \
        in chain


# ---- downstream gates remain locked ---------------------------------------

def test_no_downstream_gate_unlocked_and_no_trading_capability():
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    assert _R["candidate_9_may_continue_as_is"] is False
    assert _R["candidate_9_may_receive_another_edit"] is False
    assert _R["further_detections_authorized"] is False
    assert _R["further_replays_authorized"] is False
    assert _R["further_relabels_authorized"] is False
    for key in ("runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_replay", "runs_replay_now", "runs_relabel",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now", "applies_another_edit",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_edited_labels_artifacts",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "executes", "writes_files"):
        assert _R[key] is False, key
        tampered = copy.deepcopy(_R)
        tampered[key] = True
        assert rj9.validate_c9_rejection_record(
            tampered)["valid"] is False, key


def test_label_and_next_required_action():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj9.NEXT_REQUIRED_ACTION.upper(), banned
    assert rj9.get_c9_rejection_record_label() == rj9.RJ9_LABEL
    assert rj9.RJ9_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "REJECTED KEPT ON RECORD",
                   "EDIT SPENT ON RELAXED Z-SCORE THRESHOLD",
                   "SAMPLE-SIZE STILL BELOW THRESHOLD",
                   "NOT A PROFITABILITY CLAIM"):
        assert phrase in rj9.RJ9_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in rj9.RJ9_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(rj9.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
