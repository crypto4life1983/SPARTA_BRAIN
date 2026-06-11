"""SPARTA NY-Session FVG+CHOCH CANDLE SOURCE APPROVAL (READ-ONLY, RULES ONLY).

Which historical candle sources are ALLOWED for future 1m/15m staging --
strictly no-auth, no-login, no-credential, no-private-endpoint, historical
only. This contract approves source RULES; it fetches nothing, creates no
files, and every concrete source still needs a human signature. Actual
staging remains behind its own separate human approval.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
    VERDICT_SP_READY,
    build_real_candle_staging_plan,
    validate_real_candle_staging_plan,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

SA_SCHEMA_VERSION = "ny_session_fvg_choch_candle_source_approval.v1"
SA_LABEL = ("SPARTA NY-Session FVG+CHOCH Candle Source Approval "
            "(READ-ONLY, SOURCE RULES ONLY, FETCHES NOTHING)")
SA_MODE = "RESEARCH_ONLY"
VERDICT_SA_READY = "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_READY"
VERDICT_SA_BLOCKED = "NY_FVG_CHOCH_CANDLE_SOURCE_APPROVAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_REAL_CANDLE_STAGING"

ALLOWED_SOURCE_CATEGORIES = (
    "repo_local_approved_historical_files",
    "manually_supplied_human_approved_csv",
    "no_auth_public_historical_endpoint_human_approved",
    "approved_read_only_historical_provider_adapter_no_credentials",
)

SOURCE_REQUIREMENTS = (
    "public_or_already_approved_internal_historical_source_only",
    "no_login_no_api_key_no_secret_no_credential",
    "no_account_no_wallet_access",
    "no_private_endpoint_no_trading_endpoint",
    "no_live_market_polling_historical_only",
    "no_network_call_in_this_block",
    "source_provenance_recorded",
    "source_terms_and_limits_noted_if_applicable",
    "symbols_and_timeframes_match_staging_plan",
    "output_satisfies_staging_plan_schema",
    "actual_staging_requires_separate_human_approval",
)

FORBIDDEN = (
    "data_fetch_in_this_block", "file_creation_in_this_block",
    "api_key_usage", "credential_loading",
    "wallet_account_login_access", "private_endpoint_access",
    "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization",
    "detector_replay_scorer_runs", "optimizer_execution",
    "report_artifact_creation", "gate_unlocks",
)

PROPOSAL_REQUIRED_FIELDS = (
    "source_name", "category", "provenance", "terms_and_limits",
    "historical_only", "requires_login", "requires_api_key",
    "requires_credentials", "uses_private_endpoint", "is_live_polling",
    "symbols", "timeframes", "output_fields",
)

_FORBIDDEN_KEY_TOKENS = ("api_key", "secret", "credential", "login",
                         "wallet", "account", "password", "session_cookie",
                         "auth_token")
_FORBIDDEN_ENDPOINT_TOKENS = ("order", "trade", "position", "account",
                              "wallet", "private", "withdraw", "transfer",
                              "balance", "auth", "login", "key")


def get_candle_source_approval_label() -> str:
    return SA_LABEL


def validate_candle_source_proposal(proposal: Any) -> dict[str, Any]:
    """Pure rule check of ONE proposed source. Approvable here still means
    a human signature is required before the source may ever be used."""
    errors: list[str] = []
    if not isinstance(proposal, dict):
        return {"approvable": False, "errors": ["proposal_not_a_dict"],
                "human_signature_still_required": True}
    for field in PROPOSAL_REQUIRED_FIELDS:
        if field not in proposal:
            errors.append("missing_proposal_field:" + field)
    # declared honesty flags (requires_login etc.) are schema fields, not
    # credential payloads -- only EXTRA keys are scanned for leak tokens
    for key in proposal:
        if key in PROPOSAL_REQUIRED_FIELDS:
            continue
        lowered = str(key).lower()
        for token in _FORBIDDEN_KEY_TOKENS:
            if token in lowered:
                errors.append("forbidden_proposal_field:" + str(key))
    if errors:
        return {"approvable": False, "errors": errors,
                "human_signature_still_required": True}
    if proposal["category"] not in ALLOWED_SOURCE_CATEGORIES:
        errors.append("category_not_allowed:" + str(proposal["category"]))
    if not str(proposal["provenance"] or "").strip():
        errors.append("provenance_missing")
    if not str(proposal["terms_and_limits"] or "").strip():
        errors.append("terms_and_limits_missing")
    for flag in ("requires_login", "requires_api_key",
                 "requires_credentials", "uses_private_endpoint"):
        if proposal[flag] is not False:
            errors.append("forbidden_access_requirement:" + flag)
    if proposal["is_live_polling"] is not False:
        errors.append("live_polling_forbidden")
    if proposal["historical_only"] is not True:
        errors.append("source_not_historical_only")
    endpoint = str(proposal.get("endpoint_path") or "").lower()
    for token in _FORBIDDEN_ENDPOINT_TOKENS:
        if token in endpoint:
            errors.append("forbidden_endpoint_token:" + token)
    if tuple(proposal["symbols"] or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_mismatch_with_staging_plan")
    if tuple(proposal["timeframes"] or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_mismatch_with_staging_plan")
    if tuple(proposal["output_fields"] or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("schema_incompatible_with_staging_plan")
    return {"approvable": not errors, "errors": errors,
            "human_signature_still_required": True}


def build_candle_source_approval_contract() -> dict[str, Any]:
    """Assemble the source-approval contract, gated on the READY plan."""
    contract: dict[str, Any] = {
        "schema_version": SA_SCHEMA_VERSION, "label": SA_LABEL,
        "mode": SA_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "allowed_source_categories": list(ALLOWED_SOURCE_CATEGORIES),
        "source_requirements": list(SOURCE_REQUIREMENTS),
        "forbidden": list(FORBIDDEN),
        "required_symbols": list(REQUIRED_SYMBOLS),
        "required_timeframes": list(REQUIRED_TIMEFRAMES),
        "required_output_fields": list(REQUIRED_CANDLE_FIELDS),
        "approves_source_rules_only": True,
        "every_concrete_source_needs_human_signature": True,
        "actual_staging_requires_separate_human_approval": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
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
    plan = build_real_candle_staging_plan()
    if (not validate_real_candle_staging_plan(plan).get("valid")
            or plan.get("verdict") != VERDICT_SP_READY):
        contract["verdict"] = VERDICT_SA_BLOCKED
        contract["blockers"].append("staging_plan_not_ready")
        return contract
    contract["verdict"] = VERDICT_SA_READY
    return contract


def validate_candle_source_approval_contract(contract: Any) -> dict[str, Any]:
    """Validate the contract's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract
    if c.get("verdict") not in (VERDICT_SA_READY, VERDICT_SA_BLOCKED):
        errors.append("bad_verdict")
    if c.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(c.get("allowed_source_categories") or ()) != (
            ALLOWED_SOURCE_CATEGORIES):
        errors.append("allowed_categories_tampered")
    if tuple(c.get("source_requirements") or ()) != SOURCE_REQUIREMENTS:
        errors.append("source_requirements_tampered")
    if tuple(c.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if tuple(c.get("required_symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(c.get("required_timeframes") or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_tampered")
    if tuple(c.get("required_output_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("output_fields_tampered")
    for key, want in (
        ("approves_source_rules_only", True),
        ("every_concrete_source_needs_human_signature", True),
        ("actual_staging_requires_separate_human_approval", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if c.get(key) is not want:
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
        if c.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
