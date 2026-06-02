# SPARTA Crypto-D1 Readiness Gate / Operator Checklist v1

> **Research-only. Readiness gate / operator checklist only.**
> This gate **authorizes nothing operational**. No data fetch. No exchange
> connection. No API keys. No `.env`. No credential handling. No QA run against
> real data. No backtest. No broker / live / paper / micro-live trading. No
> scheduler / daemon. No external network calls. It **does not create
> `data/crypto_d1_research/`**. It only reports a readiness status and the
> concrete missing items.

**Readiness gate doc id:** `crypto_d1_readiness_gate_v1` · **version:** `1.0`

**Current readiness status:** **`NOT_READY_FOR_REAL_DATA`**

---

## 0. What this gate is

This is the capstone audit on top of the whole Crypto-D1 stack (Bundles 11–20).
It answers one question conservatively: *is SPARTA ready to accept real
operator-supplied Crypto-D1 data?* The honest answer today is **no**, and the
gate records exactly what is missing.

**NOT_READY_FOR_REAL_DATA is the honest default. Specification completeness is
not data readiness.** The specification + tooling foundation is complete and
safe, but **No real data has entered SPARTA**, so the lane is not data-ready.

```
B11 protocol -> B12 contract -> B13 manifest -> B14 QA/freeze spec
   -> B15 baseline backtest plan -> B16 backtest runner
   -> B17 acquisition authorization (the gate) -> B18 source evaluation
   -> B19 QA runtime tool -> B20 manual intake runbook
   -> [THIS GATE: readiness audit / operator checklist]
   -> (operator action, separately authorized) real data intake -> QA run -> baseline review
```

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (spot only).
- **Timeframe:** daily (`1d`) only. Intraday is out of scope.
- **Session calendar:** 24/7; weekday-only filters are forbidden.

## 2. Audited artifacts (Bundles 11–20)

| Bundle | Artifact | Validator | Status |
|---|---|---|---|
| 11 | `crypto_d1_protocol_v1/protocol.json` | `crypto_d1_protocol_check.py` | OK |
| 12 | `crypto_d1_data_contract_v1/data_contract.json` | `crypto_d1_data_contract_check.py` | OK |
| 13 | `crypto_d1_dataset_manifest_v1/dataset_manifest.json` | `crypto_d1_dataset_manifest_check.py` | OK |
| 14 | `crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.json` | `crypto_d1_qa_freeze_spec_check.py` | OK |
| 15 | `crypto_d1_baseline_backtest_plan_v1/backtest_plan.json` | `crypto_d1_backtest_plan_check.py` | OK |
| 16 | `crypto_d1_backtest_runner_v1/report.json` | `crypto_d1_backtest_runner.py` (code) | OK |
| 17 | `crypto_d1_data_acquisition_authorization_v1/authorization_plan.json` | `crypto_d1_data_acquisition_authorization_check.py` | OK |
| 18 | `crypto_d1_data_source_evaluation_v1/data_source_evaluation.json` | `crypto_d1_data_source_evaluation_check.py` | OK |
| 19 | `crypto_d1_data_qa_runtime_tool_v1/qa_runtime_tool.json` | `crypto_d1_data_qa_runtime_tool.py` (tool) | OK |
| 20 | `crypto_d1_manual_dataset_intake_runbook_v1/runbook.json` | `crypto_d1_manual_dataset_intake_runbook_check.py` | OK |

All 10 artifacts exist on disk and their validators pass. That makes the
**specification foundation complete** — and nothing more.

## 3. The 20 readiness questions

| # | Question | Answer |
|---|---|---|
| 1 | Are all required Crypto-D1 specs/tools/runbooks present? | **YES** |
| 2 | Are all Bundle 17 authorization gates satisfied? | **NO** |
| 3 | Has the operator selected a concrete data source? | **NO** |
| 4 | Is the source class acceptable under Bundle 18? | **NOT_YET** |
| 5 | Is there license/TOS confirmation? | **NO** |
| 6 | Are the required assets confirmed (BTC, ETH, SOL)? | **SPEC_ONLY** |
| 7 | Is market type confirmed as spot only? | **SPEC_ONLY** |
| 8 | Is timeframe confirmed as 1d only? | **SPEC_ONLY** |
| 9 | Is the date range specified? | **NO** |
| 10 | Is dataset_id specified? | **NO** |
| 11 | Is dataset version specified? | **NO** |
| 12 | Is storage path specified? | **SPEC_PATTERN_ONLY** |
| 13 | Is file naming convention specified? | **YES** |
| 14 | Are sha256 checksums ready? | **NO** |
| 15 | Are manifest.json, CHECKSUMS.txt, FREEZE_RECORD.txt, and fees/slippage ready? | **NO** |
| 16 | Has the QA Runtime Tool been run? | **NO** |
| 17 | Is there a QA_PASS or accepted QA_WARN? | **NO** |
| 18 | Is there any baseline backtest output? | **NO** |
| 19 | Is paper/live/micro-live still locked? | **YES** |
| 20 | What is the final readiness status? | **NOT_READY_FOR_REAL_DATA** |

