"""SPARTA NY-Session FVG+CHOCH MUTABLE CANDIDATE EDIT V3 - WIDER
STRUCTURAL STOP (READ-ONLY, RESEARCH ONLY, AUTHORIZES NOTHING).

The ONE V3 experiment authorized by the pushed decision contract: the stop
moves from the 1m-FVG impulse-candle extreme to the CHOCH leg STRUCTURAL
extreme (long: below the leg's structural swing low; short: above the leg's
structural swing high), and the risk unit is recomputed from entry to that
structural stop. NOTHING else changes: entry logic, HTF context, V1
freshness controls, CHOCH logic, LTF FVG logic, the 4R target reference,
the V2 cost floor (81 bps, never lowered), taker-cost assumptions (maker
NEVER assumed), locked scorer, locked instructions. Accepted labels must
still pass the 81 bps floor after the future, separately approved
re-detection. This block edits the candidate asset only and runs nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_ASSET_ACCEPTED,
    validate_candidate_asset,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    NEW_PARAMETERS as V1_PARAMETERS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    V2_NEW_PARAMETERS,
    build_edited_candidate_asset_v2,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_v3_wider_structural_stop_decision_contract import (
    VERDICT_V3D_RECORDED,
    build_v3_decision,
)

M3_SCHEMA_VERSION = (
    "ny_session_fvg_choch_mutable_candidate_edit_v3_wider_structural_stop.v1")
M3_LABEL = ("SPARTA NY-Session FVG+CHOCH Mutable Candidate Edit V3 - Wider "
            "Structural Stop (READ-ONLY, RESEARCH ONLY, EDITS THE "
            "CANDIDATE ASSET ONLY)")
M3_MODE = "RESEARCH_ONLY"
EDIT_V3_ID = (
    "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_WIDER_STRUCTURAL_STOP")
VERDICT_M3_READY = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_READY"
VERDICT_M3_BLOCKED = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_V3_REDETECTION_ON_EXPANDED_SAMPLE"

V3_STOP_RULE_TEXT = (
    "research stop placed beyond the CHOCH leg STRUCTURAL extreme: long "
    "setups below the CHOCH leg structural swing low, short setups above "
    "the CHOCH leg structural swing high; the risk unit is recomputed from "
    "entry to the structural stop; research-only, never live sizing")

V3_NEW_PARAMETERS = {
    "stop_geometry": "choch_leg_structural_extreme",
    "stop_rule_long": "stop_below_choch_leg_structural_swing_low",
    "stop_rule_short": "stop_above_choch_leg_structural_swing_high",
    "risk_unit_recomputed_from_entry_to_structural_stop": True,
    "accepted_labels_must_pass_81bps_floor": True,
}

UNCHANGED_GUARANTEES = (
    "entry_logic_unchanged",
    "htf_context_logic_unchanged",
    "v1_freshness_controls_unchanged_24_true_2",
    "choch_logic_unchanged",
    "ltf_fvg_logic_unchanged",
    "4r_target_reference_unchanged_replay_scoring_future_gated",
    "v2_cost_floor_unchanged_81bps_never_lowered",
    "maker_execution_never_assumed",
    "locked_scorer_unchanged",
    "locked_instructions_unchanged",
    "v1_v2_rejected_evidence_kept_on_record",
)

FORBIDDEN = (
    "changing_locked_scorer", "changing_locked_instructions",
    "lowering_costs", "assuming_maker_execution",
    "changing_entry_or_htf_context_logic",
    "changing_freshness_choch_or_ltf_fvg_logic",
    "detector_replay_scorer_or_optimizer_runs_in_this_block",
    "live_paper_micro_live_authorization", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "deleting_or_hiding_v1_v2_rejected_evidence", "gate_unlocks",
)


def get_mutable_candidate_edit_v3_label() -> str:
    return M3_LABEL


def build_edited_candidate_asset_v3() -> dict[str, Any]:
    """The V3-edited candidate asset: the V2-edited instance with ONLY the
    stop geometry changed. Deep-copied; V2 output never mutated. Pure."""
    base = build_edited_candidate_asset_v2()
    fields = dict(base["fields"])
    parameters = dict(fields["parameters"])
    parameters.update(V3_NEW_PARAMETERS)
    fields["parameters"] = parameters
    fields["risk_rules_text"] = V3_STOP_RULE_TEXT
    fields["constraints"] = (str(fields["constraints"])
                             + "; v3 stop geometry: choch leg structural "
                               "extreme; 81 bps floor rechecked after "
                               "redetection; accepted labels may not "
                               "bypass the floor")
    fields["lineage"] = (str(fields["lineage"])
                         + ">edit_v3_wider_structural_stop_per_v3_decision"
                           "_contract")
    fields["status"] = "proposed"
    fields["audit_notes"] = ("mutable candidate edit v3 applied per the "
                             "pushed V3 decision contract; one experiment "
                             "only; if v3 fails cost viability or "
                             "fee-honest replay the candidate is rejected "
                             "and kept on record; re-detection requires "
                             "separate human approval")
    fields["rationale"] = ("impulse-candle stops produced 2.6-33.2 bps risk "
                           "units versus the 81 bps cost floor; the CHOCH "
                           "leg structural extreme is the nearest auditable "
                           "structure wide enough to plausibly clear the "
                           "floor without touching costs or detection logic")
    edited = dict(base)
    edited["fields"] = fields
    return edited


def record_mutable_candidate_edit_v3(
        v3_decision_verdict: Any) -> dict[str, Any]:
    """Assemble the V3 edit record, gated on the V3 decision verdict. Pure."""
    record: dict[str, Any] = {
        "schema_version": M3_SCHEMA_VERSION, "label": M3_LABEL,
        "mode": M3_MODE, "lane": "crypto_d1_auto_research",
        "edit_id": EDIT_V3_ID, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "v3_decision_verdict": v3_decision_verdict,
        "v3_new_parameters": dict(V3_NEW_PARAMETERS),
        "v3_stop_rule_text": V3_STOP_RULE_TEXT,
        "unchanged_guarantees": list(UNCHANGED_GUARANTEES),
        "forbidden": list(FORBIDDEN),
        "edited_asset": None, "edited_asset_verdict": None,
        "maker_execution_assumed": False,
        "cost_floor_lowered": False,
        "accepted_labels_may_bypass_floor": False,
        "one_experiment_only": True,
        "redetection_requires_separate_human_approval": True,
        "replay_requires_separate_human_approval": True,
        "previous_evidence_kept_on_record": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False,
        "modifies_locked_instructions": False,
        "modifies_detector_rules": False,
        "modifies_detector_label_schema": False,
        "modifies_staged_candles": False,
        "modifies_previous_labels": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
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
    if v3_decision_verdict != VERDICT_V3D_RECORDED:
        record["verdict"] = VERDICT_M3_BLOCKED
        record["blockers"].append("v3_decision_not_recorded")
        return record
    edited = build_edited_candidate_asset_v3()
    asset_check = validate_candidate_asset(edited)
    record["edited_asset_verdict"] = asset_check.get("verdict")
    if asset_check.get("verdict") != VERDICT_ASSET_ACCEPTED:
        record["verdict"] = VERDICT_M3_BLOCKED
        record["blockers"].append("edited_asset_rejected_by_asset_spec")
        record["blockers"].extend(asset_check.get("errors") or [])
        return record
    record["edited_asset"] = edited
    record["verdict"] = VERDICT_M3_READY
    return record


def build_mutable_candidate_edit_v3(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Build against the LIVE pushed V3 decision contract (which itself
    verifies the frozen V2 evidence on disk)."""
    decision = build_v3_decision(repo_root, tracked_paths=[])
    return record_mutable_candidate_edit_v3(decision.get("verdict"))


