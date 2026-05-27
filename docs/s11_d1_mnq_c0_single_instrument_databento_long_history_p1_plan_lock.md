# S11-D1 P1 plan-lock (sealed)

**Candidate record id:** `s11-d1-mnq-c0-single-instrument-databento-long-history`
**Phase prefix:** `PHASE2-S11-D1-MNQ-SI`
**Authored (UTC):** `2026-05-27T04:14:54.255283Z`
**Lifecycle state:** P1_PLAN_LOCK_SEALED
**Tier-N spec inherited byte-equivalent:** commit `9c63088` (seal `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`)
**Report seal sha256:** `5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648`

## Tier-N spec inheritance

This P1 plan-lock document LOCKS the sealed Tier-N spec at the above commit. All Tier-N spec decisions are inherited byte-equivalent into the BUILD phase. No Tier-N spec modification is permitted; any change requires a fresh _revN_ Tier-N spec under a separate authorization.

- Tier-N spec path: `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec.md`
- Tier-N spec JSON: `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_sealed.json`
- Tier-N spec seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- Tier-N spec commit: `9c63088`

## 1. Exact implementation files allowed for P3 BUILD

**Total allowed file count:** 16

### Source files (5)
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/__init__.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/main.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/execution_guard.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/in_sample_driver.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/out_of_sample_driver.py`

### Test scaffold files (5)
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/__init__.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/conftest.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py`

