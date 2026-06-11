"""SPARTA Strategy Idea Batch Approval Contract (READ-ONLY, BATCH SCHEMA ONLY).

Roadmap link L3 (build sequence seq 3) of the Strategy Factory Automation Roadmap:
the piece that collapses ~10 per-step approvals into ONE signature per chain --
without surrendering an inch of human control.

    idea -> intake -> adapter proposal -> UNSIGNED packet      [links built: L1, L2]
      -> THIS MODULE: a BATCH = packet + fully enumerated      [link L3]
         step chain, born unsigned
      -> a recorded human decision (APPROVE_BATCH_AS_ENUMERATED / DENY_BATCH)
      -> scheduled research-only runs (L4, future, separate block)

How a batch works:
  - compose_batch(packet, steps) binds a GENERATED (still unsigned) approval
    packet to an explicit, fully enumerated list of steps. Every step must be a
    member of the CLOSED step-kind catalog (research-only kinds: contracts,
    tests, in-memory dry runs, report-only persisted runs, reviews,
    registrations). Steps are numbered 1..N contiguously, capped at
    MAX_BATCH_STEPS. Anything outside the catalog -- or any step whose text
    smells of execution, credentials, or live trading -- refuses the whole batch.
  - record_human_batch_decision(batch, decision, signed_by) RECORDS (and only
    records) the human's verdict on a composed batch. Recording a decision
    starts no work: every step still runs through its own refuse-by-default
    runner, on a human-issued command, exactly as today.

The deviation rule (the heart of L3, validator-enforced):
  - ONE signature covers ONLY the enumerated steps, in the enumerated order.
  - ANY deviation -- a different step, a reordered step, an extra step, a changed
    scope -- VOIDS the batch. A voided/stopped batch can only be resumed by a
    fresh human approval. There is no such thing as an implied or extended grant.

What this module can never do (validator-enforced):
  - It cannot sign anything itself: composition always yields signed=False, and
    only an explicit human decision string plus a non-empty signed_by produces a
    decision record.
  - It cannot enumerate an execution step: the catalog has no such kind, and the
    forbidden-token screen refuses batches that try to smuggle one in.
  - It persists nothing, runs nothing, schedules nothing, unlocks nothing.

Public API:
  - BATCH_SCHEMA_VERSION / BATCH_LABEL / BATCH_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_BATCH_COMPOSED / VERDICT_BATCH_REFUSED
  - VERDICT_DECISION_RECORDED / VERDICT_DECISION_REFUSED
  - DECISION_APPROVE_BATCH / DECISION_DENY_BATCH / BATCH_DECISION_OPTIONS
  - ALLOWED_STEP_KINDS / FORBIDDEN_STEP_TOKENS / MAX_BATCH_STEPS
  - NEXT_REQUIRED_ACTION
  - get_strategy_idea_batch_approval_label()
  - compose_batch(packet, steps)
  - record_human_batch_decision(batch, decision, signed_by)
  - validate_batch(batch) / validate_batch_decision(record)
  - render_batch_markdown(batch)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.strategy_idea_approval_packet_schema_contract import (
    VERDICT_PACKET_GENERATED,
    validate_approval_packet,
)

BATCH_SCHEMA_VERSION = "strategy_idea_batch_approval_contract.v1"
BATCH_LABEL = (
    "SPARTA Strategy Idea Batch Approval (READ-ONLY, BATCH SCHEMA ONLY)"
)
BATCH_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L3_batch_approval_schema"
ROADMAP_SEQ = 3

VERDICT_BATCH_COMPOSED = "STRATEGY_IDEA_BATCH_COMPOSED"
VERDICT_BATCH_REFUSED = "STRATEGY_IDEA_BATCH_REFUSED"
VERDICT_DECISION_RECORDED = "BATCH_HUMAN_DECISION_RECORDED"
VERDICT_DECISION_REFUSED = "BATCH_HUMAN_DECISION_REFUSED"

DECISION_APPROVE_BATCH = "APPROVE_BATCH_AS_ENUMERATED"
DECISION_DENY_BATCH = "DENY_BATCH"
BATCH_DECISION_OPTIONS = (DECISION_APPROVE_BATCH, DECISION_DENY_BATCH)

# The roadmap's seq 4 block: the research cycle scheduler SPEC (a document).
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RESEARCH_CYCLE_SPEC"

# CLOSED catalog of research-only step kinds. There is no execution kind, no
# fetch kind, no credential kind -- they cannot be enumerated, so they cannot
# be batch-approved.
ALLOWED_STEP_KINDS = (
    "build_contract_module",
    "write_contract_tests",
    "run_contract_tests",
    "dry_run_in_memory",
    "persisted_research_run_report_only",
    "results_review_contract",
    "human_decision_contract",
    "mission_flow_registration",
)

# Step text screen: any of these tokens in a step kind or description refuses
# the whole batch, even if the kind looks legal.
FORBIDDEN_STEP_TOKENS = (
    "execute", "order", "credential", "api key", "broker", "exchange account",
    "live", "paper", "micro", "real money", "autotrade", "promote", "unlock",
)

MAX_BATCH_STEPS = 8


def get_strategy_idea_batch_approval_label() -> str:
    """Human label for the recognized batch approval contract."""
    return BATCH_LABEL


def _batch_id(packet: dict[str, Any], steps: list[dict[str, Any]]) -> str:
    """Stable batch id from the packet and the exact enumerated chain. Pure."""
    seed = str(packet.get("packet_id")) + "|" + "|".join(
        str(s.get("seq")) + ":" + str(s.get("kind")) + ":" + str(s.get("description"))
        for s in steps
    )
    return "batch_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _base_batch() -> dict[str, Any]:
    return {
        "schema_version": BATCH_SCHEMA_VERSION,
        "label": BATCH_LABEL,
        "mode": BATCH_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "verdict": None,
        "blockers": [],
        "batch_id": None,
        "covered_packet_id": None,
        "lane": None,
        "enumerated_steps": [],
        "step_count": 0,
        # The deviation rule, stated structurally:
        "one_signature_covers_only_the_enumerated_steps": True,
        "deviation_voids_batch": True,
        "resume_after_stop_requires_fresh_human_approval": True,
        "no_implied_or_extended_grants": True,
        # Born unsigned, always.
        "signed": False,
        "human_signature": None,
        "human_decision": None,
        "batch_is_a_request_not_an_authorization": True,
        "batch_is_in_memory_only": True,
        "composing_a_batch_starts_no_work": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "writes_ledger": False,
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
        # Gate posture (UNTOUCHED):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def _screen_step_text(step: dict[str, Any]) -> str | None:
    """Return the first forbidden token found in a step's text, else None."""
    text = (str(step.get("kind", "")) + " " + str(step.get("description", ""))).lower()
    for token in FORBIDDEN_STEP_TOKENS:
        if token in text:
            return token
    return None


