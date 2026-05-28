# s14-d1-cross-sector cash-equity P4 synthetic smoke report (SEALED)

**Phase:** `P4_SYNTHETIC_SMOKE`
**Lifecycle state:** `P4_SYNTHETIC_SMOKE_SEALED`
**Verdict:** `P4_SMOKE_ALL_PASS` — **32/32 tests PASSED** (smoke 19/19, OOS 13/13) in ~0.11s
**Report seal sha256:** `e8bccb3507ffe5be646b2952ea93999b22aad70730dde3df9f9bae7eb1458ae3`
**Authored (UTC):** `2026-05-28T19:24:29.470002Z`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization:** `Authorize s14-d1-cross-sector cash-equity P4 synthetic smoke only.`

## Results

- Smoke battery (T1-T15 + T7b + T7c + T16 universe-lock + T17 split_only): **19/19 PASS**
- OOS driver invariants battery: **13/13 PASS**
- Total **32/32** in combined ~0.11s; synthetic fixture only; **sealed cross-sector CSVs (AAPL/JPM/XOM) NOT touched**.

## P3 build-report count correction (transparency)

The sealed P3 runner build report (commit `30fbc6a`) recorded the smoke `test_count_authored` as **17** (a value carried over from the s13-d1 sibling). The smoke file actually contains **19** test functions; the name-list in that same P3 report is correct at 19. P4 collected and passed all 19 smoke + 13 OOS = 32. The sealed P3 report is **NOT modified**; this P4 report is the authoritative count and records the discrepancy in the new artifact.

## Invocation note

`--rootdir`/`--confcutdir` were pinned to the harness `tests/` dir. The repo root contains a malformed sibling directory (private-use-char name) that breaks pytest's default rootdir walk with an unrelated `FileNotFoundError`; pinning confines collection. Env guards: `HTTP_PROXY=invalid`, `HTTPS_PROXY=invalid`, `TIINGO_API_KEY` popped.

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

## Caveats

P4 validates STRUCTURAL primitives + invariants only — NOT IS/OOS performance. REC1-equivalent binding carried: OOS K9 borderline at lower bound; sub-25/y effective IS rate -> structurally-probable OOS K9 unreachability -> PARKED_SAFE_BUT_OOS_INDETERMINATE. P4 PASS does NOT imply READY_FOR_LONGER_BACKTEST and NEVER implies live-readiness; 6-gate live-block applies regardless. trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.

## Boundaries held this P4 turn

Tests run against authored P3 BUILD files + synthetic fixture only · no sealed CSV touched · no real-data signal computation · no IS/OOS execution/inspection · no backtest/simulator/fetch · no tiingo/network/QC/broker · no live/paper/Strategy Lab · no DR redefinition / RSI-threshold / K9 / universe / split_only change · no modification of any sealed artifact (SEAL 53cb804 / P1 02b77d8 / P2 27dbddc / P3 30fbc6a / DRAFT bfb6495 / PLAN c61860d / DR9-result / CSVs / manifest / all-tech 214bae0 / multi-instrument / s13-d1 / s12-d1 / DR10-v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## Next phase

P6 IS: `Authorize s14-d1-cross-sector cash-equity P6 IS diagnostic only` (separate authorization).
