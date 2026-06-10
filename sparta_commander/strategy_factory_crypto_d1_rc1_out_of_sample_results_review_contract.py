"""Crypto-D1 V2 RC1 Out-of-Sample Results Review Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the persisted RC1 out-of-sample REPLAY
report for ``V2_trend_plus_cash_regime`` (the evidence-leading resume policy RP6, parameters
UNCHANGED, replayed over the four fixed Block 180 windows) and renders a HUMAN-REVIEW
DECISION: are the replay results valid, how did the policy hold up out of sample versus the
in-sample evidence, and may it be promoted to execution -- or do the results merely inform a
human review?

It reads ONLY the local artifact
``reports/crypto_d1_rc1_out_of_sample_replay/rc1_oos_replay_report.json`` (read-only),
re-validates its safety posture with the Block 181 runner's own validator, summarizes each
window, computes an explicit DEGRADATION comparison against the carried in-sample reference,
and emits:
  - a review verdict;
  - per-window evidence summaries (held-out vs boundary-straddle, honestly typed);
  - a degradation analysis acknowledging that RP6 produced USEFUL out-of-sample evidence
    (it survived the truly held-out 2020 window) but performed MATERIALLY WORSE than the
    in-sample aggregate;
  - an explicit promotion decision that is ALWAYS DO_NOT_PROMOTE_RESUME_POLICY_YET;
  - hard blockers and non-blocking risk notes.

The decision boundary is deliberate: RC1 replay results are RESEARCH EVIDENCE ONLY. The
observed out-of-sample degradation REINFORCES the standing DO_NOT_PROMOTE decision; nothing
here approves paper, micro-live, live, broker, exchange, or execution. This contract
therefore always carries a structural promotion blocker and the gates stay LOCKED.

It RUNS NOTHING: no new replay, no simulation, no backtest, no optimization, no parameter
search, no broker/exchange, no network, no credentials, no real order, no file write.

Public API:
  - RC1_REVIEW_SCHEMA_VERSION / RC1_REVIEW_LABEL / RC1_REVIEW_MODE
  - RC1_REPLAY_REPORT_RELPATH / SELECTED_VARIANT_ID
  - VERDICT_RC1_REVIEW_COMPLETE / VERDICT_RC1_REVIEW_BLOCKED
  - DO_NOT_PROMOTE_RESUME_POLICY_YET / RC1_REVIEW_CRITERIA / NEXT_REQUIRED_ACTION
  - get_rc1_oos_results_review_label()
  - rc1_review_criteria()
  - load_rc1_oos_replay_report(repo_root)
  - review_rc1_oos_results(report)
  - build_rc1_oos_results_review_decision(repo_root)
  - validate_rc1_oos_results_review_decision(decision)
  - render_rc1_oos_results_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
import statistics
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner import (
    RC1_REPLAY_LOG_DIR,
    VERDICT_REPLAYS_COMPLETE,
    validate_rc1_out_of_sample_replay_report,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract import (
    WINDOW_TYPE_HELD_OUT,
)

RC1_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc1_out_of_sample_results_review_contract.v1"
)
RC1_REVIEW_LABEL = "Crypto-D1 V2 RC1 Out-of-Sample Results Review (READ-ONLY)"
RC1_REVIEW_MODE = "RESEARCH_ONLY"

RC1_REPLAY_REPORT_RELPATH = os.path.join(RC1_REPLAY_LOG_DIR, "rc1_oos_replay_report.json")

VERDICT_RC1_REVIEW_COMPLETE = "RC1_OOS_REVIEW_COMPLETE"
VERDICT_RC1_REVIEW_BLOCKED = "RC1_OOS_REVIEW_BLOCKED"

# After this review the ONLY next step is a human decision over the RC1 out-of-sample
# evidence; no execution is authorized here.
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_RC1_OUT_OF_SAMPLE_EVIDENCE"

# Advisory bar describing what ROBUST out-of-sample evidence would look like. Used to
# annotate the results with risk notes -- NEVER to auto-promote anything to execution.
RC1_REVIEW_CRITERIA: dict[str, Any] = {
    "require_held_out_window_evaluated": True,
    "max_acceptable_worst_oos_drawdown": -0.50,
    "min_oos_mean_sharpe_ratio": 0.50,
    # OOS mean return below this fraction of the in-sample mean counts as material
    # degradation (advisory annotation only).
    "material_return_degradation_fraction": 0.5,
    "require_all_real_orders_zero": True,
    "require_no_optimization": True,
}


def get_rc1_oos_results_review_label() -> str:
    """Human label for the recognized Crypto-D1 RC1 out-of-sample results review contract."""
    return RC1_REVIEW_LABEL


def rc1_review_criteria() -> dict[str, Any]:
    """Return a fresh copy of the advisory RC1 review criteria. Pure."""
    return dict(RC1_REVIEW_CRITERIA)


def load_rc1_oos_replay_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local RC1 replay report JSON read-only. Returns {found, report, path}.
    Never raises; a missing/corrupt file yields found=False."""
    path = os.path.join(repo_root, RC1_REPLAY_REPORT_RELPATH)
    if not os.path.isfile(path):
        return {"found": False, "report": None, "path": path}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"found": True, "report": json.load(fh), "path": path}
    except (OSError, ValueError):
        return {"found": False, "report": None, "path": path}


