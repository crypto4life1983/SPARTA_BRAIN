"""SPARTA Offline Strategy Factory - QUEUE ARTIFACT SCHEMA v1 (read-only).

Bundle 4 of the Strategy Factory automation backbone. This module is a
PURE, standalone, stdlib-only *schema descriptor*: it describes the shape
of a run-queue artifact (the JSON object that Bundle 1 loads/validates,
Bundle 2 plans, and Bundle 3 renders) as plain data. It describes; it
never acts and it never writes a file.

It does TWO things and nothing else:
  - describe_schema()  : a deterministic, read-only dict describing the
                         queue artifact (schema id, required fields, the
                         closed status enum, the closed phase chain, the
                         forbidden status values, and per-field notes).
  - schema_fields()    : the tuple of required entry field names.

Both are pure: they perform no I/O and mutate nothing. The descriptor is
DERIVED from Bundle 1's single source of truth (PHASES / QUEUE_STATUS /
REQUIRED_ENTRY_FIELDS / FORBIDDEN_STATUS_VALUES / SCHEMA), so the schema
can never drift from the model that actually validates the artifact.

To keep the same isolation guarantee as Bundles 1-3 it loads Bundle 1 BY
FILE PATH, so it pulls NOTHING out of the host package: no
package-relative import, no top-level package import, and it never
executes the package __init__.

It is deliberately inert: it never writes a file, never creates live queue
data, never imports or invokes any phase module, opens no
network/broker/exchange surface, runs no backtest, fetches no data, and
starts no scheduler/loop. It carries NO execution or promotion verb, so a
schema description can never express a run, a promotion, or a live/paper
trading decision.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SCHEMA = "sparta_commander.strategy_factory_queue_schema.v1"
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
# Additional pins (parity with Bundles 1-3; this module is a pure descriptor).
CREATES_LIVE_QUEUE_DATA = False
USES_CREDENTIALS = False
READS_LOCAL_SECRETS = False
FETCHES_DATA = False

SAFETY_LEVEL = "research_only"


def _load_run_queue() -> Any:
    """Load the Bundle 1 run-queue model BY FILE PATH (no package import).

    Uses a synthetic module name so the host package __init__ is never
    executed. Bundle 1 is a pure stdlib model, so loading has no side
    effects."""
    rq_path = Path(__file__).resolve().parent / "strategy_factory_run_queue.py"
    spec = importlib.util.spec_from_file_location(
        "sfrq_bundle1_for_schema", rq_path
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load run-queue model at {rq_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_RQ = _load_run_queue()

# Re-export Bundle 1's single source of truth so callers share one origin.
QUEUE_SCHEMA_ID = _RQ.SCHEMA
PHASES = _RQ.PHASES
QUEUE_STATUS = _RQ.QUEUE_STATUS
REQUIRED_ENTRY_FIELDS = _RQ.REQUIRED_ENTRY_FIELDS
FORBIDDEN_STATUS_VALUES = _RQ.FORBIDDEN_STATUS_VALUES

# Human-readable note for each required field (descriptive only).
_FIELD_NOTES: dict[str, str] = {
    "run_id": "non-empty string; unique across all entries",
    "candidate_id": "string identifying the strategy candidate",
    "phase": "one of the closed phase chain values",
    "status": "one of the closed status enum values (never a verdict)",
    "priority": "integer (lower = higher priority); bool is rejected",
}

# Optional fields a queue entry may carry (descriptive only).
_OPTIONAL_FIELDS: dict[str, str] = {
    "blockers": "list of strings; a BLOCKED entry must carry at least one",
    "safety_level": f"must equal {SAFETY_LEVEL!r} when present",
}


def schema_fields() -> tuple[str, ...]:
    """Return the tuple of required entry field names. Pure lookup."""
    return tuple(REQUIRED_ENTRY_FIELDS)


def describe_schema() -> dict[str, Any]:
    """Return a deterministic, read-only description of the queue artifact.

    Pure -- performs no I/O and mutates nothing. The returned dict is built
    fresh on each call (callers cannot mutate shared state), and every
    structural fact is derived from Bundle 1's constants so the description
    can never drift from the validator.
    """
    return {
        "schema": SCHEMA,
        "describes_artifact_schema": QUEUE_SCHEMA_ID,
        "safety_level": SAFETY_LEVEL,
        "executes": False,
        "root": {
            "type": "object",
            "fields": {
                "schema": "optional string; must equal "
                f"{QUEUE_SCHEMA_ID!r} when present",
                "entries": "list of entry objects",
            },
        },
        "entry": {
            "type": "object",
            "required_fields": list(REQUIRED_ENTRY_FIELDS),
            "optional_fields": list(_OPTIONAL_FIELDS.keys()),
            "field_notes": {**_FIELD_NOTES, **_OPTIONAL_FIELDS},
        },
        "phase_chain": list(PHASES),
        "status_enum": list(QUEUE_STATUS),
        "forbidden_status_values": sorted(FORBIDDEN_STATUS_VALUES),
    }
