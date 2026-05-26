# s7 D1 Cross-Asset Donchian - Step 06 Simulator Specification Plan

Status: PLAN_ONLY (build not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
BOUNDARY ALERT: This is the SECOND-TIER boundary-crossing phase. Step 05 introduced signal-side code; Step 06 introduces simulator-side code (position state, sizing, stops, costs, trade ledger). It remains IS-only and contains no live-trading, no brokerage, no order code, no out-of-sample simulation, no Step 07 aggregation statistics.
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Parent Step 05 build (signal, verdict PASS): commit 25d262f, build report sha256 65ee1b6a5c7635abc1597479aacf6457a84fdb7036e50b0bcd1d0aa284897d72, seal df0f28fa974868580e882ff364c3331d2feeab54d5d1d10c000e09c29701b4cc
Parent Step 04 build (validator, verdict PASS): commit a2ec179, build report sha256 fbabd75ea7ce1914ece7a7fda8c957c9e22899538321c180e7c37c378feedd27, seal 737a3f54b0a380e1c298a83a9fb8183b0fbdba23b42fa002a2b7fe0d9883ba3f
Parent Step 03 build (loader, verdict PASS): commit d7b2a0c, build report sha256 137dd8534de840762abc9e6e3f9d22ad5314a1e6f2a4ddc783da3e90429c8386, seal 89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c
Step 02c audit (verdict PASS): commit 1b640d1, audit report sha256 a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354, seal 872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f
Naming convention: s7 D1 cross-asset Donchian yfinance proxy (alternate-vendor research track; separate from the Databento futures track).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No simulator implementation. No test implementation. No build report write. No CSV read by claude during plan authoring. No fetch_run_manifest.json modification. No audit_manifest.json modification. No CSV modification. No loader.py modification. No validator.py modification. No signal.py modification. No simulator run. No backtest. No paper-trade loop. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No Strategy Lab promotion. No brokerage connection. No real order. No paper order. No live trading. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No OOS simulation. No OOS signal computation. No OOS inspection. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Define the canonical Python simulator module for the s7 D1 cross-asset Donchian yfinance proxy research track. The simulator consumes (a) LoadedSymbol structures from the Step 03 loader and (b) SignalResult / CrossSymbolSignalResult structures from the Step 05 signal module, applies the Faith System 1 mechanic byte-equivalently per parent spec sections 6-10 (entry, exit, stop, sizing, costs), and produces an in-sample-only trade ledger plus optional daily equity ledger. The simulator does NOT compute portfolio-level performance statistics (Sharpe, sortino, calmar, expectancy, win rate, effective independent bets, pairwise dependence measures) -- those are deferred to Step 07 (aggregation/backtest report). The simulator does NOT run any out-of-sample bar through any logic path. The simulator does NOT execute any live order, paper order, or brokerage call.

The simulator is a deterministic function from (loaded, signals, cost_tier, starting_cash) to a SimulationResult dataclass. It models the mechanical execution layer: applying the four bidirectional trigger flags from Step 05 to per-symbol position state, sizing each unit at 1% per-unit dollar risk over N (Wilder ATR(20) of the entry market at the triggering bar), placing the initial stop at 2N, layering pyramid units at +0.5N steps up to four units per market, exiting all units on the same side when the Donchian-20 channel breaks the other way (open-on-next-bar), and handling intra-bar stop hits at stop price plus slippage. The simulator records per-trade-unit and per-trade-group ledger rows; it does not aggregate them into statistics.

## 2. Why Step 06 comes after Step 05 (and the second-tier boundary-crossing nature)

Step 05 sealed the signal module (verdict PASS at commit 25d262f). The signal module returns SignalEvent tuples per signal-eligible in-sample bar, with the four bidirectional Donchian-55 entry and Donchian-20 exit trigger flags. With signals computable, the next logical phase is the simulator that consumes those signals and executes them under the Faith mechanic.

Step 06 is the second-tier boundary-crossing phase. Step 05 introduced channel computation; Step 06 introduces every remaining piece of the trading-mechanic vocabulary that Step 05 deliberately deferred: Wilder ATR(20), position state, position sizing, stops, pyramid units, fills, commission, slippage, per-trade PnL, trade ledger, optional daily equity curve, and the K4 catastrophic-drawdown safety park. Each of those was forbidden in the Step 05 signal module by explicit token grep. The Step 06 plan unblocks them STRUCTURALLY (the simulator IS sizing-and-state logic) while keeping a different list of tokens forbidden: Step 07 aggregation statistics (Sharpe, sortino, calmar, expectancy, win rate, pairwise dependence measures, effective independent bets), every live-trading and brokerage token, every parameter-optimization or filter or regime-gate or asset-selection token, and every out-of-sample-simulation token.

The signal module's IS-only enforcement is inherited TRANSITIVELY: the simulator consumes the signal module's output, and the signal module structurally refuses to produce any OOS signal event. Therefore the simulator structurally cannot simulate any OOS bar (no signal exists for that bar). The simulator additionally enforces IS-only via direct date-window checks on every trade event it records (entry_date, exit_date, last_equity_date all in IN_SAMPLE_WINDOW), with HALT on any violation.

The build turn for Step 06 is the first turn whose code consumes signal output and produces trade-execution artifacts. Like Step 05, every operator authorization beyond Step 06 (Step 07 aggregation, OOS phases, live-trading-adjacent phases) requires its own explicit fresh operator approval; this plan does not pre-authorize any of those.

## 3. Inputs from prior phases

The simulator depends on the public API surfaces of the Step 03 loader, Step 04 validator, and Step 05 signal module. The simulator does not read CSV bytes directly. The simulator does not call the loader, validator, or signal module itself; the caller is responsible for calling those modules in order and passing the results.

Locked input contract:

- `loaded: Mapping[str, LoadedSymbol]` (from `load_all()`); keys must equal {"SPY","TLT","GLD","USO"}; each value an immutable LoadedSymbol with tuple-typed `dates`, `open`, `high`, `low`, `close`, `adj_close`, `volume`, plus `symbol`, `csv_path`, `csv_sha256`.
- `signals: Mapping[str, SignalResult]` (from `compute_signals_all()`); keys must equal the same four; each value an immutable SignalResult with `signals: tuple[SignalEvent, ...]`, IS-window pin, and `oos_signal_intentionally_omitted = True`.
- `cost_tier: CostTier` enum value (S0, S1, S2, S3); S1 is the baseline; S4 is OUT OF SCOPE for Step 06 (per parent spec section 10, S4 is reserved tail stress reported by Step 07 only, not a simulation pass-band tier).
- `starting_cash: float` (default 100000.0; per parent spec section 9 MNQ-equivalent starting cash; the build script shall reject negative or non-finite values).

The simulator MUST NOT accept any other public parameter (no `lookback=`, no `window=`, no `enable_short=False`, no `borrow_cost_bps=`, no `commission_per_share=` -- all such are forbidden parameter overrides). Cost-tier scaling is the only authorized parameterization, and only across the four locked tiers S0-S3.

## 4. Outputs the future build turn will create

The build turn for Step 06 shall create the following artifacts and no others:

- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/simulator.py
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/__init__.py (re-exports the public API in section 7).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/README.md
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/test_simulator.py
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/__init__.py (test package marker; may be empty)
- reports/s7_d1_cross_asset_donchian_step_06_simulator_build_report.json (sealed)
- reports/s7_d1_cross_asset_donchian_step_06_simulator_build_report.md (companion human-readable)

No other files. No log files. No data files. No supplementary modules.

## 5. Files the build turn may create or modify later

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested: scripts/_s7_d1_donchian_step_06_simulator_build.py), written, run once, deleted on success.
- A temporary commit-message file under scripts/ if the build orchestrator needs one (mirroring the Step 05 build-message workaround), deleted on success.

