"""SPARTA Offline Strategy Factory - FAKE ARTIFACT DRY WALK CONTRACT (TEMPLATE).

Bundle 30 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only planning contract template* builder: it consumes a
Bundle 29 fake-artifact smoke test contract and, only when that contract is
active with next_gate == FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED, produces a
deterministic, read-only contract describing the SHAPE of a future dry walk
over fake-artifact placeholders. It defines a planning template only -- NOT a
live system, NOT a dry walk, NOT a smoke test, NOT a pipeline run.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs the dry walk, never orchestrates, never writes runtime
state, never persists an approval, never writes a ledger file, never updates
dashboard files, never writes a registry file, never performs research, never
runs QA, never runs a baseline, never backtests, never simulates, never
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
  - DRY_WALK_CONTRACT_SCHEMA_VERSION
  - DEFAULT_DRY_WALK_CONTRACT_LABEL
  - DRY_WALK_CONTRACT_STATUS
  - DRY_WALK_CONTRACT_SAFETY_POSTURE
  - DRY_WALK_STATE_ACTIVE
  - DRY_WALK_STATE_BLOCKED
  - NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT
  - DRY_WALK_STAGE_SEQUENCE
  - FAKE_STAGE_INPUT_PLACEHOLDERS
  - FAKE_STAGE_OUTPUT_PLACEHOLDERS
  - EXPECTED_STAGE_TRACE_RECORDS
  - EXPECTED_STAGE_REVIEW_RECORDS
  - FORBIDDEN_REAL_ARTIFACT_TOKENS
  - build_fake_artifact_dry_walk_contract(smoke_test)
  - validate_fake_artifact_dry_walk_contract(contract)
  - render_fake_artifact_dry_walk_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (  # noqa: E501
    SMOKE_TEST_CONTRACT_SCHEMA_VERSION,
    SMOKE_TEST_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED,
    FAKE_PIPELINE_STAGE_SEQUENCE,
    FORBIDDEN_REAL_ARTIFACT_TOKENS,
)

__all__ = [
    "DRY_WALK_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_DRY_WALK_CONTRACT_LABEL",
    "DRY_WALK_CONTRACT_STATUS",
    "DRY_WALK_CONTRACT_SAFETY_POSTURE",
    "DRY_WALK_STATE_ACTIVE",
    "DRY_WALK_STATE_BLOCKED",
    "NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT",
    "DRY_WALK_STAGE_SEQUENCE",
    "FAKE_STAGE_INPUT_PLACEHOLDERS",
    "FAKE_STAGE_OUTPUT_PLACEHOLDERS",
    "EXPECTED_STAGE_TRACE_RECORDS",
    "EXPECTED_STAGE_REVIEW_RECORDS",
    "FORBIDDEN_REAL_ARTIFACT_TOKENS",
    "build_fake_artifact_dry_walk_contract",
    "validate_fake_artifact_dry_walk_contract",
    "render_fake_artifact_dry_walk_contract_markdown",
]

DRY_WALK_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_artifact_dry_walk_contract.v1"
)
DEFAULT_DRY_WALK_CONTRACT_LABEL = (
    "Strategy Factory Fake Artifact Dry Walk Contract"
)
DRY_WALK_CONTRACT_STATUS = "READ_ONLY_FAKE_ARTIFACT_DRY_WALK_CONTRACT"

DRY_WALK_STATE_ACTIVE = "FAKE_ARTIFACT_DRY_WALK_CONTRACT_ACTIVE"
DRY_WALK_STATE_BLOCKED = "FAKE_ARTIFACT_DRY_WALK_CONTRACT_BLOCKED"

NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED = (
    "FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT = (
    "AWAIT_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT"
)

# Inherited all-false safety posture (same keys as Bundle 29). Pinned False:
# a planning contract template only describes a future dry walk; it grants
# nothing and is never wired into runtime state.
DRY_WALK_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    SMOKE_TEST_CONTRACT_SAFETY_POSTURE
)

# Ordered stage NAMES the future dry walk would walk -- labels only. Pinned to
# the Bundle 29 stage sequence so the chain stays consistent.
DRY_WALK_STAGE_SEQUENCE: tuple[str, ...] = tuple(FAKE_PIPELINE_STAGE_SEQUENCE)

# FAKE per-stage input placeholder NAMES -- labels only, one per stage.
FAKE_STAGE_INPUT_PLACEHOLDERS: tuple[str, ...] = tuple(
    f"fake_{stage}_input_placeholder" for stage in DRY_WALK_STAGE_SEQUENCE
)

# FAKE per-stage output placeholder NAMES -- labels only, one per stage.
FAKE_STAGE_OUTPUT_PLACEHOLDERS: tuple[str, ...] = tuple(
    f"fake_{stage}_output_placeholder" for stage in DRY_WALK_STAGE_SEQUENCE
)

# Trace record field NAMES a future dry walk would carry per stage -- labels.
EXPECTED_STAGE_TRACE_RECORDS: tuple[str, ...] = (
    "stage_name_placeholder",
    "input_placeholder_ref",
    "output_placeholder_ref",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

# Review record field NAMES a human would complete per stage -- labels only.
EXPECTED_STAGE_REVIEW_RECORDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

# Deterministic, verb-safe dry-walk pass criteria.
_DRY_WALK_PASS_CRITERIA: tuple[str, ...] = (
    "Every stage carries a fake input placeholder and a fake output "
    "placeholder.",
    "Every stage trace record placeholder is present.",
    "Every stage review record placeholder is present.",
    "Every safety posture key stays disabled.",
    "Every stage name is a fake placeholder only.",
    "No real artifact name is referenced anywhere.",
    "A human completes every stage review record by hand.",
)

# Deterministic, verb-safe dry-walk fail criteria.
_DRY_WALK_FAIL_CRITERIA: tuple[str, ...] = (
    "A fake stage input or output placeholder is missing.",
    "A stage trace record placeholder is absent.",
    "A stage review record placeholder is missing.",
    "A safety posture key is found enabled.",
    "A real artifact name is referenced.",
    "A stage name is not a fake placeholder.",
    "The stage sequence does not match the planned ten stages.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake-artifact dry walk contract template and is "
    "execution-free.",
    "It defines a future dry walk plan only and changes nothing.",
    "Every artifact it names is a fake placeholder, never real output.",
    "It writes no runtime state and accesses no data.",
    "A human must author the real dry walk out of band.",
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
    "pipeline_execution",
    "smoke_test_execution",
    "dry_walk_execution",
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
_SOURCE_FAKE_SMOKE_TEST_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Artifact Smoke Test Contract reference is a fake "
    "placeholder for a later human-authored dry-walk contract."
)

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_artifact_smoke_test_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_artifact_dry_walk_contract_active",
    "fake_artifact_dry_walk_state",
    "fake_artifact_smoke_test_contract_active",
    "fake_artifact_smoke_test_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_fake_smoke_test_reference_placeholder",
    "dry_walk_stage_sequence",
    "fake_stage_input_placeholders",
    "fake_stage_output_placeholders",
    "expected_stage_trace_records",
    "expected_stage_review_records",
    "dry_walk_pass_criteria",
    "dry_walk_fail_criteria",
    "placeholder_only_guard",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_artifact_smoke_test_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DRY_WALK_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _smoke_field(smoke_test: Any, key: str) -> str:
    """Read a string field from a possibly-malformed smoke contract; safe."""
    return _as_text(smoke_test.get(key)) if isinstance(smoke_test, dict) else ""


def _placeholder_only_guard(
    inputs: tuple[str, ...],
    outputs: tuple[str, ...],
    stages: tuple[str, ...],
) -> dict[str, Any]:
    """Pure deterministic placeholder-only guard. Confirms every input/output
    is a fake placeholder and that no name references a real artifact."""
    names = tuple(inputs) + tuple(outputs) + tuple(stages)
    inputs_ph = all("fake" in n and "placeholder" in n for n in inputs)
    outputs_ph = all("fake" in n and "placeholder" in n for n in outputs)
    no_real = not any(
        tok in n.lower()
        for n in names
        for tok in FORBIDDEN_REAL_ARTIFACT_TOKENS
    )
    return {
        "all_inputs_placeholder_only": bool(inputs_ph),
        "all_outputs_placeholder_only": bool(outputs_ph),
        "no_real_artifact_reference": bool(no_real),
        "forbidden_real_artifact_tokens": FORBIDDEN_REAL_ARTIFACT_TOKENS,
        "guard_holds": bool(inputs_ph and outputs_ph and no_real),
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DRY_WALK_CONTRACT_SCHEMA_VERSION
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
    stages = tuple(safe.get("dry_walk_stage_sequence") or ())
    inputs = tuple(safe.get("fake_stage_input_placeholders") or ())
    outputs = tuple(safe.get("fake_stage_output_placeholders") or ())
    passes = tuple(safe.get("dry_walk_pass_criteria") or ())
    fails = tuple(safe.get("dry_walk_fail_criteria") or ())
    guard = safe.get("placeholder_only_guard")
    guard_ok = isinstance(guard, dict) and guard.get("guard_holds") is True
    stage_match = stages == tuple(DRY_WALK_STAGE_SEQUENCE)
    fields_ok = (
        len(stages) == len(DRY_WALK_STAGE_SEQUENCE)
        and len(inputs) == len(stages)
        and len(outputs) == len(stages)
        and len(passes) >= 1
        and len(fails) >= 1
        and stage_match
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
        and guard_ok
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
        "placeholder_only_guard_holds": guard_ok,
        "stage_sequence_matches_plan": stage_match,
        "stages_and_criteria_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_fake_artifact_dry_walk_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake-artifact dry walk contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_artifact_dry_walk_contract(smoke_test: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only Strategy Factory fake-artifact
    dry walk contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The contract becomes active
    (fake_artifact_dry_walk_contract_active=True) solely when the upstream
    Bundle 29 fake-artifact smoke test contract is active AND its next_gate is
    FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED. Even when active, every
    authorization field stays False -- it describes a future fake dry walk
    only, writes no runtime state, accesses no data, names only fake
    placeholders, and grants nothing. Returned dicts are fresh."""
    smoke_active = (
        isinstance(smoke_test, dict)
        and smoke_test.get("fake_artifact_smoke_test_contract_active") is True
    )
    smoke_next_gate = _smoke_field(smoke_test, "next_gate")
    contract_active = bool(
        smoke_active
        and smoke_next_gate
        == NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED
    )
    state = (
        DRY_WALK_STATE_ACTIVE
        if contract_active
        else DRY_WALK_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_OPERATOR_REVIEW_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT
    )

    contract = {
        "schema_version": DRY_WALK_CONTRACT_SCHEMA_VERSION,
        "fake_artifact_smoke_test_contract_schema_version": (
            SMOKE_TEST_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _smoke_field(smoke_test, "idea_id"),
        "title": _smoke_field(smoke_test, "title"),
        "label": DEFAULT_DRY_WALK_CONTRACT_LABEL,
        "status": DRY_WALK_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_artifact_dry_walk_contract_active": contract_active,
        "fake_artifact_dry_walk_state": state,
        "fake_artifact_smoke_test_contract_active": bool(smoke_active),
        "fake_artifact_smoke_test_next_gate": smoke_next_gate,
        "asset_lane": _smoke_field(smoke_test, "asset_lane"),
        "timeframe_lane": _smoke_field(smoke_test, "timeframe_lane"),
        "source_fake_smoke_test_reference_placeholder": (
            _SOURCE_FAKE_SMOKE_TEST_REFERENCE_PLACEHOLDER
        ),
        "dry_walk_stage_sequence": DRY_WALK_STAGE_SEQUENCE,
        "fake_stage_input_placeholders": FAKE_STAGE_INPUT_PLACEHOLDERS,
        "fake_stage_output_placeholders": FAKE_STAGE_OUTPUT_PLACEHOLDERS,
        "expected_stage_trace_records": EXPECTED_STAGE_TRACE_RECORDS,
        "expected_stage_review_records": EXPECTED_STAGE_REVIEW_RECORDS,
        "dry_walk_pass_criteria": _DRY_WALK_PASS_CRITERIA,
        "dry_walk_fail_criteria": _DRY_WALK_FAIL_CRITERIA,
        "placeholder_only_guard": _placeholder_only_guard(
            FAKE_STAGE_INPUT_PLACEHOLDERS,
            FAKE_STAGE_OUTPUT_PLACEHOLDERS,
            DRY_WALK_STAGE_SEQUENCE,
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
        "fake_artifact_smoke_test_contract": (
            smoke_test if isinstance(smoke_test, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_artifact_dry_walk_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake-artifact dry walk
    contract template. Pure; writes no file. Informational only."""
    stages = contract.get("dry_walk_stage_sequence") or ()
    inputs = contract.get("fake_stage_input_placeholders") or ()
    outputs = contract.get("fake_stage_output_placeholders") or ()
    trace = contract.get("expected_stage_trace_records") or ()
    review = contract.get("expected_stage_review_records") or ()
    passes = contract.get("dry_walk_pass_criteria") or ()
    fails = contract.get("dry_walk_fail_criteria") or ()
    guard = contract.get("placeholder_only_guard") or {}
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Artifact Dry Walk Contract")
    lines.append("")
    lines.append(
        "Template only: this is a fake-artifact-dry-walk-contract-only, "
        "planning-only, placeholder-only template -- no-runtime-state-write, "
        "research-only, and execution-free. It is not wired into any runtime "
        "state, accesses no data, names only fake placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Smoke schema: "
        f"`{contract.get('fake_artifact_smoke_test_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake artifact dry walk contract active: "
        f"{contract.get('fake_artifact_dry_walk_contract_active', '')}"
    )
    lines.append(
        f"Contract state: {contract.get('fake_artifact_dry_walk_state', '')}"
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
        "Source fake smoke test reference: "
        f"{contract.get('source_fake_smoke_test_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Dry Walk Stage Sequence")
    lines.append("")
    for x in stages:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Stage Input Placeholders")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Stage Output Placeholders")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Stage Trace Records")
    lines.append("")
    for x in trace:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Stage Review Records")
    lines.append("")
    for x in review:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Dry Walk Pass Criteria")
    lines.append("")
    for x in passes:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Dry Walk Fail Criteria")
    lines.append("")
    for x in fails:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Placeholder Only Guard")
    lines.append("")
    for key, value in guard.items():
        lines.append(f"- `{key}`: `{value}`")
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
        "- A human must author and review the fake-artifact dry walk before "
        "any later phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
