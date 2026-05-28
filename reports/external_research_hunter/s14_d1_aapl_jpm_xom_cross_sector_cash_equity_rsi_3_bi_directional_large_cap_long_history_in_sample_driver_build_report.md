# S14-D1-CROSS-SECTOR cash-equity P3 BUILD in-sample driver report

**Lifecycle state:** `P3_BUILD_IN_SAMPLE_DRIVER_REPORT_SEALED`
**Report seal sha256:** `8a7e525e4b9c87a8cef3561232ba3964ba674dccc1a09ffc19d4620eeba22fb5`
**Authored (UTC):** `2026-05-28T19:00:41.175628Z`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`

## Anchors

- Tier-N SEAL `53cb804` · report_seal `862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c`
- P1 plan-lock `02b77d8` · report_seal `fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00`
- P2 phase-2 plan `27dbddc` · report_seal `89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67`
- Cross-sector DR9 result `b13af03` · report_seal `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c`
- Framework DR10 v2 `78cd22e`

## C6 inherited_constraints_block (carried verbatim; 16 entries)

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

## Boundaries

P3 BUILD only · py_compile syntax-checked (no import/execution/signal computation) · tests AUTHORED NOT RUN (P4 requires separate authorization) · no backtest/fetch/OOS-inspection/live/Strategy Lab · no modification of any sealed artifact (SEAL/P1/P2/DRAFT/PLAN/DR9-result/CSVs/manifest/all-tech-214bae0/multi-instrument/s13-d1/s12-d1/DR10-v2-78cd22e) · **no `lessons.md`** · **no commit this turn**.

## Next phase

P4: `Authorize s14-d1-cross-sector cash-equity P4 synthetic smoke only` (separate authorization).
