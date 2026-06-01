# SPARTA Crypto-D1 Dataset Manifest v1

> **Research-only. Dataset manifest / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest.
> No dataset processing in this bundle. No real dataset files are created in
> this bundle.** This document defines how any future BTC / ETH / SOL daily
> OHLCV dataset will be DECLARED, FROZEN, VERSIONED, QA-checked, and
> REFERENCED before any Crypto-D1 backtest is allowed.

**Dataset manifest spec id:** `crypto_d1_dataset_manifest_v1` ·
**version:** `1.0`

**Companion documents (read-only references):**
- `reports/crypto_d1_protocol_v1/protocol.md` — the protocol this manifest
  spec serves (BTC / ETH / SOL spot, daily, 24/7).
- `reports/crypto_d1_protocol_v1/protocol.json` — machine-readable protocol.
- `reports/crypto_d1_data_contract_v1/data_contract.md` — the data contract
  this manifest spec extends (column schema, OHLCV quality rules,
  fees/slippage, freeze rules, missing/duplicate rules).
- `reports/crypto_d1_data_contract_v1/data_contract.json` — machine-readable
  data contract.

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol` (same lane as the protocol + data
  contract).
- **Target assets:** **BTC** (required), **ETH** (required), **SOL**
  (required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of
  scope**.
- **Allowed market type:** `spot` only.
- **Forbidden market types:** perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic
  instruments.

Perps and intraday remain separately-future protocols (see Crypto-D1
Protocol v1, Bundle 11).

## 2. Future manifest schema (35 required fields)

Every future Crypto-D1 per-dataset `manifest.json` MUST populate all 35
of the following fields. Missing any one of them is a **FAIL** verdict.

| # | Field | Required value / shape |
|--:|---|---|
| 1 | `dataset_id` | Immutable id matching `CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`; never reused. |
| 2 | `dataset_version` | Monotonic `V001` / `V002` / … or integer; bumped on any change. |
| 3 | `created_at` | ISO-8601 UTC. |
| 4 | `created_by` | Operator + tool label; never anonymous. |
| 5 | `research_lane` | Must be `crypto_d1_protocol`. |
| 6 | `market_type` | Must be `spot`. |
| 7 | `assets` | Subset of `{BTC, ETH, SOL}`; BTC required. |
| 8 | `symbols` | Per-venue symbol map. |
| 9 | `quote_currency` | Per-series quote currency (USD / USDT / USDC / etc.). |
| 10 | `timeframe` | Must be `1d`. |
| 11 | `time_start` | ISO-8601 UTC date (inclusive). |
| 12 | `time_end` | ISO-8601 UTC date (inclusive, fully-closed bar). |
| 13 | `timezone` | Must be `UTC`. |
| 14 | `bar_boundary` | Must be `UTC 00:00:00 close; left-closed / right-open`. |
| 15 | `data_frequency` | Must be `daily`. |
| 16 | `source_type` | One of `on_disk_frozen_file` / `operator_supplied_paid_vendor_offline_export` / `future_separately_authorized_acquisition_bundle`. |
| 17 | `source_name` | Vendor / venue; never anonymous. |
| 18 | `source_location` | Local repo-relative path. No URLs. |
| 19 | `data_contract_version` | Must reference `crypto_d1_data_contract_v1` (or later). |
| 20 | `protocol_version` | Must reference `crypto_d1_protocol_v1` (or later). |
| 21 | `checksum_policy` | sha256-per-file; recorded in `CHECKSUMS.txt`. |
| 22 | `row_count_expected` | Integer derived from (time_end − time_start) per asset, less `missing_day_list`. |
| 23 | `row_count_actual` | Integer actual; mismatch must be explained by `missing_day_list`. |
| 24 | `missing_day_policy` | `flagged in manifest; never silently forward-filled`. |
| 25 | `duplicate_policy` | `duplicate (symbol, timestamp) rejected`. |
| 26 | `partial_day_policy` | `partial-day bars excluded from frozen dataset`. |
| 27 | `zero_volume_policy` | Flagged for review; never silently kept without explicit outage / illiquidity explanation. |
| 28 | `outlier_policy` | Flagged not dropped. |
| 29 | `normalization_policy` | Per-series quote currency + stablecoin cross + tick/lot + alias-mapping policy. |
| 30 | `fee_slippage_assumption_reference` | Pointer to `fees.json` pinning maker/taker, slippage, spread proxy. |
| 31 | `freeze_status` | `DRAFT` or `FROZEN`; only `FROZEN` may be referenced by a backtest. |
| 32 | `QA_status` | One of `DRAFT` / `QA_PASS` / `QA_WARN` / `QA_FAIL` / `RETIRED` / `BLOCKED`. |
| 33 | `allowed_use` | Explicit list (e.g., pre-registered offline backtests). |
| 34 | `forbidden_use` | Explicit list (no live trading, no paper-order, no broker, no data fetch from this manifest). |
| 35 | `notes` | Human notes / caveats / revision reasons. |

## 3. Dataset identity + provenance

- **Immutable `dataset_id`.** Once minted, a `dataset_id` never points
  at different content. Any content change requires a NEW
  `dataset_version` (or a new `dataset_id` if scope changes).
- **Monotonic `dataset_version`.** `V001` → `V002` → … In-place edits
  are forbidden.
- **Source provenance.** `source_type`, `source_name`, and
  `source_location` are all required. Anonymous provenance is invalid.
- **Source location rules.** Local repo-relative path; **no URLs**;
  every dataset lives under
  `data/crypto_d1_research/<dataset_id>/<dataset_version>/`.
- **Checksum / hashing.** Every frozen dataset records a sha256 of
  each file at the time of freeze in `CHECKSUMS.txt`. Any subsequent
  diff invalidates the freeze.
- **Row count expectations.** `row_count_expected` is computed from
  (`time_end` − `time_start`) per asset less the manifest's
  `missing_day_list`; mismatch with `row_count_actual` must be
  explained.
- **Created timestamps.** `created_at` (manifest authored) and the
  freeze timestamp inside `FREEZE_RECORD.txt` are both required.
- **Created by.** Operator name + tool label, never anonymous.
- **Invalid dataset** — any of the 35 required fields missing, any
  safety flag True, any reference to a non-existing
  contract/protocol artifact, sha256 mismatch, OHLCV
  self-consistency failure, `QA_status = QA_FAIL` or `BLOCKED`.
- **Frozen dataset** — `freeze_status = FROZEN`, `CHECKSUMS.txt`
  recorded, `FREEZE_RECORD.txt` recorded, no in-place edits.
- **Untrusted dataset** — `QA_status = QA_WARN` without an explicit
  operator-acceptance note; `QA_status = BLOCKED`; checksum mismatch;
  any unresolved manifest field.

## 4. Crypto-D1-specific freeze rules

- **No Crypto-D1 backtest may use mutable / unfrozen data.**
- **Every dataset must have a manifest.**
- **Every manifest must pass validation** (validator below).
- **Every dataset must reference Crypto-D1 Protocol v1 and Data
  Contract v1** (or later versions) via `protocol_version` and
  `data_contract_version`.
- **Every dataset must carry a `QA_status`** from the declared model.
- **Every future backtest must cite `dataset_id` and `dataset_version`.**
- **Changing data creates a new `dataset_version`.**
- **Manually edited data is invalid unless explicitly documented and
  revalidated** under a new `dataset_version`.
- **Daily bars must be UTC-normalized.**
- **Weekday-only calendars are forbidden.**

## 5. QA status model

| Status | When it applies |
|---|---|
| **DRAFT** | Manifest authored but not yet sealed; row counts may shift; not usable for any downstream artifact. |
| **FROZEN** | Manifest sealed; underlying files are sha256-pinned in `CHECKSUMS.txt`; `FREEZE_RECORD.txt` recorded; no in-place edits allowed. |
| **QA_PASS** | FROZEN + QA harness completed with zero unresolved flags; dataset is research-eligible for a pre-registered backtest plan. |
| **QA_WARN** | FROZEN + QA harness raised one or more non-blocking warnings (e.g., borderline outage overlap, marginal asset history). Operator may accept `QA_WARN` ONLY with a written acceptance note attached to the manifest; lane stays **WATCH** on usage. |
| **QA_FAIL** | QA harness raised a blocking finding (e.g., self-consistency failed, OOS window peeked, irrecoverable gaps). Dataset **MUST NOT** be referenced by any backtest plan; remediation requires a new `dataset_version`. |
| **RETIRED** | Dataset was previously usable but has been superseded by a newer version; the retired version is read-only and used only for reproducibility / audit. |
| **BLOCKED** | External block exists (vendor TOS dispute, legal / compliance flag, operator hold). Dataset **MUST NOT** be referenced until the block is cleared. |

## 6. File formats and storage conventions

### Allowed future file formats

- **CSV** (UTF-8, header row, comma-separated, no BOM, LF or CRLF
  declared).
- **Parquet** (columnar; schema declared alongside).
- **JSON manifest** (`manifest.json` itself).
- **Markdown report** (e.g., `qa_report.md`, `README.md`).

### Forbidden inputs

- screenshots
- manually copied prices
- unstable web-scraped tables
- mutable notebooks as source of truth (notebook outputs may be
  exported into a frozen CSV / Parquet, but the notebook itself is
  not the source of truth)
- files without provenance
- files without checksums
- files without a manifest
- files referencing private keys or credentials

### Future naming examples (placeholders only — **no real files are
created in this bundle**)

- Example `dataset_id`s:
  - `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001`
  - `CRYPTO_D1_SPOT_BTC_V001`
  - `CRYPTO_D1_SPOT_BTC_ETH_SOL_V002`
- Standard filenames inside a future dataset folder:
  - `manifest.json`
  - `daily_ohlcv.csv`
  - `qa_report.json`
  - `CHECKSUMS.txt`
  - `FREEZE_RECORD.txt`

### Future storage root

`data/crypto_d1_research/<dataset_id>/<dataset_version>/` — local
only; no URLs.

## 7. No-profit-claim policy

- **Dataset manifest approval does not imply edge.**
- **QA_PASS does not imply profitability.**
- **Clean daily OHLCV data does not imply profit.**
- **A manifest cannot authorize backtesting by itself.**
- **A manifest cannot authorize paper or live trading.**
- **No data fetch is authorized by this bundle.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**

## 8. PASS / WATCH / FAIL rules

- **PASS** — All 35 manifest_schema `required_fields` populated; all
  7 safety flags False; `lane == "crypto_d1_protocol"`;
  `market_type == "spot"`; `timeframe == "1d"`;
  `data_contract_version` and `protocol_version` reference existing
  on-disk artifacts; `freeze_status == "FROZEN"` with a matching
  `FREEZE_RECORD.txt`; `CHECKSUMS.txt` sha256-verified per file;
  `QA_status` is `QA_PASS` OR (`QA_WARN` with an explicit
  operator-acceptance note); `allowed_use` and `forbidden_use` both
  populated.
- **WATCH** — Manifest is FROZEN and validates, but `QA_status` is
  `QA_WARN` with an explicit operator-acceptance note, OR only BTC is
  present, OR history is shorter than the preferred 5 years on one
  asset. Lane stays WATCH on this dataset's downstream use.
- **FAIL** — Any of the 35 required fields missing; any safety flag
  True; `freeze_status != "FROZEN"` while referenced by a backtest
  plan; `QA_status` is `QA_FAIL` or `BLOCKED`; sha256 mismatch;
  `FREEZE_RECORD.txt` missing; lane mismatch;
  `market_type != "spot"`; `timeframe != "1d"`; manual edits in
  place without documented re-validation.

## 9. Required future artifacts

- **Crypto-D1 Data QA / Freeze Spec v1** (P2) — QA harness spec for
  daily-crypto data; spec only, no harness run.
- **Crypto-D1 Data Source Evaluation Memo v1** — written assessment
  of which offline data sources could later satisfy this manifest
  (memo only, no fetch).
- **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-
  registration memo for the FIRST candidate strategy family + IS /
  OOS split (plan only, no backtest run).
- **Per-dataset data acquisition memo** — names source / venue /
  symbols / time-window / storage path before any data pull.
- **Per-dataset data integrity report** (P2 OUTPUT) — row counts,
  missing-day list, outage overlay, fee schedule attached, contract
  version pinned.
- **Backtest report.json + report.md** with PASS / WATCH / FAIL
  verdict per the Crypto-D1 Protocol Memo v1 rules.
- **Lane closeout memo** if a strategy family PARKs / RETIREs.

## 10. Safety boundaries (pinned, non-negotiable)

- Research-only. Dataset manifest / specification only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in
  this manifest's runtime.
- **No data fetch. No backtest. No dataset processing. No real
  dataset files created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this manifest spec alone.
- **Dataset manifest approval does not imply edge.**
  **QA_PASS does not imply profitability.**
  **Clean daily OHLCV data does not imply profit.**
  **A manifest cannot authorize backtesting by itself.**
  **A manifest cannot authorize paper or live trading.**
  **Crypto trend ideas are not profitable until tested with full
  costs.**
  **A good historical chart does not imply future returns.**
  **24/7** crypto session handling; weekday-only filters forbidden.
