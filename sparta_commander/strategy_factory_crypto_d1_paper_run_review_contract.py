"""Crypto-D1 V2 Simulated Paper-Run Review / Micro-Live Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the completed local SIMULATED
paper-trading run report for ``V2_trend_plus_cash_regime`` and renders a MICRO-LIVE
DECISION: is the simulated paper run valid, was the kill-switch behavior acceptable, and
may V2 progress toward a REAL micro-live trial -- or does it need more simulated evidence
first?

It reads ONLY the local simulated paper-run artifact
``reports/crypto_d1_paper_prep/paper_run_report.json`` (read-only), re-validates its
safety posture with the runner's own validator, inspects performance + kill-switch
outcome, and emits:
  - a review verdict;
  - a micro-live decision (PROMOTE_TO_MICRO_LIVE / DO_NOT_PROMOTE_TO_MICRO_LIVE_YET);
  - hard blockers and non-blocking risk notes;
  - an explicit kill-switch acceptability assessment.

Micro-live is a REAL-MONEY gate, so the bar is deliberately conservative: a single
simulated regime is never sufficient on its own, a run that ended HALTED (kill switch
tripped, manual resume pending) is not promotable, and the gate stays LOCKED regardless.

It RUNS NOTHING: no new paper run, no backtest, no optimization, no live/micro-live, no
broker/exchange, no network, no credentials, no real order. It UNLOCKS no gate:
paper_trading_gate, micro_live_gate and the live gate stay LOCKED. A PROMOTE decision is
only a RECOMMENDATION; an actual micro-live trial requires a SEPARATE explicit human
command on a separate gate.

Public API:
  - REVIEW_SCHEMA_VERSION / REVIEW_LABEL / REVIEW_MODE
  - PAPER_RUN_REPORT_RELPATH / SELECTED_VARIANT_ID
  - VERDICT_REVIEW_COMPLETE / VERDICT_REVIEW_BLOCKED
  - PROMOTE_TO_MICRO_LIVE / DO_NOT_PROMOTE_TO_MICRO_LIVE_YET
  - MICRO_LIVE_CRITERIA
  - get_paper_run_review_label()
  - micro_live_criteria()
  - load_paper_run_report(repo_root)
  - review_paper_run_report(report)
  - build_paper_run_review_decision(repo_root)
  - validate_paper_run_review_decision(decision)
  - render_paper_run_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    PAPER_LOG_DIR,
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_paper_trading_run_simulated import (
    VERDICT_PAPER_RUN_COMPLETE,
    validate_paper_run_report,
)

REVIEW_SCHEMA_VERSION = "strategy_factory_crypto_d1_paper_run_review_contract.v1"
REVIEW_LABEL = "Crypto-D1 V2 Simulated Paper-Run Review / Micro-Live Decision (READ-ONLY)"
REVIEW_MODE = "RESEARCH_ONLY"

PAPER_RUN_REPORT_RELPATH = os.path.join(PAPER_LOG_DIR, "paper_run_report.json")

VERDICT_REVIEW_COMPLETE = "REVIEW_COMPLETE"
VERDICT_REVIEW_BLOCKED = "REVIEW_BLOCKED"

PROMOTE_TO_MICRO_LIVE = "PROMOTE_TO_MICRO_LIVE"
DO_NOT_PROMOTE_TO_MICRO_LIVE_YET = "DO_NOT_PROMOTE_TO_MICRO_LIVE_YET"

# Conservative micro-live (REAL money) promotion bar. A single simulated regime is never
# enough; a kill-triggered or still-halted run is never promotable.
MICRO_LIVE_CRITERIA: dict[str, Any] = {
    "max_acceptable_drawdown": -0.35,
    "min_sharpe_ratio": 0.50,
    "min_simulated_trades": 1,
    "require_zero_real_orders": True,
    "require_not_halted_at_end": True,
    "require_no_kill_switch_trigger": True,
    "require_multi_regime_evidence": True,
}


def get_paper_run_review_label() -> str:
    """Human label for the recognized Crypto-D1 simulated paper-run review contract."""
    return REVIEW_LABEL


def micro_live_criteria() -> dict[str, Any]:
    """Return a fresh copy of the conservative micro-live promotion criteria. Pure."""
    return dict(MICRO_LIVE_CRITERIA)


def load_paper_run_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local simulated paper-run report JSON read-only. Returns
    {found, report, path}. Never raises; a missing/corrupt file yields found=False."""
    path = os.path.join(repo_root, PAPER_RUN_REPORT_RELPATH)
    if not os.path.isfile(path):
        return {"found": False, "report": None, "path": path}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"found": True, "report": json.load(fh), "path": path}
    except (OSError, ValueError):
        return {"found": False, "report": None, "path": path}


