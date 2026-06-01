# SPARTA Crypto-D1 Data QA / Freeze Spec v1

> **Research-only. Data QA / freeze specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No QA
> harness execution. No backtest. No dataset processing. No real dataset
> files are created in this bundle.** This document defines exactly how any
> future BTC / ETH / SOL daily OHLCV dataset will be VALIDATED, FROZEN, and
> APPROVED before any Crypto-D1 backtest is allowed.

**QA / freeze spec id:** `crypto_d1_qa_freeze_spec_v1` · **version:** `1.0`

**Companion documents (read-only references):**
- `reports/crypto_d1_protocol_v1/{protocol.md, protocol.json}` — protocol.
- `reports/crypto_d1_data_contract_v1/{data_contract.md, data_contract.json}` — data contract.
- `reports/crypto_d1_dataset_manifest_v1/{dataset_manifest.md, dataset_manifest.json}` — dataset manifest spec.

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (all required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Allowed market type:** `spot` only.
- **Forbidden market types:** perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic
  instruments.

## 2. Required inputs (every future QA harness run consumes these)

1. A per-dataset `manifest.json` that already passes
   `crypto_d1_dataset_manifest_check.py` and references
   `crypto_d1_protocol_v1` + `crypto_d1_data_contract_v1`.
2. An on-disk daily OHLCV file (CSV or Parquet only) at the location
   declared by the manifest's `source_location`.
3. A `CHECKSUMS.txt` with sha256 per file; SHA verified against the
   file contents before any check runs.
4. A `FREEZE_RECORD.txt` with freeze timestamp, operator, contract +
   protocol versions pinned.
5. A `fees.json` (or equivalent) pinning per-venue maker / taker
   fees, slippage assumption, spread proxy.

## 3. Forbidden inputs

- Live exchange API calls from this QA harness's runtime.
- Scraping HTML / WebSocket / undocumented endpoints.
- Any input requiring an API key, OAuth token, or `.env` credential.
- Any input that requires SPARTA to MAKE a network call from its
  runtime.
- Synthetic / mock-priced data.
- Screenshots; manually copied prices.
- Files without provenance / checksums / a manifest.
- Datasets whose OOS window has been peeked before sealing.
- Feeds whose terms of service forbid research use.

## 4. QA check groups (A–G)

### A — Manifest integrity

- Manifest exists and is well-formed.
- `dataset_id` and `dataset_version` present.
- `protocol_version` references an existing protocol artifact.
- `data_contract_version` references an existing data-contract
  artifact.
- Source fields present (`source_type`, `source_name`,
  `source_location`).
- `allowed_use` and `forbidden_use` present.
- `freeze_status` present.
- `QA_status` present.

### B — Timestamp checks

- UTC timestamps required (ISO-8601 in storage).
- Daily bar boundary is UTC 00:00:00; left-closed / right-open.
- No weekday-only calendar (24/7 spot-crypto only).
- No duplicate timestamps per symbol.
- Missing-day rules: flagged in manifest; **never silently
  forward-filled**.
- Partial-day handling: partial-day bars excluded from a frozen
  dataset; only fully-closed UTC bars valid.
- Timezone normalization: all stored timestamps UTC; original
  timezone preserved as metadata when source delivered local time.
- `source_timestamp` vs `ingestion_timestamp`: if both available, both
  stored; `source_timestamp` is the primary key.

### C — OHLCV checks

- `open`, `high`, `low`, `close` all **positive**.
- `high >= max(open, close, low)`.
- `low <= min(open, close, high)`.
- `close` not missing.
- Suspicious high-low range flagged (per-asset rolling-vol-aware
  band).
- Extreme gap / outlier flag (day-over-day return beyond per-asset
  threshold).
- Impossible-candle rules: `high < low` is **FAIL**; OHLC-all-equal
  with non-zero volume flagged; price drop > X% with zero volume
  flagged.
- OHLCV self-consistency check **required before freeze**.

### D — Volume checks

- `volume >= 0`.
- Zero-volume bars on a 24/7 asset highly suspicious; flagged for
  review; never silently kept in a frozen dataset without an explicit
  outage / illiquidity explanation.
- `quote_volume` consistency if present: `volume * vwap ≈
  quote_volume` documented and per-row deviations flagged.
- Suspicious volume outlier flag (per-asset rolling-volume-aware
  band).
- Missing-volume handling: row flagged; if a future test treats
  missing-volume rows as zero, the choice is documented in the
  manifest's `notes`.

### E — Symbol / source checks

- BTC / ETH / SOL canonical mapping; BTC at minimum.
- `quote_currency` consistency per symbol.
- Source consistency per dataset (cross-venue stitching only with
  documented rules).
- Duplicate `(symbol, source, timestamp)` rows are **FAIL**.
- Row-level provenance (`source_id`) required.
- Rename / fork events first-class manifest events; never silently
  re-mapped.

### F — Fee / slippage checks

- Fee assumptions present (per-venue maker / taker fees, dated,
  declared).
- Slippage assumptions present (conservative slow-day haircut +
  one-tick).
- Spread proxy declared when quote data is absent.
- Cost-sensitivity requirement: no **PASS** without a cost-
  sensitivity test (fees ±N bps, slippage ±M bps) showing the
  verdict survives.
- **No PASS if fees or slippage are missing.**
- Stablecoin quote-currency conversions documented and explicit.
- Fees as a distinct PnL line required.

### G — Freeze checks

- Dataset cannot be used until `freeze_status == FROZEN`.
- Freeze timestamp required (`FREEZE_RECORD.txt`).
- Checksums required (`CHECKSUMS.txt`, sha256 per file).
- Row counts recorded; mismatch with `row_count_expected` must be
  explained by the manifest's `missing_day_list`.
- Data revision creates a new `dataset_version`.
- Manual edits require documentation **and** re-validation under a
  new `dataset_version`.

## 5. QA status model (6 statuses)

| Status | When it applies |
|---|---|
| **QA_DRAFT** | QA harness has not yet been run on this `dataset_version`, OR a required input was missing. Not eligible for any downstream use. |
| **QA_PASS** | All blocking checks passed; zero unresolved warnings; per-asset row counts match manifest (modulo `missing_day_list`); cost-sensitivity test passed; `freeze_status == FROZEN`; `CHECKSUMS.txt` sha256-verified per file; `FREEZE_RECORD.txt` present. Dataset is research-eligible for a pre-registered backtest plan. |
| **QA_WARN** | No blocking failures, but at least one non-blocking warning was raised (borderline outage overlap, marginal asset history, an outlier cluster below the FAIL threshold). Operator MUST attach a written acceptance note to the manifest before the dataset may be referenced; the lane stays **WATCH** on downstream usage. |
| **QA_FAIL** | At least one blocking check failed (self-consistency violation, OHLCV impossible-candle, sha256 mismatch, missing `FREEZE_RECORD.txt`, OOS window peeked, manual edit without re-validation). Dataset MUST NOT be referenced; remediation requires a new `dataset_version`. |
| **QA_BLOCKED** | External block exists (vendor TOS dispute, legal / compliance flag, operator hold). Dataset MUST NOT be referenced until cleared, even if all checks would otherwise pass. |
| **QA_RETIRED** | Dataset was previously usable but has been superseded by a newer version; the retired version is read-only and used only for reproducibility / audit. |

### Distinction statements

- **QA_PASS does not imply profitability.**
- **QA_PASS does not authorize a backtest by itself.**
- **QA_PASS does not authorize paper or live trading.**
- **QA_FAIL blocks all research use.**
- **QA_WARN requires explicit operator notes and future approval
  before use.**

## 6. QA report schema (26 required fields)

Every future per-dataset `qa_report.json` MUST populate **all 26** of the
following fields. Missing any one of them is a **FAIL** verdict.

| # | Field | Purpose |
|--:|---|---|
| 1  | `qa_report_id` | Immutable id for this QA report. |
| 2  | `dataset_id` | Dataset under test. |
| 3  | `dataset_version` | Version under test. |
| 4  | `manifest_version` | Manifest spec version (e.g., `crypto_d1_dataset_manifest_v1`). |
| 5  | `data_contract_version` | `crypto_d1_data_contract_v1` (or later). |
| 6  | `protocol_version` | `crypto_d1_protocol_v1` (or later). |
| 7  | `generated_at` | ISO-8601 UTC; harness run timestamp. |
| 8  | `qa_status` | One of the 6 declared statuses. |
| 9  | `checks_run` | Integer total of QA checks executed. |
| 10 | `checks_passed` | Integer count passed. |
| 11 | `checks_warned` | Integer count raised non-blocking warning. |
| 12 | `checks_failed` | Integer count raised blocking failure. |
| 13 | `blocking_failures` | Array of `{group, check_id, detail}` for every FAIL. |
| 14 | `warnings` | Array of `{group, check_id, detail}` for every WARN. |
| 15 | `row_count_observed` | Integer; per-asset and total. |
| 16 | `missing_day_summary` | Per-asset missing-day list (counts + dates). |
| 17 | `duplicate_summary` | Per-asset duplicate-row report. |
| 18 | `timestamp_summary` | Group B aggregate. |
| 19 | `OHLCV_summary` | Group C aggregate. |
| 20 | `volume_summary` | Group D aggregate. |
| 21 | `fee_slippage_summary` | Group F aggregate. |
| 22 | `source_provenance_summary` | Group E aggregate. |
| 23 | `freeze_summary` | Group G aggregate. |
| 24 | `allowed_next_step` | Free-text; e.g., "Author Crypto-D1 Baseline Backtest Plan v1". |
| 25 | `forbidden_next_steps` | Array, mirroring this spec's `forbidden_next_steps`. |
| 26 | `safety_flags` | The 7 pinned-False flags. |

## 7. Freeze rules

- **No Crypto-D1 backtest may use mutable / unfrozen data.**
- **Every dataset must have a manifest.**
- **Every dataset must pass QA or carry an approved `QA_WARN` note.**
- **Every dataset must cite `protocol_version` /
  `data_contract_version` / `manifest_version`.**
- **Every dataset must have `CHECKSUMS.txt`** (sha256 per file).
- **Every dataset must have row counts recorded.**
- **Every dataset must have a freeze timestamp** (in
  `FREEZE_RECORD.txt`).
- **Every future backtest must cite `dataset_id` and
  `dataset_version`.**
- **Changing data creates a new `dataset_version`.**
- **Manually edited data is invalid unless documented and
  revalidated** under a new `dataset_version`.
- **Daily bars must be UTC-normalized.**
- **Weekday-only calendars are forbidden.**

## 8. Allowed next steps

1. Author the **Crypto-D1 Baseline Backtest Plan v1** (pre-
   registration memo for the FIRST candidate strategy family + IS /
   OOS split; plan only, no backtest run).
2. Author the **Crypto-D1 Data Source Evaluation Memo v1** (assess
   which offline data sources could later satisfy this QA / freeze
   spec; memo only, no fetch).
3. Author a **Crypto-D1 Data Acquisition Authorization Draft** —
   still spec-only; only if the operator wants to start the path
   toward an actual P2 acquisition.
4. **Run the future QA harness** against an existing on-disk frozen
   dataset under a SEPARATE, separately-authorized P2 bundle.

## 9. Forbidden next steps

- Fetch data from any live exchange API.
- Connect SPARTA's runtime to any exchange or vendor over the network.
- Run any backtest on the basis of `QA_PASS` alone.
- Run any paper-order or live-trading flow on the basis of `QA_PASS`
  alone.
- Modify paper / live execution files.
- Schedule any background daemon or cron job.
- Install or read any API key, OAuth token, or `.env` credential.
- Use any synthetic / mock-priced data as evidence.

## 10. PASS / WATCH / FAIL rules (this spec itself)

- **PASS** — Every QA check group A–G has its required checks
  populated; every per-dataset `qa_report.json` under this spec
  carries all 26 `required_fields`; all 7 safety flags are False;
  `lane == "crypto_d1_protocol"`; `market_type == "spot"`;
  `timeframe == "1d"`; `freeze_rules` require `CHECKSUMS.txt` +
  `FREEZE_RECORD.txt` + version pins; `QA_status_model` includes all
  6 declared statuses; `QA_report_schema` includes all 26 fields;
  `allowed_next_steps` and `forbidden_next_steps` populated.
- **WATCH** — Spec is satisfied but at least one assumption is
  borderline (e.g., an outlier-cluster threshold intentionally
  lenient for an asset with shorter history, or `QA_WARN` acceptance
  criteria are loose). Lane stays WATCH on downstream usage.
- **FAIL** — Any of the seven QA check groups missing; any safety
  flag True; `QA_status_model` omits a required status;
  `QA_report_schema` omits a required field; `freeze_rules` omit
  checksums / freeze-timestamp / version pins; `allowed_next_steps`
  or `forbidden_next_steps` empty; any forbidden capability claim
  appears in MD or JSON.

## 11. No-profit-claim policy

- **QA is not strategy validation.**
- **QA_PASS does not imply edge.**
- **QA_PASS does not imply profitability.**
- **Clean daily OHLCV data does not imply profit.**
- **A QA report cannot authorize paper or live trading.**
- **A QA report cannot authorize backtesting by itself.**
- **No data fetch is authorized by this bundle.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Data QA / freeze specification only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in
  this spec's runtime.
- **No data fetch. No QA harness execution. No backtest. No dataset
  processing. No real dataset files created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this QA / freeze spec alone.
- **QA is not strategy validation. QA_PASS does not imply edge.
  QA_PASS does not imply profitability. Clean daily OHLCV data does
  not imply profit. A QA report cannot authorize backtesting by
  itself. A QA report cannot authorize paper or live trading.
  Crypto trend ideas are not profitable until tested with full
  costs. A good historical chart does not imply future returns.
  24/7** crypto session handling; weekday-only filters forbidden.
