# SPARTA Crypto-D1 Data QA / Freeze Spec v1 — build report

> **Research-only. Data QA / freeze specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no QA harness
> execution, no backtest, no dataset processing in this bundle. No real
> dataset files created.**

This bundle satisfies the QA layer of the **P2_dataset_manifest_freeze**
phase of the Crypto-D1 Protocol Memo v1 (Bundle 11) and follows the
Crypto-D1 Data Contract v1 (Bundle 12) + Crypto-D1 Dataset Manifest v1
(Bundle 13). The future QA harness implementation is a separate,
separately-authorized P2 bundle.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.json` | Machine-readable QA/freeze spec (validator source of truth). |
| `reports/crypto_d1_qa_freeze_spec_v1/qa_freeze_spec.md` | Human-readable QA/freeze spec: required + forbidden inputs; A–G QA check groups; 6-status QA model with distinction statements; 26-field QA report schema; freeze rules; allowed/forbidden next steps; no-profit-claim policy. |
| `reports/crypto_d1_qa_freeze_spec_v1/report.md` | This build report. |
| `reports/crypto_d1_qa_freeze_spec_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_qa_freeze_spec_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_qa_freeze_spec.py` | 33 tests covering schema, safety, validator failure modes, no-real-data-files, tool stdlib-only, and integration with prior bundles. |
| `tools/strategy_candidate_registry.py` | Added the two new qa_freeze_spec docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 14 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 15 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, the Bundle 11 Crypto-D1 Protocol, the Bundle 12
Crypto-D1 Data Contract, the Bundle 13 Crypto-D1 Dataset Manifest,
all 8 prior arbitrage validators + docs, `tools/strategy_next_bundle.py`
(no artificial selection nudge), `lessons.md`.

## What the Crypto-D1 QA / Freeze Spec defines

1. **Lane + scope.** Lane `crypto_d1_protocol`; BTC + ETH + SOL spot
   only on the daily timeframe; perps / dated / options / leveraged /
   margin-spot / synthetic instruments forbidden at v1.
2. **Required inputs** (every future QA harness run): a manifest
   that already passes `crypto_d1_dataset_manifest_check.py` and
   pins protocol + data-contract versions; an on-disk CSV/Parquet
   OHLCV file; a sha256-verified `CHECKSUMS.txt`; a
   `FREEZE_RECORD.txt`; a `fees.json` (or equivalent).
3. **Forbidden inputs.** Live exchange APIs, scraping, anything
   requiring API keys / OAuth / `.env`, any source requiring a
   network call from SPARTA's runtime, synthetic data, screenshots,
   manually copied prices, no-provenance / no-checksums / no-manifest
   files, OOS-peeked datasets, TOS-incompatible feeds.
4. **7 QA check groups (A–G).** `A_manifest_integrity`,
   `B_timestamp`, `C_OHLCV`, `D_volume`, `E_symbol_source`,
   `F_fee_slippage`, `G_freeze`. Each group narrative is paired with
   a populated per-group dict (`timestamp_QA_checks`,
   `OHLCV_QA_checks`, `volume_QA_checks`, `symbol_QA_checks`,
   `source_provenance_QA_checks`, `fee_slippage_QA_checks`,
   `missing_data_QA_checks`, `duplicate_data_QA_checks`,
   `outlier_QA_checks`).
5. **6-status QA model.** `QA_DRAFT`, `QA_PASS`, `QA_WARN`,
   `QA_FAIL`, `QA_BLOCKED`, `QA_RETIRED`. Each status has explicit
   when-it-applies conditions. `QA_WARN` requires an operator
   acceptance note and keeps the lane at WATCH on usage.
6. **26-field QA report schema.** Every future
   `qa_report.json` MUST populate `qa_report_id`, `dataset_id`,
   `dataset_version`, `manifest_version`, `data_contract_version`,
   `protocol_version`, `generated_at`, `qa_status`, `checks_run`,
   `checks_passed`, `checks_warned`, `checks_failed`,
   `blocking_failures`, `warnings`, `row_count_observed`,
   `missing_day_summary`, `duplicate_summary`, `timestamp_summary`,
   `OHLCV_summary`, `volume_summary`, `fee_slippage_summary`,
   `source_provenance_summary`, `freeze_summary`,
   `allowed_next_step`, `forbidden_next_steps`, `safety_flags`.
7. **14 freeze rules.** Including: no mutable data in backtest;
   manifest required; `QA_PASS` (or approved `QA_WARN`) required
   before use; protocol + data-contract + manifest versions
   referenced; `CHECKSUMS.txt` + row counts + freeze timestamp
   required; future backtest cites `dataset_id` + `dataset_version`;
   data change creates new version; manual edits invalid unless
   documented and revalidated; daily bars must be UTC-normalized;
   weekday-only calendars forbidden.
8. **Allowed / forbidden next steps** + **PASS / WATCH / FAIL
   rules** + **required future artifacts** + **safety boundaries** +
   **no-profit-claim policy.**

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest /
  dataset-processing flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`, `backtest_enabled`,
  `dataset_processing_enabled`.
