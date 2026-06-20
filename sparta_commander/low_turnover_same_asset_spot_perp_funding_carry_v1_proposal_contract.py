"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- FAMILY PROPOSAL (PURE, RESEARCH ONLY).

The formal candidate-family proposal for the human-approved C21 research direction
(HUMAN_APPROVED_C21_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL), built on the
frozen PUBLIC BTCUSDT/ETHUSDT/SOLUSDT spot + USDT-perp + funding dataset. Chain-gated on
the committed data-readiness review (the dataset must be FROZEN_AND_READY).

THESIS (built ON the preserved C20 lesson, NOT a rescue/retune of C20): C20's fee-honest
replay proved that the same-asset mechanically-neutral CARRY return source is REAL -- the
always-on neutral-carry benchmark earned +21.2% net (Sharpe 1.09; BTC/ETH funding
strongest) -- but C20's high-turnover entry/exit TIMING (704 round-trips x 74 bps two-leg
cost = 521% cost drag) destroyed it. C21 therefore tests a DIFFERENT operating principle:
harvest the SAME carry source with LOW TURNOVER / HOLD PERSISTENCE -- enter only in a
stably positive carry regime and HOLD through basis noise, exiting only on a DURABLE
carry-regime breakdown, so round-trips (and thus the 74 bps cost) stay low enough not to
dominate. To be PROVEN net of all-in + perp-specific costs, not assumed.

It is a PROPOSAL only: it DECLARES the family thesis, why it differs from C20 and the
rejected C1-C20 families, the universe and the mechanical-neutrality gate-zero, the
low-turnover design principle, six LOW-TURNOVER candidate SUB-FAMILIES to compare, the
evaluation metrics (incl. an explicit turnover / cost-efficiency metric), the cost
assumptions (incl. perp-specific frictions reserved for replay), the data requirements
(the frozen dataset; nothing fetched), the out-of-sample requirement, the safety
boundaries, and the next human gate. It builds NO detector, NO labels, NO replay; runs NO
PnL/optimization/tuning/rescue/data fetch; touches NO paper/live/broker/order surface; and
does NOT start C22. Every capability flag is pinned False with a full scope_locks set.
Advancing to the candidate-spec gate needs an explicit human decision. C20's timing/
entry-exit strategy remains REJECTED -- this is a NEW family, not a rescue of C20.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_basis_funding_data_readiness_review_v1_contract as _dr
import sparta_commander.research_expansion_plan_v1_contract as _rep

C21_SCHEMA_VERSION = 1
C21_MODE = "RESEARCH_ONLY"
C21_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C21"
CANDIDATE_FAMILY = "low_turnover_same_asset_spot_perp_funding_carry"
CANDIDATE_NAME = "low_turnover_same_asset_spot_perp_funding_carry_v1"

REJECTED_FAMILIES_C1_TO_C20 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C20)   # 25
EXPECTED_DATA_VERDICT = "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + data (frozen public spot/perp/funding; nothing fetched) -----
UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAME = "D1"
DATA_SOURCE = ("frozen PUBLIC Binance spot + USDT-perp + funding (the committed "
               "data-readiness review dataset) -- already present, no fetch")

# --- the preserved C20 lesson (verbatim evidence this family is built on) ----
C20_LESSON_PRESERVED = {
    "c20_family": "mechanically_neutral_spot_perp_basis_funding_carry",
    "c20_status": "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD",
    "always_on_neutral_carry_net_return": 0.211648,    # +21.2%
    "always_on_neutral_carry_sharpe": 1.087808,        # Sharpe ~1.09
    "btc_eth_carry_strongest": True,                   # BTC/ETH null Sharpe ~8
    "c20_timed_strategy_net_return": -0.7452,          # -74.5%
    "c20_round_trips": 704,
    "c20_cost_drag": 5.2096,                           # 521% (74 bps x 704 trades)
    "c20_failed_due_to_churn_cost_not_signal": True,
    "carry_source_is_real": True,
    "c21_is_rescue_or_retune_of_c20": False,
}

