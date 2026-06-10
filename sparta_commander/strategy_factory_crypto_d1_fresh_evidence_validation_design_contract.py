"""Crypto-D1 V2 Fresh-Evidence Validation Design Contract (READ-ONLY, DESIGN ONLY).

A PURE, stdlib-only, read-only module that PRE-REGISTERS -- before any qualifying data
exists -- exactly what GENUINELY FRESH EVIDENCE would be required before any
reconsideration of RP4/RP5 or any other fixed resume-policy candidate. It discharges the
Block 189 structural requirement (``fresh_evidence_required_for_reconsideration``) by
turning it from a phrase into a frozen, falsifiable rulebook.

The core anti-curve-fitting property: every criterion in this design is FIXED NOW, while
the evidence that could satisfy it does not yet exist (the staged CSVs end 2026-06-08 and
every RC1/RC2 window is already consumed). The bars therefore cannot be fitted to the
data that will eventually judge them. The design's evaluation may run ONCE per fresh
window with THESE bars; re-evaluating the same window under different bars is forbidden.

It is gated on the Block 189 findings decision (thread closed with lessons, fresh
evidence required) and defines:
  - EVIDENCE SOURCE RULES -- future, manually staged daily CSV data only, strictly after
    the 2026-06-08 cutoff, zero overlap with any RC1/RC2 window, no fetch ever;
  - a MINIMUM fresh-window length (180 days; 365 preferred) before evaluation is even
    permitted;
  - FIXED pass/fail bars on return, drawdown, Sharpe, and cross-candidate stability;
  - CANDIDATE ELIGIBILITY -- only the six fixed candidates (RP1..RP6, parameters verbatim
    from Block 175); any parameter change disqualifies; new candidates need their own
    separately pre-registered design;
  - EXPLICIT REJECTION RULES -- all bars must pass, tainted or short windows are
    rejected/not evaluable, and PASSING PROMOTES NOTHING: a pass only qualifies the
    candidate for a separate future human reconsideration decision.

It RUNS NOTHING and WRITES NOTHING: no data fetch, no replay, no simulation, no backtest,
no optimization, no parameter search, no broker/exchange, no network, no credentials, no
real order, no file write. It UNLOCKS no gate: real_data_qa and baseline_backtest stay
BLOCKED, paper_trading_gate, micro_live_gate and the live gate all stay LOCKED, and
``DO_NOT_PROMOTE_RESUME_POLICY_YET`` is preserved throughout.

Public API:
  - DESIGN_SCHEMA_VERSION / DESIGN_LABEL / DESIGN_MODE / SELECTED_VARIANT_ID
  - VERDICT_DESIGN_READY / VERDICT_DESIGN_BLOCKED / NEXT_REQUIRED_ACTION
  - FRESH_EVIDENCE_CUTOFF_DATE / MIN_FRESH_WINDOW_DAYS / PREFERRED_FRESH_WINDOW_DAYS
  - EVIDENCE_SOURCE_RULES / PASS_FAIL_BARS / CANDIDATE_ELIGIBILITY / REJECTION_RULES
  - get_fresh_evidence_validation_design_label()
  - evidence_source_rules() / pass_fail_bars() / candidate_eligibility() / rejection_rules()
  - record_fresh_evidence_validation_design(rc3_findings_decision)
  - build_fresh_evidence_validation_design(repo_root)
  - validate_fresh_evidence_validation_design(design)
  - render_fresh_evidence_validation_design_markdown(design)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc3_findings_human_decision_contract import (
    VERDICT_DECISION_RECORDED,
    build_rc3_findings_human_decision,
    validate_rc3_findings_human_decision,
)

DESIGN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_fresh_evidence_validation_design_contract.v1"
)
DESIGN_LABEL = (
    "Crypto-D1 V2 Fresh-Evidence Validation Design (READ-ONLY, DESIGN ONLY)"
)
DESIGN_MODE = "RESEARCH_ONLY"

VERDICT_DESIGN_READY = "FRESH_EVIDENCE_DESIGN_READY"
VERDICT_DESIGN_BLOCKED = "FRESH_EVIDENCE_DESIGN_BLOCKED"

# After this design is recorded, the pipeline simply WAITS for qualifying evidence to
# accrue (one daily candle at a time, staged manually). The evaluation itself is a
# future, separate, explicit human command. Nothing here authorizes execution.
NEXT_REQUIRED_ACTION = "AWAIT_FRESH_EVIDENCE_ACCRUAL"

# Every RC1/RC2 window ends on or before this date (the last candle in the staged CSVs
# at design time). A qualifying fresh window must start STRICTLY AFTER it.
FRESH_EVIDENCE_CUTOFF_DATE = "2026-06-08"

# A fresh window shorter than this is NOT EVALUABLE -- wait, do not peek.
MIN_FRESH_WINDOW_DAYS = 180
PREFERRED_FRESH_WINDOW_DAYS = 365

# The six fixed candidates this design covers. Parameters verbatim from the Block 175
# research plan; any change disqualifies the candidate from THIS design.
_FIXED_CANDIDATE_IDS: tuple[str, ...] = (
    "RP1_wait_7d_trend_on",
    "RP2_wait_14d_trend_on",
    "RP3_wait_30d_trend_on",
    "RP4_breadth_2of3_above_sma200",
    "RP5_half_then_full_on_confirmation",
    "RP6_resume_after_volatility_cools",
)

EVIDENCE_SOURCE_RULES: dict[str, Any] = {
    "source": "MANUALLY_STAGED_DAILY_CSV_ONLY",
    "fetch_allowed": False,
    "window_must_start_after": FRESH_EVIDENCE_CUTOFF_DATE,
    "overlap_with_rc1_rc2_windows_allowed": False,
    "min_window_days": MIN_FRESH_WINDOW_DAYS,
    "preferred_window_days": PREFERRED_FRESH_WINDOW_DAYS,
    "evaluation_runs_once_per_window": True,
    "bars_frozen_by_this_design": True,
}

# FIXED pass/fail bars over the fresh window, frozen before any qualifying candle
# exists. Anchors: the in-sample worst drawdown was -32.4%; the OOS straddles ran
# Sharpe ~0.8-1.4. ALL bars must pass; there is no partial credit.
PASS_FAIL_BARS: dict[str, Any] = {
    "min_total_return": 0.0,            # must be strictly positive over the window
    "max_acceptable_drawdown": -0.35,   # worst drawdown must not be worse than -35%
    "min_sharpe_ratio": 0.8,            # annualized, over the fresh window
    # Stability: ranked against ALL six fixed candidates over the SAME fresh window,
    # the candidate must place in the top half (top 3 of 6) on EVERY ranking category
    # (mean return, worst drawdown, Sharpe). A leader that cannot stay top-half on
    # fresh data is the exact failure mode RC2 exposed.
    "stability_min_rank_top_half_all_categories": True,
    "all_bars_must_pass": True,
}

CANDIDATE_ELIGIBILITY: dict[str, Any] = {
    "eligible_candidate_ids": list(_FIXED_CANDIDATE_IDS),
    "parameters_must_be_verbatim_block_175": True,
    "parameter_change_disqualifies": True,
    "new_candidates_require_their_own_preregistered_design": True,
    "rp4_rp5_have_no_special_status": (
        "RP4/RP5 enter on the same bars as every other fixed candidate; their RC2 "
        "strength is evidence, not a head start"
    ),
}

REJECTION_RULES: list[str] = [
    "any_single_bar_missed_rejects_the_candidate_no_partial_credit",
    "window_shorter_than_minimum_is_not_evaluable_wait_do_not_peek",
    "any_overlap_with_rc1_rc2_windows_rejects_the_evidence_as_tainted",
    "any_parameter_change_rejects_the_candidate_from_this_design",
    "re_evaluating_the_same_window_under_different_bars_is_forbidden",
    "passing_all_bars_promotes_nothing_it_only_qualifies_the_candidate_for_a_"
    "separate_future_human_reconsideration_decision",
]


def get_fresh_evidence_validation_design_label() -> str:
    """Human label for the recognized Crypto-D1 fresh-evidence validation design."""
    return DESIGN_LABEL


def evidence_source_rules() -> dict[str, Any]:
    """Return a fresh copy of the fixed evidence-source rules. Pure."""
    return dict(EVIDENCE_SOURCE_RULES)


def pass_fail_bars() -> dict[str, Any]:
    """Return a fresh copy of the frozen pass/fail bars. Pure."""
    return dict(PASS_FAIL_BARS)


def candidate_eligibility() -> dict[str, Any]:
    """Return a fresh deep copy of the fixed candidate-eligibility rules. Pure."""
    return copy.deepcopy(CANDIDATE_ELIGIBILITY)


def rejection_rules() -> list[str]:
    """Return a fresh copy of the explicit rejection rules. Pure."""
    return list(REJECTION_RULES)


def record_fresh_evidence_validation_design(
    rc3_findings_decision: Any,
) -> dict[str, Any]:
    """Record the fresh-evidence validation design over the Block 189 findings decision.
    PURE: takes the decision dict (or None), returns a design dict. Never raises. The
    carried human decision is ALWAYS DO_NOT_PROMOTE; this contract has no promote branch,
    selects no successor, evaluates nothing, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(rc3_findings_decision, dict):
        blockers.append("rc3_findings_decision_missing")
        return _design(VERDICT_DESIGN_BLOCKED, blockers, risk_notes,
                       lessons_carried=[])

    fd = rc3_findings_decision

    fd_validation = validate_rc3_findings_human_decision(fd)
    if not fd_validation.get("valid"):
        blockers.append("rc3_findings_decision_invalid")
        blockers.extend("rc3:" + e for e in fd_validation.get("errors", []))

    if fd.get("verdict") != VERDICT_DECISION_RECORDED:
        blockers.append("rc3_findings_decision_not_recorded")

    if fd.get("thread_closed") is not True:
        blockers.append("resume_policy_thread_not_closed")

    if fd.get("fresh_evidence_required_for_reconsideration") is not True:
        blockers.append("fresh_evidence_requirement_not_recorded_upstream")

    if fd.get("human_decision") != DO_NOT_PROMOTE_RESUME_POLICY_YET:
        blockers.append("upstream_decision_not_do_not_promote")

    lessons_carried = [str(x) for x in (fd.get("lessons_recorded") or [])]

    risk_notes.append("criteria_frozen_before_any_qualifying_candle_exists")
    risk_notes.append("bars_anchor_to_committed_evidence_not_to_future_data")
    risk_notes.append("evaluation_is_a_future_separate_explicit_human_command")
    risk_notes.append("passing_qualifies_for_reconsideration_only_never_promotes")
    risk_notes.append("manual_csv_staging_only_no_fetch_ever")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    ready = (
        not blockers
        and fd.get("verdict") == VERDICT_DECISION_RECORDED
        and fd.get("thread_closed") is True
    )
    verdict = VERDICT_DESIGN_READY if ready else VERDICT_DESIGN_BLOCKED
    return _design(verdict, blockers, risk_notes, lessons_carried=lessons_carried)


