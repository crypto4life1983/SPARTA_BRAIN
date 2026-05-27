# S10-D2 P3.6 BUILD-EXTENSION: native OOS driver support

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Authored (UTC):** `2026-05-27T03:16:08.355445Z`
**Design choice:** OPTION_1_SIBLING_DRIVER
**Build verdict:** **PASS**
**Report seal sha256:** `c7d9d7888f2bc5df6850ab37f9bde0b95c3c794486382c4b0d45f32b6bd1b73d`

## Design rationale

Authored sibling file out_of_sample_driver.py via mechanical substitution from in_sample_driver.py. Preserves IS driver byte-stable on disk (P3 BUILD sha unchanged), which keeps the chain-of-custody guards across all prior phases clean. Each driver is single-purpose and the diff is fully auditable in git.

## Files authored (4)

1. `external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\out_of_sample_driver.py` — sha `7941ff28e0dbad0fae68aff3fd62b21b05fcc8fe1615c251fce1cc01858bf9b4` (34247 bytes)
2. `external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_oos_driver_invariants.py` — sha `d6769d4e76d95749feba25455dda6528c89a19321ac24cf599c99704646160d7` (8829 bytes)
3. `reports\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_out_of_sample_driver_build_report.json` (this report)
4. `reports\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_out_of_sample_driver_build_report.md` (twin)

## Mechanical substitutions applied (operational config only)

Total substitutions: 21.

- `module_docstring_header`
- `auth_comment`
- `CACHE_ROOT`
- `window_start_const_decl`
- `window_end_const_decl`
- `EXPECTED_FILES_PER_ROOT`
- `EXPECTED_CACHE_BYTES_dict_block`
- `OUTPUT_DIAGNOSTIC_JSON_path`
- `OUTPUT_DIAGNOSTIC_MD_path`
- `hard_runtime_checks_comment`
- `derive_rth_docstring_window`
- `derive_rth_date_filter`
- `run_function_def`
- `run_docstring`
- `schema_id`
- `window_key_in_return_dict`
- `main_print_1`
- `main_print_window`
- `main_print_import`
- `main_print_invocation`
- `main_print_exit`

## Operational constants changed (IS → OOS)

| Constant | IS value | OOS value |
|---|---|---|
| `CACHE_ROOT` | `…\data\databento_cache` | `…\data\databento_cache_oos` |
| `IN_SAMPLE_START` → `OUT_OF_SAMPLE_START` | `2013-01-01` | `2023-01-01` |
| `IN_SAMPLE_END` → `OUT_OF_SAMPLE_END` | `2022-12-30` | `2025-12-31` |
| `EXPECTED_FILES_PER_ROOT` | `120` | `36` |
| `EXPECTED_CACHE_BYTES` (NQ/GC/ZN/CL) | `53,148,359 / 2,162,216 / 27,939,222 / 46,540,654` | `19,770,364 / 540,803 / 8,573,282 / 13,779,406` |
| `run_in_sample` → `run_out_of_sample` | (function name) | (function name) |
| `OUTPUT_DIAGNOSTIC_JSON/MD` | `…in_sample_diagnostic_…` | `…out_of_sample_diagnostic_…` |

## Strategy parameters changed

**NONE.**

NONE — strategy parameters live in runner_main.CONFIG which is shared by both drivers. Donchian 55/20, Wilder ATR(20), 2N stop, 1% risk, max_units=1, AMB6 NONE, no-pyramid invariant, starting_cash=$500,000, S0..S4 cost tiers — ALL UNCHANGED.

## Test results

- pytest returncode:    0
- pytest wall:          0.732s
- Per-test: PASSED=19, FAILED=0, ERROR=0

