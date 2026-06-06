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

The snapshot is derived from the known, committed contract/checkpoint state of
the Strategy Factory backbone as of Bundle 54 (Crypto-D1 research-only dry-run
research archive or closure contract complete, which closes the research-only
dry-run lane) plus the recognized Crypto-D1 Strategy Candidate Protocol v1
(defined on paper in Block 95) and the recognized Crypto-D1 Strategy Candidate
Protocol Contract (built on paper in Block 97). It requires no IO to produce the
default status. Reaching any
stage in this map unlocks nothing real: every downstream real-world capability
(real data, QA, baseline, backtest, paper, live, broker, exchange, automation,
runtime/registry/dashboard writes) stays blocked and human-gated. Bundle 54
only means the research-only dry-run research archive or closure *contract*
exists on paper; it authorizes nothing and executes nothing: no dry-run
execution, data acquisition, data fetch, data inspection, QA, baseline,
backtest, paper/live, broker/exchange, or automation is unlocked.

Public API:
  - MISSION_FLOW_VERSION
  - MISSION_FLOW_MODE
  - MISSION_FLOW_SAFETY_POSTURE
  - STATE_PASSED / STATE_COMPLETE / STATE_CURRENT / STATE_NEXT
  - STATE_BLOCKED / STATE_LOCKED / STATE_PARKED
  - CURRENT_STAGE
  - LATEST_COMPLETED_BUNDLE
  - LATEST_COMPLETED_PROTOCOL
  - LATEST_COMPLETED_PROTOCOL_CONTRACT
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
)
from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    SOURCE_CLASS_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
    SPEC_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
    PLAN_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
    GATE_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract import (  # noqa: E501
    BOUNDARY_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract import (  # noqa: E501
    NEXT_STEP_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
    PREVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_review_contract import (  # noqa: E501
    REVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_contract import (  # noqa: E501
    DECISION_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_review_contract import (  # noqa: E501
    DECISION_REVIEW_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract import (  # noqa: E501
    FINAL_DECISION_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract import (  # noqa: E501
    ARCHIVE_OR_CLOSURE_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (  # noqa: E501
    PROTOCOL_SCHEMA_VERSION as NEXT_RESEARCH_PROTOCOL_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_protocol_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION as STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_mission_flow_bundle_registry import (  # noqa: E501
    get_current_stage as _registry_current_stage,
    get_latest_completed_bundle_label as _registry_latest_bundle_label,
    get_latest_completed_protocol_label as _registry_latest_protocol_label,
    get_latest_completed_protocol_contract_label as _registry_latest_protocol_contract_label,  # noqa: E501
    get_next_required_action as _registry_next_required_action,
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
    "LATEST_COMPLETED_PROTOCOL",
    "LATEST_COMPLETED_PROTOCOL_CONTRACT",
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

# Derived from the read-only bundle registry (single source of truth) so the
# mission-flow feed follows the pipeline from structured metadata instead of a
# hardcoded bundle list. Values are equivalent to the prior hardcoded ones.
CURRENT_STAGE = _registry_current_stage()
LATEST_COMPLETED_BUNDLE = _registry_latest_bundle_label()
LATEST_COMPLETED_PROTOCOL = _registry_latest_protocol_label()
LATEST_COMPLETED_PROTOCOL_CONTRACT = _registry_latest_protocol_contract_label()
NEXT_REQUIRED_ACTION = _registry_next_required_action()

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
        "reason": "Strategy Factory backbone (Bundles 11-54) complete on paper.",
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
            "You are here. Bundles 42-54 contract chain is complete on paper, "
            "through the Crypto-D1 research-only dry-run research archive or "
            "closure contract, which closes the research-only dry-run lane. "
            "Block 95 DEFINED the next research-only protocol (Crypto-D1 "
            "Strategy Candidate Protocol v1, on paper) and Block 97 has now "
            "BUILT the Strategy Candidate Protocol Contract that validates "
            "whether a proposed candidate plan follows it. The only next step "
            "is a research-only planning step: BUILD the candidate-family-"
            "selection contract, still on paper. Nothing is authorized to run: "
            "real strategy intake remains paused for operator review."
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
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 43 complete (" + SOURCE_CLASS_SCHEMA_VERSION + "). "
            "Read-only source-class paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_source_specification_contract",
        "label": "Crypto-D1 Source Specification Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 44 complete (" + SPEC_SCHEMA_VERSION + "). Read-only "
            "source-specification paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_offline_acquisition_plan_contract",
        "label": "Crypto-D1 Offline Acquisition Plan Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 45 complete (" + PLAN_SCHEMA_VERSION + "). Read-only "
            "offline-acquisition-plan paper contract; acquires no data."
        ),
    },
    {
        "id": "crypto_d1_pre_acquisition_human_gate_contract",
        "label": "Crypto-D1 Pre-Acquisition Human Approval Gate",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 46 complete (" + GATE_SCHEMA_VERSION + "). Read-only "
            "human-approval-gate paper contract only. It defines the gate but "
            "authorizes nothing: no data acquisition, QA, baseline, backtest, "
            "simulation, paper, broker, exchange, or automation is unlocked."
        ),
    },
    {
        "id": "crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
        "label": "Crypto-D1 Human-Approved Offline Acquisition Execution Boundary Contract",  # noqa: E501
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 47 complete (" + BOUNDARY_SCHEMA_VERSION + "). Read-only "
            "execution-boundary paper contract only. It authorizes nothing and "
            "executes nothing: no data acquisition, data fetch, data "
            "inspection, QA, baseline, backtest, simulation, paper, live, "
            "broker, exchange, or automation is unlocked."
        ),
    },
    {
        "id": "crypto_d1_post_boundary_research_only_next_step_contract",
        "label": "Crypto-D1 Post-Boundary Research-Only Next-Step Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 48 complete (" + NEXT_STEP_SCHEMA_VERSION + "). Read-only "
            "post-boundary next-step paper contract only. It only DECIDES which "
            "research-only, dry-run-preview-only contract is built next; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, QA, baseline, backtest, simulation, "
            "paper, live, broker, exchange, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_preview_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Preview Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 49 complete (" + PREVIEW_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run PREVIEW paper contract only. It only "
            "PREVIEWS, on paper, what a research-only dry run would look like; "
            "it authorizes nothing and executes nothing: no dry-run execution, "
            "no real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_review_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 50 complete (" + REVIEW_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run REVIEW paper contract only. It only REVIEWS, "
            "on paper, what a research-only dry-run preview produced; it "
            "authorizes nothing and executes nothing: no dry-run execution, no "
            "real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_decision_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 51 complete (" + DECISION_SCHEMA_VERSION + "). Read-only "
            "research-only dry-run DECISION paper contract only. It only "
            "DECIDES, on paper, what a research-only dry-run review produced and "
            "which research-only dry-run-decision-review-only contract is built "
            "next; it authorizes nothing and executes nothing: no dry-run "
            "execution, no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_decision_review_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Decision Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 52 complete (" + DECISION_REVIEW_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run DECISION REVIEW paper contract "
            "only. It only REVIEWS, on paper, what a research-only dry-run "
            "decision produced and which research-only dry-run-final-decision-"
            "only contract is built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_final_decision_contract",
        "label": "Crypto-D1 Research-Only Dry-Run Final Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 53 complete (" + FINAL_DECISION_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run FINAL DECISION paper contract "
            "only. It only FINALIZES, on paper, the research-only dry-run "
            "decision and which research-only research-archive-or-closure-only "
            "contract is built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_dry_run_research_archive_or_closure_contract",  # noqa: E501
        "label": "Crypto-D1 Research-Only Dry-Run Research Archive or Closure Contract",  # noqa: E501
        "state": STATE_COMPLETE,
        "reason": (
            "Bundle 54 complete (" + ARCHIVE_OR_CLOSURE_SCHEMA_VERSION + "). "
            "Read-only research-only dry-run RESEARCH ARCHIVE OR CLOSURE paper "
            "contract only. It only records, on paper, whether the research-"
            "only dry-run lane should be ARCHIVED or CLOSED, which closes the "
            "Crypto-D1 research-only dry-run lane; it authorizes nothing and "
            "executes nothing: no dry-run execution, no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_research_only_next_protocol_definition",
        "label": "Crypto-D1 Research-Only Next Protocol Definition",
        "state": STATE_COMPLETE,
        "reason": (
            "Protocol defined (" + NEXT_RESEARCH_PROTOCOL_SCHEMA_VERSION + "). "
            "The Crypto-D1 Strategy Candidate Protocol v1 is DEFINED on paper "
            "(BTC/ETH/SOL, spot, daily candles, four candidate strategy "
            "families); it authorizes nothing and executes nothing: no real "
            "data acquisition, data fetch, data inspection, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, market-data "
            "validation, paper/live, broker/exchange, automation, or runtime/"
            "registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_protocol_contract",
        "label": "Crypto-D1 Strategy Candidate Protocol Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 97 complete ("
            + STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Protocol Contract only. It only "
            "VALIDATES, on paper, whether a proposed candidate plan follows the "
            "Crypto-D1 Strategy Candidate Protocol v1; it authorizes nothing and "
            "executes nothing: no real data acquisition, data fetch, data "
            "inspection, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, market-data validation, paper, live, broker, "
            "exchange, automation, or runtime/registry/dashboard write is "
            "unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_family_selection_contract",
        "label": "Crypto-D1 Strategy Candidate Family Selection Contract",
        "state": STATE_NEXT,
        "reason": (
            "Next required action: " + NEXT_REQUIRED_ACTION + ". The next step "
            "is a research-only planning step: BUILD the Crypto-D1 candidate-"
            "family-selection contract that, on paper, scopes which of the four "
            "defined candidate strategy families to research first. Building it "
            "acquires no data, runs no dry run, QA, baseline, or backtest, and "
            "executes nothing."
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
        "latest_completed_protocol": LATEST_COMPLETED_PROTOCOL,
        "latest_completed_protocol_contract": LATEST_COMPLETED_PROTOCOL_CONTRACT,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "safety_posture": dict(MISSION_FLOW_SAFETY_POSTURE),
        "human_workflow": human_workflow_lane(),
        "machine_pipeline": machine_pipeline_lane(),
        "blocked_gates": blocked_gates(),
        "safety": safety_flags(),
    }
