"""Crypto-D1 V2 Resume-Policy Results Review / Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the completed local resume-policy
SIMULATION report for ``V2_trend_plus_cash_regime`` (six fixed policies RP1..RP6 across
four fixed regime sub-windows) and renders a HUMAN-REVIEW DECISION: are the simulated
results valid, which policy currently leads on the evidence, and may any policy be promoted
to paper/live EXECUTION -- or do the results merely inform a human review?

It reads ONLY the local artifact
``reports/crypto_d1_resume_policy_sim/resume_policy_sim_report.json`` (read-only),
re-validates its safety posture with the runner's own validator, ranks the policies, and
emits:
  - a review verdict;
  - an evidence-leading policy summary (currently RP6 on the committed evidence);
  - an explicit promotion decision that is ALWAYS DO_NOT_PROMOTE_RESUME_POLICY_YET;
  - hard blockers and non-blocking risk notes.

The decision boundary is deliberate: resume-policy simulation results are RESEARCH EVIDENCE
ONLY. Even the leading policy is NOT promoted to execution here -- promoting any policy to a
real paper/micro-live/live run is a SEPARATE human gate. This contract therefore always
carries a structural promotion blocker and the gates stay LOCKED.

It RUNS NOTHING: no new simulation, no backtest, no optimization, no parameter search, no
broker/exchange, no network, no credentials, no real order. It UNLOCKS no gate:
paper_trading_gate, micro_live_gate and the live gate all stay LOCKED.

Public API:
  - RESULTS_REVIEW_SCHEMA_VERSION / RESULTS_REVIEW_LABEL / RESULTS_REVIEW_MODE
  - RESUME_SIM_REPORT_RELPATH / SELECTED_VARIANT_ID
  - VERDICT_REVIEW_COMPLETE / VERDICT_REVIEW_BLOCKED
  - PROMOTE_RESUME_POLICY_FOR_EXECUTION / DO_NOT_PROMOTE_RESUME_POLICY_YET
  - RESULTS_REVIEW_CRITERIA / NEXT_REQUIRED_ACTION
  - get_resume_policy_results_review_label()
  - results_review_criteria()
  - load_resume_policy_simulation_report(repo_root)
  - review_resume_policy_results(report)
  - build_resume_policy_results_review_decision(repo_root)
  - validate_resume_policy_results_review_decision(decision)
  - render_resume_policy_results_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner import (
    RESUME_SIM_LOG_DIR,
    VERDICT_RERUNS_COMPLETE,
    validate_resume_policy_simulation_report,
)

RESULTS_REVIEW_SCHEMA_VERSION = "strategy_factory_crypto_d1_resume_policy_results_review_contract.v1"
RESULTS_REVIEW_LABEL = "Crypto-D1 V2 Resume-Policy Results Review / Decision (READ-ONLY)"
RESULTS_REVIEW_MODE = "RESEARCH_ONLY"

RESUME_SIM_REPORT_RELPATH = os.path.join(RESUME_SIM_LOG_DIR, "resume_policy_sim_report.json")

VERDICT_REVIEW_COMPLETE = "REVIEW_COMPLETE"
VERDICT_REVIEW_BLOCKED = "REVIEW_BLOCKED"

PROMOTE_RESUME_POLICY_FOR_EXECUTION = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
DO_NOT_PROMOTE_RESUME_POLICY_YET = "DO_NOT_PROMOTE_RESUME_POLICY_YET"

# After this review the ONLY next step is a human reading the resume-policy evidence; no
# execution is authorized here.
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_RESUME_POLICY_SIMULATION_RESULTS"

# Advisory bar describing what a STRONG resume-policy candidate would look like. Used to
# annotate the leading policy with risk notes -- NEVER to auto-promote it to execution.
RESULTS_REVIEW_CRITERIA: dict[str, Any] = {
    "min_regimes_evaluated": 4,
    "max_acceptable_worst_drawdown": -0.50,
    "min_mean_sharpe_ratio": 0.50,
    "require_all_real_orders_zero": True,
    "require_no_optimization": True,
}


def get_resume_policy_results_review_label() -> str:
    """Human label for the recognized Crypto-D1 resume-policy results review contract."""
    return RESULTS_REVIEW_LABEL


def results_review_criteria() -> dict[str, Any]:
    """Return a fresh copy of the advisory results-review criteria. Pure."""
    return dict(RESULTS_REVIEW_CRITERIA)


def load_resume_policy_simulation_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local resume-policy simulation report JSON read-only. Returns
    {found, report, path}. Never raises; a missing/corrupt file yields found=False."""
    path = os.path.join(repo_root, RESUME_SIM_REPORT_RELPATH)
    if not os.path.isfile(path):
        return {"found": False, "report": None, "path": path}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"found": True, "report": json.load(fh), "path": path}
    except (OSError, ValueError):
        return {"found": False, "report": None, "path": path}


