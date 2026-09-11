# C22 — B3 Stage Three Report: Execution-Instrument Historical OHLC (frozen step 4)

Date: 2026-09-11 · Repo `C:\SPARTA_BRAIN` (master, none pushed)
Sealed Stage Three run: `20260911T130800Z` · report sha256 `889be73018ee4d20a0031daf4797951b3bafa8245a59b4a805bc7eb59e48e763`
Machine report: `reports/c22_gc_b3_stage3/c22_b3_stage3_historical_ohlc_20260911T130800Z.{json,md}` · run manifest `data/c22_short_instrument_evidence/manifests/stage3_run_manifest__20260911T130800Z.json`
Scope honoured: read-only historical research. No performance, no cost arithmetic, no paper/live, no credentials, no strategy change, no alternative venues, no later stage started. V2, frozen exports, Phase A, B1, B2, B3 untouched.

## 1. Stage Two governance closure and final funnel

Closure of record: `reports/c22_gc_governance/c22_b3_stage2_governance_closure_20260911T130440Z.json`, sha256 `ebca5fe7afe46d23e8468a12a458d69cbe1f2a3ac74c7c004791f1cb76c7bd36` (commit `957104a8`). A first closure attempt (`…130348Z`) is retained on disk: it returned UNRESOLVED only because Bitfinex answers the daily-timeframe statistics keys with empty arrays; those empty responses are preserved. The run of record uses the minute-level series.

Recorded decisions (human, 2026-09-11; no performance information exists or was consulted):

- **Decision 1 — decisive venue policy `HOME_VENUE_ONLY`.** No cross-venue substitution to rescue a signal. Future cross-venue testing must be a separately named sensitivity experiment with one predetermined venue hierarchy across the whole cohort, never mixed into the decisive V2 replay.
- **Decision 2 — LEO** resolved by pair-specific evidence (section 2).

| Final Stage Two funnel | Signals |
|---|---|
| Frozen short signals | 75 |
| Stage One survivors | 74 |
| Stage Two PASS before governance | 72 |
| EXCLUDED_VENUE_POLICY (MORPHO) | 2 |
| Stage One elimination preserved (TEL) | 1 |
| LEO final | PASS_HISTORICAL_SHORTABILITY |
| Unresolved | 0 |
| **Decisive executable short signals after Stage Two** | **72** (20 assets) |
| Admitted for fee-honest replay | 0 |

## 2. LEO final decision and supporting evidence

**PASS_HISTORICAL_SHORTABILITY**, on pair-specific first-party evidence, not on the general funding-market inference.

Official Bitfinex statistics for the canonical pair and funding currency from the B3 mapping (`tLEOUSD`, `fLEO`), minute resolution across the required dates 2026-07-15 and 2026-07-16 (decision and both fill conventions):

| Statistic (official `stats1`) | 2026-07-15 | 2026-07-16 |
|---|---|---|
| `pos.size:1m:tLEOUSD:short` (short position size on the exact pair) | > 0 at every observed minute; ≈117,045 LEO at 00:00 UTC | > 0 at every observed minute |
| `credits.size.sym:1m:fLEO:tLEOUSD` (funding credits used on the exact pair) | > 0 at every minute; ≈9,969 LEO | > 0 at every minute; ≈10,093 LEO |

Short positions on the pair were therefore actually present, and pair-specific LEO funding was in use, throughout the required period. Present-day margin flags were not used; the general borrow-market inference was not used as decisive. Raw responses, parameters, UTC retrieval times and SHA-256 hashes are in the closure artifact (`decision_2_leo.supplemental_evidence`).

## 3. MORPHO excluded-by-policy count

**2** short signals (2026-07-01, 2026-07-06). Stage One historical existence PASS preserved. Decisive execution status `EXCLUDED_VENUE_POLICY` because both require Coinbase International rather than the frozen home-venue mapping. Not classified as instrument-nonexistent; no evidence deleted.

## 4. TEL preserved elimination

**1** signal (2026-07-09). Stage One `FAIL_WRONG_INSTRUMENT_TYPE` preserved; no alternative venue searched; decisive execution status `ELIMINATED_STAGE_ONE_PRESERVED`.

## 5. Exact Stage Three contract executed

`sparta_commander/c22_historical_evidence_acquisition_plan_contract.py`, `ACQUISITION_ORDER[3] = "4_historical_ohlc"`, authorization batch `C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION` ("authorize fetching execution-instrument historical OHLC"), token name `HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE`. Evidence categories: `historical_ohlc` (perpetual/futures) and `historical_volume` (spot-margin pair). Layout `data/c22_short_instrument_evidence/ohlc/<asset>/`, filename convention `<venue>__<asset>__historical_ohlc__<start>_<end>` with `.sha256` sidecars, manifest with per-file sha256 and coverage, never overwriting. Source tier used: T1 official venue APIs (decisive minimum T3). Steps not executed: 5 fee/tick/lot/minimum, 6 liquidity/spread, 7 full-holding-period sign-off. Authorization basis: the operator's 2026-09-11 message; no approval record was fabricated.

## 6. Inputs required by Stage Three (all sealed, all SHA-verified before use)

