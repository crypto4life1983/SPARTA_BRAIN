"""Tests for the Candidate #9 real-candle labels review / evidence-
freeze contract (LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1).

Verifies: chain-gate on the 8-record ledger + the full C9 chain
through the pushed dry-run review + V4 + V3 + V2 + REC + AP;
SHA-256 pins of the untracked detector-labels and detector-summary
artifacts and the two staged BTCUSD 15m CSVs; frozen counts (3840
bars, 8 attempts, 1 accepted pre, 1 accepted post, 7 rejected, 0
anti-cluster drops); identity checks; status breakdown
{accepted_for_replay_review: 1, rejected_geometry_floor: 7};
sample-size adequacy structurally FAILED (1 < 20) without consuming
the edit token; anti-cluster gap = 8 without consuming the edit
token; explicit-edge-argument field still proposal-locked;
downstream replay / relabel / paper / live gates remain locked;
runner and artifacts remain untracked; AST/purity green for the
contract.

Optimization: a single shared module-level `_R` record built once at
import time. Tampering tests use deepcopy + targeted mutation and
validate without rebuilding."""

from __future__ import annotations

import ast
import copy
import subprocess

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract as c9l
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
_R = c9l.build_c9_labels_review(".", _tracked_paths())


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_chain_gates_all_certify():
    assert _R["verdict"] == c9l.VERDICT_C9L_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert c9l.validate_c9_labels_review(_R)["valid"] is True


def test_full_chain_certifies():
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert c9s.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)
    assert c9d.build_candidate_9_detector_spec_contract()[
        "verdict"] == c9d.VERDICT_C9D_READY
    assert c9r.build_candidate_9_dry_run_review()["verdict"] == (
        c9r.VERDICT_C9R_FROZEN)
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

