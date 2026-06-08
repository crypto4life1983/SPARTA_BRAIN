"""SPARTA Offline Strategy Factory - MISSION FLOW BUNDLE REGISTRY.

A PURE, stdlib-only *read-only* registry of completed Strategy Factory bundle
metadata. It is the single, deterministic source of truth for *which* paper
contract bundles exist and are complete, so the JARVIS Mission Flow feed can
follow the pipeline from structured metadata instead of hardcoding each bundle
inline.

It executes NOTHING. It does not run the Strategy Factory, does not acquire,
fetch, inspect, load, validate, transform, or compute on any data, does not run
QA, does not run a baseline, does not backtest, does not simulate, does not
touch any broker / exchange / order / trading / paper / live surface, triggers
no automation, writes no file, reads no file, lists no directory, opens no
network, spawns no subprocess, reads no environment, mints no id, records no
timestamp, and dynamically imports nothing. It only imports each completed
bundle module to read its stable schema-version constant.

Every registered bundle is a RESEARCH_ONLY paper contract: read_only True,
executes False, authorizes no real-world action, and unlocks no real data, QA,
baseline, backtest, paper/live, broker/exchange, automation, or any write. The
registry itself never writes to disk; "registry writes" stay blocked.

Public API:
  - REGISTRY_VERSION
  - REGISTRY_MODE
  - REGISTRY_SAFETY_POSTURE
  - CURRENT_STAGE
  - NEXT_REQUIRED_ACTION
  - list_registered_bundles()
  - list_completed_bundles()
  - get_latest_completed_bundle()
  - get_bundle_by_number(number)
  - get_bundle_by_id(bundle_id)
  - get_latest_completed_bundle_label()
  - get_current_stage()
  - get_next_required_action()
  - get_registry_safety_posture()
  - LATEST_COMPLETED_PROTOCOL
  - get_latest_completed_protocol()
  - get_latest_completed_protocol_label()
  - LATEST_COMPLETED_PROTOCOL_CONTRACT
  - get_latest_completed_protocol_contract()
  - get_latest_completed_protocol_contract_label()
  - LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT
  - get_latest_completed_family_selection_contract()
  - get_latest_completed_family_selection_contract_label()
  - LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT
  - get_latest_completed_family_review_contract()
  - get_latest_completed_family_review_contract_label()
  - LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT
  - get_latest_completed_research_plan_contract()
  - get_latest_completed_research_plan_contract_label()
  - LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT
  - get_latest_completed_research_plan_review_contract()
  - get_latest_completed_research_plan_review_contract_label()
  - LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT
  - get_latest_completed_research_plan_approval_contract()
  - get_latest_completed_research_plan_approval_contract_label()
  - LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT
  - get_latest_completed_research_design_contract()
  - get_latest_completed_research_design_contract_label()
  - LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER
  - get_latest_completed_overnight_research_autopilot_controller()
  - get_latest_completed_overnight_research_autopilot_controller_label()
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
# The next-research-protocol module (Block 95) imports ONLY __future__ and
# typing -- it does not import this registry -- so reading its stable constants
# at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (  # noqa: E501
    PROTOCOL_ID as _PROTOCOL_ID,
    PROTOCOL_NAME as _PROTOCOL_NAME,
    PROTOCOL_MODE as _PROTOCOL_MODE,
    PROTOCOL_SCHEMA_VERSION as _PROTOCOL_SCHEMA_VERSION,
    RESEARCH_UNIVERSE as _PROTOCOL_UNIVERSE,
    MARKET_TYPE as _PROTOCOL_MARKET_TYPE,
    TIMEFRAME as _PROTOCOL_TIMEFRAME,
    NEXT_REQUIRED_ACTION as _PROTOCOL_NEXT_ACTION,
    get_candidate_strategy_families as _protocol_candidate_families,
)
# The Block 97 strategy-candidate-protocol-contract module imports only
# __future__, typing, and the Block 95 protocol module (which itself imports
# only __future__ and typing); it does NOT import this registry, so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_protocol_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION as _PROTOCOL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 99 strategy-candidate-family-selection-contract module imports only
# __future__, typing, the Block 95 protocol module, and the Block 97 protocol-
# contract module (none of which import this registry); it does NOT import this
# registry, so reading its stable schema constant at module top is cycle-safe
# (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_selection_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION as _FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 101 strategy-candidate-family-review-contract module imports only
# __future__, typing, the Block 95 protocol module, the Block 97 protocol-
# contract module, and the Block 99 family-selection-contract module (none of
# which import this registry); it does NOT import this registry, so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_review_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION as _FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 103 strategy-candidate-research-plan-contract module imports only
# __future__, typing, the Block 95 protocol module, the Block 97 protocol-
# contract module, the Block 99 family-selection-contract module, and the Block
# 101 family-review-contract module (none of which import this registry); it
# does NOT import this registry, so reading its stable schema constant at module
# top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_contract import (  # noqa: E501
    BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION as _RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 105 strategy-candidate-research-plan-review-contract module imports
# only __future__, typing, the Block 95 protocol module, the Block 97 protocol-
# contract module, the Block 99 family-selection-contract module, the Block 101
# family-review-contract module, and the Block 103 research-plan-contract module
# (none of which import this registry); it does NOT import this registry, so
# reading its stable schema constant at module top is cycle-safe (no circular
# import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_review_contract import (  # noqa: E501
    RESEARCH_PLAN_REVIEW_SCHEMA_VERSION as _RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 107 strategy-candidate-research-plan-approval-contract module imports
# only __future__, typing, the Block 95 protocol module, the Block 97 protocol-
# contract module, the Block 99 family-selection-contract module, the Block 101
# family-review-contract module, the Block 103 research-plan-contract module, and
# the Block 105 research-plan-review-contract module (none of which import this
# registry); it does NOT import this registry, so reading its stable schema
# constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_contract import (  # noqa: E501
    RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION as _RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 109 strategy-candidate-research-design-contract module imports only
# __future__, typing, and the prior chain modules (Block 95 protocol through
# Block 107 research-plan-approval-contract), none of which import this registry;
# it does NOT import this registry, so reading its stable schema constant at
# module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_contract import (  # noqa: E501
    RESEARCH_DESIGN_SCHEMA_VERSION as _RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_review_contract import (  # noqa: E501
    RESEARCH_DESIGN_REVIEW_SCHEMA_VERSION as _RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_design_approval_contract import (  # noqa: E501
    RESEARCH_DESIGN_APPROVAL_SCHEMA_VERSION as _RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_readiness_contract import (  # noqa: E501
    RESEARCH_READINESS_SCHEMA_VERSION as _RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 117 external-bot-evidence-intake contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_external_bot_evidence_intake_contract import (  # noqa: E501
    EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION as _EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 119 Hyperliquid-whale-evidence contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract import (  # noqa: E501
    WHALE_EVIDENCE_SCHEMA_VERSION as _HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 121 funding-rate-evidence contract module imports ONLY __future__
# and typing -- it does not import this registry -- so reading its stable schema
# constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_funding_rate_evidence_contract import (  # noqa: E501
    FUNDING_RATE_EVIDENCE_SCHEMA_VERSION as _FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 123 bitcoin-cycle-timing-evidence contract module imports ONLY
# __future__, datetime, and typing -- it does not import this registry -- so
# reading its stable schema constant at module top is cycle-safe.
from sparta_commander.strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract import (  # noqa: E501
    BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION as _BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 125 daily-alpha-brief-research contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_research_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_SCHEMA_VERSION as _DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 127 daily-alpha-brief-review contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_review_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION as _DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 129 daily-alpha-brief-approval contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_approval_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION as _DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 132 cohort-independence / correlation-penalty contract module imports
# ONLY __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract import (  # noqa: E501
    COHORT_INDEPENDENCE_SCHEMA_VERSION as _COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 134 real-data-QA boundary-decision contract module imports ONLY
# __future__ and typing -- it does not import this registry -- so reading its
# stable schema constant at module top is cycle-safe (no circular import).
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract import (  # noqa: E501
    RDQ_BOUNDARY_SCHEMA_VERSION as _REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 136 real-data-QA human-approval-packet and readiness-checklist
# contract modules each import ONLY __future__ and typing -- neither imports this
# registry -- so reading their stable schema constants at module top is cycle-safe
# (no circular import).
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract import (  # noqa: E501
    RDQ_APPROVAL_SCHEMA_VERSION as _REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract import (  # noqa: E501
    RDQ_READINESS_SCHEMA_VERSION as _REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
# The Block 152 overnight-research-autopilot-controller module imports only
# __future__, typing, and the Block-151 databento read-only fetch execution
# contract (which itself imports only __future__ and typing); it does NOT import
# this registry, so reading its stable schema constant at module top is cycle-safe
# (no circular import).
from sparta_commander.strategy_factory_overnight_research_autopilot_controller import (  # noqa: E501
    CONTROLLER_SCHEMA_VERSION as _OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_SCHEMA_VERSION,  # noqa: E501
)
# NOTE: the Bundle 48 post-boundary next-step contract module imports
# CURRENT_STAGE / NEXT_REQUIRED_ACTION from THIS registry, so importing its
# schema constant at module top would create a circular import. It is therefore
# imported lazily inside _bundles() (a normal stdlib `from ... import`, resolved
# only after both modules are fully initialized).

__all__ = [
    "REGISTRY_VERSION",
    "REGISTRY_MODE",
    "REGISTRY_SAFETY_POSTURE",
    "CURRENT_STAGE",
    "NEXT_REQUIRED_ACTION",
    "list_registered_bundles",
    "list_completed_bundles",
    "get_latest_completed_bundle",
    "get_bundle_by_number",
    "get_bundle_by_id",
    "get_latest_completed_bundle_label",
    "get_current_stage",
    "get_next_required_action",
    "get_registry_safety_posture",
    "LATEST_COMPLETED_PROTOCOL",
    "get_latest_completed_protocol",
    "get_latest_completed_protocol_label",
    "LATEST_COMPLETED_PROTOCOL_CONTRACT",
    "get_latest_completed_protocol_contract",
    "get_latest_completed_protocol_contract_label",
    "LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT",
    "get_latest_completed_family_selection_contract",
    "get_latest_completed_family_selection_contract_label",
    "LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT",
    "get_latest_completed_family_review_contract",
    "get_latest_completed_family_review_contract_label",
    "LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT",
    "get_latest_completed_research_plan_contract",
    "get_latest_completed_research_plan_contract_label",
    "LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT",
    "get_latest_completed_research_plan_review_contract",
    "get_latest_completed_research_plan_review_contract_label",
    "LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT",
    "get_latest_completed_research_plan_approval_contract",
    "get_latest_completed_research_plan_approval_contract_label",
    "LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT",
    "get_latest_completed_research_design_contract",
    "get_latest_completed_research_design_contract_label",
    "LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT",
    "get_latest_completed_research_design_review_contract",
    "get_latest_completed_research_design_review_contract_label",
    "LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT",
    "get_latest_completed_research_design_approval_contract",
    "get_latest_completed_research_design_approval_contract_label",
    "LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT",
    "get_latest_completed_research_readiness_contract",
    "get_latest_completed_research_readiness_contract_label",
    "LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT",
    "get_latest_completed_external_bot_evidence_intake_contract",
    "get_latest_completed_external_bot_evidence_intake_contract_label",
    "LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT",
    "get_latest_completed_hyperliquid_whale_evidence_contract",
    "get_latest_completed_hyperliquid_whale_evidence_contract_label",
    "LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT",
    "get_latest_completed_funding_rate_evidence_contract",
    "get_latest_completed_funding_rate_evidence_contract_label",
    "LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT",
    "get_latest_completed_bitcoin_cycle_timing_evidence_contract",
    "get_latest_completed_bitcoin_cycle_timing_evidence_contract_label",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT",
    "get_latest_completed_daily_alpha_brief_research_contract",
    "get_latest_completed_daily_alpha_brief_research_contract_label",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT",
    "get_latest_completed_daily_alpha_brief_review_contract",
    "get_latest_completed_daily_alpha_brief_review_contract_label",
    "LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT",
    "get_latest_completed_daily_alpha_brief_approval_contract",
    "get_latest_completed_daily_alpha_brief_approval_contract_label",
    "LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT",
    "get_latest_completed_cohort_independence_contract",
    "get_latest_completed_cohort_independence_contract_label",
    "LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT",
    "get_latest_completed_real_data_qa_boundary_decision_contract",
    "get_latest_completed_real_data_qa_boundary_decision_contract_label",
    "LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT",
    "get_latest_completed_real_data_qa_human_approval_packet_contract",
    "get_latest_completed_real_data_qa_human_approval_packet_contract_label",
    "LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT",
    "get_latest_completed_real_data_qa_readiness_checklist_contract",
    "get_latest_completed_real_data_qa_readiness_checklist_contract_label",
    "LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER",
    "get_latest_completed_overnight_research_autopilot_controller",
    "get_latest_completed_overnight_research_autopilot_controller_label",
]

REGISTRY_VERSION = "v1"
REGISTRY_MODE = "RESEARCH_ONLY"

# Post-Block-103 backbone state: the Crypto-D1 research-only dry-run governance
# lane is closed (Bundle 54), Block 95 DEFINED the next research-only protocol
# (the Crypto-D1 Strategy Candidate Protocol v1, BTC/ETH/SOL, spot-only,
# daily-only, four candidate strategy families), Block 97 BUILT the research-only
# Strategy Candidate Protocol *Contract* that validates whether a proposed
# candidate plan follows that protocol, Block 99 BUILT the research-only Strategy
# Candidate Family *Selection* Contract that validates which of the four
# candidate families a selection scopes for research first, Block 101 BUILT the
# research-only Strategy Candidate Family *Review* Contract that validates whether
# the selected/parked families are reasonable, and Block 103 has now BUILT the
# research-only Strategy Candidate Research *Plan* Contract that validates how the
# reviewed family selection would be researched before any real strategy research
# begins, Block 105 BUILT the research-only Strategy Candidate Research Plan
# *Review* Contract that validates whether that research plan is reasonable, and
# Block 107 has now BUILT the research-only Strategy Candidate Research Plan
# *Approval* Contract that records the separate, later human approval the review
# READY gate requires. The latest completed *bundle* is still Bundle 54; the
# latest recognized *protocol* is the Strategy Candidate Protocol v1 (Block 95);
# the latest recognized *protocol contract* is Block 97; the latest recognized
# *family-selection contract* is Block 99; the latest recognized *family-review
# contract* is Block 101; the latest recognized *research-plan contract* is
# Block 103; the latest recognized *research-plan review contract* is Block 105;
# the latest recognized *research-plan approval contract* is Block 107; the latest
# recognized *research design contract* is Block 109; the latest recognized
# *research design review contract* is Block 111; the latest recognized *research
# design approval contract* is Block 113.
# Block 115 BUILT the research-only Strategy Candidate Research *Readiness*
# Contract (a final readiness paper gate), Block 117 BUILT the research-only
# External Bot Evidence *Intake* Contract, Block 119 BUILT the research-only
# Hyperliquid Whale *Evidence* Contract, Block 121 BUILT the research-only
# Funding Rate *Evidence* Contract, and Block 123 has now BUILT the research-only
# Bitcoin Cycle Timing *Evidence* Contract -- a higher-level macro timing filter
# inserted before the Daily Alpha Brief contract -- that converts the BTC
# 364-day / 1064-day cycle idea into research-only timing evidence (an
# early/active/late/expired cycle-bottom watch zone and a
# caution/accumulation-watch/recovery-watch/no-signal evidence stance), under
# the core rule that cycle timing tells us when to pay attention, not when to
# buy. Recognizing the bitcoin-cycle-timing-evidence contract unlocks nothing
# real: the only next step is still the next research-only evidence paper
# contract -- BUILD a Crypto-D1 Daily Alpha Brief *Research* Contract, still on
# paper, treating cycle-timing signals as external research evidence only and
# never as execution permission or a buy instruction. No BTC data fetch, API
# call, dataset inspection, real acquisition, QA, baseline, backtest, paper/
# live, broker/exchange, or automation is unlocked.
# Block 127 BUILT the research-only Crypto-D1 Daily Alpha Brief *Review*
# Contract, which reviews whether an assembled brief is reasonable, still on
# paper. Block 129 has now BUILT the research-only Crypto-D1 Daily Alpha Brief
# *Approval* Contract, which records, on paper, a human approval decision over a
# reviewed brief: its highest stance is WATCH / RESEARCH_ONLY and an APPROVED
# verdict means ONLY that the reviewed brief may be filed as a research record --
# never a trade, and never that real-data QA, baseline, backtest, paper, live,
# broker/exchange, automation, or any runtime/dashboard write is approved.
# Recognizing it (Block 130) COMPLETES the daily-alpha-brief research-only paper
# sub-chain (research -> review -> approval) and advances the backbone to the
# separate, human-controlled real_data_qa boundary decision -- which is NOT a
# build step and NOT a research-only paper contract. real_data_qa stays BLOCKED,
# baseline_backtest stays BLOCKED, and the paper/micro-live gates stay LOCKED
# unless a separate, future, human-approved boundary contract authorizes it.
CURRENT_STAGE = "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
# The single recognized latest research-only protocol (Block 95). The registry
# tracks completed bundles by number and this one recognized protocol
# separately; DEFINING a protocol is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_PROTOCOL_LABEL = "Block 95 - " + _PROTOCOL_NAME
LATEST_COMPLETED_PROTOCOL = _RECOGNIZED_PROTOCOL_LABEL
# The single recognized latest research-only protocol *contract* (Block 97).
# Building the contract is a research-only planning step and creates no
# execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_PROTOCOL_CONTRACT_LABEL = (
    "Block 97 - Crypto-D1 Strategy Candidate Protocol Contract"
)
LATEST_COMPLETED_PROTOCOL_CONTRACT = _RECOGNIZED_PROTOCOL_CONTRACT_LABEL
# The protocol contract's own declared next step (now complete): BUILD the
# research-only candidate-family-selection contract, which Block 99 has since
# completed on paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION
# can advance without rewriting the Block 97 record's historical next step.
_PROTOCOL_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
)
# The single recognized latest research-only family-selection *contract*
# (Block 99). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_FAMILY_SELECTION_CONTRACT_LABEL = (
    "Block 99 - Crypto-D1 Strategy Candidate Family Selection Contract"
)
LATEST_COMPLETED_FAMILY_SELECTION_CONTRACT = (
    _RECOGNIZED_FAMILY_SELECTION_CONTRACT_LABEL
)
# The family-selection contract's own declared next step (now complete): BUILD
# the research-only candidate-family-review contract, which Block 101 has since
# completed on paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION
# can advance without rewriting the Block 99 record's historical next step.
_FAMILY_SELECTION_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
)
# The single recognized latest research-only family-review *contract*
# (Block 101). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_FAMILY_REVIEW_CONTRACT_LABEL = (
    "Block 101 - Crypto-D1 Strategy Candidate Family Review Contract"
)
LATEST_COMPLETED_FAMILY_REVIEW_CONTRACT = (
    _RECOGNIZED_FAMILY_REVIEW_CONTRACT_LABEL
)
# The family-review contract's own declared next step (now complete): BUILD the
# research-only candidate research-plan contract, which Block 103 has since
# completed on paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION
# can advance without rewriting the Block 101 record's historical next step.
_FAMILY_REVIEW_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT"
)
# The single recognized latest research-only research-plan *contract* (Block
# 103). Building the contract is a research-only planning step and creates no
# execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_PLAN_CONTRACT_LABEL = (
    "Block 103 - Crypto-D1 Strategy Candidate Research Plan Contract"
)
LATEST_COMPLETED_RESEARCH_PLAN_CONTRACT = (
    _RECOGNIZED_RESEARCH_PLAN_CONTRACT_LABEL
)
# The research-plan contract's own declared next step (now complete): BUILD the
# research-only candidate research-plan *review* contract, which Block 105 has
# since completed on paper. Held as a fixed local so the global
# NEXT_REQUIRED_ACTION can advance without rewriting the Block 103 record's
# historical next step.
_RESEARCH_PLAN_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
)
# The single recognized latest research-only research-plan *review* contract
# (Block 105). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_PLAN_REVIEW_CONTRACT_LABEL = (
    "Block 105 - Crypto-D1 Strategy Candidate Research Plan Review Contract"
)
LATEST_COMPLETED_RESEARCH_PLAN_REVIEW_CONTRACT = (
    _RECOGNIZED_RESEARCH_PLAN_REVIEW_CONTRACT_LABEL
)
# The research-plan review contract's own declared next step (now complete):
# BUILD the research-only candidate research-plan *approval* contract, which
# Block 107 has since completed on paper. Held as a fixed local so the global
# NEXT_REQUIRED_ACTION can advance without rewriting the Block 105 record's
# historical next step.
_RESEARCH_PLAN_REVIEW_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
)
# The single recognized latest research-only research-plan *approval* contract
# (Block 107). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_PLAN_APPROVAL_CONTRACT_LABEL = (
    "Block 107 - Crypto-D1 Strategy Candidate Research Plan Approval Contract"
)
LATEST_COMPLETED_RESEARCH_PLAN_APPROVAL_CONTRACT = (
    _RECOGNIZED_RESEARCH_PLAN_APPROVAL_CONTRACT_LABEL
)
# The research-plan approval contract's own declared next step (now complete):
# BUILD the research-only candidate research *design* contract, which Block 109
# has since completed on paper. Held as a fixed local so the global
# NEXT_REQUIRED_ACTION can advance without rewriting the Block 107 record's
# historical next step.
_RESEARCH_PLAN_APPROVAL_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
)
# The single recognized latest research-only research *design* contract (Block
# 109). Building the contract is a research-only planning step and creates no
# execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_DESIGN_CONTRACT_LABEL = (
    "Block 109 - Crypto-D1 Strategy Candidate Research Design Contract"
)
LATEST_COMPLETED_RESEARCH_DESIGN_CONTRACT = (
    _RECOGNIZED_RESEARCH_DESIGN_CONTRACT_LABEL
)
# The research design contract's own declared next step (now complete): BUILD the
# research-only candidate research design *review* contract, which Block 111 has
# since completed on paper. Held as a fixed local so the global
# NEXT_REQUIRED_ACTION can advance without rewriting the Block 109 record's
# historical next step.
_RESEARCH_DESIGN_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT"
)
# The single recognized latest research-only research design *review* contract
# (Block 111). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_DESIGN_REVIEW_CONTRACT_LABEL = (
    "Block 111 - Crypto-D1 Strategy Candidate Research Design Review Contract"
)
LATEST_COMPLETED_RESEARCH_DESIGN_REVIEW_CONTRACT = (
    _RECOGNIZED_RESEARCH_DESIGN_REVIEW_CONTRACT_LABEL
)
# The research design review contract's own declared next step (now complete):
# BUILD the research-only candidate research design *approval* contract, which
# Block 113 has since completed on paper. Held as a fixed local so the global
# NEXT_REQUIRED_ACTION can advance without rewriting the Block 111 record's
# historical next step.
_RESEARCH_DESIGN_REVIEW_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT"
)
# The single recognized latest research-only research design *approval* contract
# (Block 113). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_DESIGN_APPROVAL_CONTRACT_LABEL = (
    "Block 113 - Crypto-D1 Strategy Candidate Research Design Approval Contract"
)
LATEST_COMPLETED_RESEARCH_DESIGN_APPROVAL_CONTRACT = (
    _RECOGNIZED_RESEARCH_DESIGN_APPROVAL_CONTRACT_LABEL
)
# Frozen historical next step for the Block 113 record: BUILD the research-only
# candidate research *readiness* contract, which Block 115 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 113 record's historical next step.
_RESEARCH_DESIGN_APPROVAL_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT"
)
# The single recognized latest research-only research *readiness* contract
# (Block 115). Building the contract is a research-only planning step and creates
# no execution bundle. The label intentionally does not name a trading stage.
_RECOGNIZED_RESEARCH_READINESS_CONTRACT_LABEL = (
    "Block 115 - Crypto-D1 Strategy Candidate Research Readiness Contract"
)
LATEST_COMPLETED_RESEARCH_READINESS_CONTRACT = (
    _RECOGNIZED_RESEARCH_READINESS_CONTRACT_LABEL
)
# Frozen historical next step for the Block 115 record: BUILD the research-only
# External Bot Evidence *Intake* Contract, which Block 117 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 115 record's historical next step.
_RESEARCH_READINESS_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
)
# The single recognized latest research-only External Bot Evidence *Intake*
# contract (Block 117). Building the contract is a research-only planning step
# and creates no execution bundle. It classifies external AI trading bot / tool /
# video ideas into research-only evidence buckets; it authorizes no real-world
# action and unlocks no downstream gate. The label intentionally does not name a
# trading stage.
_RECOGNIZED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_LABEL = (
    "Block 117 - Crypto-D1 External Bot Evidence Intake Contract"
)
LATEST_COMPLETED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT = (
    _RECOGNIZED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_LABEL
)
# Frozen historical next step for the Block 117 record: BUILD the research-only
# Hyperliquid Whale *Evidence* Contract, which Block 119 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 117 record's historical next step.
_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
)
# The single recognized latest research-only Hyperliquid Whale *Evidence*
# contract (Block 119). Building the contract is a research-only planning step
# and creates no execution bundle. It classifies external Hyperliquid
# whale-tracking ideas into research-only evidence buckets; it authorizes no
# real-world action, connects to no Hyperliquid API / wallet / exchange, and
# unlocks no downstream gate. The label intentionally does not name a trading
# stage.
_RECOGNIZED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_LABEL = (
    "Block 119 - Crypto-D1 Hyperliquid Whale Evidence Contract"
)
LATEST_COMPLETED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT = (
    _RECOGNIZED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_LABEL
)
# Frozen historical next step for the Block 119 record: BUILD the research-only
# Funding Rate *Evidence* Contract, which Block 121 has since completed on paper.
# Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance without
# rewriting the Block 119 record's historical next step.
_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
)
# The single recognized latest research-only Funding Rate *Evidence* contract
# (Block 121). Building the contract is a research-only planning step and creates
# no execution bundle. It classifies external funding-rate scanner ideas into
# research-only evidence buckets; it authorizes no real-world action, connects to
# no exchange API / futures account / exchange, and unlocks no downstream gate.
# The label intentionally does not name a trading stage.
_RECOGNIZED_FUNDING_RATE_EVIDENCE_CONTRACT_LABEL = (
    "Block 121 - Crypto-D1 Funding Rate Evidence Contract"
)
LATEST_COMPLETED_FUNDING_RATE_EVIDENCE_CONTRACT = (
    _RECOGNIZED_FUNDING_RATE_EVIDENCE_CONTRACT_LABEL
)
# Frozen historical next step for the Block 121 record: BUILD the research-only
# Bitcoin Cycle Timing *Evidence* Contract, which Block 123 has since completed
# on paper. Held as a fixed local so the funding-rate record's historical next
# step is not rewritten when a later evidence contract is inserted before the
# Daily Alpha Brief contract.
_FUNDING_RATE_EVIDENCE_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
)
# The single recognized latest research-only Bitcoin Cycle Timing *Evidence*
# contract (Block 123), a higher-level macro timing filter inserted before the
# Daily Alpha Brief contract. Building the contract is a research-only planning
# step and creates no execution bundle. It converts the BTC 364-day / 1064-day
# cycle idea into research-only timing evidence; it authorizes no real-world
# action, fetches no BTC data, calls no API, inspects no dataset, and unlocks no
# downstream gate. The label intentionally does not name a trading stage.
_RECOGNIZED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_LABEL = (
    "Block 123 - Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
)
LATEST_COMPLETED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT = (
    _RECOGNIZED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_LABEL
)
# Frozen historical next step for the Block 123 record: BUILD the research-only
# Daily Alpha Brief *Research* Contract, which Block 125 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 123 record's historical next step.
_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
)
# The single recognized latest research-only Daily Alpha Brief *Research*
# contract (Block 125). Building the contract is a research-only planning step
# and creates no execution bundle. It assembles a daily crypto alpha brief from
# already-approved static evidence inputs only; it authorizes no real-world
# action, fetches no data, calls no API, inspects no dataset, and unlocks no
# downstream gate. Its highest stance is WATCH / RESEARCH_ONLY -- never a trade.
# The label intentionally does not name a trading stage.
_RECOGNIZED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_LABEL = (
    "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT = (
    _RECOGNIZED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_LABEL
)
# Frozen historical next step for the Block 125 record: BUILD the research-only
# Daily Alpha Brief *Review* Contract, which Block 127 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 125 record's historical next step.
_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
)
# The single recognized latest research-only Daily Alpha Brief *Review* contract
# (Block 127). Building the contract is a research-only planning step and creates
# no execution bundle. It reviews whether an assembled daily crypto alpha brief
# is reasonable from already-approved static evidence inputs only; it authorizes
# no real-world action, fetches no data, calls no API, inspects no dataset, and
# unlocks no downstream gate. Its highest verdict is READY for human approval --
# never a trade. The label intentionally does not name a trading stage.
_RECOGNIZED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_LABEL = (
    "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT = (
    _RECOGNIZED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_LABEL
)
# Frozen historical next step for the Block 127 record: BUILD the research-only
# Daily Alpha Brief *Approval* Contract, which Block 129 has since completed on
# paper. Held as a fixed local so the global NEXT_REQUIRED_ACTION can advance
# without rewriting the Block 127 record's historical next step.
_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_NEXT_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
)
# The single recognized latest research-only Daily Alpha Brief *Approval*
# contract (Block 129). Building the contract is a research-only planning step
# and creates no execution bundle. It records, on paper, a human approval
# decision over a reviewed daily crypto alpha brief from already-approved static
# evidence inputs only; it authorizes no real-world action, fetches no data,
# calls no API, inspects no dataset, and unlocks no downstream gate. APPROVED
# means only that the reviewed brief may be filed as a research record -- never
# a trade. The label intentionally does not name a trading stage.
_RECOGNIZED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_LABEL = (
    "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
)
LATEST_COMPLETED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT = (
    _RECOGNIZED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_LABEL
)
# Next required action: with the Block 129 daily-alpha-brief-approval contract
# complete, the research-only external-evidence sub-chain (research -> review ->
# approval) is finished. The only next step is the human-controlled real-data QA
# boundary decision -- a human judgment about whether to ever cross from
# research-only paper work into real-data QA. This is NOT a build step and NOT an
# authorization: it does not fetch data, run QA, baseline, backtest, paper/live
# trade, touch a broker/exchange, automate anything, or write any runtime
# artifact. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper/
# micro-live gates stay LOCKED unless a separate, future, human-approved boundary
# contract is built.
NEXT_REQUIRED_ACTION = "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"

# The single recognized latest research-only Cohort Independence / Correlation
# Penalty contract (Block 132). It is a research-only evidence/scoring support
# contract: on paper, it scores whether a set of already-booked paper positions
# represents genuinely independent cohorts or merely correlated/duplicate ones
# (same symbol+direction, macro event, regime, timing window, or signal family),
# and reports whether the independent-booked-cohort sample can SUPPORT a promote-
# to-review judgment. It supports a research judgment only; it authorizes nothing,
# fetches no data, calls no API, inspects no dataset, and unlocks no downstream
# gate. Registering it is purely additive latest-completed metadata: it does NOT
# advance CURRENT_STAGE or NEXT_REQUIRED_ACTION, both of which remain at the
# human-controlled real-data QA boundary above. real_data_qa and baseline stay
# BLOCKED and the paper/micro-live gates stay LOCKED.
_RECOGNIZED_COHORT_INDEPENDENCE_CONTRACT_LABEL = (
    "Block 132 - Crypto-D1 Cohort Independence / Correlation Penalty Contract"
)
LATEST_COMPLETED_COHORT_INDEPENDENCE_CONTRACT = (
    _RECOGNIZED_COHORT_INDEPENDENCE_CONTRACT_LABEL
)

# The single recognized latest research-only human-controlled Real Data QA
# Boundary Decision contract (Block 134). It is the research-only paper contract
# that DEFINES the structured human decision packet/gate to review BEFORE any
# Real Data QA may even be planned. It assesses a static, caller-supplied evidence
# summary into exactly one outcome (BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_
# DECISION) and, even at its most favourable outcome, only assembles the packet
# for a human: it authorizes nothing, fetches no data, calls no API, inspects no
# dataset, runs no QA/baseline/backtest/simulation, touches no broker/exchange/
# paper/live surface, and unlocks no downstream gate. Registering it is purely
# additive latest-completed metadata: it does NOT advance CURRENT_STAGE or
# NEXT_REQUIRED_ACTION, both of which remain at the human-controlled real-data QA
# boundary above. real_data_qa and baseline stay BLOCKED and the paper/micro-live
# gates stay LOCKED unless a separate, future, human-approved step authorizes it.
_RECOGNIZED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_LABEL = (
    "Block 134 - Crypto-D1 Real Data QA Boundary Decision Contract"
)
LATEST_COMPLETED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT = (
    _RECOGNIZED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_LABEL
)

# The single recognized latest research-only Real Data QA Human Approval Packet
# contract (Block 136, Phase A). It is the research-only paper contract that
# DEFINES the structured eight-field human approval packet (plus an exact approval
# phrase) a person must complete BEFORE any Real Data QA may even be planned. It
# assesses a static packet into exactly one outcome (BLOCK / INCOMPLETE /
# COMPLETE) and, even at COMPLETE, only marks the packet ready for human review:
# it authorizes nothing, fetches no data, calls no API, inspects no dataset, runs
# no QA/baseline/backtest/simulation, touches no broker/exchange/paper/live
# surface, and unlocks no downstream gate. Registering it is purely additive
# latest-completed metadata: it does NOT advance CURRENT_STAGE or
# NEXT_REQUIRED_ACTION, both of which remain at the human-controlled real-data QA
# boundary above. real_data_qa and baseline stay BLOCKED and the paper/micro-live
# gates stay LOCKED unless a separate, future, human-approved step authorizes it.
_RECOGNIZED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_LABEL = (
    "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
)
LATEST_COMPLETED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT = (
    _RECOGNIZED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_LABEL
)

# The single recognized latest research-only Real Data QA Readiness Checklist
# contract (Block 136, Phase B). It is the research-only paper contract that
# DEFINES the eight-item readiness checklist that must ALL pass BEFORE a human is
# even asked to approve Real Data QA. It assesses a static payload into exactly one
# outcome (BLOCK / NOT_READY / READY) and, even at READY, only means "ready for a
# separate human approval review": it authorizes nothing, fetches no data, calls
# no API, inspects no dataset, runs no QA/baseline/backtest/simulation, touches no
# broker/exchange/paper/live surface, and unlocks no downstream gate. Registering
# it is purely additive latest-completed metadata: it does NOT advance
# CURRENT_STAGE or NEXT_REQUIRED_ACTION, both of which remain at the human-
# controlled real-data QA boundary above. real_data_qa and baseline stay BLOCKED
# and the paper/micro-live gates stay LOCKED unless a separate, future, human-
# approved step authorizes it.
_RECOGNIZED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_LABEL = (
    "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
)
LATEST_COMPLETED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT = (
    _RECOGNIZED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_LABEL
)

# The single recognized latest research-only SPARTA Overnight Research Autopilot
# Controller (Block 152). It is a research-only PLANNING controller: given a
# static, caller-supplied status summary it reasons -- on paper only -- over which
# safe research-only paper bundles to prepare next, which paths each may touch,
# which scoped tests to run, and a commit/push policy that keeps every commit and
# every push gated behind explicit per-run human approval. It is a planner, not an
# actor: it stages nothing, commits nothing, pushes nothing, fetches no data,
# calls no API, inspects no dataset, runs no QA/baseline/backtest/simulation,
# touches no broker/exchange/paper/live surface, writes no runtime/dashboard
# output, and unlocks no downstream gate. Registering it is purely additive
# latest-completed metadata: it does NOT advance CURRENT_STAGE or
# NEXT_REQUIRED_ACTION, both of which remain at the human-controlled real-data QA
# boundary above and must not imply automatic execution or auto-push. real_data_qa
# and baseline stay BLOCKED and the paper/micro-live gates stay LOCKED unless a
# separate, future, human-approved step authorizes it.
_RECOGNIZED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL = (
    "Block 152 - SPARTA Overnight Research Autopilot Controller"
)
LATEST_COMPLETED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER = (
    _RECOGNIZED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL
)

# The completion stage published once Bundle 48 (post-boundary next-step) is
# registered as complete. Bundle 47 advances into this stage.
_BUNDLE_48_COMPLETE_STAGE = (
    "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 49 (research-only dry-run preview)
# is registered as complete. Bundle 48 advances into this stage.
_BUNDLE_49_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 50 (research-only dry-run review)
# is registered as complete. Bundle 49 advances into this stage.
_BUNDLE_50_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 51 (research-only dry-run decision)
# is registered as complete. Bundle 50 advances into this stage.
_BUNDLE_51_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 52 (research-only dry-run decision
# review) is registered as complete. Bundle 51 advances into this stage.
_BUNDLE_52_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 53 (research-only dry-run final
# decision) is registered as complete. Bundle 52 advances into this stage.
_BUNDLE_53_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT_COMPLETE"
)

# The completion stage published once Bundle 54 (research-only dry-run research
# archive or closure) is registered as complete. Bundle 53 advances into this
# stage; Bundle 54 itself advances into CURRENT_STAGE (lane closed).
_BUNDLE_54_COMPLETE_STAGE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_CONTRACT_"
    "COMPLETE"
)

# Read-only safety posture for the registry as a whole. Nothing here can
# execute or mutate anything; every real-world capability stays blocked.
REGISTRY_SAFETY_POSTURE = {
    "mode": REGISTRY_MODE,
    "read_only": True,
    "executes": False,
    "human_approval_required": True,
    "authorizes_real_world_action": False,
    "unlocks_data_acquisition": False,
    "unlocks_qa": False,
    "unlocks_baseline": False,
    "unlocks_backtest": False,
    "unlocks_simulation": False,
    "unlocks_paper_live": False,
    "unlocks_broker_exchange": False,
    "unlocks_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
}

# Per-bundle "this contract unlocks nothing real" flag block. Shared by every
# entry so a single audit point governs all of them.
_BUNDLE_LOCKED_CAPABILITIES = {
    "authorizes_real_world_action": False,
    "unlocks_data_acquisition": False,
    "unlocks_qa": False,
    "unlocks_baseline": False,
    "unlocks_backtest": False,
    "unlocks_simulation": False,
    "unlocks_paper_live": False,
    "unlocks_broker_exchange": False,
    "unlocks_automation": False,
    "unlocks_runtime_writes": False,
    "unlocks_registry_writes": False,
    "unlocks_dashboard_writes": False,
}


def _bundle(
    *,
    number: int,
    name: str,
    module: str,
    schema_constant: str,
    schema_version: str,
    stage: str,
    next_gate: str,
    reason: str,
) -> dict[str, Any]:
    """Build one fully-populated, read-only bundle metadata record."""
    record: dict[str, Any] = {
        "bundle_number": number,
        "bundle_id": "BUNDLE_" + str(number),
        "name": name,
        "module": module,
        "schema_constant": schema_constant,
        "schema_version": schema_version,
        "stage": stage,
        "complete": True,
        "mode": REGISTRY_MODE,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "next_gate": next_gate,
        "reason": reason,
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


_BUNDLES_CACHE: tuple[dict[str, Any], ...] | None = None


def _bundles() -> tuple[dict[str, Any], ...]:
    """Build (once, memoized) the read-only tuple of bundle records.

    The Bundle 48 schema constant is imported here, function-locally, instead
    of at module top: the Bundle 48 module imports CURRENT_STAGE /
    NEXT_REQUIRED_ACTION from this registry, so a top-level import would be a
    circular import. Resolving it here runs only after both modules are fully
    initialized, which breaks the cycle for every import order. The Bundle 49
    schema constant is imported the same way: Bundle 49 imports Bundle 48, which
    imports this registry, so a top-level import would re-enter the cycle. The
    Bundle 50 schema constant is imported the same way: Bundle 50 imports
    Bundle 49, which (transitively) imports this registry, so a top-level import
    would re-enter the cycle as well. The Bundle 51 schema constant is imported
    the same way: Bundle 51 imports Bundle 50, which (transitively) imports this
    registry, so a top-level import would re-enter the cycle as well. The Bundle
    52 schema constant is imported the same way: Bundle 52 imports Bundle 51,
    which (transitively) imports this registry, so a top-level import would
    re-enter the cycle as well. The Bundle 53 schema constant is imported the
    same way: Bundle 53 imports Bundle 52, which (transitively) imports this
    registry, so a top-level import would re-enter the cycle as well. The Bundle
    54 schema constant is imported the same way: Bundle 54 imports Bundle 53,
    which (transitively) imports this registry, so a top-level import would
    re-enter the cycle as well.
    """
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is not None:
        return _BUNDLES_CACHE
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
    _BUNDLES_CACHE = (
        _bundle(
            number=42,
        name="Crypto-D1 Acquire Decision Contract",
        module=(
            "sparta_commander."
            "strategy_factory_crypto_d1_acquire_decision_contract"
        ),
        schema_constant="ACQUIRE_SCHEMA_VERSION",
        schema_version=ACQUIRE_SCHEMA_VERSION,
        stage="CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_COMPLETE",
        next_gate="CRYPTO_D1_SOURCE_CLASS_CONTRACT_COMPLETE",
        reason=(
            "Read-only acquire-decision paper contract; acquires nothing, "
            "decides nothing, executes nothing."
        ),
    ),
    _bundle(
        number=43,
        name="Crypto-D1 Source Class Contract",
        module=(
            "sparta_commander."
            "strategy_factory_crypto_d1_source_class_contract"
        ),
        schema_constant="SOURCE_CLASS_SCHEMA_VERSION",
        schema_version=SOURCE_CLASS_SCHEMA_VERSION,
        stage="CRYPTO_D1_SOURCE_CLASS_CONTRACT_COMPLETE",
        next_gate="CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_COMPLETE",
        reason=(
            "Read-only source-class paper contract; acquires no data, "
            "executes nothing."
        ),
    ),
    _bundle(
        number=44,
        name="Crypto-D1 Source Specification Contract",
        module=(
            "sparta_commander."
            "strategy_factory_crypto_d1_source_specification_contract"
        ),
        schema_constant="SPEC_SCHEMA_VERSION",
        schema_version=SPEC_SCHEMA_VERSION,
        stage="CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_COMPLETE",
        next_gate="CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_COMPLETE",
        reason=(
            "Read-only source-specification paper contract; acquires no data, "
            "executes nothing."
        ),
    ),
    _bundle(
        number=45,
        name="Crypto-D1 Offline Acquisition Plan Contract",
        module=(
            "sparta_commander."
            "strategy_factory_crypto_d1_offline_acquisition_plan_contract"
        ),
        schema_constant="PLAN_SCHEMA_VERSION",
        schema_version=PLAN_SCHEMA_VERSION,
        stage="CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_COMPLETE",
        next_gate="CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_COMPLETE",
        reason=(
            "Read-only offline-acquisition-plan paper contract; acquires no "
            "data, executes nothing."
        ),
    ),
    _bundle(
        number=46,
        name="Crypto-D1 Pre-Acquisition Human Approval Gate",
        module=(
            "sparta_commander."
            "strategy_factory_crypto_d1_pre_acquisition_human_gate_contract"
        ),
        schema_constant="GATE_SCHEMA_VERSION",
        schema_version=GATE_SCHEMA_VERSION,
        stage="CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_COMPLETE",
        next_gate=(
            "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_"
            "BOUNDARY_CONTRACT_COMPLETE"
        ),
        reason=(
            "Read-only human-approval-gate paper contract only. It defines the "
            "gate but authorizes nothing: no data acquisition, QA, baseline, "
            "backtest, simulation, paper, broker, exchange, or automation is "
            "unlocked."
        ),
    ),
    _bundle(
        number=47,
        name=(
            "Crypto-D1 Human-Approved Offline Acquisition Execution Boundary "
            "Contract"
        ),
        module=(
            "sparta_commander.strategy_factory_crypto_d1_human_approved_"
            "offline_acquisition_execution_boundary_contract"
        ),
        schema_constant="BOUNDARY_SCHEMA_VERSION",
        schema_version=BOUNDARY_SCHEMA_VERSION,
        stage=(
            "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_"
            "BOUNDARY_CONTRACT_COMPLETE"
        ),
        next_gate=_BUNDLE_48_COMPLETE_STAGE,
        reason=(
            "Read-only execution-boundary paper contract only. It authorizes "
            "nothing and executes nothing: no data acquisition, data fetch, "
            "data inspection, QA, baseline, backtest, simulation, paper, live, "
            "broker, exchange, or automation is unlocked."
        ),
    ),
    _bundle(
        number=48,
        name="Crypto-D1 Post-Boundary Research-Only Next-Step Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_post_boundary_"
            "research_only_next_step_contract"
        ),
        schema_constant="NEXT_STEP_SCHEMA_VERSION",
        schema_version=NEXT_STEP_SCHEMA_VERSION,
        stage=_BUNDLE_48_COMPLETE_STAGE,
        next_gate=_BUNDLE_49_COMPLETE_STAGE,
        reason=(
            "Read-only post-boundary next-step paper contract only. It only "
            "DECIDES which research-only, dry-run-preview-only contract should "
            "be built next; it authorizes nothing and executes nothing: no real "
            "data acquisition, data fetch, data inspection, QA, baseline, "
            "backtest, simulation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    ),
    _bundle(
        number=49,
        name="Crypto-D1 Research-Only Dry-Run Preview Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_preview_contract"
        ),
        schema_constant="PREVIEW_SCHEMA_VERSION",
        schema_version=PREVIEW_SCHEMA_VERSION,
        stage=_BUNDLE_49_COMPLETE_STAGE,
        next_gate=_BUNDLE_50_COMPLETE_STAGE,
        reason=(
            "Read-only research-only dry-run PREVIEW paper contract only. It "
            "only PREVIEWS, on paper, what a research-only dry run would look "
            "like; it authorizes nothing and executes nothing: no dry-run "
            "execution, no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    ),
    _bundle(
        number=50,
        name="Crypto-D1 Research-Only Dry-Run Review Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_review_contract"
        ),
        schema_constant="REVIEW_SCHEMA_VERSION",
        schema_version=REVIEW_SCHEMA_VERSION,
        stage=_BUNDLE_50_COMPLETE_STAGE,
        next_gate=_BUNDLE_51_COMPLETE_STAGE,
        reason=(
            "Read-only research-only dry-run REVIEW paper contract only. It "
            "only REVIEWS, on paper, what a research-only dry-run preview "
            "produced; it authorizes nothing and executes nothing: no dry-run "
            "execution, no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper, live, broker, exchange, automation, "
            "or runtime/registry/dashboard write is unlocked."
        ),
    ),
    _bundle(
        number=51,
        name="Crypto-D1 Research-Only Dry-Run Decision Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_decision_contract"
        ),
        schema_constant="DECISION_SCHEMA_VERSION",
        schema_version=DECISION_SCHEMA_VERSION,
        stage=_BUNDLE_51_COMPLETE_STAGE,
        next_gate=_BUNDLE_52_COMPLETE_STAGE,
        reason=(
            "Read-only research-only dry-run DECISION paper contract only. It "
            "only DECIDES, on paper, what a research-only dry-run review "
            "produced and which research-only dry-run-decision-review-only "
            "contract should be built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    ),
    _bundle(
        number=52,
        name="Crypto-D1 Research-Only Dry-Run Decision Review Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_decision_review_contract"
        ),
        schema_constant="DECISION_REVIEW_SCHEMA_VERSION",
        schema_version=DECISION_REVIEW_SCHEMA_VERSION,
        stage=_BUNDLE_52_COMPLETE_STAGE,
        next_gate=_BUNDLE_53_COMPLETE_STAGE,
        reason=(
            "Read-only research-only dry-run DECISION REVIEW paper contract "
            "only. It only REVIEWS, on paper, what a research-only dry-run "
            "decision produced and which research-only dry-run-final-decision-"
            "only contract should be built next; it authorizes nothing and "
            "executes nothing: no dry-run execution, no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, market-data validation, paper, "
            "live, broker, exchange, automation, or runtime/registry/dashboard "
            "write is unlocked."
        ),
    ),
    _bundle(
        number=53,
        name="Crypto-D1 Research-Only Dry-Run Final Decision Contract",
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_final_decision_contract"
        ),
        schema_constant="FINAL_DECISION_SCHEMA_VERSION",
        schema_version=FINAL_DECISION_SCHEMA_VERSION,
        stage=_BUNDLE_53_COMPLETE_STAGE,
        next_gate=_BUNDLE_54_COMPLETE_STAGE,
        reason=(
            "Read-only research-only dry-run FINAL DECISION paper contract "
            "only. It only FINALIZES, on paper, the research-only dry-run "
            "decision and which research-only research-archive-or-closure-only "
            "contract should be built next; it authorizes nothing and executes "
            "nothing: no dry-run execution, no real data acquisition, data "
            "fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper, live, "
            "broker, exchange, automation, or runtime/registry/dashboard write "
            "is unlocked."
        ),
    ),
    _bundle(
        number=54,
        name=(
            "Crypto-D1 Research-Only Dry-Run Research Archive or Closure "
            "Contract"
        ),
        module=(
            "sparta_commander.strategy_factory_crypto_d1_research_only_"
            "dry_run_research_archive_or_closure_contract"
        ),
        schema_constant="ARCHIVE_OR_CLOSURE_SCHEMA_VERSION",
        schema_version=ARCHIVE_OR_CLOSURE_SCHEMA_VERSION,
        stage=_BUNDLE_54_COMPLETE_STAGE,
        next_gate=CURRENT_STAGE,
        reason=(
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
    ),
    )
    return _BUNDLES_CACHE


def _clone_bundle(record: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow, mutation-safe copy of one bundle record."""
    return dict(record)


