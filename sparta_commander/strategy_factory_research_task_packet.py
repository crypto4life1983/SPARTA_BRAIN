"""SPARTA Offline Strategy Factory - RESEARCH TASK PACKET v1.

Bundle 14 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only research task packet* builder: it consumes
Bundle 13 queue planner decisions and produces deterministic, read-only
research task packets. A task packet defines WHAT should be researched
later; it never performs research, never inspects market data, fetches
nothing, computes no backtest, and grants no capability.

It is informational, read-only, and task-packet-only. It runs nothing,
computes no backtest, fetches no data, inspects no market data, writes no
file, opens no network, spawns no subprocess, touches no
broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_TASK_PACKET_SCHEMA_VERSION
  - DEFAULT_RESEARCH_TASK_PACKET_LABEL
  - RESEARCH_TASK_PACKET_STATUS
  - RESEARCH_TASK_PACKET_SAFETY_POSTURE
  - TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL
  - TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
  - TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM
  - build_research_task_packet(item, *, human_research_approved=False)
  - build_research_task_packet_batch(items, *, label=None,
        human_research_approved_by_id=None)
  - render_research_task_packet_markdown(packet)
  - render_research_task_packet_batch_markdown(batch)
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
    QUEUE_PLANNER_STATUS,
    QUEUE_PLANNER_SAFETY_POSTURE,
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL,
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN,
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX,
    build_queue_plan_decision,
    build_queue_plan_summary,
)

__all__ = [
    "RESEARCH_TASK_PACKET_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_TASK_PACKET_LABEL",
    "RESEARCH_TASK_PACKET_STATUS",
    "RESEARCH_TASK_PACKET_SAFETY_POSTURE",
    "TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL",
    "TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC",
    "TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM",
    "build_research_task_packet",
    "build_research_task_packet_batch",
    "render_research_task_packet_markdown",
    "render_research_task_packet_batch_markdown",
]

RESEARCH_TASK_PACKET_SCHEMA_VERSION = "strategy_factory_research_task_packet.v1"
DEFAULT_RESEARCH_TASK_PACKET_LABEL = "Strategy Factory Research Task Packet"
RESEARCH_TASK_PACKET_STATUS = "READ_ONLY_TASK_PACKET_REVIEW"

TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL = (
    "BLOCKED_AWAITING_HUMAN_APPROVAL"
)
TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC = "READY_FOR_RESEARCH_SPEC"
TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM = "BLOCKED_INVALID_ITEM"

# Inherited all-false safety posture (same keys as Bundle 13). Pinned False:
# a task packet only describes future research; it grants nothing.
RESEARCH_TASK_PACKET_SAFETY_POSTURE: dict[str, bool] = dict(
    QUEUE_PLANNER_SAFETY_POSTURE
)

# Map a Bundle 13 planner decision to a task packet status.
_PLANNER_TO_PACKET_STATUS: dict[str, str] = {
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX: (
        TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM
    ),
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL: (
        TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL
    ),
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN: (
        TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
    ),
}

# Next-gate hint per task packet status.
_PACKET_STATUS_NEXT_GATE: dict[str, str] = {
    TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM: "human_item_repair",
    TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL: "human_research_approval",
    TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC: "research_spec_contract",
}

# Deterministic, neutral research questions. No execution/trading wording.
_DEFAULT_RESEARCH_QUESTIONS: tuple[str, ...] = (
    "What is the precise hypothesis?",
    "What market and timeframe does the idea belong to?",
    "What assumptions must be documented before any later test gate?",
    "What invalidation conditions would make the idea unsuitable?",
    "What safety gates must remain closed?",
)

# Capabilities that stay blocked for every packet, regardless of status.
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


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_TASK_PACKET_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _scope_field(item: Any, key: str, fallback: str) -> str:
    """Read a scope field from a dict item with a safe fallback."""
    if isinstance(item, dict):
        text = _as_text(item.get(key))
        if text:
            return text
    return fallback


def build_research_task_packet(
    item: Any,
    *,
    human_research_approved: bool = False,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only research task packet.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise (they resolve to BLOCKED_INVALID_ITEM). Even when the
    packet is READY_FOR_RESEARCH_SPEC, every authorization field stays False
    -- a packet describes future research, never grants permission. Returned
    dicts are fresh."""
    planner_decision_packet = build_queue_plan_decision(
        item, human_research_approved=human_research_approved
    )
    planner_decision = planner_decision_packet["decision"]
    valid = bool(planner_decision_packet["valid"])
    task_packet_status = _PLANNER_TO_PACKET_STATUS[planner_decision]
    research_spec_allowed = (
        task_packet_status == TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
    )

    research_scope = {
        "objective": (
            "Define a documented research question for idea "
            f"{_scope_field(item, 'idea_id', '(unknown)')}; this is a "
            "planning description only and authorizes nothing."
        ),
        "asset_lane": _scope_field(item, "asset_lane", "UNSPECIFIED"),
        "timeframe": _scope_field(item, "timeframe", "UNSPECIFIED"),
        "source": _scope_field(item, "source", "UNSPECIFIED"),
        "thesis": _scope_field(item, "thesis", "(none)"),
    }

    return {
        "schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(planner_decision_packet.get("idea_id")),
        "title": _as_text(planner_decision_packet.get("title")),
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "status": RESEARCH_TASK_PACKET_STATUS,
        "task_packet_status": task_packet_status,
        "planner_decision": planner_decision,
        "human_research_approved": bool(
            planner_decision_packet["human_research_approved"]
        ),
        "valid": valid,
        "research_spec_allowed": research_spec_allowed,
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
        "planner_decision_packet": planner_decision_packet,
        "research_scope": research_scope,
        "required_research_questions": _DEFAULT_RESEARCH_QUESTIONS,
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "next_gate": _PACKET_STATUS_NEXT_GATE[task_packet_status],
    }


