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
# the latest recognized *research-plan approval contract* is Block 107.
# Recognizing the research-plan approval contract unlocks nothing real: the only
# next step is a research-only planning step -- BUILD a candidate research
# *design* contract, still on paper. No real acquisition, QA, baseline, backtest,
# paper/live, broker/exchange, or automation is unlocked.
CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT_REQUIRED"
)
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
# Next required action: build the research-only candidate research *design*
# contract, still on paper -- the next research-only planning step after the
# Block 107 approval. It authorizes nothing and unlocks nothing real.
NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_DESIGN_CONTRACT"
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
        "next_required_action": NEXT_REQUIRED_ACTION,
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
            "registry/dashboard write is unlocked. The only next step is to BUILD "
            "a research-only candidate research design contract, still on paper."
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


def get_current_stage() -> str:
    """The current backbone stage after the latest completed bundle."""
    return CURRENT_STAGE


def get_next_required_action() -> str:
    """The single next required (research-only) action."""
    return NEXT_REQUIRED_ACTION


def get_registry_safety_posture() -> dict[str, Any]:
    """Read-only safety posture; every real-world capability stays blocked."""
    return dict(REGISTRY_SAFETY_POSTURE)
