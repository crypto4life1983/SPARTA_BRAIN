# S13-D1 P4 synthetic smoke report (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR` / `P4_SYNTHETIC_SMOKE`
**Authored (UTC):** `2026-05-27T18:04:47.480004Z`
**Lifecycle state:** P4_SYNTHETIC_SMOKE_SEALED
**Report seal sha256:** `35b803450d5dd55466b0c0cc94a6e6793e0405a6b4876d80df709c4ca7fcf8fc`
**Reseal verified on disk:** YES (UTF-8 explicit)

## Verdict: `P4_SMOKE_ALL_PASS`

29/29 tests PASSED (17 smoke + 12 OOS invariants) in **0.10s combined wall time**.

## Verdict caveats (LOAD-BEARING)

- P4 smoke validates STRUCTURAL primitives + invariants only; does NOT establish IS or OOS performance
- P6 IS diagnostic remains separately authorized
- **REC1-equivalent binding:** OOS K9 reachable at lower bound with thin margin; if observed IS rate falls below 25/year, OOS K9 unreachability becomes structurally probable
- P4 PASS does NOT imply `READY_FOR_LONGER_BACKTEST`
- P4 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

## Smoke battery results (T1-T15 + T7b + T7c; RSI-adapted)

Test file: `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py` (sha `d1a5f8807a95fbffe79c0dd40fd8125c6b9ebfe8fe98957c7d64c0bb177fd7ab`)

| Test | Status |
|---|---|
| test_T1_module_imports_clean | PASSED |
| test_T2_runner_class_instantiable | PASSED |
| test_T3_wilder_atr_synthetic | PASSED |
| test_T4_rsi_2_synthetic | PASSED |
| test_T5_rsi_oversold_overbought_entry_trigger | PASSED |
| test_T6_stop_placement_at_2n | PASSED |
| test_T7_pyramid_trigger_at_05n | PASSED |
| test_T7b_add_pyramid_unit_raises_under_max_units_1 | PASSED |
| test_T7c_starting_cash_invariant_200000 | PASSED |
| test_T8_exit_on_rsi_50_crossover | PASSED |
| test_T9_portfolio_cap_uses_unit_count_not_contract_count | PASSED |
| test_T10_sizing_0_5pct_floor | PASSED |
| test_T11_skip_when_contract_count_lt_one | PASSED |
| test_T12_rth_only_filter_attested | PASSED |
| test_T13_roll_cost_modeled_1_spread_tick | PASSED |
| test_T14_cost_stress_matrix_S0_S1_S2_S3_S4 | PASSED |
| test_T15_validator_harness_pass_on_synthetic | PASSED |

17 PASSED / 0 FAILED / 0 SKIPPED in 0.05s; exit code 0.

## OOS driver invariants battery

Test file: `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py` (sha `15dfe5237027c1b2a58e8ae3b36cae92a49f4c41ccd56f96bdface80b7fb3bab`)

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

12 PASSED / 0 FAILED / 0 SKIPPED in 0.05s; exit code 0.

## Combined

| Metric | Value |
|---|---|
| Total tests | 29 |
| Total passed | 29 |
| Combined wall time | 0.10s |
| Exit codes (both) | 0 |
| All pass | True |

## Sealed MNQ CSV NOT touched at P4

- Sealed CSV: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha `8b7b832c...`)
- Accessed by P4 smoke: **False**
- Rationale: P4 smoke validates structural primitives on synthetic fixture only

## Files-under-test SHA anchors

| File | sha256 |
|---|---|
| `main.py` | `89b5d5b9bafec733194fb2191ccada9298811205613a20e772c9af9419285839` |
| `execution_guard.py` | `0de7fd480ae7d82739b1e7a85cec89272bef993df833cf83d627c7e6945d00c6` |
| `in_sample_driver.py` | `fc5cde13bec22aab18b4a0c550e4f7de927147e30408c0eb606283e1ddabecbe` |
| `out_of_sample_driver.py` | `64ff35e3c04a1ba58a0a8a091c2d17a3831ee3c6daf12afc51a23ba379b10843` |
| `tests/conftest.py` | `b589298aa43f7f7f1501993a1b2f7eedce4cd865f68c8057fc079a1c8f633d4d` |
| `tests/test_smoke_t1_t15.py` | `d1a5f8807a95fbffe79c0dd40fd8125c6b9ebfe8fe98957c7d64c0bb177fd7ab` |
| `tests/test_oos_driver_invariants.py` | `15dfe5237027c1b2a58e8ae3b36cae92a49f4c41ccd56f96bdface80b7fb3bab` |
| `tests/fixtures/synthetic_mnq_daily.csv` | `265f5a08a05577061d1c00ae0bf573b58ff3140edbd16722ef2def488c8db0fe` |

## C6 inherited_constraints_block (carried verbatim from P2; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); REVISED at SEAL from default 1.0% for DR3 mitigation
3. DA4=C (BINDING): START_CASH_USD = 200000 ($200k); REVISED at SEAL from default $100k for DR10 mitigation
4. K9-reachability discipline (NEW framework standard from selection-plan revision 0e3f9d4) applied at PLAN + DRAFT + SEAL + P1 + P2 + P3 + P4; binding for all subsequent phases
5. K9_THRESHOLD_INVIOLATE: closed_trades >= 100; no relaxation at any phase
6. Mechanic family F3 RSI(2) bi-directional mean-reversion LOCKED at PLAN; no reopening
7. RSI thresholds 10/50/90/50 LOCKED at PLAN; threshold modification post-SEAL FORBIDDEN per RF13
8. DR3 risk ELEVATED (RSI lineage s9 falsification precedent); mitigated via DA3=B
9. DR10 risk ELEVATED (high-frequency turnover ~50-65 trades/y); mitigated via DA4=C ($200k START_CASH)
10. Tier-N spec LOCKED byte-equivalent at 262491c (sha 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775)
11. P1 plan-lock LOCKED byte-equivalent at 005cb8a (sha 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c)
12. s12-d1 terminal park (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at ecbd001) preserved unchanged
13. All parallel-session shorter-path sealed artifacts byte-stable; not anchored by this chain
14. Expected terminal verdict if OOS K9 fires: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED
15. P4 PASS does NOT imply READY_FOR_LONGER_BACKTEST; requires P6 IS diagnostic under separate authorization
16. P4 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

## Parent references

| Phase | Commit | Seal sha256 |
|---|---|---|
| Tier-N SEAL | `262491c` | `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |
| P1 plan-lock | `005cb8a` | `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c` |
| P2 phase-2 plan | `beecd87` | `b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6` |
| P3 BUILD (runner) | `24625c6` | `6c8875cb791765193f6494183614c2c78e63b1ef9a53d1375a6dc44a235eb4a6` |
| P3 BUILD (IS driver) | `24625c6` | `c4dc64bce87a6697ed7eeda3606dbe8247f21ad4a0fa3f753363872217f33e0a` |
| P3 BUILD (OOS driver) | `24625c6` | `dd63e967fe70d12df56ac81cb5c85584194bb39a83288da0bd9de62974d092f6` |

## Status

trading: PAUSED · live: BLOCKED_AT_6_GATES · FRC: NEVER_GRANTED · lifecycle: P4_SYNTHETIC_SMOKE_SEALED · REC1-equivalent binding: True

## Next phase requirements

P6 IS diagnostic requires separate authorization: `Authorize s13 D1 MNQ.c.0 P6 IS diagnostic only`.
