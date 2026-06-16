"""Tests for the Candidate #10 dry-run review / evidence-freeze
contract (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the 9-record rejection ledger + C10 family
proposal + C10 spec review + C10 detector spec/dry-run + V5 + V4 +
V3 + V2 + REC + AP; live recomputation matches every frozen fact (9
fixture summaries, the single accepted setup's exact daily-bar
geometry, the data-determined favorable ISO-weekday bucket, the
in-sample vs out-of-sample separation, the calendar-only trigger
purity, the stop / floor / anti-cluster boundary at exactly 5 daily
bars / sample-size minimum 100 / context enforcement); claim locks;
downstream gates locked; C10 edit token NOT consumed; AST/purity
green.

This test minimizes chain rebuilds: all assertions read from a
SINGLE module-level `_R` record built once. Tampering tests apply a
deepcopy + targeted mutation and validate without rebuilding."""

from __future__ import annotations

import ast
import copy

import sparta_commander.intraweek_calendar_seasonality_drift_v1_dry_run_review_contract as c10r

# The dominant cost of this suite is ONE full synthetic-dry-run + scan
# recompute (`_recompute_live_dry_run`, ~1.5-2h of CPU). We pay it
# EXACTLY ONCE and reuse the result everywhere:
#   * `_LIVE` holds the single live recompute.
#   * `_R` is the real, chain-gated review record. It is built while
#     the heavy recompute is temporarily redirected to return the
#     cached `_LIVE`, so the build STILL runs every upstream chain gate
#     and the real certification step -- it just does not recompute the
#     dry-run a second time.
# This removes the duplicate multi-hour rebuilds that previously made
# the full suite run >4h and never complete: the drift test now
# certifies the cached `_LIVE` directly, and the chain-certification
# test reads `_R`. No assertion or coverage is weakened.
_LIVE = c10r._recompute_live_dry_run()

_orig_recompute = c10r._recompute_live_dry_run
c10r._recompute_live_dry_run = lambda: _LIVE
try:
    _R = c10r.build_candidate_10_dry_run_review()
finally:
    c10r._recompute_live_dry_run = _orig_recompute


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
    assert _R["verdict"] == c10r.VERDICT_C10R_FROZEN
    assert _R["blockers"] == []
    assert _R["failures"] == []
    assert c10r.validate_candidate_10_dry_run_review(
        _R)["valid"] is True


def test_full_chain_certifies():
    # A FROZEN verdict with no blockers is ONLY reachable when every
    # upstream chain gate certified: the 9-record rejection ledger, the
    # C10 family proposal, the C10 spec review, the C10 detector spec,
    # the V5/V4/V3 blacklists, Overnight Autopilot V2, Recommendation
    # V1 and Autopilot Loop V1. Any broken gate short-circuits the build
    # to a BLOCKED verdict carrying a named blocker (see the ledger-
    # break test). We therefore assert on the already-built `_R` instead
    # of re-running the whole chain, which would re-pay the multi-hour
    # cost for no extra coverage.
    assert _R["verdict"] == c10r.VERDICT_C10R_FROZEN
    assert _R["blockers"] == []
    assert _R["ledger_all_rejected_kept_on_record"] is True
    assert len(_R["ledger_status_nine_records"]) == 9
    assert all(s == "REJECTED_KEPT_ON_RECORD"
               for s in _R["ledger_status_nine_records"])
    assert _R["expected_dry_run_verdict"] == (
        "CANDIDATE_10_DETECTOR_DRY_RUN_PASSED")
    assert c10r.validate_candidate_10_dry_run_review(
        _R)["valid"] is True


