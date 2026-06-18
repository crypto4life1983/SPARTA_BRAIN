"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- CANDIDATE SPEC (PURE, RESEARCH ONLY).

The human-approved (HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT ->
ADVANCE) formal specification for the frozen C17 family proposal: RISK-ADJUSTED
PORTFOLIO CONSTRUCTION -- volatility-targeted / risk-parity allocation across
BTC/ETH/SOL on D1. This is a pure, in-memory specification: it DECLARES the exact
strategy (universe / timeframe / portfolio method / weighting rules / rebalance
cadence / volatility lookback / risk target / gross exposure cap / turnover
constraints / costs / baselines / primary + secondary metrics / OOS validation /
rejection criteria / next human gate) and WHY it is materially different from the
rejected C1-C16 timing families.

It is chain-gated on the committed C17 proposal (it imports it, re-validates it,
and requires the proposal to be frozen for this exact family). It does NOTHING
else: it does NOT fetch data, NOT run a detector, NOT label, NOT replay/backtest,
NOT compute PnL, NOT optimize parameters, NOT write files, NOT stage/commit/push,
and NOT touch any paper/live/broker/credential/order surface. Every capability
flag is pinned False with a full scope_locks set. The next gate (detector spec +
synthetic dry-run) still requires an explicit human decision.

Material difference from C1-C16 (the whole point): every rejected family was a
directional / mean-reversion / pairs TIMING signal judged on RAW net return. This
candidate manages ALLOCATION and RISK (not entry timing), is judged on a
RISK-ADJUSTED basis (Sharpe / Calmar / max-drawdown vs buy-and-hold and an
equal-weight basket), is continuous (ample sample), and is low-turnover by design
(cost-tolerant).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_proposal_contract as _c17  # noqa: E501

C17_SPEC_SCHEMA_VERSION = 1
C17_SPEC_MODE = "RESEARCH_ONLY"
C17_SPEC_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C17"
CANDIDATE_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
CANDIDATE_NAME = (
    "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1")

# Chain gate: the committed C17 proposal must be frozen for this exact family.
EXPECTED_PROPOSAL_VERDICT = "C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

REJECTED_FAMILIES_C1_TO_C16 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- 1/2. universe + timeframe ----------------------------------------------
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"

# --- 3. portfolio method ----------------------------------------------------
PORTFOLIO_METHOD = "volatility_targeted_risk_parity_allocation"

# --- declared (NOT fitted) spec parameters ----------------------------------
# A pre-registered starting specification, not optimized values. No parameter
# search is performed or permitted at this gate.
SPEC_PARAMS = {
    # 4. weighting rules
    "weighting_rule": "inverse_volatility / equal_risk_contribution (risk parity)",
    "weight_floor_per_asset": 0.0,        # long-or-flat; a leg may go to zero
    "weight_cap_per_asset": 1.0,          # no single-leg concentration beyond cap
    # 5. rebalance cadence
    "rebalance_cadence": "weekly",        # low-turnover scheduled rebalance
    "no_trade_band_pct": 0.05,            # threshold band to suppress churn
    "rebalance_on": "weekly_close",
    # 6. volatility lookback
    "realized_vol_lookback_days": 30,     # rolling realized-vol estimate
    "covariance_lookback_days": 60,       # for risk-parity contributions
    # 7. risk target definition
    "target_portfolio_vol_annualized": 0.20,   # constant 20% annualized vol target
    "vol_scaling": "scale gross exposure toward the vol target, capped",
    # 8. gross exposure cap
    "max_gross_exposure": 1.0,            # long/flat basket; no leverage above cap
    "min_gross_exposure": 0.0,            # may de-risk to flat
    "allow_short": False,
    "allow_leverage_above_cap": False,
    # 9. turnover constraints
    "max_avg_weekly_turnover": 0.20,      # cap average turnover (cost-tolerant)
    "no_daily_churn": True,
    "one_edit_allowance_used": False,
}

