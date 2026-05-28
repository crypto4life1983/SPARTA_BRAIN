# S15-D1-CROSS-SECTOR cash-equity z-score exit-to-mean P3 BUILD in-sample driver report

**Lifecycle state:** `P3_BUILD_IN_SAMPLE_DRIVER_REPORT_SEALED`
**Report seal sha256:** `28741317a9663bdbe9a2b9baeabf98f7954df67af13c5b486162ab27574e83a2`
**Authored (UTC):** `2026-05-28T20:19:44.993248Z`
**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`

## Anchors

- Tier-N SEAL `597a49b` · report_seal `1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d`
- P1 plan-lock `c8d6dd5` · report_seal `d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3`
- P2 phase-2 plan `5b36ac8` · report_seal `6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40`
- Cross-sector DR9 result `b13af03` (reused; no fetch) · report_seal `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c`
- s14-d1-cross-sector P7 terminal `6485ea9` · framework DR10 v2 `78cd22e`

## Exit/stop first-principles (the binding axis)

main.py implements EXIT-TO-MEAN + 3.5σ vol-scaled catastrophe stop (NOT a fixed 2N) + vol-normalized sizing; execution_guard enforces `assert_exit_to_mean_rule` + `assert_catastrophe_stop_vol_scaled_not_2N`. The s14-d1-cross-sector failed design (RSI-mid exit + fixed 2N) is structurally excluded.

## C6 inherited_constraints_block (carried verbatim; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable on the cross-sector basket (expected ~60-105/y basket-summed). If observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS.
2. EXIT/STOP-FIRST-PRINCIPLES (BINDING; central thesis): exit = EXIT-TO-MEAN (close on re-cross of SMA_L; the reversion target itself); stop = vol-scaled catastrophe brake (3.5*sigma_L; NOT a fixed 2N). This is the candidate's entire reason to exist after s14-d1-cross-sector FAIL_SAFETY (LESSON_S14_D1_002/003); a hypothesis to TEST at P6 IS, never assumed.
3. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); proven-safe sizing
4. DA4=B (BINDING): START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin for cash equity
5. exit/stop-first-principles + K9-reachability + DR10-v2-reachability disciplines applied at PLAN+DRAFT+SEAL; binding for all subsequent phases
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family z-score/Bollinger mean-reversion exit-to-mean (NON-RSI) LOCKED at PLAN
8. z-score params LOCKED at SEAL: lookback L=20, entry band k=2.0, exit-to-mean, catastrophe stop 3.5*sigma, time-stop 10, vol-normalized sizing; modification post-SEAL FORBIDDEN
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50 turnover / 0.05 cost_drag immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention LOCKED (DA15); reuse same DR9-passed CSVs; switching/mixing post-SEAL FORBIDDEN
11. Cross-sector universe {AAPL (Tech), JPM (Financials), XOM (Energy)} LOCKED at PLAN; held constant from s14-d1-cross-sector to isolate the exit/stop variable; widening/substitution post-SEAL FORBIDDEN
12. DR9 data-availability gate PASSED all 3 symbols by REUSE (sealed b13af03; result_seal a8ff9126...); data provenance locked; NO fresh fetch; cash_equity_data_reuse_byte_equivalent
13. A7 effective_independent_bets + K10 avg_pairwise_correlation + K6 dispersion LOAD-BEARING but NOT the candidate's risk axis (already measured in-band for this universe at s14-d1-cross-sector); the risk axis is per-trade edge (K1/K2) under the new exit/stop design
14. s14-d1-cross-sector lifecycle terminal (FAIL_SAFETY; P7 6485ea9) preserved verbatim; this candidate is FRESH, NOT a _revN_/patch; clears T-FORBID-13/14/15
15. no_strategy_optimization_authorized: all parameters first-principles justified at SEAL, NOT grid-searched
16. P6 IS PASS (if reached) does NOT imply READY at OOS; P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## Boundaries

P3 BUILD only · py_compile syntax-checked (no import/execution/signal computation) · tests AUTHORED NOT RUN (P4 separate authorization) · DR9 reused (no fetch) · no backtest/OOS-inspection/live/Strategy Lab · no strategy optimization · no `_revN_`/patch/revival · no modification of any sealed artifact (SEAL/P1/P2/DRAFT/DR9-result/CSVs/all-tech-214bae0/s14-cross-sector/s13/s12/DR10-v2-78cd22e) · **no `lessons.md`** · **no commit this turn**.

## Next phase

P4: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P4 synthetic smoke only` (separate authorization).
