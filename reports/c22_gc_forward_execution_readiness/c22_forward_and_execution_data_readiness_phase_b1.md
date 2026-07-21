# C22 Forward Exit-Data & Execution-Data Readiness — Phase B1

Contract + inventory + planning only. Admits no data, selects no instrument, approves
no cost base case, runs no replay, issues no token, activates no lifecycle gate.

- Bound accepted replay-spec SHA-256: `9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867`
- Forward-data contract SHA-256: `f3a1029ae705bd67e4eb8cdebff144f949c2d0ff6a62f89344738fbec65e731c`
- Execution-data contract SHA-256: `1a207918c7146182ab41d888d1daa14cf85fbb592d97295795701932bccf713f`
- Recommendation: **READY_FOR_HUMAN_REVIEW_OF_C22_FORWARD_AND_EXECUTION_DATA_CONTRACT**

## A. Forward exit-only data contract
- Entry cutoff **2026-07-15**; first exit-only date **2026-07-16**; no new entries after cutoff; post-cutoff files marked **EXIT_ONLY**
- Initial review **30 cal days** (2026-07-16 → 2026-08-14); deterministic **15-day** extensions (first 2026-08-15 → 2026-08-29)
- Insufficient coverage → **BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA**
- Five-case distinction: absent_from_valid_top50→OUT_OF_RADAR, entire_export_missing_or_malformed→FAIL_CLOSED_HALT, no_executable_price→FAIL_CLOSED_HALT, permanent_delisting_with_real_price→DELISTED_EXIT_DIAGNOSTIC, temporary_suspension→HOLD_AND_FLAG

## Local forward inventory (read-only; nothing admitted)
- Cutoff 2026-07-15; initial horizon 2026-07-16 → 2026-08-14 (22 expected weekday sessions)
- 2026-07-16: gc_crypto_trendradar_daily_20260716.json (rows=50, valid=True) → **VALID_EXIT_ONLY_CANDIDATE**
- 2026-07-17: gc_crypto_trendradar_daily_20260717.json (rows=50, valid=True) → **VALID_EXIT_ONLY_CANDIDATE**
- 2026-07-20: gc_crypto_trendradar_daily_20260720.json (rows=50, valid=True) → **VALID_EXIT_ONLY_CANDIDATE**
- Present valid EXIT_ONLY candidate dates: 2026-07-16, 2026-07-17, 2026-07-20
- Missing expected sessions through latest collected: none
- Missing expected sessions across full initial 30-day horizon: 19 (2026-07-21, 2026-07-22, 2026-07-23, 2026-07-24, 2026-07-27 …)
- Forward-data coverage verdict: **BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA**

## B. Execution-data & short-instrument feasibility
- Short instrument: **UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION** (selected=False)
- Option 1 (perp) requirements: explicit_venue, exact_contract_symbol, quote_asset, settlement_asset, instrument_start_date, historical_ohlc_source, historical_funding_rate_source, funding_timestamps_and_payment_intervals, trading_fee_schedule, tick_size, lot_size, symbol_mapping_to_gc_signal_asset, delisting_and_contract_migration_history, availability_on_every_signal_and_holding_date
- Option 2 (spot-margin) requirements: explicit_venue, spot_symbol, margin_mode, borrowable_asset, historical_borrow_availability, historical_borrow_rate_source, borrow_charging_interval, trading_fee_schedule, symbol_mapping, suspension_and_delisting_history, availability_on_every_signal_and_holding_date
- Prohibitions: silently_using_spot_ohlc_for_perpetual_fills; silently_using_perpetual_ohlc_for_spot_margin_fills; assuming_borrow_availability; assuming_zero_funding; assuming_zero_basis; substituting_a_currently_available_instrument_for_one_that_did_not_exist_historically
- Basis review required: True (adjustment selected=False); fields: signal_price, execution_reference_price, absolute_difference, percentage_basis, timestamp_difference, symbol_map_confidence, approved_adjustment_rule_if_any
- Cost components: entry_exchange_fee, exit_exchange_fee, entry_half_spread, exit_half_spread, entry_slippage, exit_slippage, funding_or_borrow_cost, exceptional_exit_cost, basis_adjustment_cost_if_applicable
- 37 bps: **SENSITIVITY_CASE_NOT_BASE_CASE** (base case=False); result levels: gross, transaction_cost_only_net, fully_net_after_funding_or_borrow
- Liquidity evidence: daily_notional_volume, order_size_as_pct_of_volume, spread, minimum_order_size, lot_size, price_increment, instrument_availability

## Proposed lifecycle gates (not activated)
1. `C22_FORWARD_EXIT_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW` — human reviews the forward exit-only data contract (token `HUMAN_DECISION_C22_FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE`)
1. `C22_EXECUTION_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW` — human reviews the execution-data / short-feasibility contract (token `HUMAN_DECISION_C22_EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE`)
1. `C22_EXIT_ONLY_DATASET_READY_FOR_ADMISSION_REVIEW` — human reviews the frozen exit-only snapshot dataset for admission (token `HUMAN_DECISION_C22_EXIT_ONLY_DATASET_ADMIT_OR_REJECT`)
1. `C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION` — human selects perp vs spot-margin with full feasibility evidence (token `HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT`)
1. `C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW` — human reviews/freezes the component-level cost base case (token `HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE`)
1. `C22_DRY_RUN_SPEC_READY_FOR_HUMAN_REVIEW` — human reviews the no-PnL dry-run spec (only after all above accepted) (token `HUMAN_DECISION_C22_DRY_RUN_SPEC_ACCEPT_OR_REVISE`)

## Recommendation

**READY_FOR_HUMAN_REVIEW_OF_C22_FORWARD_AND_EXECUTION_DATA_CONTRACT**
