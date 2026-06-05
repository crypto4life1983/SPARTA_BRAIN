"""SPARTA Offline Strategy Factory - QUEUE READER v1.

Bundle 12 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only queue reader*: it consumes Bundle 11 research
queue items and produces deterministic, read-only review summaries for the
orchestrator. It forces every authorization field to False and marks unsafe
source items invalid; it grants no capability.

It is informational and read-only. It runs nothing, computes no backtest,
fetches no data, writes no file, opens no network, spawns no subprocess,
touches no broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - QUEUE_READER_SCHEMA_VERSION
  - DEFAULT_QUEUE_READER_LABEL
  - QUEUE_READER_STATUS
  - QUEUE_READER_SAFETY_POSTURE
  - build_queue_reader_entry(item)
  - build_queue_reader_summary(items, *, label=None)
  - render_queue_reader_entry_markdown(entry)
  - render_queue_reader_summary_markdown(summary)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_STATUS,
    RESEARCH_QUEUE_SAFETY_POSTURE,
    DEFAULT_RESEARCH_STAGE,
    DEFAULT_RESEARCH_MODE,
    build_research_queue,
    validate_research_queue_item,
)

__all__ = [
    "QUEUE_READER_SCHEMA_VERSION",
    "DEFAULT_QUEUE_READER_LABEL",
    "QUEUE_READER_STATUS",
    "QUEUE_READER_SAFETY_POSTURE",
    "build_queue_reader_entry",
    "build_queue_reader_summary",
    "render_queue_reader_entry_markdown",
    "render_queue_reader_summary_markdown",
]

QUEUE_READER_SCHEMA_VERSION = "strategy_factory_queue_reader.v1"
DEFAULT_QUEUE_READER_LABEL = "Strategy Factory Queue Reader"
QUEUE_READER_STATUS = "READ_ONLY_QUEUE_REVIEW"

# Inherited all-false safety posture (same keys as Bundle 11). Pinned False:
# this reader only summarizes; it grants nothing.
QUEUE_READER_SAFETY_POSTURE: dict[str, bool] = dict(RESEARCH_QUEUE_SAFETY_POSTURE)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(QUEUE_READER_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def build_queue_reader_entry(item: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only entry for one Bundle 11 item.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise: missing fields produce safe fallbacks and valid=False.
    Every authorization field is FORCED False regardless of the source item;
    if the source carries unsafe True flags, validation marks it invalid but
    the entry stays inert. Returned dicts are fresh."""
    safe_item = item if isinstance(item, dict) else {}
    validation = validate_research_queue_item(safe_item)

    summary = (
        f"Read-only review of idea "
        f"{_as_text(safe_item.get('idea_id')) or '(unknown)'}; "
        "all authorization fields are pinned false and it awaits human "
        "decision."
    )

    return {
        "schema_version": QUEUE_READER_SCHEMA_VERSION,
        "source_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(safe_item.get("idea_id")),
        "title": _as_text(safe_item.get("title")),
        "stage": DEFAULT_RESEARCH_STAGE,
        "mode": DEFAULT_RESEARCH_MODE,
        "status": QUEUE_READER_STATUS,
        "item_status": _as_text(safe_item.get("status")),
        "valid": bool(validation["valid"]),
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
        "validation": validation,
        "next_gate": "human_research_approval",
        "summary": summary,
    }


def build_queue_reader_summary(
    items: tuple[Any, ...],
    *,
    label: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only summary over Bundle 11 items.

    Pure; no I/O, no mutation. All authorization counts stay 0, the summary
    is read-only and inert, and the safety posture is all-false. Consumes
    Bundle 11's build_research_queue for a queue-level validation snapshot."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_QUEUE_READER_LABEL
    )
    item_tuple = tuple(items)
    entries = tuple(build_queue_reader_entry(it) for it in item_tuple)
    valid_count = sum(1 for e in entries if e["valid"])
    invalid_count = len(entries) - valid_count

    # Bundle 11 queue-level snapshot (read-only consumption); we keep only
    # its validation view, not a duplicated validation system.
    source_items = tuple(it for it in item_tuple if isinstance(it, dict))
    source_queue = build_research_queue(source_items, label=name)
    queue_validation = {
        "source_total_items": source_queue["total_items"],
        "source_valid_item_count": source_queue["valid_item_count"],
        "source_invalid_item_count": source_queue["invalid_item_count"],
        "source_status": source_queue["status"],
        "source_human_approval_required": (
            source_queue["human_approval_required"]
        ),
        "source_executes": source_queue["executes"],
    }

    return {
        "schema_version": QUEUE_READER_SCHEMA_VERSION,
        "source_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": QUEUE_READER_STATUS,
        "stage": DEFAULT_RESEARCH_STAGE,
        "mode": DEFAULT_RESEARCH_MODE,
        "total_items": len(item_tuple),
        "valid_item_count": valid_count,
        "invalid_item_count": invalid_count,
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
        "entries": entries,
        "queue_validation": queue_validation,
        "next_gate": "human_research_approval",
    }


def render_queue_reader_entry_markdown(entry: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for one reader entry.
    Pure; writes no file. Informational only."""
    safety = entry.get("safety") or {}
    validation = entry.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Queue Reader Entry")
    lines.append("")
    lines.append(f"Schema: `{entry.get('schema_version', '')}`")
    lines.append(f"Source schema: `{entry.get('source_schema_version', '')}`")
    lines.append(f"Idea ID: {entry.get('idea_id', '')}")
    lines.append(f"Title: {entry.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {entry.get('status', '')}")
    lines.append(f"Valid: {entry.get('valid', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(entry.get("summary", "") or "(none)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
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
        "- A human must review this entry and decide the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_queue_reader_summary_markdown(summary: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for the reader summary.
    Pure; writes no file. Informational only."""
    safety = summary.get("safety") or {}
    entries = summary.get("entries") or ()
    queue_validation = summary.get("queue_validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Queue Reader Summary")
    lines.append("")
    lines.append(f"Schema: `{summary.get('schema_version', '')}`")
    lines.append(
        f"Source schema: `{summary.get('source_schema_version', '')}`"
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
    lines.append("Approved for research count: 0")
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Entries")
    lines.append("")
    if entries:
        for entry in entries:
            lines.append(
                f"- `{entry.get('idea_id', '')}` {entry.get('title', '')} "
                f"(valid=`{entry.get('valid', '')}`, "
                f"read_only=`{entry.get('read_only', '')}`, "
                f"executes=`{entry.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Queue Validation")
    lines.append("")
    for key, value in queue_validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this summary and decide the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
