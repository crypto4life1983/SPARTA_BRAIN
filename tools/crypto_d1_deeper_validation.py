"""Crypto-D1 Momentum N=20 deeper-validation analysis layer (BUILD ONLY).

Research-only, local-only, stdlib-only. This module is the single, reconciled
*analysis* capability described by the committed plan
``reports/crypto_d1_momentum_n20_deeper_validation_plan/`` -- the nine deeper-
validation views of the SAME frozen N=20 OOS evidence. It:

  * runs NO backtest by itself over frozen data (the caller feeds in already-
    sliced OOS ``cbr.Bar`` series; unit tests feed tiny synthetic series);
  * executes no subprocess, opens no network, touches no credentials, places no
    order, and authorizes no paper/live/broker/exchange/fetch;
  * mutates no dataset, no QA freeze, no queue, no safety contract, no dashboard;
  * reuses ``crypto_d1_backtest_runner._simulate_equity`` /
    ``momentum_continuation`` as the SINGLE SOURCE OF TRUTH for the cost-aware
    equity + signal math (no divergent re-implementation of the cost model);
  * keeps N=20 the PRIMARY validation target. The {18, 20, 22} neighborhood is a
    bounded, explicitly-labeled *stability sensitivity* -- the winner is NEVER
    re-selected and N stays 20 (no parameter hunt, no OOS-tuning);
  * never promotes ACTIVE/STRONG, never auto-PASSes (verdict ceiling = WATCH).

This module reconciles the two earlier parallel drafts into one: it keeps the
runner-backed single-source-of-truth analysis AND the deterministic JSON
serializer + confined opt-in writer + read-only CLI. There is exactly one public
analysis API; no duplicate helpers.

Runner CLI/dispatch integration (a new ``--config
momentum_n20_deeper_validation_v1`` mode in ``crypto_d1_backtest_runner.py``) is
DEFERRED to a separately-approved step per the plan, so this build does not make
the analysis runnable over the frozen dataset.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_backtest_runner as cbr  # noqa: E402

# --- Identity / pre-registered parameters (NOT OOS-tuned) ------------------
CONFIG_NAME = "momentum_n20_deeper_validation_v1"
LAYER = "crypto_d1_momentum_n20_deeper_validation_v1"
PRIMARY_LOOKBACK = 20
REFERENCE_LOOKBACK = 30
# Bounded stability neighborhood. This is a SENSITIVITY band, not a grid search:
# the winner is never re-selected and the primary stays PRIMARY_LOOKBACK.
NEIGHBORHOOD_LOOKBACKS = (18, 20, 22)
VERDICT_CEILING = "WATCH"

# Frozen V002 cost pins -> 60 bps/side, 120 bps round-trip, taker every leg.
# Derived from the runner constants (one source of truth), NOT hardcoded.
_BASELINE_PER_SIDE_BPS = (
    cbr.V002_FALLBACK_FEE_BPS
    + cbr.V002_FALLBACK_SLIPPAGE_BPS
    + cbr.V002_FALLBACK_SPREAD_PROXY_BPS
)
BASELINE_ROUND_TRIP_BPS = 2.0 * _BASELINE_PER_SIDE_BPS  # 120.0
# Additive labeled cost-stress column (baseline 120 stays the headline).
STRESS_ROUND_TRIP_BPS = (150.0, 180.0, 240.0)
# Pre-declared regime proxies (computed only from frozen bars; no look-ahead).
REGIME_VOL_WINDOW = cbr.VOL_REGIME_WINDOW            # 30
REGIME_VOL_THRESHOLD = cbr.VOL_REGIME_MAX_ANNUALIZED  # 1.50 annualized
REGIME_TREND_SMA = 50

# Single confined writer target (opt-in only).
_BUILD_OUT_RELDIR = Path("reports") / "crypto_d1_momentum_n20_deeper_validation_build"

VALIDATION_SECTION_KEYS = (
    "1_yearly_oos_breakdown",
    "2_monthly_return_drawdown_profile",
    "3_per_asset_consistency",
    "4_trade_count_and_turnover",
    "5_fee_slippage_stress",
    "6_outlier_sensitivity",
    "7_regime_sensitivity",
    "8_basket_vs_per_asset",
    "9_small_parameter_neighborhood_sensitivity",
)

SAFETY_FLAGS = {
    "research_only": True,
    "paper_live_authorized": False,
    "broker_path_enabled": False,
    "exchange_path_enabled": False,
    "order_path_enabled": False,
    "fetch_live_data_enabled": False,
    "dataset_mutation_allowed": False,
    "active_strong_promoted": False,
    "bundle_23_started": False,
    "execution_authorized": False,
}

NON_AUTHORIZATION = (
    "Deeper-validation ANALYSIS layer only. Computes descriptive views of the "
    "frozen N=20 OOS evidence; authorizes no paper, live, broker, exchange, "
    "order, or fetch action; promotes no lane to ACTIVE/STRONG; starts no "
    "Bundle 23; mutates no dataset. Verdict ceiling stays WATCH; lane stays "
    "WATCH/MIXED and NOT_READY_FOR_REAL_DATA. A positive view is not a trading "
    "authorization."
)


# ===========================================================================
# Cost helper -- one knob (round-trip bps) folded onto the runner's simulator.
# Every equity/return/cost number in this module flows through here, so there is
# no second cost model and no drift from the runner.
# ===========================================================================
def _metrics_at_round_trip(bars, positions, round_trip_bps, start_equity):
    """Cost-aware metrics for the SAME positions at a given round-trip cost.

    Folds the whole round-trip into the runner's per-side cost knob
    (per-side = round_trip / 2; slip/spread = 0) so the cost model stays
    ``crypto_d1_backtest_runner._simulate_equity`` -- one source of truth."""
    return cbr._simulate_equity(
        positions, bars, fee_bps=round_trip_bps / 2.0, slip_bps=0.0,
        start_equity=start_equity, spread_bps=0.0,
    )


def _positions_for(bars, lookback):
    pos, err = cbr.momentum_continuation(bars, lookback)
    return pos, err


def _oos_trade_ledger(bars, positions, round_trip_bps):
    """Per-trade net-return ledger for outlier analysis (a NEW descriptive view
    the runner does not expose). A trade spans entry (0->1) to the bar it returns
    flat (or the final bar). Net return compounds held-bar returns then applies
    ONE round-trip cost anchored to the same BASELINE_ROUND_TRIP_BPS constant --
    a per-trade decomposition, NOT a second equity model. Headline numbers stay
    from the runner's simulator."""
    trades = []
    rt = round_trip_bps / 10_000.0
    n = min(len(bars), len(positions))
    t = 1
    while t < n:
        if positions[t] == 1 and positions[t - 1] == 0:
            entry = t
            gross = 1.0
            while t < n and positions[t] == 1:
                gross *= bars[t].close / bars[t - 1].close
                t += 1
            net = gross * (1.0 - rt) - 1.0
            trades.append({
                "entry_date": bars[entry].timestamp,
                "exit_date": bars[min(t, n) - 1].timestamp,
                "held_bars": min(t, n) - entry,
                "net_return": net,
            })
        else:
            t += 1
    return trades


