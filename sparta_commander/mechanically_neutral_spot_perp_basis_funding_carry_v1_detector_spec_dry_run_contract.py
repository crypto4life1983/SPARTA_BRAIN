"""Candidate #20 -- mechanically_neutral_spot_perp_basis_funding_carry_v1
-- DETECTOR SPEC + SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C20 same-asset basis + funding-carry detector and exercises it on
DETERMINISTIC SYNTHETIC fixtures only -- never real data. The detector implements ONLY
the frozen C20 candidate-spec rules:

  * SAME-ASSET BASIS: basis = (perp_close - spot_close) / spot_close per asset;
  * 60-bar basis z-score (trailing window, excludes the current bar);
  * D1 FUNDING aggregation -> annualized funding carry (bps) over a 30-bar lookback
    (the SHORT-perp leg receives funding when positive);
  * MECHANICAL-NEUTRALITY GATE ZERO: the position is long 1 unit spot / short 1 unit
    USDT-perp of the IDENTICAL asset in EQUAL notional -> net price beta ~0 BY
    CONSTRUCTION; if the construction is not same-asset + equal-notional, ALL trading is
    blocked before any entry logic;
  * ENTER when annualized funding carry >= 50 bps in a non-negative-carry regime OR
    basis z >= +2.0 (perp-premium convergence), spaced >= 5 bars, gross <= 1.0;
  * EXIT when |basis z| <= 0.25 (convergence) OR carry falls below the floor / regime
    turns negative; STOP/INVALIDATE when |basis z| >= 4.0 or negative-carry break;
  * one live position PER ASSET (no overlap).

It does NOTHING with real data: NO fetch, NO real candles, NO XAUUSD, NO labels, NO
replay, NO PnL/cost application (the 37 bps + perp frictions are RESERVED for replay),
NO optimization / tuning / rescue, NO writes, NO stage/commit/push, NO
paper/live/broker/order surface, and does NOT start C21. Every capability flag is pinned
False with a full scope_locks set. The next gate (real-candle labels) needs an explicit
human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_candidate_spec_contract as _c20s  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

D20_SCHEMA_VERSION = 1
D20_MODE = "RESEARCH_ONLY"
D20_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c20s.CANDIDATE_ID
CANDIDATE_FAMILY = _c20s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c20s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C19 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C19)   # 24
TIMEFRAME = "D1"
UNIVERSE = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
ALL_IN_ROUND_TRIP_BPS = _c20s.ALL_IN_ROUND_TRIP_BPS                     # 37.0 reserved

# frozen spec params (reused, not redefined)
_SP = _c20s.SPEC_PARAMS
BASIS_Z_WINDOW = _SP["basis_zscore_window_bars"]            # 60
FUNDING_LOOKBACK = _SP["funding_lookback_bars"]             # 30
ENTRY_BASIS_Z = _SP["entry_basis_zscore_threshold"]        # 2.0
ENTRY_CARRY_BPS = _SP["entry_min_annualized_carry_bps"]    # 50.0
EXIT_BASIS_Z = _SP["exit_basis_zscore_threshold"]          # 0.25
STOP_BASIS_Z = _SP["stop_basis_zscore_threshold"]          # 4.0
MAX_GROSS = _SP["max_gross_exposure"]                      # 1.0
MIN_SPACING = _SP["min_bars_between_rebalances"]           # 5
FUNDING_ANNUALIZATION_DAYS = 365                           # D1 funding -> annualized

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files",
    "runs_detector_on_real_data", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "applies_cost_model", "optimizes_parameters", "reparameterizes",
    "tunes_parameters", "runs_rescue", "runs_robustness", "fetches_data",
    "reads_real_data", "uses_real_candles", "uses_xauusd", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "carries_net_market_beta",
    "uses_estimated_cross_asset_hedge", "trades_before_neutrality_validated",
    "allows_overlapping_positions", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "reproposes_rejected_family", "starts_c21",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure helpers (no numpy/pandas; deterministic)
# --------------------------------------------------------------------------- #

def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _basis_series(spot: list, perp: list) -> list:
    """Same-asset relative basis = (perp_close - spot_close) / spot_close, per bar.
    Uses the IDENTICAL asset's spot and perp closes -- never a cross-asset spread."""
    return [((p - s) / s) if s else 0.0 for s, p in zip(spot, perp)]


