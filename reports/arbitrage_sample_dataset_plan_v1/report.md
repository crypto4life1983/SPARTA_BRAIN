# SPARTA Arbitrage Sample Dataset Plan v1 — build report

> **Research-only. Planning / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys, no
> scheduler, no external network calls, **no data fetch, no backtest, no
> dataset processing in this bundle. No real data files were created.**

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_sample_dataset_plan_v1/sample_dataset_plan.json` | Machine-readable plan (validator source of truth). |
| `reports/arbitrage_sample_dataset_plan_v1/sample_dataset_plan.md` | Human-readable plan: proposed sample scope + venue/symbol/time-window candidates + required fields + manifest+QA requirements + storage plan + naming convention + freeze plan + 19 approval gates + rejection rules + 11-step future collection checklist + forbidden actions + required future artifacts + PASS/WATCH/FAIL + no-profit-claim policy + safety boundaries. |
| `reports/arbitrage_sample_dataset_plan_v1/report.md` | This build report. |
| `reports/arbitrage_sample_dataset_plan_v1/report.json` | Build report (machine). |
| `tools/arbitrage_sample_dataset_plan_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_arbitrage_sample_dataset_plan.py` | 23 tests covering schema, safety, integration. |
| `tools/strategy_candidate_registry.py` | `extra_files` extended with the new plan docs for the arbitrage seed; lane stays **IDEA**. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 9 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 10 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code,
sealed data, Bundle 4/5/6/7/8 validator tools, `lessons.md`.

## What the sample dataset plan defines

1. **Proposed sample scope (TINY)** — primary category
   `cross_exchange_spot`; symbols `BTC_USDT` / `ETH_USDT` (label-only
   examples); venues `Venue_A` / `Venue_B` (label-only); duration shape
   `1_hour` or `1_day` (UTC, IS/OOS sealed before run); L1 quote level
   required with optional L2; per-venue fee schedule pinned; funding only
   if perp extension later authorized. **Explicit disclaimers** that this
   is NOT an authorization to fetch, that venue/source/storage path must
   be approved later.
2. **Candidate venues / symbols / time windows** — all label-only
   placeholders; actual values are set at approval time.
3. **Required fields** — per-quote-row, per-order-book-row (optional),
   per-fee-reference, per-funding-row (only if perp extension), per-row
   provenance.
4. **Manifest + QA requirements** — must satisfy all 32 manifest fields
   from Bundle 6 and all 8 QA check groups from Bundle 7; must pin
   versions of protocol + contract + manifest + qa + evaluation + this
   plan; freeze target `FROZEN`; QA target `QA_PASS` or accepted
   `QA_WARN`. **QA_PASS does NOT imply** edge / profitability /
   live-readiness / authorization to backtest.
5. **Storage plan** — root pattern
   `data/arbitrage_research/<dataset_id>/<dataset_version>/`; no network
   URLs; sha256 per file in `CHECKSUMS.txt`; no real data files created
   in this bundle.
6. **Naming convention** — `dataset_id` pattern
   `ARB_<CATEGORY_TAG>_<SYMBOL_TAG>_SAMPLE_V<NNN>` (e.g.,
   `ARB_XSPOT_BTCUSDT_SAMPLE_V001`); standard filenames for manifest /
   quotes / order_book / fees / funding / qa_report / CHECKSUMS /
   FREEZE_RECORD. **Examples only — no real files.**
7. **Freeze plan** — 5-step future freeze process (sha256 → manifest
   author → freeze_status=FROZEN → re-verify checksums → FREEZE_RECORD).
8. **19 approval gates** — explicit operator authorization, named
   Bundle-8 source class, exact source/venue/symbol/time-window/storage-
   path, all six version pins, no credentials/keys/trading/scheduler/
   live-or-paper, TOS review.
9. **Rejection rules** — refuse Class E (web-scraped) or Class F
   (manual); refuse network-URL source_location; refuse overbroad scope.
10. **11-step future collection checklist** — separate authorization
    bundle controls actual collection.
11. **Forbidden actions in this bundle** + **required future artifacts**
    + **PASS/WATCH/FAIL** + **no-profit-claim policy** + **safety
    boundaries**.

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest / dataset-processing
  flags pinned **False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `backtest_enabled`, `dataset_processing_enabled`.
- `research_only: true` asserted.
- Proposed scope is **TINY**: `primary_category == cross_exchange_spot`;
  symbol list ≤ 4; `scope_intent` declares TINY; explicit disclaimers
  present.
- `storage_plan.no_network_url_allowed=True` and
  `no_real_data_files_created_in_this_bundle=True` (asserted by validator
  + tests).
- `naming_convention.files_are_examples_only_no_real_files_in_this_bundle=True`.
- Approval gates include all 16 required markers (operator authorization,
  source/venue/symbol/time-window/storage path naming, six version pins,
  no credentials / no private keys / no trading / no scheduler / no
  live-or-paper).
- Future collection steps include both `explicit_operator_authorization`
  and `data_collection_in_separate_bundle`.
- Markdown carries word discipline (`NOT pure arbitrage`, `A sample
  dataset does not imply edge`, `A clean sample does not imply
  profitability`, `A price gap is not profit`, `Sample data cannot
  authorize trading`).
- Validator scans MD + JSON for forbidden capability claims (`guaranteed
  profit`, `risk-free profit`, `live-ready`, `production-ready`, `place
  the order`, `connect to exchange`, `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.
