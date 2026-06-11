"""SPARTA Prediction Market Factory V1 - SCANNER SPEC (READ-ONLY, SPEC ONLY).

Roadmap seq 1 of the Prediction Market Factory V1 lane: the frozen spec for a
FUTURE read-only scanner over Polymarket-style markets. This contract builds
NO scanner: it defines what one may ever be, gated on the lane readiness
constitution. Alerts/reports only; no wallet, login, account, key, deposit,
withdrawal, order, or position -- ever.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.prediction_market_factory_v1_research_readiness_contract import (
    CANDIDATE_FAMILIES,
    VERDICT_PM_READINESS_READY,
    build_prediction_market_factory_v1_readiness,
    validate_prediction_market_factory_v1_readiness,
)

PM_SPEC_SCHEMA_VERSION = "prediction_market_scanner_spec_contract.v1"
PM_SPEC_LABEL = ("SPARTA Prediction Market Factory V1 Scanner Spec "
                 "(READ-ONLY, SPEC ONLY)")
PM_SPEC_MODE = "RESEARCH_ONLY"
VERDICT_PM_SPEC_READY = "PREDICTION_MARKET_SCANNER_SPEC_READY"
VERDICT_PM_SPEC_BLOCKED = "PREDICTION_MARKET_SCANNER_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PREDICTION_MARKET_DATA_CONTRACT"

REPORTS_ROOT = "reports/prediction_market_factory_v1/"

ALLOWED_INPUT_DATA_TYPES = (
    "market_id", "event_id", "outcome_yes_price", "outcome_no_price",
    "yes_bid", "yes_ask", "no_bid", "no_ask", "liquidity_depth",
    "resolution_date", "market_status", "provenance_label",
    "fee_gas_settlement_cost_assumptions",
)

FORBIDDEN_INPUTS = (
    "wallet_address", "private_key", "seed_phrase", "account_balance",
    "positions", "orders", "fills", "deposits_withdrawals",
    "login_session_cookie_api_key",
)

OUTPUT_RULES = (
    "pass_watch_fail_research_alerts_only",
    "no_trading_instruction_ever",
    "no_guaranteed_or_winning_claim_ever",
    "no_wallet_or_account_action_ever",
    "full_cost_settlement_and_resolution_risk_caveat_on_every_alert",
    "mandatory_research_only_disclaimer_verbatim",
    "one_approved_run_writes_one_report_under_reports_prediction_market_factory_v1",
    "refused_or_blocked_runs_write_nothing",
    "every_run_needs_its_own_per_run_human_approval_no_scheduler",
)


def get_prediction_market_scanner_spec_label() -> str:
    return PM_SPEC_LABEL


def _base_spec() -> dict[str, Any]:
    return {
        "schema_version": PM_SPEC_SCHEMA_VERSION, "label": PM_SPEC_LABEL,
        "mode": PM_SPEC_MODE, "lane": "prediction_market_factory_v1",
        "roadmap_seq": 1, "verdict": None, "blockers": [],
        "readiness_verdict": None,
        "accepted_families": list(CANDIDATE_FAMILIES),
        "allowed_input_data_types": list(ALLOWED_INPUT_DATA_TYPES),
        "forbidden_inputs": list(FORBIDDEN_INPUTS),
        "output_rules": list(OUTPUT_RULES),
        "reports_root": REPORTS_ROOT,
        "scanner_built_by_this_contract": False,
        "alerts_and_reports_only": True,
        "modifies_arbitrage_factory_v1_lane": False,
        "modifies_crypto_d1_lane": False,
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


def record_prediction_market_scanner_spec(readiness: Any) -> dict[str, Any]:
    """Record the spec, gated on a READY, valid lane readiness constitution.
    PURE: builds no scanner, never raises."""
    spec = _base_spec()
    if not isinstance(readiness, dict):
        spec["verdict"] = VERDICT_PM_SPEC_BLOCKED
        spec["blockers"].append("readiness_missing")
        return spec
    if not validate_prediction_market_factory_v1_readiness(readiness).get("valid"):
        spec["verdict"] = VERDICT_PM_SPEC_BLOCKED
        spec["blockers"].append("readiness_invalid")
        return spec
    if readiness.get("verdict") != VERDICT_PM_READINESS_READY:
        spec["verdict"] = VERDICT_PM_SPEC_BLOCKED
        spec["blockers"].append("readiness_not_ready")
        return spec
    if readiness.get("alerts_and_reports_only") is not True:
        spec["verdict"] = VERDICT_PM_SPEC_BLOCKED
        spec["blockers"].append("lane_constitution_violated")
        return spec
    spec["verdict"] = VERDICT_PM_SPEC_READY
    spec["readiness_verdict"] = readiness.get("verdict")
    return spec


def build_prediction_market_scanner_spec() -> dict[str, Any]:
    """Build the spec against the real lane constitution. Pure."""
    return record_prediction_market_scanner_spec(
        build_prediction_market_factory_v1_readiness())


def validate_prediction_market_scanner_spec(spec: Any) -> dict[str, Any]:
    """Validate the spec's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    verdict = s.get("verdict")
    if verdict not in (VERDICT_PM_SPEC_READY, VERDICT_PM_SPEC_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_PM_SPEC_BLOCKED and not s.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_PM_SPEC_READY:
        if s.get("blockers"):
            errors.append("ready_with_blockers")
        if s.get("readiness_verdict") != VERDICT_PM_READINESS_READY:
            errors.append("ready_without_ready_readiness")
    if s.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if s.get("roadmap_seq") != 1:
        errors.append("wrong_roadmap_seq")
    if s.get("reports_root") != REPORTS_ROOT:
        errors.append("reports_root_moved")
    if tuple(s.get("accepted_families") or ()) != CANDIDATE_FAMILIES:
        errors.append("families_tampered")
    if tuple(s.get("allowed_input_data_types") or ()) != ALLOWED_INPUT_DATA_TYPES:
        errors.append("input_types_tampered")
    if tuple(s.get("forbidden_inputs") or ()) != FORBIDDEN_INPUTS:
        errors.append("forbidden_inputs_weakened")
    if tuple(s.get("output_rules") or ()) != OUTPUT_RULES:
        errors.append("output_rules_tampered")
    if s.get("scanner_built_by_this_contract") is not False:
        errors.append("scanner_claimed_built")
    for key, want in (("alerts_and_reports_only", True),
                      ("modifies_arbitrage_factory_v1_lane", False),
                      ("modifies_crypto_d1_lane", False),
                      ("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
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
