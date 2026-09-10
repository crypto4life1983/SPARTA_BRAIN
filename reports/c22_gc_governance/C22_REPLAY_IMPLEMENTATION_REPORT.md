# C22_REPLAY_IMPLEMENTATION_REPORT

Date: 2026-09-09/10 · Repo `C:\SPARTA_BRAIN` (master) · Authorization: replay infrastructure only.
Not a performance result. No strategy rule, threshold, sizing rule, frozen export, V2 artifact,
V2 hash, or Phase A/B1/B2/B3 specification was modified. No paper/live/order/credential surface
was touched. No profile was selected. No performance was computed.

## A. Files added or modified

Commits (all on master, none pushed): `ea71033e`, `32e6a4f2`, `9fd4fd89`, `a7e79fd1`, `decb76c7`, plus the docs commit that carries this report.

**Added — code**
- `sparta_commander/c22_replay_ledger_contract.py` — pure deterministic portfolio ledger (Task 3).
- `sparta_commander/c22_replay_lifecycle_engine_contract.py` — fill + lifecycle engine, both weekend profiles, END_OF_DATA (Tasks 2, 4, 8).
- `sparta_commander/c22_replay_cost_engine_contract.py` — cost interfaces; 37 bps sensitivity-only; no frozen base case (Task 7).
- `tools/c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once.py` — V3 runner over the unchanged V2 contract (Task 1).
- `tools/c22_signum_gc_v3_label_evidence_integrity_report_once.py` — V3 integrity + V2-unchanged + V2-subset proof (Task 1).
- `tools/c22_replay_dry_run_once.py` — no-P&L dry run, 88-signal reconciliation (Task 5).
- `tools/c22_fee_honest_replay_once.py` — fail-closed precondition shell (Task 6).

**Added — tests (74 new)**
`tests/test_c22_signum_trend_radar_gc_v3_extended_runner_gate.py` (10), `tests/test_c22_signum_gc_v3_label_evidence_integrity_report.py` (5), `tests/test_c22_replay_ledger_contract.py` (18), `tests/test_c22_replay_cost_engine_contract.py` (7), `tests/test_c22_replay_lifecycle_engine_contract.py` (20), `tests/test_c22_replay_dry_run_gate.py` (9), `tests/test_c22_fee_honest_replay_preconditions.py` (5).

**Added — artifacts and reports**
- `data/external_signum_trend_radar_gc/detector_labels/v3_extended/` (git-ignored): 82w, 57w, 24w V3 artifacts.
- `data/external_signum_trend_radar_gc/gc_crypto_trendradar_daily_20260816.json` + raw top-100 + reduction sidecar — admitted through the existing guarded pickup chain (operator downloaded the file; the scheduled task imported it at 22:24). Not a manufactured window.
- `reports/c22_gc_label_pipeline_v3_evidence/` — three integrity reports (json+md).
- `reports/c22_gc_replay_dry_run/c22_replay_dry_run_no_pnl.{json,md}` — sha `f76f8330…`.
- `reports/c22_gc_governance/c22_governance_reconciliation_2026-09-09.md` (Task 9).
- `reports/c22_gc_governance/c22_2026-06-26_readmission_provenance_note_PROPOSED.md` (Task 10).
- `docs/superpowers/specs/2026-09-09-c22-v3-extended-first-replay-audit.md`, `docs/superpowers/plans/2026-09-09-c22-v3-extended-first-replay-plan.md` (audit + plan from the prior turn).

**Modified:** none of the pre-existing C22 modules, tools, tests, reports, or data. (Another session regenerated the B1 readiness report and wrote a closure recommendation today in commit `a0449ca2`; not part of this work.)

## B. Tests before and after

| Suite | Before | After |
|---|---|---|
| Existing C22 tests (`tests/test_c22_*.py` + 2 wiring tests) | 190 passed | 190 passed (unchanged) |
| New tests | — | 74 passed |
| Total C22 | 190 | **264 passed** |

Run from `C:\SPARTA_BRAIN\tests` with `PYTHONPATH=C:\SPARTA_BRAIN` (root collection is broken by a pre-existing stray directory `C:\SPARTA_BRAIN\"hydra `; left in place).

## C. V3 integrity results

