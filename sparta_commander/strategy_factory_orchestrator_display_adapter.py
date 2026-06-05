"""SPARTA Offline Strategy Factory - ORCHESTRATOR READ-ONLY DISPLAY ADAPTER v1.

Bundle 9 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only display adapter*: it consumes Bundle 8's
orchestrator approval index and produces deterministic, Commander/JARVIS-
friendly display panels for every Strategy Factory action. It displays; it
never acts and it never records an approval.

Every panel, row and section is pinned ``read_only=True``,
``approval_recording_enabled=False``, ``action_controls_enabled=False``,
``approved=False``, ``executes=False`` and ``human_gated=True``. The adapter
runs nothing, computes no backtest, fetches no data, writes no file, opens
no network, spawns no subprocess, touches no broker/exchange/order/trading/
live/upload/autopilot surface, promotes/deploys nothing, and records no
approval decision. It records no timestamp, mints no random id, and reads
no environment. It exposes no action button or execution control.

Public API:
  - DISPLAY_ADAPTER_SCHEMA_VERSION
  - DEFAULT_DISPLAY_ADAPTER_LABEL
  - DISPLAY_ADAPTER_STATUS
  - DISPLAY_ADAPTER_SAFETY_POSTURE
  - build_orchestrator_display_panel(*, label=None, operator=None)
  - build_orchestrator_action_display_panel(action, *, label=None,
        operator=None)
  - render_orchestrator_display_markdown(*, label=None, operator=None)
  - render_orchestrator_action_display_markdown(action, *, label=None,
        operator=None)

The action set is derived from Bundle 5's closed PLAN_ACTION enum (no
drift). Bundle 5's FORBIDDEN_CAPABILITIES is preserved unchanged, and the
all-False safety posture is inherited from Bundle 8's
APPROVAL_INDEX_SAFETY_POSTURE.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
)
from sparta_commander.strategy_factory_orchestrator_approval_index import (
    APPROVAL_INDEX_SCHEMA_VERSION,
    APPROVAL_INDEX_STATUS,
    APPROVAL_INDEX_SAFETY_POSTURE,
    build_orchestrator_approval_index,
    entry_for_orchestrator_action,
    packet_for_orchestrator_action,
)

__all__ = [
    "DISPLAY_ADAPTER_SCHEMA_VERSION",
    "DEFAULT_DISPLAY_ADAPTER_LABEL",
    "DISPLAY_ADAPTER_STATUS",
    "DISPLAY_ADAPTER_SAFETY_POSTURE",
    "build_orchestrator_display_panel",
    "build_orchestrator_action_display_panel",
    "render_orchestrator_display_markdown",
    "render_orchestrator_action_display_markdown",
]

DISPLAY_ADAPTER_SCHEMA_VERSION = (
    "strategy_factory_orchestrator_display_adapter.v1"
)
DEFAULT_DISPLAY_ADAPTER_LABEL = (
    "Strategy Factory Orchestrator Read-Only Display"
)
DISPLAY_ADAPTER_STATUS = "READ_ONLY_PENDING_HUMAN_APPROVAL"

# Bundle 7/8 packet schema, surfaced read-only for the per-action panel.
_PACKET_SCHEMA_VERSION = "strategy_factory_orchestrator_approval_packet.v1"

# Inherited all-False safety posture (same keys as Bundle 8). Pinned False:
# this adapter only displays what a human would sign off on.
DISPLAY_ADAPTER_SAFETY_POSTURE: dict[str, bool] = dict(
    APPROVAL_INDEX_SAFETY_POSTURE
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-False posture (callers cannot taint)."""
    return dict(DISPLAY_ADAPTER_SAFETY_POSTURE)


def _resolve_name(label: str | None) -> str:
    return (
        label if isinstance(label, str) and label
        else DEFAULT_DISPLAY_ADAPTER_LABEL
    )


def _resolve_operator(operator: str | None) -> str:
    return operator if isinstance(operator, str) and operator else ""


def _display_row(entry: dict[str, Any]) -> dict[str, Any]:
    """Build a fresh read-only display row from a Bundle 8 index entry."""
    return {
        "row_id": entry["entry_id"],
        "action": entry["action"],
        "known_action": entry["known_action"],
        "status": entry["status"],
        "approval_required": True,
        "approved": False,
        "read_only": True,
        "executes": False,
        "human_gated": True,
        "summary": entry["summary"],
    }


def _display_sections(action: str) -> tuple[dict[str, Any], ...]:
    """Build a fresh, deterministic tuple of neutral read-only sections.

    Each section only displays / reviews / awaits. No section carries an
    execution or promotion verb; each is pinned ``read_only=True`` and
    ``executes=False``."""
    return (
        {
            "section_id": "01",
            "name": "entry_overview",
            "read_only": True,
            "executes": False,
            "description": (
                f"Display the approval index entry for the {action} action."
            ),
        },
        {
            "section_id": "02",
            "name": "packet_summary",
            "read_only": True,
            "executes": False,
            "description": (
                f"Summarize the human approval packet for the {action} "
                "action."
            ),
        },
        {
            "section_id": "03",
            "name": "safety_posture",
            "read_only": True,
            "executes": False,
            "description": (
                "Display the all-false safety posture and await the human "
                "decision."
            ),
        },
    )


