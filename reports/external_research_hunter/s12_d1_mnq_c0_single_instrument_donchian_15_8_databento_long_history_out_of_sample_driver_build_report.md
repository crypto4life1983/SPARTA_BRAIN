# S12-D1 P3 BUILD out-of-sample driver report (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Authored (UTC):** `2026-05-27T15:27:22.996670Z`
**Lifecycle state:** P3_BUILD_OOS_DRIVER_REPORT_SEALED
**Report seal sha256:** `30fbfbd113d64d01dfcb95645b3f70310ba5d31cdb7e49640a4c99efd0ebc946`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Build scope

`out_of_sample_driver.py` structural skeleton + hardcoded OOS-window constants + CSV sha pin + stub `run_out_of_sample` that raises at P3 BUILD + REC1 binding reminder in docstring.

## File authored

- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/out_of_sample_driver.py` (sha `65ba90f9e22695f250a3ee6402f52be410e618356e636072acd80809387ea91e`)

## Hardcoded constants

| Constant | Value |
|---|---|
| `OUT_OF_SAMPLE_START` | `datetime.date(2024, 1, 2)` |
| `OUT_OF_SAMPLE_END` | `datetime.date(2025, 12, 30)` |
| `CSV_PATH_HARDCODED` | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| `CSV_SHA256_HARDCODED` | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |

## OOS driver invariants (per P1 §10; tests AUTHORED at P3 BUILD, not run)

12 invariants tests in `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py` covering: cache path, window start/end, no IS constants leak, no IS-date references in source (word-boundary regex; CSV filename embed exempt), no `run_in_sample`, both drivers share main, CONFIG strategy params unchanged, signature compat, no top-level forbidden imports, databento function-local only, no `db.Historical()` instantiation.

## REC1 binding (verbatim in OOS driver docstring + stub)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

## Execution status

NOT_RUN at P3 BUILD. P10 OOS gate requires separate operator authorization AFTER P6 IS verdict ELIGIBLE_FOR_OOS: `Authorize s12 D1 MNQ.c.0 P10 OOS gate only`. **Expected terminal verdict per REC1: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** (analogous to S10-D2 P11 PARK at `23c7164`).

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| lifecycle_state | P3_BUILD_OOS_DRIVER_REPORT_SEALED |
| rec1_oos_k9_risk_disclosure_binding | True |
