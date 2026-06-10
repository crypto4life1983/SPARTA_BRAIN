"""Crypto-D1 V2 RC2 Cross-Policy Results Review Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the persisted RC2 cross-policy REPLAY
report for ``V2_trend_plus_cash_regime`` (all six fixed resume policies RP1..RP6,
parameters UNCHANGED, replayed over the four fixed out-of-sample windows) and renders a
HUMAN-REVIEW DECISION: are the replay results valid, did the RC1 evidence leader keep its
lead out of sample, and may any policy be promoted to execution -- or do the results merely
inform a human review?

It reads ONLY the local artifact
``reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json``
(read-only), re-validates its safety posture with the Block 185 runner's own validator,
summarizes every policy, and emits an explicit LEADERSHIP analysis that acknowledges the
flip on the committed evidence:
  - the RC1 leader (RP6 on the committed evidence) leads ZERO out-of-sample ranking
    categories -- its in-sample leadership did NOT survive out of sample;
  - other fixed candidates (RP4/RP5 on the committed evidence) lead every category and
    dominate the RC1 leader;
  - the flip is RESEARCH EVIDENCE ONLY: nothing is selected, promoted, or changed based on
    it -- choosing any successor policy would itself be a separate human research decision.

The promotion decision is ALWAYS DO_NOT_PROMOTE_RESUME_POLICY_YET; the observed leadership
instability REINFORCES it. This contract always carries a structural promotion blocker and
the gates stay LOCKED.

It RUNS NOTHING: no new replay, no simulation, no backtest, no optimization, no parameter
search, no broker/exchange, no network, no credentials, no real order, no file write.

Public API:
  - RC2_REVIEW_SCHEMA_VERSION / RC2_REVIEW_LABEL / RC2_REVIEW_MODE
  - RC2_REPLAY_REPORT_RELPATH / SELECTED_VARIANT_ID
  - VERDICT_RC2_REVIEW_COMPLETE / VERDICT_RC2_REVIEW_BLOCKED
  - DO_NOT_PROMOTE_RESUME_POLICY_YET / NEXT_REQUIRED_ACTION
  - get_rc2_cross_policy_results_review_label()
  - load_rc2_cross_policy_replay_report(repo_root)
  - review_rc2_cross_policy_results(report)
  - build_rc2_cross_policy_results_review_decision(repo_root)
  - validate_rc2_cross_policy_results_review_decision(decision)
  - render_rc2_cross_policy_results_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner import (
    RC2_REPLAY_LOG_DIR,
    VERDICT_REPLAYS_COMPLETE,
    validate_rc2_cross_policy_replay_report,
)

RC2_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract.v1"
)
RC2_REVIEW_LABEL = "Crypto-D1 V2 RC2 Cross-Policy Results Review (READ-ONLY)"
RC2_REVIEW_MODE = "RESEARCH_ONLY"

RC2_REPLAY_REPORT_RELPATH = os.path.join(
    RC2_REPLAY_LOG_DIR, "rc2_cross_policy_replay_report.json"
)

VERDICT_RC2_REVIEW_COMPLETE = "RC2_REVIEW_COMPLETE"
VERDICT_RC2_REVIEW_BLOCKED = "RC2_REVIEW_BLOCKED"

# After this review the ONLY next step is a human decision over the RC2 cross-policy
# evidence; no execution is authorized here.
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_RC2_CROSS_POLICY_EVIDENCE"

_STRUCTURAL_BLOCKER = "execution_promotion_requires_separate_human_review"


def get_rc2_cross_policy_results_review_label() -> str:
    """Human label for the recognized Crypto-D1 RC2 cross-policy results review contract."""
    return RC2_REVIEW_LABEL


def load_rc2_cross_policy_replay_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local RC2 replay report JSON read-only. Returns {found, report, path}.
    Never raises; a missing/corrupt file yields found=False."""
    path = os.path.join(repo_root, RC2_REPLAY_REPORT_RELPATH)
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
            "windows_evaluated": agg.get("windows_evaluated"),
        })
    return rows


