# C22 — B3 Stage 4A: T2 Evidence Recovery Report

Date: 2026-09-11 · Sealed run `20260911T200048Z` · report sha256 `d77b17824e5edcf4a449a4c58abaf09efdd862286b37e3604ec4403eb24ea163`
Machine report: `reports/c22_gc_b3_stage4a/c22_b3_stage4a_t2_recovery_20260911T200048Z.{json,md}` · manifest `data/c22_short_instrument_evidence/manifests/stage4a_run_manifest__20260911T200048Z.json`
Tool `tools/c22_b3_stage4a_t2_recovery_once.py` · tests `tests/test_c22_b3_stage4a_t2_recovery.py` · commit `1afafbfe`
Supplemental to sealed Stage Four run `20260911T131902Z` (sha `6c7753208b05e928…`, verified unmodified). Stage Four requirements were not weakened. No assumption selected. No performance computed. Next B3 stage not started.

Source policy applied: only first-party official exchange pages and endpoints are decisive. Search engines located records only. 38 official records were re-fetched and preserved under `data/c22_short_instrument_evidence/official_records/<venue>/` with URL, title, publication/update date, retrieval UTC, quoted values and SHA-256: 26 as raw HTML; 12 Binance pages as rendered-text captures because Binance serves a script-only shell (HTTP 202, 2 KB) to direct fetches, labelled `RENDERED_TEXT_CAPTURE_NOT_RAW_HTML`. Conservative ordinary retail tier assumed throughout: VIP0 / non-VIP / lv1 / base tier, no maker rebate, no token discount, no promotion.

## Headline

**0 of 72 eligible signals are now fully satisfied from historical evidence. 72 still require at least one conservative assumption.** Recovery did move three items from unresolved to historically established, and it also surfaced two facts that make back-projection of today's API values provably wrong: the Bybit GRAM tick size changed on 2026-08-11, and Gate's official contract endpoint contradicts Gate's own dated fee schedule.

## 1–7. Per-instrument evidence grades (20 decisive instruments)

| Asset | Instrument | Applicable dates (2026) | S4 fee | **4A fee grade** | Reconstructed taker / maker | **4A tick** | **4A lot / min** |
|---|---|---|---|---|---|---|---|
| BINANCE AAVE, CRV, IMX, INJ, LINK, PENDLE, QNT, SOL, SUN, TIA, TRX, VIRTUAL, ZEC (13) | `<BASE>USDT` USD-M | 06-20 → 07-30 (per signal) | UNRESOLVED | **UNRESOLVED** | — | CURRENT_ONLY | CURRENT_ONLY |
| BYBIT:GRAMUSDT | GRAMUSDT | 07-05 → 07-09 | UNRESOLVED | **CURRENT_ONLY** (0.055 % / 0.02 % post-window dated) | — | **T2_HISTORICAL_CONSTRAINT_RECONSTRUCTED** (in-window tick 0.0001; today 0.001) | CURRENT_ONLY |
| OKX:OKBUSDT | OKB-USDT-SWAP | 06-23 → 06-24 | UNRESOLVED | **CURRENT_ONLY** (lv1 0.05 % / 0.02 %, updated 2026-08-26) | — | CURRENT_ONLY | CURRENT_ONLY |
| GATE:GTUSDT / GATE:ASTERUSDT | GT_USDT / ASTER_USDT | 06-21 → 07-23 | UNRESOLVED | **UNRESOLVED (conflict)** | — | UNRESOLVED | UNRESOLVED |
| KRAKEN:KASUSD / KRAKEN:SPXUSD | PF_KASUSD / PF_SPXUSD | 06-28 → 07-06 | UNRESOLVED | **T2_HISTORICAL_FEE_BRACKETED** | **0.0500 % / 0.0200 %** | CURRENT_ONLY | CURRENT_ONLY |
| BITFINEX:LEOUSD | tLEOUSD | 07-15 → 07-20 | UNRESOLVED | **T2_HISTORICAL_FEE_BRACKETED** | **0 % / 0 %** (trading fees; funding interest is a later-stage borrow cost) | CURRENT_ONLY | CURRENT_ONLY |

