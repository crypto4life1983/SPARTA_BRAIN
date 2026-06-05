"""SPARTA Offline Strategy Factory - DATA QA CONTRACT (TEMPLATE) v1.

Bundle 21 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only data QA contract template* builder: it consumes a
Bundle 20 data contract planning template and, only when that planning is
active with next_gate == DATA_QA_CONTRACT_REQUIRED, produces a deterministic,
read-only *template* describing the shape a future human-authored data QA
contract must take. It defines a QA contract template only -- NOT real data
quality work.

It never loads, inspects, fetches, validates, transforms, computes on, or
touches real market data. It runs nothing, computes no historical simulation,
opens no network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - DATA_QA_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DATA_QA_CONTRACT_LABEL
  - DATA_QA_CONTRACT_STATUS
  - DATA_QA_CONTRACT_SAFETY_POSTURE
  - DATA_QA_STATE_ACTIVE
  - DATA_QA_STATE_BLOCKED
  - NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING
  - build_data_qa_contract(planning)
  - validate_data_qa_contract(contract)
  - render_data_qa_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_data_contract_planning import (
    DATA_CONTRACT_PLANNING_SCHEMA_VERSION,
    DATA_CONTRACT_PLANNING_SAFETY_POSTURE,
    NEXT_GATE_DATA_QA_CONTRACT_REQUIRED,
)

__all__ = [
    "DATA_QA_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DATA_QA_CONTRACT_LABEL",
    "DATA_QA_CONTRACT_STATUS",
    "DATA_QA_CONTRACT_SAFETY_POSTURE",
    "DATA_QA_STATE_ACTIVE",
    "DATA_QA_STATE_BLOCKED",
    "NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING",
    "build_data_qa_contract",
    "validate_data_qa_contract",
    "render_data_qa_contract_markdown",
]

DATA_QA_CONTRACT_SCHEMA_VERSION = "strategy_factory_data_qa_contract.v1"
DEFAULT_DATA_QA_CONTRACT_LABEL = "Strategy Factory Data QA Contract"
DATA_QA_CONTRACT_STATUS = "READ_ONLY_DATA_QA_CONTRACT"

DATA_QA_STATE_ACTIVE = "DATA_QA_CONTRACT_ACTIVE"
DATA_QA_STATE_BLOCKED = "DATA_QA_CONTRACT_BLOCKED"

NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED = (
    "RESEARCH_RUNNER_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING = "AWAIT_DATA_CONTRACT_PLANNING"

# Inherited all-false safety posture (same keys as Bundle 20). Pinned False:
# a QA contract template only describes a future check set; it grants nothing.
DATA_QA_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DATA_CONTRACT_PLANNING_SAFETY_POSTURE
)

# Integrity check NAMES a future QA contract must describe -- labels only.
_REQUIRED_DATA_INTEGRITY_CHECKS: tuple[str, ...] = (
    "missing_bar_check",
    "duplicate_timestamp_check",
    "monotonic_timestamp_check",
    "timezone_consistency_check",
    "ohlc_bounds_sanity_check",
    "non_negative_volume_check",
    "coverage_window_completeness_check",
    "symbol_mapping_consistency_check",
)

# Deterministic, verb-safe rejection conditions (descriptions only).
_REJECTION_CONDITIONS: tuple[str, ...] = (
    "Coverage window is incomplete beyond the agreed tolerance.",
    "Duplicate or non-monotonic timestamps exceed the agreed tolerance.",
    "Timezone or session alignment is inconsistent.",
    "Symbol mapping is ambiguous or unresolved.",
    "Bar values are out of sane bounds beyond the agreed tolerance.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only data QA contract and is execution-free.",
    "A human must author the real data QA contract out of band.",
    "No real data is loaded, inspected, transformed, or validated by this "
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
    "data_contract_planning_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "data_qa_active",
    "data_qa_state",
    "planning_active",
    "planning_next_gate",
    "asset_lane",
    "timeframe_lane",
    "required_data_integrity_checks",
    "missing_bar_policy_placeholder",
    "duplicate_timestamp_policy_placeholder",
    "timezone_policy_placeholder",
    "fee_slippage_policy_placeholder",
    "symbol_mapping_policy_placeholder",
    "minimum_coverage_policy_placeholder",
    "rejection_conditions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "data_contract_planning",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DATA_QA_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _planning_field(planning: Any, key: str) -> str:
    """Read a string field from a possibly-malformed planning dict; safe."""
    return _as_text(planning.get(key)) if isinstance(planning, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DATA_QA_CONTRACT_SCHEMA_VERSION
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
    checks = tuple(safe.get("required_data_integrity_checks") or ())
    checks_ok = len(checks) >= 1

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and checks_ok
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
        "required_data_integrity_checks_present": checks_ok,
        "missing_required_fields": missing,
    }


def validate_data_qa_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic validation of a data QA contract template.
    Pure; no I/O."""
    return _validate(contract)


