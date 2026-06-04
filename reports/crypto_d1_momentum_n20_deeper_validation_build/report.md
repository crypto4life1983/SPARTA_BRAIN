# Crypto-D1 Momentum N=20 — Deeper-Validation capability BUILD report (BUILD ONLY)

- **Build date:** 2026-06-04
- **Official master at build time:** `44c71fe990cb1c90c583d94494d8e4d70561b28f`
- **Task:** Implement Crypto-D1 N=20 deeper-validation runner/report support — **BUILD ONLY, no execution**
- **Source plan:** `reports/crypto_d1_momentum_n20_deeper_validation_plan/report.json` (committed)
- **Queue task:** `crypto_d1_momentum_n20_deeper_validation_v1`
  (`PLAN_EXISTS_AWAITING_EXECUTION_APPROVAL`, `approved_for_research=false`,
  `execution_authorized=false`)
- **Lane:** Crypto-D1 — **WATCH / MIXED**, **NOT_READY_FOR_REAL_DATA** (unchanged)
- **Status:** `BUILD_ONLY_NO_EXECUTION`

> This build adds an additive analysis capability + tests + this report only. It
> runs **no backtest**, executes **no** Strategy Factory task, constructs **no**
> runnable command, mutates **no** dataset, changes **no** runner/dashboard/queue
> behavior, and authorizes **no** paper/live/broker/exchange/order/fetch action.
> No ACTIVE/STRONG promotion. No Bundle 23.

---

## 1. What was built

A new standard-library-only, pure-function capability module
`tools/crypto_d1_deeper_validation.py` that implements the **analysis half** of
the committed N=20 deeper-validation plan, plus a focused test suite
`tests/test_crypto_d1_deeper_validation.py`.

It exposes one deterministic function per plan validation test, a schema
assembler, deterministic serialization, and an **opt-in** writer confined to a
single build folder. The future approved execution step is thin wiring: run an
N=20 momentum OOS pass via the existing confirmation engine, then feed its
per-asset OOS series / ledger into these functions to emit the computed report.

## 2. Why a separate module instead of a new runner mode

The deeper-validation outputs are **descriptive post-processing** over an
already-computed N=20 OOS result (yearly/monthly decomposition, fee/slippage
re-pricing of the same ledger, outlier exclusion, regime bucketing, basket
comparison, bounded N-neighborhood stability). Keeping them out of the
1876-line `tools/crypto_d1_backtest_runner.py`:

- guarantees the existing `default` / `v002_addendum` / `momentum_robustness_v1`
  / `momentum_confirmation_v1` paths stay **byte-identical** (zero regression
  risk — confirmed: the runner file was **not modified**); and
- makes every function **unit-testable on tiny synthetic inputs with no
  backtest**.

This mirrors the Step 1–4 factory convention (stdlib-only, deterministic,
fail-closed, opt-in writer in one build folder, pinned-false safety flags).

## 3. Required validation sections — all 9 supported

| # | Section (plan id) | Function |
|---|---|---|
| 1 | yearly_oos_breakdown | `yearly_oos_breakdown(daily_returns)` |
| 2 | monthly_return_drawdown_profile | `monthly_return_drawdown_profile(daily_returns)` |
| 3 | per_asset_consistency | `per_asset_consistency(per_asset_oos, floor=20)` |
| 4 | trade_count_and_turnover | `trade_count_and_turnover(per_asset_trades, floor=20)` |
| 5 | fee_slippage_stress | `fee_slippage_stress(trade_gross_returns, 120, (150,180,240))` |
| 6 | outlier_sensitivity | `outlier_sensitivity(trade_returns, top_k=(1,2,3))` |
| 7 | regime_sensitivity | `regime_sensitivity(daily_returns, regime_labels)` + `simple_trend_regime` |
| 8 | basket_vs_per_asset | `basket_vs_per_asset(per_asset_oos, basket_oos_return)` |
| 9 | parameter_neighborhood | `parameter_neighborhood(results_by_n)` — bounded {18,20,22} |

- **Primary target is N=20 only.** `PRIMARY_LOOKBACK=20`,
  `REFERENCE_LOOKBACK=30`.