def compose_batch(packet: Any, steps: Any) -> dict[str, Any]:
    """Bind a GENERATED, unsigned approval packet to a fully enumerated,
    research-only step chain. Refuses anything else. PURE: never raises,
    never signs, never persists, never runs anything."""
    batch = _base_batch()

    if not isinstance(packet, dict):
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("packet_missing_or_not_a_dict")
        return batch

    validation = validate_approval_packet(packet)
    if not validation.get("valid"):
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("packet_invalid")
        batch["blockers"].extend(
            "packet_error:" + str(e) for e in validation.get("errors") or []
        )
        return batch

    if packet.get("verdict") != VERDICT_PACKET_GENERATED:
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("no_generated_packet_to_batch")
        return batch

    if packet.get("signed") is not False:
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("packet_already_signed_or_tampered")
        return batch

    if not isinstance(steps, list) or not steps:
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("steps_missing_or_empty")
        return batch

    if len(steps) > MAX_BATCH_STEPS:
        batch["verdict"] = VERDICT_BATCH_REFUSED
        batch["blockers"].append("too_many_steps_for_one_signature")
        return batch

    cleaned: list[dict[str, Any]] = []
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            batch["verdict"] = VERDICT_BATCH_REFUSED
            batch["blockers"].append("step_not_a_dict_at_index_" + str(i))
            return batch
        if step.get("seq") != i + 1:
            batch["verdict"] = VERDICT_BATCH_REFUSED
            batch["blockers"].append("step_sequence_not_contiguous_at_index_" + str(i))
            return batch
        kind = step.get("kind")
        if kind not in ALLOWED_STEP_KINDS:
            batch["verdict"] = VERDICT_BATCH_REFUSED
            batch["blockers"].append("step_kind_not_in_closed_catalog:" + str(kind))
            return batch
        if not step.get("description"):
            batch["verdict"] = VERDICT_BATCH_REFUSED
            batch["blockers"].append("step_without_description_at_seq_" + str(i + 1))
            return batch
        token = _screen_step_text(step)
        if token is not None:
            batch["verdict"] = VERDICT_BATCH_REFUSED
            batch["blockers"].append("forbidden_step_token:" + token)
            return batch
        cleaned.append({
            "seq": i + 1,
            "kind": kind,
            "description": str(step.get("description")),
            "step_runs_via_its_own_refuse_by_default_runner": True,
        })

    batch["verdict"] = VERDICT_BATCH_COMPOSED
    batch["batch_id"] = _batch_id(packet, cleaned)
    batch["covered_packet_id"] = packet.get("packet_id")
    batch["lane"] = packet.get("lane")
    batch["enumerated_steps"] = cleaned
    batch["step_count"] = len(cleaned)
    return batch


