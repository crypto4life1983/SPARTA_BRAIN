# S12-D1 P6 IS Diagnostic (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.in_sample_diagnostic_result_sealed.v1`
**Phase:** `S12_D1_P6_IS_DIAGNOSTIC`
**Phase prefix:** `PHASE2-S12-D1-P6`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T16:18:05Z`
**Authorization:** *"Authorize s12 D1 P6 IS diagnostic only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Verdict: **`INSUFFICIENT_SAMPLE`**

- **closed_trades:** 33
- **K9 threshold (min):** 100
- **K9 fires:** True
- **net_pnl_usd:** $+6,277.14 on $100,000 starting cash
- **expectancy_usd:** $+190.22
- **sharpe_proxy:** +0.16773
- **maxdd_pct:** -3.78%
- **K_fires_count:** 1
- **A_fails:** ['A1_closed_trades_ge_100']
- **Duration:** 0.1s

## 1. Data source (audit-clean CSV; sha verified at load)

- Path: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv`
- sha256: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- Total rows: 2066
- IS bars in window: 1443
- IS window: 2019-05-13 -> 2023-12-29

## 2. Strategy parameters (byte-equivalent to SEAL)

- Donchian entry N / exit M: 15 / 8
- ATR: Wilder 20, 2.0N stop
- Per-trade risk: 1.0%
- START_CASH: $100,000 (DA4=B)
- max_units_per_market: 1; no_pyramid: True
- WARMUP_DAYS: 220
- Cost tier: S1 (commission $0.74 / fees $0.36 / slippage e/s/x (1, 1, 1) ticks)
- Tick size / dollar-per-tick: 0.25 / $0.5

## 3. Trade diagnostics

| Metric | Value |
|---|---|
| closed_trades | **33** |
| wins / losses | 15 / 18 |
| win_rate_pct | 45.45 |
| avg_win_usd | +$1,212.83 |
| avg_loss_usd | $-661.96 |
| expectancy_per_trade_usd | $+190.22 |
| sharpe_proxy_per_trade | +0.16773 |
| maxdd_pct | -3.78% |
| maxdd_abs_usd | $-3,775.99 |
| long trades | 19 |
| short trades | 14 |
| exits: donchian | 24 |
| exits: stop | 8 |
| exits: end_of_window | 1 |

## 4. K-gates evaluation

| Gate | Fires |
|---|---|
| K1_sharpe_lt_0 | False |
| K2_expectancy_le_0 | False |
| K4_maxdd_gt_50pct | False |
| K6_safety_warnings_gt_0 | False |
| K9_closed_trades_lt_100 | True |
| K10_avg_pairwise_dependence_gt_0_50 | False |
| K11_cap_binding_gt_1000 | False |
| K12_DR_fires | False |

## 5. A-gates evaluation

| Gate | Pass |
|---|---|
| A1_closed_trades_ge_100 | False |
| A2_sharpe_gt_0 | True |
| A3_expectancy_gt_0 | True |
| A4_maxdd_le_50pct | True |
| A6_no_pyramid_attestation_pass | True |
| A10_cap_binding_eq_0 | True |

## 6. OOS K9 risk carried forward (C1.A + C1.D)

- C1.A acknowledged: True
- C1.D disposition: DR1 INCONCLUSIVE_HOLD
- P2 expected IS trade count: 80-200 (central ~140)
- **Actual IS trade count: 33**
- K9 mitigation hypothesis at IS: **PARTIALLY_FALSIFIED at IS: closed_trades < P2 lower-bound estimate of 80; below K9 threshold of 100. The Donchian-15/8 shortened-lookback hypothesis did not produce sufficient IS sample to clear K9 on this universe.**

## 7. Comparison vs parallel session P6 IS

- Parallel P6 commit: `9241ed67bf2b2a9fa7e7d7a52b03693713929ac6`
- Parallel P6 seal: `33c91592c09860c3ab9469aab38741b7378f54ad56ff3772f9ef6a03ea92156d`
- Parallel closed_trades: 48
- Parallel verdict: `INSUFFICIENT_SAMPLE`
- This session's closed_trades: 33
- This session's verdict: `INSUFFICIENT_SAMPLE`
- **Verdicts agree (both INSUFFICIENT_SAMPLE):** True

Both this session's chain and parallel session's chain produced INSUFFICIENT_SAMPLE if K9 fires here; the substantive K9 mitigation hypothesis is independently falsified at IS by two implementations on the same audit-clean CSV.

## 8. Posture

- Trading: `PAUSED`
- Live: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- verdict_never_means_live_ready: True

## 9. Negative invariants (all True)

- `no_backtest_outside_this_p6_run`: True
- `no_branch_change`: True
- `no_brokerage_connection`: True
- `no_cache_modification`: True
- `no_candidate_promoted`: True
- `no_claude_md_modification`: True
- `no_csv_modification`: True
- `no_data_fetch`: True
- `no_data_modification`: True
- `no_databento_api_key_access`: True
- `no_databento_call`: True
- `no_decisions_md_modification`: True
- `no_external_network_call`: True
- `no_frc_grant`: True
- `no_git_push`: True
- `no_gitignore_modification`: True
- `no_idea_memory_mutation`: True
- `no_k9_threshold_relaxation_proposed`: True
- `no_key_leakage`: True
- `no_lessons_md_commit`: True
- `no_lessons_md_modification`: True
- `no_lessons_md_staging`: True
- `no_live_readiness_claim`: True
- `no_oos_confirmation_claim`: True
- `no_oos_inspection`: True
- `no_orb_artifact_modified`: True
- `no_orders_created`: True
- `no_p4_smoke_modified`: True
- `no_paper_or_live_trade`: True
- `no_parallel_session_chain_modified`: True
- `no_pipeline_manifest_modification`: True
- `no_profitability_claim`: True
- `no_review_queue_mutation`: True
- `no_runbook_modification`: True
- `no_runner_harness_module_modified`: True
- `no_s10_d1_artifact_modified`: True
- `no_s10_d2_artifact_modified`: True
- `no_s11_d1_artifact_modified`: True
- `no_s12_d1_p1_plan_lock_modified`: True
- `no_s12_d1_p2_phase_2_plan_modified`: True
- `no_s12_d1_p3_build_modified`: True
- `no_s12_d1_sealed_spec_modified`: True
- `no_s7_artifact_modified`: True
- `no_s9_artifact_modified`: True
- `no_simulator_outside_this_p6_run`: True
- `no_step_30_cost_constant_modified`: True
- `no_strategy_lab_invoked`: True
- `no_test_file_modified`: True

## 10. Labels

- `S12_D1_P6_IS_DIAGNOSTIC_COMPLETE`
- `C7_VERDICT_INSUFFICIENT_SAMPLE`
- `CLOSED_TRADES_33`
- `K9_FIRES_True`
- `K_FIRES_COUNT_1`
- `DONCHIAN_15_8_RUN_ON_REAL_AUDIT_CLEAN_CSV`
- `DA4_B_START_CASH_100K_APPLIED`
- `S1_COST_TIER_APPLIED`
- `C1_A_C1_D_CARRIED`
- `NO_DRIVER_MODIFICATION`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_DATA_FETCH`
- `NO_OOS_INSPECTION`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

## 11. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P6 IS diagnostic sealed. Verdict: `INSUFFICIENT_SAMPLE`. closed_trades=33. K9 fires=True. Trading: PAUSED. Live: BLOCKED_AT_6_GATES.**

