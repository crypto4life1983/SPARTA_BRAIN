"""SPARTA Offline Strategy Factory - V1 BACKBONE CLOSURE REPORT (TEMPLATE).

Bundle 28 (closure) of the Strategy Factory automation backbone. This module is
a PURE, stdlib-only *read-only closure report template* builder: it consumes a
Bundle 27 end-to-end fake pipeline contract and, only when that contract is
active with next_gate == BACKBONE_CLOSURE_REPORT_REQUIRED, produces a
deterministic, read-only *report* summarizing and verifying the completed
Strategy Factory v1 backbone (Bundles 11-28) and declaring the final closure
status. It defines a closure report template only -- NOT a live system.

It never runs Strategy Factory, never runs the fake pipeline, never writes
runtime state, never persists an approval, never writes a ledger file, never
updates runtime state, never updates dashboard files, never orchestrates
anything, never performs research, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing. It opens no network, spawns no subprocess, writes no file,
touches no broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION
  - DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL
  - BACKBONE_CLOSURE_REPORT_STATUS
  - BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE
  - BACKBONE_CLOSURE_STATE_ACTIVE
  - BACKBONE_CLOSURE_STATE_BLOCKED
  - FINAL_BACKBONE_STATUS_COMPLETE
  - RECOMMENDED_NEXT_PHASE
  - NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW
  - NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT
  - build_backbone_closure_report(pipeline)
  - validate_backbone_closure_report(report)
  - render_backbone_closure_report_markdown(report)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (
    END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION,
    END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED,
)

__all__ = [
    "BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION",
    "DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL",
    "BACKBONE_CLOSURE_REPORT_STATUS",
    "BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE",
    "BACKBONE_CLOSURE_STATE_ACTIVE",
    "BACKBONE_CLOSURE_STATE_BLOCKED",
    "FINAL_BACKBONE_STATUS_COMPLETE",
    "RECOMMENDED_NEXT_PHASE",
    "NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW",
    "NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT",
    "build_backbone_closure_report",
    "validate_backbone_closure_report",
    "render_backbone_closure_report_markdown",
]

BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION = (
    "strategy_factory_backbone_closure_report.v1"
)
DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL = (
    "Strategy Factory v1 Backbone Closure Report"
)
BACKBONE_CLOSURE_REPORT_STATUS = "READ_ONLY_BACKBONE_CLOSURE_REPORT"

BACKBONE_CLOSURE_STATE_ACTIVE = "BACKBONE_CLOSURE_REPORT_ACTIVE"
BACKBONE_CLOSURE_STATE_BLOCKED = "BACKBONE_CLOSURE_REPORT_BLOCKED"

# Final declared status of the v1 backbone when the closure report is active.
FINAL_BACKBONE_STATUS_COMPLETE = "STRATEGY_FACTORY_V1_BACKBONE_COMPLETE"

# The only phase this report recommends -- planning a fake-artifact smoke test,
# nothing runnable. It authorizes nothing; any later phase stays human-gated.
RECOMMENDED_NEXT_PHASE = "FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY"

# Bundle range the completed v1 backbone covers.
_COMPLETED_BUNDLE_RANGE = "Bundles 11-28"

NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW = "PAUSE_AND_OPERATOR_REVIEW"
NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT = (
    "AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 27). Pinned False:
# a closure report template only summarizes a completed template chain; it
# grants nothing and is never wired into runtime state.
BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE: dict[str, bool] = dict(
    END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE
)

# Deterministic, verb-safe one-line summary of each contract in the chain.
_COMPLETED_CONTRACT_CHAIN_SUMMARY: tuple[str, ...] = (
    "Research queue intake contract is in place.",
    "Research decision memo contract is in place.",
    "Research protocol draft contract is in place.",
    "Protocol review gate contract is in place.",
    "Data contract planning contract is in place.",
    "Data QA contract is in place.",
    "Research runner contract is in place.",
    "Orchestrator contract is in place.",
    "Dashboard registry feed contract is in place.",
    "Decision ledger contract is in place.",
    "Safety kill switch contract is in place.",
    "End to end fake pipeline contract is in place.",
)

# Runtime-write capability NAMES that stay blocked after closure -- labels only.
_REMAINING_RUNTIME_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "runtime_state_write",
    "ledger_runtime_write",
    "dashboard_runtime_update",
    "registry_file_write",
    "runtime_approval_write",
    "runtime_safety_flag_write",
    "template_edit",
    "file_write",
    "subprocess",
    "network",
    "pipeline_execution",
)

# Data capability NAMES that stay blocked after closure -- labels only.
_REMAINING_DATA_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "data_fetch",
    "market_data_inspection",
    "real_data_load",
    "real_data_transform",
    "real_data_compute",
    "backtest",
    "simulation",
)

# Trading capability NAMES that stay blocked after closure -- labels only.
_REMAINING_TRADING_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "promotion",
    "upload",
    "autopilot",
    "deploy",
)

# Deterministic, verb-safe next steps that only a human may take.
_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human must review every contract template by hand.",
    "A human must author any real workflow out of band.",
    "A human must keep all safety posture keys disabled.",
    "No automated step may proceed without human sign-off.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a closure report template and is execution-free.",
    "It writes no runtime state and changes nothing.",
    "The v1 backbone is template-only and not wired into runtime.",
    "A human must decide whether to plan a fake-artifact smoke test next.",
)

# Capabilities that stay blocked for every report, regardless of state.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "data_fetch",
    "backtest",
    "simulation",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "upload",
    "autopilot",
    "promotion",
    "subprocess",
    "network",
    "file_write",
    "dashboard_runtime_update",
    "registry_file_write",
    "template_edit",
    "ledger_runtime_write",
    "runtime_approval_write",
    "runtime_safety_flag_write",
    "pipeline_execution",
    "runtime_state_write",
)

_AUTH_FLAGS: tuple[str, ...] = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)

# Top-level schema fields required for a report to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# report to embed its own validation result would be circular.
_REQUIRED_REPORT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "end_to_end_fake_pipeline_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "backbone_closure_report_active",
    "backbone_closure_state",
    "end_to_end_fake_pipeline_contract_active",
    "end_to_end_fake_pipeline_next_gate",
    "asset_lane",
    "timeframe_lane",
    "completed_bundle_range",
    "completed_contract_chain_summary",
    "final_backbone_status",
    "remaining_runtime_capabilities_blocked",
    "remaining_data_capabilities_blocked",
    "remaining_trading_capabilities_blocked",
    "human_operator_required_next_steps",
    "recommended_next_phase",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "end_to_end_fake_pipeline_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _pipeline_field(pipeline: Any, key: str) -> str:
    """Read a string field from a possibly-malformed pipeline contract; safe."""
    return _as_text(pipeline.get(key)) if isinstance(pipeline, dict) else ""


def _validate(report: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a report dict (no I/O)."""
    safe = report if isinstance(report, dict) else {}

    missing = tuple(f for f in _REQUIRED_REPORT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    plan_only = safe.get("stage") == "PLAN_ONLY"
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )
    chain = tuple(safe.get("completed_contract_chain_summary") or ())
    steps = tuple(safe.get("human_operator_required_next_steps") or ())
    phase_ok = safe.get("recommended_next_phase") == RECOMMENDED_NEXT_PHASE
    fields_ok = len(chain) >= 1 and len(steps) >= 1 and phase_ok

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and fields_ok
        and not missing
    )

    return {
        "valid": valid,
        "schema_version_ok": schema_ok,
        "read_only": read_only,
        "research_only": research_only,
        "plan_only": plan_only,
        "human_approval_required": human_required,
        "executes": False,
        "all_authorization_flags_false": auth_all_false,
        "safety_all_false": safety_all_false,
        "recommended_next_phase_ok": phase_ok,
        "chain_and_steps_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_backbone_closure_report(
    report: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a backbone closure report template.
    Pure; no I/O."""
    return _validate(report)


def build_backbone_closure_report(pipeline: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only Strategy Factory v1 backbone
    closure report template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The report becomes active
    (backbone_closure_report_active=True) solely when the upstream Bundle 27
    end-to-end fake pipeline contract is active AND its next_gate is
    BACKBONE_CLOSURE_REPORT_REQUIRED. Even when active, every authorization
    field stays False -- it summarizes a completed template chain only, writes
    no runtime state, accesses no data, and grants nothing. Returned dicts are
    fresh."""
    pipeline_active = (
        isinstance(pipeline, dict)
        and pipeline.get("end_to_end_fake_pipeline_contract_active") is True
    )
    pipeline_next_gate = _pipeline_field(pipeline, "next_gate")
    report_active = bool(
        pipeline_active
        and pipeline_next_gate == NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED
    )
    state = (
        BACKBONE_CLOSURE_STATE_ACTIVE
        if report_active
        else BACKBONE_CLOSURE_STATE_BLOCKED
    )
    final_status = (
        FINAL_BACKBONE_STATUS_COMPLETE
        if report_active
        else "STRATEGY_FACTORY_V1_BACKBONE_INCOMPLETE"
    )
    next_gate = (
        NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW
        if report_active
        else NEXT_GATE_AWAIT_END_TO_END_FAKE_PIPELINE_CONTRACT
    )

    report = {
        "schema_version": BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION,
        "end_to_end_fake_pipeline_contract_schema_version": (
            END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _pipeline_field(pipeline, "idea_id"),
        "title": _pipeline_field(pipeline, "title"),
        "label": DEFAULT_BACKBONE_CLOSURE_REPORT_LABEL,
        "status": BACKBONE_CLOSURE_REPORT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "backbone_closure_report_active": report_active,
        "backbone_closure_state": state,
        "end_to_end_fake_pipeline_contract_active": bool(pipeline_active),
        "end_to_end_fake_pipeline_next_gate": pipeline_next_gate,
        "asset_lane": _pipeline_field(pipeline, "asset_lane"),
        "timeframe_lane": _pipeline_field(pipeline, "timeframe_lane"),
        "completed_bundle_range": _COMPLETED_BUNDLE_RANGE,
        "completed_contract_chain_summary": (
            _COMPLETED_CONTRACT_CHAIN_SUMMARY
        ),
        "final_backbone_status": final_status,
        "remaining_runtime_capabilities_blocked": (
            _REMAINING_RUNTIME_CAPABILITIES_BLOCKED
        ),
        "remaining_data_capabilities_blocked": (
            _REMAINING_DATA_CAPABILITIES_BLOCKED
        ),
        "remaining_trading_capabilities_blocked": (
            _REMAINING_TRADING_CAPABILITIES_BLOCKED
        ),
        "human_operator_required_next_steps": (
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "safety_posture": _safety_posture(),
        "next_gate": next_gate,
        "operator_notes": _OPERATOR_NOTES,
        "approved_for_research": False,
        "execution_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "data_fetch_authorized": False,
        "backtest_authorized": False,
        "promotion_authorized": False,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "end_to_end_fake_pipeline_contract": (
            pipeline if isinstance(pipeline, dict) else {}
        ),
    }
    report["validation"] = _validate(report)
    return report


def render_backbone_closure_report_markdown(
    report: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a backbone closure report
    template. Pure; writes no file. Informational only."""
    chain = report.get("completed_contract_chain_summary") or ()
    runtime_blocked = report.get("remaining_runtime_capabilities_blocked") or ()
    data_blocked = report.get("remaining_data_capabilities_blocked") or ()
    trading_blocked = report.get("remaining_trading_capabilities_blocked") or ()
    steps = report.get("human_operator_required_next_steps") or ()
    notes = report.get("operator_notes") or ()
    posture = report.get("safety_posture") or {}
    validation = report.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory v1 Backbone Closure Report")
    lines.append("")
    lines.append(
        "Template only: this is a backbone-closure-report-only template -- "
        "no-runtime-state-write, research-only, and execution-free. It is not "
        "wired into any runtime state, accesses no data, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{report.get('schema_version', '')}`")
    lines.append(
        "Pipeline schema: "
        f"`{report.get('end_to_end_fake_pipeline_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {report.get('idea_id', '')}")
    lines.append(f"Title: {report.get('title', '')}")
    lines.append(f"Status: {report.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Backbone closure report active: "
        f"{report.get('backbone_closure_report_active', '')}"
    )
    lines.append(
        f"Closure state: {report.get('backbone_closure_state', '')}"
    )
    lines.append(
        f"Completed bundle range: {report.get('completed_bundle_range', '')}"
    )
    lines.append(
        f"Final backbone status: {report.get('final_backbone_status', '')}"
    )
    lines.append(
        f"Recommended next phase: {report.get('recommended_next_phase', '')}"
    )
    lines.append(f"Next gate: {report.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {report.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {report.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Completed Contract Chain Summary")
    lines.append("")
    for x in chain:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Remaining Runtime Capabilities Blocked")
    lines.append("")
    for x in runtime_blocked:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Remaining Data Capabilities Blocked")
    lines.append("")
    for x in data_blocked:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Remaining Trading Capabilities Blocked")
    lines.append("")
    for x in trading_blocked:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Human Operator Required Next Steps")
    lines.append("")
    for x in steps:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in report.get("blocked_capabilities") or ():
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Operator Notes")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in posture.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for key, value in validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must pause here and review the closed backbone before any "
        "later phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
