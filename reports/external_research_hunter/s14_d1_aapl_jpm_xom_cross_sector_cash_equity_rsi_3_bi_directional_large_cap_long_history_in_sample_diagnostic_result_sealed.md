# s14-d1-cross-sector cash-equity P6 IS diagnostic result (SEALED)

**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Phase:** `PHASE2-S14-D1-CROSS-SECTOR-RSI-3-BIDIR` / `P6_IS_DIAGNOSTIC`
**Backtest run_id:** `PHASE2-S14-D1-CROSS-SECTOR-IS-86a6c2f2146a`
**Authored (UTC):** `2026-05-28T19:31:53.679219Z`
**Lifecycle state:** `P6_IS_DIAGNOSTIC_SEALED`
**Report seal sha256:** `5f31fd133cd78084ed43703504c096dbbcf13a060e3f48c9eb8920697ff7d443`

## Verdict: `FAIL_SAFETY`

### Reasons
- K1 sharpe_proxy_per_trade=-0.1119 < 0 at S1

### Caveats (LOAD-BEARING)
- P6 IS verdict reflects IS-window performance only; OOS verdict requires separate P10 authorization
- REC1-equivalent (binding): OOS K9 reachable with improved cross-sector margin but borderline at lower bound; sub-25/y effective IS rate -> structurally-probable OOS K9 unreachability -> PARKED_SAFE_BUT_OOS_INDETERMINATE
- P6 IS PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict
- P6.5 cost-stress NOT yet run; DR2/DR3/DR4/DR5/DR10 thresholds NOT YET EVALUATED at S0/S2/S3/S4 tiers
- A7 effective_independent_bets=2.0909 (cross-sector thesis; expected 2.3-2.8); K10 avg pairwise corr=0.4529 (expected 0.30-0.50). LOAD-BEARING for P7/OOS.

## Performance summary

| Metric | Value |
|---|---|
| `starting_cash_usd` | $100,000.00 (DA4=B) |
| `final_equity_usd` | $86,245.07 |
| `net_pnl_usd` | $-13,754.96 |
| `total_costs_usd` | $1,432.07 (commission $709.85 + slippage $722.22) |
| `max_drawdown_pct` (magnitude) | 14.0431% |
| `longest_drawdown_days` | 1774 |
| `cagr_pct` | -2.9229% |
| `sharpe_annualized` | -0.8035 |
| `sortino_annualized` | -1.0004 |
| `sharpe_proxy_per_trade` | -0.1119 |
| `expectancy_per_trade_usd` | $-39.53 |
| `profit_loss_ratio` | 0.6545 |
| `win_rate` | 54.31 |
| `closed_trades_count` | 348 |
| `trades_per_year_observed` | 69.76 |
| `annual_turnover` | 14.4539 |
| `s2_cost_drag_estimate` | 2.1481% |

## Cross-sector diagnostics (LOAD-BEARING)

- **A7 effective_independent_bets** = `2.0909` (expected 2.3-2.8)
- **K10 avg pairwise correlation** = `0.4529` (expected 0.30-0.50); pairwise: AAPL_JPM=0.4548, AAPL_XOM=0.3162, JPM_XOM=0.5877
- **K6 per-symbol dispersion**: max trade share `35.34%`, max |PnL| share `53.42%`, concentration-flag `False`

| Symbol | Closed | Long/Short | Wins | Net PnL |
|---|---|---|---|---|
| AAPL | 112 | 34/78 | 56 | $-7,348.07 |
| JPM | 123 | 57/66 | 65 | $-6,280.02 |
| XOM | 113 | 51/62 | 68 | $-126.87 |

## Scan diagnostics

| Field | Value |
|---|---|
| Universe | AAPL, JPM, XOM |
| Bars/symbol | AAPL=1258, JPM=1258, XOM=1258 |
| Unified date axis | 1258 (2019-01-02 -> 2023-12-29, ~4.9884y) |
| Warmup days | 30 |
| CSV sha verified (all 3) | True |
| OOS bars NEVER read in signal logic | True |

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

| Phase | Commit | Seal |
|---|---|---|
| Tier-N SEAL | `53cb804` | `862c00a5ffcc470580b6defe...` |
| P1 plan-lock | `02b77d8` | `fa6c2c52fb0befd5ec2345d3...` |
| P2 phase-2 plan | `27dbddc` | `89717a4a60ff6b704c592268...` |
| P3 BUILD | `30fbc6a` | runner/IS/OOS sealed |
| P4 smoke | `06bfcdb` | `e8bccb35...` |

## Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · REC1-equivalent binding · P6.5 cost-stress + P10 OOS each require separate authorization.