- `research_only: true` asserted.
- `lane == "crypto_d1_protocol"` asserted.
- Target assets MUST include BTC, ETH, SOL.
- `allowed_market_type == "spot"`; perps / dated / options /
  leveraged in `forbidden_market_types`.
- Timeframe `1d`; `intraday_explicitly_out_of_scope = True`.
- All 7 QA check groups present.
- 9 per-group QA-check dict sections all populated.
- All 6 QA statuses present in `QA_status_model`.
- All 26 QA-report fields present; `field_count` == 26.
- All 14 freeze-rule keys present; `daily_bars_must_be_utc_normalized
  = True`; `weekday_only_calendars_forbidden = True`.
- `pass_watch_fail_rules` carries PASS / WATCH / FAIL.
- `safety_boundaries` carries `research-only`, `no broker`, `no
  live`, `no order`.
- `allowed_next_steps` + `forbidden_next_steps` both populated.
- MD carries `QA is not strategy validation`, `QA_PASS does not
  imply edge`, `QA_PASS does not imply profitability`, `Clean daily
  OHLCV data does not imply profit`, `A QA report cannot authorize
  paper or live trading`, `A QA report cannot authorize
  backtesting by itself`, `Crypto trend ideas are not profitable
  until tested`, `24/7`.
- Validator scans MD + JSON for forbidden capability claims
  (`guaranteed profit`, `live-ready`, `production-ready`, `place
  the order`, `connect to exchange`, `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`).
- A dedicated test asserts **exactly 4 spec files** exist in
  `reports/crypto_d1_qa_freeze_spec_v1/` and no `.csv`, `.parquet`,
  `.pq`, `.pickle`, `.feather`, or `.h5` files were created.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_qa_freeze_spec.py --rootdir=tests -q
→ 33 passed

