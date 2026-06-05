"""SPARTA Offline Strategy Factory - DRY-RUN ORCHESTRATOR CONTRACT (TEMPLATE) v1.

Bundle 23 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only dry-run orchestrator contract template* builder: it
consumes a Bundle 22 research runner contract and, only when that contract is
active with next_gate == DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED, produces a
deterministic, read-only *template* describing the shape a future
human-authored dry-run orchestrator must take. The template references only
fake/sample artifact placeholders -- never real artifacts and never real data.
It defines an orchestrator contract template only -- NOT a runnable
orchestrator.

It never orchestrates anything, never performs research, never backtests,
never simulates, never fetches, inspects, loads, validates, transforms, or
computes on real data, and executes nothing. It opens no network, spawns no
subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL
  - DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS
  - DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE
  - DRY_RUN_ORCHESTRATOR_STATE_ACTIVE
  - DRY_RUN_ORCHESTRATOR_STATE_BLOCKED
  - NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED
  - NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT
  - build_dry_run_orchestrator_contract(runner)
  - validate_dry_run_orchestrator_contract(contract)
  - render_dry_run_orchestrator_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_runner_contract import (
    RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION,
    RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED,
)

__all__ = [
    "DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL",
    "DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS",
    "DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE",
    "DRY_RUN_ORCHESTRATOR_STATE_ACTIVE",
    "DRY_RUN_ORCHESTRATOR_STATE_BLOCKED",
    "NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED",
    "NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT",
    "build_dry_run_orchestrator_contract",
    "validate_dry_run_orchestrator_contract",
    "render_dry_run_orchestrator_contract_markdown",
]

DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_dry_run_orchestrator_contract.v1"
)
DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL = (
    "Strategy Factory Dry Run Orchestrator Contract"
)
DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS = (
    "READ_ONLY_DRY_RUN_ORCHESTRATOR_CONTRACT"
)

DRY_RUN_ORCHESTRATOR_STATE_ACTIVE = "DRY_RUN_ORCHESTRATOR_CONTRACT_ACTIVE"
DRY_RUN_ORCHESTRATOR_STATE_BLOCKED = "DRY_RUN_ORCHESTRATOR_CONTRACT_BLOCKED"

NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED = "DASHBOARD_REGISTRY_FEED_REQUIRED"
NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT = "AWAIT_RESEARCH_RUNNER_CONTRACT"

# Inherited all-false safety posture (same keys as Bundle 22). Pinned False:
# an orchestrator contract template only describes a future shape; grants none.
DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE
)

# Fake/sample artifact INPUT names a future orchestrator would consume --
# placeholder labels only, never real artifacts and never data.
_FAKE_ARTIFACT_INPUTS_REQUIRED: tuple[str, ...] = (
    "sample_protocol_artifact",
    "sample_data_contract_artifact",
    "sample_data_qa_artifact",
    "sample_runner_contract_artifact",
    "sample_parameter_grid_artifact",
)

# Fake/sample artifact OUTPUT names a future orchestrator would emit --
# placeholder labels only, never real artifacts and never data.
_FAKE_ARTIFACT_OUTPUTS_REQUIRED: tuple[str, ...] = (
    "sample_summary_metrics_artifact",
    "sample_equity_curve_artifact",
    "sample_position_log_artifact",
    "sample_orchestration_trace_artifact",
    "sample_orchestration_manifest_artifact",
)

# Trace field NAMES a future orchestrator trace must carry -- labels only.
_EXPECTED_TRACE_FIELDS: tuple[str, ...] = (
    "step_index",
    "step_name",
    "artifact_reference",
    "status_placeholder",
    "timestamp_placeholder",
    "notes_placeholder",
)

# Operator review field NAMES a human reviewer would check -- labels only.
_EXPECTED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "trace_completeness",
    "artifact_reference_integrity",
    "failure_mode_coverage",
    "reproducibility_manifest_presence",
    "human_sign_off_placeholder",
)

# Deterministic, verb-safe placeholder orchestration steps (descriptions only).
_ORCHESTRATION_STEPS_PLACEHOLDER: tuple[str, ...] = (
    "Resolve and bind the placeholder artifact references.",
    "Assemble the parameter set for a later human-authored orchestrator.",
    "Coordinate the ordered placeholder stages without computing anything.",
    "Collect placeholder trace records into a manifest.",
    "Hand the placeholder manifest to a human for review.",
)

# Deterministic, verb-safe expected failure-mode descriptions.
_EXPECTED_FAILURE_MODES: tuple[str, ...] = (
    "A placeholder artifact reference is missing or malformed.",
    "The orchestration step sequence is incomplete.",
    "The placeholder trace manifest is missing required fields.",
    "Operator review fields are absent.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only orchestrator contract and is execution-free.",
    "A human must author the real orchestrator out of band.",
    "No orchestration is performed, no data is loaded, and nothing is "
    "computed by this template.",
    "All referenced artifacts are fake/sample placeholders only.",
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
    "research_runner_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "dry_run_orchestrator_contract_active",
    "dry_run_orchestrator_state",
    "runner_contract_active",
    "runner_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_protocol_reference_placeholder",
    "source_data_contract_reference_placeholder",
    "source_data_qa_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "fake_artifact_inputs_required",
    "fake_artifact_outputs_required",
    "orchestration_steps_placeholder",
    "expected_trace_fields",
    "expected_failure_modes",
    "expected_operator_review_fields",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "research_runner_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _runner_field(runner: Any, key: str) -> str:
    """Read a string field from a possibly-malformed runner contract; safe."""
    return _as_text(runner.get(key)) if isinstance(runner, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION
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
    inputs = tuple(safe.get("fake_artifact_inputs_required") or ())
    outputs = tuple(safe.get("fake_artifact_outputs_required") or ())
    io_ok = len(inputs) >= 1 and len(outputs) >= 1

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and io_ok
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
        "fake_artifact_io_present": io_ok,
        "missing_required_fields": missing,
    }


def validate_dry_run_orchestrator_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a dry-run orchestrator contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_dry_run_orchestrator_contract(runner: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only dry-run orchestrator contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (dry_run_orchestrator_contract_active=True) solely when the upstream
    Bundle 22 research runner contract is active AND its next_gate is
    DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it defines an orchestrator contract
    template only, orchestrates nothing, accesses no data, references only
    fake/sample placeholders, and grants nothing. Returned dicts are fresh."""
    runner_active = (
        isinstance(runner, dict)
        and runner.get("runner_contract_active") is True
    )
    runner_next_gate = _runner_field(runner, "next_gate")
    contract_active = bool(
        runner_active
        and runner_next_gate
        == NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED
    )
    state = (
        DRY_RUN_ORCHESTRATOR_STATE_ACTIVE
        if contract_active
        else DRY_RUN_ORCHESTRATOR_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_RESEARCH_RUNNER_CONTRACT
    )

    contract = {
        "schema_version": DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION,
        "research_runner_contract_schema_version": (
            RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _runner_field(runner, "idea_id"),
        "title": _runner_field(runner, "title"),
        "label": DEFAULT_DRY_RUN_ORCHESTRATOR_CONTRACT_LABEL,
        "status": DRY_RUN_ORCHESTRATOR_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "dry_run_orchestrator_contract_active": contract_active,
        "dry_run_orchestrator_state": state,
        "runner_contract_active": bool(runner_active),
        "runner_next_gate": runner_next_gate,
        "asset_lane": _runner_field(runner, "asset_lane"),
        "timeframe_lane": _runner_field(runner, "timeframe_lane"),
        "source_protocol_reference_placeholder": (
            "Source protocol reference is a placeholder for a later "
            "human-authored orchestrator contract."
        ),
        "source_data_contract_reference_placeholder": (
            "Source data contract reference is a placeholder for a later "
            "human-authored orchestrator contract."
        ),
        "source_data_qa_reference_placeholder": (
            "Source data QA reference is a placeholder for a later "
            "human-authored orchestrator contract."
        ),
        "source_runner_contract_reference_placeholder": (
            "Source runner contract reference is a placeholder for a later "
            "human-authored orchestrator contract."
        ),
        "fake_artifact_inputs_required": _FAKE_ARTIFACT_INPUTS_REQUIRED,
        "fake_artifact_outputs_required": _FAKE_ARTIFACT_OUTPUTS_REQUIRED,
        "orchestration_steps_placeholder": _ORCHESTRATION_STEPS_PLACEHOLDER,
        "expected_trace_fields": _EXPECTED_TRACE_FIELDS,
        "expected_failure_modes": _EXPECTED_FAILURE_MODES,
        "expected_operator_review_fields": _EXPECTED_OPERATOR_REVIEW_FIELDS,
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
        "research_runner_contract": (
            runner if isinstance(runner, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_dry_run_orchestrator_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for an orchestrator contract
    template. Pure; writes no file. Informational only."""
    inputs = contract.get("fake_artifact_inputs_required") or ()
    outputs = contract.get("fake_artifact_outputs_required") or ()
    steps = contract.get("orchestration_steps_placeholder") or ()
    trace = contract.get("expected_trace_fields") or ()
    failures = contract.get("expected_failure_modes") or ()
    review = contract.get("expected_operator_review_fields") or ()
    blocked = contract.get("blocked_capabilities") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Dry Run Orchestrator Contract")
    lines.append("")
    lines.append(
        "Template only: this is a dry-run-orchestrator-contract-only "
        "template -- fake-artifact-placeholders-only, research-only, and "
        "execution-free. It references no real artifact, accesses no data, "
        "and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Runner schema: "
        f"`{contract.get('research_runner_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Dry run orchestrator contract active: "
        f"{contract.get('dry_run_orchestrator_contract_active', '')}"
    )
    lines.append(
        f"Orchestrator state: {contract.get('dry_run_orchestrator_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Fake Artifact Inputs Required")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Artifact Outputs Required")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Orchestration Steps Placeholder")
    lines.append("")
    for x in steps:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Expected Trace Fields")
    lines.append("")
    for x in trace:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Failure Modes")
    lines.append("")
    for x in failures:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Expected Operator Review Fields")
    lines.append("")
    for x in review:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in blocked:
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
        "- A human must author the real orchestrator before the dashboard "
        "registry feed is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