def _window_summaries(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten each window result into a compact summary row. Pure."""
    rows: list[dict[str, Any]] = []
    for wr in report.get("window_results") or []:
        m = wr.get("metrics") or {}
        rows.append({
            "window_id": wr.get("window_id"),
            "window": wr.get("window"),
            "window_type": wr.get("window_type"),
            "symbols": list(wr.get("symbols") or []),
            "evaluated": bool(wr.get("evaluated")),
            "total_return": m.get("total_return"),
            "max_drawdown": m.get("max_drawdown"),
            "sharpe_ratio": m.get("sharpe_ratio"),
            "num_kill_events": m.get("num_kill_events"),
            "num_resume_events": m.get("num_resume_events"),
            "halted_at_end": m.get("halted_at_end"),
        })
    return rows


def _degradation(summaries: list[dict[str, Any]], in_sample: dict[str, Any],
                 criteria: dict[str, Any]) -> dict[str, Any]:
    """Compute the explicit OOS-vs-in-sample degradation comparison. Pure arithmetic over
    already-reported numbers; recomputes no simulation and changes no parameter."""
    evaluated = [s for s in summaries if s.get("evaluated") and s.get("total_return") is not None]
    rets = [float(s["total_return"]) for s in evaluated]
    dds = [float(s["max_drawdown"]) for s in evaluated if s.get("max_drawdown") is not None]
    shp = [float(s["sharpe_ratio"]) for s in evaluated if s.get("sharpe_ratio") is not None]

    oos_mean_ret = statistics.fmean(rets) if rets else 0.0
    oos_worst_dd = min(dds) if dds else 0.0
    oos_mean_sharpe = statistics.fmean(shp) if shp else 0.0

    is_mean_ret = float(in_sample.get("mean_total_return", 0.0) or 0.0)
    is_worst_dd = float(in_sample.get("worst_max_drawdown", 0.0) or 0.0)
    is_mean_sharpe = float(in_sample.get("mean_sharpe_ratio", 0.0) or 0.0)

    frac = float(criteria["material_return_degradation_fraction"])
    return_materially_degraded = (
        is_mean_ret > 0 and oos_mean_ret < frac * is_mean_ret
    )
    drawdown_worse_than_in_sample = oos_worst_dd < is_worst_dd
    any_window_negative = any(r < 0 for r in rets)

    held_out = [s for s in evaluated if s.get("window_type") == WINDOW_TYPE_HELD_OUT]
    held_out_evaluated = bool(held_out)
    held_out_positive = bool(held_out) and all(
        float(s["total_return"]) > 0 for s in held_out
    )

    return {
        "oos_windows_evaluated": len(evaluated),
        "oos_mean_total_return": oos_mean_ret,
        "oos_worst_max_drawdown": oos_worst_dd,
        "oos_mean_sharpe_ratio": oos_mean_sharpe,
        "in_sample_mean_total_return": is_mean_ret,
        "in_sample_worst_max_drawdown": is_worst_dd,
        "in_sample_mean_sharpe_ratio": is_mean_sharpe,
        "return_materially_degraded": return_materially_degraded,
        "drawdown_worse_than_in_sample": drawdown_worse_than_in_sample,
        "any_window_negative": any_window_negative,
        "held_out_window_evaluated": held_out_evaluated,
        "held_out_window_positive": held_out_positive,
        "materially_degraded_versus_in_sample": (
            return_materially_degraded or drawdown_worse_than_in_sample
        ),
    }


def review_rc1_oos_results(report: Any) -> dict[str, Any]:
    """Score the RC1 replay report and render a human-review decision. PURE: takes a report
    dict (or None), returns a decision dict. Never raises. The promotion decision is ALWAYS
    DO_NOT_PROMOTE_RESUME_POLICY_YET -- the observed out-of-sample degradation reinforces it;
    promotion to execution is a separate human gate."""
    crit = rc1_review_criteria()
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(report, dict):
        blockers.append("rc1_oos_replay_report_missing")
        blockers.append("execution_promotion_requires_separate_human_review")
        return _decision(VERDICT_RC1_REVIEW_BLOCKED, blockers, risk_notes, crit,
                         results_valid=False, policy_id=None, window_summaries=[],
                         degradation={}, in_sample_reference={})

    run_validation = validate_rc1_out_of_sample_replay_report(report)
    results_valid = bool(run_validation.get("valid"))
    if not results_valid:
        blockers.append("rc1_oos_replay_safety_invalid")
        blockers.extend("replay:" + e for e in run_validation.get("errors", []))

    complete = report.get("verdict") == VERDICT_REPLAYS_COMPLETE
    if not complete:
        blockers.append("rc1_oos_replay_not_complete")

    summaries = _window_summaries(report)
    if not summaries:
        blockers.append("no_window_results")

    # Real-order safety: no window may have placed a real order.
    for wr in report.get("window_results") or []:
        m = wr.get("metrics") or {}
        if (m.get("real_orders_placed", 0) or 0) != 0:
            blockers.append("real_orders_detected:" + str(wr.get("window_id")))

    if report.get("policy_parameters_changed") is not False:
        blockers.append("policy_parameters_changed")

    in_sample = dict(report.get("in_sample_reference") or {})
    degradation = _degradation(summaries, in_sample, crit)

    # Advisory annotations (risk notes, never auto-promotion / never auto-rejection).
    if degradation.get("held_out_window_evaluated"):
        if degradation.get("held_out_window_positive"):
            risk_notes.append("held_out_window_evidence_useful_policy_survived_unseen_history")
        else:
            risk_notes.append("held_out_window_negative_return")
    elif crit["require_held_out_window_evaluated"]:
        blockers.append("held_out_window_not_evaluated")

    if degradation.get("drawdown_worse_than_in_sample"):
        risk_notes.append("oos_worst_drawdown_worse_than_in_sample")
    if degradation.get("return_materially_degraded"):
        risk_notes.append("oos_mean_return_materially_below_in_sample")
    if degradation.get("any_window_negative"):
        for s in summaries:
            if s.get("evaluated") and (s.get("total_return") or 0) < 0:
                risk_notes.append("negative_return_window:" + str(s.get("window_id")))
    if degradation.get("materially_degraded_versus_in_sample"):
        risk_notes.append("oos_performance_materially_degraded_versus_in_sample")
    if float(degradation.get("oos_worst_max_drawdown", 0.0) or 0.0) < float(
        crit["max_acceptable_worst_oos_drawdown"]
    ):
        risk_notes.append("oos_worst_drawdown_breaches_hard_kill")
    if float(degradation.get("oos_mean_sharpe_ratio", 0.0) or 0.0) < float(
        crit["min_oos_mean_sharpe_ratio"]
    ):
        risk_notes.append("oos_mean_sharpe_below_advisory_minimum")

    risk_notes.append("oos_evidence_supports_keeping_do_not_promote")
    risk_notes.append("simulated_evidence_only_not_execution_validated")
    risk_notes.append("human_review_required_before_any_execution_promotion")

    # Structural promotion boundary: RC1 results NEVER auto-promote to execution.
    blockers.append("execution_promotion_requires_separate_human_review")

    structural_only = blockers == ["execution_promotion_requires_separate_human_review"]
    verdict = (
        VERDICT_RC1_REVIEW_COMPLETE
        if (results_valid and complete and structural_only)
        else VERDICT_RC1_REVIEW_BLOCKED
    )
    return _decision(verdict, blockers, risk_notes, crit, results_valid=results_valid,
                     policy_id=report.get("policy_id"), window_summaries=summaries,
                     degradation=degradation, in_sample_reference=in_sample)


def _decision(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    criteria: dict[str, Any],
    *,
    results_valid: bool,
    policy_id: Any,
    window_summaries: list[dict[str, Any]],
    degradation: dict[str, Any],
    in_sample_reference: dict[str, Any],
) -> dict[str, Any]:
    """Assemble an RC1 results decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally and
    the promotion decision is always DO_NOT_PROMOTE -- the review is evidence only."""
    return {
        "schema_version": RC1_REVIEW_SCHEMA_VERSION,
        "label": RC1_REVIEW_LABEL,
        "mode": RC1_REVIEW_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "policy_id": policy_id,
        "results_valid": results_valid,
        "promotion_decision": DO_NOT_PROMOTE_RESUME_POLICY_YET,
        "approved_for_execution": False,
        "human_review_required": True,
        "window_summaries": list(window_summaries),
        "degradation": dict(degradation),
        "in_sample_reference": dict(in_sample_reference),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "rc1_review_criteria": dict(criteria),
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


def build_rc1_oos_results_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local RC1 replay report read-only and review it. Reads one file; writes
    nothing; runs no replay; unlocks no gate."""
    loaded = load_rc1_oos_replay_report(repo_root)
    decision = review_rc1_oos_results(loaded["report"])
    decision["rc1_oos_replay_report_found"] = loaded["found"]
    decision["rc1_oos_replay_report_path"] = loaded["path"]
    return decision


def validate_rc1_oos_results_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) an RC1 results decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_RC1_REVIEW_COMPLETE, VERDICT_RC1_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != RC1_REVIEW_SCHEMA_VERSION:
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
    if "execution_promotion_requires_separate_human_review" not in (d.get("blockers") or []):
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


