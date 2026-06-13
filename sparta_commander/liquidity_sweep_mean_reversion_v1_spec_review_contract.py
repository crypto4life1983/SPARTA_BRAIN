"""SPARTA CANDIDATE #8 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY):
LIQUIDITY_SWEEP_MEAN_REVERSION_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC + BINARY form to
every rule of the Candidate #8 hypothesis -- before any detector
exists. Gated live on the pushed C8 family proposal, the pushed V3
rejected-family blacklist, the pushed Overnight Research Autopilot
V2, the pushed Recommendation V1, the pushed Autopilot Loop V1, and
the SEVEN-record rejection ledger (C1-C7 all REJECTED_KEPT_ON
_RECORD).

THE FROZEN NUMERICS:

  - universe: BTCUSD only (single symbol);
  - timeframe: 15m (completed bars only);
  - direction: long_only;
  - ATR length: 14 15m bars, standard true range;
  - range/swing-low lookback: 96 completed 15m bars -- the reference
    low used to define a sweep is the LOWEST low across the prior
    96 completed 15m bars ending at the bar BEFORE the sweep bar;
  - sweep penetration: the sweep bar's low must move at least
    0.25 x ATR(14) BELOW the reference low (computed at the sweep
    bar);
  - reclaim window: a completed 15m bar must close back ABOVE the
    swept reference level within 4 completed 15m bars after the
    sweep bar; the reclaim bar may equal the sweep bar's NEXT bar
    or any of the following three bars;
  - reclaim close rule: reclaim bar close strictly above the swept
    reference level;
  - close-in-upper-third confirmation: the reclaim bar's close must
    lie in the upper third of its own range
    (close >= low + (2/3) * (high - low));
  - entry: at the reclaim-confirmation bar's close (the event bar);
  - evaluation starts: the next 15m bar after the reclaim close;
  - structure stop: below the sweep low, with a buffer of
    0.20 x ATR(14) below the sweep low;
  - stop_distance = entry_price - (sweep_low - 0.20 * ATR14);
  - target variants: 2R, 3R, 4R only;
  - target_price = entry + r_multiple * stop_distance;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant (3 x round-trip) checked at label time before replay
    eligibility;
  - 8-bar anti-cluster gap per symbol at label-emission time, BEFORE
    replay-time non-overlap; tie-breaker keeps the earlier accepted
    event and drops the later same-symbol event within 8 bars. THIS
    IS PROPOSAL-LEVEL LOCKED AND NOT THE SINGLE C8 EDIT TOKEN;
  - sample-size adequacy: a MINIMUM of 20 accepted setups is required
    at the labels-review gate; below 20 triggers a structural
    rejection WITHOUT spending the single C8 edit token. THIS IS
    PROPOSAL-LEVEL LOCKED AND NOT THE SINGLE C8 EDIT TOKEN;
  - sample window: 2026-05-02_2026-06-10 (existing staged 15m
    candles);
  - existing staged BTCUSD 15m data only; NO fetch ever;
  - maximum one pre-committed edit for C8; the anti-cluster gap AND
    the sample-size threshold are BOTH proposal-level locked and
    NEITHER consumes the edit token.

THIS SPEC IS MATERIALLY DIFFERENT FROM C1-C7:
  - not session-anchored (NOT C1: no NY-session FVG/CHoCH);
  - not breakout-pullback (NOT C2);
  - not trend continuation (NOT C3);
  - not BTC/SOL or SOL/BTC swing-continuation coupling (NOT C4);
  - not relative-strength pullback continuation (NOT C5);
  - not multi-symbol rank/rotation (NOT C6);
  - not ATR compression/expansion trigger (NOT C7);
  - the EDGE HYPOTHESIS is a behavioral mean-reversion after a
    downside liquidity sweep then reclaim.

C6 ANTI-CLUSTER LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the 8-bar
minimum gap and tie-breaker are part of this spec review and do NOT
consume the single allowed C8 edit token. C7 SAMPLE-SIZE ADEQUACY
LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the minimum 20 accepted
setups threshold is part of this spec review and ALSO does NOT
consume the edit token. The single edit allowance is reserved for a
genuinely different structural parameter (e.g., the sweep penetration
multiplier, the reclaim window length, the structure-stop buffer
multiplier, or the range/swing-low lookback) if the initial replay
fails on a different failure mode.

Research-only and human-gated forever: NO detector implementation
here, NO real detection, NO labels, NO replay, NO artifacts, NO
runner or scheduler, NO paper/live, NO order/api/wallet/account/
credential capability, NO profitability claim.
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C8P_READY,
    build_candidate_8_family_proposal,
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
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C8S_SCHEMA_VERSION = (
    "liquidity_sweep_mean_reversion_v1_spec_review.v1")
C8S_LABEL = ("SPARTA Candidate #8 Strategy Spec Review "
             "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
             "NOT A RESCUE, NOT A CLAIM)")
C8S_MODE = "RESEARCH_ONLY"
VERDICT_C8S_READY = "CANDIDATE_8_SPEC_REVIEW_READY"
VERDICT_C8S_BLOCKED = "CANDIDATE_8_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_8_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1+2+3. universe, timeframe, direction -----------------------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "15m"
DIRECTION = "long_only"

# 4. ATR numerics ---------------------------------------------------------
ATR_LENGTH = 14
ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE = True

# 5. range/swing-low lookback ---------------------------------------------
RANGE_SWING_LOW_LOOKBACK_BARS = 96

# 6. sweep penetration -----------------------------------------------------
SWEEP_PENETRATION_ATR_MULTIPLIER = 0.25
SWEEP_RULE = {
    "rule": (
        "the sweep bar's low must be strictly less than the lowest "
        "low across the prior RANGE_SWING_LOW_LOOKBACK_BARS completed "
        "15m bars minus SWEEP_PENETRATION_ATR_MULTIPLIER x ATR(14)"),
    "range_swing_low_lookback_bars": RANGE_SWING_LOW_LOOKBACK_BARS,
    "sweep_penetration_atr_multiplier":
        SWEEP_PENETRATION_ATR_MULTIPLIER,
    "uses_completed_15m_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "strict_inequality_below_reference_minus_penetration": True,
}

# 7. reclaim window + reclaim close + upper-third -------------------------
RECLAIM_WINDOW_BARS = 4
CLOSE_IN_UPPER_THIRD_FRACTION = 2.0 / 3.0
RECLAIM_EVENT = {
    "rule": (
        "within RECLAIM_WINDOW_BARS completed 15m bars AFTER the "
        "sweep bar, a completed bar must close strictly ABOVE the "
        "swept reference level AND must have its close in the upper "
        "third of its own range (close >= low + (2/3) * "
        "(high - low)); the FIRST such bar in the window is the "
        "reclaim-confirmation bar"),
    "reclaim_window_bars": RECLAIM_WINDOW_BARS,
    "reclaim_close_strictly_above_swept_reference": True,
    "close_in_upper_third_required": True,
    "upper_third_fraction": CLOSE_IN_UPPER_THIRD_FRACTION,
    "entry_price": "close_of_the_reclaim_confirmation_bar",
    "evaluation_starts": "next_15m_bar_after_reclaim_close",
    "one_setup_per_sweep_event": True,
    "no_intrabar_entry": True,
}

# 8. structure-stop + buffer ----------------------------------------------
STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER = 0.20
STOP_RULE = {
    "atr_length": ATR_LENGTH,
    "atr_uses_completed_15m_bars_only_standard_true_range":
        ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE,
    "structure_stop_buffer_atr_multiplier":
        STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER,
    "stop_distance_formula": (
        "entry_price - (sweep_low - "
        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)"),
    "stop_price": "entry_price - stop_distance",
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
    "stop_must_be_below_sweep_low": True,
    "never_tightened_after_entry": True,
}

# 9. target variants ------------------------------------------------------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_RULES = {
    "variants": TARGET_VARIANTS,
    "no_new_variants_after_label_freeze": True,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
}

# 10. fee-aware geometry --------------------------------------------------
FEE_BPS = 27
FLOOR_BPS = 81
FEE_GEOMETRY = {
    "fee_model_round_trip_bps": FEE_BPS,
    "minimum_gross_target_distance_floor_bps": FLOOR_BPS,
    "floor_is_3x_round_trip_fees": True,
    "applies_per_target_variant": True,
    "checked_before_replay_eligibility": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# 11. anti-cluster (proposal-level locked policy; NOT the edit token) ----
ANTI_CLUSTER_MIN_BAR_GAP_15M = 8
ANTI_CLUSTER_POLICY = {
    "applied_at": "label_emission_time_before_replay_non_overlap",
    "scope": "per_symbol",
    "min_bars_between_same_symbol_accepted_events_15m":
        ANTI_CLUSTER_MIN_BAR_GAP_15M,
    "rationale": (
        "8 completed 15m bars equals two hours at the 15m timeframe "
        "and reflects the C6 lesson that dense same-symbol clusters "
        "waste replay-time non-overlap; locked at the proposal/spec "
        "level so it does NOT consume the single allowed C8 edit "
        "token"),
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "applies_to_all_variants_uniformly": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "leaves_staged_data_unchanged": True,
    "is_not_the_single_allowed_c8_edit_token": True,
}

# 12. sample-size adequacy (proposal-level locked; NOT the edit token) ---
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 20
SAMPLE_SIZE_ADEQUACY_POLICY = {
    "minimum_accepted_setups_required_at_labels_review_gate":
        SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED,
    "below_threshold_triggers_structural_rejection_without_edit_token":
        True,
    "rationale": (
        "the C7 lesson is that zero-setup strictness is a structural "
        "failure mode; the C8 proposal commits a minimum-evaluable-"
        "count threshold of 20 at the labels-review gate so a "
        "near-zero detection result is captured as a structural "
        "rejection without consuming the single edit token"),
    "applies_at_labels_review_gate": True,
    "is_not_the_single_allowed_c8_edit_token": True,
    "applies_before_any_edit_token_decision": True,
}

# 13. data boundary / sample window --------------------------------------
SAMPLE_TAG = "2026-05-02_2026-06-10"
DATA_BOUNDARY = {
    "source": ("existing append-only staged 15m candles only "
               "(data/ny_fvg_choch/staged/, sha-pinned manifests)"),
    "aggregation": "no_aggregation_needed_native_15m_data",
    "sample_tag": SAMPLE_TAG,
    "no_fetch_ever": True,
    "no_real_time_data": True,
    "staged_data_never_modified": True,
}

# 14. replay-time same-symbol non-overlap (inherited) --------------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
}

# 15. edit allowance ------------------------------------------------------
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_requires_separate_human_approval": True,
    "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token":
        True,
    "sample_size_threshold_is_proposal_level_locked_not_the_edit"
    "_token": True,
    "edit_must_target_a_different_structural_parameter": True,
}

# 16. material differences from C1-C7 -----------------------------------
MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES = (
    "not_session_anchored_no_ny_fvg_choch_dependency_NOT_c1",
    "not_breakout_pullback_continuation_NOT_c2",
    "not_trend_continuation_thesis_NOT_c3",
    "not_btc_sol_or_sol_btc_swing_continuation_coupling_NOT_c4",
    "no_relative_strength_comparison_NOT_c5",
    "no_multi_symbol_rank_or_rotation_NOT_c6",
    "no_atr_compression_or_expansion_trigger_NOT_c7",
)

# 17. inherited lessons --------------------------------------------------
INHERITED_LESSONS = (
    "c6_lesson_anti_cluster_protection_built_in_at_proposal_and_spec"
    "_level_not_consuming_edit_token",
    "c7_lesson_sample_size_adequacy_threshold_built_in_at_proposal"
    "_and_spec_level_not_consuming_edit_token",
)

# 18. claim locks --------------------------------------------------------
CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "promotion_can_only_produce_a_human_review_record",
    "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
    "sample_size_threshold_is_proposal_level_locked_not_edit_token",
)


def get_candidate_8_spec_review_label() -> str:
    return C8S_LABEL


def build_candidate_8_spec_review() -> dict[str, Any]:
    """Assemble the C8 spec review. Chain-gated on the seven-record
    ledger, the pushed C8 family proposal, the pushed V3 blacklist,
    the pushed V2, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": C8S_SCHEMA_VERSION, "label": C8S_LABEL,
        "mode": C8S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "atr_length": ATR_LENGTH,
        "atr_uses_completed_15m_bars_only_standard_true_range":
            ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE,
        "range_swing_low_lookback_bars": RANGE_SWING_LOW_LOOKBACK_BARS,
        "sweep_rule": dict(SWEEP_RULE),
        "reclaim_event": dict(RECLAIM_EVENT),
        "stop_rule": dict(STOP_RULE),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "fee_geometry": dict(FEE_GEOMETRY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "sample_size_adequacy_policy":
            dict(SAMPLE_SIZE_ADEQUACY_POLICY),
        "data_boundary": dict(DATA_BOUNDARY),
        "non_overlap": dict(NON_OVERLAP),
        "edit_policy": dict(EDIT_POLICY),
        "material_differences_from_rejected_families":
            list(MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES),
        "inherited_lessons": list(INHERITED_LESSONS),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "ledger_status_seven_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_spec_review_only": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_detector": False, "runs_real_candle_detection": False,
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
        "unlocks_detector_now": False, "unlocks_labels_now": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS)
    record["ledger_status_seven_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append("seven_record_ledger_broken")
        return record
    proposal = build_candidate_8_family_proposal()
    if proposal["verdict"] != VERDICT_C8P_READY:
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append("candidate_8_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C8S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C8S_READY
    return record


def validate_candidate_8_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C8S_READY, VERDICT_C8S_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "15m" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("range_swing_low_lookback_bars") != 96:
        errors.append("range_swing_low_lookback_must_be_96")
    if r.get(
            "atr_uses_completed_15m_bars_only_standard_true_range"
    ) is not True:
        errors.append("atr_lookahead_protection_weakened")
    sweep = r.get("sweep_rule") or {}
    if sweep != SWEEP_RULE:
        errors.append("sweep_rule_tampered")
    if sweep.get("sweep_penetration_atr_multiplier") != 0.25:
        errors.append("sweep_penetration_must_be_0_25")
    if sweep.get("range_swing_low_lookback_bars") != 96:
        errors.append("sweep_rule_lookback_must_be_96")
    if sweep.get(
            "uses_completed_15m_bars_only") is not True \
            or sweep.get("no_future_bars") is not True \
            or sweep.get("no_same_bar_lookahead") is not True \
            or sweep.get(
            "strict_inequality_below_reference_minus_penetration"
    ) is not True:
        errors.append("sweep_lookahead_or_strictness_weakened")
    reclaim = r.get("reclaim_event") or {}
    if reclaim != RECLAIM_EVENT:
        errors.append("reclaim_event_tampered")
    if reclaim.get("reclaim_window_bars") != 4:
        errors.append("reclaim_window_must_be_4")
    if reclaim.get(
            "reclaim_close_strictly_above_swept_reference") is not (
            True):
        errors.append("reclaim_close_above_reference_weakened")
    if reclaim.get("close_in_upper_third_required") is not True:
        errors.append("close_in_upper_third_weakened")
    if reclaim.get("upper_third_fraction") != (2.0 / 3.0):
        errors.append("upper_third_fraction_must_be_two_thirds")
    if reclaim.get("entry_price") != (
            "close_of_the_reclaim_confirmation_bar"):
        errors.append("entry_price_must_be_reclaim_confirmation_bar")
    if reclaim.get("evaluation_starts") != (
            "next_15m_bar_after_reclaim_close"):
        errors.append("evaluation_must_start_next_bar_after_reclaim")
    if reclaim.get("no_intrabar_entry") is not True:
        errors.append("intrabar_entry_must_be_forbidden")
    stop = r.get("stop_rule") or {}
    if stop != STOP_RULE:
        errors.append("stop_rule_tampered")
    if stop.get("atr_length") != 14:
        errors.append("stop_atr_length_must_be_14")
    if stop.get("structure_stop_buffer_atr_multiplier") != 0.20:
        errors.append("structure_stop_buffer_must_be_0_20")
    if stop.get("stop_distance_formula") != (
            "entry_price - (sweep_low - "
            "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)"):
        errors.append("stop_distance_formula_tampered")
    if stop.get("stop_must_be_below_entry") is not True \
            or stop.get("stop_must_be_below_sweep_low") is not True \
            or stop.get("never_tightened_after_entry") is not True \
            or stop.get(
            "invalid_if_stop_distance_not_positive") is not True:
        errors.append("stop_protection_weakened")
    targets = r.get("target_rules") or {}
    if targets.get("variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if targets.get("target_price_formula") != (
            "entry_price + r_multiple * stop_distance"):
        errors.append("target_price_formula_tampered")
    fee = r.get("fee_geometry") or {}
    if fee != FEE_GEOMETRY:
        errors.append("fee_geometry_tampered")
    if fee.get("fee_model_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if fee.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if fee.get("no_maker_rebate_assumption") is not True \
            or fee.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    anti = r.get("anti_cluster_policy") or {}
    if anti != ANTI_CLUSTER_POLICY:
        errors.append("anti_cluster_policy_tampered")
    if anti.get(
            "min_bars_between_same_symbol_accepted_events_15m") != 8:
        errors.append("anti_cluster_min_bars_must_be_8")
    if anti.get(
            "is_not_the_single_allowed_c8_edit_token") is not True:
        errors.append("anti_cluster_must_not_be_the_edit_token")
    if anti.get(
            "applies_before_replay_time_non_overlap") is not True \
            or anti.get(
            "replay_time_non_overlap_unchanged") is not True:
        errors.append("anti_cluster_replay_protection_weakened")
    if anti.get(
            "tie_breaker") != "keep_the_earlier_event_drop_the_later_one":
        errors.append("anti_cluster_tie_breaker_tampered")
    sa = r.get("sample_size_adequacy_policy") or {}
    if sa != SAMPLE_SIZE_ADEQUACY_POLICY:
        errors.append("sample_size_adequacy_policy_tampered")
    if sa.get(
            "minimum_accepted_setups_required_at_labels_review_gate"
    ) != 20:
        errors.append("sample_size_minimum_must_be_20")
    if sa.get(
            "below_threshold_triggers_structural_rejection_without"
            "_edit_token") is not True:
        errors.append(
            "sample_size_must_trigger_rejection_without_edit_token")
    if sa.get(
            "is_not_the_single_allowed_c8_edit_token") is not True:
        errors.append("sample_size_must_not_be_the_edit_token")
    boundary = r.get("data_boundary") or {}
    if boundary != DATA_BOUNDARY:
        errors.append("data_boundary_tampered")
    if boundary.get("sample_tag") != "2026-05-02_2026-06-10":
        errors.append("sample_tag_changed")
    if boundary.get("no_fetch_ever") is not True \
            or boundary.get("staged_data_never_modified") is not True:
        errors.append("data_boundary_weakened")
    if r.get("non_overlap") != NON_OVERLAP:
        errors.append("non_overlap_tampered")
    edit = r.get("edit_policy") or {}
    if edit != EDIT_POLICY:
        errors.append("edit_policy_tampered")
    if edit.get("maximum_pre_committed_edits") != 1 or edit.get(
            "edit_requires_separate_human_approval") is not True:
        errors.append("edit_policy_numerics_tampered")
    if edit.get(
            "anti_cluster_gap_is_proposal_level_locked_not_the_edit"
            "_token") is not True:
        errors.append(
            "anti_cluster_must_be_proposal_level_locked_not_edit_token")
    if edit.get(
            "sample_size_threshold_is_proposal_level_locked_not_the"
            "_edit_token") is not True:
        errors.append(
            "sample_size_must_be_proposal_level_locked_not_edit_token")
    if tuple(r.get("material_differences_from_rejected_families") or
             ()) != MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES:
        errors.append("material_differences_tampered")
    if tuple(r.get("inherited_lessons") or ()) != INHERITED_LESSONS:
        errors.append("inherited_lessons_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_loop_stage") != "detector_and_label_review":
        errors.append("next_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_a_rescue_attempt", False),
                      ("is_spec_review_only", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_detector", "runs_real_candle_detection",
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
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C8S_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
