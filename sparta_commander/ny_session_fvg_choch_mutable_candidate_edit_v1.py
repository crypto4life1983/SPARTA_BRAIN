"""SPARTA NY-Session FVG+CHOCH MUTABLE CANDIDATE EDIT V1 (READ-ONLY,
RESEARCH ONLY, AUTHORIZES NOTHING).

The human-approved response to the detector-labels review: three stale-FVG
controls added to the ONE editable object in the lane -- the mutable
candidate asset's `parameters` field. Nothing else changes: locked
instructions, the locked scorer, the detector label schema, replay logic,
PnL logic, mission flow, candles, and previous labels are all untouched, and
the edit is drawn strictly from the review's recommended-edit list.

Re-detection with the edited candidate is NOT run here and requires its own
separate human approval.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_ASSET_ACCEPTED,
    validate_candidate_asset,
)
from sparta_commander.ny_session_fvg_choch_detector_labels_review_contract import (
    RECOMMENDED_MUTABLE_CANDIDATE_EDITS,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
    VERDICT_FS_READY,
    build_candidate_asset_instance,
    build_ny_fvg_choch_strategy_spec,
    validate_ny_fvg_choch_strategy_spec,
)

ME_SCHEMA_VERSION = "ny_session_fvg_choch_mutable_candidate_edit.v1"
ME_LABEL = ("SPARTA NY-Session FVG+CHOCH Mutable Candidate Edit V1 "
            "(READ-ONLY, RESEARCH ONLY, EDITS THE CANDIDATE ASSET ONLY)")
ME_MODE = "RESEARCH_ONLY"
EDIT_ID = "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1"
VERDICT_ME_READY = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_READY"
VERDICT_ME_BLOCKED = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_REDETECTION_WITH_EDITED_CANDIDATE"

# The three approved edits, drawn from the review's recommendation list.
APPLIED_EDITS = (
    "add_max_fvg_age_bars",
    "require_fresh_unmitigated_15m_fvg",
    "add_max_zone_touches_before_invalidation",
)

# V1 research values -- themselves mutable-candidate parameters, editable in
# future approved edits. They authorize nothing.
NEW_PARAMETERS = {
    # a 15m FVG older than 24 bars (6 hours) is too stale to trade-research
    "max_fvg_age_bars": 24,
    # the gap must be untested: no candle traded back into the zone between
    # formation and the session touch that starts a setup attempt
    "require_fresh_unmitigated_15m_fvg": True,
    # after this many session touches without an accepted setup the zone is
    # treated as consumed/invalid for further attempts
    "max_zone_touches_before_invalidation": 2,
}

EDIT_RATIONALE = (
    "detector labels review found 259 setup attempts with 0 accepted on "
    "2026-06-10: spec-faithful detection over-triggered stale 15m FVG zones "
    "accumulated across 10 days of context; these three controls limit "
    "attempts to fresh, unmitigated, lightly-tested zones")

UNCHANGED_GUARANTEES = (
    "locked_instructions_unchanged",
    "locked_scorer_unchanged",
    "detector_label_schema_unchanged_29_fields",
    "detector_status_set_unchanged_9_statuses",
    "frozen_deterministic_rule_text_unchanged",
    "replay_logic_unchanged",
    "no_pnl_logic_anywhere",
    "mission_flow_registry_unchanged",
    "staged_candles_unchanged",
    "previous_detector_labels_unchanged_kept_on_record",
)

FORBIDDEN = (
    "editing_locked_instructions", "editing_locked_scorer",
    "editing_detector_label_schema", "editing_replay_logic",
    "adding_pnl_or_scoring_fields", "automatic_redetection",
    "live_trading_capability", "paper_micro_live_authorization",
    "network_or_data_retrieval", "credentials_or_api_keys",
    "account_wallet_login_access", "order_endpoints", "candle_mutation",
    "gate_unlocks",
)


def get_mutable_candidate_edit_v1_label() -> str:
    return ME_LABEL


def build_edited_candidate_asset() -> dict[str, Any]:
    """The V1-edited candidate asset instance: base instance + the three
    stale-FVG controls inside `parameters`. Deep-copied; the base builder's
    output is never mutated. Pure."""
    base = build_candidate_asset_instance()
    fields = dict(base["fields"])
    parameters = dict(fields["parameters"])
    parameters.update(NEW_PARAMETERS)
    fields["parameters"] = parameters
    fields["constraints"] = (str(fields["constraints"])
                             + "; stale-FVG controls v1: max_fvg_age_bars, "
                               "require_fresh_unmitigated_15m_fvg, "
                               "max_zone_touches_before_invalidation")
    fields["lineage"] = ("edit_v1_of_root_candidate:" + CANDIDATE_ID
                         + ":per_detector_labels_review_2026-06-10")
    fields["status"] = "proposed"
    fields["audit_notes"] = ("mutable candidate edit v1 applied per detector "
                             "labels review; previous labels kept on record; "
                             "re-detection requires separate human approval")
    fields["rationale"] = EDIT_RATIONALE
    edited = dict(base)
    edited["fields"] = fields
    return edited


def build_mutable_candidate_edit_v1() -> dict[str, Any]:
    """Assemble the edit record: gated on the READY strategy spec, the
    review's recommendation list, and the edited asset passing the pushed
    mutable-asset schema. Pure."""
    record: dict[str, Any] = {
        "schema_version": ME_SCHEMA_VERSION, "label": ME_LABEL,
        "mode": ME_MODE, "lane": "crypto_d1_auto_research",
        "edit_id": EDIT_ID, "candidate_id": CANDIDATE_ID,
        "verdict": None, "blockers": [],
        "applied_edits": list(APPLIED_EDITS),
        "new_parameters": dict(NEW_PARAMETERS),
        "edit_rationale": EDIT_RATIONALE,
        "unchanged_guarantees": list(UNCHANGED_GUARANTEES),
        "forbidden": list(FORBIDDEN),
        "edited_asset": None, "edited_asset_verdict": None,
        "edits_drawn_from_review_recommendations": True,
        "redetection_not_run_here": True,
        "redetection_requires_separate_human_approval": True,
        "previous_labels_kept_on_record": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False,
        "modifies_locked_instructions": False,
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
    strategy = build_ny_fvg_choch_strategy_spec()
    if (not validate_ny_fvg_choch_strategy_spec(strategy).get("valid")
            or strategy.get("verdict") != VERDICT_FS_READY):
        record["verdict"] = VERDICT_ME_BLOCKED
        record["blockers"].append("strategy_spec_not_ready")
        return record
    recommended = set(RECOMMENDED_MUTABLE_CANDIDATE_EDITS)
    if not set(APPLIED_EDITS) <= recommended:
        record["verdict"] = VERDICT_ME_BLOCKED
        record["blockers"].append("edit_not_in_review_recommendations")
        return record
    edited = build_edited_candidate_asset()
    asset_check = validate_candidate_asset(edited)
    record["edited_asset_verdict"] = asset_check.get("verdict")
    if asset_check.get("verdict") != VERDICT_ASSET_ACCEPTED:
        record["verdict"] = VERDICT_ME_BLOCKED
        record["blockers"].append("edited_asset_rejected_by_asset_spec")
        record["blockers"].extend(asset_check.get("errors") or [])
        return record
    record["edited_asset"] = edited
    record["verdict"] = VERDICT_ME_READY
    return record


def validate_mutable_candidate_edit_v1(record: Any) -> dict[str, Any]:
    """Validate the edit record's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_ME_READY, VERDICT_ME_BLOCKED):
        errors.append("bad_verdict")
    if r.get("edit_id") != EDIT_ID:
        errors.append("edit_id_tampered")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(r.get("applied_edits") or ()) != APPLIED_EDITS:
        errors.append("applied_edits_tampered")
    if r.get("new_parameters") != NEW_PARAMETERS:
        errors.append("new_parameters_tampered")
    if tuple(r.get("unchanged_guarantees") or ()) != UNCHANGED_GUARANTEES:
        errors.append("unchanged_guarantees_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if r.get("verdict") == VERDICT_ME_READY:
        if r.get("blockers"):
            errors.append("ready_with_blockers")
        if r.get("edited_asset_verdict") != VERDICT_ASSET_ACCEPTED:
            errors.append("ready_without_accepted_asset")
        edited = r.get("edited_asset") or {}
        parameters = (edited.get("fields") or {}).get("parameters") or {}
        for key, value in NEW_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("edited_parameter_missing:" + key)
    for key, want in (
        ("edits_drawn_from_review_recommendations", True),
        ("redetection_not_run_here", True),
        ("redetection_requires_separate_human_approval", True),
        ("previous_labels_kept_on_record", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
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
