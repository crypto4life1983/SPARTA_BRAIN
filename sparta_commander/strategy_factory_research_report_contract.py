"""SPARTA Offline Strategy Factory - RESEARCH REPORT CONTRACT v1.

Bundle 15 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only research report contract* builder: it consumes
Bundle 14 research task packets and produces deterministic, read-only
research report contract templates. A report contract defines HOW future
research findings must be reported -- which sections are required, which
safety fields must be present, and which verdicts are allowed. It never
performs research, never inspects market data, fetches nothing, computes no
backtest, and grants no capability.

It is informational, read-only, and report-contract-only. It runs nothing,
computes no backtest, fetches no data, inspects no market data, writes no
file, opens no network, spawns no subprocess, touches no
broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL
  - RESEARCH_REPORT_CONTRACT_STATUS
  - RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE
  - REPORT_VERDICT_NEEDS_MORE_SPEC
  - REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT
  - REPORT_VERDICT_PARK_RESEARCH_ONLY
  - REPORT_VERDICT_REJECT_RESEARCH_ONLY
  - build_research_report_contract(item, *, human_research_approved=False)
  - build_research_report_contract_batch(items, *, label=None,
        human_research_approved_by_id=None)
  - validate_research_report_contract(contract)
  - render_research_report_contract_markdown(contract)
  - render_research_report_contract_batch_markdown(batch)
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
    RESEARCH_TASK_PACKET_STATUS,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
    TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL,
    TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC,
    TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM,
    build_research_task_packet,
    build_research_task_packet_batch,
)

__all__ = [
    "RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL",
    "RESEARCH_REPORT_CONTRACT_STATUS",
    "RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE",
    "REPORT_VERDICT_NEEDS_MORE_SPEC",
    "REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT",
    "REPORT_VERDICT_PARK_RESEARCH_ONLY",
    "REPORT_VERDICT_REJECT_RESEARCH_ONLY",
    "build_research_report_contract",
    "build_research_report_contract_batch",
    "validate_research_report_contract",
    "render_research_report_contract_markdown",
    "render_research_report_contract_batch_markdown",
]

RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_research_report_contract.v1"
)
DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL = (
    "Strategy Factory Research Report Contract"
)
RESEARCH_REPORT_CONTRACT_STATUS = "READ_ONLY_REPORT_CONTRACT"

REPORT_VERDICT_NEEDS_MORE_SPEC = "NEEDS_MORE_SPEC"
REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT = "READY_FOR_PROTOCOL_DRAFT"
REPORT_VERDICT_PARK_RESEARCH_ONLY = "PARK_RESEARCH_ONLY"
REPORT_VERDICT_REJECT_RESEARCH_ONLY = "REJECT_RESEARCH_ONLY"

# Inherited all-false safety posture (same keys as Bundle 14). Pinned False:
# a report contract only describes how to report; it grants nothing.
RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_TASK_PACKET_SAFETY_POSTURE
)

# The exact, ordered set of verdicts a future research-only report may carry.
_ALLOWED_VERDICTS: tuple[str, ...] = (
    REPORT_VERDICT_NEEDS_MORE_SPEC,
    REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT,
    REPORT_VERDICT_PARK_RESEARCH_ONLY,
    REPORT_VERDICT_REJECT_RESEARCH_ONLY,
)

# Map a Bundle 14 task packet status to report-contract gating.
_PACKET_STATUS_NEXT_GATE: dict[str, str] = {
    TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM: "fix_research_queue_item",
    TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL: "human_research_approval",
    TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC: "research_report_draft",
}

# Deterministic, neutral report sections a later report must contain.
_REQUIRED_REPORT_SECTIONS: tuple[str, ...] = (
    "hypothesis_summary",
    "asset_lane_and_timeframe",
    "assumptions_to_verify",
    "risk_notes",
    "invalidation_conditions",
    "evidence_needed_later",
    "blocked_capabilities",
    "research_only_verdict",
    "next_gate",
)

# Deterministic placeholders. None of these authorize any live capability.
_EVIDENCE_REQUIREMENTS: tuple[str, ...] = (
    "Evidence requirements are placeholders for a later approved protocol.",
    "No market data is inspected by this contract.",
    "No historical simulation gate is opened by this contract.",
    "No broker or exchange surface is authorized by this contract.",
)

# Capabilities that stay blocked for every contract, regardless of status.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "data_fetch",
    "backtest",
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
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "task_packet_schema_version",
    "planner_schema_version",
    "reader_schema_version",
    "research_queue_schema_version",
    "idea_id",
    "title",
    "stage",
    "mode",
    "status",
    "task_packet_status",
    "research_spec_allowed",
    "report_contract_allowed",
    "allowed_verdicts",
    "default_verdict",
    "human_approval_required",
    "read_only",
    "executes",
    "safety",
    "task_packet",
    "required_report_sections",
    "evidence_requirements",
    "blocked_capabilities",
    "next_gate",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    plan_only = safe.get("stage") == "PLAN_ONLY"
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(
        safe.get(flag) is False for flag in _AUTH_FLAGS
    )
    safety = safe.get("safety")
    safety_all_false = (
        isinstance(safety, dict)
        and len(safety) > 0
        and all(v is False for v in safety.values())
    )
    verdicts_ok = tuple(safe.get("allowed_verdicts") or ()) == _ALLOWED_VERDICTS
    sections = tuple(safe.get("required_report_sections") or ())
    sections_ok = all(s in sections for s in _REQUIRED_REPORT_SECTIONS)

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and verdicts_ok
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
        "allowed_verdicts_ok": verdicts_ok,
        "required_sections_present": sections_ok,
        "missing_required_fields": missing,
    }


def validate_research_report_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a report contract. Pure; no I/O."""
    return _validate(contract)