def record_human_batch_decision(
    batch: Any, decision: Any, signed_by: Any
) -> dict[str, Any]:
    """RECORD (and only record) a human's verdict on a COMPOSED batch.
    Recording starts no work; every step still requires its own human-issued
    command through its own refuse-by-default runner. PURE: never raises."""
    record: dict[str, Any] = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "label": BATCH_LABEL,
        "mode": BATCH_MODE,
        "verdict": None,
        "blockers": [],
        "batch_id": None,
        "decision": None,
        "signed_by": None,
        "recording_a_decision_starts_no_work": True,
        "decision_covers_only_the_enumerated_steps": True,
        "deviation_voids_batch": True,
        "human_review_required": True,
        "executes": False,
        "writes_files": False,
        "starts_scheduler": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }

    if not isinstance(batch, dict):
        record["verdict"] = VERDICT_DECISION_REFUSED
        record["blockers"].append("batch_missing_or_not_a_dict")
        return record

    batch_validation = validate_batch(batch)
    if not batch_validation.get("valid"):
        record["verdict"] = VERDICT_DECISION_REFUSED
        record["blockers"].append("batch_invalid")
        return record

    if batch.get("verdict") != VERDICT_BATCH_COMPOSED:
        record["verdict"] = VERDICT_DECISION_REFUSED
        record["blockers"].append("no_composed_batch_to_decide_on")
        return record

    if decision not in BATCH_DECISION_OPTIONS:
        record["verdict"] = VERDICT_DECISION_REFUSED
        record["blockers"].append("decision_not_in_closed_options")
        return record

    if not isinstance(signed_by, str) or not signed_by.strip():
        record["verdict"] = VERDICT_DECISION_REFUSED
        record["blockers"].append("signature_missing_a_decision_needs_a_human_name")
        return record

    record["verdict"] = VERDICT_DECISION_RECORDED
    record["batch_id"] = batch.get("batch_id")
    record["decision"] = decision
    record["signed_by"] = signed_by.strip()
    return record


