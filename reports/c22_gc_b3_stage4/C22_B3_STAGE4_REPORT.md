# C22 — B3 Stage Four Report: Fees, Tick/Lot/Minimum, Liquidity, Spread (frozen steps 5–6)

Date: 2026-09-11 · Sealed run `20260911T131902Z` · report sha256 `6c7753208b05e928aef786edb7f3741929a1cf119e09374672d233241965b9d1`
Machine report: `reports/c22_gc_b3_stage4/c22_b3_stage4_fees_liquidity_20260911T131902Z.{json,md}` · run manifest `data/c22_short_instrument_evidence/manifests/stage4_run_manifest__20260911T131902Z.json`
Tool `tools/c22_b3_stage4_fees_liquidity_once.py` · tests `tests/test_c22_b3_stage4_fees_liquidity.py` · commit `230638bd`
Frozen contract executed: `ACQUISITION_ORDER[4..5]` = `5_fee_tick_lot_minimum_rules`, `6_liquidity_and_spread_evidence`; batch `C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION`; token name `HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE`. Inputs SHA-verified: Stage Three report `889be730…`, dry run `f76f8330…`, V2 `b6a28a48…`.
Scope honoured: read-only. No performance, no cost arithmetic, no assumption selected, no admission change, no later stage. The six additive evidence constraints were applied as stated.

## Headline

**0 of 72 eligible signals pass Stage Four. 71 are UNRESOLVED_HISTORICAL_FEE, 1 is FAIL_NO_MARKET_ACTIVITY_AT_FILL.** No venue exposes a dated historical fee schedule or historical tick/lot/minimum effective dates through its public API, so the frozen step-5 requirement cannot be met from first-party evidence; current values were recorded but never back-projected. Step-6 evidence was collected first-party at 50 fill windows and shows real liquidity dispersion, including several very thin venues.

## Fee evidence coverage (20 instruments)

| Status | Instruments |
|---|---|
| HISTORICAL_FEE_PROVEN | **0** |
| HISTORICAL_FEE_UNRESOLVED | **20** |
| CURRENT_FEE_ONLY available (Gate GT/ASTER maker −0.01 % / taker 0.075 %; Kraken Futures "MTF Linear Rebate Fees" tier-0 maker 0.02 % / taker 0.05 %) | 4 |
| Current fee not exposed by public API (Binance USD-M ×13, Bybit, OKX, Bitfinex) | 16 |

Class of every fee value recorded: OBSERVED_FIRST_PARTY for the four current values; UNRESOLVED otherwise. No FROZEN_CONSERVATIVE_ASSUMPTION was introduced; the pre-existing 37 bps figure remains SENSITIVITY_ONLY and was not used.

## Tick / lot / minimum evidence coverage (20 instruments)

| Status | Instruments |
|---|---|
| HISTORICAL_CONSTRAINT_PROVEN | **0** |
| CURRENT_CONSTRAINT_ONLY (current tick, lot step, min qty, min notional recorded) | **20** |
| HISTORICAL_CONSTRAINT_UNRESOLVED | **20** |

Only Gate publishes a change timestamp: `config_change_time` 2026-09-01 (ASTER_USDT) and 2026-09-09 (GT_USDT), both **inside** the required window 06-20 → 09-09, so the current Gate values demonstrably post-date at least part of the holding period. No other venue exposes constraint history.

## Spread evidence coverage (50 fill windows)

| Status | Fill windows |
|---|---|
| Best-bid/ask spread observed | **0** |
| Depth proxy observed (Binance archived `bookDepth`: resting notional within ±0.2 % / ±1 % at the first snapshot after 00:00 UTC) | 36 |
| UNRESOLVED_NO_FIRST_PARTY_HISTORICAL_BOOK (Bybit, OKX, Gate, Kraken Futures, Bitfinex) | 14 |

The depth proxy is labelled `DEPTH_AT_PERCENT_LEVELS_OBSERVED_NOT_BBO_SPREAD`; it is not represented as spread. Binance's archived `bookTicker` file was absent for the sampled date.

## Liquidity evidence coverage (50 fill windows, 30 minutes after the 00:00 UTC fill timestamp)

| Venue | Windows | Evidence | Observed |
|---|---|---|---|
| Binance (13 perps) | 36 | official archived depth snapshots | resting notional within ±0.2 % of mid ≥ $4.0k bid / ≥ $4.8k ask at the thinnest (IMX), up to ~$3.3M/side (SOL) |
| Bybit GRAMUSDT | 1 | official archived public trades | 4,496 trades, ≈ $275k notional |
| OKX OKB-USDT-SWAP | 1 | official history-trades | 600 trades (6 pages, window may be truncated), ≈ $8.05M |
| Gate GT_USDT / ASTER_USDT | 5 | official futures trades | GT: 5 / 13 / 55 / 1 trades ≈ $3.2k / $9.2k / $7.9k / $13; ASTER: 156 trades ≈ $2.6k |
| Kraken Futures PF_SPXUSD | 3 | official executions history | 8 / 8 / 6 trades ≈ $0.4k / $6.3k / $2.4k |
| Kraken Futures PF_KASUSD | 1 | official executions history | **0 trades in the window on 2026-07-06** |
| Bitfinex tLEOUSD | 3 | official public trades | 6 / 8 / 5 trades ≈ $262 / $550 / $208 |