def _policy_summaries(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten each policy's aggregate into a compact summary row. Pure."""
    rows: list[dict[str, Any]] = []
    for p in report.get("policy_results") or []:
        agg = p.get("aggregate") or {}
        rows.append({
            "policy_id": p.get("policy_id"),
            "reentry_exposure": p.get("reentry_exposure"),
            "mean_total_return": agg.get("mean_total_return"),
            "min_total_return": agg.get("min_total_return"),
            "worst_max_drawdown": agg.get("worst_max_drawdown"),
            "mean_sharpe_ratio": agg.get("mean_sharpe_ratio"),
            "regimes_evaluated": agg.get("regimes_evaluated"),
        })
    return rows


def _leading_policy(report: dict[str, Any]) -> dict[str, Any]:
    """Identify the evidence-leading policy from the report's rankings: the policy that
    leads the most ranking categories (return / drawdown / Sharpe). Pure; reporting only --
    this NEVER changes any parameter and NEVER promotes the policy."""
    rankings = report.get("rankings") or {}
    cats = ["best_by_mean_return", "best_by_worst_drawdown", "best_by_mean_sharpe"]
    tally: dict[str, list[str]] = {}
    for c in cats:
        pid = rankings.get(c)
        if pid:
            tally.setdefault(pid, []).append(c)
    if not tally:
        return {"policy_id": None, "categories_led": [], "leads_all_categories": False}
    leader = max(tally.items(), key=lambda kv: len(kv[1]))
    pid, cats_led = leader
    summary = next((s for s in _policy_summaries(report) if s["policy_id"] == pid), {})
    return {
        "policy_id": pid,
        "categories_led": list(cats_led),
        "leads_all_categories": len(cats_led) == len(cats),
        "aggregate": summary,
    }


def review_resume_policy_results(report: Any) -> dict[str, Any]:
    """Score the resume-policy simulation report and render a human-review decision. PURE:
    takes a report dict (or None), returns a decision dict. Never raises. The promotion
    decision is ALWAYS DO_NOT_PROMOTE_RESUME_POLICY_YET -- these results are research
    evidence only; promotion to execution is a separate human gate."""
    crit = results_review_criteria()
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(report, dict):
        blockers.append("resume_policy_sim_report_missing")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_PROMOTE_RESUME_POLICY_YET,
                         blockers, risk_notes, crit, results_valid=False,
                         leading=_leading_policy({}), policy_summaries=[])

    run_validation = validate_resume_policy_simulation_report(report)
    results_valid = bool(run_validation.get("valid"))
    if not results_valid:
        blockers.append("resume_policy_sim_safety_invalid")
        blockers.extend("sim:" + e for e in run_validation.get("errors", []))

    complete = report.get("verdict") == VERDICT_RERUNS_COMPLETE
    if not complete:
        blockers.append("resume_policy_sim_not_complete")

    summaries = _policy_summaries(report)
    if not summaries:
        blockers.append("no_policy_results")

    # Real-order safety: no policy/regime may have placed a real order.
    for p in report.get("policy_results") or []:
        for rr in p.get("regime_results") or []:
            m = rr.get("metrics") or {}
            if (m.get("real_orders_placed", 0) or 0) != 0:
                blockers.append("real_orders_detected:" + str(p.get("policy_id")))

    leading = _leading_policy(report)

    # Advisory annotations on the leading policy (risk notes, never auto-promotion).
    agg = leading.get("aggregate") or {}
    if agg:
        worst_dd = float(agg.get("worst_max_drawdown", 0.0) or 0.0)
        mean_sharpe = float(agg.get("mean_sharpe_ratio", 0.0) or 0.0)
        regimes = int(agg.get("regimes_evaluated", 0) or 0)
        if worst_dd < float(crit["max_acceptable_worst_drawdown"]):
            risk_notes.append("leading_policy_worst_drawdown_breaches_hard_kill")
        if mean_sharpe < float(crit["min_mean_sharpe_ratio"]):
            risk_notes.append("leading_policy_mean_sharpe_below_advisory_minimum")
        if regimes < int(crit["min_regimes_evaluated"]):
            risk_notes.append("fewer_regimes_than_advisory_minimum")
    if leading.get("policy_id"):
        risk_notes.append("evidence_leading_policy:" + str(leading["policy_id"]))
    risk_notes.append("simulated_evidence_only_not_execution_validated")
    risk_notes.append("human_review_required_before_any_execution_promotion")

    # Structural promotion boundary: resume-policy results NEVER auto-promote to execution.
    blockers.append("execution_promotion_requires_separate_human_review")

    verdict = VERDICT_REVIEW_COMPLETE if (results_valid and complete) else VERDICT_REVIEW_BLOCKED
    return _decision(verdict, DO_NOT_PROMOTE_RESUME_POLICY_YET, blockers, risk_notes, crit,
                     results_valid=results_valid, leading=leading, policy_summaries=summaries,
                     rankings=report.get("rankings") or {})


