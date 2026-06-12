"""SPARTA CANDIDATE #5 FAMILY PROPOSAL (READ-ONLY, RESEARCH ONLY,
PROPOSAL GATE ONLY): ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION.

The FIRST family proposal validated through the pushed Strategy Factory
Autopilot Research Loop V1: it is built by calling the loop's own
validate_candidate_family_proposal and screen_output_language gates, and
it is BLOCKED if the loop contract or any of the four rejection records
stops certifying.

CLEAN HYPOTHESIS (evidence language only): candidate #5 tests whether
eth/sol relative strength continuation after a shallow pullback performs
better than generic long swing structures.

This is a PROPOSAL. It runs no detector, fetches nothing, builds no
labels, replays nothing, creates no artifacts and no runners, and the
next stage is candidate_spec review by the human -- not detector
execution. Seeds from closed candidates are inherited as MACHINERY and
RISK CONTROLS only, never as evidence: no C4 setup_ids, replay rows, or
labels may be reused as evidence for candidate #5.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C5P_SCHEMA_VERSION = (
    "eth_sol_relative_strength_pullback_continuation_family_proposal.v1")
C5P_LABEL = ("SPARTA Candidate #5 Family Proposal "
             "(READ-ONLY, RESEARCH ONLY, PROPOSAL GATE ONLY, "
             "VALIDATED BY AUTOPILOT LOOP V1, NOT A RESCUE)")
C5P_MODE = "RESEARCH_ONLY"
VERDICT_C5P_READY = "CANDIDATE_5_FAMILY_PROPOSAL_READY"
VERDICT_C5P_BLOCKED = "CANDIDATE_5_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_5_SPEC_REVIEW"
NEXT_LOOP_STAGE = "candidate_spec"

CANDIDATE_ID = "ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1"
CANDIDATE_FAMILY = "eth_sol_relative_strength_pullback_continuation"

CLEAN_HYPOTHESIS = (
    "candidate #5 tests whether eth/sol relative strength continuation "
    "after a shallow pullback performs better than generic long swing "
    "structures")

DIFFERENCE_FROM_REJECTED_FAMILIES = (
    "1) not ny-session fvg/choch (no session windows, no fvg, no choch); "
    "2) not generic crypto intraday breakout-pullback (no range "
    "breakout requirement); "
    "3) not long-biased trend continuation with near-zero setup "
    "scarcity (no 15m bar-sequence micro-pattern); "
    "4) not c4 long 1h swing structure using the same structural-stop "
    "geometry (relative-strength gate replaces the swing-pair "
    "requirement); "
    "5) uses relative-strength context as a required gate, not a "
    "post-failure rescue; "
    "6) applies same-symbol no-overlap/cooldown at label/replay policy "
    "time, not as a rescue edit; "
    "7) requires fee-aware risk geometry before replay approval")

# the exact proposal object that the pushed loop gate validates
LOOP_PROPOSAL = {
    "family": CANDIDATE_FAMILY,
    "hypothesis": CLEAN_HYPOTHESIS,
    "difference_from_rejected_families":
        DIFFERENCE_FROM_REJECTED_FAMILIES,
    "uses_seeds_as_rescue": False,
}

SYMBOLS = ("ETHUSD", "SOLUSD")
TIMEFRAME = "1h"
DIRECTION = "long_only"

RELATIVE_STRENGTH_CONDITION = {
    "definition": ("the traded symbol's 20-bar 1h close-to-close return "
                   "must be positive AND strictly greater than the "
                   "other symbol's 20-bar 1h return at the same "
                   "timestamp"),
    "pair": "ETHUSD_vs_SOLUSD",
    "lookback_bars_1h": 20,
    "uses_completed_bars_only_no_lookahead": True,
    "is_a_required_gate_not_a_rescue": True,
}

PULLBACK_CONDITION = {
    "definition": ("a shallow pullback of 2 to 6 completed 1h bars "
                   "retracing at most 38.2 percent of the prior 20-bar "
                   "1h up-leg (leg low to leg high), holding above the "
                   "leg low"),
    "min_bars": 2, "max_bars": 6,
    "max_retrace_pct_of_leg": 38.2,
    "must_hold_above_leg_low": True,
}

CONTINUATION_TRIGGER = {
    "definition": ("first completed 1h bar that closes above the "
                   "pullback high while the relative-strength gate "
                   "still holds"),
    "entry_price": "close_of_the_trigger_bar",
    "anti_lookahead": ("entry recorded at trigger close; any replay "
                       "starts on the next 1h bar"),
    "one_setup_per_pullback": True,
}

STOP_LOGIC_POLICY = {
    "structural_stop": "low_of_the_pullback",
    "volatility_stop": "entry_minus_1_5x_atr14_on_1h",
    "selection": "WIDER_of_structural_and_volatility_stop_always",
    "never_tightened_after_entry": True,
    "structural_stop_clustering_lessons_used_as_risk_controls_only":
        True,
}

FEE_AWARE_GEOMETRY_POLICY = {
    "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,  # 81 = 27x3
    "checked_at_label_time": True,
    "assumed_round_trip_cost_bps": 27,
    "maker_execution_assumed": False,
    "floor_may_be_lowered": False,
    "fee_aware_geometry_required_before_replay_approval": True,
}

NON_OVERLAP_POLICY = {
    "definition": ("same-symbol no-overlap/cooldown is BUILT-IN "
                   "machinery applied at label/replay policy time: a "
                   "new setup on a symbol is not labeled accepted while "
                   "a prior accepted same-symbol setup's trade window "
                   "is still open, and replays must report "
                   "overlap-adjusted results"),
    "inherited_from_c4_as_machinery_not_rescue": True,
    "applied_at_label_replay_time_not_as_rescue_edit": True,
}

EDIT_ALLOWANCE_POLICY = (
    "at most ONE pre-committed edit for candidate #5, only if "
    "evidence-supported, only via a separately human-approved contract; "
    "if spent and results remain negative, candidate #5 is "
    "REJECTED_KEPT_ON_RECORD")

SEED_USAGE = (
    "same_symbol_non_overlap_cooldown_inherited_as_built_in_machinery",
    "sol_c4_clue_is_inspiration_only_not_evidence_of_edge",
    "btc_weakness_from_c4_is_not_reused_as_edge_evidence",
    "structural_stop_and_clustering_lessons_used_as_risk_controls_only",
    "no_c4_setup_ids_replay_rows_or_labels_may_be_reused_as_evidence",
)

REJECTION_CONDITIONS = _loop.AUTO_REJECTION_RULES  # inherited verbatim

PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "fee-honest replay net-positive in at least one variant on the "
    "overlap-adjusted independent sample",
    "all artifact hashes and gates certify",
    "promotion produces a human-review record only: no claim, no paper, "
    "no live, no capability change",
)

SAFETY_AND_NO_CLAIM = (
    "no trading, no paper trading, no live trading",
    "no wallet, account, api, or order capability",
    "no auto-push, no auto-commit",
    "no profitability claim and no winner wording at any stage",
    "all output must be evidence language only",
    "every stage requires evidence freeze and explicit human gates",
)


def get_candidate_5_proposal_label() -> str:
    return C5P_LABEL


def build_candidate_5_family_proposal() -> dict[str, Any]:
    """Assemble the proposal, gated on the pushed Autopilot Loop V1
    certifying live, the loop's own proposal gate accepting it, and the
    four-record ledger holding."""
    record: dict[str, Any] = {
        "schema_version": C5P_SCHEMA_VERSION, "label": C5P_LABEL,
        "mode": C5P_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "difference_from_rejected_families":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "loop_proposal": dict(LOOP_PROPOSAL),
        "loop_proposal_check": None,
        "hypothesis_language_check": None,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "relative_strength_condition": dict(
            RELATIVE_STRENGTH_CONDITION),
        "pullback_condition": dict(PULLBACK_CONDITION),
        "continuation_trigger": dict(CONTINUATION_TRIGGER),
        "stop_logic_policy": dict(STOP_LOGIC_POLICY),
        "fee_aware_geometry_policy": dict(FEE_AWARE_GEOMETRY_POLICY),
        "non_overlap_policy": dict(NON_OVERLAP_POLICY),
        "edit_allowance_policy": EDIT_ALLOWANCE_POLICY,
        "seed_usage": list(SEED_USAGE),
        "required_evidence_stages": list(_loop.LOOP_STAGES),
        "rejection_conditions": list(REJECTION_CONDITIONS),
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
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "reuses_c4_evidence": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C3_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C4_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_C5P_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C5P_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        record["blockers"].extend(loop_contract["blockers"])
        return record
    proposal_check = _loop.validate_candidate_family_proposal(
        dict(LOOP_PROPOSAL))
    record["loop_proposal_check"] = proposal_check
    language_check = _loop.screen_output_language(CLEAN_HYPOTHESIS)
    record["hypothesis_language_check"] = language_check
    if not proposal_check["acceptable"]:
        record["verdict"] = VERDICT_C5P_BLOCKED
        record["blockers"].append("loop_proposal_gate_rejected")
        record["blockers"].extend(proposal_check["errors"])
        return record
    if not language_check["acceptable"]:
        record["verdict"] = VERDICT_C5P_BLOCKED
        record["blockers"].append("forbidden_language_in_hypothesis")
        return record
    record["verdict"] = VERDICT_C5P_READY
    return record


def validate_candidate_5_family_proposal(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5P_READY, VERDICT_C5P_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("candidate_family") in _loop.REJECTED_FAMILIES:
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
    if tuple(r.get("symbols") or ()) != SYMBOLS:
        errors.append("symbols_tampered")
    if r.get("timeframe") != TIMEFRAME:
        errors.append("timeframe_tampered")
    if r.get("direction") != "long_only":
        errors.append("direction_not_long_only")
    if r.get("relative_strength_condition") != (
            RELATIVE_STRENGTH_CONDITION):
        errors.append("relative_strength_condition_tampered")
    if r.get("pullback_condition") != PULLBACK_CONDITION:
        errors.append("pullback_condition_tampered")
    if r.get("continuation_trigger") != CONTINUATION_TRIGGER:
        errors.append("continuation_trigger_tampered")
    if r.get("stop_logic_policy") != STOP_LOGIC_POLICY:
        errors.append("stop_logic_tampered")
    if r.get("fee_aware_geometry_policy") != FEE_AWARE_GEOMETRY_POLICY:
        errors.append("fee_geometry_tampered")
    fee = r.get("fee_aware_geometry_policy") or {}
    if fee.get(
            "fee_aware_geometry_required_before_replay_approval") is not \
            True:
        errors.append("fee_geometry_must_precede_replay")
    if r.get("non_overlap_policy") != NON_OVERLAP_POLICY:
        errors.append("non_overlap_policy_tampered")
    if r.get("edit_allowance_policy") != EDIT_ALLOWANCE_POLICY:
        errors.append("edit_allowance_tampered")
    if tuple(r.get("seed_usage") or ()) != SEED_USAGE:
        errors.append("seed_usage_tampered")
    if tuple(r.get("required_evidence_stages") or ()) != (
            _loop.LOOP_STAGES):
        errors.append("evidence_stages_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            REJECTION_CONDITIONS):
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
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "reuses_c4_evidence",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
