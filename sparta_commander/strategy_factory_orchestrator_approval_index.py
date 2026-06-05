"""SPARTA Offline Strategy Factory - ORCHESTRATOR APPROVAL INDEX v1.

Bundle 8 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *approval index/registry*: it consumes Bundle 7's
orchestrator human approval packets and produces a deterministic,
searchable, human-readable index of every Strategy Factory action a human
operator would be asked to sign off on. It indexes; it never acts.

Every index, entry and embedded packet is pinned to
``status="PENDING_HUMAN_APPROVAL"``, ``approved=False``,
``approval_required=True``, ``executes=False`` and ``human_gated=True``. The
index runs nothing, computes no backtest, fetches no data, writes no file,
opens no network, spawns no subprocess, touches no broker/exchange/order/
trading/live/upload/autopilot surface, and promotes/deploys nothing. It
records no timestamp, mints no random id, and reads no environment.

Public API:
  - APPROVAL_INDEX_SCHEMA_VERSION
  - DEFAULT_APPROVAL_INDEX_LABEL
  - APPROVAL_INDEX_STATUS
  - APPROVAL_INDEX_SAFETY_POSTURE
  - build_orchestrator_approval_index(*, label=None, operator=None)
  - list_orchestrator_approval_actions()
  - entry_for_orchestrator_action(action, *, label=None, operator=None)
  - packet_for_orchestrator_action(action, *, label=None, operator=None)
  - render_orchestrator_approval_index_markdown(*, label=None, operator=None)
  - render_orchestrator_approval_action_markdown(action, *, label=None,
        operator=None)

The action set is derived from Bundle 5's closed PLAN_ACTION enum (no
drift). Bundle 5's FORBIDDEN_CAPABILITIES is preserved unchanged, and the
all-False safety posture is inherited from Bundle 7's
APPROVAL_PACKET_SAFETY_POSTURE.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_approval_packet import (
    APPROVAL_PACKET_SCHEMA_VERSION,
    APPROVAL_PACKET_STATUS,
    APPROVAL_PACKET_SAFETY_POSTURE,
    build_orchestrator_approval_packet,
    build_all_orchestrator_approval_packets,
)

__all__ = [
    "APPROVAL_INDEX_SCHEMA_VERSION",
    "DEFAULT_APPROVAL_INDEX_LABEL",
    "APPROVAL_INDEX_STATUS",
    "APPROVAL_INDEX_SAFETY_POSTURE",
    "build_orchestrator_approval_index",
    "list_orchestrator_approval_actions",
    "entry_for_orchestrator_action",
    "packet_for_orchestrator_action",
    "render_orchestrator_approval_index_markdown",
    "render_orchestrator_approval_action_markdown",
]

APPROVAL_INDEX_SCHEMA_VERSION = (
    "strategy_factory_orchestrator_approval_index.v1"
)
DEFAULT_APPROVAL_INDEX_LABEL = "Strategy Factory Orchestrator Approval Index"
APPROVAL_INDEX_STATUS = "PENDING_HUMAN_APPROVAL"

# Inherited all-False safety posture (same keys as Bundle 7). Pinned False:
# this index only describes what a human would sign off on.
APPROVAL_INDEX_SAFETY_POSTURE: dict[str, bool] = dict(
    APPROVAL_PACKET_SAFETY_POSTURE
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-False posture (callers cannot taint)."""
    return dict(APPROVAL_INDEX_SAFETY_POSTURE)


def list_orchestrator_approval_actions() -> tuple[str, ...]:
    """Return the closed action set, derived from Bundle 5's PLAN_ACTION."""
    return tuple(PLAN_ACTION)