def build_research_task_packet_batch(
    items: tuple[Any, ...],
    *,
    label: str | None = None,
    human_research_approved_by_id: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic batch of read-only task packets.

    Pure; no I/O, no mutation. All authorization counts stay 0; the batch is
    read-only and inert with an all-false safety posture. The
    human_research_approved_by_id map is read-only input only -- no approval
    is recorded anywhere. Consumes Bundle 13 build_queue_plan_summary for its
    read-only planner snapshot."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_RESEARCH_TASK_PACKET_LABEL
    )
    approvals = (
        human_research_approved_by_id
        if isinstance(human_research_approved_by_id, dict)
        else {}
    )
    item_tuple = tuple(items)

    packets: list[dict[str, Any]] = []
    for it in item_tuple:
        idea_id = _as_text(it.get("idea_id")) if isinstance(it, dict) else ""
        approved = approvals.get(idea_id, False) is True
        packets.append(
            build_research_task_packet(it, human_research_approved=approved)
        )
    packet_tuple = tuple(packets)

    ready_count = sum(
        1 for p in packet_tuple
        if p["task_packet_status"]
        == TASK_PACKET_STATUS_READY_FOR_RESEARCH_SPEC
    )
    awaiting_count = sum(
        1 for p in packet_tuple
        if p["task_packet_status"]
        == TASK_PACKET_STATUS_BLOCKED_AWAITING_APPROVAL
    )
    invalid_count = sum(
        1 for p in packet_tuple
        if p["task_packet_status"]
        == TASK_PACKET_STATUS_BLOCKED_INVALID_ITEM
    )

    planner_summary = build_queue_plan_summary(
        item_tuple,
        label=name,
        human_research_approved_by_id=approvals,
    )

    return {
        "schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": RESEARCH_TASK_PACKET_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "total_items": len(item_tuple),
        "ready_for_research_spec_count": ready_count,
        "blocked_awaiting_approval_count": awaiting_count,
        "blocked_invalid_item_count": invalid_count,
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
        "planner_summary": planner_summary,
        "task_packets": packet_tuple,
        "next_gate": "research_spec_contract",
    }


