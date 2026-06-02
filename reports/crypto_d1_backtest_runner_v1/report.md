# SPARTA Crypto-D1 Backtest Runner v1 — build report

> **Research-only. Local-only.** No data fetched. No exchange contacted. No
> order placed. No paper or live trading authorized. The runner reads
> operator-supplied LOCAL CSV files only; on missing data it emits a FAIL
> report and never fabricates results.

This bundle implements the **P3_baseline_strategy_impl** phase of the
Crypto-D1 Protocol Memo v1 (Bundle 11), executing the pre-registered plan
from the Crypto-D1 Baseline Backtest Plan v1 (Bundle 15). The runner is
code; running it against real data is a separate, operator-triggered step.

## Files changed

| Path | Purpose |
|---|---|
| `tools/crypto_d1_backtest_runner.py` | Stdlib-only Python runner. CLI: `run`, `validate-config`, `show-plan`. CSV loader with full row-level validation; 4 primary strategy families + benchmark + 1 additive-filter experiment + WATCH-only mean-reversion skip; bounded-override cost + slippage model; IS/OOS split; metrics; conservative PASS/WATCH/FAIL classifier; deterministic JSON + MD report emitter. |
| `tests/test_crypto_d1_backtest_runner.py` | 38 tests using `tmp_path` synthetic fixtures only. |
| `reports/crypto_d1_backtest_runner_v1/report.md` | This build report. |
| `reports/crypto_d1_backtest_runner_v1/report.json` | Build report (machine). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 16 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 17 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, all 5 prior Crypto-D1 spec docs (Bundles 11–15), all
14 prior validator tools, `tools/strategy_candidate_registry.py` (the
runner is code, not evidence; lane stays WATCH unchanged from Bundle
15), `tools/strategy_next_bundle.py` (no artificial selection nudge),
`local_secrets/`, `paper_trading/`, `lessons.md`.

## What the runner implements

### Strategy families (Bundle 15 plan, single grid point per family in v1)

| ID | Status | Parameters | Implementation |
|---|---|---|---|
| `buy_and_hold_benchmark` | benchmark | per-asset + equal-weight daily-rebalanced basket | Position 1 from bar 1 onward; basket averages per-asset daily returns and applies an inter-asset rebalance haircut. |
| `donchian_channel_breakout` | primary | `entry_n=20`, `exit_m=10` | Enter long when daily close > prior-20-day max-close; exit when close < prior-10-day min-close. Close-only signal. |
| `moving_average_trend_filter` | primary | `window=200` | Long when close > 200-day SMA; cash otherwise. Skipped with reason if history < 201 bars. |
| `momentum_continuation` | primary | `lookback=90` | Long if 90-day rolling return > 0; cash otherwise. Skipped with reason if history < 91 bars. |
| `volatility_regime_gate` | primary additive filter | `entry_n=20`, `exit_m=10`, `vol_window=30`, `max_ann_vol=1.50` | Donchian breakout, gated OFF when rolling-annualized vol exceeds the pre-registered band. Experimental; clearly marked. |
| `mean_reversion` | **WATCH-only** | — | Always `SKIPPED_WATCH_ONLY` in v1; must NOT revive any prior CODR-\* parameter set (per Bundle 15 plan). |

### CSV input schema (Bundle 12)

Required header columns (per data contract v1):
`timestamp`, `open`, `high`, `low`, `close`, `volume`, `symbol`, `source`,
`quote_currency`.

Row-level validation rejects (never silently keeps):
- Missing or unparseable timestamp / symbol / source / quote_currency.
- Missing close cell.
- Non-positive OHLC values.
- Negative volume.
- `high < max(open, close, low)` or `low > min(open, close, high)`
  (Bundle 12 OHLCV self-consistency check).
- Duplicate `(symbol, timestamp)` rows (per Bundle 12 duplicate policy).
- Files with missing required header columns.

Missing days are **flagged** in warnings, never silently forward-filled.

### Cost model

- Default: `taker_fee_bps=10`, `slippage_bps=5`. Both bounded to `[0, 100]`.
- Applied on every position change as `(fee_bps + slip_bps) / 10000`
  multiplied by post-return equity.
- `fees_as_distinct_pnl_line` is True in every emitted report.
- `no_zero_slippage_baseline` is True (the default `slippage_bps=5` is
  non-zero); the operator may pass `--slippage-bps 0` only as a
  research-only stress test.

### IS / OOS split

- Default: 70% chronological IS / 30% OOS, per asset.
- IS and OOS metrics computed separately on each `RAN` strategy result.
- OOS trade-count floors (Bundle 15): ≥ 20 per asset; ≥ 30 per family.

### PASS / WATCH / FAIL classifier (conservative v1)

- **PASS** is **reserved** for an explicit operator decision; the runner
  NEVER emits PASS in v1.
- **WATCH** is emitted when at least one strategy shows positive OOS
  return with sufficient trade count AND a Sharpe-like ratio above the
  per-asset buy-and-hold benchmark.
- **FAIL** is emitted when there's no data, when data fails to parse,
  when no strategy ran, or when no strategy beats buy-and-hold on a
  risk-adjusted basis.
- All emitted reports include `forbidden_next_steps` and `safety_notes`
  reminders.

## Safety guarantees (enforced by tests)

- **Stdlib-only** (AST scan): only `argparse`, `csv`, `dataclasses`,
  `datetime`, `hashlib`, `json`, `math`, `pathlib`, `sys`, `__future__`.
- **No network / broker / exchange / vendor / credentials / subprocess**
  imports (AST `Import` / `ImportFrom` scan; not text matching, so
  docstrings cannot false-positive).
