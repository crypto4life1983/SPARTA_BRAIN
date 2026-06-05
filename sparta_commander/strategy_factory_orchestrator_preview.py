"""SPARTA Offline Strategy Factory - ORCHESTRATOR PREVIEW COMPILER v1.

Bundle 6 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *preview compiler*: it consumes Bundle 5's dry-run
orchestrator contract and produces deterministic, human-readable PREVIEWS
of what a future (NOT yet built, NOT authorized) orchestrator would be
bound to honour for each Strategy Factory action. It previews; it never
acts.

It is informational only. It never runs Strategy Factory, never computes a
backtest, never fetches data, never writes a file, opens no network, spawns
no subprocess, touches no broker/exchange/order/trading/live/upload/
autopilot surface, and promotes/deploys nothing. Every preview and every
preview step is pinned to ``executes=False`` and ``human_gate_required``.

Public API:
  - DEFAULT_PREVIEW_LABEL
  - PREVIEW_SCHEMA_VERSION
  - SAFETY_POSTURE
  - build_orchestrator_preview(action, *, label=None)
  - build_all_orchestrator_previews(*, label=None)
  - render_orchestrator_preview_markdown(action, *, label=None)
  - render_all_orchestrator_previews_markdown(*, label=None)

The action set is derived from Bundle 5's closed PLAN_ACTION enum (no
drift). Bundle 5's FORBIDDEN_CAPABILITIES is preserved unchanged.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_orchestrator_contract import (
    PLAN_ACTION,
    FORBIDDEN_CAPABILITIES,
    contract_for_action,
    describe_orchestrator_contract,
)

__all__ = [
    "DEFAULT_PREVIEW_LABEL",
    "PREVIEW_SCHEMA_VERSION",
    "SAFETY_POSTURE",
    "build_orchestrator_preview",
    "build_all_orchestrator_previews",
    "render_orchestrator_preview_markdown",
    "render_all_orchestrator_previews_markdown",
]

DEFAULT_PREVIEW_LABEL = "Strategy Factory Orchestrator Preview"
PREVIEW_SCHEMA_VERSION = "strategy_factory_orchestrator_preview.v1"

# Every posture flag is pinned False: this compiler only describes.
SAFETY_POSTURE: dict[str, bool] = {
    "automation_enabled": False,
    "live_execution_enabled": False,
    "file_write_enabled": False,
    "network_enabled": False,
    "subprocess_enabled": False,
    "strategy_promotion_enabled": False,
    "broker_enabled": False,
    "exchange_enabled": False,
    "order_enabled": False,
    "data_fetch_enabled": False,
    "backtest_enabled": False,
    "upload_enabled": False,
    "autopilot_enabled": False,
}


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-False posture (callers cannot taint)."""
    return dict(SAFETY_POSTURE)


def _preview_steps(action: str) -> tuple[dict[str, Any], ...]:
    """Build a fresh, deterministic tuple of neutral preview steps.

    Every step is informational: it inspects / summarizes / awaits a human
    gate. No step carries an execution or promotion verb, and each is
    pinned ``executes=False`` with a mandatory human gate."""
    return (
        {
            "step_id": "01",
            "name": "inspect_contract",
            "human_gate_required": True,
            "executes": False,
            "description": (
                f"Inspect the orchestrator contract for the {action} action."
            ),
        },
        {
            "step_id": "02",
            "name": "summarize_preconditions",
            "human_gate_required": True,
            "executes": False,
            "description": (
                f"Summarize the preconditions recorded for the {action} "
                "action."
            ),
        },
        {
            "step_id": "03",
            "name": "await_human_gate",
            "human_gate_required": True,
            "executes": False,
            "description": (
                "Await human approval and record the intended next gate."
            ),
        },
    )


