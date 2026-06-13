"""SPARTA CANDIDATE #9 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, NOT A PROFITABILITY CLAIM):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Freezes the synthetic-fixture dry-run outcomes of the pushed
Candidate #9 detector spec. The dry run is pure, deterministic and
reads NO files, so this review certifies by RE-COMPUTING every
frozen fact live from the pushed detector module -- the per-fixture
attempt and acceptance counts, the single accepted setup's exact
geometry (rolling stats, ATR, entry, stop, targets, floor bps), the
rejection statuses for each negative-path fixture, the joint-
trigger logic, the entry-bar invalidation behaviour, the anti-
cluster filter behaviour including the kept/dropped IDs and the
boundary at exactly 8 bars, the sample-size adequacy behaviour, and
the context enforcement (BTCUSD / 15m / long_only + non-list bars
raises). If any future change makes the pushed scanner or fixtures
behave differently, this review flips to REJECTED on its own.

Synthetic fixtures only. No real candle has been touched for
Candidate #9, no staged data read, no aggregation executed, no
labels, no replay, no artifacts, and this module performs none.
This gate authorizes NO real detection: the real-candle gate
becomes reachable only after this review is committed and pushed,
and opens only on its own explicit human command. Nothing here is a
profitability claim.

Chain-gated live on: the pushed eight-record rejection ledger
(C1-C8), the pushed Overnight Research Autopilot V2, the pushed
Recommendation V1, the pushed Autopilot Loop V1, the pushed V3 + V4
rejected-family blacklists, the pushed Candidate #9 family
proposal, the pushed Candidate #9 spec review, and the pushed
Candidate #9 detector spec + synthetic-fixture dry-run path.
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract import (
    VERDICT_C9D_DRY_RUN_PASSED,
    VERDICT_C9D_READY,
    build_candidate_9_detector_spec_contract,
    run_c9_detector_dry_run,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract import (
    VERDICT_C9S_READY,
    build_candidate_9_spec_review,
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
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C9R_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_dry_run"
    "_review.v1")
C9R_LABEL = ("SPARTA Candidate #9 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM, NOT A RESCUE)")
C9R_MODE = "RESEARCH_ONLY"
VERDICT_C9R_FROZEN = "CANDIDATE_9_DRY_RUN_REVIEW_FROZEN"
VERDICT_C9R_REJECTED = "CANDIDATE_9_DRY_RUN_REVIEW_REJECTED"
VERDICT_C9R_BLOCKED = "CANDIDATE_9_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_9_REAL_CANDLE_DETECTION")
CURRENT_LOOP_STAGE = "detector_and_label_review"

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_9_DETECTOR_SPEC_READY"
EXPECTED_DRY_RUN_VERDICT = "CANDIDATE_9_DETECTOR_DRY_RUN_PASSED"
EXPECTED_COMBINED_VERDICT = (
    "CANDIDATE_9_DETECTOR_SPEC_DRY_RUN_READY")

# ---- frozen fixture-level counts from the pushed dry-run output ----------

EXPECTED_FIXTURE_COUNTS = {
    "happy_path_joint_trigger":
        {"attempts": 1, "accepted": 1,
         "first_accepted_floor_pass":
             {"2r": True, "3r": True, "4r": True}},
    "insufficient_history":
        {"attempts": 0},
    "equality_at_z_threshold":
        {"attempts": 0},
    "equality_at_volume_median":
        {"attempts": 0},
    "z_only_no_volume":
        {"attempts": 0},
    "volume_only_no_z":
        {"attempts": 0},
    "entry_bar_invalidation":
        {"attempts": 1, "accepted": 0,
         "rejected_entry_invalidation": 1},
    "geometry_floor_all_variants_fail":
        {"attempts": 1, "accepted": 0,
         "rejected_geometry_floor": 1,
         "floor_pass_by_variant":
             {"2r": False, "3r": False, "4r": False}},
    "anti_cluster":
        {"kept_ids":
             ("BTCUSD_2026-05-02T01:00:00Z", "synthetic_c_outside"),
         "dropped_ids": ("synthetic_b_inside",),
         "anti_cluster_min_bar_gap": 8,
         "anti_cluster_does_not_consume_edit_token": True},
    "sample_size_adequacy":
        {"below_minimum_at_dry_run": True,
         "at_threshold_below_flag": False,
         "enforced_at_labels_review_gate_only": True,
         "does_not_consume_edit_token": True},
    "context_enforcement":
        {"symbol_eth": True, "timeframe_1h": True,
         "direction_short": True, "non_list_bars": True},
}


# ---- frozen single accepted setup (happy path) ---------------------------

EXPECTED_ACCEPTED_SETUP = {
    "setup_id": "BTCUSD_2026-05-02T01:00:00Z",
    "symbol": "BTCUSD",
    "timeframe": "15m",
    "direction": "long_only",
    "trigger_index": 100,
    "trigger_time": "2026-05-02T01:00:00Z",
    "trigger_close": 49100.0,
    "trigger_low": 49000.0,
    "trigger_high": 50050.0,
    "trigger_volume": 50.0,
    "rolling_window_bars": 96,
    "rolling_mean_log_return": -0.0,
    "rolling_std_log_return": 0.001004747,
    "rolling_median_volume": 100.0,
    "trigger_log_return": -0.019163471,
    "downside_z_threshold_value": -0.002009494,
    "z_condition_passes": True,
    "volume_condition_passes": True,
    "joint_trigger_passes": True,
    "atr_at_trigger_bar": 126.071429,
    "entry_index": 101,
    "entry_time": "2026-05-02T01:15:00Z",
    "entry_price": 49200.0,
    "entry_bar_close_strictly_above_trigger_low": True,
    "stop_buffer_price": 25.214286,
    "stop_price": 48974.785714,
    "stop_distance": 225.214286,
    "stop_below_entry": True,
    "stop_below_trigger_low": True,
    "target_2r": 49650.428571,
    "target_3r": 49875.642857,
    "target_4r": 50100.857143,
    "target_distance_bps_2r": 91.550523,
    "target_distance_bps_3r": 137.325784,
    "target_distance_bps_4r": 183.101045,
    "geometry_floor_pass_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "accepted_for_labeling_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "replay_start_time": "2026-05-02T01:30:00Z",
    "status": "accepted_for_replay_review",
}


# ---- frozen behavioural facts independent of fixtures --------------------

EXPECTED_INSUFFICIENT_HISTORY_FACT = {
    "rolling_window_bars": 96,
    "min_evaluable_trigger_bar_index": 97,
    "scanner_skips_below_lookback": True,
    "warmup_50_attempts": 0,
}

EXPECTED_JOINT_TRIGGER_FACT = {
    "rule": "joint_z_score_AND_below_median_volume_on_same_bar",
    "z_strict_inequality_below_mean_minus_2_sigma": True,
    "volume_strict_inequality_below_rolling_median": True,
    "equality_at_z_threshold_rejects": True,
    "equality_at_volume_median_rejects": True,
    "z_only_no_volume_rejects": True,
    "volume_only_no_z_rejects": True,
}

EXPECTED_ENTRY_RULE_FACT = {
    "entry_price": "close_of_next_completed_15m_bar_after_trigger_bar",
    "no_intrabar_entry": True,
    "no_same_bar_entry": True,
    "invalidate_if_entry_bar_close_at_or_below_trigger_bar_low":
        True,
    "rejection_status_on_invalidation":
        "rejected_entry_bar_close_at_or_below_trigger_bar_low",
}

EXPECTED_STOP_FACT = {
    "structure_stop_buffer_atr_multiplier": 0.20,
    "stop_price_formula":
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar",
    "stop_must_be_below_entry_and_below_trigger_low": True,
    "stop_never_tightened_after_entry": True,
    "happy_path_trigger_low_49000_atr_126_071429":
        {"stop_buffer_price": 25.214286,
         "stop_price": 48974.785714,
         "stop_below_entry": True,
         "stop_below_trigger_low": True,
         "valid": True},
}

EXPECTED_FLOOR_FACT = {
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "tiny_stop_distance_50_at_entry_50000_all_variants_fail":
        {"2r": False, "3r": False, "4r": False},
    "stop_distance_250_at_entry_50000_all_variants_pass":
        {"2r": True, "3r": True, "4r": True},
    "stop_distance_200_at_entry_50000_boundary_2r_fails_others_pass":
        {"2r": False, "3r": True, "4r": True},
}

EXPECTED_ANTI_CLUSTER = {
    "anti_cluster_min_bar_gap": 8,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    "kept_ids_in_dry_run":
        ("BTCUSD_2026-05-02T01:00:00Z", "synthetic_c_outside"),
    "dropped_ids_in_dry_run": ("synthetic_b_inside",),
    "boundary_at_8_is_kept": True,
    "gap_of_7_is_dropped": True,
}

EXPECTED_SAMPLE_SIZE = {
    "threshold_min_accepted_at_labels_review_gate": 20,
    "count_3_is_below_threshold": True,
    "count_20_is_not_below_threshold": True,
    "enforced_at_labels_review_gate_only": True,
    "does_not_consume_edit_token": True,
}

EXPECTED_UNIVERSE_ENFORCEMENT = {
    "universe": ("BTCUSD",),
    "timeframe": "15m",
    "direction": "long_only",
    "non_btcusd_raises_valueerror": True,
    "non_15m_raises_valueerror": True,
    "non_long_only_raises_valueerror": True,
    "non_list_bars_raises_valueerror": True,
}

EXPECTED_EDIT_TOKEN_STATE = {
    "c9_edit_token_consumed_by_this_review": False,
    "anti_cluster_gap_remains_proposal_level_locked_not_edit_token":
        True,
    "sample_size_threshold_remains_proposal_level_locked_not_edit"
    "_token": True,
    "explicit_edge_argument_field_remains_proposal_level_locked_not"
    "_edit_token": True,
    "edit_token_eligible_parameters_unchanged_from_spec_review":
        True,
}

FROZEN_REVIEW_FINDINGS = (
    "valid joint price-AND-volume trigger fixture produces exactly "
    "one accepted setup with floor pass at 2r/3r/4r",
    "the accepted setup has trigger close 49100.0, trigger low "
    "49000.0, rolling std log return 0.001004747, downside z "
    "threshold -0.002009494, ATR(14) at trigger 126.071429, entry "
    "price 49200.0, stop distance 225.214286",
    "insufficient history produces zero attempts; the scanner "
    "skips every bar with index below the 96-bar rolling window",
    "strict-below z threshold rejects equality (no clip rule); "
    "strict-below median volume rejects equality (no clip rule)",
    "z-only condition without below-median volume rejects",
    "volume-only condition without below-z return rejects",
    "the joint trigger requires BOTH conditions on the SAME "
    "completed 15m bar; neither alone is a trigger",
    "entry-bar invalidation fires when the entry bar's close is at "
    "or below the trigger bar's low; the asymmetry thesis is "
    "structurally falsified by that bar",
    "structure-stop formula uses trigger_bar_low - 0.20 x ATR14 "
    "with a positive distance only when the resulting stop is "
    "below both entry and the trigger bar low",
    "81 bps floor per variant is enforced at label time; boundary "
    "at 80 bps fails 2r and passes 3r/4r",
    "btcusd-only universe is enforced by valueerror on non-btcusd "
    "/ non-15m / non-long-only / non-list bars",
    "anti-cluster gap of 8 keeps boundary events and drops events "
    "with gap < 8",
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the single c9 edit token",
    "sample-size adequacy threshold of 20 is proposal/spec-level "
    "locked, applies at the labels-review gate only, and does NOT "
    "consume the single c9 edit token",
    "explicit-edge-argument field is proposal/spec-level locked "
    "and does NOT consume the single c9 edit token",
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
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
    "explicit_edge_argument_field_remains_proposal_level_locked",
    "c9_edit_token_not_consumed_by_this_gate",
)


def get_candidate_9_dry_run_review_label() -> str:
    return C9R_LABEL


# ---- re-compute the live dry-run facts -----------------------------------

def _recompute_live_dry_run() -> dict[str, Any]:
    """Re-run the pushed dry run and the supporting fixture-level
    scans live. Pure; in-memory only."""
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as _det
    dry = run_c9_detector_dry_run()
    bars_valid = _det.fixture_happy_path_joint_trigger()
    accepted_valid = [s for s in _det.scan_c9_setups(
        bars_valid, "BTCUSD")
        if s["status"] == "accepted_for_replay_review"]
    bars_50 = _det.fixture_insufficient_history(baseline_length=50)
    setups_50 = _det.scan_c9_setups(bars_50, "BTCUSD")
    bars_30 = _det.fixture_insufficient_history(baseline_length=30)
    setups_30 = _det.scan_c9_setups(bars_30, "BTCUSD")
    # universe enforcement
    btcusd_only_raises = True
    try:
        _det.scan_c9_setups(bars_valid, "ETHUSD")
        btcusd_only_raises = False
    except ValueError:
        pass
    non_15m_raises = True
    try:
        _det.scan_c9_setups(bars_valid, "BTCUSD", timeframe="1h")
        non_15m_raises = False
    except ValueError:
        pass
    non_long_only_raises = True
    try:
        _det.scan_c9_setups(bars_valid, "BTCUSD",
                            direction="short_only")
        non_long_only_raises = False
    except ValueError:
        pass
    non_list_raises = True
    try:
        _det.scan_c9_setups("not a list", "BTCUSD")
        non_list_raises = False
    except ValueError:
        pass
    # stop call from the happy-path geometry
    stop_happy = _det.compute_stop(49200.0, 49000.0, 126.071429)
    # floor independent calls
    floor_tiny = _det.geometry_floor_by_variant(50000.0, 50.0)
    floor_big = _det.geometry_floor_by_variant(50000.0, 250.0)
    floor_boundary = _det.geometry_floor_by_variant(50000.0, 200.0)
    # anti-cluster boundary independent calls
    seed_x = {"setup_id": "X", "symbol": "BTCUSD",
              "status": "accepted_for_replay_review",
              "entry_index": 200, "rejection_reasons": []}
    pair_gap_7 = _det.apply_anti_cluster_filter([
        seed_x,
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review",
         "entry_index": 207, "rejection_reasons": []}])
    pair_gap_8 = _det.apply_anti_cluster_filter([
        seed_x,
        {"setup_id": "Z", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review",
         "entry_index": 208, "rejection_reasons": []}])
    # sample-size independent calls
    sample_3 = _det.check_sample_size_adequacy(
        [{"entry_index": i} for i in range(3)])
    sample_20 = _det.check_sample_size_adequacy(
        [{"entry_index": i}
         for i in range(20)])
    return {
        "dry_run": dry,
        "accepted_valid_setup":
            (accepted_valid[0] if accepted_valid else None),
        "accepted_valid_count": len(accepted_valid),
        "warmup_50_attempts": len(setups_50),
        "warmup_30_attempts": len(setups_30),
        "btcusd_only_raises": btcusd_only_raises,
        "non_15m_raises": non_15m_raises,
        "non_long_only_raises": non_long_only_raises,
        "non_list_raises": non_list_raises,
        "stop_happy": stop_happy,
        "floor_tiny": floor_tiny,
        "floor_big": floor_big,
        "floor_boundary": floor_boundary,
        "gap_7_pair_kept_ids": tuple(s["setup_id"] for s
                                     in pair_gap_7["kept"]),
        "gap_7_pair_dropped_ids": tuple(s["setup_id"] for s
                                        in pair_gap_7["dropped"]),
        "gap_8_pair_kept_ids": tuple(s["setup_id"] for s
                                     in pair_gap_8["kept"]),
        "gap_8_pair_dropped_ids": tuple(s["setup_id"] for s
                                        in pair_gap_8["dropped"]),
        "sample_3": sample_3,
        "sample_20": sample_20,
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
            if key == "kept_ids" or key == "dropped_ids":
                if tuple(got.get(key) or ()) != tuple(value):
                    failures.append(
                        "fixture_anti_cluster_mismatch:%s:%s"
                        % (name, key))
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
    if live.get("warmup_30_attempts") != 0:
        failures.append("insufficient_history_30_did_not_skip")
    if live.get("warmup_50_attempts") != 0:
        failures.append("insufficient_history_50_did_not_skip")
    if live.get("btcusd_only_raises") is not True:
        failures.append("non_btcusd_did_not_raise")
    if live.get("non_15m_raises") is not True:
        failures.append("non_15m_did_not_raise")
    if live.get("non_long_only_raises") is not True:
        failures.append("non_long_only_did_not_raise")
    if live.get("non_list_raises") is not True:
        failures.append("non_list_bars_did_not_raise")
    # stop facts
    s_happy = live.get("stop_happy") or {}
    want_happy = EXPECTED_STOP_FACT[
        "happy_path_trigger_low_49000_atr_126_071429"]
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
            "tiny_stop_distance_50_at_entry_50000_all_variants_fail"]:
        failures.append("floor_tiny_should_fail_all")
    big = live.get("floor_big") or {}
    if big.get("floor_pass") != EXPECTED_FLOOR_FACT[
            "stop_distance_250_at_entry_50000_all_variants_pass"]:
        failures.append("floor_big_should_pass_all")
    boundary = live.get("floor_boundary") or {}
    if boundary.get("floor_pass") != EXPECTED_FLOOR_FACT[
            "stop_distance_200_at_entry_50000_boundary_2r_fails"
            "_others_pass"]:
        failures.append("floor_boundary_mismatch")
    # anti-cluster boundary verification
    if live.get("gap_7_pair_kept_ids") != ("X",):
        failures.append("anti_cluster_gap7_should_keep_only_X")
    if live.get("gap_7_pair_dropped_ids") != ("Y",):
        failures.append("anti_cluster_gap7_should_drop_Y")
    if live.get("gap_8_pair_kept_ids") != ("X", "Z"):
        failures.append("anti_cluster_gap8_should_keep_both")
    if live.get("gap_8_pair_dropped_ids") != ():
        failures.append("anti_cluster_gap8_should_drop_none")
    # sample-size verification
    s3 = live.get("sample_3") or {}
    s20 = live.get("sample_20") or {}
    if s3.get("below_minimum_at_dry_run") is not True:
        failures.append("sample_3_should_flag_below")
    if s20.get("below_minimum_at_dry_run") is not False:
        failures.append("sample_20_should_not_flag_below")
    if s3.get("minimum_required_at_labels_review_gate") != 20:
        failures.append("sample_threshold_must_be_20")
    if s3.get("enforced_at_labels_review_gate_only") is not True:
        failures.append(
            "sample_must_be_enforced_at_labels_review_gate_only")
    if s3.get("does_not_consume_edit_token") is not True:
        failures.append("sample_must_not_consume_edit_token")
    return failures


def build_candidate_9_dry_run_review() -> dict[str, Any]:
    """Assemble the C9 dry-run review. Chain-gated on the eight-
    record ledger, the pushed C9 family proposal, the pushed C9 spec
    review, the pushed C9 detector spec + dry-run, the pushed V4
    blacklist, V3, V2, Recommendation V1, and Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C9R_SCHEMA_VERSION, "label": C9R_LABEL,
        "mode": C9R_MODE, "lane": "crypto_d1_auto_research",
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
        "expected_insufficient_history_fact":
            dict(EXPECTED_INSUFFICIENT_HISTORY_FACT),
        "expected_joint_trigger_fact":
            dict(EXPECTED_JOINT_TRIGGER_FACT),
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
        "c9_edit_token_consumed_by_this_review": False,
    }
    # chain gates
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == C6_STATUS == C7_STATUS == C8_STATUS
            == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    if build_candidate_9_family_proposal()["verdict"] != (
            VERDICT_C9P_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("candidate_9_proposal_not_certifying")
        return record
    if build_candidate_9_spec_review()["verdict"] != VERDICT_C9S_READY:
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append(
            "candidate_9_spec_review_not_certifying")
        return record
    spec_record = build_candidate_9_detector_spec_contract()
    if spec_record["verdict"] != VERDICT_C9D_READY:
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append(
            "candidate_9_detector_spec_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C9R_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    # recompute and certify
    live = _recompute_live_dry_run()
    failures = _certify_recomputed(live)
    record["failures"] = failures
    record["verdict"] = (VERDICT_C9R_FROZEN if not failures
                         else VERDICT_C9R_REJECTED)
    return record


def validate_candidate_9_dry_run_review(record: Any
                                        ) -> dict[str, Any]:
    """Validate shape, frozen evidence, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed = (VERDICT_C9R_FROZEN, VERDICT_C9R_REJECTED,
               VERDICT_C9R_BLOCKED)
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
    if r.get("expected_insufficient_history_fact") != (
            EXPECTED_INSUFFICIENT_HISTORY_FACT):
        errors.append("expected_insufficient_history_fact_tampered")
    if r.get("expected_joint_trigger_fact") != (
            EXPECTED_JOINT_TRIGGER_FACT):
        errors.append("expected_joint_trigger_fact_tampered")
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
                      ("c9_edit_token_consumed_by_this_review",
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
    if r.get("verdict") == VERDICT_C9R_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
