# s8-D1 No-Pyramid - P4 T1-T15+T7b Smoke PASS Report (SEALED)

**Artifact type:** `smoke_pass_report`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Phase:** `P4_SMOKE_PASS_SEALED_IN_SAMPLE_NOT_AUTHORIZED`
**Operational status:** `SMOKE_PASSED_READY_FOR_P6_IF_OPERATOR_AUTHORIZES`
**Report date UTC:** 2026-05-25T23:47:08Z

**Smoke report seal:** `1ab57a67f1a81be57a0f084f8fb4c6bc1fcc72de750839728a2787dcc5d0d361`
**Predecessor (in_sample_driver_build_report) seal:** `d7b82d7adad62979806abbeaa7c7b6b1a20c8388defdb31f6f15b4845089ed52`
**Runner BUILD report seal:** `e1f2a13cb860a629ba3ee87d4ddd4a61e86083be1220190ddabeaf30fcdfac32`
**Phase-2 plan seal:** `5e6fccd1aeb40db7daf850ab60eff2947a03a082a6bcb5b332c967e2d8f9c826`
**Plan-lock seal:** `612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1`
**Tier-N spec seal:** `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P4_SMOKE_REPORT_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## Pytest invocation

- Command: `C:\Users\mahmo\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pytest external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/test_smoke_t1_t15.py -v --no-header --tb=short`
- cwd: `C:\SPARTA_BRAIN`
- exit_code: **0**
- duration: **0.797s**
- summary line: `============================= 16 passed in 0.05s ==============================`

## Per-test outcomes (T1-T15 + T7b)

| Test | Outcome |
|---|---|
| `test_t1_module_imports_clean` | **PASSED** |
| `test_t2_runner_class_instantiable` | **PASSED** |
| `test_t3_wilder_atr_synthetic` | **PASSED** |
| `test_t4_donchian_55_20_synthetic` | **PASSED** |
| `test_t5_entry_trigger_synthetic_breakout` | **PASSED** |
| `test_t6_stop_placement_at_2n` | **PASSED** |
| `test_t7_pyramid_trigger_at_05n` | **PASSED** |
| `test_t7b_add_pyramid_unit_raises_under_max_units_1` | **PASSED** |
| `test_t8_exit_on_donchian_20_reversal` | **PASSED** |
| `test_t9_portfolio_cap_uses_unit_count_not_contract_count` | **PASSED** |
| `test_t10_sizing_1pct_floor` | **PASSED** |
| `test_t11_skip_when_contract_count_lt_one` | **PASSED** |
| `test_t12_rth_only_filter_attested` | **PASSED** |
| `test_t13_roll_cost_modeled_1_spread_tick` | **PASSED** |
| `test_t14_cost_stress_matrix_S0_S1_S2_S3_S4` | **PASSED** |
| `test_t15_validator_harness_pass_on_synthetic` | **PASSED** |

Tests detected: 16 / expected 16. All passed: **True**.

## Fixtures

- `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/fixtures/synthetic_nq_daily.csv` -- 5499 bytes, sha=`d906f00cf4f395a3...`
- `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/fixtures/synthetic_gc_daily.csv` -- 5259 bytes, sha=`c77c04921dbaf479...`
- `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/fixtures/synthetic_zn_daily.csv` -- 5019 bytes, sha=`bde24035c9c8fa35...`
- `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/fixtures/synthetic_cl_daily.csv` -- 4779 bytes, sha=`3bbe0eb8535f90ec...`
- `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/conftest.py` -- 351 bytes, sha=`4fa1e131e951f947...`

All fixtures carry the `SYNTHETIC_PHASE2_SMOKE_FIXTURE` marker (refused to load otherwise by the test).

## No-pyramid attestation at smoke

- `test_t7b_add_pyramid_unit_raises_under_max_units_1` present: **True**
- CONFIG max_units_per_market == 1 (asserted via T1/T2): True

## Negative invariants this turn

- `no_b005_001_revival`: True
- `no_d5_revival`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_dbn_decode`: True
- `no_frc_granted`: True
- `no_in_sample_driver_run_in_sample_invoked`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_call`: True
- `no_real_market_data`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True

---

## Next step

> **AUTHORIZE S8-D1 P6 in-sample run** -- invoke `in_sample_driver.run_in_sample(cost_tier='S1')` on the operator-confirmed local Databento cache (re-used from s7-D1 P5; 480 files, 129,789,451 bytes). Expected ~4-minute runtime.

*End of s8-D1 P4 smoke pass report.*
