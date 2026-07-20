# C22 Replay Specification — Phase A (spec-only, research-only)

Freezes *how* a future C22 fee-honest replay would run over the frozen V2 label
evidence. Runs no replay, fetches no data, issues no token, unlocks no gate.

- Verdict: **C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW**
- Spec SHA-256: `7d527fe4786328c715ae50fe778494949f4982f3ab62e5781cb405e259afa649`
- Replay-advance token (downstream, not issued): `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT`

## Frozen evidence
- Range 2026-06-20 → 2026-07-15, **26 windows**, **1300 rows**, **88 actionable** (BEAR_SHORT=72, HEDGE_SHORT=3, LONG_ENTRY=13)
- No date after 2026-07-15; excluded future dates: 2026-07-16, 2026-07-17, 2026-07-20
- Provenance tiers retained: FULL_RAW_REDUCTION_PROVENANCE=6, LEGACY_REDUCED_ONLY=8, LEGACY_REDUCED_WITH_SIDECAR_NO_RAW=12

## Exit methodology (single-sourced from the frozen detector spec)
- Long exit: `latest_closed_close < gc.upper (UPPER GC band)`; or `asset no longer in Trend Radar top-50 results on the evaluation date`
- Short: stop `latest_closed_close > gc.filter`; TP `latest_closed_close <= 0.65 * derived_short_entry_price`; or out-of-radar
- Max holding period in frozen spec: **None** (only bound = fail-closed END_OF_TEST)

## Price-path data — CRITICAL FINDING
- exit evaluation needs the daily Trend Radar SNAPSHOT (gc.upper, gc.filter, gc.trend + radar membership), NOT plain OHLC candles; only the take-profit (close <= 0.65*entry) is pure-price
- Missing-data status: **NOT_FROZEN_NOT_AUTHORIZED** (gate: `C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW`)
- Forward exit-path snapshots required 2026-07-16 → END_OF_TEST; post-2026-07-15 snapshots are admissible for EXIT EVALUATION ONLY; they MUST NOT create new entries and MUST NOT enter the V2 entry evidence
- On disk but out-of-scope until gated: 2026-07-16, 2026-07-17, 2026-07-20

## Execution & cost model (proposed, for human review)
- Entry/exit reference: next daily session OPEN after decision date D (next-bar) / next daily session OPEN after the exit-trigger evaluation date
- Transaction cost: **37 bps all-in round-trip** (NOT silently inherited; long-appropriate, short-transaction only)
- Short carry (funding if perp / borrow if margin) modeled separately; instrument UNRESOLVED pending human review

## Benchmarks
- BTC_buy_and_hold, equal_weight_passive_universe, zero_return_always_flat_null, fixed_seed_random_entry_null, c22_signal_off_null, gross_vs_net_strategy

## Pre-committed rejection gates
- Integrity: any duplicate trade; any lookahead violation; cost arithmetic mismatch; missing/interpolated bar used; provenance tiers not retained in attribution
- Execution/data: exit-path dataset not contiguous 2026-07-16..END_OF_TEST; any missing expected daily snapshot on a holding date; short instrument/carry model unspecified at run time; a post-2026-07-15 snapshot used to create a new entry
- Economic: net return <= 0 after costs; non-positive net Sharpe; does NOT beat the fixed-seed random-entry null on a risk-adjusted basis; does NOT beat BTC buy-and-hold on a risk-adjusted basis; forward/held-out segment not positive
- Power warning: 88 actionable entries over 26 daily windows is a SHORT, low-power path; annualized figures are fragile and any result is INDICATIVE, not conclusive; a WARNING is mandatory on every annualized metric

## Proposed lifecycle gates (not activated)
1. `C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW` — human reviews THIS frozen replay specification (token `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE`)
1. `C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW` — human reviews the frozen exit-path snapshot dataset + manifest (exit-only use of post-2026-07-15 snapshots) (token `HUMAN_DECISION_C22_FORWARD_PRICE_DATA_ACCEPT_OR_REJECT`)
1. `C22_DRY_RUN_READY_FOR_HUMAN_REVIEW` — human reviews the synthetic/no-PnL dry-run wiring (entry/exit/no-lookahead) (token `HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT`)
1. `C22_FEE_HONEST_REPLAY_READY_FOR_HUMAN_AUTHORIZATION` — human authorizes the ONE fee-honest replay run (token `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT`)
1. `C22_REPLAY_RESULTS_READY_FOR_HUMAN_REVIEW` — human reviews the frozen results + accept/reject decision (token `HUMAN_DECISION_C22_REPLAY_RESULTS_ACCEPT_OR_REJECT`)

## Recommendation

**READY_FOR_HUMAN_REVIEW_OF_C22_REPLAY_SPEC**
