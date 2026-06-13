"""SPARTA CANDIDATE #9 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC + BINARY form to
every rule of the Candidate #9 hypothesis -- before any detector
exists. Gated live on the pushed C9 family proposal, the pushed V4
rejected-family blacklist, the pushed V3 blacklist, the pushed V2
overnight autopilot, the pushed Recommendation V1, the pushed
Autopilot Loop V1, and the EIGHT-record rejection ledger (C1-C8
all REJECTED_KEPT_ON_RECORD).

THE FROZEN NUMERICS:

  - universe: BTCUSD only (single symbol);
  - timeframe: 15m (completed bars only);
  - direction: long_only;
  - rolling window: 96 completed 15m bars BEFORE the trigger bar
    (the trigger bar's own values are NEVER included in the rolling
    stats -- no same-bar lookahead);
  - ATR length: 14 15m bars, simple-mean true range (same primitive
    the C3/C7/C8 lane uses);
  - downside z-score trigger threshold: -2.0 (strict-below); the
    trigger bar's close-to-close log return must be strictly less
    than mean - 2.0 x std of the prior 96-bar rolling-window log
    returns;
  - volume condition: strict-below the rolling-window MEDIAN volume
    over the same 96-bar window;
  - JOINT trigger: BOTH the z-score and the volume conditions must
    hold on the SAME completed 15m bar;
  - entry: at the close of the NEXT completed 15m bar after the
    trigger bar (the post-panic confirmation bar). NO intrabar
    entry. NO same-bar entry. The entry bar must close strictly
    above the trigger bar's low, otherwise the setup is invalidated
    at the entry gate (price continued through the panic level, so
    the asymmetry thesis is falsified by that bar);
  - evaluation starts: the bar IMMEDIATELY AFTER the entry bar's
    close;
  - structure stop: stop_price = trigger_bar_low -
    STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER (0.20) x ATR(14) at the
    trigger bar; stop_distance = entry_price - stop_price; INVALID
    if stop_distance <= 0 OR stop_price is not below entry_price OR
    stop_price is not below trigger_bar_low;
  - stop is NEVER tightened after entry;
  - target variants: 2R, 3R, 4R only; target_price = entry_price +
    r_multiple x stop_distance;
  - timeout horizon: 96 completed 15m bars (24h at 15m) from the
    entry bar's close;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant (3 x round-trip) checked at label time before replay
    eligibility;
  - 8-bar anti-cluster gap per symbol at label-emission time,
    BEFORE replay-time non-overlap; tie-breaker keeps the earlier
    accepted event and drops the later same-symbol event within 8
    bars. THIS IS PROPOSAL-LEVEL LOCKED AND NOT THE SINGLE C9 EDIT
    TOKEN;
  - sample-size adequacy: a MINIMUM of 20 accepted setups is
    required at the labels-review gate; below 20 triggers a
    structural rejection WITHOUT spending the single C9 edit token.
    THIS IS PROPOSAL-LEVEL LOCKED AND NOT THE SINGLE C9 EDIT TOKEN;
  - sample window: 2026-05-02_2026-06-10 (the same staged BTCUSD
    15m candles the C8 lane used);
  - existing staged BTCUSD 15m data only; NO fetch ever;
  - maximum one pre-committed edit for C9; the anti-cluster gap,
    the sample-size threshold, AND the explicit-edge-argument field
    are ALL proposal-level locked and NONE consumes the edit token.

THIS SPEC IS MATERIALLY DIFFERENT FROM C1-C8:
  - not session-anchored (NOT C1: no NY-session FVG/CHoCH);
  - not breakout-pullback (NOT C2);
  - not trend continuation (NOT C3);
  - not BTC/SOL or SOL/BTC swing-continuation coupling (NOT C4);
  - not relative-strength pullback continuation (NOT C5);
  - not multi-symbol rank/rotation (NOT C6);
  - not ATR compression/expansion trigger (NOT C7);
  - not liquidity-sweep-then-reclaim geometry (NOT C8);
  - the EDGE HYPOTHESIS is order-book asymmetry between thin-book
    panic clearing and patient deeper-book buyers, signalled by a
    JOINT downside-z-score-AND-below-median-volume condition on a
    SINGLE completed 15m bar.

C6 ANTI-CLUSTER LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the 8-bar
minimum gap and tie-breaker are part of this spec review and do NOT
consume the single allowed C9 edit token. C7 SAMPLE-SIZE ADEQUACY
LESSON IS PROPOSAL-LEVEL LOCKED HERE -- the minimum 20 accepted
setups threshold is part of this spec review and ALSO does NOT
consume the edit token. C8 EXPLICIT-EDGE-ARGUMENT LESSON IS
PROPOSAL-LEVEL LOCKED HERE -- the V4-required microstructure claim
field is carried forward and does NOT consume the edit token
either. The single edit allowance is reserved for a genuinely
different structural parameter (the downside z-score threshold, the
volume percentile threshold, the rolling-window length, or the
structure-stop buffer multiplier) if the initial replay fails on a
different failure mode.

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
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
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

C9S_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_spec"
    "_review.v1")
C9S_LABEL = ("SPARTA Candidate #9 Strategy Spec Review "
             "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
             "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY "
             "CARRIED FORWARD FROM C9 PROPOSAL, "
             "NOT A RESCUE, NOT A CLAIM)")
C9S_MODE = "RESEARCH_ONLY"
VERDICT_C9S_READY = "CANDIDATE_9_SPEC_REVIEW_READY"
VERDICT_C9S_BLOCKED = "CANDIDATE_9_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_9_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1+2+3. universe, timeframe, direction -----------------------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "15m"
DIRECTION = "long_only"

# 4. rolling-window stats configuration -----------------------------------
ROLLING_WINDOW_BARS = 96
ROLLING_WINDOW_USES_PRIOR_BARS_ONLY_NO_SAME_BAR_LOOKAHEAD = True

# 5. ATR primitive --------------------------------------------------------
ATR_LENGTH = 14
ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE = True

# 6. downside z-score trigger ---------------------------------------------
DOWNSIDE_Z_SCORE_THRESHOLD = -2.0
DOWNSIDE_Z_SCORE_RULE = {
    "rule": (
        "the trigger bar's close-to-close log return must be "
        "STRICTLY LESS THAN mean(log_returns over the prior "
        "ROLLING_WINDOW_BARS) + DOWNSIDE_Z_SCORE_THRESHOLD x "
        "std(log_returns over the same window)"),
    "downside_z_score_threshold": DOWNSIDE_Z_SCORE_THRESHOLD,
    "rolling_window_bars": ROLLING_WINDOW_BARS,
    "uses_completed_15m_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead_in_stats": True,
    "strict_inequality_below_threshold": True,
    "log_return_definition": (
        "log(close[i] / close[i-1]) for each completed 15m bar i"),
    "stats_use_population_or_sample_std": "sample_std_n_minus_1",
}

# 7. below-median volume condition ----------------------------------------
VOLUME_BELOW_MEDIAN_RULE = {
    "rule": (
        "the trigger bar's volume must be STRICTLY LESS THAN the "
        "MEDIAN volume over the prior ROLLING_WINDOW_BARS completed "
        "15m bars"),
    "volume_percentile_threshold": 50.0,
    "rolling_window_bars": ROLLING_WINDOW_BARS,
    "uses_completed_15m_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead_in_median": True,
    "strict_inequality_below_median": True,
}

# 8. joint trigger condition ----------------------------------------------
JOINT_TRIGGER_RULE = {
    "rule": (
        "BOTH the downside-z-score condition AND the below-median-"
        "volume condition must hold on the SAME completed 15m bar; "
        "neither condition alone is a trigger; the JOINT condition "
        "is the proxy for the order-book asymmetry edge argument "
        "carried forward from the C9 proposal"),
    "both_conditions_required_on_same_bar": True,
    "is_a_joint_microstructure_trigger_not_a_chart_pattern": True,
}

# 9. entry rule -----------------------------------------------------------
ENTRY_RULE = {
    "rule": (
        "entry is at the close of the NEXT completed 15m bar AFTER "
        "the trigger bar (the post-panic confirmation bar); no "
        "intrabar entry; no same-bar entry; if the entry bar's "
        "close is at or below the trigger bar's low, the setup is "
        "INVALIDATED at the entry gate (price continued through "
        "the panic level, so the asymmetry thesis is falsified by "
        "that bar)"),
    "entry_price": "close_of_the_next_completed_15m_bar_after"
                   "_trigger_bar",
    "no_intrabar_entry": True,
    "no_same_bar_entry": True,
    "invalidate_if_entry_bar_close_le_trigger_bar_low": True,
    "evaluation_starts": "next_15m_bar_after_entry_bar_close",
}

# 10. structure-stop rule -------------------------------------------------
STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER = 0.20
STOP_RULE = {
    "atr_length": ATR_LENGTH,
    "atr_uses_completed_15m_bars_only_standard_true_range":
        ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE,
    "structure_stop_buffer_atr_multiplier":
        STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER,
    "stop_price_formula": (
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar"),
    "stop_distance_formula": (
        "entry_price - stop_price"),
    "stop_must_be_below_entry": True,
    "stop_must_be_below_trigger_bar_low": True,
    "invalid_if_stop_distance_not_positive": True,
    "never_tightened_after_entry": True,
}

# 11. target variants -----------------------------------------------------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_RULES = {
    "variants": TARGET_VARIANTS,
    "no_new_variants_after_label_freeze": True,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
}

# 12. timeout horizon -----------------------------------------------------
TIMEOUT_BARS = 96
TIMEOUT_RULE = {
    "timeout_bars": TIMEOUT_BARS,
    "horizon_hours_at_15m": 24.0,
    "applied_at_replay_time": True,
    "is_not_an_entry_gate_rule": True,
}

# 13. fee-aware geometry --------------------------------------------------
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

# 14. anti-cluster (proposal-level locked policy; NOT the edit token) ----
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
        "level so it does NOT consume the single allowed C9 edit "
        "token"),
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "applies_to_all_variants_uniformly": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "leaves_staged_data_unchanged": True,
    "is_not_the_single_allowed_c9_edit_token": True,
}

# 15. sample-size adequacy (proposal-level locked; NOT the edit token) --
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 20
SAMPLE_SIZE_ADEQUACY_POLICY = {
    "minimum_accepted_setups_required_at_labels_review_gate":
        SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED,
    "below_threshold_triggers_structural_rejection_without_edit"
    "_token": True,
    "rationale": (
        "the C7 lesson is that zero-setup strictness is a "
        "structural failure mode; the C9 proposal commits a "
        "minimum-evaluable-count threshold of 20 at the labels-"
        "review gate so a near-zero detection result is captured "
        "as a structural rejection without consuming the single "
        "edit token"),
    "applies_at_labels_review_gate": True,
    "is_not_the_single_allowed_c9_edit_token": True,
    "applies_before_any_edit_token_decision": True,
}

# 16. explicit edge argument (V4-required; proposal-level locked) -------
EXPLICIT_EDGE_ARGUMENT_POLICY = {
    "carried_forward_from_c9_family_proposal": True,
    "v4_required_field": True,
    "argument_is_microstructural_not_visual": True,
    "argument_is_falsifiable_by_per_variant_net_r_sums": True,
    "is_not_the_single_allowed_c9_edit_token": True,
    "rationale": (
        "the C8 lesson is that structural cleanliness alone does "
        "not produce edge; the V4 blacklist requires every C9+ "
        "proposal to include an explicit edge argument beyond "
        "pattern geometry; the C9 proposal supplied a six-"
        "paragraph order-book asymmetry argument and the spec "
        "review carries it forward unchanged"),
}

# 17. data boundary / sample window --------------------------------------
SAMPLE_TAG = "2026-05-02_2026-06-10"
DATA_BOUNDARY = {
    "source": ("existing append-only staged 15m candles only "
               "(data/ny_fvg_choch/staged/, sha-pinned at runtime "
               "by the future detection runner)"),
    "aggregation": "no_aggregation_needed_native_15m_data",
    "sample_tag": SAMPLE_TAG,
    "no_fetch_ever": True,
    "no_real_time_data": True,
    "staged_data_never_modified": True,
    "consumes_volume_column_structurally_for_first_time_in_lane":
        True,
}

# 18. replay-time same-symbol non-overlap (inherited) -------------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
}

# 19. edit allowance -----------------------------------------------------
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_requires_separate_human_approval": True,
    "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token":
        True,
    "sample_size_threshold_is_proposal_level_locked_not_the_edit"
    "_token": True,
    "explicit_edge_argument_field_is_proposal_level_locked_not_the"
    "_edit_token": True,
    "edit_must_target_a_different_structural_parameter": True,
    "edit_token_eligible_parameters": (
        "DOWNSIDE_Z_SCORE_THRESHOLD",
        "VOLUME_PERCENTILE_THRESHOLD_50",
        "ROLLING_WINDOW_BARS",
        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER"),
}

# 20. material differences from C1-C8 -----------------------------------
MATERIAL_DIFFERENCES_FROM_REJECTED_FAMILIES = (
    "not_session_anchored_no_ny_fvg_choch_dependency_NOT_c1",
    "not_breakout_pullback_continuation_NOT_c2",
    "not_trend_continuation_thesis_NOT_c3",
    "not_btc_sol_or_sol_btc_swing_continuation_coupling_NOT_c4",
    "no_relative_strength_comparison_NOT_c5",
    "no_multi_symbol_rank_or_rotation_NOT_c6",
    "no_atr_compression_or_expansion_trigger_NOT_c7",
    "no_sweep_below_prior_low_geometry_no_reclaim_window_NOT_c8",
)

# 21. inherited lessons -------------------------------------------------
INHERITED_LESSONS = (
    "c6_lesson_anti_cluster_protection_built_in_at_proposal_and"
    "_spec_level_not_consuming_edit_token",
    "c7_lesson_sample_size_adequacy_threshold_built_in_at_proposal"
    "_and_spec_level_not_consuming_edit_token",
    "c8_lesson_explicit_edge_argument_beyond_pattern_geometry_built"
    "_in_at_proposal_and_spec_level_not_consuming_edit_token",
)

# 22. claim locks -------------------------------------------------------
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
)


def get_candidate_9_spec_review_label() -> str:
    return C9S_LABEL


def build_candidate_9_spec_review() -> dict[str, Any]:
    """Assemble the C9 spec review. Chain-gated on the eight-record
    ledger, the pushed C9 family proposal, the pushed V4 blacklist,
    the pushed V3, V2, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": C9S_SCHEMA_VERSION, "label": C9S_LABEL,
        "mode": C9S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "rolling_window_bars": ROLLING_WINDOW_BARS,
        "rolling_window_uses_prior_bars_only_no_same_bar_lookahead":
            ROLLING_WINDOW_USES_PRIOR_BARS_ONLY_NO_SAME_BAR_LOOKAHEAD,
        "atr_length": ATR_LENGTH,
        "atr_uses_completed_15m_bars_only_standard_true_range":
            ATR_USES_COMPLETED_15M_BARS_ONLY_STANDARD_TRUE_RANGE,
        "downside_z_score_threshold": DOWNSIDE_Z_SCORE_THRESHOLD,
        "downside_z_score_rule": dict(DOWNSIDE_Z_SCORE_RULE),
        "volume_below_median_rule": dict(VOLUME_BELOW_MEDIAN_RULE),
        "joint_trigger_rule": dict(JOINT_TRIGGER_RULE),
        "entry_rule": dict(ENTRY_RULE),
        "stop_rule": dict(STOP_RULE),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "timeout_rule": dict(TIMEOUT_RULE),
        "fee_geometry": dict(FEE_GEOMETRY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "sample_size_adequacy_policy":
            dict(SAMPLE_SIZE_ADEQUACY_POLICY),
        "explicit_edge_argument_policy":
            dict(EXPLICIT_EDGE_ARGUMENT_POLICY),
        "explicit_edge_argument_beyond_pattern_geometry_carried"
        "_forward": EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
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
        "ledger_status_eight_records": None,
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
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
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
                C6_STATUS, C7_STATUS, C8_STATUS)
    record["ledger_status_eight_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    proposal = build_candidate_9_family_proposal()
    if proposal["verdict"] != VERDICT_C9P_READY:
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append(
            "candidate_9_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C9S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C9S_READY
    return record


def validate_candidate_9_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C9S_READY,
                                VERDICT_C9S_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "15m" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("rolling_window_bars") != 96:
        errors.append("rolling_window_must_be_96")
    if r.get(
            "rolling_window_uses_prior_bars_only_no_same_bar_lookahead"
    ) is not True:
        errors.append("rolling_window_lookahead_protection_weakened")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get(
            "atr_uses_completed_15m_bars_only_standard_true_range"
    ) is not True:
        errors.append("atr_lookahead_protection_weakened")
    if r.get("downside_z_score_threshold") != -2.0:
        errors.append("downside_z_score_threshold_must_be_minus_2_0")
    zr = r.get("downside_z_score_rule") or {}
    if zr != DOWNSIDE_Z_SCORE_RULE:
        errors.append("downside_z_score_rule_tampered")
    vr = r.get("volume_below_median_rule") or {}
    if vr != VOLUME_BELOW_MEDIAN_RULE:
        errors.append("volume_below_median_rule_tampered")
    if vr.get("volume_percentile_threshold") != 50.0:
        errors.append("volume_threshold_must_be_50_percentile")
    if vr.get("strict_inequality_below_median") is not True:
        errors.append("volume_strict_inequality_weakened")
    jt = r.get("joint_trigger_rule") or {}
    if jt != JOINT_TRIGGER_RULE:
        errors.append("joint_trigger_rule_tampered")
    if jt.get("both_conditions_required_on_same_bar") is not True:
        errors.append("joint_trigger_same_bar_weakened")
    er = r.get("entry_rule") or {}
    if er != ENTRY_RULE:
        errors.append("entry_rule_tampered")
    if er.get("entry_price") != (
            "close_of_the_next_completed_15m_bar_after_trigger_bar"):
        errors.append("entry_must_be_close_of_next_bar")
    if er.get("no_intrabar_entry") is not True \
            or er.get("no_same_bar_entry") is not True:
        errors.append("intrabar_or_same_bar_entry_must_be_forbidden")
    if er.get("invalidate_if_entry_bar_close_le_trigger_bar_low"
              ) is not True:
        errors.append("entry_invalidation_rule_weakened")
    stop = r.get("stop_rule") or {}
    if stop != STOP_RULE:
        errors.append("stop_rule_tampered")
    if stop.get("structure_stop_buffer_atr_multiplier") != 0.20:
        errors.append("structure_stop_buffer_must_be_0_20")
    if stop.get("stop_price_formula") != (
            "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
            "ATR14_at_trigger_bar"):
        errors.append("stop_price_formula_tampered")
    if stop.get("stop_must_be_below_entry") is not True \
            or stop.get("stop_must_be_below_trigger_bar_low") is not (
            True) \
            or stop.get("never_tightened_after_entry") is not True \
            or stop.get("invalid_if_stop_distance_not_positive") is (
            not True):
        errors.append("stop_protection_weakened")
    targets = r.get("target_rules") or {}
    if targets.get("variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if targets.get("target_price_formula") != (
            "entry_price + r_multiple * stop_distance"):
        errors.append("target_price_formula_tampered")
    timeout = r.get("timeout_rule") or {}
    if timeout != TIMEOUT_RULE:
        errors.append("timeout_rule_tampered")
    if timeout.get("timeout_bars") != 96:
        errors.append("timeout_bars_must_be_96")
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
            "is_not_the_single_allowed_c9_edit_token") is not True:
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
    ) != 20:
        errors.append("sample_size_minimum_must_be_20")
    if sa.get(
            "below_threshold_triggers_structural_rejection_without"
            "_edit_token") is not True:
        errors.append(
            "sample_size_must_trigger_rejection_without_edit_token")
    if sa.get(
            "is_not_the_single_allowed_c9_edit_token") is not True:
        errors.append("sample_size_must_not_be_the_edit_token")
    eep = r.get("explicit_edge_argument_policy") or {}
    if eep != EXPLICIT_EDGE_ARGUMENT_POLICY:
        errors.append("explicit_edge_argument_policy_tampered")
    if eep.get("v4_required_field") is not True:
        errors.append("explicit_edge_argument_must_be_v4_required")
    if eep.get(
            "is_not_the_single_allowed_c9_edit_token") is not True:
        errors.append(
            "explicit_edge_argument_must_not_be_the_edit_token")
    if r.get(
            "explicit_edge_argument_beyond_pattern_geometry_carried"
            "_forward") != (
            EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY):
        errors.append("explicit_edge_argument_carried_forward_tampered")
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
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C9S_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
