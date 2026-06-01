# SPARTA Crypto-D1 Dataset Manifest v1 — build report

> **Research-only. Dataset manifest specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no backtest,
> no dataset processing in this bundle. No real dataset files created.**

This bundle satisfies the **P2_dataset_manifest_freeze** specification
layer of the Crypto-D1 Protocol Memo v1 (Bundle 11) and follows the
Crypto-D1 Data Contract v1 (Bundle 12). The future per-dataset manifest
authoring is a separate, separately-authorized P2 bundle.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.json` | Machine-readable manifest spec (validator source of truth). |
| `reports/crypto_d1_dataset_manifest_v1/dataset_manifest.md` | Human-readable manifest spec: 35-field schema table, identity + provenance + freeze + QA-status rules, allowed/forbidden file formats with placeholder naming examples, no-profit-claim policy. |
| `reports/crypto_d1_dataset_manifest_v1/report.md` | This build report. |
| `reports/crypto_d1_dataset_manifest_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_dataset_manifest_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_dataset_manifest.py` | 30 tests covering schema, safety, validator failure modes, no-real-data-files, tool stdlib-only, and integration with prior bundles. |
| `tools/strategy_candidate_registry.py` | Added the two new dataset_manifest docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 13 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 14 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, the Bundle 11 Crypto-D1 Protocol memo, the Bundle 12
Crypto-D1 Data Contract, all 8 prior arbitrage validators + docs,
`tools/strategy_next_bundle.py` (no artificial selection nudge),
`lessons.md`.

## What the Crypto-D1 dataset manifest spec defines

1. **Lane + scope.** Lane `crypto_d1_protocol`; BTC + ETH + SOL spot
   only on the daily timeframe; perps / dated / options / leveraged /
   margin-spot / synthetic instruments forbidden at v1.
2. **35-field future manifest schema.** Every future per-dataset
   `manifest.json` MUST populate all 35 fields: `dataset_id`,
   `dataset_version`, `created_at`, `created_by`, `research_lane`,
   `market_type`, `assets`, `symbols`, `quote_currency`, `timeframe`,
   `time_start`, `time_end`, `timezone`, `bar_boundary`,
   `data_frequency`, `source_type`, `source_name`, `source_location`,
   `data_contract_version`, `protocol_version`, `checksum_policy`,
   `row_count_expected`, `row_count_actual`, `missing_day_policy`,
   `duplicate_policy`, `partial_day_policy`, `zero_volume_policy`,
   `outlier_policy`, `normalization_policy`,
   `fee_slippage_assumption_reference`, `freeze_status`, `QA_status`,
   `allowed_use`, `forbidden_use`, `notes`.
3. **Dataset identity + provenance.** Immutable `dataset_id`;
   monotonic `dataset_version`; source provenance required; local
   repo-relative `source_location` (no URLs); sha256 checksums per
   file in `CHECKSUMS.txt`; `FREEZE_RECORD.txt` recording freeze
   timestamp + operator + version pins; row-count expectations;
   created_at + created_by required.
4. **Crypto-D1-specific freeze rules.** No backtest may use mutable /
   unfrozen data; every dataset has a manifest; every manifest passes
   validation; every dataset references Crypto-D1 Protocol v1 and
   Data Contract v1 explicitly; every dataset carries a `QA_status`;
   every future backtest cites `dataset_id` and `dataset_version`;
   data changes create new versions; manual edits invalid unless
   documented and revalidated; daily bars must be UTC-normalized;
   weekday-only calendars forbidden.
5. **7-status QA model.** `DRAFT`, `FROZEN`, `QA_PASS`, `QA_WARN`,
   `QA_FAIL`, `RETIRED`, `BLOCKED`. Each status has an explicit
   when-it-applies clause; `QA_WARN` requires a written operator
   acceptance note and keeps the lane at WATCH on usage.
6. **Allowed file formats.** CSV, Parquet, JSON manifest, Markdown
   report.
7. **Forbidden inputs.** Screenshots, manually copied prices,
   unstable web-scraped tables, mutable notebooks as source of truth,
   files without provenance / checksums / manifest, files
   referencing private keys or credentials.
8. **Future naming examples (placeholders only — NO real files
   created):** `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001`, `manifest.json`,
   `daily_ohlcv.csv`, `qa_report.json`, `CHECKSUMS.txt`,
   `FREEZE_RECORD.txt`.
9. **PASS / WATCH / FAIL rules + required future artifacts +
   safety boundaries + no-profit-claim policy.**

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
- All 35 future-manifest required fields present; `field_count` ==
  35.
- All 7 QA statuses present in `qa_status_model`.
- `allowed_file_formats` includes CSV / Parquet / JSON manifest /
  Markdown report.
- `forbidden_inputs` covers screenshots, manually copied prices,
  scraping, no-provenance, no-checksums, no-manifest, credentials.
- `freeze_fields.daily_bars_must_be_utc_normalized = True`;
  `freeze_fields.weekday_only_calendars_forbidden = True`.
- `pass_watch_fail_rules` carries PASS / WATCH / FAIL.
- `safety_boundaries` carries `research-only`, `no broker`, `no
  live`, `no order`.
- MD carries `Dataset manifest approval does not imply edge`,
  `QA_PASS does not imply profitability`, `Clean daily OHLCV data
  does not imply profit`, `A manifest cannot authorize backtesting
  by itself`, `A manifest cannot authorize paper or live trading`,
  `Crypto trend ideas are not profitable until tested`, `24/7`.
- Validator scans MD + JSON for forbidden capability claims
  (`guaranteed profit`, `risk-free profit`, `live-ready`,
  `production-ready`, `place the order`, `connect to exchange`,
  `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`). No `requests`, `urllib`, `socket`,
  `ssl`, `tiingo`, `ccxt`, `alpaca`, `binance`, `dotenv`,
  `subprocess`, `os.environ`, `getenv`, `urlopen`.
- A dedicated test asserts **exactly 4 spec files** exist in
  `reports/crypto_d1_dataset_manifest_v1/` and no `.csv`, `.parquet`,
  `.pq`, `.pickle`, `.feather`, or `.h5` files were created.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_dataset_manifest.py --rootdir=tests -q
→ 30 passed

python -m pytest tests/test_crypto_d1_dataset_manifest.py tests/test_crypto_d1_data_contract.py tests/test_crypto_d1_protocol.py tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 290 passed across Bundles 2-13
```

