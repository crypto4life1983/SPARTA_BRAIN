# S12-D1 P4 synthetic smoke report (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8` / `P4_SYNTHETIC_SMOKE`
**Authored (UTC):** `2026-05-27T15:35:44.315188Z`
**Lifecycle state:** P4_SYNTHETIC_SMOKE_SEALED
**Report seal sha256:** `6d2bff4d2b40d4349a1c26d37375ca6d9e8ea616ff9f85d3d9f56293325b8bd4`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Verdict

**`P4_SMOKE_ALL_PASS`** — all 29 authored tests PASSED.

## Verdict reasons

- All 17 P4 smoke tests (T1-T15 + T7b + T7c) PASSED on synthetic fixture (0.06s)
- All 12 OOS driver invariants tests PASSED (0.05s)
- Total: **29/29 tests PASSED in 0.11s combined wall time**
- Synthetic fixture used (`SYNTHETIC_PHASE2_SMOKE_FIXTURE`); **sealed MNQ.c.0 CSV NOT touched**
- `execution_guard.full_guard_check` returns `overall_pass=True` on synthetic algo proxy

## Verdict caveats (LOAD-BEARING)

- P4 smoke validates STRUCTURAL primitives + invariants only; it does NOT establish IS or OOS performance
- P6 IS diagnostic remains separately authorized; not run by this P4 smoke
- **REC1 binding: OOS K9 STRUCTURALLY UNREACHABLE** (implied 35-87 OOS trades < K9=100); expected terminal verdict is `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` regardless of any IS outcome
- **P4 smoke PASS does NOT imply `READY_FOR_LONGER_BACKTEST`**; that requires P6 IS diagnostic under separate authorization
- **P4 smoke PASS NEVER implies live-readiness**; 6-gate live-block applies regardless of any verdict

## Pytest invocation protocol (per P1 §10)

```
python -u -m pytest <test_file> -v --no-header --tb=short -p no:cacheprovider \
  --rootdir external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests \
  --confcutdir external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests \
  --import-mode=importlib
```

Env guards active during invocation:
- `PYTHONPATH=C:\SPARTA_BRAIN`
- `HTTP_PROXY=invalid` (network attempts fail loudly)
- `HTTPS_PROXY=invalid`
- `DATABENTO_API_KEY` popped (delenv via conftest autouse fixture)

## Smoke battery results (T1-T15 + T7b + T7c)

Test file: `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py` (sha `8a08d7fdc9111dfa46cf364f8af3b828027b3e4511b0b485ce94609640a9cc22`)

| Test | Status |
|---|---|
| test_T1_module_imports_clean | PASSED |
| test_T2_runner_class_instantiable | PASSED |
| test_T3_wilder_atr_synthetic | PASSED |
| test_T4_donchian_15_8_synthetic | PASSED |
| test_T5_entry_trigger_synthetic_breakout | PASSED |
| test_T6_stop_placement_at_2n | PASSED |
| test_T7_pyramid_trigger_at_05n | PASSED |
| test_T7b_add_pyramid_unit_raises_under_max_units_1 | PASSED |
| test_T7c_starting_cash_invariant_100000 | PASSED |
| test_T8_exit_on_donchian_8_reversal | PASSED |
| test_T9_portfolio_cap_uses_unit_count_not_contract_count | PASSED |
| test_T10_sizing_1pct_floor | PASSED |
| test_T11_skip_when_contract_count_lt_one | PASSED |
| test_T12_rth_only_filter_attested | PASSED |
| test_T13_roll_cost_modeled_1_spread_tick | PASSED |
| test_T14_cost_stress_matrix_S0_S1_S2_S3_S4 | PASSED |
| test_T15_validator_harness_pass_on_synthetic | PASSED |

- 17 PASSED / 0 FAILED / 0 SKIPPED / 0 ERROR
- Wall time: 0.06s
- Exit code: 0

## OOS driver invariants battery

Test file: `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py` (sha `5a50ce4cfe751a39c34a467363ca26124cad01868658cc44311e6646c5bcef75`)

| Test | Status |
|---|---|
| test_oos_driver_cache_path_points_to_csv | PASSED |
| test_oos_driver_window_start_is_2024_01_02 | PASSED |
| test_oos_driver_window_end_is_2025_12_30 | PASSED |
| test_oos_driver_does_not_have_is_window_constants | PASSED |
| test_oos_driver_does_not_reference_is_dates_in_source | PASSED |
| test_oos_driver_does_not_have_run_in_sample_function | PASSED |
| test_both_drivers_use_same_runner_main_module | PASSED |
| test_runner_main_config_strategy_params_unchanged | PASSED |
| test_oos_run_function_signature_matches_is | PASSED |
| test_oos_driver_no_top_level_forbidden_imports | PASSED |
| test_oos_driver_databento_import_is_function_local | PASSED |
| test_oos_driver_does_not_instantiate_db_historical | PASSED |

