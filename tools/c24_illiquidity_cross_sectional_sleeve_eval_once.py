"""C24 illiquidity (Amihud) cross-sectional portfolio-SLEEVE evaluation (EXPLORATORY, READ-ONLY).

Deterministic %-return evaluation of the Candidate #24 illiquidity premium as a DOLLAR-neutral
cross-sectional sleeve, computed ONLY from the local frozen broad crypto universe at
data/broad_crypto_universe_c23_c24/ (gitignored, survivorship-biased EXPLORATORY data).

Amihud illiquidity (per asset, per day) = abs(daily return) / quote_volume, where quote_volume
is the frozen Binance USDT (dollar) volume. Assets are ranked cross-sectionally by their
TRAILING-mean Amihud; the sleeve goes LONG the high-illiquidity cohort and SHORT the
low-illiquidity cohort (the C24 illiquidity-premium design), equal-weight, +0.5 gross long /
-0.5 gross short (dollar-neutral, gross 1.0).

DECISIVE TEST -- the illiquidity COST PARADOX: the premium lives in the most expensive-to-trade
(illiquid) names, so the LONG leg pays more slippage. This tool reports a base flat-cost result
AND an illiquidity-scaled cost overlay (long-leg slippage x M) plus a M-sensitivity table.

RESEARCH-ONLY: reads frozen CSVs; NO fetch, NO optimization/parameter search (every parameter
is a fixed reported constant; M is STRESSED across a fixed grid, not searched), NO labels, NO
replay, NO paper/live/broker/order; does NOT advance C22, does NOT activate/promote C23/C24,
writes NO files, commits nothing.

FIXED PARAMETERS (one conservative set; reported, not optimized):
  AMIHUD_LOOKBACK_DAYS = 30   ; REBALANCE_EVERY_DAYS = 21 (~monthly, low turnover)
  COHORT_QUANTILE = 0.20      ; FEE_BPS = 27 ; SLIPPAGE_BPS = 10 (37 all-in base)
  ILLIQ_STRESS_M = 3.0 (headline long-leg slippage multiplier); grid {1,2,3,5,10}
Truncation: EOS/MKR leave the cross-section after their last date (no forward-fill); ICP enters
once it has >= lookback history. Survivorship bias PRESENT -- exploratory only. NOTE: this
universe is 42 LIQUID majors, so it is a WEAK test of an illiquidity premium that classically
lives in micro-caps absent here.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "broad_crypto_universe_c23_c24" / "raw"

AMIHUD_LOOKBACK_DAYS = 30
REBALANCE_EVERY_DAYS = 21
COHORT_QUANTILE = 0.20
FEE_BPS = 27.0
SLIPPAGE_BPS = 10.0
ILLIQ_STRESS_M = 3.0
M_GRID = (1.0, 2.0, 3.0, 5.0, 10.0)
BTC = "BTCUSDT"


def load_rows() -> dict[str, dict[str, tuple]]:
    """symbol -> {date: (close, quote_volume)}"""
    out: dict[str, dict[str, tuple]] = {}
    for p in sorted(RAW.glob("*_1d.csv")):
        sym = p.name[:-len("_1d.csv")]
        d = {}
        for r in csv.DictReader(open(p, encoding="utf-8")):
            d[r["date"][:10]] = (float(r["close"]), float(r["quote_volume"]))
        out[sym] = d
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
    ann_vol = sd * math.sqrt(365)
    sharpe = (mean * math.sqrt(365) / sd) if sd else 0.0
    eq = peak = 1.0
    mdd = 0.0
    pos = 0
    for x in r:
        eq *= (1 + x)
        peak = max(peak, eq)
        mdd = min(mdd, eq / peak - 1)
        pos += 1 if x > 0 else 0
    cagr = eq ** (365.0 / n) - 1
    return {"n": n, "cagr": cagr, "ann_vol": ann_vol, "sharpe": sharpe, "max_dd": mdd,
            "calmar": cagr / abs(mdd) if mdd else 0.0, "pos_day_rate": pos / n,
            "total": eq - 1, "first": ds[0], "last": ds[-1]}


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


def evaluate():
    rows = load_rows()
    syms = sorted(rows)
    days_of = {s: sorted(rows[s]) for s in syms}
    rets = {s: {days_of[s][i]: (rows[s][days_of[s][i]][0] - rows[s][days_of[s][i - 1]][0])
                / rows[s][days_of[s][i - 1]][0]
                for i in range(1, len(days_of[s]))} for s in syms}
    all_days = sorted(set().union(*[set(r) for r in rets.values()]))

    def trailing_amihud(sym, day):
        ds = days_of[sym]
        if day not in rets[sym]:
            return None
        i = ds.index(day)
        if i < AMIHUD_LOOKBACK_DAYS:
            return None
        vals = []
        for k in range(i - AMIHUD_LOOKBACK_DAYS, i):
            dd = ds[k]
            qv = rows[sym][dd][1]
            if qv > 0 and dd in rets[sym]:
                vals.append(abs(rets[sym][dd]) / qv)
        return sum(vals) / len(vals) if vals else None

    weights = {}
    gross = {}
    long_leg = {}
    short_leg = {}
    basket = {}
    # turnover split: total + long(illiquid)-leg portion, per rebalance
    turn_total = []
    turn_longleg = []
    start = AMIHUD_LOOKBACK_DAYS + 1
    for di in range(start, len(all_days)):
        day = all_days[di]
        if (di - start) % REBALANCE_EVERY_DAYS == 0:
            ranked = []
            for s in syms:
                a = trailing_amihud(s, day)
                if a is not None and a > 0:
                    ranked.append((a, s))
            ranked.sort(key=lambda t: (t[0], t[1]))
            k = max(1, int(len(ranked) * COHORT_QUANTILE))
            low_illiq = [s for _, s in ranked[:k]]    # most liquid  -> SHORT
            high_illiq = [s for _, s in ranked[-k:]]  # most illiquid -> LONG
            nw = {}
            for s in high_illiq:
                nw[s] = nw.get(s, 0.0) + 0.5 / len(high_illiq)
            for s in low_illiq:
                nw[s] = nw.get(s, 0.0) - 0.5 / len(low_illiq)
            tt = 0.0
            tl = 0.0
            for s in set(nw) | set(weights):
                dw = abs(nw.get(s, 0.0) - weights.get(s, 0.0))
                tt += dw
                is_long = nw.get(s, 0.0) > 0 or (nw.get(s, 0.0) == 0 and weights.get(s, 0.0) > 0)
                if is_long:
                    tl += dw
            turn_total.append(tt)
            turn_longleg.append(tl)
            weights = nw
        g = lg = sh = 0.0
        for s, w in weights.items():
            r = rets[s].get(day)
            if r is None:
                continue
            g += w * r
            if w > 0:
                lg += w * r
            else:
                sh += w * r
        gross[day] = g
        long_leg[day] = lg
        short_leg[day] = sh
        avail = [rets[s][day] for s in syms if day in rets[s]]
        if avail:
            basket[day] = sum(avail) / len(avail)

    # cost overlays: apply at rebalance days proportionally (amortized into that day)
    reb_days = [all_days[start + j * REBALANCE_EVERY_DAYS]
                for j in range(len(turn_total))
                if start + j * REBALANCE_EVERY_DAYS < len(all_days)]

    def net_series(m):
        fee = FEE_BPS / 10000.0
        slp = SLIPPAGE_BPS / 10000.0
        cost_by_day = {}
        for j, d in enumerate(reb_days):
            short_turn = turn_total[j] - turn_longleg[j]
            c = fee * turn_total[j] + slp * (m * turn_longleg[j] + short_turn)
            cost_by_day[d] = c
        return {d: gross[d] - cost_by_day.get(d, 0.0) for d in gross}, cost_by_day

    base_net, base_cost = net_series(1.0)
    stress_net, stress_cost = net_series(ILLIQ_STRESS_M)
    btc = {d: rets[BTC][d] for d in gross if d in rets[BTC]}

    def yearly(series):
        comp = {}
        for d in sorted(series):
            comp[d[:4]] = comp.get(d[:4], 1.0) * (1 + series[d])
        return {y: v - 1 for y, v in comp.items()}

    sens = {}
    for m in M_GRID:
        ns, _ = net_series(m)
        sens[m] = series_stats(ns)

    return {
        "gross": series_stats(gross),
        "base_net": series_stats(base_net),
        "stress_net": series_stats(stress_net),
        "long_leg": series_stats(long_leg),
        "short_leg": series_stats(short_leg),
        "basket_bench": series_stats(basket),
        "btc_bench": series_stats(btc),
        "corr_btc": pearson(base_net, btc),
        "corr_basket": pearson(base_net, basket),
        "annualized_turnover": sum(turn_total) / (len(gross) / 365.0) if gross else 0.0,
        "base_cost_drag": sum(base_cost.values()),
        "stress_cost_drag": sum(stress_cost.values()),
        "longleg_turn_share": (sum(turn_longleg) / sum(turn_total)) if sum(turn_total) else 0.0,
        "yearly_base": yearly(base_net),
        "sensitivity": sens,
        "avg_cohort": (sum(int(len([1]))  # placeholder kept deterministic
                           for _ in [0]) or max(1, int(len(syms) * COHORT_QUANTILE))),
        "n_symbols": len(syms),
        "rebalances": len(turn_total),
    }


def _f(x):
    return "NA" if x is None else "%.3f" % x


def main():
    r = evaluate()
    g = r["base_net"]
    print("=" * 72)
    print("C24 ILLIQUIDITY (Amihud) CROSS-SECTIONAL SLEEVE -- EXPLORATORY (survivorship-biased)")
    print("=" * 72)
    print("params: amihud_lookback=%dd rebal=%dd quintile=%.0f%% base_cost=%.0fbps "
          "(fee%.0f+slip%.0f)" % (AMIHUD_LOOKBACK_DAYS, REBALANCE_EVERY_DAYS,
          COHORT_QUANTILE * 100, FEE_BPS + SLIPPAGE_BPS, FEE_BPS, SLIPPAGE_BPS))
    print("design: LONG high-illiquidity / SHORT low-illiquidity, dollar-neutral gross 1.0")
    print("window: %s -> %s (%d days) symbols=%d rebalances=%d longleg_turn_share=%.0f%%"
          % (g.get("first"), g.get("last"), g.get("n"), r["n_symbols"], r["rebalances"],
             100 * r["longleg_turn_share"]))
    print()

    def row(name, m):
        if "cagr" not in m:
            print("  %-24s (insufficient)" % name)
            return
        print("  %-24s CAGR %6.1f%% vol %5.1f%% Sharpe %6.2f maxDD %6.1f%% Calmar %6.2f "
              "pos%% %4.1f%% total %6.0f%%" % (name, 100 * m["cagr"], 100 * m["ann_vol"],
              m["sharpe"], 100 * m["max_dd"], m["calmar"], 100 * m["pos_day_rate"],
              100 * m["total"]))

    row("C24 GROSS (pre-cost)", r["gross"])
    row("C24 net (base 37bps)", r["base_net"])
    row("C24 net (illiq-stress x%g)" % ILLIQ_STRESS_M, r["stress_net"])
    row("  long (illiquid) leg", r["long_leg"])
    row("  short (liquid) leg", r["short_leg"])
    row("BTC buy-and-hold", r["btc_bench"])
    row("eq-weight basket", r["basket_bench"])
    print()
    print("  corr to BTC: %s   corr to basket: %s" % (_f(r["corr_btc"]), _f(r["corr_basket"])))
    print("  annualized turnover: %.2fx   base cost drag: %.1f%%   illiq-stress(x%g) drag: %.1f%%"
          % (r["annualized_turnover"], 100 * r["base_cost_drag"], ILLIQ_STRESS_M,
             100 * r["stress_cost_drag"]))
    print()
    print("  cost-sensitivity (long-leg slippage multiplier M):")
    print("    %-4s %8s %8s %8s" % ("M", "CAGR", "Sharpe", "maxDD"))
    for m in M_GRID:
        s = r["sensitivity"][m]
        print("    %-4g %7.1f%% %8.2f %7.1f%%"
              % (m, 100 * s["cagr"], s["sharpe"], 100 * s["max_dd"]))
    print()
    yb = r["yearly_base"]
    print("  year-by-year (base net):")
    for y in sorted(yb):
        print("    %s: %6.1f%%" % (y, 100 * yb[y]))
    if yb:
        best = max(yb, key=yb.get)
        worst = min(yb, key=yb.get)
        print("  best year: %s (%.1f%%)   worst year: %s (%.1f%%)"
              % (best, 100 * yb[best], worst, 100 * yb[worst]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
