"""Phase-1 INDEX-LEVEL VRP feasibility (EXPLORATORY, READ-ONLY).

Deterministic, index-level volatility-risk-premium feasibility for BTC and ETH: compare DVOL
implied volatility (Deribit 30-day implied-vol INDEX, close) to SUBSEQUENT realized volatility
of spot, using ONLY the local frozen DVOL (data/deribit_iv_universe/) + frozen spot OHLCV
(data/broad_crypto_universe_c23_c24/). Both gitignored, exploratory.

NOT a tradeable options backtest. This is an index-level PROXY study only: it computes the
spread implied_vol - subsequent_realized_vol and asks whether the premium is positive, durable
ex-2021, present recently, and not destroyed by crash windows. DVOL is a 30-day constant-
maturity INDEX, not a delta-hedged straddle P&L.

It runs NO fetch, NO option-chain access, NO per-strike / straddle / delta-hedge simulation, NO
optimization, NO labels/replay; activates/promotes NOTHING; writes NO files.

FIXED PARAMETERS (reported, NOT optimized):
  forward realized-vol windows = 7 / 14 / 30 days (main test = 30d)
  realized vol = stdev(daily log returns over the forward window) * sqrt(365) * 100  (annualized
    %, matching DVOL units)
  spread(t,W) = DVOL_close(t) - realized_vol(t -> t+W)   [strict date align, no forward-fill]
MARCH-2020 is NOT covered (DVOL launched ~2021) -- disclosed.
"""
from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DVOL_RAW = REPO_ROOT / "data" / "deribit_iv_universe" / "raw"
OHLCV_RAW = REPO_ROOT / "data" / "broad_crypto_universe_c23_c24" / "raw"

CURRENCIES = ("BTC", "ETH")
SPOT_OF = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
FWD_WINDOWS = (7, 14, 30)
MAIN_WINDOW = 30
ANNUALIZE = math.sqrt(365.0)
MARCH_2020_COVERED = False

CRASH_WINDOWS = (
    {"name": "2021-05 China-ban/flush", "start": "2021-05-12", "end": "2021-05-31"},
    {"name": "2022-06 Luna/3AC", "start": "2022-06-10", "end": "2022-06-30"},
    {"name": "2022-11 FTX collapse", "start": "2022-11-06", "end": "2022-11-30"},
    {"name": "2024-08 yen-carry unwind", "start": "2024-08-01", "end": "2024-08-15"},
    {"name": "2025-2026 later drawdowns (sample)", "start": "2025-01-01", "end": "2026-06-21"},
)


def _dvol_close(currency: str) -> dict[str, float]:
    p = DVOL_RAW / ("%s_dvol_1d.csv" % currency)
    return {r["datetime"][:10]: float(r["close"])
            for r in csv.DictReader(open(p, encoding="utf-8"))}


def _spot_closes(currency: str) -> dict[str, float]:
    p = OHLCV_RAW / ("%s_1d.csv" % SPOT_OF[currency])
    return {r["date"][:10]: float(r["close"]) for r in csv.DictReader(open(p, encoding="utf-8"))}


def _fwd_realized_vol(closes: dict[str, float], window: int) -> dict[str, float]:
    """Annualized % realized vol of spot over the FORWARD `window` daily log returns after each
    date. No forward-fill: requires `window` consecutive subsequent daily returns."""
    ds = sorted(closes)
    logret = {ds[i]: math.log(closes[ds[i]] / closes[ds[i - 1]])
              for i in range(1, len(ds)) if closes[ds[i - 1]] > 0 and closes[ds[i]] > 0}
    rds = sorted(logret)
    out: dict[str, float] = {}
    for i in range(len(rds)):
        # forward window = returns strictly AFTER day rds[i]
        fwd = rds[i + 1:i + 1 + window]
        if len(fwd) < window:
            continue
        vals = [logret[d] for d in fwd]
        m = sum(vals) / len(vals)
        sd = math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))
        out[rds[i]] = sd * ANNUALIZE * 100.0
    return out


