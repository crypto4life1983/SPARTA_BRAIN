# C22 — B3 Stage One Report: Historical Instrument-Existence Evidence

Run: `20260910T225620Z` (sealed) · Report sha256 `95b135c3356809db971881f1ea91ed0accc7d7d595b986fca1728fad67b726d8`
Full machine report: `reports/c22_gc_b3_stage1/c22_b3_stage1_instrument_existence_20260910T225620Z.{json,md}`
Tool: `tools/c22_b3_stage1_instrument_existence_once.py` (commit `3efaa5ca`) · Tests: `tests/test_c22_b3_stage1_instrument_existence.py`

Authorization scope honoured: READ-ONLY historical instrument-existence evidence for the frozen V2 short cohort. This is **not** an ACCEPT or HOLD of C22, not Stage Two, not funding/fee/slippage acquisition, not trading. No credentials, no accounts, no strategy rule, no V2 file, no frozen export was touched. C22 performance was not computed.

A superseded first run (`20260910T225126Z`, same evidence, earlier verdict labels) is retained on disk because raw evidence is never deleted; the sealed run above is the one of record.

## Stage boundary

Stage One answers only: *did a correctly identified candidate execution instrument exist, at the Signum-named venue, on the required historical date?* It proves nothing about shortability, funding, borrow, fills, liquidity, spread, fees or slippage. Same-venue candidates only (B3: no cross-venue substitution without a human venue selection).

## A. Required short assets (22) and B. frozen V2 signal dates

| C22 asset | Risk class | Short signals | Decision dates |
|---|---|---|---|
| BINANCE:AAVEUSDT | STANDARD | 1 | 06-26 |
| BINANCE:CRVUSDT | STANDARD | 5 | 07-05 → 07-14 |
| BINANCE:IMXUSDT | STANDARD | 1 | 07-06 |
| BINANCE:INJUSDT | STANDARD | 3 | 07-11 → 07-15 |
| BINANCE:LINKUSDT | STANDARD | 1 | 07-15 |
| BINANCE:PENDLEUSDT | STANDARD | 5 | 07-03 → 07-08 |
| BINANCE:QNTUSDT | STANDARD | 5 | 06-20 → 07-11 |
| BINANCE:SOLUSDT | STANDARD | 1 | 07-02 |
| BINANCE:SUNUSDT | STANDARD | 2 | 07-06 → 07-07 |
| BINANCE:TIAUSDT | STANDARD | 6 | 06-28 → 07-08 |
| BINANCE:TRXUSDT | STANDARD | 10 | 07-06 → 07-15 |
| BINANCE:VIRTUALUSDT | MAPPING_SENSITIVE | 1 | 07-12 |
| BINANCE:ZECUSDT | STANDARD | 3 | 07-08 → 07-10 |
| BITFINEX:LEOUSD | VENUE_LOCKED_NATIVE | 1 | 07-15 |
| BYBIT:GRAMUSDT | MAPPING_SENSITIVE | 4 | 07-05 → 07-08 |
| BYBIT:TELUSDT | MAPPING_SENSITIVE | 1 | 07-09 |
| COINBASE:MORPHOUSD | STANDARD | 2 | 07-01 → 07-06 |
| GATE:ASTERUSDT | MAPPING_SENSITIVE | 3 | 06-21 → 07-05 |
| GATE:GTUSDT | VENUE_LOCKED_NATIVE | 12 | 07-04 → 07-15 |
| KRAKEN:KASUSD | STANDARD | 2 | 07-05 → 07-06 |
| KRAKEN:SPXUSD | HIGH_COLLISION_RISK | 5 | 06-28 → 07-02 |
| OKX:OKBUSDT | VENUE_LOCKED_NATIVE | 1 | 06-23 |

All dates 2026. Existence was required on or before the **decision date** (stricter than the fill date); both fill-date conventions (calendar D+1 and next weekday) are recorded per signal and checked against delisting.

## C. Candidate venues/instruments inspected, D. identity evidence, E. existence evidence