def render_research_task_packet_markdown(packet: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for one task packet.
    Pure; writes no file. Informational only."""
    safety = packet.get("safety") or {}
    scope = packet.get("research_scope") or {}
    questions = packet.get("required_research_questions") or ()
    blocked = packet.get("blocked_capabilities") or ()
    planner_packet = packet.get("planner_decision_packet") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Task Packet")
    lines.append("")
    lines.append(f"Schema: `{packet.get('schema_version', '')}`")
    lines.append(f"Planner schema: `{packet.get('planner_schema_version', '')}`")
    lines.append(f"Reader schema: `{packet.get('reader_schema_version', '')}`")
    lines.append(
        "Research queue schema: "
        f"`{packet.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {packet.get('idea_id', '')}")
    lines.append(f"Title: {packet.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {packet.get('status', '')}")
    lines.append(f"Task packet status: {packet.get('task_packet_status', '')}")
    lines.append(f"Planner decision: {packet.get('planner_decision', '')}")
    lines.append(
        f"Research spec allowed: {packet.get('research_spec_allowed', '')}"
    )
    lines.append(
        f"Human research approved: {packet.get('human_research_approved', '')}"
    )
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Research Scope")
    lines.append("")
    for key in ("objective", "asset_lane", "timeframe", "source", "thesis"):
        lines.append(f"- `{key}`: {scope.get(key, '')}")
    lines.append("")
    lines.append("## Required Research Questions")
    lines.append("")
    if questions:
        for q in questions:
            lines.append(f"- {q}")
    else:
        lines.append("- (none)")
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
    lines.append("## Planner Decision")
    lines.append("")
    lines.append(f"- `decision`: `{planner_packet.get('decision', '')}`")
    lines.append(f"- `valid`: `{planner_packet.get('valid', '')}`")
    lines.append(f"- `read_only`: `{planner_packet.get('read_only', '')}`")
    lines.append(f"- `executes`: `{planner_packet.get('executes', '')}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this packet and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_research_task_packet_batch_markdown(batch: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for a task packet batch.
    Pure; writes no file. Informational only."""
    safety = batch.get("safety") or {}
    packets = batch.get("task_packets") or ()
    planner_summary = batch.get("planner_summary") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Task Packet Batch")
    lines.append("")
    lines.append(f"Schema: `{batch.get('schema_version', '')}`")
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
        "Ready for research spec count: "
        f"{batch.get('ready_for_research_spec_count', 0)}"
    )
    lines.append(
        "Blocked awaiting approval count: "
        f"{batch.get('blocked_awaiting_approval_count', 0)}"
    )
    lines.append(
        "Blocked invalid item count: "
        f"{batch.get('blocked_invalid_item_count', 0)}"
    )
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Task Packets")
    lines.append("")
    if packets:
        for p in packets:
            lines.append(
                f"- `{p.get('idea_id', '')}` {p.get('title', '')} "
                f"(status=`{p.get('task_packet_status', '')}`, "
                f"valid=`{p.get('valid', '')}`, "
                f"read_only=`{p.get('read_only', '')}`, "
                f"executes=`{p.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Planner Summary")
    lines.append("")
    lines.append(
        f"- `total_items`: `{planner_summary.get('total_items', 0)}`"
    )
    lines.append(
        "- `ready_for_research_plan_count`: "
        f"`{planner_summary.get('ready_for_research_plan_count', 0)}`"
    )
    lines.append(
        f"- `read_only`: `{planner_summary.get('read_only', '')}`"
    )
    lines.append(
        f"- `executes`: `{planner_summary.get('executes', '')}`"
    )
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this batch and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
