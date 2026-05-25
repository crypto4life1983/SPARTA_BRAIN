# s7 D1 Cross-Asset Donchian - Step 05 Signal Computation Specification Plan

Status: PLAN_ONLY (build not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
BOUNDARY ALERT: This is the FIRST phase that will (in a future build) authorize signal-side computation. This plan defines that future scope carefully and conservatively.
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Parent Step 03 build (loader, verdict PASS): commit d7b2a0c, loader.py sha256 e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9
Parent Step 04 plan: commit a5acf59
Step 04 build (validator, verdict PASS): commit a2ec179, validator.py sha256 bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e, build report sha256 fbabd75ea7ce1914ece7a7fda8c957c9e22899538321c180e7c37c378feedd27, seal 737a3f54b0a380e1c298a83a9fb8183b0fbdba23b42fa002a2b7fe0d9883ba3f
Step 02c audit anchor: audit_manifest sha256 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb
Naming convention: s7 D1 cross-asset Donchian yfinance proxy (continues the alternate-vendor research track).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No signal module implementation. No test implementation. No build report write. No CSV read by claude during plan authoring. No fetch_run_manifest.json modification. No audit_manifest.json modification. No CSV modification. No loader.py modification. No validator.py modification. No entry-channel computation. No exit-channel computation. No 55-bar rolling-window aggregation. No 20-bar rolling-window aggregation. No Wilder ATR computation. No moving average. No exponential smoothing. No return computation. No log-return computation. No cumulative-return computation. No z-score. No pairwise dependence measure. No simulator run. No backtest. No paper-trade loop. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No Strategy Lab promotion. No brokerage connection. No live trading. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No OOS signal computation under any future authorization referenced by this plan. No OOS inspection. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Define the canonical Python signal-computation module for the s7 D1 cross-asset yfinance proxy research track. The signal module is the FIRST module in the chain that crosses the no-signal boundary held by every prior phase (02b, 02c, 03, 04). Its job is to take a LoadedSymbol structure (output of Step 03 loader) that has passed the Step 04 validator and compute Donchian channel breakout signal events for IN-SAMPLE bars only. The module is a pure deterministic function over LoadedSymbol input; it computes channel values and trigger flags per IS bar and returns them in a SignalResult dataclass. It does NOT run a simulator. It does NOT run a backtest. It does NOT compute returns, profit, drawdown, sharpe, or any portfolio-level statistic. It does NOT decide when to execute trades; the simulator (Step 06+) does that. It does NOT compute position sizing; the simulator does that. It does NOT compute Wilder ATR or stops; the simulator does that. The signal module's scope is strictly the four bidirectional Donchian breakout trigger flags per IS bar.

## 2. Why Step 05 comes after Step 04 (and the boundary-crossing nature)

Step 04 sealed the input validator (verdict PASS at commit a2ec179). The validator confirmed the loader output (Step 03 PASS at commit d7b2a0c) is fit-for-purpose for downstream channel-construction phases. With the loader and validator in place, the next logical phase is the signal module that consumes the validated LoadedSymbol structures and computes the Donchian channel breakout signals that the parent spec section 5 defines.

This phase crosses a major boundary that every prior phase explicitly forbade. To keep the chain auditable and reversible, this plan enforces tight scoping on what the signal module IS allowed to do (compute the four trigger flags per IS bar) and what it remains FORBIDDEN from doing (everything else, including OOS computation, simulator state, return / pnl / portfolio aggregation, network IO, vendor calls, Strategy Lab integration, review_queue mutation, brokerage connection, live trading). The validator's structural OOS protection rule from Step 04 section 12 is INHERITED and STRENGTHENED here: not only does the signal module not inspect OOS numerical values, it refuses to compute any signal for any OOS or post-OOS bar.

The build turn for Step 05 is the first that will write code containing channel-construction logic. Every operator authorization beyond Step 05 (Step 06 simulator, Step 07 backtest, etc.) inherits the precedent established here: explicit allow-list of what the new module can do, explicit forbid-list of what it cannot, structural enforcement of the OOS protection rule and the no-live-trading invariant.

## 3. Inputs from prior phases

The signal module depends on the public API surface of the Step 03 loader and the LoadedSymbol dataclass it returns. The signal module does NOT depend on the Step 04 validator directly (the caller is responsible for running the validator before passing the LoadedSymbol; the signal module assumes the input is valid).

Locked input contract:

- The signal module consumes a `LoadedSymbol` instance (or a `dict[str, LoadedSymbol]` keyed by symbol).
- Fields read: `symbol`, `dates`, `high`, `low`, `close` (close for diagnostic/transparency carry-through; channels use high and low ONLY), `csv_path`, `csv_sha256`.
- Fields not read: `open`, `adj_close`, `volume`. The signal module does not consume open prices (no entry timing decision), adj_close (downstream return-side concern), or volume (no liquidity filter or volume-weighted statistic).
- The signal module does not call `load_symbol()` / `load_all()` itself.
- The signal module does not call `validate_loaded_symbol()` / `validate_all()` itself.

## 4. Outputs the future build turn will create

The build turn for Step 05 shall create the following artifacts and no others:

- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/signal.py (the signal module).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/__init__.py (re-exports the public API listed in section 7).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/README.md (usage docs; pins spec/loader/validator/audit shas).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/test_signal.py (the test suite enumerated in section 18).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/__init__.py (test package marker; may be empty).
- reports/s7_d1_cross_asset_donchian_step_05_signal_module_build_report.json (sealed; canonical Python-side seal scheme).
- reports/s7_d1_cross_asset_donchian_step_05_signal_module_build_report.md (companion human-readable form).

No other files. No supplementary modules. No log files at any path.

## 5. Files the build turn may create or modify later

Permitted writes by the build turn (subject to its own separate authorization):

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested name: scripts/_s7_d1_donchian_step_05_signal_build.py) written, run once, and deleted on success.
- A temporary sealing helper under scripts/ if needed, deleted on success.

