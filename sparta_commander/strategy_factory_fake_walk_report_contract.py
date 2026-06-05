"""SPARTA Offline Strategy Factory - FAKE WALK REPORT CONTRACT.

Bundle 35 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only report contract template* builder: it consumes a Bundle
34 fake dry-walk result review contract and, only when that review contract is
active with result_review_decision == READY_FOR_FAKE_WALK_REPORT_CONTRACT and
next_gate == FAKE_WALK_REPORT_CONTRACT_REQUIRED, produces a deterministic,
read-only contract describing the SHAPE of a future fake-walk report. It
defines a report template only -- it writes no report, runs no walk, is NOT a
written report, NOT a live system, NOT a dry walk, NOT a pipeline, NOT an
orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never runs an orchestrator, never writes a
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

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
  - DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL
  - FAKE_WALK_REPORT_CONTRACT_STATUS
  - FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE
  - REPORT_STATE_ACTIVE
  - REPORT_STATE_BLOCKED
  - NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW
  - REQUIRED_REPORT_SECTIONS
  - FAKE_WALK_SUMMARY_FIELDS
  - FAKE_STAGE_SUMMARY_FIELDS
  - FAKE_TRACE_SUMMARY_FIELDS
  - OPERATOR_REVIEW_SUMMARY_FIELDS
  - PASS_FAIL_SUMMARY_FIELDS
  - SAFETY_ATTESTATION_FIELDS
  - build_fake_walk_report_contract(result_review_contract)
  - validate_fake_walk_report_contract(contract)
  - render_fake_walk_report_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_CONTRACT_SCHEMA_VERSION,
    RESULT_REVIEW_CONTRACT_SAFETY_POSTURE,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED,
)

__all__ = [
    "FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL",
    "FAKE_WALK_REPORT_CONTRACT_STATUS",
    "FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE",
    "REPORT_STATE_ACTIVE",
    "REPORT_STATE_BLOCKED",
    "NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW",
    "REQUIRED_REPORT_SECTIONS",
    "FAKE_WALK_SUMMARY_FIELDS",
    "FAKE_STAGE_SUMMARY_FIELDS",
    "FAKE_TRACE_SUMMARY_FIELDS",
    "OPERATOR_REVIEW_SUMMARY_FIELDS",
    "PASS_FAIL_SUMMARY_FIELDS",
    "SAFETY_ATTESTATION_FIELDS",
    "build_fake_walk_report_contract",
    "validate_fake_walk_report_contract",
    "render_fake_walk_report_contract_markdown",
]

FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_walk_report_contract.v1"
)
DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL = (
    "Strategy Factory Fake Walk Report Contract"
)
FAKE_WALK_REPORT_CONTRACT_STATUS = (
    "READ_ONLY_FAKE_WALK_REPORT_CONTRACT"
)

REPORT_STATE_ACTIVE = "FAKE_WALK_REPORT_CONTRACT_ACTIVE"
REPORT_STATE_BLOCKED = "FAKE_WALK_REPORT_CONTRACT_BLOCKED"

NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED = (
    "FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW = (
    "AWAIT_FAKE_DRY_WALK_RESULT_REVIEW"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-34).
FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    RESULT_REVIEW_CONTRACT_SAFETY_POSTURE
)

# Required report sections a future fake-walk report must carry.
REQUIRED_REPORT_SECTIONS: tuple[str, ...] = (
    "executive_summary",
    "fake_walk_scope",
    "fake_stage_walk_summary",
    "fake_trace_summary",
    "operator_review_summary",
    "pass_fail_summary",
    "safety_attestation",
    "blocked_capabilities",
    "next_steps",
)

# Fake placeholder field names per report sub-block.
FAKE_WALK_SUMMARY_FIELDS: tuple[str, ...] = (
    "fake_walk_title_placeholder",
    "fake_walk_scope_placeholder",
    "fake_walk_status_placeholder",
    "fake_walk_overall_result_placeholder",
)

FAKE_STAGE_SUMMARY_FIELDS: tuple[str, ...] = (
    "stage_name_placeholder",
    "stage_status_placeholder",
    "stage_fake_input_placeholder",
    "stage_fake_output_placeholder",
    "blocking_findings_placeholder",
)

FAKE_TRACE_SUMMARY_FIELDS: tuple[str, ...] = (
    "trace_id_placeholder",
    "stage_name_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

OPERATOR_REVIEW_SUMMARY_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

PASS_FAIL_SUMMARY_FIELDS: tuple[str, ...] = (
    "total_stages_placeholder",
    "fake_pass_count_placeholder",
    "fake_fail_count_placeholder",
    "all_fake_stages_passed_placeholder",
    "summary_status_placeholder",
)

SAFETY_ATTESTATION_FIELDS: tuple[str, ...] = (
    "read_only_attestation_placeholder",
    "execution_free_attestation_placeholder",
    "no_real_data_attestation_placeholder",
    "no_runtime_state_write_attestation_placeholder",
    "no_report_file_write_attestation_placeholder",
    "human_approval_required_attestation_placeholder",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake walk report contract template and is execution-free.",
    "It defines the shape of a future fake walk report only and writes no "
    "report file.",
    "It writes no runtime state and is review-only.",
    "Every field it names is a fake placeholder, never real output.",
    "It accesses no data and names only fake placeholders.",
    "A human must approve the fake walk report contract before any report is "
    "drafted.",
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

_SOURCE_FAKE_WALK_RESULT_REVIEW_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Dry Walk Result Review contract reference is a fake "
    "placeholder for a later human-reviewed fake walk report."
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_dry_walk_result_review_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_walk_report_contract_active",
    "fake_walk_report_contract_state",
    "fake_dry_walk_result_review_contract_active",
    "result_review_decision",
    "fake_dry_walk_result_review_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_walk_result_review_reference_placeholder",
    "report_title_placeholder",
    "report_sections_required",
    "fake_walk_summary_fields",
    "fake_stage_summary_fields",
    "fake_trace_summary_fields",
    "operator_review_summary_fields",
    "pass_fail_summary_fields",
    "safety_attestation_fields",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_walk_result_review",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(FAKE_WALK_REPORT_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(review: Any, key: str) -> str:
    """Read a string field from a possibly-malformed review; safe."""
    return _as_text(review.get(key)) if isinstance(review, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_REPORT_CONTRACT_ONLY")
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    sections_ok = (
        tuple(safe.get("report_sections_required") or ())
        == REQUIRED_REPORT_SECTIONS
    )
    walk_fields_ok = (
        tuple(safe.get("fake_walk_summary_fields") or ())
        == FAKE_WALK_SUMMARY_FIELDS
    )
    stage_fields_ok = (
        tuple(safe.get("fake_stage_summary_fields") or ())
        == FAKE_STAGE_SUMMARY_FIELDS
    )
    trace_fields_ok = (
        tuple(safe.get("fake_trace_summary_fields") or ())
        == FAKE_TRACE_SUMMARY_FIELDS
    )
    operator_fields_ok = (
        tuple(safe.get("operator_review_summary_fields") or ())
        == OPERATOR_REVIEW_SUMMARY_FIELDS
    )
    pass_fail_fields_ok = (
        tuple(safe.get("pass_fail_summary_fields") or ())
        == PASS_FAIL_SUMMARY_FIELDS
    )
    attestation_fields_ok = (
        tuple(safe.get("safety_attestation_fields") or ())
        == SAFETY_ATTESTATION_FIELDS
    )

    fields_ok = (
        sections_ok
        and walk_fields_ok
        and stage_fields_ok
        and trace_fields_ok
        and operator_fields_ok
        and pass_fail_fields_ok
        and attestation_fields_ok
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
        "report_sections_ok": sections_ok,
        "fake_walk_summary_fields_ok": walk_fields_ok,
        "fake_stage_summary_fields_ok": stage_fields_ok,
        "fake_trace_summary_fields_ok": trace_fields_ok,
        "operator_review_summary_fields_ok": operator_fields_ok,
        "pass_fail_summary_fields_ok": pass_fail_fields_ok,
        "safety_attestation_fields_ok": attestation_fields_ok,
        "missing_required_fields": missing,
    }


def validate_fake_walk_report_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake walk report contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_walk_report_contract(
    result_review_contract: Any,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only fake walk report contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (fake_walk_report_contract_active=True) solely when the upstream Bundle 34
    fake dry-walk result review contract is active AND its result_review_decision
    is READY_FOR_FAKE_WALK_REPORT_CONTRACT AND its next_gate is
    FAKE_WALK_REPORT_CONTRACT_REQUIRED. Even when active, every authorization
    field stays False -- it defines the SHAPE of a future fake-walk report only,
    writes no report file, writes no runtime state, accesses no data, names only
    fake placeholders, and grants nothing. Returned dicts are fresh."""
    review_active = (
        isinstance(result_review_contract, dict)
        and result_review_contract.get(
            "fake_dry_walk_result_review_contract_active"
        ) is True
    )
    decision = _field(result_review_contract, "result_review_decision")
    review_next_gate = _field(result_review_contract, "next_gate")
    decision_ok = (
        decision == RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
    )
    next_gate_ok = (
        review_next_gate == NEXT_GATE_FAKE_WALK_REPORT_CONTRACT_REQUIRED
    )
    contract_active = bool(review_active and decision_ok and next_gate_ok)

    state = REPORT_STATE_ACTIVE if contract_active else REPORT_STATE_BLOCKED

    next_gate = (
        NEXT_GATE_FAKE_WALK_REPORT_OPERATOR_REVIEW_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_FAKE_DRY_WALK_RESULT_REVIEW
    )

    contract = {
        "schema_version": FAKE_WALK_REPORT_CONTRACT_SCHEMA_VERSION,
        "fake_dry_walk_result_review_contract_schema_version": (
            RESULT_REVIEW_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _field(result_review_contract, "idea_id"),
        "title": _field(result_review_contract, "title"),
        "label": DEFAULT_FAKE_WALK_REPORT_CONTRACT_LABEL,
        "status": FAKE_WALK_REPORT_CONTRACT_STATUS,
        "stage": "FAKE_REPORT_CONTRACT_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_walk_report_contract_active": contract_active,
        "fake_walk_report_contract_state": state,
        "fake_dry_walk_result_review_contract_active": bool(review_active),
        "result_review_decision": decision,
        "fake_dry_walk_result_review_next_gate": review_next_gate,
        "asset_lane": _field(result_review_contract, "asset_lane"),
        "timeframe_lane": _field(result_review_contract, "timeframe_lane"),
        "source_fake_walk_result_review_reference_placeholder": (
            _SOURCE_FAKE_WALK_RESULT_REVIEW_REFERENCE_PLACEHOLDER
        ),
        "report_title_placeholder": (
            "Fake Walk Report (fake placeholder title -- no real walk)"
        ),
        "report_sections_required": REQUIRED_REPORT_SECTIONS,
        "fake_walk_summary_fields": FAKE_WALK_SUMMARY_FIELDS,
        "fake_stage_summary_fields": FAKE_STAGE_SUMMARY_FIELDS,
        "fake_trace_summary_fields": FAKE_TRACE_SUMMARY_FIELDS,
        "operator_review_summary_fields": OPERATOR_REVIEW_SUMMARY_FIELDS,
        "pass_fail_summary_fields": PASS_FAIL_SUMMARY_FIELDS,
        "safety_attestation_fields": SAFETY_ATTESTATION_FIELDS,
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
        "fake_walk_result_review": (
            result_review_contract
            if isinstance(result_review_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_walk_report_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake walk report contract
    template. Pure; writes no file. Informational only."""
    sections = contract.get("report_sections_required") or ()
    walk_fields = contract.get("fake_walk_summary_fields") or ()
    stage_fields = contract.get("fake_stage_summary_fields") or ()
    trace_fields = contract.get("fake_trace_summary_fields") or ()
    operator_fields = contract.get("operator_review_summary_fields") or ()
    pass_fail_fields = contract.get("pass_fail_summary_fields") or ()
    attestation_fields = contract.get("safety_attestation_fields") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Walk Report Contract")
    lines.append("")
    lines.append(
        "Template only: this is a fake-walk-report-contract-only, "
        "review-only, placeholder-only template -- no-report-file-write, "
        "no-runtime-state-write, research-only, and execution-free. It defines "
        "only the shape of a future fake walk report, is not wired into any "
        "runtime state, writes no report file, accesses no data, names only "
        "fake placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Review schema: "
        f"`{contract.get('fake_dry_walk_result_review_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: FAKE_REPORT_CONTRACT_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake walk report contract active: "
        f"{contract.get('fake_walk_report_contract_active', '')}"
    )
    lines.append(
        "Report contract state: "
        f"{contract.get('fake_walk_report_contract_state', '')}"
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
        "Source fake walk result review reference: "
        f"{contract.get('source_fake_walk_result_review_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Report Title")
    lines.append("")
    lines.append(
        "Report title: "
        f"{contract.get('report_title_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Required Report Sections")
    lines.append("")
    for x in sections:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Walk Summary Fields")
    lines.append("")
    for x in walk_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Stage Summary Fields")
    lines.append("")
    for x in stage_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Trace Summary Fields")
    lines.append("")
    for x in trace_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Operator Review Summary Fields")
    lines.append("")
    for x in operator_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Pass Fail Summary Fields")
    lines.append("")
    for x in pass_fail_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Safety Attestation Fields")
    lines.append("")
    for x in attestation_fields:
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
        "- A human must approve the fake walk report contract before any "
        "report is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
