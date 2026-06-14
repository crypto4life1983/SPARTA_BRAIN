"""Tests for the Candidate #9 single pre-committed edit decision
contract -- relaxed downside z-score threshold (-2.0 -> -1.5).

Verifies: chain-gate on the 8-record ledger + full C9 chain through
the pushed labels review + V4 + V3 + V2 + REC + AP; edit token
spent exactly once on DOWNSIDE_Z_SCORE_THRESHOLD only; old/new
values exactly -2.0 and -1.5; all other C9 parameters remain
locked (inviolable rules dict); anti-cluster gap (8), sample-size
threshold (20), AND explicit-edge-argument field all remain
proposal/spec-level locked and NOT consumed by this edit token;
labels-review motivation frozen (8/1/1/7/0 counts, sample-size
structural failure True); 12 post-edit auto-rejection triggers
present; downstream capability flags all False; AST/purity green.

Optimization: shared module-level `_R` record built once at import
time."""

from __future__ import annotations

import ast
import copy
import subprocess

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract as c9l
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


_R = c9e.build_c9_single_edit_relaxed_z_score(".", _tracked_paths())


# ---- chain gate + approved verdict --------------------------------------

def test_decision_approved_and_chain_gates_all_certify():
    assert _R["verdict"] == c9e.VERDICT_C9E_APPROVED
    assert _R["blockers"] == []
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        _R)["valid"] is True


def test_full_chain_certifies():
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert c9s.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)
    assert c9d.build_candidate_9_detector_spec_contract()[
        "verdict"] == c9d.VERDICT_C9D_READY
    assert c9r.build_candidate_9_dry_run_review()["verdict"] == (
        c9r.VERDICT_C9R_FROZEN)
    assert c9l.build_c9_labels_review(
        ".", _tracked_paths())["verdict"] == c9l.VERDICT_C9L_FROZEN
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


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_single_edit_relaxed_z_score_decision_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_c9_single_edit_relaxed_z_score(
                ".", _tracked_paths())
            assert record["verdict"] == c9e.VERDICT_C9E_BLOCKED, key
            assert "eight_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)


# ---- edit token spent on z-score threshold only ------------------------

def test_edit_token_spent_exactly_once_on_z_threshold():
    assert _R["edit_token_used"] == 1
    assert _R["edits_remaining_after_this"] == 0
    assert _R["edit_kind"] == (
        "relaxed_downside_z_score_threshold_only")
    assert _R["edit_parameter_name"] == "DOWNSIDE_Z_SCORE_THRESHOLD"
    assert _R["edit_parameter_old_value"] == -2.0
    assert _R["edit_parameter_new_value"] == -1.5
    assert _R["edit_token_spent_by_this_contract"] is True
    assert _R["this_is_the_only_allowed_c9_edit"] is True
    assert _R["is_single_controlled_relaxation"] is True
    assert _R["is_a_rescue_bundle"] is False
    assert _R["is_a_rescue_attempt"] is False
    bad = copy.deepcopy(_R)
    bad["edit_token_used"] = 2
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["edit_parameter_new_value"] = -2.5
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        bad2)["valid"] is False
    bad3 = copy.deepcopy(_R)
    bad3["edit_parameter_name"] = "VOLUME_PERCENTILE_THRESHOLD"
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        bad3)["valid"] is False


def test_edit_rule_frozen():
    rule = _R["edit_rule"]
    assert rule["parameter"] == "DOWNSIDE_Z_SCORE_THRESHOLD"
    assert rule["old_value"] == -2.0
    assert rule["new_value"] == -1.5
    assert rule["is_a_single_controlled_relaxation_not_a_bundle"] is (
        True)
    assert rule["no_other_detector_change"] is True
    assert rule["no_lookahead"] is True
    assert rule["deterministic"] is True
    assert rule["applies_to_all_attempts_uniformly"] is True
    assert rule[
        "is_a_strict_less_than_check_against_relaxed_threshold"
    ] is True
    assert "the only valid reason" not in rule["rationale"]
    assert "the closest evidence-supported relaxation" in rule[
        "rationale"] or ("relaxing the z threshold by one half-sigma"
                         in rule["rationale"])
    assert "WITHOUT relaxing the volume condition" in rule[
        "rationale"] or (
        "preserving the unchanged below-median volume condition"
        in rule["rationale"])
    bad = copy.deepcopy(_R)
    bad["edit_rule"]["no_other_detector_change"] = False
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        bad)["valid"] is False