def list_registered_bundles() -> list[dict[str, Any]]:
    """All registered bundle records (display-only), ascending by number."""
    return [_clone_bundle(b) for b in _bundles()]


def list_completed_bundles() -> list[dict[str, Any]]:
    """Registered bundles whose contract is complete (display-only)."""
    return [_clone_bundle(b) for b in _bundles() if b["complete"] is True]


def get_latest_completed_bundle() -> dict[str, Any]:
    """The highest-numbered completed bundle record."""
    completed = [b for b in _bundles() if b["complete"] is True]
    latest = max(completed, key=lambda b: b["bundle_number"])
    return _clone_bundle(latest)


def get_bundle_by_number(number: int) -> dict[str, Any] | None:
    """The bundle record with the given number, or None."""
    for b in _bundles():
        if b["bundle_number"] == number:
            return _clone_bundle(b)
    return None


def get_bundle_by_id(bundle_id: str) -> dict[str, Any] | None:
    """The bundle record with the given id (e.g. 'BUNDLE_47'), or None."""
    for b in _bundles():
        if b["bundle_id"] == bundle_id:
            return _clone_bundle(b)
    return None


def get_latest_completed_bundle_label() -> str:
    """Human label 'Bundle N - Name' for the latest completed bundle."""
    latest = get_latest_completed_bundle()
    return "Bundle " + str(latest["bundle_number"]) + " - " + latest["name"]


