# s15-d1-cross-sector z-score exit-to-mean P6 IS diagnostic result (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `P6_IS_DIAGNOSTIC` · **Backtest run_id:** `PHASE2-S15-D1-ZSCORE-EXIT-TO-MEAN-IS-1139edf424ba`
**Authored (UTC):** `2026-05-28T21:35:38.257940Z` · **Report seal sha256:** `61b15aac25516b1c5da474c390a715cf5de13c61efd848889f9bf57d2c2d8d89`

## Verdict: `FAIL_SAFETY`

- K1 sharpe_proxy_per_trade=-0.0938 < 0 at S1

## Exit/stop edge analysis (THE binding axis — the s14-d1 fix under test)

| | |
|---|---|
| exit-to-mean exits | 63 |
| catastrophe-stop exits (3.5σ) | 29 |
| time-stop exits | 88 |
| avg win | $242.31 |
| avg loss | $-276.24 |
| profit/loss ratio | 0.8772 |
| win rate | 47.78 |
| sharpe_proxy/trade (K1) | -0.0938 |
| expectancy/trade (K2) | $-28.49 |

vs s14-d1-cross-sector (RSI-mid exit + fixed 2N): win 54.31%, expectancy −$39.53, P/L<1, FAIL_SAFETY.

## Performance summary

| Metric | Value |
|---|---|
| net PnL | $-5,128.32 on $100,000 (final $94,871.66) |
| total costs | $599.54 |
| max drawdown | 7.1736% |
| CAGR | -1.0498% |
| sharpe (ann) | -0.4967 |
| closed trades | 180 (~36.08/y) — AAPL 61 / JPM 56 / XOM 63 |
| annual turnover | 4.7810 |

## Cross-sector diagnostics

A7 = `2.0909` (expected 2.3-2.8) · K10 = `0.4529` (expected 0.30-0.50; pairwise AAPL_JPM=0.4548, AAPL_XOM=0.3162, JPM_XOM=0.5877) · K6 max trade share `35.00%`, max |PnL| share `65.06%`, flag `False`.

| Symbol | Closed | Long/Short | Wins | Net PnL |
|---|---|---|---|---|
| AAPL | 61 | 19/42 | 25 | $-4,148.51 |
| JPM | 56 | 27/29 | 26 | $-1,604.07 |
| XOM | 63 | 27/36 | 35 | $624.26 |

## C6 inherited_constraints_block (carried verbatim from SEAL; 16 entries)

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

## Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding · OOS never read · P6.5/P10 each separate authorization.
