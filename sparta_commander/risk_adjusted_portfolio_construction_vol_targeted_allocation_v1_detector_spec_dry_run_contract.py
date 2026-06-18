"""Candidate #17 -- risk_adjusted_portfolio_construction_vol_targeted_allocation_v1
-- DETECTOR SPEC + SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C17 portfolio ALLOCATOR (this family has no entry/exit "detector" --
it continuously sizes a long/flat BTC/ETH/SOL basket by RISK) and exercises it on
DETERMINISTIC SYNTHETIC fixtures only -- never real data. Each rebalance the
allocator: estimates per-asset realized volatility over a trailing window, forms
inverse-volatility / equal-risk-contribution (risk-parity) weights, scales gross
exposure toward a constant volatility target (capped at 1.0 -- long/flat, no
shorting, no leverage above the cap), and rebalances on a weekly cadence with a
no-trade band that suppresses churn. There are NO directional entry/exit signals.

It does NOTHING with real data: NO fetch, NO real candles, NO labels, NO replay,
NO PnL / cost application (the 37 bps all-in is RESERVED for replay), NO
optimization, NO writes, NO stage/commit/push, NO paper/live/broker/order surface.
Every capability flag is pinned False with a full scope_locks set. The next gate
(real-candle labels) needs an explicit human decision.

The synthetic dry-run proves: deterministic inverse-vol weights that order BTC >
ETH > SOL (the lower-vol asset gets more weight); long-only weights (no shorting);
gross exposure never above the 1.0 cap; vol-targeting that scales gross DOWN in a
high-vol regime and is CAPPED at 1.0 in a calm regime (no leverage); a weekly
rebalance cadence with a no-trade band that skips churn in a stable regime; average
weekly turnover within the spec cap; near-equal risk contributions (risk parity);
the BTC/ETH/SOL universe only; and that the cost model is NOT applied here.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_candidate_spec_contract as _c17s  # noqa: E501

D17_SCHEMA_VERSION = 1
D17_MODE = "RESEARCH_ONLY"
D17_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c17s.CANDIDATE_ID
CANDIDATE_FAMILY = _c17s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c17s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C16 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)
ASSETS = tuple(_c17s.SYMBOLS)                         # BTCUSD, ETHUSD, SOLUSD
TIMEFRAME = _c17s.TIMEFRAME                           # D1
ALL_IN_ROUND_TRIP_BPS = _c17s.ALL_IN_ROUND_TRIP_BPS  # 37.0 (reserved for replay)

# Allocator parameters, read from the frozen spec (declared, not fitted).
_SP = _c17s.SPEC_PARAMS
VOL_LOOKBACK = _SP["realized_vol_lookback_days"]          # 30
COV_LOOKBACK = _SP["covariance_lookback_days"]            # 60
TARGET_VOL = _SP["target_portfolio_vol_annualized"]       # 0.20
MAX_GROSS = _SP["max_gross_exposure"]                     # 1.0
MIN_GROSS = _SP["min_gross_exposure"]                     # 0.0
NO_TRADE_BAND = _SP["no_trade_band_pct"]                  # 0.05
MAX_AVG_WEEKLY_TURNOVER = _SP["max_avg_weekly_turnover"]  # 0.20
REBALANCE_EVERY_DAYS = 7                                  # weekly

ANNUALIZATION_DAYS = 365                                  # crypto trades daily
_ANN = ANNUALIZATION_DAYS ** 0.5
SYNTHETIC_BARS = 220
# tolerance for "risk contributions near equal" (max/min ratio under risk parity)
RC_EQUALITY_RATIO_MAX = 2.0

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files",
    "runs_detector_on_real_data", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "applies_cost_model", "optimizes_parameters", "runs_robustness",
    "fetches_data", "reads_real_data", "uses_real_candles", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "uses_leverage_above_cap", "shorts", "paper_trading",
    "live_trading", "deploys_capital", "is_directional_timing_signal",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure numeric primitives
# --------------------------------------------------------------------------- #

def _ln(x: float) -> float:
    """Pure-Python natural log (no imports): 2*atanh((x-1)/(x+1)) with range
    reduction by factors of e."""
    if x <= 0:
        raise ValueError("ln domain")
    E = 2.718281828459045235360287
    k = 0
    while x > 1.5:
        x /= E
        k += 1
    while x < 0.5:
        x *= E
        k -= 1
    t = (x - 1.0) / (x + 1.0)
    t2 = t * t
    s = 0.0
    term = t
    n = 1
    while n < 60:
        s += term / n
        term *= t2
        n += 2
    return 2.0 * s + k


def _log_returns(closes: list) -> list:
    return [_ln(closes[i] / closes[i - 1]) for i in range(1, len(closes))]


def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((v - m) ** 2 for v in xs) / (len(xs) - 1)) ** 0.5


def _ann_vol(rets: list) -> float:
    """Annualized realized volatility of a daily-return series."""
    return _std(rets) * _ANN


def _inverse_vol_weights(vols: dict) -> dict:
    """Inverse-volatility (risk-parity proxy) weights, normalized to sum 1.0."""
    inv = {a: (1.0 / v if v > 0 else 0.0) for a, v in vols.items()}
    tot = sum(inv.values())
    if tot <= 0:
        n = len(vols)
        return {a: 1.0 / n for a in vols}
    return {a: inv[a] / tot for a in vols}


def _cov_matrix(rets: dict, assets: list, end: int, window: int) -> list:
    seg = {a: rets[a][end - window:end] for a in assets}
    means = {a: _mean(seg[a]) for a in assets}
    m = len(assets)
    cov = [[0.0] * m for _ in range(m)]
    L = window
    for x in range(m):
        for y in range(m):
            ax, ay = assets[x], assets[y]
            cov[x][y] = sum((seg[ax][t] - means[ax]) * (seg[ay][t] - means[ay])
                            for t in range(L)) / (L - 1)
    return cov


def _risk_contributions(weights: dict, cov: list, assets: list) -> dict:
    """Per-asset risk contribution RC_i = w_i (Sigma w)_i / (w' Sigma w)."""
    m = len(assets)
    w = [weights[a] for a in assets]
    sigma_w = [sum(cov[x][y] * w[y] for y in range(m)) for x in range(m)]
    port_var = sum(w[x] * sigma_w[x] for x in range(m))
    if port_var <= 0:
        return {a: 0.0 for a in assets}
    return {assets[x]: (w[x] * sigma_w[x]) / port_var for x in range(m)}


# --------------------------------------------------------------------------- #
# The allocator (continuous risk-based sizing; NO entry/exit signal)
# --------------------------------------------------------------------------- #

def allocate_c17(closes_by_asset: dict) -> dict:
    """Pure portfolio allocator. At each weekly rebalance: inverse-vol weights,
    vol-target gross scaling capped at MAX_GROSS, no-trade-band churn suppression.
    Returns the per-checkpoint diagnostics. NO cost model, NO PnL -- behaviour
    only."""
    assets = list(ASSETS)
    rets = {a: _log_returns(closes_by_asset[a]) for a in assets}
    n = len(rets[assets[0]])
    start = max(VOL_LOOKBACK, COV_LOOKBACK)

    checkpoints: list = []
    current: dict | None = None
    for i in range(start, n, 1):
        if (i - start) % REBALANCE_EVERY_DAYS != 0:
            continue
        vols = {a: _ann_vol(rets[a][i - VOL_LOOKBACK:i]) for a in assets}
        invw = _inverse_vol_weights(vols)
        port_rets = [sum(invw[a] * rets[a][t] for a in assets)
                     for t in range(i - VOL_LOOKBACK, i)]
        port_vol = _ann_vol(port_rets)
        uncapped_scale = (TARGET_VOL / port_vol) if port_vol > 0 else MAX_GROSS
        gross = min(MAX_GROSS, max(MIN_GROSS, uncapped_scale))
        target = {a: invw[a] * gross for a in assets}

        executed = True
        turnover = 0.0
        is_initial = current is None
        if is_initial:
            turnover = sum(target[a] for a in assets)   # initial allocation
            current = dict(target)
        else:
            drift = max(abs(target[a] - current[a]) for a in assets)
            if drift < NO_TRADE_BAND:
                executed = False                         # band suppresses churn
            else:
                turnover = sum(abs(target[a] - current[a]) for a in assets)
                current = dict(target)

        cov = _cov_matrix(rets, assets, i, COV_LOOKBACK)
        rc = _risk_contributions(current, cov, assets)
        checkpoints.append({
            "index": i,
            "vols": {a: round(vols[a], 6) for a in assets},
            "inverse_vol_weights": {a: round(invw[a], 6) for a in assets},
            "port_vol_ann": round(port_vol, 6),
            "uncapped_scale": round(uncapped_scale, 6),
            "gross_exposure": round(gross, 6),
            "weights": {a: round(current[a], 6) for a in assets},
            "executed": executed,
            "is_initial": is_initial,
            "turnover": round(turnover, 6),
            "risk_contributions": {a: round(rc[a], 6) for a in assets},
        })
    return {"checkpoints": checkpoints, "assets": assets}


# --------------------------------------------------------------------------- #
# Synthetic fixtures (deterministic; NO real data)
# --------------------------------------------------------------------------- #

def _lcg(seed: int):
    """Deterministic LCG (Numerical Recipes constants). No RNG import."""
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 0x100000000


def _asset_path(seed: int, vol_factor: float, n: int = SYNTHETIC_BARS,
                start: float = 100.0) -> list:
    """A deterministic price path: a calm regime (bars < 130) then a turbulent
    regime (>= 130, ~9x daily moves). Per-asset independent LCG -> near-zero
    cross-correlation; vol_factor scales the asset's volatility level so the three
    assets have distinct vols (BTC < ETH < SOL)."""
    gen = _lcg(seed)
    closes = [start]
    for i in range(1, n):
        calm = i < 130
        amp = (0.003 if calm else 0.027) * vol_factor
        shock = amp * (next(gen) - 0.5) * 2.0      # zero-mean daily move
        closes.append(closes[-1] * (1.0 + shock))
    return closes


def build_synthetic_fixtures() -> dict:
    # distinct vol levels: BTC lowest, SOL highest -> inverse-vol must order
    # BTC > ETH > SOL. Independent seeds keep cross-correlation near zero.
    return {
        "BTCUSD": _asset_path(seed=101, vol_factor=1.0),
        "ETHUSD": _asset_path(seed=202, vol_factor=1.4),
        "SOLUSD": _asset_path(seed=303, vol_factor=1.9),
    }


def run_synthetic_dry_run() -> dict:
    fx = build_synthetic_fixtures()
    out = allocate_c17(fx)
    cps = out["checkpoints"]
    assets = out["assets"]

    # determinism: re-run and compare the held-weight sequence.
    out2 = allocate_c17(build_synthetic_fixtures())
    deterministic = ([c["weights"] for c in cps]
                     == [c["weights"] for c in out2["checkpoints"]])

    calm = [c for c in cps if c["index"] < 130]
    turbulent = [c for c in cps if c["index"] >= 130]
    rep = calm[0] if calm else cps[0]               # representative calm checkpoint

    # inverse-vol ordering at the representative checkpoint (lower vol -> more wt)
    iw = rep["inverse_vol_weights"]
    inverse_vol_ordered = iw["BTCUSD"] > iw["ETHUSD"] > iw["SOLUSD"]

    all_weights_nonneg = all(w >= 0.0 for c in cps for w in c["weights"].values())
    gross_le_cap = all(c["gross_exposure"] <= MAX_GROSS + 1e-9 for c in cps)
    # calm regime: the UNCAPPED scale would exceed 1.0 but gross is capped at 1.0
    gross_capped_in_calm = any(
        c["uncapped_scale"] > 1.0 and abs(c["gross_exposure"] - MAX_GROSS) < 1e-9
        for c in calm)
    # turbulent regime: vol target scales gross strictly below the cap
    scales_down_in_high_vol = any(c["gross_exposure"] < MAX_GROSS - 1e-6
                                  for c in turbulent)

    # weekly cadence: every checkpoint index is a multiple of 7 from the start
    start = max(VOL_LOOKBACK, COV_LOOKBACK)
    weekly_cadence = all((c["index"] - start) % REBALANCE_EVERY_DAYS == 0
                         for c in cps)
    skipped = [c for c in cps if not c["executed"] and not c["is_initial"]]
    band_suppresses_churn = len(skipped) >= 1

    non_initial = [c for c in cps if not c["is_initial"]]
    avg_weekly_turnover = (sum(c["turnover"] for c in non_initial)
                           / len(non_initial)) if non_initial else 0.0
    turnover_within_cap = avg_weekly_turnover <= MAX_AVG_WEEKLY_TURNOVER

    # risk parity: risk contributions near equal at the representative checkpoint
    rc = rep["risk_contributions"]
    rc_vals = [v for v in rc.values() if v > 0]
    rc_ratio = (max(rc_vals) / min(rc_vals)) if rc_vals and min(rc_vals) > 0 \
        else 99.0
    rc_near_equal = rc_ratio <= RC_EQUALITY_RATIO_MAX

    checks = {
        "deterministic": deterministic,
        "inverse_vol_orders_weights": inverse_vol_ordered,
        "weights_nonnegative_no_shorting": all_weights_nonneg,
        "gross_exposure_le_cap": gross_le_cap,
        "gross_capped_at_one_in_calm": gross_capped_in_calm,
        "vol_target_scales_down_in_high_vol": scales_down_in_high_vol,
        "weekly_rebalance_cadence": weekly_cadence,
        "no_trade_band_suppresses_churn": band_suppresses_churn,
        "avg_weekly_turnover_within_cap": turnover_within_cap,
        "risk_contributions_near_equal": rc_near_equal,
        "universe_only_btc_eth_sol": set(out["assets"]) == set(ASSETS),
        "cost_model_not_applied": True,         # behaviour-only; 37 bps reserved
        "no_entry_exit_signal_continuous_allocation": True,
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "n_checkpoints": len(cps),
        "n_executed": len([c for c in cps if c["executed"]]),
        "n_skipped_by_band": len(skipped),
        "avg_weekly_turnover": round(avg_weekly_turnover, 6),
        "representative_checkpoint": rep,
        "checkpoints": cps,
    }


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_17_detector_dry_run_label() -> str:
    return (
        "Candidate #17 risk_adjusted_portfolio_construction_vol_targeted_"
        "allocation_v1 detector spec + SYNTHETIC dry-run (READ-ONLY, RESEARCH "
        "ONLY, PURE). Exercises the vol-targeted / risk-parity ALLOCATOR on "
        "DETERMINISTIC SYNTHETIC fixtures only -- never real data. Proves "
        "inverse-vol weights ordered BTC>ETH>SOL, long-only (no shorting), gross "
        "capped at 1.0 (no leverage), vol-target scaling down in high vol and "
        "capped in calm, weekly rebalance with a no-trade band, turnover within "
        "cap, near-equal risk contributions, and the BTC/ETH/SOL universe only. "
        "37 bps all-in cost RESERVED for replay. NOT a profitability claim.")


def get_candidate_17_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c17_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C17 detector spec + synthetic dry-run record. Pure; no
    I/O; chain-gated on the frozen C17 candidate spec."""
    spec = _c17s.build_c17_spec(repo_root, tracked_paths)
    spec_valid = _c17s.validate_c17_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c17_spec_invalid")
    if spec.get("verdict") != "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c17_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D17_SCHEMA_VERSION, "mode": D17_MODE, "lane": D17_LANE,
        "label": get_candidate_17_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C17_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved C17 allocator spec
        "assets": list(ASSETS), "timeframe": TIMEFRAME,
        "vol_lookback_days": VOL_LOOKBACK, "covariance_lookback_days": COV_LOOKBACK,
        "target_portfolio_vol_annualized": TARGET_VOL,
        "max_gross_exposure": MAX_GROSS, "min_gross_exposure": MIN_GROSS,
        "no_trade_band_pct": NO_TRADE_BAND,
        "max_avg_weekly_turnover": MAX_AVG_WEEKLY_TURNOVER,
        "rebalance_every_days": REBALANCE_EVERY_DAYS,
        "is_portfolio_allocator": True,
        "is_volatility_targeted": True, "is_risk_parity": True,
        "is_long_or_flat": True, "allows_shorting": False,
        "allows_leverage_above_cap": False,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "synthetic_bars_per_fixture": SYNTHETIC_BARS,
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_n_checkpoints": dry["n_checkpoints"],
        "dry_run_n_executed": dry["n_executed"],
        "dry_run_n_skipped_by_band": dry["n_skipped_by_band"],
        "dry_run_avg_weekly_turnover": dry["avg_weekly_turnover"],
        "dry_run_representative_checkpoint": dry["representative_checkpoint"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C16),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C16,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_17_detector_dry_run_next_action(),
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_real_candles": True,
        "no_labels": True, "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_cost_application": True, "no_optimization": True, "no_robustness": True,
        "no_portfolio_compute_on_real_data": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_shorting": True,
        "no_leverage_above_cap": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c17_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the dry-run is research-only,
    synthetic-only (no real data / no cost application), chain-gated on the frozen
    C17 spec, a long/flat vol-targeted risk-parity ALLOCATOR (no shorting / no
    leverage above the cap / not directional timing), all synthetic behaviour
    checks pass, the universe is exactly BTC/ETH/SOL, C1-C16 stays excluded,
    downstream gates locked, and every capability flag False."""
    failures: list = []
    if record.get("mode") != D17_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")

    # identity
    for k in ("is_portfolio_allocator", "is_volatility_targeted", "is_risk_parity",
              "is_long_or_flat", "uses_synthetic_fixtures_only",
              "cost_model_reserved_for_replay"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("uses_real_data") is not False:
        failures.append("uses_real_data_set")
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")
    if record.get("allows_shorting") is not False:
        failures.append("shorting_allowed")
    if record.get("allows_leverage_above_cap") is not False:
        failures.append("leverage_allowed")
    if record.get("is_directional_timing_signal") is not False:
        failures.append("must_not_be_directional_timing")

    # behaviour checks
    checks = record.get("dry_run_checks") or {}
    for k in ("deterministic", "inverse_vol_orders_weights",
              "weights_nonnegative_no_shorting", "gross_exposure_le_cap",
              "gross_capped_at_one_in_calm", "vol_target_scales_down_in_high_vol",
              "weekly_rebalance_cadence", "no_trade_band_suppresses_churn",
              "avg_weekly_turnover_within_cap", "risk_contributions_near_equal",
              "universe_only_btc_eth_sol", "cost_model_not_applied",
              "no_entry_exit_signal_continuous_allocation"):
        if checks.get(k) is not True:
            failures.append("dry_run_check_failed_%s" % k)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")
    if record.get("dry_run_avg_weekly_turnover", 1.0) > MAX_AVG_WEEKLY_TURNOVER:
        failures.append("avg_turnover_exceeds_cap")
    if list(record.get("assets") or []) != list(ASSETS):
        failures.append("assets_tampered")
    if record.get("timeframe") != "D1":
        failures.append("timeframe_not_d1")
    if record.get("max_gross_exposure") != 1.0:
        failures.append("gross_cap_tampered")

    # anti-loop
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("rejected_families_count") != 21:
        failures.append("ledger_not_21")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"):
        failures.append("next_action_not_labels_gate")

    # downstream gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_real_candles", "no_labels", "no_replay",
                "no_pnl", "no_cost_application", "no_optimization", "no_commit",
                "no_push", "no_broker", "no_order_logic", "no_shorting",
                "no_leverage_above_cap", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
