"""SPARTA Offline Strategy Factory - MISSION FLOW STATUS ADAPTER.

A PURE, stdlib-only *read-only display/status adapter* for the JARVIS Strategy
Factory "Mission Flow" panel. It derives a deterministic, plain-data snapshot of
where the Strategy Factory backbone currently stands -- which human workflow
stages and machine pipeline stages are complete, which is current, what the
single next required action is, and which downstream gates remain blocked or
locked. It is a *map of state*, not a controller.

It executes NOTHING. It does not run the Strategy Factory, does not acquire,
fetch, inspect, load, validate, transform, or compute on any data, does not run
QA, does not run a baseline, does not backtest, does not simulate, does not
touch any broker / exchange / order / trading / paper / live / distribution /
autopilot surface, triggers no automation, promotes/deploys nothing, records no
approval decision, writes no file, reads no file, lists no directory, opens no
network, spawns no subprocess, reads no environment, mints no id, records no
timestamp, and dynamically imports nothing.

The snapshot is hardcoded from the known, committed contract/checkpoint state of
the Strategy Factory backbone as of Bundle 42 (Crypto-D1 acquire decision
contract complete). It requires no IO to produce the default status. Reaching
any stage in this map unlocks nothing real: every downstream real-world
capability (real data, QA, baseline, backtest, paper, live, broker, exchange,
automation, runtime/registry/dashboard writes) stays blocked and human-gated.

Public API:
  - MISSION_FLOW_VERSION
  - MISSION_FLOW_MODE
  - MISSION_FLOW_SAFETY_POSTURE
  - STATE_PASSED / STATE_COMPLETE / STATE_CURRENT / STATE_NEXT
  - STATE_BLOCKED / STATE_LOCKED / STATE_PARKED
  - CURRENT_STAGE
  - LATEST_COMPLETED_BUNDLE
  - NEXT_REQUIRED_ACTION
  - human_workflow_lane()
  - machine_pipeline_lane()
  - blocked_gates()
  - safety_flags()
  - get_mission_flow_status()
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_SCHEMA_VERSION,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED,
)

__all__ = [
    "MISSION_FLOW_VERSION",
    "MISSION_FLOW_MODE",
    "MISSION_FLOW_SAFETY_POSTURE",
    "STATE_PASSED",
    "STATE_COMPLETE",
    "STATE_CURRENT",
    "STATE_NEXT",
    "STATE_BLOCKED",
    "STATE_LOCKED",
    "STATE_PARKED",
    "CURRENT_STAGE",
    "LATEST_COMPLETED_BUNDLE",
    "NEXT_REQUIRED_ACTION",
    "human_workflow_lane",
    "machine_pipeline_lane",
    "blocked_gates",
    "safety_flags",
    "get_mission_flow_status",
]

MISSION_FLOW_VERSION = "v1"
MISSION_FLOW_MODE = "RESEARCH_ONLY"

# Read-only safety posture: nothing here can execute or mutate anything.
MISSION_FLOW_SAFETY_POSTURE = {
    "mode": MISSION_FLOW_MODE,
    "read_only": True,
    "executes": False,
    "human_approval_required": True,
    "acquires_data": False,
    "inspects_data": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "touches_broker_or_exchange": False,
    "paper_or_live": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "refreshes_dashboard_snapshot": False,
}

# Per-stage status vocabulary (display-only labels).
STATE_PASSED = "PASSED"
STATE_COMPLETE = "COMPLETE"
STATE_CURRENT = "CURRENT"
STATE_NEXT = "NEXT"
STATE_BLOCKED = "BLOCKED"
STATE_LOCKED = "LOCKED"
STATE_PARKED = "PARKED"

CURRENT_STAGE = "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
LATEST_COMPLETED_BUNDLE = (
    "Bundle 42 - Crypto-D1 Acquire Decision Contract (read-only template)"
)
NEXT_REQUIRED_ACTION = NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED

# --- human workflow lane ---------------------------------------------------

_HUMAN_WORKFLOW: tuple[dict[str, str], ...] = (
    {
        "id": "idea_intake",
        "label": "Idea Intake",
        "state": STATE_PASSED,
        "reason": "Strategy ideas captured on paper in the research registry.",
    },
    {
        "id": "research_review",
        "label": "Research Review",
        "state": STATE_PASSED,
        "reason": "Research patterns reviewed; advisory-only, no execution.",
    },
    {
        "id": "candidate_creation",
        "label": "Candidate Creation",
        "state": STATE_PASSED,
        "reason": "Paper candidate strategies described in the registry.",
    },
    {
        "id": "backbone_build",
        "label": "Backbone Build",
        "state": STATE_COMPLETE,
        "reason": "Strategy Factory backbone (Bundles 11-42) complete on paper.",
    },
    {
        "id": "fake_lane",
        "label": "Fake Lane",
        "state": STATE_COMPLETE,
        "reason": "Fake-only dry-walk / report / closure lane complete; no real data used.",  # noqa: E501
    },
    {
        "id": "operator_review_before_real_strategy_intake",
        "label": "Operator Review Before Real Strategy Intake",
        "state": STATE_CURRENT,
        "reason": (
            "You are here. Bundle 42 acquire-decision contract is complete; "
            "next is a Crypto-D1 source-class contract template, still on "
            "paper. Real strategy intake remains paused for operator review."
        ),
    },
    {
        "id": "real_strategy_intake",
        "label": "Real Strategy Intake",
        "state": STATE_BLOCKED,
        "reason": "Blocked - not started. Requires explicit human approval; never automated.",  # noqa: E501
    },
)

# --- machine pipeline lane -------------------------------------------------

_MACHINE_PIPELINE: tuple[dict[str, str], ...] = (
    {
        "id": "strategy_factory_backbone",
        "label": "Strategy Factory Backbone",
        "state": STATE_COMPLETE,
        "reason": "Read-only contract backbone in place; executes nothing.",
    },
    {
        "id": "fake_dry_walk",
        "label": "Fake Dry Walk",
        "state": STATE_COMPLETE,
        "reason": "Deterministic fake walk produced on paper; no real data.",
    },
    {
        "id": "fake_report_renderer",
        "label": "Fake Report Renderer",
        "state": STATE_COMPLETE,
        "reason": "Fake report rendered from in-memory fixtures only.",
    },
    {
        "id": "fake_lane_closure",
        "label": "Fake Lane Closure",
        "state": STATE_COMPLETE,
        "reason": "Fake-only lane closed; no real-data capability unlocked.",
    },
    {
        "id": "crypto_d1_intake_reconciliation",
        "label": "Crypto-D1 Intake Reconciliation",
        "state": STATE_COMPLETE,
        "reason": "Bundle 41 reconciliation contract template complete on paper.",  # noqa: E501
    },
    {
        "id": "crypto_d1_acquire_decision_contract",
        "label": "Crypto-D1 Acquire Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 42 complete (" + ACQUIRE_SCHEMA_VERSION + "). Read-only "
            "acquire-decision template; acquires nothing, decides nothing."
        ),
    },
    {
        "id": "crypto_d1_source_class_contract",
        "label": "Crypto-D1 Source Class Contract",
        "state": STATE_NEXT,
        "reason": (
            "Next required action: "
            + NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED
            + ". Another read-only paper contract template; acquires no data."
        ),
    },
    {
        "id": "real_data_qa",
        "label": "Real Data QA",
        "state": STATE_BLOCKED,
        "reason": "Blocked - no real data acquired; QA never run.",
    },
    {
        "id": "baseline_backtest",
        "label": "Baseline Backtest",
        "state": STATE_BLOCKED,
        "reason": "Blocked - depends on real data + passed QA; never run.",
    },
    {
        "id": "paper_trading_gate",
        "label": "Paper Trading Gate",
        "state": STATE_LOCKED,
        "reason": "Locked - human approval required; never automated.",
    },
    {
        "id": "micro_live_gate",
        "label": "Micro-Live Gate",
        "state": STATE_LOCKED,
        "reason": "Locked - never automated; explicit human action only.",
    },
)

# --- blocked / locked downstream gates -------------------------------------

_BLOCKED_GATES: tuple[dict[str, str], ...] = (
    {
        "id": "real_strategy_intake",
        "label": "Real Strategy Intake",
        "state": STATE_BLOCKED,
        "reason": "Not started; requires explicit human approval.",
    },
    {
        "id": "real_data_qa",
        "label": "Real Data QA",
        "state": STATE_BLOCKED,
        "reason": "No real data acquired; QA never run.",
    },
    {
        "id": "baseline_backtest",
        "label": "Baseline Backtest",
        "state": STATE_BLOCKED,
        "reason": "Depends on real data and a passed QA verdict; never run.",
    },
    {
        "id": "paper_trading_gate",
        "label": "Paper Trading Gate",
        "state": STATE_LOCKED,
        "reason": "Human approval required before any paper trading.",
    },
    {
        "id": "micro_live_gate",
        "label": "Micro-Live Gate",
        "state": STATE_LOCKED,
        "reason": "Never automated; explicit human action only.",
    },
)

# Real-world capabilities that no stage in this map unlocks.
_SAFETY_FLAGS: dict[str, bool] = {
    "real_data": False,
    "qa": False,
    "baseline": False,
    "backtest": False,
    "simulation": False,
    "paper": False,
    "live": False,
    "broker": False,
    "exchange": False,
    "automation": False,
    "runtime_writes": False,
    "registry_writes": False,
    "dashboard_writes": False,
}


def _clone(rows: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    """Return a fresh, mutation-safe copy of static lane rows."""
    return [dict(row) for row in rows]


def human_workflow_lane() -> list[dict[str, str]]:
    """The human workflow lane (display-only stage list)."""
    return _clone(_HUMAN_WORKFLOW)


def machine_pipeline_lane() -> list[dict[str, str]]:
    """The machine pipeline lane (display-only stage list)."""
    return _clone(_MACHINE_PIPELINE)


def blocked_gates() -> list[dict[str, str]]:
    """Downstream gates that remain blocked or locked (display-only)."""
    return _clone(_BLOCKED_GATES)


def safety_flags() -> dict[str, bool]:
    """Real-world capability flags; all False (nothing is unlocked)."""
    return dict(_SAFETY_FLAGS)


def get_mission_flow_status() -> dict[str, Any]:
    """Deterministic, read-only mission-flow snapshot (no IO required)."""
    return {
        "mission_flow_version": MISSION_FLOW_VERSION,
        "mode": MISSION_FLOW_MODE,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "current_stage": CURRENT_STAGE,
        "latest_completed_bundle": LATEST_COMPLETED_BUNDLE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "safety_posture": dict(MISSION_FLOW_SAFETY_POSTURE),
        "human_workflow": human_workflow_lane(),
        "machine_pipeline": machine_pipeline_lane(),
        "blocked_gates": blocked_gates(),
        "safety": safety_flags(),
    }
