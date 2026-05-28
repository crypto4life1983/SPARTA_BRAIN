# s16-d1 expanded-universe Donchian trend P2 phase-2 plan (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history` - **Report seal:** `3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5` - **Authored:** `2026-05-28T22:17:13.684459Z`
Anchors SEAL `985c569` (`359aea43df85c153c8cb...`) + P1 `f95e5e3` (`957ca333d59a24e942a1...`); K8 PASS; C6 16 verbatim; no DA/parameter changes.

## C1-C8 phase-2 safety contracts (instantiated byte-equivalent)
| Contract | Instantiation |
|---|---|
| C1 | Algo.Initialize raises if LiveMode detected; paper-only forever |
| C2 | deterministic run_id over (tier_spec_seal + plan_lock_seal + plan_doc_sha + phase_tag + algo_version + engine dates); engine-truth date cross-check at Initialize |
| C3 | set-membership safety counters; all-zero rollup; extended_hours_fill NOT_APPLICABLE (daily bars) |
| C4 | US equity RTH session boundary; eod_cancel aligns to 16:00 ET; daily-bar trivial |
| C5 | CASH-EQUITY split_only: AMZN 20:1, WMT 3:1, NVDA 4:1/10:1, AAPL 4:1 applied+verified; JNJ Kenvue spin-off informational; dividends NOT adjusted; DR9 PASSED all 12 by REUSE (245ac0d); no fetch |
| C6 | 16-entry inherited_constraints_block carried verbatim from SEAL (REC1-equivalent + trend exit/stop-first-principles + DA3=B + DA4=B + Donchian params + split_only + 12-name universe + DR9-by-reuse + ...) |
| C7 | verdict restricted to closed enum (READY_FOR_LONGER_BACKTEST / INSUFFICIENT_SAMPLE / FAIL_SAFETY / REJECT_FAST / INCONCLUSIVE_HOLD); forbidden-token blocklist |
| C8 | permanent attributes (DIAGNOSTIC_ONLY_NOT_LIVE_GRADE; PAUSED; BLOCKED_AT_6_GATES; FRC NEVER_GRANTED; no_strategy_optimization; no_dr_redefinition_post_seal) |

## P3 BUILD scope (no auto build/run)
- runner harness (main.py): CONFIG byte-equivalent to SEAL DA register; Donchian primitives (rolling_high(N), rolling_low(N), donchian_long_entry close>prior-N_entry-high, donchian_short_entry close<prior-N_entry-low; trailing exit donchian_long_exit close<prior-N_exit-low / donchian_short_exit close>prior-N_exit-high; wilder_atr(14); compute_initial_stop entry-/+2*ATR; compute_position_shares_vol_normalized floor(0.005*equity/(2*ATR)); portfolio_can_open max_total=6); per-name independent; QC-compat shim
- in_sample_driver.py: 12-CSV registry (reuse 245ac0d); IS window 2019-01-02..2023-12-29; run_in_sample() STUB raising P6_IS_NOT_AUTHORIZED
- out_of_sample_driver.py: OOS window 2024-01-02..2025-12-30; run_out_of_sample() STUB raising P10_OOS_NOT_AUTHORIZED; OOS isolation (no IS constants/year tokens/run_in_sample/top-level vendor imports)
- execution_guard.py: C1-C8 attestation; K8 drift check vs SEAL constants; assert_locked_strategy_params (Donchian DA register); assert_trailing_donchian_exit (DA9); assert_initial_stop_2atr_not_tight (DA10); assert_split_only_convention; assert_universe_locked (12 names); assert_no_leverage_cap
- tests/: synthetic smoke battery (no real-data run at BUILD); incl. donchian breakout/trailing-exit/initial-stop/vol-sizing + exit/stop guard tests
- 3 sealed build reports (runner / IS-driver / OOS-driver)

BUILD reuses the 12 DR9-PASSED sealed CSVs (`245ac0d`; no fetch). **Must implement the TRAILING Donchian exit (N_exit=10) + 2xATR(14) initial stop exactly as locked (DA9/DA10); no tight MR stop, no oscillator exit.** P3 BUILD requires separate authorization.

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
P2 only - no P3/build/backtest/fetch/OOS/Strategy Lab - no strategy optimization - no DA/C-contract change - C6 verbatim - DR10 v2 by-ref - no MR re-skin - no _revN_/revival - no sealed-artifact mod - no lessons.md - no commit by script.

## Next
Commit: `Authorize commit s16-d1 expanded-universe trend/breakout P2 phase-2 plan only.` - Forward: `Authorize s16-d1 expanded-universe trend/breakout P3 BUILD only -- bound by DR10 v2.`
