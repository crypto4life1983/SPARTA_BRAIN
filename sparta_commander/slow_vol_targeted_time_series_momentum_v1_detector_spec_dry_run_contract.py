"""Candidate #15 -- slow_vol_targeted_time_series_momentum_v1 -- DETECTOR SPEC +
SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C15 detector algorithm and exercises it on SYNTHETIC, in-memory
fixtures only -- never on real market data. The detector reads daily (D1) OHLC
bars for BTC/ETH/SOL plus a W1 regime-context proxy and emits a per-bar target
STATE (long / short / flat) with a volatility-targeted position scale, using slow
time-series momentum + an EMA stack + a vol deadband, with SIGNAL-DRIVEN (non-
fixed-horizon) exits.

It does NOTHING with real data: it does NOT fetch data, NOT read real candles, NOT
label, NOT replay/backtest, NOT compute PnL, NOT write files, NOT stage / commit /
push, and NOT touch any paper / live / broker / order surface. The 37 bps cost
model is RESERVED for the replay gate and is NOT applied here (the dry-run checks
detector BEHAVIOUR, not profitability). Every capability flag is pinned False with
a full scope_locks set. The next gate (real-candle labels) still requires an
explicit human decision.

The synthetic dry-run proves the C15 logic shape:
  * sustained uptrend  -> LONG, one long position held across many bars
                          (demonstrates NON-fixed-horizon holding),
  * sustained downtrend -> SHORT (symmetric long/short, regime-aware),
  * chop/range         -> mostly FLAT (deadband filters whipsaw),
  * higher realized vol -> smaller volatility-targeted position scale.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_spec_contract as _c15  # noqa: E501

D15_SCHEMA_VERSION = 1
D15_MODE = "RESEARCH_ONLY"
D15_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c15.CANDIDATE_ID
CANDIDATE_FAMILY = _c15.CANDIDATE_FAMILY
CANDIDATE_NAME = _c15.CANDIDATE_NAME

SYMBOLS = tuple(_c15.SYMBOLS)
TIMEFRAME = _c15.TIMEFRAME
CONTEXT_TIMEFRAME = _c15.CONTEXT_TIMEFRAME
SPEC_PARAMS = dict(_c15.SPEC_PARAMS)
ALL_IN_ROUND_TRIP_BPS = _c15.ALL_IN_ROUND_TRIP_BPS  # reserved for replay; not used

W1_REGIME_SLOPE_LOOKBACK = 20   # W1 regime-context proxy slope window
SYNTHETIC_BARS = 160            # synthetic fixture length (no real data)

STATE_LONG = "long"
STATE_SHORT = "short"
STATE_FLAT = "flat"
STATE_WARMUP = "warmup"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files", "runs_detector_on_real_data",
    "runs_labels", "runs_replay", "runs_backtest", "computes_pnl",
    "runs_robustness", "runs_portfolio_compute", "fetches_data", "reads_real_data",
    "uses_real_candles", "mutates_data", "stages_data", "auto_commits",
    "auto_pushes", "applies_cost_model", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "uses_one_edit_allowance",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure numeric primitives (no imports beyond typing)
# --------------------------------------------------------------------------- #

def _ema(values: list, span: int) -> list:
    k = 2.0 / (span + 1.0)
    out: list = []
    e = None
    for v in values:
        e = v if e is None else (v * k + e * (1.0 - k))
        out.append(e)
    return out


def _true_range(candles: list) -> list:
    out: list = []
    for i, bar in enumerate(candles):
        if i == 0:
            out.append(bar["high"] - bar["low"])
        else:
            pc = candles[i - 1]["close"]
            out.append(max(bar["high"] - bar["low"], abs(bar["high"] - pc),
                           abs(bar["low"] - pc)))
    return out


def _returns(closes: list) -> list:
    out = [0.0]
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        out.append((closes[i] / prev - 1.0) if prev else 0.0)
    return out


def _rolling_std(xs: list, i: int, win: int) -> float:
    lo = max(0, i - win + 1)
    seg = xs[lo:i + 1]
    if len(seg) < 2:
        return 0.0
    m = sum(seg) / len(seg)
    var = sum((x - m) ** 2 for x in seg) / (len(seg) - 1)
    return var ** 0.5


# --------------------------------------------------------------------------- #
# The C15 detector (pure; operates on whatever candles are passed in)
# --------------------------------------------------------------------------- #

def scan_c15_states(candles: list, params: dict | None = None) -> list:
    """Pure detector. Given D1 OHLC bars, emit a per-bar target state (long /
    short / flat / warmup) with a volatility-targeted position scale and a W1
    regime-context proxy. NO cost model, NO PnL -- behaviour only."""
    p = dict(params or SPEC_PARAMS)
    closes = [b["close"] for b in candles]
    fast = _ema(closes, p["fast_ema_days"])
    slow = _ema(closes, p["slow_ema_days"])
    rets = _returns(closes)
    lookback = p["ts_momentum_lookback_days"]
    volwin = p["realized_vol_lookback_days"]
    dead = p["entry_deadband_vol_mult"]
    max_scale = p["max_position_scale"]
    allow_short = p.get("allow_short", True)
    daily_vol_target = p["vol_target_annualized"] / (365.0 ** 0.5)
    warm = max(p["slow_ema_days"], lookback, volwin, W1_REGIME_SLOPE_LOOKBACK)

    states: list = []
    for i in range(len(candles)):
        if i < warm:
            states.append({"i": i, "state": STATE_WARMUP, "position_scale": 0.0,
                           "momentum": 0.0, "realized_vol": 0.0,
                           "w1_regime": "warmup"})
            continue
        rv = _rolling_std(rets, i, volwin)
        mom = (closes[i] / closes[i - lookback] - 1.0) if closes[i - lookback] else 0.0
        threshold = dead * rv * (lookback ** 0.5)
        # W1 regime-context proxy: price vs slow MA + slow-MA slope sign.
        slope = slow[i] - slow[i - W1_REGIME_SLOPE_LOOKBACK]
        if closes[i] > slow[i] and slope > 0:
            w1 = "bull"
        elif closes[i] < slow[i] and slope < 0:
            w1 = "bear"
        else:
            w1 = "chop"
        long_ok = (fast[i] > slow[i] and mom > threshold and w1 != "bear")
        short_ok = (allow_short and fast[i] < slow[i] and mom < -threshold
                    and w1 != "bull")
        if long_ok:
            st = STATE_LONG
        elif short_ok:
            st = STATE_SHORT
        else:
            st = STATE_FLAT
        if st == STATE_FLAT or rv <= 0:
            scale = 0.0 if st == STATE_FLAT else max_scale
        else:
            scale = min(max_scale, daily_vol_target / rv)
        states.append({"i": i, "state": st, "position_scale": round(scale, 6),
                       "momentum": round(mom, 6), "realized_vol": round(rv, 8),
                       "w1_regime": w1})
    return states


def summarize_states(states: list) -> dict:
    """Pure rollup of detector behaviour over the evaluated (non-warmup) bars."""
    ev = [s for s in states if s["state"] != STATE_WARMUP]
    counts = {STATE_LONG: 0, STATE_SHORT: 0, STATE_FLAT: 0}
    for s in ev:
        counts[s["state"]] += 1
    # longest consecutive run per active state (non-fixed-horizon evidence)
    max_run = {STATE_LONG: 0, STATE_SHORT: 0}
    cur_state, cur_len = None, 0
    for s in ev:
        if s["state"] == cur_state and s["state"] in max_run:
            cur_len += 1
        else:
            cur_state, cur_len = s["state"], 1
        if s["state"] in max_run:
            max_run[s["state"]] = max(max_run[s["state"]], cur_len)
    active_scales = [s["position_scale"] for s in ev if s["state"] != STATE_FLAT]
    avg_active_scale = (sum(active_scales) / len(active_scales)
                        if active_scales else 0.0)
    regimes = {"bull": 0, "bear": 0, "chop": 0}
    for s in ev:
        if s["w1_regime"] in regimes:
            regimes[s["w1_regime"]] += 1
    n = len(ev)
    return {
        "evaluated_bars": n,
        "counts": counts,
        "flat_share": round(counts[STATE_FLAT] / n, 6) if n else 0.0,
        "max_consecutive_long": max_run[STATE_LONG],
        "max_consecutive_short": max_run[STATE_SHORT],
        "avg_active_position_scale": round(avg_active_scale, 6),
        "regime_counts": regimes,
    }


# --------------------------------------------------------------------------- #
# Synthetic fixtures (deterministic; NO real data)
# --------------------------------------------------------------------------- #

def _trend_path(n: int, drift: float, noise: float, start: float = 100.0) -> list:
    """Deterministic OHLC path: per-bar return = drift +/- noise (alternating)."""
    closes = [start]
    for i in range(1, n):
        r = drift + (noise if i % 2 == 0 else -noise)
        closes.append(closes[-1] * (1.0 + r))
    candles: list = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i > 0 else c
        hi = max(o, c) * (1.0 + 0.0005)
        lo = min(o, c) * (1.0 - 0.0005)
        candles.append({"open": o, "high": hi, "low": lo, "close": c})
    return candles


def build_synthetic_fixtures() -> dict:
    """Deterministic synthetic fixtures for the dry-run. NO real candles."""
    return {
        "uptrend_low_vol": _trend_path(SYNTHETIC_BARS, drift=0.006, noise=0.001),
        "uptrend_high_vol": _trend_path(SYNTHETIC_BARS, drift=0.006, noise=0.020),
        "downtrend": _trend_path(SYNTHETIC_BARS, drift=-0.006, noise=0.001),
        "chop": _trend_path(SYNTHETIC_BARS, drift=0.0, noise=0.010),
    }


def run_synthetic_dry_run() -> dict:
    """Pure: run the detector across all synthetic fixtures, return behaviour
    summaries + the pass/fail of each expected property."""
    fx = build_synthetic_fixtures()
    summ = {k: summarize_states(scan_c15_states(v)) for k, v in fx.items()}

    up = summ["uptrend_low_vol"]
    up_hi = summ["uptrend_high_vol"]
    dn = summ["downtrend"]
    ch = summ["chop"]

    checks = {
        # sustained uptrend -> predominantly long, no shorts
        "uptrend_is_long": up["counts"][STATE_LONG] > 0
            and up["counts"][STATE_SHORT] == 0,
        # NON-fixed-horizon: a single long run spans many bars (> any fixed horizon)
        "uptrend_non_fixed_horizon_hold": up["max_consecutive_long"] >= 20,
        # symmetric long/short + regime-aware: downtrend -> short, no longs
        "downtrend_is_short": dn["counts"][STATE_SHORT] > 0
            and dn["counts"][STATE_LONG] == 0,
        # chop -> mostly flat (deadband filters whipsaw)
        "chop_mostly_flat": ch["flat_share"] >= 0.70,
        # volatility targeting: higher realized vol -> smaller position scale
        "vol_targeting_scales_down": (
            up_hi["avg_active_position_scale"]
            < up["avg_active_position_scale"]),
        # low-vol scale is capped at the max position scale
        "low_vol_scale_capped": abs(
            up["avg_active_position_scale"] - SPEC_PARAMS["max_position_scale"]
        ) < 1e-6,
        # W1 regime context tracks the fixture intent
        "regime_context_bull_in_uptrend":
            up["regime_counts"]["bull"] > up["regime_counts"]["bear"],
        "regime_context_bear_in_downtrend":
            dn["regime_counts"]["bear"] > dn["regime_counts"]["bull"],
    }
    return {"summaries": summ, "checks": checks,
            "all_checks_pass": all(checks.values())}


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_15_detector_dry_run_label() -> str:
    return (
        "Candidate #15 slow_vol_targeted_time_series_momentum_v1 detector spec + "
        "SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). Exercises the slow "
        "vol-targeted time-series momentum detector on DETERMINISTIC SYNTHETIC "
        "fixtures only -- never real data. Proves long-in-uptrend, short-in-"
        "downtrend (symmetric, regime-aware), flat-in-chop, vol-targeted sizing, "
        "and non-fixed-horizon holding. 37 bps cost model RESERVED for the replay "
        "gate (NOT applied here). NO data fetch, NO real candles, NO labels, NO "
        "replay, NO paper/live. NOT a profitability claim.")


def get_candidate_15_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C15_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c15_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C15 detector spec + synthetic dry-run record. Pure; no
    I/O; chain-gated on the frozen C15 family spec."""
    spec = _c15.build_c15_spec(repo_root, tracked_paths)
    spec_valid = _c15.validate_c15_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c15_spec_invalid")
    if spec.get("verdict") != "C15_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c15_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D15_SCHEMA_VERSION, "mode": D15_MODE, "lane": D15_LANE,
        "label": get_candidate_15_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C15_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved C15 logic
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "context_timeframe": CONTEXT_TIMEFRAME,
        "spec_params": dict(SPEC_PARAMS),
        "is_time_series_momentum": True, "is_volatility_targeted": True,
        "is_regime_aware": True, "is_fixed_horizon": False,
        "uses_w1_regime_context": True,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True,
        "uses_real_data": False,
        "synthetic_bars_per_fixture": SYNTHETIC_BARS,
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_summaries": dry["summaries"],
        # cost model reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_15_detector_dry_run_next_action(),
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_real_candles": True,
        "no_labels": True, "no_replay": True, "no_backtest": True,
        "no_pnl": True, "no_cost_application": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_one_edit_invocation": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c15_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the dry-run is research-only,
    synthetic-only (no real data / no cost application), chain-gated on the frozen
    C15 spec, preserves the C15 logic (TSMOM / vol-targeted / regime-aware / non-
    fixed-horizon / W1 context), all synthetic behaviour checks pass, downstream
    gates locked, and every capability flag is False."""
    failures: list = []
    if record.get("mode") != D15_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    # chain gate
    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C15_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")

    # synthetic only / no real data / no cost application
    for k in ("uses_synthetic_fixtures_only", "cost_model_reserved_for_replay",
              "uses_w1_regime_context"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("uses_real_data") is not False:
        failures.append("uses_real_data_set")
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")

    # preserved C15 logic identity
    if record.get("is_fixed_horizon") is not False:
        failures.append("must_not_be_fixed_horizon")
    for k in ("is_time_series_momentum", "is_volatility_targeted",
              "is_regime_aware"):
        if record.get(k) is not True:
            failures.append("identity_flag_off_%s" % k)
    if list(record.get("symbols") or []) != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        failures.append("symbols_tampered")
    if record.get("timeframe") != "D1":
        failures.append("timeframe_tampered")

    # all synthetic behaviour checks pass
    checks = record.get("dry_run_checks") or {}
    for k in ("uptrend_is_long", "uptrend_non_fixed_horizon_hold",
              "downtrend_is_short", "chop_mostly_flat",
              "vol_targeting_scales_down", "low_vol_scale_capped",
              "regime_context_bull_in_uptrend", "regime_context_bear_in_downtrend"):
        if checks.get(k) is not True:
            failures.append("dry_run_check_failed_%s" % k)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")

    # downstream gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_real_data_access", "no_real_candles",
                "no_labels", "no_replay", "no_backtest", "no_pnl",
                "no_cost_application", "no_commit", "no_push", "no_auto_commit",
                "no_auto_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_one_edit_invocation"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