The temp scripts shall be byte-deleted on success. Failure cases leave them in place pending a separately authorized cleanup turn.

## 6. Files the build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed is also not permitted unless it is in section 5.

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json.
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json.
- All reports/s7_d1_cross_asset_donchian_step_02b_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_02c_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_03_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_04_*.{json,md}.
- docs/s7_d1_cross_asset_donchian_spec.md.
- docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md.
- docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md.
- docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md.
- docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md.
- This Step 05 plan file.
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/ contents.
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/ contents.
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/ contents.
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/ contents.
- CLAUDE.md, docs/decisions.md, RUNBOOK (if present), pipeline_manifest (if present), .gitignore.
- All ORB branch artifacts.
- All Step 30 cost constants.
- review_queue.json, the idea_memory directory, Strategy Lab artifacts.
- The Databento-track runner harness path external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/.

## 7. API surface

The signal module shall expose exactly the following public API and no other public symbols:

- ENTRY_CHANNEL_LOOKBACK: int = 55 (HARDCODED; matches parent spec section 5; not configurable).
- EXIT_CHANNEL_LOOKBACK: int = 20 (HARDCODED; matches parent spec section 5; not configurable).
- IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30") (HARDCODED; matches spec section 11; not configurable).
- class SignalError(Exception) - base class for every refusal mode.
- class SignalInputError(SignalError) - input not a LoadedSymbol or LoadedSymbol structurally invalid.
- class SignalOosBlockedError(SignalError) - any attempt to compute signals for OOS or post-OOS bars.
- class SignalParameterOverrideError(SignalError) - any attempt to override the hardcoded lookbacks or IS window.
- @dataclass(frozen=True) class SignalEvent (per-bar; schema in section 8).
- @dataclass(frozen=True) class SignalResult (per-symbol; schema in section 8).
- @dataclass(frozen=True) class CrossSymbolSignalResult (per-portfolio; schema in section 8).
- def compute_signals(loaded: LoadedSymbol) -> SignalResult - per-symbol IS-only signal computation.
- def compute_signals_all(data: Mapping[str, LoadedSymbol]) -> CrossSymbolSignalResult - per-portfolio IS-only signal computation.

No other public function. No public mutable state. No module-level data load at import time. No public function that accepts a `window=` parameter, a `lookback=` parameter, or any other parameter that could relax the hardcoded constants. No `compute_signals_oos`, no `compute_signals_post_oos`, no `compute_signals_full`, no `compute_signals_window` function.

## 8. SignalResult / SignalEvent schema

SignalEvent (per-bar, immutable):

- date: str (YYYY-MM-DD).
- bar_index: int (0-based index into LoadedSymbol.dates).
- entry_channel_high_55: float (max of loaded.high over bars [bar_index - 55, bar_index - 1] inclusive).
- entry_channel_low_55: float (min of loaded.low over bars [bar_index - 55, bar_index - 1] inclusive).
- exit_channel_high_20: float (max of loaded.high over bars [bar_index - 20, bar_index - 1] inclusive).
- exit_channel_low_20: float (min of loaded.low over bars [bar_index - 20, bar_index - 1] inclusive).
- today_high: float (carried through from loaded.high[bar_index]).
- today_low: float (carried through from loaded.low[bar_index]).
- today_close: float (carried through from loaded.close[bar_index]).
- entry_long_triggered: bool (today_high > entry_channel_high_55).
- entry_short_triggered: bool (today_low < entry_channel_low_55).
- exit_long_triggered: bool (today_low < exit_channel_low_20).
- exit_short_triggered: bool (today_high > exit_channel_high_20).

SignalEvent contains NO PnL field, NO position-size field, NO sizing-N field, NO Wilder-ATR field, NO stop-distance field, NO entry-timing field, NO order-status field, NO trade-id field, NO portfolio-level field. Those are downstream simulator concerns.

SignalResult (per-symbol, immutable):

