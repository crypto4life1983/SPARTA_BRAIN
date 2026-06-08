"""Offline Strategy Factory Arc Hold Decision (Bundle 163).

A pure, stdlib-only, read-only DECISION record. It records the Bundle 162
finding that the inspected untracked scaffolds are part of a larger untracked
``OFFLINE-STRATEGY-FACTORY`` arc and resolves a single verdict: ``HOLD_ARC``.

The arc is a SEPARATE lineage from the committed Crypto-D1 RESEARCH_ONLY chain
(Bundles 42-161). It partly overlaps committed Crypto-D1 modules, and its Phase 5
runner reads OHLCV and runs a deterministic paper backtest -- which crosses the
very boundary the committed chain is parked behind
(HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED). Therefore the arc must
be held as a whole: no single file may be adopted, no single file may be deleted,
it is not wired into mission flow, it is not surfaced in JARVIS as active, and it
is never staged. A future, explicit, arc-level decision is required -- one of
ADOPT_WHOLE_ARC / DELETE_WHOLE_ARC / IGNORE_WHOLE_ARC.

This module authorizes nothing and executes nothing. It builds a static decision
object in memory only: it reads no files, performs no I/O, touches no network,
reads no credentials, and writes nothing. It does not advance the mission-flow
stage, does not change the next required action, unlocks no real_data_qa, no
baseline/backtest, and no paper/micro-live gate. Every capability flag is False.
A fresh record is returned on every call for mutation isolation.
"""

from __future__ import annotations

from typing import Any

DECISION_SCHEMA_VERSION = (
    "strategy_factory_offline_strategy_factory_arc_hold_decision.v1"
)
DECISION_LABEL = "Bundle 163 - Offline Strategy Factory Arc Hold Decision"
DECISION_MODE = "RESEARCH_ONLY"
DECISION_STATUS = "READ_ONLY_DECISION_RECORD"

ARC_ID = "OFFLINE-STRATEGY-FACTORY"

# The single resolved verdict + arc status.
VERDICT_HOLD_ARC = "HOLD_ARC"
VERDICT = VERDICT_HOLD_ARC
ARC_STATUS = "LOCAL_ONLY_UNTRACKED_HELD"

# Phase 5 carries the highest capability in the arc: it reads OHLCV bars and runs
# a deterministic paper backtest. It is recorded here as present-but-not-adopted.
PHASE5_COMPONENT_NAME = "strategy_factory_phase5_offline_backtest_run"
PHASE5_RISK = "BACKTEST_AND_OHLCV_READING_PRESENT_BUT_NOT_ADOPTED"

# Boundary the committed Crypto-D1 chain stays parked at -- unchanged by this
# decision (mirrors the live mission-flow truth; never advanced here).
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The only future moves allowed -- an explicit, whole-arc, human decision.
REQUIRED_FUTURE_ARC_LEVEL_DECISIONS = (
    "ADOPT_WHOLE_ARC",
    "DELETE_WHOLE_ARC",
    "IGNORE_WHOLE_ARC",
)

# Downstream gate states -- preserved, never unlocked by this decision.
GATE_STATES = {
    "real_data_qa": "BLOCKED",
    "baseline_backtest": "BLOCKED",
    "paper_trading_gate": "LOCKED",
    "micro_live_gate": "LOCKED",
}

# Capability flags -- all False (mirrors the committed bundle-locked posture).
CAPABILITY_FLAGS = (
    "authorizes_real_world_action",
    "unlocks_data_acquisition",
    "unlocks_qa",
    "unlocks_baseline",
    "unlocks_backtest",
    "unlocks_simulation",
    "unlocks_paper_live",
    "unlocks_broker_exchange",
    "unlocks_automation",
    "unlocks_runtime_writes",
    "unlocks_registry_writes",
    "unlocks_dashboard_writes",
    "adopts_any_arc_file",
    "deletes_any_arc_file",
    "stages_any_arc_file",
    "wires_arc_into_mission_flow",
    "surfaces_arc_in_jarvis_active",
    "advances_boundary",
)