def _design(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    lessons_carried: list[str],
) -> dict[str, Any]:
    """Assemble a fresh-evidence design dict carrying the read-only safety posture. This
    contract authorizes nothing: all gates stay BLOCKED/LOCKED unconditionally, the human
    decision is always DO_NOT_PROMOTE, and the frozen criteria can never be re-fitted."""
    return {
        "schema_version": DESIGN_SCHEMA_VERSION,
        "label": DESIGN_LABEL,
        "mode": DESIGN_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": DO_NOT_PROMOTE_RESUME_POLICY_YET,
        "approved_for_execution": False,
        "human_review_required": True,
        "successors_selected": False,
        # The frozen rulebook:
        "fresh_evidence_cutoff_date": FRESH_EVIDENCE_CUTOFF_DATE,
        "min_fresh_window_days": MIN_FRESH_WINDOW_DAYS,
        "preferred_fresh_window_days": PREFERRED_FRESH_WINDOW_DAYS,
        "evidence_source_rules": evidence_source_rules(),
        "pass_fail_bars": pass_fail_bars(),
        "candidate_eligibility": candidate_eligibility(),
        "rejection_rules": rejection_rules(),
        # Structurally True: the criteria are frozen by this contract and may never be
        # adjusted to fit data that arrives later.
        "criteria_frozen": True,
        "passing_promotes_nothing": True,
        "lessons_carried": list(lessons_carried),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        # Capability posture (this is a DESIGN; it evaluates / runs / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_evaluation": False,
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
        "authorizes_real_data_qa": False,
        "authorizes_baseline_backtest": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "promotes_resume_policy": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this design):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_fresh_evidence_validation_design(repo_root: str = ".") -> dict[str, Any]:
    """Load the Block 189 findings decision (which chains read-only through the persisted
    RC1/RC2 evidence) and record the design over it. Reads nothing itself beyond what the
    upstream chain reads; writes nothing; evaluates nothing; unlocks no gate."""
    decision = build_rc3_findings_human_decision(repo_root)
    design = record_fresh_evidence_validation_design(decision)
    design["rc3_findings_decision_verdict"] = decision.get("verdict")
    return design


