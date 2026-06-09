"""Crypto-D1 Baseline Backtest Review / Promotion Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the completed local baseline
backtest report and renders a PROMOTION DECISION: may this baseline progress to
paper-trading PREP, or not (yet)?

It reads ONLY the local baseline report artifact
``reports/crypto_d1_baseline_backtest/baseline_backtest_report.json`` (read-only),
scores its metrics against explicit, fixed promotion criteria, and emits:
  - a review verdict;
  - a promotion decision (PROMOTE_TO_PAPER_PREP / DO_NOT_PROMOTE_TO_PAPER_YET);
  - hard blockers and non-blocking risk notes.

It RUNS NOTHING: no new backtest, no optimization, no parameter search, no
paper/live/micro-live, no broker/exchange, no network, no credentials. It UNLOCKS
no gate: paper_trading_gate and micro_live_gate stay LOCKED regardless of the
decision. A PROMOTE decision is only a RECOMMENDATION that a SEPARATE explicit
human command may then act on.

Public API:
  - REVIEW_SCHEMA_VERSION / REVIEW_LABEL / REVIEW_MODE
  - PROMOTION_CRITERIA
  - VERDICT_REVIEW_COMPLETE / VERDICT_REVIEW_BLOCKED
  - PROMOTE_TO_PAPER_PREP / DO_NOT_PROMOTE_TO_PAPER_YET
  - BASELINE_REPORT_RELPATH
  - get_baseline_review_label()
  - promotion_criteria()
  - load_baseline_report(repo_root)
  - review_baseline_report(report)
  - build_baseline_review_decision(repo_root)
  - validate_baseline_review_decision(decision)
  - render_baseline_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner import (
    BASELINE_REPORT_DIR,
    VERDICT_BASELINE_COMPLETE,
)

REVIEW_SCHEMA_VERSION = "strategy_factory_crypto_d1_baseline_backtest_review_contract.v1"
REVIEW_LABEL = "Crypto-D1 Baseline Backtest Review / Promotion Decision (READ-ONLY)"
REVIEW_MODE = "RESEARCH_ONLY"

BASELINE_REPORT_RELPATH = os.path.join(BASELINE_REPORT_DIR, "baseline_backtest_report.json")

VERDICT_REVIEW_COMPLETE = "REVIEW_COMPLETE"
VERDICT_REVIEW_BLOCKED = "REVIEW_BLOCKED"

PROMOTE_TO_PAPER_PREP = "PROMOTE_TO_PAPER_PREP"
DO_NOT_PROMOTE_TO_PAPER_YET = "DO_NOT_PROMOTE_TO_PAPER_YET"

# Fixed acceptance gates a baseline must clear to be ELIGIBLE for paper-trading
# prep. These are deliberately conservative: a benchmark that can lose ~all its
# value in a drawdown is not paper-ready no matter how large its terminal return.
PROMOTION_CRITERIA: dict[str, Any] = {
    "require_baseline_complete": True,
    # drawdown is a floor: max_drawdown must be >= this (i.e. no worse than -50%).
    "max_acceptable_drawdown": -0.50,
    "min_sharpe_ratio": 0.50,
    "min_total_return": 0.0,
    "min_trading_days": 365,
}

# Share of total portfolio value at exit above which a single symbol is flagged as
# a (non-blocking) concentration risk.
_CONCENTRATION_FLAG_SHARE = 0.50


def get_baseline_review_label() -> str:
    """Human label for the recognized Crypto-D1 baseline review / promotion contract."""
    return REVIEW_LABEL


def promotion_criteria() -> dict[str, Any]:
    """Return a fresh copy of the fixed promotion criteria. Pure."""
    return dict(PROMOTION_CRITERIA)


def load_baseline_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local baseline report JSON read-only. Returns {found, report}.
    Never raises; a missing/corrupt file yields found=False, report=None."""
    path = os.path.join(repo_root, BASELINE_REPORT_RELPATH)
    if not os.path.isfile(path):
        return {"found": False, "report": None, "path": path}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"found": True, "report": json.load(fh), "path": path}
    except (OSError, ValueError):
        return {"found": False, "report": None, "path": path}


def _concentration_note(report: dict[str, Any]) -> list[str]:
    """Flag (non-blocking) if one symbol dominates terminal portfolio value."""
    notes: list[str] = []
    per_symbol = report.get("per_symbol") or []
    contribs = [
        (str(s.get("symbol")), float(s.get("contribution_to_portfolio") or 0.0))
        for s in per_symbol
        if isinstance(s, dict)
    ]
    total = sum(c for _, c in contribs)
    if total > 0:
        for sym, c in contribs:
            if c / total >= _CONCENTRATION_FLAG_SHARE:
                notes.append("return_concentrated_in_" + sym)
    return notes


