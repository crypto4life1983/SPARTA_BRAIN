"""SPARTA Offline Strategy Factory - FAKE LANE CLOSURE CONTRACT.

Bundle 40 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only final closure contract template* builder: it consumes a
Bundle 39 fake report renderer result review contract and, only when that
review contract is active with result_review_decision ==
READY_FOR_FAKE_LANE_CLOSURE_CONTRACT and next_gate ==
FAKE_LANE_CLOSURE_CONTRACT_REQUIRED, produces a deterministic, read-only
contract describing the FINAL closure of the fake-only Strategy Factory lane
after the fake smoke test, fake dry walk, fake dry-walk review/implementation,
fake walk report, in-memory fake report rendering, and fake report result
review have all passed on paper. It defines a closure contract template only --
it closes nothing in runtime, writes no report file, is NOT a written report,
NOT a live system, NOT a dry walk, NOT a pipeline, NOT an orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never renders a report, never writes a
report file, never writes runtime state, never persists an approval, never
writes a ledger file, never updates dashboard files, never writes a registry
file, never performs research, never runs QA, never runs a baseline, never
backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, reads no file, lists no
directory, touches no broker/exchange/order/trading/live/distribution/autopilot
surface, promotes/deploys nothing, and records no approval decision. It records
no timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Reaching active closure unlocks NOTHING real: it only recommends a human
operator review before any real strategy intake. Every segment and artifact it
names is a FAKE placeholder. It references no real dataset, no real report
file, and no real market-data path.

Public API:
  - CLOSURE_SCHEMA_VERSION
  - DEFAULT_CLOSURE_LABEL
  - CLOSURE_STATUS
  - CLOSURE_SAFETY_POSTURE
  - CLOSURE_STATE_ACTIVE
  - CLOSURE_STATE_BLOCKED
  - CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR
  - CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX
  - CLOSURE_DECISION_PARK_FAKE_LANE
  - CLOSURE_DECISION_REJECT_FAKE_LANE
  - ALLOWED_CLOSURE_DECISIONS
  - NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE
  - NEXT_GATE_FAKE_LANE_FIX_REQUIRED
  - NEXT_GATE_FAKE_LANE_PARKED
  - NEXT_GATE_FAKE_LANE_REJECTED
  - NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION
  - NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW
  - RECOMMENDED_NEXT_PHASE
  - COMPLETED_FAKE_LANE_SEGMENTS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - build_fake_lane_closure_contract(review_contract, closure_decision=None)
  - validate_fake_lane_closure_contract(contract)
  - render_fake_lane_closure_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_report_renderer_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_SCHEMA_VERSION,
    RESULT_REVIEW_SAFETY_POSTURE,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
    NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED,
)

__all__ = [
    "CLOSURE_SCHEMA_VERSION",
    "DEFAULT_CLOSURE_LABEL",
    "CLOSURE_STATUS",
    "CLOSURE_SAFETY_POSTURE",
    "CLOSURE_STATE_ACTIVE",
    "CLOSURE_STATE_BLOCKED",
    "CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR",
    "CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX",
    "CLOSURE_DECISION_PARK_FAKE_LANE",
    "CLOSURE_DECISION_REJECT_FAKE_LANE",
    "ALLOWED_CLOSURE_DECISIONS",
    "NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
    "NEXT_GATE_FAKE_LANE_FIX_REQUIRED",
    "NEXT_GATE_FAKE_LANE_PARKED",
    "NEXT_GATE_FAKE_LANE_REJECTED",
    "NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION",
    "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW",
    "RECOMMENDED_NEXT_PHASE",
    "COMPLETED_FAKE_LANE_SEGMENTS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "build_fake_lane_closure_contract",
    "validate_fake_lane_closure_contract",
    "render_fake_lane_closure_contract_markdown",
]

CLOSURE_SCHEMA_VERSION = "strategy_factory_fake_lane_closure_contract.v1"
DEFAULT_CLOSURE_LABEL = "Strategy Factory Fake Lane Closure Contract"
CLOSURE_STATUS = "READ_ONLY_FAKE_LANE_CLOSURE_CONTRACT"

CLOSURE_STATE_ACTIVE = "FAKE_LANE_CLOSURE_CONTRACT_ACTIVE"
CLOSURE_STATE_BLOCKED = "FAKE_LANE_CLOSURE_CONTRACT_BLOCKED"

CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR = (
    "FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR"
)
CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX = "NEEDS_FAKE_LANE_FIX"
CLOSURE_DECISION_PARK_FAKE_LANE = "PARK_FAKE_LANE"
CLOSURE_DECISION_REJECT_FAKE_LANE = "REJECT_FAKE_LANE"

ALLOWED_CLOSURE_DECISIONS: tuple[str, ...] = (
    CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX,
    CLOSURE_DECISION_PARK_FAKE_LANE,
    CLOSURE_DECISION_REJECT_FAKE_LANE,
)

NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE = (
    "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
)
NEXT_GATE_FAKE_LANE_FIX_REQUIRED = "FAKE_LANE_FIX_REQUIRED"
NEXT_GATE_FAKE_LANE_PARKED = "FAKE_LANE_PARKED"
NEXT_GATE_FAKE_LANE_REJECTED = "FAKE_LANE_REJECTED"
NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION = "AWAIT_FAKE_LANE_CLOSURE_DECISION"
NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW = (
    "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"
)

# Default recommended next phase when the fake lane is closed on paper. It is a
# recommendation for a human operator review only -- it unlocks nothing real.
RECOMMENDED_NEXT_PHASE = (
    "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE"
)
_RECOMMENDED_NEXT_PHASE_BLOCKED = (
    "OPERATOR_REVIEW_REQUIRED_FAKE_LANE_NOT_COMPLETE_PLACEHOLDER"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-39).
CLOSURE_SAFETY_POSTURE: dict[str, bool] = dict(RESULT_REVIEW_SAFETY_POSTURE)

# The fake-only lane segments that must all be complete before closure. Each is
# a fake placeholder segment name, never a real artifact.
COMPLETED_FAKE_LANE_SEGMENTS: tuple[str, ...] = (
    "fake_artifact_smoke_test_contract",
    "fake_artifact_dry_walk_contract",
    "fake_dry_walk_operator_review_gate",
    "fake_dry_walk_implementation_contract",
    "fake_dry_walk_in_memory_implementation",
    "fake_dry_walk_result_review_contract",
    "fake_walk_report_contract",
    "fake_walk_report_operator_review_gate",
    "fake_report_renderer_contract",
    "fake_report_renderer_in_memory_implementation",
    "fake_report_renderer_result_review_contract",
)

# Real-world capabilities that remain blocked even after a clean fake-lane
# closure. Closing the fake lane unlocks NONE of these.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_strategy_intake",
    "real_data_load",
    "real_data_validation",
    "real_data_transform",
    "real_data_inspection",
    "real_data_compute",
    "real_market_data_inspection",
    "real_qa_run",
    "real_baseline_run",
    "real_backtest",
    "real_simulation",
    "real_pipeline_execution",
    "real_orchestrator_execution",
    "real_research_run",
    "real_data_fetch",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "autopilot",
    "automation",
    "upload",
    "deploy",
    "promotion",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake lane closure contract template and is execution-free.",
    "It closes the fake-only Strategy Factory lane on paper only and writes "
    "no report file.",
    "It writes no runtime state and is closure-contract-only.",
    "Every segment it names is a fake placeholder, never a real artifact.",
    "It accesses no data and names only fake placeholders.",
    "Closing the fake lane unlocks no real capability and no real strategy "
    "intake.",
    "A human operator must review the fake lane closure before any real "
    "strategy intake is planned.",
    "No automated step may proceed without human sign-off.",
)

# Human-operator next steps after a clean fake-lane closure. Prose only,
# verb-safe, advisory.
_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must review the completed fake lane segments before any "
    "real strategy intake is planned.",
    "A human operator must confirm no real data, broker, or live capability "
    "was touched.",
    "A human operator must decide whether to pause the fake lane for operator "
    "review before any real phase.",
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
    "real_strategy_intake",
    "runtime_state_write",
)

# Fake-lane-specific blocked capabilities (closure phase only).
_FAKE_LANE_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "fake_lane_closure_execution",
    "real_strategy_intake",
    "real_pipeline_execution",
    "real_orchestrator_execution",
    "report_file_write",
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

_SOURCE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Report Renderer Result Review reference is a fake "
    "placeholder for a final human-reviewed fake lane closure contract."
)

_FAKE_LANE_COMPLETION_SUMMARY: dict[str, str] = {
    "fake_lane_status_placeholder": "all_fake_segments_complete_placeholder",
    "fake_only_confirmation_placeholder": "fake_only_confirmed_placeholder",
    "no_real_artifact_confirmation_placeholder": (
        "no_real_artifact_confirmed_placeholder"
    ),
    "no_real_strategy_intake_confirmation_placeholder": (
        "no_real_strategy_intake_placeholder"
    ),
}

_FAKE_LANE_SAFETY_ATTESTATION: dict[str, str] = {
    "read_only_attestation_placeholder": "read_only_confirmed_placeholder",
    "execution_free_attestation_placeholder": (
        "execution_free_confirmed_placeholder"
    ),
    "no_real_data_attestation_placeholder": (
        "no_real_data_confirmed_placeholder"
    ),
    "no_runtime_state_write_attestation_placeholder": (
        "no_runtime_state_write_confirmed_placeholder"
    ),
    "no_report_file_write_attestation_placeholder": (
        "no_report_file_write_confirmed_placeholder"
    ),
    "no_broker_attestation_placeholder": "no_broker_confirmed_placeholder",
}

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_report_renderer_result_review_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_lane_closure_contract_active",
    "fake_lane_closure_contract_state",
    "fake_report_renderer_result_review_contract_active",
    "fake_report_renderer_result_review_decision",
    "fake_report_renderer_result_review_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_report_renderer_result_review_reference_placeholder",
    "closure_decision",
    "closure_decision_values",
    "completed_fake_lane_segments",
    "fake_lane_completion_summary",
    "fake_lane_safety_attestation",
    "fake_lane_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "recommended_next_phase",
    "human_operator_required_next_steps",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_report_renderer_result_review_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(CLOSURE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_CLOSURE_DECISIONS else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == CLOSURE_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_LANE_CLOSURE_ONLY")
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
        tuple(safe.get("closure_decision_values") or ())
        == ALLOWED_CLOSURE_DECISIONS
    )
    segments_ok = (
        tuple(safe.get("completed_fake_lane_segments") or ())
        == COMPLETED_FAKE_LANE_SEGMENTS
    )
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    completion_summary_ok = isinstance(
        safe.get("fake_lane_completion_summary"), dict
    ) and bool(safe.get("fake_lane_completion_summary"))
    safety_attestation_ok = isinstance(
        safe.get("fake_lane_safety_attestation"), dict
    ) and bool(safe.get("fake_lane_safety_attestation"))
    fake_lane_blocked_ok = (
        len(tuple(safe.get("fake_lane_blocked_capabilities") or ())) >= 1
    )
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    fields_ok = (
        decisions_ok
        and segments_ok
        and remaining_blocked_ok
        and completion_summary_ok
        and safety_attestation_ok
        and fake_lane_blocked_ok
        and next_steps_ok
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
        "closure_decision_values_ok": decisions_ok,
        "completed_fake_lane_segments_ok": segments_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "fake_lane_completion_summary_ok": completion_summary_ok,
        "fake_lane_safety_attestation_ok": safety_attestation_ok,
        "fake_lane_blocked_capabilities_present": fake_lane_blocked_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_fake_lane_closure_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake lane closure contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_lane_closure_contract(
    review_contract: Any,
    closure_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake lane closure contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (fake_lane_closure_contract_active=True) solely when the upstream Bundle 39
    fake report renderer result review contract is active AND its
    result_review_decision is READY_FOR_FAKE_LANE_CLOSURE_CONTRACT AND its
    next_gate is FAKE_LANE_CLOSURE_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it defines the SHAPE of a final
    fake-lane closure plus a human-operator review recommendation only, closes
    nothing real, writes no report file, writes no runtime state, accesses no
    data, names only fake placeholders, and grants nothing. Returned dicts are
    fresh."""
    review = review_contract if isinstance(review_contract, dict) else {}

    review_active = (
        review.get("fake_report_renderer_result_review_contract_active")
        is True
    )
    review_decision = _field(review, "result_review_decision")
    review_next_gate = _field(review, "next_gate")
    decision_ok = (
        review_decision
        == RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
    )
    gate_ok = (
        review_next_gate == NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED
    )

    contract_active = bool(review_active and decision_ok and gate_ok)

    decision = _normalize_decision(closure_decision)

    state = (
        CLOSURE_STATE_ACTIVE if contract_active else CLOSURE_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW
    elif decision == (
        CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR
    ):
        next_gate = (
            NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE
        )
    elif decision == CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX:
        next_gate = NEXT_GATE_FAKE_LANE_FIX_REQUIRED
    elif decision == CLOSURE_DECISION_PARK_FAKE_LANE:
        next_gate = NEXT_GATE_FAKE_LANE_PARKED
    elif decision == CLOSURE_DECISION_REJECT_FAKE_LANE:
        next_gate = NEXT_GATE_FAKE_LANE_REJECTED
    else:
        next_gate = NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION

    recommended_next_phase = (
        RECOMMENDED_NEXT_PHASE
        if contract_active
        else _RECOMMENDED_NEXT_PHASE_BLOCKED
    )

    contract = {
        "schema_version": CLOSURE_SCHEMA_VERSION,
        "fake_report_renderer_result_review_schema_version": (
            RESULT_REVIEW_SCHEMA_VERSION
        ),
        "idea_id": _field(review_contract, "idea_id"),
        "title": _field(review_contract, "title"),
        "label": DEFAULT_CLOSURE_LABEL,
        "status": CLOSURE_STATUS,
        "stage": "FAKE_LANE_CLOSURE_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_lane_closure_contract_active": contract_active,
        "fake_lane_closure_contract_state": state,
        "fake_report_renderer_result_review_contract_active": bool(
            review_active
        ),
        "fake_report_renderer_result_review_decision": review_decision,
        "fake_report_renderer_result_review_next_gate": review_next_gate,
        "asset_lane": _field(review_contract, "asset_lane"),
        "timeframe_lane": _field(review_contract, "timeframe_lane"),
        "source_fake_report_renderer_result_review_reference_placeholder": (
            _SOURCE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REFERENCE_PLACEHOLDER
        ),
        "closure_decision": decision,
        "closure_decision_values": ALLOWED_CLOSURE_DECISIONS,
        "completed_fake_lane_segments": COMPLETED_FAKE_LANE_SEGMENTS,
        "fake_lane_completion_summary": dict(_FAKE_LANE_COMPLETION_SUMMARY),
        "fake_lane_safety_attestation": dict(_FAKE_LANE_SAFETY_ATTESTATION),
        "fake_lane_blocked_capabilities": _FAKE_LANE_BLOCKED_CAPABILITIES,
        "remaining_real_world_capabilities_blocked": (
            REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "recommended_next_phase": recommended_next_phase,
        "human_operator_required_next_steps": (
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
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
        "fake_report_renderer_result_review_contract": (
            review_contract if isinstance(review_contract, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_lane_closure_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake lane closure
    contract template. Pure; writes no file. Informational only."""
    decisions = contract.get("closure_decision_values") or ()
    segments = contract.get("completed_fake_lane_segments") or ()
    completion = contract.get("fake_lane_completion_summary") or {}
    attestation = contract.get("fake_lane_safety_attestation") or {}
    fake_lane_blocked = contract.get("fake_lane_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Lane Closure Contract")
    lines.append("")
    lines.append(
        "Template only: this is a fake-lane-closure-contract-only, "
        "no-real-strategy-intake-yet, placeholder-only template -- "
        "no-report-file-write, no-runtime-state-write, research-only, and "
        "execution-free. It closes only the fake-only Strategy Factory lane on "
        "paper, is not wired into any runtime state, writes no report file, "
        "accesses no data, names only fake placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Review schema: "
        f"`{contract.get('fake_report_renderer_result_review_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_LANE_CLOSURE_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake lane closure contract active: "
        f"{contract.get('fake_lane_closure_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('fake_lane_closure_contract_state', '')}"
    )
    lines.append(
        "Closure decision: "
        f"{contract.get('closure_decision', '')}"
    )
    lines.append(
        "Recommended next phase: "
        f"{contract.get('recommended_next_phase', '')}"
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
        "Source fake report renderer result review reference: "
        f"{contract.get('source_fake_report_renderer_result_review_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Completed Fake Lane Segments")
    lines.append("")
    for x in segments:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Closure Decision Values")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Lane Completion Summary")
    lines.append("")
    for key, value in completion.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Fake Lane Safety Attestation")
    lines.append("")
    for key, value in attestation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Fake Lane Blocked Capabilities")
    lines.append("")
    for cap in fake_lane_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Remaining Real-World Capabilities Blocked")
    lines.append("")
    for cap in remaining_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in contract.get("blocked_capabilities") or ():
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Human Operator Required Next Steps")
    lines.append("")
    for step in next_steps:
        lines.append(f"- {step}")
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
        "- A human operator must approve the fake lane closure before any "
        "real strategy intake is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