| Asset | Candidate (venue) | Type | Identity evidence | Existence evidence | Existence date |
|---|---|---|---|---|---|
| 13 Binance names | `<BASE>USDT` (Binance USD-M) | linear perpetual | official `baseAsset`/`quoteAsset` in `fapi/v1/exchangeInfo` | `onboardDate` (launch timestamp) | AAVE 2020-10-16, CRV 2020-09-01, IMX 2022-02-10, INJ 2022-08-16, LINK 2020-01-17, PENDLE 2023-07-28, QNT 2022-10-18, SOL 2020-09-14, SUN 2024-08-22, TIA 2023-10-31, TRX 2020-01-15, VIRTUAL 2024-12-10, ZEC 2020-02-05 |
| BYBIT:GRAMUSDT | `GRAMUSDT` linear (Bybit) | linear perpetual | official `baseCoin`/`quoteCoin` | `launchTime` | 2026-06-22 09:46 UTC |
| BYBIT:GRAMUSDT | `GRAMUSDT` spot (Bybit) | spot, `marginTrading=utaOnly` (present-day) | official `baseCoin` | official daily klines | seen since ≤ 2026-05-27 |
| BYBIT:TELUSDT | `TELUSDT` linear (Bybit) | — | official API: `symbol invalid` | — | **no such perpetual** |
| BYBIT:TELUSDT | `TELUSDT` spot (Bybit) | spot, `marginTrading=none` | official `baseCoin` | official daily klines | seen since ≤ 2026-06-01 (wrong type for a short) |
| OKX:OKBUSDT | `OKB-USDT-SWAP` (OKX) | linear swap | official `ctValCcy`/`instFamily` | `listTime` | 2025-09-04 |
| OKX:OKBUSDT | `OKB-USDT` MARGIN (OKX) | spot margin | official `baseCcy` | `listTime` | 2021-01-29 |
| GATE:GTUSDT | `GT_USDT` (Gate futures) | linear perpetual | official contract `name` | `create_time` | 2022-03-20 |
| GATE:ASTERUSDT | `ASTER_USDT` (Gate futures) | linear perpetual | official contract `name` | `create_time` | 2025-09-19 |
| COINBASE:MORPHOUSD | `MORPHO-USD` (Coinbase Exchange) | spot, `margin_enabled=false` | official `base_currency` | — | wrong type for a short |
| COINBASE:MORPHOUSD | `MORPHO-PERP` (Coinbase International) | perpetual (USDC) | official `base_asset_name` | official daily candles | seen since ≤ 2026-06-01 |
| KRAKEN:KASUSD | `PF_KASUSD` (Kraken Futures) | flexible futures | official `base`, `category=Layer 1`, `tradfi=false` | `openingDate` + official daily chart | 2024-01-09 |
| KRAKEN:KASUSD | `KASUSD` spot (Kraken) | spot margin (`leverage_sell` present-day) | official `base` | none dated | non-decisive |
| KRAKEN:SPXUSD | `PF_SPXUSD` (Kraken Futures) | flexible futures | official `base=SPX`, **`category=Meme`, `tradfi=false`** resolves the S&P-500 ticker collision | `openingDate` + official daily chart | 2024-12-19 |
| KRAKEN:SPXUSD | `SPXUSD` spot (Kraken) | spot margin | collision **unresolved** (AssetPairs carries no classification) | none dated | non-decisive |
| BITFINEX:LEOUSD | `tLEOUSD` (Bitfinex) | spot pair, in present-day margin list | venue-native token, pair naming | official daily candles | seen since ≤ 2026-06-01 |

Coinbase `new_at` was not used. Present-day margin/leverage flags are recorded as observations only and never contribute to a PASS.

## F. Per-date verdicts

Every one of the 75 short signals received exactly one verdict per candidate instrument and one signal-level verdict (PASS if any correctly-identified, correctly-typed candidate has dated existence evidence on or before the decision date; otherwise the least-bad non-PASS verdict). No launch date fell inside a signal range, so no asset split into pass/fail by date; the date-aware logic is exercised by tests (fixture launch 2026-07-05 → June signals FAIL, July signals PASS).

| Verdict | Signals |
|---|---|
| PASS_HISTORICAL_EXISTENCE | 74 |
| FAIL_WRONG_INSTRUMENT_TYPE | 1 (BYBIT:TELUSDT 2026-07-09) |
| UNRESOLVED_* | 0 |

## G. Sources used and hashes (sealed run)

All raw responses under `data/c22_short_instrument_evidence/raw/<venue>/<asset>/` with `.sha256` and `.meta.json` (endpoint, query, UTC time, HTTP status). Run manifest: `data/c22_short_instrument_evidence/manifests/stage1_run_manifest__20260910T225620Z.json`. Normalized registry records (one per asset, run-independent hash): `data/c22_short_instrument_evidence/registry/`.