### Sealed BUILD report files (6)
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_build_report.md`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_driver_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_driver_build_report.md`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_out_of_sample_driver_build_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_out_of_sample_driver_build_report.md`

### Creation pattern

P3 BUILD shall be split into 3 sub-phases (sequential, each separately authorized): P3-RUNNER (source files 1-3 + runner sealed build report), P3-IS-DRIVER (in_sample_driver.py + IS driver build report), and P3-OOS-DRIVER (out_of_sample_driver.py + OOS driver build report). OR P3 may be a single combined authorization if the operator prefers; the P1 plan-lock does not pre-impose a sub-split. Each invocation must list exactly its target files.

### Test scaffold inclusion

Test scaffold files (tests/__init__.py, conftest.py, synthetic_mnq_daily.csv, test_smoke_t1_t15.py, test_oos_driver_invariants.py) MAY be included in P3 BUILD directly, OR may be deferred to a P3.5 BUILD-EXTENSION (lesson from S10-D2 chain where conftest + fixtures were omitted from P3 and required a P3.5 retrofit). The S11-D1 P1 plan-lock RECOMMENDS including test scaffold in the original P3 BUILD authorization to avoid the retrofit pattern.

## 2. Files explicitly forbidden during all S11-D1 phases

- Any S10-D2 sealed artifact (commit 23c7164 PARK and the full S10-D2 chain).
- Any S10-D2 source file (in_sample_driver.py, out_of_sample_driver.py, main.py, execution_guard.py, test_smoke_t1_t15.py, test_oos_driver_invariants.py, conftest.py, synthetic CSV fixtures, __init__.py).
- Any S10-D2 cache directory (data/databento_cache/, data/databento_cache_oos/, data/databento_cache_is_only/).
- Any s10-D1 MNQ+MGC artifact OTHER than the sealed MNQ.c.0 CSV at the path specified in section 3 (which is reused READ-ONLY byte-equivalent).
- Any s9 RSI-2, s7 D1 ETF-proxy, s8-D1, B005_NNN, B006_001, B006_002, T8, NKE artifact.
- next_research_track_selection_plan_*.md files (parallel-session selection plans).
- review_queue.json.
- production idea_memory directory.
- All Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- obsidian-trade-logger or any obsidian-related directory/file.
- brain_memory/projects/trading_bot/lessons.md (long-running parallel-session dirty file; explicitly off-limits in EVERY S11-D1 phase unless a separate authorization names it as the target).
- app.py, templates/base.html, or any web/UI file modified by the parallel session.
- CLAUDE.md, docs/decisions.md (if exists), RUNBOOK, pipeline_manifest, .gitignore.
- The sealed Tier-N spec files (docs/s11_d1_..._tier_n_spec.md and reports/..._tier_n_spec_sealed.json) — these are LOCKED at the Tier-N seal and cannot be modified.
- This P1 plan-lock document itself once committed — any change to the plan-lock requires a fresh _revN_ plan-lock under separate authorization.
- Any file outside the S11-D1 candidate_record_id namespace.

## 3. Input data path and sha requirement

| Field | Value |
|---|---|
| `primary_path` | data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv |
| `primary_sha256_required` | 8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e |
| `primary_row_count` | 2066 |
| `primary_observed_window` | 2019-05-13, 2025-12-29 |
| `primary_format` | CSV (per s10-D1 fetch tool output schema; daily bars with ts_event index) |
| `primary_access` | READ-ONLY; byte-equivalent reuse from s10-D1 sealed fetch |
| `fresh_fetch_required` | False |
| `fresh_fetch_authorized_by_this_plan_lock` | False |
| `secondary_data_authorized` | False |
| `alternate_symbols_authorized` | False |
| `alternate_schema_authorized` | False |
| `alternate_vendor_authorized` | False |
| `build_phase_must_verify_csv_sha_at_runtime` | True |
| `build_phase_must_fail_loudly_if_sha_mismatch` | True |
| `fail_loud_error_class_name` | S11_D1_MNQ_CSV_SHA_MISMATCH |

## 4. Strategy mechanic boundaries (LOCKED)

- `mechanic_family`: **F1 long+short bi-directional Donchian, no pyramid, ATR-stop, 1% per-trade risk**
- `donchian_entry_period_n`: **55**
- `donchian_exit_period_n`: **20**
- `atr_period`: **20**
- `atr_method`: **Wilder**
- `stop_multiplier_in_atr`: **2.0**
- `risk_pct_per_trade`: **0.01**
- `max_units_per_market`: **1**
- `max_total_units`: **1**
- `pyramid_method`: **NONE**
- `amb6_filter`: **NONE**
- `regime_overlay`: **NONE**
- `correlation_filter`: **NOT APPLICABLE (single instrument)**
- `vol_targeting`: **NONE (not vol-targeting mechanic family)**
- `leverage_cap`: **implicit via 1% per-trade risk sizing; no separate C4 leverage cap**
- `starting_cash_mnq_equivalent`: **50000**
- `starting_cash_invariant_error_class`: **S11_D1_STARTING_CASH_INVARIANT_VIOLATION**
- `tick_size_points`: **0.25**
- `tick_value_usd`: **0.5**
- `dollar_per_point`: **2.0**
- `contract_multiplier_note`: **MNQ: $2 * Nasdaq-100 index value per point**
- `rth_window_et`: **{"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0, "tz": "America/New_York"}**
- `intraday_data_used`: **False**
- `daily_bars_only`: **True**
- `roll_method`: **Continuous front-month per Databento stype_in=continuous; no operator-side roll override**
- `modification_post_build_forbidden`: **True**
- `modification_requires_fresh_candidate_record_id`: **True**

## 5. IS / OOS split enforcement

- **IS window:** 2019-05-13 → 2023-12-29
- **OOS window:** 2024-01-02 → 2025-12-30
- **Locked at SEAL:** True

**Structural enforcement in drivers:**

- `in_sample_driver_filters_to_is_window_only`: True
- `in_sample_driver_constants`: {"IN_SAMPLE_START": "datetime.date(2019, 5, 13)", "IN_SAMPLE_END": "datetime.date(2023, 12, 29)", "CSV_PATH_HARDCODED": "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv", "CSV_SHA256_HARDCODED": "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"}
- `out_of_sample_driver_filters_to_oos_window_only`: True
- `out_of_sample_driver_constants`: {"OUT_OF_SAMPLE_START": "datetime.date(2024, 1, 2)", "OUT_OF_SAMPLE_END": "datetime.date(2025, 12, 30)", "CSV_PATH_HARDCODED": "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv", "CSV_SHA256_HARDCODED": "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"}
- `oos_inspection_during_is_phase_blocked_by_separate_files`: True
- `drivers_are_authored_at_p3_build_as_siblings`: True
- `no_p3_5_retrofit_planned_for_oos_driver`: True

## 6. Cost tier definitions (LOCKED)

**Baseline costs (S1 = 1.0x scalar):**

- Commission per round-trip: $0.74
- Fees per round-trip: $0.36
- Slippage entry/stop/exit ticks: 1 / 1 / 1

**Cost-stress tiers:**

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal |
| `S1` | 1.0 | 1.0 | baseline retail (DEFAULT) |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

## 7. K9 / sample-size rules

- **K9 threshold:** **100** (closed_trades_portfolio < 100)
- **K9 threshold modification forbidden:** True
- **K9 relaxation at any phase forbidden:** True

**Expected IS trade count estimate:** DAILY DONCHIAN-55/20 ON SINGLE INSTRUMENT OVER 4.6 YEARS IS HISTORICALLY SPARSE. Reference: S10-D2 NQ leg produced 54 trades over 10 years (~5.4/year). Scaled to 4.6y single-instrument expected: 25-50 trades. THIS IS BELOW K9=100 THRESHOLD.

**K9 risk at IS phase:** STRUCTURALLY POSSIBLE — INSUFFICIENT_SAMPLE verdict expected if observed

**K9 risk at OOS phase:** STRUCTURALLY EXPECTED — 2y OOS window will produce far fewer trades than IS

**If K9 fires at IS:** Verdict at IS shall be INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY). Chain shall NOT relax K9. Appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and the operator shall decide between (a) continuing to P10 OOS despite IS being undersampled, (b) parking S11-D1 with PARK memo at IS stage, or (c) selecting a different mechanic family in a fresh candidate.

**If K9 fires at OOS:** Verdict at OOS shall be INSUFFICIENT_SAMPLE. Chain shall NOT relax K9. Appropriate response is to park S11-D1 with PARK memo (analogous to S10-D2 P11 PARK at PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED).

## 8. Rejection rules (LOCKED)

### K-gates

| K-gate | Trigger |
|---|---|
| `K1_sharpe_proxy_lt_0` | FAIL_SAFETY trigger |
| `K2_expectancy_le_0` | FAIL_SAFETY trigger |
| `K4_trade_curve_maxdd_gt_50` | FAIL_SAFETY trigger (|maxdd_pct| > 50%) |
| `K6_safety_warning_count_gt_0` | FAIL_SAFETY trigger |
| `K7_correlation_or_filter_silently_introduced` | FAIL_SAFETY trigger |
| `K8_sealed_parent_drift` | FAIL_SAFETY trigger (parent seal mismatch) |
| `K9_closed_trades_lt_100` | INSUFFICIENT_SAMPLE trigger (NOT FAIL_SAFETY) |
| `K10_avg_pairwise_corr` | NOT APPLICABLE (single instrument) |
| `K11_cap_binding_events_gt_1000` | FAIL_SAFETY trigger (mostly N/A for single-instrument 1-contract) |
| `K12_DR_fires_on_cost_stress` | evaluated at P6.5 cost-stress sweep |

### DR rules (P6.5 cost-stress sweep)

| DR | Trigger |
|---|---|
| `DR2_tier_net_pnl_le_0` | fires if any non-baseline tier net_pnl <= 0 |
| `DR3_tier_sharpe_proxy_le_0` | fires if any non-baseline tier sharpe <= 0 |
| `DR4_tier_expectancy_le_0` | fires if any non-baseline tier expectancy <= 0 |
| `DR5_tier_closed_trades_lt_100` | fires if any non-baseline tier closed_trades < 100 |

### A-gates (P6 IS)

| A-gate | Behavior |
|---|---|
| `A1_closed_trades_ge_100` | fail -> INSUFFICIENT_SAMPLE |
| `A2_sharpe_proxy_gt_0` | fail -> FAIL_SAFETY |
| `A3_expectancy_gt_0` | fail -> FAIL_SAFETY |
| `A4_trade_curve_maxdd_pct_le_30` | fail -> FAIL_SAFETY (S10-D2 used 50; S11-D1 tightens to 30 per Tier-N spec rejection-rules section, single-instrument higher concentration risk) |
| `A5` | NOT APPLICABLE (single instrument; no portfolio_wr_gap diversification claim possible) |
| `A6_no_pyramid_attestation_pass` | fail -> FAIL_SAFETY |
| `A7_effective_independent_bets` | NOT APPLICABLE (trivially 1) |
| `A8_cost_stress_S0_S4_run` | evaluated at P6.5 |
| `A9_phase2_c1_c8_inheritance_attestable` | fail -> FAIL_SAFETY |
| `A10_cap_binding_events_eq_0` | fail -> FAIL_SAFETY |

**Invariants:**

- No threshold loosening: **True**
- No DR redefinition post-SEAL: **True**
- No filter introduction post-SEAL: **True**
- No universe widening: **True**
- No starting cash modification: **True**
- No strategy parameter modification: **True**
- FAIL_SAFETY terminal: **True**

## 9. Promotion rules (LOCKED)

- `permanent_live_block`: **True**
- `permanent_paper_block_via_broker_api`: **True**
- `live_promotion_blocked_at_6_gates_permanently`: **True**
- `no_verdict_unblocks_live`: **True**
- `no_verdict_unblocks_paper_via_broker`: **True**
- `no_verdict_unblocks_frc`: **True**
- `no_verdict_unblocks_strategy_lab_promotion`: **True**
- `no_verdict_unblocks_review_queue_mutation`: **True**
- `promotion_at_any_stage_is_OUT_OF_SCOPE`: **True**
- `research_diagnostic_only`: **True**
- `diagnostic_only_not_live_grade_label`: **True**
- `no_profitability_claim`: **True**

## 10. Test plan

**Test battery:** S11-D1 P4 synthetic smoke (T1-T15 + T7b + T7c)
**Test count:** 17
**Invocation pattern:** constrained --rootdir/--confcutdir to tests/ subtree (lesson from S10-D2 P4 ghost-hydra directory blocker)
**Synthetic fixture:** `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`
**Loader-side marker:** `SYNTHETIC_PHASE2_SMOKE_FIXTURE (loader-side guard)`

### Tests required (T1-T15 + T7b + T7c)

| Test | Description |
|---|---|
| `T1_module_imports_clean` | main + execution_guard + drivers importable without QC/databento at module level |
| `T2_runner_class_instantiable` | main.Algo() Initialize() succeeds without QC runtime |
| `T3_wilder_atr_synthetic` | ATR(20) on constant 21-bar TR series returns 2.0 |
| `T4_donchian_55_20_synthetic` | Donchian high/low on synthetic series matches max/min |
| `T5_entry_trigger_synthetic_breakout` | synthetic breakout bar triggers long entry |
| `T6_stop_placement_at_2n` | stop = entry - 2 * N for long |
| `T7_pyramid_trigger_at_05n` | pyramid trigger COMPUTED at +0.5N (but invocation forbidden) |
| `T7b_add_pyramid_unit_raises_under_max_units_1` | add_pyramid_unit raises RuntimeError when max_units=1 |
| `T7c_starting_cash_invariant_50000` | CONFIG['starting_cash_mnq_equivalent'] == 50_000 (S11-D1 specific S-STOP) |
| `T8_exit_on_donchian_20_reversal` | Donchian-20 reversal triggers exit |
| `T9_portfolio_cap_uses_unit_count_not_contract_count` | max_total_units=1 enforced |
| `T10_sizing_1pct_floor` | compute_unit_contracts returns 1 for portfolio=50k / N=50 / $/pt=2 |
| `T11_skip_when_contract_count_lt_one` | tiny equity returns 0 contracts |
| `T12_rth_only_filter_attested` | RTH window 09:30-16:00 ET in CONFIG |
| `T13_roll_cost_modeled_1_spread_tick` | tick_value_usd=0.50 in CONFIG |
| `T14_cost_stress_matrix_S0_S1_S2_S3_S4` | 5 tiers in CONFIG['cost_stress_tiers'] |
| `T15_validator_harness_pass_on_synthetic` | execution_guard.full_guard_check returns overall_pass=True on synthetic algo proxy |

### OOS driver invariants tests required

| Test | Description |
|---|---|
| `test_is_driver_source_byte_stable_at_p3_6` | (NOT APPLICABLE for S11-D1; OOS driver authored at P3 BUILD alongside IS, not retrofitted at P3.5/P3.6) |
| `test_oos_driver_cache_path_points_to_csv` | oos_driver.CSV_PATH == sealed MNQ CSV |
| `test_oos_driver_window_start_is_2024_01_02` | OUT_OF_SAMPLE_START == datetime.date(2024, 1, 2) |
| `test_oos_driver_window_end_is_2025_12_30` | OUT_OF_SAMPLE_END == datetime.date(2025, 12, 30) |
| `test_oos_driver_does_not_have_is_window_constants` | no IN_SAMPLE_START/END constants leak |
| `test_oos_driver_does_not_reference_is_dates_in_source` | no 2019/2023 dates in OOS driver source |
| `test_oos_driver_does_not_have_run_in_sample_function` | no run_in_sample function on OOS driver |
| `test_both_drivers_use_same_runner_main_module` | lazy-import resolves to same module object |
| `test_runner_main_config_strategy_params_unchanged` | CONFIG strategy params byte-identical across drivers |
| `test_oos_run_function_signature_matches_is` | same parameter names and defaults |
| `test_oos_driver_no_top_level_forbidden_imports` | no top-level databento/QC/AlgorithmImports |
| `test_oos_driver_databento_import_is_function_local` | import databento as db inside load function only |
| `test_oos_driver_does_not_instantiate_db_historical` | no db.Historical() call (guard docstring allowed) |

### Pytest run protocol at P4

- `invocation_pattern`: python -u -m pytest <test_file> -v --no-header --tb=short -p no:cacheprovider --rootdir <tests_dir> --confcutdir <tests_dir> --import-mode=importlib
- `env_guards`: PYTHONPATH=C:\SPARTA_BRAIN; HTTP_PROXY=invalid; DATABENTO_API_KEY popped
- `expected_wall`: ~1s (synthetic; no real data decode)
- `verdict_threshold`: all tests PASSED (17/17 expected); any FAIL -> P4 verdict FAIL

## 11. Output artifact plan per phase

### `p1_plan_lock_this_turn`
- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_p1_plan_lock.md`
- `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_p1_plan_lock_sealed.json`

