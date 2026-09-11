# C22 — B3 Stage Two Governance Closure (20260911T130440Z)

Human decisions of 2026-09-11 recorded by the session. No performance information exists or was consulted.

## Decision 1 — decisive venue policy: **HOME_VENUE_ONLY**

- Cross-venue substitution to rescue signals: False · made before any performance calculation: True
- MORPHO: Stage One existence PASS_PRESERVED; Stage Two ['PENDING_VENUE_POLICY', 'PENDING_VENUE_POLICY']; decisive execution status **EXCLUDED_VENUE_POLICY** for signals ['2026-07-01', '2026-07-06']; not classified as instrument-nonexistent; evidence kept.
- TEL: Stage One FAIL_WRONG_INSTRUMENT_TYPE preserved; alternative venues searched: False.
- Future cross-venue testing: separately named sensitivity experiment with one predetermined venue-selection hierarchy across the entire cohort; never mixed into the decisive C22 V2 replay

## Decision 2 — LEO final verdict: **PASS_HISTORICAL_SHORTABILITY**

- General funding-market inference accepted alone: False
- Reason: official pair-specific statistics: short position size on tLEOUSD > 0 at every observed minute of every required date, and funding credits used on the exact pair > 0 throughout: short positions were actually present/possible on the pair in the required period
- Checks: `{"daily_timeframe_series_available": false, "funding_currency": "fLEO", "general_borrow_market_inference_used_as_decisive": false, "pair": "tLEOUSD", "pair_funding_credits_used_1d_on_required_dates": {"2026-07-15": null, "2026-07-16": null}, "pair_funding_credits_used_1m_daily_summary": {"2026-07-15": {"max": 10248.90057714, "min": 9659.74202222, "points": 1440}, "2026-07-16": {"max": 10495.4137087, "min": 9659.74202222, "points": 1440}}, "pair_short_position_size_1d_on_required_dates": {"2026-07-15": null, "2026-07-16": null}, "pair_short_position_size_1m_daily_summary": {"2026-07-15": {"max": 120054.91760515, "min": 109697.25096753, "points": 1440}, "2026-07-16": {"max": 110558.43681077, "min": 110119.25096753, "points": 1440}}, "present_day_margin_flag_used": false, "required_dates": ["2026-07-15", "2026-07-16"]}`

| supplemental source | params | sha256 | retrieved |
|---|---|---|---|
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tLEOUSD:short/hist | {"end": "2026-07-19", "key": "pos.size:1d:tLEOUSD:short", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:04:40+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tLEOUSD:long/hist | {"end": "2026-07-19", "key": "pos.size:1d:tLEOUSD:long", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:04:41+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/credits.size.sym:1d:fLEO:tLEOUSD/hist | {"end": "2026-07-19", "key": "credits.size.sym:1d:fLEO:tLEOUSD", "limit": 100, "sort": 1, "start": "2026-07-12"} | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | 2026-09-11T13:04:41+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/pos.size:1m:tLEOUSD:short/hist | {"end_exclusive": "2026-07-17", "key": "pos.size:1m:tLEOUSD:short", "limit": 10000, "sort": 1, "start": "2026-07-15"} | `e68cdaf4853dbfbfc659038b9bc14c73731d7b00e1f82b8d3c62c9b08f9a7743` | 2026-09-11T13:04:41+00:00 |
| https://api-pub.bitfinex.com/v2/stats1/credits.size.sym:1m:fLEO:tLEOUSD/hist | {"end_exclusive": "2026-07-17", "key": "credits.size.sym:1m:fLEO:tLEOUSD", "limit": 10000, "sort": 1, "start": "2026-07-15"} | `c6d58567e2300210efff5c97a5f3bb0ffa292df07a68495ea023f2ba5e6aa245` | 2026-09-11T13:04:42+00:00 |

## Final Stage Two funnel

| item | value |
|---|---|
| frozen_short_signals | 75 |
| stage1_survivors | 74 |
| stage2_pass_before_governance | 72 |
| excluded_venue_policy | 2 |
| leo_final | PASS_HISTORICAL_SHORTABILITY |
| eliminated_stage_one_preserved | 1 |
| unresolved | 0 |
| decisive_executable_short_signals_after_stage_two | 72 |
| decisive_executable_assets | ['BINANCE:AAVEUSDT', 'BINANCE:CRVUSDT', 'BINANCE:IMXUSDT', 'BINANCE:INJUSDT', 'BINANCE:LINKUSDT', 'BINANCE:PENDLEUSDT', 'BINANCE:QNTUSDT', 'BINANCE:SOLUSDT', 'BINANCE:SUNUSDT', 'BINANCE:TIAUSDT', 'BINANCE:TRXUSDT', 'BINANCE:VIRTUALUSDT', 'BINANCE:ZECUSDT', 'BITFINEX:LEOUSD', 'BYBIT:GRAMUSDT', 'GATE:ASTERUSDT', 'GATE:GTUSDT', 'KRAKEN:KASUSD', 'KRAKEN:SPXUSD', 'OKX:OKBUSDT'] |
| admitted_for_fee_honest_replay | 0 |

## Referenced sealed evidence

- stage1_report_run: `20260910T225620Z`
- stage1_report_sha256: `95b135c3356809db971881f1ea91ed0accc7d7d595b986fca1728fad67b726d8`
- stage2_report_run: `20260910T231336Z`
- stage2_report_sha256: `03fbc61783152c27026a54cf588c7bdc80b69ea260dc43640e9bd28dc9605e3f`
- v2_artifact_sha256: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`

- Historical evidence modified: False · sealed reports rewritten: False · admission state changed: False
- Stage Three definition: frozen B3 ACQUISITION_ORDER step 4_historical_ohlc under batch HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE

