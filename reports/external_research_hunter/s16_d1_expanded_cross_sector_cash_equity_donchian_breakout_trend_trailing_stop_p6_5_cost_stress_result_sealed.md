# s16-d1 expanded-universe Donchian trend P6.5 cost-stress result (SEALED)

**Phase:** `P6_5_COST_STRESS` - **Report seal:** `d8fa65e3341e02ae32b3f08c348f829185892c642f64dfd0936771cd9ebc8ddc` - **Authored:** `2026-05-28T22:34:42.808392Z`
**Anchors:** SEAL `985c569` - P6 IS `8976a47` (`5b2c043e`)

## Verdict: `PASS_COST_STRESS_ELIGIBLE`
- No DR2/DR3/DR4/DR5 fire at IS; DR10 v2 CLEARS (cost_drag<5%); K1/K2/K4 hold across S0-S4; edge survives full cost-stress

## Cost-stress matrix (IS; S0-S4)
| Tier | cost/slip scalar | net PnL | expectancy/trade | sharpe_proxy | maxdd | cost_drag |
|---|---|---|---|---|---|---|
| S0 | 0.0/0.0 | $18,702.55 | $57.9 | 0.0611 | 13.96% | 0.000% |
| S1 | 1.0/1.0 | $17,129.66 | $53.03 | 0.0563 | 14.05% | 1.682% |
| S2 | 1.5/1.5 | $16,465.25 | $50.98 | 0.0542 | 14.07% | 2.519% |
| S3 | 2.0/2.0 | $15,673.82 | $48.53 | 0.0518 | 14.12% | 3.350% |
| S4 | 3.0/3.0 | $15,205.07 | $47.07 | 0.0506 | 14.16% | 5.025% |

## DR / K evaluation
- DR3 (zero-cost-only survival): fires=False
- DR5 (cost-stress tier flip): fires=False
- DR10 v2: turnover_branch=True, S2 cost_drag=2.519% (>5%? False), AND-fire=False
- DR2/DR4: OOS-only (deferred to P10)
- K1 (sharpe_proxy<0 any tier)=False; K2 (expectancy<=0 S1-S4)=False; K4 (maxdd>50% any)=False; K12=False

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

## Status
trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE - OOS never read - no param optimization - no DR redefinition.