| Test | Verdict |
|---|:-:|
| `test_both_drivers_share_seal_constants` | PASSED |
| `test_both_drivers_use_same_runner_main_module` | PASSED |
| `test_is_driver_source_byte_stable_through_p3_6` | PASSED |
| `test_oos_driver_cache_root_points_to_oos_dir` | PASSED |
| `test_oos_driver_databento_import_is_function_local` | PASSED |
| `test_oos_driver_does_not_have_is_window_constants` | PASSED |
| `test_oos_driver_does_not_have_run_in_sample_function` | PASSED |
| `test_oos_driver_does_not_instantiate_db_historical` | PASSED |
| `test_oos_driver_does_not_reference_is_byte_counts_in_source` | PASSED |
| `test_oos_driver_does_not_reference_is_cache_dir_in_source` | PASSED |
| `test_oos_driver_does_not_reference_is_dates_in_source` | PASSED |
| `test_oos_driver_does_not_reference_run_in_sample_anywhere` | PASSED |
| `test_oos_driver_expected_cache_bytes_match_oos` | PASSED |
| `test_oos_driver_expected_files_per_root_is_36` | PASSED |
| `test_oos_driver_no_top_level_forbidden_imports` | PASSED |
| `test_oos_driver_window_end_is_2025_12_31` | PASSED |
| `test_oos_driver_window_start_is_2023_01_01` | PASSED |
| `test_oos_run_function_signature_matches_is` | PASSED |
| `test_runner_main_config_strategy_params_unchanged` | PASSED |

## Guard byte-stability

- IS driver baseline sha (P3 BUILD): `19749ada4d98e1b2dbd7bd226699807d6e1adfbc965d033d1ac58795350f9919`
- IS driver sha right now:           `19749ada4d98e1b2dbd7bd226699807d6e1adfbc965d033d1ac58795350f9919`
- IS driver byte-stable through P3.6: **True**
- All 13 guarded source files byte-stable: **YES**

## Confirmation: strategy parameters NOT changed

- `runner_main.CONFIG['max_units_per_market']` == 1 (no-pyramid)
- `runner_main.CONFIG['starting_cash_mnq_equivalent']` == 500_000 (S10-D2 delta vs s8-D1)
- `runner_main.CONFIG['pyramid_spacing_n_multiplier']` == 0.5
- `runner_main.CONFIG['stop_n_multiplier']` == 2.0 (2N stop)
- `runner_main.CONFIG['risk_pct_per_unit']` == 0.01 (1% portfolio)
- AMB6 filter NONE preserved
- Donchian 55 entry / 20 exit preserved
- Wilder ATR(20) preserved
- S0..S4 cost stress tiers preserved

(All strategy parameters live in `runner_main.CONFIG`; both IS and OOS drivers lazy-import the same `runner_main` module, so the strategy is byte-identical across drivers by construction.)

## Confirmation: IS path remains intact

- `in_sample_driver.py` byte-sha at P3.6 end = baseline P3 BUILD sha: **True**
- `run_in_sample()` function intact in IS driver
- IS test `test_smoke_t1_t15.py` byte-stable
- IS conftest.py + 4 synthetic CSV fixtures byte-stable

## Hard boundaries held

- no_commit_in_orchestrator: True
- no_conftest_modified: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_db_historical: True
- no_execution_guard_modified: True
- no_in_sample_driver_modified: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_execution: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_runner_main_modified: True
- no_s8_d1_or_s7_d1_modified: True
- no_strategy_parameter_change: True
- no_synthetic_csv_fixtures_modified: True
- no_test_smoke_t1_t15_modified: True

## Inherited seals

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`
- `p4_smoke_seal_sha256`: `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`
- `p6_is_diagnostic_seal_sha256`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `p6_5_cost_stress_matrix_seal_sha256`: `f9a34674de4f7fdf8098b39959032d152bf2282e9ad57cedd68bc33cee2099ab`
- `p7_decision_memo_seal_sha256`: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`

## Next step

Ready for **AUTHORIZE S10-D2 P10 OOS GATE** (separately authorized; would invoke `out_of_sample_driver.run_out_of_sample(cost_tier='S1')` against the 144-file OOS cache).