| Profile | Windows | Labels | Actionable (L/B/H) | Rebuild byte-identical | V2 unchanged | V3⊂V2 rows identical | EXIT_ONLY windows | Recommendation |
|---|---|---|---|---|---|---|---|---|
| V3_EXTENDED_82W (06-20→09-09) | 82/82 | 4100 | 75 / 104 / 29 | ✔ | ✔ | ✔ (88 actionable in V2 range) | 56 | PASS_DIAGNOSTIC_ONLY |
| SEG_A_57W (06-20→08-15) | 57/57 | 2850 | 33 / 104 / 22 | ✔ | ✔ | ✔ | 31 | PASS_DIAGNOSTIC_ONLY |
| SEG_B_24W (08-17→09-09) | 24/24 | 1200 | 42 / 0 / 7 | ✔ | ✔ | n/a (no overlap) | 24 | PASS_DIAGNOSTIC_ONLY |

Segments A+B reconcile to 82W exactly (the admitted 08-16 window carries zero actionable labels). Provenance: 62 FULL_RAW, 12 SIDECAR_NO_RAW, 8 LEGACY; no mandatory evidence missing. V3 artifacts live in a separate sub-directory, keep the V2 basename the validator requires, and tag every post-2026-07-15 window `EXIT_ONLY`. V2 artifact sha `b6a28a48…` verified unchanged.

## D. V2 88-signal reconciliation (no-P&L dry run)

V2 artifact SHA-pinned before read; 88 actionable signals loaded (13 LONG / 72 BEAR / 3 HEDGE); every signal has exactly one record under each profile; lifecycle totals sum to 88; `no_silent_drops = true` for both profiles. Ledger invariants valid (cash reconciles, gross ≤ cap, one position per asset). Realized and unrealized P&L are exactly 0.0 by construction.

Sizing observed (frozen rules only): 72 × 5 %, 3 × 3 %, 7 × 8 % (long, breakout ≤ 25 d), 6 × 2 %.

## E. Weekend-profile differences

Two interpretations run side by side; **none selected**.

| | V2_CONTRACT_EXACT (weekday sessions, B1) | CRYPTO_CALENDAR_SENSITIVITY (every export day) |
|---|---|---|
| Sessions over 06-20→09-09 | 58 | 82 |
| Weekend-dated frozen signals | 26 (decided on their date, filled next weekday) | 26 |
| CLOSED / REJECTED / MISSING_PRICE / OPEN_AT_END | 25 / 54 / 3 / 6 | 27 / 52 / 3 / 6 |

23 of 88 signals differ in at least one field: entry_date 9, entry_price 9, exit_condition_date 14, exit_date 16, exit_price 16, exit_reason 3, lifecycle_status 3, reject_reason 2, requires_external_ohlc 2. Lifecycle-status flips: `2026-06-20|DEXEUSDT|LONG` (OPEN_AT_END vs CLOSED), `2026-06-23|DEXEUSDT|LONG` (REJECTED vs OPEN_AT_END), `2026-07-07|SPXUSD|LONG` (REJECTED vs CLOSED). Full per-signal table in the dry-run report. Ruling remains human (`HUMAN_DECISION_C22_WEEKEND_SESSION_RULE`).

## F. Candidate trades per lifecycle state

| State | V2_CONTRACT_EXACT | CRYPTO_CALENDAR |
|---|---|---|
| PENDING_ENTRY | 0 | 0 |
| OPEN (mid-run only) | 0 | 0 |
| CLOSED (natural frozen exit, admitted price) | 25 | 27 |
| REJECTED (all `ONE_POSITION_PER_ASSET`; no cap or cash rejection occurred) | 54 | 52 |
| DATA_GAP | 0 | 0 |
| MISSING_EXECUTION_PRICE (entry: symbol left top-50 before fill) | 3 | 3 |
| INSTRUMENT_UNVERIFIED (lifecycle-only mode; strict mode would give 88) | 0 | 0 |
| OPEN_AT_END_OF_DATA | 6 | 6 |
| Exit reasons among closed | 17 short stop / 7 long below upper / 7 out-of-radar (fillable) | 17 / 9 / 7 |
| Peak gross exposure | 27 % NAV | 27 % NAV |

All 6 OPEN_AT_END_OF_DATA positions in both profiles are out-of-radar exit conditions whose next-bar price is not carried by any admitted export (QNT, ASTER, DEXE, OKB, GRAM, KAS). None was force-closed; mark-to-market is null where the symbol is absent from the last export.

## G. Exact external execution evidence still missing

