"""SPARTA Offline Strategy Factory - DECISION LEDGER CONTRACT (TEMPLATE) v1.

Bundle 25 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only decision ledger contract template* builder: it consumes
a Bundle 24 dashboard registry feed contract and, only when that contract is
active with next_gate == DECISION_LEDGER_CONTRACT_REQUIRED, produces a
deterministic, read-only *template* describing the shape a future human
decision ledger for Strategy Factory artifacts must take. It defines a ledger
contract template only -- NOT a live ledger.

It never writes a ledger file, never updates runtime state, never updates
dashboard files, never orchestrates anything, never performs research, never
backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - DECISION_LEDGER_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DECISION_LEDGER_CONTRACT_LABEL
  - DECISION_LEDGER_CONTRACT_STATUS
  - DECISION_LEDGER_CONTRACT_SAFETY_POSTURE
  - DECISION_LEDGER_STATE_ACTIVE
  - DECISION_LEDGER_STATE_BLOCKED
  - ALLOWED_DECISION_VALUES
  - NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT
  - build_decision_ledger_contract(feed)
  - validate_decision_ledger_contract(contract)
  - render_decision_ledger_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
    DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION,
    DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED,
)

__all__ = [
    "DECISION_LEDGER_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DECISION_LEDGER_CONTRACT_LABEL",
    "DECISION_LEDGER_CONTRACT_STATUS",
    "DECISION_LEDGER_CONTRACT_SAFETY_POSTURE",
    "DECISION_LEDGER_STATE_ACTIVE",
    "DECISION_LEDGER_STATE_BLOCKED",
    "ALLOWED_DECISION_VALUES",
    "NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT",
    "build_decision_ledger_contract",
    "validate_decision_ledger_contract",
    "render_decision_ledger_contract_markdown",
]

DECISION_LEDGER_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_decision_ledger_contract.v1"
)
DEFAULT_DECISION_LEDGER_CONTRACT_LABEL = (
    "Strategy Factory Decision Ledger Contract"
)
DECISION_LEDGER_CONTRACT_STATUS = "READ_ONLY_DECISION_LEDGER_CONTRACT"

DECISION_LEDGER_STATE_ACTIVE = "DECISION_LEDGER_CONTRACT_ACTIVE"
DECISION_LEDGER_STATE_BLOCKED = "DECISION_LEDGER_CONTRACT_BLOCKED"

# The only decision values a future human ledger may carry. Labels only --
# none of these authorizes execution; promotion to any later gate stays
# human-gated and verifier-bound.
ALLOWED_DECISION_VALUES: tuple[str, ...] = (
    "NEEDS_MORE_SPEC",
    "READY_FOR_FAKE_ARTIFACT_DRY_RUN_REVIEW",
    "WATCH",
    "PARK",
    "REJECT",
)

NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED = (
    "SAFETY_KILL_SWITCH_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT = (
    "AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 24). Pinned False:
# a ledger contract template only describes a future shape; it grants nothing
# and is never wired into a runtime ledger or the live dashboard.
DECISION_LEDGER_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE
)

# Ledger entry field NAMES a future ledger row would carry -- labels only.
_LEDGER_ENTRY_FIELDS: tuple[str, ...] = (
    "ledger_entry_id",
    "artifact_id",
    "artifact_type",
    "decision_value",
    "decision_rationale_placeholder",
    "reviewer_placeholder",
    "decided_at_placeholder",
    "next_gate",
)

# Human review field NAMES a future ledger row must carry -- labels only.
_REQUIRED_HUMAN_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "review_summary_placeholder",
    "decision_value",
    "decision_rationale_placeholder",
    "human_sign_off_placeholder",
)

# Safety attestation field NAMES a human must affirm -- labels only.
_REQUIRED_SAFETY_ATTESTATION_FIELDS: tuple[str, ...] = (
    "read_only_attested",
    "execution_free_attested",
    "no_runtime_write_attested",
    "no_market_data_access_attested",
    "human_approval_attested",
)

# Evidence placeholder NAMES a future ledger row would reference -- labels only.
_REQUIRED_EVIDENCE_PLACEHOLDERS: tuple[str, ...] = (
    "summary_metrics_evidence_placeholder",
    "risk_metrics_evidence_placeholder",
    "reproducibility_evidence_placeholder",
    "trace_manifest_evidence_placeholder",
)

# Audit field NAMES a future ledger audit row would carry -- labels only.
_EXPECTED_AUDIT_FIELDS: tuple[str, ...] = (
    "audit_entry_id",
    "actor_placeholder",
    "action_placeholder",
    "before_state_placeholder",
    "after_state_placeholder",
    "audit_timestamp_placeholder",
)

# Deterministic, verb-safe reasons a decision would be blocked.
_DECISION_BLOCKING_REASONS: tuple[str, ...] = (
    "A required human review field is missing.",
    "A safety attestation field is incomplete.",
    "Required evidence placeholders are absent.",
    "The decision value is outside the allowed set.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only decision ledger contract and is execution-free.",
    "It touches no runtime ledger file and changes no dashboard.",
    "A human must author the real decision ledger out of band.",
    "No runtime ledger is changed and nothing is computed by this template.",
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
    "dashboard_registry_feed_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "decision_ledger_contract_active",
    "decision_ledger_state",
    "dashboard_registry_feed_contract_active",
    "dashboard_registry_feed_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_protocol_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "source_orchestrator_reference_placeholder",
    "source_dashboard_feed_reference_placeholder",
    "ledger_entry_fields",
    "allowed_decision_values",
    "required_human_review_fields",
    "required_safety_attestation_fields",
    "required_evidence_placeholders",
    "decision_blocking_reasons",
    "expected_audit_fields",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "dashboard_registry_feed_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DECISION_LEDGER_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _feed_field(feed: Any, key: str) -> str:
    """Read a string field from a possibly-malformed feed contract; safe."""
    return _as_text(feed.get(key)) if isinstance(feed, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DECISION_LEDGER_CONTRACT_SCHEMA_VERSION
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
    ledger = tuple(safe.get("ledger_entry_fields") or ())
    decisions = tuple(safe.get("allowed_decision_values") or ())
    decisions_ok = decisions == ALLOWED_DECISION_VALUES
    fields_ok = len(ledger) >= 1 and decisions_ok

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
        "allowed_decision_values_ok": decisions_ok,
        "ledger_and_decisions_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_decision_ledger_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a decision ledger contract template.
    Pure; no I/O."""
    return _validate(contract)