### `p2_phase2_plan_future`
- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_p2_phase2_plan.md`
- `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_p2_phase2_plan_sealed.json`

### `p3_build_future`: (see Section 1 — 5 source + 5 test + 6 sealed-report files)

### `p4_smoke_future`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_smoke_t1_t15_report.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_smoke_t1_t15_report.md`

### `p6_is_future`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_diagnostic_result_sealed.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_in_sample_diagnostic_result_sealed.md`

### `p6_5_cost_stress_future`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_cost_stress_matrix_result_sealed.json`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_cost_stress_matrix_result_sealed.md`

### `p7_decision_memo_future`
- `reports/s11_d1_p7_decision_memo_sealed.json`
- `reports/s11_d1_p7_decision_memo_sealed.md`

### `p10_oos_gate_future`
- `reports/s11_d1_p10_oos_gate_sealed.json`
- `reports/s11_d1_p10_oos_gate_sealed.md`

### `p11_lifecycle_decision_future`
- `reports/s11_d1_p11_lifecycle_memo_sealed.json`
- `reports/s11_d1_p11_lifecycle_memo_sealed.md`

### `naming_locked_at_p1`: True

### `deviation_requires_per_phase_explicit_authorization`: True

## 12. Seal / hash protocol (LOCKED)

- **Seal method:** LESSON_HUNTER_004 canonical roundtrip
- **Canonical form:** `json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False, default=str)`
- **Excluded keys:** `['report_seal_sha256', 'seal_method']`
- **Hash algorithm:** sha256
- **Encoding:** utf-8
- **Reseal verify required after write:** True
- **Reseal mismatch error class:** `SEAL_ROUNDTRIP_FAIL`

