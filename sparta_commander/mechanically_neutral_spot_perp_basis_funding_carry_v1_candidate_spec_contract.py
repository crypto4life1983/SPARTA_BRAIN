"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- CANDIDATE SPEC (PURE, RESEARCH ONLY).

The human-approved (HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC) formal candidate
specification for the frozen C20 family proposal: a SAME-ASSET long-spot / short-perp
basis + funding carry on the frozen PUBLIC BTC/ETH/SOL spot+perp+funding dataset, where
market-neutrality is MECHANICAL (long 1 unit spot / short 1 unit USDT-perp of the
IDENTICAL underlying in equal notional) -- so net price beta is ~0 BY CONSTRUCTION, not
by estimation. This is a pure, in-memory specification: it DECLARES the EXACT rules
(basis calculation / funding calculation / the gate-zero mechanical-neutrality
requirement / entry / exit / stop & invalidation / turnover / non-overlap / replay win
criteria), the frozen BTC/ETH/SOL D1 spot+perp+funding universe and data limitations,
the market-neutral evaluation judged vs random/null (NOT buy-and-hold), the reserved
fee-honest + perp-specific replay cost, the out-of-sample requirement, the rejection
criteria, and the next human gate. It is chain-gated on the committed C20 proposal.

It builds NO detector, NO labels, NO replay; runs NO PnL / optimization / rescue /
tuning / data fetch; touches NO paper/live/broker/order surface; and does NOT start
C21. Every capability flag is pinned False with a full scope_locks set. The next gate
(detector spec + synthetic dry-run) still requires an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_proposal_contract as _c20p  # noqa: E501

C20S_SCHEMA_VERSION = 1
C20S_MODE = "RESEARCH_ONLY"
C20S_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c20p.CANDIDATE_ID
CANDIDATE_FAMILY = _c20p.CANDIDATE_FAMILY
CANDIDATE_NAME = _c20p.CANDIDATE_NAME

EXPECTED_PROPOSAL_VERDICT = "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + timeframe + data limitations --------------------------------
UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAME = "D1"
DATA_SOURCE = ("frozen PUBLIC Binance spot + USDT-perp + funding D1 (the committed "
               "data-readiness review dataset) -- already local, no fetch")

# --- declared (NOT fitted) construction parameters --------------------------
# A pre-registered starting specification, not optimized values. No parameter search
# is performed or permitted at this gate.
SPEC_PARAMS = {
    "same_asset_legs": True,               # long spot, short perp of the IDENTICAL asset
    "equal_notional_legs": True,           # |spot notional| == |perp notional| at entry
    "net_price_beta_target": 0.0,          # mechanical: price exposure cancels by build
    "max_gross_exposure": 1.0,             # no leverage; sum of |leg notionals| <= 1.0
    "basis_definition": "perp_close_minus_spot_close_over_spot_close",  # relative basis
    "basis_zscore_window_bars": 60,        # rolling window for basis mean/std (D1)
    "funding_lookback_bars": 30,           # window to assess funding-carry sign/strength
    "entry_basis_zscore_threshold": 2.0,   # basis-reversion entry when |basis z| >= this
    "entry_min_annualized_carry_bps": 50.0,  # carry entry: required net annualized carry
    "exit_basis_zscore_threshold": 0.25,   # basis-reversion exit on convergence
    "stop_basis_zscore_threshold": 4.0,    # basis-divergence invalidation
    "negative_carry_stand_down": True,     # stand aside when carry regime is negative
    "min_bars_between_rebalances": 5,      # turnover floor / low-frequency (D1 bars)
    "no_parameter_optimization": True,
    "no_parameter_tuning": True,
    "no_rescue_variant": True,
}

