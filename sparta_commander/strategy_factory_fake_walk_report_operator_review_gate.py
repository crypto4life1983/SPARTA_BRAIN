"""SPARTA Offline Strategy Factory - FAKE WALK REPORT OPERATOR REVIEW GATE.

Bundle 36 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only operator review gate template* builder: it consumes a
Bundle 35 fake walk report contract and, only when that report contract is
active with next_gate == FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED, produces a
deterministic, read-only contract describing how a human/operator must review
the fake walk report contract before any renderer phase is planned. It defines
a review gate template only -- it runs no review, writes no report, is NOT a
written report, NOT a live system, NOT a dry walk, NOT a pipeline, NOT an
orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never renders a report, never writes a
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
  - REPORT_REVIEW_GATE_SCHEMA_VERSION
  - DEFAULT_REPORT_REVIEW_GATE_LABEL
  - REPORT_REVIEW_GATE_STATUS
  - REPORT_REVIEW_GATE_SAFETY_POSTURE
  - GATE_STATE_ACTIVE
  - GATE_STATE_BLOCKED
  - OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX
  - OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
  - OPERATOR_DECISION_PARK
  - OPERATOR_DECISION_REJECT
  - ALLOWED_OPERATOR_DECISIONS
  - NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED
  - NEXT_GATE_FAKE_REPORT_FIX_REQUIRED
  - NEXT_GATE_FAKE_REPORT_PARKED
  - NEXT_GATE_FAKE_REPORT_REJECTED
  - NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION
  - NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT
  - REQUIRED_OPERATOR_REVIEW_FIELDS
  - REQUIRED_REPORT_REVIEW_FIELDS
  - REQUIRED_SAFETY_ATTESTATION_FIELDS
  - REJECTION_CONDITIONS
  - build_fake_walk_report_operator_review_gate(report_contract, operator_decision=None)
  - validate_fake_walk_report_operator_review_gate(contract)
  - render_fake_walk_report_operator_review_gate_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_walk_report_contract import (
    FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION,
    FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED,
)

__all__ = [
    "REPORT_REVIEW_GATE_SCHEMA_VERSION",
    "DEFAULT_REPORT_REVIEW_GATE_LABEL",
    "REPORT_REVIEW_GATE_STATUS",
    "REPORT_REVIEW_GATE_SAFETY_POSTURE",
    "GATE_STATE_ACTIVE",
    "GATE_STATE_BLOCKED",
    "OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX",
    "OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT",
    "OPERATOR_DECISION_PARK",
    "OPERATOR_DECISION_REJECT",
    "ALLOWED_OPERATOR_DECISIONS",
    "NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED",
    "NEXT_GATE_FAKE_REPORT_FIX_REQUIRED",
    "NEXT_GATE_FAKE_REPORT_PARKED",
    "NEXT_GATE_FAKE_REPORT_REJECTED",
    "NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION",
    "NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT",
    "REQUIRED_OPERATOR_REVIEW_FIELDS",
    "REQUIRED_REPORT_REVIEW_FIELDS",
    "REQUIRED_SAFETY_ATTESTATION_FIELDS",
    "REJECTION_CONDITIONS",
    "build_fake_walk_report_operator_review_gate",
    "validate_fake_walk_report_operator_review_gate",
    "render_fake_walk_report_operator_review_gate_markdown",
]

REPORT_REVIEW_GATE_SCHEMA_VERSION = (
    "strategy_factory_fake_walk_report_operator_review_gate.v1"
)
DEFAULT_REPORT_REVIEW_GATE_LABEL = (
    "Strategy Factory Fake Walk Report Operator Review Gate"
)
REPORT_REVIEW_GATE_STATUS = (
    "READ_ONLY_FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE"
)

GATE_STATE_ACTIVE = "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_ACTIVE"
GATE_STATE_BLOCKED = "FAKE_WALK_REPORT_OPERATOR_REVIEW_GATE_BLOCKED"

OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX = "NEEDS_FAKE_REPORT_FIX"
OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT = (
    "READY_FOR_FAKE_REPORT_RENDERER_CONTRACT"
)
OPERATOR_DECISION_PARK = "PARK"
OPERATOR_DECISION_REJECT = "REJECT"

ALLOWED_OPERATOR_DECISIONS: tuple[str, ...] = (
    OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX,
    OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT,
    OPERATOR_DECISION_PARK,
    OPERATOR_DECISION_REJECT,
)

NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED = (
    "FAKE_REPORT_RENDERER_CONTRACT_REQUIRED"
)
NEXT_GATE_FAKE_REPORT_FIX_REQUIRED = "FAKE_REPORT_FIX_REQUIRED"
NEXT_GATE_FAKE_REPORT_PARKED = "FAKE_REPORT_PARKED"
NEXT_GATE_FAKE_REPORT_REJECTED = "FAKE_REPORT_REJECTED"
NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION = (
    "AWAIT_FAKE_REPORT_OPERATOR_REVIEW_DECISION"
)
NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT = (
    "AWAIT_FAKE_WALK_REPORT_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-35).
REPORT_REVIEW_GATE_SAFETY_POSTURE: dict[str, bool] = dict(
    FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE
)

# Fake placeholder field names a reviewer must confirm.
REQUIRED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "report_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

REQUIRED_REPORT_REVIEW_FIELDS: tuple[str, ...] = (
    "report_title_review_placeholder",
    "report_sections_review_placeholder",
    "fake_walk_summary_review_placeholder",
    "pass_fail_summary_review_placeholder",
)

REQUIRED_SAFETY_ATTESTATION_FIELDS: tuple[str, ...] = (
    "read_only_attestation_placeholder",
    "execution_free_attestation_placeholder",
    "no_real_data_attestation_placeholder",
    "no_runtime_state_write_attestation_placeholder",
    "no_report_file_write_attestation_placeholder",
)

REJECTION_CONDITIONS: tuple[str, ...] = (
    "fake_report_contract_inactive_placeholder",
    "missing_required_report_section_placeholder",
    "real_artifact_reference_detected_placeholder",
    "missing_operator_sign_off_placeholder",
)

_APPROVAL_EXPIRY_PLACEHOLDER = (
    "Fake approval expiry is a placeholder only -- this gate grants nothing "
    "and no approval is ever persisted."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake walk report operator review gate template and is "
    "execution-free.",
    "It reviews a fake walk report contract only and writes no report file.",
    "It writes no runtime state and is review-only.",
    "Every field it names is a fake placeholder, never real output.",
    "It accesses no data and names only fake placeholders.",
    "A human must approve the fake walk report before any renderer phase is "
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

_SOURCE_FAKE_WALK_REPORT_CONTRACT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Walk Report contract reference is a fake "
    "placeholder for a later human-reviewed fake report renderer."
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_walk_report_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_walk_report_operator_review_gate_active",
    "fake_walk_report_operator_review_gate_state",
    "fake_walk_report_contract_active",
    "fake_walk_report_contract_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_walk_report_contract_reference_placeholder",
    "operator_decision",
    "allowed_operator_decisions",
    "required_operator_review_fields",
    "required_report_review_fields",
    "required_safety_attestation_fields",
    "approval_expiry_placeholder",
    "rejection_conditions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_walk_report_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(REPORT_REVIEW_GATE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(report: Any, key: str) -> str:
    """Read a string field from a possibly-malformed report; safe."""
    return _as_text(report.get(key)) if isinstance(report, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_OPERATOR_DECISIONS else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == REPORT_REVIEW_GATE_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_REPORT_REVIEW_ONLY")
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
        tuple(safe.get("allowed_operator_decisions") or ())
        == ALLOWED_OPERATOR_DECISIONS
    )
    operator_fields_ok = (
        tuple(safe.get("required_operator_review_fields") or ())
        == REQUIRED_OPERATOR_REVIEW_FIELDS
    )
    report_fields_ok = (
        tuple(safe.get("required_report_review_fields") or ())
        == REQUIRED_REPORT_REVIEW_FIELDS
    )
    attestation_fields_ok = (
        tuple(safe.get("required_safety_attestation_fields") or ())
        == REQUIRED_SAFETY_ATTESTATION_FIELDS
    )
    rejection_ok = len(tuple(safe.get("rejection_conditions") or ())) >= 1

    fields_ok = (
        decisions_ok
        and operator_fields_ok
        and report_fields_ok
        and attestation_fields_ok
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
        "required_operator_review_fields_ok": operator_fields_ok,
        "required_report_review_fields_ok": report_fields_ok,
        "required_safety_attestation_fields_ok": attestation_fields_ok,
        "rejection_conditions_present": rejection_ok,
        "missing_required_fields": missing,
    }


def validate_fake_walk_report_operator_review_gate(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake walk report operator review
    gate template. Pure; no I/O."""
    return _validate(contract)