- **Short-instrument evidence (B2/B3 hierarchy) for 22 assets:** AAVE, CRV, IMX, INJ, LINK, PENDLE, QNT, SOL, SUN, TIA, TRX, VIRTUAL, ZEC (Binance); LEO (Bitfinex); GRAM, TEL (Bybit); MORPHO (Coinbase); ASTER, GT (Gate); KAS, SPX (Kraken); OKB (OKX). Required per asset: canonical identity, historical execution instrument, venue, existence on required dates, historical shortability mechanism, historical OHLC coverage, fee schedule, funding/borrow, min qty/notional, tick/lot, liquidity/spread. Admitted evidence today: **0 of 22**. `data/c22_short_instrument_evidence/` does not exist.
- **Long execution-venue evidence for 8 assets:** AAVE, DEXE, JST, JUP, ZEC (Binance), AERO, MORPHO (Coinbase), SPX (Kraken). Admitted: 0 of 8.
- **External OHLC for out-of-radar / missing-price fills:** 9 signals per profile (6 exits + 3 entries).
- **Cost base case:** `C22_COST_BASE_CASE_NOT_FROZEN`; 37 bps remains `SENSITIVITY_CASE_NOT_BASE_CASE`.
- **Basis alignment:** `BASIS_ALIGNMENT_NOT_REVIEWED` (signal prices are CMC reference prices).
- Local funding ends 2026-06-21; local borrow: `ABSENT_FOR_ALL_22`.

## H. Trades currently replayable fee-honestly

**0.** Every one of the 88 records is `instrument_status = UNVERIFIED`, and no cost base case is frozen.

## I. Number blocked and why

88 blocked. Precondition shell (`tools/c22_fee_honest_replay_once.py`) unsatisfied gates: replay_spec_accepted, forward_exit_contract_accepted, execution_data_contract_accepted, dry_run_accepted, short_instrument_selected, cost_base_case_frozen, weekend_session_rule_ruled, basis_alignment_reviewed, historical_evidence_admitted, all_required_instruments_evidenced (0 of 26 instruments). Structural sub-blockers: 22 of 26 instruments are shorts with FAIL_CLOSED evidence; 9 signals per profile need an external price source; 6 positions per profile are open at the data boundary.

## J. Positions still unresolved at end of data

Boundary = last admitted export **2026-09-09** (82 exports, forward coverage under the frozen B1 weekday rule `COVERAGE_COMPLETE_FOR_RANGE`, extension #2).

| Signal | Exit condition met (V2_EXACT / CALENDAR) | Why unresolved |
|---|---|---|
| 2026-06-20 BINANCE:QNTUSDT BEAR_SHORT | 08-17 / 08-15 | out-of-radar, no admitted next-bar price |
| 2026-06-21 GATE:ASTERUSDT BEAR_SHORT | 08-17 / 08-15 | same |
| 2026-06-20 or 06-23 BINANCE:DEXEUSDT LONG_ENTRY | 06-29 / 06-28 | same (which DEXE signal holds depends on profile) |
| 2026-06-23 OKX:OKBUSDT BEAR_SHORT | 06-29 / 06-28 | same |
| 2026-07-05 BYBIT:GRAMUSDT BEAR_SHORT | 08-24 / 08-24 | same |
| 2026-07-05 KRAKEN:KASUSD BEAR_SHORT | 07-20 / 07-18 | same |

Plus 3 entries never filled (AAVE 06-26 short, AAVE 06-27 long, TEL 07-09 short: symbol absent from the next export). Performance conclusion for the frozen cohort: `INCOMPLETE_FOLLOWUP` (would apply once P&L is enabled); today `NOT_COMPUTED_PNL_DISABLED`.

## K. Whether a decisive replay can now run

**No.** Mechanically the ledger, engine, dry run and precondition shell exist and are tested; governance and evidence do not. Independent of the evidence gap, the long-only remainder (13) is below the spec's own `MIN_ACTIONABLE_LABELS_FOR_REPLAY = 30`, and a 2026-09-09 closure recommendation by another session proposes `REJECT_KEPT_ON_RECORD` on feasibility grounds. That decision is the operator's and is still unrecorded.

## L. Exact next action

1. Operator records the pending closure decision named in `reports/c22_gc_decision/c22_closure_recommendation_2026-09-09.md` (`HUMAN_DECISION_C22_REJECT_RECORDED_AT_LABELS_REVIEW` or `HUMAN_DECISION_C22_HOLD_PENDING_SHORT_INSTRUMENT_EVIDENCE`).
2. If HOLD: write the dated approval records for the B3 fetch authorizations (the operator's 2026-09-09 message authorizes historical/public/read-only acquisition; the precondition shell needs the records in `reports/approvals/`), then run B3 stage 1 (instrument-existence registry, official venue sources ≥ T3) for the 22 short instruments first, fail-close-early, into `data/c22_short_instrument_evidence/manifests/`. Present-day availability is rejected as proof by the shell.
3. Rule the weekend session profile on governance grounds and record it; then review and record ACCEPT/REVISE on the dry-run report.

Nothing above executes automatically. No performance number exists for C22.
