"""SPARTA Offline Strategy Factory - RESEARCH PIPELINE CLOSURE REPORT v1.

Bundle 17 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only phase closure report* builder: it consumes Bundles
11-16 (the completed research-contract chain) and produces a deterministic,
read-only closure report that summarizes the finished chain and names the
next-phase gate. It performs no research, inspects no market data, fetches no
data, runs no historical simulation, and executes nothing.

It is informational, read-only, and closure-report-only. It runs nothing,
computes no historical simulation, fetches no data, inspects no market data,
writes no file, opens no network, spawns no subprocess, touches no
broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION
  - DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL
  - RESEARCH_PIPELINE_CLOSURE_STATUS
  - RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE
  - NEXT_PHASE_GATE_PAUSE_AND_REVIEW
  - NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY
  - NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY
  - build_research_pipeline_closure_report(*, label=None)
  - render_research_pipeline_closure_markdown(report)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_STATUS,
    RESEARCH_QUEUE_SAFETY_POSTURE,
    build_research_queue_item,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_STATUS,
    QUEUE_READER_SAFETY_POSTURE,
    build_queue_reader_summary,
)
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    QUEUE_PLANNER_STATUS,
    QUEUE_PLANNER_SAFETY_POSTURE,
    PLAN_DECISION_WAIT_FOR_HUMAN_APPROVAL,
    PLAN_DECISION_READY_FOR_RESEARCH_PLAN,
    PLAN_DECISION_INVALID_ITEM_NEEDS_FIX,
    build_queue_plan_summary,
)
from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    RESEARCH_TASK_PACKET_STATUS,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
    build_research_task_packet_batch,
)
from sparta_commander.strategy_factory_research_report_contract import (
    RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
    RESEARCH_REPORT_CONTRACT_STATUS,
    RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE,
    build_research_report_contract_batch,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
    RESEARCH_DECISION_MEMO_CONTRACT_STATUS,
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE,
    build_research_decision_memo_contract_batch,
)

__all__ = [
    "RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL",
    "RESEARCH_PIPELINE_CLOSURE_STATUS",
    "RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE",
    "NEXT_PHASE_GATE_PAUSE_AND_REVIEW",
    "NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY",
    "NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY",
    "build_research_pipeline_closure_report",
    "render_research_pipeline_closure_markdown",
]

RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION = (
    "strategy_factory_research_pipeline_closure.v1"
)
DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL = (
    "Strategy Factory Research Pipeline Closure Report"
)
RESEARCH_PIPELINE_CLOSURE_STATUS = "READ_ONLY_PHASE_CLOSURE"

NEXT_PHASE_GATE_PAUSE_AND_REVIEW = "PAUSE_AND_REVIEW"
NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY = "PROTOCOL_DRAFT_ONLY"
NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY = "DATA_CONTRACT_PLANNING_ONLY"

# Inherited all-false safety posture (same keys as Bundle 16). Pinned False:
# a closure report only summarizes a finished chain; it grants nothing.
RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE
)

# The exact, ordered set of next-phase gates an operator may choose.
_NEXT_PHASE_OPTIONS: tuple[str, ...] = (
    NEXT_PHASE_GATE_PAUSE_AND_REVIEW,
    NEXT_PHASE_GATE_PROTOCOL_DRAFT_ONLY,
    NEXT_PHASE_GATE_DATA_CONTRACT_PLANNING_ONLY,
)

# Ordered layer identifiers for Bundles 11-16.
_PIPELINE_SEQUENCE: tuple[str, ...] = (
    "research_queue",
    "queue_reader",
    "queue_planner",
    "research_task_packet",
    "research_report_contract",
    "research_decision_memo_contract",
)

# Authorization count keys present on every batch in the sample flow.
_AUTH_COUNT_KEYS: tuple[str, ...] = (
    "approved_for_research_count",
    "execution_authorized_count",
    "paper_trading_authorized_count",
    "live_trading_authorized_count",
    "data_fetch_authorized_count",
    "backtest_authorized_count",
    "promotion_authorized_count",
)

# Deterministic, neutral, verb-safe next-step guidance for the operator.
_RECOMMENDED_NEXT_STEPS: tuple[str, ...] = (
    "Review the completed research-contract chain.",
    "Choose the next phase explicitly.",
    "Keep data, simulation, broker, exchange, distribution, and autopilot "
    "gates closed until separately approved.",
    "Prefer protocol drafting before any data-contract or "
    "historical-simulation planning.",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_PIPELINE_CLOSURE_SAFETY_POSTURE)


def _all_false(posture: dict[str, bool]) -> bool:
    """True only when a posture dict is non-empty and every value is False."""
    return (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )


def _layer_check(layer: str, schema_version: str, status: str,
                 posture: dict[str, bool]) -> dict[str, Any]:
    """Return one deterministic read-only layer check record."""
    return {
        "layer": layer,
        "schema_version": schema_version,
        "status": status,
        "read_only": True,
        "executes": False,
        "safety_all_false": _all_false(posture),
    }


def _auth_counts_zero(*batches: dict[str, Any]) -> bool:
    """True only when every known authorization count is zero across batches."""
    for batch in batches:
        for key in _AUTH_COUNT_KEYS:
            if batch.get(key, 0) != 0:
                return False
    return True


def build_research_pipeline_closure_report(
    *,
    label: str | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only research pipeline closure report.

    Pure; no I/O, no mutation, no timestamp, no random id, no environment
    read. Builds one in-memory deterministic sample item only for shape
    validation -- it inspects no market data, fetches nothing, runs no
    historical simulation, and authorizes nothing. Returned dicts are fresh."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_RESEARCH_PIPELINE_CLOSURE_LABEL
    )

    sample_item = build_research_queue_item(
        "closure-sample",
        "Closure Sample Idea",
        "Deterministic in-memory sample thesis for shape validation only.",
        asset_lane="MNQ",
        timeframe="5m",
    )
    approvals = {"closure-sample": True}

    reader_summary = build_queue_reader_summary((sample_item,))
    planner_summary = build_queue_plan_summary((sample_item,))
    task_packet_batch = build_research_task_packet_batch(
        (sample_item,), human_research_approved_by_id=approvals)
    report_contract_batch = build_research_report_contract_batch(
        (sample_item,), human_research_approved_by_id=approvals)
    decision_memo_contract_batch = build_research_decision_memo_contract_batch(
        (sample_item,), human_research_approved_by_id=approvals)

    layer_checks = (
        _layer_check(
            "research_queue", RESEARCH_QUEUE_SCHEMA_VERSION,
            RESEARCH_QUEUE_STATUS, RESEARCH_QUEUE_SAFETY_POSTURE),
        _layer_check(
            "queue_reader", QUEUE_READER_SCHEMA_VERSION,
            QUEUE_READER_STATUS, QUEUE_READER_SAFETY_POSTURE),
        _layer_check(
            "queue_planner", QUEUE_PLANNER_SCHEMA_VERSION,
            QUEUE_PLANNER_STATUS, QUEUE_PLANNER_SAFETY_POSTURE),
        _layer_check(
            "research_task_packet", RESEARCH_TASK_PACKET_SCHEMA_VERSION,
            RESEARCH_TASK_PACKET_STATUS, RESEARCH_TASK_PACKET_SAFETY_POSTURE),
        _layer_check(
            "research_report_contract",
            RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
            RESEARCH_REPORT_CONTRACT_STATUS,
            RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE),
        _layer_check(
            "research_decision_memo_contract",
            RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
            RESEARCH_DECISION_MEMO_CONTRACT_STATUS,
            RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE),
    )

    safety = _safety_posture()
    auth_counts_zero = _auth_counts_zero(
        task_packet_batch, report_contract_batch, decision_memo_contract_batch)

    closure_checks = {
        "all_safety_flags_false": _all_false(safety),
        "all_authorization_counts_zero": auth_counts_zero,
        "read_only": True,
        "executes": False,
        "no_data_fetch": True,
        "no_backtest": True,
        "no_market_data_inspection": True,
        "no_broker_exchange_order": True,
        "no_upload_autopilot": True,
        "requires_operator_next_phase_decision": True,
    }

    return {
        "schema_version": RESEARCH_PIPELINE_CLOSURE_SCHEMA_VERSION,
        "label": name,
        "status": RESEARCH_PIPELINE_CLOSURE_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "phase_complete": True,
        "next_phase_gate": NEXT_PHASE_GATE_PAUSE_AND_REVIEW,
        "next_phase_options": _NEXT_PHASE_OPTIONS,
        "schema_versions": {
            "research_queue": RESEARCH_QUEUE_SCHEMA_VERSION,
            "queue_reader": QUEUE_READER_SCHEMA_VERSION,
            "queue_planner": QUEUE_PLANNER_SCHEMA_VERSION,
            "research_task_packet": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
            "research_report_contract": RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
            "research_decision_memo_contract": (
                RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION
            ),
        },
        "statuses": {
            "research_queue": RESEARCH_QUEUE_STATUS,
            "queue_reader": QUEUE_READER_STATUS,
            "queue_planner": QUEUE_PLANNER_STATUS,
            "research_task_packet": RESEARCH_TASK_PACKET_STATUS,
            "research_report_contract": RESEARCH_REPORT_CONTRACT_STATUS,
            "research_decision_memo_contract": (
                RESEARCH_DECISION_MEMO_CONTRACT_STATUS
            ),
        },
        "pipeline_sequence": _PIPELINE_SEQUENCE,
        "safety": safety,
        "layer_checks": layer_checks,
        "sample_flow": {
            "queue_item": sample_item,
            "reader_summary": reader_summary,
            "planner_summary": planner_summary,
            "task_packet_batch": task_packet_batch,
            "report_contract_batch": report_contract_batch,
            "decision_memo_contract_batch": decision_memo_contract_batch,
        },
        "closure_checks": closure_checks,
        "recommended_next_steps": _RECOMMENDED_NEXT_STEPS,
    }


def render_research_pipeline_closure_markdown(
    report: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a closure report.
    Pure; writes no file. Informational only."""
    sequence = report.get("pipeline_sequence") or ()
    schema_versions = report.get("schema_versions") or {}
    layer_checks = report.get("layer_checks") or ()
    closure_checks = report.get("closure_checks") or {}
    next_steps = report.get("recommended_next_steps") or ()
    safety = report.get("safety") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Pipeline Closure Report")
    lines.append("")
    lines.append(f"Schema: `{report.get('schema_version', '')}`")
    lines.append(f"Label: {report.get('label', '')}")
    lines.append(f"Status: {report.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append("Phase complete: True")
    lines.append(f"Next phase gate: {report.get('next_phase_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Pipeline Sequence")
    lines.append("")
    for layer in sequence:
        lines.append(f"- `{layer}`")
    lines.append("")
    lines.append("## Schema Versions")
    lines.append("")
    for key, value in schema_versions.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Layer Checks")
    lines.append("")
    for check in layer_checks:
        lines.append(
            f"- `{check.get('layer', '')}`: "
            f"status=`{check.get('status', '')}`, "
            f"read_only=`{check.get('read_only', '')}`, "
            f"executes=`{check.get('executes', '')}`, "
            f"safety_all_false=`{check.get('safety_all_false', '')}`"
        )
    lines.append("")
    lines.append("## Closure Checks")
    lines.append("")
    for key, value in closure_checks.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Recommended Next Steps")
    lines.append("")
    for step in next_steps:
        lines.append(f"- {step}")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines)
