"""SPARTA NY-Session FVG+CHOCH MUTABLE CANDIDATE EDIT V2 - COST VIABILITY
FILTER (READ-ONLY, RESEARCH ONLY, AUTHORIZES NOTHING).

The human-approved response to the frozen fee-honest replay evidence
(NET -21.040902R at 27 bps round-trip; ETHUSD 2026-05-13 hit its full 4R
target and still lost net): a hard cost-viability filter added to the ONE
editable object -- the mutable candidate asset. A setup is REJECTED when its
entry-to-stop distance is below 3x the round-trip cost (81 bps). The 2x
(54 bps) and 4x (108 bps) variants are NOTED for future research only and
are NOT active. Everything else -- V1 freshness controls, 15m FVG logic,
CHOCH, 1m LTF FVG, fib 0.618 +/-5%, 4R, label schema, locked scorer, locked
instructions -- is unchanged. Re-detection under V2 requires its own
separate human approval; nothing runs here.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_ASSET_ACCEPTED,
    validate_candidate_asset,
)
from sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract import (
    EXPECTED_ROUND_TRIP_COST_BPS,
    EXPECTED_TOTAL_NET_R,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    NEW_PARAMETERS as V1_PARAMETERS,
    VERDICT_ME_READY as VERDICT_V1_READY,
    build_edited_candidate_asset as build_v1_edited_asset,
    build_mutable_candidate_edit_v1,
    validate_mutable_candidate_edit_v1,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
    FIB_LEVEL,
    FIB_TOLERANCE,
    RISK_REWARD_TARGET,
)

M2_SCHEMA_VERSION = (
    "ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability.v1")
M2_LABEL = ("SPARTA NY-Session FVG+CHOCH Mutable Candidate Edit V2 - Cost "
            "Viability Filter (READ-ONLY, RESEARCH ONLY, EDITS THE "
            "CANDIDATE ASSET ONLY)")
M2_MODE = "RESEARCH_ONLY"
EDIT_V2_ID = (
    "NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_COST_VIABILITY_FILTER")
VERDICT_M2_READY = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_READY"
VERDICT_M2_BLOCKED = "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_REDETECTION_WITH_COST_VIABILITY_EDIT_V2")

ROUND_TRIP_COST_BPS = 27
MINIMUM_RISK_TO_ROUND_TRIP_COST_MULTIPLE = 3
MINIMUM_RISK_DISTANCE_BPS = 81  # 27 x 3

V2_NEW_PARAMETERS = {
    "reject_cost_dominated_setups": True,
    "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
    "minimum_risk_to_round_trip_cost_multiple":
        MINIMUM_RISK_TO_ROUND_TRIP_COST_MULTIPLE,
    "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,
    "require_entry_to_stop_distance_bps_gte_minimum": True,
}

# Noted for FUTURE research only; NOT active in V2.
FUTURE_RESEARCH_VARIANTS_NOTED_ONLY = {
    "softer_2x_round_trip": 54,
    "harder_4x_round_trip": 108,
}

COST_VIABILITY_RULE = (
    "reject any setup where entry_to_stop_distance_bps < "
    "round_trip_cost_bps x minimum_risk_to_round_trip_cost_multiple "
    "(27 x 3 = 81 bps); research filter only, never an instruction")

EDIT_RATIONALE = (
    "fee-honest replay of the 7 accepted V1 labels was NET -21.040902R at "
    "27 bps round-trip costs: the 1m FVG stop distances (roughly 2.6 to 33 "
    "bps implied) were so tight that costs reached 5-10R, so even the "
    "ETHUSD 2026-05-13 full 4R target hit lost net; V2 rejects "
    "cost-dominated setups before they can ever reach replay")

UNCHANGED_GUARANTEES = (
    "v1_freshness_controls_unchanged_24_true_2",
    "15m_fvg_logic_unchanged",
    "choch_rule_unchanged",
    "1m_ltf_fvg_rule_unchanged",
    "fib_0618_plus_minus_5pct_unchanged",
    "4r_target_definition_unchanged",
    "detector_label_schema_unchanged_29_fields",
    "locked_scorer_unchanged",
    "locked_instructions_unchanged",
    "staged_candles_and_prior_labels_unchanged",
)

FORBIDDEN = (
    "editing_locked_instructions", "editing_locked_scorer",
    "editing_detector_rules", "editing_detector_label_schema",
    "adding_replay_pnl_or_scoring_fields", "automatic_redetection",
    "replay_runs", "optimizer_runs",
    "paper_live_micro_live_authorization",
    "broker_exchange_credential_access", "order_endpoints",
    "staged_candle_or_prior_label_mutation", "gate_unlocks",
)


def get_mutable_candidate_edit_v2_label() -> str:
    return M2_LABEL


def evaluate_setup_cost_viability(entry_price: Any,
                                  stop_price: Any) -> dict[str, Any]:
    """THE V2 FILTER, pure: a setup is viable only when its entry-to-stop
    distance is at least 81 bps of entry. Research gate, never an
    instruction."""
    result: dict[str, Any] = {
        "viable": False, "entry_to_stop_distance_bps": None,
        "minimum_required_bps": MINIMUM_RISK_DISTANCE_BPS,
        "rule": COST_VIABILITY_RULE, "reason": None,
        "viability_authorizes_nothing": True,
    }
    for value in (entry_price, stop_price):
        if not isinstance(value, (int, float)) or isinstance(value, bool) \
                or value <= 0:
            result["reason"] = "prices_missing_or_invalid"
            return result
    distance_bps = abs(float(entry_price) - float(stop_price)) \
        / float(entry_price) * 10000.0
    result["entry_to_stop_distance_bps"] = round(distance_bps, 6)
    if distance_bps < MINIMUM_RISK_DISTANCE_BPS:
        result["reason"] = ("cost_dominated_setup_rejected:"
                            "distance_below_81_bps")
        return result
    result["viable"] = True
    result["reason"] = "risk_distance_meets_3x_round_trip_cost_minimum"
    return result


def implied_risk_distance_bps(gross_r: Any, net_r: Any) -> float | None:
    """Back out the V1 replay's implied entry-to-stop distance in bps from
    its gross/net R figures (cost_R = 27bps x entry/risk). Pure."""
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool)
               for x in (gross_r, net_r)) or gross_r <= net_r:
        return None
    return round(ROUND_TRIP_COST_BPS / (float(gross_r) - float(net_r)), 6)


def build_edited_candidate_asset_v2() -> dict[str, Any]:
    """The V2-edited candidate asset: the V1-edited instance plus the cost
    viability parameters. Deep-copied; V1 output never mutated. Pure."""
    base = build_v1_edited_asset()
    fields = dict(base["fields"])
    parameters = dict(fields["parameters"])
    parameters.update(V2_NEW_PARAMETERS)
    fields["parameters"] = parameters
    fields["constraints"] = (str(fields["constraints"])
                             + "; cost viability v2: " + COST_VIABILITY_RULE)
    fields["lineage"] = (str(fields["lineage"])
                         + ">edit_v2_cost_viability_per_fee_honest_replay"
                           "_review_2026-06-11")
    fields["status"] = "proposed"
    fields["audit_notes"] = ("mutable candidate edit v2 applied per the "
                             "fee-honest replay results review; 2x/4x "
                             "variants noted for future research only; "
                             "re-detection requires separate human approval")
    fields["rationale"] = EDIT_RATIONALE
    edited = dict(base)
    edited["fields"] = fields
    return edited


def build_mutable_candidate_edit_v2() -> dict[str, Any]:
    """Assemble the V2 edit record: gated on the READY V1 edit, the frozen
    replay evidence constants, and the V2 asset passing the pushed
    mutable-asset schema. Pure."""
    record: dict[str, Any] = {
        "schema_version": M2_SCHEMA_VERSION, "label": M2_LABEL,
        "mode": M2_MODE, "lane": "crypto_d1_auto_research",
        "edit_id": EDIT_V2_ID, "candidate_id": CANDIDATE_ID,
        "verdict": None, "blockers": [],
        "based_on_replay_evidence": {
            "net_r_after_costs": EXPECTED_TOTAL_NET_R,
            "round_trip_cost_bps": EXPECTED_ROUND_TRIP_COST_BPS,
            "labels_replayed": 7},
        "v2_new_parameters": dict(V2_NEW_PARAMETERS),
        "cost_viability_rule": COST_VIABILITY_RULE,
        "future_research_variants_noted_only": dict(
            FUTURE_RESEARCH_VARIANTS_NOTED_ONLY),
        "edit_rationale": EDIT_RATIONALE,
        "unchanged_guarantees": list(UNCHANGED_GUARANTEES),
        "forbidden": list(FORBIDDEN),
        "edited_asset": None, "edited_asset_verdict": None,
        "redetection_not_run_here": True,
        "redetection_requires_separate_human_approval": True,
        "replay_requires_separate_human_approval": True,
        "previous_labels_kept_on_record": True,
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
    if MINIMUM_RISK_DISTANCE_BPS != (
            ROUND_TRIP_COST_BPS * MINIMUM_RISK_TO_ROUND_TRIP_COST_MULTIPLE):
        record["verdict"] = VERDICT_M2_BLOCKED
        record["blockers"].append("minimum_distance_arithmetic_inconsistent")
        return record
    v1 = build_mutable_candidate_edit_v1()
    if (v1.get("verdict") != VERDICT_V1_READY
            or not validate_mutable_candidate_edit_v1(v1).get("valid")):
        record["verdict"] = VERDICT_M2_BLOCKED
        record["blockers"].append("edit_v1_not_ready")
        return record
    edited = build_edited_candidate_asset_v2()
    asset_check = validate_candidate_asset(edited)
    record["edited_asset_verdict"] = asset_check.get("verdict")
    if asset_check.get("verdict") != VERDICT_ASSET_ACCEPTED:
        record["verdict"] = VERDICT_M2_BLOCKED
        record["blockers"].append("edited_asset_rejected_by_asset_spec")
        record["blockers"].extend(asset_check.get("errors") or [])
        return record
    record["edited_asset"] = edited
    record["verdict"] = VERDICT_M2_READY
    return record


def validate_mutable_candidate_edit_v2(record: Any) -> dict[str, Any]:
    """Validate the V2 edit record's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_M2_READY, VERDICT_M2_BLOCKED):
        errors.append("bad_verdict")
    if r.get("edit_id") != EDIT_V2_ID:
        errors.append("edit_id_tampered")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("v2_new_parameters") != V2_NEW_PARAMETERS:
        errors.append("v2_parameters_tampered")
    if r.get("cost_viability_rule") != COST_VIABILITY_RULE:
        errors.append("cost_viability_rule_tampered")
    if r.get("future_research_variants_noted_only") != (
            FUTURE_RESEARCH_VARIANTS_NOTED_ONLY):
        errors.append("future_variants_tampered")
    if tuple(r.get("unchanged_guarantees") or ()) != UNCHANGED_GUARANTEES:
        errors.append("unchanged_guarantees_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if (r.get("based_on_replay_evidence") or {}).get(
            "net_r_after_costs") != EXPECTED_TOTAL_NET_R:
        errors.append("replay_evidence_basis_tampered")
    if r.get("verdict") == VERDICT_M2_READY:
        if r.get("blockers"):
            errors.append("ready_with_blockers")
        if r.get("edited_asset_verdict") != VERDICT_ASSET_ACCEPTED:
            errors.append("ready_without_accepted_asset")
        edited = r.get("edited_asset") or {}
        parameters = (edited.get("fields") or {}).get("parameters") or {}
        for key, value in V2_NEW_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("edited_parameter_missing:" + key)
        for key, value in V1_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("v1_parameter_lost:" + key)
        for noted in FUTURE_RESEARCH_VARIANTS_NOTED_ONLY.values():
            if noted in (parameters.get("minimum_risk_distance_bps"),):
                errors.append("future_variant_must_not_be_active")
    for key, want in (
        ("redetection_not_run_here", True),
        ("redetection_requires_separate_human_approval", True),
        ("replay_requires_separate_human_approval", True),
        ("previous_labels_kept_on_record", True),
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


# Keep the strategy constants imported for drift assertions in tests.
assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
assert RISK_REWARD_TARGET == 4.0
