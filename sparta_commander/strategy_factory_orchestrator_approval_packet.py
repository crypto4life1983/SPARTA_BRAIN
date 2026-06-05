"""SPARTA Offline Strategy Factory - ORCHESTRATOR HUMAN APPROVAL PACKET v1.

Bundle 7 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *approval packet compiler*: it consumes Bundle 6's
orchestrator preview and produces deterministic, human-readable APPROVAL
PACKETS describing what a human operator would be asked to sign off on for
each Strategy Factory action. It compiles a packet; it never acts.

Every packet is pinned to ``status="PENDING_HUMAN_APPROVAL"``,
``approved=False``, ``approval_required=True``, ``executes=False`` and
``human_gated=True``. Every approval slot is pinned ``approved=False``,
``executes=False`` and ``human_approval_required=True``. The compiler runs
nothing, computes no backtest, fetches no data, writes no file, opens no
network, spawns no subprocess, touches no broker/exchange/order/trading/
live/upload/autopilot surface, and promotes/deploys nothing. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - APPROVAL_PACKET_SCHEMA_VERSION
  - DEFAULT_APPROVAL_PACKET_LABEL
  - APPROVAL_PACKET_STATUS
  - APPROVAL_PACKET_SAFETY_POSTURE
  - build_orchestrator_approval_packet(action, *, label=None, operator=None)
  - build_all_orchestrator_approval_packets(*, label=None, operator=None)
  - render_orchestrator_approval_packet_markdown(action, *, label=None,
        operator=None)
  - render_all_orchestrator_approval_packets_markdown(*, label=None,
        operator=None)

The action set is derived from Bundle 5's closed PLAN_ACTION enum (no
drift). Bundle 5's FORBIDDEN_CAPABILITIES is preserved unchanged, and the
all-False safety posture is inherited from Bundle 6's SAFETY_POSTURE.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_preview import (
    PREVIEW_SCHEMA_VERSION,
    SAFETY_POSTURE,
    build_orchestrator_preview,
    build_all_orchestrator_previews,
)

__all__ = [
    "APPROVAL_PACKET_SCHEMA_VERSION",
    "DEFAULT_APPROVAL_PACKET_LABEL",
    "APPROVAL_PACKET_STATUS",
    "APPROVAL_PACKET_SAFETY_POSTURE",
    "build_orchestrator_approval_packet",
    "build_all_orchestrator_approval_packets",
    "render_orchestrator_approval_packet_markdown",
    "render_all_orchestrator_approval_packets_markdown",
]

APPROVAL_PACKET_SCHEMA_VERSION = (
    "strategy_factory_orchestrator_approval_packet.v1"
)
DEFAULT_APPROVAL_PACKET_LABEL = (
    "Strategy Factory Orchestrator Human Approval Packet"
)
APPROVAL_PACKET_STATUS = "PENDING_HUMAN_APPROVAL"

# Inherited all-False safety posture (same 13 keys as Bundle 6). Pinned
# False: this compiler only describes what a human would sign off on.
APPROVAL_PACKET_SAFETY_POSTURE: dict[str, bool] = dict(SAFETY_POSTURE)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-False posture (callers cannot taint)."""
    return dict(APPROVAL_PACKET_SAFETY_POSTURE)


def _approval_state() -> dict[str, Any]:
    """Return a fresh, neutral approval-state block.

    Nothing is approved and nothing is recorded; the only forward pointer is
    a request to await the human decision."""
    return {
        "approved": False,
        "decision_recorded": False,
        "approval_reference": "",
        "approval_notes": "",
        "next_gate": "await_human_decision",
    }


def _approval_slots(action: str) -> tuple[dict[str, Any], ...]:
    """Build a fresh, deterministic tuple of neutral approval slots.

    Each slot only asks a human to inspect / confirm / await. No slot
    carries an execution or promotion verb; each is pinned ``approved=False``
    and ``executes=False`` with a mandatory human approval gate."""
    return (
        {
            "slot_id": "01",
            "name": "review_preview",
            "human_approval_required": True,
            "approved": False,
            "executes": False,
            "description": (
                f"Review the orchestrator preview compiled for the {action} "
                "action."
            ),
        },
        {
            "slot_id": "02",
            "name": "confirm_safety_posture",
            "human_approval_required": True,
            "approved": False,
            "executes": False,
            "description": (
                "Confirm the all-false safety posture before any human "
                "decision is recorded."
            ),
        },
        {
            "slot_id": "03",
            "name": "await_human_decision",
            "human_approval_required": True,
            "approved": False,
            "executes": False,
            "description": (
                "Await the human decision and record the pending approval "
                "gate."
            ),
        },
    )


def build_orchestrator_approval_packet(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh approval packet for one action. Pure; no I/O, no
    mutation, no timestamp, no random id.

    Unknown actions never raise: they still produce a fully gated packet
    (``approved=False``, ``approval_required=True``, ``executes=False``,
    ``human_gated=True``, every slot gated)."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_APPROVAL_PACKET_LABEL
    )
    who = operator if isinstance(operator, str) and operator else ""
    act = action if isinstance(action, str) else ""
    known = act in PLAN_ACTION
    preview = build_orchestrator_preview(act)
    return {
        "schema_version": APPROVAL_PACKET_SCHEMA_VERSION,
        "label": name,
        "status": APPROVAL_PACKET_STATUS,
        "action": act,
        "known_action": known,
        "operator": who,
        "approval_required": True,
        "approved": False,
        "executes": False,
        "human_gated": True,
        "preview_schema_version": PREVIEW_SCHEMA_VERSION,
        "preview": preview,
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "approval_state": _approval_state(),
        "approval_slots": _approval_slots(act if known else "UNKNOWN"),
    }


