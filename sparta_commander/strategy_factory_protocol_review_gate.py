"""SPARTA Offline Strategy Factory - PROTOCOL REVIEW GATE v1.

Bundle 19 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only human review gate*: it consumes a Bundle 18 research
protocol draft contract and, only when that contract is open for review
(next_gate == PROTOCOL_REVIEW_REQUIRED), exposes a deterministic gate whose
recorded human review decision moves the protocol toward a later read-only
data-contract planning review -- or back to redrafting, parking, or rejection.

It never approves execution. It never approves data intake. It never approves
simulation or historical-simulation. It persists no approval, mints no id,
records no timestamp, reads no environment, writes no file, opens no network,
spawns no subprocess, and touches no
broker/exchange/order/trading/live/distribution/autopilot surface. It is
informational, read-only, and gate-only: it computes a review *state*, it never
acts on one.

Public API:
  - PROTOCOL_REVIEW_GATE_SCHEMA_VERSION
  - DEFAULT_PROTOCOL_REVIEW_GATE_LABEL
  - PROTOCOL_REVIEW_GATE_STATUS
  - PROTOCOL_REVIEW_GATE_SAFETY_POSTURE
  - REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW
  - REVIEW_STATE_NEEDS_PROTOCOL_FIXES
  - REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING
  - REVIEW_STATE_PARK_PROTOCOL
  - REVIEW_STATE_REJECT_PROTOCOL
  - ALLOWED_REVIEW_DECISIONS
  - NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW
  - NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT
  - NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW
  - NEXT_GATE_PROTOCOL_PARKED
  - NEXT_GATE_PROTOCOL_REJECTED
  - build_protocol_review_gate(contract, *, review_decision=None)
  - validate_protocol_review_gate(gate)
  - render_protocol_review_gate_markdown(gate)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION,
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_PROTOCOL_REVIEW_REQUIRED,
)

__all__ = [
    "PROTOCOL_REVIEW_GATE_SCHEMA_VERSION",
    "DEFAULT_PROTOCOL_REVIEW_GATE_LABEL",
    "PROTOCOL_REVIEW_GATE_STATUS",
    "PROTOCOL_REVIEW_GATE_SAFETY_POSTURE",
    "REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW",
    "REVIEW_STATE_NEEDS_PROTOCOL_FIXES",
    "REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING",
    "REVIEW_STATE_PARK_PROTOCOL",
    "REVIEW_STATE_REJECT_PROTOCOL",
    "ALLOWED_REVIEW_DECISIONS",
    "NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW",
    "NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT",
    "NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW",
    "NEXT_GATE_PROTOCOL_PARKED",
    "NEXT_GATE_PROTOCOL_REJECTED",
    "build_protocol_review_gate",
    "validate_protocol_review_gate",
    "render_protocol_review_gate_markdown",
]

PROTOCOL_REVIEW_GATE_SCHEMA_VERSION = "strategy_factory_protocol_review_gate.v1"
DEFAULT_PROTOCOL_REVIEW_GATE_LABEL = "Strategy Factory Protocol Review Gate"
PROTOCOL_REVIEW_GATE_STATUS = "READ_ONLY_PROTOCOL_REVIEW_GATE"

# The five review states a human may record (or the default awaiting state).
REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW = "AWAITING_HUMAN_PROTOCOL_REVIEW"
REVIEW_STATE_NEEDS_PROTOCOL_FIXES = "NEEDS_PROTOCOL_FIXES"
REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING = (
    "READY_FOR_DATA_CONTRACT_PLANNING"
)
REVIEW_STATE_PARK_PROTOCOL = "PARK_PROTOCOL"
REVIEW_STATE_REJECT_PROTOCOL = "REJECT_PROTOCOL"

ALLOWED_REVIEW_DECISIONS: tuple[str, ...] = (
    REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW,
    REVIEW_STATE_NEEDS_PROTOCOL_FIXES,
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    REVIEW_STATE_PARK_PROTOCOL,
    REVIEW_STATE_REJECT_PROTOCOL,
)

# The gate's own next-gate signal (still read-only; opens only review steps).
NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW = "AWAIT_HUMAN_PROTOCOL_REVIEW"
NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT = "RETURN_TO_PROTOCOL_DRAFT"
NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW = "DATA_CONTRACT_PLANNING_REVIEW_REQUIRED"
NEXT_GATE_PROTOCOL_PARKED = "PROTOCOL_PARKED"
NEXT_GATE_PROTOCOL_REJECTED = "PROTOCOL_REJECTED"

_NEXT_GATE_BY_STATE: dict[str, str] = {
    REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW:
        NEXT_GATE_AWAIT_HUMAN_PROTOCOL_REVIEW,
    REVIEW_STATE_NEEDS_PROTOCOL_FIXES: NEXT_GATE_RETURN_TO_PROTOCOL_DRAFT,
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING:
        NEXT_GATE_DATA_CONTRACT_PLANNING_REVIEW,
    REVIEW_STATE_PARK_PROTOCOL: NEXT_GATE_PROTOCOL_PARKED,
    REVIEW_STATE_REJECT_PROTOCOL: NEXT_GATE_PROTOCOL_REJECTED,
}

# Inherited all-false safety posture (same keys as Bundle 18). Pinned False:
# a review gate only records a human decision; it grants nothing.
PROTOCOL_REVIEW_GATE_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_PROTOCOL_DRAFT_CONTRACT_SAFETY_POSTURE
)

# Capabilities that stay blocked for every gate, regardless of review state.
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
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a read-only protocol review gate and is execution-free.",
    "A human must record the protocol review decision out of band.",
    "A READY_FOR_DATA_CONTRACT_PLANNING decision only opens the next "
    "read-only data-contract planning review; it grants no data, simulation, "
    "broker, exchange, distribution, or autopilot capability.",
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

# Top-level schema fields required for a gate to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the gate
# to embed its own validation result would be circular.
_REQUIRED_GATE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "protocol_draft_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "gate_accepts_contract",
    "review_decision",
    "allowed_review_decisions",
    "review_state",
    "data_contract_planning_unlocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "protocol_draft_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(PROTOCOL_REVIEW_GATE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _contract_field(contract: Any, key: str) -> str:
    """Read a string field from a possibly-malformed contract; never raises."""
    return _as_text(contract.get(key)) if isinstance(contract, dict) else ""


def _normalize_decision(review_decision: Any) -> str:
    """Coerce a human review decision to an allowed value (default awaiting)."""
    if (
        isinstance(review_decision, str)
        and review_decision in ALLOWED_REVIEW_DECISIONS
    ):
        return review_decision
    return REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW


def _validate(gate: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a gate dict (no I/O)."""
    safe = gate if isinstance(gate, dict) else {}

    missing = tuple(f for f in _REQUIRED_GATE_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == PROTOCOL_REVIEW_GATE_SCHEMA_VERSION
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
    state = safe.get("review_state")
    state_ok = state in ALLOWED_REVIEW_DECISIONS
    next_gate_ok = (
        state_ok and safe.get("next_gate") == _NEXT_GATE_BY_STATE.get(state)
    )
    # data-contract planning may be unlocked only when accepted AND ready.
    unlocked = safe.get("data_contract_planning_unlocked")
    unlock_consistent = unlocked is (
        safe.get("gate_accepts_contract") is True
        and state == REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING
    )

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and state_ok
        and next_gate_ok
        and unlock_consistent
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
        "review_state_ok": state_ok,
        "next_gate_consistent": next_gate_ok,
        "unlock_consistent": unlock_consistent,
        "missing_required_fields": missing,
    }


