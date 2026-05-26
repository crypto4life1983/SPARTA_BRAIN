# s7 D1 Cross-Asset Yfinance Proxy Signal Module

Pure deterministic in-memory channel-breakout trigger detector over
LoadedSymbol structures returned by the Step 03 canonical loader.
Built under the Step 05 signal-computation specification plan.

## Anchors

- **Spec plan:** `docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md`
  - sha256 `6e039d352af7a7f20c99b1e26173f07539417a7f65b3c458458aa3ca1c8e2ff4`
  - commit `7e76bb785fa9f75b9fa483e26e6b826cde244851`
- **Upstream Step 04 build (validator, verdict PASS):** commit `a2ec179`
  - validator.py sha256 `bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e`
- **Upstream Step 03 build (loader, verdict PASS):** commit `d7b2a0c`
  - loader.py sha256 `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9`
- **Upstream Step 02c audit (verdict PASS):** commit `1b640d1`
  - audit_manifest sha256 pin `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## What this module does

- Takes `LoadedSymbol` (from `load_symbol()`) or `dict[str, LoadedSymbol]`
  (from `load_all()`) as input.
- Computes the four bidirectional channel-breakout trigger flags per
  signal-eligible in-sample bar:
  - `entry_long_triggered  = today_high > entry_channel_high_55`
  - `entry_short_triggered = today_low  < entry_channel_low_55`
  - `exit_long_triggered   = today_low  < exit_channel_low_20`
  - `exit_short_triggered  = today_high > exit_channel_high_20`
- Returns a `SignalResult` (per-symbol) or `CrossSymbolSignalResult`
  (per-portfolio).
- Raises `SignalError` subclass on any structural refusal.

## What this module does NOT do

- No signal generation outside the in-sample window. Every layer of
  the API and the loop refuses out-of-sample and post-out-of-sample
  computation.
- No simulator state, no position tracking, no unit count, no pyramid
  step.
- No Wilder ATR computation, no stop computation, no sizing, no entry
  timing (MOC/ONO), no fill / commission / slippage.
- No PnL, no profit, no daily return, no log return, no cumulative
  return, no sharpe, no sortino, no calmar, no drawdown.
- No pairwise dependence measure (no correlation, no covariance).
- No portfolio-level aggregation.
- No filter, no regime gate, no asset selection, no winner selection,
  no parameter optimization, no alternative lookbacks.
- No file IO. No network IO. No vendor SDK import. No
  `DATABENTO_API_KEY` access. No SSL bypass.
- No Strategy Lab, no review_queue, no idea_memory, no brokerage,
  no paper broker, no scheduler, no autopilot, no FRC gate touched.

## In-sample-only enforcement

Five structural layers refuse out-of-sample work:

1. The public API exposes no `window=` parameter; the caller cannot
   substitute the in-sample window.
2. `IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")` is hardcoded and
   the only window the module computes against.
3. The iteration loop reads dates and skips any bar whose date is
   outside `IN_SAMPLE_WINDOW`. Out-of-sample and post-out-of-sample
   bars are never iterated.
4. After the loop, the module asserts the last signal date is on or
   before `IN_SAMPLE_WINDOW[1]`.
5. A defensive scan refuses any signal whose date falls in
   `_OUT_OF_SAMPLE_WINDOW` or `_POST_OOS_DIAGNOSTIC_WINDOW`, raising
   `SignalOosBlockedError`.

`oos_signal_intentionally_omitted=True` and
`post_oos_signal_intentionally_omitted=True` are permanent attestations
on every `SignalResult` and `CrossSymbolSignalResult`.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import (
    compute_signals, compute_signals_all,
    ENTRY_CHANNEL_LOOKBACK, EXIT_CHANNEL_LOOKBACK,
    IN_SAMPLE_WINDOW,
)

data = load_all()
result = compute_signals_all(data)

print(result.cross_symbol_bars_in_window_equal)
# True

for sym, sr in result.per_symbol.items():
    print(sym, sr.first_signal_eligible_date, "->",
          sr.last_signal_eligible_date,
          "events:", len(sr.signals))
```

## Refusal modes (`SignalError` tree)

| Exception | When raised |
|---|---|
| `SignalInputError` | input is not a LoadedSymbol; symbol not in {SPY,TLT,GLD,USO}; column lengths mismatch; no signal-eligible bar found |
| `SignalOosBlockedError` | last signal date exceeds in-sample end; or any signal date falls in out-of-sample / post-out-of-sample window |
| `SignalParameterOverrideError` | reserved for any future attempt to override the hardcoded lookbacks or window via a side channel |
| `SignalError` (base) | any other unhandled refusal |

There is no `skip_oos=True` path. No `force_full_window` fallback. No
hidden parameter that can change the in-sample window.

## Tests

The test suite at
`tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/test_signal.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal`
performs no `open()` and no `Path.read_bytes()` call. The module does
not read any file at any point. Verified by test T12.

## Downstream phases (NOT in this module)

- **Step 06 simulator** - position state, Wilder ATR, sizing, stops,
  entry timing, fills, commission, slippage. Will be IS-only at first.
- **Step 07 backtest** - per-trade PnL aggregation into portfolio
  statistics.
- **Out-of-sample inspection** - separate plan; blocked until an
  in-sample run produces a verdict that authorizes out-of-sample access
  (per spec section 11).
- **Live trading** - separate plan; remains blocked at six gates.