def test_artifact_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == (
        "8a9bb08d9e03f7c49961830c53c182a61b619013c48ed862e2be5d4b7"
        "dd40fbf")
    assert _R["expected_summary_sha256"] == (
        "8ff429165b8cfbfaa9ed1c8cde3674cf901cd373ca1404d414b0d01e8"
        "cc90d4e")
    assert _R["head_at_detection"] == (
        "78026474f2f6798032863d1840aab5788f378b34")
    assert _R["runner_path_untracked_only"] == (
        "tools/c9_real_candle_detection_once.py")
    assert _R["labels_path"] == (
        "data/low_volume_capitulation_c9/detector_labels/"
        "c9_detector_labels_2026-05-02_2026-06-10.json")
    assert _R["summary_path"] == (
        "data/low_volume_capitulation_c9/detector_labels/"
        "c9_detector_summary_2026-05-02_2026-06-10.json")
    for field in ("expected_labels_sha256",
                  "expected_summary_sha256", "head_at_detection"):
        bad = copy.deepcopy(_R)
        bad[field] = "0" * 64
        assert c9l.validate_c9_labels_review(
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
    bad = copy.deepcopy(_R)
    bad["expected_staged_shas"] = {}
    assert c9l.validate_c9_labels_review(bad)["valid"] is False


# ---- frozen counts --------------------------------------------------------

def test_frozen_bars_scanned_window_and_counts():
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
    assert _R["expected_total_attempts"] == 8
    assert _R["expected_accepted_pre_anti_cluster"] == 1
    assert _R["expected_accepted_post_anti_cluster"] == 1
    assert _R["expected_rejected_by_scanner"] == 7
    assert _R["expected_dropped_by_anti_cluster"] == 0
    for field, bad_v in (("expected_bars_scanned", 0),
                        ("expected_bars_scanned", 1000),
                        ("expected_total_attempts", 0),
                        ("expected_accepted_pre_anti_cluster", 0),
                        ("expected_accepted_post_anti_cluster", 0),
                        ("expected_rejected_by_scanner", 0),
                        ("expected_dropped_by_anti_cluster", 5)):
        bad = copy.deepcopy(_R)
        bad[field] = bad_v
        assert c9l.validate_c9_labels_review(
            bad)["valid"] is False, (field, bad_v)


def test_identity_checks_consistent():
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


def test_status_breakdown_frozen():
    breakdown = _R["expected_status_breakdown"]
    assert breakdown["accepted_for_replay_review"] == 1
    assert breakdown["rejected_geometry_floor"] == 7
    # No other statuses present (no entry-bar invalidation, no
    # invalid stop geometry, no no_evaluation_bar, no clustered)
    assert set(breakdown.keys()) == {
        "accepted_for_replay_review", "rejected_geometry_floor"}
    assert sum(breakdown.values()) == 8
    bad = copy.deepcopy(_R)
    bad["expected_status_breakdown"] = {}
    assert c9l.validate_c9_labels_review(bad)["valid"] is False


# ---- sample-size adequacy STRUCTURAL FAILURE -----------------------------

def test_sample_size_adequacy_structurally_failed_not_satisfied():
    sa = _R["expected_sample_size_adequacy"]
    assert sa["accepted_count"] == 1
    assert sa["minimum_required_at_labels_review_gate"] == 20
    assert sa["below_minimum_at_dry_run"] is True
    assert sa["enforced_at_labels_review_gate_only"] is True
    assert sa["does_not_consume_edit_token"] is True
    assert _R["expected_sample_size_satisfied"] is False
    assert _R["expected_sample_size_structural_failure"] is True
    assert 1 < 20  # explicit arithmetic verification
    # tampering on the structural-failure flag invalidates
    bad = copy.deepcopy(_R)
    bad["expected_sample_size_satisfied"] = True
    assert c9l.validate_c9_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["expected_sample_size_structural_failure"] = False
    assert c9l.validate_c9_labels_review(bad2)["valid"] is False


def test_anti_cluster_proposal_locked_and_not_edit_token():
    anti = _R["expected_anti_cluster_facts"]
    assert anti["anti_cluster_min_bar_gap"] == 8
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert anti["anti_cluster_does_not_consume_edit_token"] is True
    assert anti["accepted_before_anti_cluster"] == 1
    assert anti["accepted_after_anti_cluster"] == 1
    assert anti["dropped_by_anti_cluster"] == 0
    bad = copy.deepcopy(_R)
    bad["expected_anti_cluster_facts"] = {}
    assert c9l.validate_c9_labels_review(bad)["valid"] is False


def test_claim_locks_present_including_proposal_locks():
    locks = _R["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_edit_token_applied_by_this_gate",
            "no_rejection_decision_made_by_this_gate",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked",
            "explicit_edge_argument_field_remains_proposal_level"
            "_locked"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c9l.validate_c9_labels_review(bad)["valid"] is False


# ---- scope locks + summary self-claims ------------------------------------

def test_expected_scope_locks_all_true():
    locks = _R["expected_scope_locks"]
    for key in ("no_replay", "no_relabel", "no_pnl", "no_fetch",
                "no_network", "no_api", "no_credentials",
                "no_broker", "no_exchange", "no_wallet",
                "no_scheduler", "no_paper_trading",
                "no_micro_live", "no_live_trading",
                "no_edit_token_consumed",
                "no_downstream_gates_unlocked",
                "explicit_edge_argument_field_proposal_locked_not"
                "_edit_token"):
        assert locks[key] is True, key


def test_expected_summary_self_claims():
    claims = _R["expected_summary_self_claims"]
    assert claims["candidate_id"] == (
        "LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1")
    assert claims["candidate_family"] == (
        "low_volume_downside_capitulation_mean_reversion")
    assert claims["symbol"] == "BTCUSD"
    assert claims["timeframe"] == "15m"
    assert claims["direction"] == "long_only"
    assert claims["attempts"] == 8
    assert claims["accepted_pre_anti_cluster"] == 1
    assert claims["accepted_post_anti_cluster"] == 1
    assert claims["rejected"] == 7
    assert claims["anti_cluster_drops"] == 0
    assert claims["bars_scanned"] == 3840
    assert claims["anti_cluster_does_not_consume_edit_token"] is True
    assert claims["source_unchanged_during_detection"] is True


# ---- frozen detection facts ----------------------------------------------

def test_frozen_detection_facts_complete():
    findings = _R["frozen_detection_facts"]
    joined = " || ".join(findings)
    assert "single-symbol btcusd 15m" in joined
    assert "3840 staged btcusd 15m bars" in joined
    assert "8 joint-trigger attempts" in joined
    assert "structurally MUCH rarer than C8's 133 attempts" in joined
    assert ("committed institutional selling drives volume UP with "
            "price") in joined
    assert "1 accepted before anti-cluster; 1 accepted after " \
        "anti-cluster" in joined
    assert "7 rejected by scanner: all 7 on geometry_floor" in joined
    assert "1 + 7 = 8" in joined
    assert "1 + 0 = 1" in joined
    assert "SAMPLE-SIZE ADEQUACY STRUCTURALLY FAILED" in joined
    assert "1 accepted-post < 20 threshold" in joined
    assert ("anti-cluster gap remains proposal-level locked at 8 "
            "bars and does NOT consume") in joined
    assert ("sample-size adequacy threshold remains proposal-level "
            "locked at 20 accepted setups and does NOT consume") \
        in joined
    assert ("explicit-edge-argument field remains proposal/spec-"
            "level locked and does NOT consume") in joined
    assert "no replay; no pnl; no relabel; no edit token applied" \
        in joined


# ---- labels-review-only safety / capability flags ------------------------

def test_labels_review_only_with_all_downstream_locked():
    assert _R["is_labels_review_only"] is True
    assert _R["current_loop_stage"] == (
        "detector_and_label_review")
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        assert _R[key] is False, key
    # exhaustive tampering check on capability flags
    for key in ("runs_real_candle_detection",
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
        assert c9l.validate_c9_labels_review(
            bad)["valid"] is False, key


def test_label_next_required_action_and_label_text():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C9_SPEND_SINGLE_EDIT_OR_REJECT_ON_SAMPLE"
        "_SIZE_INADEQUACY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c9l.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9l.get_candidate_9_labels_review_label() == c9l.C9L_LABEL
    assert c9l.C9L_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NOT A RESCUE",
                   "NOT A PROFITABILITY CLAIM",
                   "SAMPLE-SIZE ADEQUACY STRUCTURALLY FAILED",
                   "1 ACCEPTED POST ANTI-CLUSTER"):
        assert phrase in c9l.C9L_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9l.C9L_LABEL.upper(), (
            banned_phrase)


def test_runner_and_artifacts_remain_untracked_in_git():
    tracked = _tracked_paths()
    for path in (c9l.RUNNER_PATH, c9l.LABELS_PATH, c9l.SUMMARY_PATH):
        assert path not in tracked, path
    for tracked_path in tracked:
        assert not tracked_path.startswith(
            "data/low_volume_capitulation_c9/"), tracked_path
    assert _R["failures"] == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9l.__file__, encoding="utf-8").read()
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
