"""Crypto-D1 Risk-Profile Revision Plan (READ-ONLY, RESEARCH PLAN).

A PURE, stdlib-only, read-only module that turns the BLOCKED baseline review
(promotion decision DO_NOT_PROMOTE_TO_PAPER_YET, hard blocker
``max_drawdown_exceeds_limit``) into a concrete RESEARCH PLAN for reducing drawdown
BEFORE paper-trading is ever reconsidered.

It reads ONLY the local baseline review decision (which itself reads only the local
baseline report) and assembles:
  - the trigger evidence (why a revision is required);
  - candidate, FIXED (pre-registered, NON-optimized) risk controls;
  - a list of future backtest VARIANTS to test later;
  - the quantitative success target (reuses the review's promotion criteria).

It RUNS NOTHING: no new backtest, no optimization, no parameter search, no
paper/live/micro-live, no broker/exchange, no network, no credentials. It UNLOCKS
no gate. Every control is described as a single pre-registered rule -- this plan
explicitly forbids parameter sweeps; a SEPARATE human command is required before
any variant is ever run.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_MODE
  - RISK_CONTROLS / BACKTEST_VARIANTS / VARIANT_CONSTRAINTS
  - NEXT_REQUIRED_ACTION
  - get_risk_profile_revision_label()
  - proposed_risk_controls()
  - proposed_backtest_variants()
  - variant_constraints()
  - build_revision_plan_from_decision(decision)
  - build_risk_profile_revision_plan(repo_root)
  - validate_risk_profile_revision_plan(plan)
  - render_risk_profile_revision_markdown(plan)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_prep_contract import (
    BASELINE_STRATEGY_ID,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract import (
    DO_NOT_PROMOTE_TO_PAPER_YET,
    build_baseline_review_decision,
    promotion_criteria,
)

PLAN_SCHEMA_VERSION = "strategy_factory_crypto_d1_risk_profile_revision_plan.v1"
PLAN_LABEL = "Crypto-D1 Risk-Profile Revision Plan (research-only, drawdown reduction)"
PLAN_MODE = "RESEARCH_ONLY"

NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RISK_CONTROLLED_VARIANT_BACKTEST_PREP"

# Candidate risk controls. Each is a SINGLE pre-registered rule with an illustrative
# fixed default -- NOT a search space. "targets" links the control to the specific
# blocker / risk note from the baseline review it is meant to address.
RISK_CONTROLS: tuple[dict[str, Any], ...] = (
    {
        "id": "trend_filter",
        "name": "Trend filter (hold only above a long-term moving average)",
        "rule": "Hold a symbol only while its daily close is above a fixed "
                "long-term moving average (default 200-day SMA); otherwise hold "
                "that sleeve in cash. Single fixed window, no sweep.",
        "targets": ["max_drawdown_exceeds_limit", "buy_and_hold_has_no_risk_management"],
        "fixed_rule_no_optimization": True,
    },
    {
        "id": "cash_regime",
        "name": "Cash regime (portfolio-level risk-off)",
        "rule": "When a fixed breadth condition fails (e.g., majority of sleeves "
                "below their trend filter), move the whole portfolio to cash until "
                "breadth recovers. Fixed threshold, no sweep.",
        "targets": ["max_drawdown_exceeds_limit", "single_market_regime_sample"],
        "fixed_rule_no_optimization": True,
    },
    {
        "id": "volatility_cap",
        "name": "Volatility cap / target (inverse-vol position sizing)",
        "rule": "Scale each sleeve's weight inversely to its trailing realized "
                "volatility and cap gross exposure at a fixed ceiling (default "
                "100%). Fixed lookback and ceiling, no sweep.",
        "targets": ["max_drawdown_exceeds_limit"],
        "fixed_rule_no_optimization": True,
    },
    {
        "id": "stop_risk_off",
        "name": "Drawdown stop / risk-off rule",
        "rule": "If portfolio drawdown from its running peak breaches a fixed "
                "threshold (default -25%), move to cash and re-enter only on a "
                "fixed trend re-confirmation. Fixed threshold, no sweep.",
        "targets": ["max_drawdown_exceeds_limit", "buy_and_hold_has_no_risk_management"],
        "fixed_rule_no_optimization": True,
    },
    {
        "id": "periodic_rebalance",
        "name": "Periodic rebalance to target weights",
        "rule": "Rebalance back to target weights on a fixed schedule (default "
                "monthly) instead of letting winners run unbounded. Fixed cadence, "
                "no sweep.",
        "targets": ["return_concentrated_in_SOL", "buy_and_hold_has_no_risk_management"],
        "fixed_rule_no_optimization": True,
    },
    {
        "id": "sol_concentration_cap",
        "name": "Per-asset concentration cap (esp. SOL)",
        "rule": "Cap any single asset's portfolio weight at a fixed ceiling "
                "(default 33%), trimming overweight sleeves on the rebalance "
                "schedule. Fixed ceiling, no sweep.",
        "targets": ["return_concentrated_in_SOL"],
        "fixed_rule_no_optimization": True,
    },
)

# Future backtest variants to test LATER (none run here). Each composes one or more
# fixed controls into a single, pre-registered, long-only strategy hypothesis.
BACKTEST_VARIANTS: tuple[dict[str, Any], ...] = (
    {
        "id": "V1_trend_filter",
        "description": "Equal-weight buy & hold gated by a 200-day trend filter.",
        "controls": ["trend_filter"],
        "hypothesis": "Exiting downtrends to cash cuts max drawdown below the "
                      "-50% promotion floor while retaining most upside.",
    },
    {
        "id": "V2_trend_plus_cash_regime",
        "description": "Trend filter plus a portfolio-level cash regime on weak breadth.",
        "controls": ["trend_filter", "cash_regime"],
        "hypothesis": "A breadth-driven risk-off further compresses the worst "
                      "drawdowns in broad bear phases.",
    },
    {
        "id": "V3_voltarget_concentration_cap",
        "description": "Inverse-vol sizing with a 33% per-asset concentration cap.",
        "controls": ["volatility_cap", "sol_concentration_cap"],
        "hypothesis": "Down-weighting the most volatile / most concentrated sleeve "
                      "(SOL) reduces drawdown and single-name dependence.",
    },
    {
        "id": "V4_monthly_rebalance_capped",
        "description": "Monthly rebalance to capped equal weights.",
        "controls": ["periodic_rebalance", "sol_concentration_cap"],
        "hypothesis": "Systematic trimming of winners limits terminal "
                      "concentration and path risk.",
    },
    {
        "id": "V5_full_risk_managed",
        "description": "All controls combined into one defensive long-only variant.",
        "controls": ["trend_filter", "cash_regime", "volatility_cap",
                     "stop_risk_off", "periodic_rebalance", "sol_concentration_cap"],
        "hypothesis": "The fully risk-managed variant clears the drawdown floor "
                      "with an acceptable Sharpe trade-off.",
    },
)

# Hard constraints any future variant backtest must honor. Same safety envelope as
# the baseline: still long-only, still no optimization / parameter search /
# walk-forward / lookahead. (Cash and rebalancing are allowed; leverage is not.)
VARIANT_CONSTRAINTS: dict[str, Any] = {
    "base_strategy_id": BASELINE_STRATEGY_ID,
    "long_only": True,
    "allow_cash": True,
    "allow_rebalance": True,
    "allow_shorting": False,
    "allow_leverage": False,
    "allow_margin": False,
    "optimization": False,
    "parameter_search": False,
    "walk_forward": False,
    "lookahead_allowed": False,
    "single_pre_registered_parameterization": True,
    "uses_only_qa_passed_inputs": True,
    "writes_orders": False,
    "touches_broker_or_exchange": False,
}


def get_risk_profile_revision_label() -> str:
    """Human label for the recognized Crypto-D1 risk-profile revision plan."""
    return PLAN_LABEL


def proposed_risk_controls() -> list[dict[str, Any]]:
    """Return a fresh deep-ish copy of the candidate risk controls. Pure."""
    return [dict(c, targets=list(c["targets"])) for c in RISK_CONTROLS]


def proposed_backtest_variants() -> list[dict[str, Any]]:
    """Return a fresh copy of the future backtest variants. Pure."""
    return [dict(v, controls=list(v["controls"])) for v in BACKTEST_VARIANTS]


def variant_constraints() -> dict[str, Any]:
    """Return a fresh copy of the variant run constraints. Pure."""
    return dict(VARIANT_CONSTRAINTS)


def build_revision_plan_from_decision(decision: Any) -> dict[str, Any]:
    """Assemble a revision plan from a baseline review decision dict. PURE; never
    raises. A revision is required only when the decision blocked promotion."""
    d = decision if isinstance(decision, dict) else {}
    promotion_decision = d.get("promotion_decision")
    blockers = list(d.get("blockers") or [])
    risk_notes = list(d.get("risk_notes") or [])
    metrics = dict(d.get("metrics_reviewed") or {})

    revision_required = promotion_decision == DO_NOT_PROMOTE_TO_PAPER_YET

    crit = promotion_criteria()
    success_target = {
        "target_max_drawdown": crit["max_acceptable_drawdown"],
        "target_min_sharpe_ratio": crit["min_sharpe_ratio"],
        "target_min_total_return": crit["min_total_return"],
        "primary_objective": "reduce_max_drawdown_within_promotion_floor",
    }

    notes: list[str] = []
    if not revision_required:
        notes.append("baseline_already_eligible_no_revision_required")

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "label": PLAN_LABEL,
        "mode": PLAN_MODE,
        "revision_required": revision_required,
        "trigger": {
            "promotion_decision": promotion_decision,
            "blockers": blockers,
            "risk_notes": risk_notes,
            "metrics_reviewed": metrics,
        },
        "success_target": success_target,
        "risk_controls": proposed_risk_controls(),
        "backtest_variants": proposed_backtest_variants(),
        "variant_constraints": variant_constraints(),
        "notes": notes,
        # Capability posture (this plan executes / authorizes nothing):
        "executes": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "runs_parameter_search": False,
        "authorizes_variant_run": False,
        "authorizes_paper_trading": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this plan):
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_risk_profile_revision_plan(repo_root: str = ".") -> dict[str, Any]:
    """Load the local baseline review decision read-only and build the revision
    plan. Reads only what the review reads; writes nothing; runs no backtest."""
    decision = build_baseline_review_decision(repo_root)
    plan = build_revision_plan_from_decision(decision)
    plan["source_review"] = {
        "promotion_decision": decision.get("promotion_decision"),
        "baseline_report_found": decision.get("baseline_report_found"),
    }
    return plan


def validate_risk_profile_revision_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) a revision plan's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan

    if p.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if not isinstance(p.get("risk_controls"), list) or not p.get("risk_controls"):
        errors.append("no_risk_controls")
    if not isinstance(p.get("backtest_variants"), list) or not p.get("backtest_variants"):
        errors.append("no_backtest_variants")

    # Every control must declare what it targets; nothing may smuggle in optimization.
    for c in p.get("risk_controls") or []:
        if not isinstance(c, dict) or not c.get("targets"):
            errors.append("control_missing_targets")
        elif c.get("fixed_rule_no_optimization") is not True:
            errors.append("control_not_fixed_rule:" + str(c.get("id")))

    constraints = p.get("variant_constraints")
    if not isinstance(constraints, dict):
        errors.append("variant_constraints_missing")
    else:
        for key in ("optimization", "parameter_search", "walk_forward",
                    "allow_shorting", "allow_leverage", "lookahead_allowed"):
            if constraints.get(key) is not False:
                errors.append("constraint_not_false:" + key)

    must_be_locked = (
        "baseline_backtest_blocked",
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
    )
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_backtest",
        "runs_optimization",
        "runs_parameter_search",
        "authorizes_variant_run",
        "authorizes_paper_trading",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def render_risk_profile_revision_markdown(plan: Any) -> str:
    """Render a revision plan as deterministic markdown. Pure string work."""
    p = plan if isinstance(plan, dict) else {}
    trig = p.get("trigger") or {}
    tgt = p.get("success_target") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Risk-Profile Revision Plan (research-only)")
    lines.append("")
    lines.append("- Revision required: " + str(p.get("revision_required", "")))
    lines.append("- Trigger decision: " + str(trig.get("promotion_decision", "")))
    blockers = trig.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    lines.append("## Success target")
    lines.append("- Target max drawdown: " + _pct(tgt.get("target_max_drawdown")))
    lines.append("- Target min Sharpe: " + str(tgt.get("target_min_sharpe_ratio")))
    lines.append("- Primary objective: " + str(tgt.get("primary_objective")))
    lines.append("")
    lines.append("## Candidate risk controls")
    for c in p.get("risk_controls") or []:
        lines.append("- " + str(c.get("id")) + " -- " + str(c.get("name")))
        lines.append("  - targets: " + ", ".join(c.get("targets") or []))
        lines.append("  - rule: " + str(c.get("rule")))
    lines.append("")
    lines.append("## Future backtest variants (NOT run here)")
    for v in p.get("backtest_variants") or []:
        lines.append("- " + str(v.get("id")) + ": " + str(v.get("description")))
        lines.append("  - controls: " + ", ".join(v.get("controls") or []))
        lines.append("  - hypothesis: " + str(v.get("hypothesis")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- baseline_backtest: BLOCKED")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)
