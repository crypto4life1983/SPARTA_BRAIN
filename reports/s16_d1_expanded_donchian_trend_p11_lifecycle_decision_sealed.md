# s16-d1 expanded-universe Donchian trend P11 lifecycle decision memo (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`
**Phase:** `P11_LIFECYCLE_DECISION` - **Memo run_id:** `PHASE2-S16-D1-P11-2fd047cb6d29` - **Report seal:** `2b16844e5809eddd42e2ef473ed75a4b06c2bf876dddc186bd946c91bbf1c6f2` - **Authored:** `2026-05-28T22:48:24.048954Z`
**Lifecycle:** `P11_LIFECYCLE_DECISION_SEALED_CANDIDATE_TERMINAL` - **candidate_lifecycle_terminal: TRUE**

## Verdict formalized: `REJECT_FAST` -- candidate lifecycle TERMINAL

Driven by **DR4** (oos_negative_while_is_positive) at the P10 OOS gate: OOS net **$-2,837.19** while IS was **+$17,129.69**. K9 OOS SATISFIED (133 trades ~66.73/y) -> a genuine generalization failure, NOT a sample problem.

## The full arc (IS -> cost-stress -> OOS)
| Phase | Verdict | net PnL | sharpe_proxy/trade | expectancy/trade | win% / P-L |
|---|---|---|---|---|---|
| P6 IS | READY_FOR_LONGER_BACKTEST | +$17,129.69 | +0.0563 | +$53.03 | 34.67% / 2.2191 |
| P6.5 cost-stress | PASS (S0-S4 all positive) | edge survived | -- | -- | -- |
| P10 OOS | **REJECT_FAST (DR4)** | $-2,837.19 | -0.0311 | $-21.33 | 33.83% / 1.8019 |

## Central finding
A positive IS edge that survives full cost-stress is **necessary but NOT sufficient** -- the OOS gate (DR4) is the binding generalization test, and it caught a strategy that looked strong in-sample but did not generalize. The trend geometry (win<50%/P-L>1) was retained OOS, but the edge flipped negative: the 2019-2023 large-cap uptrend edge was **regime-specific** (OOS: defensive KO +$3,897 / WMT +$2,938 trended; tech/energy AMZN/CVX/JNJ/META/JPM reversed). **s16 advanced furthest of the s14/s15/s16 line and the OOS gate terminated it honestly with no gate relaxation.**

## What this does NOT demonstrate
Not that trend-following is universally non-viable (THIS spec/basket/window failed to generalize); not a K9/sample problem (ample OOS sample); not that the IS/cost-stress analysis was wrong (the edge simply did not persist); not a data problem (12-name DR9-passed data intact).

## Remains DIAGNOSTIC-ONLY
NOT live-ready, NOT paper-ready, NOT Strategy-Lab-ready, NOT FRC-granted. Trading PAUSED; Live BLOCKED_AT_6_GATES; FRC NEVER_GRANTED. No promotion.

## Operator decision paths post-P11
- **A_PARK** -- Park s16-d1 permanently (REJECT_FAST at OOS terminal) (default)
- **B_NEW_CANDIDATE** -- Start a fresh candidate informed by the OOS-generalization finding [separate auth]
  `Authorize next research-track selection plan after s16-d1 OOS REJECT_FAST only.`
- **C_LESSONS_MD_UPDATE** -- Write the eligible LESSON_S16_D1_* entries to lessons.md [separate auth]
  `Authorize s16-d1 P11 lessons.md update only.`
- **D_DEFER** -- Defer / pause

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
SEAL `985c569` - P6 IS `8976a47` - P6.5 `b3a3bc5` - P7 `ecd777f` - P10 OOS `3d466f5` (`7cbcbb20b40efa2af5d7...`) - DR9 result `245ac0d` - DR10 v2 `78cd22e`.

## Status
trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE - **candidate lifecycle TERMINAL** - REC1-equivalent binding - lessons.md NOT touched this phase.
