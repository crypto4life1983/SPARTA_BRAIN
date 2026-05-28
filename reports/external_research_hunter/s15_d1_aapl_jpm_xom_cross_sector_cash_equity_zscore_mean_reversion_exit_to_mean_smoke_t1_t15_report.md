# s15-d1-cross-sector cash-equity z-score exit-to-mean P4 synthetic smoke report (SEALED)

**Phase:** `P4_SYNTHETIC_SMOKE` · **Lifecycle:** `P4_SYNTHETIC_SMOKE_SEALED`
**Verdict:** `P4_SMOKE_ALL_PASS` — **34/34 tests PASSED** (smoke 21/21, OOS 13/13) in ~0.11s
**Report seal sha256:** `2f19bc68d6aca541c2c0117360cc59492f05cb075d929a586aa81fabff8c7dd9`
**Authored (UTC):** `2026-05-28T21:30:26.946176Z`
**Authorization:** `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P4 synthetic smoke only.`
**Anchors:** SEAL `597a49b` · P1 `c8d6dd5` · P2 `5b36ac8` · P3 BUILD `82f4919` (runner `a13fa8a5…` / IS `28741317…` / OOS `d30e37ab…`)

## Results

- Smoke battery (z-score primitives + exit-to-mean + 3.5σ catastrophe stop + vol-normalized sizing + guards T18 + time-stop T19): **21/21 PASS**
- OOS driver invariants: **13/13 PASS**
- Total **34/34** in ~0.11s; synthetic fixture only; **sealed cross-sector CSVs NOT touched**.

## Exit/stop first-principles — STRUCTURAL validation (NOT an edge claim)

T18 confirms `assert_exit_to_mean_rule` + `assert_catastrophe_stop_vol_scaled_not_2N` PASS, and that reverting to an oscillator-threshold exit or a fixed-2N stop (the s14-d1 failed design) RAISES. T6/T7/T10 confirm exit-to-mean firing, 3.5σ stop placement, and vol-normalized sizing. **Whether this produces positive expectancy is the P6 IS test (the binding axis) — NOT established here.**

## Invocation note

`--rootdir`/`--confcutdir` pinned to the harness `tests/` dir to avoid the repo-root malformed-directory walk. Env guards: `HTTP_PROXY=invalid`, `HTTPS_PROXY=invalid`, `TIINGO_API_KEY` popped.

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

## Caveats

P4 validates STRUCTURAL primitives + invariants only — NOT IS/OOS performance or per-trade edge. REC1-equivalent binding carried. P4 PASS does NOT imply READY_FOR_LONGER_BACKTEST and NEVER implies live-readiness; 6-gate live-block applies. trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

## Boundaries held this P4 turn

Synthetic-fixture-only · no sealed CSV touched · no real-data signal computation · no IS/OOS execution/inspection · no backtest/fetch · no live/paper/Strategy Lab · no strategy optimization · no exit-to-mean / catastrophe-stop / z-score / universe / split_only change · no `_revN_`/patch/revival · no modification of any sealed artifact (SEAL 597a49b / P1 c8d6dd5 / P2 5b36ac8 / P3 82f4919 / all-tech 214bae0 / DR9 result / CSVs / DR10 v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## Next phase

P6 IS: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P6 IS diagnostic only` (separate authorization).