### Embedded constants in drivers (validated via assert_seal_inheritance)

| Constant | Value |
|---|---|
| `PREDECESSOR_SEAL_SHA256` | `1a9acec (s10-D1 park reference; not a seal)` |
| `TIER_N_SPEC_SEAL_SHA256` | `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24` |
| `PLAN_LOCK_SEAL_SHA256` | `(will be populated at P1 commit; this file's seal)` |
| `PHASE2_PLAN_SEAL_SHA256` | `(will be populated at P2 commit)` |
| `PHASE2_TEMPLATE_MD_SHA256` | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` |
| `PHASE2_TEMPLATE_JSON_SHA256` | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` |

## 13. Git staging / commit protocol (LOCKED)

### Pre-stage check (required at every phase)

- Run: git status --short -uall
- Run: git diff --cached --name-status
- Halt if any parallel-session file is staged
- Halt if any S10-D2 reconciliation file is staged
- Halt if app.py / templates/base.html / lessons.md are staged
- Halt if any unrelated tracked file is in the index

- **Staging pattern:** `git add -- <exact authorized file paths>`
- **Staging pattern forbidden:** `git add . / git add -A / git add * / git add <directory>`

### Post-stage verification (required)

- Run: git diff --cached --name-status
- Verify: staged count == authorized count for this phase
- Verify: every staged path matches an authorized path regex
- Halt if either check fails

