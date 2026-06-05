"""SPARTA Offline Strategy Factory - RESEARCH PROTOCOL DRAFT CONTRACT v1.

Bundle 18 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only research protocol draft contract* builder: it consumes
a Bundle 16 research decision memo contract and, only when the recorded memo
decision is READY_FOR_PROTOCOL_DRAFT, produces a deterministic, read-only
*template* describing the shape a future human-authored research protocol must
take. It never creates a runnable protocol, never performs research, never
inspects market data, fetches nothing, runs no historical simulation, and
grants no capability.

It is informational, read-only, and template-only. It runs nothing, computes
no historical simulation, fetches no data, inspects no market data, writes no
file, opens no network, spawns no subprocess, touches no
broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL
  - RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS
  - RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE
  - PROTOCOL_DRAFT_STATE_ACTIVE
  - PROTOCOL_DRAFT_STATE_BLOCKED
  - NEXT_GATE_PROTOCOL_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION
  - build_research_protocol_draft_contract(item, *, memo_decision=None,
        human_research_approved=False)
  - validate_research_protocol_draft_contract(contract)
  - render_research_protocol_draft_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    QUEUE_PLANNER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_report_contract import (
    RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
    RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE,
    MEMO_DECISION_NEEDS_MORE_SPEC,
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
    MEMO_DECISION_PARK_RESEARCH_ONLY,
    MEMO_DECISION_REJECT_RESEARCH_ONLY,
    build_research_decision_memo_contract,
)

__all__ = [
    "RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL",
    "RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS",
    "RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE",
    "PROTOCOL_DRAFT_STATE_ACTIVE",
    "PROTOCOL_DRAFT_STATE_BLOCKED",
    "NEXT_GATE_PROTOCOL_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION",
    "build_research_protocol_draft_contract",
    "validate_research_protocol_draft_contract",
    "render_research_protocol_draft_contract_markdown",
]

RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_research_protocol_draft_contract.v1"
)
DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL = (
    "Strategy Factory Research Protocol Draft Contract"
)
RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS = "READ_ONLY_PROTOCOL_DRAFT_CONTRACT"

PROTOCOL_DRAFT_STATE_ACTIVE = "PROTOCOL_DRAFT_ACTIVE"
PROTOCOL_DRAFT_STATE_BLOCKED = "PROTOCOL_DRAFT_BLOCKED"

NEXT_GATE_PROTOCOL_REVIEW_REQUIRED = "PROTOCOL_REVIEW_REQUIRED"
NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION = "AWAIT_PROTOCOL_DRAFT_DECISION"

# Inherited all-false safety posture (same keys as Bundle 16). Pinned False:
# a protocol draft contract only describes a template; it grants nothing.
RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE
)

# Deterministic, neutral protocol-document sections a later protocol must hold.
_REQUIRED_SECTIONS: tuple[str, ...] = (
    "objective_statement",
    "hypothesis_restatement",
    "asset_lane_and_timeframe",
    "method_outline_placeholder",
    "success_criteria_placeholders",
    "invalidation_criteria_placeholders",
    "evidence_plan_placeholder",
    "safety_gate_review",
    "operator_review_notes",
    "next_gate",
)

# Deterministic, verb-safe placeholders. None authorize any live capability.
_SUCCESS_CRITERIA_PLACEHOLDERS: tuple[str, ...] = (
    "Success criteria are placeholders for a later human-authored protocol.",
    "No market data is inspected by this contract.",
    "No historical simulation gate is opened by this contract.",
    "No broker or exchange surface is authorized by this contract.",
)

_INVALIDATION_CRITERIA_PLACEHOLDERS: tuple[str, ...] = (
    "Invalidation criteria are placeholders for a later human-authored "
    "protocol.",
    "No live capability is opened by this contract.",
    "The protocol draft cannot authorize execution.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only protocol draft contract and is execution-free.",
    "A human must review and author the real protocol out of band.",
    "Keep data, simulation, broker, exchange, distribution, and autopilot "
    "gates closed until separately approved.",
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
    "decision_memo_schema_version",
    "report_contract_schema_version",
    "task_packet_schema_version",
    "planner_schema_version",
    "reader_schema_version",
    "research_queue_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "memo_decision",
    "allowed_memo_decisions",
    "decision_memo_allowed",
    "protocol_draft_active",
    "protocol_draft_state",
    "objective",
    "hypothesis_restated",
    "asset_lane",
    "timeframe_lane",
    "required_sections",
    "success_criteria_placeholders",
    "invalidation_criteria_placeholders",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "decision_memo_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _item_field(item: Any, key: str) -> str:
    """Read a string field from a possibly-malformed item; never raises."""
    return _as_text(item.get(key)) if isinstance(item, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION
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
    sections = tuple(safe.get("required_sections") or ())
    sections_ok = all(s in sections for s in _REQUIRED_SECTIONS)

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and sections_ok
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
        "required_sections_present": sections_ok,
        "missing_required_fields": missing,
    }


def validate_research_protocol_draft_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a protocol draft contract.
    Pure; no I/O."""
    return _validate(contract)


