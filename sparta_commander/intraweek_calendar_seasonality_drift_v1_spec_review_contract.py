"""SPARTA CANDIDATE #10 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY): INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC + BINARY form to
every rule of the Candidate #10 hypothesis -- before any detector
exists. Gated live on the pushed C10 family proposal, the pushed V5
rejected-family blacklist, the pushed V4 blacklist, the pushed V3
blacklist, the pushed V2 overnight autopilot, the pushed
Recommendation V1, the pushed Autopilot Loop V1, and the NINE-record
rejection ledger (C1-C9 all REJECTED_KEPT_ON_RECORD).

THE FROZEN NUMERICS:

  - universe: BTCUSD only (single symbol);
  - timeframe: 1d (completed daily bars only);
  - direction: long_only;
  - trigger: a SINGLE deterministic calendar condition -- the
    completed daily bar's ISO weekday index equals the pre-selected
    favorable weekday bucket. NO price-pattern, NO volume, NO
    statistical-excursion condition participates. The clock is the
    whole signal;
  - favorable weekday bucket cardinality: 1 (a single ISO weekday,
    not a pair);
  - favorable-bucket selection rule: the single ISO weekday whose
    mean fixed-horizon forward log return over the IN-SAMPLE
    selection window is the HIGHEST AND clears the 81 bps gross
    target-distance floor; the bucket VALUE is data-determined on the
    in-sample window and then held FIXED for the out-of-sample
    window (it is NOT hard-coded in this spec);
  - in-sample selection window: 2019-01-01_2022-12-31;
  - out-of-sample window: 2023-01-01_2025-12-31;
  - entry: a long entry at the CLOSE of the triggering completed
    daily bar. NO intrabar entry. NO same-bar lookahead;
  - evaluation starts: the bar IMMEDIATELY AFTER the entry bar's
    close;
  - holding horizon (fixed-horizon exit): 5 completed daily bars
    after entry (one trading week), exit at that bar's close;
  - ATR length: 14 daily bars, standard true range (risk-control
    only -- ATR is used for the protective stop distance, never as an
    entry trigger);
  - structure stop: stop_price = entry_price -
    STRUCTURE_STOP_ATR_MULTIPLIER (1.5) x ATR(14) at the entry bar;
    stop_distance = entry_price - stop_price; INVALID if
    stop_distance <= 0 OR stop_price is not below entry_price;
  - stop is NEVER tightened after entry;
  - target variants: 2R, 3R, 4R only; target_price = entry_price +
    r_multiple x stop_distance;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant (3 x round-trip) checked at label time before replay
    eligibility;
  - anti-cluster: a weekday bucket fires AT MOST ONCE per ISO week by
    construction, plus a 5-daily-bar (one-week) minimum gap per
    symbol at label-emission time, BEFORE replay-time non-overlap;
    tie-breaker keeps the earlier accepted event. THE CALENDAR IS THE
    PRIMARY ANTI-CLUSTER CONSTRAINT. THIS IS PROPOSAL-LEVEL LOCKED AND
    NOT THE SINGLE C10 EDIT TOKEN;
  - sample-size adequacy: a MINIMUM of 100 accepted setups is
    required at the labels-review gate; below 100 triggers a
    structural rejection WITHOUT spending the single C10 edit token.
    A weekday bucket recurs every ISO week, so a multi-year daily
    window yields hundreds of occurrences by construction. THIS IS
    PROPOSAL-LEVEL LOCKED AND NOT THE SINGLE C10 EDIT TOKEN;
  - sample window: 2019-01-01_2025-12-31 (the staged BTCUSD daily
    candles);
  - existing staged BTCUSD daily data only; NO fetch ever;
  - maximum one pre-committed edit for C10; the anti-cluster gap, the
    sample-size threshold, the explicit-edge-argument field, AND the
    single-trigger design are ALL proposal-level locked and NONE
    consumes the edit token.

THIS SPEC IS MATERIALLY DIFFERENT FROM C1-C9:
  - not session-anchored (NOT C1: no NY-session FVG/CHoCH);
  - not breakout-pullback (NOT C2);
  - not trend continuation (NOT C3);
  - not BTC/SOL or SOL/BTC swing-continuation coupling (NOT C4);
  - not relative-strength pullback continuation (NOT C5);
  - not multi-symbol rank/rotation (NOT C6);
  - not ATR compression/expansion trigger (NOT C7);
  - not liquidity-sweep-then-reclaim geometry (NOT C8);
  - not a joint price-AND-volume downside-capitulation excursion
    (NOT C9);
  - the EDGE HYPOTHESIS is an exogenous calendar risk premium driven
    by recurring weekly liquidity and flow cycles, signalled by a
    SINGLE deterministic ISO-weekday calendar condition on a completed
    daily bar -- the conditioning variable is the clock, orthogonal
    to every price and volume condition tried in C1-C9.

C6 ANTI-CLUSTER LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the one-fire-
per-ISO-week construction plus the 5-bar minimum gap are part of this
spec review and do NOT consume the single allowed C10 edit token. C7
SAMPLE-SIZE ADEQUACY LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the
minimum 100 accepted setups threshold is part of this spec review and
ALSO does NOT consume the edit token. C8 EXPLICIT-EDGE-ARGUMENT LESSON
IS PROPOSAL-LEVEL LOCKED HERE -- the V5-required calendar-risk-premium
claim field is carried forward and does NOT consume the edit token. C9
SINGLE-TRIGGER LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the deliberate
single deterministic calendar trigger (no intersection of conditions)
does NOT consume the edit token either. The single edit allowance is
reserved for a genuinely different structural parameter (the favorable
weekday bucket selection window, the holding horizon, the favorable-
bucket cardinality, or the structure-stop ATR multiplier) if the
initial replay fails on a different failure mode.

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
from sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
    VERDICT_C10P_READY,
    build_candidate_10_family_proposal,
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

C10S_SCHEMA_VERSION = (
    "intraweek_calendar_seasonality_drift_v1_spec_review.v1")
C10S_LABEL = ("SPARTA Candidate #10 Strategy Spec Review "
              "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
              "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY "
              "CARRIED FORWARD FROM C10 PROPOSAL, SINGLE-TRIGGER "
              "DESIGN, NOT A RESCUE, NOT A CLAIM)")
C10S_MODE = "RESEARCH_ONLY"
VERDICT_C10S_READY = "CANDIDATE_10_SPEC_REVIEW_READY"
VERDICT_C10S_BLOCKED = "CANDIDATE_10_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_10_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1+2+3. universe, timeframe, direction -----------------------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "1d"
DIRECTION = "long_only"

# 4. favorable weekday bucket selection -----------------------------------
FAVORABLE_WEEKDAY_BUCKET_CARDINALITY = 1
IN_SAMPLE_SELECTION_WINDOW = "2019-01-01_2022-12-31"
OUT_OF_SAMPLE_WINDOW = "2023-01-01_2025-12-31"

# 5. single deterministic calendar trigger --------------------------------
CALENDAR_TRIGGER_RULE = {
    "rule": (
        "the completed daily bar's ISO weekday index "
        "(Monday=1 ... Sunday=7) must EQUAL the pre-selected "
        "favorable weekday bucket; the bucket is selected "
        "deterministically on the IN-SAMPLE window and then held "
        "FIXED for the out-of-sample window; NO price-pattern, NO "
        "volume, and NO statistical-excursion condition participates "
        "in the trigger -- the clock is the whole signal"),
    "favorable_weekday_bucket_cardinality":
        FAVORABLE_WEEKDAY_BUCKET_CARDINALITY,
    "selection_metric": (
        "highest_in_sample_mean_fixed_horizon_forward_log_return"
        "_among_iso_weekdays_that_clears_the_81_bps_gross_floor"),
    "in_sample_selection_window": IN_SAMPLE_SELECTION_WINDOW,
    "out_of_sample_window": OUT_OF_SAMPLE_WINDOW,
    "bucket_value_is_data_determined_not_hardcoded": True,
    "is_a_single_deterministic_calendar_trigger": True,
    "uses_completed_daily_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "uses_no_price_pattern_condition": True,
    "uses_no_volume_condition": True,
    "uses_no_statistical_excursion_condition": True,
}

# 6. entry rule -----------------------------------------------------------
ENTRY_RULE = {
    "rule": (
        "long entry is at the CLOSE of the triggering completed "
        "daily bar; no intrabar entry; no same-bar lookahead; "
        "evaluation of the outcome starts on the next completed "
        "daily bar after the entry bar's close"),
    "entry_price": "close_of_the_triggering_completed_daily_bar",
    "no_intrabar_entry": True,
    "no_same_bar_lookahead": True,
    "evaluation_starts": "next_daily_bar_after_entry_bar_close",
}

# 7. fixed-horizon exit ---------------------------------------------------
HOLDING_HORIZON_BARS = 5
EXIT_RULE = {
    "rule": (
        "close the long at the CLOSE of the daily bar "
        "HOLDING_HORIZON_BARS completed daily bars after the entry "
        "bar (a one-trading-week fixed horizon); a structural "
        "protective stop a frozen distance below entry invalidates "
        "the setup if hit first"),
    "holding_horizon_bars": HOLDING_HORIZON_BARS,
    "applied_at_replay_time": True,
    "is_not_an_entry_gate_rule": True,
}

# 8. structure-stop rule (risk-control only; not an entry trigger) --------
ATR_LENGTH = 14
ATR_USES_COMPLETED_DAILY_BARS_ONLY_STANDARD_TRUE_RANGE = True
STRUCTURE_STOP_ATR_MULTIPLIER = 1.5
STOP_RULE = {
    "atr_length": ATR_LENGTH,
    "atr_uses_completed_daily_bars_only_standard_true_range":
        ATR_USES_COMPLETED_DAILY_BARS_ONLY_STANDARD_TRUE_RANGE,
    "structure_stop_atr_multiplier": STRUCTURE_STOP_ATR_MULTIPLIER,
    "stop_price_formula": (
        "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
        "ATR14_at_entry_bar"),
    "stop_distance_formula": "entry_price - stop_price",
    "stop_is_risk_control_only_not_an_entry_trigger": True,
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
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

# 11. anti-cluster (proposal-level locked policy; NOT the edit token) -----
ANTI_CLUSTER_MIN_BAR_GAP_1D = 5
ANTI_CLUSTER_POLICY = {
    "applied_at": "label_emission_time_before_replay_non_overlap",
    "scope": "per_symbol",
    "min_bars_between_same_symbol_accepted_events_1d":
        ANTI_CLUSTER_MIN_BAR_GAP_1D,
    "one_fire_per_iso_week_by_construction": True,
    "calendar_is_the_primary_anti_cluster_constraint": True,
    "rationale": (
        "a single weekday bucket fires at most once per ISO week by "
        "construction; the 5-daily-bar (one-week) minimum gap "
        "reflects the C6 lesson that dense same-symbol clusters "
        "waste replay-time non-overlap; the calendar is the primary "
        "anti-cluster constraint, locked at the proposal/spec level "
        "so it does NOT consume the single allowed C10 edit token"),
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "applies_to_all_variants_uniformly": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "leaves_staged_data_unchanged": True,
    "is_not_the_single_allowed_c10_edit_token": True,
}

# 12. sample-size adequacy (proposal-level locked; NOT the edit token) ---
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 100
SAMPLE_SIZE_ADEQUACY_POLICY = {
    "minimum_accepted_setups_required_at_labels_review_gate":
        SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED,
    "below_threshold_triggers_structural_rejection_without_edit"
    "_token": True,
    "rationale": (
        "the C7 lesson is that zero/near-zero accepted setups is a "
        "structural failure mode and the C9 lesson is that an overly "
        "narrow intersection of triggers thins the sample; C10 uses "
        "a SINGLE deterministic calendar trigger that recurs every "
        "ISO week, so a multi-year daily window yields hundreds of "
        "occurrences by construction; the 100-setup minimum captures "
        "a structural rejection without consuming the single edit "
        "token"),
    "sample_is_abundant_by_construction_a_bucket_recurs_every_iso"
    "_week": True,
    "applies_at_labels_review_gate": True,
    "is_not_the_single_allowed_c10_edit_token": True,
    "applies_before_any_edit_token_decision": True,
}

# 13. explicit edge argument (V5-required; proposal-level locked) --------
EXPLICIT_EDGE_ARGUMENT_POLICY = {
    "carried_forward_from_c10_family_proposal": True,
    "v5_required_field": True,
    "argument_is_a_calendar_risk_premium_not_visual": True,
    "argument_is_orthogonal_to_all_price_and_volume_conditions": True,
    "argument_is_falsifiable_by_per_bucket_per_variant_net_r_sums":
        True,
    "is_not_the_single_allowed_c10_edit_token": True,
    "rationale": (
        "the C8 lesson is that structural cleanliness alone does not "
        "produce edge; the V5 blacklist requires every C9+ proposal "
        "to include an explicit edge argument beyond pattern "
        "geometry; the C10 proposal supplied a six-point calendar-"
        "risk-premium argument and the spec review carries it "
        "forward unchanged"),
}

# 14. single-trigger design (C9-lesson; proposal-level locked) -----------
SINGLE_TRIGGER_POLICY = {
    "design_is_single_deterministic_trigger": True,
    "no_intersection_of_trigger_conditions": True,
    "intersection_sparsity_failure_cannot_occur": True,
    "future_second_intersecting_condition_requires_separate_pre"
    "_justification": True,
    "is_not_the_single_allowed_c10_edit_token": True,
    "rationale": (
        "the C9 lesson is that a joint price-AND-volume intersection "
        "was too sparse to reach an adequate accepted-setup count; "
        "C10 deliberately uses ONE deterministic calendar condition "
        "with no intersection, so the intersection-sparsity failure "
        "mode cannot occur; this single-trigger choice is locked at "
        "the proposal/spec level and does NOT consume the edit "
        "token"),
}

# 15. data boundary / sample window --------------------------------------
SAMPLE_TAG = "2019-01-01_2025-12-31"
DATA_BOUNDARY = {
    "source": ("existing append-only staged BTCUSD 1d candles only, "
               "sha-pinned at runtime by the future detection "
               "runner"),
    "aggregation": "no_aggregation_needed_native_1d_data",
    "sample_tag": SAMPLE_TAG,
    "in_sample_selection_window": IN_SAMPLE_SELECTION_WINDOW,
    "out_of_sample_window": OUT_OF_SAMPLE_WINDOW,
    "no_fetch_ever": True,
    "no_real_time_data": True,
    "staged_data_never_modified": True,
    "consumes_calendar_weekday_index_as_a_new_exogenous_input_for"
    "_the_first_time_in_lane": True,
}

# 16. replay-time same-symbol non-overlap (inherited) -------------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
}

# 17. edit allowance -----------------------------------------------------
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_requires_separate_human_approval": True,
    "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token":
        True,
    "sample_size_threshold_is_proposal_level_locked_not_the_edit"
    "_token": True,
    "explicit_edge_argument_field_is_proposal_level_locked_not_the"
    "_edit_token": True,
    "single_trigger_design_is_proposal_level_locked_not_the_edit"
    "_token": True,
    "edit_must_target_a_different_structural_parameter": True,
    "edit_token_eligible_parameters": (
        "FAVORABLE_WEEKDAY_BUCKET_SELECTION_WINDOW",
        "HOLDING_HORIZON_BARS",
        "FAVORABLE_WEEKDAY_BUCKET_CARDINALITY",
        "STRUCTURE_STOP_ATR_MULTIPLIER"),
}

# 18. material differences from C1-C9 -----------------------------------
MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES = (
    "not_session_anchored_no_ny_fvg_choch_dependency_NOT_c1",
    "not_breakout_pullback_continuation_NOT_c2",
    "not_trend_continuation_thesis_NOT_c3",
    "not_btc_sol_or_sol_btc_swing_continuation_coupling_NOT_c4",
    "no_relative_strength_pullback_continuation_NOT_c5",
    "no_multi_symbol_rank_or_rotation_NOT_c6",
    "no_atr_compression_or_expansion_trigger_NOT_c7",
    "no_sweep_below_prior_low_geometry_no_reclaim_window_NOT_c8",
    "no_volume_condition_no_downside_zscore_no_excursion_reversion"
    "_NOT_c9",
)

# 19. inherited lessons -------------------------------------------------
INHERITED_LESSONS = (
    "c6_lesson_anti_cluster_protection_built_in_at_proposal_and"
    "_spec_level_not_consuming_edit_token",
    "c7_lesson_sample_size_adequacy_threshold_built_in_at_proposal"
    "_and_spec_level_not_consuming_edit_token",
    "c8_lesson_explicit_edge_argument_beyond_pattern_geometry_built"
    "_in_at_proposal_and_spec_level_not_consuming_edit_token",
    "c9_lesson_single_deterministic_trigger_design_built_in_at"
    "_proposal_and_spec_level_not_consuming_edit_token",
)

# 20. claim locks -------------------------------------------------------
CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "promotion_can_only_produce_a_human_review_record",
    "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
    "sample_size_threshold_is_proposal_level_locked_not_edit_token",
    "explicit_edge_argument_field_is_proposal_level_locked_not_edit"
    "_token",
    "single_trigger_design_is_proposal_level_locked_not_edit_token",
)


def get_candidate_10_spec_review_label() -> str:
    return C10S_LABEL


def build_candidate_10_spec_review() -> dict[str, Any]:
    """Assemble the C10 spec review. Chain-gated on the nine-record
    ledger, the pushed C10 family proposal, the pushed V5 blacklist,
    the pushed V4, V3, V2, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": C10S_SCHEMA_VERSION, "label": C10S_LABEL,
        "mode": C10S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "favorable_weekday_bucket_cardinality":
            FAVORABLE_WEEKDAY_BUCKET_CARDINALITY,
        "in_sample_selection_window": IN_SAMPLE_SELECTION_WINDOW,
        "out_of_sample_window": OUT_OF_SAMPLE_WINDOW,
        "calendar_trigger_rule": dict(CALENDAR_TRIGGER_RULE),
        "entry_rule": dict(ENTRY_RULE),
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "exit_rule": dict(EXIT_RULE),
        "atr_length": ATR_LENGTH,
        "atr_uses_completed_daily_bars_only_standard_true_range":
            ATR_USES_COMPLETED_DAILY_BARS_ONLY_STANDARD_TRUE_RANGE,
        "structure_stop_atr_multiplier":
            STRUCTURE_STOP_ATR_MULTIPLIER,
        "stop_rule": dict(STOP_RULE),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "fee_geometry": dict(FEE_GEOMETRY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "sample_size_adequacy_policy":
            dict(SAMPLE_SIZE_ADEQUACY_POLICY),
        "explicit_edge_argument_policy":
            dict(EXPLICIT_EDGE_ARGUMENT_POLICY),
        "explicit_edge_argument_beyond_pattern_geometry_carried"
        "_forward": EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
        "single_trigger_policy": dict(SINGLE_TRIGGER_POLICY),
        "data_boundary": dict(DATA_BOUNDARY),
        "non_overlap": dict(NON_OVERLAP),
        "edit_policy": {
            "maximum_pre_committed_edits":
                EDIT_POLICY["maximum_pre_committed_edits"],
            "edit_requires_separate_human_approval":
                EDIT_POLICY["edit_requires_separate_human_approval"],
            "anti_cluster_gap_is_proposal_level_locked_not_the_edit"
            "_token":
                EDIT_POLICY[
                    "anti_cluster_gap_is_proposal_level_locked_not"
                    "_the_edit_token"],
            "sample_size_threshold_is_proposal_level_locked_not_the"
            "_edit_token":
                EDIT_POLICY[
                    "sample_size_threshold_is_proposal_level_locked"
                    "_not_the_edit_token"],
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_the_edit_token":
                EDIT_POLICY[
                    "explicit_edge_argument_field_is_proposal_level"
                    "_locked_not_the_edit_token"],
            "single_trigger_design_is_proposal_level_locked_not_the"
            "_edit_token":
                EDIT_POLICY[
                    "single_trigger_design_is_proposal_level_locked"
                    "_not_the_edit_token"],
            "edit_must_target_a_different_structural_parameter":
                EDIT_POLICY[
                    "edit_must_target_a_different_structural"
                    "_parameter"],
            "edit_token_eligible_parameters":
                list(EDIT_POLICY["edit_token_eligible_parameters"])},
        "material_differences_from_rejected_families":
            list(MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES),
        "inherited_lessons": list(INHERITED_LESSONS),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "candidate_10_proposal_verdict": None,
        "v5_blacklist_verdict": None,
        "v4_blacklist_verdict": None,
        "v3_blacklist_verdict": None,
        "v2_verdict": None,
        "recommendation_verdict": None,
        "autopilot_loop_verdict": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_spec_review_only": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_detector": False, "runs_real_candle_detection": False,
        "runs_dry_run": False,
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
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "uses_external_data_source": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading":
            False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_detector_now": False, "unlocks_labels_now": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    proposal = build_candidate_10_family_proposal()
    record["candidate_10_proposal_verdict"] = proposal["verdict"]
    if proposal["verdict"] != VERDICT_C10P_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append(
            "candidate_10_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    v5 = build_rejected_family_blacklist_v5()
    record["v5_blacklist_verdict"] = v5["verdict"]
    if v5["verdict"] != VERDICT_BL5_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    v4 = build_rejected_family_blacklist_v4()
    record["v4_blacklist_verdict"] = v4["verdict"]
    if v4["verdict"] != VERDICT_BL4_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    v3 = build_rejected_family_blacklist_v3()
    record["v3_blacklist_verdict"] = v3["verdict"]
    if v3["verdict"] != VERDICT_BL3_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    v2 = build_overnight_research_autopilot_v2_contract()
    record["v2_verdict"] = v2["verdict"]
    if v2["verdict"] != VERDICT_OAP2_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    recommendation = _rec.build_candidate_recommendation()
    record["recommendation_verdict"] = recommendation["verdict"]
    if recommendation["verdict"] != _rec.VERDICT_CR_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    record["autopilot_loop_verdict"] = loop_contract["verdict"]
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C10S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C10S_READY
    return record


def validate_candidate_10_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C10S_READY,
                                VERDICT_C10S_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "1d" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("favorable_weekday_bucket_cardinality") != 1:
        errors.append("favorable_weekday_bucket_cardinality_must_be_1")
    if r.get("in_sample_selection_window") != (
            IN_SAMPLE_SELECTION_WINDOW):
        errors.append("in_sample_selection_window_tampered")
    if r.get("out_of_sample_window") != OUT_OF_SAMPLE_WINDOW:
        errors.append("out_of_sample_window_tampered")
    ct = r.get("calendar_trigger_rule") or {}
    if ct != CALENDAR_TRIGGER_RULE:
        errors.append("calendar_trigger_rule_tampered")
    if ct.get("is_a_single_deterministic_calendar_trigger") is not (
            True):
        errors.append("trigger_must_be_single_deterministic_calendar")
    if ct.get("uses_no_price_pattern_condition") is not True \
            or ct.get("uses_no_volume_condition") is not True \
            or ct.get("uses_no_statistical_excursion_condition") is (
            not True):
        errors.append("trigger_purity_weakened")
    if ct.get("no_same_bar_lookahead") is not True \
            or ct.get("no_future_bars") is not True:
        errors.append("trigger_lookahead_protection_weakened")
    er = r.get("entry_rule") or {}
    if er != ENTRY_RULE:
        errors.append("entry_rule_tampered")
    if er.get("entry_price") != (
            "close_of_the_triggering_completed_daily_bar"):
        errors.append("entry_must_be_close_of_triggering_bar")
    if er.get("no_intrabar_entry") is not True \
            or er.get("no_same_bar_lookahead") is not True:
        errors.append("intrabar_or_same_bar_entry_must_be_forbidden")
    if r.get("holding_horizon_bars") != 5:
        errors.append("holding_horizon_bars_must_be_5")
    xr = r.get("exit_rule") or {}
    if xr != EXIT_RULE:
        errors.append("exit_rule_tampered")
    if xr.get("holding_horizon_bars") != 5:
        errors.append("exit_holding_horizon_must_be_5")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get(
            "atr_uses_completed_daily_bars_only_standard_true_range"
    ) is not True:
        errors.append("atr_lookahead_protection_weakened")
    if r.get("structure_stop_atr_multiplier") != 1.5:
        errors.append("structure_stop_atr_multiplier_must_be_1_5")
    stop = r.get("stop_rule") or {}
    if stop != STOP_RULE:
        errors.append("stop_rule_tampered")
    if stop.get("structure_stop_atr_multiplier") != 1.5:
        errors.append("stop_atr_multiplier_must_be_1_5")
    if stop.get("stop_price_formula") != (
            "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
            "ATR14_at_entry_bar"):
        errors.append("stop_price_formula_tampered")
    if stop.get("stop_must_be_below_entry") is not True \
            or stop.get("never_tightened_after_entry") is not True \
            or stop.get("invalid_if_stop_distance_not_positive") is (
            not True):
        errors.append("stop_protection_weakened")
    if stop.get(
            "stop_is_risk_control_only_not_an_entry_trigger") is not (
            True):
        errors.append("stop_must_remain_risk_control_only")
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
            "min_bars_between_same_symbol_accepted_events_1d") != 5:
        errors.append("anti_cluster_min_bars_must_be_5")
    if anti.get("one_fire_per_iso_week_by_construction") is not True \
            or anti.get(
            "calendar_is_the_primary_anti_cluster_constraint") is not (
            True):
        errors.append("anti_cluster_calendar_construction_weakened")
    if anti.get(
            "is_not_the_single_allowed_c10_edit_token") is not True:
        errors.append("anti_cluster_must_not_be_the_edit_token")
    if anti.get(
            "applies_before_replay_time_non_overlap") is not True \
            or anti.get(
            "replay_time_non_overlap_unchanged") is not True:
        errors.append("anti_cluster_replay_protection_weakened")
    if anti.get(
            "tie_breaker") != (
            "keep_the_earlier_event_drop_the_later_one"):
        errors.append("anti_cluster_tie_breaker_tampered")
    sa = r.get("sample_size_adequacy_policy") or {}
    if sa != SAMPLE_SIZE_ADEQUACY_POLICY:
        errors.append("sample_size_adequacy_policy_tampered")
    if sa.get(
            "minimum_accepted_setups_required_at_labels_review_gate"
    ) != 100:
        errors.append("sample_size_minimum_must_be_100")
    if sa.get(
            "below_threshold_triggers_structural_rejection_without"
            "_edit_token") is not True:
        errors.append(
            "sample_size_must_trigger_rejection_without_edit_token")
    if sa.get(
            "is_not_the_single_allowed_c10_edit_token") is not True:
        errors.append("sample_size_must_not_be_the_edit_token")
    eep = r.get("explicit_edge_argument_policy") or {}
    if eep != EXPLICIT_EDGE_ARGUMENT_POLICY:
        errors.append("explicit_edge_argument_policy_tampered")
    if eep.get("v5_required_field") is not True:
        errors.append("explicit_edge_argument_must_be_v5_required")
    if eep.get(
            "is_not_the_single_allowed_c10_edit_token") is not True:
        errors.append(
            "explicit_edge_argument_must_not_be_the_edit_token")
    if r.get(
            "explicit_edge_argument_beyond_pattern_geometry_carried"
            "_forward") != (
            EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY):
        errors.append("explicit_edge_argument_carried_forward_tampered")
    stp = r.get("single_trigger_policy") or {}
    if stp != SINGLE_TRIGGER_POLICY:
        errors.append("single_trigger_policy_tampered")
    if stp.get("design_is_single_deterministic_trigger") is not True \
            or stp.get(
            "no_intersection_of_trigger_conditions") is not True:
        errors.append("single_trigger_design_weakened")
    if stp.get(
            "is_not_the_single_allowed_c10_edit_token") is not True:
        errors.append("single_trigger_design_must_not_be_edit_token")
    boundary = r.get("data_boundary") or {}
    if boundary != DATA_BOUNDARY:
        errors.append("data_boundary_tampered")
    if boundary.get("sample_tag") != "2019-01-01_2025-12-31":
        errors.append("sample_tag_changed")
    if boundary.get("no_fetch_ever") is not True \
            or boundary.get("staged_data_never_modified") is not True:
        errors.append("data_boundary_weakened")
    if r.get("non_overlap") != NON_OVERLAP:
        errors.append("non_overlap_tampered")
    edit = r.get("edit_policy") or {}
    if edit.get("maximum_pre_committed_edits") != 1 \
            or edit.get(
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
    if edit.get(
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_the_edit_token") is not True:
        errors.append(
            "explicit_edge_argument_must_be_proposal_level_locked_not"
            "_edit_token")
    if edit.get(
            "single_trigger_design_is_proposal_level_locked_not_the"
            "_edit_token") is not True:
        errors.append(
            "single_trigger_design_must_be_proposal_level_locked_not"
            "_edit_token")
    if tuple(edit.get("edit_token_eligible_parameters") or ()) != (
            EDIT_POLICY["edit_token_eligible_parameters"]):
        errors.append("edit_token_eligible_parameters_tampered")
    if tuple(r.get("material_differences_from_rejected_families")
             or ()) != MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES:
        errors.append("material_differences_tampered")
    if tuple(r.get("inherited_lessons") or ()) != INHERITED_LESSONS:
        errors.append("inherited_lessons_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("current_loop_stage") != "candidate_spec":
        errors.append("current_stage_tampered")
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
                "runs_dry_run",
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
                "uses_external_data_source",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C10S_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