# --- 1. family thesis -------------------------------------------------------
FAMILY_THESIS = (
    "Harvest the SAME mechanically-neutral same-asset CARRY source that C20's "
    "always-on benchmark proved is REAL (+21.2% net, Sharpe 1.09), but with LOW "
    "TURNOVER / HOLD PERSISTENCE instead of C20's high-turnover timing. Hold a "
    "mechanically-neutral position (long spot / short USDT-perp of the SAME asset in "
    "equal notional, so price exposure cancels by construction) and ENTER only when the "
    "funding/basis carry regime is stably positive, then HOLD through basis noise, "
    "exiting only on a DURABLE carry-regime breakdown -- NOT on basis z-score "
    "oscillation. The thesis is that a persistence-based, cost-aware harvest can capture "
    "most of the real carry while keeping round-trips (and thus the 74 bps two-leg cost "
    "that destroyed C20) low enough not to dominate. To be PROVEN net of all-in and "
    "perp-specific costs, not assumed.")

# --- 2. why different from C20 + the rest of C1-C20 --------------------------
WHY_DIFFERENT_FROM_C1_C20 = (
    "MATERIALLY DIFFERENT FROM C20 (the operating principle is opposite, not a retune): "
    "C20 was HIGH-TURNOVER TIMING -- 704 round-trips driven by basis z-score entry/exit "
    "churn -- which lost -74.5% to a 521% cost drag. C21 is LOW-TURNOVER / HOLD "
    "PERSISTENCE: sparse, regime-gated entries and exits only on durable carry breakdown, "
    "so the round-trip count (and the 74 bps two-leg cost) is minimised BY DESIGN. Same "
    "carry source, opposite turnover model",
    "NOT a rescue or retune of C20: C20's specific timing/entry-exit strategy stays "
    "REJECTED; C21 does not reuse C20's z-score entry/exit rules with different "
    "thresholds -- it replaces the timing principle with TURNOVER/COST-AWARE PERSISTENCE "
    "as a first-class design constraint",
    "NOT long-only buy-and-hold beta (the rock C17/C18 died on) and NOT cross-asset "
    "ESTIMATED neutrality (C16/C19 failed OOS): neutrality here is SAME-ASSET and "
    "MECHANICAL (long spot / short perp of the identical underlying), so it cannot drift "
    "out of sample",
    "RETURN SOURCE IS CARRY, not directional OHLCV timing: the edge is the basis/funding "
    "the short-perp leg earns over long holds, judged vs random/null on a RISK-ADJUSTED "
    "and TURNOVER-EFFICIENT basis -- raw carry before the doubled two-leg cost is never "
    "the edge",
)

# --- 3. gate-zero: mechanical neutrality + low-turnover design principle -----
MECHANICAL_NEUTRALITY_GATE_ZERO = {
    "is_gate_zero": True,
    "requirement": ("the position is long 1 unit spot and short 1 unit USDT-perp of "
                    "the SAME asset in equal notional, so net price beta is ~0 BY "
                    "CONSTRUCTION (not by estimation); the only residual exposure is "
                    "the spot-perp basis itself"),
    "neutrality_is_mechanical_not_estimated": True,
    "fixes_c16_c19_estimated_neutrality_failure": True,
    "no_cross_asset_hedge_estimation": True,
}
LOW_TURNOVER_DESIGN_PRINCIPLE = {
    "is_first_class_design_constraint": True,
    "principle": ("turnover is the decisive cost variable (C20's 704 round-trips x 74 "
                  "bps = 521% drag killed a real carry); C21 minimises round-trips by "
                  "design -- sparse regime-gated entries, long hold persistence, and "
                  "exits only on a durable carry-regime breakdown (hysteresis, not "
                  "basis-z oscillation)"),
    "prioritizes_hold_persistence": True,
    "entry_exit_sparse_and_cost_aware_from_the_start": True,
    "is_rescue_or_retune_of_c20": False,
}