def _assess_kill_switch(report: dict[str, Any]) -> tuple[bool, list[str]]:
    """Assess whether the kill-switch behaved acceptably. A kill is acceptable when, on
    triggering, the book was flattened, the harness HALTED, and no real order was placed.
    Returns (acceptable, notes). A clean (never-triggered) run is trivially acceptable."""
    notes: list[str] = []
    triggered = bool(report.get("kill_switch_triggered"))
    halted = bool(report.get("halted_at_end"))
    real_orders = (report.get("trade_summary") or {}).get("real_orders_placed", 0)
    if not triggered:
        return True, ["kill_switch_not_triggered"]
    for ev in report.get("kill_switch_events") or []:
        notes.append("kill_event:" + str(ev.get("reason")) + "@" + str(ev.get("date")))
    acceptable = halted and (real_orders == 0)
    if halted:
        notes.append("flattened_to_cash_and_halted")
    else:
        notes.append("kill_triggered_but_not_halted")
    return acceptable, notes


def review_paper_run_report(report: Any) -> dict[str, Any]:
    """Score the simulated paper-run report and render a micro-live decision. PURE: takes
    a report dict (or None), returns a decision dict. Never raises. A missing report, an
    incomplete/invalid run, a still-halted run, a kill-trigger, or insufficient regime
    evidence blocks micro-live promotion."""
    crit = micro_live_criteria()
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(report, dict):
        blockers.append("paper_run_report_missing")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_PROMOTE_TO_MICRO_LIVE_YET,
                         blockers, risk_notes, crit, run_valid=False,
                         kill_switch_acceptable=False)

    # Re-validate the run's own safety posture (gates locked, no real orders, etc.).
    run_validation = validate_paper_run_report(report)
    run_valid = bool(run_validation.get("valid"))
    if not run_valid:
        blockers.append("paper_run_safety_invalid")
        blockers.extend("run:" + e for e in run_validation.get("errors", []))

    if report.get("verdict") != VERDICT_PAPER_RUN_COMPLETE:
        blockers.append("simulated_run_not_complete")

    perf = report.get("performance") or {}
    trades = report.get("trade_summary") or {}
    if not perf:
        blockers.append("performance_missing")

    if (trades.get("real_orders_placed", 0) or 0) != 0:
        blockers.append("real_orders_detected")

    halted = bool(report.get("halted_at_end"))
    triggered = bool(report.get("kill_switch_triggered"))

    kill_acceptable, kill_notes = _assess_kill_switch(report)
    risk_notes.extend(kill_notes)

    # Hard micro-live gating (real money => conservative).
    if halted:
        blockers.append("run_halted_pending_human_resume")
    if triggered:
        blockers.append("kill_switch_triggered_needs_resume_policy_review")
    if crit["require_multi_regime_evidence"]:
        blockers.append("insufficient_regime_evidence_for_micro_live")

    # Quantitative thresholds (recorded as risk notes when breached; the structural
    # blockers above already prevent promotion from a single simulated sample).
    max_dd = float(perf.get("max_drawdown", 0.0) or 0.0)
    sharpe = float(perf.get("sharpe_ratio", 0.0) or 0.0)
    sim_trades = int(trades.get("simulated_trades", 0) or 0)
    if max_dd < float(crit["max_acceptable_drawdown"]):
        risk_notes.append("max_drawdown_exceeds_micro_live_limit")
    if sharpe < float(crit["min_sharpe_ratio"]):
        risk_notes.append("sharpe_below_micro_live_minimum")
    if sim_trades < int(crit["min_simulated_trades"]):
        risk_notes.append("too_few_simulated_trades")
    risk_notes.append("single_market_regime_sample")
    risk_notes.append("more_simulated_paper_testing_recommended")

    decision = PROMOTE_TO_MICRO_LIVE if not blockers else DO_NOT_PROMOTE_TO_MICRO_LIVE_YET
    verdict = VERDICT_REVIEW_COMPLETE if run_valid and report.get("verdict") == VERDICT_PAPER_RUN_COMPLETE else VERDICT_REVIEW_BLOCKED
    return _decision(verdict, decision, blockers, risk_notes, crit,
                     run_valid=run_valid, kill_switch_acceptable=kill_acceptable,
                     performance=perf, trade_summary=trades)


