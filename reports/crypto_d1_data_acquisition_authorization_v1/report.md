# SPARTA Crypto-D1 Local Data Acquisition Authorization / Freeze Plan v1 — build report

> **Research-only. Authorization / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no backtest
> execution, no dataset processing in this bundle. No real data files or
> data directory created.**

This bundle pre-registers EXACTLY what the operator must MANUALLY provide
later, WHERE it should go, and WHICH checks must pass before the
Crypto-D1 Backtest Runner v1 is allowed to use it. It layers on top of
the full Crypto-D1 stack (Bundles 11 → 16).

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.json` | Machine-readable authorization / freeze plan (validator source of truth). |
| `reports/crypto_d1_data_acquisition_authorization_v1/authorization_plan.md` | Human-readable plan: scope, 12-step operator manual checklist, required CSV schema, expected file layout (placeholders only), storage path plan, manifest / QA-freeze / checksum requirements pinning Bundles 11–16, 20 approval gates, forbidden actions, allowed + forbidden next steps, no-profit-claim policy, safety boundaries. |
| `reports/crypto_d1_data_acquisition_authorization_v1/report.md` | This build report. |
| `reports/crypto_d1_data_acquisition_authorization_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_data_acquisition_authorization_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_data_acquisition_authorization.py` | 35 tests. |
| `tools/strategy_candidate_registry.py` | Added the 2 new authorization_plan docs to the `crypto_d1_protocol` seed's `extra_files`. Lane stays **WATCH** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 17 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 18 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, all 5 prior Crypto-D1 spec docs + the Crypto-D1
runner, all 14 prior validators, `tools/strategy_next_bundle.py` (no
artificial selection nudge), `tools/crypto_d1_backtest_runner.py`,
`local_secrets/`, `paper_trading/`, `lessons.md`,
`data/crypto_d1_research/` (the storage root is NOT created by this
bundle; it appears only when the operator manually places a real
dataset).

## What the authorization plan defines

1. **Approved data scope.** BTC + ETH + SOL spot only on daily
   timeframe; quote currency USDT or USD (must be consistent and
   documented); operator-approved historical OHLCV CSV provider only
   (offline export); operator-chosen time range that MUST be recorded
   exactly in the manifest. Perps / dated futures / options /
   leveraged tokens / margin spot / synthetic instruments FORBIDDEN.
   Intraday FORBIDDEN in this bundle. Synthetic / mock data,
   screenshots, manually-typed prices FORBIDDEN.
2. **12 operator manual steps.** Select source → export → normalize
   header → mint dataset_id / dataset_version → place files →
   author manifest.json → compute sha256 + write CHECKSUMS.txt →
   write FREEZE_RECORD.txt → run future QA harness → accept QA_PASS
   or attach QA_WARN acceptance note → run the Bundle-16 runner →
   review the runner's research-only report. **All MANUAL.** No
   SPARTA-side automation.
3. **Required CSV schema.** Required columns must match Bundle 12
   exactly: `timestamp`, `open`, `high`, `low`, `close`, `volume`,
   `symbol`, `source`, `quote_currency`. Optional: `vwap`,
   `trade_count`, `quote_volume`, `source_timestamp`,
   `ingestion_timestamp`.
4. **Expected file layout (placeholders only — no real files
   created):** `BTC_daily.csv`, `ETH_daily.csv`, `SOL_daily.csv`,
   `manifest.json`, `CHECKSUMS.txt`, `FREEZE_RECORD.txt`,
   `qa_report.json`. Two booleans pinned True:
   `no_real_files_created_in_this_bundle` and
   `no_data_directory_created_in_this_bundle`.
5. **Storage path plan.** Root pattern
   `data/crypto_d1_research/<dataset_id>/<dataset_version>/`. **No
   real storage directory created.** No URLs; no remote schemes
   (`s3://`, `gs://`, `http(s)://`, `ftp://`,
   `file://remote-host`). Even the parent directory
   `data/crypto_d1_research/` is NOT created by this plan; it
   appears only when the operator manually places a real dataset.
