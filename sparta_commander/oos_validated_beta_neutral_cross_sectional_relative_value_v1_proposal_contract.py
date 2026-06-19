"""Candidate #19 -- oos_validated_beta_neutral_cross_sectional_relative_value_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY).

The formal candidate-family proposal for the human-approved C19 research direction
(HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL), promoted from
the committed C19 research-direction recommendation. Chain-gated on that recommendation
(it imports it, re-validates it, and requires that its PREFERRED direction is exactly
this family).

THESIS: stop trying to out-risk-adjust buy-and-hold with long-biased exposure (the
rock C17 and C18 both died on) and instead trade a MARKET-NEUTRAL edge that carries NO
buy-and-hold beta -- a continuous dollar- AND return-beta-neutral cross-sectional
relative-value residual among BTC/ETH/SOL, built in RETURN space, where the
neutrality is VALIDATED OUT-OF-SAMPLE as GATE ZERO before any trading logic, then the
neutral residual is traded on mean reversion. Judged net-positive vs random / null
(not against holding BTC), continuous (ample sample), and low-turnover (cost-tolerant).

It is a PROPOSAL only: it DECLARES the family thesis, why it differs from the rejected
C1-C18 families (especially C16 / C17 / C18), the universe and the gate-zero
OOS-neutrality requirement, the six candidate SUB-APPROACHES to compare, the
evaluation metrics, the cost assumptions, the data requirements (cached BTC/ETH/SOL D1
only -- nothing fetched), the out-of-sample requirement, the safety boundaries, and
the next human gate. It builds NO detector, NO labels, NO replay; runs NO PnL /
optimization / data fetch; touches NO paper/live/broker/order surface; and does NOT
start C20. Every capability flag is pinned False with a full scope_locks set.
Advancing to the candidate-spec gate needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c19_research_direction_recommendation_v1_contract as _rec
import sparta_commander.research_expansion_plan_v1_contract as _rep

C19_SCHEMA_VERSION = 1
C19_MODE = "RESEARCH_ONLY"
C19_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C19"
CANDIDATE_FAMILY = "oos_validated_beta_neutral_cross_sectional_relative_value"
CANDIDATE_NAME = "oos_validated_beta_neutral_cross_sectional_relative_value_v1"

REJECTED_FAMILIES_C1_TO_C18 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C18)   # 23

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + data (cached BTC/ETH/SOL D1 spot ONLY; nothing fetched) ------
UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"
DATA_REQUIREMENTS = {
    "btc_eth_sol_d1_spot": {"required": True, "available_locally": True,
                            "note": "the existing cached C16/C17 BTC/ETH/SOL D1 "
                                    "spot OHLCV -- already present, no fetch"},
    "no_data_fetched_here": True,
    "no_new_data_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- 1. family thesis -------------------------------------------------------
FAMILY_THESIS = (
    "Build a CONTINUOUS dollar-neutral AND return-beta-neutral cross-sectional "
    "relative-value residual among BTC/ETH/SOL in RETURN space. Estimate the "
    "return-beta hedge ratios that make the long-short combination beta-neutral, "
    "VALIDATE that neutrality OUT-OF-SAMPLE as gate zero (net residual beta ~ 0 on "
    "unseen data), and only THEN trade mean-reversion of the neutral residual. "
    "Because the position carries no net market exposure, there is no buy-and-hold "
    "beta to lose to -- success is a net-positive market-neutral residual edge vs "
    "random / null, to be PROVEN (not assumed), surviving fees and forward-OOS.")

# --- 2. why different from C1-C18 (esp. C16/C17/C18) ------------------------
WHY_DIFFERENT_FROM_C1_C18 = (
    "MARKET-NEUTRAL by construction: every C1-C18 family carried net long / "
    "directional crypto beta; C17 and C18 cut drawdown but still could not beat "
    "buy-and-hold RISK-ADJUSTED -- this family has NO buy-and-hold beta to beat and "
    "is judged net-positive vs random / null instead",
    "vs C16 (cointegration pairs): C16 assumed neutrality from a level-OLS hedge on "
    "PRICE LEVELS that failed OOS (net beta 2.82) with too few cointegration windows "
    "(43); this is a RETURNS-space, beta-neutral, CONTINUOUS residual whose "
    "neutrality is an OOS-VALIDATED GATE (gate zero), not an assumption",
    "vs C17 (vol-targeted / risk-parity allocation): C17 was a LONG-ONLY allocation "
    "judged vs buy-and-hold; this is a DOLLAR-NEUTRAL long-short whose return comes "
    "from residual reversion, not net market exposure",
    "vs C18 (H4 trend-following): C18 was a long-biased intraday directional timing "
    "approximation; this is a D1 market-neutral relative-value mechanism -- a "
    "different exposure, a different success axis, and not a timing signal",
    "vs C11 (relative-strength rotation): C11 was a long-biased directional rotation; "
    "this is dollar+beta neutral with explicitly zero net long exposure",
)

# --- 3. gate-zero: OOS neutrality validation BEFORE any trading logic --------
OOS_NEUTRALITY_GATE_ZERO = {
    "is_gate_zero": True,
    "requirement": ("estimate return-beta hedge ratios in-sample, then PROVE the "
                    "long-short residual is beta-neutral on UNSEEN out-of-sample "
                    "data (net residual beta within tolerance) BEFORE any trading "
                    "logic is defined or evaluated"),
    "net_residual_beta_tolerance": 0.10,
    "fixes_c16_failure": True,
    "no_trading_logic_until_neutrality_validated_oos": True,
}

# --- 4. the six candidate SUB-APPROACHES to compare -------------------------
SUB_APPROACHES = (
    {"key": "oos_validated_return_beta_hedge_estimation",
     "desc": "GATE ZERO: estimate return-beta hedge ratios IS and validate "
             "net-residual-beta ~ 0 OOS before any trading logic"},
    {"key": "pairwise_beta_neutral_residual_reversion",
     "desc": "trade mean-reversion of the beta-neutral residual of each pair "
             "(BTC-ETH, BTC-SOL, ETH-SOL)"},
    {"key": "cross_sectional_rank_residual_reversion",
     "desc": "rank the three by neutral residual return; long the laggard / short "
             "the leader, dollar-neutral"},
    {"key": "asset_vs_basket_beta_neutral_residual_reversion",
     "desc": "each asset's beta-neutral residual vs the equal-weight basket, "
             "mean-reverting"},
    {"key": "rolling_neutrality_recalibration",
     "desc": "rolling re-estimation of hedge ratios with OOS-validated stability of "
             "the neutrality through time"},
    {"key": "neutral_residual_zscore_entry_exit",
     "desc": "entry on neutral-residual z-score extremes, exit on reversion to the "
             "mean -- turnover kept low"},
)

# --- 5. evaluation metrics --------------------------------------------------
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_residual_beta", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "diagnostics": ("net_return", "profit_factor", "win_rate", "avg_R_per_trade",
                    "turnover_low", "long_short_dollar_neutrality"),
    "baseline": ("random-entry null and a zero-edge null on the SAME neutral "
                 "residual, net of cost -- NOT buy-and-hold (there is no net "
                 "market exposure)"),
    "win_condition": ("a NET-POSITIVE market-neutral residual edge vs random / null "
                      "on a RISK-ADJUSTED basis AND surviving forward-OOS -- with "
                      "OOS-validated neutrality as a precondition"),
    "neutrality_is_precondition": True,
}

# --- 6. cost assumptions ----------------------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "two_legs_so_cost_counts_double_per_rebalance": True,
    "low_turnover_required_to_keep_cost_drag_small": True,
    "cost_applied_only_at_replay_gate": True,
}

# --- 7. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_market_neutral_edge": True,
    "neutrality_validated_oos_first": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- 8. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no "
    "orders, no credentials, no data fetch in this proposal",
    "cached BTC/ETH/SOL D1 spot ONLY -- no new data fetch, no XAUUSD / new "
    "instrument class",
    "OOS neutrality validation is GATE ZERO: no trading logic is defined or judged "
    "until the residual is proven beta-neutral out-of-sample",
    "no detector / labels / replay / optimization / rescue / parameter tuning in or "
    "after this proposal until each downstream gate is separately human-approved",
    "promotion requires a net-positive market-neutral edge vs random/null, "
    "risk-adjusted, surviving forward-OOS -- the same evidence bar that rejected "
    "C1-C18; this proposal does NOT start C20",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_robustness",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "carries_net_market_beta",
    "trades_before_neutrality_validated", "adds_new_instrument_class",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "starts_c20", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_19_proposal_label() -> str:
    return (
        "Candidate #19 oos_validated_beta_neutral_cross_sectional_relative_value_v1 "
        "family proposal (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). A continuous "
        "dollar+return-beta-neutral cross-sectional relative-value residual among "
        "BTC/ETH/SOL (D1, cached), with OOS neutrality validation as GATE ZERO before "
        "any trading logic -- materially different from C1-C18 (esp. C16/C17/C18) and "
        "carrying no buy-and-hold beta. Compares six sub-approaches. PROPOSAL ONLY: "
        "advancing to the candidate-spec gate needs an explicit human decision. NO "
        "detector, NO labels, NO replay, NO optimization, NO data fetch, NO XAUUSD, "
        "NO paper/live, does NOT start C20. NOT a profitability claim.")


def get_candidate_19_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c19_proposal(repo_root: Any = ".",
                       tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #19 family-proposal record. Pure; no I/O;
    proposal only. Chain-gated on the committed C19 research-direction recommendation
    (its PREFERRED direction must be exactly this family)."""
    rec = _rec.build_c19_research_direction_recommendation()
    rec_valid = _rec.validate_c19_research_direction_recommendation(rec)["valid"]
    rec_preferred = rec.get("preferred_direction_key")

    blockers: list = []
    if not rec_valid:
        blockers.append("c19_recommendation_invalid")
    if rec_preferred != CANDIDATE_FAMILY:
        blockers.append("recommendation_preferred_is_not_this_family")
    if rec.get("c19_assigned") is not False:
        blockers.append("recommendation_should_not_have_assigned_c19")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C18:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C19_SCHEMA_VERSION, "mode": C19_MODE, "lane": C19_LANE,
        "label": get_candidate_19_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C19_PROPOSAL_BLOCKED"),
        # chain provenance (promoted from the C19 recommendation)
        "promoted_from_recommendation": "c19_research_direction_recommendation_v1",
        "recommendation_valid": rec_valid,
        "recommendation_preferred_key": rec_preferred,
        "approved_via": "HUMAN_APPROVED_C19_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL",
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                  # 1
        "why_different_from_c1_c18": list(WHY_DIFFERENT_FROM_C1_C18),     # 2
        "oos_neutrality_gate_zero": dict(OOS_NEUTRALITY_GATE_ZERO),       # 3
        "sub_approaches": [dict(s) for s in SUB_APPROACHES],             # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),             # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                     # 6
        "oos_validation": dict(OOS_VALIDATION),                         # 7
        "safety_boundaries": list(SAFETY_BOUNDARIES),                   # 8
        # universe + data
        "universe": list(UNIVERSE),
        "timeframe": TIMEFRAME,
        "data_requirements": _deepish(DATA_REQUIREMENTS),
        "uses_cached_btc_eth_sol_d1_only": True,
        "no_new_data_fetch": True,
        "no_new_instrument_class": True,
        # identity / anti-loop
        "is_market_neutral": True,
        "is_return_space": True,
        "is_dollar_neutral": True,
        "is_beta_neutral": True,
        "oos_neutrality_validation_is_gate_zero": True,
        "carries_buy_and_hold_beta": False,
        "is_directional_timing_signal": False,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c18": list(REJECTED_FAMILIES_C1_TO_C18),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C18),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C18,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "does_not_start_c20": True,
        "c20_candidate_id": None,
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
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_net_market_beta": True,
        "no_trade_before_neutrality_validated": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c20": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c19_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the valid C19 recommendation (preferred ==
    this family), a MARKET-NEUTRAL return-space relative-value family NOT in the
    C1-C18 (23) ledger, with OOS neutrality validation as gate zero, the cached
    BTC/ETH/SOL D1-only universe (no fetch, no new instrument class), the six
    sub-approaches, the market-neutral + risk-adjusted + forward-OOS evaluation,
    preserves the gate sequence, keeps downstream gates locked, does not start C20,
    and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C19_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the C19 recommendation
    if record.get("recommendation_valid") is not True:
        failures.append("recommendation_not_valid")
    if record.get("recommendation_preferred_key") != CANDIDATE_FAMILY:
        failures.append("recommendation_preferred_mismatch")
    if record.get("promoted_from_recommendation") != (
            "c19_research_direction_recommendation_v1"):
        failures.append("promoted_from_wrong_source")

    # identity: candidate #19, market-neutral, return-space, gate-zero neutrality
    if record.get("candidate_id") != "C19":
        failures.append("candidate_id_not_c19")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    if record.get("is_market_neutral") is not True:
        failures.append("not_market_neutral")
    if record.get("is_return_space") is not True:
        failures.append("not_return_space")
    if record.get("is_dollar_neutral") is not True:
        failures.append("not_dollar_neutral")
    if record.get("is_beta_neutral") is not True:
        failures.append("not_beta_neutral")
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("oos_neutrality_validation_is_gate_zero") is not True:
        failures.append("oos_neutrality_not_gate_zero")
    gz = record.get("oos_neutrality_gate_zero") or {}
    if gz.get("is_gate_zero") is not True:
        failures.append("gate_zero_flag_wrong")
    if gz.get("no_trading_logic_until_neutrality_validated_oos") is not True:
        failures.append("trading_before_neutrality_allowed")

    # anti-loop + materially different
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C18:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 23:
        failures.append("ledger_not_23")
    diffs = record.get("why_different_from_c1_c18") or []
    if len(diffs) < 5:
        failures.append("insufficient_difference_explanation")
    joined = " ".join(diffs)
    for must in ("C16", "C17", "C18"):
        if must not in joined:
            failures.append("difference_missing_%s" % must)

    # universe + data: cached BTC/ETH/SOL D1 only, no fetch, no new instrument
    if list(record.get("universe") or []) != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        failures.append("universe_not_btc_eth_sol")
    if record.get("timeframe") != "D1":
        failures.append("timeframe_not_d1")
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch_data")
    if record.get("no_new_instrument_class") is not True:
        failures.append("must_not_add_instrument_class")
    dr = record.get("data_requirements") or {}
    if dr.get("no_data_fetched_here") is not True:
        failures.append("data_fetch_flag_wrong")
    if (dr.get("btc_eth_sol_d1_spot") or {}).get("available_locally") is not True:
        failures.append("d1_data_should_be_local")
    if dr.get("no_xauusd_or_new_instrument_class") is not True:
        failures.append("data_adds_new_instrument_class")

    # the six sub-approaches, incl. the gate-zero hedge estimation
    subs = record.get("sub_approaches") or []
    if len(subs) != 6:
        failures.append("sub_approaches_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("oos_validated_return_beta_hedge_estimation",
                 "pairwise_beta_neutral_residual_reversion",
                 "cross_sectional_rank_residual_reversion",
                 "asset_vs_basket_beta_neutral_residual_reversion",
                 "rolling_neutrality_recalibration",
                 "neutral_residual_zscore_entry_exit"):
        if must not in keys:
            failures.append("sub_approach_missing_%s" % must)

    # evaluation: market-neutral vs random/null + risk-adjusted; cost reserved
    em = record.get("evaluation_metrics") or {}
    if "net_residual_beta" not in (em.get("primary_market_neutral") or ()):
        failures.append("missing_net_residual_beta_metric")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random_null")
    if em.get("neutrality_is_precondition") is not True:
        failures.append("neutrality_not_precondition")
    ct = record.get("cost_assumptions") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")

    # OOS required, neutrality validated first, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_validated_oos_first") is not True:
        failures.append("neutrality_not_validated_first")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # gate sequence + downstream locks + no C20
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")
    if record.get("does_not_start_c20") is not True:
        failures.append("must_not_start_c20")
    if record.get("c20_candidate_id") is not None:
        failures.append("c20_must_be_none")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_xauusd", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_net_market_beta",
                "no_trade_before_neutrality_validated", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_rejected_family_repropose",
                "no_start_c20"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
