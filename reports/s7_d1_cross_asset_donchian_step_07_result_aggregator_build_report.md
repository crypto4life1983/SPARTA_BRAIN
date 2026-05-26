# s7 D1 Donchian Step 07 - Result Aggregator Build Report

> THIRD-TIER BOUNDARY-CROSSING BUILD. First aggregator-side code
> in the chain. Pure deterministic in-memory result aggregation
> over Step 06 simulator outputs across S0/S1/S2/S3. Produces
> the FIRST FORMAL IS VERDICT from the closed 8-value enum.

**Phase:** `S7_D1_DONCHIAN_STEP_07_RESULT_AGGREGATOR_BUILD`
**Schema:** `sparta.donchian.step_07_result_aggregator_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T01:25:38Z
**Build verdict:** `PASS`

## FIRST FORMAL IS VERDICT (real-data integration)

**Verdict:** `REJECT_FAST`
**Explanation:** K12 fires: DR2 / DR3 / DR5 cost-stress fail-fast on the matrix.

- portfolio.total_closed_trades: **37**
- portfolio.total_net_pnl_dollars: **589.5904078177693**
- portfolio.trade_curve_max_drawdown_pct: **69.10094005427824%**
- avg_pairwise_dependence_measure: **0.041353542957696436**
- effective_independent_bets: **3.5585269132770376**

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_step_07_result_aggregator_build_report.json` (sha256 + seal recorded only in JSON; recompute from JSON bytes to verify)

---

## 0. Anchors
- Plan: `docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md` (sha256 `fc0f0dcd34b75055405fc1ba2bbbf4a60e57e2bb1a692feb86999c31e3108983`, commit `b99151caceb307a3708dcb5ac3a97e5131df02df`)
- Step 06 simulator: seal `db2b2e9a72d5713e0f44e1a9b44fb4ca59433db3211f3c0dc3ce40b0b4083a81`
- Step 05 signal: seal `df0f28fa974868580e882ff364c3331d2feeab54d5d1d10c000e09c29701b4cc`
- Step 04 validator: seal `737a3f54b0a380e1c298a83a9fb8183b0fbdba23b42fa002a2b7fe0d9883ba3f`
- Step 03 loader: seal `89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c`
- Step 02c audit: seal `872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/aggregator.py` | 35,408 | `e6dde41745e401f3` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/__init__.py` | 2,468 | `d129b771a767efef` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/README.md` | 4,722 | `b5abcebc27131010` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/test_aggregator.py` | 21,480 | `7c87604925468da1` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_aggregator/__init__.py` | 0 | `e3b0c44298fc1c14` |

## 2. Public API surface (V4)
Expected (27 symbols); observed `__all__` exactly matches: **True**
- `A10_CAP_BINDING_EVENTS_MAX`
- `A1_MIN_CLOSED_TRADES`
- `A2_SHARPE_PROXY_MIN`
- `A3_EXPECTANCY_MIN`
- `A4_TRADE_CURVE_MAXDD_PCT_MAX`
- `A5_PER_MARKET_WR_GAP_MIN_COUNT`
- `A5_PORTFOLIO_WR_GAP_PP_MIN`
- `A7_EFFECTIVE_INDEPENDENT_BETS_MIN`
- `AGateResults`
- `AggregationResult`
- `AggregatorError`
- `AggregatorInputError`
- `AggregatorOosBlockedError`
- `AggregatorParameterOverrideError`
- `AggregatorProvenanceDriftError`
- `CostStressRow`
- `DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION`
- `DR_STRESS_TIERS_REQUIRED`
- `IN_SAMPLE_WINDOW`
- `K10_AVG_PAIRWISE_DEPENDENCE_MAX`
- `K11_CAP_BINDING_EVENTS_MAX`
- `KCriteriaResults`
- `PerSymbolStats`
- `PerTradeStats`
- `PortfolioStats`
- `VerdictReason`
- `aggregate`

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 files_exist | OK | |
| V2 AST_compiles | OK |  |
| V3 no_io_at_import | OK | |
| V4 api_surface_matches | OK | obs=27 exp=27 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_pass | OK | tests=16 f=0 e=0 s=0 |
| V8 all_T1_T16_present | OK | |
| V9 live_in_sample_round_trip | OK | T01/T02/T06/T13 PASS |
| V10 negative_path | OK | T03/T04/T07/T10/T11 PASS |

## 4. T1-T16 test results
| Test | Result |
|---|---|
| T01 | PASS |
| T02 | PASS |
| T03 | PASS |
| T04 | PASS |
| T05 | PASS |
| T06 | PASS |
| T07 | PASS |
| T08 | PASS |
| T09 | PASS |
| T10 | PASS |
| T11 | PASS |
| T12 | PASS |
| T13 | PASS |
| T14 | PASS |
| T15 | PASS |
| T16 | PASS |

