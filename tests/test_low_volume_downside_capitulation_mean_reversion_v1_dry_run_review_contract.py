"""Tests for the Candidate #9 dry-run review / evidence-freeze
contract (LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1).

Verifies: chain-gate on the 8-record ledger + C9 family proposal +
C9 spec review + C9 detector spec/dry-run + V4 + V3 + V2 + REC + AP;
live recomputation matches every frozen fact (11 fixture summaries,
the single accepted setup's exact geometry, joint trigger / entry-
bar invalidation / stop / floor / anti-cluster boundary at exactly
8 / sample-size / context enforcement); claim locks; downstream
gates locked; C9 edit token NOT consumed; AST/purity green.

This test minimizes chain rebuilds: all assertions read from a
SINGLE module-level `_R` record built once. Tampering tests apply a
shallow-copy + targeted mutation and validate without rebuilding."""

from __future__ import annotations

import ast
import copy

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract as c9r
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract as c9s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4

# Build the record ONCE at module import time. Each test reads from
# this shared record. Tampering tests use deepcopy + mutate + only
# call validate (no rebuild).
_R = c9r.build_candidate_9_dry_run_review()


def _tamper(field_path, new_value):
    """Return a deep copy of _R with the given dotted-or-tuple field
    path mutated to new_value. Used to drive validator-rejection
    tests without rebuilding the record."""
    d = copy.deepcopy(_R)
    if isinstance(field_path, str):
        d[field_path] = new_value
    else:
        cur = d
        for key in field_path[:-1]:
            cur = cur[key]
        cur[field_path[-1]] = new_value
    return d


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_chain_gates_all_certify():
    # the build call ran during module import; just check the
    # result.
    assert _R["verdict"] == c9r.VERDICT_C9R_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert c9r.validate_candidate_9_dry_run_review(_R)["valid"] is True


def test_full_chain_certifies():
    # cheap reads of cached results; no rebuilds happen here.
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert c9s.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)
    assert c9d.build_candidate_9_detector_spec_contract()[
        "verdict"] == c9d.VERDICT_C9D_READY
    assert c9d.run_c9_detector_dry_run()["verdict"] == (
        c9d.VERDICT_C9D_DRY_RUN_PASSED)
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


# ---- expected upstream verdicts (frozen) -----------------------------------

def test_expected_upstream_verdicts_frozen():
    assert _R["expected_detector_verdict"] == (
        "CANDIDATE_9_DETECTOR_SPEC_READY")
    assert _R["expected_dry_run_verdict"] == (
        "CANDIDATE_9_DETECTOR_DRY_RUN_PASSED")
    assert _R["expected_combined_verdict"] == (
        "CANDIDATE_9_DETECTOR_SPEC_DRY_RUN_READY")
    for field in ("expected_detector_verdict",
                  "expected_dry_run_verdict",
                  "expected_combined_verdict"):
        bad = _tamper(field, "CANDIDATE_9_FOO")
        assert c9r.validate_candidate_9_dry_run_review(
            bad)["valid"] is False, field


# ---- frozen per-fixture counts ---------------------------------------------

def test_expected_fixture_counts_complete():
    counts = _R["expected_fixture_counts"]
    for name in ("happy_path_joint_trigger", "insufficient_history",
                 "equality_at_z_threshold",
                 "equality_at_volume_median",
                 "z_only_no_volume", "volume_only_no_z",
                 "entry_bar_invalidation",
                 "geometry_floor_all_variants_fail",
                 "anti_cluster", "sample_size_adequacy",
                 "context_enforcement"):
        assert name in counts, name


