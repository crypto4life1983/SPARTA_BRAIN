# C22 (external_signum_trend_radar_gc_long_short) — Closure Recommendation

Date: 2026-09-09
Mode: RESEARCH_ONLY. No paper, no live, no orders, no broker, no capital. This document authorizes nothing.
Status of this document: RECOMMENDATION awaiting the operator's recorded decision (see "Decision required" at the end).

## 1. Where C22 stands today (verified 2026-09-09)

| Item | State |
|---|---|
| Frozen daily windows collected | 81 (2026-06-20 → 2026-09-09; 2026-08-16 Sunday absent) |
| Collection gate | `C22_READY_FOR_FROZEN_WINDOW_REVIEW`; the review token was already consumed in July (`COLLECTION_REVIEW_CONSUMED = True`, decision `HOLD_FOR_MORE_C22_LABEL_EVIDENCE`) |
| Label evidence | V2 artifact only: 26 windows (06-20 → 07-15), 88 actionable labels, 75 shorts / 13 longs |
| Forward exit-path data (Phase B1) | Regenerated today: **`COVERAGE_COMPLETE_FOR_RANGE`**, 0 missing initial-horizon sessions (was `BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA` with 19 missing) |
| Short-instrument evidence (Phase B2) | All 22 short assets: perp `FAIL_CLOSED`, margin `FAIL_CLOSED`, borrow `ABSENT`; funding evidence ends 2026-06-21 |
| Acquisition plan (Phase B3) | `ACQUISITION_STATUS = NOT_AUTHORIZED`; 4 assets possibly unavailable at any tier |
| Replay spec (Phase A REV1) | Spec-only, SHA `9bf10af3…`; second human review (ACCEPT) never recorded |
| Fee-honest replay runner | **Does not exist** for C22 (exists for C4–C21) |
| Dry-run runner / NAV ledger | **Does not exist** |
| Results-review + rejection-record contracts | **Do not exist** for C22 |
| Out-of-radar exit prices | Local OHLC covers 7 of 27 signal assets and ends 2026-06-21 |

## 2. Why a decisive ACCEPT is not reachable on current data

1. The spec's `data_or_execution_rejection` class fails closed for any short whose instrument, venue, symbol map, and carry are not resolved. Per B2 that is all 22 short assets, i.e. 75 of the 88 actionable labels.
2. The long-only remainder is n = 13, below the spec's own `MIN_ACTIONABLE_LABELS_FOR_REPLAY = 30`.
3. REV1 freezes entries at ≤ 2026-07-15. The 55 newer windows are exit-path only; using them as entries needs a Phase A REV2 plus re-binding of the three SHA-pinned B contracts and a fresh review cycle.
4. Even with entries fixed, 4 % of symbol-days leave the top-50 with no next-bar price locally, and the rule is `NO_EXECUTABLE_NEXT_BAR` = fail-closed.

## 3. What it would cost to reach a decisive test

- Code never written: V3 label runner (small), no-PnL dry-run runner + pure NAV ledger (medium), C22 fee-honest replay runner with buy-and-hold + seeded random-entry nulls (medium), results-review and rejection-record contracts (small).
- Data not held: T3+ historical perp OHLC and sign-correct funding (or borrow availability + rates) for 22 assets across several venues from 2026-06-20 to close; venue fee schedules; spread/slippage evidence; symbol maps. Four assets may be unobtainable at any tier.
- Governance: record REV1 ACCEPT, B1/B2/B3 review outcomes, and rule on weekend sessions (M3) and entry window (M2).

Realistic outcome if all of that were done: with 26 entry windows and 88 labels the spec itself carries `insufficient_statistical_power_warning`; every annualized metric would be non-conclusive by construction.

## 4. Recommendation

**REJECT_KEPT_ON_RECORD — grounds: DATA_AND_EXECUTION_FEASIBILITY (not edge failure).**

- The edge was never tested and is therefore neither confirmed nor refuted. The rejection is on feasibility: the short leg, which carries 85 % of the signals, cannot be priced honestly with obtainable data, and the long-only leg is below the preregistered minimum sample.
- Keep everything on record (81 frozen windows, V2 labels, Phase A/B1/B2/B3 artifacts). If short-instrument evidence at tier T3 or better ever becomes available for the 22 assets, C22 may be re-opened as a new authorization; nothing is softened or rescued now.
- C23 stays ON-DECK/frozen under the 2026-09-09 candidate-family freeze.

## 5. Decision required (operator)

Record ONE of the following in `brain_memory/projects/trading_bot/decisions.md`:

- `HUMAN_DECISION_C22_REJECT_RECORDED_AT_LABELS_REVIEW` — adopts this recommendation. Closes C22 as REJECTED_KEPT_ON_RECORD (feasibility).
- `HUMAN_DECISION_C22_HOLD_PENDING_SHORT_INSTRUMENT_EVIDENCE` — keeps C22 open; requires authorizing B3 stages 1–3 acquisition and funding the runner build listed in §3.

No tool executes either token. Nothing runs until the operator writes it.
