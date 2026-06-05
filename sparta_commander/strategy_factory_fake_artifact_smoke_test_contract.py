"""SPARTA Offline Strategy Factory - FAKE ARTIFACT SMOKE TEST CONTRACT (TEMPLATE).

Bundle 29 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only planning contract template* builder: it consumes a
Bundle 28 backbone closure report and, only when that report is active with
final_backbone_status == STRATEGY_FACTORY_V1_BACKBONE_COMPLETE,
next_gate == PAUSE_AND_OPERATOR_REVIEW, and
recommended_next_phase == FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY, produces a
deterministic, read-only contract describing the SHAPE of a future
fake-artifact smoke test. It defines a planning template only -- NOT a live
system, NOT a smoke test, NOT a pipeline run.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never orchestrates, never dry-walks, never writes runtime state,
never persists an approval, never writes a ledger file, never updates dashboard
files, never writes a registry file, never performs research, never runs QA,
never runs a baseline, never backtests, never simulates, never fetches,
inspects, loads, validates, transforms, or computes on real data, and executes
nothing. It opens no network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - SMOKE_TEST_CONTRACT_SCHEMA_VERSION
  - DEFAULT_SMOKE_TEST_CONTRACT_LABEL
  - SMOKE_TEST_CONTRACT_STATUS
  - SMOKE_TEST_CONTRACT_SAFETY_POSTURE
  - SMOKE_TEST_STATE_ACTIVE
  - SMOKE_TEST_STATE_BLOCKED
  - NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW
  - FAKE_INPUT_ARTIFACTS_REQUIRED
  - FAKE_OUTPUT_ARTIFACTS_EXPECTED
  - FAKE_PIPELINE_STAGE_SEQUENCE
  - EXPECTED_TRACE_FIELDS
  - EXPECTED_OPERATOR_REVIEW_FIELDS
  - FORBIDDEN_REAL_ARTIFACT_TOKENS
  - build_fake_artifact_smoke_test_contract(closure)
  - validate_fake_artifact_smoke_test_contract(contract)
  - render_fake_artifact_smoke_test_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_backbone_closure_report import (
    BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION,
    BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE,
    FINAL_BACKBONE_STATUS_COMPLETE,
    RECOMMENDED_NEXT_PHASE,
    NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW,
)

__all__ = [
    "SMOKE_TEST_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_SMOKE_TEST_CONTRACT_LABEL",
    "SMOKE_TEST_CONTRACT_STATUS",
    "SMOKE_TEST_CONTRACT_SAFETY_POSTURE",
    "SMOKE_TEST_STATE_ACTIVE",
    "SMOKE_TEST_STATE_BLOCKED",
    "NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW",
    "FAKE_INPUT_ARTIFACTS_REQUIRED",
    "FAKE_OUTPUT_ARTIFACTS_EXPECTED",
    "FAKE_PIPELINE_STAGE_SEQUENCE",
    "EXPECTED_TRACE_FIELDS",
    "EXPECTED_OPERATOR_REVIEW_FIELDS",
    "FORBIDDEN_REAL_ARTIFACT_TOKENS",
    "build_fake_artifact_smoke_test_contract",
    "validate_fake_artifact_smoke_test_contract",
    "render_fake_artifact_smoke_test_contract_markdown",
]

SMOKE_TEST_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_fake_artifact_smoke_test_contract.v1"
)
DEFAULT_SMOKE_TEST_CONTRACT_LABEL = (
    "Strategy Factory Fake Artifact Smoke Test Contract"
)
SMOKE_TEST_CONTRACT_STATUS = "READ_ONLY_FAKE_ARTIFACT_SMOKE_TEST_CONTRACT"

SMOKE_TEST_STATE_ACTIVE = "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_ACTIVE"
SMOKE_TEST_STATE_BLOCKED = "FAKE_ARTIFACT_SMOKE_TEST_CONTRACT_BLOCKED"

NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED = (
    "FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW = (
    "AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW"
)

# Inherited all-false safety posture (same keys as Bundle 28). Pinned False:
# a planning contract template only describes a future smoke test; it grants
# nothing and is never wired into runtime state.
SMOKE_TEST_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    BACKBONE_CLOSURE_REPORT_SAFETY_POSTURE
)

# FAKE artifact input NAMES the future smoke test would accept -- labels only.
FAKE_INPUT_ARTIFACTS_REQUIRED: tuple[str, ...] = (
    "fake_idea_record_placeholder",
    "fake_protocol_draft_placeholder",
    "fake_data_contract_placeholder",
    "fake_data_qa_report_placeholder",
)

# FAKE artifact output NAMES the future smoke test would expect -- labels only.
FAKE_OUTPUT_ARTIFACTS_EXPECTED: tuple[str, ...] = (
    "fake_summary_metrics_placeholder",
    "fake_risk_metrics_placeholder",
    "fake_trace_manifest_placeholder",
    "fake_operator_review_packet_placeholder",
)

# Ordered stage NAMES the future smoke test would walk -- labels only.
FAKE_PIPELINE_STAGE_SEQUENCE: tuple[str, ...] = (
    "research_queue_intake",
    "research_protocol_draft",
    "protocol_review_gate",
    "data_contract_planning",
    "data_qa_review",
    "research_runner_review",
    "dry_walk_orchestrator_review",
    "dashboard_registry_feed_review",
    "decision_ledger_review",
    "safety_kill_switch_review",
)

# Trace field NAMES the future smoke test would carry -- labels only.
EXPECTED_TRACE_FIELDS: tuple[str, ...] = (
    "trace_id_placeholder",
    "stage_name_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)

# Operator review field NAMES a human would complete -- labels only.
EXPECTED_OPERATOR_REVIEW_FIELDS: tuple[str, ...] = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)

# Lowercase substrings that would mark a name as a REAL (non-placeholder)
# artifact. The placeholder-only guard flags any name containing one of these.
FORBIDDEN_REAL_ARTIFACT_TOKENS: tuple[str, ...] = (
    "crypto-d1",
    "crypto_d1",
    "qa_report.json",
    "manifest.json",
    "checksums.txt",
    "freeze_record.txt",
    "fees.json",
    "baseline",
    "dataset",
    ".csv",
    ".parquet",
    "/data/",
)

# Deterministic, verb-safe pass criteria for the future smoke test.
_PASS_CRITERIA: tuple[str, ...] = (
    "Every stage maps a fake input placeholder to a fake output placeholder.",
    "Every trace field placeholder is present for each stage.",
    "Every operator review field placeholder is present.",
    "Every safety posture key stays disabled.",
    "Every artifact name is a fake placeholder only.",
    "No real artifact name is referenced anywhere.",
    "A human completes every operator review field by hand.",
)

# Deterministic, verb-safe fail criteria for the future smoke test.
_FAIL_CRITERIA: tuple[str, ...] = (
    "A fake artifact placeholder is missing.",
    "A stage produced no expected output placeholder.",
    "A trace field placeholder is absent for a stage.",
    "A safety posture key is found enabled.",
    "An operator review field placeholder is missing.",
    "A real artifact name is referenced.",
    "An artifact name is not a fake placeholder.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake-artifact smoke test contract template and is "
    "execution-free.",
    "It defines a future smoke test plan only and changes nothing.",
    "Every artifact it names is a fake placeholder, never real output.",
    "It writes no runtime state and accesses no data.",
    "A human must author the real smoke test out of band.",
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

# The source reference is a fake placeholder, never a real report handle.
_SOURCE_BACKBONE_CLOSURE_REFERENCE_PLACEHOLDER = (
    "Strategy Factory v1 Backbone Closure Report reference is a fake "
    "placeholder for a later human-authored smoke-test contract."
)

# Top-level schema fields required for a contract to validate.
# NOTE: "validation" is intentionally NOT required here -- requiring the
# contract to embed its own validation result would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "backbone_closure_report_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_artifact_smoke_test_contract_active",
    "fake_artifact_smoke_test_state",
    "backbone_closure_report_active",
    "backbone_closure_final_status",
    "backbone_closure_next_gate",
    "backbone_closure_recommended_next_phase",
    "asset_lane",
    "timeframe_lane",
    "source_backbone_closure_reference_placeholder",
    "fake_input_artifacts_required",
    "fake_output_artifacts_expected",
    "fake_pipeline_stage_sequence",
    "expected_trace_fields",
    "expected_operator_review_fields",
    "pass_criteria",
    "fail_criteria",
    "placeholder_only_guard",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "backbone_closure_report",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(SMOKE_TEST_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _closure_field(closure: Any, key: str) -> str:
    """Read a string field from a possibly-malformed closure report; safe."""
    return _as_text(closure.get(key)) if isinstance(closure, dict) else ""


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
        safe.get("schema_version") == SMOKE_TEST_CONTRACT_SCHEMA_VERSION
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
    inputs = tuple(safe.get("fake_input_artifacts_required") or ())
    outputs = tuple(safe.get("fake_output_artifacts_expected") or ())
    stages = tuple(safe.get("fake_pipeline_stage_sequence") or ())
    passes = tuple(safe.get("pass_criteria") or ())
    fails = tuple(safe.get("fail_criteria") or ())
    guard = safe.get("placeholder_only_guard")
    guard_ok = isinstance(guard, dict) and guard.get("guard_holds") is True
    fields_ok = (
        len(inputs) >= 1
        and len(outputs) >= 1
        and len(stages) >= 1
        and len(passes) >= 1
        and len(fails) >= 1
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
        "artifacts_and_criteria_present": fields_ok,
        "missing_required_fields": missing,
    }


def validate_fake_artifact_smoke_test_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake-artifact smoke test contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_fake_artifact_smoke_test_contract(closure: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only Strategy Factory fake-artifact
    smoke test contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The contract becomes active
    (fake_artifact_smoke_test_contract_active=True) solely when the upstream
    Bundle 28 backbone closure report is active AND its
    final_backbone_status is STRATEGY_FACTORY_V1_BACKBONE_COMPLETE AND its
    next_gate is PAUSE_AND_OPERATOR_REVIEW AND its recommended_next_phase is
    FAKE_ARTIFACT_SMOKE_TEST_PLANNING_ONLY. Even when active, every
    authorization field stays False -- it describes a future fake smoke test
    only, writes no runtime state, accesses no data, names only fake
    placeholders, and grants nothing. Returned dicts are fresh."""
    closure_active = (
        isinstance(closure, dict)
        and closure.get("backbone_closure_report_active") is True
    )
    final_status = _closure_field(closure, "final_backbone_status")
    closure_next_gate = _closure_field(closure, "next_gate")
    closure_phase = _closure_field(closure, "recommended_next_phase")
    contract_active = bool(
        closure_active
        and final_status == FINAL_BACKBONE_STATUS_COMPLETE
        and closure_next_gate == NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW
        and closure_phase == RECOMMENDED_NEXT_PHASE
    )
    state = (
        SMOKE_TEST_STATE_ACTIVE
        if contract_active
        else SMOKE_TEST_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_FAKE_ARTIFACT_DRY_WALK_CONTRACT_REQUIRED
        if contract_active
        else NEXT_GATE_AWAIT_BACKBONE_CLOSURE_OPERATOR_REVIEW
    )

    contract = {
        "schema_version": SMOKE_TEST_CONTRACT_SCHEMA_VERSION,
        "backbone_closure_report_schema_version": (
            BACKBONE_CLOSURE_REPORT_SCHEMA_VERSION
        ),
        "idea_id": _closure_field(closure, "idea_id"),
        "title": _closure_field(closure, "title"),
        "label": DEFAULT_SMOKE_TEST_CONTRACT_LABEL,
        "status": SMOKE_TEST_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_artifact_smoke_test_contract_active": contract_active,
        "fake_artifact_smoke_test_state": state,
        "backbone_closure_report_active": bool(closure_active),
        "backbone_closure_final_status": final_status,
        "backbone_closure_next_gate": closure_next_gate,
        "backbone_closure_recommended_next_phase": closure_phase,
        "asset_lane": _closure_field(closure, "asset_lane"),
        "timeframe_lane": _closure_field(closure, "timeframe_lane"),
        "source_backbone_closure_reference_placeholder": (
            _SOURCE_BACKBONE_CLOSURE_REFERENCE_PLACEHOLDER
        ),
        "fake_input_artifacts_required": FAKE_INPUT_ARTIFACTS_REQUIRED,
        "fake_output_artifacts_expected": FAKE_OUTPUT_ARTIFACTS_EXPECTED,
        "fake_pipeline_stage_sequence": FAKE_PIPELINE_STAGE_SEQUENCE,
        "expected_trace_fields": EXPECTED_TRACE_FIELDS,
        "expected_operator_review_fields": EXPECTED_OPERATOR_REVIEW_FIELDS,
        "pass_criteria": _PASS_CRITERIA,
        "fail_criteria": _FAIL_CRITERIA,
        "placeholder_only_guard": _placeholder_only_guard(
            FAKE_INPUT_ARTIFACTS_REQUIRED,
            FAKE_OUTPUT_ARTIFACTS_EXPECTED,
            FAKE_PIPELINE_STAGE_SEQUENCE,
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
        "backbone_closure_report": (
            closure if isinstance(closure, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_fake_artifact_smoke_test_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a fake-artifact smoke test
    contract template. Pure; writes no file. Informational only."""
    inputs = contract.get("fake_input_artifacts_required") or ()
    outputs = contract.get("fake_output_artifacts_expected") or ()
    stages = contract.get("fake_pipeline_stage_sequence") or ()
    trace = contract.get("expected_trace_fields") or ()
    review = contract.get("expected_operator_review_fields") or ()
    passes = contract.get("pass_criteria") or ()
    fails = contract.get("fail_criteria") or ()
    guard = contract.get("placeholder_only_guard") or {}
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Artifact Smoke Test Contract")
    lines.append("")
    lines.append(
        "Template only: this is a fake-artifact-smoke-test-contract-only, "
        "planning-only, placeholder-only template -- no-runtime-state-write, "
        "research-only, and execution-free. It is not wired into any runtime "
        "state, accesses no data, names only fake placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Closure schema: "
        f"`{contract.get('backbone_closure_report_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake artifact smoke test contract active: "
        f"{contract.get('fake_artifact_smoke_test_contract_active', '')}"
    )
    lines.append(
        f"Contract state: {contract.get('fake_artifact_smoke_test_state', '')}"
    )
    lines.append(
        "Backbone closure final status: "
        f"{contract.get('backbone_closure_final_status', '')}"
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
        "Source backbone closure reference: "
        f"{contract.get('source_backbone_closure_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Fake Input Artifacts Required")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Output Artifacts Expected")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Fake Pipeline Stage Sequence")
    lines.append("")
    for x in stages:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Trace Fields")
    lines.append("")
    for x in trace:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Expected Operator Review Fields")
    lines.append("")
    for x in review:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Pass Criteria")
    lines.append("")
    for x in passes:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Fail Criteria")
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
        "- A human must author and review the fake-artifact smoke test "
        "before any later phase is planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