def _decision(
    verdict: str,
    micro_live_decision: str,
    blockers: list[str],
    risk_notes: list[str],
    criteria: dict[str, Any],
    *,
    run_valid: bool,
    kill_switch_acceptable: bool,
    performance: dict[str, Any] | None = None,
    trade_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble a micro-live decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live / live stay LOCKED unconditionally,
    and a PROMOTE decision is only a RECOMMENDATION (a separate human command on a
    separate real-money gate is required)."""
    promoted = (micro_live_decision == PROMOTE_TO_MICRO_LIVE) and not blockers
    next_action = (
        "HUMAN_APPROVED_MICRO_LIVE_TRIAL_REAL_MONEY_SEPARATE_GATE"
        if promoted
        else "RUN_MORE_SIMULATED_PAPER_EVIDENCE_AND_REVIEW_RESUME_POLICY"
    )
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "label": REVIEW_LABEL,
        "mode": REVIEW_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "simulated_run_valid": run_valid,
        "kill_switch_behavior_acceptable": kill_switch_acceptable,
        "micro_live_decision": micro_live_decision,
        "approved_for_micro_live": promoted,
        "more_simulated_paper_testing_needed": not promoted,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "micro_live_criteria": dict(criteria),
        "reviewed_performance": dict(performance or {}),
        "reviewed_trade_summary": dict(trade_summary or {}),
        # Capability posture (this contract executes / authorizes nothing live):
        "executes": False,
        "runs_paper_trading": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this review):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "next_required_action": next_action,
    }


def build_paper_run_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local simulated paper-run report read-only and review it. Reads one file;
    writes nothing; runs no paper run; unlocks no gate."""
    loaded = load_paper_run_report(repo_root)
    decision = review_paper_run_report(loaded["report"])
    decision["paper_run_report_found"] = loaded["found"]
    decision["paper_run_report_path"] = loaded["path"]
    return decision


def validate_paper_run_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a micro-live decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_REVIEW_COMPLETE, VERDICT_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("micro_live_decision") not in (PROMOTE_TO_MICRO_LIVE, DO_NOT_PROMOTE_TO_MICRO_LIVE_YET):
        errors.append("bad_micro_live_decision")
    if d.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    # A DO_NOT_PROMOTE decision must never be marked approved; a PROMOTE decision must
    # carry no blockers and must mark approval consistently.
    if d.get("micro_live_decision") == DO_NOT_PROMOTE_TO_MICRO_LIVE_YET:
        if d.get("approved_for_micro_live") is not False:
            errors.append("blocked_decision_marked_approved")
        if d.get("more_simulated_paper_testing_needed") is not True:
            errors.append("blocked_decision_not_flagging_more_testing")
    if d.get("micro_live_decision") == PROMOTE_TO_MICRO_LIVE:
        if d.get("blockers") or []:
            errors.append("promoted_with_blockers")
        if d.get("approved_for_micro_live") is not True:
            errors.append("promoted_without_approval_flag")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_paper_trading",
        "runs_backtest",
        "runs_optimization",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
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


def render_paper_run_review_markdown(decision: Any) -> str:
    """Render a micro-live decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    perf = d.get("reviewed_performance") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Simulated Paper-Run Review / Micro-Live Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Simulated run valid: " + str(d.get("simulated_run_valid", "")))
    lines.append("- Kill-switch behavior acceptable: " + str(d.get("kill_switch_behavior_acceptable", "")))
    lines.append("- Micro-live decision: " + str(d.get("micro_live_decision", "")))
    lines.append("- Approved for micro-live: " + str(d.get("approved_for_micro_live", "")))
    lines.append("- More simulated paper testing needed: " + str(d.get("more_simulated_paper_testing_needed", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Reviewed simulated performance")
    lines.append("- Final equity: " + str(perf.get("final_equity")))
    lines.append("- Total return: " + _pct(perf.get("total_return"))
                 + " | Max drawdown: " + _pct(perf.get("max_drawdown")))
    lines.append("- Sharpe: " + f"{float(perf.get('sharpe_ratio', 0) or 0):.2f}")
    lines.append("")
    lines.append("## Blockers")
    blockers = d.get("blockers") or []
    for b in (blockers or ["(none)"]):
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
    lines.append("- authorizes_micro_live: False (separate real-money gate + human command required)")
    return "\n".join(lines)
