"""SPARTA Arbitrage Factory V1 - DATA CONTRACT (READ-ONLY, STAGED DATA ONLY).

Roadmap seq 2 of the Arbitrage Factory V1 lane (step 1 of signed batch
batch_aeb83ad9d637): the rulebook for WHAT DATA the future scanner may ever
read -- and, just as important, what data may NEVER exist in this lane at all.

The data model is OPERATOR-STAGED ONLY: a human manually places CSV files under
the lane's staging directory. This contract defines their shapes. It connects
to NOTHING: no exchange, no API, no credentialed endpoint, no network. Venue
names appear here as LABELS on rows of a CSV -- a venue label is a string, not
a connection, and this module cannot turn one into a connection because it
imports no transport code.

Dataset kinds (one per research family group):
  - funding_rates        -> ARB_F1 (spot-perp funding/basis)
  - spot_perp_basis      -> ARB_F1, ARB_F2 (cross-exchange basis)
  - cross_exchange_quotes-> ARB_F2, ARB_F3 (BTC/ETH/SOL pair-spread alerts)
  - fee_schedule         -> ARB_F4 (fee-adjusted net edge)
  - liquidity_depth      -> ARB_F5 (liquidity/spread/slippage filters)
All map forward into the ARB_F6 PASS/WATCH/FAIL report framework.

Hard refusals (validator-enforced):
  - FORBIDDEN FIELDS: any column whose name smells of credentials, account
    data, wallet balances, order/fill data, live positions, leverage, margin,
    or PnL refuses the WHOLE descriptor. Research data describes MARKETS,
    never ACCOUNTS. There is no execution field because execution is absent
    by construction in this lane.
  - Unknown symbols/venues/kinds refuse; missing required columns refuse;
    stale data must be flagged, never silently used.
  - This contract validates DESCRIPTORS and READINESS only. It reads no file,
    fetches nothing, scans nothing, and produces no scan result.

Public API:
  - DATA_CONTRACT_SCHEMA_VERSION / DATA_CONTRACT_LABEL / DATA_CONTRACT_MODE
  - VERDICT_DATA_CONTRACT_READY / VERDICT_DATA_CONTRACT_BLOCKED
  - ALLOWED_SYMBOLS / ALLOWED_VENUE_LABELS / STAGED_DATASET_SPECS
  - VALIDATION_RULES / FORBIDDEN_FIELD_TOKENS / FAMILY_MAPPING
  - MAX_STALENESS_DAYS_FOR_RESEARCH / NEXT_REQUIRED_ACTION
  - get_arbitrage_data_contract_label()
  - record_arbitrage_data_contract(scanner_spec)
  - build_arbitrage_data_contract()
  - validate_arbitrage_data_contract(contract)
  - validate_staged_dataset_descriptor(kind, columns)
  - render_arbitrage_data_contract_markdown(contract)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.arbitrage_scanner_spec_contract import (
    VERDICT_SPEC_READY,
    build_arbitrage_scanner_spec,
    validate_arbitrage_scanner_spec,
)

DATA_CONTRACT_SCHEMA_VERSION = "arbitrage_data_contract.v1"
DATA_CONTRACT_LABEL = (
    "SPARTA Arbitrage Factory V1 Data Contract (READ-ONLY, STAGED DATA ONLY)"
)
DATA_CONTRACT_MODE = "RESEARCH_ONLY"

VERDICT_DATA_CONTRACT_READY = "ARBITRAGE_DATA_CONTRACT_READY"
VERDICT_DATA_CONTRACT_BLOCKED = "ARBITRAGE_DATA_CONTRACT_BLOCKED"

# Roadmap seq 3: the fee/slippage model, under its own human approval.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_FEE_SLIPPAGE_MODEL"

# Labels only. A symbol or venue string names a CSV row, never a connection.
ALLOWED_SYMBOLS = ("BTC", "ETH", "SOL")
ALLOWED_VENUE_LABELS = ("binance", "bybit", "okx", "coinbase", "kraken")

# Where the human operator stages files. Nothing in this lane writes there.
STAGING_ROOT = "data/arbitrage_factory_v1/staged/"

MAX_STALENESS_DAYS_FOR_RESEARCH = 30

# The closed catalog of staged dataset kinds and their required shapes.
STAGED_DATASET_SPECS: dict[str, dict[str, Any]] = {
    "funding_rates": {
        "file_pattern": STAGING_ROOT + "funding_{symbol}_{venue}.csv",
        "required_columns": (
            "timestamp_utc", "symbol", "venue", "funding_rate_8h", "mark_price",
        ),
        "maps_to_families": ("ARB_F1_spot_perp_funding_basis",),
    },
    "spot_perp_basis": {
        "file_pattern": STAGING_ROOT + "basis_{symbol}_{venue}.csv",
        "required_columns": (
            "timestamp_utc", "symbol", "venue", "spot_price", "perp_price",
            "basis_pct",
        ),
        "maps_to_families": (
            "ARB_F1_spot_perp_funding_basis",
            "ARB_F2_cross_exchange_basis_monitoring",
        ),
    },
    "cross_exchange_quotes": {
        "file_pattern": STAGING_ROOT + "quotes_{symbol}_{venue}.csv",
        "required_columns": (
            "timestamp_utc", "symbol", "venue", "bid", "ask", "mid",
        ),
        "maps_to_families": (
            "ARB_F2_cross_exchange_basis_monitoring",
            "ARB_F3_btc_eth_sol_pair_spread_alerts",
        ),
    },
    "fee_schedule": {
        "file_pattern": STAGING_ROOT + "fees_{venue}.csv",
        "required_columns": (
            "venue", "symbol", "taker_fee_pct", "maker_fee_pct",
            "withdrawal_flat_fee",
        ),
        "maps_to_families": ("ARB_F4_fee_adjusted_net_edge_scanner",),
    },
    "liquidity_depth": {
        "file_pattern": STAGING_ROOT + "depth_{symbol}_{venue}.csv",
        "required_columns": (
            "timestamp_utc", "symbol", "venue", "bid_depth_usd_10bps",
            "ask_depth_usd_10bps", "spread_bps",
        ),
        "maps_to_families": ("ARB_F5_liquidity_spread_slippage_filters",),
    },
}

# Validation rules the future QA/scanner steps must apply to staged files.
VALIDATION_RULES = (
    "every_required_column_must_be_present_or_the_file_is_rejected",
    "timestamps_must_be_utc_iso8601_and_monotonically_nondecreasing",
    "no_duplicate_timestamp_symbol_venue_rows",
    "prices_fees_and_depths_must_be_finite_and_non_negative",
    "symbols_and_venues_must_be_in_the_allowed_label_lists",
    "stale_data_older_than_max_staleness_must_be_flagged_never_silently_used",
    "files_with_any_forbidden_field_are_rejected_whole_never_partially_read",
    "missing_or_empty_files_block_readiness_they_never_default_to_anything",
)

# Any column name containing one of these tokens refuses the whole descriptor.
# Research data describes MARKETS, never ACCOUNTS.
FORBIDDEN_FIELD_TOKENS = (
    "api_key", "apikey", "secret", "passphrase", "credential", "token",
    "account", "wallet", "address", "balance", "equity",
    "order_id", "orderid", "fill", "execution",
    "position", "leverage", "margin", "pnl",
)

# How staged data maps forward into the future scanner/report contracts.
FAMILY_MAPPING = (
    {"dataset": "funding_rates", "feeds": "ARB_F1",
     "future_report_fields": "funding carry estimate per symbol/venue"},
    {"dataset": "spot_perp_basis", "feeds": "ARB_F1+ARB_F2",
     "future_report_fields": "basis level and cross-venue basis divergence"},
    {"dataset": "cross_exchange_quotes", "feeds": "ARB_F2+ARB_F3",
     "future_report_fields": "pair-spread z-scores and venue quote divergence"},
    {"dataset": "fee_schedule", "feeds": "ARB_F4",
     "future_report_fields": "fee-adjusted net edge after taker/maker costs"},
    {"dataset": "liquidity_depth", "feeds": "ARB_F5",
     "future_report_fields": "depth/spread filters gating every alert"},
    {"dataset": "(all)", "feeds": "ARB_F6",
     "future_report_fields": "PASS/WATCH/FAIL research verdicts, alerts only"},
)


def get_arbitrage_data_contract_label() -> str:
    """Human label for the recognized arbitrage data contract."""
    return DATA_CONTRACT_LABEL


def validate_staged_dataset_descriptor(kind: Any, columns: Any) -> dict[str, Any]:
    """Validate (read-only, in-memory) a PROPOSED staged dataset descriptor:
    a dataset kind plus its column names. Reads no file. Never raises.
    Returns {"acceptable": bool, "errors": [...]}."""
    errors: list[str] = []
    if kind not in STAGED_DATASET_SPECS:
        return {"acceptable": False,
                "errors": ["unknown_dataset_kind:" + str(kind)]}
    if not isinstance(columns, (list, tuple)) or not columns:
        return {"acceptable": False, "errors": ["columns_missing_or_empty"]}

    names = [str(c).strip().lower() for c in columns]

    # Hard refusal FIRST: account/credential/order/position fields poison the
    # whole descriptor regardless of everything else.
    for name in names:
        for token in FORBIDDEN_FIELD_TOKENS:
            if token in name:
                errors.append("forbidden_field:" + name + " (token: " + token + ")")
    if errors:
        return {"acceptable": False, "errors": errors}

    required = STAGED_DATASET_SPECS[kind]["required_columns"]
    for col in required:
        if col not in names:
            errors.append("missing_required_column:" + col)
    if len(set(names)) != len(names):
        errors.append("duplicate_column_names")

    return {"acceptable": not errors, "errors": errors}


def _base_contract() -> dict[str, Any]:
    return {
        "schema_version": DATA_CONTRACT_SCHEMA_VERSION,
        "label": DATA_CONTRACT_LABEL,
        "mode": DATA_CONTRACT_MODE,
        "lane": "arbitrage_factory_v1",
        "roadmap_seq": 2,
        "verdict": None,
        "blockers": [],
        "scanner_spec_verdict": None,
        "allowed_symbols": list(ALLOWED_SYMBOLS),
        "allowed_venue_labels": list(ALLOWED_VENUE_LABELS),
        "venue_labels_are_not_connections": True,
        "staging_root": STAGING_ROOT,
        "staging_is_manual_operator_only": True,
        "staged_dataset_specs": copy.deepcopy(STAGED_DATASET_SPECS),
        "validation_rules": list(VALIDATION_RULES),
        "forbidden_field_tokens": list(FORBIDDEN_FIELD_TOKENS),
        "family_mapping": [dict(m) for m in FAMILY_MAPPING],
        "max_staleness_days_for_research": MAX_STALENESS_DAYS_FOR_RESEARCH,
        # Constitution, stated structurally:
        "data_describes_markets_never_accounts": True,
        "no_execution_fields_exist_in_any_spec": True,
        "contract_reads_no_files": True,
        "output_is_readiness_only_never_a_scan_result": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def record_arbitrage_data_contract(scanner_spec: Any) -> dict[str, Any]:
    """Record the data contract, gated on a READY, valid scanner SPEC (roadmap
    seq 1). PURE: never raises, reads no file, connects to nothing."""
    contract = _base_contract()

    if not isinstance(scanner_spec, dict):
        contract["verdict"] = VERDICT_DATA_CONTRACT_BLOCKED
        contract["blockers"].append("scanner_spec_missing")
        return contract

    validation = validate_arbitrage_scanner_spec(scanner_spec)
    if not validation.get("valid"):
        contract["verdict"] = VERDICT_DATA_CONTRACT_BLOCKED
        contract["blockers"].append("scanner_spec_invalid")
        return contract

    if scanner_spec.get("verdict") != VERDICT_SPEC_READY:
        contract["verdict"] = VERDICT_DATA_CONTRACT_BLOCKED
        contract["blockers"].append("scanner_spec_not_ready")
        return contract

    if scanner_spec.get("alerts_and_reports_only") is not True:
        contract["verdict"] = VERDICT_DATA_CONTRACT_BLOCKED
        contract["blockers"].append("lane_constitution_violated")
        return contract

    contract["verdict"] = VERDICT_DATA_CONTRACT_READY
    contract["scanner_spec_verdict"] = scanner_spec.get("verdict")
    return contract


def build_arbitrage_data_contract() -> dict[str, Any]:
    """Build the data contract against the real scanner spec chain. Pure."""
    return record_arbitrage_data_contract(build_arbitrage_scanner_spec())


def validate_arbitrage_data_contract(contract: Any) -> dict[str, Any]:
    """Validate (read-only) a data contract's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract

    verdict = c.get("verdict")
    if verdict not in (VERDICT_DATA_CONTRACT_READY, VERDICT_DATA_CONTRACT_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_DATA_CONTRACT_BLOCKED and not c.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_DATA_CONTRACT_READY:
        if c.get("blockers"):
            errors.append("ready_with_blockers")
        if c.get("scanner_spec_verdict") != VERDICT_SPEC_READY:
            errors.append("ready_without_ready_scanner_spec")

    if c.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if c.get("roadmap_seq") != 2:
        errors.append("wrong_roadmap_seq")

    specs = c.get("staged_dataset_specs")
    if not isinstance(specs, dict) or set(specs) != set(STAGED_DATASET_SPECS):
        errors.append("dataset_specs_tampered")
    else:
        for kind, spec in specs.items():
            cols = spec.get("required_columns") or ()
            joined = " ".join(str(x).lower() for x in cols)
            for token in FORBIDDEN_FIELD_TOKENS:
                if token in joined:
                    errors.append("forbidden_field_in_spec:" + kind)
                    break
            pattern = str(spec.get("file_pattern", ""))
            if not pattern.startswith(STAGING_ROOT):
                errors.append("spec_outside_staging_root:" + kind)

    if tuple(c.get("allowed_symbols") or ()) != ALLOWED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(c.get("allowed_venue_labels") or ()) != ALLOWED_VENUE_LABELS:
        errors.append("venues_tampered")
    if len(c.get("validation_rules") or []) != len(VALIDATION_RULES):
        errors.append("validation_rules_incomplete")
    if tuple(c.get("forbidden_field_tokens") or ()) != FORBIDDEN_FIELD_TOKENS:
        errors.append("forbidden_tokens_weakened")
    if len(c.get("family_mapping") or []) != 6:
        errors.append("family_mapping_incomplete")
    if c.get("max_staleness_days_for_research") != MAX_STALENESS_DAYS_FOR_RESEARCH:
        errors.append("staleness_rule_tampered")

    for key, err in (
        ("venue_labels_are_not_connections", "venues_treated_as_connections"),
        ("staging_is_manual_operator_only", "staging_not_manual"),
        ("data_describes_markets_never_accounts", "account_data_allowed"),
        ("no_execution_fields_exist_in_any_spec", "execution_fields_allowed"),
        ("contract_reads_no_files", "contract_reads_files"),
        ("output_is_readiness_only_never_a_scan_result", "scan_result_claimed"),
        ("human_review_required", "human_review_dropped"),
    ):
        if c.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if c.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if c.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_data_contract_markdown(contract: Any) -> str:
    """Render the data contract as deterministic markdown. Pure string work."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Data Contract (STAGED DATA ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(c.get("verdict", "")))
    lines.append("- Lane: " + str(c.get("lane", "")) + " (roadmap seq "
                 + str(c.get("roadmap_seq", "")) + ")")
    lines.append("- Staging: manual operator only, under " + str(c.get("staging_root")))
    lines.append("- Venue labels are NOT connections; this lane connects to nothing")
    lines.append("- Output: readiness only, never a scan result")
    lines.append("- Next required action: " + str(c.get("next_required_action", "")))
    lines.append("")
    blockers = c.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED defines nothing usable)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Allowed labels")
    lines.append("- Symbols: " + ", ".join(c.get("allowed_symbols") or []))
    lines.append("- Venues: " + ", ".join(c.get("allowed_venue_labels") or []))
    lines.append("")
    lines.append("## Staged dataset specs")
    for kind, spec in (c.get("staged_dataset_specs") or {}).items():
        lines.append("### " + str(kind))
        lines.append("- File: " + str(spec.get("file_pattern")))
        lines.append("- Columns: " + ", ".join(spec.get("required_columns") or []))
        lines.append("- Families: " + ", ".join(spec.get("maps_to_families") or []))
    lines.append("")
    lines.append("## Validation rules")
    for r in c.get("validation_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Forbidden fields (any match refuses the whole file)")
    lines.append("- " + ", ".join(c.get("forbidden_field_tokens") or []))
    lines.append("")
    lines.append("## Forward mapping into future scanner/report contracts")
    for m in c.get("family_mapping") or []:
        lines.append("- " + str(m.get("dataset")) + " -> " + str(m.get("feeds"))
                     + ": " + str(m.get("future_report_fields")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
