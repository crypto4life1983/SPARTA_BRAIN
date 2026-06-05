"""SPARTA Offline Strategy Factory - DASHBOARD REGISTRY FEED CONTRACT
(TEMPLATE) v1.

Bundle 24 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only dashboard/registry feed contract template* builder: it
consumes a Bundle 23 dry-run orchestrator contract and, only when that contract
is active with next_gate == DASHBOARD_REGISTRY_FEED_REQUIRED, produces a
deterministic, read-only *template* describing the shape a future
dashboard/JARVIS registry feed for Strategy Factory artifacts must take. It
defines a feed contract template only -- NOT a live feed.

It never updates the live dashboard, writes no registry file, alters no
template, never orchestrates anything, never performs research, never
backtests, never simulates, never fetches, inspects, loads, validates,
transforms, or computes on real data, and executes nothing. It opens no
network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DASHBOARD_REGISTRY_FEED_CONTRACT_LABEL
  - DASHBOARD_REGISTRY_FEED_CONTRACT_STATUS
  - DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE
  - DASHBOARD_REGISTRY_FEED_STATE_ACTIVE
  - DASHBOARD_REGISTRY_FEED_STATE_BLOCKED
  - NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_DRY_RUN_ORCHESTRATOR_CONTRACT
  - build_dashboard_registry_feed_contract(orchestrator)
  - validate_dashboard_registry_feed_contract(contract)
  - render_dashboard_registry_feed_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
    DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION,
    DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED,
)

__all__ = [
    "DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DASHBOARD_REGISTRY_FEED_CONTRACT_LABEL",
    "DASHBOARD_REGISTRY_FEED_CONTRACT_STATUS",
    "DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE",
    "DASHBOARD_REGISTRY_FEED_STATE_ACTIVE",
    "DASHBOARD_REGISTRY_FEED_STATE_BLOCKED",
    "NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_DRY_RUN_ORCHESTRATOR_CONTRACT",
    "build_dashboard_registry_feed_contract",
    "validate_dashboard_registry_feed_contract",
    "render_dashboard_registry_feed_contract_markdown",
]

DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_dashboard_registry_feed_contract.v1"
)
DEFAULT_DASHBOARD_REGISTRY_FEED_CONTRACT_LABEL = (
    "Strategy Factory Dashboard Registry Feed Contract"
)
DASHBOARD_REGISTRY_FEED_CONTRACT_STATUS = (
    "READ_ONLY_DASHBOARD_REGISTRY_FEED_CONTRACT"
)

DASHBOARD_REGISTRY_FEED_STATE_ACTIVE = (
    "DASHBOARD_REGISTRY_FEED_CONTRACT_ACTIVE"
)
DASHBOARD_REGISTRY_FEED_STATE_BLOCKED = (
    "DASHBOARD_REGISTRY_FEED_CONTRACT_BLOCKED"
)

NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED = (
    "DECISION_LEDGER_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_DRY_RUN_ORCHESTRATOR_CONTRACT = (
    "AWAIT_DRY_RUN_ORCHESTRATOR_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 23). Pinned False:
# a feed contract template only describes a future shape; it grants nothing
# and is never wired into the live dashboard.
DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DRY_RUN_ORCHESTRATOR_CONTRACT_SAFETY_POSTURE
)

# Registry entry field NAMES a future registry row would carry -- labels only.
_REGISTRY_ENTRY_FIELDS: tuple[str, ...] = (
    "artifact_id",
    "artifact_type",
    "schema_version",
    "created_reference_placeholder",
    "stage",
    "status_placeholder",
    "next_gate",
)

# Dashboard feed field NAMES a future feed row would carry -- labels only.
_DASHBOARD_FEED_FIELDS: tuple[str, ...] = (
    "feed_entry_id",
    "title",
    "asset_lane",
    "timeframe_lane",
    "status_badge",
    "safety_badge",
    "artifact_link",
    "last_refresh_placeholder",
)

# Status badge NAMES -- placeholder labels only.
_STATUS_BADGE_PLACEHOLDERS: tuple[str, ...] = (
    "status_badge_pending",
    "status_badge_in_review",
    "status_badge_ready",
    "status_badge_parked",
    "status_badge_rejected",
)

# Safety badge NAMES -- placeholder labels only.
_SAFETY_BADGE_PLACEHOLDERS: tuple[str, ...] = (
    "safety_badge_read_only",
    "safety_badge_execution_free",
    "safety_badge_no_live_dashboard_update",
    "safety_badge_human_approval_required",
)

# Artifact link NAMES -- placeholder labels only, never real links.
_ARTIFACT_LINK_PLACEHOLDERS: tuple[str, ...] = (
    "protocol_artifact_link_placeholder",
    "runner_contract_artifact_link_placeholder",
    "dry_run_orchestrator_artifact_link_placeholder",
    "trace_manifest_artifact_link_placeholder",
)

# Operator visibility field NAMES a human reviewer would see -- labels only.
_OPERATOR_VISIBILITY_FIELDS: tuple[str, ...] = (
    "operator_review_state",
    "blocking_reasons_placeholder",
    "next_action_placeholder",
    "human_sign_off_placeholder",
)

# Single deterministic, verb-safe refresh-behavior description.
_EXPECTED_REFRESH_BEHAVIOR_PLACEHOLDER = (
    "The feed refresh cadence is a placeholder for a later human-authored "
    "dashboard contract and performs no live dashboard change."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only dashboard registry feed contract and is "
    "execution-free.",
    "It is not wired into the live dashboard and touches no registry file.",
    "A human must author the real dashboard feed out of band.",
    "No live dashboard is changed and nothing is computed by this template.",
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
    "dry_run_orchestrator_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "dashboard_registry_feed_contract_active",
    "dashboard_registry_feed_state",
    "dry_run_orchestrator_contract_active",
    "dry_run_orchestrator_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_protocol_reference_placeholder",
    "source_runner_contract_reference_placeholder",
    "source_dry_run_orchestrator_reference_placeholder",
    "registry_entry_fields",
    "dashboard_feed_fields",
    "status_badge_placeholders",
    "safety_badge_placeholders",
    "artifact_link_placeholders",
    "operator_visibility_fields",
    "expected_refresh_behavior_placeholder",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "dry_run_orchestrator_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DASHBOARD_REGISTRY_FEED_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _orch_field(orchestrator: Any, key: str) -> str:
    """Read a string field from a possibly-malformed orchestrator dict; safe."""
    return (
        _as_text(orchestrator.get(key))
        if isinstance(orchestrator, dict)
        else ""
    )


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION
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
    registry = tuple(safe.get("registry_entry_fields") or ())
    feed = tuple(safe.get("dashboard_feed_fields") or ())
    fields_ok = len(registry) >= 1 and len(feed) >= 1

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
        "registry_and_feed_fields_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_dashboard_registry_feed_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a dashboard registry feed contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_dashboard_registry_feed_contract(
    orchestrator: Any,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only dashboard registry feed contract
    template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (dashboard_registry_feed_contract_active=True) solely when the upstream
    Bundle 23 dry-run orchestrator contract is active AND its next_gate is
    DASHBOARD_REGISTRY_FEED_REQUIRED. Even when active, every authorization
    field stays False -- it defines a feed contract template only, updates no
    live dashboard, writes no registry file, accesses no data, and grants
    nothing. Returned dicts are fresh."""
    orch_active = (
        isinstance(orchestrator, dict)
        and orchestrator.get("dry_run_orchestrator_contract_active") is True
    )
    orch_next_gate = _orch_field(orchestrator, "next_gate")
    contract_active = bool(
        orch_active
        and orch_next_gate == NEXT_GATE_DASHBOARD_REGISTRY_FEED_REQUIRED
    )
    state = (
        DASHBOARD_REGISTRY_FEED_STATE_ACTIVE
        if contract_active
        else DASHBOARD_REGISTRY_FEED_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_DECISION_LEDGER_CONTRACT_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_DRY_RUN_ORCHESTRATOR_CONTRACT
    )

    contract = {
        "schema_version": DASHBOARD_REGISTRY_FEED_CONTRACT_SCHEMA_VERSION,
        "dry_run_orchestrator_contract_schema_version": (
            DRY_RUN_ORCHESTRATOR_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _orch_field(orchestrator, "idea_id"),
        "title": _orch_field(orchestrator, "title"),
        "label": DEFAULT_DASHBOARD_REGISTRY_FEED_CONTRACT_LABEL,
        "status": DASHBOARD_REGISTRY_FEED_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "dashboard_registry_feed_contract_active": contract_active,
        "dashboard_registry_feed_state": state,
        "dry_run_orchestrator_contract_active": bool(orch_active),
        "dry_run_orchestrator_next_gate": orch_next_gate,
        "asset_lane": _orch_field(orchestrator, "asset_lane"),
        "timeframe_lane": _orch_field(orchestrator, "timeframe_lane"),
        "source_protocol_reference_placeholder": (
            "Source protocol reference is a placeholder for a later "
            "human-authored dashboard contract."
        ),
        "source_runner_contract_reference_placeholder": (
            "Source runner contract reference is a placeholder for a later "
            "human-authored dashboard contract."
        ),
        "source_dry_run_orchestrator_reference_placeholder": (
            "Source orchestrator reference is a placeholder for a later "
            "human-authored dashboard contract."
        ),
        "registry_entry_fields": _REGISTRY_ENTRY_FIELDS,
        "dashboard_feed_fields": _DASHBOARD_FEED_FIELDS,
        "status_badge_placeholders": _STATUS_BADGE_PLACEHOLDERS,
        "safety_badge_placeholders": _SAFETY_BADGE_PLACEHOLDERS,
        "artifact_link_placeholders": _ARTIFACT_LINK_PLACEHOLDERS,
        "operator_visibility_fields": _OPERATOR_VISIBILITY_FIELDS,
        "expected_refresh_behavior_placeholder": (
            _EXPECTED_REFRESH_BEHAVIOR_PLACEHOLDER
        ),
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
        "dry_run_orchestrator_contract": (
            orchestrator if isinstance(orchestrator, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_dashboard_registry_feed_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a feed contract template.
    Pure; writes no file. Informational only."""
    registry = contract.get("registry_entry_fields") or ()
    feed = contract.get("dashboard_feed_fields") or ()
    status_badges = contract.get("status_badge_placeholders") or ()
    safety_badges = contract.get("safety_badge_placeholders") or ()
    links = contract.get("artifact_link_placeholders") or ()
    visibility = contract.get("operator_visibility_fields") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Dashboard Registry Feed Contract")
    lines.append("")
    lines.append(
        "Template only: this is a dashboard-registry-feed-contract-only "
        "template -- no-live-dashboard-update, research-only, and "
        "execution-free. It is not wired into the live dashboard, accesses "
        "no data, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Orchestrator schema: "
        f"`{contract.get('dry_run_orchestrator_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Dashboard registry feed contract active: "
        f"{contract.get('dashboard_registry_feed_contract_active', '')}"
    )
    lines.append(
        "Feed state: "
        f"{contract.get('dashboard_registry_feed_state', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append(
        "Refresh behavior: "
        f"{contract.get('expected_refresh_behavior_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Registry Entry Fields")
    lines.append("")
    for x in registry:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Dashboard Feed Fields")
    lines.append("")
    for x in feed:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Status Badge Placeholders")
    lines.append("")
    for x in status_badges:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Safety Badge Placeholders")
    lines.append("")
    for x in safety_badges:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Artifact Link Placeholders")
    lines.append("")
    for x in links:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Operator Visibility Fields")
    lines.append("")
    for x in visibility:
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
        "- A human must author the real dashboard registry feed before the "
        "decision ledger contract is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
