# s7 D1 Cross-Asset Yfinance Proxy Simulator

Pure deterministic in-memory Faith System 1 mechanic executor over
the four-symbol ETF-proxy bundle. Built under the Step 06 simulator
specification plan.

## Anchors

- **Spec plan:** `docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md`
  - sha256 `f7581af358c676519d46f1a0bec486c35cf61f0f5f618faf7f000adf6223878b`
  - commit `c964c59ce0d499b7feb24611d5ea2f6c7a840e08`
- **Upstream Step 05 build (signal, verdict PASS):** commit `25d262f`
  - signal.py sha256 `67c88d9aba58ae28f22313a1bbe0d51581aee6b54b0d43dec76d93f743874a89`
- **Upstream Step 04 build (validator, verdict PASS):** commit `a2ec179`
- **Upstream Step 03 build (loader, verdict PASS):** commit `d7b2a0c`
- **Upstream Step 02c audit (verdict PASS):** commit `1b640d1`

## What this module does

- Takes (LoadedSymbol mapping, SignalResult mapping or
  CrossSymbolSignalResult, CostTier, starting_cash) as input.
- Iterates signal events in chronological order across all four
  symbols and applies the Faith mechanic byte-equivalently per spec
  sections 6-10:
  - Entry: open-on-next-bar (ONO) fills; same-symbol opposite-
    direction blocked while units open; pyramid step `+0.5*N`;
    max 4 units per group lifetime.
  - Wilder ATR(20) computed at the triggering bar (not the fill
    bar); used for stop distance and sizing.
  - Sizing: `floor((0.01 * equity) / (N * $/share))` per spec
    section 9; ETF-adapted `$/share = 1.0`.
  - Stop: `2*N` initial, per-unit persistence, no moving; intra-bar
    trigger fills at `stop_price -/+ stop_slippage_per_share`.
  - Exit: Donchian-20 channel break queues ALL same-side units for
    next-open fill.
  - Cost tiers: S0 (0x/0x), S1 (1x/1x baseline), S2 (3x/1.5x),
    S3 (5x/2x). S4 reserved out-of-scope; passing S4 raises.
  - K4 catastrophic park: portfolio MaxDD > 50% flat-marks all open
    units at the triggering bar's close; no new entries thereafter.
  - End-of-IS boundary: any units still open at the last in-sample
    signal date are flat-marked with `IN_SAMPLE_END_FLAT`.
- Returns a `SimulationResult` with the trade ledger
  (`trade_groups`), the daily equity ledger
  (`daily_equity_ledger`), `final_cash_balance`,
  `max_drawdown_pct_observed`, `k4_fired`, and the IS-only
  attestations.

## What this module does NOT do

- No Step 07 aggregation statistics (Sharpe, sortino, calmar,
  expectancy, win rate, pairwise dependence measures, effective
  independent bets) -- deferred.
- No out-of-sample simulation; structural enforcement via
  `_verify_date_is()` on every event, TradeUnit, and DailyEquityPoint.
- No live trading, no paper order, no brokerage, no broker session,
  no scheduler, no autopilot, no FRC gate.
- No data fetch, no network IO, no vendor SDK.
  No `DATABENTO_API_KEY` access.
- No file IO at all.
- No filter, no regime gate, no asset selection, no winner selection.
- No parameter optimization, no search, no sweep.
- No alternative lookbacks (55-bar entry, 20-bar exit, 20-bar ATR are
  hardcoded constants; no public API permits override).
- No `Strategy Lab` promotion. No `review_queue` mutation. No
  `idea_memory` write.
- No tax / margin / leverage modeling beyond the cash-balance equity
  tracking.

## ETF-proxy adaptations (documented; not deviations from Faith)

| Adaptation | Value | Rationale |
|---|---|---|
| `ETF_DOLLAR_PER_SHARE` | 1.0 | Replaces futures `$/pt` multiplier |
| `ETF_TICK_SIZE` | 0.01 | Penny tick for ETFs |
| Commission baseline (S1) | $0.00 per share | Zero-commission ETF broker assumption |
| Slippage baseline (S1) | 1 cent entry / 2 cents stop / 1 cent exit per share | Mirrors spec 1-tick / 2-tick / 1-tick pattern |
| ETF short borrow cost | **0 in baseline (documented adaptation)** | Defer borrow-stress to a later phase |
| Roll handling | None | ETFs do not expire |

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import compute_signals_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator import (
    simulate, CostTier,
)

loaded = load_all()
signals = compute_signals_all(loaded)  # CrossSymbolSignalResult
result = simulate(loaded, signals, cost_tier=CostTier.S1, starting_cash=100000.0)

print(f"net PnL: ${result.final_cash_balance - 100000:.2f}")
print(f"trade groups: {len(result.trade_groups)}")
print(f"max DD: {result.max_drawdown_pct_observed:.2f}%")
print(f"K4 fired: {result.k4_fired}")

for tg in result.trade_groups[:3]:
    print(f"  {tg.symbol} {tg.direction} {tg.group_unit_count} units, "
          f"net=${tg.group_net_pnl_dollars:.2f}, reason={tg.group_close_reason.value}")
```

## Refusal modes (`SimulatorError` tree)

| Exception | When raised |
|---|---|
| `SimulatorInputError` | loaded / signals not Mapping; keys != {SPY,TLT,GLD,USO}; LoadedSymbol or SignalResult structurally invalid; starting_cash non-positive or non-finite |
| `SimulatorOosBlockedError` | any event, TradeUnit, or DailyEquityPoint with date outside IN_SAMPLE_WINDOW; structural enforcement failure |
| `SimulatorParameterOverrideError` | cost_tier not in {S0,S1,S2,S3}; cost_tier value is S4; unexpected kwargs |
| `SimulatorK4FiredError` | reserved class; current implementation uses the `SimulationResult.k4_fired` flag pattern instead of raising |
| `SimulatorError` (base) | any other unhandled refusal |

There is no `skip_oos=True`, no `enable_short=False`, no
`commission_per_share=`, no `lookback=` path.

## Tests

The test suite at
`tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/test_simulator.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator`
performs no `open()` and no `Path.read_bytes()` call. Verified by
test T12 in the Step 06 plan.
