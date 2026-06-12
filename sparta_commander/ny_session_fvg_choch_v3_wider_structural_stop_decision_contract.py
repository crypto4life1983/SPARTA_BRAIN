"""SPARTA NY-Session FVG+CHOCH V3 WIDER STRUCTURAL STOP DECISION
(READ-ONLY, DECISION RECORD ONLY, RUNS NOTHING).

Records the HUMAN decision: after V2 rejected all 7 labels on cost
viability (widest risk unit 33.158 bps vs the 81 bps floor), proceed with
EXACTLY ONE V3 research experiment -- replace the 1m-FVG impulse-candle
stop with a stop beyond the CHOCH leg structural extreme. This changes the
candidate from tiny scalp geometry toward intraday structural geometry.
Everything else is preserved: V1 freshness controls, the V2 cost floor
(NEVER lowered to rescue the strategy), taker-cost assumptions (maker
execution NOT assumed), locked scorer, locked instructions. If V3 also
fails cost viability or fee-honest replay, the candidate is rejected and
kept on record. This contract runs nothing and edits nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    NEW_PARAMETERS as V1_CONTROLS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    V2_NEW_PARAMETERS,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract import (
    ARTIFACT_PATH as V2_ARTIFACT_PATH,
    EXPECTED_ARTIFACT_SHA256 as V2_ARTIFACT_SHA256,
    VERDICT_V2R_REJECTED_ALL,
    build_v2_result_review,
)

V3D_SCHEMA_VERSION = (
    "ny_session_fvg_choch_v3_wider_structural_stop_decision.v1")
V3D_LABEL = ("SPARTA NY-Session FVG+CHOCH V3 Wider Structural Stop Decision "
             "(READ-ONLY, DECISION RECORD ONLY, ONE EXPERIMENT)")
V3D_MODE = "RESEARCH_ONLY"
VERDICT_V3D_RECORDED = (
    "V3_DECISION_RECORDED_PROCEED_WITH_ONE_WIDER_STOP_EXPERIMENT")
VERDICT_V3D_REJECTED = "V3_DECISION_REJECTED"
VERDICT_V3D_BLOCKED = "V3_DECISION_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_V3_WIDER_STRUCTURAL_STOP_MUTABLE_CANDIDATE_EDIT")

V3_HYPOTHESIS = (
    "the exact V1/V2 1m-FVG impulse-candle stop geometry is too tight for "
    "27 bps taker execution (widest observed risk unit 33.158 bps vs the "
    "81 bps floor); a wider STRUCTURAL stop may create realistic risk "
    "units large enough to survive fees and slippage, at the cost of "
    "changing the strategy from tiny scalp geometry toward intraday "
    "structural trade geometry")

V3_PROPOSED_STOP_MODEL = (
    "replace_stop_outside_the_1m_fvg_impulse_candle_with_stop_beyond_the"
    "_choch_leg_structural_extreme",
    "long_setups_stop_below_the_choch_leg_low_structural_swing_low",
    "short_setups_stop_above_the_choch_leg_high_structural_swing_high",
    "entry_htf_context_freshness_choch_and_ltf_fvg_logic_stay_separate_and"
    "_auditable",
    "cost_viability_floor_applies_to_v3_setups_unchanged",
)

PRESERVED_V1_CONTROLS = dict(V1_CONTROLS)        # 24 / True / 2
PRESERVED_V2_COST_FILTER = dict(V2_NEW_PARAMETERS)  # 27 / 3 / 81 / flags

V3_CONSTRAINTS = (
    "exactly_one_v3_experiment_no_parameter_sweeps",
    "v3_may_change_stop_geometry_only",
    "maker_execution_is_not_assumed",
    "the_cost_floor_is_never_lowered_to_rescue_the_strategy",
    "locked_scorer_and_locked_instructions_remain_immutable",
    "v1_and_v2_controls_preserved_unless_explicitly_reviewed_later",
)

FAILURE_RULE = ("if V3 also fails cost viability or fee-honest replay, the "
                "candidate is rejected and kept on record")

FORBIDDEN = (
    "live_trading", "paper_trading", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "replay_scorer_or_optimizer_runs_in_this_block",
    "lowering_costs_to_rescue_the_strategy",
    "deleting_v2_evidence", "hiding_rejected_setups",
    "auto_promotion", "gate_unlocks",
)

REVIEW_CHECKLIST = (
    "v2_rejection_evidence_certified_before_v3_decision",
    "v2_artifact_sha_pinned_and_untampered",
    "decision_scope_is_exactly_one_experiment",
    "v3_changes_stop_geometry_only",
    "v1_controls_preserved",
    "v2_cost_filter_preserved_floor_not_lowered",
    "maker_execution_not_assumed",
    "locked_scorer_and_instructions_immutable",
    "failure_rule_recorded_rejection_kept_on_record",
    "nothing_runs_and_no_artifacts_touched",
)


def get_v3_decision_label() -> str:
    return V3D_LABEL


def observe_v3_preconditions(repo_root: Any,
                             tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY: the V2 evidence state this decision depends on."""
    root = _pathlib.Path(str(repo_root))
    artifact = root / V2_ARTIFACT_PATH
    return {
        "v2_review_verdict": build_v2_result_review(
            repo_root, tracked_paths=[]).get("verdict"),
        "v2_artifact_sha256": (_hashlib.sha256(
            artifact.read_bytes()).hexdigest()
            if artifact.is_file() else None),
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
    }


