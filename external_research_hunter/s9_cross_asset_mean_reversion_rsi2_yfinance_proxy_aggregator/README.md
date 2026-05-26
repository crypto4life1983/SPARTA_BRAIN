# s9 Cross-Asset RSI-2 Mean-Reversion Aggregator (ETF-Proxy Track)

Pure deterministic in-memory aggregator over the four-ETF universe
(SPY / TLT / GLD / USO), in-sample only. Consumes the four cost-tier
`SimulationResult` instances (S0/S1/S2/S3) from the s9 P8 simulator
plus the four `LoadedSymbol` structures from the Step 03 loader plus
the C1-C8 safety attestations, and produces the in-sample-close
verdict from the closed 8-value `VerdictReason` enum.

Built fresh under Option A2 of the s9 aggregator-reuse decision plan
(P9, commit 113f5b9). The s7 D1 Step 07 aggregator was NOT reused
byte-equivalent because its input-shape duck-type check requires
`trade_groups` + `num_closed_units_total` (s7 D1 pyramid schema);
the s9 simulator instead emits `trade_records` + `num_closed_trades_total`
(flat schema; no pyramid per Tier-N section 12).

## Anchors

- **Tier-N spec:** `docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md`
  - sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`
  - commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- **Aggregator-reuse decision plan:** `docs/s9_cross_asset_mean_reversion_rsi2_aggregator_reuse_decision_plan.md`
  - sha256 `af6f8fd6d1de1b91e07679a6ce6e54660d961b6d9c20efac2d7da964d60d50f6`
  - commit `113f5b954e189088e6ddda18a2138abb27ff92e2`
- **Reused upstream Step 03 loader (s7 D1 chain):** commit `d7b2a0c`
- **s9 P6 signal-module build (verdict PASS):** commit `1a055bd`
- **s9 P8 simulator-module build (verdict PASS):** commit `1de75e5`
- **Step 07 s7 D1 aggregator (pattern reference, NOT byte-equiv reuse):**
  - aggregator.py sha256 `e6dde41745e401f3f0c72715766f6d6d0edd09c7064f0feb51765dc7b4553830`

## What this module does

- Takes `Mapping[str, LoadedSymbol]` (from `load_all()`), `Mapping[str,
  SimulationResult]` keyed by `"S0"`/`"S1"`/`"S2"`/`"S3"`, and a
  `Mapping[str, bool]` for the C1-C8 safety attestations.
- Validates input shape; refuses any non-IS date encountered on any
  `TradeRecord` field or `DailyEquityPoint.date`.
- Builds per-trade stats directly from each `TradeRecord` (each
  record IS a complete closed long entry-exit cycle; no group/unit
  hierarchy traversal because the s9 mechanic does not amplify per
  symbol per Tier-N section 12).
- Builds per-symbol stats (count, net/gross PnL, avg win, avg loss,
  P/L ratio, win count, loss count, breakeven count, observed
  win-rate, implied breakeven win-rate, win-rate gap to breakeven
  in percentage points).
- Builds portfolio stats (total closed trades, total net/gross PnL,
  mean / stdev per-trade PnL, Sharpe proxy per trade, expectancy per
  trade dollars, portfolio win-rate, portfolio P/L ratio, portfolio
  implied breakeven win-rate, portfolio win-rate gap to breakeven,
  trade-curve cumulative-PnL series, trade-curve high-water mark,
  trade-curve max drawdown dollars, trade-curve max drawdown percent
  of starting cash, cap-binding events count [structurally zero on
  s9]).
- Builds the 4-row cost-stress matrix (per-tier portfolio stats).
- Computes the cross-symbol pairwise dependence measure (Pearson
  coefficient on IS-window daily adj_close returns; byte-equivalent
  to Step 07 for inheritance fidelity since the diversification
  finding is a universe property, not a mechanic property) and the
  effective independent bets `N / (1 + (N-1) * avg_pair_dep)`.
- Evaluates DR2 / DR3 / DR5 cost-stress fail-fast rules per Tier-N
  section 13. DR4 is deferred to a separately authorized next-window
  phase.
- Evaluates K1-K12 rejection criteria per Tier-N section 17.
- Evaluates A1-A10 acceptance gates per Tier-N section 16.
- Assembles the verdict per the priority order
  `K8 > K12 > K6/K7 > K10 > K9 > K11 > K1/K2/K4 > A-gates > ELIGIBLE`.
- Returns an `AggregationResult` (per-call). Raises `AggregatorError`
  subclass on any refusal mode.

## What this module does NOT do

- No out-of-sample inspection. Every layer of the API and the loop
  refuses any non-IS date encountered. The pairwise dependence
  measure slices `loaded.adj_close` strictly within
  `IN_SAMPLE_WINDOW`.
- No simulator run; the caller invokes the simulator and passes the
  four `SimulationResult` instances.
- No signal recomputation; the simulator handled that upstream.
- No live-trading or brokerage path. No order construction. No
  scheduler/autopilot/FRC-gate touch.
- No Strategy Lab promotion. No candidate promotion to production
  idea memory. No `review_queue.json` mutation. The verdict
  `ELIGIBLE_FOR_OOS` is a structural attestation that **does NOT**
  auto-trigger any onward work; OOS inspection requires a
  separately authorized turn.
- No parameter optimization. No alternative-threshold sweep. No
  alternative-lookback search.
- No filter or regime gate. No asset selection. No winner-selection
  rule.
- No file IO. No network IO. No vendor SDK import. No
  `DATABENTO_API_KEY` access. No SSL bypass.
- No R-multiple field on `PerTradeStats` (s9 has no ATR-based
  per-trade risk denominator; the equal-dollar sizing convention
  makes R undefined; the field is omitted by design).

## Public API surface (27 symbols)

**Constants (13):** `A1_MIN_CLOSED_TRADES`, `A2_SHARPE_PROXY_MIN`,
`A3_EXPECTANCY_MIN`, `A4_TRADE_CURVE_MAXDD_PCT_MAX`,
`A5_PER_MARKET_WR_GAP_MIN_COUNT`, `A5_PORTFOLIO_WR_GAP_PP_MIN`,
`A7_EFFECTIVE_INDEPENDENT_BETS_MIN`, `A10_CAP_BINDING_EVENTS_MAX`,
`K10_AVG_PAIRWISE_DEPENDENCE_MAX`, `K11_CAP_BINDING_EVENTS_MAX`,
`DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION`,
`DR_STRESS_TIERS_REQUIRED`, `IN_SAMPLE_WINDOW`.

**Enum:** `VerdictReason` with 8 closed values (byte-equivalent to
Step 07): `PARKED_PROVENANCE_BROKEN`, `REJECT_FAST`,
`PARKED_SAFETY_FAILED`, `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS`,
`PARKED_FAILED_AT_INSUFFICIENT_SAMPLE`, `PARKED_CAP_BINDING`,
`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`, `ELIGIBLE_FOR_OOS`.

**Exceptions:** `AggregatorError`, `AggregatorInputError`,
`AggregatorOosBlockedError`, `AggregatorParameterOverrideError`,
`AggregatorProvenanceDriftError`.

**Dataclasses:** `PerTradeStats`, `PerSymbolStats`, `PortfolioStats`,
`CostStressRow`, `AGateResults`, `KCriteriaResults`,
`AggregationResult`.

**Entry point:** `aggregate(loaded, simulation_results,
safety_attestations, **kwargs) -> AggregationResult`.

## Verdict assembly priority (locked)

```
K8 PROVENANCE
  > K12 REJECT_FAST
  > K6/K7 SAFETY
  > K10 DIVERSIFICATION
  > K9 SAMPLE
  > K11 CAP
  > K1/K2/K4 MONEY-NOT-PROVEN
  > A1-A10 evaluation
  > ELIGIBLE_FOR_OOS
