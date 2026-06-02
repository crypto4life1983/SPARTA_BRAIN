# SPARTA Crypto-D1 Data QA Runtime Tool v1

> **Research-only. Runtime QA checker only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No dataset
> processing. No real data files or data directory created in this bundle.**
> This tool validates an **operator-supplied** frozen dataset directory that
> the operator points it at. It does NOT acquire data and does NOT authorize
> trading. **QA_PASS is a precondition for a future, separately-authorized
> backtest plan — never the authorization itself.**

**Tool doc id:** `crypto_d1_data_qa_runtime_tool_v1` · **version:** `1.0`
**Implements tool:** `tools/crypto_d1_data_qa_runtime_tool.py`

**Companion documents (read-only references):**
- Bundle 11 — `reports/crypto_d1_protocol_v1/protocol.{json,md}`
- Bundle 12 — `reports/crypto_d1_data_contract_v1/data_contract.{json,md}`
- Bundle 13 — `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.{json,md}`
- Bundle 14 — `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.{json,md}`
- Bundle 17 — `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.{json,md}`
- Bundle 18 — `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.{json,md}`
- Build report — `reports/crypto_d1_data_qa_runtime_tool_v1/report.{json,md}`

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL**.
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Allowed market type:** `spot` only.
- **Session calendar:** 24/7; weekday-only filters are **forbidden**.

## 2. What the tool does

Executes the Bundle 14 Data QA / Freeze Spec as deterministic code against an
operator-supplied dataset directory, then emits a `qa_report.json` populating
all **26** fields declared by Bundle 14's `QA_report_schema`, plus a
human-readable `qa_report.md`. It is a **checker only** — it reads files at
`--dataset-dir` and writes reports to `--out-dir`. It never fetches data,
never connects to an exchange, and never authorizes a backtest.

## 3. Expected inputs at `--dataset-dir`

| File | Purpose |
|---|---|
| `manifest.json` | Passes `crypto_d1_dataset_manifest_check.py`; pins protocol + data-contract versions; `research_lane=crypto_d1_protocol`, `market_type=spot`, `timeframe=1d`. |
| `CHECKSUMS.txt` | One `<sha256_hex>  <filename>` line per dataset file; verified at runtime against bytes on disk. |
| `FREEZE_RECORD.txt` | Key:value lines including `freeze_timestamp_utc` + at least three version pins. |
| `fees.json` | Per-venue taker fee + slippage (+ optional spread proxy). **No QA_PASS without taker + slippage.** |
| `<asset>_daily.csv` (≥1) | Daily OHLCV carrying the 9 required columns: `timestamp, open, high, low, close, volume, symbol, source, quote_currency`. |

## 4. The seven QA check groups

| Group | Checks (summary) |
|---|---|
| **A** `manifest_integrity` | manifest present + parses; all 35 required fields; protocol/data-contract version pins; lane/market/timeframe; freeze_status; QA_status; allowed_use + forbidden_use. |
| **B** `timestamp` | no duplicate `(symbol, timestamp)`; 24/7 calendar (weekday-only rejected); missing-day reconciliation; UTC daily storage. |
| **C** `OHLCV` | `high < low` rejected; self-consistency `high≥max(o,c,l)` / `low≤min(o,c,h)`; positive OHLC; close not missing. |
| **D** `volume` | negative volume → FAIL; zero-volume bar → WARN. |
| **E** `symbol_source` | BTC/ETH/SOL canonical; quote_currency consistency; source consistency (WARN); duplicate `(symbol, source, timestamp)` rejected. |
| **F** `fee_slippage` | fees.json present; taker declared; slippage declared (no PASS if either missing); spread_proxy WARN when absent. |
| **G** `freeze` | freeze_status FROZEN; CHECKSUMS.txt present + every file sha256-verified; FREEZE_RECORD.txt present with timestamp + pins; `row_count_actual` recorded. |

## 5. QA status model + classifier

`QA_DRAFT` · `QA_PASS` · `QA_WARN` · `QA_FAIL` · `QA_BLOCKED` · `QA_RETIRED`.

**Classifier:** QA_BLOCKED if the manifest declares an external block; else
QA_FAIL if any check FAILs; else QA_WARN if any check WARNs; else QA_PASS.

- **QA_PASS** does **not** imply profitability and does **not** authorize a
  backtest by itself — it is a precondition only.
- **QA_WARN** requires a written operator-acceptance note on the manifest
  before any backtest plan references the dataset; lane stays **WATCH**.
- **QA_FAIL** blocks all research use; remediation requires a **new**
  `dataset_version`.

## 6. CLI

```text
python tools/crypto_d1_data_qa_runtime_tool.py validate-spec
python tools/crypto_d1_data_qa_runtime_tool.py show-spec
python tools/crypto_d1_data_qa_runtime_tool.py run --dataset-dir <PATH> --out-dir <PATH>
```

`run` exits `0` for QA_PASS / QA_WARN, else `2`. `qa_report.json` +
`qa_report.md` are written to `--out-dir` **only** — never inside
`--dataset-dir`, never under `data/crypto_d1_research/`.

## 7. Safety + registry status

- **Stdlib-only** (`argparse, csv, dataclasses, datetime, hashlib, json,
  math, pathlib, sys`); in-repo imports limited to the Bundle 13/14
  validators. No network, broker, exchange, subprocess, `os.environ`,
  `getenv`, or `.env` access.
- Reads only `--dataset-dir`; writes only `--out-dir`; never creates
  `data/crypto_d1_research/`; on missing data emits QA_DRAFT/QA_FAIL and
  **never fabricates** results.
- Every emitted report pins the seven safety flags
  (`research_only=true`; the other six `false`).
- **Candidate registry:** this doc pair is added to the `crypto_d1` lane
  `extra_files` for traceability only. The lane stays **WATCH**; evidence
  does **not** become STRONG; the candidate is **not** marked ACTIVE. No
  broker / live / paper / backtest authorization is implied.

## 8. No-profit-claim policy

QA is not strategy validation. QA_PASS does not imply edge or profitability.
Clean daily OHLCV data does not imply profit. A QA report cannot authorize
backtesting, paper, or live trading by itself. No data fetch is authorized by
this tool. Crypto trend ideas are not profitable until tested with full
costs. A good historical chart does not imply future returns.
