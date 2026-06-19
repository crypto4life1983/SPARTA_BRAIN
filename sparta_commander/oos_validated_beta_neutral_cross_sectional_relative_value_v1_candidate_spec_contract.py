"""Candidate #19 -- oos_validated_beta_neutral_cross_sectional_relative_value_v1
-- CANDIDATE SPEC (PURE, RESEARCH ONLY).

The human-approved (HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC) formal candidate
specification for the frozen C19 family proposal: a continuous dollar- AND
return-beta-neutral cross-sectional relative-value residual among BTC/ETH/SOL built
in RETURN space, with OOS neutrality validation as GATE ZERO before any trading
logic. This is a pure, in-memory specification: it DECLARES the EXACT rules (residual
calculation / the gate-zero OOS neutrality validation / entry / exit / stop &
invalidation / turnover constraints / non-overlap / replay win criteria), the cached
BTC/ETH/SOL D1 universe and data limitations, the market-neutral evaluation, the
reserved fee-honest replay cost, the out-of-sample requirement, the rejection
criteria, and the next human gate. It is chain-gated on the committed C19 proposal.

It builds NO detector, NO labels, NO replay; runs NO PnL / optimization / rescue /
tuning / data fetch; touches NO paper/live/broker/order surface; and does NOT start
C20. Every capability flag is pinned False with a full scope_locks set. The next gate
(detector spec + synthetic dry-run) still requires an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_proposal_contract as _c19p  # noqa: E501

C19S_SCHEMA_VERSION = 1
C19S_MODE = "RESEARCH_ONLY"
C19S_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c19p.CANDIDATE_ID
CANDIDATE_FAMILY = _c19p.CANDIDATE_FAMILY
CANDIDATE_NAME = _c19p.CANDIDATE_NAME

EXPECTED_PROPOSAL_VERDICT = "C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + timeframe + data limitations --------------------------------
UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"
DATA_SOURCE = "cached BTC/ETH/SOL D1 spot OHLCV (the C16/C17 cache) -- already local"

# --- declared (NOT fitted) construction parameters --------------------------
# A pre-registered starting specification, not optimized values. No parameter search
# is performed or permitted at this gate.
SPEC_PARAMS = {
    "return_space": True,                  # work in log/percent returns, NOT price levels
    "beta_estimation_window_bars": 90,     # IS window for return-beta hedge ratios (D1)
    "oos_neutrality_window_bars": 60,      # unseen OOS window to validate neutrality
    "net_residual_beta_tolerance": 0.10,   # |net residual beta| must be <= this OOS
    "residual_zscore_window_bars": 60,     # rolling window for residual mean/std (z-score)
    "entry_zscore_threshold": 2.0,         # enter when |residual z| >= this
    "exit_zscore_threshold": 0.25,         # exit when |residual z| reverts <= this
    "stop_zscore_threshold": 4.0,          # invalidation when |residual z| diverges >= this
    "max_gross_exposure": 1.0,             # no leverage; sum of |leg weights| <= 1.0
    "min_bars_between_rebalances": 5,      # turnover floor / low-frequency (D1 bars)
    "dollar_neutral": True,                # sum of signed dollar legs == 0
    "beta_neutral": True,                  # net return-beta of the combination ~ 0
    "no_parameter_optimization": True,
    "no_parameter_tuning": True,
    "no_rescue_variant": True,
}

# --- 1. EXACT residual calculation rule -------------------------------------
RESIDUAL_CALCULATION_RULE = (
    "Work in RETURN space (daily log returns), never price levels. For each asset, "
    "estimate -- over beta_estimation_window_bars -- the return-beta hedge ratios "
    "that make a long-short combination of the BTC/ETH/SOL returns carry ZERO net "
    "return-beta to the basket (a dollar-neutral, beta-neutral residual). The traded "
    "signal is that NEUTRAL RESIDUAL return series; it is standardized to a rolling "
    "z-score over residual_zscore_window_bars. No price-level cointegration, no "
    "level-OLS hedge ratio (that is the C16 failure mode being explicitly avoided).")

# --- 2. EXACT gate-zero OOS neutrality validation rule ----------------------
OOS_NEUTRALITY_GATE_ZERO_RULE = (
    "GATE ZERO, before ANY trading logic is defined or evaluated: take the hedge "
    "ratios estimated in-sample and measure the residual's NET RETURN-BETA on the "
    "UNSEEN oos_neutrality_window_bars. The construction PASSES only if "
    "|net residual beta| <= net_residual_beta_tolerance out-of-sample. If it FAILS, "
    "the candidate is rejected at the labels/neutrality gate BEFORE replay -- no "
    "trading rules are applied to a residual that is not actually neutral out of "
    "sample. Neutrality is re-checked on a rolling basis through the test window.")

# --- 3. EXACT entry rule ----------------------------------------------------
ENTRY_RULE = (
    "Trade ONLY the validated-neutral residual. ENTER when the residual z-score "
    "reaches an extreme: |residual z| >= entry_zscore_threshold. Direction is "
    "mean-reverting -- if the residual is rich (z >= +threshold) SHORT the residual "
    "(short the relatively over-performing leg, long the under-performing leg, "
    "dollar- and beta-neutral); if the residual is cheap (z <= -threshold) take the "
    "mirror. Position weights keep sum-of-signed-dollars == 0 and net return-beta ~ 0 "
    "and gross <= max_gross_exposure. Entries are spaced by >= min_bars_between_"
    "rebalances bars (turnover floor).")

# --- 4. EXACT exit rule -----------------------------------------------------
EXIT_RULE = (
    "Exit when the neutral residual reverts toward its mean: |residual z| <= "
    "exit_zscore_threshold (the reversion has played out). No fixed time/horizon "
    "exit; the exit is defined purely on the neutral residual reverting. On exit the "
    "dollar-neutral, beta-neutral combination is fully unwound.")

# --- 5. EXACT stop / invalidation rule --------------------------------------
STOP_INVALIDATION_RULE = (
    "Two structural invalidations, no discretionary averaging: (a) RESIDUAL "
    "DIVERGENCE STOP -- if |residual z| >= stop_zscore_threshold the mean-reversion "
    "thesis is invalidated and the position is closed (the relationship has broken, "
    "not a reason to add); (b) NEUTRALITY-BREAK INVALIDATION -- if the rolling OOS "
    "net residual beta leaves the tolerance band (the residual is no longer neutral), "
    "stand down / close: the edge precondition no longer holds. Neither is a "
    "drawdown-percent threshold.")

# --- 6. EXACT turnover constraint rule --------------------------------------
TURNOVER_CONSTRAINT_RULE = (
    "Low turnover is a REQUIREMENT, not a free parameter: re-balance / re-enter no "
    "more often than every min_bars_between_rebalances bars, hold gross <= "
    "max_gross_exposure (no leverage), and prefer holding a live neutral position to "
    "churning it. Because each leg pays the 37 bps round-trip and the position has "
    "two legs, turnover is the dominant cost risk and is bounded by construction.")

# --- 7. EXACT non-overlap rule ----------------------------------------------
NON_OVERLAP_RULE = (
    "At most ONE live neutral relative-value position at a time (one residual "
    "construction). A new entry cannot open while a position is live; there are no "
    "overlapping duplicate residual exposures and no stacking of the same residual. "
    "One trade lifecycle = entry -> reversion/stop exit, non-overlapping.")

# --- sub-approaches declared in the proposal (variants to compare later) ----
SUB_APPROACHES = tuple(s["key"] for s in _c19p.SUB_APPROACHES)

# --- evaluation metrics (market-neutral; judged vs random / null) -----------
EVALUATION_METRICS = {
    "primary_market_neutral": ("net_residual_beta", "net_positive_vs_random",
                               "net_positive_vs_null"),
    "risk_adjusted": ("sharpe_ratio", "calmar_ratio", "max_drawdown"),
    "diagnostics": ("net_return", "profit_factor", "win_rate", "avg_R_per_trade",
                    "turnover_low", "long_short_dollar_neutrality"),
    "baseline": ("random-entry null and a zero-edge null on the SAME neutral "
                 "residual, net of cost -- NOT buy-and-hold (there is no net market "
                 "exposure to compare against)"),
    "win_condition": ("a NET-POSITIVE market-neutral residual edge vs random / null "
                      "on a RISK-ADJUSTED basis AND surviving forward-OOS, with "
                      "OOS-validated neutrality as a precondition -- not raw return"),
    "neutrality_is_precondition": True,
    "judged_against_buy_and_hold": False,   # explicitly NOT vs holding BTC
}

# --- cost (reserved for the replay gate) ------------------------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
COST_RESERVED = {
    "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
    "two_legs_so_cost_counts_double_per_rebalance": True,
    "applied_at_replay_gate_only": True,
    "applied_here": False,
}

# --- data requirements (cached BTC/ETH/SOL D1 only; nothing fetched) --------
DATA_REQUIREMENTS = {
    "btc_eth_sol_d1_spot": {"required": True, "available_locally": True,
                            "note": "existing cached C16/C17 BTC/ETH/SOL D1 spot "
                                    "OHLCV -- already present, no fetch"},
    "no_data_fetched_here": True,
    "no_new_data_fetch_required": True,
    "no_xauusd_or_new_instrument_class": True,
}

# --- out-of-sample validation -----------------------------------------------
OOS_VALIDATION = {
    "forward_oos_required": True,
    "forward_oos_window": "2026_unseen_continuation",
    "forward_oos_must_hold_market_neutral_edge": True,
    "neutrality_validated_oos_first": True,
    "no_parameter_optimization": True,
    "no_in_sample_only_fit": True,
}

# --- how it differs from the relevant rejected families ---------------------
DIFFERENCE_FROM_REJECTED = {
    "vs_c16_level_ols_hedge": (
        "C16 estimated a hedge ratio on PRICE LEVELS via OLS and ASSUMED neutrality; "
        "it failed OOS (net beta 2.82) with too few cointegration windows (43). This "
        "spec works in RETURN space, treats OOS neutrality as GATE ZERO with an "
        "explicit |net residual beta| <= 0.10 tolerance, and is continuous (no rare "
        "cointegration windows)."),
    "vs_c17_long_only_allocation": (
        "C17 was a LONG-ONLY vol-targeted / risk-parity allocation judged vs "
        "buy-and-hold; it cut drawdown but lost risk-adjusted. This is DOLLAR- and "
        "BETA-NEUTRAL with no net market exposure, judged vs random / null."),
    "vs_c18_long_biased_timing": (
        "C18 was a long-biased H4 directional timing approximation that could not "
        "beat BTC buy-and-hold risk-adjusted. This carries NO buy-and-hold beta -- "
        "there is nothing to lose to -- and is a D1 relative-value mechanism, not a "
        "timing signal."),
}

# --- rejection criteria (decisive, evaluated only at the replay/labels gate) -
REJECTION_CRITERIA = {
    "reject_if_oos_neutrality_fails": True,             # gate zero
    "reject_if_not_net_positive_vs_random_null": True,
    "reject_if_not_risk_adjusted_positive": True,
    "reject_if_forward_oos_edge_fails": True,
    "reject_if_turnover_too_high_cost_dominates": True,
    "raw_return_alone_is_not_sufficient": True,
    "not_judged_against_buy_and_hold": True,
}

NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C19_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "reparameterizes", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "carries_net_market_beta",
    "trades_before_neutrality_validated", "uses_price_level_hedge",
    "allows_overlapping_positions", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "reproposes_rejected_family", "starts_c20",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
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
        "no_trade_before_neutrality_validated": True, "no_price_level_hedge": True,
        "no_overlapping_positions": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_rejected_family_repropose": True, "no_start_c20": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_19_spec_label() -> str:
    return (
        "Candidate #19 oos_validated_beta_neutral_cross_sectional_relative_value_v1 "
        "(READ-ONLY, RESEARCH ONLY, PURE CANDIDATE SPEC). EXACT market-neutral "
        "relative-value rules (return-space residual, GATE-ZERO OOS neutrality "
        "validation, z-score reversion entry, mean-reversion exit, residual-divergence "
        "& neutrality-break invalidation, low-turnover constraint, one-position "
        "non-overlap) on cached BTC/ETH/SOL D1 -- carrying NO buy-and-hold beta and "
        "materially different from C16 / C17 / C18. SPEC ONLY: the next gate (detector "
        "spec + synthetic dry-run) needs an explicit human decision. NO data fetch, NO "
        "detector, NO labels, NO replay, NO optimization / rescue / tuning, NO XAUUSD, "
        "NO paper/live, does NOT start C20. NOT a profitability claim.")


def get_candidate_19_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def build_c19_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #19 candidate-spec record. Pure; no I/O; spec
    only. Chain-gated on the committed C19 proposal (frozen, this exact family)."""
    proposal = _c19p.build_c19_proposal(repo_root, tracked_paths)
    proposal_valid = _c19p.validate_c19_proposal(proposal)["valid"]
    proposal_verdict = proposal.get("verdict")
    proposal_family = proposal.get("candidate_family")

    blockers: list = []
    if not proposal_valid:
        blockers.append("c19_proposal_invalid")
    if proposal_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c19_proposal_not_frozen")
    if proposal_family != CANDIDATE_FAMILY:
        blockers.append("proposal_family_mismatch")

    record: dict[str, Any] = {
        "schema_version": C19S_SCHEMA_VERSION, "mode": C19S_MODE, "lane": C19S_LANE,
        "label": get_candidate_19_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C19_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C19_SPEC_BLOCKED"),
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
        "residual_calculation_rule": RESIDUAL_CALCULATION_RULE,
        "oos_neutrality_gate_zero_rule": OOS_NEUTRALITY_GATE_ZERO_RULE,
        "entry_rule": ENTRY_RULE,
        "exit_rule": EXIT_RULE,
        "stop_invalidation_rule": STOP_INVALIDATION_RULE,
        "turnover_constraint_rule": TURNOVER_CONSTRAINT_RULE,
        "non_overlap_rule": NON_OVERLAP_RULE,
        "sub_approaches": list(SUB_APPROACHES),
        # identity
        "is_market_neutral": True,
        "is_return_space": True,
        "is_dollar_neutral": True,
        "is_beta_neutral": True,
        "oos_neutrality_validation_is_gate_zero": True,
        "carries_buy_and_hold_beta": False,
        "uses_price_level_hedge": False,
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
        "does_not_start_c20": True,
        "c20_candidate_id": None,
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_c19_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C19 proposal for this exact family, a
    MARKET-NEUTRAL return-space relative-value strategy carrying no buy-and-hold beta
    and not using a price-level hedge, defines all SEVEN exact rules (residual /
    gate-zero OOS neutrality / entry / exit / stop & invalidation / turnover /
    non-overlap), declares the cached BTC/ETH/SOL D1 universe (no fetch, no new
    instrument class), explains the difference from C16 / C17 / C18, reserves the 37
    bps replay cost, carries the market-neutral evaluation + OOS + rejection criteria,
    preserves the gate sequence, keeps downstream gates locked, does not start C20,
    and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C19S_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C19_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C19 proposal for this exact family
    if record.get("source_proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("source_proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("source_proposal_family") != CANDIDATE_FAMILY:
        failures.append("proposal_family_mismatch")

    # identity: candidate #19, market-neutral, return-space, gate-zero neutrality
    if record.get("candidate_id") != "C19":
        failures.append("candidate_id_not_c19")
    if record.get("candidate_family") != CANDIDATE_FAMILY:
        failures.append("family_mismatch")
    for k in ("is_market_neutral", "is_return_space", "is_dollar_neutral",
              "is_beta_neutral", "oos_neutrality_validation_is_gate_zero",
              "positions_non_overlapping", "low_turnover_required"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("carries_buy_and_hold_beta") is not False:
        failures.append("must_not_carry_buy_and_hold_beta")
    if record.get("uses_price_level_hedge") is not False:
        failures.append("must_not_use_price_level_hedge")

    # all seven EXACT rules present and non-empty
    for rule in ("residual_calculation_rule", "oos_neutrality_gate_zero_rule",
                 "entry_rule", "exit_rule", "stop_invalidation_rule",
                 "turnover_constraint_rule", "non_overlap_rule"):
        if not record.get(rule):
            failures.append("missing_rule_%s" % rule)

    # spec params declared, not optimized/tuned/rescued
    sp = record.get("spec_params") or {}
    if sp.get("return_space") is not True:
        failures.append("params_not_return_space")
    if sp.get("dollar_neutral") is not True or sp.get("beta_neutral") is not True:
        failures.append("params_not_neutral")
    if sp.get("net_residual_beta_tolerance") != 0.10:
        failures.append("neutrality_tolerance_tampered")
    if sp.get("max_gross_exposure") != 1.0:
        failures.append("gross_exposure_not_one")
    for k in ("no_parameter_optimization", "no_parameter_tuning",
              "no_rescue_variant"):
        if sp.get(k) is not True:
            failures.append("params_allow_%s" % k)

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

    # difference from C16 / C17 / C18 explained
    diff = record.get("difference_from_rejected") or {}
    for k in ("vs_c16_level_ols_hedge", "vs_c17_long_only_allocation",
              "vs_c18_long_biased_timing"):
        if not diff.get(k):
            failures.append("missing_difference_%s" % k)

    # evaluation: market-neutral vs random/null, NOT vs buy-and-hold; cost reserved
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
    if em.get("judged_against_buy_and_hold") is not False:
        failures.append("must_not_be_judged_vs_buy_and_hold")
    ct = record.get("cost_reserved") or {}
    if ct.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if ct.get("applied_at_replay_gate_only") is not True or ct.get(
            "applied_here") is not False:
        failures.append("cost_not_reserved_for_replay")

    # OOS required, neutrality validated first, no optimization
    oos = record.get("oos_validation") or {}
    if oos.get("forward_oos_required") is not True:
        failures.append("forward_oos_not_required")
    if oos.get("neutrality_validated_oos_first") is not True:
        failures.append("neutrality_not_validated_first")
    if oos.get("no_parameter_optimization") is not True:
        failures.append("optimization_not_forbidden")

    # rejection criteria preserved (gate-zero + market-neutral, not vs buy-and-hold)
    rc = record.get("rejection_criteria") or {}
    for k in ("reject_if_oos_neutrality_fails",
              "reject_if_not_net_positive_vs_random_null",
              "reject_if_forward_oos_edge_fails", "raw_return_alone_is_not_sufficient",
              "not_judged_against_buy_and_hold"):
        if rc.get(k) is not True:
            failures.append("rejection_criterion_off_%s" % k)

    # gate sequence + downstream locks + no C20
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    if record.get("does_not_start_c20") is not True:
        failures.append("must_not_start_c20")
    if record.get("c20_candidate_id") is not None:
        failures.append("c20_must_be_none")
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                "no_new_instrument_class", "no_xauusd", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_net_market_beta",
                "no_trade_before_neutrality_validated", "no_price_level_hedge",
                "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_start_c20"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
