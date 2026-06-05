"""SPARTA Offline Strategy Factory - RESEARCH QUEUE INTAKE v1.

Bundle 11 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *research-intake* layer: it turns a strategy idea into a
deterministic RESEARCH_ONLY queue item with validation, all-false safety
gates, and an explicit human-approval requirement.

It is informational and research-intake only. It runs nothing, computes no
backtest, fetches no data, writes no file, opens no network, spawns no
subprocess, touches no broker/exchange/order/trading/live/upload/autopilot
surface, promotes/deploys nothing, and records no approval decision. It
records no timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_QUEUE_SCHEMA_VERSION
  - DEFAULT_RESEARCH_QUEUE_LABEL
  - RESEARCH_QUEUE_STATUS
  - RESEARCH_QUEUE_SAFETY_POSTURE
  - DEFAULT_RESEARCH_STAGE
  - DEFAULT_RESEARCH_MODE
  - build_research_queue_item(...)
  - build_research_queue(...)
  - validate_research_queue_item(...)
  - render_research_queue_item_markdown(...)
  - render_research_queue_markdown(...)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "RESEARCH_QUEUE_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_QUEUE_LABEL",
    "RESEARCH_QUEUE_STATUS",
    "RESEARCH_QUEUE_SAFETY_POSTURE",
    "DEFAULT_RESEARCH_STAGE",
    "DEFAULT_RESEARCH_MODE",
    "build_research_queue_item",
    "build_research_queue",
    "validate_research_queue_item",
    "render_research_queue_item_markdown",
    "render_research_queue_markdown",
]

RESEARCH_QUEUE_SCHEMA_VERSION = "strategy_factory_research_queue.v1"
DEFAULT_RESEARCH_QUEUE_LABEL = "Strategy Factory Research Queue"
RESEARCH_QUEUE_STATUS = "RESEARCH_ONLY_AWAITING_HUMAN_APPROVAL"
DEFAULT_RESEARCH_STAGE = "PLAN_ONLY"
DEFAULT_RESEARCH_MODE = "RESEARCH_ONLY"

# All-false safety posture. Pinned False: this layer only describes a plan a
# human would sign off on; it grants no capability whatsoever.
RESEARCH_QUEUE_SAFETY_POSTURE: dict[str, bool] = {
    "automation_enabled": False,
    "live_execution_enabled": False,
    "paper_execution_enabled": False,
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

# Required non-empty string fields for a valid research queue item.
_REQUIRED_ITEM_FIELDS: tuple[str, ...] = ("idea_id", "title", "thesis")

# Authorization flags that must all stay False for an item to be valid.
_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_QUEUE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def build_research_queue_item(
    idea_id: str,
    title: str,
    thesis: str,
    *,
    asset_lane: str = "UNSPECIFIED",
    timeframe: str = "UNSPECIFIED",
    source: str = "operator",
    notes: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic RESEARCH_ONLY queue item.

    Pure; no I/O, no mutation, no timestamp, no random id. Empty
    idea_id/title/thesis do not raise; validation marks such an item invalid.
    Returned dicts are fresh, so mutating one result cannot taint the next."""
    note_tuple = tuple(notes) if notes is not None else ()
    item: dict[str, Any] = {
        "schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(idea_id),
        "title": _as_text(title),
        "thesis": _as_text(thesis),
        "asset_lane": _as_text(asset_lane),
        "timeframe": _as_text(timeframe),
        "source": _as_text(source),
        "stage": DEFAULT_RESEARCH_STAGE,
        "mode": DEFAULT_RESEARCH_MODE,
        "status": RESEARCH_QUEUE_STATUS,
        "approved_for_research": False,
        "execution_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "data_fetch_authorized": False,
        "backtest_authorized": False,
        "promotion_authorized": False,
        "human_approval_required": True,
        "executes": False,
        "safety": _safety_posture(),
        "notes": note_tuple,
        "required_next_gate": "human_research_approval",
    }
    item["validation"] = validate_research_queue_item(item)
    return item