- `test_crypto_d1_dataset_manifest.py` — **30 new tests** (Bundle 13).
- Bundle 12 data contract — 28 still pass.
- Bundle 11 protocol — 21 still pass.
- Bundle 10 readiness gate — 22 still pass.
- Bundle 9 sample dataset plan — 23 still pass.
- Bundle 8 data source evaluation — 23 still pass.
- Bundle 7 QA harness spec — 22 still pass.
- Bundle 6 dataset manifest (arbitrage) — 19 still pass.
- Bundle 5 data contract (arbitrage) — 16 still pass.
- Bundle 4 research protocol (arbitrage) — 14 still pass.
- Bundle 3 candidate registry — 16 still pass.
- Bundle 2 next-bundle generator — 24 still pass.

## JSON validity

```
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

## Crypto-D1 dataset manifest validation result

**`validate: OK`** on the committed manifest. All required top-level
keys present; all 7 safety flags pinned `False`; lane =
`crypto_d1_protocol`; target_assets include BTC + ETH + SOL;
allowed_market_type = `spot`; perps / dated / options / leveraged in
`forbidden_market_types`; timeframe.primary = `1d` with intraday
explicitly out of scope; **35 future-manifest required fields**
present; **7 QA statuses** present; `allowed_file_formats` covers
CSV / Parquet / JSON manifest / Markdown report; `forbidden_inputs`
covers screenshots / manually copied / scraping / no-provenance /
no-checksums / no-manifest / credentials; freeze rules require UTC
daily bars and forbid weekday-only calendars; MD carries all 7
distinction phrases; zero forbidden capability phrases.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires because the
  seed's `extra_files` now include 6 docs total: protocol + data
  contract + dataset manifest, all on disk).
- **evidence_level:** `MIXED` (21 matched docs across historical
  CODR-1 reports + the new v1 protocol + the new v1 data contract +
  the new v1 dataset manifest; cannot reach `STRONG`).
- The new dataset-manifest docs are added to `source_reports`.
- Guards held: **never ACTIVE / never STRONG**.

## Next-bundle generator selected bundle after update

**Selects "Arbitrage research protocol"** (lane =
`arbitrage_research_protocol`, priority = 3) — same as Bundles 11
and 12. Both arbitrage and crypto_d1 are now WATCH with the same
`+15` bonus; the arbitrage lane wins on the existing protocol-first
/ data-first scoring hints already in its queue item.
**Deterministic logic was not artificially modified.** I did not
edit `tools/strategy_next_bundle.py`. The operator should consult
both lanes' next-step lists to pick the actual Bundle 14.

## How this follows Crypto-D1 Data Contract v1

1. The Crypto-D1 Data Contract v1 (Bundle 12) declared "Crypto-D1
   Dataset Manifest v1 (P2)" as the next required future artifact.
2. This bundle authors that spec — spec only; no data is fetched,
   no backtest is run, no dataset is processed, no real data files
   are created.
3. All seven safety flags from the data contract carry verbatim
   into the manifest spec.
4. Lane scope is identical: BTC / ETH / SOL, spot only, daily only,
   24/7.
5. The future per-dataset `manifest.json` MUST pin both
   `data_contract_version` and `protocol_version` — so any future
   manifest is bound to Bundle 11 + Bundle 12 (or later) explicitly.
6. OHLCV required columns + self-consistency rules mirror the data
   contract one-for-one (`high >= max(open, close, low)`,
   `low <= min(open, close, high)`, etc.).
7. Missing-day / duplicate / partial-day policies echo the data
   contract.

## Recommended next bundle

All four follow this manifest spec's `required_future_artifacts`.
Each is a SEPARATE, separately-authorized future bundle; all are
spec-only (no fetch, no backtest, no execution):

1. **Crypto-D1 Data QA / Freeze Spec v1** (P2) — QA harness spec
   for daily-crypto data. Spec only, no harness run.
2. **Crypto-D1 Data Source Evaluation Memo v1** — written
   assessment of which offline data sources could later satisfy
   this manifest. Memo only, no fetch.
3. **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-
   registration memo for the FIRST candidate strategy family + IS /
   OOS split. Plan only, no backtest run.
4. **Crypto-D1 Data Acquisition Authorization Draft** — still
   spec-only; only if the operator wants to start the path toward
   an actual P2 acquisition. Does not authorize anything by itself.