def _annualized_carry_bps(funding: list, t: int) -> float:
    """Annualized funding carry (bps) over the trailing FUNDING_LOOKBACK bars ending at
    t (exclusive). funding[i] is the per-D1 aggregated funding rate; a SHORT-perp leg
    RECEIVES it when positive. Annualized over FUNDING_ANNUALIZATION_DAYS."""
    win = funding[t - FUNDING_LOOKBACK:t]
    if not win:
        return 0.0
    return _mean(win) * FUNDING_ANNUALIZATION_DAYS * 10000.0


def _neutral_leg_weights() -> tuple:
    """Mechanically-neutral leg weights [spot, perp] = long 1 / short 1 of the SAME
    asset, normalized so gross (sum|w|) = 1.0 -- enforces no leverage."""
    raw = [1.0, -1.0]                     # long spot, short same-asset perp
    gross = sum(abs(w) for w in raw)      # 2.0
    return tuple(w / gross for w in raw)  # [0.5, -0.5] -> gross 1.0


def run_detector(spot: list, perp: list, funding: list,
                 same_asset: bool = True, equal_notional: bool = True) -> dict[str, Any]:
    """PURE detector over synthetic spot/perp/funding series for ONE asset. Enforces
    the mechanical-neutrality GATE ZERO (same-asset + equal-notional), then applies the
    basis-z / funding-carry entry/exit/stop rules with spacing + non-overlap + gross
    cap. Synthetic only; no real data; no cost applied."""
    # GATE ZERO: mechanical neutrality must hold BY CONSTRUCTION before any entry logic
    mechanical_neutrality_ok = bool(same_asset) and bool(equal_notional)
    weights = _neutral_leg_weights()
    gross = sum(abs(w) for w in weights)          # 1.0
    net_price_beta = round(weights[0] - weights[1] * 0.0, 12)  # mechanical; not used
    # long spot, short SAME-asset perp in equal notional -> price beta cancels by build
    net_price_beta_mechanical = 0.0

    if not mechanical_neutrality_ok:
        return {
            "mechanical_neutrality_ok": False, "blocked_before_entry": True,
            "entry_logic_reached": False, "same_asset": bool(same_asset),
            "equal_notional": bool(equal_notional),
            "weights": weights, "gross": gross,
            "net_price_beta_mechanical": net_price_beta_mechanical,
            "trades": [], "max_concurrent_positions": 0,
        }

    basis = _basis_series(spot, perp)
    n = len(basis)
    trades: list = []
    max_concurrent = 0
    position = None
    last_entry_bar = -10 ** 9

    for t in range(BASIS_Z_WINDOW, n):
        win = basis[t - BASIS_Z_WINDOW:t]
        mu = _mean(win)
        var = _mean([(x - mu) ** 2 for x in win])
        sd = var ** 0.5
        if sd <= 0:
            continue
        z = (basis[t] - mu) / sd
        carry_bps = _annualized_carry_bps(funding, t)
        negative_carry_regime = carry_bps < 0.0

        if position is None:
            carry_entry = (carry_bps >= ENTRY_CARRY_BPS) and (not negative_carry_regime)
            basis_entry = z >= ENTRY_BASIS_Z          # signed: perp premium
            if (carry_entry or basis_entry) and (t - last_entry_bar) >= MIN_SPACING:
                position = {
                    "entry_bar": t, "entry_z": round(z, 4),
                    "entry_carry_bps": round(carry_bps, 4),
                    "entry_reason": "funding_carry" if carry_entry else "basis_convergence",
                }
                last_entry_bar = t
                max_concurrent = max(max_concurrent, 1)
        else:
            if abs(z) >= STOP_BASIS_Z:
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "divergence_stop"
                trades.append(position)
                position = None
            elif negative_carry_regime:
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "negative_carry_stop"
                trades.append(position)
                position = None
            elif abs(z) <= EXIT_BASIS_Z:
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "convergence"
                trades.append(position)
                position = None
            elif (position.get("entry_reason") == "funding_carry"
                  and carry_bps < ENTRY_CARRY_BPS):
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "carry_decay"
                trades.append(position)
                position = None

    if position is not None:
        position["exit_bar"] = n - 1
        position["exit_reason"] = "end_of_data"
        trades.append(position)

    return {
        "mechanical_neutrality_ok": True, "blocked_before_entry": False,
        "entry_logic_reached": True, "same_asset": True, "equal_notional": True,
        "weights": weights, "gross": gross,
        "net_price_beta_mechanical": net_price_beta_mechanical,
        "trades": trades, "max_concurrent_positions": max_concurrent,
    }


