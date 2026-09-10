# C22 — B3 Stage Two Report: Historical Shortability Evidence

Run of record: `20260910T231336Z` · report sha256 `03fbc61783152c27026a54cf588c7bdc80b69ea260dc43640e9bd28dc9605e3f`
Machine report: `reports/c22_gc_b3_stage2/c22_b3_stage2_historical_shortability_20260910T231336Z.{json,md}`
Tool: `tools/c22_b3_stage2_historical_shortability_once.py` · Tests: `tests/test_c22_b3_stage2_historical_shortability.py` · Commit `9750f9d7`
Stage One input of record: run `20260910T225620Z`, sha `95b135c3…` (SHA-verified before use).

Scope honoured: READ-ONLY historical research. No performance, no cost arithmetic, no paper/live, no credentials, no orders, no strategy change, no Stage Three. V2, frozen exports, Phase A, B1, B2, B3 untouched. Admission state unchanged (0 of 26).

Primary question answered per signal date: *could the frozen C22 short signal actually have been expressed as a NEW short position using the candidate instrument on the required historical execution date?*

## N. Execution-evidence funnel

| Stage | Signals |
|---|---|
| A. Frozen V2 short signals | **75** (72 BEAR_SHORT + 3 HEDGE_SHORT, 22 assets) |
| B. Stage One survivors (dated instrument existence) | **74** |
| E. Stage Two PASS_HISTORICAL_SHORTABILITY | **72** |
| H. PENDING_VENUE_POLICY | **2** (MORPHO) |
| F. Stage Two FAIL | **0** |
| G. Stage Two UNRESOLVED | **0** |
| Stage One elimination preserved (TEL) | **1** |
| Admitted for fee-honest replay | **0** (no human admission token; shell still `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED`, 0/26) |

## D. Execution path used by passing signals

| Path | Signals | Instruments |
|---|---|---|
| DERIVATIVE_PERPETUAL_OR_FUTURES (home venue) | 71 | 13 Binance USD-M perps; Bybit GRAMUSDT linear; OKX OKB-USDT-SWAP; Gate GT_USDT, ASTER_USDT; Kraken Futures PF_KASUSD, PF_SPXUSD |
| SPOT_MARGIN_BORROW (home venue) | 1 | Bitfinex tLEOUSD via the fLEO funding (borrow) market |

Secondary spot-margin candidates (Bybit GRAM spot, OKX OKB-USDT margin) are recorded as UNRESOLVED_HISTORICAL_MARGIN/BORROW_STATE because those venues expose no first-party *historical* margin or borrow state; they are not needed because the derivative path passes. Kraken spot margin candidates were not evaluated (Stage One left them present-day-only).

## C. Per-signal verdicts (summary; full per-date table in the machine report)

| Asset | Signals | S2 PASS | Path | Evidence on each decision + fill date |
|---|---|---|---|---|
| BINANCE:AAVEUSDT | 1 | 1 | perp | daily kline volume > 0 on D, D+1, next weekday; 5 funding settlements in window |
| BINANCE:CRVUSDT | 5 | 5 | perp | volume on all dates; 3 settlements per window |
| BINANCE:IMXUSDT | 1 | 1 | perp | idem |
| BINANCE:INJUSDT | 3 | 3 | perp | idem (4 settlements on the weekend-spanning window) |
| BINANCE:LINKUSDT | 1 | 1 | perp | idem |
| BINANCE:PENDLEUSDT | 5 | 5 | perp | idem |
| BINANCE:QNTUSDT | 5 | 5 | perp | idem |
| BINANCE:SOLUSDT | 1 | 1 | perp | idem |
| BINANCE:SUNUSDT | 2 | 2 | perp | idem |
| BINANCE:TIAUSDT | 6 | 6 | perp | idem |
| BINANCE:TRXUSDT | 10 | 10 | perp | idem |
| BINANCE:VIRTUALUSDT | 1 | 1 | perp | idem |
| BINANCE:ZECUSDT | 3 | 3 | perp | idem |
| BYBIT:GRAMUSDT | 4 | 4 | perp | linear kline volume on dates (activity from launch 06-22); 3 settlements per window |
| OKX:OKBUSDT | 1 | 1 | swap | history-candles volume on dates; 3 settlements in window |
| GATE:GTUSDT | 12 | 12 | perp | candlestick volume on dates; 8h settlements in window |
| GATE:ASTERUSDT | 3 | 3 | perp | candlestick volume on dates; 4h settlements in window |
| KRAKEN:KASUSD | 2 | 2 | futures | daily chart volume on dates; hourly funding records in window |
| KRAKEN:SPXUSD | 5 | 5 | futures | idem (identity: Kraken Futures `category=Meme`, `tradfi=false`) |
| BITFINEX:LEOUSD | 1 | 1 | spot margin | see J |
| COINBASE:MORPHOUSD | 2 | 0 | — | PENDING_VENUE_POLICY, see I |
| BYBIT:TELUSDT | 1 | 0 | — | NOT_EVALUATED (Stage One elimination preserved), see K |