def test_happy_path_counts():
    fx = _R["expected_fixture_counts"]["happy_path_joint_trigger"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 1
    assert fx["first_accepted_floor_pass"] == {
        "2r": True, "3r": True, "4r": True}


def test_zero_attempt_fixtures():
    fc = _R["expected_fixture_counts"]
    assert fc["insufficient_history"]["attempts"] == 0
    assert fc["equality_at_z_threshold"]["attempts"] == 0
    assert fc["equality_at_volume_median"]["attempts"] == 0
    assert fc["z_only_no_volume"]["attempts"] == 0
    assert fc["volume_only_no_z"]["attempts"] == 0


def test_rejection_fixtures():
    fc = _R["expected_fixture_counts"]
    inv = fc["entry_bar_invalidation"]
    assert inv["attempts"] == 1
    assert inv["accepted"] == 0
    assert inv["rejected_entry_invalidation"] == 1
    floor = fc["geometry_floor_all_variants_fail"]
    assert floor["attempts"] == 1
    assert floor["accepted"] == 0
    assert floor["rejected_geometry_floor"] == 1
    assert floor["floor_pass_by_variant"] == {
        "2r": False, "3r": False, "4r": False}


def test_anti_cluster_fixture_kept_dropped_ids():
    ac = _R["expected_fixture_counts"]["anti_cluster"]
    assert ac["anti_cluster_min_bar_gap"] == 8
    assert ac["anti_cluster_does_not_consume_edit_token"] is True
    assert "synthetic_b_inside" in ac["dropped_ids"]
    assert "synthetic_c_outside" in ac["kept_ids"]


def test_sample_size_fixture():
    sa = _R["expected_fixture_counts"]["sample_size_adequacy"]
    assert sa["below_minimum_at_dry_run"] is True
    assert sa["at_threshold_below_flag"] is False
    assert sa["enforced_at_labels_review_gate_only"] is True
    assert sa["does_not_consume_edit_token"] is True


def test_context_enforcement_fixture():
    ce = _R["expected_fixture_counts"]["context_enforcement"]
    assert ce == {"symbol_eth": True, "timeframe_1h": True,
                  "direction_short": True, "non_list_bars": True}


def test_tampering_with_fixture_counts_rejects():
    bad = copy.deepcopy(_R)
    bad["expected_fixture_counts"] = {}
    assert c9r.validate_candidate_9_dry_run_review(
        bad)["valid"] is False


# ---- frozen single accepted setup ------------------------------------------

def test_accepted_setup_frozen_with_exact_numerics():
    a = _R["expected_accepted_setup"]
    assert a["symbol"] == "BTCUSD"
    assert a["timeframe"] == "15m"
    assert a["direction"] == "long_only"
    assert a["trigger_index"] == 100
    assert a["entry_index"] == 101
    assert a["trigger_close"] == 49100.0
    assert a["trigger_low"] == 49000.0
    assert a["trigger_volume"] == 50.0
    assert a["rolling_median_volume"] == 100.0
    assert a["trigger_log_return"] == -0.019163471
    assert a["downside_z_threshold_value"] == -0.002009494
    assert a["entry_price"] == 49200.0
    assert a["stop_distance"] == 225.214286
    assert a["target_2r"] == 49650.428571
    assert a["target_distance_bps_2r"] == 91.550523
    assert a["z_condition_passes"] is True
    assert a["volume_condition_passes"] is True
    assert a["joint_trigger_passes"] is True
    assert a["entry_bar_close_strictly_above_trigger_low"] is True
    assert a["stop_below_entry"] is True
    assert a["stop_below_trigger_low"] is True
    assert a["status"] == "accepted_for_replay_review"
    assert a["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}


def test_tampering_with_accepted_setup_rejects():
    bad = copy.deepcopy(_R)
    bad["expected_accepted_setup"] = {}
    assert c9r.validate_candidate_9_dry_run_review(
        bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["expected_accepted_setup"]["entry_price"] = 99999.0
    assert c9r.validate_candidate_9_dry_run_review(
        bad2)["valid"] is False


# ---- frozen behavioural facts ---------------------------------------------

def test_expected_joint_trigger_fact():
    j = _R["expected_joint_trigger_fact"]
    assert j["rule"] == (
        "joint_z_score_AND_below_median_volume_on_same_bar")
    assert j["z_strict_inequality_below_mean_minus_2_sigma"] is True
    assert j["volume_strict_inequality_below_rolling_median"] is True
    assert j["equality_at_z_threshold_rejects"] is True
    assert j["equality_at_volume_median_rejects"] is True
    assert j["z_only_no_volume_rejects"] is True
    assert j["volume_only_no_z_rejects"] is True


def test_expected_entry_rule_fact():
    e = _R["expected_entry_rule_fact"]
    assert e["entry_price"] == (
        "close_of_next_completed_15m_bar_after_trigger_bar")
    assert e["no_intrabar_entry"] is True
    assert e["no_same_bar_entry"] is True
    assert e[
        "invalidate_if_entry_bar_close_at_or_below_trigger_bar_low"
    ] is True
    assert e["rejection_status_on_invalidation"] == (
        "rejected_entry_bar_close_at_or_below_trigger_bar_low")


def test_expected_stop_fact():
    s = _R["expected_stop_fact"]
    assert s["structure_stop_buffer_atr_multiplier"] == 0.20
    assert s["stop_must_be_below_entry_and_below_trigger_low"] is (
        True)
    assert s["stop_never_tightened_after_entry"] is True
    happy = s["happy_path_trigger_low_49000_atr_126_071429"]
    assert happy["stop_below_entry"] is True
    assert happy["stop_below_trigger_low"] is True
    assert happy["valid"] is True
    assert abs(happy["stop_buffer_price"] - 25.214286) < 1e-5
    assert abs(happy["stop_price"] - 48974.785714) < 1e-5


def test_expected_floor_fact_27_and_81_with_boundary():
    f = _R["expected_floor_fact"]
    assert f["fee_round_trip_bps"] == 27.0
    assert f["target_distance_floor_bps"] == 81.0
    assert f[
        "tiny_stop_distance_50_at_entry_50000_all_variants_fail"
    ] == {"2r": False, "3r": False, "4r": False}
    assert f[
        "stop_distance_250_at_entry_50000_all_variants_pass"
    ] == {"2r": True, "3r": True, "4r": True}
    assert f[
        "stop_distance_200_at_entry_50000_boundary_2r_fails_others"
        "_pass"] == {"2r": False, "3r": True, "4r": True}


def test_expected_anti_cluster_facts():
    a = _R["expected_anti_cluster"]
    assert a["anti_cluster_min_bar_gap"] == 8
    assert a["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert a["anti_cluster_does_not_consume_edit_token"] is True
    assert a["boundary_at_8_is_kept"] is True
    assert a["gap_of_7_is_dropped"] is True


def test_expected_sample_size_facts():
    s = _R["expected_sample_size"]
    assert s["threshold_min_accepted_at_labels_review_gate"] == 20
    assert s["count_3_is_below_threshold"] is True
    assert s["count_20_is_not_below_threshold"] is True
    assert s["enforced_at_labels_review_gate_only"] is True
    assert s["does_not_consume_edit_token"] is True


def test_expected_universe_enforcement():
    u = _R["expected_universe_enforcement"]
    assert u["universe"] == ["BTCUSD"]
    assert u["timeframe"] == "15m"
    assert u["direction"] == "long_only"
    assert u["non_btcusd_raises_valueerror"] is True
    assert u["non_15m_raises_valueerror"] is True
    assert u["non_long_only_raises_valueerror"] is True
    assert u["non_list_bars_raises_valueerror"] is True


def test_expected_insufficient_history_fact():
    h = _R["expected_insufficient_history_fact"]
    assert h["rolling_window_bars"] == 96
    assert h["min_evaluable_trigger_bar_index"] == 97
    assert h["scanner_skips_below_lookback"] is True
    assert h["warmup_50_attempts"] == 0


# ---- edit-token state ----------------------------------------------------

def test_c9_edit_token_state_preserved_unconsumed():
    e = _R["expected_edit_token_state"]
    assert e["c9_edit_token_consumed_by_this_review"] is False
    assert e[
        "anti_cluster_gap_remains_proposal_level_locked_not_edit"
        "_token"] is True
    assert e[
        "sample_size_threshold_remains_proposal_level_locked_not"
        "_edit_token"] is True
    assert e[
        "explicit_edge_argument_field_remains_proposal_level_locked"
        "_not_edit_token"] is True
    assert e[
        "edit_token_eligible_parameters_unchanged_from_spec_review"
    ] is True
    assert _R["c9_edit_token_consumed_by_this_review"] is False
    bad = copy.deepcopy(_R)
    bad["c9_edit_token_consumed_by_this_review"] = True
    assert c9r.validate_candidate_9_dry_run_review(
        bad)["valid"] is False


# ---- claim locks ---------------------------------------------------------

def test_claim_locks_present():
    locks = _R["claim_locks"]
    for required in (
            "no_real_candle_detection_authorized_by_this_gate",
            "no_labels_authorized_by_this_gate",
            "no_replay_authorized_by_this_gate",
            "no_relabel_authorized_by_this_gate",
            "no_paper_approval", "no_live_approval",
            "no_execution_approval", "no_winner_wording",
            "no_profitability_claim",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked",
            "explicit_edge_argument_field_remains_proposal_level"
            "_locked",
            "c9_edit_token_not_consumed_by_this_gate"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c9r.validate_candidate_9_dry_run_review(
        bad)["valid"] is False


# ---- review-only safety / capability flags --------------------------------

def test_review_only_with_all_downstream_locked():
    assert _R["is_review_only"] is True
    assert _R["current_loop_stage"] == "detector_and_label_review"
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    # spot-check just a few capability flags (full list is enforced
    # at validate time)
    for key in ("runs_real_candle_detection", "labels_now",
                "runs_replay", "fetches_data", "calls_api",
                "uses_network", "auto_pushes", "claims_profitability"):
        assert _R[key] is False, key
    # exhaustive tampering: each capability flag flipped to True
    # must invalidate (one full validator call per flag is cheap)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_real_detection_now", "runs_replay",
                "runs_replay_now", "runs_relabel", "scores_now",
                "stages_data_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now", "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now", "unlocks_labels_now",
                "unlocks_replay_now", "unlocks_relabel_now",
                "claims_profitability"):
        bad = _tamper(key, True)
        assert c9r.validate_candidate_9_dry_run_review(
            bad)["valid"] is False, key


def test_next_required_action_and_label():
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_9_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c9r.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9r.get_candidate_9_dry_run_review_label() == c9r.C9R_LABEL
    assert c9r.C9R_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "SYNTHETIC OUTCOMES ONLY",
                   "NOT A PROFITABILITY CLAIM",
                   "NOT A RESCUE"):
        assert phrase in c9r.C9R_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9r.C9R_LABEL.upper(), (
            banned_phrase)


def test_frozen_review_findings_complete():
    findings = _R["frozen_review_findings"]
    joined = " || ".join(findings)
    assert "exactly one accepted setup" in joined
    assert "trigger close 49100.0" in joined
    assert "ATR(14) at trigger 126.071429" in joined
    assert "stop distance 225.214286" in joined
    assert "strict-below z threshold rejects equality" in joined
    assert "strict-below median volume rejects equality" in joined
    assert "z-only condition" in joined
    assert "volume-only condition" in joined
    assert "BOTH conditions on the SAME completed 15m bar" in joined
    assert "entry-bar invalidation fires" in joined
    assert "81 bps floor per variant" in joined
    assert "anti-cluster gap of 8" in joined
    assert ("anti-cluster gap remains proposal-level locked and "
            "does NOT consume") in joined
    assert ("sample-size adequacy threshold of 20 is proposal/spec-"
            "level locked") in joined
    assert ("explicit-edge-argument field is proposal/spec-level "
            "locked") in joined
    assert "zero dry-run failures" in joined


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9r.__file__, encoding="utf-8").read()
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
