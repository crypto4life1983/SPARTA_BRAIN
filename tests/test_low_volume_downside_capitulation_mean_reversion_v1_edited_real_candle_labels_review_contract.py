"""Tests for the Candidate #9 EDITED real-candle labels review /
evidence-freeze contract (LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN
_REVERSION_V1).

Verifies: chain-gate on the 8-record ledger + full C9 chain through
the pushed labels review + single-edit decision + V4 + V3 + V2 +
REC + AP; SHA-256 pins of the untracked edited detection artifacts
and the two staged BTCUSD 15m CSVs; frozen edited counts (3840
bars, 27 attempts, 5 accepted pre, 5 accepted post, 22 rejected, 0
anti-cluster drops); identity checks; status breakdown
{accepted_for_replay_review: 5, rejected_geometry_floor: 12,
rejected_entry_bar_close_at_or_below_trigger_bar_low: 10};
sample-size adequacy STILL FAILED (5 < 20) post-edit; post-edit
auto-rejection trigger `sample_size_still_below_threshold_after
_edited_detection` FIRED; edit-token state carried forward (1 used,
0 remaining); anti-cluster (8), sample-size threshold (20), AND
explicit-edge-argument field all proposal-locked NOT consumed by
this edit; downstream gates locked; AST/purity green.

Optimization: shared module-level `_R` record built once at import
time."""

from __future__ import annotations

import ast
import copy
import subprocess

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_edited_real_candle_labels_review_contract as c9el
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


# Build the record ONCE at module import time.
_R = c9el.build_c9_edited_labels_review(".", _tracked_paths())


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_chain_gates_all_certify():
    assert _R["verdict"] == c9el.VERDICT_C9EL_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert c9el.validate_c9_edited_labels_review(_R)["valid"] is True


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
    assert c9e.build_c9_single_edit_relaxed_z_score(
        ".", _tracked_paths())["verdict"] == (
            c9e.VERDICT_C9E_APPROVED)
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


def test_eight_record_ledger_intact():
    assert _R["ledger_status_eight_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 8
    assert _R["ledger_all_rejected_kept_on_record"] is True


# ---- SHA pins frozen ------------------------------------------------------

def test_edited_artifact_sha_pins_frozen():
    assert _R["expected_edited_labels_sha256"] == (
        "6e4f89821547cb89bb94b58a3c6dfcaac486af278aba6cf47171f72e3"
        "59d3474")
    assert _R["expected_edited_summary_sha256"] == (
        "f689920b512587386538d83045ef3208ae8db7577abd6b0e79197f5cf"
        "afc53dc")
    assert _R["head_at_edited_detection"] == (
        "6e88a827be09ab24b062c47aa4d1e313c39e3dfb")
    assert _R["edited_runner_path_untracked_only"] == (
        "tools/c9_edited_real_candle_detection_relaxed_z_once.py")
    assert _R["edited_labels_path"].endswith(
        "c9_edited_detector_labels_relaxed_z_2026-05-02_2026-06-10.json")
    assert _R["edited_summary_path"].endswith(
        "c9_edited_detector_summary_relaxed_z_2026-05-02_2026-06-10.json")
    for field in ("expected_edited_labels_sha256",
                  "expected_edited_summary_sha256",
                  "head_at_edited_detection"):
        bad = copy.deepcopy(_R)
        bad[field] = "0" * 64
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, field


def test_staged_source_data_sha_pins_frozen():
    pins = _R["expected_staged_shas"]
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv"
    ] == ("4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0a"
          "fd1298ee9f14")
    assert pins[
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"
    ] == ("4bb50873df5194de65315bf44f1823d17922e445745401eb01aa"
          "1670aed4956d")


def test_original_labels_review_sha_pins_carried_forward():
    pins = _R["expected_original_labels_sha_pins_carried_forward"]
    # The original (pre-edit) C9 labels SHA pins from the pushed
    # labels review must be carried forward unchanged.
    assert pins["original_labels_sha256"] == (
        "8a9bb08d9e03f7c49961830c53c182a61b619013c48ed862e2be5d4b7"
        "dd40fbf")
    assert pins["original_summary_sha256"] == (
        "8ff429165b8cfbfaa9ed1c8cde3674cf901cd373ca1404d414b0d01e8"
        "cc90d4e")


# ---- frozen edited counts ------------------------------------------------

