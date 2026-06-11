"""SPARTA NY-Session FVG+CHOCH PUBLIC CANDLE FETCH PLAN (READ-ONLY,
PLAN ONLY, NO NETWORK).

The thin retrieval plan that can LATER -- only after the separate human run
approval -- pull no-auth public historical 1m/15m klines and hand normalized
rows to the already-built (and still token-gated) file creation tool. This
module is a PLAN: it contains the endpoint allowlist rules, symbol/timeframe
normalization maps, and handoff contract. It performs no network calls, has
no network imports, writes nothing, and runs nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool import (
    build_file_creation_plan,
    validate_file_creation_plan,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
    SESSION_COVERAGE,
    validate_date_range_plan,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

FP_SCHEMA_VERSION = "ny_session_fvg_choch_public_candle_fetch_plan.v1"
FP_LABEL = ("SPARTA NY-Session FVG+CHOCH Public Candle Fetch Plan "
            "(READ-ONLY, PLAN ONLY, NO NETWORK, RUNS NOTHING)")
FP_MODE = "RESEARCH_ONLY"
VERDICT_FP_READY = "NY_FVG_CHOCH_PUBLIC_CANDLE_FETCH_PLAN_READY"
VERDICT_FP_BLOCKED = "NY_FVG_CHOCH_PUBLIC_CANDLE_FETCH_PLAN_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION"

SOURCE_CATEGORY = "no_auth_public_historical_endpoint_human_approved"
SOURCE_NAME_PLACEHOLDER = (
    "public_no_auth_historical_klines_source_to_be_named_by_human")
RATE_LIMIT_TERMS_PLACEHOLDER = (
    "public rate limits and terms to be noted when the human names the "
    "concrete source")

ENDPOINT_ALLOWLIST_TOKENS = ("klines", "candles", "ohlcv", "history")
_FORBIDDEN_ENDPOINT_TOKENS = ("order", "trade", "position", "account",
                              "wallet", "balance", "private", "withdraw",
                              "transfer", "auth", "login", "key", "secret",
                              "user", "margin", "leverage")

SYMBOL_MAPPING_PLAN = {
    canonical: (canonical, canonical + "T", canonical[:-3] + "-USD")
    for canonical in REQUIRED_SYMBOLS
}  # e.g. BTCUSDT or BTC-USD on the source side normalize to BTCUSD

TIMEFRAME_MAPPING_PLAN = {"1m": ("1m", "1min", "60"),
                          "15m": ("15m", "15min", "900")}

NORMALIZATION_RULES = (
    "rows_normalize_to_required_fields_exactly",
    "timestamps_normalize_to_utc_iso8601_z",
    "gaps_are_flagged_in_flagged_gaps_never_silently_filled",
    "source_recorded_on_every_row",
    "symbols_normalize_via_symbol_mapping_plan",
    "timeframes_normalize_via_timeframe_mapping_plan",
)

PROVENANCE_FIELDS = ("source", "endpoint_path_note", "retrieval_date_note")

HANDOFF_CONTRACT = (
    "normalized_rows_pass_through_run_real_candle_staging_dry_run",
    "then_build_file_creation_plan_produces_paths_and_sha256_checksums",
    "then_execute_file_creation_refuses_without_the_exact_human_token",
    "staged_files_remain_untracked_operational_data",
)

FORBIDDEN = (
    "running_a_data_pull_in_this_block", "network_calls_in_tests_or_build",
    "file_writes", "creating_data_ny_fvg_choch_directory",
    "api_keys_secrets_credentials", "login_account_wallet_access",
    "private_endpoints", "trading_endpoints_of_any_kind",
    "live_market_polling", "detector_replay_scorer_runs",
    "optimizer_runs", "paper_live_micro_live_authorization",
    "gate_unlocks",
)

_GATE_PROPOSAL = {
    "source_name": "public_no_auth_historical_klines",
    "category": SOURCE_CATEGORY,
    "provenance": "canonical in-memory gate fixture",
    "terms_and_limits": "public rate limits apply; historical only",
    "historical_only": True,
    "requires_login": False, "requires_api_key": False,
    "requires_credentials": False, "uses_private_endpoint": False,
    "is_live_polling": False,
    "symbols": REQUIRED_SYMBOLS, "timeframes": REQUIRED_TIMEFRAMES,
    "output_fields": REQUIRED_CANDLE_FIELDS,
}
_GATE_PAYLOAD = {
    "symbol": "BTCUSD", "timeframe": "1m",
    "rows": [{"timestamp": "2026-06-10T13:3%d:00Z" % i, "open": 100.0,
              "high": 101.0, "low": 99.0, "close": 100.5, "volume": 12.5,
              "source": "public_no_auth", "timeframe": "1m",
              "symbol": "BTCUSD"} for i in range(3)],
}


def get_public_candle_fetch_plan_label() -> str:
    return FP_LABEL


def validate_fetch_source_plan(proposal: Any) -> dict[str, Any]:
    """Pure rule check of ONE concrete retrieval-source plan. Approvable
    here still requires the human run token before anything moves."""
    errors: list[str] = []
    if not isinstance(proposal, dict):
        return {"approvable": False, "errors": ["proposal_not_a_dict"],
                "human_run_approval_still_required": True}
    if proposal.get("category") != SOURCE_CATEGORY:
        errors.append("category_not_allowed:" + str(proposal.get("category")))
    if not str(proposal.get("source_name") or "").strip():
        errors.append("source_name_missing")
    endpoint = str(proposal.get("endpoint_path") or "").lower()
    if not endpoint:
        errors.append("endpoint_path_missing")
    else:
        if not any(token in endpoint for token in ENDPOINT_ALLOWLIST_TOKENS):
            errors.append("endpoint_not_in_historical_allowlist")
        for token in _FORBIDDEN_ENDPOINT_TOKENS:
            if token in endpoint:
                errors.append("forbidden_endpoint_token:" + token)
    for flag in ("uses_authenticated_headers", "requires_api_key",
                 "requires_credentials", "requires_login",
                 "uses_private_endpoint"):
        if proposal.get(flag) is not False:
            errors.append("forbidden_access_requirement:" + flag)
    if proposal.get("is_live_polling") is not False:
        errors.append("live_polling_forbidden")
    if proposal.get("historical_only") is not True:
        errors.append("source_not_historical_only")
    mapping = proposal.get("symbol_mapping")
    if (not isinstance(mapping, dict)
            or set(mapping.values()) != set(REQUIRED_SYMBOLS)):
        errors.append("symbol_mapping_does_not_cover_required_symbols")
    tf_mapping = proposal.get("timeframe_mapping")
    if (not isinstance(tf_mapping, dict)
            or set(tf_mapping.values()) != set(REQUIRED_TIMEFRAMES)):
        errors.append("timeframe_mapping_does_not_cover_required_timeframes")
    if tuple(proposal.get("normalized_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("normalization_schema_missing_or_wrong")
    if not str(proposal.get("provenance") or "").strip():
        errors.append("provenance_missing")
    if not str(proposal.get("terms_and_limits") or "").strip():
        errors.append("terms_and_limits_missing")
    if not validate_date_range_plan(
            proposal.get("date_range")).get("acceptable"):
        errors.append("date_range_plan_missing_or_invalid")
    if proposal.get("session_coverage") != SESSION_COVERAGE:
        errors.append("session_coverage_missing_or_wrong")
    return {"approvable": not errors, "errors": errors,
            "human_run_approval_still_required": True}


def build_public_candle_fetch_plan() -> dict[str, Any]:
    """Assemble the retrieval plan, gated on the pushed file creation tool
    producing a READY plan for the canonical in-memory fixture."""
    plan: dict[str, Any] = {
        "schema_version": FP_SCHEMA_VERSION, "label": FP_LABEL,
        "mode": FP_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "source_category": SOURCE_CATEGORY,
        "source_name_placeholder": SOURCE_NAME_PLACEHOLDER,
        "rate_limit_terms_note": RATE_LIMIT_TERMS_PLACEHOLDER,
        "endpoint_allowlist_tokens": list(ENDPOINT_ALLOWLIST_TOKENS),
        "symbol_mapping_plan": {k: list(v)
                                for k, v in SYMBOL_MAPPING_PLAN.items()},
        "timeframe_mapping_plan": {k: list(v)
                                   for k, v in TIMEFRAME_MAPPING_PLAN.items()},
        "required_symbols": list(REQUIRED_SYMBOLS),
        "required_timeframes": list(REQUIRED_TIMEFRAMES),
        "normalized_fields": list(REQUIRED_CANDLE_FIELDS),
        "normalization_rules": list(NORMALIZATION_RULES),
        "provenance_fields": list(PROVENANCE_FIELDS),
        "session_coverage": dict(SESSION_COVERAGE),
        "date_range_plan_source": "staging_plan_validate_date_range_plan",
        "handoff_contract": list(HANDOFF_CONTRACT),
        "forbidden": list(FORBIDDEN),
        "future_run_approval_required": True,
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
    gate = build_file_creation_plan(dict(_GATE_PROPOSAL),
                                    [dict(_GATE_PAYLOAD)])
    if (gate.get("plan_status")
            != "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL"
            or not validate_file_creation_plan(gate).get("valid")):
        plan["verdict"] = VERDICT_FP_BLOCKED
        plan["blockers"].append("file_creation_tool_not_ready")
        return plan
    plan["verdict"] = VERDICT_FP_READY
    return plan


def validate_public_candle_fetch_plan(plan: Any) -> dict[str, Any]:
    """Validate the plan's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan
    if p.get("verdict") not in (VERDICT_FP_READY, VERDICT_FP_BLOCKED):
        errors.append("bad_verdict")
    if p.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if p.get("source_category") != SOURCE_CATEGORY:
        errors.append("source_category_tampered")
    if tuple(p.get("endpoint_allowlist_tokens") or ()) != (
            ENDPOINT_ALLOWLIST_TOKENS):
        errors.append("endpoint_allowlist_tampered")
    if {k: tuple(v) for k, v in (p.get("symbol_mapping_plan")
                                 or {}).items()} != SYMBOL_MAPPING_PLAN:
        errors.append("symbol_mapping_plan_tampered")
    if {k: tuple(v) for k, v in (p.get("timeframe_mapping_plan")
                                 or {}).items()} != TIMEFRAME_MAPPING_PLAN:
        errors.append("timeframe_mapping_plan_tampered")
    if tuple(p.get("required_symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(p.get("required_timeframes") or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_tampered")
    if tuple(p.get("normalized_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("normalized_fields_tampered")
    if tuple(p.get("normalization_rules") or ()) != NORMALIZATION_RULES:
        errors.append("normalization_rules_tampered")
    if tuple(p.get("provenance_fields") or ()) != PROVENANCE_FIELDS:
        errors.append("provenance_fields_tampered")
    if p.get("session_coverage") != SESSION_COVERAGE:
        errors.append("session_coverage_tampered")
    if tuple(p.get("handoff_contract") or ()) != HANDOFF_CONTRACT:
        errors.append("handoff_contract_tampered")
    if tuple(p.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (
        ("future_run_approval_required", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if p.get(key) is not want:
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
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
