# S12-D1 P3 BUILD in-sample driver report (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Authored (UTC):** `2026-05-27T15:27:22.996670Z`
**Lifecycle state:** P3_BUILD_IS_DRIVER_REPORT_SEALED
**Report seal sha256:** `e3b09d662ff610cf912cca14d2d54552bbfbda7814038dc7721a540c1659379c`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Build scope

`in_sample_driver.py` structural skeleton + hardcoded IS-window constants + CSV sha pin + stub `run_in_sample` that raises at P3 BUILD (P6 IS execution requires separate operator authorization).

## File authored

- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/in_sample_driver.py` (sha `d9cbe86a6c59b8b4732e0fd114948a48deafcc1fbb21c5fe7a9d71b85d62bff5`)

## Hardcoded constants

| Constant | Value |
|---|---|
| `IN_SAMPLE_START` | `datetime.date(2019, 5, 13)` |
| `IN_SAMPLE_END` | `datetime.date(2023, 12, 29)` |
| `CSV_PATH_HARDCODED` | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| `CSV_SHA256_HARDCODED` | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |

## Invariants

- `is_window_constants_hardcoded`: True
- `csv_sha256_pinned`: True
- `csv_path_pinned`: True
- `run_in_sample_is_stub_raises_at_p3`: True (raises `P6_IS_NOT_AUTHORIZED`)
- `no_databento_import_at_module_level`: True
- `no_qc_runtime_dependency_at_module_level`: True

## Execution status

NOT_RUN at P3 BUILD. P6 IS diagnostic requires separate operator authorization: `Authorize s12 D1 MNQ.c.0 P6 IS diagnostic only`.

## REC1 inherited_constraints_block (carried byte-equivalent; binding)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| lifecycle_state | P3_BUILD_IS_DRIVER_REPORT_SEALED |