def build_orchestrator_preview(
    action: str, *, label: str | None = None
) -> dict[str, Any]:
    """Return a fresh preview dict for one action. Pure; no I/O, no mutation.

    Unknown actions never raise: they fall back to Bundle 5's UNKNOWN
    contract and stay fully gated (``executes=False``, ``human_gated=True``,
    every step gated)."""
    name = label if isinstance(label, str) and label else DEFAULT_PREVIEW_LABEL
    act = action if isinstance(action, str) else ""
    known = act in PLAN_ACTION
    return {
        "schema_version": PREVIEW_SCHEMA_VERSION,
        "label": name,
        "action": act,
        "known_action": known,
        "executes": False,
        "human_gated": True,
        "contract": contract_for_action(act),
        "safety": _safety_posture(),
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "preview_steps": _preview_steps(act if known else "UNKNOWN"),
    }


def build_all_orchestrator_previews(
    *, label: str | None = None
) -> dict[str, Any]:
    """Return previews for every action in Bundle 5's PLAN_ACTION. Pure.

    The action set is derived from Bundle 5 (not hardcoded), so it can never
    drift from the contract."""
    name = label if isinstance(label, str) and label else DEFAULT_PREVIEW_LABEL
    return {
        "schema_version": PREVIEW_SCHEMA_VERSION,
        "label": name,
        "executes": False,
        "human_gated": True,
        "source_contract_schema": describe_orchestrator_contract()["schema"],
        "actions": list(PLAN_ACTION),
        "previews": {
            action: build_orchestrator_preview(action, label=name)
            for action in PLAN_ACTION
        },
    }


def _contract_lines(contract: dict[str, Any]) -> list[str]:
    """Markdown lines for the contract prose (intent + preconditions)."""
    lines: list[str] = []
    lines.append(f"- intent: {contract.get('intent', '-')}")
    lines.append(
        "- requires_human_approval: "
        f"`{contract.get('requires_human_approval', True)}`"
    )
    lines.append("- preconditions:")
    pres = contract.get("preconditions", [])
    if isinstance(pres, list) and pres:
        for pre in pres:
            lines.append(f"  - {pre}")
    else:
        lines.append("  - (none)")
    return lines


def _preview_markdown_block(preview: dict[str, Any]) -> list[str]:
    """The markdown lines for a single preview dict."""
    lines: list[str] = []
    lines.append("# Strategy Factory Orchestrator Preview")
    lines.append("")
    lines.append(f"Schema: `{preview['schema_version']}`")
    lines.append(f"Label: {preview['label']}")
    lines.append(f"Action: {preview['action']}")
    lines.append(f"Known action: {preview['known_action']}")
    lines.append("Executes: False")
    lines.append("Human gated: True")
    lines.append("")
    lines.append("## Contract")
    lines.append("")
    lines.extend(_contract_lines(preview["contract"]))
    lines.append("")
    lines.append("## Preview Steps")
    lines.append("")
    for step in preview["preview_steps"]:
        lines.append(
            f"- {step['step_id']} {step['name']} "
            f"(human_gate_required=`{step['human_gate_required']}`, "
            f"executes=`{step['executes']}`): {step['description']}"
        )
    lines.append("")
    lines.append("## Forbidden Capabilities")
    lines.append("")
    for cap in preview["forbidden_capabilities"]:
        lines.append(f"- `{cap}`")
    return lines


def render_orchestrator_preview_markdown(
    action: str, *, label: str | None = None
) -> str:
    """Return deterministic, non-empty markdown for one action. Pure; writes
    no file."""
    preview = build_orchestrator_preview(action, label=label)
    return "\n".join(_preview_markdown_block(preview))


def render_all_orchestrator_previews_markdown(
    *, label: str | None = None
) -> str:
    """Return deterministic, non-empty markdown for every action. Pure;
    writes no file."""
    name = label if isinstance(label, str) and label else DEFAULT_PREVIEW_LABEL
    blocks: list[str] = []
    blocks.append(f"# {name} (all actions)")
    blocks.append("")
    blocks.append(f"Schema: `{PREVIEW_SCHEMA_VERSION}`")
    blocks.append("Executes: False")
    blocks.append("Human gated: True")
    blocks.append("")
    for action in PLAN_ACTION:
        preview = build_orchestrator_preview(action, label=name)
        blocks.extend(_preview_markdown_block(preview))
        blocks.append("")
    return "\n".join(blocks)