## 4. Missing items (what must exist before real data is ready)

- Operator decision to acquire this cycle (a research decision, not a default).
- Concrete source class (A/B/C/D; never E/F) chosen under Bundle 18.
- Concrete `source_name` (exact vendor / venue / archive).
- `license_or_tos_reference` confirming research use.
- A concrete dataset declaring BTC/ETH/SOL spot at 1d.
- Date range (`time_start`, `time_end`; ISO-8601 UTC).
- `dataset_id` (`CRYPTO_D1_SPOT_<SYMBOLS_TAG>_V<NNN>`) and `dataset_version`.
- A concrete storage path under `data/crypto_d1_research/` (operator-created).
- `fees.json` with per-venue taker fee + slippage.
- `manifest.json` passing `tools/crypto_d1_dataset_manifest_check.py`.
- `CHECKSUMS.txt` with sha256 per dataset file.
- `FREEZE_RECORD.txt` with `freeze_timestamp_utc` + operator + version pins.
- A QA run via `tools/crypto_d1_data_qa_runtime_tool.py` producing `qa_report.json`.
- A QA_PASS or operator-accepted QA_WARN verdict.
- A separately authorized baseline backtest output.

## 5. Readiness status options + rules

| Status | Meaning |
|---|---|
| **NOT_READY_FOR_REAL_DATA** | The honest default. Specs complete + safe, but no source authorized, no license, no data, no folder, no QA, no baseline. **Specification completeness is not data readiness.** |
| **READY_FOR_OPERATOR_DATA_INTAKE** | Only after the operator records a concrete source class, `source_name`, and license/TOS, and confirms BTC/ETH/SOL spot 1d scope. Authorizes nothing automatically. |
| **READY_FOR_QA_RUN** | Only after real frozen data + `manifest.json` + `CHECKSUMS.txt` + `FREEZE_RECORD.txt` + `fees.json` are on disk. The QA run stays a manual operator action. |
| **READY_FOR_BASELINE_BACKTEST_REVIEW** | Only after QA_PASS (or accepted QA_WARN) on real data AND a separately authorized backtest has produced output. |
| **BLOCKED** | A required artifact is missing, a validator fails, a safety flag is unsafe, or an external block is declared. |

## 6. Why NOT_READY_FOR_REAL_DATA is the honest default

- No operator-supplied dataset exists.
- No data source is concretely authorized.
- No data has been fetched; **No real data has entered SPARTA**.
- `data/crypto_d1_research/` does not exist.
- No `manifest.json` / `CHECKSUMS.txt` / `FREEZE_RECORD.txt` / `fees.json` exists.
- No QA run has happened; there is no QA_PASS or accepted QA_WARN.
- No baseline backtest output exists.

**Specification completeness is not data readiness.**

## 7. What this gate does NOT authorize

- **QA_PASS does not authorize automatic backtesting.**
- **QA_PASS does not authorize paper trading.**
- **QA_PASS does not authorize live trading.**
- No data fetch, no exchange connection, no credentials, no order placement.
- It does not create `data/crypto_d1_research/`.
- It does not promote the lane. **Crypto-D1 remains WATCH / MIXED.**
- A good historical chart does not imply future returns.

## 8. Allowed next steps

- **Operator step (NOT a bundle):** follow the Bundle 20 runbook — choose a
  source class (A/B/C/D), acquire BTC/ETH/SOL daily-spot CSV offline, place
  files under `data/crypto_d1_research/<dataset_id>/<dataset_version>/`, author
  `manifest.json` + `CHECKSUMS.txt` + `FREEZE_RECORD.txt` + `fees.json`, then run
  the Bundle 19 QA tool and review the `qa_report`.
- Alternative: keep Crypto-D1 in WATCH; the foundation needs no further spec work.
- Re-run this gate after any operator action to recompute the readiness status.

## 9. Registry status

The Crypto-D1 lane stays **WATCH** with **MIXED** evidence. This gate does
**not** mark the candidate ACTIVE and does **not** make evidence STRONG.
Promotion requires real data + QA_PASS + separate operator authorization that
cannot exist yet.

## 10. No-profit-claim policy

A readiness gate is not strategy validation. Specification completeness is not
data readiness. QA_PASS does not imply profitability. No real data has entered
SPARTA. A good historical chart does not imply future returns. Crypto-D1 remains
WATCH / MIXED.
