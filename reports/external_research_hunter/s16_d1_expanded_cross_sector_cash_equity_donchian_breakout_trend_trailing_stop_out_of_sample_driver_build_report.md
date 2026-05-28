# S16-D1 Donchian trend P3 BUILD out-of-sample driver report

**Lifecycle:** `P3_BUILD_OUT_OF_SAMPLE_DRIVER_REPORT_SEALED` - **Report seal:** `8e87f2e932c6316b1873461c80e778b70665c4a79efe447225dc02f74dd4f5eb` - **Authored:** `2026-05-28T22:23:34.471399Z`

## Anchors

- SEAL `985c569` (`359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8`)
- P1 `f95e5e3` (`957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86`)
- P2 `f826aea` (`3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5`)
- DR9 result `245ac0d` (`ec856253a28f7d538704b2610da8d1c3b13823335d741c356dd41259488b12e9`; reuse, no fetch)

## Exit/stop first-principles (trend)
main.py implements the TRAILING Donchian exit (N_exit=10) + 2xATR(14) initial stop (NOT tight); execution_guard enforces assert_trailing_donchian_exit + assert_initial_stop_2atr_not_tight. Mean-reversion exit/stop designs structurally excluded.

## C6 inherited_constraints_block (carried verbatim; 16 entries)

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
P3 BUILD only - py_compile syntax-checked (no import/execution) - tests AUTHORED NOT RUN (P4 separate auth) - DR9 reused (no fetch) - no backtest/OOS/live/Strategy Lab - no strategy optimization - no MR re-skin - no _revN_/revival - no sealed-artifact mod (incl. s16 DR9 result + 12 CSVs) - no lessons.md - no commit by script.

## Next
P4: `Authorize s16-d1 expanded-universe trend/breakout P4 synthetic smoke only`.
