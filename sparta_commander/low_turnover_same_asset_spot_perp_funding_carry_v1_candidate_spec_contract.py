"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- CANDIDATE SPEC (PURE, RESEARCH ONLY).

The human-approved (HUMAN_DECISION_C21_ADVANCE_TO_CANDIDATE_SPEC) formal candidate
specification for the frozen C21 family proposal: a LOW-TURNOVER, same-asset long-spot /
short-perp funding carry on the frozen PUBLIC BTC/ETH/SOL spot+perp+funding dataset,
where market-neutrality is MECHANICAL (long 1 unit spot / short 1 unit USDT-perp of the
IDENTICAL underlying in equal notional) and the carry is harvested with HOLD PERSISTENCE
(sparse, cost-aware entries; durable-carry-breakdown exits) so the 74 bps two-leg cost
that killed C20 cannot dominate.

This is a pure, in-memory specification: it DECLARES the EXACT rules (basis calculation /
funding calculation / the gate-zero mechanical-neutrality requirement / carry-regime gate
/ entry & exit hysteresis / hold-persistence + minimum-hold / turnover & round-trip limits
/ rebalance cadence / durable carry-regime breakdown exit / replay win criteria), the
frozen BTC/ETH/SOL D1 spot+perp+funding universe, a FINITE FROZEN configuration family (no
optimization), the market-neutral + TURNOVER-EFFICIENT evaluation judged vs the always-on
carry + random/null baselines (NOT buy-and-hold), the reserved fee-honest + perp-specific
replay cost, the out-of-sample requirement, the rejection criteria, and the next human
gate. It is chain-gated on the committed C21 proposal.

It PRESERVES THE C20 LESSON: C20's high-turnover timed strategy stays REJECTED; C20 failed
because churn/cost destroyed the result; the always-on neutral carry benchmark was
positive and is used ONLY as research evidence/inspiration. C21 is materially different
(c20_remains_rejected = True, is_rescue_or_retune_of_c20 = False).

It builds NO detector, NO labels, NO replay; runs NO PnL / optimization / rescue / tuning
/ data fetch; touches NO paper/live/broker/order surface; and does NOT start C22. Every
capability flag is pinned False with a full scope_locks set. C21 CANNOT be called
profitable or viable before detector validation, real-candle labeling, fee-honest replay,
OOS testing, and portfolio review. The next gate (detector spec + synthetic dry-run) still
requires an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_proposal_contract as _c21p  # noqa: E501

C21S_SCHEMA_VERSION = 1
C21S_MODE = "RESEARCH_ONLY"
C21S_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c21p.CANDIDATE_ID
CANDIDATE_FAMILY = _c21p.CANDIDATE_FAMILY
CANDIDATE_NAME = _c21p.CANDIDATE_NAME

EXPECTED_PROPOSAL_VERDICT = "C21_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

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
# A pre-registered, FINITE FROZEN configuration family -- not optimized values. No
# parameter search is performed or permitted at this gate.
SPEC_PARAMS = {
    "same_asset_legs": True,                  # long spot, short perp of the IDENTICAL asset
    "equal_notional_legs": True,              # |spot notional| == |perp notional| at entry
    "net_price_beta_target": 0.0,             # mechanical: price exposure cancels by build
    "max_gross_exposure": 1.0,                # no leverage; sum of |leg notionals| <= 1.0
    "basis_definition": "perp_close_minus_spot_close_over_spot_close",  # relative basis
    "carry_regime_window_bars": 30,           # slow window to judge carry-regime stability
    "annualized_carry_enter_bps": 100.0,      # HIGH entry threshold (regime stably positive)
    "annualized_carry_exit_bps": 0.0,         # LOW exit threshold (wide hysteresis band)
    "carry_regime_breakdown_bars": 7,         # consecutive negative-carry bars = breakdown
    "min_hold_bars": 20,                      # minimum hold once entered (persistence)
    "rebalance_cadence_bars": 30,             # rebalance no more often than ~monthly
    "max_round_trips_per_year_per_asset": 6,  # hard low-turnover ceiling
    "max_concurrent_positions_per_asset": 1,
    "finite_frozen_config_family": True,
    "no_parameter_optimization": True,
    "no_parameter_tuning": True,
    "no_rescue_variant": True,
}

