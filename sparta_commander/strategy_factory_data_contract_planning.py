"""SPARTA Offline Strategy Factory - DATA CONTRACT PLANNING (TEMPLATE) v1.

Bundle 20 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only data contract planning template* builder: it consumes a
Bundle 19 protocol review gate and, only when that gate is
READY_FOR_DATA_CONTRACT_PLANNING with data_contract_planning_unlocked True,
produces a deterministic, read-only *template* describing the shape a future
human-authored data contract must take. It defines a planning template only --
NOT real data access.

It never fetches, inspects, loads, validates, computes on, or touches real
data. It runs nothing, computes no historical simulation, opens no network,
spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - DATA_CONTRACT_PLANNING_SCHEMA_VERSION
  - DEFAULT_DATA_CONTRACT_PLANNING_LABEL
  - DATA_CONTRACT_PLANNING_STATUS
  - DATA_CONTRACT_PLANNING_SAFETY_POSTURE
  - PLANNING_STATE_ACTIVE
  - PLANNING_STATE_BLOCKED
  - NEXT_GATE_DATA_QA_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_PLANNING_UNLOCK
  - build_data_contract_planning(gate)
  - validate_data_contract_planning(contract)
  - render_data_contract_planning_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_protocol_review_gate import (
    PROTOCOL_REVIEW_GATE_SCHEMA_VERSION,
    PROTOCOL_REVIEW_GATE_SAFETY_POSTURE,
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
)

__all__ = [
    "DATA_CONTRACT_PLANNING_SCHEMA_VERSION",
    "DEFAULT_DATA_CONTRACT_PLANNING_LABEL",
    "DATA_CONTRACT_PLANNING_STATUS",
    "DATA_CONTRACT_PLANNING_SAFETY_POSTURE",
    "PLANNING_STATE_ACTIVE",
    "PLANNING_STATE_BLOCKED",
    "NEXT_GATE_DATA_QA_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_PLANNING_UNLOCK",
    "build_data_contract_planning",
    "validate_data_contract_planning",
    "render_data_contract_planning_markdown",
]

DATA_CONTRACT_PLANNING_SCHEMA_VERSION = (
    "strategy_factory_data_contract_planning.v1"
)
DEFAULT_DATA_CONTRACT_PLANNING_LABEL = (
    "Strategy Factory Data Contract Planning"
)
DATA_CONTRACT_PLANNING_STATUS = "READ_ONLY_DATA_CONTRACT_PLANNING"

PLANNING_STATE_ACTIVE = "DATA_CONTRACT_PLANNING_ACTIVE"
PLANNING_STATE_BLOCKED = "DATA_CONTRACT_PLANNING_BLOCKED"

NEXT_GATE_DATA_QA_CONTRACT_REQUIRED = "DATA_QA_CONTRACT_REQUIRED"
NEXT_GATE_AWAIT_PLANNING_UNLOCK = "AWAIT_PLANNING_UNLOCK"

# Inherited all-false safety posture (same keys as Bundle 19). Pinned False:
# a planning template only describes a future data contract; it grants nothing.
DATA_CONTRACT_PLANNING_SAFETY_POSTURE: dict[str, bool] = dict(
    PROTOCOL_REVIEW_GATE_SAFETY_POSTURE
)

# Field NAMES a future data contract must describe -- not data, just labels.
_REQUIRED_DATA_FIELDS: tuple[str, ...] = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

# Deterministic, verb-safe placeholders. None authorize any live capability.
_FEE_SLIPPAGE_ASSUMPTION_PLACEHOLDERS: tuple[str, ...] = (
    "Fee assumption is a placeholder for a later human-authored data contract.",
    "Slippage assumption is a placeholder for a later human-authored data "
    "contract.",
    "No live fee or slippage value is sourced by this template.",
)

# Deterministic, verb-safe data-quality planning prompts (questions only).
_DATA_QUALITY_QUESTIONS: tuple[str, ...] = (
    "Are there gaps or missing sessions in the intended coverage window?",
    "How are holidays and half-sessions handled in the intended coverage "
    "window?",
    "Is the timestamp convention session-aligned and consistent?",
    "Are corporate actions or contract rolls relevant to this asset lane?",
    "What is the source-of-truth reference for this asset lane?",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only data contract planning document and is "
    "execution-free.",
    "A human must author the real data contract out of band.",
    "No real data is sourced, inspected, loaded, or validated by this "
    "template.",
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
    "protocol_review_gate_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "planning_active",
    "planning_state",
    "gate_review_state",
    "data_contract_planning_unlocked",
    "asset_lane",
    "timeframe_lane",
    "required_data_fields",
    "expected_granularity",
    "coverage_window_placeholder",
    "fee_slippage_assumption_placeholders",
    "data_quality_questions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "protocol_review_gate",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DATA_CONTRACT_PLANNING_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _gate_field(gate: Any, key: str) -> str:
    """Read a string field from a possibly-malformed gate; never raises."""
    return _as_text(gate.get(key)) if isinstance(gate, dict) else ""


def _draft_field(gate: Any, key: str) -> str:
    """Read a string field from the gate's embedded draft contract; safe."""
    draft = gate.get("protocol_draft_contract") if isinstance(gate, dict) \
        else None
    return _as_text(draft.get(key)) if isinstance(draft, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DATA_CONTRACT_PLANNING_SCHEMA_VERSION
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
    fields = tuple(safe.get("required_data_fields") or ())
    fields_ok = len(fields) >= 1

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
        "required_data_fields_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_data_contract_planning(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a data contract planning template.
    Pure; no I/O."""
    return _validate(contract)


def build_data_contract_planning(gate: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only data contract planning template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    gates never raise. The template becomes active
    (planning_active=True) solely when the upstream Bundle 19 review gate is
    READY_FOR_DATA_CONTRACT_PLANNING AND data_contract_planning_unlocked is
    True. Even when active, every authorization field stays False -- it
    defines a planning template only, accesses no data, runs nothing, and
    grants nothing. Returned dicts are fresh."""
    gate_review_state = _gate_field(gate, "review_state")
    unlocked = (
        isinstance(gate, dict)
        and gate.get("data_contract_planning_unlocked") is True
    )
    planning_active = bool(
        gate_review_state == REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING
        and unlocked
    )
    state = (
        PLANNING_STATE_ACTIVE if planning_active else PLANNING_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_DATA_QA_CONTRACT_REQUIRED if planning_active
        else NEXT_GATE_AWAIT_PLANNING_UNLOCK
    )

    timeframe_lane = _draft_field(gate, "timeframe_lane")
    expected_granularity = (
        f"One bar per {timeframe_lane} interval (placeholder)."
        if timeframe_lane
        else "Bar granularity is a placeholder for a later human-authored "
        "data contract."
    )

    contract = {
        "schema_version": DATA_CONTRACT_PLANNING_SCHEMA_VERSION,
        "protocol_review_gate_schema_version": (
            PROTOCOL_REVIEW_GATE_SCHEMA_VERSION
        ),
        "idea_id": _gate_field(gate, "idea_id"),
        "title": _gate_field(gate, "title"),
        "label": DEFAULT_DATA_CONTRACT_PLANNING_LABEL,
        "status": DATA_CONTRACT_PLANNING_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "planning_active": planning_active,
        "planning_state": state,
        "gate_review_state": gate_review_state,
        "data_contract_planning_unlocked": bool(unlocked),
        "asset_lane": _draft_field(gate, "asset_lane"),
        "timeframe_lane": timeframe_lane,
        "required_data_fields": _REQUIRED_DATA_FIELDS,
        "expected_granularity": expected_granularity,
        "coverage_window_placeholder": (
            "Coverage window is a placeholder for a later human-authored "
            "data contract."
        ),
        "fee_slippage_assumption_placeholders": (
            _FEE_SLIPPAGE_ASSUMPTION_PLACEHOLDERS
        ),
        "data_quality_questions": _DATA_QUALITY_QUESTIONS,
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
        "protocol_review_gate": gate if isinstance(gate, dict) else {},
    }
    contract["validation"] = _validate(contract)
    return contract


def render_data_contract_planning_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a planning template.
    Pure; writes no file. Informational only."""
    fields = contract.get("required_data_fields") or ()
    fees = contract.get("fee_slippage_assumption_placeholders") or ()
    questions = contract.get("data_quality_questions") or ()
    blocked = contract.get("blocked_capabilities") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Data Contract Planning")
    lines.append("")
    lines.append("Template only: this document is execution-free, accesses no "
                 "data, and grants no capability.")
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Review gate schema: "
        f"`{contract.get('protocol_review_gate_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Planning active: {contract.get('planning_active', '')}")
    lines.append(f"Planning state: {contract.get('planning_state', '')}")
    lines.append(f"Gate review state: {contract.get('gate_review_state', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append(
        f"Expected granularity: {contract.get('expected_granularity', '')}"
    )
    lines.append(
        "Coverage window: "
        f"{contract.get('coverage_window_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Required Data Fields")
    lines.append("")
    for f in fields:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("## Fee And Slippage Assumption Placeholders")
    lines.append("")
    for s in fees:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Data Quality Questions")
    lines.append("")
    for q in questions:
        lines.append(f"- {q}")
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
        "- A human must author the real data contract and a data QA contract "
        "out of band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