def build_data_qa_contract(planning: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only data QA contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    planning inputs never raise. The template becomes active
    (data_qa_active=True) solely when the upstream Bundle 20 data contract
    planning is active AND its next_gate is DATA_QA_CONTRACT_REQUIRED. Even
    when active, every authorization field stays False -- it defines a QA
    contract template only, accesses no data, runs nothing, and grants
    nothing. Returned dicts are fresh."""
    planning_active = (
        isinstance(planning, dict) and planning.get("planning_active") is True
    )
    planning_next_gate = _planning_field(planning, "next_gate")
    data_qa_active = bool(
        planning_active
        and planning_next_gate == NEXT_GATE_DATA_QA_CONTRACT_REQUIRED
    )
    state = (
        DATA_QA_STATE_ACTIVE if data_qa_active else DATA_QA_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED if data_qa_active
        else NEXT_GATE_AWAIT_DATA_CONTRACT_PLANNING
    )

    contract = {
        "schema_version": DATA_QA_CONTRACT_SCHEMA_VERSION,
        "data_contract_planning_schema_version": (
            DATA_CONTRACT_PLANNING_SCHEMA_VERSION
        ),
        "idea_id": _planning_field(planning, "idea_id"),
        "title": _planning_field(planning, "title"),
        "label": DEFAULT_DATA_QA_CONTRACT_LABEL,
        "status": DATA_QA_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "data_qa_active": data_qa_active,
        "data_qa_state": state,
        "planning_active": bool(planning_active),
        "planning_next_gate": planning_next_gate,
        "asset_lane": _planning_field(planning, "asset_lane"),
        "timeframe_lane": _planning_field(planning, "timeframe_lane"),
        "required_data_integrity_checks": _REQUIRED_DATA_INTEGRITY_CHECKS,
        "missing_bar_policy_placeholder": (
            "Missing-bar policy is a placeholder for a later human-authored "
            "QA contract."
        ),
        "duplicate_timestamp_policy_placeholder": (
            "Duplicate-timestamp policy is a placeholder for a later "
            "human-authored QA contract."
        ),
        "timezone_policy_placeholder": (
            "Timezone policy is a placeholder for a later human-authored QA "
            "contract."
        ),
        "fee_slippage_policy_placeholder": (
            "Fee and slippage policy is a placeholder for a later "
            "human-authored QA contract."
        ),
        "symbol_mapping_policy_placeholder": (
            "Symbol-mapping policy is a placeholder for a later "
            "human-authored QA contract."
        ),
        "minimum_coverage_policy_placeholder": (
            "Minimum-coverage policy is a placeholder for a later "
            "human-authored QA contract."
        ),
        "rejection_conditions": _REJECTION_CONDITIONS,
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
        "data_contract_planning": planning if isinstance(planning, dict)
        else {},
    }
    contract["validation"] = _validate(contract)
    return contract


def render_data_qa_contract_markdown(contract: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for a data QA contract.
    Pure; writes no file. Informational only."""
    checks = contract.get("required_data_integrity_checks") or ()
    rejections = contract.get("rejection_conditions") or ()
    blocked = contract.get("blocked_capabilities") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Data QA Contract")
    lines.append("")
    lines.append("Template only: this document is execution-free, accesses no "
                 "data, and grants no capability.")
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Planning schema: "
        f"`{contract.get('data_contract_planning_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Data QA active: {contract.get('data_qa_active', '')}")
    lines.append(f"Data QA state: {contract.get('data_qa_state', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Required Data Integrity Checks")
    lines.append("")
    for c in checks:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("## Policy Placeholders")
    lines.append("")
    lines.append(
        f"- Missing bar: {contract.get('missing_bar_policy_placeholder', '')}"
    )
    lines.append(
        "- Duplicate timestamp: "
        f"{contract.get('duplicate_timestamp_policy_placeholder', '')}"
    )
    lines.append(
        f"- Timezone: {contract.get('timezone_policy_placeholder', '')}"
    )
    lines.append(
        "- Fee and slippage: "
        f"{contract.get('fee_slippage_policy_placeholder', '')}"
    )
    lines.append(
        "- Symbol mapping: "
        f"{contract.get('symbol_mapping_policy_placeholder', '')}"
    )
    lines.append(
        "- Minimum coverage: "
        f"{contract.get('minimum_coverage_policy_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Rejection Conditions")
    lines.append("")
    for r in rejections:
        lines.append(f"- {r}")
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
        "- A human must author the real data QA contract before any later "
        "read-only research runner contract is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
