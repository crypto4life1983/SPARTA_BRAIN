# C22 Historical Instrument Evidence Acquisition Plan — Phase B3

Source-feasibility review + acquisition plan. Fetches nothing, browses nothing, uses no
credentials, selects no instrument, creates no layout, issues no token.

- Bound SHAs: spec `9bf10af35352` · fwd `f3a1029ae705` · exe `1a207918c714` · b2 `a08a4cd58caa`
- Acquisition plan SHA-256: `c171fd73e7f1166c8e22946f1dfab728f14b738de6f1306c17860b52893dcc9f`
- Acquisition status: **NOT_AUTHORIZED** · Recommendation: **READY_FOR_HUMAN_REVIEW_OF_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN**

## Source hierarchy (best → worst; T5 never decisive)
1. T1_OFFICIAL_VENUE_HISTORICAL_FILES_OR_OFFICIAL_API_DOCS
2. T2_OFFICIAL_ARCHIVED_INSTRUMENT_AND_FEE_RECORDS
3. T3_REPUTABLE_INSTITUTIONAL_MARKET_DATA_SOURCE
4. T4_INDEPENDENTLY_ARCHIVED_PUBLIC_DATASET
5. T5_UNSUPPORTED_THIRD_PARTY_EXPLORATORY_ONLY_NOT_DECISIVE
- Decisive minimum tier: T3_REPUTABLE_INSTITUTIONAL_MARKET_DATA_SOURCE

## Feasibility matrix (22 assets)

| Asset | risk | difficulty | perp src | margin src | datasets | fail-closed |
|---|---|---|---|---|---|---|
| BINANCE:AAVEUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BINANCE:CRVUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BINANCE:IMXUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:INJUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:LINKUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BINANCE:PENDLEUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:QNTUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:SOLUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BINANCE:SUNUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:TIAUSDT | standard mapping | LOW | 3 cls | 3 cls | ~6 | BOTH |
| BINANCE:TRXUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BINANCE:VIRTUALUSDT | mapping sensitive | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| BINANCE:ZECUSDT | standard mapping | MEDIUM | 3 cls | 3 cls | ~8 | BOTH |
| BITFINEX:LEOUSD | venue locked native | POSSIBLY_UNAVAILABLE | 2 cls | 2 cls | ~11 | BOTH |
| BYBIT:GRAMUSDT | mapping sensitive | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| BYBIT:TELUSDT | mapping sensitive | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| COINBASE:MORPHOUSD | standard mapping | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| GATE:ASTERUSDT | mapping sensitive | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| GATE:GTUSDT | venue locked native | POSSIBLY_UNAVAILABLE | 2 cls | 2 cls | ~11 | BOTH |
| KRAKEN:KASUSD | standard mapping | HIGH | 3 cls | 3 cls | ~10 | BOTH |
| KRAKEN:SPXUSD | high collision risk | POSSIBLY_UNAVAILABLE | 2 cls | 2 cls | ~11 | BOTH |
| OKX:OKBUSDT | venue locked native | POSSIBLY_UNAVAILABLE | 2 cls | 2 cls | ~11 | BOTH |

## Acquisition groups (per-asset validation preserved; no cross-venue substitution)
- **ASSETS_WITH_NO_LOCAL_EVIDENCE** (16): BINANCE:IMXUSDT, BINANCE:INJUSDT, BINANCE:PENDLEUSDT, BINANCE:QNTUSDT, BINANCE:SUNUSDT, BINANCE:TIAUSDT, BINANCE:VIRTUALUSDT, BITFINEX:LEOUSD, BYBIT:GRAMUSDT, BYBIT:TELUSDT, COINBASE:MORPHOUSD, GATE:ASTERUSDT, GATE:GTUSDT, KRAKEN:KASUSD, KRAKEN:SPXUSD, OKX:OKBUSDT
- **ASSETS_WITH_PARTIAL_LOCAL_EVIDENCE** (6): BINANCE:AAVEUSDT, BINANCE:CRVUSDT, BINANCE:LINKUSDT, BINANCE:SOLUSDT, BINANCE:TRXUSDT, BINANCE:ZECUSDT
- **BINANCE_VENUE_GROUP** (13): BINANCE:AAVEUSDT, BINANCE:CRVUSDT, BINANCE:IMXUSDT, BINANCE:INJUSDT, BINANCE:LINKUSDT, BINANCE:PENDLEUSDT, BINANCE:QNTUSDT, BINANCE:SOLUSDT, BINANCE:SUNUSDT, BINANCE:TIAUSDT, BINANCE:TRXUSDT, BINANCE:VIRTUALUSDT, BINANCE:ZECUSDT
- **HIGH_COLLISION_IDENTIFIERS** (1): KRAKEN:SPXUSD
- **MAPPING_SENSITIVE_OR_NEWER_ASSETS** (4): BINANCE:VIRTUALUSDT, BYBIT:GRAMUSDT, BYBIT:TELUSDT, GATE:ASTERUSDT
- **VENUE_NATIVE_TOKENS** (3): BITFINEX:LEOUSD, GATE:GTUSDT, OKX:OKBUSDT

