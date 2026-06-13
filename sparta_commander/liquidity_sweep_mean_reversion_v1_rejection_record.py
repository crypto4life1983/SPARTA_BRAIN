"""SPARTA CANDIDATE #8 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY, REJECTED KEPT ON RECORD, ALL REPLAY VARIANTS NET-NEGATIVE
IN-SAMPLE, EDIT TOKEN NOT SPENT, NOT A PROFITABILITY CLAIM):
LIQUIDITY_SWEEP_MEAN_REVERSION_V1.

Closes out Candidate #8 on origin/master and freezes the eighth
rejected-family ledger entry. The pushed C8 evidence chain (family
proposal -> spec review -> detector spec/dry-run -> dry-run review
-> real-candle labels review -> replay review) produced:

  - 3,840 staged BTCUSD 15m bars scanned;
  - 133 sweep attempts;
  - 73 accepted setups before the proposal-level 8-bar anti-cluster
    filter; 51 accepted after; 22 anti-cluster drops; 60 rejected by
    scanner (57 on no_qualifying_reclaim_within_4_bars + 3 on
    geometry_floor);
  - sample-size adequacy SATISFIED (51 >= 20) WITHOUT consuming the
    single C8 edit token;
  - structural in-sample replay outcome under 27 bps round-trip fees
    + 81 bps floor + REDUCE-OR-KEEP-ONLY non-overlap + STOP-FIRST
    same-bar straddle + 96-bar timeout horizon:
      * 2R: 11 HIT, 38 MISS, 2 TIMEOUT; net R sum = -45.78;
        structurally_net_positive_in_sample_decisive_only = False
      * 3R:  3 HIT, 42 MISS, 6 TIMEOUT; net R sum = -58.84;
        structurally_net_positive_in_sample_decisive_only = False
      * 4R:  0 HIT, 43 MISS, 8 TIMEOUT; net R sum = -65.78;
        structurally_net_positive_in_sample_decisive_only = False

ALL THREE replay variants were structurally net-negative in-sample.
The best variant (2R) is deeply negative; this is NOT a near-miss.
On the HUMAN DECISION gate that followed the pushed replay review,
the explicit choice was REJECT WITHOUT SPENDING THE SINGLE C8 EDIT
TOKEN.

REJECTION_STATUS = REJECTED_KEPT_ON_RECORD. The single C8 edit
allowance has NOT been consumed (the rejection cleanly closes the
family without using the controlled-relaxation budget). Anti-cluster
gap (8) and sample-size adequacy threshold (20) remain proposal-
level locked and were never edit-token usage.

The C8 family `liquidity_sweep_mean_reversion` becomes the eighth
entry in the rejected-family blacklist. The next path forward is a
brand-new Candidate #9 family proposal that must clear the V4
blacklist (this module exports FUTURE_FAMILY_BLACKLIST_ADDITION as
the source of truth for the V4 update). Candidate #8 may NOT be
re-proposed as-is.

NO edge demonstrated. NO winner. NO profitability claim. NO paper
approval. NO live approval. NO trading capability authorized. The
HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY after this rejection is the
only forward path.

This module observes the pushed C8 chain (labels review + replay
review) plus the pushed staged-source SHA pins READ-ONLY and
certifies the eighth ledger entry. It runs nothing, fetches nothing,
modifies nothing, and authorizes nothing.

Chain-gated live on: the pushed seven-record rejection ledger
(C1-C7), the pushed C8 family proposal, the pushed C8 spec review,
the pushed C8 detector spec + dry-run, the pushed C8 dry-run review,
the pushed C8 real-candle labels review, the pushed C8 replay
review, the pushed V3 rejected-family blacklist, the pushed
Overnight Research Autopilot V2, the pushed Recommendation V1, and
the pushed Autopilot Loop V1.
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract import (
    VERDICT_C8R_FROZEN,
    build_candidate_8_dry_run_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract import (
    VERDICT_C8D_READY,
    build_candidate_8_detector_spec_contract,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C8P_READY,
    build_candidate_8_family_proposal,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract import (
    VERDICT_C8L_FROZEN,
    build_c8_labels_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_replay_review_contract import (
    VERDICT_C8RR_FROZEN,
    build_c8_replay_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract import (
    VERDICT_C8S_READY,
    build_candidate_8_spec_review,
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

RJ8_SCHEMA_VERSION = (
    "liquidity_sweep_mean_reversion_v1_rejection_record.v1")
RJ8_LABEL = ("SPARTA Candidate #8 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "ALL REPLAY VARIANTS NET-NEGATIVE IN-SAMPLE, EDIT "
             "TOKEN NOT SPENT, NOT A PROFITABILITY CLAIM)")
RJ8_MODE = "RESEARCH_ONLY"
VERDICT_RJ8_RECORDED = (
    "C8_REJECTED_KEPT_ON_RECORD_EDIT_TOKEN_NOT_SPENT_AND_ALL_REPLAY"
    "_VARIANTS_NET_NEGATIVE_IN_SAMPLE")
VERDICT_RJ8_REVIEW_REJECTED = (
    "C8_REJECTION_RECORD_REVIEW_REJECTED")
VERDICT_RJ8_BLOCKED = "C8_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

# Eighth ledger entry. Future Candidate #9+ contracts will gate on
# REJECTION_STATUS exactly like they gate on C1-C7.
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "ALL_REPLAY_VARIANTS_STRUCTURALLY_NET_NEGATIVE_IN_SAMPLE_AND"
    "_EDIT_TOKEN_NOT_SPENT")
EDIT_CLASSIFICATION = (
    "C8_EDIT_TOKEN_NOT_SPENT_HUMAN_CHOSE_REJECT_OVER_RELAXATION")
REPLAY_CLASSIFICATION = (
    "C8_ALL_THREE_VARIANTS_STRUCTURALLY_NET_NEGATIVE_IN_SAMPLE"
    "_DEEP_NOT_NEAR_MISS")

HEAD_AT_LABELS_REVIEW = "fb208252a5551937cb431eb25706b96ca92d43b7"
HEAD_AT_REPLAY_REVIEW = "146dce2976f1bece54122ec1f7652df58324655f"

# --- Frozen detection evidence (carried forward from labels review)-----

EXPECTED_DETECTOR_LABELS_PATH = (
    "data/liquidity_sweep_c8/detector_labels/"
    "c8_detector_labels_2026-05-02_2026-06-10.json")
EXPECTED_DETECTOR_SUMMARY_PATH = (
    "data/liquidity_sweep_c8/detector_labels/"
    "c8_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_DETECTOR_LABELS_SHA256 = (
    "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e86405cb81fee3")
EXPECTED_DETECTOR_SUMMARY_SHA256 = (
    "d1655123990b0080ef741bda49ea5baa20d6640c4b2d4476986f29deb2e4ae90")

EXPECTED_DETECTION_EVIDENCE = {
    "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
    "labels_sha256": EXPECTED_DETECTOR_LABELS_SHA256,
    "summary_sha256": EXPECTED_DETECTOR_SUMMARY_SHA256,
    "sample_tag": "2026-05-02_2026-06-10",
    "start_inclusive_utc": "2026-05-02T00:00:00Z",
    "end_inclusive_utc": "2026-06-10T23:45:00Z",
    "bars_scanned": 3840,
    "total_attempts": 133,
    "accepted_pre_anti_cluster": 73,
    "accepted_post_anti_cluster": 51,
    "rejected_by_scanner": 60,
    "dropped_by_anti_cluster": 22,
    "status_breakdown": {
        "accepted_for_replay_review": 73,
        "rejected_no_qualifying_reclaim_within_4_bars": 57,
        "rejected_geometry_floor": 3,
        "rejected_clustered_within_8_bars_of_prior_accepted": 22,
    },
    "sample_size_adequacy_satisfied": True,
    "sample_size_adequacy_threshold_min_accepted": 20,
    "sample_size_adequacy_did_not_consume_edit_token": True,
    "anti_cluster_min_bar_gap": 8,
    "anti_cluster_did_not_consume_edit_token": True,
    "no_replay_run_at_this_gate": True,
    "no_pnl_computed_at_this_gate": True,
    "no_trading_authorized": True,
}

# --- Frozen replay evidence (carried forward from replay review) -------

EXPECTED_REPLAY_LEDGER_PATH = (
    "data/liquidity_sweep_c8/replay_results/"
    "c8_replay_ledger_2026-05-02_2026-06-10.json")
EXPECTED_REPLAY_SUMMARY_PATH = (
    "data/liquidity_sweep_c8/replay_results/"
    "c8_replay_summary_2026-05-02_2026-06-10.json")
EXPECTED_REPLAY_LEDGER_SHA256 = (
    "b7b12b8ef9ffe9bf3ab587ba4bd2b097d391a78f6761e52c7103146de58dfb92")
EXPECTED_REPLAY_SUMMARY_SHA256 = (
    "2be19e38195a7a2414c661b6d3ec84a5fdc371c05e6cc7d461199683944454db")

EXPECTED_REPLAY_POLICY = {
    "timeout_bars": 96,
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "variants": ("2r", "3r", "4r"),
    "same_bar_straddle_policy": "stop_first_conservative_miss",
    "non_overlap_policy": "reduce_or_keep_only_never_add",
}

EXPECTED_REPLAY_VARIANT_2R = {
    "variant_r_multiple": 2.0,
    "kept_count": 51, "dropped_overlap_count": 0,
    "decisive_count": 51, "open_or_truncated_count": 0,
    "counts": {
        "hit": 11, "miss": 38, "miss_same_bar_straddle": 0,
        "timeout": 2, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0},
    "gross_r_sum_decisive": -15.814923512147077,
    "net_r_sum_decisive": -45.77781173130582,
    "structurally_net_positive_in_sample_decisive_only": False,
}
EXPECTED_REPLAY_VARIANT_3R = {
    "variant_r_multiple": 3.0,
    "kept_count": 51, "dropped_overlap_count": 0,
    "decisive_count": 51, "open_or_truncated_count": 0,
    "counts": {
        "hit": 3, "miss": 42, "miss_same_bar_straddle": 0,
        "timeout": 6, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0},
    "gross_r_sum_decisive": -28.876621100398147,
    "net_r_sum_decisive": -58.83950931955688,
    "structurally_net_positive_in_sample_decisive_only": False,
}
EXPECTED_REPLAY_VARIANT_4R = {
    "variant_r_multiple": 4.0,
    "kept_count": 51, "dropped_overlap_count": 0,
    "decisive_count": 51, "open_or_truncated_count": 0,
    "counts": {
        "hit": 0, "miss": 43, "miss_same_bar_straddle": 0,
        "timeout": 8, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0},
    "gross_r_sum_decisive": -35.82079188422728,
    "net_r_sum_decisive": -65.78368010338602,
    "structurally_net_positive_in_sample_decisive_only": False,
}

EXPECTED_REPLAY_EVIDENCE = {
    "head_at_replay_review": HEAD_AT_REPLAY_REVIEW,
    "ledger_sha256": EXPECTED_REPLAY_LEDGER_SHA256,
    "summary_sha256": EXPECTED_REPLAY_SUMMARY_SHA256,
    "accepted_input_count": 51,
    "policy": EXPECTED_REPLAY_POLICY,
    "variant_2r": EXPECTED_REPLAY_VARIANT_2R,
    "variant_3r": EXPECTED_REPLAY_VARIANT_3R,
    "variant_4r": EXPECTED_REPLAY_VARIANT_4R,
    "all_three_variants_structurally_net_negative_in_sample": True,
    "any_variant_structurally_net_positive_in_sample_decisive_only":
        False,
    "best_variant_label": "2r",
    "best_variant_net_r_sum": -45.77781173130582,
    "best_variant_is_a_near_miss": False,
    "no_relabel_authorized_by_this_gate": True,
    "no_replay_re_run_authorized_by_this_gate": True,
    "no_pnl_claim": True,
    "no_winner_designation": True,
}

# --- Frozen edit-token state (NOT SPENT) ------------------------------

EXPECTED_EDIT_TOKEN_STATE = {
    "single_pre_committed_edit_originally_allowed": 1,
    "edit_token_consumed_by_anti_cluster": False,
    "edit_token_consumed_by_sample_size_threshold": False,
    "edit_token_consumed_by_rejection": False,
    "edit_token_spent_at_any_gate": False,
    "edits_remaining_at_rejection_time": 1,
    "rejection_chose_close_over_relaxation": True,
    "no_further_c8_edit_allowed_after_rejection": True,
    "anti_cluster_gap_remained_proposal_level_locked": True,
    "sample_size_threshold_remained_proposal_level_locked": True,
}

# --- Frozen staged-source pins ----------------------------------------
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
    "all_replay_variants_structurally_net_negative_in_sample": True,
    "best_variant_is_not_a_near_miss": True,
    "human_chose_reject_over_spending_edit_token": True,
    "any_attempt_to_change_an_inviolable_upstream_rule": False,
    "any_attempt_to_spend_a_second_edit_on_this_family": False,
    "any_artifact_hash_or_gate_mismatch_in_pushed_chain": False,
}

# --- Rejection facts ---------------------------------------------------
REJECTION_FACTS = (
    "candidate #8 is rejected",
    "rejection is kept on record as the eighth ledger entry",
    "reason: the pushed real-candle detection produced 73 accepted-"
    "pre-anti-cluster and 51 accepted-post-anti-cluster setups out "
    "of 133 attempts on 3840 btcusd 15m bars; the pushed replay "
    "evaluation under 27 bps round-trip fees and the 81 bps gross-"
    "target-distance floor produced ALL THREE variants structurally "
    "net-negative in-sample (2R: -45.78, 3R: -58.84, 4R: -65.78); "
    "the best variant is deeply negative and is NOT a near-miss",
    "the human decision after the pushed replay review was to "
    "REJECT WITHOUT SPENDING THE SINGLE C8 EDIT TOKEN; the single "
    "pre-committed edit allowance was preserved unconsumed",
    "anti-cluster gap remained proposal-level locked at 8 bars and "
    "did not consume the edit token throughout the entire C8 chain",
    "sample-size adequacy threshold remained proposal-level locked "
    "at 20 accepted setups and did not consume the edit token; the "
    "threshold was SATISFIED (51 >= 20)",
    "candidate #8 may not continue as-is",
    "candidate #8 may not be re-proposed as-is",
    "further detections, replays, and relabels are not authorized "
    "on the c8 lane",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
    "no winner wording permitted",
    "candidate #8 has 51 accepted-post-anti-cluster real-candle "
    "setups, a pushed replay evaluation, and an all-three-variants-"
    "net-negative in-sample finding; no live trading is authorized; "
    "no edge has been demonstrated",
)

EVIDENCE_NOTES = (
    "the liquidity-sweep-mean-reversion hypothesis is unsupported "
    "on the btcusd 15m 2026-05-02_2026-06-10 window under the "
    "pushed spec (0.25 x ATR(14) sweep penetration, 4-bar reclaim "
    "window, upper-third 2/3 confirmation, 0.20 x ATR structure-"
    "stop buffer, 27/81 bps fees + floor)",
    "structural cleanliness did not produce edge: per-variant "
    "win-rates were 11/51, 3/51, 0/51 for 2R/3R/4R respectively; "
    "deep stops were hit more often than tight targets; the 24h "
    "evaluation horizon did not rescue the timeouts",
    "the headline-variant 2R win-rate of ~22% combined with the "
    "27 bps round-trip fee meant that the gross negative -15.82 "
    "R became a net negative -45.78 R after fees; this is fee-"
    "sensitivity at the per-setup level",
    "no replay re-run was attempted; no relabel; no detector change; "
    "no edit-token use; no fetch; no api; no network; no scheduler; "
    "no notification; no broker; no exchange; no wallet; no order; "
    "no portfolio touch at any stage",
    "anti-cluster gap stayed proposal-level locked at 8 bars and did "
    "not consume the edit token; this protection held",
    "sample-size adequacy threshold stayed proposal-level locked at "
    "20 accepted setups and did not consume the edit token; the "
    "threshold was satisfied (51 >= 20); this protection held",
    "every staged-data sha and every artifact sha was sha-pinned and "
    "re-verified at every gate (labels, summary, replay ledger, "
    "replay summary)",
    "the single c8 edit token was never spent; the family is closed "
    "out cleanly; the edit-token budget is not carried over to any "
    "future candidate (each family gets its own one-allowed edit)",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "liquidity_sweep_plus_reclaim_structure_alone_is_not_an_edge"
    "_source_after_27_bps_fees_on_15m_btcusd_in_a_40_day_window",
    "single_session_horizon_evaluation_windows_may_under_count_the"
    "_winners_for_long_holding_period_strategies_but_were_balanced"
    "_here_by_the_anti_cluster_gap",
    "structural_cleanliness_alone_does_not_produce_edge_the_entry"
    "_must_have_an_explicit_edge_argument_that_survives_fees_plus"
    "_the_81_bps_floor",
    "label_time_anti_cluster_filters_remain_a_real_structural_tool"
    "_inherited_from_c6_lesson",
    "proposal_level_sample_size_adequacy_thresholds_remain_a_real"
    "_structural_tool_inherited_from_c7_lesson",
    "fee_aware_geometry_with_an_81_bps_floor_remains_inviolable",
    "any_future_mean_reversion_or_reversal_family_must_provide_an"
    "_explicit_edge_argument_beyond_pattern_geometry",
    "do_not_reuse_c8_as_is",
    "any_future_candidate_must_be_a_new_clean_hypothesis_through"
    "_the_autopilot_loop",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

# Future candidate-recommendation logic must blacklist the C8 family.
FUTURE_FAMILY_BLACKLIST_ADDITION = "liquidity_sweep_mean_reversion"
FUTURE_FAMILY_BLACKLIST_REASON = (
    "candidate_8_rejected_kept_on_record_all_replay_variants_net"
    "_negative_in_sample_and_edit_token_not_spent_must_not_be_re"
    "_proposed_as_is")

# --- The full pushed C8 evidence chain (for permanence) ----------------
PUSHED_EVIDENCE_CHAIN = (
    "liquidity_sweep_mean_reversion_v1_family_proposal_contract",
    "liquidity_sweep_mean_reversion_v1_spec_review_contract",
    "liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract",
    "liquidity_sweep_mean_reversion_v1_detector_dry_run_review"
    "_contract",
    "liquidity_sweep_mean_reversion_v1_real_candle_labels_review"
    "_contract",
    "liquidity_sweep_mean_reversion_v1_replay_review_contract",
    "strategy_factory_rejected_family_blacklist_v3_contract",
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
)


def get_c8_rejection_record_label() -> str:
    return RJ8_LABEL


def build_c8_rejection_record(repo_root: Any = ".",
                              tracked_paths: Any = ()
                              ) -> dict[str, Any]:
    """Assemble the C8 eighth-ledger rejection record. Chain-gated on
    the full pushed C8 evidence chain plus the seven-record rejection
    ledger, V3 blacklist, V2, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": RJ8_SCHEMA_VERSION, "label": RJ8_LABEL,
        "mode": RJ8_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "edit_classification": EDIT_CLASSIFICATION,
        "replay_classification": REPLAY_CLASSIFICATION,
        "ledger_position": 8,
        "prior_ledger_families": list(PRIOR_LEDGER_FAMILIES),
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "head_at_replay_review": HEAD_AT_REPLAY_REVIEW,
        "expected_detector_labels_path":
            EXPECTED_DETECTOR_LABELS_PATH,
        "expected_detector_summary_path":
            EXPECTED_DETECTOR_SUMMARY_PATH,
        "expected_replay_ledger_path": EXPECTED_REPLAY_LEDGER_PATH,
        "expected_replay_summary_path": EXPECTED_REPLAY_SUMMARY_PATH,
        "expected_detection_evidence":
            {key: (dict(value) if isinstance(value, dict) else value)
             for key, value in EXPECTED_DETECTION_EVIDENCE.items()},
        "expected_replay_evidence": {
            key: (
                ({k: (dict(v) if isinstance(v, dict)
                      else list(v) if isinstance(v, tuple) else v)
                  for k, v in value.items()})
                if isinstance(value, dict)
                else list(value) if isinstance(value, tuple)
                else value)
            for key, value in EXPECTED_REPLAY_EVIDENCE.items()},
        "expected_edit_token_state":
            dict(EXPECTED_EDIT_TOKEN_STATE),
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
        "edit_allowance_spent": False,
        "edit_allowance_preserved_unconsumed_but_family_closed": True,
        "candidate_8_may_continue_as_is": False,
        "candidate_8_may_be_re_proposed_as_is": False,
        "candidate_8_may_receive_an_edit_after_rejection": False,
        "further_detections_authorized": False,
        "further_replays_authorized": False,
        "further_relabels_authorized": False,
        "ledger_now_contains_eight_records": True,
        "prior_seven_records_unchanged": True,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
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
        "modifies_staged_market_data": False,
        "modifies_detector_artifacts": False,
        "modifies_labels_artifacts": False,
        "modifies_replay_artifacts": False,
        "computes_pnl_now": False,
        "applies_an_edit": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    # seven-record ledger (C1-C7)
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS)
    if not all(s == "REJECTED_KEPT_ON_RECORD" for s in statuses):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append("seven_record_ledger_broken")
        return record
    # full C8 evidence chain
    if build_candidate_8_family_proposal()["verdict"] != (
            VERDICT_C8P_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_proposal_not_certifying")
        return record
    if build_candidate_8_spec_review()["verdict"] != VERDICT_C8S_READY:
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_spec_review_not_certifying")
        return record
    if build_candidate_8_detector_spec_contract()["verdict"] != (
            VERDICT_C8D_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_detector_spec_not_certifying")
        return record
    if build_candidate_8_dry_run_review()["verdict"] != (
            VERDICT_C8R_FROZEN):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_dry_run_review_not_certifying")
        return record
    if build_c8_labels_review(repo_root, tracked_paths)[
            "verdict"] != VERDICT_C8L_FROZEN:
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_labels_review_not_certifying")
        return record
    if build_c8_replay_review(repo_root, tracked_paths)[
            "verdict"] != VERDICT_C8RR_FROZEN:
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "candidate_8_replay_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_RJ8_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_RJ8_RECORDED
    return record


def validate_c8_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ8_RECORDED,
                                VERDICT_RJ8_REVIEW_REJECTED,
                                VERDICT_RJ8_BLOCKED):
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
    if r.get("replay_classification") != REPLAY_CLASSIFICATION:
        errors.append("replay_classification_tampered")
    if r.get("ledger_position") != 8:
        errors.append("ledger_position_must_be_8")
    if tuple(r.get("prior_ledger_families") or ()) != (
            PRIOR_LEDGER_FAMILIES):
        errors.append("prior_ledger_families_tampered")
    if r.get("head_at_labels_review") != HEAD_AT_LABELS_REVIEW:
        errors.append("head_at_labels_review_tampered")
    if r.get("head_at_replay_review") != HEAD_AT_REPLAY_REVIEW:
        errors.append("head_at_replay_review_tampered")
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
    if r.get("expected_edit_token_state") != (
            EXPECTED_EDIT_TOKEN_STATE):
        errors.append("edit_token_state_tampered")
    if r.get("expected_detection_evidence") != {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in EXPECTED_DETECTION_EVIDENCE.items()}:
        errors.append("detection_evidence_tampered")
    expected_replay = {
        key: (
            ({k: (dict(v) if isinstance(v, dict)
                  else list(v) if isinstance(v, tuple) else v)
              for k, v in value.items()})
            if isinstance(value, dict)
            else list(value) if isinstance(value, tuple)
            else value)
        for key, value in EXPECTED_REPLAY_EVIDENCE.items()}
    if r.get("expected_replay_evidence") != expected_replay:
        errors.append("replay_evidence_tampered")
    if r.get("expected_detector_labels_path") != (
            EXPECTED_DETECTOR_LABELS_PATH):
        errors.append("detector_labels_path_tampered")
    if r.get("expected_detector_summary_path") != (
            EXPECTED_DETECTOR_SUMMARY_PATH):
        errors.append("detector_summary_path_tampered")
    if r.get("expected_replay_ledger_path") != (
            EXPECTED_REPLAY_LEDGER_PATH):
        errors.append("replay_ledger_path_tampered")
    if r.get("expected_replay_summary_path") != (
            EXPECTED_REPLAY_SUMMARY_PATH):
        errors.append("replay_summary_path_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("edit_allowance_spent", False),
                      ("edit_allowance_preserved_unconsumed_but"
                       "_family_closed", True),
                      ("candidate_8_may_continue_as_is", False),
                      ("candidate_8_may_be_re_proposed_as_is", False),
                      ("candidate_8_may_receive_an_edit_after"
                       "_rejection", False),
                      ("further_detections_authorized", False),
                      ("further_replays_authorized", False),
                      ("further_relabels_authorized", False),
                      ("ledger_now_contains_eight_records", True),
                      ("prior_seven_records_unchanged", True),
                      ("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
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
                "modifies_staged_market_data",
                "modifies_detector_artifacts",
                "modifies_labels_artifacts",
                "modifies_replay_artifacts",
                "computes_pnl_now", "applies_an_edit",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_RJ8_RECORDED and r.get("blockers"):
        errors.append("recorded_with_blockers")
    return {"valid": not errors, "errors": errors}