# ===========================================================================
# Section 1 -- Yearly OOS breakdown
# ===========================================================================
def yearly_oos_breakdown(bars, positions, start_equity):
    """Per-calendar-year OOS sub-returns/trades/max-dd (read-only slice; no
    re-split, no re-optimization). Each year is re-simulated as a fresh slice."""
    years: dict[str, list[int]] = {}
    for i, b in enumerate(bars):
        years.setdefault(b.timestamp[:4], []).append(i)
    out = {}
    for yr in sorted(years):
        idx = years[yr]
        sub_bars = [bars[i] for i in idx]
        sub_pos = [positions[i] for i in idx]
        m = _metrics_at_round_trip(sub_bars, sub_pos, BASELINE_ROUND_TRIP_BPS,
                                   start_equity)
        out[yr] = {
            "total_return": m["total_return"],
            "trade_count": m["trade_count"],
            "max_drawdown": m["max_drawdown"],
            "n_bars": len(sub_bars),
            "positive": m["total_return"] > 0.0,
        }
    return out


# ===========================================================================
# Section 2 -- Monthly return / drawdown profile
# ===========================================================================
def monthly_return_drawdown(bars, positions, start_equity):
    """Per-month OOS returns plus the OOS curve's worst month, longest drawdown
    (in bars), and max drawdown. Descriptive."""
    months: dict[str, list[int]] = {}
    for i, b in enumerate(bars):
        months.setdefault(b.timestamp[:7], []).append(i)
    monthly = {}
    for mo in sorted(months):
        idx = months[mo]
        sub_bars = [bars[i] for i in idx]
        sub_pos = [positions[i] for i in idx]
        m = _metrics_at_round_trip(sub_bars, sub_pos, BASELINE_ROUND_TRIP_BPS,
                                   start_equity)
        monthly[mo] = {"total_return": m["total_return"], "n_bars": len(sub_bars)}

    full = _metrics_at_round_trip(bars, positions, BASELINE_ROUND_TRIP_BPS,
                                  start_equity)
    curve = full["equity_curve"]
    longest, cur_len, peak = 0, 0, curve[0] if curve else start_equity
    for x in curve:
        if x >= peak:
            peak = x
            cur_len = 0
        else:
            cur_len += 1
            longest = max(longest, cur_len)
    worst_month = min(monthly, key=lambda k: monthly[k]["total_return"]) if monthly else None
    return {
        "per_month": monthly,
        "worst_month": worst_month,
        "worst_month_return": monthly[worst_month]["total_return"] if worst_month else None,
        "longest_drawdown_bars": longest,
        "oos_max_drawdown": full["max_drawdown"],
    }


