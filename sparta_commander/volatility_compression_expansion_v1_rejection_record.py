"""SPARTA CANDIDATE #7 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY): VOLATILITY_COMPRESSION_EXPANSION_V1.

THE LEDGER ENTRY: Candidate #7 is REJECTED_KEPT_ON_RECORD, reason
EDIT_SPENT_AND_STILL_ZERO_ACCEPTED_REAL_CANDLE_SETUPS_AFTER_RELAXED
_CONTRACTION.

The original C7 real-candle detection produced 0 accepted setups out
of 122 attempts (all rejected on `rejected_contraction_window`). The
pushed single C7 edit token was spent on a single controlled
relaxation of CONTRACTION_FRACTION from 0.6 to 0.7 -- no other
parameter changed, no detector rewrite, no rescue bundle. The edited
real-candle detection then produced 0 accepted setups out of 122
attempts AGAIN (all rejected on `rejected_contraction_window` with
the reason text referencing the relaxed 0.7 threshold). The pushed
POST_EDIT_AUTO_REJECTION_TRIGGERS.near_zero_accepted_count_after_
edited_detection clause has fired.

ATR(14) on the BTCUSD 4h 2026-05-02_2026-06-10 sample window NEVER
dropped below 0.7 x its 100-bar rolling-average ATR for 5 consecutive
completed bars. The volatility-compression-expansion hypothesis is
unsupported on this sample regardless of the contraction threshold
within the family's pre-committed bounds. The single edit allowance
is now SPENT, permanently, on origin/master.

Frozen consequences (validator-permanent): candidate #7 may not
continue as-is; may not receive another edit; further detections /
replays / relabels are not authorized; no paper, no live, no
profitability claim, no winner wording. Seeds are preserved STRICTLY
for future families and are never rescue paths. The lane returns to
HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY after this rejection is
committed and pushed.

This module is declarative -- it freezes the rejection facts and the
chain of pushed contracts that prove them. All artifact shas (six
staged 15m files, original detector labels, original detector
summary, edited detector labels, edited detector summary) are already
verified live by the pushed labels-review contracts which this record
chain-gates on. It runs nothing, fetches nothing, modifies nothing,
and authorizes nothing.

Chain-gated on: the pushed six-record rejection ledger (C1-C6), the
pushed C7 family proposal, the pushed C7 spec review, the pushed C7
detector spec + dry-run, the pushed C7 dry-run review, the pushed C7
real-candle labels review (original), the pushed C7 single-edit
relaxed-contraction decision, the pushed C7 edited real-candle labels
review, the pushed Overnight Research Autopilot V2, the pushed
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
from sparta_commander.volatility_compression_expansion_v1_edited_real_candle_labels_review_contract import (
    EXPECTED_EDITED_LABELS_SHA256,
    EXPECTED_EDITED_SUMMARY_SHA256,
    EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED,
    HEAD_AT_EDITED_DETECTION,
    VERDICT_C7EL_FROZEN,
    build_c7_edited_labels_review,
)
from sparta_commander.volatility_compression_expansion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C7P_READY,
    build_candidate_7_family_proposal,
)
from sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as ORIGINAL_LABELS_SHA256,
    EXPECTED_STAGED_SHAS,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_SUMMARY_SHA256,
    HEAD_AT_DETECTION as HEAD_AT_ORIGINAL_DETECTION,
    VERDICT_C7L_FROZEN,
    build_c7_labels_review,
)
from sparta_commander.volatility_compression_expansion_v1_single_edit_relaxed_contraction_decision_contract import (
    EDIT_PARAMETER_NEW_VALUE,
    EDIT_PARAMETER_OLD_VALUE,
    EDITS_REMAINING_AFTER_THIS,
    EDIT_TOKEN_USED,
    VERDICT_C7E_APPROVED,
    build_c7_single_edit_relaxed_contraction,
)
from sparta_commander.volatility_compression_expansion_v1_spec_review_contract import (
    VERDICT_C7S_READY,
    build_candidate_7_spec_review,
)

RJ7_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_rejection_record.v1")
RJ7_LABEL = ("SPARTA Candidate #7 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "ZERO ACCEPTED REAL-CANDLE SETUPS BEFORE OR AFTER EDIT, "
             "NOT A PROFITABILITY CLAIM)")
RJ7_MODE = "RESEARCH_ONLY"
VERDICT_RJ7_RECORDED = (
    "C7_REJECTED_KEPT_ON_RECORD_EDIT_SPENT_AND_STILL_ZERO_ACCEPTED"
    "_REAL_CANDLE_SETUPS")
VERDICT_RJ7_REVIEW_REJECTED = (
    "C7_REJECTION_RECORD_REVIEW_REJECTED")
VERDICT_RJ7_BLOCKED = "C7_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

# This module is the SEVENTH ledger entry. Future Candidate #8+
# contracts will gate on REJECTION_STATUS exactly like they gate on
# C1-C6.
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "EDIT_SPENT_AND_STILL_ZERO_ACCEPTED_REAL_CANDLE_SETUPS_AFTER"
    "_RELAXED_CONTRACTION")
EDIT_CLASSIFICATION = (
    "C7_EDIT_V1_RELAXED_CONTRACTION_FRACTION_FAILED_REJECT_NEXT")
EDITED_DETECTION_CLASSIFICATION = (
    "C7_ORIGINAL_AND_EDITED_DETECTION_BOTH_ZERO_ACCEPTED_EDIT_SPENT")

# --- Frozen original detection evidence ---------------------------------
EXPECTED_ORIGINAL_DETECTION = {
    "head_at_detection": HEAD_AT_ORIGINAL_DETECTION,
    "labels_sha256": ORIGINAL_LABELS_SHA256,
    "summary_sha256": ORIGINAL_SUMMARY_SHA256,
    "total_attempts": 122,
    "accepted_pre_anti_cluster": 0,
    "accepted_post_anti_cluster": 0,
    "rejected_by_scanner": 122,
    "dropped_by_anti_cluster": 0,
    "status_breakdown": {"rejected_contraction_window": 122},
    "floor_pass_counts": {"2r": 0, "3r": 0, "4r": 0},
    "bars_4h_scanned": 240,
    "all_rejected_on_contraction_window": True,
    "zero_accepted_setups": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
    "no_trading_authorized": True,
}

# --- Frozen single-edit evidence ----------------------------------------
EXPECTED_EDIT = {
    "edit_parameter_name": "CONTRACTION_FRACTION",
    "edit_parameter_old_value": EDIT_PARAMETER_OLD_VALUE,
    "edit_parameter_new_value": EDIT_PARAMETER_NEW_VALUE,
    "edit_token_used": EDIT_TOKEN_USED,
    "edits_remaining_after_this": EDITS_REMAINING_AFTER_THIS,
    "this_was_the_only_allowed_c7_edit": True,
    "no_further_c7_edits_allowed": True,
    "no_other_numeric_changed": True,
    "anti_cluster_gap_remained_proposal_level_locked_not_edit_token":
        True,
    "is_single_controlled_relaxation": True,
    "is_a_rescue_bundle": False,
}

# --- Frozen edited detection evidence -----------------------------------
EXPECTED_EDITED_DETECTION = {
    "head_at_edited_detection": HEAD_AT_EDITED_DETECTION,
    "edited_labels_sha256": EXPECTED_EDITED_LABELS_SHA256,
    "edited_summary_sha256": EXPECTED_EDITED_SUMMARY_SHA256,
    "total_attempts": 122,
    "accepted_pre_anti_cluster": 0,
    "accepted_post_anti_cluster": 0,
    "rejected_by_scanner": 122,
    "dropped_by_anti_cluster": 0,
    "status_breakdown": {"rejected_contraction_window": 122},
    "floor_pass_counts": {"2r": 0, "3r": 0, "4r": 0},
    "bars_4h_scanned": 240,
    "rejection_reason_referenced_strict_below_0_7_x_rolling_avg":
        True,
    "all_rejected_on_contraction_window": True,
    "zero_accepted_setups": True,
    "original_artifacts_unchanged": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
    "no_trading_authorized": True,
    "post_edit_auto_rejection_trigger_fired":
        EXPECTED_POST_EDIT_AUTO_REJECTION_TRIGGER_FIRED,
}

# --- Frozen staged-source pins -------------------------------------------
EXPECTED_STAGED_SOURCE_SHAS = dict(EXPECTED_STAGED_SHAS)

# --- Auto-rejection triggers satisfied -----------------------------------
EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED = {
    "near_zero_accepted_count_after_edited_detection": True,
    "filter_or_edit_spent_and_still_negative_or_zero_accepted": True,
    "any_attempt_to_change_more_than_contraction_fraction": False,
    "any_attempt_to_spend_a_second_edit_on_this_family": False,
    "any_attempt_to_change_an_inviolable_upstream_rule": False,
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline": False,
}

# --- Rejection facts -----------------------------------------------------
REJECTION_FACTS = (
    "candidate #7 is rejected",
    "rejection is kept on record as the seventh ledger entry",
    "reason: the original real-candle detection produced 0 accepted "
    "setups out of 122 attempts; the single authorized structure-"
    "only edit was spent on a controlled relaxation of CONTRACTION"
    "_FRACTION from 0.6 to 0.7; the post-edit real-candle detection "
    "produced 0 accepted setups out of 122 attempts AGAIN",
    "the pushed POST_EDIT_AUTO_REJECTION_TRIGGERS.near_zero_accepted"
    "_count_after_edited_detection clause has fired",
    "the single edit allowance is now spent permanently on "
    "origin/master",
    "candidate #7 may not continue as-is",
    "candidate #7 may not receive another edit",
    "further detections, replays, and relabels are not authorized",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
    "no winner wording permitted",
    "candidate #7 has no accepted real-candle setups, no replay, no "
    "pnl, no trading output",
)

EVIDENCE_NOTES = (
    "the volatility-compression-expansion hypothesis is unsupported "
    "on the btcusd 4h 2026-05-02_2026-06-10 window regardless of "
    "the contraction threshold within the family's pre-committed "
    "bounds (0.6 in pushed spec, 0.7 in pushed edit)",
    "atr(14) never dropped below 0.7 x its 100-bar rolling-average "
    "for 5 consecutive completed bars in this window",
    "the relaxation from 0.6 to 0.7 made zero structural difference: "
    "same 122 attempts, same 122 contraction-window rejections, same "
    "zero accepted setups",
    "the sample window of 240 4h bars (after warm-up: 122 evaluable "
    "bars covering ~21 days) is too short to capture any qualifying "
    "volatility-regime episode under either fraction; a longer "
    "window or a different timeframe would be required to falsify "
    "the family hypothesis -- but that is a NEW family proposal, not "
    "a c7 continuation",
    "no replay was run on the c7 lane; no pnl was computed; no "
    "trading-adjacent capability was authorized at any stage",
    "anti-cluster gap stayed proposal-level locked at 6 bars and did "
    "not consume the edit token; this protection held",
    "every staged-data sha and every detector-artifact sha (original "
    "and edited) was sha-pinned and re-verified at every gate",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "single_symbol_volatility_regime_triggers_on_short_windows_may"
    "_be_too_sparse_to_label_meaningfully",
    "atr_contraction_check_with_strict_less_than_against_a_rolling"
    "_average_is_a_useful_primitive_but_requires_longer_history",
    "label_time_anti_cluster_filters_remain_a_real_structural_tool"
    "_inherited_from_c6_lesson",
    "fee_aware_geometry_with_an_81_bps_floor_remains_inviolable",
    "any_future_volatility_regime_family_must_target_a_longer_or"
    "_different_window_and_must_be_a_new_clean_hypothesis",
    "do_not_reuse_c7_as_is",
    "any_future_candidate_must_be_a_new_clean_hypothesis_through_the"
    "_autopilot_loop",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

# Future candidate-recommendation logic must blacklist the C7 family.
FUTURE_FAMILY_BLACKLIST_ADDITION = "volatility_compression_expansion"
FUTURE_FAMILY_BLACKLIST_REASON = (
    "candidate_7_rejected_kept_on_record_zero_accepted_after_relaxed"
    "_contraction_edit_must_not_be_reproposed_as_is")

# --- The full pushed C7 evidence chain (for permanence) ------------------
PUSHED_EVIDENCE_CHAIN = (
    "volatility_compression_expansion_v1_family_proposal_contract",
    "volatility_compression_expansion_v1_spec_review_contract",
    "volatility_compression_expansion_v1_detector_spec_dry_run"
    "_contract",
    "volatility_compression_expansion_v1_detector_dry_run_review"
    "_contract",
    "volatility_compression_expansion_v1_real_candle_labels_review"
    "_contract",
    "volatility_compression_expansion_v1_single_edit_relaxed"
    "_contraction_decision_contract",
    "volatility_compression_expansion_v1_edited_real_candle_labels"
    "_review_contract",
    "strategy_factory_overnight_research_autopilot_v2_contract",
    "strategy_factory_candidate_recommendation_v1_contract",
    "strategy_factory_autopilot_research_loop_v1_contract",
)

PRIOR_LEDGER_FAMILIES = (
    "ny_session_fvg_choch_v3",
    "crypto_intraday_breakout_pullback_structure_v2",
    "btc_sol_long_trend_continuation_v1",
    "sol_btc_long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation_v1",
    "multi_symbol_relative_strength_rotation_filter",
)


def get_c7_rejection_record_label() -> str:
    return RJ7_LABEL


def build_c7_rejection_record(repo_root: Any = ".",
                              tracked_paths: Any = ()
                              ) -> dict[str, Any]:
    """Assemble the C7 seventh-ledger rejection record. Chain-gated on
    the full pushed C7 evidence chain plus the six-record rejection
    ledger, Recommendation V1, Autopilot V1, and V2."""
    record: dict[str, Any] = {
        "schema_version": RJ7_SCHEMA_VERSION, "label": RJ7_LABEL,
        "mode": RJ7_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "edit_classification": EDIT_CLASSIFICATION,
        "edited_detection_classification":
            EDITED_DETECTION_CLASSIFICATION,
        "ledger_position": 7,
        "prior_ledger_families": list(PRIOR_LEDGER_FAMILIES),
        "expected_original_detection":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_ORIGINAL_DETECTION.items()},
        "expected_edit":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_EDIT.items()},
        "expected_edited_detection":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_EDITED_DETECTION.items()},
        "expected_staged_source_shas":
            dict(EXPECTED_STAGED_SOURCE_SHAS),
        "auto_rejection_triggers_satisfied":
            dict(EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED),
        "rejection_facts": list(REJECTION_FACTS),
        "evidence_notes": list(EVIDENCE_NOTES),
        "seeds_for_future_families_only":
            list(SEEDS_FOR_FUTURE_FAMILIES_ONLY),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "future_family_blacklist_addition":
            FUTURE_FAMILY_BLACKLIST_ADDITION,
        "future_family_blacklist_reason":
            FUTURE_FAMILY_BLACKLIST_REASON,
        "pushed_evidence_chain": list(PUSHED_EVIDENCE_CHAIN),
        "edit_allowance_spent": True,
        "candidate_7_may_continue_as_is": False,
        "candidate_7_may_receive_another_edit": False,
        "further_detections_authorized": False,
        "further_replays_authorized": False,
        "further_relabels_authorized": False,
        "ledger_now_contains_seven_records": True,
        "prior_six_records_unchanged": True,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
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
        "applies_another_edit": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    # five-record ledger (C1-C5)
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("five_record_c1_c5_ledger_broken")
        return record
    # six-record ledger (C6 must also be REJECTED)
    if C6_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("c6_ledger_entry_broken")
        return record
    # full C7 evidence chain
    if build_candidate_7_family_proposal()["verdict"] != (
            VERDICT_C7P_READY):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        return record
    if build_candidate_7_spec_review()["verdict"] != VERDICT_C7S_READY:
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_spec_review_not_certifying")
        return record
    if build_c7_detector_spec_contract()["verdict"] != (
            VERDICT_C7D_READY):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_detector_spec_not_certifying")
        return record
    if build_candidate_7_dry_run_review()["verdict"] != (
            VERDICT_C7R_FROZEN):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_dry_run_review_not_certifying")
        return record
    labels_review = build_c7_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C7L_FROZEN:
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    single_edit = build_c7_single_edit_relaxed_contraction(
        repo_root, tracked_paths)
    if single_edit["verdict"] != VERDICT_C7E_APPROVED:
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_single_edit_decision_not_certifying")
        return record
    edited_labels = build_c7_edited_labels_review(repo_root,
                                                  tracked_paths)
    if edited_labels["verdict"] != VERDICT_C7EL_FROZEN:
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "candidate_7_edited_labels_review_not_certifying")
        record["blockers"].extend(edited_labels["failures"])
        return record
    # the edited labels review must indeed record the trigger fired
    trigger_status = edited_labels.get(
        "expected_auto_rejection_trigger_status") or {}
    if trigger_status.get(
            "near_zero_accepted_count_after_edited_detection") is not (
            True):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "near_zero_accepted_count_trigger_did_not_fire")
        return record
    # the edit token must indeed have been spent
    if single_edit.get("edit_token_used") != 1 or single_edit.get(
            "edits_remaining_after_this") != 0:
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("edit_token_not_spent")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_RJ7_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_RJ7_RECORDED
    return record


def validate_c7_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, permanence flags. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ7_RECORDED,
                                VERDICT_RJ7_REVIEW_REJECTED,
                                VERDICT_RJ7_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if r.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if r.get("edit_classification") != EDIT_CLASSIFICATION:
        errors.append("edit_classification_tampered")
    if r.get("edited_detection_classification") != (
            EDITED_DETECTION_CLASSIFICATION):
        errors.append("edited_detection_classification_tampered")
    if r.get("ledger_position") != 7:
        errors.append("ledger_position_tampered")
    if tuple(r.get("prior_ledger_families") or ()) != (
            PRIOR_LEDGER_FAMILIES):
        errors.append("prior_ledger_families_tampered")
    expected_orig = {key: (dict(value) if isinstance(value, dict)
                           else value)
                     for key, value
                     in EXPECTED_ORIGINAL_DETECTION.items()}
    if r.get("expected_original_detection") != expected_orig:
        errors.append("original_detection_tampered")
    expected_edit = {key: (dict(value) if isinstance(value, dict)
                           else value)
                     for key, value in EXPECTED_EDIT.items()}
    if r.get("expected_edit") != expected_edit:
        errors.append("edit_evidence_tampered")
    expected_edited = {key: (dict(value) if isinstance(value, dict)
                             else value)
                       for key, value
                       in EXPECTED_EDITED_DETECTION.items()}
    if r.get("expected_edited_detection") != expected_edited:
        errors.append("edited_detection_tampered")
    if r.get("expected_staged_source_shas") != (
            EXPECTED_STAGED_SOURCE_SHAS):
        errors.append("staged_source_shas_tampered")
    if r.get("auto_rejection_triggers_satisfied") != (
            EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED):
        errors.append("auto_rejection_triggers_tampered")
    if tuple(r.get("rejection_facts") or ()) != REJECTION_FACTS:
        errors.append("rejection_facts_tampered")
    if tuple(r.get("evidence_notes") or ()) != EVIDENCE_NOTES:
        errors.append("evidence_notes_tampered")
    if tuple(r.get("seeds_for_future_families_only") or ()) != (
            SEEDS_FOR_FUTURE_FAMILIES_ONLY):
        errors.append("seeds_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    if r.get("future_family_blacklist_addition") != (
            FUTURE_FAMILY_BLACKLIST_ADDITION):
        errors.append("blacklist_addition_tampered")
    if r.get("future_family_blacklist_reason") != (
            FUTURE_FAMILY_BLACKLIST_REASON):
        errors.append("blacklist_reason_tampered")
    if tuple(r.get("pushed_evidence_chain") or ()) != (
            PUSHED_EVIDENCE_CHAIN):
        errors.append("pushed_evidence_chain_tampered")
    if r.get("edit_allowance_spent") is not True:
        errors.append("edit_allowance_must_be_spent")
    for key in ("candidate_7_may_continue_as_is",
                "candidate_7_may_receive_another_edit",
                "further_detections_authorized",
                "further_replays_authorized",
                "further_relabels_authorized"):
        if r.get(key) is not False:
            errors.append("permanence_flag_wrong:" + key)
    if r.get("ledger_now_contains_seven_records") is not True:
        errors.append("ledger_position_seven_must_be_true")
    if r.get("prior_six_records_unchanged") is not True:
        errors.append("prior_six_records_unchanged_must_be_true")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
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
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "computes_pnl_now", "applies_another_edit",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    return {"valid": not errors, "errors": errors}
