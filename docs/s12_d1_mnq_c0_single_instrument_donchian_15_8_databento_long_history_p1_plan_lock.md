# S12-D1 P1 plan-lock (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase prefix:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8`
**Authored (UTC):** `2026-05-27T14:56:04.217249Z`
**Lifecycle state:** P1_PLAN_LOCK_SEALED
**Tier-N spec inherited byte-equivalent:** commit `66bbbd1` (seal `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`)
**Report seal sha256:** `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES

## Tier-N spec inheritance

This P1 plan-lock document LOCKS the s12-d1 sealed Tier-N spec at commit `66bbbd1` (seal sha `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`) as the operator-confirmed source of truth. The operator's P1 authorization phrase reads verbatim: *"Preserve the SEAL at commit 66bbbd1 as source of truth, including REC1 oos_k9_risk_disclosure."* All Tier-N spec decisions are inherited byte-equivalent into the BUILD phase. No Tier-N spec modification is permitted; any change requires a fresh _revN_ Tier-N spec under a separate authorization.

- Tier-N spec MD path: `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec.md`
- Tier-N spec JSON: `reports/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_sealed.json`
- Tier-N spec seal sha256: `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`
- Tier-N spec commit: `66bbbd1`
- REC1 `oos_k9_risk_disclosure` carried byte-equivalent into this P1: TRUE

### Parallel-session SEAL acknowledgment (READ-ONLY; not anchored by this P1)

A parallel-session SEAL exists at commit `9ce4d66` at different paths (`docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_tier_n_spec.md` and `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_tier_n_spec_sealed.{json,md}`; shorter-path naming missing `_databento_long_history`). The operator's P1 authorization explicitly preserved THIS chain's SEAL at `66bbbd1` as source of truth; the parallel SEAL at `9ce4d66` is byte-stable and is NOT anchored by this P1. This P1 plan-lock does NOT supersede, modify, or re-anchor the parallel SEAL.

## 1. Exact implementation files allowed for P3 BUILD

**Total allowed file count:** 16

### Source files (5)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/__init__.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/main.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/execution_guard.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/in_sample_driver.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/out_of_sample_driver.py`

### Test scaffold files (5)
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/__init__.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/conftest.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py`
- `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py`

### Sealed BUILD report files (6)
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_build_report.json`
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_build_report.md`
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_in_sample_driver_build_report.json`
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_in_sample_driver_build_report.md`
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_out_of_sample_driver_build_report.json`
- `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_out_of_sample_driver_build_report.md`

### Creation pattern

P3 BUILD shall be split into 3 sub-phases (sequential, each separately authorized): P3-RUNNER (source files + runner build report), P3-IS-DRIVER (in_sample_driver.py + IS driver build report), and P3-OOS-DRIVER (out_of_sample_driver.py + OOS driver build report). OR P3 may be a single combined authorization if the operator prefers; the P1 plan-lock does not pre-impose a sub-split.

### Test scaffold inclusion

P1 plan-lock RECOMMENDS including the test scaffold (`tests/__init__.py`, `conftest.py`, synthetic fixture, `test_smoke_t1_t15.py`, `test_oos_driver_invariants.py`) in the original P3 BUILD authorization to avoid the S10-D2-style P3.5 retrofit pattern.

## 2. Files explicitly forbidden during all S12-D1 phases

(See JSON sidecar field `files_explicitly_forbidden_during_all_s12_d1_phases` for the full 35-item list; verbatim notable items below.)

- All s11-d1 v1 / P1 / P2 / clarification memo / rev2 sealed artifacts (BYTE-STABLE; off-limits)
- The s12-d1 SEAL Tier-N spec files at commit `66bbbd1` (LOCKED at SEAL; mod requires fresh _revN_)
- **Parallel-session SEAL artifacts at commit `9ce4d66`** (operator preserved THIS chain's SEAL at `66bbbd1` as source of truth; parallel SEAL is byte-stable and off-limits to this P1 chain)
- Parallel-session DRAFT review at commit `07be7fc`
- Parallel-session OOS K9 addendum memo at commit `538eaf3`
- Parallel-session S10-D2 vs S11-D1 comparison memo at commit `1bf45bc`
- `brain_memory/projects/trading_bot/lessons.md` (long-running parallel-session dirty file; explicitly off-limits in EVERY S12-D1 phase)
- All S10-D2 / s10-D1 / s9 / s7-D1 / B005_NNN / B006_001 / B006_002 / T8 / NKE / s8-D1 sealed artifacts
- `review_queue.json` / production `idea_memory` / Strategy Lab / ORB / obsidian / app.py / templates/base.html / CLAUDE.md / etc.
- This P1 plan-lock document itself once committed (requires fresh _revN_ plan-lock under separate authorization)
- Any file outside the `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` namespace

## 3. Input data path and sha requirement

| Field | Value |
|---|---|
| `primary_path` | data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv |
| `primary_sha256_required` | 8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e |
| `primary_row_count` | 2066 |
| `primary_observed_window` | 2019-05-13, 2025-12-29 |
| `primary_format` | CSV (daily bars with ts_event index) |
| `primary_access` | READ-ONLY; byte-equivalent reuse from s10-D1 sealed fetch |
| `fresh_fetch_required` | False |
| `fresh_fetch_authorized_by_this_plan_lock` | False |
| `build_phase_must_verify_csv_sha_at_runtime` | True |
| `build_phase_must_fail_loudly_if_sha_mismatch` | True |
| `fail_loud_error_class_name` | `S12_D1_MNQ_CSV_SHA_MISMATCH` |

## 4. Strategy mechanic boundaries (LOCKED; carried byte-equivalent from SEAL at `66bbbd1`)

| Field | Value | Notes |
|---|---|---|
| `mechanic_family` | F1 long+short bi-directional Donchian, no pyramid, ATR-stop, 1% per-trade risk | LOCKED at PLAN |
| `donchian_entry_period_n` | **15** | LOCKED at PLAN; load-bearing departure from s11-d1 v1's 55 |
| `donchian_exit_period_n` | **8** | LOCKED at PLAN; load-bearing departure from s11-d1 v1's 20 |
| `atr_period` | 20 | DA1=A; Wilder |
| `atr_method` | Wilder | byte-equivalent |
| `stop_multiplier_in_atr` | 2.0 | DA2=A |
| `risk_pct_per_trade` | 0.01 | DA3=A |
| `max_units_per_market` | 1 | LOCKED non-negotiable |
| `max_total_units` | 1 | trivially single-instrument |
| `pyramid_method` | NONE | LOCKED non-negotiable |
| `amb6_filter` | NONE | LOCKED |
| `regime_overlay` | NONE | LOCKED |
| `correlation_filter` | NOT APPLICABLE (single instrument) | -- |
| `vol_targeting` | NONE | not vol-targeting mechanic family |
| `leverage_cap` | NONE implicit via 1% per-trade risk sizing; no separate C4 | DR11 structurally absent |
| **`starting_cash_mnq_equivalent`** | **100000** | **DA4=B revised at SEAL from $50k for DR10 mitigation** |
| `starting_cash_invariant_error_class` | `S12_D1_STARTING_CASH_INVARIANT_VIOLATION` | -- |
| `tick_size_points` | 0.25 | byte-equivalent |
| `tick_value_usd` | 0.5 | byte-equivalent |
| `dollar_per_point` | 2.0 | byte-equivalent |
| `contract_multiplier_note` | MNQ: $2 * Nasdaq-100 index value per point | -- |
| `rth_window_et` | `{"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0, "tz": "America/New_York"}` | DA12=A |
| `intraday_data_used` | False | -- |
| `daily_bars_only` | True | -- |
| `roll_method` | Continuous front-month per Databento `stype_in=continuous`; no operator-side roll override | byte-equivalent |
| `modification_post_build_forbidden` | True | non-negotiable |
| `modification_requires_fresh_candidate_record_id` | True | non-negotiable |

## 5. IS / OOS split enforcement

- **IS window:** `2019-05-13 -> 2023-12-29`
- **OOS window:** `2024-01-02 -> 2025-12-30`
- **Locked at SEAL:** True

**Structural enforcement in drivers:**

- `in_sample_driver_filters_to_is_window_only`: True
- `in_sample_driver_constants`: `IN_SAMPLE_START = datetime.date(2019, 5, 13)`, `IN_SAMPLE_END = datetime.date(2023, 12, 29)`, `CSV_PATH_HARDCODED`, `CSV_SHA256_HARDCODED`
- `out_of_sample_driver_filters_to_oos_window_only`: True
- `out_of_sample_driver_constants`: `OUT_OF_SAMPLE_START = datetime.date(2024, 1, 2)`, `OUT_OF_SAMPLE_END = datetime.date(2025, 12, 30)`, `CSV_PATH_HARDCODED`, `CSV_SHA256_HARDCODED`
- `oos_inspection_during_is_phase_blocked_by_separate_files`: True
- `drivers_are_authored_at_p3_build_as_siblings`: True
- `no_p3_5_retrofit_planned_for_oos_driver`: True

## 6. Cost tier definitions (LOCKED)

**Baseline costs (S1 = 1.0x scalar):**
- Commission per round-trip: $0.74
- Fees per round-trip: $0.36
- Slippage entry/stop/exit ticks: 1 / 1 / 1

**Cost-stress tiers (5-tier; DA7=A; carried byte-equivalent from SEAL):**

| Tier | cost_scalar | slippage_scalar | Note |
|---|---:|---:|---|
| `S0` | 0.0 | 0.0 | zero-cost ideal |
| `S1` | 1.0 | 1.0 | baseline retail (DEFAULT) |
| `S2` | 1.5 | 1.5 | stressed retail |
| `S3` | 2.0 | 2.0 | adversarial |
| `S4` | 3.0 | 3.0 | extreme adversarial |

## 7. K9 / sample-size rules (REC1 carried byte-equivalent from SEAL)

- **K9 threshold:** **100** (`closed_trades_portfolio < 100`)
- K9 threshold modification forbidden: True
- K9 relaxation at any phase forbidden: True

### IS K9 disclosure

**Expected IS trade count estimate:** Donchian-15/8 bi-directional on MNQ.c.0 over 4.6y IS expected approximately **80 (low) / 140 (central) / 200 (high)** portfolio trades; ~3-4x s11-d1 v1's Donchian-55/20 expectation of 25-50 trades. K9 risk at IS phase: **borderline at lower bound** -- lower estimate 80 < K9; central estimate 140 clears with margin; upper estimate 200 clears comfortably.

### OOS K9 disclosure (REC1 carried byte-equivalent from SEAL `66bbbd1` §9.2)

**OOS K9 STRUCTURALLY UNREACHABLE.** Implied OOS trade count over 2.0y at IS rate is approximately **35 (low) / 61 (central) / 87 (high)** trades, **all below K9 = 100**. Even the upper estimate (87) falls below K9. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome (analogous to S10-D2 P11 PARK at `23c7164` -- PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED).

| Window | Length (y) | Per-year rate | Expected trades | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | 17.4 / 30.4 / 43.5 | 80 / 140 / 200 | central CLEARS K9 with margin |
| **OOS** | **2.0** | (carried from IS rate) | **35 / 61 / 87** | **STRUCTURALLY UNREACHABLE** |

**If K9 fires at IS:** Verdict shall be INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY). Chain shall NOT relax K9. Operator decides between (a) continuing to P10 OOS despite IS being undersampled, (b) parking s12-d1 with PARK memo at IS stage, or (c) selecting a different mechanic family in a fresh candidate.

**If K9 fires at OOS:** Verdict shall be INSUFFICIENT_SAMPLE / OOS_INDETERMINATE. Chain shall NOT relax K9. Appropriate response is to park s12-d1 with PARK memo analogous to S10-D2 P11 PARK. This is the EXPECTED terminal verdict per REC1 disclosure.

## 8. Rejection rules (LOCKED)

### K-gates

| K-gate | Trigger |
|---|---|
| `K1_sharpe_proxy_lt_0` | FAIL_SAFETY trigger |
| `K2_expectancy_le_0` | FAIL_SAFETY trigger |
| `K4_trade_curve_maxdd_magnitude_gt_50` | FAIL_SAFETY trigger (\|maxdd_pct\| > 50%; DA5=A) |
| `K6_safety_warning_count_gt_0` | NOT APPLICABLE (single instrument) |
| `K7_correlation_or_filter_silently_introduced` | FAIL_SAFETY trigger |
| `K8_sealed_parent_drift` | FAIL_SAFETY trigger (parent seal mismatch) |
| `K9_closed_trades_lt_100` | INSUFFICIENT_SAMPLE trigger (NOT FAIL_SAFETY) |
| `K10_avg_pairwise_corr` | NOT APPLICABLE (single instrument) |
| `K11_cap_binding_events` | NOT APPLICABLE (F1 no leverage cap) |
| `K12_DR_fires_on_cost_stress` | evaluated at P6.5 cost-stress sweep |

### DR rules (P6.5 cost-stress sweep; LOCKED non-negotiable per `no_dr_redefinition_post_seal`)

| DR | Trigger |
|---|---|
| `DR2_tier_net_pnl_le_0` | fires if any non-baseline tier net_pnl <= 0 |
| `DR3_tier_sharpe_proxy_le_0` | fires if any non-baseline tier sharpe <= 0 |
| `DR4_tier_expectancy_le_0` | fires if any non-baseline tier expectancy <= 0 |
| `DR5_tier_closed_trades_lt_100` | fires if any non-baseline tier closed_trades < 100 |
| `DR10_turnover_cost_explosion` | fires if annual_turnover > 0.50 OR S2 cost drag > 0.05; **ELEVATED prior probability** vs s11-d1 v1; mitigated via DA4=B START_CASH=$100k |

### A-gates (P6 IS)

| A-gate | Behavior |
|---|---|
| `A1_closed_trades_ge_100` | fail -> INSUFFICIENT_SAMPLE |
| `A2_sharpe_proxy_gt_0` | fail -> FAIL_SAFETY |
| `A3_expectancy_gt_0` | fail -> FAIL_SAFETY |
| `A4_trade_curve_maxdd_pct_magnitude_le_50` | fail -> FAIL_SAFETY (50%; byte-equivalent from s11-d1 v1 K4 formula per DA5=A) |
| `A5` | NOT APPLICABLE (single instrument) |
| `A6_no_pyramid_attestation_pass` | fail -> FAIL_SAFETY |
| `A7_effective_independent_bets` | NOT APPLICABLE (trivially 1) |
| `A8_cost_stress_S0_S4_run` | evaluated at P6.5 |
| `A9_phase2_c1_c8_inheritance_attestable` | fail -> FAIL_SAFETY |
| `A10_cap_binding_events_eq_0` | fail -> FAIL_SAFETY |

**Invariants:**
- No threshold loosening: True
- No DR redefinition post-SEAL: True
- No filter introduction post-SEAL: True
- No universe widening: True
- No starting cash modification: True
- No strategy parameter modification: True
- FAIL_SAFETY terminal: True

## 9. Promotion rules (LOCKED)

- `permanent_live_block`: **True**
- `permanent_paper_block_via_broker_api`: **True**
- `live_promotion_blocked_at_6_gates_permanently`: **True**
- `no_verdict_unblocks_*`: **True** (live, paper, FRC, Strategy Lab promotion, review_queue mutation)
- `promotion_at_any_stage_is_OUT_OF_SCOPE`: **True**
- `research_diagnostic_only`: **True**
- `no_profitability_claim`: **True**

## 10. Test plan (P4 synthetic smoke; adapted for Donchian-15/8 + START_CASH $100k)

**Test battery:** S12-D1 P4 synthetic smoke (T1-T15 + T7b + T7c)
**Test count:** 17 minimum
**Synthetic fixture path:** `external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`

### Tests required (T1-T15 + T7b + T7c; s12-d1 adaptations marked)

| Test | Description |
|---|---|
| `T1_module_imports_clean` | main + execution_guard + drivers importable without QC/databento at module level |
| `T2_runner_class_instantiable` | main.Algo() Initialize() succeeds without QC runtime |
| `T3_wilder_atr_synthetic` | ATR(20) on constant 21-bar TR series returns 2.0 |
| **`T4_donchian_15_8_synthetic`** | **(s12-d1-specific)** Donchian-15 high/low and Donchian-8 high/low on synthetic series match max/min |
| **`T5_entry_trigger_synthetic_breakout`** | **(s12-d1-specific Donchian-15)** synthetic 15-day breakout bar triggers long entry |
| `T6_stop_placement_at_2n` | stop = entry - 2 * N for long |
| `T7_pyramid_trigger_at_05n` | pyramid trigger COMPUTED at +0.5N (but invocation forbidden) |
| `T7b_add_pyramid_unit_raises_under_max_units_1` | add_pyramid_unit raises RuntimeError when max_units=1 |
| **`T7c_starting_cash_invariant_100000`** | **(s12-d1-specific; DA4=B)** CONFIG['starting_cash_mnq_equivalent'] == 100_000 |
| **`T8_exit_on_donchian_8_reversal`** | **(s12-d1-specific)** Donchian-8 reversal triggers exit |
| `T9_portfolio_cap_uses_unit_count_not_contract_count` | max_total_units=1 enforced |
| **`T10_sizing_1pct_floor`** | **(s12-d1-specific arithmetic)** compute_unit_contracts returns floor((0.01 * 100000) / (ATR_entry * 0.5)) for s12-d1 START_CASH=$100k |
| `T11_skip_when_contract_count_lt_one` | tiny equity returns 0 contracts |
| `T12_rth_only_filter_attested` | RTH window 09:30-16:00 ET in CONFIG |
| `T13_roll_cost_modeled_1_spread_tick` | tick_value_usd=0.50 in CONFIG |
| `T14_cost_stress_matrix_S0_S1_S2_S3_S4` | 5 tiers in CONFIG['cost_stress_tiers'] |
| `T15_validator_harness_pass_on_synthetic` | execution_guard.full_guard_check returns overall_pass=True on synthetic algo proxy |

### OOS driver invariants tests

(See JSON sidecar `oos_driver_invariants_tests_required` for full list. Key adaptations: OOS driver CONFIG must show `donchian_entry_period_n=15`, `donchian_exit_period_n=8`, `starting_cash_mnq_equivalent=100000`; no db.Historical() call since s12-d1 reuses sealed CSV.)

### Pytest run protocol at P4

- Invocation: `python -u -m pytest <test_file> -v --no-header --tb=short -p no:cacheprovider --rootdir <tests_dir> --confcutdir <tests_dir> --import-mode=importlib`
- Env guards: `PYTHONPATH=C:\SPARTA_BRAIN`; `HTTP_PROXY=invalid`; `DATABENTO_API_KEY` popped
- Expected wall: ~1s (synthetic; no real data decode)
- Verdict threshold: all tests PASSED; any FAIL -> P4 verdict FAIL

## 11. Output artifact plan per phase