# ===========================================================================
# Section 3 -- Per-asset consistency (BTC/ETH/SOL)
# ===========================================================================
def per_asset_consistency(per_asset_metrics):
    """Side-by-side per-asset N=20 OOS table (sign, floor clearance, dd,
    turnover) + a flag for any single asset carrying the basket."""
    table = {}
    positive_assets = []
    for asset, m in per_asset_metrics.items():
        clears = m["trade_count"] >= cbr.OOS_MIN_TRADES_PER_ASSET
        table[asset] = {
            "total_return": m["total_return"],
            "positive": m["total_return"] > 0.0,
            "trade_count": m["trade_count"],
            "clears_per_asset_floor": clears,
            "max_drawdown": m["max_drawdown"],
            "turnover": m["turnover"],
        }
        if m["total_return"] > 0.0:
            positive_assets.append(asset)
    total_pos = sum(max(0.0, m["total_return"]) for m in per_asset_metrics.values())
    single_asset_carry = None
    if total_pos > 0 and per_asset_metrics:
        for asset, m in per_asset_metrics.items():
            if m["total_return"] > 0.0 and (m["total_return"] / total_pos) >= 0.60:
                single_asset_carry = asset
                break
    return {
        "per_asset": table,
        "n_positive_assets": len(positive_assets),
        "all_positive": len(positive_assets) == len(per_asset_metrics) and bool(per_asset_metrics),
        "single_asset_carrying_flag": single_asset_carry,
    }


# ===========================================================================
# Section 4 -- Trade count & turnover
# ===========================================================================
def trade_count_turnover(per_asset_metrics):
    """Re-confirm OOS counts, turnover, per-asset floor clearance, family total
    against the per-family floor (operator-side; classify_run unchanged)."""
    per_asset = {}
    family_total = 0
    for asset, m in per_asset_metrics.items():
        per_asset[asset] = {
            "trade_count": m["trade_count"],
            "turnover": m["turnover"],
            "exposure_pct": m["exposure_pct"],
            "clears_per_asset_floor": m["trade_count"] >= cbr.OOS_MIN_TRADES_PER_ASSET,
        }
        family_total += m["trade_count"]
    return {
        "per_asset": per_asset,
        "per_asset_floor": cbr.OOS_MIN_TRADES_PER_ASSET,
        "family_oos_trade_total": family_total,
        "per_family_floor": cbr.OOS_MIN_TRADES_PER_FAMILY,
        "meets_family_floor": family_total >= cbr.OOS_MIN_TRADES_PER_FAMILY,
    }


# ===========================================================================
# Section 5 -- Fee / slippage stress
# ===========================================================================
def fee_slippage_stress(bars, positions, start_equity,
                        stress_levels=STRESS_ROUND_TRIP_BPS):
    """Re-price the SAME N=20 OOS ledger at higher round-trip costs as an
    additive column; report each level's return + an approximate breakeven cost.
    Baseline 120 bps stays the headline (never redefined)."""
    base = _metrics_at_round_trip(bars, positions, BASELINE_ROUND_TRIP_BPS,
                                  start_equity)
    levels = {}
    for rt in stress_levels:
        m = _metrics_at_round_trip(bars, positions, rt, start_equity)
        levels[f"{rt:g}"] = {
            "round_trip_bps": rt,
            "total_return": m["total_return"],
            "survives_positive": m["total_return"] > 0.0,
        }
    # Approximate breakeven round-trip cost via bisection (total_return is
    # monotonically non-increasing in cost when trades exist).
    breakeven = None
    if base["trade_count"] > 0 and base["total_return"] > 0.0:
        lo, hi = BASELINE_ROUND_TRIP_BPS, 4000.0
        if _metrics_at_round_trip(bars, positions, hi, start_equity)["total_return"] <= 0.0:
            for _ in range(40):
                mid = (lo + hi) / 2.0
                r = _metrics_at_round_trip(bars, positions, mid, start_equity)["total_return"]
                if r > 0.0:
                    lo = mid
                else:
                    hi = mid
            breakeven = round((lo + hi) / 2.0, 2)
    return {
        "baseline_round_trip_bps": BASELINE_ROUND_TRIP_BPS,
        "baseline_total_return": base["total_return"],
        "stress_levels": levels,
        "approx_breakeven_round_trip_bps": breakeven,
    }