- 12 PASSED / 0 FAILED / 0 SKIPPED / 0 ERROR
- Wall time: 0.05s
- Exit code: 0

## Fixture used

- Synthetic CSV: `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv` (sha `72a92ed98943eb6b7e6d8191266ea6d209d43e05629a44fa8c1bb3544cd25e1c`)
- Marker: `SYNTHETIC_PHASE2_SMOKE_FIXTURE`
- Row count: 90
- Design: 30 flat baseline bars (TR=2.0 constant) + 20 uptrend (15-day breakout) + 20 pullback (Donchian-8 reversal) + 20 flat tail

## Sealed MNQ CSV NOT touched at P4

- Sealed CSV path: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- Sealed CSV sha256: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- Accessed by P4 smoke: **False**
- Rationale: P4 smoke validates structural primitives on synthetic fixture only; sealed CSV is reserved for P6 IS diagnostic under separate authorization

## Files-under-test SHA anchors

| File | sha256 |
|---|---|
| `main.py` | `602dbdcf3afec7bbb0f2ca2be3af9539862b255f224aba93eed8c49072dc9a81` |
| `execution_guard.py` | `86107392173445bddaeea9fbcdd3d314bcbc0c9c61636408f73a0cd356ad4b42` |
| `in_sample_driver.py` | `d9cbe86a6c59b8b4732e0fd114948a48deafcc1fbb21c5fe7a9d71b85d62bff5` |
| `out_of_sample_driver.py` | `65ba90f9e22695f250a3ee6402f52be410e618356e636072acd80809387ea91e` |
| `tests/conftest.py` | `b0ea29c0c712bfba06e7c632cc1c3985511873cc5fc9cc41578e2d71afb95bc3` |
| `tests/test_smoke_t1_t15.py` | `8a08d7fdc9111dfa46cf364f8af3b828027b3e4511b0b485ce94609640a9cc22` |
| `tests/test_oos_driver_invariants.py` | `5a50ce4cfe751a39c34a467363ca26124cad01868658cc44311e6646c5bcef75` |
| `tests/fixtures/synthetic_mnq_daily.csv` | `72a92ed98943eb6b7e6d8191266ea6d209d43e05629a44fa8c1bb3544cd25e1c` |

## REC1 inherited_constraints_block (carried byte-equivalent; binding)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

## Parent references

| Phase | Commit | Seal sha256 |
|---|---|---|
| Tier-N SEAL | `66bbbd1` | `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` |
| P1 plan-lock | `d8bd359` | `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` |
| P2 phase-2 plan | `0b8d948` | `689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9` |
| P3 BUILD runner report | (within `91e740e`) | `0bbcf04cb48ec4f4989aa105b033a29d7cc20e3a09351947ce93534694115c15` |
| P3 BUILD IS driver report | (within `91e740e`) | `e3b09d662ff610cf912cca14d2d54552bbfbda7814038dc7721a540c1659379c` |
| P3 BUILD OOS driver report | (within `91e740e`) | `30fbfbd113d64d01dfcb95645b3f70310ba5d31cdb7e49640a4c99efd0ebc946` |

## Hard boundaries held (this P4 smoke turn; 34 boundaries; all True)

See JSON sidecar `hard_boundaries_held_this_p4_smoke_turn` for full attestation. Key:
- `no_backtest`, `no_is_diagnostic_execution`, `no_oos_inspection`, `no_oos_execution`
- **`no_sealed_csv_touched: True`** (sealed MNQ.c.0 CSV NOT accessed by P4 smoke)
- `no_signal_computation_against_real_data: True`
- `no_data_fetch`, `no_databento_api_call`, `no_network_call`, `no_live_trading`, `no_paper_trading`
- `no_strategy_lab_invoked`, `no_strategy_lab_promotion`, `no_review_queue_mutation`
- `no_lessons_md_touched`
- **`no_modification_of_s12_d1_seal_at_66bbbd1 / p1_at_d8bd359 / p2_at_0b8d948 / p3_at_91e740e`**: all True
- **`no_rec1_demotion_to_advisory: True`**
- `tests_were_run_against_authored_files_from_p3_build_only: True`
- `tests_used_synthetic_fixture_only_NOT_sealed_csv: True`

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| lifecycle_state | P4_SYNTHETIC_SMOKE_SEALED |
| rec1_oos_k9_risk_disclosure_binding | True |

## Next phase requirements

P6 IS diagnostic requires separate authorization: `Authorize s12 D1 MNQ.c.0 P6 IS diagnostic only`.

**NO phase beyond P6 pre-approved by this P4 smoke report.** Each subsequent phase requires its own separate operator authorization.
