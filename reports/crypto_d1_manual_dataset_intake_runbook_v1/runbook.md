# SPARTA Crypto-D1 Manual Dataset Intake Runbook v1

> **Research-only. Operator runbook (documentation) only.**
> This runbook **authorizes nothing operational**. It **does not authorize
> fetching**. It **does not authorize QA on real data by itself**. **QA_PASS
> does not authorize automatic backtesting. QA_PASS does not authorize paper
> trading. QA_PASS does not authorize live trading.** Real data may enter
> SPARTA **only through explicit operator action and the Bundle 17 gates**.
> No broker control. No exchange connection. No API keys. No `.env`. No
> credential handling. No scheduler / background daemon. No external network
> calls. No data fetch. No dataset processing. No real data files or data
> directory created by this bundle. **This bundle does not create
> `data/crypto_d1_research/`.**

**Runbook doc id:** `crypto_d1_manual_dataset_intake_runbook_v1` ·
**version:** `1.0`

**Companion documents (read-only references):**
- Bundle 11 — `reports/crypto_d1_protocol_v1/protocol.{json,md}`
- Bundle 12 — `reports/crypto_d1_data_contract_v1/data_contract.{json,md}`
- Bundle 13 — `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.{json,md}`
- Bundle 14 — `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.{json,md}`
- Bundle 17 — `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.{json,md}`
- Bundle 18 — `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.{json,md}`
- Bundle 19 — `reports/crypto_d1_data_qa_runtime_tool_v1/qa_runtime_tool.{json,md}` (implements `tools/crypto_d1_data_qa_runtime_tool.py`)

---

## 0. Where this runbook sits in the pipeline

```
B11 protocol -> B12 data contract -> B13 manifest -> B14 QA/freeze spec
   -> B17 acquisition authorization (the gate)
   -> [THIS RUNBOOK: operator manually brings data in]
   -> B19 QA runtime tool (validate the on-disk dataset)
   -> (future, separately authorized) Baseline Results Report
```

This runbook is the **human-procedure layer** that bridges the Bundle 17
authorization gate to the Bundle 19 QA tool. It adds **no automation** to that
bridge — every step is a manual operator action.

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (spot only).
- **Timeframe:** daily (`1d`) only. Intraday is **explicitly out of scope**.
- **Session calendar:** 24/7; weekday-only filters are **forbidden**.

## 2. Operator decisions before any data enters

1. Decide **whether** to acquire at all this cycle — a research decision, not a default.
2. Decide the **source class** (one of A/B/C/D from Bundle 18; never E or F).
3. Decide the concrete **source name** (vendor / venue / archive) — never anonymous.
4. Confirm the **license / TOS** permits research use; record the reference.
5. Decide which of **BTC / ETH / SOL** are in this dataset (spot only).
6. Confirm **market type is spot only** (no perps, dated futures, options, leveraged tokens, margin-facilitated spot).
7. Confirm **timeframe is 1d only** — intraday out of scope.
8. Decide the **date range** (`time_start`, `time_end`; both ISO-8601 UTC).
9. Decide the **`dataset_id`** (`CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`) and **`dataset_version`**.
10. Decide the **storage path** (`data/crypto_d1_research/<dataset_id>/<dataset_version>/`) — created only when the operator acquires data, never by SPARTA automation.
11. Decide and record **fee + slippage** assumptions per venue (taker fee + slippage; spread proxy optional).
12. Confirm **no credentials / API key / OAuth token / private key / `.env`** will enter the SPARTA repo or runtime at any step.

## 3. Source class dispositions (from Bundle 18 — not re-ranked here)

| Class | Disposition | Note |
|---|---|---|
| **C** paid market-data vendors | **PREFERRED** | Cleanest provenance + TOS clarity. **PREFERRED does NOT mean APPROVED**; concrete vendor still requires Bundle 17 gates. |
| **A** exchange public historical archives (offline) | **ACCEPTABLE** | Operator downloads; SPARTA runtime never makes a network call. |
| **D** existing local OHLCV files (pre-staged) | **ACCEPTABLE** | Require provenance re-attestation, schema normalization, fresh sha256 + manifest, NEW `dataset_id`/version. |
| **B** exchange public APIs | **WATCH (future-only)** | Operator-side only, under operator's own credentials, **outside SPARTA**; output lands as a Class D local file. SPARTA runtime MUST NOT call any exchange API. |
| **E** web-scraped / unofficial tables | **REJECTED for evidence** | TOS risk + reproducibility loss + provenance opacity. Never a backtest input. |
| **F** screenshots / manually copied prices | **REJECTED for any quantitative claim** | Forbidden inputs per Bundles 12/13/14/16/17. |

## 4. Required concrete inputs before acquisition

| Input | Requirement |
|---|---|
| `source_name` | Exact vendor / venue / archive; never anonymous. |
| `source_class` | One of A / B / C / D (never E / F). |
| `license_or_tos_reference` | Explicit pointer to the license / TOS; recorded in manifest. |
| assets | Subset of {BTC, ETH, SOL}; canonical symbols. |
| market type | **spot only**. |
| timeframe | **1d only**; intraday out of scope. |
| date range | `time_start` + `time_end`, both ISO-8601 UTC. |
| file naming | `<asset>_daily.csv` (e.g., `BTC_daily.csv`). |
| storage path | `data/crypto_d1_research/<dataset_id>/<dataset_version>/`. |
| `dataset_id` | `CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`. |
| `dataset_version` | Immutable per freeze; remediation requires a NEW version. |
| sha256 checksums | Per dataset file, recorded in `CHECKSUMS.txt`. |
| `manifest.json` | Passes `tools/crypto_d1_dataset_manifest_check.py`; pins versions; lane/market/timeframe. |
| `CHECKSUMS.txt` | One `<sha256_hex>  <filename>` line per dataset file. |
| `FREEZE_RECORD.txt` | `key:value` lines with `freeze_timestamp_utc` + operator + version pins. |
| fees / slippage | `fees.json` with per-venue taker fee + slippage (spread proxy optional). **No QA_PASS without taker fee AND slippage.** |

