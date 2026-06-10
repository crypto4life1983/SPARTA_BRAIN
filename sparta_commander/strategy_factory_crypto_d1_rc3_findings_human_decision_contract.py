"""Crypto-D1 V2 RC3 Findings HUMAN DECISION Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that RECORDS a human's decision over the completed
RC3 failure-mode findings for ``V2_trend_plus_cash_regime``. It is the human-judgment
companion to the automated Block 188 characterization: where Block 188 mechanically
described WHY the RC1 leader failed out of sample, THIS contract captures the human's
recorded verdict and CLOSES the resume-policy research thread cleanly.

It consumes the Block 188 characterization (which chains read-only through the persisted
RC1/RC2 reports and the Block 187 decision), re-validates it with Block 188's own
validator, and emits a human-decision record that:
  - acknowledges that RC3 found ALL FOUR candidate failure modes supported on the
    committed evidence (volatility-cooldown overfit, regime sensitivity,
    delayed/over-filtered re-entry, ranking instability);
  - acknowledges that the RC1 leader (RP6 on the committed evidence) failed out-of-sample
    leadership, and that the strongest candidates (RP4/RP5) are EVIDENCE ONLY -- NOT
    selected successors (``successors_selected`` is structurally False);
  - records the human decision, which is ALWAYS ``DO_NOT_PROMOTE_RESUME_POLICY_YET``;
  - records the selected outcome -- by default
    ``CLOSE_RESUME_POLICY_RESEARCH_THREAD_WITH_LESSONS`` -- with the thread's LESSONS
    written into the record;
  - records, STRUCTURALLY, that any future reconsideration of any resume policy requires
    GENUINELY FRESH EVIDENCE -- not the same RC1/RC2 windows
    (``fresh_evidence_required_for_reconsideration`` is always True and the validator
    rejects anything else).

It RUNS NOTHING and WRITES NOTHING: no data fetch, no replay, no simulation, no backtest,
no optimization, no parameter search, no broker/exchange, no network, no credentials, no
real order, no file write. It UNLOCKS no gate: paper_trading_gate, micro_live_gate and the
live gate all stay LOCKED. It approves nothing: paper, micro-live, live, broker, exchange
and execution all remain unapproved; promotion remains a SEPARATE, future, explicit human
command that would itself require the fresh evidence this record demands.

Public API:
  - RC3_DECISION_SCHEMA_VERSION / RC3_DECISION_LABEL / RC3_DECISION_MODE
  - VERDICT_DECISION_RECORDED / VERDICT_DECISION_BLOCKED
  - DECISION_DO_NOT_PROMOTE / SELECTED_VARIANT_ID
  - OUTCOME_CLOSE_THREAD_WITH_LESSONS / OUTCOME_REQUIRE_FURTHER_CHARACTERIZATION
  - OUTCOME_KEEP_THREAD_OPEN / ALLOWED_OUTCOMES
  - RECONSIDERATION_REQUIREMENT / THREAD_LESSONS / NEXT_REQUIRED_ACTION
  - get_rc3_findings_human_decision_label()
  - allowed_outcomes() / thread_lessons()
  - record_rc3_findings_human_decision(characterization, *, selected_outcome=..., decision_reason=...)
  - build_rc3_findings_human_decision(repo_root, *, selected_outcome=..., decision_reason=...)
  - validate_rc3_findings_human_decision(decision)
  - render_rc3_findings_human_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc3_failure_mode_characterization_research_contract import (
    VERDICT_RC3_COMPLETE,
    build_rc3_failure_mode_characterization,
    validate_rc3_failure_mode_characterization,
)

RC3_DECISION_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc3_findings_human_decision_contract.v1"
)
RC3_DECISION_LABEL = "Crypto-D1 V2 RC3 Findings Human Decision (READ-ONLY)"
RC3_DECISION_MODE = "RESEARCH_ONLY"

VERDICT_DECISION_RECORDED = "RC3_FINDINGS_DECISION_RECORDED"
VERDICT_DECISION_BLOCKED = "RC3_FINDINGS_DECISION_BLOCKED"

# The human decision recordable here is, by design, ALWAYS this single value. There is no
# promote branch: promoting to execution is a separate, future, explicit human command and
# is never expressible through this contract.
DECISION_DO_NOT_PROMOTE = DO_NOT_PROMOTE_RESUME_POLICY_YET

# Outcomes the human may record. All are research-only; none unlocks a gate, authorizes
# execution, or selects a successor policy.
OUTCOME_CLOSE_THREAD_WITH_LESSONS = "CLOSE_RESUME_POLICY_RESEARCH_THREAD_WITH_LESSONS"
OUTCOME_REQUIRE_FURTHER_CHARACTERIZATION = "REQUIRE_FURTHER_CHARACTERIZATION"
OUTCOME_KEEP_THREAD_OPEN = "KEEP_RESEARCH_THREAD_OPEN"
ALLOWED_OUTCOMES: tuple[str, ...] = (
    OUTCOME_CLOSE_THREAD_WITH_LESSONS,
    OUTCOME_REQUIRE_FURTHER_CHARACTERIZATION,
    OUTCOME_KEEP_THREAD_OPEN,
)

# Structural requirement carried by EVERY decision this contract emits: any future
# reconsideration of any resume policy needs genuinely fresh evidence -- never the same
# RC1/RC2 windows that exposed the overfit.
RECONSIDERATION_REQUIREMENT = (
    "REQUIRE_FRESH_EVIDENCE_VALIDATION_BEFORE_ANY_RECONSIDERATION"
)

# The lessons this thread closes with -- fixed, recorded verbatim into the decision.
THREAD_LESSONS: tuple[str, ...] = (
    "in_sample_leadership_is_not_evidence_of_out_of_sample_edge",
    "complex_fitted_triggers_underperform_simple_rules_out_of_sample",
    "successor_selection_from_the_same_windows_repeats_the_overfit_mistake",
    "genuinely_fresh_evidence_is_required_before_any_promotion_discussion",
)

# After this decision the resume-policy thread is closed; the only next step is a NEW,
# SEPARATE, explicit human research directive. Nothing here is an execution authorization.
NEXT_REQUIRED_ACTION = "AWAIT_NEW_HUMAN_RESEARCH_DIRECTIVE"

DEFAULT_DECISION_REASON = (
    "There is now enough evidence that this resume-policy path should not move toward "
    "promotion: the RC1 leader failed out of sample, the stronger candidates are only "
    "evidence from the same windows, and RC3 identified clear failure modes. The safest "
    "step is to close this thread cleanly and require genuinely fresh evidence before "
    "any future reconsideration."
)


def get_rc3_findings_human_decision_label() -> str:
    """Human label for the recognized Crypto-D1 RC3 findings human decision contract."""
    return RC3_DECISION_LABEL


def allowed_outcomes() -> tuple[str, ...]:
    """Return the allowed decision outcomes. Pure."""
    return ALLOWED_OUTCOMES


def thread_lessons() -> tuple[str, ...]:
    """Return the fixed lessons this thread closes with. Pure."""
    return THREAD_LESSONS


def record_rc3_findings_human_decision(
    characterization: Any,
    *,
    selected_outcome: str = OUTCOME_CLOSE_THREAD_WITH_LESSONS,
    decision_reason: str = DEFAULT_DECISION_REASON,
) -> dict[str, Any]:
    """Record a human's decision over the Block 188 characterization. PURE: takes the
    characterization dict (or None) plus the human's selected outcome, returns a decision
    record. Never raises. The recorded human decision is ALWAYS ``DECISION_DO_NOT_PROMOTE``;
    this contract has no promote branch, selects no successor, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if selected_outcome not in ALLOWED_OUTCOMES:
        blockers.append("invalid_selected_outcome:" + str(selected_outcome))
        selected_outcome_value: str | None = None
    else:
        selected_outcome_value = selected_outcome

    if not isinstance(characterization, dict):
        blockers.append("rc3_characterization_missing")
        return _decision(
            VERDICT_DECISION_BLOCKED, blockers, risk_notes,
            selected_outcome=selected_outcome_value, decision_reason=decision_reason,
            supported_failure_modes=[], strongest=[], rc1_leader=None,
        )

    ch = characterization

    ch_validation = validate_rc3_failure_mode_characterization(ch)
    if not ch_validation.get("valid"):
        blockers.append("rc3_characterization_invalid")
        blockers.extend("rc3:" + e for e in ch_validation.get("errors", []))

    if ch.get("verdict") != VERDICT_RC3_COMPLETE:
        blockers.append("rc3_characterization_not_complete")

    if ch.get("human_decision") != DECISION_DO_NOT_PROMOTE:
        blockers.append("characterization_decision_not_do_not_promote")

    supported = [str(x) for x in (ch.get("supported_failure_modes") or [])]
    rc1_leader = ch.get("rc1_leader_policy_id")
    strongest = [
        str(p) for p in (
            (ch.get("strength_analysis") or {}).get("strongest_evidence_policies") or []
        )
    ]

    # Acknowledge the findings honestly. Recording is descriptive only.
    for fid in supported:
        risk_notes.append("acknowledged_supported_failure_mode:" + fid)
    if rc1_leader:
        risk_notes.append(
            "acknowledged_rc1_leader_failed_oos_leadership:" + str(rc1_leader)
        )
    for pid in strongest:
        risk_notes.append("acknowledged_strongest_oos_evidence:" + pid)
    risk_notes.append("strongest_policies_are_evidence_only_not_selected_successors")
    risk_notes.append("thread_closure_is_a_research_decision_not_an_authorization")
    risk_notes.append(
        "any_future_reconsideration_requires_genuinely_fresh_evidence_not_rc1_rc2_windows"
    )
    risk_notes.append("human_decision_is_research_only_not_execution_validated")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    recorded = not blockers and ch.get("verdict") == VERDICT_RC3_COMPLETE
    verdict = VERDICT_DECISION_RECORDED if recorded else VERDICT_DECISION_BLOCKED
    return _decision(
        verdict, blockers, risk_notes,
        selected_outcome=selected_outcome_value, decision_reason=decision_reason,
        supported_failure_modes=supported, strongest=strongest, rc1_leader=rc1_leader,
    )