Coverage: fees 3 bracketed / 2 current-only / 15 unresolved; tick 1 reconstructed / 17 current-only / 2 unresolved; lot-min 18 current-only / 2 unresolved.

### Fee bases

- **Binance — UNRESOLVED.** The USDⓈ-M fee page is script-rendered and undated (static content reads "No records found"); the Fee Structure FAQ (updated 2026-05-01) states no numeric rates; five candidate public JSON paths returned 404; the 2026 announcement surface shows no USDⓈ-M fee-rate change (only a 2025-07-24 new-listing maker promotion that ended 2026-01-16 and left taker fees unchanged); the derivatives API changelog 2026-06-02 → 09-10 records no fee change. Absence of a change notice is not a dated record of the rate, so no bracket can be formed.
- **Bybit — CURRENT_ONLY.** Two dated post-window official help articles (updated 2026-08-05 and 2026-09-02) state non-VIP perpetual taker 0.055 % / maker 0.02 %. The two 2026 fee notices are TradFi-only (effective 2026-06-16) and Pro/Market-Maker-only (effective 2026-09-01, "VIP retail pricing remains unchanged"). No pre-window dated record of the retail rate was located, so the bracket is one-sided.
- **OKX — CURRENT_ONLY.** Help article (published 2023-03-20, updated 2026-08-26): "if the fee level is lv1, then the taker fee rate is 0.05%, and the maker fee rate is 0.02%." The 2026-01-15 fee-grouping notice created Futures Group 1/2 without numeric rates and without naming OKB-USDT-SWAP; group moves are announced per pair (SPCX example, 2026-06-15). OKB's futures group on the required date is not established.
- **Gate — UNRESOLVED, conflicting first-party records.** Dated schedule notices bracket VIP0 at 0.02 % / 0.05 %: effective 2024-05-20 ("without market differentiation"), effective 2026-04-09 ("0.0500% unchanged across all contract groups"), and the 2026-09-01 notice says other USDT-M contracts "followed the same fee structure". Yet the official contract endpoint (Stage Four) reports GT_USDT and ASTER_USDT at taker 0.075 % / maker −0.01 % today, and no dated notice explains a contract-level override. Fail closed.
- **Kraken Futures — T2_HISTORICAL_FEE_BRACKETED.** Pre-window: "New Listings & Incentive Rebate Fee Schedule" (effective 2026-04-01, updated 2026-06-24) base tier maker 0.0200 % / taker 0.0500 %, "All other fee rates remain unchanged". Post-window: "Fees for Derivatives trading" (updated 2026-09-05) base tier 0.0200 % / 0.0500 %. Intervening: the 2026-07-09 cross-platform notice changed tier *qualification*, not rates; the 2026-06-22 fee-service migration is calculation infrastructure (release-note text not captured verbatim, listed as a residual check).
- **Bitfinex — T2_HISTORICAL_FEE_BRACKETED at zero.** Pre-window: help article updated 2026-06-01 and blog 2025-12-17: "Starting December 17th, 2025, no (Maker or Taker) fees apply for: Spot and Margin trading". Post-window: current official zero-fee and fee pages (captured 2026-09-11). No 2026 reintroduction found on official surfaces. Funding interest and the 15 % funding-provider fee are borrow-cost items, not trading fees.

### Constraint bases

