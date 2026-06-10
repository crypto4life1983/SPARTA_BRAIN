"""Crypto-D1 V2 Post-Resume-Policy Research Continuation Plan (READ-ONLY, PLAN ONLY).

A PURE, stdlib-only, read-only module that decides WHAT RESEARCH should happen AFTER the
resume-policy chain (Blocks 175-178) completed, using that chain as evidence while strictly
PRESERVING the human decision ``DO_NOT_PROMOTE_RESUME_POLICY_YET``.

It consumes the Block 178 human-review decision (which itself only reads the local
simulation report through Block 177, read-only), re-validates it with Block 178's own
validator, asserts the recorded human decision is still DO_NOT_PROMOTE, and then emits a
FIXED, hand-specified set of research-continuation DIRECTIONS to pursue next. Every
direction is observation/analysis only over ALREADY-EXISTING evidence (QA-passed local
CSVs or already-produced simulated outputs): no new data, no fetch, no new simulation, no
backtest, no optimization, no parameter search, no fitting. The leading policy (RP6 on the
committed evidence) is acknowledged as *evidence only*; acknowledging it never promotes it.

It RUNS NOTHING and WRITES NOTHING. It UNLOCKS no gate: paper_trading_gate, micro_live_gate
and the live gate all stay LOCKED. Actually running any planned research direction, and any
later promotion of any resume policy to a real paper/micro-live/live run, remains a
SEPARATE, explicit, future human command -- this plan never performs or authorizes it.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_MODE / SELECTED_VARIANT_ID
  - VERDICT_PLAN_READY / VERDICT_PLAN_BLOCKED
  - HUMAN_DECISION_PRESERVED / NEXT_REQUIRED_ACTION
  - RESEARCH_CONTINUATION_DIRECTIONS
  - get_post_resume_policy_research_continuation_plan_label()
  - research_continuation_directions()
  - build_post_resume_policy_research_continuation_plan(repo_root)
  - validate_post_resume_policy_research_continuation_plan(plan)
  - render_post_resume_policy_research_continuation_plan_markdown(plan)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_human_review_decision_contract import (
    DECISION_DO_NOT_PROMOTE,
    VERDICT_HUMAN_REVIEW_RECORDED,
    build_resume_policy_human_review_decision,
    validate_resume_policy_human_review_decision,
)

PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_post_resume_policy_research_continuation_plan_contract.v1"
)
PLAN_LABEL = "Crypto-D1 V2 Post-Resume-Policy Research Continuation Plan (READ-ONLY)"
PLAN_MODE = "RESEARCH_ONLY"

VERDICT_PLAN_READY = "RESEARCH_CONTINUATION_PLAN_READY"
VERDICT_PLAN_BLOCKED = "RESEARCH_CONTINUATION_PLAN_BLOCKED"

# The human decision this plan must carry forward UNCHANGED. There is no promote branch:
# promotion to execution is a separate, future, explicit human command never expressible
# through this contract.
HUMAN_DECISION_PRESERVED = DECISION_DO_NOT_PROMOTE

# After this plan is recorded, the only next step remains research-only: a human selects
# which research-continuation direction to pursue. It authorizes no execution and unlocks
# no gate.
NEXT_REQUIRED_ACTION = "HUMAN_SELECT_RESEARCH_CONTINUATION_DIRECTION"

# Fixed, pre-registered research-continuation directions. Each is observation/analysis ONLY
# over already-existing evidence; none fits, optimizes, searches, fetches, or executes, and
# none changes any strategy parameter. Running any of them is gated on a separate human
# command.
RESEARCH_CONTINUATION_DIRECTIONS: list[dict[str, Any]] = [
    {
        "direction_id": "RC1_out_of_sample_robustness_of_leading_policy",
        "description": (
            "Re-observe the SINGLE evidence-leading resume policy (unchanged parameters) on "
            "existing QA-passed local data sub-windows that were not the primary evidence "
            "basis, to test out-of-sample robustness before any promotion is ever considered."
        ),
        "research_question": (
            "Does the evidence leader's edge persist out-of-sample, or is it window-specific?"
        ),
        "method": "replay_one_fixed_policy_over_additional_fixed_regime_subwindows",
        "data_scope": "QA_PASSED_LOCAL_CSV_ONLY",
        "is_executed": False,
        "requires_human_command": True,
        "changes_strategy_parameters": False,
        "is_optimization": False,
        "is_search": False,
    },
    {
        "direction_id": "RC2_cross_policy_stability_ranking",
        "description": (
            "Re-rank the fixed resume-policy candidate set across additional fixed regime "
            "sub-windows to check whether the leader is stable across regimes. No new "
            "candidates, no fitting -- only re-observation of the already-defined set."
        ),
        "research_question": (
            "Is the evidence leader a stable cross-regime leader or regime-dependent?"
        ),
        "method": "reobserve_fixed_candidate_set_ranking_across_fixed_subwindows",
        "data_scope": "QA_PASSED_LOCAL_CSV_ONLY",
        "is_executed": False,
        "requires_human_command": True,
        "changes_strategy_parameters": False,
        "is_optimization": False,
        "is_search": False,
    },
    {
        "direction_id": "RC3_failure_mode_characterization",
        "description": (
            "Catalog, purely descriptively from already-produced simulated outputs, the "
            "conditions under which the leading policy underperforms (drawdown clustering, "
            "resume-event timing, time-in-market). Description only; nothing is re-run."
        ),
        "research_question": "What are the leading policy's worst-case behaviors?",
        "method": "describe_existing_simulated_outputs_no_recompute",
        "data_scope": "EXISTING_SIMULATED_OUTPUTS_ONLY",
        "is_executed": False,
        "requires_human_command": True,
        "changes_strategy_parameters": False,
        "is_optimization": False,
        "is_search": False,
    },
    {
        "direction_id": "RC4_promotion_evidence_gap_enumeration",
        "description": (
            "Enumerate, as documentation only, the additional independent evidence a human "
            "would require before a SEPARATE, explicit promotion decision could even be "
            "considered. Ties to the Block 178 separate-approval-path; authorizes nothing."
        ),
        "research_question": (
            "What independent evidence is still missing before promotion is even discussable?"
        ),
        "method": "document_required_future_evidence_no_data_touched",
        "data_scope": "DOCUMENTATION_ONLY",
        "is_executed": False,
        "requires_human_command": True,
        "changes_strategy_parameters": False,
        "is_optimization": False,
        "is_search": False,
    },
]


def get_post_resume_policy_research_continuation_plan_label() -> str:
    """Human label for the recognized Crypto-D1 post-resume-policy research continuation plan."""
    return PLAN_LABEL


def research_continuation_directions() -> list[dict[str, Any]]:
    """Return fresh deep copies of the fixed research-continuation directions. Pure."""
    return [copy.deepcopy(d) for d in RESEARCH_CONTINUATION_DIRECTIONS]


def build_post_resume_policy_research_continuation_plan(
    repo_root: str = ".",
) -> dict[str, Any]:
    """Load the Block 178 human-review decision (read-only via Block 177) and assemble the
    research-continuation plan over it. Preserves DO_NOT_PROMOTE; writes nothing; runs no
    simulation; unlocks no gate.

    PLAN_READY requires the upstream human review to be RECORDED and to have preserved the
    DO_NOT_PROMOTE decision; otherwise the plan is BLOCKED and carries the reasons forward."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    review = build_resume_policy_human_review_decision(repo_root)

    review_validation = validate_resume_policy_human_review_decision(review)
    if not review_validation.get("valid"):
        blockers.append("human_review_decision_invalid")
        blockers.extend("human_review:" + e for e in review_validation.get("errors", []))

    if review.get("verdict") != VERDICT_HUMAN_REVIEW_RECORDED:
        blockers.append("human_review_not_recorded")

    # Hard invariant: the upstream human decision must still be DO_NOT_PROMOTE. If it is
    # anything else, refuse to build a continuation plan on top of it.
    if review.get("human_decision") != HUMAN_DECISION_PRESERVED:
        blockers.append("human_decision_not_do_not_promote")

    leading = dict(review.get("evidence_leading_policy") or {})
    leader_id = leading.get("policy_id")
    if leader_id:
        risk_notes.append("acknowledged_evidence_leading_policy:" + str(leader_id))
        risk_notes.append("acknowledged_as_evidence_only_not_promotion")
    else:
        risk_notes.append("no_evidence_leading_policy_identified")

    # Carry the human review's own blockers forward for traceability.
    review_blockers = list(review.get("blockers") or [])
    carried_review_blockers = list(review.get("review_blockers") or [])

    risk_notes.append("research_continuation_is_observation_only_over_existing_evidence")
    risk_notes.append("running_any_direction_requires_separate_human_command")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    ready = (
        not blockers
        and review.get("verdict") == VERDICT_HUMAN_REVIEW_RECORDED
        and review.get("human_decision") == HUMAN_DECISION_PRESERVED
    )
    verdict = VERDICT_PLAN_READY if ready else VERDICT_PLAN_BLOCKED

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "label": PLAN_LABEL,
        "mode": PLAN_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        # Decision posture carried forward UNCHANGED from Block 178:
        "human_decision": HUMAN_DECISION_PRESERVED,
        "approved_for_execution": False,
        "human_review_required": True,
        "recommended_path": review.get("recommended_path"),
        "evidence_leading_policy": dict(leading),
        "research_continuation_directions": research_continuation_directions(),
        "upstream_review_verdict": review.get("verdict"),
        "review_blockers": review_blockers,
        "carried_review_blockers": carried_review_blockers,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "resume_policy_sim_report_found": bool(
            review.get("resume_policy_sim_report_found")
        ),
        "resume_policy_sim_report_path": review.get("resume_policy_sim_report_path"),
        # Capability posture (this is a PLAN; it executes / runs / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
        "fetches_data": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "promotes_resume_policy": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this plan):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_post_resume_policy_research_continuation_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) a research-continuation plan's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan

    if p.get("verdict") not in (VERDICT_PLAN_READY, VERDICT_PLAN_BLOCKED):
        errors.append("bad_verdict")
    if p.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if p.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # The preserved decision is structurally always DO_NOT_PROMOTE and never approves execution.
    if p.get("human_decision") != HUMAN_DECISION_PRESERVED:
        errors.append("human_decision_not_do_not_promote")
    if p.get("approved_for_execution") is not False:
        errors.append("plan_marked_approved")
    if p.get("human_review_required") is not True:
        errors.append("plan_not_flagging_human_review")

    directions = p.get("research_continuation_directions")
    if not isinstance(directions, list) or not directions:
        errors.append("no_research_continuation_directions")
        directions = []
    seen: set[str] = set()
    for d in directions:
        if not isinstance(d, dict):
            errors.append("direction_not_a_dict")
            continue
        for key in ("direction_id", "description", "research_question", "method", "data_scope"):
            if key not in d:
                errors.append("direction_missing_field:" + key)
        did = d.get("direction_id")
        if did in seen:
            errors.append("duplicate_direction_id:" + str(did))
        if isinstance(did, str):
            seen.add(did)
        # No direction may be marked executed; each must stay human-gated and inert.
        if d.get("is_executed") is not False:
            errors.append("direction_marked_executed:" + str(did))
        if d.get("requires_human_command") is not True:
            errors.append("direction_not_human_gated:" + str(did))
        for key in ("changes_strategy_parameters", "is_optimization", "is_search"):
            if d.get(key) is not False:
                errors.append("direction_capability_not_false:" + key + ":" + str(did))

    # A READY plan must carry no blockers; a BLOCKED plan should carry at least one.
    if p.get("verdict") == VERDICT_PLAN_READY and (p.get("blockers") or []):
        errors.append("ready_with_blockers")
    if p.get("verdict") == VERDICT_PLAN_BLOCKED and not (p.get("blockers") or []):
        errors.append("blocked_without_blockers")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "ran_parameter_search",
        "parameters_changed_based_on_results",
        "fetches_data",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "promotes_resume_policy",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_post_resume_policy_research_continuation_plan_markdown(plan: Any) -> str:
    """Render a research-continuation plan as deterministic markdown. Pure string work."""
    p = plan if isinstance(plan, dict) else {}
    lead = p.get("evidence_leading_policy") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Post-Resume-Policy Research Continuation Plan (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- Selected variant: " + str(p.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(p.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(p.get("approved_for_execution", "")))
    lines.append("- Recommended path (from review): " + str(p.get("recommended_path", "")))
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    lines.append("## Evidence-leading policy (research evidence only, NOT promoted)")
    lines.append("- Policy: " + str(lead.get("policy_id")))
    lines.append("- Leads all categories: " + str(lead.get("leads_all_categories")))
    lines.append("")
    lines.append("## Research-continuation directions (fixed; each gated on a human command)")
    for d in p.get("research_continuation_directions") or []:
        lines.append("### " + str(d.get("direction_id")))
        lines.append("- " + str(d.get("description")))
        lines.append("- Question: " + str(d.get("research_question")))
        lines.append("- Data scope: " + str(d.get("data_scope")))
        lines.append("- is_executed: " + str(d.get("is_executed"))
                     + " | requires_human_command: " + str(d.get("requires_human_command")))
    lines.append("")
    lines.append("## Blockers")
    for b in (p.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in p.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- runs_simulation: False (a separate human command is required to run any direction)")
    return "\n".join(lines)
