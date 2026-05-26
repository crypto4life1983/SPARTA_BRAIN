# s9 RSI-2 Simulator Module Build Report

> Second-tier boundary-crossing build in the s9 chain. Pure
> deterministic in-memory long-only RSI-2 mechanic executor.
> In-sample only. No backtest. No OOS. No aggregation
> statistic. No risk-adjusted ratio. No pairwise dependence
> measure. No network. No vendor SDK. No live trading.

**Phase:** `S9_CROSS_ASSET_MEAN_REVERSION_RSI2_SIMULATOR_BUILD`
**Schema:** `sparta.s9.rsi2.simulator_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T18:55:34Z
**Build verdict:** `PASS`

**Companion JSON:** see same path .json; sha256 + seal recorded only in JSON to break sha cycle.

---

## 0. Anchors
- Tier-N spec: sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`  commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- Signal-module spec: sha256 `59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9`  commit `c5393ab31a58059004b8cd337cd428eacbcbaece`
- Simulator-module spec: sha256 `c64bbe7525ad06d5d870b51b6c5b8c9ba45a17675acc5ecc3e2faa4c545f83bf`  commit `3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f`
- s9 signal-module build (verdict PASS): commit `1a055bd1adecf30408de99971bf6e9f22cf53866`
  - build report sha256 `d78ad857ffc26a4392554d9208a9904513671c108037d24a02ba2d76de521b9b` seal `f553ae8a31ec0ff11dc19cf5c5336c541698df306a82c5a716a836d875a4417a`
