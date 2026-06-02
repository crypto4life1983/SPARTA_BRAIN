# SPARTA Crypto-D1 Data Source Evaluation Memo v1 — build report

> **Research-only. Data source evaluation MEMO only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no dataset
> processing in this bundle. No real data files or data directory created.
> No concrete vendor authorized.**

This bundle evaluates **6 candidate source CLASSES** the operator could
choose from when manually executing Bundle 17 step 1 (select an approved
historical OHLCV CSV source whose TOS permits research use). It mirrors
the safe pattern from the existing arbitrage Bundle 8 data-source
evaluation, scoped to BTC / ETH / SOL daily spot.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.json` | Machine-readable memo (validator source of truth). |
| `reports/crypto_d1_data_source_evaluation_v1/data_source_evaluation.md` | Human-readable memo: 6 source classes with explicit verdict + rationale + caveats; 15-field decision matrix; 20 approval gates; forbidden sources; required provenance fields; preferred class with "preferred ≠ approved" caveat; PASS/WATCH/FAIL rules; safety boundaries; no-profit-claim policy. |
| `reports/crypto_d1_data_source_evaluation_v1/report.md` | This build report. |
| `reports/crypto_d1_data_source_evaluation_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_data_source_evaluation_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_data_source_evaluation.py` | 39 tests. |
| `tools/strategy_candidate_registry.py` | Added 2 new memo docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 18 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 19 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, all 6 prior Crypto-D1 spec docs + the runner, 8
arbitrage validators, `tools/strategy_next_bundle.py` (no artificial
selection nudge), `tools/crypto_d1_backtest_runner.py`,
`local_secrets/`, `paper_trading/`, `lessons.md`,
`data/crypto_d1_research/` (NOT created; storage root appears only when
the operator manually places a real dataset).

## What the memo defines

1. **6 source CLASSES** with explicit verdict:

   | ID | Class | Verdict |
   |---|---|---|
   | A | Exchange public historical archives (offline CSV / Parquet) | **ACCEPTABLE** |
   | B | Exchange public APIs (operator-side only; SPARTA never calls) | **WATCH (future-only)** |
   | C | Paid market-data vendors (offline export) | **PREFERRED** |
   | D | Existing local OHLCV files | **ACCEPTABLE** |
   | E | Web-scraped / unofficial tables | **REJECTED for evidence**; WATCH-only context |
   | F | Manually copied prices / screenshots | **REJECTED for any quantitative claim** |

2. **15-field decision matrix** with **`allowed_now = false` on every row**.
   No concrete vendor is authorized by this memo.

3. **Preferred class = C (paid vendors)**, with explicit
   `preferred_does_not_mean_approved = True` and
   `concrete_vendor_selection_requires_bundle_17_gates = True`.

4. **20 approval gates** before any source use — operator authorization,
   source/symbols/time-window/storage-path/dataset_id named, all 6 prior
   bundle versions pinned, TOS verified, no credentials, no network call
   from SPARTA, CHECKSUMS / FREEZE_RECORD produced, manifest passes
   Bundle 13, qa_report passes Bundle 14, QA_PASS or accepted QA_WARN.

5. **Forbidden data sources / methods** — live exchange APIs from
   SPARTA's runtime, scraping, embedded credentials, SPARTA-runtime
   network calls, synthetic / mock data, anonymous provenance,
   OOS-peeked datasets, TOS-incompatible feeds, Class E (evidence
   use), Class F (any quantitative claim).

6. **Required provenance fields per dataset** — `source_class`,
   `source_name`, `source_location`, `license_or_tos_reference`,
   `row_level_source_id`, `file_hash_sha256`, `freeze_timestamp_utc`,
   `operator_name_and_tool_label`, and all 6 version pins.

7. **PASS / WATCH / FAIL rules**, **required future artifacts**,
   **safety boundaries**, **no-profit-claim policy**.

## Safety guarantees (enforced by tests)

- 7 execution / fetch / connection / backtest-execution /
  dataset-processing flags pinned **False**.
- `research_only: true` asserted.
- Lane = `crypto_d1_protocol`; market_type = `spot`; timeframe = `1d`;
  intraday explicitly out of scope.
- BTC / ETH / SOL required.
- All 6 source classes present with explicit `status` field.
- **E status starts with `REJECTED`**.
- **F status starts with `REJECTED`**.
- Decision matrix has 6 rows; every row has all 15 required fields;
  every row has `allowed_now = False`.
- Preferred class declaration includes
  `preferred_does_not_mean_approved = True` and
  `concrete_vendor_selection_requires_bundle_17_gates = True`.
- Approval gates mention operator authorization, all 6 version pins,
  CHECKSUMS.txt, FREEZE_RECORD.txt, no-credentials, no-network-call,
  QA_PASS.
- Forbidden data sources cover live exchange APIs, scraping, API key,
  network call, synthetic data, provenance-cannot-be-cited, Class E,
  Class F.
- Required provenance fields include source_class, source_name,
  license_or_tos_reference, row_level_source_id, file_hash_sha256,
  freeze_timestamp_utc, operator_name.
- `safety_boundaries` carries `research-only`, `no broker`, `no live`,
  `no order`.
- MD carries all 7 distinction phrases.
- Validator scans MD + JSON for 12 forbidden capability claims.
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`).
- Dedicated test asserts **exactly 4 spec files** in bundle dir; no
  `.csv` / `.parquet` / `.pq` / `.pickle` / `.feather` / `.h5` / `.npz`
  / `.pkl` files.