6. **Manifest requirements.** Must validate against
   `tools/crypto_d1_dataset_manifest_check.py` (Bundle 13). Must
   reference Bundle-11 `protocol_version`, Bundle-12
   `data_contract_version`, Bundle-13 `dataset_manifest_spec_version`,
   Bundle-14 `qa_freeze_spec_version`, Bundle-15 `backtest_plan_version`,
   Bundle-16 `runner_version`.
7. **QA / freeze requirements.** Must follow Bundle 14;
   `QA_status = QA_PASS` or `QA_WARN` with explicit operator-acceptance
   note; `QA_FAIL` and `QA_BLOCKED` block runner use; all 7 QA-check
   groups' blocking checks required in `checks_passed`; the
   `no_lookahead` check must be in `checks_passed`.
8. **Checksum requirements.** sha256 per file required;
   `CHECKSUMS.txt` one-line-per-file format; checksums must match at
   runner startup; `FREEZE_RECORD.txt` records freeze timestamp +
   operator + all 6 pinned versions; any revision creates a new
   `dataset_version`; manual edits invalid unless documented +
   revalidated.
9. **20 approval gates.** Including: explicit written operator
   authorization; exact source / symbols / time-window / storage path
   / dataset_id named; all 5 prior-bundle versions pinned;
   CHECKSUMS.txt + FREEZE_RECORD.txt + manifest.json + qa_report.json
   created; QA_status validated; **no credentials, no trading
   permissions, no exchange-account references, no live-trading
   authorization, no paper-order execution authorization, no broker
   connection authorization**.
10. **Forbidden actions + allowed / forbidden next steps + required
    future artifacts + safety boundaries + no-profit-claim policy.**

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest-execution /
  dataset-processing flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`, `backtest_execution_enabled`,
  `dataset_processing_enabled`.
- `research_only: true` asserted.
- `lane == "crypto_d1_protocol"` asserted.
- Target assets MUST include BTC, ETH, SOL.
- `allowed_market_type == "spot"`; perps / dated / options /
  leveraged in `forbidden_market_types`.
- Timeframe `1d`; `intraday_explicitly_out_of_scope = True`.
- `approved_data_scope` declares spot / 1d / FORBIDS perps + intraday.
- `required_csv_schema.required_columns` contains all 9 Bundle-12
  fields.
- `expected_file_layout` documents the placeholder filenames AND
  pins `no_real_files_created_in_this_bundle = True` AND
  `no_data_directory_created_in_this_bundle = True`.
- `approval_gates` collectively mention operator authorization,
  manifest, `CHECKSUMS.txt`, `FREEZE_RECORD.txt`, `qa_report.json`,
  `QA_status`, no-credentials, no-live-trading, no-paper, no-broker.
- `manifest_requirements` pin Bundles 11/12/13/14/15/16 explicitly.
- `QA_freeze_requirements` pin Bundle 14 spec + QA_PASS-or-approved-WARN.
- `checksum_requirements` declare sha256-per-file + freeze-record
  format + at-startup-verification.
- `safety_boundaries` carries `research-only`, `no broker`, `no
  live`, `no order`.
- MD carries all 8 distinction phrases.
- Validator scans MD + JSON for forbidden capability claims.
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`,
  `pathlib`, `__future__`).
- Dedicated test asserts **exactly 4 spec files** exist in the
  bundle dir and no `.csv` / `.parquet` / `.pq` / `.pickle` /
  `.feather` / `.h5` / `.npz` / `.pkl` were created.
- Dedicated test asserts `data/crypto_d1_research/` was NOT created
  by this bundle.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_data_acquisition_authorization.py --rootdir=tests -q
→ 35 passed

