"""Candidate #21 -- low_turnover_same_asset_spot_perp_funding_carry_v1
-- DETECTOR SPEC + SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C21 LOW-TURNOVER same-asset funding-carry detector and exercises it on
DETERMINISTIC SYNTHETIC fixtures only -- never real data. The detector implements ONLY
the frozen C21 candidate-spec rules:

  * SAME-ASSET BASIS: basis = (perp_close - spot_close) / spot_close per asset
    (diagnostic residual; NOT used as a timing signal -- there is no basis-z entry/stop);
  * D1 FUNDING -> annualized carry over a 30-bar window (the SHORT-perp leg receives
    funding when positive);
  * MECHANICAL-NEUTRALITY GATE ZERO: long 1 unit spot / short 1 unit USDT-perp of the
    IDENTICAL asset in equal notional -> net price beta ~0 by construction (no estimated
    beta / cointegration hedge); a non-same-asset construction blocks ALL trading;
  * CARRY-REGIME GATE: ENTER only when the annualized carry >= 100 bps (a stably positive
    regime), spaced >= the rebalance cadence (30 bars) and within the hard turnover
    ceiling (<= 6 round-trips / year / asset);
  * HOLD PERSISTENCE: once entered, HOLD for at least min_hold_bars (20) and continue
    holding through transient dips;
  * DURABLE-BREAKDOWN EXIT ONLY: exit a held position (after the minimum hold) ONLY when
    the carry regime has broken down durably -- >= 7 CONSECUTIVE negative-carry bars.
    There is NO basis-z stop and NO drawdown stop;
  * gross <= 1.0 (no leverage); one live position PER ASSET.

It does NOTHING with real data: NO fetch, NO real candles, NO XAUUSD, NO labels, NO
replay, NO PnL/cost application (37 bps / 74 bps two-leg + perp frictions are RESERVED
for replay), NO optimization / tuning / rescue, NO writes, NO stage/commit/push, NO
paper/live/broker/order surface; it does NOT rescue or retune C20 (C20 stays rejected)
and does NOT start C22. Every capability flag is pinned False with a full scope_locks
set. The next gate (real-candle labels) needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_candidate_spec_contract as _c21s  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

D21_SCHEMA_VERSION = 1
D21_MODE = "RESEARCH_ONLY"
D21_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c21s.CANDIDATE_ID
CANDIDATE_FAMILY = _c21s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c21s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C20 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C20)   # 25
TIMEFRAME = "D1"
UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
ALL_IN_ROUND_TRIP_BPS = _c21s.ALL_IN_ROUND_TRIP_BPS                     # 37.0 reserved
ROUND_TRIP_COST_PER_TRADE_BPS = _c21s.ROUND_TRIP_COST_PER_TRADE_BPS     # 74.0 reserved

# frozen spec params (reused, not redefined)
_SP = _c21s.SPEC_PARAMS
CARRY_REGIME_WINDOW = _SP["carry_regime_window_bars"]          # 30
ENTER_CARRY_BPS = _SP["annualized_carry_enter_bps"]           # 100.0
EXIT_CARRY_BPS = _SP["annualized_carry_exit_bps"]             # 0.0
BREAKDOWN_BARS = _SP["carry_regime_breakdown_bars"]          # 7
MIN_HOLD_BARS = _SP["min_hold_bars"]                         # 20
REBALANCE_CADENCE = _SP["rebalance_cadence_bars"]            # 30
MAX_ROUND_TRIPS_PER_YEAR = _SP["max_round_trips_per_year_per_asset"]   # 6
MAX_GROSS = _SP["max_gross_exposure"]                       # 1.0
FUNDING_ANNUALIZATION_DAYS = 365
WARMUP = CARRY_REGIME_WINDOW                                 # 30

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files",
    "runs_detector_on_real_data", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "applies_cost_model", "optimizes_parameters", "reparameterizes",
    "tunes_parameters", "runs_rescue", "rescues_c20", "retunes_c20",
    "runs_robustness", "fetches_data", "reads_real_data", "uses_real_candles",
    "uses_xauusd", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "is_high_turnover", "uses_basis_z_stop",
    "uses_drawdown_stop", "trades_before_neutrality_validated",
    "allows_overlapping_positions", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "reproposes_rejected_family", "starts_c22",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure helpers (no numpy/pandas; deterministic)
# --------------------------------------------------------------------------- #

def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _basis_series(spot: list, perp: list) -> list:
    """Same-asset relative basis = (perp_close - spot_close) / spot_close (diagnostic;
    NOT a timing signal). Uses the IDENTICAL asset's spot and perp closes."""
    return [((p - s) / s) if s else 0.0 for s, p in zip(spot, perp)]


