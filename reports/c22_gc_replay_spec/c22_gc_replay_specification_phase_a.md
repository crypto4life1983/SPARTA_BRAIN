# C22 Replay Specification — Phase A, REV1 (spec-only, research-only)

Revised under HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=REVISE. Freezes *how* a future C22 fee-honest replay would run over the
frozen V2 label evidence. Runs no replay, fetches/admits no data, approves no short
model or cost base case, issues no token, unlocks no gate.

- Verdict: **C22_REPLAY_SPEC_READY_FOR_SECOND_HUMAN_REVIEW**
- Spec SHA-256: `9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867`
- Replay-advance token (downstream, not issued): `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT`

## Frozen evidence
- Range 2026-06-20 → 2026-07-15, **26 windows**, **1300 rows**, **88 actionable** (BEAR_SHORT=72, HEDGE_SHORT=3, LONG_ENTRY=13)
- No new entry after 2026-07-15; excluded future dates: 2026-07-16, 2026-07-17, 2026-07-20
- Provenance tiers retained: FULL_RAW_REDUCTION_PROVENANCE=6, LEGACY_REDUCED_ONLY=8, LEGACY_REDUCED_WITH_SIDECAR_NO_RAW=12

## Exit methodology & forward-data extension (point 1)
- Long exit: `latest_closed_close < gc.upper (UPPER GC band)`; or `asset no longer in a VALID Trend Radar top-50 export on the evaluation date`
- Short: stop `latest_closed_close > gc.filter`; TP `latest_closed_close <= 0.65 * derived_short_entry_price`; or out-of-radar
- Max holding period in frozen spec: **None** — no artificial strategy max-hold
- Forced/administrative liquidation is a **non-decisive truncation diagnostic only**
- Initial review 30 calendar days; if positions remain open → **BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA**; extend in predeclared **15-day** increments until every position closes naturally
- Weekend/non-export: exit sessions occur ONLY on valid daily export dates; weekends / non-export days have NO decision session and the open position simply carries; the extension increment is counted in CALENDAR days but evaluation happens only on export sessions

## Forward Trend Radar snapshot use (point 4)
- Authoritative export: the daily Signum Trend Radar 'gc/crypto' export for the evaluation date -- the same export family and reduced top-50 convention as the frozen collection windows; determines gc.upper, gc.filter, gc.trend and top-50 radar membership
- Out-of-radar = absence from the reduced TOP-50 of a VALID, well-formed export on the evaluation date == out-of-radar
- Friday→Monday: a Friday-held position is evaluated on Friday's export; the next executable market bar is the next export session (typically Monday); no weekend fills
- Malformed/unavailable export: FAIL-CLOSED replay halt on an expected trading/export session (NOT an exit, NOT a skip); a missing expected session is a data-integrity failure
- Post-2026-07-15 snapshots marked `EXIT_ONLY` and rejected for any entry
- Missing-data status: **NOT_FROZEN_NOT_AUTHORIZED** → BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA (gate `C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW`)

## Delisting / unavailability (point 5, separate from out-of-radar)
- **ABSENT_FROM_TOP50**: valid export, asset not in top-50 -> ordinary out-of-radar exit at the next executable bar
- **MISSING_FROM_SINGLE_EXPORT**: asset still trading but absent from ONE otherwise-valid export -> flagged SINGLE_EXPORT_ABSENCE; treated as out-of-radar but reported separately for human review, never silently
- **TEMPORARY_SUSPENSION**: market halted / no executable price -> HOLD the position, flag SUSPENDED; never invent a price; if it cannot resolve within reviewed coverage -> BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA
- **PERMANENT_DELISTING**: exit ONLY at a real last executable market price, flagged DELISTED_EXIT; excluded from decisive edge attribution; NO invented/ favourable liquidation price
- **NO_EXECUTABLE_NEXT_BAR**: data-integrity FAIL-CLOSED, unless the PERMANENT_DELISTING last-real-price rule applies (then flagged)

