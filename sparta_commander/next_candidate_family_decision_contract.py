"""SPARTA NEXT CANDIDATE FAMILY DECISION (READ-ONLY, DECISION RECORD ONLY,
RUNS NOTHING).

Candidate #1 (NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1) died honestly:
COST_NON_VIABLE_RISK_GEOMETRY -- max 39.68 bps risk units against an 81 bps
floor, -21.04R fee-honest replay. This contract records the HUMAN decision
that follows: no more 1m ultra-scalp FVG/CHOCH geometry in this lane; the
next family is CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1 -- 15m/1h
context, breakout + pullback/retest + continuation confirmation, structural
or ATR-based stops with NATURALLY wider risk units, the unchanged 81 bps
floor required before any replay eligibility, and the same fee-honest
discipline. The rejected candidate is never revived without a new family or
a separately approved lower-cost lane; maker execution is never assumed.
This block decides only -- no spec, no detection, no replay, no scoring.
"""

from __future__ import annotations

import hashlib as _hashlib
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    EXPECTED_V3_ARTIFACT_SHA256,
    REJECTION_REASON as C1_REJECTION_REASON,
    REJECTION_STATUS as C1_REJECTION_STATUS,
    V3_ARTIFACT_PATH,
    VERDICT_RJ_RECORDED,
    build_rejection_record,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_FAMILY as REJECTED_FAMILY,
    CANDIDATE_ID as REJECTED_CANDIDATE_ID,
)

NF_SCHEMA_VERSION = "next_candidate_family_decision.v1"
NF_LABEL = ("SPARTA Next Candidate Family Decision "
            "(READ-ONLY, DECISION RECORD ONLY, BUILDS NOTHING)")
NF_MODE = "RESEARCH_ONLY"
VERDICT_NF_RECORDED = (
    "NEXT_CANDIDATE_FAMILY_DECISION_RECORDED_BREAKOUT_PULLBACK_STRUCTURE")
VERDICT_NF_REJECTED = "NEXT_CANDIDATE_FAMILY_DECISION_REJECTED"
VERDICT_NF_BLOCKED = "NEXT_CANDIDATE_FAMILY_DECISION_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_BREAKOUT_PULLBACK_STRATEGY_SPEC_CONTRACT")

NEXT_FAMILY_ID = "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1"
NEXT_FAMILY_NAME = "intraday_breakout_pullback_structure"

CANDIDATE_CONCEPT = (
    "use_15m_and_1h_context_instead_of_1m_scalp_geometry",
    "look_for_directional_momentum_expansion_or_range_breakout",
    "wait_for_pullback_or_retest_into_structure",
    "enter_only_if_continuation_confirms",
    "stop_at_structural_swing_or_atr_based_invalidation",
    "require_minimum_risk_distance_gte_81_bps_before_replay_eligibility",
    "preserve_fee_honest_cost_discipline_27bps_taker_round_trip",
)

PREFERENCE_RATIONALE = (
    "wider_stop_geometry_is_more_likely_to_survive_27bps_taker_execution",
    "avoids_sub_40_bps_1m_impulse_candle_risk_units",
    "still_deterministic_and_testable",
    "suitable_for_staged_historical_candle_replay",
    "compatible_with_the_existing_auto_research_machinery",
)

REJECTED_EVIDENCE_SUMMARY = {
    "rejected_candidate_id": REJECTED_CANDIDATE_ID,
    "rejected_family": REJECTED_FAMILY,
    "rejection_status": C1_REJECTION_STATUS,
    "rejection_reason": C1_REJECTION_REASON,
    "v1v2_max_risk_bps": 33.15758,
    "v3_max_risk_bps": 39.680383,
    "floor_bps": 81,
    "cost_viable_survivors": 0,
    "fee_honest_replay_net_r": -21.040902,
}

FORBIDDEN = (
    "reviving_the_rejected_fvg_choch_candidate_without_a_new_family_or"
    "_separate_lower_cost_lane",
    "assuming_maker_execution", "lowering_the_81_bps_cost_floor",
    "live_trading", "paper_trading", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "deleting_or_hiding_rejected_evidence",
    "replay_scorer_or_optimizer_runs_in_this_block", "gate_unlocks",
)

REVIEW_CHECKLIST = (
    "rejection_record_certified_and_intact",
    "rejection_evidence_artifact_sha_pinned",
    "next_family_differs_from_rejected_scalp_geometry",
    "concept_uses_htf_context_not_1m_scalp",
    "81bps_floor_required_before_replay_eligibility",
    "no_maker_assumption_and_no_cost_lowering",
    "fee_honest_discipline_preserved",
    "nothing_built_or_run_in_this_block",
)


def get_next_family_decision_label() -> str:
    return NF_LABEL


