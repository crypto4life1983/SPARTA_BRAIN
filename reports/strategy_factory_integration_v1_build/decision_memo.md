# Crypto-D1 N=20 Integration Dry-Run -- Decision Memo (research-only)

- **verdict: FAIL**  (ceiling: WATCH; allowed: WATCH, FAIL, INSUFFICIENT_EVIDENCE)
- evidence_level: NONE
- promotion_blocked: True

## Why this verdict

Synthetic dry-run did not clear the per-asset/family research trade floors; recorded as FAIL pending a future real-data review.

Research-only synthetic dry-run; not real-data validation. No promotion tier above WATCH is reachable from this dry-run.

## Checks (descriptive, from the deeper-validation views)

- all_assets_positive: True
- fee_stress_survived: True
- meets_family_floor: False
- neighborhood_sensitivity_not_optimization: True
- not_outlier_dependent: False
- not_single_regime: True
- per_asset_floor_all_clear: False

## Next action

Await separate operator approval to (a) wire real runner OOS slices into the adapter for true validation and (b) decide whether to apply the registry proposal. No further step is authorized now. Verdict stays capped at WATCH (current synthetic read: FAIL).

## Non-authorization

Research-only dry-run INTEGRATION layer. Composes read-only factory views over synthetic bars and emits descriptive artifacts plus a registry proposal and a dashboard preview. It runs no backtest over frozen data, executes no queue task, mutates no queue/registry/dashboard/dataset, and authorizes no paper/live/broker/exchange/order/fetch action. It promotes no lane to ACTIVE/STRONG and emits no PASS. Verdict ceiling stays WATCH; Crypto-D1 stays WATCH/MIXED and NOT_READY_FOR_REAL_DATA. A positive synthetic view is not a trading authorization.