Temp scripts byte-deleted on success; failures leave them pending a separately authorized cleanup turn.

## 6. Files the build turn must not modify

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json.
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json.
- All reports/s7_d1_cross_asset_donchian_step_02b_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_02c_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_03_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_04_*.{json,md}.
- All reports/s7_d1_cross_asset_donchian_step_05_*.{json,md}.
- docs/s7_d1_cross_asset_donchian_spec.md and all docs/s7_d1_cross_asset_donchian_step_02b/02c/03/04/05_*.md.
- This Step 06 plan file.
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/, _validator/, _signal/ contents.
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/, _validator/, _signal/ contents.
- CLAUDE.md, docs/decisions.md, RUNBOOK (if present), pipeline_manifest (if present), .gitignore.
- All ORB branch artifacts.
- All Step 30 cost constants.
- review_queue.json, idea_memory directory, Strategy Lab artifacts.
- The Databento-track runner harness path external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/.

## 7. API surface

The simulator module shall expose exactly the following public API and no other public symbols:

- ENTRY_CHANNEL_LOOKBACK: int = 55 (hardcoded; matches Step 05).
- EXIT_CHANNEL_LOOKBACK: int = 20 (hardcoded; matches Step 05).
- WILDER_ATR_LOOKBACK: int = 20 (hardcoded; per spec sec 6/8/9).
- STOP_DISTANCE_N_MULTIPLE: float = 2.0 (hardcoded; per spec sec 8).
- PYRAMID_STEP_N_MULTIPLE: float = 0.5 (hardcoded; per spec sec 5/6).
- MAX_UNITS_PER_SYMBOL: int = 4 (hardcoded; per spec sec 5/9).
- PER_UNIT_RISK_FRACTION: float = 0.01 (hardcoded; per spec sec 9; the 1.0%-of-equity sizing fraction; note: stop-out loss at 2N stop is 2.0% per unit, which is Faith's locked semantics, not a deviation).
- DEFAULT_STARTING_CASH: float = 100000.0 (per spec sec 9; MNQ-equivalent baseline).
- K4_PORTFOLIO_MAXDD_PCT: float = 50.0 (hardcoded; per spec sec 8 K4 catastrophic stop).
- IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30") (hardcoded; matches Step 05).
- ETF_DOLLAR_PER_SHARE: float = 1.0 (ETF-proxy adaptation: each $1 price change times 1 share equals $1 cash; replaces futures $/pt multiplier for this track).
- ETF_TICK_SIZE: float = 0.01 (ETF-proxy adaptation: penny tick).
- class CostTier(Enum) - values S0, S1, S2, S3 only (matches spec sec 10; S4 reserved per spec is OUT OF SCOPE for this simulator; loading an S4 value raises SimulatorParameterOverrideError).
- class ExitReason(Enum) - values DONCHIAN_20_EXIT, STOP_HIT, K4_FORCED_PARK, IN_SAMPLE_END_FLAT (the last reflects the IS-window boundary at which any still-open unit is logged as remaining-open-at-end-of-IS; the simulator does NOT carry positions into OOS).
- class SimulatorError(Exception) - base class for every refusal mode.
- class SimulatorInputError(SimulatorError)
- class SimulatorOosBlockedError(SimulatorError)
- class SimulatorParameterOverrideError(SimulatorError)
- class SimulatorK4FiredError(SimulatorError) - NOT a refusal; raised at end of run if K4 fires, after the simulation has completed and logged. (Alternative pattern: K4 is recorded as a flag on SimulationResult; either is acceptable, but the plan requires the flag pattern to keep K4 a structural data point rather than an exception.)
- @dataclass(frozen=True) class TradeUnit (schema in section 8).
- @dataclass(frozen=True) class TradeGroup (schema in section 8).
- @dataclass(frozen=True) class DailyEquityPoint (schema in section 17).
- @dataclass(frozen=True) class SimulationResult (schema in section 8).
- def simulate(loaded: Mapping, signals: Mapping, cost_tier: CostTier = CostTier.S1, starting_cash: float = DEFAULT_STARTING_CASH) -> SimulationResult - the single entry point.

No other public function. No public mutable state. No module-level data load at import time. No public function that accepts a `lookback=`, `window=`, `enable_short=`, `commission_per_share=`, `slippage_ticks=`, `borrow_cost_bps=`, or any other parameter outside the four pinned constants and the two API arguments (cost_tier and starting_cash).

## 8. Position state model and trade ledger schema

The simulator maintains the following stateful structures during a single `simulate()` call. None of this state is module-level; it is local to the call so that the function remains pure (same input -> same output).

Per-symbol open-position state (one instance per symbol while units are open):

- direction: "long" or "short" or None (None if flat).
- n_entry_at_first_unit: float (the Wilder ATR(20) value at the triggering bar of unit 1; reused for units 2-4 per spec sec 9).
- unit_entries: list of (date, fill_price, shares, stop_price) tuples (length up to MAX_UNITS_PER_SYMBOL).
- next_pyramid_trigger_price: float (entry_price_unit_k + 0.5 * n_entry_at_first_unit for long; minus for short).
- open_unit_count: int (length of unit_entries).

Per-portfolio state:

- cash_balance: float (mark-to-market is realized only at exit; intraday open units add no cash balance, they consume cash at entry equal to shares * fill_price and free it at exit equal to shares * exit_price net of costs).
- portfolio_equity_high_water_mark: float (for K4 drawdown tracking).
- max_drawdown_pct_observed: float (peak-to-trough during the run).
- k4_fired: bool (set True if max_drawdown_pct_observed > K4_PORTFOLIO_MAXDD_PCT; simulation continues to log remaining bars as IN_SAMPLE_END_FLAT but no new entries permitted).
- trade_groups_closed: list of TradeGroup.

TradeUnit (immutable dataclass; one row per pyramid unit):

- symbol: str
- trade_group_id: str (unique per long/short trade-group cycle on this symbol)
- unit_index: int (0-3; 0 is the first unit)
- entry_trigger_date: str (the bar on which the Donchian-55 breakout fired)
- entry_fill_date: str (the next bar's date; ONO timing per spec sec 6)
- entry_fill_price: float (next bar's open + entry slippage)
- entry_slippage_dollars: float
- n_entry_dollars: float (Wilder ATR(20) at trigger bar; same value reused across all units in the trade group per spec sec 9)
- shares: int (per spec sec 9 sizing formula; ETF adaptation per section 13 below)
- stop_price_at_entry: float (entry_fill_price -/+ 2 * n_entry_dollars per spec sec 8)
- exit_date: str
- exit_fill_price: float
- exit_slippage_dollars: float
- exit_reason: ExitReason
- commission_dollars: float (per-RT commission applied at exit; ETF adaptation per section 14)
- gross_pnl_dollars: float (shares * (exit_fill_price - entry_fill_price) for long; negate for short; signed dollar amount before costs)
- net_pnl_dollars: float (gross_pnl - entry_slippage_dollars - exit_slippage_dollars - commission_dollars)

TradeGroup (immutable dataclass; one row per long/short cycle per symbol):

- symbol: str
- trade_group_id: str
- direction: str ("long" or "short")
- n_entry_dollars: float (the n_entry_dollars shared across all units in this group)
- trigger_date_unit_0: str (the date of the first unit's Donchian-55 trigger)
- units: tuple of TradeUnit (length 1 to MAX_UNITS_PER_SYMBOL)
- group_open_date: str (== trigger_date_unit_0)
- group_close_date: str (the latest exit_date across all units)
- group_gross_pnl_dollars: float (sum across units)
- group_net_pnl_dollars: float (sum across units)
- group_unit_count: int (length of units)
- group_close_reason: ExitReason (the reason the LAST unit closed; for Donchian-20-exit groups this is DONCHIAN_20_EXIT; for stop-hit-only groups STOP_HIT; for the special end-of-IS case IN_SAMPLE_END_FLAT)

SimulationResult (immutable dataclass; the function return value):

- starting_cash: float (echo of input)
- final_cash_balance: float (cash at end of IS)
- cost_tier: str (enum name)
- cost_tier_slippage_scalar: float
- cost_tier_commission_scalar: float
- trade_groups: tuple of TradeGroup (chronological)
- trade_groups_per_symbol: Mapping[str, int]
- num_closed_units_total: int
- num_closed_units_per_symbol: Mapping[str, int]
- daily_equity_ledger: tuple of DailyEquityPoint (optional; only if compute_daily_equity_ledger=True at constants level; default is True since this is IS only)
- max_drawdown_pct_observed: float
- k4_fired: bool
- in_sample_window: tuple = IN_SAMPLE_WINDOW (echo for attestation)
- first_signal_date_processed: str
- last_signal_date_processed: str
- oos_simulation_intentionally_omitted: bool (always True; permanent attestation)
- post_oos_simulation_intentionally_omitted: bool (always True; permanent attestation)

## 9. Entry handling (per spec section 6, byte-equivalent)

Entry sequencing per spec section 6, adapted for ETF shares:

1. The simulator iterates SignalEvents in chronological order across symbols. For each SignalEvent on symbol S with date D:
2. If the per-symbol direction is None (flat) AND `entry_long_triggered` is True AND the global per-symbol open-unit-count for S is 0: queue an ENTRY_PENDING LONG for the NEXT BAR's open on S.
3. Else if the per-symbol direction is None AND `entry_short_triggered` is True AND the open-unit-count for S is 0: queue an ENTRY_PENDING SHORT for the next bar's open on S.
4. Else if the per-symbol direction is "long" AND `entry_long_triggered` is True AND the open-unit-count for S is < MAX_UNITS_PER_SYMBOL AND the price has moved through `next_pyramid_trigger_price` (i.e., today's high >= next_pyramid_trigger_price for long): queue a pyramid LONG unit at next bar's open.
5. Else if the per-symbol direction is "short" AND `entry_short_triggered` is True AND open-unit-count < MAX_UNITS_PER_SYMBOL AND today's low <= next_pyramid_trigger_price for short: queue a pyramid SHORT unit at next bar's open.
6. Otherwise no entry is queued for this bar.
7. SAME-SYMBOL OPPOSITE-DIRECTION BLOCK (per spec section 6 step 7): if direction is "long" and `entry_short_triggered` fires, no short entry is queued. The opposite-direction trigger is ignored until the long group fully exits.
8. ONO TIMING (per spec section 5/6): at the NEXT bar's open on symbol S, the simulator fills the queued entry at `next_bar_open + entry_slippage_dollars_per_share` (for long; minus for short). The slippage is applied per share.
9. On fill of the FIRST unit in a group: compute `n_entry_at_first_unit = WilderATR(20)` at the TRIGGERING bar (not the fill bar; per spec section 6 step 4). Compute stop_price = fill_price - 2 * n_entry for long (plus for short). Compute next_pyramid_trigger_price = fill_price + 0.5 * n_entry for long (minus for short). Compute shares per the section 13 sizing formula using the equity at the time of entry.
10. On fill of pyramid units 2-4: reuse the SAME `n_entry_at_first_unit`. Recompute next_pyramid_trigger_price relative to THIS unit's fill_price. Each unit has its own stop_price = THIS unit's fill_price -/+ 2*n_entry.
11. If sizing yields shares < 1 (per spec section 9 minimum size rule): the unit is SKIPPED entirely; it is NOT partial-filled. The skip is logged in the simulator's `entry_skip_log` field (a list on SimulationResult).
12. If `WilderATR(20)` cannot be computed at the triggering bar (insufficient prior bars; should not occur for IS bars since the validator confirmed 55+ warmup, and 20 < 55): the unit is SKIPPED (per spec section 9 sizing-under-data-outage rule).
13. If the K4 catastrophic stop has already fired earlier in the run: no new entries are queued for any symbol. Existing open units continue to be exit-evaluated.

## 10. Exit handling (per spec section 7, byte-equivalent)

Exit sequencing per spec section 7:

1. At each per-symbol RTH session close (i.e., each SignalEvent), evaluate the Donchian-20 exit trigger for every open unit on that symbol. (Per spec, the trigger is a SAME side trigger: long units exit on `exit_long_triggered`; short units exit on `exit_short_triggered`.)
2. If `exit_long_triggered` is True AND direction is "long" with units open: queue an EXIT_PENDING for ALL open units on the long side. The exits fill at the NEXT bar's open at `next_bar_open - exit_slippage_dollars_per_share` (adverse exit slippage).
3. If `exit_short_triggered` is True AND direction is "short" with units open: queue EXIT_PENDING for all open units on the short side. Fills at next bar's open + exit_slippage_dollars_per_share.
4. On all-unit exit: the TradeGroup is closed with `group_close_reason = DONCHIAN_20_EXIT`. The direction resets to None. The next entry (on this symbol) may go either long or short per section 9.
5. STOP HIT INTRA-BAR (per spec section 8): for each open unit, if the bar's low <= stop_price (for long) OR the bar's high >= stop_price (for short), that UNIT EXITS at stop_price -/+ stop slippage. The stop is applied INTRA-BAR (immediate), not at the next bar's open. Other open units in the same group are UNAFFECTED.
6. STOP AND EXIT-CHANNEL SAME DAY (per spec section 8 disambiguation): if both fire on the same bar:
   a. If the stop is intra-bar AND the exit-channel is at-close: the stop fires first (intra-bar wins). The unit exits at stop_price. If other units remain after the stop, the exit-channel still fires for them at next bar's open.
   b. If both are at-close (rare; would require the close to satisfy both conditions): exit-channel exits at next bar's open per spec; stop exits at intra-bar trigger which by definition fires at-close in this case.
   The simulator records the WINNING reason on TradeUnit.exit_reason.
7. NO TIME STOP, NO PROFIT TARGET, NO TRAILING ABOVE DONCHIAN-20 (per spec section 7 step 4): the only exit triggers are the Donchian-20 channel break and the 2N stop.
8. END OF IN-SAMPLE BOUNDARY: at the LAST SignalEvent's date (which is on or before IN_SAMPLE_WINDOW[1] per spec sec 11 and Step 05 sec 11), if any units remain open they are FLAT-MARKED with `exit_reason = IN_SAMPLE_END_FLAT`, `exit_date = last_signal_event.date`, `exit_fill_price = last_signal_event.today_close`, `exit_slippage_dollars = 0` (no execution at IS boundary; positional flat). Their TradeGroup is closed with `group_close_reason = IN_SAMPLE_END_FLAT`. The simulator does NOT carry positions into OOS bars.
9. K4 CATASTROPHIC STOP (per spec sec 8): when `max_drawdown_pct_observed > K4_PORTFOLIO_MAXDD_PCT`, the simulator sets `k4_fired = True`. At the end of the K4-triggering bar, ALL remaining open units are flat-marked with `exit_reason = K4_FORCED_PARK`, `exit_fill_price = bar's close`, `exit_slippage_dollars = 0`. No new entries are queued for the rest of the IS window. The simulation continues to iterate to the last IS bar but enters nothing.

## 11. Stop logic (per spec section 8, byte-equivalent)

- Initial stop distance per unit: STOP_DISTANCE_N_MULTIPLE (= 2.0) * n_entry_at_first_unit (in dollars per share for ETFs).
- Stop direction: below entry for long; above entry for short.
- Per-unit stop persistence: each unit's stop_price is locked at unit entry time. It does NOT trail. It does NOT move with the Donchian channel. It does NOT move on subsequent pyramid entries (units 2-4 have their own per-unit stops at their own 2*n_entry distance from their own entry; the first unit's stop is not adjusted when unit 2 is added).
- Stop hit handling: intra-bar low <= stop_price for long (or high >= stop_price for short) triggers immediate exit AT stop_price. Apply stop slippage (section 14): `exit_fill_price = stop_price - stop_slippage_dollars_per_share` for long (adverse); plus for short.
- No moving stop. No trailing stop above the Donchian-20 channel.
- K4 catastrophic chain-level stop (per spec sec 14 K4): MaxDD > 50% triggers K4 -> all open units flat-marked at bar close, no new entries for rest of IS.

## 12. Wilder ATR(20) computation rules (in-sample only)

Per spec sec 6 step 4 + sec 8 + sec 9: N = WilderATR(20) is required for stop distance, pyramid step, and sizing. The simulator computes it inline (no separate ATR module) using the canonical Wilder formula:

- TR_i (True Range at bar i) = max(high[i] - low[i], |high[i] - close[i-1]|, |low[i] - close[i-1]|) for i >= 1. For i == 0, the simulator uses TR_0 = high[0] - low[0] (a documented Wilder convention that affects only the first 20 warmup bars and is washed out by Wilder smoothing).
- ATR_20 at bar i for i < 20: undefined; the simulator returns None (and any entry queued for a bar with undefined ATR is SKIPPED per section 9 step 12).
- ATR_20 at bar 19: simple average of TR_1 through TR_19 (or TR_0 through TR_19 depending on the index convention; pick the spec-compatible one; document the choice in the build report).
- ATR_20 at bar i > 19: Wilder smoothing = ((20 - 1) * ATR_20[i-1] + TR_i) / 20.

The simulator computes N = ATR_20 at the TRIGGERING bar (not the fill bar; per spec sec 6 step 4). The computation iterates ONLY over loaded.high / loaded.low / loaded.close values whose bar index is <= the triggering bar's index. The simulator NEVER reads a bar whose date is in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW for ATR computation, because triggering bars are always in IN_SAMPLE_WINDOW by signal-module enforcement.

The ATR computation is permitted to look back at bars whose date precedes IN_SAMPLE_WINDOW[0] (pure warmup data; for the ETF-proxy dataset, data starts 2014-01-02 and the first signal-eligible bar is index 55 with date 2014-03-24, so ATR(20) computation at bar 55 uses TRs from bars 1-55, all in loaded warmup). The ATR computation MUST NOT look forward to any bar past the triggering bar's index.

## 13. Position sizing rules (per spec section 9, ETF-adapted)

Per spec sec 9:

- Capital basis: portfolio_equity_now = cash_balance + sum over open units of (shares * current_close - (entry_fill_price for long unit) or (entry_fill_price - current_close for short)).
- For per-unit sizing, the simulator uses portfolio_equity_now AT THE TIME OF the unit entry's fill.
- Per spec formula: per-unit contract count = floor((PER_UNIT_RISK_FRACTION * portfolio_equity_now) / (n_entry * dollar_per_unit_movement)).
- ETF ADAPTATION: dollar_per_unit_movement = ETF_DOLLAR_PER_SHARE = 1.0 (each 1.0 dollar change in price times 1 share equals 1.0 dollar change in P&L per share for ETFs). The spec's futures `$/pt` multiplier (NQ $20, GC $100, etc.) is REPLACED by 1.0 for the ETF-proxy track. This is a track-specific adaptation, NOT a deviation from Faith System 1 semantics: Faith says "size each unit so 1N adverse move equals 1% of equity"; for ETFs that gives shares = floor((0.01 * equity) / (n_entry * 1.0)) = floor(0.01 * equity / n_entry).
- Per spec sec 9 minimum: if computed shares < 1, the unit is skipped (no partial fill). Logged to `entry_skip_log`.
- Per spec sec 9 pyramid: units 2-4 reuse `n_entry_at_first_unit` (NOT recomputed at unit-2 entry). Their share counts are computed using portfolio_equity_now AT THEIR OWN entry time (so a pyramiding-up trade has size proportional to the by-then-larger equity), but with the SAME n_entry.
- Per spec sec 9 portfolio cap: at most MAX_UNITS_PER_SYMBOL (= 4) units open per symbol AND at most 4 * 4 = 16 units open across the four-symbol portfolio at any one time. The simulator tracks open units per symbol; the cross-symbol cap is enforced by the per-symbol cap on each of four symbols.
- Starting cash: DEFAULT_STARTING_CASH = 100000.0 (per spec sec 9 MNQ-equivalent baseline; ETF-proxy track uses the same nominal starting figure).
- Sizing under data outage: if Wilder ATR cannot be computed at the triggering bar (section 12), entry is skipped.

## 14. Cost model and cost-stress matrix (per spec section 10, ETF-adapted)

Per spec sec 10, the simulator applies commission and slippage per the cost-tier scalar. The spec's futures dollar amounts are NOT directly applicable to ETFs; the ETF-proxy adaptations:

ETF baseline (S1, 1x) costs and slippage:

- Commission per round trip per unit: COMMISSION_PER_RT_S1_DOLLARS = 0.00 (zero-commission ETF broker assumption; modern Robinhood / IBKR Lite / Schwab default). This is intentionally conservative-low; raising it requires a fresh _revN_ spec. (Operators preferring per-share commission: the canonical adaptation is $0.005 per share, applied at exit; the simulator BASE shall be $0.00 and a future revision may add a per-share rate via a sealed spec change.)
- Slippage per entry per share: SLIPPAGE_ENTRY_DOLLARS_PER_SHARE_S1 = ETF_TICK_SIZE * 1 = 0.01 (one penny tick; mirrors spec's "1 tick entry slippage" pattern for ETFs).
- Slippage per stop-out per share: SLIPPAGE_STOP_DOLLARS_PER_SHARE_S1 = ETF_TICK_SIZE * 2 = 0.02 (two pennies; mirrors spec's "2 tick stop-out" adverse-fill).
- Slippage per Donchian-20 exit per share: SLIPPAGE_EXIT_DOLLARS_PER_SHARE_S1 = ETF_TICK_SIZE * 1 = 0.01 (one penny).
- No funding / overnight charge for long positions (ETFs do not charge financing for cash-funded long positions).
- BORROW COST FOR SHORTS: assumed ZERO in this simulator baseline. This is a documented ETF-proxy ADAPTATION: real-world short ETF borrow costs are nonzero (typically 25-100 bps annualized for SPY/TLT/GLD; can spike higher for USO). The simulator does NOT model borrow cost in Step 06. Step 07 or a separately authorized Step 06b may add borrow-cost modeling under its own plan. Until then, simulator results on short trades are upper-bound estimates that ignore borrow drag.

Cost-tier scalars per spec sec 10:

- S0: slippage scalar = 0.0, commission scalar = 0.0 (diagnostic floor; DR3 fires if survival is S0-only).
- S1: slippage scalar = 1.0, commission scalar = 1.0 (baseline preregistered).
- S2: slippage scalar = 3.0, commission scalar = 1.5 (mild stress).
- S3: slippage scalar = 5.0, commission scalar = 2.0 (realistic adverse).
- S4 (RESERVED): out of scope for this simulator. CostTier(S4) raises SimulatorParameterOverrideError. Spec section 10 reserves S4 as "tail stress reported for analysis only" by Step 07 aggregation, not run by the simulator.

Applied costs per TradeUnit:

- entry_slippage_dollars = shares * SLIPPAGE_ENTRY_DOLLARS_PER_SHARE_S1 * cost_tier.slippage_scalar.
- exit_slippage_dollars (Donchian-20 exit): shares * SLIPPAGE_EXIT_DOLLARS_PER_SHARE_S1 * cost_tier.slippage_scalar.
- exit_slippage_dollars (stop hit): shares * SLIPPAGE_STOP_DOLLARS_PER_SHARE_S1 * cost_tier.slippage_scalar.
- commission_dollars = COMMISSION_PER_RT_S1_DOLLARS * cost_tier.commission_scalar (applied once per unit, at exit; S1 baseline is $0.00 so all tiers result in $0.00 commission unless a future revision raises the base).
- gross_pnl_dollars = shares * (exit_fill_price - entry_fill_price) for long; shares * (entry_fill_price - exit_fill_price) for short.
- net_pnl_dollars = gross_pnl_dollars - entry_slippage_dollars - exit_slippage_dollars - commission_dollars.

The simulator records cost_tier_slippage_scalar and cost_tier_commission_scalar on SimulationResult so that downstream aggregation (Step 07) can attest which tier produced which result.

## 15. Same-bar conflict rules

The spec section 8 stop-and-exit-channel-same-day rule is repeated and extended:

- Stop intra-bar AND Donchian-20 at-close on the same bar: the stop wins for the unit(s) where the stop triggers. Remaining units (if any) still execute the Donchian-20 exit at next bar's open.
- Entry trigger AND exit trigger on the same bar in the same direction: the exit is for an EXISTING position; the entry is for a NEW unit. The exit takes precedence (all open units exit at next bar's open per spec); the entry trigger that fires on the same bar is for the OPPOSITE side (e.g., long exits AND short entry both signaled on the same bar). The opposite-side entry is queued for the next bar's open IF and only IF the existing position has fully exited by then (per spec section 6 step 7 same-symbol-opposite-direction block).
- Pyramid trigger AND stop hit on the same bar: the stop hits the existing unit(s) intra-bar. The pyramid entry trigger (which is evaluated at close) still queues a new unit at next bar's open IF the per-symbol direction is unchanged at that close (i.e., not all units stopped out).
- Two pyramid triggers on the same bar (rare): only ONE pyramid unit is queued per bar per symbol. The trigger fires once; subsequent pyramid layering happens on later bars.

## 16. Trade ledger schema (cross-referenced from section 8)

See section 8 for TradeUnit, TradeGroup, and SimulationResult schemas. The trade ledger consists of:

- The chronological tuple of TradeGroup on SimulationResult.trade_groups.
- Per-group, the chronological tuple of TradeUnit on TradeGroup.units.

Ledger invariants the build turn shall verify:

- Every TradeUnit.entry_trigger_date is in IN_SAMPLE_WINDOW. (Verified by test T02.)
- Every TradeUnit.entry_fill_date is in IN_SAMPLE_WINDOW. (Verified by test T02.)
- Every TradeUnit.exit_date is in IN_SAMPLE_WINDOW (or equals the IS-end flat-mark date). (Verified by test T02.)
- Every TradeGroup.units length is between 1 and MAX_UNITS_PER_SYMBOL inclusive.
- All units within a TradeGroup have the same direction and the same n_entry_dollars.
- TradeUnit.shares >= 1 for every persisted unit (skipped units are NOT persisted to the ledger; they appear in SimulationResult.entry_skip_log instead).
- TradeUnit.gross_pnl_dollars + costs == TradeUnit.net_pnl_dollars (arithmetic sanity).
- TradeGroup.group_gross_pnl_dollars == sum(unit.gross_pnl_dollars for unit in units) and similarly for net.
- SimulationResult.num_closed_units_total == sum(len(g.units) for g in trade_groups).

## 17. Daily equity ledger schema (in-sample only)

The simulator produces a chronological daily equity ledger covering bars from the FIRST signal-eligible date (2014-03-24) through the LAST signal-eligible date (on or before 2022-12-30). The ledger has one DailyEquityPoint per IS bar processed:

DailyEquityPoint (immutable dataclass):

- date: str (IS date)
- cash_balance: float
- open_units_count_total: int
- open_units_per_symbol: Mapping[str, int]
- mark_to_market_equity: float (cash_balance + sum over open units of (shares * (close - entry_fill_price)) for long; negated for short)
- drawdown_pct_from_high_water: float
- k4_armed: bool (True if drawdown_pct_from_high_water > K4_PORTFOLIO_MAXDD_PCT; this triggers K4 enforcement at the bar's close)

The daily equity ledger is OPTIONAL in the sense that the simulator function returns it as a tuple (default included); a future flag could omit it for performance, but the Step 06 build shall always include it for in-sample.

The daily equity ledger contains NO performance statistic (no Sharpe, no sortino, no calmar, no expectancy, no win rate). Those are Step 07 aggregation. The simulator only records the per-day equity time-series; aggregation happens elsewhere.

The daily equity ledger records ONLY in-sample bars. No bar with date in OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW is included. The simulator never advances beyond the last in-sample signal date.

## 18. In-sample-only structural enforcement (inherited and extended)

The signal module (Step 05) structurally produces no OOS signal. The simulator inherits this transitively. In addition, the simulator enforces:

- Every TradeUnit's entry_trigger_date, entry_fill_date, and exit_date is checked against IN_SAMPLE_WINDOW; any violation raises SimulatorOosBlockedError.
- Every DailyEquityPoint's date is checked against IN_SAMPLE_WINDOW; any violation raises SimulatorOosBlockedError.
- The simulator iterates over signal events from compute_signals_all; since those are by Step 05 construction all in IN_SAMPLE_WINDOW, no OOS bar can enter the loop.
- The simulator does NOT have any code path that reads bars from the loader for OOS or post-OOS dates. The Wilder ATR computation (section 12) iterates from bar 0 up to the triggering bar's index; triggering bars are always in IS by signal-module enforcement, so the ATR computation cannot reach an OOS bar's index.
- The simulator does NOT have any code path that simulates a hypothetical OOS scenario. No `simulate_oos` function, no `simulate_full_window` function, no `simulate_post_oos` function.
- The SimulationResult's `oos_simulation_intentionally_omitted` and `post_oos_simulation_intentionally_omitted` fields are permanent attestations (always True).

## 19. Refusal modes and HALT conditions

Refusal modes (the simulator HALTs by raising):

- SimulatorInputError: bad input shape; loaded keys != {SPY,TLT,GLD,USO}; signals keys != same; LoadedSymbol structural invalid; SignalResult structural invalid; cost_tier not in {S0,S1,S2,S3}; starting_cash non-positive or non-finite.
- SimulatorOosBlockedError: any per-event date check fails IN_SAMPLE_WINDOW containment; any DailyEquityPoint date check fails; any internal date drift.
- SimulatorParameterOverrideError: cost_tier value is S4 or any unknown enum; any attempt to pass a `lookback=`, `window=`, `enable_short=`, `commission_per_share=`, etc. parameter via kwargs (function signature strictly does not accept these, but a defensive **kwargs reject is recommended; the build script shall add an explicit `if kwargs: raise SimulatorParameterOverrideError(...)`).
- SimulatorError (base): any other unhandled refusal.

NOT refusal modes (recorded as data, not raised):

- K4 firing: recorded as SimulationResult.k4_fired = True. The simulation completes; remaining bars are still iterated but no new entries are queued.
- Unit skip due to shares < 1: recorded in SimulationResult.entry_skip_log. The simulation continues.
- Unit skip due to ATR-undefined-at-triggering-bar: same.

The simulator shall NOT support:

- any parameter optimization or search (no grid, no random, no bayesian).
- any alternative lookback (no 50, no 60, no 25, no 15).
- any filter (no MA filter, no trend filter, no vol filter, no regime gate, no pairwise dependence gate).
- any asset selection (no top-N pick, no rank gate).
- any winner-selection rule.
- any same-symbol opposite-direction reversal except per spec section 6 step 7 (block until all units exit).
- any time-stop, profit target, or trailing-above-Donchian-20 (per spec sec 7 step 4).
- any tax modeling.
- any margin / leverage modeling beyond the cash-balance equity tracking.

## 20. Forbidden tokens, forbidden imports, ORB isolation, no live trading

Forbidden imports (verified by static grep over simulator.py):

- import yfinance, import databento, import requests, import urllib.*, from urllib *, import http.client, import socket, import curl_cffi, import aiohttp, import httpx, import grpc, import pyarrow.flight.
- import strategy_lab, import sparta_commander, import spartacus, import hydra_video, import app, import sparta_brain.
- import broker, import interactive_brokers, import alpaca, import tradestation, import ibapi, import binance, import oanda, import ib_insync.
- import quantconnect, import lean, import qcalgorithm.

Forbidden tokens (verified by static grep; comment-marker FORBIDDEN_TOKEN_EXCLUSION allowed for documentation):

Vendor / credential / network:

- DATABENTO_API_KEY, yfinance, yahoo_finance, databento, requests.get, urllib.request, socket.connect, http.client, curl_cffi, aiohttp, httpx.

Live trading / brokerage / production integration:

- Strategy Lab (with space), strategy_lab, review_queue, idea_memory.
- live trading (with space), live_trading.
- brokerage, broker_api, broker_session.
- alpaca, interactive_brokers, ibkr, ibapi, ib_insync, tradestation, binance, oanda.
- order_send, place_order, submit_order, cancel_order, modify_order, route_order.
- production_signal.
- paper_broker, paper_trade.
- scheduler, autopilot.
- frc_gate.

Step 07 (aggregation) tokens deferred:

- sharpe, sortino, calmar.
- expectancy, win_rate.
- correlation, covariance, .pct_change(.
- effective_independent_bets, avg_pairwise_correlation.

Parameter optimization tokens forbidden:

- _optimize_, _sweep_, _tune_, _grid_search_, _bayes_search_.
- alternative_lookback, lookback_grid, parameter_grid.
- winner_selection, asset_selection, top_n_pick.

Filter / regime tokens forbidden:

- regime_filter, regime_gate, ma_filter, vol_filter, dependence_filter.
- correlation_filter, beta_filter.

OOS-related tokens forbidden:

- compute_signals_oos, simulate_oos, simulate_full_window, simulate_post_oos.
- oos_simulation (the English term; the SCHEMA FIELD `oos_simulation_intentionally_omitted` is permitted because it is a permanent attestation, not an active operation).

Tokens NEWLY UNBLOCKED in Step 06 (these were forbidden in Step 05 signal module; they are necessary for simulator-side bookkeeping):

- Wilder, WilderATR, wilder_atr, wilder_n. (Needed for N computation per spec sec 6/8/9.)
- ATR( and atr_20. (Needed for sizing input.)
- position_size, position_state, unit_count, pyramid_unit. (Needed for position tracking.)
- stop_distance, stop_price, slippage, commission, fill_price. (Needed for cost model and ledger.)
- order_id and trade_id (the simulator uses trade_group_id; order_id is not a brokerage order id, it is an internal queue id; still permitted as a local variable name).
- pnl, profit, gross_pnl, net_pnl, daily_pnl. (Needed for ledger.)
- equity, portfolio_equity, cash_balance, mark_to_market. (Needed for sizing capital basis and daily equity ledger.)
- drawdown, max_drawdown, max_drawdown_pct. (Needed for K4 enforcement.)

ORB isolation: the simulator shall NOT read or modify any ORB branch artifact; shall NOT modify any Step 30 cost constant.

The build report shall include an api_key_safety_confirmation block attesting:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_imported_by_simulator: false
- yahoo_finance_called_by_simulator: false
- any_network_call_by_simulator: false
- any_file_io_by_simulator: false
- any_brokerage_call_by_simulator: false
- any_strategy_lab_call_by_simulator: false
- any_review_queue_mutation_by_simulator: false

## 21. V-gates V1-V10, tests T1-T16, build-script safety, build report schema, what build is NOT allowed to do, next authorization

V-gates the build turn shall verify in order:

V1. The seven output files in section 4 exist at the locked paths.
V2. The simulator module is syntactically valid Python (AST compiles).
V3. The simulator module imports cleanly without performing any file IO at import time (verified by patched-open sandbox).
V4. The public API surface (section 7) matches exactly.
V5. The simulator module contains no forbidden import (section 20 list), verified by static grep.
V6. The simulator module contains no forbidden token from the section 20 list, outside designated FORBIDDEN_TOKEN_EXCLUSION comment lines.
V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped. No xfail.
V8. The test suite includes every test T1..T16. Missing or renamed tests HALT.
V9. A live in-sample integration test: load_all then compute_signals_all then simulate at S1 baseline returns a SimulationResult with trade_groups non-empty for at least one symbol, every TradeUnit date in IN_SAMPLE_WINDOW, num_closed_units_total > 0, oos_simulation_intentionally_omitted True, k4_fired recorded.
V10. Negative-path tests: simulate raises SimulatorInputError on bad input; raises SimulatorParameterOverrideError on cost_tier=S4 or unknown enum or extra kwargs; raises SimulatorOosBlockedError if a synthetic SignalEvent with an OOS date is injected.

T-tests (the build turn shall implement; renames forbidden):

- T1: simulator imports loader/validator/signal modules only (no external).
- T2: every TradeUnit entry_trigger_date, entry_fill_date, and exit_date is in IN_SAMPLE_WINDOW; every DailyEquityPoint date is in IN_SAMPLE_WINDOW.
- T3: OOS injection blocked: construct a synthetic SignalEvent with date "2023-06-15" and inject into the signals input; simulate raises SimulatorOosBlockedError.
- T4: no live-trading code path: simulator's `simulate` has no kwargs other than the four pinned ones; no `broker` / `order` / `live` paths.
- T5: no brokerage import (static grep).
- T6: deterministic: simulate(loaded, signals, cost_tier=S1, starting_cash=100000) twice produces field-equal SimulationResult.
- T7: no parameter override: simulate(loaded, signals, cost_tier=CostTier.S1, starting_cash=100000, lookback=50) raises SimulatorParameterOverrideError.
- T8: no Databento/yfinance/network imports.
- T9: no review_queue/Strategy Lab imports.
- T10: same-bar conflict: a synthetic scenario where stop hits intra-bar and Donchian-20 exit-trigger also fires at close on the same bar produces a TradeUnit.exit_reason == STOP_HIT for the stopped unit (intra-bar wins).
- T11: warmup behavior: the first TradeUnit.entry_trigger_date is >= 2014-03-24 (first signal-eligible date); no entry before that.
- T12: commission/slippage behavior: simulate at S0 (zero costs) and at S1 (baseline) produces different net_pnl_dollars for each TradeUnit (S0 has zero entry/exit slippage; S1 has nonzero). Per-tier scalar verification.
- T13: stop behavior: a synthetic scenario forces a stop hit; the resulting TradeUnit.exit_fill_price equals stop_price_at_entry - (shares-irrelevant per-share slippage) for long, validated arithmetically.
- T14: sizing behavior: for a known SPY entry with N_entry = X dollars and equity = Y, shares = floor(0.01 * Y / X) verified.
- T15: pyramid behavior: a synthetic scenario produces 4 units in one TradeGroup; assert all 4 share the same n_entry_dollars; assert unit_index 0..3 in order; assert open_units never exceeds MAX_UNITS_PER_SYMBOL.
- T16: K4 catastrophic test: a synthetic scenario where portfolio max-drawdown exceeds 50% sets SimulationResult.k4_fired = True and remaining open units are flat-marked with exit_reason = K4_FORCED_PARK; no new entries are queued thereafter.

Build-script safety guardrails:

- The script shall not write to any path outside section 4 + section 5 temp paths.
- The script shall not import yfinance, databento, requests, urllib (any submodule), http.client, socket, curl_cffi, aiohttp, httpx, or any forbidden brokerage / production package.
- The script shall not set any environment variable beginning with DATABENTO_.
- The script shall not disable SSL verification.
- The script shall log build steps to stdout for the build report writer.
- The script shall self-delete on success.

Build report schema (sparta.donchian.step_06_simulator_build_report.v1):

- schema, phase, controller_session, report_date_utc.
- plan_anchor, step_05_anchor, step_04_anchor, step_03_anchor, step_02c_anchor.
- output_files (path -> sha256 + bytes).
- simulator_api_surface_observed.
- v_gate_results (V1..V10).
- t_test_results (T1..T16).
- forbidden_token_grep_results (per-token hit counts).
- forbidden_import_grep_results.
- boundaries_held, negative_invariants.
- api_key_safety_confirmation (10 fields per section 20).
- oos_protection_attestation (no_oos_simulation, no_post_oos_simulation, no_oos_value_inspected_by_simulator).
- companion_md_sha256, seal_method, report_seal_sha256.

Build acceptance checklist (the future build turn must satisfy):

- A separate operator authorization explicitly authorizes the Step 06 build.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md.
- The Step 05 signal module and earlier loader/validator are byte-unchanged.
- The four CSVs and audit_manifest.json are byte-unchanged.
- Output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture.
- No co-active Databento path, no co-active Step 07 aggregation path, no co-active OOS simulation, no co-active live-trading path.
- The build writes only the seven output files plus optional temp scripts (each deleted on success).

What the build is NOT allowed to do:

- Compute any Step 07 aggregation statistic (Sharpe, sortino, calmar, expectancy, win rate, effective independent bets, pairwise dependence measure).
- Simulate any bar outside IN_SAMPLE_WINDOW.
- Make any live order, paper order, brokerage call, broker session, or production scheduler call.
- Modify any canonical CSV, manifest, loader, validator, signal, plan, spec, ORB artifact, or Step 30 cost constant.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento. Access DATABENTO_API_KEY.
- Disable SSL certificate verification.
- Promote any candidate to Strategy Lab.
- Mutate review_queue.json or idea_memory.
- Use the phrase "run simulator now" or "execute backtest now" as an active directive (these appear here only as forbidden text).
- Treat the phrase "authorize Step 06 build" as a completed or current action.
- Treat any downstream phase (Step 07 aggregation, OOS phase, live-trading-adjacent phase) as pre-authorized.

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth; the build turn is not pre-authorized by the plan itself. No phase of this chain confers any standing authorization for OOS access, Step 07 aggregation, Strategy Lab promotion, brokerage connection, or live trading; each requires its own explicit fresh operator approval.

Future expected status on the Step 06 build turn (informational; not granted here):

STEP_06_SIMULATOR_BUILT
SIMULATOR_TEST_SUITE_PASSED_T1_TO_T16
SIMULATOR_BUILD_REPORT_SEALED
NO_CSV_MODIFIED
NO_AUDIT_MANIFEST_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_LOADER_MODIFIED
NO_VALIDATOR_MODIFIED
NO_SIGNAL_MODULE_MODIFIED
NO_OOS_SIMULATION
NO_POST_OOS_SIMULATION
NO_STEP_07_AGGREGATION_STATISTIC_COMPUTED
NO_DATA_FETCH
NO_NETWORK_CALL
NO_FILE_IO_BY_SIMULATOR
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_BROKERAGE_CONNECTION
NO_REAL_ORDER
NO_PAPER_ORDER
NO_STRATEGY_LAB_PROMOTION
NO_REVIEW_QUEUE_MUTATION
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- Step 07 aggregation: takes SimulationResult (and the four cost-tier variants S0, S1, S2, S3) and produces the portfolio-level acceptance-gate evaluation per spec section 13 (A1 sample size, A2 Sharpe, A3 expectancy, A4 MaxDD, A5 WR-gap, A6 validator pass, A7 effective independent bets, A8 cost-stress matrix, A9 safety-template inheritance, A10 cap binding events). Step 07 also evaluates DR rules DR2/DR3/DR5. Step 07 requires its own plan and authorization. Step 07 remains IS-only at first; OOS is its own further plan.
- OOS inspection (any form): separate plan beyond Step 07; per spec section 11 `oos_inspection_blocked_at_in_sample` invariant, OOS inspection requires an IS-pass verdict from Step 07 plus an explicit operator authorization. Step 06 does not pre-authorize anything OOS-side.
- Live trading: separate plan beyond all of the above; remains BLOCKED at 6 gates. No phase of this chain confers any standing authorization for live trading.

----

End of plan. Plan-authoring turn only. No simulator code written. No simulator run. No backtest. No OOS simulation. No data fetch. No network. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
