"""SPARTA Offline Strategy Factory - SAFETY KILL-SWITCH / APPROVAL GATE
CONTRACT (TEMPLATE) v1.

Bundle 26 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only safety kill-switch / approval gate contract template*
builder: it consumes a Bundle 25 decision ledger contract and, only when that
contract is active with next_gate == SAFETY_KILL_SWITCH_CONTRACT_REQUIRED,
produces a deterministic, read-only *template* describing the shape a future
hard safety approval gate must take before any fake-artifact workflow may move
forward. It defines a safety gate contract template only -- NOT a live gate.

It never writes runtime safety state, never persists an approval, never writes
a ledger file, never updates runtime state, never updates dashboard files,
never orchestrates anything, never performs research, never backtests, never
simulates, never fetches, inspects, loads, validates, transforms, or computes
on real data, and executes nothing. It opens no network, spawns no subprocess,
writes no file, touches no broker/exchange/order/trading/live/distribution/
autopilot surface, promotes/deploys nothing, and records no approval decision.
It records no timestamp, mints no random id, and reads no environment.

Public API:
  - SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION
  - DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL
  - SAFETY_KILL_SWITCH_CONTRACT_STATUS
  - SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE
  - SAFETY_KILL_SWITCH_STATE_ACTIVE
  - SAFETY_KILL_SWITCH_STATE_BLOCKED
  - NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT
  - build_safety_kill_switch_contract(ledger)
  - validate_safety_kill_switch_contract(contract)
  - render_safety_kill_switch_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_decision_ledger_contract import (
    DECISION_LEDGER_CONTRACT_SCHEMA_VERSION,
    DECISION_LEDGER_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED,
)

__all__ = [
    "SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL",
    "SAFETY_KILL_SWITCH_CONTRACT_STATUS",
    "SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE",
    "SAFETY_KILL_SWITCH_STATE_ACTIVE",
    "SAFETY_KILL_SWITCH_STATE_BLOCKED",
    "NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT",
    "build_safety_kill_switch_contract",
    "validate_safety_kill_switch_contract",
    "render_safety_kill_switch_contract_markdown",
]

SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_safety_kill_switch_contract.v1"
)
DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL = (
    "Strategy Factory Safety Kill-Switch / Approval Gate Contract"
)
SAFETY_KILL_SWITCH_CONTRACT_STATUS = "READ_ONLY_SAFETY_KILL_SWITCH_CONTRACT"

SAFETY_KILL_SWITCH_STATE_ACTIVE = "SAFETY_KILL_SWITCH_CONTRACT_ACTIVE"
SAFETY_KILL_SWITCH_STATE_BLOCKED = "SAFETY_KILL_SWITCH_CONTRACT_BLOCKED"

NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED = (
    "END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT = (
    "AWAIT_DECISION_LEDGER_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 25). Pinned False:
# a safety gate contract template only describes a future shape; it grants
# nothing and is never wired into runtime safety state.
SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DECISION_LEDGER_CONTRACT_SAFETY_POSTURE
)

# Manual approval field NAMES a human must complete -- labels only.
_REQUIRED_MANUAL_APPROVAL_FIELDS: tuple[str, ...] = (
    "approver_identity_placeholder",
    "approval_scope_placeholder",
    "approval_rationale_placeholder",
    "approval_sign_off_placeholder",
    "approval_expiry_placeholder",
)

# Operator attestation field NAMES a human must affirm -- labels only.
_REQUIRED_OPERATOR_ATTESTATION_FIELDS: tuple[str, ...] = (
    "read_only_attested",
    "execution_free_attested",
    "no_runtime_write_attested",
    "no_market_data_access_attested",
    "no_broker_contact_attested",
    "human_in_the_loop_attested",
)

# Execution surface NAMES that stay hard-blocked at this gate -- labels only.
_BLOCKED_EXECUTION_SURFACES: tuple[str, ...] = (
    "strategy_factory_run",
    "orchestrator_run",
    "dry_run_run",
    "backtest_run",
    "simulation_run",
    "promotion_step",
)

# Data surface NAMES that stay hard-blocked at this gate -- labels only.
_BLOCKED_DATA_SURFACES: tuple[str, ...] = (
    "market_data_fetch",
    "market_data_inspection",
    "real_data_load",
    "real_data_transform",
    "real_data_compute",
)

# Broker surface NAMES that stay hard-blocked at this gate -- labels only.
_BLOCKED_BROKER_SURFACES: tuple[str, ...] = (
    "broker_contact",
    "exchange_contact",
    "order_submission",
    "live_trading",
    "paper_trading",
)

# Automation surface NAMES that stay hard-blocked at this gate -- labels only.
_BLOCKED_AUTOMATION_SURFACES: tuple[str, ...] = (
    "autopilot",
    "scheduler",
    "automation_loop",
    "upload",
    "deploy",
)

# Deterministic, verb-safe conditions that would trip an emergency stop.
_EMERGENCY_STOP_CONDITIONS: tuple[str, ...] = (
    "A safety posture key is found enabled.",
    "An authorization flag is found enabled.",
    "A blocked surface is reachable from this gate.",
    "A required human approval field is missing.",
    "A required operator attestation field is missing.",
)

# Deterministic, verb-safe preflight checks a human must complete by hand.
_REQUIRED_PREFLIGHT_CHECKS: tuple[str, ...] = (
    "All safety posture keys are confirmed false.",
    "All authorization flags are confirmed false.",
    "All blocked surfaces are confirmed unreachable.",
    "A human approval record is present and unexpired.",
    "All operator attestations are present.",
)

# Deterministic, verb-safe conditions that force a rejection.
_REQUIRED_REJECTION_CONDITIONS: tuple[str, ...] = (
    "Any safety posture key is enabled.",
    "Any authorization flag is enabled.",
    "Any required approval field is missing.",
    "Any required attestation field is missing.",
    "The decision ledger source is not active.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only safety gate contract and is execution-free.",
    "It writes no runtime approval and changes no safety state.",
    "A human must author the real safety gate out of band.",
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
    "dashboard_runtime_update",
    "registry_file_write",
    "template_edit",
    "ledger_runtime_write",
    "runtime_approval_write",
    "runtime_safety_flag_write",
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

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "decision_ledger_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "safety_kill_switch_contract_active",
    "safety_kill_switch_state",
    "decision_ledger_contract_active",
    "decision_ledger_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_decision_ledger_reference_placeholder",
    "required_manual_approval_fields",
    "required_operator_attestation_fields",
    "blocked_execution_surfaces",
    "blocked_data_surfaces",
    "blocked_broker_surfaces",
    "blocked_automation_surfaces",
    "emergency_stop_conditions",
    "approval_expiry_placeholder",
    "required_preflight_checks",
    "required_rejection_conditions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "decision_ledger_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(SAFETY_KILL_SWITCH_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _ledger_field(ledger: Any, key: str) -> str:
    """Read a string field from a possibly-malformed ledger contract; safe."""
    return _as_text(ledger.get(key)) if isinstance(ledger, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    plan_only = safe.get("stage") == "PLAN_ONLY"
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )
    approvals = tuple(safe.get("required_manual_approval_fields") or ())
    attestations = tuple(safe.get("required_operator_attestation_fields") or ())
    fields_ok = len(approvals) >= 1 and len(attestations) >= 1

    valid = bool(
        schema_ok
        and research_only
        and plan_only
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
        "plan_only": plan_only,
        "human_approval_required": human_required,
        "executes": False,
        "all_authorization_flags_false": auth_all_false,
        "safety_all_false": safety_all_false,
        "approval_and_attestation_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_safety_kill_switch_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a safety gate contract template.
    Pure; no I/O."""
    return _validate(contract)