# --- 1. EXACT basis calculation rule ----------------------------------------
BASIS_CALCULATION_RULE = (
    "For each asset, on each D1 bar, compute the SAME-ASSET spot-perp BASIS as the "
    "relative premium of the USDT-perp over spot: basis = (perp_close - spot_close) / "
    "spot_close, using the frozen public spot and USDT-perp closes for the IDENTICAL "
    "underlying (BTCUSDT spot vs BTCUSDT perp, etc.). The basis is the ONLY residual "
    "exposure of the long-spot / short-perp position; it is standardized to a rolling "
    "z-score over basis_zscore_window_bars. This is a same-asset basis, NOT an "
    "estimated cross-asset hedge spread (the C16/C19 failure mode being explicitly "
    "avoided).")

# --- 2. EXACT funding calculation rule --------------------------------------
FUNDING_CALCULATION_RULE = (
    "Funding carry is the cash the SHORT-perp leg earns (or pays). On each D1 bar, take "
    "the asset's perp funding rate(s) from the frozen public funding history (summing "
    "the intraday funding events into the D1 bar) -- a SHORT perp RECEIVES funding when "
    "the funding rate is positive and PAYS when negative. Aggregate the carry signal "
    "over funding_lookback_bars into an annualized expected funding carry (bps). The "
    "funding carry plus the convergent basis is the candidate return source; it is a "
    "carry, not a directional OHLCV timing signal.")

# --- 3. EXACT gate-zero mechanical-neutrality rule --------------------------
MECHANICAL_NEUTRALITY_GATE_ZERO_RULE = (
    "GATE ZERO, before ANY carry/basis logic is evaluated: the position MUST be long 1 "
    "unit spot and short 1 unit USDT-perp of the SAME asset in EQUAL notional, so the "
    "net price beta is ~0 BY CONSTRUCTION (mechanical), not by an estimated hedge ratio. "
    "No cross-asset hedge is estimated and no net market beta is carried. Because the "
    "neutrality is mechanical it CANNOT 'fail out of sample' the way C16's level-OLS "
    "hedge and C19's return-beta hedge did. Any construction that is not same-asset, "
    "equal-notional, long-spot/short-perp is rejected at this gate before any trading "
    "rule is applied.")

# --- 4. EXACT entry rule ----------------------------------------------------
ENTRY_RULE = (
    "Open the mechanically-neutral position (long spot / short perp, equal notional, "
    "same asset) ONLY when a positive-expected-carry condition holds: EITHER (a) the "
    "expected annualized funding carry to the short-perp leg >= "
    "entry_min_annualized_carry_bps AND the basis/funding regime is NOT negative-carry "
    "(funding-carry entry), OR (b) the basis z-score is richly extreme "
    "(basis z >= +entry_basis_zscore_threshold, perp at a premium that is expected to "
    "converge) so the short-perp leg captures convergence (basis-reversion entry). "
    "Position notionals keep |spot| == |perp| (equal notional), net price beta ~0, and "
    "gross <= max_gross_exposure. Entries are spaced by >= min_bars_between_rebalances "
    "bars (turnover floor).")

# --- 5. EXACT exit rule -----------------------------------------------------
EXIT_RULE = (
    "Exit when the harvested edge has played out: for a basis-reversion entry, exit when "
    "|basis z| <= exit_basis_zscore_threshold (the perp premium has converged toward "
    "fair); for a funding-carry entry, exit when the expected annualized funding carry "
    "falls below entry_min_annualized_carry_bps (the carry is no longer paid) or the "
    "regime turns negative-carry. No fixed time/horizon exit. On exit BOTH legs (spot "
    "and perp) are unwound together so the position stays neutral through the lifecycle.")

# --- 6. EXACT stop / invalidation rule --------------------------------------
STOP_INVALIDATION_RULE = (
    "Two structural invalidations, no discretionary averaging: (a) BASIS-DIVERGENCE "
    "STOP -- if |basis z| >= stop_basis_zscore_threshold the basis has blown out beyond "
    "its structural band (convergence thesis invalidated, not a reason to add) and the "
    "position is closed; (b) NEGATIVE-CARRY / NEUTRALITY-BREAK INVALIDATION -- if the "
    "carry regime flips persistently negative (the short-perp leg now PAYS funding with "
    "no offsetting basis convergence), or the two legs can no longer be held in equal "
    "notional (mechanical neutrality would break), stand down / close. Neither is a "
    "drawdown-percent threshold.")

