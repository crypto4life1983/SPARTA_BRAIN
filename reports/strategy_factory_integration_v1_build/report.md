# Strategy Factory v1 Integration Bundle -- Research-Only Dry-Run

- layer: `strategy_factory_integration_v1`
- **dry_run: True  |  executes_anything: False  |  executes_backtest: False**
- uses_synthetic_data_only: True  |  reads_frozen_dataset: False
- primary_lookback: 20  |  verdict_ceiling: WATCH

## Chain

queue -> orchestrator -> runner_output_adapter -> deeper_validation -> validation_report -> decision_memo -> registry_update_proposal -> dashboard_feed_preview -> next_action

## Inputs (read-only)

- queue: {'layer': 'strategy_factory_queue_v1', 'item_count': 1, 'valid_item_count': 1, 'blocked_item_count': 0}
- orchestrator: {'layer': 'strategy_factory_orchestrator_v1', 'dry_run': True, 'executes_anything': False, 'execution_halted': False, 'task_count': 1}
- safety: {'layer': 'strategy_factory_safety_v1', 'valid': True, 'safe': True}
- registry: {'layer': 'strategy_report_registry_v1', 'strategy_count': 3}

## Decision

- **verdict: FAIL** (allowed: ['WATCH', 'FAIL', 'INSUFFICIENT_EVIDENCE'])
- evidence_level: NONE
- promotion_blocked: True
- rationale: Synthetic dry-run did not clear the per-asset/family research trade floors; recorded as FAIL pending a future real-data review.

### Checks

- all_assets_positive: True
- fee_stress_survived: True
- meets_family_floor: False
- neighborhood_sensitivity_not_optimization: True
- not_outlier_dependent: False
- not_single_regime: True
- per_asset_floor_all_clear: False

## Proposals / previews (not applied)

- registry_update_proposal: proposal_only=True, applied=False
- dashboard_feed_preview: preview_only=True, applied_to_dashboard=False

## Next action

Await separate operator approval to (a) wire real runner OOS slices into the adapter for true validation and (b) decide whether to apply the registry proposal. No further step is authorized now. Verdict stays capped at WATCH (current synthetic read: FAIL).

## Non-authorization

Research-only dry-run INTEGRATION layer. Composes read-only factory views over synthetic bars and emits descriptive artifacts plus a registry proposal and a dashboard preview. It runs no backtest over frozen data, executes no queue task, mutates no queue/registry/dashboard/dataset, and authorizes no paper/live/broker/exchange/order/fetch action. It promotes no lane to ACTIVE/STRONG and emits no PASS. Verdict ceiling stays WATCH; Crypto-D1 stays WATCH/MIXED and NOT_READY_FOR_REAL_DATA. A positive synthetic view is not a trading authorization.
