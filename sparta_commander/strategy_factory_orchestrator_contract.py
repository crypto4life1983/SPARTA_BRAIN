"""SPARTA Offline Strategy Factory - DRY-RUN ORCHESTRATOR CONTRACT v1.

Bundle 5 of the Strategy Factory automation backbone. This module is a
PURE, standalone, stdlib-only *contract descriptor*: for every Bundle-2
PLAN_ACTION it describes the boundary a future (NOT yet built, NOT
authorized) orchestrator would be bound to honour -- the descriptive
intent, the preconditions, whether a human sign-off is mandatory, and the
hard list of capabilities every step is forbidden from touching. It
describes a contract; it never acts and it never writes a file.

It does THREE things and nothing else:
  - describe_orchestrator_contract() : a deterministic, read-only dict
                                       describing the per-action contract.
  - contract_for_action(action)      : the contract for one action (pure
                                       lookup; safe fallback for unknowns).
  - render_contract_markdown()       : a deterministic markdown string of
                                       the contract (strings only).

All three are pure: they perform no I/O and mutate nothing. The action set
is DERIVED from Bundle 2's closed PLAN_ACTION enum (no drift). To keep the
same isolation guarantee as Bundles 1-4 it loads Bundle 2 BY FILE PATH, so
it pulls NOTHING out of the host package: no package-relative import, no
top-level package import, and it never executes the package __init__.

It is deliberately inert: it never writes a file, never creates live queue
data, never imports or invokes any phase module, opens no
network/broker/exchange surface, computes no backtest, fetches no data, and
starts no scheduler/loop. The descriptive intent text carries NO execution
or promotion verb, so a contract can never express a real run, a
promotion, or a live/paper trading decision. The forbidden-capability list
enumerates what is banned; it is data, not a command.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SCHEMA = "sparta_commander.strategy_factory_orchestrator_contract.v1"
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
# Additional pins (parity with Bundles 1-4; this module is a pure descriptor).
CREATES_LIVE_QUEUE_DATA = False
USES_CREDENTIALS = False
READS_LOCAL_SECRETS = False
FETCHES_DATA = False

SAFETY_LEVEL = "research_only"


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
        "sfrqp_bundle2_for_contract", pl_path
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load planner at {pl_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PL = _load_planner()

# Re-export Bundle 2's closed plan-action enum so callers share one source.
PLAN_ACTION = _PL.PLAN_ACTION

# --- Hard list of capabilities every step is forbidden from touching --
# This is descriptive data (a banned-capability enumeration), NOT a verb
# list a step may use. Tokens are snake_case so they never read as a
# command and never collide with the forbidden execution/promotion verbs.
FORBIDDEN_CAPABILITIES: tuple[str, ...] = (
    "execution",
    "phase_module_invocation",
    "backtest_computation",
    "data_fetch",
    "broker_exchange_order_action",
    "upload_or_autopilot",
    "registry_or_queue_mutation",
    "live_queue_data_creation",
    "credentials_or_secrets",
    "network",
    "scheduler_or_loop",
    "file_write",
    "promotion_or_verdict",
)

# Per-action contract terms. The intent + preconditions are descriptive
# prose and carry NO execution/promotion verb; the human gate is explicit.
_STEPS: dict[str, dict[str, Any]] = {
    "ADVANCE_TO_NEXT_PHASE": {
        "intent": (
            "A future authorized orchestrator would record an "
            "operator-authorized intent to advance this entry to its "
            "successor phase. It computes nothing and mutates no "
            "persistent state."
        ),
        "preconditions": [
            "the entry is actionable under the Bundle 1 model",
            "the entry carries no blockers",
            "an operator has pre-registered and authorized this candidate",
            "human sign-off has been granted out of band",
        ],
        "requires_human_approval": True,
    },
    "HOLD_BLOCKED": {
        "intent": (
            "The entry is held. Its blockers must be cleared by an "
            "operator before any further step is considered."
        ),
        "preconditions": [
            "at least one blocker is present",
            "an operator must resolve every blocker first",
        ],
        "requires_human_approval": True,
    },
    "AWAIT_HUMAN": {
        "intent": (
            "The entry defers to a human reviewer. Automation must not "
            "proceed without explicit human sign-off."
        ),
        "preconditions": [
            "a human reviewer is assigned",
            "no automated step may proceed",
        ],
        "requires_human_approval": True,
    },
    "TERMINAL_DONE": {
        "intent": (
            "No further step. The entry has reached a terminal phase or "
            "is already complete."
        ),
        "preconditions": [
            "the entry is at the terminal phase or already complete",
        ],
        "requires_human_approval": False,
    },
    "NO_ACTION": {
        "intent": (
            "No step is described. The status is unrecognized, "
            "forbidden, or marked failed."
        ),
        "preconditions": [
            "the status is not an actionable closed-enum value",
        ],
        "requires_human_approval": False,
    },
}

# A safe contract returned for any action outside the closed enum.
_UNKNOWN_CONTRACT: dict[str, Any] = {
    "intent": (
        "No contract is defined for this action. No step is described "
        "and no capability is granted."
    ),
    "preconditions": ["the action is not in the closed plan-action enum"],
    "requires_human_approval": True,
}


def _step_contract(action: str) -> dict[str, Any]:
    """Build a fresh contract row for ``action``. Pure; no I/O, no mutation."""
    base = _STEPS.get(action, _UNKNOWN_CONTRACT)
    return {
        "action": action if action in _STEPS else "UNKNOWN",
        "intent": base["intent"],
        "preconditions": list(base["preconditions"]),
        "requires_human_approval": bool(base["requires_human_approval"]),
        "forbidden": list(FORBIDDEN_CAPABILITIES),
    }


def contract_for_action(action: Any) -> dict[str, Any]:
    """Return the contract for one action. Pure lookup; never raises.

    An action outside the closed PLAN_ACTION enum yields a safe fallback
    contract that grants nothing and still requires human sign-off."""
    key = action if isinstance(action, str) else ""
    return _step_contract(key)


def describe_orchestrator_contract() -> dict[str, Any]:
    """Return a deterministic, read-only description of the dry-run contract.

    Pure -- performs no I/O and mutates nothing. The returned dict is built
    fresh on each call (callers cannot mutate shared state), and the action
    set is derived from Bundle 2's PLAN_ACTION so the contract can never
    drift from the planner. It describes what a future, separately
    authorized orchestrator would be bound to honour; it acts on nothing.
    """
    return {
        "schema": SCHEMA,
        "source_schema": _PL.SCHEMA,
        "safety_level": SAFETY_LEVEL,
        "executes": False,
        "requires_human_approval": True,
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "steps": {action: _step_contract(action) for action in PLAN_ACTION},
    }


def render_contract_markdown() -> str:
    """Return a deterministic markdown string of the contract. Pure; no
    I/O, no mutation; returns a string and writes no file."""
    c = describe_orchestrator_contract()
    lines: list[str] = []
    lines.append("# Strategy Factory Dry-Run Orchestrator Contract")
    lines.append("")
    lines.append("_Read-only; describes only. No execution. No automation._")
    lines.append("")
    lines.append(f"- schema: `{c['schema']}`")
    lines.append(f"- source_schema: `{c['source_schema']}`")
    lines.append(f"- safety_level: `{c['safety_level']}`")
    lines.append(f"- executes: `{c['executes']}`")
    lines.append(f"- requires_human_approval: `{c['requires_human_approval']}`")
    lines.append("")
    lines.append("## Forbidden capabilities (every step)")
    lines.append("")
    for cap in c["forbidden_capabilities"]:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Per-action contract")
    lines.append("")
    for action in PLAN_ACTION:
        step = c["steps"][action]
        lines.append(f"### {action}")
        lines.append("")
        lines.append(f"- intent: {step['intent']}")
        lines.append(
            f"- requires_human_approval: `{step['requires_human_approval']}`"
        )
        lines.append("- preconditions:")
        for pre in step["preconditions"]:
            lines.append(f"  - {pre}")
        lines.append("")
    return "\n".join(lines)
