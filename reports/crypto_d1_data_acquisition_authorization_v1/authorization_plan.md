# SPARTA Crypto-D1 Local Data Acquisition Authorization / Freeze Plan v1

> **Research-only. Authorization / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest
> execution. No dataset processing. No real dataset files or data directory
> created in this bundle.** This document defines exactly what the operator
> must MANUALLY provide later, WHERE it should go, and WHICH checks must
> pass before the Crypto-D1 Backtest Runner v1 is allowed to use it.

**Authorization plan id:** `crypto_d1_data_acquisition_authorization_v1`
· **version:** `1.0`

**Companion documents (read-only references):**
- `reports/crypto_d1_protocol_v1/protocol.{json,md}` — protocol (Bundle 11).
- `reports/crypto_d1_data_contract_v1/data_contract.{json,md}` — data contract (Bundle 12).
- `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.{json,md}` — dataset manifest spec (Bundle 13).
- `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.{json,md}` — QA / freeze spec (Bundle 14).
- `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.{json,md}` — backtest plan (Bundle 15).
- `tools/crypto_d1_backtest_runner.py` — runner (Bundle 16).

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (all required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Allowed market type:** `spot` only.
- **Forbidden market types:** perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic
  instruments.

## 2. Approved data scope

| Field | Value |
|---|---|
| Assets | BTC, ETH, SOL |
| Market type | spot only |
| Timeframe | daily candles only (`1d`) |
| Quote currency | USDT or USD (operator-chosen; **must be consistent and documented** per series) |
| Source | operator-approved historical OHLCV CSV provider (offline export only) |
| Time range | operator-chosen; **must be recorded exactly** in the per-dataset manifest's `time_start` / `time_end` |
| Perps / dated futures / options / leveraged tokens / margin spot / synthetic instruments | **FORBIDDEN** |
| Intraday data in this bundle | **FORBIDDEN** |
| Synthetic / mock data, screenshots, manually-typed prices | **FORBIDDEN** |

## 3. Operator manual steps (12 steps; all MANUAL)

1. **Operator MANUALLY selects an approved historical OHLCV CSV source**
   whose terms of service explicitly permit research use. NO automated
   discovery.
2. **Operator MANUALLY exports / downloads daily OHLCV CSV files** for
   BTC, ETH, SOL (whichever subset is in scope) under the operator's own
   credentials; SPARTA's runtime never sees those credentials.
3. **Operator MANUALLY normalizes the CSV(s)** so that the file header
   matches the Bundle 12 `required_csv_schema` EXACTLY (column names,
   casing, UTF-8 encoding, no BOM).
4. **Operator MANUALLY mints a `dataset_id`** matching the pattern
   `CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>` and a monotonic
   `dataset_version` (`V001`, `V002`, …).
5. **Operator MANUALLY places the CSV file(s)** at the declared
   `storage_path_plan` (`data/crypto_d1_research/<dataset_id>/<dataset_version>/`).
   No network call is made by SPARTA.
6. **Operator MANUALLY authors a per-dataset `manifest.json`** that
   satisfies `tools/crypto_d1_dataset_manifest_check.py` (extended for
   per-dataset use) and pins `protocol_version`,
   `data_contract_version`, `manifest_version`.
7. **Operator MANUALLY computes sha256** of every file in the dataset
   folder and writes them to `CHECKSUMS.txt`.
8. **Operator MANUALLY writes `FREEZE_RECORD.txt`** recording freeze
   timestamp (ISO-8601 UTC), operator name + tool label, and the
   pinned protocol + data_contract + manifest + qa-spec versions.
9. **Operator MANUALLY runs the future QA harness** (Bundle 14 spec)
   once it is implemented, and reviews `qa_report.json`.
10. **Operator MANUALLY accepts `QA_PASS`**, or attaches an explicit
    operator-acceptance note for `QA_WARN`, before authorizing the
    runner.
11. **Operator MANUALLY runs the backtest runner** against the FROZEN,
    QA-approved dataset:
    ```bash
    python tools/crypto_d1_backtest_runner.py run \
        --data-dir <PATH_TO_DATASET_FOLDER> \
        --out-dir  <PATH_TO_OUT_DIR>
    ```
12. **Operator MANUALLY reviews** the runner's emitted
    `crypto_d1_backtest_report.json` + `.md` (research-only). The
    runner NEVER emits PASS in v1, so any acted-upon decision is the
    operator's explicit judgment AFTER review.

## 4. Required CSV schema

### Required columns (must match Bundle 12 exactly)

`timestamp`, `open`, `high`, `low`, `close`, `volume`, `symbol`,
`source`, `quote_currency`.

### Optional columns

`vwap`, `trade_count`, `quote_volume`, `source_timestamp`,
`ingestion_timestamp`.

### Format rules

- UTF-8 (no BOM).
- One row per `(symbol, UTC daily timestamp)`.
- No partial-day bars allowed in a frozen dataset.
- No silent forward-fill — missing days flagged in the manifest's
  `missing_day_list`.
- Column names / casing / order **must match exactly**; the backtest
  runner rejects files whose header is missing any required column.

## 5. Expected file layout (placeholders only — NO real files created)

A future operator-supplied dataset folder is expected to contain:

| Filename | Purpose |
|---|---|
| `BTC_daily.csv` | Per-asset daily OHLCV CSV (BTC). |
| `ETH_daily.csv` | Per-asset daily OHLCV CSV (ETH). |
| `SOL_daily.csv` | Per-asset daily OHLCV CSV (SOL). |
| `manifest.json` | Per-dataset manifest; must pass `tools/crypto_d1_dataset_manifest_check.py`. |
| `CHECKSUMS.txt` | One `<sha256_hex>  <filename>` line per dataset file. |
| `FREEZE_RECORD.txt` | Freeze timestamp + operator + tool label + pinned versions. |
| `qa_report.json` | QA harness output; populates all 26 fields from `crypto_d1_qa_freeze_spec_v1.QA_report_schema.required_fields`. |

**No real files are created in this bundle. No data directory is
created in this bundle.**

## 6. Storage path plan

- **Root pattern:** `data/crypto_d1_research/<dataset_id>/<dataset_version>/`
- **No real storage directory is created** in this bundle.
- **No URLs.** All paths are local repo-relative; no `s3://`, `gs://`,
  `http(s)://`, `ftp://`, `file://remote-host`, or other remote scheme
  is permitted in any future per-dataset manifest.
- **Storage root appears only when the operator manually places a real
  dataset.** Even the parent directory `data/crypto_d1_research/` is
  NOT created by this authorization plan.
- **Gitignore recommendation:** if real OHLCV data is later acquired,
  add `data/crypto_d1_research/` to `.gitignore` unless the operator
  explicitly wants to track frozen datasets in git (typically not
  recommended for size + provenance reasons).

## 7. Manifest requirements

- Must validate against `tools/crypto_d1_dataset_manifest_check.py`
  (Bundle 13).
- Must reference:
  - `protocol_version` = `crypto_d1_protocol_v1` (or later)
  - `data_contract_version` = `crypto_d1_data_contract_v1` (or later)
  - `qa_freeze_spec_version` = `crypto_d1_qa_freeze_spec_v1` (or later)
  - `backtest_plan_version` = `crypto_d1_baseline_backtest_plan_v1`
    (or later)
  - `runner_version` = `crypto_d1_backtest_runner_v1` (or later)
- `dataset_id` matches `CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`.
- `dataset_version` is monotonic; **no in-place edits**; every change
  creates a new `dataset_version`.
- **Anonymous provenance is invalid.**

## 8. QA / freeze requirements

- Must follow `reports/crypto_d1_qa_freeze_spec_v1/` (Bundle 14).
- `QA_status` must be **`QA_PASS`** OR **`QA_WARN`** with an explicit
  operator-acceptance note.
- `QA_FAIL` and `QA_BLOCKED` **block runner use**.
- Required blocking checks present in `checks_passed`:
  - **A** — manifest integrity
  - **B** — timestamp (UTC, no weekday-only, no duplicate, no silent
    forward-fill)
  - **C** — OHLCV (positive OHLC; `high >= max(o, c, l)`;
    `low <= min(o, c, h)`; close not missing)
  - **D** — volume (non-negative; zero-volume policy applied)
  - **E** — symbol-source (BTC/ETH/SOL canonical; quote_currency
    consistency; row-level `source_id`)
  - **F** — fee + slippage assumptions present + sourced
  - **G** — freeze (FROZEN; `CHECKSUMS.txt` sha256-verified;
    `FREEZE_RECORD.txt` present)
- The QA harness's **`no_lookahead`** check must be in `checks_passed`.

## 9. Checksum requirements

- **sha256 per file required.**
- `CHECKSUMS.txt` format: one line per file
  `<sha256_hex>  <relative_filename>`.
- Checksums must match at runner startup; the backtest runner (or its
  future per-dataset validator) MUST verify each file's current sha256
  equals the recorded `CHECKSUMS.txt` entry before any backtest result
  is produced.
- `FREEZE_RECORD.txt` format: plain-text key:value lines including
  `freeze_timestamp_utc`, `operator`, `protocol_version`,
  `data_contract_version`, `manifest_version`,
  `qa_freeze_spec_version`, `backtest_plan_version`, `runner_version`.
- Any revision creates a new `dataset_version`.
- Manual edits invalid unless documented + revalidated.

## 10. Forbidden actions

- Fetch data from any live exchange API.
- Connect SPARTA's runtime to any exchange or vendor over the network.
- Use an embedded API key, OAuth token, or `.env` credential.
- Use any private key or exchange account credential.
- Scrape any venue HTML / WebSocket / undocumented endpoint.
- Use any cloud fetcher (`s3://`, `gs://`, `http(s)://`, `ftp://`,
  `file://remote-host`) as a source.
- Install or schedule any daemon / cron / background job to perform
  acquisition.
- Run the backtest runner from this bundle.
- Modify paper / live execution files.
- Promote `crypto_d1_protocol` to ACTIVE / STRONG by this bundle's
  existence alone.
- Use any synthetic / mock-priced data as evidence.
- Send a Telegram / email / Slack notification from this bundle's
  runtime.

## 11. Approval gates (20 gates; ALL required before runner use)

1. Explicit written operator authorization BEFORE any data acquisition
   step is performed.
2. Exact source named (vendor / venue / archive name) in the manifest's
   `source_name`.
3. Exact symbols named (subset of `{BTC, ETH, SOL}`) in
   `manifest.assets`.
4. Exact time window named (`time_start`, `time_end` — both ISO-8601
   UTC).
5. Exact storage path named (`data/crypto_d1_research/<dataset_id>/<dataset_version>/`).
6. Exact `dataset_id` named (`CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`).
7. `data_contract_version` pinned (`crypto_d1_data_contract_v1` or later).
8. `dataset_manifest_spec_version` pinned (`crypto_d1_dataset_manifest_v1` or later).
9. `qa_freeze_spec_version` pinned (`crypto_d1_qa_freeze_spec_v1` or later).
10. `protocol_version` pinned (`crypto_d1_protocol_v1` or later).
11. `CHECKSUMS.txt` created with sha256 per file.
12. `FREEZE_RECORD.txt` created with freeze timestamp + operator +
    pinned versions.
13. `manifest.json` created and passes
    `tools/crypto_d1_dataset_manifest_check.py`.
14. QA / freeze `qa_report.json` created and passes the Bundle 14 spec.
15. `QA_status` is **`QA_PASS`** OR (**`QA_WARN`** with an explicit
    operator-acceptance note attached).
16. **No credentials of any kind** embedded in the dataset, manifest,
    or supporting files.
17. **No trading permissions, exchange-account references, or
    order-routing identifiers** anywhere in the dataset.
18. **No live trading authorization.**
19. **No paper-order execution authorization.**
20. **No broker connection authorization.**

## 12. Allowed next steps

- Operator manually executes the 12 operator manual steps above; no
  SPARTA-side automation is invoked.
- Operator runs `python tools/crypto_d1_backtest_runner.py validate-config`
  to confirm cost bounds.
- Operator runs `python tools/crypto_d1_backtest_runner.py show-plan`
  to review the pre-registered plan.
- Operator runs
  `python tools/crypto_d1_backtest_runner.py run --data-dir <PATH> --out-dir <PATH>`
  against the FROZEN, QA-approved dataset; emitted JSON + MD reports
  are research-only.
- Author **Crypto-D1 Baseline Results Report v1** AFTER the operator
  has manually supplied data AND the runner has produced output
  (separately authorized).
- Optionally author **Crypto-D1 Data QA Runtime Tool v1** if the
  operator decides the QA runner must exist as code before any further
  backtest (code bundle; recommend Codex).

## 13. Forbidden next steps

- Trade live or paper based on a future runner output.
- Connect SPARTA's runtime to any exchange or vendor over the network.
- Promote `crypto_d1_protocol` to ACTIVE / STRONG without a separate
  operator decision.
- Schedule a daemon / cron / background process that touches the runner.
- Modify paper / live execution files.
- Install or read any API key, OAuth token, or `.env` credential.
- Use any synthetic / mock-priced data as evidence.
- Commit large frozen datasets to git without explicit operator
  instruction; the storage root is expected to be gitignored by
  default.

## 14. No-profit-claim policy

- **Data acquisition does not imply edge.**
- **Clean data does not imply profit.**
- **Running the backtest does not authorize trading.**
- **Backtest output will still require separate review.**
- **No paper/live trading is authorized.**
- **No data fetch is authorized by this bundle.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**

## 15. Required future artifacts

- Per-dataset `manifest.json` conforming to Bundle 13 schema.
- Per-dataset `CHECKSUMS.txt` with sha256 per file.
- Per-dataset `FREEZE_RECORD.txt` with freeze timestamp + operator +
  pinned versions.
- Per-dataset `qa_report.json` conforming to Bundle 14
  `QA_report_schema` (26 required fields).
- Per-strategy backtest `report.json` + `report.md` emitted by
  `tools/crypto_d1_backtest_runner.py` after the operator runs the
  runner against the FROZEN dataset.
- **Crypto-D1 Baseline Results Report v1** (separately authorized;
  only after operator has supplied data and the runner has produced
  output).
- Optional: **Crypto-D1 Data QA Runtime Tool v1** (code bundle; only
  if the operator decides the QA runner must exist as code before any
  further backtest; recommend Codex).

## 16. Safety boundaries (pinned, non-negotiable)

- Research-only. Authorization / specification only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  plan's runtime.
- **No data fetch. No backtest execution. No dataset processing. No
  real dataset files or data directory created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this authorization plan alone.
- **Data acquisition does not imply edge. Clean data does not imply
  profit. Running the backtest does not authorize trading. Backtest
  output will still require separate review. No paper/live trading is
  authorized. Crypto trend ideas are not profitable until tested with
  full costs AND forward-validated under a separately authorized
  future plan. A good historical chart does not imply future returns.
  24/7** crypto session handling; weekday-only filters forbidden.