- symbol: str.
- csv_sha256_observed: str (carried through from LoadedSymbol).
- window: tuple[str, str] = IN_SAMPLE_WINDOW (always; the field is included to make the IS-only constraint explicit in the result).
- bars_in_window: int (count of LoadedSymbol bars whose date lies in IN_SAMPLE_WINDOW).
- first_signal_eligible_bar_index: int (first index that has both >= ENTRY_CHANNEL_LOOKBACK prior loaded bars AND a date inside IN_SAMPLE_WINDOW).
- first_signal_eligible_date: str.
- last_signal_eligible_bar_index: int (last IS-window-resident bar with sufficient prior history).
- last_signal_eligible_date: str.
- signals: tuple[SignalEvent, ...] (one SignalEvent per signal-eligible IS bar; in chronological order; length equals last_eligible_index - first_eligible_index + 1).
- oos_signal_intentionally_omitted: bool (always True; permanent attestation).
- post_oos_signal_intentionally_omitted: bool (always True; permanent attestation).

CrossSymbolSignalResult (per-portfolio, immutable):

- per_symbol: Mapping[str, SignalResult] (keys: SPY, TLT, GLD, USO).
- cross_symbol_bars_in_window_equal: bool.
- cross_symbol_first_eligible_date_equal: bool.
- cross_symbol_last_eligible_date_equal: bool.
- oos_signal_intentionally_omitted: bool (always True).
- post_oos_signal_intentionally_omitted: bool (always True).

All three dataclasses are frozen. No mutable fields.

## 9. Channel computation rules (sourced from parent spec section 5; no new design)

The parent spec section 5 pins the channel construction byte-equivalently:

> "Channel construction: Donchian high/low over the previous 55 closed RTH daily bars (not including the current forming bar)"

This plan inherits that rule exactly:

- The entry channel high at bar index i is computed as the maximum of `loaded.high[j]` for j in `range(i - ENTRY_CHANNEL_LOOKBACK, i)` (i.e., the 55 bars whose indices are `i-55, i-54, ..., i-1` inclusive; NOT including bar i itself).
- The entry channel low at bar index i is the minimum of `loaded.low[j]` over the same 55-bar window.
- The exit channel high at bar index i is the maximum of `loaded.high[j]` for j in `range(i - EXIT_CHANNEL_LOOKBACK, i)` (i.e., bars `i-20, i-19, ..., i-1`).
- The exit channel low at bar index i is the minimum of `loaded.low[j]` over the same 20-bar window.

Channels use the `high` and `low` columns (not `close` and not `adj_close`). This matches the spec language ("RTH high" and "RTH low"). The signal module does NOT use close or adj_close for channel construction; close is carried through onto SignalEvent.today_close ONLY for transparency.

The channel computation at bar i is permitted to LOOK BACK at bars indexed less than `first_signal_eligible_bar_index` (those bars are loaded warmup data, not OOS data). The channel computation is NEVER permitted to look forward to a date past `IN_SAMPLE_WINDOW[1]` or to use any value from a bar whose date is in `OUT_OF_SAMPLE_WINDOW` or `POST_OOS_DIAGNOSTIC_WINDOW`. The structural guard in section 11 enforces this.

## 10. Entry and exit trigger rules (sourced from parent spec section 5; no new design)

Spec section 5 pins the trigger rules byte-equivalently:

> "Long entry trigger: Today's RTH high > previous 55-bar high"
> "Short entry trigger: Today's RTH low < previous 55-bar low"
> "Exit on opposite Donchian: Long exits if today's RTH low < previous 20-bar low; short exits if today's RTH high > previous 20-bar high"

This plan inherits those triggers exactly:

- entry_long_triggered at bar i = (loaded.high[i] > entry_channel_high_55 at bar i).
- entry_short_triggered at bar i = (loaded.low[i] < entry_channel_low_55 at bar i).
- exit_long_triggered at bar i = (loaded.low[i] < exit_channel_low_20 at bar i).
- exit_short_triggered at bar i = (loaded.high[i] > exit_channel_high_20 at bar i).

The signal module computes ALL FOUR flags per signal-eligible IS bar, regardless of any hypothetical position state. The signal module does NOT track whether a position is currently open; that is simulator state. The signal module does NOT decide whether to act on a trigger; that is simulator policy. The signal module simply records "this trigger fired on this bar," and the downstream simulator consumes the event stream.

The mechanic is intentionally BIDIRECTIONAL per spec section 5 (long and short triggers both pinned). The signal module is NOT long-only and is NOT short-only; it is "long/short trigger detector". Whether the downstream simulator chooses to act on shorts is a simulator decision, not a signal-module decision.

## 11. IS-only structural enforcement

The signal module shall structurally refuse to compute any signal for any bar whose date lies in `OUT_OF_SAMPLE_WINDOW` or `POST_OOS_DIAGNOSTIC_WINDOW`. The enforcement layers are:

