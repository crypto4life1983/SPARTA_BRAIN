"""SPARTA Offline Strategy Factory - END-TO-END FAKE PIPELINE CONTRACT
(TEMPLATE) v1.

Bundle 27 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only end-to-end fake pipeline contract template* builder: it
consumes a Bundle 26 safety kill-switch / approval gate contract and, only when
that contract is active with next_gate ==
END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED, produces a deterministic, read-only
*template* describing the shape a future end-to-end fake-artifact pipeline
review must take. It defines a pipeline contract template only -- NOT a live
pipeline, and every artifact it references is a FAKE placeholder only.

It never runs the pipeline, never writes runtime state, never persists an
approval, never writes a ledger file, never updates runtime state, never
updates dashboard files, never orchestrates anything, never performs research,
never backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, touches no broker/exchange/
order/trading/live/distribution/autopilot surface, promotes/deploys nothing,
and records no approval decision. It records no timestamp, mints no random id,
and reads no environment.

Public API:
  - END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION
  - DEFAULT_END_TO_END_FAKE_PIPELINE_CONTRACT_LABEL
  - END_TO_END_FAKE_PIPELINE_CONTRACT_STATUS
  - END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE
  - END_TO_END_FAKE_PIPELINE_STATE_ACTIVE
  - END_TO_END_FAKE_PIPELINE_STATE_BLOCKED
  - NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED
  - NEXT_GATE_AWAIT_SAFETY_KILL_SWITCH_CONTRACT
  - build_end_to_end_fake_pipeline_contract(safety_gate)
  - validate_end_to_end_fake_pipeline_contract(contract)
  - render_end_to_end_fake_pipeline_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_safety_kill_switch_contract import (
    SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION,
    SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED,
)

__all__ = [
    "END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_END_TO_END_FAKE_PIPELINE_CONTRACT_LABEL",
    "END_TO_END_FAKE_PIPELINE_CONTRACT_STATUS",
    "END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE",
    "END_TO_END_FAKE_PIPELINE_STATE_ACTIVE",
    "END_TO_END_FAKE_PIPELINE_STATE_BLOCKED",
    "NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED",
    "NEXT_GATE_AWAIT_SAFETY_KILL_SWITCH_CONTRACT",
    "build_end_to_end_fake_pipeline_contract",
    "validate_end_to_end_fake_pipeline_contract",
    "render_end_to_end_fake_pipeline_contract_markdown",
]

END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_end_to_end_fake_pipeline_contract.v1"
)
DEFAULT_END_TO_END_FAKE_PIPELINE_CONTRACT_LABEL = (
    "Strategy Factory End-to-End Fake Pipeline Contract"
)
END_TO_END_FAKE_PIPELINE_CONTRACT_STATUS = (
    "READ_ONLY_END_TO_END_FAKE_PIPELINE_CONTRACT"
)

END_TO_END_FAKE_PIPELINE_STATE_ACTIVE = (
    "END_TO_END_FAKE_PIPELINE_CONTRACT_ACTIVE"
)
END_TO_END_FAKE_PIPELINE_STATE_BLOCKED = (
    "END_TO_END_FAKE_PIPELINE_CONTRACT_BLOCKED"
)

NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED = (
    "BACKBONE_CLOSURE_REPORT_REQUIRED"
)
NEXT_GATE_AWAIT_SAFETY_KILL_SWITCH_CONTRACT = (
    "AWAIT_SAFETY_KILL_SWITCH_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 26). Pinned False:
# a pipeline contract template only describes a future shape over FAKE
# artifacts; it grants nothing and is never wired into runtime state.
END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE
)

# Ordered stage NAMES a future fake pipeline review would walk -- labels only.
_FAKE_PIPELINE_STAGE_SEQUENCE: tuple[str, ...] = (
    "research_queue_intake",
    "research_protocol_draft",
    "protocol_review_gate",
    "data_contract_planning",
    "data_qa_review",
    "research_runner_review",
    "dry_run_orchestrator_review",
    "dashboard_registry_feed_review",
    "decision_ledger_review",
    "safety_kill_switch_review",
)

# FAKE artifact input NAMES a future review would accept -- labels only.
_FAKE_ARTIFACT_INPUTS_REQUIRED: tuple[str, ...] = (
    "fake_idea_record_placeholder",
    "fake_protocol_draft_placeholder",
    "fake_data_contract_placeholder",
    "fake_data_qa_report_placeholder",
)

# FAKE artifact output NAMES a future review would expect -- labels only.
_FAKE_ARTIFACT_OUTPUTS_EXPECTED: tuple[str, ...] = (
    "fake_summary_metrics_placeholder",
    "fake_risk_metrics_placeholder",
    "fake_trace_manifest_placeholder",
    "fake_operator_review_packet_placeholder",
)

# Trace field NAMES a future review would carry -- labels only.
_EXPECTED_TRACE_FIELDS: tuple[str, ...] = (
    "trace_id_placeholder",
    "stage_name_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

# Operator review field NAMES a human would complete -- labels only.
_EXPECTED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

# Deterministic, verb-safe failure modes a future review would record.
_EXPECTED_FAILURE_MODES: tuple[str, ...] = (
    "A fake artifact placeholder is missing.",
    "A stage produced no expected output placeholder.",
    "A trace field is absent for a stage.",
    "A safety posture key is found enabled.",
    "An operator review field is missing.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only pipeline contract and is execution-free.",
    "Every artifact it names is a fake placeholder, never real output.",
    "It writes no runtime state and changes nothing.",
    "A human must author the real pipeline review out of band.",
    "No automated step may proceed without human sign-off.",
)

# Capabilities that stay blocked for every contract, regardless of state.
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

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "safety_kill_switch_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "end_to_end_fake_pipeline_contract_active",
    "end_to_end_fake_pipeline_state",
    "safety_kill_switch_contract_active",
    "safety_kill_switch_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_queue_reference_placeholder",
    "source_protocol_reference_placeholder",
    "source_data_contract_reference_placeholder",
    "source_data_qa_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "source_orchestrator_reference_placeholder",
    "source_dashboard_feed_reference_placeholder",
    "source_decision_ledger_reference_placeholder",
    "source_safety_gate_reference_placeholder",
    "fake_pipeline_stage_sequence",
    "fake_artifact_inputs_required",
    "fake_artifact_outputs_expected",
    "expected_trace_fields",
    "expected_operator_review_fields",
    "expected_failure_modes",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "safety_kill_switch_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(END_TO_END_FAKE_PIPELINE_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _gate_field(gate: Any, key: str) -> str:
    """Read a string field from a possibly-malformed gate contract; safe."""
    return _as_text(gate.get(key)) if isinstance(gate, dict) else ""


def _placeholder(label: str) -> str:
    """Deterministic reference placeholder string (no real artifact)."""
    return (
        f"{label} reference is a fake placeholder for a later human-authored "
        "pipeline contract."
    )


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION
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
    stages = tuple(safe.get("fake_pipeline_stage_sequence") or ())
    inputs = tuple(safe.get("fake_artifact_inputs_required") or ())
    outputs = tuple(safe.get("fake_artifact_outputs_expected") or ())
    fields_ok = len(stages) >= 1 and len(inputs) >= 1 and len(outputs) >= 1

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
        "stages_inputs_outputs_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_end_to_end_fake_pipeline_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake pipeline contract template.
    Pure; no I/O."""
    return _validate(contract)


