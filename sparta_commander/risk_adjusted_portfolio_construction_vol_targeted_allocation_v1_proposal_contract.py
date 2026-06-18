"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY).

The formal candidate proposal for the human-approved next research direction
(approved via HUMAN_DECISION_APPROVE_NEXT_RESEARCH_DIRECTION_THEN_BUILD_CANDIDATE_
PROPOSAL): RISK-ADJUSTED PORTFOLIO CONSTRUCTION -- volatility-targeted / risk-
parity allocation across BTC/ETH/SOL. Chain-gated on the committed next-strategy
research memo (the memo must recommend exactly this direction).

It is a PROPOSAL only: it DECLARES the strategy thesis, why it differs from the
rejected C1-C16 families, the universe, the portfolio-construction idea, the
evaluation metrics, the cost/turnover assumptions, the out-of-sample validation
requirement, the safety boundaries, and the next human gate. It builds NO detector,
NO labels, NO replay; runs NO PnL/optimization/data fetch; touches NO paper/live/
broker/order surface. Every capability flag is pinned False with a full scope_locks
set. Advancing to the candidate-spec gate needs an explicit human decision.

Why it is genuinely different from C1-C16: every rejected family was a directional /
mean-reversion / pairs TIMING signal judged on RAW net return, and they failed by
losing to buy-and-hold's raw crypto beta (C10/C14/C15), being too rare (C13/C16),
or being eroded by cost (C12/C16). This candidate manages ALLOCATION and RISK
rather than timing entries, and is judged on a RISK-ADJUSTED basis (Sharpe /
Calmar / max-drawdown vs buy-and-hold) -- a different mechanism AND a different
success axis -- continuous (ample sample) and low-turnover (cost-tolerant).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.automation_readiness_next_strategy_research_memo_v1_contract as _memo  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

C17_SCHEMA_VERSION = 1
C17_MODE = "RESEARCH_ONLY"
C17_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C17"
CANDIDATE_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
CANDIDATE_NAME = (
    "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1")
APPROVED_DIRECTION_KEY = CANDIDATE_FAMILY

REJECTED_FAMILIES_C1_TO_C16 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"

# --- 1. strategy thesis -----------------------------------------------------
STRATEGY_THESIS = (
    "Hold the BTC/ETH/SOL basket continuously but SIZE it by risk, not by a "
    "directional view: target a constant portfolio volatility and weight the legs "
    "toward risk parity (inverse-volatility / equal-risk-contribution), rebalanced "
    "on a low-turnover schedule. The thesis is that disciplined risk-based "
    "allocation delivers a BETTER RISK-ADJUSTED outcome than a static buy-and-hold "
    "basket -- comparable or better return for materially lower drawdown/volatility "
    "-- without trying to predict direction.")

# --- 2. why different from C1-C16 -------------------------------------------
WHY_DIFFERENT_FROM_C1_C16 = (
    "manages ALLOCATION / RISK, not entry TIMING (every C1-C16 family was a timing "
    "signal)",
    "judged on a RISK-ADJUSTED basis (Sharpe / Calmar / max-drawdown vs "
    "buy-and-hold), not raw net return -- the axis that rejected C10/C14/C15",
    "continuous daily allocation -> ample sample size (avoids the C13/C16 rarity "
    "structural rejection)",
    "low turnover by design -> the 37 bps cost cannot dominate (avoids the "
    "C12/C16 cost-erosion failure)",
    "not a directional bet and not a naive market-neutral hedge -> avoids both the "
    "long-bull carry trap and the C16 unvalidated-neutrality failure",
)

# --- 4. portfolio construction idea -----------------------------------------
PORTFOLIO_CONSTRUCTION_IDEA = {
    "method": "volatility_targeting_plus_risk_parity",
    "risk_parity_weighting": "inverse_volatility / equal_risk_contribution",
    "volatility_target": "constant portfolio volatility (e.g. ~20% annualized)",
    "max_gross_exposure_cap": 1.0,        # long/flat basket; no leverage beyond cap
    "direction": "long_or_flat_basket (no shorting, no leverage above the cap)",
    "rebalance_policy": "low-turnover: scheduled (e.g. weekly) or no-trade-band "
                        "threshold rebalance, not daily churn",
}

