"""Crypto-D1 Momentum N=20 — Deeper-Validation analysis capability (BUILD ONLY).

This module is the ADDITIVE, standard-library-only capability that the committed
PLAN ONLY artifact
``reports/crypto_d1_momentum_n20_deeper_validation_plan/report.json`` describes.
It implements the *analysis* half of deeper validation as a set of pure,
deterministic functions plus a schema assembler, so a FUTURE, separately-approved
execution step can feed an N=20 momentum OOS result into it and emit the required
validation report.

WHY A SEPARATE MODULE (not a new run_backtest mode):
  The deeper-validation outputs (yearly/monthly decomposition, fee/slippage
  re-pricing, outlier exclusion, regime bucketing, basket comparison, bounded
  N-neighborhood stability) are DESCRIPTIVE post-processing over an already
  computed N=20 OOS result. Keeping them out of the 1876-line
  ``tools/crypto_d1_backtest_runner.py`` guarantees the existing
  ``momentum_confirmation_v1`` / ``momentum_robustness_v1`` / ``v002_addendum``
  paths stay byte-identical (zero regression risk), and lets every function be
  unit-tested on tiny synthetic inputs WITHOUT running any backtest. The future
  execution mode is a thin wiring: run an N=20 momentum pass via the existing
  confirmation engine, then pass its per-asset OOS series/ledger into the
  functions here.

HARD SAFETY POSTURE (asserted by tests):
  * BUILD ONLY. Importing or calling anything here runs NO backtest, executes no
    Strategy Factory task, and writes nothing unless ``write_build_report`` is
    called explicitly (and then only under
    ``reports/crypto_d1_momentum_n20_deeper_validation_build/``).
  * research_only=true; every paper/live/broker/exchange/order/fetch/
    dataset-mutation/ACTIVE-STRONG/Bundle-23/execution flag pinned FALSE.
  * The N-neighborhood {18, 20, 22} is a PRE-REGISTERED, BOUNDED *sensitivity*
    check, never an optimization: the winner is N=20 and is never re-selected
    from the neighborhood probe.
  * No network, no subprocess, no broker/exchange/order/fetch code. Stdlib only.
  * Deterministic: sorted-key JSON; no wall-clock in computed values.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
LAYER_NAME = "crypto_d1_momentum_n20_deeper_validation_v1"

# The deeper-validation capability is keyed to the single best-sampled candidate.
CONFIG_NAME = "momentum_n20_deeper_validation_v1"
PRIMARY_LOOKBACK = 20
REFERENCE_LOOKBACK = 30

# Pre-registered, BOUNDED neighborhood for a stability (NOT optimization) probe.
# The winner stays N=20; the neighborhood is reported as sensitivity only.
PARAMETER_NEIGHBORHOOD = (18, 20, 22)
NEIGHBORHOOD_IS_SENSITIVITY_NOT_OPTIMIZATION = True

# Frozen cost baseline from the plan (V002 fees.json: 60 bps/side, 120 round-trip).
BASELINE_ROUND_TRIP_BPS = 120
DEFAULT_STRESS_ROUND_TRIP_BPS = (150, 180, 240)

PER_ASSET_OOS_TRADE_FLOOR = 20
ASSETS = ("BTC", "ETH", "SOL")

# Every flag pinned to the non-authorizing value. This module authorizes nothing.
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

_BUILD_OUT_RELDIR = Path("reports") / "crypto_d1_momentum_n20_deeper_validation_build"

# The required validation sections, in plan order. Used both to render the empty
# capability contract and to validate that a computed report is complete.
REQUIRED_SECTIONS = (
    "yearly_oos_breakdown",
    "monthly_return_drawdown_profile",
    "per_asset_consistency",
    "trade_count_and_turnover",
    "fee_slippage_stress",
    "outlier_sensitivity",
    "regime_sensitivity",
    "basket_vs_per_asset",
    "parameter_neighborhood",
)


# ---------------------------------------------------------------------------
# Small deterministic numeric helpers (pure).
# ---------------------------------------------------------------------------

def _round(x: Optional[float], n: int = 10) -> Optional[float]:
    return None if x is None else round(float(x), n)


def compound_returns(returns) -> float:
    """Compound a sequence of per-step simple returns into a total return."""
    mult = 1.0
    for r in returns:
        mult *= (1.0 + float(r))
    return mult - 1.0


def equity_to_daily_returns(dates, equity_curve):
    """Convert a date-aligned equity curve into [(date, simple_return), ...].

    ``equity_curve`` has one more point than there are return steps (it includes
    the starting equity). ``dates`` aligns to the post-step equity points.
    """
    out = []
    for i in range(1, len(equity_curve)):
        prev, cur = float(equity_curve[i - 1]), float(equity_curve[i])
        ret = (cur / prev - 1.0) if prev != 0 else 0.0
        d = dates[i - 1] if i - 1 < len(dates) else None
        out.append((d, ret))
    return out


def _equity_from_returns(daily_returns, start: float = 1.0):
    eq = [start]
    for _d, r in daily_returns:
        eq.append(eq[-1] * (1.0 + float(r)))
    return eq


def max_drawdown(equity_curve) -> float:
    """Most negative peak-to-trough drawdown of an equity curve (<= 0)."""
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    worst = 0.0
    for v in equity_curve:
        if v > peak:
            peak = v
        dd = (v / peak - 1.0) if peak != 0 else 0.0
        if dd < worst:
            worst = dd
    return worst


# ---------------------------------------------------------------------------
# Validation-section functions (pure). Each takes already-computed inputs that a
# future N=20 run would supply; none of them runs a backtest.
# ---------------------------------------------------------------------------

def yearly_oos_breakdown(daily_returns) -> dict:
    """Per-calendar-year compounded OOS return + day count from a dated return
    series. Read-only slice; never re-splits the IS/OOS boundary."""
    by_year: dict = {}
    for d, r in daily_returns:
        year = str(d)[:4] if d else "unknown"
        by_year.setdefault(year, []).append(float(r))
    return {
        "by_year": {
            y: {"total_return": _round(compound_returns(rs)), "n_days": len(rs)}
            for y, rs in sorted(by_year.items())
        },
        "note": "Descriptive per-year slice of the frozen OOS window; no re-split.",
    }


def monthly_return_drawdown_profile(daily_returns) -> dict:
    """Per-month compounded return and worst intramonth drawdown, plus overall
    worst month and longest drawdown (in steps)."""
    by_month: dict = {}
    for d, r in daily_returns:
        key = str(d)[:7] if d else "unknown"
        by_month.setdefault(key, []).append(float(r))

    monthly = {}
    worst_month = None
    for m, rs in sorted(by_month.items()):
        tot = compound_returns(rs)
        dd = max_drawdown(_equity_from_returns([(None, x) for x in rs]))
        monthly[m] = {"total_return": _round(tot),
                      "max_drawdown": _round(dd)}
        if worst_month is None or tot < monthly[worst_month]["total_return"]:
            worst_month = m

    full_eq = _equity_from_returns(daily_returns)
    return {
        "by_month": monthly,
        "worst_month": worst_month,
        "overall_max_drawdown": _round(max_drawdown(full_eq)),
        "longest_drawdown_steps": _longest_drawdown_steps(full_eq),
        "note": "Descriptive monthly profile; no parameter change.",
    }


def _longest_drawdown_steps(equity_curve) -> int:
    if not equity_curve:
        return 0
    peak = equity_curve[0]
    longest = 0
    cur = 0
    for v in equity_curve:
        if v >= peak:
            peak = v
            cur = 0
        else:
            cur += 1
            longest = max(longest, cur)
    return longest


def per_asset_consistency(per_asset_oos: dict, floor: int = PER_ASSET_OOS_TRADE_FLOOR) -> dict:
    """Side-by-side BTC/ETH/SOL N=20 OOS consistency. Flags whether a single
    asset is carrying the result."""
    rows = {}
    positive = []
    clears = []
    for asset, m in per_asset_oos.items():
        tr = m.get("total_return")
        tc = m.get("trade_count")
        rows[asset] = {
            "total_return": _round(tr),
            "trade_count": tc,
            "max_drawdown": _round(m.get("max_drawdown")),
            "turnover": m.get("turnover"),
            "clears_per_asset_floor": (tc is not None and tc >= floor),
        }
        if tr is not None and tr > 0:
            positive.append(asset)
        if tc is not None and tc >= floor:
            clears.append(asset)

    returns = [(a, rows[a]["total_return"]) for a in rows
               if rows[a]["total_return"] is not None]
    carrier = max(returns, key=lambda kv: kv[1])[0] if returns else None
    return {
        "rows": rows,
        "all_positive_oos": len(positive) == len(rows) and len(rows) > 0,
        "assets_positive_oos": sorted(positive),
        "assets_clearing_floor": sorted(clears),
        "all_clear_floor": len(clears) == len(rows) and len(rows) > 0,
        "highest_return_asset": carrier,
        "note": "Uses already-computed per-asset OOS metrics; no recompute of signals.",
    }


def trade_count_and_turnover(per_asset_trades: dict,
                             floor: int = PER_ASSET_OOS_TRADE_FLOOR) -> dict:
    """Confirm OOS trade counts / turnover and per-asset floor clearance, with a
    family total."""
    rows = {}
    family_total = 0
    for asset, m in per_asset_trades.items():
        tc = int(m.get("trade_count") or 0)
        family_total += tc
        rows[asset] = {
            "trade_count": tc,
            "turnover": m.get("turnover"),
            "clears_per_asset_floor": tc >= floor,
        }
    return {
        "rows": rows,
        "family_oos_trades_total": family_total,
        "per_asset_floor": floor,
        "all_clear_floor": all(r["clears_per_asset_floor"] for r in rows.values())
        and len(rows) > 0,
    }


def fee_slippage_stress(trade_gross_returns,
                        baseline_round_trip_bps: int = BASELINE_ROUND_TRIP_BPS,
                        stress_round_trip_bps=DEFAULT_STRESS_ROUND_TRIP_BPS) -> dict:
    """Re-price the SAME OOS trade ledger at higher round-trip costs.

    Each entry in ``trade_gross_returns`` is one round-trip trade's PRE-COST
    simple return. Net per trade at cost ``c`` bps = (1+g)*(1 - c/1e4) - 1;
    results are compounded. The baseline stays the headline; stress columns are
    explicitly labeled sensitivity, never a redefinition of the baseline.
    """
    def compounded_at(bps):
        c = bps / 10000.0
        mult = 1.0
        for g in trade_gross_returns:
            mult *= (1.0 + float(g)) * (1.0 - c)
        return mult - 1.0

    levels = {str(int(b)): _round(compounded_at(b))
              for b in (baseline_round_trip_bps, *stress_round_trip_bps)}
    return {
        "baseline_round_trip_bps": baseline_round_trip_bps,
        "headline_total_return": _round(compounded_at(baseline_round_trip_bps)),
        "stress_total_return_by_bps": levels,
        "breakeven_round_trip_bps": _breakeven_bps(trade_gross_returns),
        "label": "SENSITIVITY ONLY — baseline 120 bps remains the headline cost model.",
    }


def _breakeven_bps(trade_gross_returns, lo: int = 0, hi: int = 5000) -> Optional[int]:
    """Smallest 1-bp round-trip cost at which compounded OOS return turns <= 0.
    Binary search; returns None if even hi bps stays positive."""
    def comp(bps):
        c = bps / 10000.0
        mult = 1.0
        for g in trade_gross_returns:
            mult *= (1.0 + float(g)) * (1.0 - c)
        return mult - 1.0

    if comp(lo) <= 0:
        return lo
    if comp(hi) > 0:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if comp(mid) > 0:
            lo = mid + 1
        else:
            hi = mid
    return lo


def outlier_sensitivity(trade_returns, top_k=(1, 2, 3)) -> dict:
    """Recompute compounded OOS return after removing the single best, the single
    worst, and the top-k largest-magnitude trades. The UNMODIFIED figure stays
    the official one; these are robustness diagnostics only."""
    rs = [float(x) for x in trade_returns]
    base = compound_returns(rs)
    out = {
        "base_total_return": _round(base),
        "ex_best": _round(compound_returns([x for x in rs if x != max(rs)])) if rs else None,
        "ex_worst": _round(compound_returns([x for x in rs if x != min(rs)])) if rs else None,
        "ex_top_k": {},
        "note": "Diagnostic only; the unmodified result remains the official figure.",
    }
    for k in top_k:
        kept = _drop_top_k_by_magnitude(rs, k)
        out["ex_top_k"][str(k)] = _round(compound_returns(kept))
    return out


def _drop_top_k_by_magnitude(rs, k):
    order = sorted(range(len(rs)), key=lambda i: abs(rs[i]), reverse=True)
    drop = set(order[:k])
    return [x for i, x in enumerate(rs) if i not in drop]


def simple_trend_regime(prices, lookback: int = PRIMARY_LOOKBACK):
    """Pre-declared, descriptive trend label per bar derived ONLY from frozen
    prices: 'bull' if price[i] > price[i-lookback] else 'bear'. Bars before the
    lookback warmup are labeled 'warmup'. No external data, no look-ahead beyond
    the trailing window."""
    labels = []
    for i in range(len(prices)):
        if i < lookback:
            labels.append("warmup")
        else:
            labels.append("bull" if float(prices[i]) > float(prices[i - lookback]) else "bear")
    return labels


def regime_sensitivity(daily_returns, regime_labels) -> dict:
    """Bucket the OOS daily returns by a pre-declared regime label and report the
    compounded return + day count per bucket. Confirms the edge is not confined
    to a single regime."""
    buckets: dict = {}
    n = min(len(daily_returns), len(regime_labels))
    for i in range(n):
        lab = regime_labels[i]
        if lab == "warmup":
            continue
        buckets.setdefault(lab, []).append(float(daily_returns[i][1]))
    return {
        "by_regime": {
            lab: {"total_return": _round(compound_returns(rs)), "n_days": len(rs)}
            for lab, rs in sorted(buckets.items())
        },
        "regime_proxy": f"simple trailing-{PRIMARY_LOOKBACK} trend sign from frozen prices",
        "note": "Descriptive; regime proxy derived only from frozen V002 bars; no look-ahead.",
    }


def basket_vs_per_asset(per_asset_oos: dict, basket_oos_return: Optional[float]) -> dict:
    """Compare the allocate-once equal-weight basket OOS view against per-asset
    N=20 OOS, quantifying how much edge survives equal-weight basketing."""
    per = {a: _round(m.get("total_return")) for a, m in per_asset_oos.items()}
    vals = [v for v in per.values() if v is not None]
    avg = sum(vals) / len(vals) if vals else None
    return {
        "per_asset_oos_total_return": per,
        "equal_weight_mean_of_per_asset": _round(avg),
        "allocate_once_basket_oos_total_return": _round(basket_oos_return),
        "edge_retained_vs_mean": (
            _round(basket_oos_return - avg)
            if (basket_oos_return is not None and avg is not None) else None),
        "construction": "allocate-once, no daily rebalance (unchanged); reporting clarification only.",
    }


def parameter_neighborhood(results_by_n: Optional[dict] = None) -> dict:
    """BOUNDED, pre-registered stability probe around N=20 (default {18,20,22}).

    Reports each neighborhood lookback's OOS total return as a *sensitivity*
    surface so the reader can see N=20 is locally smooth, not a knife-edge. The
    winner is hard-fixed at N=20 and is NEVER re-selected from this probe. If no
    results are supplied (build-time schema), the surface is empty but the bounds
    and the no-optimization guard are still declared."""
    surface = {}
    if results_by_n:
        for n in PARAMETER_NEIGHBORHOOD:
            if n in results_by_n:
                surface[str(n)] = _round(results_by_n[n].get("oos_total_return"))
    return {
        "neighborhood": list(PARAMETER_NEIGHBORHOOD),
        "winner_fixed_at": PRIMARY_LOOKBACK,
        "is_sensitivity_not_optimization": NEIGHBORHOOD_IS_SENSITIVITY_NOT_OPTIMIZATION,
        "winner_reselected_from_probe": False,
        "oos_total_return_by_n": surface,
        "guard": ("Bounded pre-registered neighborhood; stability evidence only; "
                  "the winner is NOT re-selected. Run only if the plan authorizes it."),
    }


# ---------------------------------------------------------------------------
# Schema assembler + serialization (read-only).
# ---------------------------------------------------------------------------

def build_deeper_validation_schema(inputs: Optional[dict] = None) -> dict:
    """Assemble the deeper-validation report schema.

    With ``inputs=None`` this returns the BUILD-time capability contract: every
    required section is present as a declared placeholder (``computed=False``) so
    consumers can see the full shape without any backtest having run. With
    ``inputs`` supplied (e.g. unit tests, or a future approved execution feeding
    real N=20 OOS series), each section is computed from those inputs.
    """
    computed = inputs is not None
    sections: dict = {}

    if not computed:
        for name in REQUIRED_SECTIONS:
            sections[name] = {"computed": False,
                              "description": _section_description(name)}
    else:
        dr = inputs.get("daily_returns", [])
        pa = inputs.get("per_asset_oos", {})
        pat = inputs.get("per_asset_trades", pa)
        sections["yearly_oos_breakdown"] = yearly_oos_breakdown(dr)
        sections["monthly_return_drawdown_profile"] = monthly_return_drawdown_profile(dr)
        sections["per_asset_consistency"] = per_asset_consistency(pa)
        sections["trade_count_and_turnover"] = trade_count_and_turnover(pat)
        sections["fee_slippage_stress"] = fee_slippage_stress(
            inputs.get("trade_gross_returns", []))
        sections["outlier_sensitivity"] = outlier_sensitivity(
            inputs.get("trade_returns", []))
        sections["regime_sensitivity"] = regime_sensitivity(
            dr, inputs.get("regime_labels", []))
        sections["basket_vs_per_asset"] = basket_vs_per_asset(
            pa, inputs.get("basket_oos_return"))
        sections["parameter_neighborhood"] = parameter_neighborhood(
            inputs.get("neighborhood_results"))

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "config_name": CONFIG_NAME,
        "build_only": True,
        "is_execution_result": False,
        "ran_backtest": False,
        "primary_lookback": PRIMARY_LOOKBACK,
        "reference_lookback": REFERENCE_LOOKBACK,
        "parameter_neighborhood": list(PARAMETER_NEIGHBORHOOD),
        "neighborhood_is_sensitivity_not_optimization": NEIGHBORHOOD_IS_SENSITIVITY_NOT_OPTIMIZATION,
        "baseline_round_trip_bps": BASELINE_ROUND_TRIP_BPS,
        "per_asset_oos_trade_floor": PER_ASSET_OOS_TRADE_FLOOR,
        "computed": computed,
        "required_sections": list(REQUIRED_SECTIONS),
        "sections": sections,
        "safety_flags": dict(SAFETY_FLAGS),
        "lane_status_unchanged": "WATCH / MIXED",
        "readiness_status_unchanged": "NOT_READY_FOR_REAL_DATA",
        "source_plan": "reports/crypto_d1_momentum_n20_deeper_validation_plan/report.json",
        "non_authorization": ("BUILD ONLY capability. Runs no backtest, executes "
                              "no task, mutates no dataset, and authorizes no "
                              "paper/live/broker/exchange/order/fetch action. No "
                              "ACTIVE/STRONG promotion. No Bundle 23."),
    }


def _section_description(name: str) -> str:
    return {
        "yearly_oos_breakdown": "Per-calendar-year compounded OOS return per asset (read-only slice; no re-split).",
        "monthly_return_drawdown_profile": "Per-month OOS return + rolling max-drawdown; worst month, longest drawdown.",
        "per_asset_consistency": "BTC/ETH/SOL N=20 OOS sign/floor/drawdown/turnover; flags any single carrier asset.",
        "trade_count_and_turnover": "OOS trade counts + turnover; per-asset 20-trade floor clearance; family total.",
        "fee_slippage_stress": "Re-price the SAME N=20 OOS ledger at 150/180/240 bps; breakeven cost. Sensitivity only.",
        "outlier_sensitivity": "Recompute excluding best/worst and small top-k trades; unmodified figure stays official.",
        "regime_sensitivity": "Bucket OOS by a pre-declared trailing-trend regime proxy from frozen prices; no look-ahead.",
        "basket_vs_per_asset": "Allocate-once equal-weight basket OOS vs per-asset N=20; how much edge survives basketing.",
        "parameter_neighborhood": "Bounded {18,20,22} stability probe; sensitivity not optimization; winner fixed at N=20.",
    }.get(name, name)


def to_stable_json(obj: dict) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(schema: dict) -> str:
    lines = ["# Crypto-D1 Momentum N=20 — Deeper-Validation capability (BUILD ONLY)", ""]
    lines.append(f"- config_name: `{schema.get('config_name')}`")
    lines.append(f"- **build_only: {schema.get('build_only')}  |  ran_backtest: "
                 f"{schema.get('ran_backtest')}  |  is_execution_result: "
                 f"{schema.get('is_execution_result')}**")
    lines.append(f"- primary_lookback: {schema.get('primary_lookback')}  |  "
                 f"neighborhood (sensitivity only): {schema.get('parameter_neighborhood')}")
    lines.append(f"- lane: {schema.get('lane_status_unchanged')}  |  "
                 f"readiness: {schema.get('readiness_status_unchanged')}")
    lines += ["", "## Required validation sections", ""]
    for name in schema.get("required_sections", []):
        lines.append(f"- **{name}** — {_section_description(name)}")
    lines += ["", "## Safety flags (all non-authorizing)", ""]
    for k, v in sorted(schema.get("safety_flags", {}).items()):
        lines.append(f"- {k}: {v}")
    lines += ["", schema.get("non_authorization", ""), ""]
    return "\n".join(lines) + "\n"


def write_build_report(base: Path, schema: dict) -> list:
    """Opt-in writer. Writes ONLY under the single build folder. Returns the
    repo-relative paths written."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "capability_schema.json"
    md_path = out_dir / "capability_schema.md"
    json_path.write_text(to_stable_json(schema), encoding="utf-8")
    md_path.write_text(render_markdown(schema), encoding="utf-8")
    return [json_path.relative_to(base).as_posix(),
            md_path.relative_to(base).as_posix()]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Crypto-D1 N=20 deeper-validation capability (BUILD ONLY; "
                    "runs no backtest, executes nothing).")
    parser.add_argument("--base", default=None, help="repo root (default: cwd)")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument("--write", action="store_true",
                        help="ALSO write capability_schema.json/.md under "
                             "reports/crypto_d1_momentum_n20_deeper_validation_build/")
    args = parser.parse_args(argv)
    base = Path(args.base) if args.base else Path(".")
    schema = build_deeper_validation_schema(None)  # build-time contract only
    if args.write:
        written = write_build_report(base, schema)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(render_markdown(schema) if args.format == "md"
                     else to_stable_json(schema))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
