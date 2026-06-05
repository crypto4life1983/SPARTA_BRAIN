"""SPARTA Offline Strategy Factory - RESEARCH RUNNER CONTRACT (TEMPLATE) v1.

Bundle 22 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only research runner contract template* builder: it consumes
a Bundle 21 data QA contract and, only when that contract is active with
next_gate == RESEARCH_RUNNER_CONTRACT_REQUIRED, produces a deterministic,
read-only *template* describing the shape a future human-authored research
runner OUTPUT must take. It defines a runner output contract template only --
NOT a runnable research runner.

It never runs research, never backtests, never simulates, never fetches,
inspects, loads, validates, transforms, or computes on real data, and executes
nothing. It opens no network, spawns no subprocess, writes no file, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RESEARCH_RUNNER_CONTRACT_LABEL
  - RESEARCH_RUNNER_CONTRACT_STATUS
  - RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE
  - RUNNER_STATE_ACTIVE
  - RUNNER_STATE_BLOCKED
  - NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED
  - NEXT_GATE_AWAIT_DATA_QA_CONTRACT
  - build_research_runner_contract(data_qa)
  - validate_research_runner_contract(contract)
  - render_research_runner_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_data_qa_contract import (
    DATA_QA_CONTRACT_SCHEMA_VERSION,
    DATA_QA_CONTRACT_SAFETY_POSTURE,
    NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED,
)

__all__ = [
    "RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_RUNNER_CONTRACT_LABEL",
    "RESEARCH_RUNNER_CONTRACT_STATUS",
    "RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE",
    "RUNNER_STATE_ACTIVE",
    "RUNNER_STATE_BLOCKED",
    "NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED",
    "NEXT_GATE_AWAIT_DATA_QA_CONTRACT",
    "build_research_runner_contract",
    "validate_research_runner_contract",
    "render_research_runner_contract_markdown",
]

RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_research_runner_contract.v1"
)
DEFAULT_RESEARCH_RUNNER_CONTRACT_LABEL = (
    "Strategy Factory Research Runner Contract"
)
RESEARCH_RUNNER_CONTRACT_STATUS = "READ_ONLY_RESEARCH_RUNNER_CONTRACT"

RUNNER_STATE_ACTIVE = "RESEARCH_RUNNER_CONTRACT_ACTIVE"
RUNNER_STATE_BLOCKED = "RESEARCH_RUNNER_CONTRACT_BLOCKED"

NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED = (
    "DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED"
)
NEXT_GATE_AWAIT_DATA_QA_CONTRACT = "AWAIT_DATA_QA_CONTRACT"

# Inherited all-false safety posture (same keys as Bundle 21). Pinned False:
# a runner contract template only describes a future output; it grants nothing.
RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    DATA_QA_CONTRACT_SAFETY_POSTURE
)

# Input NAMES a future runner must consume -- labels only, never data.
_REQUIRED_RUNNER_INPUTS: tuple[str, ...] = (
    "protocol_reference",
    "data_contract_reference",
    "data_qa_reference",
    "asset_lane",
    "timeframe_lane",
    "coverage_window_reference",
    "parameter_grid_placeholder",
)

# Output NAMES a future runner must produce -- labels only, never data.
_REQUIRED_RUNNER_OUTPUTS: tuple[str, ...] = (
    "summary_metrics",
    "equity_curve_series",
    "position_log",
    "per_period_returns",
    "drawdown_series",
    "run_manifest",
)

# Reproducibility field NAMES a future runner output must carry -- labels only.
_REQUIRED_REPRODUCIBILITY_FIELDS: tuple[str, ...] = (
    "config_hash_placeholder",
    "input_reference_set",
    "parameter_set",
    "environment_descriptor_placeholder",
    "seed_policy_placeholder",
    "output_manifest",
)

# Deterministic, verb-safe metric placeholders (descriptions only).
_REQUIRED_METRICS_PLACEHOLDERS: tuple[str, ...] = (
    "Metric definitions are placeholders for a later human-authored runner "
    "contract.",
    "No metric is computed on real data by this template.",
    "Net and gross return conventions must be specified out of band.",
)

# Deterministic, verb-safe risk placeholders (descriptions only).
_REQUIRED_RISK_PLACEHOLDERS: tuple[str, ...] = (
    "Risk metric definitions are placeholders for a later human-authored "
    "runner contract.",
    "Maximum drawdown and exposure conventions must be specified out of band.",
    "No risk value is computed on real data by this template.",
)

# Deterministic, verb-safe failure-mode descriptions.
_REQUIRED_FAILURE_MODES: tuple[str, ...] = (
    "Insufficient data coverage for the requested window.",
    "Ambiguous or unresolved symbol mapping.",
    "Parameter grid is empty or malformed.",
    "Reproducibility manifest is incomplete.",
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a template-only research runner contract and is execution-free.",
    "A human must author the real research runner out of band.",
    "No research is performed, no data is loaded, and nothing is computed by "
    "this template.",
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
    "data_qa_contract_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "runner_contract_active",
    "runner_state",
    "data_qa_active",
    "data_qa_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_protocol_reference_placeholder",
    "source_data_contract_reference_placeholder",
    "source_data_qa_reference_placeholder",
    "required_runner_inputs",
    "required_runner_outputs",
    "required_metrics_placeholders",
    "required_risk_placeholders",
    "required_failure_modes",
    "required_reproducibility_fields",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_approval_required",
    "read_only",
    "executes",
    "data_qa_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_RUNNER_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _qa_field(qa: Any, key: str) -> str:
    """Read a string field from a possibly-malformed QA contract; safe."""
    return _as_text(qa.get(key)) if isinstance(qa, dict) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION
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
    inputs = tuple(safe.get("required_runner_inputs") or ())
    outputs = tuple(safe.get("required_runner_outputs") or ())
    io_ok = len(inputs) >= 1 and len(outputs) >= 1

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and io_ok
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
        "required_runner_io_present": io_ok,
        "missing_required_fields": missing,
    }


def validate_research_runner_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a research runner contract template.
    Pure; no I/O."""
    return _validate(contract)


