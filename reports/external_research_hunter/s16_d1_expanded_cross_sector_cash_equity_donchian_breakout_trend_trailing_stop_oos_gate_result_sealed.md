# s16-d1 expanded-universe Donchian trend P10 OOS gate result (SEALED)

**FIRST OOS inspection** - **Report seal:** `7cbcbb20b40efa2af5d79bd2166918753d9b91f5d2c377a9a0ed57675258637f` - **Authored:** `2026-05-28T22:45:57.324479Z`
**OOS window (LOCKED):** 2024-01-02 -> 2025-12-30 - pure-OOS (WARMUP=40 OOS bars; no IS rows touched)
**Anchors:** SEAL `985c569` - P6 IS `8976a47` - P6.5 `b3a3bc5` - P7 `ecd777f`

## Verdict: `REJECT_FAST`
- DR4 oos_negative_while_is_positive: OOS net=$-2,837.19 (IS was +$17,129.69); sharpe_proxy=-0.0311, expectancy=$-21.33 -> REJECT_FAST

## OOS performance (DIAGNOSTIC-ONLY; NOT live-ready)
| Metric | Value |
|---|---|
| net PnL | $-2,837.19 on $100,000 (final $97,162.80; CAGR -1.4337%) |
| closed trades | 133 (~66.73/y) |
| expectancy/trade | $-21.33 |
| sharpe_proxy/trade | -0.0311 |
| sharpe (ann) | -0.1592 |
| win rate / P-L ratio | 33.83 / 1.8019 (avg win $739.42 / avg loss $-410.35) |
| max drawdown | 9.9062% |
| annual turnover | 15.1950 |
| exits | initial_stop 60 / trailing 68 / window_end 5 |

## IS vs OOS (DR4 canonical risk)
IS net +$17,129.69 (sharpe_proxy 0.0563, expc $53.03) vs OOS net $-2,837.19 (sharpe_proxy -0.0311, expc $-21.33). DR4 (oos_negative_while_is_positive) fires: True. DR1 (rebalance<36) fires: False. K9 OOS fail: False.

| Symbol | OOS closed | OOS net |
|---|---|---|
| AAPL | 8 | $649.01 |
| MSFT | 12 | $-112.57 |
| NVDA | 12 | $-1.34 |
| JPM | 14 | $-1,259.75 |
| XOM | 7 | $-763.62 |
| UNH | 13 | $652.13 |
| WMT | 9 | $2,937.71 |
| KO | 7 | $3,897.40 |
| META | 13 | $-1,239.23 |
| AMZN | 11 | $-2,048.91 |
| JNJ | 16 | $-2,441.87 |
| CVX | 11 | $-3,106.15 |

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
trading `PAUSED` - live `BLOCKED_AT_6_GATES` - FRC `NEVER_GRANTED` - DIAGNOSTIC_ONLY_NOT_LIVE_GRADE - REC1-equivalent binding - P11 lifecycle decision next.