## Credential & safety
- Classes: PUBLIC_NO_AUTH, PUBLIC_API_WITH_RATE_LIMITS, AUTHENTICATED_READ_ONLY_API, PAID_VENDOR, UNAVAILABLE_OR_UNCLEAR
- Prohibited: trading_permissions, withdrawal_permissions, order_permissions, broker_or_exchange_account_linking, unrestricted_api_keys, secrets_committed_to_repository, credentials_in_reports_or_logs
- Authenticated read-only source = future human decision; no credentials created.

## Proposed local evidence layout (NOT created; under gitignored data/)
- Root: `data/c22_short_instrument_evidence`
  - borrow: `data/c22_short_instrument_evidence/borrow/<asset>/`
  - canonical_normalized_files: `data/c22_short_instrument_evidence/canonical/<venue>/<asset>/`
  - fees: `data/c22_short_instrument_evidence/fees/<venue>/`
  - funding: `data/c22_short_instrument_evidence/funding/<asset>/`
  - instrument_registry: `data/c22_short_instrument_evidence/registry/`
  - liquidity: `data/c22_short_instrument_evidence/liquidity/<asset>/`
  - manifests: `data/c22_short_instrument_evidence/manifests/`
  - ohlc: `data/c22_short_instrument_evidence/ohlc/<asset>/`
  - raw_source_files: `data/c22_short_instrument_evidence/raw/<venue>/<asset>/`
  - rejected_quarantine: `data/c22_short_instrument_evidence/_quarantine/<date>/`
  - symbol_mappings: `data/c22_short_instrument_evidence/mappings/`
  - validation_reports: `data/c22_short_instrument_evidence/validation/`
- Filename convention: <venue>__<asset>__<category>__<start>_<end>.<ext> ; dates ISO YYYY-MM-DD; every file paired with a .sha256 sidecar; manifests list per-file sha256 + coverage; NEVER overwrites

## Acquisition order (fail-close-early)
1. 1_historical_instrument_existence_registry — if the instrument/contract never existed over the signal+holding window -> asset fail-closed BEFORE any OHLC/funding acquisition
1. 2_symbol_and_venue_mapping — if signal symbol cannot be deterministically mapped (esp. SPX identity, venue-native tokens) -> fail-closed before further acquisition
1. 3_funding_or_borrow_availability — if neither perp funding nor spot-margin borrow existed historically -> asset fail-closed for BOTH implementations before OHLC/fees/liquidity
1. 4_historical_ohlc
1. 5_fee_tick_lot_minimum_rules
1. 6_liquidity_and_spread_evidence
1. 7_full_holding_period_coverage

## Forward-horizon handling
- No new entries after 2026-07-15; min acquisition start 2026-06-20; initial range end 2026-08-14; deterministic 15-day extensions; final exit end date known: False
- extend forward in 15-day increments; append-only; each increment adds files + updates the manifest; NEVER rewrites prior files or frozen entry dates

## Proposed authorization sequence (not activated)
1. `C22_INSTRUMENT_REGISTRY_FETCH_READY_FOR_HUMAN_AUTHORIZATION` — authorize fetching only the historical instrument-existence registry + listing/delisting timestamps (token `HUMAN_DECISION_C22_INSTRUMENT_REGISTRY_FETCH_AUTHORIZE`)
1. `C22_FUNDING_AND_BORROW_FETCH_READY_FOR_HUMAN_AUTHORIZATION` — authorize fetching historical funding (perp) and/or borrow availability+rate (token `HUMAN_DECISION_C22_FUNDING_AND_BORROW_FETCH_AUTHORIZE`)
1. `C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION` — authorize fetching execution-instrument historical OHLC (token `HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE`)
1. `C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION` — authorize fetching fee/tick/lot/minimum + liquidity/spread evidence (token `HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE`)
1. `C22_HISTORICAL_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW` — human reviews all acquired evidence for admission (token `HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT`)

## Recommendation

**READY_FOR_HUMAN_REVIEW_OF_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN**