1. The public API has NO function that accepts a `window=` parameter; the caller cannot inject a non-IS window.
2. The hardcoded `IN_SAMPLE_WINDOW` constant equals `("2013-01-01", "2022-12-30")` and is the ONLY window for which signal-eligible bars are constructed.
3. The signal-eligibility predicate is `(date >= IN_SAMPLE_WINDOW[0]) AND (date <= IN_SAMPLE_WINDOW[1]) AND (bar_index >= ENTRY_CHANNEL_LOOKBACK)`. The loop generating SignalEvents iterates only over indices satisfying this predicate.
4. After the loop, the module asserts that the LAST SignalEvent's date is `<= IN_SAMPLE_WINDOW[1]`. Failure is a HALT with SignalOosBlockedError.
5. The module asserts that no SignalEvent's date is in `OUT_OF_SAMPLE_WINDOW` or `POST_OOS_DIAGNOSTIC_WINDOW`. Failure is a HALT with SignalOosBlockedError.

Channel computation IS permitted to read bars whose index precedes `first_signal_eligible_bar_index` (those are loaded warmup bars; for the ETF-proxy dataset these have dates in 2014-01-02 onwards, all of which are pre-IS-window-coverage in a strict spec sense but are PRE-signal-eligible loaded data, not OOS data). Channel computation is NEVER permitted to read a bar whose date lies in `OUT_OF_SAMPLE_WINDOW` or `POST_OOS_DIAGNOSTIC_WINDOW`, because the IS-window-resident bars all have indices less than the first OOS-window-resident bar.

Concretely, with the validator-pinned ETF-proxy dataset: last IS-window date = 2022-12-30 (or nearest prior trading day); first OOS-window date = 2023-01-03 (Tuesday, first trading day on or after 2023-01-01). Channels computed for the last IS bar look back at bars all within IS. Channels computed for any OOS bar would have to look back at IS bars (legitimate warmup) but compute a signal FOR an OOS bar (forbidden). The signal-eligibility predicate strictly excludes OOS bars from the loop.

## 12. Warmup handling and first-eligible-bar policy

A bar i is signal-eligible iff `i >= ENTRY_CHANNEL_LOOKBACK` (i.e., the prior 55 bars all exist in the loaded data) AND `IN_SAMPLE_WINDOW[0] <= loaded.dates[i] <= IN_SAMPLE_WINDOW[1]`.

For the ETF-proxy dataset (data starts 2014-01-02, IS window starts 2013-01-01): the first IS-window-resident loaded bar is at index 0 with date 2014-01-02. Bar 0 has only 0 prior loaded bars, so it is NOT signal-eligible. The first signal-eligible bar is the one at index 55, which the Step 04 validator pinned as date 2014-03-24. This matches the validator's `first_in_sample_signal_eligible_index = 55` and `first_in_sample_signal_eligible_date = 2014-03-24`. The signal module's `first_signal_eligible_bar_index` and `first_signal_eligible_date` shall match these values.

For the last signal-eligible bar: it is the largest index whose date is `<= IN_SAMPLE_WINDOW[1] = "2022-12-30"`. For the ETF-proxy dataset, this is the trading day on or before 2022-12-30; the build turn shall compute it from the LoadedSymbol.dates rather than hardcoding it.