- **No real data files** were created (test enumerates the plan dir and
  asserts only the four authored doc files exist).

## Tests run

```bash
python -m pytest tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 179 passed in 1.76s
```

- `test_arbitrage_sample_dataset_plan.py` — **23 new tests** (Bundle 9).
- Bundle 8 (`test_arbitrage_data_source_evaluation.py`) — 23 still pass.
- Bundle 7 (`test_arbitrage_qa_harness_spec.py`) — 22 still pass.
- Bundle 6 (`test_arbitrage_dataset_manifest.py`) — 19 still pass.
- Bundle 5 (`test_arbitrage_data_contract.py`) — 16 still pass.
- Bundle 4 (`test_arbitrage_research_protocol.py`) — 14 still pass.
- Bundle 3 (`test_strategy_candidate_registry.py`) — 16 still pass.
- Bundle 2 (`test_strategy_next_bundle.py`) — 24 still pass.

## JSON validity

```
python tools/arbitrage_sample_dataset_plan_check.py validate    → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate        → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate       → validate: OK
python tools/arbitrage_data_contract_check.py validate          → validate: OK
python tools/arbitrage_protocol_check.py validate               → validate: OK
python tools/strategy_candidate_registry.py validate            → validate: OK
python tools/strategy_next_bundle.py validate                   → validate: OK
```

## How this fits after Data Source Evaluation Memo v1

```
Arbitrage Research Protocol v1     (30dabc4)
        ↓
Arbitrage Data Contract v1         (c4d4c8b)
        ↓
Arbitrage Dataset Manifest v1      (492fcc1)
        ↓
Arbitrage QA Harness Spec v1       (8073bf3)
        ↓
Arbitrage Data Source Evaluation Memo v1  (4786390)
        ↓
Arbitrage Sample Dataset Plan v1   (this bundle)
        ↓
(separate bundles, separately authorized)
   Arbitrage Research Readiness Gate / P2 acquisition / ...
```

The six-document arbitrage spec layer now covers WHAT arbitrage is, WHAT
data is needed, HOW each dataset is declared / frozen, HOW each dataset
is QA'd, WHICH data sources could satisfy these requirements, and WHAT
the first tiny sample dataset would look like — **all before** any data
has been pulled, any source has been contacted, or any test has been run.

## Candidate registry status for arbitrage after build

- **status:** `IDEA` ✅ (unchanged — additional docs carry only
  protocol / data / manifest / qa / evaluation / plan keywords)
- **evidence_level:** `MIXED` (**12** matched docs now; no test/baseline/
  OOS evidence; cannot reach `STRONG`)
- **source_reports:** `["data_contract.json", "data_contract.md",
  "data_source_evaluation.json", "data_source_evaluation.md",
  "dataset_manifest.json", "dataset_manifest.md", "protocol.json",
  "protocol.md", "qa_harness_spec.json", "qa_harness_spec.md",
  "sample_dataset_plan.json", "sample_dataset_plan.md"]`
- Guard held: never ACTIVE, never STRONG.

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was NOT
artificially modified. The queue at HEAD doesn't yet include Research
Readiness Gate or Data QA / Freeze items; the existing protocol/data-
first scoring axes still rank arbitrage at the top. Operator selects the
actual Bundle 10 from the `recommended_next_bundle` list.

## Recommended next bundle

All three options are **read-only specs** (no fetch, no backtest, no
execution):

1. **Arbitrage Research Readiness Gate** — written readiness checklist
   the operator must complete before authorizing the first P2 acquisition
   (TOS, cost cap, storage path, version pins, OOS sealing confirmation,
   no-credential confirmation, no-execution confirmation). Gate spec only.
2. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); would require a NEW hypothesis, not a re-tune.
3. **Data QA / Freeze bundle** — cross-cutting QA / freeze workflow that
   could later support not just arbitrage but other research lanes.

All three are spec-only; **none of them** authorize data fetch, exchange
connection, backtest, broker connection, paper-order execution, or live
trading.
