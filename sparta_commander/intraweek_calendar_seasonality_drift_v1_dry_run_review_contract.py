"""SPARTA CANDIDATE #10 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, NOT A PROFITABILITY CLAIM):
INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1.

Freezes the synthetic-fixture dry-run outcomes of the pushed
Candidate #10 detector spec. The dry run is pure, deterministic and
reads NO files, so this review certifies by RE-COMPUTING every frozen
fact live from the pushed detector module -- the per-fixture attempt
and acceptance counts, the data-determined favorable ISO-weekday
bucket selection (weekday 3 the unique in-sample winner clearing the
81 bps floor), the in-sample vs out-of-sample separation (the OOS
poison would crown weekday 5 but is ignored), the calendar-only
trigger purity (no price / volume / excursion condition), the single
accepted setup's exact geometry (ATR, entry at the triggering bar
close, stop, targets, floor bps), the geometry-floor rejection, the
no-evaluation-bar rejection, the anti-cluster filter behaviour
including the kept/dropped IDs and the boundary at exactly 5 daily
bars, the sample-size adequacy behaviour at the 100 minimum, and the
context enforcement (BTCUSD / 1d / long_only + non-list bars + off-ISO
bucket raises). If any future change makes the pushed scanner,
selector or fixtures behave differently, this review flips to REJECTED
on its own.

Synthetic fixtures only. No real candle has been touched for
Candidate #10, no staged data read, no aggregation executed, no
labels, no replay, no artifacts, and this module performs none. This
gate authorizes NO real detection: the real-candle gate becomes
reachable only after this review is committed and pushed, and opens
only on its own explicit human command. Nothing here is a
profitability claim.

Chain-gated live on: the pushed nine-record rejection ledger (C1-C9),
the pushed V5 + V4 + V3 rejected-family blacklists, the pushed
Overnight Research Autopilot V2, the pushed Recommendation V1, the
pushed Autopilot Loop V1, the pushed Candidate #10 family proposal,
the pushed Candidate #10 spec review, and the pushed Candidate #10
detector spec + synthetic-fixture dry-run path.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract import (
    VERDICT_C10D_DRY_RUN_PASSED,
    VERDICT_C10D_READY,
    build_candidate_10_detector_spec_contract,
    run_c10_detector_dry_run,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C10P_READY,
    build_candidate_10_family_proposal,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract import (
    VERDICT_C10S_READY,
    build_candidate_10_spec_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C9_STATUS,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract import (
    VERDICT_BL5_READY,
    build_rejected_family_blacklist_v5,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C10R_SCHEMA_VERSION = (
    "intraweek_calendar_seasonality_drift_v1_dry_run_review.v1")
C10R_LABEL = ("SPARTA Candidate #10 Dry-Run Review / Evidence Freeze "
              "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
              "NOT A PROFITABILITY CLAIM, NOT A RESCUE)")
C10R_MODE = "RESEARCH_ONLY"
VERDICT_C10R_FROZEN = "CANDIDATE_10_DRY_RUN_REVIEW_FROZEN"
VERDICT_C10R_REJECTED = "CANDIDATE_10_DRY_RUN_REVIEW_REJECTED"
VERDICT_C10R_BLOCKED = "CANDIDATE_10_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_10_REAL_CANDLE_DETECTION")
CURRENT_LOOP_STAGE = "detector_and_label_review"

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_10_DETECTOR_SPEC_READY"
EXPECTED_DRY_RUN_VERDICT = "CANDIDATE_10_DETECTOR_DRY_RUN_PASSED"
EXPECTED_COMBINED_VERDICT = (
    "CANDIDATE_10_DETECTOR_SPEC_DRY_RUN_READY")

# ---- frozen fixture-level counts from the pushed dry-run output ----------

EXPECTED_FIXTURE_COUNTS = {
    "bucket_selection_data_determined":
        {"favorable_weekday_bucket": 3, "cardinality": 1,
         "cleared_81_bps_floor": True,
         "bucket_value_is_data_determined_not_hardcoded": True,
         "selected_on_in_sample_window_only": True},
    "in_out_of_sample_separation":
        {"in_sample_bucket": 3, "oos_window_bucket": 5,
         "selected_on_in_sample_window_only": True},
    "geometry_happy_path":
        {"attempts": 1, "accepted": 1, "first_accepted_index": 16,
         "first_accepted_floor_pass":
             {"2r": True, "3r": True, "4r": True}},
    "geometry_floor_all_variants_fail":
        {"attempts": 1, "accepted": 0,
         "rejected_geometry_floor": 1,
         "floor_pass_by_variant":
             {"2r": False, "3r": False, "4r": False}},
    "no_price_condition":
        {"attempts": 1, "accepted": 1,
         "triggered_weekdays": (3,)},
    "no_evaluation_bar":
        {"attempts": 1, "accepted": 0,
         "rejected_no_evaluation_bar": 1},
    "anti_cluster":
        {"kept_ids": ("synthetic_a", "synthetic_c_outside"),
         "dropped_ids": ("synthetic_b_inside",),
         "anti_cluster_min_bar_gap": 5,
         "anti_cluster_does_not_consume_edit_token": True},
    "sample_size_adequacy":
        {"below_minimum_at_dry_run": True,
         "at_threshold_below_flag": False,
         "enforced_at_labels_review_gate_only": True,
         "does_not_consume_edit_token": True},
    "context_enforcement":
        {"symbol_eth": True, "timeframe_1h": True,
         "direction_short": True, "non_list_bars": True,
         "bucket_zero": True, "bucket_eight": True},
}


# ---- frozen single accepted setup (geometry happy path) ------------------

EXPECTED_ACCEPTED_SETUP = {
    "setup_id": "BTCUSD_2020-01-17",
    "symbol": "BTCUSD",
    "timeframe": "1d",
    "direction": "long_only",
    "trigger_index": 16,
    "trigger_date": "2020-01-17",
    "trigger_time": "2020-01-17T00:00:00Z",
    "trigger_iso_weekday": 3,
    "favorable_weekday_bucket": 3,
    "calendar_condition_passes": True,
    "uses_no_price_condition": True,
    "uses_no_volume_condition": True,
    "uses_no_excursion_condition": True,
    "trigger_close": 50000.0,
    "trigger_high": 50080.0,
    "trigger_low": 49920.0,
    "atr_at_entry_bar": 160.0,
    "entry_index": 16,
    "entry_date": "2020-01-17",
    "entry_time": "2020-01-17T00:00:00Z",
    "entry_price": 50000.0,
    "entry_is_at_triggering_bar_close": True,
    "entry_is_intrabar": False,
    "exit_index": 21,
    "exit_date": "2020-01-22",
    "exit_time": "2020-01-22T00:00:00Z",
    "holding_horizon_bars": 5,
    "stop_buffer_price": 240.0,
    "stop_price": 49760.0,
    "stop_distance": 240.0,
    "stop_below_entry": True,
    "target_2r": 50480.0,
    "target_3r": 50720.0,
    "target_4r": 50960.0,
    "target_distance_bps_2r": 96.0,
    "target_distance_bps_3r": 144.0,
    "target_distance_bps_4r": 192.0,
    "geometry_floor_pass_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "accepted_for_labeling_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "replay_start_time": "2020-01-18",
    "status": "accepted_for_replay_review",
}


# ---- frozen behavioural facts independent of fixtures --------------------

EXPECTED_BUCKET_SELECTION_FACT = {
    "favorable_weekday_bucket": 3,
    "cardinality": 1,
    "bucket_value_is_data_determined_not_hardcoded": True,
    "selected_on_in_sample_window_only": True,
    "per_weekday_mean_bps":
        {1: -79.523282, 2: 0.0, 3: 99.503309, 4: 0.0,
         5: -19.980027, 6: 0.0, 7: 0.0},
    "only_weekday_3_clears_81_bps_floor": True,
    "selection_metric":
        "highest_in_sample_mean_fixed_horizon_forward_log_return_among"
        "_iso_weekdays_that_clears_the_81_bps_gross_floor",
}

EXPECTED_IN_OUT_OF_SAMPLE_FACT = {
    "in_sample_window": ("2019-01-01", "2022-12-31"),
    "out_of_sample_window": ("2023-01-01", "2025-12-31"),
    "in_sample_bucket": 3,
    "oos_window_bucket": 5,
    "oos_poison_ignored_by_in_sample_selection": True,
    "bucket_selected_on_in_sample_window_only": True,
}

EXPECTED_CALENDAR_TRIGGER_FACT = {
    "rule": "single_deterministic_iso_weekday_calendar_condition",
    "cardinality": 1,
    "uses_no_price_condition": True,
    "uses_no_volume_condition": True,
    "uses_no_excursion_condition": True,
    "wild_weekday_4_crash_bar_does_not_trigger": True,
    "flat_weekday_3_bar_triggers_on_calendar_alone": True,
}

EXPECTED_ENTRY_RULE_FACT = {
    "entry_price": "close_of_the_triggering_completed_daily_bar",
    "entry_index_equals_trigger_index": True,
    "no_intrabar_entry": True,
    "holding_horizon_bars": 5,
    "exit_index_equals_entry_index_plus_5": True,
    "no_horizon_exit_bar_rejects_on":
        "rejected_no_evaluation_bar",
}

EXPECTED_STOP_FACT = {
    "structure_stop_atr_multiplier": 1.5,
    "stop_price_formula":
        "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
        "ATR14_at_entry_bar",
    "stop_must_be_below_entry": True,
    "stop_never_tightened_after_entry": True,
    "happy_path_entry_50000_atr_160":
        {"stop_buffer_price": 240.0,
         "stop_price": 49760.0,
         "stop_distance": 240.0,
         "stop_below_entry": True,
         "valid": True},
}

EXPECTED_FLOOR_FACT = {
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "tiny_stop_distance_6_at_entry_50000_all_variants_fail":
        {"2r": False, "3r": False, "4r": False},
    "stop_distance_240_at_entry_50000_all_variants_pass":
        {"2r": True, "3r": True, "4r": True},
    "stop_distance_200_at_entry_50000_boundary_2r_fails_others_pass":
        {"2r": False, "3r": True, "4r": True},
}

EXPECTED_ANTI_CLUSTER = {
    "anti_cluster_min_bar_gap": 5,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    "kept_ids_in_dry_run":
        ("synthetic_a", "synthetic_c_outside"),
    "dropped_ids_in_dry_run": ("synthetic_b_inside",),
    "boundary_at_5_is_kept": True,
    "gap_of_4_is_dropped": True,
    "one_fire_per_iso_week_by_construction": True,
}

EXPECTED_SAMPLE_SIZE = {
    "threshold_min_accepted_at_labels_review_gate": 100,
    "count_3_is_below_threshold": True,
    "count_100_is_not_below_threshold": True,
    "enforced_at_labels_review_gate_only": True,
    "does_not_consume_edit_token": True,
}

EXPECTED_UNIVERSE_ENFORCEMENT = {
    "universe": ("BTCUSD",),
    "timeframe": "1d",
    "direction": "long_only",
    "non_btcusd_raises_valueerror": True,
    "non_1d_raises_valueerror": True,
    "non_long_only_raises_valueerror": True,
    "non_list_bars_raises_valueerror": True,
    "iso_weekday_bucket_zero_raises_valueerror": True,
    "iso_weekday_bucket_eight_raises_valueerror": True,
}

EXPECTED_EDIT_TOKEN_STATE = {
    "c10_edit_token_consumed_by_this_review": False,
    "anti_cluster_gap_remains_proposal_level_locked_not_edit_token":
        True,
    "sample_size_threshold_remains_proposal_level_locked_not_edit"
    "_token": True,
    "explicit_edge_argument_field_remains_proposal_level_locked_not"
    "_edit_token": True,
    "single_trigger_design_remains_proposal_level_locked_not_edit"
    "_token": True,
    "edit_token_eligible_parameters_unchanged_from_spec_review":
        True,
}

FROZEN_REVIEW_FINDINGS = (
    "the favorable ISO-weekday bucket is DATA-DETERMINED on the "
    "in-sample window: weekday 3 is the unique winner at +99.5 bps "
    "mean fixed-horizon forward log return and the only weekday that "
    "clears the 81 bps gross floor; the value is not hard-coded",
    "in-sample and out-of-sample are separated: the OOS poison bars "
    "would crown weekday 5 if wrongly included, but the in-sample "
    "selection ignores them and stays at weekday 3",
    "the trigger is a single deterministic calendar condition; no "
    "price, volume or statistical-excursion condition participates; "
    "a wild weekday-4 crash bar does NOT trigger while a flat "
    "weekday-3 bar does",
    "the valid calendar fixture produces exactly one accepted setup "
    "with floor pass at 2r/3r/4r",
    "the accepted setup enters at the triggering daily bar close "
    "(entry_index == trigger_index, no intrabar), holds 5 bars, has "
    "ATR(14) 160.0, stop distance 240.0, targets 50480/50720/50960 "
    "and target-distance bps 96/144/192",
    "the structure-stop formula uses entry_price - 1.5 x ATR14 with "
    "a positive distance and a stop strictly below entry",
    "the 81 bps floor per variant is enforced at label time; a tiny "
    "stop distance fails all variants and the 200-distance boundary "
    "fails 2r and passes 3r/4r",
    "a calendar trigger with ATR available but no horizon-exit bar "
    "rejects on rejected_no_evaluation_bar",
    "btcusd / 1d / long_only universe is enforced by valueerror on "
    "non-btcusd / non-1d / non-long-only / non-list bars, and an "
    "ISO-weekday bucket outside 1..7 also raises",
    "anti-cluster gap of 5 daily bars keeps boundary events and "
    "drops events with gap < 5; one-fire-per-ISO-week is the primary "
    "anti-cluster constraint",
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the single c10 edit token",
    "sample-size adequacy threshold of 100 is proposal/spec-level "
    "locked, applies at the labels-review gate only, and does NOT "
    "consume the single c10 edit token",
    "explicit-edge-argument field and the single-trigger design are "
    "proposal/spec-level locked and do NOT consume the single c10 "
    "edit token",
    "zero dry-run failures",
)

CLAIM_LOCKS = (
    "no_real_candle_detection_authorized_by_this_gate",
    "no_labels_authorized_by_this_gate",
    "no_replay_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_profitability_claim",
    "favorable_weekday_bucket_value_is_data_determined_not_hardcoded",
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
    "explicit_edge_argument_field_remains_proposal_level_locked",
    "single_trigger_design_remains_proposal_level_locked",
    "c10_edit_token_not_consumed_by_this_gate",
)


def get_candidate_10_dry_run_review_label() -> str:
    return C10R_LABEL


# ---- re-compute the live dry-run facts -----------------------------------

def _recompute_live_dry_run() -> dict[str, Any]:
    """Re-run the pushed dry run and the supporting fixture-level scans
    / selector / primitives live. Pure; in-memory only."""
    import sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract as _det
    dry = run_c10_detector_dry_run()
    bars_valid = _det.fixture_geometry_happy_path()
    accepted_valid = [s for s in _det.scan_c10_setups(
        bars_valid, 3, "BTCUSD")
        if s["status"] == "accepted_for_replay_review"]
    # data-determined selection (in-sample) and OOS-window selection
    bars_sel = _det.fixture_bucket_selection_data_determined()
    sel_in = _det.select_favorable_weekday_bucket(bars_sel)
    sel_oos = _det.select_favorable_weekday_bucket(
        bars_sel, in_sample_window=_det.OUT_OF_SAMPLE_WINDOW)
    # no-price-condition: only weekday 3 triggers
    bars_np = _det.fixture_no_price_condition()
    setups_np = _det.scan_c10_setups(bars_np, 3, "BTCUSD")
    triggered_weekdays_np = sorted(
        set(s["trigger_iso_weekday"] for s in setups_np))
    # no-evaluation-bar: 18 flat bars
    bars_noeval = [_det._flat_bar(2020, i, 50000.0, 80.0)
                   for i in range(18)]
    setups_noeval = _det.scan_c10_setups(bars_noeval, 3, "BTCUSD")
    noeval_rejected = [
        s for s in setups_noeval
        if s["status"] == "rejected_no_evaluation_bar"]
    noeval_accepted = [
        s for s in setups_noeval
        if s["status"] == "accepted_for_replay_review"]
    # universe / bucket enforcement
    def _raises(fn) -> bool:
        try:
            fn()
            return False
        except ValueError:
            return True
    btcusd_only_raises = _raises(
        lambda: _det.scan_c10_setups(bars_valid, 3, "ETHUSD"))
    non_1d_raises = _raises(
        lambda: _det.scan_c10_setups(bars_valid, 3, "BTCUSD",
                                     timeframe="1h"))
    non_long_only_raises = _raises(
        lambda: _det.scan_c10_setups(bars_valid, 3, "BTCUSD",
                                     direction="short_only"))
    non_list_raises = _raises(
        lambda: _det.scan_c10_setups("not a list", 3, "BTCUSD"))
    bucket_zero_raises = _raises(
        lambda: _det.scan_c10_setups(bars_valid, 0, "BTCUSD"))
    bucket_eight_raises = _raises(
        lambda: _det.scan_c10_setups(bars_valid, 8, "BTCUSD"))
    # stop call from the happy-path geometry (entry 50000, ATR 160)
    stop_happy = _det.compute_stop(50000.0, 160.0)
    # floor independent calls
    floor_tiny = _det.geometry_floor_by_variant(50000.0, 6.0)
    floor_big = _det.geometry_floor_by_variant(50000.0, 240.0)
    floor_boundary = _det.geometry_floor_by_variant(50000.0, 200.0)
    # anti-cluster boundary independent calls (gap 4 dropped, gap 5 kept)
    seed_x = {"setup_id": "X", "symbol": "BTCUSD",
              "status": "accepted_for_replay_review",
              "entry_index": 200, "rejection_reasons": []}
    pair_gap_4 = _det.apply_anti_cluster_filter([
        seed_x,
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review",
         "entry_index": 204, "rejection_reasons": []}])
    pair_gap_5 = _det.apply_anti_cluster_filter([
        seed_x,
        {"setup_id": "Z", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review",
         "entry_index": 205, "rejection_reasons": []}])
    # sample-size independent calls
    sample_3 = _det.check_sample_size_adequacy(
        [{"entry_index": i} for i in range(3)])
    sample_100 = _det.check_sample_size_adequacy(
        [{"entry_index": i} for i in range(100)])
    return {
        "dry_run": dry,
        "accepted_valid_setup":
            (accepted_valid[0] if accepted_valid else None),
        "accepted_valid_count": len(accepted_valid),
        "sel_in_bucket": sel_in["favorable_weekday_bucket"],
        "sel_in_cleared": sel_in["cleared_81_bps_floor"],
        "sel_in_data_determined":
            sel_in["bucket_value_is_data_determined_not_hardcoded"],
        "sel_in_in_sample_only":
            sel_in["selected_on_in_sample_window_only"],
        "sel_in_per_weekday_mean_bps": sel_in["per_weekday_mean_bps"],
        "sel_oos_bucket": sel_oos["favorable_weekday_bucket"],
        "triggered_weekdays_np": tuple(triggered_weekdays_np),
        "noeval_rejected_count": len(noeval_rejected),
        "noeval_accepted_count": len(noeval_accepted),
        "btcusd_only_raises": btcusd_only_raises,
        "non_1d_raises": non_1d_raises,
        "non_long_only_raises": non_long_only_raises,
        "non_list_raises": non_list_raises,
        "bucket_zero_raises": bucket_zero_raises,
        "bucket_eight_raises": bucket_eight_raises,
        "stop_happy": stop_happy,
        "floor_tiny": floor_tiny,
        "floor_big": floor_big,
        "floor_boundary": floor_boundary,
        "gap_4_pair_kept_ids": tuple(s["setup_id"] for s
                                     in pair_gap_4["kept"]),
        "gap_4_pair_dropped_ids": tuple(s["setup_id"] for s
                                        in pair_gap_4["dropped"]),
        "gap_5_pair_kept_ids": tuple(s["setup_id"] for s
                                     in pair_gap_5["kept"]),
        "gap_5_pair_dropped_ids": tuple(s["setup_id"] for s
                                        in pair_gap_5["dropped"]),
        "sample_3": sample_3,
        "sample_100": sample_100,
    }


def _almost_equal(a: float, b: float, tol: float = 1e-5) -> bool:
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def _certify_recomputed(live: dict[str, Any]) -> list[str]:
    """Pure certification of the recomputed live facts against the
    frozen expectations. Returns the list of failures."""
    failures: list[str] = []
    dry = live["dry_run"]
    if dry["verdict"] != EXPECTED_DRY_RUN_VERDICT:
        failures.append("dry_run_verdict_mismatch:" + str(
            dry.get("verdict")))
    if dry["failures"]:
        failures.append("dry_run_has_failures:" + str(
            dry["failures"]))
    if dry["uses_synthetic_fixtures_only"] is not True \
            or dry["reads_real_candles"] is not False \
            or dry["reads_staged_data"] is not False \
            or dry["reads_any_files"] is not False:
        failures.append("dry_run_purity_broken")
    fixtures = dry.get("fixtures") or {}
    for name, want in EXPECTED_FIXTURE_COUNTS.items():
        got = fixtures.get(name) or {}
        for key, value in want.items():
            if key in ("kept_ids", "dropped_ids",
                       "triggered_weekdays"):
                if tuple(got.get(key) or ()) != tuple(value):
                    failures.append(
                        "fixture_tuple_mismatch:%s:%s" % (name, key))
            elif got.get(key) != value:
                failures.append(
                    "fixture_count_mismatch:%s:%s" % (name, key))
    accepted = live.get("accepted_valid_setup") or {}
    if live.get("accepted_valid_count") != 1:
        failures.append("accepted_valid_count_not_1")
    for key, want in EXPECTED_ACCEPTED_SETUP.items():
        got = accepted.get(key)
        if isinstance(want, float):
            if not _almost_equal(got, want):
                failures.append("accepted_field_mismatch:" + key)
        elif got != want:
            failures.append("accepted_field_mismatch:" + key)
    # data-determined selection
    if live.get("sel_in_bucket") != 3:
        failures.append("in_sample_bucket_not_3")
    if live.get("sel_in_cleared") is not True:
        failures.append("in_sample_bucket_did_not_clear_floor")
    if live.get("sel_in_data_determined") is not True:
        failures.append("bucket_value_not_data_determined")
    if live.get("sel_in_in_sample_only") is not True:
        failures.append("bucket_not_selected_in_sample_only")
    cleared = [w for w, bps
               in (live.get("sel_in_per_weekday_mean_bps") or {}).items()
               if bps >= 81.0]
    if cleared != [3]:
        failures.append("only_weekday_3_should_clear_floor")
    if live.get("sel_oos_bucket") == 3:
        failures.append(
            "oos_window_selection_must_differ_from_in_sample")
    # calendar-only trigger purity
    if live.get("triggered_weekdays_np") != (3,):
        failures.append("no_price_condition_only_weekday_3_triggers")
    # no-evaluation-bar
    if live.get("noeval_rejected_count") != 1:
        failures.append("no_evaluation_bar_expected_1_rejection")
    if live.get("noeval_accepted_count") != 0:
        failures.append("no_evaluation_bar_should_not_accept")
    # universe + bucket enforcement
    if live.get("btcusd_only_raises") is not True:
        failures.append("non_btcusd_did_not_raise")
    if live.get("non_1d_raises") is not True:
        failures.append("non_1d_did_not_raise")
    if live.get("non_long_only_raises") is not True:
        failures.append("non_long_only_did_not_raise")
    if live.get("non_list_raises") is not True:
        failures.append("non_list_bars_did_not_raise")
    if live.get("bucket_zero_raises") is not True:
        failures.append("bucket_zero_did_not_raise")
    if live.get("bucket_eight_raises") is not True:
        failures.append("bucket_eight_did_not_raise")
    # stop facts
    s_happy = live.get("stop_happy") or {}
    want_happy = EXPECTED_STOP_FACT["happy_path_entry_50000_atr_160"]
    for key, value in want_happy.items():
        got = s_happy.get(key)
        if isinstance(value, bool):
            if got is not value:
                failures.append("stop_happy_mismatch:" + key)
        elif not _almost_equal(got, value):
            failures.append("stop_happy_mismatch:" + key)
    # floor facts
    tiny = live.get("floor_tiny") or {}
    if tiny.get("floor_pass") != EXPECTED_FLOOR_FACT[
            "tiny_stop_distance_6_at_entry_50000_all_variants_fail"]:
        failures.append("floor_tiny_should_fail_all")
    big = live.get("floor_big") or {}
    if big.get("floor_pass") != EXPECTED_FLOOR_FACT[
            "stop_distance_240_at_entry_50000_all_variants_pass"]:
        failures.append("floor_big_should_pass_all")
    boundary = live.get("floor_boundary") or {}
    if boundary.get("floor_pass") != EXPECTED_FLOOR_FACT[
            "stop_distance_200_at_entry_50000_boundary_2r_fails"
            "_others_pass"]:
        failures.append("floor_boundary_mismatch")
    # anti-cluster boundary verification
    if live.get("gap_4_pair_kept_ids") != ("X",):
        failures.append("anti_cluster_gap4_should_keep_only_X")
    if live.get("gap_4_pair_dropped_ids") != ("Y",):
        failures.append("anti_cluster_gap4_should_drop_Y")
    if live.get("gap_5_pair_kept_ids") != ("X", "Z"):
        failures.append("anti_cluster_gap5_should_keep_both")
    if live.get("gap_5_pair_dropped_ids") != ():
        failures.append("anti_cluster_gap5_should_drop_none")
    # sample-size verification
    s3 = live.get("sample_3") or {}
    s100 = live.get("sample_100") or {}
    if s3.get("below_minimum_at_dry_run") is not True:
        failures.append("sample_3_should_flag_below")
    if s100.get("below_minimum_at_dry_run") is not False:
        failures.append("sample_100_should_not_flag_below")
    if s3.get("minimum_required_at_labels_review_gate") != 100:
        failures.append("sample_threshold_must_be_100")
    if s3.get("enforced_at_labels_review_gate_only") is not True:
        failures.append(
            "sample_must_be_enforced_at_labels_review_gate_only")
    if s3.get("does_not_consume_edit_token") is not True:
        failures.append("sample_must_not_consume_edit_token")
    return failures


def build_candidate_10_dry_run_review() -> dict[str, Any]:
    """Assemble the C10 dry-run review. Chain-gated on the nine-record
    ledger, the pushed C10 family proposal, the pushed C10 spec
    review, the pushed C10 detector spec + dry-run, the pushed V5 +
    V4 + V3 blacklists, the pushed V2, Recommendation V1, and Autopilot
    Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C10R_SCHEMA_VERSION, "label": C10R_LABEL,
        "mode": C10R_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_dry_run_verdict": EXPECTED_DRY_RUN_VERDICT,
        "expected_combined_verdict": EXPECTED_COMBINED_VERDICT,
        "expected_fixture_counts": {
            name: ({k: (list(v) if isinstance(v, tuple) else v)
                    for k, v in value.items()}
                   if isinstance(value, dict) else value)
            for name, value in EXPECTED_FIXTURE_COUNTS.items()},
        "expected_accepted_setup": dict(EXPECTED_ACCEPTED_SETUP),
        "expected_bucket_selection_fact": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in EXPECTED_BUCKET_SELECTION_FACT.items()},
        "expected_in_out_of_sample_fact": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_IN_OUT_OF_SAMPLE_FACT.items()},
        "expected_calendar_trigger_fact":
            dict(EXPECTED_CALENDAR_TRIGGER_FACT),
        "expected_entry_rule_fact": dict(EXPECTED_ENTRY_RULE_FACT),
        "expected_stop_fact":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_STOP_FACT.items()},
        "expected_floor_fact":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_FLOOR_FACT.items()},
        "expected_anti_cluster": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_ANTI_CLUSTER.items()},
        "expected_sample_size": dict(EXPECTED_SAMPLE_SIZE),
        "expected_universe_enforcement": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_UNIVERSE_ENFORCEMENT.items()},
        "expected_edit_token_state":
            dict(EXPECTED_EDIT_TOKEN_STATE),
        "frozen_review_findings": list(FROZEN_REVIEW_FINDINGS),
        "claim_locks": list(CLAIM_LOCKS),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_review_only": True,
        "is_a_rescue_attempt": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_detector_now": False, "unlocks_labels_now": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "claims_profitability": False,
        "c10_edit_token_consumed_by_this_review": False,
    }
    # chain gates
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    if build_candidate_10_family_proposal()["verdict"] != (
            VERDICT_C10P_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("candidate_10_proposal_not_certifying")
        return record
    if build_candidate_10_spec_review()["verdict"] != (
            VERDICT_C10S_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append(
            "candidate_10_spec_review_not_certifying")
        return record
    if build_candidate_10_detector_spec_contract()["verdict"] != (
            VERDICT_C10D_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append(
            "candidate_10_detector_spec_not_certifying")
        return record
    if build_rejected_family_blacklist_v5()["verdict"] != (
            VERDICT_BL5_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C10R_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    # recompute and certify
    live = _recompute_live_dry_run()
    failures = _certify_recomputed(live)
    record["failures"] = failures
    record["verdict"] = (VERDICT_C10R_FROZEN if not failures
                         else VERDICT_C10R_REJECTED)
    return record


def validate_candidate_10_dry_run_review(record: Any
                                         ) -> dict[str, Any]:
    """Validate shape, frozen evidence, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed = (VERDICT_C10R_FROZEN, VERDICT_C10R_REJECTED,
               VERDICT_C10R_BLOCKED)
    if r.get("verdict") not in allowed:
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("expected_detector_verdict") != EXPECTED_DETECTOR_VERDICT:
        errors.append("expected_detector_verdict_tampered")
    if r.get("expected_dry_run_verdict") != EXPECTED_DRY_RUN_VERDICT:
        errors.append("expected_dry_run_verdict_tampered")
    if r.get("expected_combined_verdict") != (
            EXPECTED_COMBINED_VERDICT):
        errors.append("expected_combined_verdict_tampered")
    expected_counts = {
        name: ({k: (list(v) if isinstance(v, tuple) else v)
                for k, v in value.items()}
               if isinstance(value, dict) else value)
        for name, value in EXPECTED_FIXTURE_COUNTS.items()}
    if r.get("expected_fixture_counts") != expected_counts:
        errors.append("expected_fixture_counts_tampered")
    if r.get("expected_accepted_setup") != EXPECTED_ACCEPTED_SETUP:
        errors.append("expected_accepted_setup_tampered")
    expected_bucket = {
        key: (dict(value) if isinstance(value, dict) else value)
        for key, value in EXPECTED_BUCKET_SELECTION_FACT.items()}
    if r.get("expected_bucket_selection_fact") != expected_bucket:
        errors.append("expected_bucket_selection_fact_tampered")
    expected_inout = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_IN_OUT_OF_SAMPLE_FACT.items()}
    if r.get("expected_in_out_of_sample_fact") != expected_inout:
        errors.append("expected_in_out_of_sample_fact_tampered")
    if r.get("expected_calendar_trigger_fact") != (
            EXPECTED_CALENDAR_TRIGGER_FACT):
        errors.append("expected_calendar_trigger_fact_tampered")
    if r.get("expected_entry_rule_fact") != (
            EXPECTED_ENTRY_RULE_FACT):
        errors.append("expected_entry_rule_fact_tampered")
    expected_stop = {key: (dict(value) if isinstance(value, dict)
                           else value)
                     for key, value
                     in EXPECTED_STOP_FACT.items()}
    if r.get("expected_stop_fact") != expected_stop:
        errors.append("expected_stop_fact_tampered")
    expected_floor = {key: (dict(value) if isinstance(value, dict)
                            else value)
                      for key, value
                      in EXPECTED_FLOOR_FACT.items()}
    if r.get("expected_floor_fact") != expected_floor:
        errors.append("expected_floor_fact_tampered")
    expected_anti = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_ANTI_CLUSTER.items()}
    if r.get("expected_anti_cluster") != expected_anti:
        errors.append("expected_anti_cluster_tampered")
    if r.get("expected_sample_size") != EXPECTED_SAMPLE_SIZE:
        errors.append("expected_sample_size_tampered")
    expected_universe = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_UNIVERSE_ENFORCEMENT.items()}
    if r.get("expected_universe_enforcement") != expected_universe:
        errors.append("expected_universe_enforcement_tampered")
    if r.get("expected_edit_token_state") != (
            EXPECTED_EDIT_TOKEN_STATE):
        errors.append("expected_edit_token_state_tampered")
    if tuple(r.get("frozen_review_findings") or ()) != (
            FROZEN_REVIEW_FINDINGS):
        errors.append("frozen_review_findings_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("current_loop_stage") != CURRENT_LOOP_STAGE:
        errors.append("current_loop_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_review_only", True),
                      ("is_a_rescue_attempt", False),
                      ("c10_edit_token_consumed_by_this_review",
                       False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
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
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C10R_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