- **Commit pattern:** `git commit -F <msg_file> -- <pathspec>`
- **Commit pattern forbidden:** `git commit -a / git commit --no-verify / git commit --amend`
- **Message must be passed via -F file (not -m inline):** True

### Post-commit verification (required)

- Run: git show --name-status HEAD
- Verify: every committed path matches an authorized path
- Verify: no unrelated files in the commit
- Run: git status --short -uall
- Report: any tracked dirty files (parallel-session noise; should not be mine)

**Always-on invariants:**

- Pathspec only at every phase: **True**
- No force push: **True**
- No amend without explicit authorization: **True**
- No rebase without explicit authorization: **True**
- No branch creation without explicit authorization: **True**
- No remote push without explicit authorization: **True**

## 14. Explicit next-phase requirement

P1 plan-lock authoring + sealing + commit completes here. The NEXT phase is P2 phase-2 plan (S10-D2 chain precedent: Tier-N -> P1 -> P2 -> P3 BUILD). P2 phase-2 plan REQUIRES SEPARATE OPERATOR AUTHORIZATION via: 'AUTHORIZE S11-D1 P2 phase-2 plan only'. The P2 phase-2 plan shall adapt the docs/phase2_safety_contract_template.md C1-C8 byte-equivalent for S11-D1 with single-instrument adaptations where the template requires per-market parameters. NO PHASE BEYOND P2 IS PRE-APPROVED by this P1 plan-lock. Each subsequent phase (P3 BUILD, P4 smoke, P6 IS, P6.5 cost-stress, P7 decision memo, P10 OOS gate, P11 lifecycle decision) requires its own separate operator authorization.