# Static catalog of the held arc components (Bundle 162 finding). Every entry is
# HELD: it is neither adopted nor deleted individually, and is never staged. The
# Phase 5 runner is additionally marked as the highest-risk component.
_ARC_COMPONENTS: tuple[dict[str, Any], ...] = (
    {
        "name": "strategy_factory_charter",
        "path": "sparta_commander/strategy_factory_charter.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_idea_intake",
        "path": "sparta_commander/strategy_factory_idea_intake.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_source_registry",
        "path": "sparta_commander/strategy_factory_source_registry.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_data_contract_gate",
        "path": "sparta_commander/strategy_factory_data_contract_gate.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_hypothesis_spec",
        "path": "sparta_commander/strategy_factory_hypothesis_spec.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_backtest_readiness",
        "path": "sparta_commander/strategy_factory_backtest_readiness.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_template_registry",
        "path": "sparta_commander/strategy_factory_template_registry.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_cost_slippage_registry",
        "path": "sparta_commander/strategy_factory_cost_slippage_registry.py",
        "kind": "module",
    },
    {
        "name": "strategy_factory_phase5_block_idea_draft",
        "path": "sparta_commander/strategy_factory_phase5_block_idea_draft.py",
        "kind": "module",
    },
    {
        "name": PHASE5_COMPONENT_NAME,
        "path": (
            "sparta_commander/strategy_factory_phase5_offline_backtest_run.py"
        ),
        "kind": "module",
        "highest_risk": True,
        "risk": PHASE5_RISK,
        "risk_note": (
            "Reads OHLCV bars and runs a deterministic paper backtest; crosses "
            "the current human-controlled real-data QA boundary. Present but "
            "NOT adopted."
        ),
    },
    {
        "name": "research_os/simulation_guard.py",
        "path": "research_os/simulation_guard.py",
        "kind": "dependency",
    },
    {
        "name": "paired tests",
        "path": "tests/",
        "kind": "tests",
    },
    {
        "name": "tests/conftest.py",
        "path": "tests/conftest.py",
        "kind": "conftest",
    },
)

# Plain-language reasons the arc is held (Bundle 162 finding).
HOLD_REASONS = (
    "It is a separate lineage from the committed Crypto-D1 RESEARCH_ONLY chain.",
    "It partly overlaps with committed Crypto-D1 modules.",
    "Phase 5 crosses the current boundary because it reads OHLCV and runs a "
    "deterministic paper backtest.",
    "The committed chain is still parked at "
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED.",
    "Partial adoption could break imports or fork the strategy factory into two "
    "competing lineages.",
)

# What this decision explicitly forbids until a whole-arc decision is made.
WHAT_REMAINS_FORBIDDEN = (
    "Adopting any single file from the arc.",
    "Deleting any single file from the arc.",
    "Wiring the arc into mission flow.",
    "Surfacing the arc in JARVIS as active.",
    "Staging any arc file; running 'git add .'.",
    "Advancing the mission-flow stage or next required action.",
    "Unlocking real_data_qa, baseline/backtest, or paper/micro-live.",
)


def _held_component_record(spec: dict[str, Any]) -> dict[str, Any]:
    """One fresh per-component HELD record. Held means: not adopted, not
    deleted, not staged, not active -- a coverage/decision note, never an
    adoption or deletion."""
    rec: dict[str, Any] = {
        "name": spec["name"],
        "path": spec["path"],
        "kind": spec["kind"],
        "held": True,
        "adopt_individually": False,
        "delete_individually": False,
        "staged": False,
        "active": False,
        "wired_into_mission_flow": False,
        "surfaced_in_jarvis_active": False,
        "highest_risk": bool(spec.get("highest_risk", False)),
        "status": "LOCAL_ONLY_UNTRACKED_HELD",
    }
    if "risk" in spec:
        rec["risk"] = spec["risk"]
    if "risk_note" in spec:
        rec["risk_note"] = spec["risk_note"]
    return rec


