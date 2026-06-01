# SPARTA Crypto-D1 Data Contract v1

> **Research-only. Data contract / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest.
> No dataset processing in this bundle.** This contract defines exactly what
> daily OHLCV crypto data WOULD be required to later test the Crypto-D1
> Protocol Memo v1 strategy families — **before** any data fetch, backtest,
> paper trading, or live trading is allowed.

**Data contract id:** `crypto_d1_data_contract_v1` · **version:** `1.0`

**Companion documents (read-only references):**
- `reports/crypto_d1_protocol_v1/protocol.md` — the protocol this contract serves (BTC / ETH / SOL spot, daily, 24/7).
- `reports/crypto_d1_protocol_v1/protocol.json` — machine-readable protocol.

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol` (same lane as the Crypto-D1 Protocol Memo v1).
- **Target assets:** **BTC** (required), **ETH** (required), **SOL** (required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**
  and requires a separate future protocol.
- **Allowed market type:** `spot` only.
- **Forbidden market types** at v1: perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic instruments.

Perpetual futures require a **separate future protocol** — funding,
liquidation, leverage, mark-vs-index, and contract specs change the research
problem and must not be folded into spot at v1.

Intraday crypto requires a **separate future protocol** — sub-daily bar
construction, microstructure noise, and the L1/L2 quote requirement raise a
different set of data and cost questions than daily-bar research.

## 2. Required daily OHLCV schema

A future per-dataset file MUST carry these **required columns**:

| Column | Description |
|---|---|
| `timestamp` | UTC bar boundary (ISO-8601). Primary key component. |
| `open` | UTC open price (positive). |
| `high` | UTC high price (positive). |
| `low` | UTC low price (positive). |
| `close` | UTC close price (positive). |
| `volume` | Non-negative; unit declared in manifest. |
| `symbol` | SPARTA canonical symbol (BTC / ETH / SOL). |
| `source` | Venue / vendor / file-hash identifier (row-level provenance). |
| `quote_currency` | USD / USDT / USDC / etc. declared per series. |

And MAY carry these **optional columns** when the source supports them:

| Column | When applicable |
|---|---|
| `vwap` | Volume-weighted average price published by the source. |
| `trade_count` | Per-bar trade count published by the source. |
| `quote_volume` | Volume in quote-currency units (when the source publishes it). |
| `taker_buy_volume` | Taker-buy volume (order-flow proxy) when available. |
| `source_timestamp` | Venue-issued bar timestamp (e.g., `open_time`). |
| `ingestion_timestamp` | SPARTA-reader-side audit timestamp. |
| `adjusted_close` | **Crypto spot normally has no equity-style split adjustments.** Supported only for source-compatibility; expected to equal `close` in nearly all rows. Any divergence MUST be explained by a documented corporate-action-equivalent event (rename / fork / network change). |

## 3. Asset + market scope

| Asset | Required? | Rationale |
|---|---|---|
| `BTC` | required | Highest liquidity, deepest historical record. |
| `ETH` | required | Second-deepest history; cross-asset robustness vs. BTC. |
| `SOL` | required | Intentionally different vol / drawdown profile; prevents BTC-only overfit. |

**Allowed market type:** `spot` only.
**Forbidden market types at v1:** perp futures, dated futures, options,
leveraged tokens, margin / borrow-facilitated spot, synthetic instruments.

## 4. Timestamp and 24/7 session rules

- **Primary clock:** UTC; ISO-8601 in storage.
- **Daily bar boundary:** UTC 00:00:00 close; left-closed / right-open
  documented per dataset manifest.
- **Session handling:** 24/7 crypto calendar; **weekday-only filters
  forbidden**.
- **Missing-day detection:** every missing daily bar flagged in the dataset
  manifest's `missing_day` list; **never silently forward-filled**.
- **Duplicate timestamp rejection:** duplicate `(symbol, timestamp)` rows
  are invalid; `(symbol, timestamp)` is the natural primary key.
- **Daylight saving:** not applicable in UTC storage; any local-time source
  is converted at ingest with the original timezone preserved as metadata.
- **Partial-day bars:** partial-day bars (latest live bar at ingest) are
  **excluded** from frozen datasets; only fully-closed UTC bars are valid.
- **Source vs. ingestion timestamp:** if both are available, both are
  stored; `source_timestamp` is the venue-issued bar time and is the primary
  key component, `ingestion_timestamp` is recorded as audit metadata only
  (never the sole primary clock).

## 5. OHLCV quality rules

- `high >= max(open, close, low)`
- `low <= min(open, close, high)`
- `open`, `high`, `low`, `close` all **positive**.
- `volume >= 0` (non-negative).
- **Duplicate rows** are invalid.
- **Missing timestamp** invalid.
- **Missing close** invalid.
- **Zero-volume daily bars** on a 24/7 asset are highly suspicious; flagged
  for review and never silently kept in a frozen dataset without an explicit
  outage / illiquidity explanation.
- **Extreme gap / outlier flag:** daily moves beyond a per-asset rolling-vol
  band (e.g., greater than N times 30d realised vol) are flagged as
  suspicious-bar events; flagged not dropped.
- **Source outage flag:** documented source outage days carry an outage
  flag column; gap rows in outage windows are not silent missing-data.
- **OHLCV self-consistency check** is required before a dataset can be
  marked frozen.

## 6. Fee + slippage requirements

- **Spot taker fee:** required per venue, dated, pre-declared before any
  future test. **Default sizing assumption is TAKER on every leg.**
- **Spot maker fee:** recorded only when a future test pre-registers maker
  fills; maker fills are never the default.
- **Fee tier:** the lowest standard tier the operator could realistically
  maintain; never best-case.
- **Slippage:** conservative slow-day haircut (constant-bps plus one-tick)
  on top of fees; depth-aware when L2 is available in a future intraday
  extension.
- **Spread assumption when quote data is absent:** a constant-bps spread
  proxy is documented and used as an additive haircut; the proxy is
  conservative.
- **Stablecoin quote currency:** declared per series; any cross-stablecoin
  conversion is documented and explicit; assumed-one-to-one is disallowed
  without explicit disclosure.
- **Cost sensitivity checks required before any PASS:** no PASS verdict is
  allowed without a cost-sensitivity test (fees ±N bps, slippage ±M bps)
  showing that the verdict survives.
- **No profitability claim allowed if fees / slippage are ignored.**
- **Fees as a distinct PnL line:** every future backtest report must carry
  fees as a distinct PnL line; never silently netted.

## 7. Data freeze requirements

- **No future backtest can use mutable / unfrozen data.** The dataset MUST
  be frozen with a sha256 manifest before any IS or OOS run.
- **Every future dataset must have a manifest.**
- **Every dataset must reference this data_contract version** explicitly.
- **Every dataset must pass data QA / freeze checks** before backtest use
  (the checks are defined in a separately-authored Crypto-D1 Data QA / Freeze
  Spec).
- **Any data revision creates a new dataset version**; in-place edits are
  forbidden.
- **No manual edits unless documented and revalidated** under a new
  `dataset_version`.

## 8. Symbol mapping, normalization, provenance

- **Canonical symbol required** per row (BTC / ETH / SOL).
- **Per-venue alias** recorded in a versioned mapping table (e.g.,
  `XBTUSD` on Kraken vs. `BTCUSDT` on Binance).
- **Rename handling:** asset renames (e.g., LUNA → LUNC, MATIC → POL)
  recorded as first-class events; not silently mapped.
- **Split handling:** crypto spot rarely splits. If a split-equivalent or
  network change occurs, treated as a corporate-action-equivalent event
  with a documented adjustment method; raw and adjusted both stored.
- **Fork handling:** forks (e.g., BCH from BTC) treated as new assets, not
  same-symbol price continuation.
- **Row-level source id required.** Anonymous rows are invalid.
- **File hash on freeze:** every frozen dataset records a sha256 of each
  file at the time of freeze.
- **Contract version pinned per dataset.**
- **Quote currency declared explicitly** per series.
- **Stablecoin cross-handling:** USDT / USDC / USD conversions require an
  explicit FX series with a documented method.

## 9. Missing-data and duplicate rules

- **No silent forward-fill.**
- **Missing day** is flagged in the manifest; missing close / missing
  timestamp / missing source id rows are invalid.
- **Partial-day bars excluded** from frozen datasets.
- **Outage calendar attached** to the manifest when source outage history
  is available.
- **Duplicate `(symbol, timestamp)` rejected.**
- **Out-of-order rows flagged.**
- **Strictly monotonic per symbol** required.

## 10. Minimum viable dataset

- **At least 3 years of daily OHLCV per asset** to support IS + sealed OOS
  windows with reasonable trade counts. 5+ years preferred when available
  (BTC ~12y, ETH ~8y, SOL ~5y at v1).
- **BTC required**; ETH and SOL recommended.
- **Single source per asset** for the full series; cross-venue stitching
  only with documented stitching rules.
- **Frozen sha256 required.**
- **Manifest required.**
- **Contract version pinned.**
- **QA report required before use.**
- **IS window sealed before run.** **OOS window sealed before run.**
- **Provenance per row.**
- **Warmup buffer documented.**
- **Fee schedule attached.**
- **Outage calendar attached** when available.

## 11. Future allowed data sources

1. Existing on-disk frozen historical files already present in SPARTA's
   research tree (NO network call from this contract's runtime).
2. A future, **SEPARATELY** authorized data-acquisition bundle (Protocol
   P2) which itself ships its own data-acquisition memo and explicit
   operator authorization.
3. Operator-supplied paid-vendor exports that DO NOT require a live API
   connection from SPARTA itself (vendor pushes files; SPARTA reads them
   offline).

## 12. Forbidden data sources or methods

- Live exchange APIs called from this contract's runtime.
- Scraping any venue HTML / WebSocket / undocumented endpoint from this
  contract's runtime.
- Any data source requiring an embedded API key, OAuth token, or `.env`
  credential.
- Any data source that requires SPARTA to MAKE a network call from its
  runtime.
- Any synthetic / mock-priced data used in place of real historical data
  for any evidence claim.
- Any dataset whose provenance cannot be cited line-by-line.
- Any dataset that has been peeked at in its OOS window before sealing.
- Any feed whose terms of service forbid research use.

## 13. PASS / WATCH / FAIL rules

- **PASS** — every required section of this contract is populated for the
  dataset; QA report shows zero unresolved flags; fee + slippage +
  stablecoin assumptions are non-null and sourced; IS / OOS windows were
  sealed before any run; OHLCV self-consistency passes per row; missing-day
  list and outage overlay are attached.
- **WATCH** — contract is satisfied but at least one assumption is
  borderline (short history on one asset, marginal QA flags accepted by
  the operator), or only one asset (BTC) is present; the dataset is
  documented and re-checked before any further phase.
- **FAIL** — any required section is missing; any forbidden data source
  was used; any safety flag is True; any OOS window was peeked; the OHLCV
  self-consistency check fails; or the dataset cannot be reproduced
  bit-for-bit.

## 14. Required future artifacts

- **Crypto-D1 Dataset Manifest v1** (P2) — per-dataset manifest schema for
  the crypto-D1 lane (spec only, no fetch).
- **Crypto-D1 Data QA / Freeze Spec v1** (P2) — QA harness spec for
  daily-crypto datasets (spec only, no harness execution).
- **Per-dataset data acquisition memo** — names source / venue / time-window
  / storage path before any data pull.
- **Per-dataset data integrity report** (P2 OUTPUT) — row counts,
  missing-day list, outage overlay, fee schedule attached, contract version
  pinned.
- **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-registration memo
  for the FIRST strategy family + IS / OOS split (plan only, no backtest
  run).
- **Backtest report.json + report.md** with PASS / WATCH / FAIL verdict per
  the Crypto-D1 Protocol Memo v1 rules.
- **Lane closeout memo** if a strategy family PARKs / RETIREs.

## 15. No-profit-claim policy

- **This contract does not imply edge.**
- **Clean OHLCV data does not imply profit.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**
- **No data fetch is authorized by this contract.**
- **No backtest is authorized by this contract alone.**
- **No paper or live trading is authorized by this contract.**

## 16. Safety boundaries (pinned, non-negotiable)

- Research-only. Data contract / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  contract's runtime.
- **No data fetch. No backtest. No dataset processing in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this contract alone.
- **Crypto trend ideas are not profitable until tested with full costs.**
  **A good historical chart does not imply future returns.**
  **Clean OHLCV data does not imply profit.**
  **No backtest is authorized by this contract alone.**