def validate_mutable_candidate_edit_v3(record: Any) -> dict[str, Any]:
    """Validate the V3 edit record's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_M3_READY, VERDICT_M3_BLOCKED):
        errors.append("bad_verdict")
    if r.get("edit_id") != EDIT_V3_ID:
        errors.append("edit_id_tampered")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("v3_new_parameters") != V3_NEW_PARAMETERS:
        errors.append("v3_parameters_tampered")
    if r.get("v3_stop_rule_text") != V3_STOP_RULE_TEXT:
        errors.append("stop_rule_text_tampered")
    if tuple(r.get("unchanged_guarantees") or ()) != UNCHANGED_GUARANTEES:
        errors.append("unchanged_guarantees_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if r.get("maker_execution_assumed") is not False:
        errors.append("maker_execution_must_never_be_assumed")
    if r.get("cost_floor_lowered") is not False:
        errors.append("cost_floor_must_never_be_lowered")
    if r.get("accepted_labels_may_bypass_floor") is not False:
        errors.append("floor_bypass_must_be_impossible")
    if r.get("verdict") == VERDICT_M3_READY:
        if r.get("blockers"):
            errors.append("ready_with_blockers")
        if r.get("v3_decision_verdict") != VERDICT_V3D_RECORDED:
            errors.append("ready_without_recorded_v3_decision")
        if r.get("edited_asset_verdict") != VERDICT_ASSET_ACCEPTED:
            errors.append("ready_without_accepted_asset")
        edited = r.get("edited_asset") or {}
        parameters = (edited.get("fields") or {}).get("parameters") or {}
        for key, value in V3_NEW_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("v3_parameter_missing:" + key)
        for key, value in V1_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("v1_parameter_lost:" + key)
        for key, value in V2_NEW_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("v2_parameter_lost:" + key)
        if (edited.get("fields") or {}).get("risk_rules_text") != (
                V3_STOP_RULE_TEXT):
            errors.append("risk_rules_text_not_v3_stop_rule")
    for key, want in (
        ("one_experiment_only", True),
        ("redetection_requires_separate_human_approval", True),
        ("replay_requires_separate_human_approval", True),
        ("previous_evidence_kept_on_record", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
        ("modifies_detector_rules", False),
        ("modifies_detector_label_schema", False),
        ("modifies_staged_candles", False),
        ("modifies_previous_labels", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