- **Bybit GRAM tick — reconstructed.** Official notice published 2026-08-06, effective 2026-08-11 08:30 UTC: GRAMUSDT tick 0.0001 → 0.001. All GRAM signal and fill dates precede it, so the in-window tick was 0.0001; today's API value would have been wrong. The 2026-07-18 risk-limit adjustment (inside the window) changed leverage/margin, not lot or minimum. Lot/min-notional remain current-only.
- **Binance — CURRENT_ONLY, no intervening change found.** Five 2026 tick-size notices (02-09, 02-27, 04-06, 04-10 → 04-16, 08-06) and the 04-14 minimum-notional notice name none of the 13 instruments; the API changelog records no filter change in the window. That is not T2_BRACKETED_UNCHANGED because no dated pre-window value record exists.
- **Gate — UNRESOLVED.** `config_change_time` inside the window (ASTER 2026-09-01, GT 2026-09-09) with no notice describing the change; fractional-lot rollout was applied per contract on unannounced dates (notice 2025-12-18).
- **Kraken — CURRENT_ONLY.** Spec article (updated 2026-09-08) matches the API tick, but the parameters changelog renders only to 2025-09-05 and the API impact-mid-size differs from the last rendered changelog value, proving unrecorded later changes.
- **OKX, Bitfinex — CURRENT_ONLY.** No dated parameter notices located.

## 8–9. Spread and liquidity grades (50 fill windows)

| Grade | Spread | Liquidity |
|---|---|---|
| OBSERVED_BBO | 0 | 0 |
| OBSERVED_ORDERBOOK | 0 | **4** (Kraken analytics) |
| DERIVED_SPREAD_FROM_BBO | **4** (Kraken analytics) | 0 |
| DEPTH_PROXY_ONLY (Binance archived bookDepth) | 36 | 36 |
| TRADE_ACTIVITY_ONLY | 0 | 10 |
| UNRESOLVED | 10 | 0 |

Kraken's official Futures Market Analytics (`/api/charts/v1/analytics/<symbol>/{orderbook,liquidity,slippage,trade-volume}`, 1-minute resolution, first 60 minutes of each fill date) yielded best bid/ask, resting liquidity at percentage bands and quoted slippage for all four Kraken fills. Derived spreads at 00:00 UTC: KAS 07-06 29 bps (median 36 over the hour); SPX 06-29 15 bps, 07-04 39 bps, 07-06 38 bps. No other venue exposes historical order-book data; Binance depth remains a proxy, and trade activity was never converted into a spread.

## 12. KAS supplemental result

Sealed Stage Four verdict for `2026-07-05 KRAKEN:KASUSD BEAR_SHORT`: FAIL_NO_MARKET_ACTIVITY_AT_FILL, **preserved**. Official analytics for 2026-07-06 00:00 → 01:00 UTC: continuous two-sided book at every minute (bid 0.03094 / ask 0.03103 at 00:00, ≈29 bps), resting liquidity ≈393 k bid / ≈420 k ask within the venue's 0.05 % band, quoted slippage for 1 k and 10 k contract orders, and trade volume 0 for the whole hour. The frozen B3 step-6 evidence categories explicitly include `historical_spread_or_orderbook_proxy` next to `historical_volume`; the "no trades in 30 minutes" rule was a Stage Four tool rule, not a frozen-plan requirement. **Proposed revised verdict** (not applied): liquidity OBSERVED_ORDERBOOK, spread DERIVED_SPREAD_FROM_BBO, signal status UNRESOLVED_HISTORICAL_FEE → after 4A bracketing, blocked only on the constraint gap. Zero trades in the hour remains a recorded fact; fill at the open is still not assumed.

## 11, 13–15. Per-signal revised status and remaining gaps

| Outcome | Signals |
|---|---|
| Fully satisfied from historical evidence after 4A | **0** |
| Still requiring conservative assumptions | **72** |
| Not eligible (MORPHO venue policy ×2, TEL ×1) | 3 |

Exact unresolved fields by group (executed = at least one fill in the sealed dry-run lifecycle):

| Group | Signals | Unresolved fields |
|---|---|---|
| Binance, not executed | 30 | historical fee; tick and lot/min current-only |
| Binance, executed | 14 | historical fee; tick and lot/min current-only; spread DEPTH_PROXY_ONLY |
| Gate, not executed | 13 | historical fee (conflict); tick and lot/min unresolved |
| Gate, executed | 2 | as above plus spread unresolved |
| Kraken, not executed | 5 | tick and lot/min current-only (fee now bracketed) |
| Kraken SPX, executed | 2 | tick and lot/min current-only (fee bracketed; spread derived from BBO) |
| Kraken KAS, executed | 1 | tick and lot/min current-only; sealed FAIL preserved pending governance on the orderbook proposal |
| Bybit GRAM, not executed | 3 | historical fee current-only; lot/min current-only (tick reconstructed) |
| Bybit GRAM, executed | 1 | as above plus spread unresolved |
| OKX OKB, executed | 1 | historical fee current-only; tick and lot/min current-only; spread unresolved |

