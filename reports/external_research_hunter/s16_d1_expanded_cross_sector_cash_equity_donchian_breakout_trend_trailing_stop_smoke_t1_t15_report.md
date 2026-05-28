# s16-d1 expanded-universe Donchian trend P4 synthetic smoke report (SEALED)

**Verdict:** `P4_SMOKE_ALL_PASS` -- **32/32** (smoke 21/21, OOS 11/11) in ~0.11s
**Report seal:** `f565f074d4f20f6ece28b8dfa13b0b62f9e574a18184186580146dfa15329e21` - **Authored:** `2026-05-28T22:29:00.487354Z`
**Anchors:** SEAL `985c569` - P1 `f95e5e3` - P2 `f826aea` - P3 BUILD `2cddb93`

## Exit/stop first-principles -- STRUCTURAL validation (NOT an edge claim)
T18 confirms assert_trailing_donchian_exit + assert_initial_stop_2atr_not_tight PASS and that reverting to an oscillator/exit-to-mean exit or a tight MR stop RAISES. T4/T5/T7/T10 confirm breakout entries, trailing exits, 2xATR stop, vol-normalized sizing. **Whether the basket trends (positive expectancy) is the P6 IS test.**

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

## Boundaries
synthetic-fixture-only - no sealed CSV touched - no real-data signal computation - no IS/OOS execution/inspection - no backtest/fetch - no live/Strategy Lab - no strategy optimization - no MR re-skin - no _revN_/revival - no sealed-artifact mod - no lessons.md - no commit by script.

## Next
`Authorize s16-d1 expanded-universe trend/breakout P6 IS diagnostic only`.
