"""SPARTA Prediction Market Factory V1 - COST & SETTLEMENT MODEL (READ-ONLY).

Roadmap seq 3: the model that makes prediction-market "edge" HONEST before any
scanner exists. Paper YES/NO inefficiencies die under spread, fees, gas,
settlement costs, thin liquidity, and resolution risk -- so this lane charges
all of them FIRST, conservatively, and refuses anything it cannot cost.

    net_edge_bps = gross_edge_bps
                   - spread_cost_bps        (full quoted spread)
                   - fee_bps                (venue fee assumption)
                   - gas_cost_bps           (gas as a COST ASSUMPTION only)
                   - settlement_cost_bps    (settlement/redemption cost)
                   - liquidity_penalty_bps  (thin-depth penalty, never zero)
                   - resolution_risk_bps    (time-to-resolution / oracle risk)

Classification (research readiness, NEVER a trade signal):
    PASS  if net >= 25 bps   WATCH if 0 <= net < 25   FAIL otherwise.
Markets that are not 'open', stale beyond the data contract's window, or
missing any cost refuse outright. Ambiguity resolves to the expensive side.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.prediction_market_data_contract import (
    ALLOWED_MARKET_STATUS,
    FORBIDDEN_FIELD_TOKENS,
    MAX_STALENESS_DAYS,
    VERDICT_PM_DATA_READY,
    build_prediction_market_data_contract,
    validate_outcome_price_row,
    validate_prediction_market_data_contract,
)

PM_MODEL_SCHEMA_VERSION = "prediction_market_cost_settlement_model_contract.v1"
PM_MODEL_LABEL = ("SPARTA Prediction Market Factory V1 Cost & Settlement Model "
                  "(READ-ONLY, MODEL ONLY)")
PM_MODEL_MODE = "RESEARCH_ONLY"
VERDICT_PM_MODEL_READY = "PM_COST_SETTLEMENT_MODEL_READY"
VERDICT_PM_MODEL_BLOCKED = "PM_COST_SETTLEMENT_MODEL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PM_ALERT_REPORT_SCHEMA"

MIN_NET_EDGE_PASS_BPS = 25.0   # PM frictions and resolution risk run higher
MIN_NET_EDGE_WATCH_BPS = 0.0

_REQUIRED_COST_INPUTS = (
    "gross_edge_bps", "spread_cost_bps", "fee_bps", "gas_cost_bps",
    "settlement_cost_bps", "liquidity_penalty_bps", "resolution_risk_bps",
)

COST_MODEL_RULES = (
    "every_cost_component_is_required_no_cost_ever_defaults_to_zero",
    "gas_enters_only_as_a_cost_assumption_in_bps_of_notional",
    "liquidity_penalty_is_never_zero_thin_books_cost_more",
    "resolution_risk_charges_time_to_resolution_and_oracle_uncertainty",
    "only_open_markets_are_evaluable_closed_resolved_paused_refuse",
    "stale_quotes_beyond_the_data_contract_window_refuse",
    "ambiguous_math_resolves_to_the_more_expensive_side",
    "classification_is_research_readiness_input_never_a_trade_signal",
)

CONSERVATIVE_ASSUMPTIONS = (
    "missing_any_cost_refuses_the_evaluation",
    "unknown_settlement_or_resolution_risk_refuses_or_FAILs_never_passes",
    "stale_data_refuses_outright",
    "no_zero_cost_default_anywhere",
    "when_in_doubt_the_classification_is_FAIL",
)


def get_pm_cost_settlement_model_label() -> str:
    return PM_MODEL_LABEL


def gross_edge_from_yes_no_sum(yes_price: Any, no_price: Any) -> dict[str, Any]:
    """Pure: turn a YES+NO sum deviation into a GROSS edge candidate (bps).
    Research framing only -- a deviation label, never an instruction."""
    row = validate_outcome_price_row(yes_price, no_price)
    if not row["acceptable"]:
        return {"computable": False, "gross_edge_bps": None,
                "errors": row["errors"]}
    total = float(yes_price) + float(no_price)
    deviation = abs(1.0 - total)
    label = ("sum_below_one_deviation" if total < 1.0
             else "sum_above_one_deviation" if total > 1.0 else "no_deviation")
    return {"computable": True, "gross_edge_bps": deviation * 10000.0,
            "deviation_label": label, "data_quality_flags": row["flags"],
            "errors": []}


def estimate_pm_net_edge_bps(inputs: Any) -> dict[str, Any]:
    """PURE arithmetic: charge every PM cost against the gross edge. Refuses
    missing/negative/non-finite costs, non-open markets, stale data, and any
    forbidden account/wallet key. Never raises."""
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

    status = inputs.get("market_status")
    if status not in ALLOWED_MARKET_STATUS:
        errors.append("market_status_unknown:" + str(status))
    elif status != "open":
        errors.append("market_not_open_refused:" + str(status))

    age = inputs.get("data_age_days")
    if not isinstance(age, (int, float)) or isinstance(age, bool) or age < 0:
        errors.append("data_age_days_missing_or_invalid")
    elif age > MAX_STALENESS_DAYS:
        errors.append("stale_data_refused_age_days_" + str(age))

    values: dict[str, float] = {}
    for name in _REQUIRED_COST_INPUTS:
        raw = inputs.get(name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            errors.append("missing_or_non_numeric:" + name)
            continue
        value = float(raw)
        if value != value or value in (float("inf"), float("-inf")):
            errors.append("non_finite:" + name)
        elif name != "gross_edge_bps" and value < 0:
            errors.append("negative_cost:" + name)
        elif name == "liquidity_penalty_bps" and value == 0:
            errors.append("zero_liquidity_penalty_refused_thin_books_cost_more")
        else:
            values[name] = value
    if errors:
        return {"computable": False, "net_edge_bps": None, "errors": errors}

    net = values["gross_edge_bps"] - sum(
        values[n] for n in _REQUIRED_COST_INPUTS if n != "gross_edge_bps")
    return {"computable": True, "net_edge_bps": net, "errors": []}


def classify_pm_net_edge(net_edge_bps: Any) -> str:
    """PASS/WATCH/FAIL research readiness. Doubt is FAIL. Never a signal."""
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
        "schema_version": PM_MODEL_SCHEMA_VERSION, "label": PM_MODEL_LABEL,
        "mode": PM_MODEL_MODE, "lane": "prediction_market_factory_v1",
        "roadmap_seq": 3, "verdict": None, "blockers": [],
        "data_contract_verdict": None,
        "required_cost_inputs": list(_REQUIRED_COST_INPUTS),
        "cost_model_rules": list(COST_MODEL_RULES),
        "conservative_assumptions": list(CONSERVATIVE_ASSUMPTIONS),
        "min_net_edge_pass_bps": MIN_NET_EDGE_PASS_BPS,
        "min_net_edge_watch_bps": MIN_NET_EDGE_WATCH_BPS,
        "max_staleness_days": MAX_STALENESS_DAYS,
        "classification_is_research_readiness_not_a_trade_signal": True,
        "costs_never_default_to_zero": True,
        "gas_is_a_cost_assumption_only": True,
        "model_reads_no_files": True,
        "output_is_model_readiness_only": True,
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


def record_pm_cost_settlement_model(data_contract: Any) -> dict[str, Any]:
    """Record the model, gated on a READY, valid seq-2 data contract."""
    m = _base_model()
    if not isinstance(data_contract, dict):
        m["verdict"] = VERDICT_PM_MODEL_BLOCKED
        m["blockers"].append("data_contract_missing")
        return m
    if not validate_prediction_market_data_contract(data_contract).get("valid"):
        m["verdict"] = VERDICT_PM_MODEL_BLOCKED
        m["blockers"].append("data_contract_invalid")
        return m
    if data_contract.get("verdict") != VERDICT_PM_DATA_READY:
        m["verdict"] = VERDICT_PM_MODEL_BLOCKED
        m["blockers"].append("data_contract_not_ready")
        return m
    m["verdict"] = VERDICT_PM_MODEL_READY
    m["data_contract_verdict"] = data_contract.get("verdict")
    return m


def build_pm_cost_settlement_model() -> dict[str, Any]:
    """Build against the real seq 0 -> 1 -> 2 chain. Pure."""
    return record_pm_cost_settlement_model(
        build_prediction_market_data_contract())


def validate_pm_cost_settlement_model(model: Any) -> dict[str, Any]:
    """Validate the model's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return {"valid": False, "errors": ["model_not_a_dict"]}
    m = model
    verdict = m.get("verdict")
    if verdict not in (VERDICT_PM_MODEL_READY, VERDICT_PM_MODEL_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_PM_MODEL_BLOCKED and not m.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_PM_MODEL_READY:
        if m.get("blockers"):
            errors.append("ready_with_blockers")
        if m.get("data_contract_verdict") != VERDICT_PM_DATA_READY:
            errors.append("ready_without_ready_data_contract")
    if m.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if m.get("roadmap_seq") != 3:
        errors.append("wrong_roadmap_seq")
    if tuple(m.get("required_cost_inputs") or ()) != _REQUIRED_COST_INPUTS:
        errors.append("cost_inputs_tampered")
    if tuple(m.get("cost_model_rules") or ()) != COST_MODEL_RULES:
        errors.append("cost_rules_tampered")
    if tuple(m.get("conservative_assumptions") or ()) != CONSERVATIVE_ASSUMPTIONS:
        errors.append("conservative_assumptions_weakened")
    p, w = m.get("min_net_edge_pass_bps"), m.get("min_net_edge_watch_bps")
    if not (isinstance(p, (int, float)) and isinstance(w, (int, float))
            and p > w >= 0 and p >= MIN_NET_EDGE_PASS_BPS):
        errors.append("thresholds_loosened")
    if m.get("max_staleness_days") != MAX_STALENESS_DAYS:
        errors.append("staleness_rule_tampered")
    for key, want in (
        ("classification_is_research_readiness_not_a_trade_signal", True),
        ("costs_never_default_to_zero", True),
        ("gas_is_a_cost_assumption_only", True),
        ("model_reads_no_files", True),
        ("output_is_model_readiness_only", True),
        ("modifies_arbitrage_factory_v1_lane", False),
        ("modifies_crypto_d1_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True),
        ("live_gate_locked", True),
    ):
        if m.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "fetches_data", "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if m.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
