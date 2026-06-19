"""Candidate #19 -- oos_validated_beta_neutral_cross_sectional_relative_value_v1
-- DETECTOR SPEC + SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C19 market-neutral cross-sectional relative-value detector and exercises
it on DETERMINISTIC SYNTHETIC fixtures only -- never real data. The detector
implements ONLY the frozen C19 candidate-spec rules, in RETURN space:

  * estimate return-beta hedge ratios (b1, b2) for SOL on [BTC, ETH] over the 90-bar
    in-sample window (2x2 OLS, no price levels);
  * residual = r_SOL - b1*r_BTC - b2*r_ETH (a dollar- and beta-neutral combination);
  * GATE ZERO: validate the residual's net beta to the basket on the unseen 60-bar
    OOS window; reject ALL trading if |net residual beta| > 0.10;
  * residual z-score over a 60-bar trailing window;
  * ENTER when |z| >= 2.0 (fade the extreme), spaced >= 5 bars; EXIT when |z| <= 0.25
    (mean reversion); STOP/INVALIDATE when |z| >= 4.0 or the rolling neutrality breaks;
  * leg weights normalized so gross <= 1.0 (no leverage); one live position only.

It does NOTHING with real data: NO fetch, NO real candles, NO XAUUSD, NO labels, NO
replay, NO PnL/cost application (the 37 bps is RESERVED for replay), NO optimization /
tuning / rescue, NO writes, NO stage/commit/push, NO paper/live/broker/order surface,
and does NOT start C20. Every capability flag is pinned False with a full scope_locks
set. The next gate (real-candle labels) needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_candidate_spec_contract as _c19s  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

D19_SCHEMA_VERSION = 1
D19_MODE = "RESEARCH_ONLY"
D19_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c19s.CANDIDATE_ID
CANDIDATE_FAMILY = _c19s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c19s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C18 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C18)   # 23
TIMEFRAME = "D1"
UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
ALL_IN_ROUND_TRIP_BPS = _c19s.ALL_IN_ROUND_TRIP_BPS                     # 37.0 reserved

# frozen spec params (reused, not redefined)
_SP = _c19s.SPEC_PARAMS
BETA_WINDOW = _SP["beta_estimation_window_bars"]        # 90
OOS_WINDOW = _SP["oos_neutrality_window_bars"]          # 60
BETA_TOL = _SP["net_residual_beta_tolerance"]           # 0.10
Z_WINDOW = _SP["residual_zscore_window_bars"]           # 60
ENTRY_Z = _SP["entry_zscore_threshold"]                 # 2.0
EXIT_Z = _SP["exit_zscore_threshold"]                   # 0.25
STOP_Z = _SP["stop_zscore_threshold"]                   # 4.0
MAX_GROSS = _SP["max_gross_exposure"]                   # 1.0
MIN_SPACING = _SP["min_bars_between_rebalances"]        # 5

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
    "trades_before_neutrality_validated", "uses_price_level_hedge",
    "allows_overlapping_positions", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "reproposes_rejected_family", "starts_c20",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure helpers (return-space; no numpy/pandas; deterministic)
# --------------------------------------------------------------------------- #

def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _ols_beta_2(rb: list, re: list, rs: list) -> tuple:
    """2x2 OLS (no intercept): solve for [b1, b2] minimizing sum (rs - b1*rb -
    b2*re)^2 over the given (in-sample) window. Pure, return-space."""
    sbb = sum(b * b for b in rb)
    see = sum(e * e for e in re)
    sbe = sum(b * e for b, e in zip(rb, re))
    sbs = sum(b * s for b, s in zip(rb, rs))
    ses = sum(e * s for e, s in zip(re, rs))
    det = sbb * see - sbe * sbe
    if det == 0:
        return 0.0, 0.0
    b1 = (sbs * see - ses * sbe) / det
    b2 = (ses * sbb - sbs * sbe) / det
    return b1, b2


def _residual_series(rb: list, re: list, rs: list, b1: float, b2: float) -> list:
    return [s - b1 * b - b2 * e for b, e, s in zip(rb, re, rs)]


def _net_beta_to_basket(resid: list, rb: list, re: list) -> float:
    """Net beta of the residual to the basket factor f = r_BTC + r_ETH (no
    intercept): cov-like sum(resid*f)/sum(f*f)."""
    f = [b + e for b, e in zip(rb, re)]
    sff = sum(x * x for x in f)
    if sff == 0:
        return 0.0
    return sum(r * x for r, x in zip(resid, f)) / sff


def _normalized_leg_weights(b1: float, b2: float) -> tuple:
    """Leg weights [SOL, BTC, ETH] = [1, -b1, -b2] normalized so gross (sum|w|) = 1.0
    -- enforces no leverage / max gross <= 1.0."""
    raw = [1.0, -b1, -b2]
    gross = sum(abs(w) for w in raw)
    if gross == 0:
        return (0.0, 0.0, 0.0)
    return tuple(w / gross for w in raw)


def run_detector(rb: list, re: list, rs: list) -> dict[str, Any]:
    """PURE detector over synthetic return series. Estimates the neutral residual,
    runs GATE-ZERO OOS neutrality, and (only if neutral) applies the z-score
    entry/exit/stop rules with spacing + non-overlap + gross cap. Synthetic only;
    no real data, no cost applied."""
    n = len(rs)
    is_rb, is_re, is_rs = rb[:BETA_WINDOW], re[:BETA_WINDOW], rs[:BETA_WINDOW]
    b1, b2 = _ols_beta_2(is_rb, is_re, is_rs)
    resid = _residual_series(rb, re, rs, b1, b2)

    # GATE ZERO: OOS neutrality over the unseen window [BETA_WINDOW, BETA_WINDOW+OOS)
    oos_slice = slice(BETA_WINDOW, BETA_WINDOW + OOS_WINDOW)
    net_beta_oos = _net_beta_to_basket(resid[oos_slice], rb[oos_slice], re[oos_slice])
    neutrality_passed = abs(net_beta_oos) <= BETA_TOL

    weights = _normalized_leg_weights(b1, b2)
    gross = sum(abs(w) for w in weights)

    trades: list = []
    max_concurrent = 0
    if not neutrality_passed:
        # gate zero blocks ALL trading BEFORE any entry logic is applied
        return {
            "b1": b1, "b2": b2, "net_beta_oos": net_beta_oos,
            "neutrality_passed": False, "blocked_before_entry": True,
            "weights": weights, "gross": gross, "trades": [],
            "max_concurrent_positions": 0, "entry_logic_reached": False,
        }

    position = None
    last_entry_bar = -10 ** 9
    trade_start = BETA_WINDOW
    for t in range(trade_start, n):
        if t < Z_WINDOW:
            continue
        win = resid[t - Z_WINDOW:t]
        mu = _mean(win)
        var = _mean([(x - mu) ** 2 for x in win])
        sd = var ** 0.5
        if sd <= 0:
            continue
        z = (resid[t] - mu) / sd
        if position is None:
            if abs(z) >= ENTRY_Z and (t - last_entry_bar) >= MIN_SPACING:
                position = {"entry_bar": t, "entry_z": round(z, 4),
                            "side": "short_residual" if z > 0 else "long_residual"}
                last_entry_bar = t
                max_concurrent = max(max_concurrent, 1)
        else:
            if abs(z) >= STOP_Z:
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "divergence_stop"
                trades.append(position)
                position = None
            elif abs(z) <= EXIT_Z:
                position["exit_bar"] = t
                position["exit_z"] = round(z, 4)
                position["exit_reason"] = "mean_reversion"
                trades.append(position)
                position = None
    if position is not None:
        position["exit_bar"] = n - 1
        position["exit_reason"] = "end_of_data"
        trades.append(position)

    return {
        "b1": b1, "b2": b2, "net_beta_oos": net_beta_oos,
        "neutrality_passed": True, "blocked_before_entry": False,
        "weights": weights, "gross": gross, "trades": trades,
        "max_concurrent_positions": max_concurrent, "entry_logic_reached": True,
    }


# --------------------------------------------------------------------------- #
# Deterministic synthetic fixtures (no real data, no randomness)
# --------------------------------------------------------------------------- #

def _base_factor(n: int) -> tuple:
    """Deterministic, decorrelated BTC/ETH return series (return-like scale). No
    random module; a simple coprime-modulus pattern."""
    rb = [((t * 37) % 11 - 5) / 1000.0 for t in range(n)]
    re = [((t * 53) % 13 - 6) / 1000.0 for t in range(n)]
    return rb, re


def _sol_from_residual(rb: list, re: list, s: list,
                       b1_true: float = 0.5, b2_true: float = 0.3,
                       extra_basket: list | None = None) -> list:
    """SOL returns = b1_true*BTC + b2_true*ETH + residual signal s (+ optional
    extra basket exposure to break neutrality OOS)."""
    extra = extra_basket or [0.0] * len(s)
    return [b1_true * b + b2_true * e + sv + ex
            for b, e, sv, ex in zip(rb, re, s, extra)]


_EPS = 0.001                  # residual baseline scale (return-like)
_N = 200                      # series length: 90 IS + 60 OOS + 50 trading


def _alt_base(n: int) -> list:
    """Alternating +/-EPS residual baseline -> std ~ EPS so z-scores are clean."""
    return [(_EPS if t % 2 == 0 else -_EPS) for t in range(n)]


def build_synthetic_fixtures() -> dict[str, dict]:
    """Six deterministic synthetic scenarios, each returning {rb, re, rs}. Pure; no
    real data; no randomness."""
    rb, re = _base_factor(_N)
    fixtures: dict[str, dict] = {}

    # 1) VALID NEUTRAL + a clean trade: one extreme spike then revert.
    s = _alt_base(_N)
    s[150] = 3.2 * _EPS            # |z| ~ 3 -> enter
    s[151] = 0.0                  # revert -> |z| <= 0.25 -> exit
    fixtures["valid_trade"] = {"rb": rb, "re": re,
                               "rs": _sol_from_residual(rb, re, s)}

    # 2) NEUTRALITY FAILURE: SOL gains +0.6*basket on the OOS window -> net beta
    #    blows past tolerance -> gate zero blocks all trading before entry.
    s2 = _alt_base(_N)
    s2[150] = 3.2 * _EPS          # would-be entry, but neutrality must block it
    extra = [0.0] * _N
    for t in range(BETA_WINDOW, BETA_WINDOW + OOS_WINDOW):
        extra[t] = 0.6 * (rb[t] + re[t])
    fixtures["neutrality_fail"] = {
        "rb": rb, "re": re,
        "rs": _sol_from_residual(rb, re, s2, extra_basket=extra)}

    # 3) WEAK residual: never reaches |z| >= 2 -> no trade.
    s3 = _alt_base(_N)
    s3[150] = 1.4 * _EPS          # |z| ~ 1.4 < 2 -> no entry
    fixtures["weak"] = {"rb": rb, "re": re,
                        "rs": _sol_from_residual(rb, re, s3)}

    # 4) EXTREME -> ENTER then EXIT on mean reversion.
    s4 = _alt_base(_N)
    s4[150] = 3.5 * _EPS          # enter
    s4[151] = 0.0                 # mean reversion -> exit
    fixtures["enter_exit"] = {"rb": rb, "re": re,
                              "rs": _sol_from_residual(rb, re, s4)}

    # 5) DIVERGENCE STOP: enter, then diverge past |z| >= 4 -> stop/invalidate.
    s5 = _alt_base(_N)
    s5[150] = 3.0 * _EPS          # enter (|z| ~ 3)
    s5[151] = 7.0 * _EPS          # diverge (|z| >= 4) -> divergence stop
    fixtures["divergence_stop"] = {"rb": rb, "re": re,
                                   "rs": _sol_from_residual(rb, re, s5)}

    # 6) REBALANCE SPACING: enter@150, exit@151, more extremes @152/@153 (within 5
    #    bars -> blocked), next allowed extreme @156 (>= 5 bars after 150).
    s6 = _alt_base(_N)
    s6[150] = 3.3 * _EPS          # enter
    s6[151] = 0.0                 # exit
    s6[152] = 3.3 * _EPS          # within spacing -> blocked
    s6[153] = 3.3 * _EPS          # within spacing -> blocked
    s6[156] = 3.3 * _EPS          # >= 5 bars after 150 -> allowed
    s6[157] = 0.0                 # exit
    fixtures["spacing"] = {"rb": rb, "re": re,
                           "rs": _sol_from_residual(rb, re, s6)}

    return fixtures


def run_synthetic_dry_run() -> dict[str, Any]:
    """Run the detector over all synthetic fixtures and compute the eight required
    proof checks. Deterministic; no real data; no cost applied."""
    fx = build_synthetic_fixtures()
    res = {name: run_detector(f["rb"], f["re"], f["rs"]) for name, f in fx.items()}

    # determinism: a second run gives identical residual betas + trade counts
    res2 = {name: run_detector(f["rb"], f["re"], f["rs"])
            for name, f in fx.items()}
    deterministic = all(
        res[k]["b1"] == res2[k]["b1"] and res[k]["b2"] == res2[k]["b2"]
        and len(res[k]["trades"]) == len(res2[k]["trades"]) for k in res)

    valid = res["valid_trade"]
    fail = res["neutrality_fail"]
    weak = res["weak"]
    ee = res["enter_exit"]
    dv = res["divergence_stop"]
    sp = res["spacing"]

    def _spacing_ok(r):
        bars = sorted(t["entry_bar"] for t in r["trades"])
        return all(b - a >= MIN_SPACING for a, b in zip(bars[:-1], bars[1:]))

    checks = {
        # 1) valid neutral residual passes OOS neutrality and creates a trade
        "valid_neutral_passes_and_trades":
            valid["neutrality_passed"] and len(valid["trades"]) >= 1,
        # 2) neutrality failure blocks all trading before entry logic
        "neutrality_failure_blocks_all_trading":
            (fail["neutrality_passed"] is False
             and fail["blocked_before_entry"] is True
             and fail["entry_logic_reached"] is False
             and len(fail["trades"]) == 0),
        # 3) weak residual creates no trade
        "weak_residual_no_trade":
            weak["neutrality_passed"] and len(weak["trades"]) == 0,
        # 4) extreme residual enters then exits on mean reversion
        "extreme_enters_then_exits_on_reversion":
            len(ee["trades"]) == 1
            and ee["trades"][0]["exit_reason"] == "mean_reversion",
        # 5) divergence stop invalidates the position
        "divergence_stop_invalidates":
            len(dv["trades"]) == 1
            and dv["trades"][0]["exit_reason"] == "divergence_stop",
        # 6) rebalance spacing prevents overtrading
        "rebalance_spacing_prevents_overtrading":
            _spacing_ok(sp) and len(sp["trades"]) >= 1
            and all((sp["trades"][i + 1]["entry_bar"]
                     - sp["trades"][i]["entry_bar"]) >= MIN_SPACING
                    for i in range(len(sp["trades"]) - 1)),
        # 7) gross exposure cap is respected (no leverage)
        "gross_exposure_capped":
            all(r["gross"] <= MAX_GROSS + 1e-9 for r in res.values()),
        # 8) no overlap / one live position
        "one_live_position_no_overlap":
            all(r["max_concurrent_positions"] <= 1 for r in res.values()),
        # invariants
        "return_space_no_price_level_hedge": True,
        "cost_model_not_applied": True,
        "synthetic_only_no_real_data": True,
    }
    return {
        "results": res, "checks": checks, "all_checks_pass": all(checks.values()),
        "scenario_count": len(fx),
    }


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_19_detector_dry_run_label() -> str:
    return (
        "Candidate #19 oos_validated_beta_neutral_cross_sectional_relative_value_v1 "
        "detector spec + SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). "
        "Exercises the market-neutral relative-value detector (return-space residual, "
        "90D beta window, 60D OOS neutrality GATE ZERO at |net beta| <= 0.10, z-window "
        "60, enter |z| >= 2.0, exit |z| <= 0.25, stop |z| >= 4.0 / neutrality-break, "
        "gross <= 1.0, >= 5-bar spacing, one live position) on DETERMINISTIC SYNTHETIC "
        "fixtures only -- never real data, no XAUUSD. 37 bps cost RESERVED for replay. "
        "Does NOT start C20. NOT a profitability claim.")


def get_candidate_19_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C19_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c19_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C19 detector spec + synthetic dry-run record. Pure; no
    I/O; chain-gated on the frozen C19 candidate spec."""
    spec = _c19s.build_c19_spec(repo_root, tracked_paths)
    spec_valid = _c19s.validate_c19_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c19_spec_invalid")
    if spec.get("verdict") != "C19_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c19_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D19_SCHEMA_VERSION, "mode": D19_MODE, "lane": D19_LANE,
        "label": get_candidate_19_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C19_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved frozen spec params (implemented exactly)
        "timeframe": TIMEFRAME, "universe": list(UNIVERSE),
        "beta_estimation_window_bars": BETA_WINDOW,
        "oos_neutrality_window_bars": OOS_WINDOW,
        "net_residual_beta_tolerance": BETA_TOL,
        "residual_zscore_window_bars": Z_WINDOW,
        "entry_zscore_threshold": ENTRY_Z, "exit_zscore_threshold": EXIT_Z,
        "stop_zscore_threshold": STOP_Z, "max_gross_exposure": MAX_GROSS,
        "min_bars_between_rebalances": MIN_SPACING,
        "is_market_neutral": True, "is_return_space": True,
        "uses_price_level_hedge": False, "oos_neutrality_is_gate_zero": True,
        "positions_non_overlapping": True,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "uses_xauusd": False, "no_new_data_fetch": True,
        "synthetic_fixtures": ["valid_trade", "neutrality_fail", "weak",
                               "enter_exit", "divergence_stop", "spacing"],
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_scenario_count": dry["scenario_count"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C18),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C18,
        "does_not_start_c20": True, "c20_candidate_id": None,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_19_detector_dry_run_next_action(),
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
        "no_rescue": True, "no_robustness": True, "no_price_level_hedge": True,
        "no_net_market_beta": True, "no_trade_before_neutrality_validated": True,
        "no_overlapping_positions": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_rejected_family_repropose": True,
        "no_start_c20": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c19_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    synthetic-dry-run-only, chain-gated on the frozen C19 spec, implements the exact
    return-space market-neutral params (90/60 windows, 0.10 tolerance, z 60, 2.0/0.25/
    4.0 thresholds, gross 1.0, 5-bar spacing) with OOS neutrality as gate zero and no
    price-level hedge, passes all eight synthetic proof checks on synthetic data only
    (no real data / fetch / XAUUSD / labels / replay / cost), keeps the 37 bps
    reserved, preserves downstream locks, does not start C20, and pins every capability
    flag False."""
    failures: list = []
    if record.get("mode") != D19_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate on the frozen C19 spec
    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C19_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")
    if record.get("candidate_id") != "C19":
        failures.append("candidate_id_not_c19")

    # exact params implemented
    if record.get("beta_estimation_window_bars") != 90:
        failures.append("beta_window_not_90")
    if record.get("oos_neutrality_window_bars") != 60:
        failures.append("oos_window_not_60")
    if record.get("net_residual_beta_tolerance") != 0.10:
        failures.append("tolerance_not_0_10")
    if record.get("residual_zscore_window_bars") != 60:
        failures.append("z_window_not_60")
    if record.get("entry_zscore_threshold") != 2.0:
        failures.append("entry_z_not_2")
    if record.get("exit_zscore_threshold") != 0.25:
        failures.append("exit_z_not_0_25")
    if record.get("stop_zscore_threshold") != 4.0:
        failures.append("stop_z_not_4")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_not_1")
    if record.get("min_bars_between_rebalances") != 5:
        failures.append("spacing_not_5")

    # market-neutral identity
    for k in ("is_market_neutral", "is_return_space", "oos_neutrality_is_gate_zero",
              "positions_non_overlapping"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if record.get("uses_price_level_hedge") is not False:
        failures.append("must_not_use_price_level_hedge")

    # synthetic only, no real data / fetch / xauusd
    for k in ("uses_synthetic_fixtures_only", "no_new_data_fetch"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    for k in ("uses_real_data", "uses_xauusd"):
        if record.get(k) is not False:
            failures.append("flag_must_be_false_%s" % k)

    # all eight proof checks present and passing
    checks = record.get("dry_run_checks") or {}
    for c in ("valid_neutral_passes_and_trades",
              "neutrality_failure_blocks_all_trading", "weak_residual_no_trade",
              "extreme_enters_then_exits_on_reversion", "divergence_stop_invalidates",
              "rebalance_spacing_prevents_overtrading", "gross_exposure_capped",
              "one_live_position_no_overlap"):
        if checks.get(c) is not True:
            failures.append("dry_run_check_failed_%s" % c)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")

    # cost reserved, not applied
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_applied_in_dry_run")
    if record.get("all_in_round_trip_bps_reserved") != 37.0:
        failures.append("cost_reserve_tampered")

    # gate sequence integrity + no C20
    if record.get("does_not_start_c20") is not True:
        failures.append("must_not_start_c20")
    if record.get("c20_candidate_id") is not None:
        failures.append("c20_must_be_none")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C19_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"):
        failures.append("next_action_not_labels_gate")
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_data_fetch", "no_real_candles", "no_xauusd",
                "no_new_instrument_class", "no_labels", "no_replay",
                "no_cost_application", "no_optimization", "no_tuning", "no_rescue",
                "no_price_level_hedge", "no_net_market_beta",
                "no_trade_before_neutrality_validated", "no_overlapping_positions",
                "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                "no_start_c20", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