# --- 7. EXACT turnover constraint rule --------------------------------------
TURNOVER_CONSTRAINT_RULE = (
    "Low turnover is a REQUIREMENT, not a free parameter: re-balance / re-enter no more "
    "often than every min_bars_between_rebalances bars, hold gross <= max_gross_exposure "
    "(no leverage), and prefer holding a live neutral carry position to churning it. "
    "Because the position has TWO legs (spot and perp) and each leg pays the 37 bps "
    "all-in round-trip, turnover is the dominant cost risk and is bounded by "
    "construction; the carry must out-earn the doubled round-trip plus the perp-specific "
    "frictions reserved for replay.")

# --- 8. EXACT non-overlap rule ----------------------------------------------
NON_OVERLAP_RULE = (
    "At most ONE live mechanically-neutral basis/funding-carry position PER ASSET at a "
    "time (one long-spot/short-perp construction per underlying). A new entry on an "
    "asset cannot open while that asset's position is live; there are no overlapping "
    "duplicate basis exposures and no stacking of the same leg. One trade lifecycle = "
    "entry -> convergence/carry-decay/stop exit, non-overlapping.")

# --- 9. EXACT replay win criteria -------------------------------------------
REPLAY_WIN_CRITERIA = (
    "At the (future, separately human-gated) fee-honest replay, the candidate WINS only "
    "if the same-asset basis/funding carry is NET-POSITIVE versus a random / zero-edge "
    "null on the SAME neutral position -- on a RISK-ADJUSTED basis (Sharpe / Calmar) -- "
    "AND survives forward-OOS, NET of the 37 bps all-in round-trip counted on BOTH legs "
    "PLUS the perp-specific frictions (funding paid/received, perp borrow, "
    "liquidation-aware margin) and realistic basis-convergence execution. It is NOT "
    "judged versus buy-and-hold (there is no net market exposure). Raw carry before "
    "these costs is never the edge.")

# --- sub-families declared in the proposal (variants to compare later) ------
SUB_FAMILIES = tuple(s["key"] for s in _c20p.SUB_FAMILIES)

# --- evaluation metrics (market-neutral; judged vs random / null) -----------
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_price_beta_mechanical", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "carry_diagnostics": ("annualized_carry", "funding_collected", "basis_convergence",
                          "negative_carry_regime_share"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "diagnostics": ("net_return", "profit_factor", "win_rate", "avg_R_per_trade",
                    "turnover_low", "leg_notional_neutrality"),
    "baseline": ("a random/zero-edge null on the SAME neutral basis position, net of "
                 "ALL-IN and perp-specific cost -- NOT buy-and-hold (there is no net "
                 "market exposure to compare against)"),
    "win_condition": ("a NET-POSITIVE carry edge vs random / null on a RISK-ADJUSTED "
                      "basis AND surviving forward-OOS, net of funding/borrow/"
                      "liquidation-aware costs -- not raw carry before costs"),
    "neutrality_is_mechanical_precondition": True,
    "judged_against_buy_and_hold": False,   # explicitly NOT vs holding BTC
}

# --- cost (reserved for the replay gate) ------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
COST_RESERVED = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "two_legs_spot_and_perp_so_cost_counts_double_per_rebalance": True,
    "perp_specific_frictions_reserved_for_replay": (
        "funding paid/received, perp borrow, and liquidation-aware margin must be "
        "modelled at the replay gate -- carry before these costs is NOT the edge"),
    "basis_convergence_execution_modelled_at_replay": True,
    "perp_spot_execution_assumptions": (
        "both legs filled at the D1 close with the all-in cost; the short-perp leg "
        "additionally accrues funding and is liquidation-aware -- modelled at replay"),
    "applied_at_replay_gate_only": True,
    "applied_here": False,
}