def build_fake_walk_report_operator_review_gate(
    report_contract: Any,
    operator_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake walk report operator review
    gate template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The gate becomes active
    (fake_walk_report_operator_review_gate_active=True) solely when the upstream
    Bundle 35 fake walk report contract is active AND its next_gate is
    FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED. Even when active, every
    authorization field stays False -- it defines the SHAPE of a human review
    only, writes no report file, writes no runtime state, accesses no data,
    names only fake placeholders, and grants nothing. Returned dicts are
    fresh."""
    report_active = (
        isinstance(report_contract, dict)
        and report_contract.get("fake_walk_report_contract_active") is True
    )
    report_next_gate = _field(report_contract, "next_gate")
    next_gate_ok = (
        report_next_gate
        == NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED
    )
    gate_active = bool(report_active and next_gate_ok)

    decision = _normalize_decision(operator_decision)

    state = GATE_STATE_ACTIVE if gate_active else GATE_STATE_BLOCKED

    if not gate_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_WALK_REPORT_CONTRACT
    elif decision == (
        OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
    ):
        next_gate = NEXT_GATE_FAKE_REPORT_RENDERER_CONTRACT_REQUIRED
    elif decision == OPERATOR_DECISION_NEEDS_FAKE_REPORT_FIX:
        next_gate = NEXT_GATE_FAKE_REPORT_FIX_REQUIRED
    elif decision == OPERATOR_DECISION_PARK:
        next_gate = NEXT_GATE_FAKE_REPORT_PARKED
    elif decision == OPERATOR_DECISION_REJECT:
        next_gate = NEXT_GATE_FAKE_REPORT_REJECTED
    else:
        next_gate = NEXT_GATE_AWAIT_REPORT_OPERATOR_REVIEW_DECISION

    contract = {
        "schema_version": REPORT_REVIEW_GATE_SCHEMA_VERSION,
        "fake_walk_report_contract_schema_version": (
            FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _field(report_contract, "idea_id"),
        "title": _field(report_contract, "title"),
        "label": DEFAULT_REPORT_REVIEW_GATE_LABEL,
        "status": REPORT_REVIEW_GATE_STATUS,
        "stage": "FAKE_REPORT_REVIEW_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_walk_report_operator_review_gate_active": gate_active,
        "fake_walk_report_operator_review_gate_state": state,
        "fake_walk_report_contract_active": bool(report_active),
        "fake_walk_report_contract_next_gate": report_next_gate,
        "asset_lane": _field(report_contract, "asset_lane"),
        "timeframe_lane": _field(report_contract, "timeframe_lane"),
        "source_fake_walk_report_contract_reference_placeholder": (
            _SOURCE_FAKE_WALK_REPORT_CONTRACT_REFERENCE_PLACEHOLDER
        ),
        "operator_decision": decision,
        "allowed_operator_decisions": ALLOWED_OPERATOR_DECISIONS,
        "required_operator_review_fields": REQUIRED_OPERATOR_REVIEW_FIELDS,
        "required_report_review_fields": REQUIRED_REPORT_REVIEW_FIELDS,
        "required_safety_attestation_fields": (
            REQUIRED_SAFETY_ATTESTATION_FIELDS
        ),
        "approval_expiry_placeholder": _APPROVAL_EXPIRY_PLACEHOLDER,
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
        "fake_walk_report_contract": (
            report_contract if isinstance(report_contract, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_walk_report_operator_review_gate_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake walk report operator
    review gate template. Pure; writes no file. Informational only."""
    decisions = contract.get("allowed_operator_decisions") or ()
    operator_fields = contract.get("required_operator_review_fields") or ()
    report_fields = contract.get("required_report_review_fields") or ()
    attestation_fields = (
        contract.get("required_safety_attestation_fields") or ()
    )
    rejection = contract.get("rejection_conditions") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Fake Walk Report Operator Review Gate"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "fake-walk-report-operator-review-gate-only, review-only, "
        "placeholder-only template -- no-report-file-write, "
        "no-runtime-state-write, research-only, and execution-free. It reviews "
        "only a fake walk report contract, is not wired into any runtime "
        "state, writes no report file, accesses no data, names only fake "
        "placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Report schema: "
        f"`{contract.get('fake_walk_report_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_REPORT_REVIEW_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake walk report operator review gate active: "
        f"{contract.get('fake_walk_report_operator_review_gate_active', '')}"
    )
    lines.append(
        "Gate state: "
        f"{contract.get('fake_walk_report_operator_review_gate_state', '')}"
    )
    lines.append(
        "Operator decision: "
        f"{contract.get('operator_decision', '')}"
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
        "Source fake walk report contract reference: "
        f"{contract.get('source_fake_walk_report_contract_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Approval Expiry")
    lines.append("")
    lines.append(
        "Approval expiry: "
        f"{contract.get('approval_expiry_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Allowed Operator Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Review Fields")
    lines.append("")
    for x in operator_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Report Review Fields")
    lines.append("")
    for x in report_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Safety Attestation Fields")
    lines.append("")
    for x in attestation_fields:
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
        "- A human must approve the fake walk report before any renderer "
        "phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