| Phase | Files |
|---|---|
| `p1_plan_lock_this_turn` | `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_p1_plan_lock.md` + `reports/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_p1_plan_lock_sealed.json` |
| `p2_phase2_plan_future` | `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_p2_phase2_plan.md` + `reports/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_p2_phase2_plan_sealed.json` |
| `p3_build_future` | see section 1 (5 source + 5 test + 6 sealed-report files) |
| `p4_smoke_future` | `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_smoke_t1_t15_report.{json,md}` |
| `p6_is_future` | `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_in_sample_diagnostic_result_sealed.{json,md}` |
| `p6_5_cost_stress_future` | `reports/external_research_hunter/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_cost_stress_matrix_result_sealed.{json,md}` |
| `p7_decision_memo_future` | `reports/s12_d1_p7_decision_memo_sealed.{json,md}` |
| `p10_oos_gate_future` | `reports/s12_d1_p10_oos_gate_sealed.{json,md}` |
| `p11_lifecycle_decision_future` | `reports/s12_d1_p11_lifecycle_memo_sealed.{json,md}` |

- `naming_locked_at_p1`: True
- `deviation_requires_per_phase_explicit_authorization`: True

## 12. Seal / hash protocol (LOCKED)

- **Seal method:** LESSON_HUNTER_004 canonical roundtrip
- **Canonical form:** `json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False, default=str)`
- **Excluded keys:** `['report_seal_sha256', 'seal_method']`
- **Hash algorithm:** sha256
- **Encoding:** utf-8
- **Reseal verify required after write:** True
- **Reseal mismatch error class:** `SEAL_ROUNDTRIP_FAIL`

### Embedded constants in drivers (validated via assert_seal_inheritance at P3 BUILD)

| Constant | Value |
|---|---|
| `PREDECESSOR_PARK_REF_S10_D1` | `1a9acec` |
| `PREDECESSOR_PARK_REF_S10_D2` | `23c7164` |
| `PREDECESSOR_SEAL_REF_S11_D1_V1` | `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24` |
| `PREDECESSOR_SEAL_REF_S11_D1_REV2` | `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d` |
| `TIER_N_SPEC_SEAL_SHA256` | `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` |
| `PLAN_LOCK_SEAL_SHA256` | `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` |
| `PHASE2_PLAN_SEAL_SHA256` | (will be populated at P2 commit under separate authorization) |
| `REC1_OOS_K9_DISCLOSURE_CARRIED_FROM_SEAL` | True |

## 13. Git staging / commit protocol (LOCKED)

(See JSON sidecar field `git_staging_commit_protocol_locked` for full pre-stage / staging / commit / post-commit verification protocol.)

- **Staging pattern:** `git add -- <exact authorized file paths>`
- **Staging pattern forbidden:** `git add . / git add -A / git add * / git add <directory>`
- **Always-on invariants:** pathspec only at every phase, no force push, no amend without explicit authorization, no rebase without explicit authorization, no branch creation without explicit authorization, no remote push without explicit authorization

## 14. Explicit next-phase requirement

P1 plan-lock authoring + sealing + commit completes here. The NEXT phase is **P2 phase-2 plan**. P2 phase-2 plan REQUIRES SEPARATE OPERATOR AUTHORIZATION via the phrase: **"Authorize s12 D1 MNQ.c.0 P2 phase-2 plan only"**.

The P2 phase-2 plan shall adapt `docs/phase2_safety_contract_template.md` C1-C8 byte-equivalent for s12-d1 with single-instrument adaptations where the template requires per-market parameters.

**NO PHASE BEYOND P2 IS PRE-APPROVED by this P1 plan-lock.** Each subsequent phase (P3 BUILD, P4 smoke, P6 IS, P6.5 cost-stress, P7 decision memo, P10 OOS gate, P11 lifecycle decision) requires its own separate operator authorization.

- Next phase pre-approved by this plan-lock: **False**
- P2 phase-2 plan requires separate authorization: **True**
- P3 BUILD requires separate authorization: **True**
- P4 smoke requires separate authorization: **True**
- P6 IS requires separate authorization: **True**
- P6.5 cost-stress requires separate authorization: **True**
- P7 decision memo requires separate authorization: **True**
- P10 OOS gate requires separate authorization: **True**
- P11 lifecycle decision requires separate authorization: **True**

## Parent references (READ-ONLY)

- `tier_n_spec_commit`: `66bbbd1` (s12-d1 SEAL; operator-preserved source of truth)
- `tier_n_spec_seal_sha256`: `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48`
- `s12_d1_plan_commit`: `b4eac65`
- `s12_d1_draft_commit`: `7e9c867`
- `s11_d1_v1_spec_commit`: `9c63088`
- `s11_d1_v1_spec_seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- `s11_d1_rev2_commit`: `c110fd4`
- `s11_d1_rev2_seal_sha256`: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
- `s11_d1_p1_plan_lock_commit`: `7d86486`
- `s11_d1_p2_phase_2_plan_commit`: `f64f984`
- `s11_d1_clarification_memo_commit`: `d13b56a`
- `s10_d2_park_commit`: `23c7164`
- `s10_d1_mnq_mgc_park_commit`: `1a9acec`
- `mnq_c0_csv_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `mnq_c0_csv_sha256`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- `mnq_c0_csv_row_count`: `2066`
- `mnq_c0_csv_observed_window`: `['2019-05-13', '2025-12-29']`

## Status / labels

- `trading_status`: PAUSED
- `live_status`: BLOCKED_AT_6_GATES
- `frc_status`: NEVER_GRANTED
- `research_label`: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
- `lifecycle_state`: P1_PLAN_LOCK_SEALED

**Labels:**

- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `P1_PLAN_LOCK_SEALED`
- `S12_D1_MNQ_DONCHIAN_15_8_FRESH_CANDIDATE`
- `NOT_LIVE_READY`
- `NOT_PAPER_READY`
- `NO_FRC_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_PHASE_PRE_APPROVED_BEYOND_THIS_PLAN_LOCK`
- `K9_THRESHOLD_INVIOLATE`
- `OOS_K9_STRUCTURALLY_UNREACHABLE_REC1_CARRIED`
- `DR10_RISK_ELEVATED_MITIGATED_VIA_DA4_B_START_CASH_100K`
- `DONCHIAN_15_8_LOCKED_AT_PLAN_NO_RETREAT_TO_55_20`
- `MECHANIC_FAMILY_F1_LOCKED_AT_PLAN_NO_REOPENING`
- `TIER_N_SPEC_LOCKED_BYTE_EQUIVALENT_AT_66BBBD1`
- `PARALLEL_SEAL_AT_9CE4D66_ACKNOWLEDGED_NOT_ANCHORED`
- `ADDENDUM_MEMO_REC1_CARRIED_BYTE_EQUIVALENT_FROM_SEAL`

## Hard boundaries held (this P1 plan-lock turn)

See JSON sidecar field `hard_boundaries_held_this_p1_plan_lock_turn` for full attestation (~37 boundaries; all True). Key additions specific to s12-d1:
- `no_modification_of_s12_d1_seal_at_66bbbd1`: True (operator-preserved source of truth)
- `no_modification_of_parallel_session_seal_at_9ce4d66`: True (parallel-session SEAL acknowledged not anchored)
- `preserves_seal_at_66bbbd1_as_source_of_truth_per_operator_authorization`: True
- `rec1_oos_k9_risk_disclosure_carried_byte_equivalent`: True

## Seal metadata

- **Report seal sha256:** `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip (json.dumps `sort_keys=True separators=',:' ensure_ascii=False default=str` EXCLUDING `report_seal_sha256` + `seal_method`)
- **Reseal verified on disk:** YES (in-script roundtrip assertion passed)