def test_frozen_edited_bars_scanned_window_and_counts():
    assert _R["expected_sample_tag"] == "2026-05-02_2026-06-10"
    assert _R["expected_start_inclusive_utc"] == (
        "2026-05-02T00:00:00Z")
    assert _R["expected_end_inclusive_utc"] == (
        "2026-06-10T23:45:00Z")
    assert _R["expected_bars_scanned"] == 3840
    assert _R["expected_first_bar_time"] == (
        "2026-05-02T00:00:00Z")
    assert _R["expected_last_bar_time"] == (
        "2026-06-10T23:45:00Z")
    assert _R["expected_total_attempts"] == 27
    assert _R["expected_accepted_pre_anti_cluster"] == 5
    assert _R["expected_accepted_post_anti_cluster"] == 5
    assert _R["expected_rejected_by_scanner"] == 22
    assert _R["expected_dropped_by_anti_cluster"] == 0
    for field, bad_v in (("expected_bars_scanned", 0),
                        ("expected_total_attempts", 8),
                        ("expected_accepted_pre_anti_cluster", 1),
                        ("expected_accepted_post_anti_cluster", 1),
                        ("expected_rejected_by_scanner", 7),
                        ("expected_dropped_by_anti_cluster", 5)):
        bad = copy.deepcopy(_R)
        bad[field] = bad_v
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, (field, bad_v)


def test_edited_identity_checks_consistent():
    identity = _R["expected_identity_checks"]
    assert identity[
        "accepted_pre_plus_rejected_equals_attempts"] is True
    assert identity[
        "accepted_post_plus_dropped_equals_accepted_pre"] is True
    assert (_R["expected_accepted_pre_anti_cluster"]
            + _R["expected_rejected_by_scanner"]
            == _R["expected_total_attempts"])
    assert (_R["expected_accepted_post_anti_cluster"]
            + _R["expected_dropped_by_anti_cluster"]
            == _R["expected_accepted_pre_anti_cluster"])


def test_edited_status_breakdown_includes_new_failure_mode():
    breakdown = _R["expected_status_breakdown"]
    assert breakdown["accepted_for_replay_review"] == 5
    assert breakdown["rejected_geometry_floor"] == 12
    assert breakdown[
        "rejected_entry_bar_close_at_or_below_trigger_bar_low"] == 10
    assert set(breakdown.keys()) == {
        "accepted_for_replay_review",
        "rejected_geometry_floor",
        "rejected_entry_bar_close_at_or_below_trigger_bar_low"}
    assert sum(breakdown.values()) == 27
    bad = copy.deepcopy(_R)
    bad["expected_status_breakdown"] = {}
    assert c9el.validate_c9_edited_labels_review(
        bad)["valid"] is False


# ---- sample-size adequacy STILL FAILED + auto-rejection trigger FIRED ---

def test_sample_size_still_failed_post_edit():
    sa = _R["expected_sample_size_adequacy"]
    assert sa["accepted_count"] == 5
    assert sa["minimum_required_at_labels_review_gate"] == 20
    assert sa["below_minimum_at_dry_run"] is True
    assert sa["enforced_at_labels_review_gate_only"] is True
    assert sa["does_not_consume_edit_token"] is True
    assert _R["expected_sample_size_satisfied"] is False
    assert _R[
        "expected_sample_size_still_below_threshold_after_edited"
        "_detection"] is True
    assert 5 < 20  # explicit arithmetic verification
    for bad_v in (False, None):
        bad = copy.deepcopy(_R)
        bad[
            "expected_sample_size_still_below_threshold_after"
            "_edited_detection"] = bad_v
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, bad_v


def test_post_edit_auto_rejection_trigger_fired():
    assert _R[
        "expected_post_edit_auto_rejection_trigger_fired"] is True
    assert _R["expected_post_edit_auto_rejection_trigger_name"] == (
        "sample_size_still_below_threshold_after_edited_detection")
    for bad_v in (False, None):
        bad = copy.deepcopy(_R)
        bad["expected_post_edit_auto_rejection_trigger_fired"] = (
            bad_v)
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, bad_v


# ---- edit-token state carried forward -----------------------------------

def test_edit_state_carried_forward_z_score_only():
    es = _R["expected_edit_state_carried_forward"]
    assert es["edit_parameter"] == "DOWNSIDE_Z_SCORE_THRESHOLD"
    assert es["original_value_signed"] == -2.0
    assert es["edited_value_signed"] == -1.5
    assert es["original_abs"] == 2.0
    assert es["edited_abs"] == 1.5
    assert es["edit_token_used"] == 1
    assert es["edits_remaining_after_this"] == 0
    assert es["no_second_edit_applied"] is True
    assert es["is_single_controlled_relaxation"] is True
    assert es["is_a_rescue_bundle"] is False
    assert es["all_other_c9_parameters_unchanged"] is True
    assert es["single_edit_decision_head"] == (
        "6e88a827be09ab24b062c47aa4d1e313c39e3dfb")
    assert es["anti_cluster_did_not_consume_edit_token"] is True
    assert es["sample_size_did_not_consume_edit_token"] is True
    assert es[
        "explicit_edge_argument_field_did_not_consume_edit_token"
    ] is True
    assert es["original_c9_labels_review_sha_pins_unchanged"] is True