def build_offline_strategy_factory_arc_hold_decision() -> dict[str, Any]:
    """Build (fresh each call) the read-only Offline Strategy Factory Arc Hold
    Decision record. In-memory only: reads nothing, writes nothing."""
    components = [_held_component_record(c) for c in _ARC_COMPONENTS]
    record: dict[str, Any] = {
        "schema_version": DECISION_SCHEMA_VERSION,
        "label": DECISION_LABEL,
        "mode": DECISION_MODE,
        "status": DECISION_STATUS,
        "arc_id": ARC_ID,
        "verdict": VERDICT_HOLD_ARC,
        "arc_status": ARC_STATUS,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "phase5_component": PHASE5_COMPONENT_NAME,
        "phase5_risk": PHASE5_RISK,
        "component_count": len(components),
        "components": components,
        "hold_reasons": list(HOLD_REASONS),
        "what_remains_forbidden": list(WHAT_REMAINS_FORBIDDEN),
        "required_future_arc_level_decisions": list(
            REQUIRED_FUTURE_ARC_LEVEL_DECISIONS
        ),
        "stage": MISSION_FLOW_CURRENT_STAGE,
        "next_gate": MISSION_FLOW_CURRENT_STAGE,
        "next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "gate_states": dict(GATE_STATES),
        "reason": (
            "Read-only HOLD decision for the entire OFFLINE-STRATEGY-FACTORY "
            "arc. The Bundle 162 inventory found the inspected scaffolds are "
            "slices of a larger LOCAL-ONLY, untracked arc (a separate lineage "
            "from the committed Crypto-D1 RESEARCH_ONLY chain) that partly "
            "overlaps committed Crypto-D1 modules and whose Phase 5 runner "
            "reads OHLCV and runs a deterministic paper backtest -- crossing "
            "the current human-controlled real-data QA boundary. The arc is "
            "held as a whole: no single file is adopted, no single file is "
            "deleted, it is not wired into mission flow, it is not surfaced in "
            "JARVIS as active, and it is never staged. This authorizes nothing "
            "and executes nothing: it adopts nothing, deletes nothing, stages "
            "nothing, wires nothing, runs no backtest, reads no data, and "
            "writes nothing. It is purely additive read-only decision metadata: "
            "it does not advance the global stage, which remains the "
            "human-controlled real-data QA boundary decision, and is never an "
            "unlock of real_data_qa. A future explicit whole-arc decision "
            "(ADOPT_WHOLE_ARC / DELETE_WHOLE_ARC / IGNORE_WHOLE_ARC) is "
            "required; real_data_qa and baseline stay BLOCKED and the "
            "paper/micro-live gates stay LOCKED until then."
        ),
    }
    for flag in CAPABILITY_FLAGS:
        record[flag] = False
    return record


def validate_offline_strategy_factory_arc_hold_decision(
    record: dict[str, Any],
) -> bool:
    """Structurally validate a built record. Returns True only if every
    boundary-preserving, hold-only invariant holds."""
    if not isinstance(record, dict):
        return False
    if record.get("schema_version") != DECISION_SCHEMA_VERSION:
        return False
    if record.get("verdict") != VERDICT_HOLD_ARC:
        return False
    if record.get("arc_status") != ARC_STATUS:
        return False
    if record.get("executes") is not False:
        return False
    if record.get("stage") != MISSION_FLOW_CURRENT_STAGE:
        return False
    if record.get("next_required_action") != MISSION_FLOW_NEXT_REQUIRED_ACTION:
        return False
    if record.get("gate_states") != dict(GATE_STATES):
        return False
    if any(record.get(flag) is not False for flag in CAPABILITY_FLAGS):
        return False
    components = record.get("components")
    if not isinstance(components, list) or not components:
        return False
    phase5_seen = False
    for c in components:
        if not isinstance(c, dict):
            return False
        if c.get("held") is not True:
            return False
        if c.get("adopt_individually") is not False:
            return False
        if c.get("delete_individually") is not False:
            return False
        if c.get("staged") is not False:
            return False
        if c.get("active") is not False:
            return False
        if c.get("name") == PHASE5_COMPONENT_NAME:
            phase5_seen = True
            if c.get("highest_risk") is not True:
                return False
            if c.get("risk") != PHASE5_RISK:
                return False
    return phase5_seen


def render_offline_strategy_factory_arc_hold_decision_markdown(
    record: dict[str, Any] | None = None,
) -> str:
    """Render the decision as Markdown (in memory; writes nothing)."""
    rec = record if record is not None else (
        build_offline_strategy_factory_arc_hold_decision()
    )
    lines = [
        f"# {rec['label']}",
        "",
        f"**Verdict: {rec['verdict']}**  -  Arc status: {rec['arc_status']}  -  "
        f"Mode: {rec['mode']}",
        "",
        f"Arc: {rec['arc_id']}  ·  Stage: {rec['stage']}  ·  Next: "
        f"{rec['next_required_action']}",
        f"Phase 5 risk: {rec['phase5_risk']}",
        "",
        "## Held arc components",
        "",
    ]
    for c in rec["components"]:
        flag = "  ← HIGHEST RISK" if c.get("highest_risk") else ""
        lines.append(f"- {c['name']} ({c['kind']}) — HELD{flag}")
    lines += ["", "## Why held", ""]
    lines += [f"- {r}" for r in rec["hold_reasons"]]
    lines += ["", "## Remains forbidden", ""]
    lines += [f"- {r}" for r in rec["what_remains_forbidden"]]
    lines += ["", "## Required future decision (whole-arc only)", ""]
    lines += [f"- {d}" for d in rec["required_future_arc_level_decisions"]]
    lines += ["", "## Gates (preserved)", ""]
    lines += [f"- {k}: {v}" for k, v in rec["gate_states"].items()]
    return "\n".join(lines).strip() + "\n"