```

`ELIGIBLE_FOR_OOS` is a STRUCTURAL ATTESTATION ONLY. It does not
trigger any subsequent-window work. It does not change Live or
brokerage blocking posture. All onward phases require fresh operator
authorization.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal import compute_signals_all
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator import simulate, CostTier
from external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator import aggregate

data = load_all()
sig = compute_signals_all(data)
sims = {tier.name: simulate(data, sig, cost_tier=tier)
        for tier in (CostTier.S0, CostTier.S1, CostTier.S2, CostTier.S3)}
safety = {f"C{i}": True for i in range(1, 9)}

result = aggregate(data, sims, safety)
print("Verdict:", result.verdict.name)
print("Explanation:", result.verdict_explanation)
print("Closed trades:", result.portfolio_stats.total_closed_trades)
print("Sharpe proxy per trade:", result.portfolio_stats.sharpe_proxy_per_trade)
print("Expectancy per trade $:", result.portfolio_stats.expectancy_per_trade_dollars)
print("Avg pairwise dependence:", result.avg_pairwise_dependence_measure)
print("Effective independent bets:", result.effective_independent_bets)
```

## Refusal modes (`AggregatorError` tree)

| Exception | When raised |
|---|---|
| `AggregatorInputError` | input not a Mapping; symbol keys mismatch; missing cost tier; LoadedSymbol / SimulationResult shape mismatch; missing C1-C8 key |
| `AggregatorOosBlockedError` | any `SimulationResult.in_sample_window` mismatch; any TradeRecord field date or DailyEquityPoint.date outside IS window |
| `AggregatorParameterOverrideError` | any unknown kwarg passed to `aggregate()` |
| `AggregatorProvenanceDriftError` | reserved for API completeness; K8 firing is routed through the verdict path rather than raising |
| `AggregatorError` (base) | any other unhandled refusal |

## Tests

The test suite at
`tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/test_aggregator.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator`
performs no `open()` and no `Path.read_bytes()` call. The module
does not read any file at any point. Verified by test T12.