# --- 1. EXACT basis calculation rule ----------------------------------------
BASIS_CALCULATION_RULE = (
    "For each asset, on each D1 bar, compute the SAME-ASSET spot-perp BASIS as the "
    "relative premium of the USDT-perp over spot: basis = (perp_close - spot_close) / "
    "spot_close, using the frozen public spot and USDT-perp closes for the IDENTICAL "
    "underlying. The basis is the only residual exposure of the long-spot / short-perp "
    "position; it is a same-asset basis, NOT an estimated cross-asset hedge spread or "
    "cointegration relationship (the C16/C19 failure mode being avoided).")

# --- 2. EXACT funding calculation rule --------------------------------------
FUNDING_CALCULATION_RULE = (
    "Funding carry is the cash the SHORT-perp leg earns. On each D1 bar, take the "
    "asset's perp funding rate(s) from the frozen public funding history (summing the "
    "intraday funding events into the D1 bar); a SHORT perp RECEIVES funding when the "
    "rate is positive and PAYS when negative. Aggregate over carry_regime_window_bars "
    "into an annualized expected funding carry (bps). The carry (plus a small convergent "
    "basis) is the return source; it is harvested by HOLDING, not by timing.")

# --- 3. EXACT gate-zero mechanical-neutrality rule --------------------------
MECHANICAL_NEUTRALITY_GATE_ZERO_RULE = (
    "GATE ZERO, before ANY carry/regime logic is evaluated: the position MUST be long 1 "
    "unit spot and short 1 unit USDT-perp of the SAME asset in EQUAL notional, so net "
    "price beta is ~0 BY CONSTRUCTION (mechanical), not by an estimated hedge ratio. No "
    "cross-asset hedge is estimated and no net market beta is carried. Because the "
    "neutrality is mechanical it CANNOT 'fail out of sample'.")

# --- 4. EXACT carry-regime gate rule ----------------------------------------
CARRY_REGIME_GATE_RULE = (
    "Trade ONLY in a stably positive carry regime: the annualized funding carry "
    "(averaged over carry_regime_window_bars) must be >= annualized_carry_enter_bps to "
    "qualify for entry. Negative / unstable carry regimes are stood aside entirely. The "
    "regime gate -- not basis noise -- is what governs participation; this is the "
    "opposite of C20's per-bar basis-z timing.")

# --- 5. EXACT entry & exit hysteresis rule ----------------------------------
ENTRY_EXIT_HYSTERESIS_RULE = (
    "WIDE HYSTERESIS to suppress churn: ENTER the mechanically-neutral position only "
    "when annualized carry >= annualized_carry_enter_bps (HIGH threshold) and no "
    "position is live for that asset; EXIT only when annualized carry falls below "
    "annualized_carry_exit_bps (a much LOWER threshold) -- never on a single-threshold "
    "crossing. The wide enter/exit band means small carry oscillations do NOT trigger "
    "round-trips. Entries keep |spot| == |perp| (equal notional), net price beta ~0, "
    "gross <= max_gross_exposure.")

# --- 6. EXACT hold-persistence + minimum-hold rule --------------------------
HOLD_PERSISTENCE_RULE = (
    "Once entered, HOLD: the position must be held for at least min_hold_bars before "
    "any non-stop exit is permitted, and is otherwise held continuously while the carry "
    "regime stays positive. Persistence is a REQUIREMENT, not an option -- the strategy "
    "prefers holding a live positive-carry position to re-evaluating it. This is the "
    "core C21 design lever: long average hold length amortises the 74 bps two-leg cost.")

# --- 7. EXACT turnover & round-trip limit rule ------------------------------
TURNOVER_LIMIT_RULE = (
    "Turnover is HARD-CAPPED by design: at most max_round_trips_per_year_per_asset "
    "complete round-trips per asset per year, rebalances no more often than every "
    "rebalance_cadence_bars bars, and gross <= max_gross_exposure (no leverage). Because "
    "the position has TWO legs paying 37 bps each (74 bps round-trip per trade), the "
    "low round-trip ceiling is the explicit control that keeps cost drag a small share "
    "of gross carry -- the variable that destroyed C20.")

# --- 8. EXACT durable carry-regime breakdown exit (stop) rule ---------------
DURABLE_BREAKDOWN_EXIT_RULE = (
    "Exits are SPARSE and only on a DURABLE breakdown: stand down / close a held "
    "position only after the carry regime has been negative for carry_regime_breakdown_"
    "bars CONSECUTIVE bars (a durable sign flip), OR if the two legs can no longer be "
    "held in equal notional (mechanical neutrality would break). A single negative "
    "funding print or transient basis blow-out is NOT an exit -- that would reintroduce "
    "C20's churn. There is no basis-z divergence stop and no drawdown-percent stop.")

