"""Crypto-D1 Variant Backtest Review / Paper-Prep Decision Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that REVIEWS the completed local risk-controlled
variant backtest report and renders a PAPER-PREP DECISION: may a risk-controlled
variant progress to paper-trading PREP (prep only), or not (yet)?

It reads ONLY the local variant report artifact
``reports/crypto_d1_variant_backtest/variant_backtest_report.json`` (read-only),
inspects each variant's pre-computed promotion eligibility (drawdown floor, Sharpe,
return, coverage -- already scored by the runner against the fixed promotion
criteria) and emits:
  - a review verdict;
  - a paper-prep decision (APPROVE_PAPER_PREP_ONLY / DO_NOT_APPROVE_PAPER_PREP_YET);
  - the selected variant (if any), hard blockers, and non-blocking risk notes.

It RUNS NOTHING: no new backtest, no optimization, no parameter search, no
paper/live/micro-live, no broker/exchange, no network, no credentials. It UNLOCKS
no gate: paper_trading_gate and micro_live_gate stay LOCKED regardless of the
decision. An APPROVE_PAPER_PREP_ONLY decision is only a RECOMMENDATION that PREP for
the selected variant may be built; the actual paper runner / config, and any gate
unlock, require a SEPARATE explicit human command.

Public API:
  - REVIEW_SCHEMA_VERSION / REVIEW_LABEL / REVIEW_MODE
  - VERDICT_REVIEW_COMPLETE / VERDICT_REVIEW_BLOCKED
  - APPROVE_PAPER_PREP_ONLY / DO_NOT_APPROVE_PAPER_PREP_YET
  - PAPER_PREP_SCOPE / VARIANT_REPORT_RELPATH
  - get_variant_review_label()
  - load_variant_report(repo_root)
  - review_variant_report(report)
  - build_variant_review_decision(repo_root)
  - validate_variant_review_decision(decision)
  - render_variant_review_markdown(decision)
"""

from __future__ import annotations

import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_variant_backtest_runner import (
    VARIANT_REPORT_DIR,
    VERDICT_VARIANTS_COMPLETE,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract import (
    promotion_criteria,
)

REVIEW_SCHEMA_VERSION = "strategy_factory_crypto_d1_variant_backtest_review_contract.v1"
REVIEW_LABEL = "Crypto-D1 Variant Backtest Review / Paper-Prep Decision (READ-ONLY)"
REVIEW_MODE = "RESEARCH_ONLY"

VARIANT_REPORT_RELPATH = os.path.join(VARIANT_REPORT_DIR, "variant_backtest_report.json")

VERDICT_REVIEW_COMPLETE = "REVIEW_COMPLETE"
VERDICT_REVIEW_BLOCKED = "REVIEW_BLOCKED"

APPROVE_PAPER_PREP_ONLY = "APPROVE_PAPER_PREP_ONLY"
DO_NOT_APPROVE_PAPER_PREP_YET = "DO_NOT_APPROVE_PAPER_PREP_YET"

# This decision recommends PREP ONLY -- never an actual paper run, never a gate unlock.
PAPER_PREP_SCOPE = "PAPER_PREP_ONLY"

# A selected variant whose drawdown sits within this band of the floor is flagged
# (non-blocking) as a thin safety margin worth noting before prep.
_DRAWDOWN_MARGIN_BAND = 0.10


def get_variant_review_label() -> str:
    """Human label for the recognized Crypto-D1 variant review / paper-prep contract."""
    return REVIEW_LABEL


def load_variant_report(repo_root: str = ".") -> dict[str, Any]:
    """Read the local variant report JSON read-only. Returns {found, report, path}.
    Never raises; a missing/corrupt file yields found=False, report=None."""
    path = os.path.join(repo_root, VARIANT_REPORT_RELPATH)
    if not os.path.isfile(path):
        return {"found": False, "report": None, "path": path}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"found": True, "report": json.load(fh), "path": path}
    except (OSError, ValueError):
        return {"found": False, "report": None, "path": path}


def _eligible_variants(variant_results: list[Any]) -> list[dict[str, Any]]:
    """Variants the runner already scored as paper-prep eligible (no blockers)."""
    out: list[dict[str, Any]] = []
    for v in variant_results:
        if not isinstance(v, dict):
            continue
        if v.get("eligible_for_paper_prep") is True and not (v.get("eligibility_blockers") or []):
            out.append(v)
    return out


