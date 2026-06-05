"""SPARTA Offline Strategy Factory - FAKE REPORT RENDERER IN-MEMORY.

Bundle 38 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *in-memory fake report renderer*: it consumes a Bundle 37 fake
report renderer contract and, only when that contract is active with next_gate
== FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED and the exact fake renderer scope,
constructs deterministic fake/sample/placeholder report content IN MEMORY ONLY
and returns it as dicts plus a rendered markdown string. It renders fake
placeholders only -- it writes no report file, is NOT a written report on disk,
NOT a live system, NOT a dry walk, NOT a pipeline, NOT an orchestrator.

It never runs Strategy Factory, never runs the fake pipeline, never runs the
smoke test, never runs a dry walk, never writes a report file, never writes
runtime state, never persists an approval, never writes a ledger file, never
updates dashboard files, never writes a registry file, never performs research,
never runs QA, never runs a baseline, never backtests, never simulates, never
fetches, inspects, loads, validates, transforms, or computes on real data, and
executes nothing beyond pure in-memory fake rendering. It opens no network,
spawns no subprocess, writes no file, reads no file, lists no directory,
touches no broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Every artifact it names is a FAKE placeholder. It references no Crypto-D1 real
data, no dataset file, no qa_report.json, no manifest.json, no CHECKSUMS.txt,
no FREEZE_RECORD.txt, no fees.json, no baseline output, and no real
market-data path. Those real names appear ONLY inside the explicit
REAL_ARTIFACT_GUARD_TOKENS guard list, which validation uses to REJECT any
content that smuggles a real artifact reference in.

Public API:
  - RENDERER_IN_MEMORY_SCHEMA_VERSION
  - DEFAULT_RENDERER_IN_MEMORY_LABEL
  - RENDERER_IN_MEMORY_STATUS
  - RENDERER_IN_MEMORY_SAFETY_POSTURE
  - RENDERER_IN_MEMORY_STATE_ACTIVE
  - RENDERER_IN_MEMORY_STATE_BLOCKED
  - NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED
  - NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT
  - REQUIRED_REPORT_SECTIONS
  - REAL_ARTIFACT_GUARD_TOKENS
  - build_fake_report_renderer_state(renderer_contract, fake_overrides=None)
  - validate_fake_report_renderer_state(state)
  - render_fake_report_markdown(state)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_fake_report_renderer_contract import (
    RENDERER_CONTRACT_SCHEMA_VERSION,
    RENDERER_CONTRACT_SAFETY_POSTURE,
    RENDERER_SCOPE,
    NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED,
)

__all__ = [
    "RENDERER_IN_MEMORY_SCHEMA_VERSION",
    "DEFAULT_RENDERER_IN_MEMORY_LABEL",
    "RENDERER_IN_MEMORY_STATUS",
    "RENDERER_IN_MEMORY_SAFETY_POSTURE",
    "RENDERER_IN_MEMORY_STATE_ACTIVE",
    "RENDERER_IN_MEMORY_STATE_BLOCKED",
    "NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED",
    "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT",
    "REQUIRED_REPORT_SECTIONS",
    "REAL_ARTIFACT_GUARD_TOKENS",
    "build_fake_report_renderer_state",
    "validate_fake_report_renderer_state",
    "render_fake_report_markdown",
]

RENDERER_IN_MEMORY_SCHEMA_VERSION = (
    "strategy_factory_fake_report_renderer_in_memory.v1"
)
DEFAULT_RENDERER_IN_MEMORY_LABEL = (
    "Strategy Factory Fake Report Renderer In Memory"
)
RENDERER_IN_MEMORY_STATUS = "READ_ONLY_FAKE_REPORT_RENDERER_IN_MEMORY"

RENDERER_IN_MEMORY_STATE_ACTIVE = "FAKE_REPORT_RENDERER_IN_MEMORY_ACTIVE"
RENDERER_IN_MEMORY_STATE_BLOCKED = "FAKE_REPORT_RENDERER_IN_MEMORY_BLOCKED"

NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED = (
    "FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED"
)
NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT = (
    "AWAIT_FAKE_REPORT_RENDERER_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-37).
RENDERER_IN_MEMORY_SAFETY_POSTURE: dict[str, bool] = dict(
    RENDERER_CONTRACT_SAFETY_POSTURE
)

REQUIRED_REPORT_SECTIONS: tuple[str, ...] = (
    "executive_summary",
    "fake_walk_scope",
    "fake_stage_walk_summary",
    "fake_trace_summary",
    "operator_review_summary",
    "pass_fail_summary",
    "safety_attestation",
    "blocked_capabilities",
    "next_steps",
)

# Real artifact references the fake renderer must NEVER emit. Validation
# REJECTS any content that contains one of these tokens. These literals exist
# ONLY here, as a guard -- the renderer's own fake content contains none.
REAL_ARTIFACT_GUARD_TOKENS: tuple[str, ...] = (
    "Crypto-D1",
    "qa_report.json",
    "manifest.json",
    "CHECKSUMS.txt",
    "FREEZE_RECORD.txt",
    "fees.json",
    "baseline_output",
    "real_dataset_name",
    ".csv",
    ".parquet",
    "/data/",
    "real_market_data_path",
)

_PLACEHOLDER_ONLY_GUARD = (
    "Every section and field rendered here is a fake placeholder only. This "
    "renderer is in-memory only and names no real artifact."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a fake in-memory report renderer and is execution-free.",
    "It renders fake placeholder content in memory only and writes no report "
    "file.",
    "It writes no runtime state and is research-only.",
    "Every section and field it names is a fake placeholder, never real "
    "output.",
    "It accesses no data and names only fake placeholders.",
    "A human must review the fake rendered output before any later phase is "
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
    "result_review_execution",
    "report_file_write",
    "report_contract_execution",
    "report_render_execution",
    "report_operator_review_execution",
    "report_renderer_build_execution",
    "report_renderer_implementation_execution",
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

_SOURCE_RENDERER_CONTRACT_REFERENCE_PLACEHOLDER = (
    "Strategy Factory Fake Report Renderer contract reference is a fake "
    "placeholder for a later human-reviewed fake report renderer result."
)

# Default fake placeholder report content -- pure, deterministic, fake only.
_DEFAULT_REPORT_SECTIONS: dict[str, str] = {
    "executive_summary": "Fake placeholder executive summary, no real result.",
    "fake_walk_scope": "Fake placeholder walk scope, no real coverage.",
    "fake_stage_walk_summary": (
        "Fake placeholder stage walk summary, no real stages."
    ),
    "fake_trace_summary": "Fake placeholder trace summary, no real traces.",
    "operator_review_summary": (
        "Fake placeholder operator review summary, no real decision."
    ),
    "pass_fail_summary": (
        "Fake placeholder pass and fail summary, no real outcome."
    ),
    "safety_attestation": (
        "Fake placeholder safety attestation, no real attestation."
    ),
    "blocked_capabilities": (
        "Fake placeholder blocked capabilities note, all stays blocked."
    ),
    "next_steps": "Fake placeholder next steps, human review only.",
}

_DEFAULT_FAKE_WALK_SUMMARY: dict[str, str] = {
    "fake_walk_id_placeholder": "fake-walk-placeholder-0001",
    "fake_walk_status_placeholder": "fake placeholder status",
    "fake_walk_note_placeholder": "Fake in-memory walk summary placeholder.",
}

_DEFAULT_FAKE_STAGE_SUMMARY: dict[str, str] = {
    "fake_stage_count_placeholder": "fake placeholder stage count",
    "fake_stage_note_placeholder": "Fake placeholder stage summary only.",
}

_DEFAULT_FAKE_TRACE_SUMMARY: dict[str, str] = {
    "fake_trace_count_placeholder": "fake placeholder trace count",
    "fake_trace_note_placeholder": "Fake placeholder trace summary only.",
}

_DEFAULT_FAKE_OPERATOR_REVIEW_SUMMARY: dict[str, str] = {
    "fake_operator_decision_placeholder": "fake placeholder operator decision",
    "fake_operator_note_placeholder": (
        "Fake placeholder operator review summary only."
    ),
}

_DEFAULT_FAKE_PASS_FAIL_SUMMARY: dict[str, str] = {
    "fake_pass_placeholder": "fake placeholder pass marker",
    "fake_fail_placeholder": "fake placeholder fail marker",
    "fake_pass_fail_note_placeholder": (
        "Fake placeholder pass and fail summary only."
    ),
}

_DEFAULT_FAKE_SAFETY_ATTESTATION: dict[str, str] = {
    "read_only_attestation_placeholder": (
        "Fake placeholder read-only attestation."
    ),
    "execution_free_attestation_placeholder": (
        "Fake placeholder execution-free attestation."
    ),
    "no_real_data_attestation_placeholder": (
        "Fake placeholder no-real-data attestation."
    ),
    "no_runtime_state_write_attestation_placeholder": (
        "Fake placeholder no-runtime-state-write attestation."
    ),
    "no_report_file_write_attestation_placeholder": (
        "Fake placeholder no-report-file-write attestation."
    ),
}

# Top-level fields required for a state to validate. "validation" is NOT
# required here -- requiring the state to embed its own validation result
# would be circular.
_REQUIRED_STATE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "fake_report_renderer_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "fake_report_renderer_active",
    "fake_report_renderer_state",
    "fake_report_renderer_contract_active",
    "fake_report_renderer_contract_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_renderer_contract_reference_placeholder",
    "report_sections",
    "fake_walk_summary",
    "fake_stage_summary",
    "fake_trace_summary",
    "fake_operator_review_summary",
    "fake_pass_fail_summary",
    "fake_safety_attestation",
    "rendered_markdown_preview",
    "placeholder_only_guard",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RENDERER_IN_MEMORY_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(contract: Any, key: str) -> str:
    """Read a string field from a possibly-malformed contract; safe."""
    return _as_text(contract.get(key)) if isinstance(contract, dict) else ""


def _merge_summary(
    default: dict[str, str], override: Any
) -> dict[str, str]:
    """Return a fresh default copy, with string-only overrides applied.

    Override values are copied verbatim (no token stripping) so that any real
    artifact reference smuggled in survives and is later REJECTED by
    validation. Non-string values are ignored."""
    out = dict(default)
    if isinstance(override, dict):
        for key, value in override.items():
            if isinstance(key, str) and isinstance(value, str):
                out[key] = value
    return out


def _gather_content_strings(state: dict[str, Any]) -> list[str]:
    """Collect every fake-content string in a state for guard scanning."""
    out: list[str] = []
    for key in (
        "report_sections",
        "fake_walk_summary",
        "fake_stage_summary",
        "fake_trace_summary",
        "fake_operator_review_summary",
        "fake_pass_fail_summary",
        "fake_safety_attestation",
    ):
        block = state.get(key)
        if isinstance(block, dict):
            for value in block.values():
                if isinstance(value, str):
                    out.append(value)
    preview = state.get("rendered_markdown_preview")
    if isinstance(preview, str):
        out.append(preview)
    return out


def _scan_real_artifacts(state: dict[str, Any]) -> tuple[str, ...]:
    """Return any real-artifact guard tokens found in the fake content."""
    strings = _gather_content_strings(state)
    hits = {
        token
        for value in strings
        for token in REAL_ARTIFACT_GUARD_TOKENS
        if token in value
    }
    return tuple(t for t in REAL_ARTIFACT_GUARD_TOKENS if t in hits)


def _validate(state: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a renderer state dict (no I/O)."""
    safe = state if isinstance(state, dict) else {}

    missing = tuple(f for f in _REQUIRED_STATE_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RENDERER_IN_MEMORY_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "FAKE_RENDER_ONLY",
        "FAKE_REPORT_RENDER_ONLY",
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    sections = safe.get("report_sections")
    sections_ok = isinstance(sections, dict) and all(
        s in sections for s in REQUIRED_REPORT_SECTIONS
    )

    preview_ok = isinstance(safe.get("rendered_markdown_preview"), str) and bool(
        safe.get("rendered_markdown_preview")
    )

    real_artifact_hits = _scan_real_artifacts(safe)
    no_real_artifacts = real_artifact_hits == ()

    valid = bool(
        schema_ok
        and research_only
        and stage_ok
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and sections_ok
        and preview_ok
        and no_real_artifacts
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
        "report_sections_ok": sections_ok,
        "rendered_markdown_preview_ok": preview_ok,
        "no_real_artifacts": no_real_artifacts,
        "real_artifact_hits": real_artifact_hits,
        "missing_required_fields": missing,
    }


def validate_fake_report_renderer_state(
    state: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a fake in-memory renderer state.
    Pure; no I/O. Flags any real artifact reference via real_artifact_hits."""
    return _validate(state)


def _render_markdown_from_parts(
    *,
    idea_id: str,
    title: str,
    active: bool,
    next_gate: str,
    report_sections: dict[str, str],
    fake_walk_summary: dict[str, str],
    fake_stage_summary: dict[str, str],
    fake_trace_summary: dict[str, str],
    fake_operator_review_summary: dict[str, str],
    fake_pass_fail_summary: dict[str, str],
    fake_safety_attestation: dict[str, str],
    blocked_capabilities: tuple[str, ...],
    operator_notes: tuple[str, ...],
    posture: dict[str, bool],
) -> str:
    """Pure deterministic markdown builder. Returns a string only."""
    summary_by_section = {
        "fake_walk_scope": fake_walk_summary,
        "fake_stage_walk_summary": fake_stage_summary,
        "fake_trace_summary": fake_trace_summary,
        "operator_review_summary": fake_operator_review_summary,
        "pass_fail_summary": fake_pass_fail_summary,
        "safety_attestation": fake_safety_attestation,
    }

    lines: list[str] = []
    lines.append("# Strategy Factory Fake Report (Fake In-Memory Render)")
    lines.append("")
    lines.append(
        "Fake in-memory render only: this is a "
        "fake-report-renderer-in-memory-only, placeholder-only, research-only, "
        "execution-free fake report -- no-report-file-write and "
        "no-runtime-state-write. It holds fake placeholder content in memory "
        "only, writes no report file, accesses no data, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Idea ID: {idea_id}")
    lines.append(f"Title: {title}")
    lines.append("Stage: FAKE_REPORT_RENDER_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Fake report renderer active: {active}")
    lines.append(f"Next gate: {next_gate}")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")

    for section in REQUIRED_REPORT_SECTIONS:
        title_text = section.replace("_", " ").title()
        lines.append(f"## {title_text}")
        lines.append("")
        lines.append(_as_text(report_sections.get(section)))
        lines.append("")
        if section in summary_by_section:
            for key, value in summary_by_section[section].items():
                lines.append(f"- `{key}`: {value}")
            lines.append("")
        elif section == "blocked_capabilities":
            for cap in blocked_capabilities:
                lines.append(f"- `{cap}`")
            lines.append("")
        elif section == "next_steps":
            lines.append(
                "- A human must review the fake rendered output before any "
                "later phase is planned."
            )
            lines.append(
                "- No automated step may proceed without human sign-off."
            )
            lines.append("")

    lines.append("## Operator Notes")
    lines.append("")
    for note in operator_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in posture.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines)


def render_fake_report_markdown(state: dict[str, Any]) -> str:
    """Return deterministic fake report markdown for a renderer state. Pure;
    writes no file; returns an in-memory string only."""
    safe = state if isinstance(state, dict) else {}

    def _d(key: str) -> dict:
        value = safe.get(key)
        return value if isinstance(value, dict) else {}

    blocked = safe.get("blocked_capabilities")
    notes = safe.get("operator_notes")
    return _render_markdown_from_parts(
        idea_id=_as_text(safe.get("idea_id")),
        title=_as_text(safe.get("title")),
        active=bool(safe.get("fake_report_renderer_active")),
        next_gate=_as_text(safe.get("next_gate")),
        report_sections=_d("report_sections"),
        fake_walk_summary=_d("fake_walk_summary"),
        fake_stage_summary=_d("fake_stage_summary"),
        fake_trace_summary=_d("fake_trace_summary"),
        fake_operator_review_summary=_d("fake_operator_review_summary"),
        fake_pass_fail_summary=_d("fake_pass_fail_summary"),
        fake_safety_attestation=_d("fake_safety_attestation"),
        blocked_capabilities=tuple(blocked) if isinstance(blocked, tuple)
        else tuple(blocked or ()),
        operator_notes=tuple(notes) if isinstance(notes, tuple)
        else tuple(notes or ()),
        posture=_d("safety_posture"),
    )


def build_fake_report_renderer_state(
    renderer_contract: Any,
    fake_overrides: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic in-memory fake report renderer state.

    Pure; no I/O, no mutation of inputs, no timestamp, no random id, no dynamic
    import. Unknown/malformed inputs never raise. The renderer becomes active
    (fake_report_renderer_active=True) solely when the upstream Bundle 37 fake
    report renderer contract is active AND its next_gate is
    FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED AND its renderer_scope matches
    the exact fake renderer scope. Even when active, every authorization field
    stays False -- it renders fake placeholder content in memory only, writes
    no report file, writes no runtime state, accesses no data, and grants
    nothing. ``fake_overrides`` may supply caller fake placeholder dict content;
    real artifact references are NOT stripped, they are flagged by validation.
    Returned dicts are fresh."""
    contract_active = (
        isinstance(renderer_contract, dict)
        and renderer_contract.get("fake_report_renderer_contract_active")
        is True
    )
    contract_next_gate = _field(renderer_contract, "next_gate")
    next_gate_ok = (
        contract_next_gate
        == NEXT_GATE_FAKE_REPORT_RENDERER_BUILD_REVIEW_REQUIRED
    )
    scope_ok = (
        isinstance(renderer_contract, dict)
        and tuple(renderer_contract.get("renderer_scope") or ())
        == RENDERER_SCOPE
    )
    renderer_active = bool(contract_active and next_gate_ok and scope_ok)

    state_label = (
        RENDERER_IN_MEMORY_STATE_ACTIVE
        if renderer_active
        else RENDERER_IN_MEMORY_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED
        if renderer_active
        else NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_CONTRACT
    )

    overrides = fake_overrides if isinstance(fake_overrides, dict) else {}
    report_sections = _merge_summary(
        _DEFAULT_REPORT_SECTIONS, overrides.get("report_sections"))
    fake_walk_summary = _merge_summary(
        _DEFAULT_FAKE_WALK_SUMMARY, overrides.get("fake_walk_summary"))
    fake_stage_summary = _merge_summary(
        _DEFAULT_FAKE_STAGE_SUMMARY, overrides.get("fake_stage_summary"))
    fake_trace_summary = _merge_summary(
        _DEFAULT_FAKE_TRACE_SUMMARY, overrides.get("fake_trace_summary"))
    fake_operator_review_summary = _merge_summary(
        _DEFAULT_FAKE_OPERATOR_REVIEW_SUMMARY,
        overrides.get("fake_operator_review_summary"))
    fake_pass_fail_summary = _merge_summary(
        _DEFAULT_FAKE_PASS_FAIL_SUMMARY,
        overrides.get("fake_pass_fail_summary"))
    fake_safety_attestation = _merge_summary(
        _DEFAULT_FAKE_SAFETY_ATTESTATION,
        overrides.get("fake_safety_attestation"))

    idea_id = _field(renderer_contract, "idea_id")
    title = _field(renderer_contract, "title")

    rendered_markdown_preview = _render_markdown_from_parts(
        idea_id=idea_id,
        title=title,
        active=renderer_active,
        next_gate=next_gate,
        report_sections=report_sections,
        fake_walk_summary=fake_walk_summary,
        fake_stage_summary=fake_stage_summary,
        fake_trace_summary=fake_trace_summary,
        fake_operator_review_summary=fake_operator_review_summary,
        fake_pass_fail_summary=fake_pass_fail_summary,
        fake_safety_attestation=fake_safety_attestation,
        blocked_capabilities=_BLOCKED_CAPABILITIES,
        operator_notes=_OPERATOR_NOTES,
        posture=_safety_posture(),
    )

    state = {
        "schema_version": RENDERER_IN_MEMORY_SCHEMA_VERSION,
        "fake_report_renderer_contract_schema_version": (
            RENDERER_CONTRACT_SCHEMA_VERSION
        ),
        "idea_id": idea_id,
        "title": title,
        "label": DEFAULT_RENDERER_IN_MEMORY_LABEL,
        "status": RENDERER_IN_MEMORY_STATUS,
        "stage": "FAKE_REPORT_RENDER_ONLY",
        "mode": "RESEARCH_ONLY",
        "fake_report_renderer_active": renderer_active,
        "fake_report_renderer_state": state_label,
        "fake_report_renderer_contract_active": bool(contract_active),
        "fake_report_renderer_contract_next_gate": contract_next_gate,
        "asset_lane": _field(renderer_contract, "asset_lane"),
        "timeframe_lane": _field(renderer_contract, "timeframe_lane"),
        "source_renderer_contract_reference_placeholder": (
            _SOURCE_RENDERER_CONTRACT_REFERENCE_PLACEHOLDER
        ),
        "report_sections": report_sections,
        "fake_walk_summary": fake_walk_summary,
        "fake_stage_summary": fake_stage_summary,
        "fake_trace_summary": fake_trace_summary,
        "fake_operator_review_summary": fake_operator_review_summary,
        "fake_pass_fail_summary": fake_pass_fail_summary,
        "fake_safety_attestation": fake_safety_attestation,
        "rendered_markdown_preview": rendered_markdown_preview,
        "placeholder_only_guard": _PLACEHOLDER_ONLY_GUARD,
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
    }
    state["validation"] = _validate(state)
    return state
