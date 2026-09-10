"""Candidate #22 -- COST ENGINE INTERFACES (PURE; RESEARCH ONLY; NO DECISIVE BASE CASE).

Arithmetic for the disaggregated cost components already frozen in the C22 execution-data
contract (COST_COMPONENTS / COST_RESULT_LEVELS). Supports, SEPARATELY: trading fees, entry
slippage, exit slippage, perpetual funding, spot-margin borrow.

Three model statuses exist and are never confused:
  * ZERO_COST_LIFECYCLE_ONLY   -- used by the no-P&L dry run (all components 0)
  * SENSITIVITY_ONLY           -- the historical 37 bps round-trip convention (27 fee + 10 slippage)
                                  retained as a LABELLED sensitivity case; it is NOT a base case
  * FROZEN_BASE_CASE           -- exists only once a human freezes component-level evidence; this
                                  module deliberately provides no such model (frozen_base_case()
                                  returns a NOT_FROZEN record).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as _exec

COST_COMPONENTS = _exec.COST_COMPONENTS
RESULT_LEVELS = _exec.COST_RESULT_LEVELS
SENSITIVITY_37BPS_STATUS = _exec.THIRTY_SEVEN_BPS_STATUS       # SENSITIVITY_CASE_NOT_BASE_CASE

MODEL_STATUS_ZERO = "ZERO_COST_LIFECYCLE_ONLY"
MODEL_STATUS_SENSITIVITY = "SENSITIVITY_ONLY"
MODEL_STATUS_FROZEN = "FROZEN_BASE_CASE"
BASE_CASE_NOT_FROZEN = "C22_COST_BASE_CASE_NOT_FROZEN"

FUNDING_MODE_NONE = "NONE"
FUNDING_MODE_PERP_SERIES = "PERP_FUNDING_SERIES"
BORROW_MODE_NONE = "NONE"
BORROW_MODE_RATE_SERIES = "SPOT_MARGIN_BORROW_RATE_SERIES"

ZERO_COST_MODEL = {"model_id": "c22_zero_cost_lifecycle_only_v1", "status": MODEL_STATUS_ZERO,
                   "trading_fee_bps_per_side": 0.0, "entry_slippage_bps": 0.0, "exit_slippage_bps": 0.0,
                   "funding_mode": FUNDING_MODE_NONE, "borrow_mode": BORROW_MODE_NONE,
                   "decisive": False}

SENSITIVITY_37BPS_MODEL = {"model_id": "c22_37bps_round_trip_sensitivity_v1", "status": MODEL_STATUS_SENSITIVITY,
                           "label": SENSITIVITY_37BPS_STATUS,
                           "trading_fee_bps_per_side": 13.5, "entry_slippage_bps": 5.0, "exit_slippage_bps": 5.0,
                           "round_trip_bps": 37.0,
                           "funding_mode": FUNDING_MODE_NONE, "borrow_mode": BORROW_MODE_NONE,
                           "decisive": False}


def frozen_base_case() -> dict:
    """No frozen base case exists. Returns a NOT_FROZEN record; never a usable model."""
    return {"status": BASE_CASE_NOT_FROZEN, "decisive": False, "model": None,
            "required_gate": "C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW",
            "required_token": "HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE"}


def validate_model(model: dict) -> dict:
    failures = []
    for k in ("model_id", "status", "trading_fee_bps_per_side", "entry_slippage_bps", "exit_slippage_bps",
              "funding_mode", "borrow_mode", "decisive"):
        if k not in model:
            failures.append("missing:%s" % k)
    if model.get("status") not in (MODEL_STATUS_ZERO, MODEL_STATUS_SENSITIVITY, MODEL_STATUS_FROZEN):
        failures.append("unknown_status")
    if model.get("status") != MODEL_STATUS_FROZEN and model.get("decisive"):
        failures.append("non_frozen_model_cannot_be_decisive")
    if model.get("status") == MODEL_STATUS_SENSITIVITY and model.get("label") != SENSITIVITY_37BPS_STATUS:
        failures.append("sensitivity_model_must_carry_sensitivity_label")
    for k in ("trading_fee_bps_per_side", "entry_slippage_bps", "exit_slippage_bps"):
        v = model.get(k)
        if not isinstance(v, (int, float)) or v < 0:
            failures.append("negative_or_non_numeric:%s" % k)
    return {"valid": not failures, "failures": failures}


def trading_fee(notional: float, model: dict) -> float:
    return abs(float(notional)) * float(model["trading_fee_bps_per_side"]) / 10000.0


def slippage_cost(notional: float, model: dict, leg: str) -> float:
    if leg not in ("entry", "exit"):
        raise ValueError("leg_must_be_entry_or_exit")
    return abs(float(notional)) * float(model["%s_slippage_bps" % leg]) / 10000.0


def funding_cost(side: str, notional: float, funding_rates: list) -> float:
    """Perpetual funding over a list of (interval_id, rate) tuples. Positive rate = longs pay
    shorts, so a SHORT receives (negative cost) and a LONG pays. Empty list -> 0.0 (the caller
    must treat an EMPTY series on a required date as MISSING evidence, not as zero funding)."""
    total = 0.0
    for _, rate in funding_rates:
        paid = abs(float(notional)) * float(rate)
        total += paid if side == "LONG" else -paid
    return total


def borrow_cost(notional: float, borrow_rates: list) -> float:
    """Spot-margin borrow over (interval_id, rate_per_interval) tuples; always a cost."""
    return sum(abs(float(notional)) * float(r) for _, r in borrow_rates)


def cost_breakdown(side: str, entry_notional: float, exit_notional: float, model: dict,
                   funding_rates=None, borrow_rates=None, exceptional_exit_cost: float = 0.0,
                   basis_adjustment_cost: float = 0.0) -> dict:
    """Per-trade components named EXACTLY as the frozen contract's COST_COMPONENTS, plus the
    three frozen result levels (gross / transaction_cost_only_net / fully_net_after_funding_or_borrow)
    expressed as total cost at each level."""
    if validate_model(model)["valid"] is False:
        raise ValueError("invalid_cost_model")
    comp = {
        "entry_exchange_fee": trading_fee(entry_notional, model),
        "exit_exchange_fee": trading_fee(exit_notional, model),
        "entry_half_spread": 0.0,
        "exit_half_spread": 0.0,
        "entry_slippage": slippage_cost(entry_notional, model, "entry"),
        "exit_slippage": slippage_cost(exit_notional, model, "exit"),
        "funding_or_borrow_cost": (funding_cost(side, entry_notional, funding_rates or [])
                                   + borrow_cost(entry_notional, borrow_rates or [])),
        "exceptional_exit_cost": float(exceptional_exit_cost),
        "basis_adjustment_cost_if_applicable": float(basis_adjustment_cost),
    }
    assert tuple(comp.keys()) == tuple(COST_COMPONENTS), "component_names_drifted_from_frozen_contract"
    tx_only = (comp["entry_exchange_fee"] + comp["exit_exchange_fee"] + comp["entry_half_spread"]
               + comp["exit_half_spread"] + comp["entry_slippage"] + comp["exit_slippage"])
    fully = tx_only + comp["funding_or_borrow_cost"] + comp["exceptional_exit_cost"] + comp["basis_adjustment_cost_if_applicable"]
    return {"model_id": model["model_id"], "model_status": model["status"], "decisive": bool(model.get("decisive")),
            "components": comp,
            "cost_at_level": {"gross": 0.0, "transaction_cost_only_net": tx_only,
                              "fully_net_after_funding_or_borrow": fully}}


def apply_slippage_to_price(price: float, side: str, leg: str, model: dict) -> float:
    """Executable price after slippage: buys pay up, sells receive less. LONG entry / SHORT exit
    are buys; LONG exit / SHORT entry are sells."""
    bps = float(model["%s_slippage_bps" % leg]) / 10000.0
    is_buy = (side == "LONG" and leg == "entry") or (side == "SHORT" and leg == "exit")
    return float(price) * (1.0 + bps) if is_buy else float(price) * (1.0 - bps)
