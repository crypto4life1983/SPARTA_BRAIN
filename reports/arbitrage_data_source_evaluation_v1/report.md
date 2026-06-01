# SPARTA Arbitrage Data Source Evaluation Memo v1 — build report

> **Research-only. Memo / specification only.** No broker, no live trading,
> no paper-order execution, no exchange connection, no API keys, no
> scheduler, no external network calls, **no data fetch, no backtest, no
> dataset processing in this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_data_source_evaluation_v1/data_source_evaluation.json` | Machine-readable evaluation memo (validator source of truth). |
| `reports/arbitrage_data_source_evaluation_v1/data_source_evaluation.md` | Human-readable memo: 6 source-class evaluations + decision matrix + approval gates + rejection rules + required metadata + expected risks + quality dimensions + future allowed/forbidden plans + required future artifacts + PASS/WATCH/FAIL + no-profit-claim policy + safety boundaries. |
| `reports/arbitrage_data_source_evaluation_v1/report.md` | This build report. |
| `reports/arbitrage_data_source_evaluation_v1/report.json` | Build report (machine). |
| `tools/arbitrage_data_source_evaluation_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_arbitrage_data_source_evaluation.py` | 23 tests covering schema, safety, integration. |
| `tools/strategy_candidate_registry.py` | `extra_files` extended with the new evaluation docs for the arbitrage seed; lane stays **IDEA**. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 8 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 9 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code,
sealed data, Bundle 4/5/6/7 validator tools, `lessons.md`.

## What the data source evaluation defines

1. **Six source classes** evaluated with pros, cons, risk dimensions, and
   future approval requirements:
   - **A** Exchange public historical archives — **ACCEPTABLE**
     (`allowed_now=False`, `future_possible=true`).
   - **B** Exchange public APIs — **WATCH** (future-only; strict no-use in
     this bundle).
   - **C** Paid market data vendors — **PREFERRED** (operator-supplied
     offline export flow preferred over live-API flow).
   - **D** Existing local CSV datasets — **ACCEPTABLE** (after provenance
     memo + sha256 + contract pin + QA_PASS).
   - **E** Web-scraped / unofficial — **REJECTED** for evidence;
     WATCH-with-warning only for anecdotal exploration.
   - **F** Manually copied / screenshots — **REJECTED** for any
     quantitative claim; anecdotal-note use only.
2. **Decision matrix** with 15 required fields per row (source_class,
   allowed_now, future_possible, requires_operator_authorization,
   requires_manifest, requires_QA, supports_order_book, supports_fees,
   supports_funding, timestamp_quality, legal_tos_risk, cost_risk,
   evidence_quality, recommended_status, notes). `allowed_now` is `false`
   for **every** row.
3. **Approval gates** — 15 conditions that must all be satisfied before
   any future data collection (explicit operator authorization, exact
   source / symbols / venues / time window / storage path / data-contract
   version / dataset-manifest version / QA-harness-spec version named;
   no credentials / no private keys / no trading permissions / no
   scheduler / no live or paper execution; TOS/licensing review).
4. **Rejection rules** — runtime network call, embedded keys / OAuth /
   `.env`, manually-copied / screenshots for quantitative claims,
   web-scraping for evidence, TOS-forbidden feeds, untraceable provenance,
   peeked OOS.
5. **Required metadata** for any future acquisition (source_class,
   source_instance_name, license_or_tos_pin, expected coverage / timestamp
   quality / depth / fees / cost / storage path / provenance attestation /
   approval message reference).
6. **Expected risks** + **source-quality dimensions** + **future
   allowed/forbidden source plan** + **required future artifacts** +
   **PASS/WATCH/FAIL rules** + **no-profit-claim policy** + **safety
   boundaries**.

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest / dataset-processing
  flags pinned **False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `backtest_enabled`, `dataset_processing_enabled`.
- `research_only: true` asserted.
- `allowed_now` is **False for every source class** (asserted by both the
  validator and the test suite).
- Manually-copied (F) and web-scraped (E) are **REJECTED** (validator
  rejects any other status).
- Approval gates include explicit operator authorization plus all the
  version-pin references.
- Validator scans MD + JSON for forbidden capability claims (`guaranteed
  profit`, `risk-free profit`, `live-ready`, `production-ready`, `place
  the order`, `connect to exchange`, `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 149 passed in 1.47s