def build_end_to_end_fake_pipeline_contract(safety_gate: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only end-to-end fake pipeline contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (end_to_end_fake_pipeline_contract_active=True) solely when the upstream
    Bundle 26 safety kill-switch contract is active AND its next_gate is
    END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it defines a pipeline contract template
    only over FAKE artifacts, writes no runtime state, accesses no data, and
    grants nothing. Returned dicts are fresh."""
    gate_active = (
        isinstance(safety_gate, dict)
        and safety_gate.get("safety_kill_switch_contract_active") is True
    )
    gate_next_gate = _gate_field(safety_gate, "next_gate")
    contract_active = bool(
        gate_active
        and gate_next_gate
        == NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED
    )
    state = (
        END_TO_END_FAKE_PIPELINE_STATE_ACTIVE
        if contract_active
        else END_TO_END_FAKE_PIPELINE_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_BACKBONE_CLOSURE_REPORT_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_SAFETY_KILL_SWITCH_CONTRACT
    )

    contract = {
        "schema_version": END_TO_END_FAKE_PIPELINE_CONTRACT_SCHEMA_VERSION,
        "safety_kill_switch_contract_schema_version": (
            SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _gate_field(safety_gate, "idea_id"),
        "title": _gate_field(safety_gate, "title"),
        "label": DEFAULT_END_TO_END_FAKE_PIPELINE_CONTRACT_LABEL,
        "status": END_TO_END_FAKE_PIPELINE_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "end_to_end_fake_pipeline_contract_active": contract_active,
        "end_to_end_fake_pipeline_state": state,
        "safety_kill_switch_contract_active": bool(gate_active),
        "safety_kill_switch_next_gate": gate_next_gate,
        "asset_lane": _gate_field(safety_gate, "asset_lane"),
        "timeframe_lane": _gate_field(safety_gate, "timeframe_lane"),
        "source_queue_reference_placeholder": _placeholder("Source queue"),
        "source_protocol_reference_placeholder": _placeholder(
            "Source protocol"),
        "source_data_contract_reference_placeholder": _placeholder(
            "Source data contract"),
        "source_data_qa_reference_placeholder": _placeholder(
            "Source data QA"),
        "source_runner_contract_reference_placeholder": _placeholder(
            "Source runner contract"),
        "source_orchestrator_reference_placeholder": _placeholder(
            "Source orchestrator"),
        "source_dashboard_feed_reference_placeholder": _placeholder(
            "Source dashboard feed"),
        "source_decision_ledger_reference_placeholder": _placeholder(
            "Source decision ledger"),
        "source_safety_gate_reference_placeholder": _placeholder(
            "Source safety gate"),
        "fake_pipeline_stage_sequence": _FAKE_PIPELINE_STAGE_SEQUENCE,
        "fake_artifact_inputs_required": _FAKE_ARTIFACT_INPUTS_REQUIRED,
        "fake_artifact_outputs_expected": _FAKE_ARTIFACT_OUTPUTS_EXPECTED,
        "expected_trace_fields": _EXPECTED_TRACE_FIELDS,
        "expected_operator_review_fields": _EXPECTED_OPERATOR_REVIEW_FIELDS,
        "expected_failure_modes": _EXPECTED_FAILURE_MODES,
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
        "safety_kill_switch_contract": (
            safety_gate if isinstance(safety_gate, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_end_to_end_fake_pipeline_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake pipeline contract
    template. Pure; writes no file. Informational only."""
    stages = contract.get("fake_pipeline_stage_sequence") or ()
    inputs = contract.get("fake_artifact_inputs_required") or ()
    outputs = contract.get("fake_artifact_outputs_expected") or ()
    trace = contract.get("expected_trace_fields") or ()
    review = contract.get("expected_operator_review_fields") or ()
    failures = contract.get("expected_failure_modes") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    _source_keys = (
        ("Queue", "source_queue_reference_placeholder"),
        ("Protocol", "source_protocol_reference_placeholder"),
        ("Data contract", "source_data_contract_reference_placeholder"),
        ("Data QA", "source_data_qa_reference_placeholder"),
        ("Runner contract", "source_runner_contract_reference_placeholder"),
        ("Orchestrator", "source_orchestrator_reference_placeholder"),
        ("Dashboard feed", "source_dashboard_feed_reference_placeholder"),
        ("Decision ledger", "source_decision_ledger_reference_placeholder"),
        ("Safety gate", "source_safety_gate_reference_placeholder"),
    )

    lines: list[str] = []
    lines.append("# Strategy Factory End-to-End Fake Pipeline Contract")
    lines.append("")
    lines.append(
        "Template only: this is an end-to-end-fake-pipeline-contract-only "
        "template -- fake-artifacts-only, no-runtime-state-write, "
        "research-only, and execution-free. It is not wired into any runtime "
        "state, accesses no data, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Gate schema: "
        f"`{contract.get('safety_kill_switch_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "End to end fake pipeline contract active: "
        f"{contract.get('end_to_end_fake_pipeline_contract_active', '')}"
    )
    lines.append(
        f"Pipeline state: {contract.get('end_to_end_fake_pipeline_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source References")
    lines.append("")
    for label, key in _source_keys:
        lines.append(f"- `{label}`: {contract.get(key, '')}")
    lines.append("")
    lines.append("## Fake Pipeline Stage Sequence")
    lines.append("")
    for x in stages:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Artifact Inputs Required")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Artifact Outputs Expected")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Trace Fields")
    lines.append("")
    for x in trace:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Operator Review Fields")
    lines.append("")
    for x in review:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Failure Modes")
    lines.append("")
    for x in failures:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in contract.get("blocked_capabilities") or ():
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
        "- A human must author the real pipeline review before the backbone "
        "closure report is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
