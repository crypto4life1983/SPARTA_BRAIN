# s15-d1-cross-sector cash-equity z-score exit-to-mean P2 phase-2 plan (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `P2_PHASE2_PLAN` · **Lifecycle:** `S15_D1_CROSS_SECTOR_CASH_EQUITY_ZSCORE_EXIT_TO_MEAN_P2_PHASE2_PLAN_SEALED`
**Authored (UTC):** `2026-05-28T20:11:30.137314Z`
**Report seal sha256:** `6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40`
**Authorization:** `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P2 phase-2 plan only — bound by DR10 v2.`

## §1. Seal inheritance (K8 drift check: PASS)

| Field | Value |
|---|---|
| Tier-N SEAL | commit `597a49b` · report_seal `1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d` |
| P1 plan-lock | commit `c8d6dd5` · report_seal `d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3` (file sha `6629f0825f1488d99b049f96e8a29ac8f47c2230691632a9545d0a4d02c2fc62`) |
| C1-C8 byte-equivalent | True |
| C6 carried verbatim | True (16 entries) |
| DA / parameter changes at P2 | NONE |

## §2. C1-C8 phase-2 safety contracts (instantiated byte-equivalent; cash-equity adaptations)

| Contract | Name | Instantiation |
|---|---|---|
| C1 | C1_live_mode_refusal | Algo.Initialize raises if LiveMode detected; candidate is paper-only forever; refuse live path |
| C2 | C2_engine_truth_run_id | deterministic run_id over (tier_spec_seal + plan_lock_seal + plan_doc_sha + phase_literal_tag + algo_version + engine_start/end dates); engine-truth date cross-check at Initialize |
| C3 | C3_safety_counters | set-membership safety counter pattern (stale_fill, unsupported_order_type, warmup_order_submit, etc.); all-zero rollup; extended_hours_fill NOT_APPLICABLE (daily bars) |
| C4 | C4_boundary_alignment | US equity RTH session boundary; eod_cancel aligns to session close (NYSE/NASDAQ 16:00 ET); daily-bar so intraday boundary trivial |
| C5 | C5_corporate_action_handling | CASH-EQUITY ADAPTATION: splits documented + applied per split_only convention (NOT structurally absent like futures). Known splits: AAPL 2020-08-31 4:1 (applied+verified); JPM none; XOM none. Dividends NOT adjusted (split_only). DR9 documented_split_event_consistency PASSED all 3 by REUSE of sealed CSVs (b13af03); no fetch. |
| C6 | C6_inherited_constraints | 16-entry inherited_constraints_block carried verbatim from SEAL (REC1-equivalent + EXIT/STOP-FIRST-PRINCIPLES binding axis + DA3=B + DA4=B + z-score params + split_only + cross-sector universe held constant + DR9 PASS by reuse + ...) |
| C7 | C7_verdict_closed_enum | verdict restricted to closed enum (READY_FOR_LONGER_BACKTEST / INSUFFICIENT_SAMPLE / FAIL_SAFETY / REJECT_FAST / INCONCLUSIVE_HOLD / ...); forbidden-token blocklist; no profitability/live-ready/money-proven tokens |
| C8 | C8_lifecycle_states | permanent lifecycle attributes carried (DIAGNOSTIC_ONLY_NOT_LIVE_GRADE; trading PAUSED; live BLOCKED_AT_6_GATES; FRC NEVER_GRANTED; no_strategy_optimization_authorized; no_dr_redefinition_post_seal) |

## §3. C6 inherited_constraints_block (carried verbatim; 16 entries)

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

## §4. P3 BUILD scope defined (no automatic build/run)

**BUILD creates:**
- runner harness (main.py): CONFIG byte-equivalent to SEAL DA register; Algo class; z-score/Bollinger primitives (rolling SMA_L + std_L + z-score; entry z<=-2.0 long / z>=+2.0 short; EXIT-TO-MEAN close on re-cross of SMA_L midline; vol-scaled catastrophe stop entry-/+3.5*sigma_L; time-stop max-hold 10 bars; vol-normalized sizing shares=floor(0.005*equity/(3.5*sigma_L))); per-name independent signal generation; portfolio max 3 positions; QC-compat shim
- in_sample_driver.py: filters sealed cross-sector CSVs to IS window 2019-01-02->2023-12-29; run_in_sample() STUB raising P6_IS_NOT_AUTHORIZED until separate P6 authorization
- out_of_sample_driver.py: filters to OOS window 2024-01-02->2025-12-30; run_out_of_sample() STUB raising P10_OOS_NOT_AUTHORIZED; REC1-equivalent binding reminder; OOS isolation (no IS constants/year tokens/run_in_sample/top-level vendor imports)
- execution_guard.py: C1-C8 attestation utilities; K8 sealed-parent-drift check against SEAL constants; assert_locked_strategy_params (z-score params); assert_exit_to_mean_rule; assert_catastrophe_stop_vol_scaled_not_2N; assert_split_only_convention; assert_universe_locked; assert_no_leverage_cap
- tests/: synthetic smoke battery (no real-data run at BUILD); incl. exit-to-mean + catastrophe-stop-not-2N + vol-normalized-sizing primitive tests
- 3 sealed build reports (runner / IS-driver / OOS-driver)

**BUILD does NOT:**
- execute any backtest / simulator / signal computation
- fetch data (reuses sealed cross-sector CSVs DR9-passed)
- read OOS rows in signal logic
- place any order / connect broker / live
- promote to Strategy Lab

BUILD reuses the DR9-PASSED sealed cross-sector CSVs (`b13af03`; no fetch). **The BUILD must implement EXIT-TO-MEAN and the 3.5σ vol-scaled catastrophe stop exactly as locked (DA9/DA10) — no fixed-2N stop, no oscillator-threshold exit (the s14-d1-cross-sector failed design).** P3 BUILD requires separate authorization.

## §5. Boundaries held this P2 turn

P2 phase-2 plan only · no P3 BUILD · no build/backtest/fetch/OOS/Strategy Lab · no strategy optimization · no DA resolution changed · no C-contract weakened · C6 carried verbatim · DR10 v2 by-reference (not redefined) · no `_revN_`/patch/revival · no modification of any sealed artifact (SEAL 597a49b, P1 c8d6dd5, DRAFT 9f0ce14, all-tech 214bae0, DR9 result, CSVs, DR10 v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## §6. Next phase

- Commit: `Authorize commit s15-d1 cross-sector cash-equity z-score exit-to-mean P2 phase-2 plan only.`
- Forward: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P3 BUILD only — bound by DR10 v2.`

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding.
