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
]

REGISTRY_VERSION = "v1"
REGISTRY_MODE = "RESEARCH_ONLY"

# Post-Bundle-47 backbone state: the execution-boundary contract exists on
# paper, but nothing downstream is authorized. The pipeline is still blocked
# until the next research-only contract is DEFINED.
CURRENT_STAGE = (
    "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_"
    "STILL_BLOCKED_NEXT_CONTRACT_REQUIRED"
)
NEXT_REQUIRED_ACTION = "DEFINE_NEXT_RESEARCH_ONLY_CRYPTO_D1_POST_BOUNDARY_CONTRACT"

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


_BUNDLES: tuple[dict[str, Any], ...] = (
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
        next_gate=CURRENT_STAGE,
        reason=(
            "Read-only execution-boundary paper contract only. It authorizes "
            "nothing and executes nothing: no data acquisition, data fetch, "
            "data inspection, QA, baseline, backtest, simulation, paper, live, "
            "broker, exchange, or automation is unlocked."
        ),
    ),
)


def _clone_bundle(record: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow, mutation-safe copy of one bundle record."""
    return dict(record)


def list_registered_bundles() -> list[dict[str, Any]]:
    """All registered bundle records (display-only), ascending by number."""
    return [_clone_bundle(b) for b in _BUNDLES]


def list_completed_bundles() -> list[dict[str, Any]]:
    """Registered bundles whose contract is complete (display-only)."""
    return [_clone_bundle(b) for b in _BUNDLES if b["complete"] is True]


def get_latest_completed_bundle() -> dict[str, Any]:
    """The highest-numbered completed bundle record."""
    completed = [b for b in _BUNDLES if b["complete"] is True]
    latest = max(completed, key=lambda b: b["bundle_number"])
    return _clone_bundle(latest)


def get_bundle_by_number(number: int) -> dict[str, Any] | None:
    """The bundle record with the given number, or None."""
    for b in _BUNDLES:
        if b["bundle_number"] == number:
            return _clone_bundle(b)
    return None


def get_bundle_by_id(bundle_id: str) -> dict[str, Any] | None:
    """The bundle record with the given id (e.g. 'BUNDLE_47'), or None."""
    for b in _BUNDLES:
        if b["bundle_id"] == bundle_id:
            return _clone_bundle(b)
    return None


def get_latest_completed_bundle_label() -> str:
    """Human label 'Bundle N - Name' for the latest completed bundle."""
    latest = get_latest_completed_bundle()
    return "Bundle " + str(latest["bundle_number"]) + " - " + latest["name"]


def get_current_stage() -> str:
    """The current backbone stage after the latest completed bundle."""
    return CURRENT_STAGE


def get_next_required_action() -> str:
    """The single next required (research-only) action."""
    return NEXT_REQUIRED_ACTION


def get_registry_safety_posture() -> dict[str, Any]:
    """Read-only safety posture; every real-world capability stays blocked."""
    return dict(REGISTRY_SAFETY_POSTURE)