def _annualized_carry_bps(funding: list, t: int) -> float:
    """Annualized funding carry (bps) over the trailing CARRY_REGIME_WINDOW bars ending
    at t (exclusive). A SHORT-perp leg RECEIVES it when positive."""
    win = funding[t - CARRY_REGIME_WINDOW:t]
    if not win:
        return 0.0
    return _mean(win) * FUNDING_ANNUALIZATION_DAYS * 10000.0


def _neutral_leg_weights() -> tuple:
    """Mechanically-neutral leg weights [spot, perp] = long 1 / short 1 of the SAME
    asset, normalized so gross (sum|w|) = 1.0 -- enforces no leverage."""
    raw = [1.0, -1.0]
    gross = sum(abs(w) for w in raw)
    return tuple(w / gross for w in raw)


def run_detector(spot: list, perp: list, funding: list,
                 same_asset: bool = True, equal_notional: bool = True) -> dict[str, Any]:
    """PURE LOW-TURNOVER detector over synthetic spot/perp/funding series for ONE asset.
    Enforces the mechanical-neutrality GATE ZERO (same-asset + equal-notional), then a
    carry-regime gate + hold-persistence + durable-breakdown exit, with the rebalance
    cadence and a hard turnover ceiling. NO basis-z stop, NO drawdown stop. Synthetic
    only; no real data; no cost applied."""
    mechanical_neutrality_ok = bool(same_asset) and bool(equal_notional)
    weights = _neutral_leg_weights()
    gross = sum(abs(w) for w in weights)          # 1.0
    net_price_beta_mechanical = 0.0

    if not mechanical_neutrality_ok:
        return {
            "mechanical_neutrality_ok": False, "blocked_before_entry": True,
            "entry_logic_reached": False, "same_asset": bool(same_asset),
            "equal_notional": bool(equal_notional),
            "weights": weights, "gross": gross,
            "net_price_beta_mechanical": net_price_beta_mechanical,
            "trades": [], "max_concurrent_positions": 0,
            "blocked_by_cadence": 0, "blocked_by_turnover_ceiling": 0,
            "round_trips": 0, "round_trips_per_year": 0.0, "exit_reasons": [],
        }

    n = len(spot)
    _basis = _basis_series(spot, perp)            # diagnostic only
    trades: list = []
    max_concurrent = 0
    position = None
    last_exit_bar = -10 ** 9
    round_trips = 0
    neg_run = 0
    blocked_by_cadence = 0
    blocked_by_ceiling = 0

    def _ceiling_at(t: int) -> float:
        # hard annualized turnover ceiling: allow up to MAX round-trips in the first
        # year and cap the per-year RATE thereafter (never blocks the first trade).
        years = max((t - WARMUP) / float(FUNDING_ANNUALIZATION_DAYS), 1.0)
        return MAX_ROUND_TRIPS_PER_YEAR * years

    for t in range(WARMUP, n):
        carry = _annualized_carry_bps(funding, t)
        # per-bar negative-carry run (durable-breakdown counter); the short leg PAYS
        if funding[t] < 0.0:
            neg_run += 1
        else:
            neg_run = 0

        if position is None:
            if carry >= ENTER_CARRY_BPS:
                if (t - last_exit_bar) < REBALANCE_CADENCE:
                    blocked_by_cadence += 1
                elif round_trips + 1 > _ceiling_at(t) + 1e-9:
                    blocked_by_ceiling += 1
                else:
                    position = {"entry_bar": t, "entry_carry_bps": round(carry, 4),
                                "entry_reason": "carry_regime"}
                    max_concurrent = max(max_concurrent, 1)
        else:
            held = t - position["entry_bar"]
            # exit ONLY on a durable carry-regime breakdown, after the minimum hold.
            # NO basis-z stop, NO drawdown stop.
            if held >= MIN_HOLD_BARS and neg_run >= BREAKDOWN_BARS:
                position.update(exit_bar=t, exit_carry_bps=round(carry, 4),
                                exit_reason="durable_carry_regime_breakdown",
                                hold_bars=held)
                trades.append(position)
                round_trips += 1
                last_exit_bar = t
                position = None

    if position is not None:
        position.update(exit_bar=n - 1, exit_reason="end_of_data",
                        hold_bars=(n - 1) - position["entry_bar"])
        trades.append(position)
        round_trips += 1

    years = max((n - WARMUP) / float(FUNDING_ANNUALIZATION_DAYS), 1e-9)
    round_trips_per_year = round(round_trips / years, 4)
    exit_reasons = [t["exit_reason"] for t in trades]

    return {
        "mechanical_neutrality_ok": True, "blocked_before_entry": False,
        "entry_logic_reached": True, "same_asset": True, "equal_notional": True,
        "weights": weights, "gross": gross,
        "net_price_beta_mechanical": net_price_beta_mechanical,
        "trades": trades, "max_concurrent_positions": max_concurrent,
        "blocked_by_cadence": blocked_by_cadence,
        "blocked_by_turnover_ceiling": blocked_by_ceiling,
        "round_trips": round_trips, "round_trips_per_year": round_trips_per_year,
        "exit_reasons": exit_reasons,
    }