- **Section 9 is bounded sensitivity, NOT optimization.** Neighborhood pinned to
  {18, 20, 22}; `winner_fixed_at=20`; `winner_reselected_from_probe=false`;
  `is_sensitivity_not_optimization=true`. It only computes a surface when
  results are explicitly supplied (i.e. only if the plan authorizes the probe).

## 4. Build-time capability contract vs computed

- `build_deeper_validation_schema(None)` → BUILD-time contract: every required
  section present as a `computed=false` placeholder so consumers can see the
  full shape without any backtest. `ran_backtest=false`, `build_only=true`,
  `is_execution_result=false`.
- `build_deeper_validation_schema(inputs)` → computes each section from supplied
  synthetic/real OOS series. `ran_backtest` stays `false` (this module never
  runs the engine; it only post-processes an externally supplied result).

## 5. Exact files created / changed

**Created (this build):**
- `tools/crypto_d1_deeper_validation.py` (capability module, stdlib only)
- `tests/test_crypto_d1_deeper_validation.py` (28 tests)
- `reports/crypto_d1_momentum_n20_deeper_validation_build/report.md` (this report)
- `reports/crypto_d1_momentum_n20_deeper_validation_build/report.json` (machine report)

**Changed:** none. `tools/crypto_d1_backtest_runner.py`,
`tests/test_crypto_d1_backtest_runner.py`, `configs/research_queue.json`, the
safety contract, datasets, and dashboards were **not** modified.

## 6. Test results

Run: `pytest test_crypto_d1_deeper_validation.py test_crypto_d1_backtest_runner.py`

- `tests/test_crypto_d1_deeper_validation.py` → **28 passed**
- `tests/test_crypto_d1_backtest_runner.py` → all `momentum_confirmation_v1` /
  runner-behavior tests **passed**; **1 pre-existing, unrelated failure**:
  `test_no_real_data_files_committed_under_data_crypto_d1_research` (asserts the
  frozen V001/V002 `daily_ohlcv.csv` are not committed — they were committed by
  a **prior operator dataset action**, not by this build; this build touched no
  dataset). Verified the same test fails identically without the new file.
- Combined: **103 passed, 1 pre-existing failure**.

Coverage of required cases:
- new capability/config exists (`config_name=momentum_n20_deeper_validation_v1`);
- only N=20 is the primary target (reference N=30);
- neighborhood bounded {18,20,22}, labeled sensitivity-not-optimization, winner
  never re-selected;
- existing `momentum_confirmation_v1` runner unchanged (runner file not edited;
  its tests pass; runner source contains no new mode token);
- no network / subprocess / broker / exchange / order / fetch (AST import scan +
  call-surface scan);
- output schema includes all 9 required sections (build-time + computed);
- safety flags all non-authorizing;
- `to_stable_json` deterministic + sorted; opt-in writer confined to the build
  folder; CLI runs no backtest and returns 0.

## 7. Safety confirmations

- **BUILD ONLY:** no backtest run, no orchestrator executed, no queue item
  executed, no runnable command constructed.
- **Stdlib only:** imports limited to `__future__, argparse, json, sys, pathlib,
  typing` (asserted). No `subprocess`/`socket`/`requests`/`urllib`/`http`/`ccxt`/
  `websocket`.
- **Safety flags pinned:** `research_only=true`; `paper_live_authorized`,
  `broker_path_enabled`, `exchange_path_enabled`, `order_path_enabled`,
  `fetch_live_data_enabled`, `dataset_mutation_allowed`, `active_strong_promoted`,
  `bundle_23_started`, `execution_authorized` all **false**.
- **No promotion / no execution authorization:** the module emits no verdict
  change; the lane stays **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**.
- **Write path confined:** the only writer targets
  `reports/crypto_d1_momentum_n20_deeper_validation_build/`.

## 8. Non-authorization statement

This build adds a read-only analysis capability, its tests, and this report
only. It executes no queue item, runs no backtest, calls/imports no runner,
constructs no runnable command, mutates no dataset, and authorizes no paper,
live, broker, exchange, order, or fetch action. It does not promote any lane to
ACTIVE or STRONG and does not start Bundle 23. A positive future backtest result
is not trading authorization. Execution requires separate explicit operator
approval. Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**.
