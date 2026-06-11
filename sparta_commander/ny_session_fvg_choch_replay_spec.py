"""SPARTA NY-Session FVG+CHOCH REPLAY Spec (READ-ONLY, SPEC ONLY).

How future approved replay code will evaluate detector-labeled setups from
provided historical candles -- net-after-costs only, locked-scorer discipline,
no trading, no fetching, no promoting. The executable replay runner is NOT
built in this block: even a perfectly well-formed replay request honestly
returns REPLAY_BLOCKED_REPLAY_RUNNER_NOT_BUILT.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_detector_spec import (
    CANDIDATE_ID,
    VERDICT_DET_READY,
    build_ny_fvg_choch_detector_spec,
    validate_ny_fvg_choch_detector_spec,
)

RP_SCHEMA_VERSION = "ny_session_fvg_choch_replay_spec.v1"
RP_LABEL = ("SPARTA NY-Session FVG+CHOCH Replay Spec "
            "(READ-ONLY, SPEC ONLY, RUNNER NOT BUILT)")
RP_MODE = "RESEARCH_ONLY"
VERDICT_RP_READY = "NY_FVG_CHOCH_REPLAY_SPEC_READY"
VERDICT_RP_BLOCKED = "NY_FVG_CHOCH_REPLAY_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_FVG_CHOCH_REPLAY_RUNNER"

REPLAY_STATUSES = (
    "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW",
    "REPLAY_REJECTED_NO_ENTRY",
    "REPLAY_REJECTED_STOP_BEFORE_ENTRY",
    "REPLAY_REJECTED_INVALID_LABEL",
    "REPLAY_REJECTED_MISSING_CANDLES",
    "REPLAY_REJECTED_COSTS_UNDEFINED",
    "REPLAY_REJECTED_FORBIDDEN_CAPABILITY",
    "REPLAY_BLOCKED_REPLAY_RUNNER_NOT_BUILT",
)

REPLAY_INPUT_FIELDS = (
    "detector_label", "candles_provided", "candidate_id", "symbol",
    "session_date", "direction", "session_window", "proposed_entry_price",
    "proposed_stop_price", "proposed_target_4r_price",
    "breakeven_structure_trigger_reference", "invalidation_reason",
    "fees_bps", "spread_bps", "slippage_bps", "replay_start_time",
    "replay_end_time",
)

REPLAY_OUTPUT_FIELDS = (
    "setup_id", "candidate_id", "symbol", "session_date", "direction",
    "entry_triggered", "entry_time", "entry_price", "stop_price",
    "target_4r_price", "breakeven_triggered", "breakeven_time", "exit_reason",
    "exit_time", "exit_price", "gross_r", "net_r_after_costs",
    "gross_pnl_model", "net_pnl_model_after_costs",
    "max_adverse_excursion_r", "max_favorable_excursion_r", "replay_status",
    "rejection_reason", "audit_notes",
)

REPLAY_RULES = (
    "inputs_come_only_from_accepted_detector_labels",
    "candles_come_only_from_a_future_approved_upstream_source",
    "fees_spread_and_slippage_must_be_defined_before_any_scorer_review",
    "no_gross_only_pass_claims_net_after_costs_is_mandatory",
    "rejected_detector_labels_can_never_replay_as_accepted_setups",
    "all_rejected_replays_remain_auditable_never_hidden",
    "the_locked_scorer_reviews_outputs_under_its_own_separate_approval",
    "the_executable_replay_runner_requires_its_own_separate_human_approval",
)

FORBIDDEN = (
    "live_trading", "paper_trading_authorization", "order_placement",
    "broker_or_exchange_api_calls", "credential_access",
    "wallet_account_login_fields", "network_calls", "data_fetching",
    "modifying_locked_scorer", "modifying_locked_instructions",
    "auto_promotion", "unlocking_gates", "hiding_rejected_replays",
    "creating_report_artifacts_in_this_block",
)

_FORBIDDEN_KEY_TOKENS = ("order", "api_key", "credential", "wallet",
                         "account", "login", "fetch_url", "live_authorized",
                         "paper_authorized", "scorer_patch")
_COST_FIELDS = ("fees_bps", "spread_bps", "slippage_bps")


def get_ny_fvg_choch_replay_spec_label() -> str:
    return RP_LABEL


def validate_replay_request(label: Any, request: Any) -> dict[str, Any]:
    """DETERMINISTIC request gate for the FUTURE runner. Pure; runs nothing.
    Even a fully valid request returns RUNNER_NOT_BUILT in this block."""
    result: dict[str, Any] = {"status": None, "errors": [],
                              "request_authorizes_nothing": True}
    if not isinstance(label, dict) or label.get(
            "detector_status") != "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
        result["status"] = "REPLAY_REJECTED_INVALID_LABEL"
        result["errors"].append("detector_label_missing_or_not_accepted")
        return result
    if not isinstance(request, dict):
        result["status"] = "REPLAY_REJECTED_INVALID_LABEL"
        result["errors"].append("request_not_a_dict")
        return result
    for key in request:
        lowered = str(key).lower()
        for token in _FORBIDDEN_KEY_TOKENS:
            if token in lowered:
                result["status"] = "REPLAY_REJECTED_FORBIDDEN_CAPABILITY"
                result["errors"].append("forbidden_field:" + str(key))
                return result
    if request.get("candles_provided") is not True:
        result["status"] = "REPLAY_REJECTED_MISSING_CANDLES"
        result["errors"].append("candles_not_provided_by_approved_source")
        return result
    for cost in _COST_FIELDS:
        raw = request.get(cost)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool) or raw < 0:
            result["status"] = "REPLAY_REJECTED_COSTS_UNDEFINED"
            result["errors"].append("cost_missing_or_invalid:" + cost)
            return result
    # Well-formed -- but the runner does not exist in this block. Honest stop.
    result["status"] = "REPLAY_BLOCKED_REPLAY_RUNNER_NOT_BUILT"
    return result


def validate_replay_output_record(record: Any) -> dict[str, Any]:
    """Validate ONE future replay OUTPUT record against the frozen schema.
    Net-after-costs is mandatory; gross-only pass claims are impossible."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"acceptable": False, "errors": ["record_not_a_dict"]}
    for field in REPLAY_OUTPUT_FIELDS:
        if field not in record:
            errors.append("missing_output_field:" + field)
    if errors:
        return {"acceptable": False, "errors": errors}
    if record.get("replay_status") not in REPLAY_STATUSES:
        errors.append("replay_status_outside_closed_set")
    if record.get("candidate_id") != CANDIDATE_ID:
        errors.append("wrong_candidate_id")
    if record.get("replay_status") == "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW":
        net = record.get("net_r_after_costs")
        if not isinstance(net, (int, float)) or isinstance(net, bool):
            errors.append("net_after_costs_mandatory_for_scorer_review")
        npm = record.get("net_pnl_model_after_costs")
        if not isinstance(npm, (int, float)) or isinstance(npm, bool):
            errors.append("net_pnl_after_costs_mandatory")
        if record.get("gross_only_pass_claim") is True:
            errors.append("gross_only_pass_claims_impossible")
    return {"acceptable": not errors, "errors": errors}


