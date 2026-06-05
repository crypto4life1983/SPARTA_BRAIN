"""SPARTA Offline Strategy Factory - RESEARCH DECISION MEMO CONTRACT v1.

Bundle 16 of the Strategy Factory automation backbone. This module is a
PURE, stdlib-only *read-only research decision memo contract* builder: it
consumes Bundle 15 research report contracts and produces deterministic,
read-only decision memo contract templates. A decision memo contract defines
the SHAPE of the final, human-authored decision memo that follows a research
report -- which sections are required, which safety fields must be present,
and which memo decisions are allowed. It never makes a decision, never
inspects market data, fetches nothing, computes no backtest, and grants no
capability.

It is informational, read-only, and decision-memo-contract-only. It runs
nothing, computes no backtest, fetches no data, inspects no market data,
writes no file, opens no network, spawns no subprocess, touches no
broker/exchange/order/trading/live/upload/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, and reads no environment.

Public API:
  - RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION
  - DEFAULT_RESEARCH_DECISION_MEMO_CONTRACT_LABEL
  - RESEARCH_DECISION_MEMO_CONTRACT_STATUS
  - RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE
  - MEMO_DECISION_NEEDS_MORE_SPEC
  - MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT
  - MEMO_DECISION_PARK_RESEARCH_ONLY
  - MEMO_DECISION_REJECT_RESEARCH_ONLY
  - build_research_decision_memo_contract(item, *, human_research_approved=False)
  - build_research_decision_memo_contract_batch(items, *, label=None,
        human_research_approved_by_id=None)
  - validate_research_decision_memo_contract(contract)
  - render_research_decision_memo_contract_markdown(contract)
  - render_research_decision_memo_contract_batch_markdown(batch)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_research_queue import (
    RESEARCH_QUEUE_SCHEMA_VERSION,
    RESEARCH_QUEUE_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_reader import (
    QUEUE_READER_SCHEMA_VERSION,
    QUEUE_READER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_queue_planner import (
    QUEUE_PLANNER_SCHEMA_VERSION,
    QUEUE_PLANNER_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_task_packet import (
    RESEARCH_TASK_PACKET_SCHEMA_VERSION,
    RESEARCH_TASK_PACKET_SAFETY_POSTURE,
)
from sparta_commander.strategy_factory_research_report_contract import (
    RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION,
    RESEARCH_REPORT_CONTRACT_STATUS,
    RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE,
    REPORT_VERDICT_NEEDS_MORE_SPEC,
    REPORT_VERDICT_READY_FOR_PROTOCOL_DRAFT,
    REPORT_VERDICT_PARK_RESEARCH_ONLY,
    REPORT_VERDICT_REJECT_RESEARCH_ONLY,
    build_research_report_contract,
    build_research_report_contract_batch,
    validate_research_report_contract,
)

__all__ = [
    "RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_DECISION_MEMO_CONTRACT_LABEL",
    "RESEARCH_DECISION_MEMO_CONTRACT_STATUS",
    "RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE",
    "MEMO_DECISION_NEEDS_MORE_SPEC",
    "MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT",
    "MEMO_DECISION_PARK_RESEARCH_ONLY",
    "MEMO_DECISION_REJECT_RESEARCH_ONLY",
    "build_research_decision_memo_contract",
    "build_research_decision_memo_contract_batch",
    "validate_research_decision_memo_contract",
    "render_research_decision_memo_contract_markdown",
    "render_research_decision_memo_contract_batch_markdown",
]

RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION = (
    "strategy_factory_research_decision_memo_contract.v1"
)
DEFAULT_RESEARCH_DECISION_MEMO_CONTRACT_LABEL = (
    "Strategy Factory Research Decision Memo Contract"
)
RESEARCH_DECISION_MEMO_CONTRACT_STATUS = "READ_ONLY_DECISION_MEMO_CONTRACT"

MEMO_DECISION_NEEDS_MORE_SPEC = "NEEDS_MORE_SPEC"
MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT = "READY_FOR_PROTOCOL_DRAFT"
MEMO_DECISION_PARK_RESEARCH_ONLY = "PARK_RESEARCH_ONLY"
MEMO_DECISION_REJECT_RESEARCH_ONLY = "REJECT_RESEARCH_ONLY"

# Inherited all-false safety posture (same keys as Bundle 15). Pinned False:
# a decision memo contract only describes the memo shape; it grants nothing.
RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE: dict[str, bool] = dict(
    RESEARCH_REPORT_CONTRACT_SAFETY_POSTURE
)

# The exact, ordered set of decisions a future research-only memo may carry.
_ALLOWED_MEMO_DECISIONS: tuple[str, ...] = (
    MEMO_DECISION_NEEDS_MORE_SPEC,
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
    MEMO_DECISION_PARK_RESEARCH_ONLY,
    MEMO_DECISION_REJECT_RESEARCH_ONLY,
)

# Map a Bundle 15 report-contract next_gate to memo-contract gating.
_REPORT_GATE_NEXT_GATE: dict[str, str] = {
    "fix_research_queue_item": "fix_research_queue_item",
    "human_research_approval": "human_research_approval",
    "research_report_draft": "operator_decision_review",
}

# Deterministic, neutral memo sections a later memo must contain.
_REQUIRED_MEMO_SECTIONS: tuple[str, ...] = (
    "idea_summary",
    "research_report_reference",
    "hypothesis_review",
    "assumptions_review",
    "risk_review",
    "evidence_gap_review",
    "safety_gate_review",
    "memo_decision",
    "next_gate",
)

# Deterministic placeholders. None of these authorize any live capability.
_DECISION_REQUIREMENTS: tuple[str, ...] = (
    "Decision requirements are placeholders for a later human-authored memo.",
    "No market data is inspected by this contract.",
    "No historical simulation gate is opened by this contract.",
    "No broker or exchange surface is authorized by this contract.",
    "The memo decision cannot authorize execution.",
)

# Capabilities that stay blocked for every contract, regardless of status.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "data_fetch",
    "backtest",
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
# NOTE: "validation" is intentionally NOT required here -- the validation
# result describes the contract; requiring the contract to embed its own
# validation would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "report_contract_schema_version",
    "task_packet_schema_version",
    "planner_schema_version",
    "reader_schema_version",
    "research_queue_schema_version",
    "idea_id",
    "title",
    "stage",
    "mode",
    "status",
    "report_contract_allowed",
    "decision_memo_allowed",
    "allowed_memo_decisions",
    "default_memo_decision",
    "human_approval_required",
    "read_only",
    "executes",
    "safety",
    "report_contract",
    "required_memo_sections",
    "decision_requirements",
    "blocked_capabilities",
    "next_gate",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(RESEARCH_DECISION_MEMO_CONTRACT_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    plan_only = safe.get("stage") == "PLAN_ONLY"
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    safety = safe.get("safety")
    safety_all_false = (
        isinstance(safety, dict)
        and len(safety) > 0
        and all(v is False for v in safety.values())
    )
    decisions_ok = (
        tuple(safe.get("allowed_memo_decisions") or ())
        == _ALLOWED_MEMO_DECISIONS
    )
    sections = tuple(safe.get("required_memo_sections") or ())
    sections_ok = all(s in sections for s in _REQUIRED_MEMO_SECTIONS)

    valid = bool(
        schema_ok
        and research_only
        and plan_only
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and decisions_ok
        and sections_ok
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
        "allowed_memo_decisions_ok": decisions_ok,
        "required_sections_present": sections_ok,
        "missing_required_fields": missing,
    }


def validate_research_decision_memo_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a memo contract. Pure; no I/O."""
    return _validate(contract)


