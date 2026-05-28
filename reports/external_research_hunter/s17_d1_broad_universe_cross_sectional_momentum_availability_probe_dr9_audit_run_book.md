# s17-d1 broad-universe (24-name) cross-sectional momentum availability probe + DR9 audit RUN_BOOK

**NOT A SEAL** (RUN_BOOK_NOT_SEALED) - **Fresh s17 path** - **Authored:** `2026-05-28T23:40:22.609473Z`
**Framework binding:** DR10 v2 (`78cd22e`) + **walk-forward K13 (`52a3b60`)** -- both bind this s17 candidate.
**Authorization:** `Authorize s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit framework only.`

## 1. Motivation
Selection plan rev2 (`75a22be`) chose T2 (cross-sectional momentum rotation) as the most walk-forward-K13-aligned direction -- relative momentum rotates into each regime's leaders (the structural fix for s16's absolute-trend OOS failure). Cross-sectional momentum needs BREADTH to rank/select -> 24 large-caps across ~8 sectors. Mechanic (lookback/rebalance/top-N) DEFERRED to the s17 Tier-N PLAN.

## 2. Vendor
Tiingo split_only (proven). `TIINGO_API_KEY` env-only, never printed.

## 3. Universe (24 names; 12 reusable DR9-passed, 12 fresh)
| Symbol | Sector | Exch | Data status | Splits in window |
|---|---|---|---|---|
| AAPL | Information Technology | NASDAQ | REUSE (DR9-passed) | 2020-08-31 4.0:1 |
| MSFT | Information Technology | NASDAQ | REUSE (DR9-passed) | none |
| NVDA | Information Technology | NASDAQ | REUSE (DR9-passed) | 2021-07-20 4.0:1; 2024-06-10 10.0:1 |
| JPM | Financials | NYSE | REUSE (DR9-passed) | none |
| XOM | Energy | NYSE | REUSE (DR9-passed) | none |
| UNH | Health Care | NYSE | REUSE (DR9-passed) | none |
| WMT | Consumer Staples | NYSE | REUSE (DR9-passed) | 2024-02-26 3.0:1 |
| KO | Consumer Staples | NYSE | REUSE (DR9-passed) | none |
| META | Communication Services | NASDAQ | REUSE (DR9-passed) | none |
| AMZN | Consumer Discretionary | NASDAQ | REUSE (DR9-passed) | 2022-06-06 20.0:1 |
| JNJ | Health Care | NYSE | REUSE (DR9-passed) | none |
| CVX | Energy | NYSE | REUSE (DR9-passed) | none |
| GOOGL | Communication Services | NASDAQ | FRESH | 2022-07-18 20.0:1 |
| V | Financials | NYSE | FRESH | none |
| MA | Financials | NYSE | FRESH | none |
| HD | Consumer Discretionary | NYSE | FRESH | none |
| PG | Consumer Staples | NYSE | FRESH | none |
| COST | Consumer Staples | NASDAQ | FRESH | none |
| ABBV | Health Care | NYSE | FRESH | none |
| MRK | Health Care | NYSE | FRESH | none |
| BAC | Financials | NYSE | FRESH | none |
| CAT | Industrials | NYSE | FRESH | none |
| DIS | Communication Services | NYSE | FRESH | none |
| COP | Energy | NYSE | FRESH | none |

Reusable (DR9-passed at `245ac0d` / `ec856253`): AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX. Fresh fetch + full DR9: GOOGL, V, MA, HD, PG, COST, ABBV, MRK, BAC, CAT, DIS, COP.

## 4. Output + manifest
Dir `data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/`; files `<SYM>_ohlcv_1d_20190102_20251230.csv` (x24) + `s17_d1_broad_universe_cross_sectional_momentum_step02b_fetch_manifest.json`. Schema `sparta.s17.broad_universe_cross_sectional_momentum.step02b_fetch_manifest.v1`. Window 2019-01-02->2025-12-30 (OOS 2024-01-02..2025-12-30 LOCKED, not inspected).

## 5. DR9 audit framework (thresholds carried; immutable)
gap_continuity >=0.95 - max_gap_ratio <=0.30 - quality <=5 - roll NOT_APPLICABLE - split-event-consistency PASS. **Key fresh split: GOOGL 20:1 (2022-07-18)** -- verify ratio ~1.0 under split_only. MRK Organon spin-off (2021-06) + COST 2023 special dividend = INFORMATIONAL (one-day price drops; not DR9 fails). Reused AAPL/NVDA/AMZN/WMT splits already verified.

## 6. K9-per-fold + walk-forward K13 reachability (the load-bearing concern)
Cross-sectional momentum rotation is LOW-TURNOVER, so **K9-per-fold under K13 (`52a3b60`)** -- not universe size -- is binding. K13 = 5 OOS folds, edge positive in >=3 of 5 + aggregate-positive + K9 holds. A monthly rotation (~12 rebalances/y x top-N) may yield only ~15-40 position-changes/y -> per ~1.4y fold ~21-56, tight vs the K9 floor. **The s17 Tier-N PLAN MUST choose a rebalance cadence / held-N / trade-counting that demonstrably clears K9 in EACH of the 5 K13 folds, or the candidate is K13/K9-blocked.** Breadth (24 names) helps ranking, not turnover.

## 7. DR10-v2 reachability
Cash-equity cost_drag stays well under 5% even at higher cadence -> DR10 v2 CLEARS strong margin.

## 8. Contingency tree
- **all_24_pass_dr9 (12 reused PASS + 12 fresh PASS)** -> `Authorize s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit RESULT SEALING only.`
- **1-6_fresh_symbols_fail_dr9** -> `Authorize s17-d1 shrunk broad-universe DR9 RESULT SEALING only (drop failing names; basket must retain >= 16 names to preserve cross-sectional ranking breadth)`
- **7+_fresh_symbols_fail_dr9 (basket would drop below 16)** -> `Authorize s17-d1 broad-universe revision to an alternative large-cap shortlist (RUN_BOOK rev only)`
- **GOOGL_20to1_split_consistency_fails** -> `Operator manual review / re-fetch GOOGL; that symbol INCONCLUSIVE_HOLD until resolved; do NOT auto-progress`
- **any_INCONCLUSIVE_HOLD** -> `Operator manual review; no auto-progression`
- **vendor_fetch_fails** -> `Operator retries Tiingo later; RUN_BOOK remains reference; no repeated decline memos (brief in-chat reminder only)`

(16-name floor preserves cross-sectional ranking breadth; GOOGL split-consistency failure -> INCONCLUSIVE_HOLD + manual review.)

## 9. Boundaries held this RUN_BOOK turn
Framework/RUN_BOOK only - NOT a seal - no fetch/vendor API/API-key/network - no DR9 RUN / no DR9 RESULT sealed - no mechanic selection (deferred to PLAN) - no DRAFT/SEAL/BUILD/backtest/OOS - no live/broker/Strategy Lab/FRC - no revival of s16/s15/s14/s13/s12 - no retroactive K13 application - no modification of reused s16 data or any sealed artifact - **no `lessons.md`** - **no commit this turn**.

## 10. Next authorization
- Commit this RUN_BOOK: `Authorize commit s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit RUN_BOOK only.`
- Then operator-side fetch of the 12 fresh names -> `Authorize s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit RESULT SEALING only.`

trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.
