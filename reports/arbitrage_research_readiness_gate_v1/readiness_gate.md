# SPARTA Arbitrage Research Readiness Gate v1

> **Research-only. Readiness gate / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No
> backtest. No dataset processing in this bundle.** This document audits the
> completed arbitrage specification stack (six documents) and produces a
> conservative readiness decision.

**Readiness gate id:** `arbitrage_research_readiness_gate_v1` ·
**version:** `1.0`

**Companion documents:**
[`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md) ·
[`arbitrage_data_contract_v1`](../arbitrage_data_contract_v1/data_contract.md) ·
[`arbitrage_dataset_manifest_v1`](../arbitrage_dataset_manifest_v1/dataset_manifest.md) ·
[`arbitrage_qa_harness_spec_v1`](../arbitrage_qa_harness_spec_v1/qa_harness_spec.md) ·
[`arbitrage_data_source_evaluation_v1`](../arbitrage_data_source_evaluation_v1/data_source_evaluation.md) ·
[`arbitrage_sample_dataset_plan_v1`](../arbitrage_sample_dataset_plan_v1/sample_dataset_plan.md).

---

## Verdict

# **`readiness_status: WATCH`**

**Decision:** The arbitrage research foundation is **complete at the
specification level**. All six arbitrage documents exist, all eight
associated validators pass, all execution / fetch / connection / backtest
/ dataset-processing safety flags are pinned `False`, and there is **NO
data**, **NO QA report**, **NO tested edge**, and **NO evidence**.

Per this gate's own rules, **WATCH is the only honest verdict**: the lane
is research-monitorable but is **NOT cleared for data collection, NOT
cleared for backtest, NOT cleared for paper or live trading**. Promotion
past WATCH requires evidence that cannot exist yet (no data has been
pulled).

## 1. Research objective

Audit the completed arbitrage specification stack (six documents) and
produce a clear, conservative readiness decision: **PASS / WATCH /
BLOCKED / PARKED**. This gate **does not authorize data collection**,
**does not authorize backtesting**, and **does not authorize paper or
live trading**. It records the state of the foundation and the strict,
named gates that future bundles must pass.

## 2. Audited artifacts

| # | Artifact | Path | Exists | Validator | Status |
|---|---|---|:-:|---|:-:|
| 1 | Arbitrage Research Protocol v1 | `reports/arbitrage_research_protocol_v1/protocol.json` | ✅ | `arbitrage_protocol_check.py` | **OK** |
| 2 | Arbitrage Data Contract v1 | `reports/arbitrage_data_contract_v1/data_contract.json` | ✅ | `arbitrage_data_contract_check.py` | **OK** |
| 3 | Arbitrage Dataset Manifest v1 | `reports/arbitrage_dataset_manifest_v1/dataset_manifest.json` | ✅ | `arbitrage_dataset_manifest_check.py` | **OK** |
| 4 | Arbitrage QA Harness Spec v1 | `reports/arbitrage_qa_harness_spec_v1/qa_harness_spec.json` | ✅ | `arbitrage_qa_harness_spec_check.py` | **OK** |
| 5 | Arbitrage Data Source Evaluation Memo v1 | `reports/arbitrage_data_source_evaluation_v1/data_source_evaluation.json` | ✅ | `arbitrage_data_source_evaluation_check.py` | **OK** |
| 6 | Arbitrage Sample Dataset Plan v1 | `reports/arbitrage_sample_dataset_plan_v1/sample_dataset_plan.json` | ✅ | `arbitrage_sample_dataset_plan_check.py` | **OK** |

### Per-artifact role + remaining limitations

- **Protocol (P0)** — defines what arbitrage means, 5 categories
  (statistical_relative_value labelled **NOT pure arbitrage**), validation
  phases P0..P6, PASS/WATCH/FAIL/PARK/RETIRE, kill conditions. *Limit:* no
  live data; no backtest authorized.
- **Data Contract (P1)** — what data would be required per category, with
  timestamp / cost / liquidity / order-book / trade-print / fee / funding /
  quality / normalization rules + MVT + allowed/forbidden sources. *Limit:*
  no data acquired; spec only.
- **Dataset Manifest** — schema every future per-dataset manifest must
  satisfy (32 fields), 7-status freeze/QA model, freeze rules. *Limit:*
  no real manifest authored beyond the spec.
- **QA Harness Spec** — 8 QA check groups, 6-status QA model
  (QA_DRAFT/QA_PASS/QA_WARN/QA_FAIL/QA_BLOCKED/QA_RETIRED), 23-field
  future QA report schema, explicit *"QA_PASS does NOT imply
  profitability / backtest / live"*. *Limit:* spec only; no harness
  implementation.
- **Data Source Evaluation** — 6 source classes evaluated (E web-scraped
  + F manual REJECTED; C paid vendors PREFERRED), `allowed_now=False`
  everywhere, 15-field decision matrix, 15 approval gates. *Limit:* no
  source approved; no data pulled.
- **Sample Dataset Plan** — TINY first sample plan (primary
  cross_exchange_spot, BTC_USDT / ETH_USDT example-only, 1h / 1d window
  shape with no dates set), 19 approval gates, 11-step future-collection
  checklist. *Limit:* no real files created; venues / symbols / time
  window still pending future operator approval.

## 3. Required artifact checks

- All 6 audited artifacts **exist on disk**. ✅
- All 6 validators return `validate: OK`. ✅
- All 6 documents pin **all execution / fetch / connection / backtest /
  dataset-processing safety flags False**. ✅
- **Word discipline preserved** across all 6 documents (Pure arbitrage
  vs. **NOT pure arbitrage** vs. **RELATIVE_VALUE**). ✅

## 4. Validator checks

The following tools must be present and return `validate: OK`:

- `tools/arbitrage_protocol_check.py`
- `tools/arbitrage_data_contract_check.py`
- `tools/arbitrage_dataset_manifest_check.py`
- `tools/arbitrage_qa_harness_spec_check.py`
- `tools/arbitrage_data_source_evaluation_check.py`
- `tools/arbitrage_sample_dataset_plan_check.py`
- `tools/strategy_candidate_registry.py`
- `tools/strategy_next_bundle.py`

**All 8 validators pass** ✅.

## 5. Safety checks

- All execution flags `False` across all 6 arbitrage docs. ✅
- No forbidden capability phrases in any doc. ✅
- No real data files present in any arbitrage report dir. ✅
- No credentials required by any arbitrage tool or doc. ✅
- No paper / live execution files modified by any arbitrage bundle. ✅
- No JARVIS / dashboard files modified by any arbitrage bundle. ✅
- No sealed artifacts touched. ✅

## 6. Missing items / blockers

- **Missing items:** none.
- **Blockers:** none. (The absence of data is **expected** and is what
  produces the WATCH verdict; it is not a blocker against the
  specification stack itself.)

## 7. Allowed next steps

- Author a **SEPARATE Arbitrage Data Collection Authorization Draft**
  bundle (still spec-only; no fetch) that proposes the exact source class
  + instance + venues + symbols + time window + storage path for the
  first TINY sample, citing Bundles 8 and 9 and this gate.
- **Alternative:** move to a **different lane** (e.g., Crypto-D1 Protocol
  Memo). The arbitrage lane is research-monitorable but does not need
  more spec work.
- **Alternative:** pause the arbitrage lane and prioritize the
  cross-cutting **Data QA / Freeze workflow** that benefits multiple
  lanes.

## 8. Forbidden next steps

- ✗ Do **not** fetch data of any kind from this gate.
- ✗ Do **not** connect to any exchange from this gate.
- ✗ Do **not** run any backtest from this gate.
- ✗ Do **not** process any dataset from this gate.
- ✗ Do **not** place any order anywhere from this gate.
- ✗ Do **not** enable paper-order execution.
- ✗ Do **not** enable live trading.
- ✗ Do **not** install any credentials / API keys / `.env` / private keys.
- ✗ Do **not** install any scheduler / cron / daemon.
- ✗ Do **not** modify paper or live execution files.
- ✗ Do **not** mark the arbitrage lane ACTIVE or STRONG.
- ✗ Do **not** claim profitability, edge, or live-readiness.

## 9. Future authorization gates

### A. Data collection gate (NOT authorized by this readiness gate)

Future data collection is allowed **only after** all of the following:

- explicit operator authorization
- exact source class from Bundle 8 selected (A / B / C / D only — **never
  E web-scraped, never F manual**)
- exact venue / source named
- exact symbols named
- exact time window named
- exact storage path named
- protocol version referenced
- data contract version referenced
- dataset manifest version referenced
- QA harness spec version referenced
- data source evaluation version referenced
- sample dataset plan version referenced
- no credentials unless separately approved
- no private keys
- no trading permissions
- TOS / licensing review if applicable
- **separate data-collection bundle approved**

### B. Backtest / research-test gate (NOT authorized by this readiness gate)

Future backtest is allowed **only after** all of the following:

- data collection complete (under its own separate authorization)
- per-dataset manifest frozen (`freeze_status == FROZEN`)
- QA report created (under the QA harness spec's 23-field schema)
- `qa_status == QA_PASS` or approved `QA_WARN` with operator-acceptance
  memo
- cost assumptions documented (fees / spread / slippage / funding /
  borrow / withdrawal / counterparty haircut)
- no-lookahead check (features available at decision time only)
- no execution claims (no live / paper / order placement)
- **separate backtest bundle approved**

### C. Paper / live trading gate (**EXPLICITLY FORBIDDEN by this gate**)

- **Forbidden by this readiness gate.**
- Requires a separate, far-future authorization **after evidence exists**.
- Note: this gate does not authorize trading and never will. A separate
  future protocol / specification / authorization stack would be
  required, and even then only after multi-bundle evidence is produced.

## 10. PASS / WATCH / BLOCKED / PARKED rules

- **PASS** — All 6 arbitrage docs exist, all validators pass, all safety
  flags pinned False, all required approvals are documented, AND the only
  next step is a future operator-authorized data collection. **PASS does
  NOT imply edge or profitability** — it certifies that the specification
  stack is complete and safe to authorize a P2 data-collection bundle on.
- **WATCH** — Docs and validators are complete, but arbitrage still has
  no evidence, no data, no QA report, and no tested edge. **This is the
  expected status for the foundation lane.**
- **BLOCKED** — Required docs are missing, validators fail, safety flags
  are unsafe, or approval gates are missing.
- **PARKED** — Protocol is complete but arbitrage is not worth pursuing
  now compared to another lane (operator-driven judgement; not a verdict
  on the lane's correctness).

## 11. Lane recommendation

- **Current verdict:** **WATCH**.
- **Rationale:** Foundation specification is COMPLETE. No data has been
  pulled. No evidence exists. The next move is operator-driven: either
  author a Data Collection Authorization Draft (still spec-only) OR pivot
  to a different research lane (e.g., Crypto-D1 Protocol Memo).
- **Do NOT promote to ACTIVE.**
- **Do NOT promote to STRONG evidence.**
- Promotion path **only via data + QA + a separate future
  authorization**.

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Readiness gate / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  gate's runtime.
- **No data fetch. No backtest. No dataset processing in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence.
- A price gap is not profit. Specification completion is not edge.
  **WATCH does not imply edge.**
