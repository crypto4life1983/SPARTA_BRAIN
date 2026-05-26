# s9 RSI-2 Signal Module Build Report

> First signal-side code in the s9 chain. Pure deterministic
> in-memory long-only RSI-2 trigger emitter. In-sample only.
> No simulator. No backtest. No PnL. No returns. No Sharpe.
> No network. No vendor SDK. No live trading.

**Phase:** `S9_CROSS_ASSET_MEAN_REVERSION_RSI2_SIGNAL_MODULE_BUILD`
**Schema:** `sparta.s9.rsi2.signal_module_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T03:20:49Z
**Build verdict:** `PASS`

**Companion JSON:** see same path .json; sha256 + seal recorded only in JSON to break sha cycle.

---

## 0. Anchors
- Tier-N spec: sha256 `6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409`  commit `5bd8e62a1a614042a30e44f4060e54c7cdd20401`
- Signal spec: sha256 `59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9`  commit `c5393ab31a58059004b8cd337cd428eacbcbaece`
- Selection plan commit: `530b54598fa7098eb746f2122b4002db2c984422`
- Predecessor park commit: `a5ac092`
- Step 03 loader.py sha256: `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9` (reused byte-equiv)
- Step 04 validator.py sha256: `bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e` (reused byte-equiv)
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/signal.py` | 14,898 | `8776e87b3482c7f5` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/__init__.py` | 1,443 | `618a8faf6cc481dd` |
| `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/README.md` | 5,912 | `aea9d5bac3ecf4a0` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/test_signal.py` | 18,380 | `1b1bc4fd877032b9` |
| `tests/external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_signal/__init__.py` | 0 | `e3b0c44298fc1c14` |

## 2. Public API surface (V4)
Expected (13 symbols); observed `__all__` exactly matches: **True**
- `CrossSymbolSignalResult`
- `IN_SAMPLE_WINDOW`
- `RSI_EXIT_THRESHOLD`
- `RSI_LOOKBACK`
- `RSI_OVERSOLD_ENTRY_THRESHOLD`
- `SignalError`
- `SignalEvent`
- `SignalInputError`
- `SignalOosBlockedError`
- `SignalParameterOverrideError`
- `SignalResult`
- `compute_signals`
- `compute_signals_all`

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 files_exist | OK | |
| V2 AST_compiles | OK |  |
| V3 no_io_at_import | OK | |
| V4 api_surface_matches | OK | obs=13 exp=13 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_pass | OK | tests=24 f=0 e=0 s=0 |
| V8 all_T1_T16_present | OK | |
| V9 live_in_sample_round_trip | OK | T01/T02/T03/T04/T08 PASS |
| V10 negative_path | OK | T06/T07/T09 PASS |

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

## 5. Live signal summary on real ETF-proxy data

| Symbol | bars_in_window | total_signals | first_eligible | last_eligible | entry_triggers | exit_triggers |
|---|---|---|---|---|---|---|
| GLD | 2266 | 2264 | 2014-01-06 | 2022-12-30 | 280 | 1169 |
| SPY | 2266 | 2264 | 2014-01-06 | 2022-12-30 | 203 | 1381 |
| TLT | 2266 | 2264 | 2014-01-06 | 2022-12-30 | 233 | 1193 |
| USO | 2266 | 2264 | 2014-01-06 | 2022-12-30 | 284 | 1186 |

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
| `drawdown` | 0 |
| `expectancy` | 0 |
| `win_rate` | 0 |
| `correlation` | 0 |
| `covariance` | 0 |
| `pearson` | 0 |
| `effective_independent_bets` | 0 |
| `avg_pairwise_correlation` | 0 |
| `avg_pairwise_dependence_measure` | 0 |
| `pnl` | 0 |
| `profit` | 0 |
| `portfolio_equity` | 0 |
| `cash_balance` | 0 |
| `mark_to_market` | 0 |
| `position_size` | 0 |
| `position_state` | 0 |
| `pyramid_unit` | 0 |
| `stop_distance` | 0 |
| `stop_price` | 0 |
| `slippage` | 0 |
| `commission` | 0 |
| `fill_price` | 0 |
| `order_id` | 0 |
| `trade_id` | 0 |
| `gross_pnl` | 0 |
| `net_pnl` | 0 |
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
| `.rolling(` | 0 |
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
| `compute_signals_oos` | 0 |
| `simulate_oos` | 0 |
| `oos_simulation` | 0 |
| `post_oos_simulation` | 0 |

## 7. Boundaries held (all True)
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
 - `no_signal_spec_modification`  
 - `no_strategy_lab_promotion`  
 - `no_tier_n_spec_modification`  
 - `no_validator_modification`  
 - `signal_module_does_not_apply_stops`  
 - `signal_module_does_not_compute_oos_signal`  
 - `signal_module_does_not_compute_pairwise_dependence_measure`  
 - `signal_module_does_not_compute_pnl_or_returns`  
 - `signal_module_does_not_compute_post_oos_signal`  
 - `signal_module_does_not_compute_sharpe_drawdown_expectancy`  
 - `signal_module_does_not_size_positions`  
 - `signal_module_does_not_track_position_state`  
 - `signal_module_has_no_file_io`  
 - `signal_module_has_no_forbidden_import`  
 - `signal_module_has_no_forbidden_token`  
 - `signal_module_has_no_module_level_mutable_state`  
 - `signal_module_in_sample_only_via_5_layer_enforcement`  
 - `signal_module_is_pure_deterministic_function`  
 - `signal_module_long_only_at_dataclass_type_level`  
 - `signal_module_rejects_extra_kwargs_via_SignalParameterOverrideError`  
 - `signal_module_uses_only_adj_close_for_rsi`  
 - `signal_module_uses_wilder_smoothing_per_spec_section_8`  
 - `signal_module_window_hardcoded_no_override_path`

## 8. Negative invariants (all False)
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
 - `file_io_performed_by_signal`  
 - `git_pushed`  
 - `idea_memory_mutated`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_signal_computed_by_signal_module`  
 - `orb_branch_mutated`  
 - `paper_order_placed`  
 - `plan_modified`  
 - `real_order_placed`  
 - `review_queue_mutated`  
 - `short_side_field_added`  
 - `signal_spec_modified`  
 - `strategy_lab_promoted`  
 - `tier_n_spec_modified`  
 - `validator_modified`  
 - `yfinance_imported_by_signal`

## 9. API-key safety confirmation
- `any_brokerage_call_by_signal`: **False**
- `any_file_io_by_signal`: **False**
- `any_network_call_by_signal`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_signal`: **False**
- `yfinance_imported_by_signal`: **False**

## 10. OOS protection attestation
- `no_oos_signal_computed`: **True**
- `no_post_oos_signal_computed`: **True**
- `no_oos_value_inspected_by_signal_module`: **True**

## 11. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

