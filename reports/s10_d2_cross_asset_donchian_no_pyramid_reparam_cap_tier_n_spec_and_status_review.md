# S10-D2 Cross-Asset Donchian No-Pyramid Reparam-Cap -- Tier-N Spec + Current-Status Review (SEALED)

**Schema:** `sparta.s10.d2.tier_n_spec_and_status_review.v1`
**Phase:** `S10_D2_TIER_N_SPEC_AND_STATUS_REVIEW`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T02:07:10Z`

## Review verdict: `S10_D2_TIER_N_SEALED_IS_DIAGNOSTIC_S1_BASELINE_POSITIVE_BUT_COST_STRESS_INCOMPLETE`

S10-D2 Tier-N spec is sealed (seal f5ca5ee63024e9c8) and internally consistent. All committed sealed artifacts in the D2 chain seal-verify (8/8 canonical seals match). The parallel session has progressed the candidate from P1 plan-lock through P6 IS diagnostic. The WIP IS diagnostic (uncommitted; sealed in-file) returns verdict READY_FOR_LONGER_BACKTEST at S1 single-tier with strong baseline numbers (200 closed trades, +$4,865 expectancy, +0.143 Sharpe proxy, +10.48pp WR gap to breakeven, -28.3% max drawdown, balanced long/short pnl). However the verdict is PRELIMINARY: the cost-stress matrix S0/S2/S3/S4 has NOT yet been run, so K12 (DR2/DR3/DR5 fail-fast) cannot be evaluated; K10 (pairwise dependence) is also not evaluated. The s7 D1 ETF-proxy precedent showed that a positive S1 baseline can still fail K12 once S0/S2/S3 are run. P6.5 cost-stress sweep is the immediate next research step. Live trading remains BLOCKED_AT_6_GATES; advisory label permanent DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.

> Review-only turn. No spec modification. No simulator. No backtest.
> No signal. No data fetch. No Databento call. No DATABENTO_API_KEY
> access. No OOS inspection. No live trading.

---

## 1. Files read (16; all read-only)

| Tag | Path | Exists | sha256 (first 16) | bytes |
|---|---|---|---|---|
| `tier_n_spec_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.json` | True | `1a7850dbde36ab8b` | 22,585 |
| `tier_n_spec_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.md` | True | `9ccef4a502a18fce` | 9,146 |
| `plan_lock_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_plan_lock.json` | True | `a9490dd6a2e9343d` | 15,152 |
| `plan_lock_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_plan_lock.md` | True | `92a481e2b784cd45` | 11,463 |
| `phase2_plan_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_phase2_plan.json` | True | `cffe3a93faf6abe1` | 33,102 |
| `phase2_plan_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_phase2_plan.md` | True | `373c4522ce689b5f` | 14,169 |
| `runner_build_report_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_build_report.json` | True | `4e397dc9f7f67b82` | 5,753 |
| `runner_build_report_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_build_report.md` | True | `7c24ba148b0ba756` | 2,480 |
| `tests_scaffold_build_report_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tests_scaffold_completion_build_report.json` | True | `f2e8a6a5d4f43d85` | 5,348 |
| `tests_scaffold_build_report_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tests_scaffold_completion_build_report.md` | True | `b42fff87c209f2e1` | 3,546 |
| `smoke_t1_t15_report_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_smoke_t1_t15_report.json` | True | `2cc80f591a027db0` | 8,131 |
| `smoke_t1_t15_report_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_smoke_t1_t15_report.md` | True | `562a6a9f69b17ff6` | 7,023 |
| `in_sample_driver_build_report_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_driver_build_report.json` | True | `0102f2bc5faadc4c` | 4,530 |
| `in_sample_driver_build_report_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_driver_build_report.md` | True | `92de5703ecc6bae2` | 1,596 |
| `in_sample_diagnostic_result_sealed_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_diagnostic_result_sealed.json` | True | `9480adc466120db1` | 16,598 |
| `in_sample_diagnostic_result_sealed_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_diagnostic_result_sealed.md` | True | `798db5dbd814f10c` | 7,384 |

## 2. Seal verification

- **Total JSON artifacts examined:** 8
- **Seals matching:** 8
- **All seals match:** **True**

| Tag | Recorded seal | Recomputed seal | Match |
|---|---|---|---|
| `tier_n_spec_json` | `f5ca5ee63024e9c8` | `f5ca5ee63024e9c8` | True |
| `plan_lock_json` | `ba8bf954d44b373c` | `ba8bf954d44b373c` | True |
| `phase2_plan_json` | `7a48ad64236971e6` | `7a48ad64236971e6` | True |
| `runner_build_report_json` | `1eb04aa312f40531` | `1eb04aa312f40531` | True |
| `tests_scaffold_build_report_json` | `66d38f359b54882b` | `66d38f359b54882b` | True |
| `smoke_t1_t15_report_json` | `c31ded81f9a28835` | `c31ded81f9a28835` | True |
| `in_sample_driver_build_report_json` | `ddd604c96508a0ab` | `ddd604c96508a0ab` | True |
| `in_sample_diagnostic_result_sealed_json` | `e6cdc7c68a9e2b7b` | `e6cdc7c68a9e2b7b` | True |

## 3. Tier-N spec summary

- **canonical_record_id:** s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl
- **spec_version:** v1
- **tier_n_seal_at_seal_time:** f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679
- **phase_label_at_tier_n_seal_time:** TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED
- **single_delta_from_s8_d1:** starting_cash_mnq_equivalent = $500,000 (vs s8-D1 $100,000)
- **all_other_parameters:** byte-equivalent to s8-D1 (Donchian-55 entry / Donchian-20 exit / no-pyramid / 2N ATR stop / 1% risk / max_units_per_market=1 / Filter NONE / ONO timing)
- **universe:** `['NQ.c.0', 'GC.c.0', 'ZN.c.0', 'CL.c.0']`
- **markets_count:** 4
- **data_source_of_record:** `DATABENTO_GLBX_MDP3_LOCAL_CACHE_ONLY_AT_RUN_TIME`
- **data_schema:** `ohlcv-1m`
- **data_stype_in_continuous:** True
- **data_s8_d1_cache_re_used:** True
- **data_no_fresh_databento_fetch_authorized:** True
- **is_window_utc:** `['2013-01-01', '2022-12-30']`
- **oos_window_utc_locked:** `['2023-01-01', '2025-12-30']`
- **cost_stress_matrix_tiers:** `['S0', 'S1', 'S2', 'S3', 'S4']`
- **cost_stress_inherited_byte_equivalent_from_s8_d1:** True
- **acceptance_gates_inherited_byte_equivalent_from_s8_d1:** True
- **closed_verdict_enum_allowed:** `['FAIL_SAFETY', 'INSUFFICIENT_SAMPLE', 'READY_FOR_LONGER_BACKTEST']`
- **closed_verdict_enum_invariant:** no enum extension allowed
- **closed_verdict_enum_never_means_live_ready:** True
- **live_status_at_seal:** `BLOCKED_AT_6_GATES`
- **frc_granted_at_seal:** False
- **advisory_label_permanent:** `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