## 10. Sources and hashes

All 38 official records with full metadata are in the machine report (`official_records`) and manifest; raw HTML files carry `.sha256` sidecars. Kraken analytics raw responses (16 files) are under `raw/KRAKEN/<asset>/` with hashes. Key decisive records:

| Record | Published / effective | Preservation | sha256 |
|---|---|---|---|
| Kraken "New Listings & Incentive Rebate Fee Schedule" | eff. 2026-04-01, upd. 2026-06-24 | raw HTML | `b35d06033ece…` |
| Kraken "Fees for Derivatives trading" | upd. 2026-09-05 | raw HTML | `fec26f8cf7db…` |
| Kraken "Cross-platform fee tier changes (July 2026)" | 2026-07-09 | raw HTML | `89286ca1d9bd…` |
| Bitfinex "What fees does Bitfinex charge" | upd. 2026-06-01 (zero fees from 2025-12-17) | raw HTML | `b816915303e6…` |
| Bitfinex "Zero Fees Q&A" | 2025-12-17 | raw HTML | `aa4e29b6a9bf…` |
| Bybit "Change Tick Size for USDT Perpetual Contract Aug 11, 2026" | pub. 2026-08-06, eff. 2026-08-11 | raw HTML | `849c6fdbdbce…` |
| Bybit "Futures Contracts: Fees Explained" | upd. 2026-08-05 | raw HTML | `6e5bd86174d8…` |
| Bybit "Lower fees, simpler structure" | pub. 2026-08-24, eff. 2026-09-01 | raw HTML | `2dd4bcd915f4…` |
| OKX "How are futures trading fees calculated" | upd. 2026-08-26 | raw HTML | `bf31d0702e27…` |
| OKX "Advance Notice: Updates to Fee Grouping Adjustment" | pub. 2025-12-31, eff. 2026-01-15 | raw HTML | `fda9f1f15bda…` |
| Gate fee structure upgrade | pub. 2026-03-25, eff. 2026-04-09 | raw HTML | `f79cc01fade7…` |
| Gate USDT-M perpetual fee updates | pub. 2026-08-26, eff. 2026-09-01 | raw HTML | `b99529d9f584…` |
| Binance tick-size notices ×5, min-notional notice, fee FAQ, API changelog | 2026-02-25 → 2026-08-05 | rendered-text capture (script-only shell served) | captured-text hashes in report |

## 16. Does the frozen B3 plan permit governance to adopt conservative assumptions for the remaining gaps?

**Not as evidence.** The frozen B3 plan grades by source tier only (T1 → T5, T3 minimum decisive, T5 never decisive) and has no assumption class, so a conservative assumption can never raise a B3 evidence grade or be admitted as historical fact. The frozen B1 execution-data contract provides the separate, human-frozen cost base case gate (`C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW`, token `HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE`), where 37 bps is already recorded as sensitivity-only. Labelled `FROZEN_CONSERVATIVE_ASSUMPTION` values for the gaps above may be adopted only through that gate, frozen before any decisive performance is inspected, and reported separately from observed evidence. Stage 4A is sealed, so that selection can now proceed without contaminating evidence recovery. Nothing here selects a value.

## Verification

- Full C22 suite: **304 passed, 0 failures** (298 + 6 new).
- Commits: `1afafbfe` (tool, tests, sealed run, preserved records manifest); this report committed separately.
- Frozen V2 artifact sha256: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`, unchanged.
- Sealed Stage Four report sha256 re-verified unchanged. Precondition shell still `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED`, 0/26. Next B3 stage (step 7) not started.