# ===========================================================================
# Section 6 -- Outlier sensitivity
# ===========================================================================
def outlier_sensitivity(bars, positions, top_k=(1, 3)):
    """Recompute the compounded trade-return edge excluding the best, the worst,
    and the small top-k best/worst OOS trades. Flags an outlier-dependent edge.
    Descriptive; the unmodified result stays official."""
    ledger = _oos_trade_ledger(bars, positions, BASELINE_ROUND_TRIP_BPS)
    rets = sorted(t["net_return"] for t in ledger)

    def _compound(seq):
        eq = 1.0
        for r in seq:
            eq *= (1.0 + r)
        return eq - 1.0

    base = _compound(rets)
    out = {
        "n_trades": len(rets),
        "compounded_trade_return_all": base,
        "exclude_best": _compound(rets[:-1]) if rets else None,
        "exclude_worst": _compound(rets[1:]) if rets else None,
    }
    for k in top_k:
        if len(rets) > 2 * k:
            out[f"exclude_top{k}_best"] = _compound(rets[:-k])
            out[f"exclude_top{k}_worst"] = _compound(rets[k:])
    # Outlier-dependent if dropping the single best flips the edge sign.
    out["edge_outlier_dependent"] = bool(
        rets and base > 0.0 and out["exclude_best"] is not None
        and out["exclude_best"] <= 0.0
    )
    return out


# ===========================================================================
# Section 7 -- Regime sensitivity
# ===========================================================================
def regime_sensitivity(bars, positions, start_equity):
    """Bucket OOS bars by PRE-DECLARED trailing vol (>/<= threshold) and trend
    (price vs trailing SMA) proxies -- computed only from frozen bars, no
    look-ahead -- and report the strategy's bucketed contribution so the edge is
    not confined to a single regime."""
    buckets = {
        "low_vol": [], "high_vol": [], "uptrend": [], "downtrend": [],
        "vol_undefined": [], "trend_undefined": [],
    }
    n = min(len(bars), len(positions))
    for t in range(1, n):
        ann_vol = cbr._rolling_annualized_vol(bars, t, REGIME_VOL_WINDOW)
        if ann_vol is None:
            buckets["vol_undefined"].append(t)
        elif ann_vol <= REGIME_VOL_THRESHOLD:
            buckets["low_vol"].append(t)
        else:
            buckets["high_vol"].append(t)
        if t >= REGIME_TREND_SMA:
            sma = sum(b.close for b in bars[t - REGIME_TREND_SMA:t]) / REGIME_TREND_SMA
            (buckets["uptrend"] if bars[t].close > sma else buckets["downtrend"]).append(t)
        else:
            buckets["trend_undefined"].append(t)

    def _bucket_return(idxs):
        eq = 1.0
        for t in idxs:
            ret = bars[t].close / bars[t - 1].close - 1.0
            eq *= (1.0 + positions[t] * ret)
        return eq - 1.0

    summary = {}
    for name, idxs in buckets.items():
        summary[name] = {
            "n_bars": len(idxs),
            "strategy_return_in_bucket": _bucket_return(idxs) if idxs else 0.0,
        }
    decisive = [k for k in ("low_vol", "high_vol", "uptrend", "downtrend")
                if summary[k]["strategy_return_in_bucket"] > 0.0]
    return {
        "proxies": {
            "vol_window": REGIME_VOL_WINDOW,
            "vol_threshold_annualized": REGIME_VOL_THRESHOLD,
            "trend_sma": REGIME_TREND_SMA,
            "look_ahead": False,
        },
        "buckets": summary,
        "positive_regime_buckets": decisive,
        "confined_to_single_regime": len(decisive) <= 1,
    }


