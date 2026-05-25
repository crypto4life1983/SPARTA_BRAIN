# s7 D1 Donchian Step 04 - Input Validator Build Report

> Build of the pure in-memory input validator over LoadedSymbol
> structures from the Step 03 loader. No file IO. No signal logic.
> No channel construction. No rolling aggregation. No returns.
> No pairwise dependence measure. OOS bar counts only.

**Phase:** `S7_D1_DONCHIAN_STEP_04_INPUT_VALIDATOR_BUILD`
**Schema:** `sparta.donchian.step_04_input_validator_build_report.v1`
**Controller session:** THIS_SESSION_ONLY
**Report date (UTC):** 2026-05-25T23:36:14Z
**Build verdict:** `PASS`

**Companion JSON:** `reports/s7_d1_cross_asset_donchian_step_04_input_validator_build_report.json` (sha256 + seal recorded only in JSON to break sha cycle; recompute from JSON bytes to verify)

---

## 0. Anchors
- Plan: `docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md` (sha256 `c1aad410b50e132540f66ee7c973048967b4f36a3cb0872bb5d55f25683466da`, commit `a5acf59f497897c0c579b584e287f0e44139e337`)
- Step 03 build report sha256: `137dd8534de840762abc9e6e3f9d22ad5314a1e6f2a4ddc783da3e90429c8386`  seal: `89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c`
- Step 03 loader.py sha256: `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9`
- Step 02c audit report sha256: `a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354`  seal: `872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f`
- audit_manifest.json sha256 pin: `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## 1. Output files
| Path | bytes | sha256 (first 16) |
|---|---|---|
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/validator.py` | 18,296 | `bae0fc410ad3d659` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/__init__.py` | 1,324 | `77796cb5f58d48e1` |
| `external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/README.md` | 4,891 | `fd71a6889e4717a3` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/test_validator.py` | 12,087 | `21c492e522c21395` |
| `tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/__init__.py` | 0 | `e3b0c44298fc1c14` |

(plus this JSON report + this MD; their shas listed at file write time)

## 2. Public API surface (V4)
Expected (alphabetical, 14 symbols):
- `CrossSymbolValidationReport`
- `DONCHIAN_ENTRY_LOOKBACK`
- `DONCHIAN_EXIT_LOOKBACK`
- `IN_SAMPLE_WINDOW`
- `OUT_OF_SAMPLE_WINDOW`
- `POST_OOS_DIAGNOSTIC_WINDOW`
- `ValidationReport`
- `ValidatorCrossSymbolAlignmentError`
- `ValidatorError`
- `ValidatorInputError`
- `WarmupInsufficientError`
- `WindowMisfitError`
- `validate_all`
- `validate_loaded_symbol`

Observed `__all__` exactly matches: **True**

## 3. V-gate results
| Gate | Result | Notes |
|---|---|---|
| V1 five_code_files_exist | OK | reports written at end of build |
| V2 validator_AST_compiles | OK |  |
| V3 import_performs_no_file_io | OK | suspect_opens=0 suspect_reads=0 |
| V4 public_api_surface_matches | OK | obs=14 exp=14 |
| V5 no_forbidden_import | OK | 0 hits |
| V6 no_forbidden_token | OK | per-token in JSON |
| V7 test_suite_all_pass | OK | tests=18 f=0 e=0 s=0 |
| V8 all_T1_T16_present | OK | |
| V9 live_round_trip | OK | T01/T02/T03/T11/T12 PASS |
| V10 negative_path | OK | T08/T09/T13 PASS |

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

## 5. Forbidden-token grep results (validator.py)
| Token | hit count |
|---|---|
| `DATABENTO_API_KEY` | 0 |
| `yfinance` | 0 |
| `yahoo_finance` | 0 |
| `requests.get` | 0 |
| `urllib.request` | 0 |
| `socket.connect` | 0 |
| `Donchian` | 0 |
| `Wilder` | 0 |
| `ATR(` | 0 |
| `rolling(` | 0 |
| `correlation` | 0 |
| `covariance` | 0 |
| `.pct_change(` | 0 |
| `log_return` | 0 |
| `ema(` | 0 |
| `sma(` | 0 |

