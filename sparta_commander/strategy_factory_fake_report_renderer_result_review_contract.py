"""SPARTA Offline Strategy Factory - FAKE REPORT RENDERER RESULT REVIEW.

Bundle 39 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only result review contract template* builder: it consumes a
Bundle 38 fake report renderer in-memory state and, only when that renderer
result is active with next_gate == FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED,
its rendered markdown preview / report sections / safety attestation /
placeholder-only guard all exist, and its real-artifact scan found nothing,
produces a deterministic, read-only contract describing how a human/operator
must review the in-memory fake rendered report result before any fake lane
closure phase is planned. It defines a review contract template only -- it runs
no review, writes no report, is NOT a written report, NOT a live system, NOT a
dry walk, NOT a pipeline, NOT an orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never renders a report beyond reviewing the
in-memory fake result object, never writes a report file, never writes runtime
state, never persists an approval, never writes a ledger file, never updates
dashboard files, never writes a registry file, never performs research, never
runs QA, never runs a baseline, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing. It opens no network, spawns no subprocess, writes no file,
reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Every artifact it names is a FAKE placeholder. It references no real dataset,
no real report file, and no real market-data path.

Public API:
  - RESULT_REVIEW_SCHEMA_VERSION
  - DEFAULT_RESULT_REVIEW_LABEL
  - RESULT_REVIEW_STATUS
  - RESULT_REVIEW_SAFETY_POSTURE
  - RESULT_REVIEW_STATE_ACTIVE
  - RESULT_REVIEW_STATE_BLOCKED
  - RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX
  - RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
  - RESULT_REVIEW_DECISION_PARK
  - RESULT_REVIEW_DECISION_REJECT
  - ALLOWED_RESULT_REVIEW_DECISIONS
  - NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED
  - NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED
  - NEXT_GATE_FAKE_REPORT_RENDERER_PARKED
  - NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED
  - NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION
  - NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT
  - REQUIRED_RENDERED_RESULT_FIELDS
  - REQUIRED_REPORT_SECTION_REVIEW_FIELDS
  - REQUIRED_SAFETY_REVIEW_FIELDS
  - REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS
  - REVIEW_PASS_CRITERIA
  - REVIEW_FAIL_CRITERIA
  - REJECTION_CONDITIONS
  - build_fake_report_renderer_result_review_contract(renderer_state, result_review_decision=None)
  - validate_fake_report_renderer_result_review_contract(contract)
  - render_fake_report_renderer_result_review_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_report_renderer_in_memory import (
    RENDERER_IN_MEMORY_SCHEMA_VERSION,
    RENDERER_IN_MEMORY_SAFETY_POSTURE,
    NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED,
)

__all__ = [
    "RESULT_REVIEW_SCHEMA_VERSION",
    "DEFAULT_RESULT_REVIEW_LABEL",
    "RESULT_REVIEW_STATUS",
    "RESULT_REVIEW_SAFETY_POSTURE",
    "RESULT_REVIEW_STATE_ACTIVE",
    "RESULT_REVIEW_STATE_BLOCKED",
    "RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX",
    "RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT",
    "RESULT_REVIEW_DECISION_PARK",
    "RESULT_REVIEW_DECISION_REJECT",
    "ALLOWED_RESULT_REVIEW_DECISIONS",
    "NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED",
    "NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED",
    "NEXT_GATE_FAKE_REPORT_RENDERER_PARKED",
    "NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED",
    "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION",
    "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT",
    "REQUIRED_RENDERED_RESULT_FIELDS",
    "REQUIRED_REPORT_SECTION_REVIEW_FIELDS",
    "REQUIRED_SAFETY_REVIEW_FIELDS",
    "REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS",
    "REVIEW_PASS_CRITERIA",
    "REVIEW_FAIL_CRITERIA",
    "REJECTION_CONDITIONS",
    "build_fake_report_renderer_result_review_contract",
    "validate_fake_report_renderer_result_review_contract",
    "render_fake_report_renderer_result_review_contract_markdown",
]

RESULT_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_fake_report_renderer_result_review_contract.v1"
)
DEFAULT_RESULT_REVIEW_LABEL = (
    "Strategy Factory Fake Report Renderer Result Review Contract"
)
RESULT_REVIEW_STATUS = (
    "READ_ONLY_FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT"
)

RESULT_REVIEW_STATE_ACTIVE = (
    "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_ACTIVE"
)
RESULT_REVIEW_STATE_BLOCKED = (
    "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_BLOCKED"
)

RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX = (
    "NEEDS_FAKE_REPORT_RENDER_FIX"
)
RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT = (
    "READY_FOR_FAKE_LANE_CLOSURE_CONTRACT"
)
RESULT_REVIEW_DECISION_PARK = "PARK"
RESULT_REVIEW_DECISION_REJECT = "REJECT"

ALLOWED_RESULT_REVIEW_DECISIONS: tuple[str, ...] = (
    RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
    RESULT_REVIEW_DECISION_PARK,
    RESULT_REVIEW_DECISION_REJECT,
)

NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED = (
    "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"
)
NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED = (
    "FAKE_REPORT_RENDER_FIX_REQUIRED"
)
NEXT_GATE_FAKE_REPORT_RENDERER_PARKED = "FAKE_REPORT_RENDERER_PARKED"
NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED = "FAKE_REPORT_RENDERER_REJECTED"
NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION = (
    "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION"
)
NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT = (
    "AWAIT_FAKE_REPORT_RENDERER_RESULT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-38).
RESULT_REVIEW_SAFETY_POSTURE: dict[str, bool] = dict(
    RENDERER_IN_MEMORY_SAFETY_POSTURE
)

# Fake placeholder field names a reviewer must confirm on the rendered result.
REQUIRED_RENDERED_RESULT_FIELDS: tuple[str, ...] = (
    "rendered_markdown_preview_review_placeholder",
    "report_sections_present_review_placeholder",
    "placeholder_only_confirmed_review_placeholder",
    "no_real_artifact_confirmed_review_placeholder",
)

REQUIRED_REPORT_SECTION_REVIEW_FIELDS: tuple[str, ...] = (
    "executive_summary_review_placeholder",
    "pass_fail_summary_review_placeholder",
    "safety_attestation_review_placeholder",
    "next_steps_review_placeholder",
)

REQUIRED_SAFETY_REVIEW_FIELDS: tuple[str, ...] = (
    "read_only_attestation_review_placeholder",
    "execution_free_attestation_review_placeholder",
    "no_real_data_attestation_review_placeholder",
    "no_runtime_state_write_attestation_review_placeholder",
    "no_report_file_write_attestation_review_placeholder",
)

REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS: tuple[str, ...] = (
    "placeholder_only_guard_present_review_placeholder",
    "real_artifact_hits_empty_review_placeholder",
)

REVIEW_PASS_CRITERIA: tuple[str, ...] = (
    "renderer_result_active_placeholder",
    "all_required_report_sections_present_placeholder",
    "placeholder_only_guard_present_placeholder",
    "real_artifact_hits_empty_placeholder",
    "human_sign_off_present_placeholder",
)

REVIEW_FAIL_CRITERIA: tuple[str, ...] = (
    "renderer_result_inactive_placeholder",
    "missing_required_report_section_placeholder",
    "missing_placeholder_only_guard_placeholder",
    "real_artifact_reference_present_placeholder",
    "missing_human_sign_off_placeholder",
)

REJECTION_CONDITIONS: tuple[str, ...] = (
    "renderer_result_inactive_placeholder",
    "real_artifact_reference_detected_placeholder",
    "missing_required_rendered_result_field_placeholder",
    "missing_operator_sign_off_placeholder",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake report renderer result review contract template and is "
    "execution-free.",
    "It reviews a fake in-memory rendered report result only and writes no "
    "report file.",
    "It writes no runtime state and is review-only.",
    "Every field it names is a fake placeholder, never real output.",
    "It accesses no data and names only fake placeholders.",
    "A human must approve the fake rendered report result before the fake "
    "lane closure phase is planned.",
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
    "report_renderer_result_review_execution",
    "fake_lane_closure_execution",
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

_SOURCE_FAKE_REPORT_RENDERER_RESULT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Report Renderer in-memory result reference is a "
    "fake placeholder for a later human-reviewed fake lane closure contract."
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_report_renderer_in_memory_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_report_renderer_result_review_contract_active",
    "fake_report_renderer_result_review_contract_state",
    "fake_report_renderer_active",
    "fake_report_renderer_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_report_renderer_result_reference_placeholder",
    "result_review_decision",
    "allowed_result_review_decisions",
    "required_rendered_result_fields",
    "required_report_section_review_fields",
    "required_safety_review_fields",
    "required_placeholder_guard_review_fields",
    "review_pass_criteria",
    "review_fail_criteria",
    "rejection_conditions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_report_renderer_in_memory",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESULT_REVIEW_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_RESULT_REVIEW_DECISIONS else ""


def _real_artifact_hits(renderer_state: Any) -> tuple[str, ...]:
    """Return the renderer state's real-artifact hits as a tuple (safe)."""
    if not isinstance(renderer_state, dict):
        return ()
    validation = renderer_state.get("validation")
    hits = validation.get("real_artifact_hits") if isinstance(
        validation, dict) else None
    if isinstance(hits, (tuple, list)):
        return tuple(str(h) for h in hits)
    return ()


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == RESULT_REVIEW_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "FAKE_RENDER_RESULT_REVIEW_ONLY",
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    decisions_ok = (
        tuple(safe.get("allowed_result_review_decisions") or ())
        == ALLOWED_RESULT_REVIEW_DECISIONS
    )
    rendered_fields_ok = (
        tuple(safe.get("required_rendered_result_fields") or ())
        == REQUIRED_RENDERED_RESULT_FIELDS
    )
    section_fields_ok = (
        tuple(safe.get("required_report_section_review_fields") or ())
        == REQUIRED_REPORT_SECTION_REVIEW_FIELDS
    )
    safety_fields_ok = (
        tuple(safe.get("required_safety_review_fields") or ())
        == REQUIRED_SAFETY_REVIEW_FIELDS
    )
    guard_fields_ok = (
        tuple(safe.get("required_placeholder_guard_review_fields") or ())
        == REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS
    )
    pass_criteria_ok = len(tuple(safe.get("review_pass_criteria") or ())) >= 1
    fail_criteria_ok = len(tuple(safe.get("review_fail_criteria") or ())) >= 1
    rejection_ok = len(tuple(safe.get("rejection_conditions") or ())) >= 1

    fields_ok = (
        decisions_ok
        and rendered_fields_ok
        and section_fields_ok
        and safety_fields_ok
        and guard_fields_ok
        and pass_criteria_ok
        and fail_criteria_ok
        and rejection_ok
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
        "allowed_decisions_ok": decisions_ok,
        "required_rendered_result_fields_ok": rendered_fields_ok,
        "required_report_section_review_fields_ok": section_fields_ok,
        "required_safety_review_fields_ok": safety_fields_ok,
        "required_placeholder_guard_review_fields_ok": guard_fields_ok,
        "review_pass_criteria_present": pass_criteria_ok,
        "review_fail_criteria_present": fail_criteria_ok,
        "rejection_conditions_present": rejection_ok,
        "missing_required_fields": missing,
    }


