"""SPARTA CANDIDATE #7 SINGLE PRE-COMMITTED EDIT --
RELAXED CONTRACTION FRACTION (0.6 -> 0.7)
(READ-ONLY, RESEARCH ONLY, SINGLE PARAMETER RELAXATION ONLY,
NOT A RESCUE, NOT A CLAIM):
VOLATILITY_COMPRESSION_EXPANSION_V1.

Spends the family's SINGLE pre-committed edit token on a SINGLE
controlled relaxation: change CONTRACTION_FRACTION from 0.6 to 0.7
while keeping every other pushed C7 numeric and rule unchanged. The
edit is motivated by the pushed C7 real-candle labels review evidence:

  - 240 scanned 4h bars
  - 122 detection attempts (event indices 118..239 inclusive)
  - 0 accepted setups pre and post the 6-bar anti-cluster filter
  - 122 / 122 rejections on `rejected_contraction_window` (ATR(14)
    never dropped below 0.6 x its 100-bar rolling-average ATR for 5
    consecutive completed bars in this window)
  - 0 floor-pass at every variant (no setup reached the floor stage)
  - 0 anti-cluster drops (no accepted events to consider)
  - the single C7 edit token has NOT been applied yet

The single observed blocker on this sample window was the contraction
window check. The pushed spec review froze CONTRACTION_FRACTION = 0.6;
the closest evidence-supported relaxation is 0.7 (one decile higher).
This contract burns the edit token EXACTLY ONCE and authorises that
single relaxation only. It does NOT touch anything else.

NOTHING ELSE CHANGES. The 14-bar ATR, the 100-bar ATR rolling-average
window, the 5-bar contraction window count, the 1.8 expansion
true-range multiplier, the upper-third close rule, the entry at the
event-bar close, the next-bar evaluation start, the 10-bar structure-
stop lookback, the WIDER stop = max(1.5 * ATR(14), structure_stop
_distance), the 2R/3R/4R variants, the 27 bps round-trip fees, the
81 bps gross target-distance floor, the BTCUSD-only single-symbol
universe, the 4h timeframe, the long-only direction, the 6-bar same-
symbol anti-cluster gap (which remains PROPOSAL-LEVEL LOCKED and does
NOT consume this edit token), the 2026-05-02_2026-06-10 sample tag,
and the no-maker-rebate / no-zero-fee assumptions all remain
inviolable. Modifying any of those invalidates this contract.

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

It freezes the edit RULE and burns the family's one edit token. The
next gate is the HUMAN decision to authorize an edited real-candle
detection run that uses CONTRACTION_FRACTION = 0.7 while keeping all
other C7 frozen numerics. If the eventual edited detection produces
near-zero accepted setups, OR an eventual edited replay still
triggers any pushed auto-rejection rule, Candidate #7 becomes the
seventh ledger entry automatically -- no further edits are allowed.

Chain-gated live on the pushed six-record rejection ledger (C1-C6),
the pushed C7 family proposal, the pushed C7 spec review, the pushed
C7 detector spec + dry-run, the pushed C7 dry-run review, the pushed
C7 real-candle labels review (the only valid reason to spend this
edit), the pushed Overnight Research Autopilot V2, the pushed
Recommendation V1, and the pushed Autopilot Loop V1.
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
from sparta_commander.volatility_compression_expansion_v1_detector_dry_run_review_contract import (
    VERDICT_C7R_FROZEN,
    build_candidate_7_dry_run_review,
)
from sparta_commander.volatility_compression_expansion_v1_detector_spec_dry_run_contract import (
    VERDICT_C7D_READY,
    build_c7_detector_spec_contract,
)
from sparta_commander.volatility_compression_expansion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C7P_READY,
    build_candidate_7_family_proposal,
)
from sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract import (
    EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    EXPECTED_FLOOR_PASS_COUNTS,
    EXPECTED_LABELS_SHA256 as LABELS_SHA256,
    EXPECTED_REJECTED_BY_SCANNER,
    EXPECTED_STATUS_BREAKDOWN,
    EXPECTED_SUMMARY_SHA256 as LABELS_SUMMARY_SHA256,
    EXPECTED_TOTAL_ATTEMPTS,
    HEAD_AT_DETECTION,
    VERDICT_C7L_FROZEN,
    build_c7_labels_review,
)
from sparta_commander.volatility_compression_expansion_v1_spec_review_contract import (
    VERDICT_C7S_READY,
    build_candidate_7_spec_review,
)

C7E_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_single_edit_relaxed"
    "_contraction_decision.v1")
C7E_LABEL = (
    "SPARTA Candidate #7 Single Pre-Committed Edit -- Relaxed "
    "Contraction Fraction (0.6 -> 0.7) "
    "(READ-ONLY, RESEARCH ONLY, SINGLE PARAMETER RELAXATION ONLY, "
    "NOT A RESCUE, NOT A CLAIM)")
C7E_MODE = "RESEARCH_ONLY"
VERDICT_C7E_APPROVED = (
    "CANDIDATE_7_SINGLE_EDIT_RELAXED_CONTRACTION_APPROVED")
VERDICT_C7E_BLOCKED = (
    "CANDIDATE_7_SINGLE_EDIT_RELAXED_CONTRACTION_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_7_EDITED_REAL_CANDLE_DETECTION_RELAXED"
    "_CONTRACTION")
CURRENT_LOOP_STAGE = "detector_and_label_review"
NEXT_LOOP_STAGE = "detector_and_label_review"

# --- The edit token ---------------------------------------------------------
EDIT_TOKEN_USED = 1
EDITS_REMAINING_AFTER_THIS = 0
EDIT_KIND = "relaxed_contraction_fraction_only"
EDIT_SCOPE = (
    "single controlled relaxation of CONTRACTION_FRACTION from 0.6 to "
    "0.7; no other parameter is changed; no detector rewrite; no new "
    "trigger or filter; no fee/floor/stop/target/universe/timeframe/"
    "direction/anti-cluster change; the 6-bar anti-cluster gap is "
    "the proposal-level locked policy and does NOT consume this edit "
    "token")

# --- The frozen edit parameter ---------------------------------------------
EDIT_PARAMETER_NAME = "CONTRACTION_FRACTION"
EDIT_PARAMETER_OLD_VALUE = 0.6
EDIT_PARAMETER_NEW_VALUE = 0.7
EDIT_RULE = {
    "parameter": EDIT_PARAMETER_NAME,
    "old_value": EDIT_PARAMETER_OLD_VALUE,
    "new_value": EDIT_PARAMETER_NEW_VALUE,
    "applies_at": (
        "label_emission_time_in_contraction_window_check_only"),
    "applies_to_all_attempts_uniformly": True,
    "is_a_single_controlled_relaxation_not_a_bundle": True,
    "is_a_strict_less_than_check_against_relaxed_fraction": True,
    "rationale": (
        "the pushed real-candle labels review proved that 122 of 122 "
        "attempts on the 2026-05-02_2026-06-10 BTCUSD 4h window "
        "rejected on the contraction window check, with zero accepted "
        "setups pre and post the 6-bar anti-cluster filter; the only "
        "evidence-supported relaxation is to widen the contraction "
        "fraction by one decile to 0.7; widening further or relaxing "
        "multiple knobs at once would be a rescue bundle and is "
        "forbidden by this contract"),
    "no_intrabar_state": True,
    "no_lookahead": True,
    "deterministic": True,
    "no_other_detector_change": True,
}

# --- Inviolable upstream rules this edit MUST NOT change --------------------
INVIOLABLE_RULES = {
    "atr_length": 14,
    "atr_rolling_average_window_4h_bars": 100,
    "contraction_window_bars": 5,
    "expansion_true_range_multiplier": 1.8,
    "close_in_upper_third_required": True,
    "entry": "close_of_the_event_bar",
    "evaluation_starts": "next_4h_bar_after_event_close",
    "structure_lookback_bars": 10,
    "wider_stop_atr_multiplier": 1.5,
    "stop_distance_formula": (
        "max(wider_stop_atr_multiplier * atr14, "
        "structure_stop_distance)"),
    "target_variants": ("2r", "3r", "4r"),
    "target_price_formula": (
        "entry_price + r_multiple * stop_distance"),
    "fee_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "universe": ("BTCUSD",),
    "timeframe": "4h",
    "direction": "long_only",
    "anti_cluster_min_bar_gap": 6,
    "anti_cluster_is_proposal_level_locked_not_edit_token": True,
    "sample_tag": "2026-05-02_2026-06-10",
    "no_fetch_ever": True,
    "staged_data_never_modified": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# --- Frozen labels-review evidence motivating the edit ---------------------
FROZEN_LABELS_REVIEW_EVIDENCE_FOR_EDIT = {
    "candidate_id": CANDIDATE_ID,
    "labels_sha256": LABELS_SHA256,
    "summary_sha256": LABELS_SUMMARY_SHA256,
    "head_at_detection": HEAD_AT_DETECTION,
    "total_attempts": EXPECTED_TOTAL_ATTEMPTS,
    "accepted_pre_anti_cluster": EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    "accepted_post_anti_cluster": EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    "rejected_by_scanner": EXPECTED_REJECTED_BY_SCANNER,
    "dropped_by_anti_cluster": EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    "status_breakdown": dict(EXPECTED_STATUS_BREAKDOWN),
    "floor_pass_counts": dict(EXPECTED_FLOOR_PASS_COUNTS),
    "all_attempts_rejected_on_contraction_window": True,
    "zero_accepted_setups": True,
    "zero_floor_pass_at_any_variant": True,
    "zero_anti_cluster_drops": True,
    "edit_token_unused_before_this_decision": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
}

# --- Post-edit auto-rejection conditions -----------------------------------
POST_EDIT_AUTO_REJECTION_TRIGGERS = (
    "near_zero_accepted_count_after_edited_detection",
    "any_variant_net_negative_after_edited_relabel_and_replay",
    "any_variant_gross_negative_after_edited_relabel_and_replay",
    "any_variant_hit_rate_below_gross_breakeven_after_edited_"
    "relabel_and_replay",
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline",
    "any_attempt_to_change_an_inviolable_upstream_rule",
    "any_attempt_to_change_more_than_contraction_fraction",
    "any_attempt_to_spend_a_second_edit_on_this_family",
)

# --- Claim locks ------------------------------------------------------------
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
)


def get_c7_single_edit_label() -> str:
    return C7E_LABEL


def build_c7_single_edit_relaxed_contraction(
        repo_root: Any = ".", tracked_paths: Any = ()
) -> dict[str, Any]:
    """Assemble the C7 single-edit relaxed-contraction decision record,
    chain-gated on the full pushed C7 lane plus the six-record
    rejection ledger, Recommendation V1, and Autopilot Loop V1. The
    pushed labels review must certify with zero accepted setups -- the
    only valid reason to spend this edit."""
    record: dict[str, Any] = {
        "schema_version": C7E_SCHEMA_VERSION, "label": C7E_LABEL,
        "mode": C7E_MODE, "lane": "crypto_d1_auto_research",
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
        "this_is_the_only_allowed_c7_edit": True,
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
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "modifies_labels_artifacts": False,
        "computes_pnl_now": False,
        "authorizes_edited_real_candle_detection": False,
        "authorizes_relabel": False, "authorizes_replay": False,
        "authorizes_pnl_now": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_replay_gate": False, "unlocks_relabel_gate": False,
        "unlocks_paper_gate": False, "unlocks_micro_live_gate": False,
        "unlocks_live_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == C6_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    if build_candidate_7_family_proposal()["verdict"] != (
            VERDICT_C7P_READY):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        return record
    if build_candidate_7_spec_review()["verdict"] != VERDICT_C7S_READY:
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append(
            "candidate_7_spec_review_not_certifying")
        return record
    if build_c7_detector_spec_contract()["verdict"] != (
            VERDICT_C7D_READY):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append(
            "candidate_7_detector_spec_not_certifying")
        return record
    if build_candidate_7_dry_run_review()["verdict"] != (
            VERDICT_C7R_FROZEN):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append(
            "candidate_7_dry_run_review_not_certifying")
        return record
    labels_review = build_c7_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C7L_FROZEN:
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append("labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    # the labels review must show zero accepted setups
    if labels_review["expected_accepted_pre_anti_cluster"] != 0 \
            or labels_review["expected_accepted_post_anti_cluster"] \
            != 0:
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append(
            "labels_review_must_show_zero_accepted_to_justify_edit")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C7E_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C7E_APPROVED
    return record


def validate_c7_single_edit_relaxed_contraction(
        record: Any) -> dict[str, Any]:
    """Validate shape, frozen edit rule, inviolable rules, and safety
    invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C7E_APPROVED,
                                VERDICT_C7E_BLOCKED):
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
            "edit_kind_must_be_relaxed_contraction_fraction_only")
    if r.get("edit_parameter_name") != "CONTRACTION_FRACTION":
        errors.append(
            "edit_parameter_must_be_contraction_fraction_only")
    if r.get("edit_parameter_old_value") != 0.6:
        errors.append("edit_old_value_must_be_0_6")
    if r.get("edit_parameter_new_value") != 0.7:
        errors.append("edit_new_value_must_be_0_7")
    rule = r.get("edit_rule") or {}
    if rule != EDIT_RULE:
        errors.append("edit_rule_tampered")
    if rule.get("parameter") != "CONTRACTION_FRACTION":
        errors.append("edit_rule_parameter_must_be_contraction_fraction")
    if rule.get("old_value") != 0.6 or rule.get("new_value") != 0.7:
        errors.append("edit_rule_values_must_be_0_6_and_0_7")
    if rule.get("is_a_single_controlled_relaxation_not_a_bundle"
                ) is not True:
        errors.append("must_be_single_controlled_relaxation_not_bundle")
    if rule.get("no_other_detector_change") is not True:
        errors.append("edit_must_be_relaxation_only_no_detector_rewrite")
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
    if invio.get("atr_rolling_average_window_4h_bars") != 100:
        errors.append("atr_rolling_average_window_changed")
    if invio.get("contraction_window_bars") != 5:
        errors.append("contraction_window_must_remain_5")
    if invio.get("expansion_true_range_multiplier") != 1.8:
        errors.append("expansion_multiplier_changed")
    if invio.get("close_in_upper_third_required") is not True:
        errors.append("close_in_upper_third_rule_weakened")
    if invio.get("structure_lookback_bars") != 10:
        errors.append("structure_lookback_changed")
    if invio.get("wider_stop_atr_multiplier") != 1.5:
        errors.append("wider_stop_atr_multiplier_changed")
    if invio.get("stop_distance_formula") != (
            "max(wider_stop_atr_multiplier * atr14, "
            "structure_stop_distance)"):
        errors.append("wider_stop_formula_changed")
    if invio.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_changed")
    if invio.get("fee_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if invio.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if invio.get("universe") != ["BTCUSD"]:
        errors.append("universe_changed")
    if invio.get("timeframe") != "4h":
        errors.append("timeframe_changed")
    if invio.get("direction") != "long_only":
        errors.append("direction_changed")
    if invio.get("anti_cluster_min_bar_gap") != 6:
        errors.append("anti_cluster_gap_changed")
    if invio.get(
            "anti_cluster_is_proposal_level_locked_not_edit_token"
    ) is not True:
        errors.append("anti_cluster_must_not_be_consumed_by_edit_token")
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
        errors.append("motivation_total_attempts_must_equal_122")
    if ev.get("accepted_pre_anti_cluster") != 0 \
            or ev.get("accepted_post_anti_cluster") != 0:
        errors.append("motivation_accepted_must_be_zero")
    if ev.get("rejected_by_scanner") != EXPECTED_REJECTED_BY_SCANNER:
        errors.append("motivation_rejected_must_equal_122")
    if ev.get("dropped_by_anti_cluster") != 0:
        errors.append("motivation_dropped_must_be_zero")
    if ev.get("status_breakdown") != dict(EXPECTED_STATUS_BREAKDOWN):
        errors.append("motivation_status_breakdown_tampered")
    if ev.get("floor_pass_counts") != dict(EXPECTED_FLOOR_PASS_COUNTS):
        errors.append("motivation_floor_pass_must_be_all_zero")
    if ev.get("all_attempts_rejected_on_contraction_window") is not (
            True):
        errors.append(
            "motivation_must_record_universal_contraction_rejection")
    if ev.get("zero_accepted_setups") is not True:
        errors.append("motivation_zero_accepted_must_be_true")
    if ev.get("zero_floor_pass_at_any_variant") is not True:
        errors.append("motivation_zero_floor_pass_must_be_true")
    if ev.get("edit_token_unused_before_this_decision") is not True:
        errors.append(
            "motivation_edit_token_must_have_been_unused")
    if ev.get("no_replay_run") is not True \
            or ev.get("no_pnl_computed") is not True:
        errors.append("motivation_no_replay_no_pnl_must_hold")
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
                      ("this_is_the_only_allowed_c7_edit", True),
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
                "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_loop_stage") != "detector_and_label_review":
        errors.append("next_loop_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_C7E_APPROVED and r.get("blockers"):
        errors.append("approved_with_blockers")
    return {"valid": not errors, "errors": errors}
