# s18-d1 weekly RS rotation — P6.7 K13 walk-forward validation (sealed)

**Authored (UTC):** `2026-05-29T02:19:15.696610Z` · **report_seal:** `309d7f3244a74ebe78da7f2073551965e3c2ce34136ed4776e589cdc9fcded06`
**Verdict: `K13_PASS`** (3/5 folds positive; aggregate net>0=True; k9_ok=True)

5 fixed pre-committed UNSEARCHED DA22 folds; SAME locked params each fold (no per-fold refit, no search, no cadence tuning). Cost S1. Folds span the full 2019-2025 history by the sealed DA22 design (F4/F5 in 2024-2025 calendar) -- this is the P6.7 phase, distinct from the P10 final gate (NOT run).

| fold | window | closed | net P&L | exp/trade | sharpe/trade | sign |
|---|---|---|---|---|---|---|
| F1 | 2019-08-21..2020-11-23 | 68 | $42,939.27 | 195.30 | 0.1836 | POS |
| F2 | 2020-11-24..2022-03-02 | 67 | $19,230.06 | 234.58 | 0.2234 | POS |
| F3 | 2022-03-03..2023-06-08 | 71 | $12,462.72 | -2.70 | -0.0025 | neg |
| F4 | 2023-06-09..2024-09-16 | 68 | $41,151.94 | 447.93 | 0.2720 | POS |
| F5 | 2024-09-17..2025-12-30 | 69 | $9,528.78 | -33.89 | -0.0319 | neg |

aggregate net $125,312.77 · aggregate closed 343 · K13 = >=3/5 positive + aggregate>0 + K9.

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.
