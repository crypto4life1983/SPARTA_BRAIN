# s7 D1 -- In-Sample Driver Build Report (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_driver_build_report.v1`
**Status:** `SEALED`
**Candidate operational status:** `IN_SAMPLE_DRIVER_BUILD_COMPLETE_NOT_EXECUTED`
**Sealed at (UTC):** `2026-05-25T19:03:42Z`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Tier-N spec seal:** `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
**Plan-lock seal:** `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
**Phase-2 plan seal:** `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
**Runner build report seal:** `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
**Execution guard build report seal:** `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
**Smoke pass report seal:** `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
**Blocked report seal:** `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> PATCH-only. No driver execution. No DBN decode. No backtest.
> No Databento API/network call. No QC call. No live/paper trading.
> No D5 / B005_001 / NKE revival. AMB6 filter NONE invariant preserved.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Driver file
- Path:        `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py`
- Size:        32,601 bytes
- Lines:       647
- byte sha256: `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`

## Static validation
- `ast.parse()` ok:                            **True**
- `compile()` ok:                              **True**
- Forbidden imports found:                     `[]`
- Forbidden imports pass:                      **True**
- No module-level side effects:                **True**
- Top-level side-effects observed:             `[]`

## Databento usage attestation
- Databento import locations:                  `[{'line': 173, 'kind': 'import'}]`
- All databento imports are lazy (inside functions): **True**
- `db.Historical` client invoked anywhere:     **False**
- `db.DBNStore.from_file` used for local decode: **True**

## Required functions
- Present: `['assert_cache_complete', 'assert_seal_inheritance', 'derive_rth_daily_bars', 'iterate_market_minute_bars', 'load_dbn_local', 'run_in_sample']`
- Missing: `[]`
- All required present: **True**

## Inheritance attestations (strings appear in driver source)
- AMB6 filter NONE mentioned:           **True**
- s6 cap-bugfix attested:               **True**
- Embedded tier_n_spec seal:            **True**
- Embedded plan_lock seal:              **True**
- Embedded phase2_plan seal:            **True**
- Embedded runner_build seal:           **True**
- Embedded execution_guard_build seal:  **True**
- Embedded smoke_pass seal:             **True**
- Embedded blocked_report seal:         **True**

## Existing runner files unchanged
- All 12 already-committed files byte-unchanged: **True**
- Modified files (must be empty):                `[]`

## Obsidian-trade-logger baseline preserved
- start == end: **True**

## Negative invariants (this turn -- all False / pass)
- `driver_executed`: `False`
- `driver_imported_for_runtime_check`: `False`
- `pytest_invoked`: `False`
- `p6_p6_5_run`: `False`
- `backtest_run`: `False`
- `databento_api_call`: `False`
- `databento_historical_client_invoked`: `False`
- `databento_fetch`: `False`
- `dbn_decode_executed`: `False`
- `real_market_data_loaded_this_turn`: `False`
- `qc_call`: `False`
- `qc_cloud_submit`: `False`
- `network_call`: `False`
- `k_criteria_evaluated`: `False`
- `a_gates_evaluated`: `False`
- `yfinance_used`: `False`
- `broker_or_exchange_adapter_imported`: `False`
- `live_trading`: `False`
- `paper_bot_changed`: `False`
- `scheduler_changed`: `False`
- `obsidian_trade_logger_mutation`: `False`
- `review_queue_mutation`: `False`
- `d5_revived`: `False`
- `b005_001_revived`: `False`
- `nke_revived`: `False`
- `any_committed_file_modified`: `False`
- `threshold_loosened`: `False`
- `amb6_filter_none_invariant_violated`: `False`
- `profitability_claim_made`: `False`

## Authorization gates
- P3.5 authorizes nothing downstream: **True**
- P6.5 in-sample run requires separate operator authorization: **True**

## Future P6.5 output paths (declared in driver; will be written when P6.5 is authorized)
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed.md`

## Next step
- `operator_authorization_required_for_in_sample_run_P6_5`

## Seal block (canonical)
- **`report_seal_sha256`**: `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_driver_build_report.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T19:03:42Z`

*End of report. PATCH-only. No driver execution. No DBN decode. No backtest.*