def build_safety_kill_switch_contract(ledger: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only safety kill-switch / approval
    gate contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (safety_kill_switch_contract_active=True) solely when the upstream Bundle
    25 decision ledger contract is active AND its next_gate is
    SAFETY_KILL_SWITCH_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it defines a safety gate contract
    template only, writes no runtime approval, changes no safety state,
    accesses no data, and grants nothing. Returned dicts are fresh."""
    ledger_active = (
        isinstance(ledger, dict)
        and ledger.get("decision_ledger_contract_active") is True
    )
    ledger_next_gate = _ledger_field(ledger, "next_gate")
    contract_active = bool(
        ledger_active
        and ledger_next_gate == NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED
    )
    state = (
        SAFETY_KILL_SWITCH_STATE_ACTIVE
        if contract_active
        else SAFETY_KILL_SWITCH_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_END_TO_END_FAKE_PIPELINE_CONTRACT_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_DECISION_LEDGER_CONTRACT
    )

    contract = {
        "schema_version": SAFETY_KILL_SWITCH_CONTRACT_SCHEMA_VERSION,
        "decision_ledger_contract_schema_version": (
            DECISION_LEDGER_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _ledger_field(ledger, "idea_id"),
        "title": _ledger_field(ledger, "title"),
        "label": DEFAULT_SAFETY_KILL_SWITCH_CONTRACT_LABEL,
        "status": SAFETY_KILL_SWITCH_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "safety_kill_switch_contract_active": contract_active,
        "safety_kill_switch_state": state,
        "decision_ledger_contract_active": bool(ledger_active),
        "decision_ledger_next_gate": ledger_next_gate,
        "asset_lane": _ledger_field(ledger, "asset_lane"),
        "timeframe_lane": _ledger_field(ledger, "timeframe_lane"),
        "source_decision_ledger_reference_placeholder": (
            "Source decision ledger reference is a placeholder for a later "
            "human-authored safety gate contract."
        ),
        "required_manual_approval_fields": _REQUIRED_MANUAL_APPROVAL_FIELDS,
        "required_operator_attestation_fields": (
            _REQUIRED_OPERATOR_ATTESTATION_FIELDS
        ),
        "blocked_execution_surfaces": _BLOCKED_EXECUTION_SURFACES,
        "blocked_data_surfaces": _BLOCKED_DATA_SURFACES,
        "blocked_broker_surfaces": _BLOCKED_BROKER_SURFACES,
        "blocked_automation_surfaces": _BLOCKED_AUTOMATION_SURFACES,
        "emergency_stop_conditions": _EMERGENCY_STOP_CONDITIONS,
        "approval_expiry_placeholder": (
            "Approval expiry is a placeholder for a later human-authored "
            "safety gate contract."
        ),
        "required_preflight_checks": _REQUIRED_PREFLIGHT_CHECKS,
        "required_rejection_conditions": _REQUIRED_REJECTION_CONDITIONS,
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "safety_posture": _safety_posture(),
        "next_gate": next_gate,
        "operator_notes": _OPERATOR_NOTES,
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
        "decision_ledger_contract": (
            ledger if isinstance(ledger, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_safety_kill_switch_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a safety gate contract
    template. Pure; writes no file. Informational only."""
    approvals = contract.get("required_manual_approval_fields") or ()
    attest = contract.get("required_operator_attestation_fields") or ()
    exec_surfaces = contract.get("blocked_execution_surfaces") or ()
    data_surfaces = contract.get("blocked_data_surfaces") or ()
    broker_surfaces = contract.get("blocked_broker_surfaces") or ()
    auto_surfaces = contract.get("blocked_automation_surfaces") or ()
    stops = contract.get("emergency_stop_conditions") or ()
    preflight = contract.get("required_preflight_checks") or ()
    rejections = contract.get("required_rejection_conditions") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Safety Kill-Switch / Approval Gate Contract")
    lines.append("")
    lines.append(
        "Template only: this is a safety-kill-switch-contract-only template -- "
        "no-runtime-approval-write, research-only, and execution-free. It is "
        "not wired into any runtime safety state, accesses no data, and grants "
        "no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Ledger schema: "
        f"`{contract.get('decision_ledger_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Safety kill switch contract active: "
        f"{contract.get('safety_kill_switch_contract_active', '')}"
    )
    lines.append(
        f"Gate state: {contract.get('safety_kill_switch_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append(
        "Approval expiry: "
        f"{contract.get('approval_expiry_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Required Manual Approval Fields")
    lines.append("")
    for x in approvals:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Attestation Fields")
    lines.append("")
    for x in attest:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Blocked Execution Surfaces")
    lines.append("")
    for x in exec_surfaces:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Blocked Data Surfaces")
    lines.append("")
    for x in data_surfaces:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Blocked Broker Surfaces")
    lines.append("")
    for x in broker_surfaces:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Blocked Automation Surfaces")
    lines.append("")
    for x in auto_surfaces:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Emergency Stop Conditions")
    lines.append("")
    for x in stops:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Required Preflight Checks")
    lines.append("")
    for x in preflight:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Required Rejection Conditions")
    lines.append("")
    for x in rejections:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in contract.get("blocked_capabilities") or ():
        lines.append(f"- `{cap}`")
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
        "- A human must author the real safety gate before the end-to-end "
        "fake pipeline contract is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