# ===========================================================================
# Section 8 -- Basket vs per-asset behavior
# ===========================================================================
def basket_vs_per_asset(per_asset_bars, start_equity):
    """Allocate-once equal-weight basket OOS vs per-asset N=20: how much edge
    survives equal-weight basketing (no rebalance). Construction unchanged."""
    per_asset = {}
    for asset, bars in per_asset_bars.items():
        pos, err = _positions_for(bars, PRIMARY_LOOKBACK)
        if err is not None:
            per_asset[asset] = {"error": err}
            continue
        m = _metrics_at_round_trip(bars, pos, BASELINE_ROUND_TRIP_BPS, start_equity)
        per_asset[asset] = {"total_return": m["total_return"], "trade_count": m["trade_count"]}
    valid = {a: d for a, d in per_asset.items() if "total_return" in d}
    basket_return = (sum(d["total_return"] for d in valid.values()) / len(valid)
                     if valid else None)
    mean_solo = basket_return  # equal-weight allocate-once == mean of per-asset legs
    return {
        "per_asset_solo": per_asset,
        "equal_weight_basket_oos_return": basket_return,
        "mean_per_asset_oos_return": mean_solo,
        "rebalance": "none (allocate once)",
    }


# ===========================================================================
# Section 9 -- Small parameter neighborhood (SENSITIVITY, not optimization)
# ===========================================================================
def neighborhood_sensitivity(bars, start_equity,
                             lookbacks=NEIGHBORHOOD_LOOKBACKS):
    """Probe N in the bounded {18, 20, 22} neighborhood as a STABILITY view.

    This is NOT a re-optimization: the winner is never re-selected, the primary
    stays N=20, and no N is promoted by being best here. Reports each N's OOS
    return/trades purely so the operator can see whether 20 sits on a plateau."""
    out = {}
    for n in lookbacks:
        pos, err = _positions_for(bars, n)
        if err is not None:
            out[str(n)] = {"error": err}
            continue
        m = _metrics_at_round_trip(bars, pos, BASELINE_ROUND_TRIP_BPS, start_equity)
        out[str(n)] = {
            "lookback": n,
            "total_return": m["total_return"],
            "trade_count": m["trade_count"],
            "is_primary": n == PRIMARY_LOOKBACK,
        }
    return {
        "neighborhood": list(lookbacks),
        "primary_lookback": PRIMARY_LOOKBACK,
        "winner_reselected": False,
        "is_sensitivity_not_optimization": True,
        "per_lookback": out,
    }