def _decision(
    verdict: str,
    promotion_decision: str,
    blockers: list[str],
    risk_notes: list[str],
    criteria: dict[str, Any],
    *,
    results_valid: bool,
    leading: dict[str, Any],
    policy_summaries: list[dict[str, Any]],
    rankings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble a resume-policy results decision dict carrying the read-only safety posture.
    This contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally,
    and the promotion decision is always a recommendation to HUMAN-REVIEW, never an
    execution authorization."""
    promoted = (promotion_decision == PROMOTE_RESUME_POLICY_FOR_EXECUTION) and not blockers
    return {
        "schema_version": RESULTS_REVIEW_SCHEMA_VERSION,
        "label": RESULTS_REVIEW_LABEL,
        "mode": RESULTS_REVIEW_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "results_valid": results_valid,
        "promotion_decision": promotion_decision,
        "approved_for_execution": promoted,
        "human_review_required": not promoted,
        "evidence_leading_policy": leading,
        "policy_summaries": list(policy_summaries),
        "rankings": dict(rankings or {}),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "results_review_criteria": dict(criteria),
        # Capability posture (this contract executes / authorizes nothing live):
        "executes": False,
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
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this review):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_resume_policy_results_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local resume-policy simulation report read-only and review it. Reads one
    file; writes nothing; runs no simulation; unlocks no gate."""
    loaded = load_resume_policy_simulation_report(repo_root)
    decision = review_resume_policy_results(loaded["report"])
    decision["resume_policy_sim_report_found"] = loaded["found"]
    decision["resume_policy_sim_report_path"] = loaded["path"]
    return decision


def validate_resume_policy_results_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a resume-policy results decision's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_REVIEW_COMPLETE, VERDICT_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("promotion_decision") not in (PROMOTE_RESUME_POLICY_FOR_EXECUTION,
                                           DO_NOT_PROMOTE_RESUME_POLICY_YET):
        errors.append("bad_promotion_decision")
    if d.get("schema_version") != RESULTS_REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    if d.get("promotion_decision") == DO_NOT_PROMOTE_RESUME_POLICY_YET:
        if d.get("approved_for_execution") is not False:
            errors.append("blocked_decision_marked_approved")
        if d.get("human_review_required") is not True:
            errors.append("blocked_decision_not_flagging_human_review")
    if d.get("promotion_decision") == PROMOTE_RESUME_POLICY_FOR_EXECUTION:
        if d.get("blockers") or []:
            errors.append("promoted_with_blockers")
        if d.get("approved_for_execution") is not True:
            errors.append("promoted_without_approval_flag")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
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
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if d.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_resume_policy_results_review_markdown(decision: Any) -> str:
    """Render a resume-policy results decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lead = d.get("evidence_leading_policy") or {}
    lead_agg = lead.get("aggregate") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Resume-Policy Results Review / Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Results valid: " + str(d.get("results_valid", "")))
    lines.append("- Promotion decision: " + str(d.get("promotion_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Human review required: " + str(d.get("human_review_required", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Evidence-leading policy")
    lines.append("- Policy: " + str(lead.get("policy_id")))
    lines.append("- Leads categories: " + ", ".join(lead.get("categories_led") or []))
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