def validate_research_queue_item(item: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic validation result for a queue item.

    Valid only when required fields are present/non-empty, schema version is
    correct, mode is RESEARCH_ONLY, stage is PLAN_ONLY, human approval is
    required, every authorization flag is False, and every safety flag is
    False. Pure; never raises on a malformed dict."""
    safety = item.get("safety")
    safety_all_false = (
        isinstance(safety, dict)
        and len(safety) == len(RESEARCH_QUEUE_SAFETY_POSTURE)
        and all(v is False for v in safety.values())
    )

    missing = tuple(
        field
        for field in _REQUIRED_ITEM_FIELDS
        if not _as_text(item.get(field))
    )

    schema_version_ok = (
        item.get("schema_version") == RESEARCH_QUEUE_SCHEMA_VERSION
    )
    research_only = item.get("mode") == DEFAULT_RESEARCH_MODE
    plan_only = item.get("stage") == DEFAULT_RESEARCH_STAGE
    human_approval_required = item.get("human_approval_required") is True

    auth_flags = {
        flag: (item.get(flag) is False) for flag in _AUTHORIZATION_FLAGS
    }
    all_auth_false = all(auth_flags.values())

    valid = (
        not missing
        and schema_version_ok
        and research_only
        and plan_only
        and human_approval_required
        and all_auth_false
        and safety_all_false
    )

    return {
        "valid": bool(valid),
        "schema_version_ok": bool(schema_version_ok),
        "research_only": bool(research_only),
        "plan_only": bool(plan_only),
        "human_approval_required": bool(human_approval_required),
        "execution_authorized": item.get("execution_authorized") is True,
        "paper_trading_authorized": (
            item.get("paper_trading_authorized") is True
        ),
        "live_trading_authorized": (
            item.get("live_trading_authorized") is True
        ),
        "data_fetch_authorized": item.get("data_fetch_authorized") is True,
        "backtest_authorized": item.get("backtest_authorized") is True,
        "promotion_authorized": item.get("promotion_authorized") is True,
        "missing_required_fields": missing,
        "safety_all_false": bool(safety_all_false),
    }


def build_research_queue(
    items: tuple[dict[str, Any], ...],
    *,
    label: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic research queue over the given items.

    Pure; no I/O, no mutation. All authorization counts stay 0, the queue
    executes nothing, and the safety posture is all-false."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_RESEARCH_QUEUE_LABEL
    )
    item_tuple = tuple(items)
    validations = tuple(
        validate_research_queue_item(it) for it in item_tuple
    )
    valid_count = sum(1 for v in validations if v["valid"])
    invalid_count = len(item_tuple) - valid_count

    return {
        "schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": RESEARCH_QUEUE_STATUS,
        "mode": DEFAULT_RESEARCH_MODE,
        "stage": DEFAULT_RESEARCH_STAGE,
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
        "executes": False,
        "safety": _safety_posture(),
        "items": item_tuple,
        "validation": validations,
    }


def render_research_queue_item_markdown(item: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for one queue item.
    Pure; writes no file. Informational only."""
    validation = item.get("validation") or validate_research_queue_item(item)
    safety = item.get("safety") or {}
    notes = item.get("notes") or ()

    lines: list[str] = []
    lines.append("# Strategy Factory Research Queue Item")
    lines.append("")
    lines.append(f"Schema: `{item.get('schema_version', '')}`")
    lines.append(f"Idea ID: {item.get('idea_id', '')}")
    lines.append(f"Title: {item.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {item.get('status', '')}")
    lines.append("Human approval required: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Thesis")
    lines.append("")
    lines.append(item.get("thesis", "") or "(none provided)")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    if notes:
        for note in notes:
            lines.append(f"- {note}")
    else:
        lines.append("- (none)")
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
        "- A human must review this item and decide the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_research_queue_markdown(queue: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for the whole queue.
    Pure; writes no file. Informational only."""
    safety = queue.get("safety") or {}
    items = queue.get("items") or ()
    validations = queue.get("validation") or ()

    lines: list[str] = []
    lines.append("# Strategy Factory Research Queue")
    lines.append("")
    lines.append(f"Schema: `{queue.get('schema_version', '')}`")
    lines.append(f"Label: {queue.get('label', '')}")
    lines.append(f"Status: {queue.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Total items: {queue.get('total_items', 0)}")
    lines.append(f"Valid item count: {queue.get('valid_item_count', 0)}")
    lines.append(f"Invalid item count: {queue.get('invalid_item_count', 0)}")
    lines.append("Approved for research count: 0")
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Items")
    lines.append("")
    if items:
        for item in items:
            lines.append(
                f"- `{item.get('idea_id', '')}` {item.get('title', '')} "
                f"(stage=`{item.get('stage', '')}`, "
                f"mode=`{item.get('mode', '')}`, "
                f"executes=`{item.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    valid_n = sum(1 for v in validations if v.get("valid"))
    lines.append(f"- `valid`: `{valid_n}`")
    lines.append(f"- `invalid`: `{len(validations) - valid_n}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this queue and decide the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