def test_nine_record_ledger_break_blocks():
    # Flip one rejection-record status to a non-rejected value and
    # rebuild once; the review must BLOCK. Restore in finally so the
    # shared record and other tests are unaffected.
    # The tampered build returns BLOCKED at the ledger gate BEFORE the
    # expensive recompute, so this is cheap. The finally restores the
    # global; the already-built _R proves the un-tampered FROZEN path.
    saved = c10r.C1_STATUS
    try:
        c10r.C1_STATUS = "APPROVED_FOR_TRADING"
        blocked = c10r.build_candidate_10_dry_run_review()
        assert blocked["verdict"] == c10r.VERDICT_C10R_BLOCKED
        assert "nine_record_ledger_broken" in blocked["blockers"]
        assert blocked["ledger_all_rejected_kept_on_record"] is False
    finally:
        c10r.C1_STATUS = saved
    assert c10r.C1_STATUS == saved


# ---- expected upstream verdicts (frozen) -----------------------------------

def test_expected_upstream_verdicts_frozen():
    assert _R["expected_detector_verdict"] == (
        "CANDIDATE_10_DETECTOR_SPEC_READY")
    assert _R["expected_dry_run_verdict"] == (
        "CANDIDATE_10_DETECTOR_DRY_RUN_PASSED")
    assert _R["expected_combined_verdict"] == (
        "CANDIDATE_10_DETECTOR_SPEC_DRY_RUN_READY")
    for field in ("expected_detector_verdict",
                  "expected_dry_run_verdict",
                  "expected_combined_verdict"):
        bad = _tamper(field, "CANDIDATE_10_FOO")
        assert c10r.validate_candidate_10_dry_run_review(
            bad)["valid"] is False, field


# ---- frozen per-fixture counts ---------------------------------------------

def test_expected_fixture_counts_complete():
    counts = _R["expected_fixture_counts"]
    for name in ("bucket_selection_data_determined",
                 "in_out_of_sample_separation",
                 "geometry_happy_path",
                 "geometry_floor_all_variants_fail",
                 "no_price_condition", "no_evaluation_bar",
                 "anti_cluster", "sample_size_adequacy",
                 "context_enforcement"):
        assert name in counts, name


def test_bucket_selection_fixture_counts():
    fx = _R["expected_fixture_counts"][
        "bucket_selection_data_determined"]
    assert fx["favorable_weekday_bucket"] == 3
    assert fx["cardinality"] == 1
    assert fx["cleared_81_bps_floor"] is True
    assert fx["bucket_value_is_data_determined_not_hardcoded"] is True
    assert fx["selected_on_in_sample_window_only"] is True


def test_in_out_of_sample_separation_fixture():
    fx = _R["expected_fixture_counts"]["in_out_of_sample_separation"]
    assert fx["in_sample_bucket"] == 3
    assert fx["oos_window_bucket"] == 5
    assert fx["selected_on_in_sample_window_only"] is True


