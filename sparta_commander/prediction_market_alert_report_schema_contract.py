"""SPARTA Prediction Market Factory V1 - ALERT/REPORT SCHEMA (READ-ONLY).

Roadmap seq 4: the FROZEN shape of every PM research alert. Honesty is
structural: an alert's net edge must equal gross minus the full 6-part cost
stack, its verdict must equal the seq-3 model's classification of that net
edge, and trade/wallet/hype language refuses the whole alert. This module
writes nothing -- it is the schema.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.prediction_market_data_contract import (
    ALLOWED_MARKET_STATUS,
    FORBIDDEN_FIELD_TOKENS,
)
from sparta_commander.prediction_market_cost_settlement_model_contract import (
    VERDICT_PM_MODEL_READY,
    build_pm_cost_settlement_model,
    classify_pm_net_edge,
    validate_pm_cost_settlement_model,
)
from sparta_commander.prediction_market_factory_v1_research_readiness_contract import (
    CANDIDATE_FAMILIES,
)

PM_RS_SCHEMA_VERSION = "prediction_market_alert_report_schema_contract.v1"
PM_RS_LABEL = ("SPARTA Prediction Market Factory V1 Alert/Report Schema "
               "(READ-ONLY, SCHEMA ONLY)")
PM_RS_MODE = "RESEARCH_ONLY"
VERDICT_PM_RS_READY = "PM_ALERT_REPORT_SCHEMA_READY"
VERDICT_PM_RS_BLOCKED = "PM_ALERT_REPORT_SCHEMA_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PM_LANE_REVIEW_CONTRACT"

REPORTS_ROOT = "reports/prediction_market_factory_v1/"
ALERT_VERDICT_STATES = ("PASS", "WATCH", "FAIL")

ALERT_COST_FIELDS = ("spread_cost_bps", "fee_cost_bps", "gas_cost_bps",
                     "settlement_cost_bps", "liquidity_penalty_bps",
                     "resolution_risk_bps")

ALERT_REQUIRED_FIELDS = (
    "alert_id", "created_at_utc", "market_id", "event_id", "question_label",
    "strategy_family", "gross_edge_bps",
) + ALERT_COST_FIELDS + (
    "net_edge_bps", "verdict", "market_status", "resolution_date_utc",
    "provenance_label", "human_action_needed",
    "research_only_not_trade_signal", "mandatory_disclaimer",
)

MANDATORY_DISCLAIMER = ("research alert only - not financial advice - "
                        "no trade signal - human review required")

FORBIDDEN_ALERT_LANGUAGE = (
    "buy", "sell", "long", "short", "guaranteed", "winning", "place order",
    "deposit", "withdraw", "wallet action", "stake",
)

REPORT_FILE_RULES = (
    "reports_live_only_under_reports_prediction_market_factory_v1",
    "one_report_per_human_approved_run_no_continuous_streams",
    "reports_are_append_only_never_overwritten",
    "every_alert_verdict_must_equal_the_seq3_model_classification",
    "every_net_edge_must_equal_gross_minus_the_full_cost_stack",
    "refused_or_blocked_alerts_write_nothing",
)


def get_pm_alert_report_schema_label() -> str:
    return PM_RS_LABEL


def _screen_language(*texts: Any) -> str | None:
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    words = joined.replace(",", " ").replace(".", " ").split()
    for bad in FORBIDDEN_ALERT_LANGUAGE:
        if " " in bad:
            if bad in joined:
                return bad
        elif bad in words:
            return bad
    return None


def validate_pm_alert_record(record: Any) -> dict[str, Any]:
    """Validate ONE proposed PM alert against the frozen schema. Pure."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"acceptable": False, "errors": ["record_not_a_dict"]}
    for field in ALERT_REQUIRED_FIELDS:
        if field not in record:
            errors.append("missing_required_field:" + field)
    if errors:
        return {"acceptable": False, "errors": errors}

    token = _screen_language(record.get("question_label"),
                             record.get("alert_id"),
                             record.get("strategy_family"),
                             record.get("provenance_label"))
    if token is not None:
        return {"acceptable": False,
                "errors": ["forbidden_alert_language:" + token]}
    for key in record:
        lowered = str(key).lower()
        for bad in FORBIDDEN_FIELD_TOKENS:
            if bad in lowered:
                return {"acceptable": False,
                        "errors": ["forbidden_alert_field:" + str(key)]}

    if record.get("verdict") not in ALERT_VERDICT_STATES:
        errors.append("verdict_outside_closed_set")
    if record.get("strategy_family") not in CANDIDATE_FAMILIES:
        errors.append("strategy_family_outside_lane_families")
    if record.get("market_status") not in ALLOWED_MARKET_STATUS:
        errors.append("market_status_outside_closed_set")

    numeric = ("gross_edge_bps", "net_edge_bps") + ALERT_COST_FIELDS
    values: dict[str, float] = {}
    for name in numeric:
        raw = record.get(name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            errors.append("non_numeric:" + name)
        else:
            values[name] = float(raw)
    if not errors:
        expected_net = values["gross_edge_bps"] - sum(
            values[c] for c in ALERT_COST_FIELDS)
        if abs(expected_net - values["net_edge_bps"]) > 1e-9:
            errors.append("net_edge_does_not_match_cost_stack")
        if record.get("verdict") != classify_pm_net_edge(values["net_edge_bps"]):
            errors.append("verdict_disagrees_with_seq3_model_classification")

    if record.get("human_action_needed") is not True:
        errors.append("human_action_flag_dropped")
    if record.get("research_only_not_trade_signal") is not True:
        errors.append("research_only_flag_dropped")
    if record.get("mandatory_disclaimer") != MANDATORY_DISCLAIMER:
        errors.append("disclaimer_missing_or_altered")
    return {"acceptable": not errors, "errors": errors}


def _base_schema() -> dict[str, Any]:
    return {
        "schema_version": PM_RS_SCHEMA_VERSION, "label": PM_RS_LABEL,
        "mode": PM_RS_MODE, "lane": "prediction_market_factory_v1",
        "roadmap_seq": 4, "verdict": None, "blockers": [],
        "cost_model_verdict": None,
        "reports_root": REPORTS_ROOT,
        "alert_verdict_states": list(ALERT_VERDICT_STATES),
        "alert_required_fields": list(ALERT_REQUIRED_FIELDS),
        "alert_cost_fields": list(ALERT_COST_FIELDS),
        "forbidden_alert_language": list(FORBIDDEN_ALERT_LANGUAGE),
        "report_file_rules": list(REPORT_FILE_RULES),
        "mandatory_disclaimer": MANDATORY_DISCLAIMER,
        "alerts_are_research_only_never_trade_signals": True,
        "verdicts_must_agree_with_seq3_model": True,
        "net_edge_must_match_cost_stack": True,
        "schema_writes_no_reports": True,
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


def record_pm_alert_report_schema(cost_model: Any) -> dict[str, Any]:
    """Record the schema, gated on a READY, valid seq-3 cost model."""
    s = _base_schema()
    if not isinstance(cost_model, dict):
        s["verdict"] = VERDICT_PM_RS_BLOCKED
        s["blockers"].append("cost_model_missing")
        return s
    if not validate_pm_cost_settlement_model(cost_model).get("valid"):
        s["verdict"] = VERDICT_PM_RS_BLOCKED
        s["blockers"].append("cost_model_invalid")
        return s
    if cost_model.get("verdict") != VERDICT_PM_MODEL_READY:
        s["verdict"] = VERDICT_PM_RS_BLOCKED
        s["blockers"].append("cost_model_not_ready")
        return s
    s["verdict"] = VERDICT_PM_RS_READY
    s["cost_model_verdict"] = cost_model.get("verdict")
    return s


def build_pm_alert_report_schema() -> dict[str, Any]:
    """Build against the real seq 0 -> 3 chain. Pure."""
    return record_pm_alert_report_schema(build_pm_cost_settlement_model())


def validate_pm_alert_report_schema(schema: Any) -> dict[str, Any]:
    """Validate the schema contract's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(schema, dict):
        return {"valid": False, "errors": ["schema_not_a_dict"]}
    s = schema
    verdict = s.get("verdict")
    if verdict not in (VERDICT_PM_RS_READY, VERDICT_PM_RS_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_PM_RS_BLOCKED and not s.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_PM_RS_READY:
        if s.get("blockers"):
            errors.append("ready_with_blockers")
        if s.get("cost_model_verdict") != VERDICT_PM_MODEL_READY:
            errors.append("ready_without_ready_cost_model")
    if s.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if s.get("roadmap_seq") != 4:
        errors.append("wrong_roadmap_seq")
    if s.get("reports_root") != REPORTS_ROOT:
        errors.append("reports_root_moved")
    if tuple(s.get("alert_verdict_states") or ()) != ALERT_VERDICT_STATES:
        errors.append("verdict_states_tampered")
    if tuple(s.get("alert_required_fields") or ()) != ALERT_REQUIRED_FIELDS:
        errors.append("required_fields_tampered")
    if tuple(s.get("forbidden_alert_language") or ()) != FORBIDDEN_ALERT_LANGUAGE:
        errors.append("forbidden_language_weakened")
    if tuple(s.get("report_file_rules") or ()) != REPORT_FILE_RULES:
        errors.append("file_rules_tampered")
    if s.get("mandatory_disclaimer") != MANDATORY_DISCLAIMER:
        errors.append("disclaimer_tampered")
    for key, want in (
        ("alerts_are_research_only_never_trade_signals", True),
        ("verdicts_must_agree_with_seq3_model", True),
        ("net_edge_must_match_cost_stack", True),
        ("schema_writes_no_reports", True),
        ("modifies_arbitrage_factory_v1_lane", False),
        ("modifies_crypto_d1_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True),
        ("live_gate_locked", True),
    ):
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
