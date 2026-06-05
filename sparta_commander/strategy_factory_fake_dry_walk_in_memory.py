"""SPARTA Offline Strategy Factory - FAKE DRY-WALK IN-MEMORY IMPLEMENTATION.

Bundle 33 of the Strategy Factory automation backbone. This module is the FIRST
fake-only, in-memory dry-walk implementation: it is PURE, stdlib-only, and
deterministic. It consumes a Bundle 32 fake dry-walk implementation contract
and, only when that contract is active with
next_gate == FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED and an
implementation_scope of exactly (fake_only, in_memory_only, deterministic,
no_real_data, no_runtime_write, no_execution_authority), walks a fixed sequence
of FAKE placeholder stages purely in memory and returns a deterministic state
dict (and markdown). It walks FAKE/sample/placeholder artifacts ONLY, in memory
ONLY, and returns deterministic dict/markdown outputs.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a real dry walk, never runs an orchestrator, never writes
runtime state, never persists an approval, never writes a ledger file, never
updates dashboard files, never writes a registry file, never performs research,
never runs QA, never runs a baseline, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing. It opens no network, spawns no subprocess, writes no file,
reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Every artifact it walks is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path.

Public API:
  - DRY_WALK_IN_MEMORY_SCHEMA_VERSION
  - DEFAULT_DRY_WALK_IN_MEMORY_LABEL
  - DRY_WALK_IN_MEMORY_STATUS
  - DRY_WALK_IN_MEMORY_SAFETY_POSTURE
  - WALK_STATE_ACTIVE
  - WALK_STATE_BLOCKED
  - NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
  - STAGE_SEQUENCE
  - PROHIBITED_REAL_ARTIFACT_REFERENCES
  - build_fake_dry_walk_state(implementation_contract)
  - validate_fake_dry_walk_state(state)
  - render_fake_dry_walk_markdown(state)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION,
    DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED,
    IMPLEMENTATION_SCOPE,
)
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    FORBIDDEN_REAL_ARTIFACT_TOKENS,
)

__all__ = [
    "DRY_WALK_IN_MEMORY_SCHEMA_VERSION",
    "DEFAULT_DRY_WALK_IN_MEMORY_LABEL",
    "DRY_WALK_IN_MEMORY_STATUS",
    "DRY_WALK_IN_MEMORY_SAFETY_POSTURE",
    "WALK_STATE_ACTIVE",
    "WALK_STATE_BLOCKED",
    "NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT",
    "STAGE_SEQUENCE",
    "PROHIBITED_REAL_ARTIFACT_REFERENCES",
    "build_fake_dry_walk_state",
    "validate_fake_dry_walk_state",
    "render_fake_dry_walk_markdown",
]

DRY_WALK_IN_MEMORY_SCHEMA_VERSION = (
    "strategy_factory_fake_dry_walk_in_memory.v1"
)
DEFAULT_DRY_WALK_IN_MEMORY_LABEL = (
    "Strategy Factory Fake Dry Walk In Memory"
)
DRY_WALK_IN_MEMORY_STATUS = "READ_ONLY_FAKE_DRY_WALK_IN_MEMORY"

WALK_STATE_ACTIVE = "FAKE_DRY_WALK_ACTIVE"
WALK_STATE_BLOCKED = "FAKE_DRY_WALK_BLOCKED"

NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED = (
    "FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT = (
    "AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT"
)

# The fixed fake stage order -- mirrors Bundle 29/30 backbone stage chain.
STAGE_SEQUENCE: tuple[str, ...] = (
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

# Inherited all-false safety posture (same 14 keys as Bundles 30-32). Pinned
# False: a fake in-memory walk grants nothing and is never wired into runtime.
DRY_WALK_IN_MEMORY_SAFETY_POSTURE: dict[str, bool] = dict(
    DRY_WALK_IMPLEMENTATION_CONTRACT_SAFETY_POSTURE
)

# Real artifact references a fake walk must never name.
PROHIBITED_REAL_ARTIFACT_REFERENCES: tuple[str, ...] = (
    "Crypto-D1",
    "qa_report.json",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees.json",
    "dataset_files",
    "baseline_outputs",
    ".csv",
    ".parquet",
    "/data/",
    "real_market_data_paths",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake dry walk in-memory implementation and is execution-free.",
    "It walks fake placeholder stages in memory only and writes no runtime "
    "state.",
    "Every stage input and output is a fake placeholder, never real output.",
    "It accesses no data and names only fake placeholders.",
    "A human must review the fake walk result before any later phase is "
    "planned.",
    "No automated step may proceed without human sign-off.",
)

# Capabilities that stay blocked for every state, regardless of activation.
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
    "smoke_test_execution",
    "dry_walk_execution",
    "operator_review_gate_execution",
    "dry_walk_implementation_execution",
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

_SOURCE_IMPLEMENTATION_CONTRACT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Dry Walk Implementation Contract reference is a "
    "fake placeholder for a later human-reviewed fake walk result."
)

# Required top-level fields for a state to validate. "validation" is NOT
# required -- requiring a state to embed its own validation result is circular.
_REQUIRED_STATE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_dry_walk_implementation_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_dry_walk_active",
    "fake_dry_walk_state",
    "fake_dry_walk_implementation_contract_active",
    "fake_dry_walk_implementation_contract_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_implementation_contract_reference_placeholder",
    "stage_sequence",
    "stage_records",
    "trace_records",
    "operator_review_packet",
    "pass_fail_summary",
    "placeholder_only_guard",
    "prohibited_real_artifact_references",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "fake_dry_walk_implementation_contract",
) + _AUTH_FLAGS

_STAGE_RECORD_KEYS = (
    "stage_name",
    "fake_input_placeholder",
    "fake_output_placeholder",
    "stage_status",
    "blocking_findings_placeholder",
)
_TRACE_RECORD_KEYS = (
    "trace_id_placeholder",
    "stage_name_placeholder",
    "input_digest_placeholder",
    "output_digest_placeholder",
    "stage_status_placeholder",
)
_OPERATOR_PACKET_KEYS = (
    "reviewer_identity_placeholder",
    "stage_assessment_placeholder",
    "blocking_findings_placeholder",
    "human_sign_off_placeholder",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DRY_WALK_IN_MEMORY_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(contract: Any, key: str) -> str:
    """Read a string field from a possibly-malformed contract; safe."""
    return (
        _as_text(contract.get(key)) if isinstance(contract, dict) else ""
    )


def _scan_strings(obj: Any) -> list[str]:
    """Collect every string in a nested dict/list/tuple structure. Pure."""
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            out.extend(_scan_strings(value))
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            out.extend(_scan_strings(value))
    return out


def _build_stage_records() -> tuple[dict[str, str], ...]:
    """Build one fake placeholder record per stage. Deterministic, fake-only."""
    records: list[dict[str, str]] = []
    for name in STAGE_SEQUENCE:
        records.append(
            {
                "stage_name": name,
                "fake_input_placeholder": f"fake_{name}_input_placeholder",
                "fake_output_placeholder": f"fake_{name}_output_placeholder",
                "stage_status": "FAKE_PASS_PLACEHOLDER",
                "blocking_findings_placeholder": "none_fake_placeholder",
            }
        )
    return tuple(records)


def _build_trace_records() -> tuple[dict[str, str], ...]:
    """Build one fake placeholder trace record per stage. Deterministic."""
    records: list[dict[str, str]] = []
    for index, name in enumerate(STAGE_SEQUENCE):
        records.append(
            {
                "trace_id_placeholder": f"fake_trace_{index}_placeholder",
                "stage_name_placeholder": name,
                "input_digest_placeholder": (
                    f"fake_input_digest_{index}_placeholder"
                ),
                "output_digest_placeholder": (
                    f"fake_output_digest_{index}_placeholder"
                ),
                "stage_status_placeholder": "FAKE_PASS_PLACEHOLDER",
            }
        )
    return tuple(records)


def _build_operator_review_packet() -> dict[str, str]:
    """Build a fake placeholder operator review packet. Deterministic."""
    return {
        "reviewer_identity_placeholder": "fake_reviewer_placeholder",
        "stage_assessment_placeholder": (
            "fake_all_stages_assessed_placeholder"
        ),
        "blocking_findings_placeholder": "none_fake_placeholder",
        "human_sign_off_placeholder": (
            "fake_pending_human_sign_off_placeholder"
        ),
    }


def _build_pass_fail_summary(
    stage_records: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    """Build a deterministic fake pass/fail summary over fake stage records."""
    total = len(stage_records)
    passed = sum(
        1
        for r in stage_records
        if r.get("stage_status") == "FAKE_PASS_PLACEHOLDER"
    )
    return {
        "total_stages": total,
        "fake_pass_count": passed,
        "fake_fail_count": total - passed,
        "all_fake_stages_passed_placeholder": bool(passed == total),
        "summary_status_placeholder": "FAKE_ALL_PASS_PLACEHOLDER",
    }


def _placeholder_only_guard(
    stage_records: Any,
    trace_records: Any,
    operator_packet: Any,
) -> dict[str, Any]:
    """Pure deterministic guard. Confirms every fake stage input/output is a
    placeholder and that no record names a forbidden real artifact token."""
    records = stage_records if isinstance(stage_records, (list, tuple)) else ()
    inputs_ok = all(
        isinstance(r, dict)
        and "placeholder" in _as_text(r.get("fake_input_placeholder")).lower()
        for r in records
    )
    outputs_ok = all(
        isinstance(r, dict)
        and "placeholder"
        in _as_text(r.get("fake_output_placeholder")).lower()
        for r in records
    )
    all_strings = (
        _scan_strings(stage_records)
        + _scan_strings(trace_records)
        + _scan_strings(operator_packet)
    )
    no_real = not any(
        tok in s.lower()
        for s in all_strings
        for tok in FORBIDDEN_REAL_ARTIFACT_TOKENS
    )
    return {
        "all_stage_inputs_placeholder_only": bool(inputs_ok),
        "all_stage_outputs_placeholder_only": bool(outputs_ok),
        "no_real_artifact_reference": bool(no_real),
        "forbidden_real_artifact_tokens": FORBIDDEN_REAL_ARTIFACT_TOKENS,
        "guard_holds": bool(inputs_ok and outputs_ok and no_real),
    }


def _stage_records_well_formed(stage_records: Any) -> bool:
    """True when stage records cover the stage sequence in order with keys."""
    if not isinstance(stage_records, (list, tuple)):
        return False
    if len(stage_records) != len(STAGE_SEQUENCE):
        return False
    for record, name in zip(stage_records, STAGE_SEQUENCE):
        if not isinstance(record, dict):
            return False
        if any(key not in record for key in _STAGE_RECORD_KEYS):
            return False
        if record.get("stage_name") != name:
            return False
    return True


def _trace_records_well_formed(trace_records: Any) -> bool:
    """True when trace records cover the stage sequence in order with keys."""
    if not isinstance(trace_records, (list, tuple)):
        return False
    if len(trace_records) != len(STAGE_SEQUENCE):
        return False
    for record, name in zip(trace_records, STAGE_SEQUENCE):
        if not isinstance(record, dict):
            return False
        if any(key not in record for key in _TRACE_RECORD_KEYS):
            return False
        if record.get("stage_name_placeholder") != name:
            return False
    return True


def _operator_packet_well_formed(packet: Any) -> bool:
    """True when the operator review packet carries every required key."""
    return isinstance(packet, dict) and all(
        key in packet for key in _OPERATOR_PACKET_KEYS
    )


def _validate(state: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a fake dry walk state (no I/O)."""
    safe = state if isinstance(state, dict) else {}

    missing = tuple(f for f in _REQUIRED_STATE_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DRY_WALK_IN_MEMORY_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in ("PLAN_ONLY", "FAKE_WALK_ONLY")
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    stage_sequence_ok = (
        tuple(safe.get("stage_sequence") or ()) == tuple(STAGE_SEQUENCE)
    )
    stage_records = safe.get("stage_records")
    trace_records = safe.get("trace_records")
    operator_packet = safe.get("operator_review_packet")
    stages_ok = _stage_records_well_formed(stage_records)
    traces_ok = _trace_records_well_formed(trace_records)
    packet_ok = _operator_packet_well_formed(operator_packet)

    guard = _placeholder_only_guard(
        stage_records, trace_records, operator_packet
    )
    guard_ok = guard.get("guard_holds") is True

    structure_ok = (
        stage_sequence_ok and stages_ok and traces_ok and packet_ok
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
        and structure_ok
        and guard_ok
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
        "stage_sequence_ok": stage_sequence_ok,
        "stage_records_well_formed": stages_ok,
        "trace_records_well_formed": traces_ok,
        "operator_review_packet_well_formed": packet_ok,
        "placeholder_only_guard_holds": guard_ok,
        "missing_required_fields": missing,
    }


def validate_fake_dry_walk_state(state: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic validation of a fake dry walk state. Pure; no I/O.

    Flags as invalid any state whose fake stage records, trace records, or
    operator packet name a real artifact token (Crypto-D1, qa_report.json,
    manifest.json, CHECKSUMS.txt, FREEZE_RECORD.txt, fees.json, baseline
    outputs, dataset names, .csv, .parquet, /data/, real market-data paths)."""
    return _validate(state)


def build_fake_dry_walk_state(
    implementation_contract: Any,
) -> dict[str, Any]:
    """Return a fresh deterministic fake-only, in-memory dry walk state.

    Pure; no I/O, no file read/write, no mutation of inputs, no timestamp, no
    random id, no dynamic import. Unknown/malformed inputs never raise. The
    walk becomes active (fake_dry_walk_active=True) solely when the upstream
    Bundle 32 implementation contract is active AND its next_gate is
    FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED AND its
    implementation_scope is exactly the six fake-only scope labels. Even when
    active, every authorization field stays False -- it walks only hardcoded
    fake placeholder stages in memory, writes no runtime state, accesses no
    data, names only fake placeholders, and grants nothing. Returned dicts are
    fresh."""
    contract_active = (
        isinstance(implementation_contract, dict)
        and implementation_contract.get(
            "fake_dry_walk_implementation_contract_active"
        )
        is True
    )
    contract_next_gate = _field(implementation_contract, "next_gate")
    scope = (
        tuple(implementation_contract.get("implementation_scope") or ())
        if isinstance(implementation_contract, dict)
        else ()
    )
    next_gate_ok = (
        contract_next_gate
        == NEXT_GATE_FAKE_DRY_WALK_IMPLEMENTATION_BUILD_REVIEW_REQUIRED
    )
    scope_ok = scope == tuple(IMPLEMENTATION_SCOPE)
    walk_active = bool(contract_active and next_gate_ok and scope_ok)

    walk_state = WALK_STATE_ACTIVE if walk_active else WALK_STATE_BLOCKED
    next_gate = (
        NEXT_GATE_FAKE_DRY_WALK_RESULT_REVIEW_REQUIRED
        if walk_active
        else NEXT_GATE_AWAIT_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
    )

    stage_records = _build_stage_records()
    trace_records = _build_trace_records()
    operator_packet = _build_operator_review_packet()
    pass_fail_summary = _build_pass_fail_summary(stage_records)
    guard = _placeholder_only_guard(
        stage_records, trace_records, operator_packet
    )

    state = {
        "schema_version": DRY_WALK_IN_MEMORY_SCHEMA_VERSION,
        "fake_dry_walk_implementation_contract_schema_version": (
            DRY_WALK_IMPLEMENTATION_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": _field(implementation_contract, "idea_id"),
        "title": _field(implementation_contract, "title"),
        "label": DEFAULT_DRY_WALK_IN_MEMORY_LABEL,
        "status": DRY_WALK_IN_MEMORY_STATUS,
        "stage": "FAKE_WALK_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_dry_walk_active": walk_active,
        "fake_dry_walk_state": walk_state,
        "fake_dry_walk_implementation_contract_active": bool(contract_active),
        "fake_dry_walk_implementation_contract_next_gate": contract_next_gate,
        "asset_lane": _field(implementation_contract, "asset_lane"),
        "timeframe_lane": _field(implementation_contract, "timeframe_lane"),
        "source_implementation_contract_reference_placeholder": (
            _SOURCE_IMPLEMENTATION_CONTRACT_REFERENCE_PLACEHOLDER
        ),
        "stage_sequence": STAGE_SEQUENCE,
        "stage_records": stage_records,
        "trace_records": trace_records,
        "operator_review_packet": operator_packet,
        "pass_fail_summary": pass_fail_summary,
        "placeholder_only_guard": guard,
        "prohibited_real_artifact_references": (
            PROHIBITED_REAL_ARTIFACT_REFERENCES
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
        "fake_dry_walk_implementation_contract": (
            implementation_contract
            if isinstance(implementation_contract, dict)
            else {}
        ),
    }
    state["validation"] = _validate(state)
    return state


def render_fake_dry_walk_markdown(state: dict[str, Any]) -> str:
    """Return deterministic, non-empty markdown for a fake dry walk state.
    Pure; writes no file. Informational only."""
    stage_records = state.get("stage_records") or ()
    trace_records = state.get("trace_records") or ()
    packet = state.get("operator_review_packet") or {}
    summary = state.get("pass_fail_summary") or {}
    guard = state.get("placeholder_only_guard") or {}
    prohibited_refs = state.get("prohibited_real_artifact_references") or ()
    notes = state.get("operator_notes") or ()
    posture = state.get("safety_posture") or {}
    validation = state.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Dry Walk In Memory")
    lines.append("")
    lines.append(
        "Walk summary: this is a fake-dry-walk-only, in-memory-only, "
        "placeholder-only fake walk -- no-runtime-state-write, research-only, "
        "and execution-free. It walks only fake placeholder stages in memory, "
        "is not wired into any runtime state, accesses no data, names only "
        "fake placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{state.get('schema_version', '')}`")
    lines.append(
        "Contract schema: "
        f"`{state.get('fake_dry_walk_implementation_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {state.get('idea_id', '')}")
    lines.append(f"Title: {state.get('title', '')}")
    lines.append(f"Status: {state.get('status', '')}")
    lines.append("Stage: FAKE_WALK_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Fake dry walk active: "
        f"{state.get('fake_dry_walk_active', '')}"
    )
    lines.append(
        "Walk state: "
        f"{state.get('fake_dry_walk_state', '')}"
    )
    lines.append(f"Next gate: {state.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {state.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {state.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source Reference")
    lines.append("")
    lines.append(
        "Source implementation contract reference: "
        f"{state.get('source_implementation_contract_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Stage Sequence")
    lines.append("")
    for name in state.get("stage_sequence") or ():
        lines.append(f"- `{name}`")
    lines.append("")
    lines.append("## Stage Records")
    lines.append("")
    for record in stage_records:
        lines.append(f"- `{record.get('stage_name', '')}`")
        for key in (
            "fake_input_placeholder",
            "fake_output_placeholder",
            "stage_status",
            "blocking_findings_placeholder",
        ):
            lines.append(f"  - `{key}`: `{record.get(key, '')}`")
    lines.append("")
    lines.append("## Trace Records")
    lines.append("")
    for record in trace_records:
        lines.append(f"- `{record.get('stage_name_placeholder', '')}`")
        for key in (
            "trace_id_placeholder",
            "input_digest_placeholder",
            "output_digest_placeholder",
            "stage_status_placeholder",
        ):
            lines.append(f"  - `{key}`: `{record.get(key, '')}`")
    lines.append("")
    lines.append("## Operator Review Packet")
    lines.append("")
    for key, value in packet.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Pass Fail Summary")
    lines.append("")
    for key, value in summary.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Placeholder Only Guard")
    lines.append("")
    for key, value in guard.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Prohibited Real Artifact References")
    lines.append("")
    for ref in prohibited_refs:
        lines.append(f"- `{ref}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in state.get("blocked_capabilities") or ():
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
        "- A human must review the fake walk result before any later phase is "
        "planned."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
