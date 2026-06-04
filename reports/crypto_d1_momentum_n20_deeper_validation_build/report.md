# Crypto-D1 Momentum N=20 — Deeper-Validation BUILD Report (BUILD ONLY)

- **Build date:** 2026-06-04
- **Build kind:** reconciliation merge of two parallel deeper-validation drafts into ONE kept module.
- **Official master at build time:** `9211d835c6550d9eff2be922eacfe501f3c027da`
- **Task:** Reconcile the Crypto-D1 N20 deeper-validation analysis into a single kept module — BUILD ONLY, no execution.
- **Backing plan:** `reports/crypto_d1_momentum_n20_deeper_validation_plan/` (committed `7add3fc1`)
- **Queue task:** `crypto_d1_momentum_n20_deeper_validation_v1`
  (`PLAN_EXISTS_AWAITING_EXECUTION_APPROVAL`, `approved_for_research=false`,
  `execution_authorized=false`)
- **Status:** `BUILD_ONLY_NO_EXECUTION`

> This build adds an offline, stdlib-only **analysis capability** plus tests and
> this report. It runs no full backtest over frozen data, executes no orchestrator
> task, changes no dataset / QA freeze / queue / safety contract / dashboard /
> runner, and authorizes no paper, live, broker, exchange, order, or fetch action.
> No ACTIVE/STRONG promotion. No Bundle 23. Verdict ceiling stays **WATCH**;
> Crypto-D1 stays **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**.

---

## 0. Reconciliation summary

This build merged the two parallel deeper-validation drafts into **one kept
module** — `tools/crypto_d1_deeper_validation.py`. It keeps the runner-backed
single-source-of-truth analysis (from the untracked N20 draft) **and** the
deterministic JSON serializer, the confined opt-in writer, the read-only CLI, and
the AST/import/call-surface safety tests (from the pushed helper). The untracked
duplicates `tools/crypto_d1_n20_deeper_validation.py` and
`tests/test_crypto_d1_n20_deeper_validation.py` were **deleted** after the merged
tests went green. No duplicate public helpers remain. The runner, queue, dashboard,
datasets, and safety contract were not touched.

---

## 1. What was built

A focused, read-only analysis module
`tools/crypto_d1_deeper_validation.py` that produces the **nine** deeper-
validation views the plan pre-registered, over already-sliced OOS `Bar` series
supplied by the caller (unit tests supply tiny synthetic series). It:

- keeps **N=20 the PRIMARY** validation target (`PRIMARY_LOOKBACK = 20`,
  reference `30`);
- treats the **{18, 20, 22}** neighborhood as a bounded, explicitly-labeled
  **stability sensitivity** — `is_sensitivity_not_optimization = True`,
  `winner_reselected = False`, primary stays 20 (no parameter hunt, no
  OOS-tuning, no promotion of any N by being "best" here);
- **reuses** `crypto_d1_backtest_runner._simulate_equity` and
  `momentum_continuation` as the **single source of truth** for the cost-aware
  equity + signal math (no divergent re-implementation of the 120 bps cost
  model);
- pins every safety flag false and carries a non-authorization statement.

### The nine sections (report schema keys)

| # | Section key | What it computes (descriptive) |
|---|---|---|
| 1 | `1_yearly_oos_breakdown` | Per-calendar-year OOS return / trades / max-DD per asset |
| 2 | `2_monthly_return_drawdown_profile` | Per-month OOS return, worst month, longest drawdown (bars), OOS max-DD |
| 3 | `3_per_asset_consistency` | BTC/ETH/SOL side-by-side sign / floor clearance / DD / turnover + single-asset-carry flag |
| 4 | `4_trade_count_and_turnover` | OOS counts, turnover, per-asset floor (20), family total vs floor (30) |
| 5 | `5_fee_slippage_stress` | Same ledger re-priced at 150/180/240 bps + approx breakeven cost; baseline 120 bps stays headline |
| 6 | `6_outlier_sensitivity` | Compounded trade edge excluding best / worst / top-k; outlier-dependence flag |
| 7 | `7_regime_sensitivity` | Pre-declared trailing-vol & trend-SMA buckets (no look-ahead); single-regime flag |
| 8 | `8_basket_vs_per_asset` | Allocate-once equal-weight basket OOS vs per-asset legs (no rebalance) |
| 9 | `9_small_parameter_neighborhood_sensitivity` | N ∈ {18,20,22} stability band, labeled sensitivity, winner not re-selected |

Public surface: the nine pure section functions, `build_deeper_validation_report(per_asset)`
(assembler, no execution), `show_plan()` (read-only descriptor),
`to_stable_json()` (deterministic sorted-key serializer), `write_build_report()`
(opt-in writer confined to the single build folder — writes
`capability_plan.json` only), and `main()` (read-only CLI that prints the plan
descriptor and runs no simulation).

---

## 2. Why a focused helper module (not a new runner run-mode)

The committed plan §5 gates any `crypto_d1_backtest_runner.py` change behind a
**separate** approval and keeps execution deferred. A helper module therefore:

- isolates all new analysis away from the `momentum_confirmation_v1` code path —
  near-zero regression risk to existing runner modes (smoke-tested);
- keeps the runner's footprint **unchanged** in this build (no new `--config`
  choice, no dispatch, no show-plan edit) — so the mode is **not yet runnable**
  over the frozen dataset, exactly matching "BUILD ONLY, no execution";
- still reuses the runner's simulator as one source of truth (imports only;
  importing defines functions, runs no backtest).

**Runner CLI/dispatch integration** (adding a `momentum_n20_deeper_validation_v1`
`--config` mode that feeds real OOS slices into this helper) is the explicitly
**deferred, separately-approved** next step.

---

## 3. Exact files modified / deleted (this reconciliation)

**Final kept module + tests + reports:**
- `tools/crypto_d1_deeper_validation.py` — the single reconciled read-only analysis layer
- `tests/test_crypto_d1_deeper_validation.py` — 19 tests (synthetic fixtures only)
- `reports/crypto_d1_momentum_n20_deeper_validation_build/report.md` (this report)
- `reports/crypto_d1_momentum_n20_deeper_validation_build/report.json` (machine report)

**Deleted (the untracked duplicate draft, after merged tests went green):**
- `tools/crypto_d1_n20_deeper_validation.py`
- `tests/test_crypto_d1_n20_deeper_validation.py`

**Unchanged:** `tools/crypto_d1_backtest_runner.py`, `tests/test_crypto_d1_backtest_runner.py`,
`configs/research_queue.json`, the safety contract, the dashboard, and all datasets
are **untouched**.

---

## 4. Test results

- `tests/test_crypto_d1_deeper_validation.py` → **19 passed**
- `tests/test_crypto_d1_backtest_runner.py` → **75 passed, 1 pre-existing failure** (below)
- `tests/test_strategy_factory_queue.py` → **23 passed**
- `tests/test_strategy_factory_safety.py` → **42 passed**
- `tests/test_strategy_factory_orchestrator.py` → **13 passed**
- `tests/test_strategy_report_registry.py` → **13 passed**

Covered: mode/config exists; N=20 is PRIMARY; neighborhood is bounded + labeled
sensitivity (winner never re-selected); all nine sections present; report
JSON-serializable + deterministic; baseline 120 bps round-trip is derived from
the runner cost constants (not hardcoded); fee stress is additive & monotonic
with baseline 120; safety flags pinned false; no subprocess/socket/urllib/
requests/ccxt code identifiers; import allowlist (runner + stdlib only); no
forbidden execution call surfaces; no URL/credential string literals; reuses the
runner simulator (single source of truth); `momentum_confirmation_v1` wiring
untouched (smoke); insufficient-history is noted, not crashed; `to_stable_json`
is byte-stable; `write_build_report` is confined to the single build folder;
the CLI `main([])` returns 0 and runs no simulation.

### Pre-existing / environmental failure (NOT from this build)

`test_crypto_d1_backtest_runner.py::test_no_real_data_files_committed_under_data_crypto_d1_research`
fails on this machine because the operator's **frozen V001/V002
`daily_ohlcv.csv`** files exist on disk under `data/crypto_d1_research/` (they are
gitignored, created by a separate operator action). The test scans the filesystem,
not git, so it fails regardless of this build. This reconciliation touches nothing
under `data/`; it fails identically with or without these changes. It is excluded
from the regression count and flagged here for transparency.

---

## 5. Safety confirmations

- **No execution:** `executes_backtest=false`; no full frozen-data backtest run;
  no orchestrator task executed; no runner CLI mode wired (deferred).
- **Read-only / offline:** stdlib only; imports only `crypto_d1_backtest_runner`;
  no `subprocess`/`socket`/`urllib`/`requests`/`ccxt` (asserted by tests); no
  network, no credentials, no broker/exchange/order/fetch path.
- **No mutation:** no dataset / QA freeze / queue / safety contract / dashboard /
  runner change.
- **Pinned-false flags:** `research_only=true`; `paper_live_authorized`,
  `broker_path_enabled`, `exchange_path_enabled`, `order_path_enabled`,
  `fetch_live_data_enabled`, `dataset_mutation_allowed`, `active_strong_promoted`,
  `bundle_23_started`, `execution_authorized` all **false**.
- **No promotion:** verdict ceiling WATCH; N=20 stays the candidate; the {18,20,22}
  neighborhood promotes no N. Crypto-D1 stays WATCH / MIXED and
  NOT_READY_FOR_REAL_DATA.

---

## 6. Non-authorization statement

This build adds a read-only deeper-validation **analysis** module, its tests, and
this report only. It executes no backtest, runs no orchestrator task, calls no
runner run-mode, constructs no runnable command, and mutates no dataset, QA file,
queue config, safety contract, dashboard, or runner. It authorizes no paper,
live, broker, exchange, order, or fetch action, promotes no lane to ACTIVE/STRONG,
and starts no Bundle 23. A positive analysis view is not a trading authorization.
Runner integration and any execution require separate explicit operator approval.