## Short instrument gate (point 2 — UNRESOLVED)
- Status: **UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION**; 37bps short model approved: **False**
- Human must select: linear_perpetual_futures OR spot_margin_short
- Fail-closed when: the required short instrument did not exist on the signal date; historical funding (perp) or borrow cost (margin) is missing; borrow availability cannot be established; the spot and derivative symbol cannot be mapped deterministically; the execution price source differs materially from the signal-price source without an approved basis adjustment

## Execution & cost model (point 3 — disaggregated)
- Entry/exit reference: next executable market session OPEN after decision date D / next executable market session OPEN after the exit-trigger evaluation date
- Components: exchange_fee_entry, exchange_fee_exit, bid_ask_spread, entry_slippage, exit_slippage, funding_or_borrow_cost, exceptional_or_liquidation_exit_cost
- 37 bps role: **LABELLED SENSITIVITY CASE ONLY (not the approved base case)** (base case NOT frozen here; from a SEPARATELY reviewed execution-data contract; the base-case component values MUST be frozen before replay (not set here))
- Results required at: gross, transaction_cost_only, fully_net

## Exposure ordering (point 6)
- Deterministic order: decision_date_ascending → market_rank_ascending → stable_asset_identifier_ascending
- on any execution session EXITS are processed BEFORE entries (freed NAV becomes available to that session's entries)
- Insufficient NAV: DETERMINISTIC REJECTION by the ordering above -- a signal that does not fit under the 100% NAV cap is SKIPPED, never proportionally resized
- No simultaneous long+short same asset: True

## Benchmarks (point 7)
- BTC_buy_and_hold, equal_weight_passive_universe_point_in_time, zero_return_always_flat_null, fixed_seed_matched_random_entry_null, c22_signal_off_control, gross_vs_net_strategy
- Survivorship control: the equal-weight passive universe uses ONLY assets KNOWN at each decision date (point-in-time top-50 membership); no asset admitted on later knowledge
- Random null: fixed seed; MATCHED to the strategy's side mix (long/hedge/bear proportions), holding-duration process, exposure profile and the SAME cost model; drawn from the same 26 frozen windows

## Pre-committed rejection gates (point 9 — four separated classes)
- Integrity: any duplicate trade; any lookahead violation; cost arithmetic mismatch; missing/interpolated bar used; provenance tiers not retained in attribution
- Data/execution: exit-path snapshots not contiguous from 2026-07-16 to natural close; BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA (positions unresolved after deterministic extension); short instrument/venue/symbol-map/carry not resolved + feasible at run time; any post-2026-07-15 snapshot used to create a new entry; malformed/missing expected export on a holding session
- Economic: net return <= 0 after fully-net costs; non-positive net Sharpe; does NOT beat the matched fixed-seed random-entry null on a risk-adjusted basis; does NOT beat BTC buy-and-hold on a risk-adjusted basis
- Power warning: 88 actionable entries over 26 daily windows is a SHORT, low-power path; annualized figures are NON-CONCLUSIVE and every annualized metric MUST carry the warning; results are indicative only
- Held-out (point 8): decisive=False — LABELLED, NON-DECISIVE robustness diagnostic only

## Proposed lifecycle gates (not activated)
1. `C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW` — human reviews the (revised) frozen replay specification (token `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE`)
1. `C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW` — human reviews the frozen exit-path snapshot dataset + manifest AND the resolved short instrument/venue/symbol-map/carry feasibility (token `HUMAN_DECISION_C22_FORWARD_PRICE_DATA_ACCEPT_OR_REJECT`)
1. `C22_DRY_RUN_READY_FOR_HUMAN_REVIEW` — human reviews the no-PnL dry-run wiring (entry/exit/no-lookahead/ordering) (token `HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT`)
1. `C22_FEE_HONEST_REPLAY_READY_FOR_HUMAN_AUTHORIZATION` — human authorizes the ONE fee-honest replay run (token `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT`)
1. `C22_REPLAY_RESULTS_READY_FOR_HUMAN_REVIEW` — human reviews the frozen results + accept/reject decision (token `HUMAN_DECISION_C22_REPLAY_RESULTS_ACCEPT_OR_REJECT`)

## Recommendation

**READY_FOR_SECOND_HUMAN_REVIEW_OF_C22_REPLAY_SPEC**
