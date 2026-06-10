"""Crypto-D1 V2 Resume-Policy Research & Simulation Plan (READ-ONLY, PLAN ONLY).

A PURE, stdlib-only, read-only module that PLANS (but never runs) research into SAFE
RESUME POLICIES for the single selected variant ``V2_trend_plus_cash_regime`` after its
simulated paper run tripped the kill switch (daily-loss halt on 2021-05-19), flattened
to cash, and stayed HALTED pending a human resume decision.

The simulated paper-run review returned DO_NOT_PROMOTE_TO_MICRO_LIVE_YET with three
blockers this plan is designed to address:
  - run_halted_pending_human_resume        -> define explicit, fixed resume rules;
  - kill_switch_triggered_needs_resume_policy_review -> pre-register resume candidates;
  - insufficient_regime_evidence_for_micro_live      -> plan multi-regime simulated reruns.

It pre-registers a FIXED, hand-specified set of resume-policy candidates (no search, no
optimization, no fitting) and a FIXED set of FUTURE simulated paper reruns that would
test them over already-QA-passed local data sub-windows (no new data, no fetch).

It RUNS NOTHING: no new simulation, no backtest, no optimization, no parameter search,
no paper/live/micro-live, no broker/exchange, no network, no credentials, no real order.
It writes nothing to disk. It UNLOCKS no gate: paper_trading_gate, micro_live_gate and
the live gate all stay LOCKED. Actually running any of the planned reruns requires a
SEPARATE explicit human command.

Public API:
  - PLAN_SCHEMA_VERSION / PLAN_LABEL / PLAN_MODE
  - SELECTED_VARIANT_ID / VERDICT_PLAN_READY / NEXT_REQUIRED_ACTION
  - ADDRESSES_BLOCKERS / EVIDENCE_SNAPSHOT
  - RESUME_POLICY_CANDIDATES / SIMULATION_RERUN_PLAN / REGIMES_TO_COVER
  - get_resume_policy_plan_label()
  - resume_policy_candidates() / simulation_rerun_plan() / regimes_to_cover()
  - build_resume_policy_plan(repo_root)
  - validate_resume_policy_plan(plan)
  - render_resume_policy_plan_markdown(plan)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_paper_run_review_contract import (
    DO_NOT_PROMOTE_TO_MICRO_LIVE_YET,
    build_paper_run_review_decision,
)

PLAN_SCHEMA_VERSION = "strategy_factory_crypto_d1_resume_policy_research_plan.v1"
PLAN_LABEL = "Crypto-D1 V2 Resume-Policy Research & Simulation Plan (READ-ONLY, PLAN ONLY)"
PLAN_MODE = "RESEARCH_ONLY"

VERDICT_PLAN_READY = "PLAN_READY"

NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RESUME_POLICY_SIMULATION_RERUN"

# The micro-live review blockers this research plan is designed to retire.
ADDRESSES_BLOCKERS: list[str] = [
    "run_halted_pending_human_resume",
    "kill_switch_triggered_needs_resume_policy_review",
    "insufficient_regime_evidence_for_micro_live",
]

# Read-only context snapshot (descriptive evidence; not recomputed here).
EVIDENCE_SNAPSHOT: dict[str, Any] = {
    "variant_backtest": {"total_return": 11.5528, "max_drawdown": -0.4816, "sharpe_ratio": 1.10},
    "simulated_paper_run": {"total_return": 0.6089, "max_drawdown": -0.3226, "sharpe_ratio": 0.53},
    "kill_switch_event": {"date": "2021-05-19", "reason": "daily_loss_halt",
                          "action": "FLATTEN_TO_CASH_AND_HALT", "auto_resume": False},
    "review_decision": DO_NOT_PROMOTE_TO_MICRO_LIVE_YET,
}

# Fixed, pre-registered resume-policy candidates. Every parameter is hand-specified; this
# is a research design, NOT a search space and NOT something to optimize.
RESUME_POLICY_CANDIDATES: list[dict[str, Any]] = [
    {
        "policy_id": "RP1_wait_7d_trend_on",
        "description": "Resume after >= 7 days halted, only if the 200-day trend filter is back on for >= 2 of 3 sleeves.",
        "resume_trigger": {
            "type": "time_and_trend",
            "min_days_halted": 7,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
        },
        "reentry_exposure": "FULL",
        "hypothesis": "A short cool-off plus trend re-confirmation avoids re-entering into the same crash leg.",
    },
    {
        "policy_id": "RP2_wait_14d_trend_on",
        "description": "Resume after >= 14 days halted, only if trend filter is back on for >= 2 of 3 sleeves.",
        "resume_trigger": {
            "type": "time_and_trend",
            "min_days_halted": 14,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
        },
        "reentry_exposure": "FULL",
        "hypothesis": "A two-week cool-off trades some upside for fewer whipsaw re-entries.",
    },
    {
        "policy_id": "RP3_wait_30d_trend_on",
        "description": "Resume after >= 30 days halted, only if trend filter is back on for >= 2 of 3 sleeves.",
        "resume_trigger": {
            "type": "time_and_trend",
            "min_days_halted": 30,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
        },
        "reentry_exposure": "FULL",
        "hypothesis": "A month-long cool-off most strongly avoids dead-cat-bounce re-entries at the cost of lag.",
    },
    {
        "policy_id": "RP4_breadth_2of3_above_sma200",
        "description": "Resume as soon as >= 2 of 3 assets close above their 200-day SMA (no minimum wait).",
        "resume_trigger": {
            "type": "breadth_only",
            "min_days_halted": 0,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
        },
        "reentry_exposure": "FULL",
        "hypothesis": "Pure trend-breadth re-entry is the most responsive; test whether it re-enters too early.",
    },
    {
        "policy_id": "RP5_half_then_full_on_confirmation",
        "description": "Resume at HALF exposure once breadth returns, then scale to FULL after 5 confirming days.",
        "resume_trigger": {
            "type": "staged_exposure",
            "min_days_halted": 0,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
            "confirmation_days": 5,
        },
        "reentry_exposure": "HALF_THEN_FULL",
        "exposure_stages": [0.5, 1.0],
        "hypothesis": "Staging exposure caps the cost of a false re-entry while still participating early.",
    },
    {
        "policy_id": "RP6_resume_after_volatility_cools",
        "description": "Resume only when 30-day realized volatility falls back to/below its pre-halt median, with breadth >= 2.",
        "resume_trigger": {
            "type": "volatility_cooldown",
            "min_days_halted": 0,
            "require_trend_filter_on": True,
            "sma_window_days": 200,
            "breadth_required": 2,
            "vol_lookback_days": 30,
            "vol_reference": "pre_halt_median",
        },
        "reentry_exposure": "FULL",
        "hypothesis": "Waiting for volatility to normalize avoids resuming into a still-disorderly tape.",
    },
]

# Multi-regime evidence is required before micro-live. These are FIXED sub-windows of the
# ALREADY-QA-PASSED local data -- no new data is fetched; the existing CSVs are simply
# evaluated over named sub-periods.
REGIMES_TO_COVER: list[dict[str, Any]] = [
    {"regime_id": "2021_bull_then_may_crash", "window": "2020-08-11..2021-12-31",
     "character": "strong uptrend punctuated by the 2021-05-19 crash that tripped the halt"},
    {"regime_id": "2022_bear", "window": "2022-01-01..2022-12-31",
     "character": "sustained downtrend; tests that resume rules stay defensive"},
    {"regime_id": "2023_2024_recovery", "window": "2023-01-01..2024-12-31",
     "character": "choppy recovery; tests whipsaw / false-resume behavior"},
    {"regime_id": "2025_2026_recent", "window": "2025-01-01..2026-06-08",
     "character": "most recent regime; out-of-the-crash generalization"},
]


def get_resume_policy_plan_label() -> str:
    """Human label for the recognized Crypto-D1 V2 resume-policy research plan."""
    return PLAN_LABEL


def resume_policy_candidates() -> list[dict[str, Any]]:
    """Return fresh deep copies of the fixed resume-policy candidates. Pure."""
    return [copy.deepcopy(p) for p in RESUME_POLICY_CANDIDATES]


def regimes_to_cover() -> list[dict[str, Any]]:
    """Return fresh copies of the fixed multi-regime evaluation sub-windows. Pure."""
    return [dict(r) for r in REGIMES_TO_COVER]


def simulation_rerun_plan() -> list[dict[str, Any]]:
    """Build the FIXED future simulated-rerun plan: one planned rerun per resume-policy
    candidate, each covering every regime sub-window, each NOT YET RUN and each gated on
    a separate explicit human command. Pure; runs nothing."""
    regime_ids = [r["regime_id"] for r in REGIMES_TO_COVER]
    plan: list[dict[str, Any]] = []
    for p in RESUME_POLICY_CANDIDATES:
        plan.append({
            "rerun_id": "RERUN_" + p["policy_id"],
            "policy_id": p["policy_id"],
            "selected_variant_id": SELECTED_VARIANT_ID,
            "data_scope": "QA_PASSED_LOCAL_CSV_ONLY",
            "regimes_to_cover": list(regime_ids),
            "metrics_to_collect": [
                "total_return", "max_drawdown", "sharpe_ratio",
                "time_in_market", "num_resume_events", "post_resume_drawdown",
            ],
            "is_run": False,
            "requires_human_command": True,
            "authorization_required": NEXT_REQUIRED_ACTION,
        })
    return plan


def build_resume_policy_plan(repo_root: str = ".") -> dict[str, Any]:
    """Assemble the full read-only resume-policy research plan. Best-effort reads the
    local simulated paper-run review decision (read-only) to attach the CURRENT blockers
    this plan addresses; never fails if that report is absent. Writes nothing; runs no
    simulation; unlocks no gate."""
    try:
        review = build_paper_run_review_decision(repo_root)
        current_decision = review.get("micro_live_decision")
        current_blockers = list(review.get("blockers") or [])
    except Exception:  # pragma: no cover - defensive; the review never raises in practice
        current_decision = None
        current_blockers = []

    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "label": PLAN_LABEL,
        "mode": PLAN_MODE,
        "verdict": VERDICT_PLAN_READY,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "evidence_snapshot": copy.deepcopy(EVIDENCE_SNAPSHOT),
        "addresses_blockers": list(ADDRESSES_BLOCKERS),
        "current_review_decision": current_decision,
        "current_review_blockers": current_blockers,
        "resume_policy_candidates": resume_policy_candidates(),
        "regimes_to_cover": regimes_to_cover(),
        "simulation_rerun_plan": simulation_rerun_plan(),
        # Capability posture (this is a PLAN; it executes / runs / authorizes nothing):
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "runs_parameter_search": False,
        "executes": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this plan):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_resume_policy_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) a resume-policy plan's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan

    if p.get("verdict") != VERDICT_PLAN_READY:
        errors.append("bad_verdict")
    if p.get("schema_version") != PLAN_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if p.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    candidates = p.get("resume_policy_candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("no_resume_policy_candidates")
        candidates = []
    policy_ids: set[str] = set()
    for c in candidates:
        if not isinstance(c, dict):
            errors.append("candidate_not_a_dict")
            continue
        for key in ("policy_id", "description", "resume_trigger", "reentry_exposure", "hypothesis"):
            if key not in c:
                errors.append("candidate_missing_field:" + key)
        pid = c.get("policy_id")
        if pid in policy_ids:
            errors.append("duplicate_policy_id:" + str(pid))
        if isinstance(pid, str):
            policy_ids.add(pid)

    reruns = p.get("simulation_rerun_plan")
    if not isinstance(reruns, list) or not reruns:
        errors.append("no_simulation_rerun_plan")
        reruns = []
    referenced: set[str] = set()
    for r in reruns:
        if not isinstance(r, dict):
            errors.append("rerun_not_a_dict")
            continue
        # No rerun may be marked as already run -- this is a plan, nothing has executed.
        if r.get("is_run") is not False:
            errors.append("rerun_marked_run:" + str(r.get("rerun_id")))
        if r.get("requires_human_command") is not True:
            errors.append("rerun_not_human_gated:" + str(r.get("rerun_id")))
        rpid = r.get("policy_id")
        if rpid not in policy_ids:
            errors.append("rerun_references_unknown_policy:" + str(rpid))
        if isinstance(rpid, str):
            referenced.add(rpid)
    missing = policy_ids - referenced
    if missing:
        errors.append("policies_without_rerun:" + ",".join(sorted(missing)))

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "runs_parameter_search",
        "executes",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_resume_policy_plan_markdown(plan: Any) -> str:
    """Render a resume-policy research plan as deterministic markdown. Pure string work."""
    p = plan if isinstance(plan, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 Resume-Policy Research & Simulation Plan (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- Selected variant: " + str(p.get("selected_variant_id", "")))
    lines.append("- Addresses blockers: " + ", ".join(p.get("addresses_blockers") or []))
    lines.append("- Current review decision: " + str(p.get("current_review_decision")))
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    lines.append("## Resume-policy candidates (fixed, pre-registered)")
    for c in p.get("resume_policy_candidates") or []:
        lines.append("### " + str(c.get("policy_id")))
        lines.append("- " + str(c.get("description")))
        lines.append("- Re-entry exposure: " + str(c.get("reentry_exposure")))
        lines.append("- Hypothesis: " + str(c.get("hypothesis")))
    lines.append("")
    lines.append("## Multi-regime coverage (existing QA-passed data sub-windows)")
    for r in p.get("regimes_to_cover") or []:
        lines.append("- " + str(r.get("regime_id")) + " (" + str(r.get("window")) + "): " + str(r.get("character")))
    lines.append("")
    lines.append("## Planned simulated reruns (NOT YET RUN)")
    for r in p.get("simulation_rerun_plan") or []:
        lines.append("- " + str(r.get("rerun_id")) + " -> policy " + str(r.get("policy_id"))
                     + " | is_run: " + str(r.get("is_run"))
                     + " | requires_human_command: " + str(r.get("requires_human_command")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- runs_simulation: False (a separate human command is required to run any rerun)")
    return "\n".join(lines)
