"""SPARTA Offline Strategy Factory - CRYPTO-D1 INTAKE RECONCILIATION CONTRACT.

Bundle 41 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper reconciliation contract template* builder: it
consumes a Bundle 40 fake lane closure contract and, only when that closure
contract is active with closure_decision ==
FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR and next_gate ==
PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE and recommended_next_phase
== OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE, produces a
deterministic, read-only contract describing how a human operator would later
reconcile the Crypto-D1 intake metadata fields on paper. It defines a
reconciliation contract template only -- it reconciles nothing in runtime,
writes no report file, is NOT a written report, NOT a live system, NOT a dry
walk, NOT a pipeline, NOT an orchestrator, NOT a QA pass, NOT a baseline.

The Crypto-D1 metadata items (operator acquire decision, source class, source
name, license/TOS evidence) are PAPER fields for a human operator to reconcile
later. The Crypto-D1 execution items (qa_run, qa_pass_or_accepted_qa_warn,
baseline_backtest_output) stay BLOCKED and DEFERRED: this contract runs no QA,
produces no QA verdict, runs no baseline, inspects no data, and unlocks no real
strategy intake.

It never runs Strategy Factory, never runs the fake pipeline, never inspects,
loads, validates, transforms, or computes on real data, never inspects market
data, never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never fetches data, never opens or reads any
Crypto-D1 dataset file, qa_report, manifest, checksum, freeze record, fees
file, or baseline output, and executes nothing. It opens no network, spawns no
subprocess, writes no file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Reaching active reconciliation unlocks NOTHING real: it only recommends a human
operator reconcile the Crypto-D1 metadata fields before any acquire decision is
planned. Every item and field it names is a placeholder. It references no real
dataset, no real report file, and no real market-data path.

Public API:
  - CRYPTO_D1_SCHEMA_VERSION
  - DEFAULT_CRYPTO_D1_LABEL
  - CRYPTO_D1_STATUS
  - CRYPTO_D1_SAFETY_POSTURE
  - CRYPTO_D1_STATE_ACTIVE
  - CRYPTO_D1_STATE_BLOCKED
  - RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
  - RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION
  - RECONCILIATION_DECISION_PARK_CRYPTO_D1
  - RECONCILIATION_DECISION_REJECT_CRYPTO_D1
  - ALLOWED_RECONCILIATION_DECISIONS
  - NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED
  - NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION
  - NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW
  - CRYPTO_D1_PENDING_ITEMS
  - CRYPTO_D1_METADATA_ITEMS
  - CRYPTO_D1_EXECUTION_ITEMS_DEFERRED
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - build_crypto_d1_intake_reconciliation_contract(closure_contract,
        reconciliation_decision=None)
  - validate_crypto_d1_intake_reconciliation_contract(contract)
  - render_crypto_d1_intake_reconciliation_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_lane_closure_contract import (
    CLOSURE_SCHEMA_VERSION,
    CLOSURE_SAFETY_POSTURE,
    CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE,
    RECOMMENDED_NEXT_PHASE,
)

__all__ = [
    "CRYPTO_D1_SCHEMA_VERSION",
    "DEFAULT_CRYPTO_D1_LABEL",
    "CRYPTO_D1_STATUS",
    "CRYPTO_D1_SAFETY_POSTURE",
    "CRYPTO_D1_STATE_ACTIVE",
    "CRYPTO_D1_STATE_BLOCKED",
    "RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT",
    "RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION",
    "RECONCILIATION_DECISION_PARK_CRYPTO_D1",
    "RECONCILIATION_DECISION_REJECT_CRYPTO_D1",
    "ALLOWED_RECONCILIATION_DECISIONS",
    "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED",
    "NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION",
    "NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW",
    "CRYPTO_D1_PENDING_ITEMS",
    "CRYPTO_D1_METADATA_ITEMS",
    "CRYPTO_D1_EXECUTION_ITEMS_DEFERRED",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "build_crypto_d1_intake_reconciliation_contract",
    "validate_crypto_d1_intake_reconciliation_contract",
    "render_crypto_d1_intake_reconciliation_contract_markdown",
]

CRYPTO_D1_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_intake_reconciliation_contract.v1"
)
DEFAULT_CRYPTO_D1_LABEL = (
    "Strategy Factory Crypto-D1 Intake Reconciliation Contract"
)
CRYPTO_D1_STATUS = "READ_ONLY_CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT"

CRYPTO_D1_STATE_ACTIVE = "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_ACTIVE"
CRYPTO_D1_STATE_BLOCKED = "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_BLOCKED"

RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT = (
    "READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT"
)
RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION = (
    "NEEDS_MORE_CRYPTO_D1_RECONCILIATION"
)
RECONCILIATION_DECISION_PARK_CRYPTO_D1 = "PARK_CRYPTO_D1"
RECONCILIATION_DECISION_REJECT_CRYPTO_D1 = "REJECT_CRYPTO_D1"

ALLOWED_RECONCILIATION_DECISIONS: tuple[str, ...] = (
    RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT,
    RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION,
    RECONCILIATION_DECISION_PARK_CRYPTO_D1,
    RECONCILIATION_DECISION_REJECT_CRYPTO_D1,
)

NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED = (
    "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED = (
    "CRYPTO_D1_RECONCILIATION_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED = "CRYPTO_D1_RECONCILIATION_PARKED"
NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED = (
    "CRYPTO_D1_RECONCILIATION_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION = (
    "AWAIT_CRYPTO_D1_RECONCILIATION_DECISION"
)
NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW = (
    "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"
)

# The seven Crypto-D1 intake reconciliation items, in canonical order. The
# first four are metadata (paper) fields; the last three are execution items
# that stay blocked and deferred.
CRYPTO_D1_PENDING_ITEMS: tuple[str, ...] = (
    "operator_acquire_decision",
    "source_class",
    "source_name",
    "license_tos_evidence",
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

# Paper metadata fields a human operator reconciles later.
CRYPTO_D1_METADATA_ITEMS: tuple[str, ...] = (
    "operator_acquire_decision",
    "source_class",
    "source_name",
    "license_tos_evidence",
)

# Execution items that remain blocked and deferred -- never produced here.
CRYPTO_D1_EXECUTION_ITEMS_DEFERRED: tuple[str, ...] = (
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-40).
CRYPTO_D1_SAFETY_POSTURE: dict[str, bool] = dict(CLOSURE_SAFETY_POSTURE)

# Real-world capabilities that remain blocked even when reconciliation is
# active. Active reconciliation unlocks NONE of these.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_strategy_intake",
    "real_data_load",
    "real_data_validation",
    "real_data_transform",
    "real_data_inspection",
    "real_data_compute",
    "real_market_data_inspection",
    "real_qa_run",
    "real_baseline_run",
    "real_backtest",
    "real_simulation",
    "real_pipeline_execution",
    "real_orchestrator_execution",
    "real_research_run",
    "real_data_fetch",
    "real_crypto_d1_dataset_inspection",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "autopilot",
    "automation",
    "upload",
    "deploy",
    "promotion",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 intake reconciliation contract template and is "
    "execution-free.",
    "It defines a paper reconciliation template only and writes no report "
    "file.",
    "It writes no runtime state and inspects no data.",
    "The metadata items are paper fields for a human operator to reconcile "
    "later.",
    "The execution items stay blocked and deferred.",
    "No QA execution occurs and no QA verdict is produced.",
    "No baseline execution occurs and no real strategy intake is unlocked.",
    "No Crypto-D1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator must reconcile the metadata fields before any acquire "
    "decision is planned.",
    "No automated step may proceed without human sign-off.",
)

# Human-operator next steps after reconciliation. Prose only, verb-safe.
_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must reconcile the crypto-d1 metadata fields before any "
    "acquire decision is planned.",
    "A human operator must confirm no real data, dataset, broker, or live "
    "capability was touched.",
    "A human operator must decide whether the crypto-d1 reconciliation is "
    "ready for an acquire decision contract.",
    "No automated step may proceed without human sign-off.",
)

# Capabilities that stay blocked for every contract, regardless of state.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "data_fetch",
    "backtest",
    "simulation",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "upload",
    "autopilot",
    "promotion",
    "subprocess",
    "network",
    "file_write",
    "file_read",
    "directory_listing",
    "dashboard_runtime_update",
    "registry_file_write",
    "template_edit",
    "ledger_runtime_write",
    "runtime_approval_write",
    "runtime_safety_flag_write",
    "pipeline_execution",
    "report_file_write",
    "runtime_state_write",
    "real_strategy_intake",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_market_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_qa_verdict",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_data_fetch",
    "crypto_d1_acquire_execution",
    "crypto_d1_intake_reconciliation_execution",
)

# Crypto-D1-specific blocked capabilities (reconciliation phase only).
_CRYPTO_D1_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_intake_reconciliation_execution",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_qa_verdict",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "real_strategy_intake",
    "report_file_write",
    "runtime_state_write",
)

_AUTH_FLAGS: tuple[str, ...] = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)

_SOURCE_FAKE_LANE_CLOSURE_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Lane Closure reference is a fake placeholder for a "
    "human-reviewed crypto-d1 intake reconciliation contract."
)

_METADATA_STATUS_PLACEHOLDER = "pending_human_operator_metadata_placeholder"
_EXECUTION_STATUS_PLACEHOLDER = "blocked_and_deferred_placeholder"

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_lane_closure_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_intake_reconciliation_contract_active",
    "crypto_d1_intake_reconciliation_contract_state",
    "fake_lane_closure_contract_active",
    "fake_lane_closure_decision",
    "fake_lane_closure_next_gate",
    "fake_lane_recommended_next_phase",
    "asset_lane",
    "timeframe_lane",
    "source_fake_lane_closure_reference_placeholder",
    "reconciliation_decision",
    "allowed_reconciliation_decisions",
    "crypto_d1_pending_items",
    "crypto_d1_metadata_items",
    "crypto_d1_execution_items_deferred",
    "reconciliation_status_by_item",
    "required_human_operator_fields",
    "crypto_d1_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_lane_closure_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(CRYPTO_D1_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_RECONCILIATION_DECISIONS else ""


def _reconciliation_status_by_item() -> dict[str, str]:
    """Return a fresh per-item reconciliation status placeholder map."""
    status: dict[str, str] = {}
    for item in CRYPTO_D1_METADATA_ITEMS:
        status[item] = _METADATA_STATUS_PLACEHOLDER
    for item in CRYPTO_D1_EXECUTION_ITEMS_DEFERRED:
        status[item] = _EXECUTION_STATUS_PLACEHOLDER
    return status


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == CRYPTO_D1_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "CRYPTO_D1_RECONCILIATION_ONLY",
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    decisions_ok = (
        tuple(safe.get("allowed_reconciliation_decisions") or ())
        == ALLOWED_RECONCILIATION_DECISIONS
    )
    pending_ok = (
        tuple(safe.get("crypto_d1_pending_items") or ())
        == CRYPTO_D1_PENDING_ITEMS
    )
    metadata_ok = (
        tuple(safe.get("crypto_d1_metadata_items") or ())
        == CRYPTO_D1_METADATA_ITEMS
    )
    execution_ok = (
        tuple(safe.get("crypto_d1_execution_items_deferred") or ())
        == CRYPTO_D1_EXECUTION_ITEMS_DEFERRED
    )
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    status_map_ok = isinstance(
        safe.get("reconciliation_status_by_item"), dict
    ) and bool(safe.get("reconciliation_status_by_item"))
    human_fields_ok = (
        len(tuple(safe.get("required_human_operator_fields") or ())) >= 1
    )
    crypto_blocked_ok = (
        len(tuple(safe.get("crypto_d1_blocked_capabilities") or ())) >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    fields_ok = (
        decisions_ok
        and pending_ok
        and metadata_ok
        and execution_ok
        and remaining_blocked_ok
        and status_map_ok
        and human_fields_ok
        and crypto_blocked_ok
        and notes_ok
        and next_steps_ok
    )

    valid = bool(
        schema_ok
        and research_only
        and stage_ok
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and fields_ok
        and not missing
    )

    return {
        "valid": valid,
        "schema_version_ok": schema_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "human_approval_required": human_required,
        "executes": False,
        "all_authorization_flags_false": auth_all_false,
        "safety_all_false": safety_all_false,
        "allowed_reconciliation_decisions_ok": decisions_ok,
        "crypto_d1_pending_items_ok": pending_ok,
        "crypto_d1_metadata_items_ok": metadata_ok,
        "crypto_d1_execution_items_deferred_ok": execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "reconciliation_status_by_item_ok": status_map_ok,
        "required_human_operator_fields_present": human_fields_ok,
        "crypto_d1_blocked_capabilities_present": crypto_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_intake_reconciliation_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 intake reconciliation
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_intake_reconciliation_contract(
    closure_contract: Any,
    reconciliation_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 intake reconciliation
    contract template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_intake_reconciliation_contract_active=True) solely when the
    upstream Bundle 40 fake lane closure contract is active AND its
    closure_decision is FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR AND its next_gate
    is PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE AND its
    recommended_next_phase is
    OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE. Even when active,
    every authorization field stays False -- it defines the SHAPE of a paper
    Crypto-D1 metadata reconciliation plus a human-operator recommendation
    only, reconciles nothing real, writes no report file, writes no runtime
    state, inspects no data, opens no dataset, names only placeholders, and
    grants nothing. Returned dicts are fresh."""
    closure = closure_contract if isinstance(closure_contract, dict) else {}

    closure_active = (
        closure.get("fake_lane_closure_contract_active") is True
    )
    closure_decision = _field(closure, "closure_decision")
    closure_next_gate = _field(closure, "next_gate")
    closure_phase = _field(closure, "recommended_next_phase")
    decision_ok = (
        closure_decision
        == CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR
    )
    gate_ok = (
        closure_next_gate
        == NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE
    )
    phase_ok = closure_phase == RECOMMENDED_NEXT_PHASE

    contract_active = bool(
        closure_active and decision_ok and gate_ok and phase_ok
    )

    decision = _normalize_decision(reconciliation_decision)

    state = (
        CRYPTO_D1_STATE_ACTIVE if contract_active else CRYPTO_D1_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW
    elif decision == (
        RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
    ):
        next_gate = NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED
    elif decision == (
        RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION
    ):
        next_gate = NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED
    elif decision == RECONCILIATION_DECISION_PARK_CRYPTO_D1:
        next_gate = NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED
    elif decision == RECONCILIATION_DECISION_REJECT_CRYPTO_D1:
        next_gate = NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED
    else:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION

    contract = {
        "schema_version": CRYPTO_D1_SCHEMA_VERSION,
        "fake_lane_closure_schema_version": CLOSURE_SCHEMA_VERSION,
        "idea_id": _field(closure_contract, "idea_id"),
        "title": _field(closure_contract, "title"),
        "label": DEFAULT_CRYPTO_D1_LABEL,
        "status": CRYPTO_D1_STATUS,
        "stage": "CRYPTO_D1_RECONCILIATION_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_intake_reconciliation_contract_active": contract_active,
        "crypto_d1_intake_reconciliation_contract_state": state,
        "fake_lane_closure_contract_active": bool(closure_active),
        "fake_lane_closure_decision": closure_decision,
        "fake_lane_closure_next_gate": closure_next_gate,
        "fake_lane_recommended_next_phase": closure_phase,
        "asset_lane": _field(closure_contract, "asset_lane"),
        "timeframe_lane": _field(closure_contract, "timeframe_lane"),
        "source_fake_lane_closure_reference_placeholder": (
            _SOURCE_FAKE_LANE_CLOSURE_REFERENCE_PLACEHOLDER
        ),
        "reconciliation_decision": decision,
        "allowed_reconciliation_decisions": ALLOWED_RECONCILIATION_DECISIONS,
        "crypto_d1_pending_items": CRYPTO_D1_PENDING_ITEMS,
        "crypto_d1_metadata_items": CRYPTO_D1_METADATA_ITEMS,
        "crypto_d1_execution_items_deferred": (
            CRYPTO_D1_EXECUTION_ITEMS_DEFERRED
        ),
        "reconciliation_status_by_item": _reconciliation_status_by_item(),
        "required_human_operator_fields": CRYPTO_D1_METADATA_ITEMS,
        "crypto_d1_blocked_capabilities": _CRYPTO_D1_BLOCKED_CAPABILITIES,
        "remaining_real_world_capabilities_blocked": (
            REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "safety_posture": _safety_posture(),
        "next_gate": next_gate,
        "operator_notes": _OPERATOR_NOTES,
        "human_operator_required_next_steps": (
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "approved_for_research": False,
        "execution_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "data_fetch_authorized": False,
        "backtest_authorized": False,
        "promotion_authorized": False,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "fake_lane_closure_contract": (
            closure_contract if isinstance(closure_contract, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_intake_reconciliation_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 intake
    reconciliation contract template. Pure; writes no file. Informational
    only."""
    decisions = contract.get("allowed_reconciliation_decisions") or ()
    pending = contract.get("crypto_d1_pending_items") or ()
    metadata = contract.get("crypto_d1_metadata_items") or ()
    execution = contract.get("crypto_d1_execution_items_deferred") or ()
    status_map = contract.get("reconciliation_status_by_item") or {}
    human_fields = contract.get("required_human_operator_fields") or ()
    crypto_blocked = contract.get("crypto_d1_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Intake Reconciliation Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-intake-reconciliation-contract-only, paper-only, "
        "no-qa-run, no-baseline-run, no-data-inspection, "
        "no-real-strategy-intake-yet, research-only, and execution-free "
        "template -- it reconciles only crypto-d1 metadata fields on paper, is "
        "not wired into any runtime state, writes no report file, inspects no "
        "data, opens no dataset, names only placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Closure schema: "
        f"`{contract.get('fake_lane_closure_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_RECONCILIATION_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 intake reconciliation contract active: "
        f"{contract.get('crypto_d1_intake_reconciliation_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_intake_reconciliation_contract_state', '')}"
    )
    lines.append(
        "Reconciliation decision: "
        f"{contract.get('reconciliation_decision', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source Reference")
    lines.append("")
    lines.append(
        "Source fake lane closure reference: "
        f"{contract.get('source_fake_lane_closure_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Crypto-D1 Pending Items")
    lines.append("")
    for x in pending:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Crypto-D1 Metadata Items (Paper Fields)")
    lines.append("")
    for x in metadata:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Crypto-D1 Execution Items (Blocked And Deferred)")
    lines.append("")
    for x in execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Reconciliation Status By Item")
    lines.append("")
    for key, value in status_map.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Required Human Operator Fields")
    lines.append("")
    for x in human_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Reconciliation Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Crypto-D1 Blocked Capabilities")
    lines.append("")
    for cap in crypto_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Remaining Real-World Capabilities Blocked")
    lines.append("")
    for cap in remaining_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in contract.get("blocked_capabilities") or ():
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Human Operator Required Next Steps")
    lines.append("")
    for step in next_steps:
        lines.append(f"- {step}")
    lines.append("")
    lines.append("## Operator Notes")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in posture.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for key, value in validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human operator must reconcile the crypto-d1 metadata fields "
        "before any acquire decision is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
