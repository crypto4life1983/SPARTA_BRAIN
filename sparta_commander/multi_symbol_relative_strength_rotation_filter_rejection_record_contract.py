"""SPARTA CANDIDATE #6 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY): MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

THE LEDGER ENTRY: Candidate #6 is REJECTED_KEPT_ON_RECORD, reason
EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE.

The original fee-honest replay of the 135 frozen accepted labels was
NET-negative and GROSS-negative in every variant (2R -11.085290, 3R
-10.846129, 4R -8.340989), with all hit rates below the gross
breakeven rate (23.1% < 33.3%, 16.7% < 25.0%, 14.3% < 20.0%). The
single allowed structure-only edit -- label-time same-symbol
minimum bar-gap clustering filter at 24 completed 1h bars -- was
authorised, applied at label-emission time, and reduced the accepted
label set from 135 to 36 (per-symbol BTCUSD 32->9, ETHUSD 32->11,
SOLUSD 71->16, total removed 99). The post-edit fee-honest replay of
the 36 surviving accepted labels was net-negative AND gross-negative
at every variant (2R -12.897835, 3R -14.793291, 4R -14.464742) with
hit rates also below the gross breakeven rate (20.0% / 12.5% / 9.1%).
Both hit rates AND net R worsened versus the original replay: the
edit reduced clustering as designed but did NOT rescue per-trade
edge.

The single edit allowance is SPENT, permanently, on origin/master.
The pre-committed auto-rejection triggers fired: any_variant_net_
negative=True, any_variant_gross_negative=True, any_variant_hit_rate_
below_gross_breakeven=True, filter_or_edit_spent_and_still_negative=
True, gross_negative_and_net_negative_after_replay=True, below_break
even_hit_rate=True.

Frozen consequences (validator-permanent): candidate #6 may not
continue as-is; may not receive another edit; further replays are not
authorized; no paper, no live, no profitability claim, no winner
wording. Seeds are preserved STRICTLY for future families and are
never rescue paths.

This module is declarative -- it freezes the rejection facts and the
chain of pushed contracts that prove them. All artifact shas (six
staged 15m files, original detector labels, original replay, edited
labels, edited replay) are already verified live by the pushed
edited-replay-results-review contract which this record chain-gates
on. It runs nothing, fetches nothing, modifies nothing, and authorizes
nothing.

Chain-gated on: the pushed five-record rejection ledger (C1-C5), the
pushed C6 family proposal, the pushed C6 spec review, the pushed C6
dry-run review, the pushed C6 real-candle labels review, the pushed
C6 informational replay results review, the pushed C6 single-edit
clustering-filter contract, the pushed C6 edited real-candle labels
review, the pushed C6 edited informational replay results review, the
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
from sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract import (
    VERDICT_C6R_FROZEN,
    build_c6_dry_run_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_real_candle_labels_review_contract import (
    EXPECTED_ACCEPTED_AFTER_EDIT,
    EXPECTED_ACCEPTED_BEFORE_EDIT,
    EXPECTED_LABELS_SHA256 as EDITED_LABELS_SHA256,
    EXPECTED_PER_SYMBOL_EDITED,
    EXPECTED_REMOVED_BY_CLUSTERING_TOTAL,
    EXPECTED_SUMMARY_SHA256 as EDITED_LABELS_SUMMARY_SHA256,
    VERDICT_C6EL_FROZEN,
    build_c6_edited_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_replay_results_review_contract import (
    EXPECTED_AUTO_REJECTION_TRIGGERS as EDITED_AUTO_REJECTION_TRIGGERS,
    EXPECTED_OVERLAP_SKIPPED_TOTAL as EDITED_OVERLAP_SKIPPED_TOTAL,
    EXPECTED_RESULTS_SHA256 as EDITED_REPLAY_RESULTS_SHA256,
    EXPECTED_SUMMARY_SHA256 as EDITED_REPLAY_SUMMARY_SHA256,
    EXPECTED_VARIANTS as EDITED_REPLAY_VARIANTS,
    HONEST_VERDICT as EDITED_REPLAY_VERDICT,
    VERDICT_C6EER_FROZEN,
    build_c6_edited_replay_results_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as ORIGINAL_LABELS_SHA256,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_LABELS_SUMMARY_SHA256,
    VERDICT_C6L_FROZEN,
    build_c6_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract import (
    EXPECTED_OVERLAP_SKIPPED_TOTAL as ORIGINAL_OVERLAP_SKIPPED_TOTAL,
    EXPECTED_RESULTS_SHA256 as ORIGINAL_REPLAY_RESULTS_SHA256,
    EXPECTED_SUMMARY_SHA256 as ORIGINAL_REPLAY_SUMMARY_SHA256,
    EXPECTED_VARIANTS as ORIGINAL_REPLAY_VARIANTS,
    HONEST_VERDICT as ORIGINAL_REPLAY_VERDICT,
    VERDICT_C6RR_FROZEN,
    build_c6_replay_results_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract import (
    EDITS_REMAINING_AFTER_THIS,
    EDIT_KIND,
    EDIT_TOKEN_USED,
    MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
    VERDICT_C6E_READY,
    build_c6_single_edit_clustering_filter,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

RJ6_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_rejection_record.v1")
RJ6_LABEL = ("SPARTA Candidate #6 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "NOT A PROFITABILITY CLAIM)")
RJ6_MODE = "RESEARCH_ONLY"
VERDICT_RJ6_RECORDED = (
    "C6_REJECTED_KEPT_ON_RECORD_EDIT_SPENT_AND_STILL_NEGATIVE"
    "_EDGE_FAILURE")
VERDICT_RJ6_REVIEW_REJECTED = "C6_REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ6_BLOCKED = "C6_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

# This module is the SIXTH ledger entry. Future Candidate #7+ contracts
# will gate on REJECTION_STATUS exactly like they gate on C1-C5.
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE"
EDIT_CLASSIFICATION = (
    "C6_EDIT_V1_LABEL_TIME_24BAR_CLUSTERING_FILTER_FAILED_REJECT_NEXT")
REPLAY_REVIEW_CLASSIFICATION = (
    "C6_ORIGINAL_AND_EDITED_REPLAY_BOTH_NEGATIVE_EDIT_SPENT")

HEAD_AT_EDITED_REPLAY_REVIEW = (
    "1dee6af606f52934fc183d3fa6446eb17c9b31bc")

# --- Frozen original replay evidence (from pushed C6 replay review) -------
EXPECTED_ORIGINAL_REPLAY = {
    "verdict": ORIGINAL_REPLAY_VERDICT,
    "results_sha256": ORIGINAL_REPLAY_RESULTS_SHA256,
    "summary_sha256": ORIGINAL_REPLAY_SUMMARY_SHA256,
    "labels_sha256": ORIGINAL_LABELS_SHA256,
    "labels_summary_sha256": ORIGINAL_LABELS_SUMMARY_SHA256,
    "overlap_skipped_total": ORIGINAL_OVERLAP_SKIPPED_TOTAL,
    "variants": {
        "2r": {
            "net_r": ORIGINAL_REPLAY_VARIANTS["2r"]["net_r_total"],
            "gross_r": ORIGINAL_REPLAY_VARIANTS["2r"]["gross_r_total"],
            "hit_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["2r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["2r"][
                    "gross_breakeven_rate_pct"],
            "max_drawdown_r":
                ORIGINAL_REPLAY_VARIANTS["2r"]["max_drawdown_r"]},
        "3r": {
            "net_r": ORIGINAL_REPLAY_VARIANTS["3r"]["net_r_total"],
            "gross_r": ORIGINAL_REPLAY_VARIANTS["3r"]["gross_r_total"],
            "hit_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["3r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["3r"][
                    "gross_breakeven_rate_pct"],
            "max_drawdown_r":
                ORIGINAL_REPLAY_VARIANTS["3r"]["max_drawdown_r"]},
        "4r": {
            "net_r": ORIGINAL_REPLAY_VARIANTS["4r"]["net_r_total"],
            "gross_r": ORIGINAL_REPLAY_VARIANTS["4r"]["gross_r_total"],
            "hit_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["4r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                ORIGINAL_REPLAY_VARIANTS["4r"][
                    "gross_breakeven_rate_pct"],
            "max_drawdown_r":
                ORIGINAL_REPLAY_VARIANTS["4r"]["max_drawdown_r"]},
    },
    "all_variants_net_negative": True,
    "all_variants_gross_negative": True,
    "all_hit_rates_below_gross_breakeven": True,
}

# --- Frozen edit evidence (from pushed C6 single-edit contract) -----------
EXPECTED_EDIT = {
    "edit_kind": EDIT_KIND,
    "min_bars_between_same_symbol_accepted_events_1h":
        MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
    "edit_token_used": EDIT_TOKEN_USED,
    "edits_remaining_after_this": EDITS_REMAINING_AFTER_THIS,
    "original_accepted_labels": EXPECTED_ACCEPTED_BEFORE_EDIT,
    "edited_accepted_labels": EXPECTED_ACCEPTED_AFTER_EDIT,
    "removed_by_clustering": EXPECTED_REMOVED_BY_CLUSTERING_TOTAL,
    "per_symbol_edited": {sym: dict(v) for sym, v
                          in EXPECTED_PER_SYMBOL_EDITED.items()},
    "edit_labels_sha256": EDITED_LABELS_SHA256,
    "edit_labels_summary_sha256": EDITED_LABELS_SUMMARY_SHA256,
    "original_overlap_skipped_total": ORIGINAL_OVERLAP_SKIPPED_TOTAL,
    "edited_overlap_skipped_total": EDITED_OVERLAP_SKIPPED_TOTAL,
    "edit_worked_structurally_but_did_not_rescue_edge": True,
}

# --- Frozen edited replay evidence (from pushed edited-replay review) -----
EXPECTED_EDITED_REPLAY = {
    "verdict": EDITED_REPLAY_VERDICT,
    "results_sha256": EDITED_REPLAY_RESULTS_SHA256,
    "summary_sha256": EDITED_REPLAY_SUMMARY_SHA256,
    "overlap_skipped_total": EDITED_OVERLAP_SKIPPED_TOTAL,
    "variants": {
        "2r": {
            "net_r": EDITED_REPLAY_VARIANTS["2r"]["net_r_total"],
            "gross_r": EDITED_REPLAY_VARIANTS["2r"]["gross_r_total"],
            "hit_rate_pct":
                EDITED_REPLAY_VARIANTS["2r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                EDITED_REPLAY_VARIANTS["2r"]["gross_breakeven_rate_pct"],
            "kept_trades": EDITED_REPLAY_VARIANTS["2r"]["kept"],
            "max_drawdown_r":
                EDITED_REPLAY_VARIANTS["2r"]["max_drawdown_r"]},
        "3r": {
            "net_r": EDITED_REPLAY_VARIANTS["3r"]["net_r_total"],
            "gross_r": EDITED_REPLAY_VARIANTS["3r"]["gross_r_total"],
            "hit_rate_pct":
                EDITED_REPLAY_VARIANTS["3r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                EDITED_REPLAY_VARIANTS["3r"]["gross_breakeven_rate_pct"],
            "kept_trades": EDITED_REPLAY_VARIANTS["3r"]["kept"],
            "max_drawdown_r":
                EDITED_REPLAY_VARIANTS["3r"]["max_drawdown_r"]},
        "4r": {
            "net_r": EDITED_REPLAY_VARIANTS["4r"]["net_r_total"],
            "gross_r": EDITED_REPLAY_VARIANTS["4r"]["gross_r_total"],
            "hit_rate_pct":
                EDITED_REPLAY_VARIANTS["4r"]["hit_rate_pct"],
            "gross_breakeven_rate_pct":
                EDITED_REPLAY_VARIANTS["4r"]["gross_breakeven_rate_pct"],
            "kept_trades": EDITED_REPLAY_VARIANTS["4r"]["kept"],
            "max_drawdown_r":
                EDITED_REPLAY_VARIANTS["4r"]["max_drawdown_r"]},
    },
    "all_variants_net_negative": True,
    "all_variants_gross_negative": True,
    "all_hit_rates_below_gross_breakeven": True,
    "edited_results_worsened_versus_original": True,
}

# --- Auto-rejection triggers satisfied -----------------------------------
EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED = {
    "any_variant_net_negative": True,
    "any_variant_gross_negative": True,
    "any_variant_hit_rate_below_gross_breakeven": True,
    "filter_or_edit_spent_and_still_negative": True,
    "gross_negative_and_net_negative_after_replay": True,
    "below_breakeven_hit_rate": True,
}

# --- Rejection facts -----------------------------------------------------
REJECTION_FACTS = (
    "candidate #6 is rejected",
    "rejection is kept on record as the sixth ledger entry",
    "reason: original replay net-negative and gross-negative at every "
    "variant, the single authorized structure-only edit was spent, "
    "and the post-edit replay was also net-negative and gross-negative "
    "at every variant",
    "both original and edited hit rates were below the gross "
    "breakeven rate at every variant",
    "edited results worsened versus original at every variant; the "
    "edit reduced clustering as designed but did not rescue edge",
    "the single edit allowance is now spent permanently on "
    "origin/master",
    "candidate #6 may not continue as-is",
    "candidate #6 may not receive another edit",
    "further replays are not authorized",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
    "no winner wording permitted",
)

EVIDENCE_NOTES = (
    "the family hypothesis (cross-sectional rank-#1 as edge on "
    "btcusd/ethusd/solusd over the 2026-05-02_2026-06-10 window) is "
    "twice unsupported: once on the original 135-label sample and "
    "once on the post-edit 36-label sample",
    "the 24-bar same-symbol minimum bar-gap clustering filter reduced "
    "replay-time overlap from 334 to 37 total skips as designed",
    "the post-edit kept-trade sample of 22-25 per variant remained "
    "above the minimum_evaluable_kept_per_variant threshold",
    "max drawdown exceeded total net loss in every variant in both "
    "the original and the edited replays",
    "solusd was the dominant clustered symbol; the edit removed 55 of "
    "71 solusd accepted events (77%)",
    "btcusd contributed zero target hits in any kept variant of the "
    "edited replay",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "cross_sectional_ranking_alone_is_not_edge_on_this_universe_and"
    "_timeframe_in_this_sample_window",
    "label_time_clustering_filters_are_a_real_structural_tool_but"
    "_do_not_substitute_for_a_per_trade_edge_hypothesis",
    "btcusd_ethusd_solusd_1h_continuation_setups_in_this_window_did"
    "_not_resolve_with_meaningful_target_to_stop_geometry",
    "any_future_family_hypothesizing_relative_strength_must_pair_it"
    "_with_an_independent_trigger_quality_filter",
    "do_not_reuse_c6_as_is",
    "any_future_candidate_must_be_a_new_clean_hypothesis_through_the"
    "_autopilot_loop",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

# --- The full pushed C6 evidence chain (for permanence) ------------------
PUSHED_EVIDENCE_CHAIN = (
    "multi_symbol_relative_strength_rotation_filter_family_proposal",
    "multi_symbol_relative_strength_rotation_filter_spec_review",
    "multi_symbol_relative_strength_rotation_filter_detector_spec",
    "multi_symbol_relative_strength_rotation_filter_dry_run_review",
    "multi_symbol_relative_strength_rotation_filter_real_candle_labels"
    "_review",
    "multi_symbol_relative_strength_rotation_filter_replay_results"
    "_review",
    "multi_symbol_relative_strength_rotation_filter_single_edit"
    "_clustering_filter",
    "multi_symbol_relative_strength_rotation_filter_edited_real"
    "_candle_labels_review",
    "multi_symbol_relative_strength_rotation_filter_edited_replay"
    "_results_review",
    "strategy_factory_candidate_recommendation_v1",
    "strategy_factory_autopilot_research_loop_v1",
)


def get_c6_rejection_record_label() -> str:
    return RJ6_LABEL


def build_c6_rejection_record(repo_root: Any = ".",
                              tracked_paths: Any = ()
                              ) -> dict[str, Any]:
    """Assemble the C6 sixth-ledger rejection record. Chain-gated on the
    full pushed C6 evidence chain plus Recommendation V1, Autopilot V1,
    and the five-record rejection ledger (C1-C5). Declarative -- the
    pushed edited-replay-results review and the pushed edited-labels
    review already certified all artifact shas and arithmetic, so this
    record just freezes the rejection narrative and the chain."""
    record: dict[str, Any] = {
        "schema_version": RJ6_SCHEMA_VERSION, "label": RJ6_LABEL,
        "mode": RJ6_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "edit_classification": EDIT_CLASSIFICATION,
        "replay_review_classification": REPLAY_REVIEW_CLASSIFICATION,
        "head_at_edited_replay_review": HEAD_AT_EDITED_REPLAY_REVIEW,
        "ledger_position": 6,
        "expected_original_replay": {
            "verdict": EXPECTED_ORIGINAL_REPLAY["verdict"],
            "results_sha256":
                EXPECTED_ORIGINAL_REPLAY["results_sha256"],
            "summary_sha256":
                EXPECTED_ORIGINAL_REPLAY["summary_sha256"],
            "labels_sha256":
                EXPECTED_ORIGINAL_REPLAY["labels_sha256"],
            "labels_summary_sha256":
                EXPECTED_ORIGINAL_REPLAY["labels_summary_sha256"],
            "overlap_skipped_total":
                EXPECTED_ORIGINAL_REPLAY["overlap_skipped_total"],
            "variants": {name: dict(value) for name, value
                         in EXPECTED_ORIGINAL_REPLAY["variants"].items()},
            "all_variants_net_negative": True,
            "all_variants_gross_negative": True,
            "all_hit_rates_below_gross_breakeven": True},
        "expected_edit": {
            "edit_kind": EXPECTED_EDIT["edit_kind"],
            "min_bars_between_same_symbol_accepted_events_1h":
                EXPECTED_EDIT[
                    "min_bars_between_same_symbol_accepted_events_1h"],
            "edit_token_used": EXPECTED_EDIT["edit_token_used"],
            "edits_remaining_after_this":
                EXPECTED_EDIT["edits_remaining_after_this"],
            "original_accepted_labels":
                EXPECTED_EDIT["original_accepted_labels"],
            "edited_accepted_labels":
                EXPECTED_EDIT["edited_accepted_labels"],
            "removed_by_clustering":
                EXPECTED_EDIT["removed_by_clustering"],
            "per_symbol_edited":
                {sym: dict(v) for sym, v
                 in EXPECTED_EDIT["per_symbol_edited"].items()},
            "edit_labels_sha256":
                EXPECTED_EDIT["edit_labels_sha256"],
            "edit_labels_summary_sha256":
                EXPECTED_EDIT["edit_labels_summary_sha256"],
            "original_overlap_skipped_total":
                EXPECTED_EDIT["original_overlap_skipped_total"],
            "edited_overlap_skipped_total":
                EXPECTED_EDIT["edited_overlap_skipped_total"],
            "edit_worked_structurally_but_did_not_rescue_edge": True},
        "expected_edited_replay": {
            "verdict": EXPECTED_EDITED_REPLAY["verdict"],
            "results_sha256":
                EXPECTED_EDITED_REPLAY["results_sha256"],
            "summary_sha256":
                EXPECTED_EDITED_REPLAY["summary_sha256"],
            "overlap_skipped_total":
                EXPECTED_EDITED_REPLAY["overlap_skipped_total"],
            "variants": {name: dict(value) for name, value
                         in EXPECTED_EDITED_REPLAY["variants"].items()},
            "all_variants_net_negative": True,
            "all_variants_gross_negative": True,
            "all_hit_rates_below_gross_breakeven": True,
            "edited_results_worsened_versus_original": True},
        "auto_rejection_triggers_satisfied":
            dict(EXPECTED_AUTO_REJECTION_TRIGGERS_SATISFIED),
        "rejection_facts": list(REJECTION_FACTS),
        "evidence_notes": list(EVIDENCE_NOTES),
        "seeds_for_future_families_only":
            list(SEEDS_FOR_FUTURE_FAMILIES_ONLY),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "pushed_evidence_chain": list(PUSHED_EVIDENCE_CHAIN),
        "edit_allowance_spent": True,
        "candidate_6_may_continue_as_is": False,
        "candidate_6_may_receive_another_edit": False,
        "further_replays_authorized": False,
        "ledger_now_contains_six_records": True,
        "prior_five_records_unchanged": True,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    # five-record ledger (C1-C5)
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    # full C6 evidence chain
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_c6_dry_run_review()["verdict"] != VERDICT_C6R_FROZEN:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    labels_review = build_c6_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C6L_FROZEN:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "original_labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    replay_review = build_c6_replay_results_review(repo_root,
                                                   tracked_paths)
    if replay_review["verdict"] != VERDICT_C6RR_FROZEN:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "original_replay_review_not_certifying")
        record["blockers"].extend(replay_review["failures"])
        return record
    single_edit = build_c6_single_edit_clustering_filter(
        repo_root, tracked_paths)
    if single_edit["verdict"] != VERDICT_C6E_READY:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "single_edit_contract_not_certifying")
        return record
    edited_labels = build_c6_edited_labels_review(repo_root,
                                                  tracked_paths)
    if edited_labels["verdict"] != VERDICT_C6EL_FROZEN:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "edited_labels_review_not_certifying")
        record["blockers"].extend(edited_labels["failures"])
        return record
    edited_replay = build_c6_edited_replay_results_review(
        repo_root, tracked_paths)
    if edited_replay["verdict"] != VERDICT_C6EER_FROZEN:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "edited_replay_review_not_certifying")
        record["blockers"].extend(edited_replay["failures"])
        return record
    # the edited replay must indeed have failed -- the only valid
    # reason to record a rejection
    if edited_replay.get("honest_verdict") != EDITED_REPLAY_VERDICT:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "edited_replay_honest_verdict_mismatch")
        return record
    # the original replay must also have failed
    if replay_review.get("honest_verdict") != ORIGINAL_REPLAY_VERDICT:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append(
            "original_replay_honest_verdict_mismatch")
        return record
    # the edit token must indeed have been spent
    if single_edit.get("edit_token_used") != 1 or single_edit.get(
            "edits_remaining_after_this") != 0:
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("edit_token_not_spent")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_RJ6_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_RJ6_RECORDED
    return record


def validate_c6_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, permanence flags. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ6_RECORDED,
                                VERDICT_RJ6_REVIEW_REJECTED,
                                VERDICT_RJ6_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if r.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if r.get("edit_classification") != EDIT_CLASSIFICATION:
        errors.append("edit_classification_tampered")
    if r.get("replay_review_classification") != (
            REPLAY_REVIEW_CLASSIFICATION):
        errors.append("replay_classification_tampered")
    if r.get("head_at_edited_replay_review") != (
            HEAD_AT_EDITED_REPLAY_REVIEW):
        errors.append("head_tampered")
    if r.get("ledger_position") != 6:
        errors.append("ledger_position_tampered")
    expected_orig = {
        "verdict": ORIGINAL_REPLAY_VERDICT,
        "results_sha256": ORIGINAL_REPLAY_RESULTS_SHA256,
        "summary_sha256": ORIGINAL_REPLAY_SUMMARY_SHA256,
        "labels_sha256": ORIGINAL_LABELS_SHA256,
        "labels_summary_sha256": ORIGINAL_LABELS_SUMMARY_SHA256,
        "overlap_skipped_total": ORIGINAL_OVERLAP_SKIPPED_TOTAL,
        "variants": {name: dict(value) for name, value
                     in EXPECTED_ORIGINAL_REPLAY["variants"].items()},
        "all_variants_net_negative": True,
        "all_variants_gross_negative": True,
        "all_hit_rates_below_gross_breakeven": True,
    }
    if r.get("expected_original_replay") != expected_orig:
        errors.append("original_replay_tampered")
    expected_edit_block = {
        "edit_kind": EDIT_KIND,
        "min_bars_between_same_symbol_accepted_events_1h":
            MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
        "edit_token_used": EDIT_TOKEN_USED,
        "edits_remaining_after_this": EDITS_REMAINING_AFTER_THIS,
        "original_accepted_labels": EXPECTED_ACCEPTED_BEFORE_EDIT,
        "edited_accepted_labels": EXPECTED_ACCEPTED_AFTER_EDIT,
        "removed_by_clustering":
            EXPECTED_REMOVED_BY_CLUSTERING_TOTAL,
        "per_symbol_edited":
            {sym: dict(v) for sym, v
             in EXPECTED_PER_SYMBOL_EDITED.items()},
        "edit_labels_sha256": EDITED_LABELS_SHA256,
        "edit_labels_summary_sha256": EDITED_LABELS_SUMMARY_SHA256,
        "original_overlap_skipped_total":
            ORIGINAL_OVERLAP_SKIPPED_TOTAL,
        "edited_overlap_skipped_total":
            EDITED_OVERLAP_SKIPPED_TOTAL,
        "edit_worked_structurally_but_did_not_rescue_edge": True,
    }
    if r.get("expected_edit") != expected_edit_block:
        errors.append("edit_evidence_tampered")
    expected_edited_replay_block = {
        "verdict": EDITED_REPLAY_VERDICT,
        "results_sha256": EDITED_REPLAY_RESULTS_SHA256,
        "summary_sha256": EDITED_REPLAY_SUMMARY_SHA256,
        "overlap_skipped_total": EDITED_OVERLAP_SKIPPED_TOTAL,
        "variants": {name: dict(value) for name, value
                     in EXPECTED_EDITED_REPLAY["variants"].items()},
        "all_variants_net_negative": True,
        "all_variants_gross_negative": True,
        "all_hit_rates_below_gross_breakeven": True,
        "edited_results_worsened_versus_original": True,
    }
    if r.get("expected_edited_replay") != expected_edited_replay_block:
        errors.append("edited_replay_tampered")
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
    if tuple(r.get("pushed_evidence_chain") or ()) != (
            PUSHED_EVIDENCE_CHAIN):
        errors.append("pushed_evidence_chain_tampered")
    if r.get("edit_allowance_spent") is not True:
        errors.append("edit_allowance_must_be_spent")
    for key in ("candidate_6_may_continue_as_is",
                "candidate_6_may_receive_another_edit",
                "further_replays_authorized"):
        if r.get(key) is not False:
            errors.append("permanence_flag_wrong:" + key)
    if r.get("ledger_now_contains_six_records") is not True:
        errors.append("ledger_position_six_must_be_true")
    if r.get("prior_five_records_unchanged") is not True:
        errors.append("prior_records_unchanged_must_be_true")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    return {"valid": not errors, "errors": errors}
