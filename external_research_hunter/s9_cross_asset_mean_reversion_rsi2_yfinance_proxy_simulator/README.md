# s9 Cross-Asset RSI-2 Mean-Reversion Simulator (ETF-Proxy Track)

Pure deterministic in-memory long-only RSI-2 mechanic executor over the
four-ETF universe (SPY / TLT / GLD / USO), in-sample only. Consumes
LoadedSymbol structures from the Step 03 loader and SignalResult /
CrossSymbolSignalResult structures from the s9 P6 signal module. Built
under the s9 simulator-module specification plan (P8).

## Anchors

- **Tier-N spec:** `docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md`
  - sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`
  - commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- **Signal-module spec:** `docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md`
  - sha256 `59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9`
  - commit `c5393ab31a58059004b8cd337cd428eacbcbaece`
- **Simulator-module spec:** `docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md`
  - sha256 `c64bbe7525ad06d5d870b51b6c5b8c9ba45a17675acc5ecc3e2faa4c545f83bf`
  - commit `3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f`
- **Reused upstream Step 03 loader (s7 D1 chain):** commit `d7b2a0c`
- **s9 P6 signal-module build (verdict PASS):** commit `1a055bd`
- **Predecessor parked candidate:** s7 D1 ETF-proxy at REJECT_FAST (commit `a5ac092`)

## What this module does

- Takes `Mapping[str, LoadedSymbol]` (from `load_all()`) and `Mapping[str,
  SignalResult]` or `CrossSymbolSignalResult` (from `compute_signals_all()`)
  as input.
- Applies the long-only RSI-2 mean-reversion entry / exit mechanic per
  the s9 Tier-N spec sections 9-13.
- Entry on `rsi_value < 10` at the next bar's open + cost-tier-scaled
  slippage.
- Exit on `rsi_value > 50` at the next bar's open - cost-tier-scaled
  slippage.
- Sizes each entry at equal-dollar `PER_SIGNAL_ALLOCATION_FRACTION =
  0.01` (= 1%) of portfolio mark-to-market equity at the trigger bar's
  close.
- Tracks cash, mark-to-market equity, high-water mark, max drawdown.
- Enforces K4 catastrophic park rule (drawdown > 50% forces close all
  open records at the K4 day's close; no slippage charged).
- Flat-marks any still-open record at the last in-sample bar's close
  with `exit_reason = IN_SAMPLE_END_FLAT`.
- Records a `DailyEquityPoint` per processed in-sample date.
- Returns a `SimulationResult` (per-call). Raises `SimulatorError`
  subclass on any refusal mode.

## What this module does NOT do

- No simulation of any out-of-sample bar. Every layer of the API and
  the loop refuses out-of-sample and post-out-of-sample dates.
- No alternative RSI lookback besides 2.
- No alternative entry threshold besides 10.0.
- No alternative exit threshold besides 50.0.
- No second concurrent open record on the same symbol
  (`MAX_UNITS_PER_SYMBOL = 1`).
- No hard stop, no time stop, no trailing stop, no profit target, no
  partial exit. The only three legitimate exits are `RSI_EXIT_TRIGGER`,
  `K4_FORCED_PARK`, `IN_SAMPLE_END_FLAT`.
- No short-side execution path. The dataclass shape enforces long-only
  at the type level.
- No borrow cost, no funding cost, no overnight cost (long-only ETF).
- No portfolio-level aggregation statistic (risk-adjusted ratio,
  win-fraction, expectancy, pairwise dependence measure). Those are
  deferred to the future s9 aggregator phase.
- No file IO. No network IO. No vendor SDK import. No
  `DATABENTO_API_KEY` access. No SSL bypass.
- No live trading. No paper order. No broker connection. No scheduler /
  autopilot / FRC gate touch.
- No parameter optimization, no search, no sweep, no tune.
- No filter, no regime gate, no asset selection, no winner selection.

## Five-layer in-sample-only enforcement

L1. No `window=` / `lookback=` / `threshold=` / `enable_short=` /
    `compute_daily_equity_ledger=` / similar parameter on any public
    API. Defensive `**kwargs` raises `SimulatorParameterOverrideError`.
L2. `IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")` hardcoded; no
    override path.
L3. The main loop's `_verify_date_is(...)` HALTs on any non-IS event
    date.
L4. Post-loop assertion: every TradeRecord date and every
    DailyEquityPoint.date is in-sample; last point's date `<=
    IN_SAMPLE_WINDOW[1]`; raises `SimulatorOosBlockedError` on
    violation.
L5. Defensive scan: no TradeRecord field date and no
    DailyEquityPoint.date in `OUT_OF_SAMPLE_WINDOW` (2023-01-01 to
    2025-12-30) or `POST_OOS_DIAGNOSTIC_WINDOW` (2026-01-02 to
    2026-05-22); raises `SimulatorOosBlockedError`.

Permanent attestations on every SimulationResult:
`oos_simulation_intentionally_omitted = True` and
`post_oos_simulation_intentionally_omitted = True`.

## Cost-stress matrix (locked; Tier-N section 13)

| Tier | Slippage scalar | Commission scalar |
|---|---|---|
| S0 | 0.0 | 0.0 |
| S1 (baseline) | 1.0 | 1.0 |
| S2 | 3.0 | 1.5 |
| S3 | 5.0 | 2.0 |

ETF-proxy baselines: $0 per-share commission baseline (zero-commission
ETF broker assumption); $0.01 per-share entry slippage baseline; $0.01
per-share exit slippage baseline. Loading `CostTier.S4` is impossible
because the enum does not include S4; the simulator is `OUT_OF_SCOPE`
for S4 stress per the Tier-N spec.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import compute_signals_all
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator import (
    simulate, CostTier,
)

data = load_all()
sig = compute_signals_all(data)
result = simulate(data, sig, cost_tier=CostTier.S1)

print(result.num_closed_trades_total, "closed records")
print(result.trade_records_per_symbol)
print("max drawdown:", result.max_drawdown_pct_observed, "%")
print("k4 fired:", result.k4_fired)
print("daily equity points:", len(result.daily_equity_ledger))
```

## Refusal modes (`SimulatorError` tree)

| Exception | When raised |
|---|---|
| `SimulatorInputError` | input not a Mapping; symbol keys mismatch; LoadedSymbol / SignalResult shape mismatch; non-positive starting_cash |
| `SimulatorOosBlockedError` | any iterated date in OOS or post-OOS; any TradeRecord field date or DailyEquityPoint.date in OOS or post-OOS |
| `SimulatorParameterOverrideError` | any unknown kwarg passed to `simulate()`; invalid `cost_tier` |
| `SimulatorK4FiredError` | reserved for API completeness; current implementation records K4 via `SimulationResult.k4_fired` flag instead of raising |
| `SimulatorError` (base) | any other unhandled refusal |

There is no `skip_oos=True` path. No `force_full_window` fallback. No
hidden parameter that can change the in-sample window. No parameter
that can enable short-side execution.

## Tests

The test suite at
`tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/test_simulator.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator`
performs no `open()` and no `Path.read_bytes()` call. The module does
not read any file at any point. Verified by test T12.
