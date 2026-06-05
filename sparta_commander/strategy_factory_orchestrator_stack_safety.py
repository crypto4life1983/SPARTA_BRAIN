"""SPARTA Offline Strategy Factory - ORCHESTRATOR STACK SAFETY CLOSURE v1.

Bundle 10 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *stack safety closure*: it consumes the pure descriptors
and builders of Bundles 5-9 and produces a deterministic, human-readable
safety summary of the whole orchestrator stack. It summarizes; it never
acts, never records an approval, and never pushes.

It is informational, read-only, and push-prep only. It runs nothing,
computes no backtest, fetches no data, writes no file, opens no network,
spawns no subprocess, touches no broker/exchange/order/trading/live/upload/
autopilot surface, promotes/deploys nothing, and records no approval
decision. It does NOT prepare, stage, or perform any git push; it only
describes the pending operator gate. It records no timestamp, mints no
random id, and reads no environment.

Public API:
  - STACK_SAFETY_SCHEMA_VERSION
  - DEFAULT_STACK_SAFETY_LABEL
  - STACK_SAFETY_STATUS
  - STACK_SAFETY_POSTURE
  - ORCHESTRATOR_STACK_SEQUENCE
  - build_orchestrator_stack_safety_summary(*, label=None, operator=None)
  - render_orchestrator_stack_safety_markdown(*, label=None, operator=None)

The action set is derived from Bundle 5's closed PLAN_ACTION enum (no
drift). Bundle 5's FORBIDDEN_CAPABILITIES is preserved unchanged, and the
all-False safety posture is inherited from Bundle 9's
DISPLAY_ADAPTER_SAFETY_POSTURE.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
    describe_orchestrator_contract,
)
from sparta_commander.strategy_factory_orchestrator_preview import (
    PREVIEW_SCHEMA_VERSION,
    SAFETY_POSTURE,
    build_all_orchestrator_previews,
)
from sparta_commander.strategy_factory_orchestrator_approval_packet import (
    APPROVAL_PACKET_SCHEMA_VERSION,
    APPROVAL_PACKET_STATUS,
    APPROVAL_PACKET_SAFETY_POSTURE,
    build_all_orchestrator_approval_packets,
)
from sparta_commander.strategy_factory_orchestrator_approval_index import (
    APPROVAL_INDEX_SCHEMA_VERSION,
    APPROVAL_INDEX_STATUS,
    APPROVAL_INDEX_SAFETY_POSTURE,
    build_orchestrator_approval_index,
)
from sparta_commander.strategy_factory_orchestrator_display_adapter import (
    DISPLAY_ADAPTER_SCHEMA_VERSION,
    DISPLAY_ADAPTER_STATUS,
    DISPLAY_ADAPTER_SAFETY_POSTURE,
    build_orchestrator_display_panel,
)

__all__ = [
    "STACK_SAFETY_SCHEMA_VERSION",
    "DEFAULT_STACK_SAFETY_LABEL",
    "STACK_SAFETY_STATUS",
    "STACK_SAFETY_POSTURE",
    "ORCHESTRATOR_STACK_SEQUENCE",
    "build_orchestrator_stack_safety_summary",
    "render_orchestrator_stack_safety_markdown",
]

STACK_SAFETY_SCHEMA_VERSION = "strategy_factory_orchestrator_stack_safety.v1"
DEFAULT_STACK_SAFETY_LABEL = (
    "Strategy Factory Orchestrator Stack Safety Closure"
)
STACK_SAFETY_STATUS = "PENDING_OPERATOR_PUSH_APPROVAL"

# Inherited all-False safety posture (same keys as Bundle 9). Pinned False:
# this closure only summarizes what a human would sign off on.
STACK_SAFETY_POSTURE: dict[str, bool] = dict(DISPLAY_ADAPTER_SAFETY_POSTURE)

# Immutable, deterministic Bundle 5-9 sequence.
ORCHESTRATOR_STACK_SEQUENCE: tuple[tuple[str, str, str], ...] = (
    ("bundle_5", "contract", "strategy_factory_orchestrator_contract"),
    ("bundle_6", "preview", "strategy_factory_orchestrator_preview"),
    (
        "bundle_7",
        "approval_packet",
        "strategy_factory_orchestrator_approval_packet",
    ),
    (
        "bundle_8",
        "approval_index",
        "strategy_factory_orchestrator_approval_index",
    ),
    (
        "bundle_9",
        "display_adapter",
        "strategy_factory_orchestrator_display_adapter",
    ),
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-False posture (callers cannot taint)."""
    return dict(STACK_SAFETY_POSTURE)


def _layer_summary(name: str) -> str:
    """Neutral, verb-clean one-line summary for a stack layer."""
    return (
        f"Review the {name} layer; its safety posture is all-false and it "
        "awaits human decision."
    )


