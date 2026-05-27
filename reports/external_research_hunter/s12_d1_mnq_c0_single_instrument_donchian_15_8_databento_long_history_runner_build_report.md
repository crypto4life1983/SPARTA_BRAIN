# S12-D1 P3 BUILD runner harness report (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Authored (UTC):** `2026-05-27T15:27:22.996670Z`
**Lifecycle state:** P3_BUILD_RUNNER_REPORT_SEALED
**Report seal sha256:** `0bbcf04cb48ec4f4989aa105b033a29d7cc20e3a09351947ce93534694115c15`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Build scope

Runner harness package source + test scaffold + synthetic fixture authored at P3 BUILD. **NO execution, NO signal computation, NO backtest, NO P4 smoke run** by this BUILD turn.

## Files authored (5 source/init + 5 test scaffold = 10 files this report covers)

### Runner harness source (3)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/__init__.py` (sha `5ab60a22596596a8c4a28b3e50162568b60aa92811e54f9d59b0deb3eb8c866c`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/main.py` (sha `602dbdcf3afec7bbb0f2ca2be3af9539862b255f224aba93eed8c49072dc9a81`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/execution_guard.py` (sha `86107392173445bddaeea9fbcdd3d314bcbc0c9c61636408f73a0cd356ad4b42`)

### Test scaffold (5)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/__init__.py` (sha `b5abb6d33fe95a965994330c6ef5bff928ba0ab89ee67da0f812f00856b6e518`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/conftest.py` (sha `b0ea29c0c712bfba06e7c632cc1c3985511873cc5fc9cc41578e2d71afb95bc3`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv` (sha `72a92ed98943eb6b7e6d8191266ea6d209d43e05629a44fa8c1bb3544cd25e1c`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py` (sha `8a08d7fdc9111dfa46cf364f8af3b828027b3e4511b0b485ce94609640a9cc22`)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py` (sha `5a50ce4cfe751a39c34a467363ca26124cad01868658cc44311e6646c5bcef75`)

## CONFIG locked strategy params (verbatim from SEAL/P1)

| Param | Value |
|---|---|
| Donchian entry N | 15 |
| Donchian exit M | 8 |
| ATR period | 20 (Wilder) |
| Stop multiplier | 2.0 (2N) |
| Per-trade risk | 1.0% |
| max_units_per_market | 1 (no pyramid) |
| START_CASH_USD | $100,000 (DA4=B) |
| Tick size / value | 0.25 / $0.50 |
| RTH window | 09:30-16:00 ET America/New_York |
| K9 threshold | 100 (inviolate) |

## Tests authored (NOT RUN at P3 BUILD; P4 smoke separately authorized)

17 tests in `test_smoke_t1_t15.py`: T1, T2, T3, T4 (Donchian-15/8), T5 (Donchian-15 breakout), T6, T7, T7b, **T7c (starting_cash invariant $100,000)**, **T8 (Donchian-8 reversal exit)**, T9, **T10 (sizing for $100k cash)**, T11, T12 (RTH 09:30-16:00 ET), T13, T14 (5-tier cost stress), T15.

12 OOS driver invariants tests in `test_oos_driver_invariants.py`: cache path, OOS window start/end, no IS constants leak, no 2019/2023 date references (word-boundary), no run_in_sample, both drivers share runner main, CONFIG strategy params unchanged, signature compat, no top-level forbidden imports, databento function-local only, no db.Historical instantiation.

## REC1 inherited_constraints_block (carried byte-equivalent; binding)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

## Hard boundaries held (~29 boundaries; all True)

See JSON sidecar `hard_boundaries_held_this_p3_build_runner_turn` for full list. Key: `no_backtest`, `no_signal_computation`, `no_p4_smoke_execution`, `no_lessons_md_touched`, `no_modification_of_s12_d1_seal_at_66bbbd1`, `no_rec1_demotion_to_advisory`.

## Next phase requirements

P4 synthetic smoke requires separate authorization: `Authorize s12 D1 MNQ.c.0 P4 synthetic smoke only`. No phase pre-approved by this report.

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| lifecycle_state | P3_BUILD_RUNNER_REPORT_SEALED |
| rec1_oos_k9_risk_disclosure_binding | True |
