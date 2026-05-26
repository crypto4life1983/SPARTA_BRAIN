# s9 Cross-Asset Mean-Reversion RSI-2 - Signal-Module Specification Plan (Phase P5)

Status: PLAN_ONLY (no signal code; no RSI computation; no simulator; no backtest).
Authored: 2026-05-25
Tier-N spec anchor: docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md (sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409, commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401).
Selection plan anchor: docs/next_research_track_selection_plan_after_s7_d1_park.md (sha256 d8753155d47c36e07830750bf892743b8a1958d1ccc6d53932bee32ff76ec954, commit 530b54598fa7098eb746f2122b4002db2c984422).
Predecessor (parked): s7 D1 cross-asset Donchian yfinance ETF-proxy at REJECT_FAST. Park report sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263, commit a5ac092.

HARD BOUNDARIES (held by this plan). Signal-module specification only. No code change. No RSI computation. No signal computation. No simulator. No backtest. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No s7 D1 artifact mutation. No s7 D1 resurrection. No Tier-N spec modification. No selection plan modification. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Lock the specification for the s9 signal module that will (in a separately authorized P6 build phase) compute RSI(2) mean-reversion trigger flags per in-sample bar over the four-symbol ETF universe and emit them as immutable SignalEvent records consumable by the future s9 simulator (P7/P8). This plan defines the API surface, the dataclass schemas, the RSI computation rules, the entry/exit trigger semantics, the in-sample-only structural enforcement layers, the forbidden-token list, the V-gates, and the T-tests for the future build phase. The plan does NOT compute RSI, does NOT generate any signal value, does NOT call the loader, and does NOT mutate any existing artifact.

This is the s9 chain's analog of the Step 05 signal-module specification plan in the parked s7 D1 chain, with the Donchian-channel computation replaced by Wilder-smoothed RSI(2) computation, the bidirectional channel-break triggers replaced by RSI threshold-crossing triggers, and the long-only scope locked at the Tier-N spec.

## 2. Why P5 comes after the Tier-N spec

The Tier-N spec (P1, committed at 5bd8e62) locked the s9 mechanic byte-equivalent:

- `RSI_LOOKBACK = 2` (Connors canonical; not optimized)
- Signal series = `adj_close` (per Tier-N section 8; removes dividend-ex-date artifacts)
- Entry trigger: `RSI(2) < 10` (Connors canonical TPS oversold threshold)
- Exit trigger: `RSI(2) > 50` (Connors canonical exit threshold)
- Direction: LONG ONLY (short side deferred for borrow modeling)
- Filter: NONE (structural lock)
- Pyramid: NONE (explicit rejection)
- Hard stop: NONE (exit is signal-based)
- Time stop: NONE

With the mechanic locked, the next natural phase is to specify the signal MODULE that consumes loader output and emits the per-bar trigger events. The signal module is the first piece of the s9 chain that contains computation logic (Wilder RSI smoothing); every prior s9 turn was plan-only.

This phase also crosses the s9 chain's first-tier boundary: signal-side computation. The s7 D1 chain's Step 05 was its first-tier boundary; s9 inherits the same five-layer in-sample-only enforcement pattern.

The signal module produces NO position state, NO sizing, NO stop logic, NO trade ledger, NO PnL. Those are simulator (P7/P8) concerns and remain deferred.

## 3. Inputs from prior phases

The signal module consumes the output of the Step 03 loader (whether reused byte-equivalent from s7 D1 or built fresh per the to-be-authorized P3 loader-reuse decision plan). The signal module reads only the fields it needs and treats the LoadedSymbol structure as a duck-typed input contract.

Locked input contract:

- The signal module accepts a `LoadedSymbol`-shaped object (or a `Mapping[str, LoadedSymbol]`-shaped object for the cross-symbol entry point).
- Fields READ by the signal module: `symbol`, `dates`, `adj_close`, `csv_path`, `csv_sha256`. The choice of `adj_close` over `close` is locked at the Tier-N spec section 8 (dividend-artifact handling); the signal module shall NOT use `close` for RSI computation.
- Fields NOT READ: `open`, `high`, `low`, `close`, `volume`. (`close` is unused because Tier-N locked adj_close; `open` / `high` / `low` are unused because the s9 mechanic operates only on the close-of-day adj_close series; `volume` is unused because no volume filter is in the locked mechanic.)
- The signal module MUST NOT call `load_symbol()` / `load_all()` itself. The caller loads first and passes the result.
- The signal module MUST NOT call the validator. The caller is responsible for validation prior to passing data.
- If the P3 loader-reuse decision plan chooses to build a fresh s9 loader, the signal module MUST work against either the s7 D1 loader's `LoadedSymbol` or the s9 loader's `LoadedSymbol` so long as both expose the field shape above. The signal module's duck-type check (section 7) ensures portability.

