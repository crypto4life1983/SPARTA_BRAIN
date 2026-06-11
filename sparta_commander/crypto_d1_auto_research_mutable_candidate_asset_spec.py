"""SPARTA Crypto-D1 Auto Research - MUTABLE CANDIDATE ASSET SPEC (READ-ONLY).

The ONE future-editable object in the auto-research lane: a controlled schema
the optimizer may propose research changes inside -- and nothing else. Locked
instructions, the locked scorer, live config, brokers, credentials, and
execution code are all outside this schema and outside the optimizer's reach.
Spec only: no detector, replay, runner, or optimizer execution exists yet.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
    VERDICT_OPT_CONTRACT_READY,
    build_optimizer_contract,
    validate_optimizer_contract,
)

CA_SCHEMA_VERSION = "crypto_d1_auto_research_mutable_candidate_asset_spec.v1"
CA_LABEL = ("SPARTA Crypto-D1 Auto Research Mutable Candidate Asset Spec "
            "(READ-ONLY, SPEC ONLY)")
CA_MODE = "RESEARCH_ONLY"
VERDICT_CA_SPEC_READY = "MUTABLE_CANDIDATE_ASSET_SPEC_READY"
VERDICT_CA_SPEC_BLOCKED = "MUTABLE_CANDIDATE_ASSET_SPEC_BLOCKED"
VERDICT_ASSET_ACCEPTED = "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH"
VERDICT_ASSET_REJECTED = "CANDIDATE_ASSET_REJECTED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_NEXT_AUTO_RESEARCH_BLOCK"

# The CLOSED set of editable fields. Anything else in an asset rejects it.
ALLOWED_EDITABLE_FIELDS = (
    "candidate_id", "candidate_family", "hypothesis", "market_scope",
    "symbol_scope", "timeframe_scope", "session_filter", "entry_rules_text",
    "exit_rules_text", "risk_rules_text", "parameters", "constraints",
    "rationale", "lineage", "status", "audit_notes",
)
ALLOWED_STATUS = ("draft", "proposed", "rejected_kept_on_record",
                  "accepted_awaiting_human_review")

# Any field NAME containing one of these tokens rejects the whole asset.
FORBIDDEN_FIELD_TOKENS = (
    "wallet", "account", "login", "session_id", "cookie", "api_key", "apikey",
    "secret", "credential", "broker", "exchange_endpoint", "order",
    "position_size_live", "live_config", "scorer", "instructions_override",
    "auto_promote", "delete_rejected", "unlock",
)

REQUIRED_ASSET_FLAGS = {
    "research_only": True,
    "live_trading_authorized": False,
    "paper_trading_authorized": False,
    "human_review_required": True,
}

SPEC_RULES = (
    "optimizer_may_edit_only_the_allowed_editable_fields",
    "locked_instructions_may_never_be_edited",
    "locked_scorer_may_never_be_edited",
    "rejected_candidates_are_kept_on_record_never_deleted",
    "no_field_may_authorize_paper_micro_live_or_live",
    "future_detector_replay_optimizer_blocks_need_separate_human_approval",
)


def get_mutable_candidate_asset_spec_label() -> str:
    return CA_LABEL


def validate_candidate_asset(asset: Any) -> dict[str, Any]:
    """Validate ONE proposed candidate asset against the closed schema.
    Pure; never raises. Acceptance promotes nothing."""
    result: dict[str, Any] = {
        "verdict": None, "errors": [],
        "acceptance_promotes_nothing": True,
        "human_review_required": True,
    }
    if not isinstance(asset, dict):
        result["verdict"] = VERDICT_ASSET_REJECTED
        result["errors"].append("asset_not_a_dict")
        return result
    errors = result["errors"]

    fields = asset.get("fields")
    if not isinstance(fields, dict) or not fields:
        errors.append("fields_missing_or_empty")
    else:
        for name in fields:
            lowered = str(name).strip().lower()
            for token in FORBIDDEN_FIELD_TOKENS:
                if token in lowered:
                    errors.append("forbidden_field:" + str(name)
                                  + " (token: " + token + ")")
                    break
            else:
                if lowered not in ALLOWED_EDITABLE_FIELDS:
                    errors.append("field_outside_closed_schema:" + str(name))
        if "candidate_id" not in fields or not fields.get("candidate_id"):
            errors.append("candidate_id_required")
        status = fields.get("status")
        if status is not None and status not in ALLOWED_STATUS:
            errors.append("status_outside_closed_set:" + str(status))

    for flag, want in REQUIRED_ASSET_FLAGS.items():
        if asset.get(flag) is not want:
            errors.append("required_flag_wrong:" + flag)
    if asset.get("locked_instructions_may_edit") is not False:
        errors.append("asset_claims_instruction_edit_rights")
    if asset.get("locked_scorer_may_edit") is not False:
        errors.append("asset_claims_scorer_edit_rights")
    if asset.get("optimizer_may_edit") is not True:
        errors.append("optimizer_edit_scope_flag_missing")

    result["verdict"] = (VERDICT_ASSET_REJECTED if errors
                         else VERDICT_ASSET_ACCEPTED)
    return result


def record_mutable_candidate_asset_spec(optimizer_contract: Any) -> dict[str, Any]:
    """Record the spec, gated on a READY, valid optimizer contract."""
    spec: dict[str, Any] = {
        "schema_version": CA_SCHEMA_VERSION, "label": CA_LABEL, "mode": CA_MODE,
        "lane": "crypto_d1_auto_research", "verdict": None, "blockers": [],
        "optimizer_contract_verdict": None,
        "allowed_editable_fields": list(ALLOWED_EDITABLE_FIELDS),
        "allowed_status": list(ALLOWED_STATUS),
        "forbidden_field_tokens": list(FORBIDDEN_FIELD_TOKENS),
        "required_asset_flags": dict(REQUIRED_ASSET_FLAGS),
        "spec_rules": list(SPEC_RULES),
        "optimizer_may_edit_candidate_asset_only": True,
        "locked_instructions_may_edit": False,
        "locked_scorer_may_edit": False,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_scanner": False, "fetches_data": False, "calls_api": False,
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
    if not isinstance(optimizer_contract, dict):
        spec["verdict"] = VERDICT_CA_SPEC_BLOCKED
        spec["blockers"].append("optimizer_contract_missing")
        return spec
    if not validate_optimizer_contract(optimizer_contract).get("valid"):
        spec["verdict"] = VERDICT_CA_SPEC_BLOCKED
        spec["blockers"].append("optimizer_contract_invalid")
        return spec
    if optimizer_contract.get("verdict") != VERDICT_OPT_CONTRACT_READY:
        spec["verdict"] = VERDICT_CA_SPEC_BLOCKED
        spec["blockers"].append("optimizer_contract_not_ready")
        return spec
    spec["verdict"] = VERDICT_CA_SPEC_READY
    spec["optimizer_contract_verdict"] = optimizer_contract.get("verdict")
    return spec


def build_mutable_candidate_asset_spec() -> dict[str, Any]:
    """Build against the real optimizer contract. Pure."""
    return record_mutable_candidate_asset_spec(build_optimizer_contract())


def validate_mutable_candidate_asset_spec(spec: Any) -> dict[str, Any]:
    """Validate the spec's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    verdict = s.get("verdict")
    if verdict not in (VERDICT_CA_SPEC_READY, VERDICT_CA_SPEC_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_CA_SPEC_BLOCKED and not s.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_CA_SPEC_READY:
        if s.get("blockers"):
            errors.append("ready_with_blockers")
        if s.get("optimizer_contract_verdict") != VERDICT_OPT_CONTRACT_READY:
            errors.append("ready_without_ready_optimizer_contract")
    if s.get("lane") != "crypto_d1_auto_research":
        errors.append("wrong_lane")
    if tuple(s.get("allowed_editable_fields") or ()) != ALLOWED_EDITABLE_FIELDS:
        errors.append("editable_fields_tampered")
    if tuple(s.get("allowed_status") or ()) != ALLOWED_STATUS:
        errors.append("status_set_tampered")
    if tuple(s.get("forbidden_field_tokens") or ()) != FORBIDDEN_FIELD_TOKENS:
        errors.append("forbidden_tokens_weakened")
    if s.get("required_asset_flags") != REQUIRED_ASSET_FLAGS:
        errors.append("required_flags_tampered")
    if tuple(s.get("spec_rules") or ()) != SPEC_RULES:
        errors.append("spec_rules_tampered")
    for key, want in (
        ("optimizer_may_edit_candidate_asset_only", True),
        ("locked_instructions_may_edit", False),
        ("locked_scorer_may_edit", False),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if s.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "fetches_data", "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