# ===========================================================================
# Assembler -- the full 9-section deeper-validation report (no execution)
# ===========================================================================
def build_deeper_validation_report(per_asset, start_equity=cbr.DEFAULT_START_EQUITY):
    """Assemble the 9-section deeper-validation report from per-asset OOS bars.

    ``per_asset`` is a list of ``{"asset": str, "bars": [cbr.Bar, ...]}`` where
    ``bars`` are the OOS-window bars only. Runs NO full backtest over frozen
    data; performs only descriptive analysis on the supplied series. Verdict
    ceiling stays WATCH; no promotion; all safety flags pinned false."""
    per_asset_bars = {}
    per_asset_metrics = {}
    notes = {}
    for item in per_asset:
        asset = item["asset"]
        bars = item["bars"]
        per_asset_bars[asset] = bars
        pos, err = _positions_for(bars, PRIMARY_LOOKBACK)
        if err is not None:
            notes[asset] = err
            continue
        m = _metrics_at_round_trip(bars, pos, BASELINE_ROUND_TRIP_BPS, start_equity)
        per_asset_metrics[asset] = m

    sections = {
        "1_yearly_oos_breakdown": {},
        "2_monthly_return_drawdown_profile": {},
        "5_fee_slippage_stress": {},
        "6_outlier_sensitivity": {},
        "7_regime_sensitivity": {},
    }
    for asset, bars in per_asset_bars.items():
        pos, err = _positions_for(bars, PRIMARY_LOOKBACK)
        if err is not None:
            continue
        sections["1_yearly_oos_breakdown"][asset] = yearly_oos_breakdown(bars, pos, start_equity)
        sections["2_monthly_return_drawdown_profile"][asset] = monthly_return_drawdown(bars, pos, start_equity)
        sections["5_fee_slippage_stress"][asset] = fee_slippage_stress(bars, pos, start_equity)
        sections["6_outlier_sensitivity"][asset] = outlier_sensitivity(bars, pos)
        sections["7_regime_sensitivity"][asset] = regime_sensitivity(bars, pos, start_equity)

    sections["3_per_asset_consistency"] = per_asset_consistency(per_asset_metrics)
    sections["4_trade_count_and_turnover"] = trade_count_turnover(per_asset_metrics)
    sections["8_basket_vs_per_asset"] = basket_vs_per_asset(per_asset_bars, start_equity)
    sections["9_small_parameter_neighborhood_sensitivity"] = {
        asset: neighborhood_sensitivity(bars, start_equity)
        for asset, bars in per_asset_bars.items()
    }

    return {
        "layer": LAYER,
        "config_mode": CONFIG_NAME,
        "executes_backtest": False,
        "status": "DEEPER_VALIDATION_ANALYSIS_ONLY",
        "dataset_id": "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002",
        "is_window": {"start": cbr.V002_IS_START, "end": cbr.V002_IS_END},
        "oos_window": {"start": cbr.V002_OOS_START, "end": cbr.V002_OOS_END},
        "primary_lookback": PRIMARY_LOOKBACK,
        "reference_lookback": REFERENCE_LOOKBACK,
        "neighborhood_lookbacks": list(NEIGHBORHOOD_LOOKBACKS),
        "neighborhood_is_sensitivity_not_optimization": True,
        "winner_reselected": False,
        "cost_model_round_trip_bps": BASELINE_ROUND_TRIP_BPS,
        "verdict_ceiling": VERDICT_CEILING,
        "insufficient_history_notes": notes,
        "validation_sections": sections,
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


def show_plan():
    """Read-only descriptor of this deeper-validation mode (no execution)."""
    return {
        "config_name": CONFIG_NAME,
        "layer": LAYER,
        "purpose": (
            "Deeper validation of the pre-registered N=20 Crypto-D1 momentum "
            "candidate via nine descriptive views of the frozen OOS evidence. "
            "No new parameter search; N stays 20; verdict ceiling WATCH."
        ),
        "primary_lookback": PRIMARY_LOOKBACK,
        "reference_lookback": REFERENCE_LOOKBACK,
        "neighborhood_lookbacks": list(NEIGHBORHOOD_LOOKBACKS),
        "neighborhood_is_sensitivity_not_optimization": True,
        "validation_sections": list(VALIDATION_SECTION_KEYS),
        "is_window": {"start": cbr.V002_IS_START, "end": cbr.V002_IS_END},
        "oos_window": {"start": cbr.V002_OOS_START, "end": cbr.V002_OOS_END},
        "cost_model_round_trip_bps": BASELINE_ROUND_TRIP_BPS,
        "stress_round_trip_bps": list(STRESS_ROUND_TRIP_BPS),
        "runner_integration": "DEFERRED to a separately-approved step",
        "build_only": True,
        "executes_backtest": False,
        "safety_flags": dict(SAFETY_FLAGS),
        "non_authorization_statement": NON_AUTHORIZATION,
    }


# ===========================================================================
# Deterministic serialization + opt-in confined writer + read-only CLI.
# ===========================================================================
def to_stable_json(obj) -> str:
    """Deterministic, sorted-key JSON (matches the factory convention). Uses
    default=str so any non-JSON scalars serialize stably and byte-identically."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False,
                      default=str) + "\n"


def write_build_report(base, descriptor) -> list:
    """Opt-in writer. Writes ONLY under the single build folder
    reports/crypto_d1_momentum_n20_deeper_validation_build/. Returns the
    repo-relative paths written. Writes no result/backtest data."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "capability_plan.json"
    json_path.write_text(to_stable_json(descriptor), encoding="utf-8")
    return [json_path.relative_to(base).as_posix()]


def main(argv=None) -> int:
    """Read-only CLI: prints the deeper-validation plan descriptor. Runs NO
    backtest, performs no simulation, executes nothing, returns 0."""
    parser = argparse.ArgumentParser(
        description="Crypto-D1 N=20 deeper-validation plan descriptor (BUILD "
                    "ONLY; runs no backtest, executes nothing).")
    parser.add_argument("--base", default=None, help="repo root (default: cwd)")
    parser.add_argument("--write", action="store_true",
                        help="ALSO write capability_plan.json under "
                             "reports/crypto_d1_momentum_n20_deeper_validation_build/")
    args = parser.parse_args(argv)
    descriptor = show_plan()  # read-only; no simulation, no frozen-data access
    if args.write:
        base = Path(args.base) if args.base else Path(".")
        written = write_build_report(base, descriptor)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(to_stable_json(descriptor))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
