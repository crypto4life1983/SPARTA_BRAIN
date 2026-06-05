"""SPARTA Offline Strategy Factory - FAKE DRY-WALK RESULT REVIEW CONTRACT.

Bundle 34 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only review contract template* builder: it consumes a Bundle
33 fake dry-walk in-memory result and, only when that result is active with
next_gate == FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED and the required fake outputs
(pass/fail summary, stage records, trace records, operator review packet) are
present, produces a deterministic, read-only contract describing how a
human/operator must review the fake dry-walk result before any later phase is
planned. It defines a review template only -- it runs no review, is NOT a live
system, NOT a dry walk, NOT a pipeline, NOT an orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never runs an orchestrator, never writes
runtime state, never persists an approval, never writes a ledger file, never
updates dashboard files, never writes a registry file, never performs research,
never runs QA, never runs a baseline, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing. It opens no network, spawns no subprocess, writes no file,
reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RESULT_REVIEW_CONTRACT_LABEL
  - RESULT_REVIEW_CONTRACT_STATUS
  - RESULT_REVIEW_CONTRACT_SAFETY_POSTURE
  - REVIEW_STATE_ACTIVE
  - REVIEW_STATE_BLOCKED
  - RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX
  - RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
  - RESULT_REVIEW_DECISION_PARK
  - RESULT_REVIEW_DECISION_REJECT
  - ALLOWED_RESULT_REVIEW_DECISIONS
  - NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED
  - NEXT_GATE_FAKE_WALK_FIX_REQUIRED
  - NEXT_GATE_FAKE_WALK_PARKED
  - NEXT_GATE_FAKE_WALK_REJECTED
  - NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION
  - NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT
  - REQUIRED_RESULT_FIELDS
  - REQUIRED_STAGE_REVIEW_FIELDS
  - REQUIRED_TRACE_REVIEW_FIELDS
  - REQUIRED_OPERATOR_REVIEW_FIELDS
  - REVIEW_PASS_CRITERIA
  - REVIEW_FAIL_CRITERIA
  - REJECTION_CONDITIONS
  - build_fake_dry_walk_result_review_contract(fake_dry_walk, result_review_decision=None)
  - validate_fake_dry_walk_result_review_contract(contract)
  - render_fake_dry_walk_result_review_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    DRY_WALK_IN_MEMORY_SCHEMA_VERSION,
    DRY_WALK_IN_MEMORY_SAFETY_POSTURE,
    NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED,
)

__all__ = [
    "RESULT_REVIEW_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RESULT_REVIEW_CONTRACT_LABEL",
    "RESULT_REVIEW_CONTRACT_STATUS",
    "RESULT_REVIEW_CONTRACT_SAFETY_POSTURE",
    "REVIEW_STATE_ACTIVE",
    "REVIEW_STATE_BLOCKED",
    "RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX",
    "RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT",
    "RESULT_REVIEW_DECISION_PARK",
    "RESULT_REVIEW_DECISION_REJECT",
    "ALLOWED_RESULT_REVIEW_DECISIONS",
    "NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED",
    "NEXT_GATE_FAKE_WALK_FIX_REQUIRED",
    "NEXT_GATE_FAKE_WALK_PARKED",
    "NEXT_GATE_FAKE_WALK_REJECTED",
    "NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION",
    "NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT",
    "REQUIRED_RESULT_FIELDS",
    "REQUIRED_STAGE_REVIEW_FIELDS",
    "REQUIRED_TRACE_REVIEW_FIELDS",
    "REQUIRED_OPERATOR_REVIEW_FIELDS",
    "REVIEW_PASS_CRITERIA",
    "REVIEW_FAIL_CRITERIA",
    "REJECTION_CONDITIONS",
    "build_fake_dry_walk_result_review_contract",
    "validate_fake_dry_walk_result_review_contract",
    "render_fake_dry_walk_result_review_contract_markdown",
]

RESULT_REVIEW_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_dry_walk_result_review_contract.v1"
)
DEFAULT_RESULT_REVIEW_CONTRACT_LABEL = (
    "Strategy Factory Fake Dry Walk Result Review Contract"
)
RESULT_REVIEW_CONTRACT_STATUS = (
    "READ_ONLY_FAKE_DRY_WALK_RESULT_REVIEW_CONTRACT"
)

REVIEW_STATE_ACTIVE = "FAKE_DRY_WALK_RESULT_REVIEW_ACTIVE"
REVIEW_STATE_BLOCKED = "FAKE_DRY_WALK_RESULT_REVIEW_BLOCKED"

RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX = "NEEDS_FAKE_WALK_FIX"
RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT = (
    "READY_FOR_FAKE_WALK_REPORT_CONTRACT"
)
RESULT_REVIEW_DECISION_PARK = "PARK"
RESULT_REVIEW_DECISION_REJECT = "REJECT"

ALLOWED_RESULT_REVIEW_DECISIONS: tuple[str, ...] = (
    RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    RESULT_REVIEW_DECISION_PARK,
    RESULT_REVIEW_DECISION_REJECT,
)

NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED = (
    "FAKE_WALK_REPORT_CONTRACT_REQUIRED"
)
NEXT_GATE_FAKE_WALK_FIX_REQUIRED = "FAKE_WALK_FIX_REQUIRED"
NEXT_GATE_FAKE_WALK_PARKED = "FAKE_WALK_PARKED"
NEXT_GATE_FAKE_WALK_REJECTED = "FAKE_WALK_REJECTED"
NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION = (
    "AWAIT_FAKE_WALK_RESULT_REVIEW_DECISION"
)
NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT = "AWAIT_FAKE_DRY_WALK_RESULT"

# Fake-only placeholder field names a reviewer must confirm on the result.
REQUIRED_RESULT_FIELDS: tuple[str, ...] = (
    "fake_pass_fail_summary_placeholder",
    "fake_stage_records_placeholder",
    "fake_trace_records_placeholder",
    "fake_operator_review_packet_placeholder",
)

REQUIRED_STAGE_REVIEW_FIELDS: tuple[str, ...] = (
    "stage_name_placeholder",
    "stage_status_placeholder",
    "blocking_findings_placeholder",
)

REQUIRED_TRACE_REVIEW_FIELDS: tuple[str, ...] = (
    "trace_id_placeholder",
    "stage_status_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
)

REQUIRED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "human_sign_off_placeholder",
)

# Verb-safe fake review criteria -- labels only, never executable checks.
REVIEW_PASS_CRITERIA: tuple[str, ...] = (
    "all_fake_stages_marked_fake_pass_placeholder",
    "no_real_artifact_reference_placeholder",
    "operator_sign_off_present_placeholder",
)

REVIEW_FAIL_CRITERIA: tuple[str, ...] = (
    "any_fake_stage_marked_fake_fail_placeholder",
    "any_real_artifact_reference_present_placeholder",
    "missing_operator_sign_off_placeholder",
)

REJECTION_CONDITIONS: tuple[str, ...] = (
    "fake_walk_inactive_placeholder",
    "missing_required_result_field_placeholder",
    "real_artifact_reference_detected_placeholder",
    "missing_operator_review_packet_placeholder",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake dry walk result review contract template and is "
    "execution-free.",
    "It reviews a fake in-memory walk result only and writes no runtime "
    "state.",
    "Every field it names is a fake placeholder, never real output.",
    "It accesses no data and names only fake placeholders.",
    "A human must approve the fake walk result before any later phase is "
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

_SOURCE_FAKE_DRY_WALK_RESULT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Dry Walk In Memory result reference is a fake "
    "placeholder for a later human-reviewed fake walk report."
)

# Keys the upstream Bundle 33 fake walk result must carry to be reviewable.
_REQUIRED_UPSTREAM_RESULT_KEYS: tuple[str, ...] = (
    "pass_fail_summary",
    "stage_records",
    "trace_records",
    "operator_review_packet",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_dry_walk_in_memory_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_dry_walk_result_review_contract_active",
    "fake_dry_walk_result_review_state",
    "fake_dry_walk_active",
    "fake_dry_walk_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_dry_walk_result_reference_placeholder",
    "result_review_decision",
    "allowed_result_review_decisions",
    "required_result_fields",
    "required_stage_review_fields",
    "required_trace_review_fields",
    "required_operator_review_fields",
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
    "fake_dry_walk_result",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESULT_REVIEW_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(result: Any, key: str) -> str:
    """Read a string field from a possibly-malformed result; safe."""
    return _as_text(result.get(key)) if isinstance(result, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_RESULT_REVIEW_DECISIONS else ""


def _upstream_outputs_present(result: Any) -> bool:
    """True when every required Bundle 33 fake output key is present + truthy."""
    if not isinstance(result, dict):
        return False
    return all(bool(result.get(key)) for key in _REQUIRED_UPSTREAM_RESULT_KEYS)


# Inherited all-false safety posture (same 14 keys as Bundles 30-33).
RESULT_REVIEW_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DRY_WALK_IN_MEMORY_SAFETY_POSTURE
)


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_REVIEW_ONLY")
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
    result_fields_ok = (
        tuple(safe.get("required_result_fields") or ())
        == REQUIRED_RESULT_FIELDS
    )
    stage_fields_ok = (
        tuple(safe.get("required_stage_review_fields") or ())
        == REQUIRED_STAGE_REVIEW_FIELDS
    )
    trace_fields_ok = (
        tuple(safe.get("required_trace_review_fields") or ())
        == REQUIRED_TRACE_REVIEW_FIELDS
    )
    operator_fields_ok = (
        tuple(safe.get("required_operator_review_fields") or ())
        == REQUIRED_OPERATOR_REVIEW_FIELDS
    )
    pass_criteria_ok = len(tuple(safe.get("review_pass_criteria") or ())) >= 1
    fail_criteria_ok = len(tuple(safe.get("review_fail_criteria") or ())) >= 1
    rejection_ok = len(tuple(safe.get("rejection_conditions") or ())) >= 1

    fields_ok = (
        decisions_ok
        and result_fields_ok
        and stage_fields_ok
        and trace_fields_ok
        and operator_fields_ok
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
        "required_result_fields_ok": result_fields_ok,
        "required_stage_review_fields_ok": stage_fields_ok,
        "required_trace_review_fields_ok": trace_fields_ok,
        "required_operator_review_fields_ok": operator_fields_ok,
        "review_criteria_present": (
            pass_criteria_ok and fail_criteria_ok and rejection_ok
        ),
        "missing_required_fields": missing,
    }


def validate_fake_dry_walk_result_review_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake dry walk result review
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_fake_dry_walk_result_review_contract(
    fake_dry_walk: Any,
    result_review_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake dry walk result review
    contract template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (fake_dry_walk_result_review_contract_active=True) solely when the upstream
    Bundle 33 fake dry-walk result is active AND its next_gate is
    FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED AND it carries the required fake
    outputs (pass/fail summary, stage records, trace records, operator review
    packet). Even when active, every authorization field stays False -- it
    defines the SHAPE of a human review only, writes no runtime state, accesses
    no data, names only fake placeholders, and grants nothing. Returned dicts
    are fresh."""
    walk_active = (
        isinstance(fake_dry_walk, dict)
        and fake_dry_walk.get("fake_dry_walk_active") is True
    )
    walk_next_gate = _field(fake_dry_walk, "next_gate")
    next_gate_ok = (
        walk_next_gate == NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED
    )
    outputs_present = _upstream_outputs_present(fake_dry_walk)
    contract_active = bool(walk_active and next_gate_ok and outputs_present)

    decision = _normalize_decision(result_review_decision)

    state = (
        REVIEW_STATE_ACTIVE if contract_active else REVIEW_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT
    elif decision == (
        RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
    ):
        next_gate = NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED
    elif decision == RESULT_REVIEW_DECISION_NEEDS_FAKE_WALK_FIX:
        next_gate = NEXT_GATE_FAKE_WALK_FIX_REQUIRED
    elif decision == RESULT_REVIEW_DECISION_PARK:
        next_gate = NEXT_GATE_FAKE_WALK_PARKED
    elif decision == RESULT_REVIEW_DECISION_REJECT:
        next_gate = NEXT_GATE_FAKE_WALK_REJECTED
    else:
        next_gate = NEXT_GATE_AWAIT_RESULT_REVIEW_DECISION

    contract = {
        "schema_version": RESULT_REVIEW_CONTRACT_SCHEMA_VERSION,
        "fake_dry_walk_in_memory_schema_version": (
            DRY_WALK_IN_MEMORY_SCHEMA_VERSION
        ),
        "idea_id": _field(fake_dry_walk, "idea_id"),
        "title": _field(fake_dry_walk, "title"),
        "label": DEFAULT_RESULT_REVIEW_CONTRACT_LABEL,
        "status": RESULT_REVIEW_CONTRACT_STATUS,
        "stage": "FAKE_REVIEW_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_dry_walk_result_review_contract_active": contract_active,
        "fake_dry_walk_result_review_state": state,
        "fake_dry_walk_active": bool(walk_active),
        "fake_dry_walk_next_gate": walk_next_gate,
        "asset_lane": _field(fake_dry_walk, "asset_lane"),
        "timeframe_lane": _field(fake_dry_walk, "timeframe_lane"),
        "source_fake_dry_walk_result_reference_placeholder": (
            _SOURCE_FAKE_DRY_WALK_RESULT_REFERENCE_PLACEHOLDER
        ),
        "result_review_decision": decision,
        "allowed_result_review_decisions": ALLOWED_RESULT_REVIEW_DECISIONS,
        "required_result_fields": REQUIRED_RESULT_FIELDS,
        "required_stage_review_fields": REQUIRED_STAGE_REVIEW_FIELDS,
        "required_trace_review_fields": REQUIRED_TRACE_REVIEW_FIELDS,
        "required_operator_review_fields": REQUIRED_OPERATOR_REVIEW_FIELDS,
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
        "fake_dry_walk_result": (
            fake_dry_walk if isinstance(fake_dry_walk, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_dry_walk_result_review_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake dry walk result
    review contract template. Pure; writes no file. Informational only."""
    decisions = contract.get("allowed_result_review_decisions") or ()
    result_fields = contract.get("required_result_fields") or ()
    stage_fields = contract.get("required_stage_review_fields") or ()
    trace_fields = contract.get("required_trace_review_fields") or ()
    operator_fields = contract.get("required_operator_review_fields") or ()
    pass_criteria = contract.get("review_pass_criteria") or ()
    fail_criteria = contract.get("review_fail_criteria") or ()
    rejection = contract.get("rejection_conditions") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Fake Dry Walk Result Review Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "fake-dry-walk-result-review-contract-only, review-only, "
        "placeholder-only template -- no-runtime-state-write, research-only, "
        "and execution-free. It reviews only a fake in-memory walk result, is "
        "not wired into any runtime state, accesses no data, names only fake "
        "placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Result schema: "
        f"`{contract.get('fake_dry_walk_in_memory_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_REVIEW_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake dry walk result review contract active: "
        f"{contract.get('fake_dry_walk_result_review_contract_active', '')}"
    )
    lines.append(
        "Review state: "
        f"{contract.get('fake_dry_walk_result_review_state', '')}"
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
        "Source fake dry walk result reference: "
        f"{contract.get('source_fake_dry_walk_result_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Allowed Result Review Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Result Fields")
    lines.append("")
    for x in result_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Stage Review Fields")
    lines.append("")
    for x in stage_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Trace Review Fields")
    lines.append("")
    for x in trace_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Review Fields")
    lines.append("")
    for x in operator_fields:
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
        "- A human must approve the fake walk result before any later phase "
        "is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
