# s9 RSI-2 Aggregator Module Build Report

> Third-tier boundary-crossing build in the s9 chain. Pure
> deterministic in-memory result aggregator. In-sample only.
> First formal s9 IS verdict produced. No backtest. No
> next-window inspection. No network. No vendor SDK. No
> live trading.

**Phase:** `S9_CROSS_ASSET_MEAN_REVERSION_RSI2_AGGREGATOR_BUILD`
**Schema:** `sparta.s9.rsi2.aggregator_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T20:16:06Z
**Build verdict:** `PASS`
**First formal s9 IS verdict:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
**Verdict explanation:** Park: K1 Sharpe<0, K2 expectancy<=0.

**Companion JSON:** see same path .json; sha256 + seal recorded only in JSON to break sha cycle.

---

## 0. Anchors
- Tier-N spec: sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`  commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- Aggregator-reuse decision plan: sha256 `af6f8fd6d1de1b91e07679a6ce6e54660d961b6d9c20efac2d7da964d60d50f6`  commit `113f5b954e189088e6ddda18a2138abb27ff92e2`
- s9 signal-module build (PASS): commit `1a055bd1adecf30408de99971bf6e9f22cf53866`
  - build report sha256 `d78ad857ffc26a4392554d9208a9904513671c108037d24a02ba2d76de521b9b`
- s9 simulator-module build (PASS): commit `1de75e576c9878a2dfc2568b8f5747fda7eb84cf`
  - build report sha256 `0bdbde0e2a0d65220e77f35baf0e06f8304ee120f428b2929301d19cba004e94`
  - build report seal `957b685110ec11e120fdbd7d218f145b6eb974de81a849c04e7aa75f04a70e44`