Liquidity status: 49 windows OBSERVED_FIRST_PARTY, 1 no activity, 0 unresolved. Trade-window summaries (count, VWAP, notional, price range, seconds to first trade) are DERIVED_FROM_OBSERVED_DATA. Nothing was inferred about zero spread, infinite liquidity, full fill at the open, or zero impact; every fill record carries those four items under `never_inferred`.

Notable observed facts (not assumptions): at Kraken (SPX), Gate (GT on 07-05 and 07-23) and Bitfinex (LEO) the notional traded in the 30 minutes after the fill timestamp is in the hundreds to low thousands of dollars, far below a 3–5 % NAV position at any meaningful NAV; and GT_USDT on 07-23 saw a single $13 trade.

## What is historically observed vs assumption-only

| Historically observed, first party | Assumption-only / unresolved |
|---|---|
| Instrument existence and launch timestamps (Stage One) | Historical fee rates on any 2026 date (all venues) |
| Historical shortability: activity + funding settlements; LEO pair-specific short positions (Stage Two) | Historical tick/lot/minimum values on the fill dates (all venues) |
| Daily OHLC 06-20 → 09-10 (Stage Three) | Best-bid/ask spread at any fill (all venues) |
| Depth within ±0.2 %/±1 % at 36 Binance fills; public trades at 14 other fills (Stage Four) | Order-book depth at non-Binance fills; market impact for any position size |
| Current fee values at Gate and Kraken Futures; current filters at all 20 instruments | Any fee or slippage model (none selected) |

## Per-signal PASS / FAIL / UNRESOLVED (75 frozen shorts)

| Verdict | Signals |
|---|---|
| PASS_STAGE_FOUR | **0** |
| UNRESOLVED_HISTORICAL_FEE (fail-closed on the first missing frozen element; constraints and, where applicable, spread are also missing) | **71** |
| FAIL_NO_MARKET_ACTIVITY_AT_FILL — `2026-07-05 KRAKEN:KASUSD BEAR_SHORT`: zero executions in the 30 minutes after the 2026-07-06 fill timestamp under both weekend profiles; a fill at the open cannot be assumed (the day as a whole did trade per Stage Two) | **1** |
| NOT_ELIGIBLE_PRIOR_STAGE (MORPHO ×2 venue policy, TEL ×1) | 3 |

Of the 72 eligible signals, 21 executed at least one fill in the sealed dry-run lifecycle; 51 never executed (rejected at fill by one-position-per-asset, or unfilled) and therefore have no fill window to evidence, which is recorded per signal.

## Updated 88-signal funnel

| Stage | Count |
|---|---|
| Frozen V2 signals | 88 |
| Long signals (no execution-evidence process yet) | 13 |
| Frozen short signals | 75 |
| Stage One: dated existence | 74 |
| Stage Two: historical shortability + HOME_VENUE_ONLY | 72 |
| Stage Three: execution OHLC coverage | 72 |
| **Stage Four: fees + constraints + liquidity + spread historically proven** | **0** (71 unresolved, 1 fail) |
| Fee-honestly replayable trades | **0** |

## Exact blockers before admission

1. **Historical fees.** No venue publishes dated fee schedules via API. Options that remain within governance: acquire T2 archived official fee records per venue (out of band, human-performed), or adopt a FROZEN_CONSERVATIVE_ASSUMPTION through the frozen governance process, explicitly labelled and frozen **before** any decisive performance is inspected. Nothing here selects one.
2. **Historical tick/lot/minimum.** Same structure; Gate's in-window config changes make back-projection provably unsafe there. A governance decision on CURRENT_CONSTRAINT_ONLY values is required.
3. **Spread.** No first-party BBO at any fill. Binance depth proxies exist for 36 fills; the other 14 have trades only. A labelled spread assumption or sensitivity band would have to come from governance.
4. **Market impact and thin venues.** Observed notional at Kraken SPX/KAS, Gate GT, Bitfinex LEO fills is tiny; the KAS 07-06 fill has no activity at all. Position sizing versus observed depth is a Stage 7 / admission question.
5. **Frozen step 7** (full holding-period coverage sign-off), the admission review token, the cost base case freeze, the weekend-rule ruling, the basis review, and long-signal execution evidence.

## Verification

- Full C22 suite: **298 passed, 0 failures** (289 + 9 new).
- Commits: `230638bd` (tool, tests, sealed run); this report committed separately.
- Frozen V2 artifact sha256 after the run: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`, unchanged.
- Precondition shell: `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED`, 0 of 26 instruments admitted.
- Raw evidence: 63 official responses preserved with hashes; 39 canonical evidence files under `fees/<venue>/` and `liquidity/<instrument>/`.
- Next frozen step (`7_full_holding_period_coverage`) not started.