def build_orchestrator_display_panel(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic display panel for every PLAN_ACTION.

    Pure. The action set is derived from Bundle 5 (not hardcoded), so it can
    never drift from the contract. Mutating one result cannot taint the
    next call."""
    name = _resolve_name(label)
    who = _resolve_operator(operator)
    index = build_orchestrator_approval_index(label=name, operator=who)
    rows = tuple(_display_row(entry) for entry in index["entries"])
    return {
        "schema_version": DISPLAY_ADAPTER_SCHEMA_VERSION,
        "label": name,
        "status": DISPLAY_ADAPTER_STATUS,
        "index_schema_version": APPROVAL_INDEX_SCHEMA_VERSION,
        "index_status": APPROVAL_INDEX_STATUS,
        "operator": who,
        "read_only": True,
        "approval_recording_enabled": False,
        "action_controls_enabled": False,
        "executes": False,
        "human_gated": True,
        "total_actions": index["total_actions"],
        "known_action_count": index["known_action_count"],
        "approval_required_count": index["approval_required_count"],
        "approved_count": 0,
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "display_rows": rows,
    }


def build_orchestrator_action_display_panel(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic display panel for one action. Pure.

    Unknown actions never raise; they still produce a fully gated read-only
    panel with ``known_action=False``."""
    name = _resolve_name(label)
    who = _resolve_operator(operator)
    entry = entry_for_orchestrator_action(action, label=name, operator=who)
    packet = packet_for_orchestrator_action(action, label=name, operator=who)
    act = entry["action"]
    known = entry["known_action"]
    return {
        "schema_version": DISPLAY_ADAPTER_SCHEMA_VERSION,
        "label": name,
        "status": DISPLAY_ADAPTER_STATUS,
        "index_schema_version": APPROVAL_INDEX_SCHEMA_VERSION,
        "packet_schema_version": _PACKET_SCHEMA_VERSION,
        "operator": who,
        "action": act,
        "known_action": known,
        "read_only": True,
        "approval_recording_enabled": False,
        "action_controls_enabled": False,
        "approval_required": True,
        "approved": False,
        "executes": False,
        "human_gated": True,
        "entry": entry,
        "packet": packet,
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "display_sections": _display_sections(act if known else "UNKNOWN"),
    }


def _row_line(row: dict[str, Any]) -> str:
    """A single markdown bullet for one display row."""
    return (
        f"- {row['row_id']} ({row['action']}) "
        f"known_action=`{row['known_action']}` "
        f"approval_required=`{row['approval_required']}` "
        f"approved=`{row['approved']}` "
        f"read_only=`{row['read_only']}` "
        f"executes=`{row['executes']}`: {row['summary']}"
    )


def _section_line(section: dict[str, Any]) -> str:
    """A single markdown bullet for one display section."""
    return (
        f"- {section['section_id']} {section['name']} "
        f"(read_only=`{section['read_only']}`, "
        f"executes=`{section['executes']}`): {section['description']}"
    )


def _safety_lines(safety: dict[str, bool]) -> list[str]:
    """Markdown bullets for the inherited safety posture (key/value data)."""
    return [f"- `{key}`: `{value}`" for key, value in safety.items()]


def _forbidden_lines(caps: tuple[str, ...]) -> list[str]:
    """Markdown bullets for the inherited forbidden-capability data."""
    return [f"- `{cap}`" for cap in caps]


def render_orchestrator_display_markdown(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for the whole display panel.
    Pure; writes no file."""
    panel = build_orchestrator_display_panel(label=label, operator=operator)
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Read-Only Display")
    lines.append("")
    lines.append(f"Schema: `{panel['schema_version']}`")
    lines.append(f"Index schema: `{panel['index_schema_version']}`")
    lines.append(f"Label: {panel['label']}")
    lines.append(f"Status: {panel['status']}")
    lines.append("Read only: True")
    lines.append("Approval recording enabled: False")
    lines.append("Action controls enabled: False")
    lines.append(f"Total actions: {panel['total_actions']}")
    lines.append(
        f"Approval required count: {panel['approval_required_count']}"
    )
    lines.append("Approved count: 0")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Display Rows")
    lines.append("")
    for row in panel["display_rows"]:
        lines.append(_row_line(row))
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    lines.extend(_safety_lines(panel["safety"]))
    lines.append("")
    lines.append("## Forbidden Capabilities")
    lines.append("")
    lines.extend(_forbidden_lines(panel["forbidden_capabilities"]))
    return "\n".join(lines)


def render_orchestrator_action_display_markdown(
    action: str,
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for one action display panel.
    Pure; writes no file. Unknown actions never raise."""
    panel = build_orchestrator_action_display_panel(
        action, label=label, operator=operator
    )
    entry = panel["entry"]
    packet = panel["packet"]
    preview = packet["preview"]
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Action Display")
    lines.append("")
    lines.append(f"Schema: `{panel['schema_version']}`")
    lines.append(f"Index schema: `{panel['index_schema_version']}`")
    lines.append(f"Packet schema: `{panel['packet_schema_version']}`")
    lines.append(f"Action: {panel['action']}")
    lines.append(f"Known action: {panel['known_action']}")
    lines.append(f"Status: {panel['status']}")
    lines.append("Read only: True")
    lines.append("Approval recording enabled: False")
    lines.append("Action controls enabled: False")
    lines.append("Approval required: True")
    lines.append("Approved: False")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Entry")
    lines.append("")
    lines.append(_row_line(_display_row(entry)))
    lines.append("")
    lines.append("## Packet Summary")
    lines.append("")
    lines.append(f"- packet_status: {packet['status']}")
    lines.append(f"- packet_approved: `{packet['approved']}`")
    lines.append(f"- packet_human_gated: `{packet['human_gated']}`")
    lines.append(f"- preview_label: {preview['label']}")
    lines.append(f"- approval_slots: {len(packet['approval_slots'])}")
    lines.append("")
    lines.append("## Display Sections")
    lines.append("")
    for section in panel["display_sections"]:
        lines.append(_section_line(section))
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    lines.extend(_safety_lines(panel["safety"]))
    return "\n".join(lines)