def _recognized_protocol() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-protocol record.

    Recognizing the protocol records, on paper, that the next research-only
    Crypto-D1 protocol is DEFINED. It is NOT an execution bundle: it authorizes
    nothing, executes nothing, and unlocks no real capability. A fresh record
    (with fresh lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "protocol_id": _PROTOCOL_ID,
        "protocol_name": _PROTOCOL_NAME,
        "label": _RECOGNIZED_PROTOCOL_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_next_research_protocol"
        ),
        "schema_constant": "PROTOCOL_SCHEMA_VERSION",
        "schema_version": _PROTOCOL_SCHEMA_VERSION,
        "mode": _PROTOCOL_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _PROTOCOL_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate "
            "Protocol v1, DEFINED in Block 95. It records, on paper, that the "
            "next research-only Crypto-D1 protocol now exists (BTC/ETH/SOL, "
            "spot, daily candles, four candidate strategy families); it "
            "authorizes nothing and executes nothing: no real data "
            "acquisition, data fetch, data inspection, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, market-data "
            "validation, paper/live, broker/exchange, automation, or runtime/"
            "registry/dashboard write is unlocked. Its declared next step was "
            "to BUILD a research-only candidate-protocol contract, which Block "
            "97 has since completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_protocol() -> dict[str, Any]:
    """The latest recognized research-only protocol record (display-only)."""
    return _recognized_protocol()


