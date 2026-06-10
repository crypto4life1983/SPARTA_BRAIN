"""Crypto-D1 V2 RC2 Cross-Policy HUMAN EVIDENCE Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that RECORDS a human's decision over the completed
RC2 cross-policy evidence for ``V2_trend_plus_cash_regime``. It is the human-judgment
companion to the automated Block 186 results review: where Block 186 mechanically scored
the persisted RC2 replay report and recorded the leadership flip, THIS contract captures
the human's recorded verdict on that evidence and the human's chosen research direction.

It consumes the Block 186 reviewer output (which itself reads only
``reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json``
read-only), re-validates it with Block 186's own validator, and emits a human-evidence
record that:
  - acknowledges that RC2 reviewed the FIXED candidate set (RP1..RP6, parameters
    unchanged) over the SAME fixed out-of-sample windows RC1 used;
  - acknowledges that the RC1 leader (RP6 on the committed evidence) FAILED out-of-sample
    leadership and led ZERO ranking categories;
  - acknowledges that other fixed candidates (RP4/RP5 on the committed evidence) showed
    the strongest out-of-sample evidence -- and EXPLICITLY records that they are EVIDENCE
    ONLY and are NOT selected successors (``successors_selected`` is structurally False:
    picking a successor out of the same windows that exposed the first leader would risk
    repeating the same overfit mistake);
  - records the human decision, which is ALWAYS ``DO_NOT_PROMOTE_RESUME_POLICY_YET``;
  - records the selected research direction -- by default
    ``CONTINUE_RESEARCH_VIA_RC3_FAILURE_MODE_CHARACTERIZATION``: understand WHY the
    leader failed and WHY the others looked better before considering any new candidate
    direction;
  - carries the reviewer's blockers, risk notes, and leadership analysis forward.

It RUNS NOTHING and WRITES NOTHING: no data fetch, no replay, no simulation, no backtest,
no optimization, no parameter search, no broker/exchange, no network, no credentials, no
real order, no file write. It UNLOCKS no gate: paper_trading_gate, micro_live_gate and the
live gate all stay LOCKED. It approves nothing: paper, micro-live, live, broker, exchange
and execution all remain unapproved; promotion remains a SEPARATE, future, explicit human
command.

Public API:
  - HUMAN_EVIDENCE_SCHEMA_VERSION / HUMAN_EVIDENCE_LABEL / HUMAN_EVIDENCE_MODE
  - VERDICT_DECISION_RECORDED / VERDICT_DECISION_BLOCKED
  - DECISION_DO_NOT_PROMOTE / SELECTED_VARIANT_ID
  - DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION / DIRECTION_FURTHER_VALIDATION
  - DIRECTION_CLOSE_RC2_THREAD / ALLOWED_DIRECTIONS / NEXT_REQUIRED_ACTION
  - get_rc2_cross_policy_human_evidence_decision_label()
  - allowed_directions()
  - record_rc2_cross_policy_human_evidence_decision(results_review_decision, *, selected_direction=..., decision_reason=...)
  - build_rc2_cross_policy_human_evidence_decision(repo_root, *, selected_direction=..., decision_reason=...)
  - validate_rc2_cross_policy_human_evidence_decision(decision)
  - render_rc2_cross_policy_human_evidence_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract import (
    VERDICT_RC2_REVIEW_COMPLETE,
    build_rc2_cross_policy_results_review_decision,
    validate_rc2_cross_policy_results_review_decision,
)

HUMAN_EVIDENCE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract.v1"
)
HUMAN_EVIDENCE_LABEL = "Crypto-D1 V2 RC2 Cross-Policy Human Evidence Decision (READ-ONLY)"
HUMAN_EVIDENCE_MODE = "RESEARCH_ONLY"

VERDICT_DECISION_RECORDED = "RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_RECORDED"
VERDICT_DECISION_BLOCKED = "RC2_CROSS_POLICY_HUMAN_EVIDENCE_DECISION_BLOCKED"

# The human decision recordable here is, by design, ALWAYS this single value. There is no
# promote branch: promoting to execution is a separate, future, explicit human command and
# is never expressible through this contract.
DECISION_DO_NOT_PROMOTE = DO_NOT_PROMOTE_RESUME_POLICY_YET

# Research directions the human may record. All are research-only; none unlocks a gate or
# authorizes execution, and none selects a successor policy.
DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION = (
    "CONTINUE_RESEARCH_VIA_RC3_FAILURE_MODE_CHARACTERIZATION"
)
DIRECTION_FURTHER_VALIDATION = "REQUIRE_FURTHER_VALIDATION"
DIRECTION_CLOSE_RC2_THREAD = "CLOSE_RC2_RESEARCH_THREAD"
ALLOWED_DIRECTIONS: tuple[str, ...] = (
    DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION,
    DIRECTION_FURTHER_VALIDATION,
    DIRECTION_CLOSE_RC2_THREAD,
)

# After this decision the only next step remains research-only: the human-approved RC3
# failure-mode characterization. Nothing here is an execution authorization.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RC3_FAILURE_MODE_CHARACTERIZATION_RESEARCH"

# The research question RC3 exists to answer; recorded for traceability.
RC3_RESEARCH_QUESTION = (
    "Why did the RC1 leader fail out of sample, and why did the other fixed candidates "
    "look better? Characterize the failure modes, purely descriptively from already-"
    "produced evidence, before considering any new candidate direction."
)

DEFAULT_DECISION_REASON = (
    "RC2 proved the original leader was overfit in sample, and other fixed candidates "
    "look better out of sample -- but selecting them from the same out-of-sample windows "
    "would risk repeating the same mistake. The next safest step is RC3 failure-mode "
    "characterization: understand why the leader failed and why the others looked better "
    "before considering any new candidate direction."
)


def get_rc2_cross_policy_human_evidence_decision_label() -> str:
    """Human label for the recognized Crypto-D1 RC2 cross-policy human evidence decision
    contract."""
    return HUMAN_EVIDENCE_LABEL


def allowed_directions() -> tuple[str, ...]:
    """Return the allowed research directions. Pure."""
    return ALLOWED_DIRECTIONS


def record_rc2_cross_policy_human_evidence_decision(
    results_review_decision: Any,
    *,
    selected_direction: str = DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION,
    decision_reason: str = DEFAULT_DECISION_REASON,
) -> dict[str, Any]:
    """Record a human's decision over the Block 186 results-review decision. PURE: takes
    the reviewer decision dict (or None) plus the human's selected research direction,
    returns a human-evidence record. Never raises. The recorded human decision is ALWAYS
    ``DECISION_DO_NOT_PROMOTE``; this contract has no promote branch, selects no
    successor, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if selected_direction not in ALLOWED_DIRECTIONS:
        blockers.append("invalid_selected_direction:" + str(selected_direction))
        selected_direction_value: str | None = None
    else:
        selected_direction_value = selected_direction

    if not isinstance(results_review_decision, dict):
        blockers.append("rc2_results_review_decision_missing")
        return _decision(
            VERDICT_DECISION_BLOCKED, blockers, risk_notes,
            selected_direction=selected_direction_value,
            decision_reason=decision_reason, leadership={},
            strongest=[], review_blockers=[], report_found=False,
        )

    rd = results_review_decision

    review_validation = validate_rc2_cross_policy_results_review_decision(rd)
    if not review_validation.get("valid"):
        blockers.append("rc2_results_review_decision_invalid")
        blockers.extend("review:" + e for e in review_validation.get("errors", []))

    if rd.get("verdict") != VERDICT_RC2_REVIEW_COMPLETE:
        blockers.append("rc2_results_review_not_complete")

    if rd.get("rc2_replay_report_found") is not True:
        blockers.append("rc2_replay_report_missing")

    if rd.get("promotion_decision") != DECISION_DO_NOT_PROMOTE:
        blockers.append("review_promotion_decision_not_do_not_promote")

    leadership = dict(rd.get("leadership_analysis") or {})

    # Acknowledge the evidence honestly. Recording is descriptive only; it never selects
    # or promotes any policy.
    risk_notes.append("acknowledged_rc2_reviewed_fixed_candidates_over_same_oos_windows")
    rc1_leader = leadership.get("rc1_leader_policy_id")
    if leadership.get("leadership_flip_confirmed"):
        risk_notes.append(
            "acknowledged_rc1_leader_failed_oos_leadership:" + str(rc1_leader)
        )
        risk_notes.append("acknowledged_rc1_leader_led_zero_categories")
    else:
        risk_notes.append("leadership_flip_not_flagged_by_review")

    # The strongest-evidence policies are the unique category leaders; they are NEVER
    # selected here.
    strongest = sorted(set(
        str(pid) for pid in (leadership.get("current_category_leaders") or {}).values()
        if pid
    ))
    for pid in strongest:
        risk_notes.append("acknowledged_strongest_oos_evidence:" + pid)
    risk_notes.append("strongest_policies_are_evidence_only_not_selected_successors")
    risk_notes.append("selecting_a_successor_from_the_same_windows_risks_repeating_overfit")

    # Carry the reviewer's own risk notes forward for human traceability.
    for note in rd.get("risk_notes") or []:
        risk_notes.append("review_note:" + str(note))

    risk_notes.append("human_decision_is_research_only_not_execution_validated")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    recorded = (
        not blockers
        and rd.get("verdict") == VERDICT_RC2_REVIEW_COMPLETE
        and rd.get("rc2_replay_report_found") is True
    )
    verdict = VERDICT_DECISION_RECORDED if recorded else VERDICT_DECISION_BLOCKED
    return _decision(
        verdict, blockers, risk_notes,
        selected_direction=selected_direction_value, decision_reason=decision_reason,
        leadership=leadership, strongest=strongest,
        review_blockers=list(rd.get("blockers") or []),
        report_found=bool(rd.get("rc2_replay_report_found")),
    )


