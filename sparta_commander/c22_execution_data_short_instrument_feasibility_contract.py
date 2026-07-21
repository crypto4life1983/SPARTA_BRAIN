"""Candidate #22 -- EXECUTION DATA & SHORT-INSTRUMENT FEASIBILITY CONTRACT
(Phase B1: CONTRACT + PLANNING ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase B1 only):
HUMAN_APPROVED_BUILD_C22_FORWARD_AND_EXECUTION_DATA_READINESS_PHASE_B1.

Defines -- WITHOUT SELECTING -- the two candidate short implementations (linear perpetual
futures vs spot-margin short), the signal/execution basis-alignment review, the component-level
execution-cost evidence contract, the liquidity/execution feasibility requirements, and the
proposed (inactive) lifecycle gate sequence + tokens. Selects NO instrument, approves NO
cost base case, admits NO data, fetches NOTHING, runs NO replay/simulation. Bound to the
accepted REV1 replay specification SHA
9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867. Every capability flag is
pinned False; suggestion-only.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as _spec  # noqa: E501

EXE_SCHEMA_VERSION = 1
EXE_MODE = "RESEARCH_ONLY"
EXE_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "execution_data_short_feasibility_b1_v1"
PHASE_B1_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_FORWARD_AND_EXECUTION_DATA_READINESS_PHASE_B1"
BOUND_SPEC_SHA256 = "9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867"

VERDICT_READY = "C22_EXECUTION_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_EXECUTION_DATA_CONTRACT_BLOCKED"

SHORT_INSTRUMENT_STATUS = "UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION"

# --- Option 1: linear perpetual futures ------------------------------------------------------
OPTION_1_PERP_REQUIREMENTS = (
    "explicit_venue", "exact_contract_symbol", "quote_asset", "settlement_asset",
    "instrument_start_date", "historical_ohlc_source", "historical_funding_rate_source",
    "funding_timestamps_and_payment_intervals", "trading_fee_schedule", "tick_size", "lot_size",
    "symbol_mapping_to_gc_signal_asset", "delisting_and_contract_migration_history",
    "availability_on_every_signal_and_holding_date")

# --- Option 2: spot-margin short -------------------------------------------------------------
OPTION_2_MARGIN_REQUIREMENTS = (
    "explicit_venue", "spot_symbol", "margin_mode", "borrowable_asset",
    "historical_borrow_availability", "historical_borrow_rate_source", "borrow_charging_interval",
    "trading_fee_schedule", "symbol_mapping", "suspension_and_delisting_history",
    "availability_on_every_signal_and_holding_date")

FAIL_CLOSED_WHEN_ANY_EVIDENCE_ABSENT = True

# hard prohibitions (never silently done)
PROHIBITIONS = (
    "silently_using_spot_ohlc_for_perpetual_fills",
    "silently_using_perpetual_ohlc_for_spot_margin_fills",
    "assuming_borrow_availability",
    "assuming_zero_funding",
    "assuming_zero_basis",
    "substituting_a_currently_available_instrument_for_one_that_did_not_exist_historically")

# --- signal vs execution basis alignment -----------------------------------------------------
BASIS_ALIGNMENT_DIAGNOSTIC_FIELDS = (
    "signal_price", "execution_reference_price", "absolute_difference", "percentage_basis",
    "timestamp_difference", "symbol_map_confidence", "approved_adjustment_rule_if_any")

# --- component-level execution cost contract -------------------------------------------------
COST_COMPONENTS = (
    "entry_exchange_fee", "exit_exchange_fee", "entry_half_spread", "exit_half_spread",
    "entry_slippage", "exit_slippage", "funding_or_borrow_cost", "exceptional_exit_cost",
    "basis_adjustment_cost_if_applicable")
COST_RESULT_LEVELS = ("gross", "transaction_cost_only_net", "fully_net_after_funding_or_borrow")
THIRTY_SEVEN_BPS_STATUS = "SENSITIVITY_CASE_NOT_BASE_CASE"
COST_BASE_CASE_EVIDENCE_FIELDS = (
    "source", "effective_date", "tier_or_volume_assumption", "maker_or_taker_assumption",
    "instrument", "venue", "deterministic_value_or_formula", "sha256_or_immutable_source_ref")

# --- liquidity / execution feasibility -------------------------------------------------------
EXECUTION_FEASIBILITY_RULES = {
    "next_executable_bar_reference": "entries/exits fill at the OPEN of the next executable "
                                     "market bar after the evaluation date",
    "exits_before_entries": True,
    "deterministic_ordering": ["decision_date_ascending", "market_rank_ascending",
                               "stable_asset_identifier_ascending"],
    "one_position_per_asset": True,
    "no_simultaneous_long_and_short_same_asset": True,
    "max_gross_exposure_pct_nav": 100.0,
    "insufficient_nav_deterministic_rejection": True,
    "no_proportional_resizing": True,
    "missing_next_bar_fail_closed": True,
    "no_invented_fill": True,
    "partial_fill_policy": "UNRESOLVED unless supported by historical data",
}
LIQUIDITY_FEASIBILITY_EVIDENCE = (
    "daily_notional_volume", "order_size_as_pct_of_volume", "spread", "minimum_order_size",
    "lot_size", "price_increment", "instrument_availability")


def _proposed_lifecycle_gates() -> list:
    return [
        {"gate": "C22_FORWARD_EXIT_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the forward exit-only data contract",
         "human_token": "HUMAN_DECISION_C22_FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE"},
        {"gate": "C22_EXECUTION_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the execution-data / short-feasibility contract",
         "human_token": "HUMAN_DECISION_C22_EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE"},
        {"gate": "C22_EXIT_ONLY_DATASET_READY_FOR_ADMISSION_REVIEW",
         "purpose": "human reviews the frozen exit-only snapshot dataset for admission",
         "human_token": "HUMAN_DECISION_C22_EXIT_ONLY_DATASET_ADMIT_OR_REJECT"},
        {"gate": "C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION",
         "purpose": "human selects perp vs spot-margin with full feasibility evidence",
         "human_token": "HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT"},
        {"gate": "C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews/freezes the component-level cost base case",
         "human_token": "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE"},
        {"gate": "C22_DRY_RUN_SPEC_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the no-PnL dry-run spec (only after all above accepted)",
         "human_token": "HUMAN_DECISION_C22_DRY_RUN_SPEC_ACCEPT_OR_REVISE"},
    ]


_CAPABILITY_FLAGS_FALSE = (
    "network", "fetch", "import", "dataset_mutation", "forward_data_admission",
    "instrument_selection", "cost_base_case_approval", "basis_adjustment_selection", "replay",
    "simulation", "dry_run", "token_issuance", "token_consumption", "lifecycle_advancement",
    "commit", "push", "assumes_borrow_availability", "assumes_zero_funding",
    "assumes_zero_basis", "substitutes_nonexistent_instrument",
)


def build_execution_data_contract() -> dict:
    """PURE. Assemble the execution-data / short-instrument feasibility contract. Selects NO
    instrument, approves NO base case, writes NOTHING."""
    blockers: list = []
    if _spec.build_replay_spec()["spec_sha256"] != BOUND_SPEC_SHA256:
        blockers.append("bound_spec_sha_mismatch")

    contract: dict[str, Any] = {
        "contract": "c22_execution_data_and_short_instrument_feasibility",
        "schema_version": EXE_SCHEMA_VERSION, "builder_version": BUILDER_VERSION,
        "mode": EXE_MODE, "lane": EXE_LANE, "candidate_id": _spec._v2._v1.CANDIDATE_ID,
        "phase": "B1_CONTRACT_AND_PLANNING_ONLY", "phase_b1_build_token": PHASE_B1_BUILD_TOKEN,
        "bound_replay_spec_sha256": BOUND_SPEC_SHA256,
        "short_instrument_status": SHORT_INSTRUMENT_STATUS,
        "instrument_selected": False,
        "option_1_linear_perpetual_futures": {
            "requirements": list(OPTION_1_PERP_REQUIREMENTS),
            "fail_closed_when_any_absent": FAIL_CLOSED_WHEN_ANY_EVIDENCE_ABSENT},
        "option_2_spot_margin_short": {
            "requirements": list(OPTION_2_MARGIN_REQUIREMENTS),
            "fail_closed_when_any_absent": FAIL_CLOSED_WHEN_ANY_EVIDENCE_ABSENT},
        "prohibitions": list(PROHIBITIONS),
        "long_and_short_price_series_stated_separately": True,
        "basis_alignment_review_required": True,
        "basis_alignment_diagnostic_fields": list(BASIS_ALIGNMENT_DIAGNOSTIC_FIELDS),
        "basis_adjustment_selected": False,
        "cost_components": list(COST_COMPONENTS),
        "cost_result_levels": list(COST_RESULT_LEVELS),
        "thirty_seven_bps_status": THIRTY_SEVEN_BPS_STATUS,
        "thirty_seven_bps_is_base_case": False,
        "cost_base_case_approved": False,
        "cost_base_case_evidence_fields": list(COST_BASE_CASE_EVIDENCE_FIELDS),
        "execution_feasibility_rules": EXECUTION_FEASIBILITY_RULES,
        "liquidity_feasibility_evidence": list(LIQUIDITY_FEASIBILITY_EVIDENCE),
        "proposed_lifecycle_gates": _proposed_lifecycle_gates(),
        "lifecycle_gates_activated": False,
        "human_review_required": True,
        "verdict": (VERDICT_READY if not blockers else VERDICT_BLOCKED),
        "blockers": blockers,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        contract[flag] = False
    contract["contract_sha256"] = _hashlib.sha256(
        canonical_contract_bytes(contract)).hexdigest()
    return contract


def canonical_contract_bytes(contract: dict) -> bytes:
    payload = {k: v for k, v in contract.items() if k != "contract_sha256"}
    return _json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def validate_execution_data_contract(c: Any) -> dict:
    """Anti-tamper validator. Valid only when research-only + B1 contract-only, bound to the
    accepted spec SHA, short instrument UNRESOLVED + not selected, both options fully specified
    + fail-closed, prohibitions present, basis review required + not selected, costs
    componentized with 37bps sensitivity-only + base case not approved, liquidity/feasibility
    present, lifecycle gates proposed but inactive, every capability flag False."""
    f: list = []
    if not isinstance(c, dict):
        return {"valid": False, "failures": ["contract_not_a_dict"]}
    if c.get("mode") != EXE_MODE:
        f.append("mode_not_research_only")
    if c.get("phase") != "B1_CONTRACT_AND_PLANNING_ONLY":
        f.append("not_b1_contract_only")
    if c.get("bound_replay_spec_sha256") != BOUND_SPEC_SHA256:
        f.append("bound_spec_sha_wrong")
    if c.get("short_instrument_status") != SHORT_INSTRUMENT_STATUS:
        f.append("short_instrument_not_unresolved")
    if c.get("instrument_selected") is not False:
        f.append("instrument_wrongly_selected")
    o1 = (c.get("option_1_linear_perpetual_futures") or {}).get("requirements") or []
    o2 = (c.get("option_2_spot_margin_short") or {}).get("requirements") or []
    for r in OPTION_1_PERP_REQUIREMENTS:
        if r not in o1:
            f.append("perp_requirement_missing:%s" % r)
    for r in OPTION_2_MARGIN_REQUIREMENTS:
        if r not in o2:
            f.append("margin_requirement_missing:%s" % r)
    for p in PROHIBITIONS:
        if p not in (c.get("prohibitions") or []):
            f.append("prohibition_missing:%s" % p)
    if c.get("basis_alignment_review_required") is not True:
        f.append("basis_review_not_required")
    if c.get("basis_adjustment_selected") is not False:
        f.append("basis_adjustment_wrongly_selected")
    for comp in COST_COMPONENTS:
        if comp not in (c.get("cost_components") or []):
            f.append("cost_component_missing:%s" % comp)
    if "funding_or_borrow_cost" not in (c.get("cost_components") or []):
        f.append("funding_or_borrow_omitted")
    for lvl in COST_RESULT_LEVELS:
        if lvl not in (c.get("cost_result_levels") or []):
            f.append("cost_result_level_missing:%s" % lvl)
    if c.get("thirty_seven_bps_status") != THIRTY_SEVEN_BPS_STATUS:
        f.append("37bps_not_sensitivity_only")
    if c.get("thirty_seven_bps_is_base_case") is not False:
        f.append("37bps_wrongly_base_case")
    if c.get("cost_base_case_approved") is not False:
        f.append("cost_base_case_wrongly_approved")
    for fld in COST_BASE_CASE_EVIDENCE_FIELDS:
        if fld not in (c.get("cost_base_case_evidence_fields") or []):
            f.append("cost_evidence_field_missing:%s" % fld)
    efr = c.get("execution_feasibility_rules") or {}
    if efr.get("exits_before_entries") is not True or \
            efr.get("no_proportional_resizing") is not True or \
            efr.get("missing_next_bar_fail_closed") is not True or \
            efr.get("insufficient_nav_deterministic_rejection") is not True:
        f.append("execution_feasibility_rules_wrong")
    if efr.get("deterministic_ordering") != ["decision_date_ascending", "market_rank_ascending",
                                             "stable_asset_identifier_ascending"]:
        f.append("execution_ordering_wrong")
    for ev in LIQUIDITY_FEASIBILITY_EVIDENCE:
        if ev not in (c.get("liquidity_feasibility_evidence") or []):
            f.append("liquidity_evidence_missing:%s" % ev)
    gates = [g.get("gate") for g in (c.get("proposed_lifecycle_gates") or [])]
    expected_gates = [
        "C22_FORWARD_EXIT_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
        "C22_EXECUTION_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW",
        "C22_EXIT_ONLY_DATASET_READY_FOR_ADMISSION_REVIEW",
        "C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION",
        "C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW",
        "C22_DRY_RUN_SPEC_READY_FOR_HUMAN_REVIEW"]
    if gates != expected_gates:
        f.append("proposed_lifecycle_gates_wrong")
    if c.get("lifecycle_gates_activated") is not False:
        f.append("lifecycle_gates_wrongly_activated")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if c.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if c.get("contract_sha256") and c["contract_sha256"] != _hashlib.sha256(
            canonical_contract_bytes(c)).hexdigest():
        f.append("contract_hash_mismatch")
    if c.get("verdict") == VERDICT_READY and c.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}
