"""SPARTA CANDIDATE #7 DRY-RUN REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, NOT A PROFITABILITY CLAIM):
VOLATILITY_COMPRESSION_EXPANSION_V1.

Freezes the synthetic dry-run outcomes of the pushed Candidate #7
detector spec. The dry run is pure, deterministic and reads NO files,
so this review certifies by RE-COMPUTING every frozen fact live from
the pushed detector module -- fixture attempt/accepted counts, the
accepted setup's exact geometry (entry 50300.0, structure-wider stop
distance 301.0, all 81 bps floors passing), the rejection statuses for
each negative-path fixture, and the anti-cluster filter behaviour
including the kept/dropped IDs and the boundary at exactly 6 bars. If
any future change makes the pushed scanner or fixtures behave
differently, this review flips to REJECTED on its own.

Synthetic fixtures only. No real candle has been touched for candidate
#7, no staged data read, no aggregation executed, no labels, no
replay, no artifacts, and this module performs none. This gate
authorizes NO real detection: the real-candle gate becomes reachable
only after this review is committed and pushed, and opens only on its
own explicit human command. Nothing here is a profitability claim.

Chain-gated live on: the pushed six-record rejection ledger (C1-C6),
the pushed Overnight Research Autopilot V2, the pushed Recommendation
V1, the pushed Autopilot Loop V1, the pushed Candidate #7 family
proposal, the pushed Candidate #7 spec review, and the pushed
Candidate #7 detector spec + dry-run path.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
import sparta_commander.volatility_compression_expansion_v1_detector_spec_dry_run_contract as _det
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
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
from sparta_commander.volatility_compression_expansion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C7P_READY,
    build_candidate_7_family_proposal,
)
from sparta_commander.volatility_compression_expansion_v1_spec_review_contract import (
    VERDICT_C7S_READY,
    build_candidate_7_spec_review,
)

C7R_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_detector_dry_run_review.v1")
C7R_LABEL = ("SPARTA Candidate #7 Dry-Run Review / Evidence Freeze "
             "(READ-ONLY, RESEARCH ONLY, SYNTHETIC OUTCOMES ONLY, "
             "NOT A PROFITABILITY CLAIM)")
C7R_MODE = "RESEARCH_ONLY"
VERDICT_C7R_FROZEN = "CANDIDATE_7_DRY_RUN_REVIEW_FROZEN"
VERDICT_C7R_REJECTED = "CANDIDATE_7_DRY_RUN_REVIEW_REJECTED"
VERDICT_C7R_BLOCKED = "CANDIDATE_7_DRY_RUN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_7_REAL_CANDLE_DETECTION")

EXPECTED_DETECTOR_VERDICT = "CANDIDATE_7_DETECTOR_SPEC_READY"
EXPECTED_DRY_RUN_VERDICT = "CANDIDATE_7_DETECTOR_DRY_RUN_PASSED"
EXPECTED_COMBINED_VERDICT = (
    "CANDIDATE_7_DETECTOR_SPEC_DRY_RUN_READY")

# Frozen fixture-level counts from the pushed dry-run output ----------------
EXPECTED_FIXTURE_COUNTS = {
    "valid_compression_expansion":
        {"attempts": 19, "accepted": 1},
    "no_contraction":
        {"attempts": 4,
         "statuses": ("rejected_contraction_window",)},
    "only_4_contraction_bars":
        {"attempts": 4, "accepted": 0},
    "expansion_below_1_8x":
        {"attempts": 19, "accepted": 0,
         "rejected_expansion_multiplier": 8},
    "close_at_midpoint":
        {"attempts": 19, "accepted": 0,
         "rejected_close_not_in_upper_third": 1},
}

# Frozen accepted setup -- the single accepted setup from the
# valid_compression_expansion fixture ---------------------------------------
EXPECTED_ACCEPTED_SETUP = {
    "setup_id": "BTCUSD_2026-01-23T12:00:00Z",
    "symbol": "BTCUSD",
    "timeframe": "4h",
    "direction": "long",
    "event_index": 135,
    "event_time": "2026-01-23T12:00:00Z",
    "entry_price": 50300.0,
    "atr14_at_event": 24.285714,
    "contracted_atr": 1.5,
    "rolling_average_atr_at_contraction_end": 4.095,
    "expansion_true_range": 320.5,
    "expansion_multiplier_observed": 213.666667,
    "close_in_upper_third_passes": True,
    "contraction_window_passes": True,
    "structure_lookback_low": 49999.0,
    "atr_stop_distance": 36.428571,
    "structure_stop_distance": 301.0,
    "stop_distance": 301.0,
    "stop_price": 49999.0,
    "stop_source": "structure_wider_than_1_5x_atr",
    "target_2r": 50902.0,
    "target_3r": 51203.0,
    "target_4r": 51504.0,
    "target_distance_bps_2r": 119.681909,
    "target_distance_bps_3r": 179.522863,
    "target_distance_bps_4r": 239.363817,
    "geometry_floor_pass_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "accepted_for_labeling_by_variant":
        {"2r": True, "3r": True, "4r": True},
    "replay_start_time": "2026-01-23T16:00:00Z",
    "status": "accepted_for_replay_review",
}

# Frozen anti-cluster filter behaviour --------------------------------------
EXPECTED_ANTI_CLUSTER = {
    "anti_cluster_min_bar_gap": 6,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    # the 3-event synthetic in the dry run: base at index 135,
    # synthetic_b at 135+3=138 (inside), synthetic_c at 135+6=141
    # (boundary - kept)
    "kept_ids_in_dry_run":
        ("BTCUSD_2026-01-23T12:00:00Z", "synthetic_c_outside"),
    "dropped_ids_in_dry_run": ("synthetic_b_inside",),
    "boundary_at_6_is_kept": True,
    "gap_of_5_is_dropped": True,
}

EXPECTED_INSUFFICIENT_HISTORY_FACT = {
    # min_event_index = 14 + 99 + 5 = 118
    "min_event_index": 118,
    "scanner_skips_below_min": True,
    "fixture_with_warmup_30_attempts": 0,
    "fixture_with_warmup_95_attempts": 0,
}

EXPECTED_STRICT_CONTRACTION_FACT = {
    "rule": "strict_less_than_0_6_x_rolling_avg",
    "equality_at_0_6_rejects": True,
}

EXPECTED_UNIVERSE_ENFORCEMENT = {
    "universe": ("BTCUSD",),
    "non_btcusd_raises_valueerror": True,
    "non_list_bars_raises_valueerror": True,
}

EXPECTED_WIDER_STOP_FACTS = {
    "formula": "max(WIDER_STOP_ATR_MULTIPLIER * atr14, "
               "structure_stop_distance)",
    "wider_stop_atr_multiplier": 1.5,
    "structure_lookback_bars": 10,
    "structure_wider_path_proven_at_entry_100_low_92_atr_2":
        {"atr_stop_distance": 3.0,
         "structure_stop_distance": 8.0,
         "stop_distance": 8.0, "stop_price": 92.0, "valid": True},
    "atr_wider_path_proven_at_entry_100_low_99_atr_4":
        {"atr_stop_distance": 6.0,
         "structure_stop_distance": 1.0,
         "stop_distance": 6.0, "stop_price": 94.0, "valid": True},
}

EXPECTED_FLOOR_FACTS = {
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "tiny_stop_distance_1_at_entry_50000_all_variants_fail": True,
    "stop_distance_250_at_entry_50000_all_variants_pass": True,
    "stop_distance_at_40_bps_only_3r_and_4r_pass":
        {"2r": False, "3r": True, "4r": True},
}

FROZEN_REVIEW_FINDINGS = (
    "valid compression-then-expansion fixture produces exactly one "
    "accepted setup with floor pass at 2r/3r/4r",
    "the accepted setup uses structure-wider stop (301.0) over the "
    "1.5x atr stop (36.43)",
    "insufficient atr/rolling history produces zero attempts; scanner "
    "skips bars below min_event_index = 118",
    "missing 5-bar contraction window rejects all attempts on "
    "contraction",
    "only 4 consecutive contraction bars rejects all expansion "
    "attempts",
    "strict less-than 0.6 threshold rejects equality (no clip rule)",
    "expansion multiplier 1.7x rejects on rejected_expansion_"
    "multiplier",
    "close at midpoint rejects on rejected_close_not_in_upper_third",
    "btcusd-only universe is enforced by valueerror on non-btcusd",
    "non-list bars raises valueerror",
    "wider-stop formula uses max(1.5 x atr14, structure_lookback_low) "
    "in both directions",
    "81 bps floor per variant is enforced at label time; boundary at "
    "80 bps fails 2r and passes 3r/4r",
    "anti-cluster gap of 6 keeps boundary events and drops events "
    "with gap < 6",
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the single c7 edit token",
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
)


def get_candidate_7_dry_run_review_label() -> str:
    return C7R_LABEL


# ---- re-compute the live dry-run facts ------------------------------------

def _recompute_live_dry_run() -> dict[str, Any]:
    """Re-run the pushed dry run and the supporting fixture-level
    scans live. Pure; in-memory only."""
    dry = _det.run_c7_detector_dry_run()
    bars_valid = _det.fixture_warmup_then_contraction_then_expansion()
    accepted_valid = [s for s in _det.scan_c7_setups(
        bars_valid, "BTCUSD")
        if s["status"] == "accepted_for_replay_review"]
    bars_strict = _det.fixture_warmup_then_contraction_then_expansion(
        contracted_atr_target=0.9, rolling_atr_target=1.5)
    setups_strict = _det.scan_c7_setups(bars_strict, "BTCUSD")
    accepted_strict = [s for s in setups_strict
                       if s["status"] == "accepted_for_replay_review"]
    contraction_rejected_strict = [
        s for s in setups_strict
        if s["status"] == "rejected_contraction_window"]
    bars_under = _det.fixture_warmup_then_contraction_then_expansion(
        warmup_length=95)
    setups_under = _det.scan_c7_setups(bars_under, "BTCUSD")
    bars_short = _det.fixture_warmup_then_contraction_then_expansion(
        warmup_length=30)
    setups_short = _det.scan_c7_setups(bars_short, "BTCUSD")
    # universe enforcement
    btcusd_only_raises = True
    try:
        _det.scan_c7_setups(bars_valid, "ETHUSD")
        btcusd_only_raises = False
    except ValueError:
        pass
    non_list_raises = True
    try:
        _det.scan_c7_setups("not a list", "BTCUSD")
        non_list_raises = False
    except ValueError:
        pass
    # wider stop independent calls
    stop_structure_wider = _det.compute_stop(100.0, 92.0, 2.0)
    stop_atr_wider = _det.compute_stop(100.0, 99.0, 4.0)
    # floor independent calls
    floor_tiny = _det.geometry_floor_by_variant(50000.0, 1.0)
    floor_big = _det.geometry_floor_by_variant(50000.0, 250.0)
    floor_40bps = _det.geometry_floor_by_variant(
        50000.0, 50000.0 * 40.0 / 10000.0)
    # anti-cluster boundary independent calls
    boundary_pair = _det.apply_anti_cluster_filter([
        {"setup_id": "X", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 200,
         "rejection_reasons": []},
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 206,
         "rejection_reasons": []}])
    gap5_pair = _det.apply_anti_cluster_filter([
        {"setup_id": "X", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 200,
         "rejection_reasons": []},
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 205,
         "rejection_reasons": []}])
    return {
        "dry_run": dry,
        "accepted_valid_setup":
            (accepted_valid[0] if accepted_valid else None),
        "accepted_valid_count": len(accepted_valid),
        "strict_at_0_6_accepted": len(accepted_strict),
        "strict_at_0_6_has_contraction_rejection":
            len(contraction_rejected_strict) >= 1,
        "warmup_95_attempts": len(setups_under),
        "warmup_30_attempts": len(setups_short),
        "btcusd_only_raises": btcusd_only_raises,
        "non_list_raises": non_list_raises,
        "stop_structure_wider": stop_structure_wider,
        "stop_atr_wider": stop_atr_wider,
        "floor_tiny": floor_tiny,
        "floor_big": floor_big,
        "floor_40bps": floor_40bps,
        "boundary_pair_kept_ids": tuple(s["setup_id"] for s
                                        in boundary_pair["kept"]),
        "boundary_pair_dropped_ids": tuple(s["setup_id"] for s
                                           in boundary_pair[
                                               "dropped"]),
        "gap5_pair_kept_ids": tuple(s["setup_id"] for s
                                    in gap5_pair["kept"]),
        "gap5_pair_dropped_ids": tuple(s["setup_id"] for s
                                       in gap5_pair["dropped"]),
    }


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
            if key == "statuses":
                if tuple(got.get("statuses") or ()) != tuple(value):
                    failures.append(
                        "fixture_status_mismatch:%s" % name)
            elif got.get(key) != value:
                failures.append(
                    "fixture_count_mismatch:%s:%s" % (name, key))
    accepted = live.get("accepted_valid_setup") or {}
    if live.get("accepted_valid_count") != 1:
        failures.append("accepted_valid_count_not_1")
    stop_source = ("structure_wider_than_1_5x_atr"
                   if accepted.get("structure_stop_distance") and
                   accepted.get("atr_stop_distance") and
                   accepted["structure_stop_distance"] > accepted[
                       "atr_stop_distance"]
                   else "atr_wider_than_structure"
                   if accepted else None)
    for key, want in EXPECTED_ACCEPTED_SETUP.items():
        if key == "stop_source":
            if stop_source != want:
                failures.append("accepted_field_mismatch:" + key)
            continue
        got = accepted.get(key)
        if got != want:
            failures.append("accepted_field_mismatch:" + key)
    if live.get("strict_at_0_6_accepted") != 0:
        failures.append("strict_contraction_at_0_6_did_not_reject")
    if live.get("strict_at_0_6_has_contraction_rejection") is not True:
        failures.append(
            "strict_contraction_at_0_6_no_contraction_rejection")
    if live.get("warmup_30_attempts") != 0:
        failures.append("insufficient_history_30_did_not_skip")
    if live.get("warmup_95_attempts") != 0:
        failures.append("insufficient_history_95_did_not_skip")
    if live.get("btcusd_only_raises") is not True:
        failures.append("non_btcusd_did_not_raise")
    if live.get("non_list_raises") is not True:
        failures.append("non_list_bars_did_not_raise")
    # wider stop verification
    s_struct = live.get("stop_structure_wider") or {}
    want_struct = EXPECTED_WIDER_STOP_FACTS[
        "structure_wider_path_proven_at_entry_100_low_92_atr_2"]
    for key, value in want_struct.items():
        if s_struct.get(key) != value:
            failures.append("stop_structure_wider_mismatch:" + key)
    s_atr = live.get("stop_atr_wider") or {}
    want_atr = EXPECTED_WIDER_STOP_FACTS[
        "atr_wider_path_proven_at_entry_100_low_99_atr_4"]
    for key, value in want_atr.items():
        if s_atr.get(key) != value:
            failures.append("stop_atr_wider_mismatch:" + key)
    # floor verification
    tiny = live.get("floor_tiny") or {}
    if tiny.get("floor_pass") != {"2r": False, "3r": False,
                                  "4r": False}:
        failures.append("floor_tiny_should_fail_all")
    big = live.get("floor_big") or {}
    if big.get("floor_pass") != {"2r": True, "3r": True, "4r": True}:
        failures.append("floor_big_should_pass_all")
    forty = live.get("floor_40bps") or {}
    if forty.get("floor_pass") != EXPECTED_FLOOR_FACTS[
            "stop_distance_at_40_bps_only_3r_and_4r_pass"]:
        failures.append("floor_40bps_mismatch")
    # anti-cluster boundary verification
    if live.get("boundary_pair_kept_ids") != ("X", "Y"):
        failures.append("anti_cluster_boundary_6_should_keep_both")
    if live.get("boundary_pair_dropped_ids") != ():
        failures.append(
            "anti_cluster_boundary_6_should_drop_none")
    if live.get("gap5_pair_kept_ids") != ("X",):
        failures.append("anti_cluster_gap5_should_keep_only_X")
    if live.get("gap5_pair_dropped_ids") != ("Y",):
        failures.append("anti_cluster_gap5_should_drop_Y")
    return failures


def build_candidate_7_dry_run_review() -> dict[str, Any]:
    """Assemble the C7 dry-run review. Chain-gated on the six-record
    ledger, the pushed C7 detector spec/dry-run, the pushed C7 spec
    review, the pushed C7 family proposal, V2, Recommendation V1, and
    Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C7R_SCHEMA_VERSION, "label": C7R_LABEL,
        "mode": C7R_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "expected_detector_verdict": EXPECTED_DETECTOR_VERDICT,
        "expected_dry_run_verdict": EXPECTED_DRY_RUN_VERDICT,
        "expected_combined_verdict": EXPECTED_COMBINED_VERDICT,
        "expected_fixture_counts": {
            name: dict(value) for name, value
            in EXPECTED_FIXTURE_COUNTS.items()},
        "expected_accepted_setup":
            dict(EXPECTED_ACCEPTED_SETUP),
        "expected_anti_cluster": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_ANTI_CLUSTER.items()},
        "expected_insufficient_history_fact":
            dict(EXPECTED_INSUFFICIENT_HISTORY_FACT),
        "expected_strict_contraction_fact":
            dict(EXPECTED_STRICT_CONTRACTION_FACT),
        "expected_universe_enforcement": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value
            in EXPECTED_UNIVERSE_ENFORCEMENT.items()},
        "expected_wider_stop_facts":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_WIDER_STOP_FACTS.items()},
        "expected_floor_facts":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_FLOOR_FACTS.items()},
        "frozen_review_findings": list(FROZEN_REVIEW_FINDINGS),
        "claim_locks": list(CLAIM_LOCKS),
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
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_labels_now": False, "unlocks_replay_now": False,
        "unlocks_relabel_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    # full chain
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == C6_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    if build_candidate_7_family_proposal()["verdict"] != (
            VERDICT_C7P_READY):
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        return record
    if build_candidate_7_spec_review()["verdict"] != VERDICT_C7S_READY:
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append(
            "candidate_7_spec_review_not_certifying")
        return record
    spec_record = _det.build_c7_detector_spec_contract()
    if spec_record["verdict"] != _det.VERDICT_C7D_READY:
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append(
            "candidate_7_detector_spec_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C7R_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    # recompute and certify
    live = _recompute_live_dry_run()
    failures = _certify_recomputed(live)
    record["failures"] = failures
    record["verdict"] = (VERDICT_C7R_FROZEN if not failures
                         else VERDICT_C7R_REJECTED)
    return record


def validate_candidate_7_dry_run_review(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C7R_FROZEN,
                                VERDICT_C7R_REJECTED,
                                VERDICT_C7R_BLOCKED):
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
    expected_counts = {name: dict(value) for name, value
                       in EXPECTED_FIXTURE_COUNTS.items()}
    if r.get("expected_fixture_counts") != expected_counts:
        errors.append("expected_fixture_counts_tampered")
    if r.get("expected_accepted_setup") != EXPECTED_ACCEPTED_SETUP:
        errors.append("expected_accepted_setup_tampered")
    expected_anti = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_ANTI_CLUSTER.items()}
    if r.get("expected_anti_cluster") != expected_anti:
        errors.append("expected_anti_cluster_tampered")
    if r.get("expected_insufficient_history_fact") != (
            EXPECTED_INSUFFICIENT_HISTORY_FACT):
        errors.append("expected_insufficient_history_fact_tampered")
    if r.get("expected_strict_contraction_fact") != (
            EXPECTED_STRICT_CONTRACTION_FACT):
        errors.append("expected_strict_contraction_fact_tampered")
    expected_universe = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_UNIVERSE_ENFORCEMENT.items()}
    if r.get("expected_universe_enforcement") != expected_universe:
        errors.append("expected_universe_enforcement_tampered")
    expected_stop = {key: (dict(value) if isinstance(value, dict)
                           else value)
                     for key, value
                     in EXPECTED_WIDER_STOP_FACTS.items()}
    if r.get("expected_wider_stop_facts") != expected_stop:
        errors.append("expected_wider_stop_facts_tampered")
    expected_floor = {key: (dict(value) if isinstance(value, dict)
                            else value)
                      for key, value
                      in EXPECTED_FLOOR_FACTS.items()}
    if r.get("expected_floor_facts") != expected_floor:
        errors.append("expected_floor_facts_tampered")
    if tuple(r.get("frozen_review_findings") or ()) != (
            FROZEN_REVIEW_FINDINGS):
        errors.append("frozen_review_findings_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_review_only", True),
                      ("is_a_rescue_attempt", False)):
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
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C7R_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}
