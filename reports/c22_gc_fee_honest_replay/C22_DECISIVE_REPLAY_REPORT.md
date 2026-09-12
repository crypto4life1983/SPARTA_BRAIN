# C22 — Decisive Replay Report

Date: 2026-09-12 · Results run `20260912T135725Z` · results sha256 `c20eaf5c1f1a38d21f85bce0320da889b0e41fd151e4eed30581f740666595ce`
Machine results: `reports/c22_gc_fee_honest_replay/c22_fee_honest_replay_results_20260912T135725Z.json`
Pre-registration: `reports/c22_gc_governance/c22_decisive_replay_preregistration_20260912T010013Z.json`, content hash `d09b0745e96c3f13…`
Commits `fc519fd9` (Stage 5, engine, sealed results) and `5e61d696` (stale test assertions).
Frozen V2 artifact `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`, unchanged. Full C22 suite: **305 passed, 0 failures**.

This is a historical research replay over sealed files. No order was placed, no exchange account was touched, no credential exists, no strategy rule was modified.

## Verdict

**INCOMPLETE_FOLLOWUP.** Six positions are still open at the data boundary, so under the frozen specification the decisive conclusion is withheld rather than declared. On the realized trades, all four economic gates fail, and the most important number does not depend on any cost assumption.

**Gross P&L is negative before a single cost is applied: −131.53 on 10,000 of NAV.** The fee, slippage, funding and borrow work decides how much is lost, not whether. Every sensitivity, including the most generous fee treatment tested, stays negative.

## Result

| | Value |
|---|---|
| Starting NAV | 10,000 (assumption; 100,000 tested as sensitivity) |
| Final NAV | 9,690.71 |
| Total return | **−3.09 %** |
| Sharpe, annualised √365 | **−1.58** (non-conclusive, low power) |
| Max drawdown | −6.79 % |
| Sessions | 58 |
| Closed trades | 22 (8 winners, 14 losers) |
| Open at boundary | 6 |

Cost levels, in NAV terms:

| Level | Total |
|---|---|
| Gross | −131.53 |
| Transaction-cost-only net | −254.74 |
| Fully net after funding/borrow | −247.38 |

Fees 70.37, slippage 52.84, funding −7.36 (received, shorts), borrow 0.00.

## By side

| Side | Trades | Gross | Fully net | Winners |
|---|---|---|---|---|
| Short | 15 | −111.49 | −148.53 | 5 |
| Long | 7 | −20.03 | −98.85 | 3 |

The long side is where the conservative fee assumption bites hardest: 60.05 of fees on 3,763 of notional, about 160 bps round trip, because no venue publishes a dated historical spot fee and the frozen rule takes the global maximum observed, Kraken Pro's 80 bps base tier. Even so, the long side is also negative before costs.

Exit reasons: 14 short stops above the GC filter, 7 long closes below the GC upper band, 1 out-of-radar. The single largest winner, IMX at +122.41 net, is the one out-of-radar exit.

## Benchmarks

| Benchmark | Total return | Sharpe |
|---|---|---|
| **C22 decisive** | **−3.09 %** | **−1.58** |
| BTC buy-and-hold | +21.33 % | +2.69 |
| Zero-return flat | 0.00 % | — |
| Signal-off control | 0.00 % | — |

Matched fixed-seed random-entry null, seed 20260911, 500 resamples, 28 matched trades, export-price basis: mean −0.02 %, median −0.18 %, 5th percentile −3.21 %, 95th percentile +3.79 %. The strategy on the same export-price basis returns −2.55 % transaction-cost-only, which sits below the null's median and far below its 95th percentile. The strategy does not beat random entry.

## Sensitivities, all labelled, none selected on results

| Variant | Return | Sharpe | Gross |
|---|---|---|---|
| Decisive (V2 sessions, venue prices, frozen base case) | −3.09 % | −1.58 | −131.53 |
| Export price basis | −2.89 % | −1.47 | −106.61 |
| Crypto-calendar session profile | −2.72 % | −1.22 | −70.02 |
| NAV 100,000 | −2.45 % | −1.18 | −920.37 |
| 37 bps round-trip convention | −2.23 % | −1.13 | −132.42 |
| Spot fee at lowest observed, 10 bps | −2.56 % | −1.31 | −132.08 |

Every variant is negative, and every variant is negative before costs.

## Integrity and fail-closed behaviour

| Check | Result |
|---|---|
| Duplicate trades | none |
| Cost arithmetic mismatch | none |
| Ledger validation | valid, cash reconciles |
| Capacity rejections | 1 |
| Minimum-order rejections | 0 |
| One-position-per-asset rejections | 54 |
| Missing execution price, failed closed | 5 |

