"""SPARTA Offline Strategy Factory - RUN-QUEUE MODEL v1 (read-only).

Bundle 1 of the Strategy Factory automation backbone. This module is a
PURE, standalone, stdlib-only data model for a strategy *run queue*: the
ordered list of candidate runs and where each one sits in the offline
factory phase chain (idea_intake -> hypothesis_spec -> backtest_readiness
-> data_contract_gate -> offline_backtest_run -> block_idea_draft).

It does THREE things and nothing else:
  - load_queue(path)      : read + json-parse one queue file (read-only).
  - validate_queue(obj)   : structurally validate a queue dict.
  - next_actionable(queue): pure read-only projection of which entries are
                            actionable next, in priority order.

It is deliberately inert: it never writes a file, never creates live
queue data, never imports or invokes any phase module, never mutates the
candidate registry, opens no network/broker/exchange surface, and starts
no scheduler/loop. Orchestration, phase invocation, and any runner
adapter are explicitly OUT of scope for this bundle and are NOT built
here. Statuses are drawn from a closed enum that contains no
PASS / PROMOTE / READY(-as-verdict) / GO / LIVE / APPROVE language, so the
queue can never express a promotion or a live/paper trading decision.

Isolation note: pure standalone stdlib. It pulls NOTHING out of the host
package (no package-relative include, no top-level package include), so it
never executes the package init module and is decoupled from routing, the
local-model layer, the tool-config layer, and 3-Brain status logic. It is
NOT wired to any Hunter / alert / dashboard / Strategy Lab bridge /
approval / run path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA = "sparta_commander.strategy_factory_run_queue.v1"
ARC_ID = "OFFLINE-STRATEGY-FACTORY"

# --- Mandated safety constants (asserted by the paired test) ---------
EXECUTES = False
NETWORK = False
MUTATES_REGISTRY = False
SCHEDULER_OR_LOOP = False
USES_BROKER = False
USES_EXCHANGE = False
# Additional pins (this module is a pure read-only model).
WRITES_FILES = False
CREATES_LIVE_QUEUE_DATA = False
INVOKES_PHASE_MODULE = False
RUNS_BACKTEST = False
USES_CREDENTIALS = False
READS_LOCAL_SECRETS = False

# --- Closed phase chain (offline factory phases, in order) -----------
PHASES: tuple[str, ...] = (
    "idea_intake",
    "hypothesis_spec",
    "backtest_readiness",
    "data_contract_gate",
    "offline_backtest_run",
    "block_idea_draft",
)
# Successor of each phase; the terminal phase has no successor.
_PHASE_SUCCESSOR: dict[str, str | None] = {
    PHASES[i]: (PHASES[i + 1] if i + 1 < len(PHASES) else None)
    for i in range(len(PHASES))
}

# --- Closed status enum ----------------------------------------------
# Intentionally contains NO promotion/execution verdict language.
QUEUE_STATUS: tuple[str, ...] = (
    "QUEUED",
    "BLOCKED",
    "READY_FOR_NEXT_PHASE",
    "AWAITING_HUMAN_REVIEW",
    "DONE",
    "FAILED",
)

# Statuses whose entries are eligible to be acted on next. BLOCKED /
# AWAITING_HUMAN_REVIEW / DONE / FAILED are deliberately excluded: they
# require an operator, not automation.
_ACTIONABLE_STATUSES: frozenset[str] = frozenset(
    {"QUEUED", "READY_FOR_NEXT_PHASE"}
)

# Exact status values that must never appear (promotion / live verdicts).
# This is a belt-and-suspenders guard ON TOP of the closed enum check.
FORBIDDEN_STATUS_VALUES: frozenset[str] = frozenset(
    {"PASS", "PROMOTE", "READY", "GO", "LIVE", "APPROVE", "APPROVED", "WIN"}
)

SAFETY_LEVEL = "research_only"

REQUIRED_ENTRY_FIELDS: tuple[str, ...] = (
    "run_id",
    "candidate_id",
    "phase",
    "status",
    "priority",
)


class RunQueueError(ValueError):
    """Raised when a queue file cannot be loaded or parsed."""


def load_queue(path: str | Path) -> dict[str, Any]:
    """Read and json-parse one queue file. READ-ONLY: opens the file for
    reading only, never creates or writes it. Returns the parsed dict.

    Raises RunQueueError if the path is missing, unreadable, not valid
    JSON, or not a JSON object.
    """
    p = Path(path)
    if not p.is_file():
        raise RunQueueError(f"queue file not found: {p}")
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise RunQueueError(f"queue file unreadable: {p}: {exc}") from exc
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RunQueueError(f"queue file is not valid JSON: {p}: {exc}") from exc
    if not isinstance(obj, dict):
        raise RunQueueError(f"queue root must be a JSON object: {p}")
    return obj


def validate_queue(obj: Any) -> tuple[bool, list[str]]:
    """Structurally validate a queue dict. Pure: no I/O, no mutation.

    Returns (ok, errors). ``ok`` is True only when ``errors`` is empty.
    """
    errors: list[str] = []

    if not isinstance(obj, dict):
        return False, ["queue must be a JSON object"]

    if obj.get("schema") not in (None, SCHEMA):
        errors.append(f"unexpected schema: {obj.get('schema')!r}")

    entries = obj.get("entries")
    if not isinstance(entries, list):
        return False, errors + ["queue 'entries' must be a list"]

    seen_run_ids: set[str] = set()
    for idx, entry in enumerate(entries):
        where = f"entry[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{where} must be an object")
            continue

        for field in REQUIRED_ENTRY_FIELDS:
            if field not in entry:
                errors.append(f"{where} missing required field '{field}'")

        run_id = entry.get("run_id")
        if isinstance(run_id, str) and run_id:
            if run_id in seen_run_ids:
                errors.append(f"{where} duplicate run_id {run_id!r}")
            seen_run_ids.add(run_id)
        elif "run_id" in entry:
            errors.append(f"{where} run_id must be a non-empty string")

        status = entry.get("status")
        if status in FORBIDDEN_STATUS_VALUES:
            errors.append(f"{where} forbidden status value {status!r}")
        elif status is not None and status not in QUEUE_STATUS:
            errors.append(f"{where} status {status!r} not in closed enum")

        phase = entry.get("phase")
        if phase is not None and phase not in PHASES:
            errors.append(f"{where} phase {phase!r} not in closed phase chain")

        priority = entry.get("priority")
        if priority is not None and not isinstance(priority, int):
            errors.append(f"{where} priority must be an integer")
        elif isinstance(priority, bool):  # bool is an int subclass; reject it
            errors.append(f"{where} priority must be an integer, not a bool")

        blockers = entry.get("blockers", [])
        if not isinstance(blockers, list):
            errors.append(f"{where} blockers must be a list")

        safety_level = entry.get("safety_level", SAFETY_LEVEL)
        if safety_level != SAFETY_LEVEL:
            errors.append(
                f"{where} safety_level must be {SAFETY_LEVEL!r}, got {safety_level!r}"
            )

        # If an entry is BLOCKED it should carry at least one blocker reason.
        if status == "BLOCKED" and not (isinstance(blockers, list) and blockers):
            errors.append(f"{where} BLOCKED entry must list at least one blocker")

    return (not errors), errors


def successor_phase(phase: str | None) -> str | None:
    """Return the next phase after ``phase`` in the closed chain, or None
    for the terminal phase / an unknown phase. Pure lookup."""
    return _PHASE_SUCCESSOR.get(phase or "", None)


def is_actionable(entry: Any) -> bool:
    """Pure predicate: True if this entry is eligible to be acted on next.
    An entry is actionable only when its status is QUEUED or
    READY_FOR_NEXT_PHASE and it carries no blockers."""
    if not isinstance(entry, dict):
        return False
    if entry.get("status") not in _ACTIONABLE_STATUSES:
        return False
    blockers = entry.get("blockers", [])
    if isinstance(blockers, list) and blockers:
        return False
    return True


def next_actionable(queue: Any) -> list[dict[str, Any]]:
    """Read-only projection: the actionable entries in priority order.

    Pure function -- performs no I/O and does not mutate ``queue``. Entries
    are ordered by ascending ``priority`` (lower number = higher priority),
    then by ``run_id`` for deterministic ties. Non-actionable entries
    (BLOCKED / AWAITING_HUMAN_REVIEW / DONE / FAILED, or any entry carrying
    blockers) are excluded. Returns shallow copies so callers cannot mutate
    the source through the result.
    """
    if not isinstance(queue, dict):
        return []
    entries = queue.get("entries")
    if not isinstance(entries, list):
        return []
    actionable = [e for e in entries if is_actionable(e)]

    def _key(e: dict[str, Any]) -> tuple[int, str]:
        prio = e.get("priority")
        prio = prio if isinstance(prio, int) and not isinstance(prio, bool) else 1_000_000
        return (prio, str(e.get("run_id", "")))

    return [dict(e) for e in sorted(actionable, key=_key)]