- **No `os.environ`, `os.getenv`, `urlopen`, `api.telegram.org`** in
  non-docstring source.
- **No order-placement / paper-order / live-trading code paths** in
  non-docstring source (verb scan).
- Seven safety flags pinned `False` in every emitted report:
  `research_only=True`, `data_fetch_enabled=False`,
  `exchange_connection_enabled=False`, `live_trading_enabled=False`,
  `broker_control_enabled=False`,
  `paper_order_execution_enabled=False`,
  `order_placement_enabled=False`.
- `validate_config` enforces fee + slippage bounds.
- `load_dataset` returns row-rejection reasons; never silently keeps
  invalid rows; never fabricates rows.
- On missing data: emits FAIL report with no fabricated metrics.
- Deterministic on same input (modulo wall-clock `generated_at`); the
  `run_id` is a sha256-derived 16-char prefix over input file bytes +
  cost + IS fraction.

## Tests run

```
python -m pytest tests/test_crypto_d1_backtest_runner.py --rootdir=tests -q
→ 38 passed in 0.56s

python -m pytest tests/test_crypto_d1_backtest_runner.py tests/test_crypto_d1_backtest_plan.py \
                 tests/test_crypto_d1_qa_freeze_spec.py tests/test_crypto_d1_dataset_manifest.py \
                 tests/test_crypto_d1_data_contract.py tests/test_crypto_d1_protocol.py \
                 tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py \
                 tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py \
                 tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py \
                 tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py \
                 tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 396 passed in 3.52s
```

## JSON validity of prior bundles unaffected (14/14)

All 14 prior validators still `validate: OK`. Bundle 16 did not modify
any prior tool or spec doc.

## How to run with local CSV data

1. **Prepare data.** Operator places one or more `*.csv` files under a
   chosen `DATA_DIR`. CSVs MUST have the Bundle-12 header columns
   (`timestamp`, `open`, `high`, `low`, `close`, `volume`, `symbol`,
   `source`, `quote_currency`). One row per `(symbol, UTC daily
   timestamp)`. Source venue named in the `source` column. **No
   network call is made by the runner**; offline acquisition is the
   operator's responsibility (and authorization).
2. **Validate config.**

   ```bash
   python tools/crypto_d1_backtest_runner.py validate-config
   ```

3. **Inspect the plan.**

   ```bash
   python tools/crypto_d1_backtest_runner.py show-plan
   ```

4. **Run.**

   ```bash
   python tools/crypto_d1_backtest_runner.py run \
       --data-dir <DATA_DIR> \
       --out-dir  <OUT_DIR>
   ```

   Optional flags:
   - `--fee-bps N` (bounded to `[0, 100]`)
   - `--slippage-bps M` (bounded to `[0, 100]`)
   - `--start-equity 100000`
   - `--is-fraction 0.7`

5. **Inspect reports.** `OUT_DIR` contains:
   - `crypto_d1_backtest_report.json`
   - `crypto_d1_backtest_report.md`

   **NEVER commit `OUT_DIR` contents to the repo unless the operator
   has explicitly authorized that.**

## What happens if no data exists

The runner emits a **FAIL** report with `assets_seen=[]`,
`strategy_results=[]`, and `failures=["missing local data: ..."]`.
JSON + MD reports are still written so the operator has a traceable
audit trail. **NO synthetic / fabricated metrics are emitted.**

Tested by `test_missing_data_dir_fails_safely` and
`test_empty_data_dir_fails_safely`.

## Real local data found at build time?

**No.** At the moment this bundle was built, no `data/crypto_d1_research/`
folder exists and no operator-supplied OHLCV files are present on disk.
The runner is implemented and tested; running it against real data is
the operator's separate, separately-authorized step.

## Backtest executed against real data in this bundle?

**No.** Only `tmp_path` synthetic fixtures generated inside the test
suite were executed. **No real backtest was run on any real Crypto-D1
dataset.**

## Candidate registry status for crypto_d1 after build

**Unchanged from Bundle 15** — `status = WATCH`, `evidence_level = MIXED`,
`source_reports = 25`. The runner is code, not evidence; the registry's
`extra_files` were not extended. Promotion to ACTIVE requires a future
per-strategy backtest report PASS verdict on REAL data **plus** an
explicit operator decision; not produced by this bundle.

## Recommended next bundle

- **Crypto-D1 Data Source Evaluation Memo v1** — written assessment of
  which offline data sources could later satisfy the QA / freeze spec.
  Memo only, no fetch. (Spec bundle; Claude works.)
- **Crypto-D1 Data Collection Authorization Draft** — still spec-only;
  only if the operator wants to start the path toward an actual P2
  acquisition. Does not authorize anything by itself. (Spec bundle;
  Claude works.)
- **Operator step (NOT a bundle):** operator-supplied offline
  acquisition of BTC / ETH / SOL daily-spot CSV data into a chosen
  `DATA_DIR`; then run the runner and review the emitted JSON + MD
  report.
- **Crypto-D1 Backtest Runner v2 (future)** — walk-forward driver +
  per-family parameter-grid sweep + structured sensitivity sweep +
  per-strategy report emitter that matches the full 27-field schema
  declared in Bundle 15. (Code bundle; recommend Codex.)

## Safety boundaries (pinned, non-negotiable)

- Research-only. Local-only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls.
- No data fetch (operator supplies local CSV only).
- Do not modify paper / live execution files.
- A future PASS verdict from this runner is **not** trading
  authorization.
- Crypto trend ideas are not profitable until tested with full costs
  AND forward-validated under a separately-authorized future plan.
- A good historical chart does not imply future returns.
- 24/7 crypto session handling; weekday-only filters forbidden.