# --- 9. EXACT replay win criteria -------------------------------------------
REPLAY_WIN_CRITERIA = (
    "At the (future, separately human-gated) fee-honest replay, the candidate WINS only "
    "if the low-turnover same-asset carry is NET-POSITIVE versus BOTH a random / "
    "zero-edge null AND the always-on neutral-carry benchmark on the SAME neutral "
    "position -- on a RISK-ADJUSTED (Sharpe / Calmar) AND TURNOVER-EFFICIENT basis (low "
    "round-trips, cost drag a small share of gross carry) -- AND survives forward-OOS, "
    "NET of the 37 bps all-in counted on BOTH legs (74 bps round-trip) PLUS the "
    "perp-specific frictions (funding paid/received, perp borrow, liquidation-aware "
    "margin) and realistic basis execution. It is NOT judged versus buy-and-hold. Raw "
    "carry before these costs, and any result that does not BEAT the always-on carry "
    "after cost, is not a win.")

# --- sub-families declared in the proposal (variants to compare later) ------
SUB_FAMILIES = tuple(s["key"] for s in _c21p.SUB_FAMILIES)

# --- evaluation metrics (market-neutral; turnover-aware; vs null + always-on)-
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_price_beta_mechanical", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "must_beat_always_on_carry_after_cost": True,
    "turnover_efficiency": ("round_trips_per_year", "two_leg_cost_drag",
                            "cost_drag_as_share_of_gross_carry", "avg_hold_length_days"),
    "carry_diagnostics": ("annualized_carry", "funding_collected", "net_carry_capture",
                          "negative_carry_regime_share"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "portfolio_value": ("expected_low_correlation", "capital_efficiency", "regime_breadth"),
    "baseline": ("a random/zero-edge null AND the always-on neutral-carry benchmark on "
                 "the SAME neutral position, net of ALL-IN and perp-specific cost -- NOT "
                 "buy-and-hold (there is no net market exposure)"),
    "win_condition": ("a NET-POSITIVE carry edge vs random / null AND beating the "
                      "always-on carry, on a RISK-ADJUSTED and TURNOVER-EFFICIENT basis, "
                      "surviving forward-OOS, net of funding/borrow/liquidation-aware "
                      "costs -- not raw carry, and not out-churned by cost like C20"),
    "neutrality_is_mechanical_precondition": True,
    "low_turnover_is_evaluation_dimension": True,
    "judged_against_buy_and_hold": False,
    "cannot_be_called_profitable_before_full_validation": True,
}

# --- cost (reserved for the replay gate) ------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
ROUND_TRIP_COST_PER_TRADE_BPS = 2 * ALL_IN_ROUND_TRIP_BPS             # 74.0 (two legs)
COST_RESERVED = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
    "two_legs_spot_and_perp_so_cost_counts_double_per_rebalance": True,
    "perp_specific_frictions_reserved_for_replay": (
        "funding paid/received, perp borrow, and liquidation-aware margin must be "
        "modelled at the replay gate -- carry before these costs is NOT the edge"),
    "low_turnover_is_the_cost_control_lever": (
        "C20 paid 74 bps x 704 round-trips = 521% drag; C21 caps round-trips so the "
        "same per-trade cost is amortised over long holds"),
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
    "forward_oos_must_hold_low_turnover": True,
    "neutrality_is_mechanical_so_cannot_fail_oos": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- how it differs from the relevant rejected families ---------------------
DIFFERENCE_FROM_REJECTED = {
    "vs_c20_high_turnover_timing": (
        "C20 was the SAME carry source but HIGH-TURNOVER TIMING (704 round-trips of "
        "basis-z entry/exit churn) and lost -74.5% to a 521% cost drag. C21 is "
        "LOW-TURNOVER / HOLD PERSISTENCE -- regime-gated entries, wide hysteresis, "
        "minimum-hold, a hard round-trip ceiling, durable-breakdown-only exits -- so "
        "turnover (and the 74 bps cost) is minimised by design. NOT a rescue/retune: "
        "C20 stays rejected; the OPERATING PRINCIPLE is opposite, not the thresholds."),
    "vs_c16_c19_estimated_neutrality": (
        "C16 (level-OLS) and C19 (return-beta) ESTIMATED cross-asset neutrality and "
        "failed OOS. Here neutrality is SAME-ASSET and MECHANICAL (long spot / short "
        "perp of the identical underlying) -- it cannot drift out of sample."),
    "vs_c17_c18_long_biased": (
        "C17 (long-only allocation) and C18 (long-biased timing) were judged vs "
        "buy-and-hold. This carries NO net market exposure and is judged vs random/null "
        "AND the always-on carry, never vs buy-and-hold."),
}

