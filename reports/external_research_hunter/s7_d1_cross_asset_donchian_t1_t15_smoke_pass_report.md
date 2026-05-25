# s7 D1 -- T1-T15 Smoke Pass Report (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_t1_t15_smoke_pass_report.v1`
**Status:** `SEALED`
**Candidate:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Operational status:** `T1_T15_SYNTHETIC_SMOKE_PASS`
**Sealed at (UTC):** `2026-05-25T16:04:10Z`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Tier-N spec seal:** `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
**Plan-lock seal:** `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
**Phase-2 plan seal:** `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
**Runner build report seal:** `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
**Execution guard build report seal:** `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> Synthetic smoke only. No real market data. No Databento. No QC. No network. No backtest.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## pytest invocation
- Command: `C:\SPARTA_BRAIN\.venv\Scripts\python.exe -m pytest external_research_hunter\s7_d1_cross_asset_donchian_runner_harness\tests\test_smoke_t1_t15.py -v --rootdir C:\SPARTA_BRAIN --tb=short -p no:cacheprovider`
- Started: `2026-05-25T16:04:09Z`
- Ended:   `2026-05-25T16:04:10Z`
- Exit code: `0`
- Summary: `15 passed in 0.05s`
- stdout sha256: `0f723de6d3762c3ca3774e26bb6bafb0bd90993f4ce077e299c59093e98f4e32`
- stderr sha256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Per-test T1-T15 results (all PASSED)
- `test_t1_*`: [OK] `test_t1_module_imports_clean`
- `test_t2_*`: [OK] `test_t2_runner_class_instantiable`
- `test_t3_*`: [OK] `test_t3_wilder_atr_synthetic`
- `test_t4_*`: [OK] `test_t4_donchian_55_20_synthetic`
- `test_t5_*`: [OK] `test_t5_entry_trigger_synthetic_breakout`
- `test_t6_*`: [OK] `test_t6_stop_placement_at_2n`
- `test_t7_*`: [OK] `test_t7_pyramid_trigger_at_05n`
- `test_t8_*`: [OK] `test_t8_exit_on_donchian_20_reversal`
- `test_t9_*`: [OK] `test_t9_portfolio_cap_uses_unit_count_not_contract_count`
- `test_t10_*`: [OK] `test_t10_sizing_1pct_floor`
- `test_t11_*`: [OK] `test_t11_skip_when_contract_count_lt_one`
- `test_t12_*`: [OK] `test_t12_rth_only_filter_attested`
- `test_t13_*`: [OK] `test_t13_roll_cost_modeled_1_spread_tick`
- `test_t14_*`: [OK] `test_t14_cost_stress_matrix_S0_S1_S2_S3_S4`
- `test_t15_*`: [OK] `test_t15_validator_harness_pass_on_synthetic`

**All 15 T-gates passed: `True`**

## Fixture attestation (SYNTHETIC_PHASE2_SMOKE_FIXTURE marker required)
- `nq`: rows=80  all_marked=True  byte_sha=364e3ab8c12ed201...
- `gc`: rows=80  all_marked=True  byte_sha=9f6f74fe2eb9f52f...
- `zn`: rows=80  all_marked=True  byte_sha=a6fcf84092aa7099...
- `cl`: rows=80  all_marked=True  byte_sha=eb0dd762aed692af...

## Obsidian-trade-logger baseline preserved
- start == end: **True**

## Negative invariants (this turn -- all True)
- `no_real_market_data_loaded`: `True`
- `no_databento_call`: `True`
- `no_qc_call`: `True`
- `no_qc_submit`: `True`
- `no_network_call`: `True`
- `no_data_fetch`: `True`
- `no_in_sample_run`: `True`
- `no_oos_inspection`: `True`
- `no_real_backtest`: `True`
- `no_obsidian_trade_logger_mutation`: `True`
- `no_review_queue_mutation`: `True`
- `no_paper_bot_change`: `True`
- `no_live_trading`: `True`
- `no_scheduler_change`: `True`
- `no_broker_or_exchange_adapter_imported`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_threshold_loosened`: `True`
- `amb6_filter_none_invariant_preserved`: `True`
- `no_profitability_claim`: `True`
- `no_code_patched_in_response_to_failure`: `True`
- `data_broker_keys_wiped_from_subprocess_env`: `True`
- `synthetic_fixture_marker_enforced`: `True`

## What this smoke pass does NOT authorize
- P5 operator-side Databento fetch is operator-managed; this report does NOT trigger it.
- P6 in-sample run requires separate operator authorization.
- P7 in-sample decision memo requires separate operator authorization.
- P8 lifecycle transition requires separate operator authorization.
- OOS inspection blocked until in-sample passes.
- Live trading permanently `BLOCKED_AT_6_GATES`.

## Next step
- `operator_managed_databento_fetch_P5_then_separate_in_sample_run_authorization_P6`

## Seal block (canonical)
- **`report_seal_sha256`**: `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_t1_t15_smoke_pass_report.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T16:04:10Z`

*End of report.*