# ---- inviolable rules locked --------------------------------------------

def test_inviolable_rules_all_other_c9_parameters_remain_locked():
    invio = _R["inviolable_rules"]
    assert invio["atr_length"] == 14
    assert invio["rolling_window_bars"] == 96
    assert invio["volume_percentile_threshold"] == 50.0
    assert invio["volume_strict_below_median"] is True
    assert invio[
        "joint_trigger_both_conditions_required_on_same_bar"] is (
        True)
    assert invio["entry_rule"] == (
        "close_of_next_completed_15m_bar_after_trigger_bar")
    assert invio["no_intrabar_entry"] is True
    assert invio[
        "entry_bar_close_must_be_strictly_above_trigger_bar_low"
    ] is True
    assert invio["structure_stop_buffer_atr_multiplier"] == 0.20
    assert invio["stop_price_formula"] == (
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar")
    assert invio["stop_never_tightened_after_entry"] is True
    assert invio[
        "stop_must_be_below_entry_and_below_trigger_low"] is True
    assert invio["target_variants"] == ["2r", "3r", "4r"]
    assert invio["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    assert invio["timeout_bars"] == 96
    assert invio["fee_round_trip_bps"] == 27
    assert invio["minimum_gross_target_distance_floor_bps"] == 81
    assert invio["universe"] == ["BTCUSD"]
    assert invio["timeframe"] == "15m"
    assert invio["direction"] == "long_only"
    assert invio["sample_tag"] == "2026-05-02_2026-06-10"
    assert invio["no_fetch_ever"] is True
    assert invio["staged_data_never_modified"] is True
    assert invio["no_maker_rebate_assumption"] is True
    assert invio["no_zero_fee_assumption"] is True


def test_anti_cluster_sample_size_and_edge_argument_remain_non_edit_token():
    invio = _R["inviolable_rules"]
    assert invio["anti_cluster_min_bar_gap"] == 8
    assert invio[
        "anti_cluster_is_proposal_level_locked_not_edit_token"
    ] is True
    assert invio["sample_size_adequacy_threshold_min_accepted"] == 20
    assert invio[
        "sample_size_adequacy_is_proposal_level_locked_not_edit"
        "_token"] is True
    assert invio[
        "explicit_edge_argument_field_is_proposal_level_locked_not"
        "_edit_token"] is True
    # spot-check tampering on each of the three non-edit-token locks
    for key in (
            "anti_cluster_is_proposal_level_locked_not_edit_token",
            "sample_size_adequacy_is_proposal_level_locked_not_edit"
            "_token",
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_edit_token"):
        bad = copy.deepcopy(_R)
        bad["inviolable_rules"][key] = False
        assert c9e.validate_c9_single_edit_relaxed_z_score(
            bad)["valid"] is False, key
    # The decision record itself must also report that the edit does
    # NOT modify any of these three
    assert _R["modifies_anti_cluster_gap_via_this_edit"] is False
    assert _R[
        "modifies_sample_size_threshold_via_this_edit"] is False
    assert _R[
        "modifies_explicit_edge_argument_field_via_this_edit"
    ] is False
    for key in ("modifies_anti_cluster_gap_via_this_edit",
                "modifies_sample_size_threshold_via_this_edit",
                "modifies_explicit_edge_argument_field_via_this_edit"
                ):
        bad = copy.deepcopy(_R)
        bad[key] = True
        assert c9e.validate_c9_single_edit_relaxed_z_score(
            bad)["valid"] is False, key


# ---- frozen labels-review motivation -----------------------------------

def test_frozen_labels_review_evidence_for_edit():
    ev = _R["frozen_labels_review_evidence_for_edit"]
    assert ev["labels_sha256"] == (
        "8a9bb08d9e03f7c49961830c53c182a61b619013c48ed862e2be5d4b7"
        "dd40fbf")
    assert ev["summary_sha256"] == (
        "8ff429165b8cfbfaa9ed1c8cde3674cf901cd373ca1404d414b0d01e8"
        "cc90d4e")
    assert ev["head_at_detection"] == (
        "78026474f2f6798032863d1840aab5788f378b34")
    assert ev["total_attempts"] == 8
    assert ev["accepted_pre_anti_cluster"] == 1
    assert ev["accepted_post_anti_cluster"] == 1
    assert ev["rejected_by_scanner"] == 7
    assert ev["dropped_by_anti_cluster"] == 0
    assert ev["status_breakdown"] == {
        "accepted_for_replay_review": 1,
        "rejected_geometry_floor": 7}
    assert ev["sample_size_threshold_min_required"] == 20
    assert ev["sample_size_satisfied"] is False
    assert ev["sample_size_structural_failure"] is True
    assert ev["edit_token_unused_before_this_decision"] is True
    assert ev["no_replay_run"] is True
    assert ev["no_pnl_computed"] is True
    assert ev["anti_cluster_did_not_consume_edit_token"] is True
    assert ev["sample_size_did_not_consume_edit_token"] is True
    assert ev[
        "explicit_edge_argument_did_not_consume_edit_token"] is True


# ---- post-edit auto-rejection triggers ----------------------------------

def test_post_edit_auto_rejection_triggers_complete():
    triggers = tuple(_R["post_edit_auto_rejection_triggers"])
    expected = (
        "near_zero_accepted_count_after_edited_detection",
        "sample_size_still_below_threshold_after_edited_detection",
        "any_variant_net_negative_after_edited_replay",
        "any_variant_gross_negative_after_edited_replay",
        "any_variant_hit_rate_below_gross_breakeven_after_edited"
        "_replay",
        "any_artifact_hash_or_gate_mismatch_in_edited_pipeline",
        "any_attempt_to_change_an_inviolable_upstream_rule",
        "any_attempt_to_change_more_than_downside_z_score_threshold",
        "any_attempt_to_spend_a_second_edit_on_this_family",
        "any_attempt_to_modify_anti_cluster_gap_via_this_edit",
        "any_attempt_to_modify_sample_size_threshold_via_this_edit",
        "any_attempt_to_modify_explicit_edge_argument_field_via"
        "_this_edit",
    )
    assert triggers == expected


# ---- claim locks present ------------------------------------------------

def test_claim_locks_present_including_three_proposal_locks():
    locks = _R["claim_locks"]
    for required in (
            "edit_is_single_parameter_relaxation_only_no_bundle",
            "edit_does_not_authorize_edited_real_candle_detection"
            "_by_itself",
            "edit_does_not_authorize_relabel",
            "edit_does_not_authorize_replay",
            "edit_does_not_authorize_pnl_computation",
            "edit_does_not_authorize_paper_or_live_or_execution",
            "edit_is_not_a_rescue_attempt",
            "no_profitability_claim",
            "no_winner_wording",
            "automatic_rejection_if_any_post_edit_trigger_fires",
            "single_pre_committed_edit_token_spent_no_further_edits"
            "_allowed",
            "anti_cluster_gap_remains_proposal_level_locked_not_edit"
            "_token",
            "sample_size_threshold_remains_proposal_level_locked_not"
            "_edit_token",
            "explicit_edge_argument_field_remains_proposal_level"
            "_locked_not_edit_token"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c9e.validate_c9_single_edit_relaxed_z_score(
        bad)["valid"] is False


# ---- decision-only safety / capability flags ---------------------------

def test_decision_only_with_all_downstream_locked():
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    assert _R["current_loop_stage"] == "detector_and_label_review"
    assert _R["next_loop_stage"] == "detector_and_label_review"
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
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "authorizes_edited_real_candle_detection",
                "authorizes_relabel", "authorizes_replay",
                "authorizes_pnl_now",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_replay_gate", "unlocks_relabel_gate",
                "unlocks_paper_gate", "unlocks_micro_live_gate",
                "unlocks_live_gate",
                "claims_profitability", "executes", "writes_files"):
        assert _R[key] is False, key
        bad = copy.deepcopy(_R)
        bad[key] = True
        assert c9e.validate_c9_single_edit_relaxed_z_score(
            bad)["valid"] is False, key


def test_next_required_action_and_label():
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_9_EDITED_REAL_CANDLE_DETECTION"
        "_RELAXED_Z_THRESHOLD")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c9e.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9e.get_c9_single_edit_label() == c9e.C9E_LABEL
    assert c9e.C9E_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "SINGLE PARAMETER RELAXATION ONLY",
                   "NOT A RESCUE", "NOT A CLAIM",
                   "Relaxed Downside Z-Score Threshold",
                   "-2.0 -> -1.5"):
        assert phrase in c9e.C9E_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9e.C9E_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9e.__file__, encoding="utf-8").read()
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