def _leadership_analysis(report: dict[str, Any],
                         summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """Describe, purely from already-reported numbers, whether the RC1 leader kept its
    lead and which fixed candidates dominate it. Pure reporting -- this never selects,
    promotes, or changes anything."""
    ls = dict(report.get("leader_stability") or {})
    rankings = dict(report.get("rankings") or {})
    rc1_leader = ls.get("rc1_leader_policy_id")

    leader_row = next(
        (s for s in summaries if s.get("policy_id") == rc1_leader), None
    )
    dominating: list[str] = []
    if leader_row:
        for s in summaries:
            if s.get("policy_id") == rc1_leader:
                continue
            try:
                better = (
                    float(s["mean_total_return"]) > float(leader_row["mean_total_return"])
                    and float(s["worst_max_drawdown"]) > float(leader_row["worst_max_drawdown"])
                    and float(s["mean_sharpe_ratio"]) > float(leader_row["mean_sharpe_ratio"])
                )
            except (TypeError, ValueError, KeyError):
                better = False
            if better:
                dominating.append(str(s.get("policy_id")))

    return {
        "rc1_leader_policy_id": rc1_leader,
        "categories_led_by_rc1_leader": list(ls.get("categories_led_by_rc1_leader") or []),
        "rc1_leader_leads_all_categories": bool(ls.get("rc1_leader_leads_all_categories")),
        "rc1_leader_leads_any_category": bool(ls.get("rc1_leader_leads_any_category")),
        "leadership_flip_confirmed": (
            rc1_leader is not None and not ls.get("rc1_leader_leads_any_category")
        ),
        "current_category_leaders": rankings,
        "policies_dominating_rc1_leader": dominating,
    }


def review_rc2_cross_policy_results(report: Any) -> dict[str, Any]:
    """Score the RC2 replay report and render a human-review decision. PURE: takes a
    report dict (or None), returns a decision dict. Never raises. The promotion decision
    is ALWAYS DO_NOT_PROMOTE_RESUME_POLICY_YET -- the observed leadership instability
    reinforces it; promotion to execution is a separate human gate."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(report, dict):
        blockers.append("rc2_replay_report_missing")
        blockers.append(_STRUCTURAL_BLOCKER)
        return _decision(VERDICT_RC2_REVIEW_BLOCKED, blockers, risk_notes,
                         results_valid=False, policy_summaries=[],
                         leadership={}, rankings={})

    run_validation = validate_rc2_cross_policy_replay_report(report)
    results_valid = bool(run_validation.get("valid"))
    if not results_valid:
        blockers.append("rc2_replay_safety_invalid")
        blockers.extend("replay:" + e for e in run_validation.get("errors", []))

    complete = report.get("verdict") == VERDICT_REPLAYS_COMPLETE
    if not complete:
        blockers.append("rc2_replay_not_complete")

    summaries = _policy_summaries(report)
    if not summaries:
        blockers.append("no_policy_results")

    # Real-order safety: no policy/window may have placed a real order.
    for p in report.get("policy_results") or []:
        for wr in p.get("window_results") or []:
            m = wr.get("metrics") or {}
            if (m.get("real_orders_placed", 0) or 0) != 0:
                blockers.append("real_orders_detected:" + str(p.get("policy_id")))

    if report.get("policy_parameters_changed") is not False:
        blockers.append("policy_parameters_changed")

    leadership = _leadership_analysis(report, summaries)

    # Honest acknowledgment annotations (risk notes, never selection or promotion).
    if leadership.get("leadership_flip_confirmed"):
        risk_notes.append("rc1_leader_leads_zero_oos_categories")
        risk_notes.append("in_sample_leadership_did_not_survive_out_of_sample")
        for pid in leadership.get("policies_dominating_rc1_leader") or []:
            risk_notes.append("policy_dominates_rc1_leader_out_of_sample:" + pid)
    elif leadership.get("rc1_leader_leads_all_categories"):
        risk_notes.append("rc1_leader_kept_full_lead_out_of_sample")
    elif leadership.get("rc1_leader_leads_any_category"):
        risk_notes.append("rc1_leader_kept_partial_lead_out_of_sample")

    risk_notes.append("rankings_are_research_evidence_only_not_selection")
    risk_notes.append("choosing_any_successor_policy_is_a_separate_human_decision")
    risk_notes.append("oos_evidence_supports_keeping_do_not_promote")
    risk_notes.append("simulated_evidence_only_not_execution_validated")
    risk_notes.append("human_review_required_before_any_execution_promotion")

    # Structural promotion boundary: RC2 results NEVER auto-promote to execution.
    blockers.append(_STRUCTURAL_BLOCKER)

    structural_only = blockers == [_STRUCTURAL_BLOCKER]
    verdict = (
        VERDICT_RC2_REVIEW_COMPLETE
        if (results_valid and complete and structural_only)
        else VERDICT_RC2_REVIEW_BLOCKED
    )
    return _decision(verdict, blockers, risk_notes, results_valid=results_valid,
                     policy_summaries=summaries, leadership=leadership,
                     rankings=dict(report.get("rankings") or {}))


def _decision(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    results_valid: bool,
    policy_summaries: list[dict[str, Any]],
    leadership: dict[str, Any],
    rankings: dict[str, Any],
) -> dict[str, Any]:
    """Assemble an RC2 results decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally and
    the promotion decision is always DO_NOT_PROMOTE -- the review is evidence only."""
    return {
        "schema_version": RC2_REVIEW_SCHEMA_VERSION,
        "label": RC2_REVIEW_LABEL,
        "mode": RC2_REVIEW_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "results_valid": results_valid,
        "promotion_decision": DO_NOT_PROMOTE_RESUME_POLICY_YET,
        "approved_for_execution": False,
        "human_review_required": True,
        "policy_summaries": list(policy_summaries),
        "leadership_analysis": dict(leadership),
        "rankings": dict(rankings),
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
        # Gate posture (UNCHANGED by this review):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_rc2_cross_policy_results_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local RC2 replay report read-only and review it. Reads one file; writes
    nothing; runs no replay; unlocks no gate."""
    loaded = load_rc2_cross_policy_replay_report(repo_root)
    decision = review_rc2_cross_policy_results(loaded["report"])
    decision["rc2_replay_report_found"] = loaded["found"]
    decision["rc2_replay_report_path"] = loaded["path"]
    return decision


def validate_rc2_cross_policy_results_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) an RC2 results decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_RC2_REVIEW_COMPLETE, VERDICT_RC2_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != RC2_REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # The promotion decision is structurally always DO_NOT_PROMOTE and never approves
    # execution.
    if d.get("promotion_decision") != DO_NOT_PROMOTE_RESUME_POLICY_YET:
        errors.append("promotion_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("decision_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("decision_not_flagging_human_review")

    # Every review must carry the structural promotion blocker.
    if _STRUCTURAL_BLOCKER not in (d.get("blockers") or []):
        errors.append("missing_structural_promotion_blocker")

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


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_rc2_cross_policy_results_review_markdown(decision: Any) -> str:
    """Render an RC2 results decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    la = d.get("leadership_analysis") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC2 Cross-Policy Results Review")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Results valid: " + str(d.get("results_valid", "")))
    lines.append("- Promotion decision: " + str(d.get("promotion_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Human review required: " + str(d.get("human_review_required", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Leadership analysis (research evidence only, NOT a selection)")
    lines.append("- RC1 leader: " + str(la.get("rc1_leader_policy_id")))
    lines.append("- Categories led out of sample: "
                 + (", ".join(la.get("categories_led_by_rc1_leader") or []) or "(none)"))
    lines.append("- Leadership flip confirmed: " + str(la.get("leadership_flip_confirmed")))
    lines.append("- Policies dominating the RC1 leader: "
                 + (", ".join(la.get("policies_dominating_rc1_leader") or []) or "(none)"))
    rk = la.get("current_category_leaders") or {}
    if rk:
        lines.append("- Best by mean return: " + str(rk.get("best_by_mean_return")))
        lines.append("- Best by worst drawdown: " + str(rk.get("best_by_worst_drawdown")))
        lines.append("- Best by mean Sharpe: " + str(rk.get("best_by_mean_sharpe")))
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
