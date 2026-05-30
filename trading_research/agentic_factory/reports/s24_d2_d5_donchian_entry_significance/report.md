# S24-D2..D5 - Donchian Entry-Rule Significance

## FINAL VERDICT: `ENTRY_EDGE_NOT_SUPPORTED`

**Validation only. No optimization, no parameter changes, no filters, no trading recommendation.**

- **Run date:** 2026-05-29
- **S24-D1 module commit:** `0394236081db934de5baf9941fccc94e6091dba4`
- **Frozen params:** entry 55 / exit 20 / ATR 20 / stop 2.0 / no pyramiding / R-only
- **Random baseline:** n_iter=5000, IS seed 2403, OOS seed 2404, same-count, no-lookahead

---

## S23 WATCH context

- IS 2013-2022: 66 trades, +10.5421R, PF 1.31, expectancy +0.16R/trade, max DD 6.34R
- OOS 2023-2025: 16 trades, +11.37R, PF 2.41, expectancy +0.71R/trade, max DD 3.0R
- S23 final verdict: **WATCH (not deployable)**

---

## Signal extraction method

- **Engine:** engine/donchian_daily.py (UNCHANGED; helpers imported read-only)
- **Raw long signal rule:** For bar i with i>=max(entry_channel=55, atr_period+1=21): a LONG breakout signal when bars[i].high > prior 55-day high (channel over bars[i-55:i], EXCLUDING current bar), with a valid prior-55 channel and Wilder ATR(20) at i-1 > 0. This matches the engine's exact LONG entry trigger condition, WITHOUT the in-position filter / exit / stop / sizing.
- **Primary test:** Raw long entry rule via engine/signal_significance.summarize_significance (the module's intended use: raw entry signal vs same-count random darts; long forward-return convention).
- **Descriptive robustness test:** Direction-aware check on the ACTUAL realized entries (both long and short) using a directional forward return (long:(c1-c0)/c0; short:(c0-c1)/c0) against a random baseline with the SAME long/short mix. Labeled descriptive-only; not the module's long-only path.
- **CORRECTION:** Earlier S23 notes implied long-only (true only for the 2013-only D10 slice). Over the full continuous streams the frozen engine is BIDIRECTIONAL: realized IS = 45 long / 21 short; realized OOS = 9 long / 7 short.

---

## Signal counts

| Window | Bars | Raw long sig | Raw short sig | Realized trades | Realized dirs | First sig | Last sig |
|---|---|---|---|---|---|---|---|
| IS | 3079 | 567 | 97 | 66 | {'long': 45, 'short': 21} | 2013-04-10 | 2022-12-13 |
| OOS | 934 | 164 | 23 | 16 | {'long': 9, 'short': 7} | 2023-03-22 | 2025-10-30 |

**Signal-vs-trade relation:** Raw long signals (IS 567 / OOS 164) vastly exceed realized trades (IS 66 / OOS 16) for three reasons: (1) IN-POSITION FILTERING - simulate() ignores any new breakout while a position is open, so only breakouts that fire while FLAT become trades (only 45 of 567 IS raw long triggers became long entries); (2) the realized set also contains SHORT entries (21 IS / 7 OOS) which are not in the long-signal set; (3) warmup (first 55 bars / ATR seed) removes early bars. Net: realized_trades = (flat-state long breakouts) + (flat-state short breakouts).

---

## IS 2013-2022 - raw long entry rule (PRIMARY, module)

| Horizon | Real n | Real mean | Baseline mean | Baseline std | Percentile | p-value | Verdict |
|---|---|---|---|---|---|---|---|
| 5 | 567 | +0.00117 | +0.00257 | 0.00094 | 7.5 | 0.9246 | **NO_EDGE** |
| 10 | 567 | +0.00164 | +0.00516 | 0.00129 | 0.4 | 0.9956 | **NO_EDGE** |
| 20 | 566 | +0.00316 | +0.01047 | 0.00178 | 0.0 | 1.0000 | **NO_EDGE** |
| 40 | 565 | +0.00839 | +0.02116 | 0.00241 | 0.0 | 1.0000 | **NO_EDGE** |

## OOS 2023-2025 - raw long entry rule (PRIMARY, module)

| Horizon | Real n | Real mean | Baseline mean | Baseline std | Percentile | p-value | Verdict |
|---|---|---|---|---|---|---|---|
| 5 | 164 | +0.00135 | +0.00490 | 0.00176 | 2.4 | 0.9764 | **NO_EDGE** |
| 10 | 164 | +0.00392 | +0.00963 | 0.00232 | 0.6 | 0.9936 | **NO_EDGE** |
| 20 | 164 | +0.01037 | +0.01880 | 0.00317 | 0.5 | 0.9948 | **NO_EDGE** |
| 40 | 164 | +0.02601 | +0.03634 | 0.00429 | 1.0 | 0.9904 | **NO_EDGE** |

## IS - realized bidirectional entries (DESCRIPTIVE, direction-aware)

| Horizon | Real n | Real mean (dir) | Baseline mean (dir) | Percentile | p-value | Verdict |
|---|---|---|---|---|---|---|
| 5 | 66 | -0.00184 | +0.00094 | 17.9 | 0.8212 | **NO_EDGE** |
| 10 | 66 | +0.00178 | +0.00184 | 48.6 | 0.5143 | **NO_EDGE** |
| 20 | 65 | +0.00495 | +0.00393 | 56.8 | 0.4319 | **INCONCLUSIVE** |
| 40 | 64 | -0.00004 | +0.00763 | 16.8 | 0.8324 | **NO_EDGE** |

## OOS - realized bidirectional entries (DESCRIPTIVE, direction-aware)

| Horizon | Real n | Real mean (dir) | Baseline mean (dir) | Percentile | p-value | Verdict |
|---|---|---|---|---|---|---|
| 5 | 16 | -0.00165 | +0.00048 | 36.4 | 0.6357 | **NO_EDGE** |
| 10 | 16 | -0.00819 | +0.00130 | 12.0 | 0.8798 | **NO_EDGE** |
| 20 | 16 | -0.01100 | +0.00209 | 12.6 | 0.8738 | **NO_EDGE** |
| 40 | 15 | +0.01623 | +0.00432 | 77.2 | 0.2280 | **INCONCLUSIVE** |

---

## Final S24 verdict - `ENTRY_EDGE_NOT_SUPPORTED`

- PRIMARY (raw long entry rule, module): NO_EDGE at ALL four pre-fixed horizons (5/10/20/40) in BOTH IS and OOS. Real mean forward return sits BELOW the random-entry baseline every time (IS percentiles 7.5/0.4/0.0/0.0, p 0.92-1.0; OOS percentiles 2.4/0.6/0.5/1.0, p 0.98-0.99).
- DESCRIPTIVE (realized bidirectional entries, direction-aware): NO_EDGE or INCONCLUSIVE at every horizon in BOTH IS and OOS - never EDGE_LIKELY. Real directional returns are at or below the direction-matched random baseline.
- Real entries are NOT better than random at forward-return prediction; in fact they are typically worse (a breakout enters AFTER an extended move, so the immediate forward window carries mean-reversion drag).
- Because the result is consistent across IS and OOS and across all four horizons, this is NOT_SUPPORTED rather than INCONCLUSIVE.

## What this means for the Donchian candidate

- ENTRY_EDGE_NOT_SUPPORTED: the entry timing does NOT carry predictive edge. S23's positive R most likely came from EXIT / PATH / position-management (fast 2N stops cutting losers, 20-day channel letting winners run) and a few fat-tailed winners - and partly luck given the low trade count.
- The candidate should be PARKED or REFRAMED. Do NOT optimize the entry, do NOT add entry filters, do NOT promote to paper/live.
- If pursued later, reframe as an EXIT/trend-capture study (the edge hypothesis moves to position management, not entry), validated as a fresh branch with its own future OOS.

## Caveats

- Forward-return significance tests the entry's PREDICTIVE timing, not the full strategy P&L (which includes exits/stops/sizing). NOT_SUPPORTED here does not 'disprove' S23's R; it explains that the R is not attributable to entry edge.
- The module's primary path is long-only forward returns; the bidirectional realized-entry test is a hand-rolled descriptive supplement using the same horizons/seeds.
- OOS realized n=16 is small; the descriptive OOS directional result is low-power, but it agrees with the decisive raw-rule result.
- IS and OOS kept SEPARATE for the core judgement; no IS+OOS pooling was used to manufacture significance.

---

**No trading recommendation. No paper/live promotion. No optimization. Engine unchanged.**