def build_research_protocol_draft_contract(
    item: Any,
    *,
    memo_decision: str | None = None,
    human_research_approved: bool = False,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only protocol draft contract.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise. The contract is a TEMPLATE only: it becomes active
    (protocol_draft_active=True) solely when the upstream Bundle 16 memo
    contract is allowed AND the recorded memo_decision is
    READY_FOR_PROTOCOL_DRAFT. Even when active, every authorization field
    stays False -- it never creates a runnable protocol, runs nothing, and
    grants nothing. Returned dicts are fresh."""
    memo_contract = build_research_decision_memo_contract(
        item, human_research_approved=human_research_approved
    )
    decision = (
        memo_decision
        if isinstance(memo_decision, str) and memo_decision
        else MEMO_DECISION_NEEDS_MORE_SPEC
    )
    decision_memo_allowed = bool(memo_contract["decision_memo_allowed"])

    protocol_draft_active = bool(
        decision_memo_allowed
        and decision == MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT
    )
    state = (
        PROTOCOL_DRAFT_STATE_ACTIVE if protocol_draft_active
        else PROTOCOL_DRAFT_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_PROTOCOL_REVIEW_REQUIRED if protocol_draft_active
        else NEXT_GATE_AWAIT_PROTOCOL_DRAFT_DECISION
    )
    objective = (
        "Define the shape of a future human-authored research protocol for "
        "the approved idea."
        if protocol_draft_active
        else "Protocol drafting stays blocked until a "
        "READY_FOR_PROTOCOL_DRAFT memo decision is recorded out of band."
    )

    contract = {
        "schema_version": RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION,
        "decision_memo_schema_version": (
            RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION
        ),
        "report_contract_schema_version": (
            RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
        ),
        "task_packet_schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(memo_contract.get("idea_id")),
        "title": _as_text(memo_contract.get("title")),
        "label": DEFAULT_RESEARCH_PROTOCOL_DRAFT_CONTRACT_LABEL,
        "status": RESEARCH_PROTOCOL_DRAFT_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "memo_decision": decision,
        "allowed_memo_decisions": tuple(
            memo_contract.get("allowed_memo_decisions") or ()
        ),
        "decision_memo_allowed": decision_memo_allowed,
        "protocol_draft_active": protocol_draft_active,
        "protocol_draft_state": state,
        "objective": objective,
        "hypothesis_restated": _item_field(item, "thesis"),
        "asset_lane": _item_field(item, "asset_lane"),
        "timeframe_lane": _item_field(item, "timeframe"),
        "required_sections": _REQUIRED_SECTIONS,
        "success_criteria_placeholders": _SUCCESS_CRITERIA_PLACEHOLDERS,
        "invalidation_criteria_placeholders": (
            _INVALIDATION_CRITERIA_PLACEHOLDERS
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
        "decision_memo_contract": memo_contract,
    }
    contract["validation"] = _validate(contract)
    return contract


def render_research_protocol_draft_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a protocol draft contract.
    Pure; writes no file. Informational only."""
    sections = contract.get("required_sections") or ()
    success = contract.get("success_criteria_placeholders") or ()
    invalidation = contract.get("invalidation_criteria_placeholders") or ()
    blocked = contract.get("blocked_capabilities") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Protocol Draft Contract")
    lines.append("")
    lines.append("Template only: this document is execution-free and grants "
                 "no capability.")
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Decision memo schema: "
        f"`{contract.get('decision_memo_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Memo decision: {contract.get('memo_decision', '')}")
    lines.append(
        f"Protocol draft active: {contract.get('protocol_draft_active', '')}"
    )
    lines.append(
        f"Protocol draft state: {contract.get('protocol_draft_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Objective: {contract.get('objective', '')}")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Required Sections")
    lines.append("")
    for s in sections:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append("## Success Criteria Placeholders")
    lines.append("")
    for s in success:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Invalidation Criteria Placeholders")
    lines.append("")
    for s in invalidation:
        lines.append(f"- {s}")
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
        "- A human must review this template and author the real protocol "
        "out of band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
