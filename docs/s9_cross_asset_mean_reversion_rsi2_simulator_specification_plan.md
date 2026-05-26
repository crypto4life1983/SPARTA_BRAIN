# s9 Cross-Asset Mean-Reversion RSI-2 - Simulator Specification Plan (Phase P7)

Status: PLAN_ONLY (no simulator code; no signal computation; no backtest; no fill simulation; no PnL computation; no commit beyond this single plan file).
Authored: 2026-05-26
BOUNDARY ALERT: This is the SECOND-TIER boundary-crossing phase in the s9 chain. The P6 signal module introduced signal-side code (RSI computation + trigger flag emission, in-sample-only). P8 (the build of this spec, separately authorized later) will introduce simulator-side code: position state, equal-dollar sizing, fills with slippage and commission, the K4 catastrophic safety park, daily equity tracking, and a per-trade ledger. The s9 simulator remains IS-only, contains no live-trading or brokerage code, contains no out-of-sample simulation, and contains no Step 07-style result-aggregation statistic.

Tier-N spec anchor: docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md (sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409, commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401).
Signal-module spec anchor: docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md (sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9, commit c5393ab31a58059004b8cd337cd428eacbcbaece).
P6 signal-module build (verdict PASS): commit 1a055bd1adecf30408de99971bf6e9f22cf53866, build report sha256 d78ad857ffc26a4392554d9208a9904513671c108037d24a02ba2d76de521b9b, seal f553ae8a31ec0ff11dc19cf5c5336c541698df306a82c5a716a836d875a4417a.
Selection plan anchor: docs/next_research_track_selection_plan_after_s7_d1_park.md (sha256 d8753155d47c36e07830750bf892743b8a1958d1ccc6d53932bee32ff76ec954, commit 530b54598fa7098eb746f2122b4002db2c984422).
Predecessor (parked): s7 D1 cross-asset Donchian yfinance ETF-proxy at REJECT_FAST. Park report sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263, commit a5ac092.
Pattern reference (not byte-equivalent inheritance): s7 D1 Step 06 simulator build (verdict PASS): commit ecd03e5, simulator.py sha256 7809cccf385b5f8b, build report sha256 cb826116c3a429fe341bc9d2c4b44a7e2312bb285f41bdd3a39baa7f78895254, seal db2b2e9a72d5713e0f44e1a9b44fb4ca59433db3211f3c0dc3ce40b0b4083a81. The s9 simulator follows the same authoring pattern (CostTier enum, ExitReason enum, TradeRecord ledger, SimulationResult dataclass, IS-only 5-layer enforcement) but is NOT a parameterization of the s7 D1 simulator; the s9 mechanic is structurally different (no Donchian channels, no Wilder ATR sizing, no pyramid, no hard stop).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No simulator implementation. No test implementation. No build report write. No signal computation. No fill simulation. No PnL computation. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No s7 D1 artifact mutation. No s7 D1 resurrection. No s9 Tier-N spec modification. No s9 signal-spec modification. No s9 signal-module modification. No selection-plan modification. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No Strategy Lab promotion. No candidate promotion. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Lock the specification for the s9 simulator module that will (in a separately authorized P8 build phase) consume LoadedSymbol structures from the Step 03 loader and SignalResult / CrossSymbolSignalResult structures from the s9 P6 signal module, apply the RSI-2 mean-reversion execution mechanic byte-equivalently per the s9 Tier-N spec sections 9-13, and produce an in-sample-only per-trade ledger plus a daily equity ledger. The simulator does NOT compute portfolio-level performance statistics (Sharpe, Sortino, Calmar, expectancy, win rate, effective independent bets, pairwise dependence measures); those are deferred to the future s9 aggregator phase (P9/P10). The simulator does NOT run any out-of-sample bar through any logic path. The simulator does NOT execute any live order, paper order, or brokerage call.

The simulator is a deterministic function from `(loaded, signals, cost_tier, starting_cash)` to a `SimulationResult` dataclass. It models the mechanical execution layer: applying the long-only RSI-2 entry trigger (`rsi_value < 10`) at the next bar's open with cost-tier-scaled entry slippage, exiting on the long-only RSI-2 exit trigger (`rsi_value > 50`) at the next bar's open with cost-tier-scaled exit slippage, sizing each entry at equal-dollar 1% of portfolio mark-to-market equity at the entry-trigger bar, tracking cash and mark-to-market equity per IS day, enforcing the K4 catastrophic-drawdown safety park (`portfolio_maxdd_pct > 50`), and flat-marking any still-open position at the last IS bar's close (`IN_SAMPLE_END_FLAT`). The simulator records per-trade ledger rows; it does not aggregate them into statistics.

## 2. Why P7 comes after P6 (and the second-tier boundary-crossing nature)

The s9 P6 signal-module build sealed PASS at commit 1a055bd. The signal module returns `SignalEvent` tuples per signal-eligible in-sample bar with long-only RSI threshold-crossing trigger flags. With signals computable, the next logical phase is the simulator that consumes those signals and executes them under the locked s9 mechanic.

P7 is the s9 chain's second-tier boundary-crossing phase. P6 introduced RSI computation; P7 introduces every remaining piece of the trading-mechanic vocabulary that P6 deliberately deferred: position state, equal-dollar sizing, fills, commission, slippage, per-trade dollar PnL, trade ledger, daily equity curve, and the K4 catastrophic-drawdown safety park. Each of those was forbidden in the s9 signal module by explicit token grep. P7 unblocks them STRUCTURALLY (the simulator IS sizing-and-state logic) while keeping a different list of tokens forbidden: result-aggregation statistics (Sharpe, Sortino, Calmar, expectancy, win-rate, pairwise dependence measures, effective independent bets), every live-trading and brokerage token, every parameter-optimization / filter / regime-gate / asset-selection token, every out-of-sample-simulation token, and the parent spec context tokens that do not apply to mean-reversion (Donchian, ATR for sizing, pyramid, hard stop, short-side).

The signal module's IS-only enforcement is inherited TRANSITIVELY: the simulator consumes the signal module's output, and the signal module structurally refuses to produce any OOS signal event. Therefore the simulator structurally cannot simulate any OOS bar (no signal exists for that bar). The simulator additionally enforces IS-only via direct date-window checks on every trade event it records (entry_trigger_date, entry_fill_date, exit_date, daily-equity-point date all in IN_SAMPLE_WINDOW), with HALT on any violation.

The build turn for P7 is the first turn whose code in the s9 chain consumes signal output and produces trade-execution artifacts. Like P6, every operator authorization beyond P8 (P9/P10 aggregator, P11 IS diagnostic, P12 IS memo, P13 lifecycle, P14/P15 OOS, live-trading-adjacent phases) requires its own explicit fresh operator approval; this plan does not pre-authorize any of those.

## 3. Inputs from prior phases

The simulator depends on the public API surfaces of the Step 03 s7 D1 loader (reused byte-equivalent for s9 per the Tier-N spec section 18 option L1) and the s9 P6 signal module. The simulator does not read CSV bytes directly. The simulator does not call the loader, validator, or signal module itself; the caller is responsible for calling those modules in order and passing the results.

Locked input contract:

- `loaded: Mapping[str, LoadedSymbol]` (from `load_all()` in the Step 03 s7 D1 loader). Keys must equal `{"SPY", "TLT", "GLD", "USO"}`. Each value is an immutable LoadedSymbol with tuple-typed `dates`, `open`, `high`, `low`, `close`, `adj_close`, `volume`, plus `symbol`, `csv_path`, `csv_sha256`. Inputs are not mutated.
- `signals: Mapping[str, SignalResult]` (from `compute_signals_all()` returning `CrossSymbolSignalResult.per_symbol`) OR `CrossSymbolSignalResult` directly. Keys must equal the same four symbols. Each value is an immutable SignalResult with `signals: tuple[SignalEvent, ...]`, IS-window pin, and `oos_signal_intentionally_omitted = True`. The simulator coerces `CrossSymbolSignalResult` to a Mapping via its `.per_symbol` attribute (mirroring the s7 D1 simulator's `_coerce_signals_to_mapping` pattern).
- `cost_tier: CostTier` enum value (S0, S1, S2, S3). S1 is the baseline. S4 is OUT OF SCOPE for the s9 simulator (per Tier-N section 13 byte-equivalent inheritance from s7 D1 spec).
- `starting_cash: float` (default 100000.0; per Tier-N section 11 inherits s7 D1 DEFAULT_STARTING_CASH). The build script shall reject negative or non-finite values.

The simulator MUST NOT accept any other public parameter: no `lookback=`, no `window=`, no `entry_threshold=`, no `exit_threshold=`, no `enable_short=`, no `borrow_cost_bps=`, no `commission_per_share=`, no `slippage_per_share=`, no `per_signal_allocation_fraction=`, no `compute_daily_equity_ledger=`. Cost-tier scaling is the only authorized parameterization, and only across the four locked tiers S0-S3.

The simulator reads only the LoadedSymbol fields needed for entry/exit execution: `symbol`, `dates`, `open` (for ONO fill price), `close` (for daily mark-to-market). It does NOT read `high`, `low`, `volume` (the s9 mechanic has no hard stop, no time stop, no intra-bar low-side check, no volume filter; therefore those fields are not required). `adj_close` is read by the signal module for RSI computation; the simulator uses `close` for mark-to-market because trade execution happens at raw prices, not dividend-adjusted prices.

## 4. Outputs the future P8 build turn will create

The P8 build turn shall create the following artifacts and no others:

- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/simulator.py`
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/__init__.py` (re-exports the public API in section 7)
- `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/README.md`
- `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/test_simulator.py`
- `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/__init__.py` (test package marker; may be empty)
- `reports/s9_cross_asset_mean_reversion_rsi2_simulator_build_report.json` (sealed; canonical Python-side seal scheme: `sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method`)
- `reports/s9_cross_asset_mean_reversion_rsi2_simulator_build_report.md` (companion human-readable form; MD references JSON sha; JSON does NOT embed MD sha to avoid the sha cycle resolved in the Step 02c audit pattern OR JSON embeds MD sha but MD does not embed JSON sha; either one-way reference is acceptable as long as the cycle is broken)

No other files. No log files. No data files. No supplementary modules.

## 5. Files the P8 build turn may create or modify later

- The seven output files in section 4.
- A temporary build script under `scripts/` (suggested: `scripts/_s9_simulator_build.py`), written, run once, deleted on success.
- A temporary commit-message file under `scripts/` if needed (mirroring the P6 signal-build apostrophe workaround), deleted on success.

Temp scripts byte-deleted on success; failures leave them pending a separately authorized cleanup turn.

## 6. Files the P8 build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed is also not permitted unless it is in section 5.

- All s7 D1 ETF-proxy artifacts (`external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_*/`, all `reports/s7_d1_cross_asset_donchian_*`). The s9 simulator may IMPORT from the Step 03 s7 D1 loader package read-only.
- The four canonical CSVs at `data/s7_d1_cross_asset_donchian/raw/*.csv`.
- `data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json` and `audit_manifest.json`.
- All s7 D1 plan files in `docs/s7_d1_cross_asset_donchian_step_*.md` and `docs/s7_d1_cross_asset_donchian_spec.md`.
- The s7 D1 park report and the s7 D1 terminal lesson append in `brain_memory/projects/trading_bot/lessons.md`.
- The s9 Tier-N spec, the s9 signal-module spec, the next-track selection plan, and this simulator spec file (the future P8 build turn quotes them and attests against them; does not edit them).
- The s9 P6 signal module package and its tests (`external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/`, `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/`). The simulator may IMPORT from the signal package read-only.
- The s9 signal-module build reports at `reports/s9_cross_asset_mean_reversion_rsi2_signal_module_build_report.{json,md}`.
- All Databento-track artifacts under `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/` and `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/` and any sealed s8 artifacts.
- `review_queue.json`, the production `idea_memory` directory, all Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- `CLAUDE.md`, `docs/decisions.md`, `RUNBOOK`, `pipeline_manifest`, `.gitignore`.

## 7. API surface

The simulator module shall expose exactly the following public API and no other public symbols:

- `RSI_LOOKBACK: int = 2` (echoed from the signal module; structural attestation that the simulator inherits the canonical RSI(2) mechanic; not used for computation in the simulator).
- `RSI_OVERSOLD_ENTRY_THRESHOLD: float = 10.0` (echoed; structural attestation).
- `RSI_EXIT_THRESHOLD: float = 50.0` (echoed; structural attestation).
- `MAX_UNITS_PER_SYMBOL: int = 1` (hardcoded; per Tier-N section 12 explicit no-pyramid lock; the simulator's entry rule refuses a second concurrent position on the same symbol).
- `PER_SIGNAL_ALLOCATION_FRACTION: float = 0.01` (hardcoded; per Tier-N section 11; 1.0% of portfolio mark-to-market equity per entry signal).
- `DEFAULT_STARTING_CASH: float = 100000.0` (per Tier-N section 11; inherits the s7 D1 simulator baseline).
- `K4_PORTFOLIO_MAXDD_PCT: float = 50.0` (hardcoded; per Tier-N section 10 step 8 K4 catastrophic stop).
- `IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30")` (hardcoded; matches the signal module's IS-only attestation).
- `ETF_DOLLAR_PER_SHARE: float = 1.0` (ETF-proxy adaptation; inherits from s7 D1 simulator; each $1 price change times 1 share equals $1 cash).
- `ETF_TICK_SIZE: float = 0.01` (ETF-proxy adaptation; penny tick; inherits from s7 D1 simulator).
- `class CostTier(Enum)` - values S0, S1, S2, S3 only (matches Tier-N section 13; S4 reserved is OUT OF SCOPE; loading S4 raises `SimulatorParameterOverrideError`).
- `class ExitReason(Enum)` - values:
  - `RSI_EXIT_TRIGGER` (the canonical s9 exit on `rsi_value > 50`).
  - `K4_FORCED_PARK` (catastrophic drawdown).
  - `IN_SAMPLE_END_FLAT` (any still-open position flat-marked at the last IS bar's close).
  No `DONCHIAN_20_EXIT` (s9 has no Donchian channel). No `STOP_HIT` (s9 has no hard stop per Tier-N section 10 step 5). No `TIME_STOP` (s9 has no time stop per Tier-N section 10 step 6). No `TRAILING_STOP`. No `PROFIT_TARGET`. No `PARTIAL_EXIT`.
- `class SimulatorError(Exception)` - base class for every refusal mode.
- `class SimulatorInputError(SimulatorError)` - input shape, type, or value invalid.
- `class SimulatorOosBlockedError(SimulatorError)` - attempt to simulate any bar outside IN_SAMPLE_WINDOW; raised by direct date-window check OR by the post-loop assertion / defensive scan.
- `class SimulatorParameterOverrideError(SimulatorError)` - attempt to override a hardcoded parameter or pass an unknown kwarg.
- `class SimulatorK4FiredError(SimulatorError)` - reserved for API completeness; current implementation uses the SimulationResult.k4_fired flag instead of raising (consistent with the s7 D1 simulator pattern).
- `@dataclass(frozen=True) class TradeRecord` - one row per long entry-exit cycle on a symbol (schema in section 8).
- `@dataclass(frozen=True) class DailyEquityPoint` - one row per IS trading day (schema in section 8).
- `@dataclass(frozen=True) class SimulationResult` - the function return value (schema in section 8).
- `def simulate(loaded: Mapping, signals: Mapping, cost_tier: CostTier = CostTier.S1, starting_cash: float = DEFAULT_STARTING_CASH) -> SimulationResult` - the single entry point. Rejects unknown kwargs via `**kwargs` defensive guard raising `SimulatorParameterOverrideError`.

No other public function. No public mutable state. No module-level data load at import time. No public function that accepts a `lookback=`, `window=`, `enable_short=`, `commission_per_share=`, `slippage_ticks=`, `borrow_cost_bps=`, or any other parameter outside the four pinned constants and the two API arguments (`cost_tier` and `starting_cash`).

The simulator does NOT expose a `simulate_oos` function, a `simulate_post_oos` function, a `simulate_full_window` function, an `optimize_thresholds` function, an `optimize_lookback` function, a `grid_search` function, a `bayes_search` function, a `compute_returns` function, a `compute_sharpe` function, or any aggregator-style summary function.

The s9 mechanic is LONG ONLY. The simulator does NOT model short-side execution. The simulator's TradeRecord does NOT have a `direction` field that can take the value "short" (it is fixed "long" or omitted; section 8 lists the canonical schema). Any signal-side `entry_short_triggered` would never be present on the s9 SignalEvent (the signal module forbids that field structurally per the signal spec section 9); transitively the simulator cannot encounter a short trigger.

## 8. Position state model, TradeRecord schema, DailyEquityPoint schema, SimulationResult schema

The simulator maintains the following stateful structures during a single `simulate()` call. None of this state is module-level; it is local to the call so that the function remains pure (same input -> same output across processes).

**Per-symbol open-position state** (one local instance per symbol while a unit is open; consolidated into a private `_SymbolState` class with `__slots__`, mirroring the s7 D1 simulator pattern):

- `symbol: str`
- `direction: "long" | None` (None if flat; "long" if a position is open; "short" is NEVER set per the long-only lock).
- `entry_trigger_date: str | None` (the bar at which the entry trigger fired).
- `entry_fill_date: str | None` (the next bar's date; ONO timing per Tier-N section 9 step 2).
- `entry_fill_price: float | None` (next bar's open + entry slippage at the chosen cost tier).
- `entry_slippage_dollars: float | None` (recorded for the eventual TradeRecord).
- `shares: int | None` (the equal-dollar-sized share count per section 11 below).
- `cost_basis_dollars: float | None` (`shares * entry_fill_price`; debited from cash on fill).
- `pending_action: dict | None` (queued at close of bar D, processed at open of D+1; one of `{"action": "ENTRY_PENDING", ...}` or `{"action": "EXIT_PENDING", ...}`; matches s7 D1 simulator pending_action pattern).

The simulator never holds more than one open position per symbol because `MAX_UNITS_PER_SYMBOL = 1` (Tier-N section 12 explicit lock). On a fired `entry_long_triggered` while a position is already open on the same symbol, the entry is SKIPPED and logged in an `entry_skip_log` tuple on the SimulationResult.

**Per-portfolio state**:

- `cash_balance: float` (mark-to-market is realized only at exit; intraday open positions consume cash equal to `shares * entry_fill_price` at entry and return cash equal to `shares * exit_fill_price` net of slippage and commission at exit).
- `portfolio_equity_high_water_mark: float` (for K4 drawdown tracking; computed from `cash_balance + sum(shares_open * close_today)` over all open positions).
- `max_drawdown_pct_observed: float` (peak-to-trough during the run, in percent).
- `k4_fired: bool` (set True if `max_drawdown_pct_observed > K4_PORTFOLIO_MAXDD_PCT`; simulation continues to log remaining bars as IN_SAMPLE_END_FLAT but no new entries permitted after K4 fires).
- `trade_records_closed: list[TradeRecord]` (chronological by exit_date).
- `entry_skip_log: list[dict]` (records: `{"symbol", "trigger_date", "reason"}` where reason is one of "position_already_open", "shares_floor_zero", "k4_already_fired", "starting_cash_zero").

**TradeRecord** (immutable frozen dataclass; one row per long entry-exit cycle on a symbol):

- `symbol: str`
- `trade_id: str` (synthesized as `f"{symbol}_{entry_trigger_date}"`).
- `direction: str = "long"` (fixed; structural long-only lock; the dataclass shape does not need a field if the direction is invariant, but recording it explicitly aids downstream inspection; the build-time invariant is that this value is exactly the string "long" on every TradeRecord).
- `entry_trigger_date: str` (the bar at which the RSI < 10 trigger fired).
- `entry_fill_date: str` (next bar's date; ONO timing).
- `entry_fill_price: float` (next bar's open + entry slippage at the chosen cost tier).
- `entry_slippage_dollars: float` (per-trade entry slippage cost).
- `shares: int` (equal-dollar-sized count; `floor(PER_SIGNAL_ALLOCATION_FRACTION * portfolio_equity_at_trigger / fill_price_pre_slippage)` or analogous formula locked at section 11).
- `exit_trigger_date: str` (the bar at which the RSI > 50 trigger fired OR the K4 day OR the last IS bar).
- `exit_fill_date: str` (next bar's date for RSI exit; SAME bar for K4 or IS-end-flat with close-of-day price).
- `exit_fill_price: float` (next bar's open minus exit slippage for RSI exit; close-of-day for K4 / IS-end-flat).
- `exit_slippage_dollars: float`
- `exit_reason: ExitReason`
- `commission_dollars: float` (per-round-trip commission applied at exit; ETF baseline is $0 per Tier-N section 13; cost tiers scale per section 11 below).
- `gross_pnl_dollars: float` (`shares * (exit_fill_price - entry_fill_price)`; long-only so always this signed expression).
- `net_pnl_dollars: float` (`gross_pnl - entry_slippage - exit_slippage - commission`).
- `hold_days: int` (count of IS calendar days between `entry_fill_date` and `exit_fill_date`, inclusive of entry-side and exclusive of exit-side; recorded for downstream diagnostic; the simulator does NOT use hold_days for any execution decision).

There is no `n_entry_dollars` field (no ATR). There is no `stop_price_at_entry` field (no hard stop). There is no `unit_index` field (no pyramid; if recorded for symmetry with the s7 D1 schema, it is fixed `0` on every TradeRecord). There is no `partial_stopped` field (no partial stops). There is no `trade_group_id` because every group has exactly one unit; `trade_id` is the unit's identifier.

**DailyEquityPoint** (immutable frozen dataclass; one row per IS trading day from the first signal-eligible date through the last):

- `date: str` (YYYY-MM-DD; in IN_SAMPLE_WINDOW).
- `cash_balance: float`
- `open_positions_count_total: int` (0 to 4; sum over the four symbols).
- `open_positions_per_symbol: Mapping[str, int]` (0 or 1 per symbol).
- `mark_to_market_equity: float` (`cash_balance + sum(shares_open * close_today)` over all open positions on this date).
- `drawdown_pct_from_high_water: float` (current drawdown vs running high-water mark, in percent).
- `k4_armed: bool` (True iff `drawdown_pct_from_high_water > K4_PORTFOLIO_MAXDD_PCT` on this bar; this is the "armed" flag and is fully equivalent to the simulator setting `k4_fired = True` at the same bar).

The DailyEquityPoint is recorded once per IS trading day across the cross-symbol-aligned date set (synchronized per Step 04 validator A3). The simulator does NOT skip days when no position is open; every IS trading day from `first_signal_date_processed` through `last_signal_date_processed` has exactly one DailyEquityPoint.

**SimulationResult** (immutable frozen dataclass; the function return value):

- `starting_cash: float` (echo of input).
- `final_cash_balance: float` (cash at end of IS, after IS-end-flat).
- `cost_tier: str` (the enum's `.name`, e.g., "S1").
- `cost_tier_slippage_scalar: float` (the slippage scalar applied; 0.0 / 1.0 / 3.0 / 5.0).
- `cost_tier_commission_scalar: float` (0.0 / 1.0 / 1.5 / 2.0).
- `per_signal_allocation_fraction: float` (echo of `PER_SIGNAL_ALLOCATION_FRACTION = 0.01`).
- `trade_records: tuple[TradeRecord, ...]` (chronological by entry_trigger_date).
- `trade_records_per_symbol: Mapping[str, int]` (count of closed records per symbol).
- `num_closed_trades_total: int` (length of trade_records).
- `entry_skip_log: tuple[dict, ...]` (the skip log).
- `daily_equity_ledger: tuple[DailyEquityPoint, ...]` (one point per IS trading day).
- `max_drawdown_pct_observed: float`
- `k4_fired: bool`
- `k4_fired_date: str | None` (the IS date on which K4 first triggered, or None).
- `in_sample_window: tuple = IN_SAMPLE_WINDOW` (echo for attestation).
- `first_signal_date_processed: str`
- `last_signal_date_processed: str`
- `oos_simulation_intentionally_omitted: bool` (always True; permanent attestation).
- `post_oos_simulation_intentionally_omitted: bool` (always True; permanent attestation).

All four dataclasses (TradeRecord, DailyEquityPoint, SimulationResult, plus the upstream signal-module ones consumed) are frozen and immutable.

## 9. Entry handling (per Tier-N section 9, byte-equivalent for s9 long-only RSI-2)

Entry sequencing:

1. The simulator iterates SignalEvents in chronological order across symbols. For each SignalEvent on symbol S with date D and `bar_index = i`:
2. If the per-symbol direction is None (flat) AND `entry_long_triggered` is True AND `k4_fired` is False: queue an ENTRY_PENDING LONG for the NEXT BAR's open on S. The bar `i+1` must exist in the loaded data (else the entry is SKIPPED and logged with reason "no_next_bar").
3. If the per-symbol direction is "long" (a position is already open on S) AND `entry_long_triggered` is True: NO new entry is queued; the existing position remains open; the trigger is logged in `entry_skip_log` with reason "position_already_open".
4. Else (rsi_value >= RSI_OVERSOLD_ENTRY_THRESHOLD): no entry is queued.
5. The s9 mechanic is LONG-ONLY. The simulator never queues a SHORT entry. The signal module structurally does not produce a `entry_short_triggered` field; the simulator confirms via type-check that the SignalEvent has only `entry_long_triggered` and `exit_long_triggered` boolean flags and no short-side flag.

ONO fill convention (matches s7 D1 simulator):

- At the open of bar `i+1` (the trading day after the trigger), the simulator computes:
  - `fill_price_pre_slippage = loaded.open[i+1]`
  - `entry_slippage_per_share = ETF_TICK_SIZE * slippage_scalar_for_tier` (S0 = 0; S1 = $0.01; S2 = $0.03; S3 = $0.05)
  - `entry_fill_price = fill_price_pre_slippage + entry_slippage_per_share` (long fills pay UP a tick of slippage)
- The simulator computes shares per section 11 below.
- If `shares < 1`, the entry is SKIPPED and logged with reason "shares_floor_zero".
- If `shares >= 1`:
  - `cost_basis_dollars = shares * entry_fill_price`
  - `cash_balance -= cost_basis_dollars`
  - `entry_slippage_dollars = shares * entry_slippage_per_share`
  - The per-symbol state is updated: direction = "long"; entry_trigger_date = D; entry_fill_date = dates[i+1]; entry_fill_price = entry_fill_price; entry_slippage_dollars = entry_slippage_dollars; shares = shares; cost_basis_dollars = cost_basis_dollars.

Entry slippage is NEVER subtracted from cash separately at entry; it is already embedded in `entry_fill_price`. The slippage dollar count is recorded on the eventual TradeRecord for downstream attribution.

## 10. Exit handling (per Tier-N section 10, byte-equivalent for s9 RSI-2)

Exit sequencing:

1. At each signal-eligible bar i on each symbol with an open position:
2. If `exit_long_triggered` is True (i.e., `rsi_value > RSI_EXIT_THRESHOLD = 50`): queue an EXIT_PENDING for the NEXT BAR's open. If bar `i+1` does not exist in the loaded data, fall through to the IN_SAMPLE_END_FLAT handling at the last IS bar (section 13).
3. If `exit_long_triggered` is False: the position remains open into the next bar.
4. There is NO hard stop. There is NO time stop. There is NO trailing stop. There is NO profit target. There is NO partial exit. The only exits are: (a) the canonical RSI > 50 trigger; (b) the K4 catastrophic park; (c) the IN_SAMPLE_END_FLAT boundary.

ONO exit fill convention:

- At the open of bar `i+1`, the simulator computes:
  - `fill_price_pre_slippage = loaded.open[i+1]`
  - `exit_slippage_per_share = ETF_TICK_SIZE * slippage_scalar_for_tier`
  - `exit_fill_price = fill_price_pre_slippage - exit_slippage_per_share` (long exits SELL DOWN a tick of slippage)
- `cash_balance += shares * exit_fill_price`
- `cash_balance -= commission_dollars` where `commission_dollars = COMMISSION_PER_RT_BASELINE * commission_scalar_for_tier * shares`. The Tier-N section 13 baseline is `$0.00 per share` so on the locked baseline this term is zero at S1; at S2/S3 with a non-zero baseline commission this would scale, but for ETF-proxy the baseline is zero so the term is zero across all tiers. The build script shall record this fact explicitly in the build report's `cost_baseline_commentary` field for transparency.
- The trade is closed: a TradeRecord is appended to `trade_records_closed`; the per-symbol state resets to direction = None and all fields None.

The first IS-end-flat or K4 day is handled in section 13; it uses `close[bar_at_event]` not the next bar's open.

## 11. Position sizing (per Tier-N section 11; equal-dollar 1% of portfolio mark-to-market equity at the entry-trigger bar)

Sizing formula (locked):

- `portfolio_equity_at_trigger = cash_balance + sum(open_position.shares * loaded[symbol].close[trigger_bar_index]) for open_position in all_open_positions` (i.e., mark-to-market at the close of the trigger bar D, BEFORE the next bar's fill).
- `target_dollars_per_signal = PER_SIGNAL_ALLOCATION_FRACTION * portfolio_equity_at_trigger` (= 0.01 * equity).
- `shares = math.floor(target_dollars_per_signal / fill_price_pre_slippage)` where `fill_price_pre_slippage = loaded.open[i+1]`.
- If `shares < 1`, the entry is SKIPPED and logged.
- If `loaded.open[i+1]` is non-positive (data outage), the entry is SKIPPED and logged.
- If `portfolio_equity_at_trigger` is non-positive (cash + mark-to-market < $0), the entry is SKIPPED and logged.

Notes:

- The 1% allocation is the LOCKED Tier-N value. Adjusting upward (e.g., to 5%) requires a fresh `_revN_` Tier-N spec. The Tier-N spec section 11 explicitly permits the simulator-spec plan to adjust UP to 5% if 1% produces no clearable signal noise; this s9 simulator spec EXPLICITLY DECLINES that adjustment and locks at 1% to preserve the conservative cost-stress sensitivity discussed in the Tier-N section 11 rationale. The cost-stress matrix is meaningful BECAUSE the per-trade dollar size is small relative to the per-share slippage cost; raising the allocation would dilute the cost-stress signal.
- The sizing fraction is applied at the TRIGGER bar D, not at the FILL bar D+1, to preserve determinism (the fill bar's mark-to-market depends on prices that are not yet known when the trigger fires; we size with information available at D's close).
- The shares count is an integer. Fractional shares are truncated. This matches the s7 D1 simulator's `floor` convention.

## 12. Cost / slippage / commission model (per Tier-N section 13; cost-stress matrix S0/S1/S2/S3)

Cost-tier scalar table (matches Tier-N section 13 byte-equivalent):

| Tier | Slippage scalar | Commission scalar | Purpose |
|---|---|---|---|
| S0 | 0.0 | 0.0 | Diagnostic floor; DR3 fires if survival is S0-only |
| S1 | 1.0 (baseline) | 1.0 (baseline) | Pre-registered baseline |
| S2 | 3.0 | 1.5 | Mild stress |
| S3 | 5.0 | 2.0 | Realistic adverse |

S4 is reserved and OUT OF SCOPE for the s9 simulator. Passing `CostTier.S4` to `simulate()` is impossible because the enum does not include S4; defensive `if cost_tier not in _TIER_SCALARS` raises `SimulatorParameterOverrideError`.

ETF-proxy baseline (S1 baseline values, multiplied by the tier scalars):

- `_COMMISSION_PER_RT_S1_DOLLARS_PER_SHARE = 0.0` (zero-commission ETF broker assumption per Tier-N).
- `_SLIPPAGE_ENTRY_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0` = $0.01 per share at entry, scaled by slippage_scalar.
- `_SLIPPAGE_EXIT_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0` = $0.01 per share at exit, scaled by slippage_scalar.
- `_SLIPPAGE_STOP_PER_SHARE_S1`: N/A (the s9 mechanic has no hard stop; this constant is not defined in the s9 simulator; the s7 D1 simulator's $0.02 stop slippage is not applicable).
- `_BORROW_COST_BPS_S1 = N/A` (long-only; no borrow cost).
- `_FUNDING_COST_BPS_S1 = N/A` (long-only ETF; no overnight funding charge).

Cost computation at exit:

- `commission_dollars = _COMMISSION_PER_RT_S1_DOLLARS_PER_SHARE * commission_scalar_for_tier * shares`.
- `entry_slippage_dollars` is embedded in `entry_fill_price` (a tick higher than `loaded.open[i+1]`).
- `exit_slippage_dollars` is embedded in `exit_fill_price` (a tick lower than `loaded.open[i+1]`).

DR rule evaluation IS NOT performed by the simulator. DR2 / DR3 / DR5 are aggregator-level (P9/P10) checks across the four cost-tier SimulationResults; the simulator merely produces ONE SimulationResult per `simulate()` call and the caller invokes `simulate()` four times (once per tier) to obtain the matrix.

## 13. K4 catastrophic safety park + IN_SAMPLE_END_FLAT boundary

K4 (catastrophic drawdown; per Tier-N section 10 step 8):

- After each daily mark-to-market update on the cross-symbol-aligned date set, the simulator computes:
  - `mark_to_market_equity_today = cash_balance + sum(shares_open * close_today)`.
  - If `mark_to_market_equity_today > portfolio_equity_high_water_mark`: update the high-water mark.
  - `drawdown_pct_today = (portfolio_equity_high_water_mark - mark_to_market_equity_today) / portfolio_equity_high_water_mark * 100.0`.
  - If `drawdown_pct_today > K4_PORTFOLIO_MAXDD_PCT` (= 50.0) AND `k4_fired` is currently False:
    - Set `k4_fired = True`.
    - Set `k4_fired_date = today`.
    - For every open position, immediately close at today's close: `exit_fill_price = close[bar_at_event]` (no slippage charged on the forced K4 close because the slippage is a model of mechanical fill, not catastrophe; this matches s7 D1 simulator behavior); `exit_reason = K4_FORCED_PARK`; append TradeRecord.
    - From this day forward, no new entries are permitted. The simulator continues to iterate the remaining IS bars to produce DailyEquityPoints (cash balance does not change once all positions are closed; mark-to-market equals cash).

The post-K4 iteration logs cleanly for transparency; the s9 simulator does not short-circuit on K4 day to terminate early.

IN_SAMPLE_END_FLAT (per Tier-N section 10 step 9):

- At the last IS bar's close (the latest date in IN_SAMPLE_WINDOW that appears in the cross-symbol-aligned date set), for every open position remaining:
  - `exit_trigger_date = last_is_date` (no separate trigger; the IS boundary itself is the exit signal).
  - `exit_fill_date = last_is_date` (close-of-day; no next-bar open is used because there is no next IS bar to fill at).
  - `exit_fill_price = loaded[symbol].close[last_is_bar_index]` (raw close; no slippage charged on the boundary close because it is a bookkeeping flat-mark, matching s7 D1 simulator behavior).
  - `exit_reason = IN_SAMPLE_END_FLAT`.
  - Append a TradeRecord. Reset per-symbol state.

The IS-end-flat handling is a STRUCTURAL safety: it guarantees that the simulator never carries a position into OOS bars (which it cannot anyway because the simulator's loop predicate excludes OOS bars, but the flat-mark also closes the bookkeeping cleanly so the SimulationResult has zero open positions at the end).

## 14. In-sample-only structural enforcement (five layers; inherited from the s9 signal-module pattern and the s7 D1 simulator pattern)

The simulator shall structurally refuse to simulate any bar whose date lies in `OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")` or `POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")`. Enforcement layers:

L1. **No `window=` parameter on `simulate()`**. The caller cannot substitute a non-IS window.

L2. **Hardcoded `IN_SAMPLE_WINDOW` constant**. The public constant `IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")` is the only window the simulator ever simulates against.

L3. **Eligibility predicate excludes OOS bars from the iteration loop**. The simulator's main loop iterates only over dates with `IN_SAMPLE_WINDOW[0] <= date <= IN_SAMPLE_WINDOW[1]`. SignalEvents on OOS dates are never delivered to the simulator (the upstream signal module structurally refuses them), but the simulator also checks SignalEvent.date directly and HALTs with `SimulatorOosBlockedError` if any non-IS SignalEvent is received.

L4. **Post-loop assertion**. After the simulator completes, it asserts that the last TradeRecord's exit_fill_date and the last DailyEquityPoint's date are both `<= IN_SAMPLE_WINDOW[1]`. Failure raises `SimulatorOosBlockedError`.

L5. **Defensive scan**. The simulator asserts that no TradeRecord field (entry_trigger_date, entry_fill_date, exit_trigger_date, exit_fill_date) and no DailyEquityPoint.date lies in OOS or post-OOS. Failure raises `SimulatorOosBlockedError`. The `oos_simulation_intentionally_omitted = True` and `post_oos_simulation_intentionally_omitted = True` attestation fields are permanent on every SimulationResult.

The ONO fill convention means that an exit triggered on the LAST signal-eligible IS bar (2022-12-30) would normally fill on the next bar (2023-01-03, the first OOS bar). The s9 simulator structurally REFUSES that fill: an exit triggered on the last IS bar is handled by `IN_SAMPLE_END_FLAT` (close-of-day on 2022-12-30 at that bar's close), not by fill on 2023-01-03. This is the analog of the s7 D1 simulator's IS-end-flat handling and is required to keep the simulator's outputs strictly IS-only.

## 15. Determinism + no-state + no-side-effects rules

The simulator shall be a pure deterministic function from input `(loaded, signals, cost_tier, starting_cash)` to output `SimulationResult`. Same input -> same output across any number of invocations and across any Python process.

The simulator shall NOT use:

- random number generators of any kind (no `random`, no `numpy.random`, no `secrets`).
- the current wall-clock time.
- environment variables.
- module-level mutable state (the `_SymbolState` private class has `__slots__` and is instantiated per-call inside `simulate()`; the module's top-level holds only immutable constants, immutable enum classes, immutable dataclasses, and pure functions).
- caches that persist across calls in module-level dicts/lists.
- any global counter that increments.
- any side-effecting operation: no print to stdout from the public API; no logging; no file write; no network call; no exception suppression that hides nondeterminism.

The simulator's `simulate()` shall not mutate the input `loaded` or `signals`. The returned SimulationResult is the only effect.

A test (T11) shall verify determinism by running `simulate(loaded, signals, CostTier.S1)` twice and asserting the two SimulationResults are field-equal across `num_closed_trades_total`, `final_cash_balance`, `max_drawdown_pct_observed`, `k4_fired`, the count of TradeRecords per symbol, and the count of DailyEquityPoints.

## 16. No-result-aggregation, no-statistics, no-OOS-inspection boundary

The simulator shall NOT contain:

- any portfolio-level performance statistic computation (no `sharpe`, no `sortino`, no `calmar`, no `expectancy`, no `win_rate`).
- any drawdown statistic beyond the K4 catastrophic check (the `max_drawdown_pct_observed` field on SimulationResult is the running peak-to-trough drawdown for K4 decision purposes; it is a STATE variable, not a downstream STATISTIC; the aggregator may re-compute or use it as input).
- any pairwise dependence measure (no `correlation`, no `covariance`, no `pearson`, no `spearman`, no `effective_independent_bets`, no `avg_pairwise_dependence`).
- any return-series computation as a public output (no `daily_return`, no `log_return`, no `pct_return`, no `compute_return`, no `cumulative_return`, no `annualized_return`, no `return_series`; the daily equity ledger records dollar mark-to-market, not return; the aggregator transforms equity to returns at its own discretion).
- any rolling pandas API call (no `.rolling(`).
- any backtest engine import or call.
- any OOS-side simulation. Loading SignalEvents whose dates lie in OUT_OF_SAMPLE_WINDOW raises `SimulatorOosBlockedError`. The simulator cannot be tricked into simulating OOS by manipulating the cost_tier or starting_cash arguments.
- any post-OOS-side simulation.
- any DR rule evaluation (DR2 / DR3 / DR5 are aggregator-level; the simulator produces one SimulationResult per tier).
- any A-gate / K-criterion evaluation (A1-A10 and K1-K12 are aggregator-level).
- any verdict assembly (the aggregator assembles the verdict from the four SimulationResults plus diversification statistics).

These quantities exist downstream in the s9 aggregator (P9/P10) and IS-diagnostic (P11) phases, each requiring its own plan and operator authorization.

## 17. Daily equity ledger requirements

The simulator's DailyEquityPoint ledger covers every IS trading day from the first signal-eligible date (per signal module: 2014-01-06 for the ETF-proxy dataset) through the last IS date (2022-12-30 or the latest cross-symbol-aligned date <= 2022-12-30). The cross-symbol-aligned date set is taken from the union of dates across the four LoadedSymbol.dates tuples, which the Step 04 validator A3 guarantees are identical; the simulator picks any one symbol's dates tuple as the master schedule.

Daily processing (per IS trading day `d`):

1. At the OPEN of day d: process pending entry / exit actions queued the previous bar. Update cash_balance and per-symbol state.
2. Iterate symbols in deterministic order (alphabetical: GLD, SPY, TLT, USO). For each symbol, look up the SignalEvent for day d (if any). Apply entry / exit rules to queue actions for day d+1.
3. At the CLOSE of day d: compute mark-to-market equity = cash + sum(open positions' shares * close[d]). Update high-water mark. Compute drawdown. Evaluate K4. Record DailyEquityPoint.

The deterministic symbol iteration order GLD-SPY-TLT-USO is locked at this Tier-N spec to ensure that ties (multiple symbols entering / exiting on the same day) are resolved identically across runs; the s7 D1 simulator uses the same alphabetical ordering and it is inherited.

The DailyEquityPoint count equals the count of cross-symbol-aligned IS trading days, which per the s9 signal-module build report is 2266. The simulator's ledger may exclude pre-first-signal-eligible days (i.e., 2014-01-02, 2014-01-03 -- the first two warmup IS bars; signal-eligibility starts at 2014-01-06); in that case the ledger length is 2264 and the simulator's `first_signal_date_processed` is "2014-01-06". The locked choice for s9 is: the daily equity ledger starts at the first signal-eligible date (2014-01-06) for clarity (no pre-warmup zero-position rows); the ledger length is then 2264. Alternative choices (start at first loaded date 2014-01-02; start at IN_SAMPLE_WINDOW[0] 2013-01-01) are forbidden.

## 18. Forbidden tokens, forbidden imports, V-gates V1-V10, T-tests T1-T16, build-script safety, build report schema

**Forbidden tokens (verified by static grep over simulator.py; comment-marker FORBIDDEN_TOKEN_EXCLUSION accepted for documentation; the orchestrator's relaxed inline marker convention from Step 07 applies):**

Vendor / credential / network:

- `DATABENTO_API_KEY`, `yfinance`, `yahoo_finance`, `databento`, `requests.get`, `urllib.request`, `socket.connect`, `http.client`, `curl_cffi`, `aiohttp`, `httpx`.

Live trading / brokerage / production:

- `Strategy Lab` (with space), `strategy_lab`, `review_queue`, `idea_memory`, `live trading` (with space), `live_trading`, `brokerage`, `broker_api`, `broker_session`, `alpaca`, `interactive_brokers`, `ibkr`, `ibapi`, `ib_insync`, `tradestation`, `binance`, `oanda`, `order_send`, `place_order`, `submit_order`, `cancel_order`, `modify_order`, `route_order`, `production_signal`, `paper_broker`, `paper_trade`, `scheduler`, `autopilot`, `frc_gate`.

Result-aggregation tokens (deferred to P9/P10 aggregator):

- `sharpe`, `sortino`, `calmar`, `expectancy`, `win_rate`, `correlation`, `covariance`, `pearson`, `effective_independent_bets`, `avg_pairwise_correlation`, `avg_pairwise_dependence`, `avg_pairwise_dependence_measure`.

Return-computation tokens (specific enough not to flag Python's `return` keyword):

- `daily_return`, `log_return`, `pct_return`, `.pct_change(`, `compute_return`, `cumulative_return`, `annualized_return`, `return_series`, `_returns_`, `_returns,`, `returns_total`, `arithmetic_return`, `geometric_return`.

Parent-spec context tokens (s7 D1 lock; s9 mechanic is structurally different):

- `Donchian` (s9 uses RSI, not Donchian channels; the literal English word `Donchian` shall not appear in the s9 simulator source).
- `ATR(` and `wilder_atr` and `wilder_n` (Wilder ATR is not used by s9; the simulator uses equal-dollar sizing, not ATR-based; the signal module uses Wilder smoothing for RSI which is a DIFFERENT Wilder usage and remains unblocked; the simulator never computes any Wilder construct).
- `pyramid` and `pyramid_unit` and `pyramid_step` and `MAX_UNITS_PER_SYMBOL = 4` (s9 has no pyramid; `MAX_UNITS_PER_SYMBOL = 1`).
- `stop_distance`, `stop_price`, `STOP_HIT`, `STOP_DISTANCE_N_MULTIPLE`, `DONCHIAN_20_EXIT` (s9 has no hard stop and no Donchian exit; these tokens shall not appear).

Optimization tokens forbidden:

- `_optimize_`, `_sweep_`, `_tune_`, `_grid_search_`, `_bayes_search_`, `alternative_lookback`, `alternative_threshold`, `lookback_grid`, `threshold_grid`, `parameter_grid`, `winner_selection`, `asset_selection`, `top_n_pick`.

Filter / regime tokens forbidden:

- `regime_filter`, `regime_gate`, `ma_filter`, `vol_filter`, `dependence_filter`, `correlation_filter`, `trend_filter`, `volume_filter`.

Short-side tokens forbidden (long-only enforcement):

- `entry_short_triggered`, `exit_short_triggered`, `short_position`, `borrow_cost`, `borrow_rate`, `short_entry`, `short_exit`, `direction == "short"`, `direction = "short"`.

OOS-related tokens forbidden:

- `simulate_oos`, `compute_oos`, `oos_simulation`, `post_oos_simulation`, `simulate_full_window`, `force_oos`.

Tokens NEWLY UNBLOCKED in the s9 simulator (were forbidden in the s9 signal module):

- `pnl`, `gross_pnl`, `net_pnl`, `gross_pnl_dollars`, `net_pnl_dollars` (the simulator IS a PnL computer at the per-trade level; downstream aggregator computes portfolio statistics).
- `commission`, `commission_dollars`, `slippage`, `entry_slippage_dollars`, `exit_slippage_dollars`, `cost_basis_dollars` (the simulator IS a cost computer; these are unblocked).
- `position_size`, `position_state`, `direction`, `shares` (the simulator IS a position-tracking layer; these are unblocked).
- `drawdown` and `drawdown_pct_from_high_water` and `max_drawdown_pct_observed` (the simulator uses drawdown for the K4 catastrophic decision and records it on SimulationResult; the AGGREGATOR may compute additional drawdown statistics).
- `fill_price`, `entry_fill_price`, `exit_fill_price`, `entry_fill_date`, `exit_fill_date`, `trade_id` (the simulator IS a fill-level ledger; these are unblocked).
- `mark_to_market` and `mark_to_market_equity` (the simulator computes mark-to-market for K4 evaluation and the daily equity ledger).
- `portfolio_equity_high_water_mark`, `cash_balance` (per-portfolio state; unblocked).
- `K4_FORCED_PARK`, `IN_SAMPLE_END_FLAT`, `RSI_EXIT_TRIGGER` (the three legitimate ExitReason values; unblocked).

The s9 simulator does NOT unblock: `Sharpe`, `Sortino`, `Calmar`, `expectancy`, `win_rate`, `correlation`, `covariance`, `effective_independent_bets`, `avg_pairwise_dependence`, `Donchian`, `ATR(`, `pyramid`, `hard_stop`, `time_stop`, `trailing_stop`. Those remain forbidden.

**Forbidden imports (verified by static grep):**

- `import yfinance`, `import databento`, `import requests`, `import urllib.*`, `from urllib`, `import http.client`, `import socket`, `import curl_cffi`, `import aiohttp`, `import httpx`, `import grpc`, `import pyarrow.flight`.
- `import strategy_lab`, `import sparta_commander`, `import spartacus`, `import hydra_video`, `import app`, `import sparta_brain`.
- `import broker`, `import interactive_brokers`, `import alpaca`, `import tradestation`, `import ibapi`, `import binance`, `import oanda`, `import ib_insync`, `import quantconnect`, `import lean`, `import qcalgorithm`.
- `import pandas`, `import numpy`, `from pandas`, `from numpy`. (The s9 simulator uses stdlib only, matching the s7 D1 simulator pattern. The signal module also uses stdlib only.)

**V-gates the P8 build turn shall verify in order:**

- V1. The seven output files in section 4 exist at the locked paths.
- V2. The simulator module is syntactically valid Python (AST compiles).
- V3. The simulator imports cleanly without performing any file IO at import time (patched-builtins sandbox).
- V4. The public API surface (section 7) matches exactly. No extra public symbol.
- V5. The simulator contains no forbidden import.
- V6. The simulator contains no forbidden token, outside designated FORBIDDEN_TOKEN_EXCLUSION lines.
- V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped. No xfail.
- V8. The test suite includes every T1..T16 (section 19 below).
- V9. A live in-sample integration: load_all via the Step 03 s7 D1 loader, compute_signals_all via the s9 signal module, then simulate at S1 baseline returns a SimulationResult with `num_closed_trades_total > 0`, `oos_simulation_intentionally_omitted = True`, `last_signal_date_processed <= "2022-12-30"`, and no TradeRecord field date in OOS / post-OOS.
- V10. Negative-path tests: simulate raises SimulatorInputError on bad input; raises SimulatorOosBlockedError if a synthetic SignalEvent with an OOS date is injected; raises SimulatorParameterOverrideError on unknown kwargs.

**T-tests the P8 build turn shall implement (renames forbidden):**

- T1: simulate returns SimulationResult with the expected schema; the four cost tiers all produce different num_closed_trades_total counts OR identical counts but different net_pnl_dollars per TradeRecord (cost-tier sensitivity smoke test).
- T2: every TradeRecord.entry_trigger_date, entry_fill_date, exit_trigger_date, exit_fill_date is in IN_SAMPLE_WINDOW.
- T3: every DailyEquityPoint.date is in IN_SAMPLE_WINDOW.
- T4: first_signal_date_processed == "2014-01-06" (matches the signal module's first_signal_eligible_date for the ETF-proxy dataset).
- T5: ExitReason invariants: every TradeRecord.exit_reason is one of `RSI_EXIT_TRIGGER`, `K4_FORCED_PARK`, `IN_SAMPLE_END_FLAT`. None is `DONCHIAN_20_EXIT`, `STOP_HIT`, `TIME_STOP`, etc.
- T6: SimulatorInputError on non-Mapping loaded input.
- T7: SimulatorInputError on non-Mapping signals input (and on a Mapping with wrong keys).
- T8: SimulatorOosBlockedError on a synthetic SignalEvent injected with date 2023-06-15.
- T9: SimulatorParameterOverrideError on unknown kwarg `enable_short=True`, `window=("2024-01-01","2025-12-31")`, `borrow_cost_bps=25`.
- T10: TradeRecord / DailyEquityPoint / SimulationResult dataclasses have NO field suggestive of forbidden computation: no `sharpe`, `sortino`, `calmar`, `expectancy`, `win_rate`, `correlation`, `covariance`, `pairwise_dependence`, `effective_independent_bets`, `Donchian`, `ATR`, `pyramid`, `unit_index`, `stop_price`, `stop_distance`, `entry_short`, `exit_short`, `short_position`, `borrow`, `daily_return`, `log_return`, `pct_return`, `return_series`. (The fields `entry_slippage_dollars`, `exit_slippage_dollars`, `commission_dollars`, `gross_pnl_dollars`, `net_pnl_dollars` ARE present; T10 confirms these and the absence of the forbidden ones.)
- T11: determinism: simulate(loaded, signals, CostTier.S1) twice produces field-equal SimulationResults.
- T12: simulator performs no file IO at import (patched open / Path.read_bytes).
- T13: static grep of simulator.py for the section 18 forbidden token list returns 0 hits outside FORBIDDEN_TOKEN_EXCLUSION lines.
- T14: static grep of simulator.py for forbidden imports returns 0 hits.
- T15: public API surface equals exactly the section 7 list.
- T16: calling simulate imports no forbidden vendor/network module as a side effect (snapshot sys.modules before/after).

**Build-script safety guardrails:**

- The script shall not write to any path outside section 4 + section 5 temp paths.
- The script shall not import any forbidden vendor / brokerage / production package.
- The script shall not set any environment variable beginning with `DATABENTO_`.
- The script shall not disable SSL verification.
- The script shall log build steps to stdout.
- The script shall self-delete on success.
- The build orchestrator's V6 grep shall accept inline FORBIDDEN_TOKEN_EXCLUSION markers (line + next 2 lines), mirroring the Step 07 aggregator-build pattern.

**Build report schema (sparta.s9.rsi2.simulator_build_report.v1):**

- `schema`, `phase`, `controller_session`, `report_date_utc`.
- `plan_anchor` (this simulator spec), `tier_n_anchor`, `signal_spec_anchor`, `signal_build_anchor` (the P6 build), `selection_plan_anchor`, `predecessor_park_anchor`.
- `output_files` (path -> sha256 + bytes).
- `simulator_api_surface_observed`.
- `v_gate_results` (V1..V10).
- `t_test_results` (T1..T16).
- `forbidden_token_grep_results`, `forbidden_import_grep_results`.
- `cost_baseline_commentary` (the locked $0 commission baseline, the 1c/1c slippage baseline, the per-tier scalar table).
- `live_run_summary_per_tier` (the four S0/S1/S2/S3 SimulationResult summaries: num_closed_trades_total, final_cash_balance, max_drawdown_pct_observed, k4_fired, k4_fired_date).
- `boundaries_held`, `negative_invariants`.
- `api_key_safety_confirmation`.
- `oos_protection_attestation`.
- `live_action_blocking_attestation`.
- `companion_md_sha256`, `seal_method`, `report_seal_sha256`.

## 19. Test corpus T1-T16 summary (cross-reference; renames forbidden)

| T | Concern | Pass criterion |
|---|---|---|
| T1 | Schema + tier-sensitivity smoke | Four S0/S1/S2/S3 SimulationResults; difference observed |
| T2 | IS-only TradeRecord date invariants | All four dates per record in IN_SAMPLE_WINDOW |
| T3 | IS-only DailyEquityPoint date invariants | Every point's date in IN_SAMPLE_WINDOW |
| T4 | First-signal-date alignment | first_signal_date_processed == "2014-01-06" |
| T5 | ExitReason invariant | Every record's exit_reason in the three locked values |
| T6 | Input refusal (loaded) | SimulatorInputError on non-Mapping |
| T7 | Input refusal (signals) | SimulatorInputError on bad shape |
| T8 | OOS injection refusal | SimulatorOosBlockedError on synthetic OOS SignalEvent |
| T9 | Parameter-override refusal | SimulatorParameterOverrideError on unknown kwargs |
| T10 | Dataclass field-name structural invariants | No forbidden field present; expected fields present |
| T11 | Determinism | Two simulate() calls produce field-equal results |
| T12 | No file IO at import | Patched builtins sandbox shows zero opens |
| T13 | Forbidden-token grep | Zero hits outside FORBIDDEN_TOKEN_EXCLUSION |
| T14 | Forbidden-import grep | Zero hits |
| T15 | Public API surface | __all__ matches exactly |
| T16 | No side-effect imports of forbidden modules | sys.modules snapshot before/after equals expected delta |

## 20. Build acceptance checklist + what build is NOT allowed to do + next authorization required

**Build acceptance checklist (the future P8 build turn must satisfy):**

- A separate operator authorization explicitly authorizes the s9 simulator-module build.
- The plan path is exactly `docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md`.
- The Tier-N spec at `docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md` is byte-unchanged at sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409.
- The signal-module spec at `docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md` is byte-unchanged at sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9.
- The s9 P6 signal module's signal.py is byte-unchanged at sha256 8776e87b3482c7f5989bd5832a1e96b12bba3b9186432483759095f30b714f1d.
- The Step 03 s7 D1 loader.py is byte-unchanged at sha256 e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9.
- The four CSVs and audit_manifest.json are byte-unchanged.
- Output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture.
- The pre-stage git index is empty (contamination cleanup if needed).
- The staged file count is exactly 7 at commit time.

**What the P8 build is NOT allowed to do:**

- Compute any signal for any OOS or post-OOS bar.
- Compute any RSI value for any bar (the signal module is upstream; the simulator does not recompute RSI).
- Use any RSI lookback other than 2.
- Use any entry threshold other than 10.0 or exit threshold other than 50.0.
- Use any series for execution other than `loaded.open` (entry / exit fills) and `loaded.close` (mark-to-market).
- Add a short-side execution path to any function.
- Add a pyramid step (`MAX_UNITS_PER_SYMBOL` is locked at 1).
- Add a hard stop, time stop, trailing stop, profit target, or partial exit.
- Add a filter, regime gate, or asset-selection rule.
- Run a backtest, OOS simulation, paper-trade loop, or live order.
- Make any brokerage call, broker session, scheduler call, production-signal write.
- Modify any of the four canonical CSVs, fetch_run_manifest, audit_manifest, s7 D1 loader, validator, signal, simulator, aggregator, spec, plan, park report, lesson file, Tier-N spec, signal-spec, or this simulator spec.
- Modify any ORB artifact, Step 30 cost constant, review_queue, idea_memory, Strategy Lab artifact.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento. Access DATABENTO_API_KEY.
- Disable SSL certificate verification.
- Treat any downstream s9 phase (aggregator, IS diagnostic, OOS, live trading) as pre-authorized.

**Next authorization required:**

A future operator authorization is required to proceed beyond this simulator-module spec. That authorization shall reference this plan by exact path:

`docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s9 simulator-module build only"** (P8; the natural next step; writes the seven output files and runs T1-T16).
- **"Authorize s9 simulator-module spec revision only"** (if this plan needs revision, e.g., adjust allocation fraction, add a hard stop, enable short side).
- **"Authorize s9 aggregator-reuse decision plan only"** (P9; if the operator wants to formally decide aggregator reuse before the simulator build; this would be unusual ordering but is permitted).

This simulator-module spec is the source of truth for the s9 simulator. The build phase inherits the lock byte-equivalent; departing from any locked value requires a fresh `_revN_` spec under separate authorization.

No phase of this chain confers any standing authorization for OOS inspection, Strategy Lab promotion, brokerage connection, or live trading. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

## 21. Validation gates for this plan + HALT conditions + NO-ACTION attestations

V-gates the plan-authoring turn satisfies:

- V1. ASCII-only.
- V2. Numbered sections in monotonic order (1..21).
- V3. No execution language.
- V4. No self-authorization (this plan does NOT authorize any onward phase; each requires its own operator turn).
- V5. No code modification.
- V6. No simulator build, no simulator run.
- V7. No RSI computation.
- V8. No signal computation.
- V9. No backtest.
- V10. No data fetch.
- V11. No network IO.
- V12. No live trading.
- V13. The committed plan file is the ONLY file changed in this turn's commit.
- V14. The pre-stage git index is empty.
- V15. The staged file count is exactly 1 at commit time.

HALT conditions:

- H1. If any V-gate fails, the plan-authoring turn HALTs.
- H2. If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the plan.
- H3. If the staged file count is anything other than 1 at commit time, the turn HALTs and remediates.
- H4. If the integrity of any reference report (Tier-N spec, signal-spec, P6 build report, selection plan, park report, audit, loader build, validator build) shows sha mismatch against the values cited in this plan, the turn HALTs and surfaces the drift.

NO-ACTION attestations:

- This plan does NOT compute RSI (no RSI value is computed).
- This plan does NOT compute any signal.
- This plan does NOT run a simulator.
- This plan does NOT compute any PnL.
- This plan does NOT compute any return.
- This plan does NOT compute any commission or slippage cost.
- This plan does NOT run a backtest.
- This plan does NOT fetch data.
- This plan does NOT call yfinance, Yahoo Finance, Databento, or any vendor.
- This plan does NOT access DATABENTO_API_KEY.
- This plan does NOT inspect OOS.
- This plan does NOT touch live trading, brokerage, review_queue, idea_memory, Strategy Lab, ORB artifacts, or Step 30 cost constants.
- This plan does NOT modify s7 D1 artifacts.
- This plan does NOT modify s9 Tier-N or signal-spec or signal-module.
- This plan does NOT authorize the s9 P8 build phase; that requires fresh operator authorization.

----

End of plan. Simulator-module specification authoring only. No code. No RSI computation. No signal computation. No simulator run. No backtest. No PnL computation. No commission or slippage computation. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No s7 D1 artifact modification. No Tier-N spec modification. No signal-spec modification. No signal-module modification. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
