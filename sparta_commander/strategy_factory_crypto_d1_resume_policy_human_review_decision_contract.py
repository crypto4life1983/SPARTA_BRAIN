"""Crypto-D1 V2 Resume-Policy HUMAN REVIEW Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that RECORDS a human's review decision over the
completed resume-policy SIMULATION results for ``V2_trend_plus_cash_regime``. It is the
human-judgment companion to the automated Block 177 results-review contract: where Block
177 mechanically scores the simulation report and prepares a decision, THIS contract
captures the human's reviewed verdict on that evidence and the human's chosen research
direction.

It consumes the Block 177 reviewer output (which itself reads only
``reports/crypto_d1_resume_policy_sim/resume_policy_sim_report.json`` read-only), re-validates
it with Block 177's own validator, and emits a human-review record that:
  - acknowledges the evidence-leading policy (RP6 on the committed evidence) and whether it
    leads every ranking category;
  - records the human decision, which is ALWAYS ``DO_NOT_PROMOTE_RESUME_POLICY_YET``;
  - records a recommended research direction (continue research / require further validation
    / require a separate explicit approval) -- a recommendation only, never an unlock;
  - DESCRIBES, as inert metadata, the separate later approval path a human would have to
    follow in a FUTURE, separate contract to ever promote -- defining that path here does
    NOT authorize it and does NOT change the DO_NOT_PROMOTE decision;
  - carries the reviewer's blockers/risk notes forward for traceability.

It RUNS NOTHING and WRITES NOTHING: no new simulation, no backtest, no optimization, no
parameter search, no broker/exchange, no network, no credentials, no real order, no file
write. It UNLOCKS no gate: paper_trading_gate, micro_live_gate and the live gate all stay
LOCKED. Promoting any resume policy to a real paper/micro-live/live run remains a SEPARATE,
explicit, future human command -- this contract never performs or authorizes it.

Public API:
  - HUMAN_REVIEW_SCHEMA_VERSION / HUMAN_REVIEW_LABEL / HUMAN_REVIEW_MODE
  - VERDICT_HUMAN_REVIEW_RECORDED / VERDICT_HUMAN_REVIEW_BLOCKED
  - DECISION_DO_NOT_PROMOTE
  - RECOMMEND_CONTINUE_RESEARCH / RECOMMEND_FURTHER_VALIDATION
  - RECOMMEND_SEPARATE_EXPLICIT_APPROVAL / RECOMMENDED_PATHS
  - SEPARATE_APPROVAL_PATH / NEXT_REQUIRED_ACTION / SELECTED_VARIANT_ID
  - get_resume_policy_human_review_decision_label()
  - recommended_paths()
  - separate_approval_path()
  - record_human_review_decision(results_review_decision, *, recommended_path=...)
  - build_resume_policy_human_review_decision(repo_root, *, recommended_path=...)
  - validate_resume_policy_human_review_decision(decision)
  - render_resume_policy_human_review_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
    VERDICT_REVIEW_COMPLETE,
    build_resume_policy_results_review_decision,
    validate_resume_policy_results_review_decision,
)

HUMAN_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_resume_policy_human_review_decision_contract.v1"
)
HUMAN_REVIEW_LABEL = "Crypto-D1 V2 Resume-Policy Human Review Decision (READ-ONLY)"
HUMAN_REVIEW_MODE = "RESEARCH_ONLY"

VERDICT_HUMAN_REVIEW_RECORDED = "HUMAN_REVIEW_RECORDED"
VERDICT_HUMAN_REVIEW_BLOCKED = "HUMAN_REVIEW_BLOCKED"

# The human decision recordable here is, by design, ALWAYS this single value. There is no
# promote branch: promoting to execution is a separate, future, explicit human command and
# is never expressible through this contract.
DECISION_DO_NOT_PROMOTE = DO_NOT_PROMOTE_RESUME_POLICY_YET

# Recommended research directions the human may record. All are research-only; none unlocks
# a gate or authorizes execution.
RECOMMEND_CONTINUE_RESEARCH = "CONTINUE_RESEARCH"
RECOMMEND_FURTHER_VALIDATION = "REQUIRE_FURTHER_VALIDATION"
RECOMMEND_SEPARATE_EXPLICIT_APPROVAL = "REQUIRE_SEPARATE_EXPLICIT_APPROVAL"
RECOMMENDED_PATHS: tuple[str, ...] = (
    RECOMMEND_CONTINUE_RESEARCH,
    RECOMMEND_FURTHER_VALIDATION,
    RECOMMEND_SEPARATE_EXPLICIT_APPROVAL,
)

# Inert, descriptive metadata: the steps a human would have to take in a FUTURE, SEPARATE
# contract to ever consider promoting a resume policy to real money. Defining the path here
# documents it; it does NOT authorize it, does NOT unlock any gate, and does NOT change the
# DO_NOT_PROMOTE decision this contract records.
SEPARATE_APPROVAL_PATH: dict[str, Any] = {
    "is_authorization": False,
    "unlocks_any_gate": False,
    "required_future_steps": [
        "human_issues_a_distinct_explicit_promotion_command_in_a_separate_contract",
        "independent_out_of_sample_or_forward_validation_of_the_leading_policy",
        "explicit_human_sign_off_recorded_against_that_separate_contract",
        "only_then_a_separate_gate_unlock_decision_is_even_considered",
    ],
    "note": (
        "This path is documentation only. No step here is performed or authorized by this "
        "contract; paper/micro-live/live gates stay LOCKED until a separate human command."
    ),
}

# After this human review is recorded, the only next step remains research-only: either keep
# researching or, in a SEPARATE future contract, request an explicit human approval. Nothing
# here is an execution authorization.
NEXT_REQUIRED_ACTION = "CONTINUE_RESEARCH_OR_REQUEST_SEPARATE_HUMAN_APPROVAL"


def get_resume_policy_human_review_decision_label() -> str:
    """Human label for the recognized Crypto-D1 resume-policy human review decision contract."""
    return HUMAN_REVIEW_LABEL


def recommended_paths() -> tuple[str, ...]:
    """Return the allowed recommended research directions. Pure."""
    return RECOMMENDED_PATHS


def separate_approval_path() -> dict[str, Any]:
    """Return a fresh copy of the inert, descriptive separate-approval-path metadata. Pure;
    authorizes nothing and unlocks nothing."""
    path = dict(SEPARATE_APPROVAL_PATH)
    path["required_future_steps"] = list(SEPARATE_APPROVAL_PATH["required_future_steps"])
    return path


def record_human_review_decision(
    results_review_decision: Any,
    *,
    recommended_path: str = RECOMMEND_SEPARATE_EXPLICIT_APPROVAL,
) -> dict[str, Any]:
    """Record a human's review decision over the Block 177 results-review decision. PURE:
    takes the reviewer decision dict (or None) plus the human's recommended research
    direction, returns a human-review record. Never raises. The recorded human decision is
    ALWAYS ``DECISION_DO_NOT_PROMOTE``; this contract has no promote branch and unlocks
    nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if recommended_path not in RECOMMENDED_PATHS:
        blockers.append("invalid_recommended_path:" + str(recommended_path))
        recommended_path_value: str | None = None
    else:
        recommended_path_value = recommended_path

    if not isinstance(results_review_decision, dict):
        blockers.append("results_review_decision_missing")
        return _decision(
            VERDICT_HUMAN_REVIEW_BLOCKED, blockers, risk_notes,
            recommended_path=recommended_path_value, leading={},
            policy_summaries=[], review_blockers=[], report_found=False,
        )

    rd = results_review_decision

    review_validation = validate_resume_policy_results_review_decision(rd)
    if not review_validation.get("valid"):
        blockers.append("results_review_decision_invalid")
        blockers.extend("review:" + e for e in review_validation.get("errors", []))

    if rd.get("verdict") != VERDICT_REVIEW_COMPLETE:
        blockers.append("results_review_not_complete")

    if rd.get("resume_policy_sim_report_found") is not True:
        blockers.append("resume_policy_sim_report_missing")

    leading = dict(rd.get("evidence_leading_policy") or {})
    summaries = list(rd.get("policy_summaries") or [])
    review_blockers = list(rd.get("blockers") or [])

    # Acknowledge the evidence-leading policy. Recording it is descriptive only; it never
    # promotes the policy.
    leader_id = leading.get("policy_id")
    if leader_id:
        risk_notes.append("acknowledged_evidence_leading_policy:" + str(leader_id))
        if leading.get("leads_all_categories") is True:
            risk_notes.append("evidence_leading_policy_leads_all_categories")
        else:
            risk_notes.append("evidence_leading_policy_does_not_lead_all_categories")
    else:
        risk_notes.append("no_evidence_leading_policy_identified")

    # Carry the reviewer's own risk notes forward for human traceability.
    for note in rd.get("risk_notes") or []:
        risk_notes.append("review_note:" + str(note))

    risk_notes.append("human_decision_is_research_only_not_execution_validated")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    recorded = (
        not blockers
        and rd.get("verdict") == VERDICT_REVIEW_COMPLETE
        and rd.get("resume_policy_sim_report_found") is True
    )
    verdict = VERDICT_HUMAN_REVIEW_RECORDED if recorded else VERDICT_HUMAN_REVIEW_BLOCKED
    return _decision(
        verdict, blockers, risk_notes, recommended_path=recommended_path_value,
        leading=leading, policy_summaries=summaries, review_blockers=review_blockers,
        report_found=bool(rd.get("resume_policy_sim_report_found")),
    )