def get_latest_completed_protocol_label() -> str:
    """Human label for the latest recognized research-only protocol."""
    return _RECOGNIZED_PROTOCOL_LABEL


def _recognized_protocol_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-protocol-contract record.

    Recognizing the protocol contract records, on paper, that the Block 97
    Crypto-D1 Strategy Candidate Protocol Contract is COMPLETE. It is NOT an
    execution bundle: it authorizes nothing, executes nothing, and unlocks no
    real capability. The contract only VALIDATES whether a proposed candidate
    plan follows the Block 95 protocol; it acquires/fetches/inspects/loads no
    data and runs no QA, baseline, backtest, simulation, paper/live, or broker/
    exchange. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "protocol_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Protocol Contract",
        "label": _RECOGNIZED_PROTOCOL_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_protocol_contract"
        ),
        "schema_constant": "STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION",
        "schema_version": _PROTOCOL_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _PROTOCOL_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Protocol "
            "Contract, BUILT in Block 97. It records, on paper, that the "
            "research-only contract validating whether a proposed candidate plan "
            "follows the Block 95 protocol (BTC/ETH/SOL, spot, daily candles, "
            "four candidate strategy families) now exists; it authorizes nothing "
            "and executes nothing: no real data acquisition, data fetch, data "
            "inspection, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, market-data validation, paper/live, broker/exchange, "
            "automation, or runtime/registry/dashboard write is unlocked. Its "
            "declared next step was to BUILD a research-only candidate-family-"
            "selection contract, which Block 99 has since completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_protocol_contract() -> dict[str, Any]:
    """The latest recognized research-only protocol-contract record."""
    return _recognized_protocol_contract()