def render_rc1_oos_results_review_markdown(decision: Any) -> str:
    """Render an RC1 results decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    deg = d.get("degradation") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC1 Out-of-Sample Results Review")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Policy (parameters UNCHANGED): " + str(d.get("policy_id", "")))
    lines.append("- Results valid: " + str(d.get("results_valid", "")))
    lines.append("- Promotion decision: " + str(d.get("promotion_decision", "")))
    lines.append("- Approved for execution: " + str(d.get("approved_for_execution", "")))
    lines.append("- Human review required: " + str(d.get("human_review_required", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Out-of-sample vs in-sample (research evidence only)")
    lines.append("- OOS mean return: " + _pct(deg.get("oos_mean_total_return"))
                 + " vs in-sample " + _pct(deg.get("in_sample_mean_total_return")))
    lines.append("- OOS worst drawdown: " + _pct(deg.get("oos_worst_max_drawdown"))
                 + " vs in-sample " + _pct(deg.get("in_sample_worst_max_drawdown")))
    lines.append("- OOS mean Sharpe: "
                 + f"{float(deg.get('oos_mean_sharpe_ratio', 0) or 0):.2f}"
                 + " vs in-sample "
                 + f"{float(deg.get('in_sample_mean_sharpe_ratio', 0) or 0):.2f}")
    lines.append("- Held-out window evaluated: " + str(deg.get("held_out_window_evaluated"))
                 + " | positive: " + str(deg.get("held_out_window_positive")))
    lines.append("- Materially degraded versus in-sample: "
                 + str(deg.get("materially_degraded_versus_in_sample")))
    lines.append("")
    lines.append("## Windows")
    for s in d.get("window_summaries") or []:
        if s.get("evaluated"):
            lines.append("- " + str(s.get("window_id")) + " (" + str(s.get("window_type"))
                         + "): return " + _pct(s.get("total_return"))
                         + ", maxDD " + _pct(s.get("max_drawdown"))
                         + ", Sharpe " + f"{float(s.get('sharpe_ratio', 0) or 0):.2f}"
                         + ", kills " + str(s.get("num_kill_events"))
                         + ", resumes " + str(s.get("num_resume_events")))
        else:
            lines.append("- " + str(s.get("window_id")) + ": NOT EVALUATED")
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