def build_ny_fvg_choch_replay_spec() -> dict[str, Any]:
    """Assemble the replay spec, gated on the READY detector spec. Pure."""
    spec: dict[str, Any] = {
        "schema_version": RP_SCHEMA_VERSION, "label": RP_LABEL, "mode": RP_MODE,
        "lane": "crypto_d1_auto_research", "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "replay_statuses": list(REPLAY_STATUSES),
        "replay_input_fields": list(REPLAY_INPUT_FIELDS),
        "replay_output_fields": list(REPLAY_OUTPUT_FIELDS),
        "replay_rules": list(REPLAY_RULES),
        "forbidden": list(FORBIDDEN),
        "replay_runner_built": False,
        "net_after_costs_mandatory": True,
        "rejected_replays_auditable": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False, "modifies_locked_instructions": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_scanner": False, "runs_replay_now": False, "scores_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
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
    detector = build_ny_fvg_choch_detector_spec()
    if (not validate_ny_fvg_choch_detector_spec(detector).get("valid")
            or detector.get("verdict") != VERDICT_DET_READY):
        spec["verdict"] = VERDICT_RP_BLOCKED
        spec["blockers"].append("detector_spec_not_ready")
        return spec
    spec["verdict"] = VERDICT_RP_READY
    return spec


def validate_ny_fvg_choch_replay_spec(spec: Any) -> dict[str, Any]:
    """Validate the replay spec's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") not in (VERDICT_RP_READY, VERDICT_RP_BLOCKED):
        errors.append("bad_verdict")
    if s.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(s.get("replay_statuses") or ()) != REPLAY_STATUSES:
        errors.append("status_set_tampered")
    if tuple(s.get("replay_input_fields") or ()) != REPLAY_INPUT_FIELDS:
        errors.append("input_fields_tampered")
    if tuple(s.get("replay_output_fields") or ()) != REPLAY_OUTPUT_FIELDS:
        errors.append("output_fields_tampered")
    if tuple(s.get("replay_rules") or ()) != REPLAY_RULES:
        errors.append("replay_rules_tampered")
    if tuple(s.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (
        ("replay_runner_built", False),
        ("net_after_costs_mandatory", True),
        ("rejected_replays_auditable", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if s.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "runs_replay_now", "scores_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
