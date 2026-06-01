# SPARTA Arbitrage Dataset Manifest v1 — build report

> **Research-only. Dataset manifest / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys, no
> scheduler, no external network calls, **no data fetch and no backtest in
> this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_dataset_manifest_v1/dataset_manifest.json` | Machine-readable manifest spec (validator source of truth). |
| `reports/arbitrage_dataset_manifest_v1/dataset_manifest.md` | Human-readable spec: 5 categories with per-category manifest requirements + manifest_schema (32 required future fields + field descriptions) + dataset identity / provenance + freeze rules + 7-status QA model + venue / instrument / time-range / timestamp / quote / order-book / trade-print / fee / funding / liquidity / latency / provenance / normalization / data-quality / freeze / validation fields + allowed file formats + forbidden inputs + required future artifacts + PASS/WATCH/FAIL + safety boundaries + no-profit-claim policy. |
| `reports/arbitrage_dataset_manifest_v1/report.md` | This build report. |
| `reports/arbitrage_dataset_manifest_v1/report.json` | Build report (machine). |
| `tools/arbitrage_dataset_manifest_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_arbitrage_dataset_manifest.py` | 19 tests covering schema, safety, integration. |
| `tools/strategy_candidate_registry.py` | `extra_files` extended with the new manifest docs for the arbitrage seed; lane stays **IDEA**. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 6 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 7 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code in
`paper_trading/`, sealed data, Bundle 4 and Bundle 5 validator tools (their
`required_future_artifacts` lists already reference future companion docs;
no edit needed), `brain_memory/projects/trading_bot/lessons.md`.

## What the dataset manifest defines

1. **Manifest schema** — the 32 required fields every future per-dataset
   manifest must contain (`dataset_id` … `notes`), with field-by-field
   descriptions including immutability, versioning, and freeze-status
   rules.
2. **5 category-specific manifest requirements** — cross_exchange_spot
   (venue pair synchronization, quote depth, transfer/withdrawal & fee
   references); spot_perp_basis_funding (funding timestamps/rates, perp
   specs, liquidation-risk notes); triangular (3-leg mapping,
   precision/rounding, leg order assumptions, depth per leg);
   futures_calendar (expiries, multipliers, roll calendar, margin/carry);
   statistical_relative_value (aligned price history, spread / z-score /
   correlation prerequisites, explicit **NOT pure arbitrage** label).
3. **Dataset identity + provenance** — immutable `dataset_id`,
   monotonically-increasing `dataset_version`, source provenance per row,
   sha256 per-file checksums, expected vs. actual row counts, ISO-8601
   timestamps for `created_at` / `freeze_timestamp`, manifest-author
   identity, explicit invalid / frozen / untrusted criteria.
4. **Data freeze rules** — no research test may use mutable/unfrozen data;
   every dataset must have a manifest; every manifest must pass
   validation; every dataset must carry a `qa_status`; every dataset is
   tied to a data-contract version; every future test must cite
   `dataset_id` AND `dataset_version`; any change → new version; manually
   edited data is invalid unless documented + re-validated under a new
   version.
5. **QA status model** — 7 statuses (DRAFT, FROZEN, QA_PASS, QA_WARN,
   QA_FAIL, RETIRED, BLOCKED) with exact transition semantics. Only
   QA_PASS or explicitly-accepted QA_WARN datasets are research-usable.
6. **Field specs** — venue, instrument, time-range, timestamp, quote,
   order-book, trade-print, fee, funding, liquidity, latency, provenance,
   normalization, data-quality, freeze, validation.
7. **Allowed file formats** — parquet (preferred), csv, json/jsonl,
   feather/arrow, sqlite.
8. **Forbidden inputs** — live exchange APIs at dataset-build time,
   scraping, embedded keys / OAuth / `.env`, synthetic-priced data
   presented as historical, untraceable provenance, peeked OOS,
   TOS-forbidden feeds, network URLs in `source_location`.
9. **Required future artifacts** — per-dataset manifest file, integrity
   report, QA harness report, freeze record, retirement memo.
10. **PASS / WATCH / FAIL rules** + **safety boundaries** + **no-profit-
    claim policy** (manifest approval does not imply edge; QA_PASS does
    not imply profitability; price gap is not profit; manifests cannot
    authorize trading).

## Safety guarantees (enforced by tests)

- **Six** execution / fetch / connection / backtest flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`, `backtest_enabled`.
- `research_only: true` asserted.
- Statistical category self-labels **NOT pure arbitrage**; markdown carries
  word discipline (`NOT pure arbitrage`, `RELATIVE_VALUE`, `price gap is
  not profit`, `QA_PASS does not imply profitability`).