def test_geometry_happy_path_counts():
    fx = _R["expected_fixture_counts"]["geometry_happy_path"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 1
    assert fx["first_accepted_index"] == 16
    assert fx["first_accepted_floor_pass"] == {
        "2r": True, "3r": True, "4r": True}


def test_geometry_floor_fixture():
    fx = _R["expected_fixture_counts"][
        "geometry_floor_all_variants_fail"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_geometry_floor"] == 1
    assert fx["floor_pass_by_variant"] == {
        "2r": False, "3r": False, "4r": False}


def test_no_price_condition_fixture():
    fx = _R["expected_fixture_counts"]["no_price_condition"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 1
    assert tuple(fx["triggered_weekdays"]) == (3,)


def test_no_evaluation_bar_fixture():
    fx = _R["expected_fixture_counts"]["no_evaluation_bar"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_no_evaluation_bar"] == 1


def test_anti_cluster_fixture_kept_dropped_ids():
    ac = _R["expected_fixture_counts"]["anti_cluster"]
    assert ac["anti_cluster_min_bar_gap"] == 5
    assert ac["anti_cluster_does_not_consume_edit_token"] is True
    assert "synthetic_b_inside" in ac["dropped_ids"]
    assert "synthetic_a" in ac["kept_ids"]
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
                  "direction_short": True, "non_list_bars": True,
                  "bucket_zero": True, "bucket_eight": True}


def test_tampering_with_fixture_counts_rejects():
    bad = copy.deepcopy(_R)
    bad["expected_fixture_counts"] = {}
    assert c10r.validate_candidate_10_dry_run_review(
        bad)["valid"] is False


# ---- frozen single accepted setup ------------------------------------------

def test_accepted_setup_frozen_with_exact_numerics():
    a = _R["expected_accepted_setup"]
    assert a["setup_id"] == "BTCUSD_2020-01-17"
    assert a["symbol"] == "BTCUSD"
    assert a["timeframe"] == "1d"
    assert a["direction"] == "long_only"
    assert a["trigger_index"] == 16
    assert a["trigger_iso_weekday"] == 3
    assert a["favorable_weekday_bucket"] == 3
    assert a["uses_no_price_condition"] is True
    assert a["uses_no_volume_condition"] is True
    assert a["uses_no_excursion_condition"] is True
    assert a["trigger_close"] == 50000.0
    assert a["atr_at_entry_bar"] == 160.0
    assert a["entry_index"] == 16
    assert a["entry_price"] == 50000.0
    assert a["entry_is_at_triggering_bar_close"] is True
    assert a["entry_is_intrabar"] is False
    assert a["exit_index"] == 21
    assert a["holding_horizon_bars"] == 5
    assert a["stop_buffer_price"] == 240.0
    assert a["stop_price"] == 49760.0
    assert a["stop_distance"] == 240.0
    assert a["stop_below_entry"] is True
    assert a["target_2r"] == 50480.0
    assert a["target_3r"] == 50720.0
    assert a["target_4r"] == 50960.0
    assert a["target_distance_bps_2r"] == 96.0
    assert a["target_distance_bps_3r"] == 144.0
    assert a["target_distance_bps_4r"] == 192.0
    assert a["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert a["status"] == "accepted_for_replay_review"


def test_tampering_with_accepted_setup_rejects():
    bad = copy.deepcopy(_R)
    bad["expected_accepted_setup"] = {}
    assert c10r.validate_candidate_10_dry_run_review(
        bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["expected_accepted_setup"]["entry_price"] = 99999.0
    assert c10r.validate_candidate_10_dry_run_review(
        bad2)["valid"] is False


# ---- frozen behavioural facts ---------------------------------------------

def test_expected_bucket_selection_fact():
    b = _R["expected_bucket_selection_fact"]
    assert b["favorable_weekday_bucket"] == 3
    assert b["cardinality"] == 1
    assert b["bucket_value_is_data_determined_not_hardcoded"] is True
    assert b["selected_on_in_sample_window_only"] is True
    assert b["only_weekday_3_clears_81_bps_floor"] is True
    mb = b["per_weekday_mean_bps"]
    assert abs(mb[3] - 99.503309) < 1e-5
    assert mb[2] == 0.0
    assert mb[1] < 0.0


def test_expected_in_out_of_sample_fact():
    f = _R["expected_in_out_of_sample_fact"]
    assert tuple(f["in_sample_window"]) == ("2019-01-01", "2022-12-31")
    assert tuple(f["out_of_sample_window"]) == (
        "2023-01-01", "2025-12-31")
    assert f["in_sample_bucket"] == 3
    assert f["oos_window_bucket"] == 5
    assert f["oos_poison_ignored_by_in_sample_selection"] is True
    assert f["bucket_selected_on_in_sample_window_only"] is True


def test_expected_calendar_trigger_fact():
    c = _R["expected_calendar_trigger_fact"]
    assert c["rule"] == (
        "single_deterministic_iso_weekday_calendar_condition")
    assert c["cardinality"] == 1
    assert c["uses_no_price_condition"] is True
    assert c["uses_no_volume_condition"] is True
    assert c["uses_no_excursion_condition"] is True
    assert c["wild_weekday_4_crash_bar_does_not_trigger"] is True
    assert c["flat_weekday_3_bar_triggers_on_calendar_alone"] is True


def test_expected_entry_rule_fact():
    e = _R["expected_entry_rule_fact"]
    assert e["entry_price"] == (
        "close_of_the_triggering_completed_daily_bar")
    assert e["entry_index_equals_trigger_index"] is True
    assert e["no_intrabar_entry"] is True
    assert e["holding_horizon_bars"] == 5
    assert e["exit_index_equals_entry_index_plus_5"] is True
    assert e["no_horizon_exit_bar_rejects_on"] == (
        "rejected_no_evaluation_bar")


def test_expected_stop_fact():
    s = _R["expected_stop_fact"]
    assert s["structure_stop_atr_multiplier"] == 1.5
    assert s["stop_must_be_below_entry"] is True
    assert s["stop_never_tightened_after_entry"] is True
    happy = s["happy_path_entry_50000_atr_160"]
    assert happy["stop_buffer_price"] == 240.0
    assert happy["stop_price"] == 49760.0
    assert happy["stop_distance"] == 240.0
    assert happy["stop_below_entry"] is True
    assert happy["valid"] is True


def test_expected_floor_fact_27_and_81_with_boundary():
    f = _R["expected_floor_fact"]
    assert f["fee_round_trip_bps"] == 27.0
    assert f["target_distance_floor_bps"] == 81.0
    assert f[
        "tiny_stop_distance_6_at_entry_50000_all_variants_fail"
    ] == {"2r": False, "3r": False, "4r": False}
    assert f[
        "stop_distance_240_at_entry_50000_all_variants_pass"
    ] == {"2r": True, "3r": True, "4r": True}
    assert f[
        "stop_distance_200_at_entry_50000_boundary_2r_fails"
        "_others_pass"] == {"2r": False, "3r": True, "4r": True}


def test_expected_anti_cluster_facts():
    a = _R["expected_anti_cluster"]
    assert a["anti_cluster_min_bar_gap"] == 5
    assert a["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert a["anti_cluster_does_not_consume_edit_token"] is True
    assert a["boundary_at_5_is_kept"] is True
    assert a["gap_of_4_is_dropped"] is True
    assert a["one_fire_per_iso_week_by_construction"] is True


def test_expected_sample_size_facts():
    s = _R["expected_sample_size"]
    assert s["threshold_min_accepted_at_labels_review_gate"] == 100
    assert s["count_3_is_below_threshold"] is True
    assert s["count_100_is_not_below_threshold"] is True
    assert s["enforced_at_labels_review_gate_only"] is True
    assert s["does_not_consume_edit_token"] is True


def test_expected_universe_enforcement():
    u = _R["expected_universe_enforcement"]
    assert tuple(u["universe"]) == ("BTCUSD",)
    assert u["timeframe"] == "1d"
    assert u["direction"] == "long_only"
    assert u["non_btcusd_raises_valueerror"] is True
    assert u["non_1d_raises_valueerror"] is True
    assert u["non_long_only_raises_valueerror"] is True
    assert u["non_list_bars_raises_valueerror"] is True
    assert u["iso_weekday_bucket_zero_raises_valueerror"] is True
    assert u["iso_weekday_bucket_eight_raises_valueerror"] is True


# ---- edit-token state ----------------------------------------------------

def test_c10_edit_token_state_preserved_unconsumed():
    e = _R["expected_edit_token_state"]
    assert e["c10_edit_token_consumed_by_this_review"] is False
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
        "single_trigger_design_remains_proposal_level_locked_not"
        "_edit_token"] is True
    assert e[
        "edit_token_eligible_parameters_unchanged_from_spec_review"
    ] is True
    assert _R["c10_edit_token_consumed_by_this_review"] is False
    bad = copy.deepcopy(_R)
    bad["c10_edit_token_consumed_by_this_review"] = True
    assert c10r.validate_candidate_10_dry_run_review(
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
            "favorable_weekday_bucket_value_is_data_determined_not"
            "_hardcoded",
            "anti_cluster_gap_remains_proposal_level_locked",
            "sample_size_threshold_remains_proposal_level_locked",
            "explicit_edge_argument_field_remains_proposal_level"
            "_locked",
            "single_trigger_design_remains_proposal_level_locked",
            "c10_edit_token_not_consumed_by_this_gate"):
        assert required in locks, required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c10r.validate_candidate_10_dry_run_review(
        bad)["valid"] is False


# ---- review-only safety / capability flags --------------------------------

def test_review_only_with_all_downstream_locked():
    assert _R["is_review_only"] is True
    assert _R["current_loop_stage"] == "detector_and_label_review"
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("runs_real_candle_detection", "labels_now",
                "runs_replay", "fetches_data", "calls_api",
                "uses_network", "auto_pushes", "claims_profitability"):
        assert _R[key] is False, key
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
        assert c10r.validate_candidate_10_dry_run_review(
            bad)["valid"] is False, key


def test_next_required_action_and_label():
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_10_REAL_CANDLE_DETECTION")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c10r.NEXT_REQUIRED_ACTION.upper(), banned
    assert c10r.get_candidate_10_dry_run_review_label() == (
        c10r.C10R_LABEL)
    assert c10r.C10R_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "SYNTHETIC OUTCOMES ONLY",
                   "NOT A PROFITABILITY CLAIM",
                   "NOT A RESCUE"):
        assert phrase in c10r.C10R_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c10r.C10R_LABEL.upper(), (
            banned_phrase)


def test_frozen_review_findings_complete():
    findings = _R["frozen_review_findings"]
    joined = " || ".join(findings)
    assert "DATA-DETERMINED" in joined
    assert "weekday 3 is the unique winner at +99.5 bps" in joined
    assert "crown weekday 5" in joined
    assert ("a wild weekday-4 crash bar does NOT trigger while a "
            "flat weekday-3 bar does") in joined
    assert "exactly one accepted setup" in joined
    assert ("ATR(14) 160.0, stop distance 240.0, targets "
            "50480/50720/50960") in joined
    assert "target-distance bps 96/144/192" in joined
    assert "rejected_no_evaluation_bar" in joined
    assert "anti-cluster gap of 5 daily bars keeps boundary" in joined
    assert ("anti-cluster gap remains proposal-level locked and "
            "does NOT") in joined
    assert ("sample-size adequacy threshold of 100 is proposal/spec-"
            "level locked") in joined
    assert "zero dry-run failures" in joined


# ---- self-rejection on detector drift -------------------------------------

def test_review_rejects_itself_if_dry_run_drifts():
    # Drift/tamper rejection is proved against the already-built live
    # recomputation (_LIVE) instead of recomputing the whole heavy
    # dry-run chain again. _certify_recomputed is the SAME pure gate the
    # production build() calls at line 787, so certifying the cached
    # _LIVE here exercises the identical rejection path without a second
    # multi-hour rebuild.
    # Baseline: the untampered live certifies clean and the built record
    # is FROZEN with no failures.
    assert c10r._certify_recomputed(_LIVE) == []
    assert _R["verdict"] == c10r.VERDICT_C10R_FROZEN
    assert _R["failures"] == []
    # Tamper a frozen expectation and confirm certification flips to a
    # non-empty failure list naming the drifted field.
    saved = c10r.EXPECTED_ACCEPTED_SETUP
    try:
        tampered = dict(saved)
        tampered["entry_price"] = 12345.0
        c10r.EXPECTED_ACCEPTED_SETUP = tampered
        failures = c10r._certify_recomputed(_LIVE)
        assert failures
        assert any("accepted_field_mismatch" in f for f in failures)
    finally:
        c10r.EXPECTED_ACCEPTED_SETUP = saved
    assert c10r.EXPECTED_ACCEPTED_SETUP is saved
    # Restoring the frozen expectation certifies clean again.
    assert c10r._certify_recomputed(_LIVE) == []


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c10r.__file__, encoding="utf-8").read()
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
