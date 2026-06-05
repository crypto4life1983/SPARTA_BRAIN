"""SPARTA Offline Strategy Factory - QUEUE PLANNER v1.

Bundle 13 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only planner*: it consumes Bundle 12 queue reader
entries/summaries and produces deterministic, read-only PLANNING decisions
for research queue items. A "decision" is a planning state only -- it never
grants execution permission and forces every authorization field to False.

It is informational, read-only, and planning-only. It runs nothing, computes
no backtest, fetches no data, writes no file, opens no network, spawns no
subprocess, touches no broker/exchange/order/trading/live/upload/autopilot
surface, promotes/deploys nothing, and records no approval decision. It
records no timestamp, mints no random id, and reads no environment.

Public API:
  - QUEUE_PLANNER_SCHEMA_VERSION
  - DEFAULT_QUEUE_PLANNER_LABEL
  - QUEUE_PLANNER_STATUS
  - QUEUE_PLANNER_SAFETY_POSTURE
  - PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL
  - PLAN_DECISION_READY_FOR_RESEARCH_PLAN
  - PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
  - build_queue_plan_decision(item, *, human_research_approved=False)
  - build_queue_plan_summary(items, *, label=None, human_research_approved_by_id=None)
  - render_queue_plan_decision_markdown(decision)
  - render_queue_plan_summary_markdown(summary)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_STATUS,
    QUEUE_READER_SAFETY_POSTURE,
    build_queue_reader_entry,
    build_queue_reader_summary,
)

__all__ = [
    "QUEUE_PLANNER_SCHEMA_VERSION",
    "DEFAULT_QUEUE_PLANNER_LABEL",
    "QUEUE_PLANNER_STATUS",
    "QUEUE_PLANNER_SAFETY_POSTURE",
    "PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL",
    "PLAN_DECISION_READY_FOR_RESEARCH_PLAN",
    "PLAN_DECISION_INVALID_ITEM_NEEDS_FIX",
    "build_queue_plan_decision",
    "build_queue_plan_summary",
    "render_queue_plan_decision_markdown",
    "render_queue_plan_summary_markdown",
]

QUEUE_PLANNER_SCHEMA_VERSION = "strategy_factory_queue_planner.v1"
DEFAULT_QUEUE_PLANNER_LABEL = "Strategy Factory Queue Planner"
QUEUE_PLANNER_STATUS = "READ_ONLY_PLANNING_REVIEW"

PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL = "WAIT_FOR_HUMAN_APPROVAL"
PLAN_DECISION_READY_FOR_RESEARCH_PLAN = "READY_FOR_RESEARCH_PLAN"
PLAN_DECISION_INVALID_ITEM_NEEDS_FIX = "INVALID_ITEM_NEEDS_FIX"

# Inherited all-false safety posture (same keys as Bundle 12). Pinned False:
# planning never grants a capability.
QUEUE_PLANNER_SAFETY_POSTURE: dict[str, bool] = dict(QUEUE_READER_SAFETY_POSTURE)

# Human-readable, verb-clean reasons per planning decision.
_DECISION_REASONS: dict[str, str] = {
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX: (
        "The item is invalid; a human must repair its required fields before "
        "any planning can continue."
    ),
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL: (
        "The item is well-formed but still awaits a human research-approval "
        "decision before a research plan may be shaped."
    ),
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN: (
        "A human has marked this item research-approved, so it is ready for a "
        "research plan; this remains a planning state with no authorization."
    ),
}

# Next-gate hint per planning decision.
_DECISION_NEXT_GATE: dict[str, str] = {
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX: "human_item_repair",
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL: "human_research_approval",
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN: "human_research_plan_shaping",
}


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(QUEUE_PLANNER_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _decide(valid: bool, human_research_approved: bool) -> str:
    """Pure decision rule. Invalid wins; else approval gates readiness."""
    if not valid:
        return PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
    if human_research_approved:
        return PLAN_DECISION_READY_FOR_RESEARCH_PLAN
    return PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL


def build_queue_plan_decision(
    item: Any,
    *,
    human_research_approved: bool = False,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only planning decision for one item.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise (they resolve to INVALID_ITEM_NEEDS_FIX). Even when
    human_research_approved is True, every authorization field stays False --
    a decision is a planning state, never execution permission. Returned
    dicts are fresh."""
    reader_entry = build_queue_reader_entry(item)
    valid = bool(reader_entry["valid"])
    approved = human_research_approved is True
    decision = _decide(valid, approved)

    return {
        "schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "source_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(reader_entry.get("idea_id")),
        "title": _as_text(reader_entry.get("title")),
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "status": QUEUE_PLANNER_STATUS,
        "decision": decision,
        "decision_reason": _DECISION_REASONS[decision],
        "human_research_approved": approved,
        "valid": valid,
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
        "reader_entry": reader_entry,
        "next_gate": _DECISION_NEXT_GATE[decision],
    }