def _decision(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    selected_outcome: str | None,
    decision_reason: str,
    supported_failure_modes: list[str],
    strongest: list[str],
    rc1_leader: Any,
) -> dict[str, Any]:
    """Assemble an RC3 findings decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally,
    the human decision is always DO_NOT_PROMOTE, no successor is selected, and fresh
    evidence is structurally required before any future reconsideration."""
    thread_closed = (
        verdict == VERDICT_DECISION_RECORDED
        and selected_outcome == OUTCOME_CLOSE_THREAD_WITH_LESSONS
    )
    return {
        "schema_version": RC3_DECISION_SCHEMA_VERSION,
        "label": RC3_DECISION_LABEL,
        "mode": RC3_DECISION_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": DECISION_DO_NOT_PROMOTE,
        "approved_for_execution": False,
        "human_review_required": True,
        "selected_outcome": selected_outcome,
        "decision_reason": decision_reason,
        "thread_closed": thread_closed,
        "lessons_recorded": list(THREAD_LESSONS) if thread_closed else [],
        # Structurally True: every decision from this contract demands fresh evidence
        # before any future reconsideration.
        "fresh_evidence_required_for_reconsideration": True,
        "reconsideration_requirement": RECONSIDERATION_REQUIREMENT,
        "rc1_leader_policy_id": rc1_leader,
        "supported_failure_modes": list(supported_failure_modes),
        "strongest_evidence_policies": list(strongest),
        # Structurally False: this contract can never crown a successor policy.
        "successors_selected": False,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        # Capability posture (this contract executes / authorizes / writes nothing live):
        "executes": False,
        "writes_files": False,
        "runs_replay": False,
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
        # Gate posture (UNCHANGED by this decision):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_rc3_findings_human_decision(
    repo_root: str = ".",
    *,
    selected_outcome: str = OUTCOME_CLOSE_THREAD_WITH_LESSONS,
    decision_reason: str = DEFAULT_DECISION_REASON,
) -> dict[str, Any]:
    """Load the Block 188 characterization (which reads the persisted RC1/RC2 reports
    read-only) and record a human decision over it. Reads nothing itself beyond what Block
    188 reads; writes nothing; runs no replay; unlocks no gate."""
    characterization = build_rc3_failure_mode_characterization(repo_root)
    decision = record_rc3_findings_human_decision(
        characterization, selected_outcome=selected_outcome,
        decision_reason=decision_reason,
    )
    decision["rc3_characterization_verdict"] = characterization.get("verdict")
    return decision