## 5. Forbidden-token grep results
| Token | hits |
|---|---|
| `DATABENTO_API_KEY` | 0 |
| `yfinance` | 0 |
| `yahoo_finance` | 0 |
| `databento` | 0 |
| `requests.get` | 0 |
| `urllib.request` | 0 |
| `socket.connect` | 0 |
| `http.client` | 0 |
| `curl_cffi` | 0 |
| `aiohttp` | 0 |
| `httpx` | 0 |
| `Strategy Lab` | 0 |
| `strategy_lab` | 0 |
| `review_queue` | 0 |
| `idea_memory` | 0 |
| `live trading` | 0 |
| `live_trading` | 0 |
| `brokerage` | 0 |
| `broker_api` | 0 |
| `broker_session` | 0 |
| `alpaca` | 0 |
| `interactive_brokers` | 0 |
| `ibkr` | 0 |
| `ibapi` | 0 |
| `ib_insync` | 0 |
| `tradestation` | 0 |
| `binance` | 0 |
| `oanda` | 0 |
| `order_send` | 0 |
| `place_order` | 0 |
| `submit_order` | 0 |
| `cancel_order` | 0 |
| `modify_order` | 0 |
| `route_order` | 0 |
| `production_signal` | 0 |
| `paper_broker` | 0 |
| `paper_trade` | 0 |
| `scheduler` | 0 |
| `autopilot` | 0 |
| `frc_gate` | 0 |
| `compute_signals_oos` | 0 |
| `simulate_oos` | 0 |
| `simulate_full_window` | 0 |
| `simulate_post_oos` | 0 |
| `oos_simulation` | 0 |
| `_optimize_` | 0 |
| `_sweep_` | 0 |
| `_tune_` | 0 |
| `_grid_search_` | 0 |
| `_bayes_search_` | 0 |
| `alternative_lookback` | 0 |
| `lookback_grid` | 0 |
| `parameter_grid` | 0 |
| `winner_selection` | 0 |
| `asset_selection` | 0 |
| `top_n_pick` | 0 |
| `regime_filter` | 0 |
| `regime_gate` | 0 |
| `ma_filter` | 0 |
| `vol_filter` | 0 |
| `dependence_filter` | 0 |

## 6. Boundaries held (all True)
 - `aggregator_does_not_call_loader_or_validator_or_signal`  
 - `aggregator_does_not_inspect_oos_values`  
 - `aggregator_does_not_recommend_oos_as_runtime_action`  
 - `aggregator_does_not_run_simulator`  
 - `aggregator_has_no_forbidden_import`  
 - `aggregator_has_no_forbidden_token`  
 - `aggregator_has_no_module_level_mutable_state`  
 - `aggregator_has_no_write_io`  
 - `aggregator_in_sample_only_via_event_date_check`  
 - `aggregator_is_pure_deterministic_function`  
 - `aggregator_uses_closed_verdict_enum_8_values`  
 - `aggregator_uses_hardcoded_thresholds_no_override`  
 - `aggregator_verdict_priority_per_plan_section_16`  
 - `build_under_operator_authorization`  
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_audit_manifest_modification`  
 - `no_branch_change`  
 - `no_broker_integration`  
 - `no_commit_beyond_seven_output_files`  
 - `no_csv_modification`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_docs_decisions_md_modification`  
 - `no_downstream_research_promotion`  
 - `no_existing_artifact_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_live_action`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_orb_branch_mutation`  
 - `no_order_creation`  
 - `no_paper_order`  
 - `no_pipeline_manifest_modification`  
 - `no_real_order`  
 - `no_review_queue_mutation`  
 - `no_signal_module_modification`  
 - `no_simulator_modification`  
 - `no_spec_modification`  
 - `no_step_07_plan_modification`  
 - `no_validator_modification`

## 7. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `branch_changed`  
 - `branch_created`  
 - `broker_integration`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `downstream_research_promoted`  
 - `fetch_manifest_modified`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_action_taken`  
 - `loader_modified`  
 - `network_used`  
 - `oos_value_inspected_by_aggregator`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `signal_module_modified`  
 - `simulator_modified`  
 - `simulator_re_run_outside_test_integration`  
 - `validator_modified`  
 - `yfinance_imported_by_aggregator`

## 8. API-key safety confirmation
- `any_brokerage_call_by_aggregator`: **False**
- `any_file_write_by_aggregator`: **False**
- `any_network_call_by_aggregator`: **False**
- `any_oos_inspection_by_aggregator`: **False**
- `any_review_queue_mutation_by_aggregator`: **False**
- `any_strategy_lab_call_by_aggregator`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_aggregator`: **False**
- `yfinance_imported_by_aggregator`: **False**

## 9. Out-of-sample protection attestation
- `no_oos_inspection_by_aggregator`: **True**
- `no_post_oos_inspection_by_aggregator`: **True**
- `no_oos_value_inspected_for_metric_computation`: **True**

## 10. Live-action blocking attestation
- `no_live_action_signal`: **True**
- `no_broker_integration_call`: **True**
- `no_real_order_placed`: **True**
- `no_paper_order_placed`: **True**
- `no_downstream_research_promotion`: **True**
- `no_review_queue_mutation`: **True**

## 11. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.**
**First formal IS verdict: `REJECT_FAST`.**
Trading: PAUSED. Live: BLOCKED at 6 gates.