- Selection plan commit: `530b54598fa7098eb746f2122b4002db2c984422`
- Predecessor park commit: `a5ac092`
- Step 03 loader.py sha256: `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9` (reused byte-equiv)
- Step 04 validator.py sha256: `bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e` (reused byte-equiv)
- s9 signal.py sha256: `8776e87b3482c7f5989bd5832a1e96b12bba3b9186432483759095f30b714f1d` (consumed read-only)
- s9 simulator.py sha256: `d5c9b9e82a7a6b92206c11d56690a0784903dbece0531da07f4ef3b330b6837e` (consumed read-only)
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/aggregator.py` | 37,950 | `95a6e9b1f153de04` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/__init__.py` | 2,567 | `4f4b5e352ab85090` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/README.md` | 9,039 | `b40f6e78a9e77c16` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/test_aggregator.py` | 18,070 | `8800caa4070e77c3` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/__init__.py` | 0 | `e3b0c44298fc1c14` |

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
| V7 test_suite_pass | OK | tests=26 f=0 e=0 s=0 |
| V8 all_T1_T16_present | OK | |
| V9 live_in_sample_round_trip | OK | T01/T02/T03/T04/T05 PASS |
| V10 negative_path | OK | T06/T07/T08/T09 PASS |

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

## 5. First formal s9 IS verdict
### Verdict: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
### Explanation: Park: K1 Sharpe<0, K2 expectancy<=0.

### Portfolio statistics (S1 baseline)
| Metric | Value |
|---|---|
| total_closed_trades | 414 |
| total_net_pnl_dollars | -1334.870032 |
| total_gross_pnl_dollars | -1272.250032 |
| mean_trade_net_pnl_dollars | -3.224324 |
| stdev_trade_net_pnl_dollars | 33.194124 |
| sharpe_proxy_per_trade | -0.097135 |
| expectancy_per_trade_dollars | -3.224324 |
| portfolio_win_rate | 0.531401 |
| portfolio_pl_ratio | 0.601472 |
| portfolio_implied_breakeven_win_rate | 0.624425 |
| portfolio_win_rate_gap_to_breakeven_pp | -9.302437 |
| trade_curve_max_drawdown_dollars | 1642.249766 |
| trade_curve_max_drawdown_pct_vs_starting_cash | 1.64225 |
| cap_binding_events_count | 0 |

### Cost-stress matrix
| Tier | slip | comm | trades | net pnl | sharpe pt | expectancy | maxdd% | win rate | pl ratio | k4 |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 0.0 | 0.0 | 414 | -1211.030033 | -0.08816 | -2.925193 | 1.56573 | 0.533816 | 0.611422 | False |
| S1 | 1.0 | 1.0 | 414 | -1334.870032 | -0.097135 | -3.224324 | 1.64225 | 0.531401 | 0.601472 | False |
| S2 | 3.0 | 1.5 | 414 | -1578.440026 | -0.115118 | -3.812657 | 1.79145 | 0.519324 | 0.586484 | False |
| S3 | 5.0 | 2.0 | 414 | -1825.78003 | -0.133048 | -4.410097 | 1.95226 | 0.507246 | 0.571144 | False |

### Per-symbol statistics
| Symbol | trades | net pnl | wins | losses | wr | ibwr | wr gap pp |
|---|---|---|---|---|---|---|---|
| SPY | 101 | 140.090297 | 65 | 36 | 0.643564 | 0.589441 | 5.41231 |
| TLT | 103 | -104.229948 | 48 | 55 | 0.466019 | 0.520576 | -5.455702 |
| GLD | 103 | -194.130359 | 58 | 45 | 0.563107 | 0.640569 | -7.746174 |
| USO | 107 | -1176.600021 | 49 | 58 | 0.457944 | 0.62159 | -16.364634 |

### DR rules
- `DR2_S2_or_S3_degrades_materially`: **False**
- `DR3_zero_cost_only_survival`: **False**
- `DR4_is_pos_oos_neg_at_S0`: **DEFERRED_TO_NEXT_WINDOW_PHASE**
- `DR5_S0_to_S1_edge_negative`: **False**

### K-criteria (True == fired)
| K | Fired |
|---|---|
| K1_sharpe_below_zero | True |
| K2_expectancy_nonpositive | True |
| K3_reserved | False |
| K4_trade_curve_maxdd_above_50 | False |
| K5_reserved | False |
| K6_safety_warning_count_above_zero | False |
| K7_filter_or_dependence_gate_silently_introduced | False |
| K8_sealed_parent_drift | False |
| K9_closed_trades_below_100 | False |
| K10_avg_pairwise_dependence_above_threshold | False |
| K11_cap_binding_events_above_1000 | False |
| K12_dr_fires | False |

### A-gates (True == passed)
| A | Passed |
|---|---|
| A1_closed_trades_at_least_min | True |
| A2_sharpe_proxy_positive | False |
| A3_expectancy_positive | False |
| A4_trade_curve_maxdd_at_or_below_max | True |
| A5_per_market_and_portfolio_wr_gap | False |
| A6_upstream_phases_all_pass | True |
| A7_effective_independent_bets_at_least_min | True |
| A8_cost_stress_matrix_complete_and_dr_clear | True |
| A9_safety_template_c1_c8_all_true | True |
| A10_cap_binding_events_zero | True |

### Diversification: avg_pairwise_dependence_measure = `0.041354` ; effective_independent_bets = `3.558527`

## 6. Forbidden-token grep results
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
| `Donchian` | 0 |
| `ATR(` | 0 |
| `wilder_atr` | 0 |
| `wilder_n` | 0 |
| `pyramid_unit` | 0 |
| `pyramid_step` | 0 |
| `stop_distance` | 0 |
| `stop_price` | 0 |
| `STOP_HIT` | 0 |
| `STOP_DISTANCE_N_MULTIPLE` | 0 |
| `DONCHIAN_20_EXIT` | 0 |
| `_optimize_` | 0 |
| `_sweep_` | 0 |
| `_tune_` | 0 |
| `_grid_search_` | 0 |
| `_bayes_search_` | 0 |
| `alternative_lookback` | 0 |
| `alternative_threshold` | 0 |
| `lookback_grid` | 0 |
| `threshold_grid` | 0 |
| `parameter_grid` | 0 |
| `winner_selection` | 0 |
| `asset_selection` | 0 |
| `top_n_pick` | 0 |
| `regime_filter` | 0 |
| `regime_gate` | 0 |
| `ma_filter` | 0 |
| `vol_filter` | 0 |
| `dependence_filter` | 0 |
| `correlation_filter` | 0 |
| `trend_filter` | 0 |
| `volume_filter` | 0 |
| `entry_short_triggered` | 0 |
| `exit_short_triggered` | 0 |
| `short_position` | 0 |
| `borrow_cost` | 0 |
| `borrow_rate` | 0 |
| `short_entry` | 0 |
| `short_exit` | 0 |
| `simulate_oos` | 0 |
| `compute_oos` | 0 |
| `aggregate_oos` | 0 |
| `post_oos_simulation` | 0 |
| `force_oos` | 0 |
| `skip_oos` | 0 |
| `disable_oos_check` | 0 |

## 7. Boundaries held (all True)
 - `aggregator_consumes_s9_trade_records_schema_only`  
 - `aggregator_does_not_compute_oos_inspection`  
 - `aggregator_does_not_compute_post_oos_inspection`  
 - `aggregator_does_not_recompute_rsi`  
 - `aggregator_does_not_run_signal_module`  
 - `aggregator_does_not_run_simulator`  
 - `aggregator_eligible_for_oos_does_not_auto_trigger_anything`  
 - `aggregator_has_no_file_io`  
 - `aggregator_has_no_forbidden_import`  
 - `aggregator_has_no_forbidden_token`  
 - `aggregator_has_no_module_level_mutable_state`  
 - `aggregator_in_sample_only_via_5_layer_enforcement`  
 - `aggregator_is_pure_deterministic_function`  
 - `aggregator_rejects_extra_kwargs`  
 - `aggregator_verdict_in_8_value_closed_enum`  
 - `build_under_operator_authorization`  
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_audit_manifest_modification`  
 - `no_branch_change`  
 - `no_brokerage_connection`  
 - `no_commit_beyond_seven_output_files`  
 - `no_csv_modification`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_decision_plan_modification`  
 - `no_docs_decisions_md_modification`  
 - `no_existing_artifact_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_live_trading`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_orb_branch_mutation`  
 - `no_order_creation`  
 - `no_paper_order`  
 - `no_pipeline_manifest_modification`  
 - `no_real_order`  
 - `no_review_queue_mutation`  
 - `no_s7_d1_artifact_modification`  
 - `no_signal_module_modification`  
 - `no_signal_spec_modification`  
 - `no_simulator_module_modification`  
 - `no_simulator_spec_modification`  
 - `no_step_07_aggregator_modification`  
 - `no_strategy_lab_promotion`  
 - `no_tier_n_spec_modification`  
 - `no_validator_modification`

## 8. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `brokerage_connection`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `fetch_manifest_modified`  
 - `file_io_performed_by_aggregator`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_inspection_performed_by_aggregator`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `rsi_recomputed_by_aggregator`  
 - `signal_module_modified`  
 - `signal_spec_modified`  
 - `simulator_module_modified`  
 - `simulator_run_by_aggregator`  
 - `simulator_spec_modified`  
 - `step_07_aggregator_modified`  
 - `strategy_lab_promoted`  
 - `tier_n_spec_modified`  
 - `validator_modified`  
 - `yfinance_imported_by_aggregator`

## 9. API-key safety confirmation
- `any_brokerage_call_by_aggregator`: **False**
- `any_file_io_by_aggregator`: **False**
- `any_network_call_by_aggregator`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_aggregator`: **False**
- `yfinance_imported_by_aggregator`: **False**

## 10. OOS protection attestation
- `no_oos_inspection_performed`: **True**
- `no_post_oos_inspection_performed`: **True**
- `no_oos_signal_computed`: **True**
- `no_oos_simulation_run`: **True**
- `no_oos_value_inspected_by_aggregator`: **True**
- `signal_module_attestation_inherited`: **True**
- `simulator_module_attestation_inherited`: **True**

## 11. Live-action blocking attestation
- `no_live_order_placed`: **True**
- `no_paper_order_placed`: **True**
- `no_brokerage_session_opened`: **True**
- `no_scheduler_invocation`: **True**
- `no_strategy_lab_promotion`: **True**
- `no_candidate_promotion`: **True**
- `no_review_queue_mutation`: **True**
- `no_production_idea_memory_mutation`: **True**
- `no_orb_branch_artifact_mutation`: **True**
- `verdict_eligible_for_oos_does_not_auto_trigger`: **True**
- `trading_paused_unchanged`: **True**
- `live_blocked_at_six_gates_unchanged`: **True**
- `frc_never_granted`: **True**

## 12. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

