# SPARTA Crypto-D1 Data Source Evaluation Memo v1

> **Research-only. Data source evaluation MEMO only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No dataset
> processing. No real data files or data directory created in this bundle.**
> This memo evaluates 6 source CLASSES for the Crypto-D1 lane. It does NOT
> name a specific vendor, venue, or archive that is authorized now; every
> concrete data source remains **NOT authorized** by this bundle alone.
> Actual data acquisition still requires separate explicit operator
> authorization through the Bundle 17 gates.

**Evaluation id:** `crypto_d1_data_source_evaluation_v1` · **version:** `1.0`

**Companion documents (read-only references):**
- Bundle 11 — `reports/crypto_d1_protocol_v1/protocol.{json,md}`
- Bundle 12 — `reports/crypto_d1_data_contract_v1/data_contract.{json,md}`
- Bundle 13 — `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.{json,md}`
- Bundle 14 — `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.{json,md}`
- Bundle 15 — `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.{json,md}`
- Bundle 16 — `tools/crypto_d1_backtest_runner.py`
- Bundle 17 — `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.{json,md}`
- Pattern reference — `reports/arbitrage_data_source_evaluation_v1/data_source_evaluation.{json,md}`

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (all required).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Allowed market type:** `spot` only.
- **Forbidden market types:** perp futures, dated futures, options,
  leveraged tokens, margin / borrow-facilitated spot, synthetic
  instruments.

## 2. Evaluation objective

Provide a written, research-only assessment of which offline data source
**CLASSES** could later satisfy:

- Bundle 17 `approved_data_scope`,
- Bundle 14 QA / freeze requirements, and
- Bundle 12 `required_csv_schema` + `OHLCV_QA_checks`.

**This memo evaluates classes only.** It does **not** name a specific
vendor, venue, or archive that is authorized now. Every concrete data
source remains **NOT authorized** by this bundle alone. Actual data
acquisition still requires separate explicit operator authorization
through the Bundle 17 gates.

## 3. The 6 source classes

| ID | Class | Status |
|---|---|:-:|
| **A** | Exchange public historical archives (offline CSV / Parquet exports) | **ACCEPTABLE** |
| **B** | Exchange public APIs (operator-side only; never called by SPARTA runtime) | **WATCH (future-only)** |
| **C** | Paid market-data vendors (operator-supplied offline export) | **PREFERRED** |
| **D** | Existing local OHLCV files (pre-staged by operator) | **ACCEPTABLE** |
| **E** | Web-scraped / unofficial tables | **REJECTED for evidence**, WATCH-only context |
| **F** | Manually copied prices / screenshots | **REJECTED for any quantitative claim** |

### A — Exchange public historical archives (ACCEPTABLE)

Public daily OHLCV archives published by reputable exchanges. The
operator manually downloads a public daily archive; SPARTA reads the
resulting CSV offline. **SPARTA's runtime never makes a network call.**

- Typical shape: daily OHLCV with timestamp / open / high / low / close /
  volume (sometimes vwap / trade_count / quote_volume). Quote currency
  typically USDT (crypto-native venues) or USD (fiat-quoting venues).
- BTC and ETH typically have many years of history (often 7+); SOL is
  shorter (~5y depending on the venue).
- TOS usually permits research use; **operator confirms per-venue**.
- Caveats: single-venue history breaks at the venue's listing date for
  the asset; cross-venue stitching requires documented rules; non-UTC
  bar boundaries need ingest-time conversion; volume aggregation method
  must be documented per series.

### B — Exchange public APIs (WATCH, future-only)

Exchange public REST / WebSocket APIs that an **operator** may use under
the operator's own credentials to produce an offline CSV. **SPARTA's
runtime never connects to these APIs.** The output of the operator's API
call is treated as a Class D local file when handed to SPARTA.

- WATCH-only because: rate limits, pagination, and reconciliation gaps
  are the operator's responsibility before handing the resulting CSV to
  SPARTA. If any API key, OAuth token, or `.env` credential is required,
  **it stays with the operator** — never enters SPARTA's runtime,
  `.env`, or `local_secrets`.
- Compatible with Bundle 17 only when the operator-side acquisition is
  complete AND the resulting file is treated as a Class D handoff.

### C — Paid market-data vendors (PREFERRED)

Commercial market-data vendors via **offline export flow**. The vendor
produces a flat CSV / Parquet export; the operator places the file under
`data/crypto_d1_research/<dataset_id>/<dataset_version>/`.

- Typically the cleanest combination of: documented provenance, TOS
  clarity, deep BTC / ETH / SOL history, ready-to-import format, and
  per-venue selection rules.
- **PREFERRED does NOT mean APPROVED.** "Preferred" is a relative
  ranking among the 6 evaluated classes for the kind of evidence the
  Crypto-D1 protocol seeks. Concrete vendor selection still requires
  explicit operator authorization through Bundle 17's 20 approval gates.