def _summ(spreads: list[float]) -> dict:
    n = len(spreads)
    if n == 0:
        return {"n": 0}
    s = sorted(spreads)
    mean = sum(s) / n
    median = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    hit = sum(1 for x in spreads if x > 0) / n
    return {"n": n, "avg_spread": mean, "median_spread": median, "hit_rate": hit,
            "worst_spread": s[0], "best_spread": s[-1]}


def _compound_window(spread_by_date: dict[str, float], pred) -> dict:
    return _summ([v for d, v in spread_by_date.items() if pred(d)])


def evaluate_currency(currency: str) -> dict:
    dvol = _dvol_close(currency)
    closes = _spot_closes(currency)
    out = {"currency": currency, "windows": {}}
    main_spread_by_date: dict[str, float] = {}
    for w in FWD_WINDOWS:
        rv = _fwd_realized_vol(closes, w)
        # align: dates where DVOL implied exists AND forward realized exists
        common = sorted(d for d in dvol if d in rv)
        spreads = {d: dvol[d] - rv[d] for d in common}
        out["windows"][w] = {**_summ(list(spreads.values())),
                             "first": common[0] if common else None,
                             "last": common[-1] if common else None}
        if w == MAIN_WINDOW:
            main_spread_by_date = spreads
    # year-by-year + ex-2021 + recent on the MAIN window
    years = sorted({d[:4] for d in main_spread_by_date})
    out["yearly"] = {y: _compound_window(main_spread_by_date, lambda d, y=y: d[:4] == y)
                     for y in years}
    out["ex_2021"] = _compound_window(main_spread_by_date, lambda d: d[:4] != "2021")
    out["y2024_2026"] = _compound_window(main_spread_by_date,
                                         lambda d: "2024" <= d[:4] <= "2026")
    out["crash_windows"] = {
        c["name"]: _compound_window(main_spread_by_date,
                                    lambda d, c=c: c["start"] <= d <= c["end"])
        for c in CRASH_WINDOWS}
    out["main_spread_by_date"] = main_spread_by_date
    return out


def evaluate() -> dict:
    return {c: evaluate_currency(c) for c in CURRENCIES}


def _row(label, m):
    if not m.get("n"):
        return "  %-26s (no data)" % label
    return ("  %-26s n=%4d  avg %+6.1f  med %+6.1f  hit %4.1f%%  worst %+7.1f  best %+6.1f"
            % (label, m["n"], m["avg_spread"], m["median_spread"], 100 * m["hit_rate"],
               m["worst_spread"], m["best_spread"]))


def main() -> int:
    r = evaluate()
    print("=" * 84)
    print("PHASE-1 INDEX-LEVEL VRP FEASIBILITY -- DVOL implied vs SUBSEQUENT realized vol")
    print("  (EXPLORATORY index-level PROXY; NOT a tradeable options backtest)")
    print("=" * 84)
    print("units: annualized vol %% ; spread = implied(DVOL close) - subsequent realized vol ; "
          "windows 7/14/30d (main=30d) ; March-2020 covered: %s" % MARCH_2020_COVERED)
    for c in CURRENCIES:
        cc = r[c]
        w30 = cc["windows"][MAIN_WINDOW]
        print("\n#### %s  (30d window: %s -> %s) ####" % (c, w30.get("first"), w30.get("last")))
        for w in FWD_WINDOWS:
            print(_row("fwd realized %dd" % w, cc["windows"][w]))
        print("  -- year-by-year (30d) --")
        for y in sorted(cc["yearly"]):
            print(_row("  %s" % y, cc["yearly"][y]))
        print(_row("ex-2021 (30d)", cc["ex_2021"]))
        print(_row("2024-2026 (30d)", cc["y2024_2026"]))
        print("  -- crash windows (30d) --")
        for name, m in cc["crash_windows"].items():
            print(_row("  " + name, m))
    # combined summary (main window)
    print("\n#### COMBINED BTC+ETH (30d) ####")
    allsp = []
    for c in CURRENCIES:
        allsp += list(r[c]["main_spread_by_date"].values())
    print(_row("BTC+ETH pooled", _summ(allsp)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
