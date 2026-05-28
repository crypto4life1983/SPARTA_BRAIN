# s14-d1-cross-sector cash-equity P2 phase-2 plan (SEALED)

**Phase:** `P2_PHASE2_PLAN`
**Authored (UTC):** `2026-05-28T18:45:24.716258Z`
**Lifecycle state:** `S14_D1_CROSS_SECTOR_CASH_EQUITY_P2_PHASE2_PLAN_SEALED`
**Report seal sha256:** `89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization:** `Authorize s14-d1-cross-sector cash-equity P2 phase-2 plan only — bound by DR10 v2.`

## §1. Seal inheritance (K8 drift check: PASS)

| Field | Value |
|---|---|
| Tier-N SEAL | commit `53cb804` · report_seal `862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c` |
| P1 plan-lock | commit `02b77d8` · report_seal `fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00` (file sha `fb19baf1c8c507a3f680cf031b847c41abc38c2265976f89e8dabe0abe0cef3c`) |
| Cross-sector DR9 result | report_seal `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c` |
| Framework DR10 v2 | commit `78cd22e` |
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
| C5 | C5_corporate_action_handling | CASH-EQUITY ADAPTATION: splits documented + applied per split_only convention (NOT structurally absent like futures). Known splits: AAPL 2020-08-31 4:1 (applied+verified); JPM none; XOM none. Dividends NOT adjusted (split_only). divCash informational only. DR9 documented_split_event_consistency PASSED all 3. |
| C6 | C6_inherited_constraints | 16-entry inherited_constraints_block carried verbatim from SEAL (REC1-equivalent + DA3=B + DA4=B + K9/DR10-reachability + split_only + cross-sector universe + A7/K10 load-bearing + DR9 PASS carried + ...) |
| C7 | C7_verdict_closed_enum | verdict restricted to closed enum (READY_FOR_LONGER_BACKTEST / INSUFFICIENT_SAMPLE / FAIL_SAFETY / REJECT_FAST / INCONCLUSIVE_HOLD / ...); forbidden-token blocklist; no profitability/live-ready/money-proven tokens |
| C8 | C8_lifecycle_states | permanent lifecycle attributes carried (DIAGNOSTIC_ONLY_NOT_LIVE_GRADE; trading PAUSED; live BLOCKED_AT_6_GATES; FRC NEVER_GRANTED; no_strategy_optimization_authorized; no_dr_redefinition_post_seal) |

**Cash-equity adaptation highlight (C5):** splits documented + applied per split_only (NOT structurally absent like futures). AAPL 2020-08-31 4:1 applied+verified; JPM/XOM no splits. Dividends NOT adjusted (split_only). DR9 split-event-consistency PASSED all 3.

## §3. C6 inherited_constraints_block (carried verbatim; 16 entries)

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

## §4. P3 BUILD scope defined (no automatic build/run)

**BUILD creates:**
- runner harness (main.py): CONFIG byte-equivalent to SEAL DA register; Algo class; RSI(3) bi-directional + Wilder ATR(14) + 2N stop + 0.5% risk per-name sizing primitives; per-name independent signal generation; portfolio max 3 positions; QC-compat shim
- in_sample_driver.py: filters sealed cross-sector CSVs to IS window 2019-01-02->2023-12-29; run_in_sample() STUB raising P6_IS_NOT_AUTHORIZED until separate P6 authorization
- out_of_sample_driver.py: filters to OOS window 2024-01-02->2025-12-30; run_out_of_sample() STUB raising P10_OOS_NOT_AUTHORIZED; REC1-equivalent binding reminder
- execution_guard.py: C1-C8 attestation utilities; K8 sealed-parent-drift check against SEAL constants; assert_locked_strategy_params; assert_split_only_convention
- tests/: synthetic smoke battery (no real-data run at BUILD)
- 3 sealed build reports (runner / IS-driver / OOS-driver)

**BUILD does NOT:**
- execute any backtest / simulator / signal computation
- fetch data (reuses sealed cross-sector CSVs DR9-passed)
- read OOS rows in signal logic
- place any order / connect broker / live
- promote to Strategy Lab

BUILD reuses the sealed cross-sector CSVs (DR9-PASSED, sealed at `b13af03`). P3 source files byte-stable across P6 (simulator-in-tmp/ pattern). **P3 BUILD requires separate authorization.**

## §5. Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding · s13-d1 + s12-d1 terminal · framework DR10 v2 binding. **s14-d1-cross-sector lifecycle: `S14_D1_CROSS_SECTOR_CASH_EQUITY_P2_PHASE2_PLAN_SEALED`.**

## §6. Hard boundaries held this P2 turn

P2 phase-2 plan only · no P3 BUILD · no BUILD executed · no fetch/refetch · no backtest/simulator/OOS · no live/Strategy Lab · no candidate promotion · no s13-d1/s12-d1/parked revival · **no DA resolution changed · no C-contract weakened** · **no modification of any existing sealed artifact** (SEAL + P1 + DRAFT bfb6495 + PLAN c61860d + cross-sector DR9 result + fetched CSVs/manifest + all-tech DRAFT 214bae0 + s14-d1-multi-instrument chain + s13-d1/s12-d1 chains + framework DR10 v2 78cd22e all byte-stable) · no phase-2-safety-contract template modification · no CLAUDE.md / .gitignore modification · **no `lessons.md` modification or staging** · no review_queue/idea_memory mutation · no profitability claim · C6 carried verbatim · DR10 v2 by-reference (not redefined) · **no commit by this turn**.

## §7. Next-phase authorization scope

- **Commit this P2:** `Authorize commit s14-d1-cross-sector cash-equity P2 phase-2 plan only.`
- **Primary forward:** `Authorize s14-d1-cross-sector cash-equity P3 BUILD only — bound by DR10 v2.`
- **Defer:** `Defer / Pause s14-d1-cross-sector cash-equity at P2.`

End of P2 phase-2 plan. C1-C8 instantiated byte-equivalent (C5 cash-equity split_only adaptation); C6 16 entries verbatim; anchors SEAL + P1; P3 BUILD scope defined (no auto build/run). Not committed this turn.
