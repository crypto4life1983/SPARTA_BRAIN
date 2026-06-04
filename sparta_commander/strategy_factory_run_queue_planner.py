"""SPARTA Offline Strategy Factory - RUN-QUEUE PLANNER v1 (read-only).

Bundle 2 of the Strategy Factory automation backbone. This module is a
PURE, standalone, stdlib-only *planner*: given a Bundle-1-validated run
queue (a dict), it produces a DESCRIPTIVE plan of what a future (not yet
built) orchestrator *would* be asked to do with each entry. It describes;
it never acts.

It does ONE thing and nothing else:
  - build_run_plan(queue): pure read-only projection mapping every queue
    entry to a closed-enum PLAN_ACTION label + the successor phase, with a
    reason and the entry's blockers. Ordered by priority then run_id.

It reuses Bundle 1's pure helpers ONLY (PHASES / successor_phase /
is_actionable / QUEUE_STATUS / FORBIDDEN_STATUS_VALUES). To keep the same
isolation guarantee as Bundle 1 it loads that module BY FILE PATH, so it
pulls NOTHING out of the host package: no package-relative import, no
top-level package import, and it never executes the package __init__.

It is deliberately inert: it never writes a file, never creates live queue
data, never imports or invokes any phase module, opens no
network/broker/exchange surface, runs no backtest, fetches no data, and
starts no scheduler/loop. The PLAN_ACTION enum contains NO execution or
promotion verb (no RUN / EXECUTE / PLACE / TRADE / PROMOTE / GO / LIVE /
APPROVE / PASS / READY / WIN), so a plan can never express a run, a
promotion, or a live/paper trading decision.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SCHEMA = "sparta_commander.strategy_factory_run_queue_planner.v1"
ARC_ID = "OFFLINE-STRATEGY-FACTORY"

# --- Mandated safety constants (asserted by the paired test) ---------
EXECUTES = False
NETWORK = False
MUTATES_REGISTRY = False
SCHEDULER_OR_LOOP = False
USES_BROKER = False
USES_EXCHANGE = False
WRITES_FILES = False
INVOKES_PHASE_MODULE = False
RUNS_BACKTEST = False
# Additional pins (parity with Bundle 1; this module is a pure planner).
CREATES_LIVE_QUEUE_DATA = False
USES_CREDENTIALS = False
READS_LOCAL_SECRETS = False
FETCHES_DATA = False

SAFETY_LEVEL = "research_only"


def _load_run_queue() -> Any:
    """Load the Bundle 1 run-queue model BY FILE PATH (no package import).

    Uses a synthetic module name so the host package __init__ is never
    executed. Bundle 1 is a pure stdlib model, so loading it has no side
    effects."""
    rq_path = Path(__file__).resolve().parent / "strategy_factory_run_queue.py"
    spec = importlib.util.spec_from_file_location(
        "sfrq_bundle1_for_planner", rq_path
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load run-queue model at {rq_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_RQ = _load_run_queue()

# Re-export Bundle 1's forbidden status guard so callers share one source.
FORBIDDEN_STATUS_VALUES = _RQ.FORBIDDEN_STATUS_VALUES

# --- Closed plan-action enum (NO execution / promotion verbs) --------
# Every action is descriptive. None expresses a run, a promotion, or a
# live/paper trading decision.
PLAN_ACTION: tuple[str, ...] = (
    "ADVANCE_TO_NEXT_PHASE",
    "HOLD_BLOCKED",
    "AWAIT_HUMAN",
    "TERMINAL_DONE",
    "NO_ACTION",
)


def _empty_plan() -> dict[str, Any]:
    """A safe, well-formed empty plan (used for garbage / malformed input)."""
    return {
        "schema": SCHEMA,
        "source_schema": _RQ.SCHEMA,
        "safety_level": SAFETY_LEVEL,
        "executes": False,
        "plan": [],
        "summary": {action: 0 for action in PLAN_ACTION},
        "entry_count": 0,
    }


def _plan_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Map ONE queue entry to a descriptive plan row. Pure; no I/O, no
    mutation of ``entry``. Never advances a blocked / human / failed /
    forbidden entry."""
    run_id = entry.get("run_id")
    candidate_id = entry.get("candidate_id")
    phase = entry.get("phase")
    status = entry.get("status")
    blockers = entry.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []

    next_phase: str | None = None
    actionable = False

    if status in FORBIDDEN_STATUS_VALUES or (
        status is not None and status not in _RQ.QUEUE_STATUS
    ):
        action = "NO_ACTION"
        reason = "unrecognized or forbidden status; never advanced"
    elif status == "BLOCKED":
        action = "HOLD_BLOCKED"
        reason = "entry is BLOCKED; awaiting blocker resolution"
    elif status == "AWAITING_HUMAN_REVIEW":
        action = "AWAIT_HUMAN"
        reason = "awaiting human review; automation must not proceed"
    elif status == "FAILED":
        action = "NO_ACTION"
        reason = "entry FAILED; no further automated step"
    elif status == "DONE":
        action = "TERMINAL_DONE"
        reason = "entry already DONE; no further step"
    else:
        # QUEUED or READY_FOR_NEXT_PHASE
        actionable = _RQ.is_actionable(entry)
        if not actionable:
            action = "HOLD_BLOCKED"
            reason = "actionable status but blockers present; held"
        else:
            successor = _RQ.successor_phase(phase)
            if successor is None:
                action = "TERMINAL_DONE"
                reason = "terminal phase reached; no successor"
            else:
                action = "ADVANCE_TO_NEXT_PHASE"
                next_phase = successor
                reason = f"actionable; next phase {successor}"

    return {
        "run_id": run_id,
        "candidate_id": candidate_id,
        "current_phase": phase,
        "next_phase": next_phase,
        "action": action,
        "actionable": bool(actionable),
        "reason": reason,
        "blockers": list(blockers),
    }


def build_run_plan(queue: Any) -> dict[str, Any]:
    """Read-only projection: a descriptive plan for ``queue``.

    Pure function -- performs no I/O and does not mutate ``queue``. Every
    dict entry is described (ordered by ascending ``priority`` then
    ``run_id`` for deterministic ties) with a closed-enum PLAN_ACTION, the
    successor phase, a reason, and a copy of its blockers. Non-dict entries
    are skipped. Malformed input returns a safe empty plan. This describes
    what a future orchestrator *would* be asked to do; it executes nothing.
    """
    if not isinstance(queue, dict):
        return _empty_plan()
    entries = queue.get("entries")
    if not isinstance(entries, list):
        return _empty_plan()

    valid = [e for e in entries if isinstance(e, dict)]

    def _key(e: dict[str, Any]) -> tuple[int, str]:
        prio = e.get("priority")
        prio = prio if isinstance(prio, int) and not isinstance(prio, bool) else 1_000_000
        return (prio, str(e.get("run_id", "")))

    plan = [_plan_entry(e) for e in sorted(valid, key=_key)]

    summary = {action: 0 for action in PLAN_ACTION}
    for row in plan:
        summary[row["action"]] = summary.get(row["action"], 0) + 1

    return {
        "schema": SCHEMA,
        "source_schema": _RQ.SCHEMA,
        "safety_level": SAFETY_LEVEL,
        "executes": False,
        "plan": plan,
        "summary": summary,
        "entry_count": len(plan),
    }