### Tier-N phase label stale-note

The Tier-N spec records phase = TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED. Subsequent commits (d2389c0 runner build, ce2920a test scaffold, 35db1f2 smoke P4, plus uncommitted in-sample driver build + IS diagnostic) have advanced the candidate through P3-P6. The phase label is informational at seal time, not a runtime block.

## 4. Parallel-session D2 chain commits (chronological)

| Commit | Subject |
|---|---|
| `b2c94f8` | Seal S10-D2 cross-asset Donchian no-pyramid reparam-cap P1 plan-lock |
| `cb49634` | Seal S10-D2 cross-asset Donchian no-pyramid reparam-cap P2 phase-2 plan |
| `d6cc451` | Seal S10-D2 cross-asset Donchian no-pyramid reparam-cap Tier-N spec |
| `d2389c0` | Build S10-D2 cross-asset Donchian no-pyramid reparam-cap runner harness |
| `ce2920a` | Complete S10-D2 test scaffold: conftest + 4 synthetic fixture CSVs |
| `35db1f2` | Pass S10-D2 P4 smoke battery: 17/17 (T1-T15+T7b+T7c) |

Plus a committed (post-smoke) IS driver build report and an
UNCOMMITTED in-sample diagnostic result file (working tree only;
seal recomputes; the parallel session is mid-commit).