# --- 5. evaluation metrics --------------------------------------------------
EVALUATION_METRICS = {
    "primary_risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "turnover": "average rebalance turnover (must stay low / cost-tolerant)",
    "net_return_vs_buy_and_hold": "net return after 37 bps vs matched B&H basket",
    "baseline": "matched buy-and-hold equal-weight (or cap-weight) BTC/ETH/SOL "
                "basket, net of the same 37 bps",
    "win_condition": ("BEAT matched buy-and-hold on a RISK-ADJUSTED basis -- higher "
                      "Sharpe AND/OR Calmar with no worse max-drawdown -- not "
                      "merely higher raw return"),
}

# --- 6. cost assumptions + turnover constraints -----------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_AND_TURNOVER = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "cost_scales_with_turnover": True,
    "turnover_constraint": ("prefer weekly or threshold-band rebalancing; cap "
                            "average turnover so the 37 bps all-in cost cannot "
                            "dominate the risk-adjusted edge"),
    "no_high_frequency_churn": True,
}

# --- 7. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_risk_adjusted_edge": True,
    "durability_window_days": 1095,            # 3-year durability
    "recent_relevance_window_days_min": 90,    # recent 3-month relevance
    "recent_relevance_window_days_max": 180,   # recent 6-month relevance
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- 8. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no "
    "orders, no credentials, no data fetch",
    "long-or-flat basket only -- no shorting and no leverage above the gross cap",
    "no parameter optimization / curve fitting; pre-registered construction",
    "every downstream gate (spec / detector / labels / replay / paper / live) stays "
    "human-gated and locked",
    "promotion requires beating buy-and-hold RISK-ADJUSTED and surviving "
    "forward-OOS -- the same evidence bar that rejected C1-C16",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

# --- decisive promote criteria (declared; evaluated only at the replay gate) -
DECISIVE_PROMOTE_CRITERIA = {
    "beats_buy_and_hold_risk_adjusted": True,   # Sharpe and/or Calmar
    "max_drawdown_no_worse_than_buy_and_hold": True,
    "forward_oos_risk_adjusted_edge_holds": True,
    "turnover_sane_cost_tolerant": True,
    "structural_sample_size_gate": {"min_observations_total": 100,
                                    "continuous_daily_allocation": True},
    "raw_return_alone_is_not_sufficient": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "uses_leverage_above_cap", "shorts", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reproposes_rejected_family", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_17_proposal_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 family proposal (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). "
        "Vol-targeted / risk-parity allocation across BTC/ETH/SOL, judged on a "
        "RISK-ADJUSTED basis (Sharpe / Calmar / max-drawdown) vs buy-and-hold -- a "
        "portfolio-construction / risk-management edge, not entry timing. PROPOSAL "
        "ONLY: advancing to the candidate-spec gate needs an explicit human "
        "decision. NO detector, NO labels, NO replay, NO optimization, NO data "
        "fetch, NO paper/live. NOT a profitability claim.")


