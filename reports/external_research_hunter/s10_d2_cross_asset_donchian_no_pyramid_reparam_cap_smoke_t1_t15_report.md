# S10-D2 P4 T1-T15+T7b+T7c synthetic smoke run report

**Candidate:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC`
**Authored (UTC):** `2026-05-27T01:22:52.790191Z`
**Overall verdict:** **PASS_16_OF_17_PLUS_T7B**
**Pytest summary:** `============================= 17 passed in 0.04s ==============================`
**Wall time:** 0.669s
**Returncode:** 0
**Report seal sha256:** `c31ded81f9a2883586883aadda4d64d629a047917fcebd56169ca42eccf4fdde`

## Per-test verdicts

| Test | Verdict |
|---|:-:|
| `test_t1_module_imports_clean` | PASSED |
| `test_t2_runner_class_instantiable` | PASSED |
| `test_t3_wilder_atr_synthetic` | PASSED |
| `test_t4_donchian_55_20_synthetic` | PASSED |
| `test_t5_entry_trigger_synthetic_breakout` | PASSED |
| `test_t6_stop_placement_at_2n` | PASSED |
| `test_t7_pyramid_trigger_at_05n` | PASSED |
| `test_t7b_add_pyramid_unit_raises_under_max_units_1` | PASSED |
| `test_t7c_starting_cash_invariant_500000` | PASSED |
| `test_t8_exit_on_donchian_20_reversal` | PASSED |
| `test_t9_portfolio_cap_uses_unit_count_not_contract_count` | PASSED |
| `test_t10_sizing_1pct_floor` | PASSED |
| `test_t11_skip_when_contract_count_lt_one` | PASSED |
| `test_t12_rth_only_filter_attested` | PASSED |
| `test_t13_roll_cost_modeled_1_spread_tick` | PASSED |
| `test_t14_cost_stress_matrix_S0_S1_S2_S3_S4` | PASSED |
| `test_t15_validator_harness_pass_on_synthetic` | PASSED |

**Counts:** passed=17, failed=0, errored=0, skipped=0, expected_total=17

## Pytest invocation

```
C:\Users\mahmo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest C:\SPARTA_BRAIN\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py -v --no-header --tb=short -p no:cacheprovider --rootdir C:\SPARTA_BRAIN\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests --confcutdir C:\SPARTA_BRAIN\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests --import-mode=importlib
```

- `cwd` = `C:\SPARTA_BRAIN`
- env guards: NO_PROXY=*, HTTP(S)_PROXY=invalid, DATABENTO_API_KEY popped

## Pytest stdout (inlined)

```
============================= test session starts =============================
collecting ... collected 17 items

external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t1_module_imports_clean PASSED [  5%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t2_runner_class_instantiable PASSED [ 11%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t3_wilder_atr_synthetic PASSED [ 17%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t4_donchian_55_20_synthetic PASSED [ 23%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t5_entry_trigger_synthetic_breakout PASSED [ 29%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t6_stop_placement_at_2n PASSED [ 35%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t7_pyramid_trigger_at_05n PASSED [ 41%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t7b_add_pyramid_unit_raises_under_max_units_1 PASSED [ 47%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t7c_starting_cash_invariant_500000 PASSED [ 52%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t8_exit_on_donchian_20_reversal PASSED [ 58%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t9_portfolio_cap_uses_unit_count_not_contract_count PASSED [ 64%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t10_sizing_1pct_floor PASSED [ 70%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t11_skip_when_contract_count_lt_one PASSED [ 76%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t12_rth_only_filter_attested PASSED [ 82%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t13_roll_cost_modeled_1_spread_tick PASSED [ 88%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t14_cost_stress_matrix_S0_S1_S2_S3_S4 PASSED [ 94%]
external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness\tests\test_smoke_t1_t15.py::test_t15_validator_harness_pass_on_synthetic PASSED [100%]

============================= 17 passed in 0.04s ==============================
```

## Pytest stderr (inlined)

```
(empty)
```

## Guard byte-stability

All 17 guarded files byte-stable across the run (0 drift):

- S10-D2 source + test scaffold (11 files)
- S8-D1 source files (3 files)
- S7-D1 source files (3 files)

## Hard boundaries held

- no_backtest: True
- no_broker_adapter_touched: True
- no_commit: True
- no_d5_b005_001_nke_revival: True
- no_databento_api_call: True
- no_db_historical: True
- no_fetch: True
- no_in_sample_driver_run: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_inspection: True
- no_paper_trading: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_real_dbn_decode: True
- no_review_queue_mutation: True
- no_s8_d1_or_s7_d1_modified: True
- no_scheduler_change: True
- no_source_file_modification: True

## Inherited seals

- `tier_n_spec_seal_sha256`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal_sha256`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal_sha256`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_build_runner_report_seal_sha256`: `1eb04aa312f4053134c1e9387be7716aa4564c019168ee2cedcf789063d96405`
- `p3_build_in_sample_driver_report_seal_sha256`: `ddd604c96508a0ab835bcbae6e72fabc2993cd3f0dc459898ca326617dd96443`
- `p3_5_scaffold_completion_report_seal_sha256`: `66d38f359b54882b3107c4ad4291673d63f05f5b0d3daa19088b4a4c76469261`

## Next step

AUTHORIZE COMMIT ONLY - S10-D2 P4 smoke run files (2 files via pathspec)