# --- 9. turnover constraints (declared) -------------------------------------
TURNOVER_CONSTRAINTS = {
    "rebalance_cadence": "weekly",
    "no_trade_band_pct": 0.05,
    "max_avg_weekly_turnover": 0.20,
    "no_high_frequency_churn": True,
    "rationale": ("low turnover by design so the 37 bps all-in cost cannot "
                  "dominate the risk-adjusted edge"),
}

# --- 10. cost assumptions (consistent with the rest of the program) ---------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
COST_ASSUMPTIONS = {
    "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
    "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "cost_charged_on": "each rebalance leg traded (cost scales with turnover)",
    "cost_scales_with_turnover": True,
}

# --- 11. baselines (decisive replay gates; declared, not run) ---------------
BASELINES_REQUIRED = {
    "buy_and_hold_per_asset": {
        "required": True,
        "rule": "matched per-asset BTC/ETH/SOL buy-and-hold over the same window, "
                "net of the same 37 bps"},
    "equal_weight_basket": {
        "required": True,
        "rule": "static equal-weight (1/3 each) BTC/ETH/SOL basket, periodically "
                "rebalanced, net of the same 37 bps"},
}

# --- 12. primary metrics (risk-adjusted) ------------------------------------
PRIMARY_METRICS = ("sharpe_ratio", "calmar_ratio", "max_drawdown")

# --- 13. secondary metrics --------------------------------------------------
SECONDARY_METRICS = ("net_return", "turnover", "fee_drag", "stability")

# --- 14. out-of-sample validation requirement -------------------------------
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

# --- 15. rejection criteria -------------------------------------------------
# The candidate is REJECTED at the replay gate unless ALL of these hold. Raw
# return alone is explicitly NOT sufficient (the axis that rejected C10/C14/C15).
REJECTION_CRITERIA = {
    "reject_if_not_beat_buy_and_hold_risk_adjusted": True,   # Sharpe and/or Calmar
    "reject_if_not_beat_equal_weight_basket_risk_adjusted": True,
    "reject_if_max_drawdown_worse_than_buy_and_hold": True,
    "reject_if_forward_oos_risk_adjusted_edge_fails": True,
    "reject_if_turnover_exceeds_cost_tolerance": True,
    "reject_if_raw_return_only_no_risk_adjusted_edge": True,
    "raw_return_alone_is_not_sufficient": True,
}

# --- 16. next human gate after spec -----------------------------------------
NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C17_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

# --- why materially different from C1-C16 -----------------------------------
MATERIAL_DIFFERENCE_FROM_C1_C16 = (
    "manages ALLOCATION / RISK, not entry TIMING (every C1-C16 family was a timing "
    "signal)",
    "judged on a RISK-ADJUSTED basis (Sharpe / Calmar / max-drawdown), not raw net "
    "return -- the axis that rejected C10/C14/C15",
    "continuous daily allocation -> ample sample size (avoids the C13/C16 rarity "
    "rejection)",
    "low turnover by design -> the 37 bps cost cannot dominate (avoids the C12/C16 "
    "cost-erosion failure)",
    "long-or-flat risk-parity basket, NOT a directional bet and NOT a naive "
    "market-neutral pairs hedge",
)

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
    "uses_one_edit_allowance", "reproposes_rejected_family",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_detector_run": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_optimization": True, "no_robustness": True, "no_portfolio_compute": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_leverage_above_cap": True, "no_shorting": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_one_edit_invocation": True, "no_rejected_family_repropose": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_17_spec_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 (READ-ONLY, RESEARCH ONLY, PURE CANDIDATE SPEC). "
        "Volatility-targeted / risk-parity allocation across BTC/ETH/SOL on D1, "
        "judged on a RISK-ADJUSTED basis (Sharpe / Calmar / max-drawdown) vs "
        "buy-and-hold and an equal-weight basket -- a portfolio-construction / "
        "risk-management edge, not entry timing. SPEC ONLY: the next gate (detector "
        "spec + synthetic dry-run) needs an explicit human decision. NO data fetch, "
        "NO detector, NO labels, NO replay/backtest, NO PnL, NO optimization, NO "
        "paper/live, BUILDS/COMMITS/PUSHES NOTHING. NOT a profitability claim.")