- **Next phase pre-approved by this plan-lock:** False
- **P2 phase-2 plan requires separate authorization:** True
- **P3 BUILD requires separate authorization:** True
- **P4 smoke requires separate authorization:** True
- **P6 IS requires separate authorization:** True
- **P6.5 cost-stress requires separate authorization:** True
- **P7 decision memo requires separate authorization:** True
- **P10 OOS gate requires separate authorization:** True
- **P11 lifecycle decision requires separate authorization:** True

## Parent references (READ-ONLY)

- `tier_n_spec_commit`: `9c63088`
- `tier_n_spec_seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- `selection_plan_commit`: `556ab3f`
- `selection_plan_path`: `docs/next_research_track_selection_plan_after_s10_d1_park.md`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `s10_d2_park_commit`: `23c7164`
- `s10_d2_park_status`: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- `s10_d2_p11_park_memo_seal`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- `mnq_c0_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `mnq_c0_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- `mnq_c0_csv_row_count`: `2066`
- `mnq_c0_csv_observed_window`: `['2019-05-13', '2025-12-29']`

## Status / labels

- `trading_status`: PAUSED
- `live_status`: BLOCKED_AT_6_GATES
- `research_label`: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE

**Labels:**

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `P1_PLAN_LOCK_SEALED`
- `S11_D1_MNQ_SINGLE_INSTRUMENT_FALLBACK`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NO_FRC_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_PHASE_PRE_APPROVED_BEYOND_THIS_PLAN_LOCK`
- `K9_THRESHOLD_INVIOLATE`
- `OOS_INDETERMINATE_RISK_DISCLOSED`
- `TIER_N_SPEC_LOCKED_BYTE_EQUIVALENT`

## Hard boundaries held (this P1 plan-lock turn)

- no_app_py_touched: True
- no_backtest: True
- no_broker_exchange_api: True
- no_commit_in_orchestrator: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_k9_relaxation: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_inspection: True
- no_paper_trading: True
- no_phase_pre_approval_beyond_plan_lock: True
- no_profitability_claim: True
- no_promotion_to_live: True
- no_qc_runtime: True
- no_review_queue_mutation: True
- no_s10_d1_modification: True
- no_s10_d2_modification: True
- no_s10_d2_revival: True
- no_safety_gate_relaxation: True
- no_source_modification: True
- no_strategy_build: True
- no_templates_base_html_touched: True
- no_threshold_loosening: True
- no_tier_n_spec_modification: True
- no_unrelated_tracked_file_modified: True

## Seal metadata

- Report seal sha256: `5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648`
- Seal method: LESSON_HUNTER_004 canonical roundtrip
- Reseal verified on disk: YES
