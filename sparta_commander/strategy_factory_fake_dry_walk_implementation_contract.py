"""SPARTA Offline Strategy Factory - FAKE DRY-WALK IMPLEMENTATION CONTRACT (TEMPLATE).

Bundle 32 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only planning contract template* builder: it consumes a
Bundle 31 fake dry-walk operator review gate and, only when that gate is active
with operator_decision == READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT and
next_gate == FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED, produces a
deterministic, read-only contract describing the SHAPE and safety rules a
future fake-only, in-memory dry-walk implementation must obey. It defines a
planning template only -- the dry walk is NOT implemented here, NOT a live
system, NOT a dry walk, NOT a smoke test, NOT a pipeline run.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs the dry walk, never implements the dry walk, never runs
an orchestrator, never writes runtime state, never persists an approval, never
writes a ledger file, never updates dashboard files, never writes a registry
file, never performs research, never runs QA, never runs a baseline, never
backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL
  - DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS
  - DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE
  - IMPLEMENTATION_STATE_ACTIVE
  - IMPLEMENTATION_STATE_BLOCKED
  - NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE
  - IMPLEMENTATION_SCOPE
  - ALLOWED_IN_MEMORY_INPUTS
  - ALLOWED_IN_MEMORY_OUTPUTS
  - DRY_WALK_FUNCTION_CONTRACT
  - STAGE_WALK_CONTRACT
  - TRACE_RECORD_CONTRACT
  - OPERATOR_REVIEW_PACKET_CONTRACT
  - PROHIBITED_REAL_ARTIFACT_REFERENCES
  - PROHIBITED_RUNTIME_SIDE_EFFECTS
  - build_fake_dry_walk_implementation_contract(operator_gate)
  - validate_fake_dry_walk_implementation_contract(contract)
  - render_fake_dry_walk_implementation_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (  # noqa: E501
    DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION,
    DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE,
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED,
)
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    FORBIDDEN_REAL_ARTIFACT_TOKENS,
)

__all__ = [
    "DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL",
    "DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS",
    "DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE",
    "IMPLEMENTATION_STATE_ACTIVE",
    "IMPLEMENTATION_STATE_BLOCKED",
    "NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE",
    "IMPLEMENTATION_SCOPE",
    "ALLOWED_IN_MEMORY_INPUTS",
    "ALLOWED_IN_MEMORY_OUTPUTS",
    "DRY_WALK_FUNCTION_CONTRACT",
    "STAGE_WALK_CONTRACT",
    "TRACE_RECORD_CONTRACT",
    "OPERATOR_REVIEW_PACKET_CONTRACT",
    "PROHIBITED_REAL_ARTIFACT_REFERENCES",
    "PROHIBITED_RUNTIME_SIDE_EFFECTS",
    "build_fake_dry_walk_implementation_contract",
    "validate_fake_dry_walk_implementation_contract",
    "render_fake_dry_walk_implementation_contract_markdown",
]

DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_dry_walk_implementation_contract.v1"
)
DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL = (
    "Strategy Factory Fake Dry Walk Implementation Contract"
)
DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS = (
    "READ_ONLY_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
)

IMPLEMENTATION_STATE_ACTIVE = "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_ACTIVE"
IMPLEMENTATION_STATE_BLOCKED = "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_BLOCKED"

NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED = (
    "FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE = (
    "AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"
)

# The hard scope a future fake-only implementation must obey -- labels only.
IMPLEMENTATION_SCOPE: tuple[str, ...] = (
    "fake_only",
    "in_memory_only",
    "deterministic",
    "no_real_data",
    "no_runtime_write",
    "no_execution_authority",
)

# Inherited all-false safety posture (same keys as Bundle 31). Pinned False:
# a planning contract template only describes a future implementation; it
# grants nothing and is never wired into runtime state.
DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE
)

# FAKE in-memory input placeholder NAMES -- labels only, fake/placeholder-only.
ALLOWED_IN_MEMORY_INPUTS: tuple[str, ...] = (
    "fake_idea_record_placeholder",
    "fake_protocol_draft_placeholder",
    "fake_data_contract_placeholder",
    "fake_data_qa_report_placeholder",
    "fake_stage_input_placeholder",
)

# FAKE in-memory output placeholder NAMES -- labels only, fake/placeholder-only.
ALLOWED_IN_MEMORY_OUTPUTS: tuple[str, ...] = (
    "fake_summary_metrics_placeholder",
    "fake_risk_metrics_placeholder",
    "fake_trace_manifest_placeholder",
    "fake_operator_review_packet_placeholder",
    "fake_stage_output_placeholder",
)

# Shape a future dry-walk function must obey -- labels only, no implementation.
DRY_WALK_FUNCTION_CONTRACT: tuple[str, ...] = (
    "accepts_fake_in_memory_inputs_only",
    "returns_fake_in_memory_outputs_only",
    "is_pure_and_deterministic",
    "raises_no_unhandled_exception_on_malformed_input",
    "performs_no_input_output_side_effect",
    "grants_no_execution_authority",
)

# Shape a future per-stage walk must obey -- labels only.
STAGE_WALK_CONTRACT: tuple[str, ...] = (
    "walks_each_fake_stage_in_declared_order",
    "carries_one_fake_input_placeholder_per_stage",
    "carries_one_fake_output_placeholder_per_stage",
    "records_one_fake_trace_record_per_stage",
    "halts_on_any_safety_violation_placeholder",
)

# Shape a future per-stage trace record must carry -- labels only.
TRACE_RECORD_CONTRACT: tuple[str, ...] = (
    "stage_name_placeholder",
    "input_placeholder_ref",
    "output_placeholder_ref",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

# Shape a future operator review packet must carry -- labels only.
OPERATOR_REVIEW_PACKET_CONTRACT: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "fake_summary_assessment_placeholder",
    "blocking_findings_placeholder",
    "safety_attestation_placeholder",
    "human_sign_off_placeholder",
)

# Real artifact references a future implementation must never name.
PROHIBITED_REAL_ARTIFACT_REFERENCES: tuple[str, ...] = (
    "Crypto-D1",
    "qa_report.json",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees.json",
    "dataset_files",
    "baseline_outputs",
    ".csv",
    ".parquet",
    "real_market_data_paths",
)

# Runtime side effects a future implementation must never perform.
PROHIBITED_RUNTIME_SIDE_EFFECTS: tuple[str, ...] = (
    "file_write",
    "runtime_state_write",
    "dashboard_runtime_update",
    "registry_file_write",
    "ledger_runtime_write",
    "approval_persistence",
    "network",
    "subprocess",
    "broker_action",
    "exchange_action",
    "order_action",
    "live_or_paper_trading_action",
    "upload_or_autopilot_action",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake dry walk implementation contract template and is "
    "execution-free.",
    "The dry walk is not implemented here; this defines its future shape "
    "only.",
    "A future implementation must stay fake-only, in-memory-only, and "
    "deterministic.",
    "Every artifact it names is a fake placeholder, never real output.",
    "It writes no runtime state and accesses no data.",
    "A human must review the future build before any later phase is planned.",
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
    "smoke_test_execution",
    "dry_walk_execution",
    "operator_review_gate_execution",
    "dry_walk_implementation_execution",
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

# The source reference is a fake placeholder, never a real contract handle.
_SOURCE_OPERATOR_REVIEW_GATE_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Dry Walk Operator Review Gate reference is a fake "
    "placeholder for a later human-authored implementation build."
)

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_dry_walk_operator_review_gate_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_dry_walk_implementation_contract_active",
    "fake_dry_walk_implementation_state",
    "fake_dry_walk_operator_review_gate_active",
    "fake_dry_walk_operator_review_gate_decision",
    "fake_dry_walk_operator_review_gate_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_operator_review_gate_reference_placeholder",
    "implementation_scope",
    "allowed_in_memory_inputs",
    "allowed_in_memory_outputs",
    "dry_walk_function_contract",
    "stage_walk_contract",
    "trace_record_contract",
    "operator_review_packet_contract",
    "placeholder_only_guard",
    "prohibited_real_artifact_references",
    "prohibited_runtime_side_effects",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_dry_walk_operator_review_gate",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _gate_field(operator_gate: Any, key: str) -> str:
    """Read a string field from a possibly-malformed gate; safe."""
    return (
        _as_text(operator_gate.get(key))
        if isinstance(operator_gate, dict)
        else ""
    )


def _placeholder_only_guard(
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
) -> dict[str, Any]:
    """Pure deterministic placeholder-only guard. Confirms every in-memory
    input/output is a fake placeholder and references no real artifact."""
    names = tuple(inputs) + tuple(outputs)
    inputs_ph = all("fake" in n and "placeholder" in n for n in inputs)
    outputs_ph = all("fake" in n and "placeholder" in n for n in outputs)
    no_real = not any(
        tok in n.lower()
        for n in names
        for tok in FORBIDDEN_REAL_ARTIFACT_TOKENS
    )
    return {
        "all_inputs_placeholder_only": bool(inputs_ph),
        "all_outputs_placeholder_only": bool(outputs_ph),
        "no_real_artifact_reference": bool(no_real),
        "forbidden_real_artifact_tokens": FORBIDDEN_REAL_ARTIFACT_TOKENS,
        "guard_holds": bool(inputs_ph and outputs_ph and no_real),
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION
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
    scope = tuple(safe.get("implementation_scope") or ())
    inputs = tuple(safe.get("allowed_in_memory_inputs") or ())
    outputs = tuple(safe.get("allowed_in_memory_outputs") or ())
    prohibited_refs = tuple(
        safe.get("prohibited_real_artifact_references") or ()
    )
    prohibited_fx = tuple(safe.get("prohibited_runtime_side_effects") or ())
    guard = safe.get("placeholder_only_guard")
    guard_ok = isinstance(guard, dict) and guard.get("guard_holds") is True
    scope_ok = scope == tuple(IMPLEMENTATION_SCOPE)
    fields_ok = (
        scope_ok
        and len(inputs) >= 1
        and len(outputs) >= 1
        and len(prohibited_refs) >= 1
        and len(prohibited_fx) >= 1
    )

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
        and guard_ok
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
        "implementation_scope_matches": scope_ok,
        "placeholder_only_guard_holds": guard_ok,
        "inputs_outputs_prohibitions_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_fake_dry_walk_implementation_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake dry walk implementation
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_fake_dry_walk_implementation_contract(
    operator_gate: Any,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only Strategy Factory fake dry walk
    implementation contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The contract becomes active
    (fake_dry_walk_implementation_contract_active=True) solely when the
    upstream Bundle 31 operator review gate is active AND its operator_decision
    is READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT AND its next_gate is
    FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it describes the SHAPE of a future
    fake-only, in-memory implementation only, writes no runtime state, accesses
    no data, names only fake placeholders, and grants nothing. The dry walk is
    NOT implemented here. Returned dicts are fresh."""
    gate_active = (
        isinstance(operator_gate, dict)
        and operator_gate.get("fake_dry_walk_operator_review_gate_active")
        is True
    )
    gate_decision = _gate_field(operator_gate, "operator_decision")
    gate_next_gate = _gate_field(operator_gate, "next_gate")
    contract_active = bool(
        gate_active
        and gate_decision
        == OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        and gate_next_gate
        == NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED
    )
    state = (
        IMPLEMENTATION_STATE_ACTIVE
        if contract_active
        else IMPLEMENTATION_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE
    )

    contract = {
        "schema_version": DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION,
        "fake_dry_walk_operator_review_gate_schema_version": (
            DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION
        ),
        "idea_id": _gate_field(operator_gate, "idea_id"),
        "title": _gate_field(operator_gate, "title"),
        "label": DEFAULT_DRY_WALK_IMPLEMENTATION_CONTRACT_LABEL,
        "status": DRY_WALK_IMPLEMENTATION_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_dry_walk_implementation_contract_active": contract_active,
        "fake_dry_walk_implementation_state": state,
        "fake_dry_walk_operator_review_gate_active": bool(gate_active),
        "fake_dry_walk_operator_review_gate_decision": gate_decision,
        "fake_dry_walk_operator_review_gate_next_gate": gate_next_gate,
        "asset_lane": _gate_field(operator_gate, "asset_lane"),
        "timeframe_lane": _gate_field(operator_gate, "timeframe_lane"),
        "source_operator_review_gate_reference_placeholder": (
            _SOURCE_OPERATOR_REVIEW_GATE_REFERENCE_PLACEHOLDER
        ),
        "implementation_scope": IMPLEMENTATION_SCOPE,
        "allowed_in_memory_inputs": ALLOWED_IN_MEMORY_INPUTS,
        "allowed_in_memory_outputs": ALLOWED_IN_MEMORY_OUTPUTS,
        "dry_walk_function_contract": DRY_WALK_FUNCTION_CONTRACT,
        "stage_walk_contract": STAGE_WALK_CONTRACT,
        "trace_record_contract": TRACE_RECORD_CONTRACT,
        "operator_review_packet_contract": OPERATOR_REVIEW_PACKET_CONTRACT,
        "placeholder_only_guard": _placeholder_only_guard(
            ALLOWED_IN_MEMORY_INPUTS,
            ALLOWED_IN_MEMORY_OUTPUTS,
        ),
        "prohibited_real_artifact_references": (
            PROHIBITED_REAL_ARTIFACT_REFERENCES
        ),
        "prohibited_runtime_side_effects": PROHIBITED_RUNTIME_SIDE_EFFECTS,
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
        "fake_dry_walk_operator_review_gate": (
            operator_gate if isinstance(operator_gate, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_dry_walk_implementation_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake dry walk
    implementation contract template. Pure; writes no file. Informational."""
    scope = contract.get("implementation_scope") or ()
    inputs = contract.get("allowed_in_memory_inputs") or ()
    outputs = contract.get("allowed_in_memory_outputs") or ()
    fn_contract = contract.get("dry_walk_function_contract") or ()
    stage_contract = contract.get("stage_walk_contract") or ()
    trace_contract = contract.get("trace_record_contract") or ()
    packet_contract = contract.get("operator_review_packet_contract") or ()
    guard = contract.get("placeholder_only_guard") or {}
    prohibited_refs = contract.get("prohibited_real_artifact_references") or ()
    prohibited_fx = contract.get("prohibited_runtime_side_effects") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Fake Dry Walk Implementation Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a fake-dry-walk-implementation-contract-only, "
        "not-implemented-yet, planning-only, placeholder-only template -- "
        "no-runtime-state-write, research-only, and execution-free. The dry "
        "walk is not implemented here. It is not wired into any runtime state, "
        "accesses no data, names only fake placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Gate schema: "
        f"`{contract.get('fake_dry_walk_operator_review_gate_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake dry walk implementation contract active: "
        f"{contract.get('fake_dry_walk_implementation_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('fake_dry_walk_implementation_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source Reference")
    lines.append("")
    lines.append(
        "Source operator review gate reference: "
        f"{contract.get('source_operator_review_gate_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Implementation Scope")
    lines.append("")
    for x in scope:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed In Memory Inputs")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed In Memory Outputs")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Dry Walk Function Contract")
    lines.append("")
    for x in fn_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Stage Walk Contract")
    lines.append("")
    for x in stage_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Trace Record Contract")
    lines.append("")
    for x in trace_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Operator Review Packet Contract")
    lines.append("")
    for x in packet_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Placeholder Only Guard")
    lines.append("")
    for key, value in guard.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Prohibited Real Artifact References")
    lines.append("")
    for x in prohibited_refs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Prohibited Runtime Side Effects")
    lines.append("")
    for x in prohibited_fx:
        lines.append(f"- `{x}`")
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
        "- A human must review the future fake implementation build before "
        "any later phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