def packet_for_orchestrator_action(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh Bundle 7 approval packet for one action. Pure.

    Unknown actions never raise; they still yield a fully gated packet with
    ``known_action=False``."""
    return build_orchestrator_approval_packet(
        action, label=label, operator=operator
    )


def entry_for_orchestrator_action(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic index entry for one action. Pure; no I/O,
    no mutation, no timestamp, no random id.

    Unknown actions never raise; they yield an ``entry_id="UNKNOWN"`` entry
    that stays fully gated."""
    packet = packet_for_orchestrator_action(
        action, label=label, operator=operator
    )
    act = packet["action"]
    known = packet["known_action"]
    entry_id = act if known else "UNKNOWN"
    summary = (
        f"Review the human approval packet compiled for the {act} action; "
        "await human decision."
        if known
        else "Review the human approval packet for an unrecognized action; "
        "await human decision."
    )
    return {
        "entry_id": entry_id,
        "action": act,
        "known_action": known,
        "status": APPROVAL_INDEX_STATUS,
        "approval_required": True,
        "approved": False,
        "executes": False,
        "human_gated": True,
        "packet_schema_version": APPROVAL_PACKET_SCHEMA_VERSION,
        "summary": summary,
    }


def build_orchestrator_approval_index(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic approval index for every PLAN_ACTION.

    Pure. The action set is derived from Bundle 5 (not hardcoded), so it can
    never drift from the contract. Mutating one result cannot taint the
    next call."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_APPROVAL_INDEX_LABEL
    )
    who = operator if isinstance(operator, str) and operator else ""
    actions = tuple(PLAN_ACTION)
    # Touch Bundle 7's aggregate builder so the derived set is shared.
    source = build_all_orchestrator_approval_packets(operator=who)
    packets_by_action = {
        action: packet_for_orchestrator_action(
            action, label=name, operator=who
        )
        for action in actions
    }
    entries = tuple(
        entry_for_orchestrator_action(action, label=name, operator=who)
        for action in actions
    )
    return {
        "schema_version": APPROVAL_INDEX_SCHEMA_VERSION,
        "label": name,
        "status": APPROVAL_INDEX_STATUS,
        "operator": who,
        "packet_schema_version": APPROVAL_PACKET_SCHEMA_VERSION,
        "source_packet_status": source["status"],
        "actions": actions,
        "total_actions": len(actions),
        "known_action_count": len(actions),
        "approval_required_count": len(actions),
        "approved_count": 0,
        "executes": False,
        "human_gated": True,
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "entries": entries,
        "packets_by_action": packets_by_action,
    }


def _entry_line(entry: dict[str, Any]) -> str:
    """A single markdown bullet for one index entry."""
    return (
        f"- {entry['entry_id']} ({entry['action']}) "
        f"known_action=`{entry['known_action']}` "
        f"approval_required=`{entry['approval_required']}` "
        f"approved=`{entry['approved']}` "
        f"executes=`{entry['executes']}`: {entry['summary']}"
    )


def _safety_lines(safety: dict[str, bool]) -> list[str]:
    """Markdown bullets for the inherited safety posture (key/value data)."""
    return [f"- `{key}`: `{value}`" for key, value in safety.items()]


def _forbidden_lines(caps: tuple[str, ...]) -> list[str]:
    """Markdown bullets for the inherited forbidden-capability data."""
    return [f"- `{cap}`" for cap in caps]


def render_orchestrator_approval_index_markdown(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for the whole index. Pure;
    writes no file."""
    index = build_orchestrator_approval_index(label=label, operator=operator)
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Approval Index")
    lines.append("")
    lines.append(f"Schema: `{index['schema_version']}`")
    lines.append(f"Packet schema: `{index['packet_schema_version']}`")
    lines.append(f"Label: {index['label']}")
    lines.append(f"Status: {index['status']}")
    lines.append(f"Total actions: {index['total_actions']}")
    lines.append(f"Known action count: {index['known_action_count']}")
    lines.append(
        f"Approval required count: {index['approval_required_count']}"
    )
    lines.append("Approved count: 0")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Entries")
    lines.append("")
    for entry in index["entries"]:
        lines.append(_entry_line(entry))
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    lines.extend(_safety_lines(index["safety"]))
    lines.append("")
    lines.append("## Forbidden Capabilities")
    lines.append("")
    lines.extend(_forbidden_lines(index["forbidden_capabilities"]))
    return "\n".join(lines)


def render_orchestrator_approval_action_markdown(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for one action. Pure; writes
    no file. Unknown actions never raise."""
    entry = entry_for_orchestrator_action(
        action, label=label, operator=operator
    )
    packet = packet_for_orchestrator_action(
        action, label=label, operator=operator
    )
    preview = packet["preview"]
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Approval Action")
    lines.append("")
    lines.append(f"Schema: `{APPROVAL_INDEX_SCHEMA_VERSION}`")
    lines.append(f"Packet schema: `{APPROVAL_PACKET_SCHEMA_VERSION}`")
    lines.append(f"Action: {entry['action']}")
    lines.append(f"Known action: {entry['known_action']}")
    lines.append(f"Status: {entry['status']}")
    lines.append("Approval required: True")
    lines.append("Approved: False")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Entry")
    lines.append("")
    lines.append(_entry_line(entry))
    lines.append("")
    lines.append("## Packet Summary")
    lines.append("")
    lines.append(f"- packet_status: {packet['status']}")
    lines.append(f"- packet_approved: `{packet['approved']}`")
    lines.append(f"- packet_human_gated: `{packet['human_gated']}`")
    lines.append(f"- preview_label: {preview['label']}")
    lines.append(f"- approval_slots: {len(packet['approval_slots'])}")
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    lines.extend(_safety_lines(packet["safety"]))
    return "\n".join(lines)
