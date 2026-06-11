"""SPARTA Intake-to-Orchestrator Adapter Contract (READ-ONLY, PROPOSAL ONLY).

Roadmap link L1 (build sequence seq 1) of the Strategy Factory Automation Roadmap:
the FIRST connecting piece between two already-built components.

    strategy_idea_intake_automation_contract  (YES / NO / MAYBE triage)
            |
            v   THIS ADAPTER (pure function, in-memory only)
    a PROPOSED run-queue entry shaped exactly like the real orchestrator
    queue schema (strategy_factory_queue_schema), status AWAITING_HUMAN_REVIEW
            |
            v   (future, separately approved blocks)
    approval packet generation (L2) -> batch approval (L3) -> scheduled runs (L4)

What the adapter does:
  - Takes a COMPLETED intake decision (the dict produced by
    intake_strategy_idea) and, ONLY when that decision is a validated YES,
    shapes an in-memory PROPOSED queue entry for the routed lane.
  - The proposed entry uses the orchestrator's own closed schema: phase is the
    first phase ('idea_intake'), status is 'AWAITING_HUMAN_REVIEW' (a member of
    the closed status enum and NOT one of the forbidden celebration statuses),
    and the suggested next command is copied VERBATIM from the intake decision --
    the adapter invents no commands of its own.

What the adapter can never do (validator-enforced):
  - It never enqueues: the proposal is IN-MEMORY ONLY; nothing is written to any
    queue file, ledger, or report. enqueued_by_adapter is False by construction.
  - NO and MAYBE decisions are REFUSED: no proposal object is created at all.
  - It runs nothing, fetches nothing, schedules nothing, connects to nothing,
    unlocks nothing, and promotes nothing. Every proposal still requires a human
    approval before it exists anywhere outside this function's return value.

Public API:
  - ADAPTER_SCHEMA_VERSION / ADAPTER_LABEL / ADAPTER_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_PROPOSAL_CREATED / VERDICT_PROPOSAL_REFUSED
  - NEXT_REQUIRED_ACTION
  - PROPOSAL_PHASE / PROPOSAL_STATUS / PROPOSAL_PRIORITY
  - get_intake_to_orchestrator_adapter_label()
  - adapt_intake_decision(intake_decision)
  - validate_adapter_record(record)
  - render_adapter_record_markdown(record)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.strategy_idea_intake_automation_contract import (
    ANSWER_MAYBE,
    ANSWER_NO,
    ANSWER_YES,
    KNOWN_LANES,
    validate_intake_decision,
)
from sparta_commander.strategy_factory_queue_schema import (
    FORBIDDEN_STATUS_VALUES,
    PHASES,
    QUEUE_SCHEMA_ID,
    QUEUE_STATUS,
    REQUIRED_ENTRY_FIELDS,
)

ADAPTER_SCHEMA_VERSION = "intake_to_orchestrator_adapter_contract.v1"
ADAPTER_LABEL = (
    "SPARTA Intake-to-Orchestrator Adapter (READ-ONLY, PROPOSAL ONLY)"
)
ADAPTER_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L1_intake_to_queue_adapter"
ROADMAP_SEQ = 1

VERDICT_PROPOSAL_CREATED = "INTAKE_PROPOSAL_CREATED"
VERDICT_PROPOSAL_REFUSED = "INTAKE_PROPOSAL_REFUSED"

# The roadmap's seq 2 block: the approval packet schema for strategy ideas.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_STRATEGY_IDEA_PACKET_SCHEMA"

# Queue alignment: first phase of the orchestrator chain, human-gated status.
PROPOSAL_PHASE = "idea_intake"
PROPOSAL_STATUS = "AWAITING_HUMAN_REVIEW"
PROPOSAL_PRIORITY = "normal"

# Hard alignment checks against the orchestrator's single source of truth.
# If the queue schema ever changes these, this module fails to import rather
# than silently shaping a proposal the orchestrator would reject.
assert PROPOSAL_PHASE in PHASES
assert PROPOSAL_STATUS in QUEUE_STATUS
assert PROPOSAL_STATUS not in FORBIDDEN_STATUS_VALUES


def get_intake_to_orchestrator_adapter_label() -> str:
    """Human label for the recognized intake-to-orchestrator adapter contract."""
    return ADAPTER_LABEL


def _deterministic_candidate_id(lane: str, decision: dict[str, Any]) -> str:
    """Stable id from the routed lane + the intake's matched keywords. Pure."""
    matched = ",".join(sorted(str(k) for k in decision.get("matched_keywords") or []))
    digest = hashlib.sha256((lane + "|" + matched).encode("utf-8")).hexdigest()[:12]
    return "idea_" + lane + "_" + digest