def review_baseline_report(report: Any) -> dict[str, Any]:
    """Score a baseline report against the fixed promotion criteria. PURE: takes a
    report dict (or None), returns a decision dict. Never raises. A missing report
    or an incomplete baseline is a hard blocker -> DO_NOT_PROMOTE_TO_PAPER_YET."""
    crit = promotion_criteria()
    blockers: list[str] = []
    risk_notes: list[str] = []
    metrics: dict[str, Any] = {}

    if not isinstance(report, dict):
        blockers.append("baseline_report_missing")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_PROMOTE_TO_PAPER_YET,
                         blockers, risk_notes, metrics, crit)

    if crit["require_baseline_complete"] and report.get("verdict") != VERDICT_BASELINE_COMPLETE:
        blockers.append("baseline_not_complete")

    perf = report.get("performance")
    if not isinstance(perf, dict):
        blockers.append("performance_missing")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_PROMOTE_TO_PAPER_YET,
                         blockers, risk_notes, metrics, crit)

    max_dd = float(perf.get("max_drawdown", 0.0) or 0.0)
    sharpe = float(perf.get("sharpe_ratio", 0.0) or 0.0)
    total_return = float(perf.get("total_return", 0.0) or 0.0)
    trading_days = int(perf.get("trading_days", 0) or 0)
    metrics = {
        "max_drawdown": max_dd,
        "sharpe_ratio": sharpe,
        "total_return": total_return,
        "trading_days": trading_days,
        "cagr": float(perf.get("cagr", 0.0) or 0.0),
    }

    if max_dd < crit["max_acceptable_drawdown"]:
        blockers.append("max_drawdown_exceeds_limit")
    if sharpe < crit["min_sharpe_ratio"]:
        blockers.append("sharpe_below_minimum")
    if total_return < crit["min_total_return"]:
        blockers.append("total_return_below_minimum")
    if trading_days < crit["min_trading_days"]:
        blockers.append("coverage_below_minimum")

    # Non-blocking structural risk notes (true even for a passing baseline).
    ts = report.get("trade_summary") or {}
    if isinstance(ts, dict) and ts.get("sells") == 0 and ts.get("rebalances") == 0:
        risk_notes.append("buy_and_hold_has_no_risk_management")
    risk_notes.append("single_market_regime_sample")
    risk_notes.extend(_concentration_note(report))

    eligible = not blockers
    decision = PROMOTE_TO_PAPER_PREP if eligible else DO_NOT_PROMOTE_TO_PAPER_YET
    verdict = VERDICT_REVIEW_COMPLETE
    return _decision(verdict, decision, blockers, risk_notes, metrics, crit)


def _decision(
    verdict: str,
    promotion_decision: str,
    blockers: list[str],
    risk_notes: list[str],
    metrics: dict[str, Any],
    criteria: dict[str, Any],
) -> dict[str, Any]:
    """Assemble a review decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live stay LOCKED unconditionally."""
    eligible = (promotion_decision == PROMOTE_TO_PAPER_PREP) and not blockers
    next_action = (
        "HUMAN_APPROVED_PAPER_TRADING_PREP_GATE"
        if eligible
        else "REVISE_BASELINE_RISK_PROFILE_BEFORE_PAPER_PREP"
    )
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "label": REVIEW_LABEL,
        "mode": REVIEW_MODE,
        "verdict": verdict,
        "promotion_decision": promotion_decision,
        "eligible_for_paper_prep": eligible,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "metrics_reviewed": dict(metrics),
        "promotion_criteria": dict(criteria),
        # Capability posture (this contract executes / authorizes nothing):
        "executes": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this review):
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "next_required_action": next_action,
    }


def build_baseline_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local baseline report read-only and review it. Reads one file;
    writes nothing; runs no backtest; unlocks no gate."""
    loaded = load_baseline_report(repo_root)
    decision = review_baseline_report(loaded["report"])
    decision["baseline_report_found"] = loaded["found"]
    decision["baseline_report_path"] = loaded["path"]
    return decision


def validate_baseline_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a review decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_REVIEW_COMPLETE, VERDICT_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("promotion_decision") not in (PROMOTE_TO_PAPER_PREP, DO_NOT_PROMOTE_TO_PAPER_YET):
        errors.append("bad_promotion_decision")
    if d.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")

    # A DO_NOT_PROMOTE decision must never be marked eligible, and an eligible
    # decision must have no blockers.
    if d.get("promotion_decision") == DO_NOT_PROMOTE_TO_PAPER_YET and d.get("eligible_for_paper_prep") is not False:
        errors.append("blocked_decision_marked_eligible")
    if d.get("eligible_for_paper_prep") is True and (d.get("blockers") or []):
        errors.append("eligible_with_blockers")

    must_be_locked = (
        "baseline_backtest_blocked",
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
    )
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_backtest",
        "runs_optimization",
        "authorizes_paper_trading",
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


def render_baseline_review_markdown(decision: Any) -> str:
    """Render a review decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    m = d.get("metrics_reviewed") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Baseline Backtest Review / Promotion Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Promotion decision: " + str(d.get("promotion_decision", "")))
    lines.append("- Eligible for paper prep: " + str(d.get("eligible_for_paper_prep", "")))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    blockers = d.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("")
    lines.append("## Metrics reviewed")
    lines.append("- Total return: " + _pct(m.get("total_return")))
    lines.append("- CAGR: " + _pct(m.get("cagr")))
    lines.append("- Sharpe ratio: " + str(m.get("sharpe_ratio")))
    lines.append("- Max drawdown: " + _pct(m.get("max_drawdown")))
    lines.append("- Trading days: " + str(m.get("trading_days")))
    lines.append("")
    lines.append("## Risk notes")
    for note in d.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- baseline_backtest: BLOCKED")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)
