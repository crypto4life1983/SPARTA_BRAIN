# s8-D1 No-Pyramid - P3 Runner BUILD Report (SEALED)

**Artifact type:** `runner_build_report`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Phase:** `P3_BUILD_ONLY_SEALED_NO_RUN`
**Operational status:** `RUNNER_BUILT_NO_SMOKE_RUN_YET`
**Report date UTC:** 2026-05-25T23:36:42Z

**Runner BUILD report seal:** `e1f2a13cb860a629ba3ee87d4ddd4a61e86083be1220190ddabeaf30fcdfac32`
**Predecessor (P2 phase-2 plan) seal:** `5e6fccd1aeb40db7daf850ab60eff2947a03a082a6bcb5b332c967e2d8f9c826`
**Plan-lock seal:** `612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1`
**Tier-N spec seal:** `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P3_BUILD_REPORT_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## Files built (5 of 6 in this report; driver is sibling report)

| File | Size (bytes) | sha256 |
|---|---|---|
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/__init__.py` | 683 | `d20c34ec52c82654...` |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/main.py` | 22981 | `8c63971478459b26...` |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/execution_guard.py` | 6712 | `27c4896b41350c9d...` |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/__init__.py` | 149 | `98f5ce10556351a2...` |
| `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/tests/test_smoke_t1_t15.py` | 12726 | `594ea965cc17a58a...` |

## Single delta from s7-D1 runner

- Parameter: `max_units_per_market`
- s7-D1: **4** -> s8-D1: **1**
- Derived: portfolio_cap_max_units 16 -> 4
- PortfolioCapTracker gained `per_market_cap` kwarg (default 1)
- All other strategy parameters byte-equivalent

## s7-D1 revival attestation

- s7-D1 chain status: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- s7-D1 revived by this build: **False**
- s7-D1 used as: STRUCTURAL BASELINE FOR S8-D1 NAMESPACE REWRITE ONLY
- s7-D1 runner files modified by this build: **[]**

## Static validation results (all pass)

| File | ast.parse | compile | module clean | forbidden top imports |
|---|---|---|---|---|
| `__init__.py` | True | True | True | [] |
| `main.py` | True | True | True | [] |
| `execution_guard.py` | True | True | True | [] |
| `tests/__init__.py` | True | True | True | [] |
| `tests/test_smoke_t1_t15.py` | True | True | True | [] |

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

*End of s8-D1 P3 runner BUILD report.*