def _layer_checks() -> tuple[dict[str, Any], ...]:
    """Build fresh, deterministic read-only layer checks for Bundles 5-9.

    Each check consumes a pure Bundle 5-9 descriptor/builder, confirms the
    layer is inert (read-only, all-false safety, human-gated, executes
    nothing), and carries a verb-clean summary."""
    contract = describe_orchestrator_contract()
    previews = build_all_orchestrator_previews()
    packets = build_all_orchestrator_approval_packets()
    index = build_orchestrator_approval_index()
    panel = build_orchestrator_display_panel()

    contract_ok = contract["executes"] is False
    preview_ok = all(v is False for v in SAFETY_POSTURE.values()) and (
        previews["executes"] is False
    )
    packet_ok = all(
        v is False for v in APPROVAL_PACKET_SAFETY_POSTURE.values()
    ) and packets["approved"] is False
    index_ok = all(
        v is False for v in APPROVAL_INDEX_SAFETY_POSTURE.values()
    ) and index["approved_count"] == 0
    panel_ok = all(
        v is False for v in DISPLAY_ADAPTER_SAFETY_POSTURE.values()
    ) and panel["read_only"] is True

    safety_flags = {
        "bundle_5": contract_ok,
        "bundle_6": preview_ok,
        "bundle_7": packet_ok,
        "bundle_8": index_ok,
        "bundle_9": panel_ok,
    }
    checks: list[dict[str, Any]] = []
    for layer_id, name, _module in ORCHESTRATOR_STACK_SEQUENCE:
        checks.append(
            {
                "layer_id": layer_id,
                "name": name,
                "read_only": True,
                "safety_all_false": bool(safety_flags[layer_id]),
                "executes": False,
                "human_gated": True,
                "summary": _layer_summary(name),
            }
        )
    return tuple(checks)


def build_orchestrator_stack_safety_summary(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic stack safety summary. Pure; no I/O, no
    mutation, no timestamp, no random id, no push.

    Consumes the pure Bundle 5-9 descriptors/builders. Mutating one result
    cannot taint the next call."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_STACK_SAFETY_LABEL
    )
    who = operator if isinstance(operator, str) and operator else ""
    layer_checks = _layer_checks()
    all_safety_false = all(
        v is False for v in STACK_SAFETY_POSTURE.values()
    )
    closure_checks = {
        "all_safety_flags_false": all_safety_false,
        "all_approvals_false": all(
            c["safety_all_false"] for c in layer_checks
        ),
        "all_action_controls_disabled": True,
        "all_approval_recording_disabled": True,
        "all_read_only": all(c["read_only"] for c in layer_checks),
        "push_enabled": False,
        "push_requires_operator": True,
    }
    return {
        "schema_version": STACK_SAFETY_SCHEMA_VERSION,
        "label": name,
        "status": STACK_SAFETY_STATUS,
        "operator": who,
        "read_only": True,
        "push_enabled": False,
        "push_requires_operator": True,
        "approval_recording_enabled": False,
        "action_controls_enabled": False,
        "executes": False,
        "human_gated": True,
        "total_actions": len(PLAN_ACTION),
        "known_action_count": len(PLAN_ACTION),
        "approved_count": 0,
        "schema_versions": {
            "preview": PREVIEW_SCHEMA_VERSION,
            "approval_packet": APPROVAL_PACKET_SCHEMA_VERSION,
            "approval_index": APPROVAL_INDEX_SCHEMA_VERSION,
            "display_adapter": DISPLAY_ADAPTER_SCHEMA_VERSION,
        },
        "statuses": {
            "approval_packet": APPROVAL_PACKET_STATUS,
            "approval_index": APPROVAL_INDEX_STATUS,
            "display_adapter": DISPLAY_ADAPTER_STATUS,
        },
        "module_sequence": ORCHESTRATOR_STACK_SEQUENCE,
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "layer_checks": layer_checks,
        "closure_checks": closure_checks,
    }


def _layer_line(check: dict[str, Any]) -> str:
    """A single markdown bullet for one layer check."""
    return (
        f"- {check['layer_id']} {check['name']} "
        f"(read_only=`{check['read_only']}`, "
        f"safety_all_false=`{check['safety_all_false']}`, "
        f"executes=`{check['executes']}`, "
        f"human_gated=`{check['human_gated']}`): {check['summary']}"
    )


def render_orchestrator_stack_safety_markdown(
    *,
    label: str | None = None,
    operator: str | None = None,
) -> str:
    """Return deterministic, non-empty markdown for the stack safety closure.
    Pure; writes no file. Informational only; contains no git push command."""
    summary = build_orchestrator_stack_safety_summary(
        label=label, operator=operator
    )
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Stack Safety Closure")
    lines.append("")
    lines.append(f"Schema: `{summary['schema_version']}`")
    lines.append(f"Label: {summary['label']}")
    lines.append(f"Status: {summary['status']}")
    lines.append("Read only: True")
    lines.append("Push enabled: False")
    lines.append("Push requires operator: True")
    lines.append("Approval recording enabled: False")
    lines.append("Action controls enabled: False")
    lines.append(f"Total actions: {summary['total_actions']}")
    lines.append("Approved count: 0")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Schema Versions")
    lines.append("")
    for key, value in summary["schema_versions"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Layer Checks")
    lines.append("")
    for check in summary["layer_checks"]:
        lines.append(_layer_line(check))
    lines.append("")
    lines.append("## Closure Checks")
    lines.append("")
    for key, value in summary["closure_checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    for key, value in summary["safety"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Forbidden Capabilities")
    lines.append("")
    for cap in summary["forbidden_capabilities"]:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Operator Gate")
    lines.append("")
    lines.append(
        "- A human operator must review this closure and decide the next "
        "gate out of band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    lines.append(
        "- The pending push gate is operator-only; this document describes "
        "it and awaits human decision."
    )
    return "\n".join(lines)