def _base_record() -> dict[str, Any]:
    return {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "label": ADAPTER_LABEL,
        "mode": ADAPTER_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "queue_schema_id": QUEUE_SCHEMA_ID,
        "verdict": None,
        "blockers": [],
        "proposed_queue_entry": None,
        "lane": None,
        "suggested_next_safe_command": None,
        "command_copied_verbatim_from_intake": True,
        "adapter_invents_no_commands": True,
        "proposal_is_in_memory_only": True,
        "enqueued_by_adapter": False,
        "human_gate": (
            "this proposal does not exist anywhere outside this return value; "
            "only a human-approved packet (roadmap seq 2) may persist or act on it"
        ),
        "human_review_required": True,
        # Capability posture (the adapter shapes a dict and nothing else):
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "runs_research": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED by this adapter):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def adapt_intake_decision(intake_decision: Any) -> dict[str, Any]:
    """Turn a validated intake YES decision into an in-memory PROPOSED queue
    entry; refuse everything else. PURE: never raises, never enqueues, never
    writes, never runs anything."""
    record = _base_record()

    if not isinstance(intake_decision, dict):
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("intake_decision_missing_or_not_a_dict")
        return record

    validation = validate_intake_decision(intake_decision)
    if not validation.get("valid"):
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("intake_decision_invalid")
        record["blockers"].extend(
            "intake_error:" + str(e) for e in validation.get("errors") or []
        )
        return record

    answer = intake_decision.get("answer")
    if answer == ANSWER_NO:
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("idea_was_rejected_by_intake_no_proposal_allowed")
        return record
    if answer == ANSWER_MAYBE:
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("idea_needs_human_clarification_before_any_proposal")
        return record
    if answer != ANSWER_YES:
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("unrecognized_intake_answer")
        return record

    lane = intake_decision.get("lane")
    if lane not in KNOWN_LANES:
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("yes_decision_without_a_known_lane")
        return record

    command = intake_decision.get("next_safe_command")
    if not command:
        record["verdict"] = VERDICT_PROPOSAL_REFUSED
        record["blockers"].append("yes_decision_without_a_suggested_command")
        return record

    candidate_id = _deterministic_candidate_id(lane, intake_decision)
    record["verdict"] = VERDICT_PROPOSAL_CREATED
    record["lane"] = lane
    record["suggested_next_safe_command"] = command
    record["proposed_queue_entry"] = {
        "run_id": "proposal_" + candidate_id,
        "candidate_id": candidate_id,
        "phase": PROPOSAL_PHASE,
        "status": PROPOSAL_STATUS,
        "priority": PROPOSAL_PRIORITY,
        "lane": lane,
        "intake_answer": ANSWER_YES,
        "intake_reasons": list(intake_decision.get("reasons") or []),
        "suggested_next_safe_command": command,
        "command_is_a_suggestion_only": True,
        "entry_is_a_proposal_not_a_queued_run": True,
    }
    return record


def validate_adapter_record(record: Any) -> dict[str, Any]:
    """Validate (read-only) an adapter record's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record

    verdict = r.get("verdict")
    if verdict not in (VERDICT_PROPOSAL_CREATED, VERDICT_PROPOSAL_REFUSED):
        errors.append("bad_verdict")

    entry = r.get("proposed_queue_entry")
    if verdict == VERDICT_PROPOSAL_REFUSED:
        if entry is not None:
            errors.append("refused_record_carries_a_proposal")
        if not r.get("blockers"):
            errors.append("refused_record_without_blockers")
    if verdict == VERDICT_PROPOSAL_CREATED:
        if r.get("blockers"):
            errors.append("created_record_carries_blockers")
        if not isinstance(entry, dict):
            errors.append("created_record_without_proposal")
        else:
            for field in REQUIRED_ENTRY_FIELDS:
                if not entry.get(field):
                    errors.append("proposal_missing_field:" + str(field))
            if entry.get("phase") != PROPOSAL_PHASE:
                errors.append("proposal_phase_not_idea_intake")
            if entry.get("status") != PROPOSAL_STATUS:
                errors.append("proposal_status_not_awaiting_human_review")
            if entry.get("status") in FORBIDDEN_STATUS_VALUES:
                errors.append("proposal_uses_forbidden_status")
            if entry.get("entry_is_a_proposal_not_a_queued_run") is not True:
                errors.append("proposal_claims_to_be_a_queued_run")
            if entry.get("command_is_a_suggestion_only") is not True:
                errors.append("proposal_command_not_marked_suggestion_only")
            if entry.get("suggested_next_safe_command") != r.get(
                "suggested_next_safe_command"
            ):
                errors.append("proposal_command_diverges_from_record")
        if r.get("lane") not in KNOWN_LANES:
            errors.append("created_record_without_known_lane")
        if not r.get("suggested_next_safe_command"):
            errors.append("created_record_without_command")

    if r.get("adapter_invents_no_commands") is not True:
        errors.append("adapter_claims_to_invent_commands")
    if r.get("command_copied_verbatim_from_intake") is not True:
        errors.append("command_not_copied_verbatim")
    if r.get("proposal_is_in_memory_only") is not True:
        errors.append("proposal_not_in_memory_only")
    if r.get("enqueued_by_adapter") is not False:
        errors.append("adapter_claims_to_have_enqueued")
    if r.get("human_review_required") is not True:
        errors.append("human_review_dropped")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "runs_research",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_adapter_record_markdown(record: Any) -> str:
    """Render an adapter record as deterministic markdown. Pure string work."""
    r = record if isinstance(record, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Intake-to-Orchestrator Adapter Record (PROPOSAL ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Roadmap link: " + str(r.get("roadmap_link_id", ""))
                 + " (seq " + str(r.get("roadmap_seq", "")) + ")")
    lines.append("- Lane: " + str(r.get("lane")))
    lines.append("- In-memory only: " + str(r.get("proposal_is_in_memory_only", "")))
    lines.append("- Enqueued by adapter: " + str(r.get("enqueued_by_adapter", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    blockers = r.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; nothing was proposed)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    entry = r.get("proposed_queue_entry")
    if isinstance(entry, dict):
        lines.append("## Proposed queue entry (awaiting human review)")
        lines.append("- run_id: " + str(entry.get("run_id")))
        lines.append("- candidate_id: " + str(entry.get("candidate_id")))
        lines.append("- phase: " + str(entry.get("phase")))
        lines.append("- status: " + str(entry.get("status")))
        lines.append("- priority: " + str(entry.get("priority")))
        lines.append("- suggested next safe command (verbatim from intake, "
                     "suggestion only, human must issue it): "
                     + str(entry.get("suggested_next_safe_command")))
        lines.append("")
    lines.append("## Human gate")
    lines.append("- " + str(r.get("human_gate", "")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