The signal module shall NOT generate any SignalEvent for a bar that fails the eligibility predicate. The signal module shall NOT pad, repeat, fill, or interpolate a missing signal. If the LoadedSymbol has 2266 IS-window-resident bars (the validator's per-symbol pin), the number of signal-eligible bars is exactly `2266 - 55 = 2211` IF the first IS-resident loaded bar is at index 0 (which is the case for this dataset). The build turn shall verify this arithmetic at runtime.

## 13. Determinism, no-state, no-side-effects rules

The signal module shall be a pure deterministic function from input LoadedSymbol to output SignalResult. The same LoadedSymbol input shall produce the same SignalResult output across any number of invocations and across any Python process.

The signal module shall NOT use:

- random number generators of any kind (no `random`, no `numpy.random`, no `secrets`);
- the current wall-clock time;
- environment variables;
- module-level mutable state;
- caches that persist across calls in module-level dicts/lists;
- any global counter that increments;
- any side-effecting operation: no print to stdout from the public API (the build script's stdout logging is separate); no logging.info; no file write; no network call; no exception suppression that hides nondeterminism.

The signal module's `compute_signals` and `compute_signals_all` shall not mutate the input LoadedSymbol or any field of it. The returned SignalResult is the only effect.

A test (T11) shall verify determinism by running compute_signals(load_symbol("SPY")) twice and asserting the two SignalResult instances are field-equal.

## 14. No-parameter-optimization, no-filter, no-regime, no-asset-selection, no-winner-selection

The signal module shall NOT support:

- any optimization loop over ENTRY_CHANNEL_LOOKBACK or EXIT_CHANNEL_LOOKBACK or any other parameter;
- any grid search over lookbacks or any other parameter;
- any alternative lookback value besides 55 and 20 (no 50, no 60, no 25, no 15, no 200, no 100, etc.);
- any filter on top of the trigger (no same-direction trend filter, no moving-average filter, no regime filter, no volatility filter, no dependence filter);
- any asset selection rule (no "trade only the top-N performers"; no "trade only the lowest-volatility symbol"; no momentum-rank gate);
- any winner-selection rule (no "after the run, keep only the symbols that worked");
- any parameter that varies across symbols (lookbacks are global constants);
- any path that "tries" a parameter and discards it (no compute-and-throw-away pattern, since that would be search-by-stealth);
- any function name suggesting a search or sweep (no `_search_`, no `_sweep_`, no `_optimize_`, no `_tune_`).

The mechanic is locked at spec time per parent spec section 5 and is byte-equivalent to s4/s5/s6 sealed chains. Loosening the lookbacks or adding a filter is a parameter change requiring a fresh `_revN_` spec.

## 15. No-simulator, no-backtest, no-PnL, no-portfolio boundary

The signal module shall NOT contain:

- any simulator step that advances a position state across bars;
- any position-tracking variable;
- any pyramid step computation;
- any Wilder ATR computation (this is sizing-side; deferred to simulator);
- any stop computation (also sizing/risk-side; deferred);
- any entry-timing decision (no MOC/ONO logic; the signal records "trigger fired"; the simulator decides timing);
- any order generation;
- any fill simulation;
- any commission computation;
- any slippage computation;
- any sizing computation (no contracts, no shares, no risk fraction);
- any PnL computation (no `daily_pnl`, no `cumulative_pnl`, no `realized_pnl`, no `unrealized_pnl`);
- any return-series computation (no `daily_return`, no `log_return`, no `pct_change(`, no `compute_return`, no `cumulative_return`, no `annualized_return`, no `return_series`, no any-prefix `_returns_` or any-suffix `_returns`);
- any portfolio-level aggregation (no `portfolio_value`, no `portfolio_equity`, no `aggregate_pnl`);
- any performance statistic (no `sharpe`, no `sortino`, no `calmar`, no `drawdown`, no `max_drawdown`, no `volatility_annualized`);
- any pairwise dependence measure (no `correlation`, no `covariance`, no `pearson`, no `spearman`, no `kendall`);
- any rolling pandas API call (no `.rolling(`);
- any backtest engine import or call (no `import backtrader`, no `import vectorbt`, no `import quantconnect`, no `lean`).

These quantities exist downstream in the simulator and backtest phases, each requiring their own plan and operator authorization. The signal module's scope is strictly the four trigger flags per IS bar.

## 16. Out-of-sample protection rule

This is the cornerstone safety rule for the signal module. It strengthens the Step 04 validator's OOS protection rule.

For any bar whose date is in `OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")` or `POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")`:

- The signal module shall NOT compute entry_channel_high_55 OR entry_channel_low_55 OR exit_channel_high_20 OR exit_channel_low_20 FOR that bar.
- The signal module shall NOT compute any trigger flag FOR that bar.
- The signal module shall NOT include that bar in the returned SignalResult.signals tuple.
- The signal module shall NOT include that bar's date in any returned summary statistic.
- The signal module shall NOT use that bar's high, low, close, open, adj_close, or volume in any computation that produces a returned value.
- The signal module shall NOT iterate the SignalEvent loop into bars with dates >= `OUT_OF_SAMPLE_WINDOW[0]`.

The `oos_signal_intentionally_omitted = True` attestation is permanent on every SignalResult and CrossSymbolSignalResult. It is an attestation that the OOS protection rule was applied, not a toggle.

A separate future operator authorization is required to inspect OOS values for any purpose. Even when an IS run passes (Step 06+ verdict PASS), OOS inspection requires its own plan and authorization. Step 05 does NOT pre-authorize OOS work in any form.

## 17. No-Databento, no-yfinance, no-network, no-API-key boundary

The signal module shall NOT contain any of: `import yfinance`, `import databento`, `import requests`, `import urllib.<anything>`, `from urllib import <anything>`, `import http.client`, `import socket`, `import curl_cffi`, `import aiohttp`, `import httpx`, `import grpc`, `import pyarrow.flight`.

The signal module shall NOT call os.environ to read any variable beginning with `DATABENTO_`, `API_KEY`, `SECRET`, `TOKEN`, or `PASSWORD`. The signal module shall NOT call os.environ["DATABENTO_API_KEY"] under any circumstance. The signal module shall NOT disable SSL verification (no `verify=False`, no `ssl._create_unverified_context`, no `PYTHONHTTPSVERIFY=0`, no `urllib3.disable_warnings`). The signal module performs no network IO at all; it does not even import a network library.

The signal module shall NOT perform any file IO (no `open()`, no `Path.read_bytes`, no `Path.write_bytes`). It is pure in-memory like the validator.

The build report shall include an api_key_safety_confirmation block attesting:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_imported_by_signal: false
- yahoo_finance_called_by_signal: false
- any_network_call_by_signal: false
- any_file_io_by_signal: false

## 18. No-Strategy-Lab, no-review-queue, no-brokerage, no-live-trading boundary

The signal module shall NOT touch any production-side artifact:

- no `import strategy_lab` or any submodule;
- no read of `strategy_lab/data/...`;
- no write to `strategy_lab/data/...`;
- no read or write of `review_queue.json`;
- no read or write of any `idea_memory` artifact;
- no `import sparta_commander` or any submodule;
- no `import spartacus` or any submodule;
- no `import hydra_video` or any submodule;
- no `import app` (the FastAPI dashboard root);
- no `import sparta_brain` or similar production package roots;
- no `import broker` / `import interactive_brokers` / `import alpaca` / `import tradestation` / `import ibapi` / `import binance` / `import oanda`;
- no `import quantconnect` / `import lean` / `import qcalgorithm`;
- no path that references a "live trading" code branch;
- no `import paper_trade` or `import paper_broker`;
- no `import scheduler` or `import autopilot` (the production scheduling layer);
- no `import frc` or `import frc_gate` (Forward Risk Controls).

The signal module is strictly the s7 D1 cross-asset Donchian yfinance proxy research module. It does not touch any production code path. It does not interact with `obsidian-trade-logger` or any other live tracking surface.

## 19. Forbidden tokens with grep semantics

The build turn shall run a case-sensitive static grep over `signal.py` bytes. The following tokens are FORBIDDEN. Any line containing a forbidden token outside a designated comment-exclusion line is a HALT.

A "designated comment-exclusion line" is a line that begins with `#` (whitespace OK before `#`) AND contains the literal substring `FORBIDDEN_TOKEN_EXCLUSION` AND continues with the reason (e.g., `# FORBIDDEN_TOKEN_EXCLUSION: this is the spec-mandated word in this docstring`). The exclusion-marker discipline keeps audits transparent: if a forbidden token must appear in a comment or docstring, the line carries an explicit waiver.

The Step 05 forbidden-token list (cumulative with prior phases' lists where applicable):

Vendor / credential / network (must not appear anywhere, including comments without the FORBIDDEN_TOKEN_EXCLUSION marker):

- `DATABENTO_API_KEY`
- `yfinance`
- `yahoo_finance`
- `databento`
- `requests.get`
- `urllib.request`
- `socket.connect`
- `http.client`
- `curl_cffi`
- `aiohttp`

Simulator / backtest / portfolio / trading-side (operator's broad-intent list, made unambiguous; no Python keyword false-match):

- `backtest`
- `portfolio`
- `pnl`
- `profit`
- `sharpe`
- `sortino`
- `calmar`
- `drawdown`
- `correlation`
- `covariance`
- `brokerage`
- `Strategy Lab` (exact phrase, with space)
- `review_queue`
- `live trading` (exact phrase, with space)
- `live_trading`

Return-computation tokens (specific enough not to flag Python's `return` keyword):

- `daily_return`
- `log_return`
- `pct_return`
- `pct_change(`
- `.pct_change(`
- `compute_return`
- `cumulative_return`
- `annualized_return`
- `return_series`
- `_returns_`
- `_returns,` (the plural at the start of an argument list / tuple)
- `returns_total`
- `arithmetic_return`
- `geometric_return`

Future-phase computation tokens (deferred to simulator):

- `Wilder` (English mixed case; the all-caps `WILDER` does not match)
- `ATR(` (function-call form; the bare word `ATR` standalone does not match)
- `.rolling(` (pandas API call)
- `wilder_atr`
- `wilder_n`
- `position_size`
- `position_state`
- `unit_count`
- `pyramid_unit`
- `stop_distance`
- `stop_price`
- `slippage`
- `commission`
- `fill_price`
- `order_id`
- `trade_id`

Donchian-specific note: the English word `Donchian` (mixed case) IS PERMITTED in the signal module's comments and docstrings without a FORBIDDEN_TOKEN_EXCLUSION marker, because the signal module's purpose IS Donchian channel computation and the word is descriptive. The constants `ENTRY_CHANNEL_LOOKBACK` and `EXIT_CHANNEL_LOOKBACK` are intentionally not named with the substring `DONCHIAN` (matching the spec language "entry channel" / "exit channel" rather than "Donchian channel").

Rolling-window note: the signal module implements rolling max/min over high and low columns. The implementation shall use explicit per-bar Python iteration (e.g., `max(loaded.high[i - 55:i])`) rather than a pandas `.rolling()` call. This keeps the dependency surface stdlib-only and avoids the `.rolling(` token entirely.

OOS / post-OOS guard tokens (must always appear True as attestations):

- `oos_signal_intentionally_omitted` (as a SignalResult / CrossSymbolSignalResult field name; permitted)
- `post_oos_signal_intentionally_omitted` (as a SignalResult / CrossSymbolSignalResult field name; permitted)

These two are SCHEMA tokens; they identify the OOS-protection attestations. They do NOT trigger the grep.

## 20. Validation gates V1-V10, test requirements T1-T16, build-script safety guardrails

V-gates the build turn shall verify, in order:

V1. The seven output files in section 4 exist at the locked paths.
V2. The signal module is syntactically valid Python (AST compiles).
V3. The signal module imports cleanly without performing any file IO at import time.
V4. The public API surface (section 7) matches exactly. No extra public symbol.
V5. The signal module contains no forbidden import (section 17 import list), verified by static grep.
V6. The signal module contains no forbidden token from the section 19 list, outside designated FORBIDDEN_TOKEN_EXCLUSION comment lines. Verified by static grep.
V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped tests. No xfail.
V8. The test suite includes every test in section 18 (T1..T16). Missing or renamed tests HALT.
V9. A live integration test: load_all() then compute_signals_all() returns CrossSymbolSignalResult with four per-symbol entries, each SignalResult.signals tuple has length > 0, every SignalEvent.date lies in IN_SAMPLE_WINDOW, every SignalEvent.bar_index >= ENTRY_CHANNEL_LOOKBACK.
V10. A live negative-path test set: (a) attempt to call compute_signals on None / dict / plain string -> SignalInputError; (b) attempt to read a SignalEvent for an OOS date in any returned tuple -> assertion 0 found; (c) attempt to monkey-patch the IN_SAMPLE_WINDOW constant on the module and re-call compute_signals -> still produces IS-only results (defensive copy or recheck inside the function ensures the operative window in use is the original constant value, OR the test asserts that no public API permits the override).

T-tests the build turn shall implement (renames forbidden; additions only if they uphold this plan's boundaries):

- T1: compute_signals returns SignalResult for SPY/TLT/GLD/USO with bars_in_window > 0.
- T2: every SignalEvent in result.signals has a date in IN_SAMPLE_WINDOW.
- T3: every SignalEvent has bar_index >= ENTRY_CHANNEL_LOOKBACK.
- T4: for each symbol, first_signal_eligible_date == validator pin "2014-03-24" and first_signal_eligible_bar_index == 55.
- T5: trigger flag arithmetic verified spot-check on at least one known trigger (e.g., assert that for SPY on a specific date where today_high > entry_channel_high_55, entry_long_triggered is True; the test inspects values rather than running a full simulator).
- T6: compute_signals raises SignalInputError on input that does not look like LoadedSymbol.
- T7: compute_signals_all raises SignalInputError on non-Mapping input.
- T8: compute_signals_all returns CrossSymbolSignalResult with the four expected keys; per-symbol SignalResult instances all share the same IN_SAMPLE_WINDOW and first/last eligible dates (cross-symbol consistency); cross_symbol_bars_in_window_equal True.
- T9: SignalResult.oos_signal_intentionally_omitted is True AND no SignalEvent date is in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW.
- T10: SignalResult and CrossSymbolSignalResult dataclasses have no field named anything like `pnl`, `profit`, `return`, `sharpe`, `drawdown`, `correlation`, `position_size`, `wilder_atr` (structural assertion via dataclasses.fields).
- T11: determinism: compute_signals(load_symbol("SPY")) twice produces equal SignalResults (compare field-by-field).
- T12: signal module performs no file IO at import (patched open/read_bytes sandbox).
- T13: signal module's static grep for section 19 forbidden tokens returns 0 hits outside FORBIDDEN_TOKEN_EXCLUSION lines.
- T14: signal module's static grep for section 17 forbidden imports returns 0 hits.
- T15: signal module's public API surface equals the section 7 list exactly.
- T16: attempting to import known forbidden-side packages from the signal module (e.g., by inspecting `sys.modules` after `compute_signals` runs) shows no `yfinance`, `databento`, `requests`, `urllib3`, `socket`, etc. were imported as a side effect of calling the signal module.

Build-script safety guardrails:

- The script shall not write to any path outside the section 4 output set + the section 5 temp-script paths.
- The script shall not import yfinance, databento, requests, urllib (any submodule), http.client, socket, curl_cffi, aiohttp, httpx.
- The script shall not set any environment variable beginning with `DATABENTO_`.
- The script shall not disable SSL verification.
- The script shall log its build steps to stdout for the build report writer to capture.
- The script shall self-delete on success.

## 21. Build report schema, build acceptance checklist, what build is NOT allowed to do, next authorization

Build report schema (sparta.donchian.step_05_signal_module_build_report.v1):

- schema, phase, controller_session, report_date_utc.
- plan_anchor: object with path, sha256, commit (this plan's commit).
- step_04_anchor: object with build_report_sha256, build_report_seal, validator_module_sha256.
- step_03_anchor: object with build_report_sha256, build_report_seal, loader_module_sha256.
- step_02c_anchor: object with audit_report_sha256, audit_report_seal, audit_manifest_sha256.
- output_files: object keyed by path; sha256 and bytes per entry.
- signal_api_surface_observed: list of the signal module's public symbols.
- v_gate_results: object with V1..V10 outcomes.
- t_test_results: object with T1..T16 outcomes.
- forbidden_token_grep_results: object with per-token hit counts.
- forbidden_import_grep_results: object with per-import hit counts.
- boundaries_held: object with one True flag per hard boundary in this plan.
- negative_invariants: object with one False flag per negative invariant.
- api_key_safety_confirmation: object with the seven fields in section 17.
- oos_protection_attestation: object with no_oos_signal_computed, no_post_oos_signal_computed, no_oos_value_inspected_by_signal_module.
- companion_md_sha256: string (one-way reference).
- seal_method: canonical string.
- report_seal_sha256: string.

Build acceptance checklist (for the future build turn to satisfy before claiming success):

- A separate operator authorization explicitly authorizes the Step 05 build.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md.
- The Step 03 loader module and Step 04 validator module are byte-unchanged at their pinned sha256s.
- The four CSVs and audit_manifest.json are byte-unchanged.
- The output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture before any write.
- No co-active Databento path. No co-active backtest path. No co-active simulator path.
- The build turn writes only the seven output files in section 4 plus the optional temp scripts in section 5 (each deleted on success).

What the build is NOT allowed to do:

- Compute a channel of any length OTHER than 55 (entry) or 20 (exit).
- Compute a Wilder ATR of any length.
- Compute any return, PnL, profit, drawdown, sharpe, or other performance statistic.
- Compute any correlation, covariance, or pairwise dependence measure.
- Compute any signal for any OOS or post-OOS bar.
- Run a simulator, a backtest, or a paper-trade loop.
- Make any live order, broker call, or live-trading code path.
- Modify any of the four canonical CSVs.
- Modify the existing fetch_run_manifest.json, audit_manifest.json, loader, validator, or any Step 02/03/04 artifact.
- Modify any spec or plan file.
- Modify ORB branch artifacts, Step 30 cost constants, review_queue.json, idea_memory, or Strategy Lab artifacts.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento or any vendor. Access DATABENTO_API_KEY.
- Disable SSL certificate verification.
- Inspect OOS or post-OOS values in any way that produces a returned-value or side-effect.
- Use the instruction phrase "compute signals now" as an active directive (this phrase appears here only as forbidden text).
- Treat the phrase "authorize Step 05 build" as a completed or current action (this phrase appears here only to mark a future-state authorization gate).
- Treat any downstream phase (Step 06 simulator, Step 07 backtest, OOS inspection, live trading) as pre-authorized.

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth for the signal-computation specification; the build turn is not pre-authorized by the plan itself.

Future expected status on the Step 05 build turn (informational; not granted here):

STEP_05_SIGNAL_MODULE_BUILT
SIGNAL_MODULE_TEST_SUITE_PASSED_T1_TO_T16
SIGNAL_MODULE_BUILD_REPORT_SEALED
NO_CSV_MODIFIED
NO_AUDIT_MANIFEST_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_LOADER_MODIFIED
NO_VALIDATOR_MODIFIED
NO_OOS_SIGNAL_COMPUTED
NO_POST_OOS_SIGNAL_COMPUTED
NO_WILDER_ATR_COMPUTED
NO_RETURNS_COMPUTED
NO_CORRELATION_COMPUTED
NO_PNL_COMPUTED
NO_PORTFOLIO_AGGREGATION
NO_SIMULATOR_RUN
NO_BACKTEST
NO_DATA_FETCH
NO_NETWORK_CALL
NO_FILE_IO_BY_SIGNAL_MODULE
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_STRATEGY_LAB_PROMOTION
NO_REVIEW_QUEUE_MUTATION
NO_BROKERAGE_CONNECTION
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- Step 06 (simulator) shall be specified in its own plan after Step 05 build completes successfully. The simulator is where position state, Wilder ATR, sizing, stops, entry-timing (MOC/ONO), and per-trade PnL first appear. The simulator REMAINS IS-only; OOS simulation is its own further plan with its own authorization. The simulator does NOT execute live trades.
- Step 07 (backtest) shall be specified in its own plan after Step 06. The backtest aggregates per-trade PnL into portfolio-level statistics. Still IS-only at first.
- OOS inspection is a separate plan beyond all of the above. Per spec section 11, OOS inspection is blocked until the IS run produces a verdict that authorizes OOS access.
- Live trading is a separate plan beyond all of the above and remains BLOCKED at 6 gates. No phase of this chain confers any standing authorization for live trading; each future live-trading-adjacent step would require its own explicit fresh operator approval.

----

End of plan. Plan-authoring turn only. No signal code written. No channel computed. No Wilder ATR. No returns. No correlation. No simulator. No backtest. No data fetch. No network. No Databento. No DATABENTO_API_KEY access. No OOS signal computed. No OOS inspection. No Strategy Lab. No review_queue mutation. No brokerage. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