# --- 4. the six LOW-TURNOVER candidate SUB-FAMILIES to compare --------------
SUB_FAMILIES = (
    {"key": "persistent_positive_carry_hold",
     "desc": "enter when the funding/basis carry has been stably positive over a slow "
             "window; HOLD the neutral position and exit only on a durable sign flip "
             "(maximises hold length, minimises round-trips)"},
    {"key": "carry_regime_gated_hold",
     "desc": "gate entry/holding by a slow carry-regime filter; stand aside entirely in "
             "negative / unstable-carry regimes and hold continuously in stable positive "
             "ones (regime changes, not basis noise, drive turnover)"},
    {"key": "funding_threshold_hysteresis_hold",
     "desc": "enter above a HIGH funding-carry threshold and exit only below a much "
             "LOWER threshold (wide hysteresis band) -- explicitly suppresses churn "
             "around a single threshold"},
    {"key": "slow_periodic_rebalanced_carry",
     "desc": "rebalance the neutral carry at most on a slow periodic cadence (e.g. "
             "monthly), never daily -- caps round-trips structurally"},
    {"key": "top_carry_asset_concentration_hold",
     "desc": "concentrate the held carry on the strongest-and-most-stable-carry "
             "asset(s) (the C20 lesson: BTC/ETH carry was strongest) -- fewer "
             "simultaneous positions, fewer rebalances"},
    {"key": "always_on_carry_with_breakdown_circuit_breaker",
     "desc": "closest to the proven always-on neutral-carry benchmark: hold continuously "
             "and only stand down on a durable carry-collapse circuit breaker (lowest "
             "turnover variant)"},
)

# --- 5. evaluation metrics (market-neutral; vs random/null; turnover-aware) --
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_price_beta_mechanical", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "carry_diagnostics": ("annualized_carry", "funding_collected", "avg_hold_length",
                          "negative_carry_regime_share"),
    "turnover_efficiency": ("round_trips_per_year", "two_leg_cost_drag",
                            "cost_drag_as_share_of_gross_carry", "avg_hold_length_days"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "baseline": ("a random/zero-edge null AND the always-on neutral-carry benchmark on "
                 "the SAME neutral position, net of ALL-IN and perp-specific cost -- NOT "
                 "buy-and-hold (there is no net market exposure)"),
    "win_condition": ("a NET-POSITIVE carry edge vs random / null on a RISK-ADJUSTED AND "
                      "TURNOVER-EFFICIENT basis (low round-trips, cost drag a small share "
                      "of gross carry) AND surviving forward-OOS, net of funding/borrow/"
                      "liquidation-aware costs -- not raw carry before costs, and not "
                      "out-churned by cost like C20"),
    "neutrality_is_mechanical_precondition": True,
    "low_turnover_is_evaluation_dimension": True,
    "judged_against_buy_and_hold": False,
}

# --- 6. cost assumptions ----------------------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS   # 37.0
COST_ASSUMPTIONS = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "two_legs_spot_and_perp_so_cost_counts_double": True,
    "round_trip_cost_per_trade_bps": 2 * ALL_IN_ROUND_TRIP_BPS,   # 74 bps (two legs)
    "low_turnover_is_the_cost_control_lever": (
        "C20 paid 74 bps x 704 round-trips = 521% drag; C21 minimises round-trips by "
        "design so the same per-trade cost is amortised over long holds"),
    "perp_specific_frictions_reserved_for_replay": (
        "funding paid/received, perp borrow, and liquidation-aware margin must be "
        "modelled at the replay gate -- carry before these costs is NOT the edge"),
    "cost_applied_only_at_replay_gate": True,
    "applied_here": False,
}

