"""SPARTA CANDIDATE #6 FAMILY PROPOSAL (READ-ONLY, RESEARCH ONLY,
PROPOSAL GATE ONLY): MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

The Recommendation V1 PREFERRED pick, selected by explicit human
decision and validated through BOTH pushed gate layers: the Autopilot
Loop V1's validate_candidate_family_proposal / screen_output_language
gates AND the Recommendation V1 hard rejection rules. BLOCKED if the
five-record ledger, the loop, or the recommendation contract stops
certifying, or if the recommendation's preferred pick ever differs from
this candidate.

CLEAN HYPOTHESIS (evidence language only): candidate #6 tests whether
cross-sectional relative-strength selection improves continuation labels
by only allowing the current top-ranked symbol among btcusd, ethusd and
solusd to qualify. Selection-before-entry, not a rescue of any rejected
family. No wallet/order/portfolio allocation logic -- research labels
only.

This is a PROPOSAL. It runs no detector, fetches nothing, builds no
labels, replays nothing, creates no artifacts/runners/schedulers, and
the next stage is candidate_spec review by the human -- not detector
execution. Seeds are inspiration and risk-control lessons only, never
rescue paths; no C1-C5 setup_ids, replay rows, or labels may be reused
as candidate #6 evidence.
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
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C6P_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_family_proposal.v1")
C6P_LABEL = ("SPARTA Candidate #6 Family Proposal "
             "(READ-ONLY, RESEARCH ONLY, PROPOSAL GATE ONLY, VALIDATED "
             "BY AUTOPILOT LOOP V1 AND RECOMMENDATION V1, NOT A RESCUE)")
C6P_MODE = "RESEARCH_ONLY"
VERDICT_C6P_READY = "CANDIDATE_6_FAMILY_PROPOSAL_READY"
VERDICT_C6P_BLOCKED = "CANDIDATE_6_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_6_SPEC_REVIEW"
NEXT_LOOP_STAGE = "candidate_spec"

CANDIDATE_ID = "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1"
CANDIDATE_FAMILY = "multi_symbol_relative_strength_rotation_filter"

CLEAN_HYPOTHESIS = (
    "candidate #6 tests whether cross-sectional relative-strength "
    "selection improves continuation labels by only allowing the "
    "current top-ranked symbol among btcusd, ethusd and solusd to "
    "qualify; selection-before-entry, research labels only, no "
    "wallet/portfolio allocation logic")

DIFFERENCE_FROM_REJECTED_FAMILIES = (
    "1) not ny-session fvg/choch (no session windows, no fvg, no "
    "choch); "
    "2) not generic breakout-pullback rescue logic (no range "
    "breakout-retest structure); "
    "3) not long-biased trend continuation with setup scarcity (no 15m "
    "bar-sequence micro-pattern); "
    "4) not generic sol/btc long swing structure (no swing-pair "
    "requirement); "
    "5) not eth/sol shallow pullback continuation (no delayed "
    "pullback-resumption trigger); "
    "6) uses cross-sectional symbol ranking before any entry logic; "
    "7) top-ranked-only labeling is the core filter, not a "
    "post-failure edit; "
    "8) btc/eth/sol are compared simultaneously; no single-symbol "
    "setup can qualify without ranking context")

LOOP_PROPOSAL = {
    "family": CANDIDATE_FAMILY,
    "hypothesis": CLEAN_HYPOTHESIS,
    "difference_from_rejected_families":
        DIFFERENCE_FROM_REJECTED_FAMILIES,
    "uses_seeds_as_rescue": False,
}

SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1h"
DIRECTION = "long_only"
DIRECTION_NOTE = "long-only research labels; never trading capability"

RANKING_CONDITION = {
    "definition": ("compute relative strength for all three symbols "
                   "using completed 1h bars only; the candidate symbol "
                   "must be rank #1 at trigger time"),
    "symbols_compared_simultaneously": True,
    "rs_metric_and_lookback_frozen_numerically_at_spec_review": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
}

CONTINUATION_CONDITION = {
    "definition": ("a simple deterministic top-ranked continuation "
                   "event: a fresh closing strength event on the "
                   "rank-#1 symbol with entry at that completed bar's "
                   "close; exact numeric form frozen at spec review"),
    "avoids_delayed_pullback_resumption_scarcity_from_c5": True,
    "does_not_reuse_c5_shallow_pullback_as_is": True,
    "no_intrabar_entry": True,
    "evaluation_starts_next_1h_bar": True,
}

STOP_LOGIC_POLICY = {
    "rule": "WIDER stop: structure or atr-based, whichever is wider",
    "exact_form_frozen_at_spec_review": True,
    "never_tightened_after_entry": True,
}

FEE_AWARE_GEOMETRY_POLICY = {
    "fee_model_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "floor_checked_before_replay_eligibility": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

NON_OVERLAP_POLICY = {
    "built_in_at_label_replay_policy_time": True,
    "reduce_or_keep_only_never_add_trades": True,
    "is_not_an_edit_or_rescue_path": True,
}

EDIT_ALLOWANCE_POLICY = (
    "at most ONE pre-committed edit for candidate #6, only if "
    "evidence-supported, only via a separately human-approved "
    "contract; if spent and results remain negative, candidate #6 is "
    "REJECTED_KEPT_ON_RECORD")

SEED_USAGE = (
    "sol_side_relative_strength_recurrence_is_inspiration_only",
    "c5_gross_positive_2r_observation_is_not_promotion_evidence",
    "thin_risk_fee_sensitivity_is_a_risk_control_lesson_only",
    "trigger_resumption_scarcity_is_a_warning_to_avoid_delayed"
    "_pullback_rescue_entries",
    "same_symbol_non_overlap_remains_a_risk_control_lesson",
    "eth_c5_negative_contribution_is_not_edge_evidence",
    "no_c1_c5_setup_ids_replay_rows_or_labels_may_be_reused_as"
    "_candidate_6_evidence",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "fee-honest replay net-positive on the overlap-adjusted "
    "independent sample with sample size not near-zero",
    "all artifact hashes and gates certify",
    "promotion produces a human-review record only: no claim, no "
    "paper, no live, no capability change",
)

SAFETY_AND_NO_CLAIM = (
    "no trading, no paper trading, no live trading",
    "no wallet, account, api, or order capability",
    "no auto-push, no auto-commit",
    "no profitability claim and no winner wording at any stage",
    "all output must be evidence language only",
    "every stage requires evidence freeze and explicit human gates",
)


def get_candidate_6_proposal_label() -> str:
    return C6P_LABEL


def build_candidate_6_family_proposal() -> dict[str, Any]:
    """Assemble the proposal, gated on the five-record ledger, the
    pushed loop, AND the pushed recommendation (preferred pick must be
    this candidate); validated by both pushed gate layers."""
    record: dict[str, Any] = {
        "schema_version": C6P_SCHEMA_VERSION, "label": C6P_LABEL,
        "mode": C6P_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "selected_candidate_id": CANDIDATE_ID,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "difference_from_rejected_families":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "loop_proposal": dict(LOOP_PROPOSAL),
        "loop_proposal_check": None,
        "hypothesis_language_check": None,
        "recommendation_hard_rules_check": None,
        "recommendation_preferred_matches": None,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "ranking_condition": dict(RANKING_CONDITION),
        "continuation_condition": dict(CONTINUATION_CONDITION),
        "stop_logic_policy": dict(STOP_LOGIC_POLICY),
        "fee_aware_geometry_policy": dict(FEE_AWARE_GEOMETRY_POLICY),
        "non_overlap_policy": dict(NON_OVERLAP_POLICY),
        "edit_allowance_policy": EDIT_ALLOWANCE_POLICY,
        "seed_usage": list(SEED_USAGE),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "required_evidence_stages": list(_loop.LOOP_STAGES),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "promotion_to_human_review_conditions": list(
            PROMOTION_TO_HUMAN_REVIEW_CONDITIONS),
        "safety_and_no_claim": list(SAFETY_AND_NO_CLAIM),
        "next_loop_stage": NEXT_LOOP_STAGE,
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
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_label_replay_files_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    recommendation = _rec.build_candidate_recommendation()
    if recommendation["verdict"] != _rec.VERDICT_CR_READY:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    record["recommendation_preferred_matches"] = (
        recommendation["preferred_candidate_6"] == CANDIDATE_ID
        and recommendation[
            "preferred_is_proposal_recommendation_only"] is True)
    if not record["recommendation_preferred_matches"]:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append(
            "selected_candidate_is_not_the_recommendation_preferred")
        return record
    proposal_check = _loop.validate_candidate_family_proposal(
        dict(LOOP_PROPOSAL))
    record["loop_proposal_check"] = proposal_check
    language_check = _loop.screen_output_language(CLEAN_HYPOTHESIS)
    record["hypothesis_language_check"] = language_check
    hard_check = _rec.apply_hard_rejection_rules({
        "family": CANDIDATE_FAMILY,
        "hypothesis": CLEAN_HYPOTHESIS,
        "materially_different_because":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "why_not_rescue": ("selection-before-entry is a new mechanism; "
                           "no rejected family geometry, labels, or "
                           "thresholds are reused"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model", "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "direction": DIRECTION,
    })
    record["recommendation_hard_rules_check"] = hard_check
    if not proposal_check["acceptable"]:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append("loop_proposal_gate_rejected")
        record["blockers"].extend(proposal_check["errors"])
        return record
    if not language_check["acceptable"]:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append("forbidden_language_in_hypothesis")
        return record
    if not hard_check["acceptable"]:
        record["verdict"] = VERDICT_C6P_BLOCKED
        record["blockers"].append(
            "recommendation_hard_rules_rejected")
        record["blockers"].extend(hard_check["rejections"])
        return record
    record["verdict"] = VERDICT_C6P_READY
    return record


def validate_candidate_6_family_proposal(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6P_READY, VERDICT_C6P_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("selected_candidate_id") != CANDIDATE_ID:
        errors.append("selected_candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("candidate_family") in _loop.REJECTED_FAMILIES \
            or r.get("candidate_family") in _rec.ALL_REJECTED_FAMILIES:
        errors.append("candidate_family_is_a_rejected_family")
    if r.get("clean_hypothesis") != CLEAN_HYPOTHESIS:
        errors.append("hypothesis_tampered")
    if r.get("difference_from_rejected_families") != (
            DIFFERENCE_FROM_REJECTED_FAMILIES):
        errors.append("differences_tampered")
    if r.get("loop_proposal") != LOOP_PROPOSAL:
        errors.append("loop_proposal_tampered")
    if r.get("loop_proposal", {}).get("uses_seeds_as_rescue") is not \
            False:
        errors.append("seeds_must_not_be_rescue_paths")
    if r.get("symbols") != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        errors.append("symbols_tampered")
    if r.get("timeframe") != "1h":
        errors.append("timeframe_tampered")
    if r.get("direction") != "long_only":
        errors.append("direction_not_long_only")
    if r.get("ranking_condition") != RANKING_CONDITION:
        errors.append("ranking_condition_tampered")
    if r.get("continuation_condition") != CONTINUATION_CONDITION:
        errors.append("continuation_condition_tampered")
    continuation = r.get("continuation_condition") or {}
    if continuation.get(
            "avoids_delayed_pullback_resumption_scarcity_from_c5") is \
            not True or continuation.get(
            "does_not_reuse_c5_shallow_pullback_as_is") is not True:
        errors.append("c5_rescue_protection_weakened")
    if r.get("stop_logic_policy") != STOP_LOGIC_POLICY:
        errors.append("stop_logic_tampered")
    fee = r.get("fee_aware_geometry_policy") or {}
    if fee != FEE_AWARE_GEOMETRY_POLICY:
        errors.append("fee_geometry_tampered")
    if fee.get("fee_model_round_trip_bps") != 27 or fee.get(
            "minimum_gross_target_distance_floor_bps") != 81:
        errors.append("fee_numbers_tampered")
    if r.get("non_overlap_policy") != NON_OVERLAP_POLICY:
        errors.append("non_overlap_tampered")
    if r.get("edit_allowance_policy") != EDIT_ALLOWANCE_POLICY:
        errors.append("edit_allowance_tampered")
    if tuple(r.get("seed_usage") or ()) != SEED_USAGE:
        errors.append("seed_usage_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_rescue_flag_tampered")
    if tuple(r.get("required_evidence_stages") or ()) != (
            _loop.LOOP_STAGES):
        errors.append("evidence_stages_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("promotion_to_human_review_conditions") or ()) != (
            PROMOTION_TO_HUMAN_REVIEW_CONDITIONS):
        errors.append("promotion_conditions_tampered")
    if tuple(r.get("safety_and_no_claim") or ()) != SAFETY_AND_NO_CLAIM:
        errors.append("safety_no_claim_tampered")
    if r.get("next_loop_stage") != "candidate_spec":
        errors.append("next_stage_must_be_candidate_spec")
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
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