def _decision(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    selected_direction: str | None,
    decision_reason: str,
    leadership: dict[str, Any],
    strongest: list[str],
    review_blockers: list[str],
    report_found: bool,
) -> dict[str, Any]:
    """Assemble a human-evidence decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally,
    the human decision is always DO_NOT_PROMOTE, no successor is selected, and the
    selected direction is a research direction only -- never an execution authorization."""
    return {
        "schema_version": HUMAN_EVIDENCE_SCHEMA_VERSION,
        "label": HUMAN_EVIDENCE_LABEL,
        "mode": HUMAN_EVIDENCE_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": DECISION_DO_NOT_PROMOTE,
        "approved_for_execution": False,
        "human_review_required": True,
        "selected_research_direction": selected_direction,
        "decision_reason": decision_reason,
        "rc3_research_question": RC3_RESEARCH_QUESTION,
        "leadership_analysis": dict(leadership),
        "strongest_evidence_policies": list(strongest),
        # Structurally False: this contract can never crown a successor policy.
        "successors_selected": False,
        "review_blockers": list(review_blockers),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "rc2_replay_report_found": report_found,
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


def build_rc2_cross_policy_human_evidence_decision(
    repo_root: str = ".",
    *,
    selected_direction: str = DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION,
    decision_reason: str = DEFAULT_DECISION_REASON,
) -> dict[str, Any]:
    """Load the Block 186 results-review decision (which reads the local RC2 replay report
    read-only) and record a human decision over it. Reads nothing itself beyond what Block
    186 reads; writes nothing; runs no replay; unlocks no gate."""
    review_decision = build_rc2_cross_policy_results_review_decision(repo_root)
    decision = record_rc2_cross_policy_human_evidence_decision(
        review_decision, selected_direction=selected_direction,
        decision_reason=decision_reason,
    )
    decision["rc2_replay_report_path"] = review_decision.get("rc2_replay_report_path")
    decision["results_review_verdict"] = review_decision.get("verdict")
    return decision


def validate_rc2_cross_policy_human_evidence_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a human-evidence decision's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_DECISION_RECORDED, VERDICT_DECISION_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != HUMAN_EVIDENCE_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # The human decision is structurally always DO_NOT_PROMOTE and never approves
    # execution; no successor policy may ever be marked selected.
    if d.get("human_decision") != DECISION_DO_NOT_PROMOTE:
        errors.append("human_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("decision_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("decision_not_flagging_human_review")
    if d.get("successors_selected") is not False:
        errors.append("successor_policy_marked_selected")

    # A recorded decision must carry a valid direction; a blocked one may carry None.
    if d.get("verdict") == VERDICT_DECISION_RECORDED:
        if d.get("selected_research_direction") not in ALLOWED_DIRECTIONS:
            errors.append("recorded_without_valid_direction")
        if d.get("blockers") or []:
            errors.append("recorded_with_blockers")
    elif d.get("selected_research_direction") is not None and (
        d.get("selected_research_direction") not in ALLOWED_DIRECTIONS
    ):
        errors.append("bad_selected_direction")

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


def render_rc2_cross_policy_human_evidence_decision_markdown(decision: Any) -> str:
    """Render a human-evidence decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    la = d.get("leadership_analysis") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC2 Cross-Policy Human Evidence Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Human decision: " + str(d.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Selected research direction: "
                 + str(d.get("selected_research_direction", "")))
    lines.append("- Successors selected: " + str(d.get("successors_selected", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Decision reason")
    lines.append(str(d.get("decision_reason", "")))
    lines.append("")
    lines.append("## RC3 research question")
    lines.append(str(d.get("rc3_research_question", "")))
    lines.append("")
    lines.append("## Acknowledged evidence (research evidence only)")
    lines.append("- RC1 leader: " + str(la.get("rc1_leader_policy_id")))
    lines.append("- Leadership flip confirmed: " + str(la.get("leadership_flip_confirmed")))
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