## 4. Outputs the future build turn will create

The future P6 build turn shall create the following artifacts and no others:

- external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/signal.py
- external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/__init__.py (re-exports per section 7)
- external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/README.md
- tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/test_signal.py
- tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/__init__.py (test package marker; may be empty)
- reports/s9_cross_asset_mean_reversion_rsi2_signal_module_build_report.json (sealed; canonical Python-side seal scheme)
- reports/s9_cross_asset_mean_reversion_rsi2_signal_module_build_report.md (companion human-readable form)

No other files. No log files. No data files. No supplementary modules.

## 5. Files the build turn may create or modify later

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested: scripts/_s9_signal_module_build.py), written, run once, deleted on success.
- A temporary commit-message file under scripts/ if needed (mirroring the Step 05/06/07 build-message workaround for apostrophe-bearing commit messages), deleted on success.

Temp scripts byte-deleted on success; failures leave them pending a separately authorized cleanup turn.

## 6. Files the build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed is also not permitted unless it is in section 5.

- All s7 D1 ETF-proxy artifacts (`external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, all `reports/s7_d1_cross_asset_donchian_*`).
- The four canonical CSVs at `data/s7_d1_cross_asset_donchian/raw/*.csv`.
- `data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json` and `audit_manifest.json`.
- All s7 D1 plan files in `docs/s7_d1_cross_asset_donchian_step_*.md`.
- The s7 D1 spec `docs/s7_d1_cross_asset_donchian_spec.md`.
- The s7 D1 park report and the s7 D1 terminal lesson in `brain_memory/projects/trading_bot/lessons.md`.
- The s9 Tier-N spec and the next-track selection plan (this signal-module spec inherits from them, does not modify them).
- This signal-module spec file (the future P6 build turn quotes it, attests against it; does not edit it).
- All Databento-track artifacts under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/` and `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`.
- `review_queue.json`, the production `idea_memory` directory, all Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- `CLAUDE.md`, `docs/decisions.md`, `RUNBOOK`, `pipeline_manifest`, `.gitignore`.

## 7. API surface

The signal module shall expose exactly the following public API and no other public symbols:

- `RSI_LOOKBACK: int = 2` (hardcoded; matches Tier-N section 8).
- `RSI_OVERSOLD_ENTRY_THRESHOLD: float = 10.0` (hardcoded; matches Tier-N).
- `RSI_EXIT_THRESHOLD: float = 50.0` (hardcoded; matches Tier-N).
- `IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30")` (hardcoded; matches Tier-N section 14 and the parent spec section 11).
- `class SignalError(Exception)` - base class for every refusal mode.
- `class SignalInputError(SignalError)` - input not a LoadedSymbol-shaped object or structurally invalid.
- `class SignalOosBlockedError(SignalError)` - any attempt to compute signals for OOS or post-OOS bars.
- `class SignalParameterOverrideError(SignalError)` - any attempt to override the hardcoded RSI parameters or window.
- `@dataclass(frozen=True) class SignalEvent` - per-bar event (schema in section 9).
- `@dataclass(frozen=True) class SignalResult` - per-symbol result (schema in section 9).
- `@dataclass(frozen=True) class CrossSymbolSignalResult` - per-portfolio result (schema in section 9).
- `def compute_signals(loaded) -> SignalResult` - per-symbol in-sample-only signal computation.
- `def compute_signals_all(data) -> CrossSymbolSignalResult` - per-portfolio in-sample-only signal computation.

No other public function. No public mutable state. No module-level data load at import time. No public function that accepts a `window=`, `lookback=`, `entry_threshold=`, `exit_threshold=`, `series=`, `enable_short=`, or any other parameter that could relax the hardcoded constants. No `compute_signals_oos`, no `compute_signals_post_oos`, no `compute_signals_full`, no `compute_signals_with_threshold` function.

The signal module shall accept either a Mapping or a CrossSymbolSignalResult-shaped object for the cross-symbol entry point only if a forward-compatible coercion is needed; the canonical input is `Mapping[str, LoadedSymbol]`.

## 8. RSI computation rules (Wilder smoothing; locked)

The signal module shall compute Wilder-smoothed RSI(2) on the `adj_close` series of each symbol over the in-sample-eligible bars. The computation is canonical Wilder RSI:

R1. **Price changes**: at each bar i >= 1, compute `delta_i = adj_close[i] - adj_close[i-1]`. Split into `gain_i = max(delta_i, 0)` and `loss_i = max(-delta_i, 0)` (loss is non-negative).

R2. **Initial averaging (seed for Wilder smoothing)**: at bar `RSI_LOOKBACK = 2` (the third bar, index 2), compute:
  - `avg_gain[2] = mean(gain_1, gain_2)` = `(gain_1 + gain_2) / 2`.
  - `avg_loss[2] = mean(loss_1, loss_2)` = `(loss_1 + loss_2) / 2`.

R3. **Wilder smoothing for bars i > RSI_LOOKBACK** (i.e., i >= 3):
  - `avg_gain[i] = ((RSI_LOOKBACK - 1) * avg_gain[i-1] + gain_i) / RSI_LOOKBACK` = `(avg_gain[i-1] + gain_i) / 2` for RSI(2).
  - `avg_loss[i] = ((RSI_LOOKBACK - 1) * avg_loss[i-1] + loss_i) / RSI_LOOKBACK` = `(avg_loss[i-1] + loss_i) / 2`.

R4. **RSI formula**: `rs[i] = avg_gain[i] / avg_loss[i]` if `avg_loss[i] > 0`, otherwise `rs[i] = float('inf')`. `rsi[i] = 100.0 - (100.0 / (1.0 + rs[i]))`. When `avg_loss == 0` (all gains over the lookback), `rsi == 100.0` (by limit). When `avg_gain == 0` (all losses), `rsi == 0.0`.

R5. **First signal-eligible bar**: the earliest bar with index >= `RSI_LOOKBACK` (= 2) AND whose date is in `IN_SAMPLE_WINDOW`. For the s7 D1 sealed dataset (data starts 2014-01-02 at bar 0), the first signal-eligible bar is bar index 2 with date 2014-01-06 (the first trading day after a two-day warmup). This is a significantly earlier eligibility than the Donchian-55 first-eligible bar (2014-03-24); the s9 mechanic benefits from much shorter warmup.

R6. **No look-ahead**: at bar i, the RSI value uses ONLY adj_close values at indices 0..i (the closing price of bar i is included; bar i+1 and beyond are never read).

R7. **No alternative lookback**: the value `2` is hardcoded; the signal module exposes no override parameter.

R8. **No alternative threshold**: entry threshold `10.0` and exit threshold `50.0` are hardcoded; no override parameter.

## 9. SignalEvent / SignalResult / CrossSymbolSignalResult schemas

**SignalEvent** (per-bar, immutable frozen dataclass):

- `date: str` (YYYY-MM-DD; in IN_SAMPLE_WINDOW).
- `bar_index: int` (0-based index into the LoadedSymbol.dates tuple).
- `rsi_value: float` (the computed Wilder RSI(2) at this bar; range [0.0, 100.0] except when avg_loss == 0 then 100.0).
- `today_adj_close: float` (carried through from loaded.adj_close[bar_index]).
- `entry_long_triggered: bool` (True iff `rsi_value < RSI_OVERSOLD_ENTRY_THRESHOLD`).
- `exit_long_triggered: bool` (True iff `rsi_value > RSI_EXIT_THRESHOLD`).

SignalEvent contains NO field for: position state, PnL, position size, stop distance, fill price, order id, trade id, R-multiple, drawdown, Sharpe, expectancy, correlation, covariance. Those are downstream simulator (P7/P8) or aggregator (P9/P10) concerns. The signal module's responsibility is the trigger flags and the underlying RSI value only.

There is NO `entry_short_triggered` or `exit_short_triggered` field. The s9 mechanic is LONG ONLY per Tier-N section 9. Adding short fields would silently re-introduce a forbidden direction; the SignalEvent dataclass shape ENFORCES the long-only lock at the type level.

**SignalResult** (per-symbol, immutable frozen dataclass):

- `symbol: str` (one of SPY/TLT/GLD/USO).
- `csv_sha256_observed: str` (carried through from LoadedSymbol).
- `window: tuple` = IN_SAMPLE_WINDOW (always; permanent attestation of the IS-only window).
- `bars_in_window: int` (count of LoadedSymbol bars whose date lies in IN_SAMPLE_WINDOW).
- `first_signal_eligible_bar_index: int` (the earliest index i with i >= RSI_LOOKBACK AND date in IS).
- `first_signal_eligible_date: str`.
- `last_signal_eligible_bar_index: int` (the latest index in IS with i >= RSI_LOOKBACK).
- `last_signal_eligible_date: str`.
- `signals: tuple` (one SignalEvent per signal-eligible IS bar in chronological order).
- `oos_signal_intentionally_omitted: bool` (always True; permanent attestation).
- `post_oos_signal_intentionally_omitted: bool` (always True; permanent attestation).

**CrossSymbolSignalResult** (per-portfolio, immutable frozen dataclass):

- `per_symbol: Mapping[str, SignalResult]` (keys: SPY, TLT, GLD, USO).
- `cross_symbol_bars_in_window_equal: bool`.
- `cross_symbol_first_eligible_date_equal: bool`.
- `cross_symbol_last_eligible_date_equal: bool`.
- `oos_signal_intentionally_omitted: bool` (always True).
- `post_oos_signal_intentionally_omitted: bool` (always True).

All three dataclasses are frozen (immutable). No mutable fields.

## 10. Entry trigger rule (locked; matches Tier-N section 9)

At signal-eligible bar i (i >= RSI_LOOKBACK AND date in IN_SAMPLE_WINDOW):

- Compute `rsi_value` per section 8 R3-R4.
- `entry_long_triggered = (rsi_value < RSI_OVERSOLD_ENTRY_THRESHOLD)`.
- The flag is set on the SignalEvent; the signal module does NOT decide whether an entry is actually queued for the next bar's open. That is the simulator's responsibility (the simulator checks per-symbol position state at consumption time; if a position is already open, the simulator ignores the entry trigger per Tier-N section 9 step 3).
- The signal module records the flag for EVERY signal-eligible bar regardless of whether a hypothetical position is open. Position state is not the signal module's concern.

## 11. Exit trigger rule (locked; matches Tier-N section 10)

At signal-eligible bar i:

- Compute `rsi_value` per section 8.
- `exit_long_triggered = (rsi_value > RSI_EXIT_THRESHOLD)`.
- The flag is set on the SignalEvent; the signal module does NOT decide whether an exit is actually queued. That is the simulator's responsibility (the simulator queues exit only if a long position is currently open on this symbol).
- The signal module records the flag for every signal-eligible bar regardless of any hypothetical position state.

The exit trigger is THE ONLY exit condition the signal module records. There is no hard-stop trigger field, no time-stop trigger field, no trailing-stop trigger field. (Per Tier-N section 10 step 5-7, the s9 mechanic has no hard stop, no time stop, no trailing stop. K4 catastrophic and IS-end flat-mark are simulator-level enforcement, not signal-level.)

## 12. In-sample-only structural enforcement (five layers; inherited from Step 05 pattern)

The signal module shall structurally refuse to compute any signal for any bar whose date lies in `OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")` or `POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")`. Enforcement layers:

L1. **No `window=` parameter on any public API**. The caller cannot substitute a non-IS window.

L2. **Hardcoded IN_SAMPLE_WINDOW constant**. The public constant `IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")` is the only window the module ever computes against.

L3. **Eligibility predicate excludes OOS bars from the iteration loop**. The signal-eligibility check is `(date >= IN_SAMPLE_WINDOW[0]) AND (date <= IN_SAMPLE_WINDOW[1]) AND (bar_index >= RSI_LOOKBACK)`. The loop generating SignalEvents iterates only over indices satisfying this predicate.

L4. **Post-loop assertion**. After the loop, the module asserts that the last SignalEvent's date is `<= IN_SAMPLE_WINDOW[1]`. Failure raises `SignalOosBlockedError`.

L5. **Defensive scan**. The module asserts that no SignalEvent's date lies in OOS or post-OOS. Failure raises `SignalOosBlockedError`. The `oos_signal_intentionally_omitted = True` and `post_oos_signal_intentionally_omitted = True` attestation fields are permanent on every SignalResult.

The RSI computation is permitted to read adj_close values at bar indices preceding `first_signal_eligible_bar_index` (those are loaded warmup data, not OOS data). The RSI computation is NEVER permitted to read a bar whose date lies in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW, because signal-eligible bars are always in IS by the eligibility predicate, and the look-back at bar i never extends past bar i.

For the ETF-proxy dataset (data starts 2014-01-02 at bar 0; in-sample window pinned 2013-01-01 to 2022-12-30): first signal-eligible bar = index 2 = date 2014-01-06 (after a 2-bar warmup); last signal-eligible bar = the last loaded bar whose date is <= 2022-12-30. No OOS bar is ever iterated.

## 13. Warmup handling

A bar i is signal-eligible iff `i >= RSI_LOOKBACK` (= 2) AND `IN_SAMPLE_WINDOW[0] <= dates[i] <= IN_SAMPLE_WINDOW[1]`.

For the ETF-proxy dataset:

- `first_signal_eligible_bar_index = 2` (the third loaded bar; date 2014-01-06).
- `last_signal_eligible_bar_index` = the index of the last loaded bar with date <= 2022-12-30.
- Expected signal-eligible bar count per symbol = `bars_in_in_sample_window - 2` (the first two IS bars are warmup-only). For the s7 D1 audit-confirmed 2266 IS bars per symbol, expected SignalEvent count per symbol = 2264.

The s9 first-eligible bar (2014-01-06) is much earlier than the s7 D1 first-eligible bar (2014-03-24) because RSI(2) requires only 2 warmup bars vs Donchian-55's 55 warmup bars. The signal module shall record both the bar index and the date and verify they correspond to the loaded data correctly.

Wilder smoothing convergence note: Wilder smoothing has long memory; with seed value = simple average of the first 2 gains/losses, the smoothing converges quickly but is not "settled" in the strict statistical sense until many bars after the seed. For RSI(2) this convergence is fast (typically within 5-10 bars), and the first few SignalEvents may have RSI values that drift as smoothing settles. The signal module emits these early events as-is (no synthetic exclusion); the simulator may choose to apply additional warmup buffer at its own discretion (documented in the simulator-spec plan P7).

## 14. Determinism + no-state + no-side-effects rules

The signal module shall be a pure deterministic function from input LoadedSymbol(s) to output SignalResult / CrossSymbolSignalResult. Same input -> same output across any number of invocations and across any Python process.

The signal module shall NOT use:

- random number generators of any kind (no `random`, no `numpy.random`, no `secrets`).
- the current wall-clock time.
- environment variables.
- module-level mutable state.
- caches that persist across calls in module-level dicts/lists.
- any global counter that increments.
- any side-effecting operation: no print to stdout from the public API; no logging; no file write; no network call; no exception suppression that hides nondeterminism.

The signal module's `compute_signals` and `compute_signals_all` shall not mutate the input LoadedSymbol or any field of it. The returned SignalResult is the only effect.

A test (T11) shall verify determinism by running `compute_signals(load_symbol("SPY"))` twice and asserting the two SignalResults are field-equal.

## 15. No-parameter-optimization, no-filter, no-regime, no-asset-selection, no-winner-selection

The signal module shall NOT support:

- any optimization loop over `RSI_LOOKBACK`, `RSI_OVERSOLD_ENTRY_THRESHOLD`, `RSI_EXIT_THRESHOLD`, or any other parameter.
- any grid search over RSI lookbacks or thresholds.
- any alternative RSI lookback besides 2.
- any alternative entry threshold besides 10.0.
- any alternative exit threshold besides 50.0.
- any alternative series choice besides adj_close.
- any filter on top of the trigger (no MA filter, no trend filter, no regime filter, no volatility filter, no dependence filter, no volume filter).
- any short-side trigger (no `entry_short_triggered`, no `exit_short_triggered` fields; the dataclass shape enforces long-only at the type level).
- any asset selection rule (no "compute signals only for the top-N performing symbols").
- any winner-selection rule.
- any same-symbol-state condition in the signal module (the simulator handles "if position already open, ignore entry trigger"; the signal module records the flag regardless).
- any function name suggesting a search or sweep (no `_search_`, no `_sweep_`, no `_optimize_`, no `_tune_`).

The Tier-N spec is the threshold-lock contract. Any deviation requires a fresh `_revN_` Tier-N spec under separate authorization.

## 16. No-simulator, no-PnL, no-position-state, no-result-aggregation boundary

The signal module shall NOT contain:

- any simulator step that advances a position state across bars.
- any position-tracking variable, position-open-count, or per-symbol direction.
- any pyramid step computation.
- any Wilder ATR computation (the s9 signal module uses Wilder smoothing for RSI, not Wilder ATR for sizing; the simulator computes no ATR either for s9 because there is no ATR-based sizing per Tier-N section 11; the simulator uses equal-dollar sizing).
- any stop computation (no hard stop per Tier-N).
- any entry-timing decision (no MOC/ONO logic; the signal records "trigger fired"; the simulator decides timing).
- any order generation.
- any fill simulation.
- any commission computation.
- any slippage computation.
- any sizing computation (no contracts, no shares, no risk fraction; signal module does not know about portfolio equity).
- any PnL computation (no `daily_pnl`, no `cumulative_pnl`, no `realized_pnl`, no `unrealized_pnl`).
- any return-series computation (no `daily_return`, no `log_return`, no `pct_change(`, no `compute_return`, no `cumulative_return`, no `annualized_return`).
- any portfolio-level aggregation (no `portfolio_value`, no `portfolio_equity`, no `aggregate_pnl`).
- any performance statistic (no `sharpe`, no `sortino`, no `calmar`, no `drawdown`, no `max_drawdown`).
- any pairwise dependence measure (no `correlation`, no `covariance`, no `pearson`, no `spearman`).
- any rolling pandas API call (no `.rolling(`).
- any backtest engine import or call.

These quantities exist downstream in the s9 simulator (P7/P8) and aggregator (P9/P10) phases, each requiring its own plan and operator authorization.

## 17. No-OOS / no-post-OOS / no-OOS-inspection boundary

The signal module shall NOT:

- compute any RSI value for any bar whose date is in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW.
- emit any SignalEvent for an OOS or post-OOS bar.
- include any OOS or post-OOS date in any returned summary.
- recommend any OOS-side action as a runtime behavior.

The OOS protection is layered (per section 12). The `oos_signal_intentionally_omitted` and `post_oos_signal_intentionally_omitted` attestation fields are permanent True on every SignalResult / CrossSymbolSignalResult.

## 18. No-Databento, no-yfinance, no-network, no-API-key, no-file-IO boundary

The signal module shall NOT contain any of: `import yfinance`, `import databento`, `import requests`, `import urllib.*`, `from urllib import *`, `import http.client`, `import socket`, `import curl_cffi`, `import aiohttp`, `import httpx`, `import grpc`, `import pyarrow.flight`.

The signal module shall NOT call `os.environ` to read any variable beginning with `DATABENTO_`, `API_KEY`, `SECRET`, `TOKEN`, or `PASSWORD`. The signal module shall NOT call `os.environ["DATABENTO_API_KEY"]` under any circumstance.

The signal module shall NOT disable SSL verification.

The signal module shall NOT perform any file IO (no `open()`, no `Path.read_bytes`, no `Path.write_bytes`). It is pure in-memory; the V3 gate verifies this via patched-builtins sandbox.

## 19. No-Strategy-Lab, no-review-queue, no-brokerage, no-live-trading boundary

The signal module shall NOT touch any production-side artifact:

- no `import strategy_lab` / `import sparta_commander` / `import spartacus` / `import hydra_video` / `import app` / `import sparta_brain`.
- no read or write of `review_queue.json`.
- no read or write of any `idea_memory` artifact.
- no `import broker` / `import interactive_brokers` / `import alpaca` / `import tradestation` / `import ibapi` / `import binance` / `import oanda` / `import ib_insync`.
- no `import quantconnect` / `import lean` / `import qcalgorithm`.
- no path that references a live-trading code branch.
- no `import paper_trade` or `import paper_broker`.
- no `import scheduler` or `import autopilot`.
- no `import frc` or `import frc_gate`.

The signal module is strictly the s9 RSI-2 mean-reversion signal-trigger emitter. It does not touch any production code path.

## 20. Forbidden tokens, forbidden imports, V-gates V1-V10, T-tests T1-T16, build-script safety, build report schema

**Forbidden tokens (verified by static grep over signal.py; comment-marker FORBIDDEN_TOKEN_EXCLUSION accepted for documentation; the orchestrator's relaxed inline marker convention from Step 07 applies):**

Vendor / credential / network:

- `DATABENTO_API_KEY`, `yfinance`, `yahoo_finance`, `databento`, `requests.get`, `urllib.request`, `socket.connect`, `http.client`, `curl_cffi`, `aiohttp`, `httpx`.

Live trading / brokerage / production:

- `Strategy Lab` (with space), `strategy_lab`, `review_queue`, `idea_memory`, `live trading` (with space), `live_trading`, `brokerage`, `broker_api`, `broker_session`, `alpaca`, `interactive_brokers`, `ibkr`, `ibapi`, `ib_insync`, `tradestation`, `binance`, `oanda`, `order_send`, `place_order`, `submit_order`, `cancel_order`, `modify_order`, `route_order`, `production_signal`, `paper_broker`, `paper_trade`, `scheduler`, `autopilot`, `frc_gate`.

Downstream computation tokens (deferred to simulator / aggregator):

- `sharpe`, `sortino`, `calmar`, `drawdown`, `expectancy`, `win_rate`, `correlation`, `covariance`, `pearson`, `effective_independent_bets`, `avg_pairwise_correlation`, `avg_pairwise_dependence_measure`, `pnl`, `profit`, `portfolio_equity`, `cash_balance`, `mark_to_market`, `position_size`, `position_state`, `pyramid_unit`, `stop_distance`, `stop_price`, `slippage`, `commission`, `fill_price`, `order_id`, `trade_id`, `gross_pnl`, `net_pnl`.

Return-computation tokens (specific enough not to flag Python's `return` keyword):

- `daily_return`, `log_return`, `pct_return`, `.pct_change(`, `compute_return`, `cumulative_return`, `annualized_return`, `return_series`, `_returns_`, `_returns,`, `returns_total`, `arithmetic_return`, `geometric_return`.

Forbidden by parent spec context (s7 D1 lock):

- `Donchian` (s9 uses RSI, not Donchian channels; the literal English word `Donchian` shall not appear in the s9 signal source).
- `ATR(` (Wilder ATR is not used by s9; the simulator uses equal-dollar sizing, not ATR-based).
- `wilder_atr`, `wilder_n` (ATR-specific Wilder uses; not relevant to s9 RSI Wilder smoothing).
- `.rolling(` (pandas API; s9 uses stdlib only).

Parameter optimization tokens forbidden:

- `_optimize_`, `_sweep_`, `_tune_`, `_grid_search_`, `_bayes_search_`, `alternative_lookback`, `alternative_threshold`, `lookback_grid`, `threshold_grid`, `parameter_grid`, `winner_selection`, `asset_selection`, `top_n_pick`.

Filter / regime tokens forbidden:

- `regime_filter`, `regime_gate`, `ma_filter`, `vol_filter`, `dependence_filter`, `correlation_filter`, `trend_filter`, `volume_filter`.

Short-side tokens forbidden (long-only enforcement):

- `entry_short_triggered`, `exit_short_triggered`, `short_position`, `borrow_cost`, `borrow_rate`, `short_entry`, `short_exit`.

OOS-related tokens forbidden:

- `compute_signals_oos`, `simulate_oos`, `oos_simulation`, `post_oos_simulation`.

Tokens NEWLY UNBLOCKED in s9 signal module (these were forbidden in s7 D1 Step 05 but are necessary for s9):

- `Wilder` (English mixed case; the s9 RSI uses Wilder smoothing; this is the canonical name and the formula is documented in section 8).
- `wilder_smoothing`, `wilder_rsi`, `_wilder_rsi_at`.
- `RSI`, `rsi_value`, `rsi_period`, `RSI_LOOKBACK` (the s9 signal IS an RSI module; these are the natural identifiers).

The s9 signal module computes ROLLING max/min equivalents via explicit per-bar Python iteration over `delta`, `gain`, `loss` series (not via pandas `.rolling()`); the `_wilder_rsi_at(adj_closes, i)` helper iterates from index 1 to i. No pandas import.

**Forbidden imports (verified by static grep):**

See section 18 + section 19 lists. Build orchestrator grep aggregates the union.

**V-gates the build turn shall verify in order:**

- V1. The seven output files in section 4 exist at the locked paths.
- V2. The signal module is syntactically valid Python (AST compiles).
- V3. The signal module imports cleanly without performing any file IO at import time (patched-builtins sandbox).
- V4. The public API surface (section 7) matches exactly. No extra public symbol.
- V5. The signal module contains no forbidden import.
- V6. The signal module contains no forbidden token, outside designated FORBIDDEN_TOKEN_EXCLUSION lines.
- V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped. No xfail.
- V8. The test suite includes every T1..T16 (section 20 below).
- V9. A live in-sample integration test: load_all via the Step 03 s7 D1 loader (reused byte-equivalent for s9), then compute_signals_all returns a CrossSymbolSignalResult with 4 per-symbol entries, every SignalEvent.date in IN_SAMPLE_WINDOW, every SignalEvent.bar_index >= RSI_LOOKBACK, every SignalEvent.rsi_value in [0.0, 100.0].
- V10. Negative-path tests: compute_signals raises SignalInputError on bad input; raises SignalOosBlockedError if a synthetic LoadedSymbol with OOS dates is injected; raises SignalParameterOverrideError on unknown kwargs (defensive `**kwargs` rejection).

**T-tests the build turn shall implement (renames forbidden):**

- T1: compute_signals returns SignalResult for SPY/TLT/GLD/USO with bars_in_window > 0.
- T2: every SignalEvent.date in IN_SAMPLE_WINDOW for every symbol.
- T3: every SignalEvent.bar_index >= RSI_LOOKBACK (= 2).
- T4: first_signal_eligible_bar_index == 2 and first_signal_eligible_date == "2014-01-06" for each symbol.
- T5: RSI arithmetic spot-check: for SPY, find a SignalEvent where rsi_value < RSI_OVERSOLD_ENTRY_THRESHOLD AND assert entry_long_triggered is True; find another with rsi_value > RSI_EXIT_THRESHOLD AND assert exit_long_triggered is True; find another with rsi_value between thresholds AND assert both flags are False. No false positives.
- T6: SignalInputError on non-LoadedSymbol input (None, dict, string).
- T7: SignalInputError on non-Mapping input to compute_signals_all.
- T8: compute_signals_all returns CrossSymbolSignalResult with 4 expected keys; per-symbol consistency (same first_eligible_date across symbols if data is cross-symbol-aligned).
- T9: oos_signal_intentionally_omitted is True AND no SignalEvent.date in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW.
- T10: SignalEvent / SignalResult / CrossSymbolSignalResult dataclasses have NO field suggestive of downstream computation: no `pnl`, `profit`, `_return`, `sharpe`, `drawdown`, `correl`, `covar`, `position_size`, `wilder_atr`, `stop`, `slippage`, `commission`, `fill`, `order_id`, `trade_id`, `pyramid`, `short` (NO short-side fields per the long-only enforcement).
- T11: determinism: compute_signals(load_symbol("SPY")) twice produces field-equal SignalResults.
- T12: signal module performs no file IO at import (patched open / Path.read_bytes).
- T13: static grep of signal.py for the section 20 forbidden token list returns 0 hits outside FORBIDDEN_TOKEN_EXCLUSION lines.
- T14: static grep of signal.py for forbidden imports returns 0 hits.
- T15: public API surface equals exactly the section 7 list.
- T16: calling compute_signals imports no forbidden vendor/network module as a side effect (snapshot sys.modules before/after).

**Build-script safety guardrails:**

- The script shall not write to any path outside section 4 + section 5 temp paths.
- The script shall not import any forbidden vendor / brokerage / production package.
- The script shall not set any environment variable beginning with `DATABENTO_`.
- The script shall not disable SSL verification.
- The script shall log build steps to stdout.
- The script shall self-delete on success.
- The build orchestrator's V6 grep shall accept inline FORBIDDEN_TOKEN_EXCLUSION markers (line + next 2 lines), mirroring the Step 07 aggregator-build pattern.

**Build report schema (sparta.s9.rsi2.signal_module_build_report.v1):**

- schema, phase, controller_session, report_date_utc.
- plan_anchor (this signal-module spec), tier_n_anchor (Tier-N spec), selection_plan_anchor, predecessor_park_anchor.
- output_files (path -> sha256 + bytes).
- signal_api_surface_observed.
- v_gate_results (V1..V10).
- t_test_results (T1..T16).
- forbidden_token_grep_results, forbidden_import_grep_results.
- boundaries_held, negative_invariants.
- api_key_safety_confirmation.
- oos_protection_attestation.
- live_action_blocking_attestation.
- companion_md_sha256, seal_method, report_seal_sha256.

## 21. Build acceptance checklist, what build is NOT allowed to do, next authorization required

**Build acceptance checklist (the future P6 build turn must satisfy):**

- A separate operator authorization explicitly authorizes the s9 signal-module build.
- The plan path is exactly docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md.
- The Tier-N spec at docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md is byte-unchanged at sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409.
- The Step 03 s7 D1 loader (or the chosen s9 loader from P3) is byte-unchanged.
- The four CSVs and audit_manifest.json are byte-unchanged.
- Output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture.
- The pre-stage git index is empty (contamination cleanup if needed).
- The staged file count is exactly 7 at commit time.

**What the build is NOT allowed to do:**

- Compute any signal for any OOS or post-OOS bar.
- Use any RSI lookback other than 2.
- Use any entry threshold other than 10.0 or exit threshold other than 50.0.
- Use any series other than adj_close.
- Add a short-side trigger field to any dataclass.
- Add a filter, regime gate, or asset-selection rule.
- Run a simulator, backtest, or paper-trade loop.
- Make any live order, paper order, broker call, broker session, scheduler call, production-signal write.
- Modify any of the four canonical CSVs, fetch_run_manifest, audit_manifest, s7 D1 loader, validator, signal, simulator, aggregator, spec, plan, park report, lesson file, Tier-N spec, or this signal-module spec.
- Modify any ORB artifact, Step 30 cost constant, review_queue, idea_memory, Strategy Lab artifact.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento. Access DATABENTO_API_KEY.
- Disable SSL certificate verification.
- Use the phrase "compute RSI now" or "build the signal now" as an active directive (these appear here only as forbidden text).
- Treat the phrase "authorize s9 signal-module build" as a completed or current action.
- Treat any downstream s9 phase (simulator, aggregator, IS diagnostic, OOS, live trading) as pre-authorized.

**Next authorization required:**

A future operator authorization is required to proceed beyond this signal-module spec. That authorization shall reference this plan by exact path:

`docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s9 signal-module build only"** (P6; the natural next step; writes the seven output files and runs T1-T16).
- **"Authorize s9 loader-reuse decision plan only"** (P3; if the operator wants to formally decide loader reuse before the signal build).
- **"Authorize s9 validator-reuse decision plan only"** (P4; if the operator wants to formally decide validator reuse before the signal build).
- **"Authorize s9 signal-module spec revision only"** (if this plan needs revision, e.g., adjust thresholds, enable short side).

This signal-module spec is the source of truth for the s9 signal module. The build phase inherits the lock byte-equivalent; departing from any locked value requires a fresh `_revN_` spec under separate authorization.

No phase of this chain confers any standing authorization for OOS inspection, Strategy Lab promotion, brokerage connection, or live trading. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

----

End of plan. Signal-module specification authoring only. No code. No RSI computation. No signal computation. No simulator. No backtest. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No s7 D1 artifact modification. No Tier-N spec modification. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