def get_candidate_17_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def build_c17_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #17 candidate-spec record. Pure; no I/O; spec
    only. Chain-gated on the committed C17 proposal (frozen, this exact family)."""
    proposal = _c17.build_c17_proposal(repo_root, tracked_paths)
    proposal_valid = _c17.validate_c17_proposal(proposal)["valid"]
    proposal_verdict = proposal.get("verdict")
    proposal_family = proposal.get("candidate_family")

    blockers: list = []
    if not proposal_valid:
        blockers.append("c17_proposal_invalid")
    if proposal_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c17_proposal_not_frozen")
    if proposal_family != CANDIDATE_FAMILY:
        blockers.append("proposal_family_mismatch")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C16:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C17_SPEC_SCHEMA_VERSION, "mode": C17_SPEC_MODE,
        "lane": C17_SPEC_LANE,
        "label": get_candidate_17_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C17_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C17_SPEC_BLOCKED"),
        # chain provenance
        "source_proposal_verdict": proposal_verdict,
        "source_proposal_valid": proposal_valid,
        "source_proposal_family": proposal_family,
        # the spec (the 16 required sections)
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,            # 1, 2
        "portfolio_method": PORTFOLIO_METHOD,                       # 3
        "spec_params": dict(SPEC_PARAMS),                           # 4-9
        "turnover_constraints": dict(TURNOVER_CONSTRAINTS),         # 9
        "cost_assumptions": dict(COST_ASSUMPTIONS),                 # 10
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "baselines_required": {k: dict(v) for k, v in BASELINES_REQUIRED.items()},  # 11
        "primary_metrics": list(PRIMARY_METRICS),                   # 12
        "secondary_metrics": list(SECONDARY_METRICS),               # 13
        "oos_validation": dict(OOS_VALIDATION),                     # 14
        "rejection_criteria": dict(REJECTION_CRITERIA),             # 15
        "next_human_gate_after_spec": NEXT_HUMAN_GATE_AFTER_SPEC,   # 16
        # identity / anti-loop
        "material_difference_from_c1_c16": list(MATERIAL_DIFFERENCE_FROM_C1_C16),
        "is_portfolio_construction": True,
        "is_volatility_targeted": True,
        "is_risk_parity": True,
        "is_directional_timing_signal": False,
        "is_market_neutral_pairs": False,
        "rejected_families_c1_to_c16": list(REJECTED_FAMILIES_C1_TO_C16),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C16),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C16,
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_SPEC,
        # downstream gates explicitly locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_c17_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C17 proposal for this exact family, a
    portfolio-construction (not timing / not pairs) candidate NOT in the C1-C16
    ledger, carries all 16 sections (universe / timeframe / method / weighting /
    rebalance / vol lookback / risk target / gross cap / turnover / costs /
    baselines / primary + secondary metrics / OOS / rejection criteria / next
    gate), preserves the gate sequence, keeps downstream gates locked, and pins
    every capability flag False."""
    failures: list = []
    if record.get("mode") != C17_SPEC_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the C17 proposal
    if record.get("source_proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("source_proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("source_proposal_family") != CANDIDATE_FAMILY:
        failures.append("proposal_family_mismatch")

    # identity + anti-loop
    if record.get("is_portfolio_construction") is not True:
        failures.append("not_portfolio_construction")
    if record.get("is_volatility_targeted") is not True:
        failures.append("not_volatility_targeted")
    if record.get("is_risk_parity") is not True:
        failures.append("not_risk_parity")
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
    if len(record.get("material_difference_from_c1_c16") or []) < 5:
        failures.append("insufficient_material_difference")

    # the 16 required sections present
    for field in ("symbols", "timeframe", "portfolio_method", "spec_params",
                  "turnover_constraints", "cost_assumptions", "baselines_required",
                  "primary_metrics", "secondary_metrics", "oos_validation",
                  "rejection_criteria", "next_human_gate_after_spec"):
        if not record.get(field):
            failures.append("spec_missing_%s" % field)
    if list(record.get("symbols") or []) != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        failures.append("symbols_not_btc_eth_sol")
    if record.get("timeframe") != "D1":
        failures.append("timeframe_not_d1")
    if record.get("portfolio_method") != PORTFOLIO_METHOD:
        failures.append("portfolio_method_tampered")

    # weighting / rebalance / vol-lookback / risk-target / gross-cap / turnover
    sp = record.get("spec_params") or {}
    if not sp.get("weighting_rule"):
        failures.append("weighting_rule_missing")
    if not sp.get("rebalance_cadence"):
        failures.append("rebalance_cadence_missing")
    if not sp.get("realized_vol_lookback_days"):
        failures.append("vol_lookback_missing")
    if not sp.get("target_portfolio_vol_annualized"):
        failures.append("risk_target_missing")
    if sp.get("max_gross_exposure") != 1.0:
        failures.append("gross_cap_tampered")
    if sp.get("allow_short") is not False:
        failures.append("shorting_not_forbidden")
    if sp.get("allow_leverage_above_cap") is not False:
        failures.append("leverage_not_forbidden")
    if not sp.get("max_avg_weekly_turnover"):
        failures.append("turnover_cap_missing")

    # costs intact (37 bps)
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)) != 37.0:
        failures.append("cost_split_tampered")
    if (record.get("cost_assumptions") or {}).get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_assumptions_tampered")

    # baselines: per-asset buy-and-hold AND equal-weight basket
    br = record.get("baselines_required") or {}
    if (br.get("buy_and_hold_per_asset") or {}).get("required") is not True:
        failures.append("buy_and_hold_baseline_not_required")
    if (br.get("equal_weight_basket") or {}).get("required") is not True:
        failures.append("equal_weight_baseline_not_required")

    # primary metrics risk-adjusted; secondary metrics present
    prim = record.get("primary_metrics") or []
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in prim:
            failures.append("primary_metric_missing_%s" % m)
    sec = record.get("secondary_metrics") or []
    for m in ("net_return", "turnover", "fee_drag", "stability"):
        if m not in sec:
            failures.append("secondary_metric_missing_%s" % m)

    # OOS required, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("forward_oos_must_hold_risk_adjusted_edge") is not True:
        failures.append("oos_risk_adjusted_not_required")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    if oos.get("durability_window_days") != 1095:
        failures.append("durability_window_not_3yr")

    # rejection criteria: risk-adjusted bar; raw return alone insufficient
    rc = record.get("rejection_criteria") or {}
    for k in ("reject_if_not_beat_buy_and_hold_risk_adjusted",
              "reject_if_not_beat_equal_weight_basket_risk_adjusted",
              "reject_if_max_drawdown_worse_than_buy_and_hold",
              "reject_if_forward_oos_risk_adjusted_edge_fails",
              "raw_return_alone_is_not_sufficient"):
        if rc.get(k) is not True:
            failures.append("rejection_criterion_off_%s" % k)

    # gate sequence + next gate + downstream locks
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    if record.get("next_human_gate_after_spec") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_gate_field_tampered")
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_data_fetch", "no_detector_run", "no_labels",
                "no_replay", "no_backtest", "no_pnl", "no_optimization",
                "no_commit", "no_push", "no_auto_commit", "no_auto_push",
                "no_broker", "no_order_logic", "no_leverage_above_cap",
                "no_shorting", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