- Validator scans both JSON and Markdown for forbidden capability claims
  (`guaranteed profit`, `risk-free profit`, `live-ready`, `production-
  ready`, `place the order`, `connect to exchange`, `fetch live data`,
  etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 98 passed in 0.98s
```

- `test_arbitrage_dataset_manifest.py` — **19 new tests** (Bundle 6).
- `test_arbitrage_data_contract.py` — 16 (Bundle 5); still pass.
- `test_arbitrage_research_protocol.py` — 14 (Bundle 4); still pass.
- `test_strategy_candidate_registry.py` — 16 (Bundle 3); still pass.
- `test_strategy_next_bundle.py` — 24 (Bundle 2); still pass after the
  `extra_files` extension to the arbitrage seed.

## JSON validity

```
python tools/arbitrage_dataset_manifest_check.py validate   → validate: OK
python tools/arbitrage_data_contract_check.py validate      → validate: OK
python tools/arbitrage_protocol_check.py validate           → validate: OK
python tools/strategy_candidate_registry.py validate        → validate: OK
python tools/strategy_next_bundle.py validate               → validate: OK
```

## How this fits after Arbitrage Data Contract v1

```
Arbitrage Research Protocol v1  (30dabc4)  ← P0_protocol
        ↓
Arbitrage Data Contract v1      (c4d4c8b)  ← P1_data_contract
        ↓
Arbitrage Dataset Manifest v1   (this bundle)  ← spec for per-dataset manifests
        ↓
(separate bundles, separately authorized)
   Arbitrage QA Harness Spec v1 / Arbitrage Data Source Evaluation Memo / P2 data acquisition / …
```

The manifest spec is the third leg of the arbitrage research framework:
the **protocol** says what arbitrage means and how it gets evaluated; the
**data contract** says what data is required to evaluate it; the **dataset
manifest spec** says how each real dataset must be declared, frozen, and
QA'd before any test can use it.

## Candidate registry status for arbitrage after build

- **status:** `IDEA` ✅ (unchanged — additional docs carry "protocol" /
  "data" / "manifest" keywords; no `failed_`/`closeout`/`retire` triggers)
- **evidence_level:** `MIXED` (6 matched docs now; no test/baseline/OOS
  evidence; cannot reach `STRONG`)
- **source_reports:** `["data_contract.json", "data_contract.md",
  "dataset_manifest.json", "dataset_manifest.md", "protocol.json",
  "protocol.md"]`
- Guard held: never ACTIVE, never STRONG.

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was NOT
artificially modified. The queue at HEAD doesn't yet include a QA Harness
Spec, Data Source Evaluation, or refreshed arbitrage queue item; the
existing protocol/data-first scoring axes still rank arbitrage at the
top. Operator selects the actual Bundle 7 from the candidates below.

## Recommended next bundle

Per the manifest spec's own required-future-artifacts list, the natural
next steps (each its own separately-authorized bundle) are:

1. **Arbitrage QA Harness Spec v1** — define the harness that will verify
   any future per-dataset manifest + dataset pair (row counts, gap stats,
   outage overlap, contract version pinned, checksums verified, QA_PASS /
   QA_WARN / QA_FAIL verdict). Spec only; **no harness run** in that
   bundle either.
2. **Arbitrage Data Source Evaluation Memo** — written assessment of
   which offline data sources could later satisfy Categories A–E
   (vendor names, license fit, latency assumptions). Spec / memo only;
   **no data pull**.
3. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); revisiting requires a NEW hypothesis, not a re-tune.

All three are read-only specs; **none of them** authorize data fetch,
exchange connection, backtest, broker connection, or execution.
