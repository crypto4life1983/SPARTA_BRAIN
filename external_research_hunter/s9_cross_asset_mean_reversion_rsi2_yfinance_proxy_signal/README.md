# s9 Cross-Asset RSI-2 Mean-Reversion Signal Module (ETF-Proxy Track)

Pure deterministic in-memory long-only RSI-2 trigger emitter over
LoadedSymbol structures returned by the Step 03 canonical loader.
Built under the s9 signal-module specification plan (P6).

## Anchors

- **Tier-N spec:** `docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md`
  - sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`
  - commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- **Signal-module spec:** `docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md`
  - sha256 `59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9`
  - commit `c5393ab31a58059004b8cd337cd428eacbcbaece`
- **Reused upstream Step 03 loader (s7 D1 chain):** commit `d7b2a0c`
- **Reused upstream Step 04 validator (s7 D1 chain):** commit `a2ec179`
- **Predecessor parked candidate:** s7 D1 ETF-proxy at REJECT_FAST (commit `a5ac092`)

## What this module does

- Takes `LoadedSymbol` (from `load_symbol()`) or
  `dict[str, LoadedSymbol]` (from `load_all()`) as input.
- Computes Wilder-smoothed RSI(2) on the `adj_close` series for each
  symbol over the in-sample window.
- Emits a long-only trigger pair per signal-eligible IS bar:
  - `entry_long_triggered = (rsi_value < 10.0)`
  - `exit_long_triggered  = (rsi_value > 50.0)`
- Returns `SignalResult` (per symbol) or `CrossSymbolSignalResult`
  (per bundle).
- Raises `SignalError` subclass on any structural refusal.

## What this module does NOT do

- No signal generation outside the in-sample window. Every layer of
  the API and the loop refuses out-of-sample and post-out-of-sample
  computation.
- No short-side fields on any dataclass. The dataclass shape itself
  enforces long-only at the type level.
- No alternative RSI lookback besides 2.
- No alternative entry threshold besides 10.0.
- No alternative exit threshold besides 50.0.
- No alternative series choice besides `adj_close`.
- No position state, no sizing, no stops, no trade ledger, no
  per-trade PnL, no Sharpe, no expectancy, no drawdown.
- No file IO at all. No network IO. No vendor SDK import. No
  `DATABENTO_API_KEY` access. No SSL bypass.
- No Strategy Lab. No `review_queue` mutation. No `idea_memory`
  write. No brokerage. No order. No live trading. No scheduler /
  autopilot / FRC gate touch.
- No parameter optimization, no search, no sweep, no tune.
- No filter, no regime gate, no asset selection, no winner
  selection.

## Five-layer in-sample-only enforcement

L1. No `window=` / `lookback=` / `threshold=` / `series=` /
    `enable_short=` parameter on any public API.
L2. `IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")` hardcoded;
    no override path.
L3. Loop predicate excludes OOS / post-OOS dates from iteration.
L4. Post-loop assertion: last SignalEvent date <=
    `IN_SAMPLE_WINDOW[1]`; raises `SignalOosBlockedError` on
    violation.
L5. Defensive scan: no SignalEvent date in `OUT_OF_SAMPLE_WINDOW`
    (2023-01-01 to 2025-12-30) or `POST_OOS_DIAGNOSTIC_WINDOW`
    (2026-01-02 to 2026-05-22); raises `SignalOosBlockedError`.

Permanent attestations:
`oos_signal_intentionally_omitted = True` and
`post_oos_signal_intentionally_omitted = True` on every
`SignalResult` and `CrossSymbolSignalResult`.

## RSI(2) computation (Wilder smoothing; locked)

```
delta_i = adj_close[i] - adj_close[i-1]  for i >= 1
gain_i  = max(delta_i, 0)
loss_i  = max(-delta_i, 0)

Seed at i == RSI_LOOKBACK == 2:
  avg_gain[2] = (gain_1 + gain_2) / 2
  avg_loss[2] = (loss_1 + loss_2) / 2

Wilder smoothing for i > 2 (RSI_LOOKBACK = 2):
  avg_gain[i] = (avg_gain[i-1] + gain_i) / 2
  avg_loss[i] = (avg_loss[i-1] + loss_i) / 2

rs  = avg_gain / avg_loss
rsi = 100.0 - (100.0 / (1.0 + rs))

Degenerate cases:
  avg_loss == 0 and avg_gain > 0  -> rsi = 100.0  (all gains)
  avg_gain == 0 and avg_loss > 0  -> rsi = 0.0    (all losses)
  avg_loss == 0 and avg_gain == 0 -> rsi = 50.0   (neutral)

No look-ahead: bar i RSI uses only adj_close[0..i].
```

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import (
    compute_signals, compute_signals_all,
    RSI_LOOKBACK, RSI_OVERSOLD_ENTRY_THRESHOLD, RSI_EXIT_THRESHOLD,
    IN_SAMPLE_WINDOW,
)

data = load_all()
result = compute_signals_all(data)

print(result.cross_symbol_bars_in_window_equal)
# True

for sym, sr in result.per_symbol.items():
    n_entry = sum(1 for ev in sr.signals if ev.entry_long_triggered)
    n_exit  = sum(1 for ev in sr.signals if ev.exit_long_triggered)
    print(sym, sr.first_signal_eligible_date, "->",
          sr.last_signal_eligible_date,
          "entries:", n_entry, "exits:", n_exit)
```

## Refusal modes (`SignalError` tree)

| Exception | When raised |
|---|---|
| `SignalInputError` | input is not a LoadedSymbol; symbol not in {SPY,TLT,GLD,USO}; column lengths mismatch; no signal-eligible bar found |
| `SignalOosBlockedError` | last signal date exceeds in-sample end; or any signal date falls in out-of-sample / post-out-of-sample window |
| `SignalParameterOverrideError` | any unknown kwarg passed to `compute_signals` / `compute_signals_all` |
| `SignalError` (base) | any other unhandled refusal |

There is no `skip_oos=True` path. No `force_full_window` fallback.
No hidden parameter that can change the in-sample window.

## Tests

The test suite at
`tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/test_signal.py`
runs T1-T16 under stdlib `unittest`. The build report records
pass status per test.

## Importing performs no file IO

`import external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal`
performs no `open()` and no `Path.read_bytes()` call. The module
does not read any file at any point. Verified by test T12.