# --- 7. data requirements (frozen; nothing fetched) -------------------------
DATA_REQUIREMENTS = {
    "spot_perp_funding_d1": {"required": True, "available_locally": True,
                             "note": "the committed data-readiness review dataset "
                                     "(BTC/ETH/SOL spot+perp+funding) -- frozen, "
                                     "SHA-pinned, gitignored"},
    "no_data_fetched_here": True,
    "no_new_data_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- 8. out-of-sample validation requirement --------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_carry_edge_net_of_cost": True,
    "forward_oos_must_hold_low_turnover": True,
    "neutrality_is_mechanical_so_cannot_fail_oos": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- 9. safety boundaries ---------------------------------------------------
SAFETY_BOUNDARIES = (
    "research-only: no paper trading, no live trading, no broker/exchange, no orders, "
    "no credentials, no data fetch in this proposal",
    "frozen public spot/perp/funding ONLY -- no new fetch, no XAUUSD / new instrument "
    "class",
    "mechanical same-asset neutrality is GATE ZERO: long spot / short perp of the "
    "IDENTICAL asset; no estimated cross-asset hedge",
    "LOW TURNOVER is a first-class design constraint -- entries/exits sparse and "
    "cost-aware from the start; carry is judged NET of all-in AND perp-specific costs "
    "(funding/borrow/liquidation) at the replay gate; raw carry is never the edge",
    "NOT a rescue or retune of C20: C20's high-turnover timing strategy stays REJECTED "
    "and on record; this is a NEW family with a different (persistence/low-turnover) "
    "operating principle",
    "no detector / labels / replay / optimization / rescue / parameter tuning in or "
    "after this proposal until each downstream gate is separately human-approved; "
    "promotion requires a net-positive carry edge vs random/null risk-adjusted AND "
    "turnover-efficient, surviving forward-OOS; this proposal does NOT start C22",
)

NEXT_HUMAN_GATE_AFTER_PROPOSAL = (
    "HUMAN_DECISION_C21_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "rescues_c20", "retunes_c20", "reactivates_c20", "runs_robustness",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "adds_new_instrument_class", "uses_xauusd",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "starts_c22", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_21_proposal_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 family "
        "proposal (READ-ONLY, RESEARCH ONLY, PURE PROPOSAL). Harvest the SAME "
        "mechanically-neutral same-asset CARRY that C20's always-on benchmark proved "
        "real (+21.2%, Sharpe 1.09) but with LOW TURNOVER / HOLD PERSISTENCE instead of "
        "C20's high-turnover timing (704 round-trips x 74 bps = 521% drag that lost "
        "-74.5%). Mechanically neutral (not estimated), CARRY source (not buy-and-hold "
        "beta, not OHLCV timing), turnover minimised BY DESIGN. Compares six low-turnover "
        "sub-families. NOT a rescue/retune of C20 (C20 stays rejected). PROPOSAL ONLY: "
        "advancing to the candidate-spec gate needs an explicit human decision. NO "
        "detector, NO labels, NO replay, NO optimization, NO data fetch, NO XAUUSD, NO "
        "paper/live, does NOT start C22. NOT a profitability claim.")


def get_candidate_21_proposal_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_PROPOSAL


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def build_c21_proposal(repo_root: Any = ".",
                       tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #21 family-proposal record. Pure; no I/O;
    proposal only. Chain-gated on the committed data-readiness review (the frozen
    spot/perp/funding dataset must be FROZEN_AND_READY)."""
    dr = _dr.build_data_readiness_review()
    dr_valid = _dr.validate_data_readiness_review(dr)["valid"]
    dr_verdict = dr.get("readiness_verdict")

    blockers: list = []
    if not dr_valid:
        blockers.append("data_readiness_review_invalid")
    if dr_verdict != EXPECTED_DATA_VERDICT:
        blockers.append("dataset_not_frozen_and_ready")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C20:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C21_SCHEMA_VERSION, "mode": C21_MODE, "lane": C21_LANE,
        "label": get_candidate_21_proposal_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_proposal_only": True,
        "blockers": blockers,
        "verdict": ("C21_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C21_PROPOSAL_BLOCKED"),
        # chain provenance (built on the frozen dataset)
        "data_readiness_verdict": dr_verdict,
        "data_readiness_valid": dr_valid,
        "promoted_from_data_readiness_review":
            "crypto_basis_funding_data_readiness_review_v1",
        "approved_via": "HUMAN_APPROVED_C21_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL",
        # built ON the preserved C20 lesson; NOT a rescue/retune of C20
        "c20_lesson_preserved": _deepish(C20_LESSON_PRESERVED),
        "is_rescue_or_retune_of_c20": False,
        "c20_remains_rejected": True,
        # the required explanation sections
        "family_thesis": FAMILY_THESIS,                                  # 1
        "why_different_from_c1_c20": list(WHY_DIFFERENT_FROM_C1_C20),     # 2
        "mechanical_neutrality_gate_zero": dict(MECHANICAL_NEUTRALITY_GATE_ZERO),  # 3
        "low_turnover_design_principle": dict(LOW_TURNOVER_DESIGN_PRINCIPLE),
        "sub_families": [dict(s) for s in SUB_FAMILIES],                # 4
        "evaluation_metrics": _deepish(EVALUATION_METRICS),            # 5
        "cost_assumptions": dict(COST_ASSUMPTIONS),                    # 6
        "data_requirements": _deepish(DATA_REQUIREMENTS),              # 7
        "oos_validation": dict(OOS_VALIDATION),                        # 8
        "safety_boundaries": list(SAFETY_BOUNDARIES),                  # 9
        # universe + data
        "universe": list(UNIVERSE),
        "timeframe": TIMEFRAME,
        "data_source": DATA_SOURCE,
        "uses_frozen_public_spot_perp_funding_only": True,
        "no_new_data_fetch": True,
        "no_new_instrument_class": True,
        # identity / anti-loop
        "is_market_neutral": True,
        "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "carries_buy_and_hold_beta": False,
        "is_directional_timing_signal": False,
        "is_low_turnover": True,
        "prioritizes_hold_persistence": True,
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "rejected_families_c1_to_c20": list(REJECTED_FAMILIES_C1_TO_C20),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C20),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C20,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "family_proposal",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "next_human_gate_after_proposal": NEXT_HUMAN_GATE_AFTER_PROPOSAL,
        "does_not_start_c22": True,
        "c22_candidate_id": None,
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
        "no_rescue_c20": True, "no_retune_c20": True, "no_reactivate_c20": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_net_market_beta": True,
        "no_estimated_cross_asset_hedge": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c22": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c21_proposal(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the proposal is research-only, pure-
    proposal-only, chain-gated on the FROZEN_AND_READY data-readiness review, a
    LOW-TURNOVER mechanically-neutral same-asset spot/perp funding-carry family NOT in
    the C1-C20 (25) ledger, with mechanical (not estimated) neutrality as gate zero, a
    carry (not buy-and-hold-beta, not timing) return source, LOW TURNOVER as a
    first-class design constraint, materially different from C20 (NOT a rescue/retune),
    the frozen public spot/perp/funding-only universe (no fetch, no new instrument
    class), six low-turnover sub-families, the market-neutral + risk-adjusted +
    turnover-efficient + forward-OOS evaluation (judged vs random/null, NOT
    buy-and-hold) with 37 bps + perp frictions reserved for replay, preserves the gate
    sequence, keeps downstream gates locked, does not start C22, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != C21_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_proposal_only") is not True:
        failures.append("not_pure_proposal_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C21_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen dataset
    if record.get("data_readiness_valid") is not True:
        failures.append("data_readiness_not_valid")
    if record.get("data_readiness_verdict") != EXPECTED_DATA_VERDICT:
        failures.append("dataset_not_frozen_and_ready")
    if record.get("promoted_from_data_readiness_review") != (
            "crypto_basis_funding_data_readiness_review_v1"):
        failures.append("promoted_from_wrong_source")

    # identity: candidate #21, mechanically neutral same-asset, carry, low turnover
    if record.get("candidate_id") != "C21":
        failures.append("candidate_id_not_c21")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing", "is_low_turnover",
              "prioritizes_hold_persistence"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("is_directional_timing_signal") is not False:
        failures.append("must_not_be_directional_timing")
    gz = record.get("mechanical_neutrality_gate_zero") or {}
    if gz.get("is_gate_zero") is not True:
        failures.append("gate_zero_flag_wrong")
    if gz.get("neutrality_is_mechanical_not_estimated") is not True:
        failures.append("neutrality_must_be_mechanical")
    if gz.get("no_cross_asset_hedge_estimation") is not True:
        failures.append("must_not_estimate_cross_asset_hedge")

    # low-turnover design principle is first-class + NOT a rescue/retune of C20
    lt = record.get("low_turnover_design_principle") or {}
    if lt.get("is_first_class_design_constraint") is not True:
        failures.append("low_turnover_not_first_class")
    if lt.get("prioritizes_hold_persistence") is not True:
        failures.append("does_not_prioritize_persistence")
    if lt.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("design_principle_must_not_be_c20_retune")
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue_or_retune")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_must_remain_rejected")
    lp = record.get("c20_lesson_preserved") or {}
    if lp.get("carry_source_is_real") is not True:
        failures.append("must_preserve_carry_real_lesson")
    if lp.get("c20_failed_due_to_churn_cost_not_signal") is not True:
        failures.append("must_preserve_c20_churn_lesson")
    if lp.get("always_on_neutral_carry_net_return") != 0.211648:
        failures.append("c20_lesson_number_tampered")

    # anti-loop + materially different (esp. vs C20)
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("candidate_family") in REJECTED_FAMILIES_C1_TO_C20:
        failures.append("family_listed_as_rejected")
    if record.get("rejected_families_count") != 25:
        failures.append("ledger_not_25")
    diffs = record.get("why_different_from_c1_c20") or []
    if len(diffs) < 4:
        failures.append("insufficient_difference_explanation")
    joined = " ".join(diffs)
    for must in ("C20", "LOW-TURNOVER", "PERSISTENCE", "CARRY"):
        if must not in joined:
            failures.append("difference_missing_%s" % must)

    # universe + data: frozen public spot/perp/funding only, no fetch, no new instrument
    if list(record.get("universe") or []) != ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        failures.append("universe_not_btc_eth_sol_perp")
    if record.get("uses_frozen_public_spot_perp_funding_only") is not True:
        failures.append("not_frozen_public_only")
    if record.get("no_new_data_fetch") is not True:
        failures.append("must_not_fetch_data")
    if record.get("no_new_instrument_class") is not True:
        failures.append("must_not_add_instrument_class")
    dr = record.get("data_requirements") or {}
    if dr.get("no_data_fetched_here") is not True:
        failures.append("data_fetch_flag_wrong")
    if (dr.get("spot_perp_funding_d1") or {}).get("available_locally") is not True:
        failures.append("data_should_be_local")
    if dr.get("no_xauusd_or_new_instrument_class") is not True:
        failures.append("data_adds_new_instrument_class")

    # the six LOW-TURNOVER sub-families
    subs = record.get("sub_families") or []
    if len(subs) != 6:
        failures.append("sub_families_not_six")
    keys = {s.get("key") for s in subs}
    for must in ("persistent_positive_carry_hold", "carry_regime_gated_hold",
                 "funding_threshold_hysteresis_hold", "slow_periodic_rebalanced_carry",
                 "top_carry_asset_concentration_hold",
                 "always_on_carry_with_breakdown_circuit_breaker"):
        if must not in keys:
            failures.append("sub_family_missing_%s" % must)

    # evaluation: carry vs random/null + risk-adjusted + turnover-efficient, not B&H
    em = record.get("evaluation_metrics") or {}
    if "net_price_beta_mechanical" not in (em.get("primary_market_neutral") or ()):
        failures.append("missing_mechanical_neutrality_metric")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "round_trips_per_year" not in (em.get("turnover_efficiency") or ()):
        failures.append("missing_turnover_efficiency_metric")
    if em.get("low_turnover_is_evaluation_dimension") is not True:
        failures.append("turnover_not_evaluation_dimension")
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random_null")
    if em.get("judged_against_buy_and_hold") is not False:
        failures.append("must_not_be_judged_vs_buy_and_hold")
    ct = record.get("cost_assumptions") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("round_trip_cost_per_trade_bps") != 74.0:
        failures.append("two_leg_cost_not_doubled")
    if ct.get("cost_applied_only_at_replay_gate") is not True:
        failures.append("cost_not_reserved_for_replay")
    if not ct.get("perp_specific_frictions_reserved_for_replay"):
        failures.append("perp_frictions_not_reserved")

    # OOS required, mechanical neutrality, low turnover holds OOS, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_is_mechanical_so_cannot_fail_oos") is not True:
        failures.append("oos_neutrality_claim_missing")
    if oos.get("forward_oos_must_hold_low_turnover") is not True:
        failures.append("oos_low_turnover_claim_missing")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # gate sequence + downstream locks + no C22
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_PROPOSAL:
        failures.append("next_action_not_spec_gate")
    if record.get("does_not_start_c22") is not True:
        failures.append("must_not_start_c22")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                "no_retune_c20", "no_data_fetch", "no_new_instrument_class",
                "no_xauusd", "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_net_market_beta", "no_estimated_cross_asset_hedge",
                "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_rejected_family_repropose", "no_start_c22"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