- Caveat: some vendors require a per-environment license; operator must
  confirm before adding the CSV to the repo or to a shared analysis.

### D — Existing local OHLCV files (ACCEPTABLE)

OHLCV CSV files that already exist on the operator's machine (e.g., from
a previous research project) and can be re-evaluated under Bundle 12 +
Bundle 13 + Bundle 14 requirements.

- Lowest-friction starting point **IF** provenance can be re-attested
  and the file can be brought into compliance with the Bundle-12 schema.
- Per Bundle 12: if provenance cannot be cited line-by-line, the file is
  invalid.
- Re-using a file from a different research lane requires a **NEW**
  `dataset_id` and a **NEW** `dataset_version`; no in-place edits.

### E — Web-scraped / unofficial tables (REJECTED for evidence)

Data obtained by scraping a venue's HTML page or pulling from an
unofficial / community-maintained dump.

- **REJECTED** as a basis for any evidence claim.
- Permitted only as **anecdotal context** with explicit **WATCH-only**
  labeling.
- Rejection reasons: TOS risk (most public venues forbid scraping);
  reproducibility loss (scraped pages change); provenance opacity
  (row-level source_id cannot be reconstructed); cross-venue stitching
  undocumented; per Bundle 12, datasets without line-by-line provenance
  are invalid.

### F — Manually copied prices / screenshots (REJECTED)

Numbers typed by hand into a spreadsheet, screenshots of charts,
hand-transcribed exchange tickers.

- **REJECTED** for any quantitative claim.
- Acceptable only as anecdotal narrative (no numeric backtest result may
  depend on this data).
- Per Bundles 12 / 13 / 14 / 16 / 17 forbidden-inputs lists,
  screenshots and manually copied prices are explicitly disallowed.

## 4. Decision matrix

`allowed_now = false` on **every** row. Concrete authorization is
reserved for the operator's per-dataset action under Bundle 17's 20
approval gates.

| ID | Status | spot/d? | BTC/ETH/SOL coverage | TOS OK? | Network call from SPARTA? | Bundle 17 compatible? |
|---|---|:-:|---|:-:|:-:|:-:|
| A | ACCEPTABLE | ✓ | good (BTC/ETH ~7y+; SOL ~5y) | ✓ | ✗ | ✓ |
| B | WATCH (future-only) | ✓ | good back to listing | venue-dep. | ✗ | ✓ (operator-side only) |
| C | PREFERRED | ✓ | deepest available | usually explicit | ✗ | ✓ |
| D | ACCEPTABLE | ✓ | whatever operator has | source-dep. | ✗ | ✓ |
| E | REJECTED (evidence) / WATCH-only context | uneven | variable | usually FORBIDDEN | ✗ | ✗ |
| F | REJECTED (any claim) | ✗ | N/A | N/A | ✗ | ✗ |

The full 15-field machine matrix lives in `data_source_evaluation.json`
under `decision_matrix.rows`.

## 5. Approval gates before any source use (20 gates)

1. Explicit written **operator authorization** BEFORE any acquisition.
2. Exact source CLASS named (one of A/B/C/D; never E/F).
3. Exact vendor / venue / archive named (`source_name`); NO anonymous
   provenance.
4. Exact symbols named (subset of `{BTC, ETH, SOL}`).
5. Exact time window named (`time_start`, `time_end` — ISO-8601 UTC).
6. Exact storage path named
   (`data/crypto_d1_research/<dataset_id>/<dataset_version>/`).
7. Exact `dataset_id` named
   (`CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`).
8. `protocol_version` pinned (`crypto_d1_protocol_v1` or later).
9. `data_contract_version` pinned (`crypto_d1_data_contract_v1` or
   later).
10. `dataset_manifest_spec_version` pinned
    (`crypto_d1_dataset_manifest_v1` or later).
11. `qa_freeze_spec_version` pinned (`crypto_d1_qa_freeze_spec_v1` or
    later).
12. `backtest_plan_version` pinned
    (`crypto_d1_baseline_backtest_plan_v1` or later).
13. `runner_version` pinned (`crypto_d1_backtest_runner_v1` or later).
14. TOS verified for the chosen source class and recorded in manifest.
15. **No** credentials / API key / OAuth token / private key / `.env`
    enters SPARTA at any step.
16. **No** network call is made from SPARTA's runtime at any step.
17. `CHECKSUMS.txt` and `FREEZE_RECORD.txt` produced per Bundle 17's
    `checksum_requirements`.
18. `manifest.json` passes
    `tools/crypto_d1_dataset_manifest_check.py`.
19. `qa_report.json` passes the Bundle 14 spec (or its future runtime
    tool when it exists).
20. `QA_status` is **`QA_PASS`** OR (**`QA_WARN`** with an explicit
    operator-acceptance note).

## 6. Forbidden data sources / methods

- Live exchange APIs called from SPARTA's runtime (Class B is
  operator-side only).
- Scraping any venue HTML / WebSocket / undocumented endpoint from
  SPARTA's runtime.
