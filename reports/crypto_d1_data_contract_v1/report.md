# SPARTA Crypto-D1 Data Contract v1 — build report

> **Research-only. Data contract / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no backtest,
> no dataset processing in this bundle**.

This bundle satisfies the **P1_data_contract** phase of the Crypto-D1
Protocol Memo v1 (Bundle 11). It is the written input spec that any
future, separately-authorized P2 data-acquisition bundle must satisfy.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_data_contract_v1/data_contract.json` | Machine-readable contract (validator source of truth). |
| `reports/crypto_d1_data_contract_v1/data_contract.md` | Human-readable contract: scope (BTC/ETH/SOL spot daily 24/7), 9 required + 7 optional OHLCV columns, timestamp + OHLCV + session + missing-data + duplicate + symbol-mapping + provenance + normalization rules, fee/slippage requirements, data freeze requirements, future allowed / forbidden data sources, minimum-viable-dataset shape, required-future-artifacts list, PASS/WATCH/FAIL rules, no-profit-claim policy, safety boundaries. |
| `reports/crypto_d1_data_contract_v1/report.md` | This build report. |
| `reports/crypto_d1_data_contract_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_data_contract_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_data_contract.py` | 28 tests covering schema, safety, validator failure modes, tool stdlib-only, and integration with prior bundles. |
| `tools/strategy_candidate_registry.py` | Added the two new data_contract docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 12 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 13 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, all 8 prior arbitrage validators + docs, the Bundle
11 Crypto-D1 Protocol memo, `tools/strategy_next_bundle.py` (no
artificial selection nudge), `lessons.md`.

## What the Crypto-D1 data contract defines

1. **Lane + scope.** Lane `crypto_d1_protocol` (same lane as the
   protocol memo). Targets BTC + ETH + SOL spot only on the daily
   timeframe. Perps / dated futures / options / leveraged tokens /
   margin-or-borrow-facilitated spot / synthetic instruments are
   forbidden at v1 — perps require a separate future protocol because
   funding / liquidation / leverage change the research problem;
   intraday requires a separate future protocol.
2. **Required daily OHLCV schema (9 columns).** `timestamp`, `open`,
   `high`, `low`, `close`, `volume`, `symbol`, `source`,
   `quote_currency`.
3. **Optional daily OHLCV columns (7 columns).** `vwap`,
   `trade_count`, `quote_volume`, `taker_buy_volume`,
   `source_timestamp`, `ingestion_timestamp`, `adjusted_close`. Note:
   crypto spot normally has no equity-style split adjustments;
   `adjusted_close` is supported only for source compatibility.
4. **Timestamp + 24/7 session rules.** UTC primary clock, ISO-8601
   storage, daily bar boundary UTC 00:00:00 close, 24/7 calendar,
   weekday-only filters forbidden, missing-day detection flagged in
   manifest (never silently forward-filled), duplicate
   `(symbol, timestamp)` rejection, DST handling N/A in UTC storage,
   partial-day bars excluded from frozen datasets, source vs.
   ingestion timestamp roles documented.
5. **OHLCV quality rules.** `high >= max(open, close, low)`,
   `low <= min(open, close, high)`, OHLC positive, volume
   non-negative, duplicate rows invalid, missing timestamp / missing
   close invalid, zero-volume suspicious-flag, extreme gap / outlier
   flag, source outage flag, self-consistency check required before
   freeze.
6. **Fee / slippage requirements.** Spot taker fee required per venue
   dated and pre-declared (taker default on every leg), spot maker
   fee recorded only when pre-registered, lowest-realistic fee tier
   default, conservative bps + 1-tick slippage, constant-bps spread
   proxy when quote data is absent, stablecoin quote currency
   declared per series, cost-sensitivity checks required before any
   PASS, no-profitability-claim if fees / slippage are ignored, fees
   as a distinct PnL line in every future backtest report.
7. **Data freeze requirements.** No future backtest can use mutable /
   unfrozen data; every dataset has a manifest, references this
   contract version, and passes data QA / freeze checks before
   backtest use; any data revision creates a new dataset version; no
   manual edits without documentation and revalidation.
8. **Symbol mapping + provenance.** Canonical SPARTA symbol required
   per row; per-venue aliases versioned; rename / fork events
   first-class; row-level source id required; file hash on freeze;
   contract version pinned per dataset.
9. **Missing-data + duplicate rules.** No silent forward-fill;
   missing-day flagged in manifest; missing close / missing timestamp
   / missing source id invalid; partial-day bars excluded; outage
   calendar attached; duplicate `(symbol, timestamp)` rejected;
   strictly monotonic per symbol.
10. **Minimum viable dataset.** At least 3 years of daily OHLCV per
    included asset (5+ preferred); BTC required; ETH + SOL
    recommended; single source per asset; frozen sha256; manifest;
    contract version pinned; QA report before use; IS + OOS windows
    sealed before run; provenance per row; warmup buffer; fee
    schedule; outage calendar (when available).
11. **Future allowed data sources.** Existing on-disk frozen files;
    a future SEPARATELY authorized P2 data-acquisition bundle;
    operator-supplied paid-vendor offline exports.
12. **Forbidden data sources / methods.** Live exchange APIs from
    this contract's runtime, web scraping, anything that requires an
    embedded API key / OAuth token / .env credential, anything that
    requires SPARTA to make a network call from its runtime,
    synthetic / mock data in place of real history, anonymous
    provenance, OOS-window peeking, TOS-incompatible feeds.
13. **PASS / WATCH / FAIL rules + safety boundaries + no-profit-claim
    policy.**

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest /
  dataset-processing flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`, `backtest_enabled`,
  `dataset_processing_enabled`.
