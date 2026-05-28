# s15-d1-cross-sector z-score exit-to-mean P7 decision memo (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `P7_DECISION_MEMO` · **Memo run_id:** `PHASE2-S15-D1-CROSS-SECTOR-P7-08d3ec230ba5`
**Authored (UTC):** `2026-05-28T21:39:02.175054Z` · **Report seal sha256:** `7aea8364333b8d3292831bc1624dfced1adaee153b85be1328dbaceaaddbf346`
**Lifecycle:** `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL`

## Verdict formalized: `FAIL_SAFETY` — candidate lifecycle TERMINAL

K1 (`sharpe_proxy/trade = -0.0938 < 0`) at S1 baseline; K2 (`expectancy = $-28.49/trade <= 0`) co-confirming. Fires upstream of the DR cost-stress chain — **P6.5 never reached**. Per SEAL `fail_safety_outcomes_terminal`, terminal.

## Central finding — the exit/stop redesign improved RISK but not EDGE

s15 tested the s14 hypothesis ("the exit/stop was the failure") by replacing BOTH components: **EXIT-TO-MEAN + 3.5σ vol-scaled catastrophe stop**. Result:

| Metric | s14 (RSI(3)+2N) | s15 (z-score+exit-to-mean) | Change |
|---|---|---|---|
| max drawdown | 14.04% | 7.17% | **halved** |
| net PnL | $-13,755 | $-5,128 | **loss cut ~63%** |
| expectancy/trade | $-39.53 | $-28.49 | less negative |
| sharpe_proxy/trade | -0.1119 | -0.0938 | less negative |
| win rate | 54.31% | 47.78% | **fell below 50%** |
| catastrophe-stop exits | (2N, frequent) | 29 of 180 | rare (disaster brake worked) |

The risk geometry improved markedly (drawdown halved, loss cut ~63%, catastrophe stop rarely hit), but the **edge did not flip positive**. The dominant failure shifted to **time-stops** (88 exits) on entries that never reverted to the mean within 10 bars. **Two consecutive FAIL_SAFETY on AAPL/JPM/XOM with two different mean-reversion mechanics indicate the mean-reversion edge on this universe over 2019-2023 IS appears structurally absent — not merely truncated by a bad stop.**

## Cross-sector thesis held again

A7 `2.0909` / K10 `0.4529` in band; K6 no concentration. Diversification was never the issue.

## Non-drivers

K4 (maxdd 7.17%) does not fire; K9 (180≥100) does not fire — NOT a sample problem; DR10 v2 / DR2-5 NOT evaluated (P6.5 never reached).

## Operator decision paths post-P7

- **A_PARK** — Park s15-d1-cross-sector z-score exit-to-mean permanently (default)
- **B_NEW_CANDIDATE_CHANGE_UNIVERSE_OR_MECHANIC_FAMILY** — Start a fresh candidate that changes the UNIVERSE or the MECHANIC FAMILY (not another mean-reversion exit tweak on AAPL/JPM/XOM) [separate authorization]
- **C_LESSONS_MD_UPDATE** — Write the eligible LESSON_S15_D1_* entries to lessons.md [separate authorization]
- **D_DEFER** — Defer / pause

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

## Parent references

Tier-N SEAL `597a49b` · P1 `c8d6dd5` · P2 `5b36ac8` · P3 BUILD `82f4919` · P4 smoke `bd02d2a` · P6 IS `2a6d130` (report_seal `61b15aac25516b1c5da474c3...`). s14-d1-cross-sector P7 terminal `6485ea9`. All-tech DRAFT `214bae0` preserved. Framework DR10 v2 `78cd22e` not modified.

## Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · **candidate lifecycle TERMINAL** · REC1-equivalent binding · `lessons.md` NOT touched this phase.