python -m pytest tests/test_crypto_d1_qa_freeze_spec.py tests/test_crypto_d1_dataset_manifest.py tests/test_crypto_d1_data_contract.py tests/test_crypto_d1_protocol.py tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 323 passed across Bundles 2-14
```

- `test_crypto_d1_qa_freeze_spec.py` — **33 new tests** (Bundle 14).
- Bundle 13 dataset manifest — 30 still pass.
- Bundle 12 data contract — 28 still pass.
- Bundle 11 protocol — 21 still pass.
- Bundle 10 readiness gate — 22 still pass.
- Bundle 9 sample dataset plan — 23 still pass.
- Bundle 8 data source evaluation — 23 still pass.
- Bundle 7 QA harness spec (arbitrage) — 22 still pass.
- Bundle 6 dataset manifest (arbitrage) — 19 still pass.
- Bundle 5 data contract (arbitrage) — 16 still pass.
- Bundle 4 research protocol (arbitrage) — 14 still pass.
- Bundle 3 candidate registry — 16 still pass.
- Bundle 2 next-bundle generator — 24 still pass.

## JSON validity

```
python tools/crypto_d1_qa_freeze_spec_check.py validate         → validate: OK
python tools/crypto_d1_dataset_manifest_check.py validate       → validate: OK
python tools/crypto_d1_data_contract_check.py validate          → validate: OK
python tools/crypto_d1_protocol_check.py validate               → validate: OK
python tools/arbitrage_readiness_gate_check.py validate         → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate    → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate        → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate       → validate: OK
python tools/arbitrage_data_contract_check.py validate          → validate: OK
python tools/arbitrage_protocol_check.py validate               → validate: OK
python tools/strategy_candidate_registry.py validate            → validate: OK
python tools/strategy_next_bundle.py validate                   → validate: OK
```

## Crypto-D1 QA / Freeze Spec validation result

**`validate: OK`** on the committed spec. All required top-level
keys present; all 7 safety flags pinned `False`; lane =
`crypto_d1_protocol`; target assets include BTC + ETH + SOL;
`allowed_market_type` = `spot`; perps / dated / options / leveraged
in `forbidden_market_types`; timeframe.primary = `1d` with intraday
explicitly out of scope; **all 7 QA check groups** present; all 9
per-group QA-check dict sections populated; **all 6 QA statuses**
present; **all 26 QA-report-schema fields** present (`field_count` =
26); freeze rules require frozen-data + checksums + dataset version
+ UTC daily bars + no weekday-only calendars; MD carries all 8
distinction phrases; zero forbidden capability phrases.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires because
  the seed's `extra_files` now include 8 docs: protocol + data
  contract + dataset manifest + QA/freeze spec, all on disk).
- **evidence_level:** `MIXED` (23 matched docs across historical
  CODR-1 reports + the four new Crypto-D1 specs; cannot reach
  `STRONG`).
- The new QA/freeze docs are added to `source_reports`.
- Guards held: **never ACTIVE / never STRONG**.

## Next-bundle generator selected bundle after update

**Selects "Arbitrage research protocol"** (lane =
`arbitrage_research_protocol`, priority = 3) — same as Bundles 10,
11, 12, 13. Both arbitrage and crypto_d1 are WATCH with the same
`+15` bonus; arbitrage still wins on the existing protocol-first /
data-first scoring hints. **Deterministic logic was not
artificially modified.** Operator picks the actual Bundle 15.

## How this follows Crypto-D1 Dataset Manifest v1

1. The Crypto-D1 Dataset Manifest v1 (Bundle 13) declared
   "Crypto-D1 Data QA / Freeze Spec v1 (P2)" as the next required
   future artifact and defined the per-dataset manifest schema this
   QA spec consumes.
2. This bundle authors that spec — spec only; no QA harness is
   executed, no data is fetched, no backtest is run, no dataset is
   processed, no real data files are created.
3. All seven safety flags from the manifest carry verbatim into the
   QA spec.
4. Lane scope identical: BTC / ETH / SOL, spot only, daily only,
   24/7.
5. **`A_manifest_integrity`** binds this QA harness to the dataset
   manifest spec: every dataset's `manifest.json` must validate
   against `crypto_d1_dataset_manifest_check.py` before any other
   QA group is allowed to proceed.
6. **`QA_report_schema.required_fields`** include `manifest_version`
   + `data_contract_version` + `protocol_version` — so any future
   `qa_report.json` pins all three spec layers explicitly.
7. Freeze rules mirror the dataset manifest's `freeze_fields`
   one-for-one (no mutable data in backtest; `CHECKSUMS.txt` +
   `FREEZE_RECORD.txt`; new version on any change; daily bars must
   be UTC-normalized; weekday-only calendars forbidden).

## Recommended next bundle

All three follow this spec's `required_future_artifacts`. Each is a
SEPARATE, separately-authorized future bundle; all are spec-only
(no fetch, no backtest, no execution):

1. **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-
   registration memo for the FIRST candidate strategy family + IS /
   OOS split. Plan only, no backtest run.
2. **Crypto-D1 Data Source Evaluation Memo v1** — written
   assessment of which offline data sources could later satisfy
   this QA / freeze spec. Memo only, no fetch.
3. **Crypto-D1 Data Acquisition Authorization Draft** — still
   spec-only; only if the operator wants to start the path toward
   an actual P2 acquisition. Does not authorize anything by itself.