def validate_fake_report_renderer_result_review_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake report renderer result review
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_fake_report_renderer_result_review_contract(
    renderer_state: Any,
    result_review_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake report renderer result review
    contract template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (fake_report_renderer_result_review_contract_active=True) solely when the
    upstream Bundle 38 fake report renderer in-memory state is active AND its
    next_gate is FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED AND its rendered
    markdown preview, report sections, fake safety attestation, and
    placeholder-only guard all exist AND its real-artifact scan found nothing.
    Even when active, every authorization field stays False -- it defines the
    SHAPE of a human review only, writes no report file, writes no runtime
    state, accesses no data, names only fake placeholders, and grants nothing.
    Returned dicts are fresh."""
    renderer = renderer_state if isinstance(renderer_state, dict) else {}

    renderer_active = renderer.get("fake_report_renderer_active") is True
    renderer_next_gate = _field(renderer_state, "next_gate")
    next_gate_ok = (
        renderer_next_gate
        == NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED
    )
    preview = renderer.get("rendered_markdown_preview")
    has_preview = isinstance(preview, str) and bool(preview)
    sections = renderer.get("report_sections")
    has_sections = isinstance(sections, dict) and bool(sections)
    attestation = renderer.get("fake_safety_attestation")
    has_attestation = isinstance(attestation, dict) and bool(attestation)
    guard = renderer.get("placeholder_only_guard")
    has_guard = isinstance(guard, str) and bool(guard)
    real_hits = _real_artifact_hits(renderer)
    no_real_hits = real_hits == ()

    contract_active = bool(
        renderer_active
        and next_gate_ok
        and has_preview
        and has_sections
        and has_attestation
        and has_guard
        and no_real_hits
    )

    decision = _normalize_decision(result_review_decision)

    state = (
        RESULT_REVIEW_STATE_ACTIVE
        if contract_active
        else RESULT_REVIEW_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT
    elif decision == (
        RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
    ):
        next_gate = NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED
    elif decision == RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX:
        next_gate = NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED
    elif decision == RESULT_REVIEW_DECISION_PARK:
        next_gate = NEXT_GATE_FAKE_REPORT_RENDERER_PARKED
    elif decision == RESULT_REVIEW_DECISION_REJECT:
        next_gate = NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED
    else:
        next_gate = (
            NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION
        )

    contract = {
        "schema_version": RESULT_REVIEW_SCHEMA_VERSION,
        "fake_report_renderer_in_memory_schema_version": (
            RENDERER_IN_MEMORY_SCHEMA_VERSION
        ),
        "idea_id": _field(renderer_state, "idea_id"),
        "title": _field(renderer_state, "title"),
        "label": DEFAULT_RESULT_REVIEW_LABEL,
        "status": RESULT_REVIEW_STATUS,
        "stage": "FAKE_RENDER_RESULT_REVIEW_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_report_renderer_result_review_contract_active": contract_active,
        "fake_report_renderer_result_review_contract_state": state,
        "fake_report_renderer_active": bool(renderer_active),
        "fake_report_renderer_next_gate": renderer_next_gate,
        "asset_lane": _field(renderer_state, "asset_lane"),
        "timeframe_lane": _field(renderer_state, "timeframe_lane"),
        "source_fake_report_renderer_result_reference_placeholder": (
            _SOURCE_FAKE_REPORT_RENDERER_RESULT_REFERENCE_PLACEHOLDER
        ),
        "result_review_decision": decision,
        "allowed_result_review_decisions": ALLOWED_RESULT_REVIEW_DECISIONS,
        "required_rendered_result_fields": REQUIRED_RENDERED_RESULT_FIELDS,
        "required_report_section_review_fields": (
            REQUIRED_REPORT_SECTION_REVIEW_FIELDS
        ),
        "required_safety_review_fields": REQUIRED_SAFETY_REVIEW_FIELDS,
        "required_placeholder_guard_review_fields": (
            REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS
        ),
        "review_pass_criteria": REVIEW_PASS_CRITERIA,
        "review_fail_criteria": REVIEW_FAIL_CRITERIA,
        "rejection_conditions": REJECTION_CONDITIONS,
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
        "fake_report_renderer_in_memory": (
            renderer_state if isinstance(renderer_state, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_report_renderer_result_review_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake report renderer
    result review contract template. Pure; writes no file. Informational
    only."""
    decisions = contract.get("allowed_result_review_decisions") or ()
    rendered_fields = contract.get("required_rendered_result_fields") or ()
    section_fields = (
        contract.get("required_report_section_review_fields") or ()
    )
    safety_fields = contract.get("required_safety_review_fields") or ()
    guard_fields = (
        contract.get("required_placeholder_guard_review_fields") or ()
    )
    pass_criteria = contract.get("review_pass_criteria") or ()
    fail_criteria = contract.get("review_fail_criteria") or ()
    rejection = contract.get("rejection_conditions") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Fake Report Renderer Result Review Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "fake-report-renderer-result-review-contract-only, review-only, "
        "placeholder-only template -- no-report-file-write, "
        "no-runtime-state-write, research-only, and execution-free. It reviews "
        "only a fake in-memory rendered report result, is not wired into any "
        "runtime state, writes no report file, accesses no data, names only "
        "fake placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Renderer schema: "
        f"`{contract.get('fake_report_renderer_in_memory_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_RENDER_RESULT_REVIEW_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake report renderer result review contract active: "
        f"{contract.get('fake_report_renderer_result_review_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('fake_report_renderer_result_review_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Result review decision: "
        f"{contract.get('result_review_decision', '')}"
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
        "Source fake report renderer result reference: "
        f"{contract.get('source_fake_report_renderer_result_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Allowed Result Review Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Rendered Result Fields")
    lines.append("")
    for x in rendered_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Report Section Review Fields")
    lines.append("")
    for x in section_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Safety Review Fields")
    lines.append("")
    for x in safety_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Placeholder Guard Review Fields")
    lines.append("")
    for x in guard_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Review Pass Criteria")
    lines.append("")
    for x in pass_criteria:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Review Fail Criteria")
    lines.append("")
    for x in fail_criteria:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Rejection Conditions")
    lines.append("")
    for x in rejection:
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
        "- A human must approve the fake rendered report result before the "
        "fake lane closure phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