def validate_rc3_findings_human_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) an RC3 findings decision's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_DECISION_RECORDED, VERDICT_DECISION_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != RC3_DECISION_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # The human decision is structurally always DO_NOT_PROMOTE and never approves
    # execution; no successor may be selected; fresh evidence is always required.
    if d.get("human_decision") != DECISION_DO_NOT_PROMOTE:
        errors.append("human_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("decision_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("decision_not_flagging_human_review")
    if d.get("successors_selected") is not False:
        errors.append("successor_policy_marked_selected")
    if d.get("fresh_evidence_required_for_reconsideration") is not True:
        errors.append("fresh_evidence_requirement_dropped")
    if d.get("reconsideration_requirement") != RECONSIDERATION_REQUIREMENT:
        errors.append("bad_reconsideration_requirement")

    # A recorded decision must carry a valid outcome; a blocked one may carry None.
    if d.get("verdict") == VERDICT_DECISION_RECORDED:
        if d.get("selected_outcome") not in ALLOWED_OUTCOMES:
            errors.append("recorded_without_valid_outcome")
        if d.get("blockers") or []:
            errors.append("recorded_with_blockers")
        # A closed thread must carry its lessons.
        if d.get("selected_outcome") == OUTCOME_CLOSE_THREAD_WITH_LESSONS:
            if d.get("thread_closed") is not True:
                errors.append("close_outcome_without_thread_closed")
            if not (d.get("lessons_recorded") or []):
                errors.append("thread_closed_without_lessons")
    elif d.get("selected_outcome") is not None and (
        d.get("selected_outcome") not in ALLOWED_OUTCOMES
    ):
        errors.append("bad_selected_outcome")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_replay",
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
        if d.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_rc3_findings_human_decision_markdown(decision: Any) -> str:
    """Render an RC3 findings decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC3 Findings Human Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Human decision: " + str(d.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Selected outcome: " + str(d.get("selected_outcome", "")))
    lines.append("- Thread closed: " + str(d.get("thread_closed", "")))
    lines.append("- Successors selected: " + str(d.get("successors_selected", "")))
    lines.append("- Reconsideration requirement: "
                 + str(d.get("reconsideration_requirement", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Decision reason")
    lines.append(str(d.get("decision_reason", "")))
    lines.append("")
    lines.append("## Lessons recorded")
    for lesson in (d.get("lessons_recorded") or ["(none)"]):
        lines.append("- " + str(lesson))
    lines.append("")
    lines.append("## Acknowledged findings (research evidence only)")
    lines.append("- RC1 leader: " + str(d.get("rc1_leader_policy_id")))
    lines.append("- Supported failure modes: "
                 + (", ".join(d.get("supported_failure_modes") or []) or "(none)"))
    lines.append("- Strongest OOS evidence (NOT selected successors): "
                 + (", ".join(d.get("strongest_evidence_policies") or []) or "(none)"))
    lines.append("")
    lines.append("## Blockers")
    for b in (d.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in d.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- authorizes_paper_execution: False (separate human gate + command required)")
    return "\n".join(lines)
