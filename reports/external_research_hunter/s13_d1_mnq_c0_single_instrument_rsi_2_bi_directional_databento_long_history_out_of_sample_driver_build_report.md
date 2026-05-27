# S13-D1 P3 BUILD out-of-sample driver report (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR`
**Authored (UTC):** `2026-05-27T17:38:00.237737Z`
**Lifecycle state:** P3_BUILD_OOS_DRIVER_REPORT_SEALED
**Report seal sha256:** `dd63e967fe70d12df56ac81cb5c85584194bb39a83288da0bd9de62974d092f6`
**Reseal verified on disk:** YES (UTF-8 explicit)

## File authored

- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/out_of_sample_driver.py` (sha `64ff35e3c04a1ba58a0a8a091c2d17a3831ee3c6daf12afc51a23ba379b10843`)

## Hardcoded constants

- `OUT_OF_SAMPLE_START` = `datetime.date(2024, 1, 2)`
- `OUT_OF_SAMPLE_END` = `datetime.date(2025, 12, 30)`
- `CSV_PATH_HARDCODED` = `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `CSV_SHA256_HARDCODED` = `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

## REC1-equivalent binding in OOS driver docstring + stub

> *"OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. ... Expected terminal verdict if K9 fires at OOS: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED."*

## Execution status

NOT_RUN at P3 BUILD. P10 OOS gate requires separate authorization AFTER P6 IS verdict ELIGIBLE_FOR_OOS: `Authorize s13 D1 MNQ.c.0 P10 OOS gate only`.

## C6 inherited_constraints_block (carried verbatim from P2)

See JSON sidecar `inherited_constraints_block_VERBATIM_FROM_P2_C6` (16 entries).

## Status

trading: PAUSED · live: BLOCKED_AT_6_GATES · lifecycle: P3_BUILD_OOS_DRIVER_REPORT_SEALED · REC1-equivalent binding: True
