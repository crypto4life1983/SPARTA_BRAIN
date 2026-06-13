"""SPARTA CANDIDATE #7 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY):
VOLATILITY_COMPRESSION_EXPANSION_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC + BINARY form to every
rule of the candidate #7 hypothesis -- before any detector exists.
Gated live on the pushed C7 family proposal, the pushed Overnight
Research Autopilot V2, the pushed Recommendation V1, the pushed
Autopilot Loop V1, and the SIX-record rejection ledger (C1-C6 all
REJECTED_KEPT_ON_RECORD).

THE FROZEN NUMERICS:

  - universe: BTCUSD only (single symbol);
  - timeframe: 4h (completed bars only);
  - direction: long_only;
  - ATR length: 14 4h bars, standard true range;
  - ATR rolling-average window: 100 completed 4h bars;
  - contraction fraction: ATR(14) must be < 0.6 x the 100-bar rolling
    average ATR for N consecutive completed bars;
  - contraction window N: 5 consecutive completed 4h bars;
  - expansion bar rule: the first completed 4h bar whose true range
    exceeds 1.8 x the contracted ATR while the rule below also holds;
  - close-in-upper-third confirmation: the expansion bar's close must
    lie in the upper third of its own range (close >= low + 2/3 *
    (high - low));
  - entry: at the expansion bar's close (event bar);
  - evaluation starts: the next 4h bar after the event close (no
    intrabar entry, no same-bar lookahead);
  - structure-stop lookback: 10 completed 4h bars;
  - WIDER stop distance: max(1.5 x ATR(14), entry - lowest low of the
    last 10 completed 4h bars); stop_price = entry - distance;
  - target variants: 2R, 3R, 4R only;
  - target_price = entry + r_multiple * stop_distance;
  - 27 bps round-trip fee model; 81 bps gross target-distance floor
    per variant (3 x round-trip), checked at label time before any
    replay eligibility; no maker rebate assumption; no zero-fee
    assumption;
  - anti-cluster policy (PROPOSAL-LEVEL, NOT THE EDIT TOKEN):
    minimum 6 completed 4h bars between accepted continuation events
    on the same symbol (= one trading day at 4h), applied at label
    emission time before replay-time non-overlap; tie-breaker keeps
    the earlier event;
  - replay-time same-symbol non-overlap remains unchanged per the
    pushed reduce-only policy;
  - sample window: 2026-05-02_2026-06-10 (the same staged 15m window
    used by C6, aggregated 15m -> 4h by the pushed aggregator);
  - existing staged 15m candles only; NO fetch ever.

C6 ANTI-CLUSTER LESSON IS PRE-COMMITTED HERE -- the 6-bar minimum gap
is locked at the spec-review level and DOES NOT consume the single
allowed C7 edit token. The single edit allowance is reserved for a
genuinely different structural parameter if the initial replay fails
on a different failure mode.

Research-only and human-gated forever: NO detector implementation
here, NO real detection, NO labels, NO replay, NO artifacts, NO runner
or scheduler, NO paper/live, NO order/api/wallet/account/credential
capability, NO profitability claim.
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

C7S_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_spec_review.v1")
C7S_LABEL = ("SPARTA Candidate #7 Strategy Spec Review "
             "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
             "NOT A RESCUE, NOT A CLAIM)")
C7S_MODE = "RESEARCH_ONLY"
VERDICT_C7S_READY = "CANDIDATE_7_SPEC_REVIEW_READY"
VERDICT_C7S_BLOCKED = "CANDIDATE_7_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_7_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1+2+3. universe, timeframe, direction -----------------------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "4h"
DIRECTION = "long_only"

# 4. ATR + rolling-average window numerics ------------------------------
ATR_LENGTH = 14
ATR_USES_COMPLETED_4H_BARS_ONLY_STANDARD_TRUE_RANGE = True
ATR_ROLLING_AVERAGE_WINDOW_4H_BARS = 100

# 5. contraction window numerics ----------------------------------------
CONTRACTION_FRACTION = 0.6
CONTRACTION_WINDOW_BARS = 5
CONTRACTION_RULE = {
    "rule": ("atr(14) must be strictly less than "
             "CONTRACTION_FRACTION times the 100-bar rolling average "
             "atr for CONTRACTION_WINDOW_BARS consecutive completed 4h "
             "bars ending at the bar immediately prior to the "
             "expansion event bar"),
    "contraction_fraction": CONTRACTION_FRACTION,
    "contraction_window_bars": CONTRACTION_WINDOW_BARS,
    "rolling_average_window_4h_bars":
        ATR_ROLLING_AVERAGE_WINDOW_4H_BARS,
    "uses_completed_4h_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "strict_inequality": True,
}

# 6. expansion event + close-in-upper-third confirmation ----------------
EXPANSION_TRUE_RANGE_MULTIPLIER = 1.8
CLOSE_IN_UPPER_THIRD_REQUIRED = True
EXPANSION_EVENT = {
    "rule": ("the first completed 4h bar whose true range exceeds "
             "EXPANSION_TRUE_RANGE_MULTIPLIER times the contracted "
             "atr AND whose close lies in the upper third of its own "
             "range (close >= low + 2/3 * (high - low))"),
    "expansion_true_range_multiplier": EXPANSION_TRUE_RANGE_MULTIPLIER,
    "close_in_upper_third_required": CLOSE_IN_UPPER_THIRD_REQUIRED,
    "contracted_atr_reference":
        "atr(14) at the bar immediately prior to this event bar",
    "entry_price": "close_of_the_event_bar",
    "evaluation_starts": "next_4h_bar_after_event_close",
    "one_setup_per_event_bar": True,
    "no_intrabar_entry": True,
}

# 7. wider-stop rule ----------------------------------------------------
STRUCTURE_STOP_LOOKBACK_BARS = 10
WIDER_STOP_ATR_MULTIPLIER = 1.5
STOP_RULE = {
    "atr_length": ATR_LENGTH,
    "atr_uses_completed_4h_bars_only_standard_true_range":
        ATR_USES_COMPLETED_4H_BARS_ONLY_STANDARD_TRUE_RANGE,
    "atr_multiplier": WIDER_STOP_ATR_MULTIPLIER,
    "structure_stop_distance": ("entry_price - lowest low of the last "
                                "STRUCTURE_STOP_LOOKBACK_BARS "
                                "completed 4h bars"),
    "structure_lookback_bars": STRUCTURE_STOP_LOOKBACK_BARS,
    "stop_distance":
        "max(WIDER_STOP_ATR_MULTIPLIER * atr14, "
        "structure_stop_distance)",
    "stop_price": "entry_price - stop_distance",
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
    "wider_stop_rule_mandatory_no_tightening": True,
}

# 8. target variants ----------------------------------------------------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_RULES = {
    "variants": TARGET_VARIANTS,
    "no_new_variants_after_label_freeze": True,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
}

# 9. fee-aware geometry -------------------------------------------------
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

# 10. anti-cluster (proposal-level locked policy, NOT the edit token) ---
ANTI_CLUSTER_MIN_BAR_GAP_4H = 6
ANTI_CLUSTER_POLICY = {
    "applied_at": "label_emission_time_before_replay_non_overlap",
    "scope": "per_symbol",
    "min_bars_between_same_symbol_accepted_events_4h":
        ANTI_CLUSTER_MIN_BAR_GAP_4H,
    "rationale": (
        "one trading day at the 4h timeframe; chosen because c6 "
        "spent its single edit on a clustering filter post-hoc and "
        "proved the structural cost of dense same-symbol setups; "
        "c7 locks this control at the proposal level so it does NOT "
        "consume the single allowed c7 edit token"),
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "applies_to_all_variants_uniformly": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "leaves_staged_data_unchanged": True,
    "is_not_the_single_allowed_c7_edit_token": True,
}

# 11. data boundary / sample window -------------------------------------
SAMPLE_TAG = "2026-05-02_2026-06-10"
DATA_BOUNDARY = {
    "source": ("existing append-only staged 15m candles only "
               "(data/ny_fvg_choch/staged/, sha-pinned manifests)"),
    "aggregation": ("15m to 4h by the pushed aggregator, complete "
                    "16-quarter-hours only"),
    "sample_tag": SAMPLE_TAG,
    "no_fetch_ever": True,
    "no_real_time_data": True,
    "staged_data_never_modified": True,
}

# 12. non-overlap (replay policy time; inherited) -----------------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
}

# 13. edit allowance (same one-token policy as C1-C6) -------------------
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_requires_separate_human_approval": True,
    "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token":
        True,
    "edit_must_target_a_different_structural_parameter_than_anti"
    "_cluster_gap_if_spent": True,
}

# 14. claim locks --------------------------------------------------------
CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "promotion_can_only_produce_a_human_review_record",
    "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
)


def get_candidate_7_spec_review_label() -> str:
    return C7S_LABEL


def build_candidate_7_spec_review() -> dict[str, Any]:
    """Assemble the C7 spec review. Chain-gated on the six-record
    ledger, the pushed C7 family proposal, the pushed Overnight
    Research Autopilot V2, the pushed Recommendation V1, and the
    pushed Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C7S_SCHEMA_VERSION, "label": C7S_LABEL,
        "mode": C7S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "atr_length": ATR_LENGTH,
        "atr_uses_completed_4h_bars_only_standard_true_range":
            ATR_USES_COMPLETED_4H_BARS_ONLY_STANDARD_TRUE_RANGE,
        "atr_rolling_average_window_4h_bars":
            ATR_ROLLING_AVERAGE_WINDOW_4H_BARS,
        "contraction_rule": dict(CONTRACTION_RULE),
        "expansion_event": dict(EXPANSION_EVENT),
        "stop_rule": dict(STOP_RULE),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "fee_geometry": dict(FEE_GEOMETRY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "data_boundary": dict(DATA_BOUNDARY),
        "non_overlap": dict(NON_OVERLAP),
        "edit_policy": dict(EDIT_POLICY),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "ledger_status_six_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_spec_review_only": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_detector": False,
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
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_detector_now": False, "unlocks_labels_now": False,
        "unlocks_replay_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS)
    record["ledger_status_six_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C7S_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    proposal = build_candidate_7_family_proposal()
    if proposal["verdict"] != VERDICT_C7P_READY:
        record["verdict"] = VERDICT_C7S_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    v2 = build_overnight_research_autopilot_v2_contract()
    if v2["verdict"] != VERDICT_OAP2_READY:
        record["verdict"] = VERDICT_C7S_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C7S_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C7S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C7S_READY
    return record


def validate_candidate_7_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C7S_READY, VERDICT_C7S_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "4h" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("atr_rolling_average_window_4h_bars") != 100:
        errors.append("atr_rolling_average_window_tampered")
    if r.get(
            "atr_uses_completed_4h_bars_only_standard_true_range"
    ) is not True:
        errors.append("atr_lookahead_protection_weakened")
    contraction = r.get("contraction_rule") or {}
    if contraction != CONTRACTION_RULE:
        errors.append("contraction_rule_tampered")
    if contraction.get("contraction_fraction") != 0.6:
        errors.append("contraction_fraction_must_be_0_6")
    if contraction.get("contraction_window_bars") != 5:
        errors.append("contraction_window_must_be_5")
    if contraction.get(
            "uses_completed_4h_bars_only") is not True \
            or contraction.get("no_future_bars") is not True \
            or contraction.get("no_same_bar_lookahead") is not True \
            or contraction.get("strict_inequality") is not True:
        errors.append("contraction_lookahead_protection_weakened")
    expansion = r.get("expansion_event") or {}
    if expansion != EXPANSION_EVENT:
        errors.append("expansion_event_tampered")
    if expansion.get("expansion_true_range_multiplier") != 1.8:
        errors.append("expansion_multiplier_must_be_1_8")
    if expansion.get("close_in_upper_third_required") is not True:
        errors.append("close_in_upper_third_required_weakened")
    if expansion.get("entry_price") != "close_of_the_event_bar":
        errors.append("entry_price_must_be_event_bar_close")
    if expansion.get("evaluation_starts") != (
            "next_4h_bar_after_event_close"):
        errors.append("evaluation_must_start_next_bar_after_event")
    if expansion.get("no_intrabar_entry") is not True:
        errors.append("intrabar_entry_must_be_forbidden")
    stop = r.get("stop_rule") or {}
    if stop != STOP_RULE:
        errors.append("stop_rule_tampered")
    if stop.get("atr_length") != 14 or stop.get("atr_multiplier") != 1.5:
        errors.append("stop_numbers_missing_or_altered")
    if stop.get("structure_lookback_bars") != 10:
        errors.append("structure_lookback_must_be_10")
    if stop.get("stop_distance") != (
            "max(WIDER_STOP_ATR_MULTIPLIER * atr14, "
            "structure_stop_distance)") \
            or stop.get(
            "wider_stop_rule_mandatory_no_tightening") is not True:
        errors.append("wider_stop_rule_missing_or_altered")
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
            "min_bars_between_same_symbol_accepted_events_4h") != 6:
        errors.append("anti_cluster_min_bars_must_be_6")
    if anti.get(
            "is_not_the_single_allowed_c7_edit_token") is not True:
        errors.append("anti_cluster_must_not_be_the_edit_token")
    if anti.get(
            "applies_before_replay_time_non_overlap") is not True \
            or anti.get(
            "replay_time_non_overlap_unchanged") is not True:
        errors.append("anti_cluster_replay_protection_weakened")
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
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C7S_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