# --- data requirements (frozen BTC/ETH/SOL spot+perp+funding; nothing fetched)
DATA_REQUIREMENTS = {
    "spot_perp_funding_d1": {"required": True, "available_locally": True,
                             "note": "the committed data-readiness review dataset "
                                     "(BTC/ETH/SOL spot+perp+funding) -- frozen, "
                                     "SHA-pinned, gitignored"},
    "no_data_fetched_here": True,
    "no_new_data_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- out-of-sample validation -----------------------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_carry_edge_net_of_cost": True,
    "neutrality_is_mechanical_so_cannot_fail_oos": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- how it differs from the relevant rejected families ---------------------
DIFFERENCE_FROM_REJECTED = {
    "vs_c16_level_ols_estimated_neutrality": (
        "C16 ESTIMATED a hedge ratio on PRICE LEVELS via OLS and ASSUMED neutrality; it "
        "failed OOS (net beta 2.82). This spec uses SAME-ASSET MECHANICAL neutrality "
        "(long spot / short perp of the identical underlying, equal notional) -- net "
        "price beta is ~0 by construction and cannot drift out of sample."),
    "vs_c19_return_beta_estimated_neutrality": (
        "C19 estimated a return-beta cross-sectional hedge among BTC/ETH/SOL whose "
        "OOS neutrality held on only ~44% of bars. Here there is NOTHING to estimate: "
        "the long-spot/short-perp legs are the SAME asset in equal notional, so "
        "neutrality is mechanical, not statistical."),
    "vs_c17_long_only_allocation": (
        "C17 was a LONG-ONLY vol-targeted / risk-parity allocation judged vs "
        "buy-and-hold; it cut drawdown but lost risk-adjusted. This carries NO net "
        "market exposure and is judged vs random / null, not buy-and-hold."),
    "vs_c18_long_biased_timing": (
        "C18 was a long-biased H4 directional timing approximation that could not beat "
        "BTC buy-and-hold risk-adjusted. This carries NO buy-and-hold beta and its "
        "return source is CARRY (basis/funding), not a price-pattern timing signal."),
}

# --- rejection criteria (decisive, evaluated only at the replay/labels gate) -
REJECTION_CRITERIA = {
    "reject_if_not_mechanically_neutral": True,        # gate zero
    "reject_if_not_net_positive_vs_random_null": True,
    "reject_if_not_risk_adjusted_positive": True,
    "reject_if_forward_oos_edge_fails": True,
    "reject_if_carry_does_not_cover_two_leg_and_perp_costs": True,
    "reject_if_turnover_too_high_cost_dominates": True,
    "raw_carry_alone_is_not_sufficient": True,
    "not_judged_against_buy_and_hold": True,
}

NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C20_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "trades_before_neutrality_validated",
    "allows_overlapping_positions", "adds_new_instrument_class", "uses_xauusd",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "starts_c21", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_rescue": True,
        "no_robustness": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_net_market_beta": True,
        "no_estimated_cross_asset_hedge": True,
        "no_trade_before_neutrality_validated": True,
        "no_overlapping_positions": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c21": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_20_spec_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 "
        "(READ-ONLY, RESEARCH ONLY, PURE CANDIDATE SPEC). EXACT same-asset basis + "
        "funding-carry rules (relative spot-perp basis, D1 funding aggregation, "
        "GATE-ZERO MECHANICAL neutrality, carry/basis-z entry, convergence/carry-decay "
        "exit, basis-divergence & negative-carry invalidation, low-turnover constraint, "
        "one-position-per-asset non-overlap, cost-honest replay win criteria) on frozen "
        "public BTC/ETH/SOL spot+perp+funding D1 -- carrying NO buy-and-hold beta and NO "
        "estimated cross-asset hedge, materially different from C16/C17/C18/C19. SPEC "
        "ONLY: the next gate (detector spec + synthetic dry-run) needs an explicit "
        "human decision. NO data fetch, NO detector, NO labels, NO replay, NO "
        "optimization / rescue / tuning, NO XAUUSD, NO paper/live, does NOT start C21. "
        "NOT a profitability claim.")


