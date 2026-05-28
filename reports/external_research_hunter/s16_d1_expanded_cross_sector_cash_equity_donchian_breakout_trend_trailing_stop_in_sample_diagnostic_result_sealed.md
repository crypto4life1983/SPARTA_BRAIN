# s16-d1 expanded-universe Donchian trend P6 IS diagnostic result (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`
**Phase:** `P6_IS_DIAGNOSTIC` - **run_id:** `PHASE2-S16-D1-DONCHIAN-TREND-IS-92254d513fda` - **Report seal:** `5b2c043e3f16f7edfa14c9e2aeefead002f945f4b2c29c721f3ac5d48b5ec55d` - **Authored:** `2026-05-28T22:31:44.251637Z`

## Verdict: `READY_FOR_LONGER_BACKTEST`
- All IS gates PASS: closed_trades=323>=100, sharpe_proxy=0.0563>0, expectancy=$53.03>0, |maxdd|=14.05%<=50%

## Trend edge analysis (binding axis)
| | |
|---|---|
| initial-stop exits | 136 |
| trailing-exit exits | 181 |
| window-end | 6 |
| avg win | $1,012.57 |
| avg loss | $-456.30 |
| profit/loss ratio | 2.2191 |
| win rate | 34.67 |
| sharpe_proxy/trade (K1) | 0.0563 |
| expectancy/trade (K2) | $53.03 |

Trend expectation: win<50% but P/L>1. The K1/K2 result is the verdict on whether the 12-name basket trended in 2019-2023 IS.

## Performance summary
| Metric | Value |
|---|---|
| net PnL | $17,129.69 on $100,000 (final $117,129.66) |
| total costs | $1,682.51 |
| max drawdown | 14.0459% |
| CAGR | 3.2204% |
| sharpe (ann) | 0.3412 |
| closed trades | 323 (~64.75/y) |
| annual turnover | 16.7817 |

## Cross-sector diagnostics (12 names)
A7 = `3.9225` - K10 = `0.4036` (66 pairs) - K6 max trade share `9.91%`, max |PnL| share `22.53%`, flag `False`.

| Symbol | Closed | Long/Short | Wins | Net PnL |
|---|---|---|---|---|
| AAPL | 23 | 14/9 | 15 | $14,034.50 |
| MSFT | 26 | 21/5 | 13 | $8,423.83 |
| NVDA | 23 | 16/7 | 7 | $6,434.30 |
| JPM | 25 | 15/10 | 7 | $-4,034.32 |
| XOM | 29 | 18/11 | 12 | $8,460.48 |
| UNH | 26 | 11/15 | 7 | $-2,650.08 |
| WMT | 32 | 15/17 | 8 | $-5,744.34 |
| KO | 27 | 13/14 | 6 | $-5,265.31 |
| META | 30 | 20/10 | 13 | $2,198.27 |
| AMZN | 27 | 15/12 | 7 | $-1,885.68 |
| JNJ | 29 | 17/12 | 9 | $-3,008.32 |
| CVX | 26 | 12/14 | 8 | $166.36 |

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

## Status
trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE - OOS never read - P6.5/P10 each separate authorization.
