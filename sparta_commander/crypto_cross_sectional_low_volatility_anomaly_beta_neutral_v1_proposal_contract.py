"""Candidate #23 -- crypto_cross_sectional_low_volatility_anomaly_beta_neutral_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY, QUEUED / ON-DECK).

The formal Candidate #23 family proposal for the human-approved C23 readiness direction
(HUMAN_APPROVED_C23_FAMILY_PROPOSAL_READINESS_ONLY). C23 is proposed as a QUEUED / ON-DECK
family: Candidate #22 (external_signum_trend_radar_gc_long_short) is still the IN-FLIGHT
active candidate at HOLD_FOR_MORE_FROZEN_DATA_WINDOWS, and this proposal must NOT displace
it, NOT open C23 as the active candidate, and NOT touch the C22 collection pipeline.

THESIS: harvest the LOW-VOLATILITY ANOMALY in crypto -- the documented effect that
low-realized-volatility assets deliver higher RISK-ADJUSTED returns than high-volatility
assets -- as a DOLLAR- and BETA-NEUTRAL CROSS-SECTIONAL long-low-vol / short-high-vol
portfolio across the liquid perp universe, rebalanced at LOW turnover. The return source is
a RISK-BASED cross-sectional anomaly (leverage-constraint / lottery-preference driven), NOT
price-timing, NOT funding/basis carry, NOT relative-value mispricing.

WHY STRUCTURALLY CHOSEN: every rejected DIRECTIONAL family (breakout/FVG/swing/trend/
momentum, and the external trend-radar C22) fires a small number of directional bets whose
net depends on a few fat-tail winners -- they fail the top-winner-removal / entry-significance
gates and lose to buy-and-hold beta. The two CARRY families (C20/C21) had the right NEUTRAL,
high-breadth shape but harvested a FREE, OOS-fragile funding null. C23 keeps the robust
NEUTRAL high-breadth structure (many small independent cross-sectional positions, not
fat-tail dependent) but switches the edge source to a DIFFERENT, non-carry, documented risk
anomaly -- and is held to the same fee-honest gates (beat a random NEUTRAL null + survive
top-decile-winner removal + forward-OOS, net of cost, residual market beta ~ 0).

It is a PROPOSAL only: it DECLARES the family thesis, why it is materially different from
the C1-C21 (26) rejected families AND from C22, the identity, six evaluation variants/
ablations, the evaluation metrics (neutral null + risk-adjusted + turnover-aware +
forward-OOS + beta-neutrality + top-decile-removal robustness), the cost assumptions
(reserved for replay), the data boundary (own/frozen OHLCV only; no fetch), the OOS
requirement, the safety boundaries, and the next human gate. It builds NO spec/detector/
labels/replay; runs NO PnL/optimization/tuning/data fetch; connects NOTHING; touches NO
paper/live/broker/order/scheduler surface; does NOT displace C22; and advances NOTHING. Every
capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

C23_SCHEMA_VERSION = 1
C23_MODE = "RESEARCH_ONLY"
C23_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C23"
CANDIDATE_TOKEN = "C23_CRYPTO_CROSS_SECTIONAL_LOW_VOLATILITY_ANOMALY_BETA_NEUTRAL_V1"
CANDIDATE_FAMILY = "crypto_cross_sectional_low_volatility_anomaly_beta_neutral"
CANDIDATE_NAME = "crypto_cross_sectional_low_volatility_anomaly_beta_neutral_v1"

REJECTED_FAMILIES_C1_TO_C21 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C21)   # 26
# the in-flight active candidate this proposal must NOT displace.
C22_FAMILY = "external_signum_trend_radar_gc_long_short"
C22_STATE = "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"

C23_READINESS_TOKEN = "HUMAN_APPROVED_C23_FAMILY_PROPOSAL_READINESS_ONLY"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- 1. family thesis -------------------------------------------------------
FAMILY_THESIS = (
    "Harvest the LOW-VOLATILITY ANOMALY in crypto: low-realized-volatility assets tend to "
    "deliver higher RISK-ADJUSTED returns than high-volatility assets (a leverage-constraint "
    "/ lottery-preference risk anomaly). Build a DOLLAR- and BETA-NEUTRAL CROSS-SECTIONAL "
    "portfolio -- long the low-realized-vol cohort, short the high-realized-vol cohort -- "
    "across the liquid crypto perp universe, rebalanced at LOW turnover. The edge source is a "
    "cross-sectional RISK ANOMALY, NOT price-timing, NOT funding/basis carry, NOT "
    "relative-value mispricing. The prior is skeptical: the anomaly must be PROVEN net of "
    "cost, survive top-decile-winner removal, hold residual market beta ~ 0, and persist in "
    "forward-OOS -- not assumed from the academic literature.")

# --- 2. why materially different from C1-C21 AND C22 ------------------------
WHY_DIFFERENT_FROM_REJECTED_AND_C22 = (
    "vs ALL DIRECTIONAL families (C1-C5 breakout/FVG/swing/structure, C13 lead-lag, C14 "
    "conviction-bar, C15 TS-momentum, C18 H4 trend, and C22 external trend-radar long/short): "
    "C23 is DOLLAR- and BETA-NEUTRAL with NO net market exposure and NO directional "
    "price-timing trigger, so buy-and-hold is NOT its target benchmark and it structurally "
    "avoids the top-winner/fat-tail-dependence + bull-beta failure that sank every directional "
    "attempt; its return source is a cross-sectional RISK ANOMALY, not trend/breakout/structure "
    "timing",
    "vs the CARRY families (C20 mechanically-neutral and C21 low-turnover spot/perp funding "
    "carry): C23 harvests NO funding or basis carry and is NOT the always-on carry null; its "
    "edge is the cross-sectional VOLATILITY anomaly in price returns -- a DIFFERENT, non-free, "
    "non-carry premium that the carry rejections do not cover",
    "vs the MEAN-REVERSION families (C8 liquidity-sweep, C9 low-volume capitulation, C11 "
    "cross-asset dispersion reversion, C12 failed-breakdown reclaim): those are TIME-SERIES "
    "price mean-reversion triggers; C23 is a CROSS-SECTIONAL risk-factor SORT with no reversion "
    "trigger and no single-name timing",
    "vs C19 (beta-neutral cross-sectional relative VALUE) and C17 (vol-TARGETING allocation): "
    "C23's factor is the LOW-VOLATILITY ANOMALY (sorting on realized-vol LEVEL), NOT a "
    "value/mispricing relative-value signal (C19) and NOT portfolio vol-targeting position "
    "SIZING (C17) -- a distinct factor and a distinct construction",
    "vs volatility_compression_expansion (C10-series vol-STATE breakout): that is a "
    "TIME-SERIES DIRECTIONAL vol-state breakout; C23 is a CROSS-SECTIONAL NEUTRAL vol-LEVEL "
    "anomaly -- opposite on every axis (level vs state, cross-section vs time-series, neutral "
    "vs directional)",
    "STRUCTURALLY CHOSEN to break the dominant failure: high breadth across the universe, many "
    "small independent positions, dollar+beta-neutral and low turnover -- the net does NOT "
    "depend on a few fat-tail winners (an explicit top-decile-removal robustness gate is "
    "required), unlike every rejected directional trigger",
)

# --- 3. identity (cross-sectional, neutral, risk-anomaly) -------------------
STRATEGY_IDENTITY = {
    "is_cross_sectional": True,
    "is_dollar_neutral": True,
    "is_beta_neutral": True,
    "is_directional": False,
    "is_long_biased": False,
    "carries_net_market_beta": False,
    "return_source_is_risk_anomaly_not_timing": True,
    "is_carry_family": False,
    "is_relative_value_mispricing_family": False,
    "is_internal_derivation": True,
    "is_reparameterization_of_a_rejected_family": False,
    "distinct_edge_axis": "cross_sectional_low_realized_volatility_risk_anomaly_beta_neutral",
    "skeptical_prior_anomaly_must_be_proven_net_of_cost_and_oos": True,
    "is_queued_on_deck_not_active": True,
}

# --- 4. six evaluation VARIANTS / ABLATIONS to compare ----------------------
EVALUATION_VARIANTS = (
    {"key": "baseline_low_vol_long_short_beta_neutral",
     "desc": "long the low-realized-vol cohort / short the high-realized-vol cohort, "
             "dollar- and beta-neutral, low-turnover rebalance (the primary object under "
             "test)"},
    {"key": "fee_honest_cost_overlay",
     "desc": "the same construction with SPARTA's fee-honest crypto perp cost + slippage "
             "applied to the rebalance turnover (the decisive net-of-cost view)"},
    {"key": "beta_neutralization_ablation",
     "desc": "raw dollar-neutral vs explicitly beta-hedged, to confirm residual market beta "
             "~ 0 and that the result is not a hidden short-beta bet"},
    {"key": "rebalance_frequency_turnover_ablation",
     "desc": "monthly vs weekly rebalance, to expose the turnover/cost tradeoff and confirm "
             "the edge is not eaten by rebalancing churn (the C20 lesson)"},
    {"key": "top_decile_winner_removal_robustness",
     "desc": "remove the top-decile contributing names/periods and re-measure -- the "
             "Donchian-style gate the directional families failed; the neutral edge must "
             "survive"},
    {"key": "forward_oos_holdout",
     "desc": "the fixed construction evaluated only on an unseen forward-OOS window, never "
             "fit in-sample -- the durability test"},
)

# --- 5. evaluation metrics (NEUTRAL: random neutral null, not buy-and-hold) --
EVALUATION_METRICS = {
    "primary_neutral": ("net_return_after_cost", "beats_random_neutral_null_risk_adjusted",
                        "residual_market_beta_near_zero"),
    "neutrality_diagnostics": ("residual_market_beta", "long_short_dollar_balance",
                               "net_exposure_near_zero"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "turnover_efficiency": ("rebalances_per_year", "all_in_cost_drag",
                            "cost_drag_as_share_of_gross"),
    "robustness": ("top_decile_winner_removal_survives", "year_distribution_positive_share"),
    "baseline": ("a RANDOM / zero-edge BETA-NEUTRAL null (random cross-sectional long/short) "
                 "net of all-in cost -- NOT buy-and-hold (the strategy is market-neutral, so "
                 "buy-and-hold is a context reference, not the target)"),
    "win_condition": ("a NET-POSITIVE edge after cost that beats the RANDOM NEUTRAL null on a "
                      "RISK-ADJUSTED basis AND survives top-decile-winner removal AND holds "
                      "residual market beta ~ 0 AND persists in forward-OOS -- beating the "
                      "random null alone is necessary but NOT sufficient"),
    "buy_and_hold_is_context_reference_only_not_target": True,
    "is_market_neutral_evaluation": True,
    "low_turnover_is_evaluation_dimension": True,
}

# --- 6. cost assumptions (reserved for replay) ------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "applies_to_rebalance_turnover_both_legs": True,
    "cost_applied_only_at_replay_gate": True,
    "applied_here": False,
    "turnover_is_a_first_class_cost_risk": (
        "cross-sectional rebalancing can churn; the rebalance-frequency ablation + the cost "
        "overlay exist specifically to expose cost drag before any promotion -- the C20 "
        "turnover-destroyed-the-carry lesson"),
}

# --- 7. data boundary (own/frozen OHLCV only; no fetch) ---------------------
DATA_REQUIREMENTS = {
    "uses_own_or_frozen_data_only": True,
    "primary_data": "per-asset daily OHLCV for the liquid crypto perp universe",
    "needs_funding_or_basis_data": False,
    "needs_options_or_implied_vol_data": False,
    "needs_open_interest_data": False,
    "no_new_instrument_class": True,
    "no_signum_connection": True,
    "no_exchange_or_hyperliquid_fetch": True,
    "no_mcp": True,
    "no_api_keys_or_credentials": True,
    "exact_universe_and_timeframe_confirmed_at_spec_gate": True,
    "no_new_data_fetched_in_this_proposal": True,
    "data_readiness_risk": "low (OHLCV only; no options/OI/funding dependency)",
}

# --- 8. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "unseen_continuation_holdout",
    "forward_oos_must_beat_random_neutral_null_risk_adjusted": True,
    "forward_oos_residual_beta_near_zero_required": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
    "construction_held_fixed": True,
}

# --- 9. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no orders, no "
    "credentials, no data fetch, no scheduler in this proposal",
    "QUEUED / ON-DECK: Candidate #22 remains the in-flight active candidate at "
    "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS; this proposal does NOT displace C22, does NOT open "
    "C23 as active, and does NOT touch the C22 collection pipeline -- opening C23 needs a "
    "separate human decision after C22 concludes",
    "MARKET-NEUTRAL: dollar- and beta-neutral; the benchmark is a RANDOM NEUTRAL null (not "
    "buy-and-hold as target); an edge must beat that null risk-adjusted AND survive "
    "top-decile-winner removal AND hold residual beta ~ 0 AND persist forward-OOS, net of cost",
    "INTERNAL construction, NOT a re-parameterization of any rejected family; the LOW-VOL "
    "anomaly factor is distinct from C19 relative-value, C17 vol-targeting, and the C10 "
    "vol-state breakout",
    "no spec / detector / labels / replay / optimization / tuning in or after this proposal "
    "until each downstream gate is separately human-approved; this proposal advances NOTHING "
    "and connects NOTHING",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "builds_spec",
    "runs_detector", "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "reproposes_rejected_family", "runs_robustness", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "displaces_active_c22", "touches_c22_pipeline",
    "opens_c23_as_active", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "edits_bots", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_23_proposal_label() -> str:
    return (
        "Candidate #23 crypto_cross_sectional_low_volatility_anomaly_beta_neutral_v1 family "
        "proposal (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL, QUEUED/ON-DECK). Harvest the "
        "cross-sectional LOW-VOLATILITY ANOMALY as a dollar- and beta-neutral long-low-vol / "
        "short-high-vol portfolio across the liquid crypto perp universe -- a risk anomaly, "
        "NOT price-timing, NOT carry, NOT relative-value. Materially different from the "
        "C1-C21 (26) rejected families AND from the in-flight C22 (external trend-radar). "
        "QUEUED: C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS and is not displaced; opening "
        "C23 needs a separate human decision after C22 concludes. Judged vs a RANDOM NEUTRAL "
        "null + top-decile-winner removal + residual beta ~ 0 + forward-OOS, net of cost. "
        "PROPOSAL ONLY: NO spec/detector/labels/replay, NO optimization, NO data fetch, NO "
        "connection, NO paper/live. NOT a profitability claim.")


def get_candidate_23_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c23_proposal() -> dict[str, Any]:
    """Assemble the frozen Candidate #23 family-proposal record. Pure; no I/O; proposal
    only; QUEUED / ON-DECK (does not displace the in-flight C22). Gated on C23 being
    materially distinct from the C1-C21 (26) rejected ledger AND from the C22 family."""
    blockers: list = []
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C21:
        blockers.append("candidate_family_in_rejected_ledger")
    if CANDIDATE_FAMILY == C22_FAMILY:
        blockers.append("candidate_family_equals_c22")
    if len(REJECTED_FAMILIES_C1_TO_C21) != 26:
        blockers.append("rejected_ledger_not_26")

    record: dict[str, Any] = {
        "schema_version": C23_SCHEMA_VERSION, "mode": C23_MODE, "lane": C23_LANE,
        "label": get_candidate_23_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "is_queued_on_deck_proposal": True,
        "approved_via": C23_READINESS_TOKEN,
        "blockers": blockers,
        "verdict": ("C23_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C23_PROPOSAL_BLOCKED"),
        # queued / on-deck: does NOT displace the in-flight C22
        "active_candidate_in_flight": "C22",
        "active_candidate_family": C22_FAMILY,
        "c22_state_unchanged": C22_STATE,
        "does_not_displace_active_c22": True,
        "does_not_open_c23_as_active": True,
        "does_not_touch_c22_collection_pipeline": True,
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                       # 1
        "why_different_from_rejected_and_c22":
            list(WHY_DIFFERENT_FROM_REJECTED_AND_C22),                        # 2
        "strategy_identity": dict(STRATEGY_IDENTITY),                         # 3
        "evaluation_variants": [dict(s) for s in EVALUATION_VARIANTS],        # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),                  # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                          # 6
        "data_requirements": dict(DATA_REQUIREMENTS),                        # 7
        "oos_validation": dict(OOS_VALIDATION),                             # 8
        "safety_boundaries": list(SAFETY_BOUNDARIES),                        # 9
        # identity / anti-loop
        "is_directional": False,
        "is_market_neutral": True,
        "is_cross_sectional": True,
        "is_reparameterization_of_a_rejected_family": False,
        "distinct_edge_axis":
            "cross_sectional_low_realized_volatility_risk_anomaly_beta_neutral",
        "buy_and_hold_is_context_reference_only": True,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c21": list(REJECTED_FAMILIES_C1_TO_C21),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C21),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C21,
        "candidate_distinct_from_c22": CANDIDATE_FAMILY != C22_FAMILY,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal_queued",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "advances_nothing": True,
        # downstream gates locked
        "spec_gate_locked": True, "detector_gate_locked": True,
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_spec": True, "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_displace_active_c22": True, "no_open_c23_as_active": True,
        "no_touch_c22_pipeline": True, "no_scheduler_change": True,
        "no_scheduler_install": True, "no_signum_connection": True, "no_mcp": True,
        "no_hyperliquid": True, "no_api_keys": True, "no_credentials": True,
        "no_bot_edits": True, "no_claude_routines": True, "no_send_trades": True,
        "no_broker": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c23_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-proposal-
    only, QUEUED/ON-DECK (does not displace the in-flight C22, does not open C23 as active,
    does not touch the C22 pipeline), a MARKET-NEUTRAL cross-sectional low-volatility-anomaly
    family NOT in the C1-C21 (26) ledger and distinct from the C22 family, with a distinct
    risk-anomaly edge axis, judged vs a RANDOM NEUTRAL null (not buy-and-hold) + top-decile
    removal + residual beta ~ 0 + forward-OOS (cost reserved for replay), preserves the gate
    sequence, keeps downstream gates locked, advances nothing, and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != C23_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("is_queued_on_deck_proposal") is not True:
        failures.append("not_queued_on_deck")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C23_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # queued / on-deck: does not displace C22
    if record.get("active_candidate_in_flight") != "C22":
        failures.append("must_acknowledge_c22_in_flight")
    if record.get("c22_state_unchanged") != C22_STATE:
        failures.append("c22_state_must_be_hold")
    for k in ("does_not_displace_active_c22", "does_not_open_c23_as_active",
              "does_not_touch_c22_collection_pipeline"):
        if record.get(k) is not True:
            failures.append("queued_guarantee_off_%s" % k)

    # identity: candidate #23, market-neutral, cross-sectional, not directional/carry
    if record.get("candidate_id") != "C23":
        failures.append("candidate_id_not_c23")
    if record.get("candidate_token") != CANDIDATE_TOKEN:
        failures.append("candidate_token_mismatch")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    ident = record.get("strategy_identity") or {}
    for k in ("is_cross_sectional", "is_dollar_neutral", "is_beta_neutral",
              "return_source_is_risk_anomaly_not_timing",
              "skeptical_prior_anomaly_must_be_proven_net_of_cost_and_oos",
              "is_queued_on_deck_not_active"):
        if ident.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    for k in ("is_directional", "is_long_biased", "carries_net_market_beta",
              "is_carry_family", "is_relative_value_mispricing_family",
              "is_reparameterization_of_a_rejected_family"):
        if ident.get(k) is not False:
            failures.append("identity_flag_must_be_false_%s" % k)
    if ident.get("distinct_edge_axis") != (
            "cross_sectional_low_realized_volatility_risk_anomaly_beta_neutral"):
        failures.append("distinct_edge_axis_wrong")

    # materially different: not in ledger, distinct from C22, references the right families
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C21:
        failures.append("family_listed_as_rejected")
    if record.get("candidate_distinct_from_c22") is not True:
        failures.append("not_distinct_from_c22")
    if record.get("candidate_family") == C22_FAMILY:
        failures.append("family_equals_c22")
    if record.get("rejected_families_count") != 26:
        failures.append("ledger_not_26")
    diffs = record.get("why_different_from_rejected_and_c22") or []
    if len(diffs) < 5:
        failures.append("insufficient_difference_explanation")
    joined = " ".join(diffs)
    for must in ("C20", "C21", "C19", "C17", "C22", "NEUTRAL"):
        if must not in joined:
            failures.append("difference_missing_%s" % must)

    # the six evaluation variants
    subs = record.get("evaluation_variants") or []
    if len(subs) != 6:
        failures.append("evaluation_variants_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("baseline_low_vol_long_short_beta_neutral", "fee_honest_cost_overlay",
                 "beta_neutralization_ablation", "rebalance_frequency_turnover_ablation",
                 "top_decile_winner_removal_robustness", "forward_oos_holdout"):
        if must not in keys:
            failures.append("variant_missing_%s" % must)

    # evaluation: NEUTRAL -> random neutral null (NOT buy-and-hold target), robustness, OOS
    em = record.get("evaluation_metrics") or {}
    if "beats_random_neutral_null_risk_adjusted" not in (em.get("primary_neutral") or ()):
        failures.append("missing_neutral_null_benchmark")
    if "residual_market_beta_near_zero" not in (em.get("primary_neutral") or ()):
        failures.append("missing_beta_neutrality_metric")
    if em.get("is_market_neutral_evaluation") is not True:
        failures.append("not_market_neutral_evaluation")
    if em.get("buy_and_hold_is_context_reference_only_not_target") is not True:
        failures.append("buy_and_hold_must_be_context_only")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "top_decile_winner_removal_survives" not in (em.get("robustness") or ()):
        failures.append("missing_top_decile_removal_gate")
    wc = str(em.get("win_condition", "")).lower()
    if "random neutral null" not in wc:
        failures.append("win_condition_not_vs_random_neutral_null")
    if "top-decile" not in wc:
        failures.append("win_condition_missing_top_decile")
    if "forward-oos" not in wc:
        failures.append("win_condition_missing_oos")

    # cost reserved for replay; OOS required + construction held fixed
    ct = record.get("cost_assumptions") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")
    if ct.get("applied_here") is not False:
        failures.append("cost_must_not_be_applied_here")
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("forward_oos_must_beat_random_neutral_null_risk_adjusted") is not True:
        failures.append("oos_must_beat_neutral_null")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")
    if oos.get("construction_held_fixed") is not True:
        failures.append("construction_not_held_fixed")

    # data boundary: own/frozen OHLCV only, no fetch, no new instrument class
    drq = record.get("data_requirements") or {}
    for k in ("uses_own_or_frozen_data_only", "no_signum_connection",
              "no_exchange_or_hyperliquid_fetch", "no_mcp",
              "no_api_keys_or_credentials", "no_new_data_fetched_in_this_proposal",
              "no_new_instrument_class"):
        if drq.get(k) is not True:
            failures.append("data_boundary_off_%s" % k)

    # gate sequence + downstream locks + advances nothing
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_open_c23_after_c22")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_spec", "no_detector", "no_labels", "no_replay",
                "no_pnl", "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_commit", "no_push",
                "no_displace_active_c22", "no_open_c23_as_active", "no_touch_c22_pipeline",
                "no_scheduler_change", "no_scheduler_install", "no_signum_connection",
                "no_mcp", "no_hyperliquid", "no_api_keys", "no_credentials",
                "no_bot_edits", "no_claude_routines", "no_send_trades", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