def _select_best(eligible: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Deterministically pick the strongest eligible variant: highest Sharpe, then
    shallowest (closest-to-zero) max drawdown, then variant_id for a stable tie-break."""
    if not eligible:
        return None

    def key(v: dict[str, Any]) -> tuple[float, float, str]:
        perf = v.get("performance") or {}
        sharpe = float(perf.get("sharpe_ratio", 0.0) or 0.0)
        max_dd = float(perf.get("max_drawdown", 0.0) or 0.0)
        return (sharpe, max_dd, str(v.get("variant_id")))

    return sorted(eligible, key=key, reverse=True)[0]


def review_variant_report(report: Any) -> dict[str, Any]:
    """Score the variant backtest report and render a paper-prep decision. PURE: takes
    a report dict (or None), returns a decision dict. Never raises. A missing report,
    an incomplete run, or zero eligible variants blocks paper prep."""
    crit = promotion_criteria()
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(report, dict):
        blockers.append("variant_report_missing")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_APPROVE_PAPER_PREP_YET,
                         None, [], blockers, risk_notes, crit)

    if report.get("verdict") != VERDICT_VARIANTS_COMPLETE:
        blockers.append("variant_backtest_not_complete")

    variant_results = report.get("variant_results")
    if not isinstance(variant_results, list) or not variant_results:
        blockers.append("no_variant_results")
        return _decision(VERDICT_REVIEW_BLOCKED, DO_NOT_APPROVE_PAPER_PREP_YET,
                         None, [], blockers, risk_notes, crit)

    eligible = _eligible_variants(variant_results)
    eligible_ids = [str(v.get("variant_id")) for v in eligible]
    selected = _select_best(eligible)

    if not eligible:
        blockers.append("no_paper_prep_eligible_variant")

    # Non-blocking structural risk notes.
    risk_notes.append("single_market_regime_sample")
    if len(eligible) == 1:
        risk_notes.append("only_one_variant_eligible")
    if selected is not None:
        perf = selected.get("performance") or {}
        max_dd = float(perf.get("max_drawdown", 0.0) or 0.0)
        floor = float(crit["max_acceptable_drawdown"])
        if floor <= max_dd <= floor + _DRAWDOWN_MARGIN_BAND:
            risk_notes.append("selected_variant_drawdown_near_floor")
    not_clearing = [
        str(v.get("variant_id"))
        for v in variant_results
        if isinstance(v, dict) and v.get("beats_drawdown_floor") is False
    ]
    if not_clearing:
        risk_notes.append("variants_exceeding_drawdown_floor:" + ",".join(not_clearing))

    decision = APPROVE_PAPER_PREP_ONLY if (eligible and not blockers) else DO_NOT_APPROVE_PAPER_PREP_YET
    verdict = VERDICT_REVIEW_COMPLETE if not blockers else VERDICT_REVIEW_BLOCKED
    selected_id = str(selected.get("variant_id")) if (selected is not None and decision == APPROVE_PAPER_PREP_ONLY) else None
    return _decision(verdict, decision, selected_id, eligible_ids, blockers, risk_notes, crit)


def _decision(
    verdict: str,
    paper_prep_decision: str,
    selected_variant_id: str | None,
    eligible_variant_ids: list[str],
    blockers: list[str],
    risk_notes: list[str],
    criteria: dict[str, Any],
) -> dict[str, Any]:
    """Assemble a paper-prep decision dict carrying the read-only safety posture. This
    contract authorizes nothing: paper / micro-live stay LOCKED unconditionally, and
    an APPROVE decision recommends PREP ONLY (a separate human command builds it)."""
    approved = (paper_prep_decision == APPROVE_PAPER_PREP_ONLY) and not blockers
    next_action = (
        "HUMAN_APPROVED_PAPER_TRADING_PREP_FOR_SELECTED_VARIANT"
        if approved
        else "REVISE_VARIANTS_BEFORE_PAPER_PREP"
    )
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "label": REVIEW_LABEL,
        "mode": REVIEW_MODE,
        "verdict": verdict,
        "paper_prep_decision": paper_prep_decision,
        "paper_prep_scope": PAPER_PREP_SCOPE,
        "approved_for_paper_prep": approved,
        "selected_variant_id": selected_variant_id,
        "eligible_variant_ids": list(eligible_variant_ids),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "promotion_criteria": dict(criteria),
        # Capability posture (this contract executes / authorizes nothing live):
        "executes": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "runs_parameter_search": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "builds_paper_runner": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this review):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "next_required_action": next_action,
    }


def build_variant_review_decision(repo_root: str = ".") -> dict[str, Any]:
    """Load the local variant report read-only and review it. Reads one file; writes
    nothing; runs no backtest; unlocks no gate."""
    loaded = load_variant_report(repo_root)
    decision = review_variant_report(loaded["report"])
    decision["variant_report_found"] = loaded["found"]
    decision["variant_report_path"] = loaded["path"]
    return decision


def validate_variant_review_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a paper-prep decision's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_REVIEW_COMPLETE, VERDICT_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if d.get("paper_prep_decision") not in (APPROVE_PAPER_PREP_ONLY, DO_NOT_APPROVE_PAPER_PREP_YET):
        errors.append("bad_paper_prep_decision")
    if d.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("paper_prep_scope") != PAPER_PREP_SCOPE:
        errors.append("bad_paper_prep_scope")

    # A DO_NOT_APPROVE decision must never be marked approved or carry a selected
    # variant; an APPROVE decision must select a variant and carry no blockers.
    if d.get("paper_prep_decision") == DO_NOT_APPROVE_PAPER_PREP_YET:
        if d.get("approved_for_paper_prep") is not False:
            errors.append("blocked_decision_marked_approved")
        if d.get("selected_variant_id") is not None:
            errors.append("blocked_decision_has_selected_variant")
    if d.get("paper_prep_decision") == APPROVE_PAPER_PREP_ONLY:
        if not d.get("selected_variant_id"):
            errors.append("approved_decision_without_selected_variant")
        if d.get("blockers") or []:
            errors.append("approved_with_blockers")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_backtest",
        "runs_optimization",
        "runs_parameter_search",
        "authorizes_paper_trading",
        "authorizes_live_trading",
        "builds_paper_runner",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if d.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_variant_review_markdown(decision: Any) -> str:
    """Render a paper-prep decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Variant Backtest Review / Paper-Prep Decision")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Paper-prep decision: " + str(d.get("paper_prep_decision", "")))
    lines.append("- Paper-prep scope: " + str(d.get("paper_prep_scope", "")))
    lines.append("- Approved for paper prep: " + str(d.get("approved_for_paper_prep", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id")))
    lines.append("- Eligible variants: " + (", ".join(d.get("eligible_variant_ids") or []) or "none"))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    blockers = d.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("")
    lines.append("## Risk notes")
    for note in d.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- builds_paper_runner: False (separate approval required)")
    return "\n".join(lines)
