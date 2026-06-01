# SPARTA Arbitrage Dataset Manifest v1

> **Research-only. Dataset manifest / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest
> in this bundle.** This document is the written input spec that any future,
> separately-authorized data-acquisition bundle MUST produce a per-dataset
> manifest under.

**Dataset manifest id:** `arbitrage_dataset_manifest_v1` · **version:** `1.0`

**Companion documents:**
[`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md) ·
[`arbitrage_data_contract_v1`](../arbitrage_data_contract_v1/data_contract.md).

---

## 1. Research objective

Define exactly how any **future** arbitrage dataset must be declared, frozen,
validated, versioned, and audited **before** any research test is allowed to
use it. This spec does not fetch data, does not connect to any exchange, does
not run a backtest, and does not authorize trading.

## 2. Manifest schema (what every future per-dataset manifest must contain)

Every real dataset must ship with a JSON manifest file that satisfies these
required fields:

`dataset_id` · `dataset_version` · `created_at` · `created_by` ·
`research_lane` · `arbitrage_category` · `venues` · `symbols` ·
`instruments` · `time_start` · `time_end` · `timezone` · `data_frequency` ·
`quote_type` · `order_book_depth` · `fee_schedule_reference` ·
`funding_schedule_reference` · `source_type` · `source_location` ·
`checksum_policy` · `row_count_expected` · `row_count_actual` ·
`missing_data_policy` · `duplicate_policy` · `stale_quote_policy` ·
`clock_skew_policy` · `normalization_policy` · `freeze_status` ·
`qa_status` · `allowed_use` · `forbidden_use` · `notes`.

Field semantics are in `dataset_manifest.json` under `manifest_schema.field_descriptions`.

## 3. Category-specific manifest requirements

### A. Cross-exchange spot arbitrage
- **venue_pair_synchronization** — documented per-venue clock skew + shared UTC alignment timestamp.
- **quote_depth** — L1 mandatory; L2 (≥5 levels) for any depth-at-size test.
- **transfer / withdrawal assumption references** — explicit cite to the withdrawal-latency assumption row in the data contract; per-asset / per-network.
- **fee schedule references** — explicit cite to fee tier per venue, dated.

### B. Spot-perp basis / funding arbitrage
- **funding timestamps** — per-row settlement timestamp aligned to the venue's exact UTC cutoff.
- **funding rates** — rate, settlement period, predicted vs. realized when distinguishable.
- **perp contract specs** — mark/index composition, tick size, lot size, contract multiplier.
- **liquidation-risk notes** — maintenance margin, liquidation-engine model, partial vs. full liquidation behaviour.

### C. Triangular arbitrage
- **three-leg pair mapping** — explicit ordered list (leg_1, leg_2, leg_3) with venue + symbol.
- **precision / rounding rules** — tick size + lot size per pair.
- **leg order assumptions** — documented send order + assumed time-to-fill per leg.
- **depth per leg** — L1 (preferably L2) at the test size for each leg.

### D. Futures calendar / basis arbitrage
- **contract expiries** — per-contract last trading day + settlement date.
- **multipliers** — contract multiplier per contract.
- **roll calendar** — which days the operator's protocol would have rolled (OI / volume / calendar method).
- **margin / carry assumptions** — initial + maintenance margin per contract per venue; cost-of-carry / funding assumption used to compute fair basis.

### E. Statistical / relative-value mispricing (**NOT pure arbitrage**)
- **aligned price history** — both legs aligned to the same bar timestamp.
- **spread definition** — log-ratio, beta-adjusted spread, distance-from-rolling-mean, etc.
- **z-score / correlation prerequisites** — cointegration / stationarity diagnostics over the **IS** window only.
- **explicit NOT pure arbitrage label** — every downstream artifact must label this category as **RELATIVE_VALUE**, not ARBITRAGE.

## 4. Dataset identity and provenance

- **Immutable `dataset_id`** — stable, never reused.
- **`dataset_version`** — monotonically increasing integer; bumped on any change to raw rows, normalization, or schema.
- **Source provenance** — every row carries a source identifier + data-contract version + `dataset_version`.
- **Checksums / hashes** — sha256 per file (or per shard); manifest stores per-file checksums for **FROZEN** status.
- **Row counts** — expected vs. actual; mismatch without an explicit gap row is invalid.
- **`created_at`** — ISO-8601 UTC.
- **`freeze_timestamp`** — ISO-8601 UTC; required when `freeze_status` transitions to **FROZEN**.
- **Manifest author** — human or tool identity; anonymous manifests are invalid.

### What makes a dataset INVALID
- Manifest missing or fails `arbitrage_dataset_manifest_check`.
- Any required future manifest field is absent.
- `source_location` is a network URL.
- Row count mismatch without a documented gap.
- Any safety flag in the manifest is True.
- `freeze_status` is **DRAFT** but the dataset is referenced in a research run.
- `qa_status` is **QA_FAIL** or **BLOCKED**.

### What makes a dataset FROZEN
- `freeze_status == FROZEN`.
- `freeze_timestamp` present and not in the future.
- All per-file checksums stored and verifiable.
- `row_count_expected == row_count_actual` (or a documented gap explains the difference).
- Manifest validates against this spec without warnings.

### What makes a dataset UNTRUSTED
- Manually edited rows without explicit documentation + re-validation.
- Source provenance missing or partially attributable.
- Checksums missing or invalid.
- OOS window was peeked before sealing.
- Manifest validates only with WARN-level issues that have not been triaged.

## 5. Data freeze rules

- No research test may use mutable / unfrozen data. `freeze_status` MUST be **FROZEN** before any test reads the rows.
- Every dataset MUST have a manifest. Datasets without manifests are invalid by definition.
- Every manifest MUST pass validation before the dataset is used.
- Every dataset MUST carry a `qa_status`. Only **QA_PASS** (or explicitly-accepted **QA_WARN**) datasets may be used.
- Every dataset MUST be tied to a specific Arbitrage Data Contract version. Dataset and contract version are paired forever.
- Every future research test MUST cite `dataset_id` AND `dataset_version` in its run record.
- Any change to raw rows, normalization, or schema produces a **NEW** dataset version. Old versions are never silently overwritten.
- Manually edited data is INVALID unless explicitly documented + re-validated under a new `dataset_version`.

## 6. QA status model

| Status | When it applies |
|---|---|
| **DRAFT** | Dataset is being assembled. Not usable for any research test. `freeze_status` is also DRAFT. |
| **FROZEN** | Frozen at the file level (checksums fixed). QA may not have run yet. Cannot be used for tests until `qa_status` is QA_PASS. |
| **QA_PASS** | QA harness reports zero unresolved flags; row counts match; provenance intact; contract version pinned. Research-usable. |
| **QA_WARN** | QA harness reports ≥1 non-blocking warning (e.g., borderline coverage / liquidity / latency). Usable **only** after an explicit operator-acceptance memo per `dataset_version`. |
| **QA_FAIL** | QA harness reports ≥1 blocking failure (missing required field, broken checksum, peeked OOS, etc.). NOT research-usable. |
| **RETIRED** | No longer used. Kept for historical traceability; cannot be re-promoted to QA_PASS. |
| **BLOCKED** | Externally blocked (legal / TOS / vendor restriction). Cannot be used; explicit unblock action required. |

## 7. Allowed file formats

`parquet` (preferred; columnar, schema-pinned) · `csv` (allowed; schema in
manifest; type pinned) · `json` / `jsonl` (event streams; schema declared) ·
`feather` / `arrow` (allowed) · `sqlite` (allowed for small offline datasets).

## 8. Forbidden inputs

- Live exchange APIs at dataset-build time from this manifest's runtime.
- Scraping any venue HTML / WebSocket / undocumented endpoint.
- Any source requiring an embedded API key, OAuth token, or `.env` credential at this manifest's runtime.
- Synthetic / mock-priced data presented as historical. (The `source_type` `synthetic_diagnostic_only_NOT_FOR_BACKTEST` is allowed for diagnostics only and never as a backtest dataset.)
- Datasets whose provenance cannot be cited line-by-line.
- Datasets whose OOS window was peeked before sealing.
- Datasets whose TOS forbid research use.
- `source_location` pointing to a network URL instead of an on-disk path.

## 9. Required future artifacts

- Per-dataset **manifest file** satisfying `manifest_schema.required_future_manifest_fields`.
- Per-dataset **integrity report** (row counts, gap stats, outage overlap, contract version pinned, checksums verified).
- Per-dataset **QA harness report** (status: QA_PASS / QA_WARN / QA_FAIL).
- Per-dataset **freeze record** (freeze_timestamp + per-file checksums) when `freeze_status` transitions to FROZEN.
- Per-dataset **retirement memo** when `freeze_status` transitions to RETIRED.

## 10. Validation

- Validator tool: `tools/arbitrage_dataset_manifest_check.py`.
- Must be run BEFORE research use; must be re-run on any manifest change.
- Outputs: `validate: OK` (pass) or `validate: FAIL` with reasons.

## 11. PASS / WATCH / FAIL rules (for THIS spec)

- **PASS** — All required top-level sections present; `manifest_schema` lists every required future manifest field; all 5 categories carry category-specific requirements; QA status model contains all 7 statuses; freeze rules documented; no safety flag True; no forbidden phrase.
- **WATCH** — Spec satisfied but at least one section is borderline; documented and re-checked.
- **FAIL** — Any required section missing; any safety flag True; any QA status missing; any required future manifest field absent; any forbidden phrase present.

## 12. No-profit-claim policy

- Dataset manifest approval does **not** imply edge.
- **QA_PASS does not imply profitability.**
- A price gap is **not** profit.
- A dataset cannot authorize trading.
- A manifest cannot authorize live or paper-order execution.
- No manifest, regardless of QA status, promotes any lane to ACTIVE or STRONG.

## 13. Safety boundaries (pinned, non-negotiable)

- Research-only. Dataset manifest / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this manifest's runtime.
- **No data fetch in this bundle. No backtest in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG evidence from this manifest alone.
- A price gap is not profit. **QA_PASS does not imply profitability.** Manifest approval does not imply edge.
