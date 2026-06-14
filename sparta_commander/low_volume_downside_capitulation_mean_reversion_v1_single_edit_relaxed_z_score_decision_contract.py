"""SPARTA CANDIDATE #9 SINGLE PRE-COMMITTED EDIT --
RELAXED DOWNSIDE Z-SCORE THRESHOLD (-2.0 -> -1.5)
(READ-ONLY, RESEARCH ONLY, SINGLE PARAMETER RELAXATION ONLY,
NOT A RESCUE, NOT A CLAIM):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Spends the family's SINGLE pre-committed edit token on a SINGLE
controlled relaxation: change DOWNSIDE_Z_SCORE_THRESHOLD from -2.0
to -1.5 while keeping every other pushed C9 numeric and rule
unchanged. The edit is motivated by the pushed C9 real-candle
labels review evidence:

  - 3,840 scanned BTCUSD 15m bars
  - 8 joint-trigger attempts (z-AND-volume conditions both fired)
  - 1 accepted setup pre and post the 8-bar anti-cluster filter
  - 7 / 7 rejections on `rejected_geometry_floor` (small-magnitude
    excursions screened out by the 81 bps fee-aware floor)
  - SAMPLE-SIZE ADEQUACY STRUCTURALLY FAILED: 1 accepted-post < 20
    threshold; below_minimum_at_dry_run = True; does NOT consume
    the edit token (the failure flag was recorded WITHOUT spending
    the token)
  - 0 anti-cluster drops (only one accepted event; nothing to
    cluster against)
  - the single C9 edit token has NOT been applied yet

The observed structural blocker on this sample window is sparse
trigger generation: the joint price-AND-volume condition is even
rarer than the marginal z-score condition would predict (at -2sigma
on a normal distribution we would expect ~2.3% of bars in the lower
tail = ~88 bars, but only 8 met BOTH the z-score AND below-median-
volume condition). The closest evidence-supported relaxation that
DIRECTLY ADDRESSES sparsity while PRESERVING the microstructure
thesis is to relax the downside z-score threshold from -2.0 to
-1.5: at -1.5sigma a normal distribution predicts ~6.7% of bars in
the lower tail (roughly 3x more), and combined with the unchanged
below-median volume condition this should yield a meaningful
increase in the joint-trigger count -- WITHOUT relaxing the volume
condition (which is the structural edge), the stop buffer (which is
the geometry), or the floor (which is the fee gate).

This contract burns the edit token EXACTLY ONCE and authorises that
single relaxation only. It does NOT touch anything else.

NOTHING ELSE CHANGES. The 14-bar ATR, the 96-bar rolling-window
stats, the strict-below-median volume condition, the joint-trigger
requirement (BOTH conditions must hold on the SAME completed
trigger bar), the next-bar-close entry, the entry-bar-close-strictly
-above-trigger-low invalidation rule, the 0.20 x ATR(14) structure-
stop buffer, the trigger_low - 0.20 x ATR(14) stop_price formula,
the never-tightened stop, the 2R/3R/4R variants, the 96-bar replay
timeout, the 27 bps round-trip fees, the 81 bps gross target-
distance floor, the BTCUSD-only single-symbol universe, the 15m
timeframe, the long-only direction, the 8-bar same-symbol anti-
cluster gap (which remains PROPOSAL/SPEC-LEVEL LOCKED and does NOT
consume this edit token), the minimum-20-accepted-setups sample-
size adequacy threshold (which also remains PROPOSAL/SPEC-LEVEL
LOCKED and does NOT consume this edit token), the explicit-edge-
argument-beyond-pattern-geometry field (which also remains
PROPOSAL/SPEC-LEVEL LOCKED and does NOT consume this edit token),
the 2026-05-02_2026-06-10 sample tag, the staged-only data
boundary, and the no-maker-rebate / no-zero-fee assumptions all
remain inviolable. Modifying any of those invalidates this
contract.

THIS CONTRACT BY ITSELF DOES NOT AUTHORIZE:
  - running edited real-candle detection,
  - re-emitting labels,
  - re-running fee-honest replay,
  - any PnL computation,
  - changing staged 15m candles,
  - paper, micro-live, or live execution,
  - any order / api / wallet / account / credential / broker /
    exchange capability,
  - any profitability or winner claim.

It freezes the edit RULE and burns the family's one edit token.
The next gate is the HUMAN decision to authorize an edited real-
candle detection run that uses DOWNSIDE_Z_SCORE_THRESHOLD = -1.5
while keeping all other C9 frozen numerics. If the eventual edited
detection still produces near-zero or below-threshold accepted
setups, OR an eventual edited replay still triggers any pushed
auto-rejection rule, Candidate #9 becomes the ninth ledger entry
automatically -- no further edits are allowed.

Chain-gated live on the pushed eight-record rejection ledger
(C1-C8), the pushed C9 family proposal, the pushed C9 spec review,
the pushed C9 detector spec + dry-run, the pushed C9 dry-run
review, the pushed C9 real-candle labels review (the only valid
reason to spend this edit), the pushed V4 + V3 blacklists, the
pushed Overnight Research Autopilot V2, the pushed Recommendation
V1, and the pushed Autopilot Loop V1.
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
    VERDICT_C9D_READY,
    build_candidate_9_detector_spec_contract,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_dry_run_review_contract import (
    VERDICT_C9R_FROZEN,
    build_candidate_9_dry_run_review,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract import (
    EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    EXPECTED_LABELS_SHA256 as LABELS_SHA256,
    EXPECTED_REJECTED_BY_SCANNER,
    EXPECTED_STATUS_BREAKDOWN,
    EXPECTED_SUMMARY_SHA256 as LABELS_SUMMARY_SHA256,
    EXPECTED_TOTAL_ATTEMPTS,
    HEAD_AT_DETECTION,
    VERDICT_C9L_FROZEN,
    build_c9_labels_review,
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

C9E_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_single_edit"
    "_relaxed_z_score_decision.v1")
C9E_LABEL = (
    "SPARTA Candidate #9 Single Pre-Committed Edit -- Relaxed "
    "Downside Z-Score Threshold (-2.0 -> -1.5) "
    "(READ-ONLY, RESEARCH ONLY, SINGLE PARAMETER RELAXATION ONLY, "
    "NOT A RESCUE, NOT A CLAIM)")
C9E_MODE = "RESEARCH_ONLY"
VERDICT_C9E_APPROVED = (
    "CANDIDATE_9_SINGLE_EDIT_RELAXED_Z_SCORE_THRESHOLD_APPROVED")
VERDICT_C9E_BLOCKED = (
    "CANDIDATE_9_SINGLE_EDIT_RELAXED_Z_SCORE_THRESHOLD_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_9_EDITED_REAL_CANDLE_DETECTION"
    "_RELAXED_Z_THRESHOLD")
CURRENT_LOOP_STAGE = "detector_and_label_review"
NEXT_LOOP_STAGE = "detector_and_label_review"

# --- The edit token ---------------------------------------------------------
EDIT_TOKEN_USED = 1
EDITS_REMAINING_AFTER_THIS = 0
EDIT_KIND = "relaxed_downside_z_score_threshold_only"
EDIT_SCOPE = (
    "single controlled relaxation of DOWNSIDE_Z_SCORE_THRESHOLD "
    "from -2.0 to -1.5; no other parameter is changed; no detector "
    "rewrite; no new trigger or filter; no fee/floor/stop/target/"
    "universe/timeframe/direction/anti-cluster/sample-size/edge-"
    "argument change; the 8-bar anti-cluster gap, the 20 accepted-"
    "setup sample-size threshold, AND the explicit-edge-argument "
    "field are all PROPOSAL/SPEC-LEVEL LOCKED policies and NONE "
    "consumes this edit token")

# --- The frozen edit parameter ---------------------------------------------
EDIT_PARAMETER_NAME = "DOWNSIDE_Z_SCORE_THRESHOLD"
EDIT_PARAMETER_OLD_VALUE = -2.0
EDIT_PARAMETER_NEW_VALUE = -1.5
EDIT_RULE = {
    "parameter": EDIT_PARAMETER_NAME,
    "old_value": EDIT_PARAMETER_OLD_VALUE,
    "new_value": EDIT_PARAMETER_NEW_VALUE,
    "applies_at": (
        "joint_trigger_check_only_in_the_z_score_strict_below"
        "_threshold_comparison"),
    "applies_to_all_attempts_uniformly": True,
    "is_a_single_controlled_relaxation_not_a_bundle": True,
    "is_a_strict_less_than_check_against_relaxed_threshold": True,
    "rationale": (
        "the pushed real-candle labels review proved that only 8 of "
        "3840 bars on the 2026-05-02_2026-06-10 BTCUSD 15m window "
        "triggered the joint price-AND-volume condition, yielding 1 "
        "accepted-post-anti-cluster setup -- below the proposal/"
        "spec-locked sample-size adequacy threshold of 20 (sample-"
        "size adequacy structurally failed). at a -2.0 z-score "
        "threshold a normal distribution predicts ~2.3% of bars in "
        "the lower tail; the joint condition is even rarer because "
        "the volume gate excludes the high-volume excursions. "
        "relaxing the z threshold by one half-sigma to -1.5 (where "
        "a normal distribution predicts ~6.7% of bars in the lower "
        "tail = roughly 3x more candidate bars) directly addresses "
        "trigger sparsity while preserving the unchanged below-"
        "median volume condition (the structural microstructure "
        "edge). relaxing the volume condition instead would weaken "
        "the edge thesis since high-volume downside excursions are "
        "exactly what the C9 edge argument excludes. relaxing the "
        "stop buffer or any other parameter would not address "
        "trigger sparsity. relaxing more than one parameter at "
        "once would be a rescue bundle and is forbidden by this "
        "contract"),
    "no_intrabar_state": True,
    "no_lookahead": True,
    "deterministic": True,
    "no_other_detector_change": True,
}

# --- Inviolable upstream rules this edit MUST NOT change -------------------
INVIOLABLE_RULES = {
    "atr_length": 14,
    "rolling_window_bars": 96,
    "volume_percentile_threshold": 50.0,
    "volume_strict_below_median": True,
    "joint_trigger_both_conditions_required_on_same_bar": True,
    "entry_rule": "close_of_next_completed_15m_bar_after_trigger"
                  "_bar",
    "no_intrabar_entry": True,
    "entry_bar_close_must_be_strictly_above_trigger_bar_low": True,
    "evaluation_starts": "next_15m_bar_after_entry_bar_close",
    "structure_stop_buffer_atr_multiplier": 0.20,
    "stop_price_formula": (
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar"),
    "stop_never_tightened_after_entry": True,
    "stop_must_be_below_entry_and_below_trigger_low": True,
    "target_variants": ("2r", "3r", "4r"),
    "target_price_formula": (
        "entry_price + r_multiple * stop_distance"),
    "timeout_bars": 96,
    "fee_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "universe": ("BTCUSD",),
    "timeframe": "15m",
    "direction": "long_only",
    "anti_cluster_min_bar_gap": 8,
    "anti_cluster_is_proposal_level_locked_not_edit_token": True,
    "sample_size_adequacy_threshold_min_accepted": 20,
    "sample_size_adequacy_is_proposal_level_locked_not_edit_token":
        True,
    "explicit_edge_argument_field_is_proposal_level_locked_not_edit"
    "_token": True,
    "sample_tag": "2026-05-02_2026-06-10",
    "no_fetch_ever": True,
    "staged_data_never_modified": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# --- Frozen labels-review evidence motivating the edit --------------------
FROZEN_LABELS_REVIEW_EVIDENCE_FOR_EDIT = {
    "candidate_id": CANDIDATE_ID,
    "labels_sha256": LABELS_SHA256,
    "summary_sha256": LABELS_SUMMARY_SHA256,
    "head_at_detection": HEAD_AT_DETECTION,
    "total_attempts": EXPECTED_TOTAL_ATTEMPTS,
    "accepted_pre_anti_cluster": EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    "accepted_post_anti_cluster":
        EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    "rejected_by_scanner": EXPECTED_REJECTED_BY_SCANNER,
    "dropped_by_anti_cluster": EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    "status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
    "sample_size_threshold_min_required": 20,
    "sample_size_satisfied": False,
    "sample_size_structural_failure": True,
    "edit_token_unused_before_this_decision": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
    "anti_cluster_did_not_consume_edit_token": True,
    "sample_size_did_not_consume_edit_token": True,
    "explicit_edge_argument_did_not_consume_edit_token": True,
}

# --- Post-edit auto-rejection conditions ---------------------------------
POST_EDIT_AUTO_REJECTION_TRIGGERS = (
    "near_zero_accepted_count_after_edited_detection",
    "sample_size_still_below_threshold_after_edited_detection",
    "any_variant_net_negative_after_edited_replay",
    "any_variant_gross_negative_after_edited_replay",
    "any_variant_hit_rate_below_gross_breakeven_after_edited"
    "_replay",
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline",
    "any_attempt_to_change_an_inviolable_upstream_rule",
    "any_attempt_to_change_more_than_downside_z_score_threshold",
    "any_attempt_to_spend_a_second_edit_on_this_family",
    "any_attempt_to_modify_anti_cluster_gap_via_this_edit",
    "any_attempt_to_modify_sample_size_threshold_via_this_edit",
    "any_attempt_to_modify_explicit_edge_argument_field_via_this"
    "_edit",
)

# --- Claim locks ----------------------------------------------------------
CLAIM_LOCKS = (
    "edit_is_single_parameter_relaxation_only_no_bundle",
    "edit_does_not_authorize_edited_real_candle_detection_by_itself",
    "edit_does_not_authorize_relabel",
    "edit_does_not_authorize_replay",
    "edit_does_not_authorize_pnl_computation",
    "edit_does_not_authorize_paper_or_live_or_execution",
    "edit_is_not_a_rescue_attempt",
    "no_profitability_claim",
    "no_winner_wording",
    "automatic_rejection_if_any_post_edit_trigger_fires",
    "single_pre_committed_edit_token_spent_no_further_edits_allowed",
    "anti_cluster_gap_remains_proposal_level_locked_not_edit_token",
    "sample_size_threshold_remains_proposal_level_locked_not_edit"
    "_token",
    "explicit_edge_argument_field_remains_proposal_level_locked_not"
    "_edit_token",
)


def get_c9_single_edit_label() -> str:
    return C9E_LABEL


def build_c9_single_edit_relaxed_z_score(
        repo_root: Any = ".", tracked_paths: Any = ()
) -> dict[str, Any]:
    """Assemble the C9 single-edit relaxed z-score decision record,
    chain-gated on the full pushed C9 lane plus the eight-record
    rejection ledger, V4, V3, Recommendation V1, and Autopilot Loop
    V1. The pushed labels review must certify with sample-size
    structural failure -- the only valid reason to spend this
    edit."""
    record: dict[str, Any] = {
        "schema_version": C9E_SCHEMA_VERSION, "label": C9E_LABEL,
        "mode": C9E_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "edit_token_used": EDIT_TOKEN_USED,
        "edits_remaining_after_this": EDITS_REMAINING_AFTER_THIS,
        "edit_kind": EDIT_KIND, "edit_scope": EDIT_SCOPE,
        "edit_parameter_name": EDIT_PARAMETER_NAME,
        "edit_parameter_old_value": EDIT_PARAMETER_OLD_VALUE,
        "edit_parameter_new_value": EDIT_PARAMETER_NEW_VALUE,
        "edit_rule": dict(EDIT_RULE),
        "inviolable_rules": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in INVIOLABLE_RULES.items()},
        "frozen_labels_review_evidence_for_edit":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in
             FROZEN_LABELS_REVIEW_EVIDENCE_FOR_EDIT.items()},
        "post_edit_auto_rejection_triggers":
            list(POST_EDIT_AUTO_REJECTION_TRIGGERS),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "edit_token_spent_by_this_contract": True,
        "this_is_the_only_allowed_c9_edit": True,
        "is_a_rescue_attempt": False,
        "is_single_controlled_relaxation": True,
        "is_a_rescue_bundle": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
        "runs_edited_real_candle_detection": False,
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
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "modifies_labels_artifacts": False,
        "computes_pnl_now": False,
        "authorizes_edited_real_candle_detection": False,
        "authorizes_relabel": False, "authorizes_replay": False,
        "authorizes_pnl_now": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading":
            False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_replay_gate": False, "unlocks_relabel_gate": False,
        "unlocks_paper_gate": False, "unlocks_micro_live_gate": False,
        "unlocks_live_gate": False,
        "claims_profitability": False,
        "modifies_anti_cluster_gap_via_this_edit": False,
        "modifies_sample_size_threshold_via_this_edit": False,
        "modifies_explicit_edge_argument_field_via_this_edit": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == C6_STATUS == C7_STATUS == C8_STATUS
            == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    if build_candidate_9_family_proposal()["verdict"] != (
            VERDICT_C9P_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "candidate_9_proposal_not_certifying")
        return record
    if build_candidate_9_spec_review()["verdict"] != VERDICT_C9S_READY:
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "candidate_9_spec_review_not_certifying")
        return record
    if build_candidate_9_detector_spec_contract()["verdict"] != (
            VERDICT_C9D_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "candidate_9_detector_spec_not_certifying")
        return record
    if build_candidate_9_dry_run_review()["verdict"] != (
            VERDICT_C9R_FROZEN):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "candidate_9_dry_run_review_not_certifying")
        return record
    labels_review = build_c9_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C9L_FROZEN:
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    # the labels review must show sample-size structural failure
    if labels_review[
            "expected_sample_size_structural_failure"] is not True:
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "labels_review_must_show_sample_size_structural_failure"
            "_to_justify_edit")
        return record
    if labels_review["expected_sample_size_satisfied"] is not False:
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "labels_review_must_show_sample_size_not_satisfied_to"
            "_justify_edit")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C9E_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C9E_APPROVED
    return record


def validate_c9_single_edit_relaxed_z_score(
        record: Any) -> dict[str, Any]:
    """Validate shape, frozen edit rule, inviolable rules, and
    safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C9E_APPROVED,
                                VERDICT_C9E_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("edit_token_used") != 1:
        errors.append("edit_token_used_must_be_exactly_1")
    if r.get("edits_remaining_after_this") != 0:
        errors.append("edits_remaining_after_this_must_be_0")
    if r.get("edit_kind") != EDIT_KIND:
        errors.append(
            "edit_kind_must_be_relaxed_downside_z_score_threshold"
            "_only")
    if r.get("edit_parameter_name") != "DOWNSIDE_Z_SCORE_THRESHOLD":
        errors.append(
            "edit_parameter_must_be_downside_z_score_threshold_only")
    if r.get("edit_parameter_old_value") != -2.0:
        errors.append("edit_old_value_must_be_minus_2_0")
    if r.get("edit_parameter_new_value") != -1.5:
        errors.append("edit_new_value_must_be_minus_1_5")
    rule = r.get("edit_rule") or {}
    if rule != EDIT_RULE:
        errors.append("edit_rule_tampered")
    if rule.get("parameter") != "DOWNSIDE_Z_SCORE_THRESHOLD":
        errors.append(
            "edit_rule_parameter_must_be_downside_z_score_threshold")
    if rule.get("old_value") != -2.0 or rule.get(
            "new_value") != -1.5:
        errors.append(
            "edit_rule_values_must_be_minus_2_0_and_minus_1_5")
    if rule.get("is_a_single_controlled_relaxation_not_a_bundle"
                ) is not True:
        errors.append(
            "must_be_single_controlled_relaxation_not_bundle")
    if rule.get("no_other_detector_change") is not True:
        errors.append(
            "edit_must_be_relaxation_only_no_detector_rewrite")
    if rule.get("no_lookahead") is not True \
            or rule.get("deterministic") is not True:
        errors.append("rule_lookahead_or_determinism_weakened")
    # inviolable rules check
    expected_invio = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in INVIOLABLE_RULES.items()}
    invio = r.get("inviolable_rules") or {}
    if invio != expected_invio:
        errors.append("inviolable_rules_tampered")
    if invio.get("atr_length") != 14:
        errors.append("atr_length_changed")
    if invio.get("rolling_window_bars") != 96:
        errors.append("rolling_window_must_remain_96")
    if invio.get("volume_percentile_threshold") != 50.0:
        errors.append("volume_threshold_must_remain_50")
    if invio.get("volume_strict_below_median") is not True:
        errors.append("volume_strict_below_weakened")
    if invio.get(
            "joint_trigger_both_conditions_required_on_same_bar"
    ) is not True:
        errors.append("joint_trigger_same_bar_weakened")
    if invio.get("entry_rule") != (
            "close_of_next_completed_15m_bar_after_trigger_bar"):
        errors.append("entry_rule_changed")
    if invio.get("no_intrabar_entry") is not True:
        errors.append("intrabar_entry_protection_weakened")
    if invio.get(
            "entry_bar_close_must_be_strictly_above_trigger_bar_low"
    ) is not True:
        errors.append("entry_invalidation_protection_weakened")
    if invio.get("structure_stop_buffer_atr_multiplier") != 0.20:
        errors.append("structure_stop_buffer_must_remain_0_20")
    if invio.get("stop_price_formula") != (
            "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR"
            "_MULTIPLIER * ATR14_at_trigger_bar"):
        errors.append("stop_price_formula_changed")
    if invio.get("stop_never_tightened_after_entry") is not True:
        errors.append("stop_tightening_protection_weakened")
    if invio.get(
            "stop_must_be_below_entry_and_below_trigger_low"
    ) is not True:
        errors.append("stop_geometry_protection_weakened")
    if invio.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_changed")
    if invio.get("target_price_formula") != (
            "entry_price + r_multiple * stop_distance"):
        errors.append("target_price_formula_changed")
    if invio.get("timeout_bars") != 96:
        errors.append("timeout_bars_changed")
    if invio.get("fee_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if invio.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if invio.get("universe") != ["BTCUSD"]:
        errors.append("universe_changed")
    if invio.get("timeframe") != "15m":
        errors.append("timeframe_changed")
    if invio.get("direction") != "long_only":
        errors.append("direction_changed")
    if invio.get("anti_cluster_min_bar_gap") != 8:
        errors.append("anti_cluster_gap_changed")
    if invio.get(
            "anti_cluster_is_proposal_level_locked_not_edit_token"
    ) is not True:
        errors.append("anti_cluster_must_not_be_consumed_by_edit"
                      "_token")
    if invio.get("sample_size_adequacy_threshold_min_accepted") != 20:
        errors.append("sample_size_threshold_changed")
    if invio.get(
            "sample_size_adequacy_is_proposal_level_locked_not_edit"
            "_token") is not True:
        errors.append(
            "sample_size_must_not_be_consumed_by_edit_token")
    if invio.get(
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_edit_token") is not True:
        errors.append(
            "explicit_edge_argument_must_not_be_consumed_by_edit"
            "_token")
    if invio.get("sample_tag") != "2026-05-02_2026-06-10":
        errors.append("sample_tag_changed")
    if invio.get("no_fetch_ever") is not True \
            or invio.get("staged_data_never_modified") is not True:
        errors.append("data_boundary_weakened")
    if invio.get("no_maker_rebate_assumption") is not True \
            or invio.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    # frozen labels-review evidence motivation
    ev = r.get("frozen_labels_review_evidence_for_edit") or {}
    if ev.get("labels_sha256") != LABELS_SHA256:
        errors.append("labels_sha_in_motivation_tampered")
    if ev.get("summary_sha256") != LABELS_SUMMARY_SHA256:
        errors.append("summary_sha_in_motivation_tampered")
    if ev.get("head_at_detection") != HEAD_AT_DETECTION:
        errors.append("head_at_detection_tampered")
    if ev.get("total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        errors.append("motivation_total_attempts_must_equal_8")
    if ev.get("accepted_pre_anti_cluster") != 1 \
            or ev.get("accepted_post_anti_cluster") != 1:
        errors.append("motivation_accepted_must_be_1")
    if ev.get("rejected_by_scanner") != EXPECTED_REJECTED_BY_SCANNER:
        errors.append("motivation_rejected_must_equal_7")
    if ev.get("dropped_by_anti_cluster") != 0:
        errors.append("motivation_dropped_must_be_zero")
    if ev.get("status_breakdown") != dict(EXPECTED_STATUS_BREAKDOWN):
        errors.append("motivation_status_breakdown_tampered")
    if ev.get("sample_size_threshold_min_required") != 20:
        errors.append("motivation_sample_size_threshold_must_be_20")
    if ev.get("sample_size_satisfied") is not False:
        errors.append("motivation_sample_size_satisfied_must_be_false")
    if ev.get("sample_size_structural_failure") is not True:
        errors.append(
            "motivation_sample_size_structural_failure_must_be_true")
    if ev.get("edit_token_unused_before_this_decision") is not True:
        errors.append("motivation_edit_token_must_have_been_unused")
    if ev.get("no_replay_run") is not True \
            or ev.get("no_pnl_computed") is not True:
        errors.append("motivation_no_replay_no_pnl_must_hold")
    if ev.get("anti_cluster_did_not_consume_edit_token") is not True:
        errors.append(
            "motivation_anti_cluster_must_not_have_consumed_token")
    if ev.get("sample_size_did_not_consume_edit_token") is not True:
        errors.append(
            "motivation_sample_size_must_not_have_consumed_token")
    if ev.get(
            "explicit_edge_argument_did_not_consume_edit_token"
    ) is not True:
        errors.append(
            "motivation_edge_argument_must_not_have_consumed_token")
    # post-edit auto-rejection triggers
    if tuple(r.get("post_edit_auto_rejection_triggers") or ()) != (
            POST_EDIT_AUTO_REJECTION_TRIGGERS):
        errors.append("post_edit_auto_rejection_triggers_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    # capability locks
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("edit_token_spent_by_this_contract", True),
                      ("this_is_the_only_allowed_c9_edit", True),
                      ("is_a_rescue_attempt", False),
                      ("is_single_controlled_relaxation", True),
                      ("is_a_rescue_bundle", False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "computes_pnl_now",
                "authorizes_edited_real_candle_detection",
                "authorizes_relabel", "authorizes_replay",
                "authorizes_pnl_now",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "unlocks_replay_gate",
                "unlocks_relabel_gate", "unlocks_paper_gate",
                "unlocks_micro_live_gate", "unlocks_live_gate",
                "claims_profitability",
                "modifies_anti_cluster_gap_via_this_edit",
                "modifies_sample_size_threshold_via_this_edit",
                "modifies_explicit_edge_argument_field_via_this_edit"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_loop_stage") != "detector_and_label_review":
        errors.append("next_loop_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_C9E_APPROVED and r.get("blockers"):
        errors.append("approved_with_blockers")
    return {"valid": not errors, "errors": errors}