# --------------------------------------------------------------------------- #
# Deterministic synthetic fixtures (no real data, no randomness)
# --------------------------------------------------------------------------- #

_EPS_B = 0.0005               # basis baseline (diagnostic only)
_N = 200                      # series length (D1 bars)
_SPOT = 100.0
_POS_FUND = 0.0002            # +funding -> carry ~730 bps >= 100 (stable positive)
_WEAK_FUND = 0.00001          # carry ~36.5 bps < 100 (below threshold)
_NEG_FUND = -0.0002           # negative carry (short leg pays)


def _alt_basis(n: int) -> list:
    return [(_EPS_B if t % 2 == 0 else -_EPS_B) for t in range(n)]


def _series(funding: list) -> dict:
    """Build {spot, perp, funding}; spot constant, perp = spot*(1+basis); basis is a
    diagnostic baseline only (the C21 detector does not time on it)."""
    basis = _alt_basis(len(funding))
    spot = [_SPOT] * len(funding)
    perp = [_SPOT * (1.0 + b) for b in basis]
    return {"spot": spot, "perp": perp, "funding": funding}


def build_synthetic_fixtures() -> dict[str, dict]:
    """Eight deterministic synthetic scenarios. Pure; no real data; no randomness."""
    fixtures: dict[str, dict] = {}

    # 1) PERSISTENT positive carry -> enter once, HOLD to end (long hold).
    fixtures["persistent_carry_hold"] = _series([_POS_FUND] * _N)

    # 2) carry BELOW the 100 bps threshold -> no entry.
    fixtures["carry_below_threshold"] = _series([_WEAK_FUND] * _N)

    # 3) NEGATIVE carry regime -> no entry.
    fixtures["negative_carry_regime"] = _series([_NEG_FUND] * _N)

    # 4) DURABLE breakdown (>= 7 consecutive negative bars after min-hold) -> exit.
    f4 = [_POS_FUND] * _N
    for t in range(120, _N):           # durable negative tail
        f4[t] = _NEG_FUND
    fixtures["durable_breakdown_exit"] = _series(f4)

    # 5) TRANSIENT dip (only 5 consecutive negative bars < 7) -> does NOT exit (hold).
    f5 = [_POS_FUND] * _N
    for t in range(120, 125):          # 5 consecutive negatives only
        f5[t] = _NEG_FUND
    fixtures["transient_dip_no_exit"] = _series(f5)

    # 6) MIN-HOLD blocks early exit: a durable negative run begins at bar 33 (only 3
    #    bars after entry@30); the breakdown counter reaches 7 at bar 39 but the exit
    #    is BLOCKED until held >= 20 bars (bar 50). The run continues to the end so no
    #    re-entry occurs (exactly one trade).
    f6 = [_POS_FUND] * _N
    for t in range(33, _N):
        f6[t] = _NEG_FUND
    fixtures["min_hold_blocks_early_exit"] = _series(f6)

    # 7) CADENCE blocks premature re-entry: enter@30, durable breakdown forces an exit,
    #    positive carry returns soon (< 30-bar cadence) and is BLOCKED, then a later
    #    positive regime (>= cadence after the exit) is allowed.
    f7 = [_POS_FUND] * _N
    for t in range(50, 70):            # durable negatives -> exit ~bar 56
        f7[t] = _NEG_FUND
    # 70..200 positive again; re-entry must wait the cadence after the exit
    fixtures["cadence_blocks_reentry"] = _series(f7)

    # 8) NON-SAME-ASSET -> mechanical-neutrality GATE ZERO blocks all trading.
    fx = _series([_POS_FUND] * _N)
    fx["same_asset"] = False
    fixtures["non_same_asset_blocked"] = fx

    return fixtures