def validate_batch(batch: Any) -> dict[str, Any]:
    """Validate (read-only) a batch's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(batch, dict):
        return {"valid": False, "errors": ["batch_not_a_dict"]}
    b = batch

    verdict = b.get("verdict")
    if verdict not in (VERDICT_BATCH_COMPOSED, VERDICT_BATCH_REFUSED):
        errors.append("bad_verdict")

    steps = b.get("enumerated_steps")
    if verdict == VERDICT_BATCH_REFUSED:
        if steps:
            errors.append("refused_batch_carries_steps")
        if not b.get("blockers"):
            errors.append("refused_batch_without_blockers")
    if verdict == VERDICT_BATCH_COMPOSED:
        if b.get("blockers"):
            errors.append("composed_batch_carries_blockers")
        if not b.get("batch_id"):
            errors.append("composed_batch_without_id")
        if not b.get("covered_packet_id"):
            errors.append("composed_batch_without_packet")
        if not isinstance(steps, list) or not steps:
            errors.append("composed_batch_without_steps")
        else:
            if len(steps) > MAX_BATCH_STEPS:
                errors.append("composed_batch_too_long")
            if b.get("step_count") != len(steps):
                errors.append("step_count_mismatch")
            for i, step in enumerate(steps):
                if step.get("seq") != i + 1:
                    errors.append("steps_not_contiguous")
                    break
            for step in steps:
                if step.get("kind") not in ALLOWED_STEP_KINDS:
                    errors.append("step_kind_outside_catalog")
                    break
            for step in steps:
                if _screen_step_text(step) is not None:
                    errors.append("step_carries_forbidden_token")
                    break
            for step in steps:
                if step.get(
                    "step_runs_via_its_own_refuse_by_default_runner"
                ) is not True:
                    errors.append("step_bypasses_refuse_by_default_runner")
                    break

    # Deviation rule and unsigned-at-composition invariants.
    if b.get("one_signature_covers_only_the_enumerated_steps") is not True:
        errors.append("signature_scope_widened")
    if b.get("deviation_voids_batch") is not True:
        errors.append("deviation_rule_dropped")
    if b.get("resume_after_stop_requires_fresh_human_approval") is not True:
        errors.append("resume_rule_dropped")
    if b.get("no_implied_or_extended_grants") is not True:
        errors.append("implied_grants_allowed")
    if b.get("signed") is not False:
        errors.append("batch_claims_to_be_signed")
    if b.get("human_signature") is not None:
        errors.append("batch_carries_a_signature")
    if b.get("human_decision") is not None:
        errors.append("batch_carries_a_decision")
    if b.get("batch_is_a_request_not_an_authorization") is not True:
        errors.append("batch_claims_to_authorize")
    if b.get("batch_is_in_memory_only") is not True:
        errors.append("batch_not_in_memory_only")
    if b.get("composing_a_batch_starts_no_work") is not True:
        errors.append("batch_claims_to_start_work")
    if b.get("human_review_required") is not True:
        errors.append("human_review_dropped")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if b.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "writes_ledger",
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
        if b.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def validate_batch_decision(record: Any) -> dict[str, Any]:
    """Validate (read-only) a recorded batch decision. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record

    verdict = r.get("verdict")
    if verdict not in (VERDICT_DECISION_RECORDED, VERDICT_DECISION_REFUSED):
        errors.append("bad_verdict")

    if verdict == VERDICT_DECISION_RECORDED:
        if r.get("decision") not in BATCH_DECISION_OPTIONS:
            errors.append("decision_outside_closed_options")
        if not r.get("signed_by"):
            errors.append("recorded_decision_without_signer")
        if not r.get("batch_id"):
            errors.append("recorded_decision_without_batch")
    if verdict == VERDICT_DECISION_REFUSED:
        if not r.get("blockers"):
            errors.append("refused_decision_without_blockers")
        if r.get("decision") is not None:
            errors.append("refused_decision_carries_a_decision")

    if r.get("recording_a_decision_starts_no_work") is not True:
        errors.append("decision_claims_to_start_work")
    if r.get("decision_covers_only_the_enumerated_steps") is not True:
        errors.append("decision_scope_widened")
    if r.get("deviation_voids_batch") is not True:
        errors.append("deviation_rule_dropped")

    for key in ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked"):
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)
    for key in ("executes", "writes_files", "starts_scheduler",
                "promotes_gate", "unlocks_downstream_gate"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_batch_markdown(batch: Any) -> str:
    """Render a batch as deterministic markdown. Pure string work."""
    b = batch if isinstance(batch, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Strategy Idea Batch Approval (UNSIGNED REQUEST)")
    lines.append("")
    lines.append("- Verdict: " + str(b.get("verdict", "")))
    lines.append("- Batch id: " + str(b.get("batch_id")))
    lines.append("- Covers packet: " + str(b.get("covered_packet_id")))
    lines.append("- Lane: " + str(b.get("lane")))
    lines.append("- Signed: " + str(b.get("signed", "")))
    lines.append("- ONE signature covers ONLY the enumerated steps; any deviation "
                 "VOIDS the batch and stops the chain")
    lines.append("- Next required action: " + str(b.get("next_required_action", "")))
    lines.append("")
    blockers = b.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; nothing can be signed)")
        for x in blockers:
            lines.append("- " + str(x))
        lines.append("")
    steps = b.get("enumerated_steps") or []
    if steps:
        lines.append("## Enumerated steps (the ENTIRE grant, nothing else)")
        for s in steps:
            lines.append("- " + str(s.get("seq")) + ". [" + str(s.get("kind"))
                         + "] " + str(s.get("description")))
        lines.append("")
    lines.append("## Decision options")
    for d in BATCH_DECISION_OPTIONS:
        lines.append("- " + str(d))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
