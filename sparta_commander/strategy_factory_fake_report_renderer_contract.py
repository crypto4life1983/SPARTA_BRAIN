"""SPARTA Offline Strategy Factory - FAKE REPORT RENDERER CONTRACT.

Bundle 37 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only renderer contract template* builder: it consumes a
Bundle 36 fake walk report operator review gate and, only when that gate is
active with operator_decision == READY_FOR_FAKE_REPORT_RENDERER_CONTRACT and
next_gate == FAKE_REPORT_RENDERER_CONTRACT_REQUIRED, produces a deterministic,
read-only contract describing the SHAPE of a future in-memory fake report
renderer. It defines a renderer contract/template only -- the renderer is NOT
implemented yet. It renders nothing, writes no report, is NOT a written report,
NOT a live system, NOT a dry walk, NOT a pipeline, NOT an orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never renders a real report, never writes a
report file, never writes runtime state, never persists an approval, never
writes a ledger file, never updates dashboard files, never writes a registry
file, never performs research, never runs QA, never runs a baseline, never
backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, reads no file, lists no
directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - RENDERER_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RENDERER_CONTRACT_LABEL
  - RENDERER_CONTRACT_STATUS
  - RENDERER_CONTRACT_SAFETY_POSTURE
  - RENDERER_STATE_ACTIVE
  - RENDERER_STATE_BLOCKED
  - NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE
  - RENDERER_SCOPE
  - ALLOWED_IN_MEMORY_INPUTS
  - ALLOWED_IN_MEMORY_OUTPUTS
  - RENDERER_FUNCTION_CONTRACT
  - MARKDOWN_RENDER_CONTRACT
  - REPORT_SECTION_RENDER_CONTRACT
  - SAFETY_ATTESTATION_RENDER_CONTRACT
  - PROHIBITED_REAL_ARTIFACT_REFERENCES
  - PROHIBITED_RUNTIME_SIDE_EFFECTS
  - build_fake_report_renderer_contract(report_review_gate)
  - validate_fake_report_renderer_contract(contract)
  - render_fake_report_renderer_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_walk_report_operator_review_gate import (  # noqa: E501
    REPORT_REVIEW_GATE_SCHEMA_VERSION,
    REPORT_REVIEW_GATE_SAFETY_POSTURE,
    OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT,
    NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED,
)

__all__ = [
    "RENDERER_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RENDERER_CONTRACT_LABEL",
    "RENDERER_CONTRACT_STATUS",
    "RENDERER_CONTRACT_SAFETY_POSTURE",
    "RENDERER_STATE_ACTIVE",
    "RENDERER_STATE_BLOCKED",
    "NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE",
    "RENDERER_SCOPE",
    "ALLOWED_IN_MEMORY_INPUTS",
    "ALLOWED_IN_MEMORY_OUTPUTS",
    "RENDERER_FUNCTION_CONTRACT",
    "MARKDOWN_RENDER_CONTRACT",
    "REPORT_SECTION_RENDER_CONTRACT",
    "SAFETY_ATTESTATION_RENDER_CONTRACT",
    "PROHIBITED_REAL_ARTIFACT_REFERENCES",
    "PROHIBITED_RUNTIME_SIDE_EFFECTS",
    "build_fake_report_renderer_contract",
    "validate_fake_report_renderer_contract",
    "render_fake_report_renderer_contract_markdown",
]

RENDERER_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_report_renderer_contract.v1"
)
DEFAULT_RENDERER_CONTRACT_LABEL = (
    "Strategy Factory Fake Report Renderer Contract"
)
RENDERER_CONTRACT_STATUS = "READ_ONLY_FAKE_REPORT_RENDERER_CONTRACT"

RENDERER_STATE_ACTIVE = "FAKE_REPORT_RENDERER_CONTRACT_ACTIVE"
RENDERER_STATE_BLOCKED = "FAKE_REPORT_RENDERER_CONTRACT_BLOCKED"

NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED = (
    "FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE = (
    "AWAIT_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-36).
RENDERER_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    REPORT_REVIEW_GATE_SAFETY_POSTURE
)

# The future renderer's scope -- every entry is a hard read-only constraint.
RENDERER_SCOPE: tuple[str, ...] = (
    "fake_only",
    "in_memory_only",
    "deterministic",
    "no_real_data",
    "no_report_file_write",
    "no_runtime_write",
    "no_execution_authority",
)

# Inputs the future renderer may accept -- all fake/sample/placeholder only.
ALLOWED_IN_MEMORY_INPUTS: tuple[str, ...] = (
    "fake_walk_report_contract_placeholder",
    "fake_stage_summary_sample_placeholder",
    "fake_trace_summary_sample_placeholder",
    "fake_pass_fail_summary_sample_placeholder",
    "fake_operator_review_summary_sample_placeholder",
)

# Outputs the future renderer may produce -- all fake/sample/placeholder only.
ALLOWED_IN_MEMORY_OUTPUTS: tuple[str, ...] = (
    "fake_report_markdown_string_placeholder",
    "fake_report_section_map_sample_placeholder",
    "fake_safety_attestation_block_placeholder",
)

# Shape of the future renderer function -- a description, not a function.
RENDERER_FUNCTION_CONTRACT: tuple[str, ...] = (
    "future_function_name_placeholder",
    "future_input_fake_walk_report_contract_placeholder",
    "future_output_fake_markdown_string_placeholder",
    "future_purity_pure_deterministic_side_effect_free_placeholder",
)

# Shape of the future markdown render -- a description, not a render.
MARKDOWN_RENDER_CONTRACT: tuple[str, ...] = (
    "fake_markdown_header_placeholder",
    "fake_markdown_body_placeholder",
    "fake_markdown_safety_footer_placeholder",
    "deterministic_string_output_placeholder",
)

# Shape of the future per-section render -- a description, not a render.
REPORT_SECTION_RENDER_CONTRACT: tuple[str, ...] = (
    "executive_summary_render_placeholder",
    "fake_walk_scope_render_placeholder",
    "fake_stage_walk_summary_render_placeholder",
    "fake_trace_summary_render_placeholder",
    "operator_review_summary_render_placeholder",
    "pass_fail_summary_render_placeholder",
    "safety_attestation_render_placeholder",
    "blocked_capabilities_render_placeholder",
    "next_steps_render_placeholder",
)

# Shape of the future safety-attestation render -- a description, not a render.
SAFETY_ATTESTATION_RENDER_CONTRACT: tuple[str, ...] = (
    "read_only_attestation_render_placeholder",
    "execution_free_attestation_render_placeholder",
    "no_real_data_attestation_render_placeholder",
    "no_runtime_state_write_attestation_render_placeholder",
    "no_report_file_write_attestation_render_placeholder",
)

# Real artifacts the future renderer must NEVER reference (fake only).
PROHIBITED_REAL_ARTIFACT_REFERENCES: tuple[str, ...] = (
    "Crypto-D1",
    "qa_report.json",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees.json",
    "real_dataset_name",
    "baseline_output",
    ".csv",
    ".parquet",
    "real_market_data_path",
)

# Runtime side effects the future renderer must NEVER perform.
PROHIBITED_RUNTIME_SIDE_EFFECTS: tuple[str, ...] = (
    "file_write",
    "report_file_write",
    "runtime_state_write",
    "dashboard_update",
    "registry_write",
    "ledger_write",
    "network_call",
    "subprocess_spawn",
    "broker_exchange_order_action",
)

_PLACEHOLDER_ONLY_GUARD = (
    "Every input and output named here is a fake placeholder only. This "
    "renderer contract is not implemented yet and names no real artifact."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake report renderer contract template and is execution-free.",
    "It defines the shape of a future in-memory fake report renderer only.",
    "It is not implemented yet and writes no report file.",
    "It writes no runtime state and is planning-only.",
    "Every input and output it names is a fake placeholder, never real "
    "output.",
    "It accesses no data and names only fake placeholders.",
    "A human must approve the renderer build before any implementation is "
    "planned.",
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
    "file_read",
    "directory_listing",
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
    "result_review_execution",
    "report_file_write",
    "report_contract_execution",
    "report_render_execution",
    "report_operator_review_execution",
    "report_renderer_build_execution",
    "report_renderer_implementation_execution",
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

_SOURCE_FAKE_REPORT_REVIEW_GATE_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Walk Report Operator Review Gate reference is a "
    "fake placeholder for a later human-reviewed fake report renderer build."
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_walk_report_operator_review_gate_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_report_renderer_contract_active",
    "fake_report_renderer_contract_state",
    "fake_walk_report_operator_review_gate_active",
    "fake_walk_report_operator_review_gate_decision",
    "fake_walk_report_operator_review_gate_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_report_review_gate_reference_placeholder",
    "renderer_scope",
    "allowed_in_memory_inputs",
    "allowed_in_memory_outputs",
    "renderer_function_contract",
    "markdown_render_contract",
    "report_section_render_contract",
    "safety_attestation_render_contract",
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
    "fake_walk_report_operator_review_gate",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RENDERER_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(gate: Any, key: str) -> str:
    """Read a string field from a possibly-malformed gate; safe."""
    return _as_text(gate.get(key)) if isinstance(gate, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RENDERER_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_RENDERER_CONTRACT_ONLY")
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    scope_ok = tuple(safe.get("renderer_scope") or ()) == RENDERER_SCOPE
    inputs_ok = (
        tuple(safe.get("allowed_in_memory_inputs") or ())
        == ALLOWED_IN_MEMORY_INPUTS
    )
    outputs_ok = (
        tuple(safe.get("allowed_in_memory_outputs") or ())
        == ALLOWED_IN_MEMORY_OUTPUTS
    )
    fn_ok = (
        tuple(safe.get("renderer_function_contract") or ())
        == RENDERER_FUNCTION_CONTRACT
    )
    md_ok = (
        tuple(safe.get("markdown_render_contract") or ())
        == MARKDOWN_RENDER_CONTRACT
    )
    section_ok = (
        tuple(safe.get("report_section_render_contract") or ())
        == REPORT_SECTION_RENDER_CONTRACT
    )
    attestation_ok = (
        tuple(safe.get("safety_attestation_render_contract") or ())
        == SAFETY_ATTESTATION_RENDER_CONTRACT
    )
    prohibited_artifacts_ok = (
        tuple(safe.get("prohibited_real_artifact_references") or ())
        == PROHIBITED_REAL_ARTIFACT_REFERENCES
    )
    prohibited_effects_ok = (
        tuple(safe.get("prohibited_runtime_side_effects") or ())
        == PROHIBITED_RUNTIME_SIDE_EFFECTS
    )

    fields_ok = (
        scope_ok
        and inputs_ok
        and outputs_ok
        and fn_ok
        and md_ok
        and section_ok
        and attestation_ok
        and prohibited_artifacts_ok
        and prohibited_effects_ok
    )

    valid = bool(
        schema_ok
        and research_only
        and stage_ok
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
        "stage_ok": stage_ok,
        "human_approval_required": human_required,
        "executes": False,
        "all_authorization_flags_false": auth_all_false,
        "safety_all_false": safety_all_false,
        "renderer_scope_ok": scope_ok,
        "allowed_in_memory_inputs_ok": inputs_ok,
        "allowed_in_memory_outputs_ok": outputs_ok,
        "renderer_function_contract_ok": fn_ok,
        "markdown_render_contract_ok": md_ok,
        "report_section_render_contract_ok": section_ok,
        "safety_attestation_render_contract_ok": attestation_ok,
        "prohibited_real_artifact_references_ok": prohibited_artifacts_ok,
        "prohibited_runtime_side_effects_ok": prohibited_effects_ok,
        "missing_required_fields": missing,
    }


def validate_fake_report_renderer_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake report renderer contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_report_renderer_contract(
    report_review_gate: Any,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake report renderer contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (fake_report_renderer_contract_active=True) solely when the upstream
    Bundle 36 fake walk report operator review gate is active AND its
    operator_decision is READY_FOR_FAKE_REPORT_RENDERER_CONTRACT AND its
    next_gate is FAKE_REPORT_RENDERER_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it defines the SHAPE of a future
    in-memory fake report renderer only, the renderer is not implemented yet,
    it writes no report file, writes no runtime state, accesses no data, names
    only fake placeholders, and grants nothing. Returned dicts are fresh."""
    gate_active = (
        isinstance(report_review_gate, dict)
        and report_review_gate.get(
            "fake_walk_report_operator_review_gate_active"
        )
        is True
    )
    gate_decision = _field(report_review_gate, "operator_decision")
    gate_next_gate = _field(report_review_gate, "next_gate")
    ready = (
        gate_decision
        == OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
    )
    next_gate_ok = (
        gate_next_gate == NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED
    )
    renderer_active = bool(gate_active and ready and next_gate_ok)

    state = (
        RENDERER_STATE_ACTIVE if renderer_active else RENDERER_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED
        if renderer_active
        else NEXT_GATE_AWAIT_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE
    )

    contract = {
        "schema_version": RENDERER_CONTRACT_SCHEMA_VERSION,
        "fake_walk_report_operator_review_gate_schema_version": (
            REPORT_REVIEW_GATE_SCHEMA_VERSION
        ),
        "idea_id": _field(report_review_gate, "idea_id"),
        "title": _field(report_review_gate, "title"),
        "label": DEFAULT_RENDERER_CONTRACT_LABEL,
        "status": RENDERER_CONTRACT_STATUS,
        "stage": "FAKE_RENDERER_CONTRACT_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_report_renderer_contract_active": renderer_active,
        "fake_report_renderer_contract_state": state,
        "fake_walk_report_operator_review_gate_active": bool(gate_active),
        "fake_walk_report_operator_review_gate_decision": gate_decision,
        "fake_walk_report_operator_review_gate_next_gate": gate_next_gate,
        "asset_lane": _field(report_review_gate, "asset_lane"),
        "timeframe_lane": _field(report_review_gate, "timeframe_lane"),
        "source_fake_report_review_gate_reference_placeholder": (
            _SOURCE_FAKE_REPORT_REVIEW_GATE_REFERENCE_PLACEHOLDER
        ),
        "renderer_scope": RENDERER_SCOPE,
        "allowed_in_memory_inputs": ALLOWED_IN_MEMORY_INPUTS,
        "allowed_in_memory_outputs": ALLOWED_IN_MEMORY_OUTPUTS,
        "renderer_function_contract": RENDERER_FUNCTION_CONTRACT,
        "markdown_render_contract": MARKDOWN_RENDER_CONTRACT,
        "report_section_render_contract": REPORT_SECTION_RENDER_CONTRACT,
        "safety_attestation_render_contract": (
            SAFETY_ATTESTATION_RENDER_CONTRACT
        ),
        "placeholder_only_guard": _PLACEHOLDER_ONLY_GUARD,
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
        "fake_walk_report_operator_review_gate": (
            report_review_gate
            if isinstance(report_review_gate, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_report_renderer_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake report renderer
    contract template. Pure; writes no file. Informational only."""
    scope = contract.get("renderer_scope") or ()
    inputs = contract.get("allowed_in_memory_inputs") or ()
    outputs = contract.get("allowed_in_memory_outputs") or ()
    fn_contract = contract.get("renderer_function_contract") or ()
    md_contract = contract.get("markdown_render_contract") or ()
    section_contract = contract.get("report_section_render_contract") or ()
    attestation_contract = (
        contract.get("safety_attestation_render_contract") or ()
    )
    prohibited_artifacts = (
        contract.get("prohibited_real_artifact_references") or ()
    )
    prohibited_effects = contract.get("prohibited_runtime_side_effects") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Report Renderer Contract")
    lines.append("")
    lines.append(
        "Template only: this is a fake-report-renderer-contract-only, "
        "not-implemented-yet, planning-only, placeholder-only template -- "
        "no-report-file-write, no-runtime-state-write, research-only, and "
        "execution-free. It defines the shape of a future in-memory fake "
        "report renderer only, is not wired into any runtime state, writes no "
        "report file, accesses no data, names only fake placeholders, and "
        "grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Gate schema: "
        f"`{contract.get('fake_walk_report_operator_review_gate_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_RENDERER_CONTRACT_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake report renderer contract active: "
        f"{contract.get('fake_report_renderer_contract_active', '')}"
    )
    lines.append(
        "Renderer state: "
        f"{contract.get('fake_report_renderer_contract_state', '')}"
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
        "Source fake report review gate reference: "
        f"{contract.get('source_fake_report_review_gate_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Renderer Scope")
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
    lines.append("## Renderer Function Contract")
    lines.append("")
    for x in fn_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Markdown Render Contract")
    lines.append("")
    for x in md_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Report Section Render Contract")
    lines.append("")
    for x in section_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Safety Attestation Render Contract")
    lines.append("")
    for x in attestation_contract:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Placeholder Only Guard")
    lines.append("")
    lines.append(
        f"Placeholder only guard: {contract.get('placeholder_only_guard', '')}"
    )
    lines.append("")
    lines.append("## Prohibited Real Artifact References")
    lines.append("")
    for x in prohibited_artifacts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Prohibited Runtime Side Effects")
    lines.append("")
    for x in prohibited_effects:
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
        "- A human must approve the renderer build before any implementation "
        "is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