def get_candidate_17_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def build_c17_proposal(repo_root: Any = ".",
                       tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #17 family-proposal record. Pure; no I/O;
    proposal only. Chain-gated on the next-strategy research memo (which must
    recommend this exact direction)."""
    memo = _memo.build_next_strategy_research_memo()
    memo_valid = _memo.validate_next_strategy_research_memo(memo)["valid"]
    memo_recommends_this = memo.get("recommended_direction_key") == (
        APPROVED_DIRECTION_KEY)

    blockers: list = []
    if not memo_valid:
        blockers.append("next_strategy_memo_invalid")
    if not memo_recommends_this:
        blockers.append("memo_does_not_recommend_this_direction")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C16:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C17_SCHEMA_VERSION, "mode": C17_MODE, "lane": C17_LANE,
        "label": get_candidate_17_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C17_PROPOSAL_BLOCKED"),
        # chain provenance
        "approved_direction_key": APPROVED_DIRECTION_KEY,
        "approved_via": ("HUMAN_DECISION_APPROVE_NEXT_RESEARCH_DIRECTION_THEN_"
                         "BUILD_CANDIDATE_PROPOSAL"),
        "source_memo_recommends_this": memo_recommends_this,
        "source_memo_valid": memo_valid,
        # the 9 required explanation sections
        "strategy_thesis": STRATEGY_THESIS,                          # 1
        "why_different_from_c1_c16": list(WHY_DIFFERENT_FROM_C1_C16),  # 2
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,            # 3
        "portfolio_construction_idea": dict(PORTFOLIO_CONSTRUCTION_IDEA),  # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),         # 5
        "cost_and_turnover": dict(COST_AND_TURNOVER),               # 6
        "oos_validation": dict(OOS_VALIDATION),                     # 7
        "safety_boundaries": list(SAFETY_BOUNDARIES),               # 8
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,  # 9
        # identity / anti-loop
        "is_portfolio_construction": True,
        "is_directional_timing_signal": False,
        "is_market_neutral_pairs": False,
        "decisive_promote_criteria": _deepish(DECISIVE_PROMOTE_CRITERIA),
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c16": list(REJECTED_FAMILIES_C1_TO_C16),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C16),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C16,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        # downstream gates locked
        "spec_gate_locked": True, "detector_gate_locked": True,
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_robustness": True, "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_leverage_above_cap": True, "no_shorting": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def validate_c17_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the memo recommending this exact direction, is a
    portfolio-construction (not timing / not pairs) candidate NOT in the C1-C16
    ledger, carries all 9 explanation sections + the risk-adjusted evaluation
    metrics + OOS requirement, preserves the gate sequence, keeps downstream gates
    locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C17_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the memo
    if record.get("source_memo_recommends_this") is not True:
        failures.append("memo_does_not_recommend_this")
    if record.get("source_memo_valid") is not True:
        failures.append("memo_not_valid")
    if record.get("approved_direction_key") != APPROVED_DIRECTION_KEY:
        failures.append("approved_direction_mismatch")

    # identity + anti-loop
    if record.get("is_portfolio_construction") is not True:
        failures.append("not_portfolio_construction")
    if record.get("is_directional_timing_signal") is not False:
        failures.append("must_not_be_directional_timing")
    if record.get("is_market_neutral_pairs") is not False:
        failures.append("must_not_be_pairs")
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C16:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 21:
        failures.append("ledger_not_21")

    # the 9 explanation sections present
    for field in ("strategy_thesis", "why_different_from_c1_c16", "symbols",
                  "portfolio_construction_idea", "evaluation_metrics",
                  "cost_and_turnover", "oos_validation", "safety_boundaries",
                  "next_human_gate_after_proposal"):
        if not record.get(field):
            failures.append("proposal_missing_%s" % field)
    if list(record.get("symbols") or []) != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        failures.append("symbols_not_btc_eth_sol")
    if len(record.get("why_different_from_c1_c16") or []) < 5:
        failures.append("insufficient_difference_explanation")

    # evaluation metrics: risk-adjusted, vs buy-and-hold, with turnover
    em = record.get("evaluation_metrics") or {}
    prim = em.get("primary_risk_adjusted") or ()
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in prim:
            failures.append("metric_missing_%s" % m)
    if not em.get("turnover"):
        failures.append("turnover_metric_missing")
    if not em.get("net_return_vs_buy_and_hold"):
        failures.append("net_vs_bh_metric_missing")
    if "risk-adjusted" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_risk_adjusted")

    # cost (37 bps) + turnover constraint
    ct = record.get("cost_and_turnover") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if not ct.get("turnover_constraint"):
        failures.append("turnover_constraint_missing")

    # OOS required, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("forward_oos_must_hold_risk_adjusted_edge") is not True:
        failures.append("oos_risk_adjusted_not_required")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # gate sequence + downstream locks
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_leverage_above_cap",
                "no_shorting", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
