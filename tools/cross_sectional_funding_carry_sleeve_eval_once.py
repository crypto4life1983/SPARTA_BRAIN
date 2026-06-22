"""Cross-sectional funding-carry SLEEVE evaluation (EXPLORATORY, READ-ONLY).

Deterministic %-return evaluation of cross_sectional_crypto_funding_carry_market_neutral_v1 as a
DELTA-NEUTRAL multi-asset basis carry, computed ONLY from the local frozen broad OHLCV
(data/broad_crypto_universe_c23_c24/) + frozen broad funding (data/broad_crypto_funding_universe/)
-- both gitignored, survivorship-biased EXPLORATORY data.

DESIGN: each rebalance, rank the 40 funding-allowlist symbols (EOS/MKR excluded) by trailing
funding; SELECT the top cohort of POSITIVE-funding names; hold each as a LONG-SPOT / SHORT-PERP
basis position (the short perp is a HEDGE, not a directional short), equal-weight, 1x basis
notional. A long-spot/short-perp position RECEIVES funding when funding is positive.

DATA LIMITATION (REQUIRED DISCLOSURE): the broad OHLCV is SPOT-ONLY (no perp klines) and funding
mark_price is sparse/zero early, so the full spot-vs-perp BASIS mark-to-market cannot be safely
reconstructed. This is therefore a FUNDING-CASHFLOW-ONLY DELTA-NEUTRAL APPROXIMATION: the sleeve
daily return = funding income on the delta-neutral position (price delta ~0 by construction;
basis convergence assumed ~0 over the hold). funding_rate is the primary cashflow; mark_price is
ignored. This OMITS basis P&L, execution basis slippage beyond the cost overlay, and funding-
crowding compression -- it is an UPPER-ish bound on the harvestable carry, exploratory only.

FIXED PARAMETERS (conservative; reported, NOT optimized):
  FUNDING_LOOKBACK_DAYS=30 ; REBALANCE_EVERY_DAYS=21 ; COHORT_QUANTILE=0.20 (top positive-funding)
  base cost 74 bps two-leg round-trip per newly-opened basis notional; stress {37,150,300} bps
Actual funding CADENCE is used (sum all funding events per calendar day from the CSV, NOT an
assumed 8h). No forward-fill of missing funding or OHLCV. Late-start perps enter after lookback.
Runs NO fetch, NO optimization, NO labels/replay, NO paper/live/broker/order; activates/promotes
NOTHING; writes NO files.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OHLCV_RAW = REPO_ROOT / "data" / "broad_crypto_universe_c23_c24" / "raw"
FUNDING_RAW = REPO_ROOT / "data" / "broad_crypto_funding_universe" / "raw"

FUNDING_LOOKBACK_DAYS = 30
REBALANCE_EVERY_DAYS = 21
COHORT_QUANTILE = 0.20
BASE_COST_BPS = 74.0
STRESS_COST_BPS = (37.0, 150.0, 300.0)
BTC = "BTCUSDT"           # OHLCV + funding share *USDT naming
EXCLUDED = ("EOSUSDT", "MKRUSDT")


def load_funding_daily() -> dict[str, dict[str, float]]:
    """funding symbol -> {date: summed funding_rate that day} (actual cadence, no forward-fill)."""
    out: dict[str, dict[str, float]] = {}
    for p in sorted(FUNDING_RAW.glob("*_funding.csv")):
        sym = p.name[:-len("_funding.csv")]
        d: dict[str, float] = {}
        for r in csv.DictReader(open(p, encoding="utf-8")):
            day = r["datetime"][:10]
            d[day] = d.get(day, 0.0) + float(r["funding_rate"])
        out[sym] = d
    return out


def load_spot_returns() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for p in sorted(OHLCV_RAW.glob("*_1d.csv")):
        sym = p.name[:-len("_1d.csv")]
        closes = {r["date"][:10]: float(r["close"]) for r in csv.DictReader(open(p, encoding="utf-8"))}
        ds = sorted(closes)
        out[sym] = {ds[i]: (closes[ds[i]] - closes[ds[i - 1]]) / closes[ds[i - 1]]
                    for i in range(1, len(ds))}
    return out


def stdev(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def series_stats(series):
    ds = sorted(series)
    r = [series[d] for d in ds]
    n = len(r)
    if n < 10:
        return {"n": n}
    mean = sum(r) / n
    sd = stdev(r)
    eq = peak = 1.0
    mdd = 0.0
    pos = 0
    worst = min(r)
    for x in r:
        eq *= (1 + x)
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
        pos += 1 if x > 0 else 0
    cagr = eq ** (365.0 / n) - 1
    return {"n": n, "cagr": cagr, "ann_vol": sd * math.sqrt(365),
            "sharpe": (mean * math.sqrt(365) / sd) if sd else 0.0,
            "max_dd": mdd, "calmar": cagr / abs(mdd) if mdd else 0.0,
            "pos_day_rate": pos / n, "total": eq - 1, "worst_day": worst,
            "first": ds[0], "last": ds[-1]}


def pearson(x, y):
    common = [d for d in x if d in y]
    if len(common) < 30:
        return None
    xs = [x[d] for d in common]
    ys = [y[d] for d in common]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def _window_stats(series, lo, hi):
    sub = {d: v for d, v in series.items() if lo <= d[:4] <= hi}
    return series_stats(sub) if len(sub) >= 10 else {"n": len(sub)}


def _compound(series, predicate):
    eq = 1.0
    for d in sorted(series):
        if predicate(d):
            eq *= (1 + series[d])
    return eq - 1


def evaluate(cohort_cost_bps=BASE_COST_BPS):
    fund = load_funding_daily()                  # 40 funding symbols
    spot = load_spot_returns()                   # 42 OHLCV (spot) symbols
    syms = sorted(s for s in fund)               # 40 funding-allowlist symbols
    assert not (set(EXCLUDED) & set(syms)), "excluded symbol present in funding universe"
    fdays = {s: sorted(fund[s]) for s in syms}
    all_days = sorted(set().union(*[set(fund[s]) for s in syms]))

    def trailing_funding(sym, day):
        ds = fdays[sym]
        # need >= LOOKBACK days of history before `day`
        prior = [d for d in ds if d < day][-FUNDING_LOOKBACK_DAYS:]
        if len(prior) < FUNDING_LOOKBACK_DAYS:
            return None
        return sum(fund[sym][d] for d in prior) / len(prior)   # avg daily funding

    weights = {}
    gross = {}
    null_broad = {}
    cohort_sizes = []
    captured_funding = []
    cost_by_day = {}
    opened_total = 0.0
    start = FUNDING_LOOKBACK_DAYS + 1
    for di in range(start, len(all_days)):
        day = all_days[di]
        if (di - start) % REBALANCE_EVERY_DAYS == 0:
            ranked = []
            for s in syms:
                tf = trailing_funding(s, day)
                if tf is not None and tf > 0:        # POSITIVE-funding eligible only
                    ranked.append((tf, s))
            ranked.sort(key=lambda t: (t[0], t[1]))
            k = max(1, int(len(ranked) * COHORT_QUANTILE))
            sel = [s for _, s in ranked[-k:]]        # top positive-funding cohort
            cohort_sizes.append(len(sel))
            nw = {s: 1.0 / len(sel) for s in sel} if sel else {}
            opened = sum(max(0.0, nw.get(s, 0.0) - weights.get(s, 0.0))
                         for s in set(nw) | set(weights))
            opened_total += opened
            cost_by_day[day] = opened * (cohort_cost_bps / 10000.0)
            weights = nw
        # daily funding income on the delta-neutral basket (long-spot/short-perp -> receive +fr)
        g = 0.0
        for s, w in weights.items():
            fr = fund[s].get(day)
            if fr is None:                            # no forward-fill
                continue
            g += w * fr
            captured_funding.append(fr)
        gross[day] = g
        # always-on broad null: eq-weight funding across ALL eligible-today symbols (no selection)
        avail = [fund[s][day] for s in syms if day in fund[s]]
        if avail:
            null_broad[day] = sum(avail) / len(avail)

    net = {d: gross[d] - cost_by_day.get(d, 0.0) for d in gross}

    # benchmarks
    btc = spot.get(BTC, {})
    basket = {}
    for d in btc:
        vals = [spot[s][d] for s in spot if d in spot[s]]
        if vals:
            basket[d] = sum(vals) / len(vals)
    btc_w = {d: btc[d] for d in net if d in btc}
    basket_w = {d: basket[d] for d in net if d in basket}

    # always-on BTC/ETH/SOL neutral funding null (subset of broad funding)
    btc3 = {}
    for d in all_days:
        legs = [fund[s][d] for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT") if d in fund.get(s, {})]
        if legs:
            btc3[d] = sum(legs) / len(legs)
    btc3_w = {d: btc3[d] for d in net if d in btc3}

    def yearly(series):
        comp = {}
        for d in sorted(series):
            comp[d[:4]] = comp.get(d[:4], 1.0) * (1 + series[d])
        return {y: v - 1 for y, v in comp.items()}

    return {
        "gross": series_stats(gross),
        "net_base": series_stats(net),
        "null_broad": series_stats(null_broad),
        "btc_bench": series_stats(btc_w),
        "basket_bench": series_stats(basket_w),
        "btc3_funding_null": series_stats(btc3_w),
        "corr_btc": pearson(net, btc),
        "corr_basket": pearson(net, basket),
        "corr_null_broad": pearson(net, null_broad),
        "yearly_net": yearly(net),
        "ex_2021": _compound(net, lambda d: d[:4] != "2021"),
        "y2022_2026": _compound(net, lambda d: "2022" <= d[:4] <= "2026"),
        "y2024_2026": _compound(net, lambda d: "2024" <= d[:4] <= "2026"),
        "top_year_removed": None,   # filled in main
        "funding_income_gross_total": series_stats(gross).get("total"),
        "annualized_turnover": opened_total / (len(gross) / 365.0) if gross else 0.0,
        "base_cost_drag": sum(cost_by_day.values()),
        "avg_cohort_size": sum(cohort_sizes) / len(cohort_sizes) if cohort_sizes else 0,
        "avg_funding_captured": sum(captured_funding) / len(captured_funding) if captured_funding else 0.0,
        "worst_funding_day": series_stats(gross).get("worst_day"),
        "n_funding_symbols": len(syms),
    }


def _f(x):
    return "NA" if x is None else "%.3f" % x


def main():
    r = evaluate()
    yb = r["yearly_net"]
    g = r["net_base"]
    print("=" * 76)
    print("CROSS-SECTIONAL FUNDING CARRY SLEEVE -- FUNDING-CASHFLOW-ONLY DELTA-NEUTRAL APPROX")
    print("  (EXPLORATORY, survivorship-biased; basis mark-to-market NOT reconstructable)")
    print("=" * 76)
    print("params: funding_lookback=%dd rebal=%dd top_quintile_positive_funding=%.0f%% "
          "base_cost=%.0fbps(2-leg)" % (FUNDING_LOOKBACK_DAYS, REBALANCE_EVERY_DAYS,
          COHORT_QUANTILE * 100, BASE_COST_BPS))
    print("window: %s -> %s (%d days) funding_symbols=%d avg_cohort=%.1f rebal_turnover=%.2fx/yr"
          % (g.get("first"), g.get("last"), g.get("n"), r["n_funding_symbols"],
             r["avg_cohort_size"], r["annualized_turnover"]))
    print("avg funding captured/interval-day: %.5f   worst funding day: %.5f"
          % (r["avg_funding_captured"], r["worst_funding_day"]))
    print()

    def row(name, m):
        if "cagr" not in m:
            print("  %-26s (insufficient: n=%s)" % (name, m.get("n")))
            return
        print("  %-26s CAGR %6.1f%% vol %5.1f%% Sharpe %6.2f maxDD %6.1f%% Calmar %6.2f "
              "pos%% %4.1f%% total %6.1f%%" % (name, 100 * m["cagr"], 100 * m["ann_vol"],
              m["sharpe"], 100 * m["max_dd"], m["calmar"], 100 * m["pos_day_rate"],
              100 * m["total"]))

    row("SLEEVE gross (no cost)", r["gross"])
    row("SLEEVE net (74bps)", r["net_base"])
    row("always-on broad null", r["null_broad"])
    row("always-on BTC/ETH/SOL null", r["btc3_funding_null"])
    row("BTC buy-and-hold", r["btc_bench"])
    row("eq-weight basket", r["basket_bench"])
    print()
    print("  corr to BTC: %s | corr to basket: %s | corr to broad null: %s"
          % (_f(r["corr_btc"]), _f(r["corr_basket"]), _f(r["corr_null_broad"])))
    print()
    print("  COST SENSITIVITY (round-trip bps on opened basis notional):")
    print("    %-8s %8s %8s %8s" % ("bps", "CAGR", "Sharpe", "total"))
    for bps in (0.0,) + (BASE_COST_BPS,) + STRESS_COST_BPS:
        rr = evaluate(cohort_cost_bps=bps)["net_base"]
        print("    %-8g %7.1f%% %8.2f %7.1f%%" % (bps, 100 * rr["cagr"], rr["sharpe"],
                                                  100 * rr["total"]))
    print()
    print("  year-by-year (net 74bps):")
    for y in sorted(yb):
        print("    %s: %6.1f%%" % (y, 100 * yb[y]))
    best = max(yb, key=yb.get) if yb else None
    if best:
        print("  best year: %s (%.1f%%)" % (best, 100 * yb[best]))
    print("  ex-2021 compounded: %.1f%% | 2022-2026: %.1f%% | 2024-2026: %.1f%%"
          % (100 * r["ex_2021"], 100 * r["y2022_2026"], 100 * r["y2024_2026"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
