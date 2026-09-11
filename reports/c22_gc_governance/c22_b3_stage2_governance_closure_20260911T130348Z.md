# C22 — B3 Stage Two Governance Closure (20260911T130348Z)

Human decisions of 2026-09-11 recorded by the session. No performance information exists or was consulted.

## Decision 1 — decisive venue policy: **HOME_VENUE_ONLY**

- Cross-venue substitution to rescue signals: False · made before any performance calculation: True
- MORPHO: Stage One existence PASS_PRESERVED; Stage Two ['PENDING_VENUE_POLICY', 'PENDING_VENUE_POLICY']; decisive execution status **EXCLUDED_VENUE_POLICY** for signals ['2026-07-01', '2026-07-06']; not classified as instrument-nonexistent; evidence kept.
- TEL: Stage One FAIL_WRONG_INSTRUMENT_TYPE preserved; alternative venues searched: False.
- Future cross-venue testing: separately named sensitivity experiment with one predetermined venue-selection hierarchy across the entire cohort; never mixed into the decisive C22 V2 replay

## Decision 2 — LEO final verdict: **UNRESOLVED_HISTORICAL_MARGIN_STATE**

- General funding-market inference accepted alone: False
- Reason: no_pair_specific_short_position_size>0_on_2026-07-15,2026-07-16
- Checks: `{"funding_currency": "fLEO", "pair": "tLEOUSD", "required_dates": ["2026-07-15", "2026-07-16"], "short_position_size_1d_on_required_dates": {"2026-07-15": null, "2026-07-16": null}}`

| supplemental source | params | sha256 | retrieved |
|---|---|---|---|
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tLEOUSD:short/hist | {"end": "2026-07-19", "key": "pos.size:1d:tLEOUSD:short", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:03:48+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tLEOUSD:long/hist | {"end": "2026-07-19", "key": "pos.size:1d:tLEOUSD:long", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:03:49+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/credits.size.sym:1d:fLEO:tLEOUSD/hist | {"end": "2026-07-19", "key": "credits.size.sym:1d:fLEO:tLEOUSD", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:03:49+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1m:tLEOUSD:short/hist | {"end_exclusive": "2026-07-17", "key": "pos.size:1m:tLEOUSD:short", "limit": 10000, "sort": 1, "start": "2026-07-15"} | `e68cdaf4853dbfbfc659038b9bc14c73731d7b00e1f82b8d3c62c9b08f9a7743` | 2026-09-11T13:03:49+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/credits.size.sym:1m:fLEO:tLEOUSD/hist | {"end_exclusive": "2026-07-17", "key": "credits.size.sym:1m:fLEO:tLEOUSD", "limit": 10000, "sort": 1, "start": "2026-07-15"} | `c6d58567e2300210efff5c97a5f3bb0ffa292df07a68495ea023f2ba5e6aa245` | 2026-09-11T13:03:50+00:00 |

## Final Stage Two funnel

| item | value |
|---|---|
| frozen_short_signals | 75 |
| stage1_survivors | 74 |
| stage2_pass_before_governance | 72 |
| excluded_venue_policy | 2 |
| leo_final | UNRESOLVED_HISTORICAL_MARGIN_STATE |
| eliminated_stage_one_preserved | 1 |
| unresolved | 1 |
| decisive_executable_short_signals_after_stage_two | 71 |
| decisive_executable_assets | ['BINANCE:AAVEUSDT', 'BINANCE:CRVUSDT', 'BINANCE:IMXUSDT', 'BINANCE:INJUSDT', 'BINANCE:LINKUSDT', 'BINANCE:PENDLEUSDT', 'BINANCE:QNTUSDT', 'BINANCE:SOLUSDT', 'BINANCE:SUNUSDT', 'BINANCE:TIAUSDT', 'BINANCE:TRXUSDT', 'BINANCE:VIRTUALUSDT', 'BINANCE:ZECUSDT', 'BYBIT:GRAMUSDT', 'GATE:ASTERUSDT', 'GATE:GTUSDT', 'KRAKEN:KASUSD', 'KRAKEN:SPXUSD', 'OKX:OKBUSDT'] |
| admitted_for_fee_honest_replay | 0 |

## Referenced sealed evidence

- stage1_report_run: `20260910T225620Z`
- stage1_report_sha256: `95b135c3356809db971881f1ea91ed0accc7d7d595b986fca1728fad67b726d8`
- stage2_report_run: `20260910T231336Z`
- stage2_report_sha256: `03fbc61783152c27026a54cf588c7bdc80b69ea260dc43640e9bd28dc9605e3f`
- v2_artifact_sha256: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`

- Historical evidence modified: False · sealed reports rewritten: False · admission state changed: False
- Stage Three definition: frozen B3 ACQUISITION_ORDER step 4_historical_ohlc under batch HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE

