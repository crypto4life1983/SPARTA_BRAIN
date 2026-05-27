# S11-D1 P2 phase-2 plan (sealed)

**Candidate record id:** `s11-d1-mnq-c0-single-instrument-databento-long-history`
**Phase prefix:** `PHASE2-S11-D1-MNQ-SI`
**Authored (UTC):** `2026-05-27T04:30:07.984515Z`
**Lifecycle state:** P2_PHASE2_PLAN_SEALED
**Tier-N inherited:** commit `9c63088` seal `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
**P1 plan-lock inherited:** commit `7d86486` seal `5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648`
**Report seal sha256:** `eacd2650bbbf1db8d190fd7567cbea869360381234623dd77b2c207ecdc735b1`

## Inheritance lock

This P2 phase-2 plan inherits the sealed Tier-N spec at commit 9c63088 and the sealed P1 plan-lock at commit 7d86486 BYTE-EQUIVALENT. No Tier-N or P1 modification permitted. Any change requires a fresh _revN_ spec / plan-lock under separate authorization. This P2 plan ADAPTS the phase2_safety_contract_template C1-C8 (md sha 1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981, json sha 695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32) for S11-D1 single-instrument execution.

## A. C1-C8 safety contracts (adapted from phase2 template)

**Phase2 template inheritance:** `docs/phase2_safety_contract_template.md` (sha `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981`) + `docs/phase2_safety_contract_template.json` (sha `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32`)

**Adaptation scope:** Single-instrument MNQ.c.0 — per-market parameters collapsed to per-instrument; C4 leverage-cap NOT APPLICABLE (not vol-targeting); C10/C11 cross-market gates trivially satisfied (single instrument).

| Contract | Applies | Rule |
|---|:-:|---|
| `C1_LiveMode_refusal` | True | main.Initialize() and both drivers MUST raise S11_D1_LIVE_MODE_REFUSAL if self.LiveMode is True (or if any LiveMode-equivalent indicator is set). |
| `C2_QuantConnect_runtime_isolation` | True | No top-level imports of AlgorithmImports or QuantConnect anywhere. All QC bindings via lazy _lazy_qc_import() called only inside main.Initialize(). |
| `C3_Databento_API_call_refusal` | True | No databento.Historical() instantiation anywhere. Local CSV reads only via standard csv module (or pandas if explicitly imported lazily inside the driver). No top-level `import databento`. |
| `C4_leverage_cap` | False | NOT APPLICABLE — S11-D1 is not vol-targeting. C4 was for B006_002 / vol-targeting mechanic families to enforce leverage cap via DR11. S11-D1 uses 1% per-trade risk sizing instead. |
| `C5_broker_exchange_api_refusal` | True | No broker SDK / exchange API import or call anywhere. No order submission. No connection establishment. All output is sealed report files only. |
| `C6_diagnostic_emission_contract` | True | Driver run_in_sample() and run_out_of_sample() return a diagnostic dict suitable for LESSON_HUNTER_004 canonical sealing. Caller (orchestrator) wraps with metadata + applies K-gate/A-gate logic + seals. Returns must include performance_summary, trade_diagnostics, safety_diagnostics, no_pyramid_attestation, scan_diagnostics, in_sample_window or out_of_sample_window, status_fields, labels, schema_id. |
| `C7_closed_verdict_enum` | True | C7 verdict enum is closed: FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST. Never live-ready. Verdict derivation in orchestrator post-processing (driver returns raw metrics; orchestrator applies K-gate/A-gate logic to derive C7 verdict). |
| `C8_phase2_safety_inheritance_attestation` | True | Every sealed diagnostic report shall include `phase2_safety_template_md_sha256` and `phase2_safety_template_json_sha256` constants matching the inherited values above. assert_seal_inheritance() in the driver validates these on every invocation. |

## 1. P3 BUILD sequence (LOCKED)

**Recommended pattern:** SINGLE_COMBINED_P3_BUILD_AUTHORIZATION

S10-D2 P3 BUILD was a single auth followed by P3.5 BUILD-EXTENSION (conftest + fixtures retrofit) and P3.6 BUILD-EXTENSION (OOS driver retrofit). S11-D1 P2 plan explicitly avoids those retrofits by INCLUDING all 16 P3 BUILD files in the single P3 BUILD authorization.

**P3 BUILD orchestrator step sequence (16 steps):**

- 1. Pre-flight: byte-stability snapshot of all guarded source files (S10-D2 + S10-D1 + S7-D1 + S8-D1 + Tier-N + P1).
- 2. Pre-flight: verify input CSV exists at sealed path + sha256 matches sealed value.
- 3. Author main.py (locked CONFIG; lazy QC import; LiveMode refusal; starting_cash invariant check).
- 4. Author execution_guard.py (validator hooks; forbidden-import scan; required-output-strings check).
- 5. Author in_sample_driver.py (CSV read; IS date filter 2019-05-13 to 2023-12-29; assert_seal_inheritance; assert_cache_complete adapted for single-file CSV; cost-tier application; bar walk; PyramidManager/PortfolioCapTracker integration).
- 6. Author out_of_sample_driver.py as sibling (mechanical adaptation; OOS date filter 2024-01-02 to 2025-12-30; run_out_of_sample signature mirror of run_in_sample).
- 7. Author __init__.py files (runner_harness/ and tests/).
- 8. Author tests/conftest.py (fixtures_dir fixture).
- 9. Author tests/fixtures/synthetic_mnq_daily.csv (60-row deterministic synthetic with SYNTHETIC_PHASE2_SMOKE_FIXTURE source marker).
- 10. Author tests/test_smoke_t1_t15.py (T1-T15 + T7b + T7c; MNQ-tick-value-adjusted thresholds).
- 11. Author tests/test_oos_driver_invariants.py (12 OOS invariants tests; mirrors S10-D2 P3.6 test pattern).
- 12. Static validation of every source file: ast.parse + compile + forbidden-import scan + module-level side-effects check + lazy-import attestation.
- 13. Author sealed BUILD reports (3 sealed reports: runner_build, in_sample_driver_build, out_of_sample_driver_build) as JSON+MD pairs (6 files total).
- 14. Post-state byte-stability check (all guarded source files + Tier-N + P1 + S10-D2 + S10-D1 + S7-D1 + S8-D1 byte-stable).
- 15. Final reseal verification on all 3 sealed BUILD reports.
- 16. Report files created + shas + seals + static validation results + git status.

- P3 orchestrator must NOT run pytest: **True** (deferred to P4)
- P3 orchestrator must NOT run driver: **True** (deferred to P6 IS / P10 OOS)
- P3 is authoring-only: **True**

## 2. P3 BUILD allowed files (16 total)

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

## 3. Files explicitly forbidden during all S11-D1 phases

- Any S10-D2 sealed artifact (commit 23c7164 PARK and the full S10-D2 chain).
- Any S10-D2 source file (in_sample_driver.py, out_of_sample_driver.py, main.py, execution_guard.py, test_smoke_t1_t15.py, test_oos_driver_invariants.py, conftest.py, synthetic CSV fixtures, __init__.py).
- Any S10-D2 cache directory (data/databento_cache/, data/databento_cache_oos/, data/databento_cache_is_only/).
- Any s10-D1 MNQ+MGC artifact OTHER than the sealed MNQ.c.0 CSV at the path specified in section 5 (which is reused READ-ONLY byte-equivalent).
- Any s9 RSI-2, s7 D1 ETF-proxy, s8-D1, B005_NNN, B006_001, B006_002, T8, NKE artifact.
- next_research_track_selection_plan_*.md files (parallel-session selection plans).
- review_queue.json.
- production idea_memory directory.
- All Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- obsidian-trade-logger or any obsidian-related directory/file.
- brain_memory/projects/trading_bot/lessons.md (long-running parallel-session dirty file; off-limits in EVERY S11-D1 phase unless a separate authorization names it as the target).
- app.py, templates/base.html, or any web/UI file modified by the parallel session.
- CLAUDE.md, docs/decisions.md (if exists), RUNBOOK, pipeline_manifest, .gitignore.
- The sealed Tier-N spec, P1 plan-lock, and (after commit) this P2 phase-2 plan files — these are LOCKED at seal.
- Any file outside the S11-D1 candidate_record_id namespace.
- docs/phase2_safety_contract_template.{md,json} (READ-ONLY template; sha-pinned at inheritance attestation).

## 4. Source / test / report artifact boundaries

### `source_files_constraints`
- `lazy_qc_import_only`: True
- `no_top_level_AlgorithmImports`: True
- `no_top_level_QuantConnect`: True
- `no_top_level_databento`: True
- `no_module_level_side_effects`: True
- `no_db_Historical_instantiation`: True
- `no_broker_or_exchange_imports`: True
- `no_network_call`: True
- `starting_cash_invariant_check_in_main_Initialize`: True
- `LiveMode_refusal_in_main_Initialize`: True

### `test_files_constraints`
- `synthetic_only`: True
- `no_real_csv_read`: True
- `no_databento_import`: True
- `no_qc_import_at_module_level`: True
- `SYNTHETIC_PHASE2_SMOKE_FIXTURE_marker_required_in_every_csv_row`: True
- `pytest_invocation_pattern_locked`: python -u -m pytest <test_file> -v --no-header --tb=short -p no:cacheprovider --rootdir <tests_dir> --confcutdir <tests_dir> --import-mode=importlib

### `report_files_constraints`
- `sealed_via_lesson_hunter_004_canonical_roundtrip`: True
- `json_pretty_indent_2_sort_keys_true`: True
- `md_twin_required_for_every_json_report`: True
- `no_seal_sha_self_reference_inside_payload`: True
- `reseal_verify_required_after_write`: True

## 5. Data-read validation rules

- `primary_input_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `primary_input_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- `csv_sha_validated_at_runtime_inside_drivers`: `True`
- `csv_sha_mismatch_error_class`: `S11_D1_MNQ_CSV_SHA_MISMATCH`
- `csv_row_count_validated_at_runtime`: `True`
- `csv_row_count_expected`: `2066`
- `csv_observed_window_validated_at_runtime`: `True`
- `csv_observed_window_expected`:
  - `2019-05-13`
  - `2025-12-29`
- `no_fresh_fetch_authorized`: `True`
- `no_alternate_symbol_authorized`: `True`
- `no_alternate_schema_authorized`: `True`
- `no_alternate_vendor_authorized`: `True`
- `no_dbn_decode_authorized`: `True`
- `no_databento_api_call_authorized`: `True`
- `fail_loud_on_any_validation_failure`: `True`
- `fail_loud_error_classes`:
  - `S11_D1_MNQ_CSV_SHA_MISMATCH`
  - `S11_D1_MNQ_CSV_PATH_MISMATCH`
  - `S11_D1_MNQ_CSV_ROW_COUNT_MISMATCH`
  - `S11_D1_MNQ_CSV_WINDOW_MISMATCH`

## 6. MNQ-only universe enforcement

- `universe_locked`: `['MNQ.c.0']`
- `universe_count`: `1`
- `second_symbol_authorized`: `False`
- `universe_widening_post_seal_forbidden`: `True`
- `universe_substitution_post_seal_forbidden`: `True`
- `universe_modification_requires_fresh_candidate_record_id`: `True`
- `enforced_in_drivers_via`:
  - `config_markets_constant`: `["MNQ"]`
  - `config_symbols_dict_lookup`: `{"MNQ": "MNQ.c.0"}`
  - `single_market_loop_in_run_function`: `True`
  - `no_per_market_cap_tracker_needed`: `True`
  - `max_total_units_equals_1`: `True`
- `violation_error_class`: `S11_D1_UNIVERSE_VIOLATION`

## 7. Starting cash invariant enforcement

- **Starting cash locked value:** **$50,000**
- **Check in main.Initialize:** True
- **Check in test T7c:** True
- **Violation error class:** `S11_D1_STARTING_CASH_INVARIANT_VIOLATION`
- **main.Initialize check pseudocode:** `if CONFIG['starting_cash_mnq_equivalent'] != 50000: raise S11_D1_STARTING_CASH_INVARIANT_VIOLATION('expected 50000; got ...')`
- Modification post-build forbidden: **True**
- Modification requires fresh candidate_record_id: **True**

## 8. IS / OOS window enforcement

- **IS window:** 2019-05-13 → 2023-12-29
- **OOS window:** 2024-01-02 → 2025-12-30
- Windows locked at SEAL: **True**

### IS driver required constants

- `IN_SAMPLE_START`: `datetime.date(2019, 5, 13)`
- `IN_SAMPLE_END`: `datetime.date(2023, 12, 29)`
- `CSV_PATH`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `CSV_SHA256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

### OOS driver required constants

- `OUT_OF_SAMPLE_START`: `datetime.date(2024, 1, 2)`
- `OUT_OF_SAMPLE_END`: `datetime.date(2025, 12, 30)`
- `CSV_PATH`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `CSV_SHA256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

- IS driver must not reference OOS dates: **True**
- OOS driver must not reference IS dates: **True**
- No OOS inspection during IS phase: **True**
- OOS inspection requires separate post-IS authorization: **True**

## 9. Cost-tier implementation expectations

- Tick size: 0.25 pts; tick value: $0.5; $/pt: $2.00
- Commission per round-trip (baseline): $0.74
- Fees per round-trip (baseline): $0.36

### Cost-stress tiers (REQUIRED in CONFIG)

| Tier | cost_scalar | slippage_scalar |
|---|---:|---:|
| `S0` | 0.0 | 0.0 |
| `S1` | 1.0 | 1.0 |
| `S2` | 1.5 | 1.5 |
| `S3` | 2.0 | 2.0 |
| `S4` | 3.0 | 3.0 |

**Fill cost formula:** `fill_cost_usd = (commission_per_rt * cost_scalar + fees_per_rt * cost_scalar) * contracts + (slip_ticks * slippage_scalar * tick_value_usd * contracts)`

**Net PnL formula:** `net_pnl_usd = gross_pnl_usd - fill_cost_usd`

## 10. K9 / sample-size enforcement expectations

- **K9 threshold:** **100** (inviolate)
- **K9 modification forbidden:** True

**Expected IS trade count:** DAILY DONCHIAN-55/20 ON SINGLE INSTRUMENT OVER 4.6Y IS HISTORICALLY SPARSE: ~25-50 trades expected. BELOW K9=100. K9 fire at IS is STRUCTURALLY POSSIBLE. Pursuing this candidate accepts that risk.

**If K9 fires at IS:** If P6 IS observes closed_trades_portfolio < 100, the orchestrator's K-gate evaluation logic shall record K9 as FIRED. The C7 verdict shall be INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY). The orchestrator shall NOT relax K9; the sealed P6 IS report shall record the verdict honestly and the operator decides next phase (P10 OOS attempt despite undersample, OR P11 PARK at IS stage).

**If K9 fires at OOS:** If P10 OOS observes closed_trades_portfolio < 100, the orchestrator's K-gate evaluation logic shall record K9 as FIRED. The C7 verdict shall be INSUFFICIENT_SAMPLE. The OOS qualitative verdict shall be OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT (or OOS_INDETERMINATE_AND_DIRECTIONALLY_INCONSISTENT) per the S10-D2 P10 verdict derivation pattern. The orchestrator shall NOT relax K9; the appropriate response is P11 PARK memo.

## 11. Native OOS driver requirements

- **OOS driver authored at P3 BUILD (not retrofit):** True

**Lesson from S10-D2:** S10-D2 omitted OOS driver from P3 BUILD and required a P3.6 BUILD-EXTENSION retrofit; S11-D1 explicitly avoids this by including out_of_sample_driver.py in the original P3 BUILD authorization.

**OOS driver pattern:** Sibling file out_of_sample_driver.py at runner_harness/ root, mechanical adaptation from in_sample_driver.py with OOS-specific constants (CACHE_ROOT or CSV_PATH, OUT_OF_SAMPLE_START/END, EXPECTED dimensions, run_out_of_sample function name). Strategy logic shared via lazy import of runner_main.CONFIG.

**OOS driver required constants:**

- `OUT_OF_SAMPLE_START`: `datetime.date(2024, 1, 2)`
- `OUT_OF_SAMPLE_END`: `datetime.date(2025, 12, 30)`
- `CSV_PATH`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `CSV_SHA256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

**Function signature:** `def run_out_of_sample(*, expected_seals: Optional[Dict[str, str]] = None, cost_tier: str = 'S1') -> Dict[str, Any]`

- OOS driver must not reference IS anywhere: **True**
- OOS driver must not have run_in_sample: **True**
- OOS invariants tested at P4: **True**
- P10 orchestrator must NOT monkey-patch any constant: **True**

## 12. Test list and expected behavior

**Total test count:** 30 (17 smoke + 13 OOS invariants)

**Smoke tests file:** `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py`

**OOS invariants tests file:** `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py`

### Smoke tests T1-T15 + T7b + T7c

| Test | Expected behavior |
|---|---|
| `T1_module_imports_clean` | PASS expected: main/execution_guard/drivers importable without QC/databento at module level |
| `T2_runner_class_instantiable` | PASS expected: main.Algo().Initialize() succeeds; _backtest_run_id starts with PHASE2-S11-D1-MNQ-SI- |
| `T3_wilder_atr_synthetic` | PASS expected: ATR(20) on constant TR=2.0 returns 2.0 |
| `T4_donchian_55_20_synthetic` | PASS expected: Donchian high/low matches max/min on first 55 bars |
| `T5_entry_trigger_synthetic_breakout` | PASS expected: synthetic breakout bar exceeds prior 55-day high |
| `T6_stop_placement_at_2n` | PASS expected: stop = entry - 2 * N for long; entry + 2 * N for short |
| `T7_pyramid_trigger_at_05n` | PASS expected: next_pyramid_trigger = entry + 0.5 * N (computed but never invoked) |
| `T7b_add_pyramid_unit_raises_under_max_units_1` | PASS expected: add_pyramid_unit raises RuntimeError 'exceed max_units=1' |
| `T7c_starting_cash_invariant_50000` | PASS expected: CONFIG['starting_cash_mnq_equivalent'] == 50_000 |
| `T8_exit_on_donchian_20_reversal` | PASS expected: today's low < min(last 20 lows) triggers exit |
| `T9_portfolio_cap_uses_unit_count_not_contract_count` | PASS expected: PortfolioCapTracker max_total_units=1; trivially single-instrument |
| `T10_sizing_1pct_floor` | PASS expected: compute_unit_contracts(50000, 50, 2.0, 0.01) returns floor((0.01 * 50000) / (50 * 2.0)) = 5; OR adjust per actual formula |
| `T11_skip_when_contract_count_lt_one` | PASS expected: tiny equity returns 0 contracts |
| `T12_rth_only_filter_attested` | PASS expected: CONFIG['markets_meta']['MNQ']['rth_open_et'] == [9, 30]; rth_close_et == [16, 0] |
| `T13_roll_cost_modeled_1_spread_tick` | PASS expected: CONFIG['markets_meta']['MNQ']['tick_value_usd'] == 0.50 |
| `T14_cost_stress_matrix_S0_S1_S2_S3_S4` | PASS expected: list(CONFIG['cost_stress_tiers'].keys()) == ['S0','S1','S2','S3','S4'] |
| `T15_validator_harness_pass_on_synthetic` | PASS expected: execution_guard.full_guard_check returns overall_pass=True on synthetic algo proxy with LiveMode=False |

### OOS driver invariants tests

| Test | Expected behavior |
|---|---|
| `test_is_driver_does_not_have_oos_constants` | PASS expected |
| `test_oos_driver_cache_path_points_to_csv` | PASS expected: oos_driver.CSV_PATH == sealed CSV path |
| `test_oos_driver_window_start_is_2024_01_02` | PASS expected: OUT_OF_SAMPLE_START == datetime.date(2024, 1, 2) |
| `test_oos_driver_window_end_is_2025_12_30` | PASS expected: OUT_OF_SAMPLE_END == datetime.date(2025, 12, 30) |
| `test_oos_driver_does_not_have_is_window_constants` | PASS expected: no IN_SAMPLE_START/END on OOS driver |
| `test_oos_driver_does_not_reference_is_dates_in_source` | PASS expected: no 2019/2023 dates |
| `test_oos_driver_does_not_have_run_in_sample_function` | PASS expected |
| `test_oos_driver_does_not_reference_run_in_sample` | PASS expected |
| `test_both_drivers_use_same_runner_main_module` | PASS expected: lazy import resolves to same module object |
| `test_runner_main_config_strategy_params_unchanged` | PASS expected: max_units=1, starting_cash=50000, donchian 55/20, ATR 20, 2N stop, 1% risk |
| `test_oos_run_function_signature_matches_is` | PASS expected: same param names + defaults |
| `test_oos_driver_no_top_level_forbidden_imports` | PASS expected: no top-level databento/QC/AlgorithmImports |
| `test_oos_driver_does_not_instantiate_db_historical` | PASS expected (guard docstring allowed) |

- P4 smoke run required after P3 BUILD via separate authorization: **True**
- P4 verdict threshold: all tests PASSED (30/30 expected); any FAIL -> P4 verdict FAIL -> halt before P6 IS

## 13. Halt conditions

- H1: index pre-stage contains any parallel-session file -> halt before stage/commit
- H2: staged-count != authorized-count after pathspec-add -> halt before commit
- H3: any staged path doesn't match an authorized path regex -> halt before commit
- H4: any guarded source file drifts during a build/run -> halt and report drift
- H5: any sealed report reseal-verify fails after write -> halt and report SEAL_ROUNDTRIP_FAIL
- H6: assert_seal_inheritance() fails inside driver -> halt and report SEAL_DRIFT
- H7: CSV sha256 mismatch -> halt and report S11_D1_MNQ_CSV_SHA_MISMATCH
- H8: starting_cash invariant violation -> halt and report S11_D1_STARTING_CASH_INVARIANT_VIOLATION
- H9: LiveMode=True observed -> halt and report S11_D1_LIVE_MODE_REFUSAL
- H10: universe widening attempted -> halt and report S11_D1_UNIVERSE_VIOLATION
- H11: pytest verdict at P4 != all-PASSED -> halt and do not advance to P6 IS
- H12: K9 fires at IS -> verdict INSUFFICIENT_SAMPLE; do NOT relax K9; operator decides next phase
- H13: K-gate K1/K2/K4/K6/K7/K11 fires at IS or OOS -> verdict FAIL_SAFETY; halt and seal park memo
- H14: any DR rule fires at P6.5 -> halt cost-stress sweep; record matrix verdict COST_STRESS_FAIL
- H15: parallel-session file appears in working tree or index during my turn -> halt before any further action

## 14. Commit / staging protocol (byte-equivalent to P1)

- **Lock source:** P1 plan-lock section 'git_staging_commit_protocol_locked' at commit 7d86486

- `pathspec_only_at_every_phase`: **True**
- `git_add_directory_or_dot_forbidden`: **True**
- `git_commit_a_forbidden`: **True**
- `git_commit_no_verify_forbidden`: **True**
- `git_commit_amend_forbidden_unless_authorized`: **True**
- `git_commit_message_via_F_file_required`: **True**
- `pre_stage_status_check_required`: **True**
- `post_stage_diff_cached_check_required`: **True**
- `staged_count_must_equal_authorized_count`: **True**
- `every_staged_path_must_match_regex`: **True**
- `post_commit_git_show_name_status_required`: **True**
- `halt_on_any_unrelated_staged_file`: **True**

## 15. Seal / hash protocol (byte-equivalent to P1)

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
| `TIER_N_SPEC_SEAL_SHA256` | `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24` |
| `PLAN_LOCK_SEAL_SHA256` | `5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648` |
| `PHASE2_PLAN_SEAL_SHA256` | `(will be populated at P2 commit; this file's seal)` |
| `PHASE2_TEMPLATE_MD_SHA256` | `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981` |
| `PHASE2_TEMPLATE_JSON_SHA256` | `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32` |
| `PREDECESSOR_SEAL_SHA256` | `(s10-D1 park report seal or selection plan commit hash; populated at P3 BUILD)` |

## 16. Explicit next-phase authorization wording

P2 phase-2 plan authoring + sealing + commit completes here. The NEXT phase is P3 BUILD (single combined authorization recommended; 16 files including test scaffold + OOS driver). P3 BUILD REQUIRES SEPARATE OPERATOR AUTHORIZATION via: 'AUTHORIZE S11-D1 P3 BUILD ONLY'. The authorization shall reference: (1) Tier-N spec commit 9c63088 seal 077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24; (2) P1 plan-lock commit 7d86486 seal 5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648; (3) this P2 phase-2 plan seal (will be populated at commit time). No phase beyond P3 is pre-approved by this P2 plan. Each subsequent phase (P4 smoke, P6 IS, P6.5 cost-stress, P7 decision memo, P10 OOS gate, P11 lifecycle decision) requires its own separate operator authorization.

- **Next phase pre-approved by this P2 plan:** False
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
- `p1_plan_lock_commit`: `7d86486`
- `p1_plan_lock_seal_sha256`: `5f25134c4c34ee1d0a9ca3004d9ac4dc6a475f52a145680e0994dd4592777648`
- `selection_plan_commit`: `556ab3f`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `s10_d2_park_commit`: `23c7164`
- `s10_d2_park_status`: `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`
- `phase2_safety_template_md_path`: `docs/phase2_safety_contract_template.md`
- `phase2_safety_template_md_sha256`: `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981`
- `phase2_safety_template_json_path`: `docs/phase2_safety_contract_template.json`
- `phase2_safety_template_json_sha256`: `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32`
- `mnq_c0_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `mnq_c0_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`

## Status / labels

- `trading_status`: PAUSED
- `live_status`: BLOCKED_AT_6_GATES
- `research_label`: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE

**Labels:**

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `P2_PHASE2_PLAN_SEALED`
- `S11_D1_MNQ_SINGLE_INSTRUMENT_FALLBACK`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NO_FRC_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_PHASE_PRE_APPROVED_BEYOND_THIS_PHASE2_PLAN`
- `K9_THRESHOLD_INVIOLATE`
- `OOS_INDETERMINATE_RISK_DISCLOSED`
- `C1_C8_SAFETY_CONTRACTS_INHERITED_BYTE_EQUIVALENT`
- `C4_NOT_APPLICABLE_NO_VOL_TARGETING`

## Hard boundaries held (this P2 plan turn)

- no_app_py_touched: True
- no_backtest: True
- no_broker_exchange_api: True
- no_commit_in_orchestrator: True
- no_d5_b005_001_nke_revival: True
- no_data_fetch: True
- no_databento_api_call: True
- no_input_csv_modification: True
- no_k9_relaxation: True
- no_lessons_md_touched: True
- no_live_trading: True
- no_network_call: True
- no_obsidian_touched: True
- no_oos_inspection: True
- no_p1_plan_lock_modification: True
- no_paper_trading: True
- no_parallel_session_file_staging: True
- no_phase2_template_modification: True
- no_phase_pre_approval_beyond_p2: True
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

- Report seal sha256: `eacd2650bbbf1db8d190fd7567cbea869360381234623dd77b2c207ecdc735b1`
- Seal method: LESSON_HUNTER_004 canonical roundtrip
- Reseal verified on disk: YES