def build_research_decision_memo_contract(
    item: Any,
    *,
    human_research_approved: bool = False,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only research decision memo contract.

    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    items never raise. Even when decision_memo_allowed is True, every
    authorization field stays False -- a contract describes the memo shape,
    never grants permission or makes a decision. Returned dicts are fresh."""
    report_contract = build_research_report_contract(
        item, human_research_approved=human_research_approved
    )
    report_contract_allowed = bool(report_contract["report_contract_allowed"])
    decision_memo_allowed = report_contract_allowed
    next_gate = _REPORT_GATE_NEXT_GATE[report_contract["next_gate"]]

    contract = {
        "schema_version": RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
        "report_contract_schema_version": (
            RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
        ),
        "task_packet_schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "idea_id": _as_text(report_contract.get("idea_id")),
        "title": _as_text(report_contract.get("title")),
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "status": RESEARCH_DECISION_MEMO_CONTRACT_STATUS,
        "report_contract_allowed": report_contract_allowed,
        "decision_memo_allowed": decision_memo_allowed,
        "allowed_memo_decisions": _ALLOWED_MEMO_DECISIONS,
        "default_memo_decision": MEMO_DECISION_NEEDS_MORE_SPEC,
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
        "safety": _safety_posture(),
        "report_contract": report_contract,
        "required_memo_sections": _REQUIRED_MEMO_SECTIONS,
        "decision_requirements": _DECISION_REQUIREMENTS,
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "next_gate": next_gate,
    }
    contract["validation"] = _validate(contract)
    return contract


def build_research_decision_memo_contract_batch(
    items: tuple[Any, ...],
    *,
    label: str | None = None,
    human_research_approved_by_id: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Return a fresh deterministic batch of read-only memo contracts.

    Pure; no I/O, no mutation. All authorization counts stay 0; the batch is
    read-only and inert with an all-false safety posture. The
    human_research_approved_by_id map is read-only input only -- no approval
    is recorded anywhere. Consumes Bundle 15
    build_research_report_contract_batch for its read-only report snapshot."""
    name = (
        label if isinstance(label, str) and label
        else DEFAULT_RESEARCH_DECISION_MEMO_CONTRACT_LABEL
    )
    approvals = (
        human_research_approved_by_id
        if isinstance(human_research_approved_by_id, dict)
        else {}
    )
    item_tuple = tuple(items)

    contracts: list[dict[str, Any]] = []
    for it in item_tuple:
        idea_id = _as_text(it.get("idea_id")) if isinstance(it, dict) else ""
        approved = approvals.get(idea_id, False) is True
        contracts.append(
            build_research_decision_memo_contract(
                it, human_research_approved=approved
            )
        )
    contract_tuple = tuple(contracts)
    validations = tuple(c["validation"] for c in contract_tuple)

    allowed_count = sum(
        1 for c in contract_tuple if c["decision_memo_allowed"]
    )
    blocked_count = len(contract_tuple) - allowed_count
    valid_count = sum(1 for v in validations if v["valid"])
    invalid_count = len(validations) - valid_count

    report_contract_batch = build_research_report_contract_batch(
        item_tuple,
        label=name,
        human_research_approved_by_id=approvals,
    )

    return {
        "schema_version": RESEARCH_DECISION_MEMO_CONTRACT_SCHEMA_VERSION,
        "report_contract_schema_version": (
            RESEARCH_REPORT_CONTRACT_SCHEMA_VERSION
        ),
        "task_packet_schema_version": RESEARCH_TASK_PACKET_SCHEMA_VERSION,
        "planner_schema_version": QUEUE_PLANNER_SCHEMA_VERSION,
        "reader_schema_version": QUEUE_READER_SCHEMA_VERSION,
        "research_queue_schema_version": RESEARCH_QUEUE_SCHEMA_VERSION,
        "label": name,
        "status": RESEARCH_DECISION_MEMO_CONTRACT_STATUS,
        "stage": "PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "total_items": len(item_tuple),
        "decision_memo_allowed_count": allowed_count,
        "blocked_memo_count": blocked_count,
        "valid_contract_count": valid_count,
        "invalid_contract_count": invalid_count,
        "approved_for_research_count": 0,
        "execution_authorized_count": 0,
        "paper_trading_authorized_count": 0,
        "live_trading_authorized_count": 0,
        "data_fetch_authorized_count": 0,
        "backtest_authorized_count": 0,
        "promotion_authorized_count": 0,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "safety": _safety_posture(),
        "report_contract_batch": report_contract_batch,
        "memo_contracts": contract_tuple,
        "validation": validations,
        "next_gate": "research_decision_memo_review",
    }


def render_research_decision_memo_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for one memo contract.
    Pure; writes no file. Informational only."""
    safety = contract.get("safety") or {}
    sections = contract.get("required_memo_sections") or ()
    requirements = contract.get("decision_requirements") or ()
    decisions = contract.get("allowed_memo_decisions") or ()
    blocked = contract.get("blocked_capabilities") or ()
    report_contract = contract.get("report_contract") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Research Decision Memo Contract")
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Report contract schema: "
        f"`{contract.get('report_contract_schema_version', '')}`"
    )
    lines.append(
        "Task packet schema: "
        f"`{contract.get('task_packet_schema_version', '')}`"
    )
    lines.append(f"Planner schema: `{contract.get('planner_schema_version', '')}`")
    lines.append(f"Reader schema: `{contract.get('reader_schema_version', '')}`")
    lines.append(
        "Research queue schema: "
        f"`{contract.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append(
        f"Decision memo allowed: {contract.get('decision_memo_allowed', '')}"
    )
    lines.append(
        f"Default memo decision: {contract.get('default_memo_decision', '')}"
    )
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Required Memo Sections")
    lines.append("")
    for s in sections:
        lines.append(f"- `{s}`")
    lines.append("")
    lines.append("## Decision Requirements")
    lines.append("")
    for r in requirements:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Allowed Memo Decisions")
    lines.append("")
    for d in decisions:
        lines.append(f"- `{d}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Report Contract")
    lines.append("")
    lines.append(f"- `idea_id`: `{report_contract.get('idea_id', '')}`")
    lines.append(
        "- `report_contract_allowed`: "
        f"`{report_contract.get('report_contract_allowed', '')}`"
    )
    lines.append(f"- `read_only`: `{report_contract.get('read_only', '')}`")
    lines.append(f"- `executes`: `{report_contract.get('executes', '')}`")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for key, value in validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this memo contract and choose the next gate "
        "out of band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)


def render_research_decision_memo_contract_batch_markdown(
    batch: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a memo contract batch.
    Pure; writes no file. Informational only."""
    safety = batch.get("safety") or {}
    contracts = batch.get("memo_contracts") or ()
    report_contract_batch = batch.get("report_contract_batch") or {}
    validations = batch.get("validation") or ()

    lines: list[str] = []
    lines.append("# Strategy Factory Research Decision Memo Contract Batch")
    lines.append("")
    lines.append(f"Schema: `{batch.get('schema_version', '')}`")
    lines.append(
        "Report contract schema: "
        f"`{batch.get('report_contract_schema_version', '')}`"
    )
    lines.append(
        "Task packet schema: "
        f"`{batch.get('task_packet_schema_version', '')}`"
    )
    lines.append(f"Planner schema: `{batch.get('planner_schema_version', '')}`")
    lines.append(f"Reader schema: `{batch.get('reader_schema_version', '')}`")
    lines.append(
        "Research queue schema: "
        f"`{batch.get('research_queue_schema_version', '')}`"
    )
    lines.append(f"Label: {batch.get('label', '')}")
    lines.append(f"Status: {batch.get('status', '')}")
    lines.append("Stage: PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(f"Total items: {batch.get('total_items', 0)}")
    lines.append(
        "Decision memo allowed count: "
        f"{batch.get('decision_memo_allowed_count', 0)}"
    )
    lines.append(
        f"Blocked memo count: {batch.get('blocked_memo_count', 0)}"
    )
    lines.append(
        f"Valid contract count: {batch.get('valid_contract_count', 0)}"
    )
    lines.append(
        f"Invalid contract count: {batch.get('invalid_contract_count', 0)}"
    )
    lines.append("Execution authorized count: 0")
    lines.append("Backtest authorized count: 0")
    lines.append("Data fetch authorized count: 0")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Memo Contracts")
    lines.append("")
    if contracts:
        for c in contracts:
            lines.append(
                f"- `{c.get('idea_id', '')}` {c.get('title', '')} "
                f"(allowed=`{c.get('decision_memo_allowed', '')}`, "
                f"read_only=`{c.get('read_only', '')}`, "
                f"executes=`{c.get('executes', '')}`)"
            )
    else:
        lines.append("- (no items)")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Report Contract Batch")
    lines.append("")
    lines.append(
        f"- `total_items`: `{report_contract_batch.get('total_items', 0)}`"
    )
    lines.append(
        "- `report_contract_allowed_count`: "
        f"`{report_contract_batch.get('report_contract_allowed_count', 0)}`"
    )
    lines.append(
        f"- `read_only`: `{report_contract_batch.get('read_only', '')}`"
    )
    lines.append(
        f"- `executes`: `{report_contract_batch.get('executes', '')}`"
    )
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    valid_total = sum(1 for v in validations if v.get("valid"))
    lines.append(f"- `valid_contract_count`: `{valid_total}`")
    lines.append(f"- `total_validations`: `{len(validations)}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human must review this batch and choose the next gate out of "
        "band."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)