def get_latest_completed_protocol_contract_label() -> str:
    """Human label for the latest recognized research-only protocol contract."""
    return _RECOGNIZED_PROTOCOL_CONTRACT_LABEL


def _recognized_family_selection_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-family-selection-contract
    record.

    Recognizing the family-selection contract records, on paper, that the Block
    99 Crypto-D1 Strategy Candidate Family Selection Contract is COMPLETE. It is
    NOT an execution bundle: it authorizes nothing, executes nothing, and unlocks
    no real capability. The contract only VALIDATES whether a proposed family
    selection follows the Block 97 protocol contract (and therefore the Block 95
    protocol): which of the four candidate families are selected or explicitly
    parked, kept on BTC/ETH/SOL spot daily candles. It acquires/fetches/inspects/
    loads no data and runs no QA, baseline, backtest, simulation, paper/live, or
    broker/exchange. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "family_selection_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_SELECTION_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Family Selection Contract",
        "label": _RECOGNIZED_FAMILY_SELECTION_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_family_selection_"
            "contract"
        ),
        "schema_constant": "STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION",
        "schema_version": _FAMILY_SELECTION_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _FAMILY_SELECTION_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Family "
            "Selection Contract, BUILT in Block 99. It records, on paper, that "
            "the research-only contract validating which of the four candidate "
            "families a proposed selection scopes for research first "
            "(BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. Its declared next step was to BUILD a research-only "
            "candidate-family-review contract, which Block 101 has since "
            "completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_family_selection_contract() -> dict[str, Any]:
    """The latest recognized research-only family-selection-contract record."""
    return _recognized_family_selection_contract()


def get_latest_completed_family_selection_contract_label() -> str:
    """Human label for the latest recognized research-only family-selection
    contract."""
    return _RECOGNIZED_FAMILY_SELECTION_CONTRACT_LABEL


def _recognized_family_review_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-family-review-contract
    record.

    Recognizing the family-review contract records, on paper, that the Block
    101 Crypto-D1 Strategy Candidate Family Review Contract is COMPLETE. It is
    NOT an execution bundle: it authorizes nothing, executes nothing, and unlocks
    no real capability. The contract only REVIEWS whether the families a Block 99
    selection chose or parked are reasonable under the Block 97 protocol contract
    (and therefore the Block 95 protocol), kept on BTC/ETH/SOL spot daily
    candles. It acquires/fetches/inspects/loads no data and runs no QA, baseline,
    backtest, simulation, paper/live, or broker/exchange. A fresh record (with
    fresh lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "family_review_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Family Review Contract",
        "label": _RECOGNIZED_FAMILY_REVIEW_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_family_review_"
            "contract"
        ),
        "schema_constant": "STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION",
        "schema_version": _FAMILY_REVIEW_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _FAMILY_REVIEW_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Family "
            "Review Contract, BUILT in Block 101. It records, on paper, that "
            "the research-only contract reviewing whether the families a "
            "selection chose or parked are reasonable "
            "(BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. Its declared next step was to BUILD a research-only "
            "candidate research-plan contract, which Block 103 has since "
            "completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_family_review_contract() -> dict[str, Any]:
    """The latest recognized research-only family-review-contract record."""
    return _recognized_family_review_contract()


def get_latest_completed_family_review_contract_label() -> str:
    """Human label for the latest recognized research-only family-review
    contract."""
    return _RECOGNIZED_FAMILY_REVIEW_CONTRACT_LABEL


def _recognized_research_plan_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-plan-contract
    record.

    Recognizing the research-plan contract records, on paper, that the Block
    103 Crypto-D1 Strategy Candidate Research Plan Contract is COMPLETE. It is
    NOT an execution bundle: it authorizes nothing, executes nothing, and unlocks
    no real capability. The contract only validates, on paper, how the reviewed
    family selection would be researched before any real strategy research begins
    (under the Block 101 family-review READY gate, the Block 97 protocol contract,
    and therefore the Block 95 protocol), kept on BTC/ETH/SOL spot daily candles.
    It acquires/fetches/inspects/loads no data and runs no QA, baseline,
    backtest, simulation, paper/live, or broker/exchange. A fresh record (with
    fresh lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_plan_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Research Plan Contract",
        "label": _RECOGNIZED_RESEARCH_PLAN_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_plan_"
            "contract"
        ),
        "schema_constant": "BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION",
        "schema_version": _RESEARCH_PLAN_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_PLAN_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Plan Contract, BUILT in Block 103. It records, on paper, that the "
            "research-only contract validating how the reviewed family selection "
            "would be researched before any real strategy research begins "
            "(BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. Its declared next step was to BUILD a research-only "
            "candidate research-plan review contract, which Block 105 has since "
            "completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_plan_contract() -> dict[str, Any]:
    """The latest recognized research-only research-plan-contract record."""
    return _recognized_research_plan_contract()


def get_latest_completed_research_plan_contract_label() -> str:
    """Human label for the latest recognized research-only research-plan
    contract."""
    return _RECOGNIZED_RESEARCH_PLAN_CONTRACT_LABEL


def _recognized_research_plan_review_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-plan-review-
    contract record.

    Recognizing the research-plan-review contract records, on paper, that the
    Block 105 Crypto-D1 Strategy Candidate Research Plan Review Contract is
    COMPLETE. It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. The contract only REVIEWS, on paper,
    whether the Block 103 research plan is reasonable under the Block 101 family-
    review READY gate, the Block 97 protocol contract, and therefore the Block 95
    protocol, kept on BTC/ETH/SOL spot daily candles. It acquires/fetches/
    inspects/loads no data and runs no QA, baseline, backtest, simulation,
    paper/live, or broker/exchange. A fresh record (with fresh lists) is returned
    every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_plan_review_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Research Plan Review Contract",
        "label": _RECOGNIZED_RESEARCH_PLAN_REVIEW_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_plan_review_"
            "contract"
        ),
        "schema_constant": "RESEARCH_PLAN_REVIEW_SCHEMA_VERSION",
        "schema_version": _RESEARCH_PLAN_REVIEW_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_PLAN_REVIEW_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Plan Review Contract, BUILT in Block 105. It records, on paper, that "
            "the research-only contract reviewing whether the Block 103 research "
            "plan is reasonable before any real strategy research begins "
            "(BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. The only next step is to BUILD a research-only candidate "
            "research-plan approval contract -- the separate, later human step "
            "the review READY gate requires."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_plan_review_contract() -> dict[str, Any]:
    """The latest recognized research-only research-plan-review-contract
    record."""
    return _recognized_research_plan_review_contract()


def get_latest_completed_research_plan_review_contract_label() -> str:
    """Human label for the latest recognized research-only research-plan-review
    contract."""
    return _RECOGNIZED_RESEARCH_PLAN_REVIEW_CONTRACT_LABEL


def _recognized_research_plan_approval_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-plan-approval-
    contract record.

    Recognizing the research-plan-approval contract records, on paper, that the
    Block 107 Crypto-D1 Strategy Candidate Research Plan Approval Contract is
    COMPLETE. It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. The contract only records, on paper,
    the separate, later human approval the Block 105 research-plan-review READY
    gate requires before any real strategy research begins (under the Block 101
    family-review READY gate, the Block 97 protocol contract, and therefore the
    Block 95 protocol), kept on BTC/ETH/SOL spot daily candles. It acquires/
    fetches/inspects/loads no data and runs no QA, baseline, backtest, simulation,
    paper/live, or broker/exchange. A fresh record (with fresh lists) is returned
    every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_plan_approval_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Research Plan Approval Contract",
        "label": _RECOGNIZED_RESEARCH_PLAN_APPROVAL_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_plan_"
            "approval_contract"
        ),
        "schema_constant": "RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION",
        "schema_version": _RESEARCH_PLAN_APPROVAL_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_PLAN_APPROVAL_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Plan Approval Contract, BUILT in Block 107. It records, on paper, "
            "that the research-only contract capturing the separate, later human "
            "approval the Block 105 research-plan-review READY gate requires "
            "before any real strategy research begins (BTC/ETH/SOL, spot, daily "
            "candles) now exists; it authorizes nothing and executes nothing: no "
            "real data acquisition, data fetch, data inspection, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, market-data "
            "validation, paper/live, broker/exchange, automation, or runtime/"
            "registry/dashboard write is unlocked. Its declared next step was to "
            "BUILD a research-only candidate research design contract, which "
            "Block 109 has since completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_plan_approval_contract() -> dict[str, Any]:
    """The latest recognized research-only research-plan-approval-contract
    record."""
    return _recognized_research_plan_approval_contract()


def get_latest_completed_research_plan_approval_contract_label() -> str:
    """Human label for the latest recognized research-only research-plan-approval
    contract."""
    return _RECOGNIZED_RESEARCH_PLAN_APPROVAL_CONTRACT_LABEL


def _recognized_research_design_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-design-contract
    record.

    Recognizing the research-design contract records, on paper, that the Block
    109 Crypto-D1 Strategy Candidate Research Design Contract is COMPLETE. It is
    NOT an execution bundle: it authorizes nothing, executes nothing, and unlocks
    no real capability. The contract only details, on paper, how the approved
    research plan would be carried out before any real strategy research begins
    (under the Block 107 research-plan-approval READY gate, the Block 105
    research-plan-review READY gate, the Block 101 family-review READY gate, the
    Block 97 protocol contract, and therefore the Block 95 protocol), kept on
    BTC/ETH/SOL spot daily candles. It acquires/fetches/inspects/loads no data
    and runs no QA, baseline, backtest, simulation, paper/live, or broker/
    exchange. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_design_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
        ),
        "name": "Crypto-D1 Strategy Candidate Research Design Contract",
        "label": _RECOGNIZED_RESEARCH_DESIGN_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_design_"
            "contract"
        ),
        "schema_constant": "RESEARCH_DESIGN_SCHEMA_VERSION",
        "schema_version": _RESEARCH_DESIGN_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_DESIGN_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Design Contract, BUILT in Block 109. It records, on paper, that the "
            "research-only contract detailing how the approved research plan "
            "would be carried out before any real strategy research begins "
            "(BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. Its declared next step was to BUILD a research-only "
            "candidate research design review contract, which Block 111 has since "
            "completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_design_contract() -> dict[str, Any]:
    """The latest recognized research-only research-design-contract record."""
    return _recognized_research_design_contract()


def get_latest_completed_research_design_contract_label() -> str:
    """Human label for the latest recognized research-only research-design
    contract."""
    return _RECOGNIZED_RESEARCH_DESIGN_CONTRACT_LABEL


def _recognized_research_design_review_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-design-review-
    contract record.

    Recognizing the research-design-review contract records, on paper, that the
    Block 111 Crypto-D1 Strategy Candidate Research Design Review Contract is
    COMPLETE. It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. The contract only records, on paper,
    a human review of whether the Block 109 research design is reasonable before
    any real strategy research begins (under the Block 109 research-design READY
    gate, the Block 107 research-plan-approval READY gate, the Block 105
    research-plan-review READY gate, the Block 101 family-review READY gate, the
    Block 97 protocol contract, and therefore the Block 95 protocol), kept on
    BTC/ETH/SOL spot daily candles. It acquires/fetches/inspects/loads no data
    and runs no QA, baseline, backtest, simulation, paper/live, or broker/
    exchange. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_design_review_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_REVIEW_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Strategy Candidate Research Design Review Contract"
        ),
        "label": _RECOGNIZED_RESEARCH_DESIGN_REVIEW_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_design_"
            "review_contract"
        ),
        "schema_constant": "RESEARCH_DESIGN_REVIEW_SCHEMA_VERSION",
        "schema_version": _RESEARCH_DESIGN_REVIEW_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_DESIGN_REVIEW_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Design Review Contract, BUILT in Block 111. It records, on paper, "
            "that the research-only contract reviewing whether the Block 109 "
            "research design is reasonable before any real strategy research "
            "begins (BTC/ETH/SOL, spot, daily candles) now exists; it authorizes "
            "nothing and executes nothing: no real data acquisition, data fetch, "
            "data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, paper/live, "
            "broker/exchange, automation, or runtime/registry/dashboard write is "
            "unlocked. Its declared next step was to BUILD a research-only "
            "candidate research design approval contract, which Block 113 has "
            "since completed on paper."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_design_review_contract() -> dict[str, Any]:
    """The latest recognized research-only research-design-review-contract
    record."""
    return _recognized_research_design_review_contract()


def get_latest_completed_research_design_review_contract_label() -> str:
    """Human label for the latest recognized research-only research-design-review
    contract."""
    return _RECOGNIZED_RESEARCH_DESIGN_REVIEW_CONTRACT_LABEL


def _recognized_research_design_approval_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-design-approval-
    contract record.

    Recognizing the research-design-approval contract records, on paper, that the
    Block 113 Crypto-D1 Strategy Candidate Research Design Approval Contract is
    COMPLETE. It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. The contract only records, on paper,
    the separate, later human approval the Block 111 research-design-review READY
    gate requires before any real strategy research begins (under the Block 109
    research-design READY gate, the Block 107 research-plan-approval READY gate,
    the Block 105 research-plan-review READY gate, the Block 101 family-review
    READY gate, the Block 97 protocol contract, and therefore the Block 95
    protocol), kept on BTC/ETH/SOL spot daily candles. It acquires/fetches/
    inspects/loads no data and runs no QA, baseline, backtest, simulation,
    paper/live, or broker/exchange. A fresh record (with fresh lists) is returned
    every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_design_approval_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_APPROVAL_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Strategy Candidate Research Design Approval Contract"
        ),
        "label": _RECOGNIZED_RESEARCH_DESIGN_APPROVAL_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_design_"
            "approval_contract"
        ),
        "schema_constant": "RESEARCH_DESIGN_APPROVAL_SCHEMA_VERSION",
        "schema_version": _RESEARCH_DESIGN_APPROVAL_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_DESIGN_APPROVAL_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Design Approval Contract, BUILT in Block 113. It records, on paper, "
            "that the research-only contract capturing the separate, later human "
            "approval the Block 111 research-design-review READY gate requires "
            "before any real strategy research begins (BTC/ETH/SOL, spot, daily "
            "candles) now exists; it authorizes nothing and executes nothing: no "
            "real data acquisition, data fetch, data inspection, dataset loading, "
            "QA, baseline, backtest, simulation, trade signal, market-data "
            "validation, paper/live, broker/exchange, automation, or runtime/"
            "registry/dashboard write is unlocked. The only next step is to BUILD "
            "a research-only candidate research readiness contract, still on "
            "paper -- a final readiness paper gate before the still-blocked "
            "real_data_qa boundary."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_design_approval_contract() -> dict[str, Any]:
    """The latest recognized research-only research-design-approval-contract
    record."""
    return _recognized_research_design_approval_contract()