## 6. Boundaries held (all True)
 - `build_under_operator_authorization`  
 - `no_CLAUDE_md_modification`  
 - `no_RUNBOOK_modification`  
 - `no_audit_manifest_modification`  
 - `no_backtest_run`  
 - `no_branch_change`  
 - `no_branch_created`  
 - `no_commit_beyond_seven_output_files`  
 - `no_csv_modification`  
 - `no_databento_api_key_access`  
 - `no_databento_call`  
 - `no_docs_decisions_md_modification`  
 - `no_existing_step_02b_02c_03_artifact_modification`  
 - `no_fetch_run_manifest_modification`  
 - `no_git_push`  
 - `no_gitignore_modification`  
 - `no_live_trading`  
 - `no_loader_modification`  
 - `no_network_call`  
 - `no_orb_branch_artifact_mutation`  
 - `no_paper_trade_loop`  
 - `no_pipeline_manifest_modification`  
 - `no_simulator_run`  
 - `no_source_modification_beyond_validator_package_and_tests_and_temp_script`  
 - `no_spec_modification`  
 - `no_step_04_plan_modification`  
 - `no_strategy_lab_run`  
 - `no_vendor_substitution`  
 - `no_wilder_atr_computed`  
 - `no_yahoo_finance_call`  
 - `no_yfinance_call`  
 - `validator_does_not_compute_channel`  
 - `validator_does_not_compute_pairwise_dependence`  
 - `validator_does_not_compute_returns`  
 - `validator_does_not_compute_rolling_window_aggregation`  
 - `validator_does_not_compute_smoothing_statistic`  
 - `validator_does_not_inspect_oos_numerical_values_beyond_bar_count`  
 - `validator_does_not_inspect_post_oos_numerical_values`  
 - `validator_has_no_file_io_at_all`  
 - `validator_has_no_forbidden_import`  
 - `validator_has_no_forbidden_token`  
 - `validator_has_no_module_level_file_io`  
 - `validator_is_pure_in_memory_checker`  
 - `validator_raises_on_any_refusal_mode_without_silent_skip`  
 - `validator_records_warmup_truncation_honestly`

## 7. Negative invariants (all False)
 - `audit_manifest_modified`  
 - `backtest_run`  
 - `branch_changed`  
 - `branch_created`  
 - `channel_computed`  
 - `commit_made_beyond_seven_output_files`  
 - `correlation_computed_by_validator`  
 - `covariance_computed_by_validator`  
 - `csv_modified`  
 - `databento_api_key_accessed`  
 - `databento_called`  
 - `fetch_manifest_modified`  
 - `file_io_performed_by_validator`  
 - `git_pushed`  
 - `live_trading`  
 - `loader_modified`  
 - `network_used`  
 - `oos_numerical_values_inspected_beyond_bar_count`  
 - `orb_branch_mutated`  
 - `plan_modified`  
 - `returns_computed_by_validator`  
 - `rolling_statistic_computed_by_validator`  
 - `simulator_run`  
 - `yahoo_finance_called_by_validator`  
 - `yfinance_imported_by_validator`

## 8. API-key safety confirmation
- `any_network_call_by_validator`: **False**
- `any_file_io_by_validator`: **False**
- `databento_api_key_accessed`: **False**
- `databento_called`: **False**
- `os_environ_DATABENTO_API_KEY_referenced`: **False**
- `yahoo_finance_called_by_validator`: **False**
- `yfinance_imported_by_validator`: **False**

## 9. Seal verification
```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field; this MD does not embed it to avoid sha cycle>
```

Companion JSON sha256 = <recompute sha256 of the JSON bytes on disk>

**Build verdict: `PASS`.** Trading: PAUSED. Live: BLOCKED at 6 gates.