def _decision(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    recommended_path: str | None,
    leading: dict[str, Any],
    policy_summaries: list[dict[str, Any]],
    review_blockers: list[str],
    report_found: bool,
) -> dict[str, Any]:
    """Assemble a human-review decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally, the
    human decision is always DO_NOT_PROMOTE, and the recommended path is a research direction
    only -- never an execution authorization."""
    return {
        "schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "label": HUMAN_REVIEW_LABEL,
        "mode": HUMAN_REVIEW_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": DECISION_DO_NOT_PROMOTE,
        "approved_for_execution": False,
        "human_review_required": True,
        "recommended_path": recommended_path,
        "evidence_leading_policy": dict(leading),
        "policy_summaries": list(policy_summaries),
        "review_blockers": list(review_blockers),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "separate_approval_path": separate_approval_path(),
        "resume_policy_sim_report_found": report_found,
        # Capability posture (this contract executes / authorizes / writes nothing live):
        "executes": False,
        "writes_files": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
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
        # Gate posture (UNCHANGED by this review):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_resume_policy_human_review_decision(
    repo_root: str = ".",
    *,
    recommended_path: str = RECOMMEND_SEPARATE_EXPLICIT_APPROVAL,
) -> dict[str, Any]:
    """Load the Block 177 results-review decision (which reads the local simulation report
    read-only) and record a human review over it. Reads nothing itself beyond what Block 177
    reads; writes nothing; runs no simulation; unlocks no gate."""
    review_decision = build_resume_policy_results_review_decision(repo_root)
    decision = record_human_review_decision(
        review_decision, recommended_path=recommended_path
    )
    decision["resume_policy_sim_report_path"] = review_decision.get(
        "resume_policy_sim_report_path"
    )
    decision["results_review_verdict"] = review_decision.get("verdict")
    return decision