- `research_only: true` asserted.
- `lane == "crypto_d1_protocol"` asserted.
- Target assets MUST include BTC, ETH, SOL.
- `allowed_market_type == "spot"`; perps / dated_futures / options /
  leveraged in `forbidden_market_types`.
- Timeframe `1d`; `intraday_explicitly_out_of_scope = True`.
- All 9 required OHLCV columns present.
- Timestamp / OHLCV / session / missing-data / duplicate /
  fee_slippage requirement sub-keys present.
- `pass_watch_fail_rules` carries PASS / WATCH / FAIL.
- `safety_boundaries` carries `research-only`, `no broker`, `no
  live`, `no order`.
- MD carries `Crypto trend ideas are not profitable until tested`,
  `A good historical chart does not imply future returns`, `No
  backtest is authorized by this contract alone`, `Clean OHLCV data
  does not imply profit`, `24/7`.
- Validator scans MD + JSON for forbidden capability claims
  (`guaranteed profit`, `risk-free profit`, `live-ready`,
  `production-ready`, `place the order`, `connect to exchange`,
  `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`). No `requests`, `urllib`, `socket`,
  `ssl`, `tiingo`, `ccxt`, `alpaca`, `binance`, `dotenv`,
  `subprocess`, `os.environ`, `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_data_contract.py --rootdir=tests -q
→ 28 passed in 0.26s

python -m pytest tests/test_crypto_d1_data_contract.py tests/test_crypto_d1_protocol.py tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 260 passed in 2.53s
```

- `test_crypto_d1_data_contract.py` — **28 new tests** (Bundle 12).
- Bundle 11 protocol — 21 still pass.
- Bundle 10 readiness gate — 22 still pass.
- Bundle 9 sample dataset plan — 23 still pass.
- Bundle 8 data source evaluation — 23 still pass.
- Bundle 7 QA harness spec — 22 still pass.
- Bundle 6 dataset manifest — 19 still pass.
- Bundle 5 data contract (arbitrage) — 16 still pass.
- Bundle 4 research protocol (arbitrage) — 14 still pass.
- Bundle 3 candidate registry — 16 still pass.
- Bundle 2 next-bundle generator — 24 still pass.

