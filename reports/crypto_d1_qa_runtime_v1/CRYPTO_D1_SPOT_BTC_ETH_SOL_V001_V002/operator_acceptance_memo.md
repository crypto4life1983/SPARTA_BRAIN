# Operator Acceptance Memo: Crypto-D1 Kraken V002 (QA_WARN)

**Status: Operator-accepted QA_WARN. Research-only. Does not authorize a backtest, paper, or live trading.**

| Field | Value |
|---|---|
| Dataset ID | CRYPTO_D1_SPOT_BTC_ETH_SOL_V001 |
| Dataset version | V002 |
| QA report ID | f0111872581a873e |
| QA verdict | QA_WARN (37 checks: 36 PASS / 1 WARN / 0 FAIL) |
| QA report (committed) | `reports/crypto_d1_qa_runtime_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/qa_report.{json,md}` |
| Official master at acceptance | 75c03bc |
| Memo author | Mahmoud Cherif (operator) |
| Acceptance date | 2026-06-03 |

### 1. QA_WARN verdict
The Crypto-D1 QA harness (`crypto_d1_data_qa_runtime_tool_v1`) ran 37 mechanical checks across 7 groups against V002. Result: **0 failures, 1 warning, 36 passes -> QA_WARN**. `blocking_failures` is empty. The V001 freeze-record blocker (`freeze_record_has_timestamp`) is now **PASS** ("freeze_timestamp_utc present"), and all freeze/checksum/OHLCV/volume/source/fee checks pass.

### 2. Exact warning
One warning only -- `missing_days_reconciled` (group **B_timestamp**), severity **WARN**:
> "missing days observed: [{'symbol': 'BTC', 'missing_days': 1}]; manifest's missing_day_policy text present"

This is BTC missing the single daily bar of **2024-03-31** (BTC observed 1658 vs expected 1659; ETH and SOL complete). No other warning exists.

### 3. Why the warning is accepted
- The gap is **a single BTC daily bar** out of 4,976 rows (~0.02% of the dataset; ~0.06% of BTC's series).
- It is **disclosed, not hidden**: the manifest's `missing_day_list` names the exact date (2024-03-31) and `missing_day_policy` states missing bars are flagged per asset and **never silently forward-filled**.
- The harness graded this WARN (not FAIL) precisely *because* the policy text is present -- the data was not silently patched.
- A daily-timeframe model can tolerate one isolated missing session without compromising research validity, provided downstream logic treats the gap as a true gap.
- **No FAIL conditions exist** -- OHLC self-consistency, positivity, UTC storage, no duplicates, checksums, and freeze record all PASS.

### 4. Why this does NOT become QA_PASS
QA_WARN and QA_PASS are **distinct mechanical verdicts** emitted by the harness; an operator memo cannot rewrite the verdict. The dataset genuinely has one unreconciled missing bar, so the honest machine verdict is QA_WARN and it stays QA_WARN. This memo records that the operator **accepts the WARN as a known limitation** -- it does not upgrade, override, or relabel the verdict. Any future QA_PASS would require a *new dataset version* whose data actually closes the gap and re-earns PASS from the harness.

### 5. Why this does NOT authorize a backtest yet
Per the Crypto-D1 protocol and the QA report's own `safety_notes`/`allowed_next_step`, a QA_PASS/QA_WARN report is a **precondition** for a backtest plan, **never the authorization itself**. The report's `allowed_next_step` is literally: *"Attach a written operator-acceptance note to the manifest before any backtest plan references the dataset."* This memo *is* that note -- but attaching it only unlocks the right to **separately propose** a backtest plan; it does not run or approve one. `forbidden_next_steps` explicitly bars trading on a QA verdict.

### 6. Why this does NOT authorize paper/live trading
A QA report is a **data-quality** artifact, not a trading authorization. The manifest's `forbidden_use` and the report's `safety_flags` confirm the lane is research-only: `live_trading_enabled=false`, `paper_order_execution_enabled=false`, `order_placement_enabled=false`, `exchange_connection_enabled=false`, `data_fetch_enabled=false`, `broker_control_enabled=false`, `research_only=true`. No clean dataset, and no backtest result, can move those flags -- that requires separate, explicit operator decisions far downstream of data QA.

### 7. Crypto-D1 remains WATCH / MIXED
Accepting a clean *dataset* says nothing about *strategy* conviction. The `crypto_d1_protocol` stays at **WATCH / MIXED**. This memo does not promote it toward ACTIVE/STRONG -- doing so is explicitly a `forbidden_next_step` ("Promote crypto_d1_protocol to ACTIVE / STRONG without a separate operator decision").

### 8. Dataset remains research-only
V002 stays an **offline, research-only** input. `freeze_status=FROZEN` (checksummed/immutable), `QA_status` reflects QA_WARN. No network call was made to obtain it; no daemon/cron may touch the tool; no credentials/keys are read; no synthetic data is admitted as evidence.

### 9. Next allowed step after acceptance
The **only** thing this acceptance unlocks is the right to **draft a baseline backtest *plan*** for V002 -- planning/pre-registration only, **separately approved** before any execution. It does **not** run a backtest, does not start Bundle 23, and does not patch the normalization tool. Each of those remains a distinct, individually-gated future decision.

### 10. Memo location
This memo is stored at `reports/crypto_d1_qa_runtime_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/operator_acceptance_memo.md`, co-located with the `qa_report.{json,md}` it accepts. It is deliberately **outside** the FROZEN dataset folder `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002/`, so no frozen file and no CHECKSUMS.txt entry is touched by writing it.