def validate_resume_policy_human_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a human-review decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_HUMAN_REVIEW_RECORDED, VERDICT_HUMAN_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != HUMAN_REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # The human decision is structurally always DO_NOT_PROMOTE and never approves execution.
    if d.get("human_decision") != DECISION_DO_NOT_PROMOTE:
        errors.append("human_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("decision_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("decision_not_flagging_human_review")

    # A recorded review must carry a valid recommended path; a blocked one may carry None.
    if d.get("verdict") == VERDICT_HUMAN_REVIEW_RECORDED:
        if d.get("recommended_path") not in RECOMMENDED_PATHS:
            errors.append("recorded_without_valid_recommended_path")
        if d.get("blockers") or []:
            errors.append("recorded_with_blockers")
    elif d.get("recommended_path") is not None and (
        d.get("recommended_path") not in RECOMMENDED_PATHS
    ):
        errors.append("bad_recommended_path")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "ran_parameter_search",
        "parameters_changed_based_on_results",
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

    # The documented separate-approval path must itself be inert.
    sap = d.get("separate_approval_path") or {}
    if sap.get("is_authorization") is not False:
        errors.append("separate_approval_path_claims_authorization")
    if sap.get("unlocks_any_gate") is not False:
        errors.append("separate_approval_path_claims_unlock")

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_resume_policy_human_review_decision_markdown(decision: Any) -> str:
    """Render a human-review decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lead = d.get("evidence_leading_policy") or {}
    lead_agg = lead.get("aggregate") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Resume-Policy Human Review Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Human decision: " + str(d.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Human review required: " + str(d.get("human_review_required", "")))
    lines.append("- Recommended path: " + str(d.get("recommended_path", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Evidence-leading policy (research evidence only)")
    lines.append("- Policy: " + str(lead.get("policy_id")))
    lines.append("- Leads categories: " + ", ".join(lead.get("categories_led") or []))
    lines.append("- Leads all categories: " + str(lead.get("leads_all_categories")))
    if lead_agg:
        lines.append("- Mean return: " + _pct(lead_agg.get("mean_total_return"))
                     + " | Worst drawdown: " + _pct(lead_agg.get("worst_max_drawdown"))
                     + " | Mean Sharpe: " + f"{float(lead_agg.get('mean_sharpe_ratio', 0) or 0):.2f}")
    lines.append("")
    lines.append("## All policies (research evidence only)")
    for s in d.get("policy_summaries") or []:
        lines.append("- " + str(s.get("policy_id")) + ": mean " + _pct(s.get("mean_total_return"))
                     + ", worstDD " + _pct(s.get("worst_max_drawdown"))
                     + ", Sharpe " + f"{float(s.get('mean_sharpe_ratio', 0) or 0):.2f}")
    lines.append("")
    lines.append("## Blockers")
    for b in (d.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Carried-forward review blockers")
    for b in (d.get("review_blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in d.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Separate approval path (documentation only, authorizes nothing)")
    sap = d.get("separate_approval_path") or {}
    lines.append("- Is authorization: " + str(sap.get("is_authorization")))
    lines.append("- Unlocks any gate: " + str(sap.get("unlocks_any_gate")))
    for step in sap.get("required_future_steps") or []:
        lines.append("  - " + str(step))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- authorizes_paper_execution: False (separate human gate + command required)")
    return "\n".join(lines)