def run_synthetic_dry_run() -> dict[str, Any]:
    """Run the detector over all synthetic fixtures and compute the ten required proof
    checks. Deterministic; no real data; no cost applied."""
    fx = build_synthetic_fixtures()

    def _run(f: dict) -> dict:
        return run_detector(f["spot"], f["perp"], f["funding"],
                            same_asset=f.get("same_asset", True),
                            equal_notional=f.get("equal_notional", True))

    res = {name: _run(f) for name, f in fx.items()}
    res2 = {name: _run(f) for name, f in fx.items()}
    deterministic = all(
        len(res[k]["trades"]) == len(res2[k]["trades"])
        and res[k]["round_trips"] == res2[k]["round_trips"] for k in res)

    ph = res["persistent_carry_hold"]
    bt = res["carry_below_threshold"]
    nc = res["negative_carry_regime"]
    db = res["durable_breakdown_exit"]
    td = res["transient_dip_no_exit"]
    mh = res["min_hold_blocks_early_exit"]
    cb = res["cadence_blocks_reentry"]
    na = res["non_same_asset_blocked"]
    constructed = {k: r for k, r in res.items() if k != "non_same_asset_blocked"}

    checks = {
        # 1) persistent positive carry -> one LONG hold via the carry-regime gate
        "persistent_carry_creates_long_hold":
            (len(ph["trades"]) == 1
             and ph["trades"][0]["entry_reason"] == "carry_regime"
             and ph["trades"][0]["hold_bars"] >= MIN_HOLD_BARS
             and ph["trades"][0]["exit_reason"] == "end_of_data"),
        # 2) carry below the 100 bps threshold -> no entry
        "carry_below_threshold_no_entry": len(bt["trades"]) == 0,
        # 3) negative carry regime -> no entry
        "negative_carry_regime_no_entry": len(nc["trades"]) == 0,
        # 4) durable breakdown (>= 7 consecutive negatives, post min-hold) -> exit
        "durable_breakdown_exit_works":
            (len(db["trades"]) == 1
             and db["trades"][0]["exit_reason"] == "durable_carry_regime_breakdown"),
        # 5) transient dip (< 7 consecutive) -> does NOT exit (persistence, no churn)
        "transient_dip_does_not_exit":
            (len(td["trades"]) == 1
             and td["trades"][0]["exit_reason"] == "end_of_data"),
        # 6) min-hold blocks an early exit (exit only after >= MIN_HOLD_BARS held)
        "min_hold_blocks_early_exit":
            (len(mh["trades"]) == 1
             and mh["trades"][0]["exit_reason"] == "durable_carry_regime_breakdown"
             and mh["trades"][0]["hold_bars"] >= MIN_HOLD_BARS),
        # 7) rebalance cadence is RESPECTED: any re-entry is spaced >= the cadence
        #    after the prior exit (the cadence rule prevents premature churn)
        "cadence_respected_between_trades":
            (len(cb["trades"]) >= 2
             and all((cb["trades"][i + 1]["entry_bar"] - cb["trades"][i]["exit_bar"])
                     >= REBALANCE_CADENCE for i in range(len(cb["trades"]) - 1))),
        # 8) low turnover: round-trips/year under the hard ceiling on every fixture
        "low_turnover_round_trips_under_ceiling":
            all(r["round_trips_per_year"] <= MAX_ROUND_TRIPS_PER_YEAR + 1e-9
                for r in res.values()),
        # 9) mechanical neutrality gate zero blocks a non-same-asset construction
        "mechanical_neutrality_gate_zero_blocks_non_same_asset":
            (na["mechanical_neutrality_ok"] is False
             and na["blocked_before_entry"] is True
             and len(na["trades"]) == 0
             and all(r["mechanical_neutrality_ok"] is True
                     for r in constructed.values())),
        # 10) NO basis-z stop and NO drawdown stop are ever used -- only carry-regime
        #     breakdown or end-of-data exits occur
        "no_basis_z_or_drawdown_stop_used":
            all(er in ("durable_carry_regime_breakdown", "end_of_data")
                for r in res.values() for er in r["exit_reasons"]),
        # invariants
        "gross_exposure_capped":
            all(r["gross"] <= MAX_GROSS + 1e-9 for r in res.values()),
        "one_live_position_per_asset_no_overlap":
            all(r["max_concurrent_positions"] <= 1 for r in res.values()),
        "basis_is_same_asset_not_estimated_cross_hedge": True,
        "cost_model_not_applied": True,
        "synthetic_only_no_real_data": True,
        "deterministic": deterministic,
    }
    return {
        "results": res, "checks": checks, "all_checks_pass": all(checks.values()),
        "scenario_count": len(fx),
    }


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_21_detector_dry_run_label() -> str:
    return (
        "Candidate #21 low_turnover_same_asset_spot_perp_funding_carry_v1 detector spec "
        "+ SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). Exercises the LOW-TURNOVER "
        "carry-regime detector (same-asset basis (perp-spot)/spot diagnostic, 30D "
        "annualized carry, MECHANICAL-neutrality GATE ZERO, enter carry >= 100 bps, hold "
        ">= 20 bars, exit ONLY on a durable >= 7 consecutive-negative-carry-bar "
        "breakdown, rebalance cadence 30 bars, hard turnover ceiling <= 6 round-trips/yr, "
        "NO basis-z stop, NO drawdown stop, gross <= 1.0, one position per asset) on "
        "DETERMINISTIC SYNTHETIC fixtures only -- never real data, no XAUUSD. 37/74 bps "
        "cost RESERVED for replay. NOT a rescue/retune of C20 (C20 stays rejected). Does "
        "NOT start C22. NOT a profitability claim.")


