# s8-D1 No-Pyramid - P3 In-Sample Driver BUILD Report (SEALED)

**Artifact type:** `in_sample_driver_build_report`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Phase:** `P3_BUILD_ONLY_SEALED_NO_RUN`
**Operational status:** `DRIVER_BUILT_NO_SMOKE_NO_IN_SAMPLE_RUN_YET`
**Report date UTC:** 2026-05-25T23:36:42Z

**Driver BUILD report seal:** `d7b82d7adad62979806abbeaa7c7b6b1a20c8388defdb31f6f15b4845089ed52`
**Predecessor (runner BUILD report) seal:** `e1f2a13cb860a629ba3ee87d4ddd4a61e86083be1220190ddabeaf30fcdfac32`
**Phase-2 plan seal:** `5e6fccd1aeb40db7daf850ab60eff2947a03a082a6bcb5b332c967e2d8f9c826`
**Plan-lock seal:** `612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1`
**Tier-N spec seal:** `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4`

---

## Driver file

| Path | Size | sha256 |
|---|---|---|
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/in_sample_driver.py` | 34039 | `129411e90fba23ff...` |

## Mechanical baseline inheritance from s7-D1 patched driver

- s7-D1 patched driver path: `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/in_sample_driver.py`
- s7-D1 patched driver sha256: `8741bc5182e22733...`
- s7-D1 driver NOT modified by this build: **True**

**Deltas from s7-D1 patched driver:**

- namespace identifiers (s7_d1 -> s8_d1_no_pyramid)
- sealed-chain anchor shas (point to s8-D1 chain seals)
- removed runner_build/execution_guard_build/smoke_pass/blocked seal anchors (do not exist for s8 yet)
- PortfolioCapTracker per_market_cap=1 kwarg
- safety_warnings dict includes new per_market_unit_count_invariant_violation_count
- metrics block adds no_pyramid_attestation
- return dict adds safety_diagnostics.per_market_unit_count_invariant_violation_count and no_pyramid_attestation
- negative_invariants adds no_pyramid_invariant_held and max_units_per_market_equals_1
- docstring + __main__ informational text updated for s8-D1 no-pyramid

## Single delta from s7-D1 (strategy-level)

- Parameter: `CONFIG['max_units_per_market']`
- s7-D1: **4** -> s8-D1: **1**
- Delta propagated via runner_main.CONFIG (driver does NOT override)

## Lazy databento attestation

- `databento_imported_at_module_top`: False
- `databento_imported_inside_load_dbn_local_function_only`: True
- `db_DBNStore_from_file_used`: True
- `db_Historical_used_anywhere`: False
- `no_databento_api_call_in_local_path`: True

## Static validation results

- `ast.parse`: True
- `compile`: True
- module-level clean: True
- forbidden top-level imports: []
- `databento` at module level: False
- `databento` at function level only: True

## Boundaries held (BUILD-only turn)

- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_broker_adapter_imported`: True
- `no_d5_revival`: True
- `no_databento_call`: True
- `no_db_historical_instantiated`: True
- `no_dbn_decoded`: True
- `no_fetch`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_pytest_run`: True
- `no_qc_call`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_smoke_run`: True

---

*End of s8-D1 P3 in-sample driver BUILD report.*
