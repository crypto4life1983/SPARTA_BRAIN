# s7 D1 Cross-Asset Yfinance Proxy Result Aggregator

Pure deterministic in-memory result aggregator that consumes Step 06
simulator outputs across S0/S1/S2/S3 cost tiers and produces an
IS-close verdict per parent spec sections 13 (A-gates A1-A10) and 14
(K-criteria K1-K11/K12). Built under the Step 07 result-aggregation
specification plan.

## Anchors

- **Spec plan:** `docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md`
  - sha256 `fc0f0dcd34b75055405fc1ba2bbbf4a60e57e2bb1a692feb86999c31e3108983`
  - commit `b99151caceb307a3708dcb5ac3a97e5131df02df`
- **Upstream Step 06 build (simulator, verdict PASS):** commit `ecd03e5`
- **Upstream Step 05 build (signal):** commit `25d262f`
- **Upstream Step 04 build (validator):** commit `a2ec179`
- **Upstream Step 03 build (loader):** commit `d7b2a0c`
- **Upstream Step 02c audit:** commit `1b640d1`

## Verdict vocabulary (locked enum)

| Verdict | Trigger |
|---|---|
| `PARKED_PROVENANCE_BROKEN` | K8 fires (upstream sha drift) |
| `REJECT_FAST` | K12 fires (DR2/DR3/DR5 cost-stress fail-fast) |
| `PARKED_SAFETY_FAILED` | K6 or K7 fires |
| `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS` | K10 fires (pairwise dep > 0.50) |
| `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE` | K9 fires (< 100 trades) |
| `PARKED_CAP_BINDING` | K11 fires (> 1000 cap-binding events) |
| `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` | K1 or K2 or K4 fires |
| `ELIGIBLE_FOR_OOS` | All A1-A10 pass, no K fires |

**`ELIGIBLE_FOR_OOS` does NOT auto-trigger OOS work.** It is a
structural attestation only. Live trading, Strategy Lab promotion,
brokerage connection, review_queue mutation all remain blocked at
separate plans regardless of verdict.

## What this module does

- Takes (`loaded` mapping, `simulation_results` mapping keyed by
  tier "S0"/"S1"/"S2"/"S3", `safety_attestations` mapping with
  C1-C8 keys) as input.
- Computes per-trade, per-symbol, and portfolio-level statistics at
  S1 baseline.
- Builds the cost-stress matrix across all four tiers; evaluates
  DR2 / DR3 / DR5 fail-fast.
- Computes pairwise Pearson dependence measure across the four
  symbols' daily adj_close returns over the in-sample window;
  derives effective independent bets.
- Evaluates K1-K11 + K12 + A1-A10.
- Assembles verdict per priority order from the closed 8-value
  enum.

## What this module does NOT do

- No out-of-sample inspection; every TradeUnit / TradeGroup /
  DailyEquityPoint date is checked against IN_SAMPLE_WINDOW.
- No simulator re-run; the caller runs the simulator four times
  (one per tier) and passes the results in.
- No loader / validator / signal module calls.
- No live trading. No paper order. No brokerage connection. No
  Strategy Lab promotion. No review_queue mutation. No
  idea_memory write. No scheduler / autopilot / FRC-gate touch.
- No network IO. No vendor SDK. No `DATABENTO_API_KEY` access.
- No parameter optimization, sweep, or search.
- No filter, regime gate, asset selection, or winner-selection.
- No threshold relaxation.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_signal import compute_signals_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_simulator import simulate, CostTier
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_aggregator import aggregate

loaded = load_all()
signals = compute_signals_all(loaded)
sims = {
    "S0": simulate(loaded, signals, cost_tier=CostTier.S0),
    "S1": simulate(loaded, signals, cost_tier=CostTier.S1),
    "S2": simulate(loaded, signals, cost_tier=CostTier.S2),
    "S3": simulate(loaded, signals, cost_tier=CostTier.S3),
}
safety = {f"C{i}": True for i in range(1, 9)}

result = aggregate(loaded, sims, safety)
print(result.verdict.value)
# REJECT_FAST  (or whichever verdict applies)
print(result.verdict_explanation)
```

## Refusal modes (`AggregatorError` tree)

| Exception | When raised |
|---|---|
| `AggregatorInputError` | bad shape / type / missing C1-C8 / missing required cost tier / non-LoadedSymbol / non-SimulationResult |
| `AggregatorOosBlockedError` | any date check fails IN_SAMPLE_WINDOW containment |
| `AggregatorParameterOverrideError` | unknown kwargs passed |
| `AggregatorProvenanceDriftError` | exported for API completeness; K8 firing flows through the verdict path rather than raising |
| `AggregatorError` (base) | any other unhandled refusal |

## Tests

The test suite at
`tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/test_aggregator.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.