def get_latest_completed_research_design_approval_contract_label() -> str:
    """Human label for the latest recognized research-only research-design-
    approval contract."""
    return _RECOGNIZED_RESEARCH_DESIGN_APPROVAL_CONTRACT_LABEL


def _recognized_research_readiness_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-research-readiness-
    contract record.

    Recognizing the research-readiness contract records, on paper, that the
    Block 115 Crypto-D1 Strategy Candidate Research Readiness Contract is
    COMPLETE. It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. It records only that the research-
    only paper chain (through the Block 113 research-design-approval READY gate,
    the Block 111 research-design-review READY gate, the Block 109 research-design
    READY gate, the Block 107 research-plan-approval READY gate, the Block 105
    research-plan-review READY gate, the Block 101 family-review READY gate, the
    Block 97 protocol contract, and therefore the Block 95 protocol) is internally
    ready on paper -- a final readiness paper gate before the still-blocked
    real_data_qa boundary, kept on BTC/ETH/SOL spot daily candles. Readiness is
    paper readiness ONLY; it does NOT authorize real_data_qa, which stays BLOCKED
    unless a separate, future, human-approved boundary contract is built. It
    acquires/fetches/inspects/loads no data and runs no QA, baseline, backtest,
    simulation, paper/live, or broker/exchange. A fresh record (with fresh lists)
    is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "research_readiness_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_READINESS_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Strategy Candidate Research Readiness Contract"
        ),
        "label": _RECOGNIZED_RESEARCH_READINESS_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_strategy_candidate_research_readiness_"
            "contract"
        ),
        "schema_constant": "RESEARCH_READINESS_SCHEMA_VERSION",
        "schema_version": _RESEARCH_READINESS_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _RESEARCH_READINESS_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Strategy Candidate Research "
            "Readiness Contract, BUILT in Block 115. It records, on paper, that "
            "the research-only paper chain is internally ready (BTC/ETH/SOL, spot, "
            "daily candles) -- a final readiness paper gate before the still-"
            "blocked real_data_qa boundary; it authorizes nothing and executes "
            "nothing: no real data acquisition, data fetch, data inspection, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "market-data validation, paper/live, broker/exchange, automation, or "
            "runtime/registry/dashboard write is unlocked. Readiness is paper "
            "readiness ONLY: real_data_qa stays BLOCKED. The only next step is to "
            "BUILD a research-only External Bot Evidence Intake Contract, still on "
            "paper, that classifies external AI trading bot / tool / video ideas "
            "into research-only evidence buckets and authorizes nothing."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_research_readiness_contract() -> dict[str, Any]:
    """The latest recognized research-only research-readiness-contract record."""
    return _recognized_research_readiness_contract()


def get_latest_completed_research_readiness_contract_label() -> str:
    """Human label for the latest recognized research-only research-readiness
    contract."""
    return _RECOGNIZED_RESEARCH_READINESS_CONTRACT_LABEL


def _recognized_external_bot_evidence_intake_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-external-bot-evidence-
    intake-contract record.

    Recognizing the external-bot-evidence-intake contract records, on paper, that
    the Block 117 Crypto-D1 External Bot Evidence Intake Contract is COMPLETE. It
    is NOT an execution bundle: it authorizes nothing, executes nothing, and
    unlocks no real capability. It records only that the research-only paper chain
    now has a contract that classifies external AI trading bot / tool / video
    ideas (support/resistance chart reads, Pine Script generation/debugging,
    TradingView webhooks, Telegram command assistant, portfolio dashboard,
    funding-rate scanning, Hyperliquid whale tracking, daily alpha brief, cloud
    bot operation) into research-only evidence buckets -- useful_for_research,
    risky_requires_validation, blocked_execution_feature,
    dashboard_or_brief_candidate, ignore_or_marketing_claim. Every execution-
    capable idea is marked blocked_execution_feature and every attractive-but-
    unverified claim is marked risky_requires_validation; evidence is never
    converted into permission. It acquires/fetches/inspects/loads no data and runs
    no QA, baseline, backtest, simulation, paper/live, or broker/exchange. A fresh
    record (with fresh lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "external_bot_evidence_intake_contract_id": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT"
        ),
        "name": (
            "Crypto-D1 External Bot Evidence Intake Contract"
        ),
        "label": _RECOGNIZED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_external_bot_evidence_intake_contract"
        ),
        "schema_constant": "EXTERNAL_BOT_EVIDENCE_INTAKE_SCHEMA_VERSION",
        "schema_version": _EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 External Bot Evidence Intake "
            "Contract, BUILT in Block 117. It records, on paper, that the "
            "research-only contract classifying external AI trading bot / tool / "
            "video ideas into research-only evidence buckets now exists; it "
            "authorizes nothing and executes nothing: no real data acquisition, "
            "data fetch, data inspection, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, market-data validation, order placement, "
            "broker/exchange connection, Telegram trade command, TradingView "
            "execution webhook, portfolio account control, live strategy "
            "deployment, cloud bot operation, paper/live, automation, or runtime/"
            "registry/dashboard write is unlocked. Every execution-capable idea is "
            "marked blocked_execution_feature and every attractive-but-unverified "
            "claim is marked risky_requires_validation; evidence is never converted "
            "into permission. The only next step is to BUILD a research-only "
            "Crypto-D1 Hyperliquid Whale Evidence Contract, still on paper, "
            "treating whale tracking as external research evidence only and never "
            "as execution permission."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_external_bot_evidence_intake_contract() -> dict[str, Any]:
    """The latest recognized research-only external-bot-evidence-intake-contract
    record."""
    return _recognized_external_bot_evidence_intake_contract()


def get_latest_completed_external_bot_evidence_intake_contract_label() -> str:
    """Human label for the latest recognized research-only external-bot-evidence-
    intake contract."""
    return _RECOGNIZED_EXTERNAL_BOT_EVIDENCE_INTAKE_CONTRACT_LABEL


def _recognized_hyperliquid_whale_evidence_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-hyperliquid-whale-
    evidence-contract record.

    Recognizing the whale-evidence contract records, on paper, that the Block 119
    Crypto-D1 Hyperliquid Whale Evidence Contract is COMPLETE. It is NOT an
    execution bundle: it authorizes nothing, executes nothing, and unlocks no real
    capability. It records only that the research-only paper chain now has a
    contract that classifies external Hyperliquid whale-tracking ideas (whale
    position observation, large whale movement claims, wallet monitoring, copy/
    follow whale execution, account/portfolio access, exchange connection, whale
    alert automation, smart-money-certainty / guaranteed-whale-signal marketing)
    into research-only evidence buckets -- useful_for_research,
    risky_requires_validation, blocked_execution_feature, ignore_or_marketing_claim,
    needs_independent_confirmation. Every execution-capable idea is marked
    blocked_execution_feature, every unverified whale movement claim is marked
    risky_requires_validation, and whale evidence is never converted into
    permission and always requires independent confirmation before later use. It
    connects to no Hyperliquid API, monitors no wallet, accesses no account/
    portfolio, connects to no exchange, acquires/fetches/inspects/loads no data,
    and runs no QA, baseline, backtest, simulation, paper/live, broker/exchange,
    or automation. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "hyperliquid_whale_evidence_contract_id": (
            "CRYPTO_D1_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Hyperliquid Whale Evidence Contract"
        ),
        "label": _RECOGNIZED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_hyperliquid_whale_evidence_contract"
        ),
        "schema_constant": "WHALE_EVIDENCE_SCHEMA_VERSION",
        "schema_version": _HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Hyperliquid Whale Evidence "
            "Contract, BUILT in Block 119. It records, on paper, that the "
            "research-only contract classifying external Hyperliquid whale-tracking "
            "ideas into research-only evidence buckets now exists; it authorizes "
            "nothing and executes nothing: no Hyperliquid API connection, wallet "
            "monitoring, account/portfolio access, exchange connection, real data "
            "acquisition, data fetch, data inspection, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, copy/"
            "follow whale execution, whale alert automation, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Every execution-capable whale idea is marked "
            "blocked_execution_feature, every unverified whale movement claim is "
            "marked risky_requires_validation, and whale evidence always requires "
            "independent confirmation before it can be used in any later research "
            "protocol; evidence is never converted into permission. The only next "
            "step is to BUILD a research-only Crypto-D1 Funding Rate Evidence "
            "Contract, still on paper, treating funding-rate signals as external "
            "research evidence only and never as execution permission."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_hyperliquid_whale_evidence_contract() -> dict[str, Any]:
    """The latest recognized research-only hyperliquid-whale-evidence-contract
    record."""
    return _recognized_hyperliquid_whale_evidence_contract()


def get_latest_completed_hyperliquid_whale_evidence_contract_label() -> str:
    """Human label for the latest recognized research-only hyperliquid-whale-
    evidence contract."""
    return _RECOGNIZED_HYPERLIQUID_WHALE_EVIDENCE_CONTRACT_LABEL


def _recognized_funding_rate_evidence_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-funding-rate-evidence-
    contract record.

    Recognizing the funding-rate-evidence contract records, on paper, that the
    Block 121 Crypto-D1 Funding Rate Evidence Contract is COMPLETE. It is NOT an
    execution bundle: it authorizes nothing, executes nothing, and unlocks no
    real capability. It records only that the research-only paper chain now has a
    contract that classifies external funding-rate scanner ideas (funding-rate
    scanning, positive/negative funding claims, basis/spread observations,
    carry-trade execution, funding arbitrage execution, exchange API connection,
    futures/perps account access, position opening, hedging logic, live funding
    monitor, guaranteed-yield / risk-free-funding marketing) into research-only
    evidence buckets -- useful_for_research, risky_requires_validation,
    blocked_execution_feature, ignore_or_marketing_claim,
    needs_independent_confirmation. Every execution-capable idea is marked
    blocked_execution_feature, every unverified funding-rate claim is marked
    risky_requires_validation, and funding-rate evidence is never converted into
    permission and always requires independent confirmation before later use. It
    connects to no exchange API, accesses no futures/perps account, opens no
    position, runs no hedging/carry/arbitrage execution, runs no live funding
    monitor, connects to no exchange, acquires/fetches/inspects/loads no data,
    and runs no QA, baseline, backtest, simulation, paper/live, broker/exchange,
    or automation. A fresh record (with fresh lists) is returned every call for
    mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "funding_rate_evidence_contract_id": (
            "CRYPTO_D1_FUNDING_RATE_EVIDENCE_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Funding Rate Evidence Contract"
        ),
        "label": _RECOGNIZED_FUNDING_RATE_EVIDENCE_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_funding_rate_evidence_contract"
        ),
        "schema_constant": "FUNDING_RATE_EVIDENCE_SCHEMA_VERSION",
        "schema_version": _FUNDING_RATE_EVIDENCE_CONTRACT_SCHEMA_VERSION,
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _FUNDING_RATE_EVIDENCE_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Funding Rate Evidence "
            "Contract, BUILT in Block 121. It records, on paper, that the "
            "research-only contract classifying external funding-rate scanner "
            "ideas into research-only evidence buckets now exists; it authorizes "
            "nothing and executes nothing: no exchange API connection, futures/"
            "perps account access, position opening, hedging, carry-trade "
            "execution, arbitrage execution, live funding monitor, real data "
            "acquisition, data fetch, data inspection, dataset loading, QA, "
            "baseline, backtest, simulation, trade signal, order placement, "
            "Telegram trade command, paper/live, automation, or runtime/registry/"
            "dashboard write is unlocked. Every execution-capable funding idea is "
            "marked blocked_execution_feature, every unverified funding-rate "
            "claim is marked risky_requires_validation, and funding-rate evidence "
            "always requires independent confirmation before it can be used in "
            "any later research protocol; evidence is never converted into "
            "permission. The only next step is to BUILD a research-only Crypto-D1 "
            "Bitcoin Cycle Timing Evidence Contract, still on paper, treating "
            "cycle-timing signals as external research evidence only and never as "
            "execution permission."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_funding_rate_evidence_contract() -> dict[str, Any]:
    """The latest recognized research-only funding-rate-evidence-contract
    record."""
    return _recognized_funding_rate_evidence_contract()


def get_latest_completed_funding_rate_evidence_contract_label() -> str:
    """Human label for the latest recognized research-only funding-rate-
    evidence contract."""
    return _RECOGNIZED_FUNDING_RATE_EVIDENCE_CONTRACT_LABEL