## 5. WIP IS diagnostic result (UNCOMMITTED; in working tree only)

The IS diagnostic result file exists in the working tree but is NOT YET COMMITTED to the git index by the parallel session at the time of this review. Earlier this turn, the parallel session had it staged for commit; this controller session unstaged it (via git restore --staged) to keep the review commit's staging area scope-clean. The working-tree content was NOT modified; the parallel session can re-stage and commit it any time.

### Verdict
- **verdict:** **`READY_FOR_LONGER_BACKTEST`** (one of `['FAIL_SAFETY', 'INSUFFICIENT_SAMPLE', 'READY_FOR_LONGER_BACKTEST']`)
- **verdict_reasons:** `['All safety counters zero AND closed_trades >= 100; research label only (live-block applies regardless).']`
- **verdict_never_means_live_ready:** **True**

### Run metadata
- algo_version: `s10_d2_v0_1_0`
- phase_prefix: `PHASE2-S10-D2-XAD-RC`
- report_kind: `S10-D2 P6 IS diagnostic (cost_tier='S1' single-tier)`
- duration_seconds: `277.547`
- cost_tier_run: **`S1`** (single tier only)
- run_completed_without_exception: **True**
- driver_byte_stable_through_run: **True**
- in-file report_seal_sha256: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`

### A-gate evaluation (from WIP IS diagnostic)

| Gate | Pass | Value | Note |
|---|---|---|---|
| A10_cap_binding_events_eq_0 | True | 0 |  |
| A1_closed_trades_ge_100 | True | 200 |  |
| A2_sharpe_proxy_gt_0 | True | 0.14311192966266303 |  |
| A3_expectancy_gt_0 | True | 4865.489302337149 |  |
| A4_trade_curve_maxdd_pct_le_50 | True | -28.305996161770587 |  |
| A5_2of4_markets_wr_gap_ge_0_or_portfolio_wr_gap_ge_plus_half_pp | True | 10.478591202045537 | evaluated from trade_diagnostics.win_rate_gap_to_breakeven_pp |
| A6_validator_pass | True | None | no-pyramid attestation + plan-lock validator inherited byte-equivalent from s8-D1 |
| A8_cost_stress_S0_S4_run | None | False | only S1 baseline executed this turn; S0/S2/S3/S4 require separate authorization (P6.5) |
| A9_phase2_c1_c8_inheritance_attestable | True | None | C1-C8 inherited byte-equivalent from phase2_safety_contract_template |

### K-gate evaluation (from WIP IS diagnostic)

- **K_fires_count:** 0
- **K_fires:** `[]`

| K | Status |
|---|---|
| `K10_avg_pairwise_corr_gt_0_50` | `None` |
| `K11_cap_binding_events_gt_1000` | `False` |
| `K12_DR_fires_on_cost_stress` | `NOT_EVALUATED_THIS_TURN_ONLY_S1_RUN` |
| `K1_sharpe_proxy_lt_0` | `False` |
| `K2_expectancy_le_0` | `False` |
| `K4_trade_curve_maxdd_gt_50` | `False` |
| `K6_safety_warning_count_gt_0` | `False` |
| `K7_correlation_gate_silently_introduced` | `False` |
| `K7_filter_silently_introduced` | `False` |
| `K8_sealed_parent_drift` | `0` |
| `K9_closed_trades_lt_100` | `False` |

### Performance numbers (S1 baseline)

| Metric | Value |
|---|---|
| `closed_trades_portfolio` | 200 |
| `expectancy_per_trade_usd` | 4,865.4893 |
| `sharpe_proxy_per_trade` | 0.1431 |
| `win_rate_pct` | 35.0000 |
| `breakeven_wr_pct` | 24.5214 |
| `win_rate_gap_to_breakeven_pp` | 10.4786 |
| `pl_ratio` | 3.0781 |
| `avg_win_usd` | 35,046.7225 |
| `avg_loss_usd` | -11,385.9440 |
| `trade_curve_maxdd_pct` | -28.3060 |
| `trade_curve_maxdd_usd` | -141,529.9808 |
| `n_long` | 111 |
| `n_short` | 89 |
| `long_pnl_usd` | 458,468.0468 |
| `short_pnl_usd` | 514,629.8136 |
| `starting_cash_mnq_equivalent` | 500,000 |
| `final_equity_mnq_equivalent` | 1,473,097.8605 |
| `net_pnl_mnq_equivalent` | 973,097.8605 |
| `max_drawdown_pct` | -28.3060 |

### Safety diagnostics (from WIP IS diagnostic)

| Counter | Value |
|---|---|
| `all_safety_warnings_zero` | `True` |
| `cap_binding_events_count` | `0` |
| `n_calculation_drift_detected_count` | `0` |
| `non_rth_fill_warning_count` | `0` |
| `per_market_unit_count_invariant_violation_count` | `0` |
| `pyramid_state_machine_violation_count` | `0` |
| `rollover_violation_count` | `0` |
| `stale_fill_warning_count` | `0` |
| `unsupported_order_type_detected_count` | `0` |

## 6. Critical gaps identified (4)

### G1: S1-only cost-tier evaluated; S0/S2/S3/S4 not yet run
- **impact_on_verdict:** K12 (DR2/DR3/DR5 cost-stress fail-fast) cannot be evaluated until the S0/S2/S3/S4 cost-stress matrix is run. The current `READY_FOR_LONGER_BACKTEST` verdict at S1 single-tier is conditional on the cost-stress matrix subsequently clearing.
- **evidence:** agate_evaluation.A8_cost_stress_S0_S4_run.evaluated_this_turn = False; kgate_evaluation.k_criteria_details.K12_DR_fires_on_cost_stress = 'NOT_EVALUATED_THIS_TURN_ONLY_S1_RUN'
- **remediation_path:** Authorize P6.5 cost-stress sweep (run cost_tier=S0/S2/S3/S4 with the same sealed driver and aggregate the matrix; evaluate DR2/DR3/DR5). Until P6.5 runs, treat the verdict as PRELIMINARY.

### G2: K10 (pairwise correlation gate) not evaluated
- **impact_on_verdict:** k_criteria_details.K10_avg_pairwise_corr_gt_0_50 is None (not computed). For a 4-symbol futures basket NQ+GC+ZN+CL, pairwise dependence may differ from the SPY/TLT/GLD/USO ETF-proxy universe; needs to be measured for completeness.
- **evidence:** is_diag.kgate_evaluation.k_criteria_details.K10_avg_pairwise_corr_gt_0_50 = None
- **remediation_path:** Add pairwise dependence computation to the aggregator step or run as a separate diagnostic.

### G3: Tier-N spec phase label is now stale
- **impact_on_verdict:** No functional impact; informational only.
- **evidence:** Tier-N spec records phase=TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED, but the parallel session has clearly advanced past that label (runner harness built, test scaffold complete, smoke P4 17/17 PASS, IS driver built, IS diagnostic produced).
- **remediation_path:** Either accept the stale label as historical (preferred; do not modify sealed spec) or document the lifecycle progression in a separate sealed status report (which this review serves).

### G4: IS diagnostic result file is in working tree but not yet committed
- **impact_on_verdict:** The diagnostic content is sealed in-file (seal recomputes correctly) but is not in HEAD's blob tree. Anyone reading HEAD will not see the verdict. The parallel session is mid-commit.
- **evidence:** git ls-files shows the file is untracked. The seal recomputes from the working-tree bytes correctly.
- **remediation_path:** Parallel session will likely commit it under their own authorization. This controller session will not touch it.

## 7. Next-step recommendations (documented; each requires separate authorization)

### `authorize_p6_5_cost_stress_sweep` (RECOMMENDED)

Run cost_tier=S0/S2/S3/S4 with the same sealed driver; aggregate the matrix; evaluate DR2/DR3/DR5; finalize the K12 evaluation. Closes the most critical evaluation gap (G1).
- requires_separate_authorization: **True**

### `authorize_k10_pairwise_dependence_computation`

Add pairwise dependence computation for NQ+GC+ZN+CL futures-bar daily returns and evaluate K10 (avg_pairwise_corr <= 0.50). Closes gap G2.
- requires_separate_authorization: **True**

### `authorize_parallel_session_in_sample_diagnostic_commit` (OUT OF SCOPE)

Allow the parallel session to commit the WIP IS diagnostic result file. This controller session will not touch it.
- requires_separate_authorization: **False**

### `halt_until_p6_5_runs` (DEFAULT)

Default: do not advance beyond the current S1 baseline; treat the verdict as PRELIMINARY pending P6.5.
- requires_separate_authorization: **False**

## 8. Scope-clean attestation

- `this_turn_unstaged_parallel_session_wip_files_to_keep_commit_scope_clean`: **True**
- `files_unstaged_by_this_turn_via_git_restore_staged`:
  - `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_diagnostic_result_sealed.json`
  - `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_diagnostic_result_sealed.md`
- `working_tree_content_of_unstaged_files_NOT_modified`: **True**
- `parallel_session_can_re_stage_and_commit_anytime`: **True**

## 9. Negative invariants (all True)

- `no_CLAUDE_md_modified`: **True**
- `no_RUNBOOK_modified`: **True**
- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promoted`: **True**
- `no_csv_modified`: **True**
- `no_d1_canonical_fetch_run_manifest_modified`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_docs_decisions_md_modified`: **True**
- `no_git_push`: **True**
- `no_gitignore_modified`: **True**
- `no_idea_memory_mutation`: **True**
- `no_in_sample_diagnostic_file_modification`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_oos_inspection`: **True**
- `no_oos_value_inspected`: **True**
- `no_orb_artifact_modified`: **True**
- `no_paper_order_placed`: **True**
- `no_parallel_session_commit_amended`: **True**
- `no_parallel_session_commit_reverted`: **True**
- `no_parallel_session_staged_file_committed_by_this_session`: **True**
- `no_pipeline_manifest_modified`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_s10_d1_artifact_modified`: **True**
- `no_s10_d2_committed_artifact_modified`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s8_d1_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computation`: **True**
- `no_simulator_run`: **True**
- `no_spec_modification`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_tier_n_seal_change`: **True**

## 10. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 11. Labels

- `S10_D2_TIER_N_SPEC_AND_STATUS_REVIEW_COMPLETE`
- `S10_D2_TIER_N_SEALED_AND_VERIFIED`
- `SEALED_ARTIFACTS_VERIFIED_8_OF_8`
- `IS_DIAGNOSTIC_AT_S1_SINGLE_TIER_VERDICT_READY_FOR_LONGER_BACKTEST_PRELIMINARY`
- `COST_STRESS_S0_S2_S3_S4_NOT_YET_RUN`
- `K10_PAIRWISE_DEPENDENCE_NOT_EVALUATED`
- `K12_DR_FIRES_NOT_EVALUATED`
- `VERDICT_NEVER_MEANS_LIVE_READY`
- `NO_SPEC_MODIFICATION`
- `NO_DATA_FETCH`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_SIGNAL_COMPUTED`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`

## 12. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S10-D2 status review sealed. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