| Input | Identity |
|---|---|
| Stage Two governance closure | `…130440Z.json`, sha `ebca5fe7…` (verified against its manifest) |
| Stage Two report of record | run `20260910T231336Z`, sha `03fbc617…` |
| Stage One report of record | run `20260910T225620Z`, sha `95b135c3…` |
| No-P&L dry run (holding windows) | sha `f76f8330…` |
| Frozen forward horizon | initial range → 2026-08-14; extension #2 = 2026-08-30..09-13; replay boundary 2026-09-09 (last admitted export) |
| Frozen V2 artifact | `b6a28a48…` |

Range fetched: 2026-06-20 → 2026-09-10 (last complete UTC day). Required coverage: through 2026-09-09.

## 7. Per-instrument and per-signal Stage Three outcomes

**Instruments (20, home venue, official daily OHLC):**

| Asset | Instrument | Rows | Coverage 06-20→09-09 | Canonical sha256 (prefix) |
|---|---|---|---|---|
| BINANCE AAVE/CRV/IMX/INJ/LINK/PENDLE/QNT/SOL/SUN/TIA/TRX/VIRTUAL/ZEC | `<BASE>USDT` USD-M perps | 83 each | 82/82 | `691b9f10`, `f9e963de`, `14c9ec6b`, `d2dca9c4`, `04e981f9`, `707c9ed7`, `20b30c25`, `0d996e20`, `aaf3e4fc`, `de23b130`, `5c8d5789`, `9a2fc8a5`, `436f18ad` |
| BYBIT:GRAMUSDT | GRAMUSDT linear | 81 | 80/82 (06-20, 06-21 pre-launch; no GRAM signal before 07-05) | `7bd02f5c` |
| OKX:OKBUSDT | OKB-USDT-SWAP | 83 | 82/82 | `b8d14aac` |
| GATE:GTUSDT / GATE:ASTERUSDT | GT_USDT / ASTER_USDT | 83 / 83 | 82/82 | `152eb666` / `cc547b71` |
| KRAKEN:KASUSD / KRAKEN:SPXUSD | PF_KASUSD / PF_SPXUSD | 83 / 83 | 82/82 | `5490872f` / `4e6be6ac` |
| BITFINEX:LEOUSD | tLEOUSD | 83 | 82/82 | `a7f87038` |

**Per-signal (75 frozen shorts):**

| Verdict | Signals |
|---|---|
| PASS_OHLC_COVERAGE (official candle every day from decision date to exit fill or 09-09 boundary) | **72** |
| FAIL_OHLC_COVERAGE_GAP | 0 |
| UNRESOLVED_OHLC_SOURCE | 0 |
| NOT_ELIGIBLE_EXCLUDED_VENUE_POLICY (MORPHO) | 2 |
| NOT_ELIGIBLE_STAGE_ONE_ELIMINATED (TEL) | 1 |

Holding windows come from the sealed dry run, taking the longer of the two weekend profiles; the six positions open at the data boundary require coverage through 2026-09-09 and have it.

## 8. Updated funnel from the 88 frozen signals

| Stage | Count |
|---|---|
| Frozen V2 signals | 88 |
| Long signals (no execution evidence process yet; B3 covers shorts) | 13 |
| Frozen short signals | 75 |
| Stage One: dated instrument existence | 74 |
| Stage Two: historical shortability + HOME_VENUE_ONLY governance | 72 |
| Stage Three: execution OHLC coverage over holding windows | 72 |
| Steps 5–7 (fees/tick/lot/minimums, liquidity/spread, holding-period sign-off) | not started |
| Human admission (`…HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT`) | not recorded |
| Cost base case frozen | no |
| **Fee-honestly replayable trades** | **0** |

## 9. Every remaining blocker

1. Frozen steps 5 (fee schedule, tick, lot, minimum notional) and 6 (liquidity/spread) for the 20 instruments; then step 7 sign-off.
2. Human admission review and token for the acquired evidence (the precondition shell reads only admission manifests, none exist: still `REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED`, 0/26).
3. Cost base case freeze (`…EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE`); 37 bps stays sensitivity-only.
4. Weekend session rule ruling; basis-alignment review (signal prices are CMC reference prices).
5. Execution-venue evidence for the 13 long signals (outside B3's short scope).
6. Lifecycle ACCEPT records for Phase A REV1, B1, B2, B3 and the dry run; the closure decision requested by the 2026-09-09 closure recommendation.
7. Out-of-radar exit prices: the acquired OHLC now covers the six open-at-boundary positions' instruments through 09-09, but admitting it as the exit price source is a human decision (B1 price-source contract).

## 10. Does the frozen specification permit requesting the next stage?

**Yes.** With 0 unresolved and 72 PASS, the plan's fail-close-early conditions for steps 1–4 are satisfied, so batch 4 (`C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION`, token `HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE`, steps 5–6) may be requested. It was **not** started.

## 11. Complete C22 test count

**289 passed, 0 failures** (280 after Stage Two + 9 new closure/Stage Three tests).

## 12. Commits created

- `957104a8` — Stage Two governance closure tool + sealed closure artifacts.
- `d90352a2` — Stage Three tool, tests, sealed run report.
- This report is committed separately after it.

## 13. Frozen V2 artifact hash

`b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8` — verified after Stage Three, unchanged.