- Dedicated test asserts `data/crypto_d1_research/` was NOT created.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_data_source_evaluation.py --rootdir=tests -q
→ 39 passed

python -m pytest <all 17 test files> --rootdir=tests -q
→ 470 passed across Bundles 2-18
```

## JSON validity

```
python tools/crypto_d1_data_source_evaluation_check.py validate           → validate: OK
python tools/crypto_d1_data_acquisition_authorization_check.py validate   → validate: OK
python tools/crypto_d1_backtest_plan_check.py validate                    → validate: OK
python tools/crypto_d1_qa_freeze_spec_check.py validate                   → validate: OK
python tools/crypto_d1_dataset_manifest_check.py validate                 → validate: OK
python tools/crypto_d1_data_contract_check.py validate                    → validate: OK
python tools/crypto_d1_protocol_check.py validate                         → validate: OK
python tools/arbitrage_readiness_gate_check.py validate                   → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate              → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate           → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate                  → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate                 → validate: OK
python tools/arbitrage_data_contract_check.py validate                    → validate: OK
python tools/arbitrage_protocol_check.py validate                         → validate: OK
python tools/strategy_candidate_registry.py validate                      → validate: OK
python tools/strategy_next_bundle.py validate                             → validate: OK
```

## Does local data exist?

**No.** `data/crypto_d1_research/` does NOT exist on disk. This bundle
authored documentation only; it did not create the storage root, did
not place any CSV file, and did not name a concrete vendor.

## Were any real data files created?

**No.** The bundle directory contains exactly 4 spec files. Zero
`.csv` / `.parquet` / `.pq` / `.pickle` / `.feather` / `.h5` / `.npz`
/ `.pkl` files.

## Was any concrete vendor authorized?

**No.** This memo evaluates source CLASSES only. Every row in the
decision matrix has `allowed_now = false`. Concrete vendor selection
still requires explicit operator authorization through Bundle 17's 20
approval gates.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires; seed's
  `extra_files` now include 14 docs: protocol×2 + data_contract×2 +
  dataset_manifest×2 + qa_freeze_spec×2 + backtest_plan×2 +
  authorization_plan×2 + data_source_evaluation×2, all on disk).
- **evidence_level:** `MIXED`.
- **source_reports** grew from 27 (Bundle 17) → 29 (Bundle 18).
- Guards held: **never ACTIVE / never STRONG**.

## How this follows Crypto-D1 Authorization Plan v1

1. Bundle 17 step 1 says: *"Operator MANUALLY selects an approved
   historical OHLCV CSV source whose terms of service explicitly
   permit research use."*
2. This memo evaluates the 6 candidate classes the operator could
   choose from, ranks them by suitability for the Crypto-D1 protocol,
   and pins explicit caveats per class.
3. The memo does NOT authorize any specific vendor or archive. Every
   row carries `allowed_now = false`. Concrete selection still
   requires Bundle 17's 20 approval gates.
4. The 20 approval gates in this memo are aligned one-for-one with
   Bundle 17's `approval_gates`, plus a Bundle-18-specific addition:
   "Source CLASS must be one of A/B/C/D; never E/F."

## How this follows the arbitrage Bundle 8 pattern

Bundle 8 (`reports/arbitrage_data_source_evaluation_v1/`) established
the 6-class A→F evaluation pattern with `allowed_now = false` and
REJECTED status for E + F. Bundle 18 mirrors that exact pattern,
scoped to BTC / ETH / SOL daily spot, with class C (paid vendors)
elevated to PREFERRED for the Crypto-D1 protocol's evidence needs.

## Recommended next step

- **Operator step (NOT a bundle):** operator MANUALLY chooses a
  source class (A/B/C/D; never E/F) and a concrete vendor or archive
  name; documents TOS; then runs the 11 remaining Bundle 17 manual
  steps.
- **Crypto-D1 Baseline Results Report v1** (separately authorized;
  only after operator has supplied data AND the runner has produced
  output).
- **Optional: Crypto-D1 Data QA Runtime Tool v1** (code bundle;
  recommend Codex).
- **Optional: Crypto-D1 Backtest Runner v2** (future code bundle;
  recommend Codex).

## Safety boundaries (pinned, non-negotiable)

- Research-only. Data source evaluation MEMO only.
- No broker control, no exchange connection, no API keys, no
  `.env`, no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls.
- **No data fetch. No dataset processing. No real data files or data
  directory created in this bundle. No concrete vendor authorized.**
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
