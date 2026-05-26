# s7 D1 Donchian Step 05 - Signal Module Build Report

> BOUNDARY-CROSSING BUILD. First signal-side module in the chain.
> Pure deterministic in-memory channel breakout trigger detector
> over LoadedSymbol from Step 03 loader. In-sample only. No
> simulator, no result-aggregation, no execution-side cost, no
> performance statistic. No file IO. No network. No vendor SDK.

**Phase:** `S7_D1_DONCHIAN_STEP_05_SIGNAL_MODULE_BUILD`
**Schema:** `sparta.donchian.step_05_signal_module_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-26T00:05:41Z
**Build verdict:** `PASS`

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_step_05_signal_module_build_report.json` (sha256 + seal recorded only in JSON; recompute from JSON bytes to verify)

---

## 0. Anchors
- Plan: `docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md` (sha256 `6e039d352af7a7f20c99b1e26173f07539417a7f65b3c458458aa3ca1c8e2ff4`, commit `7e76bb785fa9f75b9fa483e26e6b826cde244851`)
- Step 04 validator build sha256: `fbabd75ea7ce1914ece7a7fda8c957c9e22899538321c180e7c37c378feedd27` seal: `737a3f54b0a380e1c298a83a9fb8183b0fbdba23b42fa002a2b7fe0d9883ba3f`
- Step 04 validator.py sha256: `bae0fc410ad3d659be3b1ada2137e64988de41ab2e2d03cd13f5e751827c998e`
- Step 03 loader build sha256: `137dd8534de840762abc9e6e3f9d22ad5314a1e6f2a4ddc783da3e90429c8386` seal: `89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c`
- Step 03 loader.py sha256: `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9`
- Step 02c audit sha256: `a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354` seal: `872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f`
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/signal.py` | 12,418 | `67c88d9aba58ae28` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/__init__.py` | 1,174 | `71a49db76a3a8463` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/README.md` | 5,703 | `b53b1cd039ca52aa` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/test_signal.py` | 16,382 | `7b9926ecd9f513ed` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_signal/__init__.py` | 0 | `e3b0c44298fc1c14` |

## 2. Public API surface (V4)
Expected (12 symbols):
- `CrossSymbolSignalResult`
- `ENTRY_CHANNEL_LOOKBACK`
- `EXIT_CHANNEL_LOOKBACK`
- `IN_SAMPLE_WINDOW`
- `SignalError`
- `SignalEvent`
- `SignalInputError`
- `SignalOosBlockedError`
- `SignalParameterOverrideError`
- `SignalResult`
- `compute_signals`
- `compute_signals_all`

Observed `__all__` exactly matches: **True**

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 five_code_files_exist | OK | reports written at end |
| V2 signal_AST_compiles | OK |  |
| V3 import_performs_no_file_io | OK | suspect_opens=0 suspect_reads=0 |
| V4 public_api_surface_matches | OK | obs=12 exp=12 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_all_pass | OK | tests=24 f=0 e=0 s=0 |
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

## 5. Forbidden-token grep results (signal.py); each shows hit count
| Token | hit count |
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
| `backtest` | 0 |
| `portfolio` | 0 |
| `pnl` | 0 |
| `profit` | 0 |
| `sharpe` | 0 |
| `sortino` | 0 |
| `calmar` | 0 |
| `drawdown` | 0 |
| `correlation` | 0 |
| `covariance` | 0 |
| `brokerage` | 0 |
| `Strategy Lab` | 0 |
| `review_queue` | 0 |
| `live trading` | 0 |
| `live_trading` | 0 |
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
| `Wilder` | 0 |
| `ATR(` | 0 |
| `.rolling(` | 0 |
| `wilder_atr` | 0 |
| `wilder_n` | 0 |
| `position_size` | 0 |
| `position_state` | 0 |
| `unit_count` | 0 |
| `pyramid_unit` | 0 |
| `stop_distance` | 0 |
| `stop_price` | 0 |
| `slippage` | 0 |
| `commission` | 0 |
| `fill_price` | 0 |
| `order_id` | 0 |
| `trade_id` | 0 |

## 6. Boundaries held (all True)
 - `build_under_operator_authorization`  
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_audit_manifest_modification`  
 - `no_backtest_run_in_this_build`  
 - `no_branch_change`  
 - `no_branch_created`  
 - `no_commit_beyond_seven_output_files`  
 - `no_csv_modification`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_docs_decisions_md_modification`  
 - `no_existing_step_02b_02c_03_04_artifact_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_idea_memory_mutation`  
 - `no_live_trading`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_oos_inspection_authorized`  
 - `no_orb_branch_artifact_mutation`  
 - `no_pipeline_manifest_modification`  
 - `no_review_queue_mutation`  
 - `no_simulator_run_in_this_build`  
 - `no_source_modification_beyond_signal_package_and_tests_and_temp_script`  
 - `no_spec_modification`  
 - `no_step_05_plan_modification`  
 - `no_strategy_lab_run`  
 - `no_validator_modification`  
 - `no_vendor_substitution`  
 - `no_yahoo_finance_call`  
 - `no_yfinance_call`  
 - `signal_module_does_not_aggregate_at_portfolio_level_intentional_word_choice_avoided_in_source`  
 - `signal_module_does_not_apply_filter_or_regime_gate`  
 - `signal_module_does_not_compute_entry_timing`  
 - `signal_module_does_not_compute_execution_costs`  
 - `signal_module_does_not_compute_fills`  
 - `signal_module_does_not_compute_oos_channel_value_for_oos_bar`  
 - `signal_module_does_not_compute_oos_signal`  
 - `signal_module_does_not_compute_pairwise_dependence_measures`  
 - `signal_module_does_not_compute_performance_statistics`  
 - `signal_module_does_not_compute_post_oos_signal`  
 - `signal_module_does_not_compute_pyramid_step`  
 - `signal_module_does_not_compute_returns`  
 - `signal_module_does_not_compute_sizing`  
 - `signal_module_does_not_compute_stops`  
 - `signal_module_does_not_compute_wilder_atr`  
 - `signal_module_does_not_perform_parameter_optimization_or_search`  
 - `signal_module_does_not_track_position_state`  
 - `signal_module_has_no_file_io_at_all`  
 - `signal_module_has_no_forbidden_import`  
 - `signal_module_has_no_forbidden_token`  
 - `signal_module_has_no_module_level_file_io`  
 - `signal_module_is_pure_deterministic_function`  
 - `signal_module_uses_high_low_columns_only_for_channels`  
 - `signal_module_window_is_hardcoded_no_override_path`

## 7. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `channel_value_computed_for_oos_bar`  
 - `commit_made_beyond_seven_output_files`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `fetch_manifest_modified`  
 - `file_io_performed_by_signal_module`  
 - `git_pushed`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_signal_computed_by_signal_module`  
 - `orb_branch_mutated`  
 - `pairwise_dependence_measure_computed`  
 - `plan_modified`  
 - `post_oos_signal_computed_by_signal_module`  
 - `returns_computed_by_signal_module`  
 - `review_queue_mutated`  
 - `rolling_aggregation_computed_via_pandas_rolling_api`  
 - `simulator_run`  
 - `strategy_lab_run`  
 - `validator_modified`  
 - `wilder_atr_computed_by_signal_module`  
 - `yahoo_finance_called_by_signal_module`  
 - `yfinance_imported_by_signal_module`

## 8. API-key safety confirmation
- `any_file_io_by_signal`: **False**
- `any_network_call_by_signal`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_signal`: **False**
- `yfinance_imported_by_signal`: **False**

## 9. Out-of-sample protection attestation
- `no_oos_signal_computed`: **True**
- `no_post_oos_signal_computed`: **True**
- `no_oos_value_inspected_by_signal_module`: **True**

## 10. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

