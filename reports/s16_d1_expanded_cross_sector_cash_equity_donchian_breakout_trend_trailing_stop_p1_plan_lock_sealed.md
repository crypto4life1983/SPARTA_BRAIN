# s16-d1 expanded-universe Donchian trend P1 plan-lock (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history` - **Report seal:** `957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86` - **Authored:** `2026-05-28T22:15:55.051922Z`
**Anchors SEAL** `985c569` (report_seal `359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8`, file sha `68cbfb34078811e977a1c91aea30158c604c3c01f01f64fee0b66c001c845e53`) byte-equivalent; **K8 drift check PASS**; C6 16 carried verbatim; DA1-DA20 locked by-reference (no parameter changes at P1); lifecycle phase-ladder locked (P1->P2->P3 BUILD->P4->P6 IS->P6.5->P7->P10; P3 reuses the 12 DR9-passed CSVs 245ac0d).

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
P1 only (no P2) - C6 verbatim - no DA/param change - DR10 v2 by-ref - no build/backtest/fetch/OOS/Strategy Lab - no strategy optimization - no MR re-skin - no _revN_/revival - no sealed-artifact mod - no lessons.md - no commit by script.

## Next
Commit: `Authorize commit s16-d1 expanded-universe trend/breakout P1 plan-lock only.` - Forward: `Authorize s16-d1 expanded-universe trend/breakout P2 phase-2 plan only -- bound by DR10 v2.`