python -m pytest <all 16 test files> --rootdir=tests -q
→ 431 passed across Bundles 2-17
```

## JSON validity

```
python tools/crypto_d1_data_acquisition_authorization_check.py validate → validate: OK
python tools/crypto_d1_backtest_plan_check.py validate                   → validate: OK
python tools/crypto_d1_qa_freeze_spec_check.py validate                  → validate: OK
python tools/crypto_d1_dataset_manifest_check.py validate                → validate: OK
python tools/crypto_d1_data_contract_check.py validate                   → validate: OK
python tools/crypto_d1_protocol_check.py validate                        → validate: OK
python tools/arbitrage_readiness_gate_check.py validate                  → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate             → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate          → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate                 → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate                → validate: OK
python tools/arbitrage_data_contract_check.py validate                   → validate: OK
python tools/arbitrage_protocol_check.py validate                        → validate: OK
python tools/strategy_candidate_registry.py validate                     → validate: OK
python tools/strategy_next_bundle.py validate                            → validate: OK
```

## Does local Crypto-D1 data exist?

**No.** `data/crypto_d1_research/` does NOT exist on disk. This bundle
authored documentation only; it did not create the storage root, did
not place any CSV file, and did not run the backtest runner.

## Were any real data files created in this bundle?

**No.** The bundle directory contains exactly 4 spec files
(`authorization_plan.json`, `authorization_plan.md`, `report.json`,
`report.md`). Zero `.csv` / `.parquet` / `.pq` / `.pickle` /
`.feather` / `.h5` / `.npz` / `.pkl` files. A dedicated test
(`test_no_real_data_files_created`) asserts this invariant.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (lane_status_override fires; the seed's
  `extra_files` now include 12 docs: protocol×2 + data_contract×2 +
  dataset_manifest×2 + qa_freeze_spec×2 + backtest_plan×2 +
  authorization_plan×2, all on disk).
- **evidence_level:** `MIXED`.
- **source_reports** grew from 25 (Bundle 15) → 27 (Bundle 17; the 2
  new authorization_plan docs added).
- Guards held: **never ACTIVE / never STRONG**.

## Recommended next step

- **Operator step (NOT a bundle):** operator MANUALLY executes the
  12 operator manual steps in the authorization plan — choose a
  TOS-compliant CSV provider, export BTC / ETH / SOL daily OHLCV,
  normalize to the Bundle-12 header, place files under
  `data/crypto_d1_research/<dataset_id>/<dataset_version>/`, author
  `manifest.json` (passes Bundle 13 check), write `CHECKSUMS.txt` +
  `FREEZE_RECORD.txt`, run the future QA harness (Bundle 14 spec),
  accept `QA_PASS` or attach a `QA_WARN` acceptance note, then run
  the Bundle-16 runner. **SPARTA does not automate any of these
  steps.**
- **Crypto-D1 Baseline Results Report v1** — separately authorized;
  only after the operator has supplied data AND the runner has
  produced output. Documents what the operator-reviewed run looks
  like and pins the resulting verdict + caveats. (Spec bundle;
  Claude works.)
- **Optional: Crypto-D1 Data QA Runtime Tool v1** — only if the
  operator decides the QA runner must exist as code before any
  further backtest. (Code bundle; recommend Codex.)
- **Optional: Crypto-D1 Backtest Runner v2 (future)** —
  walk-forward driver + per-family parameter-grid sweep + structured
  sensitivity sweep + per-strategy report emitter matching the full
  27-field Bundle 15 schema. (Code bundle; recommend Codex.)

## Safety boundaries (pinned, non-negotiable)

- Research-only. Authorization / specification only.
- No broker control, no exchange connection, no API keys, no
  `.env`, no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls.
- **No data fetch. No backtest execution. No dataset processing. No
  real data files or data directory created in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this authorization plan alone.
- **Data acquisition does not imply edge. Clean data does not imply
  profit. Running the backtest does not authorize trading. Backtest
  output will still require separate review. No paper/live trading
  is authorized. Crypto trend ideas are not profitable until tested
  with full costs AND forward-validated under a separately
  authorized future plan. A good historical chart does not imply
  future returns. 24/7** crypto session handling; weekday-only
  filters forbidden.