- Any source requiring an embedded API key, OAuth token, or `.env`
  credential.
- Any source that requires SPARTA to MAKE a network call from its
  runtime.
- Any synthetic / mock-priced data used in place of real historical
  data for any evidence claim.
- Any dataset whose provenance cannot be cited line-by-line.
- Any dataset that has been peeked at in its OOS window before sealing.
- Any feed whose terms of service forbid research use.
- Class **E** (web-scraped / unofficial) as evidence.
- Class **F** (screenshots / manually copied prices) for any
  quantitative claim.

## 7. Required provenance fields (per dataset)

- `source_class` (one of A, B, C, D).
- `source_name` (vendor / venue / archive).
- `source_location` (local repo-relative path).
- `license_or_tos_reference` (explicit pointer to the TOS or license).
- `row_level_source_id` (every row carries a per-row source identifier).
- `file_hash_sha256` (recorded in `CHECKSUMS.txt` at freeze).
- `freeze_timestamp_utc` (recorded in `FREEZE_RECORD.txt` at freeze).
- `operator_name_and_tool_label` (recorded in `FREEZE_RECORD.txt`).
- `data_contract_version`, `protocol_version`,
  `dataset_manifest_version`, `qa_freeze_spec_version`,
  `backtest_plan_version`, `runner_version` (all pinned per dataset).

## 8. Preferred class for Crypto-D1 (with explicit caveats)

- **Preferred:** Class **C** (paid market-data vendors).
- **Rationale:** Of the 6 evaluated classes, Class C offers the cleanest
  combination of documented provenance, TOS clarity, deep BTC / ETH /
  SOL history, ready-to-import format, and per-venue selection rules.
- **Preferred does NOT mean Approved.** "Preferred" is a relative
  ranking among the evaluated classes only; it is NOT an authorization
  for any specific vendor. Concrete vendor selection still requires
  explicit operator authorization through Bundle 17 gates.
- **Fallback if Class C is not feasible:** Class **A** (exchange public
  historical archives). Preserves TOS clarity and single-venue
  provenance without requiring any SPARTA-side network call.

## 9. PASS / WATCH / FAIL rules

- **PASS** — A future per-dataset source declaration passes IF:
  `source_class` is one of A/B/C/D (never E/F); `source_name` is
  explicitly named; `source_location` is local repo-relative; license /
  TOS reference is attached; row-level `source_id` is present; sha256
  per file is recorded; freeze record is recorded; all 6 version pins
  are present; `manifest.json` passes
  `tools/crypto_d1_dataset_manifest_check.py`; `qa_report.json` passes
  the Bundle 14 spec; `QA_status` is `QA_PASS` or accepted `QA_WARN`.
- **WATCH** — Source declaration passes but at least one borderline
  condition (e.g., SOL history is < 5y on the chosen source; vendor TOS
  requires a per-environment license that the operator has not yet
  attached; per-venue stitching rule is documented but unusual). Lane
  stays WATCH on downstream usage.
- **FAIL** — `source_class` is E or F; `source_name` is anonymous;
  license / TOS reference missing; row-level `source_id` missing;
  sha256 not recorded; freeze record missing; any version pin missing;
  manifest fails Bundle 13 check; qa_report fails Bundle 14 check;
  `QA_status` is `QA_FAIL` or `QA_BLOCKED`; any safety flag is True;
  any forbidden phrase appears in the manifest or evidence chain.

## 10. Required future artifacts

- Per-dataset `manifest.json` conforming to Bundle 13 schema
  (operator-authored under Bundle 17 gates).
- Per-dataset `CHECKSUMS.txt` with sha256 per file (operator-produced
  at freeze).
- Per-dataset `FREEZE_RECORD.txt` with freeze timestamp + operator +
  pinned versions (operator-produced at freeze).
- Per-dataset `qa_report.json` conforming to Bundle 14
  `QA_report_schema` (26 fields).
- Per-strategy backtest `report.json` + `report.md` emitted by
  `tools/crypto_d1_backtest_runner.py` after the operator runs the
  runner against the FROZEN dataset.
- **Crypto-D1 Baseline Results Report v1** (separately authorized;
  only after operator has supplied data AND the runner has produced
  output).

## 11. No-profit-claim policy

- **Source evaluation does not imply edge.**
- **Acceptable source class does not authorize acquisition.**
- **Preferred does not mean approved.**
- **No data fetch is authorized by this bundle.**
- **Clean OHLCV data does not imply profit.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Data source evaluation MEMO only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  memo's runtime.
- **No data fetch. No dataset processing. No real data files or data
  directory created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this memo alone.
- **Source evaluation does not imply edge. Acceptable source class
  does not authorize acquisition. Preferred does not mean approved.
  No data fetch is authorized by this bundle. Crypto trend ideas are
  not profitable until tested with full costs AND forward-validated
  under a separately authorized future plan. A good historical chart
  does not imply future returns. 24/7** crypto session handling;
  weekday-only filters forbidden.