| Raw file | sha256 (prefix) |
|---|---|
| BINANCE `fapi/v1/exchangeInfo` (shared) | `6fc9697a75997d71` |
| BITFINEX LEO daily candles | `b06f7652a2de7903` |
| BITFINEX margin pair list (present-day, non-decisive) | `96880a5c0d66a8ca` |
| BYBIT GRAM linear instruments-info | `b64fc89fcfb8bbf9` |
| BYBIT GRAM spot daily kline | `8245aa2adc0e45e1` |
| BYBIT GRAM spot instruments-info | `5954e2e4ae119bf3` |
| BYBIT TEL linear instruments-info | `e2eb545d8e32bfba` |
| BYBIT TEL spot daily kline | `453cf60ed7208e05` |
| BYBIT TEL spot instruments-info | `75196a09c49464a3` |
| COINBASE MORPHO exchange product | `d17408f764b1119a` |
| COINBASE MORPHO INTX daily candles | `751c148574beb5ca` |
| COINBASE MORPHO INTX instrument | `0ffa7d6de93d080a` |
| GATE ASTER futures contract | `0dc8d634d770d9e6` |
| GATE GT futures contract | `4c9354a1929b92fc` |
| KRAKEN KAS futures daily chart | `1d81b4bf353223f4` |
| KRAKEN KAS spot AssetPairs | `9bc87697ebdca3dc` |
| KRAKEN SPX futures daily chart | `bc22616532b4da0e` |
| KRAKEN SPX spot AssetPairs | `8c200327dd0c7998` |
| KRAKEN Futures instruments (shared) | `2835e75a89870403` |
| OKX OKB MARGIN instruments | `b5e6d3a2c8f22858` |
| OKX OKB SWAP instruments | `9f6e49cf2b58d07c` |

Full 64-hex hashes are in the machine report and sidecars.

## H / I / J. Counts

| | Signals |
|---|---|
| Surviving Stage One | **74** of 75 |
| Eliminated | **1** |
| Unresolved | **0** |

## K. Exact reasons for every elimination

- **BYBIT:TELUSDT, 2026-07-09 (BEAR_SHORT):** Bybit's official instruments endpoint returns `symbol invalid` for a `TELUSDT` linear perpetual (`FAIL_NO_SUCH_INSTRUMENT_AT_VENUE`), and the Bybit spot pair `TELUSDT` reports `marginTrading=none` (`FAIL_WRONG_INSTRUMENT_TYPE`). No same-venue instrument can express the short. Cross-venue alternatives were not inspected (B3: human venue selection required).

## L. Assets requiring a second authoritative source before Stage Two

| Asset | Why |
|---|---|
| BITFINEX:LEOUSD | existence rests on official candles (no launch timestamp); venue-native token; margin enablement date unproven |
| COINBASE:MORPHOUSD | execution platform (Coinbase International, USDC perp) differs from the Signum-named Coinbase Exchange spot product; existence rests on official candles; jurisdiction/access is a Stage Two question |
| BYBIT:GRAMUSDT | mapping-sensitive; launch 2026-06-22 is only 13 days before the first signal, spot-kline evidence corroborates |
| KRAKEN:SPXUSD | collision resolved only via Kraken Futures' own classification (`category=Meme`, `tradfi=false`); spot candidate remains collision-unresolved |
| BINANCE:VIRTUALUSDT, GATE:ASTERUSDT, BYBIT:TELUSDT | mapping-sensitive per B2 |
| GATE:GTUSDT, OKX:OKBUSDT | venue-native tokens per B2 (identity is strong at the native venue; flagged for completeness) |

## M. Is Stage One complete enough to request Stage Two authorization?

**Yes, with the caveats in L.** 74 of 75 short signals have a correctly identified candidate instrument with first-party dated existence evidence on or before the decision date; 0 are unresolved; 1 is eliminated with an explicit, sourced reason. Stage Two (shortability mechanism, funding/borrow availability and rates on every holding date, fees, tick/lot/minimums, liquidity/spread) has **not** been started and requires its own authorization. The fee-honest precondition shell still reports `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED` with 0 of 26 instruments admitted, as it must: Stage One produces a run manifest, not an admission manifest.

## Tests and commits

- Full C22 suite: **273 passed** (264 before Stage One + 9 new).
- Commit `3efaa5ca` — tool, tests, both run reports. Frozen surfaces verified unchanged (`git diff --diff-filter=M` against `5d5a3575` on the C22 modules and Phase A/B reports is empty; V2 artifact sha `b6a28a48…`).