def build_all_orchestrator_approval_packets(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return approval packets for every action in Bundle 5's PLAN_ACTION.

    Pure. The action set is derived from Bundle 5 (not hardcoded), so it can
    never drift from the contract."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_APPROVAL_PACKET_LABEL
    )
    who = operator if isinstance(operator, str) and operator else ""
    # Touch Bundle 6's aggregate builder so the derived action set is shared.
    source_previews = build_all_orchestrator_previews()
    return {
        "schema_version": APPROVAL_PACKET_SCHEMA_VERSION,
        "label": name,
        "status": APPROVAL_PACKET_STATUS,
        "operator": who,
        "approval_required": True,
        "approved": False,
        "executes": False,
        "human_gated": True,
        "preview_schema_version": PREVIEW_SCHEMA_VERSION,
        "source_preview_schema": source_previews["schema_version"],
        "actions": list(PLAN_ACTION),
        "packets": {
            action: build_orchestrator_approval_packet(
                action, label=name, operator=who
            )
            for action in PLAN_ACTION
        },
    }


def _preview_summary_lines(packet: dict[str, Any]) -> list[str]:
    """Markdown lines summarizing the embedded Bundle 6 preview."""
    preview = packet["preview"]
    lines: list[str] = []
    lines.append(f"- preview_schema: `{packet['preview_schema_version']}`")
    lines.append(f"- preview_label: {preview['label']}")
    lines.append(f"- preview_known_action: {preview['known_action']}")
    lines.append("- preview_executes: False")
    lines.append("- preview_human_gated: True")
    lines.append(f"- preview_steps: {len(preview['preview_steps'])}")
    return lines


def _approval_state_lines(state: dict[str, Any]) -> list[str]:
    """Markdown lines for the neutral approval-state block."""
    ref = state.get("approval_reference", "") or "(none)"
    notes = state.get("approval_notes", "") or "(none)"
    return [
        f"- approved: `{state.get('approved', False)}`",
        f"- decision_recorded: `{state.get('decision_recorded', False)}`",
        f"- approval_reference: {ref}",
        f"- approval_notes: {notes}",
        f"- next_gate: {state.get('next_gate', 'await_human_decision')}",
    ]


def _packet_markdown_block(packet: dict[str, Any]) -> list[str]:
    """The markdown lines for a single approval packet dict."""
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Human Approval Packet")
    lines.append("")
    lines.append(f"Schema: `{packet['schema_version']}`")
    lines.append(f"Preview schema: `{packet['preview_schema_version']}`")
    lines.append(f"Label: {packet['label']}")
    lines.append(f"Status: {packet['status']}")
    lines.append(f"Action: {packet['action']}")
    lines.append(f"Known action: {packet['known_action']}")
    lines.append(f"Operator: {packet['operator'] or '(unassigned)'}")
    lines.append("Approval required: True")
    lines.append("Approved: False")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Preview Summary")
    lines.append("")
    lines.extend(_preview_summary_lines(packet))
    lines.append("")
    lines.append("## Approval State")
    lines.append("")
    lines.extend(_approval_state_lines(packet["approval_state"]))
    lines.append("")
    lines.append("## Approval Slots")
    lines.append("")
    for slot in packet["approval_slots"]:
        lines.append(
            f"- {slot['slot_id']} {slot['name']} "
            f"(human_approval_required=`{slot['human_approval_required']}`, "
            f"approved=`{slot['approved']}`, "
            f"executes=`{slot['executes']}`): {slot['description']}"
        )
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    for key, value in packet["safety"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Forbidden Capabilities")
    lines.append("")
    for cap in packet["forbidden_capabilities"]:
        lines.append(f"- `{cap}`")
    return lines


def render_orchestrator_approval_packet_markdown(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for one action. Pure; writes
    no file."""
    packet = build_orchestrator_approval_packet(
        action, label=label, operator=operator
    )
    return "\n".join(_packet_markdown_block(packet))


def render_all_orchestrator_approval_packets_markdown(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for every action. Pure;
    writes no file."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_APPROVAL_PACKET_LABEL
    )
    who = operator if isinstance(operator, str) and operator else ""
    blocks: list[str] = []
    blocks.append(f"# {name} (all actions)")
    blocks.append("")
    blocks.append(f"Schema: `{APPROVAL_PACKET_SCHEMA_VERSION}`")
    blocks.append(f"Status: {APPROVAL_PACKET_STATUS}")
    blocks.append("Approval required: True")
    blocks.append("Approved: False")
    blocks.append("Executes: False")
    blocks.append("Human gated: True")
    blocks.append("")
    for action in PLAN_ACTION:
        packet = build_orchestrator_approval_packet(
            action, label=name, operator=who
        )
        blocks.extend(_packet_markdown_block(packet))
        blocks.append("")
    return "\n".join(blocks)