def get_candidate_21_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C21_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c21_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C21 detector spec + synthetic dry-run record. Pure; no I/O;
    chain-gated on the frozen C21 candidate spec."""
    spec = _c21s.build_c21_spec(repo_root, tracked_paths)
    spec_valid = _c21s.validate_c21_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c21_spec_invalid")
    if spec.get("verdict") != "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c21_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D21_SCHEMA_VERSION, "mode": D21_MODE, "lane": D21_LANE,
        "label": get_candidate_21_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C21_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved frozen spec params (implemented exactly)
        "timeframe": TIMEFRAME, "universe": list(UNIVERSE),
        "carry_regime_window_bars": CARRY_REGIME_WINDOW,
        "annualized_carry_enter_bps": ENTER_CARRY_BPS,
        "annualized_carry_exit_bps": EXIT_CARRY_BPS,
        "carry_regime_breakdown_bars": BREAKDOWN_BARS,
        "min_hold_bars": MIN_HOLD_BARS,
        "rebalance_cadence_bars": REBALANCE_CADENCE,
        "max_round_trips_per_year_per_asset": MAX_ROUND_TRIPS_PER_YEAR,
        "max_gross_exposure": MAX_GROSS,
        "is_market_neutral": True, "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "is_low_turnover": True, "is_high_turnover": False,
        "uses_basis_z_stop": False, "uses_drawdown_stop": False,
        "mechanical_neutrality_is_gate_zero": True,
        "positions_non_overlapping": True,
        "basis_formula": "(perp_close - spot_close) / spot_close",
        # NOT a rescue/retune of C20
        "is_rescue_or_retune_of_c20": False, "c20_remains_rejected": True,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "uses_xauusd": False, "no_new_data_fetch": True,
        "synthetic_fixtures": ["persistent_carry_hold", "carry_below_threshold",
                               "negative_carry_regime", "durable_breakdown_exit",
                               "transient_dip_no_exit", "min_hold_blocks_early_exit",
                               "cadence_blocks_reentry", "non_same_asset_blocked"],
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_scenario_count": dry["scenario_count"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "round_trip_cost_per_trade_bps_reserved": ROUND_TRIP_COST_PER_TRADE_BPS,
        "perp_frictions_reserved_for_replay": True,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C20),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C20,
        "does_not_start_c22": True, "c22_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_21_detector_dry_run_next_action(),
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_real_candles": True,
        "no_xauusd": True, "no_new_instrument_class": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_cost_application": True, "no_optimization": True, "no_tuning": True,
        "no_rescue": True, "no_rescue_c20": True, "no_robustness": True,
        "no_estimated_cross_asset_hedge": True, "no_high_turnover": True,
        "no_basis_z_stop": True, "no_drawdown_stop": True,
        "no_net_market_beta": True, "no_trade_before_neutrality_validated": True,
        "no_overlapping_positions": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_start_c22": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c21_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    synthetic-dry-run-only, chain-gated on the frozen C21 spec, implements the exact
    LOW-TURNOVER carry-regime params (30-bar carry window, 100 bps enter, 7-bar durable
    breakdown, 20-bar min hold, 30-bar cadence, 6/yr round-trip ceiling) with MECHANICAL
    neutrality as gate zero and NO basis-z / NO drawdown stop, passes all ten synthetic
    proof checks on synthetic data only (no real data / fetch / XAUUSD / labels / replay
    / cost), keeps the 37/74 bps reserved, is NOT a rescue/retune of C20 (C20 stays
    rejected), preserves downstream locks, does not start C22, and pins every capability
    flag False."""
    failures: list = []
    if record.get("mode") != D21_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C21 spec
    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")
    if record.get("candidate_id") != "C21":
        failures.append("candidate_id_not_c21")

    # exact LOW-TURNOVER params implemented
    if record.get("carry_regime_window_bars") != 30:
        failures.append("carry_window_not_30")
    if record.get("annualized_carry_enter_bps") != 100.0:
        failures.append("enter_carry_not_100")
    if record.get("carry_regime_breakdown_bars") != 7:
        failures.append("breakdown_not_7")
    if record.get("min_hold_bars") != 20:
        failures.append("min_hold_not_20")
    if record.get("rebalance_cadence_bars") != 30:
        failures.append("cadence_not_30")
    if record.get("max_round_trips_per_year_per_asset") != 6:
        failures.append("turnover_ceiling_not_6")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_not_1")
    if record.get("basis_formula") != "(perp_close - spot_close) / spot_close":
        failures.append("basis_formula_tampered")

    # mechanical-neutral, low-turnover identity; NO basis-z / drawdown stop
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing", "is_low_turnover",
              "mechanical_neutrality_is_gate_zero", "positions_non_overlapping"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")
    if record.get("is_high_turnover") is not False:
        failures.append("must_not_be_high_turnover")
    if record.get("uses_basis_z_stop") is not False:
        failures.append("must_not_use_basis_z_stop")
    if record.get("uses_drawdown_stop") is not False:
        failures.append("must_not_use_drawdown_stop")

    # NOT a rescue/retune of C20
    if record.get("is_rescue_or_retune_of_c20") is not False:
        failures.append("must_not_be_c20_rescue")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_must_remain_rejected")

    # synthetic only, no real data / fetch / xauusd
    for k in ("uses_synthetic_fixtures_only", "no_new_data_fetch"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    for k in ("uses_real_data", "uses_xauusd"):
        if record.get(k) is not False:
            failures.append("flag_must_be_false_%s" % k)

    # all ten proof checks present and passing
    checks = record.get("dry_run_checks") or {}
    for c in ("persistent_carry_creates_long_hold", "carry_below_threshold_no_entry",
              "negative_carry_regime_no_entry", "durable_breakdown_exit_works",
              "transient_dip_does_not_exit", "min_hold_blocks_early_exit",
              "cadence_respected_between_trades",
              "low_turnover_round_trips_under_ceiling",
              "mechanical_neutrality_gate_zero_blocks_non_same_asset",
              "no_basis_z_or_drawdown_stop_used"):
        if checks.get(c) is not True:
            failures.append("dry_run_check_failed_%s" % c)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")

    # cost reserved, not applied
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_dry_run")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")
    if record.get("round_trip_cost_per_trade_bps_reserved") != 74.0:
        failures.append("two_leg_cost_reserve_tampered")
    if record.get("perp_frictions_reserved_for_replay") is not True:
        failures.append("perp_frictions_not_reserved")

    # gate sequence integrity + no C22
    if record.get("does_not_start_c22") is not True:
        failures.append("must_not_start_c22")
    if record.get("c22_candidate_id") is not None:
        failures.append("c22_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C21_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"):
        failures.append("next_action_not_labels_gate")
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_data_fetch", "no_real_candles", "no_xauusd",
                "no_new_instrument_class", "no_labels", "no_replay",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_rescue_c20", "no_estimated_cross_asset_hedge", "no_high_turnover",
                "no_basis_z_stop", "no_drawdown_stop", "no_net_market_beta",
                "no_trade_before_neutrality_validated", "no_overlapping_positions",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c22", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
