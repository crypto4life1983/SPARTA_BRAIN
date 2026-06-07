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
  - LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT
  - LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT
  - LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT
  - LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT
  - LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT
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
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_selection_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION as STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_review_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_contract import (  # noqa: E501
    BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_review_contract import (  # noqa: E501
    RESEARCH_PLAN_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_contract import (  # noqa: E501
    RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_contract import (  # noqa: E501
    RESEARCH_DESIGN_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_review_contract import (  # noqa: E501
    RESEARCH_DESIGN_REVIEW_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_approval_contract import (  # noqa: E501
    RESEARCH_DESIGN_APPROVAL_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_readiness_contract import (  # noqa: E501
    RESEARCH_READINESS_SCHEMA_VERSION as STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_external_bot_evidence_intake_contract import (  # noqa: E501
    EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION as STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract import (  # noqa: E501
    WHALE_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_funding_rate_evidence_contract import (  # noqa: E501
    FUNDING_RATE_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract import (  # noqa: E501
    BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION as CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_research_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_review_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_approval_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION as CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract import (  # noqa: E501
    COHORT_INDEPENDENCE_SCHEMA_VERSION as CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract import (  # noqa: E501
    RDQ_BOUNDARY_SCHEMA_VERSION as CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_mission_flow_bundle_registry import (  # noqa: E501
    get_current_stage as _registry_current_stage,
    get_latest_completed_bundle_label as _registry_latest_bundle_label,
    get_latest_completed_protocol_label as _registry_latest_protocol_label,
    get_latest_completed_protocol_contract_label as _registry_latest_protocol_contract_label,  # noqa: E501
    get_latest_completed_family_selection_contract_label as _registry_latest_family_selection_contract_label,  # noqa: E501
    get_latest_completed_family_review_contract_label as _registry_latest_family_review_contract_label,  # noqa: E501
    get_latest_completed_research_plan_contract_label as _registry_latest_research_plan_contract_label,  # noqa: E501
    get_latest_completed_research_plan_review_contract_label as _registry_latest_research_plan_review_contract_label,  # noqa: E501
    get_latest_completed_research_plan_approval_contract_label as _registry_latest_research_plan_approval_contract_label,  # noqa: E501
    get_latest_completed_research_design_contract_label as _registry_latest_research_design_contract_label,  # noqa: E501
    get_latest_completed_research_design_review_contract_label as _registry_latest_research_design_review_contract_label,  # noqa: E501
    get_latest_completed_research_design_approval_contract_label as _registry_latest_research_design_approval_contract_label,  # noqa: E501
    get_latest_completed_research_readiness_contract_label as _registry_latest_research_readiness_contract_label,  # noqa: E501
    get_latest_completed_external_bot_evidence_intake_contract_label as _registry_latest_external_bot_evidence_intake_contract_label,  # noqa: E501
    get_latest_completed_hyperliquid_whale_evidence_contract_label as _registry_latest_hyperliquid_whale_evidence_contract_label,  # noqa: E501
    get_latest_completed_funding_rate_evidence_contract_label as _registry_latest_funding_rate_evidence_contract_label,  # noqa: E501
    get_latest_completed_bitcoin_cycle_timing_evidence_contract_label as _registry_latest_bitcoin_cycle_timing_evidence_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_research_contract_label as _registry_latest_daily_alpha_brief_research_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_review_contract_label as _registry_latest_daily_alpha_brief_review_contract_label,  # noqa: E501
    get_latest_completed_daily_alpha_brief_approval_contract_label as _registry_latest_daily_alpha_brief_approval_contract_label,  # noqa: E501
    get_latest_completed_cohort_independence_contract_label as _registry_latest_cohort_independence_contract_label,  # noqa: E501
    get_latest_completed_real_data_qa_boundary_decision_contract_label as _registry_latest_real_data_qa_boundary_decision_contract_label,  # noqa: E501
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
    "LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT",
    "LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT",
    "LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT",
    "LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT",
    "LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT",
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
LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT = (
    _registry_latest_family_selection_contract_label()
)
LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT = (
    _registry_latest_family_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT = (
    _registry_latest_research_plan_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT = (
    _registry_latest_research_plan_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT = (
    _registry_latest_research_plan_approval_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT = (
    _registry_latest_research_design_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT = (
    _registry_latest_research_design_review_contract_label()
)
LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT = (
    _registry_latest_research_design_approval_contract_label()
)
LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT = (
    _registry_latest_research_readiness_contract_label()
)
LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT = (
    _registry_latest_external_bot_evidence_intake_contract_label()
)
LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT = (
    _registry_latest_hyperliquid_whale_evidence_contract_label()
)
LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT = (
    _registry_latest_funding_rate_evidence_contract_label()
)
LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT = (
    _registry_latest_bitcoin_cycle_timing_evidence_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT = (
    _registry_latest_daily_alpha_brief_research_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT = (
    _registry_latest_daily_alpha_brief_review_contract_label()
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT = (
    _registry_latest_daily_alpha_brief_approval_contract_label()
)
LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT = (
    _registry_latest_cohort_independence_contract_label()
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT = (
    _registry_latest_real_data_qa_boundary_decision_contract_label()
)
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
            "Strategy Candidate Protocol v1, on paper), Block 97 BUILT the "
            "Strategy Candidate Protocol Contract that validates whether a "
            "proposed candidate plan follows it, Block 99 BUILT the "
            "Strategy Candidate Family Selection Contract that validates which "
            "of the four defined candidate strategy families a research-only "
            "selection packet scopes first, Block 101 BUILT the "
            "Strategy Candidate Family Review Contract that validates whether "
            "the selected/parked families are reasonable, Block 103 BUILT the "
            "Strategy Candidate Research Plan Contract that validates how the "
            "reviewed family selection would be researched before any real "
            "strategy research begins, Block 105 BUILT the Strategy Candidate "
            "Research Plan Review Contract that validates whether that research "
            "plan is reasonable, Block 107 BUILT the Strategy Candidate Research "
            "Plan Approval Contract that records the separate, later human "
            "approval the review READY gate requires, Block 109 BUILT the "
            "Strategy Candidate Research Design Contract that details how the "
            "approved research plan would be carried out before any real "
            "strategy research begins, Block 111 BUILT the Strategy Candidate "
            "Research Design Review Contract that reviews whether that research "
            "design is reasonable, Block 113 BUILT the Strategy Candidate "
            "Research Design Approval Contract that records the separate, later "
            "human approval the research-design-review READY gate requires, "
            "Block 115 BUILT the Strategy Candidate Research Readiness Contract "
            "that records, on paper, that the research-only paper chain is "
            "internally ready -- a final readiness paper gate before the still-"
            "blocked real_data_qa boundary -- Block 117 BUILT the "
            "External Bot Evidence Intake Contract that classifies external AI "
            "trading bot / tool / video ideas into research-only evidence buckets, "
            "Block 119 BUILT the Hyperliquid Whale Evidence Contract that "
            "classifies external Hyperliquid whale-tracking ideas into "
            "research-only evidence buckets, Block 121 BUILT the "
            "Funding Rate Evidence Contract that classifies external funding-rate "
            "scanner ideas into research-only evidence buckets, Block 123 BUILT "
            "the Bitcoin Cycle Timing Evidence Contract that converts the BTC "
            "364-day / 1064-day cycle idea into research-only timing evidence "
            "under the rule that cycle timing tells us when to pay attention, not "
            "when to buy, Block 125 BUILT the Daily Alpha Brief "
            "Research Contract that assembles a daily crypto alpha brief from "
            "already-approved static evidence inputs only (the external-bot, "
            "hyperliquid-whale, funding-rate, and bitcoin-cycle-timing evidence "
            "lanes), under the core rule that the brief tells us what to watch "
            "and research, never what to trade -- its highest stance is "
            "WATCH / RESEARCH_ONLY and it never produces a buy/sell/long/short/"
            "entry/exit/order instruction -- Block 127 BUILT the "
            "Daily Alpha Brief Review Contract that reviews whether an assembled "
            "brief is reasonable, still on paper, treating every input as "
            "external research evidence only; its highest verdict is READY for "
            "human approval and it never produces a trade instruction -- and "
            "Block 129 has now BUILT the Daily Alpha Brief Approval Contract that "
            "records, on paper, a human approval decision over a reviewed brief; "
            "its highest verdict is APPROVED, which only files the reviewed brief "
            "as a research record and never as a trade. With the research-only "
            "external-evidence sub-chain (research -> review -> approval) now "
            "complete, the only next step is the human-controlled real-data QA "
            "boundary decision -- a human judgment about whether to ever cross "
            "from research-only paper work into real-data QA. That boundary "
            "decision is not a build step and not an authorization: it fetches no "
            "data, runs no QA, baseline, or backtest, places no order, and writes "
            "no runtime artifact; real_data_qa stays BLOCKED unless a separate, "
            "future, human-approved boundary contract authorizes it. "
            "Nothing is authorized to run: real strategy intake remains paused for "
            "operator review."
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
        "state": STATE_COMPLETE,
        "reason": (
            "Block 99 complete ("
            + STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Family Selection Contract only. It "
            "only VALIDATES, on paper, which of the four defined candidate "
            "strategy families a research-only selection packet scopes first; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_family_review_contract",
        "label": "Crypto-D1 Strategy Candidate Family Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 101 complete ("
            + STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Family Review Contract only. It "
            "only REVIEWS, on paper, whether the candidate strategy families a "
            "research-only selection packet chose or parked are reasonable; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 103 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION + "). "
            "Read-only Strategy Candidate Research Plan Contract only. It only "
            "validates, on paper, how the reviewed family selection would be "
            "researched before any real strategy research begins; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_review_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 105 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Plan Review Contract "
            "only. It only reviews, on paper, whether the Block 103 research "
            "plan is reasonable before any real strategy research begins; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_plan_approval_contract",
        "label": "Crypto-D1 Strategy Candidate Research Plan Approval Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 107 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Plan Approval Contract "
            "only. It only records, on paper, the separate, later human approval "
            "the Block 105 research-plan review READY gate requires before any "
            "real strategy research begins; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_contract",
        "label": "Crypto-D1 Strategy Candidate Research Design Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 109 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Contract only. It "
            "only details, on paper, how the Block 107 approved research plan "
            "would be carried out before any real strategy research begins; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_review_contract",
        "label": "Crypto-D1 Strategy Candidate Research Design Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 111 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Review Contract "
            "only. It only records, on paper, a human review of whether the "
            "Block 109 research design is reasonable before any real strategy "
            "research begins; it authorizes nothing and executes nothing: no "
            "real data acquisition, data fetch, data inspection, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_design_approval_contract",
        "label": (
            "Crypto-D1 Strategy Candidate Research Design Approval Contract"
        ),
        "state": STATE_COMPLETE,
        "reason": (
            "Block 113 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Design Approval Contract "
            "only. It only records, on paper, the separate, later human approval "
            "the Block 111 research-design-review READY gate requires before any "
            "real strategy research begins; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_strategy_candidate_research_readiness_contract",
        "label": "Crypto-D1 Strategy Candidate Research Readiness Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 115 complete ("
            + STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION
            + "). Read-only Strategy Candidate Research Readiness Contract only. "
            "It only records, on paper, that the research-only paper chain is "
            "internally ready -- a final readiness paper gate before the still-"
            "blocked real_data_qa boundary; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked. Readiness is paper "
            "readiness ONLY: real_data_qa stays BLOCKED."
        ),
    },
    {
        "id": "crypto_d1_external_bot_evidence_intake_contract",
        "label": "Crypto-D1 External Bot Evidence Intake Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 117 complete ("
            + STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION
            + "). Read-only External Bot Evidence Intake Contract only. It only "
            "classifies external AI trading bot / tool / video ideas into "
            "research-only evidence buckets (useful_for_research, "
            "risky_requires_validation, blocked_execution_feature, "
            "dashboard_or_brief_candidate, ignore_or_marketing_claim), marking "
            "every execution-capable idea blocked and every attractive-but-"
            "unverified claim risky, and never converting evidence into "
            "permission; it authorizes nothing and executes nothing: no real data "
            "acquisition, data fetch, data inspection, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, market-data "
            "validation, order placement, broker, exchange, Telegram trade "
            "command, TradingView execution webhook, portfolio account control, "
            "live deployment, cloud bot operation, paper, live, automation, or "
            "runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_hyperliquid_whale_evidence_contract",
        "label": "Crypto-D1 Hyperliquid Whale Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 119 complete ("
            + CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Hyperliquid Whale Evidence Contract only. It only "
            "classifies external Hyperliquid whale-tracking ideas into research-"
            "only evidence buckets (useful_for_research, risky_requires_validation, "
            "blocked_execution_feature, ignore_or_marketing_claim, "
            "needs_independent_confirmation), marking every execution-capable whale "
            "idea blocked, every unverified whale movement claim risky, requiring "
            "independent confirmation, and never converting whale evidence into "
            "permission; it authorizes nothing and executes nothing: no Hyperliquid "
            "API connection, wallet monitoring, account/portfolio access, exchange "
            "connection, real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, copy/follow whale execution, whale alert automation, "
            "Telegram trade command, paper, live, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_funding_rate_evidence_contract",
        "label": "Crypto-D1 Funding Rate Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 121 complete ("
            + CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Funding Rate Evidence Contract only. It only "
            "classifies external funding-rate scanner ideas into research-"
            "only evidence buckets (useful_for_research, risky_requires_validation, "
            "blocked_execution_feature, ignore_or_marketing_claim, "
            "needs_independent_confirmation), marking every execution-capable "
            "funding idea blocked, every unverified funding-rate claim risky, "
            "requiring independent confirmation, and never converting funding-rate "
            "evidence into permission or 'free money'; it authorizes nothing and "
            "executes nothing: no exchange API connection, futures/perps account "
            "access, position opening, hedging, carry-trade execution, arbitrage "
            "execution, live funding monitor, real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper, live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_bitcoin_cycle_timing_evidence_contract",
        "label": "Crypto-D1 Bitcoin Cycle Timing Evidence Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 123 complete ("
            + CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Bitcoin Cycle Timing Evidence Contract only -- a "
            "higher-level macro timing filter inserted before the Daily Alpha "
            "Brief contract. It only converts the BTC 364-day / 1064-day cycle "
            "idea into research-only timing evidence (an early/active/late/expired "
            "cycle-bottom watch zone and a caution/accumulation-watch/recovery-"
            "watch/no-signal evidence stance), under the core rule that cycle "
            "timing tells us when to pay attention, not when to buy; it requires "
            "independent confirmation and never converts timing evidence into "
            "permission or a buy instruction; it authorizes nothing and executes "
            "nothing: no BTC data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper, live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_research_contract",
        "label": "Crypto-D1 Daily Alpha Brief Research Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 125 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Research Contract only. It only "
            "assembles, on paper, a daily crypto alpha brief from already-"
            "approved static evidence inputs only (the external-bot, hyperliquid-"
            "whale, funding-rate, and bitcoin-cycle-timing evidence lanes) into a "
            "deterministic structured brief with an overall research decision and "
            "stance, under the core rule that the brief tells us what to watch and "
            "research, never what to trade. Its highest stance is WATCH / "
            "RESEARCH_ONLY and it never produces a buy/sell/long/short/entry/exit/"
            "order instruction; every input is treated as external research "
            "evidence only, always requires independent confirmation, and is never "
            "converted into permission. It authorizes nothing and executes "
            "nothing: no data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_review_contract",
        "label": "Crypto-D1 Daily Alpha Brief Review Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 127 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Review Contract only. It only "
            "reviews, on paper, whether an assembled daily crypto alpha brief is "
            "reasonable -- derived from already-approved static evidence inputs "
            "only (the external-bot, hyperliquid-whale, funding-rate, and bitcoin-"
            "cycle-timing evidence lanes) -- and emits a research verdict, under "
            "the core rule that the review tells us whether the brief is "
            "reasonable to escalate for human approval, never what to trade. Its "
            "highest verdict is READY and it never produces a buy/sell/long/short/"
            "entry/exit/order instruction; every input is treated as external "
            "research evidence only, always requires independent confirmation, and "
            "is never converted into permission. It authorizes nothing and "
            "executes nothing: no data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked."
        ),
    },
    {
        "id": "crypto_d1_daily_alpha_brief_approval_contract",
        "label": "Crypto-D1 Daily Alpha Brief Approval Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 129 complete ("
            + CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION
            + "). Read-only Daily Alpha Brief Approval Contract only. It only "
            "records, on paper, a human approval decision over a reviewed daily "
            "crypto alpha brief -- derived from already-approved static evidence "
            "inputs only (the external-bot, hyperliquid-whale, funding-rate, and "
            "bitcoin-cycle-timing evidence lanes) -- under the core rule that an "
            "approval only files the reviewed brief as a research record, never "
            "what to trade. Its highest verdict is APPROVED and it never produces "
            "a buy/sell/long/short/entry/exit/order instruction; every input is "
            "treated as external research evidence only, always requires "
            "independent confirmation, and is never converted into permission. It "
            "authorizes nothing and executes nothing: no data fetch, API call, "
            "dataset inspection, real data acquisition, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked."
        ),
    },
    {
        "id": "crypto_d1_cohort_independence_correlation_penalty_contract",
        "label": "Crypto-D1 Cohort Independence / Correlation Penalty Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 132 complete ("
            + CRYPTO_D1_COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION
            + "). Read-only Cohort Independence / Correlation Penalty Contract "
            "only -- a research-only evidence/scoring support contract. It only "
            "scores, on paper, whether a set of already-booked paper positions "
            "forms genuinely independent cohorts or merely correlated/duplicate "
            "ones (sharing symbol+direction, macro event, market regime, open/"
            "close timing window, or signal family) and reports whether the "
            "independent-booked-cohort sample can SUPPORT a promote-to-review "
            "judgment, under the core rule that it scores evidence independence, "
            "never what to trade. Its highest output is a research-support signal "
            "(can_support_promote_to_review) and it never produces a buy/sell/long/"
            "short/entry/exit/order instruction; every input is treated as static "
            "research evidence only, always requires independent confirmation, and "
            "is never converted into permission. It authorizes nothing and "
            "executes nothing: no data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "crypto_d1_real_data_qa_boundary_decision_contract",
        "label": "Crypto-D1 Real Data QA Boundary Decision Contract",
        "state": STATE_COMPLETE,
        "reason": (
            "Block 134 complete ("
            + CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION
            + "). Read-only Real Data QA Boundary Decision Contract only -- the "
            "research-only paper contract that defines the structured human "
            "decision packet/gate reviewed BEFORE any Real Data QA may even be "
            "planned. It only assigns, on paper, a static evidence summary exactly "
            "one outcome (BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_DECISION) and "
            "assembles that packet for a human, under the core rule that it readies "
            "a human decision, never what to trade and never an unlock. Its highest "
            "outcome is READY_FOR_HUMAN_DECISION and it never produces a buy/sell/"
            "long/short/entry/exit/order instruction; every input is treated as "
            "static research evidence only, always requires independent "
            "confirmation, and is never converted into permission. It authorizes "
            "nothing and executes nothing: no data fetch, API call, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Recognizing it is purely additive latest-completed "
            "metadata: it does not advance the stage past the human-controlled "
            "real-data QA boundary."
        ),
    },
    {
        "id": "human_controlled_real_data_qa_boundary_decision",
        "label": "Human-Controlled Real Data QA Boundary Decision",
        "state": STATE_NEXT,
        "reason": (
            "Next required action: " + NEXT_REQUIRED_ACTION + ". With the Block "
            "129 daily alpha brief approval contract now complete, the research-"
            "only external-evidence sub-chain (research -> review -> approval) is "
            "finished and the only next step is the human-controlled real-data QA "
            "boundary decision: a human judgment about whether to ever cross from "
            "research-only paper work into real-data QA. It is NOT a build step "
            "and NOT an authorization -- it acquires no data, runs no dry run, QA, "
            "baseline, or backtest, places no order, automates nothing, and writes "
            "no runtime/registry/dashboard artifact. real_data_qa stays BLOCKED "
            "unless a separate, future, human-approved boundary contract "
            "authorizes it."
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
        "latest_completed_family_selection_contract": LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT,  # noqa: E501
        "latest_completed_family_review_contract": LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_contract": LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_review_contract": LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_plan_approval_contract": LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_research_design_contract": LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT,  # noqa: E501
        "latest_completed_research_design_review_contract": LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_research_design_approval_contract": LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_research_readiness_contract": LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT,  # noqa: E501
        "latest_completed_external_bot_evidence_intake_contract": LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT,  # noqa: E501
        "latest_completed_hyperliquid_whale_evidence_contract": LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_funding_rate_evidence_contract": LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_bitcoin_cycle_timing_evidence_contract": LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_research_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_review_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT,  # noqa: E501
        "latest_completed_daily_alpha_brief_approval_contract": LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT,  # noqa: E501
        "latest_completed_cohort_independence_contract": LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT,  # noqa: E501
        "latest_completed_real_data_qa_boundary_decision_contract": LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT,  # noqa: E501
        "next_required_action": NEXT_REQUIRED_ACTION,
        "safety_posture": dict(MISSION_FLOW_SAFETY_POSTURE),
        "human_workflow": human_workflow_lane(),
        "machine_pipeline": machine_pipeline_lane(),
        "blocked_gates": blocked_gates(),
        "safety": safety_flags(),
    }
