"""SPARTA Arbitrage Factory V1 Scanner SPEC Contract (READ-ONLY, SPEC ONLY).

A PURE, stdlib-only, read-only module that SPECIFIES -- and explicitly does NOT build --
the future Arbitrage Factory V1 scanner. It is roadmap block 1 (gate G1) of the lane
opened by the readiness contract: every later block (data contract, fee/slippage model,
report schema, review contract) builds against THIS frozen specification.

What the future scanner will be, by specification:
  - a READ-ONLY analyzer over operator-staged inputs (defined by the future data
    contract), covering families ARB_F1..ARB_F5 and reducing everything through
    ARB_F6 into PASS/WATCH/FAIL reports;
  - a writer of NEW report files only, under its own report directory -- it never
    modifies inputs, never holds credentials, never opens a network connection, never
    contains order logic, and never runs without a per-run explicit human approval;
  - a refuser by default: if ANY refusal condition holds (missing approved data
    contract, missing fee/slippage model, missing frozen report schema, missing human
    run approval, any credentialed source, any network dependency), it must return
    BLOCKED and write nothing.

This contract itself RUNS NOTHING and WRITES NOTHING: no scanner exists after this
block; no data fetch, no API call, no exchange connection, no credentials, no order
logic, no paper/micro-live/live. It does not touch the sealed Crypto-D1 lane and unlocks
no gate anywhere.

Public API:
  - SCANNER_SPEC_SCHEMA_VERSION / SCANNER_SPEC_LABEL / SCANNER_SPEC_MODE
  - VERDICT_SPEC_READY / VERDICT_SPEC_BLOCKED / NEXT_REQUIRED_ACTION
  - SCANNER_IO_SPEC / FAMILY_COVERAGE / REFUSAL_CONDITIONS / SCANNER_PROHIBITIONS
  - get_arbitrage_scanner_spec_label()
  - scanner_io_spec() / family_coverage() / refusal_conditions() / scanner_prohibitions()
  - record_arbitrage_scanner_spec(readiness_spec)
  - build_arbitrage_scanner_spec()
  - validate_arbitrage_scanner_spec(spec)
  - render_arbitrage_scanner_spec_markdown(spec)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.arbitrage_factory_v1_research_readiness_contract import (
    VERDICT_READINESS_READY,
    build_arbitrage_factory_v1_readiness,
    validate_arbitrage_factory_v1_readiness,
)

SCANNER_SPEC_SCHEMA_VERSION = "arbitrage_scanner_spec_contract.v1"
SCANNER_SPEC_LABEL = (
    "SPARTA Arbitrage Factory V1 Scanner SPEC (READ-ONLY, SPEC ONLY)"
)
SCANNER_SPEC_MODE = "RESEARCH_ONLY"

VERDICT_SPEC_READY = "ARBITRAGE_SCANNER_SPEC_READY"
VERDICT_SPEC_BLOCKED = "ARBITRAGE_SCANNER_SPEC_BLOCKED"

# Roadmap sequence is binding: after the scanner SPEC, the next block is the DATA
# contract (gate G2). Nothing here authorizes a scan, a fetch, or a connection.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_ARBITRAGE_DATA_CONTRACT"

SCANNER_IO_SPEC: dict[str, Any] = {
    "inputs": {
        "source": "operator_staged_files_as_defined_by_the_future_data_contract",
        "access": "read_only",
        "modified_by_scanner": False,
        "network_inputs_allowed": False,
        "credentialed_inputs_allowed": False,
    },
    "outputs": {
        "writes_only_under": "reports/arbitrage_factory_v1/",
        "files_per_scan": [
            "arb_scan_report.json",
            "arb_scan_report.md",
            "arb_scan_log.jsonl",
        ],
        "verdict_states": ["PASS", "WATCH", "FAIL"],
        "existing_reports_modified": False,
        "schema": "frozen_by_the_future_report_schema_contract_before_first_scan",
    },
    "run_model": {
        "per_run_human_approval_required": True,
        "scheduler_allowed": False,
        "background_loop_allowed": False,
        "dry_run_write_false_must_exist": True,
    },
}

FAMILY_COVERAGE: list[dict[str, Any]] = [
    {"family_id": "ARB_F1_spot_perp_funding_basis",
     "planned_metrics": ["funding_rate", "spot_perp_basis", "fee_adjusted_carry",
                          "carry_inversion_frequency"]},
    {"family_id": "ARB_F2_cross_exchange_basis_monitoring",
     "planned_metrics": ["cross_venue_spread", "spread_persistence",
                          "round_trip_cost_coverage"]},
    {"family_id": "ARB_F3_btc_eth_sol_pair_spread_alerts",
     "planned_metrics": ["pair_ratio_zscore", "ratio_extreme_flag",
                          "mean_reversion_half_life"]},
    {"family_id": "ARB_F4_fee_adjusted_net_edge_scanner",
     "planned_metrics": ["raw_edge", "net_edge_after_all_costs",
                          "edge_survival_fraction"]},
    {"family_id": "ARB_F5_liquidity_spread_slippage_filters",
     "planned_metrics": ["min_book_depth_check", "max_quoted_spread_check",
                          "slippage_ceiling_check"]},
    {"family_id": "ARB_F6_pass_watch_fail_report_framework",
     "planned_metrics": ["per_opportunity_verdict", "evidence_attachment",
                          "reproducibility_from_staged_inputs"]},
]

REFUSAL_CONDITIONS: list[str] = [
    "data_contract_not_yet_human_approved",
    "required_staged_inputs_missing_or_failing_data_contract_qa",
    "fee_slippage_model_not_yet_human_approved",
    "report_schema_not_yet_frozen",
    "per_run_human_approval_absent",
    "any_credentialed_or_authenticated_source_detected",
    "any_network_dependency_detected",
    "refusal_writes_nothing_blocked_means_no_output_files",
]

SCANNER_PROHIBITIONS: list[str] = [
    "no_network_connections_of_any_kind",
    "no_credentials_read_or_write_ever",
    "no_order_logic_in_the_scanner_or_any_helper_it_imports",
    "no_scheduler_no_automation_no_background_loop",
    "inputs_are_read_only_and_never_modified",
    "alerts_and_reports_are_the_only_outputs",
]


def get_arbitrage_scanner_spec_label() -> str:
    """Human label for the recognized Arbitrage Factory V1 scanner spec contract."""
    return SCANNER_SPEC_LABEL


def scanner_io_spec() -> dict[str, Any]:
    """Return a fresh deep copy of the fixed scanner I/O specification. Pure."""
    return copy.deepcopy(SCANNER_IO_SPEC)


def family_coverage() -> list[dict[str, Any]]:
    """Return fresh deep copies of the per-family coverage plan. Pure."""
    return [copy.deepcopy(f) for f in FAMILY_COVERAGE]


def refusal_conditions() -> list[str]:
    """Return a fresh copy of the refusal conditions. Pure."""
    return list(REFUSAL_CONDITIONS)


def scanner_prohibitions() -> list[str]:
    """Return a fresh copy of the scanner prohibitions. Pure."""
    return list(SCANNER_PROHIBITIONS)


def record_arbitrage_scanner_spec(readiness_spec: Any) -> dict[str, Any]:
    """Record the scanner SPEC over the lane's readiness contract. PURE: takes the
    readiness dict (or None), returns a spec dict. Never raises. Builds no scanner,
    fetches nothing, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(readiness_spec, dict):
        blockers.append("readiness_spec_missing")
    else:
        rs = readiness_spec
        rs_validation = validate_arbitrage_factory_v1_readiness(rs)
        if not rs_validation.get("valid"):
            blockers.append("readiness_spec_invalid")
        if rs.get("verdict") != VERDICT_READINESS_READY:
            blockers.append("readiness_not_ready")
        if rs.get("alerts_and_reports_only") is not True:
            blockers.append("lane_constitution_violated")

    risk_notes.append("this_is_a_specification_document_no_scanner_exists_after_it")
    risk_notes.append("scanner_must_refuse_by_default_blocked_writes_nothing")
    risk_notes.append("roadmap_sequence_is_binding_data_contract_comes_next")
    risk_notes.append("per_run_human_approval_is_non_negotiable")

    ready = not blockers
    verdict = VERDICT_SPEC_READY if ready else VERDICT_SPEC_BLOCKED
    return {
        "schema_version": SCANNER_SPEC_SCHEMA_VERSION,
        "label": SCANNER_SPEC_LABEL,
        "mode": SCANNER_SPEC_MODE,
        "verdict": verdict,
        "lane": "arbitrage_factory_v1",
        "roadmap_seq": 1,
        "scanner_io_spec": scanner_io_spec(),
        "family_coverage": family_coverage(),
        "refusal_conditions": refusal_conditions(),
        "scanner_prohibitions": scanner_prohibitions(),
        # Spec constitution, stated structurally:
        "scanner_built_by_this_contract": False,
        "alerts_and_reports_only": True,
        "execution_capability_exists": False,
        "modifies_crypto_d1_lane": False,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        # Capability posture (this spec runs / fetches / connects / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
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
        # Gate posture (the global trading gates are UNTOUCHED and stay locked):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_arbitrage_scanner_spec() -> dict[str, Any]:
    """Build the lane readiness in memory and record the scanner SPEC over it. PURE:
    no disk read, no fetch, no connection. Builds no scanner; unlocks nothing."""
    readiness = build_arbitrage_factory_v1_readiness()
    spec = record_arbitrage_scanner_spec(readiness)
    spec["readiness_verdict"] = readiness.get("verdict")
    return spec


def validate_arbitrage_scanner_spec(spec: Any) -> dict[str, Any]:
    """Validate (read-only) a scanner spec's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec

    if s.get("verdict") not in (VERDICT_SPEC_READY, VERDICT_SPEC_BLOCKED):
        errors.append("bad_verdict")
    if s.get("schema_version") != SCANNER_SPEC_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if s.get("lane") != "arbitrage_factory_v1":
        errors.append("bad_lane")
    if s.get("roadmap_seq") != 1:
        errors.append("bad_roadmap_seq")

    io = s.get("scanner_io_spec") or {}
    inputs = io.get("inputs") or {}
    outputs = io.get("outputs") or {}
    run_model = io.get("run_model") or {}
    if inputs.get("modified_by_scanner") is not False:
        errors.append("spec_allows_input_modification")
    if inputs.get("network_inputs_allowed") is not False:
        errors.append("spec_allows_network_inputs")
    if inputs.get("credentialed_inputs_allowed") is not False:
        errors.append("spec_allows_credentialed_inputs")
    if outputs.get("existing_reports_modified") is not False:
        errors.append("spec_allows_report_mutation")
    if set(outputs.get("verdict_states") or []) != {"PASS", "WATCH", "FAIL"}:
        errors.append("bad_verdict_states")
    if run_model.get("per_run_human_approval_required") is not True:
        errors.append("per_run_approval_dropped")
    if run_model.get("scheduler_allowed") is not False:
        errors.append("scheduler_allowed")
    if run_model.get("background_loop_allowed") is not False:
        errors.append("background_loop_allowed")

    cov = s.get("family_coverage")
    if not isinstance(cov, list) or len(cov) != 6:
        errors.append("family_coverage_not_six")
    else:
        for f in cov:
            if not (f.get("family_id") and f.get("planned_metrics")):
                errors.append("family_coverage_entry_incomplete")
                break

    refusals = s.get("refusal_conditions")
    if not isinstance(refusals, list) or len(refusals) < 7:
        errors.append("refusal_conditions_incomplete")
    elif not any("writes_nothing" in r for r in refusals):
        errors.append("blocked_writes_nothing_rule_missing")

    prohibitions = s.get("scanner_prohibitions")
    if not isinstance(prohibitions, list) or len(prohibitions) < 6:
        errors.append("prohibitions_incomplete")
    elif not any("no_order_logic" in p for p in prohibitions):
        errors.append("no_order_logic_rule_missing")

    if s.get("scanner_built_by_this_contract") is not False:
        errors.append("scanner_claimed_built")
    if s.get("alerts_and_reports_only") is not True:
        errors.append("lane_not_alerts_only")
    if s.get("execution_capability_exists") is not False:
        errors.append("execution_capability_claimed")
    if s.get("modifies_crypto_d1_lane") is not False:
        errors.append("crypto_d1_lane_touched")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
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
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_scanner_spec_markdown(spec: Any) -> str:
    """Render a scanner spec as deterministic markdown. Pure string work."""
    s = spec if isinstance(spec, dict) else {}
    io = s.get("scanner_io_spec") or {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Scanner SPEC (SPEC ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Lane: " + str(s.get("lane", "")) + " | roadmap seq: "
                 + str(s.get("roadmap_seq", "")))
    lines.append("- Scanner built by this contract: "
                 + str(s.get("scanner_built_by_this_contract", "")))
    lines.append("- Alerts and reports only: " + str(s.get("alerts_and_reports_only", "")))
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    lines.append("## I/O specification")
    inputs = io.get("inputs") or {}
    outputs = io.get("outputs") or {}
    run_model = io.get("run_model") or {}
    lines.append("- Inputs: " + str(inputs.get("source")) + " (read-only, never modified, "
                 "no network, no credentials)")
    lines.append("- Outputs: new files only under " + str(outputs.get("writes_only_under"))
                 + " -- " + ", ".join(outputs.get("files_per_scan") or []))
    lines.append("- Verdicts: " + ", ".join(outputs.get("verdict_states") or []))
    lines.append("- Run model: per-run human approval "
                 + str(run_model.get("per_run_human_approval_required"))
                 + ", scheduler " + str(run_model.get("scheduler_allowed"))
                 + ", background loop " + str(run_model.get("background_loop_allowed")))
    lines.append("")
    lines.append("## Family coverage")
    for f in s.get("family_coverage") or []:
        lines.append("- " + str(f.get("family_id")) + ": "
                     + ", ".join(f.get("planned_metrics") or []))
    lines.append("")
    lines.append("## Refusal conditions (BLOCKED writes nothing)")
    for r in s.get("refusal_conditions") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Scanner prohibitions")
    for p in s.get("scanner_prohibitions") or []:
        lines.append("- " + str(p))
    lines.append("")
    lines.append("## Blockers")
    for b in (s.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- execution: absent by construction (alerts and reports only)")
    return "\n".join(lines)
