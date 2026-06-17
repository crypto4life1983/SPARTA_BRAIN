"""Candidate #15 -- slow_vol_targeted_time_series_momentum_v1 -- FAMILY SPEC
(PURE, RESEARCH ONLY).

The Strategy Family Tournament v1 winner (trend following / slow vol-targeted
time-series momentum) advanced into a Candidate #15 FAMILY SPEC. This is a pure,
in-memory specification: it DECLARES the candidate's logic (symbols / timeframes /
entry / exit / risk / costs / regime tags / baselines / forward-OOS / durability +
recent-relevance windows) and WHY it is materially different from the rejected
C1-C14 variants.

It is chain-gated on the pushed tournament proposal (it imports it, re-validates
it, and requires the winner to be trend_following). It does NOTHING else: it does
NOT fetch data, NOT run a detector, NOT label, NOT replay/backtest, NOT write
files, NOT stage / commit / push, and NOT touch any paper / live / broker /
credential / order surface. Every capability flag is pinned False with a full
scope_locks set. The next gate (detector spec + synthetic dry-run) still requires
an explicit human decision.

Material difference from C1-C14 (the whole point): the rejected trend variants
(C4 long_biased_trend_continuation, C5 btc_sol_long_trend_continuation, the 1h
continuation/swing setups) were FAST, FIXED-HORIZON, long-only directional
CONTINUATION setups. This candidate is SLOW (weeks-to-months), VOLATILITY-TARGETED
(ATR-scaled sizing), symmetric LONG/SHORT/FLAT time-series momentum with REGIME-
AWARE exposure and SIGNAL-DRIVEN (not fixed-horizon) exits.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.strategy_family_tournament_v1_proposal_contract as _sft

C15_SCHEMA_VERSION = 1
C15_MODE = "RESEARCH_ONLY"
C15_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C15"
CANDIDATE_FAMILY = "slow_vol_targeted_time_series_momentum"
CANDIDATE_NAME = "slow_vol_targeted_time_series_momentum_v1"

# Chain gate: the tournament winner must be trend following.
EXPECTED_TOURNAMENT_WINNER = "trend_following"

REJECTED_FAMILIES_C1_TO_C14 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C14)
C14_LESSON = _rep.C14_LESSON

# --- the preserved, frozen gate sequence (each stage human-gated) -----------
GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)

# --- universe + timeframe ---------------------------------------------------
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "D1"
CONTEXT_TIMEFRAME = "W1"          # higher-timeframe regime context only

# --- declared (NOT fitted) spec parameters ----------------------------------
# These are a pre-registered starting specification, not optimized values. The
# one-edit allowance is reserved and NOT used here.
SPEC_PARAMS = {
    "fast_ema_days": 20,
    "slow_ema_days": 100,
    "ts_momentum_lookback_days": 90,      # slow: ~3-month time-series momentum
    "realized_vol_lookback_days": 30,
    "atr_lookback_days": 14,
    "vol_target_annualized": 0.20,        # 20% annualized target vol
    "max_position_scale": 1.5,            # vol-targeting cap (no unbounded lever)
    "entry_deadband_vol_mult": 0.5,       # |momentum| must exceed 0.5 * rolling vol
    "vol_stop_atr_mult": 3.0,             # signal/vol stop distance
    "allow_short": True,
    "allow_flat": True,
    "fixed_horizon": None,                # NOT fixed-horizon -- signal-driven exits
    "rebalance": "daily_on_close",
    "one_edit_allowance_used": False,
}

# --- entry / exit / risk logic (declared) -----------------------------------
ENTRY_LOGIC = (
    "On the D1 close: compute the sign of slow time-series momentum (return over "
    "ts_momentum_lookback_days) AND the fast/slow EMA stack. Go LONG when both are "
    "positive and |momentum| exceeds entry_deadband_vol_mult * realized vol; go "
    "SHORT (symmetric) when both are negative beyond the deadband; otherwise FLAT. "
    "No intrabar/intraday triggers -- daily-close only.")
EXIT_LOGIC = (
    "Signal-driven, NOT fixed-horizon: exit/flip when the EMA stack crosses or the "
    "momentum sign flips, or when the vol-stop (vol_stop_atr_mult * ATR from the "
    "trailing anchor) is hit. Winners are allowed to run across many bars; there "
    "is no max-hold horizon cap.")
RISK_LOGIC = (
    "Volatility targeting: position scale = min(max_position_scale, "
    "vol_target / realized_vol), so risk is constant in vol terms. Per-trade "
    "vol-stop, symmetric long/short, and a portfolio heat cap across the 3 "
    "symbols. No pyramiding beyond the vol-target scale.")

# --- cost model (consistent with the rest of the program) -------------------
FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0

# --- regime tags ------------------------------------------------------------
REGIMES = ("bull", "bear", "chop")
REGIME_EXPECTATION = {
    "bull": "primary edge (ride sustained up-legs)",
    "bear": "secondary edge (symmetric short / flat avoids drawdown)",
    "chop": "expected drag (whipsaw) -- must not dominate net result",
}

# --- baselines + forward-OOS (decisive replay gates, declared not run) ------
BASELINES_REQUIRED = {
    "buy_and_hold": {"required": True,
                     "rule": "matched per-asset buy-and-hold over the same window, "
                             "net of the same 37 bps round-trip"},
    "random_entry": {"required": True,
                     "rule": "deterministic fixed-seed random-entry resamples "
                             "(>=200), same holding distribution, net of costs"},
}
FORWARD_OOS = {"required": True, "window": "2026_unseen_continuation",
               "must_be_net_positive": True}

DECISIVE_REPLAY_GATES = {
    "must_beat_buy_and_hold": True,        # the C14 trap: beating random isn't enough
    "must_beat_random_entry": True,
    "forward_oos_must_be_net_positive": True,
    "regime_net_symmetry_required": True,  # bull/bear/chop net signs sane
    "structural_sample_size_gate": {        # C13 lesson, before replay
        "min_labels_total": 100, "min_labels_per_asset": 20,
        "min_labels_per_regime": 20, "forward_oos_must_be_populated": True},
    "horizon_exit_cap_applicable": False,   # signal-driven exits, not fixed-horizon
    "turnover_sanity_cap_required": True,   # slow strategy must not churn daily
}

# --- evaluation windows (requirement 5) -------------------------------------
EVALUATION_WINDOWS = {
    "durability_window_days": 1095,            # 3-year long-history durability
    "recent_relevance_window_days_min": 90,    # recent 3-month relevance
    "recent_relevance_window_days_max": 180,   # recent 6-month relevance
    "forward_oos_required": True,
    "regime_specific_tagging_required": True,
    "regimes": REGIMES,
}

# --- why materially different from C1-C14 -----------------------------------
MATERIAL_DIFFERENCE_FROM_C1_C14 = (
    "slow (weeks-to-months) time horizon, NOT fast fixed-horizon continuation",
    "volatility-targeted position sizing (ATR-scaled), NOT fixed-size entries",
    "symmetric long/short/flat time-series momentum, NOT long-only continuation",
    "regime-aware exposure (flat/short in confirmed downtrend)",
    "signal-driven exits (trend flip / vol-stop), NOT a fixed max-hold horizon",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector",
    "runs_labels", "runs_replay", "runs_backtest", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "uses_one_edit_allowance", "reproposes_rejected_family",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_detector_run": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_scheduler_change": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_one_edit_invocation": True, "no_rejected_family_repropose": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def get_candidate_15_spec_label() -> str:
    return (
        "Candidate #15 slow_vol_targeted_time_series_momentum_v1 (READ-ONLY, "
        "RESEARCH ONLY, PURE FAMILY SPEC). Slow, volatility-targeted, symmetric "
        "long/short/flat time-series momentum on crypto-D1 with regime-aware "
        "exposure and signal-driven (non-fixed-horizon) exits. Materially "
        "different from the rejected C1-C14 fast continuation variants. SPEC ONLY: "
        "the next gate (detector spec + synthetic dry-run) needs an explicit human "
        "decision. NO data fetch, NO detector, NO labels, NO replay/backtest, NO "
        "paper/live, BUILDS/COMMITS/PUSHES NOTHING. NOT a profitability claim.")


def get_candidate_15_spec_next_action() -> str:
    return "HUMAN_DECISION_C15_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def build_c15_spec(repo_root: Any = ".",
                   tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen Candidate #15 family-spec record. Pure; no I/O; spec
    only. Chain-gated on the tournament proposal (winner == trend_following)."""
    proposal = _sft.build_strategy_family_tournament_proposal(repo_root, tracked_paths)
    proposal_valid = _sft.validate_strategy_family_tournament_proposal(
        proposal)["valid"]
    winner = (proposal.get("recommended_first_family") or {}).get("key")

    blockers: list = []
    if not proposal_valid:
        blockers.append("tournament_proposal_invalid")
    if winner != EXPECTED_TOURNAMENT_WINNER:
        blockers.append("tournament_winner_not_trend_following")
    if CANDIDATE_FAMILY in REJECTED_FAMILIES_C1_TO_C14:
        blockers.append("candidate_family_in_rejected_ledger")

    record: dict[str, Any] = {
        "schema_version": C15_SCHEMA_VERSION, "mode": C15_MODE, "lane": C15_LANE,
        "label": get_candidate_15_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_pure_spec_only": True,
        "blockers": blockers,
        "verdict": ("C15_SPEC_FROZEN_FOR_HUMAN_REVIEW" if not blockers
                    else "C15_SPEC_BLOCKED"),
        # chain provenance
        "source_tournament_winner": winner,
        "tournament_proposal_valid": proposal_valid,
        "tournament_recommended_score":
            (proposal.get("recommended_first_family") or {}).get("priority_score"),
        # the spec
        "gate_sequence": list(GATE_SEQUENCE),
        "gate_sequence_preserved_unchanged": True,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "context_timeframe": CONTEXT_TIMEFRAME,
        "spec_params": dict(SPEC_PARAMS),
        "entry_logic": ENTRY_LOGIC, "exit_logic": EXIT_LOGIC,
        "risk_logic": RISK_LOGIC,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "regimes": list(REGIMES), "regime_expectation": dict(REGIME_EXPECTATION),
        "baselines_required": {k: dict(v) for k, v in BASELINES_REQUIRED.items()},
        "forward_oos": dict(FORWARD_OOS),
        "decisive_replay_gates": _deepish(DECISIVE_REPLAY_GATES),
        "evaluation_windows": dict(EVALUATION_WINDOWS),
        "material_difference_from_c1_c14": list(MATERIAL_DIFFERENCE_FROM_C1_C14),
        "is_fixed_horizon": False,
        "is_volatility_targeted": True,
        "is_time_series_momentum": True,
        "is_regime_aware": True,
        "c14_lesson": C14_LESSON,
        "rejected_families_c1_to_c14": list(REJECTED_FAMILIES_C1_TO_C14),
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C14),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C14,
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": get_candidate_15_spec_next_action(),
        # downstream gates explicitly locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def _deepish(d: dict) -> dict:
    """Shallow copy with one level of nested-dict copy (pure, no I/O)."""
    out: dict = {}
    for k, v in d.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    return out