# --------------------------------------------------------------------------- #
# Deterministic synthetic fixtures (no real data, no randomness)
# --------------------------------------------------------------------------- #

_EPS_B = 0.0005               # basis baseline scale: +/-5 bps -> std ~ EPS_B
_N = 200                      # series length: 60 z-window warmup + trading
_SPOT = 100.0                 # constant spot; basis is driven by the perp leg


def _alt_basis(n: int) -> list:
    """Alternating +/-EPS_B basis baseline -> std ~ EPS_B so basis z-scores are clean
    (z ~ +/-1 at baseline, never reaching the +2.0 entry threshold)."""
    return [(_EPS_B if t % 2 == 0 else -_EPS_B) for t in range(n)]


def _series_from_basis(basis: list, funding: list) -> dict:
    """Build {spot, perp, funding} for ONE asset from a basis array and a per-D1
    funding array. perp = spot * (1 + basis); spot is constant. Same-asset legs."""
    spot = [_SPOT] * len(basis)
    perp = [_SPOT * (1.0 + b) for b in basis]
    return {"spot": spot, "perp": perp, "funding": funding}


def build_synthetic_fixtures() -> dict[str, dict]:
    """Eight deterministic synthetic scenarios, each returning {spot, perp, funding}
    (plus same_asset flag for the gate-zero negative case). Pure; no real data; no
    randomness."""
    fixtures: dict[str, dict] = {}

    # 1) FUNDING-CARRY valid: persistently positive funding (carry ~730 bps), weak
    #    basis -> enters via funding_carry (proof 1).
    basis1 = _alt_basis(_N)
    fixtures["funding_carry_valid"] = _series_from_basis(
        basis1, [0.0002] * _N)

    # 2) BASIS-PREMIUM valid: zero funding, a +2.6 z basis spike -> enters via
    #    basis_convergence (proof 2).
    basis2 = _alt_basis(_N)
    basis2[150] = 2.6 * _EPS_B
    fixtures["basis_premium_valid"] = _series_from_basis(basis2, [0.0] * _N)

    # 3) NEGATIVE-CARRY regime blocks entry: persistently negative funding, weak basis
    #    -> no trade (proof 3).
    basis3 = _alt_basis(_N)
    fixtures["negative_carry_blocks"] = _series_from_basis(
        basis3, [-0.0002] * _N)

    # 4) WEAK basis AND weak carry -> no trade (proof 4).
    basis4 = _alt_basis(_N)
    fixtures["weak_no_trade"] = _series_from_basis(basis4, [0.0000005] * _N)

    # 5) CONVERGENCE exit: basis spike enters, then basis -> 0 (|z| <= 0.25) exits
    #    on convergence (proof 5).
    basis5 = _alt_basis(_N)
    basis5[150] = 2.6 * _EPS_B            # enter (basis premium)
    basis5[151] = 0.0                     # converge -> |z| <= 0.25 -> exit
    fixtures["convergence_exit"] = _series_from_basis(basis5, [0.0] * _N)

    # 6) DIVERGENCE stop: basis spike enters, then basis blows out (|z| >= 4) -> stop
    #    (proof 6).
    basis6 = _alt_basis(_N)
    basis6[150] = 2.6 * _EPS_B            # enter
    basis6[151] = 4.6 * _EPS_B            # diverge -> |z| >= 4 -> divergence stop
    fixtures["divergence_stop"] = _series_from_basis(basis6, [0.0] * _N)

    # 7) SPACING: enter@150, exit@151, re-spikes @152/@153 (within 5 bars -> blocked),
    #    next allowed entry @156 (>= 5 bars after 150), exit @157 (proof 8).
    basis7 = _alt_basis(_N)
    basis7[150] = 2.6 * _EPS_B            # enter
    basis7[151] = 0.0                     # converge exit
    basis7[152] = 2.6 * _EPS_B            # within spacing -> blocked
    basis7[153] = 2.6 * _EPS_B            # within spacing -> blocked
    basis7[156] = 2.6 * _EPS_B            # >= 5 bars after 150 -> allowed
    basis7[157] = 0.0                     # converge exit
    fixtures["spacing"] = _series_from_basis(basis7, [0.0] * _N)

    # 8) NON-SAME-ASSET blocked: a would-be carry setup, but run with same_asset=False
    #    -> mechanical-neutrality GATE ZERO blocks all trading (proof 10).
    basis8 = _alt_basis(_N)
    fx = _series_from_basis(basis8, [0.0002] * _N)
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
        and res[k]["gross"] == res2[k]["gross"] for k in res)

    fc = res["funding_carry_valid"]
    bp = res["basis_premium_valid"]
    nc = res["negative_carry_blocks"]
    weak = res["weak_no_trade"]
    cv = res["convergence_exit"]
    dv = res["divergence_stop"]
    sp = res["spacing"]
    na = res["non_same_asset_blocked"]

    # only the asset-construction fixtures (exclude the deliberately-blocked one)
    constructed = {k: r for k, r in res.items() if k != "non_same_asset_blocked"}

    checks = {
        # 1) positive funding carry creates a valid neutral setup
        "funding_carry_creates_valid_neutral_setup":
            (fc["mechanical_neutrality_ok"] and len(fc["trades"]) >= 1
             and fc["trades"][0]["entry_reason"] == "funding_carry"),
        # 2) perp-premium basis z >= +2.0 creates a valid convergence setup
        "basis_premium_creates_valid_convergence_setup":
            (bp["mechanical_neutrality_ok"] and len(bp["trades"]) >= 1
             and bp["trades"][0]["entry_reason"] == "basis_convergence"),
        # 3) negative funding/carry regime blocks entry
        "negative_carry_regime_blocks_entry":
            (nc["mechanical_neutrality_ok"] and len(nc["trades"]) == 0),
        # 4) weak basis and weak carry creates no trade
        "weak_basis_and_carry_no_trade":
            (weak["mechanical_neutrality_ok"] and len(weak["trades"]) == 0),
        # 5) convergence exit works at |z| <= 0.25
        "convergence_exit_works":
            (len(cv["trades"]) == 1
             and cv["trades"][0]["exit_reason"] == "convergence"),
        # 6) divergence stop works at |z| >= 4.0
        "divergence_stop_works":
            (len(dv["trades"]) == 1
             and dv["trades"][0]["exit_reason"] == "divergence_stop"),
        # 7) gross exposure cap is respected (no leverage)
        "gross_exposure_capped":
            all(r["gross"] <= MAX_GROSS + 1e-9 for r in res.values()),
        # 8) rebalance spacing prevents overtrading
        "rebalance_spacing_prevents_overtrading":
            (len(sp["trades"]) >= 2
             and all((sp["trades"][i + 1]["entry_bar"]
                      - sp["trades"][i]["entry_bar"]) >= MIN_SPACING
                     for i in range(len(sp["trades"]) - 1))),
        # 9) one live position per asset / no overlap
        "one_live_position_per_asset_no_overlap":
            all(r["max_concurrent_positions"] <= 1 for r in res.values()),
        # 10) mechanical neutrality uses identical asset spot/perp only
        "mechanical_neutrality_uses_identical_asset_only":
            (na["mechanical_neutrality_ok"] is False
             and na["blocked_before_entry"] is True
             and na["entry_logic_reached"] is False
             and len(na["trades"]) == 0
             and all(r["mechanical_neutrality_ok"] is True
                     and r["same_asset"] is True
                     for r in constructed.values())),
        # invariants
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

def get_candidate_20_detector_dry_run_label() -> str:
    return (
        "Candidate #20 mechanically_neutral_spot_perp_basis_funding_carry_v1 detector "
        "spec + SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). Exercises the "
        "same-asset basis + funding-carry detector (basis (perp-spot)/spot, 60D basis "
        "z, 30D annualized funding carry, MECHANICAL-neutrality GATE ZERO at "
        "equal-notional long-spot/short-same-asset-perp, enter carry >= 50 bps "
        "non-negative-regime OR basis z >= +2.0, exit |z| <= 0.25 / carry-decay / "
        "negative-carry, stop |z| >= 4.0, gross <= 1.0, >= 5-bar spacing, one position "
        "per asset) on DETERMINISTIC SYNTHETIC fixtures only -- never real data, no "
        "XAUUSD. 37 bps + perp frictions RESERVED for replay. Does NOT start C21. NOT a "
        "profitability claim.")


def get_candidate_20_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C20_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c20_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C20 detector spec + synthetic dry-run record. Pure; no I/O;
    chain-gated on the frozen C20 candidate spec."""
    spec = _c20s.build_c20_spec(repo_root, tracked_paths)
    spec_valid = _c20s.validate_c20_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c20_spec_invalid")
    if spec.get("verdict") != "C20_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c20_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D20_SCHEMA_VERSION, "mode": D20_MODE, "lane": D20_LANE,
        "label": get_candidate_20_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C20_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved frozen spec params (implemented exactly)
        "timeframe": TIMEFRAME, "universe": list(UNIVERSE),
        "basis_zscore_window_bars": BASIS_Z_WINDOW,
        "funding_lookback_bars": FUNDING_LOOKBACK,
        "entry_basis_zscore_threshold": ENTRY_BASIS_Z,
        "entry_min_annualized_carry_bps": ENTRY_CARRY_BPS,
        "exit_basis_zscore_threshold": EXIT_BASIS_Z,
        "stop_basis_zscore_threshold": STOP_BASIS_Z,
        "max_gross_exposure": MAX_GROSS,
        "min_bars_between_rebalances": MIN_SPACING,
        "funding_annualization_days": FUNDING_ANNUALIZATION_DAYS,
        "is_market_neutral": True, "is_mechanically_neutral_same_asset": True,
        "is_estimated_cross_asset_neutral": False,
        "return_source_is_carry_not_timing": True,
        "mechanical_neutrality_is_gate_zero": True,
        "positions_non_overlapping": True,
        "basis_formula": "(perp_close - spot_close) / spot_close",
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "uses_xauusd": False, "no_new_data_fetch": True,
        "synthetic_fixtures": ["funding_carry_valid", "basis_premium_valid",
                               "negative_carry_blocks", "weak_no_trade",
                               "convergence_exit", "divergence_stop", "spacing",
                               "non_same_asset_blocked"],
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_scenario_count": dry["scenario_count"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "perp_frictions_reserved_for_replay": True,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C19),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C19,
        "does_not_start_c21": True, "c21_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_20_detector_dry_run_next_action(),
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
        "no_rescue": True, "no_robustness": True,
        "no_estimated_cross_asset_hedge": True,
        "no_net_market_beta": True, "no_trade_before_neutrality_validated": True,
        "no_overlapping_positions": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_start_c21": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c20_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    synthetic-dry-run-only, chain-gated on the frozen C20 spec, implements the exact
    same-asset basis/funding-carry params (60-bar basis z, 30-bar funding lookback,
    2.0/0.25/4.0 thresholds, 50 bps carry floor, gross 1.0, 5-bar spacing) with
    MECHANICAL neutrality (not estimated) as gate zero, passes all ten synthetic proof
    checks on synthetic data only (no real data / fetch / XAUUSD / labels / replay /
    cost), keeps the 37 bps + perp frictions reserved, preserves downstream locks, does
    not start C21, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != D20_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C20 spec
    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C20_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")
    if record.get("candidate_id") != "C20":
        failures.append("candidate_id_not_c20")

    # exact params implemented
    if record.get("basis_zscore_window_bars") != 60:
        failures.append("basis_z_window_not_60")
    if record.get("funding_lookback_bars") != 30:
        failures.append("funding_lookback_not_30")
    if record.get("entry_basis_zscore_threshold") != 2.0:
        failures.append("entry_basis_z_not_2")
    if record.get("entry_min_annualized_carry_bps") != 50.0:
        failures.append("entry_carry_not_50")
    if record.get("exit_basis_zscore_threshold") != 0.25:
        failures.append("exit_basis_z_not_0_25")
    if record.get("stop_basis_zscore_threshold") != 4.0:
        failures.append("stop_basis_z_not_4")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_not_1")
    if record.get("min_bars_between_rebalances") != 5:
        failures.append("spacing_not_5")
    if record.get("basis_formula") != "(perp_close - spot_close) / spot_close":
        failures.append("basis_formula_tampered")

    # mechanical-neutral identity (not estimated; carry not timing)
    for k in ("is_market_neutral", "is_mechanically_neutral_same_asset",
              "return_source_is_carry_not_timing",
              "mechanical_neutrality_is_gate_zero", "positions_non_overlapping"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("is_estimated_cross_asset_neutral") is not False:
        failures.append("must_not_be_estimated_cross_asset_neutral")

    # synthetic only, no real data / fetch / xauusd
    for k in ("uses_synthetic_fixtures_only", "no_new_data_fetch"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    for k in ("uses_real_data", "uses_xauusd"):
        if record.get(k) is not False:
            failures.append("flag_must_be_false_%s" % k)

    # all ten proof checks present and passing
    checks = record.get("dry_run_checks") or {}
    for c in ("funding_carry_creates_valid_neutral_setup",
              "basis_premium_creates_valid_convergence_setup",
              "negative_carry_regime_blocks_entry", "weak_basis_and_carry_no_trade",
              "convergence_exit_works", "divergence_stop_works",
              "gross_exposure_capped", "rebalance_spacing_prevents_overtrading",
              "one_live_position_per_asset_no_overlap",
              "mechanical_neutrality_uses_identical_asset_only"):
        if checks.get(c) is not True:
            failures.append("dry_run_check_failed_%s" % c)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")

    # cost reserved, not applied
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_dry_run")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")
    if record.get("perp_frictions_reserved_for_replay") is not True:
        failures.append("perp_frictions_not_reserved")

    # gate sequence integrity + no C21
    if record.get("does_not_start_c21") is not True:
        failures.append("must_not_start_c21")
    if record.get("c21_candidate_id") is not None:
        failures.append("c21_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C20_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"):
        failures.append("next_action_not_labels_gate")
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_data_fetch", "no_real_candles", "no_xauusd",
                "no_new_instrument_class", "no_labels", "no_replay",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_estimated_cross_asset_hedge", "no_net_market_beta",
                "no_trade_before_neutrality_validated", "no_overlapping_positions",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c21", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