The **9 required CSV columns**: `timestamp, open, high, low, close, volume,
symbol, source, quote_currency`.

## 5. File placement procedure

1. Create `data/crypto_d1_research/<dataset_id>/<dataset_version>/` (operator action; **SPARTA does NOT create it**).
2. Place each `<asset>_daily.csv` there with the 9 required columns and UTC daily timestamps.
3. Place `fees.json` declaring per-venue taker fee + slippage (+ optional spread proxy).
4. Author `manifest.json` so it passes `tools/crypto_d1_dataset_manifest_check.py`.
5. Compute sha256 for every dataset file and write `CHECKSUMS.txt`.
6. Write `FREEZE_RECORD.txt` with `freeze_timestamp_utc`, operator name/label, and version pins.
7. Do **not** commit dataset contents unless explicitly authorized; treat the storage path as gitignored by default.
8. Keep the QA `--out-dir` **separate** from `--dataset-dir`; never write QA output inside the dataset directory.

## 6. Validate with the QA runtime tool (Bundle 19)

```text
python tools/crypto_d1_data_qa_runtime_tool.py validate-spec
python tools/crypto_d1_data_qa_runtime_tool.py show-spec
python tools/crypto_d1_data_qa_runtime_tool.py run --dataset-dir <PATH> --out-dir <PATH>
```

`run` exits `0` for QA_PASS / QA_WARN, else `2`. It writes `qa_report.json` +
`qa_report.md` to `--out-dir` **only**.

## 7. What the six QA statuses mean

| Status | Meaning |
|---|---|
| **QA_DRAFT** | No checks could run (e.g., `--dataset-dir` missing). Not eligible for any downstream use. |
| **QA_PASS** | All 7 groups passed, zero warnings. Deterministic. Does **not** imply profitability and does **not** authorize a backtest/paper/live by itself. |
| **QA_WARN** | No blocking failures but ≥1 warning. Operator attaches a written acceptance note to the manifest before any backtest plan references the dataset; lane stays WATCH. |
| **QA_FAIL** | ≥1 blocking failure. Dataset MUST NOT be referenced; remediation requires a NEW `dataset_version`. |
| **QA_BLOCKED** | External block declared in the manifest. Dataset MUST NOT be referenced until cleared. |
| **QA_RETIRED** | Superseded by a newer version; read-only for reproducibility / audit. |

## 8. Why QA_PASS authorizes nothing

- QA_PASS is a **data-quality precondition**, not strategy validation.
- **QA_PASS does not authorize automatic backtesting.**
- **QA_PASS does not authorize paper trading.**
- **QA_PASS does not authorize live trading.**
- Clean daily OHLCV data does not imply profit.
- A good historical chart does not imply future returns.

## 9. What must happen after QA, before baseline results

- On QA_PASS (or operator-accepted QA_WARN with a written manifest note), the
  dataset becomes eligible to be **referenced** by a separately authorized
  backtest plan — it is not itself authorized to run.
- A separately authorized **Crypto-D1 Baseline Results Report** (future bundle)
  documents the operator-reviewed run only **after** data is supplied, QA is
  PASS/accepted-WARN, and the runner has produced output.
- SPARTA does **not** chain QA into a backtest automatically.
- On QA_FAIL / QA_BLOCKED, no downstream use until remediated (NEW
  `dataset_version`) or the block is cleared.

## 10. Forbidden list

- no perps
- no leverage
- no intraday
- no scraping / unofficial data as evidence
- no screenshots / manually copied prices
- no broker / live / paper execution
- no credentials / API keys in repo
- no network automation from SPARTA

## 11. Keeping the pipeline safe, repeatable, and auditable

- Every dataset is **frozen**: immutable `dataset_version` + sha256 in
  `CHECKSUMS.txt` + `FREEZE_RECORD.txt` (timestamp + operator + version pins).
- Provenance is **line-by-line**: `source_name` + `source_class` + license/TOS
  + row-level `source_id`; anonymous provenance is invalid per Bundle 12.
- Re-running the QA tool on the same frozen bytes yields the same verdict.
- Remediation **never edits in place** — a FAIL requires a NEW `dataset_version`.
- SPARTA's runtime never fetches, never connects to an exchange, never holds
  credentials; all acquisition is operator-side and offline.

## 12. Registry status

This runbook doc pair is added to the `crypto_d1` lane `extra_files` for
traceability only. The lane stays **WATCH**; evidence does **not** become
STRONG; the candidate is **not** marked ACTIVE. No broker / live / paper /
backtest authorization is implied.

## 13. No-profit-claim policy

A runbook is not strategy validation. Manual intake does not imply edge.
QA_PASS does not imply profitability. Clean daily OHLCV data does not imply
profit. A runbook cannot authorize backtesting, paper, or live trading by
itself. No data fetch is authorized by this runbook. Crypto trend ideas are
not profitable until tested with full costs.
A good historical chart does not imply future returns.