def validate_c15_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, pure-spec-
    only, chain-gated on the trend-following tournament winner, materially
    different from C1-C14 (slow / vol-targeted / TSMOM / regime-aware / non-fixed-
    horizon), carries the full entry/exit/risk/costs/baselines/forward-OOS + both
    windows, keeps downstream gates locked, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != C15_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_spec_only") is not True:
        failures.append("not_pure_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C15_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("source_tournament_winner") != EXPECTED_TOURNAMENT_WINNER:
        failures.append("winner_not_trend_following")
    if record.get("tournament_proposal_valid") is not True:
        failures.append("tournament_proposal_not_valid")

    # gate sequence preserved
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")

    # material difference + identity flags (the whole point)
    if record.get("is_fixed_horizon") is not False:
        failures.append("must_not_be_fixed_horizon")
    for k in ("is_volatility_targeted", "is_time_series_momentum",
              "is_regime_aware"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    md = record.get("material_difference_from_c1_c14") or []
    if len(md) < 5:
        failures.append("insufficient_material_difference")

    # full logic present
    for field in ("entry_logic", "exit_logic", "risk_logic", "spec_params",
                  "symbols", "timeframe"):
        if not record.get(field):
            failures.append("spec_missing_%s" % field)

    # costs intact (37 bps)
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")
    if (record.get("fee_round_trip_bps", 0)
            + record.get("slippage_round_trip_bps", 0)) != 37.0:
        failures.append("cost_split_tampered")

    # baselines + forward-OOS required (decisive gates; the C14 trap)
    br = record.get("baselines_required") or {}
    if (br.get("buy_and_hold") or {}).get("required") is not True:
        failures.append("buy_and_hold_baseline_not_required")
    if (br.get("random_entry") or {}).get("required") is not True:
        failures.append("random_entry_baseline_not_required")
    dg = record.get("decisive_replay_gates") or {}
    for k in ("must_beat_buy_and_hold", "must_beat_random_entry",
              "forward_oos_must_be_net_positive", "regime_net_symmetry_required"):
        if dg.get(k) is not True:
            failures.append("decisive_gate_off_%s" % k)
    if (record.get("forward_oos") or {}).get("required") is not True:
        failures.append("forward_oos_not_required")

    # both windows (requirement 5)
    w = record.get("evaluation_windows") or {}
    if w.get("durability_window_days") != 1095:
        failures.append("durability_window_not_3yr")
    for k in ("recent_relevance_window_days_min", "recent_relevance_window_days_max"):
        if not w.get(k):
            failures.append("recent_relevance_window_missing_%s" % k)

    # ledger / anti-loop
    if record.get("rejected_families_count") != 19:
        failures.append("rejected_ledger_not_19")
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if not record.get("c14_lesson"):
        failures.append("c14_lesson_missing")

    # downstream gates locked
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_data_fetch", "no_detector_run", "no_labels",
                "no_replay", "no_backtest", "no_commit", "no_push",
                "no_auto_commit", "no_auto_push", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_one_edit_invocation", "no_rejected_family_repropose"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