# --- rejection criteria (decisive, evaluated only at the replay/labels gate) -
REJECTION_CRITERIA = {
    "reject_if_not_mechanically_neutral": True,           # gate zero
    "reject_if_not_net_positive_vs_random_null": True,
    "reject_if_does_not_beat_always_on_carry_after_cost": True,
    "reject_if_not_risk_adjusted_positive": True,
    "reject_if_turnover_or_cost_drag_too_high": True,
    "reject_if_forward_oos_edge_fails": True,
    "raw_carry_alone_is_not_sufficient": True,
    "not_judged_against_buy_and_hold": True,
}

# --- the preserved C20 lesson ------------------------------------------------
C20_LESSON_PRESERVED = dict(_c21p.C20_LESSON_PRESERVED)

NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C21_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "rescues_c20", "retunes_c20", "reactivates_c20", "runs_robustness",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "connects_broker", "connects_exchange",
    "uses_real_money", "places_orders", "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "is_high_turnover",
    "trades_before_neutrality_validated", "allows_overlapping_positions",
    "adds_new_instrument_class", "uses_xauusd", "claims_profitability_before_validation",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "reproposes_rejected_family",
    "starts_c22", "advances_without_human_approval", "claims_profitability",
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
        "no_rescue_c20": True, "no_retune_c20": True, "no_robustness": True,
        "no_data_fetch": True, "no_real_data_access": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_net_market_beta": True,
        "no_estimated_cross_asset_hedge": True, "no_high_turnover": True,
        "no_trade_before_neutrality_validated": True,
        "no_overlapping_positions": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c22": True,
        "no_profitability_claim_before_validation": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_21_spec_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 (READ-ONLY, "
        "RESEARCH ONLY, PURE CANDIDATE SPEC). EXACT LOW-TURNOVER same-asset funding-carry "
        "rules (relative spot-perp basis, D1 funding, GATE-ZERO MECHANICAL neutrality, "
        "carry-regime gate, wide enter/exit hysteresis, minimum-hold persistence, hard "
        "round-trip ceiling, ~monthly rebalance cadence, durable-carry-breakdown-only "
        "exits, cost-honest replay-win criteria that must BEAT the always-on carry) on "
        "frozen public BTC/ETH/SOL spot+perp+funding D1, a FINITE FROZEN config family. "
        "Carries NO buy-and-hold beta, NO estimated cross-asset hedge; materially "
        "different from C16/C17/C18/C19 and from C20's high-turnover timing (C20 stays "
        "rejected; NOT a rescue/retune). SPEC ONLY: the next gate (detector spec + "
        "synthetic dry-run) needs an explicit human decision. NO data fetch, NO detector, "
        "NO labels, NO replay, NO optimization / rescue / tuning, NO XAUUSD, NO "
        "paper/live, does NOT start C22. Cannot be called profitable before full "
        "validation. NOT a profitability claim.")


