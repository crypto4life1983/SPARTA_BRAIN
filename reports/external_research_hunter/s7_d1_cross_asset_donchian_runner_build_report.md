# s7 D1 — Runner Build Report (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_runner_build_report.v1`
**Status:** `SEALED`
**Candidate:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Sealed at (UTC):** `2026-05-25T15:38:54Z`
**Tier-N spec seal:** `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
**Plan-lock seal:** `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
**Phase-2 plan seal:** `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> BUILD-only. No execution, no smoke, no fetch, no backtest, no network.
> No D5 / B005_001 / NKE revival. AMB6 filter NONE invariant preserved.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Negative invariants (this turn)
- `no_runner_executed`: `True`
- `no_smoke_test_executed`: `True`
- `no_pytest_invoked`: `True`
- `no_backtest_run`: `True`
- `no_databento_call`: `True`
- `no_qc_call`: `True`
- `no_data_fetch`: `True`
- `no_real_market_data_loaded`: `True`
- `no_network_call`: `True`
- `no_live_trading`: `True`
- `no_paper_bot_change`: `True`
- `no_scheduler_change`: `True`
- `no_obsidian_trade_logger_mutation`: `True`
- `no_review_queue_mutation`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_strategy_lab_promotion`: `True`
- `no_filter_or_corr_gate_added`: `True`
- `no_threshold_loosened`: `True`
- `no_amb6_violation`: `True`
- `no_broker_or_exchange_adapter_imported_anywhere`: `True`
- `no_module_level_side_effects_in_execution_guard`: `True`

## Seal block (canonical)
- **`report_seal_sha256`**: `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_runner_build_report.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T15:38:54Z`

*End of report. BUILD-only. No execution.*