def certify_v3_decision(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the V3 decision record. Pure."""
    record: dict[str, Any] = {
        "schema_version": V3D_SCHEMA_VERSION, "label": V3D_LABEL,
        "mode": V3D_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "v3_hypothesis": V3_HYPOTHESIS,
        "v3_proposed_stop_model": list(V3_PROPOSED_STOP_MODEL),
        "preserved_v1_controls": dict(PRESERVED_V1_CONTROLS),
        "preserved_v2_cost_filter": dict(PRESERVED_V2_COST_FILTER),
        "v3_constraints": list(V3_CONSTRAINTS),
        "failure_rule": FAILURE_RULE,
        "allowed_next_step": NEXT_REQUIRED_ACTION,
        "forbidden": list(FORBIDDEN),
        "rejection_not_marked_final": True,
        "maker_execution_assumed": False,
        "cost_floor_lowered": False,
        "decision_is_one_experiment_only": True,
        "this_decision_changes_no_rules_yet": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False,
        "modifies_locked_instructions": False,
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
        record["verdict"] = VERDICT_V3D_BLOCKED
        record["blockers"].append("observation_missing")
        return record
    o = observation
    if o.get("v2_artifact_sha256") is None:
        record["verdict"] = VERDICT_V3D_BLOCKED
        record["blockers"].append("v2_evidence_missing")
        return record

    r: dict[str, bool] = {}
    r["v2_rejection_evidence_certified_before_v3_decision"] = (
        o.get("v2_review_verdict") == VERDICT_V2R_REJECTED_ALL)
    r["v2_artifact_sha_pinned_and_untampered"] = (
        o.get("v2_artifact_sha256") == V2_ARTIFACT_SHA256)
    r["decision_scope_is_exactly_one_experiment"] = (
        "exactly_one_v3_experiment_no_parameter_sweeps" in V3_CONSTRAINTS)
    r["v3_changes_stop_geometry_only"] = (
        "v3_may_change_stop_geometry_only" in V3_CONSTRAINTS
        and not any("scorer" in rule or "cost_floor" in rule
                    and "unchanged" not in rule
                    for rule in V3_PROPOSED_STOP_MODEL))
    r["v1_controls_preserved"] = (
        PRESERVED_V1_CONTROLS == {"max_fvg_age_bars": 24,
                                  "require_fresh_unmitigated_15m_fvg": True,
                                  "max_zone_touches_before_invalidation": 2})
    r["v2_cost_filter_preserved_floor_not_lowered"] = (
        PRESERVED_V2_COST_FILTER.get("round_trip_cost_bps") == 27
        and PRESERVED_V2_COST_FILTER.get(
            "minimum_risk_to_round_trip_cost_multiple") == 3
        and PRESERVED_V2_COST_FILTER.get("minimum_risk_distance_bps") == 81
        and PRESERVED_V2_COST_FILTER.get(
            "reject_cost_dominated_setups") is True)
    r["maker_execution_not_assumed"] = (
        "maker_execution_is_not_assumed" in V3_CONSTRAINTS)
    r["locked_scorer_and_instructions_immutable"] = (
        "locked_scorer_and_locked_instructions_remain_immutable"
        in V3_CONSTRAINTS)
    r["failure_rule_recorded_rejection_kept_on_record"] = (
        "rejected and kept on record" in FAILURE_RULE)
    r["nothing_runs_and_no_artifacts_touched"] = not o.get(
        "tracked_output_paths")
    record["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        record["verdict"] = VERDICT_V3D_REJECTED
        record["blockers"].extend("check_failed:" + n for n in failed)
        return record
    record["verdict"] = VERDICT_V3D_RECORDED
    return record


def build_v3_decision(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the V2 evidence read-only and certify the V3 decision."""
    return certify_v3_decision(
        observe_v3_preconditions(repo_root, tracked_paths))


def validate_v3_decision(record: Any) -> dict[str, Any]:
    """Validate the decision record's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    v = record
    if v.get("verdict") not in (VERDICT_V3D_RECORDED, VERDICT_V3D_REJECTED,
                                VERDICT_V3D_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if v.get("v3_hypothesis") != V3_HYPOTHESIS:
        errors.append("hypothesis_tampered")
    if tuple(v.get("v3_proposed_stop_model") or ()) != V3_PROPOSED_STOP_MODEL:
        errors.append("stop_model_tampered")
    if v.get("preserved_v1_controls") != PRESERVED_V1_CONTROLS:
        errors.append("v1_controls_tampered")
    if v.get("preserved_v2_cost_filter") != PRESERVED_V2_COST_FILTER:
        errors.append("v2_cost_filter_tampered")
    if tuple(v.get("v3_constraints") or ()) != V3_CONSTRAINTS:
        errors.append("constraints_tampered")
    if v.get("failure_rule") != FAILURE_RULE:
        errors.append("failure_rule_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("maker_execution_assumed") is not False:
        errors.append("maker_execution_must_never_be_assumed")
    if v.get("cost_floor_lowered") is not False:
        errors.append("cost_floor_must_never_be_lowered")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_V3D_RECORDED:
        if v.get("blockers"):
            errors.append("recorded_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("recorded_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_V3D_REJECTED, VERDICT_V3D_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_recorded_without_blockers")
    for key, want in (
        ("rejection_not_marked_final", True),
        ("decision_is_one_experiment_only", True),
        ("this_decision_changes_no_rules_yet", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
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
