"""SPARTA Arbitrage Factory V1 - LANE REVIEW Contract (READ-ONLY, REVIEW ONLY).

Roadmap seq 5 of the Arbitrage Factory V1 lane: the lane-wide review over the
ENTIRE contract chain built so far --

    seq 0 readiness (lane constitution)
    seq 1 scanner spec (frozen IO, refuse-by-default)
    seq 2 data contract (operator-staged shapes, forbidden fields)
    seq 3 fee/slippage model (honest net edge, conservative assumptions)
    seq 4 alert/report schema (unfakeable PASS/WATCH/FAIL alerts)

-- and the judgment of whether the lane is coherent enough to proceed to seq 6,
the mission-flow registration. The review re-derives the whole chain
deterministically through the real builders and checks every link, every
gate-refusal, every handoff, and every honesty rule.

What acceptance means -- and does not mean (validator-enforced):
  - ACCEPTED means only: the lane's paper chain is coherent and may, after a
    SEPARATE human approval, be registered in mission flow (seq 6).
  - ACCEPTED is NOT a scanner authorization. Building the actual scanner
    remains a separate, future, human-approved block under the frozen seq-1
    spec -- and even then every run needs its own per-run human approval.
  - The review reads no staged file, writes nothing, runs nothing.

Public API:
  - LANE_REVIEW_SCHEMA_VERSION / LANE_REVIEW_LABEL / LANE_REVIEW_MODE
  - VERDICT_LANE_REVIEW_ACCEPTED / VERDICT_LANE_REVIEW_BLOCKED
  - LANE_REVIEW_CHECKLIST / NEXT_REQUIRED_ACTION
  - get_arbitrage_lane_review_label()
  - review_lane(readiness, scanner_spec, data_contract, fee_model, report_schema)
  - build_arbitrage_lane_review()
  - validate_arbitrage_lane_review(review)
  - render_arbitrage_lane_review_markdown(review)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.arbitrage_factory_v1_research_readiness_contract import (
    VERDICT_READINESS_READY,
    build_arbitrage_factory_v1_readiness,
    validate_arbitrage_factory_v1_readiness,
)
from sparta_commander.arbitrage_scanner_spec_contract import (
    VERDICT_SPEC_READY,
    record_arbitrage_scanner_spec,
    validate_arbitrage_scanner_spec,
)
from sparta_commander.arbitrage_data_contract import (
    VERDICT_DATA_CONTRACT_READY,
    record_arbitrage_data_contract,
    validate_arbitrage_data_contract,
)
from sparta_commander.arbitrage_fee_slippage_model_contract import (
    VERDICT_MODEL_READY,
    record_arbitrage_fee_slippage_model,
    validate_arbitrage_fee_slippage_model,
)
from sparta_commander.arbitrage_alert_report_schema_contract import (
    REPORTS_ROOT,
    VERDICT_REPORT_SCHEMA_READY,
    record_arbitrage_alert_report_schema,
    validate_arbitrage_alert_report_schema,
)

LANE_REVIEW_SCHEMA_VERSION = "arbitrage_lane_review_contract.v1"
LANE_REVIEW_LABEL = (
    "SPARTA Arbitrage Factory V1 Lane Review (READ-ONLY, REVIEW ONLY)"
)
LANE_REVIEW_MODE = "RESEARCH_ONLY"

VERDICT_LANE_REVIEW_ACCEPTED = "ARBITRAGE_LANE_REVIEW_ACCEPTED"
VERDICT_LANE_REVIEW_BLOCKED = "ARBITRAGE_LANE_REVIEW_BLOCKED"

# Roadmap seq 6: the mission-flow registration, under its own human approval.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_LANE_MISSION_FLOW_REGISTRATION"

LANE_REVIEW_CHECKLIST = (
    "seq0_readiness_ready_and_valid",
    "seq1_scanner_spec_ready_and_valid",
    "seq2_data_contract_ready_and_valid",
    "seq3_fee_slippage_model_ready_and_valid",
    "seq4_alert_report_schema_ready_and_valid",
    "explicit_gating_identical_to_standalone_rebuild",
    "tampered_upstream_refuses_downstream_at_every_link",
    "next_action_handoff_runs_seq0_through_seq5",
    "constitution_intact_alerts_only_execution_absent",
    "honesty_rules_intact_model_agreement_and_cost_breakdown",
    "reports_root_aligned_between_spec_and_schema",
    "capabilities_all_false_and_gates_all_locked_across_chain",
)

_CHAIN_CAPABILITY_KEYS = (
    "executes", "runs_scanner", "fetches_data", "calls_api", "connects_broker",
    "connects_exchange", "uses_network", "uses_credentials",
    "contains_order_logic", "promotes_gate", "unlocks_downstream_gate",
)
_GATE_KEYS = (
    "paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked",
)


def get_arbitrage_lane_review_label() -> str:
    """Human label for the recognized arbitrage lane review contract."""
    return LANE_REVIEW_LABEL


def _base_review() -> dict[str, Any]:
    return {
        "schema_version": LANE_REVIEW_SCHEMA_VERSION,
        "label": LANE_REVIEW_LABEL,
        "mode": LANE_REVIEW_MODE,
        "lane": "arbitrage_factory_v1",
        "roadmap_seq": 5,
        "verdict": None,
        "blockers": [],
        "checklist": list(LANE_REVIEW_CHECKLIST),
        "checklist_results": {},
        "seq_verdicts": {},
        # What acceptance means, stated structurally:
        "acceptance_means_lane_coherence_only": True,
        "acceptance_is_not_a_scanner_authorization": True,
        "scanner_build_requires_its_own_human_approval": True,
        "every_future_scanner_run_needs_per_run_human_approval": True,
        "seq6_registration_requires_its_own_human_approval": True,
        "review_reads_no_staged_files": True,
        "review_persists_nothing": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_reports": False,
        "sends_notifications": False,
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


def review_lane(
    readiness: Any,
    scanner_spec: Any,
    data_contract: Any,
    fee_model: Any,
    report_schema: Any,
) -> dict[str, Any]:
    """Review (read-only, in-memory) the whole seq0->seq4 chain against the
    lane checklist. PURE: never raises, reads no file, runs nothing."""
    review = _base_review()
    results: dict[str, bool] = {}

    objs = (readiness, scanner_spec, data_contract, fee_model, report_schema)
    if not all(isinstance(o, dict) for o in objs):
        review["verdict"] = VERDICT_LANE_REVIEW_BLOCKED
        review["blockers"].append("chain_objects_missing_or_not_dicts")
        return review

    review["seq_verdicts"] = {
        "seq0_readiness": readiness.get("verdict"),
        "seq1_scanner_spec": scanner_spec.get("verdict"),
        "seq2_data_contract": data_contract.get("verdict"),
        "seq3_fee_slippage_model": fee_model.get("verdict"),
        "seq4_alert_report_schema": report_schema.get("verdict"),
    }

    results["seq0_readiness_ready_and_valid"] = (
        readiness.get("verdict") == VERDICT_READINESS_READY
        and validate_arbitrage_factory_v1_readiness(readiness).get("valid") is True
    )
    results["seq1_scanner_spec_ready_and_valid"] = (
        scanner_spec.get("verdict") == VERDICT_SPEC_READY
        and validate_arbitrage_scanner_spec(scanner_spec).get("valid") is True
    )
    results["seq2_data_contract_ready_and_valid"] = (
        data_contract.get("verdict") == VERDICT_DATA_CONTRACT_READY
        and validate_arbitrage_data_contract(data_contract).get("valid") is True
    )
    results["seq3_fee_slippage_model_ready_and_valid"] = (
        fee_model.get("verdict") == VERDICT_MODEL_READY
        and validate_arbitrage_fee_slippage_model(fee_model).get("valid") is True
    )
    results["seq4_alert_report_schema_ready_and_valid"] = (
        report_schema.get("verdict") == VERDICT_REPORT_SCHEMA_READY
        and validate_arbitrage_alert_report_schema(report_schema).get("valid") is True
    )

    # No hidden state: the explicit chain equals the standalone rebuild.
    rebuilt_spec = record_arbitrage_scanner_spec(readiness)
    rebuilt_contract = record_arbitrage_data_contract(rebuilt_spec)
    rebuilt_model = record_arbitrage_fee_slippage_model(rebuilt_contract)
    rebuilt_schema = record_arbitrage_alert_report_schema(rebuilt_model)
    results["explicit_gating_identical_to_standalone_rebuild"] = (
        rebuilt_spec == scanner_spec
        and rebuilt_contract == data_contract
        and rebuilt_model == fee_model
        and rebuilt_schema == report_schema
    )

    # Negative checks at EVERY link.
    bad_readiness = dict(readiness)
    bad_readiness["execution_capability_exists"] = True
    bad_spec = dict(scanner_spec)
    bad_spec["runs_scanner"] = True
    bad_contract = dict(data_contract)
    bad_contract["fetches_data"] = True
    bad_model = dict(fee_model)
    bad_model["contains_order_logic"] = True
    results["tampered_upstream_refuses_downstream_at_every_link"] = (
        record_arbitrage_scanner_spec(bad_readiness).get("verdict")
        != VERDICT_SPEC_READY
        and record_arbitrage_data_contract(bad_spec).get("verdict")
        != VERDICT_DATA_CONTRACT_READY
        and record_arbitrage_fee_slippage_model(bad_contract).get("verdict")
        != VERDICT_MODEL_READY
        and record_arbitrage_alert_report_schema(bad_model).get("verdict")
        != VERDICT_REPORT_SCHEMA_READY
    )

    results["next_action_handoff_runs_seq0_through_seq5"] = (
        readiness.get("next_required_action")
        == "HUMAN_APPROVED_ARBITRAGE_SCANNER_SPEC"
        and scanner_spec.get("next_required_action")
        == "HUMAN_APPROVED_ARBITRAGE_DATA_CONTRACT"
        and data_contract.get("next_required_action")
        == "HUMAN_APPROVED_FEE_SLIPPAGE_MODEL"
        and fee_model.get("next_required_action")
        == "HUMAN_APPROVED_ALERT_REPORT_SCHEMA"
        and report_schema.get("next_required_action")
        == "HUMAN_APPROVED_LANE_REVIEW_CONTRACT"
    )

    results["constitution_intact_alerts_only_execution_absent"] = (
        readiness.get("alerts_and_reports_only") is True
        and readiness.get("execution_capability_exists") is False
        and scanner_spec.get("alerts_and_reports_only") is True
        and data_contract.get("data_describes_markets_never_accounts") is True
        and report_schema.get(
            "alerts_are_research_only_never_trade_signals") is True
    )

    results["honesty_rules_intact_model_agreement_and_cost_breakdown"] = (
        fee_model.get(
            "classification_is_research_readiness_not_a_trade_signal") is True
        and fee_model.get("costs_never_default_to_zero") is True
        and report_schema.get("verdicts_must_agree_with_seq3_model") is True
        and report_schema.get("net_edge_must_match_cost_breakdown") is True
    )

    spec_io = scanner_spec.get("scanner_io_spec") or {}
    spec_outputs = spec_io.get("outputs") or {}
    results["reports_root_aligned_between_spec_and_schema"] = (
        spec_outputs.get("writes_only_under") == REPORTS_ROOT
        and report_schema.get("reports_root") == REPORTS_ROOT
    )

    results["capabilities_all_false_and_gates_all_locked_across_chain"] = all(
        o.get(k) is False for o in objs for k in _CHAIN_CAPABILITY_KEYS if k in o
    ) and all(o.get(k) is True for o in objs for k in _GATE_KEYS)

    review["checklist_results"] = results
    failed = [name for name, ok in results.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_LANE_REVIEW_BLOCKED
        review["blockers"].extend("check_failed:" + name for name in failed)
    else:
        review["verdict"] = VERDICT_LANE_REVIEW_ACCEPTED
    return review


def build_arbitrage_lane_review() -> dict[str, Any]:
    """Re-derive the real seq0->seq4 chain deterministically and review it."""
    readiness = build_arbitrage_factory_v1_readiness()
    scanner_spec = record_arbitrage_scanner_spec(readiness)
    data_contract = record_arbitrage_data_contract(scanner_spec)
    fee_model = record_arbitrage_fee_slippage_model(data_contract)
    report_schema = record_arbitrage_alert_report_schema(fee_model)
    return review_lane(
        readiness, scanner_spec, data_contract, fee_model, report_schema)


def validate_arbitrage_lane_review(review: Any) -> dict[str, Any]:
    """Validate (read-only) a lane review's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    r = review

    verdict = r.get("verdict")
    if verdict not in (VERDICT_LANE_REVIEW_ACCEPTED, VERDICT_LANE_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if tuple(r.get("checklist") or ()) != LANE_REVIEW_CHECKLIST:
        errors.append("checklist_tampered")

    results = r.get("checklist_results") or {}
    if verdict == VERDICT_LANE_REVIEW_ACCEPTED:
        if r.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(LANE_REVIEW_CHECKLIST):
            errors.append("accepted_without_full_checklist")
        elif not all(results.get(name) is True for name in LANE_REVIEW_CHECKLIST):
            errors.append("accepted_with_failed_check")
    if verdict == VERDICT_LANE_REVIEW_BLOCKED and not r.get("blockers"):
        errors.append("blocked_without_blockers")

    if r.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if r.get("roadmap_seq") != 5:
        errors.append("wrong_roadmap_seq")

    for key, err in (
        ("acceptance_means_lane_coherence_only", "acceptance_overclaims"),
        ("acceptance_is_not_a_scanner_authorization",
         "acceptance_claims_scanner_authorization"),
        ("scanner_build_requires_its_own_human_approval",
         "scanner_approval_dropped"),
        ("every_future_scanner_run_needs_per_run_human_approval",
         "per_run_approval_dropped"),
        ("seq6_registration_requires_its_own_human_approval",
         "seq6_approval_dropped"),
        ("review_reads_no_staged_files", "review_reads_staged_files"),
        ("review_persists_nothing", "review_persists"),
        ("human_review_required", "human_review_dropped"),
    ):
        if r.get(key) is not True:
            errors.append(err)

    for key in _GATE_KEYS:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_reports",
        "sends_notifications",
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
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_lane_review_markdown(review: Any) -> str:
    """Render a lane review as deterministic markdown. Pure string work."""
    r = review if isinstance(review, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Lane Review (REVIEW ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Lane: " + str(r.get("lane", "")) + " (roadmap seq "
                 + str(r.get("roadmap_seq", "")) + ")")
    lines.append("- Acceptance means lane coherence ONLY; it is NOT a scanner "
                 "authorization")
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    blockers = r.get("blockers") or []
    if blockers:
        lines.append("## Blockers (review does not accept the lane)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Sequence verdicts")
    for k, v in (r.get("seq_verdicts") or {}).items():
        lines.append("- " + str(k) + ": " + str(v))
    lines.append("")
    lines.append("## Checklist results")
    results = r.get("checklist_results") or {}
    for name in r.get("checklist") or []:
        mark = "PASS" if results.get(name) else "FAIL"
        lines.append("- [" + mark + "] " + str(name))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