def validate_protocol_review_gate(gate: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic validation of a protocol review gate.
    Pure; no I/O."""
    return _validate(gate)


def build_protocol_review_gate(
    contract: Any,
    *,
    review_decision: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only protocol review gate.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    contracts never raise. The gate ACCEPTS a Bundle 18 protocol draft contract
    only when that contract is open for review
    (next_gate == PROTOCOL_REVIEW_REQUIRED and protocol_draft_active True).
    The recorded human review_decision takes effect only when the gate accepts
    the contract; otherwise the gate stays in the awaiting state and advances
    nothing. Even on a READY_FOR_DATA_CONTRACT_PLANNING decision every
    authorization field stays False -- it approves no execution, no data
    intake, no simulation, no historical-simulation. Returned dicts are
    fresh."""
    gate_accepts_contract = bool(
        isinstance(contract, dict)
        and contract.get("next_gate") == NEXT_GATE_PROTOCOL_REVIEW_REQUIRED
        and contract.get("protocol_draft_active") is True
    )

    normalized = _normalize_decision(review_decision)
    review_state = (
        normalized
        if gate_accepts_contract
        else REVIEW_STATE_AWAITING_HUMAN_PROTOCOL_REVIEW
    )
    next_gate = _NEXT_GATE_BY_STATE[review_state]
    data_contract_planning_unlocked = bool(
        gate_accepts_contract
        and review_state == REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING
    )

    gate = {
        "schema_version": PROTOCOL_REVIEW_GATE_SCHEMA_VERSION,
        "protocol_draft_schema_version": (
            RESEARCH_PROTOCOL_DRAFT_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _contract_field(contract, "idea_id"),
        "title": _contract_field(contract, "title"),
        "label": DEFAULT_PROTOCOL_REVIEW_GATE_LABEL,
        "status": PROTOCOL_REVIEW_GATE_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "gate_accepts_contract": gate_accepts_contract,
        "review_decision": review_state,
        "allowed_review_decisions": ALLOWED_REVIEW_DECISIONS,
        "review_state": review_state,
        "data_contract_planning_unlocked": data_contract_planning_unlocked,
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
        "protocol_draft_contract": contract if isinstance(contract, dict)
        else {},
    }
    gate["validation"] = _validate(gate)
    return gate


def render_protocol_review_gate_markdown(gate: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for a protocol review gate.
    Pure; writes no file. Informational only."""
    allowed = gate.get("allowed_review_decisions") or ()
    blocked = gate.get("blocked_capabilities") or ()
    notes = gate.get("operator_notes") or ()
    posture = gate.get("safety_posture") or {}
    validation = gate.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Protocol Review Gate")
    lines.append("")
    lines.append("Gate only: this document is execution-free and grants no "
                 "capability.")
    lines.append("")
    lines.append(f"Schema: `{gate.get('schema_version', '')}`")
    lines.append(
        "Protocol draft schema: "
        f"`{gate.get('protocol_draft_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {gate.get('idea_id', '')}")
    lines.append(f"Title: {gate.get('title', '')}")
    lines.append(f"Status: {gate.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        f"Gate accepts contract: {gate.get('gate_accepts_contract', '')}"
    )
    lines.append(f"Review state: {gate.get('review_state', '')}")
    lines.append(
        "Data contract planning unlocked: "
        f"{gate.get('data_contract_planning_unlocked', '')}"
    )
    lines.append(f"Next gate: {gate.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Allowed Review Decisions")
    lines.append("")
    for d in allowed:
        lines.append(f"- `{d}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in blocked:
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
        "- A human must record the protocol review decision before any "
        "later read-only planning step is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
