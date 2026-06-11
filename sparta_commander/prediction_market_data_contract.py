"""SPARTA Prediction Market Factory V1 - DATA CONTRACT (READ-ONLY, STAGED ONLY).

Roadmap seq 2: the rulebook for WHAT DATA the future PM scanner may ever read.
Operator-staged (or future separately-approved no-auth public import) only.
Markets, never accounts: wallet/key/login/order/position data refuses outright.
This module reads no file, fetches nothing, connects to nothing.
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.prediction_market_scanner_spec_contract import (
    VERDICT_PM_SPEC_READY,
    build_prediction_market_scanner_spec,
    validate_prediction_market_scanner_spec,
)

PM_DATA_SCHEMA_VERSION = "prediction_market_data_contract.v1"
PM_DATA_LABEL = ("SPARTA Prediction Market Factory V1 Data Contract "
                 "(READ-ONLY, STAGED DATA ONLY)")
PM_DATA_MODE = "RESEARCH_ONLY"
VERDICT_PM_DATA_READY = "PREDICTION_MARKET_DATA_CONTRACT_READY"
VERDICT_PM_DATA_BLOCKED = "PREDICTION_MARKET_DATA_CONTRACT_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PM_COST_SETTLEMENT_MODEL"

STAGING_ROOT = "data/prediction_market_factory_v1/staged/"
MAX_STALENESS_DAYS = 7  # prediction markets move fast; quotes older than this
                        # must be explicitly acknowledged

ALLOWED_MARKET_STATUS = ("open", "closed", "resolved", "paused")
ALLOWED_RELATIONSHIPS = ("same_event", "mutually_exclusive", "correlated",
                         "inverse", "parent_child")

STAGED_DATASET_SPECS: dict[str, dict[str, Any]] = {
    "markets": {"file_pattern": STAGING_ROOT + "markets.csv",
                "required_columns": ("market_id", "event_id", "question_label",
                                     "resolution_date_utc", "market_status",
                                     "provenance_label")},
    "outcome_prices": {"file_pattern": STAGING_ROOT + "outcome_prices.csv",
                       "required_columns": ("timestamp_utc", "market_id",
                                            "outcome_yes_price",
                                            "outcome_no_price",
                                            "provenance_label")},
    "orderbook_quotes": {"file_pattern": STAGING_ROOT + "orderbook_quotes.csv",
                         "required_columns": ("timestamp_utc", "market_id",
                                              "yes_bid", "yes_ask", "no_bid",
                                              "no_ask", "provenance_label")},
    "liquidity_depth": {"file_pattern": STAGING_ROOT + "liquidity_depth.csv",
                        "required_columns": ("timestamp_utc", "market_id",
                                             "yes_depth_usd", "no_depth_usd",
                                             "spread_bps", "provenance_label")},
    "event_relationships": {"file_pattern": STAGING_ROOT + "event_relationships.csv",
                            "required_columns": ("market_id", "related_market_id",
                                                 "relationship_type", "event_id",
                                                 "provenance_label")},
    "cost_assumptions": {"file_pattern": STAGING_ROOT + "cost_assumptions.csv",
                         "required_columns": ("venue_label", "fee_bps",
                                              "gas_cost_usd",
                                              "settlement_cost_bps",
                                              "provenance_label")},
}

FORBIDDEN_FIELD_TOKENS = (
    "wallet", "private_key", "seed_phrase", "account", "balance", "position",
    "order_id", "fill", "deposit", "withdraw", "login", "session", "cookie",
    "api_key", "apikey", "secret", "bearer_token", "auth_token",
)

VALIDATION_RULES = (
    "no_private_account_wallet_or_authenticated_data_ever",
    "no_execution_or_trade_fields_in_any_dataset",
    "timestamps_and_resolution_dates_utc_iso8601_only",
    "quotes_older_than_max_staleness_must_be_explicitly_acknowledged",
    "missing_dataset_kinds_block_scanner_readiness",
    "duplicate_market_id_outcome_rows_refuse",
    "probabilities_must_lie_in_zero_to_one",
    "yes_plus_no_outside_sanity_band_is_flagged_as_data_quality_not_edge",
    "market_status_and_relationship_labels_from_closed_lists_only",
)


def get_prediction_market_data_contract_label() -> str:
    return PM_DATA_LABEL


def validate_pm_dataset_descriptor(kind: Any, columns: Any) -> dict[str, Any]:
    """Validate (pure) a proposed staged dataset descriptor. Reads no file."""
    if kind not in STAGED_DATASET_SPECS:
        return {"acceptable": False, "errors": ["unknown_dataset_kind:" + str(kind)]}
    if not isinstance(columns, (list, tuple)) or not columns:
        return {"acceptable": False, "errors": ["columns_missing_or_empty"]}
    names = [str(c).strip().lower() for c in columns]
    errors = []
    for name in names:  # forbidden FIRST: account data poisons the file
        for token in FORBIDDEN_FIELD_TOKENS:
            if token in name:
                errors.append("forbidden_field:" + name + " (token: " + token + ")")
    if errors:
        return {"acceptable": False, "errors": errors}
    for col in STAGED_DATASET_SPECS[kind]["required_columns"]:
        if col not in names:
            errors.append("missing_required_column:" + col)
    if len(set(names)) != len(names):
        errors.append("duplicate_column_names")
    return {"acceptable": not errors, "errors": errors}


def validate_outcome_price_row(yes_price: Any, no_price: Any) -> dict[str, Any]:
    """Pure probability sanity check for one YES/NO price pair."""
    errors: list[str] = []
    flags: list[str] = []
    for name, p in (("outcome_yes_price", yes_price), ("outcome_no_price", no_price)):
        if not isinstance(p, (int, float)) or isinstance(p, bool):
            errors.append("non_numeric:" + name)
        elif not (0.0 <= float(p) <= 1.0):
            errors.append("probability_out_of_range:" + name)
    if not errors and abs(float(yes_price) + float(no_price) - 1.0) > 0.25:
        flags.append("yes_no_sum_outside_sanity_band_check_data_quality")
    return {"acceptable": not errors, "errors": errors, "flags": flags}


def _base_contract() -> dict[str, Any]:
    return {
        "schema_version": PM_DATA_SCHEMA_VERSION, "label": PM_DATA_LABEL,
        "mode": PM_DATA_MODE, "lane": "prediction_market_factory_v1",
        "roadmap_seq": 2, "verdict": None, "blockers": [],
        "scanner_spec_verdict": None,
        "staging_root": STAGING_ROOT,
        "staged_dataset_specs": copy.deepcopy(STAGED_DATASET_SPECS),
        "allowed_market_status": list(ALLOWED_MARKET_STATUS),
        "allowed_relationships": list(ALLOWED_RELATIONSHIPS),
        "forbidden_field_tokens": list(FORBIDDEN_FIELD_TOKENS),
        "validation_rules": list(VALIDATION_RULES),
        "max_staleness_days": MAX_STALENESS_DAYS,
        "staging_is_manual_operator_only": True,
        "data_describes_markets_never_accounts": True,
        "contract_reads_no_files": True,
        "output_is_readiness_only_never_a_scan_result": True,
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


def record_prediction_market_data_contract(scanner_spec: Any) -> dict[str, Any]:
    """Record the data contract, gated on a READY, valid seq-1 scanner spec."""
    c = _base_contract()
    if not isinstance(scanner_spec, dict):
        c["verdict"] = VERDICT_PM_DATA_BLOCKED
        c["blockers"].append("scanner_spec_missing")
        return c
    if not validate_prediction_market_scanner_spec(scanner_spec).get("valid"):
        c["verdict"] = VERDICT_PM_DATA_BLOCKED
        c["blockers"].append("scanner_spec_invalid")
        return c
    if scanner_spec.get("verdict") != VERDICT_PM_SPEC_READY:
        c["verdict"] = VERDICT_PM_DATA_BLOCKED
        c["blockers"].append("scanner_spec_not_ready")
        return c
    c["verdict"] = VERDICT_PM_DATA_READY
    c["scanner_spec_verdict"] = scanner_spec.get("verdict")
    return c


def build_prediction_market_data_contract() -> dict[str, Any]:
    """Build against the real seq 0 -> 1 chain. Pure."""
    return record_prediction_market_data_contract(
        build_prediction_market_scanner_spec())


def validate_prediction_market_data_contract(contract: Any) -> dict[str, Any]:
    """Validate the contract's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract
    verdict = c.get("verdict")
    if verdict not in (VERDICT_PM_DATA_READY, VERDICT_PM_DATA_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_PM_DATA_BLOCKED and not c.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_PM_DATA_READY:
        if c.get("blockers"):
            errors.append("ready_with_blockers")
        if c.get("scanner_spec_verdict") != VERDICT_PM_SPEC_READY:
            errors.append("ready_without_ready_scanner_spec")
    if c.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if c.get("roadmap_seq") != 2:
        errors.append("wrong_roadmap_seq")
    if c.get("staging_root") != STAGING_ROOT:
        errors.append("staging_root_moved")
    specs = c.get("staged_dataset_specs")
    if not isinstance(specs, dict) or set(specs) != set(STAGED_DATASET_SPECS):
        errors.append("dataset_specs_tampered")
    else:
        for kind, spec in specs.items():
            joined = " ".join(str(x).lower() for x in spec.get("required_columns") or ())
            for token in FORBIDDEN_FIELD_TOKENS:
                if token in joined:
                    errors.append("forbidden_field_in_spec:" + kind)
                    break
            if not str(spec.get("file_pattern", "")).startswith(STAGING_ROOT):
                errors.append("spec_outside_staging_root:" + kind)
    if tuple(c.get("allowed_market_status") or ()) != ALLOWED_MARKET_STATUS:
        errors.append("status_labels_tampered")
    if tuple(c.get("allowed_relationships") or ()) != ALLOWED_RELATIONSHIPS:
        errors.append("relationship_labels_tampered")
    if tuple(c.get("forbidden_field_tokens") or ()) != FORBIDDEN_FIELD_TOKENS:
        errors.append("forbidden_tokens_weakened")
    if tuple(c.get("validation_rules") or ()) != VALIDATION_RULES:
        errors.append("validation_rules_tampered")
    if c.get("max_staleness_days") != MAX_STALENESS_DAYS:
        errors.append("staleness_rule_tampered")
    for key, want in (("staging_is_manual_operator_only", True),
                      ("data_describes_markets_never_accounts", True),
                      ("contract_reads_no_files", True),
                      ("output_is_readiness_only_never_a_scan_result", True),
                      ("modifies_arbitrage_factory_v1_lane", False),
                      ("modifies_crypto_d1_lane", False),
                      ("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if c.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "fetches_data", "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if c.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