def _recognized_bitcoin_cycle_timing_evidence_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-bitcoin-cycle-timing-
    evidence-contract record.

    Recognizing the bitcoin-cycle-timing-evidence contract records, on paper,
    that the Block 123 Crypto-D1 Bitcoin Cycle Timing Evidence Contract is
    COMPLETE. It is a higher-level macro timing filter inserted before the Daily
    Alpha Brief contract. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. It records only that the
    research-only paper chain now has a contract that converts the BTC
    364-day / 1064-day cycle idea into research-only timing evidence -- days
    since the latest ATH, distance to the ~364-day cycle-bottom window,
    previous ATH-to-bottom and bottom-to-next-ATH duration comparisons, an
    early/active/late/expired cycle-bottom watch zone, an optional
    drawdown-from-ATH, and a caution/accumulation-watch/recovery-watch/no-signal
    evidence stance -- under the core rule that cycle timing tells us when to pay
    attention, not when to buy. It fetches no BTC data, calls no API, inspects no
    dataset, acquires/loads no data, and runs no QA, baseline, backtest,
    simulation, paper/live, broker/exchange, or automation; every number is
    computed from static input fields only. A fresh record (with fresh lists) is
    returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "bitcoin_cycle_timing_evidence_contract_id": (
            "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
        ),
        "label": _RECOGNIZED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract"
        ),
        "schema_constant": "BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION",
        "schema_version": (
            _BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": (
            _BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_NEXT_ACTION
        ),
        "reason": (
            "Read-only recognition of the Crypto-D1 Bitcoin Cycle Timing "
            "Evidence Contract, BUILT in Block 123 as a higher-level macro "
            "timing filter inserted before the Daily Alpha Brief contract. It "
            "records, on paper, that the research-only contract converting the "
            "BTC 364-day / 1064-day cycle idea into research-only timing "
            "evidence (an early/active/late/expired cycle-bottom watch zone and "
            "a caution/accumulation-watch/recovery-watch/no-signal evidence "
            "stance) now exists; it authorizes nothing and executes nothing: no "
            "BTC data fetch, API call, dataset inspection, real data "
            "acquisition, dataset loading, QA, baseline, backtest, simulation, "
            "trade signal, order placement, Telegram trade command, paper/live, "
            "automation, or runtime/registry/dashboard write is unlocked. Under "
            "the core rule that cycle timing tells us when to pay attention, not "
            "when to buy, every timing signal is attention-only evidence that "
            "always requires independent confirmation before it can be used in "
            "any later research protocol; evidence is never converted into "
            "permission. The only next step is to BUILD a research-only Crypto-D1 "
            "Daily Alpha Brief Research Contract, still on paper, treating "
            "cycle-timing signals as external research evidence only and never as "
            "execution permission."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_bitcoin_cycle_timing_evidence_contract() -> dict[
    str, Any
]:
    """The latest recognized research-only bitcoin-cycle-timing-evidence-
    contract record."""
    return _recognized_bitcoin_cycle_timing_evidence_contract()


def get_latest_completed_bitcoin_cycle_timing_evidence_contract_label() -> str:
    """Human label for the latest recognized research-only bitcoin-cycle-timing-
    evidence contract."""
    return _RECOGNIZED_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_LABEL


def _recognized_daily_alpha_brief_research_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-daily-alpha-brief-
    research-contract record.

    Recognizing the daily-alpha-brief-research contract records, on paper, that
    the Block 125 Crypto-D1 Daily Alpha Brief Research Contract is COMPLETE. It
    is the read-only contract that defines how SPARTA assembles a daily crypto
    alpha brief from already-approved static evidence inputs only -- the
    external-bot, hyperliquid-whale, funding-rate, and bitcoin-cycle-timing
    evidence lanes -- into a deterministic structured brief with an overall
    research decision and stance. It is NOT an execution bundle: it authorizes
    nothing, executes nothing, and unlocks no real capability. Under its core
    rule, the brief tells us what to watch and research, never what to trade;
    the highest stance it can produce is WATCH / RESEARCH_ONLY and it never
    produces a buy/sell/long/short/entry/exit/order instruction. It fetches no
    data, calls no API, inspects no dataset, acquires/loads no data, and runs no
    QA, baseline, backtest, simulation, paper/live, broker/exchange, or
    automation; every field is derived from static input only. A fresh record
    (with fresh lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "daily_alpha_brief_research_contract_id": (
            "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Daily Alpha Brief Research Contract"
        ),
        "label": _RECOGNIZED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_daily_alpha_brief_research_contract"
        ),
        "schema_constant": "DAILY_ALPHA_BRIEF_SCHEMA_VERSION",
        "schema_version": (
            _DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Daily Alpha Brief Research "
            "Contract, BUILT in Block 125. It records, on paper, that the "
            "research-only contract that assembles a daily crypto alpha brief "
            "from already-approved static evidence inputs only (external-bot, "
            "hyperliquid-whale, funding-rate, and bitcoin-cycle-timing evidence "
            "lanes) now exists; it authorizes nothing and executes nothing: no "
            "data fetch, API call, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Under the core rule "
            "that the brief tells us what to watch and research, never what to "
            "trade, the highest stance it can produce is WATCH / RESEARCH_ONLY; "
            "it never produces a buy/sell/long/short/entry/exit/order "
            "instruction, always requires independent confirmation, and never "
            "converts evidence into permission. The only next step is to BUILD a "
            "research-only Crypto-D1 Daily Alpha Brief Review Contract, still on "
            "paper, that reviews whether the assembled brief is reasonable."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_daily_alpha_brief_research_contract() -> dict[str, Any]:
    """The latest recognized research-only daily-alpha-brief-research-contract
    record."""
    return _recognized_daily_alpha_brief_research_contract()


def get_latest_completed_daily_alpha_brief_research_contract_label() -> str:
    """Human label for the latest recognized research-only daily-alpha-brief-
    research contract."""
    return _RECOGNIZED_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_LABEL


def _recognized_daily_alpha_brief_review_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-daily-alpha-brief-
    review-contract record.

    Recognizing the daily-alpha-brief-review contract records, on paper, that
    the Block 127 Crypto-D1 Daily Alpha Brief Review Contract is COMPLETE. It is
    the read-only contract that reviews whether an assembled daily crypto alpha
    brief is reasonable, derived from already-approved static evidence inputs
    only, and emits a research verdict (its highest verdict is READY for human
    approval). It is NOT an execution bundle: it authorizes nothing, executes
    nothing, and unlocks no real capability. Under its core rule, the review
    tells us whether the brief is reasonable to escalate for human approval,
    never what to trade; it never produces a buy/sell/long/short/entry/exit/
    order instruction. It fetches no data, calls no API, inspects no dataset,
    acquires/loads no data, and runs no QA, baseline, backtest, simulation,
    paper/live, broker/exchange, or automation; every field is derived from
    static input only. A fresh record (with fresh lists) is returned every call
    for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "daily_alpha_brief_review_contract_id": (
            "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Daily Alpha Brief Review Contract"
        ),
        "label": _RECOGNIZED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_daily_alpha_brief_review_contract"
        ),
        "schema_constant": "DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION",
        "schema_version": (
            _DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": _DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_NEXT_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Daily Alpha Brief Review "
            "Contract, BUILT in Block 127. It records, on paper, that the "
            "research-only contract that reviews whether an assembled daily "
            "crypto alpha brief is reasonable -- derived from already-approved "
            "static evidence inputs only (external-bot, hyperliquid-whale, "
            "funding-rate, and bitcoin-cycle-timing evidence lanes) -- now "
            "exists; it authorizes nothing and executes nothing: no data fetch, "
            "API call, dataset inspection, real data acquisition, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, order "
            "placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Under the core rule "
            "that the review tells us whether the brief is reasonable to "
            "escalate for human approval, never what to trade, its highest "
            "verdict is READY; it never produces a buy/sell/long/short/entry/"
            "exit/order instruction, always requires independent confirmation, "
            "and never converts evidence into permission. The only next step is "
            "to BUILD a research-only Crypto-D1 Daily Alpha Brief Approval "
            "Contract, still on paper, that records a human approval decision "
            "over a reviewed brief."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_daily_alpha_brief_review_contract() -> dict[str, Any]:
    """The latest recognized research-only daily-alpha-brief-review-contract
    record."""
    return _recognized_daily_alpha_brief_review_contract()


def get_latest_completed_daily_alpha_brief_review_contract_label() -> str:
    """Human label for the latest recognized research-only daily-alpha-brief-
    review contract."""
    return _RECOGNIZED_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_LABEL


def _recognized_daily_alpha_brief_approval_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-daily-alpha-brief-
    approval-contract record.

    Recognizing the daily-alpha-brief-approval contract records, on paper, that
    the Block 129 Crypto-D1 Daily Alpha Brief Approval Contract is COMPLETE. It
    is the read-only contract that records a human approval decision over a
    reviewed daily crypto alpha brief, derived from already-approved static
    evidence inputs only. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. Under its core rule, an
    APPROVED verdict means only that the reviewed brief may be filed as a
    research record -- never what to trade; it never produces a buy/sell/long/
    short/entry/exit/order instruction. It fetches no data, calls no API,
    inspects no dataset, acquires/loads no data, and runs no QA, baseline,
    backtest, simulation, paper/live, broker/exchange, or automation; every
    field is derived from static input only. A fresh record (with fresh lists)
    is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "daily_alpha_brief_approval_contract_id": (
            "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Daily Alpha Brief Approval Contract"
        ),
        "label": _RECOGNIZED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract"
        ),
        "schema_constant": "DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION",
        "schema_version": (
            _DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Daily Alpha Brief Approval "
            "Contract, BUILT in Block 129. It records, on paper, that the "
            "research-only contract that records a human approval decision over "
            "a reviewed daily crypto alpha brief -- derived from already-"
            "approved static evidence inputs only (external-bot, hyperliquid-"
            "whale, funding-rate, and bitcoin-cycle-timing evidence lanes) -- "
            "now exists; it authorizes nothing and executes nothing: no data "
            "fetch, API call, dataset inspection, real data acquisition, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, order "
            "placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Under the core rule "
            "that an approval only files the reviewed brief as a research "
            "record, never as a trade, its highest verdict is APPROVED; it never "
            "produces a buy/sell/long/short/entry/exit/order instruction, always "
            "requires independent confirmation, and never converts evidence into "
            "permission. With the research-only external-evidence sub-chain "
            "(research -> review -> approval) now complete, the only next step is "
            "the human-controlled real-data QA boundary decision: a human "
            "judgment about whether to ever cross into real-data QA. That "
            "boundary decision is not a build step and not an authorization; it "
            "fetches no data, runs no QA/baseline/backtest, places no order, and "
            "writes no runtime artifact. real_data_qa and baseline stay BLOCKED "
            "and the paper/micro-live gates stay LOCKED unless a separate, "
            "future, human-approved boundary contract is built."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_daily_alpha_brief_approval_contract() -> dict[str, Any]:
    """The latest recognized research-only daily-alpha-brief-approval-contract
    record."""
    return _recognized_daily_alpha_brief_approval_contract()


def get_latest_completed_daily_alpha_brief_approval_contract_label() -> str:
    """Human label for the latest recognized research-only daily-alpha-brief-
    approval contract."""
    return _RECOGNIZED_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_LABEL


def _recognized_cohort_independence_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized-cohort-independence /
    correlation-penalty-contract record.

    Recognizing the cohort-independence contract records, on paper, that the
    Block 132 Crypto-D1 Cohort Independence / Correlation Penalty Contract is
    COMPLETE. It is a research-only evidence/scoring support contract: given a
    set of already-booked paper positions, it scores whether they form genuinely
    independent cohorts or merely correlated/duplicate ones (sharing symbol+
    direction, macro event, market regime, open/close timing window, or signal
    family) and reports whether the independent-booked-cohort sample can SUPPORT
    a promote-to-review judgment. It is NOT an execution bundle: it authorizes
    nothing, executes nothing, and unlocks no real capability. It fetches no
    data, calls no API, inspects no dataset, acquires/loads no data, and runs no
    QA, baseline, backtest, simulation, paper/live, broker/exchange, or
    automation; every field is derived from static input only. Its highest
    output, can_support_promote_to_review, is a research-support signal only --
    never a trade, order, or authorization. A fresh record (with fresh lists) is
    returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "cohort_independence_contract_id": (
            "CRYPTO_D1_COHORT_INDEPENDENCE_CORRELATION_PENALTY_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Cohort Independence / Correlation Penalty Contract"
        ),
        "label": _RECOGNIZED_COHORT_INDEPENDENCE_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_cohort_independence_correlation_penalty_contract"
        ),
        "schema_constant": "COHORT_INDEPENDENCE_SCHEMA_VERSION",
        "schema_version": (
            _COHORT_INDEPENDENCE_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Cohort Independence / "
            "Correlation Penalty Contract, BUILT in Block 132. It records, on "
            "paper, that the research-only evidence/scoring support contract -- "
            "which scores whether a set of already-booked paper positions forms "
            "genuinely independent cohorts or merely correlated/duplicate ones "
            "(sharing symbol+direction, macro event, market regime, open/close "
            "timing window, or signal family) and reports whether the "
            "independent-booked-cohort sample can SUPPORT a promote-to-review "
            "judgment -- now exists; it authorizes nothing and executes nothing: "
            "no data fetch, API call, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Its highest output is "
            "a research-support signal (can_support_promote_to_review), never a "
            "buy/sell/long/short/entry/exit/order instruction; it always requires "
            "independent confirmation and never converts evidence into "
            "permission. Registering it is purely additive latest-completed "
            "metadata: it does not advance the global stage. The only next step "
            "remains the human-controlled real-data QA boundary decision -- a "
            "human judgment about whether to ever cross into real-data QA -- "
            "which is not a build step and not an authorization. real_data_qa and "
            "baseline stay BLOCKED and the paper/micro-live gates stay LOCKED "
            "unless a separate, future, human-approved boundary contract is built."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_cohort_independence_contract() -> dict[str, Any]:
    """The latest recognized research-only cohort-independence / correlation-
    penalty-contract record."""
    return _recognized_cohort_independence_contract()


def get_latest_completed_cohort_independence_contract_label() -> str:
    """Human label for the latest recognized research-only cohort-independence /
    correlation-penalty contract."""
    return _RECOGNIZED_COHORT_INDEPENDENCE_CONTRACT_LABEL


def _recognized_real_data_qa_boundary_decision_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized human-controlled Real
    Data QA Boundary Decision contract record.

    Recognizing the boundary-decision contract records, on paper, that the Block
    134 Crypto-D1 Real Data QA Boundary Decision Contract is COMPLETE. It is the
    research-only paper contract that DEFINES the structured human decision
    packet/gate that must be reviewed BEFORE any Real Data QA may even be planned.
    Given a static, caller-supplied evidence summary it assigns exactly one
    outcome (BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_DECISION) and assembles the
    packet for a human; even its most favourable outcome only readies that packet
    and authorizes nothing. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. It fetches no data, calls no
    API, inspects no dataset, acquires/loads no data, and runs no QA, baseline,
    backtest, simulation, paper/live, broker/exchange, or automation; every field
    is derived from static input only. Its highest output, READY_FOR_HUMAN_
    DECISION, is a research-support signal only -- never a trade, order, or
    authorization, and never an unlock of real_data_qa. A fresh record (with fresh
    lists) is returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "real_data_qa_boundary_decision_contract_id": (
            "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Real Data QA Boundary Decision Contract"
        ),
        "label": _RECOGNIZED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract"
        ),
        "schema_constant": "RDQ_BOUNDARY_SCHEMA_VERSION",
        "schema_version": (
            _REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Real Data QA Boundary "
            "Decision Contract, BUILT in Block 134. It records, on paper, that "
            "the research-only paper contract -- which defines the structured "
            "human decision packet/gate reviewed BEFORE any Real Data QA may even "
            "be planned, assigning a static evidence summary exactly one outcome "
            "(BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_DECISION) and assembling "
            "that packet for a human -- now exists; it authorizes nothing and "
            "executes nothing: no data fetch, API call, dataset inspection, real "
            "data acquisition, dataset loading, QA, baseline, backtest, "
            "simulation, trade signal, order placement, Telegram trade command, "
            "paper/live, automation, or runtime/registry/dashboard write is "
            "unlocked. Its highest outcome, READY_FOR_HUMAN_DECISION, only readies "
            "a packet for human review, never a buy/sell/long/short/entry/exit/"
            "order instruction and never an unlock of real_data_qa; it always "
            "requires independent confirmation and never converts evidence into "
            "permission. Registering it is purely additive latest-completed "
            "metadata: it does not advance the global stage. The only next step "
            "remains the human-controlled real-data QA boundary decision -- a "
            "human judgment about whether to ever cross into real-data QA -- "
            "which is not a build step and not an authorization. real_data_qa and "
            "baseline stay BLOCKED and the paper/micro-live gates stay LOCKED "
            "unless a separate, future, human-approved step provides explicit "
            "authorization."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_real_data_qa_boundary_decision_contract() -> dict[str, Any]:
    """The latest recognized research-only human-controlled Real Data QA
    boundary-decision-contract record."""
    return _recognized_real_data_qa_boundary_decision_contract()


def get_latest_completed_real_data_qa_boundary_decision_contract_label() -> str:
    """Human label for the latest recognized research-only human-controlled Real
    Data QA boundary-decision contract."""
    return _RECOGNIZED_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_LABEL


def _recognized_real_data_qa_human_approval_packet_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized Real Data QA Human
    Approval Packet contract record.

    Recognizing the human-approval-packet contract records, on paper, that the
    Block 136 Crypto-D1 Real Data QA Human Approval Packet Contract is COMPLETE. It
    is the research-only paper contract that DEFINES the structured eight-field
    human approval packet (plus an exact approval phrase) a person must complete
    BEFORE any Real Data QA may even be planned. Given a static, caller-supplied
    packet it assigns exactly one outcome (BLOCK / INCOMPLETE / COMPLETE); even its
    most favourable outcome, COMPLETE, only marks the packet ready for human review
    and authorizes nothing. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. It fetches no data, calls no
    API, inspects no dataset, acquires/loads no data, and runs no QA, baseline,
    backtest, simulation, paper/live, broker/exchange, or automation; every field
    is derived from static input only. A fresh record (with fresh lists) is
    returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "real_data_qa_human_approval_packet_contract_id": (
            "CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Real Data QA Human Approval Packet Contract"
        ),
        "label": _RECOGNIZED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract"
        ),
        "schema_constant": "RDQ_APPROVAL_SCHEMA_VERSION",
        "schema_version": (
            _REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Real Data QA Human Approval "
            "Packet Contract, BUILT in Block 136 (Phase A). It records, on paper, "
            "that the research-only paper contract -- which defines the structured "
            "eight-field human approval packet plus an exact approval phrase a "
            "person must complete BEFORE any Real Data QA may even be planned, "
            "assigning a static packet exactly one outcome (BLOCK / INCOMPLETE / "
            "COMPLETE) -- now exists; it authorizes nothing and executes nothing: "
            "no data fetch, API call, dataset inspection, real data acquisition, "
            "dataset loading, QA, baseline, backtest, simulation, trade signal, "
            "order placement, Telegram trade command, paper/live, automation, or "
            "runtime/registry/dashboard write is unlocked. Its highest outcome, "
            "COMPLETE, only marks the packet ready for human review, never a buy/"
            "sell/long/short/entry/exit/order instruction and never an unlock of "
            "real_data_qa; it always requires independent confirmation. "
            "Registering it is purely additive latest-completed metadata: it does "
            "not advance the global stage. real_data_qa and baseline stay BLOCKED "
            "and the paper/micro-live gates stay LOCKED unless a separate, future, "
            "human-approved step provides explicit authorization."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_real_data_qa_human_approval_packet_contract() -> dict[str, Any]:
    """The latest recognized research-only Real Data QA human-approval-packet-
    contract record."""
    return _recognized_real_data_qa_human_approval_packet_contract()


def get_latest_completed_real_data_qa_human_approval_packet_contract_label() -> str:
    """Human label for the latest recognized research-only Real Data QA human-
    approval-packet contract."""
    return _RECOGNIZED_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_LABEL


def _recognized_real_data_qa_readiness_checklist_contract() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized Real Data QA Readiness
    Checklist contract record.

    Recognizing the readiness-checklist contract records, on paper, that the Block
    136 Crypto-D1 Real Data QA Readiness Checklist Contract is COMPLETE. It is the
    research-only paper contract that DEFINES the eight-item readiness checklist
    that must ALL pass BEFORE a human is even asked to approve Real Data QA. Given
    a static, caller-supplied payload it assigns exactly one outcome (BLOCK /
    NOT_READY / READY); even its most favourable outcome, READY, only means the
    checklist passed and this is ready for a SEPARATE human approval review -- it
    authorizes nothing. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. It fetches no data, calls no
    API, inspects no dataset, acquires/loads no data, and runs no QA, baseline,
    backtest, simulation, paper/live, broker/exchange, or automation; every field
    is derived from static input only. A fresh record (with fresh lists) is
    returned every call for mutation isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "real_data_qa_readiness_checklist_contract_id": (
            "CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
        ),
        "name": (
            "Crypto-D1 Real Data QA Readiness Checklist Contract"
        ),
        "label": _RECOGNIZED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract"
        ),
        "schema_constant": "RDQ_READINESS_SCHEMA_VERSION",
        "schema_version": (
            _REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the Crypto-D1 Real Data QA Readiness "
            "Checklist Contract, BUILT in Block 136 (Phase B). It records, on "
            "paper, that the research-only paper contract -- which defines the "
            "eight-item readiness checklist that must ALL pass BEFORE a human is "
            "even asked to approve Real Data QA, assigning a static payload exactly "
            "one outcome (BLOCK / NOT_READY / READY) -- now exists; it authorizes "
            "nothing and executes nothing: no data fetch, API call, dataset "
            "inspection, real data acquisition, dataset loading, QA, baseline, "
            "backtest, simulation, trade signal, order placement, Telegram trade "
            "command, paper/live, automation, or runtime/registry/dashboard write "
            "is unlocked. Its highest outcome, READY, only means the checklist "
            "passed and this is ready for a separate human approval review, never "
            "a buy/sell/long/short/entry/exit/order instruction and never an "
            "unlock of real_data_qa; it always requires independent confirmation. "
            "Registering it is purely additive latest-completed metadata: it does "
            "not advance the global stage. The only next step remains the human-"
            "controlled real-data QA boundary decision. real_data_qa and baseline "
            "stay BLOCKED and the paper/micro-live gates stay LOCKED unless a "
            "separate, future, human-approved step provides explicit authorization."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_real_data_qa_readiness_checklist_contract() -> dict[str, Any]:
    """The latest recognized research-only Real Data QA readiness-checklist-
    contract record."""
    return _recognized_real_data_qa_readiness_checklist_contract()


def get_latest_completed_real_data_qa_readiness_checklist_contract_label() -> str:
    """Human label for the latest recognized research-only Real Data QA readiness-
    checklist contract."""
    return _RECOGNIZED_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_LABEL


def _recognized_overnight_research_autopilot_controller() -> dict[str, Any]:
    """Build (fresh each call) the read-only recognized Overnight Research Autopilot
    Controller record.

    Recognizing the autopilot controller records, on paper, that the Block 152
    SPARTA Overnight Research Autopilot Controller is COMPLETE. It is a research-
    only PLANNING controller that, given a static, caller-supplied status summary,
    reasons -- on paper only -- over which safe research-only paper bundles to
    prepare next, which paths each may touch, which scoped tests to run, and a
    commit/push policy that keeps every commit and every push gated behind explicit
    per-run human approval. It is NOT an execution bundle: it authorizes nothing,
    executes nothing, and unlocks no real capability. It stages nothing, commits
    nothing, pushes nothing, fetches no data, calls no API, inspects no dataset,
    acquires/loads no data, and runs no QA, baseline, backtest, simulation, paper/
    live, broker/exchange, or automation; every field is derived from static input
    only. A fresh record (with fresh lists) is returned every call for mutation
    isolation.
    """
    families = _protocol_candidate_families()
    record: dict[str, Any] = {
        "overnight_research_autopilot_controller_id": (
            "SPARTA_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER"
        ),
        "name": "SPARTA Overnight Research Autopilot Controller",
        "label": _RECOGNIZED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL,
        "module": (
            "sparta_commander."
            "strategy_factory_overnight_research_autopilot_controller"
        ),
        "schema_constant": "CONTROLLER_SCHEMA_VERSION",
        "schema_version": (
            _OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_SCHEMA_VERSION
        ),
        "validates_protocol_id": _PROTOCOL_ID,
        "validates_protocol_name": _PROTOCOL_NAME,
        "mode": REGISTRY_MODE,
        "defined": True,
        "complete": True,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "per_run_push_approval_required": True,
        "requires_independent_confirmation": True,
        "research_universe": [str(a) for a in _PROTOCOL_UNIVERSE],
        "market_type": _PROTOCOL_MARKET_TYPE,
        "timeframe": _PROTOCOL_TIMEFRAME,
        "candidate_family_ids": [f["family_id"] for f in families],
        "candidate_family_names": [f["name"] for f in families],
        "stage": CURRENT_STAGE,
        "next_gate": CURRENT_STAGE,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "reason": (
            "Read-only recognition of the SPARTA Overnight Research Autopilot "
            "Controller, BUILT in Block 152. It records, on paper, that the "
            "research-only PLANNING controller -- which reasons over a static "
            "status summary to plan which safe research-only paper bundles to "
            "prepare next, the only paths each may touch, the scoped tests to run, "
            "and a commit/push policy that keeps every commit and every push gated "
            "behind explicit per-run human approval -- now exists; it authorizes "
            "nothing and executes nothing: no staging, no commit, no push, no data "
            "fetch, API call, dataset inspection, real data acquisition, dataset "
            "loading, QA, baseline, backtest, simulation, trade signal, order "
            "placement, Telegram trade command, paper/live, automation, or runtime/"
            "registry/dashboard write is unlocked. It is a planner, not an actor, "
            "and never converts a research judgment into permission; every prepared "
            "bundle still requires explicit human approval before any commit and "
            "explicit per-run human approval before any push, never a buy/sell/long/"
            "short/entry/exit/order instruction and never an unlock of "
            "real_data_qa; it always requires independent confirmation. Registering "
            "it is purely additive latest-completed metadata: it does not advance "
            "the global stage, which remains the human-controlled real-data QA "
            "boundary decision and must not imply automatic execution or auto-push. "
            "real_data_qa and baseline stay BLOCKED and the paper/micro-live gates "
            "stay LOCKED unless a separate, future, human-approved step provides "
            "explicit authorization."
        ),
    }
    record.update(_BUNDLE_LOCKED_CAPABILITIES)
    return record


def get_latest_completed_overnight_research_autopilot_controller() -> dict[str, Any]:
    """The latest recognized research-only Overnight Research Autopilot Controller
    record."""
    return _recognized_overnight_research_autopilot_controller()


def get_latest_completed_overnight_research_autopilot_controller_label() -> str:
    """Human label for the latest recognized research-only Overnight Research
    Autopilot Controller."""
    return _RECOGNIZED_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL


def get_current_stage() -> str:
    """The current backbone stage after the latest completed bundle."""
    return CURRENT_STAGE


def get_next_required_action() -> str:
    """The single next required (research-only) action."""
    return NEXT_REQUIRED_ACTION


def get_registry_safety_posture() -> dict[str, Any]:
    """Read-only safety posture; every real-world capability stays blocked."""
    return dict(REGISTRY_SAFETY_POSTURE)
