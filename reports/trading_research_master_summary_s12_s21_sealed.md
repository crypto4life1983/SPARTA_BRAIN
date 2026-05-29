# Trading research MASTER SUMMARY (s12->s21) — sealed

**report_seal:** `175d4cd3cffe2b1b9cf6d93df8008013c53a32a2d9253c09ba76f56aabcdbba4` · **Authored:** 2026-05-29T05:46:24.159282Z
Read-only synthesis of sealed lifecycle artifacts; modifies none. ALL figures are PAPER backtests ($100k CSV simulator, split_only daily, proxy costs) -- NOT real money, NOT live.

## Candidate ladder — final states
| Cand | Mechanic | Final | Why |
|---|---|---|---|
| s12 | MNQ Donchian 15/8 breakout (futures) | PARKED | weak/insufficient sample (~21 implied OOS << K9 100) |
| s13 | MNQ RSI(2) bi-directional (futures MR) | TERMINAL | DR10 REJECT_FAST @P6.5 (turnover x cost) |
| s14 | cross-sector cash-equity | TERMINAL | FAIL_SAFETY @P6 IS (negative edge) |
| s15 | cross-sector z-score exit-to-mean (MR) | TERMINAL | FAIL_SAFETY @P6 IS (negative edge) |
| s16 | expanded Donchian trend | TERMINAL | DR4 @P10 (IS +$17k but OOS NEGATIVE) |
| s17 | broad xmom MONTHLY | TERMINAL | K9 @P6 IS (85<100); motivated weekly pivot |
| **s18** | weekly RS 126-21/top-8 (broad 24) | **OOS_CONFIRMED** (caveat) | first full-ladder pass; recent-fold F5 negative |
| s19 | weekly RS (independent 24) | TERMINAL | K9 @P10 (87/43.6y) -- edge generalized, candidate sample-short |
| **s20** | weekly RS (combined 48) | **OOS_CONFIRMED** | breadth solved K9 w/o tuning; selection caveat |
| **s21** | weekly RS (FRESH 48, 0/48 seen) | **OOS_CONFIRMED CLEAN** | resolves selection caveat; edge generalizes |

## Paper-backtest OOS P&L (diagnostic only; $100k notional)
s18 +$39,786 (+$210/tr) · s19 +$44,050 (+$336/tr, terminal) · s20 +$60,004 (+$353/tr) · **s21 +$48,475 (+$171/tr, CLEAN)**. Earlier candidates (s12-s17): NO certifiable edge.

## Best candidates
**s21** strongest (clean generalization) · **s20** sample-size breakthrough · **s18** first OOS_CONFIRMED · **s19** informative failure (edge generalizes != candidate certifiable).

## Failure taxonomy (s12-s17)
K9 sample (s12, s17) · negative edge / FAIL_SAFETY (s14, s15) · cost / DR10 (s13) · OOS / DR4 (s16). The gates rejected every early candidate on distinct grounds -- no false promotions.

## Why weekly RS is parked DIAGNOSTIC_ONLY (not live-ready)
Permanent 6-gate live-block + FRC NEVER_GRANTED (no promotion phrase exists by design); PAPER not money-proven (CSV sim, proxy costs); MODEST edge (+$171/trade clean); research-scope only. Parked -- central question (does it generalize?) answered YES (real, portable, modest, diagnostic).

## Conclusion
The weekly RS line is the **strongest completed diagnostic edge** and the only line to reach OOS_CONFIRMED -- now clean-generalization-confirmed (s21). REAL, PORTABLE, MODEST, and **permanently DIAGNOSTIC_ONLY**. PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED. No sealed artifact modified; lessons.md untouched.