def build_research_runner_contract(data_qa: Any) -> dict[str, Any]:
    """Return a fresh deterministic read-only research runner contract template.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The template becomes active
    (runner_contract_active=True) solely when the upstream Bundle 21 data QA
    contract is active AND its next_gate is RESEARCH_RUNNER_CONTRACT_REQUIRED.
    Even when active, every authorization field stays False -- it defines a
    runner OUTPUT contract template only, runs no research, accesses no data,
    and grants nothing. Returned dicts are fresh."""
    data_qa_active = (
        isinstance(data_qa, dict) and data_qa.get("data_qa_active") is True
    )
    data_qa_next_gate = _qa_field(data_qa, "next_gate")
    runner_contract_active = bool(
        data_qa_active
        and data_qa_next_gate == NEXT_GATE_RESEARCH_RUNNER_CONTRACT_REQUIRED
    )
    state = (
        RUNNER_STATE_ACTIVE if runner_contract_active else RUNNER_STATE_BLOCKED
    )
    next_gate = (
        NEXT_GATE_DRY_RUN_ORCHESTRATOR_CONTRACT_REQUIRED
        if runner_contract_active
        else NEXT_GATE_AWAIT_DATA_QA_CONTRACT
    )

    contract = {
        "schema_version": RESEARCH_RUNNER_CONTRACT_SCHEMA_VERSION,
        "data_qa_contract_schema_version": DATA_QA_CONTRACT_SCHEMA_VERSION,
        "idea_id": _qa_field(data_qa, "idea_id"),
        "title": _qa_field(data_qa, "title"),
        "label": DEFAULT_RESEARCH_RUNNER_CONTRACT_LABEL,
        "status": RESEARCH_RUNNER_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "runner_contract_active": runner_contract_active,
        "runner_state": state,
        "data_qa_active": bool(data_qa_active),
        "data_qa_next_gate": data_qa_next_gate,
        "asset_lane": _qa_field(data_qa, "asset_lane"),
        "timeframe_lane": _qa_field(data_qa, "timeframe_lane"),
        "source_protocol_reference_placeholder": (
            "Source protocol reference is a placeholder for a later "
            "human-authored runner contract."
        ),
        "source_data_contract_reference_placeholder": (
            "Source data contract reference is a placeholder for a later "
            "human-authored runner contract."
        ),
        "source_data_qa_reference_placeholder": (
            "Source data QA reference is a placeholder for a later "
            "human-authored runner contract."
        ),
        "required_runner_inputs": _REQUIRED_RUNNER_INPUTS,
        "required_runner_outputs": _REQUIRED_RUNNER_OUTPUTS,
        "required_metrics_placeholders": _REQUIRED_METRICS_PLACEHOLDERS,
        "required_risk_placeholders": _REQUIRED_RISK_PLACEHOLDERS,
        "required_failure_modes": _REQUIRED_FAILURE_MODES,
        "required_reproducibility_fields": _REQUIRED_REPRODUCIBILITY_FIELDS,
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
        "data_qa_contract": data_qa if isinstance(data_qa, dict) else {},
    }
    contract["validation"] = _validate(contract)
    return contract


def render_research_runner_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a runner contract template.
    Pure; writes no file. Informational only."""
    inputs = contract.get("required_runner_inputs") or ()
    outputs = contract.get("required_runner_outputs") or ()
    metrics = contract.get("required_metrics_placeholders") or ()
    risks = contract.get("required_risk_placeholders") or ()
    failures = contract.get("required_failure_modes") or ()
    repro = contract.get("required_reproducibility_fields") or ()
    blocked = contract.get("blocked_capabilities") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Runner Contract")
    lines.append("")
    lines.append(
        "Template only: this is a research runner contract template -- "
        "runner-contract-only, research-only, and execution-free. It accesses "
        "no data and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Data QA schema: "
        f"`{contract.get('data_qa_contract_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        f"Runner contract active: {contract.get('runner_contract_active', '')}"
    )
    lines.append(f"Runner state: {contract.get('runner_state', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Required Runner Inputs")
    lines.append("")
    for x in inputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Runner Outputs")
    lines.append("")
    for x in outputs:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Metrics Placeholders")
    lines.append("")
    for x in metrics:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Required Risk Placeholders")
    lines.append("")
    for x in risks:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Required Failure Modes")
    lines.append("")
    for x in failures:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("## Required Reproducibility Fields")
    lines.append("")
    for x in repro:
        lines.append(f"- `{x}`")
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
        "- A human must author the real research runner before the next "
        "read-only orchestrator contract is opened."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
