# s16-d1 expanded-universe Donchian trend P7 decision memo (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`
**Phase:** `P7_DECISION_MEMO` - **Memo run_id:** `PHASE2-S16-D1-P7-d1e157b42d5d` - **Report seal:** `48ef86e2cc205b70d4f6f8b5f6d90347aaa7abc55e2cce36bcbe13b188c584bf` - **Authored:** `2026-05-28T22:43:00.518621Z`
**Lifecycle:** `P7_DECISION_MEMO_SEALED_READY_FOR_LONGER_BACKTEST_ELIGIBLE_FOR_OOS` - **candidate_lifecycle_terminal: FALSE**

## Verdict formalized: `READY_FOR_LONGER_BACKTEST` -> ELIGIBLE for P10 OOS (NON-terminal)

**The first candidate in the s14/s15/s16 line to reach a positive, cost-stress-surviving IS edge.** This is a PROCEED memo, NOT a park. The candidate is eligible for OOS validation under separate authorization. **NOT money-proven, NOT live-ready, NOT OOS-confirmed.**

## P6 IS economics (RECORD-ONLY; diagnostic; favorable)
net **+$17,129.69** on $100,000 (CAGR 3.2204%); expectancy **+$53.03/trade**; sharpe_proxy/trade **+0.0563**; maxdd 14.05%; 323 trades (~64.75/y).

## Trend thesis validated at IS
Observed **win 34.67% / P/L 2.2191** (avg win $1012.57 / avg loss $-456.3) -- the textbook trend profile (win<50%, P/L>1), the MIRROR of the s14/s15 mean-reversion failure. Trailing-exit dominated (181) vs initial-stop (136). The family-level fix worked.

## P6.5 cost-stress (edge survives full stress)
| Tier | net PnL | expectancy/trade | sharpe_proxy | maxdd |
|---|---|---|---|---|
| S0 | $18,702.55 | $57.9 | 0.0611 | 13.96% |
| S1 | $17,129.66 | $53.03 | 0.0563 | 14.05% |
| S2 | $16,465.25 | $50.98 | 0.0542 | 14.07% |
| S3 | $15,673.82 | $48.53 | 0.0518 | 14.12% |
| S4 | $15,205.07 | $47.07 | 0.0506 | 14.16% |

`PASS_COST_STRESS_ELIGIBLE`: DR3 no-fire, DR5 no-fire, DR10 v2 CLEARS (S2 cost_drag 2.519%<5%), K1/K2/K4 hold across S0-S4.

## What remains UNPROVEN (explicit)
- OOS NOT established (never inspected; P10 separate). READY does NOT imply OOS-confirmed/money-proven/live-ready.
- REC1-equivalent BINDING at OOS; chain shall NOT relax K9; DR4 (oos-negative-while-is-positive) is the canonical OOS risk, evaluated only at P10. Trend edges are regime-dependent; a 2019-2023 uptrend does not guarantee 2024-2025 trends.
- 6-gate live-block applies regardless; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.

## Cross-sector diagnostics
A7 = `3.9225` (12-name; vs 3-name 2.09), K10 = `0.4036`, K6 concentration flag `False`.

## Operator decision paths post-P7
- **A_PROCEED_TO_OOS** -- Authorize the P10 OOS gate (REC1-equivalent binding) (default) [separate authorization]
  `Authorize s16-d1 expanded-universe trend/breakout P10 OOS gate only -- bound by DR10 v2 and REC1-equivalent OOS-K9 disclosure.`
- **B_LESSONS_MD_UPDATE** -- Write the eligible LESSON_S16_D1_* entries to lessons.md [separate authorization]
  `Authorize s16-d1 P7 lessons.md update only.`
- **C_DEFER** -- Defer / pause at READY

## C6 inherited_constraints_block (carried verbatim from SEAL; 16 entries)
1. REC1-equivalent (BINDING): OOS K9 reachable on the 12-name basket (expected ~96-180/y). If observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS.
2. EXIT/STOP-FIRST-PRINCIPLES (BINDING; trend variant): exit = TRAILING DONCHIAN channel (N_exit=10; let winners run/cut losers) + 2xATR(14) initial catastrophe stop. Opposite geometry to the failed mean-reversion family; expected trend profile win<50% / P/L>1. Hypothesis tested at P6 IS, never assumed.
3. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%)
4. DA4=B: START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin for cash equity
5. exit/stop-first-principles + K9-reachability + DR10-v2-reachability disciplines applied at PLAN+DRAFT; binding for all subsequent phases
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family Donchian breakout trend (trailing-stop), NON-mean-reversion, LOCKED at PLAN
8. Donchian params N_entry=20 / N_exit=10 / ATR(14) 2N initial stop first-principles; to be JUSTIFIED (not tuned) and LOCKED at SEAL
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50/0.05 immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention CONFIRMED (DA15); reuse DR9-passed CSVs; switching post-SEAL FORBIDDEN
11. 12-name expanded cross-sector universe LOCKED at PLAN; widening/substitution post-SEAL FORBIDDEN
12. DR9 data-availability gate PASSED all 12 by REUSE (sealed 245ac0d; result_seal ec856253...); NO fresh fetch; cash_equity_data_reuse_byte_equivalent
13. A7 effective_independent_bets + K10 avg_pairwise_correlation + K6 dispersion LOAD-BEARING (12 names ~7 sectors; expected higher A7 / lower K10 than 3-name basket); NOT the candidate's risk axis (per-trade trend edge K1/K2 is)
14. s15-d1 + s14-d1-cross-sector terminal (FAIL_SAFETY) preserved verbatim; this candidate is FRESH NON-mean-reversion; clears T-FORBID-16/17/18
15. no_strategy_optimization_authorized: parameters first-principles justified at SEAL, NOT grid-searched
16. P6 IS PASS (if reached) does NOT imply READY at OOS; P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## Parent references
SEAL `985c569` - P1 `f95e5e3` - P2 `f826aea` - P3 BUILD `2cddb93` - P4 `58904e8` - P6 IS `8976a47` (`5b2c043e3f16f7edfa14...`) - P6.5 `b3a3bc5` (`d8fa65e3341e02ae32b3...`) - DR9 result `245ac0d` - DR10 v2 `78cd22e`.

## Status
trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE - **candidate NON-terminal, ELIGIBLE for OOS** - REC1-equivalent binding - lessons.md NOT touched this phase.
