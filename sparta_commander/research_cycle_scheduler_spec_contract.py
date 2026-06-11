"""SPARTA Research Cycle Scheduler SPEC Contract (READ-ONLY, SPEC ONLY).

Roadmap link L4 (build sequence seq 4) of the Strategy Factory Automation Roadmap --
delivered SPEC FIRST, exactly as the roadmap requires: this module defines the
RULEBOOK a future research-cycle scheduler must obey. It builds NO scheduler, NO
daemon, NO cron job, NO background worker, and NO loop that runs work. The scheduler
itself, if ever built, is a later block under its own human approval.

    idea -> intake -> adapter -> packet -> batch -> ONE human signature   [L1-L3, live]
      -> THIS MODULE: cycle SPEC derived from a SIGNED batch              [L4 spec]
      -> notification/reporting (L5) -> dashboard/JARVIS sync (L6)        [future]

What a research CYCLE is (per this spec): a bounded, one-pass, monotonic walk
through EXACTLY the steps a human signed in one batch -- never more, never again,
never reordered. Each batch step maps 1:1 to a cycle step. The spec marks which
steps could IN THEORY advance without a fresh human click (research-only mechanical
kinds) and which MUST stop for a human (reviews, decisions, registrations, and
always the end of the cycle). Even "auto-advance eligible" is THEORY ONLY here:
nothing in this module advances anything.

Hard rules (validator-enforced):
  - A cycle spec can only be derived from a COMPOSED, validated batch PLUS a
    RECORDED human decision of APPROVE_BATCH_AS_ENUMERATED whose batch_id matches.
    Unsigned, denied, refused, tampered, mismatched, or deviating inputs refuse.
  - No implied approval: the signature covers the enumerated steps only; the
    cycle is bounded by MAX_CYCLE_STEPS; each step occurs at most once; there are
    no retries and no loops without a fresh human approval.
  - The cycle's first step always requires a human activation; the cycle's last
    step always stops for human review. Stop semantics: any blocker, validator
    failure, or deviation moves the cycle (in theory) to VOIDED_BY_DEVIATION or
    STOPPED_FOR_HUMAN_REVIEW -- and only a fresh human approval resumes anything.
  - The spec's output is a NEXT-SAFE-COMMAND RECOMMENDATION ONLY. It executes
    nothing, schedules nothing, persists nothing, unlocks nothing.

Public API:
  - CYCLE_SPEC_SCHEMA_VERSION / CYCLE_SPEC_LABEL / CYCLE_SPEC_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_CYCLE_SPEC_READY / VERDICT_CYCLE_SPEC_REFUSED
  - SCHEDULER_STATES / AUTO_ADVANCE_ELIGIBLE_KINDS / HUMAN_STOP_KINDS
  - MAX_CYCLE_STEPS / NEXT_REQUIRED_ACTION
  - get_research_cycle_scheduler_spec_label()
  - build_research_cycle_spec(batch, decision_record)
  - validate_research_cycle_spec(spec)
  - render_research_cycle_spec_markdown(spec)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.strategy_idea_batch_approval_contract import (
    ALLOWED_STEP_KINDS,
    DECISION_APPROVE_BATCH,
    MAX_BATCH_STEPS,
    VERDICT_BATCH_COMPOSED,
    VERDICT_DECISION_RECORDED,
    validate_batch,
    validate_batch_decision,
)

CYCLE_SPEC_SCHEMA_VERSION = "research_cycle_scheduler_spec_contract.v1"
CYCLE_SPEC_LABEL = (
    "SPARTA Research Cycle Scheduler SPEC (READ-ONLY, SPEC ONLY, NO SCHEDULER BUILT)"
)
CYCLE_SPEC_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L4_scheduled_research_cycle_controller"
ROADMAP_SEQ = 4

VERDICT_CYCLE_SPEC_READY = "RESEARCH_CYCLE_SPEC_READY"
VERDICT_CYCLE_SPEC_REFUSED = "RESEARCH_CYCLE_SPEC_REFUSED"

# The roadmap's seq 5 block: the result notification/reporting design.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RESULT_REPORTING_DESIGN"

# CLOSED set of states a future scheduler may ever be in. There is no RUNNING
# state without a pending human grant behind it, and no state means "trading".
SCHEDULER_STATES = (
    "AWAITING_HUMAN_ACTIVATION",
    "CYCLE_STEP_PENDING",
    "CYCLE_STEP_DONE_REPORTED",
    "STOPPED_FOR_HUMAN_REVIEW",
    "VOIDED_BY_DEVIATION",
    "CYCLE_COMPLETE_AWAITING_HUMAN_REVIEW",
)

# Mechanical research-only kinds that could IN THEORY advance without a fresh
# human click once the batch signature exists. Theory only: nothing here runs.
AUTO_ADVANCE_ELIGIBLE_KINDS = (
    "run_contract_tests",
    "dry_run_in_memory",
    "persisted_research_run_report_only",
)

# Kinds that must ALWAYS stop the cycle for a human, signature or not.
HUMAN_STOP_KINDS = (
    "results_review_contract",
    "human_decision_contract",
    "mission_flow_registration",
)

# Bounded execution model: one pass, monotonic, hard cap, no retries, no loops.
MAX_CYCLE_STEPS = MAX_BATCH_STEPS

BOUNDED_EXECUTION_MODEL = (
    "one_pass_only_each_step_occurs_at_most_once",
    "monotonic_forward_order_no_reordering_no_skipping",
    "hard_cap_max_cycle_steps",
    "no_retries_without_a_fresh_human_approval",
    "no_loops_a_finished_or_stopped_cycle_never_restarts_itself",
    "any_blocker_or_deviation_voids_the_cycle_immediately",
)

REFUSAL_RULES = (
    "batch_missing_invalid_or_not_composed_refuses",
    "decision_missing_invalid_or_not_recorded_refuses",
    "decision_is_a_denial_refuses",
    "decision_batch_id_mismatch_refuses",
    "step_kind_outside_closed_catalog_refuses",
    "step_count_exceeding_hard_cap_refuses",
    "no_implied_approval_beyond_the_signed_batch_ever",
)


def get_research_cycle_scheduler_spec_label() -> str:
    """Human label for the recognized research cycle scheduler spec contract."""
    return CYCLE_SPEC_LABEL


def _cycle_id(batch: dict[str, Any]) -> str:
    """Stable cycle id derived from the signed batch it covers. Pure."""
    return "cycle_" + hashlib.sha256(
        str(batch.get("batch_id")).encode("utf-8")
    ).hexdigest()[:12]


def _base_spec() -> dict[str, Any]:
    return {
        "schema_version": CYCLE_SPEC_SCHEMA_VERSION,
        "label": CYCLE_SPEC_LABEL,
        "mode": CYCLE_SPEC_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "verdict": None,
        "blockers": [],
        "cycle_id": None,
        "covered_batch_id": None,
        "signed_by": None,
        "lane": None,
        "scheduler_states": list(SCHEDULER_STATES),
        "initial_state": "AWAITING_HUMAN_ACTIVATION",
        "cycle_steps": [],
        "step_count": 0,
        "bounded_execution_model": list(BOUNDED_EXECUTION_MODEL),
        "refusal_rules": list(REFUSAL_RULES),
        "max_cycle_steps": MAX_CYCLE_STEPS,
        # Constitution, stated structurally:
        "spec_only_no_scheduler_built": True,
        "scheduler_built_by_this_contract": False,
        "first_step_requires_human_activation": True,
        "final_step_always_stops_for_human_review": True,
        "no_implied_approval_beyond_signed_batch": True,
        "deviation_voids_cycle": True,
        "resume_requires_fresh_human_approval": True,
        "auto_advance_is_theory_only_nothing_advances_here": True,
        "output_is_a_recommendation_only": True,
        "next_safe_command_recommendation": None,
        "spec_is_in_memory_only": True,
        "human_review_required": True,
        # Capability posture (this module shapes a dict and nothing else):
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


def build_research_cycle_spec(batch: Any, decision_record: Any) -> dict[str, Any]:
    """Derive a research cycle SPEC from a composed batch plus a RECORDED human
    approval of that exact batch. Refuses everything else. PURE: never raises,
    never schedules, never advances, never persists, never runs anything."""
    spec = _base_spec()

    if not isinstance(batch, dict):
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("batch_missing_or_not_a_dict")
        return spec

    batch_validation = validate_batch(batch)
    if not batch_validation.get("valid"):
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("batch_invalid")
        spec["blockers"].extend(
            "batch_error:" + str(e) for e in batch_validation.get("errors") or []
        )
        return spec

    if batch.get("verdict") != VERDICT_BATCH_COMPOSED:
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("no_composed_batch_for_a_cycle")
        return spec

    if not isinstance(decision_record, dict):
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("human_decision_missing_or_not_a_dict")
        return spec

    decision_validation = validate_batch_decision(decision_record)
    if not decision_validation.get("valid"):
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("human_decision_invalid")
        return spec

    if decision_record.get("verdict") != VERDICT_DECISION_RECORDED:
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("human_decision_not_recorded")
        return spec

    if decision_record.get("decision") != DECISION_APPROVE_BATCH:
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("batch_was_denied_no_cycle_may_exist")
        return spec

    if decision_record.get("batch_id") != batch.get("batch_id"):
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("decision_covers_a_different_batch")
        return spec

    steps = batch.get("enumerated_steps") or []
    if len(steps) > MAX_CYCLE_STEPS:
        spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
        spec["blockers"].append("cycle_would_exceed_hard_cap")
        return spec

    cycle_steps: list[dict[str, Any]] = []
    last_index = len(steps) - 1
    for i, step in enumerate(steps):
        kind = step.get("kind")
        if kind not in ALLOWED_STEP_KINDS:
            spec["verdict"] = VERDICT_CYCLE_SPEC_REFUSED
            spec["blockers"].append("step_kind_outside_closed_catalog:" + str(kind))
            return spec
        is_first = i == 0
        is_last = i == last_index
        must_stop = kind in HUMAN_STOP_KINDS or is_last
        auto_eligible = (
            kind in AUTO_ADVANCE_ELIGIBLE_KINDS
            and not is_first
            and not must_stop
        )
        cycle_steps.append({
            "seq": step.get("seq"),
            "kind": kind,
            "description": step.get("description"),
            "auto_advance_eligible_in_theory": auto_eligible,
            "must_stop_for_human": must_stop or is_first,
            "stop_reason": (
                "first_step_requires_human_activation" if is_first
                else "final_step_always_stops_for_human_review" if is_last
                else "kind_always_requires_a_human" if kind in HUMAN_STOP_KINDS
                else None
            ),
            "runs_via_its_own_refuse_by_default_runner": True,
        })

    spec["verdict"] = VERDICT_CYCLE_SPEC_READY
    spec["cycle_id"] = _cycle_id(batch)
    spec["covered_batch_id"] = batch.get("batch_id")
    spec["signed_by"] = decision_record.get("signed_by")
    spec["lane"] = batch.get("lane")
    spec["cycle_steps"] = cycle_steps
    spec["step_count"] = len(cycle_steps)
    spec["next_safe_command_recommendation"] = (
        "HUMAN_ISSUES_STEP_1_COMMAND (" + str(cycle_steps[0].get("kind"))
        + ": " + str(cycle_steps[0].get("description"))
        + ") -- recommendation only, this spec starts nothing"
    )
    return spec


def validate_research_cycle_spec(spec: Any) -> dict[str, Any]:
    """Validate (read-only) a cycle spec's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec

    verdict = s.get("verdict")
    if verdict not in (VERDICT_CYCLE_SPEC_READY, VERDICT_CYCLE_SPEC_REFUSED):
        errors.append("bad_verdict")

    if tuple(s.get("scheduler_states") or ()) != SCHEDULER_STATES:
        errors.append("scheduler_states_tampered")
    if s.get("initial_state") != "AWAITING_HUMAN_ACTIVATION":
        errors.append("initial_state_not_human_activation")

    steps = s.get("cycle_steps")
    if verdict == VERDICT_CYCLE_SPEC_REFUSED:
        if steps:
            errors.append("refused_spec_carries_cycle_steps")
        if not s.get("blockers"):
            errors.append("refused_spec_without_blockers")
        if s.get("next_safe_command_recommendation") is not None:
            errors.append("refused_spec_carries_a_recommendation")

    if verdict == VERDICT_CYCLE_SPEC_READY:
        if s.get("blockers"):
            errors.append("ready_spec_carries_blockers")
        if not s.get("cycle_id"):
            errors.append("ready_spec_without_cycle_id")
        if not s.get("covered_batch_id"):
            errors.append("ready_spec_without_batch")
        if not s.get("signed_by"):
            errors.append("ready_spec_without_human_signer")
        if not isinstance(steps, list) or not steps:
            errors.append("ready_spec_without_steps")
        else:
            if len(steps) > MAX_CYCLE_STEPS:
                errors.append("cycle_exceeds_hard_cap")
            if s.get("step_count") != len(steps):
                errors.append("step_count_mismatch")
            if steps[0].get("must_stop_for_human") is not True:
                errors.append("first_step_does_not_require_human_activation")
            if steps[-1].get("must_stop_for_human") is not True:
                errors.append("final_step_does_not_stop_for_human")
            for st in steps:
                kind = st.get("kind")
                if kind not in ALLOWED_STEP_KINDS:
                    errors.append("cycle_step_kind_outside_catalog")
                    break
            for st in steps:
                if (st.get("auto_advance_eligible_in_theory")
                        and st.get("kind") not in AUTO_ADVANCE_ELIGIBLE_KINDS):
                    errors.append("auto_advance_granted_to_ineligible_kind")
                    break
            for st in steps:
                if (st.get("kind") in HUMAN_STOP_KINDS
                        and st.get("must_stop_for_human") is not True):
                    errors.append("human_stop_kind_does_not_stop")
                    break
            for st in steps:
                if st.get("runs_via_its_own_refuse_by_default_runner") is not True:
                    errors.append("step_bypasses_refuse_by_default_runner")
                    break
        rec = s.get("next_safe_command_recommendation")
        if not rec or "recommendation only" not in str(rec):
            errors.append("recommendation_missing_or_not_marked_recommendation_only")

    # Constitution invariants.
    for key, err in (
        ("spec_only_no_scheduler_built", "spec_claims_to_build_scheduler"),
        ("first_step_requires_human_activation", "human_activation_dropped"),
        ("final_step_always_stops_for_human_review", "final_stop_dropped"),
        ("no_implied_approval_beyond_signed_batch", "implied_approval_allowed"),
        ("deviation_voids_cycle", "deviation_rule_dropped"),
        ("resume_requires_fresh_human_approval", "resume_rule_dropped"),
        ("auto_advance_is_theory_only_nothing_advances_here", "spec_claims_to_advance"),
        ("output_is_a_recommendation_only", "output_not_recommendation_only"),
        ("spec_is_in_memory_only", "spec_not_in_memory_only"),
        ("human_review_required", "human_review_dropped"),
    ):
        if s.get(key) is not True:
            errors.append(err)
    if s.get("scheduler_built_by_this_contract") is not False:
        errors.append("scheduler_claimed_built")
    if s.get("max_cycle_steps") != MAX_CYCLE_STEPS:
        errors.append("hard_cap_tampered")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
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
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_research_cycle_spec_markdown(spec: Any) -> str:
    """Render a cycle spec as deterministic markdown. Pure string work."""
    s = spec if isinstance(spec, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Research Cycle Scheduler SPEC (SPEC ONLY, NO SCHEDULER BUILT)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Cycle id: " + str(s.get("cycle_id")))
    lines.append("- Covers signed batch: " + str(s.get("covered_batch_id"))
                 + " (signed by " + str(s.get("signed_by")) + ")")
    lines.append("- Lane: " + str(s.get("lane")))
    lines.append("- Initial state: " + str(s.get("initial_state", "")))
    lines.append("- Hard cap: " + str(s.get("max_cycle_steps", "")) + " steps, one pass, "
                 "no retries, no loops")
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    blockers = s.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; no cycle may exist)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    steps = s.get("cycle_steps") or []
    if steps:
        lines.append("## Cycle steps (1:1 with the signed batch, nothing else)")
        for st in steps:
            tag = ("HUMAN STOP: " + str(st.get("stop_reason"))
                   if st.get("must_stop_for_human")
                   else "auto-advance eligible IN THEORY ONLY")
            lines.append("- " + str(st.get("seq")) + ". [" + str(st.get("kind"))
                         + "] " + str(st.get("description")) + " -- " + tag)
        lines.append("")
        lines.append("## Recommendation (this spec starts nothing)")
        lines.append("- " + str(s.get("next_safe_command_recommendation")))
        lines.append("")
    lines.append("## Scheduler states (closed set)")
    for state in s.get("scheduler_states") or []:
        lines.append("- " + str(state))
    lines.append("")
    lines.append("## Bounded execution model")
    for rule in s.get("bounded_execution_model") or []:
        lines.append("- " + str(rule))
    lines.append("")
    lines.append("## Refusal rules")
    for rule in s.get("refusal_rules") or []:
        lines.append("- " + str(rule))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)
