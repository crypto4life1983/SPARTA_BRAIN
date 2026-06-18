"""Candidate #16 -- cointegration_pairs_market_neutral_v1 -- CANDIDATE SPEC
(PURE, RESEARCH ONLY).

Advances the C16 family proposal (market-neutral cointegration pairs) into a pure
candidate SPEC. It DECLARES the deterministic pair universe, the cointegration /
spread logic, entry/exit rules, long/short leg handling, stop/risk rules, the
two-leg fee/slippage assumptions, the baselines suitable for a MARKET-NEUTRAL
strategy, the FORBIDDEN directional-carry / buy-and-hold shortcut, and the next
gate. It is chain-gated on the frozen C16 proposal (re-validated; selected family
must be statistical_arbitrage_pairs; candidate not in the C1-C15 rejected ledger
and not reusing C15).

It does NOTHING else: NO detector, NO labels, NO replay/backtest, NO optimization,
NO data fetch, NO writes, NO stage/commit/push, and NO paper/live/broker/order
surface. Every capability flag is pinned False with a full scope_locks set. The
next gate (detector spec + synthetic dry-run) needs an explicit human decision.

The whole point is to avoid the carry trap that rejected C14 and C15: this is a
DOLLAR/BETA-NEUTRAL cointegrated spread. The decisive gates therefore FORBID any
reliance on net directional exposure or buy-and-hold leg drift, and require a
near-zero net beta -- there is no buy-and-hold beta to lose to.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.cointegration_pairs_market_neutral_v1_proposal_contract as _c16p  # noqa: E501
import sparta_commander.gate_decision_coordinator_v1_contract as _gdc
import sparta_commander.research_expansion_plan_v1_contract as _rep

S16_SCHEMA_VERSION = 1
S16_MODE = "RESEARCH_ONLY"
S16_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c16p.CANDIDATE_ID
CANDIDATE_FAMILY = _c16p.CANDIDATE_FAMILY
CANDIDATE_NAME = _c16p.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C15 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C15)

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- deterministic, pre-registered pair universe ----------------------------
LEG_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"
PAIR_UNIVERSE = (
    {"pair": "ETHBTC", "numerator": "ETHUSD", "denominator": "BTCUSD"},
    {"pair": "SOLETH", "numerator": "SOLUSD", "denominator": "ETHUSD"},
    {"pair": "SOLBTC", "numerator": "SOLUSD", "denominator": "BTCUSD"},
)
PAIR_UNIVERSE_IS_DETERMINISTIC = True

# --- declared (NOT fitted) spec parameters ----------------------------------
SPEC_PARAMS = {
    "spread_definition": "log(numerator) - hedge_ratio * log(denominator)",
    "hedge_ratio_method": "rolling_ols_log_price",
    "cointegration_window_days": 180,        # rolling estimation/validity window
    "cointegration_pvalue_max": 0.05,        # spread must be cointegrated to trade
    "zscore_lookback_days": 60,
    "entry_z": 2.0,                          # |z| >= entry_z -> enter (fade)
    "exit_z": 0.5,                           # |z| <= exit_z -> take (revert to mean)
    "stop_z": 3.5,                           # |z| >= stop_z -> z-band stop
    "rebalance": "daily_on_close",
    "dollar_neutral": True,
    "beta_neutral": True,
    "fixed_horizon": None,                   # signal-driven (z) exits, not horizon
    "one_edit_allowance_used": False,
}

# --- cointegration / spread logic (declared) --------------------------------
COINTEGRATION_LOGIC = (
    "For each pre-registered pair, estimate a rolling hedge ratio by OLS of "
    "log(numerator) on log(denominator) over cointegration_window_days, form the "
    "spread residual, and compute its rolling z-score. A pair is TRADEABLE only "
    "while its rolling cointegration test p-value <= cointegration_pvalue_max; a "
    "pair that loses cointegration is not entered (and open positions are "
    "invalidation-exited).")
ENTRY_LOGIC = (
    "Enter when |spread z-score| >= entry_z AND the pair is currently cointegrated: "
    "go LONG the cheap leg and SHORT the rich leg (fade the spread), dollar- and "
    "beta-neutral. No directional/outright entries.")
EXIT_LOGIC = (
    "Take when |z| <= exit_z (spread reverts toward its mean); z-band STOP when "
    "|z| >= stop_z (spread keeps widening); cointegration-break invalidation exit "
    "if the rolling p-value degrades above cointegration_pvalue_max. Signal-driven, "
    "not fixed-horizon.")
LONG_SHORT_LEG_HANDLING = (
    "each trade holds TWO legs sized to be dollar-neutral (equal notional) and "
    "beta-neutral via the hedge ratio: long the relatively cheap leg, short the "
    "relatively rich leg; net market exposure ~ 0 by construction.")
STOP_RISK_LOGIC = (
    "z-band stop at stop_z, cointegration-break invalidation exit, per-pair risk "
    "cap, spread vol-stop, and a portfolio cap across the 3 pairs; no leg is ever "
    "carried as a naked directional position.")

# --- fee / slippage (TWO legs; reserved for replay) -------------------------
FEE_PER_LEG_ROUND_TRIP_BPS = 27.0
SLIPPAGE_PER_LEG_ROUND_TRIP_BPS = 10.0
ALL_IN_PER_LEG_ROUND_TRIP_BPS = (
    FEE_PER_LEG_ROUND_TRIP_BPS + SLIPPAGE_PER_LEG_ROUND_TRIP_BPS)        # 37.0
LEGS_PER_PAIR_TRADE = 2
ALL_IN_PAIR_ROUND_TRIP_BPS = ALL_IN_PER_LEG_ROUND_TRIP_BPS * LEGS_PER_PAIR_TRADE  # 74.0

# --- baselines suitable for a MARKET-NEUTRAL strategy ------------------------
# Buy-and-hold is NOT the comparator (a dollar-neutral spread has no directional
# beta); instead we require a random-entry null AND a zero-edge spread null, and
# we explicitly FORBID a directional-carry / buy-and-hold shortcut.
BASELINES_REQUIRED = {
    "random_entry": {"required": True,
                     "rule": "deterministic fixed-seed random-entry resamples "
                             "(>=200): random tradeable-pair + random z-timed "
                             "entry/side, net of the two-leg 74 bps"},
    "zero_edge_spread_null": {"required": True,
                              "rule": "random-sign spread positions held the same "
                                      "way -> confirms the z-timing adds value "
                                      "beyond just being in the spread"},
    "buy_and_hold": {"is_comparator": False,
                     "reason": "market-neutral: no directional buy-and-hold beta "
                               "to compare against; using it would reintroduce the "
                               "carry shortcut"},
}
FORWARD_OOS = {"required": True, "window": "2026_unseen_continuation",
               "must_be_net_positive": True}

# --- the FORBIDDEN directional-carry / buy-and-hold shortcut -----------------
FORBIDDEN_CARRY_SHORTCUT = {
    "net_directional_exposure_must_be_near_zero": True,
    "must_not_rely_on_long_leg_drift": True,
    "must_not_rely_on_buy_and_hold_carry": True,
    "max_abs_net_beta": 0.10,                 # near-zero net beta required
    "rationale": ("the edge must come from mean-reversion of a cointegrated "
                  "residual, NOT from net long exposure or leg drift -- this is the "
                  "exact carry trap that rejected C14 and C15"),
}

DECISIVE_REPLAY_GATES = {
    "must_beat_random_entry": True,
    "must_beat_zero_edge_spread_null": True,
    "must_be_net_positive_after_two_leg_cost": True,
    "forward_oos_must_be_net_positive": True,
    "no_single_pair_dependence": True,
    "market_neutral_net_beta_near_zero": True,
    "no_directional_carry_shortcut": True,
    "cointegration_validity_required": True,
    "structural_sample_size_gate": {          # C13 lesson, before replay
        "min_labels_total": 100, "min_labels_per_pair": 20,
        "min_labels_per_regime": 20, "forward_oos_must_be_populated": True},
    "horizon_exit_cap_applicable": False,     # z-driven exits, not fixed-horizon
}

# --- evaluation windows -----------------------------------------------------
EVALUATION_WINDOWS = {
    "durability_window_days": 1095,           # 3-year durability
    "recent_relevance_window_days_min": 90,   # recent 3-month relevance
    "recent_relevance_window_days_max": 180,  # recent 6-month relevance
    "forward_oos_required": True,
    "regime_specific_tagging_required": True,
    "regimes": ("bull", "bear", "chop"),
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "optimizes_parameters",
    "runs_robustness", "runs_portfolio_compute", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "uses_one_edit_allowance", "reproposes_rejected_family",
    "relies_on_directional_carry", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_optimization": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_one_edit_invocation": True,
        "no_rejected_family_repropose": True, "no_reuse_of_c15": True,
        "no_directional_carry_shortcut": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_16_spec_label() -> str:
    return (
        "Candidate #16 cointegration_pairs_market_neutral_v1 spec (READ-ONLY, "
        "RESEARCH ONLY, PURE). Dollar/beta-neutral cointegration pairs on crypto-D1 "
        "ratio spreads: rolling-OLS hedge ratio, z-score fade with cointegration-"
        "validity gating, two-leg 74 bps cost reserved for replay. Baselines are "
        "random-entry + zero-edge spread null (NOT buy-and-hold); the directional-"
        "carry / buy-and-hold shortcut is FORBIDDEN. SPEC ONLY: the detector gate "
        "needs an explicit human decision. NO detector, NO labels, NO replay, NO "
        "optimization, NO paper/live. NOT a profitability claim.")


def get_candidate_16_spec_next_action() -> str:
    return "HUMAN_DECISION_C16_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def build_c16_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #16 spec record. Pure; no I/O; spec only.
    Chain-gated on the frozen C16 family proposal."""
    proposal = _c16p.build_c16_family_proposal(repo_root, tracked_paths)
    proposal_valid = _c16p.validate_c16_family_proposal(proposal)["valid"]

    blockers: list = []
    if not proposal_valid:
        blockers.append("c16_proposal_invalid")
    if proposal.get("verdict") != "C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c16_proposal_not_frozen")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C15:
        blockers.append("candidate_family_in_rejected_ledger")
    if CANDIDATE_FAMILY == "slow_vol_targeted_time_series_momentum":
        blockers.append("must_not_reuse_c15")

    record: dict[str, Any] = {
        "schema_version": S16_SCHEMA_VERSION, "mode": S16_MODE, "lane": S16_LANE,
        "label": get_candidate_16_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C16_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C16_SPEC_BLOCKED"),
        # chain provenance
        "proposal_verdict": proposal.get("verdict"),
        "proposal_valid": proposal_valid,
        "selected_tournament_family": proposal.get("tournament_family_key"),
        # the spec
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "leg_symbols": list(LEG_SYMBOLS), "timeframe": TIMEFRAME,
        "pair_universe": [dict(p) for p in PAIR_UNIVERSE],
        "pair_universe_is_deterministic": PAIR_UNIVERSE_IS_DETERMINISTIC,
        "spec_params": dict(SPEC_PARAMS),
        "cointegration_logic": COINTEGRATION_LOGIC,
        "entry_logic": ENTRY_LOGIC, "exit_logic": EXIT_LOGIC,
        "long_short_leg_handling": LONG_SHORT_LEG_HANDLING,
        "stop_risk_logic": STOP_RISK_LOGIC,
        "fee_per_leg_round_trip_bps": FEE_PER_LEG_ROUND_TRIP_BPS,
        "slippage_per_leg_round_trip_bps": SLIPPAGE_PER_LEG_ROUND_TRIP_BPS,
        "all_in_per_leg_round_trip_bps": ALL_IN_PER_LEG_ROUND_TRIP_BPS,
        "legs_per_pair_trade": LEGS_PER_PAIR_TRADE,
        "all_in_pair_round_trip_bps": ALL_IN_PAIR_ROUND_TRIP_BPS,
        "baselines_required": {k: dict(v) for k, v in BASELINES_REQUIRED.items()},
        "forward_oos": dict(FORWARD_OOS),
        "forbidden_carry_shortcut": dict(FORBIDDEN_CARRY_SHORTCUT),
        "decisive_replay_gates": _deepish(DECISIVE_REPLAY_GATES),
        "evaluation_windows": dict(EVALUATION_WINDOWS),
        "is_market_neutral": True, "is_directional": False,
        "is_dollar_neutral": True, "is_beta_neutral": True,
        "is_fixed_horizon": False,
        "uses_cointegration_validity_gate": True,
        # anti-loop
        "rejected_families_c1_to_c15": list(REJECTED_FAMILIES_C1_TO_C15),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C15),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C15,
        "does_not_reuse_c15":
            CANDIDATE_FAMILY != "slow_vol_targeted_time_series_momentum",
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": get_candidate_16_spec_next_action(),
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def decision_ready_report(record: dict | None = None) -> dict[str, Any]:
    """ONE decision-ready report using the Gate Decision Coordinator v1 logic: it
    frames the freshly-built C16 spec as an open candidate gate and returns the
    coordinator's single recommended next safe HUMAN command. Pure; executes
    nothing; reduces manual back-and-forth."""
    rec = record if record is not None else build_c16_spec()
    state = {
        "repo": {"clean": True, "ahead": 0, "behind": 0,
                 "uncommitted_changes": False},
        "ledger": {"canonical_count": 20, "expected_count": 20, "reconciles": True},
        "candidates": {
            "C15": {"family": "slow_vol_targeted_time_series_momentum",
                    "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                    "next_action": "NONE__C15_CLOSED", "shipped": True},
            CANDIDATE_ID: {"family": CANDIDATE_FAMILY, "active": True,
                           "next_action": rec.get("next_required_action")},
        },
    }
    decision = _gdc.coordinate(state)
    report = _gdc.summarize_for_morning_report(decision)
    report["candidate_id"] = CANDIDATE_ID
    report["spec_verdict"] = rec.get("verdict")
    report["next_gate"] = rec.get("next_required_action")
    report["uses_gate_decision_coordinator_v1"] = True
    report["executes_nothing"] = True
    return report


def validate_c16_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the frozen C16 proposal, declares the deterministic pair
    universe + cointegration/entry/exit/leg/stop logic, the two-leg 74 bps cost,
    market-neutral baselines (NOT buy-and-hold) + the FORBIDDEN carry shortcut, is
    dollar/beta-neutral and not in the C1-C15 ledger / not reusing C15, keeps
    downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != S16_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C16_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("proposal_verdict") != "C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("proposal_not_frozen")
    if record.get("selected_tournament_family") != "statistical_arbitrage_pairs":
        failures.append("selected_family_not_stat_arb")

    # deterministic pair universe + logic present
    if record.get("pair_universe_is_deterministic") is not True:
        failures.append("pair_universe_not_deterministic")
    if len(record.get("pair_universe") or []) != 3:
        failures.append("pair_universe_size_unexpected")
    for field in ("cointegration_logic", "entry_logic", "exit_logic",
                  "long_short_leg_handling", "stop_risk_logic", "spec_params"):
        if not record.get(field):
            failures.append("spec_missing_%s" % field)
    if record.get("uses_cointegration_validity_gate") is not True:
        failures.append("cointegration_validity_gate_off")

    # market-neutral identity
    for k in ("is_market_neutral", "is_dollar_neutral", "is_beta_neutral"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_directional") is not False:
        failures.append("must_not_be_directional")
    if record.get("is_fixed_horizon") is not False:
        failures.append("must_not_be_fixed_horizon")

    # two-leg cost (74 bps), not droppable
    if record.get("all_in_per_leg_round_trip_bps") != 37.0:
        failures.append("per_leg_cost_tampered")
    if record.get("legs_per_pair_trade") != 2:
        failures.append("legs_per_pair_tampered")
    if record.get("all_in_pair_round_trip_bps") != 74.0:
        failures.append("pair_cost_tampered")

    # baselines: random + zero-edge null required; buy-and-hold NOT a comparator
    br = record.get("baselines_required") or {}
    if (br.get("random_entry") or {}).get("required") is not True:
        failures.append("random_entry_baseline_not_required")
    if (br.get("zero_edge_spread_null") or {}).get("required") is not True:
        failures.append("zero_edge_null_not_required")
    if (br.get("buy_and_hold") or {}).get("is_comparator") is not False:
        failures.append("buy_and_hold_must_not_be_comparator")

    # forbidden carry shortcut (the C14/C15 trap)
    fc = record.get("forbidden_carry_shortcut") or {}
    for k in ("net_directional_exposure_must_be_near_zero",
              "must_not_rely_on_long_leg_drift",
              "must_not_rely_on_buy_and_hold_carry"):
        if fc.get(k) is not True:
            failures.append("carry_shortcut_not_forbidden_%s" % k)
    dg = record.get("decisive_replay_gates") or {}
    for k in ("must_beat_random_entry", "must_beat_zero_edge_spread_null",
              "must_be_net_positive_after_two_leg_cost",
              "forward_oos_must_be_net_positive", "no_single_pair_dependence",
              "market_neutral_net_beta_near_zero", "no_directional_carry_shortcut",
              "cointegration_validity_required"):
        if dg.get(k) is not True:
            failures.append("decisive_gate_off_%s" % k)
    if (record.get("forward_oos") or {}).get("required") is not True:
        failures.append("forward_oos_not_required")

    # both windows
    w = record.get("evaluation_windows") or {}
    if w.get("durability_window_days") != 1095:
        failures.append("durability_window_not_3yr")
    for k in ("recent_relevance_window_days_min", "recent_relevance_window_days_max"):
        if not w.get(k):
            failures.append("recent_relevance_window_missing_%s" % k)

    # anti-loop
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("does_not_reuse_c15") is not True:
        failures.append("reuses_c15")
    if record.get("rejected_families_count") != 20:
        failures.append("ledger_not_20")

    # gate sequence + downstream locks
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay",
                "no_optimization", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_reuse_of_c15", "no_directional_carry_shortcut"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
