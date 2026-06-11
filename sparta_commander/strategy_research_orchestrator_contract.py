"""SPARTA Strategy Research Orchestrator Contract (READ-ONLY, PLAN ONLY).

The UMBRELLA over the completed, registered L1-L6 Strategy Factory Automation
Roadmap. One entry point, one pipeline, one rule: ideas from ANY source -- a
human typing one in, or a future automated scout that does not exist yet --
walk the SAME front door and the SAME chain, and stop at the SAME human
signature.

    idea (manual human OR future scout)
      -> L1 intake triage (YES / NO / MAYBE) + lane routing      [referenced]
      -> L1 adapter: in-memory proposal                          [referenced]
      -> L2 packet: unsigned, lane-aware, grants exactly one     [referenced]
      -> L3 batch: DRAFT enumerated research-only chain,         [referenced]
         composed but UNSIGNED -- the orchestrator can draft a
         batch; it can never sign one
      -> STOP: human signature required (the orchestrator's
         terminal state for every successful plan)
      -> L4 cycle rules / L5 report payloads / L6 display model  [referenced,
         future per-step usage under their own contracts]

This module DUPLICATES NOTHING: it imports and composes the real L1-L3
functions and references the L4-L6 rule constants by module name. If any link
tightens its rules, the orchestrator inherits the tightening automatically.

What the orchestrator can never do (validator-enforced):
  - It cannot sign, approve, run, schedule, fetch, send, or display anything
    real. Its only outputs are an in-memory PLAN and a recommendation string.
  - A hard-NO idea (execution, credentials, private data, hype, tainted
    windows) is refused at L1 and the refusal propagates -- there is no
    orchestrator path around the front door.
  - Scout-sourced ideas get NO shortcut: same pipeline, plus an extra
    mandatory human review flag, and the scout itself is NOT BUILT -- the
    source is accepted by the schema so the pipeline is ready, nothing more.
  - Auto-progression exists only IN THEORY under the L4 spec's eligible kinds;
    this module advances nothing and the FORBIDDEN_FOREVER list can never be
    weakened.

Public API:
  - ORCHESTRATOR_SCHEMA_VERSION / ORCHESTRATOR_LABEL / ORCHESTRATOR_MODE
  - VERDICT_ORCHESTRATION_PLANNED / VERDICT_ORCHESTRATION_REFUSED
  - VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION
  - ORCHESTRATOR_STATES / IDEA_SOURCES / HUMAN_ESCALATION_POINTS
  - FORBIDDEN_FOREVER / FUTURE_BLOCK_BOUNDARIES / CHAIN_LINK_REFERENCES
  - NEXT_REQUIRED_ACTION
  - get_strategy_research_orchestrator_label()
  - plan_orchestration(idea, source)
  - validate_orchestration_plan(plan)
  - render_orchestration_plan_markdown(plan)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_idea_intake_automation_contract import (
    ANSWER_MAYBE,
    ANSWER_NO,
    ANSWER_YES,
    intake_strategy_idea,
    validate_intake_decision,
)
from sparta_commander.intake_to_orchestrator_adapter_contract import (
    VERDICT_PROPOSAL_CREATED,
    adapt_intake_decision,
    validate_adapter_record,
)
from sparta_commander.strategy_idea_approval_packet_schema_contract import (
    VERDICT_PACKET_GENERATED,
    generate_approval_packet,
    validate_approval_packet,
)
from sparta_commander.strategy_idea_batch_approval_contract import (
    VERDICT_BATCH_COMPOSED,
    compose_batch,
    validate_batch,
)
from sparta_commander.research_cycle_scheduler_spec_contract import (
    AUTO_ADVANCE_ELIGIBLE_KINDS,
    HUMAN_STOP_KINDS,
    MAX_CYCLE_STEPS,
)

ORCHESTRATOR_SCHEMA_VERSION = "strategy_research_orchestrator_contract.v1"
ORCHESTRATOR_LABEL = (
    "SPARTA Strategy Research Orchestrator (READ-ONLY, PLAN ONLY, SIGNS NOTHING)"
)
ORCHESTRATOR_MODE = "RESEARCH_ONLY"

VERDICT_ORCHESTRATION_PLANNED = "ORCHESTRATION_PLANNED_AWAITING_HUMAN_SIGNATURE"
VERDICT_ORCHESTRATION_REFUSED = "ORCHESTRATION_REFUSED"
VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION = (
    "ORCHESTRATION_NEEDS_HUMAN_CLARIFICATION"
)

NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_DRAFTED_BATCH"

# CLOSED set of states the orchestrator can describe. Every successful plan
# terminates at the human signature; there is no state past it in this module.
ORCHESTRATOR_STATES = (
    "IDLE_AWAITING_IDEA",
    "TRIAGED",
    "PROPOSED",
    "PACKETED",
    "BATCH_DRAFTED_AWAITING_HUMAN_SIGNATURE",
    "NEEDS_HUMAN_CLARIFICATION",
    "REFUSED_STOPPED",
)

# CLOSED set of idea sources. Both walk the identical pipeline; the scout is
# NOT BUILT -- accepting the source string readies the pipeline, nothing more.
SOURCE_MANUAL = "manual_human_intake"
SOURCE_SCOUT = "future_automated_scout"
IDEA_SOURCES = (SOURCE_MANUAL, SOURCE_SCOUT)

# Every point where a human is mandatory, regardless of source or lane.
HUMAN_ESCALATION_POINTS = (
    "maybe_triage_needs_human_clarification",
    "batch_signature_one_human_signature_per_enumerated_chain",
    "every_cycle_review_stop_under_the_l4_rules",
    "every_report_and_display_is_read_before_any_next_command",
    "every_gate_decision_and_every_promotion_forever",
    "any_blocker_or_deviation_stops_the_chain_until_a_fresh_human_approval",
)

# Actions forbidden FOREVER -- not deferred, not gated: forbidden. Weakening
# this list is a validation error.
FORBIDDEN_FOREVER = (
    "placing_or_preparing_any_order",
    "holding_or_reading_broker_or_exchange_credentials",
    "spending_or_risking_real_money",
    "unlocking_any_trading_gate",
    "promoting_anything_without_a_human",
    "signing_or_approving_its_own_packets_or_batches",
    "extending_its_own_scope_beyond_the_signed_batch",
)

# The four future blocks, each OUTSIDE this contract and behind its own
# separate human approval.
FUTURE_BLOCK_BOUNDARIES = (
    {"block": "real_dashboard_jarvis_wiring",
     "boundary": "display models exist; wiring them into app.py/JARVIS is a "
                 "separate, human-approved runtime change"},
    {"block": "manual_start_notification_transport",
     "boundary": "report payloads exist; any send goes through the existing "
                 "hardened Telegram boundary, manual-start, separately approved"},
    {"block": "real_scheduler_build_under_l4_rules",
     "boundary": "only the L4 SPEC exists; building a scheduler that actually "
                 "runs is a separate, human-approved block"},
    {"block": "arbitrage_data_contract_roadmap_seq_2",
     "boundary": "the arbitrage lane's own next step, under its own lane "
                 "constitution and its own approval"},
)

# How L1-L6 are REFERENCED (module names), never duplicated.
CHAIN_LINK_REFERENCES = (
    {"link": "L1", "module": "sparta_commander.strategy_idea_intake_automation_contract"
                            " + sparta_commander.intake_to_orchestrator_adapter_contract",
     "used_for": "triage, lane routing, in-memory proposal"},
    {"link": "L2", "module": "sparta_commander.strategy_idea_approval_packet_schema_contract",
     "used_for": "unsigned lane-aware packet, grants exactly one command"},
    {"link": "L3", "module": "sparta_commander.strategy_idea_batch_approval_contract",
     "used_for": "draft enumerated batch; signature is human-only"},
    {"link": "L4", "module": "sparta_commander.research_cycle_scheduler_spec_contract",
     "used_for": "cycle rules: bounded, theory-only auto-advance, human stops"},
    {"link": "L5", "module": "sparta_commander.result_notification_reporting_contract",
     "used_for": "safe report payloads, nothing sent"},
    {"link": "L6", "module": "sparta_commander.dashboard_jarvis_sync_design_contract",
     "used_for": "display model, no controls, no runtime edit"},
)

# The standard research-only draft chain the orchestrator proposes per lane.
# Kinds come from the L3 closed catalog; descriptions are screened by L3.
_DRAFT_STEP_TEMPLATE = (
    ("build_contract_module", "build the lane's next research-only contract module"),
    ("write_contract_tests", "write the contract test file"),
    ("run_contract_tests", "run the new tests plus the commander safety suite"),
    ("dry_run_in_memory", "in-memory dry walk of the contract chain"),
    ("results_review_contract", "review contract over the dry-walk findings"),
)


def get_strategy_research_orchestrator_label() -> str:
    """Human label for the recognized strategy research orchestrator contract."""
    return ORCHESTRATOR_LABEL


def _draft_steps_for_lane(lane: str) -> list[dict[str, Any]]:
    """Draft the standard research-only step chain for a lane. Pure."""
    steps = []
    for i, (kind, description) in enumerate(_DRAFT_STEP_TEMPLATE):
        steps.append({
            "seq": i + 1,
            "kind": kind,
            "description": description + " (lane: " + str(lane) + ")",
        })
    return steps


def _base_plan(source: Any) -> dict[str, Any]:
    return {
        "schema_version": ORCHESTRATOR_SCHEMA_VERSION,
        "label": ORCHESTRATOR_LABEL,
        "mode": ORCHESTRATOR_MODE,
        "verdict": None,
        "final_state": None,
        "blockers": [],
        "source": source if source in IDEA_SOURCES else None,
        "scout_is_built": False,
        "scout_sourced_requires_extra_human_review": source == SOURCE_SCOUT,
        "lane": None,
        "orchestrator_states": list(ORCHESTRATOR_STATES),
        "chain_link_references": [dict(r) for r in CHAIN_LINK_REFERENCES],
        "human_escalation_points": list(HUMAN_ESCALATION_POINTS),
        "forbidden_forever": list(FORBIDDEN_FOREVER),
        "future_block_boundaries": [dict(b) for b in FUTURE_BLOCK_BOUNDARIES],
        # The walked chain (in-memory artifacts from the real L1-L3 modules):
        "intake_decision": None,
        "adapter_record": None,
        "approval_packet": None,
        "drafted_batch": None,
        "clarifications": [],
        # Progress record: in-memory trace only, never persisted by this module.
        "progress_record": [],
        "records_in_memory_only": True,
        # L4 rules referenced, not duplicated:
        "l4_auto_advance_eligible_kinds": list(AUTO_ADVANCE_ELIGIBLE_KINDS),
        "l4_human_stop_kinds": list(HUMAN_STOP_KINDS),
        "l4_max_cycle_steps": MAX_CYCLE_STEPS,
        "auto_progress_is_theory_only_nothing_advances_here": True,
        # Constitution, stated structurally:
        "orchestrator_signs_nothing": True,
        "orchestrator_approves_nothing": True,
        "same_pipeline_for_all_sources": True,
        "no_implied_approval_of_anything": True,
        "recommendation_is_suggestion_only": True,
        "plan_is_in_memory_only": True,
        "human_review_required": True,
        "next_safe_command_recommendation": None,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "writes_ledger": False,
        "writes_dashboard": False,
        "modifies_jarvis_runtime": False,
        "sends_notifications": False,
        "runs_research": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
        "advances_any_cycle": False,
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


def plan_orchestration(idea: Any, source: Any = SOURCE_MANUAL) -> dict[str, Any]:
    """Walk an idea through the real L1-L3 chain and stop at the human
    signature. PURE: never raises, never signs, never approves, never runs,
    never schedules, never persists anything."""
    plan = _base_plan(source)

    if source not in IDEA_SOURCES:
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("idea_source_not_in_closed_set:" + str(source))
        return plan

    # L1: triage at the one and only front door.
    decision = intake_strategy_idea(idea)
    plan["intake_decision"] = decision
    plan["progress_record"].append("L1_triage:" + str(decision.get("answer")))

    if not validate_intake_decision(decision).get("valid"):
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("intake_decision_invalid")
        return plan

    answer = decision.get("answer")
    if answer == ANSWER_NO:
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("idea_rejected_at_the_front_door")
        plan["blockers"].extend(str(r) for r in decision.get("reasons") or [])
        return plan
    if answer == ANSWER_MAYBE:
        plan["verdict"] = VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION
        plan["final_state"] = "NEEDS_HUMAN_CLARIFICATION"
        plan["clarifications"] = list(decision.get("clarifications") or [])
        plan["blockers"].append("idea_needs_human_clarification_before_any_plan")
        return plan
    if answer != ANSWER_YES:
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("unrecognized_triage_answer")
        return plan

    # L1 adapter: in-memory proposal.
    record = adapt_intake_decision(decision)
    plan["adapter_record"] = record
    plan["progress_record"].append("L1_adapter:" + str(record.get("verdict")))
    if (not validate_adapter_record(record).get("valid")
            or record.get("verdict") != VERDICT_PROPOSAL_CREATED):
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("adapter_refused_the_proposal")
        return plan

    # L2: unsigned lane-aware packet.
    packet = generate_approval_packet(record)
    plan["approval_packet"] = packet
    plan["progress_record"].append("L2_packet:" + str(packet.get("verdict")))
    if (not validate_approval_packet(packet).get("valid")
            or packet.get("verdict") != VERDICT_PACKET_GENERATED):
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("packet_generation_refused")
        return plan

    # L3: DRAFT batch (composed, unsigned -- signing is human-only, elsewhere).
    lane = packet.get("lane")
    batch = compose_batch(packet, _draft_steps_for_lane(lane))
    plan["drafted_batch"] = batch
    plan["progress_record"].append("L3_batch_draft:" + str(batch.get("verdict")))
    if (not validate_batch(batch).get("valid")
            or batch.get("verdict") != VERDICT_BATCH_COMPOSED):
        plan["verdict"] = VERDICT_ORCHESTRATION_REFUSED
        plan["final_state"] = "REFUSED_STOPPED"
        plan["blockers"].append("batch_draft_refused")
        return plan

    plan["verdict"] = VERDICT_ORCHESTRATION_PLANNED
    plan["final_state"] = "BATCH_DRAFTED_AWAITING_HUMAN_SIGNATURE"
    plan["lane"] = lane
    plan["progress_record"].append("STOP:human_signature_required")
    plan["next_safe_command_recommendation"] = (
        "HUMAN_DECIDES_ON_DRAFTED_BATCH " + str(batch.get("batch_id"))
        + " (record APPROVE_BATCH_AS_ENUMERATED or DENY_BATCH with your name; "
        "the drafted batch grants exactly: "
        + str(packet.get("approval_grants_exactly"))
        + ") -- recommendation only, this plan starts nothing"
    )
    return plan


def validate_orchestration_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) an orchestration plan's shape and safety
    invariants. Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan

    verdict = p.get("verdict")
    if verdict not in (VERDICT_ORCHESTRATION_PLANNED,
                       VERDICT_ORCHESTRATION_REFUSED,
                       VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION):
        errors.append("bad_verdict")
    if p.get("final_state") not in ORCHESTRATOR_STATES:
        errors.append("final_state_outside_closed_set")
    if tuple(p.get("orchestrator_states") or ()) != ORCHESTRATOR_STATES:
        errors.append("orchestrator_states_tampered")

    if verdict == VERDICT_ORCHESTRATION_REFUSED:
        if p.get("final_state") != "REFUSED_STOPPED":
            errors.append("refused_plan_with_wrong_state")
        if not p.get("blockers"):
            errors.append("refused_plan_without_blockers")
        if p.get("drafted_batch") is not None:
            errors.append("refused_plan_carries_a_batch")
        if p.get("next_safe_command_recommendation") is not None:
            errors.append("refused_plan_carries_a_recommendation")

    if verdict == VERDICT_ORCHESTRATION_NEEDS_CLARIFICATION:
        if p.get("final_state") != "NEEDS_HUMAN_CLARIFICATION":
            errors.append("clarification_plan_with_wrong_state")
        if not p.get("clarifications"):
            errors.append("clarification_plan_without_questions")
        if p.get("drafted_batch") is not None:
            errors.append("clarification_plan_carries_a_batch")

    if verdict == VERDICT_ORCHESTRATION_PLANNED:
        if p.get("final_state") != "BATCH_DRAFTED_AWAITING_HUMAN_SIGNATURE":
            errors.append("planned_plan_with_wrong_state")
        if p.get("blockers"):
            errors.append("planned_plan_carries_blockers")
        batch = p.get("drafted_batch")
        if not isinstance(batch, dict):
            errors.append("planned_plan_without_batch")
        else:
            if batch.get("signed") is not False:
                errors.append("drafted_batch_claims_signature")
            if not validate_batch(batch).get("valid"):
                errors.append("drafted_batch_invalid")
        packet = p.get("approval_packet")
        if not isinstance(packet, dict) or packet.get("signed") is not False:
            errors.append("packet_missing_or_signed")
        rec = p.get("next_safe_command_recommendation")
        if not rec or "recommendation only" not in str(rec):
            errors.append("recommendation_missing_or_not_marked")
        if not p.get("progress_record"):
            errors.append("planned_plan_without_progress_record")
        elif p["progress_record"][-1] != "STOP:human_signature_required":
            errors.append("plan_does_not_stop_at_human_signature")

    # The constitution can never be weakened.
    if tuple(p.get("forbidden_forever") or ()) != FORBIDDEN_FOREVER:
        errors.append("forbidden_forever_weakened")
    if tuple(p.get("human_escalation_points") or ()) != HUMAN_ESCALATION_POINTS:
        errors.append("escalation_points_tampered")
    if len(p.get("future_block_boundaries") or []) != 4:
        errors.append("future_block_boundaries_incomplete")
    if len(p.get("chain_link_references") or []) != 6:
        errors.append("chain_link_references_incomplete")
    if p.get("scout_is_built") is not False:
        errors.append("scout_claimed_built")
    if p.get("source") == SOURCE_SCOUT and p.get(
        "scout_sourced_requires_extra_human_review"
    ) is not True:
        errors.append("scout_extra_review_dropped")

    for key, err in (
        ("orchestrator_signs_nothing", "orchestrator_claims_to_sign"),
        ("orchestrator_approves_nothing", "orchestrator_claims_to_approve"),
        ("same_pipeline_for_all_sources", "scout_shortcut_allowed"),
        ("no_implied_approval_of_anything", "implied_approval_allowed"),
        ("recommendation_is_suggestion_only", "recommendation_not_suggestion_only"),
        ("auto_progress_is_theory_only_nothing_advances_here",
         "plan_claims_to_advance"),
        ("records_in_memory_only", "records_persisted"),
        ("plan_is_in_memory_only", "plan_not_in_memory_only"),
        ("human_review_required", "human_review_dropped"),
    ):
        if p.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "writes_ledger",
        "writes_dashboard",
        "modifies_jarvis_runtime",
        "sends_notifications",
        "runs_research",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
        "advances_any_cycle",
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
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_orchestration_plan_markdown(plan: Any) -> str:
    """Render an orchestration plan as deterministic markdown. Pure."""
    p = plan if isinstance(plan, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Strategy Research Orchestrator Plan (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- Final state: " + str(p.get("final_state")))
    lines.append("- Source: " + str(p.get("source"))
                 + (" (scout NOT built; extra human review required)"
                    if p.get("source") == SOURCE_SCOUT else ""))
    lines.append("- Lane: " + str(p.get("lane")))
    lines.append("- The orchestrator signs nothing and approves nothing")
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    blockers = p.get("blockers") or []
    if blockers:
        lines.append("## Blockers (stopped; a fresh human approval is required)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    clar = p.get("clarifications") or []
    if clar:
        lines.append("## Human clarification needed")
        for c in clar:
            lines.append("- " + str(c))
        lines.append("")
    progress = p.get("progress_record") or []
    if progress:
        lines.append("## Progress record (in-memory trace only)")
        for step in progress:
            lines.append("- " + str(step))
        lines.append("")
    if p.get("next_safe_command_recommendation"):
        lines.append("## Recommendation (suggestion only, human must act)")
        lines.append("- " + str(p.get("next_safe_command_recommendation")))
        lines.append("")
    lines.append("## Human escalation points (always)")
    for e in p.get("human_escalation_points") or []:
        lines.append("- " + str(e))
    lines.append("")
    lines.append("## Forbidden forever")
    for f in p.get("forbidden_forever") or []:
        lines.append("- " + str(f))
    lines.append("")
    lines.append("## Future blocks (each behind its own separate human approval)")
    for b in p.get("future_block_boundaries") or []:
        lines.append("- " + str(b.get("block")) + ": " + str(b.get("boundary")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