def get_candidate_21_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def build_c21_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #21 candidate-spec record. Pure; no I/O; spec
    only. Chain-gated on the committed C21 proposal (frozen, this exact family)."""
    proposal = _c21p.build_c21_proposal(repo_root, tracked_paths)
    proposal_valid = _c21p.validate_c21_proposal(proposal)["valid"]
    proposal_verdict = proposal.get("verdict")
    proposal_family = proposal.get("candidate_family")

    blockers: list = []
    if not proposal_valid:
        blockers.append("c21_proposal_invalid")
    if proposal_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c21_proposal_not_frozen")
    if proposal_family != CANDIDATE_FAMILY:
        blockers.append("proposal_family_mismatch")

    record: dict[str, Any] = {
        "schema_version": C21S_SCHEMA_VERSION, "mode": C21S_MODE, "lane": C21S_LANE,
        "label": get_candidate_21_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C21_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C21_SPEC_BLOCKED"),
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
        "carry_regime_gate_rule": CARRY_REGIME_GATE_RULE,
        "entry_exit_hysteresis_rule": ENTRY_EXIT_HYSTERESIS_RULE,
        "hold_persistence_rule": HOLD_PERSISTENCE_RULE,
        "turnover_limit_rule": TURNOVER_LIMIT_RULE,
        "durable_breakdown_exit_rule": DURABLE_BREAKDOWN_EXIT_RULE,
        "replay_win_criteria": REPLAY_WIN_CRITERIA,
        "sub_families": list(SUB_FAMILIES),
        # identity
        "is_market_neutral": True,
        "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "is_low_turnover": True,
        "prioritizes_hold_persistence": True,
        "is_high_turnover": False,
        "carries_buy_and_hold_beta": False,
        "is_directional_timing_signal": False,
        "positions_non_overlapping": True,
        "finite_frozen_config_family": True,
        # C20 lesson preserved; NOT a rescue/retune
        "c20_lesson_preserved": dict(C20_LESSON_PRESERVED),
        "is_rescue_or_retune_of_c20": False,
        "c20_remains_rejected": True,
        # how it differs from the rejected families
        "difference_from_rejected": _deepish(DIFFERENCE_FROM_REJECTED),
        # evaluation + cost reserved
        "evaluation_metrics": _deepish(EVALUATION_METRICS),
        "cost_reserved": dict(COST_RESERVED),
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "round_trip_cost_per_trade_bps": ROUND_TRIP_COST_PER_TRADE_BPS,
        # data requirements (nothing fetched)
        "data_requirements": _deepish(DATA_REQUIREMENTS),
        "no_new_data_fetch": True,
        "no_new_instrument_class": True,
        # OOS + rejection criteria
        "oos_validation": dict(OOS_VALIDATION),
        "rejection_criteria": dict(REJECTION_CRITERIA),
        "next_human_gate_after_spec": NEXT_HUMAN_GATE_AFTER_SPEC,
        "human_review_required": True,
        "cannot_be_called_profitable_before_full_validation": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_SPEC,
        "does_not_start_c22": True,
        "c22_candidate_id": None,
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_c21_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C21 proposal for this exact family, a MARKET-NEUTRAL
    LOW-TURNOVER same-asset funding-carry strategy whose neutrality is MECHANICAL (not
    estimated) carrying no buy-and-hold beta and no estimated cross-asset hedge, NOT a
    rescue/retune of C20 (C20 stays rejected), defines all NINE exact rules (basis /
    funding / gate-zero mechanical neutrality / carry-regime gate / entry-exit
    hysteresis / hold-persistence / turnover limit / durable-breakdown exit / replay win
    criteria), uses a FINITE FROZEN config family (no optimization), declares the frozen
    BTC/ETH/SOL D1 spot+perp+funding universe (no fetch, no new instrument class),
    explains the difference from C20 + C16/C17/C18/C19, reserves the 37 bps / 74 bps
    two-leg + perp-specific replay cost, carries the market-neutral + turnover-efficient
    evaluation (vs random/null AND always-on carry, NOT buy-and-hold) + OOS + rejection
    criteria, asserts it cannot be called profitable before full validation, preserves
    the gate sequence, keeps downstream gates locked, does not start C22, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != C21S_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C21 proposal for this exact family
    if record.get("source_proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("source_proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("source_proposal_family") != CANDIDATE_FAMILY:
        failures.append("proposal_family_mismatch")

    # identity: candidate #21, market-neutral, mechanical, low-turnover, carry
    if record.get("candidate_id") != "C21":
        failures.append("candidate_id_not_c21")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing", "is_low_turnover",
              "prioritizes_hold_persistence", "positions_non_overlapping",
              "finite_frozen_config_family"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("is_high_turnover") is not False:
        failures.append("must_not_be_high_turnover")

    # NOT a rescue/retune of C20; C20 stays rejected; lesson preserved
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue_or_retune")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_must_remain_rejected")
    lp = record.get("c20_lesson_preserved") or {}
    if lp.get("carry_source_is_real") is not True:
        failures.append("must_preserve_carry_real_lesson")
    if lp.get("c20_failed_due_to_churn_cost_not_signal") is not True:
        failures.append("must_preserve_c20_churn_lesson")

    # all nine EXACT rules present and non-empty
    for rule in ("basis_calculation_rule", "funding_calculation_rule",
                 "mechanical_neutrality_gate_zero_rule", "carry_regime_gate_rule",
                 "entry_exit_hysteresis_rule", "hold_persistence_rule",
                 "turnover_limit_rule", "durable_breakdown_exit_rule",
                 "replay_win_criteria"):
        if not record.get(rule):
            failures.append("missing_rule_%s" % rule)

    # spec params: frozen finite config, low-turnover knobs, no optimization
    sp = record.get("spec_params") or {}
    if sp.get("same_asset_legs") is not True:
        failures.append("params_not_same_asset_legs")
    if sp.get("equal_notional_legs") is not True:
        failures.append("params_not_equal_notional")
    if sp.get("net_price_beta_target") != 0.0:
        failures.append("net_price_beta_target_not_zero")
    if sp.get("max_gross_exposure") != 1.0:
        failures.append("gross_exposure_not_one")
    if not (isinstance(sp.get("min_hold_bars"), int) and sp["min_hold_bars"] > 0):
        failures.append("min_hold_not_positive")
    if not (isinstance(sp.get("max_round_trips_per_year_per_asset"), int)
            and sp["max_round_trips_per_year_per_asset"] > 0):
        failures.append("round_trip_ceiling_not_positive")
    if sp.get("annualized_carry_enter_bps", 0) <= sp.get("annualized_carry_exit_bps", 0):
        failures.append("hysteresis_band_not_wide")   # enter > exit
    if sp.get("finite_frozen_config_family") is not True:
        failures.append("config_not_finite_frozen")
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

    # difference from C20 + C16/C17/C18/C19 explained
    diff = record.get("difference_from_rejected") or {}
    for k in ("vs_c20_high_turnover_timing", "vs_c16_c19_estimated_neutrality",
              "vs_c17_c18_long_biased"):
        if not diff.get(k):
            failures.append("missing_difference_%s" % k)

    # evaluation: turnover-aware, vs random/null AND always-on carry, NOT buy-and-hold
    em = record.get("evaluation_metrics") or {}
    if "net_price_beta_mechanical" not in (em.get("primary_market_neutral") or ()):
        failures.append("missing_net_price_beta_metric")
    if "round_trips_per_year" not in (em.get("turnover_efficiency") or ()):
        failures.append("missing_turnover_efficiency_metric")
    if em.get("must_beat_always_on_carry_after_cost") is not True:
        failures.append("must_beat_always_on_carry")
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        if m not in (em.get("risk_adjusted") or ()):
            failures.append("metric_missing_%s" % m)
    if "random" not in str(em.get("win_condition", "")).lower():
        failures.append("win_condition_not_vs_random_null")
    if em.get("low_turnover_is_evaluation_dimension") is not True:
        failures.append("turnover_not_evaluation_dimension")
    if em.get("judged_against_buy_and_hold") is not False:
        failures.append("must_not_be_judged_vs_buy_and_hold")
    if em.get("cannot_be_called_profitable_before_full_validation") is not True:
        failures.append("must_not_claim_profitable_early")
    ct = record.get("cost_reserved") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("round_trip_cost_per_trade_bps") != 74.0:
        failures.append("two_leg_cost_not_doubled")
    if ct.get("applied_at_replay_gate_only") is not True or ct.get(
            "applied_here") is not False:
        failures.append("cost_not_reserved_for_replay")

    # OOS required, mechanical neutrality, low-turnover OOS, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_is_mechanical_so_cannot_fail_oos") is not True:
        failures.append("neutrality_not_mechanical_oos")
    if oos.get("forward_oos_must_hold_low_turnover") is not True:
        failures.append("oos_low_turnover_claim_missing")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # rejection criteria preserved (gate-zero + must beat always-on; not vs B&H)
    rc = record.get("rejection_criteria") or {}
    for k in ("reject_if_not_mechanically_neutral",
              "reject_if_not_net_positive_vs_random_null",
              "reject_if_does_not_beat_always_on_carry_after_cost",
              "reject_if_turnover_or_cost_drag_too_high",
              "reject_if_forward_oos_edge_fails", "raw_carry_alone_is_not_sufficient",
              "not_judged_against_buy_and_hold"):
        if rc.get(k) is not True:
            failures.append("rejection_criterion_off_%s" % k)

    # cannot be called profitable before full validation
    if record.get("cannot_be_called_profitable_before_full_validation") is not True:
        failures.append("must_not_claim_profitable_before_validation")

    # gate sequence + downstream locks + no C22
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    if record.get("does_not_start_c22") is not True:
        failures.append("must_not_start_c22")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                "no_data_fetch", "no_new_instrument_class", "no_xauusd", "no_commit",
                "no_push", "no_broker", "no_order_logic", "no_net_market_beta",
                "no_estimated_cross_asset_hedge", "no_high_turnover",
                "no_trade_before_neutrality_validated", "no_overlapping_positions",
                "no_paper_trading", "no_live_trading", "no_gate_skip", "no_start_c22"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
