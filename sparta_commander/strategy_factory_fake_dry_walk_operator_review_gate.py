"""SPARTA Offline Strategy Factory - FAKE DRY-WALK OPERATOR REVIEW GATE (TEMPLATE).

Bundle 31 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only planning gate template* builder: it consumes a Bundle 30
fake-artifact dry walk contract and, only when that contract is active with
next_gate == FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED, produces a
deterministic, read-only contract describing the SHAPE of the human/operator
review gate that must precede any future fake dry-walk implementation. It
defines a planning template only -- NOT a live system, NOT a dry walk, NOT a
smoke test, NOT a pipeline run, NOT an operator review run.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs the dry walk, never runs an orchestrator, never writes
runtime state, never persists an approval, never writes a ledger file, never
updates dashboard files, never writes a registry file, never performs research,
never runs QA, never runs a baseline, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing. It opens no network, spawns no subprocess, writes no file,
touches no broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION
  - DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL
  - DRY_WALK_OPERATOR_REVIEW_GATE_STATUS
  - DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE
  - GATE_STATE_ACTIVE
  - GATE_STATE_BLOCKED
  - OPERATOR_DECISION_NEEDS_MORE_SPEC
  - OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
  - OPERATOR_DECISION_PARK
  - OPERATOR_DECISION_REJECT
  - ALLOWED_OPERATOR_DECISIONS
  - NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED
  - NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED
  - NEXT_GATE_FAKE_DRY_WALK_PARKED
  - NEXT_GATE_FAKE_DRY_WALK_REJECTED
  - NEXT_GATE_AWAIT_OPERATOR_DECISION
  - NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT
  - REQUIRED_OPERATOR_REVIEW_FIELDS
  - REQUIRED_SAFETY_ATTESTATION_FIELDS
  - REJECTION_CONDITIONS
  - build_fake_dry_walk_operator_review_gate(dry_walk, operator_decision=None)
  - validate_fake_dry_walk_operator_review_gate(contract)
  - render_fake_dry_walk_operator_review_gate_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (  # noqa: E501
    DRY_WALK_CONTRACT_SCHEMA_VERSION,
    DRY_WALK_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED,
)

__all__ = [
    "DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION",
    "DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL",
    "DRY_WALK_OPERATOR_REVIEW_GATE_STATUS",
    "DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE",
    "GATE_STATE_ACTIVE",
    "GATE_STATE_BLOCKED",
    "OPERATOR_DECISION_NEEDS_MORE_SPEC",
    "OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT",
    "OPERATOR_DECISION_PARK",
    "OPERATOR_DECISION_REJECT",
    "ALLOWED_OPERATOR_DECISIONS",
    "NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED",
    "NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED",
    "NEXT_GATE_FAKE_DRY_WALK_PARKED",
    "NEXT_GATE_FAKE_DRY_WALK_REJECTED",
    "NEXT_GATE_AWAIT_OPERATOR_DECISION",
    "NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT",
    "REQUIRED_OPERATOR_REVIEW_FIELDS",
    "REQUIRED_SAFETY_ATTESTATION_FIELDS",
    "REJECTION_CONDITIONS",
    "build_fake_dry_walk_operator_review_gate",
    "validate_fake_dry_walk_operator_review_gate",
    "render_fake_dry_walk_operator_review_gate_markdown",
]

DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION = (
    "strategy_factory_fake_dry_walk_operator_review_gate.v1"
)
DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL = (
    "Strategy Factory Fake Dry Walk Operator Review Gate"
)
DRY_WALK_OPERATOR_REVIEW_GATE_STATUS = (
    "READ_ONLY_FAKE_DRY_WALK_OPERATOR_REVIEW_GATE"
)

GATE_STATE_ACTIVE = "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_ACTIVE"
GATE_STATE_BLOCKED = "FAKE_DRY_WALK_OPERATOR_REVIEW_GATE_BLOCKED"

# The four operator decisions a human may record by hand -- labels only.
OPERATOR_DECISION_NEEDS_MORE_SPEC = "NEEDS_MORE_SPEC"
OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT = (
    "READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
)
OPERATOR_DECISION_PARK = "PARK"
OPERATOR_DECISION_REJECT = "REJECT"
ALLOWED_OPERATOR_DECISIONS: tuple[str, ...] = (
    OPERATOR_DECISION_NEEDS_MORE_SPEC,
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    OPERATOR_DECISION_PARK,
    OPERATOR_DECISION_REJECT,
)

# The single forward gate (only the ready decision unlocks it) plus the safe
# paused/blocked gates for every other decision and for inactive inputs.
NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED = (
    "FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED"
)
NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED = "FAKE_DRY_WALK_SPEC_FIX_REQUIRED"
NEXT_GATE_FAKE_DRY_WALK_PARKED = "FAKE_DRY_WALK_PARKED"
NEXT_GATE_FAKE_DRY_WALK_REJECTED = "FAKE_DRY_WALK_REJECTED"
NEXT_GATE_AWAIT_OPERATOR_DECISION = "AWAIT_OPERATOR_DECISION"
NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT = (
    "AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT"
)

# Decision -> forward/paused gate. A missing/unknown decision is absent here
# and falls back to AWAIT_OPERATOR_DECISION.
_DECISION_NEXT_GATE: dict[str, str] = {
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT: (
        NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED
    ),
    OPERATOR_DECISION_NEEDS_MORE_SPEC: (
        NEXT_GATE_FAKE_DRY_WALK_SPEC_FIX_REQUIRED
    ),
    OPERATOR_DECISION_PARK: NEXT_GATE_FAKE_DRY_WALK_PARKED,
    OPERATOR_DECISION_REJECT: NEXT_GATE_FAKE_DRY_WALK_REJECTED,
}

# Inherited all-false safety posture (same keys as Bundle 30). Pinned False:
# a planning gate template only describes a future operator review; it grants
# nothing and is never wired into runtime state.
DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE: dict[str, bool] = dict(
    DRY_WALK_CONTRACT_SAFETY_POSTURE
)

# Review record field NAMES a human operator would complete -- labels only.
REQUIRED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "review_window_placeholder",
    "dry_walk_spec_assessment_placeholder",
    "blocking_findings_placeholder",
    "operator_decision_placeholder",
)

# Safety attestation field NAMES a human operator must affirm -- labels only.
REQUIRED_SAFETY_ATTESTATION_FIELDS: tuple[str, ...] = (
    "no_real_data_attestation_placeholder",
    "no_execution_attestation_placeholder",
    "no_runtime_state_write_attestation_placeholder",
    "placeholder_only_attestation_placeholder",
    "human_sign_off_attestation_placeholder",
)

# Deterministic, verb-safe conditions that force a blocked/rejected outcome.
REJECTION_CONDITIONS: tuple[str, ...] = (
    "A real artifact name is referenced anywhere.",
    "Any safety posture key is enabled.",
    "Any authorization flag is set true.",
    "The placeholder-only guard does not hold.",
    "Any safety attestation field is incomplete.",
    "The dry walk stage sequence does not match the planned ten stages.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake dry walk operator review gate template and is "
    "execution-free.",
    "It defines a future operator review gate only and changes nothing.",
    "A human operator must complete every review and attestation field by "
    "hand.",
    "Only the ready decision points toward a later implementation contract.",
    "It writes no runtime state and accesses no data.",
    "No automated step may proceed without human sign-off.",
)

# A placeholder approval window note -- a human sets any window by hand.
_APPROVAL_EXPIRY_PLACEHOLDER = (
    "Approval window is a placeholder a human sets by hand out of band; no "
    "automated window applies and nothing is persisted."
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
    "pipeline_execution",
    "smoke_test_execution",
    "dry_walk_execution",
    "operator_review_gate_execution",
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

# The source reference is a fake placeholder, never a real contract handle.
_SOURCE_FAKE_DRY_WALK_CONTRACT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Artifact Dry Walk Contract reference is a fake "
    "placeholder for a later human-authored operator review gate."
)

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_artifact_dry_walk_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_dry_walk_operator_review_gate_active",
    "fake_dry_walk_operator_review_gate_state",
    "fake_artifact_dry_walk_contract_active",
    "fake_artifact_dry_walk_next_gate",
    "asset_lane",
    "timeframe_lane",
    "operator_decision",
    "source_fake_dry_walk_contract_reference_placeholder",
    "required_operator_review_fields",
    "required_safety_attestation_fields",
    "allowed_operator_decisions",
    "approval_expiry_placeholder",
    "rejection_conditions",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_artifact_dry_walk_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DRY_WALK_OPERATOR_REVIEW_GATE_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _dw_field(dry_walk: Any, key: str) -> str:
    """Read a string field from a possibly-malformed dry walk contract; safe."""
    return _as_text(dry_walk.get(key)) if isinstance(dry_walk, dict) else ""


def _normalize_decision(operator_decision: Any) -> str:
    """Return the operator decision if it is one of the allowed labels, else
    the empty string. Never raises."""
    return (
        operator_decision
        if operator_decision in ALLOWED_OPERATOR_DECISIONS
        else ""
    )


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION
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
    decisions = tuple(safe.get("allowed_operator_decisions") or ())
    review_fields = tuple(safe.get("required_operator_review_fields") or ())
    attest_fields = tuple(
        safe.get("required_safety_attestation_fields") or ()
    )
    rejections = tuple(safe.get("rejection_conditions") or ())
    decisions_ok = decisions == tuple(ALLOWED_OPERATOR_DECISIONS)
    fields_ok = (
        decisions_ok
        and len(review_fields) >= 1
        and len(attest_fields) >= 1
        and len(rejections) >= 1
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
        "allowed_operator_decisions_match": decisions_ok,
        "review_and_attestation_fields_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_fake_dry_walk_operator_review_gate(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake dry walk operator review gate
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_dry_walk_operator_review_gate(
    dry_walk: Any,
    operator_decision: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only Strategy Factory fake dry walk
    operator review gate template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The gate becomes active
    (fake_dry_walk_operator_review_gate_active=True) solely when the upstream
    Bundle 30 fake-artifact dry walk contract is active AND its next_gate is
    FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED. Even when active, every
    authorization field stays False -- it describes a future operator review
    gate only, writes no runtime state, accesses no data, names only fake
    placeholders, and grants nothing. The forward gate
    FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT_REQUIRED is reachable solely when the
    operator decision is READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT; every
    other decision yields a paused gate and a missing/unknown decision yields
    AWAIT_OPERATOR_DECISION. Returned dicts are fresh."""
    dw_active = (
        isinstance(dry_walk, dict)
        and dry_walk.get("fake_artifact_dry_walk_contract_active") is True
    )
    dw_next_gate = _dw_field(dry_walk, "next_gate")
    gate_active = bool(
        dw_active
        and dw_next_gate
        == NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED
    )
    decision = _normalize_decision(operator_decision)

    if not gate_active:
        next_gate = NEXT_GATE_AWAIT_FAKE_ARTIFACT_DRY_WALK_CONTRACT
    else:
        next_gate = _DECISION_NEXT_GATE.get(
            decision, NEXT_GATE_AWAIT_OPERATOR_DECISION
        )

    state = GATE_STATE_ACTIVE if gate_active else GATE_STATE_BLOCKED

    contract = {
        "schema_version": DRY_WALK_OPERATOR_REVIEW_GATE_SCHEMA_VERSION,
        "fake_artifact_dry_walk_contract_schema_version": (
            DRY_WALK_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _dw_field(dry_walk, "idea_id"),
        "title": _dw_field(dry_walk, "title"),
        "label": DEFAULT_DRY_WALK_OPERATOR_REVIEW_GATE_LABEL,
        "status": DRY_WALK_OPERATOR_REVIEW_GATE_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_dry_walk_operator_review_gate_active": gate_active,
        "fake_dry_walk_operator_review_gate_state": state,
        "fake_artifact_dry_walk_contract_active": bool(dw_active),
        "fake_artifact_dry_walk_next_gate": dw_next_gate,
        "asset_lane": _dw_field(dry_walk, "asset_lane"),
        "timeframe_lane": _dw_field(dry_walk, "timeframe_lane"),
        "operator_decision": decision,
        "source_fake_dry_walk_contract_reference_placeholder": (
            _SOURCE_FAKE_DRY_WALK_CONTRACT_REFERENCE_PLACEHOLDER
        ),
        "required_operator_review_fields": REQUIRED_OPERATOR_REVIEW_FIELDS,
        "required_safety_attestation_fields": (
            REQUIRED_SAFETY_ATTESTATION_FIELDS
        ),
        "allowed_operator_decisions": ALLOWED_OPERATOR_DECISIONS,
        "approval_expiry_placeholder": _APPROVAL_EXPIRY_PLACEHOLDER,
        "rejection_conditions": REJECTION_CONDITIONS,
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
        "fake_artifact_dry_walk_contract": (
            dry_walk if isinstance(dry_walk, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_dry_walk_operator_review_gate_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake dry walk operator
    review gate template. Pure; writes no file. Informational only."""
    decisions = contract.get("allowed_operator_decisions") or ()
    review_fields = contract.get("required_operator_review_fields") or ()
    attest_fields = contract.get("required_safety_attestation_fields") or ()
    rejections = contract.get("rejection_conditions") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Fake Dry Walk Operator Review Gate"
    )
    lines.append("")
    lines.append(
        "Template only: this is a fake-dry-walk-operator-review-gate-only, "
        "planning-only, placeholder-only template -- no-runtime-state-write, "
        "research-only, and execution-free. It is not wired into any runtime "
        "state, accesses no data, names only fake placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Dry walk schema: "
        f"`{contract.get('fake_artifact_dry_walk_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake dry walk operator review gate active: "
        f"{contract.get('fake_dry_walk_operator_review_gate_active', '')}"
    )
    lines.append(
        "Gate state: "
        f"{contract.get('fake_dry_walk_operator_review_gate_state', '')}"
    )
    lines.append(f"Operator decision: {contract.get('operator_decision', '')}")
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
        "Source fake dry walk contract reference: "
        f"{contract.get('source_fake_dry_walk_contract_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Allowed Operator Decisions")
    lines.append("")
    for x in decisions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Operator Review Fields")
    lines.append("")
    for x in review_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Safety Attestation Fields")
    lines.append("")
    for x in attest_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Approval Expiry")
    lines.append("")
    lines.append(
        f"Approval expiry: {contract.get('approval_expiry_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Rejection Conditions")
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
        "- A human operator must review and attest the fake dry walk before "
        "any later phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