def build_research_report_contract(
    item: Any,
    *,
    human_research_approved: bool = False,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only research report contract.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise. Even when report_contract_allowed is True, every
    authorization field stays False -- a contract describes how to report,
    never grants permission. Returned dicts are fresh."""
    task_packet = build_research_task_packet(
        item, human_research_approved=human_research_approved
    )
    task_packet_status = task_packet["task_packet_status"]
    report_contract_allowed = (
        task_packet_status == TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
    )

    contract = {
        "schema_version": RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
        "task_packet_schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(task_packet.get("idea_id")),
        "title": _as_text(task_packet.get("title")),
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "status": RESEARCH_REPORT_CONTRACT_STATUS,
        "task_packet_status": task_packet_status,
        "research_spec_allowed": bool(task_packet["research_spec_allowed"]),
        "report_contract_allowed": report_contract_allowed,
        "allowed_verdicts": _ALLOWED_VERDICTS,
        "default_verdict": REPORT_VERDICT_NEEDS_MORE_SPEC,
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
        "safety": _safety_posture(),
        "task_packet": task_packet,
        "required_report_sections": _REQUIRED_REPORT_SECTIONS,
        "evidence_requirements": _EVIDENCE_REQUIREMENTS,
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "next_gate": _PACKET_STATUS_NEXT_GATE[task_packet_status],
    }
    contract["validation"] = _validate(contract)
    return contract


def build_research_report_contract_batch(
    items: tuple[Any, ...],
    *,
    label: str | None = None,
    human_research_approved_by_id: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic batch of read-only report contracts.

    Pure; no I/O, no mutation. All authorization counts stay 0; the batch is
    read-only and inert with an all-false safety posture. The
    human_research_approved_by_id map is read-only input only -- no approval
    is recorded anywhere. Consumes Bundle 14 build_research_task_packet_batch
    for its read-only task packet snapshot."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_RESEARCH_REPORT_CONTRACT_LABEL
    )
    approvals = (
        human_research_approved_by_id
        if isinstance(human_research_approved_by_id, dict)
        else {}
    )
    item_tuple = tuple(items)

    contracts: list[dict[str, Any]] = []
    for it in item_tuple:
        idea_id = _as_text(it.get("idea_id")) if isinstance(it, dict) else ""
        approved = approvals.get(idea_id, False) is True
        contracts.append(
            build_research_report_contract(
                it, human_research_approved=approved
            )
        )
    contract_tuple = tuple(contracts)
    validations = tuple(c["validation"] for c in contract_tuple)

    allowed_count = sum(
        1 for c in contract_tuple if c["report_contract_allowed"]
    )
    blocked_count = len(contract_tuple) - allowed_count
    valid_count = sum(1 for v in validations if v["valid"])
    invalid_count = len(validations) - valid_count

    task_packet_batch = build_research_task_packet_batch(
        item_tuple,
        label=name,
        human_research_approved_by_id=approvals,
    )

    return {
        "schema_version": RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
        "task_packet_schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": RESEARCH_REPORT_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "total_items": len(item_tuple),
        "report_contract_allowed_count": allowed_count,
        "blocked_contract_count": blocked_count,
        "valid_contract_count": valid_count,
        "invalid_contract_count": invalid_count,
        "approved_for_research_count": 0,
        "execution_authorized_count": 0,
        "paper_trading_authorized_count": 0,
        "live_trading_authorized_count": 0,
        "data_fetch_authorized_count": 0,
        "backtest_authorized_count": 0,
        "promotion_authorized_count": 0,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "safety": _safety_posture(),
        "task_packet_batch": task_packet_batch,
        "contracts": contract_tuple,
        "validation": validations,
        "next_gate": "research_report_review",
    }


def render_research_report_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for one report contract.
    Pure; writes no file. Informational only."""
    safety = contract.get("safety") or {}
    sections = contract.get("required_report_sections") or ()
    evidence = contract.get("evidence_requirements") or ()
    verdicts = contract.get("allowed_verdicts") or ()
    blocked = contract.get("blocked_capabilities") or ()
    task_packet = contract.get("task_packet") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Report Contract")
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Task packet schema: "
        f"`{contract.get('task_packet_schema_version', '')}`"
    )
    lines.append(f"Planner schema: `{contract.get('planner_schema_version', '')}`")
    lines.append(f"Reader schema: `{contract.get('reader_schema_version', '')}`")
    lines.append(
        "Research queue schema: "
        f"`{contract.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append(
        f"Report contract allowed: {contract.get('report_contract_allowed', '')}"
    )
    lines.append(f"Default verdict: {contract.get('default_verdict', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Required Report Sections")
    lines.append("")
    for s in sections:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append("## Evidence Requirements")
    lines.append("")
    for e in evidence:
        lines.append(f"- {e}")
    lines.append("")
    lines.append("## Allowed Verdicts")
    lines.append("")
    for v in verdicts:
        lines.append(f"- `{v}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Task Packet")
    lines.append("")
    lines.append(f"- `idea_id`: `{task_packet.get('idea_id', '')}`")
    lines.append(
        f"- `task_packet_status`: `{task_packet.get('task_packet_status', '')}`"
    )
    lines.append(f"- `read_only`: `{task_packet.get('read_only', '')}`")
    lines.append(f"- `executes`: `{task_packet.get('executes', '')}`")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for key, value in validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this contract and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_research_report_contract_batch_markdown(
    batch: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a report contract batch.
    Pure; writes no file. Informational only."""
    safety = batch.get("safety") or {}
    contracts = batch.get("contracts") or ()
    task_packet_batch = batch.get("task_packet_batch") or {}
    validations = batch.get("validation") or ()

    lines: list[str] = []
    lines.append("# Strategy Factory Research Report Contract Batch")
    lines.append("")
    lines.append(f"Schema: `{batch.get('schema_version', '')}`")
    lines.append(
        "Task packet schema: "
        f"`{batch.get('task_packet_schema_version', '')}`"
    )
    lines.append(f"Planner schema: `{batch.get('planner_schema_version', '')}`")
    lines.append(f"Reader schema: `{batch.get('reader_schema_version', '')}`")
    lines.append(
        "Research queue schema: "
        f"`{batch.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Label: {batch.get('label', '')}")
    lines.append(f"Status: {batch.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Total items: {batch.get('total_items', 0)}")
    lines.append(
        "Report contract allowed count: "
        f"{batch.get('report_contract_allowed_count', 0)}"
    )
    lines.append(
        f"Blocked contract count: {batch.get('blocked_contract_count', 0)}"
    )
    lines.append(
        f"Valid contract count: {batch.get('valid_contract_count', 0)}"
    )
    lines.append(
        f"Invalid contract count: {batch.get('invalid_contract_count', 0)}"
    )
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Contracts")
    lines.append("")
    if contracts:
        for c in contracts:
            lines.append(
                f"- `{c.get('idea_id', '')}` {c.get('title', '')} "
                f"(allowed=`{c.get('report_contract_allowed', '')}`, "
                f"read_only=`{c.get('read_only', '')}`, "
                f"executes=`{c.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Task Packet Batch")
    lines.append("")
    lines.append(
        f"- `total_items`: `{task_packet_batch.get('total_items', 0)}`"
    )
    lines.append(
        "- `ready_for_research_spec_count`: "
        f"`{task_packet_batch.get('ready_for_research_spec_count', 0)}`"
    )
    lines.append(
        f"- `read_only`: `{task_packet_batch.get('read_only', '')}`"
    )
    lines.append(
        f"- `executes`: `{task_packet_batch.get('executes', '')}`"
    )
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    valid_total = sum(1 for v in validations if v.get("valid"))
    lines.append(f"- `valid_contract_count`: `{valid_total}`")
    lines.append(f"- `total_validations`: `{len(validations)}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this batch and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
