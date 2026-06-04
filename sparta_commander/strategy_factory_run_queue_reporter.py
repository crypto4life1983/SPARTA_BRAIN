"""SPARTA Offline Strategy Factory - RUN-QUEUE REPORTER v1 (read-only).

Bundle 3 of the Strategy Factory automation backbone. This module is a
PURE, standalone, stdlib-only *reporter*: given a Bundle-2 plan dict (the
output of ``build_run_plan``), it renders a DESCRIPTIVE, human-readable
report. It renders text; it never acts and it never writes a file.

It does THREE things and nothing else:
  - render_plan_text(plan)     : a deterministic plain-text report string.
  - render_plan_markdown(plan) : a deterministic markdown-table report string.
  - summarize_plan(plan)       : a one-line action-count summary string.

All three are pure: they perform no I/O, mutate nothing, and RETURN
STRINGS ONLY -- they write no files. Malformed / garbage input returns a
single safe, fixed string rather than raising.

It reuses Bundle 2's pure surface ONLY (SCHEMA / PLAN_ACTION). To keep the
same isolation guarantee as Bundles 1 and 2 it loads Bundle 2 BY FILE
PATH, so it pulls NOTHING out of the host package: no package-relative
import, no top-level package import, and it never executes the package
__init__.

It is deliberately inert: it never writes a file, never creates live queue
data, never imports or invokes any phase module, opens no
network/broker/exchange surface, runs no backtest, fetches no data, and
starts no scheduler/loop. The rendered output is descriptive only and
carries NO execution or promotion verb (no RUN / EXECUTE / PLACE / TRADE /
PROMOTE / GO / LIVE / APPROVE / PASS / READY / WIN), so a report can never
express a run, a promotion, or a live/paper trading decision.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SCHEMA = "sparta_commander.strategy_factory_run_queue_reporter.v1"
ARC_ID = "OFFLINE-STRATEGY-FACTORY"

# --- Mandated safety constants (asserted by the paired test) ---------
EXECUTES = False
NETWORK = False
WRITES_FILES = False
MUTATES_REGISTRY = False
SCHEDULER_OR_LOOP = False
USES_BROKER = False
USES_EXCHANGE = False
INVOKES_PHASE_MODULE = False
RUNS_BACKTEST = False
# Additional pins (parity with Bundles 1 & 2; this module is a pure reporter).
CREATES_LIVE_QUEUE_DATA = False
USES_CREDENTIALS = False
READS_LOCAL_SECRETS = False
FETCHES_DATA = False

SAFETY_LEVEL = "research_only"

# A single safe, fixed string returned for any malformed / unusable input.
_EMPTY_REPORT = "(empty plan: nothing to report)"


def _load_planner() -> Any:
    """Load the Bundle 2 planner BY FILE PATH (no package import).

    Uses a synthetic module name so the host package __init__ is never
    executed. Bundle 2 is a pure stdlib planner (which itself loads Bundle
    1 by file path), so loading it has no side effects."""
    pl_path = (
        Path(__file__).resolve().parent
        / "strategy_factory_run_queue_planner.py"
    )
    spec = importlib.util.spec_from_file_location(
        "sfrqp_bundle2_for_reporter", pl_path
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load planner at {pl_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PL = _load_planner()

# Re-export Bundle 2's closed plan-action enum so callers share one source.
PLAN_ACTION = _PL.PLAN_ACTION


def _is_plan(plan: Any) -> bool:
    """True only for a well-formed plan dict with a list 'plan' field."""
    return isinstance(plan, dict) and isinstance(plan.get("plan"), list)


def _rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """The dict rows of a plan, in their given (already-ordered) order."""
    return [r for r in plan.get("plan", []) if isinstance(r, dict)]


def _blockers_str(row: dict[str, Any]) -> str:
    blockers = row.get("blockers", [])
    if not isinstance(blockers, list) or not blockers:
        return "-"
    return "; ".join(str(b) for b in blockers)


def _field(row: dict[str, Any], key: str) -> str:
    val = row.get(key)
    if val is None:
        return "-"
    return str(val)


def summarize_plan(plan: Any) -> str:
    """One-line action-count summary string. Pure; no I/O, no mutation.

    Returns a fixed safe string for malformed input."""
    if not _is_plan(plan):
        return _EMPTY_REPORT
    rows = _rows(plan)
    counts = {action: 0 for action in PLAN_ACTION}
    for r in rows:
        action = r.get("action")
        if action in counts:
            counts[action] += 1
        else:
            counts[action] = counts.get(action, 0) + 1
    parts = [f"{action}={counts.get(action, 0)}" for action in PLAN_ACTION]
    return f"{len(rows)} entries | " + " ".join(parts)


def render_plan_text(plan: Any) -> str:
    """Deterministic plain-text report string. Pure; no I/O, no mutation.

    Returns a fixed safe string for malformed input. Describes each entry;
    emits no execution/promotion verb and no command."""
    if not _is_plan(plan):
        return _EMPTY_REPORT
    rows = _rows(plan)
    lines: list[str] = []
    lines.append("Strategy Factory Run-Queue Report (read-only; describes only)")
    lines.append(f"schema: {SCHEMA}")
    lines.append(f"safety_level: {SAFETY_LEVEL}")
    lines.append(f"summary: {summarize_plan(plan)}")
    lines.append("")
    if not rows:
        lines.append("(no entries)")
        return "\n".join(lines)
    for i, r in enumerate(rows, start=1):
        lines.append(f"{i}. {_field(r, 'run_id')} [{_field(r, 'candidate_id')}]")
        lines.append(
            f"   phase: {_field(r, 'current_phase')}"
            f" -> {_field(r, 'next_phase')}"
        )
        lines.append(f"   action: {_field(r, 'action')}")
        lines.append(f"   reason: {_field(r, 'reason')}")
        lines.append(f"   blockers: {_blockers_str(r)}")
    return "\n".join(lines)


def render_plan_markdown(plan: Any) -> str:
    """Deterministic markdown-table report string. Pure; no I/O, no
    mutation. Returns a fixed safe string for malformed input."""
    if not _is_plan(plan):
        return _EMPTY_REPORT
    rows = _rows(plan)
    lines: list[str] = []
    lines.append("# Strategy Factory Run-Queue Report")
    lines.append("")
    lines.append("_Read-only; describes only. No execution._")
    lines.append("")
    lines.append(f"- schema: `{SCHEMA}`")
    lines.append(f"- safety_level: `{SAFETY_LEVEL}`")
    lines.append(f"- summary: {summarize_plan(plan)}")
    lines.append("")
    lines.append(
        "| # | run_id | candidate_id | current_phase | next_phase"
        " | action | reason | blockers |"
    )
    lines.append("| - | - | - | - | - | - | - | - |")
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"| {i} | {_field(r, 'run_id')} | {_field(r, 'candidate_id')}"
            f" | {_field(r, 'current_phase')} | {_field(r, 'next_phase')}"
            f" | {_field(r, 'action')} | {_field(r, 'reason')}"
            f" | {_blockers_str(r)} |"
        )
    return "\n".join(lines)
