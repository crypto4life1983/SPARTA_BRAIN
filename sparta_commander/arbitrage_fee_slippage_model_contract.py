"""SPARTA Arbitrage Factory V1 - FEE / SLIPPAGE MODEL Contract (READ-ONLY).

Roadmap seq 3 of the Arbitrage Factory V1 lane: the model that makes "net edge"
HONEST before any scanner exists. Most paper arbitrage edges die the moment
fees, spread, slippage, funding, and transfer costs are charged against them --
so this lane charges them FIRST, conservatively, and refuses to evaluate
anything it cannot cost.

The model is pure rule text plus pure arithmetic:

    net_edge_bps = gross_edge_bps
                   - 2 x taker_fee_bps          (taker BOTH legs, never maker)
                   - spread_cost_bps            (full half-spread paid per leg)
                   - slippage_bps               (from staged depth, never zero)
                   - funding_adjustment_bps     (staged funding only, no forecast)
                   - withdrawal_amortization_bps(flat venue fee, labels only)

Classification (research readiness inputs for the future scanner/report
contracts, NEVER a trade signal):
    PASS  if net_edge_bps >= MIN_NET_EDGE_PASS_BPS
    WATCH if 0 <= net_edge_bps < MIN_NET_EDGE_PASS_BPS
    FAIL  otherwise -- and when in doubt, FAIL.

Inputs come ONLY from the seq-2 data contract's staged shapes (fee_schedule and
liquidity_depth, plus funding_rates for the funding term). This module aligns
to those shapes at import time and reads NO file, fetches NOTHING, connects to
NOTHING. Account/credential/order/position fields are refused outright via the
data contract's own forbidden-token screen.

Public API:
  - MODEL_SCHEMA_VERSION / MODEL_LABEL / MODEL_MODE
  - VERDICT_MODEL_READY / VERDICT_MODEL_BLOCKED
  - COST_MODEL_RULES / CONSERVATIVE_ASSUMPTIONS / VALIDATION_RULES
  - REQUIRED_FEE_FIELDS / REQUIRED_LIQUIDITY_FIELDS / MODEL_INPUT_KINDS
  - MIN_NET_EDGE_PASS_BPS / MAX_DEPTH_UTILIZATION_PCT / NEXT_REQUIRED_ACTION
  - get_arbitrage_fee_slippage_model_label()
  - record_arbitrage_fee_slippage_model(data_contract)
  - build_arbitrage_fee_slippage_model()
  - validate_arbitrage_fee_slippage_model(model)
  - validate_model_input_descriptor(kind, columns)
  - estimate_net_edge_bps(inputs) / classify_net_edge(net_edge_bps)
  - render_arbitrage_fee_slippage_model_markdown(model)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.arbitrage_data_contract import (
    FORBIDDEN_FIELD_TOKENS,
    MAX_STALENESS_DAYS_FOR_RESEARCH,
    STAGED_DATASET_SPECS,
    VERDICT_DATA_CONTRACT_READY,
    build_arbitrage_data_contract,
    validate_arbitrage_data_contract,
    validate_staged_dataset_descriptor,
)

MODEL_SCHEMA_VERSION = "arbitrage_fee_slippage_model_contract.v1"
MODEL_LABEL = (
    "SPARTA Arbitrage Factory V1 Fee/Slippage Model (READ-ONLY, MODEL ONLY)"
)
MODEL_MODE = "RESEARCH_ONLY"

VERDICT_MODEL_READY = "ARBITRAGE_FEE_SLIPPAGE_MODEL_READY"
VERDICT_MODEL_BLOCKED = "ARBITRAGE_FEE_SLIPPAGE_MODEL_BLOCKED"

# Roadmap seq 4: the alert/report schema, under its own human approval.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_ALERT_REPORT_SCHEMA"

# The only staged dataset kinds this model may take inputs from.
MODEL_INPUT_KINDS = ("fee_schedule", "liquidity_depth", "funding_rates")

# Aligned at import time to the seq-2 data contract's single source of truth.
REQUIRED_FEE_FIELDS = STAGED_DATASET_SPECS["fee_schedule"]["required_columns"]
REQUIRED_LIQUIDITY_FIELDS = (
    STAGED_DATASET_SPECS["liquidity_depth"]["required_columns"]
)
assert "taker_fee_pct" in REQUIRED_FEE_FIELDS
assert "maker_fee_pct" in REQUIRED_FEE_FIELDS
assert "withdrawal_flat_fee" in REQUIRED_FEE_FIELDS
assert "spread_bps" in REQUIRED_LIQUIDITY_FIELDS
assert "bid_depth_usd_10bps" in REQUIRED_LIQUIDITY_FIELDS

# Thresholds (research readiness, never trade triggers).
MIN_NET_EDGE_PASS_BPS = 10.0
MIN_NET_EDGE_WATCH_BPS = 0.0
# A research evaluation may never assume consuming more than this share of the
# staged top-of-book depth; beyond it, slippage is declared not estimable.
MAX_DEPTH_UTILIZATION_PCT = 10.0

# The model's cost rules, as enforceable rule text.
COST_MODEL_RULES = (
    "fees_use_taker_rate_on_both_legs_maker_fills_are_never_assumed",
    "funding_uses_staged_realized_rates_only_never_a_forward_forecast",
    "withdrawal_and_transfer_costs_are_flat_venue_label_fees_no_chain_lookup",
    "spread_cost_charges_the_full_half_spread_per_leg",
    "slippage_comes_from_staged_depth_and_is_never_assumed_zero",
    "net_edge_subtracts_every_cost_before_any_classification",
    "classification_is_research_readiness_input_never_a_trade_signal",
)

CONSERVATIVE_ASSUMPTIONS = (
    "every_ambiguous_cost_resolves_to_the_more_expensive_choice",
    "depth_utilization_above_the_cap_makes_slippage_not_estimable",
    "stale_fee_or_depth_data_refuses_the_evaluation_outright",
    "unknown_symbol_or_venue_label_refuses_the_evaluation_outright",
    "missing_any_cost_component_refuses_no_cost_ever_defaults_to_zero",
    "when_in_doubt_the_classification_is_FAIL",
)

VALIDATION_RULES = (
    "fee_rows_must_exist_for_every_venue_symbol_pair_evaluated",
    "fees_spreads_and_depths_must_be_finite_and_non_negative",
    "liquidity_rows_older_than_max_staleness_refuse_the_evaluation",
    "zero_or_negative_depth_refuses_slippage_estimation",
    "forbidden_account_credential_order_position_fields_refuse_whole_inputs",
    "inputs_come_only_from_the_seq2_staged_dataset_shapes",
)

_REQUIRED_EDGE_INPUTS = (
    "gross_edge_bps",
    "taker_fee_bps",
    "spread_cost_bps",
    "slippage_bps",
    "funding_adjustment_bps",
    "withdrawal_amortization_bps",
)


def get_arbitrage_fee_slippage_model_label() -> str:
    """Human label for the recognized fee/slippage model contract."""
    return MODEL_LABEL


def validate_model_input_descriptor(kind: Any, columns: Any) -> dict[str, Any]:
    """Validate (read-only, in-memory) a proposed model input descriptor.
    Only the three model input kinds are accepted; everything else -- and any
    forbidden account/credential/order/position field -- refuses. Pure."""
    if kind not in MODEL_INPUT_KINDS:
        return {"acceptable": False,
                "errors": ["kind_not_a_model_input:" + str(kind)]}
    return validate_staged_dataset_descriptor(kind, columns)


def estimate_net_edge_bps(inputs: Any) -> dict[str, Any]:
    """PURE arithmetic: charge every cost against the gross edge. Returns
    {"computable": bool, "net_edge_bps": float|None, "errors": [...]}.
    Refuses missing, non-numeric, negative-cost, or forbidden inputs; a cost
    can never default to zero. Never raises."""
    if not isinstance(inputs, dict):
        return {"computable": False, "net_edge_bps": None,
                "errors": ["inputs_not_a_dict"]}

    errors: list[str] = []
    for key in inputs:
        lowered = str(key).lower()
        for token in FORBIDDEN_FIELD_TOKENS:
            if token in lowered:
                errors.append("forbidden_input:" + str(key))
                break
    if errors:
        return {"computable": False, "net_edge_bps": None, "errors": errors}

    values: dict[str, float] = {}
    for name in _REQUIRED_EDGE_INPUTS:
        raw = inputs.get(name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            errors.append("missing_or_non_numeric:" + name)
            continue
        value = float(raw)
        if value != value or value in (float("inf"), float("-inf")):
            errors.append("non_finite:" + name)
            continue
        if name != "gross_edge_bps" and name != "funding_adjustment_bps" and value < 0:
            # costs are charges; a negative cost would secretly add edge
            errors.append("negative_cost:" + name)
            continue
        values[name] = value
    if errors:
        return {"computable": False, "net_edge_bps": None, "errors": errors}

    depth_utilization = inputs.get("depth_utilization_pct")
    if isinstance(depth_utilization, (int, float)) and not isinstance(
        depth_utilization, bool
    ):
        if float(depth_utilization) > MAX_DEPTH_UTILIZATION_PCT:
            return {"computable": False, "net_edge_bps": None,
                    "errors": ["depth_utilization_above_cap_slippage_not_estimable"]}

    net = (
        values["gross_edge_bps"]
        - 2.0 * values["taker_fee_bps"]
        - values["spread_cost_bps"]
        - values["slippage_bps"]
        - values["funding_adjustment_bps"]
        - values["withdrawal_amortization_bps"]
    )
    return {"computable": True, "net_edge_bps": net, "errors": []}


def classify_net_edge(net_edge_bps: Any) -> str:
    """Classify a computed net edge into the research readiness states.
    NEVER a trade signal. Anything non-numeric or doubtful is FAIL. Pure."""
    if not isinstance(net_edge_bps, (int, float)) or isinstance(net_edge_bps, bool):
        return "FAIL"
    value = float(net_edge_bps)
    if value != value or value in (float("inf"), float("-inf")):
        return "FAIL"
    if value >= MIN_NET_EDGE_PASS_BPS:
        return "PASS"
    if value >= MIN_NET_EDGE_WATCH_BPS:
        return "WATCH"
    return "FAIL"


def _base_model() -> dict[str, Any]:
    return {
        "schema_version": MODEL_SCHEMA_VERSION,
        "label": MODEL_LABEL,
        "mode": MODEL_MODE,
        "lane": "arbitrage_factory_v1",
        "roadmap_seq": 3,
        "verdict": None,
        "blockers": [],
        "data_contract_verdict": None,
        "model_input_kinds": list(MODEL_INPUT_KINDS),
        "required_fee_fields": list(REQUIRED_FEE_FIELDS),
        "required_liquidity_fields": list(REQUIRED_LIQUIDITY_FIELDS),
        "cost_model_rules": list(COST_MODEL_RULES),
        "conservative_assumptions": list(CONSERVATIVE_ASSUMPTIONS),
        "validation_rules": list(VALIDATION_RULES),
        "forbidden_field_tokens": list(FORBIDDEN_FIELD_TOKENS),
        "min_net_edge_pass_bps": MIN_NET_EDGE_PASS_BPS,
        "min_net_edge_watch_bps": MIN_NET_EDGE_WATCH_BPS,
        "max_depth_utilization_pct": MAX_DEPTH_UTILIZATION_PCT,
        "max_staleness_days_for_research": MAX_STALENESS_DAYS_FOR_RESEARCH,
        # Constitution, stated structurally:
        "classification_is_research_readiness_not_a_trade_signal": True,
        "costs_never_default_to_zero": True,
        "withdrawal_costs_are_labels_only_no_chain_lookup": True,
        "model_reads_no_files": True,
        "output_is_model_readiness_only": True,
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


def record_arbitrage_fee_slippage_model(data_contract: Any) -> dict[str, Any]:
    """Record the fee/slippage model, gated on a READY, valid seq-2 data
    contract. PURE: never raises, reads no file, connects to nothing."""
    model = _base_model()

    if not isinstance(data_contract, dict):
        model["verdict"] = VERDICT_MODEL_BLOCKED
        model["blockers"].append("data_contract_missing")
        return model

    validation = validate_arbitrage_data_contract(data_contract)
    if not validation.get("valid"):
        model["verdict"] = VERDICT_MODEL_BLOCKED
        model["blockers"].append("data_contract_invalid")
        return model

    if data_contract.get("verdict") != VERDICT_DATA_CONTRACT_READY:
        model["verdict"] = VERDICT_MODEL_BLOCKED
        model["blockers"].append("data_contract_not_ready")
        return model

    specs = data_contract.get("staged_dataset_specs") or {}
    for kind in MODEL_INPUT_KINDS:
        if kind not in specs:
            model["verdict"] = VERDICT_MODEL_BLOCKED
            model["blockers"].append("model_input_kind_missing_from_data_contract:" + kind)
            return model

    model["verdict"] = VERDICT_MODEL_READY
    model["data_contract_verdict"] = data_contract.get("verdict")
    return model


def build_arbitrage_fee_slippage_model() -> dict[str, Any]:
    """Build the model against the real seq 0 -> 1 -> 2 chain. Pure."""
    return record_arbitrage_fee_slippage_model(build_arbitrage_data_contract())


def validate_arbitrage_fee_slippage_model(model: Any) -> dict[str, Any]:
    """Validate (read-only) a model's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return {"valid": False, "errors": ["model_not_a_dict"]}
    m = model

    verdict = m.get("verdict")
    if verdict not in (VERDICT_MODEL_READY, VERDICT_MODEL_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_MODEL_BLOCKED and not m.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_MODEL_READY:
        if m.get("blockers"):
            errors.append("ready_with_blockers")
        if m.get("data_contract_verdict") != VERDICT_DATA_CONTRACT_READY:
            errors.append("ready_without_ready_data_contract")

    if m.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if m.get("roadmap_seq") != 3:
        errors.append("wrong_roadmap_seq")

    if tuple(m.get("model_input_kinds") or ()) != MODEL_INPUT_KINDS:
        errors.append("input_kinds_tampered")
    if tuple(m.get("required_fee_fields") or ()) != REQUIRED_FEE_FIELDS:
        errors.append("fee_fields_diverge_from_data_contract")
    if tuple(m.get("required_liquidity_fields") or ()) != REQUIRED_LIQUIDITY_FIELDS:
        errors.append("liquidity_fields_diverge_from_data_contract")
    if tuple(m.get("cost_model_rules") or ()) != COST_MODEL_RULES:
        errors.append("cost_rules_tampered")
    if tuple(m.get("conservative_assumptions") or ()) != CONSERVATIVE_ASSUMPTIONS:
        errors.append("conservative_assumptions_weakened")
    if len(m.get("validation_rules") or []) != len(VALIDATION_RULES):
        errors.append("validation_rules_incomplete")
    if tuple(m.get("forbidden_field_tokens") or ()) != FORBIDDEN_FIELD_TOKENS:
        errors.append("forbidden_tokens_weakened")

    pass_bps = m.get("min_net_edge_pass_bps")
    watch_bps = m.get("min_net_edge_watch_bps")
    if not (isinstance(pass_bps, (int, float)) and isinstance(watch_bps, (int, float))
            and pass_bps > watch_bps >= 0):
        errors.append("thresholds_not_conservative")
    util = m.get("max_depth_utilization_pct")
    if not isinstance(util, (int, float)) or not (0 < util <= MAX_DEPTH_UTILIZATION_PCT):
        errors.append("depth_utilization_cap_loosened")

    for key, err in (
        ("classification_is_research_readiness_not_a_trade_signal",
         "trade_signal_claimed"),
        ("costs_never_default_to_zero", "zero_cost_default_allowed"),
        ("withdrawal_costs_are_labels_only_no_chain_lookup", "chain_lookup_allowed"),
        ("model_reads_no_files", "model_reads_files"),
        ("output_is_model_readiness_only", "output_overclaims"),
        ("human_review_required", "human_review_dropped"),
    ):
        if m.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if m.get(key) is not True:
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
        if m.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_fee_slippage_model_markdown(model: Any) -> str:
    """Render the model contract as deterministic markdown. Pure string work."""
    m = model if isinstance(model, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Fee/Slippage Model (MODEL ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(m.get("verdict", "")))
    lines.append("- Lane: " + str(m.get("lane", "")) + " (roadmap seq "
                 + str(m.get("roadmap_seq", "")) + ")")
    lines.append("- Classification is a research readiness input, NEVER a trade signal")
    lines.append("- Costs never default to zero; when in doubt, FAIL")
    lines.append("- Next required action: " + str(m.get("next_required_action", "")))
    lines.append("")
    blockers = m.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED defines nothing usable)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Net edge formula (all costs charged before classification)")
    lines.append("- net = gross - 2*taker_fee - spread_cost - slippage "
                 "- funding_adjustment - withdrawal_amortization (all bps)")
    lines.append("- PASS >= " + str(m.get("min_net_edge_pass_bps")) + " bps; WATCH >= "
                 + str(m.get("min_net_edge_watch_bps")) + " bps; FAIL otherwise")
    lines.append("- Depth utilization cap: " + str(m.get("max_depth_utilization_pct"))
                 + "% of staged top-of-book depth")
    lines.append("")
    lines.append("## Cost model rules")
    for r in m.get("cost_model_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Conservative assumptions")
    for a in m.get("conservative_assumptions") or []:
        lines.append("- " + str(a))
    lines.append("")
    lines.append("## Validation rules")
    for r in m.get("validation_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Required staged fields (aligned to the seq-2 data contract)")
    lines.append("- fee_schedule: " + ", ".join(m.get("required_fee_fields") or []))
    lines.append("- liquidity_depth: "
                 + ", ".join(m.get("required_liquidity_fields") or []))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