Derivative PASS conditions applied on every date: launched ≤ decision date (Stage One timestamp); not expired/delisted through the fill dates; official daily candle with volume > 0 on the decision date and on both fill conventions (calendar D+1 and next weekday); at least one official funding settlement inside [decision date, last fill date + 1]; short exposure supported by the instrument type (linear perpetual / flexible futures permit sell-to-open by design). Continuous tradability was **not** assumed from present-day status: the per-date candle and funding records are the evidence.

## I. Exact treatment of MORPHO

- Stage One: `historical_existence = PASS` via official Coinbase International daily candles for `MORPHO-PERP`; the Signum-named product `COINBASE:MORPHO-USD` is a spot pair with `margin_enabled=false` and cannot express a short.
- Venue policy check against the frozen B3 contract: every asset carries `no_cross_venue_substitution = True` (`c22_historical_evidence_acquisition_plan_contract.py:235,305,398`) and venue-locked/substitution cases require the human decision `approve_home_venue_implementation_or_explicit_cross_venue_approval` (`:188`). Coinbase International Exchange is a distinct platform from Coinbase Exchange (different product, USDC settlement, separate access regime). **No explicit cross-venue approval is recorded.**
- Stage Two verdict for both MORPHO signals (07-01, 07-06): **PENDING_VENUE_POLICY**. The evidence-only result that *would* apply if policy allowed it is preserved in `checks`: launched ≤ D, activity on all dates, but funding settlements were **not** collected pending policy, so it would currently read UNRESOLVED_MARKET_STATE, not PASS. MORPHO is not admitted and was not decided on P&L.

## J. Exact treatment of LEO

- Stage One candles proved only that `tLEOUSD` existed. Present-day membership in Bitfinex's margin pair list was recorded as a non-decisive observation.
- Stage Two collected official Bitfinex **funding-market** evidence for the base currency (`fLEO`): `funding/stats/fLEO/hist` (4 pages, hourly) and daily funding-market candles (`fLEO:a30:p2:p30`). On the required dates: funding amount used 9,968.72 LEO (2026-07-15) and 10,093.23 LEO (2026-07-16); funding-market volume 733.49 on 2026-07-16 (no daily aggregate row for 07-15). Pair candles show trading volume on both dates.
- Reasoning: on Bitfinex, a margin short of LEO/USD is executed by borrowing LEO from the fLEO funding market; first-party evidence that LEO was being borrowed on those dates establishes that the borrow mechanism was operational and available. Verdict: **PASS_HISTORICAL_SHORTABILITY** on the spot-margin path.
- Caveat recorded in the verdict itself: the API does not expose margin-pair-enablement *history* directly; margin enablement is inferred from the active borrow market. LEO is listed under M as requiring a second authoritative source, and it remains **unadmitted** (no human admission token, no fee/tick/lot/liquidity evidence yet).

## K. TEL

Status **unchanged**: Stage One `FAIL_WRONG_INSTRUMENT_TYPE` (no Bybit linear perpetual exists for TELUSDT per the official API; Bybit spot `marginTrading=none`). Stage Two verdict `NOT_EVALUATED_STAGE_ONE_NOT_PASSED`. No alternative venue was searched. If governance later approves a venue-neutral rule, venue mapping reopens for the whole cohort under one deterministic rule, not for TEL alone.

## L. Historical evidence sources and hashes (run of record)

47 raw responses preserved under `data/c22_short_instrument_evidence/raw/<venue>/<asset>/` with `.sha256` and `.meta.json`; window 2026-06-15 → 2026-07-25; run manifest `data/c22_short_instrument_evidence/manifests/stage2_run_manifest__20260910T231336Z.json`.

