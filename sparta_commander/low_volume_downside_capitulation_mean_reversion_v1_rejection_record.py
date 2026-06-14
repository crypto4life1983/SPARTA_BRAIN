"""SPARTA CANDIDATE #9 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY, REJECTED KEPT ON RECORD, EDIT SPENT ON RELAXED Z-SCORE
THRESHOLD AND SAMPLE-SIZE STILL BELOW THRESHOLD AFTER EDITED
DETECTION, NOT A PROFITABILITY CLAIM):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Closes out Candidate #9 on origin/master and freezes the NINTH
rejected-family ledger entry. The pushed C9 evidence chain (family
proposal -> spec review -> detector spec/dry-run -> dry-run review
-> original real-candle labels review -> single-edit decision ->
edited real-candle labels review) produced:

ORIGINAL DETECTION (pre-edit, DOWNSIDE_Z_SCORE_THRESHOLD = -2.0):
  - 3,840 staged BTCUSD 15m bars scanned;
  - 8 joint-trigger attempts;
  - 1 accepted setup before and after the 8-bar anti-cluster filter;
  - 7 rejected by scanner (all on geometry_floor);
  - sample-size adequacy FAILED: 1 accepted-post < 20 threshold;
  - the failure was a SAMPLE-SIZE STRUCTURAL FAILURE, not replay
    negativity; no replay was run.

SINGLE EDIT TOKEN SPENT:
  - parameter: DOWNSIDE_Z_SCORE_THRESHOLD
  - old value: -2.0
  - new value: -1.5 (one half-sigma less strict);
  - rationale: directly address trigger sparsity while preserving
    the volume condition (the structural microstructure edge);
  - all other C9 numerics and rules unchanged;
  - anti-cluster gap (8), sample-size threshold (20), AND explicit-
    edge-argument field all remained PROPOSAL/SPEC-LEVEL LOCKED
    and NONE consumed the edit token;
  - the edit was the single allowed C9 edit; 0 remaining.

EDITED DETECTION (post-edit, DOWNSIDE_Z_SCORE_THRESHOLD = -1.5):
  - 3,840 same staged BTCUSD 15m bars scanned;
  - 27 joint-trigger attempts (vs 8 original; 3.4x increase from
    the relaxed z threshold, matching the predicted normal-
    distribution lower-tail expansion);
  - 5 accepted setups before and after the 8-bar anti-cluster
    filter;
  - 22 rejected by scanner (12 on geometry_floor + 10 on a NEW
    failure mode that did not appear in the original: rejected
    _entry_bar_close_at_or_below_trigger_bar_low; entry bars
    continued through the trigger low, structurally falsifying the
    asymmetry thesis on those bars);
  - sample-size adequacy STRUCTURALLY STILL FAILED: 5 accepted-
    post < 20 threshold;
  - post-edit auto-rejection trigger `sample_size_still_below
    _threshold_after_edited_detection` FIRED -- this is one of the
    12 post-edit auto-rejection triggers frozen in the pushed C9
    single-edit decision.

REJECTION_STATUS = REJECTED_KEPT_ON_RECORD. The single C9 edit
allowance is now SPENT permanently (on DOWNSIDE_Z_SCORE_THRESHOLD);
0 edits remaining. Anti-cluster gap (8) and sample-size adequacy
threshold (20) and explicit-edge-argument field remain proposal-
level locked and were never edit-token usage. The relaxed z
threshold expanded triggers 3.4x as predicted but accepted setups
only grew from 1 to 5; the joint condition's volume gate (the
structural microstructure edge) remains the binding constraint, not
the z-score. The C9 hypothesis's explicit edge argument was
empirically CORRECT about thin-book panic excursions being rare;
the data on this 40-day sample does not support C9 producing
enough qualifying events to be evaluable. No replay was authorized
because the sample-size gate failed.

The C9 family `low_volume_downside_capitulation_mean_reversion`
becomes the NINTH entry in the rejected-family blacklist. The next
path forward is a brand-new Candidate #10 family proposal that must
clear the V5 blacklist (this module exports
FUTURE_FAMILY_BLACKLIST_ADDITION as the source of truth for the V5
update). Candidate #9 may NOT be re-proposed as-is.

NO edge demonstrated. NO winner. NO profitability claim. NO paper
approval. NO live approval. NO trading capability authorized. The
HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY after this rejection is the
only forward path.

This module observes the pushed C9 chain (original labels review +
single-edit decision + edited labels review) plus the pushed
staged-source SHA pins READ-ONLY and certifies the ninth ledger
entry. It runs nothing, fetches nothing, modifies nothing, and
authorizes nothing.

Chain-gated live on: the pushed eight-record rejection ledger
(C1-C8), the pushed C9 family proposal, the pushed C9 spec review,
the pushed C9 detector spec + dry-run, the pushed C9 dry-run
review, the pushed C9 original real-candle labels review, the
pushed C9 single-edit decision, the pushed C9 edited real-candle
labels review, the pushed V4 rejected-family blacklist, the pushed
V3 blacklist, the pushed Overnight Research Autopilot V2, the
pushed Recommendation V1, and the pushed Autopilot Loop V1.
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
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_edited_real_candle_labels_review_contract import (
    EXPECTED_EDITED_LABELS_SHA256,
    EXPECTED_EDITED_SUMMARY_SHA256,
    VERDICT_C9EL_FROZEN,
    build_c9_edited_labels_review,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as ORIGINAL_LABELS_SHA256,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_SUMMARY_SHA256,
    VERDICT_C9L_FROZEN,
    build_c9_labels_review,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_single_edit_relaxed_z_score_decision_contract import (
    EDIT_PARAMETER_NAME,
    EDIT_PARAMETER_NEW_VALUE,
    EDIT_PARAMETER_OLD_VALUE,
    VERDICT_C9E_APPROVED,
    build_c9_single_edit_relaxed_z_score,
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

RJ9_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_rejection"
    "_record.v1")
RJ9_LABEL = ("SPARTA Candidate #9 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "EDIT SPENT ON RELAXED Z-SCORE THRESHOLD AND SAMPLE-"
             "SIZE STILL BELOW THRESHOLD AFTER EDITED DETECTION, "
             "NOT A PROFITABILITY CLAIM)")
RJ9_MODE = "RESEARCH_ONLY"
VERDICT_RJ9_RECORDED = (
    "C9_REJECTED_KEPT_ON_RECORD_EDIT_SPENT_ON_RELAXED_Z_AND_SAMPLE"
    "_SIZE_STILL_BELOW_THRESHOLD")
VERDICT_RJ9_REVIEW_REJECTED = (
    "C9_REJECTION_RECORD_REVIEW_REJECTED")
VERDICT_RJ9_BLOCKED = "C9_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

# Ninth ledger entry. Future Candidate #10+ contracts will gate on
# REJECTION_STATUS exactly like they gate on C1-C8.
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "EDIT_SPENT_ON_RELAXED_DOWNSIDE_Z_SCORE_THRESHOLD_AND_SAMPLE"
    "_SIZE_STILL_BELOW_THRESHOLD_AFTER_EDITED_DETECTION")
EDIT_CLASSIFICATION = (
    "C9_EDIT_V1_RELAXED_DOWNSIDE_Z_SCORE_THRESHOLD_FAILED_REJECT"
    "_NEXT")
EDITED_DETECTION_CLASSIFICATION = (
    "C9_ORIGINAL_1_ACCEPTED_AND_EDITED_5_ACCEPTED_BOTH_BELOW"
    "_SAMPLE_SIZE_THRESHOLD_20")

HEAD_AT_ORIGINAL_DETECTION = (
    "ba02fdea73bc344cd8e9fcd1e28a32c60932b63b")
HEAD_AT_SINGLE_EDIT_DECISION = (
    "6e88a827be09ab24b062c47aa4d1e313c39e3dfb")
HEAD_AT_EDITED_DETECTION = (
    "ae65340d9999d7bc91ca11db608531e0e60f7d5c")

# --- Frozen original detection evidence ---------------------------------
EXPECTED_ORIGINAL_DETECTION = {
    "head_at_detection": HEAD_AT_ORIGINAL_DETECTION,
    "labels_sha256": ORIGINAL_LABELS_SHA256,
    "summary_sha256": ORIGINAL_SUMMARY_SHA256,
    "total_attempts": 8,
    "accepted_pre_anti_cluster": 1,
    "accepted_post_anti_cluster": 1,
    "rejected_by_scanner": 7,
    "dropped_by_anti_cluster": 0,
    "status_breakdown": {
        "accepted_for_replay_review": 1,
        "rejected_geometry_floor": 7,
    },
    "sample_size_threshold_min_required": 20,
    "sample_size_satisfied": False,
    "sample_size_structural_failure": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
    "no_trading_authorized": True,
}

# --- Frozen single-edit evidence ----------------------------------------
EXPECTED_EDIT = {
    "edit_parameter_name": "DOWNSIDE_Z_SCORE_THRESHOLD",
    "edit_parameter_old_value": EDIT_PARAMETER_OLD_VALUE,
    "edit_parameter_new_value": EDIT_PARAMETER_NEW_VALUE,
    "head_at_single_edit_decision": HEAD_AT_SINGLE_EDIT_DECISION,
    "edit_token_used": 1,
    "edits_remaining_after_this": 0,
    "this_was_the_only_allowed_c9_edit": True,
    "no_further_c9_edits_allowed": True,
    "no_other_numeric_changed": True,
    "anti_cluster_gap_remained_proposal_level_locked_not_edit_token":
        True,
    "sample_size_threshold_remained_proposal_level_locked_not_edit"
    "_token": True,
    "explicit_edge_argument_field_remained_proposal_level_locked_not"
    "_edit_token": True,
    "is_single_controlled_relaxation": True,
    "is_a_rescue_bundle": False,
}

# --- Frozen edited detection evidence -----------------------------------
EXPECTED_EDITED_DETECTION = {
    "head_at_edited_detection": HEAD_AT_EDITED_DETECTION,
    "edited_labels_sha256": EXPECTED_EDITED_LABELS_SHA256,
    "edited_summary_sha256": EXPECTED_EDITED_SUMMARY_SHA256,
    "total_attempts": 27,
    "accepted_pre_anti_cluster": 5,
    "accepted_post_anti_cluster": 5,
    "rejected_by_scanner": 22,
    "dropped_by_anti_cluster": 0,
    "status_breakdown": {
        "accepted_for_replay_review": 5,
        "rejected_geometry_floor": 12,
        "rejected_entry_bar_close_at_or_below_trigger_bar_low": 10,
    },
    "sample_size_threshold_min_required": 20,
    "sample_size_satisfied_after_edit": False,
    "sample_size_still_below_threshold_after_edited_detection": True,
    "attempts_increased_from_8_to_27_a_3_4x_increase_matching"
    "_lower_tail_expansion": True,
    "accepted_increased_from_1_to_5": True,
    "new_failure_mode_observed_entry_bar_close_at_or_below_trigger"
    "_bar_low_10_setups": True,
    "original_artifacts_unchanged": True,
    "no_replay_run": True,
    "no_pnl_computed": True,
    "no_trading_authorized": True,
    "post_edit_auto_rejection_trigger_fired": True,
    "post_edit_auto_rejection_trigger_name": (
        "sample_size_still_below_threshold_after_edited_detection"),
}

# --- Frozen staged-source pins -------------------------------------------
EXPECTED_STAGED_SOURCE_SHAS = {
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv":
        "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd"
        "1298ee9f14",
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv":
        "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa16"
        "70aed4956d",
}

# --- Auto-rejection triggers satisfied ---------------------------------
EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED = {
    "sample_size_still_below_threshold_after_edited_detection": True,
    "edit_token_was_spent_on_single_allowed_parameter_only": True,
    "any_attempt_to_change_more_than_downside_z_score_threshold":
        False,
    "any_attempt_to_spend_a_second_edit_on_this_family": False,
    "any_attempt_to_change_an_inviolable_upstream_rule": False,
    "any_attempt_to_modify_anti_cluster_gap_via_this_edit": False,
    "any_attempt_to_modify_sample_size_threshold_via_this_edit":
        False,
    "any_attempt_to_modify_explicit_edge_argument_field_via_this"
    "_edit": False,
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline": False,
}

# --- Rejection facts ---------------------------------------------------
REJECTION_FACTS = (
    "candidate #9 is rejected",
    "rejection is kept on record as the ninth ledger entry",
    "reason: the original real-candle detection produced 1 accepted-"
    "post-anti-cluster setup out of 8 attempts on 3840 btcusd 15m "
    "bars, below the proposal/spec-locked sample-size adequacy "
    "threshold of 20 (sample-size structural failure); the single "
    "authorized structure-only edit was spent on a controlled "
    "relaxation of DOWNSIDE_Z_SCORE_THRESHOLD from -2.0 to -1.5; the "
    "post-edit real-candle detection increased attempts from 8 to "
    "27 (a 3.4x increase, matching the predicted normal-distribution "
    "lower-tail expansion) and increased accepted setups from 1 to "
    "5; sample-size adequacy STILL FAILED post-edit: 5 < 20",
    "the pushed POST_EDIT_AUTO_REJECTION_TRIGGERS.sample_size_still"
    "_below_threshold_after_edited_detection clause has fired",
    "the single edit allowance is now spent permanently on "
    "origin/master at the C9 single-edit decision commit "
    "6e88a827be09ab24b062c47aa4d1e313c39e3dfb",
    "candidate #9 may not continue as-is",
    "candidate #9 may not receive another edit",
    "further detections, replays, and relabels are not authorized",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
    "no winner wording permitted",
    "candidate #9 has 1 accepted-original and 5 accepted-edited real-"
    "candle setups; no replay was run; no pnl was computed; no "
    "trading-adjacent capability was authorized at any stage",
)

EVIDENCE_NOTES = (
    "the low-volume-downside-capitulation-mean-reversion hypothesis "
    "is unsupported on the btcusd 15m 2026-05-02_2026-06-10 window "
    "regardless of the downside-z-score threshold within the "
    "family's pre-committed bounds (-2.0 in pushed spec, -1.5 in "
    "pushed edit)",
    "the joint price-AND-volume trigger is structurally rare: at "
    "the original -2.0sigma threshold the joint fired on 8 of 3840 "
    "bars (0.21%); at the relaxed -1.5sigma threshold the joint "
    "fired on 27 of 3840 bars (0.70%); both rates are well below "
    "the marginal z-score predictions of 2.3% and 6.7% respectively, "
    "confirming that the volume condition (the structural "
    "microstructure edge) is the binding constraint, not the z-"
    "score",
    "the post-edit detection revealed a NEW failure mode that did "
    "not appear in the original: 10 trigger candidates had entry "
    "bars whose close continued through the trigger bar's low, "
    "structurally falsifying the asymmetry thesis on those bars; "
    "the entry-bar invalidation gate correctly filtered these out "
    "as the C9 explicit edge argument designed it to",
    "the C9 hypothesis's edge argument was empirically CORRECT "
    "about thin-book panic excursions being rare; the data on this "
    "40-day sample does not support C9 producing enough qualifying "
    "events to be evaluable, even with the one allowed structure-"
    "only edit applied",
    "no replay was run on the c9 lane (the sample-size adequacy "
    "gate failed both pre- and post-edit); no pnl was computed; no "
    "trading-adjacent capability was authorized at any stage",
    "anti-cluster gap stayed proposal-level locked at 8 bars and "
    "did not consume the edit token; this protection held",
    "sample-size adequacy threshold stayed proposal-level locked "
    "at 20 accepted setups and did not consume the edit token; the "
    "structural-failure flag was recorded both pre- and post-edit "
    "WITHOUT spending the token; this protection held",
    "explicit-edge-argument field stayed proposal/spec-level locked "
    "and did not consume the edit token; this protection held",
    "every staged-data sha and every detector-artifact sha "
    "(original and edited) was sha-pinned and re-verified at every "
    "gate",
    "the single c9 edit token is now permanently spent on the z-"
    "score threshold; the family is closed out; the edit-token "
    "budget is not carried over to any future candidate (each "
    "family gets its own one-allowed edit)",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "joint_price_and_volume_thresholds_can_be_structurally_too"
    "_sparse_when_both_conditions_are_strict_low_probability_events",
    "the_binding_constraint_in_a_joint_trigger_is_the_intersection"
    "_rate_not_the_marginal_rates_so_a_single_edit_to_one_threshold"
    "_cannot_rescue_a_family_where_the_other_condition_is_the"
    "_bottleneck",
    "future_families_must_pre_justify_sample_size_adequacy_for"
    "_joint_or_intersection_triggers_at_proposal_time_or_offer_a"
    "_disjunctive_trigger_structure_instead",
    "an_edge_argument_can_be_empirically_correct_about_signal"
    "_rarity_yet_the_family_can_still_fail_the_sample_size_gate"
    "_in_a_fixed_window_research_only_lane",
    "label_time_anti_cluster_filters_remain_a_real_structural_tool"
    "_inherited_from_c6_lesson",
    "proposal_level_sample_size_adequacy_thresholds_remain_a_real"
    "_structural_tool_inherited_from_c7_lesson",
    "explicit_edge_argument_at_proposal_time_remains_a_real"
    "_structural_tool_inherited_from_c8_lesson",
    "fee_aware_geometry_with_an_81_bps_floor_remains_inviolable",
    "any_future_microstructure_family_must_provide_an_explicit"
    "_argument_that_the_joint_or_intersection_trigger_will_fire"
    "_often_enough_within_the_available_sample_window",
    "do_not_reuse_c9_as_is",
    "any_future_candidate_must_be_a_new_clean_hypothesis_through"
    "_the_autopilot_loop",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

# Future candidate-recommendation logic must blacklist the C9 family.
FUTURE_FAMILY_BLACKLIST_ADDITION = (
    "low_volume_downside_capitulation_mean_reversion")
FUTURE_FAMILY_BLACKLIST_REASON = (
    "candidate_9_rejected_kept_on_record_edit_spent_on_relaxed_z"
    "_score_threshold_and_sample_size_still_below_threshold_after"
    "_edited_detection_must_not_be_reproposed_as_is")

# --- The full pushed C9 evidence chain (for permanence) ----------------
PUSHED_EVIDENCE_CHAIN = (
    "low_volume_downside_capitulation_mean_reversion_v1_family"
    "_proposal_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_spec_review"
    "_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_detector"
    "_spec_dry_run_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_dry_run"
    "_review_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_real_candle"
    "_labels_review_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_single_edit"
    "_relaxed_z_score_decision_contract",
    "low_volume_downside_capitulation_mean_reversion_v1_edited_real"
    "_candle_labels_review_contract",
    "strategy_factory_rejected_family_blacklist_v4_contract",
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
    "volatility_compression_expansion",
    "liquidity_sweep_mean_reversion",
)


def get_c9_rejection_record_label() -> str:
    return RJ9_LABEL


def build_c9_rejection_record(repo_root: Any = ".",
                              tracked_paths: Any = ()
                              ) -> dict[str, Any]:
    """Assemble the C9 ninth-ledger rejection record. Chain-gated on
    the full pushed C9 evidence chain plus the eight-record rejection
    ledger, V4, V3, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": RJ9_SCHEMA_VERSION, "label": RJ9_LABEL,
        "mode": RJ9_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "edit_classification": EDIT_CLASSIFICATION,
        "edited_detection_classification":
            EDITED_DETECTION_CLASSIFICATION,
        "ledger_position": 9,
        "prior_ledger_families": list(PRIOR_LEDGER_FAMILIES),
        "head_at_original_detection": HEAD_AT_ORIGINAL_DETECTION,
        "head_at_single_edit_decision":
            HEAD_AT_SINGLE_EDIT_DECISION,
        "head_at_edited_detection": HEAD_AT_EDITED_DETECTION,
        "expected_original_detection":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_ORIGINAL_DETECTION.items()},
        "expected_edit":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_EDIT.items()},
        "expected_edited_detection":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in
             EXPECTED_EDITED_DETECTION.items()},
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
        "candidate_9_may_continue_as_is": False,
        "candidate_9_may_receive_another_edit": False,
        "further_detections_authorized": False,
        "further_replays_authorized": False,
        "further_relabels_authorized": False,
        "ledger_now_contains_nine_records": True,
        "prior_eight_records_unchanged": True,
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
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "modifies_labels_artifacts": False,
        "modifies_edited_labels_artifacts": False,
        "computes_pnl_now": False,
        "applies_another_edit": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading":
            False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS)
    if not all(s == "REJECTED_KEPT_ON_RECORD" for s in statuses):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    if build_candidate_9_family_proposal()["verdict"] != (
            VERDICT_C9P_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_proposal_not_certifying")
        return record
    if build_candidate_9_spec_review()["verdict"] != VERDICT_C9S_READY:
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_spec_review_not_certifying")
        return record
    if build_candidate_9_detector_spec_contract()["verdict"] != (
            VERDICT_C9D_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_detector_spec_not_certifying")
        return record
    if build_candidate_9_dry_run_review()["verdict"] != (
            VERDICT_C9R_FROZEN):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_dry_run_review_not_certifying")
        return record
    if build_c9_labels_review(repo_root, tracked_paths)[
            "verdict"] != VERDICT_C9L_FROZEN:
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_original_labels_review_not_certifying")
        return record
    if build_c9_single_edit_relaxed_z_score(
            repo_root, tracked_paths)["verdict"] != (
            VERDICT_C9E_APPROVED):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_single_edit_decision_not_certifying")
        return record
    # The single-edit decision must show z-score parameter
    if EDIT_PARAMETER_NAME != "DOWNSIDE_Z_SCORE_THRESHOLD" \
            or EDIT_PARAMETER_OLD_VALUE != -2.0 \
            or EDIT_PARAMETER_NEW_VALUE != -1.5:
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "single_edit_decision_parameter_or_values_drifted")
        return record
    if build_c9_edited_labels_review(
            repo_root, tracked_paths)["verdict"] != (
            VERDICT_C9EL_FROZEN):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "candidate_9_edited_labels_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_RJ9_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_RJ9_RECORDED
    return record


def validate_c9_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ9_RECORDED,
                                VERDICT_RJ9_REVIEW_REJECTED,
                                VERDICT_RJ9_BLOCKED):
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
    if r.get("ledger_position") != 9:
        errors.append("ledger_position_must_be_9")
    if tuple(r.get("prior_ledger_families") or ()) != (
            PRIOR_LEDGER_FAMILIES):
        errors.append("prior_ledger_families_tampered")
    if r.get("head_at_original_detection") != (
            HEAD_AT_ORIGINAL_DETECTION):
        errors.append("head_at_original_detection_tampered")
    if r.get("head_at_single_edit_decision") != (
            HEAD_AT_SINGLE_EDIT_DECISION):
        errors.append("head_at_single_edit_decision_tampered")
    if r.get("head_at_edited_detection") != (
            HEAD_AT_EDITED_DETECTION):
        errors.append("head_at_edited_detection_tampered")
    if r.get("future_family_blacklist_addition") != (
            FUTURE_FAMILY_BLACKLIST_ADDITION):
        errors.append("future_blacklist_addition_tampered")
    if r.get("future_family_blacklist_reason") != (
            FUTURE_FAMILY_BLACKLIST_REASON):
        errors.append("future_blacklist_reason_tampered")
    if tuple(r.get("pushed_evidence_chain") or ()) != (
            PUSHED_EVIDENCE_CHAIN):
        errors.append("pushed_evidence_chain_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_be_never_rescue")
    if tuple(r.get("seeds_for_future_families_only") or ()) != (
            SEEDS_FOR_FUTURE_FAMILIES_ONLY):
        errors.append("seeds_for_future_families_only_tampered")
    if tuple(r.get("rejection_facts") or ()) != REJECTION_FACTS:
        errors.append("rejection_facts_tampered")
    if tuple(r.get("evidence_notes") or ()) != EVIDENCE_NOTES:
        errors.append("evidence_notes_tampered")
    if r.get("expected_staged_source_shas") != (
            EXPECTED_STAGED_SOURCE_SHAS):
        errors.append("staged_source_shas_tampered")
    if r.get("auto_rejection_triggers_satisfied") != (
            EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED):
        errors.append("auto_rejection_triggers_tampered")
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
        errors.append("expected_edit_tampered")
    expected_edited = {key: (dict(value) if isinstance(value, dict)
                             else value)
                       for key, value
                       in EXPECTED_EDITED_DETECTION.items()}
    if r.get("expected_edited_detection") != expected_edited:
        errors.append("edited_detection_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("edit_allowance_spent", True),
                      ("candidate_9_may_continue_as_is", False),
                      ("candidate_9_may_receive_another_edit",
                       False),
                      ("further_detections_authorized", False),
                      ("further_replays_authorized", False),
                      ("further_relabels_authorized", False),
                      ("ledger_now_contains_nine_records", True),
                      ("prior_eight_records_unchanged", True),
                      ("human_review_required", True),
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
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_edited_labels_artifacts",
                "computes_pnl_now", "applies_another_edit",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_RJ9_RECORDED and r.get("blockers"):
        errors.append("recorded_with_blockers")
    return {"valid": not errors, "errors": errors}