def test_edit_token_remaining_zero_and_no_further_edits():
    assert _R["edit_token_remaining"] == 0
    assert _R["no_further_c9_edits_allowed"] is True
    assert _R["second_edit_applied_by_this_gate"] is False
    for bad_v in (1, 2, None):
        bad = copy.deepcopy(_R)
        bad["edit_token_remaining"] = bad_v
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, bad_v
    for key in ("no_further_c9_edits_allowed",
                "second_edit_applied_by_this_gate"):
        bad = copy.deepcopy(_R)
        bad[key] = not _R[key]
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, key


def test_anti_cluster_proposal_locked_and_not_edit_token():
    anti = _R["expected_anti_cluster_facts"]
    assert anti["anti_cluster_min_bar_gap"] == 8
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["accepted_before_anti_cluster"] == 5
    assert anti["accepted_after_anti_cluster"] == 5
    assert anti["dropped_by_anti_cluster"] == 0


def test_claim_locks_present_including_edit_already_spent():
    locks = _R["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_second_edit_applied_by_this_gate",
            "no_rejection_decision_made_by_this_gate",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked",
            "explicit_edge_argument_field_remains_proposal_level"
            "_locked",
            "edit_token_already_spent_no_further_edits_allowed",
            "post_edit_auto_rejection_trigger_fired_recorded_only"
            "_human_must_authorize_rejection_record"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c9el.validate_c9_edited_labels_review(
        bad)["valid"] is False


# ---- frozen detection facts ----------------------------------------------

def test_frozen_edited_detection_facts_complete():
    findings = _R["frozen_edited_detection_facts"]
    joined = " || ".join(findings)
    assert "single-symbol btcusd 15m" in joined
    assert ("DOWNSIDE_Z_SCORE_THRESHOLD changed from -2.0 to -1.5"
            in joined)
    assert "27 joint-trigger attempts (vs 8 original)" in joined
    assert "3.4x increase" in joined
    assert "5 accepted before anti-cluster; 5 accepted after " \
        "anti-cluster" in joined
    assert "22 rejected by scanner: 12 on geometry_floor" in joined
    assert ("10 on a NEW failure mode that did not appear in the "
            "original: rejected_entry_bar_close_at_or_below_trigger"
            "_bar_low") in joined
    assert "5 + 22 = 27" in joined
    assert "5 + 0 = 5" in joined
    assert "SAMPLE-SIZE ADEQUACY STRUCTURALLY STILL FAILED" in joined
    assert "POST-EDIT AUTO-REJECTION TRIGGER FIRED" in joined
    assert ("sample_size_still_below_threshold_after_edited"
            "_detection") in joined
    assert "anti-cluster gap remains proposal-level locked" in joined
    assert "sample-size adequacy threshold remains proposal-level " \
        "locked" in joined
    assert "explicit-edge-argument field remains proposal/spec-" \
        "level locked" in joined
    assert ("edit token state: 1 used (on DOWNSIDE_Z_SCORE_THRESHOLD"
            " only)") in joined
    assert "0 remaining, no second edit allowed" in joined


# ---- edited-labels-review-only safety / capability flags ----------------

def test_edited_labels_review_only_with_all_downstream_locked():
    assert _R["is_edited_labels_review_only"] is True
    assert _R["current_loop_stage"] == (
        "detector_and_label_review")
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("second_edit_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        assert _R[key] is False, key
    # exhaustive tampering check on capability flags
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
                "computes_pnl_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_edited_labels_artifacts",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability",
                "executes", "writes_files"):
        assert _R[key] is False, key
        bad = copy.deepcopy(_R)
        bad[key] = True
        assert c9el.validate_c9_edited_labels_review(
            bad)["valid"] is False, key


def test_next_required_action_and_label_text():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C9_REJECT_AFTER_EDIT_DID_NOT_RESOLVE_SAMPLE"
        "_SIZE_INADEQUACY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c9el.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9el.get_candidate_9_edited_labels_review_label() == (
        c9el.C9EL_LABEL)
    assert c9el.C9EL_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NOT A RESCUE",
                   "NOT A PROFITABILITY CLAIM",
                   "POST-EDIT SAMPLE-SIZE STILL FAILED",
                   "POST-EDIT AUTO-REJECTION TRIGGER FIRED",
                   "5 ACCEPTED POST ANTI-CLUSTER"):
        assert phrase in c9el.C9EL_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9el.C9EL_LABEL.upper(), (
            banned_phrase)


def test_runner_and_artifacts_remain_untracked_in_git():
    tracked = _tracked_paths()
    for path in (c9el.EDITED_RUNNER_PATH, c9el.EDITED_LABELS_PATH,
                 c9el.EDITED_SUMMARY_PATH):
        assert path not in tracked, path
    for tracked_path in tracked:
        assert not tracked_path.startswith(
            "data/low_volume_capitulation_c9/"), tracked_path
    assert _R["failures"] == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9el.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "os", "io", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "statistics",
                   "random"}
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