| Source (official) | Files | sha256 prefixes |
|---|---|---|
| Binance `fapi/v1/klines` 1d + `fapi/v1/fundingRate`, 13 symbols | 26 | AAVE `a40272a6`/`71c73514`, CRV `841d29ce`/`e5a00358`, IMX `4b36fc1d`/`a816cfbe`, INJ `73add7ce`/`b3e02b60`, LINK `89681736`/`57f930b9`, PENDLE `e8b754ac`/`1394cc4a`, QNT `1266ee9d`/`ec8151a6`, SOL `611a9b44`/`ac6d7334`, SUN `9880b9da`/`c0972c11`, TIA `f5917a31`/`38d07576`, TRX `04e307aa`/`f4c7e2ea`, VIRTUAL `63d014b2`/`842d1bef`, ZEC `8b90bf3b`/`c29e556c` |
| Bybit `v5/market/kline` linear + `v5/market/funding/history` (GRAM) | 2 | `05e3d661`, `2e2ccb86` |
| OKX `market/history-candles` + `public/funding-rate-history` ×3 pages (OKB swap) | 4 | `a914daaf`, `cd1c14d2`, `1af72703`, `d76497c0` |
| Gate `futures/usdt/candlesticks` + `futures/usdt/funding_rate` (GT, ASTER) | 4 | GT `50f756f4`/`7c18abd8`, ASTER `186ca21b`/`aca13626` |
| Kraken Futures `charts/v1/trade/…/1d` + `historicalfundingrates` (KAS, SPX) | 4 | KAS `cac2e06b`/`fc9f7aff`, SPX `85607782`/`08109e69` |
| Bitfinex pair candles, `funding/stats/fLEO/hist` ×4, funding-market candles | 6 | `2c4f1786`, `f0b73b8e`, `9e5ee966`, `ec06186e`, `174436f1`, `19c394d0` |
| Coinbase International `instruments/MORPHO-PERP/candles` | 1 | `385538dd` |

Full 64-hex hashes are in the machine report. Registry records (22, one per asset, run-independent normalized hash) and candidate-admission artifacts (22) are listed in the run manifest.

On-disk history note: an aborted run (`20260910T231010Z`, stopped by the never-overwrite guard on a same-second pagination filename) and a first complete run (`20260910T231100Z`, identical verdicts, produced by the pre-commit code) are retained because raw evidence is never deleted. The run of record is `20260910T231336Z`, produced by the committed code.

## M. Instruments / signals requiring further evidence before admission

| Asset | Why |
|---|---|
| COINBASE:MORPHOUSD | venue-policy decision (home-venue vs explicit cross-venue approval); INTX funding history not collected pending that decision |
| BITFINEX:LEOUSD | margin enablement inferred from active borrow market; second authoritative source recommended; venue-native token |
| BYBIT:GRAMUSDT, GATE:ASTERUSDT, BINANCE:VIRTUALUSDT | mapping-sensitive per B2 (identity confirmed same-venue in Stage One) |
| KRAKEN:SPXUSD | high-collision identity, resolved by Kraken Futures classification only |
| GATE:GTUSDT, OKX:OKBUSDT | venue-native tokens (home-venue implementation decision per B3) |
| All 22 | later-stage evidence still absent: fee schedule, minimum quantity/notional, tick/lot constraints, liquidity/spread; funding/borrow **cost** arithmetic deferred by the cost boundary |

## Admission and cost boundary

- Stage Two wrote `data/c22_short_instrument_evidence/candidate_admission/<venue>__<asset>__candidate_admission__<run>.json` for all 22 assets with `admission_status = CANDIDATE_PENDING_HUMAN_ADMIT_NOT_ADMITTED` and the evidence categories each stage covers. It did **not** write any `manifests/<venue>__<asset>__evidence_manifest.json`; the fee-honest precondition shell still reports 0 of 26 instruments admitted.
- Funding and borrow records were preserved as *mechanism* evidence only. No rate was multiplied by any notional; no cost or P&L figure exists.

## O. Should Stage Three be requested?

**Yes, for the 72 PASS signals (20 assets), with two open governance items first:** (1) the MORPHO venue-policy decision, and (2) whether the LEO borrow-market inference is accepted as the historical short mechanism or a second source is required. Stage Three (fees, tick/lot/minimums, liquidity/spread, then funding/borrow cost arithmetic) was **not** started. TEL stays eliminated under the current mapping.

## Verification

- Full C22 suite after implementation: **280 passed, 0 failures** (273 before Stage Two + 7 new).
- Commits: `9750f9d7` (tool, tests, run reports); this report is committed separately.
- Frozen V2 artifact sha256 verified after the run: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8` (unchanged).
- Precondition shell after the run: `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED`, 0/26.