def get_candidate_20_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def build_c20_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #20 candidate-spec record. Pure; no I/O; spec
    only. Chain-gated on the committed C20 proposal (frozen, this exact family)."""
    proposal = _c20p.build_c20_proposal(repo_root, tracked_paths)
    proposal_valid = _c20p.validate_c20_proposal(proposal)["valid"]
    proposal_verdict = proposal.get("verdict")
    proposal_family = proposal.get("candidate_family")

    blockers: list = []
    if not proposal_valid:
        blockers.append("c20_proposal_invalid")
    if proposal_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c20_proposal_not_frozen")
    if proposal_family != CANDIDATE_FAMILY:
        blockers.append("proposal_family_mismatch")

    record: dict[str, Any] = {
        "schema_version": C20S_SCHEMA_VERSION, "mode": C20S_MODE, "lane": C20S_LANE,
        "label": get_candidate_20_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C20_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C20_SPEC_BLOCKED"),
        # chain provenance
        "source_proposal_verdict": proposal_verdict,
        "source_proposal_valid": proposal_valid,
        "source_proposal_family": proposal_family,
        # the spec
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "universe": list(UNIVERSE),
        "timeframe": TIMEFRAME,
        "data_source": DATA_SOURCE,
        "spec_params": dict(SPEC_PARAMS),
        # the EXACT rules
        "basis_calculation_rule": BASIS_CALCULATION_RULE,
        "funding_calculation_rule": FUNDING_CALCULATION_RULE,
        "mechanical_neutrality_gate_zero_rule": MECHANICAL_NEUTRALITY_GATE_ZERO_RULE,
        "entry_rule": ENTRY_RULE,
        "exit_rule": EXIT_RULE,
        "stop_invalidation_rule": STOP_INVALIDATION_RULE,
        "turnover_constraint_rule": TURNOVER_CONSTRAINT_RULE,
        "non_overlap_rule": NON_OVERLAP_RULE,
        "replay_win_criteria": REPLAY_WIN_CRITERIA,
        "sub_families": list(SUB_FAMILIES),
        # identity
        "is_market_neutral": True,
        "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "carries_buy_and_hold_beta": False,
        "is_directional_timing_signal": False,
        "positions_non_overlapping": True,
        "low_turnover_required": True,
        # how it differs from the rejected families
        "difference_from_rejected": _deepish(DIFFERENCE_FROM_REJECTED),
        # evaluation + cost reserved
        "evaluation_metrics": _deepish(EVALUATION_METRICS),
        "cost_reserved": dict(COST_RESERVED),
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        # data requirements (nothing fetched)
        "data_requirements": _deepish(DATA_REQUIREMENTS),
        "no_new_data_fetch": True,
        "no_new_instrument_class": True,
        # OOS + rejection criteria
        "oos_validation": dict(OOS_VALIDATION),
        "rejection_criteria": dict(REJECTION_CRITERIA),
        "next_human_gate_after_spec": NEXT_HUMAN_GATE_AFTER_SPEC,
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_SPEC,
        "does_not_start_c21": True,
        "c21_candidate_id": None,
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_c20_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C20 proposal for this exact family, a
    MARKET-NEUTRAL same-asset basis/funding-carry strategy whose neutrality is
    MECHANICAL (not estimated) carrying no buy-and-hold beta and no estimated
    cross-asset hedge, defines all NINE exact rules (basis / funding / gate-zero
    mechanical neutrality / entry / exit / stop & invalidation / turnover / non-overlap
    / replay win criteria), declares the frozen BTC/ETH/SOL D1 spot+perp+funding
    universe (no fetch, no new instrument class), explains the difference from
    C16 / C17 / C18 / C19, reserves the 37 bps all-in plus perp-specific replay cost,
    carries the market-neutral evaluation + OOS + rejection criteria, preserves the
    gate sequence, keeps downstream gates locked, does not start C21, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != C20S_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C20_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C20 proposal for this exact family
    if record.get("source_proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("source_proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("source_proposal_family") != CANDIDATE_FAMILY:
        failures.append("proposal_family_mismatch")

    # identity: candidate #20, market-neutral, MECHANICAL (not estimated), carry
    if record.get("candidate_id") != "C20":
        failures.append("candidate_id_not_c20")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing", "positions_non_overlapping",
              "low_turnover_required"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("is_directional_timing_signal") is not False:
        failures.append("must_not_be_directional_timing_signal")

    # all nine EXACT rules present and non-empty
    for rule in ("basis_calculation_rule", "funding_calculation_rule",
                 "mechanical_neutrality_gate_zero_rule", "entry_rule", "exit_rule",
                 "stop_invalidation_rule", "turnover_constraint_rule",
                 "non_overlap_rule", "replay_win_criteria"):
        if not record.get(rule):
            failures.append("missing_rule_%s" % rule)

    # spec params declared, not optimized/tuned/rescued; mechanical neutrality params
    sp = record.get("spec_params") or {}
    if sp.get("same_asset_legs") is not True:
        failures.append("params_not_same_asset_legs")
    if sp.get("equal_notional_legs") is not True:
        failures.append("params_not_equal_notional")
    if sp.get("net_price_beta_target") != 0.0:
        failures.append("net_price_beta_target_not_zero")
    if sp.get("max_gross_exposure") != 1.0:
        failures.append("gross_exposure_not_one")
    for k in ("no_parameter_optimization", "no_parameter_tuning",
              "no_rescue_variant"):
        if sp.get(k) is not True:
            failures.append("params_allow_%s" % k)

    # universe + data: frozen BTC/ETH/SOL D1 spot+perp+funding only, no fetch
    if list(record.get("universe") or []) != ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
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
    if (dr.get("spot_perp_funding_d1") or {}).get("available_locally") is not True:
        failures.append("d1_data_should_be_local")
    if dr.get("no_xauusd_or_new_instrument_class") is not True:
        failures.append("data_adds_new_instrument_class")

    # difference from C16 / C17 / C18 / C19 explained
    diff = record.get("difference_from_rejected") or {}
    for k in ("vs_c16_level_ols_estimated_neutrality",
              "vs_c19_return_beta_estimated_neutrality",
              "vs_c17_long_only_allocation", "vs_c18_long_biased_timing"):
        if not diff.get(k):
            failures.append("missing_difference_%s" % k)

    # evaluation: market-neutral vs random/null, NOT vs buy-and-hold; cost reserved
    em = record.get("evaluation_metrics") or {}
    if "net_price_beta_mechanical" not in (em.get("primary_market_neutral") or ()):
        failures.append("missing_net_price_beta_metric")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random_null")
    if em.get("neutrality_is_mechanical_precondition") is not True:
        failures.append("neutrality_not_precondition")
    if em.get("judged_against_buy_and_hold") is not False:
        failures.append("must_not_be_judged_vs_buy_and_hold")
    ct = record.get("cost_reserved") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if not ct.get("perp_specific_frictions_reserved_for_replay"):
        failures.append("perp_frictions_not_reserved")
    if ct.get("applied_at_replay_gate_only") is not True or ct.get(
            "applied_here") is not False:
        failures.append("cost_not_reserved_for_replay")

    # OOS required, mechanical neutrality, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_is_mechanical_so_cannot_fail_oos") is not True:
        failures.append("neutrality_not_mechanical_oos")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # rejection criteria preserved (gate-zero + market-neutral, not vs buy-and-hold)
    rc = record.get("rejection_criteria") or {}
    for k in ("reject_if_not_mechanically_neutral",
              "reject_if_not_net_positive_vs_random_null",
              "reject_if_forward_oos_edge_fails", "raw_carry_alone_is_not_sufficient",
              "not_judged_against_buy_and_hold"):
        if rc.get(k) is not True:
            failures.append("rejection_criterion_off_%s" % k)

    # gate sequence + downstream locks + no C21
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    if record.get("does_not_start_c21") is not True:
        failures.append("must_not_start_c21")
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_xauusd", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_net_market_beta",
                "no_estimated_cross_asset_hedge",
                "no_trade_before_neutrality_validated",
                "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_start_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