def build_queue_plan_summary(
    items: tuple[Any, ...],
    *,
    label: str | None = None,
    human_research_approved_by_id: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only planning summary over items.

    Pure; no I/O, no mutation. All authorization counts stay 0; the summary
    is read-only and inert with an all-false safety posture. The
    human_research_approved_by_id map is read-only input only -- no approval
    is recorded anywhere. Consumes Bundle 12 build_queue_reader_summary for
    its read-only reader snapshot."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_QUEUE_PLANNER_LABEL
    )
    approvals = (
        human_research_approved_by_id
        if isinstance(human_research_approved_by_id, dict)
        else {}
    )
    item_tuple = tuple(items)

    decisions: list[dict[str, Any]] = []
    for it in item_tuple:
        idea_id = _as_text(it.get("idea_id")) if isinstance(it, dict) else ""
        approved = approvals.get(idea_id, False) is True
        decisions.append(
            build_queue_plan_decision(it, human_research_approved=approved)
        )
    decision_tuple = tuple(decisions)

    valid_count = sum(1 for d in decision_tuple if d["valid"])
    invalid_count = len(decision_tuple) - valid_count
    wait_count = sum(
        1 for d in decision_tuple
        if d["decision"] == PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL
    )
    ready_count = sum(
        1 for d in decision_tuple
        if d["decision"] == PLAN_DECISION_READY_FOR_RESEARCH_PLAN
    )
    needs_fix_count = sum(
        1 for d in decision_tuple
        if d["decision"] == PLAN_DECISION_INVALID_ITEM_NEEDS_FIX
    )

    reader_summary = build_queue_reader_summary(item_tuple, label=name)

    return {
        "schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "source_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": QUEUE_PLANNER_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "total_items": len(item_tuple),
        "valid_item_count": valid_count,
        "invalid_item_count": invalid_count,
        "wait_for_human_approval_count": wait_count,
        "ready_for_research_plan_count": ready_count,
        "invalid_item_needs_fix_count": needs_fix_count,
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
        "reader_summary": reader_summary,
        "decisions": decision_tuple,
        "next_gate": "operator_review",
    }


def render_queue_plan_decision_markdown(decision: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for one planning decision.
    Pure; writes no file. Informational only."""
    safety = decision.get("safety") or {}
    reader_entry = decision.get("reader_entry") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Queue Plan Decision")
    lines.append("")
    lines.append(f"Schema: `{decision.get('schema_version', '')}`")
    lines.append(
        f"Source schema: `{decision.get('source_schema_version', '')}`"
    )
    lines.append(
        "Research queue schema: "
        f"`{decision.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {decision.get('idea_id', '')}")
    lines.append(f"Title: {decision.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {decision.get('status', '')}")
    lines.append(f"Decision: {decision.get('decision', '')}")
    lines.append(
        f"Human research approved: {decision.get('human_research_approved', '')}"
    )
    lines.append(f"Valid: {decision.get('valid', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Decision Reason")
    lines.append("")
    lines.append(decision.get("decision_reason", "") or "(none)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Reader Entry")
    lines.append("")
    lines.append(f"- `idea_id`: `{reader_entry.get('idea_id', '')}`")
    lines.append(f"- `valid`: `{reader_entry.get('valid', '')}`")
    lines.append(f"- `read_only`: `{reader_entry.get('read_only', '')}`")
    lines.append(f"- `executes`: `{reader_entry.get('executes', '')}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this decision and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_queue_plan_summary_markdown(summary: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for the planning summary.
    Pure; writes no file. Informational only."""
    safety = summary.get("safety") or {}
    decisions = summary.get("decisions") or ()
    reader_summary = summary.get("reader_summary") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Queue Plan Summary")
    lines.append("")
    lines.append(f"Schema: `{summary.get('schema_version', '')}`")
    lines.append(
        f"Source schema: `{summary.get('source_schema_version', '')}`"
    )
    lines.append(
        "Research queue schema: "
        f"`{summary.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Label: {summary.get('label', '')}")
    lines.append(f"Status: {summary.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Total items: {summary.get('total_items', 0)}")
    lines.append(f"Valid item count: {summary.get('valid_item_count', 0)}")
    lines.append(
        f"Invalid item count: {summary.get('invalid_item_count', 0)}"
    )
    lines.append(
        "Wait for human approval count: "
        f"{summary.get('wait_for_human_approval_count', 0)}"
    )
    lines.append(
        "Ready for research plan count: "
        f"{summary.get('ready_for_research_plan_count', 0)}"
    )
    lines.append(
        "Invalid item needs fix count: "
        f"{summary.get('invalid_item_needs_fix_count', 0)}"
    )
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Decisions")
    lines.append("")
    if decisions:
        for d in decisions:
            lines.append(
                f"- `{d.get('idea_id', '')}` {d.get('title', '')} "
                f"(decision=`{d.get('decision', '')}`, "
                f"valid=`{d.get('valid', '')}`, "
                f"read_only=`{d.get('read_only', '')}`, "
                f"executes=`{d.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Reader Summary")
    lines.append("")
    lines.append(
        f"- `total_items`: `{reader_summary.get('total_items', 0)}`"
    )
    lines.append(
        f"- `valid_item_count`: `{reader_summary.get('valid_item_count', 0)}`"
    )
    lines.append(
        f"- `read_only`: `{reader_summary.get('read_only', '')}`"
    )
    lines.append(
        f"- `executes`: `{reader_summary.get('executes', '')}`"
    )
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this summary and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
