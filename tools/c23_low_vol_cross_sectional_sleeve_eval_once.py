"""C23 low-volatility cross-sectional portfolio-SLEEVE evaluation (EXPLORATORY, READ-ONLY).

Deterministic % -return evaluation of the Candidate #23 low-volatility anomaly as a DOLLAR-
neutral cross-sectional sleeve, computed ONLY from the local frozen broad crypto universe at
data/broad_crypto_universe_c23_c24/ (gitignored, survivorship-biased EXPLORATORY data).

It is RESEARCH-ONLY: reads frozen CSVs, computes a daily percentage-return series for the
long-low-vol / short-high-vol sleeve, and prints metrics + benchmarks. It runs NO fetch, NO
optimization / parameter search (every parameter is a fixed, reported constant), NO labels, NO
replay, NO paper/live/broker/order code; it does NOT advance C22, does NOT activate/promote
C23 or C24, and writes NO files / commits nothing.

FIXED PARAMETERS (conservative defaults; the C23 proposal leaves cohort size / lookback /
rebalance frequency open, so ONE conservative set is chosen and reported -- NOT optimized):
  VOL_LOOKBACK_DAYS = 30      trailing daily-return stdev (realized vol)
  REBALANCE_EVERY_DAYS = 21   ~monthly (low turnover; the C20 churn lesson)
  COHORT_QUANTILE = 0.20      long bottom-20% vol cohort / short top-20% vol cohort
  ALL_IN_ROUND_TRIP_BPS = 37  (27 fee + 10 slippage), applied to rebalance turnover
Construction: equal-weight within each cohort; +0.5 gross long / -0.5 gross short (dollar-
neutral, gross 1.0). Beta is NOT hedged (a hedge overlay adds estimation params) -- residual
beta to the broad basket is MEASURED and reported instead (low-vol longs are low-beta and
high-vol shorts are high-beta, so the dollar-neutral sleeve is expected to carry NEGATIVE
residual beta -- reported, not hidden).
Truncation: EOS/MKR drop out of the cross-section after their last available date (no forward-
fill); ICP enters only once it has >= VOL_LOOKBACK_DAYS of history. Survivorship bias is
PRESENT (Binance-public) -- exploratory only, not a deployment claim.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "broad_crypto_universe_c23_c24" / "raw"

VOL_LOOKBACK_DAYS = 30
REBALANCE_EVERY_DAYS = 21
COHORT_QUANTILE = 0.20
ALL_IN_ROUND_TRIP_BPS = 37.0
COST_PER_TURN = ALL_IN_ROUND_TRIP_BPS / 10000.0
BTC = "BTCUSDT"


def load_closes() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for p in sorted(RAW.glob("*_1d.csv")):
        sym = p.name[:-len("_1d.csv")]
        d: dict[str, float] = {}
        for r in csv.DictReader(open(p, encoding="utf-8")):
            d[r["date"][:10]] = float(r["close"])
        out[sym] = d
    return out


def daily_returns(closes: dict[str, float]) -> dict[str, float]:
    ds = sorted(closes)
    return {ds[i]: (closes[ds[i]] - closes[ds[i - 1]]) / closes[ds[i - 1]]
            for i in range(1, len(ds))}


def stdev(xs: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def series_stats(series: dict[str, float]) -> dict:
    ds = sorted(series)
    r = [series[d] for d in ds]
    n = len(r)
    if n < 10:
        return {"n": n}
    mean = sum(r) / n
    sd = stdev(r)
    ann_vol = sd * math.sqrt(365)
    sharpe = (mean * math.sqrt(365) / sd) if sd else 0.0
    eq = 1.0
    peak = 1.0
    mdd = 0.0
    pos = 0
    for x in r:
        eq *= (1 + x)
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
        if x > 0:
            pos += 1
    cagr = eq ** (365.0 / n) - 1
    calmar = cagr / abs(mdd) if mdd else 0.0
    return {"n": n, "cagr": cagr, "ann_vol": ann_vol, "sharpe": sharpe,
            "max_dd": mdd, "calmar": calmar, "pos_day_rate": pos / n,
            "total": eq - 1, "first": ds[0], "last": ds[-1]}


def pearson(x: dict[str, float], y: dict[str, float]) -> float | None:
    common = [d for d in x if d in y]
    if len(common) < 30:
        return None
    xs = [x[d] for d in common]
    ys = [y[d] for d in common]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def beta(sleeve: dict[str, float], mkt: dict[str, float]) -> float | None:
    common = [d for d in sleeve if d in mkt]
    if len(common) < 30:
        return None
    xs = [mkt[d] for d in common]
    ys = [sleeve[d] for d in common]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    return sxy / sxx if sxx > 0 else None


def evaluate() -> dict:
    closes = load_closes()
    rets = {s: daily_returns(c) for s, c in closes.items()}
    all_days = sorted(set().union(*[set(r) for r in rets.values()]))

    # precompute trailing realized vol per symbol per day index
    sym_days = {s: sorted(rets[s]) for s in rets}

    def realized_vol(sym: str, day: str):
        ds = sym_days[sym]
        if day not in rets[sym]:
            return None
        i = ds.index(day)
        if i < VOL_LOOKBACK_DAYS:
            return None
        window = [rets[sym][ds[k]] for k in range(i - VOL_LOOKBACK_DAYS, i)]
        return stdev(window)

    weights: dict[str, float] = {}
    sleeve: dict[str, float] = {}
    long_leg: dict[str, float] = {}
    short_leg: dict[str, float] = {}
    basket: dict[str, float] = {}
    turnover_events: list[float] = []
    cohort_sizes: list[int] = []

    start_idx = VOL_LOOKBACK_DAYS + 1
    for di in range(start_idx, len(all_days)):
        day = all_days[di]
        # rebalance?
        if (di - start_idx) % REBALANCE_EVERY_DAYS == 0:
            ranked = []
            for s in sorted(rets):
                v = realized_vol(s, day)
                if v is not None and v > 0:
                    ranked.append((v, s))
            ranked.sort(key=lambda t: (t[0], t[1]))  # deterministic tie-break by symbol
            k = max(1, int(len(ranked) * COHORT_QUANTILE))
            longs = [s for _, s in ranked[:k]]
            shorts = [s for _, s in ranked[-k:]]
            cohort_sizes.append(k)
            new_w: dict[str, float] = {}
            for s in longs:
                new_w[s] = new_w.get(s, 0.0) + 0.5 / len(longs)
            for s in shorts:
                new_w[s] = new_w.get(s, 0.0) - 0.5 / len(shorts)
            turn = sum(abs(new_w.get(s, 0.0) - weights.get(s, 0.0))
                       for s in set(new_w) | set(weights))
            turnover_events.append(turn)
            weights = new_w
            cur_longs, cur_shorts = set(longs), set(shorts)
            day_cost = turn * COST_PER_TURN
        else:
            day_cost = 0.0

        # daily sleeve return from held weights (no forward-fill: skip absent returns)
        g = 0.0
        lg = 0.0
        sh = 0.0
        for s, w in weights.items():
            r = rets[s].get(day)
            if r is None:
                continue
            g += w * r
            if w > 0:
                lg += w * r
            else:
                sh += w * r
        sleeve[day] = g - day_cost
        long_leg[day] = lg
        short_leg[day] = sh
        # equal-weight broad basket of assets trading that day
        avail = [rets[s][day] for s in rets if day in rets[s]]
        if avail:
            basket[day] = sum(avail) / len(avail)

    btc = {d: rets[BTC][d] for d in sleeve if d in rets[BTC]}

    # yearly sleeve returns
    yearly: dict[str, float] = {}
    for d in sorted(sleeve):
        y = d[:4]
        yearly[y] = (1 + yearly.get(y, 0.0) + 0.0) if y not in yearly else yearly[y]
    yr_compound: dict[str, float] = {}
    for d in sorted(sleeve):
        y = d[:4]
        yr_compound[y] = (yr_compound.get(y, 1.0)) * (1 + sleeve[d])
    yearly = {y: v - 1 for y, v in yr_compound.items()}

    return {
        "sleeve": series_stats(sleeve),
        "long_leg": series_stats(long_leg),
        "short_leg": series_stats(short_leg),
        "basket_bench": series_stats(basket),
        "btc_bench": series_stats(btc),
        "corr_btc": pearson(sleeve, btc),
        "corr_basket": pearson(sleeve, basket),
        "residual_beta_to_basket": beta(sleeve, basket),
        "avg_turnover_per_rebalance": (sum(turnover_events) / len(turnover_events)
                                       if turnover_events else 0.0),
        "rebalances": len(turnover_events),
        "annualized_turnover": (sum(turnover_events) / (len(sleeve) / 365.0)
                                if sleeve else 0.0),
        "total_cost_drag": sum(turnover_events) * COST_PER_TURN,
        "avg_cohort_size": (sum(cohort_sizes) / len(cohort_sizes)
                            if cohort_sizes else 0),
        "yearly_sleeve": yearly,
        "n_symbols": len(rets),
    }


def main() -> int:
    import json
    r = evaluate()
    s = r["sleeve"]
    print("=" * 70)
    print("C23 LOW-VOL CROSS-SECTIONAL SLEEVE -- EXPLORATORY (survivorship-biased)")
    print("=" * 70)
    print("params: vol_lookback=%dd rebal=%dd quintile=%.0f%% cost=%.0fbps/turn"
          % (VOL_LOOKBACK_DAYS, REBALANCE_EVERY_DAYS, COHORT_QUANTILE * 100,
             ALL_IN_ROUND_TRIP_BPS))
    print("eval window: %s -> %s  (%d days)  symbols=%d  avg_cohort=%.0f/side  rebalances=%d"
          % (s.get("first"), s.get("last"), s.get("n"), r["n_symbols"],
             r["avg_cohort_size"], r["rebalances"]))
    print()

    def row(name, m):
        if "cagr" not in m:
            print("  %-22s (insufficient data)" % name)
            return
        print("  %-22s CAGR %6.1f%% vol %5.1f%% Sharpe %6.2f maxDD %6.1f%% Calmar %6.2f "
              "pos%% %4.1f%% total %7.0f%%"
              % (name, 100 * m["cagr"], 100 * m["ann_vol"], m["sharpe"],
                 100 * m["max_dd"], m["calmar"], 100 * m["pos_day_rate"],
                 100 * m["total"]))

    row("C23 sleeve (net)", r["sleeve"])
    row("  long leg", r["long_leg"])
    row("  short leg", r["short_leg"])
    row("BTC buy-and-hold", r["btc_bench"])
    row("eq-weight basket", r["basket_bench"])
    print()
    print("  corr to BTC:            %s" % _f(r["corr_btc"]))
    print("  corr to broad basket:   %s" % _f(r["corr_basket"]))
    print("  residual beta (basket): %s  (negative => net short-beta, as expected)"
          % _f(r["residual_beta_to_basket"]))
    print("  annualized turnover:    %.2fx   total cost drag: %.1f%%"
          % (r["annualized_turnover"], 100 * r["total_cost_drag"]))
    print()
    print("  year-by-year sleeve net return:")
    for y in sorted(r["yearly_sleeve"]):
        print("    %s: %6.1f%%" % (y, 100 * r["yearly_sleeve"][y]))
    return 0


def _f(x):
    return "NA" if x is None else "%.3f" % x


if __name__ == "__main__":
    raise SystemExit(main())
