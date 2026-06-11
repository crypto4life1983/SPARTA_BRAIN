"""SPARTA Prediction Market Factory V1 - LANE REVIEW (READ-ONLY, REVIEW ONLY).

Roadmap seq 5: the lane-wide review over the entire PM paper chain
(seq 0 readiness -> seq 1 scanner spec -> seq 2 data contract -> seq 3 cost &
settlement model -> seq 4 alert/report schema). It re-derives the chain
deterministically through the real builders and checks every link, every
gate-refusal, every handoff, and every honesty rule.

ACCEPTED means only: the lane's paper chain is coherent and may, after a
SEPARATE human approval, be registered in mission flow (seq 6). It is NOT a
scanner authorization, NOT a registration, and writes nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.prediction_market_factory_v1_research_readiness_contract import (
    VERDICT_PM_READINESS_READY,
    build_prediction_market_factory_v1_readiness,
    validate_prediction_market_factory_v1_readiness,
)
from sparta_commander.prediction_market_scanner_spec_contract import (
    VERDICT_PM_SPEC_READY,
    record_prediction_market_scanner_spec,
    validate_prediction_market_scanner_spec,
)
from sparta_commander.prediction_market_data_contract import (
    VERDICT_PM_DATA_READY,
    record_prediction_market_data_contract,
    validate_prediction_market_data_contract,
)
from sparta_commander.prediction_market_cost_settlement_model_contract import (
    VERDICT_PM_MODEL_READY,
    record_pm_cost_settlement_model,
    validate_pm_cost_settlement_model,
)
from sparta_commander.prediction_market_alert_report_schema_contract import (
    VERDICT_PM_RS_READY,
    record_pm_alert_report_schema,
    validate_pm_alert_report_schema,
)

PM_LR_SCHEMA_VERSION = "prediction_market_factory_v1_lane_review_contract.v1"
PM_LR_LABEL = ("SPARTA Prediction Market Factory V1 Lane Review "
               "(READ-ONLY, REVIEW ONLY)")
PM_LR_MODE = "RESEARCH_ONLY"
VERDICT_PM_LANE_REVIEW_ACCEPTED = "PM_LANE_REVIEW_ACCEPTED"
VERDICT_PM_LANE_REVIEW_BLOCKED = "PM_LANE_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_PM_MISSION_FLOW_REGISTRATION"

PM_LANE_REVIEW_CHECKLIST = (
    "seq0_readiness_ready_and_valid",
    "seq1_scanner_spec_ready_and_valid",
    "seq2_data_contract_ready_and_valid",
    "seq3_cost_model_ready_and_valid",
    "seq4_alert_schema_ready_and_valid",
    "explicit_gating_identical_to_standalone_rebuild",
    "tampered_upstream_refuses_downstream_at_every_link",
    "constitution_intact_research_only_no_wallet_no_execution",
    "honesty_rules_intact_model_agreement_and_cost_stack",
    "capabilities_all_false_and_gates_all_locked_across_chain",
)

_CAP_KEYS = ("executes", "runs_scanner", "fetches_data", "calls_api",
             "uses_network", "uses_credentials", "uses_wallet",
             "contains_order_logic", "starts_scheduler", "promotes_gate",
             "unlocks_downstream_gate")
_GATE_KEYS = ("paper_trading_gate_locked", "micro_live_gate_locked",
              "live_gate_locked")


def get_pm_lane_review_label() -> str:
    return PM_LR_LABEL


def _base_review() -> dict[str, Any]:
    return {
        "schema_version": PM_LR_SCHEMA_VERSION, "label": PM_LR_LABEL,
        "mode": PM_LR_MODE, "lane": "prediction_market_factory_v1",
        "roadmap_seq": 5, "verdict": None, "blockers": [],
        "checklist": list(PM_LANE_REVIEW_CHECKLIST),
        "checklist_results": {}, "seq_verdicts": {},
        "acceptance_means_lane_coherence_only": True,
        "acceptance_is_not_a_scanner_authorization": True,
        "seq6_registration_requires_its_own_human_approval": True,
        "review_reads_no_staged_files": True,
        "review_persists_nothing": True,
        "modifies_mission_flow": False,
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


def review_pm_lane(readiness: Any, spec: Any, data: Any, model: Any,
                   schema: Any) -> dict[str, Any]:
    """Review (pure, in-memory) the whole seq0->seq4 PM chain. Never raises."""
    review = _base_review()
    objs = (readiness, spec, data, model, schema)
    if not all(isinstance(o, dict) for o in objs):
        review["verdict"] = VERDICT_PM_LANE_REVIEW_BLOCKED
        review["blockers"].append("chain_objects_missing_or_not_dicts")
        return review

    review["seq_verdicts"] = {
        "seq0_readiness": readiness.get("verdict"),
        "seq1_scanner_spec": spec.get("verdict"),
        "seq2_data_contract": data.get("verdict"),
        "seq3_cost_model": model.get("verdict"),
        "seq4_alert_schema": schema.get("verdict"),
    }
    r: dict[str, bool] = {}
    r["seq0_readiness_ready_and_valid"] = (
        readiness.get("verdict") == VERDICT_PM_READINESS_READY
        and validate_prediction_market_factory_v1_readiness(readiness)["valid"])
    r["seq1_scanner_spec_ready_and_valid"] = (
        spec.get("verdict") == VERDICT_PM_SPEC_READY
        and validate_prediction_market_scanner_spec(spec)["valid"])
    r["seq2_data_contract_ready_and_valid"] = (
        data.get("verdict") == VERDICT_PM_DATA_READY
        and validate_prediction_market_data_contract(data)["valid"])
    r["seq3_cost_model_ready_and_valid"] = (
        model.get("verdict") == VERDICT_PM_MODEL_READY
        and validate_pm_cost_settlement_model(model)["valid"])
    r["seq4_alert_schema_ready_and_valid"] = (
        schema.get("verdict") == VERDICT_PM_RS_READY
        and validate_pm_alert_report_schema(schema)["valid"])

    rb_spec = record_prediction_market_scanner_spec(readiness)
    rb_data = record_prediction_market_data_contract(rb_spec)
    rb_model = record_pm_cost_settlement_model(rb_data)
    rb_schema = record_pm_alert_report_schema(rb_model)
    r["explicit_gating_identical_to_standalone_rebuild"] = (
        rb_spec == spec and rb_data == data and rb_model == model
        and rb_schema == schema)

    bad_readiness = dict(readiness); bad_readiness["execution_capability_exists"] = True
    bad_spec = dict(spec); bad_spec["runs_scanner"] = True
    bad_data = dict(data); bad_data["uses_wallet"] = True
    bad_model = dict(model); bad_model["contains_order_logic"] = True
    r["tampered_upstream_refuses_downstream_at_every_link"] = (
        record_prediction_market_scanner_spec(bad_readiness).get("verdict")
        != VERDICT_PM_SPEC_READY
        and record_prediction_market_data_contract(bad_spec).get("verdict")
        != VERDICT_PM_DATA_READY
        and record_pm_cost_settlement_model(bad_data).get("verdict")
        != VERDICT_PM_MODEL_READY
        and record_pm_alert_report_schema(bad_model).get("verdict")
        != VERDICT_PM_RS_READY)

    r["constitution_intact_research_only_no_wallet_no_execution"] = (
        readiness.get("alerts_and_reports_only") is True
        and readiness.get("execution_capability_exists") is False
        and all(o.get("uses_wallet") is False for o in objs if "uses_wallet" in o)
        and data.get("data_describes_markets_never_accounts") is True)

    r["honesty_rules_intact_model_agreement_and_cost_stack"] = (
        model.get("classification_is_research_readiness_not_a_trade_signal") is True
        and model.get("costs_never_default_to_zero") is True
        and schema.get("verdicts_must_agree_with_seq3_model") is True
        and schema.get("net_edge_must_match_cost_stack") is True)

    r["capabilities_all_false_and_gates_all_locked_across_chain"] = all(
        o.get(k) is False for o in objs for k in _CAP_KEYS if k in o
    ) and all(o.get(k) is True for o in objs for k in _GATE_KEYS)

    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_PM_LANE_REVIEW_BLOCKED
        review["blockers"].extend("check_failed:" + n for n in failed)
    else:
        review["verdict"] = VERDICT_PM_LANE_REVIEW_ACCEPTED
    return review


def build_pm_lane_review() -> dict[str, Any]:
    """Re-derive the real seq0->seq4 chain and review it. Pure."""
    readiness = build_prediction_market_factory_v1_readiness()
    spec = record_prediction_market_scanner_spec(readiness)
    data = record_prediction_market_data_contract(spec)
    model = record_pm_cost_settlement_model(data)
    schema = record_pm_alert_report_schema(model)
    return review_pm_lane(readiness, spec, data, model, schema)


def validate_pm_lane_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    verdict = v.get("verdict")
    if verdict not in (VERDICT_PM_LANE_REVIEW_ACCEPTED,
                       VERDICT_PM_LANE_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if tuple(v.get("checklist") or ()) != PM_LANE_REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    results = v.get("checklist_results") or {}
    if verdict == VERDICT_PM_LANE_REVIEW_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(PM_LANE_REVIEW_CHECKLIST):
            errors.append("accepted_without_full_checklist")
        elif not all(results.get(n) is True for n in PM_LANE_REVIEW_CHECKLIST):
            errors.append("accepted_with_failed_check")
    if verdict == VERDICT_PM_LANE_REVIEW_BLOCKED and not v.get("blockers"):
        errors.append("blocked_without_blockers")
    if v.get("lane") != "prediction_market_factory_v1":
        errors.append("wrong_lane")
    if v.get("roadmap_seq") != 5:
        errors.append("wrong_roadmap_seq")
    for key, want in (
        ("acceptance_means_lane_coherence_only", True),
        ("acceptance_is_not_a_scanner_authorization", True),
        ("seq6_registration_requires_its_own_human_approval", True),
        ("review_reads_no_staged_files", True),
        ("review_persists_nothing", True),
        ("modifies_mission_flow", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True),
        ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "fetches_data", "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