The capacity rejection is `2026-07-15 BITFINEX:LEOUSD`: a 5 % NAV short is 500 against roughly 200 of observed traded notional in the fill window. The frozen rule rejected it rather than assuming the fill. That is the thin-venue problem from Stage Four showing up as a concrete refusal.

The five missing-price cases fail closed rather than invent a price: two AAVE signals, two MORPHO shorts (no home-venue short instrument), and the TEL short (no instrument exists).

## Positions open at the boundary

Never force-closed. Six positions, entered between 06-22 and 07-06, still open on 2026-09-09:

| Asset | Side | Entry | Notional |
|---|---|---|---|
| BINANCE:DEXEUSDT | long | 06-22 | 199.88 |
| BINANCE:QNTUSDT | short | 06-22 | 498.14 |
| GATE:ASTERUSDT | short | 06-22 | 499.74 |
| OKX:OKBUSDT | short | 06-24 | 445.50 |
| BYBIT:GRAMUSDT | short | 07-06 | 494.77 |
| KRAKEN:KASUSD | short | 07-06 | 494.70 |

Only ASTER has a mark at the boundary, showing −90.47 unrealized as a non-decisive diagnostic. The other five left the top-50 radar and have no admitted price, so no mark is invented. These positions are why the conclusion is INCOMPLETE_FOLLOWUP rather than a final REJECT: they carry roughly 2,600 of notional whose outcome is unknown.

## What was frozen before any result existed

The pre-registration fixed every rule and value, with its evidence class, before the engine computed anything:

- **Fees.** Conservative rule: the highest observed first-party retail taker per venue, or the global maximum where a venue publishes none. Binance perps 7.5 bps and all spot 80 bps are assumptions; Bybit 5.5, OKX 5.0, Gate 7.5, Kraken Futures 5.0 and Bitfinex 0 are observed. No maker rebate, token discount, VIP tier or promotion, ever.
- **Slippage.** Kraken fills use their observed derived half-spreads, 7.5 to 19.5 bps. Everything else uses 25 bps per side, derived as half the worst observed Kraken median spread.
- **Constraints.** Current tick, lot and minimum values as labelled assumptions, except the Bybit GRAM tick, reconstructed to 0.0001 from the dated notice because today's 0.001 would have been wrong for the window.
- **Capacity.** Order notional must not exceed observed liquidity at the fill: Binance resting notional within 0.2 %, Kraken analytics liquidity at 0.05 %, traded notional at trade-only venues, 1 % of daily volume for spot.
- **Funding.** Observed per settlement, 249 to 1,992 records per instrument. LEO borrow is an assumption at 0.557 % daily, since the observed flash return rate was zero.
- **Sessions.** V2_CONTRACT_EXACT decisive, crypto-calendar as sensitivity.

Basis diagnostic across 105 fills: median −7.3 bps between venue open and the CMC reference, mean absolute 17.3 bps, range −378 to +110. No basis adjustment was applied.

## Governance recorded

All outstanding lifecycle decisions were recorded on 2026-09-11 as present-day operator authorizations, never as historical tokens: Phase A REV1, B1, B2 and B3 acceptance, dry-run acceptance, evidence admission, short-instrument selection, cost base case freeze, weekend session rule, basis alignment, and the single advance-to-replay decision. Written to `reports/approvals/c22_governance_approvals_20260912T010013Z.json`.

The precondition shell now treats two instruments as governance-excluded rather than unevidenced, reported explicitly in every check: TEL, eliminated at Stage One because no instrument exists, and the MORPHO short, excluded by HOME_VENUE_ONLY. All 25 remaining required instruments are evidenced.

## Recommendation

The evidence supports **REJECT_KEPT_ON_RECORD**, which is what the 2026-09-09 closure recommendation proposed on feasibility grounds and what the economics now independently confirm. The case is stronger than a cost argument: the signal loses money before costs, loses to random entry, and loses badly to holding BTC.

Two honest caveats. The formal verdict is INCOMPLETE_FOLLOWUP while six positions remain open, and 22 closed trades is far too few to be statistically conclusive. Neither caveat points toward a different answer: closing the six positions favourably would need to overcome a negative gross edge, a failed null comparison, and a 24-point gap to buy-and-hold.

The decision is yours to record. If you want the open positions resolved first, the collection needs to run until they close naturally, then this replay re-runs unchanged under the same sealed pre-registration.
