# C22 Short-Instrument Historical Evidence Request — Phase B2

Provider-neutral evidence request for the 22 short assets. Browses nothing, fetches
nothing, selects no instrument, approves no mapping/basis/cost, issues no token.

- Bound replay-spec SHA: `9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867`
- Bound forward-data / execution-data SHA: `f3a1029ae705bd67e4eb8cdebff144f949c2d0ff6a62f89344738fbec65e731c` / `1a207918c7146182ab41d888d1daa14cf85fbb592d97295795701932bccf713f`
- Evidence-request contract SHA-256: `a08a4cd58caa373cd5c9ec4f8c980a646105aa6c126fe269c33d2534e7108b40`
- Assets: **22** · BEAR_SHORT 72 · HEDGE_SHORT 3 · acquisition **NOT_AUTHORIZED**
- Recommendation: **READY_FOR_HUMAN_REVIEW_OF_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST**

## Identity-risk classes (retained)
- HIGH_COLLISION_RISK: KRAKEN:SPXUSD
- VENUE_LOCKED_NATIVE: GATE:GTUSDT, OKX:OKBUSDT, BITFINEX:LEOUSD
- MAPPING_SENSITIVE: BYBIT:GRAMUSDT, BYBIT:TELUSDT, GATE:ASTERUSDT, BINANCE:VIRTUALUSDT
- PARTIAL (Binance funding ends 2026-06-21, insufficient): BINANCE:AAVEUSDT, BINANCE:CRVUSDT, BINANCE:LINKUSDT, BINANCE:SOLUSDT, BINANCE:TRXUSDT, BINANCE:ZECUSDT
- Borrow evidence: **ABSENT_FOR_ALL_22**

## Coverage periods
- Entry evidence: 2026-06-20 → 2026-07-15
- Initial exit evidence: 2026-07-16 → 2026-08-14
- Later exit: deterministic 15-day increments; final exit end date known: False

## Evidence matrix (22 assets)

| Asset | risk | shorts (B/H) | first→last | perp | margin | funding | borrow | blocker |
|---|---|---|---|---|---|---|---|---|
| BINANCE:AAVEUSDT | standard mapping | 1/0 | 2026-06-26→2026-06-26 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:CRVUSDT | standard mapping | 5/0 | 2026-07-05→2026-07-14 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:IMXUSDT | standard mapping | 1/0 | 2026-07-06→2026-07-06 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:INJUSDT | standard mapping | 3/0 | 2026-07-11→2026-07-15 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:LINKUSDT | standard mapping | 1/0 | 2026-07-15→2026-07-15 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:PENDLEUSDT | standard mapping | 5/0 | 2026-07-03→2026-07-08 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:QNTUSDT | standard mapping | 5/0 | 2026-06-20→2026-07-11 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:SOLUSDT | standard mapping | 1/0 | 2026-07-02→2026-07-02 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:SUNUSDT | standard mapping | 2/0 | 2026-07-06→2026-07-07 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:TIAUSDT | standard mapping | 4/2 | 2026-06-28→2026-07-08 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:TRXUSDT | standard mapping | 10/0 | 2026-07-06→2026-07-15 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:VIRTUALUSDT | mapping sensitive | 1/0 | 2026-07-12→2026-07-12 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BINANCE:ZECUSDT | standard mapping | 3/0 | 2026-07-08→2026-07-10 | FAIL_CLOSED | FAIL_CLOSED | PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BITFINEX:LEOUSD | venue locked native | 1/0 | 2026-07-15→2026-07-15 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BYBIT:GRAMUSDT | mapping sensitive | 4/0 | 2026-07-05→2026-07-08 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| BYBIT:TELUSDT | mapping sensitive | 1/0 | 2026-07-09→2026-07-09 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| COINBASE:MORPHOUSD | standard mapping | 1/1 | 2026-07-01→2026-07-06 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| GATE:ASTERUSDT | mapping sensitive | 3/0 | 2026-06-21→2026-07-05 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| GATE:GTUSDT | venue locked native | 12/0 | 2026-07-04→2026-07-15 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| KRAKEN:KASUSD | standard mapping | 2/0 | 2026-07-05→2026-07-06 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| KRAKEN:SPXUSD | high collision risk | 5/0 | 2026-06-28→2026-07-02 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |
| OKX:OKBUSDT | venue locked native | 1/0 | 2026-06-23→2026-06-23 | FAIL_CLOSED | FAIL_CLOSED | ABSENT | ABSENT | no_admissible_historical_instrument_or_cost_evidence |

## Signal/execution basis alignment
- Status: **BASIS_ALIGNMENT_NOT_REVIEWED** (no adjustment selected)
- Fields: trend_radar_signal_price_source, execution_instrument_price_source, signal_timestamp, execution_timestamp, signal_price, execution_reference_price, absolute_basis, percentage_basis, symbol_map_confidence, approved_basis_adjustment_rule_if_later_needed

## Component-cost evidence
- Components: entry_trading_fee, exit_trading_fee, entry_half_spread, exit_half_spread, entry_slippage, exit_slippage, funding_or_borrow_cost, exceptional_exit_cost, basis_adjustment_cost_if_applicable
- 37_BPS_SENSITIVITY_CASE_NOT_BASE_CASE

## Proposed lifecycle gates (not activated)
1. `C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_READY_FOR_HUMAN_REVIEW` — human reviews this provider-neutral evidence request (token `HUMAN_DECISION_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_ACCEPT_OR_REVISE`)
1. `C22_HISTORICAL_INSTRUMENT_DATA_FETCH_READY_FOR_HUMAN_AUTHORIZATION` — human authorizes a specific provider-neutral acquisition (out of band) (token `HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_DATA_FETCH_AUTHORIZE`)
1. `C22_SHORT_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW` — human reviews acquired evidence for admission (token `HUMAN_DECISION_C22_SHORT_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT`)
1. `C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION` — human selects perp vs spot-margin per asset with full evidence (token `HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT`)

## Recommendation

**READY_FOR_HUMAN_REVIEW_OF_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST**
