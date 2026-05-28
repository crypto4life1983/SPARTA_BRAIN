# s15-d1-cross-sector cash-equity z-score exit-to-mean P1 plan-lock (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `P1_PLAN_LOCK` · **Lifecycle:** `S15_D1_CROSS_SECTOR_CASH_EQUITY_ZSCORE_EXIT_TO_MEAN_P1_PLAN_LOCK_SEALED`
**Authored (UTC):** `2026-05-28T20:08:20.035764Z`
**Report seal sha256:** `d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3`
**Authorization:** `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P1 plan-lock only — bound by DR10 v2.`

## §1. Seal inheritance (K8 drift check: PASS)

| Field | Value |
|---|---|
| Tier-N SEAL | commit `597a49b` · report_seal `1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d` (file sha `ef73aa6bb32c943cf0e9e15fbabcbc5e348fec89a108276d012a39e3d0fc57d6`) |
| DRAFT | `9f0ce14` |
| PLAN | `ae0f4fb` |
| K8 sealed-parent-drift | PASS (SEAL report_seal + file sha re-read; no drift) |
| DA1-DA20 | locked by-reference; **no parameter changes at P1** |
| C6 carried verbatim | 16 entries |

## §2. DA key-locks (by-reference to SEAL)

mechanic z-score exit-to-mean (DA2) · L=20 (DA6) · k=2.0σ entry (DA8) · **EXIT-TO-MEAN (DA9)** · **catastrophe stop 3.5σ, NOT 2N (DA10)** · time-stop 10 (DA11) · vol-normalized sizing (DA12) · DA3=B 0.5% · DA4=B $100k · split_only (DA15) · tiingo (DA16) · universe AAPL/JPM/XOM (DA17) · portfolio cap 3 (DA18) · warmup 30 (DA19) · bi-directional (DA20).

## §3. Lifecycle phase-ladder (LOCKED)

| Phase | Name | Status |
|---|---|---|
| P1 | plan-lock | THIS_TURN |
| P2 | phase-2 plan | FUTURE_SEPARATE_AUTH |
| P3 | BUILD | FUTURE_SEPARATE_AUTH |
| P4 | synthetic smoke | FUTURE_SEPARATE_AUTH |
| P6 | IS diagnostic | FUTURE_SEPARATE_AUTH |
| P6.5 | cost-stress matrix | FUTURE_SEPARATE_AUTH |
| P7 | decision memo | FUTURE_SEPARATE_AUTH |
| P10 | OOS gate | FUTURE_SEPARATE_AUTH_REC1_BINDING |

P3 BUILD reuses the DR9-passed cross-sector CSVs (`b13af03`); no fetch.

## §4. C6 inherited_constraints_block (carried verbatim from SEAL; 16 entries)

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

## §5. Boundaries held this P1 turn

P1 plan-lock only (no P2) · C6 carried verbatim · no DA/parameter change · DR10 v2 by-reference (not redefined) · no build/backtest/fetch/OOS/Strategy Lab · no strategy optimization · no `_revN_`/patch/revival · no modification of any sealed artifact (SEAL 597a49b, DRAFT 9f0ce14, all-tech 214bae0, DR9 result, CSVs, DR10 v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## §6. Next phase

- Commit: `Authorize commit s15-d1 cross-sector cash-equity z-score exit-to-mean P1 plan-lock only.`
- Forward: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P2 phase-2 plan only — bound by DR10 v2.`

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding.