```

- `test_arbitrage_data_source_evaluation.py` — **23 new tests** (Bundle 8).
- Bundle 7 (`test_arbitrage_qa_harness_spec.py`) — 22 still pass.
- Bundle 6 (`test_arbitrage_dataset_manifest.py`) — 19 still pass.
- Bundle 5 (`test_arbitrage_data_contract.py`) — 16 still pass.
- Bundle 4 (`test_arbitrage_research_protocol.py`) — 14 still pass.
- Bundle 3 (`test_strategy_candidate_registry.py`) — 16 still pass.
- Bundle 2 (`test_strategy_next_bundle.py`) — 24 still pass after the
  `extra_files` extension to the arbitrage seed.

## JSON validity

```
python tools/arbitrage_data_source_evaluation_check.py validate  → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate         → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate        → validate: OK
python tools/arbitrage_data_contract_check.py validate           → validate: OK
python tools/arbitrage_protocol_check.py validate                → validate: OK
python tools/strategy_candidate_registry.py validate             → validate: OK
python tools/strategy_next_bundle.py validate                    → validate: OK
```

## How this fits after QA Harness Spec v1

```
Arbitrage Research Protocol v1     (30dabc4)
        ↓
Arbitrage Data Contract v1         (c4d4c8b)
        ↓
Arbitrage Dataset Manifest v1      (492fcc1)
        ↓
Arbitrage QA Harness Spec v1       (8073bf3)
        ↓
Arbitrage Data Source Evaluation Memo v1  (this bundle)
        ↓
(separate bundles, separately authorized)
   Arbitrage Sample Dataset Plan v1 / Arbitrage Research Readiness Gate / P2 acquisition / …
```

The five-document arbitrage spec layer now covers WHAT arbitrage is, WHAT
data is needed, HOW each dataset is declared/frozen, HOW each dataset is
QA'd, and WHICH data sources could ever satisfy these requirements — **all
before** any data has been pulled, any source has been contacted, or any
test has been run.

## Candidate registry status for arbitrage after build

- **status:** `IDEA` ✅ (unchanged — additional docs carry only protocol /
  data / manifest / qa / evaluation keywords)
- **evidence_level:** `MIXED` (**10** matched docs now; no test/baseline/
  OOS evidence; cannot reach `STRONG`)
- **source_reports:** `["data_contract.json", "data_contract.md",
  "data_source_evaluation.json", "data_source_evaluation.md",
  "dataset_manifest.json", "dataset_manifest.md", "protocol.json",
  "protocol.md", "qa_harness_spec.json", "qa_harness_spec.md"]`
- Guard held: never ACTIVE, never STRONG.

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was NOT
artificially modified. The Routine Layer queue at HEAD doesn't yet include
Arbitrage Sample Dataset Plan or Research Readiness Gate items; existing
protocol/data-first scoring axes still rank arbitrage at the top.
Operator selects the actual Bundle 9 from the `recommended_next_bundle`
list below.

## Recommended next bundle

Per the evaluation's future-allowed-source plan and the broader spec
layer, the natural next steps (each its own separately-authorized bundle,
all spec-only / no fetch / no backtest / no execution) are:

1. **Arbitrage Sample Dataset Plan v1** — pre-acquisition plan for the
   first concrete dataset (preferred: paid-vendor Class C offline export
   on a narrow window for ONE category, smallest realistic symbol set;
   alternative: Class A archive; backup: Class D qualified local CSV).
   Plan only; no fetch.
2. **Arbitrage Research Readiness Gate** — written readiness checklist
   that an operator must complete before authorizing the first P2
   acquisition (TOS / cost / storage / version-pins / OOS sealing
   confirmation). Gate spec only.
3. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); revisiting requires a NEW hypothesis, not a re-tune.

All three are read-only specs; **none of them** authorize data fetch,
exchange connection, backtest, broker connection, paper-order execution,
or live trading.
