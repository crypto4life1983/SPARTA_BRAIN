# SPARTA Arbitrage QA Harness Spec v1 — build report

> **Research-only. QA harness specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys, no
> scheduler, no external network calls, **no data fetch, no backtest, no
> dataset processing in this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_qa_harness_spec_v1/qa_harness_spec.json` | Machine-readable QA harness spec (validator source of truth). |
| `reports/arbitrage_qa_harness_spec_v1/qa_harness_spec.md` | Human-readable spec: 5 per-category QA checks + 8 QA check groups (manifest integrity / timestamp / quote / order-book / trade-print / fee-funding / liquidity-latency / anomaly) + 6-status QA model + 23-field future QA report schema + PASS/WATCH/FAIL + safety boundaries + no-profit-claim policy. |
| `reports/arbitrage_qa_harness_spec_v1/report.md` | This build report. |
| `reports/arbitrage_qa_harness_spec_v1/report.json` | Build report (machine). |
| `tools/arbitrage_qa_harness_spec_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_arbitrage_qa_harness_spec.py` | 22 tests covering schema, safety, integration. |
| `tools/strategy_candidate_registry.py` | `extra_files` extended with the new QA harness docs for the arbitrage seed; lane stays **IDEA**. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 7 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 8 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code in
`paper_trading/`, sealed data, Bundle 4/5/6 validator tools (their existing
`required_future_artifacts` lists already point to future companion docs),
`brain_memory/projects/trading_bot/lessons.md`.

## What the QA harness spec defines

1. **Required inputs** — frozen on-disk dataset, per-dataset manifest
   satisfying the Bundle-6 manifest schema, pinned Data Contract version,
   pinned Research Protocol version, QA configuration (pre-declared, no
   auto-tuning).
2. **Forbidden inputs** — live exchange APIs, scraping, embedded keys /
   OAuth / `.env`, network URLs in `source_location`, datasets without a
   manifest, manifests failing the dataset-manifest validator, peeked OOS.
3. **8 QA check groups**:
   - **A** Manifest integrity (11 checks)
   - **B** Timestamp + synchronization (8 checks)
   - **C** Quote + spread (7 checks)
   - **D** Order book + depth (6 checks)
   - **E** Trade print (6 checks)
   - **F** Fee / funding / cost (6 checks)
   - **G** Liquidity + latency (5 checks)
   - **H** Anomaly detection (5 checks)
4. **Per-category QA checks** for all 5 Arbitrage Research Protocol v1
   categories.
5. **6-status QA model** — `QA_DRAFT`, `QA_PASS`, `QA_WARN`, `QA_FAIL`,
   `QA_BLOCKED`, `QA_RETIRED` — with exact semantics.
6. **23-field future QA report schema** that any future per-run QA report
   must satisfy, with `safety_flags` pinned `False` in every report.
7. **PASS / WATCH / FAIL rules** for THIS spec + **safety boundaries** +
   **no-profit-claim policy**.

### Hard rules (the manifesto of this bundle)
- **QA_PASS does NOT imply profitability.**
- **QA_PASS does NOT authorize backtesting.**
- **QA_PASS does NOT authorize paper or live trading.**
- **QA_FAIL blocks research use.**
- **QA_WARN requires explicit operator-acceptance memo before any research use.**
- **QA is not strategy validation.**

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest / dataset-processing
  flags pinned **False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `backtest_enabled`, `dataset_processing_enabled`.
- `research_only: true` asserted.
- Statistical category self-labels **NOT pure arbitrage**; markdown carries
  word discipline (`NOT pure arbitrage`, `RELATIVE_VALUE`, `price gap is
  not profit`, `QA is not strategy validation`, `QA_PASS does NOT`).
- Validator scans both JSON and Markdown for forbidden capability claims
  (`guaranteed profit`, `risk-free profit`, `live-ready`, `production-
  ready`, `place the order`, `connect to exchange`, `fetch live data`,
  `qa_pass implies profit`, `qa_pass authorizes backtest`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 123 passed in 1.25s
```

- `test_arbitrage_qa_harness_spec.py` — **22 new tests** (Bundle 7).
- `test_arbitrage_dataset_manifest.py` — 19 (Bundle 6); still pass.
- `test_arbitrage_data_contract.py` — 16 (Bundle 5); still pass.
- `test_arbitrage_research_protocol.py` — 14 (Bundle 4); still pass.
- `test_strategy_candidate_registry.py` — 16 (Bundle 3); still pass.
- `test_strategy_next_bundle.py` — 24 (Bundle 2); still pass.

## JSON validity

```
python tools/arbitrage_qa_harness_spec_check.py validate     → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate    → validate: OK
python tools/arbitrage_data_contract_check.py validate       → validate: OK
python tools/arbitrage_protocol_check.py validate            → validate: OK
python tools/strategy_candidate_registry.py validate         → validate: OK
python tools/strategy_next_bundle.py validate                → validate: OK
```

## How this fits after Dataset Manifest v1

```
Arbitrage Research Protocol v1  (30dabc4)  ← P0_protocol
        ↓
Arbitrage Data Contract v1      (c4d4c8b)  ← P1_data_contract
        ↓
Arbitrage Dataset Manifest v1   (492fcc1)  ← per-dataset manifest spec
        ↓
Arbitrage QA Harness Spec v1    (this bundle)  ← per-dataset QA spec
        ↓
(separate bundles, separately authorized)
   Arbitrage Data Source Evaluation Memo / Arbitrage Sample Dataset Plan v1 / P2 data acquisition / ...
```

The four documents now define WHAT arbitrage is, WHAT data is needed,
HOW each dataset is declared/frozen, and HOW each dataset is QA'd
— **all before** any data has been pulled or any test has been run.

## Candidate registry status for arbitrage after build

- **status:** `IDEA` ✅ (unchanged — additional docs carry only
  protocol / data / manifest / spec keywords)
- **evidence_level:** `MIXED` (8 matched docs now; no test/baseline/OOS
  evidence; cannot reach `STRONG`)
- **source_reports:** `["data_contract.json", "data_contract.md",
  "dataset_manifest.json", "dataset_manifest.md", "protocol.json",
  "protocol.md", "qa_harness_spec.json", "qa_harness_spec.md"]`
- Guard held: never ACTIVE, never STRONG.

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was NOT
artificially modified. The Routine Layer queue at HEAD doesn't yet
include a Data Source Evaluation Memo, Sample Dataset Plan, or
Crypto-D1-revival item; the existing protocol/data-first scoring axes
still rank arbitrage at the top. Operator selects the actual Bundle 8
from the `recommended_next_bundle` list below.

## Recommended next bundle

Per the manifest spec's required-future-artifacts and the QA harness
spec's downstream phases, the natural next steps (each its own
separately-authorized bundle, all spec-only / no data pull / no
backtest / no harness execution) are:

1. **Arbitrage Data Source Evaluation Memo** — written assessment of
   which offline data sources could later satisfy Categories A–E (vendor
   names, license fit, latency assumptions). Memo only; no data pull.
2. **Arbitrage Sample Dataset Plan v1** — pre-acquisition plan for a
   small first dataset (one category, one venue, narrow window, with
   pre-declared IS/OOS split). Plan only; no fetch.
3. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); would require a NEW hypothesis, not a re-tune.

All three are read-only specs; **none of them** authorize data fetch,
exchange connection, backtest, broker connection, paper-order execution,
or live trading.