## JSON validity

```
python tools/crypto_d1_data_contract_check.py validate         → validate: OK
python tools/crypto_d1_protocol_check.py validate              → validate: OK
python tools/arbitrage_readiness_gate_check.py validate        → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate   → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate→ validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate       → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate      → validate: OK
python tools/arbitrage_data_contract_check.py validate         → validate: OK
python tools/arbitrage_protocol_check.py validate              → validate: OK
python tools/strategy_candidate_registry.py validate           → validate: OK
python tools/strategy_next_bundle.py validate                  → validate: OK
```

## Crypto-D1 data contract validation result

**`validate: OK`** on the committed contract. All required top-level
keys present; all 7 safety flags pinned `False`; lane =
`crypto_d1_protocol`; target assets include BTC + ETH + SOL; allowed
market type = `spot`; perps / dated / options / leveraged in
`forbidden_market_types`; timeframe = `1d` with intraday explicitly
out of scope; all 9 required OHLCV columns present (`timestamp`,
`open`, `high`, `low`, `close`, `volume`, `symbol`, `source`,
`quote_currency`); timestamp / OHLCV / session / fee_slippage /
missing-data / duplicate sub-keys all present; MD carries all 5
required distinction phrases; zero forbidden capability phrases.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires because the
  seed's `extra_files` now include both `protocol.md/.json` and the
  new `data_contract.md/.json`, all of which exist on disk).
- **evidence_level:** `MIXED` (19 matched docs across historical
  CODR-1 reports + the new v1 protocol + the new v1 data contract;
  cannot reach `STRONG`).
- The new data-contract docs are added to `source_reports`.
- Guards held: **never ACTIVE / never STRONG**.

## Next-bundle generator selected bundle after update

**Selects "Arbitrage research protocol"** (lane =
`arbitrage_research_protocol`, priority = 3) — same as Bundle 11.
Both arbitrage and crypto_d1 are now WATCH with the same `+15` bonus;
the arbitrage lane wins on the existing protocol-first / data-first
scoring hints already in its queue item. **Deterministic logic was
not artificially modified.** The operator should consult both lanes'
next-step lists to pick the actual Bundle 13.

## How this follows Crypto-D1 Protocol Memo v1

1. Bundle 11 declared `P1_data_contract` as a required future artifact.
2. This bundle authors that data contract — spec only; no data is
   fetched, no backtest is run, no dataset is processed.
3. All seven safety flags from the protocol carry verbatim into the
   data contract.
4. Lane scope is identical: BTC / ETH / SOL, spot only, daily only,
   24/7; perps and intraday remain separately-future protocols.
5. Fee / slippage requirements echo the protocol's
   `fee_slippage_requirements` and add concrete contract-level
   assertions (taker default, conservative slippage, cost-sensitivity
   checks before PASS, fees as a distinct PnL line, no-profitability-
   claim-if-fees-ignored).
6. Data requirements echo the protocol's `data_requirements` with
   concrete column-level schema, validity rules, and a
   minimum-viable-dataset shape.

## Recommended next bundle

All four follow this contract's `required_future_artifacts`. Each is
a SEPARATE, separately-authorized future bundle; all are spec-only
(no fetch, no backtest, no execution):

1. **Crypto-D1 Dataset Manifest v1** (P2) — per-dataset manifest
   schema for the crypto-D1 lane. Spec only.
2. **Crypto-D1 Data QA / Freeze Spec v1** (P2) — QA harness spec
   for daily-crypto data. Spec only, no harness run.
3. **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-
   registration memo for the FIRST candidate strategy family + IS /
   OOS split. Plan only, no backtest run.
4. **Crypto-D1 Data Acquisition Authorization Draft** — still
   spec-only; only if the operator wants to start the path toward an
   actual P2 acquisition. Does not authorize anything by itself.