def observe_decision_preconditions(repo_root: Any,
                                   tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY: the rejection evidence this decision depends on."""
    root = _pathlib.Path(str(repo_root))
    artifact = root / V3_ARTIFACT_PATH
    return {
        "rejection_record_verdict": build_rejection_record(
            repo_root, tracked_paths=[]).get("verdict"),
        "v3_artifact_sha256": (_hashlib.sha256(
            artifact.read_bytes()).hexdigest()
            if artifact.is_file() else None),
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
    }


def certify_next_family_decision(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the next-family decision. Pure."""
    record: dict[str, Any] = {
        "schema_version": NF_SCHEMA_VERSION, "label": NF_LABEL,
        "mode": NF_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "next_family_id": NEXT_FAMILY_ID,
        "next_family_name": NEXT_FAMILY_NAME,
        "candidate_concept": list(CANDIDATE_CONCEPT),
        "preference_rationale": list(PREFERENCE_RATIONALE),
        "rejected_evidence_summary": dict(REJECTED_EVIDENCE_SUMMARY),
        "forbidden": list(FORBIDDEN),
        "maker_execution_assumed": False,
        "cost_floor_lowered": False,
        "rejected_candidate_revived": False,
        "rejected_evidence_kept_on_record": True,
        "strategy_spec_built_here": False,
        "this_decision_changes_no_rules": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "modifies_labels": False, "deletes_labels": False,
        "modifies_staged_files": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(observation, dict):
        record["verdict"] = VERDICT_NF_BLOCKED
        record["blockers"].append("observation_missing")
        return record
    o = observation
    if o.get("v3_artifact_sha256") is None:
        record["verdict"] = VERDICT_NF_BLOCKED
        record["blockers"].append("rejection_evidence_missing")
        return record

    r: dict[str, bool] = {}
    r["rejection_record_certified_and_intact"] = (
        o.get("rejection_record_verdict") == VERDICT_RJ_RECORDED)
    r["rejection_evidence_artifact_sha_pinned"] = (
        o.get("v3_artifact_sha256") == EXPECTED_V3_ARTIFACT_SHA256)
    r["next_family_differs_from_rejected_scalp_geometry"] = (
        NEXT_FAMILY_ID != REJECTED_CANDIDATE_ID
        and NEXT_FAMILY_NAME != REJECTED_FAMILY
        and "fvg_choch" not in NEXT_FAMILY_NAME)
    r["concept_uses_htf_context_not_1m_scalp"] = (
        "use_15m_and_1h_context_instead_of_1m_scalp_geometry"
        in CANDIDATE_CONCEPT
        and not any("1m_scalp" in item and "instead" not in item
                    for item in CANDIDATE_CONCEPT))
    r["81bps_floor_required_before_replay_eligibility"] = (
        "require_minimum_risk_distance_gte_81_bps_before_replay_eligibility"
        in CANDIDATE_CONCEPT
        and REJECTED_EVIDENCE_SUMMARY["floor_bps"] == 81)
    r["no_maker_assumption_and_no_cost_lowering"] = (
        "assuming_maker_execution" in FORBIDDEN
        and "lowering_the_81_bps_cost_floor" in FORBIDDEN)
    r["fee_honest_discipline_preserved"] = (
        "preserve_fee_honest_cost_discipline_27bps_taker_round_trip"
        in CANDIDATE_CONCEPT)
    r["nothing_built_or_run_in_this_block"] = not o.get(
        "tracked_output_paths")
    record["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        record["verdict"] = VERDICT_NF_REJECTED
        record["blockers"].extend("check_failed:" + n for n in failed)
        return record
    record["verdict"] = VERDICT_NF_RECORDED
    return record


def build_next_family_decision(repo_root: Any,
                               tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the rejection evidence read-only and certify the decision."""
    return certify_next_family_decision(
        observe_decision_preconditions(repo_root, tracked_paths))


def validate_next_family_decision(record: Any) -> dict[str, Any]:
    """Validate the decision record's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    v = record
    if v.get("verdict") not in (VERDICT_NF_RECORDED, VERDICT_NF_REJECTED,
                                VERDICT_NF_BLOCKED):
        errors.append("bad_verdict")
    if v.get("next_family_id") != NEXT_FAMILY_ID:
        errors.append("next_family_tampered")
    if v.get("next_family_name") != NEXT_FAMILY_NAME:
        errors.append("family_name_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("candidate_concept") or ()) != CANDIDATE_CONCEPT:
        errors.append("concept_tampered")
    if tuple(v.get("preference_rationale") or ()) != PREFERENCE_RATIONALE:
        errors.append("rationale_tampered")
    if v.get("rejected_evidence_summary") != REJECTED_EVIDENCE_SUMMARY:
        errors.append("rejected_evidence_summary_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key in ("maker_execution_assumed", "cost_floor_lowered",
                "rejected_candidate_revived", "strategy_spec_built_here"):
        if v.get(key) is not False:
            errors.append("must_be_false_forever:" + key)
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_NF_RECORDED:
        if v.get("blockers"):
            errors.append("recorded_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("recorded_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_NF_REJECTED, VERDICT_NF_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_recorded_without_blockers")
    for key, want in (
        ("rejected_evidence_kept_on_record", True),
        ("this_decision_changes_no_rules", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_labels", "deletes_labels", "modifies_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
