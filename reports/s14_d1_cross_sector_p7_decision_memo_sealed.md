# s14-d1-cross-sector cash-equity P7 decision memo (SEALED)

**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Phase:** `P7_DECISION_MEMO`
**Memo run_id:** `PHASE2-S14-D1-CROSS-SECTOR-P7-094569a4d672`
**Authored (UTC):** `2026-05-28T19:37:32.543212Z`
**Lifecycle state:** `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL`
**Report seal sha256:** `addd83cf2cf358d0b0e95a1f860ff0ccf295b9989a1ef7af7b6d204a6d19c13e`

## Verdict formalized: `FAIL_SAFETY` — candidate lifecycle TERMINAL

Driven by **K1** (`sharpe_proxy_per_trade = -0.1119 < 0`) at the P6 IS S1 baseline, with **K2** (`expectancy = $-39.53/trade <= 0`) co-confirming. K1/K2 fire at S1 baseline, **upstream** of the DR cost-stress chain — **P6.5 was never reached** (moot once S1 baseline edge is negative). Per SEAL `fail_safety_outcomes_terminal_for_this_candidate_record_id`, the lifecycle is terminal.

## IS economics (RECORD-ONLY; unfavorable; not money-proven / not live-ready)

Unlike s13-d1 (which rejected a *profitable* strategy via a DR rule), this candidate fails on its own economics — net **NEGATIVE** in-sample.

| Metric | Value |
|---|---|
| net PnL | $-13,754.96 on $100,000 (final $86,245.07) |
| total costs | $1,432.07 (loss is mostly gross, not cost erosion) |
| expectancy / trade | $-39.53 |
| sharpe proxy / trade | -0.1119 |
| sharpe (annualized) | -0.8035 |
| max drawdown | 14.04% |
| win rate | 54.31% (>50% but negative expectancy: 2N stop-outs > RSI-exit winners) |
| closed trades | 348 (~69.76/y) — AAPL 112 / JPM 123 / XOM 113 |
| annual turnover | 14.4539 |

## Cross-sector thesis HELD — failure is the edge, not the basket

- **A7 effective-independent-bets** = `2.0909` (expected 2.3-2.8) — in band
- **K10 avg pairwise correlation** = `0.4529` (expected 0.30-0.50) — in band
- **K6** concentration flag: `False`

The AAPL/JPM/XOM basket diversified as intended; the RSI(3) bi-directional mechanic simply has a negative in-sample edge after the 2N stop.

## Non-drivers (audit)

- K4 (maxdd) does NOT fire (<50%); K9 does NOT fire (348 ≥ 100, ample sample); K6/K10 healthy.
- DR10 v2 / DR2 / DR3 / DR4 / DR5: **NOT evaluated** — P6.5 cost-stress was never reached (FAIL_SAFETY upstream at S1).

## What this does / does NOT demonstrate

Does: RSI(3) bi-dir mean-reversion + 2N hard stop = negative IS edge here; loss is gross; win-rate>50% with negative expectancy is the hard-stop signature; FAIL_SAFETY is fail-closed and terminal.

Does NOT: disprove the cross-sector hypothesis (A7/K10 in band); indicate a K9/sample problem (ample); condemn the all-tech sibling DRAFT `214bae0` (separate, preserved); prove RSI(3) universally dead (this *locked* spec failed; no post-SEAL iteration permitted within this candidate).

## Operator decision paths post-P7

- **A_PARK** — Park s14-d1-cross-sector RSI(3) bi-directional permanently for this framework (default)
- **B_NEW_CANDIDATE_DIFFERENT_MECHANIC_OR_EXIT** — Start a fresh candidate with a different exit/stop structure or mechanic family [separate authorization]
- **C_LESSONS_MD_UPDATE** — Write the eligible LESSON_S14_D1_* entries to lessons.md [separate authorization]
- **D_DEFER** — Defer / pause

## C6 inherited_constraints_block (carried verbatim from SEAL; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable with improved margin vs all-tech (cross-sector higher signal independence ~75% vs all-tech ~60%; expected effective rate 45-79/y vs 50/y OOS floor). If observed effective IS rate falls below 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per s10-d2/s12-d1 precedent. The chain shall NOT relax K9 at OOS.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); standard sizing (not nano); admissible under DR10 v2 for cash equity
3. DA4=B (BINDING): START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin at $100k for cash equity
4. K9-reachability discipline applied at PLAN+DRAFT+SEAL; binding for all subsequent phases
5. DR10-v2-reachability discipline applied at PLAN+DRAFT+SEAL (AND-conjunction); CLEARS WITH STRONG MARGIN
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family F3-adjacent RSI(3) bi-directional mean-reversion LOCKED at PLAN
8. RSI thresholds 15/55/85/45 LOCKED at PLAN; modification post-SEAL FORBIDDEN
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50 turnover / 0.05 cost_drag immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention LOCKED (DA17); switching/mixing post-SEAL FORBIDDEN
11. Cross-sector universe {AAPL (Tech), JPM (Financials), XOM (Energy)} LOCKED at PLAN; universe widening/substitution post-SEAL FORBIDDEN
12. A7 effective_independent_bets + K10 avg_pairwise_correlation LOAD-BEARING (multi-name cross-sector; A7 ~2.3-2.8 / K10 ~0.30-0.50 expected; the candidate's central diversification thesis)
13. Cross-sector DR9 data-availability gate PASSED all 3 symbols (AAPL reused+carried; JPM/XOM fresh-fetched+audited); sealed at b13af03 report_seal a8ff9126...; data provenance locked
14. All-tech sibling DRAFT (214bae0) preserved byte-stable; non-mutually-exclusive sibling; this candidate is NOT a _revN_
15. P6 IS PASS (if reached) does NOT imply READY at OOS; OOS requires separate P10-equivalent authorization
16. P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## Parent references

Tier-N SEAL `53cb804` · P1 `02b77d8` · P2 `27dbddc` · P3 BUILD `30fbc6a` · P4 smoke `06bfcdb` · P6 IS `7248a96` (report_seal `5f31fd133cd78084ed437035...`). All-tech sibling DRAFT `214bae0` preserved. Framework DR10 v2 `78cd22e` not modified.

## Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · **candidate lifecycle TERMINAL** · REC1-equivalent binding · no_dr_redefinition_post_seal. `lessons.md` NOT touched this phase.