- Selection plan commit: `530b54598fa7098eb746f2122b4002db2c984422`
- Predecessor park commit: `a5ac092`
- Step 03 loader.py sha256: `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9` (reused byte-equiv)
- Step 04 validator.py sha256: `bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e` (reused byte-equiv)
- s9 signal.py sha256: `8776e87b3482c7f5989bd5832a1e96b12bba3b9186432483759095f30b714f1d` (consumed read-only)
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/simulator.py` | 36,522 | `d5c9b9e82a7a6b92` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/__init__.py` | 2,190 | `c44da22685fb6736` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/README.md` | 7,216 | `4d32b8c5fbb904e8` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/test_simulator.py` | 19,562 | `3e1ccb8c03204f1e` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/__init__.py` | 0 | `e3b0c44298fc1c14` |

## 2. Public API surface (V4)
Expected (21 symbols); observed `__all__` exactly matches: **True**
- `CostTier`
- `DEFAULT_STARTING_CASH`
- `DailyEquityPoint`
- `ETF_DOLLAR_PER_SHARE`
- `ETF_TICK_SIZE`
- `ExitReason`
- `IN_SAMPLE_WINDOW`
- `K4_PORTFOLIO_MAXDD_PCT`
- `MAX_UNITS_PER_SYMBOL`
- `PER_SIGNAL_ALLOCATION_FRACTION`
- `RSI_EXIT_THRESHOLD`
- `RSI_LOOKBACK`
- `RSI_OVERSOLD_ENTRY_THRESHOLD`
- `SimulationResult`
- `SimulatorError`
- `SimulatorInputError`
- `SimulatorK4FiredError`
- `SimulatorOosBlockedError`
- `SimulatorParameterOverrideError`
- `TradeRecord`
- `simulate`

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 files_exist | OK | |
| V2 AST_compiles | OK |  |
| V3 no_io_at_import | OK | |
| V4 api_surface_matches | OK | obs=21 exp=21 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_pass | OK | tests=29 f=0 e=0 s=0 |
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

## 5. Live simulator summary on real ETF-proxy data (IS-only)

| Tier | trades | per-sym | final cash | maxdd % | k4 | first | last | daily-pts | skips |
|---|---|---|---|---|---|---|---|---|---|
| S0 | 414 | GLD:103/SPY:101/TLT:103/USO:107 | 98,788.97 | 1.63 | False | 2014-01-06 | 2022-12-30 | 2264 | 586 |
| S1 | 414 | GLD:103/SPY:101/TLT:103/USO:107 | 98,727.75 | 1.66 | False | 2014-01-06 | 2022-12-30 | 2264 | 586 |
| S2 | 414 | GLD:103/SPY:101/TLT:103/USO:107 | 98,609.12 | 1.73 | False | 2014-01-06 | 2022-12-30 | 2264 | 586 |
| S3 | 414 | GLD:103/SPY:101/TLT:103/USO:107 | 98,486.62 | 1.81 | False | 2014-01-06 | 2022-12-30 | 2264 | 586 |

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
| `sharpe` | 0 |
| `sortino` | 0 |
| `calmar` | 0 |
| `expectancy` | 0 |
| `win_rate` | 0 |
| `correlation` | 0 |
| `covariance` | 0 |
| `pearson` | 0 |
| `effective_independent_bets` | 0 |
| `avg_pairwise_correlation` | 0 |
| `avg_pairwise_dependence` | 0 |
| `avg_pairwise_dependence_measure` | 0 |
| `daily_return` | 0 |
| `log_return` | 0 |
| `pct_return` | 0 |
| `.pct_change(` | 0 |
| `compute_return` | 0 |
| `cumulative_return` | 0 |
| `annualized_return` | 0 |
| `return_series` | 0 |
| `_returns_` | 0 |
| `_returns,` | 0 |
| `returns_total` | 0 |
| `arithmetic_return` | 0 |
| `geometric_return` | 0 |
| `Donchian` | 0 |
| `ATR(` | 0 |
| `wilder_atr` | 0 |
| `wilder_n` | 0 |
| `pyramid` | 0 |
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
| `oos_simulation` | 0 |
| `post_oos_simulation` | 0 |
| `simulate_full_window` | 0 |
| `force_oos` | 0 |

## 7. Cost baseline commentary
- Commission per share baseline (S1): **$0.00** (zero-commission ETF broker assumption per Tier-N)
- Slippage entry per share baseline (S1): **$0.01** (one ETF penny tick)
- Slippage exit per share baseline (S1): **$0.01** (one ETF penny tick)
- Stop slippage baseline: **N/A** (no hard stop in s9 mechanic)
- Borrow cost baseline: **N/A** (long-only)
- Tier scalars: see JSON `cost_baseline_commentary.tier_scalars`
- Tier S4: RESERVED — passing CostTier.S4 raises SimulatorParameterOverrideError

## 8. Boundaries held (all True)
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
 - `no_simulator_spec_modification`  
 - `no_strategy_lab_promotion`  
 - `no_tier_n_spec_modification`  
 - `no_validator_modification`  
 - `simulator_does_not_compute_aggregation_statistic`  
 - `simulator_does_not_compute_oos_simulation`  
 - `simulator_does_not_compute_pairwise_dependence_measure`  
 - `simulator_does_not_compute_post_oos_simulation`  
 - `simulator_does_not_compute_return_series`  
 - `simulator_does_not_compute_risk_adjusted_ratio`  
 - `simulator_does_not_compute_rsi`  
 - `simulator_has_no_file_io`  
 - `simulator_has_no_forbidden_import`  
 - `simulator_has_no_forbidden_token`  
 - `simulator_has_no_module_level_mutable_state`  
 - `simulator_in_sample_only_via_5_layer_enforcement`  
 - `simulator_is_pure_deterministic_function`  
 - `simulator_long_only_at_dataclass_type_level`  
 - `simulator_max_units_per_symbol_is_one_no_pyramid`  
 - `simulator_no_hard_stop_no_time_stop_no_trailing`  
 - `simulator_rejects_extra_kwargs`  
 - `simulator_uses_only_open_for_fill_close_for_mtm`  
 - `simulator_window_hardcoded_no_override_path`

## 9. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `brokerage_connection`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `downstream_aggregation_statistic_computed`  
 - `fetch_manifest_modified`  
 - `file_io_performed_by_simulator`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_simulation_executed_by_simulator`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `rsi_recomputed_by_simulator`  
 - `short_side_field_added`  
 - `signal_module_modified`  
 - `signal_spec_modified`  
 - `simulator_spec_modified`  
 - `strategy_lab_promoted`  
 - `tier_n_spec_modified`  
 - `validator_modified`  
 - `yfinance_imported_by_simulator`

## 10. API-key safety confirmation
- `any_brokerage_call_by_simulator`: **False**
- `any_file_io_by_simulator`: **False**
- `any_network_call_by_simulator`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_simulator`: **False**
- `yfinance_imported_by_simulator`: **False**

## 11. OOS protection attestation
- `no_oos_simulated`: **True**
- `no_post_oos_simulated`: **True**
- `no_oos_value_inspected_by_simulator`: **True**
- `signal_module_attestation_inherited`: **True**

## 12. Live-action blocking attestation
- `no_live_order_placed`: **True**
- `no_paper_order_placed`: **True**
- `no_brokerage_session_opened`: **True**
- `no_scheduler_invocation`: **True**
- `no_strategy_lab_promotion`: **True**
- `no_candidate_promotion`: **True**
- `no_review_queue_mutation`: **True**
- `no_production_idea_memory_mutation`: **True**
- `no_orb_branch_artifact_mutation`: **True**
- `trading_paused_unchanged`: **True**
- `live_blocked_at_six_gates_unchanged`: **True**
- `frc_never_granted`: **True**

## 13. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

