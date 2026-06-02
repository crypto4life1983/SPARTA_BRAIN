# SPARTA Crypto-D1 Operator Missing Items Checklist v1

> **Research-only. Operator checklist / template only.**
> This checklist **authorizes nothing operational**. No data fetch. No exchange
> connection. No API keys. No `.env`. No credential handling. No QA run against
> real data. No backtest. No broker / live / paper / micro-live trading. No
> scheduler / daemon. No external network calls. It does **not** create
> `data/crypto_d1_research/`. It is a fillable template for the 16 missing
> items reported by the Bundle 21 readiness gate.

**Checklist doc id:** `crypto_d1_operator_missing_items_checklist_v1` ·
**version:** `1.0`

**Default overall readiness status:** **`NOT_READY_FOR_REAL_DATA`**

**NOT_READY_FOR_REAL_DATA is the honest default.** Specification completeness is not data readiness. No real data has entered SPARTA. Crypto-D1 remains WATCH / MIXED.

**Companion documents:**
- Bundle 17 — `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.{json,md}`
- Bundle 18 — `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.{json,md}`
- Bundle 19 — `reports/crypto_d1_data_qa_runtime_tool_v1/qa_runtime_tool.{json,md}` (implements `tools/crypto_d1_data_qa_runtime_tool.py`)
- Bundle 20 — `reports/crypto_d1_manual_dataset_intake_runbook_v1/runbook.{json,md}`
- Bundle 21 — `reports/crypto_d1_readiness_gate_v1/readiness_gate.{json,md}`

---

## 0. What this checklist is

The Bundle 21 readiness gate produces a single conservative verdict
(`readiness_status = NOT_READY_FOR_REAL_DATA`) and a prose list of 16
missing items. This checklist turns that prose into a **structured,
fillable, schema-validated template** the operator works through
item-by-item.

- Every item starts at `status = MISSING` with empty
  `operator_answer` / `evidence_path` / `reviewer_notes` and
  `approval_status = PENDING`.
- An item can only move to `status = COMPLETE` when **both** `evidence_path`
  is non-empty **and** `approval_status = APPROVED`. The validator rejects any
  checklist that violates that rule.
- The overall verdict stays `NOT_READY_FOR_REAL_DATA` until every required
  item is COMPLETE (or explicitly documented as BLOCKED with a recorded
  `overall_readiness_status_override_reason`).
- This checklist authorizes **nothing**. It is a record of operator progress.

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC**, **ETH**, **SOL** (spot only).
- **Timeframe:** daily (`1d`) only. Intraday is out of scope.
- **Session calendar:** 24/7; weekday-only filters are forbidden.

## 2. Item status options

| Status | Meaning |
|---|---|
| **MISSING** | Default. The operator has not yet provided an answer + evidence. |
| **COMPLETE** | The operator has filled `operator_answer` and `evidence_path` and the reviewer has set `approval_status = APPROVED`. |
| **BLOCKED** | An external block prevents completion (e.g., license unclear, vendor unresponsive); `blocking_reason` MUST be non-empty. |
| **NOT_APPLICABLE** | The item does not apply in this cycle (rare; requires `reviewer_notes` to explain). |

## 3. Approval status options

| Status | Meaning |
|---|---|
| **PENDING** | Default. No approval decision yet. |
| **APPROVED** | Reviewer approves the operator's answer + evidence. Required for `status = COMPLETE`. |
| **REJECTED** | Reviewer rejects the answer; operator must revise. |
| **WITHDRAWN** | Operator withdraws the answer (e.g., switched source). |

## 4. The 16 items

Current status as of 2026-06-02 (dataset `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V001`
frozen). Items 5–13 are COMPLETE / APPROVED with on-disk evidence. Items 1–4
remain operator-driven (item 4 License/TOS stays PENDING while
`FREEZE_RECORD.txt` carries a TOS-evidence placeholder). Items 14–16 stay
MISSING: no QA run, no QA_PASS, no baseline backtest. The overall verdict stays
`NOT_READY_FOR_REAL_DATA`.

| # | Name | Status | Approval | Notes |
|---|---|---|---|---|
| 1 | Operator acquire-decision | MISSING | PENDING | A research decision, not a default. |
| 2 | Source class | MISSING | PENDING | A/B/C/D only — never E (web-scraped) or F (manual). |
| 3 | Source name | MISSING | PENDING | Exact vendor / venue / archive identity. |
| 4 | License/TOS confirmation | MISSING | PENDING | Stays PENDING — `FREEZE_RECORD.txt` TOS-evidence reference is still a placeholder. |
| 5 | BTC/ETH/SOL spot 1D dataset | COMPLETE | APPROVED | Spot-only daily BTC/ETH/SOL; `daily_ohlcv.csv` frozen. |
| 6 | Date range | COMPLETE | APPROVED | `time_start` 2021-06-17 → `time_end` 2025-12-31 (UTC) in manifest. |
| 7 | `dataset_id` | COMPLETE | APPROVED | `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001` matches pattern. |
| 8 | `dataset_version` | COMPLETE | APPROVED | `V001` — first immutable freeze. |
| 9 | Storage path | COMPLETE | APPROVED | `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V001/` exists. |
| 10 | `fees.json` | COMPLETE | APPROVED | Taker 40bps + slippage 10bps declared (FILLED_PENDING_QA). |
| 11 | `manifest.json` | COMPLETE | APPROVED | Passes `tools/crypto_d1_dataset_manifest_check.py validate`. |
| 12 | `CHECKSUMS.txt` | COMPLETE | APPROVED | sha256 per frozen dataset file. |
| 13 | `FREEZE_RECORD.txt` | COMPLETE | APPROVED | `freeze_timestamp` + operator + 3 version pins. |
| 14 | QA run / `qa_report.json` | MISSING | PENDING | No QA run yet. Via `tools/crypto_d1_data_qa_runtime_tool.py run`. |
| 15 | QA_PASS or accepted QA_WARN | MISSING | PENDING | No QA_PASS / accepted QA_WARN. QA_FAIL / QA_BLOCKED do NOT satisfy this item. |
| 16 | Baseline backtest output | MISSING | PENDING | No baseline backtest. Requires a separately authorized backtest bundle first. |

