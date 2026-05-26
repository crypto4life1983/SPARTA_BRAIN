# s7 D1 Donchian Step 06 - Simulator Build Report

> SECOND-TIER BOUNDARY-CROSSING BUILD. First simulator-side code
> in the chain. Pure deterministic in-memory Faith System 1
> mechanic executor. In-sample only. No result aggregation. No
> network. No vendor SDK. No broker. No live trading.

**Phase:** `S7_D1_DONCHIAN_STEP_06_SIMULATOR_BUILD`
**Schema:** `sparta.donchian.step_06_simulator_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T00:43:12Z
**Build verdict:** `PASS`

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_step_06_simulator_build_report.json` (sha256 + seal recorded only in JSON; recompute from JSON bytes to verify)

---

## 0. Anchors
- Plan: `docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md` (sha256 `f7581af358c676519d46f1a0bec486c35cf61f0f5f618faf7f000adf6223878b`, commit `c964c59ce0d499b7feb24611d5ea2f6c7a840e08`)
- Step 05 signal build sha256: `65ee1b6a5c7635abc1597479aacf6457a84fdb7036e50b0bcd1d0aa284897d72`  seal: `df0f28fa974868580e882ff364c3331d2feeab54d5d1d10c000e09c29701b4cc`
- Step 05 signal.py sha256: `67c88d9aba58ae28f22313a1bbe0d51581aee6b54b0d43dec76d93f743874a89`
- Step 04 validator build sha256: `fbabd75ea7ce1914ece7a7fda8c957c9e22899538321c180e7c37c378feedd27`
- Step 03 loader build sha256: `137dd8534de840762abc9e6e3f9d22ad5314a1e6f2a4ddc783da3e90429c8386`
- Step 02c audit sha256: `a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354`
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/simulator.py` | 45,198 | `7809cccf385b5f8b` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/__init__.py` | 1,803 | `55a643a9c096071d` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/README.md` | 6,010 | `ce3d56bd10a6ca89` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/test_simulator.py` | 20,512 | `2691ee940dddf960` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_simulator/__init__.py` | 0 | `e3b0c44298fc1c14` |

## 2. Public API surface (V4)
Expected (24 symbols); observed `__all__` exactly matches: **True**
- `CostTier`
- `DEFAULT_STARTING_CASH`
- `DailyEquityPoint`
- `ENTRY_CHANNEL_LOOKBACK`
- `ETF_DOLLAR_PER_SHARE`
- `ETF_TICK_SIZE`
- `EXIT_CHANNEL_LOOKBACK`
- `ExitReason`
- `IN_SAMPLE_WINDOW`
- `K4_PORTFOLIO_MAXDD_PCT`
- `MAX_UNITS_PER_SYMBOL`
- `PER_UNIT_RISK_FRACTION`
- `PYRAMID_STEP_N_MULTIPLE`
- `STOP_DISTANCE_N_MULTIPLE`
- `SimulationResult`
- `SimulatorError`
- `SimulatorInputError`
- `SimulatorK4FiredError`
- `SimulatorOosBlockedError`
- `SimulatorParameterOverrideError`
- `TradeGroup`
- `TradeUnit`
- `WILDER_ATR_LOOKBACK`
- `simulate`

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 five_code_files_exist | OK | reports written at end |
| V2 simulator_AST_compiles | OK |  |
| V3 import_performs_no_file_io | OK | |
| V4 api_surface_matches | OK | obs=24 exp=24 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_pass | OK | tests=17 f=0 e=0 s=0 |
| V8 all_T1_T16_present | OK | |
| V9 live_in_sample_round_trip | OK | T01/T02/T06/T11/T15 PASS |
| V10 negative_path | OK | T03/T04/T07 PASS |

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
| `sharpe` | 0 |
| `sortino` | 0 |
| `calmar` | 0 |
| `expectancy` | 0 |
| `win_rate` | 0 |
| `correlation` | 0 |
| `covariance` | 0 |
| `.pct_change(` | 0 |
| `effective_independent_bets` | 0 |
| `avg_pairwise_correlation` | 0 |
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
| `correlation_filter` | 0 |
| `beta_filter` | 0 |
| `compute_signals_oos` | 0 |
| `simulate_oos` | 0 |
| `simulate_full_window` | 0 |
| `simulate_post_oos` | 0 |

## 6. Boundaries held (all True)
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
 - `no_docs_decisions_md_modification`  
 - `no_existing_step_02b_02c_03_04_05_artifact_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_live_trading`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_orb_branch_mutation`  
 - `no_paper_order`  
 - `no_pipeline_manifest_modification`  
 - `no_real_order`  
 - `no_review_queue_mutation`  
 - `no_signal_module_modification`  
 - `no_simulator_run_on_oos_bar`  
 - `no_spec_modification`  
 - `no_step_06_plan_modification`  
 - `no_strategy_lab_promotion`  
 - `no_validator_modification`  
 - `simulator_does_not_compute_pairwise_dependence_measure`  
 - `simulator_does_not_compute_step_07_aggregation_statistic`  
 - `simulator_flat_marks_at_in_sample_end_no_oos_carry`  
 - `simulator_has_no_file_io`  
 - `simulator_has_no_forbidden_import`  
 - `simulator_has_no_forbidden_token`  
 - `simulator_has_no_module_level_mutable_state`  
 - `simulator_in_sample_only_via_event_date_check`  
 - `simulator_in_sample_only_via_signal_module_inheritance`  
 - `simulator_is_pure_deterministic_function`  
 - `simulator_max_units_per_group_lifetime_4`  
 - `simulator_no_new_entry_after_k4_fired`  
 - `simulator_no_time_stop_no_profit_target_no_trailing`  
 - `simulator_pyramid_uses_same_n_entry_from_unit_0`  
 - `simulator_stop_intra_bar_wins_over_close_trigger_same_bar`  
 - `simulator_uses_hardcoded_in_sample_window_no_override`  
 - `simulator_uses_hardcoded_lookbacks_no_override`

## 7. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `backtest_run_in_this_build`  
 - `branch_changed`  
 - `branch_created`  
 - `broker_session_opened`  
 - `brokerage_connection`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `fetch_manifest_modified`  
 - `file_io_performed_by_simulator`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_signal_computed_by_simulator`  
 - `oos_value_inspected_by_simulator`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `signal_module_modified`  
 - `step_07_aggregation_statistic_computed`  
 - `strategy_lab_promoted`  
 - `validator_modified`  
 - `yfinance_imported_by_simulator`

## 8. API-key safety confirmation
- `any_brokerage_call_by_simulator`: **False**
- `any_file_io_by_simulator`: **False**
- `any_network_call_by_simulator`: **False**
- `any_review_queue_mutation_by_simulator`: **False**
- `any_strategy_lab_call_by_simulator`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_simulator`: **False**
- `yfinance_imported_by_simulator`: **False**

## 9. Out-of-sample protection attestation
- `no_oos_simulation`: **True**
- `no_post_oos_simulation`: **True**
- `no_oos_value_inspected_by_simulator`: **True**

## 10. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