def validate_fresh_evidence_validation_design(design: Any) -> dict[str, Any]:
    """Validate (read-only) a fresh-evidence design's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(design, dict):
        return {"valid": False, "errors": ["design_not_a_dict"]}
    d = design

    if d.get("verdict") not in (VERDICT_DESIGN_READY, VERDICT_DESIGN_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != DESIGN_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    if d.get("human_decision") != DO_NOT_PROMOTE_RESUME_POLICY_YET:
        errors.append("human_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("design_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("design_not_flagging_human_review")
    if d.get("successors_selected") is not False:
        errors.append("successor_policy_marked_selected")
    if d.get("criteria_frozen") is not True:
        errors.append("criteria_not_frozen")
    if d.get("passing_promotes_nothing") is not True:
        errors.append("pass_treated_as_promotion")

    if d.get("fresh_evidence_cutoff_date") != FRESH_EVIDENCE_CUTOFF_DATE:
        errors.append("bad_cutoff_date")
    try:
        if int(d.get("min_fresh_window_days", 0)) < 90:
            errors.append("min_window_below_floor")
    except (TypeError, ValueError):
        errors.append("min_window_not_an_int")

    src = d.get("evidence_source_rules") or {}
    if src.get("fetch_allowed") is not False:
        errors.append("source_rules_allow_fetch")
    if src.get("overlap_with_rc1_rc2_windows_allowed") is not False:
        errors.append("source_rules_allow_tainted_overlap")
    if src.get("bars_frozen_by_this_design") is not True:
        errors.append("source_rules_bars_not_frozen")

    bars = d.get("pass_fail_bars") or {}
    for key in ("min_total_return", "max_acceptable_drawdown", "min_sharpe_ratio",
                "stability_min_rank_top_half_all_categories", "all_bars_must_pass"):
        if key not in bars:
            errors.append("missing_bar:" + key)
    if bars.get("all_bars_must_pass") is not True:
        errors.append("partial_credit_allowed")

    elig = d.get("candidate_eligibility") or {}
    if set(elig.get("eligible_candidate_ids") or []) != set(_FIXED_CANDIDATE_IDS):
        errors.append("eligible_candidates_not_the_fixed_six")
    if elig.get("parameter_change_disqualifies") is not True:
        errors.append("parameter_change_not_disqualifying")

    rules = d.get("rejection_rules")
    if not isinstance(rules, list) or len(rules) < 5:
        errors.append("rejection_rules_incomplete")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_evaluation",
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
        "authorizes_real_data_qa",
        "authorizes_baseline_backtest",
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


def render_fresh_evidence_validation_design_markdown(design: Any) -> str:
    """Render a fresh-evidence design as deterministic markdown. Pure string work."""
    d = design if isinstance(design, dict) else {}
    bars = d.get("pass_fail_bars") or {}
    src = d.get("evidence_source_rules") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Fresh-Evidence Validation Design (DESIGN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(d.get("human_decision", "")))
    lines.append("- Criteria frozen: " + str(d.get("criteria_frozen", "")))
    lines.append("- Passing promotes nothing: " + str(d.get("passing_promotes_nothing", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Evidence source rules (fixed)")
    lines.append("- Source: " + str(src.get("source")))
    lines.append("- Window must start after: " + str(src.get("window_must_start_after")))
    lines.append("- Minimum window: " + str(d.get("min_fresh_window_days")) + " days"
                 + " (preferred " + str(d.get("preferred_fresh_window_days")) + ")")
    lines.append("- Overlap with RC1/RC2 windows allowed: "
                 + str(src.get("overlap_with_rc1_rc2_windows_allowed")))
    lines.append("- One evaluation per window, bars frozen: "
                 + str(src.get("evaluation_runs_once_per_window")))
    lines.append("")
    lines.append("## Pass/fail bars (frozen NOW, before the data exists)")
    lines.append("- Total return > " + str(bars.get("min_total_return")))
    lines.append("- Worst drawdown not worse than " + str(bars.get("max_acceptable_drawdown")))
    lines.append("- Sharpe >= " + str(bars.get("min_sharpe_ratio")))
    lines.append("- Stability: top half of the six fixed candidates on every category: "
                 + str(bars.get("stability_min_rank_top_half_all_categories")))
    lines.append("- ALL bars must pass: " + str(bars.get("all_bars_must_pass")))
    lines.append("")
    lines.append("## Candidate eligibility")
    elig = d.get("candidate_eligibility") or {}
    for cid in elig.get("eligible_candidate_ids") or []:
        lines.append("- " + str(cid))
    lines.append("- Parameter change disqualifies: "
                 + str(elig.get("parameter_change_disqualifies")))
    lines.append("- " + str(elig.get("rp4_rp5_have_no_special_status")))
    lines.append("")
    lines.append("## Rejection rules")
    for r in d.get("rejection_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Lessons carried from Block 189")
    for lesson in (d.get("lessons_carried") or ["(none)"]):
        lines.append("- " + str(lesson))
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