## 5. Per-item required fields (every item carries all 9)

- `number` — 1..16
- `name` — item title
- `status` — MISSING / COMPLETE / BLOCKED / NOT_APPLICABLE
- `operator_answer` — the operator's filled answer (empty by default)
- `evidence_path` — pointer to the evidence on disk or external system
- `reviewer_notes` — free-form reviewer text (initials, caveats, conditions)
- `approval_status` — PENDING / APPROVED / REJECTED / WITHDRAWN
- `blocking_reason` — required non-empty when status = BLOCKED
- `next_action` — concrete next step for this item

## 6. Anti-fake-completion rules

The validator REJECTS any checklist that violates any of these:

1. An item with `status = COMPLETE` must have **non-empty** `evidence_path`.
2. An item with `status = COMPLETE` must have `approval_status = APPROVED`.
3. An item with `status = BLOCKED` must have **non-empty** `blocking_reason`.
4. If any item is COMPLETE while `overall_readiness_status` remains
   `NOT_READY_FOR_REAL_DATA`, the field
   `overall_readiness_status_override_reason` must explicitly document why
   (e.g., "items 1-13 COMPLETE but item 14 BLOCKED pending vendor delivery").

## 7. Consistency rule

`overall_readiness_status` is the truth of record. The default — and the
correct value while any required item is MISSING without an override — is
`NOT_READY_FOR_REAL_DATA`. Items moving to COMPLETE never automatically
promote the overall status; promotion requires re-running the Bundle 21
readiness gate against the current checklist state.

## 8. What this checklist does NOT authorize

- No data fetch. No exchange connection. No credentials. No order placement.
- **QA_PASS does not authorize automatic backtesting.**
- **QA_PASS does not authorize paper trading.**
- **QA_PASS does not authorize live trading.**
- A good historical chart does not imply future returns.
- It does not create `data/crypto_d1_research/`.
- It does not promote the lane. **Crypto-D1 remains WATCH / MIXED.**

## 9. Allowed next steps

- **Operator step (NOT a bundle):** operator follows the Bundle 20 runbook,
  fills items 1–13 with evidence, then runs the Bundle 19 QA tool to populate
  item 14 with a `qa_report.json` path. Item 15 follows from QA_PASS or an
  accepted QA_WARN with operator memo. Item 16 requires a separately
  authorized backtest bundle.
- After any operator fill, **re-run**
  `python tools/crypto_d1_operator_missing_items_checklist_check.py validate`
  to catch fake-completion or inconsistency.
- After items 1–15 are COMPLETE, re-run the Bundle 21 readiness gate to
  recompute the overall verdict.
- Alternative: keep Crypto-D1 in WATCH; the foundation needs no further spec
  work.

## 10. Forbidden next steps

- ✗ Do not fetch data of any kind from this checklist.
- ✗ Do not connect to any exchange.
- ✗ Do not run any QA against real data.
- ✗ Do not run any backtest.
- ✗ Do not create `data/crypto_d1_research/`.
- ✗ Do not mark any item COMPLETE without non-empty `evidence_path` AND
  `approval_status = APPROVED`.
- ✗ Do not place any order. Do not enable paper / live / micro-live.
- ✗ Do not install credentials / API keys / `.env` / private keys.
- ✗ Do not install scheduler / cron / daemon.
- ✗ Do not mark the Crypto-D1 lane ACTIVE or STRONG.
- ✗ Do not claim profitability, edge, or live-readiness.

## 11. Registry status

The Crypto-D1 lane stays **WATCH** with **MIXED** evidence. This checklist
does **not** mark the candidate ACTIVE and does **not** make evidence
STRONG. Promotion requires real data + QA_PASS + separate operator
authorization that cannot exist yet.

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Operator checklist / template only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls.
- **No data fetch. No QA run against real data. No backtest in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence.

## 13. No-profit-claim policy

A checklist is not strategy validation. **Specification completeness is not
data readiness.** QA_PASS does not imply profitability. **QA_PASS does not
authorize live trading. QA_PASS does not authorize paper trading. QA_PASS
does not authorize automatic backtesting.** **No real data has entered
SPARTA.** **A good historical chart does not imply future returns.**
**Crypto-D1 remains WATCH / MIXED.**
