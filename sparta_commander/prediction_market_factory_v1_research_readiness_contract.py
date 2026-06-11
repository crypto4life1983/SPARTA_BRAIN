"""SPARTA Prediction Market Factory V1 - RESEARCH READINESS (READ-ONLY).

Lane constitution for Polymarket-style prediction-market research -- a NEW lane,
separate from the crypto-exchange Arbitrage Factory V1. Alerts/reports only;
execution is absent by construction; no wallet, key, login, or account, ever.
"""

from __future__ import annotations

from typing import Any

PM_SCHEMA_VERSION = "prediction_market_factory_v1_research_readiness_contract.v1"
PM_LABEL = ("SPARTA Prediction Market Factory V1 Research Readiness "
            "(READ-ONLY, RESEARCH ONLY)")
PM_MODE = "RESEARCH_ONLY"
VERDICT_PM_READINESS_READY = "PREDICTION_MARKET_FACTORY_V1_READINESS_READY"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PREDICTION_MARKET_SCANNER_SPEC"

CANDIDATE_FAMILIES = (
    "PM_F1_yes_no_pricing_inefficiency",
    "PM_F2_cross_market_inconsistency",
    "PM_F3_correlated_event_mispricing",
    "PM_F4_probability_drift_and_spread",
    "PM_F5_fee_gas_settlement_adjusted_edge",
    "PM_F6_pass_watch_fail_report_framework",
)

REQUIRED_FUTURE_DATA_TYPES = (
    "market_id", "event_id", "outcome_yes_price", "outcome_no_price",
    "bid_ask_per_outcome", "liquidity_depth", "resolution_date",
    "market_status", "source_provenance_label",
    "fee_gas_settlement_cost_assumptions",
)

FORBIDDEN_DATA = (
    "wallet_address", "private_key", "seed_phrase", "account_balance",
    "positions", "orders", "fills", "deposits_withdrawals",
    "login_session_cookie_api_key",
)

NO_TRADE_RULES = (
    "alerts_and_reports_only_execution_is_absent_by_construction",
    "no_wallet_key_login_account_or_credential_ever",
    "no_deposits_no_withdrawals_no_settlement_actions",
    "public_read_only_data_only_staged_by_a_human_or_future_approved_contract",
    "every_future_scanner_run_needs_per_run_human_approval",
    "top_level_architecture_authorization_required_before_any_execution_talk",
)

FUTURE_BLOCKS_ROADMAP = (
    {"seq": 1, "block": "prediction_market_scanner_spec_contract"},
    {"seq": 2, "block": "prediction_market_data_contract"},
    {"seq": 3, "block": "prediction_market_cost_and_settlement_model_contract"},
    {"seq": 4, "block": "prediction_market_alert_report_schema_contract"},
    {"seq": 5, "block": "prediction_market_lane_review_contract"},
    {"seq": 6, "block": "prediction_market_mission_flow_registration"},
)


def get_prediction_market_factory_v1_readiness_label() -> str:
    return PM_LABEL


def build_prediction_market_factory_v1_readiness() -> dict[str, Any]:
    """Assemble the lane constitution. PURE: defines, never acts."""
    return {
        "schema_version": PM_SCHEMA_VERSION, "label": PM_LABEL, "mode": PM_MODE,
        "lane": "prediction_market_factory_v1",
        "verdict": VERDICT_PM_READINESS_READY,
        "separate_from_arbitrage_factory_v1": True,
        "candidate_families": list(CANDIDATE_FAMILIES),
        "required_future_data_types": list(REQUIRED_FUTURE_DATA_TYPES),
        "forbidden_data": list(FORBIDDEN_DATA),
        "no_trade_rules": list(NO_TRADE_RULES),
        "future_blocks_roadmap": [dict(b) for b in FUTURE_BLOCKS_ROADMAP],
        "alerts_and_reports_only": True,
        "execution_capability_exists": False,
        "modifies_crypto_d1_lane": False,
        "modifies_arbitrage_factory_v1_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "runs_scanner": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_prediction_market_factory_v1_readiness(spec: Any) -> dict[str, Any]:
    """Validate the constitution's safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") != VERDICT_PM_READINESS_READY:
        errors.append("bad_verdict")
    if s.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if tuple(s.get("candidate_families") or ()) != CANDIDATE_FAMILIES:
        errors.append("families_tampered")
    if tuple(s.get("required_future_data_types") or ()) != REQUIRED_FUTURE_DATA_TYPES:
        errors.append("data_types_tampered")
    if tuple(s.get("forbidden_data") or ()) != FORBIDDEN_DATA:
        errors.append("forbidden_data_weakened")
    if tuple(s.get("no_trade_rules") or ()) != NO_TRADE_RULES:
        errors.append("no_trade_rules_weakened")
    if [b.get("seq") for b in s.get("future_blocks_roadmap") or []] != [1, 2, 3, 4, 5, 6]:
        errors.append("roadmap_broken")
    for key, want in (("alerts_and_reports_only", True),
                      ("execution_capability_exists", False),
                      ("separate_from_arbitrage_factory_v1", True),
                      ("modifies_crypto_d1_lane", False),
                      ("modifies_arbitrage_factory_v1_lane", False),
                      ("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if s.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "runs_scanner", "fetches_data",
                "calls_api", "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
