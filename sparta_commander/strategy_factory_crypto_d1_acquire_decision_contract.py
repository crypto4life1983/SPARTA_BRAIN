"""SPARTA Offline Strategy Factory - CRYPTO-D1 ACQUIRE DECISION CONTRACT.

Bundle 42 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper acquire-decision contract template* builder: it
consumes a Bundle 41 crypto-d1 intake reconciliation contract and, only when
that reconciliation contract is active with reconciliation_decision ==
READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT and next_gate ==
CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED, produces a deterministic,
read-only contract describing how a human operator would later record an
acquire / no-acquire decision for the Crypto-D1 source on paper. It defines an
acquire-decision contract template only -- it acquires nothing, inspects no
data, decides nothing in runtime, writes no report file, is NOT a written
report, NOT a live system, NOT a data acquisition, NOT a QA pass, NOT a
baseline.

Reaching an active acquire-decision contract unlocks NOTHING real. An approved
acquire decision only moves, on paper, to a future source-class contract: it
acquires no data, inspects no data, approves no QA, approves no baseline,
approves no real-strategy backtest path, and unlocks no real strategy intake.
The deferred execution items (qa_run, qa_pass_or_accepted_qa_warn,
baseline_backtest_output) stay blocked and deferred.

It never runs Strategy Factory, never acquires data, never inspects, loads,
validates, transforms, or computes on real data, never inspects market data,
never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never fetches data, never opens or reads any
Crypto-D1 dataset file, qa_report, manifest, checksum, freeze record, fees
file, or baseline output, and executes nothing. It opens no network, spawns no
subprocess, writes no file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Public API:
  - ACQUIRE_SCHEMA_VERSION
  - DEFAULT_ACQUIRE_LABEL
  - ACQUIRE_STATUS
  - ACQUIRE_SAFETY_POSTURE
  - ACQUIRE_STATE_ACTIVE
  - ACQUIRE_STATE_BLOCKED
  - ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT
  - ACQUIRE_DECISION_NEEDS_MORE_INFO
  - ACQUIRE_DECISION_PARKED
  - ACQUIRE_DECISION_REJECTED
  - ALLOWED_ACQUIRE_DECISIONS
  - NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED
  - NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION
  - NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT
  - REQUIRED_OPERATOR_DECISION_FIELDS
  - REQUIRED_OPERATOR_ATTESTATION_FIELDS
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_PENDING_ITEMS_AFTER_DECISION
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - build_crypto_d1_acquire_decision_contract(reconciliation_contract,
        acquire_decision=None)
  - validate_crypto_d1_acquire_decision_contract(contract)
  - render_crypto_d1_acquire_decision_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract import (  # noqa: E501
    CRYPTO_D1_SCHEMA_VERSION,
    CRYPTO_D1_SAFETY_POSTURE,
    RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT,
    NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED,
)

__all__ = [
    "ACQUIRE_SCHEMA_VERSION",
    "DEFAULT_ACQUIRE_LABEL",
    "ACQUIRE_STATUS",
    "ACQUIRE_SAFETY_POSTURE",
    "ACQUIRE_STATE_ACTIVE",
    "ACQUIRE_STATE_BLOCKED",
    "ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT",
    "ACQUIRE_DECISION_NEEDS_MORE_INFO",
    "ACQUIRE_DECISION_PARKED",
    "ACQUIRE_DECISION_REJECTED",
    "ALLOWED_ACQUIRE_DECISIONS",
    "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED",
    "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
    "NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT",
    "REQUIRED_OPERATOR_DECISION_FIELDS",
    "REQUIRED_OPERATOR_ATTESTATION_FIELDS",
    "BLOCKED_EXECUTION_ITEMS",
    "REMAINING_PENDING_ITEMS_AFTER_DECISION",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "build_crypto_d1_acquire_decision_contract",
    "validate_crypto_d1_acquire_decision_contract",
    "render_crypto_d1_acquire_decision_contract_markdown",
]

ACQUIRE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_acquire_decision_contract.v1"
)
DEFAULT_ACQUIRE_LABEL = (
    "Strategy Factory Crypto-D1 Acquire Decision Contract"
)
ACQUIRE_STATUS = "READ_ONLY_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT"

ACQUIRE_STATE_ACTIVE = "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_ACTIVE"
ACQUIRE_STATE_BLOCKED = "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_BLOCKED"

ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT = (
    "ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT"
)
ACQUIRE_DECISION_NEEDS_MORE_INFO = "ACQUIRE_NEEDS_MORE_INFO"
ACQUIRE_DECISION_PARKED = "ACQUIRE_PARKED"
ACQUIRE_DECISION_REJECTED = "ACQUIRE_REJECTED"

ALLOWED_ACQUIRE_DECISIONS: tuple[str, ...] = (
    ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    ACQUIRE_DECISION_NEEDS_MORE_INFO,
    ACQUIRE_DECISION_PARKED,
    ACQUIRE_DECISION_REJECTED,
)

NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED = (
    "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED = (
    "CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED = (
    "CRYPTO_D1_ACQUIRE_DECISION_PARKED"
)
NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED = (
    "CRYPTO_D1_ACQUIRE_DECISION_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION = (
    "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
)
NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT = (
    "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-41).
ACQUIRE_SAFETY_POSTURE: dict[str, bool] = dict(CRYPTO_D1_SAFETY_POSTURE)

# Paper decision fields a human operator records when making the acquire call.
REQUIRED_OPERATOR_DECISION_FIELDS: tuple[str, ...] = (
    "operator_acquire_decision",
    "acquire_decision_rationale",
    "source_class_intent",
)

# Paper attestation fields a human operator records alongside the decision.
REQUIRED_OPERATOR_ATTESTATION_FIELDS: tuple[str, ...] = (
    "human_operator_identity_attestation",
    "no_data_acquired_attestation",
    "no_data_inspected_attestation",
    "no_qa_run_attestation",
    "no_baseline_run_attestation",
    "read_only_attestation",
)

# Execution items that stay blocked and deferred -- never approved here.
BLOCKED_EXECUTION_ITEMS: tuple[str, ...] = (
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

# Pending items that remain after the acquire decision is recorded. The acquire
# decision itself is resolved by this contract; everything else stays pending.
REMAINING_PENDING_ITEMS_AFTER_DECISION: tuple[str, ...] = (
    "source_class",
    "source_name",
    "license_tos_evidence",
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

# Real-world capabilities that remain blocked even when the acquire decision
# contract is active. An approved acquire decision unlocks NONE of these.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_strategy_intake",
    "real_data_acquisition",
    "real_data_load",
    "real_data_validation",
    "real_data_transform",
    "real_data_inspection",
    "real_data_compute",
    "real_market_data_inspection",
    "real_crypto_d1_dataset_inspection",
    "real_qa_run",
    "real_baseline_run",
    "real_backtest",
    "real_simulation",
    "real_pipeline_execution",
    "real_orchestrator_execution",
    "real_research_run",
    "real_data_fetch",
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
    "This is a crypto-d1 acquire decision contract template and is "
    "execution-free.",
    "It defines a paper acquire-decision template only and writes no report "
    "file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It approves no QA, produces no QA verdict, and approves no baseline "
    "computation.",
    "It approves no execution item and unlocks no real strategy intake.",
    "If approved, it only moves to the next paper-only source-class contract.",
    "The deferred execution items stay blocked: qa, qa acceptance, and "
    "baseline output.",
    "No Crypto-D1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator must record the acquire decision and the supporting "
    "attestation before any source-class contract is planned.",
    "No automated step may proceed without human sign-off.",
)

# Human-operator next steps. Prose only, verb-safe, advisory.
_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record an acquire or no-acquire decision with a "
    "supporting rationale on paper.",
    "A human operator must confirm no real data, dataset, broker, or live "
    "capability was touched.",
    "A human operator must decide whether the acquire decision is approved for "
    "a paper-only source-class contract.",
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
    "crypto_d1_data_acquisition",
    "crypto_d1_acquire_execution",
    "crypto_d1_acquire_decision_execution",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_market_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_qa_verdict",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
)

# Acquire-decision-specific blocked capabilities (this phase only).
_ACQUIRE_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_acquire_decision_execution",
    "crypto_d1_data_acquisition",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_qa_run",
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

_SOURCE_RECONCILIATION_CONTRACT_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 intake reconciliation reference is a paper placeholder for a "
    "human-recorded acquire decision contract."
)

_ACQUIRE_DECISION_RATIONALE_PLACEHOLDER = (
    "Operator acquire-decision rationale is a paper placeholder for a "
    "human-recorded acquire or no-acquire decision and its supporting reason."
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_intake_reconciliation_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_acquire_decision_contract_active",
    "crypto_d1_acquire_decision_contract_state",
    "crypto_d1_intake_reconciliation_contract_active",
    "crypto_d1_intake_reconciliation_decision",
    "crypto_d1_intake_reconciliation_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_reconciliation_contract_reference_placeholder",
    "acquire_decision",
    "allowed_acquire_decisions",
    "required_operator_decision_fields",
    "required_operator_attestation_fields",
    "acquire_decision_rationale_placeholder",
    "blocked_execution_items",
    "remaining_pending_items_after_decision",
    "acquire_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_intake_reconciliation_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(ACQUIRE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _normalize_decision(decision: Any) -> str:
    """Map an arbitrary decision to a known decision or empty string."""
    text = _as_text(decision)
    return text if text in ALLOWED_ACQUIRE_DECISIONS else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == ACQUIRE_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "CRYPTO_D1_ACQUIRE_DECISION_ONLY",
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
        tuple(safe.get("allowed_acquire_decisions") or ())
        == ALLOWED_ACQUIRE_DECISIONS
    )
    decision_fields_ok = (
        tuple(safe.get("required_operator_decision_fields") or ())
        == REQUIRED_OPERATOR_DECISION_FIELDS
    )
    attestation_fields_ok = (
        tuple(safe.get("required_operator_attestation_fields") or ())
        == REQUIRED_OPERATOR_ATTESTATION_FIELDS
    )
    blocked_execution_ok = (
        tuple(safe.get("blocked_execution_items") or ())
        == BLOCKED_EXECUTION_ITEMS
    )
    remaining_pending_ok = (
        tuple(safe.get("remaining_pending_items_after_decision") or ())
        == REMAINING_PENDING_ITEMS_AFTER_DECISION
    )
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    acquire_blocked_ok = (
        len(tuple(safe.get("acquire_blocked_capabilities") or ())) >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    fields_ok = (
        decisions_ok
        and decision_fields_ok
        and attestation_fields_ok
        and blocked_execution_ok
        and remaining_pending_ok
        and remaining_blocked_ok
        and acquire_blocked_ok
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
        "allowed_acquire_decisions_ok": decisions_ok,
        "required_operator_decision_fields_ok": decision_fields_ok,
        "required_operator_attestation_fields_ok": attestation_fields_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_pending_items_after_decision_ok": remaining_pending_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "acquire_blocked_capabilities_present": acquire_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_acquire_decision_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 acquire decision
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_acquire_decision_contract(
    reconciliation_contract: Any,
    acquire_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 acquire decision
    contract template.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_acquire_decision_contract_active=True) solely when the upstream
    Bundle 41 crypto-d1 intake reconciliation contract is active AND its
    reconciliation_decision is READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT AND
    its next_gate is CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED. Even when
    active, every authorization field stays False -- it defines the SHAPE of a
    paper operator acquire / no-acquire decision plus a human-operator
    recommendation only, acquires nothing, inspects no data, approves no QA, no
    baseline, and no backtest, writes no report file, writes no runtime state,
    names only placeholders, and grants nothing. Returned dicts are fresh."""
    recon = (
        reconciliation_contract
        if isinstance(reconciliation_contract, dict)
        else {}
    )

    recon_active = (
        recon.get("crypto_d1_intake_reconciliation_contract_active") is True
    )
    recon_decision = _field(recon, "reconciliation_decision")
    recon_next_gate = _field(recon, "next_gate")
    decision_ok = (
        recon_decision
        == RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
    )
    gate_ok = (
        recon_next_gate
        == NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED
    )

    contract_active = bool(recon_active and decision_ok and gate_ok)

    decision = _normalize_decision(acquire_decision)

    state = (
        ACQUIRE_STATE_ACTIVE if contract_active else ACQUIRE_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT
    elif decision == ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED
    elif decision == ACQUIRE_DECISION_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED
    elif decision == ACQUIRE_DECISION_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED
    elif decision == ACQUIRE_DECISION_REJECTED:
        next_gate = NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED
    else:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION

    contract = {
        "schema_version": ACQUIRE_SCHEMA_VERSION,
        "crypto_d1_intake_reconciliation_schema_version": (
            CRYPTO_D1_SCHEMA_VERSION
        ),
        "idea_id": _field(reconciliation_contract, "idea_id"),
        "title": _field(reconciliation_contract, "title"),
        "label": DEFAULT_ACQUIRE_LABEL,
        "status": ACQUIRE_STATUS,
        "stage": "CRYPTO_D1_ACQUIRE_DECISION_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_acquire_decision_contract_active": contract_active,
        "crypto_d1_acquire_decision_contract_state": state,
        "crypto_d1_intake_reconciliation_contract_active": bool(recon_active),
        "crypto_d1_intake_reconciliation_decision": recon_decision,
        "crypto_d1_intake_reconciliation_next_gate": recon_next_gate,
        "asset_lane": _field(reconciliation_contract, "asset_lane"),
        "timeframe_lane": _field(reconciliation_contract, "timeframe_lane"),
        "source_reconciliation_contract_reference_placeholder": (
            _SOURCE_RECONCILIATION_CONTRACT_REFERENCE_PLACEHOLDER
        ),
        "acquire_decision": decision,
        "allowed_acquire_decisions": ALLOWED_ACQUIRE_DECISIONS,
        "required_operator_decision_fields": REQUIRED_OPERATOR_DECISION_FIELDS,
        "required_operator_attestation_fields": (
            REQUIRED_OPERATOR_ATTESTATION_FIELDS
        ),
        "acquire_decision_rationale_placeholder": (
            _ACQUIRE_DECISION_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "remaining_pending_items_after_decision": (
            REMAINING_PENDING_ITEMS_AFTER_DECISION
        ),
        "acquire_blocked_capabilities": _ACQUIRE_BLOCKED_CAPABILITIES,
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
        "crypto_d1_intake_reconciliation_contract": (
            reconciliation_contract
            if isinstance(reconciliation_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_acquire_decision_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 acquire
    decision contract template. Pure; writes no file. Informational only."""
    decisions = contract.get("allowed_acquire_decisions") or ()
    decision_fields = contract.get("required_operator_decision_fields") or ()
    attestation_fields = (
        contract.get("required_operator_attestation_fields") or ()
    )
    blocked_execution = contract.get("blocked_execution_items") or ()
    remaining_pending = (
        contract.get("remaining_pending_items_after_decision") or ()
    )
    acquire_blocked = contract.get("acquire_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Crypto-D1 Acquire Decision Contract")
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-acquire-decision-contract-only, paper-only, "
        "no-data-acquisition, no-qa-run, no-baseline-run, no-data-inspection, "
        "no-real-strategy-intake-yet, research-only, and execution-free "
        "template -- it records only a paper acquire or no-acquire decision, "
        "is not wired into any runtime state, writes no report file, acquires "
        "no data, inspects no data, opens no dataset, names only placeholders, "
        "and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Reconciliation schema: "
        f"`{contract.get('crypto_d1_intake_reconciliation_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_ACQUIRE_DECISION_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 acquire decision contract active: "
        f"{contract.get('crypto_d1_acquire_decision_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_acquire_decision_contract_state', '')}"
    )
    lines.append(
        "Acquire decision: "
        f"{contract.get('acquire_decision', '')}"
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
        "Source reconciliation contract reference: "
        f"{contract.get('source_reconciliation_contract_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Allowed Acquire Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Decision Fields")
    lines.append("")
    for x in decision_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Attestation Fields")
    lines.append("")
    for x in attestation_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Acquire Decision Rationale")
    lines.append("")
    lines.append(
        "Acquire decision rationale: "
        f"{contract.get('acquire_decision_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Remaining Pending Items After Decision")
    lines.append("")
    for x in remaining_pending:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Crypto-D1 Acquire Blocked Capabilities")
    lines.append("")
    for cap in acquire_blocked:
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
        "- A human operator must record the acquire decision before any "
        "source-class contract is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