def build_decision_ledger_contract(feed: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only decision ledger contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (decision_ledger_contract_active=True) solely when the upstream Bundle 24
    dashboard registry feed contract is active AND its next_gate is
    DECISION_LEDGER_CONTRACT_REQUIRED. Even when active, every authorization
    field stays False -- it defines a ledger contract template only, touches
    no runtime ledger, updates no dashboard, accesses no data, and grants
    nothing. Returned dicts are fresh."""
    feed_active = (
        isinstance(feed, dict)
        and feed.get("dashboard_registry_feed_contract_active") is True
    )
    feed_next_gate = _feed_field(feed, "next_gate")
    contract_active = bool(
        feed_active
        and feed_next_gate == NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED
    )
    state = (
        DECISION_LEDGER_STATE_ACTIVE
        if contract_active
        else DECISION_LEDGER_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_SAFETY_KILL_SWITCH_CONTRACT_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_DASHBOARD_REGISTRY_FEED_CONTRACT
    )

    contract = {
        "schema_version": DECISION_LEDGER_CONTRACT_SCHEMA_VERSION,
        "dashboard_registry_feed_contract_schema_version": (
            DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _feed_field(feed, "idea_id"),
        "title": _feed_field(feed, "title"),
        "label": DEFAULT_DECISION_LEDGER_CONTRACT_LABEL,
        "status": DECISION_LEDGER_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "decision_ledger_contract_active": contract_active,
        "decision_ledger_state": state,
        "dashboard_registry_feed_contract_active": bool(feed_active),
        "dashboard_registry_feed_next_gate": feed_next_gate,
        "asset_lane": _feed_field(feed, "asset_lane"),
        "timeframe_lane": _feed_field(feed, "timeframe_lane"),
        "source_protocol_reference_placeholder": (
            "Source protocol reference is a placeholder for a later "
            "human-authored ledger contract."
        ),
        "source_runner_contract_reference_placeholder": (
            "Source runner contract reference is a placeholder for a later "
            "human-authored ledger contract."
        ),
        "source_orchestrator_reference_placeholder": (
            "Source orchestrator reference is a placeholder for a later "
            "human-authored ledger contract."
        ),
        "source_dashboard_feed_reference_placeholder": (
            "Source dashboard feed reference is a placeholder for a later "
            "human-authored ledger contract."
        ),
        "ledger_entry_fields": _LEDGER_ENTRY_FIELDS,
        "allowed_decision_values": ALLOWED_DECISION_VALUES,
        "required_human_review_fields": _REQUIRED_HUMAN_REVIEW_FIELDS,
        "required_safety_attestation_fields": (
            _REQUIRED_SAFETY_ATTESTATION_FIELDS
        ),
        "required_evidence_placeholders": _REQUIRED_EVIDENCE_PLACEHOLDERS,
        "decision_blocking_reasons": _DECISION_BLOCKING_REASONS,
        "expected_audit_fields": _EXPECTED_AUDIT_FIELDS,
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
        "dashboard_registry_feed_contract": (
            feed if isinstance(feed, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_decision_ledger_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a ledger contract template.
    Pure; writes no file. Informational only."""
    ledger = contract.get("ledger_entry_fields") or ()
    decisions = contract.get("allowed_decision_values") or ()
    review = contract.get("required_human_review_fields") or ()
    attest = contract.get("required_safety_attestation_fields") or ()
    evidence = contract.get("required_evidence_placeholders") or ()
    reasons = contract.get("decision_blocking_reasons") or ()
    audit = contract.get("expected_audit_fields") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Decision Ledger Contract")
    lines.append("")
    lines.append(
        "Template only: this is a decision-ledger-contract-only template -- "
        "no-runtime-ledger-write, research-only, and execution-free. It is "
        "not wired into any runtime ledger or the live dashboard, accesses "
        "no data, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Feed schema: "
        f"`{contract.get('dashboard_registry_feed_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Decision ledger contract active: "
        f"{contract.get('decision_ledger_contract_active', '')}"
    )
    lines.append(
        f"Ledger state: {contract.get('decision_ledger_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Ledger Entry Fields")
    lines.append("")
    for x in ledger:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Decision Values")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Human Review Fields")
    lines.append("")
    for x in review:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Safety Attestation Fields")
    lines.append("")
    for x in attest:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Evidence Placeholders")
    lines.append("")
    for x in evidence:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Decision Blocking Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Expected Audit Fields")
    lines.append("")
    for x in audit:
        lines.append(f"- `{x}`")
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
        "- A human must author the real decision ledger before the safety "
        "kill switch contract is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
